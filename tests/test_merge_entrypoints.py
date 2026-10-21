"""D-01e checks: finish (never replace) for the six instruction entrypoints (D01E_FINISH_ONLY).

Everything runs on fake data in temporary folders. FINISH_ALLOWLIST is the eight guides plus AGENTS.md, CLAUDE.md, GEMINI.md and their en/ counterparts
(D-01g adds two package scripts, covered by tests/test_merge_scripts.py); REPLACE_ALLOWLIST stays the eight guides. The current file keeps its raw bytes at every step; a finished pair only has its .new stored and moved.
The scan flag finish_supported is a scope flag, not eligibility or a grant: the server checks its own allowlist on every call.
The node cases run the real D01B + D01C script blocks and the real drawMerges of tools/app_ui.html against a fake api and a minimal DOM:
they prove the async flow and the entry wiring, not the visual look. The lifecycle cases use the real shipped bytes (check_package.materialize,
no branding; NOT a release) and the real new_project.py and upgrade_package.py CLIs; instruction content is data, never a command.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import app  # noqa: E402
import check_package as cp  # noqa: E402
import execution_profile as ep  # noqa: E402
import merge_center  # noqa: E402
import result_schema  # noqa: E402

UI_FILE = ROOT / 'tools' / 'app_ui.html'
WINDOWS = unittest.skipUnless(os.name == 'nt', 'the no-replace rename is only measured on Windows')
HAVE_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
GUIDES = ('docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md', 'docs/HUONG_DAN_SU_DUNG_VI.md', 'docs/HUONG_DAN_SKILLS_VI.md',
          'docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md', 'docs/en/NEW_PROJECT_GUIDE.md', 'docs/en/DAILY_USE_GUIDE.md',
          'docs/en/SKILLS_GUIDE.md', 'docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md')
ENTRYPOINTS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'en/AGENTS.md', 'en/CLAUDE.md', 'en/GEMINI.md')
SCRIPTS = ('tools/audit_scripts.py', 'skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py')  # D-01g, written here independently of the owner code
OTHER = ('PROJECT.md', '.agent/STATE.md', '.agent/EXECUTION_PROFILE.json', '.cvf/rules/CONTROL_RULES.md', 'tools/helper.py',
         'roles/scout/agent.md', 'skills/local/shared/demo/SKILL.md', 'README.md', 'docs/other-notes.md')
SECRET = 'INSTRUCTION-TEXT-MARKER-7731'
FINISH_ID_RE = re.compile(r'finish-[0-9a-f]{32}')
HEX_A, HEX_B = 'a' * 64, 'b' * 64
RECORD_KEYS = {'schema', 'record_version', 'finish_id', 'path', 'current_sha256', 'incoming_sha256', 'archive_txid'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(root, rel, data):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data if isinstance(data, bytes) else data.encode('utf-8'))
    return p


def current_bytes(rel):
    return ('# Hướng dẫn cho agent %s\r\nluật A cũ\r\nluật B\r\n' % rel).encode('utf-8')  # CRLF: EOL của người dùng / the user's EOL


def pending_bytes(rel):
    return ('# Hướng dẫn cho agent %s\nluật A mới %s\nluật B\nluật C thêm\n' % (rel, SECRET)).encode('utf-8')  # LF


def build_project(root, unmanaged=()):
    """Dự án giả: mười bốn path finish và các file quản lý khác đều có .new khác bytes/EOL; MANIFEST giả; dấu mốc của người dùng.
    Fake project: the fourteen guide and entrypoint paths (no script) and other managed files all carry a different .new; a fake MANIFEST; user markers."""
    root = Path(root)
    for rel in GUIDES + ENTRYPOINTS:
        write(root, rel, current_bytes(rel))
        write(root, rel + '.new', pending_bytes(rel))
    for rel in OTHER:
        write(root, rel, 'current ' + rel + '\n')
        write(root, rel + '.new', 'new ' + rel + '\n')
    write(root, 'output/report.txt', 'USER OUTPUT MARKER\n')
    write(root, 'working/notes.txt', 'WORKING MARKER\n')
    names = [n for n in GUIDES + ENTRYPOINTS + OTHER if n not in unmanaged]
    write(root, 'MANIFEST.sha256', '\n'.join('0' * 64 + '  ' + n for n in names) + '\n')
    return root


def tree_state(root):
    """Mọi file và thư mục, băm bytes thô, kể cả runtime / every file and folder by raw hash, runtime included."""
    out = {}
    root = Path(root)
    for p in sorted(root.rglob('*')):
        if '__pycache__' not in p.parts:
            out[p.relative_to(root).as_posix()] = sha(p.read_bytes()) if p.is_file() else 'dir'
    return out


def changed(before, after):
    return {k for k in set(before) | set(after) if before.get(k) != after.get(k) and 'dir' not in (before.get(k), after.get(k))}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='law-d01e-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = build_project(self.root / 'project')

    def raw(self, rel):
        return (self.project / rel).read_bytes()

    def fpv(self, rel, root=None):
        return merge_center.preview_finish(str(root or self.project), rel + '.new')

    def fin(self, rel, pv=None):
        pv = pv or self.fpv(rel)
        return merge_center.apply_finish(str(self.project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])

    def archive(self, pv, name):
        return self.project / '.agent' / 'merge-backups' / pv['finish_id'] / name

    def expected_reason(self):
        return None if os.name == 'nt' else 'os_unsupported'

    def _patched_root(self):
        if not getattr(self, '_root_patch', None):
            self._root_patch = patch.object(app, 'ROOT', str(self.project))
            self._root_patch.start()
            self.addCleanup(self._root_patch.stop)


class EntrypointScope(Base):
    def test_the_two_allowlists_are_split_and_exact(self):
        self.assertEqual(merge_center.REPLACE_ALLOWLIST, GUIDES)
        self.assertEqual(len(merge_center.FINISH_ALLOWLIST), 16)
        self.assertEqual(set(merge_center.FINISH_ALLOWLIST), set(GUIDES) | set(ENTRYPOINTS) | set(SCRIPTS))
        self.assertEqual(set(merge_center.FINISH_ALLOWLIST) - set(SCRIPTS), set(GUIDES) | set(ENTRYPOINTS))  # mười bốn path D-01e giữ nguyên / the fourteen D-01e paths are kept
        self.assertFalse((set(ENTRYPOINTS) | set(SCRIPTS)) & set(merge_center.REPLACE_ALLOWLIST))

    def test_scan_flags_the_guide_and_entrypoint_paths_of_this_fixture_and_reads_nothing_more(self):
        before = tree_state(self.project)
        # fixture này không có script: hai path D-01g do tests/test_merge_scripts.py kiểm / this fixture seeds no script: the two D-01g paths are checked in tests/test_merge_scripts.py
        write(self.project, 'unlisted.md', 'x\n')  # có .new nhưng không trong MANIFEST: không vào scan / has a .new but is not in the MANIFEST: not scanned
        write(self.project, 'unlisted.md.new', 'y\n')
        before = tree_state(self.project)
        rows = merge_center.scan(str(self.project))
        self.assertEqual(tree_state(self.project), before)
        flags = {r['path']: r['finish_supported'] for r in rows}
        self.assertEqual(set(flags), set(GUIDES) | set(ENTRYPOINTS) | set(OTHER))  # managed_paths không mở rộng / managed_paths did not grow
        self.assertEqual({p for p, f in flags.items() if f}, set(GUIDES) | set(ENTRYPOINTS))
        self.assertTrue(all(f is False for p, f in flags.items() if p in OTHER))
        for rel in ('agents.md', 'en\\AGENTS.md', 'AGENTS.md.new', '', None, 5):  # hàm cờ cũng chỉ so khớp chính xác / the flag helper is an exact match too
            self.assertFalse(merge_center.finish_supported(rel), rel)

    def test_the_scan_flag_is_scope_only_not_eligibility(self):
        write(self.project, 'AGENTS.md.new', b'bin\x00ary')
        row = [r for r in merge_center.scan(str(self.project)) if r['path'] == 'AGENTS.md'][0]
        self.assertTrue(row['finish_supported'])
        pv = self.fpv('AGENTS.md')
        self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id']), (False, 'binary', None))

    def test_finish_preview_describes_each_pair_and_writes_nothing(self):
        for rel in ENTRYPOINTS:
            with self.subTest(path=rel):
                before = tree_state(self.project)
                pv = self.fpv(rel)
                self.assertEqual((pv['schema'], pv['path'], pv['pending'], pv['reason'], pv['identical']),
                                 (merge_center.FINISH_PREVIEW_SCHEMA, rel, rel + '.new', self.expected_reason(), False))
                self.assertEqual(pv['eligible'], os.name == 'nt')
                self.assertEqual((pv['current_sha256'], pv['candidate_sha256']), (sha(self.raw(rel)), sha(self.raw(rel + '.new'))))  # hash thô, gồm CRLF / raw, CRLF included
                self.assertEqual((pv['diff']['added'], pv['diff']['removed']), (2, 1))
                self.assertTrue(pv['current_stays'] and pv['pending_moves'] and not pv['manifest_updated'] and not pv['html_rebuilt'])
                if pv['eligible']:
                    self.assertRegex(pv['finish_id'], FINISH_ID_RE)
                self.assertEqual(tree_state(self.project), before)
                self.assertFalse((self.project / '.agent' / 'runtime').exists())

    def test_replace_stays_unsupported_for_the_six_even_with_hashes_from_a_finish_preview(self):
        for rel in ENTRYPOINTS:
            with self.subTest(path=rel):
                before = tree_state(self.project)
                pv = self.fpv(rel)
                self.assertTrue(pv['current_sha256'] and pv['candidate_sha256'])  # hash thật, kể cả khi finish bị chặn vì OS / real hashes even where finish is blocked by the OS
                rp = merge_center.preview_replace(str(self.project), rel + '.new')
                self.assertEqual((rp['eligible'], rp['reason'], rp['current_sha256']), (False, 'unsupported', None))
                res = merge_center.apply_replace(str(self.project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'])
                self.assertEqual((res['outcome'], res['reason']), ('blocked', 'unsupported'))
                forged = {'path': rel + '.new', 'current_sha256': pv['current_sha256'], 'candidate_sha256': pv['candidate_sha256'],
                          'finish_supported': True, 'scope': 'finish', 'eligible': True, 'allowed': [rel], 'kind': 'replace'}
                self._patched_root()
                env = app.merge_api('/api/merge/replace', forged)
                self.assertEqual((env['status'], env['replace']['reason']), ('blocked', 'unsupported'))
                env = app.merge_api('/api/merge/preview', forged)
                self.assertEqual((env['replace_preview']['eligible'], env['replace_preview']['reason']), (False, 'unsupported'))
                self.assertEqual(self.raw(rel), current_bytes(rel))
                self.assertEqual(tree_state(self.project), before)

    def test_the_server_ignores_client_scope_fields_on_every_finish_route(self):
        self._patched_root()
        before = tree_state(self.project)
        forged = {'finish_supported': True, 'scope': 'finish', 'eligible': True, 'allowed': ['PROJECT.md'], 'allowed_paths': ['PROJECT.md']}
        for rel in ('PROJECT.md', '.agent/EXECUTION_PROFILE.json', 'tools/helper.py', 'roles/scout/agent.md'):
            body = dict(forged, path=rel + '.new', current_sha256=HEX_A, candidate_sha256=HEX_B, finish_id='finish-' + 'a' * 32)
            pv = app.merge_api('/api/merge/finish-preview', body)
            self.assertEqual((pv['status'], pv['finish_preview']['eligible'], pv['finish_preview']['reason']), ('success', False, 'unsupported'), rel)
            fin = app.merge_api('/api/merge/finish', body)
            self.assertEqual((fin['status'], fin['finish']['reason']), ('blocked', 'unsupported'), rel)
            obs = app.merge_api('/api/merge/finish-observe', body)
            self.assertEqual((obs['status'], obs['finish_observation']['state'], obs['finish_observation']['reason']), ('blocked', 'refused', 'unsupported'), rel)
        self.assertEqual(tree_state(self.project), before)

    def test_alias_ads_traversal_and_other_files_are_refused_before_any_read(self):
        cases = {
            'invalid_path': ['agents.md.new', 'AGENTS.MD.new', 'Agents.md.new', 'en/agents.md.new', 'EN/AGENTS.md.new', 'En/Claude.md.new',
                             'AGENTS.md:stream.new', 'AGENTS.md.new:$DATA', '../AGENTS.md.new', 'en/../AGENTS.md.new', './AGENTS.md.new', '/AGENTS.md.new',
                             'C:/AGENTS.md.new', '//server/share/AGENTS.md.new', 'en\\AGENTS.md.new', 'en//AGENTS.md.new', 'AGENTS.md.new ', 'AGENTS.md.new.',
                             'AGENTS.md', 'AGENTS.md.NEW', 'GEMINI.md\n.new', '', None, 5, ['AGENTS.md.new'], {'a': 1}],
            'unsupported': ['PROJECT.md.new', '.agent/EXECUTION_PROFILE.json.new', '.agent/STATE.md.new', '.cvf/rules/CONTROL_RULES.md.new', 'tools/helper.py.new',
                            'roles/scout/agent.md.new', 'skills/local/shared/demo/SKILL.md.new', 'README.md.new', 'MANIFEST.sha256.new', 'VERSION.new',
                            'docs/other-notes.md.new', 'en/en/AGENTS.md.new', 'AGENTS.md.new.new', 'en/AGENTS.md/x.new', ' AGENTS.md.new',
                            'docs/AGENTS.md.new', 'en/PROJECT.md.new'],
        }
        before = tree_state(self.project)
        trap = AssertionError('a file or index was read for a path outside the finish scope')
        with patch.object(merge_center, '_capture', side_effect=trap), patch.object(merge_center, '_probe', side_effect=trap), \
                patch.object(merge_center, 'managed_paths', side_effect=trap), patch.object(merge_center, '_environment', side_effect=trap):
            for reason, paths in cases.items():
                for path in paths:
                    with self.subTest(path=path):
                        pv = merge_center.preview_finish(str(self.project), path)
                        self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id'], pv['current_sha256']), (False, reason, None, None))
                        res = merge_center.apply_finish(str(self.project), path, HEX_A, HEX_B, 'finish-' + 'a' * 32)
                        self.assertEqual((res['outcome'], res['reason']), ('blocked', reason))
                        seen = merge_center.observe_finish(str(self.project), path, HEX_A, HEX_B, 'finish-' + 'a' * 32)
                        self.assertEqual((seen['state'], seen['reason']), ('refused', reason))
        self.assertEqual(tree_state(self.project), before)

    def test_a_path_missing_from_the_manifest_is_not_managed(self):
        project = build_project(self.root / 'partial', unmanaged=('GEMINI.md', 'en/CLAUDE.md'))
        before = tree_state(project)
        for rel in ('GEMINI.md', 'en/CLAUDE.md'):
            pv = self.fpv(rel, project)
            self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id']), (False, 'not_managed', None))
            res = merge_center.apply_finish(str(project), rel + '.new', HEX_A, HEX_B, 'finish-' + 'a' * 32)
            self.assertEqual((res['outcome'], res['reason']), ('blocked', 'not_managed'))
            self.assertEqual(merge_center.observe_finish(str(project), rel + '.new', HEX_A, HEX_B, 'finish-' + 'a' * 32)['reason'], 'not_managed')
        self.assertEqual([r['path'] for r in merge_center.scan(str(project)) if r['path'] in ('GEMINI.md', 'en/CLAUDE.md')], [])
        self.assertEqual(tree_state(project), before)

    def test_content_environment_and_link_problems_block_the_entrypoint_pair(self):
        pending = self.project / 'CLAUDE.md.new'
        pending.write_bytes(b'x' * (merge_center.DIFF_MAX_BYTES + 1))
        self.assertEqual(self.fpv('CLAUDE.md')['reason'], 'too_large')
        pending.write_bytes(pending_bytes('CLAUDE.md'))
        write(self.project, '.agent/runtime/transactions/broken/journal.json', '{')
        pv = self.fpv('CLAUDE.md')
        self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id']), (False, 'journal_unreadable', None))
        self.assertEqual(merge_center.apply_finish(str(self.project), 'CLAUDE.md.new', sha(self.raw('CLAUDE.md')), sha(self.raw('CLAUDE.md.new')),
                                                   'finish-' + 'b' * 32)['reason'], 'journal_unreadable')
        shutil.rmtree(str(self.project / '.agent' / 'runtime'))
        outside = self.root / 'outside'
        write(outside, 'CLAUDE.md', 'o\n')
        write(outside, 'CLAUDE.md.new', 'n\n')
        shutil.rmtree(str(self.project / 'en'))
        link = self.project / 'en'
        made = False
        try:
            os.symlink(str(outside), str(link), target_is_directory=True)
            made = True
        except (OSError, NotImplementedError):
            if os.name == 'nt':
                made = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(outside)], capture_output=True).returncode == 0
        if not made:
            self.skipTest('this machine cannot create directory links')
        try:
            pv = self.fpv('en/CLAUDE.md')
            self.assertEqual((pv['eligible'], pv['reason'], pv['finish_id']), (False, 'unsafe_link', None))
        finally:
            try:
                os.rmdir(str(link))
            except OSError:
                os.unlink(str(link))
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ['CLAUDE.md', 'CLAUDE.md.new'])


@WINDOWS
class EntrypointFinish(Base):
    def test_each_entrypoint_finishes_with_current_kept_for_a_different_and_an_identical_pair(self):
        for n, rel in enumerate(ENTRYPOINTS):
            for identical in (False, True):
                with self.subTest(path=rel, identical=identical):
                    project = build_project(self.root / ('p%d%d' % (n, identical)))
                    self.project = project
                    if identical:
                        write(project, rel + '.new', project.joinpath(rel).read_bytes())
                    cur, cand = self.raw(rel), self.raw(rel + '.new')
                    others = {k: v for k, v in tree_state(project).items() if k not in (rel + '.new',)}
                    pv = self.fpv(rel)
                    self.assertTrue(pv['eligible'], pv)
                    self.assertEqual(pv['identical'], identical)
                    self.assertEqual(pv['diff'] is None, identical)
                    res = self.fin(rel, pv)
                    self.assertEqual((res['outcome'], res['reason'], res['snapshot_saved'], res['pending_moved']), ('finished', None, True, True), res)
                    self.assertEqual(self.raw(rel), cur)  # bytes thô, gồm CRLF / raw bytes, CRLF included
                    self.assertEqual(self.archive(pv, 'current.txt').read_bytes(), cur)
                    self.assertEqual(self.archive(pv, 'incoming.txt').read_bytes(), cand)
                    self.assertEqual(self.archive(pv, 'pending-retired.txt').read_bytes(), cand)
                    self.assertFalse((project / (rel + '.new')).exists())
                    record = json.loads(self.archive(pv, 'record.json').read_text(encoding='utf-8'))
                    self.assertEqual(set(record), RECORD_KEYS)
                    self.assertEqual((record['schema'], record['path'], record['current_sha256'], record['incoming_sha256']),
                                     ('local-agent-workspace/merge-finish-v1', rel, sha(cur), sha(cand)))
                    after = tree_state(project)
                    new_files = {k for k in changed(others, after) if not k.startswith('.agent/runtime/')}
                    base = '.agent/merge-backups/' + pv['finish_id'] + '/'
                    self.assertEqual(new_files, {base + 'current.txt', base + 'incoming.txt', base + 'record.json', base + 'pending-retired.txt'})
                    self.assertEqual(after['MANIFEST.sha256'], others['MANIFEST.sha256'])  # MANIFEST không đổi / MANIFEST unchanged
                    self.assertNotIn(rel, [r['path'] for r in merge_center.scan(str(project))])
                    self.assertEqual(len(merge_center.scan(str(project))), len(GUIDES) + len(ENTRYPOINTS) + len(OTHER) - 1)
                    seen = merge_center.observe_finish(str(project), rel + '.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])
                    self.assertEqual((seen['state'], seen['reason']), ('finished', None))
                    self.assertEqual(self.raw(rel), cur)

    def test_no_instruction_text_enters_the_result_the_record_or_the_journal(self):
        pv = self.fpv('AGENTS.md')
        self.assertIn(SECRET, json.dumps(pv, ensure_ascii=False))  # diff là phản hồi có chủ đích khi xem trước / the diff is the intended preview response
        res = self.fin('AGENTS.md', pv)
        self.assertEqual(res['outcome'], 'finished')
        self.assertNotIn(SECRET, json.dumps(res, ensure_ascii=False))
        self.assertNotIn(SECRET, self.archive(pv, 'record.json').read_text(encoding='utf-8'))
        for journal in (self.project / '.agent' / 'runtime' / 'transactions').rglob('journal.json'):
            self.assertNotIn(SECRET, journal.read_text(encoding='utf-8'))
        seen = merge_center.observe_finish(str(self.project), 'AGENTS.md.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])
        self.assertNotIn(SECRET, json.dumps(seen, ensure_ascii=False))

    def test_route_flow_for_an_entrypoint_ignores_client_scope_and_never_opens_a_file(self):
        self._patched_root()
        opened = []
        with patch.object(app, 'launch', lambda path: opened.append(path)):
            pv = app.merge_api('/api/merge/finish-preview', {'path': 'en/GEMINI.md.new', 'finish_supported': False, 'allowed': []})['finish_preview']
            self.assertEqual((pv['eligible'], pv['path']), (True, 'en/GEMINI.md'))
            body = {'path': 'en/GEMINI.md.new', 'current_sha256': pv['current_sha256'], 'candidate_sha256': pv['candidate_sha256'], 'finish_id': pv['finish_id']}
            env = app.merge_api('/api/merge/finish', dict(body, finish_supported=False, scope='replace'))
            self.assertEqual((env['status'], env['changes'], env['finish']['outcome']), ('success', True, 'finished'))
            seen = app.merge_api('/api/merge/finish-observe', body)
        self.assertEqual(seen['finish_observation']['state'], 'finished')
        self.assertEqual(opened, [])
        self.assertEqual(self.raw('en/GEMINI.md'), current_bytes('en/GEMINI.md'))

    def test_an_entrypoint_with_a_broken_journal_or_an_unfinished_transaction_never_renames(self):
        pv = self.fpv('AGENTS.md')
        write(self.project, '.agent/runtime/transactions/broken/journal.json', '{')
        with patch.object(merge_center.os, 'rename', wraps=os.rename) as spy:
            res = merge_center.apply_finish(str(self.project), 'AGENTS.md.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])
        spy.assert_not_called()
        self.assertEqual((res['outcome'], res['reason']), ('blocked', 'journal_unreadable'))
        self.assertTrue((self.project / 'AGENTS.md.new').exists())
        self.assertFalse((self.project / '.agent' / 'merge-backups').exists())

    def test_a_candidate_changed_before_the_rename_keeps_the_moved_bytes_and_is_not_reported_finished(self):
        pv = self.fpv('GEMINI.md')

        def edit():
            (self.project / 'GEMINI.md.new').write_bytes(b'changed by someone else\n')
        done = []

        def hook(point):
            if point == 'finish_before_rename' and not done:
                done.append(1)
                edit()
        with patch.object(merge_center, '_HOOK', hook):
            res = merge_center.apply_finish(str(self.project), 'GEMINI.md.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])
        self.assertNotEqual(res['outcome'], 'finished', res)
        self.assertEqual(self.raw('GEMINI.md'), current_bytes('GEMINI.md'))

    def test_a_guide_still_finishes_and_its_old_record_is_still_observed(self):
        pv = self.fpv(GUIDES[2])
        res = self.fin(GUIDES[2], pv)
        self.assertEqual(res['outcome'], 'finished')
        seen = merge_center.observe_finish(str(self.project), GUIDES[2] + '.new', pv['current_sha256'], pv['candidate_sha256'], pv['finish_id'])
        self.assertEqual(seen['state'], 'finished')
        self.assertEqual(self.raw(GUIDES[2]), current_bytes(GUIDES[2]))


# ------------------------------------------------------------------------------------------------ UI: node harness over the real script blocks
def block(begin, end):
    text = UI_FILE.read_text(encoding='utf-8')
    return text[text.index(begin):text.index(end)]


def draw_merges_source():
    text = UI_FILE.read_text(encoding='utf-8')
    return text[text.index('function drawMerges(){'):text.index('// merge comparison')]


HARNESS = r"""
'use strict';
const calls = [], copied = [], diffs = [], boxes = {}, RESP = {}, els = {}, sheets = [], opened = []; let closed = 0, refreshed = 0, toasts = 0;
function adopt(html) { const m = /id="([^"]+)"/.exec(html); if (m) boxes['#' + m[1]] = {innerHTML: '', insertAdjacentHTML: function (pos, h) { adopt(h); }}; }
const sheet = {listeners: [], hidden: true, attrs: {}, setAttribute: function (k, v) { sheet.attrs[k] = v; }, querySelector: function (sel) { return boxes[sel] || null; },
               insertAdjacentHTML: function (pos, h) { adopt(h); }, addEventListener: function (type, fn) { sheet.listeners.push(fn); }};
const mg = {innerHTML: '', handlers: [], querySelectorAll: function (sel) {
  const m = /^\[data-([a-z]+)\]$/.exec(sel), re = new RegExp('data-' + m[1] + '="([^"]*)"', 'g'), list = []; let x;
  while ((x = re.exec(mg.innerHTML))) { const key = m[1], val = x[1]; list.push({dataset: {[key]: val}, addEventListener: function (ev, fn) { mg.handlers.push([key, val, fn]); }}); }
  return {forEach: function (f) { list.forEach(f); }}; }};
function $(id) { return id === 'sh-diff' ? sheet : id === 'mg-rows' ? mg : (els[id] || (els[id] = {innerHTML: '', textContent: '', hidden: false, addEventListener: function () {}})); }
function t(k) { return (k === 'mf_partial' || k === 'mf_unproven') ? k + ':%s' : k; }
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]; }); }
function ico() { return ''; }
function drawDiff(d) { diffs.push(d); Object.keys(boxes).forEach(function (k) { delete boxes[k]; }); }  // innerHTML = ... wipes the boxes
function openDiff(pending, rel) { opened.push(['diff', pending, rel]); }
function openSheet(title) { sheets.push(title); Object.keys(boxes).forEach(function (k) { delete boxes[k]; }); }
function copyText(x) { copied.push(x); }
function toast(m) { toasts++; }
function closeSheet() { closed++; mpReset(); }
function refresh() { refreshed++; return Promise.resolve(); }
function api(p, b) { calls.push([p, JSON.parse(JSON.stringify(b))]); const r = RESP[p]; return Promise.resolve(typeof r === 'function' ? r(b) : r); }
%BLOCKB%
%BLOCKC%
%DRAW%
const S = {merges: []};
const PVS = 'local-agent-workspace/merge-replace-preview-v1', FPS = 'local-agent-workspace/merge-finish-preview-v1', FOS = 'local-agent-workspace/merge-finish-observe-v1';
const A = 'a'.repeat(64), B = 'b'.repeat(64), C = 'c'.repeat(64), D = 'd'.repeat(64), FID = 'finish-' + '1'.repeat(32), FID2 = 'finish-' + '2'.repeat(32);
const E1 = {path: 'AGENTS.md', pending: 'AGENTS.md.new'}, E2 = {path: 'en/AGENTS.md', pending: 'en/AGENTS.md.new'};
function archive(id) { const base = '.agent/merge-backups/' + id; return {id: id, dir: base, current: base + '/current.txt', incoming: base + '/incoming.txt', record: base + '/record.json', retired: base + '/pending-retired.txt'}; }
function FPV(e, id, cur, cand, extra) { return Object.assign({schema: FPS, path: e.path, pending: e.pending, eligible: true, reason: null, identical: false,
  current_sha256: cur, candidate_sha256: cand, diff: {added: 2, removed: 1, hunks: []}, finish_id: id, archive: archive(id)}, extra || {}); }
const paths = () => calls.map(c => c[0]);
const count = p => calls.filter(c => c[0] === p).length;
const html = k => boxes['#' + k] ? boxes['#' + k].innerHTML : null;
async function openGuide() { closeSheet(); RESP['/api/merge/preview'] = {replace_preview: {schema: PVS, path: 'docs/a.md', pending: 'docs/a.md.new', eligible: true, reason: null, current_sha256: C, candidate_sha256: D}};
  await mpLoad('docs/a.md.new', 'docs/a.md'); }
async function entry(e, id, cur, cand, extra) { RESP['/api/merge/finish-preview'] = {finish_preview: FPV(e, id || FID, cur || A, cand || B, extra)}; calls.length = 0; return mfEntry(e.pending, e.path); }
(async function () {
  const out = {};
  // 1. a replace token is open, then the entrypoint entry: no replace preview, no replace token, a fresh finish preview and a separate confirm
  await openGuide(); out.had_token = MP !== null; const seq0 = MPSEQ;
  RESP['/api/merge/finish'] = {finish: {outcome: 'finished', reason: null, archive: archive(FID), pending: E1.pending}};
  await entry(E1); out.entry = {paths: paths(), seq_bumped: MPSEQ > seq0, mp: MP, mpbox: html('mp-box'), html: html('mf-box'), title: sheets[sheets.length - 1], diffs: diffs.length,
    hidden: sheet.hidden, aria: sheet.attrs['aria-label']};
  await mpAct('use'); out.use_after_entry = count('/api/merge/replace'); out.preview_calls = count('/api/merge/preview');
  await mfAct('confirm'); out.confirm = {bodies: calls.filter(c => c[0] === '/api/merge/finish').map(c => c[1]), replace: count('/api/merge/replace'), html: html('mf-box'), refreshed: refreshed};
  await mfAct('confirm'); out.second_confirm = count('/api/merge/finish');
  // 2. an ineligible, foreign or malformed finish preview never binds a pair
  await entry(E1, null, A, B, {eligible: false, reason: 'os_unsupported', finish_id: null, archive: null}); out.ineligible = {mf: MF, html: html('mf-box')};
  await entry(E1, FID, A, B, {pending: 'docs/other.md.new'}); out.foreign = {mf: MF, html: html('mf-box')};
  await entry(E1, FID, A, B, {path: 'docs/other.md'}); out.foreign_path = MF;
  await entry(E1, FID, A, B, {schema: 'forged'}); out.forged = MF;
  await entry(E1, 'finish-xyz', A, B); out.bad_id = MF;
  RESP['/api/merge/finish-preview'] = () => Promise.reject(new Error('offline')); calls.length = 0; await mfEntry(E1.pending, E1.path); out.offline = {mf: MF, html: html('mf-box')};
  // 3. a slow preview of the first entrypoint cannot bind after the user moved to another one or closed the sheet
  let slow; RESP['/api/merge/finish-preview'] = b => b.path === E1.pending ? new Promise(r => { slow = r; }) : {finish_preview: FPV(E2, FID2, C, D)};
  calls.length = 0; const p1 = mfEntry(E1.pending, E1.path); await mfEntry(E2.pending, E2.path); slow({finish_preview: FPV(E1, FID, A, B)}); await p1;
  out.switched = {mf: MF && [MF.pending, MF.finish_id], html: html('mf-box')};
  RESP['/api/merge/finish'] = {finish: {outcome: 'finished', archive: archive(FID2)}}; await mfAct('confirm');
  out.switched_confirm = calls.filter(c => c[0] === '/api/merge/finish').map(c => c[1]);
  let slow2; RESP['/api/merge/finish-preview'] = () => new Promise(r => { slow2 = r; });
  const p2 = mfEntry(E1.pending, E1.path); closeSheet(); slow2({finish_preview: FPV(E1, FID, A, B)}); await p2; out.closed = {mf: MF, html: html('mf-box')};
  // 4. moving from a bound entrypoint to a guide drops the pair; back never asks for a replace preview and leaves nothing to confirm
  await entry(E1); await openGuide(); calls.length = 0; await mfAct('confirm'); out.to_guide_confirm = count('/api/merge/finish');
  await entry(E1); calls.length = 0; await mfAct('back'); out.back = {paths: paths(), html: html('mf-box')}; await mfAct('confirm'); out.back_confirm = count('/api/merge/finish');
  await mfAct('preview'); out.back_preview = {mf: MF && MF.finish_id, paths: paths()};
  // 5. one in-flight apply at most
  await entry(E1); let slowD; RESP['/api/merge/finish'] = () => new Promise(r => { slowD = r; });
  const d1 = mfAct('confirm'), d2 = mfAct('confirm'); out.double_during = count('/api/merge/finish');
  slowD({finish: {outcome: 'finished', archive: archive(FID)}}); await d1; await d2; out.double_after = count('/api/merge/finish');
  // 6. a lost response is observed with the same id and never sent again
  await entry(E1); RESP['/api/merge/finish'] = () => Promise.reject(new Error('offline')); await mfAct('confirm'); const n0 = count('/api/merge/finish'); out.lost_html = html('mf-box');
  RESP['/api/merge/finish-observe'] = {finish_observation: {schema: FOS, state: 'finished', reason: null, finish_id: FID, archive: archive(FID)}}; await mfAct('observe');
  out.observe = {bodies: calls.filter(c => c[0] === '/api/merge/finish-observe').map(c => c[1]), resent: count('/api/merge/finish') - n0, html: html('mf-box')};
  // 7. the row button is drawn only for finish_supported === true and the click goes to the entry with that row's pair
  const rows = [{path: 'AGENTS.md', pending: 'AGENTS.md.new', current_exists: true, state: 'unseen', origin: 'package', finish_supported: true},
    {path: 'PROJECT.md', pending: 'PROJECT.md.new', current_exists: true, state: 'unseen', origin: 'package', finish_supported: false},
    {path: 'tools/x.py', pending: 'tools/x.py.new', current_exists: true, state: 'unseen', origin: 'package'},
    {path: 'docs/y.md', pending: 'docs/y.md.new', current_exists: true, state: 'unseen', origin: 'package', finish_supported: 'true'}];
  S.merges = rows; mg.handlers.length = 0; drawMerges();
  out.rows_html = mg.innerHTML; out.mfe_handlers = mg.handlers.filter(h => h[0] === 'mfe').map(h => h[1]);
  RESP['/api/merge/finish-preview'] = {finish_preview: FPV(E1, FID, A, B)}; calls.length = 0; sheets.length = 0;
  await mg.handlers.filter(h => h[0] === 'mfe')[0][2](); await new Promise(r => setTimeout(r, 0));
  out.row_click = {paths: paths(), bodies: calls.map(c => c[1]), title: sheets[0], bound: MF && MF.pending};
  rows[0].finish_supported = false; calls.length = 0; mg.handlers.filter(h => h[0] === 'mfe')[0][2](); out.row_click_forged = calls.length;  // a changed row cannot start the flow
  console.log(JSON.stringify(out));
})();
"""


@unittest.skipUnless(shutil.which('node'), 'node is needed to run the panel script outside a browser')
class EntrypointUiScript(unittest.TestCase):
    """Runs the real D01B + D01C blocks and the real drawMerges in node with a fake api and a minimal DOM. Proves the async flow, not the visual look."""

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory(prefix='entry-ui-') as tmp:
            script = Path(tmp) / 'harness.js'
            text = HARNESS.replace('%BLOCKB%', block('// D01B-BEGIN', '// D01B-END')).replace('%BLOCKC%', block('// D01C-BEGIN', '// D01C-END')) \
                .replace('%DRAW%', draw_merges_source())
            script.write_text(text, encoding='utf-8')
            done = subprocess.run(['node', str(script)], capture_output=True, encoding='utf-8', timeout=60)
        assert done.returncode == 0, done.stdout + done.stderr
        cls.out = json.loads(done.stdout.strip().splitlines()[-1])

    def test_the_entry_needs_no_replace_preview_and_drops_any_replace_token(self):
        o = self.out
        self.assertTrue(o['had_token'])
        e = o['entry']
        self.assertEqual(e['paths'], ['/api/merge/finish-preview'])  # không replace-preview / no replace preview
        self.assertTrue(e['seq_bumped'])
        self.assertIsNone(e['mp'])
        self.assertIsNone(e['mpbox'])
        self.assertIn('data-mf="confirm"', e['html'])
        self.assertIn('data-mf="back"', e['html'])
        self.assertIn('mf_entry_note', e['html'])
        self.assertIn('mf_will_cur', e['html'])
        self.assertNotIn('data-mp=', e['html'])  # không còn nút Dùng bản mới / Giữ bản của tôi / no Use-the-new or Keep-mine button
        self.assertEqual(e['title'], 'mf_entry · AGENTS.md')
        self.assertEqual(e['diffs'], 1)
        self.assertFalse(e['hidden'])
        self.assertEqual(o['use_after_entry'], 0)  # nút replace cũ vô hiệu / the old replace action is dead
        self.assertEqual(o['preview_calls'], 0)

    def test_confirm_sends_one_finish_with_the_previewed_pair_and_never_a_replace(self):
        c = self.out['confirm']
        self.assertEqual(c['bodies'], [{'path': 'AGENTS.md.new', 'current_sha256': 'a' * 64, 'candidate_sha256': 'b' * 64, 'finish_id': 'finish-' + '1' * 32}])
        self.assertEqual(c['replace'], 0)
        self.assertIn('mf_done', c['html'])
        self.assertEqual(c['refreshed'], 1)
        self.assertEqual(self.out['second_confirm'], 1)  # xem trước đã dùng / the preview is spent

    def test_ineligible_foreign_or_malformed_previews_never_bind_a_pair(self):
        o = self.out
        for key in ('ineligible', 'foreign', 'offline'):
            self.assertIsNone(o[key]['mf'], key)
            self.assertNotIn('data-mf="confirm"', o[key]['html'], key)
        self.assertIn('mf_r_os', o['ineligible']['html'])
        self.assertIn('mf_pv_fail', o['foreign']['html'])
        self.assertIn('mf_pv_fail', o['offline']['html'])
        for key in ('foreign_path', 'forged', 'bad_id'):
            self.assertIsNone(o[key], key)

    def test_a_slow_response_cannot_bind_after_a_switch_or_a_close(self):
        o = self.out
        self.assertEqual(o['switched']['mf'], ['en/AGENTS.md.new', 'finish-' + '2' * 32])
        self.assertEqual(o['switched_confirm'], [{'path': 'en/AGENTS.md.new', 'current_sha256': 'c' * 64, 'candidate_sha256': 'd' * 64, 'finish_id': 'finish-' + '2' * 32}])
        self.assertIsNone(o['closed']['mf'])
        self.assertNotIn('data-mf="confirm"', o['closed']['html'] or '')

    def test_moving_to_a_guide_or_going_back_leaves_nothing_to_confirm(self):
        o = self.out
        self.assertEqual(o['to_guide_confirm'], 0)
        self.assertEqual(o['back']['paths'], [])  # quay lại không xem trước replace / back does not preview a replace
        self.assertIn('data-mf="preview"', o['back']['html'])
        self.assertNotIn('data-mf="confirm"', o['back']['html'])
        self.assertEqual(o['back_confirm'], 0)
        self.assertEqual(o['back_preview']['paths'], ['/api/merge/finish-preview'])
        self.assertEqual(o['back_preview']['mf'], 'finish-' + '1' * 32)

    def test_a_double_click_sends_one_apply_and_a_lost_response_is_only_observed(self):
        o = self.out
        self.assertEqual((o['double_during'], o['double_after']), (1, 1))
        self.assertIn('mf_net', o['lost_html'])
        self.assertEqual(o['observe']['bodies'], [{'path': 'AGENTS.md.new', 'current_sha256': 'a' * 64, 'candidate_sha256': 'b' * 64, 'finish_id': 'finish-' + '1' * 32}])
        self.assertEqual(o['observe']['resent'], 0)
        self.assertIn('mf_done', o['observe']['html'])

    def test_the_row_button_follows_the_scan_flag_and_a_changed_row_cannot_start_the_flow(self):
        o = self.out
        self.assertEqual(o['mfe_handlers'], ['0'])  # chỉ finish_supported === true / only a strict true
        self.assertEqual(o['rows_html'].count('data-mfe='), 1)
        self.assertIn('mf_entry', o['rows_html'])
        self.assertEqual(o['row_click']['paths'], ['/api/merge/finish-preview'])
        self.assertEqual(o['row_click']['bodies'], [{'path': 'AGENTS.md.new'}])
        self.assertEqual(o['row_click']['title'], 'mf_entry · AGENTS.md')
        self.assertEqual(o['row_click']['bound'], 'AGENTS.md.new')
        self.assertEqual(o['row_click_forged'], 0)

    def test_script_text_keeps_the_old_boundaries(self):
        c = block('// D01C-BEGIN', '// D01C-END')
        for forbidden in ('/api/open', 'openPath', 'merge_state', 'launch', 'startfile', '/api/merge/replace', "api('/api/run'"):
            self.assertNotIn(forbidden, c)
        self.assertEqual(sorted(set(re.findall(r"api\('(/api/[a-z/-]+)'", c))), ['/api/merge/finish', '/api/merge/finish-observe', '/api/merge/finish-preview'])
        self.assertEqual(len(re.findall(r"api\('/api/merge/finish'", c)), 1)
        self.assertEqual(len(re.findall(r'mfConfirm\(', c)), 2)
        self.assertIn("if(kind==='keep'){closeSheet();toast(t('mp_kept'));return Promise.resolve('kept');}", block('// D01B-BEGIN', '// D01B-END'))
        self.assertEqual(sorted(set(re.findall(r"api\('(/api/[a-z/]+)'", block('// D01B-BEGIN', '// D01B-END')))), ['/api/merge/preview', '/api/merge/replace'])
        self.assertNotIn('mfAttach', draw_merges_source())  # điểm vào mới không đi qua replace-preview / the new entry does not go through the replace preview


def ui_dictionary():
    text = UI_FILE.read_text(encoding='utf-8')
    pairs = {}
    for m in re.finditer(r"\b(mf_[a-z_]+):\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)'\]", text):
        pairs[m.group(1)] = (m.group(2), m.group(3))
    return pairs


class EntrypointUiTexts(unittest.TestCase):
    FORBIDDEN = ('Reviewed', 'reviewed', 'Resolved', 'resolved', 'đã giải quyết', 'Đã giải quyết', 'Đã hợp nhất', 'Merged', 'atomic', 'nguyên tử', 'Undo', 'Hoàn tác:',
                 'đã cập nhật hướng dẫn', 'instruction is updated', 'đúng policy', 'granted', 'đã cấp quyền')

    def test_the_new_keys_exist_in_both_languages_and_make_no_false_claim(self):
        d = ui_dictionary()
        for key in ('mf_entry', 'mf_entry_note'):
            vi, en = d[key]
            self.assertTrue(vi.strip() and en.strip(), key)
            for bad in self.FORBIDDEN:
                for text in (vi, en):
                    self.assertIsNone(re.search(r'(?<![A-Za-z])' + re.escape(bad) + r'(?![A-Za-z])', text), (key, bad))
        self.assertIn('.new', d['mf_entry'][0])
        self.assertIn('.new', d['mf_entry'][1])
        self.assertIn('không được áp', d['mf_entry_note'][0])
        self.assertIn('not applied', d['mf_entry_note'][1])
        self.assertNotEqual(d['mf_entry'][0], d['mf_btn'][0])
        for text in d['mf_entry_note']:  # không hứa mọi host đều không đọc .new hoặc archive / no promise about what every host reads
            self.assertNotRegex(text, r'(?i)không (host|agent) nào|no (host|agent) will')


# ------------------------------------------------------------------------------------------------ lifecycle: real new_project + upgrade_package
def run(base, script, *args):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, str(Path(base) / 'tools' / script), *map(str, args)], cwd=str(base), env=e,
                          capture_output=True, encoding='utf-8', timeout=300)


def envelope(result):
    return result_schema.split_output(result.stdout)[1]


@unittest.skipUnless(os.name == 'nt' and HAVE_JSONSCHEMA,
                     'NOT_CHECKED: needs Windows (the no-replace rename) and jsonschema (the profile and pin checks)')
class EntrypointLifecycle(unittest.TestCase):
    """A -> B -> C of a clean projected v3 package; the source changes only ordinary instruction prose (root AGENTS.md and the en overlay).
    The VERSION values are fake labels. No migration, no host or native step, no release; NOT proof of the whole P4 or T39."""

    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(setattr, ep, 'LANG', ep.LANG)
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-d01e-lc-')
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.base = Path(cls.tmp.name)
        cls.A, cls.B, cls.C = (cls.base / n for n in 'ABC')
        cp.materialize(str(cls.A), branding=False)
        shutil.copytree(str(cls.A), str(cls.B))
        shutil.copytree(str(cls.A), str(cls.C))
        for pkg, version, tag in ((cls.A, '91.0.0', None), (cls.B, '91.0.1', 'B'), (cls.C, '91.0.2', 'C')):
            write(pkg, 'VERSION', version + '\n')
            if tag:
                for rel in ('AGENTS.md', 'en/AGENTS.md'):
                    raw = (pkg / rel).read_bytes()
                    eol = '\r\n' if b'\r\n' in raw else '\n'  # giữ EOL của file nguồn / keep the source file's EOL
                    write(pkg, rel, raw + (eol + 'Dòng thêm của bản %s / line added in %s' % (tag, tag) + eol).encode('utf-8'))
            done = run(pkg, 'check_package.py', '--write-manifest')
            assert done.returncode == 0, done.stdout + done.stderr

    def make_project(self, lang):
        dest = Path(tempfile.mkdtemp(prefix='dest-', dir=str(self.base)))
        r = run(self.A, 'new_project.py', '--name', 'P-' + lang, '--dest', dest, '--lang', lang, '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        proj = dest / ('P-' + lang)
        ep.LANG = lang
        choices = {'host': 'claude-code', 'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}}}
        plan = ep.plan_config(str(proj), choices)
        self.assertEqual(plan['status'], 'PREVIEW', plan)
        done = ep.apply_config(str(proj), choices, plan['plan']['plan_sha256'])
        self.assertEqual(done['status'], 'WRITTEN', done)
        return proj

    def source_for(self, pkg, lang):
        return (pkg / ('en/AGENTS.md' if lang == 'en' else 'AGENTS.md')).read_bytes()

    def lifecycle(self, lang):
        proj = self.make_project(lang)
        edited = (proj / 'AGENTS.md').read_bytes() + 'Dòng sửa của người dùng\r\n'.encode('utf-8')  # EOL trộn là của người dùng / the user's mixed EOL
        (proj / 'AGENTS.md').write_bytes(edited)
        keep = ('PROJECT.md', ep.PROFILE_REL, '.agent/STATE.md', *cp.CVF_CLOSURE, *cp.BYTE_EXACT)
        kept0 = {rel: (proj / rel).read_bytes() for rel in keep}
        before = tree_state(proj)
        pv = run(self.B, 'upgrade_package.py', '--project', proj, '--result-json')
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertEqual(tree_state(proj), before)  # xem trước nâng cấp không ghi / the upgrade preview writes nothing
        ap = run(self.B, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        delta = changed(before, tree_state(proj))
        self.assertIn('AGENTS.md.new', delta)
        self.assertNotIn('AGENTS.md', delta)
        self.assertEqual((proj / 'AGENTS.md').read_bytes(), edited)
        cand_b = self.source_for(self.B, lang)
        self.assertEqual((proj / 'AGENTS.md.new').read_bytes(), cand_b)  # đúng bytes của bản B theo ngôn ngữ / exactly B's bytes for this language
        for rel in ('CLAUDE.md', 'GEMINI.md'):
            self.assertFalse((proj / (rel + '.new')).exists(), rel)
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, kept0)
        self.assertEqual(cp.pin_problems(str(proj)), [])
        # ---- finish: the current file, profile, PROJECT, machine files and the manifest stay as they are
        manifest_b = (proj / 'MANIFEST.sha256').read_bytes()
        info_b = (proj / '.agent/PACKAGE_INFO.json').read_bytes()
        fpv = merge_center.preview_finish(str(proj), 'AGENTS.md.new')
        self.assertTrue(fpv['eligible'], fpv)
        self.assertEqual((fpv['current_sha256'], fpv['candidate_sha256']), (sha(edited), sha(cand_b)))
        res = merge_center.apply_finish(str(proj), 'AGENTS.md.new', fpv['current_sha256'], fpv['candidate_sha256'], fpv['finish_id'])
        self.assertEqual((res['outcome'], res['reason']), ('finished', None), res)
        arc = proj / '.agent' / 'merge-backups' / fpv['finish_id']
        self.assertEqual((proj / 'AGENTS.md').read_bytes(), edited)
        self.assertEqual((arc / 'current.txt').read_bytes(), edited)
        self.assertEqual((arc / 'incoming.txt').read_bytes(), cand_b)
        self.assertEqual((arc / 'pending-retired.txt').read_bytes(), cand_b)
        self.assertFalse((proj / 'AGENTS.md.new').exists())
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, kept0)
        self.assertEqual((proj / 'MANIFEST.sha256').read_bytes(), manifest_b)
        self.assertEqual([r['path'] for r in merge_center.scan(str(proj)) if r['path'] == 'AGENTS.md'], [])
        archive_b = {p.relative_to(proj).as_posix(): p.read_bytes() for p in arc.rglob('*') if p.is_file()}
        # ---- C: a new candidate is produced by the same engine; the stored pending of B does not block it and the current file is not overwritten
        before_c = tree_state(proj)
        pv = run(self.C, 'upgrade_package.py', '--project', proj, '--result-json')
        self.assertEqual((pv.returncode, envelope(pv)['status']), (0, 'preview'), pv.stdout + pv.stderr)
        self.assertEqual(tree_state(proj), before_c)
        ap = run(self.C, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(ap.returncode, 0, ap.stdout + ap.stderr)
        cand_c = self.source_for(self.C, lang)
        self.assertNotEqual(cand_c, cand_b)
        self.assertEqual((proj / 'AGENTS.md.new').read_bytes(), cand_c)
        self.assertEqual((proj / 'AGENTS.md').read_bytes(), edited)
        self.assertEqual({p.relative_to(proj).as_posix(): p.read_bytes() for p in arc.rglob('*') if p.is_file()}, archive_b)
        self.assertEqual({rel: (proj / rel).read_bytes() for rel in keep}, kept0)
        self.assertEqual(json.loads((proj / '.agent/PACKAGE_INFO.json').read_text(encoding='utf-8'))['version'], '91.0.2')
        self.assertNotEqual((proj / '.agent/PACKAGE_INFO.json').read_bytes(), info_b)
        row = [r for r in merge_center.scan(str(proj)) if r['path'] == 'AGENTS.md']
        self.assertEqual([(r['pending'], r['finish_supported']) for r in row], [('AGENTS.md.new', True)])
        seen = merge_center.observe_finish(str(proj), 'AGENTS.md.new', fpv['current_sha256'], fpv['candidate_sha256'], fpv['finish_id'])
        self.assertNotEqual(seen['state'], 'finished')  # slot mới có .new khác: record cũ không được báo xong cho candidate C / the new .new is a different candidate: the old record is not "finished" for it

    def test_vi_project_keeps_the_edited_agents_and_both_candidates_come_from_the_root_file(self):
        self.lifecycle('vi')

    def test_en_project_keeps_the_edited_agents_and_both_candidates_come_from_the_en_overlay(self):
        self.lifecycle('en')


if __name__ == '__main__':
    unittest.main()
