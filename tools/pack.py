#!/usr/bin/env python3
"""Quản lý "gói lĩnh vực" (domain pack): bộ skill và mẫu của một lĩnh vực, cài theo nhu cầu vào từng project.
Manage "domain packs": a set of skills and templates for one domain, installed per project on demand.

Dùng / Usage (chạy từ thư mục project / run from the project folder):
  python tools/pack.py list                 liệt kê gói có sẵn và gói đã cài / list available and installed packs
  python tools/pack.py add <tên> [--confirm]  cài gói vào skills/local/packs/<tên>/ và ghi vào .agent/SKILL_INDEX.md (--confirm: cài và nhận luôn)
  python tools/pack.py update <tên>         cập nhật gói đã cài lên bản trong packs/ (file bạn đã sửa -> <tên>.new); --apply ghi, thêm --confirm để nhận lại luôn
  python tools/pack.py remove <tên>         gỡ gói: chuyển vào archive/, bỏ khỏi SKILL_INDEX (không xóa file)
  python tools/pack.py confirm <tên>        nhận gói đã cài cho project này, chạy luôn (--dry-run: chỉ xem)
  python tools/pack.py check [<tên>]        kiểm tra cấu trúc gói (người viết gói dùng)
  python tools/pack.py new <tên>            tạo gói mới trong packs/<tên>/ từ packs/_template (người viết gói dùng)

Một gói là thư mục packs/<tên>/ có pack.json và skills/<skill-id>/SKILL.md. Xem packs/README.md.
Cài, cập nhật hay kiểm cấu trúc không phải tiếp nhận. Khối "intake" trong pack.json chỉ là LỜI KHAI của gói (skills/README.md);
gói cài vào project mặc định ghi Status REVIEW (ứng viên, dùng thử). Chỉ hành động xác nhận rõ ràng của người dùng (--confirm khi cài
hoặc cập nhật, hoặc lệnh "confirm"; gắn với đúng nội dung đang cài) mới ghi AVAILABLE, và chỉ khi lời khai hợp lệ: hồ sơ giải được tới một file local có thật. Nội dung đổi sau khi xác
nhận, hoặc hồ sơ từ chối đúng bản đã cài, thì xác nhận không còn hiệu lực.
Installing, updating or checking the structure is not intake. The "intake" block in pack.json is only the pack's CLAIM
(skills/README.md); a pack installed into a project is recorded as REVIEW by default (candidate, trial use). Only an explicit
confirmation by the user (--confirm on install or update, or the "confirm" command; bound to the exact installed content) records AVAILABLE, and only when the claim is valid: its record
resolves to a real local file. Content changed after confirming, or a record refusing the installed version, voids it.
No script of a pack is ever run.
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

def _resolve_locator(v, base):
    """Đường dẫn local tương đối, không thoát thư mục, tới một file có thật. URL, đường dẫn tuyệt đối, '..' hay chuỗi lạ là
    chưa giải được (không ngầm hợp lệ). / A relative local path that stays inside and points to a real file; anything else
    (URL, absolute path, '..', an odd string) is unresolved, never silently valid."""
    v = str(v or '').strip().replace('\\', '/')
    if not v or '://' in v or v.startswith('/') or re.match(r'^[A-Za-z]:', v) or '..' in v.split('/'):
        return False
    return any(os.path.isfile(os.path.join(b, *v.split('/'))) for b in (base, ROOT) if b)

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
        if (v or key == 'record') and not _resolve_locator(v, base):
            out.update(reason='record_not_found', missing=v)
            return out
    out.update(state='accepted', reason=d.lower(), root_update=d == 'ROOT_ELIGIBLE' and bool(it.get('root_grant')))
    return out

def intake_label(st):
    r = st['reason']
    if st['state'] == 'accepted':
        return L('lời khai đã nhận (%s), chưa xác nhận ở project', 'claims accepted (%s), not confirmed in a project') % st['decision'] + (L('; khai được cập nhật gốc', '; claims root update') if st['root_update'] else '')
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
        'record_not_found': L('ứng viên, hồ sơ %s không giải được (cần đường dẫn local có thật)', 'candidate, record %s does not resolve (a real local path is needed)') % st.get('missing'),
    }.get(r, L('ứng viên', 'candidate'))

def content_digest(d):
    """Dấu vân tay nội dung gói đã cài (không tính .pack-install.json và file .new). Chỉ nhận diện thay đổi, không chứng minh chất lượng.
    Fingerprint of the installed pack content (not .pack-install.json or .new files). It detects change; it proves no quality."""
    h = hashlib.sha256()
    for rel in walk(d):
        if rel == '.pack-install.json' or rel.endswith('.new'):
            continue
        h.update(rel.encode('utf-8') + b'\0' + sha_file(os.path.join(d, rel)).encode('ascii') + b'\n')
    return h.hexdigest()

def installed_eligibility(name):
    """None khi gói đã cài có xác nhận còn hiệu lực cho đúng nội dung đang cài; nếu không thì lý do.
    None when the installed pack has a confirmation that still holds for the exact installed content; else the reason."""
    ins = installed().get(name)
    if not ins:
        return 'not_installed'
    c = ins.get('confirmed')
    if not isinstance(c, dict) or not c.get('digest'):
        return 'not_confirmed'
    if content_digest(P('%s/%s' % (INSTALL_DIR, name))) != c['digest']:
        return 'content_changed'
    src = P('packs/%s/pack.json' % name)
    if os.path.isfile(src):
        try:
            meta = json.load(io.open(src, encoding='utf-8'))
        except ValueError:
            meta = None
        if isinstance(meta, dict) and meta.get('version') == ins.get('version'):  # hồ sơ về bản khác không đụng bản đã cài
            st = intake_state(meta, P('packs/' + name))
            if st['state'] == 'refused':
                return 'refused'
            if st['state'] != 'accepted':
                return 'claim_withdrawn'
    return None

def eligibility_text(name, why):
    return {
        'not_confirmed': L('Gói %s chưa được xác nhận tiếp nhận ở project này: chạy "python tools/pack.py confirm %s".',
                           'Pack %s is not confirmed in this project: run "python tools/pack.py confirm %s".') % (name, name),
        'content_changed': L('Nội dung gói %s đã cài khác bản đã xác nhận: xét lại phần đổi rồi chạy lại "pack.py confirm %s".',
                             'The installed content of pack %s differs from what was confirmed: review the change, then run "pack.py confirm %s" again.') % (name, name),
        'refused': L('Gói %s đã cài nhưng hồ sơ tiếp nhận từ chối đúng bản này; cân nhắc gỡ (pack.py remove %s).',
                     'Pack %s is installed but its intake record refuses this very version; consider removing it (pack.py remove %s).') % (name, name),
        'claim_withdrawn': L('Hồ sơ tiếp nhận của gói %s không còn ở mức đã nhận cho bản đã cài; xác nhận cũ không còn đủ căn cứ.',
                             'The intake record of pack %s no longer claims acceptance for the installed version; the old confirmation has lost its basis.') % name,
    }.get(why, why)

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

def index_rows(name, meta, st, approved=False):
    """(skill id, trạng thái, mẫu dòng có chỗ %s cho trạng thái). Chỉ gói đã được người dùng xác nhận (approved) mới ghi AVAILABLE.
    (skill id, status, row template with %s for the status). Only a pack the user confirmed (approved) is recorded AVAILABLE."""
    rows = []
    note = intake_label(st).replace('|', '/')
    for sid in meta['skills']:
        sp = P('packs/%s/skills/%s/SKILL.md' % (name, sid))
        import check_package as cp
        fm = cp.frontmatter(io.open(sp, encoding='utf-8').read()) or {}
        desc = re.sub(r'\s*(Kích hoạt khi|Triggers when).*$', '', fm.get('description', ''), flags=re.S).strip().replace('|', '/')
        rows.append((sid, 'AVAILABLE' if approved else 'REVIEW',
                     ('| %s | LOCAL | PACK | %s/%s/skills/%s/SKILL.md | %s | ' % (sid, INSTALL_DIR, name, sid, desc[:220])).replace('%', '%%')
                     + '%s' + (' | Gói/Pack %s v%s; %s%s |' % (name, meta['version'], note, L('; đã xác nhận ở project', '; confirmed in this project') if approved else '')).replace('%', '%%')))
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

def edit_index(name, rows):
    """Bỏ mọi dòng của gói `name` khỏi SKILL_INDEX rồi chèn `rows` (nếu có) sau dòng bảng cuối. Luôn giữ DISABLED người dùng đã đặt;
    giữ ACTIVE chỉ khi dòng mới là AVAILABLE (đã xác nhận). Trạng thái do người dùng tự gõ vào index không phải xác nhận.
    Always keeps a user's DISABLED; keeps ACTIVE only when the new row is AVAILABLE (confirmed). A status typed into the index by hand is not a confirmation."""
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
            if prev == 'DISABLED' or (prev == 'ACTIVE' and status == 'AVAILABLE'):
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
    if a.confirm and st['state'] != 'accepted':  # dừng trước khi ghi: không âm thầm hạ xuống bản thử / stop before writing, never silently downgrade
        stop(L('Không cài và nhận gói %s được: %s. Muốn dùng thử thì cài không có --confirm.',
               'Cannot install and accept pack %s: %s. To try it, install without --confirm.') % (a.name, intake_label(st)), pack=a.name, intake=st)
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
    confirmed = None
    if a.confirm:
        it = meta.get('intake', {})
        confirmed = {'digest': content_digest(P(dst)), 'version': meta['version'], 'decision': it.get('decision'), 'record': it.get('record'),
                     'date': datetime.date.today().isoformat()}
    wr(dst + '/.pack-install.json', json.dumps({'name': a.name, 'version': meta['version'], 'skills': meta['skills'],
        'installed': datetime.date.today().isoformat(), 'claim': st['state'], 'confirmed': confirmed, 'files': files}, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'add'})
    ok = edit_index(a.name, index_rows(a.name, meta, st, bool(confirmed)))
    if ok:
        DONE.append({'path': '.agent/SKILL_INDEX.md', 'action': 'index'})
    trial = not confirmed  # cài không kèm --confirm không phải xác nhận / installing without --confirm is not confirmation
    nxt = [] if ok else [L('Thêm dòng skill vào .agent/SKILL_INDEX.md (file này chưa có).', 'Add the skill rows to .agent/SKILL_INDEX.md (the file is missing).')]
    if confirmed:
        pass
    elif st['state'] == 'accepted':
        nxt.append(L('Hồ sơ tiếp nhận do chính gói khai, chưa phải quyết định của bạn. Gói ở REVIEW (dùng thử, không xuất sang ứng dụng). Đã xét hồ sơ và muốn nhận cho project này: python tools/pack.py confirm %s',
                     'The intake record is the pack\'s own claim, not your decision. The pack stays REVIEW (trial; not exported to apps). If you reviewed the record and accept it for this project: python tools/pack.py confirm %s') % a.name)
    else:
        nxt.append(L('Gói là ứng viên (REVIEW): dùng thử trong project này; không được xuất sang ứng dụng. Muốn nhận thì lập hồ sơ theo skills/README.md rồi chạy pack.py confirm.',
                     'The pack is a candidate (REVIEW): try it in this project; it is not exported to apps. To accept it, record intake as in skills/README.md, then run pack.py confirm.'))
    set_result('success', 0, (L('Đã cài gói %s v%s để thử (ứng viên).', 'Installed pack %s v%s for trial (candidate).') if trial else
                              L('Đã cài và nhận gói %s v%s cho project này.', 'Installed and accepted pack %s v%s for this project.')) % (a.name, meta['version']), changes=True,
               pack=a.name, version=meta['version'], skills=meta['skills'], files=list(DONE), intake=st, next_actions=nxt)
    print(L('Đã cài gói %s v%s: %d skill (%s).', 'Installed pack %s v%s: %d skills (%s).') % (a.name, meta['version'], len(meta['skills']), ', '.join(meta['skills'])))
    print(L('Tiếp nhận: %s; trạng thái trong chỉ mục: %s.', 'Intake: %s; index status: %s.') % (intake_label(st), 'AVAILABLE (bạn đã xác nhận)' if confirmed else 'REVIEW'))
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
    conf_old = old.get('confirmed') if isinstance(old.get('confirmed'), dict) and old['confirmed'].get('digest') else None
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
    if a.confirm and st['state'] != 'accepted':
        stop(L('Không nhận lại gói %s khi cập nhật được: %s. Bỏ --confirm để cập nhật mà không nhận.', 'Cannot re-accept pack %s on update: %s. Drop --confirm to update without accepting.')
             % (a.name, intake_label(st)), pack=a.name, intake=st)
    if conf_old and (upd or add or st['state'] != 'accepted') and not a.confirm:  # nội dung đổi hoặc lời khai không còn: xác nhận cũ hết hiệu lực
        print(L('Xác nhận tiếp nhận cũ sẽ hết hiệu lực: nội dung đổi hoặc hồ sơ không còn ở mức đã nhận (%s). Skill của gói về REVIEW cho tới khi bạn xét phần đổi ở trên rồi chạy "pack.py confirm %s" (hoặc cập nhật lại với --apply --confirm).',
                'The old confirmation will lapse: the content changes or the record no longer claims acceptance (%s). The pack skills go back to REVIEW until you review the change above and run "pack.py confirm %s" (or update again with --apply --confirm).')
              % (intake_label(st), a.name))
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
    new_digest = content_digest(P(dst))
    it = meta.get('intake', {})
    if a.confirm and st['state'] == 'accepted':  # người dùng xác nhận nội dung mới ngay lúc cập nhật / the user confirms the new content right on update
        conf_new = {'digest': new_digest, 'version': meta['version'], 'decision': it.get('decision'), 'record': it.get('record'),
                    'date': datetime.date.today().isoformat()}
    else:
        conf_new = conf_old if (conf_old and st['state'] == 'accepted' and new_digest == conf_old['digest']) else None
    keep = bool(conf_new)
    old.pop('intake', None)
    old.update({'version': meta['version'], 'skills': meta['skills'], 'files': newfiles, 'claim': st['state'],
                'confirmed': conf_new, 'updated': datetime.date.today().isoformat()})
    wr(dst + '/.pack-install.json', json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'update'})
    if edit_index(a.name, index_rows(a.name, meta, st, keep)):
        DONE.append({'path': index_file, 'action': 'index'})
    set_result('success', 0, L('Đã cập nhật gói %s lên v%s.', 'Updated pack %s to v%s.') % (a.name, meta['version']), changes=True,
               merge_required=bool(conf), files=list(DONE),
               next_actions=[L('Hợp nhất các file .new rồi xóa chúng.', 'Merge the .new files, then delete them.')] if conf else [], **versions)
    print(L('Đã cập nhật.', 'Updated.'))

def cmd_confirm(a):
    """Bước xác nhận của người dùng: nhận gói đã cài cho project này, gắn với đúng nội dung đang cài. Chạy luôn; --dry-run chỉ xem.
    The user's confirmation step: accept the installed pack for this project, bound to the exact installed content. Runs at once; --dry-run only shows."""
    av, ins = available(), installed()
    need(a.name, ins); need(a.name, av)
    old, meta = ins[a.name], av[a.name]
    if meta.get('version') != old.get('version'):
        stop(L('Bản trong packs/ (%s) khác bản đã cài (%s): chạy "pack.py update %s --apply" trước rồi xác nhận.',
               'The version in packs/ (%s) differs from the installed one (%s): run "pack.py update %s --apply" first, then confirm.')
             % (meta.get('version'), old.get('version'), a.name), pack=a.name)
    st = intake_state(meta, P('packs/' + a.name))
    if st['state'] != 'accepted':
        stop(L('Chưa xác nhận được gói %s: %s. Lời khai phải hợp lệ và hồ sơ giải được tới file local có thật (xem packs/README.md).',
               'Cannot confirm pack %s: %s. The claim must be valid and its record must resolve to a real local file (see packs/README.md).')
             % (a.name, intake_label(st)), pack=a.name, intake=st)
    dst = '%s/%s' % (INSTALL_DIR, a.name)
    digest = content_digest(P(dst))
    edited = sorted(r for r in walk(P(dst)) if r != '.pack-install.json' and not r.endswith('.new')
                    and (r not in old.get('files', {}) or sha_file(P('%s/%s' % (dst, r))) != old['files'][r]))
    it = meta.get('intake', {})
    print(L('Nhận gói %s %s cho project này: quyết định %s, hồ sơ %s, dấu vân tay nội dung %s.',
            'Accepting pack %s %s for this project: decision %s, record %s, content fingerprint %s.')
          % (a.name, old['version'], it.get('decision'), it.get('record'), digest[:12]))
    print(L('Xác nhận này gắn với đúng nội dung đang cài; đổi nội dung thì phải xác nhận lại. Bạn nên đã đọc hồ sơ và phần căn cứ trước khi xác nhận.',
            'This confirmation is bound to the exact installed content; changing it requires confirming again. You should have read the record and its evidence first.'))
    if edited:
        print(L('Lưu ý: file đã cài khác bản lúc cài (bạn hoặc công cụ khác đã sửa): %s. Xác nhận áp dụng cho nội dung hiện tại.',
                'Note: installed files differ from the install-time copy (edited by you or another tool): %s. The confirmation covers the current content.') % ', '.join(edited))
    plan = [{'path': dst + '/.pack-install.json', 'action': 'update'}]
    if os.path.isfile(P('.agent/SKILL_INDEX.md')):
        plan.append({'path': '.agent/SKILL_INDEX.md', 'action': 'index'})
    info = dict(pack=a.name, version=old['version'], intake=st, fingerprint=digest, edited=edited)
    if a.dry_run:
        print(L('[XEM TRƯỚC] Bỏ --dry-run để xác nhận.', '[PREVIEW] Drop --dry-run to confirm.'))
        set_result('preview', 0, L('Xem trước xác nhận tiếp nhận; chưa ghi file nào.', 'Intake confirmation preview; no file written yet.'),
                   changes=True, files=plan, next_actions=[L('Bỏ --dry-run để xác nhận.', 'Drop --dry-run to confirm.')], **info)
        return
    old['confirmed'] = {'digest': digest, 'version': old['version'], 'decision': it.get('decision'), 'record': it.get('record'),
                        'date': datetime.date.today().isoformat()}
    old['claim'] = st['state']
    old.pop('intake', None)
    wr(dst + '/.pack-install.json', json.dumps(old, ensure_ascii=False, indent=2) + '\n')
    DONE.append({'path': dst + '/.pack-install.json', 'action': 'update'})
    if edit_index(a.name, index_rows(a.name, meta, st, True)):
        DONE.append({'path': '.agent/SKILL_INDEX.md', 'action': 'index'})
    set_result('success', 0, L('Đã xác nhận tiếp nhận gói %s cho project này.', 'Confirmed intake of pack %s for this project.') % a.name,
               changes=True, files=list(DONE), **info)
    print(L('Đã xác nhận. Skill của gói ghi AVAILABLE trong .agent/SKILL_INDEX.md.', 'Confirmed. The pack skills are recorded AVAILABLE in .agent/SKILL_INDEX.md.'))

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
        # chỉ mục ghi đã nhận nhưng không có xác nhận còn hiệu lực cho nội dung đang cài (gõ tay, nội dung đổi, hồ sơ từ chối)
        # the index says accepted but no confirmation holds for the installed content (typed by hand, content changed, record refuses)
        if not a.name or a.name == n:
            why = installed_eligibility(n)
            if why and any(v in ('AVAILABLE', 'ACTIVE') for v in index_status(n).values()):
                msg = eligibility_text(n, why)
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
    for c, f in (('add', cmd_add), ('update', cmd_update), ('confirm', cmd_confirm), ('remove', cmd_remove), ('new', cmd_new)):
        s = sub.add_parser(c); s.add_argument('name'); s.set_defaults(f=f)
        if c in ('add', 'update'):
            s.add_argument('--confirm', action='store_true', help='nhận gói luôn (hồ sơ phải hợp lệ) / accept the pack right away (the record must be valid)')
        if c == 'update':
            s.add_argument('--apply', action='store_true')
        if c == 'confirm':
            s.add_argument('--dry-run', action='store_true', help='chỉ xem, không ghi / only show, write nothing')
            s.add_argument('--apply', action='store_true', help=argparse.SUPPRESS)  # giữ cho lệnh cũ / kept for older commands
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
