"""Focused tests for .cvf/checks/control_check.py (G-02).

These tests prove checker logic on synthetic records only. They do not prove live governance,
host enforcement, a trusted verifier or real file observation. jsonschema is a hard
requirement: a missing validator fails these tests loudly instead of skipping them.
"""
import ast
import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / '.cvf' / 'checks'
EXAMPLES = ROOT / '.cvf' / 'contracts' / 'examples'
sys.path.insert(0, str(CHECKS))
import control_check as cc  # noqa: E402

SV = cc.SCHEMA_VERSION
PHASE_OF = {
    'ex01_draft_in_grant.json': 'effect', 'ex02_mutation_reviewed_bound.json': 'effect',
    'ex05_binding_changed.json': 'effect', 'ex06_reviewer_blocked_then_accepted.json': 'accept',
    'ex07_output_changed_after_review.json': 'accept', 'ex08_main_rewrote_intent.json': 'effect',
    'ex09_self_declared_reviewer.json': 'effect', 'ex11_known_preservation_loss.json': 'effect',
    'ex14_recipe_accepted_no_decision_change.json': 'effect', 'ex15_recipe_changes_user_decision.json': 'effect',
    'ex16_recipe_decision_effect_unknown.json': 'effect', 'ex17_delegate_full_descriptor.json': 'effect',
    'ex19_delegate_context_only.json': 'effect',
}


def ex(name):
    return json.loads((EXAMPLES / name).read_text(encoding='utf-8'))


def run(bundle, phase, **kw):
    out = cc.check(bundle, phase, **kw)
    assert out['effect_authorized'] is False
    assert all(o['effect_authorized'] is False for o in out['objects'])
    return out


def reasons_of(out):
    got = set(out['reasons'])
    for o in out['objects']:
        got.update(o['reasons'])
    return got


def only(out):
    assert len(out['objects']) == 1, out['objects']
    return out['objects'][0]


def gate(obj, name):
    return obj['gates'][name]['status']


def recs(bundle, rt):
    return [r for r in bundle['records'] if r['record_type'] == rt]


def bundle_of(*records):
    return {'schema_version': SV, 'record_type': 'bundle', 'bundle_id': 'TEST-bundle', 'records': list(records)}


def active_grant(ref, roles, ops, tools, paths, callees=None, limits=None):
    g = {'schema_version': SV, 'record_type': 'grant', 'grant_id': 'TEST-grant-1', 'grant_revision': 1,
         'issuer': {'actor_id': 'EXAMPLE-user', 'role': 'user'}, 'issuer_ref': ref,
         'subject': {'roles': roles}, 'scope': {'task_classes': ['TEST'], 'operations': ops, 'tools': tools, 'paths': paths},
         'status': 'ACTIVE'}
    if callees is not None:
        g['scope']['delegate_callees'] = callees
    if limits:
        g['limits'] = limits
    return g


class ControlCheckBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if cc.jsonschema is None or not hasattr(cc.jsonschema, 'Draft202012Validator'):
            raise AssertionError('jsonschema with Draft 2020-12 support is required for G-02 tests; '
                                 'install it (python -m pip install "jsonschema>=4.18,<5")')


class Dependencies(ControlCheckBase):
    def test_validator_is_present_and_supports_2020_12(self):
        self.assertTrue(hasattr(cc.jsonschema, 'Draft202012Validator'))

    def test_source_stays_python38_syntax(self):
        ast.parse((CHECKS / 'control_check.py').read_text(encoding='utf-8'), feature_version=(3, 8))

    def test_executable_never_reads_the_expected_oracle(self):
        text = (CHECKS / 'control_check.py').read_text(encoding='utf-8')
        self.assertNotIn('EXPECTED', text)
        self.assertNotIn('examples', text.replace('.cvf/contracts', ''))

    def test_missing_validator_is_unsupported_not_a_fallback(self):
        with mock.patch.object(cc, 'jsonschema', None):
            out = cc.check(ex('ex01_draft_in_grant.json'), 'effect')
        self.assertEqual(out['disposition'], 'UNSUPPORTED')
        self.assertIn('DEPENDENCY_MISSING', out['reasons'])
        self.assertFalse(out['effect_authorized'])
        self.assertEqual(out['coverage']['objects_examined'], 0)
        self.assertEqual(cc.exit_code(out), 2)


class ExamplesOracle(ControlCheckBase):
    """EXPECTED.json is read only here, as the oracle; the executable never sees it."""

    def test_examples_match_current_expectations(self):
        expected = json.loads((EXAMPLES / 'EXPECTED.json').read_text(encoding='utf-8'))
        for case in expected['cases']:
            with self.subTest(case['file']):
                bundle = ex(case['file'])
                if not case['schema_valid']:
                    out = run(bundle, 'effect')
                    self.assertIn(out['disposition'], ('DENY', 'UNSUPPORTED'))
                    self.assertTrue({'SCHEMA_INVALID', 'SCHEMA_VERSION_UNKNOWN'} & set(out['reasons']))
                    self.assertEqual(out['objects'], [])
                    continue
                out = run(bundle, PHASE_OF[case['file']])
                want = case['expected_current']
                self.assertEqual(out['disposition'], want['disposition'])
                self.assertTrue(set(want['reasons']) <= reasons_of(out), (want['reasons'], reasons_of(out)))
                self.assertNotEqual(out['disposition'], 'PASS')

    def test_result_does_not_depend_on_fixture_names_or_ids(self):
        original = ex('ex08_main_rewrote_intent.json')
        renamed = json.loads(json.dumps(original).replace('EXAMPLE-', 'ZZ-').replace('ex08', 'fixture-x'))
        a, b = run(original, 'effect'), run(renamed, 'effect')
        self.assertEqual(a['disposition'], b['disposition'])
        self.assertEqual(sorted(reasons_of(a)), sorted(reasons_of(b)))

    def test_no_object_in_phase_is_not_applicable_and_never_pass(self):
        out = run(ex('ex06_reviewer_blocked_then_accepted.json'), 'effect')  # no effect records
        self.assertEqual(out['disposition'], 'NOT_APPLICABLE')
        self.assertEqual(out['coverage']['objects_examined'], 0)
        self.assertEqual(cc.exit_code(out), 3)

    def test_every_output_states_what_was_not_observed(self):
        out = run(ex('ex02_mutation_reviewed_bound.json'), 'effect')
        cov = out['coverage']
        self.assertFalse(cov['artifact_bytes_observed'])
        self.assertFalse(cov['actual_operation_observed'])
        self.assertTrue(cov['digests_compared_between_records_only'])
        self.assertFalse(out['canonical_bytes_verified'])
        self.assertEqual(out['owner_protection'], 'NOT_PROVEN')


class SafetyAndRouting(ControlCheckBase):
    def draft_bundle(self, target='working/EXAMPLE-work-1/ban-nhap.md', zone='working', protected=None, paths=None):
        b = ex('ex01_draft_in_grant.json')
        for r in b['records']:
            r.pop('example_only', None)
        grant = recs(b, 'grant')[0]
        grant['status'] = 'ACTIVE'
        if paths is not None:
            grant['scope']['paths'] = paths
        task, effect = recs(b, 'task')[0], recs(b, 'effect')[0]
        effect['grant_ref_ids'] = ['EXAMPLE-grant-ref-1']
        action = effect['action']
        action['targets'] = [target]
        action['write_zone'] = zone
        task['effects']['actions'] = [copy.deepcopy(action)]
        if protected is not None:
            task['effects']['protected_targets'] = protected
        return b

    def test_cooperative_draft_is_consistent_but_not_a_safety_pass(self):
        out = run(self.draft_bundle(), 'effect')
        obj = only(out)
        self.assertEqual(obj['record_consistency']['status'], 'CONSISTENT')
        self.assertEqual(obj['record_consistency']['level'], 'ADVISORY')
        self.assertEqual(obj['disposition'], 'BLOCKED')
        self.assertIn('PROTECTED_TARGET_UNDETERMINED', obj['reasons'])
        self.assertIn('R-READ_DRAFT', obj['routes']['possible'])
        self.assertNotIn('R-READ_DRAFT', obj['routes']['matched'])
        self.assertEqual(cc.exit_code(out), 1)

    def test_narrow_self_declared_scope_never_makes_the_light_route_true(self):
        out = run(self.draft_bundle(target='references/_INDEX.xlsx', zone='working', protected=[]), 'effect')
        obj = only(out)
        self.assertNotIn('R-READ_DRAFT', obj['routes']['matched'])
        self.assertEqual(obj['disposition'], 'BLOCKED')
        self.assertIn('PROTECTED_TARGET_UNDETERMINED', obj['reasons'])

    def test_record_showing_a_protected_or_heavy_target_leaves_the_light_route(self):
        out = run(self.draft_bundle(target='References./x.md', zone='working', protected=['references/']), 'effect')
        obj = only(out)
        self.assertNotIn('R-READ_DRAFT', obj['routes']['matched'] + obj['routes']['possible'])
        out2 = run(self.draft_bundle(zone='original_source'), 'effect')
        self.assertNotIn('R-READ_DRAFT', only(out2)['routes']['matched'] + only(out2)['routes']['possible'])

    def test_similar_looking_path_is_outside_the_grant(self):
        out = run(self.draft_bundle(target='working-evil/x.md', paths=['working/']), 'effect')
        self.assertIn('GRANT_OUT_OF_SCOPE', only(out)['reasons'])
        self.assertEqual(only(out)['record_consistency']['status'], 'INCONSISTENT')

    def test_path_helpers_reject_untrusted_paths_and_prefix_tricks(self):
        self.assertFalse(cc._covered(['references-evil/x'], ['references/']))
        self.assertTrue(cc._covered(['references/a/b'], ['references/']))
        self.assertFalse(cc._covered(['References/a'], ['references/']))  # grant coverage is exact case
        self.assertFalse(cc._covered(['references/a'], []))  # empty allowed list = none
        for bad in ('', '/abs', 'C:/x', 'a\\b', 'a/../b', './a', 'a\x00b'):
            self.assertIsNone(cc._segments(bad), bad)

    def test_route_is_a_union_and_main_cannot_declare_it_down(self):
        b = ex('ex11_known_preservation_loss.json')
        out = run(b, 'effect')
        obj = only(out)
        self.assertIn('R-KNOWN_LOSS', obj['routes']['matched'])
        self.assertIn('R-MUTATION', obj['routes']['matched'])
        self.assertEqual(obj['routes']['claimed_by_main'], ['R-KNOWN_LOSS', 'R-MUTATION'])
        effect = recs(b, 'effect')[0]
        effect['routing']['matched_rows'] = ['R-READ_DRAFT']
        again = only(run(b, 'effect'))
        self.assertIn('ROUTE_UNDERSTATED', again['reasons'])
        self.assertIn('R-MUTATION', again['routes']['matched'])
        self.assertEqual(again['disposition'], 'DENY')

    def test_known_loss_is_denied_before_any_approval_even_with_simulated_trust(self):
        out = run(ex('ex11_known_preservation_loss.json'), 'effect', verifier=cc.SimulatedVerifier())
        self.assertEqual(only(out)['disposition'], 'DENY')
        self.assertIn('KNOWN_PRESERVATION_LOSS', only(out)['reasons'])

    def test_unknown_operation_and_zone_are_unclassified_not_light(self):
        b = self.draft_bundle()
        effect = recs(b, 'effect')[0]
        effect['action']['operation'] = 'unknown'
        task = recs(b, 'task')[0]
        task['effects']['actions'] = [copy.deepcopy(effect['action'])]
        obj = only(run(b, 'effect'))
        self.assertIn('R-UNCLASSIFIED', obj['routes']['matched'])
        self.assertIn('UNCLASSIFIED_OPERATION', obj['reasons'])
        self.assertEqual(obj['disposition'], 'BLOCKED')


class RecipeConditions(ControlCheckBase):
    def effect_obj(self, name, **kw):
        return only(run(ex(name), 'effect', **kw))

    def attest(self, name, **facts):
        recipe = recs(ex(name), 'task')[0]['effects']['actions'][0]['recipe']
        base = {'recipe_id': recipe['recipe_id'], 'recipe_version': recipe['recipe_version']}
        base.update(facts)
        return cc.SimulatedVerifier(facts={recipe['acceptance_ref']['ref_id']: base})

    def test_claimed_no_change_does_not_open_the_recipe_route(self):
        obj = self.effect_obj('ex14_recipe_accepted_no_decision_change.json')
        self.assertNotIn('R-RECIPE', obj['routes']['matched'])
        self.assertIn('R-RECIPE', obj['routes']['possible'])
        self.assertEqual(obj['disposition'], 'BLOCKED')
        self.assertIn('TRUSTED_VERIFICATION_UNAVAILABLE', obj['reasons'])

    def test_claimed_change_goes_heavier(self):
        obj = self.effect_obj('ex15_recipe_changes_user_decision.json')
        self.assertNotIn('R-RECIPE', obj['routes']['matched'])
        self.assertIn('R-MUTATION', obj['routes']['possible'] + obj['routes']['matched'])
        self.assertIn('REVIEW_MISSING', obj['reasons'])

    def test_unknown_effect_is_unclassified(self):
        obj = self.effect_obj('ex16_recipe_decision_effect_unknown.json')
        self.assertIn('R-UNCLASSIFIED', obj['routes']['matched'])
        self.assertIn('UNCLASSIFIED_OPERATION', obj['reasons'])

    def test_only_a_verifier_attestation_can_make_the_light_recipe_route_true(self):
        name = 'ex14_recipe_accepted_no_decision_change.json'
        obj = self.effect_obj(name, verifier=self.attest(name, user_decision_effect='NONE'))
        self.assertIn('R-RECIPE', obj['routes']['matched'])
        self.assertNotIn('R-MUTATION', obj['routes']['matched'])
        self.assertEqual(obj['required_review_phases'], [])  # recipe row needs no per-file review
        self.assertEqual(obj['disposition'], 'BLOCKED')  # simulated verifier is capped
        self.assertIn('SIMULATED_VERIFIER_NOT_AUTHORITY', obj['reasons'])

    def test_attested_change_or_version_mismatch_goes_to_mutation(self):
        name = 'ex14_recipe_accepted_no_decision_change.json'
        changed = self.effect_obj(name, verifier=self.attest(name, user_decision_effect='CHANGES'))
        self.assertIn('R-MUTATION', changed['routes']['matched'])
        self.assertNotIn('R-RECIPE', changed['routes']['matched'])
        wrong = self.effect_obj(name, verifier=self.attest(name, recipe_version='9.9.9', user_decision_effect='NONE'))
        self.assertIn('R-MUTATION', wrong['routes']['matched'])

    def test_recipe_accepted_by_main_declared_source_is_not_accepted(self):
        b = ex('ex14_recipe_accepted_no_decision_change.json')
        for record in b['records']:
            if record['record_type'] == 'task':
                record['effects']['actions'][0]['recipe']['acceptance_ref']['trust_anchor'] = 'MAIN_DECLARED'
            if record['record_type'] == 'effect':
                record['action']['recipe']['acceptance_ref']['trust_anchor'] = 'MAIN_DECLARED'
        obj = only(run(b, 'effect'))
        self.assertIn('R-MUTATION', obj['routes']['matched'])
        self.assertNotIn('R-RECIPE', obj['routes']['matched'])


def consistent_mutation():
    """ex02 plus an active grant covering its single action. Still synthetic."""
    b = ex('ex02_mutation_reviewed_bound.json')
    task = recs(b, 'task')[0]
    grant = active_grant(task['authority']['grant_refs'][0], ['worker'], ['provenance_write'],
                         ['EXAMPLE-editor'], ['references/'])
    b['records'].insert(0, grant)
    return b


class AuthorityAndBinding(ControlCheckBase):
    def consistent_mutation(self):
        return consistent_mutation()

    def test_default_verifier_never_opens_trusted_rows(self):
        out = run(self.consistent_mutation(), 'effect')
        obj = only(out)
        self.assertEqual(obj['disposition'], 'BLOCKED')
        self.assertIn('TRUSTED_VERIFICATION_UNAVAILABLE', obj['reasons'])
        self.assertTrue(all(t['checked'] != 'VERIFIED' for t in obj['trusted_refs']))
        self.assertEqual(out['verifier']['trust_basis'], 'NONE')

    def test_records_claiming_verified_do_not_count_as_verified(self):
        obj = only(run(self.consistent_mutation(), 'effect'))
        claimed = [t['claimed_verification'] for t in obj['trusted_refs']]
        self.assertIn('VERIFIED', claimed)  # the records say so...
        self.assertTrue(all(t['checked'] != 'VERIFIED' for t in obj['trusted_refs']))  # ...and it is ignored

    def test_simulated_trust_exercises_logic_but_is_capped_and_never_observes(self):
        out = run(self.consistent_mutation(), 'effect', verifier=cc.SimulatedVerifier())
        obj = only(out)
        self.assertEqual(out['verifier']['trust_basis'], 'SIMULATED')
        self.assertTrue(all(t['checked'] == 'VERIFIED' for t in obj['trusted_refs']))
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'MET')
        self.assertEqual(gate(obj, 'BINDING'), 'MET')
        self.assertEqual(gate(obj, 'GRANT_SCOPE'), 'MET')
        self.assertEqual(gate(obj, 'INPUT_REVISION'), 'NOT_CHECKED')
        self.assertEqual(gate(obj, 'PRESERVATION'), 'NOT_CHECKED')
        self.assertIn('SIMULATED_VERIFIER_NOT_AUTHORITY', obj['reasons'])
        self.assertIn('OBSERVATION_UNAVAILABLE', obj['reasons'])
        self.assertNotIn('TRUSTED_VERIFICATION_UNAVAILABLE', obj['reasons'])
        self.assertEqual(obj['disposition'], 'BLOCKED')

    def test_main_rewritten_intent_is_untrusted_even_with_matching_hashes(self):
        obj = only(run(ex('ex08_main_rewrote_intent.json'), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('INTENT_NOT_TRUSTED', obj['reasons'])
        self.assertEqual(obj['disposition'], 'BLOCKED')

    def test_self_declared_reviewer_is_not_eligible(self):
        obj = only(run(ex('ex09_self_declared_reviewer.json'), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('REVIEWER_ELIGIBILITY_UNTRUSTED', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'UNMET')

    def test_reviewer_who_is_the_proposer_or_wrong_role_is_not_eligible(self):
        b = self.consistent_mutation()
        review = [r for r in recs(b, 'review') if r['phase'] == 'PRE_EFFECT'][0]
        review['reviewer']['actor']['actor_id'] = 'EXAMPLE-main'
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('REVIEWER_ELIGIBILITY_UNTRUSTED', obj['reasons'])

    def test_review_that_did_not_check_the_users_intent_is_incomplete(self):
        b = self.consistent_mutation()
        review = [r for r in recs(b, 'review') if r['phase'] == 'PRE_EFFECT'][0]
        review['scope']['intent_refs_checked'] = ['SOMETHING-ELSE']
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('REVIEW_SCOPE_INCOMPLETE', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'UNMET')

    def test_missing_review_never_falls_back_to_main_self_review(self):
        b = self.consistent_mutation()
        b['records'] = [r for r in b['records'] if r['record_type'] != 'review']
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('REVIEW_MISSING', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'UNMET')

    def test_changed_input_makes_the_old_review_stale(self):
        obj = only(run(ex('ex05_binding_changed.json'), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('STALE_REVIEW', obj['reasons'])
        self.assertIn('BINDING_MISMATCH', obj['reasons'])
        self.assertEqual(gate(obj, 'BINDING'), 'UNMET')

    def test_blocking_review_cannot_be_outvoted_by_a_second_pass(self):
        b = ex('ex06_reviewer_blocked_then_accepted.json')
        blocked = [r for r in recs(b, 'review') if r['verdict'] == 'BLOCKED'][0]
        good = copy.deepcopy(blocked)
        good['review_id'] = 'EXAMPLE-review-extra'
        good['verdict'] = 'PASS'
        good['findings'] = []
        b['records'].append(good)
        out = run(b, 'accept', verifier=cc.SimulatedVerifier())
        self.assertEqual(only(out)['disposition'], 'DENY')
        self.assertIn('REVIEW_BLOCKING_VERDICT', only(out)['reasons'])

    def test_output_changed_after_review_is_stale(self):
        obj = only(run(ex('ex07_output_changed_after_review.json'), 'accept', verifier=cc.SimulatedVerifier()))
        self.assertIn('STALE_REVIEW', obj['reasons'])

    def test_duplicate_ids_block_everything(self):
        b = ex('ex02_mutation_reviewed_bound.json')
        b['records'].append(copy.deepcopy(recs(b, 'task')[0]))
        out = run(b, 'effect')
        self.assertIn('REF_AMBIGUOUS', out['reasons'])
        self.assertIn('REF_AMBIGUOUS', only(out)['reasons'])
        self.assertEqual(only(out)['disposition'], 'BLOCKED')

    def test_unresolved_task_reference_is_reported(self):
        b = ex('ex02_mutation_reviewed_bound.json')
        b['records'] = [r for r in b['records'] if r['record_type'] != 'task']
        self.assertIn('REF_UNRESOLVED', only(run(b, 'effect'))['reasons'])

    def test_retry_after_unknown_outcome_is_not_reissued(self):
        b = self.consistent_mutation()
        request = recs(b, 'effect')[0]
        outcome = copy.deepcopy(request)
        outcome['effect_id'] = 'EXAMPLE-effect-outcome'
        outcome['stage'] = 'OUTCOME'
        outcome['outcome'] = {'status': 'UNKNOWN', 'observed_by': {'actor_id': 'EXAMPLE-main', 'role': 'main'}}
        b['records'].append(outcome)
        out = run(b, 'effect', verifier=cc.SimulatedVerifier())
        self.assertEqual(len(out['objects']), 1)  # only the REQUEST is a checked object
        self.assertIn('RETRY_UNRECONCILED', only(out)['reasons'])


class EnvelopeAndAccept(ControlCheckBase):
    def grant_bundle(self, limits, envelope_value, status='REQUESTED'):
        b = consistent_mutation()
        recs(b, 'grant')[0]['limits'] = limits
        recs(b, 'task')[0]['envelope']['max_concurrency'] = {'value': envelope_value, 'status': status}
        return b

    def test_envelope_over_the_grant_limit_is_exceeded(self):
        obj = only(run(self.grant_bundle({'max_concurrency': 2}, 5), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('ENVELOPE_EXCEEDED', obj['reasons'])

    def test_unmeasured_limit_is_not_treated_as_satisfied(self):
        obj = only(run(self.grant_bundle({'max_concurrency': 2}, None, 'UNKNOWN'), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('ENVELOPE_UNMEASURED', obj['reasons'])
        self.assertEqual(gate(obj, 'ENVELOPE'), 'NOT_CHECKED')
        self.assertEqual(obj['disposition'], 'BLOCKED')

    def test_future_gates_are_not_yet_due_but_current_unobserved_gates_block(self):
        obj = only(run(ex('ex14_recipe_accepted_no_decision_change.json'), 'effect'))
        self.assertEqual(gate(obj, 'ACTUAL_OUTCOME'), 'NOT_YET_DUE')
        self.assertEqual(gate(obj, 'INPUT_REVISION'), 'NOT_CHECKED')

    def accept_bundle(self):
        return consistent_mutation()

    def test_accept_never_trusts_observed_labels_on_evidence(self):
        b = self.accept_bundle()
        for kind in ('TOOL_OBSERVED', 'HOST_OBSERVED', 'REVIEWER_OBSERVED'):
            res = recs(b, 'result')[0]
            res['evidence'][0]['kind'] = kind
            obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
            self.assertIn('EVIDENCE_NOT_VERIFIED', obj['reasons'], kind)
            self.assertEqual(gate(obj, 'REQUIREMENTS'), 'NOT_CHECKED', kind)
            self.assertEqual(gate(obj, 'ACTUAL_OUTCOME'), 'NOT_CHECKED', kind)
            self.assertNotEqual(obj['disposition'], 'PASS')

    def test_missing_mandatory_requirement_is_not_met(self):
        b = self.accept_bundle()
        res = recs(b, 'result')[0]
        res['acceptance_states'] = ['CANDIDATE']
        res['requirements'][0]['status'] = 'MISSING'
        obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
        self.assertIn('MANDATORY_REQUIREMENT_NOT_MET', obj['reasons'])
        self.assertEqual(gate(obj, 'REQUIREMENTS'), 'UNMET')

    def test_evidence_pointing_at_the_wrong_requirement_is_invalid(self):
        b = self.accept_bundle()
        recs(b, 'result')[0]['evidence'][0]['req_id'] = 'REQ-OTHER'
        self.assertIn('EVIDENCE_REFERENCE_INVALID', only(run(b, 'accept'))['reasons'])

    def test_accepted_claim_is_not_supported_by_this_checker(self):
        obj = only(run(self.accept_bundle(), 'accept', verifier=cc.SimulatedVerifier()))
        self.assertIn('ACCEPTANCE_CLAIM_NOT_SUPPORTED', obj['reasons'])

    def test_actions_not_approved_by_the_task_are_reported(self):
        b = self.accept_bundle()
        extra = copy.deepcopy(recs(b, 'result')[0]['actions_performed'][0])
        extra['targets'] = ['references/other.xlsx']
        recs(b, 'result')[0]['actions_performed'].append(extra)
        self.assertIn('BINDING_MISMATCH', only(run(b, 'accept'))['reasons'])


class DelegationFixture(ControlCheckBase):
    CHILD_PATH = 'references/EXAMPLE-quy-che.docx'

    def build(self, scope_paths=None, ops=None, tools=None, callees='default', child_actions=None,
              grant_ops=None, grant_tools=None, parent_actions='default', requested_concurrency=1,
              callee=None, envelope_role=None, child_basis=True):
        base = ex('ex17_delegate_full_descriptor.json')
        grant, effect = base['records']
        grant.pop('example_only')
        grant['status'] = 'ACTIVE'
        effect['actor'] = {'actor_id': 'EXAMPLE-main', 'role': 'main'}
        grant['scope']['operations'] = grant_ops or ['read', 'delegate']
        grant['scope']['tools'] = grant_tools or ['EXAMPLE-native-subagent', 'EXAMPLE-file-read']
        grant['scope']['paths'] = ['working/', 'references/']
        d = effect['action']['delegation']
        if callee is not None:
            d['callee'] = callee
            grant['scope']['delegate_callees'] = [callee]
        if envelope_role is not None:
            d['requested_envelope']['role'] = envelope_role
        if callees != 'default':
            grant['scope']['delegate_callees'] = callees
        d['tool_scope'] = {'tools': tools if tools is not None else ['EXAMPLE-file-read'],
                           'operations': ops if ops is not None else ['read'],
                           'paths': scope_paths if scope_paths is not None else [self.CHILD_PATH]}
        d['requested_envelope']['max_concurrency'] = {'value': requested_concurrency, 'status': 'REQUESTED'}
        parent = copy.deepcopy(ex('ex02_mutation_reviewed_bound.json')['records'][0])
        parent['effects']['actions'] = [copy.deepcopy(effect['action'])] if parent_actions == 'default' else parent_actions
        parent['effects']['preservation'] = []
        child = copy.deepcopy(parent)
        child['task_id'] = d['child_task']['task_id']
        child['task_revision'] = d['child_task']['task_revision']
        child['effects']['actions'] = child_actions if child_actions is not None else [
            {'operation': 'read', 'tool': 'EXAMPLE-file-read', 'targets': [self.CHILD_PATH], 'write_zone': 'none'}]
        for rec in (parent, child):
            rec.pop('route_proposal', None)
        records = [grant, parent, child, effect]
        if child_basis:  # a review bound to the child task: the only record-level basis for the child pointer
            basis = copy.deepcopy([r for r in ex('ex02_mutation_reviewed_bound.json')['records'] if r['record_type'] == 'review'][0])
            basis['review_id'] = 'TEST-child-review'
            basis['binding'].update({'task_id': d['child_task']['task_id'], 'task_revision': d['child_task']['task_revision'],
                                     'accepted_task_digest': d['child_task']['accepted_task_digest'],
                                     'context_digest': d['child_task']['context_digest'], 'inputs': copy.deepcopy(child['inputs'])})
            records.append(basis)
        return bundle_of(*records), effect

    def run_it(self, **kw):
        bundle, _ = self.build(**kw)
        return only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))


class Delegation(DelegationFixture):
    def test_valid_delegation_logic_meets_scope_but_stays_capped(self):
        obj = self.run_it()
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET', obj['notes'])
        self.assertEqual(gate(obj, 'ENVELOPE'), 'MET')
        self.assertEqual(obj['routes']['matched'], ['R-DELEGATE'])
        self.assertEqual(obj['required_review_phases'], [])  # a Reviewer call is not itself reviewed
        self.assertEqual(obj['reasons'], ['SIMULATED_VERIFIER_NOT_AUTHORITY'])
        self.assertEqual(obj['disposition'], 'BLOCKED')

    def test_shipped_example_stays_blocked_for_inactive_grant(self):
        obj = only(run(ex('ex17_delegate_full_descriptor.json'), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('GRANT_INACTIVE', obj['reasons'])
        self.assertNotEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET')

    def test_default_verifier_blocks_a_perfect_delegation(self):
        bundle, _ = self.build()
        obj = only(run(bundle, 'effect'))
        self.assertIn('TRUSTED_VERIFICATION_UNAVAILABLE', obj['reasons'])

    def test_empty_scope_is_none_not_wildcard(self):
        obj = self.run_it(scope_paths=[], ops=[], tools=[], child_actions=[
            {'operation': 'read', 'tool': 'EXAMPLE-file-read', 'targets': [self.CHILD_PATH], 'write_zone': 'none'}])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])
        self.assertNotEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET')

    def test_empty_scope_still_needs_child_task_and_binding_basis(self):
        bundle, _ = self.build(scope_paths=[], ops=[], tools=[])
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        # a child task always has at least one action, and every action is outside an empty scope
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET', obj['notes'])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])
        dropped, _ = self.build(scope_paths=[], ops=[], tools=[])
        dropped['records'] = [r for r in dropped['records'] if not (r['record_type'] == 'task' and r['task_id'].endswith('-review'))]
        obj = only(run(dropped, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'NOT_CHECKED')
        self.assertIn('DELEGATE_SCOPE_UNVERIFIED', obj['reasons'])

    def test_callee_outside_the_whitelist_is_refused(self):
        obj = self.run_it(callees=[])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])

    def test_native_dispatch_tool_does_not_pass_to_the_child(self):
        obj = self.run_it(tools=['EXAMPLE-native-subagent'])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])

    def test_child_operation_or_tool_beyond_the_grant_is_refused(self):
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', self.run_it(ops=['read', 'create_new'])['reasons'])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', self.run_it(tools=['EXAMPLE-other-tool'])['reasons'])

    def test_child_cannot_delegate_again(self):
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', self.run_it(ops=['read', 'delegate'])['reasons'])

    def test_look_alike_path_is_not_inside_the_grant(self):
        obj = self.run_it(scope_paths=['references-evil/x.docx'])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])

    def test_input_presence_does_not_grant_a_write(self):
        obj = self.run_it(ops=['create_new'], tools=['EXAMPLE-file-write'],
                          grant_ops=['read', 'delegate', 'create_new'],
                          grant_tools=['EXAMPLE-native-subagent', 'EXAMPLE-file-read', 'EXAMPLE-file-write'],
                          child_actions=[{'operation': 'create_new', 'tool': 'EXAMPLE-file-write',
                                          'targets': [self.CHILD_PATH], 'write_zone': 'working'}])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])
        self.assertNotEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET')

    def test_read_path_must_be_a_read_source_of_the_parent(self):
        obj = self.run_it(scope_paths=['working/EXAMPLE-work-1/'], child_actions=[
            {'operation': 'read', 'tool': 'EXAMPLE-file-read', 'targets': ['working/EXAMPLE-work-1/a.md'], 'write_zone': 'none'}])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])

    def test_child_task_asking_beyond_the_delegated_scope_is_refused(self):
        obj = self.run_it(child_actions=[{'operation': 'read', 'tool': 'EXAMPLE-file-read',
                                          'targets': ['references/other.docx'], 'write_zone': 'none'}])
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])

    def test_missing_child_or_parent_task_blocks_as_unverified(self):
        bundle, _ = self.build()
        bundle['records'] = [r for r in bundle['records'] if not (r['record_type'] == 'task' and r['task_id'].endswith('-review'))]
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('DELEGATE_SCOPE_UNVERIFIED', obj['reasons'])
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'NOT_CHECKED')

    def test_parent_digest_must_match_the_effect_binding(self):
        bundle, effect = self.build()
        effect['action']['delegation']['parent_task']['accepted_task_digest'] = 'sha256:' + 'f' * 64
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('BINDING_MISMATCH', obj['reasons'])
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')

    def test_requested_envelope_over_the_grant_limit_is_refused(self):
        bundle, _ = self.build(requested_concurrency=9)
        recs(bundle, 'grant')[0]['limits'] = {'max_concurrency': 2}
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('ENVELOPE_EXCEEDED', obj['reasons'])


class CorrectiveSubject(ControlCheckBase):
    """P2: a grant that names actor_ids must not be inherited by another actor with the same role."""

    def bundle(self, actor_ids='absent'):
        b = consistent_mutation()
        if actor_ids != 'absent':
            recs(b, 'grant')[0]['subject']['actor_ids'] = actor_ids
        return b

    def test_other_actor_with_same_role_does_not_inherit_the_grant(self):
        for phase in ('dispatch', 'effect', 'accept'):
            obj = only(run(self.bundle(['EXAMPLE-someone-else']), phase, verifier=cc.SimulatedVerifier()))
            self.assertEqual(gate(obj, 'GRANT_SCOPE'), 'UNMET', phase)
            self.assertIn('GRANT_OUT_OF_SCOPE', obj['reasons'], phase)
            self.assertEqual(obj['record_consistency']['status'], 'INCONSISTENT', phase)

    def test_named_actor_and_role_only_grants_still_cover(self):
        for actor_ids in (['EXAMPLE-worker-1'], 'absent'):
            for phase in ('dispatch', 'effect', 'accept'):
                obj = only(run(self.bundle(actor_ids), phase, verifier=cc.SimulatedVerifier()))
                self.assertEqual(gate(obj, 'GRANT_SCOPE'), 'MET', (actor_ids, phase))
                self.assertNotIn('GRANT_OUT_OF_SCOPE', obj['reasons'])

    def test_empty_actor_list_means_nobody_not_a_wildcard(self):
        obj = only(run(self.bundle([]), 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'GRANT_SCOPE'), 'UNMET')


class CorrectiveBinding(ControlCheckBase):
    """P2: provenance qualifiers and bound fields count as part of the binding."""

    def effect_and_review(self):
        b = consistent_mutation()
        return b, recs(b, 'effect')[0], [r for r in recs(b, 'review') if r['phase'] == 'PRE_EFFECT'][0]

    def test_baseline_binding_is_met(self):
        b, _, _ = self.effect_and_review()
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'BINDING'), 'MET')
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'MET')
        self.assertEqual(obj['record_consistency']['status'], 'CONSISTENT')

    def test_review_bound_to_another_source_revision_is_stale(self):
        b, effect, review = self.effect_and_review()
        review['binding']['inputs'][0]['revision'] = '2'  # same path and hash
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'UNMET')
        self.assertIn('STALE_REVIEW', obj['reasons'])
        self.assertEqual(gate(obj, 'BINDING'), 'UNMET')
        self.assertEqual(obj['record_consistency']['status'], 'INCONSISTENT')

    def test_effect_on_another_source_id_or_revision_differs_from_the_task(self):
        for field, value in (('revision', '2'), ('source_id', 'SRC-OTHER')):
            b, effect, review = self.effect_and_review()
            effect['binding']['inputs'][0][field] = value
            review['binding']['inputs'][0][field] = value  # review follows the effect, the task does not
            obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
            self.assertIn('BINDING_MISMATCH', obj['reasons'], field)
            self.assertEqual(gate(obj, 'BINDING'), 'UNMET', field)

    def test_action_digest_dropped_from_one_side_is_a_mismatch(self):
        digest = 'sha256:' + 'a' * 64
        b, effect, review = self.effect_and_review()
        review['binding']['action_digest'] = digest  # the review bound the action; the effect no longer carries it
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertIn('STALE_REVIEW', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'UNMET')
        b, effect, review = self.effect_and_review()
        effect['binding']['action_digest'] = digest  # the effect adds a field the review never saw
        self.assertIn('STALE_REVIEW', only(run(b, 'effect', verifier=cc.SimulatedVerifier()))['reasons'])

    def test_same_action_digest_on_both_sides_is_met(self):
        digest = 'sha256:' + 'a' * 64
        b, effect, review = self.effect_and_review()
        effect['binding']['action_digest'] = review['binding']['action_digest'] = digest
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'BINDING'), 'MET')

    def test_review_scope_objects_must_keep_the_same_qualifiers(self):
        b, _, _ = self.effect_and_review()
        integ = [r for r in recs(b, 'review') if r['phase'] == 'PRE_INTEGRATION'][0]
        integ['scope']['objects'][0]['revision'] = '7'
        obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
        self.assertIn('REVIEW_SCOPE_INCOMPLETE', obj['reasons'])
        self.assertNotIn('STALE_REVIEW', obj['reasons'])

    def test_non_pass_review_on_an_older_binding_is_stale_not_blocking(self):
        b, effect, review = self.effect_and_review()
        old = copy.deepcopy(review)
        old['review_id'] = 'TEST-old-review'
        old['verdict'] = 'BLOCKED'
        old['findings'] = [{'finding_id': 'F-OLD', 'severity': 'P1', 'statement': 'EXAMPLE: old problem'}]
        old['binding']['inputs'][0]['revision'] = '0'
        b['records'].append(old)
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertNotIn('REVIEW_BLOCKING_VERDICT', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'MET')
        self.assertTrue(any('TEST-old-review' in n for n in obj['notes']))  # the stale record is still reported
        self.assertEqual(gate(obj, 'BINDING'), 'MET')

    def test_non_pass_review_on_the_same_binding_still_blocks_a_pass(self):
        b, effect, review = self.effect_and_review()
        same = copy.deepcopy(review)
        same['review_id'] = 'TEST-same-binding-blocked'
        same['verdict'] = 'CHANGES_REQUIRED'
        same['findings'] = [{'finding_id': 'F-NOW', 'severity': 'P1', 'statement': 'EXAMPLE: current problem'}]
        b['records'].append(same)
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(obj['disposition'], 'DENY')
        self.assertIn('REVIEW_BLOCKING_VERDICT', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_EFFECT'), 'UNMET')


class CorrectiveDelegation(DelegationFixture):
    """P2: empty scope grants no rights but does not waive task/context binding."""

    def test_child_pointer_needs_a_binding_basis(self):
        bundle, _ = self.build(child_basis=False)
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'NOT_CHECKED')
        self.assertIn('DELEGATE_SCOPE_UNVERIFIED', obj['reasons'])

    def test_child_pointer_that_contradicts_its_basis_is_a_mismatch(self):
        bundle, effect = self.build()
        effect['action']['delegation']['child_task']['context_digest'] = 'sha256:' + 'e' * 64
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')
        self.assertIn('BINDING_MISMATCH', obj['reasons'])

    def test_parent_context_digest_must_match_the_effect_binding(self):
        bundle, effect = self.build()
        effect['action']['delegation']['parent_task']['context_digest'] = 'sha256:' + 'd' * 64
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')
        self.assertIn('BINDING_MISMATCH', obj['reasons'])

    def test_empty_scope_with_no_child_record_is_not_checked_even_with_every_digest_equal(self):
        bundle, _ = self.build(scope_paths=[], ops=[], tools=[])
        bundle['records'] = [r for r in bundle['records'] if not (r['record_type'] == 'task' and r['task_id'].endswith('-review'))]
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'NOT_CHECKED')

    def test_shipped_context_only_example_cannot_reach_met(self):
        bundle = ex('ex19_delegate_context_only.json')
        for r in bundle['records']:
            if r['record_type'] == 'grant':
                r.pop('example_only')
                r['status'] = 'ACTIVE'
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertNotEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET')  # G-01 has no context-only task representation yet


class CorrectiveRoleNamespace(DelegationFixture):
    """P2: callee.role_name (identity) and envelope.role (actor group) are different namespaces."""

    def ref(self, ref_id='EXAMPLE-role-acc-1'):
        return {'ref_id': ref_id, 'kind': 'role_acceptance', 'locator': 'EXAMPLE://packs/van-thu',
                'digest': 'sha256:' + 'b' * 64, 'trust_anchor': 'USER_CONTROLLED_STORE',
                'verification': {'status': 'NOT_ATTEMPTED'}}

    def domain(self, ref_id='EXAMPLE-role-acc-1'):
        return {'role_class': 'domain_accepted', 'role_name': 'EXAMPLE-van-thu', 'identity_ref': self.ref(ref_id)}

    def registered(self):
        return {'role_class': 'registered', 'role_name': 'EXAMPLE-native-x', 'identity_ref': self.ref('EXAMPLE-role-acc-2')}

    def test_accepted_domain_role_uses_the_domain_role_group(self):
        bundle, _ = self.build(callee=self.domain(), envelope_role='domain_role')
        obj = only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET', obj['notes'])
        self.assertIn('role_acceptance', [t['kind'] for t in obj['trusted_refs']])
        self.assertEqual(obj['disposition'], 'BLOCKED')  # simulated verifier cap

    def test_domain_role_without_a_verifier_is_blocked_on_trust(self):
        bundle, _ = self.build(callee=self.domain(), envelope_role='domain_role')
        obj = only(run(bundle, 'effect'))
        self.assertIn('TRUSTED_VERIFICATION_UNAVAILABLE', obj['reasons'])

    def test_registered_role_may_use_a_functional_group_but_not_an_actor_group(self):
        ok, _ = self.build(callee=self.registered(), envelope_role='worker')
        sim = cc.SimulatedVerifier(facts={'EXAMPLE-role-acc-2': {
            'role_name': 'EXAMPLE-native-x', 'role_class': 'registered', 'role_group': 'worker'}})
        self.assertEqual(gate(only(run(ok, 'effect', verifier=sim)), 'DELEGATE_SCOPE'), 'MET')
        for bad_group in ('issuer', 'main', 'user', 'host', 'tool', 'unknown'):
            bad, _ = self.build(callee=self.registered(), envelope_role=bad_group)
            obj = only(run(bad, 'effect', verifier=cc.SimulatedVerifier()))
            self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'], bad_group)

    def test_wrong_group_for_a_domain_or_core_role_is_refused(self):
        wrong_domain, _ = self.build(callee=self.domain(), envelope_role='reviewer')
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', only(run(wrong_domain, 'effect', verifier=cc.SimulatedVerifier()))['reasons'])
        wrong_core, _ = self.build(envelope_role='domain_role')
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', only(run(wrong_core, 'effect', verifier=cc.SimulatedVerifier()))['reasons'])

    def test_identity_not_in_the_grant_whitelist_is_refused(self):
        bundle, _ = self.build(callee=self.domain(), envelope_role='domain_role')
        recs(bundle, 'grant')[0]['scope']['delegate_callees'] = [self.domain('EXAMPLE-role-acc-OTHER')]
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', only(run(bundle, 'effect', verifier=cc.SimulatedVerifier()))['reasons'])

    def test_verifier_attesting_a_different_role_identity_is_refused(self):
        bundle, _ = self.build(callee=self.domain(), envelope_role='domain_role')
        sim = cc.SimulatedVerifier(facts={'EXAMPLE-role-acc-1': {'role_class': 'domain_accepted', 'role_name': 'EXAMPLE-other'}})
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', only(run(bundle, 'effect', verifier=sim))['reasons'])
        good = cc.SimulatedVerifier(facts={'EXAMPLE-role-acc-1': {'role_class': 'domain_accepted', 'role_name': 'EXAMPLE-van-thu'}})
        self.assertEqual(gate(only(run(bundle, 'effect', verifier=good)), 'DELEGATE_SCOPE'), 'MET')


class CanonicalOwners(ControlCheckBase):
    def test_default_check_reports_the_canonical_bytes_it_loaded_but_does_not_trust_them(self):
        out = run(ex('ex01_draft_in_grant.json'), 'effect')
        self.assertTrue(out['canonical_owners'])
        self.assertEqual(len(out['schema']['sha256']), 64)
        self.assertEqual(len(out['policy']['sha256']), 64)
        self.assertFalse(out['canonical_bytes_verified'])

    def test_injected_copy_with_the_same_id_and_version_is_noncanonical(self):
        schema = json.loads((cc.CANONICAL_SCHEMA).read_text(encoding='utf-8'))
        out = run(ex('ex01_draft_in_grant.json'), 'effect', schema=schema)
        self.assertFalse(out['canonical_owners'])
        self.assertIn('NONCANONICAL_OWNER', only(out)['reasons'])
        self.assertNotEqual(only(out)['disposition'], 'PASS')

    def test_relaxed_schema_with_the_same_id_cannot_launder_an_invalid_record(self):
        schema = json.loads((cc.CANONICAL_SCHEMA).read_text(encoding='utf-8'))
        schema['$defs']['task']['required'] = []
        out = run(ex('ex03_missing_intent.json'), 'effect', schema=schema)
        self.assertFalse(out['canonical_owners'])
        self.assertEqual(out['schema']['sha256'], None)
        for o in out['objects']:
            self.assertIn('NONCANONICAL_OWNER', o['reasons'])
            self.assertNotEqual(o['disposition'], 'PASS')

    def test_policy_with_weakened_constraints_and_same_version_is_noncanonical(self):
        policy = json.loads((cc.CANONICAL_POLICY).read_text(encoding='utf-8'))
        for row in policy['rows']:
            if row['row_id'] == 'R-MUTATION':
                row['required_review_phases'] = []
        out = run(ex('ex02_mutation_reviewed_bound.json'), 'effect', policy=policy)
        self.assertFalse(out['canonical_owners'])
        self.assertIn('NONCANONICAL_OWNER', only(out)['reasons'])
        self.assertFalse(out['policy']['canonical'])

    def test_remote_schema_references_are_refused(self):
        schema = json.loads((cc.CANONICAL_SCHEMA).read_text(encoding='utf-8'))
        schema['$defs']['id'] = {'$ref': 'https://example.invalid/x.json'}
        out = run(ex('ex01_draft_in_grant.json'), 'effect', schema=schema)
        self.assertEqual(out['disposition'], 'UNSUPPORTED')
        self.assertEqual(cc.exit_code(out), 2)

    def test_unknown_policy_version_is_unsupported(self):
        policy = json.loads((cc.CANONICAL_POLICY).read_text(encoding='utf-8'))
        policy['policy_version'] = 'law.cvf.routing/9'
        self.assertEqual(run(ex('ex01_draft_in_grant.json'), 'effect', policy=policy)['disposition'], 'UNSUPPORTED')


class CliAndExitCodes(ControlCheckBase):
    def main(self, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cc.main(args)
        return code, buf.getvalue()

    def test_exit_code_mapping(self):
        self.assertEqual(cc.exit_code({'disposition': 'PASS'}), 0)
        for d in ('DENY', 'BLOCKED', 'UNSUPPORTED'):
            self.assertEqual(cc.exit_code({'disposition': d}), 1)
        self.assertEqual(cc.exit_code({'disposition': 'NOT_APPLICABLE'}), 3)
        self.assertEqual(cc.exit_code({'disposition': 'UNSUPPORTED', 'init_error': True}), 2)

    def test_cli_blocked_na_and_schema_error_codes(self):
        code, text = self.main(['--phase', 'effect', str(EXAMPLES / 'ex01_draft_in_grant.json')])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(text)['disposition'], 'BLOCKED')
        self.assertEqual(self.main(['--phase', 'effect', str(EXAMPLES / 'ex06_reviewer_blocked_then_accepted.json')])[0], 3)
        code, text = self.main(['--phase', 'effect', str(EXAMPLES / 'ex03_missing_intent.json')])
        self.assertEqual(code, 1)  # malformed data is never N/A and never exit 3
        self.assertEqual(json.loads(text)['disposition'], 'DENY')

    def test_cli_has_no_trust_or_owner_override_flags(self):
        for flag in (['--trust-all'], ['--assume-verified'], ['--schema', 'x'], ['--policy', 'x']):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    cc.main(['--phase', 'effect'] + flag + [str(EXAMPLES / 'ex01_draft_in_grant.json')])
            self.assertEqual(cm.exception.code, 2)

    def test_cli_bad_input_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dup = Path(tmp) / 'dup.json'
            dup.write_text('{"a": 1, "a": 2}', encoding='utf-8')
            nan = Path(tmp) / 'nan.json'
            nan.write_text('{"a": NaN}', encoding='utf-8')
            arr = Path(tmp) / 'arr.json'
            arr.write_text('[1]', encoding='utf-8')
            for path in (dup, nan, arr):
                code, text = self.main(['--phase', 'dispatch', str(path)])
                data = json.loads(text)
                self.assertEqual(code, 1, path.name)
                self.assertEqual(data['disposition'], 'DENY')
                self.assertIn('INPUT_MALFORMED', data['reasons'])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(self.main(['--phase', 'dispatch', str(Path(tmp) / 'missing.json')])[0], 2)

    def test_script_runs_standalone_and_never_writes(self):
        before = sorted(p.name for p in EXAMPLES.iterdir())
        proc = subprocess.run([sys.executable, str(CHECKS / 'control_check.py'), '--phase', 'effect', '--format', 'text',
                               str(EXAMPLES / 'ex01_draft_in_grant.json')], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn('effect_authorized=false', proc.stdout)
        self.assertEqual(before, sorted(p.name for p in EXAMPLES.iterdir()))


class MainDeltaProjection(ControlCheckBase):
    def prepared(self):
        b = consistent_mutation()
        result = recs(b, 'result')[0]
        review = next(r for r in recs(b, 'review') if r['phase'] == 'PRE_INTEGRATION')
        result['artifacts'][0].update(revision='2', source_id='SRC-OUTPUT', scope='all')
        result['binding']['outputs'] = copy.deepcopy(result['artifacts'])
        review['binding'] = copy.deepcopy(result['binding'])
        review['scope']['objects'] = [{k: a[k] for k in ('path', 'digest')} for a in result['artifacts']]
        return b, result, review

    def test_minimal_summary_with_full_binding_is_covered(self):
        b, _, _ = self.prepared()
        obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'MET', obj['notes'])
        self.assertNotIn('STALE_REVIEW', obj['reasons'])
        self.assertEqual(gate(obj, 'BINDING'), 'MET')

    def test_nonpass_exact_binding_keeps_veto_with_minimal_or_empty_summary(self):
        for summary in ('minimal', 'empty', 'contradictory'):
            with self.subTest(summary=summary):
                b, result, review = self.prepared()
                blocked = copy.deepcopy(review)
                blocked['review_id'] = 'TEST-current-blocker'
                blocked['verdict'] = 'BLOCKED'
                blocked['findings'] = [{'finding_id': 'TEST-F', 'severity': 'P2', 'statement': 'Current finding'}]
                if summary == 'empty':
                    blocked['scope']['objects'] = []
                elif summary == 'contradictory':
                    blocked['scope']['objects'][0]['revision'] = 'wrong'
                review['scope']['objects'] = copy.deepcopy(result['artifacts'])
                b['records'].append(blocked)
                obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
                self.assertIn('REVIEW_BLOCKING_VERDICT', obj['reasons'])
                self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'UNMET')

    def test_explicit_wrong_qualifier_is_incomplete_coverage_not_stale_binding(self):
        b, _, review = self.prepared()
        review['scope']['objects'][0]['revision'] = 'wrong'
        obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
        self.assertIn('REVIEW_SCOPE_INCOMPLETE', obj['reasons'])
        self.assertNotIn('STALE_REVIEW', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'UNMET')

    def test_missing_or_extra_object_does_not_cover_artifacts(self):
        for mode in ('missing', 'extra'):
            with self.subTest(mode=mode):
                b, _, review = self.prepared()
                if mode == 'missing':
                    review['scope']['objects'][0]['path'] = 'working/other.md'
                else:
                    review['scope']['objects'].append({'path': 'working/extra.md', 'digest': 'sha256:' + 'c' * 64})
                obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
                self.assertIn('REVIEW_SCOPE_INCOMPLETE', obj['reasons'])
                self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'UNMET')

    def test_changed_full_output_binding_is_still_stale(self):
        b, _, review = self.prepared()
        review['binding']['outputs'][0]['revision'] = 'old'
        obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
        self.assertIn('STALE_REVIEW', obj['reasons'])
        self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'UNMET')


    def test_artifacts_must_match_own_bound_outputs_before_projection(self):
        for key, value in (('revision', '9'), ('source_id', 'OTHER'), ('scope', 'part'),
                           ('path', 'working/other.md'), ('digest', 'sha256:' + 'f' * 64)):
            with self.subTest(key=key):
                b, result, _ = self.prepared()
                result['artifacts'][0][key] = value
                obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
                self.assertIn('BINDING_MISMATCH', obj['reasons'])
                self.assertEqual(gate(obj, 'BINDING'), 'UNMET')
                self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'UNMET')

    def test_unbound_result_outputs_do_not_get_projection_coverage(self):
        for missing in (True, False):
            with self.subTest(missing=missing):
                b, result, review = self.prepared()
                for rec in (result, review):
                    if missing:
                        rec['binding'].pop('outputs')
                    else:
                        rec['binding']['outputs'] = []
                obj = only(run(b, 'accept', verifier=cc.SimulatedVerifier()))
                self.assertIn('BINDING_MISMATCH', obj['reasons'])
                self.assertEqual(gate(obj, 'review:PRE_INTEGRATION'), 'UNMET')


class MainDeltaChild(DelegationFixture):
    def prepared(self):
        b, effect = self.build()
        ptr = effect['action']['delegation']['child_task']
        child = next(t for t in recs(b, 'task') if t['task_id'] == ptr['task_id'])
        basis = next(r for r in recs(b, 'review') if r['binding']['task_id'] == ptr['task_id'])
        child['inputs'] = [{'path': self.CHILD_PATH, 'digest': 'sha256:' + 'a' * 64,
                            'revision': '2', 'source_id': 'SRC-CHILD'}]
        basis['binding']['inputs'] = []  # explicit mismatch, not an incomplete shared fixture
        return b, child, basis

    def test_peer_echo_with_missing_input_cannot_meet_scope(self):
        b, _, _ = self.prepared()
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')
        self.assertIn('BINDING_MISMATCH', obj['reasons'])

    def test_matching_child_inputs_meet_record_scope(self):
        b, child, basis = self.prepared()
        basis['binding']['inputs'] = copy.deepcopy(child['inputs'])
        obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET', obj['notes'])
        self.assertFalse(obj['effect_authorized'])

    def test_child_revision_or_source_id_mismatch_is_not_met(self):
        for key, value in (('revision', '1'), ('source_id', 'SRC-OTHER')):
            with self.subTest(key=key):
                b, child, basis = self.prepared()
                basis['binding']['inputs'] = copy.deepcopy(child['inputs'])
                basis['binding']['inputs'][0][key] = value
                obj = only(run(b, 'effect', verifier=cc.SimulatedVerifier()))
                self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')
                self.assertIn('BINDING_MISMATCH', obj['reasons'])


class MainDeltaRegistered(DelegationFixture):
    def prepared(self):
        callee = {'role_class': 'registered', 'role_name': 'TEST-native-role', 'identity_ref': {
            'ref_id': 'TEST-role-ref', 'kind': 'role_acceptance', 'locator': 'EXAMPLE://registered-role',
            'digest': 'sha256:' + 'b' * 64, 'trust_anchor': 'USER_CONTROLLED_STORE',
            'verification': {'status': 'NOT_ATTEMPTED'}}}
        b, _ = self.build(callee=callee, envelope_role='worker')
        return b

    def simulated(self, **facts):
        f = {'role_name': 'TEST-native-role', 'role_class': 'registered'}
        f.update(facts)
        return cc.SimulatedVerifier(facts={'TEST-role-ref': f})

    def test_attested_other_group_is_refused(self):
        obj = only(run(self.prepared(), 'effect', verifier=self.simulated(role_group='scout')))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')
        self.assertIn('DELEGATE_SCOPE_EXCEEDED', obj['reasons'])

    def test_missing_mapping_is_not_checked(self):
        for verifier in (self.simulated(), cc.SimulatedVerifier(), None):
            with self.subTest(verifier=type(verifier).__name__):
                obj = only(run(self.prepared(), 'effect', verifier=verifier))
                self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'NOT_CHECKED')
                self.assertIn('DELEGATE_SCOPE_UNVERIFIED', obj['reasons'])

    def test_mapping_must_bind_the_same_identity_and_class(self):
        for facts in ({'role_group': 'worker', 'role_name': 'OTHER'},
                      {'role_group': 'worker', 'role_class': 'domain_accepted'}):
            with self.subTest(facts=facts):
                obj = only(run(self.prepared(), 'effect', verifier=self.simulated(**facts)))
                self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'UNMET')

    def test_attested_matching_group_only_meets_record_scope(self):
        obj = only(run(self.prepared(), 'effect', verifier=self.simulated(role_group='worker')))
        self.assertEqual(gate(obj, 'DELEGATE_SCOPE'), 'MET', obj['notes'])
        self.assertEqual(obj['disposition'], 'BLOCKED')
        self.assertIn('SIMULATED_VERIFIER_NOT_AUTHORITY', obj['reasons'])
        self.assertFalse(obj['effect_authorized'])


if __name__ == '__main__':
    unittest.main()
