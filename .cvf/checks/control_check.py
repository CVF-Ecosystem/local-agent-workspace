#!/usr/bin/env python3
"""LAW control checker (G-02): read-only comparison of control records.

What this does: validates a bundle of task/grant/review/effect/result records against the
canonical schema, recomputes routing from the canonical policy, and compares records with
each other (grant scope, bindings, reviews, delegation scope). What it never does: authorize
an effect, issue a receipt, read source bytes, observe the real operation, or trust a value
because a record says it is verified. Every result carries effect_authorized=false.

Known limits (see .cvf/checks/README.md): no trusted verifier exists before G-03, so rows that
need trusted references stay BLOCKED; artifact bytes and the actual operation are not observed;
digests are only compared between records. Python 3.8 compatible; needs `jsonschema` with
Draft 2020-12 (UNSUPPORTED + DEPENDENCY_MISSING otherwise, never a weaker fallback).
"""
import argparse
import collections
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

RESULT_VERSION = 'law.cvf.check/1'
SCHEMA_ID = 'urn:law:cvf:control:1'
SCHEMA_VERSION = 'law.cvf.control/1'
POLICY_VERSION = 'law.cvf.routing/1'
HERE = Path(__file__).resolve().parent
CANONICAL_SCHEMA = HERE.parent / 'contracts' / 'control.schema.json'
CANONICAL_POLICY = HERE.parent / 'rules' / 'ROUTING_POLICY.json'
MAX_INPUT_BYTES = 8 * 1024 * 1024
PHASES = ('dispatch', 'effect', 'accept')

try:  # a missing or too-old jsonschema is reported, never replaced by a weaker check
    import jsonschema
    from jsonschema import Draft202012Validator, FormatChecker
except Exception:  # pragma: no cover - exercised by tests through a patched flag
    jsonschema = None

T, F, U = 'T', 'F', 'U'

# ---------------------------------------------------------------- reason catalog
# class: RECORD = records contradict each other; GATE = a required step is missing;
# AUTHORITY = trust/permission not established; OBSERVATION = nothing observed to compare;
# SAFETY = a safety condition cannot be established from self-declared facts.
REASON_CLASS = {
    'SCHEMA_INVALID': 'RECORD', 'INPUT_MALFORMED': 'RECORD', 'REF_UNRESOLVED': 'RECORD',
    'REF_AMBIGUOUS': 'RECORD', 'ROUTE_UNDERSTATED': 'RECORD', 'BINDING_MISMATCH': 'RECORD',
    'STALE_REVIEW': 'RECORD', 'REVIEW_BLOCKING_VERDICT': 'RECORD', 'GRANT_OUT_OF_SCOPE': 'RECORD',
    'DELEGATE_SCOPE_EXCEEDED': 'RECORD', 'RETRY_UNRECONCILED': 'RECORD',
    'MANDATORY_REQUIREMENT_NOT_MET': 'RECORD', 'ENVELOPE_EXCEEDED': 'RECORD',
    'EVIDENCE_REFERENCE_INVALID': 'RECORD', 'REVIEW_SCOPE_INCOMPLETE': 'RECORD',
    'KNOWN_PRESERVATION_LOSS': 'RECORD',
    'GRANT_MISSING': 'AUTHORITY', 'GRANT_INACTIVE': 'AUTHORITY', 'INTENT_NOT_TRUSTED': 'AUTHORITY',
    'REVIEWER_ELIGIBILITY_UNTRUSTED': 'AUTHORITY', 'TRUSTED_VERIFICATION_UNAVAILABLE': 'AUTHORITY',
    'REVIEW_MISSING': 'GATE', 'RECIPE_NOT_ACCEPTED': 'AUTHORITY',
    'SIMULATED_VERIFIER_NOT_AUTHORITY': 'AUTHORITY', 'NONCANONICAL_OWNER': 'AUTHORITY',
    'ACCEPTANCE_CLAIM_NOT_SUPPORTED': 'GATE',
    'OBSERVATION_UNAVAILABLE': 'OBSERVATION', 'ENVELOPE_UNMEASURED': 'OBSERVATION',
    'EVIDENCE_NOT_VERIFIED': 'OBSERVATION', 'DELEGATE_SCOPE_UNVERIFIED': 'OBSERVATION',
    'OUT_OF_CHECKER_SCOPE': 'OBSERVATION',
    'PROTECTED_TARGET_UNDETERMINED': 'SAFETY', 'UNCLASSIFIED_OPERATION': 'SAFETY',
    'CONDITION_UNRESOLVED': 'SAFETY', 'PRESERVATION_UNKNOWN': 'SAFETY',
    'SCHEMA_VERSION_UNKNOWN': 'RECORD', 'POLICY_VERSION_UNKNOWN': 'RECORD',
    'DEPENDENCY_MISSING': 'OBSERVATION',
}
DENY_REASONS = {'SCHEMA_INVALID', 'INPUT_MALFORMED', 'KNOWN_PRESERVATION_LOSS', 'REVIEW_BLOCKING_VERDICT'}
UNSUPPORTED_REASONS = {'SCHEMA_VERSION_UNKNOWN', 'POLICY_VERSION_UNKNOWN', 'DEPENDENCY_MISSING'}
RANK = {'PASS': 0, 'BLOCKED': 1, 'UNSUPPORTED': 2, 'DENY': 3}

WRITE_OPS = {'overwrite', 'delete', 'register_write', 'provenance_write', 'verification_status_write',
             'schema_or_policy_write', 'grant_write', 'skill_install', 'skill_export'}
HEAVY_ZONES = {'original_source', 'shared_register', 'framework', 'external'}
ZONES_UNKNOWN = {'unknown'}
UNTRUSTED_ANCHORS = {'MAIN_DECLARED', 'MAIN_WRITABLE_FILE', 'UNKNOWN'}
KIND_REASON = {'user_intent': 'INTENT_NOT_TRUSTED', 'reviewer_eligibility': 'REVIEWER_ELIGIBILITY_UNTRUSTED'}

# Gate due table: phases in which a gate must be MET. Gates not due are NOT_YET_DUE and never block.
GATE_DUE = {
    'GRANT_SCOPE': 'dea', 'PATH_SCOPE': 'dea', 'TOOL_SCOPE': 'dea', 'GRANT_EXACT_COVERAGE': 'dea',
    'ENVELOPE': 'dea', 'RECIPE_VERSION_ACCEPTED': 'dea', 'DELEGATE_SCOPE': 'de', 'BINDING': 'ea',
    'INPUT_REVISION': 'ea', 'PRESERVATION': 'ea', 'ACTUAL_OUTCOME': 'a', 'SOURCE_SCOPE_AND_CONCLUSION': 'a',
    'SKILL_INTAKE_STANDARD': 'ea', 'REQUIREMENTS': 'a',
}
REVIEW_DUE = {'PRE_EFFECT': 'ea', 'PRE_INTEGRATION': 'a', 'PRE_DELIVERY': 'a'}
MET, UNMET, NOT_CHECKED, NOT_YET_DUE = 'MET', 'UNMET', 'NOT_CHECKED', 'NOT_YET_DUE'


# ---------------------------------------------------------------- verifier interface
class VerifyResult(collections.namedtuple('VerifyResult', 'status facts')):
    """status: VERIFIED | FAILED | UNAVAILABLE. facts: attested values (e.g. recipe version)."""


class Verifier(object):
    trust_basis = 'NONE'

    def verify(self, ref, expected_kind):  # pragma: no cover - interface
        raise NotImplementedError


class NoVerifier(Verifier):
    """Production default before G-03: nothing can be verified outside Main's control."""
    trust_basis = 'NONE'

    def verify(self, ref, expected_kind):
        return VerifyResult('UNAVAILABLE', {})


class SimulatedVerifier(Verifier):
    """Unit-test double. Proves only the checker's authority logic; any disposition derived
    from it is capped at BLOCKED and labelled SIMULATED."""
    trust_basis = 'SIMULATED'

    def __init__(self, status='VERIFIED', facts=None):
        self.status = status
        self.facts = dict(facts or {})

    def verify(self, ref, expected_kind):
        return VerifyResult(self.status, self.facts.get(ref.get('ref_id'), {}))


# ---------------------------------------------------------------- small helpers
def _and3(vals):
    if any(v == F for v in vals):
        return F
    return U if any(v == U for v in vals) else T


def _or3(vals):
    if any(v == T for v in vals):
        return T
    return U if any(v == U for v in vals) else F


def _segments(path):
    """Normalized path segments, or None when the path cannot be trusted as a path."""
    if not isinstance(path, str) or not path or '\\' in path or path.startswith('/'):
        return None
    if any(ord(c) < 32 for c in path):
        return None
    segs = [s for s in path.split('/') if s != '']
    if not segs or any(s in ('.', '..') for s in segs) or re.match(r'^[A-Za-z]:$', segs[0]):
        return None
    return tuple(segs)


def _within(child, parent):
    return child is not None and parent is not None and len(parent) <= len(child) and child[:len(parent)] == parent


def _fold(segs):
    return tuple((s.casefold().rstrip('. ') or s.casefold()) for s in segs)


def _covered(paths, allowed):
    """Every path inside one allowed path, exact case, whole segments. Empty allowed = none."""
    segs_allowed = [_segments(a) for a in allowed]
    return all(any(_within(_segments(p), a) for a in segs_allowed if a is not None) for p in paths)


BOUND_KEYS = ('path', 'digest', 'source_id', 'revision', 'scope')


def _digest_set(items):
    """Bound objects keep their source/revision qualifiers: same path+hash at another revision differs."""
    return set(tuple(i.get(k) for k in BOUND_KEYS) for i in (items or []))


def _parse_time(value):
    try:
        text = value[:-1] + '+00:00' if value.endswith('Z') else value
        parsed = datetime.datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        return parsed
    except Exception:
        return None


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


class InputError(Exception):
    pass


def _no_dupes(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise InputError('duplicate JSON key: %s' % k)
        out[k] = v
    return out


def _no_constant(name):
    raise InputError('non-standard JSON constant: %s' % name)


def parse_json_bytes(data):
    if len(data) > MAX_INPUT_BYTES:
        raise InputError('input larger than %d bytes' % MAX_INPUT_BYTES)
    try:
        text = data.decode('utf-8-sig')
        obj = json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_no_constant)
    except InputError:
        raise
    except Exception as exc:
        raise InputError('not valid UTF-8 JSON: %s' % exc)
    if not isinstance(obj, dict):
        raise InputError('top-level JSON value must be an object')
    return obj


def _has_remote_ref(node):
    if isinstance(node, dict):
        ref = node.get('$ref')
        if isinstance(ref, str) and not ref.startswith('#'):
            return True
        return any(_has_remote_ref(v) for v in node.values())
    if isinstance(node, list):
        return any(_has_remote_ref(v) for v in node)
    return False


# ---------------------------------------------------------------- context
class Ctx(object):
    def __init__(self, records, policy, verifier, now, canonical):
        self.policy = policy
        self.rows = policy['rows']
        self.verifier = verifier
        self.now = now
        self.canonical = canonical
        self.tasks = collections.defaultdict(list)
        self.grants_by_ref = collections.defaultdict(list)
        self.reviews = []
        self.effects = []
        self.results = []
        self.global_reasons = set()
        self.ambiguous = []
        seen = collections.defaultdict(list)
        for rec in records:
            rt = rec.get('record_type')
            if rt == 'task':
                self.tasks[(rec['task_id'], rec['task_revision'])].append(rec)
                seen[('task', '%s@%s' % (rec['task_id'], rec['task_revision']))].append(rec)
            elif rt == 'grant':
                self.grants_by_ref[rec['issuer_ref']['ref_id']].append(rec)
                seen[('grant', rec['grant_id'])].append(rec)
            elif rt == 'review':
                self.reviews.append(rec)
                seen[('review', rec['review_id'])].append(rec)
            elif rt == 'effect':
                self.effects.append(rec)
                seen[('effect', rec['effect_id'])].append(rec)
            elif rt == 'result':
                self.results.append(rec)
                seen[('result', rec['result_id'])].append(rec)
        for key, recs in seen.items():
            if len(recs) > 1:
                self.ambiguous.append('%s:%s' % key)
        for refid, gs in self.grants_by_ref.items():
            if len(gs) > 1:
                self.ambiguous.append('grant-ref:%s' % refid)
        if self.ambiguous:
            self.global_reasons.add('REF_AMBIGUOUS')
        self.tasks_list = [rec for rec in records if rec.get('record_type') == 'task']

    def task(self, task_id, revision):
        found = self.tasks.get((task_id, revision), [])
        return found[0] if len(found) == 1 else None


# ---------------------------------------------------------------- trusted references
def _check_ref(ctx, ref, kind):
    """-> (state, reason). state in VERIFIED | UNAVAILABLE | UNTRUSTED_ANCHOR | FAILED."""
    kinds = ('user_intent', 'user_condition') if kind == 'user_intent' else (kind,)
    if ref.get('kind') not in kinds:
        return 'FAILED', 'TRUSTED_VERIFICATION_UNAVAILABLE'
    if ref.get('trust_anchor') in UNTRUSTED_ANCHORS:
        return 'UNTRUSTED_ANCHOR', KIND_REASON.get(kind, 'TRUSTED_VERIFICATION_UNAVAILABLE')
    res = ctx.verifier.verify(ref, kind)
    if res.status == 'VERIFIED':
        return 'VERIFIED', None
    return ('FAILED' if res.status == 'FAILED' else 'UNAVAILABLE'), 'TRUSTED_VERIFICATION_UNAVAILABLE'


def _attested(ctx, ref, kind):
    """Facts attested by the verifier for a ref, or {} when it is not verified."""
    if ref is None or ref.get('kind') != kind or ref.get('trust_anchor') in UNTRUSTED_ANCHORS:
        return {}
    res = ctx.verifier.verify(ref, kind)
    return res.facts if res.status == 'VERIFIED' else {}


# ---------------------------------------------------------------- per-action facts
class Facts(object):
    pass


def _action_key(action):
    return (action.get('operation'), action.get('tool'), tuple(action.get('targets') or ()))


def _grants_for(ctx, ref_ids, reasons, notes):
    grants = []
    for rid in ref_ids:
        found = ctx.grants_by_ref.get(rid, [])
        if not found:
            reasons.add('REF_UNRESOLVED')
            notes.append('grant reference %s does not resolve inside the bundle' % rid)
        elif len(found) > 1:
            reasons.add('REF_AMBIGUOUS')
        else:
            grants.append(found[0])
    return grants


def _grant_coverage(ctx, grants, actor, action):
    """-> dict(grant=ok/missing/inactive/out, ops, tools, paths) comparing record to record."""
    out = {'state': 'MISSING', 'ops': False, 'tools': False, 'paths': False, 'role': False}
    if not grants:
        return out
    states = []
    for g in grants:
        scope = g.get('scope', {})
        active = g.get('status') == 'ACTIVE' and not g.get('example_only')
        limits = g.get('limits', {})
        if active and limits.get('expires_at'):
            exp = _parse_time(limits['expires_at'])
            if exp is None or exp <= ctx.now:
                active = False
        if not active:
            states.append('INACTIVE')
            continue
        subject = g.get('subject', {})
        role_ok = actor.get('role') in (subject.get('roles') or [])
        if 'actor_ids' in subject:  # optional: absent = role only; present (even empty) = only those actors
            role_ok = role_ok and actor.get('actor_id') in (subject.get('actor_ids') or [])
        ops_ok = action.get('operation') in (scope.get('operations') or [])
        tools_ok = action.get('tool') in (scope.get('tools') or [])
        targets = action.get('targets') or []
        paths_ok = _covered(targets, scope.get('paths') or []) if targets else True
        if role_ok and ops_ok and tools_ok and paths_ok:
            return {'state': 'COVERED', 'ops': True, 'tools': True, 'paths': True, 'role': True, 'grant': g}
        states.append('OUT')
        out.update({'ops': ops_ok, 'tools': tools_ok, 'paths': paths_ok, 'role': role_ok})
    out['state'] = 'OUT' if 'OUT' in states else 'INACTIVE'
    return out


def _envelope_state(envelope, grants):
    """-> 'ok' | 'exceeded' | 'unmeasured'. Compares requested values with grant limits only."""
    limits = {}
    for g in grants:
        for k, v in (g.get('limits') or {}).items():
            limits.setdefault(k, []).append(v)
    if not limits:
        return 'ok'
    if not envelope:
        return 'unmeasured'
    state = 'ok'
    for key, bounds in limits.items():
        field = envelope.get(key)
        if not isinstance(field, dict) or field.get('status') not in ('APPLIED', 'REQUESTED'):
            state = 'unmeasured' if state == 'ok' else state
            continue
        value = field.get('value')
        for bound in bounds:
            if key in ('max_concurrency', 'max_retries'):
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if value > bound:
                        return 'exceeded'
                else:
                    state = 'unmeasured' if state == 'ok' else state
            elif key == 'expires_at':
                a, b = _parse_time(value) if isinstance(value, str) else None, _parse_time(bound)
                if a is None or b is None:
                    state = 'unmeasured' if state == 'ok' else state
                elif a > b:
                    return 'exceeded'
            else:  # cost_limit and any future limit: only exact equality is comparable
                if value != bound:
                    state = 'unmeasured' if state == 'ok' else state
    return state


def _facts(ctx, action, task, actor, grants, envelope):
    f = Facts()
    f.action = action
    f.op = action.get('operation')
    f.zone = action.get('write_zone')
    f.content_use = set(action.get('content_use') or [])
    f.targets = action.get('targets') or []
    f.recipe = action.get('recipe')
    protected = []
    if task is not None:
        protected = [_segments(p) for p in (task.get('effects', {}).get('protected_targets') or [])]
    hit = False
    bad_path = False
    for t in f.targets:
        s = _segments(t)
        if s is None:
            bad_path = True
            continue
        for p in protected:
            if p is not None and _within(_fold(s), _fold(p)):
                hit = True
    f.protected_hit = hit
    f.bad_path = bad_path
    f.coverage = _grant_coverage(ctx, grants, actor, action)
    f.env = _envelope_state(envelope, grants)
    preservation = []
    if task is not None:
        preservation = task.get('effects', {}).get('preservation') or []
    f.known_loss = any(p.get('known_loss_state') == 'KNOWN_LOSS' and any(
        _within(_segments(t), _segments(p.get('target'))) for t in f.targets) for p in preservation)
    f.write_op = f.op in WRITE_OPS
    # recipe / user-decision conditions: negative self-claims never lower the route
    f.recipe_accepted = F
    f.recipe_changed = T
    f.decision = {'NO_USER_DECISION_CHANGE': U, 'USER_DECISION_CHANGE': U, 'USER_DECISION_EFFECT_UNKNOWN': U}
    if f.recipe:
        attest = _attested(ctx, f.recipe.get('acceptance_ref'), 'recipe_acceptance')
        anchor = (f.recipe.get('acceptance_ref') or {}).get('trust_anchor')
        if anchor in UNTRUSTED_ANCHORS:
            f.recipe_accepted, f.recipe_changed = F, T
        elif attest:
            same = attest.get('recipe_id') == f.recipe.get('recipe_id') and \
                attest.get('recipe_version') == f.recipe.get('recipe_version')
            f.recipe_accepted, f.recipe_changed = (T, F) if same else (F, T)
        else:
            f.recipe_accepted, f.recipe_changed = U, U
        claim = f.recipe.get('user_decision_effect')
        eff = attest.get('user_decision_effect') if attest else None
        if eff:
            f.decision = {'NO_USER_DECISION_CHANGE': T if eff == 'NONE' else F,
                          'USER_DECISION_CHANGE': T if eff == 'CHANGES' else F,
                          'USER_DECISION_EFFECT_UNKNOWN': T if eff == 'UNKNOWN' else F}
        elif claim == 'CHANGES':
            f.decision = {'NO_USER_DECISION_CHANGE': F, 'USER_DECISION_CHANGE': T, 'USER_DECISION_EFFECT_UNKNOWN': F}
        elif claim == 'UNKNOWN':
            f.decision = {'NO_USER_DECISION_CHANGE': F, 'USER_DECISION_CHANGE': U, 'USER_DECISION_EFFECT_UNKNOWN': T}
    return f


def _condition(name, f, derived):
    if name == 'NO_PROTECTED_TARGET':
        # Never TRUE from self-declared zone/protected_targets (D3): FALSE when the record itself
        # shows a protected or heavy target, UNKNOWN otherwise.
        return F if (f.protected_hit or f.zone in HEAVY_ZONES) else U
    if name == 'RECIPE_ACCEPTED_VERSION':
        return f.recipe_accepted
    if name == 'RECIPE_ABSENT_OR_CHANGED':
        return f.recipe_changed
    if name in f.decision:
        return f.decision[name]
    if name == 'KNOWN_PRESERVATION_LOSS':
        if f.known_loss:
            return T
        return U if f.write_op else F
    if name == 'ENVELOPE_EXCEEDED':
        return {'exceeded': T, 'ok': F, 'unmeasured': U}[f.env]
    if name == 'UNCLASSIFIED':
        return T if (f.op == 'unknown' or f.zone in ZONES_UNKNOWN) else F
    if name == 'MISSING_AUTHORITY':
        return T if derived.get('missing_authority') else F
    if name == 'MISSING_REQUIRED_REVIEW':
        return T if derived.get('missing_review') else F
    return U  # a condition this checker does not know cannot be resolved


def _clause(clause, f, derived):
    vals = []
    if 'operations' in clause:
        vals.append(T if f.op in clause['operations'] else F)
    if 'write_zones' in clause:
        vals.append(T if f.zone in clause['write_zones'] else F)
    if 'content_use' in clause:
        vals.append(T if f.content_use & set(clause['content_use']) else F)
    if 'conditions_all' in clause:
        vals.extend(_condition(c, f, derived) for c in clause['conditions_all'])
    if 'conditions_any' in clause:
        vals.append(_or3([_condition(c, f, derived) for c in clause['conditions_any']]))
    return _and3(vals) if vals else U


def _route(ctx, f, derived):
    """-> (row values, causes). Unknown rows stay in the route as 'possible'."""
    vals = {}
    for row in ctx.rows:
        vals[row['row_id']] = _or3([_clause(c, f, derived) for c in row['match_any']])
    causes = []
    if f.op == 'unknown':
        causes.append('operation_unknown')
    if f.zone in ZONES_UNKNOWN:
        causes.append('zone_unknown')
    if f.bad_path:
        causes.append('path_not_normalizable')
    if not any(v in (T, U) for v in vals.values()):
        causes.append('no_row_matched')
    if any(v == U for rid, v in vals.items() if rid != 'R-UNCLASSIFIED'):
        causes.append('unresolved_condition')
    if causes and vals.get('R-UNCLASSIFIED') == F:
        vals['R-UNCLASSIFIED'] = T
    return vals, causes


# ---------------------------------------------------------------- review evaluation
def _binding_diff(a, b, with_outputs):
    diffs = []
    for key in ('task_id', 'task_revision', 'intent_digest', 'accepted_task_digest', 'context_digest', 'policy_version'):
        if a.get(key) != b.get(key):
            diffs.append(key)
    if _digest_set(a.get('inputs')) != _digest_set(b.get('inputs')):
        diffs.append('inputs')
    if a.get('action_digest') != b.get('action_digest'):  # a field bound on one side only is a mismatch
        diffs.append('action_digest')
    if with_outputs and _digest_set(a.get('outputs')) != _digest_set(b.get('outputs')):
        diffs.append('outputs')
    return diffs


def _scope_covers_objects(summaries, artifacts):
    """Coverage projection, called only after full bindings match strictly.

    path/digest are mandatory. Optional qualifiers may be omitted in a summary,
    but every explicitly supplied qualifier must match. Neither missing artifacts
    nor extra/unmatched summaries count as complete coverage.
    """
    def matches(summary, artifact):
        return all(artifact.get(k) == summary[k] for k in BOUND_KEYS if k in summary)

    return (all(any(matches(s, a) for a in artifacts) for s in summaries)
            and all(any(matches(s, a) for s in summaries) for a in artifacts))


def _review_phase(ctx, phase_name, task, binding, blocked_ids, result_rec, reasons, notes):
    """-> (state MET|UNMET, used reviews). Adds reasons. Never accepts a self-declared reviewer."""
    task_id, rev = binding['task_id'], binding['task_revision']
    cands = [r for r in ctx.reviews if r['binding'].get('task_id') == task_id and
             r['binding'].get('task_revision') == rev and r['phase'] == phase_name]
    if not cands:
        reasons.add('REVIEW_MISSING')
        return UNMET, []
    with_outputs = phase_name != 'PRE_EFFECT'
    same, stale = [], []
    for r in cands:
        problems = _binding_diff(r['binding'], binding, with_outputs)
        if problems:
            stale.append((r, problems))
        else:
            same.append(r)
    for r, problems in stale:
        notes.append('review %s is bound to something else (differs on: %s)' % (r['review_id'], ', '.join(problems)))
    # only a review for this exact binding can block it; an older non-PASS verdict is stale, not a veto
    if any(r['verdict'] != 'PASS' for r in same):
        reasons.add('REVIEW_BLOCKING_VERDICT')
        return UNMET, []
    if not same:
        reasons.update(('STALE_REVIEW', 'BINDING_MISMATCH'))
        return UNMET, []
    if result_rec is not None and not _bound_artifacts_match(result_rec):
        reasons.add('BINDING_MISMATCH')
        notes.append('result artifacts differ from their own bound outputs; summary projection cannot supply the missing binding')
        return UNMET, []
    good = []
    for r in same:
        if with_outputs and result_rec is not None and not _scope_covers_objects(
                r['scope'].get('objects') or [], result_rec.get('artifacts') or []):
            reasons.add('REVIEW_SCOPE_INCOMPLETE')
            notes.append('review %s does not cover the result artifacts or has contradictory scope qualifiers' % r['review_id'])
            continue
        if phase_name == 'PRE_EFFECT' and task is not None:
            need = set(ref['ref_id'] for ref in task['intent']['refs'])
            if not need <= set(r['scope'].get('intent_refs_checked') or []):
                reasons.add('REVIEW_SCOPE_INCOMPLETE')
                continue
        rv = r['reviewer']
        if rv['independence_observed'] != 'OBSERVED_SEPARATE_CONTEXT' or rv['actor'].get('role') != 'reviewer' \
                or rv['actor'].get('actor_id') in blocked_ids:
            reasons.add('REVIEWER_ELIGIBILITY_UNTRUSTED')
            continue
        good.append(r)
    return (MET if good else UNMET), good


# ---------------------------------------------------------------- delegation
ACTOR_GROUPS_FOR_REGISTERED = ('scout', 'worker', 'reviewer', 'domain_role')


def _group_ok(callee, group):
    """callee.role_name is an identity; envelope.role is an actor group. Map them by role_class."""
    cls = callee.get('role_class')
    if cls == 'core':
        return group == callee.get('role_name')
    if cls == 'domain_accepted':
        return group == 'domain_role'
    if cls == 'registered':
        return group in ACTOR_GROUPS_FOR_REGISTERED
    return False


def _delegation(ctx, action, cov, effect_binding, reasons, notes):
    """-> (MET|UNMET|NOT_CHECKED, extra trusted refs). Record comparison only; no host enforcement."""
    d = action['delegation']
    callee, scope = d['callee'], d['tool_scope']
    extra = []
    grant = cov.get('grant')
    if grant is None:
        return NOT_CHECKED, extra
    if callee.get('role_class') != 'core':
        extra.append((callee.get('identity_ref'), 'role_acceptance'))
    allowed = [(c.get('role_class'), c.get('role_name'), (c.get('identity_ref') or {}).get('ref_id'))
               for c in grant['scope'].get('delegate_callees') or []]
    mine = (callee.get('role_class'), callee.get('role_name'), (callee.get('identity_ref') or {}).get('ref_id'))
    if mine not in allowed:
        reasons.add('DELEGATE_SCOPE_EXCEEDED')
        notes.append('callee is not in the grant delegate_callees list')
        return UNMET, extra
    envelope = d['requested_envelope']
    if not _group_ok(callee, envelope.get('role')):
        reasons.add('DELEGATE_SCOPE_EXCEEDED')
        notes.append('envelope role %s is not an actor group allowed for a %s callee' % (envelope.get('role'), callee.get('role_class')))
        return UNMET, extra
    if callee.get('role_class') != 'core':
        facts = _attested(ctx, callee.get('identity_ref'), 'role_acceptance')
        if facts and (facts.get('role_name') not in (None, callee.get('role_name'))
                      or facts.get('role_class') not in (None, callee.get('role_class'))):
            reasons.add('DELEGATE_SCOPE_EXCEEDED')
            notes.append('the verified role acceptance names a different role than the callee')
            return UNMET, extra
        if callee.get('role_class') == 'registered':
            if (facts.get('role_name') != callee['role_name']
                    or facts.get('role_class') != 'registered' or 'role_group' not in facts):
                reasons.add('DELEGATE_SCOPE_UNVERIFIED')
                notes.append('registered identity has no complete attested role_name/class/group mapping')
                return NOT_CHECKED, extra
            if facts['role_group'] != envelope['role']:
                reasons.add('DELEGATE_SCOPE_EXCEEDED')
                notes.append('requested actor group differs from the accepted registered identity mapping')
                return UNMET, extra
    ops, tools, paths = scope['operations'], scope['tools'], scope['paths']
    g_ops = grant['scope'].get('operations') or []
    g_tools = grant['scope'].get('tools') or []
    if 'delegate' in ops or action.get('tool') in tools or not set(ops) <= set(g_ops) or not set(tools) <= set(g_tools) \
            or not _covered(paths, grant['scope'].get('paths') or []):
        reasons.add('DELEGATE_SCOPE_EXCEEDED')
        notes.append('child tool scope exceeds the grant (or reuses the dispatch tool / delegates again)')
        return UNMET, extra
    if _envelope_state(envelope, [grant]) == 'exceeded':
        reasons.add('ENVELOPE_EXCEEDED')
        return UNMET, extra
    parent_p, child_p = d['parent_task'], d['child_task']
    parent = ctx.task(parent_p['task_id'], parent_p['task_revision'])
    child = ctx.task(child_p['task_id'], child_p['task_revision'])
    # an empty scope grants no rights, but it does not waive the task/context binding of parent and child
    if parent is None or child is None:
        reasons.add('DELEGATE_SCOPE_UNVERIFIED')
        notes.append('parent or child task does not resolve to exactly one task record in the bundle')
        return NOT_CHECKED, extra
    if effect_binding is None:
        reasons.add('DELEGATE_SCOPE_UNVERIFIED')
        notes.append('no effect binding ties the parent pointer to an accepted task and context')
        return NOT_CHECKED, extra
    if any(effect_binding.get(k) != parent_p[k] for k in ('task_id', 'task_revision', 'accepted_task_digest', 'context_digest')):
        reasons.add('BINDING_MISMATCH')
        notes.append('parent pointer differs from the effect binding (task, revision, accepted task or context)')
        return UNMET, extra
    basis = [r['binding'] for r in ctx.reviews + ctx.effects + ctx.results
             if r['binding'].get('task_id') == child_p['task_id'] and r['binding'].get('task_revision') == child_p['task_revision']]
    if not basis:
        reasons.add('DELEGATE_SCOPE_UNVERIFIED')
        notes.append('no review, effect or result in the bundle binds the child task, so its pointer cannot be compared')
        return NOT_CHECKED, extra
    if any(b.get(k) != child_p[k] for b in basis for k in ('accepted_task_digest', 'context_digest')):
        reasons.add('BINDING_MISMATCH')
        notes.append('child pointer differs from the record that binds the child task')
        return UNMET, extra
    if any(_digest_set(b.get('inputs')) != _digest_set(child.get('inputs')) for b in basis):
        reasons.add('BINDING_MISMATCH')
        notes.append('child binding basis contradicts the resolved child task inputs/provenance/revision')
        return UNMET, extra
    parent_actions = parent['effects']['actions']
    read_sources = [p.get('path') for p in parent.get('inputs') or []] + \
                   [p.get('path') for p in parent.get('context_refs') or []]
    for a in parent_actions:
        if a.get('operation') == 'read':
            read_sources.extend(a.get('targets') or [])
    for op in ops:
        if op == 'read':
            if not _covered(paths, read_sources):
                reasons.add('DELEGATE_SCOPE_EXCEEDED')
                notes.append('child read paths are not read sources of the parent task')
                return UNMET, extra
        else:
            sources = []
            for a in parent_actions:
                if a.get('operation') == op and a.get('tool') in tools:
                    sources.extend(a.get('targets') or [])
            if not set(tools) <= set(a.get('tool') for a in parent_actions if a.get('operation') == op) \
                    or not _covered(paths, sources):
                reasons.add('DELEGATE_SCOPE_EXCEEDED')
                notes.append('child %s scope is not an approved parent action scope' % op)
                return UNMET, extra
    child_allowed = [(o, t) for o in ops for t in tools]
    for a in child['effects']['actions']:
        if (a.get('operation'), a.get('tool')) not in child_allowed or not _covered(a.get('targets') or [], paths):
            reasons.add('DELEGATE_SCOPE_EXCEEDED')
            notes.append('child task asks for an operation, tool or file outside the delegated scope')
            return UNMET, extra
    return MET, extra


# ---------------------------------------------------------------- object evaluation
def _bound_artifacts_match(result_rec):
    return _digest_set(result_rec['binding'].get('outputs')) == _digest_set(result_rec.get('artifacts'))


def _gate_status(gate, phase, status):
    return status if phase[0] in GATE_DUE[gate] else NOT_YET_DUE


def _worst(states):
    return UNMET if UNMET in states else (NOT_CHECKED if NOT_CHECKED in states else MET)


def _evaluate(ctx, phase, obj):
    reasons = set(ctx.global_reasons)
    notes = []
    task = obj['task']
    if task is None and obj.get('task_wanted'):
        reasons.add('REF_UNRESOLVED')
        notes.append('task %s@%s does not resolve to exactly one task record in the bundle' % obj['task_wanted'])
    actions = obj['actions']
    grant_ids = list(obj['grant_ref_ids'])
    if task is not None:
        grant_ids += [r['ref_id'] for r in task['authority']['grant_refs']]
    grants = _grants_for(ctx, sorted(set(grant_ids)), reasons, notes)
    actor = obj['actor']
    binding = obj.get('binding')
    envelope = task.get('envelope') if task is not None else None
    facts_list = []
    for action in actions:
        env = (action.get('delegation') or {}).get('requested_envelope') or envelope
        facts_list.append(_facts(ctx, action, task, actor, grants, env))

    # pass 1: route from the record's facts only; this decides which review phases are required
    first = [_route(ctx, f, {}) for f in facts_list]
    rows_by_id = dict((r['row_id'], r) for r in ctx.rows)
    in_route = set()
    for vals, _ in first:
        in_route.update(rid for rid, v in vals.items() if v in (T, U))
    phases_needed = set()
    for rid in in_route:
        phases_needed.update(rows_by_id[rid]['required_review_phases'])

    # reviews (only phases that are due now; later phases are NOT_YET_DUE)
    review_state, used_reviews = {}, []
    blocked_ids = set([obj['actor'].get('actor_id')])
    if task is not None:
        blocked_ids.add(task['proposed_by']['actor_id'])
    for ph in sorted(phases_needed):
        if phase[0] not in REVIEW_DUE[ph]:
            review_state[ph] = NOT_YET_DUE
        elif binding is None:
            reasons.add('REVIEW_MISSING')
            review_state[ph] = UNMET
        else:
            st, used = _review_phase(ctx, ph, task, binding, blocked_ids, obj.get('result'), reasons, notes)
            review_state[ph] = st
            used_reviews.extend(used)
    due_reviews = [p for p, s in review_state.items() if s != NOT_YET_DUE]
    review_ok = all(review_state[p] == MET for p in due_reviews)

    # pass 2: authority and review conditions are derived from what was actually found
    derived = {'missing_authority': any(f.coverage['state'] != 'COVERED' for f in facts_list),
               'missing_review': not review_ok}
    final = [_route(ctx, f, derived) for f in facts_list]
    values = collections.defaultdict(lambda: F)
    order = {F: 0, U: 1, T: 2}
    causes = []
    for vals, why in final:
        causes.extend(why)
        for rid, v in vals.items():
            if order[v] > order[values[rid]]:
                values[rid] = v
    matched = sorted(rid for rid, v in values.items() if v == T)
    possible = sorted(rid for rid, v in values.items() if v == U)
    claimed = set(obj['claimed_rows'])
    understated = set(matched) - claimed - {'R-UNCLASSIFIED'}
    if claimed and understated:
        reasons.add('ROUTE_UNDERSTATED')
        notes.append('Main declared fewer rows than the checker computed: %s' % ', '.join(sorted(understated)))
    required_gates, trusted_kinds = set(), set()
    for rid in matched + possible:
        row = rows_by_id[rid]
        required_gates.update(row['required_gates'])
        if row['authority_evidence'] == 'TRUSTED_VERIFIED':
            trusted_kinds.update(row['trusted_refs_required'])
    # why R-UNCLASSIFIED is in the route (not merely because authority/review is missing)
    first_uncl = any(v.get('R-UNCLASSIFIED') in (T, U) for v, _ in first) or any(why for _, why in first)
    if first_uncl:
        reasons.add('UNCLASSIFIED_OPERATION')
    if any(why for _, why in first if 'unresolved_condition' in why):
        reasons.add('CONDITION_UNRESOLVED')
    if any(v.get('R-READ_DRAFT') == U for v, _ in first):
        reasons.add('PROTECTED_TARGET_UNDETERMINED')
    if 'R-KNOWN_LOSS' in matched:
        reasons.add('KNOWN_PRESERVATION_LOSS')
    if any(f.write_op and not f.known_loss for f in facts_list):
        reasons.add('PRESERVATION_UNKNOWN')

    # grant, path, tool, envelope, recipe gates (record-to-record comparison)
    gate = {}
    grant_reason = {'MISSING': 'GRANT_MISSING', 'INACTIVE': 'GRANT_INACTIVE', 'OUT': 'GRANT_OUT_OF_SCOPE'}
    for f in facts_list:
        if f.coverage['state'] in grant_reason:
            reasons.add(grant_reason[f.coverage['state']])
    covered = [MET if f.coverage['state'] == 'COVERED' else UNMET for f in facts_list]
    gate['GRANT_SCOPE'] = gate['GRANT_EXACT_COVERAGE'] = _worst(covered)
    gate['TOOL_SCOPE'] = _worst([MET if f.coverage['tools'] else UNMET for f in facts_list])
    gate['PATH_SCOPE'] = _worst([MET if f.coverage['paths'] else UNMET for f in facts_list])
    env_states = []
    for f in facts_list:
        if f.env == 'exceeded':
            reasons.add('ENVELOPE_EXCEEDED')
            env_states.append(UNMET)
        elif f.env == 'unmeasured':
            reasons.add('ENVELOPE_UNMEASURED')
            env_states.append(NOT_CHECKED)
        else:
            env_states.append(MET)
    gate['ENVELOPE'] = _worst(env_states)
    gate['RECIPE_VERSION_ACCEPTED'] = _worst([UNMET if f.recipe is None else (MET if f.recipe_accepted == T else NOT_CHECKED)
                                              for f in facts_list])
    deleg, extra_refs = [], []
    for f, action in zip(facts_list, actions):
        if f.op == 'delegate':
            st, more = _delegation(ctx, action, f.coverage, binding, reasons, notes)
            deleg.append(st)
            extra_refs.extend(more)
    gate['DELEGATE_SCOPE'] = _worst(deleg) if deleg else MET

    # binding to the task, and retry reconciliation
    if binding is not None and task is not None:
        problems = []
        if _digest_set(binding.get('inputs')) != _digest_set(task.get('inputs')):
            problems.append('inputs')
        if obj['kind'] == 'effect' and _action_key(actions[0]) not in [_action_key(a) for a in _task_actions(task)]:
            problems.append('action not in task')
        if problems:
            reasons.add('BINDING_MISMATCH')
            notes.append('binding differs from the task on: %s' % ', '.join(problems))
    if obj['kind'] == 'result' and not _bound_artifacts_match(obj['result']):
        reasons.add('BINDING_MISMATCH')
        notes.append('result artifacts do not match their bound outputs including provenance/revision')
    if obj['kind'] == 'effect':
        key = _action_key(actions[0])
        for e in ctx.effects:
            if e['stage'] == 'OUTCOME' and e['binding'].get('task_id') == binding.get('task_id') \
                    and _action_key(e['action']) == key and (e.get('outcome') or {}).get('status') in ('UNKNOWN', 'PARTIAL'):
                reasons.add('RETRY_UNRECONCILED')
    if binding is None:
        gate['BINDING'] = NOT_CHECKED
    else:
        gate['BINDING'] = MET if ('BINDING_MISMATCH' not in reasons and review_ok) else UNMET

    # observation gates: never MET before G-03 (no bytes, operation or outcome is observed)
    gate['INPUT_REVISION'] = NOT_CHECKED
    gate['PRESERVATION'] = UNMET if any(f.known_loss for f in facts_list) else NOT_CHECKED
    gate['ACTUAL_OUTCOME'] = NOT_CHECKED
    gate['SKILL_INTAKE_STANDARD'] = NOT_CHECKED
    gate['SOURCE_SCOPE_AND_CONCLUSION'] = UNMET if review_state.get('PRE_DELIVERY') == UNMET else NOT_CHECKED
    if obj['kind'] == 'result':
        _accept_checks(ctx, obj, task, reasons, notes, gate)

    # trusted references: claims inside records are listed, never accepted
    refs, trusted = [], []
    if 'user_intent' in trusted_kinds:
        if task is None:
            reasons.add('TRUSTED_VERIFICATION_UNAVAILABLE')
        else:
            refs += [(r, 'user_intent') for r in task['intent']['refs']]
    if 'grant' in trusted_kinds:
        if not grants:
            reasons.add('TRUSTED_VERIFICATION_UNAVAILABLE')
        refs += [(g['issuer_ref'], 'grant') for g in grants]
        if task is not None:
            refs += [(r, 'grant') for r in task['authority']['grant_refs']]
    if 'recipe_acceptance' in trusted_kinds:
        for f in facts_list:
            if f.recipe is None:
                reasons.add('RECIPE_NOT_ACCEPTED')
            else:
                refs.append((f.recipe['acceptance_ref'], 'recipe_acceptance'))
    if 'reviewer_eligibility' in trusted_kinds:
        refs += [(r['reviewer']['eligibility_ref'], 'reviewer_eligibility') for r in used_reviews]
    refs += extra_refs
    seen = set()
    for ref, kind in refs:
        if ref is None:
            reasons.add('TRUSTED_VERIFICATION_UNAVAILABLE')
            continue
        mark = (kind, ref.get('ref_id'), ref.get('digest'), ref.get('trust_anchor'))
        if mark in seen:
            continue
        seen.add(mark)
        state, why = _check_ref(ctx, ref, kind)
        if why:
            reasons.add(why)
        trusted.append({'kind': kind, 'ref_id': ref.get('ref_id'), 'trust_anchor': ref.get('trust_anchor'),
                        'claimed_verification': (ref.get('verification') or {}).get('status'), 'checked': state})
    trust_ok = all(t['checked'] == 'VERIFIED' for t in trusted) and \
        not ({'TRUSTED_VERIFICATION_UNAVAILABLE', 'RECIPE_NOT_ACCEPTED'} & reasons)

    gates = {}
    for g in sorted(required_gates | ({'REQUIREMENTS', 'ACTUAL_OUTCOME'} if obj['kind'] == 'result' else set())):
        gates[g] = {'status': _gate_status(g, phase, gate[g]), 'due_in': GATE_DUE[g]}
    for ph, st in sorted(review_state.items()):
        gates['review:' + ph] = {'status': st, 'due_in': REVIEW_DUE[ph]}
    gates_blocked = [g for g, v in gates.items() if v['status'] in (UNMET, NOT_CHECKED)]
    for g, v in gates.items():
        if v['status'] == NOT_CHECKED and g in ('INPUT_REVISION', 'PRESERVATION', 'ACTUAL_OUTCOME'):
            reasons.add('OBSERVATION_UNAVAILABLE')
        elif v['status'] == NOT_CHECKED and g == 'SKILL_INTAKE_STANDARD':
            reasons.add('OUT_OF_CHECKER_SCOPE')

    if ctx.verifier.trust_basis == 'SIMULATED':
        reasons.add('SIMULATED_VERIFIER_NOT_AUTHORITY')
    if not ctx.canonical:
        reasons.add('NONCANONICAL_OWNER')
    if reasons & DENY_REASONS:
        disposition = 'DENY'
    elif reasons & UNSUPPORTED_REASONS:
        disposition = 'UNSUPPORTED'
    elif reasons or gates_blocked or not trust_ok or 'R-UNCLASSIFIED' in matched + possible:
        disposition = 'BLOCKED'
    else:
        disposition = 'PASS'
    record_issues = sorted(c for c in reasons if REASON_CLASS.get(c) == 'RECORD')
    return {
        'object': {'kind': obj['kind'], 'id': obj['id'], 'phase': phase},
        'disposition': disposition,
        'effect_authorized': False,
        'assurance_level': 'ADVISORY' if disposition == 'PASS' else 'UNVERIFIED',
        'reasons': sorted(reasons),
        'record_consistency': {'status': 'INCONSISTENT' if record_issues else 'CONSISTENT',
                               'level': 'ADVISORY', 'issues': record_issues,
                               'note': 'record-to-record comparison only; not a safety or permission conclusion'},
        'routes': {'matched': matched, 'possible': possible, 'claimed_by_main': sorted(claimed)},
        'required_review_phases': sorted(phases_needed),
        'gates': gates,
        'trusted_refs': trusted,
        'notes': notes,
    }


def _accept_checks(ctx, obj, task, reasons, notes, gate_status):
    result = obj['result']
    if task is None:
        gate_status['REQUIREMENTS'] = NOT_CHECKED
        return
    approved = set(_action_key(a) for a in task['effects']['actions'])
    performed = result.get('actions_performed')
    if performed is not None:
        extra = [a for a in performed if _action_key(a) not in approved]
        if extra:
            reasons.add('BINDING_MISMATCH')
            notes.append('result reports actions that the task did not approve')
    by_id = dict((r['req_id'], r) for r in result.get('requirements') or [])
    evidence = dict((e['evidence_id'], e) for e in result.get('evidence') or [])
    unmet = False
    for req in task['acceptance']['requirements']:
        if not req.get('mandatory'):
            continue
        item = by_id.get(req['req_id'])
        if item is None or item.get('status') != 'MET':
            reasons.add('MANDATORY_REQUIREMENT_NOT_MET')
            unmet = True
            continue
        refs = item.get('evidence_ids') or []
        if not refs or any(i not in evidence or evidence[i].get('req_id') != req['req_id'] for i in refs):
            reasons.add('EVIDENCE_REFERENCE_INVALID')
            unmet = True
    if not unmet:
        reasons.add('EVIDENCE_NOT_VERIFIED')
        notes.append('requirements are claimed MET; evidence kind labels and locators are claims, not observation')
    gate_status['REQUIREMENTS'] = UNMET if unmet else NOT_CHECKED
    claimed = set(result.get('acceptance_states') or []) - {'CANDIDATE'}
    if claimed:
        reasons.add('ACCEPTANCE_CLAIM_NOT_SUPPORTED')
        notes.append('claimed states %s cannot be supported by this checker' % ', '.join(sorted(claimed)))


# ---------------------------------------------------------------- objects per phase
def _task_actions(task):
    return task['effects']['actions']


def _objects(ctx, phase):
    objs = []
    if phase == 'dispatch':
        for task in ctx.tasks_list:
            for i, action in enumerate(_task_actions(task)):
                objs.append({'kind': 'task_action', 'id': '%s@%s#%d' % (task['task_id'], task['task_revision'], i),
                             'task': task, 'actor': task['authority']['subject'], 'actions': [action],
                             'binding': None, 'grant_ref_ids': [],
                             'claimed_rows': (task.get('route_proposal') or {}).get('proposed_rows', [])})
    elif phase == 'effect':
        for e in ctx.effects:
            if e['stage'] != 'REQUEST':
                continue
            b = e['binding']
            task = ctx.task(b['task_id'], b['task_revision'])
            objs.append({'kind': 'effect', 'id': e['effect_id'], 'task': task, 'task_wanted': (b['task_id'], b['task_revision']),
                         'actor': e['actor'], 'actions': [e['action']], 'binding': b,
                         'grant_ref_ids': e.get('grant_ref_ids') or [],
                         'claimed_rows': e['routing'].get('matched_rows', [])})
    else:
        for r in ctx.results:
            b = r['binding']
            task = ctx.task(b['task_id'], b['task_revision'])
            actions = list(_task_actions(task)) if task is not None else list(r.get('actions_performed') or [])
            objs.append({'kind': 'result', 'id': r['result_id'], 'task': task, 'task_wanted': (b['task_id'], b['task_revision']),
                         'actor': r['produced_by'], 'actions': actions or [{'operation': 'unknown', 'tool': 'unknown', 'targets': [], 'write_zone': 'unknown'}],
                         'binding': b, 'result': r, 'grant_ref_ids': [], 'claimed_rows': []})
    return objs


# ---------------------------------------------------------------- top-level API
def _blank(phase, disposition, reasons, details=None, coverage=None, init_error=False):
    return {
        'check_version': RESULT_VERSION, 'phase': phase, 'disposition': disposition,
        'effect_authorized': False, 'assurance_level': 'UNVERIFIED', 'reasons': sorted(reasons),
        'objects': [], 'details': details or [], 'init_error': init_error,
        'coverage': coverage or _coverage(0, False),
    }


def _coverage(count, schema_checked, extra=None):
    cov = {
        'objects_examined': count, 'schema_checked': schema_checked,
        'artifact_bytes_observed': False, 'actual_operation_observed': False,
        'digests_compared_between_records_only': True, 'envelope_enforced_by_host': False,
        'scope_enforced_by_host': False,
        'not_checked': ['current input/artifact bytes', 'real operation and outcome', 'preservation of real files',
                        'semantic correctness of content', 'authenticity of intent, grant and reviewer'],
    }
    if extra:
        cov['not_checked'].extend(extra)
    return cov


def exit_code(result):
    if result.get('init_error'):
        return 2
    return {'PASS': 0, 'NOT_APPLICABLE': 3}.get(result['disposition'], 1)


def check(bundle, phase, verifier=None, schema=None, policy=None, now=None):
    """Check one bundle (or a single record) for one phase. Returns a plain dict."""
    if phase not in PHASES:
        raise ValueError('phase must be one of %s' % ', '.join(PHASES))
    verifier = verifier or NoVerifier()
    if jsonschema is None or not hasattr(jsonschema, 'Draft202012Validator'):
        return _blank(phase, 'UNSUPPORTED', {'DEPENDENCY_MISSING'},
                      ['jsonschema with Draft 2020-12 support is required; install it or run in an environment that has it'], init_error=True)
    canonical = schema is None and policy is None
    try:
        schema_bytes = CANONICAL_SCHEMA.read_bytes() if schema is None else None
        policy_bytes = CANONICAL_POLICY.read_bytes() if policy is None else None
        schema_obj = parse_json_bytes(schema_bytes) if schema is None else schema
        policy_obj = parse_json_bytes(policy_bytes) if policy is None else policy
    except (OSError, InputError) as exc:
        return _blank(phase, 'UNSUPPORTED', {'INPUT_MALFORMED'}, ['cannot load canonical schema/policy: %s' % exc], init_error=True)
    if _has_remote_ref(schema_obj):
        return _blank(phase, 'UNSUPPORTED', {'SCHEMA_VERSION_UNKNOWN'}, ['schema has a non-local $ref; remote references are refused'], init_error=True)
    if schema_obj.get('$id') != SCHEMA_ID:
        return _blank(phase, 'UNSUPPORTED', {'SCHEMA_VERSION_UNKNOWN'}, ['schema $id is not %s' % SCHEMA_ID], init_error=True)
    if policy_obj.get('policy_version') != POLICY_VERSION or policy_obj.get('schema_version') != SCHEMA_VERSION:
        return _blank(phase, 'UNSUPPORTED', {'POLICY_VERSION_UNKNOWN'}, ['policy version is not %s' % POLICY_VERSION], init_error=True)
    try:
        validator = Draft202012Validator(schema_obj, format_checker=FormatChecker())
        Draft202012Validator.check_schema(schema_obj)
    except Exception as exc:
        return _blank(phase, 'UNSUPPORTED', {'SCHEMA_VERSION_UNKNOWN'}, ['schema is not a valid Draft 2020-12 schema: %s' % exc], init_error=True)
    meta = {
        'schema': {'id': SCHEMA_ID, 'canonical': canonical,
                   'sha256': _sha256(schema_bytes) if schema_bytes else None},
        'policy': {'id': policy_obj.get('policy_id'), 'version': policy_obj.get('policy_version'),
                   'status': policy_obj.get('status'), 'canonical': canonical,
                   'sha256': _sha256(policy_bytes) if policy_bytes else None},
        'canonical_owners': canonical, 'canonical_bytes_verified': False, 'owner_protection': 'NOT_PROVEN',
        'verifier': {'trust_basis': verifier.trust_basis},
    }
    format_gap = [] if 'date-time' in FormatChecker.checkers else ['date-time format (no format library installed)']

    def fail(disposition, reasons, details):
        out = _blank(phase, disposition, reasons, details, _coverage(0, True, format_gap))
        out.update(meta)
        return out

    errs = list(Draft202012Validator(schema_obj).iter_errors(policy_obj))
    if errs:
        return fail('UNSUPPORTED', {'POLICY_VERSION_UNKNOWN'}, ['policy does not validate: %s' % errs[0].message])
    if not isinstance(bundle, dict):
        return fail('DENY', {'INPUT_MALFORMED'}, ['input is not a JSON object'])
    records = bundle.get('records') if bundle.get('record_type') == 'bundle' else [bundle]
    versions = [bundle.get('schema_version')] + [r.get('schema_version') for r in (records or []) if isinstance(r, dict)]
    if any(v != SCHEMA_VERSION for v in versions):
        return fail('UNSUPPORTED', {'SCHEMA_VERSION_UNKNOWN'}, ['unknown schema_version: %s' % sorted(set(str(v) for v in versions))])
    errors = sorted(validator.iter_errors(bundle), key=lambda e: list(e.absolute_path))
    if errors:
        details = ['%s: %s' % ('/'.join(str(p) for p in e.absolute_path) or '<root>', e.message[:160]) for e in errors[:10]]
        return fail('DENY', {'SCHEMA_INVALID'}, details)
    if any(r.get('record_type') == 'routing_policy' for r in records):
        return fail('DENY', {'SCHEMA_INVALID'}, ['a routing_policy is not a checkable record; the canonical policy is fixed'])
    ctx = Ctx(records, policy_obj, verifier, now or datetime.datetime.now(datetime.timezone.utc), canonical)
    objects = [_evaluate(ctx, phase, o) for o in _objects(ctx, phase)]
    out = _blank(phase, 'NOT_APPLICABLE', set(), [], _coverage(len(objects), True, format_gap))
    out.update(meta)
    out['objects'] = objects
    out['reasons'] = sorted(set(ctx.global_reasons))
    if ctx.ambiguous:
        out['details'] = ['ambiguous ids: %s' % ', '.join(sorted(ctx.ambiguous))]
    if objects:
        worst = max(objects, key=lambda o: RANK[o['disposition']])
        out['disposition'] = worst['disposition']
        out['assurance_level'] = 'ADVISORY' if all(o['assurance_level'] == 'ADVISORY' for o in objects) else 'UNVERIFIED'
    elif ctx.global_reasons:
        out['disposition'] = 'BLOCKED'
    return out


# ---------------------------------------------------------------- CLI
def _format_text(result):
    lines = ['%s phase=%s disposition=%s effect_authorized=false assurance=%s' % (
        result['check_version'], result['phase'], result['disposition'], result['assurance_level'])]
    if result.get('reasons'):
        lines.append('reasons: ' + ', '.join(result['reasons']))
    for d in result.get('details', []):
        lines.append('detail: ' + d)
    for o in result['objects']:
        lines.append('- %s %s: %s (record_consistency=%s)' % (o['object']['kind'], o['object']['id'], o['disposition'],
                                                              o['record_consistency']['status']))
        lines.append('    reasons: ' + ', '.join(o['reasons']))
    cov = result['coverage']
    lines.append('coverage: objects=%d artifact_bytes_observed=%s actual_operation_observed=%s' % (
        cov['objects_examined'], cov['artifact_bytes_observed'], cov['actual_operation_observed']))
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Read-only LAW control record checker (G-02). Never authorizes an effect.')
    ap.add_argument('bundle', help='bundle or single record JSON file')
    ap.add_argument('--phase', required=True, choices=PHASES)
    ap.add_argument('--format', choices=('json', 'text'), default='json')
    args = ap.parse_args(argv)
    try:
        data = Path(args.bundle).read_bytes()
    except OSError as exc:
        sys.stderr.write('cannot read %s: %s\n' % (args.bundle, exc))
        return 2
    try:
        bundle = parse_json_bytes(data)
    except InputError as exc:
        result = _blank(args.phase, 'DENY', {'INPUT_MALFORMED'}, [str(exc)])
    else:
        result = check(bundle, args.phase)
    sys.stdout.write((_format_text(result) if args.format == 'text' else json.dumps(result, indent=2, ensure_ascii=False)) + '\n')
    return exit_code(result)


if __name__ == '__main__':
    sys.exit(main())
