#!/usr/bin/env python3
"""Cập nhật ghi chú vận hành STATE/HANDOFF có sẵn (protocol P-CTX1, prototype). / Update an existing operational-context file.

Dùng / Usage:
  python tools/context_update.py --project DIR --target {state,handoff} --content FILE --expected sha256:HEX [--apply] [--result-json]

Mặc định chỉ xem trước (đọc, không ghi); --apply mới ghi. Without --apply nothing is written.
Kết quả / results: WRITTEN, UNCHANGED, CONFLICT, ERROR, UNKNOWN (preview: PREVIEW). Mã thoát / exit codes: 0 WRITTEN/UNCHANGED/PREVIEW;
3 CONFLICT; 4 ERROR; 5 UNKNOWN; 2 usage error.

Phạm vi hẹp / narrow scope: đúng `.agent/STATE.md` hoặc `.agent/HANDOFF.md`, một file mỗi lần gọi, file phải có sẵn (init tạo; thiếu thì từ chối).
`--expected` là SHA256 của chính bytes đã đọc; nội dung đổi từ lúc đọc thì CONFLICT, không ghi. Bytes mới được ghi nguyên văn, công cụ không sửa
hay chuẩn hóa văn bản. STATE phải giữ đúng tám heading chuẩn, có dòng trống sau mỗi heading, tối đa 60 dòng; HANDOFF không áp giới hạn dòng.
Exactly one existing file per call; the new bytes are written verbatim, the tool never edits or normalizes the text.

Windows + local NTFS only (còn lại là UNSUPPORTED_FS, chưa ghi gì). Root, `.agent` và `.agent/runtime` phải có sẵn, là thư mục thường (không liên kết)
và được giữ handle trước mọi probe/ghi; thiếu thì từ chối, công cụ không tạo hộ. Ghi bằng tools/transaction.py với prune=False: không xóa journal của
giao dịch khác, không xóa thư mục runtime; chỉ dọn staging/backup của chính giao dịch này. Không tự resume/rollback.
Hash là bảo vệ single-writer hợp tác (ADVISORY), không phải CAS của filesystem và không chặn mọi editor; một file mỗi lần gọi nên không có atomic hai file.
Context không phải grant, policy, review hay nghiệm thu; công cụ không kiểm quyền của người gọi (actor phải kiểm group grant trước khi gọi).
Journal của mỗi lần ghi còn lại trong .agent/runtime/transactions/ (không tự dọn).
"""
import argparse
import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import publish_new as _pn  # noqa: E402  (platform/pin helpers only; its own pin is P-CN1's, not this tool's)
import transaction  # noqa: E402
from result_schema import emit, make  # noqa: E402

PROTOCOL = 'P-CTX1'
PROTOCOL_VERSION = 1
PLATFORM = 'windows-ntfs-local'
TOOL_NAME = 'context_update'
TARGETS = {'state': '.agent/STATE.md', 'handoff': '.agent/HANDOFF.md'}
STATE_HEADINGS = ('Goal', 'Current phase', 'Completed', 'Current artifact', 'Open items', 'Waiting on user', 'Decisions', 'Next milestone')
STATE_MAX_LINES = 60
MAX_BYTES = 8 * 1024 * 1024
HEX_RE = re.compile(r'^(?:sha256:)?([0-9a-f]{64})$')
EXIT = {'WRITTEN': 0, 'UNCHANGED': 0, 'PREVIEW': 0, 'CONFLICT': 3, 'ERROR': 4, 'UNKNOWN': 5}
STATUS = {'WRITTEN': 'success', 'UNCHANGED': 'success', 'PREVIEW': 'preview', 'CONFLICT': 'blocked', 'ERROR': 'error', 'UNKNOWN': 'partial'}
LANG = 'vi'
_HOOK = None  # TEST ONLY: _HOOK(point, info), point = pinned (apply, after the chain is pinned, before the target is read)


def L(vi, en): return en if LANG == 'en' else vi


def _hook(point, info):
    if _HOOK is not None:
        _HOOK(point, info)


def sha_hex(data):
    return hashlib.sha256(data).hexdigest()


def _result(result, reason=None, rel=None, changes=False, txid=None, detail=None, mode='APPLY', **extra):
    """Envelope result-v1 plus: result, reason, mode, target, txid, detail. `changes` is True/False only when proven, else None."""
    msg = {'WRITTEN': L('Đã ghi %s.', 'Wrote %s.'), 'UNCHANGED': L('%s đã đúng nội dung này; chưa ghi gì.', '%s already has this content; nothing written.'),
           'PREVIEW': L('Xem trước %s; chưa ghi gì.', 'Preview of %s; nothing written.'),
           'CONFLICT': L('%s đã đổi so với bản đã đọc; chưa ghi gì.', '%s differs from the bytes that were read; nothing written.'),
           'ERROR': L('Từ chối hoặc lỗi với %s', 'Refused or failed for %s'),
           'UNKNOWN': L('Chưa xác định được kết quả ghi %s.', 'Could not establish the outcome of writing %s.')}[result] % (rel or '-')
    if reason:
        msg += ' [' + reason + ']'
    out = make(STATUS[result], code=EXIT[result], message=msg, changes=changes, **extra)
    out.update(result=result, reason=reason, mode=mode, target=rel, txid=txid, detail=detail)
    return out


def state_problem(text):
    """None when text keeps the STATE frame, else a short code: STATE_TOO_LONG, STATE_HEADINGS or STATE_BLANK_AFTER_HEADING."""
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    lines = [ln[:-1] if ln.endswith('\r') else ln for ln in lines]
    if len(lines) > STATE_MAX_LINES:
        return 'STATE_TOO_LONG'
    at = [i for i, ln in enumerate(lines) if ln.startswith('## ')]
    if [lines[i][3:] for i in at] != list(STATE_HEADINGS):
        return 'STATE_HEADINGS'
    for i in at:
        if i + 1 >= len(lines) or lines[i + 1].strip():
            return 'STATE_BLANK_AFTER_HEADING'
    return None


def content_problem(target, content):
    """None when content may be written to target as given, else a reason code. Never alters the bytes."""
    if not content:
        return 'CONTENT_EMPTY'
    if len(content) > MAX_BYTES:
        return 'CONTENT_TOO_LARGE'
    if b'\x00' in content:
        return 'CONTENT_NOT_TEXT'
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        return 'CONTENT_NOT_UTF8'
    return state_problem(text) if target == 'state' else None


def _args(project_root, target, content, expected_before):
    """(rel, content bytes, expected hex, None) or (None, None, None, reason). Pure: no filesystem access."""
    if type(project_root) is not str or not project_root:
        return None, None, None, 'PROJECT_INVALID'
    if type(target) is not str or target not in TARGETS:
        return None, None, None, 'TARGET_INVALID'
    if not isinstance(content, (bytes, bytearray)):
        return None, None, None, 'CONTENT_INVALID'
    m = HEX_RE.match(expected_before) if type(expected_before) is str else None
    if not m:
        return None, None, None, 'EXPECTED_BEFORE_INVALID'
    content = bytes(content)
    problem = content_problem(target, content)
    if problem:
        return None, None, None, problem
    return TARGETS[target], content, m.group(1), None


def _abs(project, rel):
    return os.path.join(project, *rel.split('/'))


def _read_target(project, rel):
    """(bytes, None) or (None, reason). The target must be an existing regular file that is not (and is not reached through) a link."""
    path = _abs(project, rel)
    if not os.path.lexists(path):
        return None, 'TARGET_MISSING'
    if not _pn._is_regular(_pn.file_info(path)) or not transaction.link_free(path, project):
        return None, 'TARGET_UNSAFE'
    try:
        with open(path, 'rb') as f:
            data = f.read(MAX_BYTES + 1)
    except OSError:
        return None, 'TARGET_UNREADABLE'
    if len(data) > MAX_BYTES:
        return None, 'TARGET_TOO_LARGE'
    return data, None


def _plan(rel, current, content):
    return [{'path': rel, 'action': 'replace', 'before': 'sha256:' + sha_hex(current), 'after': 'sha256:' + sha_hex(content),
             'bytes_before': len(current), 'bytes_after': len(content)}]


def _decide(rel, current, content, expected, mode):
    """Result for a stale expected hash or identical content, else None. Same order for preview and apply."""
    if sha_hex(current) != expected:
        return _result('CONFLICT', 'EXPECTED_BEFORE_MISMATCH', rel, False, mode=mode,
                       next_actions=[L('Đọc lại file, soạn lại trên bản hiện tại, rồi gọi lại với hash mới.',
                                       'Read the file again, redo the edit on the current bytes, then call again with the new hash.')])
    if current == content:
        return _result('UNCHANGED', None, rel, False, mode=mode)
    return None


def _platform_problem(project):
    if os.name != 'nt':
        return 'UNSUPPORTED_FS'
    if _pn._root_problem(project):
        return 'ROOT_LINKED'
    if not _pn.volume_supported(project)[0]:
        return 'UNSUPPORTED_FS'
    return None


def _parents_error(rel, state, mode='APPLY'):
    reason = {'MISSING': 'RUNTIME_PARENT_MISSING', 'NO_PIN': 'PIN_UNAVAILABLE'}.get(state, 'RUNTIME_LINKED')
    return _result('ERROR', reason, rel, False, mode=mode)


def preview(project_root, target, content, *, expected_before):
    """Read-only plan: what update() would do. Never writes, never takes a pin, never reports WRITTEN."""
    rel, content, expected, bad = _args(project_root, target, content, expected_before)
    if bad:
        return _result('ERROR', bad, TARGETS.get(target) if type(target) is str else None, False, mode='PREVIEW')
    project = os.path.abspath(project_root)
    problem = _platform_problem(project) or _pn.runtime_parents_problem(project)
    if problem:
        return _result('ERROR', problem, rel, False, mode='PREVIEW')
    current, bad = _read_target(project, rel)
    if bad:
        return _result('ERROR', bad, rel, False, mode='PREVIEW', **_missing_hint(bad))
    early = _decide(rel, current, content, expected, 'PREVIEW')
    if early:
        return early
    return _result('PREVIEW', None, rel, False, mode='PREVIEW', planned_changes=_plan(rel, current, content),
                   next_actions=[L('Thêm --apply để ghi.', 'Add --apply to write.')])


def _missing_hint(reason):
    if reason == 'TARGET_MISSING':
        return {'next_actions': [L('Khởi tạo project bằng tools/init_project.py; công cụ này không tạo file.',
                                   'Initialise the project with tools/init_project.py; this tool never creates the file.')]}
    return {}


def update(project_root, target, content, *, expected_before):
    """Replace one existing context file (target 'state' or 'handoff') with `content` if it still has the bytes whose SHA256 is expected_before."""
    rel, content, expected, bad = _args(project_root, target, content, expected_before)
    if bad:
        return _result('ERROR', bad, TARGETS.get(target) if type(target) is str else None, False)
    project = os.path.abspath(project_root)
    problem = _platform_problem(project)
    if problem:
        return _result('ERROR', problem, rel, False)
    with transaction.Pins() as pins:
        held = _pn._PinSet(pins)
        # root -> .agent -> .agent/runtime must already exist and be pinned before the first probe, temp file or write; none is created here
        state = _pn._walk(project, _pn.RUNTIME_PARENTS, held, [], 'C0', False, required=len(_pn.RUNTIME_PARENTS))
        if state:
            return _parents_error(rel, state)
        _hook('pinned', {'project': project, 'target': rel})
        problem = _pn.runtime_parents_problem(project)
        if problem:
            return _result('ERROR', problem, rel, False)
        current, bad = _read_target(project, rel)
        if bad:
            return _result('ERROR', bad, rel, False, **_missing_hint(bad))
        early = _decide(rel, current, content, expected, 'APPLY')
        if early:
            return early
        try:
            pending = transaction.incomplete(project, strict=True)
        except (OSError, ValueError, TypeError, AttributeError, transaction.TransactionError) as exc:
            return _result('ERROR', 'TRANSACTION_STATUS_UNREADABLE', rel, False, detail=str(exc))
        if pending:
            return _result('ERROR', 'TRANSACTION_UNFINISHED', rel, False, detail=pending[0]['id'],
                           next_actions=[L('Có giao dịch file chưa xong; chạy tools/transaction.py status rồi resume hoặc rollback.',
                                           'A file transaction is unfinished; run tools/transaction.py status, then resume or rollback.')])
        return _write(project, rel, current, content, expected)


def _write(project, rel, current, content, expected):
    tx = transaction.Transaction(project, 'context-update', prune=False)
    before, after = sha_hex(current), sha_hex(content)
    stamp = {'before_sha256': 'sha256:' + before, 'after_sha256': 'sha256:' + after}
    try:  # planning only reads: a failure here proves nothing was written
        planned = tx.add(rel, content, expected_before=expected)
    except transaction.TransactionError as exc:  # stale hash, or a path that now passes through a link
        if _file_sha(_abs(project, rel)) != expected:
            return _result('CONFLICT', 'EXPECTED_BEFORE_MISMATCH', rel, False, detail=str(exc), **stamp)
        return _result('ERROR', 'TARGET_UNSAFE', rel, False, detail=str(exc), **stamp)
    except OSError as exc:
        return _result('ERROR', 'TARGET_UNREADABLE', rel, False, detail=str(exc), **stamp)
    if planned is None:
        return _result('UNCHANGED', None, rel, False)  # became identical since the read: no journal, nothing staged
    try:
        tx.run()
    except Exception as exc:  # the outcome is decided from the file itself, never from the exception alone
        return _after_failure(project, rel, tx, before, after, exc, stamp)
    finally:
        tx.close()
    seen = _file_sha(_abs(project, rel))
    if seen == after:
        return _result('WRITTEN', None, rel, True, txid=tx.txid, files=[{'path': rel, 'action': 'replaced'}], protection=tx.protection, **stamp)
    return _result('UNKNOWN', 'POST_WRITE_VERIFY_MISMATCH', rel, None, txid=tx.txid, detail=tx.txid, protection=tx.protection, **stamp,
                   next_actions=[L('Kiểm file thực; có thể một trình khác vừa sửa nó.', 'Check the real file; another program may have just changed it.')])


def _file_sha(path):
    try:
        return transaction.sha_file(path)
    except OSError:
        return None


def _after_failure(project, rel, tx, before, after, exc, stamp):
    """WRITTEN only if the file now has the new bytes; changes=False only if it still has the old bytes; otherwise UNKNOWN."""
    seen = _file_sha(_abs(project, rel))
    unfinished = [L('Có thể còn giao dịch chưa xong: python tools/transaction.py status.', 'A transaction may be unfinished: python tools/transaction.py status.')]
    detail = '%s: %s' % (type(exc).__name__, exc)
    if seen == after:
        return _result('WRITTEN', 'COMPLETION_ERROR', rel, True, txid=tx.txid, detail=detail, files=[{'path': rel, 'action': 'replaced'}],
                       next_actions=unfinished, **stamp)
    if isinstance(exc, transaction.CommitConflict) and [o.get('state') for o in tx.journal['ops']] == ['skipped_conflict']:
        # commit marks skipped_conflict before it gives up and never after os.replace, so the file is not ours to report as written
        return _result('CONFLICT', 'CHANGED_AFTER_PLANNING', rel, False, txid=tx.txid, detail=detail, next_actions=unfinished, **stamp)
    if seen == before:
        reason = 'REPLACE_REFUSED' if isinstance(exc, transaction.TransactionError) else 'WRITE_FAILED'
        return _result('ERROR', reason, rel, False, txid=tx.txid, detail=detail, next_actions=unfinished, **stamp)
    return _result('UNKNOWN', 'OUTCOME_UNPROVEN', rel, None, txid=tx.txid, detail=detail, next_actions=unfinished, **stamp)


def _cli(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--project', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--target', required=True, choices=sorted(TARGETS))
    ap.add_argument('--content', required=True, help='file chứa bytes mới / file holding the new bytes')
    ap.add_argument('--expected', required=True, help='sha256:HEX của bytes đã đọc / SHA256 of the bytes that were read')
    ap.add_argument('--apply', action='store_true', help='ghi thật; mặc định chỉ xem trước / write for real; the default is a preview')
    ap.add_argument('--result-json', action='store_true')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    a = ap.parse_args(argv)
    LANG = a.lang
    if not a.expected.startswith('sha256:'):
        ap.error('--expected must look like sha256:<64 hex>')
    try:
        with open(a.content, 'rb') as f:
            data = f.read(MAX_BYTES + 1)
    except OSError as e:
        ap.error('cannot read --content: %s' % e)
    run = update if a.apply else preview
    res = run(a.project, a.target, data, expected_before=a.expected)
    if a.result_json:
        emit(res)
    else:
        print(res['message'])
        for c in res.get('planned_changes', []):
            print('  - %s %s: %s -> %s' % (c['action'], c['path'], c['before'][:19], c['after'][:19]))
        for n in res['next_actions']:
            print('  ' + n)
    return res['code']


if __name__ == '__main__':
    sys.exit(_cli(sys.argv[1:]))
