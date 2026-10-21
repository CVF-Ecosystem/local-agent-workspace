"""P-CTX1 owner checks (tools/context_update.py). Every write stays in a fresh temporary project with fake data.

Hash guards detect a changed read, they are not filesystem CAS; nothing here proves host enforcement, grants or acceptance.
"""
import copy
import hashlib
import importlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    import jsonschema
except ImportError:  # the schema check below is then reported as skipped, never replaced by a weaker one
    jsonschema = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import context_update as cu  # noqa: E402
import result_schema  # noqa: E402
import transaction as tx  # noqa: E402

WINDOWS = os.name == 'nt'
HEADINGS = cu.STATE_HEADINGS
STATE_REL = '.agent/STATE.md'
HANDOFF_REL = '.agent/HANDOFF.md'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def state_text(body='text', blank=True, extra_lines=0):
    gap = '\n' if blank else ''
    parts = ['# PROJECT STATE\n\n']
    for h in HEADINGS:
        parts.append('## %s\n%s%s\n\n' % (h, gap, body))
    return ''.join(parts) + ''.join('- extra\n' for _ in range(extra_lines))


def tree(root):
    """Every file and folder below root with bytes (None for folders): the whole project, runtime included."""
    out = {}
    for p in sorted(Path(root).rglob('*')):
        out[p.relative_to(root).as_posix()] = p.read_bytes() if p.is_file() else None
    return out


@unittest.skipUnless(WINDOWS, 'P-CTX1 writes only on Windows NTFS local')
class Base(unittest.TestCase):
    bootstrap = True

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='law-pctx1-')
        self.addCleanup(self._cleanup)
        self.junctions = []
        self.project = self.tmp
        self.state = state_text().encode('utf-8')
        self.handoff = b'None\n'
        os.makedirs(os.path.join(self.project, '.agent', 'runtime') if self.bootstrap else os.path.join(self.project, '.agent'))
        self.put(STATE_REL, self.state)
        self.put(HANDOFF_REL, self.handoff)

    def _cleanup(self):
        for j in self.junctions:
            try:
                os.rmdir(j)  # the junction itself, never its target's content
            except OSError:
                pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def path(self, rel):
        return os.path.join(self.project, *rel.split('/'))

    def put(self, rel, data):
        with open(self.path(rel), 'wb') as f:
            f.write(data)

    def get(self, rel):
        with open(self.path(rel), 'rb') as f:
            return f.read()

    def junction(self, link, target):
        os.makedirs(target, exist_ok=True)
        r = subprocess.run(['cmd', '/c', 'mklink', '/J', link, target], capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest('cannot create a junction here: ' + r.stdout + r.stderr)
        self.junctions.append(link)

    def new_state(self, body='moi'):
        return state_text(body).encode('utf-8')

    def update(self, target='state', content=None, expected=None):
        rel = cu.TARGETS[target]
        content = self.new_state() if content is None and target == 'state' else (b'handoff moi\n' if content is None else content)
        expected = sha(self.get(rel)) if expected is None else expected
        return cu.update(self.project, target, content, expected_before=expected)

    def runtime_files(self):
        base = Path(self.project, '.agent', 'runtime')
        return sorted(p.relative_to(self.project).as_posix() for p in base.rglob('*')) if base.exists() else None


class PreviewAndApply(Base):
    def test_preview_changes_nothing_and_never_says_written(self):
        before = tree(self.project)
        with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = cu.preview(self.project, 'state', self.new_state(), expected_before=sha(self.state))
        self.assertEqual((r['result'], r['status'], r['mode'], r['changes']), ('PREVIEW', 'preview', 'PREVIEW', False))
        self.assertEqual(r['planned_changes'][0]['path'], STATE_REL)
        self.assertEqual(r['planned_changes'][0]['after'], 'sha256:' + sha(self.new_state()))
        self.assertEqual(tree(self.project), before)

    def test_apply_writes_exact_bytes_for_both_targets(self):
        for target, rel, old in (('state', STATE_REL, self.state), ('handoff', HANDOFF_REL, self.handoff)):
            new = self.new_state('khác') if target == 'state' else 'Bàn giao mới\r\n'.encode('utf-8')
            r = cu.update(self.project, target, new, expected_before=sha(old))
            self.assertEqual((r['result'], r['changes'], r['mode']), ('WRITTEN', True, 'APPLY'), r)
            self.assertEqual(self.get(rel), new)
            self.assertEqual(r['after_sha256'], 'sha256:' + sha(new))
            self.assertTrue(r['txid'])

    def test_only_target_and_own_journal_change_and_private_files_are_cleaned(self):
        before = tree(self.project)
        r = self.update()
        after = tree(self.project)
        added = sorted(set(after) - set(before))
        txd = '.agent/runtime/transactions/' + r['txid']
        self.assertEqual(added, ['.agent/runtime/transactions', txd, txd + '/journal.json'])
        self.assertEqual([k for k in before if before[k] != after.get(k)], [STATE_REL])
        journal = json.loads(self.get(txd + '/journal.json'))
        self.assertEqual((journal['status'], journal['operation'], [o['path'] for o in journal['ops']]), ('committed', 'context-update', [STATE_REL]))
        self.assertNotIn(self.new_state().decode(), json.dumps(journal))  # contents never enter the journal

    def test_bytes_are_kept_verbatim(self):
        text = '﻿' + state_text('dòng cuối').replace('\n', '\r\n').rstrip('\r\n')  # BOM, CRLF, no final newline
        r = self.update(content=text.encode('utf-8'))
        self.assertEqual(r['result'], 'WRITTEN', r)
        self.assertEqual(self.get(STATE_REL), text.encode('utf-8'))

    def test_prune_false_is_requested_and_other_journals_stay_byte_identical(self):
        base = Path(self.project, '.agent', 'runtime', 'transactions')
        for i in range(25):
            d = base / ('20260101-0000%02d-aaaa%04d' % (i, i))
            d.mkdir(parents=True)
            (d / 'journal.json').write_text(json.dumps({'schema': tx.SCHEMA, 'id': d.name, 'status': 'committed', 'created': '2026-01-01T00:00:%02d' % i, 'ops': []}),
                                            encoding='utf-8')
        extra = d
        (extra / 'note.txt').write_bytes(b'keep me')
        before = tree(base)
        kwargs = []
        real = tx.Transaction

        def spy(*a, **k):
            kwargs.append(k)
            return real(*a, **k)

        with mock.patch.object(cu.transaction, 'Transaction', spy):
            r = self.update()
        self.assertEqual(r['result'], 'WRITTEN', r)
        self.assertEqual(kwargs, [{'prune': False}])
        after = tree(base)
        self.assertEqual({k: v for k, v in after.items() if k in before}, before)  # nothing removed or changed
        self.assertEqual(len(after) - len(before), 2)  # only this transaction's folder and journal

    def test_no_op_writes_nothing_and_skips_probe_and_journal(self):
        before = tree(self.project)
        with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = cu.update(self.project, 'state', self.state, expected_before=sha(self.state))
        self.assertEqual((r['result'], r['changes'], r['txid']), ('UNCHANGED', False, None))
        self.assertEqual(tree(self.project), before)

    def test_no_op_with_stale_hash_is_still_a_conflict(self):
        r = cu.update(self.project, 'state', self.state, expected_before=sha(b'older'))
        self.assertEqual((r['result'], r['reason'], r['changes']), ('CONFLICT', 'EXPECTED_BEFORE_MISMATCH', False))


class Refusals(Base):
    def assertRefused(self, r, reason, before):
        self.assertEqual((r['result'], r['reason'], r['changes']), ('ERROR', reason, False), r)
        self.assertEqual(tree(self.project), before)

    def test_stale_expected_hash_writes_nothing(self):
        before = tree(self.project)
        with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = cu.update(self.project, 'state', self.new_state(), expected_before=sha(b'not what was read'))
        self.assertEqual((r['result'], r['reason'], r['changes']), ('CONFLICT', 'EXPECTED_BEFORE_MISMATCH', False))
        self.assertEqual(tree(self.project), before)

    def test_file_changed_between_plan_and_commit_is_a_conflict_and_is_not_overwritten(self):
        other = b'edited by someone else\n'

        def hook(point, path):
            if point == 'commit' and self.get(STATE_REL) == self.state:
                self.put(STATE_REL, other)

        with mock.patch.object(tx, '_HOOK', hook):
            r = self.update()
        self.assertEqual((r['result'], r['reason'], r['changes']), ('CONFLICT', 'CHANGED_AFTER_PLANNING', False), r)
        self.assertEqual(self.get(STATE_REL), other)
        self.assertTrue(r['txid'] and tx.incomplete(self.project))  # the open journal is reported, never auto-resumed

    def test_file_changed_between_read_and_plan_is_a_conflict_before_any_probe(self):
        other = b'edited after the read\n'

        def changed(project, *, strict=False):
            self.put(STATE_REL, other)
            return []

        with mock.patch.object(tx, 'incomplete', changed), mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = self.update()
        self.assertEqual((r['result'], r['reason'], r['changes']), ('CONFLICT', 'EXPECTED_BEFORE_MISMATCH', False), r)
        self.assertEqual(self.get(STATE_REL), other)
        self.assertEqual(self.runtime_files(), [])

    def test_missing_target_is_refused_not_created(self):
        for target, rel in (('state', STATE_REL), ('handoff', HANDOFF_REL)):
            os.remove(self.path(rel))
            before = tree(self.project)
            r = cu.update(self.project, target, b'x\n' if target == 'handoff' else self.new_state(), expected_before=sha(b''))
            self.assertRefused(r, 'TARGET_MISSING', before)
            self.assertFalse(os.path.exists(self.path(rel)))

    def test_target_that_is_a_folder_is_unsafe(self):
        os.remove(self.path(HANDOFF_REL))
        os.mkdir(self.path(HANDOFF_REL))
        before = tree(self.project)
        r = cu.update(self.project, 'handoff', b'x\n', expected_before=sha(b''))
        self.assertRefused(r, 'TARGET_UNSAFE', before)

    def test_target_symlink_is_unsafe(self):
        outside = os.path.join(self.tmp + '-out.txt')
        self.addCleanup(lambda: os.path.exists(outside) and os.remove(outside))
        with open(outside, 'wb') as f:
            f.write(self.handoff)
        os.remove(self.path(HANDOFF_REL))
        try:
            os.symlink(outside, self.path(HANDOFF_REL))
        except (OSError, NotImplementedError):
            self.skipTest('cannot create a file symlink here')
        r = cu.update(self.project, 'handoff', b'x\n', expected_before=sha(self.handoff))
        self.assertEqual((r['result'], r['reason'], r['changes']), ('ERROR', 'TARGET_UNSAFE', False))
        with open(outside, 'rb') as f:
            self.assertEqual(f.read(), self.handoff)

    def test_each_missing_bootstrap_parent_is_refused_and_nothing_is_created(self):
        shutil.rmtree(os.path.join(self.project, '.agent'))
        before = tree(self.project)
        with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = cu.update(self.project, 'state', self.new_state(), expected_before=sha(self.state))
        self.assertRefused(r, 'RUNTIME_PARENT_MISSING', before)
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent')))
        os.makedirs(os.path.join(self.project, '.agent'))
        self.put(STATE_REL, self.state)
        before = tree(self.project)  # .agent exists, .agent/runtime does not
        with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = cu.update(self.project, 'state', self.new_state(), expected_before=sha(self.state))
        self.assertRefused(r, 'RUNTIME_PARENT_MISSING', before)
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent', 'runtime')))

    def test_linked_runtime_agent_or_root_is_refused_before_any_write(self):
        real_runtime = self.tmp + '-elsewhere'
        self.addCleanup(shutil.rmtree, real_runtime, True)
        os.rmdir(os.path.join(self.project, '.agent', 'runtime'))
        self.junction(os.path.join(self.project, '.agent', 'runtime'), real_runtime)
        before = tree(self.project)
        r = self.update()
        self.assertRefused(r, 'RUNTIME_LINKED', before)
        self.assertEqual(os.listdir(real_runtime), [])
        os.rmdir(os.path.join(self.project, '.agent', 'runtime'))
        os.makedirs(os.path.join(self.project, '.agent', 'runtime'))
        # root itself reached through a junction
        link = self.tmp + '-link'
        self.junction(link, self.project)
        r = cu.update(link, 'state', self.new_state(), expected_before=sha(self.state))
        self.assertEqual((r['result'], r['reason'], r['changes']), ('ERROR', 'ROOT_LINKED', False))
        self.assertEqual(self.get(STATE_REL), self.state)

    def test_linked_agent_folder_is_refused(self):
        elsewhere = self.tmp + '-agent'
        self.addCleanup(shutil.rmtree, elsewhere, True)
        shutil.move(os.path.join(self.project, '.agent'), elsewhere)
        self.junction(os.path.join(self.project, '.agent'), elsewhere)
        before = dict(tree(elsewhere))
        r = self.update()
        self.assertEqual((r['result'], r['reason'], r['changes']), ('ERROR', 'RUNTIME_LINKED', False))
        self.assertEqual(tree(elsewhere), before)

    def test_missing_pin_is_refused_before_any_write(self):
        before = tree(self.project)
        with mock.patch.object(tx, 'PIN_ENABLED', False), mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = self.update()
        self.assertRefused(r, 'PIN_UNAVAILABLE', before)

    def test_unknown_filesystem_or_platform_is_refused(self):
        before = tree(self.project)
        with mock.patch.object(cu._pn, 'volume_supported', return_value=(False, {})):
            self.assertRefused(self.update(), 'UNSUPPORTED_FS', before)
        with mock.patch.object(os, 'name', 'posix'):
            self.assertEqual(cu._platform_problem(self.project), 'UNSUPPORTED_FS')

    def test_parents_are_pinned_before_the_first_probe_and_mkdir(self):
        seen = []
        real_probe = tx.probe_writable
        agent, runtime = os.path.join(self.project, '.agent'), os.path.join(self.project, '.agent', 'runtime')

        def probe(project):
            for folder in (runtime, agent, self.project):
                with self.assertRaises(OSError):
                    os.rename(folder, folder + '-moved')  # a held folder handle blocks the rename
            seen.append(os.path.exists(os.path.join(runtime, 'transactions')))
            return real_probe(project)

        with mock.patch.object(tx, 'probe_writable', probe):
            r = self.update()
        self.assertEqual(r['result'], 'WRITTEN', r)
        self.assertEqual(seen, [False])  # the probe came before any transaction folder existed

    def test_unfinished_transaction_blocks_without_touching_it(self):
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'commit:1'}):
            r1 = self.update()
        self.assertEqual(r1['result'], 'WRITTEN')
        before = tree(self.project)
        r2 = self.update(content=self.new_state('lần hai'), expected=sha(self.get(STATE_REL)))
        self.assertRefused(r2, 'TRANSACTION_UNFINISHED', before)
        self.assertEqual(r2['detail'], r1['txid'])

    def test_unreadable_transaction_status_is_refused_before_probe_or_write(self):
        before = tree(self.project)
        with mock.patch.object(tx, 'incomplete', side_effect=PermissionError('cannot list transactions')), \
                mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = self.update()
        self.assertRefused(r, 'TRANSACTION_STATUS_UNREADABLE', before)

    def test_corrupt_or_unreadable_journal_is_not_treated_as_clean(self):
        base = Path(self.project, '.agent', 'runtime', 'transactions')
        journal_dir = base / '20260101-000000-aaaa0000'
        journal_dir.mkdir(parents=True)
        journal = journal_dir / 'journal.json'
        for data in (b'{broken', b'[]', b'{"schema":"' + tx.SCHEMA.encode() + b'","status":"unknown","ops":[]}',
                     json.dumps({'schema': tx.SCHEMA, 'status': 'prepared', 'ops': [None]}).encode()):
            journal.write_bytes(data)
            before = tree(self.project)
            with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
                self.assertRefused(self.update(), 'TRANSACTION_STATUS_UNREADABLE', before)
        journal.write_text(json.dumps({'schema': tx.SCHEMA, 'status': 'prepared', 'ops': []}), encoding='utf-8')
        before = tree(self.project)
        with mock.patch.object(tx, '_load', side_effect=PermissionError('cannot read journal')), \
                mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            self.assertRefused(self.update(), 'TRANSACTION_STATUS_UNREADABLE', before)

    def test_unreadable_journal_directory_is_refused(self):
        base = Path(self.project, '.agent', 'runtime', 'transactions')
        base.mkdir()
        before = tree(self.project)
        with mock.patch.object(tx.os, 'listdir', side_effect=PermissionError('cannot list journals')), \
                mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
            r = self.update()
        self.assertRefused(r, 'TRANSACTION_STATUS_UNREADABLE', before)

    def test_non_directory_or_orphan_transaction_base_is_refused(self):
        base = Path(self.project, '.agent', 'runtime', 'transactions')
        base.write_bytes(b'not a directory')
        before = tree(self.project)
        self.assertRefused(self.update(), 'TRANSACTION_STATUS_UNREADABLE', before)
        base.unlink()
        (base / 'orphan').mkdir(parents=True)
        before = tree(self.project)
        self.assertRefused(self.update(), 'TRANSACTION_STATUS_UNREADABLE', before)


class Outcomes(Base):
    def test_fault_before_replace_reports_no_change_and_leaves_old_bytes(self):
        base = Path(self.project, '.agent', 'runtime', 'transactions')
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'stage:1'}):
            r = self.update()
        self.assertEqual((r['result'], r['changes']), ('ERROR', False), r)
        self.assertEqual(self.get(STATE_REL), self.state)
        self.assertEqual(tx.incomplete(self.project), [])  # abandoned, nothing open
        for d in base.iterdir():
            self.assertFalse((d / 'staging').exists() or (d / 'backup').exists())

    def test_error_after_replace_is_never_reported_as_unchanged(self):
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'commit:1'}):
            r = self.update()
        self.assertEqual((r['result'], r['reason'], r['changes']), ('WRITTEN', 'COMPLETION_ERROR', True), r)
        self.assertEqual(self.get(STATE_REL), self.new_state())
        self.assertTrue(r['txid'] and r['detail'])

    def test_unprovable_outcome_is_unknown_with_changes_none(self):
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'commit:1'}), mock.patch.object(cu, '_file_sha', return_value=None):
            r = self.update()
        self.assertEqual((r['result'], r['reason'], r['changes'], r['status']), ('UNKNOWN', 'OUTCOME_UNPROVEN', None, 'partial'), r)

    def test_post_write_mismatch_is_unknown(self):
        with mock.patch.object(cu, '_file_sha', return_value='f' * 64):
            r = self.update()
        self.assertEqual((r['result'], r['reason'], r['changes']), ('UNKNOWN', 'POST_WRITE_VERIFY_MISMATCH', None), r)

    def test_unreplaceable_target_reports_no_change(self):
        os.chmod(self.path(STATE_REL), 0o444)
        self.addCleanup(os.chmod, self.path(STATE_REL), 0o666)
        r = self.update()
        self.assertEqual((r['result'], r['changes']), ('ERROR', False), r)
        self.assertEqual(self.get(STATE_REL), self.state)


class Validation(Base):
    def refused(self, target, content, reason):
        before = tree(self.project)
        r = cu.update(self.project, target, content, expected_before=sha(self.get(cu.TARGETS[target])))
        self.assertEqual((r['result'], r['reason'], r['changes']), ('ERROR', reason, False), r)
        self.assertEqual(tree(self.project), before)

    def test_state_frame_is_enforced(self):
        good = state_text()
        lines = good.split('\n')
        self.refused('state', good.replace('## Decisions', '## Decision').encode(), 'STATE_HEADINGS')
        self.refused('state', good.replace('## Goal\n', '').encode(), 'STATE_HEADINGS')
        self.refused('state', (good + '## Extra\n\nx\n').encode(), 'STATE_HEADINGS')
        self.refused('state', (good + '## Goal\n\nx\n').encode(), 'STATE_HEADINGS')
        swapped = good.replace('## Goal', '## @@').replace('## Decisions', '## Goal').replace('## @@', '## Decisions')
        self.refused('state', swapped.encode(), 'STATE_HEADINGS')
        self.refused('state', state_text(blank=False).encode(), 'STATE_BLANK_AFTER_HEADING')
        self.refused('state', (good.rstrip('\n') + '\n').replace('## Next milestone\n\ntext', '## Next milestone').encode(), 'STATE_BLANK_AFTER_HEADING')

    def test_state_line_limit_is_sixty(self):
        base = state_text().split('\n')
        n = len(base) - 1
        ok = state_text(extra_lines=60 - n)
        self.assertEqual(len(ok.split('\n')) - 1, 60)
        self.assertEqual(cu.update(self.project, 'state', ok.encode(), expected_before=sha(self.state))['result'], 'WRITTEN')
        self.refused('state', state_text(extra_lines=61 - n).encode(), 'STATE_TOO_LONG')

    def test_handoff_has_no_line_limit(self):
        big = ('dòng\n' * 5000).encode('utf-8')
        r = cu.update(self.project, 'handoff', big, expected_before=sha(self.handoff))
        self.assertEqual((r['result'], r['changes']), ('WRITTEN', True), r)
        self.assertEqual(self.get(HANDOFF_REL), big)

    def test_content_must_be_valid_non_empty_utf8_text_within_size(self):
        self.refused('handoff', b'', 'CONTENT_EMPTY')
        self.refused('handoff', b'\xff\xfe bad', 'CONTENT_NOT_UTF8')
        self.refused('handoff', b'a\x00b', 'CONTENT_NOT_TEXT')
        self.refused('state', b'\x80', 'CONTENT_NOT_UTF8')
        with mock.patch.object(cu, 'MAX_BYTES', 10):
            self.refused('handoff', b'x' * 11, 'CONTENT_TOO_LARGE')

    def test_argument_shapes(self):
        before = tree(self.project)
        h = sha(self.handoff)
        cases = [
            (dict(target='other'), 'TARGET_INVALID'), (dict(target='.agent/STATE.md'), 'TARGET_INVALID'), (dict(target='STATE'), 'TARGET_INVALID'),
            (dict(target=None), 'TARGET_INVALID'),
            (dict(content='text'), 'CONTENT_INVALID'), (dict(content=None), 'CONTENT_INVALID'),
            (dict(expected_before=None), 'EXPECTED_BEFORE_INVALID'), (dict(expected_before=h.upper()), 'EXPECTED_BEFORE_INVALID'),
            (dict(expected_before=h[:-1]), 'EXPECTED_BEFORE_INVALID'), (dict(expected_before=''), 'EXPECTED_BEFORE_INVALID'),
            (dict(expected_before=b'x'), 'EXPECTED_BEFORE_INVALID'),
            (dict(project_root=''), 'PROJECT_INVALID'), (dict(project_root=None), 'PROJECT_INVALID'),
        ]
        for over, reason in cases:
            a = dict(project_root=self.project, target='handoff', content=b'x\n', expected_before=h)
            a.update(over)
            with mock.patch.object(tx, 'probe_writable', side_effect=AssertionError('probe')):
                r = cu.update(a['project_root'], a['target'], a['content'], expected_before=a['expected_before'])
            self.assertEqual((r['result'], r['reason'], r['changes']), ('ERROR', reason, False), (over, r))
        self.assertEqual(tree(self.project), before)
        with self.assertRaises(TypeError):
            cu.update(self.project, 'handoff', b'x\n', h)  # expected_before is keyword-only

    def test_prefixed_expected_hash_is_accepted(self):
        r = cu.update(self.project, 'handoff', b'x\n', expected_before='sha256:' + sha(self.handoff))
        self.assertEqual(r['result'], 'WRITTEN')

    def test_content_that_looks_like_a_command_or_json_is_only_text(self):
        text = '{"cmd": "python -c \\"import os; os.remove(1)\\""}\n# ROOT: rm -rf\n'.encode('utf-8')
        r = cu.update(self.project, 'handoff', text, expected_before=sha(self.handoff))
        self.assertEqual(r['result'], 'WRITTEN')
        self.assertEqual(self.get(HANDOFF_REL), text)
        self.assertEqual(self.get(STATE_REL), self.state)


POLICY = ROOT / '.cvf' / 'rules' / 'v3' / 'ROUTING_POLICY.json'
SCHEMA = ROOT / '.cvf' / 'contracts' / 'v3' / 'control.schema.json'
ENTRY = ROOT / '.cvf' / 'checks' / 'control_check_v3.py'
PRIOR_POLICY_SHA = '255d76c66021c4f1931f97417bff437cd4f903166d40a891d6d1f9f3e2e49457'  # policy bytes before the P-CTX1 field was added
WRITER_PIN = '8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852'
NOTE_ADDED = ' Also declares operational_context_protocol P-CTX1'
FIELD = 'operational_context_protocol'


def without_ctx(policy):
    """The policy as it was before this amendment: drop the field, its unsupported entry and the note sentence."""
    old = copy.deepcopy(policy)
    old.pop(FIELD)
    old['unsupported_in_candidate'].remove('OPERATIONAL_CONTEXT_P_CTX1_CHECKER_EVALUATION')
    old['note'] = old['note'][:old['note'].index(NOTE_ADDED)]
    return old


def dumps_policy(policy):
    return (json.dumps(policy, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


class TemplateValidation(unittest.TestCase):
    def test_clean_release_state_template_passes_content_validation(self):
        content = (ROOT / 'release_templates' / '.agent' / 'STATE.md').read_bytes()
        self.assertIsNone(cu.content_problem('state', content))


class PolicyAmendment(unittest.TestCase):
    """The P-CTX1 declaration in policy v3: one field, pinned owner, no semantic change elsewhere, nothing evaluated."""

    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(POLICY.read_text(encoding='utf-8'))
        cls.field = cls.policy[FIELD]

    def test_pin_is_the_sha256_of_the_owner_entrypoint_bytes(self):
        data = (ROOT / 'tools' / 'context_update.py').read_bytes()
        self.assertEqual(self.field['entrypoint_sha256'], 'sha256:' + sha(data))
        self.assertEqual((self.field['entrypoint'], self.field['owner_tool']), ('tools/context_update.py', cu.TOOL_NAME))
        self.assertEqual((self.field['protocol_id'], self.field['protocol_version'], self.field['platform']), (cu.PROTOCOL, cu.PROTOCOL_VERSION, cu.PLATFORM))
        self.assertEqual(self.field['pin_semantics'], 'VERSION_COMPARE_ADVISORY')

    def test_field_matches_what_the_owner_enforces(self):
        self.assertEqual(self.field['target_paths'], [cu.TARGETS['state'], cu.TARGETS['handoff']])
        self.assertEqual((self.field['files_per_call'], self.field['existing_file_only'], self.field['transaction_prune']), (1, True, False))
        self.assertEqual([e['id'] for e in self.field['envelope']], ['C1', 'C2', 'C3', 'C4', 'C5'])
        self.assertEqual(self.field['grant_precondition']['checked_by'], 'ACTOR_BEFORE_CALL')
        self.assertEqual(self.field['artifact_checker_handling'], 'UNSUPPORTED')
        self.assertIn('NOT_ARTIFACT_PASS', self.field['non_authority'])
        self.assertIn('OPERATIONAL_CONTEXT_P_CTX1_CHECKER_EVALUATION', self.policy['unsupported_in_candidate'])

    def test_prior_policy_bytes_are_recovered_so_the_field_is_the_only_semantic_delta(self):
        self.assertEqual(sha(dumps_policy(without_ctx(self.policy))), PRIOR_POLICY_SHA)

    def test_pcn1_owner_protocol_and_writer_pin_are_unchanged(self):
        self.assertEqual([p['protocol_id'] for p in self.policy['owner_protocols']], ['P-CN1'])
        self.assertEqual(self.policy['owner_protocols'][0]['entrypoint_sha256'], 'sha256:' + WRITER_PIN)
        self.assertEqual([e['id'] for e in self.policy['owner_protocols'][0]['envelope']], ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'])
        self.assertEqual(sha((ROOT / 'tools' / 'publish_new.py').read_bytes()), WRITER_PIN)

    @unittest.skipIf(jsonschema is None, 'jsonschema not installed')
    def test_schema_accepts_the_policy_and_rejects_shape_drift(self):
        schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
        validator = jsonschema.Draft202012Validator({'$ref': '#/$defs/routing_policy', '$defs': schema['$defs']})
        self.assertEqual(list(validator.iter_errors(self.policy)), [])

        def field(p):
            return p[FIELD]

        mutations = {
            'field missing': lambda p: p.pop(FIELD),
            'extra key': lambda p: field(p).__setitem__('extra', 1),
            'pin not a digest': lambda p: field(p).__setitem__('entrypoint_sha256', 'sha256:abc'),
            'third path': lambda p: field(p)['target_paths'].append('.agent/INDEX.md'),
            'other path': lambda p: field(p)['target_paths'].__setitem__(0, 'PROJECT.md'),
            'two files per call': lambda p: field(p).__setitem__('files_per_call', 2),
            'prune on': lambda p: field(p).__setitem__('transaction_prune', True),
            'envelope reordered': lambda p: field(p)['envelope'].reverse(),
            'envelope longer': lambda p: field(p)['envelope'].append(dict(field(p)['envelope'][0])),
            'envelope other scope': lambda p: field(p)['envelope'][3].__setitem__('path_scope', 'RUNTIME_ANY'),
            'grant not required': lambda p: field(p)['grant_precondition'].__setitem__('required', False),
            'checker handling pass': lambda p: field(p).__setitem__('artifact_checker_handling', 'PASS'),
            'other protocol id': lambda p: field(p).__setitem__('protocol_id', 'P-CN1'),
            'posix platform': lambda p: field(p).__setitem__('platform', 'posix'),
            'entrypoint missing': lambda p: field(p).pop('entrypoint'),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                p = copy.deepcopy(self.policy)
                mutate(p)
                self.assertTrue(list(validator.iter_errors(p)), name)

    def test_routing_is_identical_with_and_without_the_field_and_state_writes_stay_unresolved(self):
        spec = importlib.util.spec_from_file_location('law_cvf_entry_v3_ctx_test', str(ENTRY))
        entry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(entry)
        entry._load_package()
        routing = importlib.import_module('law_cvf_check_v3.routing')
        now = routing.load_route_policy(POLICY.read_bytes())
        old = routing.load_route_policy(dumps_policy(without_ctx(self.policy)))
        bundle = json.loads((ROOT / '.cvf' / 'contracts' / 'v3' / 'examples' / 'ex01_pcn1_working_request.json').read_text(encoding='utf-8'))
        task = [r for r in bundle['records'] if r['record_type'] == 'task'][0]
        for target in ('working/w/x.docx', cu.TARGETS['state'], cu.TARGETS['handoff']):
            for op in ('create_new', 'overwrite'):
                for phase in ('dispatch', 'effect', 'accept'):
                    t = copy.deepcopy(task)
                    t['effects']['actions'][0].update(targets=[target], operation=op)
                    a, b = routing.evaluate_task(t, now, phase), routing.evaluate_task(t, old, phase)
                    self.assertEqual((list(a.matched), a.status), (list(b.matched), b.status), (target, op, phase))
                    if target != 'working/w/x.docx':
                        self.assertIn('R-UNCLASSIFIED', a.matched)
                        self.assertEqual(a.status, 'UNRESOLVED')

    def test_no_checker_module_reads_the_field(self):
        for path in (ROOT / '.cvf' / 'checks').rglob('*.py'):
            self.assertNotIn(FIELD, path.read_text(encoding='utf-8'), path.name)


class Cli(Base):
    def run_cli(self, *args):
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        env.pop(tx.FAULT_ENV, None)
        cmd = [sys.executable, '-I', str(ROOT / 'tools' / 'context_update.py'), '--project', self.project] + list(args)
        return subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, encoding='utf-8', timeout=120)

    def content_file(self, data):
        p = os.path.join(self.tmp + '-content.bin')
        self.addCleanup(lambda: os.path.exists(p) and os.remove(p))
        with open(p, 'wb') as f:
            f.write(data)
        return p

    def test_default_is_preview_and_apply_writes(self):
        new = self.new_state('cli')
        f = self.content_file(new)
        before = tree(self.project)
        r = self.run_cli('--target', 'state', '--content', f, '--expected', 'sha256:' + sha(self.state), '--result-json')
        env = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, env['result'], env['changes']), (0, 'PREVIEW', False), r.stderr)
        self.assertEqual(tree(self.project), before)
        r = self.run_cli('--target', 'state', '--content', f, '--expected', 'sha256:' + sha(self.state), '--apply', '--result-json')
        env = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, env['result'], env['changes']), (0, 'WRITTEN', True), r.stderr)
        self.assertEqual(self.get(STATE_REL), new)

    def test_exit_codes(self):
        f = self.content_file(self.new_state('x'))
        r = self.run_cli('--target', 'state', '--content', f, '--expected', 'sha256:' + sha(b'stale'), '--apply', '--result-json')
        self.assertEqual((r.returncode, result_schema.split_output(r.stdout)[1]['result']), (3, 'CONFLICT'))
        r = self.run_cli('--target', 'state', '--content', self.content_file(b'bad'), '--expected', 'sha256:' + sha(self.state), '--apply', '--result-json')
        self.assertEqual((r.returncode, result_schema.split_output(r.stdout)[1]['reason']), (4, 'STATE_HEADINGS'))
        r = self.run_cli('--target', 'state', '--content', f, '--expected', sha(self.state))
        self.assertEqual(r.returncode, 2)  # --expected must carry the sha256: prefix
        r = self.run_cli('--target', 'elsewhere', '--content', f, '--expected', 'sha256:' + sha(self.state))
        self.assertEqual(r.returncode, 2)
        r = self.run_cli('--target', 'state', '--content', f + '.missing', '--expected', 'sha256:' + sha(self.state))
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.get(STATE_REL), self.state)


if __name__ == '__main__':
    unittest.main()
