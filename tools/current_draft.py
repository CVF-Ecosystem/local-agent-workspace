#!/usr/bin/env python3
"""Nháp hiện tại và lịch sử các bản (điều hướng cho luồng P-CN1). / Current draft and its history (navigation for the P-CN1 flow).

Dùng / Usage (agent và bảng điều khiển dùng cùng helper này / agents and the panel share this helper):
  python tools/current_draft.py status [--project DIR] [--result-json]
  python tools/current_draft.py list   [--project DIR] [--result-json]
  python tools/current_draft.py select --rid RID [--project DIR]                                   xem trước, không ghi / preview, nothing written
  python tools/current_draft.py select --rid RID --apply --expected-state HEX --expected-selection HEX [--project DIR]
  python tools/current_draft.py open   --rid RID [--ack changed|unverified] [--project DIR]

Đây chỉ là chọn và mở bản, KHÔNG là nghiệm thu: không PASS, không D4, không "đã nghiệm thu". Hash khớp chỉ nói bytes hiện tại bằng bytes owner đã ghi.
It only selects and opens a revision: no PASS, no D4, never "accepted". A matching hash only says the bytes are the ones the writer recorded.

Con trỏ duy nhất / the only pointer: đúng một dòng trong mục `## Current artifact` của .agent/STATE.md
  <!-- law-current-draft/1 {"path":"working/...","rid":"<32 hex>","digest":"sha256:<64 hex>"} -->
Mọi marker `law-current-draft` khác (trùng, hỏng, sai mục) hoặc mục thiếu/trùng ⇒ UNRESOLVED, không chọn theo mtime hay supersedes. Con trỏ chỉ điều hướng.

Ghi duy nhất của helper: một marker vào STATE qua P-CTX1 (tools/context_update.py), sau khi so pin với policy. Preview, status, list, open không ghi gì.
Code owner luôn nạp từ cây LAW cố định cạnh file này (đúng bytes đã so pin); --project chỉ là dữ liệu.
TEST ONLY: biến LOCAL_AGENT_WORKSPACE_TEST_OPEN_LOG (đường dẫn file) khiến `open` ghi đường dẫn vào file thay vì mở ứng dụng; không đặt khi dùng thật.
Windows + NTFS cục bộ, hợp tác/ADVISORY: quan sát tại thời điểm, không chống đua hay sửa ngoài. Cần jsonschema (checker v3) để so pin; thiếu thì UNAVAILABLE và không làm gì.
Mã thoát / exit: 0 ok; 3 CONFLICT; 4 ERROR/UNAVAILABLE/REFUSED; 5 UNKNOWN; 2 lỗi cách dùng.
"""
import argparse
import hashlib
import importlib
import importlib.util
import json
import os
import re
import sys
import threading

sys.dont_write_bytecode = True  # không để lại __pycache__ trong cây LAW / leave no __pycache__ in the LAW tree
CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(CODE_ROOT, 'tools'))
import transaction  # noqa: E402
from result_schema import emit, make  # noqa: E402

MARKER_VERSION = 'law-current-draft/1'
MARKER_WORD = 'law-current-draft'
SECTION = 'Current artifact'
ALLOWED_EXT = ('.docx', '.xlsx', '.pptx', '.pdf', '.txt', '.md', '.csv')
LIGHT_ZONES = ('working', 'output_new')
MAX_CANDIDATES = 512
HISTORY_SHOWN = 5
MAX_STATE_BYTES = 8 * 1024 * 1024
HEX64 = re.compile(r'^[0-9a-f]{64}$')
HEX_ARG = re.compile(r'^(?:sha256:)?([0-9a-f]{64})$')
MARKER_LINE = re.compile(r'^<!-- law-current-draft/1 (\{.*\}) -->[ \t]*$')
ENTRY_FILE = os.path.join(CODE_ROOT, '.cvf', 'checks', 'control_check_v3.py')
CTX_REL = ('tools', 'context_update.py')
STATES = ('matched', 'changed', 'unverified', 'unopenable')
EXIT = {'OK': 0, 'PREVIEW': 0, 'UNCHANGED': 0, 'WRITTEN': 0, 'OPENED': 0, 'ACK_REQUIRED': 4, 'CONFLICT': 3, 'ERROR': 4, 'UNAVAILABLE': 4,
        'REFUSED': 4, 'UNKNOWN': 5}
STATUS = {'OK': 'success', 'PREVIEW': 'preview', 'UNCHANGED': 'success', 'WRITTEN': 'success', 'OPENED': 'success', 'ACK_REQUIRED': 'blocked',
          'CONFLICT': 'blocked', 'ERROR': 'error', 'UNAVAILABLE': 'error', 'REFUSED': 'error', 'UNKNOWN': 'partial'}
LANG = 'vi'
OPEN_LOG_ENV = 'LOCAL_AGENT_WORKSPACE_TEST_OPEN_LOG'  # TEST ONLY, không đặt khi dùng thật / never set in real use
_lock = threading.RLock()      # bootstrap của owner / owner bootstrap
_apply_lock = threading.Lock()  # một lần chọn ghi mỗi lúc trong một tiến trình / one selection write at a time in a process
_ctx_cache = {}


def L(vi, en): return en if LANG == 'en' else vi


class Unavailable(Exception):
    """Owner, pin hoặc phụ thuộc không dùng được: không làm gì, không đoán. / owner, pin or dependency unusable: do nothing, never guess."""

    def __init__(self, reason):
        Exception.__init__(self, reason)
        self.reason = reason


# ---------------------------------------------------------------- bootstrap từ cây nguồn cố định / fixed-source bootstrap
def _checks():
    """(observer, loader) của checker v3 nạp bằng đúng entry cố định; code không bao giờ lấy từ project_root."""
    with _lock:
        try:
            mod = sys.modules.get('law_cvf_entry_v3_current_draft')
            if mod is None:
                spec = importlib.util.spec_from_file_location('law_cvf_entry_v3_current_draft', ENTRY_FILE)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sys.modules['law_cvf_entry_v3_current_draft'] = mod
            package = mod._load_package()
            return importlib.import_module(package.__name__ + '.observer'), importlib.import_module(package.__name__ + '.loader')
        except Exception:
            raise Unavailable('CHECKS_UNAVAILABLE')


def _unavailable_reason(exc):
    reasons = getattr(exc, 'reasons', None)
    return 'DEPENDENCY_MISSING' if isinstance(reasons, set) and 'DEPENDENCY_MISSING' in reasons else 'OWNER_UNAVAILABLE'


class Env(object):
    """Một lần gọi: owner P-CN1 đúng pin (qua observer), project là dữ liệu. P-CTX1 chỉ nạp khi cần ghi."""

    def __init__(self, project_root):
        if type(project_root) is not str or not project_root or not os.path.isdir(project_root):
            raise Unavailable('PROJECT_INVALID')
        self.project = os.path.abspath(project_root)
        self.observer, self.loader = _checks()
        try:
            self.pn = self.observer.load_owner()
        except Exception as exc:
            raise Unavailable(_unavailable_reason(exc))
        info = self.pn.file_info(self.project)
        if not info or info['attributes'] & (0x10 | 0x400) != 0x10:
            raise Unavailable('ROOT_UNSAFE')  # phải là thư mục thường, không phải liên kết / must be a plain folder, not a link

    def ctx(self):
        """Module context_update chỉ sau khi so bytes với pin trong policy; thực thi đúng bytes đã so, publish_new là bản đã pin của P-CN1."""
        with _lock:
            try:
                owners = self.loader.load_owners()
                field = self.loader.parse_json_bytes(owners.policy_bytes).get('operational_context_protocol')
                path = os.path.join(CODE_ROOT, *CTX_REL)
                with open(path, 'rb') as fh:
                    raw = fh.read()
            except Exception as exc:
                raise Unavailable(_unavailable_reason(exc))
            digest = hashlib.sha256(raw).hexdigest()
            if not (isinstance(field, dict) and (field.get('protocol_id'), field.get('protocol_version'), field.get('entrypoint')) ==
                    ('P-CTX1', 1, 'tools/context_update.py') and field.get('entrypoint_sha256') == 'sha256:' + digest):
                raise Unavailable('CONTEXT_OWNER_PIN_MISMATCH')
            cached = _ctx_cache.get('mod')
            if cached is not None and _ctx_cache.get('key') == (digest, id(self.pn)):
                return cached
            mod = importlib.util.module_from_spec(importlib.util.spec_from_file_location('law_current_draft_context_update', path))
            saved_mod, saved_path = sys.modules.get('publish_new'), list(sys.path)
            sys.modules['publish_new'] = self.pn  # context_update gọi helper của đúng bản P-CN1 đã pin / it uses the pinned P-CN1 module
            try:
                exec(compile(raw, path, 'exec'), mod.__dict__)  # đúng bytes đã băm, không đọc lại / the bytes that were hashed, not a second read
            except Exception:
                raise Unavailable('CONTEXT_OWNER_UNAVAILABLE')
            finally:
                if saved_mod is None:
                    sys.modules.pop('publish_new', None)
                else:
                    sys.modules['publish_new'] = saved_mod
                sys.path[:] = saved_path
            _ctx_cache.update(mod=mod, key=(digest, id(self.pn)))
            return mod


# ---------------------------------------------------------------- con trỏ trong STATE / the pointer in STATE
def _strict_json(text):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate key')
            out[key] = value
        return out

    def const(_name):
        raise ValueError('non-finite')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=const)


def _ext_ok(path):
    return path.lower().endswith(ALLOWED_EXT)


def _path_ok(pn, path):
    """Dạng đường dẫn theo owner, chỉ working/output, đuôi trong danh sách, và an toàn trong chú thích HTML."""
    return (isinstance(path, str) and not pn.path_form_problem(path) and pn.target_zone(path) in LIGHT_ZONES
            and _ext_ok(path) and '--' not in path)


def _tuple_of(pn, obj):
    """{'path','rid','digest'} nếu obj đúng ba khóa và đúng kiểu, else None."""
    if not (isinstance(obj, dict) and set(obj) == {'path', 'rid', 'digest'}):
        return None
    path, rid, digest = obj['path'], obj['rid'], obj['digest']
    if not (isinstance(rid, str) and pn.RID_RE.fullmatch(rid) and isinstance(digest, str) and pn.DIGEST_RE.fullmatch(digest)):
        return None
    return {'path': path, 'rid': rid, 'digest': digest} if _path_ok(pn, path) else None


def _lines(text):
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    return [ln[:-1] if ln.endswith('\r') else ln for ln in lines]


def parse_pointer(pn, text):
    """Phân tích con trỏ. Đếm MỌI marker ứng viên trước khi parse; không chọn marker 'còn hợp lệ' khi có nhiều hơn một.

    Trả {'state': 'NONE'|'SET'|'UNRESOLVED', 'reason', 'tuple', 'line'}. UNRESOLVED nếu mục thiếu/trùng, marker trùng/hỏng/sai mục/sai version/key thừa-trùng.
    """
    lines = _lines(text)
    heads = [i for i, ln in enumerate(lines) if ln.startswith('## ')]
    sections = [i for i in heads if lines[i].rstrip() == '## ' + SECTION]
    out = {'state': 'UNRESOLVED', 'reason': None, 'tuple': None, 'line': None}
    if len(sections) != 1:
        out['reason'] = 'SECTION_MISSING' if not sections else 'SECTION_DUPLICATE'
        return out
    if lines[sections[0]] != '## ' + SECTION:
        out['reason'] = 'SECTION_MALFORMED'
        return out
    start = sections[0]
    end = next((i for i in heads if i > start), len(lines))
    hits = [i for i, ln in enumerate(lines) for _ in range(ln.count(MARKER_WORD))]
    if not hits:
        out['state'] = 'NONE'
        return out
    if len(hits) > 1:
        out['reason'] = 'MARKER_DUPLICATE'
        return out
    at = hits[0]
    if not start < at < end:
        out['reason'] = 'MARKER_WRONG_SECTION'
        return out
    m = MARKER_LINE.match(lines[at])
    if not m:
        out['reason'] = 'MARKER_MALFORMED'
        return out
    try:
        obj = _strict_json(m.group(1))
    except (ValueError, RecursionError):
        out['reason'] = 'MARKER_MALFORMED'
        return out
    tup = _tuple_of(pn, obj)
    if tup is None:
        out['reason'] = 'MARKER_MALFORMED'
        return out
    out.update(state='SET', tuple=tup, line=at)
    return out


def marker_line(tup):
    body = json.dumps({'path': tup['path'], 'rid': tup['rid'], 'digest': tup['digest']}, ensure_ascii=True, separators=(',', ':'))
    return '<!-- %s %s -->' % (MARKER_VERSION, body)


def with_marker(pn, text, tup):
    """STATE mới = STATE cũ + đúng một marker (thay marker hợp lệ, hoặc thêm ngay sau dòng trống của heading). Giữ nguyên mọi byte khác, kể cả newline."""
    ptr = parse_pointer(pn, text)
    if ptr['state'] == 'UNRESOLVED':
        raise ValueError(ptr['reason'])
    parts = re.findall(r'[^\n]*\n|[^\n]+', text)
    eol = lambda part: '\r\n' if part.endswith('\r\n') else ('\n' if part.endswith('\n') else '')
    if ptr['state'] == 'SET':
        parts[ptr['line']] = marker_line(tup) + eol(parts[ptr['line']])
    else:
        head = next(i for i, part in enumerate(parts) if part.rstrip('\r\n') == '## ' + SECTION)
        newline = eol(parts[head]) or '\n'
        at = head + 2  # sau heading và dòng trống bắt buộc / after the heading and its required blank line
        if at > len(parts):
            raise ValueError('SECTION_MISSING')
        if at == len(parts) and parts and not eol(parts[-1]):
            parts[-1] += newline
        parts.insert(at, marker_line(tup) + newline)
    new = ''.join(parts)
    again = parse_pointer(pn, new)
    if again['state'] != 'SET' or again['tuple'] != tup:
        raise ValueError('MARKER_BUILD_FAILED')
    return new


# ---------------------------------------------------------------- đọc STATE và evidence / reading STATE and evidence
def _read_state(env):
    """(bytes, None) hoặc (None, lý do). Không theo liên kết."""
    path = os.path.join(env.project, '.agent', 'STATE.md')
    if not os.path.lexists(path):
        return None, 'STATE_MISSING'
    info = env.pn.file_info(path)
    if not info or info['attributes'] & (0x10 | 0x400) or not transaction.link_free(path, env.project):
        return None, 'STATE_UNSAFE'
    try:
        with open(path, 'rb') as fh:
            data = fh.read(MAX_STATE_BYTES + 1)
    except OSError:
        return None, 'STATE_UNREADABLE'
    if len(data) > MAX_STATE_BYTES:
        return None, 'STATE_TOO_LARGE'
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        return None, 'STATE_NOT_UTF8'
    return data, None


def _candidate(env, rid):
    """(candidate, None) từ evidence prepared+published hợp lệ của đúng rid, hoặc (None, lý do)."""
    ev = env.observer.load_evidence(env.project, rid)
    if not ev['available']:
        return None, 'EVIDENCE_MISSING'
    if ev['terminal'] != 'published' or not ev['consistent'] or ev['problems']:
        return None, 'EVIDENCE_INCONSISTENT' if ev['files'] else 'EVIDENCE_MISSING'
    prepared, published, raw_sha = ev['prepared'], ev['published'], ev['raw_published_sha256']
    if prepared is None or published is None or raw_sha is None:
        return None, 'EVIDENCE_INVALID'
    owner_pin = env.observer.entrypoint_sha256()
    if owner_pin is None or prepared['entrypoint_sha256'] != 'sha256:' + owner_pin:
        return None, 'EVIDENCE_OWNER_PIN_MISMATCH'
    try:
        task = prepared['task']
        path = task['effects']['actions'][0]['targets'][0]
        work_id = task['work_id']
    except (KeyError, IndexError, TypeError):
        return None, 'EVIDENCE_INVALID'
    if published['target'] != path or prepared['content'] != published['content'] or not isinstance(work_id, str):
        return None, 'EVIDENCE_TUPLE_MISMATCH'
    if not _path_ok(env.pn, path):
        return None, 'PATH_NOT_SUPPORTED'
    return {'rid': rid, 'path': path, 'name': path.rsplit('/', 1)[-1], 'work_id': work_id, 'at': prepared['at'],
            'digest': published['content']['sha256'], 'size': published['content']['size'], 'identity': published['identity'],
            'prepared_sha256': 'sha256:' + hashlib.sha256(env.pn.cj_dumps(prepared)).hexdigest(), 'published_sha256': raw_sha}, None


def _candidates(env):
    """(danh sách ứng viên hợp lệ, incomplete). Kiểm tối đa MAX_CANDIDATES bản mới nhất theo mtime file published (chỉ để chọn phần kiểm).

    owner.status vẫn đọc tên toàn bộ thư mục publish; giới hạn này không phải I/O bị chặn cứng.
    """
    safe = env.observer.observe(env.project, None)
    if not safe.get('available'):
        raise Unavailable(safe.get('reason') or 'RUNTIME_UNAVAILABLE')
    folder = os.path.join(env.project, *env.pn.PUBLISH_DIR)
    rows, incomplete = [], False
    try:
        with os.scandir(folder) as entries:
            for entry in entries:
                match = env.pn.FILE_RE.fullmatch(entry.name)
                if not match or match.group(2) != 'published.json':
                    continue
                try:
                    if not env.pn._is_regular(env.pn.file_info(entry.path)):
                        incomplete = True
                        continue
                    mtime = entry.stat(follow_symlinks=False).st_mtime
                except OSError:
                    incomplete = True
                    continue
                rows.append((mtime, match.group(1)))
    except FileNotFoundError:
        return [], False
    except OSError:
        return [], True
    rows.sort(reverse=True)
    out = []
    for _, rid in rows[:MAX_CANDIDATES]:
        cand, why = _candidate(env, rid)
        if cand is not None:
            out.append(cand)
        elif why != 'PATH_NOT_SUPPORTED':
            incomplete = True
    out.sort(key=lambda c: (c['at'], c['rid']), reverse=True)
    return out, incomplete or len(rows) > MAX_CANDIDATES


def _facts(env, path):
    return env.observer.observe(env.project, path)


def _judge(cand, obs):
    """(state, reason) của một bản so với bytes hiện tại. cand=None: không có evidence để so."""
    if not obs.get('available'):
        return 'unopenable', obs.get('reason') or 'OBSERVATION_UNAVAILABLE'
    t = obs.get('target')
    if not t or not obs.get('parents_link_free'):
        return 'unopenable', 'PARENT_UNSAFE'
    if not t.get('exists'):
        return 'unopenable', 'TARGET_MISSING'
    if not t.get('regular'):
        return 'unopenable', 'TARGET_NOT_REGULAR'
    if cand is None:
        return 'unverified', 'EVIDENCE_MISSING'
    same = t.get('sha256') == cand['digest'] and t.get('size') == cand['size'] and t.get('identity') == cand['identity']
    return ('matched', None) if same else ('changed', 'BYTES_OR_IDENTITY_CHANGED')


def _describe(env, cand, selected=False):
    state, reason = _judge(cand, _facts(env, cand['path']))
    return {'rid': cand['rid'], 'path': cand['path'], 'name': cand['name'], 'work_id': cand['work_id'], 'at': cand['at'],
            'state': state, 'reason': reason, 'selected': selected}


# ---------------------------------------------------------------- readiness (I3)
def readiness(project_root):
    """Điều kiện để luồng có kiểm soát (thẻ Nháp hiện tại, P-CN1/P-CTX1) chạy được bằng ĐÚNG interpreter đang chạy. Chỉ đọc: không cài, không ghi, không đổi Python.
    Trả {'usable', 'reason', 'python', 'version', 'jsonschema', 'fs'}; reason là mã đóng (PLATFORM_UNSUPPORTED, DEPENDENCY_MISSING, OWNER_*, CONTEXT_OWNER_PIN_MISMATCH,
    FS_UNSUPPORTED, PROJECT_INVALID, ROOT_UNSAFE...) hoặc None. Thiếu/sai ⇒ thẻ UNAVAILABLE, không có đường fallback bỏ pin. Chỉ thẻ này chịu điều kiện này.
    Conditions for the controlled flow with the exact interpreter that is running. Read only: installs nothing, writes nothing."""
    out = {'usable': False, 'reason': None, 'python': sys.executable, 'version': sys.version.split()[0], 'jsonschema': None, 'fs': None}
    try:
        import importlib.metadata
        out['jsonschema'] = importlib.metadata.version('jsonschema')
    except Exception:
        out['jsonschema'] = None
    if os.name != 'nt':
        out['reason'] = 'PLATFORM_UNSUPPORTED'
        return out
    try:
        env = Env(project_root)  # owner P-CN1 đúng pin + dependency của loader; thiếu jsonschema ⇒ DEPENDENCY_MISSING
        env.loader.load_owners()
    except Unavailable as exc:
        out['reason'] = exc.reason
        return out
    except Exception as exc:
        out['reason'] = _unavailable_reason(exc)
        return out
    try:
        ok, vol = env.pn.volume_supported(env.project)
        out['fs'] = vol.get('fs')
        if not ok:
            out['reason'] = 'FS_UNSUPPORTED'
            return out
        env.ctx()  # owner P-CTX1 đúng pin trong policy / the P-CTX1 owner matches the policy pin
    except Unavailable as exc:
        out['reason'] = exc.reason
        return out
    except Exception:
        out['reason'] = 'OWNER_UNAVAILABLE'
        return out
    out['usable'] = True
    return out


# ---------------------------------------------------------------- API
def _res(result, message='', changes=False, **extra):
    out = make(STATUS[result], code=EXIT[result], message=message, changes=changes, **extra)
    out['result'] = result
    return out


def _unavailable(exc):
    return _res('UNAVAILABLE', L('Chưa đối chiếu được: thành phần kiểm không dùng được; chưa làm gì. [%s]', 'Cannot compare: the check component is unusable; nothing done. [%s]') % exc.reason,
                False, reason=exc.reason)


def _rid_ok(rid):
    return type(rid) is str and bool(re.fullmatch(r'[0-9a-f]{32}', rid))


def status(project_root):
    """Thẻ Nháp hiện tại: con trỏ, bản đã chọn và tối đa HISTORY_SHOWN bản liên quan cùng work_id. Chỉ đọc."""
    try:
        env = Env(project_root)
        raw, bad = _read_state(env)
        out = {'pointer': {'state': 'UNRESOLVED', 'reason': bad, 'tuple': None}, 'selected': None, 'history': [], 'more': 0, 'incomplete': False}
        if raw is not None:
            ptr = parse_pointer(env.pn, raw.decode('utf-8'))
            out['pointer'] = {'state': ptr['state'], 'reason': ptr['reason'], 'tuple': ptr['tuple']}
            out['state_sha256'] = 'sha256:' + hashlib.sha256(raw).hexdigest()
            if ptr['state'] == 'SET':
                tup = ptr['tuple']
                cand, why = _candidate(env, tup['rid'])
                if cand is not None and (cand['path'], cand['digest']) != (tup['path'], tup['digest']):
                    cand, why = None, 'POINTER_EVIDENCE_MISMATCH'
                obs = _facts(env, tup['path'])
                state, reason = _judge(cand, obs)
                if cand is None and state == 'unverified':
                    reason = why
                out['selected'] = {'rid': tup['rid'], 'path': tup['path'], 'name': tup['path'].rsplit('/', 1)[-1], 'digest': tup['digest'],
                                   'work_id': cand['work_id'] if cand else None, 'at': cand['at'] if cand else None, 'state': state, 'reason': reason}
                if cand is not None and state in ('matched', 'changed'):
                    cands, out['incomplete'] = _candidates(env)
                    related = [c for c in cands if c['work_id'] == cand['work_id'] and c['rid'] != tup['rid']]
                    out['more'] = max(0, len(related) - HISTORY_SHOWN)
                    out['history'] = [_describe(env, c) for c in related[:HISTORY_SHOWN]]
        return _res('OK', '', False, **out)
    except Unavailable as exc:
        return _unavailable(exc)


def list_candidates(project_root):
    """Các bản có evidence published hợp lệ để chọn (mới nhất trước). Không so bytes hiện tại: việc đó thuộc preview của select."""
    try:
        env = Env(project_root)
        cands, incomplete = _candidates(env)
        raw, _ = _read_state(env)
        ptr = parse_pointer(env.pn, raw.decode('utf-8')) if raw is not None else {'state': 'UNRESOLVED', 'tuple': None}
        sel = ptr['tuple']['rid'] if ptr['state'] == 'SET' else None
        items = [{'rid': c['rid'], 'path': c['path'], 'name': c['name'], 'work_id': c['work_id'], 'at': c['at'], 'size': c['size'],
                  'selected': c['rid'] == sel} for c in cands]
        return _res('OK', '', False, items=items, incomplete=incomplete, pointer_state=ptr['state'])
    except Unavailable as exc:
        return _unavailable(exc)


def _fingerprint(cand, target):
    """SHA256 của snapshot ổn định: tuple + hash bytes prepared/published + bytes/size/identity của đích. Không có thời gian quan sát; chỉ chuỗi nên không mất độ chính xác khi qua JavaScript."""
    snap = {'v': 'law-current-draft-select/1', 'path': cand['path'], 'rid': cand['rid'], 'digest': cand['digest'],
            'prepared_sha256': cand['prepared_sha256'], 'published_sha256': cand['published_sha256'],
            'target': {'sha256': target['sha256'], 'size': target['size'], 'volume_serial': target['identity']['volume_serial'],
                       'file_index': target['identity']['file_index']}}
    return hashlib.sha256(json.dumps(snap, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii')).hexdigest()


def _plan_selection(env, rid):
    """(kế hoạch, None) hoặc (None, kết quả lỗi). Cùng một đường cho preview và apply; không ghi gì."""
    cand, why = _candidate(env, rid)
    if cand is None:
        return None, _res('ERROR', L('Bản này không có bằng chứng xuất bản hợp lệ để chọn. [%s]', 'This revision has no valid publish evidence to select. [%s]') % why, False, reason=why)
    obs = _facts(env, cand['path'])
    state, reason = _judge(cand, obs)
    if state != 'matched':
        return None, _res('ERROR', L('Bản này không còn khớp bản đã ghi nhận nên chưa chọn. [%s]', 'This revision no longer matches what was recorded, so it is not selected. [%s]') % (reason or state),
                          False, reason='TARGET_NOT_MATCHING', draft_state=state)
    raw, bad = _read_state(env)
    if raw is None:
        return None, _res('ERROR', L('Không đọc được STATE. [%s]', 'Cannot read STATE. [%s]') % bad, False, reason=bad)
    text = raw.decode('utf-8')
    ptr = parse_pointer(env.pn, text)
    if ptr['state'] == 'UNRESOLVED':
        return None, _res('ERROR', L('Con trỏ trong STATE chưa rõ [%s]; nhờ agent sửa STATE theo quyền đã cấp qua tools/context_update.py, công cụ này không tự sửa.',
                                     'The pointer in STATE is unresolved [%s]; ask the agent to fix STATE through tools/context_update.py under its grant; this tool does not repair it.') % ptr['reason'],
                          False, reason='POINTER_UNRESOLVED', detail=ptr['reason'])
    tup = {'path': cand['path'], 'rid': cand['rid'], 'digest': cand['digest']}
    try:
        new = with_marker(env.pn, text, tup).encode('utf-8')
    except ValueError as exc:
        return None, _res('ERROR', L('Không dựng được marker trong STATE. [%s]', 'Cannot build the marker in STATE. [%s]') % exc, False, reason=str(exc))
    return {'cand': cand, 'tuple': tup, 'state_bytes': raw, 'new_bytes': new, 'state_sha256': hashlib.sha256(raw).hexdigest(),
            'fingerprint': _fingerprint(cand, obs['target']), 'already': ptr['state'] == 'SET' and ptr['tuple'] == tup}, None


def select_preview(project_root, rid):
    """Xem trước chọn bản `rid`: chỉ đọc. Trả tuple, SHA256 STATE đã đọc và selection_fingerprint để apply bắt buộc mang theo."""
    try:
        if not _rid_ok(rid):
            return _res('ERROR', L('Mã bản không hợp lệ.', 'Invalid revision id.'), False, reason='RID_INVALID')
        env = Env(project_root)
        plan, err = _plan_selection(env, rid)
        if err:
            return err
        r = env.ctx().preview(env.project, 'state', plan['new_bytes'], expected_before=plan['state_sha256'])
        common = {'selection': plan['tuple'], 'state_sha256': plan['state_sha256'], 'selection_fingerprint': plan['fingerprint'],
                  'work_id': plan['cand']['work_id'], 'name': plan['cand']['name'], 'mode': 'PREVIEW'}
        if r['result'] == 'PREVIEW':
            return _res('PREVIEW', L('Xem trước: sẽ đặt bản này làm Nháp hiện tại bằng một marker trong STATE; chưa ghi gì.',
                                     'Preview: this revision would become the current draft with one marker in STATE; nothing written.'),
                        False, planned_changes=r['planned_changes'], next_actions=[L('Áp dụng bằng --apply kèm hash đã nêu.', 'Apply with --apply and the hashes above.')],
                        reason=None, **common)
        if r['result'] == 'UNCHANGED':
            return _res('UNCHANGED', L('Bản này đã là Nháp hiện tại; chưa ghi gì.', 'This revision is already the current draft; nothing written.'), False, reason=None, **common)
        return _res(r['result'] if r['result'] in ('CONFLICT', 'ERROR', 'UNKNOWN') else 'ERROR', r['message'], False, reason=r.get('reason'), **common)
    except Unavailable as exc:
        return _unavailable(exc)


def select_apply(project_root, rid, expected_state, expected_selection):
    """Chọn bản `rid`: đọc lại toàn bộ snapshot, khác preview thì CONFLICT; ghi đúng một marker qua P-CTX1.update. Trạng thái ghi lấy nguyên từ P-CTX1."""
    try:
        if not _rid_ok(rid):
            return _res('ERROR', L('Mã bản không hợp lệ.', 'Invalid revision id.'), False, reason='RID_INVALID')
        m = HEX_ARG.match(expected_state) if type(expected_state) is str else None
        if not m or type(expected_selection) is not str or not HEX64.match(expected_selection):
            return _res('ERROR', L('Cần hash STATE và selection_fingerprint của bản xem trước.', 'The STATE hash and selection_fingerprint from the preview are required.'),
                        False, reason='EXPECTED_INVALID')
        expected_state = m.group(1)
        env = Env(project_root)
        with _apply_lock:
            plan, err = _plan_selection(env, rid)
            if err:
                return err
            if plan['fingerprint'] != expected_selection:
                return _res('CONFLICT', L('Bản, bằng chứng hoặc file đã đổi sau lần xem trước; chưa ghi gì. Xem trước lại.',
                                          'The revision, its evidence or the file changed after the preview; nothing written. Preview again.'),
                            False, reason='SELECTION_CHANGED')
            if plan['state_sha256'] != expected_state:
                return _res('CONFLICT', L('STATE đã đổi sau lần xem trước; chưa ghi gì. Xem trước lại.', 'STATE changed after the preview; nothing written. Preview again.'),
                            False, reason='STATE_CHANGED')
            r = env.ctx().update(env.project, 'state', plan['new_bytes'], expected_before=expected_state)
        r = dict(r)
        r['selection'] = plan['tuple']
        r['selection_fingerprint'] = plan['fingerprint']
        return r
    except Unavailable as exc:
        return _unavailable(exc)


def _startfile(path):
    log = os.environ.get(OPEN_LOG_ENV)  # TEST ONLY: ghi đường dẫn vào file thay vì mở ứng dụng / records the path instead of launching an app
    if log:
        with open(log, 'a', encoding='utf-8') as fh:
            fh.write(path + '\n')
        return
    os.startfile(path)  # noqa  (chỉ Windows / Windows only; owner đã từ chối nơi khác)


def open_draft(project_root, rid, ack=None):
    """Mở một bản bằng ứng dụng liên kết. Quan sát lại mỗi lần; không tin payload hay trạng thái cũ. Không ghi gì.

    matched mở ngay. changed/unverified (bytes đổi, hoặc thiếu evidence nhưng file an toàn) chỉ mở khi `ack` đúng trạng thái vừa quan sát.
    Owner/pin không dùng được, liên kết, ngoài phạm vi, thiếu file, đuôi lạ ⇒ từ chối, không dùng opener chung. Không hứa Office mở chỉ-đọc hay chống sửa.
    """
    try:
        if not _rid_ok(rid):
            return _res('ERROR', L('Mã bản không hợp lệ.', 'Invalid revision id.'), False, reason='RID_INVALID')
        env = Env(project_root)
        cand, why = _candidate(env, rid)
        path, pointer_mismatch = None, False
        raw, _ = _read_state(env)
        ptr = parse_pointer(env.pn, raw.decode('utf-8')) if raw is not None else {'state': 'UNRESOLVED', 'tuple': None}
        pointed = ptr['tuple'] if ptr['state'] == 'SET' and ptr['tuple']['rid'] == rid else None
        if pointed is not None:
            path = pointed['path']
            pointer_mismatch = cand is not None and (pointed['path'], pointed['digest']) != (cand['path'], cand['digest'])
            if pointer_mismatch:
                cand = None  # keep the file shown by the card; conflicting evidence never redirects an open
        elif cand is not None:
            path = cand['path']
        if path is None:
            return _res('REFUSED', L('Không xác định được file của bản này; không mở. [%s]', 'The file of this revision cannot be determined; not opened. [%s]') % why, False, reason='UNKNOWN_DRAFT')
        if not _path_ok(env.pn, path):
            return _res('REFUSED', L('Đường dẫn hoặc loại file không được mở trong luồng này; không mở.', 'This path or file type may not be opened here; not opened.'), False, reason='PATH_NOT_SUPPORTED')
        state, reason = _judge(cand, _facts(env, path))
        if state == 'unverified':
            reason = 'POINTER_EVIDENCE_MISMATCH' if pointer_mismatch else why
        if state == 'unopenable':
            return _res('REFUSED', L('Không mở được file này (liên kết, ngoài phạm vi, thiếu hoặc không quan sát được); không mở. [%s]',
                                     'This file cannot be opened (link, outside scope, missing or unobservable); not opened. [%s]') % reason, False, reason=reason, draft_state=state)
        if state != 'matched' and ack != state:
            return _res('ACK_REQUIRED', L('File không còn khớp bản đã ghi nhận hoặc chưa đối chiếu được; chỉ mở khi bạn chọn mở kèm cảnh báo.',
                                          'The file no longer matches what was recorded or cannot be compared; it opens only if you choose to open it with the warning.'),
                        False, reason=reason, draft_state=state)
        if os.name != 'nt':
            return _res('REFUSED', L('Chỉ hỗ trợ Windows.', 'Windows only.'), False, reason='UNSUPPORTED_FS', draft_state=state)
        _startfile(os.path.join(env.project, *path.split('/')))
        return _res('OPENED', L('Đã gửi lệnh mở file bằng ứng dụng liên kết.', 'Asked the associated application to open the file.'), False,
                    reason=reason, draft_state=state, path=path)
    except Unavailable as exc:
        return _unavailable(exc)
    except OSError:
        return _res('ERROR', L('Hệ điều hành không mở được file.', 'The operating system could not open the file.'), False, reason='OPEN_FAILED')


# ---------------------------------------------------------------- CLI
def _human(res):
    print(res['message'])
    for k in ('reason',):
        if res.get(k):
            print('  %s: %s' % (k, res[k]))
    if res.get('selected'):
        s = res['selected']
        print('  Nháp hiện tại / current: %s  [%s]  rid=%s' % (s['path'], s['state'], s['rid']))
    for h in res.get('history') or []:
        print('  - %s  [%s]  rid=%s  %s' % (h['path'], h['state'], h['rid'], h['at']))
    for it in res.get('items') or []:
        print('  %s%s  rid=%s  work=%s  %s' % ('* ' if it['selected'] else '  ', it['path'], it['rid'], it['work_id'], it['at']))
    if res.get('selection_fingerprint'):
        print('  expected-state: %s' % res.get('state_sha256'))
        print('  expected-selection: %s' % res['selection_fingerprint'])
    for n in res.get('next_actions') or []:
        print('  ' + n)


def _cli(argv):
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['status', 'list', 'select', 'open'])
    ap.add_argument('--project', default=CODE_ROOT)
    ap.add_argument('--rid')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--expected-state')
    ap.add_argument('--expected-selection')
    ap.add_argument('--ack', choices=['changed', 'unverified'])
    ap.add_argument('--result-json', action='store_true')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    a = ap.parse_args(argv)
    LANG = a.lang
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    if a.cmd in ('select', 'open') and not a.rid:
        ap.error('--rid is required')
    if a.cmd == 'select' and a.apply and not (a.expected_state and a.expected_selection):
        ap.error('--apply needs --rid, --expected-state and --expected-selection')
    if a.cmd == 'status':
        res = status(a.project)
    elif a.cmd == 'list':
        res = list_candidates(a.project)
    elif a.cmd == 'select':
        res = select_apply(a.project, a.rid, a.expected_state, a.expected_selection) if a.apply else select_preview(a.project, a.rid)
    else:
        res = open_draft(a.project, a.rid, a.ack)
    if a.result_json:
        emit(res)
    else:
        _human(res)
    return res['code']


if __name__ == '__main__':
    sys.exit(_cli(sys.argv[1:]))
