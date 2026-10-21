#!/usr/bin/env python3
"""Tạo một file nháp mới, không bao giờ ghi đè (protocol P-CN1, prototype). / Publish one new draft file, never overwrite.

Dùng / Usage:
  python tools/publish_new.py publish --request <request.json> --staged <file> [--rid <rid>] [--project DIR] [--result-json]
  python tools/publish_new.py observe --target <rel> [--input <rel> ...] [--rid <rid>] [--project DIR] [--result-json]
  python tools/publish_new.py status [<rid>] [--project DIR] [--result-json]
  python tools/publish_new.py recover <rid> [--project DIR] [--result-json]
  python tools/publish_new.py discard-staged <rid> [--project DIR] [--result-json]

Mã thoát / exit codes: 0 PUBLISHED/OBSERVED/STATUS/NO_ACTION/DISCARDED; 3 CONFLICT; 4 REFUSED/UNSUPPORTED;
5 ABANDONED/UNKNOWN/PUBLISHED_EVIDENCE_PENDING; 6 BUSY; 2 usage error.

Contract: roadmap/G02_C2_S3_D0_AMENDMENT_PACKET_2026-10-18.md section 4.3.3 (source repository only).
Windows + local NTFS only; anything else is UNSUPPORTED_FS and nothing is written. The tool records physical facts only:
it does not check grants, run a checker or accept anything on the user's behalf. Evidence is cooperative (ADVISORY):
whoever can write .agent/runtime/ can change it.

Revision P-CN1 v1 (caller request_id, runtime bootstrap precondition): the caller may choose the request id (--rid / request_id=, 32 lowercase
hex) so one task snapshot (task_id pcn1-<rid>) can be planned, checked, published and accepted; without it a UUID is generated as before. A rid
that already has any file under .agent/runtime/publish is RID_TAKEN and nothing of it is overwritten or deleted. `.agent` and `.agent/runtime`
must already exist as plain folders (REFUSED RUNTIME_PARENT_MISSING otherwise, nothing created); only the `publish` folder is created here.

TEST ONLY / CHỈ DÙNG KIỂM THỬ: LOCAL_AGENT_WORKSPACE_TEST_FAULT=pcn1-kill:<point> (os._exit(70)) or pcn1-fail:<point>
(raise OSError). kill points: after_prepared, after_stage, after_link, after_verify, after_published.
fail points: prepared_write, stage_write, published_write, terminal_write, cleanup. Never set this in real use.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import re
import sys
import unicodedata
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transaction  # noqa: E402  (helpers only: link_free, Pins; no Transaction/journal)
from result_schema import emit, make  # noqa: E402

SCHEMA = 'local-agent-workspace/publish-v1'
PROTOCOL = 'P-CN1'
PROTOCOL_VERSION = 1
PLATFORM = 'windows-ntfs-local'
TASK_SCHEMA_VERSION = 'law.cvf.control/3'  # candidate only: not valid under the active v2 schema (const /2)
TOOL_NAME = 'publish_new'
MAX_STAGED_BYTES = 104857600
MAX_JSON_BYTES = 1048576
LOCK_OFFSET = 1073741824  # 2**30: above MAX_JSON_BYTES, below 2**31
LOCK_LEN = 1
INT_LIMIT = 2 ** 53 - 1
RUNTIME_PARENTS = ('.agent', 'runtime')  # must exist before publish; the tool creates only the folder below them
PUBLISH_DIR = RUNTIME_PARENTS + ('publish',)
RID_FILE_STATES = ('prepared', 'published', 'conflict', 'abandoned', 'unknown', 'staged')
TERMINALS = ('published', 'conflict', 'abandoned', 'unknown')
FAULT_ENV = 'LOCAL_AGENT_WORKSPACE_TEST_FAULT'
_HOOK = None  # TEST ONLY: _HOOK(point, info) called at named points inside publish/recover

RID_RE = re.compile(r'^[0-9a-f]{32}$')
ID_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
DIGEST_RE = re.compile(r'^sha256:[0-9a-f]{64}$')
KEY_RE = re.compile(r'^[A-Za-z0-9_.-]{1,64}$')
SHORT_NAME_RE = re.compile(r'~[0-9]')
FILE_RE = re.compile(r'^([0-9a-f]{32})\.(prepared\.json|published\.json|conflict\.json|abandoned\.json|unknown\.json|staged)$')
DEVICE_NAMES = {'con', 'prn', 'aux', 'nul', 'conin$', 'conout$'} | {'com%d' % i for i in range(10)} | {'lpt%d' % i for i in range(10)}
AUTHORITY_PATTERNS = ('agents.md', 'project.md', 'claude.md', 'gemini.md', 'routing_policy*.json', '*.schema.json',
                      'control_rules*.md', 'control_contract*.md', 'execution_profile*.json', 'skill.md', 'pack.json',
                      'manifest.sha256', '*.grant.json', 'grant*.json')
ROLES = {'user', 'main', 'scout', 'worker', 'reviewer', 'domain_role', 'host', 'tool', 'issuer', 'unknown'}
SOURCE_CLASSES = {'USER_CONFIRMATION', 'MAIN_PROPOSAL', 'ROLE_REPORT', 'TOOL_OBSERVATION', 'UNVERIFIED'}
CHANNELS = {'USER_MESSAGE', 'HOST_CONFIRMATION_UI', 'USER_AUTHORED_FILE', 'TOOL_OUTPUT', 'ROLE_OUTPUT', 'MAIN_AUTHORED', 'NONE'}
EXIT = {'PUBLISHED': 0, 'OBSERVED': 0, 'STATUS': 0, 'NO_ACTION': 0, 'DISCARDED': 0, 'CONFLICT': 3, 'REFUSED': 4,
        'UNSUPPORTED': 4, 'ABANDONED': 5, 'UNKNOWN': 5, 'PUBLISHED_EVIDENCE_PENDING': 5, 'BUSY': 6}


# ---------------------------------------------------------------- LAW-CJ/2 (private serializer, C1 4.1)
class CJError(ValueError):
    def __init__(self, reason):
        ValueError.__init__(self, reason)
        self.reason = reason


def _cj_check_str(s):
    for ch in s:
        if 0xD800 <= ord(ch) <= 0xDFFF:
            raise CJError('LONE_SURROGATE')
    if unicodedata.normalize('NFC', s) != s:
        raise CJError('NON_NFC_STRING')


def _cj_str(s):
    _cj_check_str(s)
    out = ['"']
    for ch in s:
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        elif ch == '\b':
            out.append('\\b')
        elif ch == '\t':
            out.append('\\t')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\f':
            out.append('\\f')
        elif ch == '\r':
            out.append('\\r')
        elif o < 0x20:
            out.append('\\u%04x' % o)
        else:
            out.append(ch)
    out.append('"')
    return ''.join(out)


def _cj(value):
    if value is None:
        return 'null'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if isinstance(value, int):
        if value > INT_LIMIT or value < -INT_LIMIT:
            raise CJError('INTEGER_OUT_OF_RANGE')
        return str(value)
    if isinstance(value, float):
        raise CJError('NON_INTEGER_NUMBER')
    if isinstance(value, str):
        return _cj_str(value)
    if isinstance(value, (list, tuple)):
        return '[' + ','.join(_cj(v) for v in value) + ']'
    if isinstance(value, dict):
        parts = []
        for k in sorted(value, key=lambda key: key.encode('utf-8') if isinstance(key, str) else b''):
            if not isinstance(k, str) or not KEY_RE.fullmatch(k):
                raise CJError('KEY_NOT_ALLOWED')
            parts.append(_cj_str(k) + ':' + _cj(value[k]))
        return '{' + ','.join(parts) + '}'
    raise CJError('UNSUPPORTED_TYPE')


def cj_dumps(value):
    """LAW-CJ/2 canonical UTF-8 bytes; raises CJError instead of normalising."""
    return _cj(value).encode('utf-8')


def _pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise CJError('DUPLICATE_KEY')
        out[k] = v
    return out


def _bad_float(_):
    raise CJError('NON_INTEGER_NUMBER')


def _bad_const(_):
    raise CJError('NON_FINITE_NUMBER')


def _int(text):
    n = int(text)
    if n > INT_LIMIT or n < -INT_LIMIT:
        raise CJError('INTEGER_OUT_OF_RANGE')
    return n


def cj_loads(data):
    """Strict parse (no duplicate keys, integers only, NFC, no lone surrogate, allowed keys). Does not require canonical form."""
    if isinstance(data, bytes):
        if data.startswith(b'\xef\xbb\xbf'):
            raise CJError('BOM')
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            raise CJError('NOT_UTF8')
    try:
        value = json.loads(data, object_pairs_hook=_pairs, parse_float=_bad_float, parse_int=_int, parse_constant=_bad_const)
    except CJError:
        raise
    except ValueError:
        raise CJError('NOT_JSON')
    _cj(value)  # walks every string and key: NFC, surrogates, key pattern, integer range
    return value


def cj_digest(value):
    return 'sha256:' + hashlib.sha256(cj_dumps(value)).hexdigest()


# ---------------------------------------------------------------- small helpers
def _sha_bytes(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def _sha_file(path):
    h = hashlib.sha256()
    size = 0
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    return 'sha256:' + h.hexdigest(), size


def _now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def _abs(project, rel):
    return os.path.join(project, *rel.split('/'))


def _rel(project, path):
    return os.path.relpath(path, project).replace(os.sep, '/')


def _fault(kind):
    spec = os.environ.get(FAULT_ENV, '')
    return spec.partition(':')[2] if spec.startswith(kind + ':') else None


def _kill_point(point):
    if _fault('pcn1-kill') == point:
        os._exit(70)


def _fail_point(point):
    if _fault('pcn1-fail') == point:
        raise OSError('synthetic fault: ' + point)


def _hook(point, info=None):
    if _HOOK is not None:
        _HOOK(point, info)


def entrypoint_sha256():
    with open(os.path.abspath(__file__), 'rb') as f:
        return _sha_bytes(f.read())


def _result(outcome, reason=None, request_id=None, wrote=None, **extra):
    out = {'outcome': outcome, 'reason': reason, 'request_id': request_id, 'wrote': list(wrote or [])}
    out.update(extra)
    return out


# ---------------------------------------------------------------- Windows adapter (volume, identity, attributes)
_FILE_ATTRIBUTE_DIRECTORY = 0x10
_FILE_ATTRIBUTE_REPARSE_POINT = 0x400
_FILE_ATTRIBUTE_OFFLINE = 0x1000
_CLOUD_ATTRIBUTES = 0x1000 | 0x40000 | 0x80000 | 0x100000 | 0x400000  # offline, recall-on-open, pinned, unpinned, recall-on-data-access
_k32 = None


def _kernel32():
    global _k32
    if _k32 is None:
        import ctypes
        from ctypes import wintypes

        class BHFI(ctypes.Structure):
            _fields_ = [('dwFileAttributes', wintypes.DWORD), ('ftCreationTime', wintypes.FILETIME),
                        ('ftLastAccessTime', wintypes.FILETIME), ('ftLastWriteTime', wintypes.FILETIME),
                        ('dwVolumeSerialNumber', wintypes.DWORD), ('nFileSizeHigh', wintypes.DWORD),
                        ('nFileSizeLow', wintypes.DWORD), ('nNumberOfLinks', wintypes.DWORD),
                        ('nFileIndexHigh', wintypes.DWORD), ('nFileIndexLow', wintypes.DWORD)]
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        k.CreateFileW.restype = wintypes.HANDLE
        k.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                  wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        k.CloseHandle.argtypes = [wintypes.HANDLE]
        k.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(BHFI)]
        k.GetFileInformationByHandle.restype = wintypes.BOOL
        k.GetVolumePathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        k.GetVolumePathNameW.restype = wintypes.BOOL
        k.GetVolumeInformationW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                            ctypes.POINTER(wintypes.DWORD), ctypes.POINTER(wintypes.DWORD),
                                            wintypes.LPWSTR, wintypes.DWORD]
        k.GetVolumeInformationW.restype = wintypes.BOOL
        k.GetDriveTypeW.argtypes = [wintypes.LPCWSTR]
        k.GetDriveTypeW.restype = wintypes.UINT
        k.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
        k.GetFileAttributesW.restype = wintypes.DWORD
        k.SetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
        k.SetFileInformationByHandle.restype = wintypes.BOOL
        k._BHFI = BHFI
        _k32 = k
    return _k32


def _info_from_handle(h):
    import ctypes
    k = _kernel32()
    info = k._BHFI()
    if not k.GetFileInformationByHandle(h, ctypes.byref(info)):
        return None
    index = (int(info.nFileIndexHigh) << 32) | int(info.nFileIndexLow)
    return {'attributes': int(info.dwFileAttributes), 'nlink': int(info.nNumberOfLinks),
            'size': (int(info.nFileSizeHigh) << 32) | int(info.nFileSizeLow),
            'volume_serial': '%08x' % int(info.dwVolumeSerialNumber), 'file_index': '%016x' % index,
            'index_value': index}


def file_info(path):
    """Win32 identity of the object at path itself (reparse points are not followed). None when absent or unreadable."""
    if os.name != 'nt':
        return None
    import ctypes
    k = _kernel32()
    # FILE_READ_ATTRIBUTES; share read|write|delete; OPEN_EXISTING; BACKUP_SEMANTICS | OPEN_REPARSE_POINT
    h = k.CreateFileW(path, 0x80, 0x7, None, 3, 0x02000000 | 0x00200000, None)
    if h in (None, ctypes.c_void_p(-1).value):
        return None
    try:
        return _info_from_handle(h)
    finally:
        k.CloseHandle(h)


def fd_info(fd):
    if os.name != 'nt':
        return None
    import msvcrt
    try:
        return _info_from_handle(msvcrt.get_osfhandle(fd))
    except OSError:
        return None


def identity_of(info):
    """{volume_serial: hex8, file_index: hex16} or None when the OS gave no usable identity (never compared as equal)."""
    if not info or info['index_value'] == 0:
        return None
    return {'volume_serial': info['volume_serial'], 'file_index': info['file_index']}


def _is_regular(info):
    return bool(info) and not info['attributes'] & (_FILE_ATTRIBUTE_DIRECTORY | _FILE_ATTRIBUTE_REPARSE_POINT)


def _is_plain_dir(info):
    return bool(info) and bool(info['attributes'] & _FILE_ATTRIBUTE_DIRECTORY) and not info['attributes'] & _FILE_ATTRIBUTE_REPARSE_POINT


def volume_of(project):
    """{'fs': name or None, 'local': bool, 'drive_type': int or None, 'cloud_attributes': bool}."""
    out = {'fs': None, 'local': False, 'drive_type': None, 'cloud_attributes': False}
    if os.name != 'nt':
        return out
    import ctypes
    from ctypes import wintypes
    k = _kernel32()
    root = ctypes.create_unicode_buffer(1024)
    if not k.GetVolumePathNameW(project, root, 1024):
        return out
    fs = ctypes.create_unicode_buffer(64)
    serial, maxlen, flags = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
    if k.GetVolumeInformationW(root.value, None, 0, ctypes.byref(serial), ctypes.byref(maxlen), ctypes.byref(flags), fs, 64):
        out['fs'] = fs.value
    out['drive_type'] = int(k.GetDriveTypeW(root.value))
    out['local'] = out['drive_type'] == 3  # DRIVE_FIXED; removable/remote/cdrom/ramdisk are not local here
    attrs = k.GetFileAttributesW(project)
    if attrs != 0xFFFFFFFF and attrs & _CLOUD_ATTRIBUTES:
        out['cloud_attributes'] = True
    return out


def volume_supported(project):
    v = volume_of(project)
    return os.name == 'nt' and v['fs'] == 'NTFS' and v['local'] and not v['cloud_attributes'], v


def _root_problem(project):
    """'ROOT_LINKED' unless the project root itself is a plain folder (not a junction, symlink or other reparse point)."""
    return None if _is_plain_dir(file_info(project)) else 'ROOT_LINKED'


class _PinSet:
    """Folder pins (transaction.Pins) held for the whole mutation; each folder is pinned once, then proven to be itself."""

    def __init__(self, pins):
        self.pins = pins
        self.done = set()

    def pin(self, path):
        """'OK', 'UNSAFE' (not a plain folder, or not the folder the handle holds) or 'NO_PIN' (the OS gave no handle)."""
        key = os.path.normcase(path)
        if key in self.done:
            return 'OK'
        before = file_info(path)
        if not _is_plain_dir(before):
            return 'UNSAFE'
        count = len(getattr(self.pins, '_handles', ()))
        if not self.pins.hold(path) or len(self.pins._handles) != count + 1:
            return 'NO_PIN'
        # the handle follows links, file_info does not: equal identity means the path is the held folder itself
        mine, after = _info_from_handle(self.pins._handles[-1]), file_info(path)
        ident = identity_of(after)
        if not _is_plain_dir(after) or ident is None or identity_of(mine) != ident or identity_of(before) != ident:
            return 'UNSAFE'
        self.done.add(key)
        return 'OK'


def _walk(project, segments, held, wrote, envelope, create, required=0):
    """Pin the root, then each folder of segments in order, creating missing ones (pin before every mkdir) when create.

    Returns None when done (without create it stops at the first missing folder, so None does not prove the folders exist),
    else 'UNSAFE', 'NO_PIN', 'CREATE_FAILED' or 'MISSING'. The first `required` folders must already exist: a missing one
    returns 'MISSING' and nothing is created at or below it. Every folder before it is pinned first, so existence is proven
    against the pinned chain, not against a path that may change.
    A parent is pinned and proven before anything is created inside it, so a replaced parent is never written through.
    """
    state = held.pin(project)
    if state != 'OK':
        return state
    path = project
    for index, seg in enumerate(segments):
        path = os.path.join(path, seg)
        if not os.path.lexists(path):
            if index < required:
                return 'MISSING'
            if not create:
                return None
            try:
                os.mkdir(path)
            except FileExistsError:
                pass  # someone else made it; the pin below proves what it is
            except OSError:
                return 'CREATE_FAILED'
            else:
                wrote.append({'path': _rel(project, path), 'op': 'mkdir', 'envelope': envelope})
        state = held.pin(path)
        if state != 'OK':
            return state
    return None


def _delete_exact(path, expected):
    """Delete the file at path only if the handle opened on it is a regular file with identity `expected`.

    'DELETED' when deletion was requested; other sharing handles can defer removal until they close.
    'CHANGED' when the object found is not the one expected (nothing deleted); 'FAILED' otherwise.
    The handle shares read/write but not delete, so nobody can rename or remove the object between check and delete;
    the disposition is set on that handle, so it removes only that name (a hard link elsewhere is untouched).
    """
    if expected is None or os.name != 'nt':
        return 'FAILED'
    import ctypes
    k = _kernel32()
    _hook('before_delete_open', {'path': path})
    # DELETE | FILE_READ_ATTRIBUTES; share read|write; OPEN_EXISTING; OPEN_REPARSE_POINT (never follow a link)
    h = k.CreateFileW(path, 0x00010000 | 0x80, 0x3, None, 3, 0x00200000, None)
    if h in (None, ctypes.c_void_p(-1).value):
        return 'FAILED'
    try:
        info = _info_from_handle(h)
        if not _is_regular(info) or identity_of(info) != expected:
            return 'CHANGED'
        try:
            _fail_point('cleanup')
        except OSError:
            return 'FAILED'
        flag = ctypes.c_ubyte(1)  # FILE_DISPOSITION_INFO.DeleteFile
        return 'DELETED' if k.SetFileInformationByHandle(h, 4, ctypes.byref(flag), 1) else 'FAILED'
    finally:
        k.CloseHandle(h)


# ---------------------------------------------------------------- lexical path checks (packet 2.2, 2.3)
def path_form_problem(rel):
    """None when rel is an accepted project-relative POSIX path, else 'PATH_UNSUPPORTED_FORM'."""
    if not isinstance(rel, str) or not rel or unicodedata.normalize('NFC', rel) != rel:
        return 'PATH_UNSUPPORTED_FORM'
    if rel.startswith('/') or '\\' in rel or ':' in rel:
        return 'PATH_UNSUPPORTED_FORM'
    for seg in rel.split('/'):
        if seg in ('', '.', '..') or seg[-1] in '. ' or SHORT_NAME_RE.search(seg):
            return 'PATH_UNSUPPORTED_FORM'
        if any(ord(c) < 0x20 or c in '<>"|?*' for c in seg):
            return 'PATH_UNSUPPORTED_FORM'
        if seg.casefold().split('.')[0] in DEVICE_NAMES:
            return 'PATH_UNSUPPORTED_FORM'
    return None


def _authority_name(rel):
    import fnmatch
    base = rel.rsplit('/', 1)[-1].casefold()
    return any(fnmatch.fnmatchcase(base, p) for p in AUTHORITY_PATTERNS)


def target_zone(rel):
    segs = rel.split('/')
    if len(segs) >= 2 and segs[0] == 'working':
        return 'working'
    if len(segs) >= 2 and segs[0] == 'output':
        return 'output_new'
    return None


# ---------------------------------------------------------------- request -> task snapshot (C-2.1, C-2.4)
class RequestError(Exception):
    def __init__(self, reason):
        Exception.__init__(self, reason)
        self.reason = reason


REQUEST_KEYS = {'work_id', 'target', 'content_use', 'intent_ref', 'main_interpretation', 'unconfirmed', 'requirements',
                'grant_refs', 'subject', 'inputs', 'supersedes'}
REQUIRED_KEYS = ('work_id', 'target', 'intent_ref', 'main_interpretation', 'requirements', 'grant_refs', 'subject', 'inputs')


def _need(cond):
    if not cond:
        raise RequestError('REQUEST_INVALID')


def _check_str(v, min_len=1):
    _need(isinstance(v, str) and len(v) >= min_len)


def _check_actor(v):
    _need(isinstance(v, dict) and set(v) <= {'actor_id', 'role', 'host', 'session_ref'} and {'actor_id', 'role'} <= set(v))
    _need(isinstance(v['actor_id'], str) and ID_RE.fullmatch(v['actor_id'])
          and isinstance(v['role'], str) and v['role'] in ROLES)
    for k in ('host', 'session_ref'):
        if k in v:
            _check_str(v[k], 0)


def _check_attribution(v):
    _need(isinstance(v, dict) and set(v) <= {'source_class', 'channel', 'recorded_by', 'observed_by', 'evidence_locator', 'note'})
    _need({'source_class', 'channel', 'recorded_by'} <= set(v))
    _need(isinstance(v['source_class'], str) and v['source_class'] in SOURCE_CLASSES
          and isinstance(v['channel'], str) and v['channel'] in CHANNELS)
    _check_actor(v['recorded_by'])
    if 'observed_by' in v:
        _check_actor(v['observed_by'])
    if 'evidence_locator' in v:
        _check_str(v['evidence_locator'])
    if 'note' in v:
        _check_str(v['note'], 0)
    if v['source_class'] == 'USER_CONFIRMATION':
        _need('evidence_locator' in v and v['channel'] in ('USER_MESSAGE', 'HOST_CONFIRMATION_UI', 'USER_AUTHORED_FILE'))
    if v['source_class'] == 'TOOL_OBSERVATION':
        _need('observed_by' in v and v['channel'] == 'TOOL_OUTPUT' and v['observed_by']['role'] in ('tool', 'host'))
    if v['source_class'] == 'ROLE_REPORT':
        _need('observed_by' in v and v['channel'] == 'ROLE_OUTPUT')


def _ref(v, kind):
    """attributed_ref without 'kind' from the caller; the tool sets kind."""
    _need(isinstance(v, dict) and 'kind' not in v and set(v) <= {'ref_id', 'locator', 'revision', 'digest', 'issuer', 'attribution'})
    _need({'ref_id', 'locator', 'digest', 'attribution'} <= set(v))
    _need(isinstance(v['ref_id'], str) and ID_RE.fullmatch(v['ref_id']))
    _check_str(v['locator'])
    _need(isinstance(v['digest'], str) and DIGEST_RE.fullmatch(v['digest']))
    if 'revision' in v:
        _check_str(v['revision'], 0)
    if 'issuer' in v:
        _check_actor(v['issuer'])
    _check_attribution(v['attribution'])
    out = dict(v)
    out['kind'] = kind
    return out


def _as_set(items):
    """Sort a C1 'set' by canonical bytes; a duplicate is refused, never deduplicated."""
    keyed = sorted(((cj_dumps(i), i) for i in items), key=lambda p: p[0])
    keys = [k for k, _ in keyed]
    _need(len(set(keys)) == len(keys))
    return [i for _, i in keyed]


def build_task(request, rid):
    """Map the API request onto one C1-shaped task snapshot. Raises RequestError(reason)."""
    if not isinstance(request, dict):
        raise RequestError('REQUEST_INVALID')
    if set(request) - REQUEST_KEYS:
        raise RequestError('REQUEST_INVALID')  # includes extra_review_phases, completion, context_refs, ... (unsupported in v1)
    if any(k not in request for k in REQUIRED_KEYS):
        raise RequestError('SNAPSHOT_INCOMPLETE')
    try:
        cj_dumps(request)
    except CJError:
        raise RequestError('REQUEST_INVALID')
    work_id, target = request['work_id'], request['target']
    _need(isinstance(work_id, str) and ID_RE.fullmatch(work_id))
    if path_form_problem(target):
        raise RequestError('PATH_UNSUPPORTED_FORM')
    zone = target_zone(target)
    if zone is None:
        raise RequestError('ZONE_NOT_LIGHT')
    if _authority_name(target):
        raise RequestError('AUTHORITY_NAME')
    action = {'operation': 'create_new', 'tool': TOOL_NAME, 'targets': [target], 'write_zone': zone}
    if zone == 'output_new':
        if 'content_use' not in request:
            raise RequestError('SNAPSHOT_INCOMPLETE')
        cu = request['content_use']
        _need(isinstance(cu, list) and all(isinstance(c, str) for c in cu))
        if cu != ['internal_draft']:
            raise RequestError('CONTENT_USE_NOT_INTERNAL')
        action['content_use'] = ['internal_draft']
    elif 'content_use' in request:
        raise RequestError('REQUEST_INVALID')
    _check_str(request['main_interpretation'])
    intent = {'refs': [_ref(request['intent_ref'], 'user_intent')], 'main_interpretation': request['main_interpretation']}
    if 'unconfirmed' in request:
        _need(isinstance(request['unconfirmed'], list) and all(isinstance(u, str) for u in request['unconfirmed']))
        intent['unconfirmed'] = list(request['unconfirmed'])
    reqs = request['requirements']
    _need(isinstance(reqs, list))
    seen = set()
    for r in reqs:
        _need(isinstance(r, dict) and set(r) <= {'req_id', 'statement', 'mandatory', 'expected_evidence', 'fail_when'})
        _need({'req_id', 'statement', 'mandatory'} <= set(r))
        _need(isinstance(r['req_id'], str) and ID_RE.fullmatch(r['req_id']) and r['req_id'] not in seen)
        seen.add(r['req_id'])
        _check_str(r['statement'])
        _need(isinstance(r['mandatory'], bool))
        if 'expected_evidence' in r:
            _need(isinstance(r['expected_evidence'], list) and all(isinstance(e, str) for e in r['expected_evidence']))
        if 'fail_when' in r:
            _check_str(r['fail_when'], 0)
    if not any(r['mandatory'] for r in reqs):
        raise RequestError('SNAPSHOT_INCOMPLETE')
    grants = request['grant_refs']
    _need(isinstance(grants, list))
    if not grants:
        raise RequestError('SNAPSHOT_INCOMPLETE')
    grants = _as_set([_ref(g, 'grant') for g in grants])
    subject = request['subject']
    _check_actor(subject)
    inputs = request['inputs']
    _need(isinstance(inputs, list))
    for i in inputs:
        _need(isinstance(i, dict) and set(i) <= {'path', 'digest', 'source_id', 'revision', 'scope'} and {'path', 'digest'} <= set(i))
        if path_form_problem(i['path']):
            raise RequestError('PATH_UNSUPPORTED_FORM')
        _need(isinstance(i['digest'], str) and DIGEST_RE.fullmatch(i['digest']))
        for k in ('source_id', 'revision', 'scope'):
            if k in i:
                _check_str(i[k], 0)
    _need(len({i['path'] for i in inputs}) == len(inputs))
    inputs = _as_set([dict(i) for i in inputs])
    if 'supersedes' in request:
        _need(isinstance(request['supersedes'], str) and RID_RE.fullmatch(request['supersedes']))
    task = {
        'record_type': 'task', 'schema_version': TASK_SCHEMA_VERSION, 'evaluation_basis': 'COOPERATIVE_WORKFLOW',
        'work_id': work_id, 'task_id': 'pcn1-' + rid, 'task_revision': 1, 'proposed_by': dict(subject),
        'intent': intent, 'authority': {'grant_refs': grants, 'subject': dict(subject)}, 'inputs': inputs,
        'effects': {'actions': [action], 'expected_outputs': [target], 'on_missing': 'STOP_DEPENDENT_EFFECT'},
        'acceptance': {'requirements': [dict(r) for r in reqs]}, 'envelope': {'role': subject['role']},
    }
    return task


# ---------------------------------------------------------------- evidence (C-2.3)
COMMON = ('schema', 'protocol', 'protocol_version', 'request_id', 'state', 'at')
AT_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
REASONS = {
    'conflict': {'TARGET_EXISTS'},
    'abandoned': {'STAGE_FAILED', 'STAGE_HASH_MISMATCH', 'PARENT_CREATE_FAILED', 'LINK_FAILED'},
    'unknown': {'POST_LINK_MISMATCH', 'TARGET_ABSENT', 'STAGED_ABSENT', 'IDENTITY_MISMATCH', 'IDENTITY_UNAVAILABLE',
                'TARGET_MODIFIED', 'TARGET_NOT_REGULAR', 'PREPARED_UNREADABLE', 'EVIDENCE_INCONSISTENT', 'EVIDENCE_WRITE_FAILED'},
}


def _header(rid, state):
    return {'schema': SCHEMA, 'protocol': PROTOCOL, 'protocol_version': PROTOCOL_VERSION, 'request_id': rid,
            'state': state, 'at': _now()}


def _content_ok(c):
    return (isinstance(c, dict) and set(c) == {'sha256', 'size'} and isinstance(c['sha256'], str) and DIGEST_RE.fullmatch(c['sha256'])
            and isinstance(c['size'], int) and not isinstance(c['size'], bool) and c['size'] >= 0)


def _identity_ok(i):
    return (isinstance(i, dict) and set(i) == {'volume_serial', 'file_index'} and isinstance(i['volume_serial'], str)
            and re.fullmatch(r'[0-9a-f]{8}', i['volume_serial']) and isinstance(i['file_index'], str)
            and re.fullmatch(r'[0-9a-f]{16}', i['file_index']) and i['file_index'] != '0' * 16)


def request_from_task(task):
    """The request this version's mapper would need to produce `task` (pure; inverse of build_task for the fields it supports).

    Fields build_task does not produce (custom envelope, context_refs, extra effects, ...) are not copied, so build_task of the
    result differs from a task that carries them: a task is owner-representable exactly when the rebuild equals it.
    Raises KeyError, TypeError, IndexError or AttributeError when the task lacks the fields the mapper reads.
    """
    intent, authority = task['intent'], task['authority']
    action = task['effects']['actions'][0]
    request = {
        'work_id': task['work_id'], 'target': action['targets'][0],
        'intent_ref': {k: v for k, v in intent['refs'][0].items() if k != 'kind'},
        'main_interpretation': intent['main_interpretation'],
        'requirements': task['acceptance']['requirements'],
        'grant_refs': [{k: v for k, v in g.items() if k != 'kind'} for g in authority['grant_refs']],
        'subject': authority['subject'], 'inputs': task['inputs'],
    }
    if 'unconfirmed' in intent:
        request['unconfirmed'] = intent['unconfirmed']
    if 'content_use' in action:
        request['content_use'] = action['content_use']
    return request


def _snapshot_ok(task, rid):
    """Accept exactly a snapshot this version's request mapper can produce, without a second task schema."""
    try:
        return cj_dumps(build_task(request_from_task(task), rid)) == cj_dumps(task)
    except (RequestError, CJError, KeyError, TypeError, IndexError, AttributeError):
        return False


def validate_evidence(raw, rid, state):
    """Parsed evidence when raw is canonical LAW-CJ/2 bytes of a valid `state` record for rid, else None (fail closed)."""
    if not raw or len(raw) > MAX_JSON_BYTES:
        return None
    try:
        obj = cj_loads(raw)
        if cj_dumps(obj) != raw:
            return None
    except CJError:
        return None
    if not isinstance(obj, dict):
        return None
    if type(obj.get('protocol_version')) is not int:
        return None
    if (obj.get('schema'), obj.get('protocol'), obj.get('protocol_version'), obj.get('request_id'), obj.get('state')) != \
            (SCHEMA, PROTOCOL, PROTOCOL_VERSION, rid, state.upper()):
        return None
    if not (isinstance(obj.get('at'), str) and AT_RE.fullmatch(obj['at'])):
        return None
    keys = set(obj) - set(COMMON)
    if state == 'prepared':
        need = {'task', 'content', 'inputs_observed_at_publish', 'platform', 'entrypoint_sha256'}
        if not (need <= keys <= need | {'supersedes'}):
            return None
        if obj['platform'] != PLATFORM or not (isinstance(obj['entrypoint_sha256'], str) and DIGEST_RE.fullmatch(obj['entrypoint_sha256'])):
            return None
        if not _content_ok(obj['content']) or not _snapshot_ok(obj['task'], rid):
            return None
        if 'supersedes' in obj and not (isinstance(obj['supersedes'], str) and RID_RE.fullmatch(obj['supersedes'])):
            return None
        task = obj['task']
        try:
            action = task['effects']['actions'][0]
            if task['task_id'] != 'pcn1-' + rid or len(task['effects']['actions']) != 1 or len(action['targets']) != 1:
                return None
            target = action['targets'][0]
            inputs = task['inputs']
            observed = obj['inputs_observed_at_publish']
            if not isinstance(observed, list) or sorted((o['path'], o['digest']) for o in observed) != \
                    sorted((i['path'], i['digest']) for i in inputs) or any(set(o) != {'path', 'digest'} for o in observed):
                return None
        except (KeyError, TypeError, IndexError, AttributeError):
            return None
        if path_form_problem(target) or target_zone(target) is None:
            return None
        return obj
    if state == 'published':
        need = {'target', 'content', 'identity', 'nlink_at_check', 'protection', 'recovered'}
        if keys != need:
            return None
        if not (_content_ok(obj['content']) and _identity_ok(obj['identity']) and isinstance(obj['target'], str)
                and isinstance(obj['nlink_at_check'], int) and not isinstance(obj['nlink_at_check'], bool)
                and obj['nlink_at_check'] >= 2 and obj['protection'] in ('held', 'recheck_only')
                and isinstance(obj['recovered'], bool)):
            return None
        return obj
    allowed = {'reason', 'detail'} | ({'by'} if state == 'unknown' else set())
    need = {'reason'} | ({'by'} if state == 'unknown' else set())
    if not (need <= keys <= allowed) or not isinstance(obj['reason'], str) or obj['reason'] not in REASONS[state]:
        return None
    if 'detail' in obj and not (isinstance(obj['detail'], str) and len(obj['detail']) <= 200):
        return None
    if state == 'unknown' and obj['by'] not in ('publish', 'recover'):
        return None
    return obj


def _publish_dir(project):
    return os.path.join(project, *PUBLISH_DIR)


def _evidence_path(project, rid, state):
    return os.path.join(_publish_dir(project), '%s.%s' % (rid, 'staged' if state == 'staged' else state + '.json'))


def _read_raw(path):
    try:
        with open(path, 'rb') as f:
            return f.read(MAX_JSON_BYTES + 1)
    except OSError:
        return None


def _runtime_problem(project):
    """'RUNTIME_LINKED' when the root, .agent, .agent/runtime or the publish folder is (or passes through) a link or reparse point."""
    folder = _publish_dir(project)
    if _root_problem(project) or not transaction.link_free(folder, project):
        return 'RUNTIME_LINKED'
    path = project
    for seg in PUBLISH_DIR:
        path = os.path.join(path, seg)
        if os.path.lexists(path):
            info = file_info(path)
            if not _is_plain_dir(info):
                return 'RUNTIME_LINKED'
    return None


def runtime_parents_problem(project):
    """None when `.agent` and `.agent/runtime` both exist as plain folders; 'RUNTIME_PARENT_MISSING' or 'RUNTIME_LINKED' otherwise.

    The same precondition publish enforces under its pins, as a read-only fact for observers; it is not proof once publish runs.
    """
    path = project
    for seg in RUNTIME_PARENTS:
        path = os.path.join(path, seg)
        if not os.path.lexists(path):
            return 'RUNTIME_PARENT_MISSING'
        if not _is_plain_dir(file_info(path)):
            return 'RUNTIME_LINKED'
    return None


def _rid_files(project, rid):
    """States for which this rid already has a file under the publish folder (terminal, prepared or orphan staged)."""
    return [s for s in RID_FILE_STATES if os.path.lexists(_evidence_path(project, rid, s))]


def _write_all(fd, data):
    view = memoryview(data)
    while view:
        n = os.write(fd, view)
        if n <= 0:
            raise OSError('short write')
        view = view[n:]


def _write_new(project, path, data, wrote, envelope, fail_point=None):
    """Create path with O_EXCL, write, fsync. Returns True; on failure after creation the (partial) file stays and False is returned."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0), 0o600)
    wrote.append({'path': _rel(project, path), 'op': 'create', 'envelope': envelope})
    try:
        if fail_point:
            _fail_point(fail_point)
        _write_all(fd, data)
        os.fsync(fd)
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def _write_terminal(project, rid, state, fields, wrote):
    """Create the single terminal file for rid. True when written completely."""
    obj = _header(rid, state.upper())
    obj.update(fields)
    path = _evidence_path(project, rid, state)
    try:
        return _write_new(project, path, cj_dumps(obj), wrote, 'T6',
                          fail_point='published_write' if state == 'published' else 'terminal_write')
    except OSError:
        return False


def _terminal_files(project, rid):
    return [s for s in TERMINALS if os.path.lexists(_evidence_path(project, rid, s))]


# ---------------------------------------------------------------- lock (C-3)
class LockBusy(Exception):
    pass


def _lock(fd):
    import msvcrt
    os.lseek(fd, LOCK_OFFSET, os.SEEK_SET)
    try:
        msvcrt.locking(fd, msvcrt.LK_NBLCK, LOCK_LEN)
    except OSError as e:
        if e.errno in (13, 36):  # EACCES / EDEADLOCK: another holder of this byte
            raise LockBusy()
        raise


def _unlock(fd):
    import msvcrt
    try:
        os.lseek(fd, LOCK_OFFSET, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, LOCK_LEN)
    except OSError:
        pass  # closing the descriptor releases it anyway


# ---------------------------------------------------------------- publish
def _check_parents(project, target):
    """PARENT_UNSAFE when an existing ancestor of target is not a plain folder or the path passes through a link."""
    parent = os.path.dirname(_abs(project, target))
    if not transaction.link_free(parent, project):
        return 'PARENT_UNSAFE'
    path = project
    for seg in target.split('/')[:-1]:
        path = os.path.join(path, seg)
        if not os.path.lexists(path):
            break
        if not _is_plain_dir(file_info(path)):
            return 'PARENT_UNSAFE'
    return None


def publish(project_root, request, staged, *, request_id=None):
    """Publish one new file. `request_id` (32 lowercase hex, chosen by the caller) fixes the task id pcn1-<rid>; default: a new UUID.

    An invalid request_id is REFUSED before any mutation. A used id or late collision never overwrites or deletes its existing artifacts;
    REFUSED may report prior bootstrap/prepared writes in `wrote`, which is authoritative for effects already performed.
    """
    if not isinstance(project_root, str) or not isinstance(staged, (bytes, bytearray)):
        raise TypeError('project_root must be str and staged bytes')
    project = os.path.abspath(project_root)
    wrote = []
    if request_id is None:
        rid = uuid.uuid4().hex
    elif type(request_id) is str and RID_RE.fullmatch(request_id):
        rid = request_id
    else:
        return _result('REFUSED', 'REQUEST_ID_INVALID')
    # ---- step 1: request, path, zone, volume (nothing written)
    if len(staged) > MAX_STAGED_BYTES:
        return _result('REFUSED', 'STAGED_TOO_LARGE')
    try:
        task = build_task(request, rid)
    except RequestError as e:
        return _result('REFUSED', e.reason)
    target = task['effects']['actions'][0]['targets'][0]
    if os.name != 'nt':
        return _result('REFUSED', 'UNSUPPORTED_FS')
    if _root_problem(project):
        return _result('REFUSED', 'PARENT_UNSAFE', detail='ROOT_LINKED')
    ok, _vol = volume_supported(project)
    if not ok:
        return _result('REFUSED', 'UNSUPPORTED_FS')
    problem = _runtime_problem(project)
    if problem:
        return _result('REFUSED', problem)
    problem = _check_parents(project, target)
    if problem:
        return _result('REFUSED', problem)
    # ---- step 2: inputs must still be the bytes the drafting tool read
    observed = []
    for item in task['inputs']:
        path = _abs(project, item['path'])
        info = file_info(path)
        try:
            if not transaction.link_free(path, project) or not _is_regular(info):
                return _result('REFUSED', 'INPUT_CHANGED_SINCE_READ')
            digest, _ = _sha_file(path)
        except OSError:
            return _result('REFUSED', 'INPUT_CHANGED_SINCE_READ')
        if digest != item['digest']:
            return _result('REFUSED', 'INPUT_CHANGED_SINCE_READ')
        observed.append({'path': item['path'], 'digest': digest})
    content = {'sha256': _sha_bytes(bytes(staged)), 'size': len(staged)}
    prepared = _header(rid, 'PREPARED')
    prepared.update({'task': task, 'content': content, 'inputs_observed_at_publish': observed, 'platform': PLATFORM,
                     'entrypoint_sha256': entrypoint_sha256()})
    if 'supersedes' in request:
        prepared['supersedes'] = request['supersedes']
    try:
        prepared_bytes = cj_dumps(prepared)
    except CJError:
        return _result('REFUSED', 'REQUEST_INVALID')
    if len(prepared_bytes) > MAX_JSON_BYTES:
        return _result('REFUSED', 'SNAPSHOT_TOO_LARGE')
    # ---- pins held from before the first mutation until the terminal and T7 are done (pins, not the byte lock, protect paths)
    with transaction.Pins() as pins:
        held = _PinSet(pins)
        _hook('before_pin', {'rid': rid, 'project': project})
        # existing target folders first (nothing is written if one is unsafe), then the runtime chain: `.agent` and `.agent/runtime`
        # must already exist (pinned, never created here); only `publish` is created, under the pinned runtime folder (T2)
        state = _walk(project, target.split('/')[:-1], held, wrote, 'T1', False)
        if state:
            return _unsafe_result('PARENT_UNSAFE', state, wrote)
        state = _walk(project, PUBLISH_DIR, held, wrote, 'T2', True, required=len(RUNTIME_PARENTS))
        if state == 'MISSING':
            return _result('REFUSED', 'RUNTIME_PARENT_MISSING', None, wrote)
        if state == 'CREATE_FAILED':
            return _result('REFUSED', 'EVIDENCE_WRITE_FAILED', None, wrote)
        if state:
            return _unsafe_result('RUNTIME_LINKED', state, wrote)
        return _publish_pinned(project, rid, task, target, bytes(staged), content, prepared_bytes, wrote, held)


def _unsafe_result(reason, state, wrote):
    return _result('REFUSED', reason, None, wrote, **({'detail': 'PIN_UNAVAILABLE'} if state == 'NO_PIN' else {}))


def _publish_pinned(project, rid, task, target, staged, content, prepared_bytes, wrote, held):
    problem = _runtime_problem(project)
    if problem:
        return _result('REFUSED', problem, None, wrote)
    prep_path = _evidence_path(project, rid, 'prepared')
    if _rid_files(project, rid):  # a file of this rid appeared since the first check: never reuse, overwrite or delete it
        return _result('REFUSED', 'RID_TAKEN', rid, wrote)
    try:
        fd = os.open(prep_path, os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0), 0o600)
    except FileExistsError:
        return _result('REFUSED', 'RID_TAKEN', rid, wrote)
    except OSError:
        return _result('REFUSED', 'EVIDENCE_WRITE_FAILED', None, wrote)
    wrote.append({'path': _rel(project, prep_path), 'op': 'create', 'envelope': 'T3'})
    _hook('after_bootstrap', {'rid': rid, 'project': project})
    try:
        try:
            _lock(fd)
        except (LockBusy, OSError):
            return _result('REFUSED', 'LOCK_UNAVAILABLE', rid, wrote)
        try:
            # ---- recheck under the lock: still our empty file, no terminal written by a recover that came first
            mine, here = fd_info(fd), file_info(prep_path)
            if (_terminal_files(project, rid) or os.path.lexists(_evidence_path(project, rid, 'staged'))
                    or identity_of(mine) is None or identity_of(mine) != identity_of(here) or os.fstat(fd).st_size != 0):
                return _result('REFUSED', 'RID_TAKEN', rid, wrote)
            try:
                _fail_point('prepared_write')
                os.lseek(fd, 0, os.SEEK_SET)
                _write_all(fd, prepared_bytes)
                os.fsync(fd)
            except OSError:
                return _result('REFUSED', 'EVIDENCE_WRITE_FAILED', rid, wrote)
            _kill_point('after_prepared')
            return _publish_locked(project, rid, task, target, staged, content, wrote, held)
        finally:
            _unlock(fd)
    finally:
        os.close(fd)


def _publish_locked(project, rid, task, target, staged, content, wrote, held):
    common = {'target': target, 'content': content}
    staged_path = _evidence_path(project, rid, 'staged')
    # ---- step 4: stage
    try:
        ok = _write_new(project, staged_path, staged, wrote, 'T4', fail_point='stage_write')
        reason = None if ok else 'STAGE_FAILED'
        if ok:
            digest, size = _sha_file(staged_path)
            if (digest, size) != (content['sha256'], content['size']):
                reason = 'STAGE_HASH_MISMATCH'
    except OSError:
        reason = 'STAGE_FAILED'
    if reason:
        return _terminal_outcome(project, rid, 'abandoned', {'reason': reason}, wrote, 'ABANDONED', reason, common)
    _kill_point('after_stage')
    # ---- step 5: parents (T1) and the create-only link (T5); every folder is pinned before anything is created in it
    target_path = _abs(project, target)
    state = _walk(project, target.split('/')[:-1], held, wrote, 'T1', True)
    if state == 'CREATE_FAILED':
        return _terminal_outcome(project, rid, 'abandoned', {'reason': 'PARENT_CREATE_FAILED'}, wrote,
                                 'ABANDONED', 'PARENT_CREATE_FAILED', common)
    if state:
        return _terminal_outcome(project, rid, 'abandoned', {'reason': 'LINK_FAILED', 'detail': 'PARENT_UNSAFE'}, wrote,
                                 'ABANDONED', 'LINK_FAILED', common)
    protection = 'held'  # reached only with every folder of root, target parents and runtime pinned
    if _check_parents(project, target) or _runtime_problem(project) or not _is_regular(file_info(staged_path)):
        return _terminal_outcome(project, rid, 'abandoned', {'reason': 'LINK_FAILED', 'detail': 'PARENT_UNSAFE'}, wrote,
                                 'ABANDONED', 'LINK_FAILED', common)
    _hook('before_link', {'rid': rid, 'target': target_path, 'staged': staged_path})
    try:
        os.link(staged_path, target_path)
    except FileExistsError:
        return _terminal_outcome(project, rid, 'conflict', {'reason': 'TARGET_EXISTS'}, wrote, 'CONFLICT', 'TARGET_EXISTS', common)
    except OSError:
        return _terminal_outcome(project, rid, 'abandoned', {'reason': 'LINK_FAILED'}, wrote, 'ABANDONED', 'LINK_FAILED', common)
    wrote.append({'path': target, 'op': 'link', 'envelope': 'T5'})
    _kill_point('after_link')
    _hook('after_link', {'rid': rid, 'target': target_path, 'staged': staged_path})
    # ---- step 6: the new name is the staged file, with the planned bytes
    t_info, s_info = file_info(target_path), file_info(staged_path)
    t_id, s_id = identity_of(t_info), identity_of(s_info)
    reason = None
    if not _is_regular(t_info):
        reason = 'TARGET_NOT_REGULAR'
    elif t_id is None or s_id is None:
        reason = 'IDENTITY_UNAVAILABLE'
    elif t_id != s_id or t_info['nlink'] < 2:
        reason = 'POST_LINK_MISMATCH'
    else:
        try:
            if _sha_file(target_path) != (content['sha256'], content['size']):
                reason = 'POST_LINK_MISMATCH'
        except OSError:
            reason = 'POST_LINK_MISMATCH'
    if reason:
        return _terminal_outcome(project, rid, 'unknown', {'reason': reason, 'by': 'publish'}, wrote, 'UNKNOWN', reason, common)
    _kill_point('after_verify')
    # ---- step 7: published, then T7
    fields = dict(common, identity=t_id, nlink_at_check=t_info['nlink'], protection=protection, recovered=False)
    if not _write_terminal(project, rid, 'published', fields, wrote):
        return _result('PUBLISHED_EVIDENCE_PENDING', 'PUBLISHED_WRITE_FAILED', rid, wrote, protection=protection, **common)
    _kill_point('after_published')
    cleaned = _cleanup_published_staged(project, rid, t_id, wrote)
    return _result('PUBLISHED', None if cleaned else 'STAGED_CLEANUP_PENDING', rid, wrote, protection=protection,
                   cleanup_pending=not cleaned, **common)


def _terminal_outcome(project, rid, state, fields, wrote, outcome, reason, common):
    if _write_terminal(project, rid, state, fields, wrote):
        return _result(outcome, reason, rid, wrote, **common)
    return _result('UNKNOWN', 'EVIDENCE_WRITE_FAILED', rid, wrote, **common)


def _cleanup_published_staged(project, rid, published_identity, wrote):
    """T7 after published: remove exactly <rid>.staged, only the object that has the published identity (checked on the delete handle)."""
    if published_identity is None or _runtime_problem(project):
        return False
    path = _evidence_path(project, rid, 'staged')
    if _delete_exact(path, published_identity) != 'DELETED':
        return False
    wrote.append({'path': _rel(project, path), 'op': 'delete', 'envelope': 'T7'})
    return not os.path.lexists(path)  # deletion can remain pending while another sharing handle is open


# ---------------------------------------------------------------- recover / discard
def _open_locked(project, rid, held):
    """(fd, None) holding the rid lock, or (None, result). The runtime chain is pinned (by `held`) before PREPARED is opened."""
    if not isinstance(rid, str) or not RID_RE.fullmatch(rid):
        raise ValueError('request_id must be 32 lowercase hex characters')
    if os.name != 'nt':
        return None, _result('REFUSED', 'UNSUPPORTED_FS', rid)
    if _root_problem(project):
        return None, _result('REFUSED', 'PARENT_UNSAFE', rid, detail='ROOT_LINKED')
    ok, _ = volume_supported(project)
    if not ok:
        return None, _result('REFUSED', 'UNSUPPORTED_FS', rid)
    problem = _runtime_problem(project)
    if problem:
        return None, _result('REFUSED', problem, rid)
    _hook('before_runtime_pin', {'rid': rid})
    state = _walk(project, PUBLISH_DIR, held, [], 'T2', False)
    if state:
        return None, _result('REFUSED', 'RUNTIME_LINKED', rid, **({'detail': 'PIN_UNAVAILABLE'} if state == 'NO_PIN' else {}))
    prep = _evidence_path(project, rid, 'prepared')
    if not os.path.lexists(prep) or not _is_regular(file_info(prep)):
        return None, _result('UNKNOWN', 'PREPARED_UNREADABLE', rid)
    _hook('before_prepared_open', {'rid': rid, 'prepared': prep})
    try:
        fd = os.open(prep, os.O_RDWR | getattr(os, 'O_BINARY', 0))
    except OSError:
        return None, _result('REFUSED', 'LOCK_UNAVAILABLE', rid)
    try:
        _lock(fd)
    except LockBusy:
        os.close(fd)
        return None, _result('BUSY', 'LOCK_BUSY', rid)
    except OSError:
        os.close(fd)
        return None, _result('REFUSED', 'LOCK_UNAVAILABLE', rid)
    # after acquire: the descriptor is the file at the path now, and the runtime path is still plain
    mine, here = fd_info(fd), file_info(prep)
    if identity_of(mine) is None or identity_of(mine) != identity_of(here) or not _is_regular(here) or _runtime_problem(project):
        _close_locked(fd)
        return None, _result('UNKNOWN', 'EVIDENCE_INCONSISTENT', rid)
    return fd, None


def _close_locked(fd):
    _unlock(fd)
    os.close(fd)


def _single_terminal(project, rid, prepared):
    """(state, obj) for exactly one valid terminal consistent with prepared; (None, None) when none; ('BAD', None) otherwise."""
    names = _terminal_files(project, rid)
    if not names:
        return None, None
    if len(names) > 1:
        return 'BAD', None
    state = names[0]
    obj = validate_evidence(_read_raw(_evidence_path(project, rid, state)), rid, state)
    if obj is None:
        return 'BAD', None
    if prepared is None and not (state == 'unknown' and obj['reason'] == 'PREPARED_UNREADABLE'):
        return 'BAD', None  # a terminal next to an unreadable prepared is only consistent when it says exactly that
    if state == 'published':
        action_target = prepared['task']['effects']['actions'][0]['targets'][0]
        if obj['target'] != action_target or obj['content'] != prepared['content']:
            return 'BAD', None
    return state, obj


def recover(project_root, request_id):
    project = os.path.abspath(project_root)
    with transaction.Pins() as pins:
        return _recover_pinned(project, request_id, _PinSet(pins))


def _recover_pinned(project, request_id, held):
    fd, early = _open_locked(project, request_id, held)
    if early:
        return early
    rid, wrote = request_id, []
    try:
        _hook('recover_locked', {'rid': rid})
        prepared = validate_evidence(_read_raw(_evidence_path(project, rid, 'prepared')), rid, 'prepared')
        state, obj = _single_terminal(project, rid, prepared)
        if state == 'BAD':
            return _result('UNKNOWN', 'EVIDENCE_INCONSISTENT', rid, wrote)
        if state == 'published':
            staged = _evidence_path(project, rid, 'staged')
            if os.path.lexists(staged):
                cleaned = _cleanup_published_staged(project, rid, obj['identity'], wrote)
                return _result('NO_ACTION', None if cleaned else 'STAGED_CLEANUP_PENDING', rid, wrote, terminal=state,
                               cleanup_pending=not cleaned)
            return _result('NO_ACTION', None, rid, wrote, terminal=state)
        if state is not None:
            return _result('NO_ACTION', None, rid, wrote, terminal=state)
        # ---- no terminal filename: decide from proof, never guess "never published"
        def unknown(reason):
            if _write_terminal(project, rid, 'unknown', {'reason': reason, 'by': 'recover'}, wrote):
                return _result('UNKNOWN', reason, rid, wrote)
            return _result('UNKNOWN', 'EVIDENCE_WRITE_FAILED', rid, wrote)
        if prepared is None:
            return unknown('PREPARED_UNREADABLE')
        staged = _evidence_path(project, rid, 'staged')
        if not os.path.lexists(staged):
            return unknown('STAGED_ABSENT')
        target = prepared['task']['effects']['actions'][0]['targets'][0]
        target_path = _abs(project, target)
        if not os.path.lexists(target_path):
            return unknown('TARGET_ABSENT')
        if not transaction.link_free(os.path.dirname(target_path), project):
            return unknown('TARGET_NOT_REGULAR')
        t_info, s_info = file_info(target_path), file_info(staged)
        if not _is_regular(t_info) or not _is_regular(s_info):
            return unknown('TARGET_NOT_REGULAR')
        t_id, s_id = identity_of(t_info), identity_of(s_info)
        if t_id is None or s_id is None:
            return unknown('IDENTITY_UNAVAILABLE')
        if t_id != s_id:
            return unknown('IDENTITY_MISMATCH')
        try:
            if _sha_file(target_path) != (prepared['content']['sha256'], prepared['content']['size']):
                return unknown('TARGET_MODIFIED')
        except OSError:
            return unknown('TARGET_MODIFIED')
        fields = {'target': target, 'content': prepared['content'], 'identity': t_id, 'nlink_at_check': t_info['nlink'],
                  'protection': 'recheck_only', 'recovered': True}
        if not _write_terminal(project, rid, 'published', fields, wrote):
            return _result('PUBLISHED_EVIDENCE_PENDING', 'PUBLISHED_WRITE_FAILED', rid, wrote)
        cleaned = _cleanup_published_staged(project, rid, t_id, wrote)
        return _result('PUBLISHED', None if cleaned else 'STAGED_CLEANUP_PENDING', rid, wrote, recovered=True,
                       cleanup_pending=not cleaned, target=target, content=prepared['content'])
    finally:
        _close_locked(fd)


def discard_staged(project_root, request_id):
    project = os.path.abspath(project_root)
    with transaction.Pins() as pins:
        return _discard_pinned(project, request_id, _PinSet(pins))


def _discard_pinned(project, request_id, held):
    fd, early = _open_locked(project, request_id, held)
    if early:
        return early
    rid, wrote = request_id, []
    try:
        prepared = validate_evidence(_read_raw(_evidence_path(project, rid, 'prepared')), rid, 'prepared')
        state, _obj = _single_terminal(project, rid, prepared)
        if state == 'BAD':
            return _result('UNKNOWN', 'EVIDENCE_INCONSISTENT', rid, wrote)
        if state is None:
            return _result('REFUSED', 'NO_TERMINAL', rid, wrote)
        if state == 'published':
            return _result('REFUSED', 'TERMINAL_IS_PUBLISHED', rid, wrote)
        path = _evidence_path(project, rid, 'staged')
        if not os.path.lexists(path):
            return _result('REFUSED', 'STAGED_ABSENT', rid, wrote)
        info = file_info(path)
        if not _is_regular(info) or _runtime_problem(project):
            return _result('UNKNOWN', 'EVIDENCE_INCONSISTENT', rid, wrote)
        done = _delete_exact(path, identity_of(info))  # only the object just checked; otherwise it stays
        if done == 'CHANGED':
            return _result('UNKNOWN', 'EVIDENCE_INCONSISTENT', rid, wrote)
        if done != 'DELETED':
            return _result('REFUSED', 'EVIDENCE_WRITE_FAILED', rid, wrote)
        wrote.append({'path': _rel(project, path), 'op': 'delete', 'envelope': 'T7'})
        pending = os.path.lexists(path)
        return _result('DISCARDED', 'STAGED_CLEANUP_PENDING' if pending else None, rid, wrote,
                       terminal=state, cleanup_pending=pending)
    finally:
        _close_locked(fd)


# ---------------------------------------------------------------- status / observe (read only)
def _rid_status(project, rid, names):
    prepared = None
    problems = []
    if 'prepared.json' in names:
        prepared = validate_evidence(_read_raw(_evidence_path(project, rid, 'prepared')), rid, 'prepared')
    else:
        problems.append('PREPARED_MISSING')
    state, obj = _single_terminal(project, rid, prepared)
    if 'prepared.json' in names and prepared is None and not (state == 'unknown' and obj['reason'] == 'PREPARED_UNREADABLE'):
        problems.append('PREPARED_UNREADABLE')
    if state == 'BAD':
        problems.append('EVIDENCE_INCONSISTENT')
    staged = 'staged' in names
    return {'request_id': rid, 'files': sorted(names), 'staged_present': staged,
            'terminal': state if state not in (None, 'BAD') else None, 'consistent': not problems,
            'cleanup_pending': state == 'published' and staged, 'problems': problems}


def status(project_root, request_id=None):
    project = os.path.abspath(project_root)
    folder = _publish_dir(project)
    if _runtime_problem(project):
        return _result('UNSUPPORTED', 'RUNTIME_LINKED', request_id)
    groups, unexpected = {}, []
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            m = FILE_RE.fullmatch(name)
            if not m:
                unexpected.append(name)
                continue
            groups.setdefault(m.group(1), set()).add(m.group(2))
    if request_id is not None:
        if not RID_RE.fullmatch(request_id):
            raise ValueError('request_id must be 32 lowercase hex characters')
        groups = {request_id: groups.get(request_id, set())}
    items = [_rid_status(project, rid, names) for rid, names in sorted(groups.items())]
    return _result('STATUS', None, request_id, [], items=items, unexpected=unexpected)


def observe(project_root, target=None, inputs=None, request_id=None):
    project = os.path.abspath(project_root)
    ok, vol = volume_supported(project)
    out = {'volume': {'fs': vol['fs'], 'local': vol['local']}, 'entrypoint_sha256': entrypoint_sha256(), 'at': _now(),
           'parents_link_free': None, 'runtime_parents_ready': None, 'target': None, 'inputs': []}
    if not ok:
        return _result('UNSUPPORTED', 'UNSUPPORTED_FS', request_id, [], **out)
    if _runtime_problem(project):
        return _result('UNSUPPORTED', 'RUNTIME_LINKED', request_id, [], **out)
    out['runtime_parents_ready'] = runtime_parents_problem(project) is None  # the precondition publish enforces; a fact at this time only
    reason = None
    published = None
    if request_id is not None:
        st = status(project, request_id)['items'][0]
        out['evidence'] = st
        if not st['consistent']:
            reason = reason or 'EVIDENCE_INCONSISTENT'
        if st['terminal'] == 'published':
            published = validate_evidence(_read_raw(_evidence_path(project, request_id, 'published')), request_id, 'published')
            if target is None and published:
                target = published['target']
    if target is not None:
        if path_form_problem(target):
            return _result('UNSUPPORTED', 'PATH_UNSUPPORTED_FORM', request_id, [], **out)
        out['parents_link_free'] = _check_parents(project, target) is None
        if not out['parents_link_free']:
            reason = reason or 'PARENT_UNSAFE'
        path = _abs(project, target)
        t = {'exists': os.path.lexists(path), 'regular': False}
        if t['exists'] and out['parents_link_free']:
            info = file_info(path)
            t['regular'] = _is_regular(info)
            ident = identity_of(info)
            if ident:
                t['identity'] = ident
            elif t['regular']:
                reason = reason or 'IDENTITY_UNAVAILABLE'
            if t['regular']:
                try:
                    t['sha256'], t['size'] = _sha_file(path)
                except OSError:
                    reason = reason or 'OBSERVATION_UNAVAILABLE'
        if published is not None:
            t['matches_published'] = t.get('sha256') == published['content']['sha256'] and t.get('size') == published['content']['size']
        out['target'] = t
    for rel in inputs or []:
        entry = {'path': rel, 'sha256': None}
        if path_form_problem(rel):
            reason = reason or 'PATH_UNSUPPORTED_FORM'
        else:
            path = _abs(project, rel)
            if transaction.link_free(path, project) and _is_regular(file_info(path)):
                try:
                    entry['sha256'] = _sha_file(path)[0]
                except OSError:
                    pass
        out['inputs'].append(entry)
    return _result('UNSUPPORTED' if reason else 'OBSERVED', reason, request_id, [], **out)


# ---------------------------------------------------------------- CLI
def _project_default():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _status_of(code):
    return {0: 'success', 3: 'blocked', 4: 'blocked', 5: 'partial', 6: 'blocked'}.get(code, 'blocked')


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    want_json = '--result-json' in argv
    argv = [a for a in argv if a != '--result-json']
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--project', default=_project_default())
    ap = argparse.ArgumentParser(prog='publish_new.py', parents=[common])
    sub = ap.add_subparsers(dest='cmd')
    p = sub.add_parser('publish', parents=[common])
    p.add_argument('--request', required=True)
    p.add_argument('--staged', required=True)
    p.add_argument('--rid')
    o =sub.add_parser('observe', parents=[common])
    o.add_argument('--target')
    o.add_argument('--input', action='append', default=[])
    o.add_argument('--rid')
    s = sub.add_parser('status', parents=[common])
    s.add_argument('rid', nargs='?')
    r = sub.add_parser('recover', parents=[common])
    r.add_argument('rid')
    d = sub.add_parser('discard-staged', parents=[common])
    d.add_argument('rid')
    try:
        args = ap.parse_args(argv)
    except SystemExit:
        if want_json:
            emit(make('blocked', code=2, message='usage error', changes=False))
        return 2
    try:
        if args.cmd == 'publish':
            if os.path.getsize(args.staged) > MAX_STAGED_BYTES:
                res = _result('REFUSED', 'STAGED_TOO_LARGE')
            else:
                with io.open(args.request, 'rb') as f:
                    try:
                        request = cj_loads(f.read())
                    except CJError:
                        request = None
                with open(args.staged, 'rb') as f:
                    data = f.read()
                res = (publish(args.project, request, data, request_id=args.rid) if request is not None
                       else _result('REFUSED', 'REQUEST_INVALID'))
        elif args.cmd == 'observe':
            res = observe(args.project, target=args.target, inputs=args.input, request_id=args.rid)
        elif args.cmd == 'status':
            res = status(args.project, args.rid)
        elif args.cmd == 'recover':
            res = recover(args.project, args.rid)
        elif args.cmd == 'discard-staged':
            res = discard_staged(args.project, args.rid)
        else:
            ap.print_usage()
            if want_json:
                emit(make('blocked', code=2, message='usage error', changes=False))
            return 2
    except (ValueError, TypeError, OSError) as e:
        print('Lỗi cách dùng / usage error: %s' % e, file=sys.stderr)
        if want_json:
            emit(make('blocked', code=2, message=str(e), changes=False))
        return 2
    code = EXIT[res['outcome']]
    print(json.dumps(res, ensure_ascii=False, indent=2, sort_keys=True))
    if want_json:
        emit(make(_status_of(code), code=code, message='%s %s' % (res['outcome'], res['reason'] or ''),
                  changes=bool(res['wrote']), files=[{'path': w['path'], 'action': w['op']} for w in res['wrote']],
                  outcome=res['outcome'], reason=res['reason'], request_id=res['request_id']))
    return code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
