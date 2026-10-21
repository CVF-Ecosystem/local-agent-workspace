"""LAW-CJ/2 canonical JSON, projection và digest theo `law.cvf.bind/2` (C1) / per contract C1, `law.cvf.bind/2`.

Digest chỉ nhận dạng bytes đã định nghĩa; nó không chứng minh nguồn gốc, quyền hay tính đúng. Phần ngoài miền là UNSUPPORTED, không
chuẩn hóa hộ. Module này không đọc file, không phụ thuộc cây test, và S1 không dùng nó để đánh giá binding của bundle.
A digest only identifies defined bytes; it proves no origin, authority or correctness. Anything outside the domain is UNSUPPORTED and
is never normalized. This module reads no files, depends on nothing in the test tree, and S1 does not use it to evaluate a bundle's bindings.
"""
import copy
import hashlib
import json
import re
import unicodedata

BIND_VERSION = 'law.cvf.bind/2'
MAX_INT = 2 ** 53 - 1
KEY_RE = re.compile(r'^[A-Za-z0-9_.-]{1,64}$')


class Unsupported(Exception):
    """Đầu vào ngoài miền LAW-CJ/2 / input outside the LAW-CJ/2 domain. `reason` là mã cố định, không chép payload."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# ---------------------------------------------------------------- strict parse (vectors / canonical input)
def parse_strict(text):
    """Parse văn bản JSON cho canonicalization: khóa trùng, số thập phân, NaN/Infinity đều là UNSUPPORTED."""
    def pairs(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            raise Unsupported('DUPLICATE_KEY')
        return dict(items)

    def bad_float(_):
        raise Unsupported('NON_INTEGER_NUMBER')

    def bad_const(_):
        raise Unsupported('NON_FINITE_NUMBER')

    return json.loads(text, object_pairs_hook=pairs, parse_float=bad_float, parse_constant=bad_const)


# ---------------------------------------------------------------- LAW-CJ/2
def _string_problem(s):
    """Mã lý do nếu chuỗi ngoài miền, ngược lại None / reason code if the string is outside the domain, else None."""
    if unicodedata.normalize('NFC', s) != s:
        return 'NON_NFC_STRING'
    try:
        s.encode('utf-8')
    except UnicodeEncodeError:
        return 'LONE_SURROGATE'
    return None


def _esc(s):
    problem = _string_problem(s)
    if problem:
        raise Unsupported(problem)
    short = {'"': '\\"', '\\': '\\\\', '\b': '\\b', '\t': '\\t', '\n': '\\n', '\f': '\\f', '\r': '\\r'}
    out = ['"']
    for ch in s:
        if ch in short:
            out.append(short[ch])
        elif ord(ch) < 0x20:
            out.append('\\u%04x' % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    return ''.join(out)


def _enc(v):
    if v is None:
        return 'null'
    if v is True:
        return 'true'
    if v is False:
        return 'false'
    if isinstance(v, int):
        if abs(v) > MAX_INT:
            raise Unsupported('INTEGER_OUT_OF_RANGE')
        return str(v)
    if isinstance(v, float):
        raise Unsupported('NON_INTEGER_NUMBER')
    if isinstance(v, str):
        return _esc(v)
    if isinstance(v, list):
        return '[' + ','.join(_enc(x) for x in v) + ']'
    if isinstance(v, dict):
        for k in v:
            if not isinstance(k, str) or not KEY_RE.fullmatch(k):
                raise Unsupported('KEY_NOT_ALLOWED')
        return '{' + ','.join(_esc(k) + ':' + _enc(v[k]) for k in sorted(v, key=lambda x: x.encode('utf-8'))) + '}'
    raise Unsupported('TYPE_NOT_ALLOWED')


def canonical_text(v):
    return _enc(v)


def canonical_bytes(v):
    return _enc(v).encode('utf-8')


def digest_of(v):
    return 'sha256:' + hashlib.sha256(canonical_bytes(v)).hexdigest()


def bytes_digest(b):
    """Digest của byte file nguyên văn (không chuẩn hóa xuống dòng/BOM/Unicode) / digest of raw file bytes, never normalized."""
    return 'sha256:' + hashlib.sha256(b).hexdigest()


def domain_violations(value):
    """Mọi chỗ trong `value` mà LAW-CJ/2 từ chối, dạng [(path, reason)] đã sắp, không đệ quy.

    Path chỉ gồm chỉ số mảng và khóa hợp lệ; khóa sai mẫu không bao giờ nằm trong path (báo ở object cha) để không chép payload.
    """
    found = []
    stack = [('$', value)]
    while stack:
        path, v = stack.pop()
        if v is None or v is True or v is False:
            continue
        if isinstance(v, int):
            if abs(v) > MAX_INT:
                found.append((path, 'INTEGER_OUT_OF_RANGE'))
        elif isinstance(v, float):
            found.append((path, 'NON_INTEGER_NUMBER'))
        elif isinstance(v, str):
            problem = _string_problem(v)
            if problem:
                found.append((path, problem))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                stack.append(('%s[%d]' % (path, i), x))
        elif isinstance(v, dict):
            for k, x in v.items():
                if isinstance(k, str) and KEY_RE.fullmatch(k):
                    stack.append(('%s.%s' % (path, k), x))
                else:
                    found.append((path, 'KEY_NOT_ALLOWED'))
                    stack.append((path + '.?', x))
        else:
            found.append((path, 'TYPE_NOT_ALLOWED'))
    return sorted(found)


# ---------------------------------------------------------------- projections (contract 4.2 / 4.3)
def sorted_set(items):
    """Sắp theo byte canonical của từng phần tử; trùng là UNSUPPORTED / sorted by canonical bytes; duplicates are UNSUPPORTED."""
    pairs = sorted(((canonical_bytes(i), i) for i in items), key=lambda p: p[0])
    for a, b in zip(pairs, pairs[1:]):
        if a[0] == b[0]:
            raise Unsupported('DUPLICATE_SET_ELEMENT')
    return [i for _, i in pairs]


def ref_proj(r):
    d = {'digest': r['digest'], 'kind': r['kind']}
    if 'revision' in r:
        d['revision'] = r['revision']
    return d


def obj_proj(o):
    return {k: o[k] for k in ('path', 'digest', 'source_id', 'revision', 'scope') if k in o}


def action_proj(a):
    a = copy.deepcopy(a)
    a['targets'] = sorted_set(a['targets'])
    if 'content_use' in a:
        a['content_use'] = sorted_set(a['content_use'])
    if 'payload' in a:
        a['payload'] = obj_proj(a['payload'])
    if 'recipe' in a:
        a['recipe']['acceptance_ref'] = ref_proj(a['recipe']['acceptance_ref'])
    if 'delegation' in a:
        d = a['delegation']
        d.pop('parent_task', None)  # tự tham chiếu task chứa nó: so riêng / self-reference to the containing task: checked separately
        if 'identity_ref' in d['callee']:
            d['callee']['identity_ref'] = ref_proj(d['callee']['identity_ref'])
        ts = d['tool_scope']
        for k in ('tools', 'operations', 'paths'):
            ts[k] = sorted_set(ts[k])
    return a


def intent_part(task):
    return {'bind': BIND_VERSION, 'part': 'intent', 'refs': sorted_set([ref_proj(r) for r in task['intent']['refs']])}


def context_part(task):
    return {'bind': BIND_VERSION, 'part': 'context',
            'context_refs': sorted_set([obj_proj(o) for o in task.get('context_refs', [])])}


def action_part(a):
    return {'bind': BIND_VERSION, 'part': 'action', 'action': action_proj(a)}


def policy_part(policy):
    return {'bind': BIND_VERSION, 'part': 'policy', 'policy': policy}


def task_part(task):
    eff = task['effects']
    e = {'actions': [action_proj(a) for a in eff['actions']], 'on_missing': eff['on_missing']}
    if 'protected_targets' in eff:
        e['protected_targets'] = sorted_set(eff['protected_targets'])
    if 'preservation' in eff:
        e['preservation'] = eff['preservation']
    if 'expected_outputs' in eff:
        e['expected_outputs'] = sorted_set(eff['expected_outputs'])
    p = {
        'bind': BIND_VERSION, 'part': 'task',
        'schema_version': task['schema_version'], 'evaluation_basis': task['evaluation_basis'],
        'work_id': task['work_id'], 'task_id': task['task_id'], 'task_revision': task['task_revision'],
        'intent_digest': digest_of(intent_part(task)),
        'main_interpretation': task['intent']['main_interpretation'],
        'subject': {'actor_id': task['authority']['subject']['actor_id'], 'role': task['authority']['subject']['role']},
        'grant_refs': sorted_set([ref_proj(r) for r in task['authority']['grant_refs']]),
        'inputs': sorted_set([obj_proj(o) for o in task['inputs']]),
        'effects': e, 'acceptance': task['acceptance'], 'envelope': task['envelope'],
    }
    if 'unconfirmed' in task['intent']:
        p['unconfirmed'] = task['intent']['unconfirmed']
    return p


def binding_digests(task, policy):
    """Bốn digest binding tính từ task và policy / the four binding digests computed from a task and the policy."""
    return {
        'intent_digest': digest_of(intent_part(task)),
        'accepted_task_digest': digest_of(task_part(task)),
        'context_digest': digest_of(context_part(task)),
        'policy_digest': digest_of(policy_part(policy)),
    }
