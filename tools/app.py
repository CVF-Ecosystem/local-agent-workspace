#!/usr/bin/env python3
"""Bảng điều khiển của workspace: giao diện trong trình duyệt cho các công cụ trong tools/.
Workspace control panel: a browser interface for the tools in tools/.

Cách mở / How to open: bấm đúp APP.bat (Windows) hoặc APP.command (macOS), hoặc: python tools/app.py
  --no-browser   không tự mở trình duyệt (in địa chỉ để tự mở) / do not open the browser (prints the address)
  --port N       dùng cổng N thay vì cổng ngẫu nhiên / use port N instead of a random one

Chỉ chạy trên máy này (127.0.0.1), có mã truy cập riêng cho mỗi lần mở. Không dùng mạng, không cài thêm gì.
Mỗi nút gọi đúng một script có sẵn trong tools/ với tham số cố định; thao tác ghi luôn có bước xem trước.
Tự tắt khi đóng trang khoảng 3 phút, hoặc bấm "Thoát". Chỉ cần Python 3.8+.
Runs on this computer only (127.0.0.1) with a per-session access code. No network, nothing to install.
Each button calls one existing script in tools/ with fixed arguments; writing actions always have a preview step.
Shuts down about 3 minutes after the page is closed, or with "Quit". Python 3.8+ only.
"""
import http.server, io, json, os, re, secrets, socketserver, subprocess, sys, threading, time, webbrowser
import urllib.parse
import hashlib
import merge_center
from result_schema import make, split_output

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
UI_FILE = os.path.join(TOOLS, 'app_ui.html')
TOKEN = secrets.token_urlsafe(18)
NAME_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
IDLE_LIMIT = 180          # giây không có tín hiệu từ trang thì tắt / seconds without a ping before shutdown
FIRST_GRACE = 600         # chờ lần mở trang đầu / wait for the first page load
STATE = {'last_ping': None, 'started': time.time(), 'server': None, 'port': 0}
STRUCTURED_TOOLS = {'adopt_project.py', 'upgrade_package.py', 'check_output.py', 'build_release.py'}

sys.path.insert(0, TOOLS)


def rd(rel, default=''):
    try:
        with io.open(os.path.join(ROOT, *rel.split('/')), encoding='utf-8') as src:
            return src.read()
    except (OSError, UnicodeDecodeError):
        return default


# ------------------------------------------------------------------ đọc trạng thái / status
def project_info():
    info = {}
    raw = rd('.agent/PACKAGE_INFO.json')
    if raw:
        try:
            info = json.loads(raw)
            if not isinstance(info, dict) or info.get('package') != 'local-agent-workspace' or not info.get('version'):
                info = {}
        except ValueError:
            info = {}
    name = None
    m = re.search(r'^- (?:Tên dự án|Project name):\s*(.+)$', rd('PROJECT.md'), re.M)
    if m and not m.group(1).strip().startswith('['):
        name = m.group(1).strip()
    return info, name


def state_summary():
    txt = re.sub(r'<!--.*?-->', '', rd('.agent/STATE.md'), flags=re.S)
    sections, cur = [], None
    for line in txt.splitlines():
        if line.startswith('## '):
            cur = {'title': line[3:].strip(), 'lines': []}
            sections.append(cur)
        elif cur is not None and line.strip():
            cur['lines'].append(line.rstrip())
    for s in sections:
        s['empty'] = all(re.fullmatch(r'-?\s*\[.*\]\s*', l.strip()) or l.strip() in ('None', '-') for l in s['lines'])
        s['lines'] = s['lines'][:12]
    path = os.path.join(ROOT, '.agent', 'STATE.md')
    mtime = os.path.getmtime(path) if os.path.isfile(path) else None
    # giải nén ZIP có thể để ngày 1980; chỉ báo ngày khi STATE có nội dung thật / unzipping can leave 1980 dates
    if mtime is not None and (mtime < 946684800 or not any(not x['empty'] for x in sections)):
        mtime = None
    return {'sections': sections, 'mtime': mtime}


def skill_rows():
    rows = []
    for line in rd('.agent/SKILL_INDEX.md').splitlines():
        if not line.startswith('| ') or line.startswith('| Skill ID') or set(line) <= set('|- '):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 6:
            rows.append({'id': cells[0], 'origin': cells[1], 'scope': cells[2], 'location': cells[3],
                         'use': cells[4], 'status': cells[5]})
    return rows


def pack_info(lang):
    try:
        import pack
        pack.LANG = lang
        av, ins = pack.available(), pack.installed()
    except Exception as e:  # gói hỏng không làm sập bảng điều khiển / a broken pack must not crash the panel
        return {'error': str(e), 'items': []}
    items = []
    for n, m in av.items():
        items.append({'name': n, 'version': m.get('version'), 'title': pack.loc(m.get('title')),
                      'description': pack.loc(m.get('description')), 'skills': m.get('skills', []),
                      'installed': ins.get(n, {}).get('version')})
    for n, m in ins.items():
        if n not in av:
            items.append({'name': n, 'version': None, 'title': n, 'description': '', 'skills': m.get('skills', []),
                          'installed': m.get('version')})
    return {'items': items}


def count_files(rel):
    n = 0
    for d, dirs, files in os.walk(os.path.join(ROOT, rel)):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        n += sum(1 for f in files if f != 'README.md' and not f.startswith('.'))
    return n


def tk_available():
    try:
        import tkinter  # noqa: F401
        return True
    except Exception:
        return False


def status():
    info, name = project_info()
    lang = info.get('language') or info.get('lang') or ('en' if re.search(r'^- Project name:', rd('PROJECT.md'), re.M) else 'vi')
    home = os.path.expanduser('~')
    # Identify a template by its contents, never by the folder name alone.
    project_hash = hashlib.sha256(rd('PROJECT.md').replace('\r\n', '\n').encode('utf-8')).hexdigest()
    template = not rd('.agent/PACKAGE_INFO.json') and any(
        line == project_hash + '  PROJECT.md' or line == project_hash + '  en/PROJECT.md'
        for line in rd('MANIFEST.sha256').splitlines())
    kind = 'project' if info else ('template' if template else 'unknown')
    return {
        'version': rd('VERSION').strip(),
        'initialized': bool(info),
        'workspace_kind': kind,
        'info': info,
        'project_name': name,
        'folder': os.path.basename(ROOT),
        'root': ROOT,
        'lang': lang,
        'state': state_summary(),
        'merges': merge_center.scan(ROOT),
        'skills': skill_rows(),
        'packs': pack_info(lang),
        'counts': {k: count_files(k) for k in ('output', 'references', 'working', 'archive')},
        'is_source': kind == 'template',
        'release_source': os.path.isdir(os.path.join(ROOT, 'release_templates')),
        'template_folder': kind == 'template',
        'dests': {'claude': os.path.join(home, '.claude', 'skills'), 'agents': os.path.join(home, '.agents', 'skills')},
        'picker': tk_available(),
        'python': sys.version.split()[0],
    }


# ------------------------------------------------------------------ chạy script / run scripts
def run_tool(script, args, timeout=600):
    env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
    tool_args = list(args) + (['--result-json'] if script in STRUCTURED_TOOLS else [])
    cmd = [sys.executable, os.path.join(TOOLS, script)] + tool_args
    shown = 'python tools/%s %s' % (script, ' '.join('"%s"' % a if (' ' in a or not a) else a for a in args))
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, env=env, timeout=timeout, stdin=subprocess.DEVNULL)
        out = p.stdout.decode('utf-8', 'replace')
        err = p.stderr.decode('utf-8', 'replace')
        if err.strip():
            out += '\n' + err
        human, structured = split_output(out.strip())
        if structured is not None and structured.get('code') != p.returncode:
            structured = None
        if script in STRUCTURED_TOOLS and structured is None:
            structured = make('error', code=-2, message='Tool did not return a valid result schema.',
                              changes=None, unchecked=[{'tool': script, 'reason': 'invalid_result_schema'}])
            return {'code': -2, 'out': human, 'cmd': shown.strip(), 'result': structured}
        if structured is None:
            structured = make('success' if p.returncode == 0 else 'error', code=p.returncode,
                              message='', changes=None)
        return {'code': p.returncode, 'out': human, 'cmd': shown.strip(), 'result': structured}
    except subprocess.TimeoutExpired:
        structured = make('not_checked' if script == 'check_output.py' else 'error', code=-1,
                          message='Timed out', changes=None,
                          unchecked=[{'tool': script, 'reason': 'timeout'}])
        return {'code': -1, 'out': 'Quá thời gian chờ / Timed out (%ds).' % timeout,
                'cmd': shown, 'result': structured}


class BadInput(Exception):
    pass


def need_dir(p):
    p = (p or '').strip().strip('"')
    if not p or not os.path.isdir(os.path.expanduser(p)):
        raise BadInput('Không thấy thư mục / Folder not found: %s' % (p or '(trống / empty)'))
    return os.path.expanduser(p)


def need_name(n):
    n = (n or '').strip()
    if not NAME_RE.match(n):
        raise BadInput('Tên gói không hợp lệ / Invalid pack name: %s' % n)
    return n


def need_text(p, key, msg):
    v = (p.get(key) or '').strip()
    if not v:
        raise BadInput(msg)
    return v


def need_project():
    if not os.path.isfile(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json')):
        raise BadInput('Thư mục này chưa khởi tạo thành project; khởi tạo trước rồi mới cài gói hoặc nâng cấp.\n'
                       'This folder is not set up as a project yet; set it up before installing packs or upgrading.')


def action(name, p):
    apply = bool(p.get('apply'))
    if name in ('upgrade', 'pack_add', 'pack_remove', 'pack_update'):
        need_project()
    if name == 'init':
        args = ['--name', need_text(p, 'name', 'Cần nhập tên project / A project name is required.'),
                '--lang', 'en' if p.get('lang') == 'en' else 'vi']
        for k in ('purpose', 'outputs', 'style', 'sources', 'constraints', 'sensitivity'):
            v = (p.get(k) or '').strip()
            if v:
                args += ['--' + k, v]
        if os.path.isfile(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json')):
            args.append('--force')  # chạy lại: chỉ cập nhật PROJECT.md / re-run: only updates PROJECT.md
        return run_tool('init_project.py', args + ([] if apply else ['--dry-run']))
    if name == 'upgrade':
        return run_tool('upgrade_package.py', ['--from', need_dir(p.get('source'))] + (['--apply'] if apply else []))
    if name == 'upgrade_other':
        target = need_dir(p.get('project'))
        if os.path.normcase(os.path.abspath(target)) == os.path.normcase(ROOT):
            raise BadInput('Chọn thư mục project khác, không phải thư mục đang mở. / Choose another project folder, not this one.')
        return run_tool('upgrade_package.py', ['--project', target] + (['--apply'] if apply else []))
    if name == 'adopt':
        args = ['--project', need_dir(p.get('project')),
                '--name', need_text(p, 'name', 'Cần nhập tên project / A project name is required.'),
                '--lang', 'en' if p.get('lang') == 'en' else 'vi']
        return run_tool('adopt_project.py', args + (['--apply'] if apply else []))
    if name == 'pack_list':
        return run_tool('pack.py', ['list'])
    if name in ('pack_add', 'pack_remove'):
        return run_tool('pack.py', [name.split('_')[1], need_name(p.get('pack'))])
    if name == 'pack_update':
        return run_tool('pack.py', ['update', need_name(p.get('pack'))] + (['--apply'] if apply else []))
    if name == 'check_output':
        files = [f.strip().strip('"') for f in (p.get('files') or []) if f and f.strip()]
        if not files:
            raise BadInput('Chọn ít nhất một file / Choose at least one file.')
        return run_tool('check_output.py', (['--declaration'] if p.get('declaration') else []) + files)
    if name == 'install_skills':
        target = p.get('target')
        if target == 'claude':
            dest = os.path.join('~', '.claude', 'skills')
        elif target == 'agents':
            dest = os.path.join('~', '.agents', 'skills')
        else:
            dest = need_text(p, 'dest', 'Cần thư mục đích / A destination folder is required.').strip('"')
        args = ['--dest', dest]
        if p.get('skills'):
            sel = [s for s in p['skills'] if NAME_RE.match(s)]
            if sel:
                args += ['--skills', ','.join(sel)]
        for k, f in (('include_packs', '--include-packs'), ('overwrite', '--overwrite'), ('apply', '--yes')):
            if p.get(k):
                args.append(f)
        return run_tool('install_skills.py', args)
    if name == 'library_init':
        return run_tool('library.py', ['init'])
    if name == 'library_check':
        return run_tool('library.py', ['check'] + (['--days', str(int(p.get('days')))] if p.get('days') else []))
    if name == 'library_stats':
        return run_tool('library.py', ['stats', '--json'])
    if name == 'library_find':
        q = need_text(p, 'query', 'Cần từ khóa / A keyword is required.')
        args = ['find', q, '--json', '--all']
        if p.get('group'):
            args += ['--group', str(p.get('group'))]
        return run_tool('library.py', args)
    if name == 'check_package':
        return run_tool('check_package.py', ['--verify'] if p.get('verify') else [])
    if name == 'build_guides':
        return run_tool('build_guides_html.py', [])
    if name == 'build_release':
        return run_tool('build_release.py', [], timeout=900)
    if name == 'merge_state':
        try:
            changed = merge_center.set_state(ROOT, need_text(p, 'path', 'Cần đường dẫn file hợp nhất.'),
                                             need_text(p, 'state', 'Cần trạng thái hợp nhất.'))
        except ValueError as e:
            raise BadInput(str(e))
        return {'code': 0, 'out': '', 'cmd': '', 'result': make('success', message='Merge state updated',
                changes=True, files=[changed])}
    raise BadInput('Thao tác không có / Unknown action: %s' % name)


# ------------------------------------------------------------------ chọn file, mở thư mục / pickers, open
PICK_SCRIPT = r'''
import json, sys, tkinter as tk
from tkinter import filedialog
r = tk.Tk(); r.withdraw()
try: r.attributes('-topmost', True)
except Exception: pass
kind, start = sys.argv[1], sys.argv[2]
if kind == 'dir':
    v = filedialog.askdirectory(initialdir=start, mustexist=True)
    out = [v] if v else []
else:
    out = list(filedialog.askopenfilenames(initialdir=start))
r.destroy()
print(json.dumps(out))
'''


def pick(kind):
    try:
        start = os.path.join(ROOT, 'output') if kind != 'dir' and os.path.isdir(os.path.join(ROOT, 'output')) else os.path.dirname(ROOT)
        p = subprocess.run([sys.executable, '-c', PICK_SCRIPT, 'dir' if kind == 'dir' else 'files', start],
                           capture_output=True, timeout=900)
        paths = json.loads(p.stdout.decode('utf-8', 'replace').strip() or '[]')
        return {'paths': [os.path.normpath(x) for x in paths]}
    except Exception as e:
        return {'paths': [], 'error': str(e)}


def open_path(rel):
    rel = (rel or '').strip().replace('\\', '/')
    target = os.path.normpath(os.path.join(ROOT, rel)) if rel else ROOT
    if not (target == ROOT or target.startswith(ROOT + os.sep)) or not os.path.exists(target):
        raise BadInput('Không mở được / Cannot open: %s' % rel)
    if sys.platform.startswith('win'):
        os.startfile(target)  # noqa
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', target])
    else:
        subprocess.Popen(['xdg-open', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {'ok': True}


# ------------------------------------------------------------------ máy chủ / server
class Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'WorkspacePanel'

    def log_message(self, *a):
        pass

    def _host_ok(self):
        return (self.headers.get('Host') or '').split(':')[0] in ('127.0.0.1', 'localhost')

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {'error': 'host'})
        u = urllib.parse.urlparse(self.path)
        if u.path in ('/', '/index.html'):
            if urllib.parse.parse_qs(u.query).get('t', [''])[0] != TOKEN:
                msg = ('<!doctype html><meta charset="utf-8"><title>Workspace</title>'
                       '<body style="font:16px system-ui;padding:40px">Mở lại bảng điều khiển bằng APP.bat / APP.command.'
                       '<br>Open the panel again with APP.bat / APP.command.</body>')
                return self._send(403, msg.encode('utf-8'), 'text/html; charset=utf-8')
            html = io.open(UI_FILE, encoding='utf-8').read().replace('__PANEL_TOKEN__', TOKEN)
            STATE['last_ping'] = time.time()
            return self._send(200, html.encode('utf-8'), 'text/html; charset=utf-8')
        return self._send(404, {'error': 'not found'})

    def do_POST(self):
        if not self._host_ok() or self.headers.get('X-Panel-Token') != TOKEN:
            return self._send(403, {'error': 'forbidden'})
        try:
            n = int(self.headers.get('Content-Length') or 0)
            body = json.loads(self.rfile.read(n).decode('utf-8') or '{}') if n else {}
        except ValueError:
            return self._send(400, {'error': 'bad json'})
        path = urllib.parse.urlparse(self.path).path
        STATE['last_ping'] = time.time()
        try:
            if path == '/api/ping':
                return self._send(200, {'ok': True})
            if path == '/api/status':
                return self._send(200, status())
            if path == '/api/run':
                return self._send(200, action(body.get('action', ''), body.get('params') or {}))
            if path == '/api/pick':
                return self._send(200, pick(body.get('kind')))
            if path == '/api/open':
                return self._send(200, open_path(body.get('path')))
            if path == '/api/quit':
                self._send(200, {'ok': True})
                threading.Thread(target=STATE['server'].shutdown, daemon=True).start()
                return None
        except BadInput as e:
            return self._send(200, {'code': 2, 'out': str(e), 'cmd': '', 'input_error': True,
                              'result': make('blocked', code=2, message=str(e), changes=False)})
        except Exception as e:  # lỗi bất ngờ vẫn trả về trang / unexpected errors still reach the page
            return self._send(500, {'code': -1, 'out': 'Lỗi / Error: %r' % (e,), 'cmd': ''})
        return self._send(404, {'error': 'not found'})


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def watchdog():
    while True:
        time.sleep(10)
        now, last = time.time(), STATE['last_ping']
        if (last is None and now - STATE['started'] > FIRST_GRACE) or (last is not None and now - last > IDLE_LIMIT):
            print('Không còn trang nào mở, tắt bảng điều khiển. / No page open, shutting down.')
            STATE['server'].shutdown()
            return


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    port = 0
    if '--port' in argv:
        try:
            port = int(argv[argv.index('--port') + 1])
        except (IndexError, ValueError):
            print('Dùng / Usage: python tools/app.py [--port N] [--no-browser]')
            return 2
    if not os.path.isfile(UI_FILE):
        print('Thiếu tools/app_ui.html / Missing tools/app_ui.html')
        return 1
    srv = Server(('127.0.0.1', port), Handler)
    STATE['server'], STATE['port'] = srv, srv.server_address[1]
    url = 'http://127.0.0.1:%d/?t=%s' % (STATE['port'], TOKEN)
    print('Bảng điều khiển workspace đang chạy. / Workspace panel is running.')
    print('Địa chỉ / Address: ' + url)
    print('Giữ cửa sổ này mở trong lúc dùng; đóng trang hoặc bấm "Thoát" để tắt.')
    print('Keep this window open while using it; close the page or press "Quit" to stop.')
    threading.Thread(target=watchdog, daemon=True).start()
    if '--no-browser' not in argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    print('Đã tắt. / Stopped.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
