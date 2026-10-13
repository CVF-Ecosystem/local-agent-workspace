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
"""
import argparse, datetime, hashlib, io, json, os, shutil, sys, uuid
from result_schema import emit, make

SCHEMA = 'local-agent-workspace/transaction-v1'
RUNTIME_DIR = '.agent/runtime'
KEEP_JOURNALS = 20
MARGIN = 1024 * 1024
FAULT_ENV = 'LOCAL_AGENT_WORKSPACE_TEST_FAULT'
INCOMPLETE = ('prepared', 'committing')  # rollback_partial là trạng thái kết thúc, không chặn / terminal, does not block
LANG = 'vi'

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

def txdir(project, txid):
    return os.path.join(runtime_root(project), 'transactions', txid)

def _write_json_atomic(path, data):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    tmp = path + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def probe_writable(project):
    """Kiểm quyền ghi bằng file tạm trong .agent/runtime. / Write probe inside the runtime folder."""
    d = runtime_root(project)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, '.probe-' + uuid.uuid4().hex)
    with open(p, 'wb') as f:
        f.write(b'probe')
    os.remove(p)

class Transaction:
    """Một lần ghi có nhật ký. Dùng: plan -> stage -> backup -> commit. / One journaled write.

    ops: [{'path', 'action', 'before', 'after', 'size', 'state'}]; content is held in memory only
    until staged, never written to the journal.
    """

    def __init__(self, project, operation, txid=None):
        self.project = os.path.abspath(project)
        self.txid = txid or (datetime.datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
        self.dir = txdir(self.project, self.txid)
        self.stage_dir = os.path.join(self.dir, 'staging')
        self.backup_dir = os.path.join(self.dir, 'backup')
        self.journal = {'schema': SCHEMA, 'id': self.txid, 'operation': operation, 'status': 'prepared',
                        'created': _now(), 'updated': _now(), 'ops': []}
        self._content = {}

    # ---- planning / lập kế hoạch
    def add(self, rel, data, action='write'):
        """Thêm một thao tác ghi file rel với nội dung data (bytes). / Plan a write of rel with bytes data."""
        if rel.startswith('/') or '..' in rel.split('/') or '\\' in rel:
            raise TransactionError('Invalid relative path / Đường dẫn không hợp lệ: ' + rel)
        dst = os.path.join(self.project, *rel.split('/'))
        before = sha_file(dst)
        if before is not None and before == sha_bytes(data):
            return None  # đã đúng nội dung: không cần thao tác / already identical: no op needed
        op = {'path': rel, 'action': action, 'before': before, 'after': sha_bytes(data),
              'size': len(data), 'state': 'pending'}
        self.journal['ops'].append(op)
        self._content[rel] = data
        return op

    def _save(self):
        self.journal['updated'] = _now()
        _write_json_atomic(os.path.join(self.dir, 'journal.json'), self.journal)

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
        return problems

    # ---- execution / thực thi
    def begin(self):
        os.makedirs(self.stage_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        self._save()

    def stage(self):
        n = 0
        limit = _fault('stage')
        for op in self.journal['ops']:
            p = os.path.join(self.stage_dir, *op['path'].split('/'))
            os.makedirs(os.path.dirname(p), exist_ok=True)
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
            os.makedirs(os.path.dirname(dst), exist_ok=True)
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
            dst = os.path.join(self.project, *op['path'].split('/'))
            if sha_file(dst) != op['before']:
                self._set_state(op, 'skipped_conflict')
                raise CommitConflict(L('Fileđã đổi sau khi lập kế hoạch: %s', 'File changed after planning: %s') % op['path'])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.replace(os.path.join(self.stage_dir, *op['path'].split('/')), dst)
            self._set_state(op, 'done')
            done += 1
            if limit is not None and done >= limit:
                raise OSError('synthetic fault: commit')
            if kill is not None and done >= kill:
                os._exit(70)
        self.journal['status'] = 'committed'
        self._save()
        self._cleanup()

    def _cleanup(self):
        for d in (self.stage_dir, self.backup_dir):
            shutil.rmtree(d, ignore_errors=True)
        prune(self.project, keep=self.txid)

    def run(self):
        """Chạy toàn bộ: preflight -> begin -> stage -> backup -> commit. Lỗi giữa chừng để lại nhật ký. / Full run."""
        if not self.journal['ops']:
            return None  # không có gì để ghi: không tạo nhật ký / nothing to write: no journal created
        problems = self.preflight()
        if problems:
            # Không để lại nhật ký: thư mục giao dịch được dọn ngay / no journal is kept after a failed preflight
            shutil.rmtree(self.dir, ignore_errors=True)
            _prune_empty_runtime(self.project)
            raise TransactionError('; '.join(problems))
        self.begin()
        try:
            self.stage()
            self.backup()
        except Exception as e:
            # chưa chạm file người dùng: hủy giao dịch, không để việc dở / no user file touched: abandon, no open work
            self.abandon()
            raise TransactionError(L('Lỗi trước khi ghi file: %s', 'Failed before any file was written: %s') % e)
        self.commit()
        return self.txid

    def abandon(self):
        self.journal['status'] = 'rolled_back'
        self.journal['note'] = 'abandoned before commit'
        self._save()
        for d in (self.stage_dir, self.backup_dir):
            shutil.rmtree(d, ignore_errors=True)

def _prune_empty_runtime(project):
    for d in (os.path.join(runtime_root(project), 'transactions'), runtime_root(project)):
        try:
            os.rmdir(d)
        except OSError:
            pass

def _load(project, txid):
    path = os.path.join(txdir(project, txid), 'journal.json')
    with io.open(path, encoding='utf-8') as f:
        j = json.load(f)
    if j.get('schema') != SCHEMA:
        raise TransactionError(L('Nhật ký không đúng schema.', 'Journal has an unexpected schema.'))
    return j

def _save_journal(project, txid, journal):
    journal['updated'] = _now()
    _write_json_atomic(os.path.join(txdir(project, txid), 'journal.json'), journal)

def incomplete(project_root):
    """Tóm tắt các giao dịch chưa hoàn tất. / Summaries of unfinished transactions."""
    base = os.path.join(runtime_root(os.path.abspath(project_root)), 'transactions')
    out = []
    if not os.path.isdir(base):
        return out
    for name in sorted(os.listdir(base)):
        try:
            j = _load(os.path.abspath(project_root), name)
        except (OSError, ValueError, TransactionError):
            continue
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
        dst = os.path.join(project, *op['path'].split('/'))
        cur = sha_file(dst)
        staged = os.path.join(txdir(project, txid), 'staging', *op['path'].split('/'))
        if cur == op['after']:
            op['state'] = 'done'; finished.append(op['path'])
        elif cur == op['before'] and os.path.isfile(staged) and sha_file(staged) == op['after']:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.replace(staged, dst)
            op['state'] = 'done'; applied.append(op['path'])
            n += 1
            if commit_limit is not None and n >= commit_limit:
                _save_journal(project, txid, j)
                raise OSError('synthetic fault: commit')
            if kill is not None and n >= kill:
                _save_journal(project, txid, j)
                os._exit(70)
        elif cur == op['before']:
            unstaged.append(op['path'])  # chưa có bản staging hợp lệ: không thể áp / no valid staged copy to apply
        else:
            op['state'] = 'skipped_conflict'; skipped.append(op['path'])
        _save_journal(project, txid, j)
    remaining = [o for o in j['ops'] if o['state'] in ('pending', 'skipped_conflict')]
    if not remaining:
        j['status'] = 'committed'
        _save_journal(project, txid, j)
        shutil.rmtree(os.path.join(txdir(project, txid), 'staging'), ignore_errors=True)
        shutil.rmtree(os.path.join(txdir(project, txid), 'backup'), ignore_errors=True)
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

def _restore_atomic(backup, dst, tdir, expect):
    """Sao lưu -> file tạm cùng ổ -> kiểm hash -> os.replace. / Copy to a temp file on the same volume, verify, then replace."""
    tmp = os.path.join(tdir, 'restore.tmp')
    shutil.copyfile(backup, tmp)
    if sha_file(tmp) != expect:
        os.remove(tmp)
        raise TransactionError(L('Hash bản khôi phục không khớp: %s', 'Restore hash mismatch: %s') % os.path.basename(dst))
    os.replace(tmp, dst)

def rollback(project_root, txid):
    """Khôi phục bản gốc của thao tác đã done nếu file chưa bị sửa. File người dùng đã sửa được giữ nguyên;
    khi đó trạng thái rollback_partial KHÔNG chặn thao tác mới và thư mục backup được giữ để khôi phục tay.
    Restore originals for done ops; user-edited files are kept. rollback_partial does not block new work;
    the backup folder is kept for manual recovery.
    """
    project = os.path.abspath(project_root)
    _check_id(txid)
    j = _load(project, txid)
    if j.get('status') == 'committed':
        return make('blocked', code=1, transaction=txid, changes=False,
                    message=L('Giao dịch %s đã hoàn tất; không còn bản sao lưu để phục hồi.', 'Transaction %s is already committed; no backups remain to restore.') % txid,
                    next_actions=[L('Không cần phục hồi. Muốn đổi lại, hãy chạy lại thao tác.', 'Nothing to roll back. Re-run the operation if you need a different result.')])
    tdir = txdir(project, txid)
    restored, removed = [], []
    for op in j['ops']:
        if op['state'] not in ('done', 'skipped_conflict'):
            continue
        dst = os.path.join(project, *op['path'].split('/'))
        cur = sha_file(dst)
        if op['before'] is None:
            if cur is None:
                op['state'] = 'rolled_back'
            elif cur == op['after']:
                os.remove(dst); op['state'] = 'rolled_back'; removed.append(op['path'])
            else:
                op['state'] = 'skipped_conflict'
        elif cur == op['before']:
            op['state'] = 'rolled_back'
        else:
            backup = os.path.join(tdir, 'backup', *op['path'].split('/'))
            if cur == op['after'] and os.path.isfile(backup) and sha_file(backup) == op['before']:
                _restore_atomic(backup, dst, tdir, op['before'])
                op['state'] = 'rolled_back'; restored.append(op['path'])
            else:
                op['state'] = 'skipped_conflict'
        _save_journal(project, txid, j)
    pending = [o['path'] for o in j['ops'] if o['state'] == 'pending']
    partial = [o['path'] for o in j['ops'] if o['state'] == 'skipped_conflict']
    j['status'] = 'rollback_partial' if partial else 'rolled_back'
    _save_journal(project, txid, j)
    shutil.rmtree(os.path.join(tdir, 'staging'), ignore_errors=True)
    if not partial:
        shutil.rmtree(os.path.join(tdir, 'backup'), ignore_errors=True)
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
    if not os.path.isdir(base):
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
        shutil.rmtree(os.path.join(base, name), ignore_errors=True)

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
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['status', 'resume', 'rollback'])
    ap.add_argument('txid', nargs='?')
    ap.add_argument('--project', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--result-json', action='store_true')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    a = ap.parse_args(argv)
    LANG = a.lang
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    project = os.path.abspath(a.project)
    if a.cmd == 'status':
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
