#!/usr/bin/env python3
"""Entrypoint checker v2 candidate (G-02-C2/S1, FOUNDATION_ONLY). KHÔNG phải checker đầy đủ, không cấp quyền / not a full checker, grants nothing.

S1 chỉ có: router `--contract`, loader strict, canonicalization và output nền. Chưa có evaluator binding/route/gate: cấu trúc hợp lệ
luôn BLOCKED (CANDIDATE_EVALUATION_NOT_IMPLEMENTED), không bao giờ PASS hay NOT_APPLICABLE. Hợp đồng output ở v2/README.md.
S1 has no evaluator: a structurally valid input is always BLOCKED and never PASS or NOT_APPLICABLE. Output contract: v2/README.md.

Chạy / run:  python -I <absolute path>/control_check_v2.py --contract {v1,v2} --phase {dispatch,effect,accept} [--format json|text] bundle.json
`--contract` bắt buộc, không mặc định, không suy từ record. `v1` chuyển nguyên argv còn lại cho control_check.py (không đổi byte).
"""
import argparse
import importlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_NAME = 'law_cvf_check_v2'
V1_MODULE_NAME = 'law_cvf_check_v1'
PROG = 'control_check_v2.py'
PHASES = ('dispatch', 'effect', 'accept')
CONTRACTS = ('v1', 'v2')

CHECK_VERSION = 'law.cvf.check/2'
CANDIDATE_STATUS = 'CANDIDATE_NOT_ACTIVE'
IMPLEMENTATION_STAGE = 'S1_FOUNDATION_ONLY'
COVERAGE_FLAGS = ('record_structure_checked', 'binding_evaluated', 'routing_evaluated', 'gates_evaluated',
                  'artifact_bytes_observed', 'actual_operation_observed', 'requirements_semantic_verified', 'owner_protection')


class _WrapperError(Exception):
    pass


# ---------------------------------------------------------------- bootstrap (không dùng cwd/PYTHONPATH; không sửa đường nạp module)
def _load_package():
    """Nạp package v2 bằng đường tuyệt đối cạnh file này; đúng dưới `python -I` từ thư mục bất kỳ."""
    init = HERE / 'v2' / '__init__.py'
    mod = sys.modules.get(PACKAGE_NAME)
    if mod is not None:
        if Path(getattr(mod, '__file__', None) or '').resolve() != init.resolve():
            raise RuntimeError('module %s is already loaded from another location' % PACKAGE_NAME)
        return mod
    spec = importlib.util.spec_from_file_location(PACKAGE_NAME, str(init), submodule_search_locations=[str(HERE / 'v2')])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(PACKAGE_NAME, None)
        raise
    return mod


def _load_v1():
    """Nạp checker v1 đóng băng bằng đường tuyệt đối; chỉ gọi từ nhánh `--contract v1`."""
    mod = sys.modules.get(V1_MODULE_NAME)
    if mod is not None:
        return mod
    spec = importlib.util.spec_from_file_location(V1_MODULE_NAME, str(HERE / 'control_check.py'))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[V1_MODULE_NAME] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(V1_MODULE_NAME, None)
        raise
    return mod


# ---------------------------------------------------------------- output
def _build(phase, selection, disposition, reasons, details, init_error, basis, structure_ok, schema_sha, policy_sha):
    coverage = dict.fromkeys(COVERAGE_FLAGS, False)
    coverage['record_structure_checked'] = bool(structure_ok)
    coverage['owner_protection'] = 'NOT_PROVEN'
    return {
        'check_version': CHECK_VERSION,
        'contract': 'v2',
        'selection': selection,
        'candidate_status': CANDIDATE_STATUS,
        'implementation_stage': IMPLEMENTATION_STAGE,
        'evaluation_basis': basis,
        'phase': phase,
        'disposition': disposition,
        'effect_authorized': False,
        'assurance_level': 'UNVERIFIED',
        'init_error': bool(init_error),
        'reasons': sorted(set(reasons)),
        'details': list(details),
        'owners': {'schema_sha256': schema_sha, 'policy_sha256': policy_sha},
        'coverage': coverage,
        'objects': [],
        'gates': [],
    }


def _init_error(phase, selection, reasons, details, schema_sha=None, policy_sha=None):
    return _build(phase, selection, 'UNSUPPORTED', reasons, details, True, None, False, schema_sha, policy_sha)


def _check(data, phase, selection):
    try:
        _load_package()
        loader = importlib.import_module(PACKAGE_NAME + '.loader')
    except Exception as exc:
        return _init_error(phase, selection, {'PACKAGE_UNAVAILABLE'}, ['checker v2 package could not be loaded (%s)' % type(exc).__name__])
    try:
        owners = loader.load_owners()
    except loader.InitFailure as exc:
        return _init_error(phase, selection, exc.reasons, exc.details, exc.schema_sha256, exc.policy_sha256)
    outcome = loader.inspect_bundle(data, owners)
    return _build(phase, selection, outcome.disposition, outcome.reasons, outcome.details, False, outcome.evaluation_basis,
                  outcome.record_structure_checked, owners.schema_sha256, owners.policy_sha256)


def check_bytes(data, phase, contract):
    """API S1: kiểm cấu trúc một bundle (bytes) bằng contract v2. Không fallback, không check_records, không tiêm owner."""
    if not isinstance(data, bytes):
        raise TypeError('data must be bytes')
    if contract != 'v2':
        raise ValueError('S1 supports contract "v2" only; v1 compatibility is a CLI router, not an API')
    if phase not in PHASES:
        raise ValueError('phase must be one of %s' % ', '.join(PHASES))
    return _check(data, phase, 'API_EXPLICIT')


def exit_code(result):
    """2 lỗi khởi tạo/đọc; 1 mọi trường hợp khác. S1 không có exit 0 (PASS) hay 3 (NOT_APPLICABLE)."""
    return 2 if result.get('init_error') else 1


def _flag(value):
    return 'true' if value else 'false'


def _format_text(res):
    cov = res['coverage']
    lines = [
        '%s contract=%s selection=%s stage=%s candidate=%s phase=%s disposition=%s effect_authorized=%s assurance=%s init_error=%s basis=%s'
        % (res['check_version'], res['contract'], res['selection'], res['implementation_stage'], res['candidate_status'],
           res['phase'], res['disposition'], _flag(res['effect_authorized']), res['assurance_level'], _flag(res['init_error']),
           res['evaluation_basis'] if res['evaluation_basis'] is not None else 'null'),
        'reasons: ' + (', '.join(res['reasons']) if res['reasons'] else '-'),
    ]
    lines.extend('detail: ' + d for d in res['details'])
    lines.append('owners: schema_sha256=%s policy_sha256=%s' % (res['owners']['schema_sha256'] or 'null', res['owners']['policy_sha256'] or 'null'))
    lines.append('coverage: ' + ' '.join('%s=%s' % (k, cov[k] if k == 'owner_protection' else _flag(cov[k])) for k in COVERAGE_FLAGS))
    lines.append('objects=0 gates=0')
    return '\n'.join(lines)


# ---------------------------------------------------------------- CLI
def _split_contract(args):
    """Tách cờ --contract, giữ nguyên phần còn lại / split off --contract and keep the remaining argv untouched."""
    rest, found, i = [], [], 0
    while i < len(args):
        arg = args[i]
        if arg == '--':
            rest.extend(args[i:])
            break
        if arg == '--contract':
            if i + 1 >= len(args):
                raise _WrapperError('--contract requires a value: v1 or v2')
            found.append(args[i + 1])
            i += 2
            continue
        if arg.startswith('--contract='):
            found.append(arg[len('--contract='):])
            i += 1
            continue
        rest.append(arg)
        i += 1
    if not found:
        raise _WrapperError('--contract {v1,v2} is required; there is no default and the contract is never inferred from the input')
    if len(found) > 1:
        raise _WrapperError('--contract was given more than once')
    if found[0] not in CONTRACTS:
        raise _WrapperError('unknown --contract value %r; expected v1 or v2' % found[0][:40])
    return found[0], rest


def _exit_value(code):
    if code is None:
        return 0
    return code if isinstance(code, int) else 1


def _run_v1(rest):
    """Chuyển nguyên argv còn lại tới main() của v1, đặt argv/prog như chạy trực tiếp và khôi phục sau gọi."""
    v1 = _load_v1()
    saved = sys.argv
    sys.argv = [str(HERE / 'control_check.py')] + list(rest)
    try:
        return v1.main(list(rest))
    except SystemExit as exc:
        return _exit_value(exc.code)
    finally:
        sys.argv = saved


def _parser():
    ap = argparse.ArgumentParser(prog=PROG, allow_abbrev=False,
                                 description='LAW control record checker v2 candidate (S1 FOUNDATION_ONLY). Never authorizes an effect.')
    ap.add_argument('--contract', required=True, choices=CONTRACTS, help='explicit contract; no default')
    ap.add_argument('--phase', required=True, choices=PHASES)
    ap.add_argument('--format', choices=('json', 'text'), default='json')
    ap.add_argument('bundle', help='bundle or single record JSON file')
    return ap


def _read_bundle(path, limit):
    with open(path, 'rb') as fh:
        return fh.read(limit + 1)


def _run_v2(args):
    try:
        ns = _parser().parse_args(args)
    except SystemExit as exc:
        return _exit_value(exc.code)
    try:
        limit = _load_package().MAX_INPUT_BYTES
        data = _read_bundle(ns.bundle, limit)
    except OSError as exc:
        result = _init_error(ns.phase, 'CLI_EXPLICIT', {'BUNDLE_UNREADABLE'},
                             ['cannot read bundle (%s, errno %s)' % (type(exc).__name__, exc.errno)])
    except Exception as exc:
        result = _init_error(ns.phase, 'CLI_EXPLICIT', {'PACKAGE_UNAVAILABLE'},
                             ['checker v2 package could not be loaded (%s)' % type(exc).__name__])
    else:
        result = _check(data, ns.phase, 'CLI_EXPLICIT')
    text = _format_text(result) if ns.format == 'text' else json.dumps(result, indent=2, ensure_ascii=True)
    sys.stdout.write(text + '\n')
    return exit_code(result)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        contract, rest = _split_contract(args)
    except _WrapperError as exc:
        sys.stderr.write('usage: %s --contract {v1,v2} --phase {dispatch,effect,accept} [--format {json,text}] bundle\n'
                         '%s: error: %s\n' % (PROG, PROG, exc))
        return 2
    if contract == 'v1':
        return _run_v1(rest)
    return _run_v2(args)


if __name__ == '__main__':
    sys.exit(main())
