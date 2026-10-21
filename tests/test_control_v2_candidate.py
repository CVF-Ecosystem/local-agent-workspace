"""G-01-C1: kiểm candidate contract v2 (schema, policy, ví dụ giả, vectors) / candidate v2 contract checks.

Chỉ kiểm cấu trúc và định nghĩa binding. Không chạy workflow, không dùng checker G-02 (checker v1 không đọc v2),
không cấp quyền. Hàm tham chiếu law.cvf.bind/2 ở đây để tính lại vectors và binding trong ví dụ; nó không phải loader/checker.
Structure and binding-definition checks only: no workflow run, no G-02 checker, no authority.
The reference functions below recompute the vectors and the example bindings; they are not a loader or a checker.
"""
import copy
import hashlib
import json
import os
import re
import unicodedata
import unittest

try:
    import jsonschema
    HAVE_JSONSCHEMA = True
except ImportError:  # báo lỗi rõ ở setUpModule, không bỏ qua im lặng / fail loudly, never skip silently
    HAVE_JSONSCHEMA = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CVF = os.path.join(ROOT, '.cvf')
V2C = os.path.join(CVF, 'contracts', 'v2')
V2R = os.path.join(CVF, 'rules', 'v2')

BV = 'law.cvf.bind/2'
MAX_INT = 2 ** 53 - 1
KEY_RE = re.compile(r'^[A-Za-z0-9_.-]{1,64}$')

# hash 16 ký tự đầu của owner v1 phải không đổi / v1 owners must stay byte-identical
V1_PINS = {
    'contracts/control.schema.json': '933265fa7b113941',
    'contracts/CONTROL_CONTRACT.md': 'd22848dee934d4cf',
    'contracts/examples/EXPECTED.json': 'c72e1e6b2bfda8ff',
    'rules/ROUTING_POLICY.json': '8db011baf5d5c5a0',
    'rules/CONTROL_RULES.md': 'ad3337b9baee23e4',
    'checks/control_check.py': 'f95bfc367bb7f470',
}


class Unsupported(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# ---------------------------------------------------------------- LAW-CJ/2 canonical JSON
def parse_strict(text):
    def pairs(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            raise Unsupported('DUPLICATE_KEY')
        return dict(items)

    def bad_float(_):
        raise Unsupported('NON_INTEGER_NUMBER')

    def bad_const(_):
        raise Unsupported('NON_FINITE_NUMBER')
    return json.loads(text, object_pairs_hook=pairs, parse_float=bad_float, parse_constant=bad_const)


def _esc(s):
    if unicodedata.normalize('NFC', s) != s:
        raise Unsupported('NON_NFC_STRING')
    out = ['"']
    short = {'"': '\\"', '\\': '\\\\', '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', '\r': '\\r'}
    for ch in s:
        if ch in short:
            out.append(short[ch])
        elif ord(ch) < 0x20:
            out.append('\\u%04x' % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    text = ''.join(out)
    try:
        text.encode('utf-8')
    except UnicodeEncodeError:
        raise Unsupported('LONE_SURROGATE')
    return text


def _enc(v):
    if v is None:
        return 'null'
    if v is True:
        return 'true'
    if v is False:
        return 'false'
    if isinstance(v, int):
        if abs(v) > MAX_INT:
            raise Unsupported('INTEGER_OUT_OF_RANGE')
        return str(v)
    if isinstance(v, float):
        raise Unsupported('NON_INTEGER_NUMBER')
    if isinstance(v, str):
        return _esc(v)
    if isinstance(v, list):
        return '[' + ','.join(_enc(x) for x in v) + ']'
    if isinstance(v, dict):
        for k in v:
            if not isinstance(k, str) or not KEY_RE.fullmatch(k):
                raise Unsupported('KEY_NOT_ALLOWED')
        return '{' + ','.join(_esc(k) + ':' + _enc(v[k]) for k in sorted(v, key=lambda x: x.encode('utf-8'))) + '}'
    raise Unsupported('TYPE_NOT_ALLOWED')


def canonical_text(v):
    return _enc(v)


def canonical_bytes(v):
    return _enc(v).encode('utf-8')


def digest_of(v):
    return 'sha256:' + hashlib.sha256(canonical_bytes(v)).hexdigest()


def bytes_digest(b):
    return 'sha256:' + hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- projections
def sorted_set(items):
    pairs = sorted(((canonical_bytes(i), i) for i in items), key=lambda p: p[0])
    for a, b in zip(pairs, pairs[1:]):
        if a[0] == b[0]:
            raise Unsupported('DUPLICATE_SET_ELEMENT')
    return [i for _, i in pairs]


def ref_proj(r):
    d = {'digest': r['digest'], 'kind': r['kind']}
    if 'revision' in r:
        d['revision'] = r['revision']
    return d


def obj_proj(o):
    return {k: o[k] for k in ('path', 'digest', 'source_id', 'revision', 'scope') if k in o}


def action_proj(a):
    a = copy.deepcopy(a)
    a['targets'] = sorted_set(a['targets'])
    if 'content_use' in a:
        a['content_use'] = sorted_set(a['content_use'])
    if 'payload' in a:
        a['payload'] = obj_proj(a['payload'])
    if 'recipe' in a:
        a['recipe']['acceptance_ref'] = ref_proj(a['recipe']['acceptance_ref'])
    if 'delegation' in a:
        d = a['delegation']
        d.pop('parent_task', None)  # tự tham chiếu task chứa nó / self-reference to the containing task: checked separately
        if 'identity_ref' in d['callee']:
            d['callee']['identity_ref'] = ref_proj(d['callee']['identity_ref'])
        ts = d['tool_scope']
        for k in ('tools', 'operations', 'paths'):
            ts[k] = sorted_set(ts[k])
    return a


def intent_part(task):
    return {'bind': BV, 'part': 'intent', 'refs': sorted_set([ref_proj(r) for r in task['intent']['refs']])}


def context_part(task):
    return {'bind': BV, 'part': 'context', 'context_refs': sorted_set([obj_proj(o) for o in task.get('context_refs', [])])}


def action_part(a):
    return {'bind': BV, 'part': 'action', 'action': action_proj(a)}


def policy_part(policy):
    return {'bind': BV, 'part': 'policy', 'policy': policy}


def task_part(task):
    eff = task['effects']
    e = {'actions': [action_proj(a) for a in eff['actions']], 'on_missing': eff['on_missing']}
    if 'protected_targets' in eff:
        e['protected_targets'] = sorted_set(eff['protected_targets'])
    if 'preservation' in eff:
        e['preservation'] = eff['preservation']
    if 'expected_outputs' in eff:
        e['expected_outputs'] = sorted_set(eff['expected_outputs'])
    p = {
        'bind': BV, 'part': 'task',
        'schema_version': task['schema_version'], 'evaluation_basis': task['evaluation_basis'],
        'work_id': task['work_id'], 'task_id': task['task_id'], 'task_revision': task['task_revision'],
        'intent_digest': digest_of(intent_part(task)),
        'main_interpretation': task['intent']['main_interpretation'],
        'subject': {'actor_id': task['authority']['subject']['actor_id'], 'role': task['authority']['subject']['role']},
        'grant_refs': sorted_set([ref_proj(r) for r in task['authority']['grant_refs']]),
        'inputs': sorted_set([obj_proj(o) for o in task['inputs']]),
        'effects': e, 'acceptance': task['acceptance'], 'envelope': task['envelope'],
    }
    if 'unconfirmed' in task['intent']:
        p['unconfirmed'] = task['intent']['unconfirmed']
    return p


def binding_digests(task, policy):
    return {
        'intent_digest': digest_of(intent_part(task)),
        'accepted_task_digest': digest_of(task_part(task)),
        'context_digest': digest_of(context_part(task)),
        'policy_digest': digest_of(policy_part(policy)),
    }


# ---------------------------------------------------------------- helpers
def read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def read_text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def sha16(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def schema_validator(schema):
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def setUpModule():
    if not HAVE_JSONSCHEMA:
        raise RuntimeError('jsonschema>=4.18 không có / not installed: BLOCKED, không tự cài / not auto-installed')


class CandidateBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = read_json(os.path.join(V2C, 'control.schema.json'))
        cls.policy = read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))
        cls.expected = read_json(os.path.join(V2C, 'examples', 'EXPECTED.json'))
        cls.vectors = read_json(os.path.join(V2C, 'vectors.json'))
        cls.validator = schema_validator(cls.schema)

    def example(self, name):
        return read_json(os.path.join(V2C, 'examples', name))


class V1Untouched(unittest.TestCase):
    def test_v1_owner_hashes_unchanged(self):
        for rel, want in V1_PINS.items():
            self.assertEqual(sha16(os.path.join(CVF, *rel.split('/'))), want, rel)

    def test_checker_does_not_discover_v2(self):
        src = read_text(os.path.join(CVF, 'checks', 'control_check.py'))
        self.assertNotIn('contracts/v2', src)
        self.assertNotIn('rules/v2', src)
        self.assertNotIn('control/2', src)


class SchemaAndPolicy(CandidateBase):
    def test_schema_is_valid_draft_2020_12(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_literals(self):
        self.assertEqual(self.schema['$id'], 'urn:law:cvf:control:2')
        d = self.schema['$defs']
        self.assertEqual(d['schema_version']['const'], 'law.cvf.control/2')
        self.assertEqual(d['policy_version']['const'], 'law.cvf.routing/2')
        self.assertEqual(d['evaluation_basis']['const'], 'COOPERATIVE_WORKFLOW')
        self.assertEqual(d['bind_version']['const'], BV)
        self.assertEqual(d['effect']['properties']['assurance_level']['enum'], ['UNVERIFIED', 'ADVISORY'])

    def test_no_self_verifiable_trust_fields(self):
        raw = json.dumps(self.schema)
        for word in ('trust_anchor', 'trusted_ref', '"verification"', 'ENFORCED_FOR_NAMED_ACTIONS', 'TRUSTED_VERIFIED'):
            self.assertNotIn(word, raw)

    def test_policy_valid_and_candidate(self):
        self.assertEqual(list(self.validator.iter_errors(self.policy)), [])
        self.assertEqual(self.policy['status'], 'CANDIDATE_NOT_ACTIVE')
        for k, v in (('assurance_ceiling', 'ADVISORY'), ('tamper_resistance', 'NONE'), ('basis_change_per_run', 'FORBIDDEN'),
                     ('legacy_and_unknown_handling', 'REFUSE_NO_AUTO_MIGRATION'), ('main_may_downgrade', False),
                     ('review_grants_authority', False), ('unknown_handling', 'NEVER_ALLOW')):
            self.assertEqual(self.policy[k], v)

    def test_rows_equal_v1_except_authority_fields(self):
        v1 = read_json(os.path.join(CVF, 'rules', 'ROUTING_POLICY.json'))
        self.assertEqual([r['row_id'] for r in v1['rows']], [r['row_id'] for r in self.policy['rows']])
        keep = ('row_id', 'title', 'match_any', 'required_gates', 'required_review_phases', 'forced_disposition', 'additional_owner')
        for a, b in zip(v1['rows'], self.policy['rows']):
            self.assertEqual({k: a.get(k) for k in keep}, {k: b.get(k) for k in keep}, a['row_id'])
        for k in ('combine', 'missing_required_reviewer', 'reviewer_dispatch_needs_review', 'unresolved_condition',
                  'unmatched_effect_route', 'group_grant_reuse', 'match_semantics'):
            self.assertEqual(v1[k], self.policy[k], k)

    def test_user_confirmed_grant_where_v1_needed_a_grant_and_no_row_accepts_main_or_unverified(self):
        v1 = {r['row_id']: r for r in read_json(os.path.join(CVF, 'rules', 'ROUTING_POLICY.json'))['rows']}
        for r in self.policy['rows']:
            need = {x['kind']: x['accepted_source_classes'] for x in r['attributed_refs_required']}
            self.assertEqual('grant' in need, 'grant' in v1[r['row_id']]['trusted_refs_required'] or r['row_id'] == 'R-READ_DRAFT', r['row_id'])
            self.assertEqual(sorted(need), sorted(v1[r['row_id']]['trusted_refs_required']) if r['row_id'] != 'R-READ_DRAFT' else ['grant'], r['row_id'])
            if 'grant' in need:
                self.assertEqual(need['grant'], ['USER_CONFIRMATION'], r['row_id'])
            for classes in need.values():
                self.assertFalse(set(classes) & {'MAIN_PROPOSAL', 'UNVERIFIED', 'ROLE_REPORT'}, r['row_id'])
            if 'user_intent' in need:
                self.assertEqual(need['user_intent'], ['USER_CONFIRMATION'], r['row_id'])


class Examples(CandidateBase):
    def test_expected_covers_every_file(self):
        files = sorted(f for f in os.listdir(os.path.join(V2C, 'examples')) if f.startswith('ex') and f.endswith('.json'))
        self.assertEqual(files, sorted(c['file'] for c in self.expected['cases']))
        self.assertTrue(self.expected['example_only'])
        self.assertEqual(self.expected['workflow_status'], 'NOT_RUN')

    def test_schema_validity_matches_expected(self):
        for c in self.expected['cases']:
            errs = list(self.validator.iter_errors(self.example(c['file'])))
            self.assertEqual(not errs, c['schema_valid'], '%s: %s' % (c['file'], errs[:1]))
            self.assertFalse(c['workflow_tested'], c['file'])

    def test_examples_are_fake_and_inactive(self):
        for c in self.expected['cases']:
            raw = read_text(os.path.join(V2C, 'examples', c['file']))
            self.assertIn('"example_only": true', raw)
            self.assertNotIn('"status": "ACTIVE"', raw)
            self.assertNotIn('"disposition": "PASS"', raw)

    def test_binding_recomputation_matches_expectation(self):
        for c in self.expected['cases']:
            if not c['schema_valid']:
                continue
            bundle = self.example(c['file'])
            tasks = [r for r in bundle['records'] if r['record_type'] == 'task']
            if not tasks:
                continue
            task = tasks[0]
            want = binding_digests(task, self.policy)
            bad = []
            for r in bundle['records']:
                b = r.get('binding')
                if not b:
                    continue
                for k, v in want.items():
                    if b.get(k) != v:
                        bad.append((r['record_type'], k))
            self.assertEqual(bool(bad), c['binding_stale_or_mismatched'], '%s %s' % (c['file'], bad))

    def test_attribution_classes_in_examples_are_claims_only(self):
        for c in self.expected['cases']:
            if not c['schema_valid']:
                continue
            raw = read_text(os.path.join(V2C, 'examples', c['file']))
            self.assertNotIn('trust_anchor', raw)
            self.assertNotIn('"verification"', raw)


class Mutations(CandidateBase):
    def bundle(self):
        return copy.deepcopy(self.example('ex02_mutation_reviewed_bound.json'))

    def rejects(self, mutate, label):
        b = self.bundle()
        mutate(b)
        self.assertTrue(list(self.validator.iter_errors(b)), label)

    def test_baseline_valid(self):
        self.assertEqual(list(self.validator.iter_errors(self.bundle())), [])

    def test_mutations_are_rejected(self):
        def first(b, rt): return next(r for r in b['records'] if r['record_type'] == rt)
        def task(b): return first(b, 'task')
        def review(b): return first(b, 'review')
        def effect(b): return first(b, 'effect')
        cases = {
            'schema_version v1': lambda b: task(b).__setitem__('schema_version', 'law.cvf.control/1'),
            'schema_version v3': lambda b: task(b).__setitem__('schema_version', 'law.cvf.control/3'),
            'basis missing': lambda b: task(b).pop('evaluation_basis'),
            'basis unknown': lambda b: task(b).__setitem__('evaluation_basis', 'TRUSTED_ENFORCED'),
            'binding bind_version missing': lambda b: review(b)['binding'].pop('bind_version'),
            'binding policy_version v1': lambda b: review(b)['binding'].__setitem__('policy_version', 'law.cvf.routing/1'),
            'binding policy_digest missing': lambda b: review(b)['binding'].pop('policy_digest'),
            'binding basis other': lambda b: review(b)['binding'].__setitem__('evaluation_basis', 'OTHER'),
            'trust_anchor field': lambda b: task(b)['intent']['refs'][0].__setitem__('trust_anchor', 'MAIN_DECLARED'),
            'verification field': lambda b: task(b)['intent']['refs'][0].__setitem__('verification', {'status': 'VERIFIED'}),
            'enforced assurance': lambda b: effect(b).__setitem__('assurance_level', 'ENFORCED_FOR_NAMED_ACTIONS'),
            'main authored user confirmation': lambda b: task(b)['intent']['refs'][0]['attribution'].__setitem__('channel', 'MAIN_AUTHORED'),
            'user confirmation without locator': lambda b: task(b)['intent']['refs'][0]['attribution'].pop('evidence_locator'),
            'tool observation by main': lambda b: review(b)['reviewer']['eligibility_ref']['attribution'].__setitem__('observed_by', {'actor_id': 'EXAMPLE-main', 'role': 'main'}),
            'attribution missing': lambda b: task(b)['intent']['refs'][0].pop('attribution'),
            'unknown source class': lambda b: task(b)['intent']['refs'][0]['attribution'].__setitem__('source_class', 'VERIFIED'),
            'reason from v1 only': lambda b: effect(b).__setitem__('reasons', ['TRUSTED_VERIFICATION_UNAVAILABLE']),
            'pass without objects': lambda b: review(b)['scope'].__setitem__('objects', []),
        }
        for label, m in cases.items():
            with self.subTest(label):
                self.rejects(m, label)

    def test_policy_mutations_are_rejected(self):
        def bad(mut):
            p = copy.deepcopy(self.policy)
            mut(p)
            return list(self.validator.iter_errors(p))
        cases = {
            'active enforced status': lambda p: p.__setitem__('status', 'ACTIVE_ENFORCED_FOR_NAMED_ACTIONS'),
            'ceiling raised': lambda p: p.__setitem__('assurance_ceiling', 'ENFORCED_FOR_NAMED_ACTIONS'),
            'tamper claim': lambda p: p.__setitem__('tamper_resistance', 'PARTIAL'),
            'basis per run': lambda p: p.__setitem__('basis_change_per_run', 'ALLOWED'),
            'v1 version': lambda p: p.__setitem__('policy_version', 'law.cvf.routing/1'),
            'row without refs': lambda p: p['rows'][0].pop('attributed_refs_required'),
            'row v1 field': lambda p: p['rows'][0].__setitem__('trusted_refs_required', ['grant']),
            'empty classes': lambda p: p['rows'][0]['attributed_refs_required'][0].__setitem__('accepted_source_classes', []),
            'main may downgrade': lambda p: p.__setitem__('main_may_downgrade', True),
        }
        for label, m in cases.items():
            with self.subTest(label):
                self.assertTrue(bad(m), label)


class Vectors(CandidateBase):
    def test_canonical_vectors_recomputed(self):
        for v in self.vectors['canonical']:
            with self.subTest(v['id']):
                exp = v['expected']
                if exp['status'] == 'UNSUPPORTED':
                    with self.assertRaises(Unsupported) as cm:
                        canonical_bytes(parse_strict(v['input_json']))
                    self.assertEqual(cm.exception.reason, exp['reason'])
                else:
                    value = parse_strict(v['input_json'])
                    self.assertEqual(canonical_text(value), exp['canonical_utf8'])
                    self.assertEqual(digest_of(value), exp['digest'])

    def test_object_bytes_vectors(self):
        for v in self.vectors['object_bytes']:
            with self.subTest(v['id']):
                self.assertEqual(bytes_digest(bytes.fromhex(v['bytes_hex'])), v['digest'])
        d = {v['id']: v['digest'] for v in self.vectors['object_bytes']}
        self.assertNotEqual(d['lf'], d['crlf'])

    def test_projection_vectors_recomputed(self):
        fixture = self.vectors['projection_fixture']
        task = copy.deepcopy(fixture['task'])
        got = {
            'intent': digest_of(intent_part(task)),
            'context': digest_of(context_part(task)),
            'task': digest_of(task_part(task)),
            'action': digest_of(action_part(task['effects']['actions'][0])),
        }
        for k, want in fixture['expected'].items():
            self.assertEqual(got[k], want, k)
        self.assertEqual(canonical_text(intent_part(task)), fixture['canonical_intent'])
        self.assertEqual(canonical_text(context_part(task)), fixture['canonical_context'])
        self.assertEqual(canonical_text(action_part(task['effects']['actions'][0])), fixture['canonical_action'])

    def test_exclusions_do_not_change_digests(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        base = binding_digests(task, self.policy)
        t = copy.deepcopy(task)
        t['route_proposal'] = {'policy_version': 'law.cvf.routing/2', 'proposed_rows': ['R-READ_DRAFT']}
        t['proposed_by'] = {'actor_id': 'someone-else', 'role': 'worker'}
        t['note'] = 'changed'
        t['intent']['refs'][0]['locator'] = 'EXAMPLE://elsewhere'
        t['intent']['refs'][0]['ref_id'] = 'renamed'
        t['intent']['refs'][0]['attribution']['source_class'] = 'UNVERIFIED'
        t['intent']['refs'][0]['attribution']['channel'] = 'NONE'
        t['authority']['subject']['host'] = 'other-host'
        self.assertEqual(binding_digests(t, self.policy), base)

    def test_included_fields_change_digests(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        base = binding_digests(task, self.policy)
        edits = {
            'main_interpretation': lambda t: t['intent'].__setitem__('main_interpretation', 'other'),
            'task_revision': lambda t: t.__setitem__('task_revision', 2),
            'input digest': lambda t: t['inputs'][0].__setitem__('digest', 'sha256:' + '0' * 64),
            'input revision': lambda t: t['inputs'][0].__setitem__('revision', '2'),
            'action target': lambda t: t['effects']['actions'][0]['targets'].append('references/other.xlsx'),
            'requirement': lambda t: t['acceptance']['requirements'][0].__setitem__('statement', 'other'),
            'intent blob digest': lambda t: t['intent']['refs'][0].__setitem__('digest', 'sha256:' + '1' * 64),
            'grant digest': lambda t: t['authority']['grant_refs'][0].__setitem__('digest', 'sha256:' + '2' * 64),
            'context ref': lambda t: t.__setitem__('context_refs', [{'path': 'references/c.txt', 'digest': 'sha256:' + '3' * 64}]),
        }
        for label, edit in edits.items():
            with self.subTest(label):
                t = copy.deepcopy(task)
                edit(t)
                self.assertNotEqual(binding_digests(t, self.policy), base)

    def test_set_fields_are_order_independent_but_sequences_are_not(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        task['effects']['actions'][0]['targets'] = ['b.txt', 'a.txt']
        a = digest_of(action_part(task['effects']['actions'][0]))
        task['effects']['actions'][0]['targets'] = ['a.txt', 'b.txt']
        self.assertEqual(digest_of(action_part(task['effects']['actions'][0])), a)
        task['acceptance']['requirements'].append({'req_id': 'REQ-2', 'statement': 'x', 'mandatory': True})
        d1 = digest_of(task_part(task))
        task['acceptance']['requirements'].reverse()
        self.assertNotEqual(digest_of(task_part(task)), d1)

    def test_policy_digest_vector_matches_file(self):
        self.assertEqual(self.vectors['policy_digest']['digest'], digest_of(policy_part(self.policy)))
        self.assertEqual(self.vectors['policy_digest']['file'], '.cvf/rules/v2/ROUTING_POLICY.json')

    def test_unsupported_list_is_explicit(self):
        parts = {u['part'] for u in self.vectors['unsupported']}
        for need in ('path_alias_equivalence', 'non_file_objects', 'role_actual_context', 'review_effect_result_digests',
                     'v1_digest_comparison', 'time_and_expiry', 'attribution_authenticity'):
            self.assertIn(need, parts)


if __name__ == '__main__':
    unittest.main()
