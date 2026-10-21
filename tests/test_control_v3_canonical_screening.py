"""G-02-C2: screening miền canonical theo projection (BINDING_ROUTING_ONLY) / projection-aware canonical screening.

Thay quét LAW-CJ/2 toàn bundle bằng `canon.bound_violations`: chỉ dữ liệu thật sự đi vào projection C1 hoặc khóa object của comparator.
Hai oracle độc lập với nhau và với hàm được kiểm: (1) bảng cặp mutation viết tay từ contract mục 7 và README v3 (trường bound/unbound,
locator kỳ vọng chính xác); (2) sweep từng lá của ví dụ, trong đó "bound" nghĩa là đổi lá sang giá trị TRONG miền làm đổi digest hoặc quan hệ
binding do builder/comparator thật tính, không phải kết quả của `bound_violations`. Không sửa fixtures, vectors, schema, policy.
Two independent oracles: a hand-written paired-mutation table and a per-leaf digest-sensitivity sweep. Nothing here edits fixtures, vectors, schema or policy.
"""
import copy
import importlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CVF = os.path.join(ROOT, '.cvf')
ENTRY = os.path.join(CVF, 'checks', 'control_check_v3.py')
V3C = os.path.join(CVF, 'contracts', 'v3')
V3R = os.path.join(CVF, 'rules', 'v3')
EX_DIR = os.path.join(V3C, 'examples')
NFD = 'é'  # hợp schema (chuỗi), không NFC / valid string, not NFC
SURROGATE = '\ud800'
BIG = 2 ** 60
MARKER = 'LEAK-MARKER-'
EX01 = 'ex01_pcn1_working_request.json'
EX02 = 'ex02_pcn1_output_internal_request.json'
EX04 = 'ex04_pcn1_accepted_d4_complete.json'
EX11 = 'ex11_pcn1_direct_runtime_write.json'
EX13 = 'ex13_pcn1_review_required_unsupported.json'
EX14 = 'ex14_pcn1_authority_named_target.json'
EX15 = 'ex15_pcn1_output_without_content_use.json'


def _read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _dumps(obj):
    return json.dumps(obj, ensure_ascii=True).encode('utf-8')


def _setat(bundle, path, value):
    out = copy.deepcopy(bundle)
    cur = out
    for part in path[:-1]:
        cur = cur[part]
    cur[path[-1]] = value
    return out


def _leaves(node, path=()):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _leaves(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from _leaves(v, path + (i,))
    elif isinstance(node, (str, int)) and not isinstance(node, bool):
        yield path, node


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('law_cvf_entry_v3_screening_test', ENTRY)
        cls.entry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.entry)
        cls.entry._load_package()
        name = cls.entry.PACKAGE_NAME + '.'
        cls.loader = importlib.import_module(name + 'loader')
        cls.canon = importlib.import_module(name + 'canon')
        cls.refs = importlib.import_module(name + 'refs')
        cls.binding = importlib.import_module(name + 'binding')
        cls.owners = cls.loader.load_owners()
        cls.pctx = cls.binding.make_policy_context(cls.owners.policy_bytes)
        cls.scratch = tempfile.mkdtemp(prefix='law-screening-')

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.scratch, ignore_errors=True)

    def bundle(self, name):
        return _read_json(os.path.join(EX_DIR, name))

    def check(self, bundle, phase='effect'):
        return self.entry.check_bytes(_dumps(bundle), phase, 'v3')

    def schema_ok(self, bundle):
        ok, _, _ = self.loader.validate_structure(bundle, self.owners)
        return ok

    def violations(self, bundle):
        return self.canon.bound_violations(self.refs.records_of(bundle))

    @staticmethod
    def apply(bundle, paths, value):
        for path in paths:
            bundle = _setat(bundle, path, value)
        return bundle

    def fingerprint(self, bundle):
        """Digest/quan hệ do builder và comparator thật tính (không dùng bound_violations)."""
        recs = self.refs.records_of(bundle)
        index = self.refs.build_index(recs)
        out = []
        for pos, rec in enumerate(recs):
            if rec.get('record_type') in ('review', 'effect', 'result') and isinstance(rec.get('binding'), dict):
                rep = self.binding.compare_binding(index, pos, self.pctx)
                relations = [(r.name, r.state, r.reason) for r in rep.relations]
                ua = rec.get('user_acceptance')
                if rec.get('record_type') == 'result' and isinstance(ua, dict):
                    # D4 comparison used by the one-file workflow: accepted_artifacts EXACT with result.artifacts (same keys as every object set)
                    d4 = self.binding.compare_object_sets(ua.get('accepted_artifacts'), rec.get('artifacts'), 'EXACT_QUALIFIED', name='D4-ARTIFACTS')
                    relations.append((d4.name, d4.state, d4.reason))
                out.append(tuple(relations))
            elif rec.get('record_type') == 'task':
                d = self.binding.recompute_task(rec)
                out.append((d.intent.digest, d.accepted_task.digest, d.context.digest, tuple(a.digest for a in d.actions)))
        return out


# Bảng viết tay. Mỗi dòng: nhãn, đường dẫn, danh sách giá trị ngoài miền; bound có thêm tập locator kỳ vọng chính xác.
# Hand-written table. Each bound row names the exact locator set the contract/README predict.
STRINGS = (NFD, SURROGATE)
UNBOUND = [
    ('task.note', [('records', 0, 'note')], STRINGS),
    ('task.intent.refs.locator', [('records', 0, 'intent', 'refs', 0, 'locator')], STRINGS),
    ('task.intent.refs.attribution.evidence_locator', [('records', 0, 'intent', 'refs', 0, 'attribution', 'evidence_locator')], STRINGS),
    # Shared ref_id: change both inline claims together; changing one still causes REF_CONFLICT.
    ('grant ref locator (both sites)', [('records', 0, 'authority', 'grant_refs', 0, 'locator'), ('records', 1, 'issuer_ref', 'locator')], STRINGS),
    ('grant.note', [('records', 1, 'note')], STRINGS),
    ('effect.receipt_ref.revision (single-site ref, not projected)', [('records', 3, 'receipt_ref', 'revision')], STRINGS),
    ('grant.grant_revision', [('records', 1, 'grant_revision')], (BIG,)),
    ('grant.limits.max_retries', [('records', 1, 'limits')], ({'max_retries': BIG}, {'max_retries': 2.0})),
    ('effect.note', [('records', 2, 'note')], STRINGS),
    ('effect.receipt_ref.locator', [('records', 3, 'receipt_ref', 'locator')], STRINGS),
    ('result.note', [('records', 4, 'note')], STRINGS),
    ('result.user_acceptance.ref.locator (attribution metadata, compared raw)', [('records', 4, 'user_acceptance', 'ref', 'locator')], STRINGS),
    ('result.user_acceptance.presented_summary.locator', [('records', 4, 'user_acceptance', 'presented_summary', 'locator')], STRINGS),
]
BOUND = [
    ('task.intent.main_interpretation', ('records', 0, 'intent', 'main_interpretation'), STRINGS, {'records[0].task'}),
    ('task.acceptance.statement', ('records', 0, 'acceptance', 'requirements', 0, 'statement'), STRINGS, {'records[0].task'}),
    ('task.actions.targets', ('records', 0, 'effects', 'actions', 0, 'targets', 0), STRINGS, {'records[0].task'}),
    ('task.inputs.path', ('records', 0, 'inputs', 0, 'path'), STRINGS, {'records[0].task'}),
    ('task.inputs.scope', ('records', 0, 'inputs', 0, 'scope'), STRINGS, {'records[0].task'}),
    ('task.task_revision', ('records', 0, 'task_revision'), (BIG, 2.0), {'records[0].task'}),
    ('task.intent.refs.revision (ref_proj)', ('records', 0, 'intent', 'refs', 0, 'revision'), STRINGS,
     {'records[0].intent', 'records[0].task'}),
    ('task.grant_refs.revision (ref_proj)', ('records', 0, 'authority', 'grant_refs', 0, 'revision'), STRINGS, {'records[0].task'}),
    ('task.context_refs.path', ('records', 0, 'context_refs'), ([{'path': NFD, 'digest': 'sha256:' + '0' * 64}],),
     {'records[0].context'}),
    ('effect.action.targets', ('records', 2, 'action', 'targets', 0), STRINGS, {'records[2].action'}),
    ('effect.binding.inputs.path', ('records', 2, 'binding', 'inputs', 0, 'path'), STRINGS, {'records[2].binding.inputs'}),
    ('effect.outcome.artifacts.path', ('records', 3, 'outcome', 'artifacts', 0, 'path'), STRINGS, {'records[3].artifacts'}),
    ('effect.binding.outputs.path', ('records', 3, 'binding', 'outputs', 0, 'path'), STRINGS, {'records[3].binding.outputs'}),
    ('result.artifacts.path', ('records', 4, 'artifacts', 0, 'path'), STRINGS, {'records[4].artifacts'}),
    ('result.binding.outputs.path', ('records', 4, 'binding', 'outputs', 0, 'path'), STRINGS, {'records[4].binding.outputs'}),
    ('result.user_acceptance.accepted_artifacts.path (D4 comparator)', ('records', 4, 'user_acceptance', 'accepted_artifacts', 0, 'path'), STRINGS,
     {'records[4].user_acceptance.accepted_artifacts'}),
]


class PairedMutations(Base):
    def test_unbound_metadata_outside_the_domain_changes_nothing(self):
        base_bundle = self.bundle(EX04)
        base = {phase: self.check(base_bundle, phase) for phase in ('dispatch', 'effect', 'accept')}
        base_fp = self.fingerprint(base_bundle)
        for label, paths, values in UNBOUND:
            for value in values:
                with self.subTest(label=label, value=type(value).__name__):
                    mutated = self.apply(base_bundle, paths, value)
                    self.assertTrue(self.schema_ok(mutated), 'the case must stay schema-valid or it proves nothing')
                    self.assertEqual(self.violations(mutated), [])
                    self.assertEqual(self.fingerprint(mutated), base_fp, 'unbound data must not change any digest or relation')
                    for phase, want in base.items():
                        self.assertEqual(self.check(mutated, phase), want)

    def test_old_pure_scan_still_flags_the_same_values(self):
        # API canonical thuần không đổi: cùng giá trị vẫn là vi phạm miền LAW-CJ/2 khi quét như một giá trị bất kỳ.
        base_bundle = self.bundle(EX04)
        for label, paths, values in UNBOUND:
            for value in values:
                with self.subTest(label=label):
                    self.assertTrue(self.canon.domain_violations(self.apply(base_bundle, paths, value)))

    def test_same_defect_in_a_bound_part_is_rejected_at_the_expected_parts(self):
        base_bundle = self.bundle(EX04)
        for label, path, values, parts in BOUND:
            for value in values:
                with self.subTest(label=label, value=type(value).__name__):
                    mutated = _setat(base_bundle, path, value)
                    self.assertTrue(self.schema_ok(mutated), 'the case must stay schema-valid or it proves nothing')
                    self.assertEqual({loc for loc, _ in self.violations(mutated)}, parts)
                    res = self.check(mutated)
                    self.assertEqual((res['disposition'], res['reasons']), ('UNSUPPORTED', ['UNSUPPORTED_BINDING_PART']))
                    self.assertIsNone(res['phase_scope'])
                    self.assertIs(res['coverage']['record_structure_checked'], False)
                    self.assertIs(res['coverage']['binding_evaluated'], False)
                    self.assertIs(res['coverage']['routing_evaluated'], False)
                    self.assertEqual(res['route'], {'evaluated': False, 'rows': [], 'status': None, 'assumptions': []})
                    self.assertIs(res['effect_authorized'], False)

    def test_bound_rejection_names_parts_and_counts_but_never_the_value(self):
        base_bundle = self.bundle(EX04)
        mutated = _setat(base_bundle, ('records', 0, 'intent', 'main_interpretation'), MARKER + NFD)
        res = self.check(mutated)
        text = json.dumps(res)
        self.assertNotIn('LEAK', text)
        self.assertTrue(any('bound projection parts (task)' in d and 'NON_NFC_STRING x1' in d for d in res['details']), res['details'])
        mutated = _setat(base_bundle, ('records', 4, 'artifacts', 0, 'path'), MARKER + SURROGATE)
        res = self.check(mutated)
        self.assertNotIn('LEAK', json.dumps(res))
        self.assertTrue(any('LONE_SURROGATE x1' in d and 'artifacts' in d for d in res['details']), res['details'])

    def test_one_paired_value_unbound_accepted_bound_rejected(self):
        # Cùng giá trị NFD, cùng loại trường ref: `locator` (bị loại) được nhận, `revision` vào ref_proj thì bị từ chối.
        b = self.bundle(EX04)
        self.assertEqual(self.violations(_setat(b, ('records', 0, 'intent', 'refs', 0, 'locator'), NFD)), [])
        self.assertEqual(self.violations(_setat(b, ('records', 0, 'intent', 'refs', 0, 'revision'), NFD)),
                         [('records[0].intent', 'NON_NFC_STRING'), ('records[0].task', 'NON_NFC_STRING')])

    def test_a_ref_field_outside_the_projection_is_still_compared_raw_by_the_claim_groups(self):
        # Không phải screening: nhóm lời khai inline so các trường ref thô giữa các vị trí; đổi một nơi là xung đột, không bị coi là bound.
        b = _setat(self.bundle(EX04), ('records', 1, 'issuer_ref', 'locator'), NFD)
        self.assertEqual(self.violations(b), [])
        res = self.check(b)
        self.assertEqual(res['disposition'], 'BLOCKED')
        self.assertIn('REF_CONFLICT', res['reasons'])
        self.assertNotIn('UNSUPPORTED_BINDING_PART', res['reasons'])


class LeafSweep(Base):
    """Oracle độc lập: một lá là bound khi đổi nó sang giá trị trong miền làm đổi digest/quan hệ do builder và comparator thật tính."""

    EXAMPLES = (EX01, EX02, EX04, EX11)

    def test_screening_matches_digest_sensitivity_on_every_leaf(self):
        bound = unbound = 0
        for name in self.EXAMPLES:
            bundle = self.bundle(name)
            base = self.fingerprint(bundle)
            for path, value in list(_leaves(bundle)):
                if len(path) >= 3 and path[-1] == 'task_revision' and path[-2] == 'binding':
                    continue  # khóa tra cứu task, kiểm riêng ở LookupKey
                inside, outside = ((value + 'x', value + NFD) if isinstance(value, str) else (value + 1, BIG))
                a, b = _setat(bundle, path, inside), _setat(bundle, path, outside)
                if not (self.schema_ok(a) and self.schema_ok(b)):
                    continue  # const/pattern/enum: không thể mang giá trị ngoài miền
                is_bound = self.fingerprint(a) != base
                bound += is_bound
                unbound += not is_bound
                with self.subTest(example=name[:4], path='/'.join(str(p) for p in path), bound=is_bound):
                    self.assertEqual(bool(self.violations(b)), is_bound)
        self.assertGreaterEqual(bound, 40, 'the sweep must exercise bound leaves')
        self.assertGreaterEqual(unbound, 40, 'the sweep must exercise unbound leaves')


class LookupKey(Base):
    """Khóa tra cứu (`binding.task_revision`, `grant_revision`) so thô, không canonicalize: không thuộc screening, nhưng không crash hay lọt thành PASS."""

    def test_non_integer_grant_revision_is_an_index_problem_not_a_screening_one(self):
        m = _setat(self.bundle(EX04), ('records', 1, 'grant_revision'), 2.0)
        self.assertTrue(self.schema_ok(m))
        self.assertEqual(self.violations(m), [])
        res = self.check(m)
        self.assertIn('GRANT_MISSING', res['reasons'])
        self.assertNotIn(res['disposition'], ('PASS', 'NOT_APPLICABLE'))

    def test_out_of_domain_lookup_key_is_not_screened_and_never_passes(self):
        b = self.bundle(EX04)
        for value, want in ((BIG, 'BINDING_INCOMPLETE'), (2.0, 'UNSUPPORTED_BINDING_PART')):
            with self.subTest(value=repr(value)):
                m = _setat(b, ('records', 2, 'binding', 'task_revision'), value)
                self.assertTrue(self.schema_ok(m))
                self.assertEqual(self.violations(m), [])
                res = self.check(m)
                self.assertIn(want, res['reasons'])
                self.assertNotIn(res['disposition'], ('PASS', 'NOT_APPLICABLE'))
                self.assertIs(res['effect_authorized'], False)


class IndependentSetValidity(Base):
    def test_standalone_task_sets_are_checked_without_binding_coverage(self):
        base = self.bundle(EX04)['records'][0]
        mutations = (
            (('inputs',), base['inputs'] * 2),
            (('intent', 'refs'), base['intent']['refs'] * 2),
            (('context_refs',), [copy.deepcopy(base['inputs'][0])] * 2),
            (('effects', 'actions', 0, 'targets'), base['effects']['actions'][0]['targets'] * 2),
        )
        for path, value in mutations:
            with self.subTest(path=path):
                task = _setat(base, path, value)
                self.assertTrue(self.schema_ok(task))
                self.assertEqual(self.violations(task), [], 'duplicate is a builder error, not domain screening')
                res = self.check(task)
                self.assertEqual(res['disposition'], 'UNSUPPORTED')
                self.assertIn('UNSUPPORTED_BINDING_PART', res['reasons'])
                self.assertIs(res['coverage']['binding_evaluated'], False)

    def test_duplicate_task_set_does_not_hide_known_loss(self):
        task = self.bundle(EX04)['records'][0]
        task['inputs'] *= 2
        task['effects']['preservation'] = [{'target': task['effects']['actions'][0]['targets'][0],
                                            'must_keep': 'source bytes', 'known_loss_state': 'KNOWN_LOSS'}]
        self.assertTrue(self.schema_ok(task))
        res = self.check(task)
        self.assertEqual(res['disposition'], 'DENY')
        self.assertTrue({'KNOWN_PRESERVATION_LOSS', 'UNSUPPORTED_BINDING_PART'}.issubset(res['reasons']))
        self.assertIs(res['coverage']['binding_evaluated'], False)

    def orphan_records(self):
        records = self.bundle(EX04)['records']
        eligibility = copy.deepcopy(records[0]['intent']['refs'][0])
        eligibility['kind'] = 'reviewer_eligibility'
        review = {k: records[0][k] for k in ('schema_version', 'evaluation_basis')}
        review.update(record_type='review', review_id='review-orphan', phase='PRE_DELIVERY',
                      binding=copy.deepcopy(records[2]['binding']),
                      reviewer={'actor': {'actor_id': 'independent', 'role': 'reviewer'},
                                'eligibility_ref': eligibility, 'independence_observed': 'NOT_OBSERVED'},
                      scope={'objects': [], 'requirements_checked': [], 'not_checked': []}, verdict='UNKNOWN', findings=[])
        return [copy.deepcopy(records[2]), copy.deepcopy(records[3]), copy.deepcopy(records[4]), review]

    def test_orphan_input_sets_keep_unsupported_and_missing_counterpart(self):
        for rec in self.orphan_records():
            with self.subTest(record_type=rec['record_type'], stage=rec.get('stage')):
                rec['binding']['inputs'] *= 2
                self.assertTrue(self.schema_ok(rec))
                self.assertEqual(self.violations(rec), [])
                res = self.check(rec)
                self.assertEqual(res['disposition'], 'UNSUPPORTED')
                self.assertTrue({'UNSUPPORTED_BINDING_PART', 'BINDING_INCOMPLETE'}.issubset(res['reasons']))
                self.assertIs(res['coverage']['binding_evaluated'], False)

    def test_orphan_bound_domain_is_screened_but_unbound_metadata_is_not(self):
        for rec in self.orphan_records():
            with self.subTest(record_type=rec['record_type'], stage=rec.get('stage')):
                metadata = copy.deepcopy(rec)
                metadata['note'] = NFD + SURROGATE
                self.assertEqual(self.check(metadata), self.check(rec))
                rec['binding']['inputs'][0]['path'] = NFD
                self.assertTrue(self.schema_ok(rec))
                self.assertIn(('records[0].binding.inputs', 'NON_NFC_STRING'), self.violations(rec))
                res = self.check(rec)
                self.assertEqual(res['disposition'], 'UNSUPPORTED')
                self.assertIs(res['coverage']['binding_evaluated'], False)


class UnchangedBehaviour(Base):
    def test_every_valid_example_still_screens_clean(self):
        for name in sorted(os.listdir(EX_DIR)):
            if not (name.startswith('ex') and name.endswith('.json')):
                continue
            bundle = self.bundle(name)
            if self.schema_ok(bundle) and bundle.get('schema_version') == 'law.cvf.control/3':
                with self.subTest(name=name):
                    self.assertEqual(self.violations(bundle), [])

    def test_duplicate_set_is_not_a_domain_violation_and_is_never_deduplicated(self):
        b = self.bundle(EX04)
        task = b['records'][0]
        task['inputs'] = task['inputs'] * 2
        self.assertEqual(self.violations(b), [])
        with self.assertRaises(self.canon.Unsupported) as cm:
            self.canon.task_part(task)
        self.assertEqual(cm.exception.reason, 'DUPLICATE_SET_ELEMENT')
        rel = self.binding.compare_object_sets(task['inputs'], task['inputs'], 'EXACT_QUALIFIED', name='B-INPUTS')
        self.assertEqual((rel.state, rel.reason), ('UNSUPPORTED', 'DUPLICATE_SET_ELEMENT'))
        res = self.check(b)
        self.assertEqual(res['disposition'], 'UNSUPPORTED')
        self.assertIn('UNSUPPORTED_BINDING_PART', res['reasons'])
        self.assertIs(res['coverage']['routing_evaluated'], True, 'the duplicate is reported by the comparator, after screening')

    def test_policy_projection_is_still_the_whole_policy_object(self):
        with open(os.path.join(V3R, 'ROUTING_POLICY.json'), 'rb') as f:
            raw = f.read()
        vectors = _read_json(os.path.join(V3C, 'vectors.json'))
        self.assertEqual(self.binding.make_policy_context(raw).digest, vectors['policy_digest']['digest'])
        obj = json.loads(raw.decode('utf-8'))
        obj['note'] = obj['note'] + 'x'  # trường metadata của policy vẫn đổi policy_digest
        changed = self.binding.make_policy_context(json.dumps(obj).encode('utf-8'))
        self.assertEqual(changed.state, 'COMPUTED')
        self.assertNotEqual(changed.digest, vectors['policy_digest']['digest'])
        obj['note'] = obj['note'] + NFD  # và ngoài miền ở bất kỳ trường nào của policy thì UNSUPPORTED
        bad = self.binding.make_policy_context(json.dumps(obj).encode('utf-8'))
        self.assertEqual((bad.state, bad.reason), ('UNSUPPORTED', 'NON_NFC_STRING'))

    def test_input_guards_are_unchanged(self):
        # The loader translates a decoder RecursionError; it specifies no fixed depth limit.
        # Inject at the decoder boundary so Python/OS recursion thresholds do not define the oracle.
        with mock.patch.object(self.loader.json, 'loads', side_effect=RecursionError('simulated decoder limit')) as decode:
            res = self.entry.check_bytes(b'{"a":[]}', 'effect', 'v3')
        decode.assert_called_once()
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['INPUT_MALFORMED']))
        nested = _setat(self.bundle(EX04), ('records', 0, 'note'), [[[[['deep']]]]])
        res = self.check(nested)
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['SCHEMA_INVALID']), 'metadata still passes the schema')
        res = self.entry.check_bytes(b' ' * (8 * 1024 * 1024 + 1), 'effect', 'v3')
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['INPUT_MALFORMED']))
        res = self.entry.check_bytes(b'{"a":1,"a":2}', 'effect', 'v3')
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['INPUT_MALFORMED']))
        res = self.entry.check_bytes(b'{"a":NaN}', 'effect', 'v3')
        self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['INPUT_MALFORMED']))

    def test_metadata_still_obeys_the_schema(self):
        for path, value in ((('records', 0, 'note'), 5), (('records', 0, 'proposed_by', 'role'), 'not-a-role'),
                            (('records', 1, 'issuer_ref', 'locator'), 5)):
            with self.subTest(path=path):
                res = self.check(_setat(self.bundle(EX04), path, value))
                self.assertEqual((res['disposition'], res['reasons']), ('DENY', ['SCHEMA_INVALID']))

    def test_route_obligations_survive_unbound_metadata_changes(self):
        for name in (EX01, EX02, EX11, EX13, EX14, EX15):
            bundle = self.bundle(name)
            for phase in ('dispatch', 'effect', 'accept'):
                with self.subTest(example=name[:4], phase=phase):
                    base = self.check(bundle, phase)
                    mutated = self.check(_setat(bundle, ('records', 0, 'note'), NFD + SURROGATE), phase)
                    self.assertEqual(mutated, base)
                    self.assertNotIn(mutated['disposition'], ('PASS', 'NOT_APPLICABLE'))
                    self.assertIs(mutated['coverage']['gates_evaluated'], False)

    def test_cli_with_lone_surrogate_in_unbound_metadata_does_not_crash_or_leak(self):
        b = _setat(self.bundle(EX04), ('records', 0, 'note'), MARKER + SURROGATE)
        path = os.path.join(self.scratch, 'surrogate.json')
        with open(path, 'wb') as f:
            f.write(_dumps(b))
        for extra in ([], ['--format', 'text']):
            proc = subprocess.run([sys.executable, '-B', '-I', ENTRY, '--contract', 'v3', '--phase', 'accept'] + extra + [path],
                                  cwd=self.scratch, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual((proc.returncode, proc.stderr), (1, b''))
            self.assertNotIn(b'LEAK', proc.stdout)
            self.assertIn(b'BLOCKED' if extra else b'"BLOCKED"', proc.stdout)


if __name__ == '__main__':
    unittest.main()
