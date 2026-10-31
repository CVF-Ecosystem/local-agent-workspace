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
import check_package as cp

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


class LegacyCreateCompatibility(unittest.TestCase):
    """Default create labels remain v1; only explicit intake transactions opt in to v2."""
    def test_default_mixed_write_create_create_exclusive_recovery(self):
        with tempfile.TemporaryDirectory(prefix='tx-legacy-create-') as folder:
            project = Path(folder)
            write(project, 'old.txt', 'old')
            transaction = tx.Transaction(folder, 'legacy-mixed')
            transaction.add('old.txt', b'new', 'write')
            transaction.add('created.txt', b'created', 'create')
            transaction.add('pending.new', b'pending', 'create_exclusive')
            self.assertEqual(transaction.journal['schema'], tx.SCHEMA)
            with patch.dict(os.environ, {FAULT: 'commit:1'}):
                with self.assertRaises(OSError): transaction.run()
            self.assertEqual(tx._load(folder, transaction.txid)['schema'], tx.SCHEMA)
            self.assertEqual(tx.resume(folder, transaction.txid)['code'], 0)
            self.assertEqual((project / 'created.txt').read_bytes(), b'created')
            self.assertEqual((project / 'pending.new').read_bytes(), b'pending')


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
        """Use the consumer projection: clean context/profile, no live user files or branding."""
        dst = self.root / name
        cp.materialize(str(dst), branding=False)
        return dst

    def test_package_fixture_never_reads_live_user_files_or_copies_workspace(self):
        real_open = open
        def bounded_open(path, *args, **kwargs):
            if isinstance(path, (str, os.PathLike)):
                full = Path(path).resolve()
                if ROOT in full.parents:
                    rel = full.relative_to(ROOT).as_posix()
                    normalized = rel[3:] if rel.startswith('en/') else rel
                    if normalized in cp.USER_FILES or (cp.in_user_dir(rel) and not cp.package_readme(rel)):
                        self.fail('consumer fixture attempted to read live user content: ' + rel)
            return real_open(path, *args, **kwargs)
        with patch('shutil.copytree', side_effect=AssertionError('copytree is forbidden for this fixture')), patch('builtins.open', side_effect=bounded_open):
            pkg = self.package('bounded-package')
        self.assertEqual([p.name for p in (pkg / 'working').iterdir()], ['README.md'])
        self.assertFalse((pkg / '.agent/runtime').exists())
        self.assertFalse((pkg / 'release_templates').exists())
        self.assertEqual((pkg / cp.PROFILE_REL).read_bytes(), cp._ep().clean_profile_bytes())

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
        pkg = self.package('pkg-dry')
        r = run('adopt_project.py', '--project', target, '--name', 'Example', base=pkg)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(snapshot(target), before)
        self.assertFalse((target / '.agent' / 'runtime').exists())
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

    def seed_journals(self, proj, count):
        base = proj / '.agent' / 'runtime' / 'transactions'
        for i in range(count):
            d = base / ('20260101-0000%02d-aaaa%04d' % (i, i))
            d.mkdir(parents=True)
            (d / 'journal.json').write_text(json.dumps({'schema': tx.SCHEMA, 'id': d.name, 'status': 'committed',
                                                        'created': '2026-01-01T00:00:%02d' % i, 'ops': []}), encoding='utf-8')
        return base

    def test_prune_false_keeps_other_journals_on_success_and_default_still_prunes(self):
        for prune, expected in ((False, 26), (True, 20)):
            proj = self.root / ('prune-%s' % prune)
            write(proj, 'a.txt', 'orig')
            base = self.seed_journals(proj, 25)
            before = {p.name: (p / 'journal.json').read_bytes() for p in base.iterdir()}
            t = tx.Transaction(str(proj), 'context-update', prune=prune)
            t.add('a.txt', b'new')
            t.run()
            self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'new')
            after = {p.name: (p / 'journal.json').read_bytes() for p in base.iterdir() if (p / 'journal.json').exists()}
            self.assertEqual(len(after), expected, prune)
            if not prune:
                self.assertEqual({k: v for k, v in after.items() if k in before}, before)  # byte identical, none removed
            self.assertFalse((base / t.txid / 'staging').exists() or (base / t.txid / 'backup').exists())  # own private files go either way

    def test_prune_false_keeps_runtime_folders_when_preflight_fails_default_removes_the_empty_ones(self):
        Usage = collections.namedtuple('Usage', 'total used free')
        for prune in (False, True):
            proj = self.root / ('pre-%s' % prune)
            write(proj, 'a.txt', 'orig')
            (proj / '.agent' / 'runtime').mkdir(parents=True)
            t = tx.Transaction(str(proj), 'context-update', prune=prune)
            t.add('a.txt', b'new')
            with patch('shutil.disk_usage', return_value=Usage(10 ** 9, 10 ** 9, 0)):
                with self.assertRaises(tx.TransactionError):
                    t.run()
            self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'orig')
            self.assertEqual((proj / '.agent' / 'runtime').exists(), not prune)  # default: pruned as before; prune=False: parents stay

    def test_prune_false_keeps_other_journals_when_stage_fails(self):
        proj = self.root / 'stage-fail'
        write(proj, 'a.txt', 'orig')
        base = self.seed_journals(proj, 3)
        before = {p.name: (p / 'journal.json').read_bytes() for p in base.iterdir()}
        t = tx.Transaction(str(proj), 'context-update', prune=False)
        t.add('a.txt', b'new')
        with patch.dict(os.environ, {FAULT: 'stage:1'}):
            with self.assertRaises(tx.TransactionError):
                t.run()
        self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'orig')
        after = {p.name: (p / 'journal.json').read_bytes() for p in base.iterdir()}
        self.assertEqual({k: v for k, v in after.items() if k in before}, before)
        self.assertEqual(tx.incomplete(str(proj)), [])

    def test_prune_is_keyword_only_and_default_true(self):
        t = tx.Transaction(str(self.root), 'x')
        self.assertTrue(t._prune)
        with self.assertRaises(TypeError):
            tx.Transaction(str(self.root), 'x', None, False)

    def test_strict_incomplete_refuses_bad_journal_default_still_skips_it(self):
        proj = self.root / 'strict-scan'
        base = proj / '.agent' / 'runtime' / 'transactions'
        self.assertEqual(tx.incomplete(str(proj), strict=True), [])
        journal = base / '20260101-000000-aaaa0000' / 'journal.json'
        journal.parent.mkdir(parents=True)
        journal.write_bytes(b'{broken')
        self.assertEqual(tx.incomplete(str(proj)), [])
        with self.assertRaises(tx.TransactionError):
            tx.incomplete(str(proj), strict=True)
        self.assertEqual(journal.read_bytes(), b'{broken')
        with patch.object(tx.os, 'lstat', side_effect=PermissionError('cannot inspect journal directory')):
            with self.assertRaises(PermissionError):
                tx.incomplete(str(proj), strict=True)

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



def make_dir_link(link, target):
    """A directory symlink, or a junction on Windows. False when this machine can create neither (e.g. Windows error 1314)."""
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        pass
    if os.name == 'nt':
        result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)], capture_output=True)
        return result.returncode == 0 and os.path.isdir(str(link))
    return False


def drop_dir_link(link):
    """Remove a directory link without touching its target; a link the code under test already removed is fine."""
    try:
        os.rmdir(str(link))
    except FileNotFoundError:
        return
    except OSError:
        os.unlink(str(link))


def tree(folder):
    return {str(p.relative_to(folder)): p.read_bytes() for p in sorted(Path(folder).rglob('*')) if p.is_file()}


class RuntimeLinks(unittest.TestCase):
    """A-06: the runtime folder and every write target must stay inside the project. Temp dirs; real junctions where possible."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='tx-links-')
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.count = 0

    def project(self):
        self.count += 1
        proj = self.root / ('proj%d' % self.count)
        write(proj, 'a.txt', 'orig')
        return proj

    def outside(self):
        folder = self.root / ('outside%d' % self.count)
        write(folder, 'sentinel.txt', 'keep')
        return folder

    def link(self, where, target):
        where.parent.mkdir(parents=True, exist_ok=True)
        if not make_dir_link(where, target):
            self.skipTest('this machine cannot create a directory symlink or junction')
        self.addCleanup(drop_dir_link, where)

    def test_runtime_components_that_are_links_stop_the_transaction_before_any_write(self):
        cases = {'.agent': ('.agent',), '.agent/runtime': ('.agent', 'runtime'),
                 '.agent/runtime/transactions': ('.agent', 'runtime', 'transactions'),
                 'transaction folder': ('.agent', 'runtime', 'transactions', 'fixed'),
                 'staging': ('.agent', 'runtime', 'transactions', 'fixed', 'staging'),
                 'backup': ('.agent', 'runtime', 'transactions', 'fixed', 'backup')}
        for name, parts in cases.items():
            with self.subTest(link=name):
                proj, out = self.project(), None
                out = self.outside()
                self.link(proj.joinpath(*parts), out)
                before = tree(out)
                t = tx.Transaction(str(proj), 'upgrade', txid='fixed')
                t.add('a.txt', b'new')
                with self.assertRaises((tx.TransactionError, OSError)):
                    t.run()
                self.assertEqual(tree(out), before, 'nothing was created, written or deleted outside the project')
                self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'orig')

    def test_a_target_that_passes_through_a_link_is_refused_when_planned(self):
        proj, out = self.project(), None
        out = self.outside()
        self.link(proj / 'docs', out)
        before = tree(out)
        t = tx.Transaction(str(proj), 'upgrade')
        with self.assertRaises(tx.TransactionError):
            t.add('docs/x.txt', b'data')
        self.assertEqual(tree(out), before)

    def test_a_journal_outside_the_project_is_never_read_resumed_or_rolled_back(self):
        proj = self.project()
        out = self.root / 'outside-runtime'
        evil = out / 'transactions' / 'evil'
        write(evil, 'staging/a.txt', 'pwned')
        journal = {'schema': tx.SCHEMA, 'id': 'evil', 'operation': 'upgrade', 'status': 'committing', 'created': 'x', 'updated': 'x',
                   'ops': [{'path': 'a.txt', 'action': 'write', 'before': tx.sha_bytes(b'orig'), 'after': tx.sha_bytes(b'pwned'),
                            'size': 5, 'state': 'pending'}]}
        write(evil, 'journal.json', json.dumps(journal))
        self.link(proj / '.agent' / 'runtime', out)
        before = tree(out)
        self.assertEqual(tx.incomplete(str(proj)), [], 'an outside journal is not listed as unfinished work')
        for call in (tx.resume, tx.rollback):
            with self.assertRaises(tx.TransactionError):
                call(str(proj), 'evil')
        status = run('transaction.py', 'status', '--project', proj)
        self.assertEqual(status.returncode, 2, status.stdout)
        self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'orig', 'the outside staged file was not applied')
        self.assertEqual(tree(out), before)

    def test_prune_never_deletes_through_a_link(self):
        proj = self.project()
        out = self.root / 'outside-runtime'
        for n in range(tx.KEEP_JOURNALS + 5):
            journal = {'schema': tx.SCHEMA, 'id': 'old%02d' % n, 'status': 'committed', 'created': '2026-01-%02d' % (n + 1), 'ops': []}
            write(out, 'transactions/old%02d/journal.json' % n, json.dumps(journal))
        self.link(proj / '.agent' / 'runtime', out)
        before = tree(out)
        tx.prune(str(proj))
        self.assertEqual(tree(out), before, 'older journals outside the project were not removed')

    def test_folders_are_released_after_success_and_after_failure(self):
        proj = self.project()
        t = tx.Transaction(str(proj), 'upgrade')
        t.add('sub/b.txt', b'one')
        t.run()
        os.rename(str(proj / 'sub'), str(proj / 'sub2'))  # fails on Windows if a folder handle leaked
        t2 = tx.Transaction(str(proj), 'upgrade')
        t2.add('a.txt', b'new')
        write(proj, 'a.txt', 'user edit')
        with self.assertRaises(tx.TransactionError):
            t2.run()
        os.rename(str(proj / '.agent'), str(proj / '.agent2'))
        self.assertEqual((proj / 'a.txt').read_text(encoding='utf-8'), 'user edit')

    def test_held_folder_cannot_be_swapped_but_can_be_written(self):
        if os.name != 'nt':
            self.skipTest('folder handles that block renaming are implemented for Windows only')
        proj = self.project()
        folder = proj / 'held'
        folder.mkdir()
        with tx.Pins() as pins:
            self.assertTrue(pins.hold(str(folder)))
            with self.assertRaises(PermissionError):
                os.rename(str(folder), str(proj / 'moved'))
            with self.assertRaises(PermissionError):
                os.rename(str(proj), str(self.root / 'renamed-parent'))
            (folder / 'x.txt').write_text('ok', encoding='utf-8')
        os.rename(str(folder), str(proj / 'moved'))
        self.assertEqual((proj / 'moved' / 'x.txt').read_text(encoding='utf-8'), 'ok')

    # ---- A-06 review fixes: the paths actually used (nested staging/backup, journal leaf), recovery, protection ----
    def prepared(self, proj, ops, txid='fixed'):
        """A transaction stopped after begin/stage/backup, before commit (what a crash in that window leaves behind)."""
        t = tx.Transaction(str(proj), 'upgrade', txid=txid)
        for rel, data in ops:
            t.add(rel, data)
        t.begin()
        t.stage()
        t.backup()
        t.close()
        return t

    def crashed_after_first_commit(self, proj, ops, txid='fixed'):
        t = tx.Transaction(str(proj), 'upgrade', txid=txid)
        for rel, data in ops:
            t.add(rel, data)
        with patch.dict(os.environ, {FAULT: 'commit:1'}):
            with self.assertRaises(OSError):
                t.run()
        return t

    def read(self, path):
        return Path(path).read_text(encoding='utf-8')

    def save_as_user_once(self, proj, name, text='USER SAVED'):
        state = {'done': False}

        def hook(point, path):
            if point in ('resume', 'rollback', 'commit') and os.path.basename(path) == name and not state['done']:
                state['done'] = True
                write(proj, os.path.relpath(path, proj).replace(os.sep, '/'), text)
        return hook, state

    def test_nested_staging_folder_that_is_a_link_stops_the_run(self):
        proj, out = self.project(), None
        out = self.outside()
        self.link(proj / '.agent' / 'runtime' / 'transactions' / 'fixed' / 'staging' / 'sub', out)
        before = tree(out)
        t = tx.Transaction(str(proj), 'upgrade', txid='fixed')
        t.add('sub/a.txt', b'data')
        with self.assertRaises((tx.TransactionError, OSError)):
            t.run()
        self.assertEqual(tree(out), before, 'nothing was written to, moved from or deleted in the outside folder')
        self.assertFalse((proj / 'sub' / 'a.txt').exists())

    def test_nested_backup_folder_that_is_a_link_stops_the_run(self):
        proj, out = self.project(), None
        out = self.outside()
        write(proj, 'sub/a.txt', 'orig')
        self.link(proj / '.agent' / 'runtime' / 'transactions' / 'fixed' / 'backup' / 'sub', out)
        before = tree(out)
        t = tx.Transaction(str(proj), 'upgrade', txid='fixed')
        t.add('sub/a.txt', b'new')
        with self.assertRaises((tx.TransactionError, OSError)):
            t.run()
        self.assertEqual(tree(out), before)
        self.assertEqual(self.read(proj / 'sub' / 'a.txt'), 'orig')

    def test_resume_refuses_a_staging_folder_that_became_a_link(self):
        proj, out = self.project(), None
        out = self.outside()
        write(proj, 'sub/a.txt', 'orig')
        t = self.prepared(proj, [('sub/a.txt', b'data')])
        write(out, 'a.txt', 'data')  # outside holds bytes whose hash equals the planned result
        staged = Path(t.stage_dir) / 'sub'
        shutil.rmtree(staged)
        self.link(staged, out)
        before = tree(out)
        with self.assertRaises(tx.TransactionError):
            tx.resume(str(proj), 'fixed')
        self.assertEqual(tree(out), before, 'the outside file was not moved into the project')
        self.assertEqual(self.read(proj / 'sub' / 'a.txt'), 'orig')

    def test_rollback_refuses_a_backup_folder_that_became_a_link(self):
        proj, out = self.project(), None
        out = self.outside()
        write(proj, 'sub/a.txt', 'orig')
        t = self.crashed_after_first_commit(proj, [('sub/a.txt', b'new')])
        self.assertEqual(self.read(proj / 'sub' / 'a.txt'), 'new')
        write(out, 'a.txt', 'orig')  # outside holds bytes whose hash equals the original
        backup = Path(t.backup_dir) / 'sub'
        shutil.rmtree(backup)
        self.link(backup, out)
        before = tree(out)
        with self.assertRaises(tx.TransactionError):
            tx.rollback(str(proj), 'fixed')
        self.assertEqual(tree(out), before)
        self.assertEqual(self.read(proj / 'sub' / 'a.txt'), 'new', 'nothing was restored from outside the project')

    def swap_with_link_hook(self, folder, out, name='a.txt'):
        state = {'done': False, 'blocked': None, 'swapped': False}

        def hook(point, path):
            if point != 'commit' or os.path.basename(path) != name or state['done']:
                return
            state['done'] = True
            try:
                os.rename(str(folder), str(folder) + '.real')
            except OSError as e:
                state['blocked'] = e
                return
            if not make_dir_link(folder, out):
                os.rename(str(folder) + '.real', str(folder))
                state['blocked'] = OSError('could not create the link')
                return
            state['swapped'] = True
            self.addCleanup(lambda: drop_dir_link(folder) if os.path.isdir(str(folder) + '.real') else None)
        return hook, state

    def test_swapping_the_staging_folder_at_commit_is_blocked_while_it_is_held(self):
        if os.name != 'nt':
            self.skipTest('held folders are implemented for Windows only')
        proj, out = self.project(), None
        out = self.outside()
        write(out, 'a.txt', 'data')
        before = tree(out)
        t = tx.Transaction(str(proj), 'upgrade', txid='fixed')
        t.add('sub/a.txt', b'data')
        hook, state = self.swap_with_link_hook(Path(t.stage_dir) / 'sub', out)
        with patch.object(tx, '_HOOK', hook):
            t.run()
        self.assertIsInstance(state['blocked'], PermissionError)
        self.assertEqual(self.read(proj / 'sub' / 'a.txt'), 'data')
        self.assertEqual(tree(out), before, 'the outside file was not moved away')

    def test_swapping_the_staging_folder_is_refused_when_nothing_can_be_held(self):
        proj, out = self.project(), None
        out = self.outside()
        write(out, 'a.txt', 'data')
        before = tree(out)
        t = tx.Transaction(str(proj), 'upgrade', txid='fixed')
        t.add('sub/a.txt', b'data')
        hook, state = self.swap_with_link_hook(Path(t.stage_dir) / 'sub', out)
        with patch.object(tx, 'PIN_ENABLED', False), patch.object(tx, '_HOOK', hook):
            with self.assertRaises(OSError):
                t.run()
        self.assertTrue(state['swapped'])
        self.assertEqual(tree(out), before, 'recheck-only mode still refuses before moving the outside file')
        self.assertFalse((proj / 'sub' / 'a.txt').exists())

    def test_resume_keeps_a_file_the_user_saved_after_the_first_check(self):
        proj = self.project()
        self.prepared(proj, [('a.txt', b'data')])
        hook, state = self.save_as_user_once(proj, 'a.txt')
        with patch.object(tx, '_HOOK', hook):
            res = tx.resume(str(proj), 'fixed')
        self.assertTrue(state['done'])
        self.assertEqual(self.read(proj / 'a.txt'), 'USER SAVED')
        self.assertEqual((res['status'], res['code']), ('partial', 1), 'not reported as success')
        self.assertIn('skipped_conflict', [f['action'] for f in res['files']])

    def test_rollback_keeps_a_file_the_user_saved_after_the_first_check(self):
        proj = self.project()
        t = self.crashed_after_first_commit(proj, [('a.txt', b'data')])
        self.assertEqual(self.read(proj / 'a.txt'), 'data')
        hook, state = self.save_as_user_once(proj, 'a.txt')
        with patch.object(tx, '_HOOK', hook):
            res = tx.rollback(str(proj), 'fixed')
        self.assertTrue(state['done'])
        self.assertEqual(self.read(proj / 'a.txt'), 'USER SAVED')
        self.assertEqual((res['status'], res['code']), ('partial', 1), 'not reported as success')
        self.assertTrue((Path(t.backup_dir) / 'a.txt').exists(), 'the original stays in backup for manual recovery')

    def test_recovery_and_idempotence_still_work_on_plain_paths(self):
        proj = self.project()
        self.prepared(proj, [('sub/b.txt', b'one'), ('a.txt', b'two')])
        res = tx.resume(str(proj), 'fixed')
        self.assertEqual(res['code'], 0)
        self.assertEqual((self.read(proj / 'sub' / 'b.txt'), self.read(proj / 'a.txt')), ('one', 'two'))
        self.assertEqual(tx.resume(str(proj), 'fixed')['code'], 0, 'idempotent')
        proj2 = self.project()
        self.crashed_after_first_commit(proj2, [('a.txt', b'two')])
        self.assertEqual(tx.rollback(str(proj2), 'fixed')['code'], 0)
        self.assertEqual(self.read(proj2 / 'a.txt'), 'orig')
        self.assertEqual(tx.rollback(str(proj2), 'fixed')['code'], 0, 'idempotent')

    def test_journal_leaf_that_is_a_link_is_not_followed(self):
        proj, out = self.project(), None
        out = self.outside()
        tmp_target = out / 'stolen.txt'
        write(out, 'stolen.txt', 'keep')
        txd = proj / '.agent' / 'runtime' / 'transactions' / 'fixed'
        txd.mkdir(parents=True)
        try:
            os.symlink(str(tmp_target), str(txd / 'journal.json.tmp'))
        except (OSError, NotImplementedError):
            self.skipTest('this machine cannot create a file symlink (Windows error 1314); no junction can stand in for a file')
        self.addCleanup(lambda: os.unlink(str(txd / 'journal.json.tmp')) if os.path.islink(str(txd / 'journal.json.tmp')) else None)
        before = tree(out)
        t = tx.Transaction(str(proj), 'upgrade', txid='fixed')
        t.add('a.txt', b'new')
        with self.assertRaises((tx.TransactionError, OSError)):
            t.run()
        self.assertEqual(tree(out), before)

    def test_protection_level_is_recorded_and_the_fallback_is_named(self):
        proj = self.project()
        t = tx.Transaction(str(proj), 'upgrade')
        t.add('a.txt', b'one')
        t.run()
        expected = 'held' if os.name == 'nt' else 'recheck_only'
        self.assertEqual(t.protection, expected)
        proj2 = self.project()
        t2 = tx.Transaction(str(proj2), 'upgrade')
        t2.add('a.txt', b'one')
        with patch.object(tx, 'PIN_ENABLED', False):
            t2.run()
        self.assertEqual(t2.protection, 'recheck_only', 'no handle means no claim of the Windows level of protection')
        journal = json.loads((proj2 / '.agent' / 'runtime' / 'transactions' / t2.txid / 'journal.json').read_text(encoding='utf-8'))
        self.assertEqual(journal['protection'], 'recheck_only')


if __name__ == '__main__':
    unittest.main()
