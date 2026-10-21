#!/usr/bin/env python3
"""Entrypoint checker v3 candidate (G-02-C2). KHÔNG phải checker đầy đủ, không cấp quyền / not a full checker, grants nothing.

Không `--root`: entry `--contract v3`, loader strict, canonicalization, binding và routing thuần cho luồng một action (stage BINDING_ROUTING_ONLY),
cấu trúc hợp lệ luôn BLOCKED (CANDIDATE_EVALUATION_NOT_IMPLEMENTED) hoặc DENY/UNSUPPORTED/BLOCKED; không PASS, không đọc `tools/`.
Có `--root` (stage P_CN1_ONE_FILE): thêm gate + observer chỉ đọc + receipt + D4 cho đúng một task/action `create_new`/target/grant của protocol P-CN1.
Chỉ khi đó mới có PASS (ADVISORY, effect_authorized=false). Hợp đồng output ở v3/README.md.
Without a root a structurally valid input is never PASS or NOT_APPLICABLE; with an explicit root only the one-file P-CN1 flow can PASS.

Chạy / run:  python -B -I <absolute path>/control_check_v3.py --contract v3 --phase {dispatch,effect,accept} [--root DIR] [--format json|text] bundle.json
`--contract` bắt buộc, chỉ nhận v3, không mặc định, không suy từ record. Không gọi, không chọn và không fallback sang checker v1/v2.
Root chỉ chứa dữ liệu: code owner luôn nạp từ cây nguồn LAW cố định, không từ root.
"""
import argparse
import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_NAME = 'law_cvf_check_v3'
PROG = 'control_check_v3.py'
PHASES = ('dispatch', 'effect', 'accept')
CONTRACTS = ('v3',)

CHECK_VERSION = 'law.cvf.check/3'
CANDIDATE_STATUS = 'CANDIDATE_NOT_ACTIVE'
IMPLEMENTATION_STAGE = 'BINDING_ROUTING_ONLY'
IMPLEMENTATION_STAGE_ROOT = 'P_CN1_ONE_FILE'
PHASE_SCOPE_STRUCTURE = 'STRUCTURE_ONLY'
COVERAGE_FLAGS = ('record_structure_checked', 'binding_evaluated', 'routing_evaluated', 'gates_evaluated',
                  'artifact_bytes_observed', 'target_existence_observed', 'actual_operation_observed',
                  'requirements_semantic_verified', 'owner_protection')
AGGREGATE_COUNTS = ('due_gates', 'met', 'not_required', 'not_yet_due', 'not_checked', 'unsupported', 'not_met', 'user_accepted_declared')
OUTPUT_KEYS = ('check_version', 'contract', 'selection', 'candidate_status', 'implementation_stage', 'evaluation_basis', 'phase',
               'phase_scope', 'disposition', 'effect_authorized', 'assurance_level', 'init_error', 'reasons', 'details', 'owners',
               'route', 'gates', 'aggregate', 'coverage')


def _not_evaluated_route():
    return {'evaluated': False, 'rows': [], 'status': None, 'assumptions': []}

# Ánh xạ trạng thái liên kết grant (refs.link_grants) sang lý do; LINKED chỉ là lời khai nối, không phải quyền.
# Grant-link state to reason; LINKED only means the claim links to a record, never authority.
_LINK_BLOCK = {'CONFLICT': 'REF_CONFLICT', 'AMBIGUOUS': 'REF_AMBIGUOUS', 'NO_GRANT_RECORD': 'GRANT_MISSING', 'INCOMPLETE': 'REF_INCOMPLETE'}


# ---------------------------------------------------------------- bootstrap (không dùng cwd/PYTHONPATH; không sửa đường nạp module)
def _load_package():
    """Nạp package v3 bằng đường tuyệt đối cạnh file này; đúng dưới `python -I` từ thư mục bất kỳ."""
    init = HERE / 'v3' / '__init__.py'
    mod = sys.modules.get(PACKAGE_NAME)
    if mod is not None:
        if Path(getattr(mod, '__file__', None) or '').resolve() != init.resolve():
            raise RuntimeError('module %s is already loaded from another location' % PACKAGE_NAME)
        return mod
    spec = importlib.util.spec_from_file_location(PACKAGE_NAME, str(init), submodule_search_locations=[str(HERE / 'v3')])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(PACKAGE_NAME, None)
        raise
    return mod


# ---------------------------------------------------------------- đánh giá / evaluation
class _Evidence(object):
    """Lý do và cờ đã tính. Cờ chỉ bật khi quan hệ thực sự được tính; không bật vì helper tồn tại."""

    def __init__(self):
        self.deny = set()
        self.unsupported = set()
        self.blocked = set()
        self.details = []
        self.binding_evaluated = False
        self.routing_evaluated = False
        self.route = _not_evaluated_route()
        self.wf = None  # workflow P-CN1 (chỉ khi có root) / one-file workflow, only with an explicit root


def _workflow_failed(ev, exc):
    ev.unsupported.add('WORKFLOW_ERROR')
    ev.details.append('the one-file workflow failed (%s); nothing was concluded from it' % type(exc).__name__)
    if ev.wf is not None:
        ev.wf.supported = False
        ev.wf.gates, ev.wf.gates_evaluated = [], False


def _evaluate(bundle, owners, phase, root=None):
    """Binding, liên kết grant và routing cho bundle đã qua cấu trúc. Chỉ đọc bundle và hai owner đã nạp; không đọc artifact/locator/mạng."""
    refs = importlib.import_module(PACKAGE_NAME + '.refs')
    binding = importlib.import_module(PACKAGE_NAME + '.binding')
    routing = importlib.import_module(PACKAGE_NAME + '.routing')
    ev = _Evidence()
    records = refs.records_of(bundle)
    index = refs.build_index(records)
    claims = refs.collect_claims(index)
    if any(group.status == 'CONFLICT' for group in claims.groups()):
        ev.blocked.add('REF_CONFLICT')

    for pos, rec in enumerate(records):
        rtype = rec.get('record_type')
        # A task's own projected sets must be valid even without a binding record.
        # Recomputing a part is not a binding comparison and does not set coverage.
        if rtype == 'task':
            parts = binding.recompute_task(rec)
            if parts.actions_malformed or any(part.state == 'UNSUPPORTED' for part in
                                              (parts.intent, parts.accepted_task, parts.context) + parts.actions):
                ev.unsupported.add('UNSUPPORTED_BINDING_PART')
        # Known loss is a task-wide veto even when routing cannot select a supported task/action.
        # Do not let MULTI_TASK_UNSUPPORTED hide an already declared preservation loss.
        if rtype == 'task' and any(p.get('known_loss_state') == 'KNOWN_LOSS'
                                   for p in rec['effects'].get('preservation', [])):
            ev.deny.add('KNOWN_PRESERVATION_LOSS')
        if rtype in ('task', 'effect'):
            for link in refs.link_grants(index, claims, pos):
                if link.state == 'UNSUPPORTED':
                    ev.unsupported.add('REF_UNSUPPORTED')
                elif link.state != 'LINKED':
                    ev.blocked.add(_LINK_BLOCK.get(link.state, 'REF_INCOMPLETE'))

    policy_ctx = binding.make_policy_context(owners.policy_bytes)
    reports = {}
    for pos, rec in enumerate(records):
        if rec.get('record_type') not in ('review', 'effect', 'result') or not isinstance(rec.get('binding'), dict):
            continue
        # Validate the self-declared input set independently of task resolution.
        # Keep the normal missing-counterpart relations INCOMPLETE below; equality
        # with itself proves neither a binding nor observation of artifact bytes.
        inputs = rec['binding'].get('inputs')
        validity = binding.compare_object_sets(inputs, inputs, 'EXACT_QUALIFIED', name='B-INPUTS')
        if validity.state == 'UNSUPPORTED':
            ev.unsupported.add('UNSUPPORTED_BINDING_PART')
        report = binding.compare_binding(index, pos, policy_ctx)
        reports[pos] = report
        if report.recomputation_complete:
            ev.binding_evaluated = True
        for rel in report.relations:
            if rel.state == 'MISMATCH':
                ev.blocked.add('BINDING_MISMATCH')
            elif rel.state == 'UNSUPPORTED':
                ev.unsupported.add('UNSUPPORTED_BINDING_PART')
            elif rel.state in ('INCOMPLETE', 'AMBIGUOUS', 'ONE_SIDED'):
                ev.blocked.add('BINDING_INCOMPLETE')
        ev.details.append('binding position %d: %s' % (pos, ', '.join('%s=%s' % (r.name, r.state) for r in report.relations)))

    tasks = [pos for pos, rec in enumerate(records) if rec.get('record_type') == 'task']
    route_policy = routing.load_route_policy(owners.policy_bytes)
    external = None
    if root is not None:
        # Only with an explicit root: the observer and gates are loaded here (the no-root path never touches tools/).
        # Any unexpected failure stays fail-closed (UNSUPPORTED, no gates, no traceback, no message echoed).
        try:
            workflow = importlib.import_module(PACKAGE_NAME + '.workflow')
            ev.wf = workflow.Workflow(records, index, claims, phase, root, owners, refs)
            external = ev.wf.prepare()
        except Exception as exc:
            _workflow_failed(ev, exc)
            external = None
    if len(tasks) > 1:
        ev.unsupported.add('MULTI_TASK_UNSUPPORTED')
        result = routing.RouteResult()
    elif tasks:
        result = routing.evaluate_task(records[tasks[0]], route_policy, phase, external)
    else:
        result = routing.RouteResult()
    ev.deny.update(result.deny)
    ev.unsupported.update(result.unsupported)
    ev.blocked.update(result.blocked)
    ev.routing_evaluated = result.evaluated
    ev.route = result.as_dict()
    if result.evaluated:
        for rec in records:
            if rec.get('record_type') == 'effect' and routing.declared_mismatch(result, rec.get('routing')):
                ev.blocked.add('ROUTE_DECLARED_MISMATCH')
        ev.details.append('route: status=%s rows=%d' % (result.status, len(result.rows)))
    if ev.wf is not None:
        if ev.wf.supported and result.evaluated:
            try:
                ev.wf.finish(result, reports)
            except Exception as exc:
                _workflow_failed(ev, exc)
        ev.deny |= ev.wf.deny
        ev.unsupported |= ev.wf.unsupported
        ev.blocked |= ev.wf.blocked
        ev.details.extend(ev.wf.details)
    return ev


def _decide(ev):
    """DENY (known-loss) > UNSUPPORTED (phần không hỗ trợ) > BLOCKED. PASS chỉ khi có workflow P-CN1 hỗ trợ, route RESOLVED và mọi gate đến hạn đạt."""
    reasons = set(ev.deny) | set(ev.unsupported) | set(ev.blocked)
    if ev.deny:
        return 'DENY', reasons
    if ev.unsupported:
        return 'UNSUPPORTED', reasons
    wf = ev.wf
    if wf is not None and wf.supported and wf.gates_evaluated:
        if not reasons and wf.all_due_ok and ev.route['status'] == 'RESOLVED' and ev.routing_evaluated:
            return 'PASS', set()
        return 'BLOCKED', reasons or {'GATE_NOT_SATISFIED'}
    reasons.add('CANDIDATE_EVALUATION_NOT_IMPLEMENTED')
    return 'BLOCKED', reasons


# ---------------------------------------------------------------- output
def _phase_scope(structure_ok, ev):
    if not structure_ok:
        return None
    suffix = []
    if ev is not None and ev.binding_evaluated:
        suffix.append('BINDING')
    if ev is not None and ev.routing_evaluated:
        suffix.append('ROUTING')
    if ev is not None and ev.wf is not None and ev.wf.gates_evaluated:
        suffix.append('GATES')
    if ev is not None and ev.wf is not None and ev.wf.observer_ran:
        suffix.append('OBSERVER')
    return 'STRUCTURE_' + '_'.join(suffix) if suffix else PHASE_SCOPE_STRUCTURE


def _build(phase, selection, disposition, reasons, details, init_error, basis, structure_ok, schema_sha, policy_sha, ev=None, rooted=False):
    coverage = dict.fromkeys(COVERAGE_FLAGS, False)
    coverage['record_structure_checked'] = bool(structure_ok)
    coverage['binding_evaluated'] = bool(ev and ev.binding_evaluated)
    coverage['routing_evaluated'] = bool(ev and ev.routing_evaluated)
    coverage['owner_protection'] = 'NOT_PROVEN'
    wf = ev.wf if ev is not None else None
    gates = []
    if wf is not None:
        coverage['gates_evaluated'] = bool(wf.gates_evaluated)
        coverage['target_existence_observed'] = bool(wf.target_observed)
        coverage['artifact_bytes_observed'] = bool(wf.bytes_observed)
    if wf is not None and wf.gates_evaluated:
        gates = wf.gates
        aggregate = dict(wf.aggregate)
    else:
        aggregate = {'records_checked_state': 'NOT_EVALUATED'}
        aggregate.update(dict.fromkeys(AGGREGATE_COUNTS, 0))
        aggregate['open_assumptions'] = []
        aggregate['conclusion_scope'] = 'RECORD_CONSISTENCY_IN_MEMORY'
    return {
        'check_version': CHECK_VERSION,
        'contract': 'v3',
        'selection': selection,
        'candidate_status': CANDIDATE_STATUS,
        'implementation_stage': IMPLEMENTATION_STAGE_ROOT if rooted else IMPLEMENTATION_STAGE,
        'evaluation_basis': basis,
        'phase': phase,
        'phase_scope': _phase_scope(structure_ok, ev),
        'disposition': disposition,
        'effect_authorized': False,
        'assurance_level': 'ADVISORY' if disposition == 'PASS' else 'UNVERIFIED',
        'init_error': bool(init_error),
        'reasons': sorted(set(reasons)),
        'details': list(details) + (list(ev.details) if ev is not None else []),
        'owners': {'schema_sha256': schema_sha, 'policy_sha256': policy_sha},
        'route': dict(ev.route) if ev is not None else _not_evaluated_route(),
        'gates': gates,
        'aggregate': aggregate,
        'coverage': coverage,
    }


def _init_error(phase, selection, reasons, details, schema_sha=None, policy_sha=None, rooted=False):
    return _build(phase, selection, 'UNSUPPORTED', reasons, details, True, None, False, schema_sha, policy_sha, rooted=rooted)


def _check(data, phase, selection, root=None):
    rooted = root is not None
    try:
        _load_package()
        loader = importlib.import_module(PACKAGE_NAME + '.loader')
    except Exception as exc:
        return _init_error(phase, selection, {'PACKAGE_UNAVAILABLE'}, ['checker v3 package could not be loaded (%s)' % type(exc).__name__],
                           rooted=rooted)
    if rooted and not os.path.isdir(root):
        return _init_error(phase, selection, {'ROOT_UNUSABLE'}, ['the explicit project root is not an existing directory (path withheld)'],
                           rooted=True)
    try:
        owners = loader.load_owners()
    except loader.InitFailure as exc:
        return _init_error(phase, selection, exc.reasons, exc.details, exc.schema_sha256, exc.policy_sha256, rooted)
    bundle, outcome = loader.inspect_structure(data, owners)
    if bundle is None:
        return _build(phase, selection, outcome.disposition, outcome.reasons, outcome.details, False, outcome.evaluation_basis,
                      False, owners.schema_sha256, owners.policy_sha256, rooted=rooted)
    ev = _evaluate(bundle, owners, phase, os.path.abspath(root) if rooted else None)
    disposition, reasons = _decide(ev)
    return _build(phase, selection, disposition, reasons, outcome.details, False, outcome.evaluation_basis, True,
                  owners.schema_sha256, owners.policy_sha256, ev, rooted)


def check_bytes(data, phase, contract, *, project_root=None):
    """API: kiểm một bundle (bytes) bằng contract v3. Không fallback, không check_records, không tiêm owner/facts/observer.

    `project_root` (str, tường minh, chỉ dữ liệu) bật workflow P-CN1 một file; không có thì chỉ diagnostic, không bao giờ PASS.
    """
    if not isinstance(data, bytes):
        raise TypeError('data must be bytes')
    if project_root is not None and not (isinstance(project_root, str) and project_root):
        raise TypeError('project_root must be a non-empty str or None')
    if contract != 'v3':
        raise ValueError('this entry supports contract "v3" only; v1 and v2 have their own entries and are never tried here')
    if phase not in PHASES:
        raise ValueError('phase must be one of %s' % ', '.join(PHASES))
    return _check(data, phase, 'API_EXPLICIT', project_root)


def exit_code(result):
    """2 lỗi khởi tạo/đọc; 0 chỉ khi PASS của workflow P-CN1 có root; 1 mọi trường hợp khác. Không có exit 3 (NOT_APPLICABLE)."""
    if result.get('init_error'):
        return 2
    return 0 if result.get('disposition') == 'PASS' else 1


def _flag(value):
    return 'true' if value else 'false'


def _format_text(res):
    cov, agg = res['coverage'], res['aggregate']
    lines = [
        '%s contract=%s selection=%s stage=%s candidate=%s phase=%s phase_scope=%s disposition=%s effect_authorized=%s assurance=%s init_error=%s basis=%s'
        % (res['check_version'], res['contract'], res['selection'], res['implementation_stage'], res['candidate_status'], res['phase'],
           res['phase_scope'] if res['phase_scope'] is not None else 'null', res['disposition'], _flag(res['effect_authorized']),
           res['assurance_level'], _flag(res['init_error']), res['evaluation_basis'] if res['evaluation_basis'] is not None else 'null'),
        'reasons: ' + (', '.join(res['reasons']) if res['reasons'] else '-'),
    ]
    lines.extend('detail: ' + d for d in res['details'])
    lines.append('owners: schema_sha256=%s policy_sha256=%s' % (res['owners']['schema_sha256'] or 'null', res['owners']['policy_sha256'] or 'null'))
    lines.append('coverage: ' + ' '.join('%s=%s' % (k, cov[k] if k == 'owner_protection' else _flag(cov[k])) for k in COVERAGE_FLAGS))
    lines.append('route: evaluated=%s rows=%d status=%s assumptions=%d' % (_flag(res['route']['evaluated']), len(res['route']['rows']),
                                                                        res['route']['status'] if res['route']['status'] is not None else 'null',
                                                                        len(res['route']['assumptions'])))
    lines.append('aggregate: records_checked_state=%s %s open_assumptions=%d conclusion_scope=%s'
                 % (agg['records_checked_state'], ' '.join('%s=%d' % (k, agg[k]) for k in AGGREGATE_COUNTS), len(agg['open_assumptions']),
                    agg['conclusion_scope']))
    lines.append('gates=%d' % len(res['gates']))
    for gate in res['gates']:
        lines.append('gate: %s status=%s reasons=%s' % (gate['gate'], gate['status'], ','.join(gate['reasons']) or '-'))
    return '\n'.join(lines)


# ---------------------------------------------------------------- CLI
def _exit_value(code):
    if code is None:
        return 0
    return code if isinstance(code, int) else 1


def _parser():
    ap = argparse.ArgumentParser(prog=PROG, allow_abbrev=False,
                                 description='LAW control record checker v3 candidate (S3-C/D BINDING_ROUTING_ONLY). Never authorizes an effect.')
    ap.add_argument('--contract', required=True, action='append', choices=CONTRACTS, help='explicit contract; only v3; no default; once')
    ap.add_argument('--phase', required=True, choices=PHASES)
    ap.add_argument('--root', action='append', default=None, help='explicit project root (data only); enables the one-file P-CN1 workflow; once')
    ap.add_argument('--format', choices=('json', 'text'), default='json')
    ap.add_argument('bundle', help='bundle or single record JSON file')
    return ap


def _read_bundle(path, limit):
    with open(path, 'rb') as fh:
        return fh.read(limit + 1)


def _run(args):
    ap = _parser()
    try:
        ns = ap.parse_args(args)
        if len(ns.contract) != 1:
            ap.error('--contract was given more than once')
        if ns.root is not None and (len(ns.root) != 1 or not ns.root[0]):
            ap.error('--root must be given once with a non-empty path')
    except SystemExit as exc:
        return _exit_value(exc.code)
    try:
        limit = _load_package().MAX_INPUT_BYTES
        data = _read_bundle(ns.bundle, limit)
    except OSError as exc:
        result = _init_error(ns.phase, 'CLI_EXPLICIT', {'BUNDLE_UNREADABLE'},
                             ['cannot read bundle (%s, errno %s)' % (type(exc).__name__, exc.errno)], rooted=bool(ns.root))
    except Exception as exc:
        result = _init_error(ns.phase, 'CLI_EXPLICIT', {'PACKAGE_UNAVAILABLE'},
                             ['checker v3 package could not be loaded (%s)' % type(exc).__name__], rooted=bool(ns.root))
    else:
        result = _check(data, ns.phase, 'CLI_EXPLICIT', ns.root[0] if ns.root else None)
    text = _format_text(result) if ns.format == 'text' else json.dumps(result, indent=2, ensure_ascii=True)
    sys.stdout.write(text + '\n')
    return exit_code(result)


def main(argv=None):
    return _run(list(sys.argv[1:] if argv is None else argv))


if __name__ == '__main__':
    sys.exit(main())
