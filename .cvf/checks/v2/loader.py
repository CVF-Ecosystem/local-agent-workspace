"""Loader strict của checker v2 candidate (G-02-C2/S1) / strict loader of the v2 candidate checker.

Chỉ đọc bundle (bytes do entry đưa vào) và hai owner cố định cạnh package. Không observer, không thư mục gốc tùy chọn, không fetch locator,
không remote $ref, không exec. Tên owner đúng không chống sửa: chỉ ghi hash byte đã đọc (`owner_protection = NOT_PROVEN`).
Reads only the bundle bytes handed in by the entry and the two fixed owners next to the package. No locator fetch, no remote $ref.

Thứ tự kiểm bundle / bundle order: parse strict → version → basis → literal của binding → schema Draft 2020-12 → miền canonical.
Sai literal version/basis/binding và ngoài miền canonical = UNSUPPORTED (từ chối, không diễn giải); sai cấu trúc còn lại = DENY.
"""
import hashlib
import importlib
import importlib.metadata
import json
import re
from pathlib import Path

from . import (BIND_VERSION, EVALUATION_BASIS, MAX_INPUT_BYTES, MIN_JSONSCHEMA, POLICY_STATUS, POLICY_VERSION, SCHEMA_ID,
               SCHEMA_VERSION, V1_SCHEMA_VERSION)
from . import canon

SCHEMA_REL = ('contracts', 'v2', 'control.schema.json')
POLICY_REL = ('rules', 'v2', 'ROUTING_POLICY.json')
_ABSENT = object()
_SAFE_KEY = re.compile(r'^[A-Za-z0-9_.-]{1,40}$')
_OWNER_CACHE = {}


class InputError(Exception):
    """Input hỏng (không phải JSON, khóa trùng, nonfinite...). Thông điệp cố định, không chép payload."""


class InitFailure(Exception):
    """Lỗi khởi tạo (dependency, owner) / initialization failure (dependency, owner). Entry đổi thành init_error và exit 2."""

    def __init__(self, reasons, details, schema_sha256=None, policy_sha256=None):
        super().__init__(','.join(sorted(reasons)))
        self.reasons = set(reasons)
        self.details = list(details)
        self.schema_sha256 = schema_sha256
        self.policy_sha256 = policy_sha256


class Owners(object):
    def __init__(self, schema, policy, validator, schema_sha256, policy_sha256, notes, policy_bytes=b''):
        self.schema = schema
        self.policy = policy
        self.validator = validator
        self.schema_sha256 = schema_sha256
        self.policy_sha256 = policy_sha256
        self.notes = list(notes)
        # bytes bất biến đúng như đã hash `policy_sha256`; S2 parse bản riêng từ đây, không dùng dict `policy` dùng chung từ cache
        self.policy_bytes = bytes(policy_bytes)


class Outcome(object):
    """Kết quả kiểm cấu trúc bundle của S1; entry dựng output từ đây / S1 structure outcome the entry turns into output."""

    def __init__(self):
        self.disposition = 'BLOCKED'
        self.reasons = set()
        self.details = []
        self.evaluation_basis = None
        self.record_structure_checked = False

    def refuse(self, disposition, reasons, details):
        self.disposition = disposition
        self.reasons.update(reasons)
        self.details.extend(details)
        return self


# ---------------------------------------------------------------- dependency
def _import_jsonschema():
    return importlib.import_module('jsonschema')


def _jsonschema_version():
    try:
        text = importlib.metadata.version('jsonschema')
    except Exception:
        return None
    match = re.match(r'^(\d+)\.(\d+)', text)
    return (int(match.group(1)), int(match.group(2))) if match else None


def default_cvf_dir():
    return Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------- strict parse
def _no_dupes(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise InputError('duplicate JSON key (name withheld)')
        out[k] = v
    return out


def _no_constant(_name):
    raise InputError('non-finite JSON constant')


def parse_json_bytes(data):
    """Parse strict: UTF-8 (BOM đầu được bỏ như v1), khóa trùng và NaN/Infinity bị từ chối, top-level phải là object, tối đa 8 MiB."""
    if len(data) > MAX_INPUT_BYTES:
        raise InputError('input larger than %d bytes' % MAX_INPUT_BYTES)
    try:
        text = data.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise InputError('not valid UTF-8 (byte offset %d)' % exc.start)
    try:
        obj = json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_no_constant)
    except InputError:
        raise
    except RecursionError:
        raise InputError('JSON nesting too deep')
    except ValueError as exc:
        raise InputError('not valid JSON (line %s column %s)' % (getattr(exc, 'lineno', '?'), getattr(exc, 'colno', '?')))
    if not isinstance(obj, dict):
        raise InputError('top-level JSON value must be an object')
    return obj


def _read_owner(path, label):
    try:
        with open(str(path), 'rb') as fh:
            data = fh.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise InitFailure({'OWNER_UNREADABLE'}, ['cannot read %s owner (%s)' % (label, type(exc).__name__)])
    return data


def _has_remote_ref(node):
    stack = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for keyword in ('$ref', '$dynamicRef', '$recursiveRef'):
                ref = cur.get(keyword)
                if isinstance(ref, str) and not ref.startswith('#'):
                    return True
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return False


# ---------------------------------------------------------------- owners
def load_owners(cvf_dir=None):
    """Nạp và validate hai owner cố định; mọi lỗi là InitFailure, không fallback / load and validate the fixed owners."""
    try:
        jsonschema = _import_jsonschema()
        from referencing import Registry
        from referencing.exceptions import NoSuchResource
    except Exception:
        raise InitFailure({'DEPENDENCY_MISSING'}, ['jsonschema (Draft 2020-12) is required and was not importable'])
    version = _jsonschema_version()
    if version is None or version < MIN_JSONSCHEMA or not hasattr(jsonschema, 'Draft202012Validator'):
        raise InitFailure({'DEPENDENCY_MISSING'}, ['jsonschema >= %d.%d with Draft 2020-12 support is required' % MIN_JSONSCHEMA])

    root = Path(cvf_dir if cvf_dir is not None else default_cvf_dir())
    schema_bytes = _read_owner(root.joinpath(*SCHEMA_REL), 'schema')
    try:
        policy_bytes = _read_owner(root.joinpath(*POLICY_REL), 'policy')
    except InitFailure as exc:
        exc.schema_sha256 = hashlib.sha256(schema_bytes).hexdigest()
        raise
    schema_sha = hashlib.sha256(schema_bytes).hexdigest()
    policy_sha = hashlib.sha256(policy_bytes).hexdigest()

    def fail(reasons, details):
        return InitFailure(reasons, details, schema_sha, policy_sha)

    cached = _OWNER_CACHE.get((schema_sha, policy_sha, version))
    if cached is not None:
        return cached
    try:
        schema = parse_json_bytes(schema_bytes)
    except InputError as exc:
        raise fail({'OWNER_INVALID'}, ['schema owner: %s' % exc])
    try:
        policy = parse_json_bytes(policy_bytes)
    except InputError as exc:
        raise fail({'OWNER_INVALID'}, ['policy owner: %s' % exc])

    literal = set()
    details = []
    if schema.get('$id') != SCHEMA_ID:
        literal.add('SCHEMA_VERSION_UNKNOWN')
        details.append('schema owner $id is not %s' % SCHEMA_ID)
    if policy.get('policy_version') != POLICY_VERSION or policy.get('schema_version') != SCHEMA_VERSION:
        literal.add('POLICY_VERSION_UNKNOWN')
        details.append('policy owner version literals are not %s / %s' % (POLICY_VERSION, SCHEMA_VERSION))
    if literal:
        raise fail(literal, details)
    if policy.get('status') != POLICY_STATUS or policy.get('evaluation_basis') != EVALUATION_BASIS:
        raise fail({'OWNER_INVALID'}, ['policy owner status/basis is not %s/%s' % (POLICY_STATUS, EVALUATION_BASIS)])
    if _has_remote_ref(schema):
        raise fail({'OWNER_INVALID'}, ['schema owner has a non-local $ref; remote references are refused'])

    def deny_retrieval(uri):
        raise NoSuchResource(ref=uri)

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker(), registry=Registry(retrieve=deny_retrieval))
        policy_errors = list(validator.iter_errors(policy))
    except Exception as exc:
        raise fail({'OWNER_INVALID'}, ['schema owner is not usable as a Draft 2020-12 schema (%s)' % type(exc).__name__])
    if policy_errors:
        raise fail({'OWNER_INVALID'}, ['policy owner does not validate against the schema owner'])
    notes = []
    if 'date-time' not in jsonschema.FormatChecker.checkers:
        notes.append('date-time format not checked (no format library installed)')
    owners = Owners(schema, policy, validator, schema_sha, policy_sha, notes, policy_bytes)
    _OWNER_CACHE[(schema_sha, policy_sha, version)] = owners
    return owners


# ---------------------------------------------------------------- bundle
def _vkey(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True)


def _label(index, rec):
    if index is None:
        return 'top-level'
    return 'records[%d]' % index


def _carriers(bundle):
    out = [(_label(None, bundle), bundle)]
    records = bundle.get('records')
    if bundle.get('record_type') == 'bundle' and isinstance(records, list):
        for i, rec in enumerate(records):
            if isinstance(rec, dict):
                out.append((_label(i, rec), rec))
    return out


def _check_versions(carriers, out):
    present = {}
    missing = []
    for label, rec in carriers:
        value = rec.get('schema_version', _ABSENT)
        if value is _ABSENT:
            missing.append(label)
        else:
            present.setdefault(_vkey(value), (value, []))[1].append(label)
    reasons = set()
    if missing:
        reasons.add('VERSION_MISSING')
        out.details.append('schema_version missing in: %s' % ', '.join(missing[:10]))
    unknown = [k for k, (v, _) in present.items() if v != SCHEMA_VERSION]
    if unknown:
        reasons.add('SCHEMA_VERSION_UNKNOWN')
        for k in unknown:
            labels = present[k][1]
            out.details.append('unsupported schema_version in: %s' % ', '.join(labels[:10]))
    if len(present) > 1:
        reasons.add('VERSION_MIXED')
    if reasons:
        v1_only = set(present) == set(unknown) and all(present[k][0] == V1_SCHEMA_VERSION for k in unknown) and not missing
        if v1_only:
            out.details.append('input is %s: choose --contract v1 explicitly; v2 neither tries v1 nor reinterprets it'
                               % V1_SCHEMA_VERSION)
        out.refuse('UNSUPPORTED', reasons, [])
        return False
    return True


def _check_basis(carriers, out):
    present = {}
    missing = []
    mismatch = []
    for label, rec in carriers:
        own = rec.get('evaluation_basis', _ABSENT)
        if own is _ABSENT:
            missing.append(label)
        else:
            present.setdefault(_vkey(own), own)
        binding = rec.get('binding')
        if isinstance(binding, dict):
            bound = binding.get('evaluation_basis', _ABSENT)
            if bound is _ABSENT:
                missing.append(label + ' binding')
            else:
                present.setdefault(_vkey(bound), bound)
                if own is not _ABSENT and _vkey(own) != _vkey(bound):
                    mismatch.append(label)
    reasons = set()
    if missing:
        reasons.add('BASIS_MISSING')
        out.details.append('evaluation_basis missing in: %s' % ', '.join(missing[:10]))
    if any(v != EVALUATION_BASIS for v in present.values()):
        reasons.add('BASIS_UNKNOWN')
        out.details.append('evaluation_basis other than %s is not supported' % EVALUATION_BASIS)
    if len(present) > 1:
        reasons.add('BASIS_MIXED')
    if mismatch:
        reasons.add('BASIS_MISMATCH')
        out.details.append('binding basis differs from its record in: %s' % ', '.join(mismatch[:10]))
    if reasons:
        out.refuse('UNSUPPORTED', reasons, [])
        return False
    return True


def _check_binding_literals(carriers, out):
    bad = []
    for label, rec in carriers:
        binding = rec.get('binding')
        if not isinstance(binding, dict):
            continue
        if binding.get('bind_version') != BIND_VERSION or binding.get('policy_version') != POLICY_VERSION \
                or 'policy_digest' not in binding:
            bad.append(label)
    if bad:
        out.refuse('UNSUPPORTED', {'BINDING_VERSION_UNKNOWN'},
                   ['binding is not %s / %s with a policy_digest in: %s (a v1 binding is never reused)'
                    % (BIND_VERSION, POLICY_VERSION, ', '.join(bad[:10]))])
        return False
    return True


def _safe_path(parts):
    out = []
    for p in parts:
        if isinstance(p, int):
            out.append('[%d]' % p)
        elif isinstance(p, str) and _SAFE_KEY.fullmatch(p):
            out.append('.' + p)
        else:
            out.append('.?')
    return ''.join(out) or '<root>'


def parse_and_preflight(data, owners):
    """Strict parse → version → basis → literal binding, đúng thứ tự/lý do/details của S1 / S1 order, reasons and details.

    Trả (bundle, Outcome); bundle là None khi bị từ chối. Outcome ở đây chưa bao giờ đặt record_structure_checked=True;
    `evaluation_basis` được đặt khi basis đã hợp lệ. `owners` được giữ trong chữ ký cho đồng bộ với `validate_structure`.
    """
    out = Outcome()
    try:
        bundle = parse_json_bytes(data)
    except InputError as exc:
        out.refuse('DENY', {'INPUT_MALFORMED'}, [str(exc)])
        return None, out
    carriers = _carriers(bundle)
    if not _check_versions(carriers, out):
        return None, out
    if not _check_basis(carriers, out):
        return None, out
    out.evaluation_basis = EVALUATION_BASIS
    if not _check_binding_literals(carriers, out):
        return None, out
    return bundle, out


def validate_structure(bundle, owners):
    """Schema Draft 2020-12 + loại `routing_policy`: (ok, reasons, details). `details` luôn bắt đầu bằng ghi chú của owners.

    ok=False tương ứng DENY. Schema-valid KHÔNG có nghĩa canonical-supported; screen miền canonical là việc riêng của S1.
    """
    details = list(owners.notes)
    try:
        errors = sorted(owners.validator.iter_errors(bundle), key=lambda e: [str(p) for p in e.absolute_path])
    except RecursionError:
        return False, ('INPUT_MALFORMED',), tuple(details + ['JSON nesting too deep for schema validation'])
    if errors:
        shown = ['%s: violates %s' % (_safe_path(list(e.absolute_path)), e.validator) for e in errors[:10]]
        if len(errors) > 10:
            shown.append('... %d more schema violations' % (len(errors) - 10))
        return False, ('SCHEMA_INVALID',), tuple(details + shown)
    if any(rec.get('record_type') == 'routing_policy' for _, rec in _carriers(bundle)):
        return False, ('SCHEMA_INVALID',), tuple(
            details + ['a routing_policy is not a checkable record; the canonical policy is fixed'])
    return True, (), tuple(details)


def inspect_bundle(data, owners):
    """Kiểm cấu trúc bundle theo thứ tự đã nêu; S1 dừng ở đây và entry báo BLOCKED nếu cấu trúc hợp lệ."""
    bundle, out = parse_and_preflight(data, owners)
    if bundle is None:
        return out
    ok, reasons, details = validate_structure(bundle, owners)
    if not ok:
        return out.refuse('DENY', set(reasons), list(details))
    out.details.extend(details)

    violations = canon.domain_violations(bundle)
    if violations:
        counts = {}
        for _path, reason in violations:
            counts[reason] = counts.get(reason, 0) + 1
        return out.refuse('UNSUPPORTED', {'UNSUPPORTED_BINDING_PART'},
                          ['outside the LAW-CJ/2 domain, never normalized: %s'
                           % ', '.join('%s x%d' % (r, n) for r, n in sorted(counts.items()))])
    out.record_structure_checked = True
    out.refuse('BLOCKED', {'CANDIDATE_EVALUATION_NOT_IMPLEMENTED'}, [])
    return out
