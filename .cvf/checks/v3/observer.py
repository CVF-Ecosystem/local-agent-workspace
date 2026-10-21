"""Observer S4 hẹp, CHỈ ĐỌC, cho luồng P-CN1 một file / narrow read-only observer for the one-file P-CN1 flow.

Chỉ nạp khi người gọi đưa root tường minh. Mỏng: gọi lại `observe`/`validate_evidence` của `tools/publish_new.py` (owner đã nhận) và đọc raw evidence
của đúng một rid dưới đường publish cố định. Không gọi publish/recover/discard_staged, không mkdir, không ghi, không fetch locator/URL.
Code owner luôn được nạp từ cây nguồn LAW cố định (từ vị trí file này), không bao giờ từ root: root chỉ là dữ liệu.
Mọi lỗi/thiếu quan sát trả `available=False` với mã đóng; KHÔNG BAO GIỜ được hiểu là "đích vắng". Không echo thông điệp ngoại lệ hay đường dẫn.
Loaded only when an explicit root is given. Observations are at-time facts (EXCLUSIVE_WRITE_NOT_PROVEN, RACE_NOT_EXCLUDED, tamper_resistance NONE).
"""
import copy
import hashlib
import importlib.util
import os
import sys
from pathlib import Path

from .loader import load_owners, parse_json_bytes

OWNER_REL = ('tools', 'publish_new.py')
OWNER_MODULE = 'law_cvf_check_v3_owner_publish_new'
UNAVAILABLE = 'OBSERVATION_UNAVAILABLE'
_FILE_ATTRIBUTE_DIRECTORY = 0x10
_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
_cache = {}


def owner_path():
    """Đường cố định của owner trong cây nguồn LAW: `.cvf/checks/v3/observer.py` lên ba cấp."""
    return Path(__file__).resolve().parents[3].joinpath(*OWNER_REL)


def load_owner():
    """Nạp đúng bytes đã so pin từ source LAW; dependency trùng tên ở host không được dùng thay owner."""
    path = owner_path()
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    protocols = [p for p in parse_json_bytes(load_owners().policy_bytes).get('owner_protocols', [])
                 if (p.get('protocol_id'), p.get('protocol_version'), p.get('entrypoint')) ==
                 ('P-CN1', 1, 'tools/publish_new.py')]
    if len(protocols) != 1 or protocols[0].get('entrypoint_sha256') != 'sha256:' + digest:
        raise ImportError('owner entrypoint bytes do not match the fixed policy pin')
    for name in ('result_schema', 'transaction'):
        dependency = sys.modules.get(name)
        if dependency is not None:
            origin = getattr(dependency, '__file__', None)
            if not isinstance(origin, str) or Path(origin).resolve() != (path.parent / (name + '.py')).resolve():
                raise ImportError('owner dependency origin is not the fixed LAW source')
    mod = _cache.get('owner')
    if mod is not None and _cache.get('owner_sha256') == digest:
        return mod
    before = list(sys.path)
    spec = importlib.util.spec_from_file_location(OWNER_MODULE, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[OWNER_MODULE] = mod
    try:
        # Execute the bytes that were hashed, without a second source read or a cached pyc.
        exec(compile(raw, str(path), 'exec'), mod.__dict__)
    except BaseException:
        sys.modules.pop(OWNER_MODULE, None)
        raise
    finally:
        sys.path[:] = before
    _cache['owner'] = mod
    _cache['owner_sha256'] = digest
    return mod


def entrypoint_sha256():
    """SHA-256 hex của chính bytes đã nạp và còn khớp pin hiện hành, hoặc None."""
    try:
        load_owner()
    except Exception:
        return None
    return _cache.get('owner_sha256')


def _safe(fn):
    try:
        return fn()
    except Exception:  # an owner failure is an unavailable observation, never evidence of absence; the message is never echoed
        return None


def rebuild_task(task, rid):
    """Dựng lại task bằng hàm thuần của owner: `build_task(request_from_task(task), rid)`; không gọi hàm ghi nào.

    Trả (trạng thái, task dựng lại): `OK`; `UNAVAILABLE` nếu không nạp được owner đúng pin; `UNREPRESENTABLE` nếu owner từ chối request dựng lại
    từ các trường nó hỗ trợ (task có trường owner không sinh ra được thì kết quả khác task gốc: so bằng projection C1 ở workflow, không ở đây).
    """
    owner = _safe(load_owner)
    if owner is None:
        return 'UNAVAILABLE', None
    try:
        return 'OK', owner.build_task(owner.request_from_task(copy.deepcopy(task)), rid)
    except Exception:  # RequestError, missing fields, canonical-domain errors: the owner cannot express this task; never echoed
        return 'UNREPRESENTABLE', None


def observe(root, target, inputs=(), rid=None):
    """Một lần quan sát tại thời điểm. Trả dict: available, reason, volume_ok, parents_link_free, target, inputs, evidence.

    available chỉ true khi owner trả OBSERVED (NTFS local, runtime/cha không bị link). `target` có `exists`, `regular`, `identity`, `sha256`, `size`.
    `runtime_parents_ready`: True/False theo precondition của owner (`.agent` và `.agent/runtime` có sẵn, thư mục thường), None nếu không quan sát được.
    """
    out = {'available': False, 'reason': UNAVAILABLE, 'parents_link_free': None, 'runtime_parents_ready': None, 'target': None, 'inputs': [],
           'evidence': None}
    owner = _safe(load_owner)
    if owner is None:
        return out
    # The owner's own request_id mode reports a missing prepared file as EVIDENCE_INCONSISTENT; before publish that is normal, so evidence is read separately.
    res = _safe(lambda: owner.observe(root, target=target, inputs=list(inputs) or None))
    if not isinstance(res, dict):
        return out
    out['parents_link_free'] = res.get('parents_link_free')
    out['runtime_parents_ready'] = res.get('runtime_parents_ready') if isinstance(res.get('runtime_parents_ready'), bool) else None
    out['target'] = res.get('target')
    out['inputs'] = list(res.get('inputs') or [])
    if res.get('outcome') == 'OBSERVED':
        out['available'] = True
        out['reason'] = None
    else:
        reason = res.get('reason')
        out['reason'] = reason if isinstance(reason, str) and reason.isupper() and len(reason) <= 40 else UNAVAILABLE
    if rid is not None and out['available']:
        status = _safe(lambda: owner.status(root, rid))
        items = status.get('items') if isinstance(status, dict) and status.get('outcome') == 'STATUS' else None
        if items:
            out['evidence'] = items[0]
        else:
            out['available'], out['reason'] = False, UNAVAILABLE  # runtime evidence state could not be read: not "no evidence"
    return out


def _read_regular(owner, path):
    """Đọc có giới hạn một file thường (không link/reparse); None nếu không đọc được."""
    info = _safe(lambda: owner.file_info(path))
    if not info or info['attributes'] & (_FILE_ATTRIBUTE_DIRECTORY | _FILE_ATTRIBUTE_REPARSE_POINT):
        return None
    try:
        with open(path, 'rb') as fh:
            data = fh.read(owner.MAX_JSON_BYTES + 1)
    except OSError:
        return None
    return data if len(data) <= owner.MAX_JSON_BYTES else None


def load_evidence(root, rid):
    """Đọc evidence prepared/published của đúng rid, chỉ sau khi `observe` xác nhận runtime không bị link.

    Trả {available, reason, files, terminal, consistent, problems, prepared, published, raw_published_sha256}. Evidence không hợp lệ (không phải
    LAW-CJ/2 canonical của đúng state/rid) ⇒ None theo `validate_evidence`, không sửa hộ.
    """
    out = {'available': False, 'reason': UNAVAILABLE, 'files': [], 'terminal': None, 'consistent': False, 'problems': [],
           'prepared': None, 'published': None, 'raw_published_sha256': None}
    owner = _safe(load_owner)
    if owner is None:
        return out
    status = _safe(lambda: owner.status(root, rid))
    if not isinstance(status, dict) or status.get('outcome') != 'STATUS' or not status.get('items'):
        out['reason'] = (status or {}).get('reason') if isinstance(status, dict) and isinstance((status or {}).get('reason'), str) else UNAVAILABLE
        return out
    item = status['items'][0]
    out.update(available=True, reason=None, files=list(item.get('files') or []), terminal=item.get('terminal'),
               consistent=bool(item.get('consistent')), problems=list(item.get('problems') or []))
    folder = os.path.join(os.path.abspath(root), *owner.PUBLISH_DIR)
    if 'prepared.json' in out['files']:
        raw = _read_regular(owner, os.path.join(folder, rid + '.prepared.json'))
        out['prepared'] = owner.validate_evidence(raw, rid, 'prepared') if raw else None
    if 'published.json' in out['files']:
        raw = _read_regular(owner, os.path.join(folder, rid + '.published.json'))
        out['published'] = owner.validate_evidence(raw, rid, 'published') if raw else None
        if raw:
            out['raw_published_sha256'] = 'sha256:' + hashlib.sha256(raw).hexdigest()
    return out
