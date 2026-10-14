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
Cài hay kiểm cấu trúc không phải tiếp nhận: gói không có hồ sơ tiếp nhận hợp lệ cho đúng phiên bản (khối "intake" trong
pack.json, xem skills/README.md) được ghi Status REVIEW (ứng viên, dùng thử), chỉ gói đã tiếp nhận mới ghi AVAILABLE.
Installing or checking the structure is not intake: a pack without a valid intake record for its exact version is recorded
as REVIEW (candidate, trial use); only an accepted pack is recorded as AVAILABLE. No script of a pack is ever run.
Chỉ cần Python 3.8+, không dùng mạng, không chạy script nào của gói.
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
# Tiếp nhận (skills/README.md, mục "Tiếp nhận"): công cụ chỉ kiểm phần kiểm được bằng máy, không chấm "tốt hơn native".
# Intake (skills/README.md): the tool checks only what a machine can check; it never scores "better than native".
USABLE = ('ADD_MISSING_PART', 'PROJECT_ONLY', 'ROOT_ELIGIBLE')
REFUSED = ('REUSE_NO_IMPORT', 'REJECT_VERSION')
DECISIONS = USABLE + REFUSED + ('DEFER',)
RELATIONS = ('SUPPLEMENT', 'REPLACEMENT', 'FALLBACK', 'UNKNOWN')
USER_STATUS = ('AVAILABLE', 'ACTIVE', 'DISABLED')  # trạng thái người dùng tự đặt trong SKILL_INDEX / statuses set by the user

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
    return errs + intake_errors(meta.get('intake'), name)

# ---------------------------------------------------------------- tiếp nhận / intake
INTAKE_KEYS = {'decision', 'version', 'relation', 'record', 'comparison', 'root_grant', 'note'}

def intake_errors(it, name):
    """Lỗi mẫu của khối "intake" trong pack.json (không có khối thì không lỗi: gói là ứng viên).
    Format errors of the optional "intake" block (no block is not an error: the pack is a candidate)."""
    if it is None:
        return []
    if not isinstance(it, dict):
        return ['%s/pack.json: "intake" phải là đối tượng JSON.' % name]
    e = ['%s/pack.json: "intake.%s" không thuộc mẫu (%s).' % (name, k, ', '.join(sorted(INTAKE_KEYS))) for k in sorted(set(it) - INTAKE_KEYS)]
    if it.get('decision') not in DECISIONS:
        e.append('%s/pack.json: "intake.decision" phải là một trong %s.' % (name, ', '.join(DECISIONS)))
    if not re.fullmatch(r'\d+\.\d+\.\d+', str(it.get('version', ''))):
        e.append('%s/pack.json: "intake.version" phải dạng MAJOR.MINOR.PATCH (bản mà quyết định áp dụng).' % name)
    if it.get('relation') not in RELATIONS:
        e.append('%s/pack.json: "intake.relation" phải là một trong %s.' % (name, ', '.join(RELATIONS)))
    if not str(it.get('record') or '').strip():
        e.append('%s/pack.json: "intake.record" cần chỉ tới hồ sơ tiếp nhận.' % name)
    if it.get('root_grant') and it.get('decision') != 'ROOT_ELIGIBLE':
        e.append('%s/pack.json: "intake.root_grant" chỉ dùng với decision ROOT_ELIGIBLE.' % name)
    return e

def _local_locator(v):
    return '://' not in v and re.search(r'\.(md|json|txt|html|pdf|docx|xlsx)$', v, re.I)

def intake_state(meta, base=None):
    """Trạng thái tiếp nhận của một gói, chỉ từ điều kiện kiểm được bằng máy.
    The pack's intake state, from machine-checkable conditions only:
    accepted (đủ điều kiện dùng / usable), candidate (ứng viên / candidate), refused (không nhận / not taken)."""
    it = meta.get('intake')
    out = {'state': 'candidate', 'reason': 'no_record', 'decision': None, 'root_update': False}
    if it is None:
        return out
    if not isinstance(it, dict) or intake_errors(it, ''):
        out['reason'] = 'invalid_record'
        return out
    d = out['decision'] = it['decision']
    if it['version'] != meta.get('version'):
        out.update(reason='version_changed', record_version=it['version'])
        return out
    if d in REFUSED:
        out.update(state='refused', reason=d.lower())
        return out
    if d == 'DEFER':
        out['reason'] = 'deferred'
        return out
    if it['relation'] == 'UNKNOWN':
        out['reason'] = 'native_unknown'
        return out
    if it['relation'] == 'REPLACEMENT' and not str(it.get('comparison') or '').strip():
        out['reason'] = 'no_comparison'
        return out
    for key in ('record', 'comparison'):
        v = str(it.get(key) or '').strip()
        if v and _local_locator(v) and not any(os.path.exists(os.path.join(b, *v.split('/'))) for b in (base or ROOT, ROOT)):
            out.update(reason='record_not_found', missing=v)
            return out
    out.update(state='accepted', reason=d.lower(), root_update=d == 'ROOT_ELIGIBLE' and bool(it.get('root_grant')))
    return out

def intake_label(st):
    r = st['reason']
    if st['state'] == 'accepted':
        return L('đã tiếp nhận (%s)', 'accepted (%s)') % st['decision'] + (L(', được cập nhật gốc', ', root update granted') if st['root_update'] else '')
    if st['state'] == 'refused':
        return L('không nhận: dùng khả năng sẵn có', 'not taken: reuse existing capability') if r == 'reuse_no_import' \
            else L('không nhận phiên bản này', 'this version not taken')
    return {
        'no_record': L('ứng viên, chưa có hồ sơ tiếp nhận', 'candidate, no intake record'),
        'invalid_record': L('ứng viên, hồ sơ tiếp nhận sai mẫu', 'candidate, intake record malformed'),
        'version_changed': L('ứng viên, hồ sơ tiếp nhận dành cho bản %s; phần đổi chưa xét', 'candidate, intake record covers %s; the change is not reviewed') % st.get('record_version'),
        'deferred': L('ứng viên, tiếp nhận đang hoãn', 'candidate, intake deferred'),
        'native_unknown': L('ứng viên, chưa xác minh khả năng native', 'candidate, native capability not verified'),
        'no_comparison': L('ứng viên, bản thay thế chưa có bằng chứng so sánh', 'candidate, replacement without comparison evidence'),
        'record_not_found': L('ứng viên, không thấy hồ sơ %s', 'candidate, record %s not found') % st.get('missing'),
    }.get(r, L('ứng viên', 'candidate'))

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

def index_rows(name, meta, st):
    """(skill id, trạng thái, mẫu dòng có chỗ %s cho trạng thái). Ứng viên ghi REVIEW, chỉ gói đã tiếp nhận ghi AVAILABLE.
    (skill id, status, row template with %s for the status). Candidates get REVIEW; only accepted packs get AVAILABLE."""
    rows = []
    note = intake_label(st).replace('|', '/')
    for sid in meta['skills']:
        sp = P('packs/%s/skills/%s/SKILL.md' % (name, sid))
        import check_package as cp
        fm = cp.frontmatter(io.open(sp, encoding='utf-8').read()) or {}
        desc = re.sub(r'\s*(Kích hoạt khi|Triggers when).*$', '', fm.get('description', ''), flags=re.S).strip().replace('|', '/')
        rows.append((sid, 'AVAILABLE' if st['state'] == 'accepted' else 'REVIEW',
                     ('| %s | LOCAL | PACK | %s/%s/skills/%s/SKILL.md | %s | ' % (sid, INSTALL_DIR, name, sid, desc[:220])).replace('%', '%%')
                     + '%s' + (' | Gói/Pack %s v%s; %s |' % (name, meta['version'], note)).replace('%', '%%')))
    return rows

def index_status(name):
    """Trạng thái hiện có trong SKILL_INDEX của các skill thuộc gói `name` / current SKILL_INDEX status of the pack's skills."""
    out, tag = {}, 'Gói/Pack %s v' % name
    if os.path.isfile(P('.agent/SKILL_INDEX.md')):
        for l in rd('.agent/SKILL_INDEX.md').split('\n'):
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            if l.startswith('| ') and tag in l and len(cells) >= 6:
                out[cells[0]] = cells[5]
    return out

def edit_index(name, rows, keep_user=False):
    """Bỏ mọi dòng của gói `name` khỏi SKILL_INDEX rồi chèn `rows` (nếu có) sau dòng bảng cuối.
    Luôn giữ DISABLED người dùng đã đặt; với keep_user (cùng phiên bản, hồ sơ không bị rút) giữ cả AVAILABLE/ACTIVE người dùng đã đặt.
    Always keeps a user's DISABLED; with keep_user (same version, record not withdrawn) also keeps a user's AVAILABLE/ACTIVE."""
    f = '.agent/SKILL_INDEX.md'
    if not os.path.isfile(P(f)):
        return False
    old = index_status(name)
    lines = rd(f).split('\n')
    tag = 'Gói/Pack %s v' % name
    lines = [l for l in lines if not (l.startswith('| ') and tag in l)]
    if rows:
        out = []
        for sid, status, tmpl in rows:
            prev = old.get(sid)
            if prev == 'DISABLED' or (keep_user and prev in USER_STATUS):
                status = prev
            out.append(tmpl % status)
        rows = out
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
    intake = {n: intake_state(m, P('packs/' + n)) for n, m in av.items()}
    for n, m in av.items():
        st = ''
        if n in ins:
            st = L(' [đã cài v%s%s]', ' [installed v%s%s]') % (ins[n]['version'], L(', có bản mới v%s', ', newer v%s') % m['version'] if vt(m['version']) > vt(ins[n]['version']) else '')
        print('  - %s v%s: %s%s — %s' % (n, m['version'], loc(m.get('title')), st, intake_label(intake[n])))
    extra = [n for n in ins if n not in av]
    for n in extra:
        print('  - %s v%s %s' % (n, ins[n]['version'], L('[đã cài; không còn trong packs/]', '[installed; no longer in packs/]')))
    packs = [{'name': n, 'version': m.get('version'), 'installed': ins[n].get('version') if n in ins else None, 'available': True,
              'intake': intake[n]} for n, m in av.items()]
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
    st = intake_state(meta, P('packs/' + a.name))
    if st['state'] == 'refused':
        stop(L('Không cài gói %s: hồ sơ tiếp nhận ghi "%s". Tiếp tục bằng khả năng sẵn có.', 'Pack %s not installed: its intake record says "%s". Carry on with the existing capability.')
             % (a.name, intake_label(st)), pack=a.name, intake=st)
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
        'installed': datetime.date.today().isoformat(), 'intake': st['state'], 'files': files}, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'add'})
    ok = edit_index(a.name, index_rows(a.name, meta, st))
    if ok:
        DONE.append({'path': '.agent/SKILL_INDEX.md', 'action': 'index'})
    trial = st['state'] != 'accepted'
    nxt = [] if ok else [L('Thêm dòng skill vào .agent/SKILL_INDEX.md (file này chưa có).', 'Add the skill rows to .agent/SKILL_INDEX.md (the file is missing).')]
    if trial:
        nxt.append(L('Gói là ứng viên (REVIEW): dùng thử trong project này; không được xuất sang ứng dụng. Muốn nhận thì lập hồ sơ theo skills/README.md.',
                     'The pack is a candidate (REVIEW): try it in this project; it is not exported to apps. To accept it, record intake as in skills/README.md.'))
    set_result('success', 0, (L('Đã cài gói %s v%s để thử (ứng viên).', 'Installed pack %s v%s for trial (candidate).') if trial else
                              L('Đã cài gói %s v%s.', 'Installed pack %s v%s.')) % (a.name, meta['version']), changes=True,
               pack=a.name, version=meta['version'], skills=meta['skills'], files=list(DONE), intake=st, next_actions=nxt)
    print(L('Đã cài gói %s v%s: %d skill (%s).', 'Installed pack %s v%s: %d skills (%s).') % (a.name, meta['version'], len(meta['skills']), ', '.join(meta['skills'])))
    print(L('Tiếp nhận: %s; trạng thái trong chỉ mục: %s.', 'Intake: %s; index status: %s.') % (intake_label(st), 'REVIEW' if trial else 'AVAILABLE'))
    print(L('Đã ghi vào .agent/SKILL_INDEX.md.', 'Recorded in .agent/SKILL_INDEX.md.') if ok else L('Chưa có .agent/SKILL_INDEX.md: hãy tự thêm dòng skill.', 'No .agent/SKILL_INDEX.md: add the skill rows yourself.'))

def cmd_update(a):
    av, ins = available(), installed()
    need(a.name, ins); need(a.name, av)
    old, meta = ins[a.name], av[a.name]
    errs = validate_pack(P('packs/' + a.name), a.name)
    if errs:
        stop(L('Gói trong packs/ chưa hợp lệ:\n  ', 'The pack in packs/ is not valid:\n  ') + '\n  '.join(errs), pack=a.name, findings=[{'pack': a.name, 'message': x} for x in errs])
    st = intake_state(meta, P('packs/' + a.name))
    if st['state'] == 'refused':
        stop(L('Không cập nhật gói %s: hồ sơ tiếp nhận ghi "%s"; bản đang cài được giữ nguyên.', 'Pack %s not updated: its intake record says "%s"; the installed version is kept.')
             % (a.name, intake_label(st)), pack=a.name, intake=st)
    same_version = old.get('version') == meta['version']
    # hồ sơ đã nhận lúc cài nay không còn: AVAILABLE trong chỉ mục là do công cụ ghi, không phải người dùng, nên về REVIEW
    # the record accepted at install time is gone: AVAILABLE came from the tool, not the user, so it returns to REVIEW
    withdrawn = old.get('intake') == 'accepted' and st['state'] != 'accepted'
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
    versions = dict(pack=a.name, from_version=old.get('version'), to_version=meta['version'], intake=st)
    if (upd or add or conf) and (withdrawn or not same_version) and st['state'] != 'accepted':
        print(L('Bản này chưa qua tiếp nhận (hoặc hồ sơ đã rút): sau khi cập nhật, skill của gói về REVIEW cho tới khi phần đổi ở trên được xét (%s).',
                'This version has not been through intake (or its record was withdrawn): after the update the pack skills go back to REVIEW until the change above is reviewed (%s).')
              % intake_label(st))
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
    old.update({'version': meta['version'], 'skills': meta['skills'], 'files': newfiles, 'intake': st['state'],
                'updated': datetime.date.today().isoformat()})
    wr(dst + '/.pack-install.json', json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'update'})
    if edit_index(a.name, index_rows(a.name, meta, st), same_version and not withdrawn):
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
    intake = {}
    for n in names:
        e = validate_pack(P('packs/' + n), n)
        print('%s: %s' % (n, L('cấu trúc OK', 'structure OK') if not e else '%d lỗi / errors' % len(e)))
        for x in e: print('  - ' + x)
        bad += len(e)
        findings += [{'pack': n, 'message': x} for x in e]
        if not e and not n.startswith('_'):
            try:
                intake[n] = intake_state(json.load(io.open(P('packs/%s/pack.json' % n), encoding='utf-8')), P('packs/' + n))
                # cấu trúc đạt không có nghĩa đã tiếp nhận / a passing structure is not intake
                print('  ' + L('Tiếp nhận: ', 'Intake: ') + intake_label(intake[n]))
            except (OSError, ValueError):
                pass
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
        # hồ sơ hiện tại ghi không nhận đúng bản đang cài: update bị chặn, nên phải báo ở đây
        # the current record refuses the installed version: update is blocked, so report it here
        src = P('packs/%s/pack.json' % n)
        if (not a.name or a.name == n) and os.path.isfile(src):
            try:
                cur = json.load(io.open(src, encoding='utf-8'))
            except ValueError:
                cur = {}
            ist = intake_state(cur, P('packs/' + n))
            if cur.get('version') == m.get('version') and ist['state'] == 'refused':
                msg = L('%s v%s đã cài nhưng hồ sơ tiếp nhận ghi "%s"; cân nhắc gỡ (pack.py remove %s).',
                        '%s v%s is installed but its intake record says "%s"; consider removing it (pack.py remove %s).') % (n, m.get('version'), intake_label(ist), n)
                print('  - ' + msg); bad += 1
                findings.append({'pack': n, 'message': msg})
    if a.name and not os.path.isdir(P('packs/' + a.name)):
        set_result('blocked', 1, L('Không thấy gói "%s" trong packs/.', 'Pack "%s" not found in packs/.') % a.name, changes=False,
                   pack=a.name, findings=findings, checked=names)
    elif bad:
        set_result('issues', 1, L('Có %d vấn đề trong gói.', '%d problems found in the packs.') % bad, changes=False,
                   findings=findings, checked=names, intake=intake)
    else:
        set_result('success', 0, L('Các gói đều đạt kiểm tra cấu trúc (không phải kết luận tiếp nhận).', 'All packs pass the structure check (this is not an intake decision).'),
                   changes=False, checked=names, intake=intake)
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
