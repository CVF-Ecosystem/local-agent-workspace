"""Helper (copy-forward S2 v2): index record, nhóm lời khai inline và liên kết grant, trong bộ nhớ / in-memory record index, inline claim groups, grant links.

Hàm thuần: không I/O, không mạng, không cache hay trạng thái giữa các lần gọi. Mọi kết quả chỉ mô tả so sánh/liên kết, KHÔNG phải PASS,
quyền, receipt hay xác minh nguồn. Kết quả công khai không chia sẻ container mutable với đầu vào; không echo
id, path, digest thô hay tên khóa (chỉ vị trí nguồn, locator đóng, tên trường đóng, reason đóng, số đếm).
Pure functions. Results describe comparison/linkage only and are not a PASS, an authority, a receipt or source verification.

Tiền điều kiện của người gọi / caller preconditions: bundle đã qua strict parse, literal preflight và schema (loader.parse_and_preflight +
loader.validate_structure). Dữ liệu lệch dạng trả MALFORMED_RECORD / UNSUPPORTED, trừ giới hạn phòng thủ khi build_index:
lồng quá MAX_DEPTH (64) ném ValueError ngoài miền đầu vào đã qua schema. Ghép claims với sai index cũng là ValueError của caller.
"""
import copy
import json
from dataclasses import dataclass

STATES = ('MATCH', 'MISMATCH', 'ONE_SIDED', 'INCOMPLETE', 'AMBIGUOUS', 'UNSUPPORTED', 'NOT_BOUND', 'NOT_APPLICABLE')
BASES = ('RECOMPUTED', 'PEER_CLAIM', 'LITERAL', 'DECLARED_SET')
RECORD_TYPES = ('task', 'grant', 'review', 'effect', 'result')
MAX_DEPTH = 64
OBSERVATION_FLAGS = (('bytes_observed', False), ('authenticity_observed', False), ('semantic_verified', False))

KIND_ENUM = frozenset(['user_intent', 'user_condition', 'user_acceptance', 'grant', 'policy', 'recipe_acceptance', 'review_receipt',
                       'reviewer_eligibility', 'role_acceptance', 'host_observation', 'effect_receipt'])
# từ vựng đóng của tên trường dùng trong locator; khóa lạ luôn thành "?" / closed vocabulary of field names allowed in locators
FIELD_VOCAB = frozenset([
    'intent', 'refs', 'authority', 'grant_refs', 'issuer_ref', 'effects', 'actions', 'action', 'delegation', 'parent_task', 'child_task',
    'callee', 'identity_ref', 'recipe', 'acceptance_ref', 'reviewer', 'eligibility_ref', 'receipt_ref', 'user_acceptance', 'ref', 'outcome',
    'binding', 'inputs', 'outputs', 'artifacts', 'actions_performed', 'grant_ref_ids', 'bind_version', 'evaluation_basis', 'task_id',
    'task_revision', 'intent_digest', 'accepted_task_digest', 'context_digest', 'policy_version', 'policy_digest', 'action_digest'])
_ABSENT = '#ABSENT'
# trường mang lời khai (khác nhau ⇒ CONFLICT) và metadata (chỉ đếm) / claim-bearing fields and metadata-only fields
CLAIM_FIELDS = ('kind', 'locator', 'revision', 'digest', 'issuer', 'source_class', 'channel', 'evidence_locator', 'observed_by')
METADATA_FIELDS = ('note', 'recorded_by')


def loc(position, *parts):
    """Locator đóng: 'records[i]' + chỉ số mảng + tên trường thuộc từ vựng đóng / closed locator."""
    out = '' if position is None else 'records[%d]' % position
    for part in parts:
        if isinstance(part, bool):
            out += '.?'
        elif isinstance(part, int):
            out += '[%d]' % part
        elif isinstance(part, str) and part in FIELD_VOCAB:
            out += '.' + part
        else:
            out += '.?'
    return out


def vkey(value):
    """Khóa so sánh theo kiểu JSON: 1, true, 1.0 và "1" khác nhau; chuỗi so nguyên văn."""
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def to_plain(value):
    if hasattr(value, '__dataclass_fields__'):
        out = dict((name, to_plain(getattr(value, name))) for name in value.__dataclass_fields__)
        if getattr(value, '_FLAGS', False):
            out.update(OBSERVATION_FLAGS)
        return out
    if isinstance(value, (tuple, list)):
        return [to_plain(x) for x in value]
    return value


class _Plain(object):
    _FLAGS = False

    def as_dict(self):
        return to_plain(self)


# ---------------------------------------------------------------- kiểu kết quả / result types
@dataclass(frozen=True)
class Relation(_Plain):
    _FLAGS = True
    name: str
    state: str
    basis: str
    locator: str = ''
    reason: object = None
    fields: tuple = ()
    indexes: tuple = ()
    counts: tuple = ()
    limitations: tuple = ()

    def as_dict(self):
        out = to_plain(self)
        out['counts'] = dict((k, v) for k, v in self.counts)
        return out


@dataclass(frozen=True)
class Lookup(_Plain):
    record_type: str
    status: str
    positions: tuple = ()


@dataclass(frozen=True)
class Occurrence(_Plain):
    position: int
    locator: str
    role: str
    group_no: int


@dataclass(frozen=True)
class ClaimGroup(_Plain):
    _FLAGS = True
    group_no: int
    status: str
    occurrences: int
    kind: object
    conflict_fields: tuple
    metadata_differs: tuple
    locators: tuple
    resolution: str = 'INLINE_CLAIM_ONLY'


@dataclass(frozen=True)
class GrantLink(_Plain):
    _FLAGS = True
    source_locator: str
    source_role: str
    state: str
    reasons: tuple = ()
    candidate_positions: tuple = ()
    claim_status: object = None
    claim_conflict_fields: tuple = ()
    kind_is_grant: object = None
    in_task_grant_refs: object = None
    link_is_authority: bool = False


# ---------------------------------------------------------------- index
def _depth_exceeds(value, limit):
    stack = [(value, 0)]
    while stack:
        node, depth = stack.pop()
        if isinstance(node, dict):
            children = node.values()
        elif isinstance(node, (list, tuple)):
            children = node
        else:
            continue
        if depth >= limit:
            return True
        stack.extend((c, depth + 1) for c in children)
    return False


def _tag(value):
    if isinstance(value, str):
        return ('s', value)
    if is_int(value):
        return ('i', value)
    return None


def _record_key(rec):
    """(record_type, khóa có kiểu) hoặc None nếu record thiếu/lệch khóa / typed key or None when malformed."""
    rtype = rec.get('record_type')
    if rtype == 'task':
        parts = (rec.get('task_id'), rec.get('task_revision'))
    elif rtype == 'grant':
        parts = (rec.get('grant_id'), rec.get('grant_revision'))
    elif rtype == 'review':
        parts = (rec.get('review_id'),)
    elif rtype == 'effect':
        parts = (rec.get('effect_id'),)
    elif rtype == 'result':
        parts = (rec.get('result_id'),)
    else:
        return None
    tagged = tuple(_tag(p) for p in parts)
    expected = ('s', 'i') if rtype in ('task', 'grant') else ('s',)
    if None in tagged or tuple(t[0] for t in tagged) != expected:
        return None
    return rtype, tagged


class RecordIndex(object):
    """Snapshot riêng của records (deep-copy container) + tra cứu có kiểu. Thứ tự nguồn là position; không sắp lại."""

    def __init__(self, records):
        if not isinstance(records, (list, tuple)):
            raise TypeError('records must be a list or tuple of dict')
        for rec in records:
            if not isinstance(rec, dict):
                raise TypeError('every record must be a dict')
        if _depth_exceeds(list(records), MAX_DEPTH):
            raise ValueError('record nesting exceeds the supported depth of %d levels' % MAX_DEPTH)
        self._records = tuple(copy.deepcopy(list(records)))
        self._claim_token = object()
        self._by_key = {}
        self._grants_by_id = {}
        malformed = []
        for position, rec in enumerate(self._records):
            rtype = rec.get('record_type')
            if not isinstance(rtype, str):
                malformed.append(position)
                continue
            if rtype not in RECORD_TYPES:
                continue
            key = _record_key(rec)
            if key is None:
                malformed.append(position)
                continue
            self._by_key.setdefault(key, []).append(position)
            if rtype == 'grant':
                self._grants_by_id.setdefault(key[1][0], []).append(position)
        self.malformed_positions = tuple(malformed)

    @property
    def count(self):
        return len(self._records)

    def _record(self, position):
        """Snapshot nội bộ của package; không bao giờ nằm trong kết quả công khai / package-internal snapshot."""
        return self._records[position]

    def lookup(self, record_type, *key):
        if record_type not in RECORD_TYPES:
            raise ValueError('unknown record_type')
        arity = (2,) if record_type == 'task' else ((1, 2) if record_type == 'grant' else (1,))
        if len(key) not in arity:
            raise ValueError('wrong number of key parts for %s' % record_type)
        tagged = tuple(_tag(k) for k in key)
        expected = ('s', 'i')[:len(key)]
        if None in tagged or tuple(t[0] for t in tagged) != expected:
            return Lookup(record_type, 'MISSING', ())
        if record_type == 'grant' and len(key) == 1:
            positions = tuple(self._grants_by_id.get(tagged[0], ()))
        else:
            positions = tuple(self._by_key.get((record_type, tagged), ()))
        status = 'MISSING' if not positions else ('FOUND' if len(positions) == 1 else 'AMBIGUOUS')
        return Lookup(record_type, status, positions)

    def collisions(self):
        out = [Lookup(key[0], 'AMBIGUOUS', tuple(pos)) for key, pos in self._by_key.items() if len(pos) > 1]
        return tuple(sorted(out, key=lambda l: (l.positions[0], l.record_type)))

    def positions_of(self, record_type):
        return tuple(self._by_key_positions(record_type))

    def _by_key_positions(self, record_type):
        found = []
        for key, pos in self._by_key.items():
            if key[0] == record_type:
                found.extend(pos)
        return sorted(found)

    def as_dict(self):
        return {'count': self.count, 'malformed_positions': list(self.malformed_positions),
                'collisions': [c.as_dict() for c in self.collisions()]}


def records_of(bundle):
    """`bundle['records']` khi record_type == "bundle", ngược lại [bundle]. Position = thứ tự nguồn (record đơn = 0)."""
    if not isinstance(bundle, dict):
        raise TypeError('bundle must be a dict')
    records = bundle.get('records')
    if bundle.get('record_type') == 'bundle' and isinstance(records, list):
        return records
    return [bundle]


def build_index(records):
    return RecordIndex(records)


# ---------------------------------------------------------------- inline claims
def _get(container, key):
    """(present, value) cho container dict; container sai kiểu ⇒ (False, None)."""
    if isinstance(container, dict) and key in container:
        return True, container[key]
    return False, None


def _action_sites(position, parts, action, out, bad):
    if not isinstance(action, dict):
        return
    present, recipe = _get(action, 'recipe')
    if present:
        if isinstance(recipe, dict):
            ok, ref = _get(recipe, 'acceptance_ref')
            if ok:
                out.append((loc(position, *(parts + ('recipe', 'acceptance_ref'))), 'recipe_acceptance', ref))
        else:
            bad.append(loc(position, *(parts + ('recipe',))))
    present, deleg = _get(action, 'delegation')
    if present:
        callee = deleg.get('callee') if isinstance(deleg, dict) else None
        if isinstance(callee, dict):
            ok, ref = _get(callee, 'identity_ref')
            if ok:
                out.append((loc(position, *(parts + ('delegation', 'callee', 'identity_ref'))), 'identity_ref', ref))
        elif isinstance(deleg, dict) and 'callee' in deleg:
            bad.append(loc(position, *(parts + ('delegation', 'callee'))))
        elif not isinstance(deleg, dict):
            bad.append(loc(position, *(parts + ('delegation',))))


def _sites(position, rec, bad):
    out = []
    rtype = rec.get('record_type')
    if rtype == 'task':
        for section, key, role in (('intent', 'refs', 'intent_ref'), ('authority', 'grant_refs', 'grant_ref')):
            present, sec = _get(rec, section)
            if not present:
                continue
            if not isinstance(sec, dict):
                bad.append(loc(position, section))
                continue
            ok, items = _get(sec, key)
            if not ok:
                continue
            if not isinstance(items, list):
                bad.append(loc(position, section, key))
                continue
            for i, ref in enumerate(items):
                out.append((loc(position, section, key, i), role, ref))
        ok, eff = _get(rec, 'effects')
        actions = eff.get('actions') if isinstance(eff, dict) else None
        if isinstance(actions, list):
            for j, action in enumerate(actions):
                _action_sites(position, ('effects', 'actions', j), action, out, bad)
    elif rtype == 'grant':
        ok, ref = _get(rec, 'issuer_ref')
        if ok:
            out.append((loc(position, 'issuer_ref'), 'issuer_ref', ref))
    elif rtype == 'review':
        ok, reviewer = _get(rec, 'reviewer')
        if ok:
            ok2, ref = _get(reviewer, 'eligibility_ref')
            if ok2:
                out.append((loc(position, 'reviewer', 'eligibility_ref'), 'eligibility_ref', ref))
        ok, ref = _get(rec, 'receipt_ref')
        if ok:
            out.append((loc(position, 'receipt_ref'), 'receipt_ref', ref))
    elif rtype == 'effect':
        ok, action = _get(rec, 'action')
        if ok:
            _action_sites(position, ('action',), action, out, bad)
        ok, ref = _get(rec, 'receipt_ref')
        if ok:
            out.append((loc(position, 'receipt_ref'), 'receipt_ref', ref))
    elif rtype == 'result':
        present, acceptance = _get(rec, 'user_acceptance')
        if present:
            if isinstance(acceptance, dict):
                ok, ref = _get(acceptance, 'ref')
                if ok:
                    out.append((loc(position, 'user_acceptance', 'ref'), 'user_acceptance_ref', ref))
            else:
                bad.append(loc(position, 'user_acceptance'))
        ok, performed = _get(rec, 'actions_performed')
        if ok and isinstance(performed, list):
            for k, action in enumerate(performed):
                _action_sites(position, ('actions_performed', k), action, out, bad)
    return out


def _claim_view(ref):
    attribution = ref.get('attribution') if isinstance(ref.get('attribution'), dict) else {}
    view = {}
    for name in ('kind', 'locator', 'revision', 'digest', 'issuer'):
        view[name] = vkey(ref[name]) if name in ref else _ABSENT
    for name in ('source_class', 'channel', 'evidence_locator', 'observed_by'):
        view[name] = vkey(attribution[name]) if name in attribution else _ABSENT
    meta = {}
    for name in METADATA_FIELDS:
        meta[name] = vkey(attribution[name]) if name in attribution else _ABSENT
    return view, meta


class ClaimTable(object):
    """Các nhóm lời khai inline theo ref_id (một namespace toàn bundle). AGREE không chứng minh nguồn hay quyền."""

    def __init__(self, groups, by_ref, occurrences, malformed, origin_token):
        self._groups = tuple(groups)
        self._by_ref = dict(by_ref)
        self._occurrences = dict(occurrences)
        self.malformed = tuple(malformed)
        self._origin_token = origin_token

    def group(self, ref_id):
        if not isinstance(ref_id, str):
            return None
        number = self._by_ref.get(ref_id)
        return None if number is None else self._groups[number]

    def groups(self):
        return self._groups

    def occurrences_at(self, position):
        return tuple(self._occurrences.get(position, ()))

    def as_dict(self):
        return {'groups': [g.as_dict() for g in self._groups], 'malformed': list(self.malformed)}


def collect_claims(index):
    if not isinstance(index, RecordIndex):
        raise TypeError('index must be a RecordIndex')
    bad = []
    grouped = {}
    order = []
    sites_by_position = {}
    for position in range(index.count):
        rec = index._record(position)
        for locator, role, ref in _sites(position, rec, bad):
            if not isinstance(ref, dict) or not isinstance(ref.get('ref_id'), str):
                bad.append(locator)
                continue
            ref_id = ref['ref_id']
            if ref_id not in grouped:
                grouped[ref_id] = []
                order.append(ref_id)
            grouped[ref_id].append((position, locator, role, ref))
            sites_by_position.setdefault(position, []).append((ref_id, locator, role))
    groups, by_ref = [], {}
    for number, ref_id in enumerate(order):
        occ = grouped[ref_id]
        views = [_claim_view(o[3]) for o in occ]
        conflicts = tuple(name for name in CLAIM_FIELDS if len(set(v[0][name] for v in views)) > 1)
        meta = tuple(sorted(name for name in METADATA_FIELDS if len(set(v[1][name] for v in views)) > 1))
        kind = None
        if not conflicts:
            raw = occ[0][3].get('kind')
            kind = raw if isinstance(raw, str) and raw in KIND_ENUM else None
        groups.append(ClaimGroup(number, 'CONFLICT' if conflicts else 'AGREE', len(occ), kind, conflicts, meta,
                                 tuple(o[1] for o in occ)))
        by_ref[ref_id] = number
    occurrences = {}
    for position, items in sites_by_position.items():
        occurrences[position] = [Occurrence(position, locator, role, by_ref[ref_id]) for ref_id, locator, role in items]
    return ClaimTable(groups, by_ref, occurrences, bad, index._claim_token)


# ---------------------------------------------------------------- grant links
_CONFLICT = ('CLAIM_CONFLICT', 'KIND_NOT_GRANT', 'NOT_IN_TASK_GRANT_REFS')
_AMBIGUOUS = ('MULTIPLE_CANDIDATES', 'TASK_AMBIGUOUS')


def _grant_candidates(index, ref_id):
    found = []
    for position in index.positions_of('grant'):
        ref = index._record(position).get('issuer_ref')
        if isinstance(ref, dict) and isinstance(ref.get('ref_id'), str) and ref['ref_id'] == ref_id:
            found.append(position)
    return tuple(found)


def _task_ref_ids(task):
    authority = task.get('authority')
    refs = authority.get('grant_refs') if isinstance(authority, dict) else None
    out = set()
    if isinstance(refs, list):
        for ref in refs:
            if isinstance(ref, dict) and isinstance(ref.get('ref_id'), str):
                out.add(ref['ref_id'])
    return out


def _primary(reasons):
    if any(r in _CONFLICT for r in reasons):
        return 'CONFLICT'
    if any(r in _AMBIGUOUS for r in reasons):
        return 'AMBIGUOUS'
    if 'NO_CANDIDATE' in reasons:
        return 'NO_GRANT_RECORD'
    if 'TASK_UNRESOLVED' in reasons:
        return 'INCOMPLETE'
    return 'LINKED'


def link_grants(index, claims, position):
    """Nối ref_id với record grant qua issuer_ref.ref_id (không bao giờ qua grant_id). Chỉ nối lời khai: link_is_authority=false."""
    if not isinstance(index, RecordIndex):
        raise TypeError('index must be a RecordIndex')
    if not isinstance(claims, ClaimTable):
        raise TypeError('claims must be a ClaimTable')
    if claims._origin_token is not index._claim_token:
        raise ValueError('claims must be collected from this RecordIndex snapshot')
    if not is_int(position):
        raise TypeError('position must be an int')
    if position < 0 or position >= index.count:
        raise ValueError('position out of range')
    rec = index._record(position)
    rtype = rec.get('record_type')
    items = []  # (locator, role, ref_id|None)
    task_look = None
    task_rec = None
    if rtype == 'task':
        authority = rec.get('authority')
        refs = authority.get('grant_refs') if isinstance(authority, dict) else None
        if refs is None:
            return ()
        if not isinstance(refs, list):
            return (GrantLink(loc(position, 'authority', 'grant_refs'), 'task_grant_ref', 'UNSUPPORTED', ('MALFORMED_RECORD',)),)
        for i, ref in enumerate(refs):
            rid = ref.get('ref_id') if isinstance(ref, dict) else None
            items.append((loc(position, 'authority', 'grant_refs', i), 'task_grant_ref', rid if isinstance(rid, str) else None))
    elif rtype == 'effect':
        ids = rec.get('grant_ref_ids')
        if ids is None:
            return ()
        if not isinstance(ids, list):
            return (GrantLink(loc(position, 'grant_ref_ids'), 'effect_grant_ref_id', 'UNSUPPORTED', ('MALFORMED_RECORD',)),)
        for i, rid in enumerate(ids):
            items.append((loc(position, 'grant_ref_ids', i), 'effect_grant_ref_id', rid if isinstance(rid, str) else None))
        binding = rec.get('binding')
        tid = binding.get('task_id') if isinstance(binding, dict) else None
        trev = binding.get('task_revision') if isinstance(binding, dict) else None
        task_look = index.lookup('task', tid, trev)
        if task_look.status == 'FOUND':
            task_rec = index._record(task_look.positions[0])
    else:
        return ()
    out = []
    for locator, role, rid in items:
        if rid is None:
            out.append(GrantLink(locator, role, 'UNSUPPORTED', ('MALFORMED_RECORD',)))
            continue
        group = claims.group(rid)
        candidates = _grant_candidates(index, rid)
        reasons = []
        claim_status = group.status if group is not None else None
        conflict_fields = group.conflict_fields if group is not None else ()
        kind_is_grant = None
        if group is not None:
            if group.status == 'CONFLICT':
                reasons.append('CLAIM_CONFLICT')
            else:
                kind_is_grant = group.kind == 'grant'
                if not kind_is_grant:
                    reasons.append('KIND_NOT_GRANT')
        if not candidates:
            reasons.append('NO_CANDIDATE')
        elif len(candidates) > 1:
            reasons.append('MULTIPLE_CANDIDATES')
        in_task = None
        if role == 'effect_grant_ref_id':
            if task_look.status == 'AMBIGUOUS':
                reasons.append('TASK_AMBIGUOUS')
            elif task_look.status == 'MISSING':
                reasons.append('TASK_UNRESOLVED')
            else:
                in_task = rid in _task_ref_ids(task_rec)
                if not in_task:
                    reasons.append('NOT_IN_TASK_GRANT_REFS')
        out.append(GrantLink(locator, role, _primary(reasons), tuple(reasons), candidates, claim_status, tuple(conflict_fields),
                             kind_is_grant, in_task))
    return tuple(out)
