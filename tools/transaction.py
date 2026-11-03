#!/usr/bin/env python3
"""Giao dịch file có nhật ký: ghi an toàn và phục hồi khi gián đoạn. / Journaled file transactions with recovery.

Dùng / Usage:
  python tools/transaction.py status [--project DIR] [--result-json]
  python tools/transaction.py resume <txid> [--project DIR] [--result-json]
  python tools/transaction.py rollback <txid> [--project DIR] [--result-json]

Mã thoát: status 0 không có giao dịch dở, 1 có; resume/rollback 0 hoàn tất, 1 còn việc hoặc xung đột, 2 lỗi dùng.
Exit codes: status 0 = nothing unfinished, 1 = unfinished exists; resume/rollback 0 = done, 1 = pending or conflict, 2 = usage error.

Dữ liệu chạy nằm trong <project>/.agent/runtime/transactions/<txid>/ (không vào MANIFEST/ZIP).
Only journal.json is kept after commit; staging and backups are deleted.
Nhật ký không chứa nội dung file, tên người hay đường dẫn tuyệt đối / the journal stores no contents, names or absolute paths.

TEST ONLY / CHỈ DÙNG KIỂM THỬ: biến môi trường LOCAL_AGENT_WORKSPACE_TEST_FAULT, ví dụ / e.g.
  stage:N   raise OSError sau khi đã stage N file / after staging N files
  backup:N  raise OSError sau khi đã sao lưu N file / after backing up N files
  commit:N  raise OSError sau khi đã commit N thao tác / after N committed ops
  kill:N    os._exit(70) sau khi đã commit N thao tác / after N committed ops
Không đặt biến này khi dùng thật. / Never set this in real use.

Liên kết và ranh giới kiểm→ghi / Links and the check-to-write boundary:
  - Thư mục runtime và mọi đích ghi phải không đi qua symlink/junction (link_free); vi phạm thì chưa ghi gì.
    Runtime and every write target must not pass through a symlink or junction; a violation writes nothing.
  - Trên Windows, giữ mở handle thư mục (không FILE_SHARE_DELETE) chặn đổi tên/xóa thư mục đó và mọi thư mục cha, nên không thể thay
    nó bằng junction giữa lúc kiểm và lúc ghi. Nơi không giữ được handle, chỉ kiểm lại sát trước khi ghi (thu hẹp, không đóng cửa sổ).
    On Windows an open folder handle without FILE_SHARE_DELETE blocks renaming or deleting that folder and its parents, so it cannot be
    swapped for a junction between check and write. Elsewhere only a re-check right before the write narrows the window, it does not close it.
  - Hash lúc đọc (expected_before) chỉ phát hiện nội dung đổi, không thay cho kiểm ranh giới: đích ngoài có cùng bytes vẫn khớp hash.
    The hash taken at read time detects changed content only; an outside target with identical bytes would match it.
"""
import argparse, contextlib, datetime, hashlib, io, json, os, shutil, sys, uuid
from result_schema import emit, make

SCHEMA = 'local-agent-workspace/transaction-v1'
CREATE_SCHEMA = 'local-agent-workspace/transaction-v2'
RUNTIME_DIR = '.agent/runtime'
KEEP_JOURNALS = 20
MARGIN = 1024 * 1024
FAULT_ENV = 'LOCAL_AGENT_WORKSPACE_TEST_FAULT'
INCOMPLETE = ('prepared', 'committing')  # rollback_partial là trạng thái kết thúc, không chặn / terminal, does not block
LANG = 'vi'
_UNSET = object()
PIN_ENABLED = True  # chỉ test đặt False để thử nhánh không giữ handle / tests set False to exercise the no-handle path
_HOOK = None  # TEST ONLY: _HOOK(point, path), point = stage|backup|commit|resume|rollback; gọi sau khi giữ thư mục, trước khi băm/ghi / called once the folders are held, before hashing or writing

def L(vi, en): return en if LANG == 'en' else vi

class TransactionError(Exception):
    """Lỗi trước khi ghi file người dùng: chưa ghi gì / failed before any user file was written."""
    pass

class CommitConflict(OSError):
    """Lỗi trong lúc commit: một phần đã ghi, giao dịch còn dở / failed during commit: partly written, transaction open."""
    pass

def _fault(kind):
    """Trả về số N nếu biến kiểm thử khớp với kind, không thì None. / N if the test fault matches kind."""
    spec = os.environ.get(FAULT_ENV, '')
    if ':' not in spec:
        return None
    k, _, n = spec.partition(':')
    if k != kind:
        return None
    try:
        return int(n)
    except ValueError:
        return None

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha_file(path):
    """Hash nội dung thô hoặc None nếu không có file. / Raw content hash, or None when absent."""
    if not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        return sha_bytes(f.read())

def _now():
    return datetime.datetime.now().isoformat(timespec='seconds')

def runtime_root(project):
    return os.path.join(project, *RUNTIME_DIR.split('/'))

def link_free(path, root):
    """True when no component of path below root is a symlink or junction (realpath equals the plain path)."""
    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    expected = os.path.normpath(os.path.join(os.path.realpath(root), rel))
    return os.path.normcase(os.path.realpath(path)) == os.path.normcase(expected)

def guard(project, *paths):
    """Raise TransactionError, before anything is written, when a path passes through a link. / Chặn đường dẫn đi qua liên kết."""
    for path in paths:
        if not link_free(path, project):
            rel = os.path.relpath(os.path.abspath(path), os.path.abspath(project)).replace(os.sep, '/')
            raise TransactionError(L('Đường dẫn ghi hoặc runtime là, hoặc đi qua, liên kết (symlink/junction); chưa ghi gì: %s',
                                     'A write or runtime path is, or passes through, a link (symlink/junction); nothing was written: %s') % rel)

def runtime_problem(project):
    """None when the runtime folder is plain; otherwise the message. / Thông báo nếu runtime đi qua liên kết."""
    project = os.path.abspath(project)
    try:
        guard(project, os.path.join(runtime_root(project), 'transactions'))
    except TransactionError as e:
        return str(e)
    return None

def _rmtree(project, path):
    """rmtree only inside the project: never delete through a link. / Không xóa qua liên kết."""
    if link_free(path, project):
        shutil.rmtree(path, ignore_errors=True)

_k32 = None

def _open_dir_handle(path):
    """Windows: open a folder handle that blocks renaming or deleting it (and its parents) but allows writing inside."""
    global _k32
    import ctypes
    from ctypes import wintypes
    if _k32 is None:
        _k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        _k32.CreateFileW.restype = wintypes.HANDLE
        _k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
                                     wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        _k32.CloseHandle.argtypes = [wintypes.HANDLE]
    # FILE_LIST_DIRECTORY|FILE_READ_ATTRIBUTES; share READ|WRITE only (no DELETE); OPEN_EXISTING; FILE_FLAG_BACKUP_SEMANTICS
    h = _k32.CreateFileW(path, 0x1 | 0x80, 0x1 | 0x2, None, 3, 0x02000000, None)
    return None if h in (None, ctypes.c_void_p(-1).value) else h

class Pins:
    """Folder handles held for the length of a write. hold() is False when the OS cannot give one; callers still re-check."""

    def __init__(self):
        self._handles = []

    def hold(self, path):
        if not PIN_ENABLED or os.name != 'nt':
            return False
        try:
            h = _open_dir_handle(path)
        except Exception:
            return False
        if h is None:
            return False
        self._handles.append(h)
        return True

    def close(self):
        while self._handles:
            try:
                _k32.CloseHandle(self._handles.pop())
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False

class _Held:
    """Handed to the caller inside held(): call it to re-check, read .protected for the level of protection."""

    def __init__(self, project, files):
        self._project, self._files, self.protected = project, files, False

    def __call__(self):
        guard(self._project, *self._files)

@contextlib.contextmanager
def held(project, *files, create=(), point=None):
    """Protect the files about to be read, hashed, written, replaced or removed (sources and targets alike).

    Order: check the full path of every file -> create the listed parents -> hold every parent folder -> check again ->
    test hook (point, first file) -> caller works and calls the yielded recheck() right before the write.
    .protected is True only when every existing parent folder is really held (Windows); otherwise only re-checking protects.
    """
    files = [os.path.abspath(f) for f in files]
    guard(project, *files)
    for f in create:
        os.makedirs(os.path.dirname(os.path.abspath(f)), exist_ok=True)
    with Pins() as pins:
        every = True
        for folder in sorted({os.path.dirname(f) for f in files}):
            if os.path.isdir(folder):
                every = pins.hold(folder) and every
        check = _Held(project, files)
        check.protected = every
        check()
        if point and _HOOK is not None:
            _HOOK(point, files[0])
        yield check

def txdir(project, txid):
    return os.path.join(runtime_root(project), 'transactions', txid)

def _write_json_atomic(project, path, data):
    tmp = path + '.tmp'
    with held(project, tmp, path, create=(tmp,)) as check:  # cả file tạm và file nhật ký / the temp file and the journal leaf
        with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            f.flush()
            os.fsync(f.fileno())
        check()
        os.replace(tmp, path)

def probe_writable(project):
    """Probe this transaction's temporary file, including deletion; never bypass a failed probe."""
    d = runtime_root(project)
    p = os.path.join(d, '.probe-' + uuid.uuid4().hex)
    phase = 'guard'
    try:
        guard(project, d)
        phase = 'mkdir'
        os.makedirs(d, exist_ok=True)
        phase = 'create'
        with open(p, 'xb') as f:
            phase = 'write'
            f.write(b'probe')
            phase = 'close'
        phase = 'remove'
        os.remove(p)
    except OSError as exc:
        # Put the useful facts first: execution_profile bounds exception details.
        rel = os.path.relpath(p, project).replace('\\', '/')
        detail = 'WRITE_PROBE_FAILED phase=%s errno=%s winerror=%s path=%s' % (
            phase, exc.errno, getattr(exc, 'winerror', None), rel)
        detail += L('; file người dùng chưa ghi; kiểm quyền thao tác file tạm của host.',
                    '; user files not written; check host permissions for transaction temporaries.')
        raise OSError(exc.errno, detail) from exc

class Transaction:
    """Một lần ghi có nhật ký. Dùng: plan -> stage -> backup -> commit. / One journaled write.

    ops: [{'path', 'action', 'before', 'after', 'size', 'state'}]; content is held in memory only
    until staged, never written to the journal.
    """

    def __init__(self, project, operation, txid=None, *, prune=True, create_only=False):
        # prune=False (owner opt-in, P-CTX1): never delete another transaction's journal and never remove the runtime folders; the
        # transaction still cleans its own staging/backup. Default True keeps the long-standing behaviour.
        self._prune = bool(prune)
        self.project = os.path.abspath(project)
        self.txid = txid or (datetime.datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
        self.dir = txdir(self.project, self.txid)
        self.stage_dir = os.path.join(self.dir, 'staging')
        self.backup_dir = os.path.join(self.dir, 'backup')
        self.journal = {'schema': CREATE_SCHEMA if create_only else SCHEMA, 'id': self.txid, 'operation': operation, 'status': 'prepared',
                        'created': _now(), 'updated': _now(), 'ops': []}
        self._content = {}
        self._pins = Pins()
        self._prot = []  # mức bảo vệ của từng vùng ghi vào project / protection level of each write into the project

    @property
    def protection(self):
        """'held' when every write into the project had its folders held open (Windows), else 'recheck_only'; 'none' before any."""
        if not self._prot:
            return 'none'
        return 'held' if all(self._prot) else 'recheck_only'

    # ---- planning / lập kế hoạch
    def add(self, rel, data, action='write', expected_before=_UNSET):
        """Plan a write; expected_before binds it to a hash captured when the caller read the file."""
        if rel.startswith('/') or '..' in rel.split('/') or '\\' in rel:
            raise TransactionError('Invalid relative path / Đường dẫn không hợp lệ: ' + rel)
        dst = os.path.join(self.project, *rel.split('/'))
        guard(self.project, os.path.dirname(dst))
        before = sha_file(dst)
        if action == 'create' and self.journal['schema'] == CREATE_SCHEMA:
            if any(o['action'] != 'create' for o in self.journal['ops']):
                raise TransactionError('Create operations must precede replacements')
            if before is not None or os.path.lexists(dst):
                raise TransactionError('Create target already exists: ' + rel)
        if expected_before is not _UNSET and before != expected_before:
            raise TransactionError('File changed since it was read / File đã đổi từ lúc đọc: ' + rel)
        if before is not None and before == sha_bytes(data):
            return None  # đã đúng nội dung: không cần thao tác / already identical: no op needed
        op = {'path': rel, 'action': action, 'before': before, 'after': sha_bytes(data),
              'size': len(data), 'state': 'pending'}
        self.journal['ops'].append(op)
        self._content[rel] = data
        return op

    def _save(self):
        self.journal['updated'] = _now()
        _write_json_atomic(self.project, os.path.join(self.dir, 'journal.json'), self.journal)

    def _set_state(self, op, state):
        op['state'] = state
        self._save()

    def preflight(self):
        """Kiểm trước: quyền ghi, dung lượng, file đang đổi. Không ghi file người dùng. / Checks before any write."""
        problems = []
        try:
            probe_writable(self.project)
        except OSError as e:
            problems.append(L('Không ghi được vào thư mục project: %s', 'Cannot write to the project folder: %s') % e)
        need = sum(o['size'] for o in self.journal['ops']) * 2 + MARGIN
        try:
            free = shutil.disk_usage(runtime_root(self.project)).free
            if free < need:
                problems.append(L('Thiếu dung lượng: cần khoảng %d byte, còn %d.', 'Not enough disk space: need about %d bytes, %d free.') % (need, free))
        except OSError as e:
            problems.append(L('Không kiểm được dung lượng: %s', 'Cannot check disk space: %s') % e)
        for op in self.journal['ops']:
            dst = os.path.join(self.project, *op['path'].split('/'))
            if os.path.isdir(dst):
                problems.append(L('Đường dẫn đích là thư mục: %s', 'Target is a folder: %s') % op['path'])
            if self.journal['schema'] == CREATE_SCHEMA and op['before'] is not None:
                try:
                    fd = os.open(dst, os.O_RDWR)
                    os.close(fd)
                except OSError as e:
                    problems.append('Cannot open the existing target for writing: %s: %s' % (op['path'], e))
        return problems

    # ---- execution / thực thi
    def begin(self):
        _validate_create_journal(self.journal)
        guard(self.project, self.dir)
        os.makedirs(self.stage_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        self._pins.hold(self.dir)  # runtime của giao dịch không bị thay bằng liên kết khi đang chạy / keeps the runtime from being swapped
        guard(self.project, self.dir)
        self._save()

    def close(self):
        self._pins.close()

    def stage(self):
        n = 0
        limit = _fault('stage')
        for op in self.journal['ops']:
            p = os.path.join(self.stage_dir, *op['path'].split('/'))
            with held(self.project, p, create=(p,), point='stage') as check:
                check()
                with open(p, 'wb') as f:
                    f.write(self._content[op['path']])
                    f.flush(); os.fsync(f.fileno())
                if sha_file(p) != op['after']:
                    raise TransactionError(L('Hash bản staging không khớp: %s', 'Staged hash mismatch: %s') % op['path'])
            n += 1
            if limit is not None and n >= limit:
                raise OSError('synthetic fault: stage')

    def backup(self):
        n = 0
        limit = _fault('backup')
        for op in self.journal['ops']:
            if op['before'] is None:
                continue
            src = os.path.join(self.project, *op['path'].split('/'))
            dst = os.path.join(self.backup_dir, *op['path'].split('/'))
            with held(self.project, src, dst, create=(dst,), point='backup') as check:
                check()
                shutil.copyfile(src, dst)
                if sha_file(dst) != op['before']:
                    raise TransactionError(L('Hash bản sao lưu không khớp: %s', 'Backup hash mismatch: %s') % op['path'])
            n += 1
            if limit is not None and n >= limit:
                raise OSError('synthetic fault: backup')

    def commit(self):
        self.journal['status'] = 'committing'
        self._save()
        limit = _fault('commit')
        kill = _fault('kill')
        done = 0
        for op in self.journal['ops']:
            if op['state'] != 'pending':
                continue
            if self.journal['schema'] == CREATE_SCHEMA:
                _check_created_dependencies(self.project, self.dir, self.journal, op)
            dst = os.path.join(self.project, *op['path'].split('/'))
            staged = os.path.join(self.stage_dir, *op['path'].split('/'))
            try:
                with held(self.project, dst, staged, create=(dst,), point='commit') as recheck:
                    self._prot.append(recheck.protected)
                    recheck()  # trước khi băm / before hashing
                    if self.journal['schema'] == CREATE_SCHEMA:
                        _check_created_dependencies(self.project, self.dir, self.journal, op)
                    if sha_file(dst) != op['before']:
                        self._set_state(op, 'skipped_conflict')
                        raise CommitConflict(L('File đã đổi sau khi lập kế hoạch: %s', 'File changed after planning: %s') % op['path'])
                    if sha_file(staged) != op['after']:
                        self._set_state(op, 'skipped_conflict')
                        raise CommitConflict(L('Bản staging không còn đúng: %s', 'The staged copy is no longer valid: %s') % op['path'])
                    recheck()  # sát trước khi ghi / right before the write
                    if self.journal['schema'] == CREATE_SCHEMA:
                        _check_created_dependencies(self.project, self.dir, self.journal, op)
                    try:
                        if op['action'] == 'create' and self.journal['schema'] == CREATE_SCHEMA:
                            # Atomic no-clobber. Keep the staged name as ownership evidence until cleanup.
                            os.link(staged, dst)
                        else:
                            os.replace(staged, dst)
                    except OSError as e:
                        if any(o['state'] == 'done' for o in self.journal['ops']):
                            raise
                        # chưa ghi file nào (đang mở trong ứng dụng khác, chỉ đọc, bị khóa): hủy sạch, không để việc dở
                        # nothing written yet (open in another app, read-only, locked): abandon cleanly, no open work
                        self.abandon()
                        raise TransactionError(L('Không thay được file %s (đang mở trong ứng dụng khác, chỉ đọc hoặc bị khóa?): %s. Chưa ghi gì; đóng ứng dụng rồi chạy lại.',
                                                 'Could not replace %s (open in another application, read-only or locked?): %s. Nothing was written; close it and run again.') % (op['path'], e))
            except TransactionError as e:
                if self.journal['status'] == 'rolled_back':
                    raise
                self._set_state(op, 'skipped_conflict')  # đích đổi thành liên kết: từ chối, không ghi / target became a link: refused
                raise CommitConflict(str(e))
            self._set_state(op, 'done')
            done += 1
            if limit is not None and done >= limit:
                raise OSError('synthetic fault: commit')
            if kill is not None and done >= kill:
                os._exit(70)
        self.journal['status'] = 'committed'
        self.journal['protection'] = self.protection
        self._save()
        self._cleanup()

    def _cleanup(self):
        for d in (self.stage_dir, self.backup_dir):
            _rmtree(self.project, d)
        if self._prune:
            prune(self.project, keep=self.txid)

    def run(self):
        """Chạy toàn bộ: preflight -> begin -> stage -> backup -> commit. Lỗi giữa chừng để lại nhật ký. / Full run."""
        if not self.journal['ops']:
            return None  # không có gì để ghi: không tạo nhật ký / nothing to write: no journal created
        guard(self.project, self.dir)
        problems = self.preflight()
        if problems:
            # Không để lại nhật ký: thư mục giao dịch được dọn ngay / no journal is kept after a failed preflight
            _rmtree(self.project, self.dir)
            if self._prune:
                _prune_empty_runtime(self.project)
            raise TransactionError('; '.join(problems))
        try:
            self.begin()
            try:
                self.stage()
                self.backup()
            except Exception as e:
                # chưa chạm file người dùng: hủy giao dịch, không để việc dở / no user file touched: abandon, no open work
                self.abandon()
                raise TransactionError(L('Lỗi trước khi ghi file: %s', 'Failed before any file was written: %s') % e)
            self.commit()
        finally:
            self.close()
        return self.txid

    def abandon(self):
        self.journal['status'] = 'rolled_back'
        self.journal['note'] = 'abandoned before commit'
        self._save()
        for d in (self.stage_dir, self.backup_dir):
            _rmtree(self.project, d)

def _prune_empty_runtime(project):
    for d in (os.path.join(runtime_root(project), 'transactions'), runtime_root(project)):
        if not link_free(d, project):
            continue
        try:
            os.rmdir(d)
        except OSError:
            pass

def _load(project, txid):
    path = os.path.join(txdir(project, txid), 'journal.json')
    guard(project, path)  # không đọc nhật ký qua liên kết / never read a journal through a link
    with io.open(path, encoding='utf-8') as f:
        j = json.load(f)
    if j.get('schema') not in (SCHEMA, CREATE_SCHEMA):
        raise TransactionError(L('Nhật ký không đúng schema.', 'Journal has an unexpected schema.'))
    _validate_create_journal(j)
    return j

def _validate_create_journal(j):
    """v2 is opt-in: old readers reject it instead of treating a create as a replace."""
    ops = j.get('ops')
    if j.get('schema') == SCHEMA:
        # Legacy callers used create/create_exclusive as informational labels, including mixed ordering.
        return
    if (j.get('status') not in ('prepared', 'committing', 'committed', 'rolled_back', 'rollback_partial') or
            not isinstance(j.get('id'), str) or not j['id'] or any(c in j['id'] for c in '/\\.') or
            not isinstance(ops, list) or not ops or not any(isinstance(o, dict) and o.get('action') == 'create' for o in ops)):
        raise TransactionError('Malformed transaction-v2 operations')
    seen, writing = set(), False
    for op in ops:
        if not isinstance(op, dict) or set(op) != {'path', 'action', 'before', 'after', 'size', 'state'}:
            raise TransactionError('Malformed transaction-v2 operation')
        path = op.get('path')
        if (not isinstance(path, str) or not path or path.startswith('/') or ':' in path or '\\' in path or
                any(p in ('', '.', '..') for p in path.split('/')) or path in seen or
                op.get('action') not in ('create', 'write') or
                op.get('state') not in ('pending', 'done', 'skipped_conflict', 'rolled_back') or
                not isinstance(op.get('after'), str) or len(op['after']) != 64 or
                any(c not in '0123456789abcdef' for c in op['after']) or
                type(op.get('size')) is not int or op['size'] < 0):
            raise TransactionError('Malformed transaction-v2 operation')
        seen.add(path)
        if op['action'] == 'create':
            if writing or op.get('before') is not None:
                raise TransactionError('Create operations must precede replacements and start absent')
        else:
            writing = True
            before = op.get('before')
            if not isinstance(before, str) or len(before) != 64 or any(c not in '0123456789abcdef' for c in before):
                raise TransactionError('Malformed transaction-v2 replacement basis')

def _owns_created(project, folder, op):
    dst = os.path.join(project, *op['path'].split('/'))
    staged = os.path.join(folder, 'staging', *op['path'].split('/'))
    guard(project, dst, staged)
    try:
        return os.path.samefile(dst, staged) and sha_file(dst) == op['after'] and sha_file(staged) == op['after']
    except FileNotFoundError:
        return False

def _check_created_dependencies(project, folder, journal, current):
    """A catalog replacement may not follow a missing, edited or foreign created file."""
    if current['action'] == 'create':
        return
    for prior in journal['ops']:
        if prior['action'] == 'create' and (prior['state'] != 'done' or not _owns_created(project, folder, prior)):
            raise CommitConflict('Created-file dependency changed; catalog not written: ' + prior['path'])

def _save_journal(project, txid, journal):
    journal['updated'] = _now()
    _write_json_atomic(project, os.path.join(txdir(project, txid), 'journal.json'), journal)

def incomplete(project_root, *, strict=False):
    """Tóm tắt các giao dịch chưa hoàn tất. / Summaries of unfinished transactions.

    strict=True refuses unsafe, unreadable or uninterpretable journals instead of skipping them (P-CTX1).
    It only checks the fields needed for this scan, not the full recovery schema, and never writes.
    """
    base = os.path.join(runtime_root(os.path.abspath(project_root)), 'transactions')
    out = []
    if strict:
        try:
            os.lstat(base)  # unlike lexists(), an inspection error must not look like a missing directory
        except FileNotFoundError:
            return out
        if not os.path.isdir(base) or runtime_problem(project_root):
            raise TransactionError('Cannot safely inspect transaction journals')
    if not os.path.isdir(base) or runtime_problem(project_root):
        return out  # không đọc nhật ký qua liên kết; writer và status báo lỗi riêng / never read journals through a link
    for name in sorted(os.listdir(base)):
        try:
            j = _load(os.path.abspath(project_root), name)
            if strict and (not isinstance(j, dict) or j.get('status') not in
                           ('prepared', 'committing', 'committed', 'rolled_back', 'rollback_partial') or
                           not isinstance(j.get('ops'), list) or any(
                               not isinstance(o, dict) or o.get('state') not in
                               ('pending', 'done', 'skipped_conflict', 'rolled_back') for o in j['ops'])):
                raise TransactionError('Cannot determine transaction status from journal')
        except (OSError, ValueError, TransactionError):
            if strict:
                raise TransactionError('Cannot read or interpret transaction journal')
            continue
        except (AttributeError, TypeError):
            if strict:
                raise TransactionError('Cannot read or interpret transaction journal')
            raise  # preserve the existing non-strict caller behaviour
        if j.get('status') not in INCOMPLETE:
            continue
        ops = j.get('ops', [])
        out.append({'id': j.get('id', name), 'operation': j.get('operation'), 'status': j.get('status'),
                    'created': j.get('created'), 'done': sum(1 for o in ops if o.get('state') == 'done'),
                    'pending': sum(1 for o in ops if o.get('state') == 'pending'), 'total': len(ops)})
    return out

def _check_id(txid):
    if not txid or any(c in txid for c in '/\\.'):
        raise TransactionError(L('Mã giao dịch không hợp lệ.', 'Invalid transaction id.'))

def resume(project_root, txid):
    """Áp các thao tác còn pending nếu target còn như trước; đánh dấu done nếu đã có after. / Finish pending ops."""
    project = os.path.abspath(project_root)
    _check_id(txid)
    guard(project, txdir(project, txid))
    j = _load(project, txid)
    if j.get('status') == 'rollback_partial':
        return make('blocked', code=1, transaction=txid, changes=False,
                    message=L('Giao dịch %s đã phục hồi một phần (có file bạn đã sửa); không tiếp tục được.',
                              'Transaction %s was rolled back partially (you edited some files); it cannot be resumed.') % txid,
                    next_actions=[L('Chạy: python tools/transaction.py rollback %s, hoặc khôi phục tay từ thư mục backup.',
                                    'Run: python tools/transaction.py rollback %s, or restore by hand from the backup folder.') % txid])
    if j.get('status') == 'rolled_back':
        return make('success', code=0, message=L('Giao dịch %s đã được phục hồi trước đó.', 'Transaction %s was already rolled back.') % txid,
                    changes=False, transaction=txid)
    applied, skipped, finished, unstaged = [], [], [], []
    kill = _fault('kill')
    commit_limit = _fault('commit')
    n = 0
    for op in j['ops']:
        if op['state'] != 'pending':
            continue
        if j.get('schema') == CREATE_SCHEMA:
            try:
                _check_created_dependencies(project, txdir(project, txid), j, op)
            except CommitConflict:
                skipped.append(op['path'])
                break
        dst = os.path.join(project, *op['path'].split('/'))
        staged = os.path.join(txdir(project, txid), 'staging', *op['path'].split('/'))
        did_apply = False
        # Băm và quyết định nằm trong vùng bảo vệ, sau hook, sát trước replace / hash and decide inside the protected span
        with held(project, dst, staged, create=(dst,), point='resume') as check:
            check()
            if j.get('schema') == CREATE_SCHEMA:
                try:
                    _check_created_dependencies(project, txdir(project, txid), j, op)
                except CommitConflict:
                    skipped.append(op['path'])
                    break
            cur = sha_file(dst)
            if op.get('action') == 'create' and j.get('schema') == CREATE_SCHEMA:
                if _owns_created(project, txdir(project, txid), op):
                    op['state'] = 'done'; finished.append(op['path'])
                elif cur is None and not os.path.lexists(dst) and os.path.isfile(staged) and sha_file(staged) == op['after']:
                    check()
                    try:
                        os.link(staged, dst)
                    except FileExistsError:
                        op['state'] = 'skipped_conflict'; skipped.append(op['path'])
                    else:
                        op['state'] = 'done'; applied.append(op['path']); did_apply = True
                elif cur is None:
                    unstaged.append(op['path'])
                else:
                    op['state'] = 'skipped_conflict'; skipped.append(op['path'])
            elif cur == op['after']:
                op['state'] = 'done'; finished.append(op['path'])
            elif cur == op['before'] and os.path.isfile(staged) and sha_file(staged) == op['after']:
                check()
                os.replace(staged, dst)
                op['state'] = 'done'; applied.append(op['path']); did_apply = True
            elif cur == op['before']:
                unstaged.append(op['path'])  # chưa có bản staging hợp lệ: không thể áp / no valid staged copy to apply
            else:
                op['state'] = 'skipped_conflict'; skipped.append(op['path'])
        _save_journal(project, txid, j)
        if j.get('schema') == CREATE_SCHEMA and op['state'] != 'done':
            break
        if did_apply:
            n += 1
            if commit_limit is not None and n >= commit_limit:
                raise OSError('synthetic fault: commit')
            if kill is not None and n >= kill:
                os._exit(70)
    remaining = [o for o in j['ops'] if o['state'] in ('pending', 'skipped_conflict')]
    if not remaining:
        j['status'] = 'committed'
        _save_journal(project, txid, j)
        _rmtree(project, os.path.join(txdir(project, txid), 'staging'))
        _rmtree(project, os.path.join(txdir(project, txid), 'backup'))
        prune(project, keep=txid)
    else:
        j['status'] = 'committing' if any(o['state'] == 'pending' for o in j['ops']) else j['status']
        _save_journal(project, txid, j)
    code = 0 if not remaining else 1
    status = 'success' if not remaining else 'partial'
    nxt = []
    if not remaining and j.get('operation') == 'adopt':
        # bước init_project.py nằm ngoài giao dịch / the init_project.py step runs outside the transaction
        nxt.append(L('Các file package đã đủ. Chạy tiếp: python tools/init_project.py --name "<tên project>" --force',
                     'Package files are complete. Next: python tools/init_project.py --name "<project name>" --force'))
    if unstaged:
        nxt.append(L('Thiếu bản staging của %d file; chạy: python tools/transaction.py rollback %s', 'Staged copy missing for %d files; run: python tools/transaction.py rollback %s') % (len(unstaged), txid))
    if skipped:
        nxt.append(L('Kiểm tra file bị bỏ qua, rồi chạy: python tools/transaction.py rollback %s', 'Check the skipped files, then run: python tools/transaction.py rollback %s') % txid)
    return make(status, code=code, message=L('Đã tiếp tục giao dịch %s.', 'Resumed transaction %s.') % txid,
                changes=bool(applied or finished), transaction=txid,
                files=[{'path': p, 'action': 'applied'} for p in applied] +
                      [{'path': p, 'action': 'already_done'} for p in finished] +
                      [{'path': p, 'action': 'skipped_conflict'} for p in skipped] +
                      [{'path': p, 'action': 'not_staged'} for p in unstaged],
                next_actions=nxt)

def rollback(project_root, txid):
    """Khôi phục bản gốc của thao tác đã done hoặc còn pending (xét theo nội dung file) nếu file chưa bị sửa. File người dùng đã sửa được giữ nguyên;
    khi đó trạng thái rollback_partial KHÔNG chặn thao tác mới và thư mục backup được giữ để khôi phục tay.
    Restore originals for done or pending ops (judged by file content); user-edited files are kept. rollback_partial does not block new work;
    the backup folder is kept for manual recovery.
    """
    project = os.path.abspath(project_root)
    _check_id(txid)
    guard(project, txdir(project, txid))
    j = _load(project, txid)
    if j.get('status') == 'committed':
        return make('blocked', code=1, transaction=txid, changes=False,
                    message=L('Giao dịch %s đã hoàn tất; không còn bản sao lưu để phục hồi.', 'Transaction %s is already committed; no backups remain to restore.') % txid,
                    next_actions=[L('Không cần phục hồi. Muốn đổi lại, hãy chạy lại thao tác.', 'Nothing to roll back. Re-run the operation if you need a different result.')])
    tdir = txdir(project, txid)
    restored, removed = [], []
    for op in j['ops']:
        # 'pending' cũng phải xét theo nội dung: sự cố có thể xảy ra sau os.replace nhưng trước khi nhật ký ghi 'done'
        # 'pending' is judged by content too: a crash can land after os.replace but before the journal records 'done'
        if op['state'] not in ('pending', 'done', 'skipped_conflict'):
            continue
        dst = os.path.join(project, *op['path'].split('/'))
        backup = os.path.join(tdir, 'backup', *op['path'].split('/'))
        tmp = os.path.join(tdir, 'restore.tmp')
        # Băm, xét điều kiện và khôi phục đều trong vùng bảo vệ, sau hook, sát trước replace/remove
        # Hash, eligibility and restore all happen inside the protected span, after the hook, right before replace/remove
        with held(project, dst, backup, tmp, point='rollback') as check:
            check()
            cur = sha_file(dst)
            if op['before'] is None:
                if cur is None:
                    op['state'] = 'rolled_back'
                elif cur == op['after'] and (j.get('schema') != CREATE_SCHEMA or
                                             _owns_created(project, tdir, op)):
                    check()
                    os.remove(dst); op['state'] = 'rolled_back'; removed.append(op['path'])
                else:
                    op['state'] = 'skipped_conflict'
            elif cur == op['before']:
                op['state'] = 'rolled_back'
            elif cur == op['after'] and os.path.isfile(backup) and sha_file(backup) == op['before']:
                shutil.copyfile(backup, tmp)
                if sha_file(tmp) != op['before']:
                    os.remove(tmp)
                    raise TransactionError(L('Hash bản khôi phục không khớp: %s', 'Restore hash mismatch: %s') % os.path.basename(dst))
                check()
                os.replace(tmp, dst)
                op['state'] = 'rolled_back'; restored.append(op['path'])
            else:
                op['state'] = 'skipped_conflict'
        _save_journal(project, txid, j)
    pending = [o['path'] for o in j['ops'] if o['state'] == 'pending']  # còn lại sau vòng trên: không xác định được / left undecided
    partial = [o['path'] for o in j['ops'] if o['state'] in ('skipped_conflict', 'pending')]
    j['status'] = 'rollback_partial' if partial else 'rolled_back'
    _save_journal(project, txid, j)
    _rmtree(project, os.path.join(tdir, 'staging'))
    if not partial:
        _rmtree(project, os.path.join(tdir, 'backup'))
    extra, nxt = {}, []
    if partial:
        bdir = '.agent/runtime/transactions/%s/backup/' % txid
        extra['backup_dir'] = bdir
        nxt.append(L('Giữ nguyên %d file bạn đã sửa sau sự cố; không ghi đè. Bản gốc để khôi phục tay: %s',
                     'Kept %d files you edited after the interruption; not overwritten. Originals for manual recovery: %s') % (len(partial), bdir))
    return make('partial' if partial else 'success', code=1 if partial else 0,
                message=L('Đã phục hồi giao dịch %s.', 'Rolled back transaction %s.') % txid,
                changes=bool(restored or removed), transaction=txid,
                files=[{'path': p, 'action': 'restored'} for p in restored] +
                      [{'path': p, 'action': 'removed'} for p in removed] +
                      [{'path': p, 'action': 'skipped_conflict'} for p in partial],
                unchecked=pending, next_actions=nxt, **extra)

def prune(project, keep=None):
    """Giữ KEEP_JOURNALS nhật ký đã committed mới nhất. / Keep the newest committed journals."""
    base = os.path.join(runtime_root(os.path.abspath(project)), 'transactions')
    if not os.path.isdir(base) or runtime_problem(project):
        return
    done = []
    for name in os.listdir(base):
        try:
            j = _load(os.path.abspath(project), name)
        except (OSError, ValueError, TransactionError):
            continue
        if j.get('status') == 'committed' and name != keep:
            done.append((j.get('created', ''), name))
    done.sort(reverse=True)
    for _, name in done[KEEP_JOURNALS - (1 if keep else 0):]:
        _rmtree(os.path.abspath(project), os.path.join(base, name))

def blocked_message(project):
    """Thông báo chặn khi có giao dịch dở (VI / EN); None nếu không có. / Bilingual block notice, None when clear."""
    items = incomplete(project)
    if not items:
        return None
    t = items[0]['id']
    return ('Có giao dịch chưa hoàn tất %s: chưa ghi thêm gì. Chọn MỘT trong hai lệnh:\n'
            '  python tools/transaction.py resume %s     (tiếp tục / continue)\n'
            '  python tools/transaction.py rollback %s   (phục hồi bản gốc / restore originals)\n'
            'Unfinished transaction %s: nothing new written. Run ONE of the two commands above.') % (t, t, t, t)

def _cli(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['status', 'resume', 'rollback'])
    ap.add_argument('txid', nargs='?')
    ap.add_argument('--project', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--result-json', action='store_true')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    a = ap.parse_args(argv)
    LANG = a.lang
    project = os.path.abspath(a.project)
    if a.cmd == 'status':
        problem = runtime_problem(project)
        if problem:
            if a.result_json:
                emit(make('error', code=2, message=problem, changes=False))
            else:
                print(problem)
            return 2
        items = incomplete(project)
        code = 1 if items else 0
        if a.result_json:
            emit(make('issues' if items else 'success', code=code, message='Unfinished transactions: %d' % len(items),
                      changes=False, transactions=items,
                      next_actions=[('resume %s / rollback %s' % (i['id'], i['id'])) for i in items]))
        else:
            if not items:
                print(L('Không có giao dịch dở.', 'No unfinished transactions.'))
            for i in items:
                print('%s  %s  %s  %d/%d' % (i['id'], i['operation'], i['status'], i['done'], i['total']))
        return code
    if not a.txid:
        raise SystemExit(2)
    try:
        res = resume(project, a.txid) if a.cmd == 'resume' else rollback(project, a.txid)
    except (OSError, ValueError, TransactionError) as e:
        res = make('error', code=2, message=str(e), changes=None, transaction=a.txid)
    if a.result_json:
        emit(res)
    else:
        print(res['message'])
        for f in res['files']:
            print('  - %s: %s' % (f['action'], f['path']))
        for n in res['next_actions']:
            print('  ' + n)
    return res['code']

if __name__ == '__main__':
    sys.exit(_cli(sys.argv[1:]))
