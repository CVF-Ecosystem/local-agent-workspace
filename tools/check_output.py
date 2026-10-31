#!/usr/bin/env python3
"""Kiểm tra nhanh một sản phẩm trước khi giao: còn chỗ chưa điền, còn nhãn mẫu minh họa, tài nguyên mạng trong HTML...
Quick pre-delivery check of a deliverable: unfilled placeholders, leftover demo labels, network resources in HTML...

Dùng / Usage:
  python tools/check_output.py <file> [<file> ...] [--lang vi|en] [--profile auto|nd30|none]
  (.docx: ngoài chữ còn kiểm bố cục; --profile nd30 ép kiểm thể thức Nghị định 30/2020/NĐ-CP / .docx layout is checked too)
  python tools/check_output.py --declaration <reply.txt|.md>   (kiểm khối "Khai báo thực hiện" / check the "Execution declaration" block)

Hỗ trợ: .md .txt .html .docx .csv .xlsx (CSV/Excel được chuyển cho skill spreadsheet-check). Chỉ đọc, không sửa file.
Mã thoát: 0 đã kiểm đạt; 1 đã kiểm có vấn đề/cần xem xét; 2 chưa kiểm được ít nhất một file.
Python 3.8+; Excel cần openpyxl. Không dùng mạng.
Đây là kiểm tra cơ học, không thay thế việc đọc lại và đối chiếu số liệu với nguồn.
"""
import argparse, io, os, re, subprocess, sys, zipfile
import importlib.util
import xml.etree.ElementTree as ET
from result_schema import emit, make

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = 'vi'
def L(vi, en): return en if LANG == 'en' else vi

PLACEHOLDER = re.compile(r'\[([^\[\]\n]{2,80})\](?!\()')
FLAG = re.compile(r'(cần xác nhận|chưa xác nhận|to be confirmed|needs? confirmation|TBC|TBD)', re.I)
DEMO = re.compile(r'(MẪU MINH HỌA|DỮ LIỆU MINH HỌA|ILLUSTRATIVE (TEMPLATE|DATA)|dữ liệu giả|fake data)', re.I)

def text_of(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.docx':
        with zipfile.ZipFile(path) as z:
            parts = ['word/document.xml'] + sorted(n for n in z.namelist() if
                re.fullmatch(r'word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml', n))
            texts = []
            ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
            for part in parts:
                root = ET.fromstring(z.read(part))
                for p in root.iter(ns + 'p'):
                    texts.append(''.join(e.text or '' for e in p.iter(ns + 't')))
            return '\n'.join(texts)
    return io.open(path, encoding='utf-8').read()

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
# Mechanical subset of the local nd30-presentation.md reference, not legal certification.
# Keep these stdlib-only rules independent of the optional HTML renderer.
ND30_RULES = {'margins_mm': {'top': (20, 25), 'bottom': (20, 25), 'left': (30, 35), 'right': (15, 20)},
              'font': 'Times New Roman', 'body_pt': (13, 14)}
QUOC_HIEU = 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM'

def _rp(rpr):
    """(phông, cỡ nửa điểm) trong w:rPr / (font, size in half-points) of a w:rPr."""
    f = s = None
    if rpr is not None:
        rf, sz = rpr.find(W + 'rFonts'), rpr.find(W + 'sz')
        if rf is not None:
            f = rf.get(W + 'ascii') or rf.get(W + 'hAnsi')
            if not f and (rf.get(W + 'asciiTheme') or rf.get(W + 'hAnsiTheme')):
                f = '@' + (rf.get(W + 'asciiTheme') or rf.get(W + 'hAnsiTheme'))  # phông theo chủ đề / theme font
        if sz is not None and (sz.get(W + 'val') or '').isdigit():
            s = int(sz.get(W + 'val'))
    return f, s

def _styles(z):
    st = {}
    try:
        root = ET.fromstring(z.read('word/styles.xml'))
    except KeyError:
        return st
    dd = root.find(W + 'docDefaults/' + W + 'rPrDefault/' + W + 'rPr')
    st['_default'] = _rp(dd) + (None,)
    for s in root.iter(W + 'style'):
        b = s.find(W + 'basedOn')
        st[s.get(W + 'styleId')] = _rp(s.find(W + 'rPr')) + (b.get(W + 'val') if b is not None else None,)
    return st

def _eff(st, sid, idx, defaults=True):
    """Giá trị phông (0) hoặc cỡ (1) có hiệu lực của một kiểu, đi theo basedOn / effective font (0) or size (1) of a style."""
    seen = 0
    sid = sid or 'Normal'
    while sid in st and seen < 8:
        if st[sid][idx] is not None:
            return st[sid][idx]
        sid, seen = st[sid][2], seen + 1
    return st.get('_default', (None, None, None))[idx] if defaults else None

def _ptext(p):
    out = []
    for e in p.iter():
        if e.tag == W + 't':
            out.append(e.text or '')
        elif e.tag in (W + 'tab', W + 'br'):
            out.append(' ')
    return re.sub(r'\s+', ' ', ''.join(out)).strip()

def _segments(p):
    """Các đoạn chữ của một đoạn văn, cắt tại ngắt dòng cứng (không tính ngắt trang) / text segments split at hard line breaks."""
    segs, cur = [], []
    for e in p.iter():
        if e.tag == W + 't':
            cur.append(e.text or '')
        elif e.tag == W + 'br' and e.get(W + 'type') in (None, 'textWrapping'):
            segs.append(''.join(cur)); cur = []
    segs.append(''.join(cur))
    return [s.strip() for s in segs]

def check_docx_layout(path, profile='auto'):
    """Bố cục .docx, độc lập với công cụ tạo ra file / layout checks that do not depend on how the file was made.
    Mọi file (trừ none): ngắt dòng cứng giữa câu, đoạn lặp sau bảng, dòng trống thay giãn đoạn.
    Văn bản hành chính (có Quốc hiệu, hoặc --profile nd30): lề, phông, cỡ chữ, số trang theo nd30-presentation.md."""
    if profile not in ('auto', 'nd30', 'none'):
        raise ValueError('Unsupported layout profile: %s' % profile)
    must, note = [], []
    with zipfile.ZipFile(path) as z:
        doc = ET.fromstring(z.read('word/document.xml'))
        st = _styles(z)
        page_instructions = []
        for name in z.namelist():
            if re.fullmatch(r'word/(?:header|footer)\d+\.xml', name):
                part = ET.fromstring(z.read(name))
                page_instructions.append(''.join(t.text or '' for t in part.iter(W + 'instrText')))
                page_instructions.extend(t.get(W + 'instr', '') for t in part.iter(W + 'fldSimple'))
        theme = {}
        for n in z.namelist():
            if re.fullmatch(r'word/theme/theme\d+\.xml', n):
                tx = z.read(n).decode('utf-8', 'replace')
                for kind in ('major', 'minor'):
                    m_ = re.search(r'<a:%sFont>\s*<a:latin typeface="([^"]*)"' % kind, tx)
                    if m_:
                        theme[kind] = m_.group(1)
                break
    body = doc.find(W + 'body')
    if body is None:
        return [L('thiếu thân tài liệu DOCX; chưa kiểm được bố cục', 'DOCX body missing; layout not checked')], note
    if profile == 'none':
        return must, note
    alltext = re.sub(r'\s+', ' ', ' '.join(_ptext(p) for p in body.iter(W + 'p'))).upper()
    admin = profile == 'nd30' or QUOC_HIEU in alltext
    # khổ giấy / paper size
    sect = body.find(W + 'sectPr')
    pg = sect.find(W + 'pgSz') if sect is not None else None
    if admin and pg is None:
        note.append(L('chưa khai báo khổ giấy', 'no paper size declared'))
    elif admin:
        try:
            dims = sorted((int(pg.get(W + 'w')), int(pg.get(W + 'h'))))
        except (TypeError, ValueError):
            dims = None
        if dims is None:
            must.append(L('khổ giấy không hợp lệ', 'invalid paper dimensions'))
        elif not (abs(dims[0] - 11906) <= 60 and abs(dims[1] - 16838) <= 60):
            must.append(L('khổ giấy không phải A4 (%.1f x %.1f cm)', 'paper is not A4 (%.1f x %.1f cm)') % (dims[0] * 2.54 / 1440, dims[1] * 2.54 / 1440))
    # ngắt dòng cứng giữa câu / hard line breaks inside a sentence
    bad, ex = 0, ''
    for p in body.iter(W + 'p'):
        segs = _segments(p)
        for a, b in zip(segs, segs[1:]):
            if a and b and not re.search(r'[.;:!?”")\]]$', a) and b[:1].islower():
                bad += 1
                ex = ex or ('"%s ⏎ %s"' % (a[-25:], b[:25]))
                break
    if bad >= 3:
        must.append(L('có %d đoạn bị ngắt dòng cứng giữa câu (ví dụ %s); nên để Word tự xuống dòng',
                      '%d paragraph(s) have a hard line break inside a sentence (for example %s); let Word wrap the lines') % (bad, ex))
    # đoạn lặp ngay sau bảng / paragraphs that repeat the text of the table just above
    pool, dup, exd = '', 0, ''
    for ch in body:
        if ch.tag == W + 'tbl':
            pool = _ptext(ch)
        elif ch.tag == W + 'p':
            t = _ptext(ch)
            if not t:
                continue
            if pool and len(t) >= 20 and t in pool:
                dup += 1
                exd = exd or t[:40]
            else:
                pool = ''
    if dup >= 2:
        must.append(L('có %d đoạn lặp lại chữ của bảng ngay phía trên (ví dụ "%s"); nhiều khả năng bị nhân đôi khi chuyển đổi',
                      '%d paragraph(s) repeat the text of the table just above (for example "%s"); likely duplicated during conversion') % (dup, exd))
    # dòng trống thay cho giãn đoạn / blank paragraphs used as spacing
    paras = [c for c in body if c.tag == W + 'p']
    empty = [c for c in paras if not _ptext(c) and c.find('.//' + W + 'drawing') is None and c.find('.//' + W + 'pict') is None
             and not any(b.get(W + 'type') in ('page', 'column') for b in c.iter(W + 'br'))]
    if len(paras) >= 20 and len(empty) > 0.2 * len(paras):
        note.append(L('%d/%d đoạn là dòng trống; nên dùng giãn đoạn thay vì dòng trống', '%d/%d paragraphs are blank lines; use paragraph spacing instead') % (len(empty), len(paras)))
    # văn bản hành chính / administrative documents
    if not admin:
        return must, note
    if sect is not None and sect.find(W + 'pgMar') is not None:
        m = sect.find(W + 'pgMar')
        mm = {}
        for k in ('top', 'bottom', 'left', 'right'):
            try:
                mm[k] = int(m.get(W + k)) * 25.4 / 1440
            except (TypeError, ValueError):
                mm[k] = None
        for k, (lo, hi) in ND30_RULES['margins_mm'].items():
            if mm[k] is None:
                note.append(L('chưa xác định được lề %s', 'margin %s could not be resolved') % k)
            elif not (lo - 1.5 <= mm[k] <= hi + 1.5):
                must.append(L('lề %s %.0f mm, thể thức Nghị định 30 yêu cầu %d-%d mm', 'margin %s %.0f mm, Decree 30 layout asks for %d-%d mm') % (
                    {'top': L('trên', 'top'), 'bottom': L('dưới', 'bottom'), 'left': L('trái', 'left'), 'right': L('phải', 'right')}[k], mm[k], lo, hi))
    else:
        note.append(L('chưa khai báo lề trang', 'no page margins declared'))
    fonts, sizes = {}, {}
    pstyles = {id(r): (p.find(W + 'pPr/' + W + 'pStyle').get(W + 'val')
                if p.find(W + 'pPr/' + W + 'pStyle') is not None else None)
               for p in body.iter(W + 'p') for r in p.iter(W + 'r')}
    for r in body.iter(W + 'r'):
        n = sum(len(t.text or '') for t in r.iter(W + 't'))
        if not n:
            continue
        f, s = _rp(r.find(W + 'rPr'))
        rs = r.find(W + 'rPr/' + W + 'rStyle')
        sid = rs.get(W + 'val') if rs is not None else None
        f = f or _eff(st, sid, 0, defaults=False) if sid else f
        s = s or _eff(st, sid, 1, defaults=False) if sid else s
        f = f or _eff(st, pstyles.get(id(r)), 0)
        s = s or _eff(st, pstyles.get(id(r)), 1)
        if f and f.startswith('@'):
            f = theme.get('major' if 'major' in f.lower() else 'minor') or f
        if f:
            fonts[f.lower()] = fonts.get(f.lower(), 0) + n
        if s:
            sizes[s] = sizes.get(s, 0) + n
    if fonts:
        top = max(fonts, key=fonts.get)
        if top != ND30_RULES['font'].lower():
            must.append(L('phông chữ chủ đạo là "%s", thể thức yêu cầu %s', 'dominant font is "%s", the layout asks for %s') % (top, ND30_RULES['font']))
    else:
        note.append(L('chưa xác định được phông chữ', 'font could not be resolved'))
    if sizes:
        top = max(sizes, key=sizes.get) / 2.0
        lo, hi = ND30_RULES['body_pt']
        if not (lo <= top <= hi):
            must.append(L('cỡ chữ chủ đạo %.4g pt, thể thức yêu cầu %d-%d pt', 'dominant font size %.4g pt, the layout asks for %d-%d pt') % (top, lo, hi))
    else:
        note.append(L('chưa xác định được cỡ chữ', 'font size could not be resolved'))
    if len(paras) > 40 and not any(re.search(r'\bPAGE\b', text, re.I) for text in page_instructions):
        note.append(L('văn bản dài nhưng chưa thấy số trang trong đầu/chân trang', 'long document but no page number found in the header/footer'))
    return must, note

def check_text(path, text, ext):
    must, note = [], []
    body = re.sub(r'```.*?```', '', text, flags=re.S) if ext == '.md' else text
    if ext == '.html':
        body = re.sub(r'<(script|style)\b.*?</\1>', '', body, flags=re.S | re.I)
        body = re.sub(r'<[^>]+>', ' ', body)
    ph = []
    for m in PLACEHOLDER.finditer(body):
        s = m.group(1).strip()
        if FLAG.search(s) or re.fullmatch(r'[ xX]', s) or re.fullmatch(r'\d+', s) or s.startswith('^'):
            continue
        if re.search(r'[A-ZÀ-Ỹa-zà-ỹ]{2}', s):
            ph.append(s)
    if ph:
        must.append(L('còn %d chỗ có vẻ chưa điền, ví dụ: %s', 'about %d place(s) look unfilled, for example: %s') % (len(ph), '; '.join('[%s]' % x for x in ph[:4])))
    fl = FLAG.findall(body)
    if fl:
        note.append(L('có %d chỗ đánh dấu "cần xác nhận"; hãy chắc chúng được xử lý hoặc nói rõ với người nhận', '%d place(s) are marked "to be confirmed"; make sure they are resolved or tell the recipient') % len(fl))
    if DEMO.search(body):
        must.append(L('còn nhãn "mẫu/dữ liệu minh họa/giả" trong nội dung', 'a "template / illustrative / fake data" label is still in the content'))
    if ext == '.html':
        if re.search(r'<(script|link|img|iframe)\b[^>]*(src|href)=["\']https?://', text, re.I) or re.search(r'@import|url\(\s*["\']?https?:', text):
            must.append(L('HTML tải tài nguyên từ mạng (sẽ không mở được offline)', 'the HTML loads resources from the network (it will not open offline)'))
        if re.search(r'isDemo["\']?\s*[:=]\s*true', text):
            must.append(L('isDemo vẫn là true (báo cáo còn ở chế độ minh họa)', 'isDemo is still true (the report is still in demo mode)'))
        t = re.search(r'<title>(.*?)</title>', text, re.S | re.I)
        if not t or not t.group(1).strip():
            must.append(L('thiếu thẻ <title>', 'missing <title>'))
    if len(text.strip()) < 20:
        must.append(L('nội dung gần như trống', 'the content is almost empty'))
    return must, note

DECL_HEAD = re.compile(r'^[ \t]*(?:#+[ \t]*|\*\*)?(Khai báo thực hiện|Execution declaration)', re.I | re.M)
DECL_FIELDS = [('cách làm', 'method', 'Cách làm / Method'), ('nguồn', 'sources', 'Nguồn / Sources'),
               ('file', 'files', 'File / Files'), ('chưa kiểm', 'not checked', 'Chưa kiểm / Not checked')]

def check_declaration(text):
    must, note = [], []
    m = DECL_HEAD.search(text)
    if not m:
        return [L('không có khối "Khai báo thực hiện" (xem AGENTS.md)', 'no "Execution declaration" block (see AGENTS.md)')], note
    fields, cur = {}, None
    for line in text[m.end():].split('\n'):
        fm = re.match(r'^\s*[-*]\s*(?:\*\*)?([^:\n]{2,40}?)(?:\*\*)?\s*:\s*(.*)$', line)
        if fm:
            cur = fm.group(1).strip().lower(); fields[cur] = fm.group(2).strip()
        elif cur and line.strip() and not line.lstrip().startswith(('-', '*', '#')):
            fields[cur] += ' ' + line.strip()
    def get(*names):
        for k, v in fields.items():
            if any(k.startswith(n) for n in names): return v
        return None
    for vi, en, label in DECL_FIELDS:
        v = get(vi, en)
        if v is None:
            must.append(L('thiếu mục "%s"', 'missing item "%s"') % label)
        elif not v or re.fullmatch(r'\[[^\]]*\]', v):
            must.append(L('mục "%s" chưa điền', 'item "%s" is not filled in') % label)
    if get('skill') is None:
        note.append(L('chưa có mục "Skill" (tên skill đã đọc hoặc "không dùng skill")', 'no "Skill" item (name of the skill read, or "no skill used")'))
    how = get('cách làm', 'method') or ''
    if how and not re.search(r'python|\.py|script|thủ công|manual|không chạy|no script|by hand', how, re.I):
        note.append(L('mục Cách làm chưa nói rõ có chạy script/công cụ hay đọc thủ công', 'Method does not say whether a script/tool was run or the work was done manually'))
    if re.search(r'check_spreadsheet', how) and not re.search(r'dấu vết|trace', how, re.I):
        note.append(L('Cách làm nhắc check_spreadsheet nhưng thiếu dòng "Dấu vết" / "Trace" mà script in ra', 'Method mentions check_spreadsheet but lacks the "Trace" line the script prints'))
    figs = get('số liệu', 'figures')
    whole = text[m.end():]
    if re.search(r'sai lệch|lệch|không khớp|mismatch|discrepan|does not match', whole, re.I) and not (figs and re.search(r'\d', figs)):
        note.append(L('có nói về sai lệch nhưng mục Số liệu không có con số cụ thể', 'mentions a discrepancy but the Figures item has no concrete numbers'))
    return must, note

def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--lang', choices=['vi', 'en'], default=None)
    ap.add_argument('--profile', choices=['auto', 'nd30', 'none'], default='auto',
                    help='bố cục .docx: auto (tự nhận văn bản hành chính qua Quốc hiệu), nd30 (ép kiểm thể thức Nghị định 30), none (bỏ kiểm bố cục, vẫn kiểm chữ) / .docx layout profile')
    ap.add_argument('--declaration', action='store_true', help='kiểm khối Khai báo thực hiện trong câu trả lời đã lưu / check the Execution declaration block in a saved reply')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    LANG = a.lang or LANG
    if a.lang is None:
        try:
            import json
            LANG = json.load(io.open(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json'), encoding='utf-8')).get('language', 'vi')
        except (OSError, ValueError):
            pass
    statuses, records = [], []
    current_file = [None]
    def result(code):
        statuses.append(code)
        records.append({'path': current_file[0], 'status': ('pass', 'issues', 'not_checked')[code]})
        print('  ' + [L('ĐÃ KIỂM — ĐẠT trong phạm vi hỗ trợ.', 'CHECKED — PASS within supported scope.'),
                      L('ĐÃ KIỂM — CÓ VẤN ĐỀ / CẦN XEM XÉT.', 'CHECKED — ISSUES / REVIEW REQUIRED.'),
                      L('CHƯA KIỂM ĐƯỢC.', 'NOT CHECKED.')][code])
    for f in a.files:
        current_file[0] = f
        ext = os.path.splitext(f)[1].lower()
        print('== %s ==' % f)
        if not os.path.isfile(f):
            print('  ' + L('Không thấy file. Chưa kiểm được: kiểm lại đường dẫn hoặc chép file về máy rồi thử lại.',
                     'File not found. Not checked: check the path, or copy the file to this computer and try again.')); result(2); continue
        if a.declaration:
            try:
                must, note = check_declaration(io.open(f, encoding='utf-8').read())
            except (OSError, UnicodeError) as e:
                print('  ' + L('Không đọc được file (%s). Chưa kiểm được.', 'Could not read the file (%s). Not checked.') % e); result(2); continue
            for m_ in must: print('  ' + L('CẦN SỬA: ', 'FIX: ') + m_)
            for n_ in note: print('  ' + L('LƯU Ý: ', 'NOTE: ') + n_)
            if not must and not note: print('  ' + L('Khai báo đủ các mục.', 'Declaration has all items.'))
            result(1 if must or note else 0); continue
        if ext in ('.csv', '.xlsx', '.xlsm'):
            if ext != '.csv' and importlib.util.find_spec('openpyxl') is None:
                print(L('Thiếu openpyxl cho Excel. Cài bằng: python -m pip install openpyxl. CSV vẫn dùng được.',
                        'Excel requires openpyxl. Install with: python -m pip install openpyxl. CSV still works.'))
                result(2); continue
            sc = os.path.join(ROOT, 'skills', 'local', 'shared', 'spreadsheet-check', 'scripts', 'check_spreadsheet.py')
            try:
                r = subprocess.run([sys.executable, sc, f, '--lang', LANG, '--status-exit'], capture_output=True)
            except OSError as e:
                print('  ' + L('Không chạy được công cụ kiểm Excel (%s). Chưa kiểm được file này.', 'Could not run the Excel check tool (%s). This file was not checked.') % e); result(2); continue
            print(r.stdout.decode('utf-8', 'replace').rstrip() or r.stderr.decode('utf-8', 'replace').rstrip())
            if r.returncode not in (0, 1):
                err = r.stderr.decode('utf-8', 'replace').strip().splitlines()
                print('  ' + L('LỖI CÔNG CỤ: skill spreadsheet-check không chạy xong (mã %d) - KHÔNG kiểm được file này, đừng hiểu là không có lỗi. %s', 'TOOL ERROR: the spreadsheet-check skill did not finish (code %d) - this file was NOT checked, do not read it as no problems. %s') % (r.returncode, err[-1] if err else ''))
                result(2)
            else:
                result(r.returncode)
            continue
        if ext not in ('.md', '.txt', '.html', '.docx'):
            print('  ' + L('Định dạng chưa hỗ trợ (%s).', 'Unsupported format (%s).') % ext); result(2); continue
        if ext == '.docx':
            print(L('  Phạm vi: thân bài, đầu/chân trang, chú thích chân trang/cuối tài liệu; bố cục section cuối (ngắt dòng cứng, đoạn lặp sau bảng, dòng trống; với profile hành chính: A4, lề, phông, cỡ chữ, số trang). Chưa kiểm: giãn đoạn, canh lề từng đoạn, chữ trong ảnh, bình luận, thay đổi được theo dõi, cách trình bày thực tế khi mở bằng Word.',
                    '  Scope: body, headers/footers, footnotes/endnotes; layout of final section (hard line breaks, text repeated after tables, blank lines; with the administrative profile: A4, margins, font, size, page number). Not verified: paragraph spacing, per-paragraph alignment, text in images, comments, tracked changes, how it actually looks when opened in Word.'))
        try:
            must, note = check_text(f, text_of(f), ext)
            if ext == '.docx':
                lm, ln = check_docx_layout(f, a.profile)
                must, note = must + lm, note + ln
        except (zipfile.BadZipFile, KeyError, OSError, ET.ParseError, UnicodeError, RuntimeError, ValueError) as e:
            print('  ' + L('Không đọc được file (%s). Chưa kiểm được: mở file bằng ứng dụng gốc để xem có hỏng hoặc bị khóa không; nếu có, lưu bản khác rồi kiểm lại.',
                     'Could not read the file (%s). Not checked: open the file in its own application to see whether it is damaged or locked; if so, save another copy and check that.') % e); result(2); continue
        for m in must: print('  ' + L('CẦN SỬA: ', 'FIX: ') + m)
        for n in note: print('  ' + L('LƯU Ý: ', 'NOTE: ') + n)
        if not must and not note:
            print('  ' + L('Không phát hiện vấn đề cơ học.', 'No mechanical problems found.'))
        result(1 if must or note else 0)
    print('\n' + L('Kiểm tra cơ học, chưa thay việc đọc lại và đối chiếu số liệu với nguồn (xem delivery-checklist).',
                  'A mechanical check; it does not replace re-reading and checking figures against sources (see delivery-checklist).'))
    print(L('Tổng kết: %d đạt; %d cần xem xét; %d chưa kiểm được.',
            'Summary: %d passed; %d need review; %d not checked.') % tuple(statuses.count(i) for i in range(3)))
    code = max(statuses, default=2)
    if a.result_json:
        emit(make(('success', 'issues', 'not_checked')[code], code=code,
                  message=L('Kiểm tra đầu ra đã hoàn tất.', 'Output check completed.'),
                  changes=False, files=records,
                  findings=[x for x in records if x['status'] == 'issues'],
                  unchecked=[x for x in records if x['status'] == 'not_checked']))
    sys.exit(code)

if __name__ == '__main__':
    main()
