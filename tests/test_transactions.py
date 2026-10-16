"""Transaction checks: faults at each stage, recovery, rollback safety, journal contents. Temp dirs only."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import contextlib
import io
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import result_schema
import transaction as tx
import upgrade_package as up

FAULT = tx.FAULT_ENV
RUNTIME = '.agent/runtime/'
INDEX = ('# SKILL INDEX\n\n| Skill ID | Origin | Scope | Location / Provider | Use when | Status | Provenance / Notes |\n'
         '|---|---|---|---|---|---|---|\n\n## Ghi chú\nNone\n')


def snapshot(root):
    """Mọi file trừ dữ liệu giao dịch / every file except transaction runtime data."""
    out = {}
    for p in root.rglob('*'):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and '__pycache__' not in p.parts and not rel.startswith(RUNTIME):
            out[rel] = p.read_bytes()
    return out


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return p


def run(script, *args, base=ROOT, env=None):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    e.pop(FAULT, None)
    e.update(env or {})
    return subprocess.run([sys.executable, str(base / 'tools' / script), *map(str, args)],
                          cwd=base, env=e, capture_output=True, encoding='utf-8', timeout=300)


def envelope(r):
    return result_schema.split_output(r.stdout)[1]


def manifest(root):
    lines = []
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name != 'MANIFEST.sha256':
            lines.append(hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest() + '  ' + p.relative_to(root).as_posix())
    write(root, 'MANIFEST.sha256', '\n'.join(lines) + '\n')


def only_tx(project):
    items = tx.incomplete(str(project))
    assert len(items) == 1, items
    return items[0]


class Transactions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tx-check-')
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def upgrade_pair(self, name):
        """Gói cũ và mới; 5 thao tác khi nâng cấp / old and new packages; five ops on upgrade."""
        old, new = self.root / (name + '-old'), self.root / (name + '-new')
        for r in (old, new):
            write(r, 'VERSION', '1.6.0\n')
            write(r, 'untouched.txt', 'old package')
            write(r, 'conflict.txt', 'old package')
            write(r, 'kept.txt', 'old package')
            write(r, 'PROJECT.md', 'private context')
            manifest(r)
        write(old, '.agent/PACKAGE_INFO.json', json.dumps({'package': 'local-agent-workspace', 'version': '1.6.0', 'language': 'vi'}))
        write(old, 'conflict.txt', 'user change')
        write(old, 'kept.txt', 'user change')
        write(new, 'untouched.txt', 'new package')
        write(new, 'conflict.txt', 'new package')
        write(new, 'added.txt', 'new file')
        manifest(new)
        return old, new

    def apply_upgrade(self, old, new, env=None, *extra):
        return run('upgrade_package.py', '--project', old, '--from', new, '--apply', *extra, env=env)

    def package(self, name):
        dst = self.root / name
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', '__pycache__', 'dist', 'roadmap', 'tests', 'feedback'))
        shutil.rmtree(str(dst / '.agent' / 'runtime'), ignore_errors=True)  # dữ liệu vận hành của máy phát triển không vào bản sao / dev-machine runtime data never enters the copy
        [f.unlink() for f in (dst / 'assets').glob('*') if f.is_file() and f.name != 'README.md']  # logo/nhận diện của máy phát triển / dev-machine branding
        return dst

    def test_preview_and_dry_run_write_nothing_and_create_no_runtime(self):
        old, new = self.upgrade_pair('pv')
        before = snapshot(old)
        r = run('upgrade_package.py', '--project', old, '--from', new)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run('upgrade_package.py', '--project', old, '--from', new, '--result-json')
        self.assertEqual(envelope(r)['status'], 'preview')
        self.assertEqual(snapshot(old), before)
        self.assertFalse((old / '.agent' / 'runtime').exists())
        target = self.root / 'adopt-pv'
        write(target, 'AGENTS.md', 'PRIVATE')
        before = snapshot(target)
        r = run('adopt_project.py', '--project', target, '--name', 'Example')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(target), before)
        self.assertFalse((target / '.agent' / 'runtime').exists())
        pkg = self.package('pkg-dry')
        before = snapshot(pkg)
        r = run('init_project.py', '--name', 'Example', '--lang', 'en', '--dry-run', '--result-json', base=pkg)
        self.assertEqual(envelope(r)['status'], 'preview')
        self.assertEqual(snapshot(pkg), before)
        self.assertFalse((pkg / '.agent' / 'runtime').exists())

    def test_fault_at_stage_and_backup_writes_nothing_and_does_not_block(self):
        for fault in ('stage:2', 'backup:1'):
            with self.subTest(fault=fault):
                old, new = self.upgrade_pair(fault.replace(':', '-'))
                before = snapshot(old)
                r = self.apply_upgrade(old, new, env={FAULT: fault})
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn('NOTHING WRITTEN', r.stdout + r.stderr)
                self.assertNotIn('còn dở', r.stdout + r.stderr)
                self.assertEqual(snapshot(old), before)
                self.assertEqual(tx.incomplete(str(old)), [])
                r = self.apply_upgrade(old, new, None, '--result-json')
                self.assertEqual((r.returncode, envelope(r)['status']), (0, 'success'))

    def test_interrupted_commit_resumes_to_same_state_as_clean_apply(self):
        clean_old, clean_new = self.upgrade_pair('clean')
        self.assertEqual(self.apply_upgrade(clean_old, clean_new).returncode, 0)
        clean = snapshot(clean_old)
        old, new = self.upgrade_pair('broken')
        r = self.apply_upgrade(old, new, env={FAULT: 'commit:2'})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        item = only_tx(old)
        self.assertEqual((item['status'], item['done'], item['pending'], item['total']), ('committing', 2, 3, 5))
        r = run('transaction.py', 'resume', item['id'], '--project', old, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(envelope(r)['code'], 0)
        self.assertEqual(snapshot(old), clean)
        self.assertEqual(tx.incomplete(str(old)), [])

    def test_killed_process_is_reported_and_resumable(self):
        clean_old, clean_new = self.upgrade_pair('kclean')
        self.assertEqual(self.apply_upgrade(clean_old, clean_new).returncode, 0)
        clean = snapshot(clean_old)
        old, new = self.upgrade_pair('killed')
        r = self.apply_upgrade(old, new, env={FAULT: 'kill:2'})
        self.assertEqual(r.returncode, 70)
        item = only_tx(old)
        self.assertEqual((item['done'], item['pending']), (2, 3))
        r = run('transaction.py', 'resume', item['id'], '--project', old)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(snapshot(old), clean)

    def test_rollback_restores_byte_identical_originals(self):
        old, new = self.upgrade_pair('rb')
        before = snapshot(old)
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:3'}).returncode, 1)
        item = only_tx(old)
        r = run('transaction.py', 'rollback', item['id'], '--project', old, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(envelope(r)['status'], 'success')
        self.assertEqual(snapshot(old), before)
        self.assertFalse((old / 'added.txt').exists())
        self.assertFalse((old / 'conflict.txt.new').exists())
        self.assertEqual(tx.incomplete(str(old)), [])
        self.assertFalse((Path(tx.txdir(str(old), item['id'])) / 'backup').exists())

    def test_rollback_does_not_overwrite_user_edit_made_after_crash(self):
        old, new = self.upgrade_pair('edit')
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:3'}).returncode, 1)
        item = only_tx(old)
        write(old, 'untouched.txt', 'USER EDIT')
        r = run('transaction.py', 'rollback', item['id'], '--project', old, '--result-json')
        env = envelope(r)
        self.assertEqual((r.returncode, env['status'], env['code']), (1, 'partial', 1))
        self.assertEqual((old / 'untouched.txt').read_text(encoding='utf-8'), 'USER EDIT')
        self.assertTrue(any(f['action'] == 'skipped_conflict' and f['path'] == 'untouched.txt' for f in env['files']))
        self.assertEqual(tx.incomplete(str(old)), [])
        self.assertIn('backup', ' '.join(env['next_actions']))
        self.assertTrue((Path(tx.txdir(str(old), item['id'])) / 'backup').is_dir())

    def test_resume_skips_target_changed_by_user(self):
        old, new = self.upgrade_pair('skip')
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:1'}).returncode, 1)
        item = only_tx(old)
        write(old, 'added.txt', 'USER')
        r = run('transaction.py', 'resume', item['id'], '--project', old, '--result-json')
        env = envelope(r)
        self.assertEqual((r.returncode, env['status']), (1, 'partial'))
        self.assertEqual((old / 'added.txt').read_text(encoding='utf-8'), 'USER')
        self.assertTrue((old / 'conflict.txt.new').is_file())
        self.assertTrue((old / 'MANIFEST.sha256').is_file())
        self.assertTrue(any(f['action'] == 'skipped_conflict' and f['path'] == 'added.txt' for f in env['files']))

    def test_resume_and_rollback_are_idempotent(self):
        old, new = self.upgrade_pair('idem')
        before = snapshot(old)
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:2'}).returncode, 1)
        item = only_tx(old)
        self.assertEqual(run('transaction.py', 'resume', item['id'], '--project', old).returncode, 0)
        after = snapshot(old)
        r = run('transaction.py', 'resume', item['id'], '--project', old, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['changes']), (0, False))
        self.assertEqual(snapshot(old), after)
        self.assertEqual(sum(1 for line in (old / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines() if 'untouched.txt' in line), 1)

        old, new = self.upgrade_pair('idem-rb')
        before = snapshot(old)
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:3'}).returncode, 1)
        item = only_tx(old)
        self.assertEqual(run('transaction.py', 'rollback', item['id'], '--project', old).returncode, 0)
        self.assertEqual(snapshot(old), before)
        r = run('transaction.py', 'rollback', item['id'], '--project', old, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['changes']), (0, False))
        self.assertEqual(snapshot(old), before)
        r = run('transaction.py', 'resume', item['id'], '--project', old, '--result-json')
        self.assertEqual(r.returncode, 0)
        self.assertEqual(snapshot(old), before)

    def test_committed_transaction_is_not_rolled_back(self):
        old, new = self.upgrade_pair('done')
        self.assertEqual(self.apply_upgrade(old, new).returncode, 0)
        base = old / '.agent' / 'runtime' / 'transactions'
        txid = os.listdir(str(base))[0]
        after = snapshot(old)
        r = run('transaction.py', 'rollback', txid, '--project', old, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['status']), (1, 'blocked'))
        self.assertEqual(snapshot(old), after)

    def test_journal_holds_no_contents_or_absolute_paths(self):
        old, new = self.upgrade_pair('jr')
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:2'}).returncode, 1)
        item = only_tx(old)
        text = (Path(tx.txdir(str(old), item['id'])) / 'journal.json').read_text(encoding='utf-8')
        for secret in ('old package', 'new package', 'new file', 'user change', 'private context'):
            self.assertNotIn(secret, text)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn(old.as_posix(), text)
        self.assertIsNone(re.search(r'[A-Za-z]:[\\/]', text))
        journal = json.loads(text)
        self.assertEqual(journal['schema'], 'local-agent-workspace/transaction-v1')
        for op in journal['ops']:
            self.assertEqual(set(op), {'path', 'action', 'before', 'after', 'size', 'state'})
            self.assertFalse(op['path'].startswith('/'))

    def test_preflight_failure_writes_nothing_and_leaves_no_runtime(self):
        proj = self.root / 'preflight'
        write(proj, 'a.txt', 'orig')
        Usage = collections.namedtuple('Usage', 'total used free')
        t = tx.Transaction(str(proj), 'upgrade')
        t.add('a.txt', b'new')
        with patch('shutil.disk_usage', return_value=Usage(10 ** 9, 10 ** 9, 0)):
            with self.assertRaises(tx.TransactionError):
                t.run()
        self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'orig')
        self.assertFalse((proj / '.agent' / 'runtime').exists())

    def test_missing_package_file_blocks_before_any_write(self):
        old, new = self.upgrade_pair('miss')
        (new / 'added.txt').unlink()
        before = snapshot(old)
        r = self.apply_upgrade(old, new, None, '--result-json')
        env = envelope(r)
        self.assertEqual((r.returncode, env['status']), (1, 'blocked'))
        self.assertEqual(snapshot(old), before)
        self.assertFalse((old / '.agent' / 'runtime').exists())

    def test_target_changed_after_planning_is_not_overwritten(self):
        proj = self.root / 'plan'
        write(proj, 'a.txt', 'orig')
        t = tx.Transaction(str(proj), 'upgrade')
        t.add('a.txt', b'new')
        write(proj, 'a.txt', 'user edit')
        with self.assertRaises(tx.TransactionError):
            t.run()
        self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'user edit')
        self.assertEqual(tx.incomplete(str(proj)), [])

    def test_committed_journals_are_pruned_to_newest_twenty(self):
        proj = self.root / 'prune'
        proj.mkdir()
        for i in range(22):
            t = tx.Transaction(str(proj), 'init')
            t.add('f%02d.txt' % i, ('x%d' % i).encode('utf-8'))
            t.run()
        self.assertEqual(len(os.listdir(str(proj / '.agent' / 'runtime' / 'transactions'))), 20)
        self.assertEqual(tx.incomplete(str(proj)), [])

    def test_cli_status_and_result_codes_match_exit_codes(self):
        old, new = self.upgrade_pair('cli')
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:2'}).returncode, 1)
        item = only_tx(old)
        r = run('transaction.py', 'status', '--project', old, '--result-json')
        env = envelope(r)
        self.assertEqual((r.returncode, env['code']), (1, 1))
        self.assertEqual(env['transactions'][0]['id'], item['id'])
        self.assertEqual(run('transaction.py', 'status', '--project', old).returncode, 1)
        empty = self.root / 'empty'
        empty.mkdir()
        r = run('transaction.py', 'status', '--project', empty, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['code'], envelope(r)['transactions']), (0, 0, []))
        r = run('transaction.py', 'resume', 'no-such-id', '--project', old, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['code']), (2, 2))

    def test_adopt_interrupted_then_resumed_matches_clean_adopt(self):
        def target(name):
            t = self.root / name
            write(t, 'AGENTS.md', 'PRIVATE')
            write(t, '.agent/SKILL_INDEX.md', INDEX)
            write(t, 'skills/local/project/my-own/SKILL.md', '---\nname: my-own\ndescription: Own skill used by the transaction test here.\n---\n# My own\n')
            return t
        clean = target('adopt-clean')
        self.assertEqual(run('adopt_project.py', '--project', clean, '--name', 'Example', '--apply').returncode, 0)
        expected = snapshot(clean)
        broken = target('adopt-broken')
        r = run('adopt_project.py', '--project', broken, '--name', 'Example', '--apply', env={FAULT: 'commit:2'})
        self.assertNotEqual(r.returncode, 0)
        item = only_tx(broken)
        self.assertEqual(item['operation'], 'adopt')
        r = run('adopt_project.py', '--project', broken, '--name', 'Example', '--apply', '--result-json')
        env = envelope(r)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((env['status'], env['transaction']), ('blocked', item['id']))
        r = run('transaction.py', 'resume', item['id'], '--project', broken, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('init_project.py', ' '.join(envelope(r)['next_actions']))
        r = run('init_project.py', '--name', 'Example', '--lang', 'vi', base=broken)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(snapshot(broken), expected)
        rows = (broken / '.agent' / 'SKILL_INDEX.md').read_text(encoding='utf-8').count('| my-own |')
        self.assertEqual(rows, 1)

    def test_init_interrupted_then_resumed_matches_clean_init(self):
        clean = self.package('init-clean')
        self.assertEqual(run('init_project.py', '--name', 'Example', '--lang', 'en', base=clean).returncode, 0)
        expected = snapshot(clean)
        broken = self.package('init-broken')
        r = run('init_project.py', '--name', 'Example', '--lang', 'en', base=broken, env={FAULT: 'commit:2'})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        item = only_tx(broken)
        self.assertEqual(item['operation'], 'init')
        self.assertFalse((broken / '.agent' / 'PACKAGE_INFO.json').exists())
        r = run('init_project.py', '--name', 'Example', '--lang', 'en', '--result-json', base=broken)
        self.assertEqual((r.returncode, envelope(r)['status'], envelope(r)['transaction']), (1, 'blocked', item['id']))
        r = run('transaction.py', 'resume', item['id'], '--project', broken, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(snapshot(broken), expected)

    def test_init_refuses_to_overwrite_existing_backup_with_other_content(self):
        pkg = self.package('init-bak')
        (pkg / 'README.md').write_text('PRIVATE README', encoding='utf-8')
        write(pkg, 'README.md.bak-' + datetime.date.today().strftime('%Y%m%d'), 'OLD BACKUP')
        before = snapshot(pkg)
        r = run('init_project.py', '--name', 'Example', '--lang', 'en', base=pkg)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(snapshot(pkg), before)

    def test_user_edit_after_crash_does_not_block_new_operations(self):
        old, new = self.upgrade_pair('forever')
        self.assertEqual(self.apply_upgrade(old, new, env={FAULT: 'commit:3'}).returncode, 1)
        item = only_tx(old)
        write(old, 'untouched.txt', 'USER EDIT')
        r = run('transaction.py', 'rollback', item['id'], '--project', old, '--result-json')
        env = envelope(r)
        self.assertEqual((r.returncode, env['status']), (1, 'partial'))
        self.assertIn('.agent/runtime/transactions/%s/backup/' % item['id'], ' '.join(env['next_actions']))
        self.assertTrue((Path(tx.txdir(str(old), item['id'])) / 'backup' / 'untouched.txt').is_file())
        self.assertEqual(tx.incomplete(str(old)), [])
        r = run('transaction.py', 'resume', item['id'], '--project', old, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['status']), (1, 'blocked'))
        r = self.apply_upgrade(old, new, None, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((old / 'untouched.txt').read_text(encoding='utf-8'), 'USER EDIT')

    def test_target_changed_during_commit_is_reported_as_partial(self):
        old, new = self.upgrade_pair('cc')
        real_backup = tx.Transaction.backup

        def backup_then_edit(t):
            real_backup(t)
            write(old, 'MANIFEST.sha256', 'USER MANIFEST')
        with patch.object(tx.Transaction, 'backup', backup_then_edit), \
                patch.object(sys, 'argv', ['upgrade', '--project', str(old), '--from', str(new), '--apply']), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(tx.CommitConflict):
                up.main()
        item = only_tx(old)
        self.assertEqual((item['status'], item['done'], item['pending'], item['total']), ('committing', 3, 1, 5))
        self.assertEqual(up.TX['id'], item['id'])
        self.assertEqual((old / 'MANIFEST.sha256').read_text(encoding='utf-8'), 'USER MANIFEST')
        r = run('transaction.py', 'rollback', item['id'], '--project', old, '--result-json')
        self.assertEqual((r.returncode, envelope(r)['status']), (1, 'partial'))
        self.assertFalse((old / 'added.txt').exists())

    def crash_after_replace(self, project, files):
        """Ghi từng file rồi chết ngay sau os.replace, trước khi nhật ký ghi 'done' (cửa sổ LAW-01).
        Writes then dies right after os.replace, before the journal records 'done' (the LAW-01 window)."""
        driver = ("import json, os, sys\n"
                  "sys.path.insert(0, sys.argv[1])\n"
                  "import transaction as tx\n"
                  "t = tx.Transaction(sys.argv[2], 'crash-window', txid='crash-window')\n"
                  "for rel, text in json.loads(sys.argv[3]).items():\n"
                  "    t.add(rel, text.encode('utf-8'))\n"
                  "real = t._set_state\n"
                  "def die(op, state):\n"
                  "    if state == 'done':\n"
                  "        os._exit(70)\n"
                  "    real(op, state)\n"
                  "t._set_state = die\n"
                  "t.run()\n")
        e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        e.pop(FAULT, None)
        r = subprocess.run([sys.executable, '-c', driver, str(ROOT / 'tools'), str(project), json.dumps(files)],
                           env=e, capture_output=True, timeout=60)
        self.assertEqual(r.returncode, 70, r.stderr)
        return Path(tx.txdir(str(project), 'crash-window'))

    def test_rollback_after_crash_between_replace_and_journal_restores_the_original(self):
        """LAW-01: nhật ký còn 'pending' nhưng file đã thay; rollback phải phục hồi, không báo thành công rỗng.
        LAW-01: the journal still says 'pending' but the file was replaced; rollback must restore it, not report an empty success."""
        project = self.root / 'law01'
        write(project, 'existing.txt', 'ORIGINAL')
        tdir = self.crash_after_replace(project, {'existing.txt': 'REPLACED'})
        journal = json.loads((tdir / 'journal.json').read_text(encoding='utf-8'))
        self.assertEqual(journal['ops'][0]['state'], 'pending')
        self.assertEqual((project / 'existing.txt').read_text(encoding='utf-8'), 'REPLACED')
        res = tx.rollback(str(project), 'crash-window')
        self.assertEqual((res['status'], res['code'], res['unchecked']), ('success', 0, []))
        self.assertEqual((project / 'existing.txt').read_text(encoding='utf-8'), 'ORIGINAL')
        self.assertEqual([f['action'] for f in res['files']], ['restored'])
        self.assertEqual(tx.incomplete(str(project)), [])

    def test_rollback_after_crash_removes_a_file_it_created(self):
        project = self.root / 'law01-new'
        write(project, 'keep.txt', 'x')
        self.crash_after_replace(project, {'created.txt': 'NEW'})
        self.assertTrue((project / 'created.txt').exists())
        res = tx.rollback(str(project), 'crash-window')
        self.assertEqual((res['status'], res['code']), ('success', 0))
        self.assertFalse((project / 'created.txt').exists())

    def test_rollback_after_crash_keeps_backup_when_the_file_was_edited_again(self):
        """Không xác định được thì không báo thành công và không xóa bản sao lưu. / Undecidable: no success, backup kept."""
        project = self.root / 'law01-edit'
        write(project, 'existing.txt', 'ORIGINAL')
        tdir = self.crash_after_replace(project, {'existing.txt': 'REPLACED'})
        write(project, 'existing.txt', 'USER EDIT')
        res = tx.rollback(str(project), 'crash-window')
        self.assertEqual((res['status'], res['code']), ('partial', 1))
        self.assertEqual((project / 'existing.txt').read_text(encoding='utf-8'), 'USER EDIT')
        self.assertEqual((tdir / 'backup' / 'existing.txt').read_text(encoding='utf-8'), 'ORIGINAL')

    def test_resume_after_crash_between_replace_and_journal_finishes_cleanly(self):
        project = self.root / 'law01-resume'
        write(project, 'existing.txt', 'ORIGINAL')
        self.crash_after_replace(project, {'existing.txt': 'REPLACED'})
        res = tx.resume(str(project), 'crash-window')
        self.assertEqual((res['status'], res['code']), ('success', 0))
        self.assertEqual((project / 'existing.txt').read_text(encoding='utf-8'), 'REPLACED')
        self.assertEqual(tx.incomplete(str(project)), [])


if __name__ == '__main__':
    unittest.main()
