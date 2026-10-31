"""Bounded B1 maintenance reconstruction, 28/10/2026; NOT the 18/10 generator.

Replays the reviewed owner-canon + indent=2/ensure_ascii=False refresh, preserving
each input's EOL/trailing newline. Default is read-only. --apply is a separate,
compare-before write of the complete validated plan. Temporary roots supply DATA
only; executable canon code always comes from this helper's real source tree.
Only P-CTX1/P-CN1 entrypoint pin changes are in this reconstruction's scope.
This helper is not shipped as a product tool and does not grant policy changes.
"""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat


SOURCE = Path(__file__).resolve().parents[3]
POLICY = '.cvf/rules/v3/ROUTING_POLICY.json'
VECTORS = '.cvf/contracts/v3/vectors.json'
EXAMPLES = '.cvf/contracts/v3/examples'
CHECK_TEST = 'tests/test_control_check_v3.py'
DRAFT_TEST = 'tests/test_current_draft.py'
OLD_DIGEST = 'sha256:3fb735bbb88087fcd3c76bd23851609d93e57fc4f8c43194b29d61b0466d6794'
OLD_PINS = {POLICY: '4577f71406997acb', VECTORS: 'eb59221f24200df8',
            'examples': '0857c44d4bc15e9b'}
BASE_VECTOR_SHA = 'eb59221f24200df82b6a1b168cc1405df8a1ccdfb57cb9c8f3d7f3dfec87e0d7'
BASE_EXAMPLES_SHA = '0857c44d4bc15e9b38431cb5800b8289227583cfb146c69fbb4db27d5fa4fc88'
BASE_OWNER_PINS = {
    ('operational_context_protocol', 'entrypoint_sha256'):
        'sha256:65fd87929e8863937e96f084beadee791044b5dc5ca3c048f1137b13ae5e148d',
    ('owner_protocols', 0, 'entrypoint_sha256'):
        'sha256:8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852',
}


class Refused(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, rel):
    """Reject traversal, symlinks and Windows reparse points before reading/writing."""
    root = Path(root).absolute()
    parts = Path(rel).parts
    if Path(rel).is_absolute() or not parts or any(p in ('.', '..') or ':' in p for p in parts):
        raise Refused('unsafe relative path')
    for p in [root, *root.parents]:
        if p.is_symlink() or (p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400):
            raise Refused('linked root')
    p = root
    for part in parts:
        p = p / part
        s = p.lstat()
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 0x400:
            raise Refused('linked target')
    if not p.resolve().is_relative_to(root.resolve()):
        raise Refused('escaped root')
    return p


def load_canon():
    # Fixed trusted source: never import a module from --root.
    path = safe_path(SOURCE, '.cvf/checks/v3/canon.py')
    spec = importlib.util.spec_from_file_location('_b1_trusted_canon', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse(raw):
    def pairs(items):
        if len(dict(items)) != len(items):
            raise Refused('duplicate JSON key')
        return dict(items)
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(Refused('nonfinite JSON')))


def serialize(obj, original):
    if b'\r' in original.replace(b'\r\n', b''):
        raise Refused('unsupported EOL')
    eol = b'\r\n' if b'\r\n' in original else b'\n'
    if eol == b'\r\n' and b'\n' in original.replace(b'\r\n', b''):
        raise Refused('mixed EOL')
    suffix = eol if original.endswith(eol) else b''
    return json.dumps(obj, indent=2, ensure_ascii=False).encode('utf-8').replace(b'\n', eol) + suffix


def leaf_paths(obj, predicate, path=()):
    if isinstance(obj, dict):
        return [p for k, v in obj.items() for p in leaf_paths(v, predicate, path + (k,))]
    if isinstance(obj, list):
        return [p for k, v in enumerate(obj) for p in leaf_paths(v, predicate, path + (k,))]
    return [path] if predicate(path, obj) else []


def get(obj, path):
    for key in path:
        obj = obj[key]
    return obj


def put(obj, path, value):
    for key in path[:-1]:
        obj = obj[key]
    obj[path[-1]] = value


def same_order_shape(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return list(a) == list(b) and all(same_order_shape(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same_order_shape(x, y) for x, y in zip(a, b))
    return True


def normalized_baseline(raw):
    """Restore only the known digest field areas for the 28/10 baseline hash.

    Allows a previously applied replay to remain a no-op without silently
    adopting unrelated edits from the trusted source fixture tree.
    """
    obj = parse(raw)
    if serialize(obj, raw) != raw:
        raise Refused('trusted fixture baseline changed serialization')
    paths = leaf_paths(obj, lambda p, v: p == ('policy_digest', 'digest') or p[-1] == 'policy_digest')
    for path in paths:
        put(obj, path, OLD_DIGEST)
    return obj, serialize(obj, raw)


def example_names(root):
    directory = safe_path(root, EXAMPLES)
    names = sorted(p.name for p in directory.iterdir() if p.name.startswith('ex') and p.name.endswith('.json'))
    if len(names) != 22:
        raise Refused('expected exactly 22 lower-case ex*.json examples')
    return names


def pin_edits(raw, dictionary, replacements):
    """AST selects exact dictionary keys; byte offsets preserve all surrounding WIP."""
    try:
        tree = ast.parse(raw.decode('utf-8'))
    except (SyntaxError, UnicodeError) as exc:
        raise Refused('unparseable pin module') from exc
    nodes = [n.value for n in tree.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == dictionary for t in n.targets)]
    if len(nodes) != 1 or not isinstance(nodes[0], ast.Dict):
        raise Refused('pin dictionary missing/ambiguous')
    edits = []
    lines = raw.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    keys = [ast.literal_eval(k) for k in nodes[0].keys]
    if len(set(keys)) != len(keys):
        raise Refused('duplicate pin key')
    for key, (old, new) in replacements.items():
        if keys.count(key) != 1:
            raise Refused('pin key missing/ambiguous')
        node = nodes[0].values[keys.index(key)]
        if not isinstance(node, ast.Constant) or node.value not in (old, new):
            raise Refused('stale pin')
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        literal = raw[start:end]
        if literal not in (b"'" + node.value.encode() + b"'", b'"' + node.value.encode() + b'"'):
            raise Refused('unexpected pin literal')
        edits.append((start, end, literal[:1] + new.encode() + literal[-1:]))
    result = raw
    for start, end, value in sorted(edits, reverse=True):
        result = result[:start] + value + result[end:]
    return result


def plan(root):
    root = Path(root).absolute()
    canon = load_canon()
    names = example_names(SOURCE)
    if example_names(root) != names:
        raise Refused('unexpected example names')
    baseline_joined = '\n'.join(n + ':' + sha(normalized_baseline(
        safe_path(SOURCE, EXAMPLES + '/' + n).read_bytes())[1]) for n in names)
    if (sha(normalized_baseline(safe_path(SOURCE, VECTORS).read_bytes())[1]) != BASE_VECTOR_SHA
            or sha(baseline_joined.encode('utf-8')) != BASE_EXAMPLES_SHA):
        raise Refused('trusted fixture baseline changed; re-review reconstruction')
    before = {}

    def read(rel):
        raw = safe_path(root, rel).read_bytes()
        before[rel] = raw
        return raw

    policy_raw = read(POLICY)
    policy = parse(policy_raw)
    if serialize(policy, policy_raw) != policy_raw:
        raise Refused('unexpected policy serialization/EOL')
    baseline_policy = parse(safe_path(SOURCE, POLICY).read_bytes())
    for path, pin in BASE_OWNER_PINS.items():
        put(baseline_policy, path, pin)
    if not same_order_shape(policy, baseline_policy):
        raise Refused('unexpected policy shape/key order')
    restored = copy.deepcopy(policy)
    for path in BASE_OWNER_PINS:
        if not re.fullmatch('sha256:[0-9a-f]{64}', get(policy, path)):
            raise Refused('invalid owner pin')
        put(restored, path, get(baseline_policy, path))
    if restored != baseline_policy:
        raise Refused('policy change outside owner-pin scope')
    digest = canon.digest_of(canon.policy_part(policy))
    if canon.digest_of(canon.policy_part(baseline_policy)) != OLD_DIGEST:
        raise Refused('trusted baseline changed; re-review reconstruction')
    after = {}
    allowed_count = 0
    for rel in [VECTORS] + [EXAMPLES + '/' + n for n in names]:
        raw = read(rel)
        source_raw = safe_path(SOURCE, rel).read_bytes()
        baseline, baseline_raw = normalized_baseline(source_raw)
        obj = parse(raw)
        paths = leaf_paths(baseline, lambda p, v: v == OLD_DIGEST and
                           (p == ('policy_digest', 'digest') or p[-1] == 'policy_digest'))
        allowed_count += len(paths)
        if not paths or not same_order_shape(obj, baseline):
            raise Refused('unexpected fixture shape/key order: ' + rel)
        inverse = copy.deepcopy(obj)
        for path in paths:
            if get(obj, path) not in (OLD_DIGEST, digest):
                raise Refused('stale fixture digest: ' + rel)
            put(inverse, path, OLD_DIGEST)
        if inverse != baseline or serialize(obj, raw) != raw:
            raise Refused('unexpected fixture content/serialization: ' + rel)
        # Exact reverse bytes against trusted fixture, with the input EOL convention.
        if serialize(inverse, raw) != serialize(baseline, raw):
            raise Refused('inverse bytes mismatch')
        if serialize(baseline, baseline_raw) != baseline_raw:
            raise Refused('trusted serialization changed')
        for path in paths:
            put(obj, path, digest)
        proposed = serialize(obj, raw)
        reverse = parse(proposed)
        for path in paths:
            put(reverse, path, get(parse(raw), path))
        if serialize(reverse, proposed) != raw:
            raise Refused('raw reverse proof failed')
        after[rel] = proposed
    if allowed_count != 43:
        raise Refused('expected exactly 43 authorized digest leaves')
    joined = '\n'.join(n + ':' + sha(after[EXAMPLES + '/' + n]) for n in names).encode('utf-8')
    pins = {POLICY: sha(policy_raw)[:16], VECTORS: sha(after[VECTORS])[:16], 'examples': sha(joined)[:16]}
    check_raw = read(CHECK_TEST)
    check_new = pin_edits(check_raw, 'FILE_PINS', {
        tuple(rel.split('/')[1:]): (OLD_PINS[rel], pins[rel]) for rel in (POLICY, VECTORS)})
    # This separate tuple assignment is bounded to its complete named line.
    example_assignments = [n for n in ast.parse(check_new.decode('utf-8')).body
                           if isinstance(n, ast.Assign) and any(
                               isinstance(t, ast.Name) and t.id == 'V3_EXAMPLES_PIN' for t in n.targets)]
    if len(example_assignments) != 1:
        raise Refused('ambiguous examples pin assignment')
    matches = list(re.finditer(rb"(?m)^V3_EXAMPLES_PIN = \((['\"])([0-9a-f]{16})\1, 22\)([^\r\n]*)\r?$", check_new))
    if len(matches) != 1 or matches[0][2].decode() not in (OLD_PINS['examples'], pins['examples']):
        raise Refused('stale/ambiguous examples pin')
    m = matches[0]
    check_new = check_new[:m.start(2)] + pins['examples'].encode() + check_new[m.end(2):]
    after[CHECK_TEST] = check_new
    after[DRAFT_TEST] = pin_edits(read(DRAFT_TEST), 'OWNER_PINS', {
        rel: (OLD_PINS[rel], pins[rel]) for rel in (POLICY, VECTORS)})
    return {'root': root, 'before': before, 'after': after, 'digest': digest,
            'allowed_leaves': allowed_count, 'pins': pins,
            'changed': sorted(k for k in after if before[k] != after[k])}


def apply(result):
    # Preflight ALL inputs and path safety before the first write. Not a host
    # transaction/lock: concurrent mutation after this check remains unsupported.
    if example_names(result['root']) != example_names(SOURCE):
        raise Refused('examples inventory changed')
    for rel, raw in result['before'].items():
        if safe_path(result['root'], rel).read_bytes() != raw:
            raise Refused('compare-before failed: ' + rel)
    for rel in result['changed']:
        safe_path(result['root'], rel).write_bytes(result['after'][rel])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=SOURCE)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = plan(args.root)
        if args.apply:
            apply(result)
        print(json.dumps({k: result[k] for k in ('digest', 'allowed_leaves', 'pins', 'changed')}, ensure_ascii=False))
        return 0
    except (Refused, OSError, ValueError, TypeError, KeyError) as exc:
        print('REFUSED: ' + str(exc))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
