"""G-02-C2/S2: kiểm helper refs/binding trong bộ nhớ và refactor hẹp của loader / checks for the in-memory refs/binding helpers.

Chỉ kiểm so sánh/tính lại: không có PASS/MET/permit, không route/gate/review verdict, không quan sát byte, không nối vào entry.
Fixture dựng trong bộ nhớ từ bản sao sâu của ví dụ C1, không thêm file fixture. Comparison/recomputation only; fixtures are in-memory copies.
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
import sys
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
V2C = os.path.join(CVF, 'contracts', 'v2')
V2R = os.path.join(CVF, 'rules', 'v2')
REF_TEST = os.path.join(ROOT, 'tests', 'test_control_v2_candidate.py')

# Owner S1/C1/v1 không được đổi trong S2; pin này là hash lúc nhận brief S2 và không được sửa để test xanh.
# S1/C1/v1 owners must not change in S2; these pins are the hashes at dispatch and must not be edited to turn tests green.
OWNER_PINS = {
    ('checks', 'control_check.py'): 'f95bfc367bb7f470',
    ('checks', 'control_check_v2.py'): '5179e7091579c048',
    ('checks', 'v2', '__init__.py'): '83ba965d6a3ac57a',
    ('checks', 'v2', 'canon.py'): 'c593c6d070ccdf67',
    ('contracts', 'v2', 'control.schema.json'): '4c6dd3dae50596b5',
    ('contracts', 'v2', 'vectors.json'): '8d59d60ccd3af136',
    ('contracts', 'v2', 'examples', 'EXPECTED.json'): '3b463f654d51a9ec',
    ('rules', 'v2', 'ROUTING_POLICY.json'): '20cff567afe4fa0f',
}
TEST_PINS = {'test_control_check.py': '454e3f4944825809', 'test_control_v2_candidate.py': 'b32d7b3ff0e8a014'}

NFD = 'é'  # không NFC / not NFC
STATES = {'MATCH', 'MISMATCH', 'ONE_SIDED', 'INCOMPLETE', 'AMBIGUOUS', 'UNSUPPORTED', 'NOT_BOUND', 'NOT_APPLICABLE'}
TASK_KEY = ('EXAMPLE-task-1', 1)


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def sha_prefix(path):
    return hashlib.sha256(read_bytes(path)).hexdigest()[:16]


def load_module_from(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def setUpModule():
    if not HAVE_JSONSCHEMA:
        raise RuntimeError('jsonschema>=4.18 không có / not installed: BLOCKED, không tự cài / not auto-installed')


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = load_module_from(ENTRY, 'law_cvf_entry_s2')
        cls.entry._load_package()
        cls.loader = importlib.import_module('law_cvf_check_v2.loader')
        cls.canon = importlib.import_module('law_cvf_check_v2.canon')
        cls.refs = importlib.import_module('law_cvf_check_v2.refs')
        cls.binding = importlib.import_module('law_cvf_check_v2.binding')
        cls.policy_bytes = read_bytes(os.path.join(V2R, 'ROUTING_POLICY.json'))
        cls.policy = cls.binding.make_policy_context(cls.policy_bytes)
        cls.vectors = read_json(os.path.join(V2C, 'vectors.json'))

    # ---- fixtures
    def ex(self, name):
        return copy.deepcopy(read_json(os.path.join(V2C, 'examples', name + '.json')))

    def ex02(self):
        return self.refs.records_of(self.ex('ex02_mutation_reviewed_bound'))

    def ex09(self):
        return self.refs.records_of(self.ex('ex09_child_exceeds_scope'))

    @staticmethod
    def of(records, rtype, n=0):
        return [r for r in records if r['record_type'] == rtype][n]

    @staticmethod
    def pos(records, rtype, n=0):
        return [i for i, r in enumerate(records) if r['record_type'] == rtype][n]

    def index(self, records):
        return self.refs.build_index(records)

    def report(self, records, position, policy=None):
        return self.binding.compare_binding(self.index(records), position, policy or self.policy)

    @staticmethod
    def states(report):
        out = {}
        for rel in report.relations:
            out.setdefault(rel.name, []).append(rel.state)
        return {k: (v[0] if len(v) == 1 else tuple(v)) for k, v in out.items()}

    def rel(self, relations, name):
        found = [r for r in relations if r.name == name]
        self.assertEqual(len(found), 1, '%s -> %d relations' % (name, len(found)))
        return found[0]

    def all_results_dicts(self, records, policy=None):
        """Chạy mọi hàm công khai trên mọi record và gom as_dict() / run every public helper on every record and collect as_dict()."""
        policy = policy or self.policy
        index = self.index(records)
        claims = self.refs.collect_claims(index)
        out = [policy.as_dict(), claims.as_dict(), index.as_dict()]
        for p, r in enumerate(records):
            out.extend(link.as_dict() for link in self.refs.link_grants(index, claims, p))
            out.append(self.binding.compare_binding(index, p, policy).as_dict())
            out.extend(rel.as_dict() for rel in self.binding.compare_pointers(index, p, policy))
            if r['record_type'] == 'task':
                out.append(self.binding.recompute_task(r).as_dict())
        return out


# ====================================================================== loader refactor
class OwnersUntouched(unittest.TestCase):
    def test_s1_c1_v1_owner_pins(self):
        for rel, want in OWNER_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(CVF, *rel)), want, '/'.join(rel))

    def test_v1_and_c1_tests_unchanged(self):
        for name, want in TEST_PINS.items():
            self.assertEqual(sha_prefix(os.path.join(ROOT, 'tests', name)), want, name)

    def test_package_tree_has_exactly_the_s2_modules(self):
        names = sorted(n for n in os.listdir(PKG) if n.endswith(('.py', '.md')))
        self.assertEqual(names, ['README.md', '__init__.py', 'binding.py', 'canon.py', 'loader.py', 'refs.py'])

    def test_helpers_do_io_free_and_import_only_package_modules(self):
        for name in ('refs.py', 'binding.py'):
            src = read_bytes(os.path.join(PKG, name)).decode('utf-8')
            for needle in ('open(', 'socket', 'subprocess', 'urllib', 'import os', 'os.path', 'pathlib', 'sys.path', 'import tests',
                           'from tests', 'importlib', 'requests', 'time.', 'datetime', 'random', '--root'):
                self.assertFalse(needle in src, '%s contains %r' % (name, needle))


class LoaderHelpers(Base):
    def bytes_of(self, name):
        return read_bytes(os.path.join(V2C, 'examples', name + '.json'))

    def test_owners_carry_immutable_policy_bytes_snapshot(self):
        owners = self.loader.load_owners()
        self.assertIsInstance(owners.policy_bytes, bytes)
        self.assertEqual(owners.policy_bytes, self.policy_bytes)
        self.assertEqual(hashlib.sha256(owners.policy_bytes).hexdigest(), owners.policy_sha256)

    def test_parse_and_preflight_success_shape(self):
        owners = self.loader.load_owners()
        bundle, out = self.loader.parse_and_preflight(self.bytes_of('ex02_mutation_reviewed_bound'), owners)
        self.assertIsInstance(bundle, dict)
        self.assertEqual(out.evaluation_basis, 'COOPERATIVE_WORKFLOW')
        self.assertIs(out.record_structure_checked, False)
        self.assertEqual((set(out.reasons), out.details), (set(), []))

    def test_parse_and_preflight_refusals_match_inspect_bundle(self):
        owners = self.loader.load_owners()
        cases = {
            'ex15_v1_record_in_v2_bundle': 'UNSUPPORTED', 'ex16_unknown_schema_version': 'UNSUPPORTED',
            'ex17_basis_missing': 'UNSUPPORTED', 'ex18_basis_unknown': 'UNSUPPORTED', 'ex23_v1_binding_reused': 'UNSUPPORTED',
        }
        for name, disp in cases.items():
            with self.subTest(name):
                data = self.bytes_of(name)
                bundle, out = self.loader.parse_and_preflight(data, owners)
                full = self.loader.inspect_bundle(data, owners)
                self.assertIsNone(bundle)
                self.assertEqual((out.disposition, out.reasons, out.details), (disp, full.reasons, full.details))
        bundle, out = self.loader.parse_and_preflight(b'{"a": 1, "a": 2}', owners)
        self.assertIsNone(bundle)
        self.assertEqual((out.disposition, out.reasons), ('DENY', {'INPUT_MALFORMED'}))

    def test_validate_structure_shapes(self):
        owners = self.loader.load_owners()
        ok, reasons, details = self.loader.validate_structure(self.ex('ex02_mutation_reviewed_bound'), owners)
        self.assertEqual((ok, reasons, details), (True, (), tuple(owners.notes)))
        ok, reasons, details = self.loader.validate_structure(self.ex('ex04_main_authored_user_confirmation'), owners)
        self.assertIs(ok, False)
        self.assertEqual(reasons, ('SCHEMA_INVALID',))
        self.assertIsInstance(details, tuple)
        self.assertEqual(details[:len(owners.notes)], tuple(owners.notes))
        self.assertGreater(len(details), len(owners.notes))
        policy_record = json.loads(self.policy_bytes.decode('utf-8'))
        ok, reasons, details = self.loader.validate_structure(policy_record, owners)
        self.assertEqual((ok, reasons), (False, ('SCHEMA_INVALID',)))
        self.assertTrue(any('routing_policy' in d for d in details))

    def test_inspect_bundle_delegates_to_the_two_helpers_in_order(self):
        owners = self.loader.load_owners()
        calls = []
        real_parse, real_validate = self.loader.parse_and_preflight, self.loader.validate_structure

        def spy_parse(*a, **k):
            calls.append('parse')
            return real_parse(*a, **k)

        def spy_validate(*a, **k):
            calls.append('validate')
            return real_validate(*a, **k)

        with mock.patch.object(self.loader, 'parse_and_preflight', spy_parse), \
                mock.patch.object(self.loader, 'validate_structure', spy_validate):
            res = self.loader.inspect_bundle(self.bytes_of('ex02_mutation_reviewed_bound'), owners)
            self.assertEqual((res.disposition, calls), ('BLOCKED', ['parse', 'validate']))
            del calls[:]
            res = self.loader.inspect_bundle(self.bytes_of('ex15_v1_record_in_v2_bundle'), owners)
            self.assertEqual((res.disposition, calls), ('UNSUPPORTED', ['parse']))
            del calls[:]
            res = self.loader.inspect_bundle(self.bytes_of('ex04_main_authored_user_confirmation'), owners)
            self.assertEqual((res.disposition, calls), ('DENY', ['parse', 'validate']))

    def test_s1_whole_bundle_screen_still_rejects_what_the_s2_pipeline_accepts(self):
        owners = self.loader.load_owners()
        bundle = self.ex('ex02_mutation_reviewed_bound')
        self.binding_task(bundle)['note'] = 'outside the projection ' + NFD
        data = json.dumps(bundle).encode('utf-8')
        parsed, out = self.loader.parse_and_preflight(data, owners)
        ok, _, _ = self.loader.validate_structure(parsed, owners)
        self.assertTrue(parsed is not None and ok)
        full = self.loader.inspect_bundle(data, owners)
        self.assertEqual((full.disposition, full.reasons), ('UNSUPPORTED', {'UNSUPPORTED_BINDING_PART'}))
        self.assertIs(full.record_structure_checked, False)
        res = self.entry.check_bytes(data, 'effect', 'v2')
        self.assertEqual((res['disposition'], res['reasons']), ('UNSUPPORTED', ['UNSUPPORTED_BINDING_PART']))

    @staticmethod
    def binding_task(bundle):
        return [r for r in bundle['records'] if r['record_type'] == 'task'][0]

    def test_policy_context_comes_from_bytes_not_from_the_cached_mutable_dict(self):
        owners = self.loader.load_owners()
        want = self.vectors['policy_digest']['digest']
        saved = copy.deepcopy(owners.policy)
        try:
            owners.policy['rows'][0]['row_id'] = 'R-TAMPERED'
            tampered = self.canon.digest_of(self.canon.policy_part(owners.policy))
            ctx = self.binding.make_policy_context(owners.policy_bytes)
        finally:
            owners.policy.clear()
            owners.policy.update(saved)
        self.assertNotEqual(tampered, want, 'the in-place mutation must change the dict digest or this test proves nothing')
        self.assertEqual((ctx.state, ctx.digest, ctx.literals_ok), ('COMPUTED', want, True))

    def test_s1_entry_and_cli_behavior_unchanged_on_the_valid_examples(self):
        expected = read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))
        valid = [c['file'] for c in expected['cases'] if c['schema_valid']]
        self.assertEqual(len(valid), 13)
        for name in valid:
            res = self.entry.check_bytes(read_bytes(os.path.join(V2C, 'examples', name)), 'effect', 'v2')
            self.assertEqual((res['disposition'], res['reasons']), ('BLOCKED', ['CANDIDATE_EVALUATION_NOT_IMPLEMENTED']), name)
            self.assertIs(res['coverage']['binding_evaluated'], False, name)
            self.assertIs(res['coverage']['record_structure_checked'], True, name)


# ====================================================================== policy context
class PolicyContext(Base):
    def test_policy_context_matches_vector_and_flags(self):
        self.assertEqual((self.policy.state, self.policy.digest, self.policy.literals_ok, self.policy.reason),
                         ('COMPUTED', self.vectors['policy_digest']['digest'], True, None))
        d = self.policy.as_dict()
        self.assertEqual(sorted(d), ['digest', 'literals_ok', 'reason', 'state'])

    def test_malformed_and_wrong_literal_policy_bytes(self):
        bad = {
            'not json': b'{',
            'duplicate key': b'{"a": 1, "a": 2}',
            'not an object': b'[]',
            'float in policy': json.dumps(dict(json.loads(self.policy_bytes), extra=1.5)).encode('utf-8'),
        }
        for label, data in bad.items():
            with self.subTest(label):
                ctx = self.binding.make_policy_context(data)
                self.assertEqual(ctx.state, 'UNSUPPORTED')
                self.assertIsNone(ctx.digest)
                self.assertIsNotNone(ctx.reason)
        wrong = json.loads(self.policy_bytes)
        wrong['policy_version'] = 'law.cvf.routing/1'
        ctx = self.binding.make_policy_context(json.dumps(wrong).encode('utf-8'))
        self.assertEqual((ctx.state, ctx.literals_ok, ctx.reason), ('UNSUPPORTED', False, 'POLICY_LITERAL_MISMATCH'))

    def test_argument_types(self):
        for bad in ('{}', bytearray(b'{}'), None, 5, {}):
            with self.assertRaises(TypeError):
                self.binding.make_policy_context(bad)


# ====================================================================== index
class IndexTests(Base):
    def test_locator_vocabulary_is_closed(self):
        self.assertEqual(self.refs.loc(3, 'intent', 'refs', 0), 'records[3].intent.refs[0]')
        self.assertEqual(self.refs.loc(None, 'binding', 'inputs'), '.binding.inputs')
        for part in ('CANARY-KEY', 'x y', '', True, None, 1.5):
            self.assertEqual(self.refs.loc(0, 'binding', part), 'records[0].binding.?')

    def test_typed_lookup_and_namespaces(self):
        recs = self.ex02()
        index = self.index(recs)
        self.assertEqual(index.count, 6)
        look = index.lookup('task', *TASK_KEY)
        self.assertEqual((look.status, look.positions, look.record_type), ('FOUND', (0,), 'task'))
        for key in (('EXAMPLE-task-1', 2), ('EXAMPLE-task-1', '1'), ('EXAMPLE-task-1', True), ('EXAMPLE-task-1', 1.0), ('nope', 1)):
            with self.subTest(key=key):
                self.assertEqual(index.lookup('task', *key).status, 'MISSING')
        self.assertEqual(index.lookup('grant', 'EXAMPLE-grant-1', 1).positions, (1,))
        self.assertEqual(index.lookup('grant', 'EXAMPLE-grant-1').positions, (1,))
        self.assertEqual(index.lookup('review', 'EXAMPLE-review-pre').positions, (2,))
        self.assertEqual(index.lookup('effect', 'EXAMPLE-effect-1').positions, (5,))
        self.assertEqual(index.lookup('result', 'EXAMPLE-result-1').positions, (4,))
        self.assertEqual(index.collisions(), ())
        self.assertEqual(index.malformed_positions, ())

    def test_same_string_in_two_namespaces_is_not_a_collision(self):
        recs = self.ex02()
        self.of(recs, 'grant')['grant_id'] = 'EXAMPLE-review-pre'
        index = self.index(recs)
        self.assertEqual(index.lookup('grant', 'EXAMPLE-review-pre').status, 'FOUND')
        self.assertEqual(index.lookup('review', 'EXAMPLE-review-pre').status, 'FOUND')
        self.assertEqual(index.collisions(), ())

    def test_duplicate_standalone_key_is_ambiguous_even_with_different_work_id(self):
        recs = self.ex02()
        dup = copy.deepcopy(recs[0])
        dup['work_id'] = 'EXAMPLE-work-OTHER'
        recs.append(dup)
        index = self.index(recs)
        look = index.lookup('task', *TASK_KEY)
        self.assertEqual((look.status, look.positions), ('AMBIGUOUS', (0, 6)))
        self.assertEqual([(c.record_type, c.status, c.positions) for c in index.collisions()], [('task', 'AMBIGUOUS', (0, 6))])
        for rtype, rid, n in (('review', 'EXAMPLE-review-pre', 2), ('effect', 'EXAMPLE-effect-1', 5), ('result', 'EXAMPLE-result-1', 4)):
            with self.subTest(rtype):
                extra = copy.deepcopy(recs[n])
                r2 = recs + [extra]
                self.assertEqual(self.index(r2).lookup(rtype, rid).status, 'AMBIGUOUS')

    def test_two_revisions_are_distinct_keys_and_never_latest(self):
        recs = self.ex02()
        t2 = copy.deepcopy(recs[0])
        t2['task_revision'] = 2
        g2 = copy.deepcopy(recs[1])
        g2['grant_revision'] = 2
        index = self.index(recs + [t2, g2])
        self.assertEqual(index.lookup('task', 'EXAMPLE-task-1', 1).positions, (0,))
        self.assertEqual(index.lookup('task', 'EXAMPLE-task-1', 2).positions, (6,))
        self.assertEqual(index.lookup('grant', 'EXAMPLE-grant-1', 1).positions, (1,))
        by_id = index.lookup('grant', 'EXAMPLE-grant-1')
        self.assertEqual((by_id.status, by_id.positions), ('AMBIGUOUS', (1, 7)))
        self.assertEqual(index.collisions(), ())

    def test_malformed_records_are_reported_not_raised(self):
        recs = self.ex02()
        del recs[0]['task_id']
        recs.append({'record_type': 5})
        recs.append({})
        recs.append({'record_type': 'task', 'task_id': 7, 'task_revision': 1})
        recs.append({'record_type': 'task', 'task_id': 'T', 'task_revision': True})
        index = self.index(recs)
        self.assertEqual(index.malformed_positions, (0, 6, 7, 8, 9))
        self.assertEqual(index.lookup('task', *TASK_KEY).status, 'MISSING')

    def test_programmer_errors(self):
        for bad in ('x', {}, None, 5):
            with self.assertRaises(TypeError):
                self.refs.build_index(bad)
        with self.assertRaises(TypeError):
            self.refs.build_index([1])
        index = self.index(self.ex02())
        with self.assertRaises(ValueError):
            index.lookup('source', 'x')
        with self.assertRaises(ValueError):
            index.lookup('task', 'only-id')
        with self.assertRaises(ValueError):
            index.lookup('review', 'a', 'b')
        deep = {'record_type': 'task', 'task_id': 'T', 'task_revision': 1, 'x': None}
        cursor = deep
        for _ in range(200):
            cursor['x'] = {'x': None}
            cursor = cursor['x']
        with self.assertRaises(ValueError):
            self.refs.build_index([deep])

    def test_records_of_and_source_order(self):
        bundle = self.ex('ex02_mutation_reviewed_bound')
        self.assertEqual(self.refs.records_of(bundle), bundle['records'])
        single = bundle['records'][0]
        self.assertEqual(self.refs.records_of(single), [single])
        self.assertEqual(self.index([single]).lookup('task', *TASK_KEY).positions, (0,))
        reverse = list(reversed(bundle['records']))
        self.assertEqual(self.index(reverse).lookup('task', *TASK_KEY).positions, (5,))
        with self.assertRaises(TypeError):
            self.refs.records_of([])

    def test_index_snapshot_is_independent_of_later_input_mutation(self):
        recs = self.ex02()
        index = self.index(recs)
        recs[0]['task_id'] = 'MUTATED'
        recs[1]['issuer_ref']['ref_id'] = 'MUTATED'
        self.assertEqual(index.lookup('task', *TASK_KEY).status, 'FOUND')
        self.assertEqual(index.lookup('task', 'MUTATED', 1).status, 'MISSING')
        claims = self.refs.collect_claims(index)
        self.assertIsNotNone(claims.group('EXAMPLE-grant-ref-1'))
        self.assertIsNone(claims.group('MUTATED'))


# ====================================================================== claims
class ClaimTests(Base):
    GRANT_REF = 'EXAMPLE-grant-ref-1'

    def claims(self, recs):
        return self.refs.collect_claims(self.index(recs))

    def test_ex02_groups_are_inline_claims_only(self):
        t = self.claims(self.ex02())
        self.assertEqual(len(t.groups()), 3)
        g = t.group(self.GRANT_REF)
        self.assertEqual((g.status, g.occurrences, g.kind, g.conflict_fields, g.metadata_differs, g.resolution),
                         ('AGREE', 2, 'grant', (), (), 'INLINE_CLAIM_ONLY'))
        elig = t.group('EXAMPLE-elig-ref-1')
        self.assertEqual((elig.status, elig.occurrences, elig.kind, elig.resolution), ('AGREE', 2, 'reviewer_eligibility', 'INLINE_CLAIM_ONLY'))
        intent = t.group('EXAMPLE-intent-ref-1')
        self.assertEqual((intent.status, intent.occurrences, intent.kind), ('AGREE', 1, 'user_intent'))
        self.assertEqual(t.malformed, ())
        roles = sorted(o.role for p in range(6) for o in t.occurrences_at(p))
        self.assertEqual(roles, ['eligibility_ref', 'eligibility_ref', 'grant_ref', 'intent_ref', 'issuer_ref'])
        # không có record nguồn nào tồn tại cho lời khai inline / no standalone source record exists for an inline claim
        index = self.index(self.ex02())
        with self.assertRaises(ValueError):
            index.lookup('source', 'EXAMPLE-elig-ref-1')
        self.assertEqual(index.lookup('review', 'EXAMPLE-elig-ref-1').status, 'MISSING')

    def test_each_claim_bearing_field_creates_conflict_and_is_outside_the_task_hash(self):
        def set_(path, value):
            def f(ref):
                node = ref
                for p in path[:-1]:
                    node = node[p]
                node[path[-1]] = value
            return f

        def drop(path):
            def f(ref):
                node = ref
                for p in path[:-1]:
                    node = node[p]
                del node[path[-1]]
            return f

        cases = {
            'kind': set_(['kind'], 'user_intent'),
            'locator': set_(['locator'], 'EXAMPLE://elsewhere'),
            'revision': set_(['revision'], '2'),
            'revision-absent': drop(['revision']),
            'revision-null': set_(['revision'], None),
            'digest': set_(['digest'], 'sha256:' + '0' * 64),
            'issuer': set_(['issuer'], {'actor_id': 'EXAMPLE-user', 'role': 'user'}),
            'source_class': set_(['attribution', 'source_class'], 'UNVERIFIED'),
            'channel': set_(['attribution', 'channel'], 'HOST_CONFIRMATION_UI'),
            'evidence_locator': drop(['attribution', 'evidence_locator']),
        }
        field_of = {'revision-absent': 'revision', 'revision-null': 'revision'}
        base = self.binding.recompute_task(self.of(self.ex02(), 'task'))
        for label, mutate in cases.items():
            with self.subTest(label):
                recs = self.ex02()
                mutate(self.of(recs, 'grant')['issuer_ref'])
                group = self.claims(recs).group(self.GRANT_REF)
                self.assertEqual(group.status, 'CONFLICT')
                want = field_of.get(label, label)
                if label == 'source_class':
                    want = 'source_class'
                self.assertIn(want, group.conflict_fields)
                self.assertEqual(self.binding.recompute_task(self.of(recs, 'task')), base)

    def test_actor_claims_compare_every_declared_field(self):
        recs = self.ex02()
        e = self.of(recs, 'review', 1)['reviewer']['eligibility_ref']['attribution']['observed_by']
        e['session_ref'] = 'EXAMPLE-session-2'
        self.assertEqual(self.claims(recs).group('EXAMPLE-elig-ref-1').conflict_fields, ('observed_by',))
        recs = self.ex02()
        self.of(recs, 'grant')['issuer_ref']['issuer'] = {'actor_id': 'U', 'role': 'user', 'host': 'h1'}
        self.of(recs, 'task')['authority']['grant_refs'][0]['issuer'] = {'actor_id': 'U', 'role': 'user', 'host': 'h2'}
        self.assertEqual(self.claims(recs).group(self.GRANT_REF).conflict_fields, ('issuer',))

    def test_recorder_and_note_are_metadata_only(self):
        recs = self.ex02()
        att = self.of(recs, 'grant')['issuer_ref']['attribution']
        att['recorded_by'] = {'actor_id': 'someone-else', 'role': 'main', 'host': 'EXAMPLE-host'}
        att['note'] = 'different note'
        g = self.claims(recs).group(self.GRANT_REF)
        self.assertEqual((g.status, g.conflict_fields, g.metadata_differs), ('AGREE', (), ('note', 'recorded_by')))

    def test_same_ref_id_with_two_kinds_conflicts_and_has_no_kind(self):
        recs = self.ex02()
        clash = copy.deepcopy(self.of(recs, 'task')['authority']['grant_refs'][0])
        clash['kind'] = 'user_intent'
        self.of(recs, 'task')['intent']['refs'].append(clash)
        g = self.claims(recs).group(self.GRANT_REF)
        self.assertEqual((g.status, g.kind, g.occurrences), ('CONFLICT', None, 3))
        self.assertIn('kind', g.conflict_fields)

    def test_strings_compare_verbatim_no_nfc_no_trim(self):
        for value in (NFD, 'EXAMPLE://user-store/grant-1 ', 'EXAMPLE://USER-STORE/grant-1'):
            with self.subTest(value=value):
                recs = self.ex02()
                self.of(recs, 'grant')['issuer_ref']['locator'] = value
                self.assertEqual(self.claims(recs).group(self.GRANT_REF).conflict_fields, ('locator',))
        recs = self.ex02()
        for r in (self.of(recs, 'grant')['issuer_ref'], self.of(recs, 'task')['authority']['grant_refs'][0]):
            r['locator'] = 'x' + NFD
        self.assertEqual(self.claims(recs).group(self.GRANT_REF).status, 'AGREE')

    def test_non_canonical_metadata_does_not_break_claims(self):
        recs = self.ex02()
        att = self.of(recs, 'grant')['issuer_ref']['attribution']
        att['note'] = 'outside the hash ' + NFD
        att['evidence_locator'] = 'EXAMPLE://' + NFD
        g = self.claims(recs).group(self.GRANT_REF)
        self.assertEqual(g.status, 'CONFLICT')
        self.assertEqual(g.conflict_fields, ('evidence_locator',))

    def test_malformed_occurrences_are_listed_not_raised(self):
        recs = self.ex02()
        self.of(recs, 'task')['intent']['refs'].append({'kind': 'user_intent'})
        self.of(recs, 'task')['intent']['refs'].append('not a dict')
        self.of(recs, 'review')['reviewer']['eligibility_ref'] = None
        t = self.claims(recs)
        self.assertEqual(len(t.malformed), 3)
        self.assertTrue(all(isinstance(x, str) and x.startswith('records[') for x in t.malformed))

    def test_wrong_typed_containers_are_reported_as_malformed_locators(self):
        recs = self.ex02()
        self.of(recs, 'task')['intent'] = 'not an object'
        self.of(recs, 'task')['authority'] = ['x']
        t = self.claims(recs)
        self.assertEqual(sorted(t.malformed), ['records[0].authority', 'records[0].intent'])
        self.assertIsNone(t.group('EXAMPLE-intent-ref-1'))

    def test_group_lookup_by_wrong_type(self):
        t = self.claims(self.ex02())
        self.assertIsNone(t.group(5))
        self.assertIsNone(t.group('missing'))

    def test_recipe_and_delegation_refs_are_collected_from_every_action_site(self):
        recs = self.ex09()
        recs[0]['effects']['actions'][0]['delegation']['callee'] = {
            'role_class': 'registered', 'role_name': 'x',
            'identity_ref': copy.deepcopy(recs[0]['intent']['refs'][0])}
        recs[0]['effects']['actions'][0]['delegation']['callee']['identity_ref'].update(ref_id='ID-REF', kind='role_acceptance')
        t = self.claims(recs)
        self.assertEqual(t.group('ID-REF').occurrences, 1)
        self.assertEqual(sorted(o.role for o in t.occurrences_at(0) if o.role == 'identity_ref'), ['identity_ref'])


# ====================================================================== grant links
class GrantLinkTests(Base):
    REF = 'EXAMPLE-grant-ref-1'

    def links(self, recs, position):
        index = self.index(recs)
        return self.refs.link_grants(index, self.refs.collect_claims(index), position)

    def one(self, recs, position):
        links = self.links(recs, position)
        self.assertEqual(len(links), 1)
        return links[0]

    def test_claim_table_must_belong_to_the_current_index(self):
        recs = self.ex02()
        original = self.index(recs)
        old_claims = self.refs.collect_claims(original)
        self.of(recs, 'grant')['issuer_ref']['locator'] = 'EXAMPLE://changed-source'
        current = self.index(recs)
        with self.assertRaises(ValueError):
            self.refs.link_grants(current, old_claims, 0)
        fresh = self.refs.collect_claims(current)
        link = self.refs.link_grants(current, fresh, 0)[0]
        self.assertEqual((link.state, link.claim_status), ('CONFLICT', 'CONFLICT'))
        self.assertIn('locator', link.claim_conflict_fields)

    def test_ex02_task_and_effect_link_although_ref_id_differs_from_grant_id(self):
        recs = self.ex02()
        self.assertNotEqual(self.of(recs, 'grant')['grant_id'], self.REF)
        t = self.one(recs, 0)
        self.assertEqual((t.state, t.reasons, t.candidate_positions, t.claim_status, t.kind_is_grant, t.source_role),
                         ('LINKED', (), (1,), 'AGREE', True, 'task_grant_ref'))
        self.assertIs(t.link_is_authority, False)
        e = self.one(recs, 5)
        self.assertEqual((e.state, e.in_task_grant_refs, e.source_role, e.candidate_positions),
                         ('LINKED', True, 'effect_grant_ref_id', (1,)))
        for p in (1, 2, 3, 4):
            self.assertEqual(self.links(recs, p), ())

    def test_ref_id_is_never_matched_against_grant_id(self):
        recs = self.ex02()
        self.of(recs, 'task')['authority']['grant_refs'][0]['ref_id'] = 'EXAMPLE-grant-1'  # = grant_id, not an issuer_ref id
        link = self.one(recs, 0)
        self.assertEqual((link.state, link.candidate_positions, link.reasons), ('NO_GRANT_RECORD', (), ('NO_CANDIDATE',)))

    def test_no_issuer_ref_means_no_grant_record(self):
        recs = self.ex02()
        del self.of(recs, 'grant')['issuer_ref']
        self.assertEqual(self.one(recs, 0).state, 'NO_GRANT_RECORD')

    def test_two_candidates_are_ambiguous_including_revisions_and_none_is_latest(self):
        recs = self.ex02()
        other = copy.deepcopy(recs[1])
        other['grant_id'] = 'EXAMPLE-grant-OTHER'
        link = self.one(recs + [other], 0)
        self.assertEqual((link.state, link.candidate_positions, link.reasons), ('AMBIGUOUS', (1, 6), ('MULTIPLE_CANDIDATES',)))
        rev2 = copy.deepcopy(recs[1])
        rev2['grant_revision'] = 2
        link = self.one(recs + [rev2], 0)
        self.assertEqual((link.state, link.candidate_positions), ('AMBIGUOUS', (1, 6)))

    def test_claim_conflict_is_the_primary_state_and_candidates_are_preserved(self):
        recs = self.ex02()
        self.of(recs, 'grant')['issuer_ref']['digest'] = 'sha256:' + '0' * 64
        for p in (0, 5):
            link = self.one(recs, p)
            self.assertEqual((link.state, link.candidate_positions, link.claim_status), ('CONFLICT', (1,), 'CONFLICT'))
            self.assertIn('CLAIM_CONFLICT', link.reasons)
            self.assertEqual(link.claim_conflict_fields, ('digest',))
            self.assertIs(link.link_is_authority, False)

    def test_group_kind_other_than_grant_is_a_conflict_even_when_claims_agree(self):
        recs = self.ex02()
        self.of(recs, 'grant')['issuer_ref']['kind'] = 'user_intent'
        self.of(recs, 'task')['authority']['grant_refs'][0]['kind'] = 'user_intent'
        link = self.one(recs, 0)
        self.assertEqual((link.state, link.claim_status, link.kind_is_grant), ('CONFLICT', 'AGREE', False))
        self.assertIn('KIND_NOT_GRANT', link.reasons)

    def test_effect_reference_outside_the_task_refs_is_a_conflict(self):
        recs = self.ex02()
        extra = copy.deepcopy(recs[1])
        extra['grant_id'] = 'EXAMPLE-grant-X'
        extra['issuer_ref']['ref_id'] = 'EXAMPLE-grant-ref-X'
        recs.append(extra)
        self.of(recs, 'effect')['grant_ref_ids'] = [self.REF, 'EXAMPLE-grant-ref-X']
        links = self.links(recs, 5)
        self.assertEqual([l.state for l in links], ['LINKED', 'CONFLICT'])
        self.assertEqual((links[1].reasons, links[1].in_task_grant_refs, links[1].candidate_positions),
                         (('NOT_IN_TASK_GRANT_REFS',), False, (6,)))

    def test_effect_without_a_resolvable_task_is_incomplete_and_ambiguous_task_is_ambiguous(self):
        recs = self.ex02()
        task = recs.pop(0)
        link = self.one(recs, self.pos(recs, 'effect'))
        self.assertEqual((link.state, link.in_task_grant_refs, link.reasons), ('INCOMPLETE', None, ('TASK_UNRESOLVED',)))
        recs2 = [task, copy.deepcopy(task)] + recs
        link = self.one(recs2, self.pos(recs2, 'effect'))
        self.assertEqual((link.state, link.reasons), ('AMBIGUOUS', ('TASK_AMBIGUOUS',)))

    def test_missing_task_and_no_candidate_reports_both(self):
        recs = self.ex02()
        recs.pop(0)
        recs.pop(0)  # grant too
        link = self.one(recs, self.pos(recs, 'effect'))
        self.assertEqual(link.state, 'NO_GRANT_RECORD')
        self.assertEqual(set(link.reasons), {'NO_CANDIDATE', 'TASK_UNRESOLVED'})

    def test_repeated_task_ref_gives_one_link_per_element_and_malformed_element_is_unsupported(self):
        recs = self.ex02()
        refs = self.of(recs, 'task')['authority']['grant_refs']
        refs.append(copy.deepcopy(refs[0]))
        refs.append({'kind': 'grant'})
        links = self.links(recs, 0)
        self.assertEqual([l.state for l in links], ['LINKED', 'LINKED', 'UNSUPPORTED'])
        self.assertEqual(links[2].reasons, ('MALFORMED_RECORD',))
        self.assertEqual(links[1].source_locator, 'records[0].authority.grant_refs[1]')

    def test_empty_or_absent_refs_and_other_record_types_give_empty_tuple(self):
        recs = self.ex02()
        self.of(recs, 'task')['authority']['grant_refs'] = []
        self.assertEqual(self.links(recs, 0), ())
        self.of(recs, 'effect')['grant_ref_ids'] = []
        self.assertEqual(self.links(recs, 5), ())

    def test_argument_errors(self):
        recs = self.ex02()
        index = self.index(recs)
        claims = self.refs.collect_claims(index)
        with self.assertRaises(ValueError):
            self.refs.link_grants(index, claims, 99)
        with self.assertRaises(ValueError):
            self.refs.link_grants(index, claims, -1)
        for bad in ('0', None, 1.0, True):
            with self.assertRaises(TypeError):
                self.refs.link_grants(index, claims, bad)
        with self.assertRaises(TypeError):
            self.refs.link_grants(recs, claims, 0)
        with self.assertRaises(TypeError):
            self.refs.link_grants(index, recs, 0)


# ====================================================================== kernel
class KernelTests(Base):
    def test_every_valid_example_task_matches_c1_functions_and_declared_bindings(self):
        ref = load_module_from(REF_TEST, 'law_ref_candidate_for_s2')
        policy_obj = json.loads(self.policy_bytes.decode('utf-8'))
        expected = read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))
        seen = 0
        for case in expected['cases']:
            if not case['schema_valid']:
                continue
            for task in (r for r in self.ex(case['file'][:-5])['records'] if r['record_type'] == 'task'):
                with self.subTest(case['file']):
                    d = self.binding.recompute_task(task)
                    want = ref.binding_digests(copy.deepcopy(task), policy_obj)
                    self.assertEqual((d.intent.digest, d.accepted_task.digest, d.context.digest),
                                     (want['intent_digest'], want['accepted_task_digest'], want['context_digest']))
                    self.assertEqual(self.policy.digest, want['policy_digest'])
                    self.assertTrue(all(p.state == 'COMPUTED' for p in (d.intent, d.accepted_task, d.context) + d.actions))
                    self.assertEqual(len(d.actions), len(task['effects']['actions']))
                    for a, part in zip(task['effects']['actions'], d.actions):
                        self.assertEqual(part.digest, ref.digest_of(ref.action_part(copy.deepcopy(a))))
                    seen += 1
        self.assertGreaterEqual(seen, 10)

    def test_c1_projection_vectors(self):
        fx = self.vectors['projection_fixture']
        d = self.binding.recompute_task(fx['task'])
        want = fx['expected']
        self.assertEqual((d.intent.digest, d.context.digest, d.accepted_task.digest, d.actions[0].digest),
                         (want['intent'], want['context'], want['task'], want['action']))

    def schema_valid(self, records):
        owners = self.loader.load_owners()
        ok, reasons, details = self.loader.validate_structure({
            'schema_version': 'law.cvf.control/2', 'record_type': 'bundle', 'evaluation_basis': 'COOPERATIVE_WORKFLOW',
            'bundle_id': 'EXAMPLE-s2', 'records': records}, owners)
        return ok, reasons

    def test_schema_valid_metadata_outside_projection_is_not_canonical_rejected(self):
        recs = self.ex02()
        base = self.binding.recompute_task(recs[0])
        task = recs[0]
        task['note'] = 'metadata ' + NFD
        task['intent']['refs'][0]['locator'] = 'EXAMPLE://' + NFD
        task['intent']['refs'][0]['attribution']['note'] = NFD
        task['authority']['grant_refs'][0]['attribution']['evidence_locator'] = 'EXAMPLE://' + NFD
        self.of(recs, 'grant')['limits'] = {'max_retries': 1.0}
        ok, reasons = self.schema_valid(recs)
        self.assertTrue(ok, reasons)
        d = self.binding.recompute_task(task)
        self.assertEqual(d, base)
        self.assertTrue(all(p.state == 'COMPUTED' for p in (d.intent, d.accepted_task, d.context)))
        # cùng nội dung ở S1: screen toàn bundle từ chối / the S1 whole-bundle screen rejects the same bundle
        res = self.entry.check_bytes(json.dumps({'schema_version': 'law.cvf.control/2', 'record_type': 'bundle',
                                                 'evaluation_basis': 'COOPERATIVE_WORKFLOW', 'bundle_id': 'EXAMPLE-s2',
                                                 'records': recs}).encode('utf-8'), 'effect', 'v2')
        self.assertEqual(res['reasons'], ['UNSUPPORTED_BINDING_PART'])

    def test_the_same_content_inside_the_projection_is_unsupported_only_for_the_parts_it_feeds(self):
        def part_states(d):
            return (d.intent.state, d.context.state, d.accepted_task.state, tuple(p.state for p in d.actions))

        cases = {
            'main_interpretation': (lambda t: t['intent'].__setitem__('main_interpretation', NFD),
                                    ('COMPUTED', 'COMPUTED', 'UNSUPPORTED', ('COMPUTED',))),
            'requirement statement': (lambda t: t['acceptance']['requirements'][0].__setitem__('statement', NFD),
                                      ('COMPUTED', 'COMPUTED', 'UNSUPPORTED', ('COMPUTED',))),
            'envelope model': (lambda t: t['envelope']['model'].__setitem__('value', NFD),
                               ('COMPUTED', 'COMPUTED', 'UNSUPPORTED', ('COMPUTED',))),
            'action tool': (lambda t: t['effects']['actions'][0].__setitem__('tool', NFD),
                            ('COMPUTED', 'COMPUTED', 'UNSUPPORTED', ('UNSUPPORTED',))),
            'intent ref digest': (lambda t: t['intent']['refs'][0].__setitem__('digest', NFD),
                                  ('UNSUPPORTED', 'COMPUTED', 'UNSUPPORTED', ('COMPUTED',))),
            'context ref source_id': (lambda t: t.__setitem__('context_refs', [
                {'path': 'references/c.txt', 'digest': 'sha256:' + '3' * 64, 'source_id': NFD}]),
                                      ('COMPUTED', 'UNSUPPORTED', 'COMPUTED', ('COMPUTED',))),
            'input source_id': (lambda t: t['inputs'][0].__setitem__('source_id', NFD),
                                ('COMPUTED', 'COMPUTED', 'UNSUPPORTED', ('COMPUTED',))),
        }
        for label, (mutate, want) in cases.items():
            with self.subTest(label):
                task = self.of(self.ex02(), 'task')
                mutate(task)
                d = self.binding.recompute_task(task)
                self.assertEqual(part_states(d), want)
                bad = [p for p in (d.intent, d.context, d.accepted_task) + d.actions if p.state == 'UNSUPPORTED']
                self.assertTrue(all(p.reason == 'NON_NFC_STRING' and p.digest is None for p in bad))

    def test_float_huge_integer_surrogate_and_duplicate_sets(self):
        task = self.of(self.ex02(), 'task')
        task['envelope']['max'] = 1.5
        d = self.binding.recompute_task(task)
        self.assertEqual((d.accepted_task.state, d.accepted_task.reason, d.intent.state), ('UNSUPPORTED', 'NON_INTEGER_NUMBER', 'COMPUTED'))
        task = self.of(self.ex02(), 'task')
        task['acceptance']['n'] = 2 ** 60
        self.assertEqual(self.binding.recompute_task(task).accepted_task.reason, 'INTEGER_OUT_OF_RANGE')
        task = self.of(self.ex02(), 'task')
        task['intent']['main_interpretation'] = '\ud800'
        self.assertEqual(self.binding.recompute_task(task).accepted_task.reason, 'LONE_SURROGATE')
        task = self.of(self.ex02(), 'task')
        task['effects']['actions'][0]['targets'] = ['a', 'a']
        d = self.binding.recompute_task(task)
        self.assertEqual((d.accepted_task.reason, d.actions[0].reason, d.context.state), ('DUPLICATE_SET_ELEMENT',) * 2 + ('COMPUTED',))
        task = self.of(self.ex02(), 'task')
        obj = {'path': 'references/c.txt', 'digest': 'sha256:' + '3' * 64}
        task['context_refs'] = [obj, dict(obj)]
        d = self.binding.recompute_task(task)
        self.assertEqual((d.context.reason, d.accepted_task.state), ('DUPLICATE_SET_ELEMENT', 'COMPUTED'))

    def test_malformed_content_never_raises(self):
        for label, task in {
            'empty': {},
            'effects none': {'effects': None},
            'actions string': {'effects': {'actions': 'x', 'on_missing': 'STOP_DEPENDENT_EFFECT'}},
            'intent list': {'intent': []},
            'missing refs': {'intent': {}, 'authority': {}},
        }.items():
            with self.subTest(label):
                d = self.binding.recompute_task(task)
                self.assertEqual((d.intent.state, d.accepted_task.state, d.context.state), ('UNSUPPORTED',) * 2 + ('COMPUTED',)
                                 if label != 'empty' else ('UNSUPPORTED', 'UNSUPPORTED', 'COMPUTED'))
                self.assertEqual(d.intent.reason, 'MALFORMED_RECORD')
        deep = self.of(self.ex02(), 'task')
        cursor = deep['acceptance']
        for _ in range(3000):
            cursor['x'] = {}
            cursor = cursor['x']
        d = self.binding.recompute_task(deep)
        self.assertEqual((d.accepted_task.state, d.accepted_task.reason), ('UNSUPPORTED', 'MALFORMED_RECORD'))
        for bad in ('x', None, [], 5):
            with self.assertRaises(TypeError):
                self.binding.recompute_task(bad)


# ====================================================================== object sets
class ObjectSetTests(Base):
    def o(self, path='a.txt', digest='1', **q):
        d = {'path': path, 'digest': 'sha256:' + digest * 64}
        d.update(q)
        return d

    def cmp(self, a, b, mode='EXACT_QUALIFIED', **k):
        return self.binding.compare_object_sets(a, b, mode, **k)

    def test_caller_metadata_cannot_upgrade_basis_or_escape_closed_locator(self):
        items = [self.o('a')]
        for basis in ('RECOMPUTED', 'LITERAL', 'UNKNOWN'):
            with self.subTest(basis=basis), self.assertRaises(ValueError):
                self.cmp(items, items, basis=basis)
        for locator in ('law_review_canary\n', 'records[0].law_private_marker', '.binding.inputs\n'):
            with self.subTest(locator=repr(locator)), self.assertRaises(ValueError):
                self.cmp(items, items, locator=locator)
        for basis in ('DECLARED_SET', 'PEER_CLAIM'):
            rel = self.cmp(items, items, basis=basis, locator='records[0].binding.inputs')
            self.assertEqual((rel.state, rel.basis), ('MATCH', basis))
        with self.assertRaises(ValueError):
            self.cmp(items, items, name='law_review_canary\n')

    def test_exact_qualified(self):
        base = [self.o('a'), self.o('b', '2', source_id='S', revision='1')]
        r = self.cmp(base, list(reversed(copy.deepcopy(base))), name='scope')
        self.assertEqual((r.name, r.state, r.basis, r.limitations), ('scope', 'MATCH', 'DECLARED_SET', ('UNVERIFIED_RAW_BYTES',)))
        changed = {
            'source_id removed': [self.o('a'), self.o('b', '2', revision='1')],
            'revision differs': [self.o('a'), self.o('b', '2', source_id='S', revision='2')],
            'scope added': [self.o('a'), self.o('b', '2', source_id='S', revision='1', scope='s')],
            'digest differs': [self.o('a'), self.o('b', '3', source_id='S', revision='1')],
            'path differs by case': [self.o('A'), self.o('b', '2', source_id='S', revision='1')],
            'extra element': base + [self.o('c')],
            'missing element': base[:1],
        }
        for label, other in changed.items():
            with self.subTest(label):
                r = self.cmp(base, other)
                self.assertEqual(r.state, 'MISMATCH')
        r = self.cmp(base, base + [self.o('c')])
        self.assertEqual(dict(r.counts), {'only_left': 0, 'only_right': 1})

    def test_duplicates_and_out_of_domain_are_unsupported_not_deduped(self):
        r = self.cmp([self.o('a'), self.o('a')], [self.o('a')])
        self.assertEqual((r.state, r.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        r = self.cmp([self.o('a')], [self.o('a'), self.o('a')])
        self.assertEqual((r.state, r.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        r = self.cmp([self.o('a' + NFD)], [self.o('a' + NFD)])
        self.assertEqual((r.state, r.reason), ('UNSUPPORTED', 'NON_NFC_STRING'))
        for bad in ('x', [1], [{'path': 'a'}], {'a': 1}):
            with self.subTest(bad=bad):
                self.assertEqual(self.cmp(bad, [self.o('a')]).state, 'UNSUPPORTED')
                self.assertEqual(self.cmp(bad, [self.o('a')]).reason, 'MALFORMED_RECORD')

    def test_absent_sides(self):
        self.assertEqual(self.cmp(None, None).state, 'NOT_BOUND')
        self.assertEqual(self.cmp([self.o()], None).state, 'ONE_SIDED')
        self.assertEqual(self.cmp(None, [self.o()]).state, 'ONE_SIDED')
        self.assertEqual(self.cmp([], []).state, 'MATCH')
        self.assertEqual(self.cmp([], [self.o()]).state, 'MISMATCH')

    def test_cover_requires_path_digest_and_supplied_qualifiers_both_ways(self):
        arts = [self.o('a', source_id='S', revision='1'), self.o('b', '2')]
        summary = [self.o('a'), self.o('b', '2')]  # qualifier tùy chọn có thể vắng / optional qualifiers may be omitted
        self.assertEqual(self.cmp(summary, arts, 'COVER_REQUIRED_QUALIFIERS').state, 'MATCH')
        self.assertEqual(self.cmp(arts, summary, 'COVER_REQUIRED_QUALIFIERS').state, 'MISMATCH')  # qualifier khai ở trái, vắng ở phải
        self.assertEqual(self.cmp([self.o('a', source_id='X')], arts[:1], 'COVER_REQUIRED_QUALIFIERS').state, 'MISMATCH')
        self.assertEqual(self.cmp(summary[:1], arts, 'COVER_REQUIRED_QUALIFIERS').state, 'MISMATCH')  # artifact b không được phủ
        self.assertEqual(self.cmp(summary + [self.o('z', '9')], arts, 'COVER_REQUIRED_QUALIFIERS').state, 'MISMATCH')
        r = self.cmp([self.o('a'), self.o('a')], arts, 'COVER_REQUIRED_QUALIFIERS')
        self.assertEqual((r.state, r.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        r = self.cmp(summary, arts, 'COVER_REQUIRED_QUALIFIERS')
        self.assertEqual(r.limitations, ('UNVERIFIED_RAW_BYTES',))

    def test_mode_and_type_errors(self):
        with self.assertRaises(ValueError):
            self.cmp([], [], 'LOOSE')
        with self.assertRaises(ValueError):
            self.cmp([], [], None)
        with self.assertRaises(TypeError):
            self.binding.compare_object_sets([], [], 'EXACT_QUALIFIED', name=5)

    def test_pre_effect_scope_is_only_a_declared_set_and_never_mapped_to_the_task_digest(self):
        recs = self.ex02()
        pre = self.of(recs, 'review', 0)
        self.assertEqual(pre['scope']['objects'][0]['digest'], pre['binding']['accepted_task_digest'])
        r = self.cmp(pre['scope']['objects'], copy.deepcopy(pre['scope']['objects']), 'COVER_REQUIRED_QUALIFIERS', name='scope')
        self.assertEqual((r.state, r.basis, r.limitations), ('MATCH', 'DECLARED_SET', ('UNVERIFIED_RAW_BYTES',)))
        names = {rel.name for p in (2, 3, 4, 5) for rel in self.report(recs, p).relations}
        self.assertFalse([n for n in names if 'SCOPE' in n.upper()], names)
        d = r.as_dict()
        self.assertEqual((d['bytes_observed'], d['authenticity_observed'], d['semantic_verified']), (False, False, False))


# ====================================================================== binding relations
class BindingTests(Base):
    MATCHES = ['B-REF', 'B-LIT.bind_version', 'B-LIT.evaluation_basis', 'B-LIT.policy_version', 'B-INTENT', 'B-TASK', 'B-CONTEXT',
               'B-POLICY', 'B-INPUTS']

    def test_present_null_sets_in_records_are_malformed_not_absent(self):
        for field in ('inputs', 'outputs'):
            with self.subTest(peer_field=field):
                left = copy.deepcopy(self.ex02()[2]['binding'])
                left[field] = None
                relations = self.binding.compare_peer_bindings(left, copy.deepcopy(left))
                relation = next(r for r in relations if r.name == 'peer.' + field)
                self.assertEqual((relation.state, relation.reason), ('UNSUPPORTED', 'MALFORMED_RECORD'))
        for rtype, field, name in (('review', 'inputs', 'B-INPUTS'),
                                   ('review', 'outputs', 'B-OUTPUTS'),
                                   ('result', 'outputs', 'B-OUT-RESULT')):
            with self.subTest(record_type=rtype, field=field):
                recs = self.ex02()
                position = self.pos(recs, rtype)
                recs[position]['binding'][field] = None
                relation = next(r for r in self.report(recs, position).relations if r.name == name)
                self.assertEqual((relation.state, relation.reason), ('UNSUPPORTED', 'MALFORMED_RECORD'))

    def test_ex02_relations_are_listed_per_record_not_blanket_match(self):
        recs = self.ex02()
        review_pre = self.states(self.report(recs, 2))
        self.assertEqual({k: review_pre[k] for k in self.MATCHES}, dict.fromkeys(self.MATCHES, 'MATCH'))
        self.assertEqual((review_pre['B-ACTION-CLAIM'], review_pre['B-OUTPUTS']), ('NOT_BOUND', 'NOT_BOUND'))
        review_int = self.states(self.report(recs, 3))
        self.assertEqual((review_int['B-ACTION-CLAIM'], review_int['B-OUTPUTS']), ('NOT_BOUND', 'NOT_APPLICABLE'))
        result = self.states(self.report(recs, 4))
        self.assertEqual(result['B-OUT-RESULT'], 'MATCH')
        self.assertEqual(result['B-ACTION-CLAIM'], 'NOT_BOUND')
        self.assertNotIn('B-OUTPUTS', result)
        effect_rep = self.report(recs, 5)
        effect = self.states(effect_rep)
        self.assertEqual((effect['B-ACTION-OWN'], effect['B-ACTION-IN-TASK'], effect['B-OUTPUTS']), ('MATCH', 'MATCH', 'NOT_APPLICABLE'))
        self.assertEqual(self.rel(effect_rep.relations, 'B-ACTION-IN-TASK').indexes, (0,))
        self.assertNotIn('B-ACTION-CLAIM', effect)
        for p in (0, 1):
            rep = self.report(recs, p)
            self.assertEqual((rep.applicable, rep.recomputation_complete, rep.relations[0].state), (False, False, 'NOT_APPLICABLE'))
        for p in (2, 3, 4, 5):
            self.assertIs(self.report(recs, p).recomputation_complete, True)
            self.assertEqual(self.report(recs, p).position, p)

    def test_constant_non_observation_flags_on_every_relation(self):
        for rel in self.report(self.ex02(), 5).relations:
            d = rel.as_dict()
            self.assertIn(d['state'], STATES)
            self.assertEqual((d['bytes_observed'], d['authenticity_observed'], d['semantic_verified']), (False, False, False))

    def test_edit_after_binding_flags_exactly_the_dependent_relations(self):
        def mut(f):
            recs = self.ex02()
            f(self.of(recs, 'task'))
            return recs

        cases = {
            'main_interpretation': (lambda t: t['intent'].__setitem__('main_interpretation', 'other'), {'B-TASK'}),
            'requirement': (lambda t: t['acceptance']['requirements'][0].__setitem__('statement', 'other'), {'B-TASK'}),
            'input digest': (lambda t: t['inputs'][0].__setitem__('digest', 'sha256:' + '0' * 64), {'B-TASK', 'B-INPUTS'}),
            'input revision': (lambda t: t['inputs'][0].__setitem__('revision', '2'), {'B-TASK', 'B-INPUTS'}),
            'action target': (lambda t: t['effects']['actions'][0]['targets'].append('references/other.xlsx'), {'B-TASK'}),
            'context ref': (lambda t: t.__setitem__('context_refs', [{'path': 'references/c.txt', 'digest': 'sha256:' + '3' * 64}]),
                            {'B-CONTEXT'}),
            'intent ref digest': (lambda t: t['intent']['refs'][0].__setitem__('digest', 'sha256:' + '1' * 64), {'B-INTENT', 'B-TASK'}),
            'grant ref digest': (lambda t: t['authority']['grant_refs'][0].__setitem__('digest', 'sha256:' + '2' * 64), {'B-TASK'}),
            'task note (outside projection)': (lambda t: t.__setitem__('note', 'other'), set()),
            'proposed_by (outside projection)': (lambda t: t.__setitem__('proposed_by', {'actor_id': 'x', 'role': 'main'}), set()),
        }
        for label, (f, flagged) in cases.items():
            with self.subTest(label):
                recs = mut(f)
                for p in (2, 3, 4, 5):
                    rep = self.report(recs, p)
                    st = self.states(rep)
                    mism = {k for k in ('B-INTENT', 'B-TASK', 'B-CONTEXT', 'B-INPUTS') if st[k] == 'MISMATCH'}
                    self.assertEqual(mism, flagged, (label, p, st))
                    self.assertEqual(st['B-REF'], 'MATCH')
                    self.assertIs(rep.recomputation_complete, True)  # MISMATCH đã tính đủ vẫn là complete / a fully computed MISMATCH is still complete

    def test_policy_change_and_literal_mismatch(self):
        recs = self.ex02()
        changed = json.loads(self.policy_bytes)
        changed['note'] = changed['note'] + ' changed'
        ctx = self.binding.make_policy_context(json.dumps(changed).encode('utf-8'))
        self.assertEqual((ctx.state, ctx.literals_ok), ('COMPUTED', True))
        st = self.states(self.report(recs, 2, ctx))
        self.assertEqual(st['B-POLICY'], 'MISMATCH')
        self.assertEqual(st['B-TASK'], 'MATCH')
        wrong = json.loads(self.policy_bytes)
        wrong['policy_version'] = 'law.cvf.routing/1'
        ctx = self.binding.make_policy_context(json.dumps(wrong).encode('utf-8'))
        rep = self.report(recs, 2, ctx)
        self.assertEqual((self.states(rep)['B-POLICY'], self.rel(rep.relations, 'B-POLICY').reason), ('UNSUPPORTED', 'POLICY_LITERAL_MISMATCH'))
        self.assertIs(rep.recomputation_complete, False)
        recs = self.ex02()
        self.of(recs, 'review')['binding']['policy_version'] = 'law.cvf.routing/1'
        self.assertEqual(self.states(self.report(recs, 2))['B-LIT.policy_version'], 'MISMATCH')

    def test_missing_or_ambiguous_task_is_incomplete_even_when_peers_agree(self):
        recs = self.ex02()
        task = recs.pop(0)
        for p in range(len(recs)):
            rep = self.report(recs, p)
            if not rep.applicable:
                continue
            st = self.states(rep)
            for k in ('B-REF', 'B-INTENT', 'B-TASK', 'B-CONTEXT', 'B-INPUTS'):
                self.assertEqual(st[k], 'INCOMPLETE', (p, k))
            self.assertEqual(st['B-POLICY'], 'MATCH')  # chỉ cần policy / needs only the policy
            self.assertIs(rep.recomputation_complete, False)
            self.assertEqual(st['B-LIT.bind_version'], 'MATCH')
        peers = self.binding.compare_peer_bindings(recs[1]['binding'], recs[-1]['binding'])
        self.assertEqual(self.rel(peers, 'peer.accepted_task_digest').state, 'MATCH')
        recs2 = [task, copy.deepcopy(task)] + recs
        rep = self.report(recs2, self.pos(recs2, 'review'))
        st = self.states(rep)
        self.assertEqual((st['B-REF'], st['B-TASK'], st['B-INPUTS']), ('AMBIGUOUS',) * 3)
        self.assertIs(rep.recomputation_complete, False)

    def test_unsupported_parts_and_unsupported_policy_are_not_complete(self):
        recs = self.ex02()
        self.of(recs, 'task')['intent']['main_interpretation'] = NFD
        rep = self.report(recs, 2)
        st = self.states(rep)
        self.assertEqual((st['B-TASK'], st['B-INTENT'], st['B-CONTEXT'], st['B-INPUTS']), ('UNSUPPORTED', 'MATCH', 'MATCH', 'MATCH'))
        self.assertEqual(self.rel(rep.relations, 'B-TASK').reason, 'NON_NFC_STRING')
        self.assertIs(rep.recomputation_complete, False)
        bad_ctx = self.binding.make_policy_context(b'{')
        rep = self.report(self.ex02(), 2, bad_ctx)
        self.assertEqual(self.states(rep)['B-POLICY'], 'UNSUPPORTED')
        self.assertIs(rep.recomputation_complete, False)

    def test_vacuous_complete_is_false(self):
        recs = [self.of(self.ex02(), 'grant')]
        rep = self.report(recs, 0)
        self.assertEqual((rep.applicable, rep.recomputation_complete), (False, False))
        review = self.of(self.ex02(), 'review')
        review['binding'] = {}
        rep = self.report([review], 0)
        self.assertIs(rep.recomputation_complete, False)

    def test_peer_equality_is_not_recomputation(self):
        recs = self.ex02()
        self.of(recs, 'task')['inputs'][0]['digest'] = 'sha256:' + '0' * 64  # task đổi sau khi ký / task edited after binding
        a, b = self.of(recs, 'review', 0)['binding'], self.of(recs, 'effect')['binding']
        peers = self.binding.compare_peer_bindings(a, b)
        self.assertEqual({r.name: r.state for r in peers}['peer.accepted_task_digest'], 'MATCH')
        self.assertEqual({r.name: r.state for r in peers}['peer.inputs'], 'MATCH')
        for r in peers:
            self.assertEqual(r.basis, 'PEER_CLAIM')
        st = self.states(self.report(recs, 5))
        self.assertEqual((st['B-TASK'], st['B-INPUTS']), ('MISMATCH', 'MISMATCH'))

    def test_peer_one_sided_and_not_bound(self):
        recs = self.ex02()
        pre, eff = self.of(recs, 'review', 0)['binding'], self.of(recs, 'effect')['binding']
        peers = {r.name: r.state for r in self.binding.compare_peer_bindings(pre, eff)}
        self.assertEqual((peers['peer.outputs'], peers['peer.action_digest']), ('ONE_SIDED', 'ONE_SIDED'))
        self.assertEqual(peers['peer.task_id'], 'MATCH')
        peers = {r.name: r.state for r in self.binding.compare_peer_bindings(pre, copy.deepcopy(pre))}
        self.assertEqual((peers['peer.outputs'], peers['peer.action_digest']), ('NOT_BOUND', 'NOT_BOUND'))
        both = {r.name: r.state for r in self.binding.compare_peer_bindings(eff, copy.deepcopy(eff))}
        self.assertEqual((both['peer.outputs'], both['peer.action_digest']), ('MATCH', 'MATCH'))
        other = copy.deepcopy(eff)
        other['outputs'][0]['digest'] = 'sha256:' + '0' * 64
        self.assertEqual({r.name: r.state for r in self.binding.compare_peer_bindings(eff, other)}['peer.outputs'], 'MISMATCH')
        with self.assertRaises(TypeError):
            self.binding.compare_peer_bindings([], eff)

    def test_ex08_stale_group_is_the_one_that_disagrees_with_the_task(self):
        recs = self.refs.records_of(self.ex('ex08_binding_stale_input_revision'))
        reviews = [p for p, r in enumerate(recs) if r['record_type'] == 'review']
        later = [p for p, r in enumerate(recs) if r['record_type'] in ('effect', 'result')]
        group_a = {p: self.states(self.report(recs, p)) for p in reviews}
        group_b = {p: self.states(self.report(recs, p)) for p in later}
        a_inputs = {s['B-INPUTS'] for s in group_a.values()}
        b_inputs = {s['B-INPUTS'] for s in group_b.values()}
        self.assertEqual(len(a_inputs), 1)
        self.assertEqual(len(b_inputs), 1)
        self.assertEqual(a_inputs | b_inputs, {'MATCH', 'MISMATCH'})
        stale = group_a if 'MISMATCH' in a_inputs else group_b
        self.assertTrue(all(s['B-TASK'] == 'MISMATCH' or s['B-INPUTS'] == 'MISMATCH' for s in stale.values()))
        peers = {r.name: r.state for r in self.binding.compare_peer_bindings(recs[reviews[0]]['binding'], recs[later[0]]['binding'])}
        self.assertEqual((peers['peer.inputs'], peers['peer.accepted_task_digest']), ('MISMATCH', 'MISMATCH'))

    def test_action_relations_optional_present_and_subset_only(self):
        recs = self.ex02()
        eff = self.of(recs, 'effect')
        del eff['binding']['action_digest']
        st = self.states(self.report(recs, 5))
        self.assertEqual((st['B-ACTION-OWN'], st['B-ACTION-IN-TASK']), ('NOT_BOUND', 'MATCH'))
        recs = self.ex02()
        self.of(recs, 'effect')['action']['tool'] = 'EXAMPLE-other-tool'
        st = self.states(self.report(recs, 5))
        self.assertEqual((st['B-ACTION-OWN'], st['B-ACTION-IN-TASK']), ('MISMATCH', 'MISMATCH'))
        # review/result mang action_digest: khớp tập con action, không phủ toàn result
        recs = self.ex02()
        task = self.of(recs, 'task')
        second = copy.deepcopy(task['effects']['actions'][0])
        second['targets'] = ['references/second.xlsx']
        task['effects']['actions'].append(second)
        d = self.binding.recompute_task(task)
        review = self.of(recs, 'review', 0)
        review['binding']['action_digest'] = d.actions[1].digest
        rep = self.report(recs, 2)
        claim = self.rel(rep.relations, 'B-ACTION-CLAIM')
        self.assertEqual((claim.state, claim.indexes, claim.limitations), ('MATCH', (1,), ('SUBSET_OF_ACTIONS_ONLY',)))
        review['binding']['action_digest'] = 'sha256:' + '0' * 64
        self.assertEqual(self.rel(self.report(recs, 2).relations, 'B-ACTION-CLAIM').state, 'MISMATCH')
        task['effects']['actions'][1] = copy.deepcopy(task['effects']['actions'][0])  # hai action y hệt / two identical actions
        d = self.binding.recompute_task(task)
        review['binding']['action_digest'] = d.actions[0].digest
        claim = self.rel(self.report(recs, 2).relations, 'B-ACTION-CLAIM')
        self.assertEqual((claim.state, claim.indexes), ('MATCH', (0, 1)))
        # result có action_digest cũng chỉ là tuyên bố về tập con
        result = self.of(recs, 'result')
        result['binding']['action_digest'] = d.actions[0].digest
        self.assertEqual(self.rel(self.report(recs, 4).relations, 'B-ACTION-CLAIM').limitations, ('SUBSET_OF_ACTIONS_ONLY',))

    def test_effect_action_is_compared_by_whole_projection_not_by_operation_tool_targets(self):
        recs = self.ex02()
        self.of(recs, 'effect')['action']['write_zone'] = 'working'
        st = self.states(self.report(recs, 5))
        self.assertEqual(st['B-ACTION-IN-TASK'], 'MISMATCH')

    def test_inputs_duplicate_order_and_qualifiers(self):
        recs = self.ex02()
        rev = self.of(recs, 'review', 0)['binding']
        rev['inputs'] = rev['inputs'] + copy.deepcopy(rev['inputs'])
        r = self.rel(self.report(recs, 2).relations, 'B-INPUTS')
        self.assertEqual((r.state, r.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        self.assertIs(self.report(recs, 2).recomputation_complete, False)
        recs = self.ex02()
        task = self.of(recs, 'task')
        extra = {'path': 'references/b.docx', 'digest': 'sha256:' + '5' * 64}
        task['inputs'].append(extra)
        for r in recs:
            if 'binding' in r:
                r['binding']['inputs'] = [copy.deepcopy(extra)] + r['binding']['inputs']
        # accepted_task_digest của binding giờ lệch (input mới) nhưng thứ tự đảo vẫn MATCH ở B-INPUTS
        self.assertEqual(self.states(self.report(recs, 2))['B-INPUTS'], 'MATCH')
        del self.of(recs, 'review', 0)['binding']['inputs'][1]['source_id']
        rep = self.report(recs, 2)
        r = self.rel(rep.relations, 'B-INPUTS')
        self.assertEqual((r.state, dict(r.counts)), ('MISMATCH', {'only_left': 1, 'only_right': 1}))

    def test_result_outputs_vs_artifacts(self):
        recs = self.ex02()
        res = self.of(recs, 'result')
        res['artifacts'][0]['source_id'] = 'S'
        self.assertEqual(self.states(self.report(recs, 4))['B-OUT-RESULT'], 'MISMATCH')
        recs = self.ex02()
        del self.of(recs, 'result')['binding']['outputs']
        st = self.states(self.report(recs, 4))
        self.assertEqual(st['B-OUT-RESULT'], 'NOT_BOUND')
        self.assertIs(self.report(recs, 4).recomputation_complete, True)
        recs = self.ex02()
        self.of(recs, 'result')['artifacts'] = []
        self.assertEqual(self.states(self.report(recs, 4))['B-OUT-RESULT'], 'MISMATCH')

    def test_outputs_on_review_or_effect_are_not_derived_from_anything(self):
        recs = self.ex02()
        eff = self.of(recs, 'effect')
        self.assertIn('outputs', eff['binding'])
        self.assertEqual(self.states(self.report(recs, 5))['B-OUTPUTS'], 'NOT_APPLICABLE')
        self.assertIsNone(self.of(recs, 'task')['effects'].get('expected_outputs'))

    def test_argument_errors(self):
        recs = self.ex02()
        index = self.index(recs)
        with self.assertRaises(ValueError):
            self.binding.compare_binding(index, 6, self.policy)
        with self.assertRaises(ValueError):
            self.binding.compare_binding(index, -1, self.policy)
        for bad in ('0', None, True):
            with self.assertRaises(TypeError):
                self.binding.compare_binding(index, bad, self.policy)
        with self.assertRaises(TypeError):
            self.binding.compare_binding(recs, 0, self.policy)
        with self.assertRaises(TypeError):
            self.binding.compare_binding(index, 0, self.policy_bytes)

    def test_garbage_bindings_never_raise(self):
        garbage = [{'record_type': 'review', 'binding': 'x'}, {'record_type': 'effect', 'binding': {'task_id': 5}},
                   {'record_type': 'result', 'binding': {'task_id': 'T', 'task_revision': 'one', 'inputs': 'nope'}},
                   {'record_type': 'effect', 'binding': {}, 'action': 5}, {'record_type': 'review', 'binding': {'inputs': [1]}}]
        index = self.index(garbage)
        for p in range(len(garbage)):
            rep = self.binding.compare_binding(index, p, self.policy)
            self.assertIs(rep.recomputation_complete, False)
            self.assertTrue(all(r.state in STATES for r in rep.relations))
            self.binding.compare_pointers(index, p, self.policy)


# ====================================================================== pointers
class PointerTests(Base):
    PARENT_FIELDS = ('task_id', 'task_revision', 'accepted_task_digest', 'context_digest')

    def build(self, with_child=False, with_basis=False):
        recs = self.ex09()
        task, effect = recs[0], recs[2]
        if with_child:
            child = copy.deepcopy(task)
            child['task_id'] = 'EXAMPLE-task-2'
            child['effects']['actions'] = [{'operation': 'read', 'tool': 'read', 'targets': ['working/EXAMPLE-work-1/a.md'],
                                            'write_zone': 'none'}]
            child['route_proposal'] = {'policy_version': 'law.cvf.routing/2', 'proposed_rows': ['R-READ_DRAFT']}
            d = self.binding.recompute_task(child)
            ptr = task['effects']['actions'][0]['delegation']['child_task']
            ptr.update(accepted_task_digest=d.accepted_task.digest, context_digest=d.context.digest)
            recs.append(child)
            if with_basis:
                rev = copy.deepcopy(self.of(self.ex02(), 'review', 0))
                rev['binding'].update(task_id='EXAMPLE-task-2', accepted_task_digest=d.accepted_task.digest,
                                      context_digest=d.context.digest, intent_digest=d.intent.digest,
                                      inputs=copy.deepcopy(child['inputs']))
                recs.append(rev)
        self.sync_parent(recs)
        return recs

    def sync_parent(self, recs):
        task, effect = recs[0], recs[2]
        d = self.binding.recompute_task(task)
        task['effects']['actions'][0]['delegation']['parent_task'].update(
            accepted_task_digest=d.accepted_task.digest, context_digest=d.context.digest)
        effect['action'] = copy.deepcopy(task['effects']['actions'][0])
        effect['binding'].update(accepted_task_digest=d.accepted_task.digest, context_digest=d.context.digest)
        d2 = self.binding.recompute_task(task)
        effect['binding']['accepted_task_digest'] = d2.accepted_task.digest

    def pointers(self, recs, p):
        return {r.name: r for r in self.binding.compare_pointers(self.index(recs), p, self.policy)}

    def names(self, rels):
        return {n: r.state for n, r in rels.items()}

    def test_ex09_as_shipped_child_missing_is_incomplete_not_mismatch(self):
        recs = self.ex09()
        rels = self.pointers(recs, 0)
        st = self.names(rels)
        self.assertEqual(st['P-RESOLVE'], 'MATCH')
        self.assertEqual(st['P-SELF'], 'MATCH')
        for k in ('C-RESOLVE', 'C-TASK-DIGEST', 'C-CONTEXT-DIGEST', 'C-BASIS', 'C-INPUTS'):
            self.assertEqual(st[k], 'INCOMPLETE', k)
        self.assertNotIn('P-EFFECT', st)
        self.assertNotIn('MISMATCH', st.values())
        self.assertEqual(rels['P-RESOLVE'].locator, 'records[0].effects.actions[0].delegation.parent_task')
        # cha: digest ví dụ phải khớp tính lại / the shipped parent digests equal the recomputation
        self.assertEqual((st['P-TASK-DIGEST'], st['P-CONTEXT-DIGEST']), ('MATCH', 'MATCH'))

    def test_effect_pointer_vs_effect_binding_and_self(self):
        recs = self.ex09()
        st = self.names(self.pointers(recs, 2))
        self.assertEqual((st['P-SELF'], st['P-EFFECT'], st['P-RESOLVE']), ('MATCH', 'MATCH', 'MATCH'))
        recs[2]['binding']['context_digest'] = 'sha256:' + '0' * 64
        self.assertEqual(self.names(self.pointers(recs, 2))['P-EFFECT'], 'MISMATCH')
        self.assertEqual(self.rel(list(self.pointers(recs, 2).values()), 'P-EFFECT').fields, ('context_digest',))

    def test_parent_digest_off_by_one_character_mismatches_alone(self):
        recs = self.ex09()
        ptr = recs[0]['effects']['actions'][0]['delegation']['parent_task']
        ptr['accepted_task_digest'] = ptr['accepted_task_digest'][:-1] + ('0' if ptr['accepted_task_digest'][-1] != '0' else '1')
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['P-TASK-DIGEST'], st['P-CONTEXT-DIGEST'], st['P-SELF'], st['P-RESOLVE']),
                         ('MISMATCH', 'MATCH', 'MATCH', 'MATCH'))

    def test_parent_other_than_the_containing_task_mismatches_p_self(self):
        recs = self.ex09()
        other = copy.deepcopy(recs[0])
        other['task_id'] = 'EXAMPLE-task-0'
        recs.append(other)
        ptr = recs[0]['effects']['actions'][0]['delegation']['parent_task']
        ptr['task_id'] = 'EXAMPLE-task-0'
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['P-SELF'], st['P-RESOLVE']), ('MISMATCH', 'MATCH'))
        ptr['task_revision'] = 2
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['P-SELF'], st['P-RESOLVE'], st['P-TASK-DIGEST']), ('MISMATCH', 'INCOMPLETE', 'INCOMPLETE'))

    def test_effect_whose_binding_task_is_not_the_pointer_parent_mismatches_p_self(self):
        recs = self.ex09()
        recs[2]['binding']['task_id'] = 'EXAMPLE-task-9'
        st = self.names(self.pointers(recs, 2))
        self.assertEqual((st['P-SELF'], st['P-EFFECT']), ('MISMATCH', 'MISMATCH'))

    def test_child_resolves_and_recomputes(self):
        recs = self.build(with_child=True)
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['C-RESOLVE'], st['C-TASK-DIGEST'], st['C-CONTEXT-DIGEST']), ('MATCH',) * 3)
        self.assertEqual((st['C-BASIS'], st['C-INPUTS']), ('INCOMPLETE', 'INCOMPLETE'))  # chưa record nào bind con
        self.assertEqual((st['P-TASK-DIGEST'], st['P-CONTEXT-DIGEST'], st['P-SELF']), ('MATCH',) * 3)
        child_ptr = recs[0]['effects']['actions'][0]['delegation']['child_task']
        child_ptr['accepted_task_digest'] = 'sha256:' + '0' * 64
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['C-TASK-DIGEST'], st['C-CONTEXT-DIGEST']), ('MISMATCH', 'MATCH'))

    def test_child_basis_records_peer_claims_and_inputs(self):
        recs = self.build(with_child=True, with_basis=True)
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['C-BASIS'], st['C-INPUTS']), ('MATCH', 'MATCH'))
        recs[-1]['binding']['accepted_task_digest'] = 'sha256:' + '0' * 64
        rels = self.pointers(recs, 0)
        self.assertEqual((rels['C-BASIS'].state, rels['C-BASIS'].fields), ('MISMATCH', ('accepted_task_digest',)))
        self.assertEqual(rels['C-BASIS'].basis, 'PEER_CLAIM')
        self.assertEqual(rels['C-TASK-DIGEST'].state, 'MATCH')  # tính lại từ task con, không bị echo của peer che / recomputation is not hidden by peer echo
        recs[-1]['binding']['inputs'] = []
        self.assertEqual(self.names(self.pointers(recs, 0))['C-INPUTS'], 'MISMATCH')

    def test_ambiguous_parent_or_child(self):
        recs = self.build(with_child=True)
        recs.append(copy.deepcopy(recs[0]))
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['P-RESOLVE'], st['P-TASK-DIGEST']), ('AMBIGUOUS', 'AMBIGUOUS'))
        self.assertEqual(st['P-SELF'], 'MATCH')
        recs = self.build(with_child=True)
        recs.append(copy.deepcopy(recs[3]))
        st = self.names(self.pointers(recs, 0))
        self.assertEqual((st['C-RESOLVE'], st['C-TASK-DIGEST']), ('AMBIGUOUS', 'AMBIGUOUS'))

    def test_records_without_delegation_give_empty_tuple_and_errors(self):
        recs = self.ex02()
        index = self.index(recs)
        for p in range(len(recs)):
            self.assertEqual(self.binding.compare_pointers(index, p, self.policy), ())
        with self.assertRaises(ValueError):
            self.binding.compare_pointers(index, 99, self.policy)
        with self.assertRaises(TypeError):
            self.binding.compare_pointers(index, '0', self.policy)

    def test_malformed_delegation_never_raises(self):
        recs = self.ex09()
        recs[0]['effects']['actions'][0]['delegation']['parent_task'] = 'x'
        recs[2]['action']['delegation']['child_task'] = {'task_id': 5}
        for p in (0, 2):
            rels = self.pointers(recs, p)
            self.assertTrue(all(r.state in STATES for r in rels.values()))


# ====================================================================== purity
class PurityTests(Base):
    def test_inputs_are_not_mutated_by_any_helper(self):
        for recs in (self.ex02(), self.ex09(), self.refs.records_of(self.ex('ex08_binding_stale_input_revision'))):
            before = copy.deepcopy(recs)
            policy_before = bytes(self.policy_bytes)
            self.all_results_dicts(recs)
            self.assertEqual(recs, before)
            self.assertEqual(self.policy_bytes, policy_before)
            self.assertEqual(json.dumps(recs, sort_keys=True), json.dumps(before, sort_keys=True))

    def test_results_hold_no_mutable_alias_of_the_input(self):
        recs = self.ex02()
        containers = set()
        stack = [recs]
        while stack:
            node = stack.pop()
            if isinstance(node, (dict, list)):
                containers.add(id(node))
                stack.extend(node.values() if isinstance(node, dict) else node)
        index = self.index(recs)
        claims = self.refs.collect_claims(index)
        results = [index, claims, self.binding.recompute_task(recs[0]), self.policy,
                   self.report(recs, 5), self.refs.link_grants(index, claims, 0),
                   self.binding.compare_peer_bindings(recs[2]['binding'], recs[5]['binding']),
                   self.binding.compare_object_sets(recs[2]['binding']['inputs'], recs[0]['inputs'], 'EXACT_QUALIFIED')]
        seen = []

        def walk(node):
            seen.append(id(node))
            if hasattr(node, '__dataclass_fields__'):
                for name in node.__dataclass_fields__:
                    walk(getattr(node, name))
            elif isinstance(node, (list, tuple)):
                for x in node:
                    walk(x)
            elif isinstance(node, dict):
                for x in node.values():
                    walk(x)
        for r in results:
            if hasattr(r, 'as_dict'):
                walk(r.as_dict())
            else:
                walk(r)
        self.assertFalse(containers & {i for i in seen}, 'a result shares a mutable container with the input')

    def test_no_value_echo_in_any_result(self):
        recs = self.ex02()
        text = json.dumps(recs)
        canaries = {'CANARYTASK1': 'EXAMPLE-task-1', 'CANARYREF1': 'EXAMPLE-grant-ref-1', 'CANARYPATH': 'references/EXAMPLE-quy-che.docx',
                    'CANARYGRANT': 'EXAMPLE-grant-1', 'CANARYLOC': 'EXAMPLE://user-store/grant-1', 'CANARYEFF': 'EXAMPLE-effect-1'}
        for new, old in canaries.items():
            text = text.replace(old, new)
        digest_canary = 'sha256:' + 'c' * 64
        recs = json.loads(text)
        self.of(recs, 'task')['inputs'][0]['digest'] = digest_canary
        results = json.dumps(self.all_results_dicts(recs))
        for new in list(canaries) + ['c' * 64, 'EXAMPLE-']:
            self.assertNotIn(new, results, new)
        # locator chỉ có chỉ số và tên trường đóng / locators hold only indexes and closed field names
        for rel in self.report(recs, 5).relations:
            self.assertRegex(rel.locator, r'^(records\[\d+\])?(\.[a-z_]+|\[\d+\])*$')

    def test_no_io_no_network_and_no_state_between_calls(self):
        recs = self.ex02()
        with mock.patch('builtins.open', side_effect=AssertionError('open called')), \
                mock.patch('io.open', side_effect=AssertionError('io.open called')), \
                mock.patch('socket.socket.connect', side_effect=AssertionError('network used')):
            first = json.dumps(self.all_results_dicts(recs), sort_keys=True)
            second = json.dumps(self.all_results_dicts(recs), sort_keys=True)
        self.assertEqual(first, second)

    def test_record_order_changes_positions_but_not_the_relation_set(self):
        recs = self.ex02()
        rev = list(reversed(copy.deepcopy(recs)))
        a = self.states(self.report(recs, 5))
        b = self.states(self.report(rev, 0))
        self.assertEqual(a, b)
        reversed_index = self.index(rev)
        self.assertEqual(self.refs.link_grants(reversed_index, self.refs.collect_claims(reversed_index), 0)[0].candidate_positions, (4,))

    def test_as_dict_is_json_safe_and_closed_vocabulary(self):
        for d in self.all_results_dicts(self.ex09()):
            json.dumps(d)

    def test_dataclasses_are_frozen(self):
        rep = self.report(self.ex02(), 5)
        with self.assertRaises(Exception):
            rep.recomputation_complete = False
        with self.assertRaises(Exception):
            rep.relations[0].state = 'MISMATCH'

    def test_s1_public_surface_unchanged(self):
        public = sorted(n for n in dir(self.entry) if not n.startswith('_') and callable(getattr(self.entry, n))
                        and getattr(getattr(self.entry, n), '__module__', None) == self.entry.__name__)
        self.assertEqual(public, ['check_bytes', 'exit_code', 'main'])
        res = self.entry.check_bytes(read_bytes(os.path.join(V2C, 'examples', 'ex02_mutation_reviewed_bound.json')), 'effect', 'v2')
        self.assertEqual(list(res), ['check_version', 'contract', 'selection', 'candidate_status', 'implementation_stage',
                                     'evaluation_basis', 'phase', 'disposition', 'effect_authorized', 'assurance_level',
                                     'init_error', 'reasons', 'details', 'owners', 'coverage', 'objects', 'gates'])
        self.assertIs(res['coverage']['binding_evaluated'], False)
        self.assertEqual(res['implementation_stage'], 'S1_FOUNDATION_ONLY')


if __name__ == '__main__':
    unittest.main()
