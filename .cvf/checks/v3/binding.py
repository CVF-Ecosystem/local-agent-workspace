"""Helper (copy-forward S2 v2): kernel projection theo phần và comparator binding/tập/pointer, trong bộ nhớ / projection kernel and comparators.

Hàm thuần, không I/O, không mạng, không cache. Kết quả mô tả TÍNH LẠI / SO SÁNH, không phải PASS, MET, quyền, receipt, "stale" hay xác nhận
byte/nguồn: digest object nghĩa là byte file thô chưa quan sát. Kernel chỉ gọi đúng projection C1 (canon.py) cho từng phần; phần nào ngoài
miền canonical chỉ làm chính phần đó UNSUPPORTED. Metadata bị loại khỏi hash không bị canonicalize ở đây (chúng vẫn qua schema và nhóm lời khai).
Comparison and recomputation only. Peer equality never counts as recomputation. Kết quả không chia sẻ container mutable với đầu vào và không echo giá trị record.
"""
import re
from dataclasses import dataclass

from . import (BIND_VERSION, EVALUATION_BASIS, POLICY_STATUS, POLICY_VERSION, SCHEMA_VERSION, canon)
from .loader import InputError, parse_json_bytes
from .refs import FIELD_VOCAB, Relation, RecordIndex, _Plain, is_int, loc, vkey

MODES = ('EXACT_QUALIFIED', 'COVER_REQUIRED_QUALIFIERS')
BOUND_KEYS = ('path', 'digest', 'source_id', 'revision', 'scope')
PEER_FIELDS = ('bind_version', 'evaluation_basis', 'task_id', 'task_revision', 'intent_digest', 'accepted_task_digest',
               'context_digest', 'policy_version', 'policy_digest', 'inputs', 'outputs', 'action_digest')
POINTER_FIELDS = ('task_id', 'task_revision', 'accepted_task_digest', 'context_digest')
MANDATORY = ('B-REF', 'B-INTENT', 'B-TASK', 'B-CONTEXT', 'B-POLICY', 'B-INPUTS')
OPTIONAL = ('B-ACTION-OWN', 'B-ACTION-IN-TASK', 'B-ACTION-CLAIM', 'B-OUT-RESULT', 'B-OUT-EFFECT')
COMPUTED_STATES = ('MATCH', 'MISMATCH')
OBJECT_SET_NAMES = ('object_sets', 'scope', 'B-INPUTS', 'B-OUT-RESULT', 'B-OUT-EFFECT', 'C-INPUTS', 'D4-ARTIFACTS', 'peer.inputs',
                    'peer.outputs')
OBJECT_SET_BASES = ('DECLARED_SET', 'PEER_CLAIM')
_SET_LOCATION_FIELDS = FIELD_VOCAB | frozenset(('scope', 'objects'))
_MALFORMED = (KeyError, TypeError, AttributeError, IndexError, ValueError, RecursionError)


# ---------------------------------------------------------------- kiểu kết quả / result types
@dataclass(frozen=True)
class Part(_Plain):
    state: str
    digest: object = None
    reason: object = None


@dataclass(frozen=True)
class TaskDigests(_Plain):
    intent: Part
    accepted_task: Part
    context: Part
    actions: tuple = ()
    actions_malformed: bool = False


@dataclass(frozen=True)
class PolicyContext(_Plain):
    state: str
    digest: object = None
    literals_ok: bool = False
    reason: object = None


@dataclass(frozen=True)
class BindingReport(_Plain):
    _FLAGS = True
    position: int
    applicable: bool
    relations: tuple
    recomputation_complete: bool


def _rel(name, state, basis, locator='', reason=None, **kw):
    return Relation(name, state, basis, locator, reason, tuple(kw.get('fields', ())), tuple(kw.get('indexes', ())),
                    tuple(kw.get('counts', ())), tuple(kw.get('limitations', ())))


# ---------------------------------------------------------------- policy
def make_policy_context(policy_bytes):
    """Parse bản policy riêng từ bytes (strict), kiểm literal và tính policy_part. Không dùng dict dùng chung từ cache."""
    if not isinstance(policy_bytes, bytes):
        raise TypeError('policy_bytes must be bytes')
    try:
        obj = parse_json_bytes(policy_bytes)
    except InputError:
        return PolicyContext('UNSUPPORTED', None, False, 'MALFORMED_RECORD')
    literals_ok = (obj.get('policy_version') == POLICY_VERSION and obj.get('schema_version') == SCHEMA_VERSION
                   and obj.get('evaluation_basis') == EVALUATION_BASIS and obj.get('status') == POLICY_STATUS)
    try:
        digest = canon.digest_of(canon.policy_part(obj))
    except canon.Unsupported as exc:
        return PolicyContext('UNSUPPORTED', None, literals_ok, exc.reason)
    except _MALFORMED:
        return PolicyContext('UNSUPPORTED', None, literals_ok, 'MALFORMED_RECORD')
    if not literals_ok:
        return PolicyContext('UNSUPPORTED', None, False, 'POLICY_LITERAL_MISMATCH')
    return PolicyContext('COMPUTED', digest, True, None)


# ---------------------------------------------------------------- kernel
def _part(build):
    try:
        return Part('COMPUTED', canon.digest_of(build()), None)
    except canon.Unsupported as exc:
        return Part('UNSUPPORTED', None, exc.reason)
    except _MALFORMED:
        return Part('UNSUPPORTED', None, 'MALFORMED_RECORD')


def _action_parts(task):
    effects = task.get('effects')
    actions = effects.get('actions') if isinstance(effects, dict) else None
    if not isinstance(actions, list):
        return (), True
    return tuple(_part(lambda a=a: canon.action_part(a)) for a in actions), False


def recompute_task(task):
    """Tính lại digest theo từng phần projection C1; một phần UNSUPPORTED không che các phần khác. Không canonicalize metadata ngoài hash."""
    if not isinstance(task, dict):
        raise TypeError('task must be a dict')
    actions, malformed = _action_parts(task)
    return TaskDigests(_part(lambda: canon.intent_part(task)), _part(lambda: canon.task_part(task)),
                       _part(lambda: canon.context_part(task)), actions, malformed)


# ---------------------------------------------------------------- tập đối tượng
def _object_keys(items):
    """Danh sách khóa canonical của obj_proj; (keys, None) hoặc (None, reason). Trùng phần tử ⇒ DUPLICATE_SET_ELEMENT, không dedupe."""
    if not isinstance(items, list):
        return None, 'MALFORMED_RECORD'
    keys = []
    for o in items:
        if not isinstance(o, dict) or not isinstance(o.get('path'), str) or not isinstance(o.get('digest'), str):
            return None, 'MALFORMED_RECORD'
        try:
            keys.append(canon.canonical_bytes(canon.obj_proj(o)))
        except canon.Unsupported as exc:
            return None, exc.reason
        except _MALFORMED:
            return None, 'MALFORMED_RECORD'
    if len(set(keys)) != len(keys):
        return None, 'DUPLICATE_SET_ELEMENT'
    return keys, None


def _covers(summary, artifact):
    for k in BOUND_KEYS:
        if k in summary and (k not in artifact or vkey(artifact[k]) != vkey(summary[k])):
            return False
    return True


def compare_object_sets(left, right, mode, name='object_sets', locator='', basis='DECLARED_SET'):
    """So hai tập object_digest khai báo. Digest nghĩa là byte file thô CHƯA quan sát (limitations)."""
    if mode not in MODES:
        raise ValueError('mode must be one of %s' % ', '.join(MODES))
    if not isinstance(name, str):
        raise TypeError('name must be a str')
    if name not in OBJECT_SET_NAMES:
        raise ValueError('unknown object-set relation name')
    if not isinstance(basis, str):
        raise TypeError('basis must be a str')
    if basis not in OBJECT_SET_BASES:
        raise ValueError('object-set basis must describe declared sets or peer claims')
    if not isinstance(locator, str):
        raise TypeError('locator must be a str')
    if not re.fullmatch(r'(?:records\[[0-9]+\])?(?:\.[a-z_]+|\.\?|\[[0-9]+\])*', locator) \
            or any(field != '?' and field not in _SET_LOCATION_FIELDS
                   for field in re.findall(r'\.([a-z_]+|\?)', locator)):
        raise ValueError('locator must use the closed source-position vocabulary')
    limits = ('UNVERIFIED_RAW_BYTES',)

    def out(state, reason=None, counts=()):
        return _rel(name, state, basis, locator, reason, counts=counts, limitations=limits)

    if left is None and right is None:
        return out('NOT_BOUND')
    if left is None or right is None:
        return out('ONE_SIDED')
    lk, reason = _object_keys(left)
    if reason:
        return out('UNSUPPORTED', reason)
    rk, reason = _object_keys(right)
    if reason:
        return out('UNSUPPORTED', reason)
    if mode == 'EXACT_QUALIFIED':
        only_left, only_right = len(set(lk) - set(rk)), len(set(rk) - set(lk))
    else:
        only_left = sum(1 for s in left if not any(_covers(s, a) for a in right))
        only_right = sum(1 for a in right if not any(_covers(s, a) for s in left))
    state = 'MATCH' if not only_left and not only_right else 'MISMATCH'
    return out(state, None, (('only_left', only_left), ('only_right', only_right)))


# ---------------------------------------------------------------- peer
def compare_peer_bindings(a, b):
    """So hai binding theo từng trường (PEER_CLAIM). Không bao giờ là tính lại và không cộng vào recomputation_complete."""
    if not isinstance(a, dict) or not isinstance(b, dict):
        raise TypeError('bindings must be dicts')
    out = []
    for field in PEER_FIELDS:
        name, where = 'peer.' + field, loc(None, 'binding', field)
        in_a, in_b = field in a, field in b
        if not in_a and not in_b:
            out.append(_rel(name, 'NOT_BOUND', 'PEER_CLAIM', where))
        elif field in ('inputs', 'outputs') and ((in_a and not isinstance(a[field], list))
                                                or (in_b and not isinstance(b[field], list))):
            out.append(_rel(name, 'UNSUPPORTED', 'PEER_CLAIM', where, 'MALFORMED_RECORD'))
        elif in_a != in_b:
            out.append(_rel(name, 'ONE_SIDED', 'PEER_CLAIM', where))
        elif field in ('inputs', 'outputs'):
            r = compare_object_sets(a[field], b[field], 'EXACT_QUALIFIED', name=name, locator=where, basis='PEER_CLAIM')
            out.append(r)
        else:
            out.append(_rel(name, 'MATCH' if vkey(a[field]) == vkey(b[field]) else 'MISMATCH', 'PEER_CLAIM', where))
    return tuple(out)


# ---------------------------------------------------------------- binding
def _task_state(index, binding):
    """(Lookup|None, task snapshot|None, reason|None)."""
    tid, trev = binding.get('task_id'), binding.get('task_revision')
    if not isinstance(tid, str) or not is_int(trev):
        return None, None, 'MALFORMED_RECORD'
    look = index.lookup('task', tid, trev)
    if look.status == 'FOUND':
        return look, index._record(look.positions[0]), None
    return look, None, 'TASK_AMBIGUOUS' if look.status == 'AMBIGUOUS' else 'TASK_UNRESOLVED'


def _dependent(name, basis, locator, look, reason, **kw):
    """Quan hệ phụ thuộc task khi task không resolve được."""
    if reason == 'MALFORMED_RECORD':
        return _rel(name, 'UNSUPPORTED', basis, locator, reason, **kw)
    if reason == 'TASK_AMBIGUOUS':
        return _rel(name, 'AMBIGUOUS', basis, locator, reason, **kw)
    return _rel(name, 'INCOMPLETE', basis, locator, reason, **kw)


def _digest_relation(name, position, field, binding, part, task_reason, look):
    where = loc(position, 'binding', field)
    declared = binding.get(field)
    if not isinstance(declared, str):
        return _rel(name, 'UNSUPPORTED', 'RECOMPUTED', where, 'MALFORMED_RECORD')
    if task_reason:
        return _dependent(name, 'RECOMPUTED', where, look, task_reason)
    if part.state != 'COMPUTED':
        return _rel(name, 'UNSUPPORTED', 'RECOMPUTED', where, part.reason)
    return _rel(name, 'MATCH' if declared == part.digest else 'MISMATCH', 'RECOMPUTED', where)


def _match_actions(task_digests, wanted):
    """(indexes, unsupported_reason|None): chỉ số action của task có cùng projection."""
    indexes = tuple(j for j, p in enumerate(task_digests.actions) if p.state == 'COMPUTED' and p.digest == wanted)
    bad = [p.reason for p in task_digests.actions if p.state != 'COMPUTED']
    if task_digests.actions_malformed:
        bad.append('MALFORMED_RECORD')
    return indexes, (bad[0] if bad else None)


def compare_binding(index, position, policy_ctx):
    """Báo cáo quan hệ binding của record tại `position` (review/effect/result). Record không có binding ⇒ applicable=false."""
    if not isinstance(index, RecordIndex):
        raise TypeError('index must be a RecordIndex')
    if not isinstance(policy_ctx, PolicyContext):
        raise TypeError('policy_ctx must be a PolicyContext')
    if not is_int(position):
        raise TypeError('position must be an int')
    if position < 0 or position >= index.count:
        raise ValueError('position out of range')
    rec = index._record(position)
    binding = rec.get('binding')
    rtype = rec.get('record_type')
    if not isinstance(binding, dict) or rtype not in ('review', 'effect', 'result'):
        return BindingReport(position, False, (_rel('binding', 'NOT_APPLICABLE', 'LITERAL', loc(position, 'binding'),
                                                    'NO_BINDING'),), False)
    rels = []
    look, task, reason = _task_state(index, binding)
    where_ref = loc(position, 'binding', 'task_id')
    if reason is None:
        rels.append(_rel('B-REF', 'MATCH', 'RECOMPUTED', where_ref, counts=(('candidates', 1),)))
    else:
        rels.append(_dependent('B-REF', 'RECOMPUTED', where_ref, look, reason,
                               counts=(('candidates', len(look.positions)),) if look is not None else ()))
    for field, const in (('bind_version', BIND_VERSION), ('evaluation_basis', EVALUATION_BASIS), ('policy_version', POLICY_VERSION)):
        ok = field in binding and vkey(binding[field]) == vkey(const)
        rels.append(_rel('B-LIT.' + field, 'MATCH' if ok else 'MISMATCH', 'LITERAL', loc(position, 'binding', field),
                         None if field in binding else 'ABSENT_FIELD'))
    digests = recompute_task(task) if task is not None else None
    for name, field, attr in (('B-INTENT', 'intent_digest', 'intent'), ('B-TASK', 'accepted_task_digest', 'accepted_task'),
                              ('B-CONTEXT', 'context_digest', 'context')):
        rels.append(_digest_relation(name, position, field, binding, getattr(digests, attr) if digests else None, reason, look))
    where = loc(position, 'binding', 'policy_digest')
    declared = binding.get('policy_digest')
    if not isinstance(declared, str):
        rels.append(_rel('B-POLICY', 'UNSUPPORTED', 'RECOMPUTED', where, 'MALFORMED_RECORD'))
    elif policy_ctx.state != 'COMPUTED':
        rels.append(_rel('B-POLICY', 'UNSUPPORTED', 'RECOMPUTED', where, policy_ctx.reason))
    else:
        rels.append(_rel('B-POLICY', 'MATCH' if declared == policy_ctx.digest else 'MISMATCH', 'RECOMPUTED', where))
    where = loc(position, 'binding', 'inputs')
    if 'inputs' not in binding or not isinstance(binding['inputs'], list):
        rels.append(_rel('B-INPUTS', 'UNSUPPORTED', 'DECLARED_SET', where, 'MALFORMED_RECORD'))
    elif reason:
        rels.append(_dependent('B-INPUTS', 'DECLARED_SET', where, look, reason, limitations=('UNVERIFIED_RAW_BYTES',)))
    elif not isinstance(task.get('inputs'), list):
        rels.append(_rel('B-INPUTS', 'UNSUPPORTED', 'DECLARED_SET', where, 'MALFORMED_RECORD'))
    else:
        rels.append(compare_object_sets(binding['inputs'], task.get('inputs'), 'EXACT_QUALIFIED', name='B-INPUTS', locator=where))

    claim = binding.get('action_digest')
    has_claim = 'action_digest' in binding
    where = loc(position, 'binding', 'action_digest')
    if rtype == 'effect':
        action = rec.get('action')
        own = _part(lambda: canon.action_part(action)) if isinstance(action, dict) else Part('UNSUPPORTED', None, 'MALFORMED_RECORD')
        if not has_claim:
            rels.append(_rel('B-ACTION-OWN', 'NOT_BOUND', 'RECOMPUTED', where))
        elif not isinstance(claim, str):
            rels.append(_rel('B-ACTION-OWN', 'UNSUPPORTED', 'RECOMPUTED', where, 'MALFORMED_RECORD'))
        elif own.state != 'COMPUTED':
            rels.append(_rel('B-ACTION-OWN', 'UNSUPPORTED', 'RECOMPUTED', where, own.reason))
        else:
            rels.append(_rel('B-ACTION-OWN', 'MATCH' if claim == own.digest else 'MISMATCH', 'RECOMPUTED', where))
        where = loc(position, 'action')
        if own.state != 'COMPUTED':
            rels.append(_rel('B-ACTION-IN-TASK', 'UNSUPPORTED', 'RECOMPUTED', where, own.reason))
        elif reason:
            rels.append(_dependent('B-ACTION-IN-TASK', 'RECOMPUTED', where, look, reason))
        else:
            idx, bad = _match_actions(digests, own.digest)
            if idx:
                rels.append(_rel('B-ACTION-IN-TASK', 'MATCH', 'RECOMPUTED', where, indexes=idx))
            elif bad:
                rels.append(_rel('B-ACTION-IN-TASK', 'UNSUPPORTED', 'RECOMPUTED', where, bad))
            else:
                rels.append(_rel('B-ACTION-IN-TASK', 'MISMATCH', 'RECOMPUTED', where))
    else:
        if not has_claim:
            rels.append(_rel('B-ACTION-CLAIM', 'NOT_BOUND', 'RECOMPUTED', where))
        elif not isinstance(claim, str):
            rels.append(_rel('B-ACTION-CLAIM', 'UNSUPPORTED', 'RECOMPUTED', where, 'MALFORMED_RECORD'))
        elif reason:
            rels.append(_dependent('B-ACTION-CLAIM', 'RECOMPUTED', where, look, reason, limitations=('SUBSET_OF_ACTIONS_ONLY',)))
        else:
            idx, bad = _match_actions(digests, claim)
            if idx:
                rels.append(_rel('B-ACTION-CLAIM', 'MATCH', 'RECOMPUTED', where, indexes=idx, limitations=('SUBSET_OF_ACTIONS_ONLY',)))
            elif bad:
                rels.append(_rel('B-ACTION-CLAIM', 'UNSUPPORTED', 'RECOMPUTED', where, bad, limitations=('SUBSET_OF_ACTIONS_ONLY',)))
            else:
                rels.append(_rel('B-ACTION-CLAIM', 'MISMATCH', 'RECOMPUTED', where, limitations=('SUBSET_OF_ACTIONS_ONLY',)))

    where = loc(position, 'binding', 'outputs')
    if rtype == 'result':
        if 'outputs' not in binding:
            rels.append(_rel('B-OUT-RESULT', 'NOT_BOUND', 'DECLARED_SET', where, limitations=('UNVERIFIED_RAW_BYTES',)))
        elif not isinstance(binding['outputs'], list) or not isinstance(rec.get('artifacts'), list):
            rels.append(_rel('B-OUT-RESULT', 'UNSUPPORTED', 'DECLARED_SET', where, 'MALFORMED_RECORD',
                             limitations=('UNVERIFIED_RAW_BYTES',)))
        else:
            rels.append(compare_object_sets(binding['outputs'], rec.get('artifacts'), 'EXACT_QUALIFIED', name='B-OUT-RESULT',
                                            locator=where))
    elif rtype == 'effect' and rec.get('stage') == 'OUTCOME':
        outcome = rec.get('outcome')
        artifacts = outcome.get('artifacts') if isinstance(outcome, dict) else None
        if 'outputs' not in binding:
            rels.append(_rel('B-OUT-EFFECT', 'NOT_BOUND', 'DECLARED_SET', where, limitations=('UNVERIFIED_RAW_BYTES',)))
        elif not isinstance(binding['outputs'], list) or not isinstance(artifacts, list):
            rels.append(_rel('B-OUT-EFFECT', 'UNSUPPORTED', 'DECLARED_SET', where, 'MALFORMED_RECORD',
                             limitations=('UNVERIFIED_RAW_BYTES',)))
        else:
            rels.append(compare_object_sets(binding['outputs'], artifacts, 'EXACT_QUALIFIED', name='B-OUT-EFFECT', locator=where))
    elif 'outputs' not in binding:
        rels.append(_rel('B-OUTPUTS', 'NOT_BOUND', 'DECLARED_SET', where))
    elif not isinstance(binding['outputs'], list):
        rels.append(_rel('B-OUTPUTS', 'UNSUPPORTED', 'DECLARED_SET', where, 'MALFORMED_RECORD'))
    else:
        rels.append(_rel('B-OUTPUTS', 'NOT_APPLICABLE', 'DECLARED_SET', where, 'NO_COUNTERPART'))

    required = [r for r in rels if r.name in MANDATORY or (r.name in OPTIONAL and r.state not in ('NOT_BOUND', 'NOT_APPLICABLE'))]
    complete = bool(required) and all(r.state in COMPUTED_STATES for r in required)
    return BindingReport(position, True, tuple(rels), complete)


# ---------------------------------------------------------------- pointers
def _pointer_ok(p):
    return (isinstance(p, dict) and isinstance(p.get('task_id'), str) and is_int(p.get('task_revision'))
            and isinstance(p.get('accepted_task_digest'), str) and isinstance(p.get('context_digest'), str))


def _digest_pair(prefix, index, pointer, where):
    """P-/C- RESOLVE + TASK/CONTEXT digest so với task tra theo pointer. Trả (relations, look, task snapshot|None)."""
    look = index.lookup('task', pointer['task_id'], pointer['task_revision'])
    counts = (('candidates', len(look.positions)),)
    if look.status == 'FOUND':
        task = index._record(look.positions[0])
        d = recompute_task(task)
        rels = [_rel(prefix + '-RESOLVE', 'MATCH', 'RECOMPUTED', where, counts=counts)]
        for name, field, part in ((prefix + '-TASK-DIGEST', 'accepted_task_digest', d.accepted_task),
                                  (prefix + '-CONTEXT-DIGEST', 'context_digest', d.context)):
            if part.state != 'COMPUTED':
                rels.append(_rel(name, 'UNSUPPORTED', 'RECOMPUTED', where, part.reason))
            else:
                rels.append(_rel(name, 'MATCH' if pointer[field] == part.digest else 'MISMATCH', 'RECOMPUTED', where))
        return rels, look, task
    state, why = ('AMBIGUOUS', 'TASK_AMBIGUOUS') if look.status == 'AMBIGUOUS' else ('INCOMPLETE', 'TASK_UNRESOLVED')
    return [_rel(prefix + '-RESOLVE', state, 'RECOMPUTED', where, why, counts=counts),
            _rel(prefix + '-TASK-DIGEST', state, 'RECOMPUTED', where, why),
            _rel(prefix + '-CONTEXT-DIGEST', state, 'RECOMPUTED', where, why)], look, None


def _pointer_malformed(prefix, where, names):
    return [_rel(prefix + '-' + n, 'UNSUPPORTED', 'RECOMPUTED', where, 'MALFORMED_RECORD') for n in names]


def _delegations(position, rec):
    rtype = rec.get('record_type')
    found = []
    if rtype == 'task':
        effects = rec.get('effects')
        actions = effects.get('actions') if isinstance(effects, dict) else None
        if isinstance(actions, list):
            for j, a in enumerate(actions):
                if isinstance(a, dict) and isinstance(a.get('delegation'), dict):
                    found.append((loc(position, 'effects', 'actions', j, 'delegation'), a['delegation']))
    elif rtype == 'effect':
        a = rec.get('action')
        if isinstance(a, dict) and isinstance(a.get('delegation'), dict):
            found.append((loc(position, 'action', 'delegation'), a['delegation']))
    return found


def _containing_key(rec):
    if rec.get('record_type') == 'task':
        return rec.get('task_id'), rec.get('task_revision')
    binding = rec.get('binding')
    if isinstance(binding, dict):
        return binding.get('task_id'), binding.get('task_revision')
    return None, None


def compare_pointers(index, position, policy_ctx):
    """Quan hệ độc lập cho từng pointer cha/con của action có delegation trong task hoặc effect. Record khác ⇒ ()."""
    if not isinstance(index, RecordIndex):
        raise TypeError('index must be a RecordIndex')
    if not isinstance(policy_ctx, PolicyContext):
        raise TypeError('policy_ctx must be a PolicyContext')
    if not is_int(position):
        raise TypeError('position must be an int')
    if position < 0 or position >= index.count:
        raise ValueError('position out of range')
    rec = index._record(position)
    out = []
    for base, deleg in _delegations(position, rec):
        parent, child = deleg.get('parent_task'), deleg.get('child_task')
        pwhere, cwhere = base + '.parent_task', base + '.child_task'
        if _pointer_ok(parent):
            rels, _, _ = _digest_pair('P', index, parent, pwhere)
            out.extend(rels)
            key = _containing_key(rec)
            if isinstance(key[0], str) and is_int(key[1]):
                same = key[0] == parent['task_id'] and key[1] == parent['task_revision']
                out.append(_rel('P-SELF', 'MATCH' if same else 'MISMATCH', 'PEER_CLAIM', pwhere))
            else:
                out.append(_rel('P-SELF', 'UNSUPPORTED', 'PEER_CLAIM', pwhere, 'MALFORMED_RECORD'))
            if rec.get('record_type') == 'effect':
                binding = rec.get('binding') if isinstance(rec.get('binding'), dict) else {}
                differ = tuple(f for f in POINTER_FIELDS if f not in binding or vkey(binding[f]) != vkey(parent[f]))
                out.append(_rel('P-EFFECT', 'MISMATCH' if differ else 'MATCH', 'PEER_CLAIM', pwhere, fields=differ))
        else:
            out.extend(_pointer_malformed('P', pwhere, ('RESOLVE', 'TASK-DIGEST', 'CONTEXT-DIGEST')))
            out.append(_rel('P-SELF', 'UNSUPPORTED', 'PEER_CLAIM', pwhere, 'MALFORMED_RECORD'))
            if rec.get('record_type') == 'effect':
                out.append(_rel('P-EFFECT', 'UNSUPPORTED', 'PEER_CLAIM', pwhere, 'MALFORMED_RECORD'))
        if not _pointer_ok(child):
            out.extend(_pointer_malformed('C', cwhere, ('RESOLVE', 'TASK-DIGEST', 'CONTEXT-DIGEST')))
            out.append(_rel('C-BASIS', 'UNSUPPORTED', 'PEER_CLAIM', cwhere, 'MALFORMED_RECORD'))
            out.append(_rel('C-INPUTS', 'UNSUPPORTED', 'DECLARED_SET', cwhere, 'MALFORMED_RECORD'))
            continue
        rels, look, child_task = _digest_pair('C', index, child, cwhere)
        out.extend(rels)
        basis_positions = []
        for p in range(index.count):
            other = index._record(p)
            b = other.get('binding')
            if other.get('record_type') in ('review', 'effect', 'result') and isinstance(b, dict) \
                    and b.get('task_id') == child['task_id'] and is_int(b.get('task_revision')) \
                    and b['task_revision'] == child['task_revision'] and isinstance(b.get('task_id'), str):
                basis_positions.append(p)
        counts = (('basis_records', len(basis_positions)),)
        if not basis_positions:
            out.append(_rel('C-BASIS', 'INCOMPLETE', 'PEER_CLAIM', cwhere, 'NO_BASIS_RECORD', counts=counts))
        else:
            differ = set()
            for p in basis_positions:
                b = index._record(p)['binding']
                for f in ('accepted_task_digest', 'context_digest'):
                    if f not in b or vkey(b[f]) != vkey(child[f]):
                        differ.add(f)
            ordered = tuple(f for f in POINTER_FIELDS if f in differ)
            out.append(_rel('C-BASIS', 'MISMATCH' if ordered else 'MATCH', 'PEER_CLAIM', cwhere, fields=ordered, counts=counts))
        if child_task is None:
            state, why = ('AMBIGUOUS', 'TASK_AMBIGUOUS') if look.status == 'AMBIGUOUS' else ('INCOMPLETE', 'TASK_UNRESOLVED')
            out.append(_rel('C-INPUTS', state, 'DECLARED_SET', cwhere, why, counts=counts, limitations=('UNVERIFIED_RAW_BYTES',)))
        elif not basis_positions:
            out.append(_rel('C-INPUTS', 'INCOMPLETE', 'DECLARED_SET', cwhere, 'NO_BASIS_RECORD', counts=counts,
                            limitations=('UNVERIFIED_RAW_BYTES',)))
        else:
            results = [compare_object_sets(index._record(p)['binding'].get('inputs'), child_task.get('inputs'), 'EXACT_QUALIFIED',
                                           name='C-INPUTS', locator=cwhere) for p in basis_positions]
            bad = [r for r in results if r.state == 'UNSUPPORTED']
            if bad:
                state, why = 'UNSUPPORTED', bad[0].reason
            elif any(r.state != 'MATCH' for r in results):
                state, why = 'MISMATCH', None
            else:
                state, why = 'MATCH', None
            out.append(_rel('C-INPUTS', state, 'DECLARED_SET', cwhere, why, counts=counts, limitations=('UNVERIFIED_RAW_BYTES',)))
    return tuple(out)
