#!/usr/bin/env python3
"""Track package-managed .new files without reading or storing their contents.

diff() compares a managed file with its .new copy on request, read-only; nothing is stored or merged.
"""
import difflib, hashlib, io, json, os

STATE_REL = '.agent/MERGE_STATUS.json'
ALLOWED_STATES = {'unseen', 'reviewing', 'ready'}
DIFF_MAX_BYTES = 256 * 1024  # mỗi file; file lớn hơn không so sánh trong giao diện / per file; larger files are not compared
DIFF_MAX_ROWS = 4000         # số dòng kết quả tối đa / maximum result rows
DIFF_CONTEXT = 3             # dòng ngữ cảnh quanh mỗi thay đổi / context lines around each change

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

def _pair(root, pending_rel):
    """Chuẩn hóa và kiểm cặp (bản hiện hành, bản .new) của file package quản lý / Normalise and check a managed pair."""
    rel = (pending_rel or '').replace('\\', '/').lstrip('/')
    current_rel = rel[:-4] if rel.endswith('.new') else ''
    if not current_rel or current_rel not in managed_paths(root):
        raise ValueError('Not a package-managed merge file: ' + rel)
    return rel, current_rel

def _inside(root, rel):
    """Đường dẫn tuyệt đối nằm trong root, không chứa '..' / Absolute path that stays inside root."""
    parts = rel.split('/')
    path = os.path.abspath(os.path.join(root, *parts))
    if '..' in parts or not path.startswith(os.path.abspath(root) + os.sep):
        raise ValueError('Path outside the project: ' + rel)
    return path

def set_state(root, pending_rel, state):
    if state not in ALLOWED_STATES:
        raise ValueError('Invalid merge state: ' + str(state))
    pending_rel, _ = _pair(root, pending_rel)
    pending = _inside(root, pending_rel)
    if not os.path.isfile(pending):
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

def _text_lines(data):
    """Dòng UTF-8, hoặc None nếu là file nhị phân / UTF-8 lines, or None for binary data."""
    if b'\x00' in data[:8192]:
        return None
    try:
        return data.decode('utf-8').splitlines()
    except UnicodeDecodeError:
        return None

def _read_bytes(path):
    with open(path, 'rb') as src:
        return src.read()

def diff(root, pending_rel, max_bytes=DIFF_MAX_BYTES):
    """So sánh chỉ đọc giữa bản hiện hành và bản .new theo hunk có số dòng; không lưu, không ghi.
    Read-only line diff between the current file and its .new copy, as hunks with line numbers; nothing is stored.
    Sizes are checked before reading: a file larger than max_bytes is flagged too_large. A missing current file is
    flagged current_missing and every line of the new copy counts as added. Identical files are flagged identical
    only when both are within max_bytes.
    """
    pending_rel, current_rel = _pair(root, pending_rel)
    pending, current = _inside(root, pending_rel), _inside(root, current_rel)
    if not os.path.isfile(pending):
        raise ValueError('Merge file does not exist: ' + pending_rel)
    exists = os.path.isfile(current)
    res = {'path': current_rel, 'pending': pending_rel, 'current_missing': not exists, 'identical': False,
           'binary': False, 'too_large': False, 'truncated': False, 'added': 0, 'removed': 0, 'hunks': [],
           'max_bytes': max_bytes, 'max_rows': DIFF_MAX_ROWS}
    if max(os.path.getsize(pending), os.path.getsize(current) if exists else 0) > max_bytes:
        res['too_large'] = True
        return res
    new_data = _read_bytes(pending)
    old_data = _read_bytes(current) if exists else b''
    if exists and old_data == new_data:
        res['identical'] = True
        return res
    new_lines, old_lines = _text_lines(new_data), _text_lines(old_data)
    if new_lines is None or old_lines is None:
        res['binary'] = True
        return res
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ('replace', 'delete'):
            res['removed'] += i2 - i1
        if tag in ('replace', 'insert'):
            res['added'] += j2 - j1
    rows = 0
    for group in matcher.get_grouped_opcodes(DIFF_CONTEXT):
        old_count = group[-1][2] - group[0][1]
        new_count = group[-1][4] - group[0][3]
        hunk = {'old_start': group[0][1] + 1 if old_count else group[0][1], 'old_count': old_count,
                'new_start': group[0][3] + 1 if new_count else group[0][3], 'new_count': new_count, 'lines': []}
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                entries = [('context', i + 1, j1 + (i - i1) + 1, old_lines[i]) for i in range(i1, i2)]
            else:
                entries = []
                if tag in ('replace', 'delete'):
                    entries += [('removed', i + 1, None, old_lines[i]) for i in range(i1, i2)]
                if tag in ('replace', 'insert'):
                    entries += [('added', None, j + 1, new_lines[j]) for j in range(j1, j2)]
            for op, old_no, new_no, text in entries:
                if rows >= DIFF_MAX_ROWS:
                    res['truncated'] = True
                    break
                hunk['lines'].append({'op': op, 'old': old_no, 'new': new_no, 'text': text})
                rows += 1
            if res['truncated']:
                break
        if hunk['lines']:
            res['hunks'].append(hunk)
        if res['truncated']:
            break
    return res
