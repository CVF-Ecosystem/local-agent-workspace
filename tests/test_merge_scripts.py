"""D-01g checks: finish (never replace) for exactly two package scripts (D01G_SCRIPT_FINISH_ONLY).

Everything runs on fake data in temporary folders. FINISH_ALLOWLIST is the eight guides, the six instruction entrypoints and the two scripts
tools/audit_scripts.py and skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py (16); REPLACE_ALLOWLIST stays the eight guides.
The allowlist does NOT replace managed_paths: an allowed path that the MANIFEST does not list is refused as not_managed before any read.
The current script keeps its raw bytes at every step and a finished pair only has its .new stored and moved. The bytes are text: no case here
imports, compiles or runs a script, and the payloads carry side-effect sentinels and invalid Python only to prove that nothing ever executes them.
A finished pending does not prove that a script is correct, safe, runnable, accepted into the package or allowed to be used.
The lifecycle case uses the real shipped bytes (check_package.materialize, no branding; NOT a release) and the real new_project.py and upgrade_package.py CLIs.
"""
import builtins
import contextlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
import threading
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import app  # noqa: E402
import check_package as cp  # noqa: E402
import execution_profile as ep  # noqa: E402
import merge_center  # noqa: E402
import transaction as tx  # noqa: E402
from test_merge_entrypoints import changed, envelope, run, sha, tree_state, write  # noqa: E402  (functions only: no test class is collected from here)

WINDOWS = unittest.skipUnless(os.name == 'nt', 'the no-replace rename is only measured on Windows')
HAVE_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
GUIDES = ('docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md', 'docs/HUONG_DAN_SU_DUNG_VI.md', 'docs/HUONG_DAN_SKILLS_VI.md',
          'docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md', 'docs/en/NEW_PROJECT_GUIDE.md', 'docs/en/DAILY_USE_GUIDE.md',
          'docs/en/SKILLS_GUIDE.md', 'docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md')
ENTRYPOINTS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'en/AGENTS.md', 'en/CLAUDE.md', 'en/GEMINI.md')
SCRIPTS = ('tools/audit_scripts.py', 'skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py')  # written here independently of the owner code
# managed in the fake MANIFEST, but outside every allowlist / listed in the MANIFEST, outside every allowlist
OTHER = ('tools/helper.py', 'tools/other_tool.py', 'skills/local/shared/demo/scripts/run.py', '.cvf/checks/control_check_v3.py', 'PROJECT.md',
         'en/tools/audit_scripts.py')
PACK_SCRIPT = 'skills/local/packs/demo/scripts/pack_tool.py'  # managed through the pack tree, not through the MANIFEST
MARK = 'SCRIPT-PAYLOAD-MARKER-4417'
HEX_A, HEX_B = 'a' * 64, 'b' * 64
RECORD_KEYS = {'schema', 'record_version', 'finish_id', 'path', 'current_sha256', 'incoming_sha256', 'archive_txid'}
FINISH_ID_RE = re.compile(r'finish-[0-9a-f]{32}')


def current_script(rel, sentinel):
    """CRLF with one LF-only line (the user's mixed EOL); importing it would write a sentinel / importing it would touch a sentinel."""
    return ('# script hiện hành %s %s\r\nimport os\r\nopen(%r, "w").write("current ran")\r\nprint("dòng của người dùng")\r\n# dòng cuối chỉ LF\n'
            % (rel, MARK, os.path.join(sentinel, 'current'))).encode('utf-8')


def incoming_script(kind, rel, sentinel):
    """Text payloads that must never run: a side effect plus raise, or invalid Python."""
    if kind == 'poison':
        return ('# script mới %s %s\nimport os\nopen(%r, "w").write("pending ran")\nraise SystemExit("never")\n# Tiếng Việt: ưu tiên\n'
                % (rel, MARK, os.path.join(sentinel, 'pending'))).encode('utf-8')
    return ('def broken(:\n    ??? %s ??? %s\n' % (MARK, rel)).encode('utf-8')


def build_project(root, sentinel, kind='poison', unmanaged=()):
    """Fake project: the two scripts, other managed files and a pack script all carry a different .new; the fake MANIFEST lists all but `unmanaged`."""
    root = Path(root)
    for rel in SCRIPTS:
        write(root, rel, current_script(rel, sentinel))
        write(root, rel + '.new', incoming_script(kind, rel, sentinel))
    for rel in GUIDES[:2] + ENTRYPOINTS[:1] + OTHER + (PACK_SCRIPT,):
        write(root, rel, 'current ' + rel + '\n')
        write(root, rel + '.new', 'new ' + rel + '\n')
    write(root, 'output/report.txt', 'USER OUTPUT MARKER\n')
    write(root, 'working/notes.txt', 'WORKING MARKER\n')
    names = [n for n in SCRIPTS + GUIDES[:2] + ENTRYPOINTS[:1] + OTHER if n not in unmanaged]
    write(root, 'MANIFEST.sha256', '\n'.join('0' * 64 + '  ' + n for n in names) + '\n')
    return root


def dir_link(link, target):
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        if os.name == 'nt':
            return subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)], capture_output=True).returncode == 0
    return False


def drop_link(link):
    try:
        os.rmdir(str(link))
    except OSError:
        os.unlink(str(link))


class Base(unittest.TestCase):
    kind = 'poison'

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='law-d01g-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sentinel = self.root / 'sentinel'  # an executed payload would leave a file here / an executed payload would leave a file here
        self.sentinel.mkdir()
        self.project = build_project(self.root / 'project', str(self.sentinel), self.kind)

    def raw(self, rel, project=None):
        return (Path(project or self.project) / rel).read_bytes()

    def fpv(self, rel, project=None):
        return merge_center.preview_finish(str(project or self.project), rel + '.new')

    def fin(self, rel, pv=None):
        pv = pv or self.fpv(rel)
        return merge_center.apply_finish(str(self.project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])

    def obs(self, rel, pv):
        return merge_center.observe_finish(str(self.project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])

    def archive(self, pv, name):
        return self.project / '.agent' / 'merge-backups' / pv['finish_id'] / name

    def expected_reason(self):
        return None if os.name == 'nt' else 'os_unsupported'

    def untouched(self):
        """Check execution traces; their absence alone does not prove that compilation never occurred."""
        self.assertEqual(list(self.sentinel.iterdir()), [])
        self.assertEqual([p for p in self.root.rglob('*') if p.suffix == '.pyc' or p.name == '__pycache__'], [])
        loaded = [n for n, m in list(sys.modules.items()) if str(getattr(m, '__file__', None) or '').startswith(str(self.project))]
        self.assertEqual(loaded, [])

    @contextlib.contextmanager
    def no_execution(self):
        """Traps compile/exec/eval of the payload text, new processes and imports from the project during a call (the owner code never needs them)."""
        def guard(real):
            def wrapped(source, *args, **kwargs):
                text = source.decode('utf-8', 'replace') if isinstance(source, bytes) else str(source)
                if MARK in text or any(isinstance(a, str) and str(self.project) in a for a in args[:1]):
                    raise AssertionError('script text was compiled or executed')
                return real(source, *args, **kwargs)
            return wrapped
        trap = AssertionError('a process was started')
        with contextlib.ExitStack() as stack:
            for name in ('compile', 'exec', 'eval'):
                stack.enter_context(patch.object(builtins, name, guard(getattr(builtins, name))))
            stack.enter_context(patch.object(subprocess, 'Popen', side_effect=trap))
            stack.enter_context(patch.object(os, 'system', side_effect=trap))
            if hasattr(os, 'startfile'):
                stack.enter_context(patch.object(os, 'startfile', side_effect=trap))
            before_path = list(sys.path)
            yield
            self.assertEqual(sys.path, before_path)


class ScriptScope(Base):
    def test_the_allowlists_are_exact_and_keep_the_fourteen_older_paths(self):
        self.assertEqual(merge_center.REPLACE_ALLOWLIST, GUIDES)
        self.assertEqual(len(merge_center.FINISH_ALLOWLIST), 16)
        self.assertEqual(set(merge_center.FINISH_ALLOWLIST), set(GUIDES) | set(ENTRYPOINTS) | set(SCRIPTS))
        self.assertEqual(set(merge_center.FINISH_ALLOWLIST) - set(SCRIPTS), set(GUIDES) | set(ENTRYPOINTS))
        self.assertFalse(set(SCRIPTS) & set(merge_center.REPLACE_ALLOWLIST))  # replace không bao giờ nhận script / replace never takes a script
        for rel in OTHER[:4] + (PACK_SCRIPT,):
            self.assertFalse(merge_center.finish_supported(rel), rel)

    def test_scan_flags_the_two_managed_scripts_only_and_reads_nothing_more(self):
        before = tree_state(self.project)
        rows = {r['path']: r for r in merge_center.scan(str(self.project))}
        self.assertEqual(tree_state(self.project), before)
        flags = {p: r['finish_supported'] for p, r in rows.items()}
        self.assertEqual({p for p, f in flags.items() if f}, set(SCRIPTS) | set(GUIDES[:2]) | set(ENTRYPOINTS[:1]))
        for rel in OTHER + (PACK_SCRIPT,):  # script khác, gói, lõi, .cvf, bản en/ giả: cờ sai / other scripts, pack, core, .cvf and an en/ look-alike: flag False
            self.assertIn(rel, rows)
            self.assertIs(flags[rel], False, rel)
        self.assertEqual(rows[PACK_SCRIPT]['origin'], 'domain_pack')
        self.untouched()

    def test_an_allowed_path_that_the_manifest_does_not_list_is_not_managed_and_is_never_read(self):
        for n, unmanaged in enumerate(((SCRIPTS[0],), (SCRIPTS[1],), SCRIPTS)):  # kể cả đúng trạng thái MANIFEST repo: audit_scripts.py chưa có / including a MANIFEST without audit_scripts.py
            with self.subTest(unmanaged=unmanaged):
                project = build_project(self.root / ('unmanaged%d' % n), str(self.sentinel), unmanaged=unmanaged)
                before = tree_state(self.root)
                trap = AssertionError('a script was read although it is not managed')
                with patch.object(merge_center, '_capture', side_effect=trap), patch.object(merge_center, '_environment', side_effect=trap):
                    for rel in unmanaged:
                        pv = merge_center.preview_finish(str(project), rel + '.new')
                        self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id'], pv['current_sha256']), (False, 'not_managed', None, None))
                        res = merge_center.apply_finish(str(project), rel + '.new', HEX_A, HEX_B, 'finish-' + 'a' * 32)
                        self.assertEqual((res['outcome'], res['reason']), ('blocked', 'not_managed'))
                        seen = merge_center.observe_finish(str(project), rel + '.new', HEX_A, HEX_B, 'finish-' + 'a' * 32)
                        self.assertEqual((seen['state'], seen['reason']), ('refused', 'not_managed'))
                self.assertEqual(tree_state(self.root), before)
                self.assertEqual([r['path'] for r in merge_center.scan(str(project)) if r['path'] in unmanaged], [])  # không dòng scan, không cờ / no scan row, so no flag
        self.untouched()

    def test_managed_scripts_are_eligible_and_every_other_script_stays_outside_the_scope(self):
        for rel in SCRIPTS:
            pv = self.fpv(rel)
            self.assertEqual((pv['path'], pv['pending'], pv['reason'], pv['eligible']), (rel, rel + '.new', self.expected_reason(), os.name == 'nt'))
            self.assertEqual((pv['current_sha256'], pv['candidate_sha256']), (sha(self.raw(rel)), sha(self.raw(rel + '.new'))))
        trap = AssertionError('a file was read for a path outside the finish scope')
        cases = {'unsupported': ['tools/helper.py.new', 'tools/other_tool.py.new', 'skills/local/shared/demo/scripts/run.py.new', PACK_SCRIPT + '.new',
                                 '.cvf/checks/control_check_v3.py.new', 'en/tools/audit_scripts.py.new', 'tools/audit_scripts.pyc.new',
                                 'tools/audit_scripts.py.bak.new', 'tools/audit_scripts.py.new.new', 'tools/sub/audit_scripts.py.new', 'audit_scripts.py.new',
                                 'skills/local/shared/spreadsheet-check/scripts/other.py.new', 'skills/local/shared/spreadsheet-check/SKILL.md.new',
                                 'tools/*.py.new', 'skills/local/shared/*/scripts/*.py.new'],
                 'invalid_path': ['tools/Audit_Scripts.py.new', 'TOOLS/audit_scripts.py.new', 'tools/audit_scripts.PY.new', 'tools\\audit_scripts.py.new',
                                  'skills/local/shared/spreadsheet-check/scripts/CHECK_SPREADSHEET.py.new',
                                  'skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py:stream.new', 'tools/audit_scripts.py.new:$DATA',
                                  'tools/../tools/audit_scripts.py.new', './tools/audit_scripts.py.new', '/tools/audit_scripts.py.new',
                                  'C:/tools/audit_scripts.py.new', 'tools//audit_scripts.py.new', 'tools/audit_scripts.py.new ', 'tools/audit_scripts.py.new.',
                                  'tools/audit_scripts.py', 'tools/audit_scripts.py.NEW', 'tools/audit_scripts.py\n.new', '', None, 5, ['tools/audit_scripts.py.new']]}
        before = tree_state(self.root)
        with patch.object(merge_center, '_capture', side_effect=trap), patch.object(merge_center, 'managed_paths', side_effect=trap), \
                patch.object(merge_center, '_environment', side_effect=trap):
            for reason, paths in cases.items():
                for path in paths:
                    with self.subTest(path=path):
                        pv = merge_center.preview_finish(str(self.project), path)
                        self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id'], pv['current_sha256']), (False, reason, None, None))
                        res = merge_center.apply_finish(str(self.project), path, HEX_A, HEX_B, 'finish-' + 'a' * 32)
                        self.assertEqual((res['outcome'], res['reason']), ('blocked', reason))
                        seen = merge_center.observe_finish(str(self.project), path, HEX_A, HEX_B, 'finish-' + 'a' * 32)
                        self.assertEqual((seen['state'], seen['reason']), ('refused', reason))
        self.assertEqual(tree_state(self.root), before)
        self.untouched()

    def test_replace_stays_unsupported_for_both_scripts_even_with_hashes_from_a_finish_preview(self):
        app_root = patch.object(app, 'ROOT', str(self.project))
        app_root.start()
        self.addCleanup(app_root.stop)
        for rel in SCRIPTS:
            with self.subTest(path=rel):
                before = tree_state(self.root)
                pv = self.fpv(rel)
                rp = merge_center.preview_replace(str(self.project), rel + '.new')
                self.assertEqual((rp['eligible'], rp['reason'], rp['current_sha256']), (False, 'unsupported', None))
                res = merge_center.apply_replace(str(self.project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'])
                self.assertEqual((res['outcome'], res['reason']), ('blocked', 'unsupported'))
                forged = {'path': rel + '.new', 'current_sha256': pv['current_sha256'], 'candidate_sha256': pv['candidate_sha256'],
                          'finish_supported': True, 'scope': 'finish', 'eligible': True, 'allowed': [rel], 'kind': 'replace'}
                env = app.merge_api('/api/merge/replace', forged)
                self.assertEqual((env['status'], env['replace']['reason']), ('blocked', 'unsupported'))
                env = app.merge_api('/api/merge/preview', forged)
                self.assertEqual((env['replace_preview']['eligible'], env['replace_preview']['reason']), (False, 'unsupported'))
                self.assertEqual(tree_state(self.root), before)
        self.untouched()


@WINDOWS
class ScriptFinish(Base):
    def finish_one(self, rel, identical):
        if identical:
            write(self.project, rel + '.new', self.raw(rel))
        cur, cand = self.raw(rel), self.raw(rel + '.new')
        before = tree_state(self.root)
        rows_before = [r['path'] for r in merge_center.scan(str(self.project))]
        with self.no_execution():
            pv = self.fpv(rel)
            self.assertTrue(pv['eligible'], pv)
            self.assertEqual(pv['identical'], identical)
            self.assertEqual(pv['diff'] is None, identical)
            self.assertEqual((pv['current_sha256'], pv['candidate_sha256']), (sha(cur), sha(cand)))  # hash thô, gồm CRLF / raw, CRLF included
            self.assertRegex(pv['finish_id'], FINISH_ID_RE)
            self.assertEqual(tree_state(self.root), before)  # xem trước không ghi / the preview writes nothing
            self.assertFalse((self.project / '.agent' / 'runtime').exists())
            res = self.fin(rel, pv)
            self.assertEqual((res['outcome'], res['reason'], res['snapshot_saved'], res['pending_moved']), ('finished', None, True, True), res)
            seen = self.obs(rel, pv)
        self.assertEqual((seen['state'], seen['reason']), ('finished', None))
        self.assertEqual(self.raw(rel), cur)  # bản hiện hành giữ bytes thô / the current script keeps its raw bytes
        self.assertEqual(self.archive(pv, 'current.txt').read_bytes(), cur)
        self.assertEqual(self.archive(pv, 'incoming.txt').read_bytes(), cand)
        self.assertEqual(self.archive(pv, 'pending-retired.txt').read_bytes(), cand)
        self.assertFalse((self.project / (rel + '.new')).exists())
        record = json.loads(self.archive(pv, 'record.json').read_text(encoding='utf-8'))
        self.assertEqual(set(record), RECORD_KEYS)
        self.assertEqual((record['schema'], record['path'], record['current_sha256'], record['incoming_sha256']),
                         ('local-agent-workspace/merge-finish-v1', rel, sha(cur), sha(cand)))
        base = 'project/.agent/merge-backups/' + pv['finish_id'] + '/'
        after = tree_state(self.root)
        files = {k for k in changed(before, after) if '/.agent/runtime/' not in k}
        self.assertEqual(files, {base + 'current.txt', base + 'incoming.txt', base + 'record.json', base + 'pending-retired.txt', 'project/' + rel + '.new'})
        self.assertEqual({k: v for k, v in after.items() if k not in files and '.agent' not in k.split('/')},
                         {k: v for k, v in before.items() if k not in files and '.agent' not in k.split('/')})  # file ngoài tác động giữ nguyên / everything else is as it was
        self.assertEqual([r['path'] for r in merge_center.scan(str(self.project))], [p for p in rows_before if p != rel])  # chỉ pending đã chọn hết scan / only the chosen pending left the scan
        for text in (json.dumps(res, ensure_ascii=False), json.dumps(seen, ensure_ascii=False), self.archive(pv, 'record.json').read_text(encoding='utf-8'),
                     *[j.read_text(encoding='utf-8') for j in (self.project / '.agent' / 'runtime' / 'transactions').rglob('journal.json')]):
            self.assertNotIn(MARK, text)  # nội dung mã không vào kết quả, record hay nhật ký / no script text in the result, the record or the journal
        rp = merge_center.preview_replace(str(self.project), rel + '.new')
        self.assertEqual((rp['eligible'], rp['reason']), (False, 'unsupported'))
        rr = merge_center.apply_replace(str(self.project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'])
        self.assertEqual((rr['outcome'], rr['reason']), ('blocked', 'unsupported'))
        self.untouched()
        return pv

    def test_each_script_finishes_with_current_kept_for_a_different_and_an_identical_pair(self):
        for rel in SCRIPTS:
            for identical in (False, True):
                with self.subTest(path=rel, identical=identical):
                    self.setUp()
                    # The guard must reject current bytes even with a generic filename;
                    # compile is intercepted before Python can compile the synthetic payload.
                    with self.no_execution(), self.assertRaisesRegex(AssertionError, 'script text was compiled or executed'):
                        compile(self.raw(rel), '<string>', 'exec')
                    self.finish_one(rel, identical)

    def test_invalid_python_text_finishes_like_any_other_text(self):
        for rel in SCRIPTS:
            with self.subTest(path=rel):
                self.kind = 'invalid'
                self.setUp()
                self.assertIn('def broken(:', self.raw(rel + '.new').decode('utf-8'))  # payload cố ý sai cú pháp; không biên dịch để thử / invalid on purpose; never compiled to find out
                self.finish_one(rel, False)
        self.kind = 'poison'

    def test_finishing_one_script_leaves_the_other_pending_and_untouched(self):
        other = SCRIPTS[1]
        keep = {p: self.raw(p) for p in (other, other + '.new', *OTHER, PACK_SCRIPT)}
        self.finish_one(SCRIPTS[0], False)
        self.assertEqual({p: self.raw(p) for p in keep}, keep)
        self.assertIn(other, [r['path'] for r in merge_center.scan(str(self.project))])

    def test_stale_pairs_and_environment_problems_never_write_or_rename(self):
        rel = SCRIPTS[1]
        pv = self.fpv(rel)
        before = tree_state(self.root)
        with patch.object(merge_center.os, 'rename', wraps=os.rename) as spy:
            (self.project / (rel + '.new')).write_bytes(b'# changed later\n')
            res = self.fin(rel, pv)
            self.assertEqual((res['outcome'], res['reason'], res['stale']), ('stale', 'stale_preview', {'current': False, 'candidate': True}))
            (self.project / rel).write_bytes(b'# current changed later\n')
            res = self.fin(rel, pv)
            self.assertEqual((res['outcome'], res['reason'], res['stale']['current']), ('stale', 'stale_preview', True))
        spy.assert_not_called()
        self.assertFalse((self.project / '.agent' / 'merge-backups').exists())
        self.assertFalse((self.project / '.agent' / 'runtime').exists())
        self.assertNotEqual(tree_state(self.root), before)  # chỉ hai file bị cố ý đổi / only the two deliberately edited files differ
        self.assertEqual(set(changed(before, tree_state(self.root))), {'project/' + rel, 'project/' + rel + '.new'})
        self.setUp()
        rel = SCRIPTS[0]
        pv = self.fpv(rel)
        write(self.project, '.agent/runtime/transactions/broken/journal.json', '{')
        with patch.object(merge_center.os, 'rename', wraps=os.rename) as spy:
            res = self.fin(rel, pv)
        spy.assert_not_called()
        self.assertEqual((res['outcome'], res['reason']), ('blocked', 'journal_unreadable'))
        self.assertEqual(self.fpv(rel)['reason'], 'journal_unreadable')
        self.assertTrue((self.project / (rel + '.new')).exists())
        self.assertFalse((self.project / '.agent' / 'merge-backups').exists())

    def test_cleanup_failure_and_rename_failure_after_the_committed_archive_are_not_reported_finished(self):
        rel = SCRIPTS[0]
        cur, cand = self.raw(rel), self.raw(rel + '.new')
        pv = self.fpv(rel)
        with patch.object(tx.Transaction, '_cleanup', side_effect=OSError('cleanup after commit')), patch.object(merge_center.os, 'rename', wraps=os.rename) as spy:
            res = self.fin(rel, pv)
        spy.assert_not_called()
        self.assertEqual((res['outcome'], res['phase'], res['reason'], res['snapshot_saved'], res['pending_moved']),
                         ('still_pending', 'committed', 'archive_committed_after_error', True, False))
        self.assertEqual((self.raw(rel), self.raw(rel + '.new')), (cur, cand))
        self.assertEqual(self.archive(pv, 'incoming.txt').read_bytes(), cand)
        self.assertEqual(self.obs(rel, pv)['state'], 'still_pending')
        self.setUp()
        rel = SCRIPTS[1]
        cur, cand = self.raw(rel), self.raw(rel + '.new')
        pv = self.fpv(rel)
        real = os.rename

        def refuse(src, dst, *args, **kwargs):  # chỉ lần chuyển .new bị từ chối, giao dịch archive vẫn ghi được / only the .new move is refused; the archive transaction still writes
            if str(dst).endswith('pending-retired.txt'):
                raise OSError('rename refused')
            return real(src, dst, *args, **kwargs)
        with patch.object(merge_center.os, 'rename', refuse):
            res = self.fin(rel, pv)
        self.assertEqual((res['outcome'], res['reason'], res['snapshot_saved'], res['pending_moved']), ('still_pending', 'rename_failed', True, False))
        self.assertEqual((self.raw(rel), self.raw(rel + '.new')), (cur, cand))
        self.assertEqual(self.archive(pv, 'current.txt').read_bytes(), cur)
        self.assertEqual(self.obs(rel, pv)['state'], 'still_pending')
        self.untouched()


class ScriptContent(Base):
    def test_binary_oversized_truncated_and_missing_text_block_the_preview(self):
        rel = SCRIPTS[0]
        before_other = {p: self.raw(p) for p in (SCRIPTS[1], SCRIPTS[1] + '.new')}
        pending = self.project / (rel + '.new')

        def blocked(reason):
            pv = self.fpv(rel)
            self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id'], pv['archive']), (False, reason, None, None))
            res = merge_center.apply_finish(str(self.project), rel + '.new', HEX_A, HEX_B, 'finish-' + 'a' * 32)
            self.assertEqual((res['outcome'], res['reason']), ('blocked', reason))
        pending.write_bytes(b'print(1)\x00print(2)\n')
        blocked('binary')
        pending.write_bytes(b'# \xff\xfe not utf-8\n')
        blocked('binary')
        pending.write_bytes(b'x' * (merge_center.DIFF_MAX_BYTES + 1))
        blocked('too_large')
        (self.project / rel).write_bytes(''.join('a%d = 1\n' % i for i in range(5000)).encode('utf-8'))
        pending.write_bytes(''.join('b%d = 2\n' % i for i in range(5000)).encode('utf-8'))
        blocked('truncated')
        pending.unlink()
        blocked('candidate_missing')
        pending.write_bytes(b'# new\n')
        (self.project / rel).unlink()
        blocked('current_missing')
        self.assertFalse((self.project / '.agent' / 'merge-backups').exists())
        self.assertEqual({p: self.raw(p) for p in before_other}, before_other)
        self.untouched()

    def test_a_link_in_the_ancestry_of_the_pair_is_refused_and_the_target_is_not_touched(self):
        rel = SCRIPTS[1]
        outside = self.root / 'outside'
        write(outside, 'check_spreadsheet.py', b'# outside current\n')
        write(outside, 'check_spreadsheet.py.new', incoming_script('poison', rel, str(self.sentinel)))
        folder = self.project / 'skills' / 'local' / 'shared' / 'spreadsheet-check' / 'scripts'
        shutil.rmtree(str(folder))
        if not dir_link(folder, outside):
            self.skipTest('this machine cannot create directory links')
        names = {p.name: p.read_bytes() for p in outside.iterdir()}
        try:
            pv = self.fpv(rel)
            self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id']), (False, 'unsafe_link', None))
            res = merge_center.apply_finish(str(self.project), rel + '.new', HEX_A, HEX_B, 'finish-' + 'a' * 32)
            self.assertEqual((res['outcome'], res['reason']), ('blocked', 'unsafe_link'))
        finally:
            drop_link(folder)
        self.assertEqual({p.name: p.read_bytes() for p in outside.iterdir()}, names)
        self.assertFalse((self.project / '.agent' / 'merge-backups').exists())
        self.untouched()


class ScriptHttp(Base):
    """The adapter with the harness token and the real Host header; a client flag does not make replace supported."""

    def serve(self):
        patcher = patch.object(app, 'ROOT', str(self.project))
        patcher.start()
        self.addCleanup(patcher.stop)
        token = patch.object(app, 'TOKEN', 'test-token')
        token.start()
        self.addCleanup(token.stop)
        opened = []
        launch = patch.object(app, 'launch', lambda path: opened.append(path))
        launch.start()
        self.addCleanup(launch.stop)
        self.opened = opened
        srv = app.Server(('127.0.0.1', 0), app.Handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(lambda: (srv.shutdown(), srv.server_close()))
        return 'http://127.0.0.1:%d' % srv.server_address[1]

    def post(self, base, path, body, token='test-token'):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-Panel-Token'] = token
        data = json.dumps(body).encode('utf-8') if token == 'test-token' else b''  # token sai: thân rỗng vì bị từ chối trước khi đọc thân / a bad token: empty body, refused before it is read
        req = urllib.request.Request(base + path, data=data, method='POST', headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode('utf-8') or '{}')

    def test_routes_check_the_token_and_ignore_client_scope_flags_for_both_scripts(self):
        base = self.serve()
        for rel in SCRIPTS:
            with self.subTest(path=rel):
                before = tree_state(self.root)
                forged = {'finish_supported': False, 'scope': 'replace', 'eligible': False, 'allowed': []}
                self.assertEqual(self.post(base, '/api/merge/finish-preview', {'path': rel + '.new'}, 'wrong')[0], 403)
                self.assertEqual(self.post(base, '/api/merge/finish-preview', {'path': rel + '.new'}, None)[0], 403)
                code, body = self.post(base, '/api/merge/finish-preview', dict(forged, path=rel + '.new'))
                pv = body['finish_preview']
                self.assertEqual((code, body['status'], body['changes'], pv['path'], pv['reason']), (200, 'success', False, rel, self.expected_reason()))
                self.assertEqual(pv['eligible'], os.name == 'nt')
                self.assertEqual(tree_state(self.root), before)
                hashes = {'path': rel + '.new', 'current_sha256': pv['current_sha256'], 'candidate_sha256': pv['candidate_sha256']}
                forged_ok = dict(hashes, finish_supported=True, scope='finish', eligible=True, allowed=[rel], kind='replace')
                code, body = self.post(base, '/api/merge/replace', forged_ok)
                self.assertEqual((code, body['status'], body['replace']['reason']), (200, 'blocked', 'unsupported'))
                code, body = self.post(base, '/api/merge/preview', forged_ok)
                self.assertEqual((body['replace_preview']['eligible'], body['replace_preview']['reason']), (False, 'unsupported'))
                self.assertEqual(tree_state(self.root), before)
        self.assertEqual(self.opened, [])
        self.untouched()

    @WINDOWS
    def test_finish_through_the_adapter_keeps_the_current_script_and_logs_nothing_else(self):
        base = self.serve()
        rel = SCRIPTS[0]
        cur = self.raw(rel)
        pv = self.post(base, '/api/merge/finish-preview', {'path': rel + '.new'})[1]['finish_preview']
        body = {'path': rel + '.new', 'current_sha256': pv['current_sha256'], 'candidate_sha256': pv['candidate_sha256'], 'finish_id': pv['finish_id']}
        code, ok = self.post(base, '/api/merge/finish', dict(body, finish_supported=False))
        self.assertEqual((code, ok['status'], ok['changes'], ok['finish']['outcome']), (200, 'success', True, 'finished'))
        seen = self.post(base, '/api/merge/finish-observe', body)[1]
        self.assertEqual(seen['finish_observation']['state'], 'finished')
        self.assertEqual(self.raw(rel), cur)
        self.assertFalse((self.project / (rel + '.new')).exists())
        self.assertEqual(self.opened, [])
        self.untouched()


# ------------------------------------------------------------------------------------------------ lifecycle: real new_project + upgrade_package
@unittest.skipUnless(os.name == 'nt' and HAVE_JSONSCHEMA,
                     'NOT_CHECKED: needs Windows (the no-replace rename) and jsonschema (the profile and pin checks)')
class ScriptLifecycle(unittest.TestCase):
    """A -> B -> C of a clean projected v3 package (VI only); the source changes only the text of the two scripts, which are never run.
    The VERSION values are fake labels. No migration, no host or native step, no release; NOT proof of the whole P4 or T39."""

    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(setattr, ep, 'LANG', ep.LANG)
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-d01g-lc-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name)
        cls.sentinel = cls.base / 'sentinel'
        cls.sentinel.mkdir()
        cls.A, cls.B, cls.C = (cls.base / n for n in 'ABC')
        cp.materialize(str(cls.A), branding=False)
        shutil.copytree(str(cls.A), str(cls.B))
        shutil.copytree(str(cls.A), str(cls.C))
        for pkg, version, tag, kind in ((cls.A, '92.0.0', None, None), (cls.B, '92.0.1', 'B', 'poison'), (cls.C, '92.0.2', 'C', 'invalid')):
            write(pkg, 'VERSION', version + '\n')
            if tag:
                for rel in SCRIPTS:
                    raw = (pkg / rel).read_bytes()
                    eol = '\r\n' if b'\r\n' in raw else '\n'  # giữ EOL của file nguồn / keep the source file's EOL
                    extra = incoming_script(kind, rel, str(cls.sentinel)).decode('utf-8').replace('\n', eol)
                    write(pkg, rel, raw + (eol + '# bản %s' % tag + eol + extra).encode('utf-8'))
            done = run(pkg, 'check_package.py', '--write-manifest')
            assert done.returncode == 0, done.stdout + done.stderr

    def make_project(self):
        dest = Path(tempfile.mkdtemp(prefix='dest-', dir=str(self.base)))
        r = run(self.A, 'new_project.py', '--name', 'P-vi', '--dest', dest, '--lang', 'vi', '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        proj = dest / 'P-vi'
        ep.LANG = 'vi'
        choices = {'host': 'claude-code', 'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}}}
        plan = ep.plan_config(str(proj), choices)
        self.assertEqual(plan['status'], 'PREVIEW', plan)
        done = ep.apply_config(str(proj), choices, plan['plan']['plan_sha256'])
        self.assertEqual(done['status'], 'WRITTEN', done)
        return proj

    def manifest(self, pkg):
        return {k: v for k, v in (line.split('  ', 1)[::-1] for line in (pkg / 'MANIFEST.sha256').read_text(encoding='utf-8').splitlines() if line.strip())}

    def pendings(self, proj):
        return sorted(p.relative_to(proj).as_posix() for p in proj.rglob('*.new') if '.agent' not in p.parts)

    def test_vi_project_keeps_both_edited_scripts_and_each_candidate_comes_from_the_root_files(self):
        proj = self.make_project()
        for rel in SCRIPTS:  # cả hai path do MANIFEST nguồn quản lý, không nhờ allowlist / both are managed by the source MANIFEST, not by the allowlist
            self.assertIn(rel, self.manifest(self.A))
            self.assertIn(rel, merge_center.managed_paths(str(proj)))
            self.assertEqual((proj / rel).read_bytes(), (self.A / rel).read_bytes())
        edited = {}
        for rel in SCRIPTS:
            edited[rel] = (proj / rel).read_bytes() + ('\r\n# sửa của người dùng\r\nopen(%r, "w").write("user edit ran")\r\n' % os.path.join(str(self.sentinel), 'user')).encode('utf-8')
            (proj / rel).write_bytes(edited[rel])
        keep = ('PROJECT.md', ep.PROFILE_REL, '.agent/STATE.md', *cp.CVF_CLOSURE, *cp.BYTE_EXACT)
        kept0 = {rel: (proj / rel).read_bytes() for rel in keep}
        before = tree_state(proj)
        pv = run(self.B, 'upgrade_package.py', '--project', proj, '--result-json')
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertEqual(tree_state(proj), before)  # xem trước nâng cấp không ghi / the upgrade preview writes nothing
        ap = run(self.B, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        self.assertEqual(self.pendings(proj), sorted(rel + '.new' for rel in SCRIPTS))
        for rel in SCRIPTS:
            self.assertEqual((proj / rel).read_bytes(), edited[rel])
            self.assertEqual((proj / (rel + '.new')).read_bytes(), (self.B / rel).read_bytes())
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, kept0)
        self.assertEqual(cp.pin_problems(str(proj)), [])
        self.assertEqual(self.manifest(proj), self.manifest(self.B))  # manifest đúng nguồn B / the manifest is B's
        manifest_b = (proj / 'MANIFEST.sha256').read_bytes()
        archives = {}
        for rel in SCRIPTS:
            fpv = merge_center.preview_finish(str(proj), rel + '.new')
            self.assertTrue(fpv['eligible'], fpv)
            cand_b = (self.B / rel).read_bytes()
            self.assertEqual((fpv['current_sha256'], fpv['candidate_sha256']), (sha(edited[rel]), sha(cand_b)))
            res = merge_center.apply_finish(str(proj), rel + '.new', fpv['current_sha256'], fpv['candidate_sha256'], fpv['finish_id'])
            self.assertEqual((res['outcome'], res['reason']), ('finished', None), res)
            arc = proj / '.agent' / 'merge-backups' / fpv['finish_id']
            self.assertEqual((proj / rel).read_bytes(), edited[rel])
            self.assertEqual((arc / 'current.txt').read_bytes(), edited[rel])
            self.assertEqual((arc / 'incoming.txt').read_bytes(), cand_b)
            self.assertEqual((arc / 'pending-retired.txt').read_bytes(), cand_b)
            self.assertFalse((proj / (rel + '.new')).exists())
            self.assertEqual([r['path'] for r in merge_center.scan(str(proj)) if r['path'] == rel], [])
            archives[rel] = (fpv, {p.relative_to(proj).as_posix(): p.read_bytes() for p in arc.rglob('*') if p.is_file()})
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, kept0)
        self.assertEqual((proj / 'MANIFEST.sha256').read_bytes(), manifest_b)  # finish không đổi manifest / finish leaves the manifest as it is
        # ---- C: new candidates come from the same engine; the stored pending of B blocks neither of them and the current scripts are not overwritten
        before_c = tree_state(proj)
        pv = run(self.C, 'upgrade_package.py', '--project', proj, '--result-json')
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertEqual(tree_state(proj), before_c)
        ap = run(self.C, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        self.assertEqual(self.pendings(proj), sorted(rel + '.new' for rel in SCRIPTS))
        rows = {r['path']: r for r in merge_center.scan(str(proj)) if r['path'] in SCRIPTS}
        for rel in SCRIPTS:
            cand_c = (self.C / rel).read_bytes()
            self.assertNotEqual(cand_c, (self.B / rel).read_bytes())
            self.assertEqual((proj / (rel + '.new')).read_bytes(), cand_c)
            self.assertEqual((proj / rel).read_bytes(), edited[rel])
            fpv, stored = archives[rel]
            arc = proj / '.agent' / 'merge-backups' / fpv['finish_id']
            self.assertEqual({p.relative_to(proj).as_posix(): p.read_bytes() for p in arc.rglob('*') if p.is_file()}, stored)
            self.assertEqual((rows[rel]['pending'], rows[rel]['finish_supported']), (rel + '.new', True))
            seen = merge_center.observe_finish(str(proj), rel + '.new', fpv['current_sha256'], fpv['candidate_sha256'], fpv['finish_id'])
            self.assertNotEqual(seen['state'], 'finished')  # slot mới có .new khác: record cũ không báo xong cho candidate C / the old record is not "finished" for candidate C
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, kept0)
        self.assertEqual(self.manifest(proj), self.manifest(self.C))
        self.assertEqual(json.loads((proj / '.agent/PACKAGE_INFO.json').read_text(encoding='utf-8'))['version'], '92.0.2')
        # ---- no execution traces observed; this alone is not a process-execution or compilation audit
        self.assertEqual(list(self.sentinel.iterdir()), [])
        self.assertEqual([p for p in self.base.rglob('*.pyc') if p.name.split('.')[0] in ('audit_scripts', 'check_spreadsheet')], [])


if __name__ == '__main__':
    unittest.main()
