"""G-02-C2/S3-C/D: kiểm checker v3 candidate sau khi nối binding và routing (BINDING_ROUTING_ONLY) / checks the v3 candidate after binding and routing are wired.

Kiểm entrypoint, loader strict, canon, helper refs/binding, routing thuần (`routing.py`) và output. Không có gate/observer/receipt/D4 runtime:
mọi bundle hợp lệ về cấu trúc vẫn BLOCKED (CANDIDATE_EVALUATION_NOT_IMPLEMENTED) hoặc DENY/UNSUPPORTED/BLOCKED theo quan hệ đã tính; không PASS.
`expected_design` của ví dụ là kỳ vọng giả định, không phải verdict đã chạy. Oracle route lấy từ `route_rows` của EXPECTED và luật policy, không từ `effect.routing` tự khai.
Gates are not evaluated, so nothing here is PASS; the route oracle comes from EXPECTED route_rows and the policy, not from the fixture's own declared routing.
Thiếu jsonschema thì thất bại rõ, không skip / a missing jsonschema fails loudly, never skips.
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
from unittest import mock

try:
    import jsonschema  # noqa: F401
    HAVE_JSONSCHEMA = True
except ImportError:
    HAVE_JSONSCHEMA = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CVF = os.path.join(ROOT, '.cvf')
CHECKS = os.path.join(CVF, 'checks')
ENTRY = os.path.join(CHECKS, 'control_check_v3.py')
PKG = os.path.join(CHECKS, 'v3')
V3C = os.path.join(CVF, 'contracts', 'v3')
V3R = os.path.join(CVF, 'rules', 'v3')
REF_TEST = os.path.join(ROOT, 'tests', 'test_control_v3_candidate.py')

# Pin 16 ký tự đầu: không được sửa để test xanh. / 16-char prefixes: do not edit to turn tests green.
V1_PINS = {
    ('contracts', 'control.schema.json'): '933265fa7b113941',
    ('contracts', 'CONTROL_CONTRACT.md'): 'd22848dee934d4cf',
    ('contracts', 'examples', 'EXPECTED.json'): 'c72e1e6b2bfda8ff',
    ('rules', 'ROUTING_POLICY.json'): '8db011baf5d5c5a0',
    ('rules', 'CONTROL_RULES.md'): 'ad3337b9baee23e4',
    ('checks', 'control_check.py'): 'f95bfc367bb7f470',
}
V2_TREE_PIN = ('e154e1db4438adb9', 30)           # .cvf/contracts/v2 + .cvf/rules/v2
V2_CHECK_TREE_PIN = ('3a4895ec9979faaa', 6)      # .cvf/checks/v2 (*.py, *.md)
# P-CTX1 revision 28/10/2026: approved derivative refresh; see HANDOFF rev144.
FILE_PINS = {
    ('checks', 'control_check_v2.py'): '5179e7091579c048',
    ('contracts', 'v3', 'control.schema.json'): '21d3b192151b84f6',
    ('contracts', 'v3', 'vectors.json'): 'eb59221f24200df8',
    ('rules', 'v3', 'ROUTING_POLICY.json'): '4577f71406997acb',
}
V3_EXAMPLES_PIN = ('0857c44d4bc15e9b', 22)
TEST_PINS = {
    'test_control_check.py': '454e3f4944825809',
    'test_control_v2_candidate.py': 'b32d7b3ff0e8a014',
    'test_control_check_v2.py': 'a5daf2e48c402323',
    'test_control_check_v2_s2.py': '6d449aa72411b490',
}
WRITER_PIN = '8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852'

OUTPUT_KEYS = ['check_version', 'contract', 'selection', 'candidate_status', 'implementation_stage', 'evaluation_basis', 'phase',
               'phase_scope', 'disposition', 'effect_authorized', 'assurance_level', 'init_error', 'reasons', 'details', 'owners',
               'route', 'gates', 'aggregate', 'coverage']
COVERAGE_KEYS = ['record_structure_checked', 'binding_evaluated', 'routing_evaluated', 'gates_evaluated', 'artifact_bytes_observed',
                 'target_existence_observed', 'actual_operation_observed', 'requirements_semantic_verified', 'owner_protection']
COVERAGE_FALSE = [k for k in COVERAGE_KEYS if k not in ('record_structure_checked', 'binding_evaluated', 'routing_evaluated', 'owner_protection')]
ROUTE_KEYS = ['evaluated', 'rows', 'status', 'assumptions']
NOT_EVALUATED_ROUTE = {'evaluated': False, 'rows': [], 'status': None, 'assumptions': []}
BASE_OPEN = ('dispatch', 'effect')  # A-NEW_TARGET còn mở (không có S4 observer) ở dispatch/effect; accept không áp dụng
AGG_COUNTS = ['due_gates', 'met', 'not_required', 'not_yet_due', 'not_checked', 'unsupported', 'not_met', 'user_accepted_declared']
PHASES = ('dispatch', 'effect', 'accept')
NOT_IMPL = 'CANDIDATE_EVALUATION_NOT_IMPLEMENTED'
V3 = 'law.cvf.control/3'
EX_WORKING = 'ex01_pcn1_working_request.json'
EX_ACCEPTED = 'ex04_pcn1_accepted_d4_complete.json'


def sha_prefix(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_module_from(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dumps(obj):
    return json.dumps(obj).encode('utf-8')


def tree_pin(bases, suffixes=None):
    lines = []
    for base in bases:
        for root, _, files in os.walk(os.path.join(ROOT, *base.split('/'))):
            for name in files:
                if '__pycache__' in root or (suffixes and not name.endswith(suffixes)):
                    continue
                full = os.path.join(root, name)
                lines.append('%s:%s' % (os.path.relpath(full, ROOT).replace(os.sep, '/'), hashlib.sha256(read_bytes(full)).hexdigest()))
    lines.sort()
    return hashlib.sha256('\n'.join(lines).encode()).hexdigest()[:16], len(lines)


def setUpModule():
    if not HAVE_JSONSCHEMA:
        raise RuntimeError('jsonschema>=4.18 không có / not installed: BLOCKED, không tự cài / not auto-installed')


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.mkdtemp(prefix='law-c2-s3b-')
        cls.entry = load_module_from(ENTRY, 'law_cvf_entry_v3_under_test')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def example(self, name):
        return read_json(os.path.join(V3C, 'examples', name))

    def example_bytes(self, name):
        return read_bytes(os.path.join(V3C, 'examples', name))

    def write_scratch(self, name, data):
        path = os.path.join(self.scratch, name)
        with open(path, 'wb') as f:
            f.write(data)
        return path

    def run_cli(self, argv, env=None):
        proc = subprocess.run([sys.executable, '-B', '-I', ENTRY] + list(argv), cwd=self.scratch, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, proc.stdout, proc.stderr

    def check(self, data, phase='effect'):
        return self.entry.check_bytes(data, phase, 'v3')

    def assert_foundation_shape(self, res):
        self.assertEqual(list(res.keys()), OUTPUT_KEYS)
        self.assertEqual(res['check_version'], 'law.cvf.check/3')
        self.assertEqual(res['contract'], 'v3')
        self.assertEqual(res['candidate_status'], 'CANDIDATE_NOT_ACTIVE')
        self.assertEqual(res['implementation_stage'], 'BINDING_ROUTING_ONLY')
        self.assertIs(res['effect_authorized'], False)
        self.assertEqual(res['assurance_level'], 'UNVERIFIED')
        self.assertIsInstance(res['init_error'], bool)
        self.assertEqual(res['reasons'], sorted(set(res['reasons'])))
        self.assertTrue(all(isinstance(d, str) for d in res['details']))
        self.assertEqual(sorted(res['owners']), ['policy_sha256', 'schema_sha256'])
        cov = res['coverage']
        self.assertEqual(list(cov.keys()), COVERAGE_KEYS)
        self.assertEqual(cov['owner_protection'], 'NOT_PROVEN')
        self.assertIsInstance(cov['record_structure_checked'], bool)
        for k in COVERAGE_FALSE:
            self.assertIs(cov[k], False, k)
        self.assertEqual(list(res['route'].keys()), ROUTE_KEYS)
        if not res['route']['evaluated']:
            self.assertEqual(res['route'], NOT_EVALUATED_ROUTE)
        else:
            self.assertIn(res['route']['status'], ('RESOLVED', 'CONDITIONAL', 'UNRESOLVED'))
            self.assertIs(cov['routing_evaluated'], True)
        self.assertEqual(res['gates'], [])
        self.assertIs(cov['gates_evaluated'], False)
        agg = res['aggregate']
        self.assertEqual(list(agg.keys()), ['records_checked_state'] + AGG_COUNTS + ['open_assumptions', 'conclusion_scope'])
        self.assertEqual(agg['records_checked_state'], 'NOT_EVALUATED')
        self.assertEqual([agg[k] for k in AGG_COUNTS], [0] * len(AGG_COUNTS))
        self.assertEqual((agg['open_assumptions'], agg['conclusion_scope']), ([], 'RECORD_CONSISTENCY_IN_MEMORY'))
        self.assertNotIn(res['disposition'], ('PASS', 'NOT_APPLICABLE'))
        if not cov['record_structure_checked']:
            self.assertIsNone(res['phase_scope'])
        else:
            suffix = [w for w, flag in (('BINDING', cov['binding_evaluated']), ('ROUTING', cov['routing_evaluated'])) if flag]
            self.assertEqual(res['phase_scope'], 'STRUCTURE_' + '_'.join(suffix) if suffix else 'STRUCTURE_ONLY')


class OwnersUntouched(unittest.TestCase):
    def test_v1_owner_hashes_unchanged(self):
        for rel, want in V1_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(CVF, *rel)), want, '/'.join(rel))

    def test_v2_candidate_contract_rules_and_checker_are_byte_identical(self):
        self.assertEqual(tree_pin(['.cvf/contracts/v2', '.cvf/rules/v2']), V2_TREE_PIN)
        self.assertEqual(tree_pin(['.cvf/checks/v2'], ('.py', '.md')), V2_CHECK_TREE_PIN)

    def test_accepted_v3_owners_vectors_examples_and_writer_are_byte_identical(self):
        for rel, want in FILE_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(CVF, *rel)), want, '/'.join(rel))
        names = sorted(n for n in os.listdir(os.path.join(V3C, 'examples')) if n.startswith('ex') and n.endswith('.json'))
        joined = chr(10).join('%s:%s' % (n, hashlib.sha256(read_bytes(os.path.join(V3C, 'examples', n))).hexdigest()) for n in names)
        self.assertEqual((hashlib.sha256(joined.encode()).hexdigest()[:16], len(names)), V3_EXAMPLES_PIN)
        self.assertEqual(hashlib.sha256(read_bytes(os.path.join(ROOT, 'tools', 'publish_new.py'))).hexdigest(), WRITER_PIN)

    def test_earlier_tests_unchanged(self):
        for name, want in TEST_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(ROOT, 'tests', name)), want, name)

    def test_package_tree_is_exactly_the_accepted_modules_plus_the_two_narrow_workflow_modules(self):
        names = sorted(n for n in os.listdir(PKG) if n.endswith(('.py', '.md')))
        self.assertEqual(names, ['README.md', '__init__.py', 'binding.py', 'canon.py', 'loader.py', 'observer.py', 'refs.py', 'routing.py',
                                 'workflow.py'])
        for forbidden in ('pathing.py', 'zones.py', 'gates.py', 'delegation.py', 'observe.py', 'engine.py', 'route.py'):
            self.assertFalse(os.path.exists(os.path.join(PKG, forbidden)), forbidden)

    def test_product_does_not_import_tests_or_older_checkers_or_touch_sys_path(self):
        for path in [ENTRY] + [os.path.join(PKG, n) for n in ('__init__.py', 'canon.py', 'loader.py', 'refs.py', 'binding.py', 'routing.py')]:
            src = read_bytes(path).decode('utf-8')
            # `--root` is the single new option of the one-file flow; the no-root modules still never mention the writer or sys.path.
            for needle in ('import tests', 'from tests', 'sys.path', '--basis', '--trust', '--schema', '--policy', 'law_cvf_check_v1',
                           'law_cvf_check_v2', 'monkeypatch', 'publish_new'):
                self.assertFalse(needle in src, '%s contains %r' % (os.path.basename(path), needle))
        for name in ('observer.py', 'workflow.py'):
            src = read_bytes(os.path.join(PKG, name)).decode('utf-8')
            for needle in ('import tests', 'from tests', '--basis', '--trust', '--schema', '--policy', 'law_cvf_check_v1', 'law_cvf_check_v2',
                           'monkeypatch', 'subprocess', 'os.system', 'socket', 'urllib', '.publish(', '.recover(', '.discard_staged(', 'os.mkdir',
                           'os.makedirs', 'os.remove', 'os.unlink', 'os.rename', 'os.replace', "'wb'", '"wb"', "'w'", '"w"', "'a'", "'ab'"):
                self.assertFalse(needle in src, '%s contains %r' % (name, needle))
        entry_src = read_bytes(ENTRY).decode('utf-8')
        for needle in ('control_check_v2', "'control_check.py'", 'subprocess', 'os.system'):
            self.assertNotIn(needle, entry_src)

    def test_literals_repeat_the_v3_owners(self):
        pkg = load_module_from(os.path.join(PKG, '__init__.py'), 'law_cvf_check_v3_literals')
        schema = read_json(os.path.join(V3C, 'control.schema.json'))
        policy = read_json(os.path.join(V3R, 'ROUTING_POLICY.json'))
        self.assertEqual(pkg.SCHEMA_ID, schema['$id'])
        self.assertEqual(pkg.SCHEMA_VERSION, schema['$defs']['schema_version']['const'])
        self.assertEqual(pkg.POLICY_VERSION, policy['policy_version'])
        self.assertEqual(pkg.BIND_VERSION, schema['$defs']['bind_version']['const'])
        self.assertEqual((pkg.POLICY_STATUS, pkg.EVALUATION_BASIS), (policy['status'], policy['evaluation_basis']))
        self.assertEqual(pkg.V2_SCHEMA_VERSION, 'law.cvf.control/2')


LIGHT_CREATE_NEW = ('ex01', 'ex02', 'ex03', 'ex04', 'ex05', 'ex06', 'ex07', 'ex08', 'ex09', 'ex10', 'ex12')


def expected_reasons(name, phase):
    """Lý do kỳ vọng theo luật routing/binding và EXPECTED (không lấy từ output của code).

    NOT_IMPL luôn có (gate/observer/receipt/D4 chưa chạy). A-NEW_TARGET mở ở dispatch/effect cho create_new khớp mệnh đề create_new.
    ENVELOPE_EXCEEDED chưa đánh giá: hàng external có thể áp dụng và giữ nghĩa vụ review; hợp chưa phân loại được.
    Routing khai trong fixtures là counterfactual, không bằng tập definite/possible hiện tại. ex07 còn lệch binding.
    """
    key = name[:4]
    reasons = {NOT_IMPL, 'UNCLASSIFIED_OPERATION', 'REVIEW_REQUIRED_UNSUPPORTED', 'ROUTE_DECLARED_MISMATCH'}
    if key == 'ex07':
        reasons.add('BINDING_MISMATCH')
    if key in ('ex14', 'ex15'):
        reasons.add('UNCLASSIFIED_OPERATION')
    if key in ('ex11', 'ex13'):
        reasons.add('REVIEW_REQUIRED_UNSUPPORTED')
    if key in LIGHT_CREATE_NEW or key == 'ex11':
        if phase in BASE_OPEN:
            reasons.add('ROUTE_ASSUMPTION_OPEN')
    return sorted(reasons)


class OutputContract(Base):
    def valid_files(self):
        return [c['file'] for c in read_json(os.path.join(V3C, 'examples', 'EXPECTED.json'))['cases'] if c['schema_valid']]

    def test_valid_examples_are_blocked_never_pass_in_every_phase(self):
        valid = self.valid_files()
        self.assertEqual(len(valid), 15)
        for name in valid:
            for phase in PHASES:
                with self.subTest(name=name, phase=phase):
                    res = self.check(self.example_bytes(name), phase)
                    self.assert_foundation_shape(res)
                    self.assertEqual((res['disposition'], res['reasons']), ('BLOCKED', expected_reasons(name, phase)))
                    self.assertEqual((res['phase'], res['selection'], res['evaluation_basis']), (phase, 'API_EXPLICIT', 'COOPERATIVE_WORKFLOW'))
                    self.assertIs(res['init_error'], False)
                    self.assertIs(res['coverage']['record_structure_checked'], True)
                    self.assertIs(res['coverage']['routing_evaluated'], True)
                    self.assertIs(res['coverage']['binding_evaluated'], True)

    def test_expected_design_is_never_turned_into_a_verdict(self):
        expected = read_json(os.path.join(V3C, 'examples', 'EXPECTED.json'))
        passes = [c['file'] for c in expected['cases'] if c['expected_design']['disposition'] == 'PASS']
        self.assertEqual(passes, ['ex01_pcn1_working_request.json', 'ex02_pcn1_output_internal_request.json', EX_ACCEPTED])
        for name in passes:
            res = self.check(self.example_bytes(name), 'accept')
            self.assertEqual((res['disposition'], res['reasons']), ('BLOCKED', expected_reasons(name, 'accept')), name)
        # Lỗi do checker sở hữu (receipt, verdict review, D4) chưa có ở candidate: chỉ lý do routing/binding đã biết mới xuất hiện.
        # Checker-owned defects (receipt, review verdict, D4) are not implemented; only known route/binding reasons appear.
        for name in ('ex05_pcn1_receipt_missing.json', 'ex11_pcn1_direct_runtime_write.json', 'ex13_pcn1_review_required_unsupported.json'):
            res = self.check(self.example_bytes(name), 'effect')
            self.assertEqual(res['reasons'], expected_reasons(name, 'effect'), name)
            self.assertNotIn('PRECONDITION_PROOF_MISSING', res['reasons'])
            self.assertNotIn('REVIEW_MISSING', res['reasons'])

    def test_schema_invalid_examples_are_refused_never_blocked_as_valid(self):
        want = {'ex16_pcn1_v2_record_in_v3.json': ('UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN', 'VERSION_MIXED'])}
        for case in read_json(os.path.join(V3C, 'examples', 'EXPECTED.json'))['cases']:
            if case['schema_valid']:
                continue
            res = self.check(self.example_bytes(case['file']))
            self.assert_foundation_shape(res)
            self.assertEqual((res['disposition'], res['reasons']), want.get(case['file'], ('DENY', ['SCHEMA_INVALID'])), case['file'])
            self.assertIs(res['coverage']['record_structure_checked'], False)
            self.assertIsNone(res['phase_scope'])

    def test_owner_hashes_are_the_bytes_actually_read(self):
        res = self.check(self.example_bytes(EX_ACCEPTED))
        self.assertEqual(res['owners']['schema_sha256'], hashlib.sha256(read_bytes(os.path.join(V3C, 'control.schema.json'))).hexdigest())
        self.assertEqual(res['owners']['policy_sha256'], hashlib.sha256(read_bytes(os.path.join(V3R, 'ROUTING_POLICY.json'))).hexdigest())

    def test_single_record_input_is_accepted(self):
        task = [r for r in self.example(EX_WORKING)['records'] if r['record_type'] == 'task'][0]
        res = self.check(dumps(task))
        # Task đứng một mình: route tính được (một action), grant không có trong input nên GRANT_MISSING; không bịa binding.
        # A lone task: routing is computed; its grant record is not in the input, so GRANT_MISSING; no binding is invented.
        self.assertEqual((res['disposition'], res['reasons']),
                         ('BLOCKED', sorted([NOT_IMPL, 'GRANT_MISSING', 'ROUTE_ASSUMPTION_OPEN',
                                             'REVIEW_REQUIRED_UNSUPPORTED', 'UNCLASSIFIED_OPERATION'])))
        self.assertIs(res['coverage']['binding_evaluated'], False)
        self.assertIs(res['coverage']['routing_evaluated'], True)

    def test_single_effect_without_its_task_is_not_bound_or_routed(self):
        effect = [r for r in self.example(EX_ACCEPTED)['records'] if r['record_type'] == 'effect' and r['stage'] == 'REQUEST'][0]
        res = self.check(dumps(effect))
        self.assertEqual(res['route'], NOT_EVALUATED_ROUTE)
        self.assertIs(res['coverage']['binding_evaluated'], False)
        self.assertIs(res['coverage']['routing_evaluated'], False)
        self.assertIn('BINDING_INCOMPLETE', res['reasons'])
        self.assertNotIn('BINDING_MISMATCH', res['reasons'])
        self.assertEqual(res['phase_scope'], 'STRUCTURE_ONLY')

    def test_api_argument_errors(self):
        good = self.example_bytes(EX_WORKING)
        for bad in ('{}', bytearray(b'{}'), memoryview(b'{}'), None, 5):
            with self.subTest(data=type(bad).__name__), self.assertRaises(TypeError):
                self.entry.check_bytes(bad, 'effect', 'v3')
        for contract in ('v1', 'v2', 'V3', '', None, 'v3 '):
            with self.subTest(contract=contract), self.assertRaises(ValueError):
                self.entry.check_bytes(good, 'effect', contract)
        for phase in ('PRE_EFFECT', '', None, 'Accept'):
            with self.subTest(phase=phase), self.assertRaises(ValueError):
                self.entry.check_bytes(good, phase, 'v3')

    def test_public_surface_has_no_injection_or_check_records(self):
        names = {n for n in dir(self.entry) if not n.startswith('_')}
        for banned in ('check_records', 'load_owners', 'evaluate', 'route', 'gates_for', 'observe'):
            self.assertNotIn(banned, names)
        self.assertTrue(set(self.entry.CONTRACTS) == {'v3'})


    def test_known_loss_is_not_hidden_when_multiple_tasks_prevent_routing(self):
        bundle = self.example(EX_ACCEPTED)
        task = next(r for r in bundle['records'] if r['record_type'] == 'task')
        twin = copy.deepcopy(task)
        twin['task_id'] = 'pcn1-known-loss-other-task'
        twin['effects']['preservation'] = [{'target': 'references/source-documents/original.xlsx',
                                           'must_keep': 'validation', 'known_loss_state': 'KNOWN_LOSS'}]
        bundle['records'].append(twin)
        result = self.check(dumps(bundle), 'accept')
        self.assertTrue(result['coverage']['record_structure_checked'])
        self.assertEqual(result['disposition'], 'DENY')
        self.assertIn('KNOWN_PRESERVATION_LOSS', result['reasons'])
        self.assertIn('MULTI_TASK_UNSUPPORTED', result['reasons'])
        self.assertFalse(result['coverage']['routing_evaluated'])
        self.assertFalse(result['effect_authorized'])


class RefusalMatrix(Base):
    def bundle(self, name=EX_ACCEPTED):
        return self.example(name)

    def records(self, b, rt):
        return [r for r in b['records'] if r['record_type'] == rt]

    def refuse(self, b, disposition, reasons):
        res = self.check(dumps(b))
        self.assert_foundation_shape(res)
        self.assertEqual((res['disposition'], res['reasons']), (disposition, sorted(reasons)))
        return res

    def test_version_missing_mixed_and_garbage(self):
        b = self.bundle()
        del self.records(b, 'task')[0]['schema_version']
        self.refuse(b, 'UNSUPPORTED', ['VERSION_MISSING'])
        b = self.bundle()
        self.records(b, 'task')[0]['schema_version'] = 'law.cvf.control/2'
        self.refuse(b, 'UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN', 'VERSION_MIXED'])
        for value in (3, None, ['law.cvf.control/3'], {'v': 3}, 'LAW.CVF.CONTROL/3', ''):
            b = self.bundle()
            b['schema_version'] = value
            with self.subTest(value=repr(value)):
                res = self.check(dumps(b))
                self.assertEqual(res['disposition'], 'UNSUPPORTED')
                self.assertIn('SCHEMA_VERSION_UNKNOWN', res['reasons'])

    def test_all_old_version_bundles_are_refused_with_an_explicit_hint_and_never_tried(self):
        for old, entry in (('law.cvf.control/1', 'control_check.py (v1)'), ('law.cvf.control/2', 'control_check_v2.py (v2)')):
            b = self.bundle()
            b['schema_version'] = old
            for r in b['records']:
                r['schema_version'] = old
            with self.subTest(old):
                res = self.check(dumps(b))
                self.assertEqual((res['disposition'], res['reasons']), ('UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN']))
                self.assertTrue(any(entry in d and 'neither tries it nor reinterprets it' in d for d in res['details']), res['details'])
                self.assertIs(res['coverage']['record_structure_checked'], False)

    def test_real_v2_example_is_refused(self):
        v2 = read_bytes(os.path.join(CVF, 'contracts', 'v2', 'examples', 'ex01_draft_in_grant.json'))
        res = self.check(v2)
        self.assertEqual((res['disposition'], res['reasons']), ('UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN']))

    def test_basis_variants(self):
        b = self.bundle()
        del self.records(b, 'task')[0]['evaluation_basis']
        self.refuse(b, 'UNSUPPORTED', ['BASIS_MISSING'])
        b = self.bundle()
        self.records(b, 'task')[0]['evaluation_basis'] = 'TRUSTED_ENFORCED'
        self.refuse(b, 'UNSUPPORTED', ['BASIS_UNKNOWN', 'BASIS_MIXED'])
        b = self.bundle()
        self.records(b, 'effect')[0]['binding']['evaluation_basis'] = 'OTHER'
        res = self.check(dumps(b))
        self.assertEqual(res['disposition'], 'UNSUPPORTED')
        self.assertIn('BASIS_MISMATCH', res['reasons'])
        self.assertIsNone(res['evaluation_basis'], 'no basis is reported as confirmed when the input basis is not valid')

    def test_binding_literals(self):
        for field, value in (('bind_version', 'law.cvf.bind/2'), ('policy_version', 'law.cvf.routing/2')):
            b = self.bundle()
            self.records(b, 'effect')[0]['binding'][field] = value
            with self.subTest(field):
                res = self.refuse(b, 'UNSUPPORTED', ['BINDING_VERSION_UNKNOWN'])
                self.assertEqual(res['evaluation_basis'], 'COOPERATIVE_WORKFLOW')
        b = self.bundle()
        del self.records(b, 'effect')[0]['binding']['policy_digest']
        self.refuse(b, 'UNSUPPORTED', ['BINDING_VERSION_UNKNOWN'])

    def test_v3_specific_structure_defects_are_schema_invalid_deny(self):
        mutations = {
            'staged role': lambda b: self.records(b, 'effect')[1]['outcome']['artifacts'][0].__setitem__('role', 'STAGED_BYTES'),
            'receipt on request': lambda b: self.records(b, 'effect')[0].__setitem__('receipt_ref', self.records(b, 'effect')[1]['receipt_ref']),
            'old user_acceptance_ref': lambda b: self.records(b, 'result')[0].__setitem__('user_acceptance_ref', {}),
            'acceptance via file': lambda b: self.records(b, 'result')[0]['user_acceptance']['ref']['attribution'].__setitem__('channel', 'USER_AUTHORED_FILE'),
            'completion deferred': lambda b: self.records(b, 'task')[0]['effects']['actions'][0].__setitem__('completion', 'REQUIRED'),
            'agent_state zone': lambda b: self.records(b, 'task')[0]['effects']['actions'][0].__setitem__('write_zone', 'agent_state'),
        }
        for label, mutate in mutations.items():
            b = self.bundle()
            mutate(b)
            with self.subTest(label):
                res = self.check(dumps(b))
                self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['SCHEMA_INVALID']))

    def test_schema_invalid_after_literals_is_deny_and_does_not_echo_values(self):
        b = self.bundle()
        self.records(b, 'task')[0]['work_id'] = 'SECRET-WORK-ID bad id!'
        res = self.check(dumps(b))
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['SCHEMA_INVALID']))
        self.assertNotIn('SECRET-WORK-ID', json.dumps(res))

    def test_routing_policy_record_is_not_checkable(self):
        policy = read_json(os.path.join(V3R, 'ROUTING_POLICY.json'))
        res = self.check(dumps(policy))
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['SCHEMA_INVALID']))

    def test_malformed_input(self):
        cases = [b'', b'{', b'[]', b'"x"', b'null', b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'\xff\xfe{}',
                 b'{"schema_version":"law.cvf.control/3"} trailing']
        for data in cases:
            with self.subTest(data=data[:20]):
                res = self.check(data)
                self.assert_foundation_shape(res)
                self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['INPUT_MALFORMED']))
                self.assertIsNone(res['evaluation_basis'])
        too_big = self.check(b' ' * (8 * 1024 * 1024 + 1))
        self.assertEqual((too_big['disposition'], too_big['reasons']), ('DENY', ['INPUT_MALFORMED']))
        deep = self.check(b'[' * 5000 + b']' * 5000)
        self.assertEqual(deep['reasons'], ['INPUT_MALFORMED'])

    def test_duplicate_key_nested_in_a_valid_bundle(self):
        text = self.example_bytes(EX_WORKING).decode('utf-8').replace('"task_revision": 1,', '"task_revision": 1, "task_revision": 2,', 1)
        res = self.check(text.encode('utf-8'))
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['INPUT_MALFORMED']))
        self.assertNotIn('task_revision', ' '.join(res['details']))

    def test_canonical_domain_is_unsupported_not_guessed(self):
        edits = {
            'float': lambda t: t['acceptance']['requirements'][0].__setitem__('expected_evidence', [1.5]) or t.__setitem__('note', 1.5),
            'big int': lambda t: t.__setitem__('task_revision', 2 ** 53),
            'non nfc': lambda t: t['intent'].__setitem__('main_interpretation', 'é'),
            'lone surrogate': lambda t: t['intent'].__setitem__('main_interpretation', '\ud800'),
        }
        for label, edit in edits.items():
            b = self.bundle(EX_WORKING)
            edit(self.records(b, 'task')[0])
            with self.subTest(label):
                data = json.dumps(b, ensure_ascii=True).encode('utf-8')
                res = self.check(data)
                self.assertIn(res['disposition'], ('UNSUPPORTED', 'DENY'))
                self.assertNotEqual(res['reasons'], [NOT_IMPL])

    def test_bundle_bom_is_tolerated(self):
        res = self.check(b'\xef\xbb\xbf' + self.example_bytes(EX_WORKING))
        self.assertEqual((res['disposition'], res['reasons']), ('BLOCKED', expected_reasons(EX_WORKING, 'effect')))

    def test_diagnostics_do_not_echo_record_type_or_secret_values(self):
        b = self.bundle()
        self.records(b, 'task')[0]['record_type'] = 'SECRET-TYPE-VALUE'
        res = self.check(dumps(b))
        self.assertNotIn('SECRET-TYPE-VALUE', json.dumps(res))


class LoaderInit(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.entry._load_package()
        cls.loader = importlib.import_module('law_cvf_check_v3.loader')

    def owner_tree(self, mutate_schema=None, mutate_policy=None, drop=None):
        root = tempfile.mkdtemp(dir=self.scratch)
        os.makedirs(os.path.join(root, 'contracts', 'v3'))
        os.makedirs(os.path.join(root, 'rules', 'v3'))
        schema = read_json(os.path.join(V3C, 'control.schema.json'))
        policy = read_json(os.path.join(V3R, 'ROUTING_POLICY.json'))
        if mutate_schema:
            mutate_schema(schema)
        if mutate_policy:
            mutate_policy(policy)
        for rel, obj in ((('contracts', 'v3', 'control.schema.json'), schema), (('rules', 'v3', 'ROUTING_POLICY.json'), policy)):
            if drop != rel[-1]:
                with open(os.path.join(root, *rel), 'wb') as f:
                    f.write(json.dumps(obj).encode('utf-8'))
        return root

    def init_failure(self, root):
        with self.assertRaises(self.loader.InitFailure) as cm:
            self.loader.load_owners(root)
        return cm.exception

    def test_real_owners_load_and_are_the_v3_files(self):
        owners = self.loader.load_owners()
        self.assertEqual(owners.schema_sha256, hashlib.sha256(read_bytes(os.path.join(V3C, 'control.schema.json'))).hexdigest())
        self.assertEqual(owners.policy_sha256, hashlib.sha256(read_bytes(os.path.join(V3R, 'ROUTING_POLICY.json'))).hexdigest())
        self.assertEqual(owners.policy_bytes, read_bytes(os.path.join(V3R, 'ROUTING_POLICY.json')))
        self.assertTrue(self.loader.SCHEMA_REL[1] == self.loader.POLICY_REL[1] == 'v3')

    def test_missing_owner_files(self):
        for name in ('control.schema.json', 'ROUTING_POLICY.json'):
            with self.subTest(name):
                self.assertIn('OWNER_UNREADABLE', self.init_failure(self.owner_tree(drop=name)).reasons)

    def test_remote_references_are_refused_without_network(self):
        cases = {
            'ref': lambda s: s['$defs'].__setitem__('id', {'$ref': 'https://example.invalid/x.json'}),
            'dynamicRef': lambda s: s.__setitem__('allOf', [{'$dynamicRef': 'https://example.invalid/d'}]),
            'rebased': lambda s: s.__setitem__('allOf', [{'$id': 'https://example.invalid/rebased/', '$ref': '#missing'}]),
        }
        for label, mutate in cases.items():
            root = self.owner_tree(mutate_schema=mutate)
            with self.subTest(label), mock.patch('urllib.request.urlopen', side_effect=AssertionError('retrieval canary')) as retrieval:
                self.assertIn('OWNER_INVALID', self.init_failure(root).reasons)
            retrieval.assert_not_called()

    def test_registry_denies_retrieval_even_if_the_scan_misses(self):
        root = self.owner_tree(mutate_schema=lambda s: s.__setitem__('allOf', [{'$ref': 'https://example.invalid/registry-canary'}]))
        with mock.patch.object(self.loader, '_has_remote_ref', return_value=False), \
                mock.patch('urllib.request.urlopen', side_effect=AssertionError('retrieval canary')) as retrieval:
            self.assertIn('OWNER_INVALID', self.init_failure(root).reasons)
        retrieval.assert_not_called()

    def test_owner_literals(self):
        for pin_target, mutate_kw, reason in (
                ('schema id v2', {'mutate_schema': lambda s: s.__setitem__('$id', 'urn:law:cvf:control:2')}, 'SCHEMA_VERSION_UNKNOWN'),
                ('policy routing v2', {'mutate_policy': lambda p: p.__setitem__('policy_version', 'law.cvf.routing/2')}, 'POLICY_VERSION_UNKNOWN'),
                ('policy schema v2', {'mutate_policy': lambda p: p.__setitem__('schema_version', 'law.cvf.control/2')}, 'POLICY_VERSION_UNKNOWN'),
                ('policy active', {'mutate_policy': lambda p: p.__setitem__('status', 'ACTIVE_COOPERATIVE')}, 'OWNER_INVALID')):
            with self.subTest(pin_target):
                self.assertIn(reason, self.init_failure(self.owner_tree(**mutate_kw)).reasons)

    def test_invalid_schema_and_policy_including_owner_protocols(self):
        cases = (('schema type', {'mutate_schema': lambda s: s.__setitem__('type', 5)}),
                 ('policy downgrade', {'mutate_policy': lambda p: p.__setitem__('main_may_downgrade', True)}),
                 ('policy without owner_protocols', {'mutate_policy': lambda p: p.pop('owner_protocols')}),
                 ('policy review phase supported', {'mutate_policy': lambda p: p['owner_protocols'][0].__setitem__('review_phases_supported', ['PRE_EFFECT'])}),
                 ('policy conditional pass', {'mutate_policy': lambda p: p.__setitem__('conditional_route_disposition', 'PASS')}))
        for label, kw in cases:
            with self.subTest(label):
                self.assertIn('OWNER_INVALID', self.init_failure(self.owner_tree(**kw)).reasons)

    def test_duplicate_key_in_owner(self):
        root = self.owner_tree()
        path = os.path.join(root, 'rules', 'v3', 'ROUTING_POLICY.json')
        text = read_bytes(path).decode('utf-8')
        with open(path, 'wb') as f:
            f.write(text.replace('{', '{"policy_id": "x", ', 1).encode('utf-8'))
        self.assertIn('OWNER_INVALID', self.init_failure(root).reasons)

    def test_dependency_missing_or_too_old_is_init_error_exit_2(self):
        data = self.example_bytes(EX_WORKING)
        for label, patch in (('missing', mock.patch.object(self.loader, '_import_jsonschema', side_effect=ImportError('x'))),
                             ('too old', mock.patch.object(self.loader, '_jsonschema_version', return_value=(4, 17)))):
            with self.subTest(label), patch:
                res = self.check(data)
                self.assert_foundation_shape(res)
                self.assertEqual((res['disposition'], res['reasons'], res['init_error']), ('UNSUPPORTED', ['DEPENDENCY_MISSING'], True))
                self.assertEqual(res['owners'], {'schema_sha256': None, 'policy_sha256': None})
                self.assertIsNone(res['evaluation_basis'])
                self.assertEqual(self.entry.exit_code(res), 2)

    def test_owner_failure_is_init_error_with_hash_of_what_was_read_and_never_a_user_verdict(self):
        bad_root = self.owner_tree(mutate_policy=lambda p: p.__setitem__('main_may_downgrade', True))
        with mock.patch.object(self.loader, 'default_cvf_dir', return_value=bad_root):
            res = self.check(self.example_bytes(EX_WORKING))
        self.assert_foundation_shape(res)
        self.assertEqual((res['disposition'], res['init_error']), ('UNSUPPORTED', True))
        self.assertIn('OWNER_INVALID', res['reasons'])
        self.assertIsNotNone(res['owners']['schema_sha256'])
        self.assertIsNotNone(res['owners']['policy_sha256'])
        self.assertIsNone(res['phase_scope'])
        self.assertEqual(self.entry.exit_code(res), 2)

    def test_package_load_failure_is_init_error(self):
        with mock.patch.object(self.entry, '_load_package', side_effect=RuntimeError('boom')):
            res = self.check(self.example_bytes(EX_WORKING))
        self.assertEqual((res['disposition'], res['reasons'], res['init_error']), ('UNSUPPORTED', ['PACKAGE_UNAVAILABLE'], True))


class NoObservation(Base):
    def test_valid_bundle_reads_no_artifact_and_uses_no_network(self):
        canary = self.write_scratch('canary.txt', b'CANARY-CONTENT')
        bundle = self.example(EX_ACCEPTED)
        task = [r for r in bundle['records'] if r['record_type'] == 'task'][0]
        task['inputs'][0]['path'] = canary.replace('\\', '/')
        task['context_refs'] = [{'path': canary.replace('\\', '/'), 'digest': 'sha256:' + '0' * 64}]
        task['intent']['refs'][0]['locator'] = 'file:///' + canary.replace('\\', '/')
        for r in bundle['records']:
            if r['record_type'] == 'effect' and r.get('stage') == 'OUTCOME':
                r['receipt_ref']['locator'] = 'file:///' + canary.replace('\\', '/')
        opened = []
        real_open = io.open

        def recording_open(file, *a, **k):
            opened.append(os.path.abspath(str(file)) if not isinstance(file, int) else file)
            return real_open(file, *a, **k)

        with mock.patch('builtins.open', recording_open), mock.patch('io.open', recording_open), \
                mock.patch('socket.socket.connect', side_effect=AssertionError('network used')):
            res = self.check(dumps(bundle))
        # Test này tự sửa task.inputs (canary), nên digest khai báo lệch là đúng; không có kết luận PASS.
        # The test edits task.inputs on purpose, so the declared digests are stale; this is a mismatch, never a PASS.
        self.assertIn('BINDING_MISMATCH', res['reasons'])
        self.assertIn(NOT_IMPL, res['reasons'])
        self.assertNotEqual(res['disposition'], 'PASS')
        self.assertNotIn(os.path.abspath(canary), opened)
        self.assertFalse([p for p in opened if not isinstance(p, int) and p.startswith(self.scratch)], opened)
        owners_read = sorted(p for p in opened if not isinstance(p, int) and p.startswith(CVF))
        self.assertEqual(owners_read, sorted([os.path.join(V3C, 'control.schema.json'), os.path.join(V3R, 'ROUTING_POLICY.json')]))
        self.assertFalse([p for p in opened if not isinstance(p, int) and p.startswith(os.path.join(ROOT, 'tools'))], 'tools/ is never read')
        others = [p for p in opened if not isinstance(p, int) and not p.startswith(CVF)]
        self.assertTrue(all('site-packages' in p or p.endswith('.zip') for p in others), others)

    def test_entry_wires_binding_and_routing_and_loads_no_older_checker(self):
        code = (
            "import importlib.util, sys\n"
            "spec = importlib.util.spec_from_file_location('e', %r)\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "res = m.check_bytes(open(%r, 'rb').read(), 'accept', 'v3')\n"
            "print(res['coverage']['binding_evaluated'], res['coverage']['routing_evaluated'],\n"
            "      all('law_cvf_check_v3.' + n in sys.modules for n in ('binding', 'refs', 'routing')),\n"
            "      any(n.startswith(('law_cvf_check_v1', 'law_cvf_check_v2')) for n in sys.modules))\n"
        ) % (ENTRY, os.path.join(V3C, 'examples', EX_ACCEPTED))
        proc = subprocess.run([sys.executable, '-B', '-I', '-c', code], cwd=self.scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((proc.returncode, proc.stderr), (0, b''))
        self.assertEqual(proc.stdout.decode().split(), ['True', 'True', 'True', 'False'])

    def test_binding_flag_needs_a_real_complete_relation_not_a_helper_run(self):
        # Chạy helper trong tiến trình không được bật cờ của entry; chỉ lần kiểm thực của entry mới bật.
        # Running a helper in-process must not flip the entry's flags; only a real entry evaluation does.
        self.entry._load_package()
        refs = importlib.import_module('law_cvf_check_v3.refs')
        binding = importlib.import_module('law_cvf_check_v3.binding')
        loader = importlib.import_module('law_cvf_check_v3.loader')
        owners = loader.load_owners()
        effect = [r for r in self.example(EX_ACCEPTED)['records'] if r['record_type'] == 'effect' and r['stage'] == 'REQUEST'][0]
        index = refs.build_index([effect])
        ctx = binding.make_policy_context(owners.policy_bytes)
        report = binding.compare_binding(index, 0, ctx)
        self.assertIs(report.recomputation_complete, False)
        res = self.check(dumps(effect))
        self.assertIs(res['coverage']['binding_evaluated'], False)


class CliV3(Base):
    def test_json_and_text_agree(self):
        path = self.write_scratch('ex04.json', self.example_bytes(EX_ACCEPTED))
        for phase in PHASES:
            with self.subTest(phase):
                code_j, out_j, err_j = self.run_cli(['--contract', 'v3', '--phase', phase, path])
                code_t, out_t, err_t = self.run_cli(['--contract', 'v3', '--phase', phase, '--format', 'text', path])
                res = json.loads(out_j.decode('utf-8'))
                self.assert_foundation_shape(res)
                self.assertEqual((res['selection'], res['phase'], res['disposition'], res['reasons']),
                                 ('CLI_EXPLICIT', phase, 'BLOCKED', expected_reasons(EX_ACCEPTED, phase)))
                self.assertEqual((code_j, code_t, err_j, err_t), (1, 1, b'', b''))
                text = out_t.decode('utf-8')
                self.assertTrue(text.startswith('law.cvf.check/3 '))
                # A-NEW_TARGET: mở ở dispatch/effect, không áp dụng ở accept (không kiểm đích-vắng ở accept).
                route_line = 'route: evaluated=true rows=3 status=UNRESOLVED assumptions=1'
                for needle in ('contract=v3', 'selection=CLI_EXPLICIT', 'stage=BINDING_ROUTING_ONLY', 'phase=' + phase,
                               'phase_scope=STRUCTURE_BINDING_ROUTING', 'disposition=BLOCKED', 'effect_authorized=false', 'assurance=UNVERIFIED',
                               NOT_IMPL, 'binding_evaluated=true', 'routing_evaluated=true', 'gates_evaluated=false',
                               'artifact_bytes_observed=false', 'target_existence_observed=false', 'actual_operation_observed=false',
                               'requirements_semantic_verified=false', 'owner_protection=NOT_PROVEN', route_line,
                               'records_checked_state=NOT_EVALUATED', 'gates=0', res['owners']['schema_sha256'], res['owners']['policy_sha256']):
                    self.assertIn(needle, text)

    def test_exit_codes(self):
        old = self.example(EX_ACCEPTED)
        for r in old['records']:
            r['schema_version'] = 'law.cvf.control/2'
        old['schema_version'] = 'law.cvf.control/2'
        cases = [
            (self.write_scratch('valid.json', self.example_bytes(EX_ACCEPTED)), 1, 'BLOCKED'),
            (self.write_scratch('bad.json', b'{'), 1, 'DENY'),
            (self.write_scratch('v2.json', dumps(old)), 1, 'UNSUPPORTED'),
            (os.path.join(self.scratch, 'does-not-exist.json'), 2, 'UNSUPPORTED'),
            (self.scratch, 2, 'UNSUPPORTED'),
        ]
        for path, want_code, want_disp in cases:
            with self.subTest(os.path.basename(path)):
                code, out, err = self.run_cli(['--contract', 'v3', '--phase', 'effect', path])
                res = json.loads(out.decode('utf-8'))
                self.assertEqual((code, res['disposition']), (want_code, want_disp))
                self.assertEqual(res['init_error'], want_code == 2)
                if want_code == 2:
                    self.assertEqual(res['reasons'], ['BUNDLE_UNREADABLE'])

    def test_oversized_file_is_denied_not_init_error(self):
        path = self.write_scratch('big.json', b' ' * (8 * 1024 * 1024 + 1))
        code, out, _ = self.run_cli(['--contract', 'v3', '--phase', 'effect', path])
        res = json.loads(out.decode('utf-8'))
        self.assertEqual((code, res['disposition'], res['reasons']), (1, 'DENY', ['INPUT_MALFORMED']))

    def test_option_errors_are_argparse_exit_2_with_empty_stdout(self):
        path = self.write_scratch('ok.json', self.example_bytes(EX_WORKING))
        base = ['--phase', 'effect', path]
        for argv in (['--contract', 'v3', path], ['--contract', 'v3', '--phase', 'bogus', path],
                     ['--contract', 'v3', '--phase', 'effect', '--format', 'xml', path], ['--contract', 'v3', '--phase', 'effect'],
                     ['--contract', 'v3', '--phase', 'effect', path, path],
                     ['--phase', 'effect', path], ['--contract', 'v1'] + base, ['--contract', 'v2'] + base, ['--contract', 'v4'] + base,
                     ['--contract', ''] + base, ['--contract=v1', '--phase', 'effect', path], ['--contract'] + base,
                     ['--contract', 'v3', '--contract', 'v3'] + base,
                     ['--contract', 'v3', '--phase', 'effect', '--root', self.scratch, '--root', self.scratch, path],
                     ['--contract', 'v3', '--phase', 'effect', '--root', '', path],
                     ['--contract', 'v3', '--phase', 'effect', '--owner', self.scratch, path],
                     ['--contract', 'v3', '--phase', 'effect', '--basis', 'COOPERATIVE_WORKFLOW', path],
                     ['--contract', 'v3', '--phase', 'effect', '--schema', 'x', path], ['--contract', 'v3', '--phase', 'effect', '--policy', 'x', path],
                     ['--contract', 'v3', '--phase', 'effect', '--trust', 'x', path], ['--contract', 'v3', '--phas', 'effect', path]):
            with self.subTest(argv=argv[:3]):
                code, out, err = self.run_cli(argv)
                self.assertEqual((code, out), (2, b''))
                self.assertIn(b'usage: control_check_v3.py', err)

    def test_older_entries_are_not_chosen_for_a_rejected_contract(self):
        path = self.write_scratch('ok2.json', self.example_bytes(EX_WORKING))
        for contract in ('v1', 'v2'):
            code, out, err = self.run_cli(['--contract', contract, '--phase', 'effect', path])
            self.assertEqual((code, out), (2, b''), contract)
            self.assertNotIn(b'law.cvf.check/2', err)

    def test_python_dash_I_from_outside_the_repo_does_not_depend_on_cwd_or_path(self):
        path = self.write_scratch('smoke.json', self.example_bytes(EX_WORKING))
        env = dict(os.environ)
        env['PYTHONPATH'] = self.scratch
        planted = os.path.join(self.scratch, 'json.py')
        with open(planted, 'w') as f:
            f.write('raise RuntimeError("planted module imported")\n')
        try:
            code, out, err = self.run_cli(['--contract', 'v3', '--phase', 'dispatch', path], env=env)
        finally:
            os.remove(planted)
        self.assertEqual((code, err), (1, b''))
        self.assertEqual(json.loads(out.decode('utf-8'))['reasons'], expected_reasons(EX_WORKING, 'dispatch'))

    def test_cli_output_does_not_copy_payload(self):
        b = self.example(EX_WORKING)
        [r for r in b['records'] if r['record_type'] == 'task'][0]['work_id'] = 'SECRET PAYLOAD bad id'
        path = self.write_scratch('secret.json', dumps(b))
        code, out, err = self.run_cli(['--contract', 'v3', '--phase', 'effect', path])
        self.assertNotIn(b'SECRET PAYLOAD', out + err)
        self.assertEqual(code, 1)


def _reference():
    return load_module_from(REF_TEST, 'law_ref_v3_candidate_test')


class Canon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = load_module_from(ENTRY, 'law_cvf_entry_v3_canon')
        cls.entry._load_package()
        cls.canon = importlib.import_module('law_cvf_check_v3.canon')
        cls.vectors = read_json(os.path.join(V3C, 'vectors.json'))
        cls.policy = read_json(os.path.join(V3R, 'ROUTING_POLICY.json'))
        cls.ref = _reference()

    def test_literal(self):
        self.assertEqual(self.canon.BIND_VERSION, 'law.cvf.bind/3')
        self.assertEqual(self.vectors['bind_version'], 'law.cvf.bind/3')

    def test_canonical_vectors(self):
        self.assertEqual(len(self.vectors['canonical']), 20)
        for v in self.vectors['canonical']:
            with self.subTest(v['id']):
                exp = v['expected']
                if exp['status'] == 'UNSUPPORTED':
                    with self.assertRaises(self.canon.Unsupported) as cm:
                        self.canon.canonical_bytes(self.canon.parse_strict(v['input_json']))
                    self.assertEqual(cm.exception.reason, exp['reason'])
                else:
                    value = self.canon.parse_strict(v['input_json'])
                    self.assertEqual(self.canon.canonical_text(value), exp['canonical_utf8'])
                    self.assertEqual(self.canon.digest_of(value), exp['digest'])

    def test_object_bytes_vectors(self):
        for v in self.vectors['object_bytes']:
            self.assertEqual(self.canon.bytes_digest(bytes.fromhex(v['bytes_hex'])), v['digest'], v['id'])

    def test_projection_fixture_and_policy_digest(self):
        fx = self.vectors['projection_fixture']
        task = copy.deepcopy(fx['task'])
        got = {'intent': self.canon.digest_of(self.canon.intent_part(task)), 'context': self.canon.digest_of(self.canon.context_part(task)),
               'task': self.canon.digest_of(self.canon.task_part(task)),
               'action': self.canon.digest_of(self.canon.action_part(task['effects']['actions'][0]))}
        self.assertEqual(got, fx['expected'])
        self.assertEqual(self.canon.canonical_text(self.canon.intent_part(task)), fx['canonical_intent'])
        self.assertEqual(self.canon.canonical_text(self.canon.action_part(task['effects']['actions'][0])), fx['canonical_action'])
        self.assertEqual(self.canon.digest_of(self.canon.policy_part(self.policy)), self.vectors['policy_digest']['digest'])

    def test_parity_with_the_candidate_reference_on_vectors_and_every_valid_example(self):
        for v in self.vectors['canonical']:
            if v['expected']['status'] != 'UNSUPPORTED':
                value = self.ref.parse_strict(v['input_json'])
                self.assertEqual(self.canon.canonical_bytes(value), self.ref.canonical_bytes(value), v['id'])
        expected = read_json(os.path.join(V3C, 'examples', 'EXPECTED.json'))
        for case in expected['cases']:
            if not case['schema_valid']:
                continue
            task = [r for r in read_json(os.path.join(V3C, 'examples', case['file']))['records'] if r['record_type'] == 'task'][0]
            for name, mine, theirs in (('intent', self.canon.intent_part, self.ref.intent_part), ('task', self.canon.task_part, self.ref.task_part),
                                       ('context', self.canon.context_part, self.ref.context_part)):
                self.assertEqual(self.canon.digest_of(mine(task)), self.ref.digest_of(theirs(task)), (case['file'], name))

    def test_product_digests_match_declared_bindings_of_non_stale_examples(self):
        expected = read_json(os.path.join(V3C, 'examples', 'EXPECTED.json'))
        for case in expected['cases']:
            if not case['schema_valid'] or case['binding_stale_or_mismatched']:
                continue
            bundle = read_json(os.path.join(V3C, 'examples', case['file']))
            task = [r for r in bundle['records'] if r['record_type'] == 'task'][0]
            for r in bundle['records']:
                b = r.get('binding')
                if b:
                    self.assertEqual(b['accepted_task_digest'], self.canon.digest_of(self.canon.task_part(task)), case['file'])
                    self.assertEqual(b['intent_digest'], self.canon.digest_of(self.canon.intent_part(task)), case['file'])
                    self.assertEqual(b['policy_digest'], self.canon.digest_of(self.canon.policy_part(self.policy)), case['file'])

    def test_exclusions_inclusions_sets_and_sequences(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        base = self.canon.digest_of(self.canon.task_part(task))
        t = copy.deepcopy(task)
        t['proposed_by'] = {'actor_id': 'x', 'role': 'worker'}
        t['note'] = 'n'
        t['example_only'] = True
        t['intent']['refs'][0]['locator'] = 'elsewhere'
        t['authority']['subject']['host'] = 'h'
        self.assertEqual(self.canon.digest_of(self.canon.task_part(t)), base)
        for label, edit in (('revision', lambda x: x.__setitem__('task_revision', 2)), ('schema', lambda x: x.__setitem__('schema_version', 'law.cvf.control/2')),
                            ('zone', lambda x: x['effects']['actions'][0].__setitem__('write_zone', 'output_new')),
                            ('requirement', lambda x: x['acceptance']['requirements'][0].__setitem__('statement', 'other'))):
            t = copy.deepcopy(task)
            edit(t)
            self.assertNotEqual(self.canon.digest_of(self.canon.task_part(t)), base, label)
        a = copy.deepcopy(task['effects']['actions'][0])
        a['content_use'] = ['internal_draft', 'sign']
        d1 = self.canon.digest_of(self.canon.action_part(a))
        a['content_use'] = ['sign', 'internal_draft']
        self.assertEqual(self.canon.digest_of(self.canon.action_part(a)), d1)
        task['acceptance']['requirements'].append({'req_id': 'REQ-9', 'statement': 'x', 'mandatory': False})
        d2 = self.canon.digest_of(self.canon.task_part(task))
        task['acceptance']['requirements'].reverse()
        self.assertNotEqual(self.canon.digest_of(self.canon.task_part(task)), d2)

    def test_duplicate_set_element_and_domain_violations(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        task['effects']['actions'][0]['targets'] = ['a', 'a']
        with self.assertRaises(self.canon.Unsupported) as cm:
            self.canon.action_part(task['effects']['actions'][0])
            self.canon.digest_of(self.canon.action_part(task['effects']['actions'][0]))
        self.assertEqual(cm.exception.reason, 'DUPLICATE_SET_ELEMENT')
        self.assertEqual(self.canon.domain_violations({'a': {'b': 1}}), [])
        self.assertTrue(self.canon.domain_violations({'a': 1.5}))
        self.assertTrue(self.canon.domain_violations({'a': 2 ** 60}))
        self.assertTrue(self.canon.domain_violations({'bad key!': 1}))
        self.assertTrue(self.canon.domain_violations({'a': 'é'}))


class HelperBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = load_module_from(ENTRY, 'law_cvf_entry_v3_helpers')
        cls.entry._load_package()
        cls.loader = importlib.import_module('law_cvf_check_v3.loader')
        cls.refs = importlib.import_module('law_cvf_check_v3.refs')
        cls.binding = importlib.import_module('law_cvf_check_v3.binding')
        cls.owners = cls.loader.load_owners()
        cls.ctx = cls.binding.make_policy_context(cls.owners.policy_bytes)

    def example(self, name):
        return read_json(os.path.join(V3C, 'examples', name))

    def index_of(self, bundle):
        data = dumps(bundle)
        parsed, _ = self.loader.parse_and_preflight(data, self.owners)
        self.assertIsNotNone(parsed)
        ok, reasons, _ = self.loader.validate_structure(parsed, self.owners)
        self.assertTrue(ok, reasons)
        return self.refs.build_index(self.refs.records_of(parsed))

    def report(self, bundle, rtype, stage=None, nth=0):
        index = self.index_of(bundle)
        pos = [i for i in range(index.count) if index._record(i)['record_type'] == rtype and (stage is None or index._record(i).get('stage') == stage)][nth]
        return self.binding.compare_binding(index, pos, self.ctx)

    @staticmethod
    def states(report):
        return dict((r.name, r.state) for r in report.relations)


class RefsHelpers(HelperBase):
    def test_index_keys_are_typed_and_collisions_are_ambiguous(self):
        index = self.index_of(self.example('ex04_pcn1_accepted_d4_complete.json'))
        task = self.example('ex04_pcn1_accepted_d4_complete.json')['records'][0]
        self.assertEqual(index.lookup('task', task['task_id'], 1).status, 'FOUND')
        for rev in (True, '1', 2):
            self.assertEqual(index.lookup('task', task['task_id'], rev).status, 'MISSING', repr(rev))
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        b['records'].append(copy.deepcopy(b['records'][0]))
        dup = self.index_of(b)
        self.assertEqual(dup.lookup('task', task['task_id'], 1).status, 'AMBIGUOUS')
        self.assertTrue(dup.collisions())
        with self.assertRaises(TypeError):
            self.refs.build_index('not records')

    def test_v3_claim_sites_receipt_and_user_acceptance(self):
        index = self.index_of(self.example('ex04_pcn1_accepted_d4_complete.json'))
        table = self.refs.collect_claims(index)
        receipt = table.group('receipt-4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a')
        acceptance = table.group('ua-1')
        self.assertEqual((receipt.status, receipt.kind), ('AGREE', 'effect_receipt'))
        self.assertEqual((acceptance.status, acceptance.kind), ('AGREE', 'user_acceptance'))
        self.assertEqual(table.malformed, ())
        locators = set()
        for pos in range(index.count):
            locators.update(o.locator for o in table.occurrences_at(pos))
        self.assertIn('records[3].receipt_ref', locators)
        self.assertIn('records[4].user_acceptance.ref', locators)
        self.assertEqual(table.group('grant-1').status, 'AGREE')
        self.assertIsNone(table.group('does-not-exist'))

    def test_conflicting_receipt_ref_is_a_conflict_and_metadata_only_is_not(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        out = [r for r in b['records'] if r['record_type'] == 'effect' and r['stage'] == 'OUTCOME'][0]
        res = [r for r in b['records'] if r['record_type'] == 'result'][0]
        res['user_acceptance']['ref']['ref_id'] = out['receipt_ref']['ref_id']
        index = self.index_of(b)
        group = self.refs.collect_claims(index).group(out['receipt_ref']['ref_id'])
        self.assertEqual(group.status, 'CONFLICT')
        self.assertIn('kind', group.conflict_fields)
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        out = [r for r in b['records'] if r['record_type'] == 'effect' and r['stage'] == 'OUTCOME'][0]
        out['receipt_ref']['attribution']['note'] = 'metadata only'
        self.assertEqual(self.refs.collect_claims(self.index_of(b)).group(out['receipt_ref']['ref_id']).status, 'AGREE')

    def test_grant_links(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        index = self.index_of(b)
        claims = self.refs.collect_claims(index)
        task_links = self.refs.link_grants(index, claims, 0)
        effect_links = self.refs.link_grants(index, claims, 2)
        self.assertEqual([l.state for l in task_links], ['LINKED'])
        self.assertEqual([l.state for l in effect_links], ['LINKED'])
        self.assertTrue(all(l.link_is_authority is False for l in task_links + effect_links))
        self.assertEqual(self.refs.link_grants(index, claims, 4), ())
        # grant record removed => nothing to link
        b2 = copy.deepcopy(b)
        b2['records'] = [r for r in b2['records'] if r['record_type'] != 'grant']
        i2 = self.index_of(b2)
        self.assertEqual([l.state for l in self.refs.link_grants(i2, self.refs.collect_claims(i2), 0)], ['NO_GRANT_RECORD'])
        # two grants answering for one ref_id => ambiguous
        b3 = copy.deepcopy(b)
        extra = copy.deepcopy(b3['records'][1])
        extra['grant_id'] = 'grant-1b'
        b3['records'].append(extra)
        i3 = self.index_of(b3)
        self.assertEqual([l.state for l in self.refs.link_grants(i3, self.refs.collect_claims(i3), 0)], ['AMBIGUOUS'])
        other_index = self.index_of(b)
        with self.assertRaises(ValueError):
            self.refs.link_grants(other_index, claims, 0)

    def test_result_objects_carry_the_observation_flags(self):
        index = self.index_of(self.example('ex04_pcn1_accepted_d4_complete.json'))
        table = self.refs.collect_claims(index)
        d = table.group('grant-1').as_dict()
        self.assertEqual((d['bytes_observed'], d['authenticity_observed'], d['semantic_verified']), (False, False, False))
        self.assertEqual(d['resolution'], 'INLINE_CLAIM_ONLY')


class BindingHelpers(HelperBase):
    def test_policy_context_matches_the_vector_and_rejects_bad_input(self):
        vectors = read_json(os.path.join(V3C, 'vectors.json'))
        self.assertEqual((self.ctx.state, self.ctx.digest, self.ctx.literals_ok), ('COMPUTED', vectors['policy_digest']['digest'], True))
        with self.assertRaises(TypeError):
            self.binding.make_policy_context('text')
        self.assertEqual(self.binding.make_policy_context(b'{').state, 'UNSUPPORTED')
        wrong = json.loads(self.owners.policy_bytes)
        wrong['policy_version'] = 'law.cvf.routing/2'
        ctx = self.binding.make_policy_context(dumps(wrong))
        self.assertEqual((ctx.state, ctx.literals_ok, ctx.reason), ('UNSUPPORTED', False, 'POLICY_LITERAL_MISMATCH'))

    def test_accepted_example_recomputes_completely_for_effects_and_result(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        for rtype, stage, check in (('effect', 'REQUEST', ('B-ACTION-OWN', 'B-ACTION-IN-TASK')), ('effect', 'OUTCOME', ('B-ACTION-OWN', 'B-OUT-EFFECT')),
                                    ('result', None, ('B-OUT-RESULT',))):
            rep = self.report(b, rtype, stage)
            states = self.states(rep)
            self.assertTrue(rep.applicable)
            for name in ('B-REF', 'B-INTENT', 'B-TASK', 'B-CONTEXT', 'B-POLICY', 'B-INPUTS') + check:
                self.assertEqual(states[name], 'MATCH', (rtype, stage, name))
            for lit in ('B-LIT.bind_version', 'B-LIT.evaluation_basis', 'B-LIT.policy_version'):
                self.assertEqual(states[lit], 'MATCH')
            self.assertTrue(rep.recomputation_complete, (rtype, stage))
            d = rep.as_dict()
            self.assertEqual((d['relations'][0]['bytes_observed'], d['relations'][0]['semantic_verified']), (False, False))

    def test_request_has_no_outputs_and_result_has_no_action_digest_by_default(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        req = self.states(self.report(b, 'effect', 'REQUEST'))
        self.assertEqual(req['B-OUTPUTS'], 'NOT_BOUND')
        self.assertNotIn('B-OUT-EFFECT', req)
        res = self.states(self.report(b, 'result'))
        self.assertEqual(res['B-ACTION-CLAIM'], 'NOT_BOUND')
        self.assertNotIn('B-ACTION-OWN', res)

    def test_task_record_has_no_binding_relation(self):
        index = self.index_of(self.example(EX_WORKING))
        rep = self.binding.compare_binding(index, 0, self.ctx)
        self.assertEqual((rep.applicable, rep.recomputation_complete, rep.relations[0].state), (False, False, 'NOT_APPLICABLE'))

    def test_stale_binding_is_a_mismatch_of_exactly_the_stale_parts(self):
        b = self.example('ex07_pcn1_binding_stale.json')
        states = self.states(self.report(b, 'effect', 'OUTCOME'))
        self.assertEqual(states['B-TASK'], 'MISMATCH')
        self.assertEqual(states['B-INTENT'], 'MATCH', 'the intent did not change, only the task reading did')
        self.assertEqual(states['B-REF'], 'MATCH')
        self.assertTrue(self.report(b, 'effect', 'OUTCOME').recomputation_complete, 'MISMATCH on a fully recomputed digest still counts as computed')

    def test_outputs_vs_artifacts_exact_mismatch_missing_null_and_duplicate(self):
        base = self.example('ex04_pcn1_accepted_d4_complete.json')

        def out_effect(b):
            return [r for r in b['records'] if r['record_type'] == 'effect' and r['stage'] == 'OUTCOME'][0]

        b = copy.deepcopy(base)
        out_effect(b)['binding']['outputs'][0]['digest'] = 'sha256:' + '9' * 64
        rep = self.report(b, 'effect', 'OUTCOME')
        self.assertEqual(self.states(rep)['B-OUT-EFFECT'], 'MISMATCH')
        b = copy.deepcopy(base)
        del out_effect(b)['binding']['outputs']
        rep = self.report(b, 'effect', 'OUTCOME')
        self.assertEqual(self.states(rep)['B-OUT-EFFECT'], 'NOT_BOUND')
        b = copy.deepcopy(base)
        art = out_effect(b)['outcome']['artifacts']
        art.append(copy.deepcopy(art[0]))
        out_effect(b)['binding']['outputs'].append(copy.deepcopy(art[0]))
        rep = self.report(b, 'effect', 'OUTCOME')
        rel = [r for r in rep.relations if r.name == 'B-OUT-EFFECT'][0]
        self.assertEqual((rel.state, rel.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        self.assertFalse(rep.recomputation_complete)
        b = copy.deepcopy(base)
        out_effect(b)['binding']['outputs'] = []
        self.assertEqual(self.states(self.report(b, 'effect', 'OUTCOME'))['B-OUT-EFFECT'], 'MISMATCH', 'outputs [] is not absent')
        b = copy.deepcopy(base)
        [r for r in b['records'] if r['record_type'] == 'result'][0]['binding']['outputs'] = []
        self.assertEqual(self.states(self.report(b, 'result'))['B-OUT-RESULT'], 'MISMATCH')

    def test_malformed_outputs_are_unsupported_not_not_bound(self):
        index_data = self.example('ex04_pcn1_accepted_d4_complete.json')
        out = [r for r in index_data['records'] if r['record_type'] == 'effect' and r['stage'] == 'OUTCOME'][0]
        out['binding']['outputs'] = None
        parsed = index_data
        index = self.refs.build_index(self.refs.records_of(parsed))
        pos = [i for i in range(index.count) if index._record(i).get('stage') == 'OUTCOME'][0]
        rep = self.binding.compare_binding(index, pos, self.ctx)
        rel = [r for r in rep.relations if r.name == 'B-OUT-EFFECT'][0]
        self.assertEqual((rel.state, rel.reason), ('UNSUPPORTED', 'MALFORMED_RECORD'))

    def test_action_digest_is_optional_but_compared_when_present(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        result = [r for r in b['records'] if r['record_type'] == 'result'][0]
        task_digest = [r for r in b['records'] if r['record_type'] == 'effect'][0]['binding']['action_digest']
        result['binding']['action_digest'] = task_digest
        rep = self.report(b, 'result')
        claim = [r for r in rep.relations if r.name == 'B-ACTION-CLAIM'][0]
        self.assertEqual((claim.state, claim.indexes), ('MATCH', (0,)))
        self.assertIn('SUBSET_OF_ACTIONS_ONLY', claim.limitations)
        result['binding']['action_digest'] = 'sha256:' + '1' * 64
        self.assertEqual(self.states(self.report(b, 'result'))['B-ACTION-CLAIM'], 'MISMATCH')
        out = [r for r in b['records'] if r['record_type'] == 'effect' and r['stage'] == 'OUTCOME'][0]
        out['binding']['action_digest'] = 'sha256:' + '2' * 64
        self.assertEqual(self.states(self.report(b, 'effect', 'OUTCOME'))['B-ACTION-OWN'], 'MISMATCH')
        del out['binding']['action_digest']
        self.assertEqual(self.states(self.report(b, 'effect', 'OUTCOME'))['B-ACTION-OWN'], 'NOT_BOUND')

    def test_missing_and_ambiguous_task_are_not_mismatches(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        gone = copy.deepcopy(b)
        gone['records'] = [r for r in gone['records'] if r['record_type'] != 'task']
        rep = self.report(gone, 'effect', 'REQUEST')
        states = self.states(rep)
        for name in ('B-REF', 'B-INTENT', 'B-TASK', 'B-CONTEXT', 'B-INPUTS'):
            self.assertEqual(states[name], 'INCOMPLETE', name)
        self.assertFalse(rep.recomputation_complete)
        dup = copy.deepcopy(b)
        dup['records'].append(copy.deepcopy(dup['records'][0]))
        rep = self.report(dup, 'effect', 'REQUEST')
        self.assertEqual(self.states(rep)['B-TASK'], 'AMBIGUOUS')
        self.assertFalse(rep.recomputation_complete)

    def test_one_sided_and_peer_claims_never_count_as_recomputation(self):
        b = self.example('ex04_pcn1_accepted_d4_complete.json')
        req = [r for r in b['records'] if r['record_type'] == 'effect' and r['stage'] == 'REQUEST'][0]['binding']
        out = [r for r in b['records'] if r['record_type'] == 'effect' and r['stage'] == 'OUTCOME'][0]['binding']
        rels = dict((r.name, r) for r in self.binding.compare_peer_bindings(req, out))
        self.assertEqual(rels['peer.outputs'].state, 'ONE_SIDED')
        self.assertEqual(rels['peer.accepted_task_digest'].state, 'MATCH')
        self.assertEqual(rels['peer.accepted_task_digest'].basis, 'PEER_CLAIM')
        self.assertEqual(rels['peer.outputs'].basis, 'PEER_CLAIM')
        with self.assertRaises(TypeError):
            self.binding.compare_peer_bindings([], {})

    def test_object_set_modes_are_exact_or_cover_and_asymmetric(self):
        o = {'path': 'a', 'digest': 'sha256:' + '1' * 64}
        q = dict(o, revision='2')
        rel = self.binding.compare_object_sets([o], [o], 'EXACT_QUALIFIED')
        self.assertEqual((rel.state, rel.limitations), ('MATCH', ('UNVERIFIED_RAW_BYTES',)))
        self.assertEqual(self.binding.compare_object_sets([o], [q], 'EXACT_QUALIFIED').state, 'MISMATCH')
        self.assertEqual(self.binding.compare_object_sets([o], [q], 'COVER_REQUIRED_QUALIFIERS').state, 'MATCH')
        self.assertEqual(self.binding.compare_object_sets([q], [o], 'COVER_REQUIRED_QUALIFIERS').state, 'MISMATCH')
        rel = self.binding.compare_object_sets([o, o], [o], 'EXACT_QUALIFIED')
        self.assertEqual((rel.state, rel.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        self.assertEqual(self.binding.compare_object_sets([], [], 'EXACT_QUALIFIED').state, 'MATCH')
        self.assertEqual(self.binding.compare_object_sets(None, None, 'EXACT_QUALIFIED').state, 'NOT_BOUND')
        self.assertEqual(self.binding.compare_object_sets(None, [o], 'EXACT_QUALIFIED').state, 'ONE_SIDED')
        # role is a v3 field of output objects but not part of the object identity
        self.assertEqual(self.binding.compare_object_sets([dict(o, role='ACTUAL_BYTES')], [dict(o, role='ACTUAL_BYTES')], 'EXACT_QUALIFIED').state, 'MATCH')
        with self.assertRaises(ValueError):
            self.binding.compare_object_sets([o], [o], 'LOOSE')
        with self.assertRaises(ValueError):
            self.binding.compare_object_sets([o], [o], 'EXACT_QUALIFIED', name='made up')
        with self.assertRaises(ValueError):
            self.binding.compare_object_sets([o], [o], 'EXACT_QUALIFIED', name='B-OUT-EFFECT', basis='RECOMPUTED')

    def test_recompute_task_is_per_part_and_rejects_non_dict(self):
        task = self.example(EX_WORKING)['records'][0]
        d = self.binding.recompute_task(task)
        self.assertEqual((d.intent.state, d.accepted_task.state, d.context.state), ('COMPUTED', 'COMPUTED', 'COMPUTED'))
        self.assertEqual(len(d.actions), 1)
        self.assertEqual(d.actions[0].digest, self.entry_canon().digest_of(self.entry_canon().action_part(task['effects']['actions'][0])))
        task['intent']['main_interpretation'] = 'é'
        d = self.binding.recompute_task(task)
        self.assertEqual(d.accepted_task.state, 'UNSUPPORTED')
        self.assertEqual(d.intent.state, 'COMPUTED', 'one unsupported part does not hide the others')
        with self.assertRaises(TypeError):
            self.binding.recompute_task([])

    def entry_canon(self):
        return importlib.import_module('law_cvf_check_v3.canon')

    def test_argument_errors(self):
        index = self.index_of(self.example(EX_WORKING))
        for args, exc in (((None, 0, self.ctx), TypeError), ((index, 0, None), TypeError), ((index, True, self.ctx), TypeError),
                          ((index, 99, self.ctx), ValueError), ((index, -1, self.ctx), ValueError)):
            with self.assertRaises(exc):
                self.binding.compare_binding(*args)


if __name__ == '__main__':
    unittest.main()
