"""A0 hẹp: kiểm candidate contract v3 (schema, policy, ví dụ giả, vectors) / narrow A0 candidate v3 contract checks.

Chỉ kiểm cấu trúc, định nghĩa binding và đối chiếu với owner đã nhận (tools/publish_new.py). Không chạy workflow, không có evaluator/checker,
không cấp quyền. Hàm tham chiếu law.cvf.bind/3 ở đây tính lại vectors và binding trong ví dụ; so sánh D4 và recipe route ở đây là so khớp trường dữ liệu
của ví dụ với kỳ vọng đã khai, không phải verdict của workflow.
Structure and binding-definition checks plus alignment with the accepted owner tool: no workflow run, no evaluator, no checker, no authority.
The reference functions recompute vectors and example bindings; the acceptance comparison only matches example fields against declared expectations.
"""
import copy
import hashlib
import json
import os
import re
import sys
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
V3C = os.path.join(CVF, 'contracts', 'v3')
V3R = os.path.join(CVF, 'rules', 'v3')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import publish_new as pn  # noqa: E402  (read-only: serializer, build_task and constants of the accepted owner)

BV = 'law.cvf.bind/3'
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
# v2 candidate: each key file, and the whole tree (30 files: contracts/v2 incl. 22 examples, rules/v2)
V2_PINS = {
    'contracts/v2/control.schema.json': '4c6dd3dae50596b5',
    'contracts/v2/CONTROL_CONTRACT.md': 'd3ad993fd4954506',
    'contracts/v2/vectors.json': '8d59d60ccd3af136',
    'contracts/v2/examples/EXPECTED.json': '3b463f654d51a9ec',
    'rules/v2/ROUTING_POLICY.json': '20cff567afe4fa0f',
    'rules/v2/CONTROL_RULES.md': '53738f251308b188',
}
V2_TREE_PIN = 'e154e1db4438adb9'
V2_TREE_FILES = 30
# SHA256 đầy đủ của writer đã nhận (tools/publish_new.py sau review corrective I)
WRITER_PIN = '8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852'
ENVELOPE = [('T1', 'mkdir'), ('T2', 'mkdir'), ('T3', 'create'), ('T4', 'create'), ('T5', 'link'), ('T6', 'create'), ('T7', 'delete')]


class Unsupported(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# ---------------------------------------------------------------- LAW-CJ/2 canonical JSON (unchanged from v2)
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


# ---------------------------------------------------------------- projections (bind/3: same definitions as v2, literal changed)
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
        d.pop('parent_task', None)
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


def sha_full(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def tree_hash(bases):
    lines = []
    for base in bases:
        for root, _, files in os.walk(os.path.join(ROOT, *base.split('/'))):
            for name in files:
                full = os.path.join(root, name)
                rel = os.path.relpath(full, ROOT).replace(os.sep, '/')
                lines.append('%s:%s' % (rel, sha_full(full)))
    lines.sort()
    return hashlib.sha256('\n'.join(lines).encode()).hexdigest()[:16], len(lines)


def schema_validator(schema):
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def setUpModule():
    if not HAVE_JSONSCHEMA:
        raise RuntimeError('jsonschema>=4.18 không có / not installed: BLOCKED, không tự cài / not auto-installed')


def records(bundle, record_type, stage=None):
    return [r for r in bundle['records'] if r['record_type'] == record_type and (stage is None or r.get('stage') == stage)]


def acceptance_consistency(bundle):
    """Fixture reference comparison (not an evaluator): how the user_acceptance fields relate to the current task and result."""
    task, result = records(bundle, 'task')[0], records(bundle, 'result')
    if not result or 'user_acceptance' not in result[0]:
        return 'ABSENT'
    result, ua = result[0], result[0]['user_acceptance']
    mandatory = {r['req_id'] for r in task['acceptance']['requirements'] if r['mandatory']}
    if not mandatory <= set(ua['accepted_requirements']):
        return 'REQUIREMENTS_INCOMPLETE'
    if (ua['task_id'], ua['task_revision'], ua['accepted_task_digest']) != (task['task_id'], task['task_revision'], digest_of(task_part(task))):
        return 'TASK_DIGEST_STALE'
    if ua['accepted_artifacts'] != result['artifacts'] or ua['result_id'] != result['result_id']:
        return 'ARTIFACTS_DIFFER'
    return 'MATCHES_CURRENT_TASK_AND_RESULT'


class CandidateBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = read_json(os.path.join(V3C, 'control.schema.json'))
        cls.policy = read_json(os.path.join(V3R, 'ROUTING_POLICY.json'))
        cls.expected = read_json(os.path.join(V3C, 'examples', 'EXPECTED.json'))
        cls.vectors = read_json(os.path.join(V3C, 'vectors.json'))
        cls.validator = schema_validator(cls.schema)

    def example(self, name):
        return read_json(os.path.join(V3C, 'examples', name))


class OlderVersionsUntouched(unittest.TestCase):
    def test_v1_owner_hashes_unchanged(self):
        for rel, want in V1_PINS.items():
            self.assertEqual(sha16(os.path.join(CVF, *rel.split('/'))), want, rel)

    def test_v2_candidate_tree_is_byte_identical(self):
        for rel, want in V2_PINS.items():
            self.assertEqual(sha16(os.path.join(CVF, *rel.split('/'))), want, rel)
        self.assertEqual(tree_hash(['.cvf/contracts/v2', '.cvf/rules/v2']), (V2_TREE_PIN, V2_TREE_FILES))

    def test_no_checker_discovers_v3(self):
        for rel in ('control_check.py', 'control_check_v2.py'):
            src = read_text(os.path.join(CVF, 'checks', rel))
            for word in ('contracts/v3', 'rules/v3', 'control/3', 'bind/3', 'routing/3'):
                self.assertNotIn(word, src, rel)
        v2 = os.path.join(CVF, 'checks', 'v2')
        for name in sorted(os.listdir(v2)):
            if name.endswith('.py'):
                src = read_text(os.path.join(v2, name))
                for word in ('contracts/v3', 'rules/v3', 'control/3'):
                    self.assertNotIn(word, src, name)

    def test_v2_schema_still_refuses_v3_and_v3_refuses_v2(self):
        v2 = schema_validator(read_json(os.path.join(V2C, 'control.schema.json')))
        v3 = schema_validator(read_json(os.path.join(V3C, 'control.schema.json')))
        b3 = read_json(os.path.join(V3C, 'examples', 'ex04_pcn1_accepted_d4_complete.json'))
        self.assertTrue(list(v2.iter_errors(b3)))
        b2 = read_json(os.path.join(V2C, 'examples', 'ex01_draft_in_grant.json'))
        self.assertTrue(list(v3.iter_errors(b2)))


class WriterPin(unittest.TestCase):
    """The accepted writer is pinned by full SHA256. A different hash is reported, never silently re-pinned."""

    def test_writer_bytes_equal_the_accepted_pin(self):
        self.assertEqual(sha_full(os.path.join(ROOT, 'tools', 'publish_new.py')), WRITER_PIN)
        self.assertEqual(pn.entrypoint_sha256(), 'sha256:' + WRITER_PIN)

    def test_policy_pin_equals_the_writer_pin(self):
        policy = read_json(os.path.join(V3R, 'ROUTING_POLICY.json'))
        self.assertEqual([o['entrypoint_sha256'] for o in policy['owner_protocols']], ['sha256:' + WRITER_PIN])


class SchemaAndPolicy(CandidateBase):
    def test_schema_is_valid_draft_2020_12(self):
        jsonschema.Draft202012Validator.check_schema(self.schema)

    def test_literals(self):
        self.assertEqual(self.schema['$id'], 'urn:law:cvf:control:3')
        d = self.schema['$defs']
        self.assertEqual(d['schema_version']['const'], 'law.cvf.control/3')
        self.assertEqual(d['policy_version']['const'], 'law.cvf.routing/3')
        self.assertEqual(d['evaluation_basis']['const'], 'COOPERATIVE_WORKFLOW')
        self.assertEqual(d['bind_version']['const'], BV)
        self.assertEqual(d['routing_policy']['properties']['binding_definition']['const'], BV)
        self.assertEqual(d['effect']['properties']['assurance_level']['enum'], ['UNVERIFIED', 'ADVISORY'])
        self.assertEqual(d['output_object']['properties']['role'], {'const': 'ACTUAL_BYTES'})

    def test_no_self_verifiable_trust_fields(self):
        raw = json.dumps(self.schema)
        for word in ('trust_anchor', 'trusted_ref', '"verification"', 'ENFORCED_FOR_NAMED_ACTIONS', 'TRUSTED_VERIFIED', 'overlay_digest'):
            self.assertNotIn(word, raw)

    def test_only_the_needed_zone_and_condition_were_added(self):
        v2 = read_json(os.path.join(V2C, 'control.schema.json'))['$defs']
        self.assertEqual(sorted(set(self.schema['$defs']['write_zone']['enum']) - set(v2['write_zone']['enum'])), ['agent_runtime'])
        self.assertEqual(set(v2['write_zone']['enum']) - set(self.schema['$defs']['write_zone']['enum']), set())
        self.assertEqual(sorted(set(self.schema['$defs']['condition']['enum']) - set(v2['condition']['enum'])), ['CONTENT_USE_INTERNAL_ONLY'])
        self.assertEqual(sorted(set(self.schema['$defs']['reason_code']['enum']) - set(v2['reason_code']['enum'])),
                         sorted(['INPUT_CHANGED_SINCE_READ', 'PRECONDITION_PROOF_MISSING', 'CHANGED_AFTER_PUBLISH', 'REVIEW_REQUIRED_UNSUPPORTED']))
        for gone in ('protection_overlay',):
            self.assertNotIn(gone, self.schema['properties']['record_type']['enum'])

    def test_policy_valid_and_candidate(self):
        self.assertEqual(list(self.validator.iter_errors(self.policy)), [])
        self.assertEqual(self.policy['status'], 'CANDIDATE_NOT_ACTIVE')
        self.assertEqual(self.policy['policy_version'], 'law.cvf.routing/3')
        self.assertEqual(self.policy['binding_definition'], BV)
        for k, v in (('assurance_ceiling', 'ADVISORY'), ('tamper_resistance', 'NONE'), ('basis_change_per_run', 'FORBIDDEN'),
                     ('legacy_and_unknown_handling', 'REFUSE_NO_AUTO_MIGRATION'), ('main_may_downgrade', False),
                     ('review_grants_authority', False), ('unknown_handling', 'NEVER_ALLOW'), ('conditional_route_disposition', 'BLOCKED'),
                     ('unmapped_path_handling', 'UNCLASSIFIED'), ('unmatched_effect_route', 'R-UNCLASSIFIED')):
            self.assertEqual(self.policy[k], v)

    def test_rows_equal_v2_except_the_two_changed_rows(self):
        v2 = read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))
        self.assertEqual([r['row_id'] for r in v2['rows']], [r['row_id'] for r in self.policy['rows']])
        for a, b in zip(v2['rows'], self.policy['rows']):
            if b['row_id'] in ('R-READ_DRAFT', 'R-MUTATION'):
                continue
            self.assertEqual({k: v for k, v in a.items()}, {k: v for k, v in b.items()}, a['row_id'])
        for k in ('combine', 'missing_required_reviewer', 'reviewer_dispatch_needs_review', 'unresolved_condition', 'unmatched_effect_route',
                  'group_grant_reuse', 'match_semantics', 'unsupported_binding_part_handling', 'independent_read_draft_continues'):
            self.assertEqual(v2[k], self.policy[k], k)

    def test_changed_rows_keep_gates_reviews_and_sources(self):
        v2 = {r['row_id']: r for r in read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))['rows']}
        rows = {r['row_id']: r for r in self.policy['rows']}
        for rid in ('R-READ_DRAFT', 'R-MUTATION'):
            for k in ('required_gates', 'required_review_phases', 'authority_evidence', 'attributed_refs_required'):
                self.assertEqual(v2[rid][k], rows[rid][k], (rid, k))
        self.assertEqual(rows['R-READ_DRAFT']['required_review_phases'], [])

    def test_read_draft_is_split_in_three_clauses(self):
        clauses = {r['row_id']: r for r in self.policy['rows']}['R-READ_DRAFT']['match_any']
        self.assertEqual(clauses, [
            {'operations': ['read'], 'write_zones': ['none']},
            {'operations': ['create_new'], 'write_zones': ['working'], 'conditions_all': ['NO_PROTECTED_TARGET']},
            {'operations': ['create_new'], 'write_zones': ['output_new'], 'conditions_all': ['NO_PROTECTED_TARGET', 'CONTENT_USE_INTERNAL_ONLY']}])

    def test_mutation_gains_exactly_the_runtime_create_clause(self):
        v2 = {r['row_id']: r for r in read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))['rows']}['R-MUTATION']['match_any']
        now = {r['row_id']: r for r in self.policy['rows']}['R-MUTATION']['match_any']
        self.assertEqual(now[:len(v2)], v2)
        self.assertEqual(now[len(v2):], [{'operations': ['create_new'], 'write_zones': ['agent_runtime']}])

    def test_no_row_other_than_read_draft_can_match_light_create_new(self):
        for r in self.policy['rows']:
            if r['row_id'] == 'R-READ_DRAFT':
                continue
            for clause in r['match_any']:
                ops, zones = clause.get('operations'), clause.get('write_zones')
                self.assertFalse(ops and 'create_new' in ops and zones and set(zones) & {'working', 'output_new'}, r['row_id'])

    def test_zones_and_light_zones(self):
        self.assertEqual(self.policy['light_write_zones'], ['working', 'output_new'])
        self.assertEqual(self.policy['zone_map'], [{'path_prefix': 'working/', 'write_zone': 'working'},
                                                   {'path_prefix': 'output/', 'write_zone': 'output_new'},
                                                   {'path_prefix': '.agent/runtime/', 'write_zone': 'agent_runtime'}])
        rank = self.policy['write_zone_rank']
        self.assertEqual(rank, ['none', 'working', 'output_new', 'agent_runtime', 'original_source', 'shared_register', 'framework', 'external'])
        self.assertNotIn('unknown', rank)
        self.assertLess(rank.index('output_new'), rank.index('agent_runtime'))
        for zone in self.policy['light_write_zones']:
            self.assertLess(rank.index(zone), rank.index('agent_runtime'))
        self.assertEqual(self.policy['authority_name_patterns'], list(pn.AUTHORITY_PATTERNS))

    def test_new_target_assumption_is_closable_only_before_the_effect(self):
        self.assertEqual(self.policy['open_assumptions'], [{
            'id': 'A-NEW_TARGET', 'applies_to_operations': ['create_new'], 'route_status_while_open': 'CONDITIONAL', 'closed_by': 'S4_OBSERVER',
            'closes_in_phases': ['dispatch', 'effect'], 'observation_scope': 'AT_TIME_ONLY',
            'limits': ['EXCLUSIVE_WRITE_NOT_PROVEN', 'RACE_NOT_EXCLUDED'], 'not_applicable_in_phases': ['accept']}])

    def test_owner_protocol_entry(self):
        (op,) = self.policy['owner_protocols']
        self.assertEqual((op['protocol_id'], op['protocol_version'], op['owner_tool'], op['entrypoint']), ('P-CN1', 1, 'publish_new', 'tools/publish_new.py'))
        self.assertEqual((op['platform'], op['operation'], op['runtime_zone'], op['attaches_to_row']), ('windows-ntfs-local', 'create_new', 'agent_runtime', 'R-READ_DRAFT'))
        self.assertEqual([(e['id'], e['operation']) for e in op['envelope']], ENVELOPE)
        self.assertEqual(op['review_phases_supported'], [])
        self.assertEqual(op['grant_must_cover'], {'tools': ['publish_new'], 'operations': ['create_new', 'delete'],
                                                  'path_scopes': ['TARGET_AND_ANCESTORS', 'RUNTIME_DIR'], 'delete_scope': 'T7_STAGED_OF_SAME_RID_ONLY'})
        self.assertEqual(op['pin_semantics'], 'VERSION_COMPARE_ADVISORY')
        self.assertIn('DECLARED_TOOL_NAME_ONLY', op['not_exempt'])
        self.assertIn('FILE_LOCATION_ONLY', op['not_exempt'])
        self.assertIn('EVIDENCE_EDIT_OR_DELETE', op['not_exempt'])

    def test_receipt_is_only_required_at_accept(self):
        (op,) = self.policy['owner_protocols']
        self.assertEqual(op['receipt']['required_in_phases'], ['accept'])
        self.assertEqual(op['receipt']['ref_kind'], 'effect_receipt')
        phases = op['required_by_phase']
        for phase in ('dispatch', 'effect'):
            self.assertNotIn('RECEIPT_REF_RESOLVES_TO_PUBLISHED', phases[phase], phase)
            self.assertNotIn('PUBLISHED_EVIDENCE_RESOLVES_FOR_RID', phases[phase], phase)
            self.assertIn('ENTRYPOINT_SHA256_OBSERVED_EQUALS_PIN', phases[phase])
            self.assertIn('TARGET_ABSENT_OBSERVED_AT_TIME', phases[phase])
            self.assertIn('NO_REVIEW_PHASE_REQUIRED', phases[phase])
        self.assertNotIn('TARGET_ABSENT_OBSERVED_AT_TIME', phases['accept'])
        self.assertNotIn('ENTRYPOINT_SHA256_OBSERVED_EQUALS_PIN', phases['accept'])
        for need in ('PUBLISHED_EVIDENCE_RESOLVES_FOR_RID', 'RECEIPT_REF_RESOLVES_TO_PUBLISHED', 'RUNTIME_FILES_WITHIN_ENVELOPE',
                     'CURRENT_BYTES_EQUAL_PUBLISHED_CONTENT', 'USER_ACCEPTANCE_COMPLETE_D4'):
            self.assertIn(need, phases['accept'])

    def test_unsupported_scope_is_listed(self):
        for need in ('PROTECTION_OVERLAY', 'STAGED_BYTES_AND_RELATION', 'MULTI_ACTION_OCCURRENCE_AND_COMPLETION', 'EXTRA_REVIEW_PHASES',
                     'REVIEW_SCOPE_AND_CONCLUSIONS', 'OVERWRITE_OR_INPUT_IS_TARGET', 'POSIX_NETWORK_CLOUD_FILESYSTEMS', 'HOST_ENFORCEMENT'):
            self.assertIn(need, self.policy['unsupported_in_candidate'])

    def test_policy_mutations_are_rejected(self):
        def bad(mut):
            p = copy.deepcopy(self.policy)
            mut(p)
            return list(self.validator.iter_errors(p))
        op = lambda p: p['owner_protocols'][0]  # noqa: E731
        cases = {
            'active enforced status': lambda p: p.__setitem__('status', 'ACTIVE_ENFORCED_FOR_NAMED_ACTIONS'),
            'ceiling raised': lambda p: p.__setitem__('assurance_ceiling', 'ENFORCED_FOR_NAMED_ACTIONS'),
            'tamper claim': lambda p: p.__setitem__('tamper_resistance', 'PARTIAL'),
            'basis per run': lambda p: p.__setitem__('basis_change_per_run', 'ALLOWED'),
            'v2 policy version': lambda p: p.__setitem__('policy_version', 'law.cvf.routing/2'),
            'v2 schema version': lambda p: p.__setitem__('schema_version', 'law.cvf.control/2'),
            'bind v2 definition': lambda p: p.__setitem__('binding_definition', 'law.cvf.bind/2'),
            'row without refs': lambda p: p['rows'][0].pop('attributed_refs_required'),
            'row v1 field': lambda p: p['rows'][0].__setitem__('trusted_refs_required', ['grant']),
            'empty classes': lambda p: p['rows'][0]['attributed_refs_required'][0].__setitem__('accepted_source_classes', []),
            'main may downgrade': lambda p: p.__setitem__('main_may_downgrade', True),
            'conditional route allowed': lambda p: p.__setitem__('conditional_route_disposition', 'PASS'),
            'unmapped path light': lambda p: p.__setitem__('unmapped_path_handling', 'WORKING'),
            'light zone runtime': lambda p: p['light_write_zones'].append('agent_runtime'),
            'zone map unknown zone': lambda p: p['zone_map'].append({'path_prefix': 'x/', 'write_zone': 'agent_state'}),
            'no owner protocols': lambda p: p.__setitem__('owner_protocols', []),
            'missing owner_protocols': lambda p: p.pop('owner_protocols'),
            'owner pin missing': lambda p: op(p).pop('entrypoint_sha256'),
            'owner pin not a digest': lambda p: op(p).__setitem__('entrypoint_sha256', 'sha256:abc'),
            'owner pin semantics strong': lambda p: op(p).__setitem__('pin_semantics', 'AUTHENTICATED'),
            'owner platform posix': lambda p: op(p).__setitem__('platform', 'posix'),
            'owner operation overwrite': lambda p: op(p).__setitem__('operation', 'overwrite'),
            'owner zone framework': lambda p: op(p)['target_zones'].append('framework'),
            'owner attaches to mutation': lambda p: op(p).__setitem__('attaches_to_row', 'R-MUTATION'),
            'owner review phase supported': lambda p: op(p).__setitem__('review_phases_supported', ['PRE_EFFECT']),
            'owner envelope short': lambda p: op(p)['envelope'].pop(),
            'owner envelope swapped': lambda p: op(p)['envelope'].reverse(),
            'owner envelope extra': lambda p: op(p)['envelope'].append({'id': 'T8', 'operation': 'delete', 'path_scope': 'TARGET'}),
            'owner delete anywhere': lambda p: op(p)['grant_must_cover'].__setitem__('delete_scope', 'ANY'),
            'owner receipt before accept': lambda p: op(p)['receipt'].__setitem__('required_in_phases', ['dispatch', 'accept']),
            'owner token unknown': lambda p: op(p)['required_by_phase']['accept'].append('TOOL_NAME_DECLARED'),
            'owner phase missing': lambda p: op(p)['required_by_phase'].pop('effect'),
            'assumption closed at accept': lambda p: p['open_assumptions'][0].__setitem__('closes_in_phases', ['dispatch', 'effect', 'accept']),
            'assumption observer other': lambda p: p['open_assumptions'][0].__setitem__('closed_by', 'MAIN'),
        }
        for label, m in cases.items():
            with self.subTest(label):
                self.assertTrue(bad(m), label)


class Examples(CandidateBase):
    def test_expected_covers_every_file(self):
        files = sorted(f for f in os.listdir(os.path.join(V3C, 'examples')) if f.startswith('ex') and f.endswith('.json'))
        self.assertEqual(files, sorted(c['file'] for c in self.expected['cases']))
        self.assertEqual(len(files), 22)
        self.assertTrue(self.expected['example_only'])
        self.assertEqual(self.expected['workflow_status'], 'NOT_RUN')
        self.assertEqual(self.expected['policy'], '../../../rules/v3/ROUTING_POLICY.json')

    def test_schema_validity_matches_expected(self):
        for c in self.expected['cases']:
            errs = list(self.validator.iter_errors(self.example(c['file'])))
            self.assertEqual(not errs, c['schema_valid'], '%s: %s' % (c['file'], errs[:1]))
            self.assertFalse(c['workflow_tested'], c['file'])
        self.assertEqual(sum(1 for c in self.expected['cases'] if c['schema_valid']), 15)

    def test_examples_are_fake_and_inactive(self):
        for c in self.expected['cases']:
            raw = read_text(os.path.join(V3C, 'examples', c['file']))
            self.assertIn('"example_only": true', raw)
            self.assertNotIn('"status": "ACTIVE"', raw)
            self.assertNotIn('"disposition": "PASS"', raw)
            self.assertNotIn('trust_anchor', raw)
            self.assertNotIn('"verification"', raw)

    def test_every_expected_case_has_a_design_and_no_shipped_verdict_claim(self):
        for c in self.expected['cases']:
            self.assertIn('why', c['expected_design'], c['file'])
            if not c['schema_valid']:
                self.assertEqual(c['expected_design']['disposition'], 'NOT_EVALUATED', c['file'])
            else:
                self.assertIn(c['expected_design']['disposition'], ('PASS', 'BLOCKED', 'DENY', 'UNSUPPORTED'), c['file'])
                self.assertEqual(c['expected_design']['assurance_level'], 'ADVISORY', c['file'])
        self.assertIn('NOT_RUN', json.dumps(self.expected['as_shipped_expectation']))
        for c in self.expected['cases']:
            if c['expected_design']['disposition'] == 'PASS':
                self.assertIn('Counterfactual only', c['expected_design']['why'], c['file'])

    def test_expected_reasons_are_schema_codes_and_checker_owned_codes_stay_outside_the_enum(self):
        enum = set(self.schema['$defs']['reason_code']['enum'])
        owned = set()
        for c in self.expected['cases']:
            design = c['expected_design']
            self.assertTrue(set(design.get('reasons', [])) <= enum, c['file'])
            self.assertFalse(set(design.get('reasons_checker_owned', [])) & enum, c['file'])
            owned |= set(design.get('reasons_checker_owned', []))
        for need in ('USER_ACCEPTANCE_INCOMPLETE', 'USER_ACCEPTANCE_STALE'):
            self.assertIn(need, owned)
        for o in self.expected['observation_scenarios']:
            self.assertTrue(set(o['expected_design'].get('reasons', [])) <= enum, o['id'])
            self.assertFalse(set(o['expected_design'].get('reasons_checker_owned', [])) & enum, o['id'])

    def test_binding_recomputation_matches_expectation(self):
        for c in self.expected['cases']:
            if not c['schema_valid']:
                continue
            bundle = self.example(c['file'])
            task = records(bundle, 'task')[0]
            want = binding_digests(task, self.policy)
            want_action = digest_of(action_part(task['effects']['actions'][0]))
            bad = []
            for r in bundle['records']:
                b = r.get('binding')
                if not b:
                    continue
                self.assertEqual(b['bind_version'], BV)
                self.assertEqual(b['policy_version'], 'law.cvf.routing/3')
                self.assertEqual((b['task_id'], b['task_revision']), (task['task_id'], task['task_revision']))
                for k, v in want.items():
                    if b.get(k) != v:
                        bad.append((r['record_type'], k))
                if 'action_digest' in b and b['action_digest'] != want_action:
                    bad.append((r['record_type'], 'action_digest'))
            self.assertEqual(bool(bad), c['binding_stale_or_mismatched'], '%s %s' % (c['file'], bad))

    def test_outputs_artifacts_and_result_are_exact_and_actual_bytes_only(self):
        for c in self.expected['cases']:
            if not c['schema_valid']:
                continue
            bundle = self.example(c['file'])
            for e in records(bundle, 'effect', 'REQUEST'):
                self.assertNotIn('outputs', e['binding'], c['file'])
                self.assertNotIn('receipt_ref', e, c['file'])
            for e in records(bundle, 'effect', 'OUTCOME'):
                self.assertEqual(e['binding']['outputs'], e['outcome']['artifacts'], c['file'])
            for r in records(bundle, 'result'):
                self.assertEqual(r['binding']['outputs'], r['artifacts'], c['file'])
                if 'action_digest' in r['binding']:
                    task = records(bundle, 'task')[0]
                    self.assertEqual(r['binding']['action_digest'], digest_of(action_part(task['effects']['actions'][0])), c['file'])
            for item in [a for r in records(bundle, 'result') for a in r['artifacts']]:
                self.assertEqual(item['role'], 'ACTUAL_BYTES')

    def test_route_rows_and_phases_declared_in_effects_match_expectation(self):
        for c in self.expected['cases']:
            if not c['schema_valid']:
                continue
            bundle = self.example(c['file'])
            for e in records(bundle, 'effect'):
                self.assertEqual(e['routing']['matched_rows'], c['route_rows'], c['file'])
                self.assertEqual(e['routing']['required_review_phases'], c['required_review_phases'], c['file'])
                self.assertEqual(e['action'], records(bundle, 'task')[0]['effects']['actions'][0], c['file'])

    def test_acceptance_fields_match_the_declared_consistency(self):
        for c in self.expected['cases']:
            if c['schema_valid']:
                self.assertEqual(acceptance_consistency(self.example(c['file'])), c['acceptance_consistency'], c['file'])

    def test_result_action_digest_remains_optional_as_in_v2(self):
        bundle = self.example('ex04_pcn1_accepted_d4_complete.json')
        task, result = records(bundle, 'task')[0], records(bundle, 'result')[0]
        self.assertNotIn('action_digest', result['binding'])
        wanted = digest_of(action_part(task['effects']['actions'][0]))
        result['binding']['action_digest'] = wanted
        self.assertEqual(list(self.validator.iter_errors(bundle)), [], 'deferred delta08 must not forbid the v2 optional field')
        self.assertEqual(result['binding']['action_digest'], wanted)
        result['binding']['action_digest'] = 'sha256:' + '0' * 64
        self.assertEqual(list(self.validator.iter_errors(bundle)), [], 'a stale digest has valid shape; a future checker must block it')
        self.assertNotEqual(result['binding']['action_digest'], wanted)

    def test_receipt_digest_is_the_digest_of_the_raw_published_bytes(self):
        fx = self.vectors['receipt_fixture']
        raw = pn.cj_dumps(fx['published'])
        self.assertEqual(raw.decode('utf-8'), fx['canonical_utf8'])
        self.assertEqual(bytes_digest(raw), fx['digest'])
        self.assertEqual(canonical_bytes(fx['published']), raw, 'reference serializer equals the owner serializer')
        self.assertIsNotNone(pn.validate_evidence(raw, fx['published']['request_id'], 'published'))
        seen = 0
        for c in self.expected['cases']:
            if not c['schema_valid']:
                continue
            bundle = self.example(c['file'])
            for e in records(bundle, 'effect', 'OUTCOME'):
                if 'receipt_ref' not in e:
                    continue
                seen += 1
                ref = e['receipt_ref']
                self.assertEqual(ref['digest'], fx['digest'], c['file'])
                self.assertEqual(ref['kind'], 'effect_receipt')
                self.assertEqual(ref['locator'], '.agent/runtime/publish/%s.published.json' % fx['published']['request_id'])
                self.assertEqual(ref['attribution']['source_class'], 'TOOL_OBSERVATION')
                art = e['outcome']['artifacts'][0]
                self.assertEqual((fx['published']['target'], fx['published']['content']['sha256']), (art['path'], art['digest']))
        self.assertGreaterEqual(seen, 3)

    def test_missing_receipt_example_has_none_and_the_rest_have_one(self):
        no_receipt = [c['file'] for c in self.expected['cases'] if c['schema_valid']
                      and any('receipt_ref' not in e for e in records(self.example(c['file']), 'effect', 'OUTCOME'))]
        self.assertEqual(no_receipt, ['ex05_pcn1_receipt_missing.json'])

    def test_observation_scenarios_point_at_real_cases(self):
        files = {c['file'] for c in self.expected['cases']}
        for o in self.expected['observation_scenarios']:
            self.assertIn(o['base'], files, o['id'])
            self.assertNotEqual(o['expected_design']['disposition'], 'PASS', o['id'])
        self.assertEqual([o['id'] for o in self.expected['observation_scenarios']], ['OBS-1', 'OBS-2', 'OBS-3', 'OBS-4', 'OBS-5'])

    def test_grant_examples_cover_or_miss_the_envelope_as_declared(self):
        full = self.example('ex01_pcn1_working_request.json')
        (grant,) = records(full, 'grant')
        (op,) = self.policy['owner_protocols']
        self.assertTrue(set(op['grant_must_cover']['tools']) <= set(grant['scope']['tools']))
        self.assertTrue(set(op['grant_must_cover']['operations']) <= set(grant['scope']['operations']))
        self.assertIn(op['runtime_dir'], grant['scope']['paths'])
        self.assertNotIn('expires_at', grant.get('limits', {}))
        self.assertEqual(grant['status'], 'EXAMPLE_INACTIVE')
        (narrow,) = records(self.example('ex12_pcn1_grant_not_covering_envelope.json'), 'grant')
        self.assertNotIn('delete', narrow['scope']['operations'])
        self.assertNotIn(op['runtime_dir'], narrow['scope']['paths'])


class Mutations(CandidateBase):
    def bundle(self):
        return copy.deepcopy(self.example('ex04_pcn1_accepted_d4_complete.json'))

    def rejects(self, mutate, label):
        b = self.bundle()
        mutate(b)
        self.assertTrue(list(self.validator.iter_errors(b)), label)

    def test_baseline_valid(self):
        self.assertEqual(list(self.validator.iter_errors(self.bundle())), [])

    def test_mutations_are_rejected(self):
        def first(b, rt, stage=None): return next(r for r in b['records'] if r['record_type'] == rt and (stage is None or r.get('stage') == stage))
        def task(b): return first(b, 'task')
        def req(b): return first(b, 'effect', 'REQUEST')
        def out(b): return first(b, 'effect', 'OUTCOME')
        def res(b): return first(b, 'result')
        def ua(b): return res(b)['user_acceptance']
        cases = {
            'schema_version v2': lambda b: task(b).__setitem__('schema_version', 'law.cvf.control/2'),
            'schema_version v4': lambda b: task(b).__setitem__('schema_version', 'law.cvf.control/4'),
            'basis missing': lambda b: task(b).pop('evaluation_basis'),
            'basis unknown': lambda b: task(b).__setitem__('evaluation_basis', 'TRUSTED_ENFORCED'),
            'binding bind_version v2': lambda b: out(b)['binding'].__setitem__('bind_version', 'law.cvf.bind/2'),
            'binding policy_version v2': lambda b: out(b)['binding'].__setitem__('policy_version', 'law.cvf.routing/2'),
            'binding policy_digest missing': lambda b: out(b)['binding'].pop('policy_digest'),
            'effect routing policy v2': lambda b: out(b)['routing'].__setitem__('policy_version', 'law.cvf.routing/2'),
            'trust_anchor field': lambda b: task(b)['intent']['refs'][0].__setitem__('trust_anchor', 'MAIN_DECLARED'),
            'enforced assurance': lambda b: out(b).__setitem__('assurance_level', 'ENFORCED_FOR_NAMED_ACTIONS'),
            'main authored user confirmation': lambda b: task(b)['intent']['refs'][0]['attribution'].__setitem__('channel', 'MAIN_AUTHORED'),
            'user confirmation without locator': lambda b: task(b)['intent']['refs'][0]['attribution'].pop('evidence_locator'),
            'unknown zone agent_state': lambda b: task(b)['effects']['actions'][0].__setitem__('write_zone', 'agent_state'),
            'unknown zone package_content': lambda b: req(b)['action'].__setitem__('write_zone', 'package_content'),
            'action completion deferred': lambda b: task(b)['effects']['actions'][0].__setitem__('completion', 'OPTIONAL'),
            'extra review phases deferred': lambda b: task(b)['effects'].__setitem__('extra_review_phases', ['PRE_EFFECT']),
            'effect action_index deferred': lambda b: out(b).__setitem__('action_index', 0),
            'overlay digest in binding': lambda b: out(b)['binding'].__setitem__('overlay_digest', 'sha256:' + '0' * 64),
            'staged role on outcome': lambda b: out(b)['outcome']['artifacts'][0].__setitem__('role', 'STAGED_BYTES'),
            'staged role on binding outputs': lambda b: out(b)['binding']['outputs'][0].__setitem__('role', 'STAGED_BYTES'),
            'relation on artifact': lambda b: out(b)['outcome']['artifacts'][0].__setitem__('relation', 'COPY_IDENTICAL'),
            'role missing on artifact': lambda b: res(b)['artifacts'][0].pop('role'),
            'role missing on binding outputs': lambda b: res(b)['binding']['outputs'][0].pop('role'),
            'receipt on request': lambda b: req(b).__setitem__('receipt_ref', copy.deepcopy(out(b)['receipt_ref'])),
            'receipt wrong kind': lambda b: out(b)['receipt_ref'].__setitem__('kind', 'review_receipt'),
            'receipt without attribution': lambda b: out(b)['receipt_ref'].pop('attribution'),
            'user accepted without object': lambda b: res(b).pop('user_acceptance'),
            'old user_acceptance_ref field': lambda b: res(b).__setitem__('user_acceptance_ref', copy.deepcopy(ua(b)['ref'])),
            'acceptance via file channel': lambda b: ua(b)['ref']['attribution'].__setitem__('channel', 'USER_AUTHORED_FILE'),
            'acceptance from main proposal': lambda b: ua(b)['ref']['attribution'].update({'source_class': 'MAIN_PROPOSAL', 'channel': 'MAIN_AUTHORED'}),
            'acceptance ref wrong kind': lambda b: ua(b)['ref'].__setitem__('kind', 'user_intent'),
            'acceptance ref without locator evidence': lambda b: ua(b)['ref']['attribution'].pop('evidence_locator'),
            'acceptance missing task digest': lambda b: ua(b).pop('accepted_task_digest'),
            'acceptance missing task id': lambda b: ua(b).pop('task_id'),
            'acceptance missing revision': lambda b: ua(b).pop('task_revision'),
            'acceptance missing requirements': lambda b: ua(b).pop('accepted_requirements'),
            'acceptance empty requirements': lambda b: ua(b).__setitem__('accepted_requirements', []),
            'acceptance duplicate requirements': lambda b: ua(b).__setitem__('accepted_requirements', ['REQ-1', 'REQ-1']),
            'acceptance missing result id': lambda b: ua(b).pop('result_id'),
            'acceptance missing artifacts': lambda b: ua(b).pop('accepted_artifacts'),
            'acceptance empty artifacts': lambda b: ua(b).__setitem__('accepted_artifacts', []),
            'acceptance artifact staged': lambda b: ua(b)['accepted_artifacts'][0].__setitem__('role', 'STAGED_BYTES'),
            'acceptance missing summary': lambda b: ua(b).pop('presented_summary'),
            'acceptance summary without digest': lambda b: ua(b)['presented_summary'].pop('digest'),
            'acceptance extra field': lambda b: ua(b).__setitem__('verified', True),
            'overlay record': lambda b: b['records'].append({'schema_version': 'law.cvf.control/3', 'record_type': 'protection_overlay',
                                                             'evaluation_basis': 'COOPERATIVE_WORKFLOW'}),
        }
        for label, m in cases.items():
            with self.subTest(label):
                self.rejects(m, label)

    def test_structure_alone_never_decides_a_semantic_defect(self):
        # schema-valid records that the checker (not built yet) must still block: they are valid here by design
        for name in ('ex05_pcn1_receipt_missing.json', 'ex08_pcn1_acceptance_incomplete.json', 'ex09_pcn1_acceptance_stale_task.json',
                     'ex10_pcn1_acceptance_other_artifact.json', 'ex11_pcn1_direct_runtime_write.json', 'ex13_pcn1_review_required_unsupported.json'):
            with self.subTest(name):
                self.assertEqual(list(self.validator.iter_errors(self.example(name))), [])


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
        self.assertEqual(len(self.vectors['canonical']), 20)

    def test_canonical_vectors_are_the_v2_canon_and_the_owner_serializer_agrees(self):
        v2 = read_json(os.path.join(V2C, 'vectors.json'))
        self.assertEqual(self.vectors['canonical'], v2['canonical'])
        self.assertEqual(self.vectors['object_bytes'], v2['object_bytes'])
        for v in self.vectors['canonical']:
            with self.subTest(v['id']):
                exp = v['expected']
                if exp['status'] == 'UNSUPPORTED':
                    with self.assertRaises(pn.CJError):
                        pn.cj_dumps(pn.cj_loads(v['input_json']))
                else:
                    self.assertEqual(pn.cj_dumps(pn.cj_loads(v['input_json'])).decode('utf-8'), exp['canonical_utf8'])

    def test_object_bytes_vectors(self):
        for v in self.vectors['object_bytes']:
            with self.subTest(v['id']):
                self.assertEqual(bytes_digest(bytes.fromhex(v['bytes_hex'])), v['digest'])
        d = {v['id']: v['digest'] for v in self.vectors['object_bytes']}
        self.assertNotEqual(d['lf'], d['crlf'])

    def test_projection_vectors_recomputed_from_the_owner_snapshot(self):
        fixture = self.vectors['projection_fixture']
        task = copy.deepcopy(fixture['task'])
        self.assertEqual(task, pn.build_task(fixture['request'], fixture['request_id']), 'the fixture is exactly the snapshot the owner builds')
        self.assertEqual(task['schema_version'], 'law.cvf.control/3')
        self.assertEqual(pn.TASK_SCHEMA_VERSION, 'law.cvf.control/3')
        self.assertEqual(list(self.validator.iter_errors(task)), [], 'the owner snapshot is valid under the v3 schema')
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

    def test_v2_snapshot_literal_is_refused_by_v3(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        task['schema_version'] = 'law.cvf.control/2'
        self.assertTrue(list(self.validator.iter_errors(task)))

    def test_digests_differ_from_what_bind_2_would_give(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        old = canonical_bytes(dict(intent_part(task), bind='law.cvf.bind/2'))
        self.assertNotEqual(bytes_digest(old), digest_of(intent_part(task)))

    def test_exclusions_do_not_change_digests(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        base = binding_digests(task, self.policy)
        t = copy.deepcopy(task)
        t['route_proposal'] = {'policy_version': 'law.cvf.routing/3', 'proposed_rows': ['R-READ_DRAFT']}
        t['proposed_by'] = {'actor_id': 'someone-else', 'role': 'worker'}
        t['note'] = 'changed'
        t['example_only'] = True
        t['intent']['refs'][0]['locator'] = 'EXAMPLE://elsewhere'
        t['intent']['refs'][0]['ref_id'] = 'renamed'
        t['intent']['refs'][0]['attribution']['source_class'] = 'UNVERIFIED'
        t['intent']['refs'][0]['attribution']['channel'] = 'NONE'
        t['authority']['grant_refs'][0]['locator'] = 'EXAMPLE://elsewhere'
        t['authority']['subject']['host'] = 'other-host'
        self.assertEqual(binding_digests(t, self.policy), base)

    def test_included_fields_change_digests(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        base = binding_digests(task, self.policy)
        edits = {
            'main_interpretation': lambda t: t['intent'].__setitem__('main_interpretation', 'other'),
            'task_revision': lambda t: t.__setitem__('task_revision', 2),
            'input digest': lambda t: t['inputs'][0].__setitem__('digest', 'sha256:' + '0' * 64),
            'action target': lambda t: t['effects']['actions'][0]['targets'].append('working/other.docx'),
            'action write_zone': lambda t: t['effects']['actions'][0].__setitem__('write_zone', 'output_new'),
            'expected output': lambda t: t['effects']['expected_outputs'].append('working/other.docx'),
            'requirement': lambda t: t['acceptance']['requirements'][0].__setitem__('statement', 'other'),
            'mandatory flag': lambda t: t['acceptance']['requirements'][0].__setitem__('mandatory', False),
            'intent blob digest': lambda t: t['intent']['refs'][0].__setitem__('digest', 'sha256:' + '1' * 64),
            'grant digest': lambda t: t['authority']['grant_refs'][0].__setitem__('digest', 'sha256:' + '2' * 64),
            'schema_version': lambda t: t.__setitem__('schema_version', 'law.cvf.control/2'),
        }
        for label, edit in edits.items():
            with self.subTest(label):
                t = copy.deepcopy(task)
                edit(t)
                self.assertNotEqual(binding_digests(t, self.policy), base)

    def test_set_fields_are_order_independent_but_sequences_are_not(self):
        task = copy.deepcopy(self.vectors['projection_fixture']['task'])
        task['effects']['actions'][0]['content_use'] = ['internal_draft', 'sign']
        a = digest_of(action_part(task['effects']['actions'][0]))
        task['effects']['actions'][0]['content_use'] = ['sign', 'internal_draft']
        self.assertEqual(digest_of(action_part(task['effects']['actions'][0])), a)
        d1 = digest_of(task_part(task))
        task['acceptance']['requirements'].reverse()
        self.assertNotEqual(digest_of(task_part(task)), d1)

    def test_policy_digest_vector_matches_file(self):
        self.assertEqual(self.vectors['policy_digest']['digest'], digest_of(policy_part(self.policy)))
        self.assertEqual(self.vectors['policy_digest']['file'], '.cvf/rules/v3/ROUTING_POLICY.json')
        v2 = read_json(os.path.join(V2R, 'ROUTING_POLICY.json'))
        self.assertNotEqual(self.vectors['policy_digest']['digest'], digest_of(dict(policy_part(v2), bind=BV)))

    def test_unsupported_list_is_explicit(self):
        parts = {u['part'] for u in self.vectors['unsupported']}
        for need in ('path_alias_equivalence', 'non_file_objects', 'role_actual_context', 'review_effect_result_digests', 'v1_digest_comparison',
                     'time_and_expiry', 'attribution_authenticity', 'bind_2_bind_3_equivalence', 'staged_bytes_and_relation', 'overlay_digest',
                     'multi_action_occurrence', 'receipt_authenticity', 'entrypoint_pin_authenticity', 'historical_precondition_from_current_state'):
            self.assertIn(need, parts)


class OwnerToolAlignment(CandidateBase):
    """The candidate must describe the accepted writer, not a different one. These are read-only comparisons."""

    def test_constants_match_the_policy_entry(self):
        (op,) = self.policy['owner_protocols']
        self.assertEqual(pn.PROTOCOL, op['protocol_id'])
        self.assertEqual(pn.PROTOCOL_VERSION, op['protocol_version'])
        self.assertEqual(pn.TOOL_NAME, op['owner_tool'])
        self.assertEqual(pn.PLATFORM, op['platform'])
        self.assertEqual('/'.join(pn.PUBLISH_DIR) + '/', op['runtime_dir'])
        self.assertEqual(pn.SCHEMA, op['receipt']['evidence_schema'])
        self.assertTrue(os.path.isfile(os.path.join(ROOT, *op['entrypoint'].split('/'))))

    def test_authority_patterns_and_zones_match_the_tool(self):
        self.assertEqual(self.policy['authority_name_patterns'], list(pn.AUTHORITY_PATTERNS))
        for target, zone in (('working/a/b.docx', 'working'), ('output/a/b.docx', 'output_new')):
            self.assertEqual(pn.target_zone(target), zone)
            self.assertIn(zone, self.policy['light_write_zones'])
        self.assertIsNone(pn.target_zone('references/a.docx'))
        self.assertIsNone(pn.target_zone('.agent/runtime/publish/x.json'))

    def test_tool_uses_exactly_the_envelope_labels_of_the_policy(self):
        src = read_text(os.path.join(ROOT, 'tools', 'publish_new.py'))
        for label, _ in ENVELOPE:
            self.assertIn("'%s'" % label, src, label)
        self.assertNotIn("'T8'", src)
        self.assertEqual([e['id'] for e in self.policy['owner_protocols'][0]['envelope']], [label for label, _ in ENVELOPE])

    def test_tool_refuses_what_the_candidate_does_not_support(self):
        base = {'work_id': 'w-1', 'target': 'working/w-1/a.docx',
                'intent_ref': {'ref_id': 'i', 'locator': 'host:1', 'digest': 'sha256:' + '1' * 64,
                               'attribution': {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:1',
                                               'recorded_by': {'actor_id': 'main', 'role': 'main'}}},
                'main_interpretation': 'x', 'requirements': [{'req_id': 'R1', 'statement': 's', 'mandatory': True}],
                'grant_refs': [{'ref_id': 'g', 'locator': 'P.md#1', 'digest': 'sha256:' + '2' * 64,
                                'attribution': {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:2',
                                                'recorded_by': {'actor_id': 'main', 'role': 'main'}}}],
                'subject': {'actor_id': 'main', 'role': 'main'}, 'inputs': []}
        rid = '0' * 32
        self.assertEqual(pn.build_task(base, rid)['effects']['actions'][0]['write_zone'], 'working')
        for label, extra in (('extra review phases', {'extra_review_phases': ['PRE_EFFECT']}), ('completion', {'completion': 'REQUIRED'}),
                             ('protected targets', {'protected_targets': ['x']}), ('context refs', {'context_refs': []})):
            with self.subTest(label), self.assertRaises(pn.RequestError):
                pn.build_task(dict(base, **extra), rid)
        for target, reason in (('references/a.docx', 'ZONE_NOT_LIGHT'), ('working/w-1/AGENTS.md', 'AUTHORITY_NAME')):
            with self.subTest(target), self.assertRaises(pn.RequestError) as cm:
                pn.build_task(dict(base, target=target), rid)
            self.assertEqual(cm.exception.reason, reason)
        with self.assertRaises(pn.RequestError) as cm:
            pn.build_task(dict(base, target='output/w-1/a.docx', content_use=['internal_draft', 'send_external']), rid)
        self.assertEqual(cm.exception.reason, 'CONTENT_USE_NOT_INTERNAL')
        with self.assertRaises(pn.RequestError) as cm:
            pn.build_task(dict(base, target='output/w-1/a.docx'), rid)
        self.assertEqual(cm.exception.reason, 'SNAPSHOT_INCOMPLETE')

    def test_negative_examples_describe_cases_the_tool_would_not_build(self):
        # the tool never builds these tasks, so a record like this is hand-written and the checker must not trust it
        for name, reason in (('ex13_pcn1_review_required_unsupported.json', 'CONTENT_USE_NOT_INTERNAL'),
                             ('ex14_pcn1_authority_named_target.json', 'AUTHORITY_NAME'),
                             ('ex15_pcn1_output_without_content_use.json', 'SNAPSHOT_INCOMPLETE')):
            task = records(self.example(name), 'task')[0]
            action = task['effects']['actions'][0]
            req = {'work_id': task['work_id'], 'target': action['targets'][0], 'intent_ref': {k: v for k, v in task['intent']['refs'][0].items() if k != 'kind'},
                   'main_interpretation': task['intent']['main_interpretation'], 'requirements': task['acceptance']['requirements'],
                   'grant_refs': [{k: v for k, v in g.items() if k != 'kind'} for g in task['authority']['grant_refs']],
                   'subject': task['authority']['subject'], 'inputs': task['inputs']}
            if 'content_use' in action:
                req['content_use'] = action['content_use']
            with self.subTest(name), self.assertRaises(pn.RequestError) as cm:
                pn.build_task(req, '0' * 32)
            self.assertEqual(cm.exception.reason, reason)

    def test_positive_example_tasks_are_what_the_tool_builds(self):
        for name in ('ex01_pcn1_working_request.json', 'ex02_pcn1_output_internal_request.json', 'ex04_pcn1_accepted_d4_complete.json'):
            task = records(self.example(name), 'task')[0]
            action = task['effects']['actions'][0]
            rid = task['task_id'][len('pcn1-'):]
            req = {'work_id': task['work_id'], 'target': action['targets'][0], 'intent_ref': {k: v for k, v in task['intent']['refs'][0].items() if k != 'kind'},
                   'main_interpretation': task['intent']['main_interpretation'], 'requirements': task['acceptance']['requirements'],
                   'grant_refs': [{k: v for k, v in g.items() if k != 'kind'} for g in task['authority']['grant_refs']],
                   'subject': task['authority']['subject'], 'inputs': task['inputs']}
            if 'content_use' in action:
                req['content_use'] = action['content_use']
            built = pn.build_task(req, rid)
            shown = {k: v for k, v in task.items() if k not in ('example_only', 'note')}
            with self.subTest(name):
                self.assertEqual(shown, built)


if __name__ == '__main__':
    unittest.main()
