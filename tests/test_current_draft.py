"""I2 checks: current draft and its history (tools/current_draft.py, the dedicated /api/draft/* routes).

Every test works in a fresh temporary project with fake data and revisions written by the real P-CN1 writer (tools/publish_new.py).
Opening a file never launches an application here: the opener is replaced (in-process) or recorded (TEST ONLY env var in a subprocess).
Selecting a draft is navigation, not acceptance: nothing here evaluates grants, D4 or a checker PASS.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import context_update as cu  # noqa: E402
import current_draft as cd  # noqa: E402
import publish_new as pn  # noqa: E402
import result_schema  # noqa: E402
import transaction as tx  # noqa: E402

try:
    import jsonschema  # noqa: F401
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False

WINDOWS = os.name == 'nt'
NEED = unittest.skipUnless(WINDOWS and HAVE_JSONSCHEMA, 'current draft needs Windows NTFS and jsonschema (the pin check)')
STATE_REL = '.agent/STATE.md'
HEADINGS = cu.STATE_HEADINGS
# Reviewed owner-byte regression pins (SHA256 prefixes); AN C2 refreshes only reviewed owner deltas.
# Context/policy and transaction pins include the permitted CLI UTF-8 maintenance; other pins stay fixed.
# P-CTX1 revision 28/10/2026: derived vectors refresh; see HANDOFF rev144.
# Transaction pin follows reviewed P1 opt-in owner (p1/REVIEW.md + custody.json); default v1 remains.
OWNER_PINS = {
    'tools/publish_new.py': '8a4e5914d0892ea1', 'tools/context_update.py': '65fd87929e886393', 'tools/transaction.py': '5aa6482007e0c0c2',
    '.cvf/checks/v3/observer.py': '7c0a089e5eb03475', '.cvf/checks/v3/workflow.py': '3019bd55a70281d0', '.cvf/checks/v3/loader.py': '0a50424e8e767ce8',
    '.cvf/checks/v3/canon.py': '7ab1bf8e6b94e2b0', '.cvf/checks/v3/binding.py': 'f227eda4a8f73e5e', '.cvf/checks/v3/routing.py': '37845b6bc357ad24',
    '.cvf/checks/v3/refs.py': '33761fd35bd6b8f6', '.cvf/checks/control_check_v3.py': 'e4bcbf35faa3392d',
    '.cvf/rules/v3/ROUTING_POLICY.json': '4577f71406997acb', '.cvf/contracts/v3/control.schema.json': '21d3b192151b84f6',
    '.cvf/contracts/v3/vectors.json': 'eb59221f24200df8', '.cvf/checks/v2/loader.py': 'a1216b35eba1ff4f',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def tree(root):
    """Every file and folder under root with bytes: the whole project, runtime included."""
    out = {}
    for p in sorted(Path(root).rglob('*')):
        out[p.relative_to(root).as_posix()] = p.read_bytes() if p.is_file() else None
    return out


def att():
    return {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:msg/0012',
            'recorded_by': {'actor_id': 'main', 'role': 'main'}}


def state_text(section_body='- Chưa chọn bản nào.\n', lines_after=0, eol='\n'):
    parts = ['# PROJECT STATE', '']
    for h in HEADINGS:
        parts += ['## ' + h, '', section_body.rstrip('\n') if h == 'Current artifact' else 'Nội dung ' + h, '']
    parts += ['- thêm'] * lines_after
    return eol.join(parts) + eol


def rid_of(n):
    return '%032x' % n


def make_project(root, state=None):
    os.makedirs(os.path.join(root, '.agent', 'runtime'))
    os.makedirs(os.path.join(root, 'references', 'source-documents'))
    with open(os.path.join(root, 'references', 'source-documents', 'quy-che.pdf'), 'wb') as f:
        f.write(b'%PDF fake source')
    with open(os.path.join(root, STATE_REL), 'wb') as f:
        f.write((state if state is not None else state_text()).encode('utf-8'))


def publish(root, n, work, target, data=None):
    """One real P-CN1 revision (caller rid): request -> prepared -> staged -> link -> published, in a single owner call."""
    request = {'work_id': work, 'target': target,
               'intent_ref': {'ref_id': 'intent-1', 'locator': 'host:msg/0012', 'digest': 'sha256:' + '5' * 64, 'attribution': att()},
               'main_interpretation': 'Báo cáo ngắn',
               'requirements': [{'req_id': 'REQ-1', 'statement': 'Tóm tắt', 'mandatory': True}],
               'grant_refs': [{'ref_id': 'grant-1', 'locator': 'PROJECT.md#pham-vi', 'digest': 'sha256:' + '1' * 64, 'attribution': att()}],
               'subject': {'actor_id': 'main', 'role': 'main'},
               'inputs': [{'path': 'references/source-documents/quy-che.pdf', 'digest': pn._sha_bytes(b'%PDF fake source')}]}
    if target.startswith('output/'):
        request['content_use'] = ['internal_draft']
    r = pn.publish(root, request, data if data is not None else ('PK bản %d' % n).encode('utf-8'), request_id=rid_of(n))
    assert r['outcome'] == 'PUBLISHED', r
    return rid_of(n)


@NEED
class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='law-i2-')
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.junctions = []
        self.addCleanup(self._unlink_junctions)
        self.project = self.tmp
        make_project(self.project)
        self.r1 = publish(self.project, 1, 'w-1', 'working/w-1/bao-cao-v1.docx')
        self.r2 = publish(self.project, 2, 'w-1', 'working/w-1/bao-cao-v2.docx')
        self.r3 = publish(self.project, 3, 'w-2', 'working/w-2/khac.docx')
        self.opened = []
        patcher = mock.patch.object(cd, '_startfile', lambda path: self.opened.append(path))
        patcher.start()
        self.addCleanup(patcher.stop)
        guard = mock.patch.object(os, 'startfile', side_effect=AssertionError('generic opener must not be used'), create=True)
        guard.start()
        self.addCleanup(guard.stop)

    def _unlink_junctions(self):
        for j in self.junctions:
            try:
                os.rmdir(j)
            except OSError:
                pass

    def path(self, rel):
        return os.path.join(self.project, *rel.split('/'))

    def read(self, rel):
        with open(self.path(rel), 'rb') as f:
            return f.read()

    def write(self, rel, data):
        with open(self.path(rel), 'wb') as f:
            f.write(data)

    def junction(self, link, target):
        os.makedirs(target, exist_ok=True)
        r = subprocess.run(['cmd', '/c', 'mklink', '/J', link, target], capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest('cannot create a junction here: ' + r.stdout + r.stderr)
        self.junctions.append(link)

    def select(self, rid):
        """Preview then apply with the preview's own hashes, as the panel and the agent CLI do."""
        pv = cd.select_preview(self.project, rid)
        self.assertEqual(pv['result'], 'PREVIEW', pv)
        ap = cd.select_apply(self.project, rid, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual(ap['result'], 'WRITTEN', ap)
        return pv, ap

    def marker_count(self):
        return self.read(STATE_REL).decode('utf-8').count(cd.MARKER_WORD)


class Selection(Base):
    def test_nothing_is_selected_at_first_and_the_list_has_every_published_revision(self):
        s = cd.status(self.project)
        self.assertEqual((s['result'], s['pointer']['state'], s['selected'], s['history']), ('OK', 'NONE', None, []))
        lst = cd.list_candidates(self.project)
        self.assertEqual({i['rid'] for i in lst['items']}, {self.r1, self.r2, self.r3})
        self.assertEqual({i['name'] for i in lst['items']}, {'bao-cao-v1.docx', 'bao-cao-v2.docx', 'khac.docx'})
        self.assertFalse(any(i['selected'] for i in lst['items']))

    def test_preview_writes_nothing_and_binds_state_and_selection(self):
        before = tree(self.project)
        pv = cd.select_preview(self.project, self.r1)
        self.assertEqual((pv['result'], pv['status'], pv['changes'], pv['mode']), ('PREVIEW', 'preview', False, 'PREVIEW'))
        self.assertEqual(pv['state_sha256'], sha(self.read(STATE_REL)))
        self.assertRegex(pv['selection_fingerprint'], r'^[0-9a-f]{64}$')
        self.assertEqual(pv['selection']['rid'], self.r1)
        self.assertEqual(tree(self.project), before)
        again = cd.select_preview(self.project, self.r1)
        self.assertEqual(again['selection_fingerprint'], pv['selection_fingerprint'])  # deterministic: no observation time inside

    def test_apply_changes_only_state_and_its_own_p_ctx1_journal_and_keeps_every_artifact(self):
        before = tree(self.project)
        pv, ap = self.select(self.r1)
        after = tree(self.project)
        changed = [k for k in before if before[k] != after.get(k)]
        self.assertEqual(changed, [STATE_REL])
        added = sorted(set(after) - set(before))
        txd = '.agent/runtime/transactions/' + ap['txid']
        self.assertEqual(added, ['.agent/runtime/transactions', txd, txd + '/journal.json'])
        for rel in before:  # every artifact, receipt and source stays byte for byte
            if rel != STATE_REL:
                self.assertEqual(after[rel], before[rel], rel)
        self.assertEqual(self.marker_count(), 1)
        self.assertFalse(os.path.exists(self.path('.agent/runtime/operations.jsonl')))

    def test_marker_is_the_documented_line_and_text_outside_it_is_kept(self):
        before = self.read(STATE_REL).decode('utf-8')
        self.select(self.r1)
        after = self.read(STATE_REL).decode('utf-8')
        line = [ln for ln in after.split('\n') if cd.MARKER_WORD in ln]
        self.assertEqual(len(line), 1)
        obj = json.loads(line[0][len('<!-- law-current-draft/1 '):-len(' -->')])
        self.assertEqual(sorted(obj), ['digest', 'path', 'rid'])
        self.assertEqual((obj['path'], obj['rid']), ('working/w-1/bao-cao-v1.docx', self.r1))
        self.assertEqual(obj['digest'], pn._sha_bytes(self.read('working/w-1/bao-cao-v1.docx')))
        self.assertEqual(after.replace(line[0] + '\n', '', 1), before)
        self.assertTrue(after.index('## Current artifact') < after.index(cd.MARKER_WORD) < after.index('## Open items'))

    def test_crlf_and_missing_final_newline_are_preserved(self):
        text = state_text(eol='\r\n').rstrip('\r\n')
        self.write(STATE_REL, text.encode('utf-8'))
        self.select(self.r1)
        after = self.read(STATE_REL).decode('utf-8')
        self.assertNotIn('\n', after.replace('\r\n', ''))
        self.assertFalse(after.endswith('\n'))
        self.assertEqual(after.count(cd.MARKER_WORD), 1)
        self.assertEqual(cd.parse_pointer(pn, after)['state'], 'SET')
        self.select(self.r2)  # replacing keeps the same line ending and the rest
        again = self.read(STATE_REL).decode('utf-8')
        self.assertEqual(len(again.split('\r\n')), len(after.split('\r\n')))
        self.assertNotIn('\n', again.replace('\r\n', ''))

    def test_it_never_shortens_the_text_to_stay_under_sixty_lines(self):
        base = state_text()
        n = len(base.split('\n')) - 1
        self.write(STATE_REL, state_text(lines_after=60 - n).encode('utf-8'))
        before = tree(self.project)
        pv = cd.select_preview(self.project, self.r1)
        self.assertEqual((pv['result'], pv['reason'], pv['changes']), ('ERROR', 'STATE_TOO_LONG', False))
        pv = cd.select_apply(self.project, self.r1, sha(self.read(STATE_REL)), 'f' * 64)
        self.assertNotEqual(pv['result'], 'WRITTEN')
        self.assertEqual(tree(self.project), before)

    def test_selecting_one_two_one_with_the_card_and_history_each_time(self):
        self.select(self.r1)
        s = cd.status(self.project)
        self.assertEqual((s['selected']['rid'], s['selected']['state'], s['selected']['work_id']), (self.r1, 'matched', 'w-1'))
        self.assertEqual([(h['rid'], h['state']) for h in s['history']], [(self.r2, 'matched')])  # w-2 is not related
        self.select(self.r2)
        s = cd.status(self.project)
        self.assertEqual((s['selected']['rid'], s['selected']['name']), (self.r2, 'bao-cao-v2.docx'))
        self.assertEqual([h['rid'] for h in s['history']], [self.r1])
        self.select(self.r1)
        s = cd.status(self.project)
        self.assertEqual((s['selected']['rid'], [h['rid'] for h in s['history']]), (self.r1, [self.r2]))
        self.assertEqual(self.marker_count(), 1)  # a single pointer throughout
        self.assertEqual(self.read('working/w-1/bao-cao-v1.docx'), 'PK bản 1'.encode('utf-8'))  # old bytes kept
        self.assertEqual(self.read('working/w-1/bao-cao-v2.docx'), 'PK bản 2'.encode('utf-8'))
        again = cd.select_preview(self.project, self.r1)
        self.assertEqual(again['result'], 'UNCHANGED')

    def test_history_is_capped_at_five_related_revisions_of_the_same_work(self):
        extra = [publish(self.project, 10 + i, 'w-1', 'working/w-1/v%d.docx' % i) for i in range(6)]
        self.select(self.r1)
        s = cd.status(self.project)
        self.assertEqual(len(s['history']), cd.HISTORY_SHOWN)
        self.assertEqual(s['more'], len(extra) + 1 - cd.HISTORY_SHOWN)
        self.assertTrue(all(h['work_id'] == 'w-1' for h in s['history']))
        self.assertNotIn(self.r3, [h['rid'] for h in s['history']])
        times = [h['at'] for h in s['history']]
        self.assertEqual(times, sorted(times, reverse=True))  # time only orders the display

    def test_supersedes_is_not_used_to_choose_or_chain(self):
        s = cd.status(self.project)
        self.assertEqual(s['pointer']['state'], 'NONE')  # three published revisions, still nothing chosen by itself

    def test_candidate_limit_precedes_evidence_validation(self):
        owner = cd.Env(self.project).pn
        before = tree(self.project)
        with mock.patch.object(cd, 'MAX_CANDIDATES', 1), mock.patch.object(owner, 'status', wraps=owner.status) as scan:
            result = cd.list_candidates(self.project)
        self.assertEqual((len(result['items']), result['incomplete']), (1, True))
        self.assertTrue(scan.call_args_list)
        self.assertTrue(all(len(c.args) > 1 and c.args[1] is not None for c in scan.call_args_list))
        self.assertEqual(tree(self.project), before)

    def test_failed_history_discovery_or_candidate_read_is_incomplete(self):
        before = tree(self.project)
        with mock.patch.object(cd.os, 'scandir', side_effect=PermissionError('cannot list publish')):
            result = cd.list_candidates(self.project)
        self.assertEqual((result['result'], result['items'], result['incomplete']), ('OK', [], True))
        with mock.patch.object(cd, '_candidate', return_value=(None, 'EVIDENCE_INVALID')):
            result = cd.list_candidates(self.project)
        self.assertEqual((result['items'], result['incomplete']), ([], True))
        self.assertEqual(tree(self.project), before)

    def test_rid_must_be_32_lowercase_hex(self):
        for bad in (None, '', 'abc', 'a' * 31 + 'A', self.r1 + '0', '../' + self.r1[3:], 123):
            self.assertEqual(cd.select_preview(self.project, bad)['reason'], 'RID_INVALID')
            self.assertEqual(cd.open_draft(self.project, bad)['reason'], 'RID_INVALID')
        self.assertEqual(cd.select_apply(self.project, self.r1, sha(b'x'), 'abc')['reason'], 'EXPECTED_INVALID')
        self.assertEqual(cd.select_apply(self.project, self.r1, 'xyz', 'a' * 64)['reason'], 'EXPECTED_INVALID')


class Staleness(Base):
    def test_stale_state_after_preview_is_a_conflict_and_nothing_is_written(self):
        pv = cd.select_preview(self.project, self.r1)
        self.write(STATE_REL, self.read(STATE_REL) + 'Một dòng do người dùng thêm.\n'.encode('utf-8'))
        before = tree(self.project)
        ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['reason'], ap['changes']), ('CONFLICT', 'STATE_CHANGED', False))
        self.assertEqual(tree(self.project), before)

    def test_a_different_selection_fingerprint_is_a_conflict(self):
        pv = cd.select_preview(self.project, self.r1)
        before = tree(self.project)
        for fp in ('0' * 64, cd.select_preview(self.project, self.r2)['selection_fingerprint']):
            ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], fp)
            self.assertEqual((ap['result'], ap['reason']), ('CONFLICT', 'SELECTION_CHANGED'))
        self.assertEqual(tree(self.project), before)

    def test_bytes_or_identity_changing_after_preview_blocks_apply(self):
        pv = cd.select_preview(self.project, self.r1)
        target = 'working/w-1/bao-cao-v1.docx'
        original = self.read(target)
        self.write(target, original + b' sua')
        before = tree(self.project)
        ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['reason'], ap['changes']), ('ERROR', 'TARGET_NOT_MATCHING', False))
        self.assertEqual(tree(self.project), before)
        # same bytes again but a different file (new identity): still not the recorded file
        os.remove(self.path(target))
        self.write(target, original)
        ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['reason']), ('ERROR', 'TARGET_NOT_MATCHING'))
        self.assertEqual(self.marker_count(), 0)

    def test_evidence_removed_after_preview_blocks_apply(self):
        pv = cd.select_preview(self.project, self.r1)
        os.remove(self.path('.agent/runtime/publish/%s.published.json' % self.r1))
        ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['changes']), ('ERROR', False))
        self.assertEqual(self.marker_count(), 0)

    def test_a_changed_revision_cannot_be_selected_but_stays_openable_after_acknowledgement(self):
        self.select(self.r1)
        self.write('working/w-1/bao-cao-v2.docx', b'user edit outside the app')
        s = cd.status(self.project)
        self.assertEqual([(h['rid'], h['state']) for h in s['history']], [(self.r2, 'changed')])
        pv = cd.select_preview(self.project, self.r2)
        self.assertEqual((pv['result'], pv['reason'], pv['draft_state']), ('ERROR', 'TARGET_NOT_MATCHING', 'changed'))

    def test_failure_to_update_the_context_after_publish_keeps_the_files_and_does_not_publish_again(self):
        listing = sorted(os.listdir(self.path('.agent/runtime/publish')))
        pv = cd.select_preview(self.project, self.r1)
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'stage:1'}):
            ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['changes']), ('ERROR', False), ap)
        self.assertEqual(self.marker_count(), 0)
        self.assertEqual(sorted(os.listdir(self.path('.agent/runtime/publish'))), listing)  # no new publish, nothing deleted
        self.assertEqual(self.read('working/w-1/bao-cao-v1.docx'), 'PK bản 1'.encode('utf-8'))
        self.assertEqual(cd.status(self.project)['pointer']['state'], 'NONE')

    def test_unknown_write_outcome_is_passed_through_not_invented(self):
        pv = cd.select_preview(self.project, self.r1)
        unknown = {'result': 'UNKNOWN', 'reason': 'OUTCOME_UNPROVEN', 'changes': None, 'status': 'partial', 'code': 5, 'txid': 'x'}
        fake = mock.Mock(update=mock.Mock(return_value=unknown), preview=cu.preview)
        with mock.patch.object(cd.Env, 'ctx', lambda self: fake):
            ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['changes'], ap['code']), ('UNKNOWN', None, 5))
        self.assertEqual(ap['selection']['rid'], self.r1)
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'commit:1'}):
            ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
        self.assertEqual((ap['result'], ap['changes'], ap['reason']), ('WRITTEN', True, 'COMPLETION_ERROR'))  # replaced, but the journal was left open
        self.assertEqual(self.marker_count(), 1)


class Pointer(Base):
    def parse(self, body):
        return cd.parse_pointer(pn, state_text(section_body=body))

    def good(self, **over):
        obj = {'path': 'working/w-1/bao-cao-v1.docx', 'rid': rid_of(1), 'digest': 'sha256:' + 'a' * 64}
        obj.update(over)
        return '<!-- law-current-draft/1 %s -->\n' % json.dumps(obj, separators=(',', ':'))

    def test_exactly_one_well_formed_marker_in_the_section_resolves(self):
        p = self.parse(self.good())
        self.assertEqual((p['state'], p['tuple']['rid']), ('SET', rid_of(1)))

    def test_absent_marker_is_none_not_a_guess(self):
        p = self.parse('- Chưa chọn.\n')
        self.assertEqual((p['state'], p['tuple']), ('NONE', None))

    def test_every_malformed_or_ambiguous_marker_is_unresolved(self):
        good = self.good()
        cases = {
            'duplicate marker': (good + good, 'MARKER_DUPLICATE'),
            'second marker, one broken': (good + '<!-- law-current-draft/1 {broken -->\n', 'MARKER_DUPLICATE'),
            'marker word in prose': (good + 'ghi chú law-current-draft ở đây\n', 'MARKER_DUPLICATE'),
            'other version': ('<!-- law-current-draft/2 {"path":"working/a.docx","rid":"%s","digest":"sha256:%s"} -->\n' % (rid_of(1), 'a' * 64), 'MARKER_MALFORMED'),
            'extra key': (self.good(extra=1), 'MARKER_MALFORMED'),
            'missing key': ('<!-- law-current-draft/1 {"path":"working/a.docx","rid":"%s"} -->\n' % rid_of(1), 'MARKER_MALFORMED'),
            'duplicate JSON key': ('<!-- law-current-draft/1 {"path":"working/a.docx","path":"working/b.docx","rid":"%s","digest":"sha256:%s"} -->\n' % (rid_of(1), 'a' * 64), 'MARKER_MALFORMED'),
            'not JSON': ('<!-- law-current-draft/1 not json -->\n', 'MARKER_MALFORMED'),
            'NaN': ('<!-- law-current-draft/1 {"path":NaN,"rid":"x","digest":"y"} -->\n', 'MARKER_MALFORMED'),
            'text on the marker line': ('Nháp: ' + good, 'MARKER_MALFORMED'),
            'int rid': (self.good(rid=1), 'MARKER_MALFORMED'),
            'upper rid': (self.good(rid=rid_of(1).upper().replace('0', 'A')), 'MARKER_MALFORMED'),
            'short digest': (self.good(digest='sha256:abc'), 'MARKER_MALFORMED'),
            'digest without prefix': (self.good(digest='a' * 64), 'MARKER_MALFORMED'),
            'absolute path': (self.good(path='/working/a.docx'), 'MARKER_MALFORMED'),
            'drive path': (self.good(path='C:/working/a.docx'), 'MARKER_MALFORMED'),
            'backslash': (self.good(path='working\\a.docx'), 'MARKER_MALFORMED'),
            'traversal': (self.good(path='working/../PROJECT.md'), 'MARKER_MALFORMED'),
            'alternate data stream': (self.good(path='working/a.docx:evil'), 'MARKER_MALFORMED'),
            'outside working/output': (self.good(path='references/a.docx'), 'MARKER_MALFORMED'),
            'runtime path': (self.good(path='.agent/runtime/a.docx'), 'MARKER_MALFORMED'),
            'unknown extension': (self.good(path='working/a.exe'), 'MARKER_MALFORMED'),
            'html': (self.good(path='working/a.html'), 'MARKER_MALFORMED'),
            'svg': (self.good(path='working/a.svg'), 'MARKER_MALFORMED'),
            'macro workbook': (self.good(path='working/a.xlsm'), 'MARKER_MALFORMED'),
            'comment terminator in path': (self.good(path='working/a--b.docx'), 'MARKER_MALFORMED'),
        }
        for name, (body, reason) in cases.items():
            with self.subTest(name):
                p = self.parse(body)
                self.assertEqual((p['state'], p['reason'], p['tuple']), ('UNRESOLVED', reason, None), name)

    def test_marker_in_the_wrong_section_or_a_broken_section_is_unresolved(self):
        text = state_text().replace('Nội dung Goal', self.good().rstrip('\n'), 1)
        self.assertEqual(cd.parse_pointer(pn, text)['reason'], 'MARKER_WRONG_SECTION')
        no_section = state_text().replace('## Current artifact', '## Other artifact')
        self.assertEqual(cd.parse_pointer(pn, no_section)['reason'], 'SECTION_MISSING')
        twice = state_text() + '\n## Current artifact\n\nnữa\n'
        self.assertEqual(cd.parse_pointer(pn, twice)['reason'], 'SECTION_DUPLICATE')
        self.assertEqual(cd.parse_pointer(pn, state_text() + '<!-- law-current-draft/1 {} -->\n')['reason'], 'MARKER_WRONG_SECTION')

    def test_a_broken_pointer_blocks_select_and_is_never_repaired(self):
        self.write(STATE_REL, state_text(self.good() + self.good()).encode('utf-8'))
        before = tree(self.project)
        s = cd.status(self.project)
        self.assertEqual((s['pointer']['state'], s['pointer']['reason'], s['selected']), ('UNRESOLVED', 'MARKER_DUPLICATE', None))
        pv = cd.select_preview(self.project, self.r1)
        self.assertEqual((pv['result'], pv['reason'], pv['detail']), ('ERROR', 'POINTER_UNRESOLVED', 'MARKER_DUPLICATE'))
        ap = cd.select_apply(self.project, self.r1, sha(self.read(STATE_REL)), 'a' * 64)
        self.assertNotEqual(ap['result'], 'WRITTEN')
        self.assertEqual(tree(self.project), before)

    def test_a_noncanonical_section_heading_is_refused_without_an_exception(self):
        for ending in (' ', '\t'):
            self.write(STATE_REL, state_text().replace('## Current artifact\n', '## Current artifact' + ending + '\n').encode('utf-8'))
            before = tree(self.project)
            s = cd.status(self.project)
            self.assertEqual((s['pointer']['state'], s['pointer']['reason']), ('UNRESOLVED', 'SECTION_MALFORMED'))
            pv = cd.select_preview(self.project, self.r1)
            self.assertEqual((pv['result'], pv['reason'], pv['detail']), ('ERROR', 'POINTER_UNRESOLVED', 'SECTION_MALFORMED'))
            self.assertEqual(tree(self.project), before)

    def test_no_mtime_or_supersedes_fallback_when_the_pointer_is_unresolved(self):
        self.write(STATE_REL, state_text(self.good() + self.good()).encode('utf-8'))
        s = cd.status(self.project)
        self.assertIsNone(s['selected'])
        self.assertEqual(s['history'], [])


class Observation(Base):
    def test_a_pointer_to_unknown_evidence_is_unverified_but_still_listed_as_such(self):
        self.select(self.r1)
        for name in ('published.json', 'prepared.json'):
            os.remove(self.path('.agent/runtime/publish/%s.%s' % (self.r1, name)))
        s = cd.status(self.project)
        self.assertEqual((s['selected']['state'], s['selected']['reason']), ('unverified', 'EVIDENCE_MISSING'))
        self.assertEqual(s['history'], [])  # no work_id can be resolved, so no history is inferred from names or mtime

    def test_proof_missing_but_safe_differs_from_unavailable_owner_or_pin(self):
        self.select(self.r1)
        os.remove(self.path('.agent/runtime/publish/%s.published.json' % self.r1))
        s = cd.status(self.project)
        self.assertEqual((s['result'], s['selected']['state']), ('OK', 'unverified'))

        class NoOwner(object):
            def load_owner(self):
                raise ImportError('pin mismatch')

        with mock.patch.object(cd, '_checks', lambda: (NoOwner(), None)):
            u = cd.status(self.project)
            self.assertEqual((u['result'], u['reason'], u['status']), ('UNAVAILABLE', 'OWNER_UNAVAILABLE', 'error'))
            o = cd.open_draft(self.project, self.r1, 'unverified')
            self.assertEqual(o['result'], 'UNAVAILABLE')
        self.assertEqual(self.opened, [])

    def test_a_context_owner_whose_bytes_do_not_match_the_policy_pin_is_refused_before_any_write(self):
        pv = cd.select_preview(self.project, self.r1)
        before = tree(self.project)
        with mock.patch.object(cd, 'CTX_REL', ('tools', 'publish_new.py')):
            self.assertEqual(cd.select_preview(self.project, self.r1)['reason'], 'CONTEXT_OWNER_PIN_MISMATCH')
            ap = cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint'])
            self.assertEqual((ap['result'], ap['reason']), ('UNAVAILABLE', 'CONTEXT_OWNER_PIN_MISMATCH'))
        self.assertEqual(tree(self.project), before)

    def test_p_ctx1_runs_the_hashed_bytes_with_the_pinned_p_cn1_module(self):
        env = cd.Env(self.project)
        ctx = env.ctx()
        self.assertIs(ctx._pn, env.pn)  # context_update used the pinned P-CN1 module, not whatever 'publish_new' was cached
        self.assertEqual(ctx.TARGETS, cu.TARGETS)
        self.assertIsNot(ctx, cu)
        self.assertIsNot(sys.modules.get('publish_new'), env.pn)  # and the swap was undone

    def test_read_paths_never_mutate_the_tree(self):
        self.select(self.r1)
        before = tree(self.project)
        cd.status(self.project)
        cd.list_candidates(self.project)
        cd.select_preview(self.project, self.r2)
        cd.select_preview(self.project, self.r1)
        cd.open_draft(self.project, self.r1)
        cd.open_draft(self.project, self.r2)
        cd.open_draft(self.project, rid_of(99))
        self.assertEqual(tree(self.project), before)

    def test_missing_or_too_old_jsonschema_refuses_every_api_without_mutation(self):
        pv, _ = self.select(self.r1)
        _, loader = cd._checks()
        before = tree(self.project)
        for target, kwargs in (('_import_jsonschema', {'side_effect': ImportError('not installed')}),
                               ('_jsonschema_version', {'return_value': (4, 17)})):
            with mock.patch.object(loader, target, **kwargs):
                results = [cd.status(self.project), cd.list_candidates(self.project), cd.select_preview(self.project, self.r2),
                           cd.select_apply(self.project, self.r1, pv['state_sha256'], pv['selection_fingerprint']),
                           cd.open_draft(self.project, self.r1, 'unverified')]
            self.assertTrue(all((r['result'], r['reason'], r['changes']) == ('UNAVAILABLE', 'DEPENDENCY_MISSING', False)
                                for r in results), results)
        self.assertEqual(self.opened, [])
        self.assertEqual(tree(self.project), before)

    def test_historical_owner_pin_mismatch_is_not_matched_or_selectable(self):
        self.select(self.r1)
        rel = '.agent/runtime/publish/%s.prepared.json' % self.r1
        prepared = json.loads(self.read(rel))
        prepared['entrypoint_sha256'] = 'sha256:' + 'b' * 64
        self.write(rel, pn.cj_dumps(prepared))
        before = tree(self.project)
        s = cd.status(self.project)
        self.assertEqual((s['selected']['state'], s['selected']['reason']), ('unverified', 'EVIDENCE_OWNER_PIN_MISMATCH'))
        self.assertEqual(cd.select_preview(self.project, self.r1)['reason'], 'EVIDENCE_OWNER_PIN_MISMATCH')
        self.assertEqual(cd.open_draft(self.project, self.r1)['result'], 'ACK_REQUIRED')
        self.assertEqual(cd.open_draft(self.project, self.r1, 'unverified')['result'], 'OPENED')
        self.assertEqual(tree(self.project), before)


class Opening(Base):
    def test_matched_opens_with_the_associated_app_once_and_only_that_path(self):
        self.select(self.r1)
        r = cd.open_draft(self.project, self.r1)
        self.assertEqual((r['result'], r['draft_state'], r['changes']), ('OPENED', 'matched', False))
        self.assertEqual(self.opened, [self.path('working/w-1/bao-cao-v1.docx')])

    def test_changed_needs_the_matching_acknowledgement_then_opens_with_a_warning_state(self):
        self.write('working/w-1/bao-cao-v2.docx', b'edited')
        r = cd.open_draft(self.project, self.r2)
        self.assertEqual((r['result'], r['draft_state']), ('ACK_REQUIRED', 'changed'))
        self.assertEqual(cd.open_draft(self.project, self.r2, 'unverified')['result'], 'ACK_REQUIRED')  # wrong acknowledgement
        self.assertEqual(self.opened, [])
        r = cd.open_draft(self.project, self.r2, 'changed')
        self.assertEqual((r['result'], r['draft_state']), ('OPENED', 'changed'))
        self.assertEqual(len(self.opened), 1)

    def test_every_click_looks_again_a_stale_ui_state_cannot_open_a_changed_file(self):
        self.select(self.r1)
        self.assertEqual(cd.open_draft(self.project, self.r1)['result'], 'OPENED')
        self.write('working/w-1/bao-cao-v1.docx', b'now different')
        r = cd.open_draft(self.project, self.r1)  # the UI may still believe 'matched'; no acknowledgement came
        self.assertEqual((r['result'], r['draft_state']), ('ACK_REQUIRED', 'changed'))
        self.assertEqual(len(self.opened), 1)

    def test_missing_evidence_with_a_safe_file_opens_only_after_acknowledgement(self):
        self.select(self.r1)
        os.remove(self.path('.agent/runtime/publish/%s.published.json' % self.r1))
        r = cd.open_draft(self.project, self.r1)
        self.assertEqual((r['result'], r['draft_state']), ('ACK_REQUIRED', 'unverified'))
        self.assertEqual(self.opened, [])
        self.assertEqual(cd.open_draft(self.project, self.r1, 'unverified')['result'], 'OPENED')

    def test_pointer_evidence_mismatch_opens_only_the_displayed_pointer_path_after_ack(self):
        self.select(self.r1)
        original = self.read(STATE_REL).decode('utf-8')
        for path, digest in (('working/w-1/bao-cao-v2.docx', pn._sha_bytes(self.read('working/w-1/bao-cao-v2.docx'))),
                             ('working/w-1/bao-cao-v1.docx', 'sha256:' + 'a' * 64)):
            tup = {'path': path, 'rid': self.r1, 'digest': digest}
            self.write(STATE_REL, cd.with_marker(pn, original, tup).encode('utf-8'))
            before = tree(self.project)
            s = cd.status(self.project)
            self.assertEqual((s['selected']['path'], s['selected']['state']), (path, 'unverified'))
            self.assertEqual(cd.open_draft(self.project, self.r1)['result'], 'ACK_REQUIRED')
            result = cd.open_draft(self.project, self.r1, 'unverified')
            self.assertEqual((result['result'], result['path'], self.opened[-1]), ('OPENED', path, self.path(path)))
            self.assertEqual(tree(self.project), before)

    def test_unknown_rid_without_evidence_or_pointer_is_refused(self):
        r = cd.open_draft(self.project, rid_of(77), 'unverified')
        self.assertEqual((r['result'], r['reason']), ('REFUSED', 'UNKNOWN_DRAFT'))
        self.assertEqual(self.opened, [])

    def test_missing_target_is_refused_even_with_acknowledgement(self):
        os.remove(self.path('working/w-1/bao-cao-v1.docx'))
        for ack in (None, 'changed', 'unverified'):
            r = cd.open_draft(self.project, self.r1, ack)
            self.assertEqual((r['result'], r['reason']), ('REFUSED', 'TARGET_MISSING'), ack)
        self.assertEqual(self.opened, [])

    def test_a_linked_parent_is_refused_and_the_generic_opener_is_not_called(self):
        real = self.path('working/w-1-real')
        os.rename(self.path('working/w-1'), real)
        self.junction(self.path('working/w-1'), real)
        for ack in (None, 'changed', 'unverified'):
            r = cd.open_draft(self.project, self.r1, ack)
            self.assertEqual(r['result'], 'REFUSED', (ack, r))
        self.assertEqual(self.opened, [])

    def test_a_target_that_is_a_folder_or_replaced_by_a_link_is_refused(self):
        target = self.path('working/w-1/bao-cao-v1.docx')
        os.remove(target)
        os.mkdir(target)
        r = cd.open_draft(self.project, self.r1, 'changed')
        self.assertEqual(r['result'], 'REFUSED')
        self.assertEqual(self.opened, [])

    def test_only_listed_extensions_can_be_opened_or_selected(self):
        for ext in ('.docx', '.xlsx', '.pptx', '.pdf', '.txt', '.md', '.csv', '.DOCX'):
            self.assertTrue(cd._ext_ok('working/a' + ext), ext)
        for ext in ('.exe', '.bat', '.cmd', '.lnk', '.html', '.htm', '.svg', '.docm', '.xlsm', '.pptm', '.js', '.ps1', '.docx.exe', ''):
            self.assertFalse(cd._ext_ok('working/a' + ext), ext)
        bad = publish(self.project, 40, 'w-9', 'working/w-9/nhung.html')
        self.assertEqual(cd.select_preview(self.project, bad)['reason'], 'PATH_NOT_SUPPORTED')
        self.assertEqual(cd.open_draft(self.project, bad, 'unverified')['result'], 'REFUSED')
        self.assertEqual(self.opened, [])
        self.assertNotIn(bad, [i['rid'] for i in cd.list_candidates(self.project)['items']])

    def test_output_zone_revisions_can_be_selected_and_opened(self):
        rid = publish(self.project, 41, 'w-3', 'output/w-3/ket-qua.xlsx')
        self.select(rid)
        self.assertEqual(cd.status(self.project)['selected']['state'], 'matched')
        self.assertEqual(cd.open_draft(self.project, rid)['result'], 'OPENED')
        self.assertEqual(self.opened, [self.path('output/w-3/ket-qua.xlsx')])


class OwnersUnchanged(unittest.TestCase):
    def test_accepted_owner_bytes_are_unchanged(self):
        for rel, want in OWNER_PINS.items():
            with self.subTest(rel):
                self.assertEqual(sha((ROOT / rel).read_bytes())[:16], want, rel)

    def test_the_policy_pin_of_p_ctx1_still_matches_its_owner(self):
        policy = json.loads((ROOT / '.cvf/rules/v3/ROUTING_POLICY.json').read_text(encoding='utf-8'))
        self.assertEqual(policy['operational_context_protocol']['entrypoint_sha256'], 'sha256:' + sha((ROOT / 'tools/context_update.py').read_bytes()))
        self.assertEqual(policy['owner_protocols'][0]['entrypoint_sha256'], 'sha256:' + sha((ROOT / 'tools/publish_new.py').read_bytes()))

    def test_the_helper_imports_neither_owner_directly(self):
        text = (ROOT / 'tools' / 'current_draft.py').read_text(encoding='utf-8')
        self.assertNotRegex(text, r'(?m)^\s*(import|from)\s+(publish_new|context_update)\b')
        self.assertNotIn('operations', text.replace('operations.jsonl', ''))  # no ops-log writer: the history file is not touched


@NEED
class Cli(Base):
    def run_cli(self, *args, env=None):
        e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        e.pop(tx.FAULT_ENV, None)
        e.update(env or {})
        cmd = [sys.executable, '-I', str(ROOT / 'tools' / 'current_draft.py'), args[0], '--project', self.project] + list(args[1:]) + ['--result-json']
        r = subprocess.run(cmd, cwd=str(ROOT), env=e, capture_output=True, encoding='utf-8', timeout=120)
        return r.returncode, result_schema.split_output(r.stdout)[1], r

    def test_status_list_select_preview_apply_open(self):
        code, env, _ = self.run_cli('status')
        self.assertEqual((code, env['pointer']['state']), (0, 'NONE'))
        code, env, _ = self.run_cli('list')
        self.assertEqual((code, len(env['items'])), (0, 3))
        before = tree(self.project)
        code, pv, _ = self.run_cli('select', '--rid', self.r1)
        self.assertEqual((code, pv['result'], pv['changes']), (0, 'PREVIEW', False))
        self.assertEqual(tree(self.project), before)  # preview is the default
        code, ap, _ = self.run_cli('select', '--rid', self.r1, '--apply', '--expected-state', 'sha256:' + pv['state_sha256'],
                                   '--expected-selection', pv['selection_fingerprint'])
        self.assertEqual((code, ap['result'], ap['changes']), (0, 'WRITTEN', True))
        log = os.path.join(self.tmp + '-open.log')
        self.addCleanup(lambda: os.path.exists(log) and os.remove(log))
        code, op, _ = self.run_cli('open', '--rid', self.r1, env={cd.OPEN_LOG_ENV: log})
        self.assertEqual((code, op['result']), (0, 'OPENED'))
        with open(log, encoding='utf-8') as f:
            self.assertEqual(f.read().strip(), self.path('working/w-1/bao-cao-v1.docx'))

    def test_apply_without_rid_or_expected_hashes_is_a_usage_error_and_writes_nothing(self):
        before = tree(self.project)
        for args in (['select', '--apply'], ['select', '--rid', self.r1, '--apply'], ['select', '--rid', self.r1, '--apply', '--expected-state', 'a' * 64],
                     ['open'], ['status', '--bogus']):
            code, _, r = self.run_cli(*args)
            self.assertEqual(code, 2, (args, r.stderr))
        self.assertEqual(tree(self.project), before)

    def test_conflict_and_refusal_exit_codes(self):
        code, pv, _ = self.run_cli('select', '--rid', self.r1)
        code, ap, _ = self.run_cli('select', '--rid', self.r1, '--apply', '--expected-state', pv['state_sha256'], '--expected-selection', '0' * 64)
        self.assertEqual((code, ap['result']), (3, 'CONFLICT'))
        code, op, _ = self.run_cli('open', '--rid', rid_of(99))
        self.assertEqual((code, op['result']), (4, 'REFUSED'))


@NEED
class Routes(unittest.TestCase):
    """The panel's dedicated routes over HTTP: token and Host checks, no operations log, no generic run path."""

    @classmethod
    def setUpClass(cls):
        import test_ui_browser as ub
        cls.ub = ub
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-i2-routes-')
        cls.pkg = ub.copy_package(Path(cls.tmp.name) / 'package')
        for rel in ('.agent/runtime',):
            os.makedirs(str(cls.pkg / rel))
        make_project_files(str(cls.pkg))
        cls.r1 = publish(str(cls.pkg), 1, 'w-1', 'working/w-1/bao-cao-v1.docx')
        cls.r2 = publish(str(cls.pkg), 2, 'w-1', 'working/w-1/bao-cao-v2.docx')
        cls.panel = ub.Panel(cls.pkg, cls.tmp.name)
        cls.panel.env = {cd.OPEN_LOG_ENV: os.path.join(cls.tmp.name, 'open.log')}
        cls.panel.start()

    @classmethod
    def tearDownClass(cls):
        cls.panel.stop()
        cls.tmp.cleanup()

    def post(self, path, body=None, token=True, host=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-Panel-Token'] = self.panel.token
        if host:
            headers['Host'] = host
        req = urllib.request.Request(self.panel.base + path, data=json.dumps(body or {}).encode('utf-8'), method='POST', headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode('utf-8') or '{}')

    def test_routes_need_the_token_and_a_local_host(self):
        for path in ('/api/draft/status', '/api/draft/list', '/api/draft/select', '/api/draft/open'):
            self.assertEqual(self.post(path, {}, token=False)[0], 403, path)
            self.assertEqual(self.post(path, {}, host='evil.example')[0], 403, path)
        req = urllib.request.Request(self.panel.base + '/api/draft/status', method='GET')
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=30)
        self.assertEqual(cm.exception.code, 404)

    def test_select_then_status_open_and_the_operations_log_stays_untouched(self):
        log = self.pkg / '.agent' / 'runtime' / 'operations.jsonl'
        self.assertFalse(log.exists())
        code, st = self.post('/api/draft/status')
        self.assertEqual((code, st['result'], st['pointer']['state']), (200, 'OK', 'NONE'))
        code, pv = self.post('/api/draft/select', {'rid': self.r1})
        self.assertEqual((code, pv['result']), (200, 'PREVIEW'))
        code, ap = self.post('/api/draft/select', {'rid': self.r1, 'apply': True, 'expected_state': pv['state_sha256'], 'expected_selection': pv['selection_fingerprint']})
        self.assertEqual((code, ap['result']), (200, 'WRITTEN'))
        code, st = self.post('/api/draft/status')
        self.assertEqual((st['selected']['rid'], st['selected']['state'], [h['rid'] for h in st['history']]), (self.r1, 'matched', [self.r2]))
        code, op = self.post('/api/draft/open', {'rid': self.r1})
        self.assertEqual(op['result'], 'OPENED')
        self.assertEqual(self.post('/api/draft/open', {'rid': self.r1, 'ack': 'nonsense'})[1]['reason'], 'ACK_INVALID')
        self.assertEqual(self.post('/api/draft/select', {'rid': 5})[1]['reason'], 'RID_INVALID')
        self.assertFalse(log.exists())  # draft routes are outside run_api/_record

    def test_the_generic_run_route_has_no_draft_action(self):
        code, r = self.post('/api/run', {'action': 'draft_select', 'params': {'rid': self.r1}})
        self.assertEqual(r['code'], 2)
        self.assertTrue(r.get('input_error'))


def make_project_files(root):
    os.makedirs(os.path.join(root, 'references', 'source-documents'), exist_ok=True)
    with open(os.path.join(root, 'references', 'source-documents', 'quy-che.pdf'), 'wb') as f:
        f.write(b'%PDF fake source')
    with open(os.path.join(root, STATE_REL), 'wb') as f:
        f.write(state_text().encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
