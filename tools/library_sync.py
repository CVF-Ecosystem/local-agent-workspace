"""Bounded source-catalog sync for library.py. No content extraction or legal verification."""
import contextlib
import datetime
import hashlib
import io
import json
import os
import re
import stat
import zipfile

import library
import transaction


META = ('LAW revision', 'LAW SHA-256', 'LAW observed', 'LAW file state')
ID_PATTERN = re.compile(r'^SRC-(\d+)$')
# Dòng của PROJECT.md do người dùng điền; công cụ chỉ đọc, không bao giờ ghi.
# The PROJECT.md line the user fills in; the tool only reads it and never writes it.
SCOPE_LABELS = ('Ngoại lệ thư mục nguồn cũ', 'Existing source-folder exceptions')
NO_SCOPE = frozenset(('khong co', 'none', 'n/a', '-'))
# Vùng của gói hoặc kết quả: không dùng làm nguồn cũ. / Package or output areas: never a source scope.
RESERVED_TOP = frozenset(('.agent', '.git', '.github', 'archive', 'assets', 'dist', 'docs', 'en', 'examples',
                          'feedback', 'output', 'packs', 'references', 'release_templates', 'roadmap', 'roles',
                          'skills', 'tests', 'tools', 'working'))
OUT_OF_SCOPE = 'OUT_OF_SCOPE'


class SyncError(Exception):
    pass


class IntakeWriteError(SyncError):
    """Preserve known effects (or unknown effects) when a multi-file intake is interrupted."""
    def __init__(self, message, tx):
        SyncError.__init__(self, message)
        self.files = [{'path': op['path'], 'action': op['action']} for op in tx.journal['ops'] if op['state'] == 'done']
        self.changes = True if self.files else (None if tx.journal['status'] in ('committing', 'committed') else False)
        self.transaction = tx.txid if os.path.isfile(os.path.join(tx.dir, 'journal.json')) else None


class PreviewMismatch(SyncError):
    """expected_preview thiếu, sai cấu trúc hoặc không còn khớp plan tính lại dưới khóa; reason: invalid | snapshot | sources | scopes.
    expected_preview is malformed or no longer matches the plan recomputed under the lock."""

    def __init__(self, message, reason):
        SyncError.__init__(self, message)
        self.reason = reason


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def contained(path, root):
    try:
        return os.path.commonpath((os.path.realpath(path), os.path.realpath(root))) == os.path.realpath(root)
    except ValueError:  # different Windows drives
        return False


link_free = transaction.link_free  # một định nghĩa dùng chung với giao dịch / one definition shared with the transaction layer


def guard_targets(root):
    """Refuse, before reading the workbook or taking the lock, when references or its index is or passes through a link.

    A link there makes both paths resolve to the same outside place, so a containment check of one against the other passes.
    Checked against the project root instead. / So sánh với thư mục gốc project, không so ref với index.
    """
    ref = os.path.join(root, 'references')
    index = os.path.join(ref, '_INDEX.xlsx')
    for path in (ref, index):
        if not link_free(path, root):
            raise SyncError('References or its index is, or passes through, a link; stopped before any read or write / '
                            'references hoặc sổ là hoặc đi qua liên kết; dừng trước khi đọc hoặc ghi: '
                            + os.path.relpath(path, root).replace(os.sep, '/'))
    return ref, index


def scope_text(root):
    try:
        with io.open(os.path.join(root, 'PROJECT.md'), encoding='utf-8-sig') as f:
            text = f.read()
    except OSError:
        return ''
    pattern = re.compile(r'^\s*[-*]\s*(?:%s)\s*:\s*(.*)$' % '|'.join(re.escape(x) for x in SCOPE_LABELS))
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return ''


def scopes(root):
    """Old-source folders the user chose in PROJECT.md. Empty when the field is blank, a placeholder or "none"."""
    value = scope_text(root)
    if not value or re.fullmatch(r'\[[^\]]*\]', value):
        return []
    found = []
    for raw in value.split(';'):
        entry = raw.strip().strip('`"\'').strip()
        if not entry or library.fold(entry) in NO_SCOPE:
            continue
        if '[' in entry or ']' in entry:
            raise SyncError('Source-folder exception still has a placeholder / Ngoại lệ thư mục nguồn cũ còn chỗ trống: ' + entry)
        path = entry.replace('\\', '/')
        path = re.sub(r'^\./', '', path).rstrip('/')
        parts = path.split('/')
        if (not path or path.startswith('/') or re.match(r'^[A-Za-z]:', path) or
                any(part in ('', '.', '..') for part in parts)):
            raise SyncError('Exception must be a plain folder inside the project (no absolute path, no ..) / '
                            'Ngoại lệ phải là thư mục trong project (không dùng đường dẫn tuyệt đối hoặc ..): ' + entry)
        if parts[0].lower() in RESERVED_TOP:
            raise SyncError('Exception cannot be a package, references, working, output or archive folder / '
                            'Ngoại lệ không được là vùng của gói, references, working, output hoặc archive: ' + entry)
        full = os.path.join(root, *parts)
        if not os.path.isdir(full):
            raise SyncError('Exception folder not found / Không thấy thư mục ngoại lệ: ' + entry)
        if not link_free(full, root) or not contained(full, root):
            raise SyncError('Exception folder is or passes through a link / Thư mục ngoại lệ là hoặc đi qua liên kết: ' + entry)
        found.append({'path': '/'.join(parts), 'real': os.path.realpath(full)})
    return found


def manifest_hashes(root):
    hashes = {}
    try:
        with io.open(os.path.join(root, 'MANIFEST.sha256'), encoding='utf-8') as f:
            for line in f:
                match = re.match(r'^([0-9a-fA-F]{64})\s+\*?(.+?)\s*$', line)
                if match:
                    hashes[match.group(2).replace('\\', '/')] = match.group(1).lower()
    except OSError:
        pass
    return hashes


def package_owned(root, hashes, path, sha, group_folder=None, group=None):
    """A file shipped by the package, unchanged. A README the user wrote or edited is a source."""
    rel = os.path.relpath(path, root).replace(os.sep, '/')
    if sha in (hashes.get(rel), hashes.get('en/' + rel)):
        return True
    if group and os.path.basename(path) == 'README.md' and os.path.dirname(path) == group_folder:
        try:
            with io.open(path, encoding='utf-8', newline='') as f:
                return f.read().replace('\r\n', '\n') == library.group_readme(group)
        except (OSError, ValueError):
            return False
    return False


def sources(root, zones=None):
    ref = os.path.join(root, 'references')
    zones = scopes(root) if zones is None else zones
    hashes = manifest_hashes(root)
    areas = [(os.path.join(ref, name), ref, name) for name in library.GROUP_DIRS]
    areas += [(os.path.join(root, *zone['path'].split('/')), zone['real'], None) for zone in zones]
    found, skipped = {}, []
    for folder, zone_real, group in areas:
        if not os.path.isdir(folder):
            continue
        if group and (os.path.islink(folder) or not contained(folder, ref)):
            skipped.append((group, 'link_outside_references'))
            continue
        for here, dirs, files in os.walk(folder, followlinks=False):
            keep = []
            for name in sorted(dirs):
                full = os.path.join(here, name)
                if name.startswith(('.', '_')):
                    continue
                if os.path.islink(full) or not link_free(full, root) or not contained(full, zone_real):
                    skipped.append((os.path.relpath(full, ref).replace(os.sep, '/'), 'link'))
                    continue
                keep.append(name)
            dirs[:] = keep
            for name in sorted(files):
                if name.startswith(('~$', '.', '_INDEX')) or not name.lower().endswith(library.FILE_EXT):
                    continue
                path = os.path.join(here, name)
                rel = os.path.relpath(path, ref).replace(os.sep, '/')
                if os.path.islink(path) or not link_free(path, root) or not contained(path, zone_real):
                    skipped.append((rel, 'link'))
                    continue
                before = os.stat(path)
                sha = digest(path)
                after = os.stat(path)
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise SyncError('Source changed during scan / Nguồn đổi khi quét: ' + rel)
                if package_owned(root, hashes, path, sha, folder, group):
                    continue  # shipped folder guidance, not a user source
                found[rel] = sha
    return found, skipped


def in_scope(root, path, zones):
    ref = os.path.join(root, 'references')
    target = os.path.normcase(os.path.normpath(os.path.join(ref, *path.split('/'))))
    for zone in zones:
        base = os.path.normcase(os.path.normpath(os.path.join(root, *zone['path'].split('/'))))
        if target.startswith(base + os.sep):
            return True
    return False


def lost_state(root, zones, path):
    """State of an indexed path the scan did not return. None: not a path this sync manages."""
    top = path.split('/', 1)[0]
    if top in library.GROUP_DIRS:
        return 'MISSING'
    if top == '..':
        return 'MISSING' if in_scope(root, path, zones) else OUT_OF_SCOPE
    return None


def really_missing(root, zones, path):
    """True only when the indexed file is gone from the current scope and nothing is left at that path.

    OUT_OF_SCOPE, and a file still on disk that the scan skipped (link, package file), are not a move.
    """
    return (lost_state(root, zones, path) == 'MISSING' and
            not os.path.lexists(os.path.join(root, 'references', *path.split('/'))))


def parse_renames(tokens):
    renames, ids, paths = [], set(), set()
    for token in tokens or ():
        ident, sep, rest = str(token).partition('=')
        path, sep2, sha = rest.rpartition('#')
        ident, path, sha = ident.strip(), library.norm_path(path), sha.strip().lower()
        if not (sep and sep2 and ident and path):
            raise SyncError('A rename needs the form ID=path#sha256 taken from the preview / '
                            'Đổi tên cần dạng ID=đường_dẫn#sha256 lấy từ bản xem trước: ' + str(token))
        if not re.fullmatch(r'[0-9a-f]{8,64}', sha):
            raise SyncError('The confirmation code must be 8-64 hex characters of the new file hash / '
                            'Mã xác nhận phải là 8-64 ký tự hex của hash file mới: ' + str(token))
        if ident in ids or path in paths:
            raise SyncError('A rename is listed twice / Khai báo đổi tên bị lặp: ' + str(token))
        ids.add(ident)
        paths.add(path)
        renames.append({'id': ident, 'path': path, 'sha': sha})
    return renames


def duplicate_id_message(ident, rows):
    """Cùng nội dung với `library.py check`: nêu mã, các dòng và bước xử lý; sync không tự sửa mã. / Same facts as `library.py check`: the ID, its rows and the next step; sync never edits an ID."""
    return ('Duplicate SourceID / Trùng mã: %s (rows / dòng %s). ' % (ident, ', '.join(str(r) for r in rows)) +
            library.L('Chạy python tools/library.py check để xem mọi mã trùng, sửa hoặc bỏ dòng thừa trực tiếp trong Excel rồi chạy lại. Đừng dựng lại sổ.',
                      'Run python tools/library.py check to list every duplicate, fix or drop the extra rows directly in Excel, then run again. Do not rebuild the index.'))


def columns(ws):
    headers = [str(ws.cell(library.HEADER_ROW, i).value or '') for i in range(1, ws.max_column + 1)]
    cols = {}
    for key, prefix in library.KEYS.items():
        for i, heading in enumerate(headers, 1):
            if heading.startswith(prefix) and i not in cols.values():
                cols[key] = i
                break
    needed = ('id', 'group', 'title', 'file', 'fulltext', 'verify')
    missing = [library.KEYS[key] for key in needed if key not in cols]
    if missing:
        raise SyncError('Index is missing required columns / Sổ thiếu cột: ' + ', '.join(missing) + '. ' + library.book_steps('missing_columns'))
    for label in META:
        if label in headers:
            cols[label] = headers.index(label) + 1
        else:
            headers.append(label)
            cols[label] = len(headers)
            ws.cell(library.HEADER_ROW, cols[label], label)
    return cols


def lossy_notices(original):
    """Parts of the workbook that openpyxl cannot keep when it rewrites the file. Reported, never guessed back.

    Excel stores list validations that point at another sheet in an extension block (x14); openpyxl drops it on save.
    Cell values are not affected. Only the literal `x14:dataValidation` in a worksheet part is recognised: other namespace
    aliases or extensions are not detected. A scan that cannot finish is reported as 'x14_scan_incomplete', never as "none".
    """
    try:
        with zipfile.ZipFile(io.BytesIO(original)) as z:
            for name in z.namelist():
                if name.startswith('xl/worksheets/') and name.endswith('.xml') and b'x14:dataValidation' in z.read(name):
                    return ['x14_data_validation']
    except Exception:  # an unreadable part must not turn into "no x14"
        return ['x14_scan_incomplete']
    return []


def next_row(ws, cols):
    for row in range(library.HEADER_ROW + 1, ws.max_row + 1):
        if not any(ws.cell(row, cols[key]).value not in (None, '') for key in ('id', 'file', 'title')):
            return row
    return max(library.HEADER_ROW + 1, ws.max_row + 1)


def plan(root, renames=()):
    _, index = guard_targets(root)
    if not os.path.isfile(index):
        raise SyncError('No index / Chưa có sổ. Run: python tools/library.py init')
    confirmed = parse_renames(renames)
    zones = scopes(root)
    with open(index, 'rb') as f:
        original = f.read()
    snapshot = transaction.sha_bytes(original)
    opx = library.need_openpyxl()
    try:
        wb = opx.load_workbook(io.BytesIO(original), data_only=False)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
        raise SyncError('Cannot open index / Không mở được sổ: %s. %s' % (e, library.book_steps('unreadable')))
    if library.SHEET not in wb.sheetnames:
        raise SyncError('Index is missing sheet / Sổ thiếu sheet: ' + library.SHEET + '. ' + library.book_steps('missing_sheet'))
    ws = wb[library.SHEET]
    history = wb['LAW history'] if 'LAW history' in wb.sheetnames else None
    try:
        history_state(history)
        if library.CONTENT_SHEET in wb.sheetnames:
            library.parse_content(wb[library.CONTENT_SHEET])
        check_registry(wb)
    except ContentError as e:
        wb.close()
        raise SyncError(str(e))
    old_headers = tuple(ws.cell(library.HEADER_ROW, i).value for i in range(1, ws.max_column + 1))
    cols = columns(ws)
    by_path, by_id, ids = {}, {}, set()
    maximum = 0
    for row in range(library.HEADER_ROW + 1, ws.max_row + 1):
        ident = str(ws.cell(row, cols['id']).value or '').strip()
        path = library.norm_path(ws.cell(row, cols['file']).value)
        if not ident and not path:
            continue
        if ident:
            if ident in ids:
                raise SyncError(duplicate_id_message(ident, [by_id[ident], row]))
            ids.add(ident)
            by_id[ident] = row
            match = ID_PATTERN.match(ident)
            if match:
                maximum = max(maximum, int(match.group(1)))
        if path:
            if path in by_path:
                raise SyncError('Duplicate source path / Trùng đường dẫn: ' + path)
            by_path[path] = row
    scanned, skipped = sources(root, zones)
    changes = []
    observed = datetime.date.today().isoformat()
    renamed = set()
    for item in confirmed:
        row = by_id.get(item['id'])
        if row is None:
            raise SyncError('Rename: SourceID is not in the index / Đổi tên: mã không có trong sổ: ' + item['id'])
        old = library.norm_path(ws.cell(row, cols['file']).value)
        if not old:
            raise SyncError('Rename: the SourceID has no path / Đổi tên: mã chưa có đường dẫn: ' + item['id'])
        if old in scanned:
            raise SyncError('Rename: the file is still at its old path, so this is a copy, not a move / '
                            'Đổi tên: file vẫn còn ở đường dẫn cũ, đây là bản sao chứ không phải đổi tên: ' + old)
        if lost_state(root, zones, old) != 'MISSING':
            raise SyncError('Rename: the old source is outside the current scope, not missing from it / '
                            'Đổi tên: nguồn cũ nằm ngoài phạm vi hiện hành, không phải file thiếu trong phạm vi: ' + old)
        if not really_missing(root, zones, old):
            raise SyncError('Rename: something is still at the old path (skipped, a link or a package file), so this is not a move / '
                            'Đổi tên: đường dẫn cũ vẫn còn thứ gì đó (bị bỏ qua, liên kết hoặc file của gói), không phải đổi tên: ' + old)
        new = item['path']
        if new not in scanned:
            raise SyncError('Rename: the new path is not a scanned source (wrong scope, missing, skipped or a package file) / '
                            'Đổi tên: đường dẫn mới không phải nguồn đã quét (sai phạm vi, không có, bị bỏ qua hoặc là file của gói): ' + new)
        owner = by_path.get(new)
        if owner is not None and owner != row:
            raise SyncError('Rename: the new path already belongs to another SourceID / '
                            'Đổi tên: đường dẫn mới đã thuộc mã khác: ' + new)
        if not scanned[new].startswith(item['sha']):
            raise SyncError('Rename: the file changed since the preview or the code is wrong; preview again / '
                            'Đổi tên: file đã đổi sau bản xem trước hoặc mã sai; xem trước lại: ' + new)
        old_sha = str(ws.cell(row, cols['LAW SHA-256']).value or '')
        ws.cell(row, cols['file'], new)
        del by_path[old]
        by_path[new] = row
        renamed.add(new)
        changes.append({'action': 'renamed', 'id': item['id'], 'path': new, 'from': old,
                        'same_content': bool(old_sha) and old_sha == scanned[new]})
    # Ứng viên đổi tên: chỉ báo, không áp dụng. / Rename candidates: reported only, never applied.
    candidates = []
    fresh = [path for path in scanned if path not in by_path]
    for old, row in by_path.items():
        old_sha = str(ws.cell(row, cols['LAW SHA-256']).value or '')
        ident = str(ws.cell(row, cols['id']).value or '').strip()
        if old in scanned or not old_sha or not ident or not really_missing(root, zones, old):
            continue
        for new in fresh:
            if scanned[new] == old_sha:
                candidates.append({'id': ident, 'from': old, 'to': new,
                                   'token': '%s=%s#%s' % (ident, new, old_sha[:12])})
    for candidate in candidates:
        candidate['ambiguous'] = (sum(1 for c in candidates if c['to'] == candidate['to']) > 1 or
                                  sum(1 for c in candidates if c['id'] == candidate['id']) > 1)
    for path, sha in sorted(scanned.items()):
        row = by_path.get(path)
        if row is None:
            row = next_row(ws, cols)
            maximum += 1
            ws.cell(row, cols['id'], 'SRC-%06d' % maximum)
            top = path.split('/', 1)[0]
            old_source = top == '..'
            ws.cell(row, cols['group'], library.GROUP_DIRS['source-documents' if old_source else top][0])
            ws.cell(row, cols['title'], os.path.basename(path))
            ws.cell(row, cols['file'], path)
            ws.cell(row, cols['fulltext'], 'Có')
            ws.cell(row, cols['verify'], 'Cần đối chiếu')
            if old_source and 'notes' in cols and ws.cell(row, cols['notes']).value in (None, ''):
                ws.cell(row, cols['notes'], 'Nguồn cũ giữ tại chỗ; phạm vi do người dùng chọn trong PROJECT.md')
            changes.append({'action': 'add', 'path': path, 'id': ws.cell(row, cols['id']).value})
        old_sha = str(ws.cell(row, cols['LAW SHA-256']).value or '')
        old_state = ws.cell(row, cols['LAW file state']).value
        if old_sha != sha:
            revision = ws.cell(row, cols['LAW revision']).value
            if revision not in (None, '') and (not isinstance(revision, int) or revision < 1):
                raise SyncError('Invalid revision / Revision sai ở dòng %d' % row)
            new_revision = (revision + 1) if old_sha and revision else 1
            if old_sha:
                if history is None:
                    history = wb.create_sheet('LAW history')
                    history.append(HISTORY_LEGACY)
                prior = (ws.cell(row, cols['id']).value, revision, old_sha, ws.cell(row, cols['verify']).value, observed)
                if history_layout_for_sync(history) == 'extended':  # B-01: giữ đúng định dạng đã mở rộng / keep the extended format
                    history_add(history, prior + ('', 'BYTES_CHANGED', new_revision) + ('',) * 8)
                else:
                    history.append(prior)
                ws.cell(row, cols['verify'], 'Cần đối chiếu')
            ws.cell(row, cols['LAW revision'], new_revision)
            ws.cell(row, cols['LAW SHA-256'], sha)
            if old_sha:
                changes.append({'action': 'changed', 'path': path, 'id': ws.cell(row, cols['id']).value})
            elif not any(change['path'] == path for change in changes):
                changes.append({'action': 'observed', 'path': path, 'id': ws.cell(row, cols['id']).value})
        elif ws.cell(row, cols['LAW revision']).value in (None, ''):
            ws.cell(row, cols['LAW revision'], 1)
            changes.append({'action': 'revision_initialized', 'path': path,
                            'id': ws.cell(row, cols['id']).value})
        record_state = ('NEEDS_REVIEW' if old_sha and old_sha != sha else
                        'NEEDS_REVIEW' if old_state == 'NEEDS_REVIEW' and
                        library.fold(ws.cell(row, cols['verify']).value) == 'can doi chieu' else 'PRESENT')
        if old_sha != sha or old_state != record_state:
            ws.cell(row, cols['LAW observed'], observed)
            ws.cell(row, cols['LAW file state'], record_state)
            if old_sha == sha and old_state != record_state and path not in renamed:
                changes.append({'action': 'state', 'path': path,
                                'id': ws.cell(row, cols['id']).value, 'state': record_state})
        if not ws.cell(row, cols['id']).value:
            maximum += 1
            ws.cell(row, cols['id'], 'SRC-%06d' % maximum)
            changes.append({'action': 'assign_id', 'path': path, 'id': ws.cell(row, cols['id']).value})
    for path, row in by_path.items():
        if path in scanned:
            continue
        state = lost_state(root, zones, path)
        if state is None:
            continue
        action = 'missing' if state == 'MISSING' else 'out_of_scope'
        if ws.cell(row, cols['LAW file state']).value != state:
            ws.cell(row, cols['LAW file state'], state)
            ws.cell(row, cols['LAW observed'], observed)
            changes.append({'action': action, 'path': path, 'id': ws.cell(row, cols['id']).value})
    changed_header = old_headers != tuple(ws.cell(library.HEADER_ROW, i).value for i in range(1, ws.max_column + 1))
    extra = {'candidates': candidates, 'scopes': [zone['path'] for zone in zones], 'notices': []}
    if not (changes or changed_header):
        wb.close()
        return dict(extra, snapshot=snapshot, changes=[], skipped=skipped, bytes=None, sources=scanned)
    stream = io.BytesIO()
    wb.save(stream)
    wb.close()
    opx.load_workbook(io.BytesIO(stream.getvalue()), read_only=True).close()
    extra['notices'] = lossy_notices(original)
    return dict(extra, snapshot=snapshot, changes=changes, skipped=skipped, bytes=stream.getvalue(), sources=scanned)


def preview_binding(result):
    """Điều kiện hợp tác để Apply đúng bản đã xem: snapshot sổ, hash nguồn theo đường dẫn, phạm vi nguồn cũ. Không chứa bytes; JSON
    round-trip ổn định. Không phải quyền hay biên nhận. / The cooperative precondition for applying exactly what was previewed:
    index snapshot, source hashes by path, old-source scopes. No bytes; stable through JSON. Not a grant, not a receipt."""
    return {'snapshot': result['snapshot'], 'sources': dict(result['sources']), 'scopes': list(result['scopes'])}


_SHA256 = re.compile(r'[0-9a-f]{64}')


def check_expected_preview(expected):
    """Kiểm cấu trúc trước khi chạm khóa hay đọc sổ / structural check before any lock or read."""
    bad = PreviewMismatch('The preview is missing or malformed; preview again before applying / '
                          'Bản xem trước thiếu hoặc sai cấu trúc; xem trước lại rồi mới ghi.', 'invalid')
    if not isinstance(expected, dict) or set(expected) != {'snapshot', 'sources', 'scopes'}:
        raise bad
    snap, srcs, zones = expected['snapshot'], expected['sources'], expected['scopes']
    if not (isinstance(snap, str) and _SHA256.fullmatch(snap) and isinstance(srcs, dict) and isinstance(zones, list)):
        raise bad
    if not all(isinstance(k, str) and isinstance(v, str) and _SHA256.fullmatch(v) for k, v in srcs.items()):
        raise bad
    if not all(isinstance(z, str) for z in zones):
        raise bad
    return expected


def compare_expected_preview(expected, result):
    """So với plan vừa tính dưới khóa; lệch thì từ chối, kể cả khi plan mới không có gì để ghi. / Compare with the plan just recomputed under the lock."""
    now = preview_binding(result)
    for reason, en, vi in (('snapshot', 'The index changed after the preview', 'Sổ đã đổi sau bản xem trước'),
                           ('sources', 'The source files changed after the preview', 'Các file nguồn đã đổi sau bản xem trước'),
                           ('scopes', 'The old-source scope in PROJECT.md changed after the preview',
                            'Phạm vi nguồn cũ trong PROJECT.md đã đổi sau bản xem trước')):
        if expected[reason] != now[reason]:
            raise PreviewMismatch('%s; LAW did not change the index or source files, and no new file transaction was created; preview again / '
                                  '%s; LAW không sửa sổ hoặc file nguồn, chưa tạo giao dịch file mới; xem trước lại.' % (en, vi), reason)


def guard_runtime(root):
    """Refuse, before the lock exists, when .agent or its runtime folders are or pass through a link."""
    problem = transaction.runtime_problem(root)
    folder = os.path.join(root, '.agent', 'runtime', 'library')
    if problem or not link_free(folder, root):
        raise SyncError('The LAW runtime folder is, or passes through, a link; stopped before any lock or journal was created / '
                        'Thư mục runtime của LAW là hoặc đi qua liên kết; dừng trước khi tạo khóa hoặc nhật ký: .agent/runtime')
    return folder


def take_os_lock(fd):
    """Become the owner of the lock file: an exclusive, non-blocking lock held by the operating system on this open file.

    It goes away when the holder closes the file or dies, so no process id is read or trusted (a reused id means nothing),
    and nobody ever deletes or rewrites the file to take over. Raises OSError when someone else holds it.
    """
    if os.name == 'nt':
        import msvcrt
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def drop_os_lock(fd):
    try:
        if os.name == 'nt':
            import msvcrt
            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass  # closing the file releases it anyway


REPARSE_POINT = 0x400  # FILE_ATTRIBUTE_REPARSE_POINT: symlink, junction or other reparse leaf on Windows


def refuse_lock_leaf(fd, why_en, why_vi):
    """Close the lock descriptor (if any) and refuse. Nothing has been byte-locked when this runs before take_os_lock."""
    if fd is not None:
        try:
            os.close(fd)
        except OSError:
            pass
    raise SyncError('The index.lock file is not safe to lock (%s); the index and the existing transaction records were not changed / '
                    'File index.lock chưa an toàn để khóa (%s); chưa đổi sổ hay hồ sơ giao dịch hiện có: .agent/runtime/library/index.lock'
                    % (why_en, why_vi))


def lock_leaf_identity(st, fd=None):
    """Identity (device, file id) of a lock leaf from lstat/fstat, or a refusal. Must be one plain regular file with a single link."""
    if stat.S_ISLNK(st.st_mode) or (getattr(st, 'st_file_attributes', 0) or 0) & REPARSE_POINT:
        refuse_lock_leaf(fd, 'it is a symlink or reparse point', 'là liên kết hoặc điểm phân tích lại')
    if not stat.S_ISREG(st.st_mode):
        refuse_lock_leaf(fd, 'it is not a regular file', 'không phải file thường')
    links = getattr(st, 'st_nlink', None)
    if type(links) is not int or links < 1:
        refuse_lock_leaf(fd, 'its link count cannot be determined', 'không xác định được số liên kết')
    if links != 1:
        refuse_lock_leaf(fd, 'it has %d names, so locking it would lock another path too' % links,
                         'nó có %d tên nên khóa nó sẽ khóa cả đường dẫn khác' % links)
    dev, ino = getattr(st, 'st_dev', None), getattr(st, 'st_ino', None)
    if type(dev) is not int or type(ino) is not int or not dev or not ino:
        refuse_lock_leaf(fd, 'its identity cannot be determined', 'không xác định được định danh')
    return (dev, ino)


def lock_leaf_state(path, fd=None):
    """lstat of the full leaf: None when absent, else its checked identity. Any other metadata error is a refusal."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as e:
        refuse_lock_leaf(fd, 'its metadata cannot be read: %s' % e, 'không đọc được thông tin: %s' % e)
    return lock_leaf_identity(st, fd)


def recheck_lock_leaf(fd, path, identity, close=True):
    """The open descriptor, the path now and the identity first seen must be the same single plain file. Raises SyncError.

    close=False leaves the descriptor to the caller (the lock is already held and its owner closes it once).
    """
    owned = fd if close else None
    try:
        st = os.fstat(fd)
    except OSError as e:
        refuse_lock_leaf(owned, 'the open file cannot be inspected: %s' % e, 'không kiểm tra được file đang mở: %s' % e)
    seen = lock_leaf_identity(st, owned)
    current = lock_leaf_state(path, owned)
    if current is None or seen != current or (identity is not None and seen != identity):
        refuse_lock_leaf(owned, 'the file at that path is not the one that was opened', 'file tại đường dẫn không phải file đã mở')
    return seen


def open_lock_leaf(path):
    """Open index.lock and return (fd, identity) only for one plain, single-link regular file.

    Absent: created with O_CREAT|O_EXCL, so an entry that appears meanwhile is never followed by a create. Existing: opened
    without O_CREAT or O_TRUNC after its metadata was checked. Old lock bytes (even a process id) are kept and never trusted.
    This is not an atomic no-follow open: a swap after the checks is caught by comparing the descriptor, the path and the
    first identity, not prevented. Exclusive creation says nothing about ownership; the OS byte lock still does.
    """
    binary = getattr(os, 'O_BINARY', 0)
    for _ in range(3):  # bounded: absent -> exists/vanishes meanwhile -> look again, never loop forever
        before = lock_leaf_state(path)
        try:
            if before is None:
                fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL | binary, 0o600)
            else:
                fd = os.open(path, os.O_RDWR | binary)
        except (FileExistsError, FileNotFoundError):
            continue
        except OSError as e:
            refuse_lock_leaf(None, 'it cannot be opened: %s' % e, 'không mở được: %s' % e)
        return fd, recheck_lock_leaf(fd, path, before)
    refuse_lock_leaf(None, 'it kept appearing or disappearing while it was opened', 'nó liên tục xuất hiện hoặc biến mất khi mở')


@contextlib.contextmanager
def writer_lock(root):
    folder = guard_runtime(root)
    os.makedirs(folder, exist_ok=True)
    with transaction.Pins() as pins:
        pins.hold(folder)  # giữ thư mục khóa để không bị thay bằng liên kết / keeps the lock folder from being swapped
        guard_runtime(root)
        lock = os.path.join(folder, 'index.lock')
        fd, identity = open_lock_leaf(lock)  # exclusive-create or checked existing; never O_TRUNC, never unlinked
        try:
            try:
                take_os_lock(fd)
            except OSError:
                raise SyncError('Another LAW writer holds the index; wait for it to finish and run again / '
                                'Sổ đang được một lần LAW khác ghi; chờ lần đó xong rồi chạy lại.')
            try:
                recheck_lock_leaf(fd, lock, identity, close=False)  # still the same single plain file once the byte lock is held
                yield
            finally:
                drop_os_lock(fd)
        finally:
            try:
                os.close(fd)
            except OSError:
                pass


def refuse_if_lossy(notices):
    """Từ chối trước mọi Transaction/staging/backup khi ghi lại sẽ làm mất phần openpyxl không giữ được (A-06 x14).
    Refuse before any Transaction, staging or backup when the rewrite would drop what openpyxl cannot keep (A-06 x14 known loss)."""
    if 'x14_data_validation' in notices:
        raise SyncError('Refused: the index holds drop-down lists in Excel extended (x14) form that a rewrite would drop; nothing was written. '
                        'Preview still works / Từ chối: sổ có danh sách thả xuống dạng mở rộng (x14) của Excel sẽ mất khi ghi lại; chưa ghi gì. '
                        'Vẫn xem trước được.')
    if 'x14_scan_incomplete' in notices:
        raise SyncError('Refused: could not finish checking the index for x14 drop-down lists, so a rewrite is not known to be safe; nothing was written / '
                        'Từ chối: chưa kiểm xong sổ có danh sách thả xuống x14 hay không nên chưa biết ghi lại có an toàn; chưa ghi gì.')


def locked_commit(root, prepare, check=None, recheck=None, operation='library-sync'):
    """Một đường ghi sổ duy nhất cho sync, nội dung và sự kiện nguồn: khóa writer, Pins, nhật ký strict, plan tính lại dưới khóa,
    x14, Transaction expected_before. One index-write path for sync, content and source events."""
    ref, _ = guard_targets(root)  # refuse a link target before the lock or any transaction exists
    guard_runtime(root)
    with writer_lock(root), transaction.Pins() as pins:
        # Giữ references từ lúc kiểm đến hết ghi: không thể thay nó bằng liên kết ở giữa (Windows).
        # Hold references from the check to the end of the write: it cannot be swapped for a link in between (Windows).
        held_ref = pins.hold(ref)
        guard_targets(root)
        # strict: a journal that cannot be read or interpreted must stop the write, never look like "nothing unfinished" (A-06).
        # strict: nhật ký không đọc/diễn giải được phải chặn ghi, không được coi là "không có giao dịch dở".
        try:
            pending = transaction.incomplete(root, strict=True)
        except (OSError, ValueError, TypeError, AttributeError, transaction.TransactionError) as e:
            raise SyncError('Cannot tell whether a file transaction is unfinished (journal unreadable or not understood); '
                            'the index and existing transaction records were not changed, and no new file transaction was created; '
                            'check the records under .agent/runtime/transactions, do not delete them to continue / '
                            'Không xác định được có giao dịch file dở hay không (nhật ký không đọc hoặc không diễn giải được); '
                            'không đổi sổ hoặc hồ sơ giao dịch hiện có, chưa tạo giao dịch file mới; '
                            'kiểm hồ sơ trong .agent/runtime/transactions, không xóa nhật ký để chạy tiếp: %s' % e)
        if pending:
            raise SyncError('Unfinished file transaction / Có giao dịch file chưa xong; chạy tools/transaction.py status')
        result = prepare()
        if check is not None:
            check(result)
        if result['bytes'] is None:
            return dict(result, protection='not_needed')
        refuse_if_lossy(result['notices'])
        if recheck is not None:
            recheck(result)
        tx = (transaction.Transaction(root, operation, create_only=True) if result.get('create_files')
              else transaction.Transaction(root, operation))
        try:
            for item in result.get('create_files', ()):
                tx.add(item['path'], item['data'], action='create', expected_before=None)
            tx.add('references/_INDEX.xlsx', result['bytes'], expected_before=result['snapshot'])
            tx.run()
        except transaction.TransactionError as e:
            if result.get('create_files'):
                raise IntakeWriteError(str(e), tx) from e
            raise SyncError(str(e))
        except OSError as e:
            tail = transaction.blocked_message(root)
            if result.get('create_files'):
                raise IntakeWriteError('Intake transaction did not finish cleanly: %s%s' %
                                       (e, ('\n' + tail) if tail else ''), tx) from e
            raise SyncError('Writing the index did not finish; the index may be unchanged or partly written / '
                            'Ghi sổ chưa hoàn tất, sổ có thể chưa đổi hoặc mới ghi một phần: %s%s' % (e, ('\n' + tail) if tail else ''))
        # 'held': thư mục được giữ mở suốt lúc kiểm→ghi (Windows). 'recheck_only': chỉ kiểm lại sát trước ghi, cửa sổ ngắn còn mở.
        # 'held': folders held open from check to write (Windows). 'recheck_only': re-check right before the write only; a short window stays open.
        return dict(result, protection='held' if held_ref and tx.protection == 'held' else 'recheck_only')


def intake_plan(root, selection):
    """Prepare create-only source files and their catalog rows in this owner's single write path."""
    import library_intake
    observation = library_intake.observe(root, selection)
    original, snapshot, wb = open_index(root)
    opx = library.need_openpyxl()
    try:
        history = wb['LAW history'] if 'LAW history' in wb.sheetnames else None
        history_state(history)
        check_registry(wb)
        entries = library.parse_content(wb[library.CONTENT_SHEET]) if library.CONTENT_SHEET in wb.sheetnames else []
        ws = wb[library.SHEET]
        old_columns = ws.max_column
        cols = columns(ws)
        if 'number' not in cols:
            raise SyncError('Intake needs the Number/code column; no source was imported')
        by_id, by_path, by_code, maximum = {}, {}, {}, 0
        for row in range(library.HEADER_ROW + 1, ws.max_row + 1):
            ident = str(ws.cell(row, cols['id']).value or '').strip()
            path = library.norm_path(ws.cell(row, cols['file']).value)
            if ident:
                if ident in by_id:
                    raise SyncError(duplicate_id_message(ident, [by_id[ident], row]))
                by_id[ident] = row
                match = ID_PATTERN.fullmatch(ident)
                maximum = max(maximum, int(match.group(1))) if match else maximum
            if path:
                folded = path.casefold()
                if folded in by_path:
                    raise SyncError('Duplicate source path: ' + path)
                by_path[folded] = row
            code = str(ws.cell(row, cols['number']).value or '').strip() if 'number' in cols else ''
            if code:
                by_code.setdefault(code, []).append(row)
        observed = datetime.date.today().isoformat()
        items, creates, allowed = [], [], set()
        for selected in observation['selected']:
            code, path = selected['code'], selected['destination']
            if path.casefold() in by_path:
                raise SyncError('Replacement refused: destination is already cataloged: ' + path)
            rows = by_code.get(code, [])
            if len(rows) > 1:
                raise SyncError('Multiple catalog rows for code: ' + code)
            row = rows[0] if rows else next((n for n in range(library.HEADER_ROW + 1, ws.max_row + 1)
                                            if all(ws.cell(n, col).value in (None, '')
                                                   for col in range(1, ws.max_column + 1))),
                                           max(library.HEADER_ROW + 1, ws.max_row + 1))
            ident = str(ws.cell(row, cols['id']).value or '').strip()
            if rows:
                if library.norm_path(ws.cell(row, cols['file']).value):
                    raise SyncError('Replacement refused: code already has a path: ' + code)
                if (ws.cell(row, cols['LAW revision']).value not in (None, '') or
                        ws.cell(row, cols['LAW SHA-256']).value not in (None, '') or
                        any(e['source_id'] == ident for e in entries) or
                        (history is not None and any(str(history.cell(n, 1).value or '').strip() == ident
                                                    for n in range(2, history.max_row + 1)))):
                    raise SyncError('Reattachment refused: source has a prior observation/history/content basis: ' + code)
                if library.fold(ws.cell(row, cols['fulltext']).value) == 'co':
                    raise SyncError('Pathless source declares full text; confirm its basis before intake: ' + code)
            if not ident:
                maximum += 1
                ident = 'SRC-%06d' % maximum
            values = {'id': ident, 'file': path, 'verify': 'Cần đối chiếu', 'LAW revision': 1,
                      'LAW SHA-256': selected['sha256'], 'LAW observed': observed, 'LAW file state': 'PRESENT'}
            if not rows:
                values.update(group=library.GROUP_DIRS[path.split('/')[0]][0], title=selected['canonical_name'], fulltext=None)
                if 'number' in cols:
                    values['number'] = code
                # Full text stays blank: receiving bytes is not a declaration of completeness.
            for key, value in values.items():
                put(ws, row, cols[key], value)
                allowed.add((row, cols[key]))
            items.append({'source': selected['source'], 'destination': path, 'id': ident, 'row': row,
                          'revision': 1, 'sha256': selected['sha256'], 'verification': 'Cần đối chiếu',
                          'fulltext': ws.cell(row, cols['fulltext']).value, 'observed': observed})
            creates.append({'path': 'references/' + path, 'data': selected['data']})
            by_path[path.casefold()] = row
        staged = save_workbook(wb)
        wb = None
        verify_staged(opx, original, staged, lambda name, key: name == library.SHEET and
                      (key in allowed or (key[0] == library.HEADER_ROW and key[1] > old_columns)))
        basis = library_intake.binding(observation)
        token = plan_token('intake', selection, snapshot, {'observation': basis, 'items': items})
        return {'snapshot': snapshot, 'plan_token': token, 'items': items, 'bytes': staged,
                'create_files': creates, 'notices': lossy_notices(original), 'observation': basis,
                'warning': 'Classification only; identity, full text and current validity are not verified. Staging is retained.'}
    finally:
        if wb is not None:
            wb.close()


def intake_apply(root, selection, token):
    import library_intake
    if not isinstance(token, str) or not _SHA256.fullmatch(token):
        raise SyncError('Apply needs the exact preview plan token')

    def check(result):
        if token != result['plan_token']:
            raise SyncError('Intake config, index, sources, selection or plan changed; preview again; no new transaction created')

    def recheck(result):
        now = library_intake.observe(root, selection)
        if library_intake.binding(now) != result['observation']:
            raise SyncError('Intake source/config changed while preparing; no new transaction created')

    return locked_commit(root, lambda: intake_plan(root, selection), check=check, recheck=recheck,
                         operation='library-intake')


def apply(root, renames=(), expected_preview=None):
    """expected_preview=None giữ nguyên hành vi CLI. Khác None (giao diện) thì phải khớp plan tính lại dưới khóa, trước mọi Transaction.
    expected_preview=None keeps the CLI behaviour. Anything else (the panel) must match the plan recomputed under the lock, before any Transaction."""
    if expected_preview is not None:
        expected_preview = check_expected_preview(expected_preview)

    def recheck(result):
        current, _ = sources(root)
        if current != result['sources']:
            raise SyncError('Sources changed while preparing / Nguồn đổi khi chuẩn bị ghi; xem lại và chạy lại')

    return locked_commit(root, lambda: plan(root, renames),
                         check=(lambda result: compare_expected_preview(expected_preview, result)) if expected_preview is not None else None,
                         recheck=recheck)


# ---------------------------------------------------------------- B-01: nội dung theo phiên bản nguồn và source-event explicit
# Cùng writer (locked_commit) với sync; không quét lại thư viện, không đọc nguồn nào ngoài nguồn được khai.
# Same writer (locked_commit) as sync; no library rescan, no source read beyond the declared one.
HISTORY_LEGACY = ('SourceID', 'Prior revision', 'Prior SHA-256', 'Prior verification', 'Changed on')
HISTORY_EXTENDED = HISTORY_LEGACY + ('Event ID', 'Event kind', 'New revision', 'Reason', 'Evidence ref', 'Actor', 'Request payload',
                                     'Observed before: status', 'Observed before: replaces',
                                     'Observed before: replaced by', 'Observed before: effective')
EVENT_MODES = ('semantic_update', 'reconcile_manual_edit')
EVENT_KINDS = {'semantic_update': 'SEMANTIC_UPDATE', 'reconcile_manual_edit': 'RECONCILE_MANUAL_EDIT'}
EVENT_KEYS = ('event_id', 'source_id', 'expected_revision', 'expected_sha256', 'mode', 'changes', 'reason', 'evidence_ref',
              'recorded_by')
EVENT_CHANGE_KEYS = tuple(key for key, _ in library.SEMANTIC_FIELDS)
MAX_REQUEST_BYTES = 1024 * 1024
ContentError = library.ContentError


def bad_request(vi, en):
    return ContentError('MALFORMED_REQUEST', 'Yêu cầu không hợp lệ: ' + vi, 'Malformed request: ' + en)


def canon(value):
    """JSON chuẩn hóa để so idempotence và buộc token. / Canonical JSON for idempotence and the plan token."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def put(ws, row, col, value):
    """Ghi một ô; chuỗi luôn là chuỗi literal (kể cả bắt đầu bằng = + - @), không bao giờ thành công thức.
    Write one cell; a string stays a literal string (even when it starts with = + - @), never a formula."""
    cell = ws.cell(row, col)
    cell.value = value
    if isinstance(value, str):
        cell.data_type = 's'
    return cell


def load_request(path):
    """Đọc file yêu cầu JSON: dữ liệu thuần, không chạy như script, khóa trùng bị từ chối. / Read a JSON request file as plain data."""
    def no_duplicates(pairs):
        keys = [k for k, _ in pairs]
        if len(set(keys)) != len(keys):
            raise ValueError('duplicate key')
        return dict(pairs)
    try:
        with open(path, 'rb') as f:
            raw = f.read(MAX_REQUEST_BYTES + 1)
    except OSError as e:
        raise bad_request('không đọc được file: %s' % e, 'cannot read the file: %s' % e)
    if len(raw) > MAX_REQUEST_BYTES:
        raise bad_request('file quá lớn', 'the file is too large')
    try:
        data = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, ValueError) as e:
        raise bad_request('không phải JSON UTF-8 hợp lệ (%s)' % e, 'not valid UTF-8 JSON (%s)' % e)
    if not isinstance(data, dict):
        raise bad_request('phải là một đối tượng JSON', 'it must be a JSON object')
    return data


def clean_text(name, value, required=False):
    if not isinstance(value, str):
        raise bad_request('%s phải là chuỗi' % name, '%s must be a string' % name)
    if required and not value.strip():
        raise bad_request('%s không được trống' % name, '%s must not be empty' % name)
    if library.BAD_CHARS.search(value):
        raise bad_request('%s chứa ký tự điều khiển không lưu được' % name, '%s has a control character that cannot be stored' % name)
    if len(value) > library.CELL_LIMIT:
        raise bad_request('%s dài hơn giới hạn ô %d ký tự; không cắt bớt' % (name, library.CELL_LIMIT),
                          '%s is longer than the %d-character cell limit; it is not truncated' % (name, library.CELL_LIMIT))
    return value


def clean_revision(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise bad_request('%s phải là số nguyên dương' % name, '%s must be a positive integer' % name)
    return value


def clean_sha(name, value):
    value = clean_text(name, value, True).strip().lower()
    if not library.SHA256_RE.fullmatch(value):
        raise bad_request('%s phải là SHA-256 đủ 64 ký tự hex' % name, '%s must be a full 64-hex SHA-256' % name)
    return value


def content_request(request):
    """Chuẩn hóa yêu cầu ghi nội dung; khóa lạ hoặc sai kiểu bị từ chối. / Normalise a content request; unknown keys or wrong types are refused."""
    if not isinstance(request, dict):
        raise bad_request('phải là một đối tượng', 'it must be an object')
    unknown = sorted(set(request) - set(library.CONTENT_REQUEST_KEYS))
    if unknown:
        raise bad_request('khóa không được biết: ' + ', '.join(map(str, unknown)), 'unknown keys: ' + ', '.join(map(str, unknown)))
    missing = [k for k in library.CONTENT_REQUIRED if k not in request]
    if missing:
        raise bad_request('thiếu: ' + ', '.join(missing), 'missing: ' + ', '.join(missing))
    out = {}
    for key in library.CONTENT_REQUEST_KEYS:
        value = request.get(key, 'NOT_CHECKED' if key == 'check_level' else ('' if key != 'source_revision' else None))
        if key == 'source_revision':
            out[key] = clean_revision(key, value)
        elif key == 'source_sha256':
            out[key] = clean_sha(key, value)
        else:
            out[key] = clean_text(key, value, key in library.CONTENT_REQUIRED)
    if out['kind'] not in library.CONTENT_KINDS:
        raise bad_request('kind phải là một trong ' + '/'.join(library.CONTENT_KINDS), 'kind must be one of ' + '/'.join(library.CONTENT_KINDS))
    checks = ('check_scope', 'check_evidence_ref', 'checked_by', 'checked_at')
    if out['check_level'] not in library.CHECK_LEVELS:
        raise bad_request('check_level phải là NOT_CHECKED hoặc DECLARED_CHECK', 'check_level must be NOT_CHECKED or DECLARED_CHECK')
    if out['check_level'] == 'DECLARED_CHECK' and not all(out[k].strip() for k in checks):
        raise bad_request('DECLARED_CHECK cần đủ ' + ', '.join(checks), 'DECLARED_CHECK needs all of ' + ', '.join(checks))
    if out['check_level'] == 'NOT_CHECKED' and any(out[k] for k in checks):
        raise bad_request('NOT_CHECKED không đi kèm thông tin kiểm', 'NOT_CHECKED cannot carry check details')
    if bool(out['user_decision'].strip()) != bool(out['user_confirmation_ref'].strip()):
        raise bad_request('user_decision và user_confirmation_ref phải đi cùng nhau, chỉ điền từ căn cứ thực của người dùng',
                          'user_decision and user_confirmation_ref must come together, filled only from real user evidence')
    if out['supersedes'] and out['supersedes'] == out['entry_id']:
        raise bad_request('supersedes không được trỏ chính nó', 'supersedes cannot point to itself')
    return out


def event_request(request):
    """Chuẩn hóa yêu cầu source-event; changes chỉ nhận bốn trường ngữ nghĩa. / Normalise a source-event request; changes accept only the four semantic fields."""
    if not isinstance(request, dict):
        raise bad_request('phải là một đối tượng', 'it must be an object')
    unknown = sorted(set(request) - set(EVENT_KEYS))
    if unknown:
        raise bad_request('khóa không được biết: ' + ', '.join(map(str, unknown)), 'unknown keys: ' + ', '.join(map(str, unknown)))
    missing = [k for k in EVENT_KEYS if k not in request and k != 'changes']
    if missing:
        raise bad_request('thiếu: ' + ', '.join(missing), 'missing: ' + ', '.join(missing))
    out = {'event_id': clean_text('event_id', request['event_id'], True), 'source_id': clean_text('source_id', request['source_id'], True),
           'expected_revision': clean_revision('expected_revision', request['expected_revision']),
           'expected_sha256': clean_sha('expected_sha256', request['expected_sha256']),
           'mode': clean_text('mode', request['mode'], True), 'reason': clean_text('reason', request['reason'], True),
           'evidence_ref': clean_text('evidence_ref', request['evidence_ref'], True),
           'recorded_by': clean_text('recorded_by', request['recorded_by'], True)}
    if out['mode'] not in EVENT_MODES:
        raise bad_request('mode phải là ' + ' hoặc '.join(EVENT_MODES), 'mode must be ' + ' or '.join(EVENT_MODES))
    changes = request.get('changes', {})
    if not isinstance(changes, dict) or set(changes) - set(EVENT_CHANGE_KEYS):
        raise bad_request('changes chỉ nhận ' + '/'.join(EVENT_CHANGE_KEYS), 'changes accepts only ' + '/'.join(EVENT_CHANGE_KEYS))
    out['changes'] = {k: clean_text('changes.' + k, v).strip() for k, v in changes.items()}
    if out['mode'] == 'semantic_update' and not out['changes']:
        raise bad_request('semantic_update cần ít nhất một thay đổi', 'semantic_update needs at least one change')
    if len(canon(out)) > library.CELL_LIMIT:
        raise bad_request('yêu cầu dài hơn giới hạn ô; không cắt bớt', 'the request is longer than the cell limit; it is not truncated')
    return out


# ---- lịch sử / history
def history_layout(history):
    """legacy (5 cột cũ) | extended (định dạng B-01) | unknown (nhiều cột hơn nhưng không phải định dạng đã tài liệu hóa)."""
    width = history.max_column
    header = tuple(str(history.cell(1, i).value or '') for i in range(1, width + 1))
    if any(cell.data_type == 'f' for cell in history[1]):
        return 'unknown'
    if header == HISTORY_LEGACY:
        return 'legacy'
    return 'extended' if header == HISTORY_EXTENDED else 'unknown'


def history_events(history):
    """event_id -> {row, kind, new_revision, payload}. Khóa trùng thì từ chối. / Duplicate event ids are refused."""
    events = {}
    for row in range(2, history.max_row + 1):
        values = tuple(history.cell(row, col).value for col in range(1, len(HISTORY_EXTENDED) + 1))
        if any(history.cell(row, col).data_type == 'f' for col in range(1, len(HISTORY_EXTENDED) + 1)):
            raise ContentError('UNSUPPORTED_HISTORY', 'LAW history có công thức ở dòng %s' % row,
                               'LAW history has a formula at row %s' % row)
        if not any(value not in (None, '') for value in values[5:]):
            continue  # untouched rows from the legacy five-column layout
        kind, revision, payload = values[6], values[7], values[11]
        valid_revision = isinstance(revision, int) and not isinstance(revision, bool) and revision > 0
        ident = history.cell(row, 6).value
        if kind == 'BYTES_CHANGED' and ident in (None, '') and valid_revision and \
                all(value in (None, '') for value in values[8:]):
            continue
        try:
            req = event_request(json.loads(payload)) if isinstance(payload, str) else None
        except (ValueError, TypeError, ContentError):
            req = None
        if not (req and valid_revision and kind == EVENT_KINDS[req['mode']] and ident == req['event_id'] and
                values[0] == req['source_id'] and type(values[1]) is int and values[1] == req['expected_revision'] and
                values[2] == req['expected_sha256'] and revision == req['expected_revision'] + 1 and
                values[8:11] == (req['reason'], req['evidence_ref'], req['recorded_by']) and payload == canon(req)):
            raise ContentError('UNSUPPORTED_HISTORY', 'LAW history có sự kiện không diễn giải được ở dòng %s' % row,
                               'LAW history has an uninterpretable event at row %s' % row)
        if ident in (None, ''):
            continue
        ident = str(ident)
        if ident in events:
            raise ContentError('UNSUPPORTED_HISTORY', 'LAW history có Event ID trùng: ' + ident, 'LAW history has a duplicate Event ID: ' + ident)
        events[ident] = {'row': row, 'kind': str(history.cell(row, 7).value or ''), 'new_revision': history.cell(row, 8).value,
                         'payload': str(history.cell(row, 12).value or '')}
    return events


def history_state(history):
    """(layout, events) hoặc ContentError. layout 'absent' khi chưa có sheet. / (layout, events) or a refusal."""
    if history is None:
        return 'absent', {}
    layout = history_layout(history)
    if layout == 'unknown':
        raise ContentError('UNSUPPORTED_HISTORY', 'LAW history có định dạng không được biết; không ghi đè',
                           'LAW history has an unknown layout; it is not overwritten')
    if layout == 'legacy' and any(cell.data_type == 'f' for row in history.iter_rows(min_row=2) for cell in row):
        raise ContentError('UNSUPPORTED_HISTORY', 'LAW history có ô công thức; không ghi đè',
                           'LAW history has a formula cell; it is not overwritten')
    return layout, (history_events(history) if layout == 'extended' else {})


def check_registry(wb):
    """B-02: hai sheet LAW artifacts/LAW relations (nếu có) phải hợp lệ trước khi bất kỳ đường ghi sổ nào chạy; không so với sổ hiện tại.
    B-02: the LAW artifacts/LAW relations sheets, when present, must be valid before any index write; never compared with the current catalog."""
    try:
        import artifacts  # lazy: artifacts imports this module / nhập muộn để tránh vòng
    except ImportError as e:  # an incomplete tools folder: fail closed, never skip the check / thiếu module thì dừng, không bỏ qua kiểm
        raise SyncError('tools/artifacts.py cannot be loaded, so the registry sheets cannot be validated and the index is not written / '
                        'Không nạp được tools/artifacts.py nên chưa kiểm được hai sheet registry, chưa ghi sổ: %s' % e)
    artifacts.parse_registry(wb)


def history_layout_for_sync(history):
    """Dùng trong sync: định dạng lạ hoặc Event ID trùng thì dừng, không thay lịch sử. / Used by sync: an unknown layout stops it."""
    try:
        return history_state(history)[0]
    except ContentError as e:
        raise SyncError(str(e))


def history_add(history, values):
    row = max(history.max_row + 1, 2)
    for col, value in enumerate(values, 1):
        if value not in (None, ''):
            put(history, row, col, value)
    return row


def history_extend(history):
    """Mở rộng sheet cũ 5 cột tại chỗ: chỉ thêm tiêu đề cột mới, không đụng dòng cũ. / Extend an old 5-column sheet in place: new headers only."""
    for col, name in enumerate(HISTORY_EXTENDED, 1):
        if col > len(HISTORY_LEGACY):
            put(history, 1, col, name)


# ---- đọc sổ và nguồn / reading the index and the source
def open_index(root):
    _, index = guard_targets(root)
    if not os.path.isfile(index):
        raise SyncError('No index / Chưa có sổ. Run: python tools/library.py init')
    with open(index, 'rb') as f:
        original = f.read()
    opx = library.need_openpyxl()
    try:
        wb = opx.load_workbook(io.BytesIO(original), data_only=False)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
        raise SyncError('Cannot open index / Không mở được sổ: %s. %s' % (e, library.book_steps('unreadable')))
    if library.SHEET not in wb.sheetnames:
        wb.close()
        raise SyncError('Index is missing sheet / Sổ thiếu sheet: ' + library.SHEET + '. ' + library.book_steps('missing_sheet'))
    return original, transaction.sha_bytes(original), wb


def catalog_row(ws, cols, source_id):
    """Dòng duy nhất của SourceID; trùng mã ở bất kỳ dòng nào hoặc không thấy thì từ chối. / The one row of a SourceID; duplicates or absence refuse."""
    seen, found = {}, None
    for row in range(library.HEADER_ROW + 1, ws.max_row + 1):
        ident = str(ws.cell(row, cols['id']).value or '').strip()
        if not ident:
            continue
        if ident in seen:
            raise SyncError(duplicate_id_message(ident, [seen[ident], row]))
        seen[ident] = row
        if ident == source_id:
            found = row
    if found is None:
        raise ContentError('UNKNOWN_SOURCE', 'SourceID không có trong sổ: ' + source_id, 'SourceID is not in the index: ' + source_id)
    return found


def observe_source(root, ws, cols, source_id, expected_revision, expected_sha):
    """Quan sát nguồn được khai: sổ + đúng một file. Revision/SHA kỳ vọng phải khớp cả sổ lẫn bytes file đang đọc.
    Observe the declared source: the index plus exactly one file. Expected revision/SHA must match both the index and the bytes now read."""
    row = catalog_row(ws, cols, source_id)
    revision = library.revision_of(ws.cell(row, cols['LAW revision']).value)
    sha = str(ws.cell(row, cols['LAW SHA-256']).value or '').strip().lower()
    if not (isinstance(revision, int) and revision >= 1 and library.SHA256_RE.fullmatch(sha)):
        raise ContentError('SOURCE_BASIS_MISSING', 'Nguồn %s chưa có revision/SHA hợp lệ trong sổ; chạy sync trước' % source_id,
                           'Source %s has no valid revision/SHA in the index; run sync first' % source_id)
    if revision != expected_revision or sha != expected_sha:
        raise ContentError('STALE_SOURCE_BASIS', 'Revision/SHA kỳ vọng không khớp sổ (sổ: revision %s, SHA %s…)' % (revision, sha[:12]),
                           'The expected revision/SHA does not match the index (index: revision %s, SHA %s...)' % (revision, sha[:12]))
    path = library.norm_path(ws.cell(row, cols['file']).value)
    full, why = library.locate_source(root, path)
    if full is None:
        raise ContentError('SOURCE_UNAVAILABLE', 'Không mở được file nguồn (%s): %s' % (why, path), 'The source file cannot be opened (%s): %s' % (why, path))
    try:
        before = os.stat(full)
        actual = digest(full)
        after = os.stat(full)
    except OSError as e:
        raise ContentError('SOURCE_UNAVAILABLE', 'Không đọc được file nguồn: %s' % e, 'The source file cannot be read: %s' % e)
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise SyncError('Source changed during scan / Nguồn đổi khi quét: ' + path)
    if actual != sha:
        raise ContentError('STALE_SOURCE_BASIS', 'File nguồn đã đổi so với sổ (SHA thực %s…); chạy sync rồi lập lại' % actual[:12],
                           'The source file differs from the index (actual SHA %s...); run sync and prepare again' % actual[:12])
    semantic = {key: library.fmt(ws.cell(row, cols[key]).value) if key in cols else '' for key, _ in library.SEMANTIC_FIELDS}
    return {'row': row, 'revision': revision, 'sha256': sha, 'path': path, 'file_sha256': actual, 'semantic': semantic}


def plan_token(kind, payload, snapshot, observation):
    """Token buộc payload chuẩn hóa + bytes sổ + quan sát nguồn/revision/ngữ nghĩa. Không phải quyền hay biên nhận.
    Binds the normalised payload, the workbook bytes and the source/revision/semantic observation. Not a grant, not a receipt."""
    return hashlib.sha256(canon({'kind': kind, 'payload': payload, 'snapshot': snapshot, 'observation': observation}).encode('utf-8')).hexdigest()


def cell_values(wb):
    out = {}
    for ws in wb.worksheets:
        out[ws.title] = {(c.row, c.column): (c.value, c.data_type) for row in ws.iter_rows() for c in row if c.value is not None}
    return out


def verify_staged(opx, original, staged, allowed):
    """Đọc lại bytes sẽ ghi và so với sổ gốc: mọi ô ngoài vùng được phép phải giữ nguyên (công thức, sheet, dữ liệu người dùng).
    Reload the bytes about to be written: every cell outside the allowed area must be unchanged."""
    old, new = opx.load_workbook(io.BytesIO(original), data_only=False), opx.load_workbook(io.BytesIO(staged), data_only=False)
    try:
        before, after = cell_values(old), cell_values(new)
        for name, cells in before.items():
            if name not in after:
                raise SyncError('Verification of the staged workbook failed: a sheet disappeared / Kiểm bản sẽ ghi không đạt: mất sheet ' + name)
            for key in set(cells) | set(after[name]):
                if cells.get(key) != after[name].get(key) and not allowed(name, key):
                    raise SyncError('Verification of the staged workbook failed: a cell outside the change changed (%s %s) / '
                                    'Kiểm bản sẽ ghi không đạt: có ô ngoài phạm vi thay đổi (%s %s)' % (name, key, name, key))
        return new
    finally:
        old.close()
        new.close()


def save_workbook(wb):
    stream = io.BytesIO()
    wb.save(stream)
    wb.close()
    return stream.getvalue()


def content_plan(root, request):
    """Xem trước ghi một entry nội dung. Chỉ đọc sổ và đúng một file nguồn được khai; không ghi gì, không tạo sheet.
    Preview recording one content entry. Reads the workbook and the one declared source only; writes nothing and creates no sheet."""
    req = content_request(request)
    original, snapshot, wb = open_index(root)
    opx = library.need_openpyxl()
    try:
        history_state(wb['LAW history'] if 'LAW history' in wb.sheetnames else None)
        check_registry(wb)
        present = library.CONTENT_SHEET in wb.sheetnames
        entries = library.parse_content(wb[library.CONTENT_SHEET]) if present else []
        by_id = {e['entry_id']: e for e in entries}
        extra = {'entry_id': req['entry_id'], 'source_id': req['source_id'], 'sheet_created': not present}
        found = by_id.get(req['entry_id'])
        if found is not None:
            if {k: found[k] for k in library.CONTENT_REQUEST_KEYS} == req:
                return dict(extra, action='already_recorded', snapshot=snapshot, bytes=None, notices=[], sources={}, observation=None,
                            plan_token=plan_token('content', req, snapshot, None), sheet_created=False)
            raise ContentError('ENTRY_CONFLICT', 'entry_id %s đã có với nội dung khác; dùng EntryID mới và supersedes' % req['entry_id'],
                               'entry_id %s already exists with a different payload; use a new EntryID and supersedes' % req['entry_id'])
        ws = wb[library.SHEET]
        cols = columns(ws)
        seen = observe_source(root, ws, cols, req['source_id'], req['source_revision'], req['source_sha256'])
        target = req['supersedes']
        if target:
            old = by_id.get(target)
            if old is None or old['source_id'] != req['source_id']:
                raise ContentError('BAD_SUPERSEDES', 'supersedes phải trỏ entry đã có cùng SourceID', 'supersedes must point to an existing entry of the same SourceID')
            if any(e['supersedes'] == target for e in entries):
                raise ContentError('BAD_SUPERSEDES', 'entry %s đã bị thay thế; nhánh mơ hồ' % target, 'entry %s is already superseded; ambiguous branch' % target)
        for e in entries:
            if e['source_id'] == req['source_id'] and e['source_revision'] == seen['revision'] and (
                    e['source_sha256'] != seen['sha256'] or
                    any(e[snap] != seen['semantic'][key] for key, snap in library.SEMANTIC_FIELDS)):
                raise ContentError('UNVERSIONED_SEMANTIC_CHANGE',
                                   'Cùng revision %s nhưng metadata ngữ nghĩa/SHA trong sổ khác lúc entry %s được ghi; cần source-event explicit trước'
                                   % (seen['revision'], e['entry_id']),
                                   'Same revision %s but the semantic metadata/SHA in the index differs from when entry %s was recorded; '
                                   'an explicit source-event is needed first' % (seen['revision'], e['entry_id']))
        if present:
            sheet = wb[library.CONTENT_SHEET]
            row = max([e['_row'] for e in entries] + [library.CONTENT_HEADER_ROW]) + 1
        else:
            sheet = wb.create_sheet(library.CONTENT_SHEET)
            put(sheet, 1, 1, library.CONTENT_MARKER)
            for col, name in enumerate(library.CONTENT_HEADERS, 1):
                put(sheet, library.CONTENT_HEADER_ROW, col, name)
            row = library.CONTENT_HEADER_ROW + 1
        recorded = dict(req, source_path=seen['path'], recorded_at=datetime.datetime.now().replace(microsecond=0).isoformat(),
                        **{snap: seen['semantic'][key] for key, snap in library.SEMANTIC_FIELDS})
        for col, name in enumerate(library.CONTENT_HEADERS, 1):
            if recorded[name] != '':
                put(sheet, row, col, recorded[name])
        staged = save_workbook(wb)
        wb = None
        check = opx.load_workbook(io.BytesIO(staged), data_only=False)
        try:
            again = {e['entry_id']: e for e in library.parse_content(check[library.CONTENT_SHEET])}
        finally:
            check.close()
        if {k: again[req['entry_id']][k] for k in library.CONTENT_REQUEST_KEYS} != req or len(again) != len(entries) + 1:
            raise SyncError('Verification of the staged workbook failed: the entry does not read back as written / '
                            'Kiểm bản sẽ ghi không đạt: entry đọc lại không đúng như đã ghi')
        verify_staged(opx, original, staged, lambda name, key: name == library.CONTENT_SHEET)
        observation = {k: seen[k] for k in ('revision', 'sha256', 'path', 'file_sha256', 'semantic')}
        return dict(extra, action='record', snapshot=snapshot, bytes=staged, notices=lossy_notices(original), observation=observation,
                    sources={seen['path']: seen['file_sha256']}, plan_token=plan_token('content', req, snapshot, observation),
                    row=row)
    finally:
        if wb is not None:
            wb.close()


def event_plan(root, request):
    """Xem trước một source-event explicit. Chỉ đọc sổ và đúng một file nguồn được khai. / Preview one explicit source-event."""
    req = event_request(request)
    original, snapshot, wb = open_index(root)
    opx = library.need_openpyxl()
    try:
        if library.CONTENT_SHEET in wb.sheetnames:
            library.parse_content(wb[library.CONTENT_SHEET])
        check_registry(wb)
        history = wb['LAW history'] if 'LAW history' in wb.sheetnames else None
        layout, events = history_state(history)
        text = canon(req)
        extra = {'event_id': req['event_id'], 'source_id': req['source_id'], 'mode': req['mode']}
        prior = events.get(req['event_id'])
        if prior is not None:
            if prior['payload'] == text:
                return dict(extra, action='already_recorded', snapshot=snapshot, bytes=None, notices=[], sources={}, observation=None,
                            revision_after=prior['new_revision'], current_basis_validated=False,
                            plan_token=plan_token('event', req, snapshot, None))
            raise ContentError('EVENT_CONFLICT', 'event_id %s đã ghi với nội dung khác' % req['event_id'],
                               'event_id %s was already recorded with a different payload' % req['event_id'])
        ws = wb[library.SHEET]
        cols = columns(ws)
        seen = observe_source(root, ws, cols, req['source_id'], req['expected_revision'], req['expected_sha256'])
        missing = [k for k in req['changes'] if k not in cols]
        if missing:
            raise ContentError('CATALOG_COLUMN_MISSING', 'Sổ thiếu cột: ' + ', '.join(missing), 'The index lacks column(s): ' + ', '.join(missing))
        differing = {k: v for k, v in req['changes'].items() if v != seen['semantic'][k]}
        observation = {k: seen[k] for k in ('revision', 'sha256', 'path', 'file_sha256', 'semantic')}
        extra.update(revision_before=seen['revision'], observed_before=seen['semantic'])
        if req['mode'] == 'semantic_update' and not differing:
            return dict(extra, action='no_change', snapshot=snapshot, bytes=None, notices=[], sources={seen['path']: seen['file_sha256']},
                        observation=observation, revision_after=seen['revision'], plan_token=plan_token('event', req, snapshot, observation))
        row, observed = seen['row'], datetime.date.today().isoformat()
        verify_before = ws.cell(row, cols['verify']).value
        for key, value in differing.items():
            put(ws, row, cols[key], value)
        new_revision = seen['revision'] + 1
        put(ws, row, cols['LAW revision'], new_revision)
        put(ws, row, cols['verify'], 'Cần đối chiếu')
        put(ws, row, cols['LAW file state'], 'NEEDS_REVIEW')
        put(ws, row, cols['LAW observed'], observed)
        if history is None:
            history = wb.create_sheet('LAW history')
            for col, name in enumerate(HISTORY_EXTENDED, 1):
                put(history, 1, col, name)
        elif layout == 'legacy':
            history_extend(history)
        history_row = history_add(history, (req['source_id'], seen['revision'], seen['sha256'], verify_before, observed, req['event_id'],
                                            EVENT_KINDS[req['mode']], new_revision, req['reason'], req['evidence_ref'],
                                            req['recorded_by'], text) + tuple(seen['semantic'][k] for k in EVENT_CHANGE_KEYS))
        staged = save_workbook(wb)
        wb = None
        check = opx.load_workbook(io.BytesIO(staged), data_only=False)
        try:
            back = history_events(check['LAW history']).get(req['event_id'])
            revision_back = library.revision_of(check[library.SHEET].cell(row, cols['LAW revision']).value)
        finally:
            check.close()
        if back is None or back['payload'] != text or revision_back != new_revision:
            raise SyncError('Verification of the staged workbook failed: the event does not read back as written / '
                            'Kiểm bản sẽ ghi không đạt: sự kiện đọc lại không đúng như đã ghi')
        touched = {cols[k] for k in differing} | {cols['LAW revision'], cols['verify'], cols['LAW file state'], cols['LAW observed']}
        verify_staged(opx, original, staged, lambda name, key: (name == library.SHEET and key[0] == row and key[1] in touched) or
                      (name == 'LAW history' and (key[0] == history_row or (key[0] == 1 and key[1] > len(HISTORY_LEGACY)))))
        return dict(extra, action='event', snapshot=snapshot, bytes=staged, notices=lossy_notices(original), observation=observation,
                    sources={seen['path']: seen['file_sha256']}, revision_after=new_revision,
                    plan_token=plan_token('event', req, snapshot, observation))
    finally:
        if wb is not None:
            wb.close()


def check_plan_token(token):
    if not (isinstance(token, str) and library.SHA256_RE.fullmatch(token)):
        raise PreviewMismatch('The plan token is missing or malformed; preview again before applying / '
                              'Mã kế hoạch thiếu hoặc sai cấu trúc; xem trước lại rồi mới ghi.', 'invalid')
    return token


def commit_planned(root, make_plan, token, operation):
    """Ghi đúng bản đã xem: plan tính lại dưới khóa phải ra cùng token (sổ, payload, nguồn, ngữ nghĩa chưa đổi), trước mọi Transaction.
    Write exactly what was previewed: the plan recomputed under the lock must produce the same token, before any Transaction."""
    token = check_plan_token(token)

    def check(result):
        if result['plan_token'] != token:
            raise PreviewMismatch('The workbook, the declared source or the request changed after the preview; LAW did not change the index, '
                                  'and no new file transaction was created; preview again / '
                                  'Sổ, nguồn được khai hoặc yêu cầu đã đổi sau bản xem trước; LAW không sửa sổ, chưa tạo giao dịch file mới; '
                                  'xem trước lại.', 'plan')

    def recheck(result):
        for path, sha in result['sources'].items():
            full, why = library.locate_source(root, path)
            if full is None or digest(full) != sha:
                raise SyncError('Source changed while preparing / Nguồn đổi khi chuẩn bị ghi; xem lại và chạy lại: ' + path)

    return locked_commit(root, make_plan, check=check, recheck=recheck, operation=operation)


def content_apply(root, request, expect_plan):
    return commit_planned(root, lambda: content_plan(root, request), expect_plan, 'library-content')


def event_apply(root, request, expect_plan):
    return commit_planned(root, lambda: event_plan(root, request), expect_plan, 'library-source-event')
