#!/usr/bin/env python3
"""Track package-managed .new files without reading or storing their contents.

diff() compares a managed file with its .new copy on request, read-only; nothing is stored or merged.

D-01b (hẹp / narrow): preview_replace() và apply_replace() chỉ cho đúng tám tài liệu hướng dẫn Markdown (REPLACE_ALLOWLIST).
Preview chỉ đọc. Apply lưu bản hiện hành + bản .new đã xem vào .agent/merge-backups/<id>/ rồi mới thay bản hiện hành, trong một
Transaction; .new, MERGE_STATUS, MANIFEST và HTML đã dựng không đổi. Đây không phải resolve, undo hay phục hồi tự động.
Preview is read-only. Apply stores the current file and the previewed .new bytes under .agent/merge-backups/<id>/ and only then replaces
the current file, in one Transaction; the .new copy, MERGE_STATUS, MANIFEST and built HTML are untouched. It is not resolve, undo or auto-recovery.

D-01e: finish (không phải replace) mở thêm sáu instruction entrypoint (AGENTS/CLAUDE/GEMINI ở gốc và en/): FINISH_ALLOWLIST = tám guide + sáu path, validator phía server;
REPLACE_ALLOWLIST vẫn đúng tám guide. scan() thêm finish_supported (chỉ là phạm vi, không phải eligible hay grant).
Finish (not replace) also covers six instruction entrypoints; FINISH_ALLOWLIST is checked server-side and REPLACE_ALLOWLIST stays the eight guides.

D-01g: finish mở thêm đúng hai script package (tools/audit_scripts.py và skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py): FINISH_ALLOWLIST = 8 + 6 + 2 = 16.
Allowlist không thay managed_paths: path trong allowlist mà không thuộc MANIFEST vẫn là not_managed. Chỉ lưu .new theo bytes; không import, biên dịch hay chạy script.
Finish also covers exactly two package scripts (16 paths in all); the allowlist does not replace managed_paths (allowed but unmanaged stays not_managed); the bytes are archived, never imported, compiled or run.

D-01c (cùng tám tài liệu / the same eight guides): preview_finish(), apply_finish() và observe_finish() giữ nguyên bản hiện hành, lưu bản hiện hành + .new đã xem
vào .agent/merge-backups/<finish_id>/ bằng một Transaction, rồi (chỉ khi nhật ký 'committed') đưa .new vào pending-retired.txt bằng MỘT os.rename không thay thế
trên Windows. Hai bước tách rời, không nguyên tử; kết quả luôn do quan sát file thật quyết định. Không xóa, không hoàn tác, không sửa MANIFEST/HTML.
Keeps the current file, stores it and the previewed .new under .agent/merge-backups/<finish_id>/ in one Transaction, then (only once the journal reads
'committed') moves the .new into pending-retired.txt with ONE no-replace os.rename on Windows. Two separate steps; the observed files decide the result.
"""
import datetime, difflib, hashlib, io, json, os, re, stat, uuid
import transaction

STATE_REL = '.agent/MERGE_STATUS.json'
ALLOWED_STATES = {'unseen', 'reviewing', 'ready'}
DIFF_MAX_BYTES = 256 * 1024  # mỗi file; file lớn hơn không so sánh trong giao diện / per file; larger files are not compared
DIFF_MAX_ROWS = 4000         # số dòng kết quả tối đa / maximum result rows
DIFF_CONTEXT = 3             # dòng ngữ cảnh quanh mỗi thay đổi / context lines around each change

def _read_json(path):
    try:
        with io.open(path, encoding='utf-8') as src:
            value = json.load(src)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}

def _manifest_paths(root):
    out = set()
    try:
        with io.open(os.path.join(root, 'MANIFEST.sha256'), encoding='utf-8') as src:
            for line in src:
                if '  ' in line:
                    out.add(line.rstrip('\r\n').split('  ', 1)[1].replace('\\', '/'))
    except OSError:
        pass
    return out

def _pack_paths(root):
    out = set()
    base = os.path.join(root, 'skills', 'local', 'packs')
    if not os.path.isdir(base):
        return out
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        for name in files:
            rel = os.path.relpath(os.path.join(d, name), root).replace(os.sep, '/')
            out.add(rel[:-4] if rel.endswith('.new') else rel)
    return out

def managed_paths(root):
    return _manifest_paths(root) | _pack_paths(root)

def _sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def scan(root):
    root = os.path.abspath(root)
    saved = _read_json(os.path.join(root, *STATE_REL.split('/'))).get('items', {})
    items = []
    for rel in sorted(managed_paths(root)):
        pending_rel = rel + '.new'
        pending = os.path.join(root, *pending_rel.split('/'))
        if not os.path.isfile(pending):
            continue
        current = os.path.join(root, *rel.split('/'))
        fingerprint = _sha(pending)
        old = saved.get(pending_rel, {}) if isinstance(saved.get(pending_rel), dict) else {}
        state = old.get('state') if old.get('fingerprint') == fingerprint else 'unseen'
        if state not in ALLOWED_STATES:
            state = 'unseen'
        origin = 'domain_pack' if rel.startswith('skills/local/packs/') else 'package'
        items.append({'path': rel, 'pending': pending_rel, 'current_exists': os.path.isfile(current),
                      'state': state, 'origin': origin, 'fingerprint': fingerprint,
                      'finish_supported': finish_supported(rel)})  # D-01e: scope flag; không phải eligible/granted / scope flag; not eligible or granted
    return items

def _pair(root, pending_rel):
    """Chuẩn hóa và kiểm cặp (bản hiện hành, bản .new) của file package quản lý / Normalise and check a managed pair."""
    rel = (pending_rel or '').replace('\\', '/').lstrip('/')
    current_rel = rel[:-4] if rel.endswith('.new') else ''
    if not current_rel or current_rel not in managed_paths(root):
        raise ValueError('Not a package-managed merge file: ' + rel)
    return rel, current_rel

def _inside(root, rel):
    """Đường dẫn tuyệt đối nằm trong root, không chứa '..' / Absolute path that stays inside root."""
    parts = rel.split('/')
    path = os.path.abspath(os.path.join(root, *parts))
    if '..' in parts or not path.startswith(os.path.abspath(root) + os.sep):
        raise ValueError('Path outside the project: ' + rel)
    return path

def set_state(root, pending_rel, state):
    if state not in ALLOWED_STATES:
        raise ValueError('Invalid merge state: ' + str(state))
    pending_rel, _ = _pair(root, pending_rel)
    pending = _inside(root, pending_rel)
    if not os.path.isfile(pending):
        raise ValueError('Merge file does not exist: ' + pending_rel)
    state_path = os.path.join(root, *STATE_REL.split('/'))
    data = _read_json(state_path)
    items = data.get('items') if isinstance(data.get('items'), dict) else {}
    items[pending_rel] = {'state': state, 'fingerprint': _sha(pending)}
    data = {'schema': 'local-agent-workspace/merge-state-v1', 'items': items}
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with io.open(state_path, 'w', encoding='utf-8', newline='') as dst:
        json.dump(data, dst, ensure_ascii=False, indent=2, sort_keys=True)
        dst.write('\n')
    return {'ok': True, 'path': pending_rel, 'state': state}

def _text_lines(data):
    """Dòng UTF-8, hoặc None nếu là file nhị phân / UTF-8 lines, or None for binary data."""
    if b'\x00' in data[:8192]:
        return None
    try:
        return data.decode('utf-8').splitlines()
    except UnicodeDecodeError:
        return None

def _read_bytes(path):
    with open(path, 'rb') as src:
        return src.read()

def diff(root, pending_rel, max_bytes=DIFF_MAX_BYTES):
    """So sánh chỉ đọc giữa bản hiện hành và bản .new theo hunk có số dòng; không lưu, không ghi.
    Read-only line diff between the current file and its .new copy, as hunks with line numbers; nothing is stored.
    Sizes are checked before reading: a file larger than max_bytes is flagged too_large. A missing current file is
    flagged current_missing and every line of the new copy counts as added. Identical files are flagged identical
    only when both are within max_bytes.
    """
    pending_rel, current_rel = _pair(root, pending_rel)
    pending, current = _inside(root, pending_rel), _inside(root, current_rel)
    if not os.path.isfile(pending):
        raise ValueError('Merge file does not exist: ' + pending_rel)
    exists = os.path.isfile(current)
    res = _diff_result(current_rel, pending_rel, exists, max_bytes)
    if max(os.path.getsize(pending), os.path.getsize(current) if exists else 0) > max_bytes:
        res['too_large'] = True
        return res
    new_data = _read_bytes(pending)
    old_data = _read_bytes(current) if exists else b''
    return _diff_data(res, old_data, new_data, exists)

def _diff_result(current_rel, pending_rel, exists, max_bytes):
    return {'path': current_rel, 'pending': pending_rel, 'current_missing': not exists, 'identical': False,
            'binary': False, 'too_large': False, 'truncated': False, 'added': 0, 'removed': 0, 'hunks': [],
            'max_bytes': max_bytes, 'max_rows': DIFF_MAX_ROWS}

def _diff_data(res, old_data, new_data, exists):
    """Phần so sánh trên hai buffer đã đọc (dùng chung cho diff và preview_replace) / the comparison on two buffers already read."""
    if exists and old_data == new_data:
        res['identical'] = True
        return res
    new_lines, old_lines = _text_lines(new_data), _text_lines(old_data)
    if new_lines is None or old_lines is None:
        res['binary'] = True
        return res
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('replace', 'delete'):
            res['removed'] += i2 - i1
        if tag in ('replace', 'insert'):
            res['added'] += j2 - j1
    rows = 0
    for group in matcher.get_grouped_opcodes(DIFF_CONTEXT):
        old_count = group[-1][2] - group[0][1]
        new_count = group[-1][4] - group[0][3]
        hunk = {'old_start': group[0][1] + 1 if old_count else group[0][1], 'old_count': old_count,
                'new_start': group[0][3] + 1 if new_count else group[0][3], 'new_count': new_count, 'lines': []}
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                entries = [('context', i + 1, j1 + (i - i1) + 1, old_lines[i]) for i in range(i1, i2)]
            else:
                entries = []
                if tag in ('replace', 'delete'):
                    entries += [('removed', i + 1, None, old_lines[i]) for i in range(i1, i2)]
                if tag in ('replace', 'insert'):
                    entries += [('added', None, j + 1, new_lines[j]) for j in range(j1, j2)]
            for op, old_no, new_no, text in entries:
                if rows >= DIFF_MAX_ROWS:
                    res['truncated'] = True
                    break
                hunk['lines'].append({'op': op, 'old': old_no, 'new': new_no, 'text': text})
                rows += 1
            if res['truncated']:
                break
        if hunk['lines']:
            res['hunks'].append(hunk)
        if res['truncated']:
            break
    return res

# ---------------------------------------------------------------- D-01b: xem trước và thay một tài liệu / preview and replace one guide
REPLACE_ALLOWLIST = (
    'docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md', 'docs/HUONG_DAN_SU_DUNG_VI.md', 'docs/HUONG_DAN_SKILLS_VI.md',
    'docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md', 'docs/en/NEW_PROJECT_GUIDE.md', 'docs/en/DAILY_USE_GUIDE.md',
    'docs/en/SKILLS_GUIDE.md', 'docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md')
_ALLOW_LOWER = {x.lower() for x in REPLACE_ALLOWLIST}

# D-01e: finish mở rộng thêm sáu instruction entrypoint; replace vẫn đúng tám guide / D-01e: finish adds six instruction entrypoints; replace keeps the eight guides
_FINISH_ENTRYPOINTS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'en/AGENTS.md', 'en/CLAUDE.md', 'en/GEMINI.md')
# D-01g: finish thêm đúng hai script package (chỉ lưu .new, không chạy/biên dịch); path vẫn phải thuộc managed_paths / exactly two package scripts, finish only (never run or compiled); the path must still be managed
_FINISH_SCRIPTS = ('tools/audit_scripts.py', 'skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py')
FINISH_ALLOWLIST = REPLACE_ALLOWLIST + _FINISH_ENTRYPOINTS + _FINISH_SCRIPTS
_FINISH_ALLOW_LOWER = {x.lower() for x in FINISH_ALLOWLIST}
ARCHIVE_BASE = '.agent/merge-backups'
RECORD_SCHEMA = 'local-agent-workspace/merge-backup-v1'
PREVIEW_SCHEMA = 'local-agent-workspace/merge-replace-preview-v1'
_HEX64 = re.compile(r'[0-9a-f]{64}')
_HOOK = None  # TEST ONLY: _HOOK(point) tại 'captured' (sau khi đọc hai buffer) và 'before_run' (sau kiểm lại .new, trước Transaction.run) / at 'captured' and 'before_run'

class ReplaceRefused(ValueError):
    """Đầu vào bị từ chối trước mọi đọc/ghi; .reason là mã ổn định / refused before any read or write; .reason is a stable code."""
    def __init__(self, reason):
        ValueError.__init__(self, reason)
        self.reason = reason

def _validate_pending_path(pending_rel):
    """Phần kiểm chung cho cả replace_target và finish_target: không strip/chuẩn hóa, từ chối trước đọc file.
    Shared validation for both replace_target and finish_target: no stripping or normalising, refused before any file read."""
    if not isinstance(pending_rel, str) or not pending_rel or len(pending_rel) > 300:
        raise ReplaceRefused('invalid_path')
    if '\\' in pending_rel or ':' in pending_rel or pending_rel.startswith('/') or any(ord(c) < 32 for c in pending_rel):
        raise ReplaceRefused('invalid_path')  # dấu phân cách ngược, ổ đĩa/UNC/ADS, tuyệt đối, ký tự điều khiển / backslash, drive/UNC/ADS, absolute, control chars
    for seg in pending_rel.split('/'):
        if seg in ('', '.', '..') or seg != seg.rstrip(' .'):
            raise ReplaceRefused('invalid_path')  # đoạn rỗng, '.', '..', đuôi chấm/khoảng trắng (Windows bỏ qua) / empty, dot, '..', trailing dot or space
    if not pending_rel.endswith('.new'):
        raise ReplaceRefused('invalid_path')
    return pending_rel[:-4]  # current_rel

def replace_target(pending_rel):
    """Kiểm đường dẫn .new cho replace: không strip, không chuẩn hóa, so khớp chính xác với tám guide.
    Validate the client's .new path for replace: no stripping or normalising, exact match against the eight guides."""
    current_rel = _validate_pending_path(pending_rel)
    if current_rel in REPLACE_ALLOWLIST:
        return pending_rel, current_rel
    if current_rel.lower() in _ALLOW_LOWER:
        raise ReplaceRefused('invalid_path')  # khác hoa/thường: trên NTFS vẫn mở đúng file / a case alias still opens the same file on NTFS
    raise ReplaceRefused('unsupported')

def finish_target(pending_rel):
    """Kiểm đường dẫn .new cho finish: so khớp với mười sáu path (tám guide + sáu instruction entrypoint + hai script package); replace vẫn chỉ tám guide.
    Validate the client's .new path for finish: matches sixteen paths (eight guides + six instruction entrypoints + two package scripts); replace still only the eight guides."""
    current_rel = _validate_pending_path(pending_rel)
    if current_rel in FINISH_ALLOWLIST:
        return pending_rel, current_rel
    if current_rel.lower() in _FINISH_ALLOW_LOWER:
        raise ReplaceRefused('invalid_path')  # khác hoa/thường / a case alias
    raise ReplaceRefused('unsupported')

def finish_supported(path):
    """True khi path (không có .new) nằm trong FINISH_ALLOWLIST; chỉ kiểm scope, không phải eligibility hay grant.
    True when path (without .new) is in FINISH_ALLOWLIST; scope check only, not eligibility or grant."""
    return isinstance(path, str) and path in FINISH_ALLOWLIST

def _sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def _capture(root, rel):
    """Đọc một file thành buffer có giới hạn: (trạng thái, bytes). Lỗi đọc/kiểm KHÔNG được coi là 'missing'.
    One bounded read into a buffer: (status, bytes). A read or check error is never treated as 'missing'."""
    path = os.path.join(root, *rel.split('/'))
    try:
        if not transaction.link_free(path, root):
            return 'unsafe_link', None
        info = os.lstat(path)
    except FileNotFoundError:
        return 'missing', None
    except (OSError, ValueError):
        return 'read_error', None
    if not stat.S_ISREG(info.st_mode):
        return 'not_regular', None
    if info.st_size > DIFF_MAX_BYTES:
        return 'too_large', None
    try:
        with open(path, 'rb') as src:
            data = src.read(DIFF_MAX_BYTES + 1)
    except OSError:
        return 'read_error', None
    if len(data) > DIFF_MAX_BYTES:
        return 'too_large', None
    return 'ok', data

def _strict_text(data):
    """UTF-8 hợp lệ và không có NUL ở bất kỳ vị trí nào / valid UTF-8 and no NUL anywhere."""
    if b'\x00' in data:
        return False
    try:
        data.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False

def _environment(root):
    """(mã lý do hoặc None, các giao dịch dở). Chỉ đọc; không tạo runtime/archive. / (reason or None, unfinished transactions). Read-only."""
    if transaction.runtime_problem(root):
        return 'runtime_unsafe', []
    base = os.path.join(root, *ARCHIVE_BASE.split('/'))
    try:
        if not transaction.link_free(base, root) or (os.path.lexists(base) and not os.path.isdir(base)):
            return 'archive_unsafe', []
    except (OSError, ValueError):
        return 'archive_unsafe', []
    try:
        open_tx = transaction.incomplete(root, strict=True)
    except (OSError, ValueError, TypeError, AttributeError, transaction.TransactionError):
        return 'journal_unreadable', []
    if open_tx:
        return 'transaction_pending', open_tx
    return None, []

def _evaluate(root, pending_rel, target=None):
    """Một lần chụp cặp: (mô tả preview, bytes hiện hành, bytes .new). Hash và diff đều tính từ chính hai buffer này.
    One snapshot of the pair: (preview description, current bytes, candidate bytes). Hashes and the diff come from these same two buffers."""
    root = os.path.abspath(root)
    ev = {'schema': PREVIEW_SCHEMA, 'path': None, 'pending': None, 'eligible': False, 'reason': None, 'identical': False,
          'current_sha256': None, 'candidate_sha256': None, 'diff': None, 'unfinished': [],
          'pending_stays': True, 'html_rebuilt': False, 'archive_base': ARCHIVE_BASE,
          'max_bytes': DIFF_MAX_BYTES, 'max_rows': DIFF_MAX_ROWS}
    try:
        pending_rel, current_rel = (target or replace_target)(pending_rel)  # D-01e: finish truyền finish_target; replace giữ tám guide / finish passes finish_target; replace keeps the eight guides
    except ReplaceRefused as e:
        ev['reason'] = e.reason
        return ev, None, None
    ev['path'], ev['pending'] = current_rel, pending_rel
    if current_rel not in managed_paths(root):
        ev['reason'] = 'not_managed'
        return ev, None, None
    cur_status, cur = _capture(root, current_rel)
    new_status, cand = _capture(root, pending_rel)
    if cur is not None:
        ev['current_sha256'] = _sha_bytes(cur)
    if cand is not None:
        ev['candidate_sha256'] = _sha_bytes(cand)
    if cur_status != 'ok':
        ev['reason'] = 'current_missing' if cur_status == 'missing' else cur_status
    elif new_status != 'ok':
        ev['reason'] = 'candidate_missing' if new_status == 'missing' else new_status
    elif not (_strict_text(cur) and _strict_text(cand)):
        ev['reason'] = 'binary'
    elif cur == cand:
        ev['identical'] = True
        ev['reason'] = 'identical'
    else:
        ev['diff'] = _diff_data(_diff_result(current_rel, pending_rel, True, DIFF_MAX_BYTES), cur, cand, True)
        if ev['diff']['truncated']:
            ev['reason'] = 'truncated'
    if ev['reason'] in (None, 'identical'):
        environment_reason, ev['unfinished'] = _environment(root)
        if environment_reason is not None:
            ev['reason'] = environment_reason
    ev['eligible'] = ev['reason'] is None
    return ev, cur, cand

def preview_replace(root, pending_rel):
    """Chỉ đọc: mô tả snapshot của cặp (đường dẫn chuẩn, hai hash thô, eligibility và lý do, diff). Không phải biên nhận hay quyền.
    Read-only description of a snapshot of the pair; not a receipt, a grant or a security token."""
    return _evaluate(root, pending_rel)[0]

def _new_id():
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8]

def _file_hash(root, rel):
    try:
        return transaction.sha_file(os.path.join(root, *rel.split('/')))
    except OSError:
        return None

def _result(outcome, reason, ev, **extra):
    out = {'outcome': outcome, 'reason': reason, 'path': ev.get('path'), 'pending': ev.get('pending'),
           'pending_stays': True, 'html_rebuilt': False}
    out.update(extra)
    return out

def apply_replace(root, pending_rel, current_sha256, candidate_sha256):
    """Thay bản hiện hành của MỘT tài liệu bằng đúng bytes .new đã xem; lưu cả hai bản trước, giữ .new.
    Replace the current file of ONE guide with the .new bytes that were previewed; both versions are stored first, the .new stays.
    outcome: replaced | noop | stale | blocked | error | partial. Bốn thao tác nằm trong một Transaction; thay current là thao tác CUỐI.
    Giới hạn / limits: Transaction chỉ kiểm hash lúc lập kế hoạch và sát trước replace, không khóa file; .new không bị khóa suốt giao dịch.
    """
    root = os.path.abspath(root)
    if not (isinstance(current_sha256, str) and isinstance(candidate_sha256, str)
            and _HEX64.fullmatch(current_sha256) and _HEX64.fullmatch(candidate_sha256)):
        return _result('blocked', 'bad_request', {})
    ev, cur, cand = _evaluate(root, pending_rel)
    if ev['reason'] is not None and ev['reason'] != 'identical':
        return _result('blocked', ev['reason'], ev, unfinished=[i['id'] for i in ev['unfinished']])
    if (ev['current_sha256'], ev['candidate_sha256']) != (current_sha256, candidate_sha256):
        return _result('stale', 'stale_preview', ev)
    if ev['identical']:
        return _result('noop', 'identical', ev)
    cur_hash, cand_hash = ev['current_sha256'], ev['candidate_sha256']
    if _HOOK is not None:
        _HOOK('captured')
    arch_id = _new_id()
    base = ARCHIVE_BASE + '/' + arch_id
    archive = {'id': arch_id, 'dir': base, 'current': base + '/current.txt', 'incoming': base + '/incoming.txt',
               'record': base + '/record.json', 'current_sha256': cur_hash, 'incoming_sha256': cand_hash}
    record = {'schema': RECORD_SCHEMA, 'record_version': 1, 'path': ev['path'],
              'current_sha256': cur_hash, 'incoming_sha256': cand_hash}
    record_bytes = (json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    tx = transaction.Transaction(root, 'merge_replace', prune=False)
    plan = ((archive['current'], cur, None), (archive['incoming'], cand, None), (archive['record'], record_bytes, None),
            (ev['path'], cand, cur_hash))  # thay current đặt CUỐI cùng / replacing the current file is the last op
    try:
        for rel, data, expected in plan:
            if tx.add(rel, data, 'create_exclusive' if expected is None else 'write', expected_before=expected) is None:
                return _result('blocked', 'plan_failed', ev)
    except transaction.TransactionError:
        if any(os.path.lexists(os.path.join(root, *p[0].split('/'))) for p in plan[:3]):
            return _result('blocked', 'archive_collision', ev)  # không đổi id để né / no retry with another id
        if _file_hash(root, ev['path']) != cur_hash:
            return _result('stale', 'current_changed', ev)
        return _result('blocked', 'unsafe_boundary', ev)
    except OSError:
        return _result('blocked', 'read_error', ev)
    status, again = _capture(root, ev['pending'])  # kiểm lại .new sát trước run / re-check the .new right before the run
    if status != 'ok' or _sha_bytes(again) != cand_hash:
        return _result('stale', 'candidate_changed', ev)
    if _HOOK is not None:
        _HOOK('before_run')
    try:
        tx.run()
    except Exception as exc:
        return _failure(root, tx, exc, ev, archive)
    finally:
        tx.close()
    live_status, live = _capture(root, ev['pending'])
    live_changed = live_status != 'ok' or _sha_bytes(live) != cand_hash
    if not _verify(root, archive, ev['path'], cur_hash, cand_hash, record_bytes):
        return _result('partial', 'verify_mismatch', ev, archive=archive, txid=tx.txid, candidate_live_changed=live_changed,
                       current_state='unknown')
    return _result('replaced', None, ev, archive=archive, txid=tx.txid, protection=tx.protection,
                   candidate_live_changed=live_changed)

def _verify(root, archive, path, cur_hash, cand_hash, record_bytes):
    return (_file_hash(root, path) == cand_hash and _file_hash(root, archive['current']) == cur_hash
            and _file_hash(root, archive['incoming']) == cand_hash and _file_hash(root, archive['record']) == _sha_bytes(record_bytes))

def _failure(root, tx, exc, ev, archive):
    """Quyết định kết quả từ trạng thái thật của giao dịch và file, không từ riêng ngoại lệ; không tự resume/rollback.
    Decide from the real journal and files, never from the exception alone; no automatic resume or rollback."""
    cur_hash, cand_hash = archive['current_sha256'], archive['incoming_sha256']
    try:
        open_tx = [i for i in transaction.incomplete(root) if i['id'] == tx.txid]
    except Exception:
        open_tx = []
    live = _file_hash(root, ev['path'])
    stored = {k: _file_hash(root, archive[k]) for k in ('current', 'incoming', 'record')}
    state = 'unchanged' if live == cur_hash else ('replaced' if live == cand_hash else 'unknown')
    if not open_tx and all(v is None for v in stored.values()) and state == 'unchanged':
        return _result('error', 'write_failed', ev, detail=type(exc).__name__)  # chưa ghi gì / nothing written
    saved = {k: archive[k] for k in ('current', 'incoming', 'record') if stored[k] is not None}
    return _result('partial', 'transaction_unfinished' if open_tx else 'outcome_unproven', ev, txid=tx.txid,
                   archive=dict(archive, saved=saved), current_state=state, detail=type(exc).__name__,
                   done=open_tx[0]['done'] if open_tx else None, total=open_tx[0]['total'] if open_tx else None)

# ---------------------------------------------------------------- D-01c: lưu .new khỏi danh sách chờ, giữ bản hiện hành / archive the .new, keep the current file
# Hai bước tách rời, có thể bị gián đoạn / two separate steps that can be interrupted:
#   1. một Transaction lưu current.txt, incoming.txt, record.json (create_exclusive) vào .agent/merge-backups/<finish_id>/ ; current và .new không nằm trong ops;
#   2. chỉ khi nhật ký quan sát được 'committed' và ba file kiểm đủ: MỘT os.rename không thay thế đưa .new vào pending-retired.txt (Windows, cùng ổ đĩa).
# Không fallback (replace/move/copy+xóa), không xóa, không chuyển ngược. Kết quả luôn được quan sát lại từ file thật, không suy từ ngoại lệ.
FINISH_PREVIEW_SCHEMA = 'local-agent-workspace/merge-finish-preview-v1'
FINISH_OBSERVE_SCHEMA = 'local-agent-workspace/merge-finish-observe-v1'
FINISH_RECORD_SCHEMA = 'local-agent-workspace/merge-finish-v1'
FINISH_OPERATION = 'merge_finish_archive'
RETIRED_SLOT = 'pending-retired.txt'
_FINISH_ID = re.compile(r'finish-[0-9a-f]{32}')
_TXID = re.compile(r'[0-9]{8}-[0-9]{6}-[0-9a-f]{8}')
_BAD_FILE = ('unsafe_link', 'not_regular', 'read_error')

def _windows_supported():
    """Tách riêng để test điều khiển được; rename không thay thế chỉ đã đo trên Windows (trên POSIX os.rename có thể thay đích).
    A seam for tests; the no-replace rename is only measured on Windows (on POSIX os.rename may replace the destination)."""
    return os.name == 'nt'

def _abs(root, rel):
    return os.path.join(root, *rel.split('/'))

def finish_locators(finish_id):
    """Vị trí cố định, dựng từ ID đã kiểm định dạng; không lấy gì từ client / fixed locators built from a format-checked id."""
    base = ARCHIVE_BASE + '/' + finish_id
    return {'id': finish_id, 'dir': base, 'current': base + '/current.txt', 'incoming': base + '/incoming.txt',
            'record': base + '/record.json', 'retired': base + '/' + RETIRED_SLOT}

def _record_bytes(finish_id, path, cur_hash, cand_hash, txid):
    record = {'schema': FINISH_RECORD_SCHEMA, 'record_version': 1, 'finish_id': finish_id, 'path': path,
              'current_sha256': cur_hash, 'incoming_sha256': cand_hash, 'archive_txid': txid}
    return (json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')

def _same_volume(root, pending_rel, dest_rel):
    """Thư mục chứa .new và nơi đặt đích (tổ tiên gần nhất đang có) cùng một ổ đĩa; không chứng minh được thì False.
    The folder holding the .new and the nearest existing ancestor of the destination share a volume; False when it cannot be shown."""
    try:
        src = os.stat(os.path.dirname(_abs(root, pending_rel)))
        target = _abs(root, dest_rel)
        while not os.path.lexists(target):
            parent = os.path.dirname(target)
            if parent == target:
                return False
            target = parent
        dst = os.stat(target)
    except OSError:
        return False
    return bool(src.st_dev) and src.st_dev == dst.st_dev

def _probe(root, rel):
    """(trạng thái, sha256) của một file; lỗi đọc hoặc liên kết không bao giờ là 'absent' / (state, sha256); a read error or link is never 'absent'."""
    path = _abs(root, rel)
    try:
        if not transaction.link_free(path, root):
            return 'unsafe_link', None
        info = os.lstat(path)
    except FileNotFoundError:
        return 'absent', None
    except (OSError, ValueError):
        return 'read_error', None
    if not stat.S_ISREG(info.st_mode):
        return 'not_regular', None
    try:
        return 'present', _sha(path)
    except OSError:
        return 'read_error', None

def _probe_dir(root, rel):
    path = _abs(root, rel)
    try:
        if not transaction.link_free(path, root):
            return 'unsafe_link'
        info = os.lstat(path)
    except FileNotFoundError:
        return 'absent'
    except (OSError, ValueError):
        return 'read_error'
    return 'present' if stat.S_ISDIR(info.st_mode) else 'not_regular'

def _view(probe):
    return {'state': probe[0], 'sha256': probe[1]}

def _journal_info(root, txid, want_paths):
    """Trạng thái nhật ký archive đọc từ chính file nhật ký; lỗi đọc là 'unreadable', không phải 'absent'.
    Archive journal status read from the journal file itself; a read error is 'unreadable', never 'absent'."""
    path = os.path.join(transaction.txdir(root, txid), 'journal.json')
    try:
        if not transaction.link_free(path, root):
            return 'unsafe_link', False
        with io.open(path, encoding='utf-8') as src:
            journal = json.load(src)
    except FileNotFoundError:
        return 'absent', False
    except (OSError, ValueError):
        return 'unreadable', False
    if not (isinstance(journal, dict) and journal.get('schema') == transaction.SCHEMA and isinstance(journal.get('status'), str)
            and isinstance(journal.get('ops'), list)):
        return 'unreadable', False
    ops = journal['ops']
    ops_ok = (journal.get('operation') == FINISH_OPERATION and all(isinstance(o, dict) for o in ops)
              and [o.get('path') for o in ops] == want_paths and all(o.get('state') == 'done' for o in ops))
    return journal['status'], ops_ok

def _archive_status(root, finish_id, path, cur_hash, cand_hash, txid=None):
    """Đối chiếu thư mục archive, record và nhật ký với cặp đã chọn; chỉ đọc. phase: none | unfinished | incomplete | rolled_back | unverified | committed.
    Check the archive folder, record and journal against the chosen pair; read-only."""
    loc = finish_locators(finish_id)
    st = {'dir': _probe_dir(root, loc['dir']), 'files': {k: _probe(root, loc[k]) for k in ('current', 'incoming', 'record')},
          'txid': txid, 'journal': 'absent', 'ops_ok': False, 'record_ok': False, 'ok': False, 'phase': 'none'}
    if st['files']['record'][0] == 'present':
        status, data = _capture(root, loc['record'])
        parsed = None
        if status == 'ok':
            try:
                value = json.loads(data.decode('utf-8'))
            except (ValueError, UnicodeDecodeError):
                value = None
            if isinstance(value, dict) and isinstance(value.get('archive_txid'), str) and _TXID.fullmatch(value['archive_txid']):
                parsed = value['archive_txid']
        if parsed is not None and txid in (None, parsed):
            st['txid'] = txid = parsed
            st['record_ok'] = data == _record_bytes(finish_id, path, cur_hash, cand_hash, parsed)  # đúng từng byte / byte for byte
    if txid is not None:
        st['journal'], st['ops_ok'] = _journal_info(root, txid, [loc[k] for k in ('current', 'incoming', 'record')])
    files = st['files']
    snapshots_ok = (files['current'] == ('present', cur_hash) and files['incoming'] == ('present', cand_hash))
    st['ok'] = st['record_ok'] and snapshots_ok and st['journal'] == 'committed' and st['ops_ok']
    anything = st['dir'] != 'absent' or any(v[0] != 'absent' for v in files.values())
    if st['ok']:
        st['phase'] = 'committed'
    elif st['journal'] in transaction.INCOMPLETE:
        st['phase'] = 'unfinished'
    elif st['journal'] in ('rolled_back', 'rollback_partial'):
        st['phase'] = 'rolled_back'
    elif not anything and st['journal'] == 'absent':
        st['phase'] = 'none'
    elif files['record'][0] == 'absent' and st['journal'] == 'absent':
        st['phase'] = 'incomplete'
    else:
        st['phase'] = 'unverified'
    return st

def _classify(source, slot, current, arc, cur_hash, cand_hash):
    """Bảng quan sát → (trạng thái, lý do). Chỉ 'finished' khi source vắng, slot đúng bytes đã chọn, current đúng, archive đủ.
    The observation table → (state, reason). 'finished' only when the source is gone, the slot holds the chosen bytes, current is as chosen and the archive is verified."""
    seen = [source[0], slot[0], current[0], arc['dir']] + [v[0] for v in arc['files'].values()]
    if any(s in _BAD_FILE for s in seen) or arc['journal'] in ('unsafe_link', 'unreadable'):
        return 'unknown', 'unreadable_or_unsafe'
    if current[0] != 'present':
        return 'conflict', 'current_missing'
    if current[1] != cur_hash:
        return 'conflict', 'current_changed'
    has_source, has_slot = source[0] == 'present', slot[0] == 'present'
    phase = arc['phase']
    if phase == 'committed':
        if has_source and has_slot:
            return 'conflict', 'both_present'
        if has_slot:
            return ('finished', None) if slot[1] == cand_hash else ('conflict', 'moved_bytes_differ')
        if not has_source:
            return 'unknown', 'both_absent'
        return ('still_pending', None) if source[1] == cand_hash else ('conflict', 'candidate_changed')
    if not has_source and not has_slot:
        return 'unknown', 'both_absent'
    if has_slot:
        return 'conflict', 'archive_unverified'
    if source[1] != cand_hash:
        return 'conflict', 'candidate_changed'
    return {'none': ('not_started', None), 'unfinished': ('partial', 'transaction_unfinished'),
            'incomplete': ('partial', 'archive_incomplete'), 'rolled_back': ('partial', 'archive_rolled_back')}.get(
                phase, ('partial', 'archive_unverified'))

def _finish_report(root, path, cur_hash, cand_hash, finish_id, txid=None):
    """Quan sát chỉ đọc: source .new, slot archive, current, snapshot, record, nhật ký → trạng thái. Không ghi, không hoàn tất giùm.
    Read-only observation of the .new source, the archive slot, current, snapshots, record and journal."""
    loc = finish_locators(finish_id)
    source, slot, current = _probe(root, path + '.new'), _probe(root, loc['retired']), _probe(root, path)
    arc = _archive_status(root, finish_id, path, cur_hash, cand_hash, txid)
    state, reason = _classify(source, slot, current, arc, cur_hash, cand_hash)
    unfinished = []
    if arc['phase'] in ('unfinished', 'incomplete', 'unverified'):
        try:
            unfinished = [i['id'] for i in transaction.incomplete(root) if i.get('operation') == FINISH_OPERATION]
        except Exception:
            unfinished = []
    return {'schema': FINISH_OBSERVE_SCHEMA, 'state': state, 'reason': reason, 'phase': arc['phase'], 'finish_id': finish_id,
            'path': path, 'pending': path + '.new', 'archive': loc, 'archive_dir': arc['dir'], 'txid': arc['txid'], 'journal': arc['journal'],
            'observed': {'source': _view(source), 'slot': _view(slot), 'current': _view(current),
                         'snapshot': {k: _view(v) for k, v in arc['files'].items()}},
            'unfinished': unfinished, 'current_stays': True, 'html_rebuilt': False, 'manifest_updated': False}

def _finish_inputs_ok(current_sha256, candidate_sha256, finish_id):
    return (isinstance(current_sha256, str) and isinstance(candidate_sha256, str) and isinstance(finish_id, str)
            and _HEX64.fullmatch(current_sha256) is not None and _HEX64.fullmatch(candidate_sha256) is not None
            and _FINISH_ID.fullmatch(finish_id) is not None)

def _finish_eval(root, pending_rel):
    """Một lần chụp cặp cho finish: cùng _evaluate nhưng allowlist mười sáu path; cặp giống nhau vẫn hợp lệ; thêm điều kiện OS/ổ đĩa.
    One snapshot of the pair for finish: the same _evaluate with the sixteen-path allowlist; an identical pair is eligible; adds the OS and volume conditions."""
    root = os.path.abspath(root)
    ev, cur, cand = _evaluate(root, pending_rel, finish_target)
    fv = dict(ev, schema=FINISH_PREVIEW_SCHEMA, finish_id=None, archive=None, current_stays=True, pending_moves=True, manifest_updated=False)
    for key in ('pending_stays', 'eligible'):
        fv.pop(key, None)
    reason = None if ev['reason'] == 'identical' else ev['reason']
    if reason is None and fv['path'] is not None:
        if not _windows_supported():
            reason = 'os_unsupported'
        elif not _same_volume(root, fv['pending'], ARCHIVE_BASE):
            reason = 'filesystem_unsupported'
    fv['reason'] = reason
    fv['eligible'] = reason is None
    return fv, cur, cand

def preview_finish(root, pending_rel):
    """Chỉ đọc: mô tả cặp và cấp finish_id (chỉ để tìm lần thao tác; không phải quyền, token hay bằng chứng đã review). Không tạo file hay runtime.
    Read-only: describes the pair and issues a finish_id (only to find the operation again; not a grant, a token or review evidence)."""
    fv = _finish_eval(os.path.abspath(root), pending_rel)[0]
    if fv['eligible']:
        fv['finish_id'] = 'finish-' + uuid.uuid4().hex
        fv['archive'] = finish_locators(fv['finish_id'])
    return fv

def observe_finish(root, pending_rel, current_sha256, candidate_sha256, finish_id):
    """Chỉ đọc: kiểm một lần finish theo ID + cặp đã xem; vị trí tự dựng, record không phải locator hay quyền. Không mutate, không retry.
    Read-only: check one finish by id and the previewed pair; locators are built here, the record is neither a locator nor a grant."""
    root = os.path.abspath(root)
    refused = {'schema': FINISH_OBSERVE_SCHEMA, 'state': 'refused', 'reason': None, 'finish_id': None, 'path': None, 'pending': None}
    if not _finish_inputs_ok(current_sha256, candidate_sha256, finish_id):
        return dict(refused, reason='bad_request')
    try:
        pending_rel, current_rel = finish_target(pending_rel)  # D-01e/g: dùng finish_target (16 path) thay replace_target (8 guide) / use finish_target (16 paths) not replace_target (8 guides)
    except ReplaceRefused as e:
        return dict(refused, reason=e.reason)
    if current_rel not in managed_paths(root):
        return dict(refused, reason='not_managed')
    return _finish_report(root, current_rel, current_sha256, candidate_sha256, finish_id)

def _finish_result(outcome, reason, fv, **extra):
    out = {'outcome': outcome, 'reason': reason, 'path': fv.get('path'), 'pending': fv.get('pending'),
           'current_stays': True, 'html_rebuilt': False, 'manifest_updated': False}
    out.update(extra)
    return out

def apply_finish(root, pending_rel, current_sha256, candidate_sha256, finish_id):
    """Giữ nguyên bản hiện hành; lưu bản hiện hành + .new đã xem rồi chuyển đúng .new đó khỏi chỗ đang được quét. Không ghi vào current.
    Keep the current file; store the current file and the previewed .new, then move that .new out of the scanned place. Never writes to current.
    outcome: finished | still_pending | partial | conflict | unknown | stale | blocked | error. Hai bước, không nguyên tử về mặt hệ thống / two steps, no system-wide guarantee."""
    root = os.path.abspath(root)
    if not _finish_inputs_ok(current_sha256, candidate_sha256, finish_id):
        return _finish_result('blocked', 'bad_request', {})
    fv, cur, cand = _finish_eval(root, pending_rel)
    if not fv['eligible']:
        return _finish_result('blocked', fv['reason'], fv, finish_id=finish_id, unfinished=[i['id'] for i in fv['unfinished']])
    cur_hash, cand_hash = fv['current_sha256'], fv['candidate_sha256']
    if (cur_hash, cand_hash) != (current_sha256, candidate_sha256):
        return _finish_result('stale', 'stale_preview', fv, finish_id=finish_id,
                              stale={'current': cur_hash != current_sha256, 'candidate': cand_hash != candidate_sha256})
    loc = finish_locators(finish_id)
    if any(os.path.lexists(_abs(root, loc[k])) for k in ('dir', 'current', 'incoming', 'record', 'retired')):
        return _finish_result('blocked', 'archive_collision', fv, finish_id=finish_id)  # không đổi id, không dùng lại / no new id, no reuse
    tx = transaction.Transaction(root, FINISH_OPERATION, prune=False)
    record = _record_bytes(finish_id, fv['path'], cur_hash, cand_hash, tx.txid)
    plan = ((loc['current'], cur), (loc['incoming'], cand), (loc['record'], record))  # current và .new KHÔNG nằm trong ops / neither is an op
    try:
        for rel, data in plan:
            if tx.add(rel, data, 'create_exclusive', expected_before=None) is None:
                return _finish_result('blocked', 'plan_failed', fv, finish_id=finish_id)
    except transaction.TransactionError:
        if any(os.path.lexists(_abs(root, p[0])) for p in plan):
            return _finish_result('blocked', 'archive_collision', fv, finish_id=finish_id)
        return _finish_result('blocked', 'unsafe_boundary', fv, finish_id=finish_id)
    except OSError:
        return _finish_result('blocked', 'read_error', fv, finish_id=finish_id)
    cur_status, cur_again = _capture(root, fv['path'])
    if cur_status != 'ok' or _sha_bytes(cur_again) != cur_hash:
        return _finish_result('stale', 'current_changed', fv, finish_id=finish_id)
    cand_status, cand_again = _capture(root, fv['pending'])
    if cand_status != 'ok' or _sha_bytes(cand_again) != cand_hash:
        return _finish_result('stale', 'candidate_changed', fv, finish_id=finish_id)
    if _HOOK is not None:
        _HOOK('finish_before_run')
    try:
        tx.run()
    except Exception as exc:
        return _finish_failure(root, tx, exc, fv, finish_id)
    finally:
        tx.close()
    if _HOOK is not None:
        _HOOK('finish_after_run')
    rep = _finish_report(root, fv['path'], cur_hash, cand_hash, finish_id, tx.txid)
    if rep['phase'] != 'committed' or rep['txid'] != tx.txid:  # commit không chứng minh được: KHÔNG rename / commit not proven: no rename
        return _finish_result('partial', 'verify_mismatch', fv, finish_id=finish_id, txid=tx.txid, phase=rep['phase'], state=rep['state'],
                              archive=rep['archive'], observed=rep['observed'], snapshot_saved=False, pending_moved=False)
    blocked, exc, pinned = _finish_move(root, fv['path'], finish_id, cur_hash, cand_hash, tx.txid)
    rep = _finish_report(root, fv['path'], cur_hash, cand_hash, finish_id, tx.txid)
    state = rep['state']
    if state == 'finished':
        reason = 'observed_after_error' if exc is not None else None
    elif state == 'still_pending':
        reason = blocked or ('rename_failed' if exc is not None else 'rename_not_observed')
    else:
        reason = rep['reason']
    obs = rep['observed']
    moved = True if (obs['source']['state'], obs['slot']['state']) == ('absent', 'present') else (
        False if (obs['source']['state'], obs['slot']['state']) == ('present', 'absent') else None)
    return _finish_result(state, reason, fv, finish_id=finish_id, state=state, phase=rep['phase'], txid=tx.txid, archive=rep['archive'],
                          observed=obs, snapshot_saved=rep['phase'] == 'committed', pending_moved=moved, dir_pins=pinned,
                          protection=tx.protection, detail=type(exc).__name__ if exc is not None else None)

def _finish_move(root, path, finish_id, cur_hash, cand_hash, txid):
    """MỘT os.rename không thay thế, trong held() của parent. Mọi lỗi (OS, guard, hook) chỉ được ghi lại; kết quả do quan sát quyết định.
    ONE no-replace os.rename inside held(); every error (OS, guard, hook) is only recorded, the observation decides the result."""
    loc = finish_locators(finish_id)
    src, dst = _abs(root, path + '.new'), _abs(root, loc['retired'])
    blocked, exc, pinned = None, None, False
    try:
        with transaction.held(root, src, dst, _abs(root, path), *[_abs(root, loc[k]) for k in ('current', 'incoming', 'record')]) as check:
            pinned = bool(check.protected)
            blocked = _finish_precheck(root, path, loc, cur_hash, cand_hash, txid)
            if blocked is None:
                check()
                if _HOOK is not None:
                    _HOOK('finish_before_rename')
                try:
                    os.rename(src, dst)  # KHÔNG os.replace/shutil.move/copy-xóa/chuyển ngược: đích đã có thì Windows từ chối / never replaces, no fallback
                except OSError as e:
                    exc = e
                if _HOOK is not None:
                    _HOOK('finish_after_rename')
    except Exception as e:  # lỗi guard hoặc hook có thể xảy ra sau khi đã chuyển; luôn quan sát lại / may land after the move; always re-observe
        exc = exc or e
    return blocked, exc, pinned

def _finish_precheck(root, path, loc, cur_hash, cand_hash, txid):
    """Kiểm lại sát rename: hai hash thô, archive đã kiểm, slot vắng, hệ điều hành, cùng ổ đĩa. Trả lý do chặn hoặc None."""
    status, data = _capture(root, path)
    if status != 'ok' or _sha_bytes(data) != cur_hash:
        return 'current_changed'
    status, data = _capture(root, path + '.new')
    if status != 'ok' or _sha_bytes(data) != cand_hash:
        return 'candidate_changed'
    arc = _archive_status(root, loc['id'], path, cur_hash, cand_hash, txid)
    if arc['phase'] != 'committed':
        return 'archive_changed'
    if os.path.lexists(_abs(root, loc['retired'])):
        return 'slot_occupied'
    if not _windows_supported():
        return 'os_unsupported'
    if not _same_volume(root, path + '.new', loc['retired']):
        return 'filesystem_unsupported'
    return None

def _finish_failure(root, tx, exc, fv, finish_id):
    """Ngoại lệ từ giao dịch archive: không bao giờ rename. Quyết định từ nhật ký và file thật, không từ riêng ngoại lệ; không tự resume/rollback.
    The archive transaction raised: never rename. Decide from the real journal and files; no automatic resume or rollback."""
    try:
        open_tx = [i for i in transaction.incomplete(root) if i['id'] == tx.txid]
    except Exception:
        open_tx = []
    rep = _finish_report(root, fv['path'], fv['current_sha256'], fv['candidate_sha256'], finish_id, tx.txid)
    obs = rep['observed']
    nothing = rep['archive_dir'] == 'absent' and all(v['state'] == 'absent' for v in obs['snapshot'].values())
    if not open_tx and nothing and obs['source']['state'] == 'present':
        return _finish_result('error', 'write_failed', fv, finish_id=finish_id, detail=type(exc).__name__)  # chưa ghi gì / nothing written
    if rep['phase'] == 'committed':
        state = rep['state']
        reason = ('archive_committed_after_error' if state == 'still_pending' else
                  'observed_after_error' if state == 'finished' else rep['reason'])
        moved = True if (obs['source']['state'], obs['slot']['state']) == ('absent', 'present') else (
            False if (obs['source']['state'], obs['slot']['state']) == ('present', 'absent') else None)
        return _finish_result(state, reason, fv, finish_id=finish_id, txid=tx.txid, phase=rep['phase'], state=state,
                              archive=rep['archive'], observed=obs, snapshot_saved=True, pending_moved=moved,
                              detail=type(exc).__name__)
    return _finish_result('partial', 'transaction_unfinished' if open_tx else 'outcome_unproven', fv, finish_id=finish_id, txid=tx.txid,
                          phase=rep['phase'], state=rep['state'], archive=rep['archive'], observed=obs, snapshot_saved=False, pending_moved=False,
                          detail=type(exc).__name__, done=open_tx[0]['done'] if open_tx else None, total=open_tx[0]['total'] if open_tx else None)
