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
import datetime, getpass, http.server, importlib.util, io, json, os, platform, re, secrets, socketserver, subprocess, sys, threading, time, webbrowser, zipfile
import urllib.parse
import hashlib
sys.dont_write_bytecode = True  # không để lại __pycache__ trong bộ mẫu / leave no __pycache__ in the template
import merge_center, ops_log, transaction
from result_schema import make, split_output

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
UI_FILE = os.path.join(TOOLS, 'app_ui.html')
TOKEN = secrets.token_urlsafe(18)
NAME_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
TXID_RE = re.compile(r'[0-9A-Za-z-]{1,80}')
IDLE_LIMIT = 180          # giây không có tín hiệu từ trang thì tắt / seconds without a ping before shutdown
FIRST_GRACE = 600         # chờ lần mở trang đầu / wait for the first page load
HISTORY_SHOWN = 20        # thao tác gần nhất hiện ở trang tình trạng / recent operations shown on the status page
DIAG_REL = '.agent/runtime/diagnostics'
HISTORY_REL = '.agent/runtime/operations.jsonl'
STATE = {'last_ping': None, 'started': time.time(), 'server': None, 'port': 0}
# mọi công cụ có envelope có cấu trúc / every tool that returns a native result envelope
STRUCTURED_TOOLS = {'init_project.py', 'new_project.py', 'adopt_project.py', 'upgrade_package.py', 'check_output.py', 'build_release.py',
                    'check_package.py', 'pack.py', 'install_skills.py', 'library.py', 'build_guides_html.py', 'transaction.py'}
# tên thao tác được phép ghi vào lịch sử; còn lại ghi là 'unknown' / action names allowed in the history
ACTION_NAMES = {'init', 'new_project', 'project_open', 'upgrade', 'upgrade_other', 'adopt', 'pack_list', 'pack_add', 'pack_remove', 'pack_update', 'pack_confirm',
                'check_output', 'install_skills', 'library_init', 'library_check', 'library_stats', 'library_find', 'library_sync',
                'check_package', 'build_guides', 'build_release', 'merge_state', 'merge_diff', 'diagnostics',
                'tx_resume', 'tx_rollback', 'history_clear'}
# đọc thư viện (tìm, thống kê) không phải tác động: không ghi lịch sử / reading the library (search, stats) is not an effect: never logged
NO_LOG_ACTIONS = {'library_find', 'library_stats'}

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
    # xuất được hay không do cùng một hàm với install_skills (nhãn chỉ mục + xác nhận gói), để giao diện và CLI không lệch nhau
    # whether a skill can be exported comes from the same function install_skills uses, so the panel and the CLI cannot drift apart
    idx = {r['id']: (r['location'], r['status']) for r in rows}
    try:
        import install_skills
    except Exception:
        install_skills = None
    for r in rows:
        if install_skills is None or r['origin'] != 'LOCAL' or r['scope'] not in ('SHARED', 'PACK'):
            why = 'not_exportable'
        else:
            why = install_skills.eligibility(r['id'], r['location'], idx)
        r['eligible'], r['reason'] = why is None, why
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
        st = pack.intake_state(m, os.path.join(ROOT, 'packs', n))
        items.append({'name': n, 'version': m.get('version'), 'title': pack.loc(m.get('title')),
                      'description': pack.loc(m.get('description')), 'skills': m.get('skills', []),
                      'installed': ins.get(n, {}).get('version'), 'intake': st['state'], 'intake_label': pack.intake_label(st),
                      'eligibility': pack.installed_eligibility(n) if n in ins else None})
    for n, m in ins.items():
        if n not in av:
            items.append({'name': n, 'version': None, 'title': n, 'description': '', 'skills': m.get('skills', []),
                          'installed': m.get('version')})
    return {'items': items}


def recent_files(rel, limit=8):
    """File người dùng trong một thư mục (mới nhất trước), bỏ README/file ẩn/chỉ mục. / User files, newest first."""
    out, base = [], os.path.join(ROOT, rel)
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        for f in files:
            if f == 'README.md' or f.startswith(('.', '~$')) or f == '_INDEX.xlsx':
                continue
            full = os.path.join(d, f)
            try:
                st = os.stat(full)
            except OSError:
                continue
            out.append({'path': os.path.relpath(full, ROOT).replace(os.sep, '/'), 'name': f,
                        'mtime': st.st_mtime if st.st_mtime > 946684800 else None, 'size': st.st_size})
    out.sort(key=lambda x: x['mtime'] or 0, reverse=True)
    return {'total': len(out), 'items': out[:limit]}


def project_field(*labels):
    """Một dòng đã điền trong PROJECT.md (None nếu còn [chỗ trống]). / A filled-in PROJECT.md line, or None."""
    for label in labels:
        m = re.search(r'^- %s:\s*(.+?)\s*$' % re.escape(label), rd('PROJECT.md'), re.M)
        if m and not m.group(1).startswith('['):
            return m.group(1)
    return None


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


def workspace_kind(info):
    """project | template | unknown, từ bằng chứng trong file, không từ tên thư mục / from file evidence, never the folder name."""
    if info:
        return 'project'
    # Identify a template by its contents, never by the folder name alone.
    project_hash = hashlib.sha256(rd('PROJECT.md').replace('\r\n', '\n').encode('utf-8')).hexdigest()
    template = not rd('.agent/PACKAGE_INFO.json') and any(
        line == project_hash + '  PROJECT.md' or line == project_hash + '  en/PROJECT.md'
        for line in rd('MANIFEST.sha256').splitlines())
    return 'template' if template else 'unknown'


def _has_module(name):
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def components():
    """Chức năng tùy chọn và có dùng được không; panel không tự cài gì / Optional features and whether they can run.
    Nothing is installed here; the status page shows the command to run."""
    opx = _has_module('openpyxl')
    return [
        {'feature': 'python', 'needs': '3.8', 'usable': sys.version_info >= (3, 8), 'version': sys.version.split()[0]},
        {'feature': 'library', 'needs': 'openpyxl', 'usable': opx},
        {'feature': 'xlsx', 'needs': 'openpyxl', 'usable': opx},
        {'feature': 'picker', 'needs': 'tkinter', 'usable': tk_available()},
        controlled_component(),
    ]


def controlled_component():
    """Luồng nháp có kiểm soát (thẻ Nháp hiện tại) chạy được hay không, đo bằng đúng Python đang chạy bảng điều khiển: Windows + NTFS cục bộ,
    jsonschema>=4.18 (Draft 2020-12) và owner nạp đúng pin. Chỉ đọc; không cài gì, không lưu hồ sơ. Chỉ thẻ này chịu các điều kiện đó.
    Whether the controlled draft flow can run, measured with the exact Python running this panel. Read only; installs and stores nothing."""
    out = {'feature': 'controlled', 'needs': 'jsonschema>=4.18', 'usable': False, 'reason': 'READINESS_UNKNOWN',
           'python_path': sys.executable, 'version': sys.version.split()[0], 'jsonschema': None, 'fs': None}
    try:
        import current_draft
        r = current_draft.readiness(ROOT)
        out.update(usable=bool(r.get('usable')), reason=r.get('reason'), jsonschema=r.get('jsonschema'), fs=r.get('fs'))
    except Exception:  # không đo được thì coi là chưa dùng được, không đoán / unmeasured counts as unusable, never guessed
        pass
    return out


def branding_info():
    """Logo và tên đơn vị trong assets/ (nếu có) cho thanh bên; ghi lại assets/branding.js cho trang hướng dẫn.
    Organization logo and name from assets/ for the sidebar; refreshes assets/branding.js for the guide pages."""
    import check_package as cp
    title, sub, logo_path = cp.branding_config(ROOT)
    logo_data = None
    if logo_path:
        try:
            if os.path.getsize(logo_path) <= 2 * 1024 * 1024:
                import base64
                ext = os.path.splitext(logo_path)[1].lower()
                mime = {'.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(ext, 'image/png')
                with open(logo_path, 'rb') as lf:
                    logo_data = 'data:%s;base64,%s' % (mime, base64.b64encode(lf.read()).decode('ascii'))
        except OSError:
            logo_data = None
    js = cp.branding_js(ROOT)
    if js:
        try:
            js_file = os.path.join(ROOT, 'assets', 'branding.js')
            if not os.path.isfile(js_file) or io.open(js_file, encoding='utf-8').read() != js:
                with io.open(js_file, 'w', encoding='utf-8', newline='\n') as jf:
                    jf.write(js)
        except OSError:
            pass
    if not (title or sub or logo_data):
        return None
    return {'title': title or None, 'subtitle': sub or None, 'logo': logo_data}


def status():
    info, name = project_info()
    lang = info.get('language') or info.get('lang') or ('en' if re.search(r'^- Project name:', rd('PROJECT.md'), re.M) else 'vi')
    home = os.path.expanduser('~')
    kind = workspace_kind(info)
    records = ops_log.read(ROOT)
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
        'sources': recent_files('references'),
        'outputs': recent_files('output'),
        'drafts': recent_files('working', 4),
        'purpose': project_field('Mục đích và người đọc', 'Purpose and audience'),
        'expected': project_field('Đầu ra mong đợi', 'Expected outputs'),
        'parent': os.path.dirname(ROOT),
        'is_source': kind == 'template',
        'release_source': os.path.isdir(os.path.join(ROOT, 'release_templates')),
        'template_folder': kind == 'template',
        'dests': {'claude': os.path.join(home, '.claude', 'skills'), 'agents': os.path.join(home, '.agents', 'skills')},
        'picker': tk_available(),
        'python': sys.version.split()[0],
        'platform': '%s %s' % (platform.system(), platform.release()),
        'transactions': transaction.incomplete(ROOT),
        'components': components(),
        'history': list(reversed(records))[:HISTORY_SHOWN],
        'history_summary': ops_log.summary(records),
        'branding': branding_info(),
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


def need_txid(p):
    v = str(p.get('txid') or '')  # không cắt khoảng trắng: phải khớp đúng / no trimming: must match exactly
    if not TXID_RE.fullmatch(v):  # chỉ chữ, số và dấu gạch ngang / letters, digits and hyphens only
        raise BadInput('Mã giao dịch không hợp lệ / Invalid transaction id.')
    return v


def need_project():
    if not os.path.isfile(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json')):
        raise BadInput('Thư mục này chưa được thiết lập thành dự án; thiết lập trước rồi mới cài gói hoặc cập nhật.\n'
                       'This folder is not set up as a project yet; set it up before installing packs or upgrading.')


def action(name, p):
    apply = bool(p.get('apply'))
    if name in ('upgrade', 'pack_add', 'pack_remove', 'pack_update', 'pack_confirm'):
        need_project()
    if name == 'init':
        args = ['--name', need_text(p, 'name', 'Cần nhập tên dự án / A project name is required.'),
                '--lang', 'en' if p.get('lang') == 'en' else 'vi']
        for k in ('purpose', 'outputs', 'style', 'sources', 'constraints', 'sensitivity'):
            v = (p.get(k) or '').strip()
            if v:
                args += ['--' + k, v]
        if os.path.isfile(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json')):
            args.append('--force')  # chạy lại: chỉ cập nhật PROJECT.md / re-run: only updates PROJECT.md
        return run_tool('init_project.py', args + ([] if apply else ['--dry-run']))
    if name == 'new_project':
        args = ['--name', need_text(p, 'name', 'Cần nhập tên công việc / A task name is required.'),
                '--lang', 'en' if p.get('lang') == 'en' else 'vi']
        if (p.get('dest') or '').strip():
            args += ['--dest', need_dir(p.get('dest'))]
        return run_tool('new_project.py', args + (['--apply'] if apply else []))
    if name == 'project_open':
        return open_project(p.get('target'), p.get('what'))
    if name == 'upgrade':
        return run_tool('upgrade_package.py', ['--from', need_dir(p.get('source'))] + (['--apply'] if apply else []))
    if name == 'upgrade_other':
        target = need_dir(p.get('project'))
        if os.path.normcase(os.path.abspath(target)) == os.path.normcase(ROOT):
            raise BadInput('Chọn thư mục dự án khác, không phải thư mục đang mở. / Choose another project folder, not this one.')
        return run_tool('upgrade_package.py', ['--project', target] + (['--apply'] if apply else []))
    if name == 'adopt':
        args = ['--project', need_dir(p.get('project')),
                '--name', need_text(p, 'name', 'Cần nhập tên dự án / A project name is required.'),
                '--lang', 'en' if p.get('lang') == 'en' else 'vi']
        return run_tool('adopt_project.py', args + (['--apply'] if apply else []))
    if name == 'pack_list':
        return run_tool('pack.py', ['list'])
    if name in ('pack_add', 'pack_remove'):
        # --confirm chỉ khi người dùng đã bấm xác nhận trên giao diện; không bao giờ mặc định / only after an explicit click, never a default
        return run_tool('pack.py', [name.split('_')[1], need_name(p.get('pack'))] + (['--confirm'] if name == 'pack_add' and p.get('confirm') else []))
    if name == 'pack_update':
        return run_tool('pack.py', ['update', need_name(p.get('pack'))] + (['--apply'] if apply else []) + (['--confirm'] if apply and p.get('confirm') else []))
    if name == 'pack_confirm':
        return run_tool('pack.py', ['confirm', need_name(p.get('pack'))])
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
    if name == 'library_sync':
        return library_sync_action(p, apply)
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
    if name == 'merge_diff':  # chỉ đọc; không lưu kết quả / read-only; the result is not stored
        try:
            diff = merge_center.diff(ROOT, need_text(p, 'path', 'Cần đường dẫn file hợp nhất.'))
        except ValueError as e:
            raise BadInput(str(e))
        return {'code': 0, 'out': '', 'cmd': '', 'result': make('success', message='Compared', changes=False, diff=diff)}
    if name in ('tx_resume', 'tx_rollback'):
        lang = 'en' if p.get('lang') == 'en' else 'vi'
        return run_tool('transaction.py', [name[3:], need_txid(p), '--project', ROOT, '--lang', lang])
    if name == 'diagnostics':
        rel = diagnostics_bundle()
        return {'code': 0, 'out': 'Đã tạo / Created: %s' % rel, 'cmd': '',
                'result': make('success', message='Diagnostics bundle created', changes=True,
                               files=[{'path': rel, 'action': 'created'}])}
    if name == 'history_clear':
        removed = ops_log.clear(ROOT)
        return {'code': 0, 'out': '', 'cmd': '',
                'result': make('success', message='History cleared', changes=removed,
                               files=[{'path': HISTORY_REL, 'action': 'removed'}] if removed else [])}
    raise BadInput('Thao tác không có / Unknown action: %s' % name)


# ------------------------------------------------------------------ gói chẩn đoán / diagnostics bundle
def _user_names():
    names = {os.environ.get(k) for k in ('USERNAME', 'USER', 'LOGNAME')}
    try:
        names.add(getpass.getuser())
    except Exception:  # không lấy được tên thì không có gì để che / no user name: nothing to hide
        pass
    return [n for n in names if n]


def mask_pairs():
    """Chuỗi cần che: thư mục project, thư mục người dùng, tên người dùng, kể cả dạng gạch chéo và dạng JSON.
    Strings to hide: project folder, home folder, user name; including slash and JSON-escaped forms."""
    pairs, home = [], os.path.expanduser('~')
    for raw, repl in ((ROOT, '<PROJECT>'), (os.path.realpath(ROOT), '<PROJECT>'), (home, '~'), (os.path.realpath(home), '~')):
        for form in {raw, raw.replace('\\', '/'), raw.replace('\\', '\\\\')}:
            if form:
                pairs.append((form, repl))
    pairs += [(n, '<USER>') for n in _user_names()]
    return sorted(pairs, key=lambda x: len(x[0]), reverse=True)


def mask_text(text, pairs):
    for raw, repl in pairs:
        text = re.sub(re.escape(raw), repl, text, flags=re.I)
    return text


def _mask_obj(value, pairs):
    if isinstance(value, dict):
        return {mask_text(str(k), pairs): _mask_obj(v, pairs) for k, v in value.items()}
    if isinstance(value, list):
        return [_mask_obj(v, pairs) for v in value]
    if isinstance(value, str):
        return mask_text(value, pairs)
    return value


def _diagnostic_components(rows):
    """Export only bounded component metadata; local status keeps interpreter paths."""
    fields = ('feature', 'needs', 'version', 'reason', 'jsonschema', 'fs')
    out = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = {}
        for key in fields:
            value = row.get(key)
            if key in row and (value is None or (isinstance(value, str) and
                    re.fullmatch(r'[A-Za-z0-9_.<>= -]{1,80}', value))):
                item[key] = value
        if type(row.get('usable')) is bool:
            item['usable'] = row['usable']
        out.append(item)
    return out


def diagnostics_bundle():
    """Ghi ZIP chẩn đoán (đã che đường dẫn và tên người dùng); trả về đường dẫn tương đối của ZIP.
    Writes the diagnostics ZIP with paths and user name masked; returns its package-relative path.
    Contains JSON only: no document text, no project name, no typed values."""
    info, _ = project_info()
    pairs = mask_pairs()
    merges = merge_center.scan(ROOT)
    by_state = {}
    for m in merges:
        by_state[m['state']] = by_state.get(m['state'], 0) + 1
    check = run_tool('check_package.py', ['--verify'])['result'] or {}
    data = {
        'schema': 'local-agent-workspace/diagnostics-v1',
        'created': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'package': {'version': rd('VERSION').strip(), 'installed_version': info.get('version')},
        'workspace_kind': workspace_kind(info),
        'python': {'version': sys.version.split()[0], 'implementation': platform.python_implementation()},
        'platform': {'system': platform.system(), 'release': platform.release(), 'machine': platform.machine()},
        'components': _diagnostic_components(components()),
        'merges': {'count': len(merges), 'by_state': by_state,
                   'items': [{'path': m['path'], 'pending': m['pending'], 'state': m['state'],
                              'origin': m['origin'], 'current_exists': m['current_exists']} for m in merges]},
        'transactions': transaction.incomplete(ROOT),
        'history': ops_log.read(ROOT),
        'package_check': {'status': check.get('status'), 'code': check.get('code'), 'message': check.get('message'),
                          'findings': [{'severity': f.get('severity'), 'message': f.get('message')}
                                       for f in (check.get('findings') or [])]},
    }
    text = mask_text(json.dumps(_mask_obj(data, pairs), ensure_ascii=False, indent=2), pairs)
    folder = os.path.join(ROOT, *DIAG_REL.split('/'))
    os.makedirs(folder, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    name, n = 'diagnostics-%s.zip' % stamp, 1
    while os.path.exists(os.path.join(folder, name)):
        n += 1
        name = 'diagnostics-%s-%d.zip' % (stamp, n)
    with zipfile.ZipFile(os.path.join(folder, name), 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('diagnostics.json', text.encode('utf-8'))
    return DIAG_REL + '/' + name


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


def open_project(target, what):
    """Mở thư mục hoặc bảng điều khiển của một project khác (vd. project vừa tạo). Chỉ nhận thư mục đã khởi tạo
    thành project của package này. / Open another project's folder or panel; only an initialised project folder."""
    t = os.path.abspath(os.path.expanduser((target or '').strip().strip('"')))
    info = os.path.join(t, '.agent', 'PACKAGE_INFO.json')
    try:
        ok = json.load(io.open(info, encoding='utf-8')).get('package') == 'local-agent-workspace'
    except (OSError, ValueError, AttributeError):
        ok = False
    if not ok or not os.path.isfile(os.path.join(t, 'tools', 'app.py')) or os.path.normcase(t) == os.path.normcase(ROOT):
        raise BadInput('Không phải thư mục dự án đã thiết lập / Not a set-up project folder: %s' % (target or ''))
    if what == 'panel':
        kw = {'cwd': t, 'stdin': subprocess.DEVNULL, 'stdout': subprocess.DEVNULL, 'stderr': subprocess.DEVNULL}
        if sys.platform.startswith('win'):
            kw['creationflags'] = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0)
        subprocess.Popen([sys.executable, os.path.join(t, 'tools', 'app.py')], **kw)
        msg = 'Đang mở bảng điều khiển dự án trong một tab mới của trình duyệt. / Opening the project panel in a new browser tab.'
    else:
        if sys.platform.startswith('win'):
            os.startfile(t)  # noqa
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', t])
        else:
            subprocess.Popen(['xdg-open', t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        msg = 'Đã mở thư mục dự án. / Opened the project folder.'
    return {'code': 0, 'out': msg, 'cmd': '', 'result': make('success', code=0, message=msg, changes=False)}


def open_path(rel):
    rel = (rel or '').strip().replace('\\', '/')
    target = os.path.normpath(os.path.join(ROOT, rel)) if rel else ROOT
    if not (target == ROOT or target.startswith(ROOT + os.sep)) or not os.path.exists(target):
        raise BadInput('Không mở được / Cannot open: %s' % rel)
    launch(target)
    return {'ok': True}


def launch(target):
    """Giao đường dẫn cho ứng dụng mặc định của hệ điều hành / hand a path to the operating system's default application."""
    if sys.platform.startswith('win'):
        os.startfile(target)  # noqa
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', target])
    else:
        subprocess.Popen(['xdg-open', target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ------------------------------------------------------------------ thư viện nguồn / source library (A-07)
def library_api(path, body):
    """Đường đọc của thư viện: route riêng, không qua run_api/_record nên không ghi lịch sử; chỉ đọc sổ đã lưu, không quét nguồn.
    The library read path: dedicated routes outside run_api/_record (nothing is logged); reads the saved index only, never scans sources.
    browse: duyệt/tìm/lọc nhóm. select: kiểm lại và tạo văn bản sao chép. open: mở đúng một nguồn sau khi gắn lại dòng và kiểm tiếp cận."""
    import library
    action_name = path.rsplit('/', 1)[-1]
    if action_name == 'browse':
        res = library.browse(ROOT, str(body.get('query') or '')[:500], str(body.get('group') or '')[:200])
        if not res['ok'] and res['kind'] == 'openpyxl_missing':
            res['message'] = 'CHƯA KIỂM ĐƯỢC: thư viện nguồn cần openpyxl. / NOT CHECKED: the source library requires openpyxl.'
            res['next_actions'] = ['Chạy / Run: python -m pip install openpyxl']
        return res
    if action_name == 'select':
        sels = body.get('selections')
        if not isinstance(sels, list) or not sels or len(sels) > 200:
            return {'ok': False, 'reason': 'bad_selection', 'items': []}
        book = library.read_book(ROOT)
        bad, recs = [], []
        for sel in sels:
            rec, why = library.rebind(ROOT, sel, book)
            if rec is not None and rec['identity'] != 'ok':
                why = rec['identity']  # no_id | dup_id | no_revision: không thành input đã định danh / not an identified input
            if why:
                bad.append({'row': sel.get('row') if isinstance(sel, dict) else None, 'reason': why})
            else:
                recs.append(rec)
        if bad:
            return {'ok': False, 'reason': 'rows', 'items': bad}
        return {'ok': True, 'count': len(recs), 'text': library.select_text(recs, book['snapshot'], 'en' if body.get('lang') == 'en' else 'vi')}
    if action_name == 'open':
        rec, why = library.rebind(ROOT, body.get('selection'))
        if why:
            return {'ok': False, 'reason': why}
        full, why = library.locate_source(ROOT, rec['locator'])
        if why:
            return {'ok': False, 'reason': why}
        try:
            launch(full)
        except OSError:
            return {'ok': False, 'reason': 'launch_failed'}
        return {'ok': True}
    if action_name in ('links', 'artifact-open', 'artifact-copy'):
        return artifacts_api(action_name, body)
    return None


def artifacts_api(action_name, body):
    """B-02: phụ lục/kết quả liên quan, mở đúng bản, sao chép đầu vào. Cùng helper với CLI tools/artifacts.py; đọc sổ đã lưu, không quét, không AI,
    không ghi sổ hay lịch sử. Registry chỉ ghi qua CLI/API preview→apply. / Same helpers as the CLI; reads the saved index; never writes the registry."""
    import artifacts, library
    try:
        if action_name == 'links':
            return artifacts.links(ROOT, body.get('selection'))
        if action_name == 'artifact-open':
            return artifacts.open_artifact(ROOT, body.get('selection'))
        return artifacts.copy_input(ROOT, body.get('selection'), 'en' if body.get('lang') == 'en' else 'vi')
    except (library.ContentError, artifacts.SyncError) as e:
        return {'ok': False, 'reason': getattr(e, 'code', None) or 'refused', 'message': str(e)}
    except SystemExit:  # thiếu openpyxl / openpyxl missing
        return {'ok': False, 'reason': 'index:openpyxl_missing'}


def library_sync_action(p, apply):
    """Xem trước / ghi sổ nguồn qua đúng library_sync.plan/apply (cùng writer với CLI). Ghi chỉ khi có expected_preview của bản đã xem.
    Preview / apply the source index through the same library_sync.plan/apply as the CLI. Apply needs the expected_preview of what was previewed."""
    import library, library_sync
    lang = 'en' if p.get('lang') == 'en' else 'vi'
    en = lang == 'en'
    try:
        if apply:
            exp = p.get('expected_preview')
            # thiếu thì bị từ chối: None sẽ là hành vi CLI / missing is refused: None would mean the CLI behaviour
            result = library_sync.apply(ROOT, (), {} if exp is None else exp)
        else:
            result = library_sync.plan(ROOT)
    except library_sync.PreviewMismatch as e:
        return {'code': 1, 'out': str(e), 'cmd': '', 'result': make(
            'blocked', code=1, message=str(e), changes=False, reason='PREVIEW_INVALID' if e.reason == 'invalid' else 'PREVIEW_STALE',
            next_actions=['Bấm xem trước lại rồi mới ghi. / Preview again before applying.'])}
    except library_sync.SyncError as e:
        return {'code': 1, 'out': str(e), 'cmd': '', 'result': make('blocked', code=1, message=str(e), changes=None, next_actions=[
            'Kiểm nguồn/sổ, giải quyết rồi xem trước lại. / Check the source/index, resolve it, then preview again.'])}
    except SystemExit:  # thiếu openpyxl: library.need_openpyxl đã thoát mã 2 / openpyxl missing: library.need_openpyxl exited with code 2
        msg = 'CHƯA KIỂM ĐƯỢC: thư viện nguồn cần openpyxl. / NOT CHECKED: the source library requires openpyxl.'
        return {'code': 2, 'out': msg, 'cmd': '', 'result': make(
            'not_checked', code=2, message=msg, changes=False, unchecked=[{'tool': 'library.py', 'reason': 'openpyxl_missing'}],
            next_actions=['Chạy / Run: python -m pip install openpyxl'])}
    changed = result['bytes'] is not None
    if apply:
        label = (('Source index updated.' if en else 'Đã cập nhật sổ nguồn.') if changed else ('Source index unchanged.' if en else 'Sổ nguồn không đổi.'))
    else:
        label = (('Source index preview.' if en else 'Xem trước cập nhật sổ nguồn.') if changed else ('Source index unchanged.' if en else 'Sổ nguồn không đổi.'))
    extra = dict(planned=len(result['changes']), rows=result['changes'], skipped=result['skipped'], candidates=result['candidates'],
                 scopes=result['scopes'], notices=result.get('notices') or [], protection=result.get('protection'))
    if apply:
        env = make('success', code=0, message=label, changes=changed,
                   files=[{'path': 'references/_INDEX.xlsx', 'action': 'update'}] if changed else [], **extra)
    else:
        env = make('preview' if changed else 'success', code=0, message=label, changes=None if changed else False, **extra)
        if changed:
            env['expected_preview'] = library_sync.preview_binding(result)  # client giữ tạm, gửi lại khi Apply / held by the client, sent back on Apply
    return {'code': 0, 'out': '\n'.join(library.sync_lines(result, label, True, lang)), 'cmd': '', 'result': env}


def draft_api(path, body):
    """Nháp hiện tại: route riêng, không qua run_api/_record nên không ghi lịch sử thao tác. Chỉ select (apply) ghi, và chỉ một marker STATE qua P-CTX1.
    Current draft: a dedicated route, outside run_api/_record, so the operations log is untouched. Only select/apply writes: one STATE marker via P-CTX1."""
    try:
        import current_draft
    except Exception as e:
        return make('error', code=4, message='Không nạp được current_draft / current_draft could not load: %s' % type(e).__name__,
                    changes=False, result='UNAVAILABLE', reason='HELPER_UNAVAILABLE')
    rid = body.get('rid')
    action = path.rsplit('/', 1)[-1]
    if action == 'status':
        return current_draft.status(ROOT)
    if action == 'list':
        return current_draft.list_candidates(ROOT)
    if action == 'select':
        if body.get('apply') is True:
            return current_draft.select_apply(ROOT, rid, body.get('expected_state'), body.get('expected_selection'))
        return current_draft.select_preview(ROOT, rid)
    if action == 'open':
        ack = body.get('ack')
        if ack not in (None, 'changed', 'unverified'):
            return make('error', code=4, message='Invalid acknowledgement', changes=False, result='ERROR', reason='ACK_INVALID')
        return current_draft.open_draft(ROOT, rid, ack)
    return None


_REPLACE_STATUS = {'replaced': ('success', 0, True), 'noop': ('success', 0, False), 'stale': ('blocked', 1, False),
                   'blocked': ('blocked', 1, False), 'error': ('error', 1, False), 'partial': ('partial', 1, None)}
# D-01c: changes theo thực tế; snapshot có thể đã ghi dù .new chưa chuyển / changes follow what happened; the snapshot may be written without the move
_FINISH_STATUS = {'finished': ('success', 0, True), 'still_pending': ('partial', 1, True), 'partial': ('partial', 1, None),
                  'conflict': ('partial', 1, None), 'unknown': ('partial', 1, None), 'stale': ('blocked', 1, False),
                  'blocked': ('blocked', 1, False), 'error': ('error', 1, False)}


def merge_api(path, body):
    """D-01b: xem trước và thay MỘT tài liệu hướng dẫn bằng bản .new đã xem (giữ .new, lưu cả hai bản). Route riêng, không qua run_api/_record:
    không ghi lịch sử thao tác. preview chỉ đọc. replace ghi qua merge_center.apply_replace (một Transaction), phải gửi lại hai hash của preview.
    Preview and replace of ONE guide with its previewed .new copy (the .new is kept, both versions are stored). Dedicated routes outside
    run_api/_record, so the operations log is untouched. preview is read-only; replace writes through merge_center.apply_replace (one
    Transaction) and must send back both hashes from the preview.
    D-01c: finish-preview / finish / finish-observe giữ nguyên bản hiện hành và đưa .new vào archive; cùng quy tắc: ngoài run_api/_record, preview và observe chỉ đọc.
    D-01c: finish-preview / finish / finish-observe keep the current file and move the .new into the archive; same rules, outside run_api/_record, preview and observe are read-only."""
    name = path.rsplit('/', 1)[-1]
    if name == 'preview':
        pv = merge_center.preview_replace(ROOT, body.get('path'))
        bad = pv['reason'] == 'invalid_path'
        return make('blocked' if bad else 'success', code=2 if bad else 0, changes=False, replace_preview=pv,
                    message='Đường dẫn không hợp lệ / Invalid path' if bad else 'Preview only; nothing was written / Chỉ xem trước, chưa ghi gì')
    if name == 'replace':
        res = merge_center.apply_replace(ROOT, body.get('path'), body.get('current_sha256'), body.get('candidate_sha256'))
        status_value, code, changes = _REPLACE_STATUS[res['outcome']]
        files = []
        if res['outcome'] == 'replaced':
            files = [{'path': res['path'], 'action': 'replaced'}] + [
                {'path': res['archive'][k], 'action': 'created'} for k in ('current', 'incoming', 'record')]
        return make(status_value, code=code, changes=changes, files=files, replace=res, message=res['outcome'],
                    transaction=res.get('txid') if res['outcome'] == 'partial' else None)
    if name == 'finish-preview':  # D-01c: chỉ đọc, không tạo file/runtime / read-only
        pv = merge_center.preview_finish(ROOT, body.get('path'))
        bad = pv['reason'] == 'invalid_path'
        return make('blocked' if bad else 'success', code=2 if bad else 0, changes=False, finish_preview=pv,
                    message='Đường dẫn không hợp lệ / Invalid path' if bad else 'Preview only; nothing was written / Chỉ xem trước, chưa ghi gì')
    if name == 'finish-observe':  # D-01c: chỉ đọc; không hoàn tất, không retry / read-only; completes nothing, retries nothing
        obs = merge_center.observe_finish(ROOT, body.get('path'), body.get('current_sha256'), body.get('candidate_sha256'), body.get('finish_id'))
        refused = obs['state'] == 'refused'
        return make('blocked' if refused else 'success', code=2 if refused else 0, changes=False, finish_observation=obs,
                    message='Chỉ quan sát; chưa ghi gì / Observation only; nothing was written')
    if name == 'finish':
        res = merge_center.apply_finish(ROOT, body.get('path'), body.get('current_sha256'), body.get('candidate_sha256'), body.get('finish_id'))
        status_value, code, changes = _FINISH_STATUS[res['outcome']]
        saved = res.get('snapshot_saved') is True
        if changes is None and saved:
            changes = True  # snapshot đã ghi dù chưa chuyển được .new / the snapshot is written even if the .new was not moved
        files = []
        if saved:
            arc = res['archive']
            files = [{'path': arc[k], 'action': 'created'} for k in ('current', 'incoming', 'record')]
            if res['outcome'] == 'finished':
                files.append({'path': arc['retired'], 'action': 'moved_from_' + res['pending']})
        return make(status_value, code=code, changes=changes, files=files, finish=res, message=res['outcome'],
                    transaction=res.get('txid') if res['outcome'] not in ('finished', 'stale', 'blocked', 'error') else None)
    return None


def _record(name, res, started):
    """Một dòng lịch sử cho mỗi thao tác; lỗi ghi nhật ký không làm hỏng thao tác / One line per action;
    a logging failure never breaks the action."""
    try:
        result = res.get('result') or {}
        status_value = result.get('status') or ('success' if res.get('code') == 0 else 'error')
        tx = result.get('transaction')
        ops_log.record(ROOT, name if name in ACTION_NAMES else 'unknown', status_value, res.get('code', -1),
                       len(result.get('files') or []), tx if isinstance(tx, str) else None,
                       int((time.time() - started) * 1000))
    except Exception:
        pass


def unexpected_result(e):
    """Envelope cho lỗi bất ngờ của bảng điều khiển / envelope for an unexpected panel error."""
    return make('error', code=-1, message='Lỗi bất ngờ trong bảng điều khiển / Unexpected panel error: %s' % type(e).__name__,
                changes=None, next_actions=[
                    'Xem trang Tình trạng ứng dụng: nếu có giao dịch dở, chọn Tiếp tục hoặc Phục hồi. / '
                    'Open App status: if a transaction is unfinished, choose Resume or Roll back.',
                    'Nếu lỗi lặp lại, tạo gói chẩn đoán và gửi cho người hỗ trợ. / '
                    'If it happens again, create a diagnostics bundle and send it to support.'])


def run_api(body):
    """Chạy một thao tác và ghi lịch sử; trả về (mã HTTP, nội dung) / Run one action and record it; returns (HTTP code, payload)."""
    name = body.get('action', '')
    if not isinstance(name, str):
        name = ''
    params = body.get('params') or {}
    if not isinstance(params, dict):
        params = {}
    started, http_code = time.time(), 200
    try:
        res = action(name, params)
    except BadInput as e:
        res = {'code': 2, 'out': str(e), 'cmd': '', 'input_error': True,
               'result': make('blocked', code=2, message=str(e), changes=False)}
    except Exception as e:  # lỗi bất ngờ vẫn trả về trang / unexpected errors still reach the page
        res, http_code = {'code': -1, 'out': 'Lỗi / Error: %r' % (e,), 'cmd': '', 'result': unexpected_result(e)}, 500
    if name != 'history_clear' and name not in NO_LOG_ACTIONS:  # xóa lịch sử, đọc thư viện: không ghi dòng nào / clearing the history and reading the library write no line
        _record(name, res, started)
    return http_code, res


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
                code, payload = run_api(body)
                return self._send(code, payload)
            if path in ('/api/draft/status', '/api/draft/list', '/api/draft/select', '/api/draft/open'):
                return self._send(200, draft_api(path, body if isinstance(body, dict) else {}))
            if path in ('/api/merge/preview', '/api/merge/replace', '/api/merge/finish-preview', '/api/merge/finish', '/api/merge/finish-observe'):
                return self._send(200, merge_api(path, body if isinstance(body, dict) else {}))
            if path in ('/api/library/browse', '/api/library/select', '/api/library/open', '/api/library/links', '/api/library/artifact-open', '/api/library/artifact-copy'):
                return self._send(200, library_api(path, body if isinstance(body, dict) else {}))
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
            return self._send(500, {'code': -1, 'out': 'Lỗi / Error: %r' % (e,), 'cmd': '', 'result': unexpected_result(e)})
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
