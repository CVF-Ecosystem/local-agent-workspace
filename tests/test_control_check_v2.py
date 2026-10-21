"""G-02-C2/S1: kiểm nền checker v2 candidate / checks for the v2 candidate checker foundation.

Chỉ S1 (entrypoint, loader strict, canon, router CLI v1, output FOUNDATION_ONLY). Không kiểm binding/route/gate/guard của workflow:
S1 chưa có evaluator, nên mọi bundle hợp lệ về cấu trúc đều BLOCKED. Không dùng kết quả này để suy v2 đã đánh giá được điều gì.
S1 only: entrypoint, strict loader, canon, v1 CLI router, FOUNDATION_ONLY output. There is no evaluator yet, so every structurally
valid bundle is BLOCKED; nothing here shows that v2 evaluates any workflow.
Thiếu jsonschema thì thất bại rõ, không skip / a missing jsonschema fails loudly, never skips.
"""
import contextlib
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
ENTRY = os.path.join(CHECKS, 'control_check_v2.py')
PKG = os.path.join(CHECKS, 'v2')
V1_CHECKER = os.path.join(CHECKS, 'control_check.py')
V1_EXAMPLES = os.path.join(CVF, 'contracts', 'examples')
V2C = os.path.join(CVF, 'contracts', 'v2')
V2R = os.path.join(CVF, 'rules', 'v2')
REF_TEST = os.path.join(ROOT, 'tests', 'test_control_v2_candidate.py')

# Hash 16 ký tự đầu của owner v1 và test v1/C1 phải không đổi; pin này không được sửa để test xanh.
# 16-char prefixes of v1 owners and the v1/C1 tests must not change; do not edit these pins to turn tests green.
V1_PINS = {
    ('contracts', 'control.schema.json'): '933265fa7b113941',
    ('contracts', 'CONTROL_CONTRACT.md'): 'd22848dee934d4cf',
    ('contracts', 'examples', 'EXPECTED.json'): 'c72e1e6b2bfda8ff',
    ('rules', 'ROUTING_POLICY.json'): '8db011baf5d5c5a0',
    ('rules', 'CONTROL_RULES.md'): 'ad3337b9baee23e4',
    ('checks', 'control_check.py'): 'f95bfc367bb7f470',
}
TEST_PINS = {
    'test_control_check.py': '454e3f4944825809',
    'test_control_v2_candidate.py': 'b32d7b3ff0e8a014',
}

OUTPUT_KEYS = ['check_version', 'contract', 'selection', 'candidate_status', 'implementation_stage', 'evaluation_basis',
               'phase', 'disposition', 'effect_authorized', 'assurance_level', 'init_error', 'reasons', 'details',
               'owners', 'coverage', 'objects', 'gates']
COVERAGE_FALSE = {'binding_evaluated': False, 'routing_evaluated': False, 'gates_evaluated': False,
                  'artifact_bytes_observed': False, 'actual_operation_observed': False,
                  'requirements_semantic_verified': False}
PHASES = ('dispatch', 'effect', 'accept')
NOT_IMPL = 'CANDIDATE_EVALUATION_NOT_IMPLEMENTED'
V2 = 'law.cvf.control/2'


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


def setUpModule():
    if not HAVE_JSONSCHEMA:
        raise RuntimeError('jsonschema>=4.18 không có / not installed: BLOCKED, không tự cài / not auto-installed')


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.mkdtemp(prefix='law-c2-s1-')
        cls.entry = load_module_from(ENTRY, 'law_cvf_entry_under_test')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def example(self, name):
        return read_json(os.path.join(V2C, 'examples', name))

    def example_bytes(self, name):
        return read_bytes(os.path.join(V2C, 'examples', name))

    def write_scratch(self, name, data):
        path = os.path.join(self.scratch, name)
        with open(path, 'wb') as f:
            f.write(data)
        return path

    def run_cli(self, argv, entry=True):
        exe = [sys.executable, '-I', ENTRY if entry else V1_CHECKER]
        proc = subprocess.run(exe + list(argv), cwd=self.scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, proc.stdout, proc.stderr

    def check(self, data, phase='effect'):
        return self.entry.check_bytes(data, phase, 'v2')

    def assert_foundation_shape(self, res):
        self.assertEqual(list(res.keys()), OUTPUT_KEYS)
        self.assertEqual(res['check_version'], 'law.cvf.check/2')
        self.assertEqual(res['contract'], 'v2')
        self.assertEqual(res['candidate_status'], 'CANDIDATE_NOT_ACTIVE')
        self.assertEqual(res['implementation_stage'], 'S1_FOUNDATION_ONLY')
        self.assertIs(res['effect_authorized'], False)
        self.assertEqual(res['assurance_level'], 'UNVERIFIED')
        self.assertIsInstance(res['init_error'], bool)
        self.assertEqual(res['reasons'], sorted(set(res['reasons'])))
        self.assertTrue(all(isinstance(d, str) for d in res['details']))
        self.assertEqual(sorted(res['owners']), ['policy_sha256', 'schema_sha256'])
        cov = res['coverage']
        self.assertEqual(cov['owner_protection'], 'NOT_PROVEN')
        self.assertIsInstance(cov['record_structure_checked'], bool)
        for k, v in COVERAGE_FALSE.items():
            self.assertIs(cov[k], v, k)
        self.assertEqual(sorted(cov), sorted(set(COVERAGE_FALSE) | {'record_structure_checked', 'owner_protection'}))
        self.assertEqual(res['objects'], [])
        self.assertEqual(res['gates'], [])
        self.assertNotIn(res['disposition'], ('PASS', 'NOT_APPLICABLE'))


class OwnersUntouched(unittest.TestCase):
    def test_v1_owner_hashes_unchanged(self):
        for rel, want in V1_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(CVF, *rel)), want, '/'.join(rel))

    def test_v1_and_c1_tests_unchanged(self):
        for name, want in TEST_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(ROOT, 'tests', name)), want, name)

    def test_package_tree_is_s1_plus_the_two_s2_modules(self):
        names = sorted(n for n in os.listdir(PKG) if n.endswith(('.py', '.md')))
        self.assertEqual(names, ['README.md', '__init__.py', 'binding.py', 'canon.py', 'loader.py', 'refs.py'])

    def test_product_does_not_import_tests_or_touch_sys_path(self):
        for path in [ENTRY] + [os.path.join(PKG, n) for n in ('__init__.py', 'canon.py', 'loader.py', 'refs.py', 'binding.py')]:
            src = read_bytes(path).decode('utf-8')
            for needle in ('import tests', 'from tests', 'sys.path', '--root', '--basis', '--trust', '--schema', '--policy'):
                self.assertFalse(needle in src, '%s contains %r' % (os.path.basename(path), needle))


class OutputContract(Base):
    def test_valid_examples_are_blocked_never_pass(self):
        valid = [c['file'] for c in read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))['cases'] if c['schema_valid']]
        self.assertEqual(len(valid), 13)
        for name in valid:
            for phase in PHASES:
                with self.subTest(name=name, phase=phase):
                    res = self.check(self.example_bytes(name), phase)
                    self.assert_foundation_shape(res)
                    self.assertEqual(res['disposition'], 'BLOCKED')
                    self.assertEqual(res['reasons'], [NOT_IMPL])
                    self.assertEqual(res['phase'], phase)
                    self.assertEqual(res['selection'], 'API_EXPLICIT')
                    self.assertEqual(res['evaluation_basis'], 'COOPERATIVE_WORKFLOW')
                    self.assertIs(res['init_error'], False)
                    self.assertIs(res['coverage']['record_structure_checked'], True)

    def test_owner_hashes_are_the_bytes_actually_read(self):
        res = self.check(self.example_bytes('ex02_mutation_reviewed_bound.json'))
        self.assertEqual(res['owners']['schema_sha256'], hashlib.sha256(read_bytes(os.path.join(V2C, 'control.schema.json'))).hexdigest())
        self.assertEqual(res['owners']['policy_sha256'], hashlib.sha256(read_bytes(os.path.join(V2R, 'ROUTING_POLICY.json'))).hexdigest())

    def test_single_record_input_is_accepted_like_v1(self):
        task = [r for r in self.example('ex02_mutation_reviewed_bound.json')['records'] if r['record_type'] == 'task'][0]
        res = self.check(dumps(task))
        self.assertEqual((res['disposition'], res['reasons']), ('BLOCKED', [NOT_IMPL]))

    def test_api_argument_errors(self):
        good = self.example_bytes('ex02_mutation_reviewed_bound.json')
        for bad in ('{}', bytearray(b'{}'), memoryview(b'{}'), None, 5):
            with self.subTest(data=type(bad).__name__):
                with self.assertRaises(TypeError):
                    self.entry.check_bytes(bad, 'effect', 'v2')
        for contract in ('v1', 'V2', '', None, 'v3'):
            with self.subTest(contract=contract):
                with self.assertRaises(ValueError):
                    self.entry.check_bytes(good, 'effect', contract)
        for phase in ('', 'Dispatch', 'integration', None):
            with self.subTest(phase=phase):
                with self.assertRaises(ValueError):
                    self.entry.check_bytes(good, phase, 'v2')

    def test_public_surface_has_no_injection_or_check_records(self):
        public = sorted(n for n in dir(self.entry) if not n.startswith('_') and callable(getattr(self.entry, n))
                        and getattr(getattr(self.entry, n), '__module__', None) == self.entry.__name__)
        self.assertEqual(public, ['check_bytes', 'exit_code', 'main'])


class RefusalMatrix(Base):
    """Version → basis → binding literal → schema → canonical domain. Version/basis/literal = UNSUPPORTED; structure = DENY."""

    def assert_result(self, data, disposition, reasons, phase='effect'):
        res = self.check(data, phase)
        self.assert_foundation_shape(res)
        self.assertEqual((res['disposition'], res['reasons']), (disposition, sorted(reasons)), res['details'])
        self.assertIs(res['init_error'], False)
        self.assertIs(res['coverage']['record_structure_checked'], False)
        return res

    def ex02(self):
        return copy.deepcopy(self.example('ex02_mutation_reviewed_bound.json'))

    def record(self, bundle, rtype, index=0):
        return [r for r in bundle['records'] if r['record_type'] == rtype][index]

    def test_example_files_from_expected(self):
        table = {
            'ex04_main_authored_user_confirmation.json': ('DENY', ['SCHEMA_INVALID']),
            'ex15_v1_record_in_v2_bundle.json': ('UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN', 'VERSION_MIXED']),
            'ex16_unknown_schema_version.json': ('UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN', 'VERSION_MIXED']),
            'ex17_basis_missing.json': ('UNSUPPORTED', ['BASIS_MISSING']),
            'ex18_basis_unknown.json': ('UNSUPPORTED', ['BASIS_MIXED', 'BASIS_UNKNOWN']),
            'ex20_external_send_missing_payload.json': ('DENY', ['SCHEMA_INVALID']),
            'ex21_zero_object_pass.json': ('DENY', ['SCHEMA_INVALID']),
            'ex22_worker_sets_acceptance.json': ('DENY', ['SCHEMA_INVALID']),
            'ex23_v1_binding_reused.json': ('UNSUPPORTED', ['BINDING_VERSION_UNKNOWN']),
        }
        invalid = sorted(c['file'] for c in read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))['cases'] if not c['schema_valid'])
        self.assertEqual(sorted(table), invalid)
        for name, (disp, reasons) in table.items():
            with self.subTest(name):
                self.assert_result(self.example_bytes(name), disp, reasons)

    def test_version_missing(self):
        b = self.ex02()
        del self.record(b, 'task')['schema_version']
        self.assert_result(dumps(b), 'UNSUPPORTED', ['VERSION_MISSING'])
        b = self.ex02()
        del b['schema_version']
        self.assert_result(dumps(b), 'UNSUPPORTED', ['VERSION_MISSING'])

    def test_preflight_diagnostics_do_not_echo_record_type_values(self):
        for marker in ('law_private_marker', 'law_private_marker\n', 'task\n'):
            with self.subTest(marker=repr(marker)):
                b = self.ex02()
                b['records'][0]['record_type'] = marker
                b['records'][0].pop('schema_version', None)
                res = self.assert_result(dumps(b), 'UNSUPPORTED', ['VERSION_MISSING'])
                self.assertEqual(res['details'], ['schema_version missing in: records[0]'])

    def test_diagnostic_path_key_requires_full_match(self):
        self.entry._load_package()
        loader = importlib.import_module(self.entry.PACKAGE_NAME + '.loader')
        self.assertEqual(loader._safe_path(['task_revision']), '.task_revision')
        self.assertEqual(loader._safe_path(['task_revision\n']), '.?')

    def test_all_v1_bundle_is_refused_with_explicit_hint_and_never_tried(self):
        b = self.ex02()
        b['schema_version'] = 'law.cvf.control/1'
        for r in b['records']:
            r['schema_version'] = 'law.cvf.control/1'
        res = self.assert_result(dumps(b), 'UNSUPPORTED', ['SCHEMA_VERSION_UNKNOWN'])
        self.assertTrue(any('--contract v1' in d for d in res['details']))
        self.assertNotIn('law_cvf_check_v1', sys.modules)

    def test_non_string_and_garbage_versions(self):
        for value in (2, None, ['law.cvf.control/2'], 'law.cvf.control/2 ', 'LAW.CVF.CONTROL/2', 'law.cvf.control/3'):
            with self.subTest(value=value):
                b = self.ex02()
                self.record(b, 'review')['schema_version'] = value
                res = self.check(dumps(b))
                self.assertEqual(res['disposition'], 'UNSUPPORTED')
                self.assertIn('SCHEMA_VERSION_UNKNOWN', res['reasons'])

    def test_basis_variants(self):
        b = self.ex02()
        del self.record(b, 'grant')['evaluation_basis']
        self.assert_result(dumps(b), 'UNSUPPORTED', ['BASIS_MISSING'])
        b = self.ex02()
        self.record(b, 'grant')['evaluation_basis'] = 'TRUSTED_ENFORCED'
        self.assert_result(dumps(b), 'UNSUPPORTED', ['BASIS_MIXED', 'BASIS_UNKNOWN'])
        b = self.ex02()
        for r in [b] + b['records']:
            r['evaluation_basis'] = 'TRUSTED_ENFORCED'
            if 'binding' in r:
                r['binding']['evaluation_basis'] = 'TRUSTED_ENFORCED'
        self.assert_result(dumps(b), 'UNSUPPORTED', ['BASIS_UNKNOWN'])
        b = self.ex02()
        self.record(b, 'review')['binding']['evaluation_basis'] = 'OTHER'
        self.assert_result(dumps(b), 'UNSUPPORTED', ['BASIS_MISMATCH', 'BASIS_MIXED', 'BASIS_UNKNOWN'])
        b = self.ex02()
        del self.record(b, 'review')['binding']['evaluation_basis']
        self.assert_result(dumps(b), 'UNSUPPORTED', ['BASIS_MISSING'])

    def test_binding_literals(self):
        cases = {
            'bind_version missing': lambda r: r['binding'].pop('bind_version'),
            'bind_version v1': lambda r: r['binding'].__setitem__('bind_version', 'law.cvf.bind/1'),
            'policy_version v1': lambda r: r['binding'].__setitem__('policy_version', 'law.cvf.routing/1'),
            'policy_digest missing': lambda r: r['binding'].pop('policy_digest'),
        }
        for label, mutate in cases.items():
            with self.subTest(label):
                b = self.ex02()
                mutate(self.record(b, 'review'))
                self.assert_result(dumps(b), 'UNSUPPORTED', ['BINDING_VERSION_UNKNOWN'])

    def test_schema_invalid_after_literals_is_deny_and_does_not_echo_values(self):
        b = self.ex02()
        self.record(b, 'task')['task_revision'] = 'SECRET-VALUE-123'
        res = self.assert_result(dumps(b), 'DENY', ['SCHEMA_INVALID'])
        self.assertNotIn('SECRET-VALUE-123', json.dumps(res))
        self.assertTrue(res['details'])

    def test_routing_policy_record_is_not_checkable(self):
        res = self.assert_result(read_bytes(os.path.join(V2R, 'ROUTING_POLICY.json')), 'DENY', ['SCHEMA_INVALID'])
        self.assertTrue(any('routing_policy' in d for d in res['details']))

    def test_malformed_input(self):
        cases = {
            'duplicate key': b'{"DUPKEYSECRET": 1, "DUPKEYSECRET": 2}',
            'NaN': b'{"a": NaN}',
            'Infinity': b'{"a": Infinity}',
            'invalid utf8': b'\xff\xfe\x00',
            'not json': b'not json',
            'top-level array': b'[]',
            'top-level string': b'"x"',
            'empty': b'',
            'too large': b' ' * (8 * 1024 * 1024 + 1),
        }
        for label, data in cases.items():
            with self.subTest(label):
                res = self.assert_result(data, 'DENY', ['INPUT_MALFORMED'])
                self.assertNotIn('DUPKEYSECRET', json.dumps(res))
                self.assertIsNone(res['evaluation_basis'])

    def test_duplicate_key_nested_in_a_valid_bundle(self):
        text = self.example_bytes('ex02_mutation_reviewed_bound.json').decode('utf-8').replace(
            '"task_revision": 1', '"task_revision": 1, "task_revision": 2', 1)
        self.assertIn('"task_revision": 1, "task_revision": 2', text)
        self.assert_result(text.encode('utf-8'), 'DENY', ['INPUT_MALFORMED'])

    def test_canonical_domain_is_unsupported_not_guessed(self):
        base = self.example_bytes('ex02_mutation_reviewed_bound.json').decode('utf-8')
        cases = {
            'float revision': base.replace('"task_revision": 1', '"task_revision": 1.0', 1),
            'huge integer': base.replace('"task_revision": 1', '"task_revision": %d' % (2 ** 60), 1),
            'non-NFC string': base.replace('"main_interpretation": "', '"main_interpretation": "e\\u0301 ', 1),
            'lone surrogate': base.replace('"main_interpretation": "', '"main_interpretation": "\\ud800 ', 1),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assertNotEqual(text, base, label)
                res = self.assert_result(text.encode('utf-8'), 'UNSUPPORTED', ['UNSUPPORTED_BINDING_PART'])
                json.dumps(res, ensure_ascii=True).encode('ascii')

    def test_bundle_bom_is_tolerated_like_v1(self):
        res = self.check(b'\xef\xbb\xbf' + self.example_bytes('ex02_mutation_reviewed_bound.json'))
        self.assertEqual(res['reasons'], [NOT_IMPL])


class LoaderInit(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.entry._load_package()
        cls.loader = importlib.import_module('law_cvf_check_v2.loader')

    def owner_tree(self, mutate_schema=None, mutate_policy=None, drop=None):
        root = tempfile.mkdtemp(dir=self.scratch)
        os.makedirs(os.path.join(root, 'contracts', 'v2'))
        os.makedirs(os.path.join(root, 'rules', 'v2'))
        schema = read_json(os.path.join(V2C, 'control.schema.json'))
        policy = read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))
        if mutate_schema:
            mutate_schema(schema)
        if mutate_policy:
            mutate_policy(policy)
        for rel, obj in ((('contracts', 'v2', 'control.schema.json'), schema), (('rules', 'v2', 'ROUTING_POLICY.json'), policy)):
            if drop != rel[-1]:
                with open(os.path.join(root, *rel), 'wb') as f:
                    f.write(json.dumps(obj).encode('utf-8'))
        return root

    def init_failure(self, root):
        with self.assertRaises(self.loader.InitFailure) as cm:
            self.loader.load_owners(root)
        return cm.exception

    def test_real_owners_load(self):
        owners = self.loader.load_owners()
        self.assertEqual(len(owners.schema_sha256), 64)
        self.assertEqual(len(owners.policy_sha256), 64)

    def test_missing_owner_files(self):
        for name, reason in (('control.schema.json', 'OWNER_UNREADABLE'), ('ROUTING_POLICY.json', 'OWNER_UNREADABLE')):
            with self.subTest(name):
                self.assertIn(reason, self.init_failure(self.owner_tree(drop=name)).reasons)

    def test_remote_ref_is_refused(self):
        def add_remote(schema):
            schema['$defs']['id'] = {'$ref': 'https://example.invalid/x.json'}
        exc = self.init_failure(self.owner_tree(mutate_schema=add_remote))
        self.assertIn('OWNER_INVALID', exc.reasons)

    def test_remote_dynamic_ref_is_refused_before_retrieval(self):
        def add_remote(schema):
            schema['allOf'] = [{'$dynamicRef': 'https://example.invalid/s1-dynamic-canary'}]
        root = self.owner_tree(mutate_schema=add_remote)
        with mock.patch('urllib.request.urlopen', side_effect=AssertionError('retrieval canary')) as retrieval:
            exc = self.init_failure(root)
        self.assertIn('OWNER_INVALID', exc.reasons)
        retrieval.assert_not_called()
        self.assertTrue(self.loader._has_remote_ref({'$dynamicRef': 'https://example.invalid/x'}))

    def test_reference_registry_denies_rebased_fragment_without_network(self):
        def rebase(schema):
            schema['allOf'] = [{'$id': 'https://example.invalid/rebased/', '$ref': '#missing'}]
        root = self.owner_tree(mutate_schema=rebase)
        with mock.patch('urllib.request.urlopen', side_effect=AssertionError('retrieval canary')) as retrieval:
            exc = self.init_failure(root)
        self.assertIn('OWNER_INVALID', exc.reasons)
        retrieval.assert_not_called()

    def test_reference_registry_denies_retrieval_even_if_scan_misses(self):
        def add_remote(schema):
            schema['allOf'] = [{'$ref': 'https://example.invalid/s1-registry-canary'}]
        root = self.owner_tree(mutate_schema=add_remote)
        with mock.patch.object(self.loader, '_has_remote_ref', return_value=False), \
                mock.patch('urllib.request.urlopen', side_effect=AssertionError('retrieval canary')) as retrieval:
            exc = self.init_failure(root)
        self.assertIn('OWNER_INVALID', exc.reasons)
        retrieval.assert_not_called()

    def test_owner_literals(self):
        exc = self.init_failure(self.owner_tree(mutate_schema=lambda s: s.__setitem__('$id', 'urn:law:cvf:control:1')))
        self.assertIn('SCHEMA_VERSION_UNKNOWN', exc.reasons)
        exc = self.init_failure(self.owner_tree(mutate_policy=lambda p: p.__setitem__('policy_version', 'law.cvf.routing/1')))
        self.assertIn('POLICY_VERSION_UNKNOWN', exc.reasons)
        exc = self.init_failure(self.owner_tree(mutate_policy=lambda p: p.__setitem__('status', 'ACTIVE')))
        self.assertIn('OWNER_INVALID', exc.reasons)

    def test_invalid_schema_and_policy(self):
        exc = self.init_failure(self.owner_tree(mutate_schema=lambda s: s.__setitem__('type', 5)))
        self.assertIn('OWNER_INVALID', exc.reasons)
        exc = self.init_failure(self.owner_tree(mutate_policy=lambda p: p.__setitem__('main_may_downgrade', True)))
        self.assertIn('OWNER_INVALID', exc.reasons)

    def test_duplicate_key_in_owner(self):
        root = self.owner_tree()
        path = os.path.join(root, 'rules', 'v2', 'ROUTING_POLICY.json')
        text = read_bytes(path).decode('utf-8')
        with open(path, 'wb') as f:
            f.write(text.replace('{', '{"policy_id": "x", ', 1).encode('utf-8'))
        self.assertIn('OWNER_INVALID', self.init_failure(root).reasons)

    def test_dependency_missing_or_too_old_is_init_error_exit_2(self):
        data = self.example_bytes('ex02_mutation_reviewed_bound.json')
        for label, patch in (('missing', mock.patch.object(self.loader, '_import_jsonschema', side_effect=ImportError('x'))),
                             ('too old', mock.patch.object(self.loader, '_jsonschema_version', return_value=(4, 17)))):
            with self.subTest(label), patch:
                res = self.check(data)
                self.assert_foundation_shape(res)
                self.assertEqual((res['disposition'], res['reasons'], res['init_error']), ('UNSUPPORTED', ['DEPENDENCY_MISSING'], True))
                self.assertEqual(res['owners'], {'schema_sha256': None, 'policy_sha256': None})
                self.assertIsNone(res['evaluation_basis'])
                self.assertEqual(self.entry.exit_code(res), 2)

    def test_owner_failure_is_init_error_with_hash_of_what_was_read(self):
        bad_root = self.owner_tree(mutate_policy=lambda p: p.__setitem__('main_may_downgrade', True))
        with mock.patch.object(self.loader, 'default_cvf_dir', return_value=bad_root):
            res = self.check(self.example_bytes('ex02_mutation_reviewed_bound.json'))
        self.assert_foundation_shape(res)
        self.assertEqual((res['disposition'], res['init_error']), ('UNSUPPORTED', True))
        self.assertIn('OWNER_INVALID', res['reasons'])
        self.assertIsNotNone(res['owners']['schema_sha256'])
        self.assertIsNotNone(res['owners']['policy_sha256'])
        self.assertEqual(self.entry.exit_code(res), 2)


class NoObservation(Base):
    def test_valid_bundle_reads_no_artifact_and_uses_no_network(self):
        canary = self.write_scratch('canary.txt', b'CANARY-CONTENT')
        bundle = self.example('ex02_mutation_reviewed_bound.json')
        task = [r for r in bundle['records'] if r['record_type'] == 'task'][0]
        task['inputs'][0]['path'] = canary.replace('\\', '/')
        task['context_refs'] = [{'path': canary.replace('\\', '/'), 'digest': 'sha256:' + '0' * 64}]
        task['intent']['refs'][0]['locator'] = 'file:///' + canary.replace('\\', '/')
        data = dumps(bundle)
        opened = []
        real_open = io.open

        def recording_open(file, *a, **k):
            opened.append(os.path.abspath(str(file)) if not isinstance(file, int) else file)
            return real_open(file, *a, **k)

        with mock.patch('builtins.open', recording_open), mock.patch('io.open', recording_open), \
                mock.patch('socket.socket.connect', side_effect=AssertionError('network used')):
            res = self.check(data)
        self.assertEqual(res['reasons'], [NOT_IMPL])
        self.assertNotIn(os.path.abspath(canary), opened)
        self.assertFalse([p for p in opened if not isinstance(p, int) and p.startswith(self.scratch)], opened)
        owners_read = sorted(p for p in opened if not isinstance(p, int) and p.startswith(CVF))
        self.assertEqual(owners_read, sorted([os.path.join(V2C, 'control.schema.json'), os.path.join(V2R, 'ROUTING_POLICY.json')]))
        # ngoài hai owner chỉ còn việc dò phiên bản jsonschema của interpreter / apart from the owners only the interpreter's jsonschema version probe
        others = [p for p in opened if not isinstance(p, int) and not p.startswith(CVF)]
        self.assertTrue(all('site-packages' in p or p.endswith('.zip') for p in others), others)


class CliV2(Base):
    def test_json_and_text_agree(self):
        path = self.write_scratch('ex02.json', self.example_bytes('ex02_mutation_reviewed_bound.json'))
        for phase in PHASES:
            with self.subTest(phase):
                code_j, out_j, err_j = self.run_cli(['--contract', 'v2', '--phase', phase, path])
                code_t, out_t, err_t = self.run_cli(['--contract', 'v2', '--phase', phase, '--format', 'text', path])
                res = json.loads(out_j.decode('utf-8'))
                self.assert_foundation_shape(res)
                self.assertEqual((res['selection'], res['phase'], res['disposition'], res['reasons']),
                                 ('CLI_EXPLICIT', phase, 'BLOCKED', [NOT_IMPL]))
                self.assertEqual((code_j, code_t, err_j, err_t), (1, 1, b'', b''))
                text = out_t.decode('utf-8')
                self.assertTrue(text.startswith('law.cvf.check/2 '))
                for needle in ('contract=v2', 'selection=CLI_EXPLICIT', 'stage=S1_FOUNDATION_ONLY', 'phase=' + phase,
                               'disposition=BLOCKED', 'effect_authorized=false', 'assurance=UNVERIFIED', NOT_IMPL,
                               'binding_evaluated=false', 'routing_evaluated=false', 'gates_evaluated=false',
                               'artifact_bytes_observed=false', 'actual_operation_observed=false',
                               'requirements_semantic_verified=false', 'owner_protection=NOT_PROVEN',
                               res['owners']['schema_sha256'], res['owners']['policy_sha256']):
                    self.assertIn(needle, text)

    def test_exit_codes(self):
        valid = self.write_scratch('valid.json', self.example_bytes('ex02_mutation_reviewed_bound.json'))
        v1b = self.example('ex02_mutation_reviewed_bound.json')
        v1b['schema_version'] = 'law.cvf.control/1'
        cases = [
            (valid, 1, 'BLOCKED'),
            (self.write_scratch('bad.json', b'{'), 1, 'DENY'),
            (self.write_scratch('v1.json', dumps(v1b)), 1, 'UNSUPPORTED'),
            (os.path.join(self.scratch, 'does-not-exist.json'), 2, 'UNSUPPORTED'),
            (self.scratch, 2, 'UNSUPPORTED'),
        ]
        for path, want_code, want_disp in cases:
            with self.subTest(os.path.basename(path)):
                code, out, err = self.run_cli(['--contract', 'v2', '--phase', 'effect', path])
                res = json.loads(out.decode('utf-8'))
                self.assertEqual((code, res['disposition']), (want_code, want_disp))
                self.assertEqual(res['init_error'], want_code == 2)
                if want_code == 2:
                    self.assertEqual(res['reasons'], ['BUNDLE_UNREADABLE'])

    def test_oversized_file_is_denied_not_init_error(self):
        path = self.write_scratch('big.json', b' ' * (8 * 1024 * 1024 + 1))
        code, out, _ = self.run_cli(['--contract', 'v2', '--phase', 'effect', path])
        res = json.loads(out.decode('utf-8'))
        self.assertEqual((code, res['disposition'], res['reasons']), (1, 'DENY', ['INPUT_MALFORMED']))

    def test_option_errors_are_argparse_exit_2(self):
        path = self.write_scratch('ok.json', self.example_bytes('ex02_mutation_reviewed_bound.json'))
        for argv in (['--contract', 'v2', path], ['--contract', 'v2', '--phase', 'bogus', path],
                     ['--contract', 'v2', '--phase', 'effect', '--format', 'xml', path],
                     ['--contract', 'v2', '--phase', 'effect'], ['--contract', 'v2', '--phase', 'effect', path, path],
                     ['--contract', 'v2', '--phase', 'effect', '--root', self.scratch, path],
                     ['--contract', 'v2', '--phase', 'effect', '--basis', 'COOPERATIVE_WORKFLOW', path],
                     ['--contract', 'v2', '--phase', 'effect', '--schema', 'x', path],
                     ['--contract', 'v2', '--phase', 'effect', '--policy', 'x', path],
                     ['--contract', 'v2', '--phase', 'effect', '--trust', 'x', path],
                     ['--contract', 'v2', '--phas', 'effect', path]):
            with self.subTest(argv=argv[2:]):
                code, out, err = self.run_cli(argv)
                self.assertEqual((code, out), (2, b''))
                self.assertIn(b'usage: control_check_v2.py', err)

    def test_python_dash_I_from_outside_the_repo_does_not_depend_on_cwd_or_path(self):
        path = self.write_scratch('smoke.json', self.example_bytes('ex02_mutation_reviewed_bound.json'))
        env = dict(os.environ)
        env['PYTHONPATH'] = self.scratch
        planted = os.path.join(self.scratch, 'json.py')
        with open(planted, 'w') as f:
            f.write('raise RuntimeError("planted module imported")\n')
        proc = subprocess.run([sys.executable, '-I', ENTRY, '--contract', 'v2', '--phase', 'dispatch', path],
                              cwd=self.scratch, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(planted)
        self.assertEqual((proc.returncode, proc.stderr), (1, b''))
        self.assertEqual(json.loads(proc.stdout.decode('utf-8'))['reasons'], [NOT_IMPL])


class ContractRouter(Base):
    V1_FILES = ('ex01_draft_in_grant.json', 'ex02_mutation_reviewed_bound.json', 'ex04_unknown_schema_version.json')

    def assert_parity(self, rest, contract_args=('--contract', 'v1'), position='start'):
        direct = self.run_cli(rest, entry=False)
        if position == 'start':
            argv = list(contract_args) + list(rest)
        elif position == 'end':
            argv = list(rest) + list(contract_args)
        else:
            argv = list(rest[:1]) + list(contract_args) + list(rest[1:])
        routed = self.run_cli(argv)
        self.assertEqual(routed, direct, 'argv=%r' % (rest,))
        return direct

    def v1_paths(self):
        return [os.path.join(V1_EXAMPLES, n) for n in self.V1_FILES]

    def test_parity_stdout_stderr_exit_json_and_text(self):
        for path in self.v1_paths():
            for phase in PHASES:
                for fmt in ('json', 'text'):
                    with self.subTest(file=os.path.basename(path), phase=phase, fmt=fmt):
                        direct = self.assert_parity(['--phase', phase, '--format', fmt, path])
                        self.assertIn(b'law.cvf.check/1', direct[1])
                        self.assertNotIn(b'law.cvf.check/2', direct[1])

    def test_flag_position_and_equals_form(self):
        path = self.v1_paths()[0]
        rest = ['--phase', 'dispatch', path]
        for position in ('start', 'middle', 'end'):
            with self.subTest(position):
                self.assert_parity(rest, position=position)
        self.assert_parity(rest, contract_args=('--contract=v1',))

    def test_forwarded_errors_and_help(self):
        missing = os.path.join(self.scratch, 'missing.json')
        notjson = self.write_scratch('notjson.json', b'{')
        cases = [['--phase', 'dispatch', missing], ['--phase', 'dispatch', notjson], [], ['--phase', 'dispatch'],
                 ['--phase', 'bogus', notjson], ['--phase', 'dispatch', '--format', 'xml', notjson],
                 ['--phase', 'dispatch', notjson, notjson], ['-h'], ['--help'], ['--phase', 'dispatch', '--bogus', notjson],
                 ['--root', self.scratch, '--phase', 'dispatch', notjson]]
        for rest in cases:
            with self.subTest(rest=rest):
                direct = self.assert_parity(rest)
                if direct[0] == 2 and direct[2].startswith(b'usage:'):
                    self.assertTrue(direct[2].startswith(b'usage: control_check.py '), direct[2])

    def test_v1_prog_name_in_forwarded_usage(self):
        code, out, err = self.run_cli(['--contract', 'v1'])
        self.assertEqual(code, 2)
        self.assertTrue(err.startswith(b'usage: control_check.py '), err)
        self.assertEqual(out, b'')

    def test_v1_blocked_is_not_retried_as_v2(self):
        path = self.v1_paths()[0]
        code, out, err = self.run_cli(['--contract', 'v1', '--phase', 'effect', path])
        res = json.loads(out.decode('utf-8'))
        self.assertEqual(res['check_version'], 'law.cvf.check/1')
        self.assertEqual(code, 1)
        self.assertNotIn('evaluation_basis', res)
        self.assertNotIn('implementation_stage', res)

    def test_v1_records_are_not_given_a_basis(self):
        path = self.v1_paths()[1]
        self.assertNotIn(b'evaluation_basis', read_bytes(path))
        self.assert_parity(['--phase', 'dispatch', path])

    def test_v2_bundle_through_v1_is_refused_by_v1_itself(self):
        path = self.write_scratch('v2-through-v1.json', self.example_bytes('ex02_mutation_reviewed_bound.json'))
        direct = self.run_cli(['--phase', 'dispatch', path], entry=False)
        routed = self.run_cli(['--contract', 'v1', '--phase', 'dispatch', path])
        self.assertEqual(routed, direct)
        self.assertEqual(json.loads(direct[1].decode('utf-8'))['reasons'], ['SCHEMA_VERSION_UNKNOWN'])

    def test_contract_flag_errors_are_wrapper_errors(self):
        path = self.v1_paths()[0]
        base = ['--phase', 'dispatch', path]
        cases = [base, ['--contract'] + base, ['--contract', 'v3'] + base, ['--contract', 'V1'] + base, ['--contract', ''] + base,
                 ['--contract=', ] + base, ['--contract', 'v1', '--contract', 'v1'] + base,
                 ['--contract', 'v1', '--contract', 'v2'] + base, ['--cont', 'v1'] + base, ['--contract', 'v2', '--contract', 'v1'] + base,
                 []]
        for argv in cases:
            with self.subTest(argv=argv):
                code, out, err = self.run_cli(argv)
                self.assertEqual((code, out), (2, b''), err)
                self.assertIn(b'control_check_v2.py', err)
                self.assertIn(b'--contract', err)

    def test_arguments_after_double_dash_are_not_scanned(self):
        # một file tên '--contract' là tham số vị trí hợp lệ sau '--' / a positional file named --contract after '--'
        code, out, err = self.run_cli(['--contract', 'v1', '--phase', 'dispatch', '--', '--contract'])
        direct = self.run_cli(['--phase', 'dispatch', '--', '--contract'], entry=False)
        self.assertEqual((code, out, err), direct)

    def _isolated_modules(self, argv):
        script = (
            'import importlib.util, io, json, sys, contextlib\n'
            'spec = importlib.util.spec_from_file_location("law_entry_iso", %r)\n'
            'mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n'
            'before = list(sys.argv)\n'
            'with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):\n'
            '    try:\n'
            '        rc = mod.main(%r)\n'
            '    except SystemExit as exc:\n'
            '        rc = exc.code\n'
            'print(json.dumps({"rc": rc, "argv_restored": sys.argv == before,\n'
            '                  "mods": sorted(m for m in sys.modules if m.startswith("law_cvf_check_"))}))\n'
        ) % (ENTRY, argv)
        proc = subprocess.run([sys.executable, '-I', '-c', script], cwd=self.scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout.decode('utf-8'))

    def test_v1_branch_imports_no_v2_and_restores_argv(self):
        path = self.v1_paths()[0]
        for argv in (['--contract', 'v1', '--phase', 'dispatch', path], ['--contract', 'v1', '--phase', 'bogus', path]):
            with self.subTest(argv=argv[2:]):
                out = self._isolated_modules(argv)
                self.assertTrue(out['argv_restored'])
                self.assertEqual([m for m in out['mods'] if m.startswith('law_cvf_check_v2')], [])
                self.assertIn('law_cvf_check_v1', out['mods'])

    def test_v2_branch_imports_no_v1(self):
        path = self.write_scratch('iso.json', self.example_bytes('ex02_mutation_reviewed_bound.json'))
        out = self._isolated_modules(['--contract', 'v2', '--phase', 'dispatch', path])
        self.assertEqual(out['rc'], 1)
        self.assertNotIn('law_cvf_check_v1', out['mods'])
        self.assertTrue(any(m.startswith('law_cvf_check_v2') for m in out['mods']))

    def test_wrapper_error_imports_neither(self):
        out = self._isolated_modules(['--phase', 'dispatch', 'x.json'])
        self.assertEqual(out['rc'], 2)
        self.assertEqual(out['mods'], [])


class Canon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        entry = load_module_from(ENTRY, 'law_cvf_entry_for_canon')
        entry._load_package()
        cls.canon = importlib.import_module('law_cvf_check_v2.canon')
        cls.ref = load_module_from(REF_TEST, 'law_ref_candidate_under_test')
        cls.vectors = read_json(os.path.join(V2C, 'vectors.json'))
        cls.policy = read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))

    def test_canonical_vectors(self):
        c = self.canon
        self.assertEqual(len(self.vectors['canonical']), 20)
        for v in self.vectors['canonical']:
            with self.subTest(v['id']):
                exp = v['expected']
                if exp['status'] == 'UNSUPPORTED':
                    with self.assertRaises(c.Unsupported) as cm:
                        c.canonical_bytes(c.parse_strict(v['input_json']))
                    self.assertEqual(cm.exception.reason, exp['reason'])
                else:
                    value = c.parse_strict(v['input_json'])
                    self.assertEqual(c.canonical_text(value), exp['canonical_utf8'])
                    self.assertEqual(c.digest_of(value), exp['digest'])

    def test_terminal_newline_key_is_rejected_by_fullmatch(self):
        with self.assertRaises(self.canon.Unsupported) as cm:
            self.canon.canonical_bytes({'key\n': 1})
        self.assertEqual(cm.exception.reason, 'KEY_NOT_ALLOWED')
        self.assertIn('fullmatch', read_bytes(os.path.join(PKG, 'canon.py')).decode('utf-8'))

    def test_object_bytes_vectors(self):
        self.assertEqual(len(self.vectors['object_bytes']), 4)
        for v in self.vectors['object_bytes']:
            with self.subTest(v['id']):
                self.assertEqual(self.canon.bytes_digest(bytes.fromhex(v['bytes_hex'])), v['digest'])

    def test_projection_fixture_and_policy_digest(self):
        c = self.canon
        fx = self.vectors['projection_fixture']
        task = copy.deepcopy(fx['task'])
        got = {'intent': c.digest_of(c.intent_part(task)), 'context': c.digest_of(c.context_part(task)),
               'task': c.digest_of(c.task_part(task)), 'action': c.digest_of(c.action_part(task['effects']['actions'][0]))}
        for k, want in fx['expected'].items():
            self.assertEqual(got[k], want, k)
        self.assertEqual(c.canonical_text(c.intent_part(task)), fx['canonical_intent'])
        self.assertEqual(c.canonical_text(c.context_part(task)), fx['canonical_context'])
        self.assertEqual(c.canonical_text(c.action_part(task['effects']['actions'][0])), fx['canonical_action'])
        self.assertEqual(self.vectors['policy_digest']['digest'], c.digest_of(c.policy_part(self.policy)))
        self.assertEqual(self.vectors['bind_version'], c.BIND_VERSION)

    def test_parity_with_reference_on_every_vector_input(self):
        for v in self.vectors['canonical']:
            with self.subTest(v['id']):
                try:
                    want = ('OK', self.ref.canonical_text(self.ref.parse_strict(v['input_json'])))
                except self.ref.Unsupported as exc:
                    want = ('UNSUPPORTED', exc.reason)
                try:
                    got = ('OK', self.canon.canonical_text(self.canon.parse_strict(v['input_json'])))
                except self.canon.Unsupported as exc:
                    got = ('UNSUPPORTED', exc.reason)
                self.assertEqual(got, want)

    def test_parity_with_reference_on_every_valid_example(self):
        expected = read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))
        seen = 0
        for case in expected['cases']:
            if not case['schema_valid']:
                continue
            bundle = read_json(os.path.join(V2C, 'examples', case['file']))
            for task in (r for r in bundle['records'] if r['record_type'] == 'task'):
                with self.subTest(case['file']):
                    self.assertEqual(self.canon.binding_digests(copy.deepcopy(task), self.policy),
                                     self.ref.binding_digests(copy.deepcopy(task), self.policy))
                    for a in task['effects']['actions']:
                        self.assertEqual(self.canon.digest_of(self.canon.action_part(copy.deepcopy(a))),
                                         self.ref.digest_of(self.ref.action_part(copy.deepcopy(a))))
                    seen += 1
        self.assertGreaterEqual(seen, 10)

    def test_product_digests_match_declared_bindings_of_non_stale_examples(self):
        expected = read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))
        for case in expected['cases']:
            if not case['schema_valid'] or case['binding_stale_or_mismatched']:
                continue
            bundle = read_json(os.path.join(V2C, 'examples', case['file']))
            tasks = [r for r in bundle['records'] if r['record_type'] == 'task']
            if not tasks:
                continue
            want = self.canon.binding_digests(tasks[0], self.policy)
            for r in bundle['records']:
                if r.get('binding'):
                    for k, v in want.items():
                        self.assertEqual(r['binding'][k], v, '%s %s' % (case['file'], k))

    def test_exclusions_inclusions_sets_and_sequences(self):
        c = self.canon
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        base = c.binding_digests(task, self.policy)
        t = copy.deepcopy(task)
        t['route_proposal'] = {'policy_version': 'law.cvf.routing/2', 'proposed_rows': ['R-READ_DRAFT']}
        t['proposed_by'] = {'actor_id': 'someone-else', 'role': 'worker'}
        t['note'] = 'changed'
        t['intent']['refs'][0]['locator'] = 'EXAMPLE://elsewhere'
        t['intent']['refs'][0]['ref_id'] = 'renamed'
        t['intent']['refs'][0]['attribution']['source_class'] = 'UNVERIFIED'
        t['authority']['subject']['host'] = 'other-host'
        self.assertEqual(c.binding_digests(t, self.policy), base)
        edits = {
            'main_interpretation': lambda x: x['intent'].__setitem__('main_interpretation', 'other'),
            'task_revision': lambda x: x.__setitem__('task_revision', 2),
            'input digest': lambda x: x['inputs'][0].__setitem__('digest', 'sha256:' + '0' * 64),
            'input revision': lambda x: x['inputs'][0].__setitem__('revision', '2'),
            'action target': lambda x: x['effects']['actions'][0]['targets'].append('references/other.xlsx'),
            'requirement': lambda x: x['acceptance']['requirements'][0].__setitem__('statement', 'other'),
            'context ref': lambda x: x.__setitem__('context_refs', [{'path': 'references/c.txt', 'digest': 'sha256:' + '3' * 64}]),
        }
        for label, edit in edits.items():
            with self.subTest(label):
                x = copy.deepcopy(task)
                edit(x)
                self.assertNotEqual(c.binding_digests(x, self.policy), base)
        task['effects']['actions'][0]['targets'] = ['b.txt', 'a.txt']
        a = c.digest_of(c.action_part(task['effects']['actions'][0]))
        task['effects']['actions'][0]['targets'] = ['a.txt', 'b.txt']
        self.assertEqual(c.digest_of(c.action_part(task['effects']['actions'][0])), a)
        task['acceptance']['requirements'].append({'req_id': 'REQ-2', 'statement': 'x', 'mandatory': True})
        d1 = c.digest_of(c.task_part(task))
        task['acceptance']['requirements'].reverse()
        self.assertNotEqual(c.digest_of(c.task_part(task)), d1)

    def test_missing_differs_from_null_and_empty_containers_are_kept(self):
        c = self.canon
        self.assertNotEqual(c.digest_of({'a': None}), c.digest_of({}))
        self.assertEqual(c.canonical_text({'z': [], 'y': {}}), '{"y":{},"z":[]}')

    def test_duplicate_set_element_is_unsupported(self):
        with self.assertRaises(self.canon.Unsupported) as cm:
            self.canon.sorted_set(['a', 'a'])
        self.assertEqual(cm.exception.reason, 'DUPLICATE_SET_ELEMENT')

    def test_domain_violations(self):
        c = self.canon
        self.assertEqual(c.domain_violations({'a': [1, 'x', None, True, {'b': 2 ** 53 - 1}]}), [])
        cases = {
            'NON_INTEGER_NUMBER': {'a': 1.0},
            'INTEGER_OUT_OF_RANGE': {'a': 2 ** 53},
            'NON_NFC_STRING': {'a': 'é'},
            'LONE_SURROGATE': {'a': '\ud800'},
            'KEY_NOT_ALLOWED': {'key\n': 1},
        }
        for reason, value in cases.items():
            with self.subTest(reason):
                found = c.domain_violations(value)
                self.assertEqual([r for _, r in found], [reason])
        self.assertEqual([r for _, r in c.domain_violations({'a': [True, 1.5]})], ['NON_INTEGER_NUMBER'])
        for _path, _reason in c.domain_violations({'secret-key é': 1}):
            self.assertNotIn('secret', _path)


if __name__ == '__main__':
    unittest.main()
