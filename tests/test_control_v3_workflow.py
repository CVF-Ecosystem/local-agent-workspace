"""Luồng P-CN1 một file: gate + observer + receipt + D4 (stage P_CN1_ONE_FILE) / one-file P-CN1 gates, observer, receipt and D4.

Dữ liệu giả trong thư mục tạm; vòng thật dispatch -> effect -> `publish_new.publish` (gọi từ test, không từ checker) -> accept. Oracle là kỳ vọng viết tay
theo contract v3 (mục 4-8, 11) và README, không lấy từ chính output. Không sửa ví dụ/vectors/policy/schema frozen; mọi biến thể làm trong bộ nhớ.
Chỉ Windows NTFS local (owner chỉ hỗ trợ đó): nơi khác lớp kiểm này bị bỏ qua và ghi rõ.
"""
import copy
import hashlib
import importlib
import importlib.util
import inspect
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
ENTRY = ROOT / '.cvf' / 'checks' / 'control_check_v3.py'
sys.path.insert(0, str(ROOT / 'tools'))
import publish_new as pn  # noqa: E402

V3 = 'law.cvf.control/3'
EB = 'COOPERATIVE_WORKFLOW'
WRITER_PIN = '8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852'
OUTPUT_KEYS = ['check_version', 'contract', 'selection', 'candidate_status', 'implementation_stage', 'evaluation_basis', 'phase',
               'phase_scope', 'disposition', 'effect_authorized', 'assurance_level', 'init_error', 'reasons', 'details', 'owners',
               'route', 'gates', 'aggregate', 'coverage']
GATES = ['GRANT_SCOPE', 'PATH_SCOPE', 'TOOL_SCOPE', 'ENVELOPE', 'BINDING', 'INPUT_REVISION', 'ACTUAL_OUTCOME', 'REQUIREMENTS']
CAN_RUN = os.name == 'nt' and pn.volume_supported(tempfile.gettempdir())[0]
MARKER = 'LEAK-MARKER-7f3a'


def att(source='USER_CONFIRMATION', channel='USER_MESSAGE', locator='host:msg/0012'):
    return {'source_class': source, 'channel': channel, 'evidence_locator': locator, 'recorded_by': {'actor_id': 'main', 'role': 'main'}}


def tool_att():
    actor = {'actor_id': 'publish_new', 'role': 'tool'}
    return {'source_class': 'TOOL_OBSERVATION', 'channel': 'TOOL_OUTPUT', 'recorded_by': actor, 'observed_by': actor}


def slurp(path):
    with open(path, 'rb') as f:
        return f.read()


def sha_file(path):
    with open(path, 'rb') as f:
        return 'sha256:' + hashlib.sha256(f.read()).hexdigest()


@unittest.skipUnless(CAN_RUN, 'the P-CN1 owner supports Windows NTFS local only (this layer is skipped elsewhere, not passed)')
class Loop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('law_cvf_entry_v3_workflow_test', str(ENTRY))
        cls.entry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.entry)
        cls.entry._load_package()
        base = cls.entry.PACKAGE_NAME + '.'
        cls.canon = importlib.import_module(base + 'canon')
        cls.loader = importlib.import_module(base + 'loader')
        cls.observer = importlib.import_module(base + 'observer')
        cls.owners = cls.loader.load_owners()
        cls.v3_pin = hashlib.sha256((ROOT / 'tools' / 'publish_new.py').read_bytes()).hexdigest()

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix='law-wf-')
        self.addCleanup(shutil.rmtree, self.project, True)
        os.makedirs(os.path.join(self.project, '.agent', 'runtime'))  # bootstrap parents are made by the fixture: the owner never creates them
        src = os.path.join(self.project, 'references', 'source-documents', 'team')
        os.makedirs(src)
        self.source = os.path.join(src, 'quy-che-gia.pdf')
        with open(self.source, 'wb') as f:
            f.write(b'%PDF fake source bytes')
        self.source_digest = pn._sha_bytes(b'%PDF fake source bytes')
        self.staged = b'PK fake docx draft bytes ' * 50
        self.rid0 = 'a1b2c3d4' * 4  # planned id used before publish: the owner generates its own rid at publish time

    # ---------------------------------------------------------------- builders
    def request(self, **over):
        r = {'work_id': 'w-20261018-01', 'target': 'working/w-20261018-01/bao-cao-nhap.docx',
             'intent_ref': {'ref_id': 'intent-1', 'locator': 'host:msg/0012', 'digest': 'sha256:' + '5' * 64, 'attribution': att()},
             'main_interpretation': 'Báo cáo ngắn về mục giá',
             'requirements': [{'req_id': 'REQ-1', 'statement': 'Tóm tắt mục giá', 'mandatory': True},
                              {'req_id': 'REQ-2', 'statement': 'Nêu điểm chưa chắc', 'mandatory': True}],
             'grant_refs': [{'ref_id': 'grant-1', 'locator': 'PROJECT.md#pham-vi', 'digest': 'sha256:' + '1' * 64, 'attribution': att(locator='host:msg/0007')}],
             'subject': {'actor_id': 'main', 'role': 'main'},
             'inputs': [{'path': 'references/source-documents/team/quy-che-gia.pdf', 'digest': self.source_digest}]}
        r.update(over)
        return r

    def planned_task(self, **over):
        return pn.build_task(self.request(**over), self.rid0)

    def grant(self, task, **over):
        g = {'schema_version': V3, 'record_type': 'grant', 'evaluation_basis': EB, 'grant_id': 'grant-1', 'grant_revision': 1,
             'issuer': {'actor_id': 'the-user', 'role': 'user'}, 'issuer_ref': copy.deepcopy(task['authority']['grant_refs'][0]),
             'subject': {'roles': ['main'], 'actor_ids': ['main']},
             'scope': {'task_classes': ['draft'], 'operations': ['create_new', 'delete', 'read'], 'tools': ['publish_new'],
                       'paths': ['working/', 'output/', '.agent/runtime/publish/']},
             'status': 'ACTIVE'}
        g.update(over)
        return g

    def binding(self, task, outputs=None):
        d = self.canon.binding_digests(task, self.owners.policy)
        action = task['effects']['actions'][0]
        b = {'bind_version': 'law.cvf.bind/3', 'evaluation_basis': EB, 'task_id': task['task_id'], 'task_revision': task['task_revision'],
             'intent_digest': d['intent_digest'], 'accepted_task_digest': d['accepted_task_digest'], 'context_digest': d['context_digest'],
             'policy_version': 'law.cvf.routing/3', 'policy_digest': d['policy_digest'], 'inputs': copy.deepcopy(task['inputs']),
             'action_digest': self.canon.digest_of(self.canon.action_part(action))}
        if outputs is not None:
            b['outputs'] = outputs
        return b

    def effect(self, task, stage, artifacts=None, receipt=None, **over):
        subject = task['authority']['subject']
        rec = {'schema_version': V3, 'record_type': 'effect', 'evaluation_basis': EB, 'effect_id': 'eff-req-1' if stage == 'REQUEST' else 'eff-out-1',
               'stage': stage, 'binding': self.binding(task, artifacts), 'actor': dict(subject), 'action': copy.deepcopy(task['effects']['actions'][0]),
               'routing': {'policy_version': 'law.cvf.routing/3', 'matched_rows': ['R-READ_DRAFT'], 'required_review_phases': []},
               'grant_ref_ids': ['grant-1'], 'review_ids': [], 'assurance_level': 'ADVISORY',
               'disposition': 'PENDING' if stage == 'REQUEST' else 'NOT_APPLICABLE', 'reasons': [], 'decided_by': dict(subject)}
        if stage == 'OUTCOME':
            rec['outcome'] = {'status': 'APPLIED', 'artifacts': copy.deepcopy(artifacts), 'observed_by': {'actor_id': 'publish_new', 'role': 'tool'}}
            if receipt is not None:
                rec['receipt_ref'] = receipt
        rec.update(over)
        return rec

    def result(self, task, artifacts, acceptance=True, **over):
        subject = task['authority']['subject']
        rid = task['task_id'][len('pcn1-'):]
        res = {'schema_version': V3, 'record_type': 'result', 'evaluation_basis': EB, 'result_id': 'pcn1-r-' + rid,
               'binding': self.binding(task, artifacts), 'produced_by': dict(subject), 'artifacts': copy.deepcopy(artifacts),
               'actions_performed': [copy.deepcopy(task['effects']['actions'][0])], 'evidence': [],
               'requirements': [{'req_id': r['req_id'], 'mandatory': True, 'status': 'UNKNOWN'} for r in task['acceptance']['requirements']],
               'gaps': ['No tool checked the semantic content of the draft; only the user can accept it.'],
               'acceptance_states': ['CANDIDATE', 'EFFECT_APPLIED'], 'state_set_by': dict(subject)}
        if acceptance:
            res['acceptance_states'].append('USER_ACCEPTED')
            res['user_acceptance'] = self.acceptance(task, artifacts)
        res.update(over)
        return res

    def acceptance(self, task, artifacts, **over):
        rid = task['task_id'][len('pcn1-'):]
        ua = {'ref': {'ref_id': 'ua-1', 'kind': 'user_acceptance', 'locator': 'host:msg/0031', 'digest': 'sha256:' + '9' * 64,
                      'attribution': att(locator='host:msg/0031')},
              'task_id': task['task_id'], 'task_revision': task['task_revision'],
              'accepted_task_digest': self.canon.binding_digests(task, self.owners.policy)['accepted_task_digest'],
              'accepted_requirements': [r['req_id'] for r in task['acceptance']['requirements'] if r['mandatory']],
              'result_id': 'pcn1-r-' + rid, 'accepted_artifacts': copy.deepcopy(artifacts),
              'presented_summary': {'locator': 'host:msg/0030', 'digest': 'sha256:' + '8' * 64}}
        ua.update(over)
        return ua

    def bundle(self, *records):
        return {'schema_version': V3, 'record_type': 'bundle', 'evaluation_basis': EB, 'bundle_id': 'wf-test', 'records': list(records)}

    def run_check(self, bundle, phase, root=True):
        data = json.dumps(bundle, ensure_ascii=True).encode('utf-8')
        if root is True:
            root = self.project
        return self.entry.check_bytes(data, phase, 'v3', project_root=root) if root else self.entry.check_bytes(data, phase, 'v3')

    def gate(self, res, name):
        return [g for g in res['gates'] if g['gate'] == name][0]

    def statuses(self, res):
        return dict((g['gate'], g['status']) for g in res['gates'])

    def tree(self):
        out = {}
        for d, dirs, files in os.walk(self.project):
            for n in dirs + files:
                p = os.path.join(d, n)
                st = os.lstat(p)
                out[os.path.relpath(p, self.project)] = (st.st_size, st.st_mtime_ns)
        return out

    def planned(self, **over):
        task = self.planned_task(**over)
        return task, self.grant(task)

    def publish(self, request=None, rid=None):
        res = pn.publish(self.project, request or self.request(), self.staged, request_id=rid)
        self.assertEqual(res['outcome'], 'PUBLISHED', res)
        rid = res['request_id']
        prepared = pn.cj_loads(slurp(pn._evidence_path(self.project, rid, 'prepared')))
        return rid, prepared['task']

    def accept_bundle(self, rid, task, **kw):
        published_raw = slurp(pn._evidence_path(self.project, rid, 'published'))
        published = pn.cj_loads(published_raw)
        artifacts = [{'path': published['target'], 'digest': published['content']['sha256'], 'role': 'ACTUAL_BYTES'}]
        receipt = {'ref_id': 'receipt-' + rid, 'kind': 'effect_receipt', 'locator': '.agent/runtime/publish/%s.published.json' % rid,
                   'digest': pn._sha_bytes(published_raw), 'attribution': tool_att()}
        records = [task, self.grant(task), self.effect(task, 'OUTCOME', artifacts, receipt), self.result(task, artifacts, kw.get('acceptance', True))]
        return self.bundle(*records), artifacts, receipt

    def assert_not_pass(self, res):
        self.assertNotEqual(res['disposition'], 'PASS')
        self.assertIs(res['effect_authorized'], False)
        self.assertEqual(res['assurance_level'], 'UNVERIFIED')


class HappyLoop(Loop):
    def test_real_loop_dispatch_effect_publish_accept(self):
        task, grant = self.planned()
        before = self.tree()
        d = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assertEqual(self.tree(), before, 'the checker must not write anything')
        self.assertEqual(list(d), OUTPUT_KEYS)
        self.assertEqual((d['disposition'], d['reasons'], d['assurance_level'], d['effect_authorized']), ('PASS', [], 'ADVISORY', False))
        self.assertEqual(d['implementation_stage'], 'P_CN1_ONE_FILE')
        self.assertEqual(d['phase_scope'], 'STRUCTURE_ROUTING_GATES_OBSERVER')
        self.assertEqual([g['gate'] for g in d['gates']], GATES)
        self.assertEqual(self.statuses(d), {'GRANT_SCOPE': 'MET', 'PATH_SCOPE': 'MET', 'TOOL_SCOPE': 'MET', 'ENVELOPE': 'MET', 'BINDING': 'NOT_YET_DUE',
                                            'INPUT_REVISION': 'NOT_YET_DUE', 'ACTUAL_OUTCOME': 'NOT_YET_DUE', 'REQUIREMENTS': 'NOT_YET_DUE'})
        self.assertEqual((d['route']['status'], [r['row_id'] for r in d['route']['rows']]), ('RESOLVED', ['R-READ_DRAFT']))
        self.assertEqual(d['route']['rows'][0]['not_evaluated_conditions'], [])
        assumption = d['route']['assumptions'][0]
        self.assertEqual((assumption['id'], assumption['status']), ('A-NEW_TARGET', 'CLOSED_BY_OBSERVATION'))
        self.assertEqual(assumption['limits'], ['EXCLUSIVE_WRITE_NOT_PROVEN', 'RACE_NOT_EXCLUDED'])
        cov = d['coverage']
        self.assertEqual((cov['gates_evaluated'], cov['target_existence_observed'], cov['artifact_bytes_observed']), (True, True, False))
        self.assertIs(cov['actual_operation_observed'], False)
        self.assertIs(cov['requirements_semantic_verified'], False)
        self.assertEqual(d['aggregate']['open_assumptions'], [])
        self.assertEqual((d['aggregate']['due_gates'], d['aggregate']['met'], d['aggregate']['not_yet_due']), (4, 4, 4))

        request = self.effect(task, 'REQUEST')
        e = self.run_check(self.bundle(task, grant, request), 'effect')
        self.assertEqual(self.tree(), before)
        self.assertEqual((e['disposition'], e['reasons']), ('PASS', []))
        self.assertEqual(self.statuses(e)['BINDING'], 'MET')
        self.assertEqual(self.statuses(e)['INPUT_REVISION'], 'MET')
        self.assertEqual(self.statuses(e)['ACTUAL_OUTCOME'], 'NOT_YET_DUE')
        self.assertEqual(e['phase_scope'], 'STRUCTURE_BINDING_ROUTING_GATES_OBSERVER')
        self.assertIs(e['coverage']['artifact_bytes_observed'], True, 'the input bytes were read by the observer in this run')
        self.assertIs(e['coverage']['binding_evaluated'], True)

        # The caller chose the rid before dispatch: the owner publishes exactly the planned snapshot, and accept uses that same task.
        rid, final_task = self.publish(rid=self.rid0)
        self.assertEqual((rid, final_task['task_id'], final_task['task_revision']), (self.rid0, task['task_id'], task['task_revision']))
        self.assertEqual(pn.cj_dumps(final_task), pn.cj_dumps(task), 'prepared holds the planned task, not another one')
        self.assertEqual(self.canon.binding_digests(final_task, self.owners.policy), self.canon.binding_digests(task, self.owners.policy))
        bundle, artifacts, _ = self.accept_bundle(rid, task)
        want = self.canon.binding_digests(task, self.owners.policy)
        action_digest = self.canon.digest_of(self.canon.action_part(task['effects']['actions'][0]))
        for label, rec in [('effect-request', request)] + [(r['record_type'], r) for r in bundle['records'] if 'binding' in r]:
            with self.subTest(label):  # the same task, revision and intent/context/accepted_task/action digests in all three phases
                for key in ('intent_digest', 'accepted_task_digest', 'context_digest', 'policy_digest'):
                    self.assertEqual(rec['binding'][key], want[key])
                self.assertEqual((rec['binding']['task_id'], rec['binding']['task_revision'], rec['binding']['action_digest']),
                                 (task['task_id'], task['task_revision'], action_digest))
        self.assertEqual(self.canon.digest_of(self.canon.action_part(final_task['effects']['actions'][0])), action_digest)
        listing = self.tree()
        a = self.run_check(bundle, 'accept')
        self.assertEqual(self.tree(), listing)
        self.assertEqual((a['disposition'], a['reasons'], a['assurance_level'], a['effect_authorized']), ('PASS', [], 'ADVISORY', False))
        self.assertEqual(self.statuses(a), {'GRANT_SCOPE': 'MET', 'PATH_SCOPE': 'MET', 'TOOL_SCOPE': 'MET', 'ENVELOPE': 'MET', 'BINDING': 'MET',
                                            'INPUT_REVISION': 'MET', 'ACTUAL_OUTCOME': 'MET', 'REQUIREMENTS': 'USER_ACCEPTED_DECLARED'})
        self.assertEqual([g for g in a['gates'] if g['gate'] == 'PATH_SCOPE'][0]['subchecks'],
                         {'lexical': 'MET', 'observed_at_time': 'NOT_REQUIRED', 'precondition_history': 'MET'})
        self.assertEqual(a['aggregate']['user_accepted_declared'], 1)
        self.assertEqual(a['route']['assumptions'][0]['status'], 'NOT_APPLICABLE_IN_PHASE')
        self.assertEqual(a['route']['status'], 'RESOLVED')
        self.assertIs(a['coverage']['artifact_bytes_observed'], True)
        self.assertIs(a['coverage']['requirements_semantic_verified'], False)
        self.assertIs(a['coverage']['actual_operation_observed'], False)

    def test_accept_does_not_open_effect_and_receipt_does_not_open_dispatch(self):
        # A published receipt for a different (earlier) run cannot open the planned task: the target now exists, so dispatch/effect stay BLOCKED.
        rid, final_task = self.publish()
        planned = self.planned_task()
        res = self.run_check(self.bundle(planned, self.grant(planned)), 'dispatch')
        self.assertEqual(res['disposition'], 'BLOCKED')
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'NOT_MET')
        self.assertIn('TARGET_EXISTS_OBSERVED', res['reasons'])
        self.assertEqual(res['route']['status'], 'CONDITIONAL', 'A-NEW_TARGET must stay open when the target is not absent')
        self.assertEqual(res['route']['assumptions'][0]['status'], 'OPEN')
        self.assertIn('ROUTE_ASSUMPTION_OPEN', res['reasons'])

    def test_output_zone_task_with_internal_content_use_also_passes_dispatch(self):
        task, grant = self.planned(target='output/w-1/bao-cao.docx', content_use=['internal_draft'])
        res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assertEqual((res['disposition'], res['reasons']), ('PASS', []))

    def test_no_root_stays_diagnostic_and_never_loads_the_observer(self):
        task, grant = self.planned()
        res = self.run_check(self.bundle(task, grant), 'dispatch', root=None)
        self.assertEqual((res['disposition'], res['implementation_stage'], res['gates']), ('BLOCKED', 'BINDING_ROUTING_ONLY', []))
        self.assertIn('CANDIDATE_EVALUATION_NOT_IMPLEMENTED', res['reasons'])
        code = ("import importlib.util, sys\n"
                "spec = importlib.util.spec_from_file_location('e', %r)\n"
                "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
                "res = m.check_bytes(open(%r, 'rb').read(), 'accept', 'v3')\n"
                "print(res['disposition'], any(n.endswith(('.workflow', '.observer')) for n in sys.modules),\n"
                "      any('publish_new' in n for n in sys.modules))\n") % (
            str(ENTRY), str(ROOT / '.cvf' / 'contracts' / 'v3' / 'examples' / 'ex04_pcn1_accepted_d4_complete.json'))
        proc = subprocess.run([sys.executable, '-B', '-I', '-c', code], cwd=self.project, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((proc.returncode, proc.stderr), (0, b''))
        self.assertEqual(proc.stdout.decode().split(), ['BLOCKED', 'False', 'False'])

    def test_frozen_example_is_never_pass_even_with_a_root(self):
        for name in ('ex01_pcn1_working_request.json', 'ex04_pcn1_accepted_d4_complete.json'):
            data = (ROOT / '.cvf' / 'contracts' / 'v3' / 'examples' / name).read_bytes()
            for phase in ('dispatch', 'effect', 'accept'):
                res = self.entry.check_bytes(data, phase, 'v3', project_root=self.project)
                with self.subTest(example=name[:4], phase=phase):
                    self.assert_not_pass(res)
                    self.assertIn('GRANT_INACTIVE', res['reasons'])


class StableSnapshot(Loop):
    """Corrective P-CN1: one task snapshot across the three phases, T2 bootstrap parents, and no task the owner cannot rebuild."""

    def loop(self, **over):
        """Plan with the caller rid, run dispatch and effect, publish with the same rid and request, then accept with the same task."""
        request = self.request(**over)
        task = pn.build_task(request, self.rid0)
        grant = self.grant(task)
        self.assertEqual(self.run_check(self.bundle(task, grant), 'dispatch')['disposition'], 'PASS')
        self.assertEqual(self.run_check(self.bundle(task, grant, self.effect(task, 'REQUEST')), 'effect')['disposition'], 'PASS')
        rid, prepared = self.publish(request, rid=self.rid0)
        self.assertEqual(pn.cj_dumps(prepared), pn.cj_dumps(task))
        bundle, _, _ = self.accept_bundle(rid, task)
        return task, bundle

    def test_working_and_output_zones_keep_one_snapshot(self):
        for label, over in (('working', {}), ('output', {'target': 'output/w-1/bao-cao.docx', 'content_use': ['internal_draft']})):
            with self.subTest(label):
                task, bundle = self.loop(**over)
                res = self.run_check(bundle, 'accept')
                self.assertEqual((res['disposition'], res['reasons']), ('PASS', []))
                self.assertEqual(self.gate(res, 'TOOL_SCOPE')['status'], 'MET')
                shutil.rmtree(os.path.join(self.project, '.agent', 'runtime', 'publish'))
                shutil.rmtree(os.path.join(self.project, 'working'), ignore_errors=True)
                shutil.rmtree(os.path.join(self.project, 'output'), ignore_errors=True)

    def test_a_prepared_snapshot_that_differs_from_the_planned_task_is_blocked(self):
        planned = pn.build_task(self.request(), self.rid0)
        other = self.request(main_interpretation='Một cách hiểu khác của yêu cầu')
        rid, prepared = self.publish(other, rid=self.rid0)
        self.assertEqual(prepared['task_id'], planned['task_id'])
        self.assertNotEqual(pn.cj_dumps(prepared), pn.cj_dumps(planned))
        bundle, _, _ = self.accept_bundle(rid, planned)
        res = self.run_check(bundle, 'accept')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['precondition_history'], 'NOT_MET')
        self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])
        # the other task is what was really published: the same rid with its own snapshot passes, so the block is about the mismatch only
        bundle_other, _, _ = self.accept_bundle(rid, prepared)
        self.assertEqual(self.run_check(bundle_other, 'accept')['disposition'], 'PASS')

    def test_a_task_the_owner_cannot_rebuild_is_blocked_in_every_phase_and_keeps_its_gate_diagnostics(self):
        extras = {
            'envelope': lambda t: t['envelope'].update(max_retries={'status': 'REQUESTED', 'value': 1}),
            'context_refs': lambda t: t.update(context_refs=[{'path': 'references/source-documents/team/quy-che-gia.pdf', 'digest': self.source_digest}]),
            'protected_targets': lambda t: t['effects'].update(protected_targets=['AGENTS.md']),
            'preservation': lambda t: t['effects'].update(preservation=[{'target': 'working/w-20261018-01/bao-cao-nhap.docx',
                                                                          'must_keep': 'tiêu đề', 'known_loss_state': 'NONE_KNOWN'}]),
        }
        for label, mutate in extras.items():
            task = self.planned_task()
            mutate(task)
            grant = self.grant(task, limits={'max_retries': 2}) if label == 'envelope' else self.grant(task)
            for phase, records in (('dispatch', (task, grant)), ('effect', (task, grant, self.effect(task, 'REQUEST')))):
                with self.subTest(label, phase=phase):
                    before = self.tree()
                    res = self.run_check(self.bundle(*records), phase)
                    self.assertEqual(self.tree(), before)
                    self.assert_not_pass(res)
                    self.assertEqual(len(res['gates']), 8, 'gate diagnostics are still computed')
                    self.assertEqual(self.gate(res, 'TOOL_SCOPE')['status'], 'UNSUPPORTED')
                    self.assertIn('TASK_NOT_OWNER_REPRESENTABLE', self.gate(res, 'TOOL_SCOPE')['reasons'])
                    self.assertIn('TASK_NOT_OWNER_REPRESENTABLE', res['reasons'])
                    self.assertEqual(self.gate(res, 'GRANT_SCOPE')['status'], 'MET', 'the other gates keep their own result')

    def test_accept_never_builds_another_task_for_one_the_owner_cannot_express(self):
        task = self.planned_task()
        task['envelope'] = {'role': 'main', 'max_retries': {'status': 'REQUESTED', 'value': 1}}
        grant = self.grant(task, limits={'max_retries': 2})
        self.assertEqual(self.run_check(self.bundle(task, grant), 'dispatch')['gates'][2]['status'], 'UNSUPPORTED')
        # the owner can only publish its own mapping: the published snapshot has no custom envelope and is a different task
        rid, prepared = self.publish(rid=self.rid0)
        self.assertNotEqual(pn.cj_dumps(prepared), pn.cj_dumps(task))
        for label, final in (('custom task', task), ('owner task', prepared)):
            bundle, _, _ = self.accept_bundle(rid, final)
            res = self.run_check(bundle, 'accept')
            with self.subTest(label):
                if final is task:
                    self.assert_not_pass(res)
                    self.assertIn('TASK_NOT_OWNER_REPRESENTABLE', res['reasons'])
                    self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['precondition_history'], 'NOT_MET')
                else:
                    self.assertEqual(res['disposition'], 'PASS', 'the snapshot the owner really wrote is still acceptable on its own')

    def test_the_rebuild_uses_pure_owner_functions_and_never_a_writer(self):
        task, grant = self.planned()
        owner = self.observer.load_owner()
        boom = mock.Mock(side_effect=AssertionError('the checker must not write'))
        with mock.patch.object(owner, 'publish', boom), mock.patch.object(owner, 'recover', boom), mock.patch.object(owner, 'discard_staged', boom):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        boom.assert_not_called()
        self.assertEqual(res['disposition'], 'PASS')
        self.assertIn('OWNER_BUILD_TASK_ROUNDTRIP_C1_PROJECTION', self.gate(res, 'TOOL_SCOPE')['limits'])

    def test_rebuild_failure_modes_are_closed(self):
        task, grant = self.planned()
        owner = self.observer.load_owner()
        with mock.patch.object(owner, 'build_task', side_effect=RuntimeError(MARKER)):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertNotIn(MARKER, json.dumps(res))
        self.assertIn('TASK_NOT_OWNER_REPRESENTABLE', res['reasons'])
        with mock.patch.object(self.observer, 'rebuild_task', return_value=('UNAVAILABLE', None)):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'TOOL_SCOPE')['status'], 'NOT_CHECKED')

    # ---- T2 precondition seen by the checker
    def test_a_root_without_bootstrap_parents_never_passes_dispatch_or_effect(self):
        task, grant = self.planned()
        for label, setup in (('no .agent', lambda: shutil.rmtree(os.path.join(self.project, '.agent'))),
                             ('no runtime', lambda: os.makedirs(os.path.join(self.project, '.agent')))):
            if label == 'no runtime':
                shutil.rmtree(os.path.join(self.project, '.agent'), ignore_errors=True)
            setup()
            for phase, records in (('dispatch', (task, grant)), ('effect', (task, grant, self.effect(task, 'REQUEST')))):
                with self.subTest(label, phase=phase):
                    before = self.tree()
                    res = self.run_check(self.bundle(*records), phase)
                    self.assertEqual(self.tree(), before, 'the checker does not create the missing parents')
                    self.assert_not_pass(res)
                    self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'NOT_MET')
                    self.assertIn('RUNTIME_PARENT_MISSING', res['reasons'])
                    self.assertEqual(res['route']['assumptions'][0]['status'], 'CLOSED_BY_OBSERVATION', 'the target is still observed absent')

    def test_an_unreported_runtime_precondition_is_not_checked_not_assumed(self):
        task, grant = self.planned()
        real = self.observer.observe

        def without_field(*args, **kwargs):
            out = real(*args, **kwargs)
            out['runtime_parents_ready'] = None
            return out
        with mock.patch.object(self.observer, 'observe', side_effect=without_field):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'NOT_CHECKED')
        self.assertIn('OBSERVATION_UNAVAILABLE', res['reasons'])

    def test_accept_does_not_need_the_precondition_once_the_evidence_exists(self):
        task, bundle = self.loop()
        res = self.run_check(bundle, 'accept')
        self.assertEqual(res['disposition'], 'PASS')
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'NOT_REQUIRED')


class GrantAndScope(Loop):
    def dispatch(self, task, grant, **kw):
        return self.run_check(self.bundle(task, grant, *kw.get('more', [])), 'dispatch')

    def test_grant_negatives(self):
        task = self.planned_task()
        cases = {
            'inactive': (self.grant(task, status='REVOKED'), 'GRANT_INACTIVE'),
            'example_flag': (self.grant(task, example_only=True, status='EXAMPLE_INACTIVE'), 'GRANT_INACTIVE'),
            'no_delete': (self.grant(task, scope={'task_classes': ['d'], 'operations': ['create_new'], 'tools': ['publish_new'],
                                                  'paths': ['working/', '.agent/runtime/publish/']}), 'GRANT_OUT_OF_SCOPE'),
            'wrong_role': (self.grant(task, subject={'roles': ['worker'], 'actor_ids': ['main']}), 'GRANT_OUT_OF_SCOPE'),
            'other_actor': (self.grant(task, subject={'roles': ['main'], 'actor_ids': ['someone-else']}), 'GRANT_OUT_OF_SCOPE'),
            'empty_actor_ids': (self.grant(task, subject={'roles': ['main'], 'actor_ids': []}), 'GRANT_OUT_OF_SCOPE'),
            'tool_missing': (self.grant(task, scope={'task_classes': ['d'], 'operations': ['create_new', 'delete'], 'tools': ['other_tool'],
                                                     'paths': ['working/', '.agent/runtime/publish/']}), 'GRANT_OUT_OF_SCOPE'),
            'runtime_not_covered': (self.grant(task, scope={'task_classes': ['d'], 'operations': ['create_new', 'delete'], 'tools': ['publish_new'],
                                                            'paths': ['working/']}), 'GRANT_OUT_OF_SCOPE'),
        }
        for label, (grant, reason) in cases.items():
            with self.subTest(label):
                res = self.dispatch(task, grant)
                self.assert_not_pass(res)
                self.assertEqual(res['disposition'], 'BLOCKED')
                self.assertIn(reason, res['reasons'])

    def test_user_confirmation_is_required_on_the_grant_record_too(self):
        task = self.planned_task()
        grant = self.grant(task)
        grant['issuer_ref']['attribution'] = {'source_class': 'MAIN_PROPOSAL', 'channel': 'MAIN_AUTHORED',
                                              'recorded_by': {'actor_id': 'main', 'role': 'main'}}
        res = self.dispatch(task, grant)
        self.assert_not_pass(res)
        self.assertTrue({'REF_CONFLICT', 'USER_CONFIRMATION_MISSING'} & set(res['reasons']), res['reasons'])

    def test_missing_ambiguous_and_conflicting_grants_do_not_pass(self):
        task = self.planned_task()
        res = self.run_check(self.bundle(task), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual((self.gate(res, 'GRANT_SCOPE')['status'], 'GRANT_MISSING' in res['reasons']), ('NOT_MET', True))
        twin = self.grant(task, grant_id='grant-2')
        res = self.run_check(self.bundle(task, self.grant(task), twin), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'GRANT_SCOPE')['status'], 'NOT_CHECKED')
        self.assertTrue({'REF_AMBIGUOUS', 'REF_CONFLICT'} & set(res['reasons']))

    def test_paths_cover_by_segment_not_by_string_prefix(self):
        task = self.planned_task()
        for paths in (['working-evil/', '.agent/runtime/publish/'], ['work/', '.agent/runtime/publish/'], ['working/w-20261018-01/bao-cao-nhap.docx', '.agent/runtime/publish/'],
                      ['working/*', '.agent/runtime/publish/'], ['working/', '.agent/runtime/publish-evil/'], ['working/', '.agent/runtime/']):
            grant = self.grant(task, scope={'task_classes': ['d'], 'operations': ['create_new', 'delete'], 'tools': ['publish_new'], 'paths': paths})
            res = self.dispatch(task, grant)
            with self.subTest(paths=paths):
                covers_runtime = paths[-1] == '.agent/runtime/'
                if covers_runtime:
                    self.assertEqual(res['disposition'], 'PASS', 'a broader grant path that is a segment prefix does cover the runtime folder')
                else:
                    self.assertEqual(res['disposition'], 'BLOCKED')
                    self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['lexical'], 'NOT_MET')

    def test_actor_of_the_effect_record_must_be_the_task_subject(self):
        task = self.planned_task()
        request = self.effect(task, 'REQUEST', actor={'actor_id': 'impostor', 'role': 'main'})
        res = self.run_check(self.bundle(task, self.grant(task), request), 'effect')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'GRANT_SCOPE')['status'], 'NOT_MET')

    def test_task_classes_are_not_semantically_checked_and_say_so(self):
        task, grant = self.planned()
        grant['scope']['task_classes'] = ['anything free text, never classified']
        res = self.dispatch(task, grant)
        self.assertEqual(res['disposition'], 'PASS')
        self.assertIn('TASK_CLASSES_NOT_CHECKED', self.gate(res, 'GRANT_SCOPE')['limits'])

    def test_shape_outside_the_one_file_flow_is_unsupported_not_downgraded(self):
        base = self.planned_task()
        grant = self.grant(base)

        def with_task(fn):
            t = copy.deepcopy(base)
            fn(t)
            return t

        variants = {
            'two_actions': with_task(lambda t: t['effects']['actions'].append(dict(t['effects']['actions'][0], targets=['working/x/other.docx']))),
            'other_tool': with_task(lambda t: t['effects']['actions'][0].update(tool='something_else')),
            'overwrite': with_task(lambda t: t['effects']['actions'][0].update(operation='overwrite')),
            'input_is_target': with_task(lambda t: t['inputs'].__setitem__(0, dict(t['inputs'][0], path=t['effects']['actions'][0]['targets'][0]))),
            'recipe': with_task(lambda t: t['effects']['actions'][0].update(recipe={'recipe_id': 'r', 'recipe_version': '1', 'acceptance_ref': {
                'ref_id': 'rec', 'kind': 'recipe_acceptance', 'locator': 'x', 'digest': 'sha256:' + '2' * 64, 'attribution': att()}})),
            'bad_task_id': with_task(lambda t: t.update(task_id='not-a-pcn1-id')),
            'two_grant_refs': with_task(lambda t: t['authority']['grant_refs'].append(dict(t['authority']['grant_refs'][0], ref_id='grant-2'))),
        }
        for label, task in variants.items():
            with self.subTest(label):
                data = json.dumps(self.bundle(task, grant)).encode()
                res = self.entry.check_bytes(data, 'dispatch', 'v3', project_root=self.project)
                self.assert_not_pass(res)
                self.assertIn(res['disposition'], ('UNSUPPORTED', 'DENY', 'BLOCKED'))
                self.assertEqual(res['gates'], [])
                self.assertIs(res['coverage']['gates_evaluated'], False)
                if label in ('other_tool', 'input_is_target', 'bad_task_id', 'two_grant_refs', 'overwrite'):
                    self.assertIn('P_CN1_SHAPE_UNSUPPORTED', res['reasons'])

    def test_known_loss_and_review_required_tasks_keep_their_route_obligations(self):
        task = self.planned_task()
        task['effects']['preservation'] = [{'target': task['effects']['actions'][0]['targets'][0], 'must_keep': 'formatting', 'known_loss_state': 'KNOWN_LOSS'}]
        res = self.dispatch(task, self.grant(task))
        self.assertEqual((res['disposition'], 'KNOWN_PRESERVATION_LOSS' in res['reasons']), ('DENY', True))
        task = self.planned_task(target='output/w-1/x.docx', content_use=['internal_draft'])
        task['effects']['actions'][0]['content_use'] = ['internal_draft', 'sign']
        res = self.dispatch(task, self.grant(task))
        self.assert_not_pass(res)
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', res['reasons'])

    def test_deferred_extra_review_field_is_refused_before_the_light_workflow(self):
        for phase in ('dispatch', 'effect'):
            with self.subTest(phase=phase):
                task = self.planned_task()
                task['effects']['extra_review_phases'] = ['PRE_EFFECT']
                records = [task, self.grant(task)]
                if phase == 'effect':
                    records.append(self.effect(task, 'REQUEST'))
                res = self.run_check(self.bundle(*records), phase)
                self.assert_not_pass(res)
                self.assertEqual((res['disposition'], res['reasons'], res['gates']), ('DENY', ['SCHEMA_INVALID'], []))


class EnvelopeGate(Loop):
    def case(self, limits, envelope):
        task = self.planned_task()
        task['envelope'] = dict({'role': 'main'}, **envelope)
        return self.run_check(self.bundle(task, self.grant(task, limits=limits)), 'dispatch')

    def test_envelope_arithmetic_is_declared_and_feeds_the_route(self):
        ok = self.case({'max_retries': 2, 'max_concurrency': 1}, {'max_retries': {'value': 2, 'status': 'REQUESTED'},
                                                                  'max_concurrency': {'value': 1, 'status': 'APPLIED'}})
        # The arithmetic diagnostic is kept, but the owner's build_task drops a custom envelope, so this task is not owner-representable and is never PASS.
        self.assertEqual((ok['disposition'], self.gate(ok, 'ENVELOPE')['status']), ('BLOCKED', 'MET'))
        self.assertEqual((self.gate(ok, 'TOOL_SCOPE')['status'], ok['reasons']), ('UNSUPPORTED', ['TASK_NOT_OWNER_REPRESENTABLE']))
        self.assertIn('ENVELOPE_DECLARED_NOT_HOST_OBSERVED', self.gate(ok, 'ENVELOPE')['limits'])
        over = self.case({'max_retries': 1}, {'max_retries': {'value': 3, 'status': 'REQUESTED'}})
        self.assertEqual((over['disposition'], self.gate(over, 'ENVELOPE')['status']), ('BLOCKED', 'NOT_MET'))
        self.assertIn('ENVELOPE_EXCEEDED', over['reasons'])
        self.assertIn('R-EXTERNAL', [r['row_id'] for r in over['route']['rows']], 'T from the gate selects the R-EXTERNAL obligations')
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', over['reasons'])

    def test_unmeasured_or_unknown_stays_u_and_is_never_green(self):
        cases = {
            'missing_field': ({'max_retries': 1}, {}),
            'unknown_status': ({'max_retries': 1}, {'max_retries': {'value': 0, 'status': 'UNKNOWN'}}),
            'unsupported_status': ({'max_concurrency': 1}, {'max_concurrency': {'value': 1, 'status': 'UNSUPPORTED'}}),
            'null_value': ({'max_retries': 1}, {'max_retries': {'value': None, 'status': 'REQUESTED'}}),
            'cost_unit_unknown': ({'cost_limit': '5 USD'}, {'cost_limit': {'value': '500 JPY', 'status': 'REQUESTED'}}),
        }
        for label, (limits, envelope) in cases.items():
            with self.subTest(label):
                res = self.case(limits, envelope)
                self.assert_not_pass(res)
                self.assertEqual(self.gate(res, 'ENVELOPE')['status'], 'NOT_CHECKED')
                self.assertIn('ENVELOPE_UNMEASURED', res['reasons'])
                self.assertEqual(res['route']['status'], 'UNRESOLVED', 'U is never turned into F')
                self.assertEqual(res['route']['rows'][0]['not_evaluated_conditions'], ['ENVELOPE_EXCEEDED'])

    def test_a_non_integer_envelope_number_is_outside_the_canonical_domain_and_never_measured(self):
        res = self.case({'max_retries': 1}, {'max_retries': {'value': 0.5, 'status': 'REQUESTED'}})
        self.assertEqual((res['disposition'], res['reasons'], res['gates']), ('UNSUPPORTED', ['UNSUPPORTED_BINDING_PART'], []))

    def test_equal_cost_strings_and_time_limits(self):
        res = self.case({'cost_limit': '5 USD'}, {'cost_limit': {'value': '5 USD', 'status': 'REQUESTED'}})
        self.assertEqual((res['disposition'], self.gate(res, 'ENVELOPE')['status'], res['reasons']), ('BLOCKED', 'MET', ['TASK_NOT_OWNER_REPRESENTABLE']))
        self.assertIn('COST_LIMIT_EQUAL_STRINGS_ONLY', self.gate(res, 'ENVELOPE')['limits'])
        res = self.case({'expires_at': '2030-01-01T00:00:00Z'}, {})
        self.assertEqual(self.gate(res, 'ENVELOPE')['status'], 'UNSUPPORTED')
        self.assertIn('EXPIRES_AT_UNSUPPORTED', res['reasons'])
        self.assert_not_pass(res)

    def test_envelope_role_must_match_the_subject(self):
        task = self.planned_task()
        task['envelope'] = {'role': 'worker'}
        res = self.run_check(self.bundle(task, self.grant(task)), 'dispatch')
        self.assertEqual(self.gate(res, 'ENVELOPE')['status'], 'NOT_MET')
        self.assertIn('ENVELOPE_ROLE_MISMATCH', res['reasons'])

    def test_unresolved_profile_ref_keeps_envelope_unknown_and_blocks(self):
        res = self.case({}, {'profile_ref': 'profiles/a.json'})
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'ENVELOPE')['status'], 'UNSUPPORTED')
        self.assertIn('PROFILE_UNSUPPORTED', res['reasons'])
        self.assertEqual(res['route']['status'], 'UNRESOLVED')
        self.assertIn('R-EXTERNAL', [row['row_id'] for row in res['route']['rows']])
        self.assertIn('PROFILE_NOT_EVALUATED', self.gate(res, 'ENVELOPE')['limits'])


class ObserverGates(Loop):
    def test_unavailable_observation_is_not_the_same_as_absent(self):
        task, grant = self.planned()
        owner = self.observer.load_owner()
        with mock.patch.object(owner, 'volume_supported', return_value=(False, {'fs': 'FAT32', 'local': True, 'drive_type': 3, 'cloud_attributes': False})):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'UNSUPPORTED')
        self.assertIn('OBSERVATION_UNAVAILABLE', res['reasons'])
        self.assertEqual(res['route']['assumptions'][0]['status'], 'OPEN', 'no observation, so A-NEW_TARGET is not closed')
        self.assertIs(res['coverage']['target_existence_observed'], False)

    def test_owner_exception_is_unavailable_and_never_echoed(self):
        task, grant = self.planned()
        owner = self.observer.load_owner()
        with mock.patch.object(owner, 'observe', side_effect=RuntimeError(MARKER)):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertNotIn(MARKER, json.dumps(res))
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'NOT_CHECKED')

    def test_linked_parent_blocks_instead_of_pretending_the_target_is_absent(self):
        outside = tempfile.mkdtemp(prefix='law-wf-outside-')
        self.addCleanup(shutil.rmtree, outside, True)
        link = os.path.join(self.project, 'working')
        r = subprocess.run(['cmd', '/c', 'mklink', '/J', link, outside], capture_output=True, text=True)
        if r.returncode != 0:
            self.skipTest('cannot create a junction here')
        self.addCleanup(os.rmdir, link)
        task, grant = self.planned()
        res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual(os.listdir(outside), [], 'nothing is written through the junction')
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['observed_at_time'], 'NOT_CHECKED')

    def test_pin_mismatch_at_dispatch_and_historical_pin_at_accept(self):
        task, grant = self.planned()
        with mock.patch.object(self.observer, 'entrypoint_sha256', return_value='0' * 64):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'TOOL_SCOPE')['status'], 'NOT_MET')
        self.assertIn('ENTRYPOINT_PIN_MISMATCH', res['reasons'])
        # at accept the current script hash does not replace the historical pin recorded in prepared
        rid, final = self.publish()
        bundle, _, _ = self.accept_bundle(rid, final)
        with mock.patch.object(self.observer, 'entrypoint_sha256', return_value='0' * 64):
            res = self.run_check(bundle, 'accept')
        self.assertEqual(res['disposition'], 'PASS')
        # a tampered historical pin (valid canonical evidence, wrong pin) is NOT_MET
        path = pn._evidence_path(self.project, rid, 'prepared')
        prepared = pn.cj_loads(slurp(path))
        prepared['entrypoint_sha256'] = 'sha256:' + '0' * 64
        with open(path, 'wb') as f:
            f.write(pn.cj_dumps(prepared))
        res = self.run_check(bundle, 'accept')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'TOOL_SCOPE')['status'], 'NOT_MET')
        self.assertIn('ENTRYPOINT_PIN_MISMATCH', res['reasons'])

    def test_rid_evidence_already_present_blocks_effect_and_dispatch(self):
        os.makedirs(pn._publish_dir(self.project))
        with open(pn._evidence_path(self.project, self.rid0, 'prepared'), 'wb') as f:
            f.write(b'')
        task, grant = self.planned()
        res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assert_not_pass(res)
        self.assertIn('RID_EVIDENCE_PRESENT', res['reasons'])
        self.assertEqual(res['route']['assumptions'][0]['status'], 'OPEN')

    def test_owner_code_comes_from_the_law_tree_never_from_the_root(self):
        tools = os.path.join(self.project, 'tools')
        os.makedirs(tools)
        canary = os.path.join(self.project, 'CANARY.txt')
        for name in ('publish_new.py', 'transaction.py', 'result_schema.py'):
            with open(os.path.join(tools, name), 'w') as f:
                f.write("open(%r, 'w').write('executed')\nraise SystemExit(99)\n" % canary)
        cvf = os.path.join(self.project, '.cvf', 'rules', 'v3')
        os.makedirs(cvf)
        with open(os.path.join(cvf, 'ROUTING_POLICY.json'), 'w') as f:
            f.write('{"hostile": true}')
        task, grant = self.planned()
        res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assertEqual(res['disposition'], 'PASS')
        self.assertFalse(os.path.exists(canary), 'root content must never be executed')
        self.assertEqual(self.observer.owner_path().resolve(), (ROOT / 'tools' / 'publish_new.py').resolve())
        self.assertEqual(res['owners']['policy_sha256'], hashlib.sha256((ROOT / '.cvf' / 'rules' / 'v3' / 'ROUTING_POLICY.json').read_bytes()).hexdigest())

    def test_observer_never_calls_a_writer_function(self):
        task, grant = self.planned()
        rid, final = self.publish()
        accept, _, _ = self.accept_bundle(rid, final)
        owner = self.observer.load_owner()
        boom = mock.Mock(side_effect=AssertionError('the checker must not write'))
        before = self.tree()
        with mock.patch.object(owner, 'publish', boom), mock.patch.object(owner, 'recover', boom), mock.patch.object(owner, 'discard_staged', boom):
            self.assertEqual(self.run_check(accept, 'accept')['disposition'], 'PASS')
            dispatch = self.run_check(self.bundle(task, grant), 'dispatch')
            self.assertEqual(dispatch['gates'][1]['subchecks']['observed_at_time'], 'NOT_MET')
            self.assertIn('TARGET_EXISTS_OBSERVED', dispatch['reasons'])
        boom.assert_not_called()
        self.assertEqual(self.tree(), before)

    def test_an_unexpected_workflow_failure_is_fail_closed_without_a_traceback_or_message(self):
        task, grant = self.planned()
        workflow = importlib.import_module(self.entry.PACKAGE_NAME + '.workflow')
        with mock.patch.object(workflow.Workflow, '_g_envelope', side_effect=RuntimeError(MARKER)):
            res = self.run_check(self.bundle(task, grant), 'dispatch')
        self.assertEqual((res['disposition'], 'WORKFLOW_ERROR' in res['reasons'], res['gates']), ('UNSUPPORTED', True, []))
        self.assertNotIn(MARKER, json.dumps(res))
        self.assertIs(res['coverage']['gates_evaluated'], False)
        self.assertEqual(res['assurance_level'], 'UNVERIFIED')

    def test_the_root_is_data_only_even_when_it_looks_like_a_law_tree(self):
        self.assertEqual(self.observer.owner_path().parents[1], ROOT)
        self.assertFalse(str(self.project).startswith(str(ROOT)))


class EffectGates(Loop):
    def test_effect_needs_exactly_one_request_record_with_matching_binding(self):
        task, grant = self.planned()
        res = self.run_check(self.bundle(task, grant), 'effect')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'BINDING')['status'], 'NOT_CHECKED')
        self.assertIn('EFFECT_RECORD_MISSING', res['reasons'])
        one, two = self.effect(task, 'REQUEST'), self.effect(task, 'REQUEST', effect_id='eff-req-2')
        res = self.run_check(self.bundle(task, grant, one, two), 'effect')
        self.assert_not_pass(res)
        self.assertIn('DUPLICATE_EFFECT_RECORD', res['reasons'])

    def test_stale_binding_and_declared_route_mismatch_and_outputs_on_a_request(self):
        task, grant = self.planned()
        stale = self.effect(task, 'REQUEST')
        stale['binding']['accepted_task_digest'] = 'sha256:' + '0' * 64
        res = self.run_check(self.bundle(task, grant, stale), 'effect')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'BINDING')['status'], 'NOT_MET')
        self.assertIn('BINDING_MISMATCH', res['reasons'])
        wrong_route = self.effect(task, 'REQUEST', routing={'policy_version': 'law.cvf.routing/3', 'matched_rows': ['R-READ_DRAFT', 'R-MUTATION'],
                                                            'required_review_phases': []})
        res = self.run_check(self.bundle(task, grant, wrong_route), 'effect')
        self.assert_not_pass(res)
        self.assertIn('ROUTE_DECLARED_MISMATCH', res['reasons'])
        with_outputs = self.effect(task, 'REQUEST')
        with_outputs['binding']['outputs'] = [{'path': 'working/x.docx', 'digest': 'sha256:' + '3' * 64, 'role': 'ACTUAL_BYTES'}]
        res = self.run_check(self.bundle(task, grant, with_outputs), 'effect')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'BINDING')['status'], 'NOT_MET')

    def test_changed_or_missing_input_blocks_the_effect(self):
        task, grant = self.planned()
        request = self.effect(task, 'REQUEST')
        with open(self.source, 'wb') as f:
            f.write(b'%PDF changed after the drafting tool read it')
        res = self.run_check(self.bundle(task, grant, request), 'effect')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'INPUT_REVISION')['status'], 'NOT_MET')
        self.assertIn('INPUT_CHANGED_SINCE_READ', res['reasons'])
        os.remove(self.source)
        res = self.run_check(self.bundle(task, grant, request), 'effect')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'INPUT_REVISION')['status'], 'NOT_CHECKED')
        self.assertIn('OBSERVATION_UNAVAILABLE', res['reasons'])

    def test_a_receipt_does_not_open_the_effect_phase(self):
        rid, final = self.publish()
        bundle, artifacts, receipt = self.accept_bundle(rid, final)
        res = self.run_check(bundle, 'effect')
        self.assert_not_pass(res)  # the target exists now and no REQUEST record belongs to this phase
        self.assertIn('TARGET_EXISTS_OBSERVED', res['reasons'])


class AcceptGates(Loop):
    def setUp(self):
        super().setUp()
        self.rid, self.final = self.publish()
        self.bundle_ok, self.artifacts, self.receipt = self.accept_bundle(self.rid, self.final)

    def accept(self, mutate=None):
        bundle = copy.deepcopy(self.bundle_ok)
        if mutate:
            mutate(bundle['records'])
        return self.run_check(bundle, 'accept')

    def rec(self, records, rtype, stage=None):
        return [r for r in records if r['record_type'] == rtype and (stage is None or r.get('stage') == stage)][0]

    def test_baseline_passes(self):
        self.assertEqual(self.accept()['disposition'], 'PASS')

    def test_planned_task_without_evidence_has_no_history(self):
        planned = self.planned_task()
        artifacts = self.artifacts
        bundle = self.bundle(planned, self.grant(planned), self.effect(planned, 'OUTCOME', artifacts, self.receipt), self.result(planned, artifacts))
        res = self.run_check(bundle, 'accept')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['precondition_history'], 'NOT_CHECKED')
        self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])

    def test_a_request_record_of_the_planned_task_cannot_ride_along_into_accept(self):
        planned = self.planned_task()
        res = self.accept(lambda records: records.append(self.effect(planned, 'REQUEST')))
        self.assert_not_pass(res)
        self.assertIn('BINDING_INCOMPLETE', res['reasons'], 'its task is not in the bundle: it proves nothing about the final task')

    def test_receipt_problems(self):
        def drop(records):
            del self.rec(records, 'effect', 'OUTCOME')['receipt_ref']

        def wrong_digest(records):
            self.rec(records, 'effect', 'OUTCOME')['receipt_ref']['digest'] = 'sha256:' + '0' * 64

        def wrong_locator(records):
            self.rec(records, 'effect', 'OUTCOME')['receipt_ref']['locator'] = '.agent/runtime/publish/' + '0' * 32 + '.published.json'

        def self_declared(records):
            self.rec(records, 'effect', 'OUTCOME')['receipt_ref']['attribution'] = {
                'source_class': 'MAIN_PROPOSAL', 'channel': 'MAIN_AUTHORED', 'recorded_by': {'actor_id': 'main', 'role': 'main'}}

        for fn in (drop, wrong_digest, wrong_locator, self_declared):
            with self.subTest(fn.__name__):
                res = self.accept(fn)
                self.assert_not_pass(res)
                self.assertEqual(self.gate(res, 'ACTUAL_OUTCOME')['status'] in ('NOT_MET', 'NOT_CHECKED'), True)
                self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])

    def test_history_missing_corrupt_or_multiple(self):
        pub = pn._evidence_path(self.project, self.rid, 'published')
        raw = slurp(pub)
        os.remove(pub)
        res = self.accept()
        self.assert_not_pass(res)
        self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])
        self.assertEqual(self.gate(res, 'ACTUAL_OUTCOME')['status'], 'NOT_CHECKED')
        with open(pub, 'wb') as f:
            f.write(raw + b' ')  # not canonical: hash of the receipt would not even match
        res = self.accept()
        self.assert_not_pass(res)
        self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])
        with open(pub, 'wb') as f:
            f.write(raw)
        self.assertEqual(self.accept()['disposition'], 'PASS')
        with open(pn._evidence_path(self.project, self.rid, 'conflict'), 'wb') as f:
            f.write(pn.cj_dumps(dict(pn._header(self.rid, 'CONFLICT'), reason='TARGET_EXISTS')))
        res = self.accept()
        self.assert_not_pass(res)
        self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])
        os.remove(pn._evidence_path(self.project, self.rid, 'prepared'))
        res = self.accept()
        self.assert_not_pass(res)

    def test_snapshot_must_match_the_current_task(self):
        def other_requirement(records):
            task = self.rec(records, 'task')
            task['acceptance']['requirements'][0]['statement'] = 'A different statement'
            for rtype, stage in (('effect', 'OUTCOME'), ('result', None)):
                self.rec(records, rtype, stage)['binding'] = self.binding(task, self.artifacts)
            self.rec(records, 'result')['user_acceptance'] = self.acceptance(task, self.artifacts)

        res = self.accept(other_requirement)
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['precondition_history'], 'NOT_MET')
        self.assertIn('PRECONDITION_PROOF_MISSING', res['reasons'])

    def test_current_bytes_must_equal_the_published_bytes_and_identity(self):
        target = os.path.join(self.project, *self.final['effects']['actions'][0]['targets'][0].split('/'))
        original = slurp(target)
        with open(target, 'ab') as f:
            f.write(b'edited later')
        res = self.accept()
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'ACTUAL_OUTCOME')['status'], 'NOT_MET')
        self.assertIn('CHANGED_AFTER_PUBLISH', res['reasons'])
        with open(target, 'wb') as f:
            f.write(original)
        self.assertEqual(self.accept()['disposition'], 'PASS', 'restoring the bytes in place keeps the same file object')
        os.remove(target)
        with open(target, 'wb') as f:
            f.write(original)
        res = self.accept()
        self.assert_not_pass(res)
        self.assertIn('CHANGED_AFTER_PUBLISH', res['reasons'], 'identical bytes under a different file object are not the published object')
        os.remove(target)
        res = self.accept()
        self.assertIn('CHANGED_AFTER_PUBLISH', res['reasons'])
        self.assert_not_pass(res)

    def test_input_changed_after_publish_blocks_accept_even_when_history_matches(self):
        with open(self.source, 'wb') as f:
            f.write(b'%PDF edited long after publishing')
        res = self.accept()
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'INPUT_REVISION')['status'], 'NOT_MET')
        self.assertIn('INPUT_CHANGED_SINCE_READ', res['reasons'])
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['precondition_history'], 'MET')
        self.assertIn('HISTORICAL_PUBLISH_INPUTS_CHECKED', self.gate(res, 'INPUT_REVISION')['limits'])

    def test_missing_current_input_blocks_accept_even_when_history_matches(self):
        os.remove(self.source)
        res = self.accept()
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'INPUT_REVISION')['status'], 'NOT_CHECKED')
        self.assertIn('OBSERVATION_UNAVAILABLE', res['reasons'])
        self.assertEqual(self.gate(res, 'PATH_SCOPE')['subchecks']['precondition_history'], 'MET')

    def test_artifact_claims_must_equal_the_published_bytes_exactly(self):
        other = [{'path': self.artifacts[0]['path'], 'digest': 'sha256:' + '4' * 64, 'role': 'ACTUAL_BYTES'}]
        moved = [{'path': 'working/w-20261018-01/other.docx', 'digest': self.artifacts[0]['digest'], 'role': 'ACTUAL_BYTES'}]
        for label, artifacts in (('digest', other), ('path', moved), ('extra', self.artifacts + moved), ('none', [])):
            for where in ('outcome', 'result'):
                def mutate(records, artifacts=artifacts, where=where):
                    task = self.rec(records, 'task')
                    if where == 'outcome':
                        out = self.rec(records, 'effect', 'OUTCOME')
                        out['outcome']['artifacts'] = copy.deepcopy(artifacts)
                        out['binding'] = self.binding(task, artifacts)
                    else:
                        res = self.rec(records, 'result')
                        res['artifacts'] = copy.deepcopy(artifacts)
                        res['binding'] = self.binding(task, artifacts)
                with self.subTest(label=label, where=where):
                    res = self.accept(mutate)
                    self.assert_not_pass(res)
                    self.assertTrue({'OPERATION_MISMATCH', 'BINDING_MISMATCH', 'USER_ACCEPTANCE_STALE'} & set(res['reasons']), res['reasons'])

    def test_result_must_report_the_performed_action_and_a_failed_outcome_is_not_applied(self):
        def no_actions(records):
            del self.rec(records, 'result')['actions_performed']

        def other_action(records):
            self.rec(records, 'result')['actions_performed'][0]['targets'] = ['working/w-20261018-01/else.docx']

        def not_applied(records):
            self.rec(records, 'effect', 'OUTCOME')['outcome']['status'] = 'PARTIAL'

        for fn, reason in ((no_actions, 'ACTION_UNREPORTED'), (other_action, 'OPERATION_MISMATCH'), (not_applied, 'ACTION_INCOMPLETE')):
            with self.subTest(fn.__name__):
                res = self.accept(fn)
                self.assert_not_pass(res)
                self.assertIn(reason, res['reasons'])

    def test_duplicate_or_missing_records_at_accept(self):
        res = self.accept(lambda records: records.pop(2))
        self.assert_not_pass(res)
        self.assertIn('OUTCOME_RECORD_MISSING', res['reasons'])
        res = self.accept(lambda records: records.pop(3))
        self.assert_not_pass(res)
        self.assertIn('RESULT_RECORD_MISSING', res['reasons'])
        res = self.accept(lambda records: records.append(dict(copy.deepcopy(records[3]), result_id='pcn1-r-second')))
        self.assert_not_pass(res)
        self.assertIn('DUPLICATE_RESULT_RECORD', res['reasons'])
        res = self.accept(lambda records: records.append(dict(copy.deepcopy(records[2]), effect_id='eff-out-2')))
        self.assert_not_pass(res)
        self.assertIn('DUPLICATE_EFFECT_RECORD', res['reasons'])

    def test_d4_missing_incomplete_and_stale(self):
        task = self.final
        res = self.run_check(self.accept_bundle(self.rid, self.final, acceptance=False)[0], 'accept')
        self.assert_not_pass(res)
        self.assertEqual(self.gate(res, 'REQUIREMENTS')['status'], 'NOT_CHECKED')
        self.assertIn('EVIDENCE_NOT_VERIFIED', res['reasons'])
        stale_digest = 'sha256:' + '6' * 64
        other_artifact = [{'path': self.artifacts[0]['path'], 'digest': 'sha256:' + '7' * 64, 'role': 'ACTUAL_BYTES'}]

        def ua(**over):
            def mutate(records):
                self.rec(records, 'result')['user_acceptance'] = self.acceptance(task, self.artifacts, **over)
            return mutate

        incomplete = self.accept(ua(accepted_requirements=['REQ-1']))
        self.assert_not_pass(incomplete)
        self.assertEqual(self.gate(incomplete, 'REQUIREMENTS')['status'], 'NOT_CHECKED')
        self.assertIn('USER_ACCEPTANCE_INCOMPLETE', incomplete['reasons'])
        stales = {'task_digest': ua(accepted_task_digest=stale_digest), 'task_id': ua(task_id='pcn1-' + '0' * 32), 'revision': ua(task_revision=2),
                  'result_id': ua(result_id='pcn1-r-other'), 'artifact': ua(accepted_artifacts=other_artifact),
                  'unknown_requirement': ua(accepted_requirements=['REQ-1', 'REQ-2', 'REQ-9'])}
        for label, mutate in stales.items():
            with self.subTest(label):
                res = self.accept(mutate)
                self.assert_not_pass(res)
                self.assertEqual(self.gate(res, 'REQUIREMENTS')['status'], 'NOT_MET')
                self.assertIn('USER_ACCEPTANCE_STALE', res['reasons'])

    def test_d4_is_declared_not_semantic_and_a_higher_claim_is_refused(self):
        res = self.accept()
        gate = self.gate(res, 'REQUIREMENTS')
        self.assertEqual(gate['status'], 'USER_ACCEPTED_DECLARED')
        self.assertIn('SEMANTIC_NOT_VERIFIED', gate['limits'])
        self.assertIs(res['coverage']['requirements_semantic_verified'], False)

        def higher(records):
            self.rec(records, 'result')['acceptance_states'].append('ACCEPTED_FOR_INTEGRATION')
            for item in self.rec(records, 'result')['requirements']:
                item['status'] = 'MET'

        res = self.accept(higher)
        self.assert_not_pass(res)
        self.assertIn('ACCEPTANCE_CLAIM_NOT_SUPPORTED', res['reasons'])

    def test_a_mandatory_requirement_reported_not_met_blocks(self):
        for status in ('NOT_MET', 'MISSING', 'BLOCKED'):
            with self.subTest(status=status):
                def unmet(records):
                    self.rec(records, 'result')['requirements'][0]['status'] = status
                res = self.accept(unmet)
                self.assert_not_pass(res)
                self.assertIn('MANDATORY_REQUIREMENT_NOT_MET', res['reasons'])

    def test_user_authored_file_channel_is_not_enough_for_acceptance(self):
        def file_channel(records):
            self.rec(records, 'result')['user_acceptance']['ref']['attribution']['channel'] = 'USER_AUTHORED_FILE'
        res = self.accept(file_channel)
        self.assert_not_pass(res)  # the schema refuses the channel before any gate runs
        self.assertEqual(res['disposition'], 'DENY')

    def test_silence_grant_or_receipt_are_not_acceptance(self):
        res = self.run_check(self.accept_bundle(self.rid, self.final, acceptance=False)[0], 'accept')
        self.assertNotEqual(res['disposition'], 'PASS')
        self.assertEqual(self.gate(res, 'ACTUAL_OUTCOME')['status'], 'MET', 'the receipt and bytes are fine, the acceptance still is not')
        self.assertEqual(self.gate(res, 'REQUIREMENTS')['status'], 'NOT_CHECKED')

    def test_cli_runs_from_another_cwd_and_exit_codes_follow_the_disposition(self):
        scratch = tempfile.mkdtemp(prefix='law-wf-cwd-')
        self.addCleanup(shutil.rmtree, scratch, True)
        path = os.path.join(scratch, 'bundle.json')
        with open(path, 'w') as f:
            json.dump(self.bundle_ok, f)
        base = [sys.executable, '-B', '-I', str(ENTRY), '--contract', 'v3', '--phase', 'accept']
        proc = subprocess.run(base + ['--root', self.project, path], cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((proc.returncode, proc.stderr), (0, b''))
        res = json.loads(proc.stdout)
        self.assertEqual((res['disposition'], res['selection'], res['implementation_stage']), ('PASS', 'CLI_EXPLICIT', 'P_CN1_ONE_FILE'))
        self.assertEqual(res, dict(self.run_check(self.bundle_ok, 'accept'), selection='CLI_EXPLICIT'))
        text = subprocess.run(base + ['--root', self.project, '--format', 'text', path], cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(text.returncode, 0)
        self.assertIn('gate: REQUIREMENTS status=USER_ACCEPTED_DECLARED', text.stdout.decode())
        os.remove(pn._evidence_path(self.project, self.rid, 'published'))
        blocked = subprocess.run(base + ['--root', self.project, path], cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(blocked.returncode, 1)
        self.assertEqual(json.loads(blocked.stdout)['disposition'], 'BLOCKED')


class CliAndApi(Loop):
    def run_cli(self, *args):
        scratch = tempfile.mkdtemp(prefix='law-wf-cli-')
        self.addCleanup(shutil.rmtree, scratch, True)
        task, grant = self.planned()
        path = os.path.join(scratch, 'b.json')
        with open(path, 'w') as f:
            json.dump(self.bundle(task, grant), f)
        return subprocess.run([sys.executable, '-B', '-I', str(ENTRY), '--contract', 'v3', '--phase', 'dispatch'] + list(args) + [path],
                              cwd=scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_root_must_exist_and_is_never_echoed(self):
        secret = os.path.join(self.project, MARKER + '-missing')
        proc = self.run_cli('--root', secret)
        self.assertEqual(proc.returncode, 2)
        out = json.loads(proc.stdout)
        self.assertEqual((out['disposition'], out['init_error'], out['reasons']), ('UNSUPPORTED', True, ['ROOT_UNUSABLE']))
        self.assertNotIn(MARKER, proc.stdout.decode())
        self.assertNotIn(self.project, proc.stdout.decode())
        self.assertEqual(out['implementation_stage'], 'P_CN1_ONE_FILE')

    def test_root_given_twice_or_empty_is_a_usage_error_and_no_injection_options_exist(self):
        for args in (['--root', self.project, '--root', self.project], ['--root', ''], ['--owner', 'x'], ['--facts', 'x'], ['--observer', 'x'],
                     ['--policy', 'x'], ['--schema', 'x'], ['--basis', 'x'], ['--trust', 'x']):
            with self.subTest(args=args):
                proc = self.run_cli(*args)
                self.assertEqual((proc.returncode, proc.stdout), (2, b''))

    def test_api_has_no_injection_path(self):
        params = inspect.signature(self.entry.check_bytes).parameters
        self.assertEqual(list(params), ['data', 'phase', 'contract', 'project_root'])
        self.assertEqual(params['project_root'].kind, inspect.Parameter.KEYWORD_ONLY)
        for bad in (123, b'x', ['x'], ''):
            with self.assertRaises(TypeError):
                self.entry.check_bytes(b'{}', 'dispatch', 'v3', project_root=bad)
        with self.assertRaises(TypeError):
            self.entry.check_bytes(b'{}', 'dispatch', 'v3', 'positional-root')
        self.assertFalse([n for n in dir(self.entry) if n in ('check_records', 'check_with_facts')])

    def test_writer_and_policy_pins_are_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT / 'tools' / 'publish_new.py').read_bytes()).hexdigest(), WRITER_PIN)
        policy = json.loads((ROOT / '.cvf' / 'rules' / 'v3' / 'ROUTING_POLICY.json').read_text(encoding='utf-8'))
        self.assertEqual(policy['owner_protocols'][0]['entrypoint_sha256'], 'sha256:' + WRITER_PIN)

    def test_bundle_that_fails_structure_with_a_root_still_reports_the_stage(self):
        res = self.entry.check_bytes(b'{"not": "a record"}', 'dispatch', 'v3', project_root=self.project)
        self.assertEqual((res['implementation_stage'], res['gates']), ('P_CN1_ONE_FILE', []))
        self.assertNotEqual(res['disposition'], 'PASS')
        self.assertIsNone(res['phase_scope'])


class RoutingExternal(Loop):
    """`routing.evaluate_task(..., external)`: only the workflow may supply T/F/U for ENVELOPE_EXCEEDED and the observer-closed assumption."""

    def route(self, phase, external=None):
        routing = importlib.import_module(self.entry.PACKAGE_NAME + '.routing')
        return routing.evaluate_task(self.planned_task(), routing.load_route_policy(self.owners.policy_bytes), phase, external)

    def test_default_is_unchanged_u_and_open(self):
        res = self.route('dispatch')
        self.assertEqual((res.status, res.rows[0]['not_evaluated_conditions']), ('UNRESOLVED', ['ENVELOPE_EXCEEDED']))
        self.assertEqual(res.assumptions[0]['status'], 'OPEN')

    def test_f_and_the_closed_assumption_give_resolved_only_in_dispatch_and_effect(self):
        for phase in ('dispatch', 'effect'):
            res = self.route(phase, {'envelope_exceeded': 'F', 'closed_assumptions': ('A-NEW_TARGET',)})
            self.assertEqual((res.status, res.matched, res.blocked, res.review_phases), ('RESOLVED', ('R-READ_DRAFT',), [], ()))
        res = self.route('accept', {'envelope_exceeded': 'F', 'closed_assumptions': ('A-NEW_TARGET',)})
        self.assertEqual((res.status, res.assumptions[0]['status']), ('RESOLVED', 'NOT_APPLICABLE_IN_PHASE'))

    def test_f_alone_leaves_the_assumption_open_and_u_or_t_never_resolve(self):
        res = self.route('dispatch', {'envelope_exceeded': 'F'})
        self.assertEqual((res.status, 'ROUTE_ASSUMPTION_OPEN' in res.blocked), ('CONDITIONAL', True))
        self.assertEqual(self.route('dispatch', {'envelope_exceeded': 'U', 'closed_assumptions': ('A-NEW_TARGET',)}).status, 'UNRESOLVED')
        res = self.route('dispatch', {'envelope_exceeded': 'T', 'closed_assumptions': ('A-NEW_TARGET',)})
        self.assertIn('R-EXTERNAL', res.matched)
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', res.blocked)

    def test_unknown_assumption_ids_and_bad_values_are_refused(self):
        res = self.route('dispatch', {'envelope_exceeded': 'F', 'closed_assumptions': ('A-SOMETHING-ELSE',)})
        self.assertEqual(res.assumptions[0]['status'], 'OPEN')
        for bad in ({'envelope_exceeded': 'X'}, 'F'):
            with self.assertRaises((ValueError, TypeError)):
                self.route('dispatch', bad)


class OwnerLoadingReview(Loop):
    def test_owner_pin_uses_fixed_policy_bytes_not_a_mutable_policy_view(self):
        with mock.patch.dict(self.owners.policy['owner_protocols'][0], {'entrypoint_sha256': 'sha256:' + '0' * 64}):
            self.assertEqual(self.observer.entrypoint_sha256(), WRITER_PIN)

    def test_owner_load_restores_the_exact_host_search_path(self):
        before = list(sys.path)
        with mock.patch.dict(self.observer._cache, {}, clear=True):
            owner = self.observer.load_owner()
            self.assertEqual(sys.path, before)
            self.assertEqual(Path(owner.__file__).resolve(), (ROOT / 'tools' / 'publish_new.py').resolve())
            self.assertEqual(self.observer.entrypoint_sha256(), WRITER_PIN)

    def test_an_unrelated_cached_dependency_is_refused_before_owner_execution(self):
        for name in ('transaction', 'result_schema'):
            foreign = type('ForeignModule', (), {'__file__': os.path.join(self.project, name + '.py')})()
            before = list(sys.path)
            with self.subTest(name=name), mock.patch.dict(self.observer._cache, {}, clear=True), \
                    mock.patch.dict(sys.modules, {name: foreign}):
                with self.assertRaises(ImportError):
                    self.observer.load_owner()
                self.assertFalse(self.observer.observe(self.project, self.request()['target'])['available'])
            self.assertEqual(sys.path, before)

    def test_unpinned_owner_bytes_are_never_executed(self):
        original_read = Path.read_bytes
        owner_path = self.observer.owner_path()

        def changed(path):
            return b'raise AssertionError("unpinned owner executed")\n' if path == owner_path else original_read(path)

        with mock.patch.dict(self.observer._cache, {}, clear=True), \
                mock.patch.object(Path, 'read_bytes', autospec=True, side_effect=changed), \
                mock.patch.object(self.observer.importlib.util, 'module_from_spec', side_effect=AssertionError('owner execution attempted')):
            with self.assertRaises(ImportError):
                self.observer.load_owner()
            self.assertIsNone(self.observer.entrypoint_sha256())

    def test_cached_owner_is_not_used_when_current_source_loses_its_pin(self):
        self.observer.load_owner()
        original_read = Path.read_bytes
        owner_path = self.observer.owner_path()

        def changed(path):
            return b'# changed owner bytes\n' if path == owner_path else original_read(path)

        with mock.patch.object(Path, 'read_bytes', autospec=True, side_effect=changed):
            self.assertIsNone(self.observer.entrypoint_sha256())
            self.assertFalse(self.observer.observe(self.project, self.request()['target'])['available'])


if __name__ == '__main__':
    unittest.main()
