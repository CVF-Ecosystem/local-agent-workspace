"""Panel checks: operations history, status data, transaction recovery, diagnostics bundle, merge comparison.

Every test works in temporary folders. The panel's ROOT is patched to a temporary project and its TOOLS to a
temporary copy of the package, so the real repository (and its .agent/runtime) is never written.
"""
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import app
import merge_center
import ops_log
import result_schema
import transaction as tx

FAULT = tx.FAULT_ENV
RUNTIME = '.agent/runtime/'
PKG_IGNORE = shutil.ignore_patterns('.git', '__pycache__', 'dist', 'roadmap', 'tests', 'feedback')
ALLOWED_RECORD_FIELDS = {'time', 'action', 'status', 'code', 'files', 'transaction', 'duration_ms'}


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text, encoding='utf-8')
    return p


def snapshot(root):
    """Mọi file trừ dữ liệu giao dịch / every file except transaction runtime data."""
    out = {}
    root = Path(root)
    for p in root.rglob('*'):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and '__pycache__' not in p.parts and not rel.startswith(RUNTIME):
            out[rel] = p.read_bytes()
    return out


def manifest(root):
    lines = []
    for p in sorted(Path(root).rglob('*')):
        if p.is_file() and p.name != 'MANIFEST.sha256':
            lines.append(hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest() + '  ' + p.relative_to(root).as_posix())
    write(root, 'MANIFEST.sha256', '\n'.join(lines) + '\n')


PKG_TMP = None
PKG = None  # temporary copy of the package; the tools run from here, so the real repository is not touched


def setUpModule():
    global PKG_TMP, PKG
    PKG_TMP = tempfile.TemporaryDirectory(prefix='panel-pkg-')
    PKG = Path(PKG_TMP.name) / 'package'
    shutil.copytree(ROOT, PKG, ignore=PKG_IGNORE)
    shutil.rmtree(str(PKG / '.agent' / 'runtime'), ignore_errors=True)  # dữ liệu vận hành của máy phát triển không vào bản sao / dev-machine runtime data never enters the copy
    [f.unlink() for f in (PKG / 'assets').rglob('*') if f.is_file() and f.name != 'README.md']  # logo, font của máy phát triển / dev-machine branding and fonts


def tearDownModule():
    PKG_TMP.cleanup()


def run_script(script, *args, env=None):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    e.pop(FAULT, None)
    e.update(env or {})
    return subprocess.run([sys.executable, str(PKG / 'tools' / script), *map(str, args)],
                          cwd=str(PKG), env=e, capture_output=True, encoding='utf-8', timeout=300)


class PanelBase(unittest.TestCase):
    """Temp project + patched ROOT and TOOLS (the temp package copy)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='panel-check-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.patch(app, 'ROOT', str(self.project))
        self.patch(app, 'TOOLS', str(PKG / 'tools'))

    def patch(self, obj, name, value):
        p = patch.object(obj, name, value)
        p.start()
        self.addCleanup(p.stop)

    def upgrade_pair(self, name):
        """Gói cũ và mới; năm thao tác khi nâng cấp / old and new packages; five ops on upgrade."""
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

    def interrupt_upgrade(self, old, new, fault='commit:1'):
        """Nâng cấp bị dừng giữa chừng bằng biến kiểm thử / an upgrade interrupted by the test-only fault variable."""
        r = run_script('upgrade_package.py', '--project', old, '--from', new, '--apply', env={FAULT: fault})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        items = tx.incomplete(str(old))
        self.assertEqual(len(items), 1, items)
        return items[0]['id']


class OperationsHistory(PanelBase):
    def test_records_hold_only_allowed_fields_and_no_secrets(self):
        user = getpass.getuser()
        secret_project = 'Dự án BÍ MẬT 4471'
        secret_file = 'SECRET-PERSON Nguyen Van An.docx.new'
        secret_query = 'NGUYEN-VAN-AN-QUERY-7733'
        app.run_api({'action': 'merge_state', 'params': {'path': secret_file, 'state': 'ready'}})
        app.run_api({'action': 'library_find', 'params': {'query': secret_query}})
        app.run_api({'action': 'init', 'params': {'name': secret_project, 'lang': 'vi'}})
        app.run_api({'action': 'check_output', 'params': {'files': [str(self.project / secret_file)]}})
        app.run_api({'action': 'tx_resume', 'params': {'txid': 'bad id!'}})
        text = (self.project / '.agent' / 'runtime' / 'operations.jsonl').read_text(encoding='utf-8')
        self.assertEqual(len(text.splitlines()), 5)
        for line in text.splitlines():
            rec = json.loads(line)
            self.assertEqual(set(rec), ALLOWED_RECORD_FIELDS)
        for forbidden in (secret_project, secret_file, 'SECRET-PERSON', secret_query, 'Nguyen Van An',
                          str(self.project), str(self.project).replace('\\', '/'), os.path.expanduser('~'),
                          app.TOKEN, user):
            if len(forbidden) >= 2:
                self.assertNotIn(forbidden.lower(), text.lower())
        self.assertIn('"status": "blocked"', text)

    def test_unknown_action_name_is_recorded_as_unknown(self):
        app.run_api({'action': 'my_private_action_name', 'params': {}})
        rec = ops_log.read(str(self.project))[-1]
        self.assertEqual(rec['action'], 'unknown')
        self.assertEqual(rec['status'], 'blocked')
        self.assertNotIn('my_private', (self.project / '.agent' / 'runtime' / 'operations.jsonl').read_text(encoding='utf-8'))

    def test_cap_keeps_only_newest_records(self):
        extra = 25
        for i in range(ops_log.MAX_RECORDS + extra):
            ops_log.record(str(self.project), 'check_output', 'success', 0, i)
        records = ops_log.read(str(self.project))
        self.assertEqual(len(records), ops_log.MAX_RECORDS)
        self.assertEqual(records[0]['files'], extra)
        self.assertEqual(records[-1]['files'], ops_log.MAX_RECORDS + extra - 1)

    def test_clear_removes_only_the_history_file(self):
        ops_log.record(str(self.project), 'check_output', 'success', 0)
        keep = {
            '.agent/runtime/transactions/t1/journal.json': '{"schema": "x"}',
            '.agent/STATE.md': 'state text',
            'output/report.txt': 'document text',
        }
        for rel, text in keep.items():
            write(self.project, rel, text)
        before = {rel: (self.project / rel).read_bytes() for rel in keep}
        res = app.action('history_clear', {})
        self.assertEqual(res['result']['status'], 'success')
        self.assertFalse((self.project / '.agent' / 'runtime' / 'operations.jsonl').exists())
        for rel, data in before.items():
            self.assertEqual((self.project / rel).read_bytes(), data)
        self.assertEqual(ops_log.read(str(self.project)), [])

    def test_status_reports_history_and_latest_outcomes(self):
        ops_log.record(str(self.project), 'check_output', 'success', 0)
        ops_log.record(str(self.project), 'upgrade', 'partial', 1, 2, 'tid-1')
        ops_log.record(str(self.project), 'check_package', 'error', -1)
        with patch.object(app, 'pack_info', return_value={'items': []}):
            status = app.status()
        self.assertEqual([h['action'] for h in status['history']], ['check_package', 'upgrade', 'check_output'])
        summary = status['history_summary']
        self.assertEqual(summary['last_success']['action'], 'check_output')
        self.assertEqual(summary['last_failure']['action'], 'check_package')
        self.assertEqual(summary['last_unfinished']['transaction'], 'tid-1')


class StatusData(PanelBase):
    def test_status_keeps_old_fields_and_adds_new_ones(self):
        with patch.object(app, 'pack_info', return_value={'items': []}):
            status = app.status()
        for key in ('version', 'initialized', 'workspace_kind', 'info', 'project_name', 'folder', 'root', 'lang', 'state',
                    'merges', 'skills', 'packs', 'counts', 'is_source', 'release_source', 'template_folder', 'dests',
                    'picker', 'python', 'platform', 'transactions', 'components', 'history', 'history_summary'):
            self.assertIn(key, status)
        self.assertEqual(status['transactions'], [])
        self.assertEqual(status['history'], [])
        self.assertEqual({c['feature'] for c in status['components']}, {'python', 'library', 'xlsx', 'picker'})
        self.assertTrue(all(isinstance(c['usable'], bool) for c in status['components']))

    def test_status_lists_sources_results_and_purpose_newest_first(self):
        write(self.project, 'references/source-documents/a.txt', 'a')
        write(self.project, 'references/README.md', 'scaffold')
        write(self.project, 'output/old.md', 'old')
        write(self.project, 'output/new.md', 'new')
        os.utime(str(self.project / 'output' / 'old.md'), (1700000000, 1700000000))
        write(self.project, 'PROJECT.md', '- Tên dự án: X\n- Mục đích và người đọc: Biên bản cho tổ\n- Đầu ra mong đợi: [Tài liệu]\n')
        with patch.object(app, 'pack_info', return_value={'items': []}):
            status = app.status()
        self.assertEqual([f['path'] for f in status['sources']['items']], ['references/source-documents/a.txt'])
        self.assertEqual([f['name'] for f in status['outputs']['items']], ['new.md', 'old.md'])
        self.assertEqual((status['purpose'], status['expected']), ('Biên bản cho tổ', None))
        self.assertEqual(status['parent'], os.path.dirname(app.ROOT))

    def test_project_open_accepts_only_another_initialised_project(self):
        for bad in ('', str(self.project / 'nope'), str(app.ROOT)):
            with self.assertRaises(app.BadInput):
                app.open_project(bad, 'folder')

    def test_missing_optional_components_are_reported_not_usable(self):
        with patch.object(app, '_has_module', return_value=False), patch.object(app, 'tk_available', return_value=False):
            by_feature = {c['feature']: c for c in app.components()}
        self.assertFalse(by_feature['library']['usable'])
        self.assertFalse(by_feature['xlsx']['usable'])
        self.assertFalse(by_feature['picker']['usable'])
        self.assertEqual(by_feature['library']['needs'], 'openpyxl')

    def test_status_lists_an_interrupted_transaction(self):
        old, new = self.upgrade_pair('status')
        txid = self.interrupt_upgrade(old, new)
        with patch.object(app, 'ROOT', str(old)), patch.object(app, 'pack_info', return_value={'items': []}):
            status = app.status()
        self.assertEqual(len(status['transactions']), 1)
        item = status['transactions'][0]
        self.assertEqual((item['id'], item['operation'], item['status'], item['done']), (txid, 'upgrade', 'committing', 1))

    def test_status_branding_from_assets(self):
        work = Path(tempfile.mkdtemp(prefix='test-brand-'))
        try:
            write(work, 'VERSION', '1.8.0\n')
            write(work, 'PROJECT.md', '- Tên dự án: Demo\n')
            write(work, 'assets/branding.json', json.dumps({'title': 'Đơn vị Mẫu', 'subtitle': 'Agent Workspace', 'logo': 'logo.png'}))
            write(work, 'assets/logo.png', b'\x89PNG\r\n\x1a\nfakeimage')
            with patch.object(app, 'ROOT', str(work)), patch.object(app, 'pack_info', return_value={'items': []}):
                st = app.status()
            self.assertIsNotNone(st['branding'])
            self.assertEqual(st['branding']['title'], 'Đơn vị Mẫu')
            self.assertEqual(st['branding']['subtitle'], 'Agent Workspace')
            self.assertTrue(st['branding']['logo'].startswith('data:image/png;base64,'))
        finally:
            shutil.rmtree(work, ignore_errors=True)


class TransactionRecovery(PanelBase):
    def test_bad_transaction_ids_are_rejected_before_any_tool_runs(self):
        bad = ['../x', 'a/b', 'a.b', '', '   ', 'a b', 'x;rm', 'abc\n', 'a' * 81, '..\\x']
        for txid in bad:
            for act in ('tx_resume', 'tx_rollback'):
                with self.subTest(txid=txid, action=act):
                    with self.assertRaises(app.BadInput):
                        app.action(act, {'txid': txid})
                    res = app.run_api({'action': act, 'params': {'txid': txid}})
                    self.assertEqual(res[0], 200)
                    self.assertEqual(res[1]['result']['status'], 'blocked')
                    self.assertTrue(res[1]['input_error'])

    def test_resume_completes_interrupted_upgrade_like_a_clean_apply(self):
        clean_old, clean_new = self.upgrade_pair('clean')
        r = run_script('upgrade_package.py', '--project', clean_old, '--from', clean_new, '--apply')
        self.assertEqual(r.returncode, 0, r.stderr)
        clean = snapshot(clean_old)
        old, new = self.upgrade_pair('broken')
        txid = self.interrupt_upgrade(old, new)
        with patch.object(app, 'ROOT', str(old)):
            res = app.action('tx_resume', {'txid': txid, 'lang': 'en'})
        self.assertEqual(res['code'], 0, res['out'])
        self.assertEqual(res['result']['code'], res['code'])
        self.assertEqual(res['result']['status'], 'success')
        self.assertEqual(res['result']['transaction'], txid)
        self.assertEqual(snapshot(old), clean)
        self.assertEqual(tx.incomplete(str(old)), [])

    def test_rollback_restores_the_original_files(self):
        old, new = self.upgrade_pair('rb')
        before = snapshot(old)
        txid = self.interrupt_upgrade(old, new, 'commit:3')
        with patch.object(app, 'ROOT', str(old)):
            res = app.action('tx_rollback', {'txid': txid})
        self.assertEqual((res['code'], res['result']['status'], res['result']['code']), (0, 'success', 0))
        self.assertEqual(snapshot(old), before)
        self.assertEqual(tx.incomplete(str(old)), [])

    def test_rollback_keeps_a_user_edit_and_reports_next_steps(self):
        old, new = self.upgrade_pair('edit')
        txid = self.interrupt_upgrade(old, new, 'commit:3')
        write(old, 'untouched.txt', 'USER EDIT')
        with patch.object(app, 'ROOT', str(old)):
            res = app.run_api({'action': 'tx_rollback', 'params': {'txid': txid}})
            payload = res[1]
        self.assertEqual(payload['result']['status'], 'partial')
        self.assertEqual(payload['code'], 1)
        self.assertEqual(payload['result']['code'], payload['code'])
        self.assertEqual(payload['result']['transaction'], txid)
        self.assertTrue(payload['result']['next_actions'])
        self.assertEqual((old / 'untouched.txt').read_text(encoding='utf-8'), 'USER EDIT')
        history = ops_log.read(str(old))
        self.assertEqual((history[-1]['status'], history[-1]['transaction']), ('partial', txid))


class Diagnostics(PanelBase):
    def test_bundle_contains_no_paths_user_name_or_document_text(self):
        old, new = self.upgrade_pair('diag')
        write(old, 'output/secret-report.txt', 'CONFIDENTIAL BODY TEXT 8842 Nguyen Van An')
        write(old, 'references/legal/law.txt', 'LEGAL BODY TEXT 5519')
        write(old, 'skills/local/packs/demo/SKILL.md.new', 'pack body')
        write(old, 'SECRET-PERSON-NAME.new', 'named file')
        txid = self.interrupt_upgrade(old, new)
        with patch.object(app, 'ROOT', str(old)), patch.object(app, 'pack_info', return_value={'items': []}):
            res = app.action('diagnostics', {})
            self.assertEqual(res['result']['status'], 'success')
            rel = res['result']['files'][0]['path']
            self.assertTrue(rel.startswith('.agent/runtime/diagnostics/') and rel.endswith('.zip'), rel)
            archive = old / rel
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(str(archive)) as z:
                self.assertEqual(z.namelist(), ['diagnostics.json'])
                text = z.read('diagnostics.json').decode('utf-8')
        data = json.loads(text)
        self.assertEqual(data['transactions'][0]['id'], txid)
        pendings = [item['pending'] for item in data['merges']['items']]
        self.assertIn('skills/local/packs/demo/SKILL.md.new', pendings)
        self.assertNotIn('SECRET-PERSON-NAME.new', pendings)  # not package-managed: not listed at all
        self.assertEqual(data['merges']['count'], len(merge_center.scan(str(old))))
        for forbidden in ('CONFIDENTIAL BODY TEXT', 'LEGAL BODY TEXT', 'secret-report', 'Nguyen Van An', 'SECRET-PERSON-NAME',
                          'pack body', 'named file'):
            self.assertNotIn(forbidden, text)
        home = os.path.expanduser('~')
        user = getpass.getuser()
        for forbidden in (str(old), str(old).replace('\\', '/'), home, home.replace('\\', '/'), user):
            if len(forbidden) >= 2:
                self.assertNotIn(forbidden.lower(), text.lower())
        self.assertIsNone(re.search(r'[A-Za-z]:[\\/]', text), 'absolute Windows path found')
        self.assertNotIn('/Users/', text)
        self.assertNotIn('/home/', text)

    def test_bundle_is_written_only_under_runtime_diagnostics(self):
        before = snapshot(self.project)
        with patch.object(app, 'pack_info', return_value={'items': []}):
            res = app.action('diagnostics', {})
        self.assertTrue(res['result']['files'][0]['path'].startswith('.agent/runtime/diagnostics/'))
        after = snapshot(self.project)
        self.assertEqual(before, after)


class MergeComparison(PanelBase):
    def setUp(self):
        super().setUp()
        root = self.project
        write(root, 'managed.txt', 'line one\nline two\nline three\nline four\nline five\n')
        write(root, 'managed.txt.new', 'line one\nline 2 changed\nline three\nline four\nline five\nline six\n')
        write(root, 'same.txt', 'identical text\n')
        write(root, 'same.txt.new', 'identical text\n')
        write(root, 'binary.bin', b'\x00\x01\x02')
        write(root, 'binary.bin.new', b'\x00\x05\x06')
        write(root, 'notutf.txt', 'plain text\n')
        write(root, 'notutf.txt.new', b'\xff\xfe\xfd\x00')
        write(root, 'big.txt', 'x' * 500 + '\n')
        write(root, 'big.txt.new', 'y' * 500 + '\n')
        write(root, 'missing.txt.new', 'only new\nsecond line\n')
        write(root, 'user-note.txt.new', 'not managed')
        manifest_lines = ['0' * 64 + '  ' + name for name in ('managed.txt', 'same.txt', 'binary.bin', 'notutf.txt',
                                                              'big.txt', 'missing.txt')]
        write(root, 'MANIFEST.sha256', '\n'.join(manifest_lines) + '\n')

    def test_text_diff_has_hunks_with_line_numbers(self):
        d = merge_center.diff(str(self.project), 'managed.txt.new')
        self.assertFalse(d['identical'] or d['binary'] or d['too_large'] or d['current_missing'])
        self.assertEqual((d['added'], d['removed']), (2, 1))
        self.assertEqual(len(d['hunks']), 1)
        hunk = d['hunks'][0]
        removed = [x for x in hunk['lines'] if x['op'] == 'removed']
        added = [x for x in hunk['lines'] if x['op'] == 'added']
        self.assertEqual([(x['old'], x['text']) for x in removed], [(2, 'line two')])
        self.assertEqual([(x['new'], x['text']) for x in added], [(2, 'line 2 changed'), (6, 'line six')])
        self.assertTrue(any(x['op'] == 'context' and x['text'] == 'line one' for x in hunk['lines']))

    def test_flags_identical_binary_undecodable_too_large_and_missing(self):
        root = str(self.project)
        self.assertTrue(merge_center.diff(root, 'same.txt.new')['identical'])
        self.assertEqual(merge_center.diff(root, 'same.txt.new')['hunks'], [])
        self.assertTrue(merge_center.diff(root, 'binary.bin.new')['binary'])
        self.assertTrue(merge_center.diff(root, 'notutf.txt.new')['binary'])
        self.assertTrue(merge_center.diff(root, 'big.txt.new', max_bytes=100)['too_large'])
        self.assertEqual(merge_center.diff(root, 'big.txt.new', max_bytes=100)['hunks'], [])
        missing = merge_center.diff(root, 'missing.txt.new')
        self.assertTrue(missing['current_missing'])
        self.assertEqual(missing['added'], 2)
        self.assertEqual(missing['removed'], 0)

    def test_unmanaged_paths_and_traversal_are_refused(self):
        root = str(self.project)
        for rel in ('user-note.txt.new', '../outside.txt.new', 'a/../../outside.txt.new', 'C:/managed.txt.new',
                    'managed.txt', '', 'missing-entirely.txt.new'):
            with self.subTest(rel=rel):
                with self.assertRaises(ValueError):
                    merge_center.diff(root, rel)
                with self.assertRaises(app.BadInput):
                    app.action('merge_diff', {'path': rel})

    def test_diff_is_read_only_and_stores_nothing(self):
        before = snapshot(self.project)
        merge_center.diff(str(self.project), 'managed.txt.new')
        res = app.action('merge_diff', {'path': 'managed.txt.new'})
        self.assertEqual(res['code'], 0)
        self.assertEqual(res['result']['diff']['path'], 'managed.txt')
        self.assertEqual(snapshot(self.project), before)
        self.assertFalse((self.project / '.agent' / 'MERGE_STATUS.json').exists())

    def test_set_state_still_refuses_unmanaged_files(self):
        with self.assertRaises(ValueError):
            merge_center.set_state(str(self.project), 'user-note.txt.new', 'ready')
        self.assertEqual(merge_center.set_state(str(self.project), 'managed.txt.new', 'reviewing')['state'], 'reviewing')


class EnvelopeCodes(PanelBase):
    """Each structured tool, called through app.action, returns an envelope whose code is the exit code.
    Runs against a temporary copy of the package, so the tools write only inside it."""

    def test_structured_tools_return_matching_envelopes(self):
        work = self.root / 'work'
        work.mkdir()
        sample = write(work, 'sample.txt', 'A complete text with enough content for the check.')
        write(work, 'adopt-target/AGENTS.md', 'own instructions')
        old, new = self.upgrade_pair('env')
        self.patch(app, 'ROOT', str(PKG))
        calls = [
            ('library_init', {}),
            ('library_stats', {}),
            ('library_check', {}),
            ('library_find', {'query': 'luat'}),
            ('pack_list', {}),
            ('check_package', {}),
            ('check_package', {'verify': True}),
            ('check_output', {'files': [str(sample)]}),
            ('install_skills', {'target': 'custom', 'dest': str(work / 'skills-out')}),
            ('init', {'name': 'Demo', 'lang': 'en', 'apply': False}),
            ('adopt', {'project': str(work / 'adopt-target'), 'name': 'Demo'}),
            ('upgrade_other', {'project': str(old)}),
            ('tx_resume', {'txid': '20000101-000000-deadbeef'}),
        ]
        for action_name, params in calls:
            with self.subTest(action=action_name, params=params):
                res = app.action(action_name, params)
                env = res['result']
                self.assertEqual(env['schema'], result_schema.SCHEMA)
                self.assertEqual(env['code'], res['code'])
                self.assertFalse(any(u.get('reason') == 'invalid_result_schema' for u in env['unchecked']))
        stats = app.action('library_stats', {})
        self.assertEqual(stats['result']['status'], 'success', stats['out'])
        self.assertEqual(json.loads(stats['out'])['index'], True)
        found = app.action('library_find', {'query': 'luat'})
        self.assertEqual(json.loads(found['out'])['query'], 'luat')
        self.assertEqual(app.action('check_output', {'files': [str(sample)]})['result']['status'], 'success')


if __name__ == '__main__':
    unittest.main()
