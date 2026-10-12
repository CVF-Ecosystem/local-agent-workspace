#!/usr/bin/env python3
"""Thư viện nguồn của project: khung thư mục references/ và chỉ mục references/_INDEX.xlsx.
Source library of a project: the references/ folder layout and the references/_INDEX.xlsx index.

Dùng / Usage (chạy từ thư mục gốc của project / run from the project root):
  python tools/library.py init                 tạo khung thư mục và chỉ mục nếu chưa có (không ghi đè)
                                               create the folders and the index if missing (never overwrites)
  python tools/library.py check [--days 180]   kiểm chỉ mục: thiếu file, file chưa vào chỉ mục, trùng số hiệu,
                                               tình trạng mâu thuẫn, ngày kiểm quá cũ / check the index
  python tools/library.py find <từ khóa> [--group "Pháp luật"] [--all]
                                               tìm theo số hiệu, trích yếu, lĩnh vực, điều (không phân biệt dấu)
                                               search number, title, domain, articles (accent-insensitive)
  python tools/library.py stats                đếm theo nhóm và tình trạng / counts by group and status
  Thêm --json để lấy kết quả dạng JSON (bảng điều khiển dùng) / add --json for JSON output.

Chỉ đọc sheet "Danh mục"; sheet "Ví dụ" chỉ để xem. Không xóa, không sửa file của người dùng (init chỉ tạo cái còn thiếu).
Reads only the "Danh mục" sheet. Never deletes or edits user files (init only creates what is missing).
Cần Python 3.8+ và openpyxl (pip install openpyxl). Không dùng mạng. / Needs Python 3.8+ and openpyxl. No network.
"""
import datetime, io, json, os, re, shutil, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, 'references')
INDEX = os.path.join(REF, '_INDEX.xlsx')
TEMPLATE = os.path.join(ROOT, 'skills', 'local', 'shared', 'source-library', 'assets', 'source-index-template.xlsx')
SHEET = 'Danh mục'
HEADER_ROW = 4
FILE_EXT = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.xlsm', '.odt', '.ods', '.rtf', '.txt', '.md', '.html', '.htm',
            '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.ppt', '.pptx', '.zip')
GROUP_DIRS = {  # nhóm -> thư mục / group -> folder
    'legal': ('Pháp luật', 'Văn bản quy phạm pháp luật và văn bản của cơ quan nhà nước, chia theo lĩnh vực: legal/<linh-vuc>/.',
              'Laws, decrees, circulars and other state documents, one sub-folder per domain: legal/<domain>/.'),
    'policies': ('Nội bộ', 'Quy chế, nội quy, quy định, quyết định nội bộ của đơn vị, chia theo mảng: policies/<mang>/.',
                 'The organisation\'s own rules, regulations and internal decisions, one sub-folder per area: policies/<area>/.'),
    'templates': ('Mẫu biểu', 'Mẫu văn bản, biểu mẫu, mẫu báo cáo đã duyệt: templates/<mang>/.',
                  'Approved document, form and report templates: templates/<area>/.'),
    'source-documents': ('Tài liệu nguồn', 'Tài liệu nghiệp vụ khác dùng làm nguồn: hồ sơ, số liệu, tài liệu tham khảo.',
                         'Other business documents used as sources: case files, data, reference material.'),
}
# khóa cột -> tiền tố tiêu đề (phần tiếng Việt) / column key -> header prefix
KEYS = {
    'id': 'Mã', 'group': 'Nhóm', 'domain': 'Lĩnh vực', 'issuer': 'Cơ quan', 'number': 'Số, ký hiệu', 'type': 'Loại văn bản',
    'issued': 'Ngày ban hành', 'effective': 'Ngày có hiệu lực', 'title': 'Trích yếu', 'replaces': 'Thay thế',
    'replaced_by': 'Bị thay thế', 'status': 'Tình trạng', 'checked': 'Ngày kiểm', 'verify': 'Mức độ xác minh',
    'fulltext': 'Có toàn văn', 'file': 'Đường dẫn file', 'articles': 'Điều', 'sensitivity': 'Mức nhạy cảm',
    'used_by': 'Gói', 'url': 'Nguồn', 'notes': 'Ghi chú',
}
LANG = 'vi'


def L(vi, en):
    return en if LANG == 'en' else vi


def fold(s):
    s = unicodedata.normalize('NFD', str(s or '')).replace('đ', 'd').replace('Đ', 'D')
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().strip()


def need_openpyxl():
    try:
        import openpyxl  # noqa: F401
        return openpyxl
    except ImportError:
        sys.exit(L('Cần openpyxl: chạy "pip install openpyxl" rồi thử lại.', 'openpyxl is required: run "pip install openpyxl" and retry.'))


def as_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', str(v or ''))
    if m:
        try:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    return None


def fmt(v):
    d = as_date(v) if isinstance(v, (datetime.date, datetime.datetime)) else None
    return d.strftime('%d/%m/%Y') if d else ('' if v is None else str(v).strip())


def load():
    opx = need_openpyxl()
    if not os.path.isfile(INDEX):
        sys.exit(L('Chưa có references/_INDEX.xlsx. Chạy: python tools/library.py init',
                   'references/_INDEX.xlsx not found. Run: python tools/library.py init'))
    wb = opx.load_workbook(INDEX, data_only=True, read_only=True)
    if SHEET not in wb.sheetnames:
        sys.exit(L('Chỉ mục thiếu sheet "%s".', 'The index has no "%s" sheet.') % SHEET)
    ws = wb[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < HEADER_ROW:
        return {}, []
    header = [str(h or '') for h in rows[HEADER_ROW - 1]]
    cols = {}
    for k, pre in KEYS.items():
        for i, h in enumerate(header):
            if h.startswith(pre) and i not in cols.values():
                cols[k] = i
                break
    data = []
    for n, r in enumerate(rows[HEADER_ROW:], HEADER_ROW + 1):
        if not any(c not in (None, '') for c in r):
            continue
        rec = {k: (r[i] if i < len(r) else None) for k, i in cols.items()}
        rec['_row'] = n
        data.append(rec)
    return cols, data


def library_files():
    out = []
    if not os.path.isdir(REF):
        return out
    for d, dirs, files in os.walk(REF):
        dirs[:] = [x for x in dirs if not x.startswith(('.', '_'))]
        for f in files:
            if f.startswith(('~$', '.', '_INDEX')) or f == 'README.md':
                continue
            if f.lower().endswith(FILE_EXT):
                out.append(os.path.relpath(os.path.join(d, f), REF).replace(os.sep, '/'))
    return sorted(out)


def norm_path(p):
    s = str(p or '').strip().replace('\\', '/')
    s = re.sub(r'^\./', '', s)
    return re.sub(r'^references/', '', s)


# ---------------------------------------------------------------- lệnh / commands
def cmd_init(args):
    made = []
    os.makedirs(REF, exist_ok=True)
    for d, (grp, vi, en) in GROUP_DIRS.items():
        p = os.path.join(REF, d)
        if not os.path.isdir(p):
            os.makedirs(p)
            made.append('references/%s/' % d)
        rd = os.path.join(p, 'README.md')
        if not os.path.isfile(rd):
            io.open(rd, 'w', encoding='utf-8', newline='\n').write(
                '# references/%s/\n\nNhóm "%s" trong chỉ mục `references/_INDEX.xlsx`. %s\n\n%s\n\n'
                'Mỗi lĩnh vực một thư mục con, tên không dấu, nối bằng gạch ngang. Thư mục con có thể có README ngắn: phạm vi, người cập nhật, '
                'nguồn chính thống. Thêm file thì thêm dòng vào chỉ mục; xem skill `source-library`.\n' % (d, grp, vi, en))
            made.append('references/%s/README.md' % d)
    if not os.path.isfile(INDEX):
        if not os.path.isfile(TEMPLATE):
            sys.exit(L('Thiếu mẫu chỉ mục: %s', 'Index template missing: %s') % os.path.relpath(TEMPLATE, ROOT))
        shutil.copy2(TEMPLATE, INDEX)
        made.append('references/_INDEX.xlsx')
    out = {'created': made}
    if args.get('json'):
        print(json.dumps(out, ensure_ascii=False))
        return 0
    if made:
        print(L('Đã tạo:', 'Created:'))
        for m in made:
            print('  - ' + m)
    else:
        print(L('Khung thư viện đã có đủ; không tạo gì.', 'The library is already set up; nothing created.'))
    print(L('Tiếp theo: đặt file vào thư mục nhóm/lĩnh vực, thêm dòng vào sheet "Danh mục", rồi chạy python tools/library.py check.',
            'Next: put files in group/domain folders, add rows to the "Danh mục" sheet, then run python tools/library.py check.'))
    return 0


def cmd_check(args):
    cols, data = load()
    days = int(args.get('days') or 180)
    today = datetime.date.today()
    errs, warns = [], []
    missing_cols = [KEYS[k] for k in ('group', 'number', 'title', 'status', 'fulltext', 'file') if k not in cols]
    if missing_cols:
        errs.append((0, L('Chỉ mục thiếu cột: %s', 'Index is missing columns: %s') % ', '.join(missing_cols)))
    seen = {}
    indexed = set()
    for r in data:
        n = r['_row']
        num = str(r.get('number') or '').strip()
        if not (num or str(r.get('title') or '').strip()):
            errs.append((n, L('thiếu cả Số, ký hiệu lẫn Trích yếu', 'both Number and Title are empty')))
        if not r.get('group'):
            warns.append((n, L('chưa ghi Nhóm', 'Group is empty')))
        key = fold(num)
        if key and not key.startswith('['):
            if key in seen:
                errs.append((n, L('trùng Số, ký hiệu "%s" với dòng %d', 'duplicate Number "%s" (row %d)') % (num, seen[key])))
            else:
                seen[key] = n
        path = norm_path(r.get('file'))
        ft = fold(r.get('fulltext'))
        if path:
            indexed.add(path)
            if '[' in path:
                warns.append((n, L('đường dẫn file còn chỗ trống: %s', 'file path has a placeholder: %s') % path))
            elif not os.path.isfile(os.path.join(REF, *path.split('/'))):
                (errs if ft == 'co' else warns).append((n, L('không thấy file references/%s', 'file not found: references/%s') % path))
        if fold(r.get('verify')) == 'da doi chieu toan van' and not (path and os.path.isfile(os.path.join(REF, *path.split('/')))):
            warns.append((n, L('ghi "Đã đối chiếu toàn văn" nhưng không có file trong thư viện', '"checked against full text" but no file in the library')))
        if ft == 'co' and not path:
            errs.append((n, L('Có toàn văn = Có nhưng không có đường dẫn file', 'Full text = Có but no file path')))
        if path and ft != 'co' and os.path.isfile(os.path.join(REF, *path.split('/'))):
            warns.append((n, L('có file nhưng cột Có toàn văn chưa ghi "Có"', 'file exists but Full text is not "Có"')))
        st = fold(r.get('status'))
        rb = str(r.get('replaced_by') or '').strip()
        if st == 'con hieu luc' and rb and rb not in ('—', '-'):
            d = as_date(rb)
            if d is None or d <= today:
                warns.append((n, L('Tình trạng "Còn hiệu lực" nhưng có ghi bị thay thế: %s', 'status "in force" but replaced by: %s') % rb))
        if not st:
            warns.append((n, L('chưa ghi Tình trạng', 'Status is empty')))
        chk = as_date(r.get('checked'))
        if r.get('group') and fold(r.get('group')) == 'phap luat':
            if chk is None:
                warns.append((n, L('văn bản pháp luật chưa ghi Ngày kiểm tình trạng', 'legal document without a status check date')))
            elif (today - chk).days > days:
                warns.append((n, L('kiểm tình trạng lần cuối %s, quá %d ngày', 'status last checked %s, over %d days ago') % (fmt(chk), days)))
        if fold(r.get('verify')) == 'can doi chieu':
            warns.append((n, L('mức độ xác minh: Cần đối chiếu', 'verification: needs checking')))
        if fold(r.get('sensitivity')) == 'mat':
            warns.append((n, L('văn bản Mật: không đưa lên dịch vụ đám mây', 'confidential: do not upload to cloud services')))
    unindexed = [f for f in library_files() if f not in indexed]
    for f in unindexed:
        warns.append((0, L('file chưa có trong chỉ mục: references/%s', 'file not in the index: references/%s') % f))
    out = {'rows': len(data), 'errors': [{'row': n, 'msg': m} for n, m in errs], 'warnings': [{'row': n, 'msg': m} for n, m in warns],
           'unindexed': unindexed}
    if args.get('json'):
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(L('Chỉ mục: %d dòng (sheet "%s").', 'Index: %d rows ("%s" sheet).') % (len(data), SHEET))
        for tag, lst in ((L('LỖI', 'ERROR'), errs), (L('CẢNH BÁO', 'WARNING'), warns)):
            for n, m in lst:
                print('%s%s: %s' % (tag, (L(' dòng %d', ' row %d') % n) if n else '', m))
        print(L('\n%s: %d lỗi, %d cảnh báo.', '\n%s: %d errors, %d warnings.') % (L('ĐẠT', 'PASS') if not errs else L('KHÔNG ĐẠT', 'FAIL'), len(errs), len(warns)))
    return 1 if errs else 0


def show(r):
    path = norm_path(r.get('file'))
    has = fold(r.get('fulltext')) == 'co' and path and os.path.isfile(os.path.join(REF, *path.split('/')))
    return {'row': r['_row'], 'id': fmt(r.get('id')), 'group': fmt(r.get('group')), 'number': fmt(r.get('number')),
            'type': fmt(r.get('type')), 'title': fmt(r.get('title')), 'status': fmt(r.get('status')),
            'checked': fmt(r.get('checked')), 'verify': fmt(r.get('verify')), 'effective': fmt(r.get('effective')),
            'replaced_by': fmt(r.get('replaced_by')), 'articles': fmt(r.get('articles')),
            'file': ('references/' + path) if path else '', 'fulltext': bool(has)}


def cmd_find(args):
    q = fold(args.get('query') or '')
    if not q:
        sys.exit(L('Cần từ khóa. Ví dụ: python tools/library.py find "30/2020"', 'A keyword is required. Example: python tools/library.py find "30/2020"'))
    _, data = load()
    grp = fold(args.get('group') or '')
    words = q.split()
    hits = []
    for r in data:
        if grp and fold(r.get('group')) != grp:
            continue
        hay = fold(' '.join(str(r.get(k) or '') for k in ('id', 'number', 'title', 'domain', 'issuer', 'type', 'articles', 'notes', 'used_by')))
        if all(w in hay for w in words):
            hits.append(show(r))
    limit = None if args.get('all') else 30
    if args.get('json'):
        print(json.dumps({'query': args.get('query'), 'count': len(hits), 'hits': hits[:limit]}, ensure_ascii=False))
        return 0
    if not hits:
        print(L('Không thấy văn bản khớp "%s" trong chỉ mục. Chưa có trong thư viện thì không trích nguyên văn; tra nguồn chính thống và thêm vào chỉ mục.',
                'No document matches "%s". Not in the library means no verbatim quotes; look it up officially and add it to the index.') % args.get('query'))
        return 0
    print(L('%d văn bản khớp "%s":', '%d documents match "%s":') % (len(hits), args.get('query')))
    for h in hits[:limit]:
        print('- [%s %d] %s - %s' % (L('dòng', 'row'), h['row'], ' '.join(x for x in (h['type'], h['number']) if x), h['title']))
        print('    %s: %s%s | %s: %s | %s: %s' % (
            L('Tình trạng', 'Status'), h['status'] or '?', (' (%s %s)' % (L('kiểm', 'checked'), h['checked'])) if h['checked'] else '',
            L('Xác minh', 'Verified'), h['verify'] or '?',
            L('Toàn văn', 'Full text'), h['file'] if h['fulltext'] else L('không có, không trích nguyên văn', 'none, no verbatim quotes')))
        if h['replaced_by']:
            print('    %s: %s' % (L('Bị thay thế bởi', 'Replaced by'), h['replaced_by']))
        if h['articles']:
            print('    %s: %s' % (L('Điều hay dùng', 'Key articles'), h['articles']))
    if limit and len(hits) > limit:
        print(L('... còn %d dòng; thêm --all để xem hết.', '... %d more; add --all to see all.') % (len(hits) - limit))
    return 0


def cmd_stats(args):
    _, data = load()
    groups = {}
    for r in data:
        g = fmt(r.get('group')) or L('(chưa ghi nhóm)', '(no group)')
        s = fmt(r.get('status')) or L('(chưa ghi)', '(empty)')
        groups.setdefault(g, {}).setdefault(s, 0)
        groups[g][s] += 1
    no_ft = sum(1 for r in data if fold(r.get('fulltext')) != 'co')
    verify = sum(1 for r in data if fold(r.get('verify')) == 'can doi chieu')
    out = {'rows': len(data), 'groups': groups, 'no_fulltext': no_ft, 'needs_check': verify,
           'files': len(library_files()), 'index': os.path.isfile(INDEX)}
    if args.get('json'):
        print(json.dumps(out, ensure_ascii=False))
        return 0
    print(L('Chỉ mục: %d văn bản; %d file trong references/; %d chưa có toàn văn; %d cần đối chiếu.',
            'Index: %d documents; %d files in references/; %d without full text; %d need checking.') % (len(data), out['files'], no_ft, verify))
    for g, st in groups.items():
        print('- %s: %s' % (g, ', '.join('%s %d' % (k, v) for k, v in st.items())))
    return 0


def main(argv):
    global LANG
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    try:
        info = json.load(io.open(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json'), encoding='utf-8'))
        LANG = 'en' if info.get('language') == 'en' else 'vi'
    except (OSError, ValueError):
        pass
    if '--lang' in argv:
        i = argv.index('--lang')
        LANG = argv[i + 1] if i + 1 < len(argv) else LANG
        del argv[i:i + 2]
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    args = {'json': '--json' in rest, 'all': '--all' in rest}
    rest = [a for a in rest if a not in ('--json', '--all')]
    for opt in ('--days', '--group'):
        if opt in rest:
            i = rest.index(opt)
            args[opt[2:]] = rest[i + 1] if i + 1 < len(rest) else ''
            del rest[i:i + 2]
    args['query'] = ' '.join(rest)
    fn = {'init': cmd_init, 'check': cmd_check, 'find': cmd_find, 'stats': cmd_stats}.get(cmd)
    if not fn:
        print(L('Lệnh không có: %s. Dùng: init | check | find | stats', 'Unknown command: %s. Use: init | check | find | stats') % cmd)
        return 2
    return fn(args)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
