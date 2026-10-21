"""Workflow P-CN1 một file: gate + observer + receipt + D4 (stage P_CN1_ONE_FILE) / one-file P-CN1 gates, observer, receipt and D4.

Chỉ chạy khi có root tường minh (entry nạp module này lazily). Một task, một action `create_new` (tool `publish_new`), một target, một grant_ref.
Ngoài shape đó ⇒ không đánh giá gate, báo `P_CN1_SHAPE_UNSUPPORTED`. Không general engine/registry/plugin: mọi quy tắc nằm ở đây theo contract v3
mục 4–8, 11 và README. Mọi kết luận là nhất quán record hợp tác (ADVISORY); `effect_authorized` luôn false, không semantic_verified, không semantic của
`task_classes`. Observer chỉ đọc (observer.py). T/F/U: thiếu hoặc lỗi quan sát giữ NOT_CHECKED/UNSUPPORTED, không bao giờ là "vắng".
"""
import re

from . import binding, canon, observer, routing
from .loader import InputError, parse_json_bytes
from .refs import is_int

PHASES = ('dispatch', 'effect', 'accept')
GATE_ORDER = ('GRANT_SCOPE', 'PATH_SCOPE', 'TOOL_SCOPE', 'ENVELOPE', 'BINDING', 'INPUT_REVISION', 'ACTUAL_OUTCOME', 'REQUIREMENTS')
DUE = {'GRANT_SCOPE': PHASES, 'PATH_SCOPE': PHASES, 'TOOL_SCOPE': PHASES, 'ENVELOPE': PHASES, 'BINDING': ('effect', 'accept'),
       'INPUT_REVISION': ('effect', 'accept'), 'ACTUAL_OUTCOME': ('accept',), 'REQUIREMENTS': ('accept',)}
OK_STATES = ('MET', 'NOT_REQUIRED', 'USER_ACCEPTED_DECLARED', 'NOT_YET_DUE')
TOOL = 'publish_new'
PROTOCOL_ID, PROTOCOL_VERSION = 'P-CN1', 1
LIGHT_ZONES = ('working', 'output_new')
RUNTIME_SEGS = ('.agent', 'runtime', 'publish')
TASK_ID_RE = re.compile(r'^pcn1-([0-9a-f]{32})$')
REQUIRED_OPS = ('create_new', 'delete')
USER_CHANNELS = ('USER_MESSAGE', 'HOST_CONFIRMATION_UI')
UNSUPPORTED_OBSERVATION = ('UNSUPPORTED_FS', 'PATH_UNSUPPORTED_FORM')
# Trạng thái liên kết grant → (trạng thái gate, lý do) / grant-link state to (gate status, reason). LINKED is only a claim link, never authority.
_LINK = {'NO_GRANT_RECORD': ('NOT_MET', 'GRANT_MISSING'), 'CONFLICT': ('NOT_CHECKED', 'REF_CONFLICT'), 'AMBIGUOUS': ('NOT_CHECKED', 'REF_AMBIGUOUS'),
         'INCOMPLETE': ('NOT_CHECKED', 'REF_INCOMPLETE'), 'UNSUPPORTED': ('UNSUPPORTED', 'REF_UNSUPPORTED')}
_MALFORMED = (KeyError, TypeError, AttributeError, IndexError, ValueError)


def _fold(statuses):
    """Gộp trạng thái con: NOT_MET > UNSUPPORTED > NOT_CHECKED > MET (NOT_REQUIRED / NOT_YET_DUE bị bỏ)."""
    live = [s for s in statuses if s not in ('NOT_REQUIRED', 'NOT_YET_DUE')]
    for worst in ('NOT_MET', 'UNSUPPORTED', 'NOT_CHECKED'):
        if worst in live:
            return worst
    return 'MET' if live else 'NOT_REQUIRED'


def _segments(path):
    """Đoạn lexical của đường dẫn grant (cho phép `/` cuối); None nếu dạng không hỗ trợ ⇒ không phủ gì."""
    if not isinstance(path, str):
        return None
    return routing.lexical_segments(path[:-1] if path.endswith('/') else path)


def _same_actor(a, b):
    return isinstance(a, dict) and isinstance(b, dict) and a.get('actor_id') == b.get('actor_id') and a.get('role') == b.get('role')


def _source_class(ref):
    att = ref.get('attribution') if isinstance(ref, dict) else None
    return att.get('source_class') if isinstance(att, dict) else None


def _digest_hex(text):
    return text.split(':', 1)[-1] if isinstance(text, str) else None


class Workflow(object):
    def __init__(self, records, index, claims, phase, root, owners, refs):
        if phase not in PHASES:
            raise ValueError('unknown phase')
        self.records, self.index, self.claims, self.phase, self.root, self.owners, self.refs = records, index, claims, phase, root, owners, refs
        self.blocked, self.unsupported, self.deny, self.details = set(), set(), set(), []
        self.supported = False
        self.gates, self.gates_evaluated = [], False
        self.aggregate = None
        self.bytes_observed = self.target_observed = self.observer_ran = False
        self.target_absent = False
        self.task = self.grant = self.link = self.protocol = self.obs = self.evidence = None
        self.rid = self.target = None
        self.env_value, self.env_status, self.env_reasons, self.env_limits = 'U', 'NOT_CHECKED', set(), []
        self.hist = ('NOT_CHECKED', set(), [])
        self.snap = ('NOT_CHECKED', set())
        pos = {'task': [], 'grant': [], 'REQUEST': [], 'OUTCOME': [], 'result': []}
        for i, rec in enumerate(records):
            rtype = rec.get('record_type')
            if rtype == 'effect':
                pos.setdefault(rec.get('stage'), []).append(i)
            elif rtype in pos:
                pos[rtype].append(i)
        self.pos = pos

    # ---------------------------------------------------------------- shape / chuẩn bị
    def _shape(self):
        """Danh sách mã đóng của các lý do shape không hỗ trợ (rỗng = hỗ trợ). Không echo giá trị."""
        if len(self.pos['task']) != 1:
            return ['TASK_COUNT']
        problems = []
        task = self.task = self.records[self.pos['task'][0]]
        try:
            actions = task['effects']['actions']
            if len(actions) != 1:
                return ['ACTION_COUNT']
            action = actions[0]
            if action.get('operation') != 'create_new' or action.get('tool') != TOOL:
                problems.append('OPERATION_OR_TOOL')
            for key in ('recipe', 'delegation', 'payload'):
                if key in action:
                    problems.append(key.upper() + '_PRESENT')
            targets = action.get('targets')
            segs = None
            if not isinstance(targets, list) or len(targets) != 1:
                problems.append('TARGET_COUNT')
            else:
                self.target = targets[0]
                segs = routing.lexical_segments(self.target)
                if segs is None:
                    problems.append('TARGET_FORM')
            if action.get('write_zone') not in LIGHT_ZONES:
                problems.append('ZONE')
            match = TASK_ID_RE.fullmatch(task.get('task_id') if isinstance(task.get('task_id'), str) else '')
            if match is None:
                problems.append('TASK_ID')
            else:
                self.rid = match.group(1)
            if len(task['authority']['grant_refs']) != 1:
                problems.append('GRANT_REF_COUNT')
            if segs is not None and any(routing.lexical_segments(i.get('path')) == segs for i in task['inputs']):
                problems.append('INPUT_IS_TARGET')
            self.protocol = self._protocol(action)
            if self.protocol is None:
                problems.append('PROTOCOL_NOT_ACCEPTED')
        except _MALFORMED:
            problems.append('MALFORMED')
        return problems

    def _protocol(self, action):
        """Mục owner_protocols khớp P-CN1/v1 cho đúng tool, thao tác, vùng, nền tảng; None nếu không có. Tên tool tự khai không đủ."""
        try:
            policy = parse_json_bytes(self.owners.policy_bytes)
        except InputError:
            return None
        for item in policy.get('owner_protocols', []):
            if (item.get('protocol_id') == PROTOCOL_ID and item.get('protocol_version') == PROTOCOL_VERSION and item.get('owner_tool') == TOOL
                    and item.get('operation') == action.get('operation') and action.get('write_zone') in item.get('target_zones', [])
                    and item.get('platform') == 'windows-ntfs-local' and item.get('review_phases_supported') == []):
                return item
        return None

    def prepare(self):
        """Shape, grant, envelope và quan sát. Trả `external` cho routing, hoặc None nếu shape không hỗ trợ."""
        problems = self._shape()
        if problems:
            self.unsupported.add('P_CN1_SHAPE_UNSUPPORTED')
            self.details.append('p_cn1 shape unsupported (%s)' % ', '.join(sorted(set(problems))))
            return None
        self.supported = True
        links = self.refs.link_grants(self.index, self.claims, self.pos['task'][0])
        self.link = links[0] if len(links) == 1 else None
        if self.link is not None and self.link.state == 'LINKED' and len(self.link.candidate_positions) == 1:
            self.grant = self.records[self.link.candidate_positions[0]]
        self._envelope()
        self._observe()
        external = {'envelope_exceeded': self.env_value}
        if self.target_absent:
            external['closed_assumptions'] = ('A-NEW_TARGET',)
        return external

    def _envelope(self):
        """Số học DECLARED giữa task.envelope và grant.limits ⇒ T/F/U cho `ENVELOPE_EXCEEDED` và trạng thái gate ENVELOPE."""
        env = self.task.get('envelope') if isinstance(self.task.get('envelope'), dict) else {}
        subject = self.task['authority']['subject']
        reasons, limits = set(), ['ENVELOPE_DECLARED_NOT_HOST_OBSERVED']
        role_bad = env.get('role') != subject.get('role')
        if role_bad:
            reasons.add('ENVELOPE_ROLE_MISMATCH')
        exceeded = unknown = unsupported = False
        if 'profile_ref' in env:
            unknown = unsupported = True
            reasons.add('PROFILE_UNSUPPORTED')
            limits.append('PROFILE_NOT_EVALUATED')
        if self.grant is None:
            unknown = True
            reasons.add('ENVELOPE_UNMEASURED')
        else:
            lim = self.grant.get('limits') if isinstance(self.grant.get('limits'), dict) else {}
            if 'expires_at' in lim or 'expires_at' in env:
                unknown = unsupported = True
                reasons.add('EXPIRES_AT_UNSUPPORTED')
            for key in ('max_retries', 'max_concurrency'):
                if key in lim:
                    field = env.get(key)
                    if not isinstance(field, dict) or field.get('status') not in ('REQUESTED', 'APPLIED') or not is_int(field.get('value')):
                        unknown = True
                        reasons.add('ENVELOPE_UNMEASURED')
                    elif field['value'] > lim[key]:
                        exceeded = True
                        reasons.add('ENVELOPE_EXCEEDED')
            if 'cost_limit' in lim:
                field = env.get('cost_limit')
                if isinstance(field, dict) and field.get('status') in ('REQUESTED', 'APPLIED') and field.get('value') == lim['cost_limit']:
                    limits.append('COST_LIMIT_EQUAL_STRINGS_ONLY')
                else:
                    unknown = True
                    reasons.add('ENVELOPE_UNMEASURED')
                    limits.append('COST_LIMIT_UNITS_NOT_COMPARABLE')
        self.env_value = 'T' if exceeded else ('U' if unknown else 'F')
        if exceeded or role_bad:
            status = 'NOT_MET'
        elif unsupported:
            status = 'UNSUPPORTED'
        elif unknown:
            status = 'NOT_CHECKED'
        else:
            status = 'MET'
        self.env_status, self.env_reasons, self.env_limits = status, reasons, limits

    def _observe(self):
        inputs = [i['path'] for i in self.task['inputs']] if self.phase in ('effect', 'accept') else []
        self.obs = observer.observe(self.root, self.target, inputs, self.rid)
        self.observer_ran = True
        target = self.obs['target']
        self.target_observed = bool(self.obs['available'] and isinstance(target, dict))
        shas = [i.get('sha256') for i in self.obs['inputs'] if isinstance(i, dict)]
        self.bytes_observed = bool((isinstance(target, dict) and target.get('sha256')) or any(shas))
        if self.phase == 'accept':
            self.evidence = observer.load_evidence(self.root, self.rid)
        else:
            files = (self.obs['evidence'] or {}).get('files') if isinstance(self.obs['evidence'], dict) else None
            self.target_absent = bool(self.obs['available'] and self.obs['parents_link_free'] is True and isinstance(target, dict)
                                      and target.get('exists') is False and not files)

    # ---------------------------------------------------------------- tiện ích gate
    def _mk(self, name, status, required, provided, limits, reasons, owner, **extra):
        due = self.phase in DUE[name]
        gate = {'gate': name, 'due_in': list(DUE[name]), 'status': status if due else 'NOT_YET_DUE',
                'evidence': {'required': list(required), 'provided': list(provided) if due else []},
                'limits': list(limits), 'reasons': sorted(set(reasons)) if due else [], 'owner_of_proof': owner}
        gate.update(extra if due else {})
        return gate

    def _phase_actors(self):
        out = [('task.proposed_by', self.task.get('proposed_by'))]
        if self.phase in ('effect', 'accept'):
            for stage in ('REQUEST', 'OUTCOME'):
                for p in self.pos[stage]:
                    out.append(('effect.actor', self.records[p].get('actor')))
        if self.phase == 'accept':
            for p in self.pos['result']:
                out.append(('result.produced_by', self.records[p].get('produced_by')))
        return out

    def _cover(self, paths, segs):
        return any(p is not None and segs[:len(p)] == p for p in paths)

    # ---------------------------------------------------------------- gate
    def _g_grant(self):
        link, grant = self.link, self.grant
        if grant is None:
            status, reason = _LINK.get(link.state if link else 'INCOMPLETE', ('NOT_CHECKED', 'REF_INCOMPLETE'))
            return self._mk('GRANT_SCOPE', status, 'DC', '', ['TASK_CLASSES_NOT_CHECKED'], {reason}, 'user (grant) / host')
        reasons = set()
        if grant.get('status') != 'ACTIVE' or grant.get('example_only'):
            reasons.add('GRANT_INACTIVE')
        ref = self.task['authority']['grant_refs'][0]
        if _source_class(ref) != 'USER_CONFIRMATION' or _source_class(grant.get('issuer_ref')) != 'USER_CONFIRMATION':
            reasons.add('USER_CONFIRMATION_MISSING')
        subject = self.task['authority']['subject']
        who = grant.get('subject') if isinstance(grant.get('subject'), dict) else {}
        if subject.get('role') not in who.get('roles', []) or ('actor_ids' in who and subject.get('actor_id') not in who['actor_ids']):
            reasons.add('GRANT_OUT_OF_SCOPE')
        for label, actor in self._phase_actors():
            if not _same_actor(actor, subject):
                reasons.add('GRANT_OUT_OF_SCOPE')
                self.details.append('actor of %s is not the task subject' % label)
        scope = grant.get('scope') if isinstance(grant.get('scope'), dict) else {}
        if not set(REQUIRED_OPS) <= set(scope.get('operations', [])):
            reasons.add('GRANT_OUT_OF_SCOPE')
        return self._mk('GRANT_SCOPE', 'NOT_MET' if reasons else 'MET', 'DC', 'DC', ['ATTRIBUTION_NOT_PROVEN', 'TASK_CLASSES_NOT_CHECKED',
                                                                                      'DELETE_ONLY_T7_NOT_ENFORCED'], reasons, 'user (grant) / host')

    def _lexical(self, route):
        if self.grant is None:
            return 'NOT_CHECKED', {'GRANT_MISSING'}
        scope = self.grant.get('scope') if isinstance(self.grant.get('scope'), dict) else {}
        paths = [_segments(p) for p in scope.get('paths', [])]
        segs = routing.lexical_segments(self.target)
        needed = [segs] + [segs[:i] for i in range(1, len(segs))] + [RUNTIME_SEGS]
        reasons = set()
        if not all(self._cover(paths, s) for s in needed):
            reasons.add('GRANT_OUT_OF_SCOPE')
        zones = set()
        for row in route.rows:
            zones.update(row['write_zones'])
        if not route.evaluated or not zones or not zones <= set(LIGHT_ZONES):
            reasons.add('PATH_ZONE_UNDETERMINED')
        return ('NOT_MET' if reasons else 'MET'), reasons

    def _observed_at_time(self):
        if self.phase == 'accept':
            return 'NOT_REQUIRED', set()
        obs = self.obs
        if not obs['available'] or obs['parents_link_free'] is not True or not isinstance(obs['target'], dict):
            status = 'UNSUPPORTED' if obs['reason'] in UNSUPPORTED_OBSERVATION else 'NOT_CHECKED'
            return status, {'OBSERVATION_UNAVAILABLE'}
        if obs.get('runtime_parents_ready') is False:
            return 'NOT_MET', {'RUNTIME_PARENT_MISSING'}  # the owner never creates `.agent` / `.agent/runtime`; a root without them cannot publish
        if obs.get('runtime_parents_ready') is not True:
            return 'NOT_CHECKED', {'OBSERVATION_UNAVAILABLE'}
        if obs['target'].get('exists') is not False:
            return 'NOT_MET', {'TARGET_EXISTS_OBSERVED'}
        files = (obs['evidence'] or {}).get('files') if isinstance(obs['evidence'], dict) else None
        if files:
            return 'NOT_MET', {'RID_EVIDENCE_PRESENT'}
        return 'MET', set()

    def _snapshot(self):
        """Task có biểu diễn được đúng bởi owner không: `build_task(request_from_task(task), rid)` cho cùng projection C1 (intent/context/accepted_task/action).

        Chạy ở mọi pha. Task có context/envelope/effects mà owner bỏ hoặc không hỗ trợ không roundtrip, nên không thể publish rồi accept cùng snapshot.
        Dùng comparator C1 sẵn có (`binding.recompute_task`), không digest hay projection mới; không gọi hàm ghi của owner.
        """
        state, rebuilt = observer.rebuild_task(self.task, self.rid)
        if state == 'UNAVAILABLE':
            return 'NOT_CHECKED', {'OBSERVATION_UNAVAILABLE'}
        unsupported = ('UNSUPPORTED', {'TASK_NOT_OWNER_REPRESENTABLE'})
        if state != 'OK':
            return unsupported
        theirs, mine = binding.recompute_task(self.task), binding.recompute_task(rebuilt)
        pairs = [(theirs.intent, mine.intent), (theirs.accepted_task, mine.accepted_task), (theirs.context, mine.context)]
        pairs += list(zip(theirs.actions, mine.actions))
        if len(theirs.actions) != 1 or len(mine.actions) != 1 or any(a.state != 'COMPUTED' or b.state != 'COMPUTED' for a, b in pairs):
            return unsupported
        return ('MET', set()) if all(a.digest == b.digest for a, b in pairs) else unsupported

    def _history(self):
        """Lịch sử precondition (accept): đúng một prepared + published hợp lệ cùng rid và khớp snapshot task hiện hành."""
        if self.phase != 'accept':
            return 'NOT_YET_DUE', set()
        ev = self.evidence
        missing = ('NOT_CHECKED', {'PRECONDITION_PROOF_MISSING'})
        if not ev or not ev['available'] or not ev['consistent'] or ev['terminal'] != 'published':
            return missing
        prepared, published = ev['prepared'], ev['published']
        if prepared is None or published is None or not {'prepared.json', 'published.json'} <= set(ev['files']):
            return missing
        if not set(ev['files']) <= {'prepared.json', 'published.json', 'staged'}:
            return 'NOT_MET', {'PRECONDITION_PROOF_MISSING'}
        theirs, mine = binding.recompute_task(prepared['task']), binding.recompute_task(self.task)
        pairs = [(theirs.intent, mine.intent), (theirs.accepted_task, mine.accepted_task), (theirs.context, mine.context)]
        pairs += list(zip(theirs.actions, mine.actions))
        same = (len(theirs.actions) == len(mine.actions) == 1
                and all(a.state == 'COMPUTED' and b.state == 'COMPUTED' and a.digest == b.digest for a, b in pairs))
        if not same or published.get('target') != self.target or published.get('content') != prepared.get('content'):
            return 'NOT_MET', {'PRECONDITION_PROOF_MISSING'}
        return 'MET', set()

    def _g_path(self, route):
        lex_s, lex_r = self._lexical(route)
        obs_s, obs_r = self._observed_at_time()
        hist_s, hist_r = self.hist
        status = _fold([lex_s, obs_s, hist_s])
        limits = ['LEXICAL_ONLY_NO_ALIAS_CHECK', 'OBSERVED_AT_TIME_ONLY', 'EXCLUSIVE_WRITE_NOT_PROVEN', 'RACE_NOT_EXCLUDED']
        sub = {'lexical': lex_s, 'observed_at_time': obs_s, 'precondition_history': hist_s}
        provided = 'RO' if self.phase != 'accept' else 'RC'
        return self._mk('PATH_SCOPE', status, 'RO', provided, limits, lex_r | obs_r | hist_r, 'S4 observer; writer evidence P-CN1', subchecks=sub)

    def _g_tool(self):
        reasons = set()
        statuses = []
        if self.grant is None:
            statuses.append('NOT_CHECKED')
            reasons.add('GRANT_MISSING')
        elif TOOL not in (self.grant.get('scope') or {}).get('tools', []):
            statuses.append('NOT_MET')
            reasons.add('GRANT_OUT_OF_SCOPE')
        else:
            statuses.append('MET')
        snap_status, snap_reasons = self.snap
        statuses.append(snap_status)
        reasons |= snap_reasons
        pin = _digest_hex(self.protocol.get('entrypoint_sha256'))
        if self.phase != 'accept':
            current = observer.entrypoint_sha256()
            if current is None:
                statuses.append('NOT_CHECKED')
                reasons.add('OBSERVATION_UNAVAILABLE')
            elif current != pin:
                statuses.append('NOT_MET')
                reasons.add('ENTRYPOINT_PIN_MISMATCH')
        else:
            prepared = self.evidence['prepared'] if self.evidence else None
            if prepared is None:
                statuses.append('NOT_CHECKED')
                reasons.add('PRECONDITION_PROOF_MISSING')
            elif _digest_hex(prepared.get('entrypoint_sha256')) != pin:
                statuses.append('NOT_MET')
                reasons.add('ENTRYPOINT_PIN_MISMATCH')
        return self._mk('TOOL_SCOPE', _fold(statuses), 'DCO', 'DCO', ['PIN_IS_VERSION_COMPARE_ADVISORY', 'PROCESS_NOT_PROVEN',
                                                                     'OWNER_BUILD_TASK_ROUNDTRIP_C1_PROJECTION'], reasons,
                        'policy owner_protocols; S4 observer')

    def _g_envelope(self):
        return self._mk('ENVELOPE', self.env_status, 'DC', 'DC', self.env_limits, self.env_reasons, 'host (not measured)')

    def _binding_state(self, pos, reports, kind):
        """(status, reasons) cho một record effect/result theo BindingReport."""
        report = reports.get(pos)
        if report is None:
            return 'NOT_CHECKED', {'BINDING_INCOMPLETE'}
        rels = dict((r.name, r) for r in report.relations)
        if any(r.state == 'MISMATCH' for r in report.relations):
            return 'NOT_MET', {'BINDING_MISMATCH'}
        if any(r.state == 'UNSUPPORTED' for r in report.relations):
            return 'UNSUPPORTED', {'UNSUPPORTED_BINDING_PART'}
        must = {'effect': ('B-ACTION-OWN', 'B-ACTION-IN-TASK'), 'outcome': ('B-ACTION-OWN', 'B-ACTION-IN-TASK', 'B-OUT-EFFECT'),
                'result': ('B-OUT-RESULT',)}[kind]
        rec = self.records[pos]
        if kind == 'effect' and 'outputs' in rec.get('binding', {}):
            return 'NOT_MET', {'BINDING_MISMATCH'}
        if not report.recomputation_complete or any(rels.get(n) is None or rels[n].state != 'MATCH' for n in must):
            return 'NOT_CHECKED', {'BINDING_INCOMPLETE'}
        return 'MET', set()

    def _g_binding(self, route, reports):
        statuses, reasons = [], set()
        wanted = []
        if self.phase == 'effect':
            wanted.append(('REQUEST', 'effect', 'EFFECT_RECORD_MISSING', 'DUPLICATE_EFFECT_RECORD'))
        elif self.phase == 'accept':
            wanted.append(('OUTCOME', 'outcome', 'OUTCOME_RECORD_MISSING', 'DUPLICATE_EFFECT_RECORD'))
            wanted.append(('result', 'result', 'RESULT_RECORD_MISSING', 'DUPLICATE_RESULT_RECORD'))
        for key, kind, missing, duplicate in wanted:
            found = self.pos[key]
            if len(found) == 0:
                statuses.append('NOT_CHECKED')
                reasons.add(missing)
            elif len(found) > 1:
                statuses.append('NOT_MET')
                reasons.add(duplicate)
            else:
                s, r = self._binding_state(found[0], reports, kind)
                statuses.append(s)
                reasons |= r
        if self.phase == 'accept' and len(self.pos['REQUEST']) > 1:
            statuses.append('NOT_MET')
            reasons.add('DUPLICATE_EFFECT_RECORD')
        for stage in ('REQUEST', 'OUTCOME'):
            for p in self.pos[stage]:
                if route.evaluated and routing.declared_mismatch(route, self.records[p].get('routing')):
                    statuses.append('NOT_MET')
                    reasons.add('ROUTE_DECLARED_MISMATCH')
        return self._mk('BINDING', _fold(statuses), 'RC', 'RC', ['FILE_BYTES_DECLARED_ONLY'], reasons, 'checker (recomputed); bytes: S4 observer')

    def _g_input(self):
        inputs = self.task['inputs']
        if self.phase in ('effect', 'accept'):
            obs, reasons, statuses = self.obs, set(), []
            if not obs['available']:
                return self._mk('INPUT_REVISION', 'UNSUPPORTED' if obs['reason'] in UNSUPPORTED_OBSERVATION else 'NOT_CHECKED', 'O', '',
                                ['OBSERVED_AT_TIME_ONLY'], {'OBSERVATION_UNAVAILABLE'}, 'S4 observer')
            seen = dict((i.get('path'), i.get('sha256')) for i in obs['inputs'] if isinstance(i, dict))
            for item in inputs:
                sha = seen.get(item['path'])
                if sha is None:
                    statuses.append('NOT_CHECKED')
                    reasons.add('OBSERVATION_UNAVAILABLE')
                elif sha != item['digest']:
                    statuses.append('NOT_MET')
                    reasons.add('INPUT_CHANGED_SINCE_READ')
                else:
                    statuses.append('MET')
            limits = ['OBSERVED_AT_TIME_ONLY'] + ([] if inputs else ['NO_INPUTS_DECLARED'])
            if self.phase == 'accept':
                ev = self.evidence
                limits.append('HISTORICAL_PUBLISH_INPUTS_CHECKED')
                if not ev or ev['prepared'] is None:
                    statuses.append('NOT_CHECKED')
                    reasons.add('PRECONDITION_PROOF_MISSING')
                else:
                    rel = binding.compare_object_sets(inputs, ev['prepared']['inputs_observed_at_publish'],
                                                      'EXACT_QUALIFIED', name='C-INPUTS')
                    if rel.state == 'UNSUPPORTED':
                        statuses.append('UNSUPPORTED')
                        reasons.add('UNSUPPORTED_BINDING_PART')
                    elif rel.state != 'MATCH':
                        statuses.append('NOT_MET')
                        reasons.add('INPUT_CHANGED_SINCE_READ')
                    else:
                        statuses.append('MET')
            proof = 'DCO' if self.phase == 'accept' else 'DO'
            owner = 'S4 observer; writer evidence P-CN1' if self.phase == 'accept' else 'S4 observer'
            return self._mk('INPUT_REVISION', _fold(statuses), proof, proof, limits, reasons, owner)
        return self._mk('INPUT_REVISION', 'NOT_YET_DUE', 'DO', '', [], set(), 'S4 observer')

    def _expected_artifacts(self):
        published = self.evidence['published']
        return [{'path': self.target, 'digest': published['content']['sha256'], 'role': 'ACTUAL_BYTES'}]

    def _match(self, left, right, name='object_sets'):
        return binding.compare_object_sets(left, right, 'EXACT_QUALIFIED', name=name).state

    def _g_outcome(self):
        limits = ['TAMPER_RESISTANCE_NONE', 'EVIDENCE_IN_AGENT_WRITABLE_ZONE', 'AT_TIME_CURRENT_BYTES_ONLY']
        if self.phase != 'accept':
            return self._mk('ACTUAL_OUTCOME', 'NOT_YET_DUE', 'CRO', '', limits, set(), 'S4 observer; writer evidence P-CN1')
        reasons, statuses = set(), []
        if len(self.pos['OUTCOME']) != 1 or len(self.pos['result']) != 1:
            for key, miss, dup in (('OUTCOME', 'OUTCOME_RECORD_MISSING', 'DUPLICATE_EFFECT_RECORD'), ('result', 'RESULT_RECORD_MISSING', 'DUPLICATE_RESULT_RECORD')):
                if len(self.pos[key]) != 1:
                    reasons.add(miss if not self.pos[key] else dup)
            return self._mk('ACTUAL_OUTCOME', 'NOT_CHECKED', 'CRO', '', limits, reasons, 'S4 observer; writer evidence P-CN1')
        hist_status, hist_reasons = self.hist
        if hist_status != 'MET':
            return self._mk('ACTUAL_OUTCOME', 'NOT_CHECKED', 'CRO', '', limits, hist_reasons or {'PRECONDITION_PROOF_MISSING'},
                            'S4 observer; writer evidence P-CN1')
        out, res = self.records[self.pos['OUTCOME'][0]], self.records[self.pos['result'][0]]
        outcome = out.get('outcome') if isinstance(out.get('outcome'), dict) else {}
        if outcome.get('status') != 'APPLIED':
            statuses.append('NOT_MET')
            reasons.add('ACTION_INCOMPLETE')
        receipt = out.get('receipt_ref')
        published = self.evidence['published']
        if not isinstance(receipt, dict):
            statuses.append('NOT_CHECKED')
            reasons.add('PRECONDITION_PROOF_MISSING')
        else:
            att = receipt.get('attribution') if isinstance(receipt.get('attribution'), dict) else {}
            if (receipt.get('kind') != 'effect_receipt' or receipt.get('locator') != '.agent/runtime/publish/%s.published.json' % self.rid
                    or receipt.get('digest') != self.evidence['raw_published_sha256']
                    or att.get('source_class') != 'TOOL_OBSERVATION' or att.get('channel') != 'TOOL_OUTPUT'):
                statuses.append('NOT_MET')
                reasons.add('PRECONDITION_PROOF_MISSING')
        expected = self._expected_artifacts()
        for left in (outcome.get('artifacts'), res.get('artifacts'), (out.get('binding') or {}).get('outputs'), (res.get('binding') or {}).get('outputs')):
            state = self._match(left, expected) if isinstance(left, list) else 'ONE_SIDED'
            if state == 'UNSUPPORTED':
                statuses.append('UNSUPPORTED')
                reasons.add('UNSUPPORTED_BINDING_PART')
            elif state != 'MATCH':
                statuses.append('NOT_MET')
                reasons.add('OPERATION_MISMATCH')
        performed = res.get('actions_performed')
        action_digest = binding.recompute_task(self.task).actions
        if not isinstance(performed, list) or not performed:
            statuses.append('NOT_CHECKED')
            reasons.add('ACTION_UNREPORTED')
        else:
            try:
                digests = [canon.digest_of(canon.action_part(a)) for a in performed]
            except (canon.Unsupported,) + _MALFORMED:
                digests = None
            if digests is None or len(action_digest) != 1 or action_digest[0].state != 'COMPUTED' or digests != [action_digest[0].digest]:
                statuses.append('NOT_MET')
                reasons.add('OPERATION_MISMATCH')
        statuses.append(self._current_bytes(published, reasons))
        return self._mk('ACTUAL_OUTCOME', _fold(statuses), 'CRO', 'CRO', limits, reasons, 'S4 observer; writer evidence P-CN1')

    def _current_bytes(self, published, reasons):
        obs = self.obs
        target = obs['target'] if isinstance(obs['target'], dict) else None
        if not obs['available'] or target is None:
            reasons.add('OBSERVATION_UNAVAILABLE')
            return 'UNSUPPORTED' if obs['reason'] in UNSUPPORTED_OBSERVATION else 'NOT_CHECKED'
        content = published['content']
        if (target.get('exists') is not True or target.get('regular') is not True or target.get('sha256') != content['sha256']
                or target.get('size') != content['size']):
            reasons.add('CHANGED_AFTER_PUBLISH')
            return 'NOT_MET'
        if target.get('identity') != published.get('identity'):
            reasons.add('CHANGED_AFTER_PUBLISH')  # same bytes under another file identity is not the published object
            self.details.append('current target identity differs from the published identity')
            return 'NOT_MET'
        return 'MET'

    def _g_requirements(self):
        limits = ['USER_ACCEPTANCE_IS_DECLARED', 'SEMANTIC_NOT_VERIFIED']
        if self.phase != 'accept':
            return self._mk('REQUIREMENTS', 'NOT_YET_DUE', 'D', '', limits, set(), 'user')
        if len(self.pos['result']) != 1:
            return self._mk('REQUIREMENTS', 'NOT_CHECKED', 'D', '', limits,
                            {'RESULT_RECORD_MISSING' if not self.pos['result'] else 'DUPLICATE_RESULT_RECORD'}, 'user')
        res = self.records[self.pos['result'][0]]
        ua = res.get('user_acceptance')
        reasons = set()
        if 'ACCEPTED_FOR_INTEGRATION' in res.get('acceptance_states', []):
            reasons.add('ACCEPTANCE_CLAIM_NOT_SUPPORTED')  # no supported review can justify it in this flow
        if not isinstance(ua, dict):
            return self._mk('REQUIREMENTS', 'NOT_MET' if reasons else 'NOT_CHECKED', 'D', '', limits, reasons | {'EVIDENCE_NOT_VERIFIED'}, 'user')
        status, more = self._d4(res, ua)
        reasons |= more
        if 'ACCEPTANCE_CLAIM_NOT_SUPPORTED' in reasons and status != 'UNSUPPORTED':
            status = 'NOT_MET'
        return self._mk('REQUIREMENTS', status, 'D', 'D', limits, reasons, 'user')

    def _d4(self, res, ua):
        stale, incomplete, reasons = False, False, set()
        att = (ua.get('ref') or {}).get('attribution') or {}
        if att.get('source_class') != 'USER_CONFIRMATION' or att.get('channel') not in USER_CHANNELS or not att.get('evidence_locator'):
            reasons.add('USER_CONFIRMATION_MISSING')
        task = self.task
        mine = binding.recompute_task(task)
        if (ua.get('task_id') != task.get('task_id') or ua.get('task_revision') != task.get('task_revision') or ua.get('result_id') != res.get('result_id')
                or mine.accepted_task.state != 'COMPUTED' or ua.get('accepted_task_digest') != mine.accepted_task.digest):
            stale = True
        reqs = task['acceptance']['requirements']
        mandatory = set(r['req_id'] for r in reqs if r.get('mandatory'))
        given = set(ua.get('accepted_requirements', []))
        if given - set(r['req_id'] for r in reqs):
            stale = True
        if mandatory - given:
            incomplete = True
        accepted = ua.get('accepted_artifacts')
        for right in (res.get('artifacts'), self._expected_artifacts() if self.evidence and self.evidence['published'] else None):
            if not isinstance(accepted, list) or not isinstance(right, list):
                stale = True
                continue
            state = binding.compare_object_sets(accepted, right, 'EXACT_QUALIFIED', name='D4-ARTIFACTS').state
            if state == 'UNSUPPORTED':
                reasons.add('UNSUPPORTED_BINDING_PART')
            elif state != 'MATCH':
                stale = True
        for item in res.get('requirements', []):
            if item.get('req_id') in mandatory and item.get('status') in ('NOT_MET', 'MISSING', 'BLOCKED'):
                reasons.add('MANDATORY_REQUIREMENT_NOT_MET')
        if stale:
            reasons.add('USER_ACCEPTANCE_STALE')
        if incomplete:
            reasons.add('USER_ACCEPTANCE_INCOMPLETE')
        if 'UNSUPPORTED_BINDING_PART' in reasons and not stale:
            return 'UNSUPPORTED', reasons
        if stale or 'USER_CONFIRMATION_MISSING' in reasons or 'MANDATORY_REQUIREMENT_NOT_MET' in reasons:
            return 'NOT_MET', reasons
        if incomplete:
            return 'NOT_CHECKED', reasons
        return 'USER_ACCEPTED_DECLARED', reasons

    # ---------------------------------------------------------------- tổng hợp
    def finish(self, route, reports):
        """Tính gate sau khi routing đã chạy. `reports` = {position: BindingReport} do entry đã tính."""
        self.snap = self._snapshot()
        self.hist = self._history()
        gates = [self._g_grant(), self._g_path(route), self._g_tool(), self._g_envelope(), self._g_binding(route, reports), self._g_input(),
                 self._g_outcome(), self._g_requirements()]
        self.gates, self.gates_evaluated = gates, True
        for gate in gates:
            if gate['status'] in ('NOT_MET', 'NOT_CHECKED', 'UNSUPPORTED'):
                self.blocked.update(gate['reasons'] or ['GATE_%s_%s' % (gate['gate'], gate['status'])])
        if route.evaluated and route.status == 'RESOLVED' and tuple(route.matched) != ('R-READ_DRAFT',):
            self.blocked.add('ROUTE_NOT_P_CN1_LIGHT')
        counts = dict.fromkeys(('due_gates', 'met', 'not_required', 'not_yet_due', 'not_checked', 'unsupported', 'not_met', 'user_accepted_declared'), 0)
        for gate in gates:
            status = gate['status']
            counts['not_yet_due' if status == 'NOT_YET_DUE' else 'due_gates'] += 1
            key = status.lower()
            if key in counts and key not in ('due_gates', 'not_yet_due'):
                counts[key] += 1
        inconsistent = counts['not_met'] > 0 or bool(self.deny) or bool(self.blocked & {'BINDING_MISMATCH', 'DUPLICATE_EFFECT_RECORD',
                                                                                         'DUPLICATE_RESULT_RECORD', 'ROUTE_DECLARED_MISMATCH'})
        self.aggregate = {'records_checked_state': 'INCONSISTENT' if inconsistent else 'CONSISTENT_IN_CHECKED_SCOPE'}
        self.aggregate.update(counts)
        self.aggregate['open_assumptions'] = [a for a in route.assumptions if a.get('status') == 'OPEN']
        self.aggregate['conclusion_scope'] = 'RECORD_CONSISTENCY_IN_MEMORY'
        self.details.append('p_cn1 gates: ' + ', '.join('%s=%s' % (g['gate'], g['status']) for g in gates))
        if self.observer_ran:
            self.details.append('observer: available=%s target_absent_at_time=%s' % (str(bool(self.obs['available'])).lower(),
                                                                                    str(self.target_absent).lower()))

    @property
    def all_due_ok(self):
        return self.gates_evaluated and all(g['status'] in OK_STATES for g in self.gates)
