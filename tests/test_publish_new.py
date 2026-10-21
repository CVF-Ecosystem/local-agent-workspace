"""P-CN1-I writer checks (tools/publish_new.py). Every write stays in a fresh temporary project with fake data.

Checker/eligibility branches of contract 4.3.3 C-4 (grant, route, entrypoint pin, D4) are not implemented by the tool and are
deferred to A0; nothing here evaluates them.
"""
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import publish_new as pn  # noqa: E402
import result_schema  # noqa: E402

WINDOWS = os.name == 'nt'
VECTORS = ROOT / '.cvf' / 'contracts' / 'v2' / 'vectors.json'


def att():
    return {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:msg/0012',
            'recorded_by': {'actor_id': 'main', 'role': 'main'}}


class Base(unittest.TestCase):
    bootstrap = True  # the fixture creates `.agent/runtime` itself: publish no longer creates these two parents (T2 precondition)

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='law-pcn1-')
        self.addCleanup(self._cleanup)
        self.project = self.tmp
        self.junctions = []
        if self.bootstrap:
            os.makedirs(os.path.join(self.project, '.agent', 'runtime'))
        src = os.path.join(self.project, 'references', 'source-documents', 'team')
        os.makedirs(src)
        self.source = os.path.join(src, 'quy-che-gia.pdf')
        with open(self.source, 'wb') as f:
            f.write(b'%PDF fake source bytes')
        self.source_digest = pn._sha_bytes(b'%PDF fake source bytes')
        self.staged = b'PK fake docx draft bytes ' * 100

    def _cleanup(self):
        for j in self.junctions:
            try:
                os.rmdir(j)  # remove the junction itself, never its target's content
            except OSError:
                pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def request(self, **over):
        r = {'work_id': 'w-20261018-01', 'target': 'working/w-20261018-01/bao-cao-nhap.docx',
             'intent_ref': {'ref_id': 'intent-1', 'locator': 'host:msg/0012', 'digest': 'sha256:' + '5' * 64, 'attribution': att()},
             'main_interpretation': 'Báo cáo ngắn về mục giá',
             'requirements': [{'req_id': 'REQ-1', 'statement': 'Tóm tắt mục giá', 'mandatory': True},
                              {'req_id': 'REQ-2', 'statement': 'Nêu điểm chưa chắc', 'mandatory': True}],
             'grant_refs': [{'ref_id': 'grant-1', 'locator': 'PROJECT.md#pham-vi', 'digest': 'sha256:' + '1' * 64, 'attribution': att()}],
             'subject': {'actor_id': 'main', 'role': 'main'},
             'inputs': [{'path': 'references/source-documents/team/quy-che-gia.pdf', 'digest': self.source_digest}]}
        r.update(over)
        return r

    def pub_dir(self):
        return os.path.join(self.project, '.agent', 'runtime', 'publish')

    def ev(self, rid, state):
        return pn._evidence_path(self.project, rid, state)

    def target(self, rel='working/w-20261018-01/bao-cao-nhap.docx'):
        return os.path.join(self.project, *rel.split('/'))

    def read(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def junction(self, link, target):
        os.makedirs(target, exist_ok=True)
        r = subprocess.run(['cmd', '/c', 'mklink', '/J', link, target], capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest('cannot create a junction here: ' + r.stdout + r.stderr)
        self.junctions.append(link)

    def cli(self, *args, fault=None, json_result=True):
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        env.pop(pn.FAULT_ENV, None)
        if fault:
            env[pn.FAULT_ENV] = fault
        cmd = [sys.executable, '-I', str(ROOT / 'tools' / 'publish_new.py')] + list(args) + ['--project', self.project]
        if json_result:
            cmd.append('--result-json')
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env, timeout=60)

    def cli_publish(self, request=None, staged=None, fault=None, rid=None):
        req = os.path.join(self.tmp, 'req.json')
        st = os.path.join(self.tmp, 'staged.bin')
        with open(req, 'wb') as f:
            f.write(pn.cj_dumps(request or self.request()))
        with open(st, 'wb') as f:
            f.write(self.staged if staged is None else staged)
        extra = ['--rid', rid] if rid is not None else []
        return self.cli('publish', '--request', req, '--staged', st, *extra, fault=fault)

    def tree(self):
        out = []
        for base, dirs, files in os.walk(self.project):
            out.extend(os.path.relpath(os.path.join(base, n), self.project) for n in dirs + files)
        return sorted(out)

    def only_rid(self):
        names = {n.split('.')[0] for n in os.listdir(self.pub_dir())}
        self.assertEqual(len(names), 1, names)
        return names.pop()


class Canonical(unittest.TestCase):
    """LAW-CJ/2 private serializer against the v2 vectors (valid and UNSUPPORTED), without changing them."""

    def test_v2_canonical_vectors(self):
        data = json.loads(VECTORS.read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(data['canonical']), 20)
        for vec in data['canonical']:
            exp = vec['expected']
            with self.subTest(vec['id']):
                if exp['status'] == 'OK':
                    value = pn.cj_loads(vec['input_json'])
                    self.assertEqual(pn.cj_dumps(value).decode('utf-8'), exp['canonical_utf8'])
                    self.assertEqual(pn.cj_digest(value), exp['digest'])
                else:
                    with self.assertRaises(pn.CJError) as ctx:
                        pn.cj_dumps(pn.cj_loads(vec['input_json']))
                    self.assertEqual(ctx.exception.reason, exp['reason'])

    def test_wire_must_be_canonical_raw_bytes(self):
        obj = {'b': 1, 'a': 'x'}
        self.assertEqual(pn.cj_dumps(obj), b'{"a":"x","b":1}')
        self.assertEqual(pn.cj_loads(b'{ "b": 1, "a": "x" }'), obj, 'parse accepts it ...')
        self.assertNotEqual(pn.cj_dumps(pn.cj_loads(b'{ "b": 1, "a": "x" }')), b'{ "b": 1, "a": "x" }', '... but it is not wire')
        with self.assertRaises(pn.CJError):
            pn.cj_loads(b'\xef\xbb\xbf{}')

    def test_identity_is_hex_and_never_an_out_of_range_integer(self):
        top = 2 ** 64 - 1
        info = {'attributes': 0x20, 'nlink': 2, 'size': 1, 'volume_serial': '%08x' % 0xFFFFFFFF, 'file_index': '%016x' % top,
                'index_value': top}
        ident = pn.identity_of(info)
        self.assertEqual(ident, {'volume_serial': 'ffffffff', 'file_index': 'ffffffffffffffff'})
        self.assertEqual(int(ident['file_index'], 16), top, 'round trip keeps all 64 bits')
        self.assertTrue(pn._identity_ok(ident))
        self.assertIsNone(pn.identity_of(dict(info, index_value=0, file_index='0' * 16)), 'no identity is never comparable')
        self.assertIsNone(pn.identity_of(None))
        with self.assertRaises(pn.CJError):
            pn.cj_dumps({'file_index': 2 ** 53})
        pn.cj_dumps({'file_index': 2 ** 53 - 1})


class PortablePlatformRefusal(Base):
    def test_mutating_apis_refuse_unsupported_platform_before_native_root_adapter(self):
        request = self.request()
        with mock.patch.object(pn.os, 'name', 'posix'), \
                mock.patch.object(pn, '_root_problem', side_effect=AssertionError('native root adapter must not run')):
            results = [pn.publish(self.project, request, self.staged),
                       pn.recover(self.project, '0' * 32),
                       pn.discard_staged(self.project, '0' * 32)]
        for result in results:
            self.assertEqual((result['outcome'], result['reason'], result['wrote']),
                             ('REFUSED', 'UNSUPPORTED_FS', []))
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent', 'runtime', 'publish')))


@unittest.skipIf(WINDOWS, 'non-Windows refusal')
class NotWindows(Base):
    def test_refused_before_any_write(self):
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'UNSUPPORTED_FS', []))
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent', 'runtime', 'publish')))


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class Publish(Base):
    # ---- P-01
    def test_happy_path_writes_canonical_evidence_and_the_exact_bytes(self):
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('PUBLISHED', None))
        rid = res['request_id']
        self.assertRegex(rid, r'^[0-9a-f]{32}$')
        self.assertEqual(self.read(self.target()), self.staged)
        self.assertFalse(os.path.exists(self.ev(rid, 'staged')), 'T7 removed the staged name')
        self.assertEqual([(w['envelope'], w['op']) for w in res['wrote']],
                         [('T2', 'mkdir'), ('T3', 'create'), ('T4', 'create'),
                          ('T1', 'mkdir'), ('T1', 'mkdir'), ('T5', 'link'), ('T6', 'create'), ('T7', 'delete')])
        self.assertIn(res['protection'], ('held', 'recheck_only'))
        raw = self.read(self.ev(rid, 'prepared'))
        prepared = pn.validate_evidence(raw, rid, 'prepared')
        self.assertIsNotNone(prepared)
        self.assertEqual(pn.cj_dumps(prepared), raw)
        task = prepared['task']
        self.assertEqual(task['task_id'], 'pcn1-' + rid)
        self.assertEqual(task['schema_version'], 'law.cvf.control/3')
        self.assertEqual(task['effects']['actions'], [{'operation': 'create_new', 'tool': 'publish_new',
                                                        'targets': ['working/w-20261018-01/bao-cao-nhap.docx'], 'write_zone': 'working'}])
        self.assertEqual(task['intent']['refs'][0]['kind'], 'user_intent')
        self.assertEqual(task['authority']['grant_refs'][0]['kind'], 'grant')
        self.assertEqual(prepared['inputs_observed_at_publish'], [{'path': 'references/source-documents/team/quy-che-gia.pdf',
                                                                     'digest': self.source_digest}])
        published = pn.validate_evidence(self.read(self.ev(rid, 'published')), rid, 'published')
        self.assertEqual(published['content'], {'sha256': pn._sha_bytes(self.staged), 'size': len(self.staged)})
        self.assertEqual(published['identity'], pn.identity_of(pn.file_info(self.target())))
        self.assertEqual(published['nlink_at_check'], 2)
        self.assertFalse(published['recovered'])
        self.assertEqual(self.read(self.source), b'%PDF fake source bytes', 'the source is only read')
        st = pn.status(self.project, rid)['items'][0]
        self.assertEqual((st['terminal'], st['consistent'], st['staged_present']), ('published', True, False))
        ob = pn.observe(self.project, request_id=rid, inputs=['references/source-documents/team/quy-che-gia.pdf'])
        self.assertEqual(ob['outcome'], 'OBSERVED')
        self.assertTrue(ob['target']['matches_published'])
        self.assertEqual(ob['inputs'][0]['sha256'], self.source_digest)
        self.assertEqual(ob['wrote'], [])

    def test_output_needs_internal_draft_and_sets_are_canonical(self):
        req = self.request(target='output/bao-cao.docx', content_use=['internal_draft'],
                           inputs=[{'path': 'references/source-documents/team/quy-che-gia.pdf', 'digest': self.source_digest}])
        res = pn.publish(self.project, req, self.staged)
        self.assertEqual(res['outcome'], 'PUBLISHED')
        task = pn.validate_evidence(self.read(self.ev(res['request_id'], 'prepared')), res['request_id'], 'prepared')['task']
        self.assertEqual(task['effects']['actions'][0]['write_zone'], 'output_new')
        self.assertEqual(task['effects']['actions'][0]['content_use'], ['internal_draft'])
        self.assertEqual(pn.publish(self.project, self.request(target='output/b.docx'), self.staged)['reason'], 'SNAPSHOT_INCOMPLETE')
        self.assertEqual(pn.publish(self.project, self.request(target='output/c.docx', content_use=['sign']), self.staged)['reason'],
                         'CONTENT_USE_NOT_INTERNAL')
        two = [{'ref_id': 'grant-2', 'locator': 'b', 'digest': 'sha256:' + '2' * 64, 'attribution': att()},
               {'ref_id': 'grant-1', 'locator': 'a', 'digest': 'sha256:' + '1' * 64, 'attribution': att()}]
        res = pn.publish(self.project, self.request(target='working/w/d.docx', grant_refs=two), self.staged)
        grants = pn.validate_evidence(self.read(self.ev(res['request_id'], 'prepared')), res['request_id'], 'prepared')['task']['authority']['grant_refs']
        self.assertEqual([g['ref_id'] for g in grants], ['grant-1', 'grant-2'], 'set sorted by canonical bytes')

    # ---- P-03 / P-04 and case-only names
    def test_existing_target_is_kept_and_conflict_recorded(self):
        os.makedirs(os.path.dirname(self.target()))
        with open(self.target(), 'wb') as f:
            f.write(b'user file')
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('CONFLICT', 'TARGET_EXISTS'))
        self.assertEqual(self.read(self.target()), b'user file')
        rid = res['request_id']
        self.assertIsNotNone(pn.validate_evidence(self.read(self.ev(rid, 'conflict')), rid, 'conflict'))
        self.assertTrue(os.path.exists(self.ev(rid, 'staged')), 'failed staged is kept until discard-staged')
        self.assertEqual(pn.discard_staged(self.project, rid)['outcome'], 'DISCARDED')
        again = pn.discard_staged(self.project, rid)
        self.assertEqual((again['outcome'], again['reason'], again['wrote']), ('REFUSED', 'STAGED_ABSENT', []))

    def test_case_only_difference_is_a_conflict(self):
        os.makedirs(os.path.dirname(self.target()))
        upper = self.target('working/w-20261018-01/BAO-CAO-NHAP.DOCX')
        with open(upper, 'wb') as f:
            f.write(b'user file')
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(res['outcome'], 'CONFLICT')
        self.assertEqual(self.read(upper), b'user file')

    def test_two_requests_racing_for_one_target(self):
        results = {}

        def hook(point, info):
            if point == 'before_link' and 'second' not in results:
                pn._HOOK = None
                results['second'] = pn.publish(self.project, self.request(), b'second writer bytes')
                pn._HOOK = hook
        pn._HOOK = hook
        self.addCleanup(setattr, pn, '_HOOK', None)
        first = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(results['second']['outcome'], 'PUBLISHED')
        self.assertEqual(first['outcome'], 'CONFLICT')
        self.assertEqual(self.read(self.target()), b'second writer bytes', 'the loser never replaced the winner')

    # ---- P-05 path, zone, authority, parents, runtime
    def test_refused_forms_write_nothing(self):
        cases = {'../x.docx': 'PATH_UNSUPPORTED_FORM', 'C:/x.docx': 'PATH_UNSUPPORTED_FORM', 'working/a:b.docx': 'PATH_UNSUPPORTED_FORM',
                 'working/x.': 'PATH_UNSUPPORTED_FORM', 'working/x ': 'PATH_UNSUPPORTED_FORM', 'working/PROGRA~1/x.docx': 'PATH_UNSUPPORTED_FORM',
                 'working/con.txt': 'PATH_UNSUPPORTED_FORM', 'working\\x.docx': 'PATH_UNSUPPORTED_FORM', '/working/x.docx': 'PATH_UNSUPPORTED_FORM',
                 'working//x.docx': 'PATH_UNSUPPORTED_FORM', 'references/x.docx': 'ZONE_NOT_LIGHT', 'working': 'ZONE_NOT_LIGHT',
                 'x.docx': 'ZONE_NOT_LIGHT', 'working/w/AGENTS.md': 'AUTHORITY_NAME', 'working/w/ROUTING_POLICY.json': 'AUTHORITY_NAME',
                 'output/a.schema.json': 'AUTHORITY_NAME', 'working/w/e\u0301.docx': 'REQUEST_INVALID'}
        for target, reason in cases.items():
            with self.subTest(target):
                res = pn.publish(self.project, self.request(target=target), self.staged)
                self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', reason, []))
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent', 'runtime', 'publish')))

    def test_junction_parent_and_runtime_are_refused_before_writing(self):
        outside = os.path.join(self.tmp, 'outside')
        os.makedirs(os.path.join(self.project, 'working'))
        self.junction(os.path.join(self.project, 'working', 'w-20261018-01'), outside)
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'PARENT_UNSAFE', []))
        self.assertEqual(os.listdir(outside), [])
        self.assertEqual(pn.observe(self.project, target='working/w-20261018-01/bao-cao-nhap.docx')['reason'], 'PARENT_UNSAFE')
        os.rmdir(os.path.join(self.project, '.agent', 'runtime'))  # replace the fixture's plain folder with a junction
        self.junction(os.path.join(self.project, '.agent', 'runtime'), os.path.join(self.tmp, 'rt-outside'))
        res = pn.publish(self.project, self.request(target='working/w2/a.docx'), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RUNTIME_LINKED', []))
        self.assertEqual(os.listdir(os.path.join(self.tmp, 'rt-outside')), [])

    def test_unsupported_volume_writes_nothing(self):
        with mock.patch.object(pn, 'volume_supported', return_value=(False, {'fs': 'FAT32', 'local': True})):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'UNSUPPORTED_FS', []))

    # ---- P-07, P-08, P-22, P-23
    def test_request_shape(self):
        bad = {'extra_review_phases': ['PRE_DELIVERY'], 'protected_targets': [], 'context_refs': [], 'completion': 'REQUIRED',
               'task_id': 'x'}
        for k, v in bad.items():
            with self.subTest(k):
                self.assertEqual(pn.publish(self.project, self.request(**{k: v}), self.staged)['reason'], 'REQUEST_INVALID')
        r = self.request()
        r['intent_ref'] = dict(r['intent_ref'], kind='user_intent')
        self.assertEqual(pn.publish(self.project, r, self.staged)['reason'], 'REQUEST_INVALID', 'kind is set by the tool')
        self.assertEqual(pn.publish(self.project, self.request(content_use=['internal_draft']), self.staged)['reason'], 'REQUEST_INVALID')
        self.assertEqual(pn.publish(self.project, self.request(main_interpretation='e\u0301'), self.staged)['reason'], 'REQUEST_INVALID')
        dup = [{'path': 'references/source-documents/team/quy-che-gia.pdf', 'digest': self.source_digest}] * 2
        self.assertEqual(pn.publish(self.project, self.request(inputs=dup), self.staged)['reason'], 'REQUEST_INVALID')
        r = self.request()
        del r['intent_ref']
        self.assertEqual(pn.publish(self.project, r, self.staged)['reason'], 'SNAPSHOT_INCOMPLETE')
        self.assertEqual(pn.publish(self.project, self.request(grant_refs=[]), self.staged)['reason'], 'SNAPSHOT_INCOMPLETE')
        opt = [{'req_id': 'REQ-1', 'statement': 's', 'mandatory': False}]
        self.assertEqual(pn.publish(self.project, self.request(requirements=opt), self.staged)['reason'], 'SNAPSHOT_INCOMPLETE')
        self.assertEqual(pn.publish(self.project, 'not a dict', self.staged)['reason'], 'REQUEST_INVALID')
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent', 'runtime', 'publish')))

    def test_changed_or_missing_source_is_refused(self):
        with open(self.source, 'ab') as f:
            f.write(b' edited')
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'INPUT_CHANGED_SINCE_READ', []))
        os.remove(self.source)
        self.assertEqual(pn.publish(self.project, self.request(), self.staged)['reason'], 'INPUT_CHANGED_SINCE_READ')

    def test_size_limits(self):
        with mock.patch.object(pn, 'MAX_STAGED_BYTES', 10):
            self.assertEqual(pn.publish(self.project, self.request(), self.staged)['reason'], 'STAGED_TOO_LARGE')
        big = self.request(main_interpretation='x' * (pn.MAX_JSON_BYTES + 1))
        res = pn.publish(self.project, big, self.staged)
        self.assertEqual((res['reason'], res['wrote']), ('SNAPSHOT_TOO_LARGE', []))

    # ---- P-17, P-29, P-30: failures after bootstrap report what they wrote
    def fault(self, point):
        return mock.patch.dict(os.environ, {pn.FAULT_ENV: 'pcn1-fail:' + point})

    def test_bootstrap_then_lock_or_prepared_write_failure_reports_writes(self):
        with mock.patch.object(pn, '_lock', side_effect=OSError(5, 'boom')):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('REFUSED', 'LOCK_UNAVAILABLE'))
        self.assertEqual([w['envelope'] for w in res['wrote']], ['T2', 'T3'], 'not "nothing written"')
        with self.fault('prepared_write'):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('REFUSED', 'EVIDENCE_WRITE_FAILED'))
        self.assertEqual([w['envelope'] for w in res['wrote']], ['T3'])
        self.assertFalse(os.path.exists(self.target()))

    def test_stage_failure_abandons(self):
        with self.fault('stage_write'):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('ABANDONED', 'STAGE_FAILED'))
        self.assertFalse(os.path.exists(self.target()))
        self.assertIsNotNone(pn.validate_evidence(self.read(self.ev(res['request_id'], 'abandoned')), res['request_id'], 'abandoned'))

    def test_terminal_write_failure_is_unknown_and_not_hidden(self):
        os.makedirs(os.path.dirname(self.target()))
        with open(self.target(), 'wb') as f:
            f.write(b'user file')
        with self.fault('terminal_write'):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('UNKNOWN', 'EVIDENCE_WRITE_FAILED'))
        rid = res['request_id']
        self.assertEqual(self.read(self.ev(rid, 'conflict')), b'', 'the broken terminal stays as it is')
        self.assertEqual(pn.recover(self.project, rid)['reason'], 'EVIDENCE_INCONSISTENT')
        self.assertEqual(self.read(self.target()), b'user file')

    def test_published_write_failure_is_pending_and_stays_blocked(self):
        with self.fault('published_write'):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('PUBLISHED_EVIDENCE_PENDING', 'PUBLISHED_WRITE_FAILED'))
        rid = res['request_id']
        self.assertEqual(self.read(self.target()), self.staged)
        self.assertTrue(os.path.exists(self.ev(rid, 'staged')))
        rec = pn.recover(self.project, rid)
        self.assertEqual((rec['outcome'], rec['reason'], rec['wrote']), ('UNKNOWN', 'EVIDENCE_INCONSISTENT', []),
                         'an empty published.json is a terminal filename: no rewrite, no second terminal')
        self.assertFalse(pn.status(self.project, rid)['items'][0]['consistent'])

    def test_cleanup_failure_keeps_proof_and_recover_cleans_only_the_right_file(self):
        with self.fault('cleanup'):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['cleanup_pending']), ('PUBLISHED', 'STAGED_CLEANUP_PENDING', True))
        self.assertNotIn('T7', [w['envelope'] for w in res['wrote']])
        rid = res['request_id']
        self.assertTrue(pn.status(self.project, rid)['items'][0]['cleanup_pending'])
        # a different file under the staged name is never deleted
        os.remove(self.ev(rid, 'staged'))
        with open(self.ev(rid, 'staged'), 'wb') as f:
            f.write(self.staged)
        rec = pn.recover(self.project, rid)
        self.assertEqual((rec['outcome'], rec['reason'], rec['wrote']), ('NO_ACTION', 'STAGED_CLEANUP_PENDING', []))
        self.assertTrue(os.path.exists(self.ev(rid, 'staged')))
        self.assertEqual(self.read(self.target()), self.staged)
        self.assertEqual(pn.discard_staged(self.project, rid)['reason'], 'TERMINAL_IS_PUBLISHED')

    # ---- P-14, P-21: serialization of one rid
    def test_recover_that_comes_before_the_publisher_takes_the_rid(self):
        seen = {}

        def hook(point, info):
            if point == 'after_bootstrap':
                seen['recover'] = pn.recover(info['project'], info['rid'])
        pn._HOOK = hook
        self.addCleanup(setattr, pn, '_HOOK', None)
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((seen['recover']['outcome'], seen['recover']['reason']), ('UNKNOWN', 'PREPARED_UNREADABLE'))
        self.assertEqual((res['outcome'], res['reason']), ('REFUSED', 'RID_TAKEN'))
        self.assertEqual([w['envelope'] for w in res['wrote']], ['T2', 'T3'])
        self.assertFalse(os.path.exists(self.target()))
        self.assertFalse(os.path.exists(self.ev(res['request_id'], 'staged')))

    def test_recover_and_discard_are_busy_while_another_process_holds_the_rid(self):
        seen = {}

        def hook(point, info):
            if point == 'before_link':
                for cmd in ('recover', 'discard-staged'):
                    r = self.cli(cmd, info['rid'])
                    seen[cmd] = (r.returncode, result_schema.split_output(r.stdout)[1])
        pn._HOOK = hook
        self.addCleanup(setattr, pn, '_HOOK', None)
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(res['outcome'], 'PUBLISHED')
        for cmd in ('recover', 'discard-staged'):
            code, env = seen[cmd]
            self.assertEqual((code, env['outcome'], env['changes']), (6, 'BUSY', False), cmd)

    def test_two_recovers_of_one_rid(self):
        r = self.cli_publish(fault='pcn1-kill:after_link')
        self.assertEqual(r.returncode, 70)
        rid = self.only_rid()
        holder = subprocess.Popen([sys.executable, '-I', '-c', (
            'import os,msvcrt,time\nfd=os.open(%r, os.O_RDWR|os.O_BINARY)\nos.lseek(fd,%d,0)\n'
            'msvcrt.locking(fd,msvcrt.LK_NBLCK,1)\nprint("L",flush=True)\ntime.sleep(5)') % (self.ev(rid, 'prepared'), pn.LOCK_OFFSET)],
            stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.stdout.close)
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), 'L')
        busy = pn.recover(self.project, rid)
        self.assertEqual((busy['outcome'], busy['reason'], busy['wrote']), ('BUSY', 'LOCK_BUSY', []))
        holder.kill()
        holder.wait()
        self.assertEqual(pn.recover(self.project, rid)['outcome'], 'PUBLISHED')
        self.assertEqual(pn.recover(self.project, rid)['outcome'], 'NO_ACTION')


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class Crash(Base):
    """Real process kills (os._exit) at protocol points, then manual recover."""

    def killed(self, point):
        r = self.cli_publish(fault='pcn1-kill:' + point)
        self.assertEqual(r.returncode, 70, r.stdout + r.stderr)
        return self.only_rid()

    def test_kill_after_prepared(self):
        rid = self.killed('after_prepared')
        res = pn.recover(self.project, rid)
        self.assertEqual((res['outcome'], res['reason']), ('UNKNOWN', 'STAGED_ABSENT'))
        self.assertEqual(pn.validate_evidence(self.read(self.ev(rid, 'unknown')), rid, 'unknown')['by'], 'recover')

    def test_kill_before_link_never_claims_not_published(self):
        rid = self.killed('after_stage')
        self.assertEqual(pn.discard_staged(self.project, rid)['reason'], 'NO_TERMINAL')
        res = pn.recover(self.project, rid)
        self.assertEqual((res['outcome'], res['reason']), ('UNKNOWN', 'TARGET_ABSENT'))
        self.assertEqual(pn.discard_staged(self.project, rid)['outcome'], 'DISCARDED')
        self.assertEqual(pn.discard_staged(self.project, rid)['reason'], 'STAGED_ABSENT')

    def test_kill_after_link_is_recovered_by_identity_and_bytes(self):
        for point in ('after_link', 'after_verify'):
            with self.subTest(point):
                shutil.rmtree(os.path.join(self.project, '.agent', 'runtime', 'publish'), ignore_errors=True)
                shutil.rmtree(os.path.join(self.project, 'working'), ignore_errors=True)
                rid = self.killed(point)
                res = pn.recover(self.project, rid)
                self.assertEqual((res['outcome'], res['reason'], res['recovered']), ('PUBLISHED', None, True))
                self.assertEqual([w['envelope'] for w in res['wrote']], ['T6', 'T7'])
                pub = pn.validate_evidence(self.read(self.ev(rid, 'published')), rid, 'published')
                self.assertTrue(pub['recovered'])
                self.assertEqual(self.read(self.target()), self.staged)

    def test_in_place_edit_before_recover_is_unknown(self):
        rid = self.killed('after_link')
        with open(self.target(), 'r+b') as f:
            f.write(b'EDITED')
        res = pn.recover(self.project, rid)
        self.assertEqual((res['outcome'], res['reason']), ('UNKNOWN', 'TARGET_MODIFIED'))

    def test_replaced_target_with_same_bytes_is_unknown(self):
        rid = self.killed('after_link')
        os.remove(self.target())
        with open(self.target(), 'wb') as f:
            f.write(self.staged)
        res = pn.recover(self.project, rid)
        self.assertEqual((res['outcome'], res['reason']), ('UNKNOWN', 'IDENTITY_MISMATCH'))
        self.assertEqual(self.read(self.target()), self.staged, 'the target is not touched')

    def test_kill_after_published_leaves_cleanup_to_recover(self):
        rid = self.killed('after_published')
        st = pn.status(self.project, rid)['items'][0]
        self.assertEqual((st['terminal'], st['consistent'], st['cleanup_pending']), ('published', True, True))
        res = pn.recover(self.project, rid)
        self.assertEqual((res['outcome'], [w['envelope'] for w in res['wrote']]), ('NO_ACTION', ['T7']))
        self.assertFalse(os.path.exists(self.ev(rid, 'staged')))


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class Evidence(Base):
    def test_snapshot_shape_is_exact_before_recover_or_discard(self):
        os.makedirs(os.path.dirname(self.target()))
        with open(self.target(), 'wb') as f:
            f.write(b'user file')
        rid = pn.publish(self.project, self.request(), self.staged)['request_id']
        path = self.ev(rid, 'prepared')
        good = self.read(path)
        variants = {
            'unknown task key': lambda o: o['task'].update(extra=True),
            'wrong task version': lambda o: o['task'].update(schema_version='wrong'),
            'boolean protocol version': lambda o: o.update(protocol_version=True),
            'wrong operation': lambda o: o['task']['effects']['actions'][0].update(operation='overwrite'),
            'wrong tool': lambda o: o['task']['effects']['actions'][0].update(tool='other'),
            'unknown action key': lambda o: o['task']['effects']['actions'][0].update(extra=True),
            'wrong outputs': lambda o: o['task']['effects'].update(expected_outputs=['working/other.txt']),
            'boolean revision': lambda o: o['task'].update(task_revision=True),
            'missing intent': lambda o: o['task'].pop('intent'),
            'wrong intent kind': lambda o: o['task']['intent']['refs'][0].update(kind='grant'),
            'malformed task': lambda o: o.update(task=[]),
            'malformed actor': lambda o: o['task']['authority']['subject'].update(role=[]),
        }
        try:
            for label, change in variants.items():
                with self.subTest(label):
                    obj = pn.cj_loads(good)
                    change(obj)
                    raw = pn.cj_dumps(obj)
                    with open(path, 'wb') as f:
                        f.write(raw)
                    self.assertIsNone(pn.validate_evidence(raw, rid, 'prepared'))
                    self.assertFalse(pn.status(self.project, rid)['items'][0]['consistent'])
                    for op in (pn.recover, pn.discard_staged):
                        result = op(self.project, rid)
                        self.assertEqual((result['outcome'], result['reason'], result['wrote']),
                                         ('UNKNOWN', 'EVIDENCE_INCONSISTENT', []))
                    self.assertEqual(self.read(self.ev(rid, 'staged')), self.staged)
                    self.assertEqual(self.read(self.target()), b'user file')
        finally:
            with open(path, 'wb') as f:
                f.write(good)

    def test_malformed_enum_types_refuse_without_an_exception(self):
        for field in ('role', 'source_class', 'channel'):
            for value in ([], {}):
                with self.subTest(field=field, value=value):
                    request = self.request()
                    owner = request['subject'] if field == 'role' else request['intent_ref']['attribution']
                    owner[field] = value
                    result = pn.publish(self.project, request, self.staged)
                    self.assertEqual((result['outcome'], result['reason'], result['wrote']),
                                     ('REFUSED', 'REQUEST_INVALID', []))
        self.assertFalse(os.path.exists(self.pub_dir()))
        for state in ('conflict', 'abandoned', 'unknown'):
            obj = dict(pn._header('a' * 32, state.upper()), reason=[])
            if state == 'unknown':
                obj['by'] = 'recover'
            self.assertIsNone(pn.validate_evidence(pn.cj_dumps(obj), 'a' * 32, state))

    def published(self):
        res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(res['outcome'], 'PUBLISHED')
        return res['request_id']

    def test_non_canonical_or_foreign_evidence_fails_closed(self):
        rid = self.published()
        path = self.ev(rid, 'published')
        good = self.read(path)
        variants = {
            'whitespace': json.dumps(json.loads(good.decode('utf-8')), indent=1).encode('utf-8'),
            'extra key': pn.cj_dumps(dict(pn.cj_loads(good), extra=1)),
            'other version': pn.cj_dumps(dict(pn.cj_loads(good), protocol_version=2)),
            'identity as integer': pn.cj_dumps(dict(pn.cj_loads(good), identity={'volume_serial': 1, 'file_index': 2})),
            'wrong content': pn.cj_dumps(dict(pn.cj_loads(good), content={'sha256': 'sha256:' + '0' * 64, 'size': 1})),
        }
        for name, raw in variants.items():
            with self.subTest(name):
                with open(path, 'wb') as f:
                    f.write(raw)
                self.assertFalse(pn.status(self.project, rid)['items'][0]['consistent'])
                rec = pn.recover(self.project, rid)
                self.assertEqual((rec['outcome'], rec['reason'], rec['wrote']), ('UNKNOWN', 'EVIDENCE_INCONSISTENT', []))
                self.assertEqual(pn.observe(self.project, request_id=rid)['reason'], 'EVIDENCE_INCONSISTENT')
        with open(path, 'wb') as f:
            f.write(good)
        self.assertTrue(pn.status(self.project, rid)['items'][0]['consistent'])

    def test_multiple_terminals_and_empty_prepared(self):
        rid = self.published()
        with open(self.ev(rid, 'conflict'), 'wb') as f:
            f.write(pn.cj_dumps(dict(pn._header(rid, 'CONFLICT'), reason='TARGET_EXISTS')))
        rec = pn.recover(self.project, rid)
        self.assertEqual((rec['outcome'], rec['reason'], rec['wrote']), ('UNKNOWN', 'EVIDENCE_INCONSISTENT', []))
        self.assertEqual(pn.discard_staged(self.project, rid)['reason'], 'EVIDENCE_INCONSISTENT')
        empty = 'a' * 32
        open(self.ev(empty, 'prepared'), 'wb').close()
        rec = pn.recover(self.project, empty)
        self.assertEqual((rec['outcome'], rec['reason']), ('UNKNOWN', 'PREPARED_UNREADABLE'))
        self.assertEqual(pn.recover(self.project, empty)['outcome'], 'NO_ACTION', 'unknown is terminal; not rewritten')
        self.assertEqual(pn.recover(self.project, 'b' * 32)['reason'], 'PREPARED_UNREADABLE')
        self.assertFalse(os.path.exists(self.ev('b' * 32, 'unknown')), 'no prepared, no lock: nothing written')
        with open(os.path.join(self.pub_dir(), 'stray.txt'), 'wb') as f:
            f.write(b'x')
        self.assertEqual(pn.status(self.project)['unexpected'], ['stray.txt'])

    def test_terminal_next_to_broken_prepared_is_inconsistent(self):
        os.makedirs(os.path.dirname(self.target()))
        with open(self.target(), 'wb') as f:
            f.write(b'user file')
        rid = pn.publish(self.project, self.request(), self.staged)['request_id']
        with open(self.ev(rid, 'prepared'), 'ab') as f:
            f.write(b' ')
        self.assertEqual(pn.recover(self.project, rid)['reason'], 'EVIDENCE_INCONSISTENT')
        self.assertEqual(pn.discard_staged(self.project, rid)['reason'], 'EVIDENCE_INCONSISTENT')
        self.assertTrue(os.path.exists(self.ev(rid, 'staged')), 'nothing deleted on inconsistent evidence')
        self.assertFalse(pn.status(self.project, rid)['items'][0]['consistent'])

    def test_rid_taken_by_an_early_recover_is_a_consistent_terminal(self):
        empty = 'c' * 32
        os.makedirs(self.pub_dir())
        open(self.ev(empty, 'prepared'), 'wb').close()
        pn.recover(self.project, empty)
        st = pn.status(self.project, empty)['items'][0]
        self.assertEqual((st['terminal'], st['consistent']), ('unknown', True))

    def test_supersedes_is_unbound_metadata(self):
        first = self.published()
        res = pn.publish(self.project, self.request(target='working/w-20261018-01/bao-cao-nhap-v2.docx', supersedes=first), self.staged)
        prepared = pn.validate_evidence(self.read(self.ev(res['request_id'], 'prepared')), res['request_id'], 'prepared')
        self.assertEqual(prepared['supersedes'], first)
        self.assertNotIn('supersedes', prepared['task'])


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class CallerRid(Base):
    """Corrective P-CN1: a caller-chosen request id keeps one task snapshot across plan, publish and accept."""
    RID = 'a1b2c3d4' * 4

    def test_caller_rid_is_the_task_id_and_the_snapshot_is_the_planned_one(self):
        request = self.request()
        planned = pn.build_task(request, self.RID)
        res = pn.publish(self.project, request, self.staged, request_id=self.RID)
        self.assertEqual((res['outcome'], res['request_id']), ('PUBLISHED', self.RID))
        prepared = pn.validate_evidence(self.read(self.ev(self.RID, 'prepared')), self.RID, 'prepared')
        self.assertEqual(pn.cj_dumps(prepared['task']), pn.cj_dumps(planned), 'the task snapshot is exactly build_task(request, rid)')
        self.assertEqual(prepared['task']['task_id'], 'pcn1-' + self.RID)
        self.assertEqual(self.only_rid(), self.RID)

    def test_default_rid_is_still_generated(self):
        a = pn.publish(self.project, self.request(target='working/w/a.docx'), self.staged)
        b = pn.publish(self.project, self.request(target='working/w/b.docx'), self.staged)
        self.assertRegex(a['request_id'], r'^[0-9a-f]{32}$')
        self.assertNotEqual(a['request_id'], b['request_id'])

    def test_invalid_rid_is_refused_before_anything_is_written(self):
        before = self.tree()
        bad = ['', 'A' * 32, 'a' * 31, 'a' * 33, self.RID + '\n', ' ' + self.RID[1:], '../' + self.RID[3:], self.RID.replace('a', 'g'),
               b'a' * 32, 12345, True, False, 0, [], {}, 1.5]
        for value in bad:
            with self.subTest(repr(value)):
                res = pn.publish(self.project, self.request(), self.staged, request_id=value)
                self.assertEqual((res['outcome'], res['reason'], res['request_id'], res['wrote']), ('REFUSED', 'REQUEST_ID_INVALID', None, []))
                self.assertEqual(self.tree(), before)
        self.assertFalse(os.path.exists(self.target()))

    def test_reused_rid_never_overwrites_or_deletes_the_first_run(self):
        first = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual(first['outcome'], 'PUBLISHED')
        names = ('prepared', 'published')
        kept = dict((n, self.read(self.ev(self.RID, n))) for n in names)
        listing, target = self.tree(), self.read(self.target())
        again = pn.publish(self.project, self.request(target='working/w-20261018-01/khac.docx'), b'other bytes', request_id=self.RID)
        self.assertEqual((again['outcome'], again['reason'], again['request_id'], again['wrote']), ('REFUSED', 'RID_TAKEN', self.RID, []))
        for n in names:
            self.assertEqual(self.read(self.ev(self.RID, n)), kept[n])
        self.assertEqual((self.tree(), self.read(self.target())), (listing, target))

    def test_any_orphan_file_of_the_rid_is_a_collision(self):
        os.makedirs(self.pub_dir())
        for state in pn.RID_FILE_STATES:
            with self.subTest(state):
                path = self.ev(self.RID, state)
                with open(path, 'wb') as f:
                    f.write(b'sentinel ' + state.encode())
                before = self.tree()
                res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
                self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RID_TAKEN', []))
                self.assertEqual(self.read(path), b'sentinel ' + state.encode())
                self.assertEqual(self.tree(), before)
                os.remove(path)
        self.assertFalse(os.path.exists(self.target()))

    def test_two_callers_with_one_rid_only_one_publishes(self):
        seen = {}

        def hook(point, info):
            if point == 'after_bootstrap' and 'second' not in seen:
                seen['second'] = pn.publish(self.project, self.request(target='working/w/b.docx'), b'second', request_id=self.RID)
        with mock.patch.object(pn, '_HOOK', hook):
            first = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual((seen['second']['outcome'], seen['second']['reason'], seen['second']['wrote']), ('REFUSED', 'RID_TAKEN', []))
        self.assertEqual(first['outcome'], 'PUBLISHED')
        self.assertEqual(self.read(self.target()), self.staged)
        self.assertFalse(os.path.exists(self.target('working/w/b.docx')))

    def test_orphan_that_appears_before_the_pins_are_taken_is_kept(self):
        orphan = self.ev(self.RID, 'staged')

        def hook(point, info):
            if point == 'before_pin':  # after the lexical checks, before any pin or mutation: the pinned check is the one that counts
                os.makedirs(self.pub_dir())
                with open(orphan, 'wb') as f:
                    f.write(b'late orphan')
        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RID_TAKEN', []))
        self.assertEqual(self.read(orphan), b'late orphan')
        self.assertEqual(os.listdir(self.pub_dir()), [os.path.basename(orphan)])

    def test_orphan_that_appears_after_prepared_is_kept_and_wrote_is_honest(self):
        orphan = self.ev(self.RID, 'staged')

        def hook(point, info):
            if point == 'after_bootstrap':
                with open(orphan, 'wb') as f:
                    f.write(b'late orphan')
        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual((res['outcome'], res['reason']), ('REFUSED', 'RID_TAKEN'))
        self.assertEqual([(w['envelope'], w['op']) for w in res['wrote']], [('T2', 'mkdir'), ('T3', 'create')], 'the empty prepared stays and is reported')
        self.assertEqual(self.read(orphan), b'late orphan')
        self.assertFalse(os.path.exists(self.target()))

    def test_cli_rid_and_invalid_rid(self):
        r = self.cli_publish(rid=self.RID)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.only_rid(), self.RID)
        before = self.tree()
        for value in (self.RID, 'nothex', self.RID.upper()):
            r = self.cli_publish(request=self.request(target='working/w/x.docx'), rid=value)
            with self.subTest(value):
                self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
                self.assertEqual(self.tree(), before)

    def test_request_from_task_is_the_inverse_only_for_supported_fields(self):
        for over in ({}, {'target': 'output/w/a.docx', 'content_use': ['internal_draft']}, {'unconfirmed': ['gia']}):
            task = pn.build_task(self.request(**over), self.RID)
            self.assertEqual(pn.cj_dumps(pn.build_task(pn.request_from_task(task), self.RID)), pn.cj_dumps(task))
            self.assertTrue(pn._snapshot_ok(task, self.RID))
        base = pn.build_task(self.request(), self.RID)
        for label, mutate in (('envelope', lambda t: t['envelope'].update(max_retries={'status': 'REQUESTED', 'value': 1})),
                              ('context_refs', lambda t: t.update(context_refs=[{'path': 'references/a.md', 'digest': 'sha256:' + '3' * 64}])),
                              ('effects', lambda t: t['effects'].update(protected_targets=['AGENTS.md'])),
                              ('second_action', lambda t: t['effects']['actions'].append(dict(t['effects']['actions'][0])))):
            task = json.loads(json.dumps(base))
            mutate(task)
            with self.subTest(label):
                self.assertNotEqual(pn.cj_dumps(pn.build_task(pn.request_from_task(task), self.RID)), pn.cj_dumps(task))
                self.assertFalse(pn._snapshot_ok(task, self.RID))


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class RuntimeBootstrap(Base):
    """T2: `.agent` and `.agent/runtime` must already exist; publish creates only `publish` below them."""
    bootstrap = False
    RID = CallerRid.RID

    def test_missing_agent_or_runtime_is_refused_and_nothing_is_created(self):
        for label, prepare in (('no .agent', lambda: None), ('no runtime', lambda: os.mkdir(os.path.join(self.project, '.agent')))):
            with self.subTest(label):
                prepare()
                before = self.tree()
                res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
                self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RUNTIME_PARENT_MISSING', []))
                self.assertEqual(self.tree(), before, 'not even the target parents are created')
                self.assertFalse(os.path.exists(os.path.join(self.project, 'working')))
                self.assertEqual(pn.publish(self.project, self.request(), self.staged)['reason'], 'RUNTIME_PARENT_MISSING')

    def test_with_the_parents_in_place_only_publish_is_created(self):
        os.makedirs(os.path.join(self.project, '.agent', 'runtime'))
        res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual(res['outcome'], 'PUBLISHED')
        mk = [(w['path'], w['envelope']) for w in res['wrote'] if w['op'] == 'mkdir' and w['envelope'] == 'T2']
        self.assertEqual(mk, [('.agent/runtime/publish', 'T2')])

    def test_runtime_removed_after_the_first_check_is_not_recreated(self):
        runtime = os.path.join(self.project, '.agent', 'runtime')
        os.makedirs(runtime)

        def hook(point, info):
            if point == 'before_pin':
                os.rmdir(runtime)
        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RUNTIME_PARENT_MISSING', []))
        self.assertFalse(os.path.exists(runtime))
        self.assertFalse(os.path.exists(os.path.join(self.project, 'working')))

    def test_pin_unavailable_for_a_bootstrap_parent_stops_before_publish_is_created(self):
        os.makedirs(os.path.join(self.project, '.agent', 'runtime'))
        real_hold = pn.transaction.Pins.hold
        for name in ('.agent', 'runtime'):
            def hold(pins, path, name=name):
                return False if os.path.basename(path) == name else real_hold(pins, path)
            with self.subTest(name):
                before = self.tree()
                with mock.patch.object(pn.transaction.Pins, 'hold', hold):
                    res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
                self.assertEqual((res['outcome'], res['reason'], res['wrote'], res['detail']), ('REFUSED', 'RUNTIME_LINKED', [], 'PIN_UNAVAILABLE'))
                self.assertEqual(self.tree(), before, 'no publish folder, prepared or target parent was created')

    def test_linked_agent_is_refused_without_writing(self):
        outside = os.path.join(self.tmp, 'agent-outside')
        self.junction(os.path.join(self.project, '.agent'), outside)
        res = pn.publish(self.project, self.request(), self.staged, request_id=self.RID)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RUNTIME_LINKED', []))
        self.assertEqual(os.listdir(outside), [])

    def test_observe_reports_the_same_precondition_read_only(self):
        before = self.tree()
        ob = pn.observe(self.project, target='working/w/a.docx')
        self.assertEqual((ob['outcome'], ob['runtime_parents_ready'], ob['wrote']), ('OBSERVED', False, []))
        self.assertEqual(pn.runtime_parents_problem(self.project), 'RUNTIME_PARENT_MISSING')
        self.assertEqual(self.tree(), before)
        os.makedirs(os.path.join(self.project, '.agent', 'runtime'))
        self.assertTrue(pn.observe(self.project, target='working/w/a.docx')['runtime_parents_ready'])
        self.assertIsNone(pn.runtime_parents_problem(self.project))


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class Cli(Base):
    def test_exit_codes_and_changes(self):
        r = self.cli_publish()
        env = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, env['status'], env['outcome'], env['changes']), (0, 'success', 'PUBLISHED', True))
        r = self.cli_publish()
        env = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, env['status'], env['outcome'], env['changes']), (3, 'blocked', 'CONFLICT', True),
                         'a conflict still wrote evidence')
        r = self.cli_publish(request=self.request(target='references/x.docx'))
        env = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, env['outcome'], env['changes']), (4, 'REFUSED', False))
        r = self.cli('status')
        self.assertEqual(r.returncode, 0)
        r = self.cli('recover', 'not-a-rid')
        self.assertEqual(r.returncode, 2)
        r = self.cli('nonsense')
        self.assertEqual(r.returncode, 2)
        req = os.path.join(self.tmp, 'bad.json')
        with open(req, 'wb') as f:
            f.write(b'{"a":1,"a":2}')
        st = os.path.join(self.tmp, 'staged.bin')
        r = self.cli('publish', '--request', req, '--staged', st)
        self.assertEqual((r.returncode, result_schema.split_output(r.stdout)[1]['reason']), (4, 'REQUEST_INVALID'))


@unittest.skipUnless(WINDOWS, 'P-CN1 v1 is Windows + local NTFS only')
class ReviewerMutationBoundaries(Base):
    """Path and cleanup boundaries of every mutation (reviewer regressions, then the bounded corrective).

    All junction destinations remain in this fake temporary project, outside the approved working/runtime subtree; no user
    document or real project is changed. A pin or delete handle may stop the injected swap itself: the harness then records
    the blocked operation and the tests check that nothing moved and no data was lost, instead of forcing the bad swap.
    """

    def swap_for_junction(self, folder, outside, blocked):
        """Replace `folder` by a junction to `outside`. An OSError from the OS (pinned/held folder) is recorded, not hidden."""
        try:
            os.rename(folder, folder + '-moved')
            self.junction(folder, outside)
        except OSError as e:
            blocked.append(getattr(e, 'winerror', e.errno))

    def tree(self, root):
        out = []
        for base, dirs, files in os.walk(root):
            out.extend(os.path.relpath(os.path.join(base, n), root) for n in dirs + files)
        return sorted(out)

    def test_t1_parent_changed_after_initial_check_does_not_create_through_junction(self):
        working = os.path.join(self.project, 'working')
        outside = os.path.join(self.project, 'outside-working')
        os.mkdir(working)
        os.mkdir(outside)
        blocked = []

        def hook(point, info):
            if point == 'after_bootstrap':
                try:
                    os.rmdir(working)
                    self.junction(working, outside)
                except OSError as e:
                    blocked.append(e.winerror)

        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(blocked, [32], 'the pinned parent cannot be removed or replaced while the mutation runs')
        self.assertFalse(os.path.exists(os.path.join(outside, 'w-20261018-01')),
                         'T1 must stop before mkdir through a replaced parent')
        self.assertEqual(os.listdir(outside), [])
        self.assertTrue(pn._is_plain_dir(pn.file_info(working)), 'working is still the plain folder it was')
        self.assertEqual((res['outcome'], self.read(self.target())), ('PUBLISHED', self.staged), 'nothing else changed')

    def test_t1_parent_replaced_before_it_is_pinned_is_refused_before_any_write(self):
        working = os.path.join(self.project, 'working')
        outside = os.path.join(self.project, 'outside-working')
        os.mkdir(working)
        os.mkdir(outside)

        def hook(point, info):
            if point == 'before_pin':  # after the first lexical check, before the first pin: nothing holds `working` yet
                os.rmdir(working)
                self.junction(working, outside)

        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'PARENT_UNSAFE', []))
        self.assertEqual(os.listdir(outside), [], 'nothing was created through the junction')
        self.assertFalse(os.path.exists(os.path.join(self.project, '.agent', 'runtime', 'publish')), 'no publish folder before the parents are proven')

    def test_t2_runtime_replaced_before_it_is_pinned_is_refused_before_any_write(self):
        outside = os.path.join(self.project, 'outside-runtime')
        os.mkdir(outside)
        runtime = os.path.join(self.project, '.agent', 'runtime')

        def hook(point, info):
            if point == 'before_pin':  # after the first lexical check, before any pin: nothing holds `.agent/runtime` yet
                os.rmdir(runtime)
                self.junction(runtime, outside)

        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RUNTIME_LINKED', []))
        self.assertEqual(os.listdir(outside), [], 'T2 must not create `publish` through a replaced runtime folder')

    def test_t2_runtime_folder_cannot_be_swapped_after_it_is_pinned(self):
        outside = os.path.join(self.project, 'outside-runtime')
        os.mkdir(outside)
        runtime = os.path.join(self.project, '.agent', 'runtime')
        real_mkdir = os.mkdir
        blocked = []

        def mkdir(path, *args, **kwargs):
            result = real_mkdir(path, *args, **kwargs)
            if os.path.normcase(path) == os.path.normcase(os.path.join(runtime, 'publish')):
                self.swap_for_junction(runtime, outside, blocked)  # runtime is pinned already: the OS must refuse
            return result

        with mock.patch.object(pn.os, 'mkdir', side_effect=mkdir):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(blocked, [32])
        self.assertEqual(os.listdir(outside), [])
        self.assertTrue(pn._is_plain_dir(pn.file_info(runtime)))
        self.assertEqual(res['outcome'], 'PUBLISHED')

    def test_root_junction_is_refused_everywhere_and_writes_nothing(self):
        real = os.path.join(self.tmp, 'real-root')
        link = os.path.join(self.tmp, 'link-root')
        os.makedirs(os.path.join(real, 'references', 'source-documents', 'team'))
        with open(os.path.join(real, 'references', 'source-documents', 'team', 'quy-che-gia.pdf'), 'wb') as f:
            f.write(b'%PDF fake source bytes')
        self.junction(link, real)
        before = self.tree(real)
        res = pn.publish(link, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'PARENT_UNSAFE', []))
        for call in (pn.recover, pn.discard_staged):
            r = call(link, '0' * 32)
            self.assertEqual((r['outcome'], r['reason'], r['wrote']), ('REFUSED', 'PARENT_UNSAFE', []))
        st = pn.status(link)
        self.assertEqual((st['outcome'], st['reason']), ('UNSUPPORTED', 'RUNTIME_LINKED'))
        self.assertEqual(self.tree(real), before, 'nothing was created behind the root junction')

    def test_pin_unavailable_stops_publish_recover_and_discard_without_writing(self):
        # a conflict leaves a terminal and a staged file for recover/discard to look at
        os.makedirs(os.path.dirname(self.target()))
        with open(self.target(), 'wb') as f:
            f.write(b'user file')
        conflict = pn.publish(self.project, self.request(), self.staged)
        rid = conflict['request_id']
        before = self.tree(self.project)
        with mock.patch.object(pn.transaction.Pins, 'hold', return_value=False):
            for call in (pn.recover, pn.discard_staged):
                r = call(self.project, rid)
                self.assertEqual((r['outcome'], r['reason'], r['wrote']), ('REFUSED', 'RUNTIME_LINKED', []))
                self.assertEqual(r['detail'], 'PIN_UNAVAILABLE')
            r = pn.publish(self.project, self.request(target='working/other/draft.docx'), self.staged)
            self.assertEqual((r['outcome'], r['reason'], r['wrote']), ('REFUSED', 'PARENT_UNSAFE', []))
            self.assertEqual(r['detail'], 'PIN_UNAVAILABLE')
        self.assertEqual(self.tree(self.project), before, 'no file or folder was created, changed or removed')
        self.assertTrue(os.path.exists(self.ev(rid, 'staged')))
        self.assertEqual(self.read(self.target()), b'user file')

    def test_pin_lost_for_a_new_parent_after_prepared_is_abandoned_with_true_wrote(self):
        real_hold = pn.transaction.Pins.hold

        def hold(self_, path):
            if os.path.basename(path) == 'w-20261018-01':
                return False
            return real_hold(self_, path)

        with mock.patch.object(pn.transaction.Pins, 'hold', hold):
            res = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual((res['outcome'], res['reason']), ('ABANDONED', 'LINK_FAILED'))
        self.assertFalse(os.path.exists(self.target()), 'nothing was linked without the folder being pinned')
        ops = [(w['envelope'], w['op']) for w in res['wrote']]
        self.assertIn(('T1', 'mkdir'), ops, 'the folder made before the pin failed is reported')
        self.assertNotIn(('T5', 'link'), ops)
        rid = res['request_id']
        self.assertIsNotNone(pn.validate_evidence(self.read(self.ev(rid, 'abandoned')), rid, 'abandoned'))

    def test_recover_does_not_write_terminal_through_parent_changed_before_open(self):
        crash = self.cli_publish(fault='pcn1-kill:after_link')
        self.assertEqual(crash.returncode, 70)
        rid = self.only_rid()
        prep = self.ev(rid, 'prepared')
        moved = os.path.join(self.project, 'outside-publish')
        real_open = os.open
        blocked = []

        def opening(path, flags, *args, **kwargs):
            if path == prep and not blocked:
                try:
                    os.rename(self.pub_dir(), moved)
                    self.junction(self.pub_dir(), moved)
                except OSError as e:
                    blocked.append(e.winerror)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(pn.os, 'open', side_effect=opening):
            res = pn.recover(self.project, rid)
        self.assertEqual(blocked, [32], 'the pinned runtime chain cannot be renamed while recover holds it')
        self.assertFalse(os.path.exists(moved))
        self.assertTrue(pn._is_plain_dir(pn.file_info(self.pub_dir())))
        self.assertEqual((res['outcome'], res['recovered']), ('PUBLISHED', True))
        self.assertTrue(os.path.exists(self.ev(rid, 'published')), 'the terminal is in the real runtime folder')

    def test_recover_and_discard_refuse_a_runtime_folder_replaced_before_it_is_pinned(self):
        crash = self.cli_publish(fault='pcn1-kill:after_link')
        self.assertEqual(crash.returncode, 70)
        rid = self.only_rid()
        moved = os.path.join(self.project, 'outside-publish')
        before = self.tree(self.pub_dir())
        for which in (pn.recover, pn.discard_staged):
            with self.subTest(which=which.__name__):
                def hook(point, info):
                    if point == 'before_runtime_pin':  # plain at the first check, not pinned yet
                        os.rename(self.pub_dir(), moved)
                        self.junction(self.pub_dir(), moved)

                with mock.patch.object(pn, '_HOOK', hook):
                    res = which(self.project, rid)
                self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('REFUSED', 'RUNTIME_LINKED', []))
                self.assertEqual(self.tree(moved), before, 'nothing written, removed or created in the swapped-in folder')
                os.rmdir(self.pub_dir())  # drop the junction itself; the real folder is what `moved` holds
                os.rename(moved, self.pub_dir())

    def test_published_cleanup_keeps_file_replaced_after_identity_check(self):
        # the object verified on the delete handle cannot be swapped under it
        def keep_staged(point):
            if point == 'cleanup':
                raise OSError('keep staged for the reviewer regression')

        with mock.patch.object(pn, '_fail_point', side_effect=keep_staged):
            result = pn.publish(self.project, self.request(), self.staged)
        self.assertEqual(result['outcome'], 'PUBLISHED')
        rid = result['request_id']
        path = self.ev(rid, 'staged')
        replacement = b'foreign replacement must stay'
        blocked = []

        def replace_after_check(point):
            if point == 'cleanup':
                try:
                    os.remove(path)
                    with open(path, 'wb') as handle:
                        handle.write(replacement)
                except OSError as e:
                    blocked.append(e.winerror)

        with mock.patch.object(pn, '_fail_point', side_effect=replace_after_check):
            res = pn.recover(self.project, rid)
        self.assertEqual(blocked, [32], 'the handle that verified the object also keeps it from being removed or renamed')
        self.assertFalse(os.path.exists(path), 'the verified staged object itself was removed')
        self.assertEqual((res['outcome'], res['reason'], res['cleanup_pending']), ('NO_ACTION', None, False))
        self.assertEqual([(w['envelope'], w['op']) for w in res['wrote']], [('T7', 'delete')])
        self.assertEqual(self.read(self.target()), self.staged, 'the published file kept its bytes')

    def test_published_cleanup_keeps_a_different_file_that_appears_before_the_handle_opens(self):
        def keep_staged(point):
            if point == 'cleanup':
                raise OSError('keep staged')

        with mock.patch.object(pn, '_fail_point', side_effect=keep_staged):
            result = pn.publish(self.project, self.request(), self.staged)
        rid = result['request_id']
        path = self.ev(rid, 'staged')
        replacement = b'foreign replacement must stay'

        def hook(point, info):
            if point == 'before_delete_open':
                os.remove(path)
                with open(path, 'wb') as handle:
                    handle.write(replacement)

        with mock.patch.object(pn, '_HOOK', hook):
            res = pn.recover(self.project, rid)
        self.assertEqual((res['outcome'], res['reason'], res['cleanup_pending'], res['wrote']),
                         ('NO_ACTION', 'STAGED_CLEANUP_PENDING', True, []))
        self.assertEqual(self.read(path), replacement)
        self.assertEqual(self.read(self.target()), self.staged)

    def test_discard_deletes_only_the_object_it_checked(self):
        os.makedirs(os.path.dirname(self.target()))
        with open(self.target(), 'wb') as f:
            f.write(b'user file')
        rid = pn.publish(self.project, self.request(), self.staged)['request_id']
        path = self.ev(rid, 'staged')
        replacement = b'foreign replacement must stay'

        def swapped(point, info):
            if point == 'before_delete_open':
                os.remove(path)
                with open(path, 'wb') as handle:
                    handle.write(replacement)

        with mock.patch.object(pn, '_HOOK', swapped):
            res = pn.discard_staged(self.project, rid)
        self.assertEqual((res['outcome'], res['reason'], res['wrote']), ('UNKNOWN', 'EVIDENCE_INCONSISTENT', []))
        self.assertEqual(self.read(path), replacement)
        # a swap that arrives after the check is stopped by the handle; discard then deletes exactly the checked file
        os.remove(path)
        with open(path, 'wb') as handle:
            handle.write(self.staged)
        blocked = []

        def after_check(point):
            if point == 'cleanup':
                try:
                    os.rename(path, path + '.moved')
                except OSError as e:
                    blocked.append(e.winerror)

        with mock.patch.object(pn, '_fail_point', side_effect=after_check):
            res = pn.discard_staged(self.project, rid)
        self.assertEqual(blocked, [32])
        self.assertEqual((res['outcome'], [(w['envelope'], w['op']) for w in res['wrote']]), ('DISCARDED', [('T7', 'delete')]))
        self.assertFalse(os.path.exists(path))
        self.assertEqual(self.read(self.target()), b'user file')


    def test_cleanup_reports_pending_until_a_sharing_reader_closes(self):
        import ctypes

        kernel = pn._kernel32()
        readers = []

        def open_reader(path):
            handle = kernel.CreateFileW(path, 0x80, 0x7, None, 3, 0x00200000, None)
            self.assertNotIn(handle, (None, ctypes.c_void_p(-1).value))
            readers.append(handle)

        def keep_staged(point):
            if point == 'cleanup':
                raise OSError('leave staged for pending-delete regression')

        try:
            for method, outcome in (('publish', 'PUBLISHED'), ('recover', 'NO_ACTION'), ('discard', 'DISCARDED')):
                with self.subTest(method=method):
                    target = 'working/pending-' + method + '/draft.docx'
                    expected = self.staged
                    if method == 'publish':
                        def reader_after_link(point, info):
                            if point == 'after_link':
                                open_reader(info['staged'])

                        with mock.patch.object(pn, '_HOOK', reader_after_link):
                            result = pn.publish(self.project, self.request(target=target), self.staged)
                        rid = result['request_id']
                    else:
                        if method == 'discard':
                            os.makedirs(os.path.dirname(self.target(target)))
                            expected = b'user file'
                            with open(self.target(target), 'wb') as handle:
                                handle.write(expected)
                            first = pn.publish(self.project, self.request(target=target), self.staged)
                            self.assertEqual(first['outcome'], 'CONFLICT')
                        else:
                            with mock.patch.object(pn, '_fail_point', side_effect=keep_staged):
                                first = pn.publish(self.project, self.request(target=target), self.staged)
                            self.assertEqual(first['outcome'], 'PUBLISHED')
                        rid = first['request_id']
                        open_reader(self.ev(rid, 'staged'))
                        result = (pn.recover if method == 'recover' else pn.discard_staged)(self.project, rid)
                    staged_path = self.ev(rid, 'staged')
                    self.assertEqual((result['outcome'], result['reason'], result['cleanup_pending']),
                                     (outcome, 'STAGED_CLEANUP_PENDING', True))
                    self.assertEqual(len([w for w in result['wrote'] if w['envelope'] == 'T7']), 1,
                                     'wrote retains the delete disposition actually requested')
                    self.assertTrue(os.path.lexists(staged_path), 'another reader still holds the pending-delete name')
                    self.assertEqual(self.read(self.target(target)), expected)
                    kernel.CloseHandle(readers.pop())
                    self.assertFalse(os.path.lexists(staged_path), 'the name disappears after the sharing reader closes')
                    self.assertEqual(self.read(self.target(target)), expected, 'the output hard link remains intact')
        finally:
            while readers:
                kernel.CloseHandle(readers.pop())


if __name__ == '__main__':
    unittest.main()
