"""Scratch: break the checker in targeted ways; the G-02 tests must go red for each."""
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / '.cvf/checks'))
sys.path.insert(0, str(ROOT))
import control_check as cc  # noqa: E402

orig = {k: getattr(cc, k) for k in ('_condition', '_check_ref', '_covered', '_delegation', '_route', '_review_phase', '_attested',
                                    '_grant_coverage', '_digest_set', '_binding_diff', '_group_ok')}
orig_nv = cc.NoVerifier.verify


def restore():
    for k, v in orig.items():
        setattr(cc, k, v)
    cc.NoVerifier.verify = orig_nv


def mutate_protected():
    base = orig['_condition']
    cc._condition = lambda name, f, d: 'T' if name == 'NO_PROTECTED_TARGET' and not f.protected_hit and f.zone not in cc.HEAVY_ZONES else base(name, f, d)


def mutate_trust_claims():
    cc._check_ref = lambda ctx, ref, kind: ('VERIFIED', None) if (ref.get('verification') or {}).get('status') == 'VERIFIED' else ('UNAVAILABLE', 'TRUSTED_VERIFICATION_UNAVAILABLE')


def mutate_prefix_paths():
    cc._covered = lambda paths, allowed: all(any(p.startswith(a.rstrip('/')) for a in allowed) for p in paths)


def mutate_default_verifier():
    cc.NoVerifier.verify = lambda self, ref, kind: cc.VerifyResult('VERIFIED', {})


def mutate_delegation():
    cc._delegation = lambda *a, **k: (cc.MET, [])


def mutate_unknown_to_false():
    base = orig['_route']

    def route(ctx, f, derived):
        vals, causes = base(ctx, f, derived)
        return dict((k, ('F' if v == 'U' else v)) for k, v in vals.items()), []
    cc._route = route


def mutate_attestation_from_claim():
    cc._attested = lambda ctx, ref, kind: {'recipe_id': 'x', 'user_decision_effect': 'NONE'} if ref else {}


def mutate_ignore_actor_ids():
    base = orig['_grant_coverage']

    def cov(ctx, grants, actor, action):
        stripped = []
        for g in grants:
            g = dict(g, subject=dict((k, v) for k, v in g['subject'].items() if k != 'actor_ids'))
            stripped.append(g)
        return base(ctx, stripped, actor, action)
    cc._grant_coverage = cov


def mutate_path_digest_only():
    cc._digest_set = lambda items: set((i.get('path'), i.get('digest')) for i in (items or []))


def mutate_action_digest_one_sided():
    base = orig['_binding_diff']
    cc._binding_diff = lambda a, b, w: [d for d in base(a, b, w) if d != 'action_digest' or (a.get('action_digest') and b.get('action_digest'))]


def mutate_role_name_equals_group():
    cc._group_ok = lambda callee, group: group == callee.get('role_name')


def mutate_any_non_pass_blocks():
    base = orig['_review_phase']

    def phase(ctx, name, task, binding, blocked, result, reasons, notes):
        cands = [r for r in ctx.reviews if r['binding'].get('task_id') == binding['task_id'] and r['phase'] == name]
        if any(r['verdict'] != 'PASS' for r in cands):
            reasons.add('REVIEW_BLOCKING_VERDICT')
            return cc.UNMET, []
        return base(ctx, name, task, binding, blocked, result, reasons, notes)
    cc._review_phase = phase


MUTATIONS = [mutate_protected, mutate_trust_claims, mutate_prefix_paths, mutate_default_verifier,
             mutate_delegation, mutate_unknown_to_false, mutate_attestation_from_claim,
             mutate_ignore_actor_ids, mutate_path_digest_only, mutate_action_digest_one_sided,
             mutate_role_name_equals_group, mutate_any_non_pass_blocks]
import tests.test_control_check as T  # noqa: E402

bad = 0
for m in MUTATIONS:
    restore()
    m()
    suite = unittest.defaultTestLoader.loadTestsFromModule(T)
    res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
    red = len(res.failures) + len(res.errors)
    print('%-34s failing tests: %d' % (m.__name__, red))
    bad += red == 0
restore()
suite = unittest.defaultTestLoader.loadTestsFromModule(T)
res = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)
print('restored baseline: failures+errors =', len(res.failures) + len(res.errors), 'of', res.testsRun)
print('SURVIVING MUTATIONS:', bad)
