#!/usr/bin/env python3
"""Quản lý "gói lĩnh vực" (domain pack): bộ skill và mẫu của một lĩnh vực, cài theo nhu cầu vào từng project.
Manage "domain packs": a set of skills and templates for one domain, installed per project on demand.

Dùng / Usage (chạy từ thư mục project / run from the project folder):
  python tools/pack.py list                 liệt kê gói có sẵn và gói đã cài / list available and installed packs
  python tools/pack.py add <tên>            cài gói vào skills/local/packs/<tên>/ và ghi vào .agent/SKILL_INDEX.md
  python tools/pack.py update <tên>         cập nhật gói đã cài lên bản trong packs/ (file bạn đã sửa -> <tên>.new)
  python tools/pack.py remove <tên>         gỡ gói: chuyển vào archive/, bỏ khỏi SKILL_INDEX (không xóa file)
  python tools/pack.py check [<tên>]        kiểm tra cấu trúc gói (người viết gói dùng)
  python tools/pack.py new <tên>            tạo gói mới trong packs/<tên>/ từ packs/_template (người viết gói dùng)

Một gói là thư mục packs/<tên>/ có pack.json và skills/<skill-id>/SKILL.md. Xem packs/README.md.
Chỉ cần Python 3.8+, không dùng mạng.
"""
import argparse, datetime, hashlib, io, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
INSTALL_DIR = 'skills/local/packs'
SHARED = 'skills/local/shared'
NAME_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
ALLOWED_TOP = {'pack.json', 'README.md', 'skills', 'templates', 'references'}
LANG = 'vi'

def L(vi, en): return en if LANG == 'en' else vi
def P(rel): return os.path.join(ROOT, *rel.split('/'))
def rd(rel): return io.open(P(rel), encoding='utf-8', newline='').read()
def wr(rel, text):
    os.makedirs(os.path.dirname(P(rel)), exist_ok=True)
    io.open(P(rel), 'w', encoding='utf-8', newline='').write(text)

def vt(v):
    try:
        return tuple(int(x) for x in v.split('.'))
    except ValueError:
        return (0,)

def sha_file(path):
    return hashlib.sha256(open(path, 'rb').read().replace(b'\r\n', b'\n')).hexdigest()

def walk(base):
    out = []
    for d, dirs, files in os.walk(base):
        dirs.sort()
        for f in sorted(files):
            out.append(os.path.relpath(os.path.join(d, f), base).replace(os.sep, '/'))
    return out

def core_version():
    try:
        return rd('VERSION').strip()
    except OSError:
        return '0.0.0'

def core_skills():
    d = P(SHARED)
    return sorted(x for x in os.listdir(d) if os.path.isfile(os.path.join(d, x, 'SKILL.md'))) if os.path.isdir(d) else []

def loc(v):
    """Chuỗi hai ngôn ngữ {'vi':..,'en':..} -> chuỗi theo LANG."""
    if isinstance(v, dict):
        return v.get(LANG) or v.get('vi') or v.get('en') or ''
    return str(v or '')

# ---------------------------------------------------------------- kiểm tra gói
def validate_pack(base, name):
    """Trả về danh sách lỗi (chuỗi) của thư mục gói `base`. `name` là tên thư mục."""
    import check_package as cp
    errs = []
    pj = os.path.join(base, 'pack.json')
    if not os.path.isfile(pj):
        return ['%s: thiếu pack.json.' % name]
    try:
        meta = json.load(io.open(pj, encoding='utf-8'))
    except ValueError as e:
        return ['%s/pack.json không phải JSON hợp lệ (%s).' % (name, e)]
    tmpl = name.startswith('_')
    if meta.get('name') != name:
        errs.append('%s/pack.json: "name" (%r) phải trùng tên thư mục.' % (name, meta.get('name')))
    if not tmpl and not NAME_RE.match(name):
        errs.append('%s: tên gói phải là chữ thường, số, dấu gạch ngang.' % name)
    if not re.fullmatch(r'\d+\.\d+\.\d+', str(meta.get('version', ''))):
        errs.append('%s/pack.json: "version" phải dạng MAJOR.MINOR.PATCH.' % name)
    if not re.fullmatch(r'\d+\.\d+', str(meta.get('requires_core', ''))):
        errs.append('%s/pack.json: "requires_core" phải dạng MAJOR.MINOR (bản package tối thiểu).' % name)
    for k in ('title', 'description'):
        v = meta.get(k)
        if not (isinstance(v, dict) and (v.get('vi') or v.get('en'))):
            errs.append('%s/pack.json: "%s" cần dạng {"vi": "...", "en": "..."} (ít nhất một ngôn ngữ).' % (name, k))
    skills = meta.get('skills')
    if not isinstance(skills, list) or not skills or len(set(skills)) != len(skills):
        errs.append('%s/pack.json: "skills" phải là danh sách không rỗng, không trùng.' % name)
        skills = []
    for top in sorted(os.listdir(base)):
        if top not in ALLOWED_TOP:
            errs.append('%s: mục "%s" không nằm trong cấu trúc gói (%s).' % (name, top, ', '.join(sorted(ALLOWED_TOP))))
    core = set(core_skills())
    for sid in skills:
        sp = os.path.join(base, 'skills', sid, 'SKILL.md')
        if not NAME_RE.match(str(sid)):
            errs.append('%s: skill id "%s" không hợp lệ.' % (name, sid)); continue
        if sid in core:
            errs.append('%s: skill id "%s" trùng skill của package (đổi tên).' % (name, sid))
        if not os.path.isfile(sp):
            errs.append('%s: thiếu skills/%s/SKILL.md.' % (name, sid)); continue
        txt = io.open(sp, encoding='utf-8').read()
        fm = cp.frontmatter(txt)
        if fm is None:
            errs.append('%s/skills/%s/SKILL.md thiếu frontmatter.' % (name, sid)); continue
        if fm.get('name') != sid: errs.append('%s/skills/%s: "name" (%r) không khớp thư mục.' % (name, sid, fm.get('name')))
        if len(fm.get('description', '')) < 40: errs.append('%s/skills/%s: description thiếu hoặc quá ngắn.' % (name, sid))
        if not re.search(r'^\s+version:\s*"?\d', txt, re.M): errs.append('%s/skills/%s: thiếu metadata.version.' % (name, sid))
    skills_dir = os.path.join(base, 'skills')
    if os.path.isdir(skills_dir):
        for d in sorted(os.listdir(skills_dir)):
            if d not in skills:
                errs.append('%s: thư mục skills/%s không có trong pack.json.' % (name, d))
    for rel in walk(base):
        if '..' in rel.split('/') or rel.startswith('/'):
            errs.append('%s: đường dẫn không hợp lệ %s.' % (name, rel))
        try:
            if rel.endswith(('.md', '.json', '.txt', '.html')):
                io.open(os.path.join(base, rel), encoding='utf-8').read()
        except UnicodeDecodeError:
            errs.append('%s/%s không phải UTF-8.' % (name, rel))
    return errs

# ---------------------------------------------------------------- bản ghi cài đặt
def available():
    out = {}
    d = P('packs')
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            if not n.startswith('_') and os.path.isfile(os.path.join(d, n, 'pack.json')):
                try:
                    out[n] = json.load(io.open(os.path.join(d, n, 'pack.json'), encoding='utf-8'))
                except ValueError:
                    pass
    return out

def installed():
    out = {}
    d = P(INSTALL_DIR)
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            f = os.path.join(d, n, '.pack-install.json')
            if os.path.isfile(f):
                try:
                    out[n] = json.load(io.open(f, encoding='utf-8'))
                except ValueError:
                    pass
    return out

def index_rows(name, meta):
    rows = []
    for sid in meta['skills']:
        sp = P('packs/%s/skills/%s/SKILL.md' % (name, sid))
        import check_package as cp
        fm = cp.frontmatter(io.open(sp, encoding='utf-8').read()) or {}
        desc = re.sub(r'\s*(Kích hoạt khi|Triggers when).*$', '', fm.get('description', ''), flags=re.S).strip().replace('|', '/')
        rows.append('| %s | LOCAL | PACK | %s/%s/skills/%s/SKILL.md | %s | AVAILABLE | Gói/Pack %s v%s |' %
                    (sid, INSTALL_DIR, name, sid, desc[:220], name, meta['version']))
    return rows

def edit_index(name, rows):
    """Bỏ mọi dòng của gói `name` khỏi SKILL_INDEX rồi chèn `rows` (nếu có) sau dòng bảng cuối."""
    f = '.agent/SKILL_INDEX.md'
    if not os.path.isfile(P(f)):
        return False
    lines = rd(f).split('\n')
    tag = 'Gói/Pack %s v' % name
    lines = [l for l in lines if not (l.startswith('| ') and tag in l)]
    if rows:
        last = max(i for i, l in enumerate(lines) if l.startswith('| ') and '---' not in l and i < next((j for j, x in enumerate(lines) if x.startswith('## ')), len(lines)))
        lines[last + 1:last + 1] = rows
    wr(f, '\n'.join(lines))
    return True

# ---------------------------------------------------------------- lệnh
def cmd_list(a):
    av, ins = available(), installed()
    print(L('Gói có sẵn trong packs/:', 'Packs available in packs/:'))
    if not av:
        print('  ' + L('(chưa có gói nào ngoài mẫu _template)', '(none yet apart from the _template skeleton)'))
    for n, m in av.items():
        st = ''
        if n in ins:
            st = L(' [đã cài v%s%s]', ' [installed v%s%s]') % (ins[n]['version'], L(', có bản mới v%s', ', newer v%s') % m['version'] if vt(m['version']) > vt(ins[n]['version']) else '')
        print('  - %s v%s: %s%s' % (n, m['version'], loc(m.get('title')), st))
    extra = [n for n in ins if n not in av]
    for n in extra:
        print('  - %s v%s %s' % (n, ins[n]['version'], L('[đã cài; không còn trong packs/]', '[installed; no longer in packs/]')))

def need(name, kind):
    if name not in kind:
        sys.exit(L('Không thấy gói "%s". Dùng "python tools/pack.py list".', 'Pack "%s" not found. Use "python tools/pack.py list".') % name)

def cmd_add(a):
    av, ins = available(), installed()
    need(a.name, av)
    if a.name in ins:
        sys.exit(L('Gói "%s" đã cài (v%s). Dùng "update" để cập nhật.', 'Pack "%s" is already installed (v%s). Use "update".') % (a.name, ins[a.name]['version']))
    meta = av[a.name]
    errs = validate_pack(P('packs/' + a.name), a.name)
    if errs:
        sys.exit(L('Gói chưa hợp lệ:\n  ', 'The pack is not valid:\n  ') + '\n  '.join(errs))
    if vt(core_version()) < vt(meta['requires_core'] + '.0'):
        sys.exit(L('Gói cần package >= %s (đang là %s). Nâng cấp package trước (tools/upgrade_package.py).', 'The pack needs package >= %s (this is %s). Upgrade the package first (tools/upgrade_package.py).') % (meta['requires_core'], core_version()))
    clash = [s for s in meta['skills'] for o, im in ins.items() if s in im.get('skills', [])]
    if clash:
        sys.exit(L('Trùng skill id với gói đã cài: %s', 'Skill id clashes with an installed pack: %s') % ', '.join(clash))
    dst = '%s/%s' % (INSTALL_DIR, a.name)
    if os.path.exists(P(dst)):
        sys.exit(L('%s đã tồn tại; không ghi đè.', '%s already exists; not overwriting.') % dst)
    files = {}
    for rel in walk(P('packs/' + a.name)):
        os.makedirs(os.path.dirname(P('%s/%s' % (dst, rel))), exist_ok=True)
        shutil.copyfile(P('packs/%s/%s' % (a.name, rel)), P('%s/%s' % (dst, rel)))
        files[rel] = sha_file(P('%s/%s' % (dst, rel)))
    wr(dst + '/.pack-install.json', json.dumps({'name': a.name, 'version': meta['version'], 'skills': meta['skills'],
        'installed': datetime.date.today().isoformat(), 'files': files}, ensure_ascii=False, indent=2) + '\n')
    ok = edit_index(a.name, index_rows(a.name, meta))
    print(L('Đã cài gói %s v%s: %d skill (%s).', 'Installed pack %s v%s: %d skills (%s).') % (a.name, meta['version'], len(meta['skills']), ', '.join(meta['skills'])))
    print(L('Đã ghi vào .agent/SKILL_INDEX.md.', 'Recorded in .agent/SKILL_INDEX.md.') if ok else L('Chưa có .agent/SKILL_INDEX.md: hãy tự thêm dòng skill.', 'No .agent/SKILL_INDEX.md: add the skill rows yourself.'))

def cmd_update(a):
    av, ins = available(), installed()
    need(a.name, ins); need(a.name, av)
    old, meta = ins[a.name], av[a.name]
    errs = validate_pack(P('packs/' + a.name), a.name)
    if errs:
        sys.exit(L('Gói trong packs/ chưa hợp lệ:\n  ', 'The pack in packs/ is not valid:\n  ') + '\n  '.join(errs))
    dst = '%s/%s' % (INSTALL_DIR, a.name)
    upd, conf, add = [], [], []
    newfiles = {}
    for rel in walk(P('packs/' + a.name)):
        newfiles[rel] = sha_file(P('packs/%s/%s' % (a.name, rel)))
    for rel, h in newfiles.items():
        d = '%s/%s' % (dst, rel)
        if not os.path.isfile(P(d)):
            add.append(rel)
        elif sha_file(P(d)) == h:
            continue
        elif sha_file(P(d)) == old['files'].get(rel):
            upd.append(rel)
        else:
            conf.append(rel)
    print(L('Gói %s: v%s -> v%s', 'Pack %s: v%s -> v%s') % (a.name, old['version'], meta['version']))
    for k, vi, en, it in (('u', 'Cập nhật', 'Updated', upd), ('a', 'Thêm', 'Added', add), ('c', 'XUNG ĐỘT (lưu <tên>.new)', 'CONFLICT (saved as <name>.new)', conf)):
        if it:
            print('%s: %s' % (L(vi, en), ', '.join(it)))
    if not (upd or add or conf):
        print(L('Không có gì cần cập nhật.', 'Nothing to update.')); return
    if not a.apply:
        print(L('[BÁO CÁO] Thêm --apply để thực hiện.', '[REPORT] Add --apply to carry it out.')); return
    for rel in upd + add:
        os.makedirs(os.path.dirname(P('%s/%s' % (dst, rel))), exist_ok=True)
        shutil.copyfile(P('packs/%s/%s' % (a.name, rel)), P('%s/%s' % (dst, rel)))
    for rel in conf:
        shutil.copyfile(P('packs/%s/%s' % (a.name, rel)), P('%s/%s.new' % (dst, rel)))
    old.update({'version': meta['version'], 'skills': meta['skills'], 'files': newfiles, 'updated': datetime.date.today().isoformat()})
    wr(dst + '/.pack-install.json', json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    edit_index(a.name, index_rows(a.name, meta))
    print(L('Đã cập nhật.', 'Updated.'))

def cmd_remove(a):
    ins = installed()
    need(a.name, ins)
    stamp = datetime.date.today().strftime('%Y%m%d')
    dst = 'archive/packs-removed-%s-%s' % (a.name, stamp)
    n = 1
    while os.path.exists(P(dst)):
        n += 1; dst = 'archive/packs-removed-%s-%s-%d' % (a.name, stamp, n)
    os.makedirs(os.path.dirname(P(dst)), exist_ok=True)
    shutil.move(P('%s/%s' % (INSTALL_DIR, a.name)), P(dst))
    edit_index(a.name, None)
    print(L('Đã gỡ gói %s: thư mục chuyển vào %s, bỏ khỏi SKILL_INDEX. Không có file nào bị xóa.', 'Removed pack %s: folder moved to %s, dropped from SKILL_INDEX. No file was deleted.') % (a.name, dst))

def cmd_check(a):
    names = [a.name] if a.name else sorted(n for n in os.listdir(P('packs')) if os.path.isdir(P('packs/' + n))) if os.path.isdir(P('packs')) else []
    bad = 0
    for n in names:
        e = validate_pack(P('packs/' + n), n)
        print('%s: %s' % (n, 'OK' if not e else '%d lỗi / errors' % len(e)))
        for x in e: print('  - ' + x)
        bad += len(e)
    ins = installed()
    idx = rd('.agent/SKILL_INDEX.md') if os.path.isfile(P('.agent/SKILL_INDEX.md')) else ''
    for n, m in ins.items():
        for sid in m['skills']:
            if not os.path.isfile(P('%s/%s/skills/%s/SKILL.md' % (INSTALL_DIR, n, sid))):
                print('  - %s: thiếu / missing %s' % (n, sid)); bad += 1
            if idx and ('| %s | LOCAL | PACK |' % sid) not in idx:
                print('  - %s: skill %s chưa có trong SKILL_INDEX / not in SKILL_INDEX' % (n, sid)); bad += 1
    sys.exit(1 if bad else 0)

def cmd_new(a):
    if not NAME_RE.match(a.name):
        sys.exit('Tên gói phải là chữ thường, số, dấu gạch ngang (ví dụ: logistics). / Use lowercase letters, digits and hyphens.')
    if os.path.exists(P('packs/' + a.name)):
        sys.exit('packs/%s đã tồn tại. / already exists.' % a.name)
    if not os.path.isdir(P('packs/_template')):
        sys.exit('Thiếu packs/_template. / packs/_template is missing.')
    for rel in walk(P('packs/_template')):
        s = P('packs/_template/' + rel)
        d = rel.replace('example-skill', a.name + '-example')
        os.makedirs(os.path.dirname(P('packs/%s/%s' % (a.name, d))), exist_ok=True)
        txt = io.open(s, encoding='utf-8', newline='').read().replace('example-skill', a.name + '-example').replace('"_template"', '"%s"' % a.name).replace('_template', a.name)
        wr('packs/%s/%s' % (a.name, d), txt)
    print('Đã tạo packs/%s/. Sửa pack.json, đổi tên và viết skill trong skills/, rồi chạy: python tools/pack.py check %s' % (a.name, a.name))
    print('Created packs/%s/. Edit pack.json, rename and write the skills in skills/, then run: python tools/pack.py check %s' % (a.name, a.name))

def main():
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('list').set_defaults(f=cmd_list)
    for c, f in (('add', cmd_add), ('update', cmd_update), ('remove', cmd_remove), ('new', cmd_new)):
        s = sub.add_parser(c); s.add_argument('name'); s.set_defaults(f=f)
        if c == 'update':
            s.add_argument('--apply', action='store_true')
    s = sub.add_parser('check'); s.add_argument('name', nargs='?'); s.set_defaults(f=cmd_check)
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        LANG = json.loads(rd('.agent/PACKAGE_INFO.json')).get('language', 'vi')
    except (OSError, ValueError):
        pass
    a.f(a)

if __name__ == '__main__':
    main()
