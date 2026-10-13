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
import argparse, datetime, hashlib, io, json, os, re, shutil, sys, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from result_schema import emit, make
INSTALL_DIR = 'skills/local/packs'
SHARED = 'skills/local/shared'
NAME_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
ALLOWED_TOP = {'pack.json', 'README.md', 'skills', 'templates', 'references'}
LANG = 'vi'

def L(vi, en): return en if LANG == 'en' else vi
def P(rel): return os.path.join(ROOT, *rel.split('/'))
RESULT_REQUESTED = '--result-json' in sys.argv  # cờ ẩn: phát một kết quả có cấu trúc / hidden flag: emit one structured result
LAST_RESULT = None
DONE = []  # file đã ghi trong lượt này / files written in this run, for partial results

def set_result(status, code, message, **kw):
    global LAST_RESULT
    LAST_RESULT = make(status, code=code, message=message, **kw)

def stop(msg, status='blocked', **kw):
    """Như sys.exit(msg) (mã 1), nhưng ghi kết quả có cấu trúc trước / Like sys.exit(msg) (code 1), recording the structured result first."""
    set_result(status, 1, msg, changes=False, **kw)
    sys.exit(msg)

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
    packs = [{'name': n, 'version': m.get('version'), 'installed': ins[n].get('version') if n in ins else None, 'available': True} for n, m in av.items()]
    packs += [{'name': n, 'version': None, 'installed': ins[n].get('version'), 'available': False} for n in extra]
    set_result('success', 0, L('%d gói trong packs/, %d gói đã cài.', '%d packs in packs/, %d installed.') % (len(av), len(ins)), changes=False, packs=packs)

def need(name, kind):
    if name not in kind:
        stop(L('Không thấy gói "%s". Dùng "python tools/pack.py list".', 'Pack "%s" not found. Use "python tools/pack.py list".') % name, pack=name)

def cmd_add(a):
    av, ins = available(), installed()
    need(a.name, av)
    if a.name in ins:
        stop(L('Gói "%s" đã cài (v%s). Dùng "update" để cập nhật.', 'Pack "%s" is already installed (v%s). Use "update".') % (a.name, ins[a.name]['version']), pack=a.name)
    meta = av[a.name]
    errs = validate_pack(P('packs/' + a.name), a.name)
    if errs:
        stop(L('Gói chưa hợp lệ:\n  ', 'The pack is not valid:\n  ') + '\n  '.join(errs), pack=a.name, findings=[{'pack': a.name, 'message': x} for x in errs])
    if vt(core_version()) < vt(meta['requires_core'] + '.0'):
        stop(L('Gói cần package >= %s (đang là %s). Nâng cấp package trước (tools/upgrade_package.py).', 'The pack needs package >= %s (this is %s). Upgrade the package first (tools/upgrade_package.py).') % (meta['requires_core'], core_version()), pack=a.name)
    clash = [s for s in meta['skills'] for o, im in ins.items() if s in im.get('skills', [])]
    if clash:
        stop(L('Trùng skill id với gói đã cài: %s', 'Skill id clashes with an installed pack: %s') % ', '.join(clash), pack=a.name)
    dst = '%s/%s' % (INSTALL_DIR, a.name)
    if os.path.exists(P(dst)):
        stop(L('%s đã tồn tại; không ghi đè.', '%s already exists; not overwriting.') % dst, pack=a.name)
    files = {}
    for rel in walk(P('packs/' + a.name)):
        os.makedirs(os.path.dirname(P('%s/%s' % (dst, rel))), exist_ok=True)
        shutil.copyfile(P('packs/%s/%s' % (a.name, rel)), P('%s/%s' % (dst, rel)))
        DONE.append({'path': '%s/%s' % (dst, rel), 'action': 'add'})
        files[rel] = sha_file(P('%s/%s' % (dst, rel)))
    wr(dst + '/.pack-install.json', json.dumps({'name': a.name, 'version': meta['version'], 'skills': meta['skills'],
        'installed': datetime.date.today().isoformat(), 'files': files}, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'add'})
    ok = edit_index(a.name, index_rows(a.name, meta))
    if ok:
        DONE.append({'path': '.agent/SKILL_INDEX.md', 'action': 'index'})
    set_result('success', 0, L('Đã cài gói %s v%s.', 'Installed pack %s v%s.') % (a.name, meta['version']), changes=True,
               pack=a.name, version=meta['version'], skills=meta['skills'], files=list(DONE),
               next_actions=[] if ok else [L('Thêm dòng skill vào .agent/SKILL_INDEX.md (file này chưa có).', 'Add the skill rows to .agent/SKILL_INDEX.md (the file is missing).')])
    print(L('Đã cài gói %s v%s: %d skill (%s).', 'Installed pack %s v%s: %d skills (%s).') % (a.name, meta['version'], len(meta['skills']), ', '.join(meta['skills'])))
    print(L('Đã ghi vào .agent/SKILL_INDEX.md.', 'Recorded in .agent/SKILL_INDEX.md.') if ok else L('Chưa có .agent/SKILL_INDEX.md: hãy tự thêm dòng skill.', 'No .agent/SKILL_INDEX.md: add the skill rows yourself.'))

def cmd_update(a):
    av, ins = available(), installed()
    need(a.name, ins); need(a.name, av)
    old, meta = ins[a.name], av[a.name]
    errs = validate_pack(P('packs/' + a.name), a.name)
    if errs:
        stop(L('Gói trong packs/ chưa hợp lệ:\n  ', 'The pack in packs/ is not valid:\n  ') + '\n  '.join(errs), pack=a.name, findings=[{'pack': a.name, 'message': x} for x in errs])
    dst = '%s/%s' % (INSTALL_DIR, a.name)
    index_file = '.agent/SKILL_INDEX.md'
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
    versions = dict(pack=a.name, from_version=old.get('version'), to_version=meta['version'])
    if not (upd or add or conf):
        print(L('Không có gì cần cập nhật.', 'Nothing to update.'))
        set_result('success', 0, L('Gói đã đủ bản mới; không có gì cần cập nhật.', 'The pack is up to date; nothing to update.'), changes=False, **versions)
        return
    plan = [{'path': '%s/%s' % (dst, r), 'action': 'update'} for r in upd] + [{'path': '%s/%s' % (dst, r), 'action': 'add'} for r in add] \
        + [{'path': '%s/%s.new' % (dst, r), 'action': 'merge'} for r in conf]
    if not a.apply:
        print(L('[BÁO CÁO] Thêm --apply để thực hiện.', '[REPORT] Add --apply to carry it out.'))
        if os.path.isfile(P(index_file)):
            plan.append({'path': index_file, 'action': 'index'})
        set_result('preview', 0, L('Xem trước cập nhật gói; chưa ghi file nào.', 'Pack update preview; no file written yet.'), changes=True, files=plan,
                   next_actions=[L('Thêm --apply để cập nhật.', 'Add --apply to update.')] +
                   ([L('Sau khi cập nhật, hợp nhất các file .new.', 'After the update, merge the .new files.')] if conf else []), **versions)
        return
    for rel in upd + add:
        os.makedirs(os.path.dirname(P('%s/%s' % (dst, rel))), exist_ok=True)
        shutil.copyfile(P('packs/%s/%s' % (a.name, rel)), P('%s/%s' % (dst, rel)))
        DONE.append({'path': '%s/%s' % (dst, rel), 'action': 'update' if rel in upd else 'add'})
    for rel in conf:
        shutil.copyfile(P('packs/%s/%s' % (a.name, rel)), P('%s/%s.new' % (dst, rel)))
        DONE.append({'path': '%s/%s.new' % (dst, rel), 'action': 'merge'})
    old.update({'version': meta['version'], 'skills': meta['skills'], 'files': newfiles, 'updated': datetime.date.today().isoformat()})
    wr(dst + '/.pack-install.json', json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'update'})
    if edit_index(a.name, index_rows(a.name, meta)):
        DONE.append({'path': index_file, 'action': 'index'})
    set_result('success', 0, L('Đã cập nhật gói %s lên v%s.', 'Updated pack %s to v%s.') % (a.name, meta['version']), changes=True,
               merge_required=bool(conf), files=list(DONE),
               next_actions=[L('Hợp nhất các file .new rồi xóa chúng.', 'Merge the .new files, then delete them.')] if conf else [], **versions)
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
    DONE.append({'path': '%s/%s' % (INSTALL_DIR, a.name), 'action': 'archive', 'to': dst})
    if edit_index(a.name, None):
        DONE.append({'path': '.agent/SKILL_INDEX.md', 'action': 'index'})
    set_result('success', 0, L('Đã gỡ gói %s.', 'Removed pack %s.') % a.name, changes=True, pack=a.name, files=list(DONE))
    print(L('Đã gỡ gói %s: thư mục chuyển vào %s, bỏ khỏi SKILL_INDEX. Không có file nào bị xóa.', 'Removed pack %s: folder moved to %s, dropped from SKILL_INDEX. No file was deleted.') % (a.name, dst))

def cmd_check(a):
    names = [a.name] if a.name else sorted(n for n in os.listdir(P('packs')) if os.path.isdir(P('packs/' + n))) if os.path.isdir(P('packs')) else []
    bad = 0
    findings = []
    for n in names:
        e = validate_pack(P('packs/' + n), n)
        print('%s: %s' % (n, 'OK' if not e else '%d lỗi / errors' % len(e)))
        for x in e: print('  - ' + x)
        bad += len(e)
        findings += [{'pack': n, 'message': x} for x in e]
    ins = installed()
    idx = rd('.agent/SKILL_INDEX.md') if os.path.isfile(P('.agent/SKILL_INDEX.md')) else ''
    for n, m in ins.items():
        for sid in m['skills']:
            if not os.path.isfile(P('%s/%s/skills/%s/SKILL.md' % (INSTALL_DIR, n, sid))):
                print('  - %s: thiếu / missing %s' % (n, sid)); bad += 1
                findings.append({'pack': n, 'message': 'thiếu / missing %s' % sid})
            if idx and ('| %s | LOCAL | PACK |' % sid) not in idx:
                print('  - %s: skill %s chưa có trong SKILL_INDEX / not in SKILL_INDEX' % (n, sid)); bad += 1
                findings.append({'pack': n, 'message': 'skill %s chưa có trong SKILL_INDEX / not in SKILL_INDEX' % sid})
    if a.name and not os.path.isdir(P('packs/' + a.name)):
        set_result('blocked', 1, L('Không thấy gói "%s" trong packs/.', 'Pack "%s" not found in packs/.') % a.name, changes=False,
                   pack=a.name, findings=findings, checked=names)
    elif bad:
        set_result('issues', 1, L('Có %d vấn đề trong gói.', '%d problems found in the packs.') % bad, changes=False,
                   findings=findings, checked=names)
    else:
        set_result('success', 0, L('Các gói đều đạt kiểm tra cấu trúc.', 'All packs pass the structure check.'), changes=False, checked=names)
    sys.exit(1 if bad else 0)

def cmd_new(a):
    if not NAME_RE.match(a.name):
        stop('Tên gói phải là chữ thường, số, dấu gạch ngang (ví dụ: logistics). / Use lowercase letters, digits and hyphens.')
    if os.path.exists(P('packs/' + a.name)):
        stop('packs/%s đã tồn tại. / already exists.' % a.name, pack=a.name)
    if not os.path.isdir(P('packs/_template')):
        stop('Thiếu packs/_template. / packs/_template is missing.', status='error')
    for rel in walk(P('packs/_template')):
        s = P('packs/_template/' + rel)
        d = rel.replace('example-skill', a.name + '-example')
        os.makedirs(os.path.dirname(P('packs/%s/%s' % (a.name, d))), exist_ok=True)
        txt = io.open(s, encoding='utf-8', newline='').read().replace('example-skill', a.name + '-example').replace('"_template"', '"%s"' % a.name).replace('_template', a.name)
        wr('packs/%s/%s' % (a.name, d), txt)
        DONE.append({'path': 'packs/%s/%s' % (a.name, d), 'action': 'create'})
    set_result('success', 0, L('Đã tạo packs/%s/.', 'Created packs/%s/.') % a.name, changes=True, pack=a.name, files=list(DONE),
               next_actions=[L('Sửa pack.json và skills/, rồi chạy: python tools/pack.py check %s', 'Edit pack.json and skills/, then run: python tools/pack.py check %s') % a.name])
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
    a = ap.parse_args([x for x in sys.argv[1:] if x != '--result-json'])
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        LANG = json.loads(rd('.agent/PACKAGE_INFO.json')).get('language', 'vi')
    except (OSError, ValueError):
        pass
    a.f(a)

def run_with_result():
    """Chạy lệnh và phát đúng một kết quả có cấu trúc; mã trong kết quả luôn bằng mã thoát / Run the command and emit exactly one structured result; its code always equals the exit code."""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    code, msg, fallback = 0, '', 'success'
    try:
        main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        fallback = 'success' if code == 0 else 'blocked'
        if isinstance(e.code, str):
            msg = e.code
            print(msg, file=sys.stderr)  # như sys.exit(msg) / same as sys.exit(msg)
        elif code:  # argparse đã in lỗi cú pháp / argparse has printed the usage error
            msg = L('Tham số không hợp lệ; xem trợ giúp của lệnh.', 'Invalid arguments; see the command help.')
    except OSError as e:
        code, msg, fallback = 1, str(e), 'error'
        if DONE:
            set_result('partial', 1, msg, changes=True, files=list(DONE),
                       next_actions=[L('Kiểm các file đã ghi; chưa tự hoàn tác.', 'Check the files already written; no automatic rollback.')])
            print('CHƯA HOÀN TẤT / INCOMPLETE: %s. Có thể đã ghi một số file; chưa tự hoàn tác. / Some files may have been written; no automatic rollback.' % e, file=sys.stderr)
        else:
            print('Lỗi / Error: %s' % e, file=sys.stderr)
    except Exception as e:  # lỗi bất ngờ vẫn phát kết quả / unexpected errors still emit a result
        traceback.print_exc()
        code, msg, fallback = 1, repr(e), 'error'
    res = LAST_RESULT
    if res is None:
        res = make(fallback, code=code, message=msg)
    elif res['code'] != code:
        res = make('error', code=code, message=L('Mã kết quả không khớp mã thoát.', 'Result code does not match the exit code.'))
    emit(res)
    return code

if __name__ == '__main__':
    if RESULT_REQUESTED:
        sys.exit(run_with_result())
    main()
