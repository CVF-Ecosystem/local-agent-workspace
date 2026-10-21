"""Routing v3 thuần cho luồng một action (G-02-C2/S3-C/D, BINDING_ROUTING_ONLY): đường dẫn lexical, vùng ghi, điều kiện và hàng theo ROUTING_POLICY canonical.

Hàm thuần: không I/O, không đọc artifact/locator/mạng, không grant, không gate, không observer. Route chỉ là kết quả tính từ bảng policy
trong bộ nhớ và các trường thật của action; không PASS, không effect_authorized. `effect.routing` tự khai KHÔNG là nguồn route, chỉ được so để báo lệch.
Pure routing for one action. Three-valued logic T/F/U (Kleene): U is never treated as F; a row that is U makes the route UNCLASSIFIED
(TREAT_AS_UNCLASSIFIED). A path in an unsupported form is refused, never normalized.
Ngoài phạm vi (không đánh giá ở đây): ENVELOPE_EXCEEDED (thuộc gate ENVELOPE, ghi `not_evaluated_conditions`), recipe đang có (UNSUPPORTED),
review bắt buộc (REVIEW_REQUIRED_UNSUPPORTED), nhiều action (MULTI_ACTION_UNSUPPORTED).
"""
import fnmatch
import re

from .loader import InputError, parse_json_bytes

T, F, U = 'T', 'F', 'U'
ZONE_NONE = 'none'
ZONE_FRAMEWORK = 'framework'
ZONE_ORIGINAL = 'original_source'
ZONE_UNCLASSIFIED = 'UNCLASSIFIED'  # trạng thái, không phải hạng / a state, not a rank
ZONE_UNSUPPORTED = 'UNSUPPORTED'  # dạng path không hỗ trợ / path form not supported
DECLARED_UNKNOWN = 'unknown'
UNCLASSIFIED_ROW = 'R-UNCLASSIFIED'
LIGHT_ROW = 'R-READ_DRAFT'
KNOWN_LOSS_ROW = 'R-KNOWN_LOSS'
READ_OPS = ('read', 'delegate')
RECIPE_CONDITIONS = ('RECIPE_ACCEPTED_VERSION', 'RECIPE_ABSENT_OR_CHANGED', 'NO_USER_DECISION_CHANGE', 'USER_DECISION_CHANGE',
                     'USER_DECISION_EFFECT_UNKNOWN')
NOT_EVALUATED_HERE = ('ENVELOPE_EXCEEDED',)

_RESERVED = frozenset(['con', 'prn', 'aux', 'nul', 'conin$', 'conout$'] + ['com%d' % i for i in range(10)] + ['lpt%d' % i for i in range(10)])
_SHORT_NAME = re.compile(r'~\d')


# ---------------------------------------------------------------- đường dẫn / path
def lexical_segments(path):
    """Đoạn đã casefold của đường dẫn POSIX tương đối, hoặc None nếu dạng không hỗ trợ (từ chối, không chuẩn hóa hộ).

    Từ chối: rỗng, tuyệt đối, `\\`, `:` (ổ/ADS), ký tự điều khiển, đoạn rỗng (`//`, dấu `/` cuối), `.`/`..`,
    đoạn có khoảng trắng đầu/cuối hoặc kết thúc bằng `.`, tên ngắn 8.3 (`~<số>`), tên thiết bị Windows.
    Lexical only: không realpath, không lstat, không đọc đĩa.
    """
    if not isinstance(path, str) or not path or path.startswith('/') or '\\' in path or ':' in path:
        return None
    if any(ord(ch) < 32 or ord(ch) == 127 or ch in '<>"|?*' for ch in path):
        return None
    out = []
    for seg in path.split('/'):
        if seg in ('', '.', '..') or seg != seg.strip() or seg.endswith('.') or _SHORT_NAME.search(seg):
            return None
        if seg.split('.')[0].casefold() in _RESERVED:
            return None
        out.append(seg.casefold())
    return tuple(out)


# ---------------------------------------------------------------- policy
class RoutePolicy(object):
    """Trường routing của ROUTING_POLICY canonical, parse từ bytes riêng; không dùng dict dùng chung từ cache."""

    def __init__(self, obj):
        self.rows = dict((r['row_id'], r) for r in obj['rows'])
        self.row_order = tuple(r['row_id'] for r in obj['rows'])
        self.light = frozenset(obj['light_write_zones'])
        self.rank = dict((z, i) for i, z in enumerate(obj['write_zone_rank']))
        zone_map = []
        for item in obj['zone_map']:
            zone_map.append((tuple(p.casefold() for p in item['path_prefix'].rstrip('/').split('/')), item['write_zone']))
        self.zone_map = sorted(zone_map, key=lambda pair: -len(pair[0]))
        self.patterns = tuple(p.casefold() for p in obj['authority_name_patterns'])
        self.assumptions = tuple(obj['open_assumptions'])
        if obj.get('unmapped_path_handling') != 'UNCLASSIFIED' or obj.get('conditional_route_disposition') != 'BLOCKED':
            raise ValueError('routing policy disposition literals differ from the candidate')


def load_route_policy(policy_bytes):
    if not isinstance(policy_bytes, bytes):
        raise TypeError('policy_bytes must be bytes')
    try:
        obj = parse_json_bytes(policy_bytes)
    except InputError:
        raise ValueError('routing policy is not strict JSON')
    return RoutePolicy(obj)


# ---------------------------------------------------------------- vùng / zones
def path_zone(segs, declared, policy, protected):
    """Vùng hiệu lực: hạng cao nhất trong các nguồn ĐÃ phân loại; không nguồn nào ⇒ UNCLASSIFIED (kể cả khi khai vùng nhẹ).

    Nguồn: zone_map theo tiền tố dài nhất (ranh giới đoạn); tên khớp authority_name_patterns ⇒ framework; liên quan protected_targets
    ⇒ tối thiểu original_source. Vùng khai của action chỉ nâng, không hạ, không tự phân loại đường dẫn.
    """
    if declared == DECLARED_UNKNOWN:
        return ZONE_UNCLASSIFIED
    sources = []
    for prefix, zone in policy.zone_map:
        if len(segs) > len(prefix) and segs[:len(prefix)] == prefix:
            sources.append(zone)
            break
    if any(fnmatch.fnmatchcase(segs[-1], pat) for pat in policy.patterns):
        sources.append(ZONE_FRAMEWORK)
    if any(segs[:len(p)] == p or p[:len(segs)] == segs for p in protected):
        sources.append(ZONE_ORIGINAL)
    if not sources:
        return ZONE_UNCLASSIFIED
    if declared in policy.rank and declared != ZONE_NONE:
        sources.append(declared)
    return max(sources, key=policy.rank.__getitem__)


# ---------------------------------------------------------------- Kleene / điều kiện
def _and(values):
    if F in values:
        return F
    return U if U in values else T


def _or(values):
    if T in values:
        return T
    return U if U in values else F


def _clause(clause, op, zones, content, cond):
    """(giá trị T/F/U, có khớp mệnh đề create_new không). Trường vắng trong mệnh đề không đóng góp."""
    vals = []
    if 'operations' in clause:
        vals.append(T if op in clause['operations'] else F)
    if 'write_zones' in clause:
        vals.append(T if zones and all(z in clause['write_zones'] for z in zones) else F)
    if 'content_use' in clause:
        vals.append(T if isinstance(content, list) and any(c in clause['content_use'] for c in content) else F)
    if 'conditions_all' in clause:
        vals.append(_and([cond.get(c, U) for c in clause['conditions_all']]))
    if 'conditions_any' in clause:
        vals.append(_or([cond.get(c, U) for c in clause['conditions_any']]))
    value = _and(vals)
    return value, value == T and 'create_new' in clause.get('operations', ())


def _row(row, op, zones, content, cond):
    results = [_clause(c, op, zones, content, cond) for c in row['match_any']]
    return _or([v for v, _ in results]), any(c for _, c in results)


# ---------------------------------------------------------------- kết quả / result
class RouteResult(object):
    """Kết quả route một task. `evaluated=False` khi không có task đúng một action; không bịa action."""

    def __init__(self):
        self.evaluated = False
        self.rows = []
        self.status = None
        self.assumptions = []
        self.matched = ()
        self.review_phases = ()
        self.deny = []
        self.unsupported = []
        self.blocked = []

    def as_dict(self):
        return {'evaluated': self.evaluated, 'rows': list(self.rows), 'status': self.status, 'assumptions': list(self.assumptions)}


def evaluate_task(task, policy, phase, external=None):
    """Route một task. `external` (chỉ do workflow có root truyền vào): `envelope_exceeded` ∈ T/F/U từ gate ENVELOPE và `closed_assumptions`
    (id giả định đã được observer đóng trong lần kiểm này). Không có ⇒ như cũ: ENVELOPE_EXCEEDED là U, mọi giả định còn OPEN."""
    if external is None:
        external = {}
    elif not isinstance(external, dict):
        raise TypeError('external must be a dict or None')
    envelope = external.get('envelope_exceeded')
    if envelope not in (None, T, F, U):
        raise ValueError('envelope_exceeded must be T, F or U')
    closed = frozenset(external.get('closed_assumptions') or ())
    res = RouteResult()
    effects = task.get('effects') if isinstance(task, dict) else None
    preservation = effects.get('preservation') if isinstance(effects, dict) else None
    states = [p.get('known_loss_state') for p in preservation if isinstance(p, dict)] if isinstance(preservation, list) else []
    if 'KNOWN_LOSS' in states:
        res.deny.append('KNOWN_PRESERVATION_LOSS')  # task-wide veto still applies when action routing is unsupported
    actions = effects.get('actions') if isinstance(effects, dict) else None
    if not isinstance(actions, list) or not actions:
        return res
    if len(actions) != 1:
        res.unsupported.append('MULTI_ACTION_UNSUPPORTED')
        return res
    res.evaluated = True
    action = actions[0]
    op = action.get('operation')
    declared = action.get('write_zone')
    content = action.get('content_use')
    targets = action.get('targets') or []
    grants = (task.get('authority') or {}).get('grant_refs') or []
    prs = [p for p in (effects.get('preservation') or []) if isinstance(p, dict)]
    protected_raw = effects.get('protected_targets') or []
    protected = [lexical_segments(p) for p in protected_raw]
    protected_bad = any(p is None for p in protected)
    protected = [p for p in protected if p is not None]

    unsupported = set()
    unclassified = False
    writes = op not in READ_OPS
    if writes:
        if declared == ZONE_NONE or not targets:
            unclassified = True
        zones = []
        for target in targets:
            segs = lexical_segments(target)
            if segs is None or protected_bad:
                zones.append(ZONE_UNSUPPORTED)
                unsupported.add('PATH_UNSUPPORTED_FORM')
            else:
                zones.append(path_zone(segs, declared, policy, protected))
    else:
        if declared != ZONE_NONE:
            unclassified = True
        zones = [ZONE_NONE]
    if any(z in (ZONE_UNCLASSIFIED, ZONE_UNSUPPORTED) for z in zones):
        unclassified = True

    cond = {}
    if not writes:
        cond['NO_PROTECTED_TARGET'] = T  # tập ghi rỗng
    elif not zones or ZONE_UNCLASSIFIED in zones or ZONE_UNSUPPORTED in zones:
        cond['NO_PROTECTED_TARGET'] = U
    else:
        cond['NO_PROTECTED_TARGET'] = T if all(z in policy.light for z in zones) else F
    if not isinstance(content, list) or not content:
        cond['CONTENT_USE_INTERNAL_ONLY'] = U
    else:
        cond['CONTENT_USE_INTERNAL_ONLY'] = T if all(c == 'internal_draft' for c in content) else F
    if 'recipe' in action:
        for name in RECIPE_CONDITIONS:
            cond[name] = U
        unsupported.add('RECIPE_NOT_IN_CANDIDATE')
    else:
        cond.update({'RECIPE_ABSENT_OR_CHANGED': T, 'RECIPE_ACCEPTED_VERSION': F, 'NO_USER_DECISION_CHANGE': F,
                     'USER_DECISION_CHANGE': F, 'USER_DECISION_EFFECT_UNKNOWN': F})
    for name in NOT_EVALUATED_HERE:
        # not evaluated is unknown, never evidence that the trigger is false; only the ENVELOPE gate may supply a T/F/U
        cond[name] = envelope if envelope is not None and name == 'ENVELOPE_EXCEEDED' else U
    not_evaluated = [] if envelope in (T, F) else list(NOT_EVALUATED_HERE)
    states = [p.get('known_loss_state') for p in prs]
    cond['KNOWN_PRESERVATION_LOSS'] = T if 'KNOWN_LOSS' in states else (U if 'UNKNOWN' in states else F)
    cond['MISSING_AUTHORITY'] = F if grants else T
    cond['UNCLASSIFIED'] = T if unclassified else F

    values = {}
    creates = {}
    for rid in policy.row_order:
        if rid != UNCLASSIFIED_ROW:
            values[rid], creates[rid] = _row(policy.rows[rid], op, zones, content, cond)
    possible_review_phases = set()
    for rid, value in values.items():
        if value in (T, U):
            possible_review_phases.update(policy.rows[rid].get('required_review_phases', []))
    # No review evaluator exists: do not claim a required review is present or missing.
    cond['MISSING_REQUIRED_REVIEW'] = U if possible_review_phases else F
    if U in values.values():
        cond['UNCLASSIFIED'] = T  # TREAT_AS_UNCLASSIFIED: hàng không xác định làm route không phân loại được
    values[UNCLASSIFIED_ROW], creates[UNCLASSIFIED_ROW] = _row(policy.rows[UNCLASSIFIED_ROW], op, zones, content, cond)
    matched = [rid for rid in policy.row_order if values[rid] in (T, U)]
    if not matched:
        matched = [UNCLASSIFIED_ROW]  # unmatched_effect_route: không hàng nào khớp thì không được coi là nhẹ
        values[UNCLASSIFIED_ROW] = T

    assumptions = []
    for assumption in policy.assumptions:
        if op in assumption['applies_to_operations'] and any(creates.get(rid) for rid in matched):
            entry = {'id': assumption['id'], 'action_index': 0}
            if phase in assumption.get('not_applicable_in_phases', []):
                entry['status'] = 'NOT_APPLICABLE_IN_PHASE'
            elif assumption['id'] in closed and phase in assumption.get('closes_in_phases', []):
                entry['status'] = 'CLOSED_BY_OBSERVATION'
                entry['limits'] = list(assumption.get('limits', []))
            else:
                entry['status'] = 'OPEN'
            assumptions.append(entry)
    open_ids = [a for a in assumptions if a['status'] == 'OPEN']

    phases = set()
    for rid in matched:
        phases.update(policy.rows[rid].get('required_review_phases', []))
    zone_values = sorted(set(zones))
    res.rows = [{'row_id': rid, 'match_state': values.get(rid, U), 'required_gates': list(policy.rows[rid].get('required_gates', [])),
                 'required_review_phases': list(policy.rows[rid].get('required_review_phases', [])),
                 'write_zones': zone_values, 'not_evaluated_conditions': list(not_evaluated)} for rid in matched]
    if UNCLASSIFIED_ROW in matched:
        res.status = 'UNRESOLVED'
    elif open_ids:
        res.status = 'CONDITIONAL'
    else:
        res.status = 'RESOLVED'
    res.assumptions = assumptions
    res.matched = tuple(matched)
    res.review_phases = tuple(sorted(phases))

    if values.get(KNOWN_LOSS_ROW) == T and 'KNOWN_PRESERVATION_LOSS' not in res.deny:
        res.deny.append('KNOWN_PRESERVATION_LOSS')
    if phases:
        res.blocked.append('REVIEW_REQUIRED_UNSUPPORTED')
    if UNCLASSIFIED_ROW in matched:
        res.blocked.append('UNCLASSIFIED_OPERATION')
    if cond['KNOWN_PRESERVATION_LOSS'] == U:
        res.blocked.append('PRESERVATION_UNKNOWN')
    if open_ids:
        res.blocked.append('ROUTE_ASSUMPTION_OPEN')
    res.unsupported.extend(sorted(unsupported))
    return res


def declared_mismatch(res, declared):
    """`effect.routing` tự khai (nếu có) phải trùng hàng và pha review đã tính; khác ⇒ True. Khai báo không bao giờ là nguồn route."""
    if not res.evaluated or not isinstance(declared, dict):
        return False
    return (set(declared.get('matched_rows') or []) != set(res.matched)
            or set(declared.get('required_review_phases') or []) != set(res.review_phases))
