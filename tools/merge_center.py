#!/usr/bin/env python3
"""Track package-managed .new files without reading or storing their contents."""
import hashlib, io, json, os

STATE_REL = '.agent/MERGE_STATUS.json'
ALLOWED_STATES = {'unseen', 'reviewing', 'ready'}

def _read_json(path):
    try:
        with io.open(path, encoding='utf-8') as src:
            value = json.load(src)
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}

def _manifest_paths(root):
    out = set()
    try:
        with io.open(os.path.join(root, 'MANIFEST.sha256'), encoding='utf-8') as src:
            for line in src:
                if '  ' in line:
                    out.add(line.rstrip('\r\n').split('  ', 1)[1].replace('\\', '/'))
    except OSError:
        pass
    return out

def _pack_paths(root):
    out = set()
    base = os.path.join(root, 'skills', 'local', 'packs')
    if not os.path.isdir(base):
        return out
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith('.')]
        for name in files:
            rel = os.path.relpath(os.path.join(d, name), root).replace(os.sep, '/')
            out.add(rel[:-4] if rel.endswith('.new') else rel)
    return out

def managed_paths(root):
    return _manifest_paths(root) | _pack_paths(root)

def _sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def scan(root):
    root = os.path.abspath(root)
    saved = _read_json(os.path.join(root, *STATE_REL.split('/'))).get('items', {})
    items = []
    for rel in sorted(managed_paths(root)):
        pending_rel = rel + '.new'
        pending = os.path.join(root, *pending_rel.split('/'))
        if not os.path.isfile(pending):
            continue
        current = os.path.join(root, *rel.split('/'))
        fingerprint = _sha(pending)
        old = saved.get(pending_rel, {}) if isinstance(saved.get(pending_rel), dict) else {}
        state = old.get('state') if old.get('fingerprint') == fingerprint else 'unseen'
        if state not in ALLOWED_STATES:
            state = 'unseen'
        origin = 'domain_pack' if rel.startswith('skills/local/packs/') else 'package'
        items.append({'path': rel, 'pending': pending_rel, 'current_exists': os.path.isfile(current),
                      'state': state, 'origin': origin, 'fingerprint': fingerprint})
    return items

def set_state(root, pending_rel, state):
    if state not in ALLOWED_STATES:
        raise ValueError('Invalid merge state: ' + str(state))
    pending_rel = (pending_rel or '').replace('\\', '/').lstrip('/')
    current_rel = pending_rel[:-4] if pending_rel.endswith('.new') else ''
    if not current_rel or current_rel not in managed_paths(root):
        raise ValueError('Not a package-managed merge file: ' + pending_rel)
    pending = os.path.abspath(os.path.join(root, *pending_rel.split('/')))
    root_abs = os.path.abspath(root)
    if not pending.startswith(root_abs + os.sep) or not os.path.isfile(pending):
        raise ValueError('Merge file does not exist: ' + pending_rel)
    state_path = os.path.join(root, *STATE_REL.split('/'))
    data = _read_json(state_path)
    items = data.get('items') if isinstance(data.get('items'), dict) else {}
    items[pending_rel] = {'state': state, 'fingerprint': _sha(pending)}
    data = {'schema': 'local-agent-workspace/merge-state-v1', 'items': items}
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with io.open(state_path, 'w', encoding='utf-8', newline='') as dst:
        json.dump(data, dst, ensure_ascii=False, indent=2, sort_keys=True)
        dst.write('\n')
    return {'ok': True, 'path': pending_rel, 'state': state}
