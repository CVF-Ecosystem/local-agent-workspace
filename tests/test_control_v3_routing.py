"""G-02-C2/S3-C/D: routing thuần và nối binding/routing vào entry v3 (BINDING_ROUTING_ONLY) / pure routing and its wiring into the v3 entry.

Oracle độc lập: `route_rows` của EXPECTED và luật ROUTING_POLICY canonical, không lấy từ `effect.routing` tự khai của fixture.
Mọi biến thể là bản sao của ví dụ rồi sửa đúng một điều; không ghi file nào của repo. Không gate, không observer, không PASS.
Independent oracle: EXPECTED route_rows and the canonical policy, never the fixture's declared routing. Variants are copies with one change each.
"""
import copy
import importlib
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CVF = os.path.join(ROOT, '.cvf')
CHECKS = os.path.join(CVF, 'checks')
ENTRY = os.path.join(CHECKS, 'control_check_v3.py')
V3C = os.path.join(CVF, 'contracts', 'v3')
V3R = os.path.join(CVF, 'rules', 'v3')
EX_DIR = os.path.join(V3C, 'examples')
NOT_IMPL = 'CANDIDATE_EVALUATION_NOT_IMPLEMENTED'
PHASES = ('dispatch', 'effect', 'accept')
EX02 = 'ex02_pcn1_output_internal_request.json'
EX01 = 'ex01_pcn1_working_request.json'
EX04 = 'ex04_pcn1_accepted_d4_complete.json'
EX07 = 'ex07_pcn1_binding_stale.json'
EX11 = 'ex11_pcn1_direct_runtime_write.json'
EX13 = 'ex13_pcn1_review_required_unsupported.json'
EX14 = 'ex14_pcn1_authority_named_target.json'
EX15 = 'ex15_pcn1_output_without_content_use.json'


def _read_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _entry():
    import importlib.util
    spec = importlib.util.spec_from_file_location('law_cvf_entry_v3_routing_test', ENTRY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = _entry()
        cls.entry._load_package()
        cls.routing = importlib.import_module('law_cvf_check_v3.routing')
        with open(os.path.join(V3R, 'ROUTING_POLICY.json'), 'rb') as f:
            cls.policy = cls.routing.load_route_policy(f.read())
        cls.expected = _read_json(os.path.join(EX_DIR, 'EXPECTED.json'))

    def bundle(self, name):
        return _read_json(os.path.join(EX_DIR, name))

    def task_of(self, bundle):
        return [r for r in bundle['records'] if r['record_type'] == 'task'][0]

    def action_of(self, bundle):
        return self.task_of(bundle)['effects']['actions'][0]

    def route(self, task, phase='effect'):
        return self.routing.evaluate_task(task, self.policy, phase)

    def route_envelope_false_scenario(self, task, phase='effect'):
        """Counterfactual oracle only: assume envelope excess is false, without modifying the canonical policy file.

        The shipped diagnostic cannot establish that assumption; separate canonical-policy tests below keep it Unknown.
        """
        policy = copy.deepcopy(self.policy)
        external = policy.rows['R-EXTERNAL']
        external['match_any'] = [c for c in external['match_any'] if c != {'conditions_all': ['ENVELOPE_EXCEEDED']}]
        return self.routing.evaluate_task(task, policy, phase)

    def check(self, bundle, phase='effect'):
        return self.entry.check_bytes(json.dumps(bundle).encode('utf-8'), phase, 'v3')


class LexicalPaths(Base):
    def test_supported_relative_posix_forms_are_accepted_and_casefolded(self):
        ok = {
            'working/w1/a.docx': ('working', 'w1', 'a.docx'),
            'Working/W1/A.DOCX': ('working', 'w1', 'a.docx'),
            'output/b.v2.docx': ('output', 'b.v2.docx'),
            'notes/x-y_z.md': ('notes', 'x-y_z.md'),
        }
        for path, want in ok.items():
            with self.subTest(path=path):
                self.assertEqual(self.routing.lexical_segments(path), want)

    def test_unsupported_forms_are_refused_never_normalized(self):
        bad = ['', '/abs/x', 'a\\b', 'C:x', 'a:b', 'a//b', 'a/', 'a/./b', 'a/../b', '../x', 'a/b.', 'a/b ', ' a', 'a/PROGRA~1/x',
               'a/CON', 'a/nul.txt', 'a/LPT1.log', 'a/conin$', 'a/conout$.txt', 'a/x?.docx', 'a/x*.docx',
               'a/x<y', 'a/x>y', 'a/x"y', 'a/x|y', 'a/x\x01y', 'a/\x7f', 'a/b\n', None, 5]
        for path in bad:
            with self.subTest(path=path):
                self.assertIsNone(self.routing.lexical_segments(path))


class ZoneClassification(Base):
    def zone(self, path, declared='working', protected=()):
        segs = self.routing.lexical_segments(path)
        prot = [self.routing.lexical_segments(p) for p in protected]
        return self.routing.path_zone(segs, declared, self.policy, [p for p in prot if p])

    def test_baseline_zone_map_and_segment_boundaries(self):
        self.assertEqual(self.zone('working/x.docx'), 'working')
        self.assertEqual(self.zone('output/x.docx', 'output_new'), 'output_new')
        self.assertEqual(self.zone('.agent/runtime/publish/r.json', 'agent_runtime'), 'agent_runtime')
        self.assertEqual(self.zone('working2/x.docx'), 'UNCLASSIFIED', 'prefix must end on a segment boundary')
        self.assertEqual(self.zone('working'), 'UNCLASSIFIED', 'the directory itself is not a file under it')

    def test_unmapped_path_is_unclassified_even_when_declared_light(self):
        self.assertEqual(self.zone('notes/x.docx', 'working'), 'UNCLASSIFIED')
        self.assertEqual(self.zone('notes/x.docx', 'output_new'), 'UNCLASSIFIED')

    def test_declared_zone_only_raises(self):
        self.assertEqual(self.zone('working/x.docx', 'output_new'), 'output_new')
        self.assertEqual(self.zone('working/x.docx', 'framework'), 'framework')
        self.assertEqual(self.zone('working/x.docx', 'none'), 'working')

    def test_declared_unknown_is_unclassified(self):
        self.assertEqual(self.zone('working/x.docx', 'unknown'), 'UNCLASSIFIED')

    def test_authority_name_raises_to_framework_in_any_zone(self):
        self.assertEqual(self.zone('working/w1/AGENTS.md'), 'framework')
        self.assertEqual(self.zone('output/w1/routing_policy_v3.json'), 'framework')
        self.assertEqual(self.zone('working/w1/notes.md'), 'working')

    def test_protected_target_and_its_ancestors_raise_to_original_source(self):
        self.assertEqual(self.zone('working/keep/a.docx', protected=['working/keep/a.docx']), 'original_source')
        self.assertEqual(self.zone('working/keep', protected=['working/keep/a.docx']), 'original_source', 'an ancestor of a protected target is protected')
        self.assertEqual(self.zone('working/keep/a.docx', protected=['working/keep']), 'original_source')
        self.assertEqual(self.zone('working/keepsake.docx', protected=['working/keep']), 'working')


class RouteOracle(Base):
    def test_valid_examples_match_expected_route_rows_in_every_phase(self):
        for case in self.expected['cases']:
            if not case['schema_valid']:
                continue
            bundle = self.bundle(case['file'])
            for phase in PHASES:
                with self.subTest(file=case['file'], phase=phase):
                    res = self.route_envelope_false_scenario(self.task_of(bundle), phase)
                    self.assertTrue(res.evaluated)
                    definite = [r['row_id'] for r in res.rows if r['match_state'] == self.routing.T]
                    self.assertEqual(definite, case['route_rows'])

    def test_fixture_declared_routing_is_not_a_source(self):
        bundle = self.bundle(EX02)
        declared = [r for r in bundle['records'] if r['record_type'] == 'effect'][0]['routing']
        self.assertEqual(declared['matched_rows'], ['R-READ_DRAFT'])
        for changed in (['R-HIGH_STAKES'], ['R-MUTATION'], []):
            with self.subTest(changed=changed):
                b = copy.deepcopy(bundle)
                [r for r in b['records'] if r['record_type'] == 'effect'][0]['routing']['matched_rows'] = changed
                self.assertEqual(list(self.route_envelope_false_scenario(self.task_of(b)).matched), ['R-READ_DRAFT'])

    def test_stage_is_not_authority_and_read_is_not_a_write(self):
        bundle = self.bundle(EX02)
        action = self.action_of(bundle)
        action['operation'] = 'read'
        action['write_zone'] = 'none'
        res = self.route_envelope_false_scenario(self.task_of(bundle))
        self.assertEqual(list(res.matched), ['R-READ_DRAFT'])
        self.assertEqual(res.status, 'RESOLVED', 'read has no A-NEW_TARGET')
        self.assertEqual(res.assumptions, [])

    def test_a_new_target_opens_only_for_create_new_clauses_and_closes_at_accept_as_not_applicable(self):
        res = self.route_envelope_false_scenario(self.task_of(self.bundle(EX02)), 'dispatch')
        self.assertEqual((res.status, [a['status'] for a in res.assumptions]), ('CONDITIONAL', ['OPEN']))
        res = self.route_envelope_false_scenario(self.task_of(self.bundle(EX02)), 'accept')
        self.assertEqual((res.status, [a['status'] for a in res.assumptions]), ('RESOLVED', ['NOT_APPLICABLE_IN_PHASE']))


class SyntheticRows(Base):
    def run_action(self, bundle, phase='effect'):
        return self.route_envelope_false_scenario(self.task_of(bundle), phase)

    def test_declared_zone_raise_keeps_a_light_row_only_when_the_row_still_holds(self):
        b = self.bundle(EX01)
        self.action_of(b)['write_zone'] = 'output_new'
        self.assertIn('R-UNCLASSIFIED', self.run_action(b).matched, 'output_new needs content_use internal, which EX01 lacks')
        self.action_of(b)['content_use'] = ['internal_draft']
        self.assertEqual(list(self.run_action(b).matched), ['R-READ_DRAFT'])

    def test_declared_framework_and_unknown_never_become_light(self):
        for declared in ('framework', 'unknown'):
            with self.subTest(declared=declared):
                b = self.bundle(EX01)
                self.action_of(b)['write_zone'] = declared
                self.assertEqual(list(self.run_action(b).matched), ['R-UNCLASSIFIED'])

    def test_unmapped_target_declared_working_is_unclassified(self):
        b = self.bundle(EX01)
        self.action_of(b)['targets'] = ['notes/bao-cao.docx']
        res = self.run_action(b)
        self.assertEqual((list(res.matched), res.status), (['R-UNCLASSIFIED'], 'UNRESOLVED'))
        self.assertIn('UNCLASSIFIED_OPERATION', res.blocked)

    def test_write_declared_none_or_without_target_is_unclassified(self):
        b = self.bundle(EX01)
        self.action_of(b)['write_zone'] = 'none'
        self.assertIn('R-UNCLASSIFIED', self.run_action(b).matched)
        b = self.bundle(EX01)
        self.action_of(b)['targets'] = []
        self.assertEqual(list(self.run_action(b).matched), ['R-UNCLASSIFIED'])

    def test_read_declared_anything_but_none_is_unclassified(self):
        b = self.bundle(EX01)
        self.action_of(b)['operation'] = 'read'
        self.action_of(b)['write_zone'] = 'none'
        self.assertEqual(list(self.run_action(b).matched), ['R-READ_DRAFT'], 'a read with declared none is the light read row')
        self.action_of(b)['write_zone'] = 'working'
        self.assertIn('R-UNCLASSIFIED', self.run_action(b).matched, 'a read declaring a zone is a contradiction')

    def test_missing_content_use_is_unknown_for_output_but_not_for_working(self):
        self.assertIn('R-UNCLASSIFIED', self.run_action(self.bundle(EX15)).matched)
        self.assertEqual(list(self.run_action(self.bundle(EX01)).matched), ['R-READ_DRAFT'])

    def test_sign_content_routes_high_stakes_and_review_is_reported_not_lowered(self):
        res = self.run_action(self.bundle(EX13))
        self.assertIn('R-HIGH_STAKES', res.matched)
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', res.blocked)
        self.assertEqual(res.review_phases, ('PRE_DELIVERY',))

    def test_agent_runtime_create_is_mutation_with_review_not_the_light_row(self):
        res = self.run_action(self.bundle(EX11))
        self.assertIn('R-MUTATION', res.matched)
        self.assertEqual(res.review_phases, ('PRE_EFFECT', 'PRE_INTEGRATION'))
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', res.blocked)

    def test_authority_named_working_target_has_no_row_and_is_unmatched(self):
        res = self.run_action(self.bundle(EX14))
        self.assertEqual((list(res.matched), res.status), (['R-UNCLASSIFIED'], 'UNRESOLVED'))

    def test_overwrite_goes_to_mutation_and_delete_is_never_light(self):
        b = self.bundle(EX01)
        self.action_of(b)['operation'] = 'overwrite'
        res = self.run_action(b)
        self.assertIn('R-MUTATION', res.matched)
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', res.blocked)

    def test_delegate_and_external_send_rows(self):
        b = self.bundle(EX01)
        self.action_of(b)['operation'] = 'delegate'
        self.action_of(b)['targets'] = []
        self.action_of(b)['write_zone'] = 'none'
        res = self.run_action(b)
        self.assertEqual((list(res.matched), res.status), (['R-DELEGATE'], 'RESOLVED'))
        b = self.bundle(EX01)
        self.action_of(b)['operation'] = 'external_send'
        res = self.run_action(b)
        self.assertIn('R-EXTERNAL', res.matched)
        self.assertIn('REVIEW_REQUIRED_UNSUPPORTED', res.blocked)

    def test_unknown_operation_is_unclassified(self):
        b = self.bundle(EX01)
        self.action_of(b)['operation'] = 'unknown'
        res = self.run_action(b)
        self.assertEqual((list(res.matched), res.status), (['R-UNCLASSIFIED'], 'UNRESOLVED'))

    def test_known_loss_is_forced_deny_and_unknown_loss_is_not_false(self):
        b = self.bundle(EX02)
        self.task_of(b)['effects']['preservation'] = [{'target': 'output/w-20261018-01/bao-cao-nhap.docx', 'must_keep': 'tables',
                                                       'known_loss_state': 'KNOWN_LOSS'}]
        res = self.run_action(b)
        self.assertEqual(list(res.matched), ['R-READ_DRAFT', 'R-KNOWN_LOSS'], 'known loss is forced beside the union, it does not replace it')
        self.assertEqual(res.deny, ['KNOWN_PRESERVATION_LOSS'])
        b = self.bundle(EX02)
        self.task_of(b)['effects']['preservation'] = [{'target': 'output/w-20261018-01/bao-cao-nhap.docx', 'must_keep': 'tables',
                                                       'known_loss_state': 'UNKNOWN'}]
        res = self.run_action(b)
        self.assertIn('R-UNCLASSIFIED', res.matched)
        self.assertEqual(next(r['match_state'] for r in res.rows if r['row_id'] == 'R-KNOWN_LOSS'), self.routing.U)
        self.assertEqual(res.deny, [], 'a possible known-loss row must not force DENY')
        self.assertIn('PRESERVATION_UNKNOWN', res.blocked)
        b = self.bundle(EX02)
        self.task_of(b)['effects']['preservation'] = [{'target': 'output/w-20261018-01/bao-cao-nhap.docx', 'must_keep': 'tables',
                                                       'known_loss_state': 'NONE_KNOWN'}]
        self.assertEqual(list(self.run_action(b).matched), ['R-READ_DRAFT'])

    def test_missing_grant_is_unclassified_and_recipe_is_unsupported_not_light(self):
        b = self.bundle(EX02)
        self.task_of(b)['authority']['grant_refs'] = []
        res = self.run_action(b)
        self.assertIn('R-UNCLASSIFIED', res.matched)
        b = self.bundle(EX02)
        self.action_of(b)['recipe'] = {'recipe_id': 'r1', 'recipe_version': '1', 'acceptance_ref': {}, 'user_decision_effect': 'NONE'}
        res = self.run_action(b)
        self.assertIn('R-UNCLASSIFIED', res.matched)
        self.assertIn('RECIPE_NOT_IN_CANDIDATE', res.unsupported)

    def test_unsupported_path_form_is_reported_as_unsupported(self):
        b = self.bundle(EX02)
        self.action_of(b)['targets'] = ['output/../escape.docx']
        res = self.run_action(b)
        self.assertEqual(list(res.matched), ['R-UNCLASSIFIED'])
        self.assertIn('PATH_UNSUPPORTED_FORM', res.unsupported)

    def test_multi_action_is_not_invented_into_one_route(self):
        b = self.bundle(EX02)
        extra = copy.deepcopy(self.action_of(b))
        self.task_of(b)['effects']['actions'].append(extra)
        res = self.run_action(b)
        self.assertFalse(res.evaluated)
        self.assertEqual(res.rows, [])
        self.assertEqual(res.unsupported, ['MULTI_ACTION_UNSUPPORTED'])


class ConservativeCanonicalRouting(Base):
    def test_unknown_envelope_preserves_possible_external_obligations_in_every_phase(self):
        task = self.task_of(self.bundle(EX01))
        for phase in PHASES:
            with self.subTest(phase=phase):
                result = self.route(task, phase)
                rows = {r['row_id']: r for r in result.rows}
                self.assertEqual((result.status, rows['R-EXTERNAL']['match_state']), ('UNRESOLVED', self.routing.U))
                self.assertEqual(rows['R-READ_DRAFT']['match_state'], self.routing.T,
                                 'a definite light match still cannot override the unresolved union')
                self.assertIn('R-UNCLASSIFIED', rows)
                expected = self.policy.rows['R-EXTERNAL']
                self.assertEqual(rows['R-EXTERNAL']['required_gates'], expected['required_gates'])
                self.assertTrue(set(expected['required_review_phases']) <= set(result.review_phases))
                self.assertIn('ENVELOPE_EXCEEDED', rows['R-EXTERNAL']['not_evaluated_conditions'])
                self.assertEqual(result.deny, [], 'an unknown condition never forces DENY')

    def test_true_and_unknown_rows_union_without_turning_unknown_known_loss_into_deny(self):
        task = self.task_of(self.bundle(EX13))
        task['effects']['preservation'] = [{'target': task['effects']['actions'][0]['targets'][0],
                                          'must_keep': 'tables', 'known_loss_state': 'UNKNOWN'}]
        result = self.route(task)
        rows = {r['row_id']: r for r in result.rows}
        self.assertEqual(rows['R-HIGH_STAKES']['match_state'], self.routing.T)
        self.assertEqual(rows['R-KNOWN_LOSS']['match_state'], self.routing.U)
        self.assertEqual(set(result.review_phases), {'PRE_DELIVERY', 'PRE_EFFECT', 'PRE_INTEGRATION'})
        self.assertEqual(result.deny, [])
        self.assertIn('PRESERVATION_UNKNOWN', result.blocked)

    def test_known_loss_still_vetoes_when_multiple_actions_are_unsupported(self):
        task = self.task_of(self.bundle(EX01))
        task['effects']['actions'].append(copy.deepcopy(task['effects']['actions'][0]))
        task['effects']['preservation'] = [{'target': task['effects']['actions'][0]['targets'][0],
                                          'must_keep': 'tables', 'known_loss_state': 'KNOWN_LOSS'}]
        result = self.route(task)
        self.assertFalse(result.evaluated, 'this does not implement multi-action routing')
        self.assertEqual(result.unsupported, ['MULTI_ACTION_UNSUPPORTED'])
        self.assertEqual(result.deny, ['KNOWN_PRESERVATION_LOSS'])


class EntryWiring(Base):
    def test_binding_mismatch_is_blocked_not_hidden(self):
        res = self.check(self.bundle(EX07), 'accept')
        self.assertEqual(res['disposition'], 'BLOCKED')
        self.assertIn('BINDING_MISMATCH', res['reasons'])
        self.assertIs(res['coverage']['binding_evaluated'], True)

    def test_known_loss_gives_deny_and_route_says_so(self):
        b = self.bundle(EX04)
        self.task_of(b)['effects']['preservation'] = [{'target': 'working/w-20261018-01/bao-cao-nhap.docx', 'must_keep': 'tables',
                                                       'known_loss_state': 'KNOWN_LOSS'}]
        res = self.check(b, 'accept')
        self.assertEqual(res['disposition'], 'DENY')
        self.assertIn('KNOWN_PRESERVATION_LOSS', res['reasons'])
        self.assertIs(res['effect_authorized'], False)
        self.assertIn('R-KNOWN_LOSS', [r['row_id'] for r in res['route']['rows']])

    def test_unsupported_path_form_gives_unsupported_disposition(self):
        b = self.bundle(EX02)
        self.action_of(b)['targets'] = ['output/../escape.docx']
        res = self.check(b)
        self.assertEqual(res['disposition'], 'UNSUPPORTED')
        self.assertIn('PATH_UNSUPPORTED_FORM', res['reasons'])
        self.assertNotIn(NOT_IMPL, res['reasons'])

    def test_conflicting_inline_grant_claims_block(self):
        b = self.bundle(EX02)
        grant = [r for r in b['records'] if r['record_type'] == 'grant'][0]
        grant['issuer_ref']['digest'] = 'sha256:' + '1' * 64
        res = self.check(b)
        self.assertIn('REF_CONFLICT', res['reasons'])
        self.assertEqual(res['disposition'], 'BLOCKED')

    def test_grant_record_missing_is_grant_missing_not_a_pass(self):
        b = self.bundle(EX02)
        b['records'] = [r for r in b['records'] if r['record_type'] != 'grant']
        res = self.check(b)
        self.assertIn('GRANT_MISSING', res['reasons'])
        self.assertNotIn(res['disposition'], ('PASS', 'NOT_APPLICABLE'))

    def test_declared_routing_mismatch_is_reported_and_never_replaces_the_route(self):
        b = self.bundle(EX02)
        [r for r in b['records'] if r['record_type'] == 'effect'][0]['routing']['matched_rows'] = ['R-MUTATION']
        res = self.check(b)
        self.assertIn('ROUTE_DECLARED_MISMATCH', res['reasons'])
        self.assertEqual({r['row_id']: r['match_state'] for r in res['route']['rows']},
                         {'R-READ_DRAFT': self.routing.T, 'R-EXTERNAL': self.routing.U, 'R-UNCLASSIFIED': self.routing.T})

    def test_two_tasks_do_not_pick_one_for_routing(self):
        b = self.bundle(EX02)
        twin = copy.deepcopy(self.task_of(b))
        twin['task_id'] = 'pcn1-twin'
        b['records'].append(twin)
        res = self.check(b)
        self.assertIn('MULTI_TASK_UNSUPPORTED', res['reasons'])
        self.assertIs(res['coverage']['routing_evaluated'], False)
        self.assertEqual(res['route']['evaluated'], False)


if __name__ == '__main__':
    unittest.main()
