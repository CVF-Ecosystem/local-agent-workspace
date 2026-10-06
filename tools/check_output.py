#!/usr/bin/env python3
"""Kiểm tra nhanh một sản phẩm trước khi giao: còn chỗ chưa điền, còn nhãn mẫu minh họa, tài nguyên mạng trong HTML...
Quick pre-delivery check of a deliverable: unfilled placeholders, leftover demo labels, network resources in HTML...

Dùng / Usage:
  python tools/check_output.py <file> [<file> ...] [--lang vi|en]
  python tools/check_output.py --declaration <reply.txt|.md>   (kiểm khối "Khai báo thực hiện" / check the "Execution declaration" block)

Hỗ trợ: .md .txt .html .docx .csv .xlsx (CSV/Excel được chuyển cho skill spreadsheet-check). Chỉ đọc, không sửa file.
Mã thoát: 0 không có lỗi cần sửa; 1 có điều cần sửa trước khi giao. Chỉ cần Python 3.8+, không dùng mạng.
Đây là kiểm tra cơ học, không thay thế việc đọc lại và đối chiếu số liệu với nguồn.
"""
import argparse, io, os, re, subprocess, sys, zipfile

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
            x = z.read('word/document.xml').decode('utf-8', 'replace')
        x = re.sub(r'</w:p>', '\n', x)
        return re.sub(r'<[^>]+>', '', x)
    return io.open(path, encoding='utf-8', errors='replace').read()

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
    how = get('cách làm', 'method') or ''
    if how and not re.search(r'python|\.py|script|thủ công|manual|không chạy|no script|by hand|skill', how, re.I):
        note.append(L('mục Cách làm chưa nói rõ có chạy script/công cụ hay đọc thủ công', 'Method does not say whether a script/tool was run or the work was done manually'))
    figs = get('số liệu', 'figures')
    whole = text[m.end():]
    if re.search(r'sai lệch|lệch|không khớp|mismatch|discrepan|does not match', whole, re.I) and not (figs and re.search(r'\d', figs)):
        note.append(L('có nói về sai lệch nhưng mục Số liệu không có con số cụ thể', 'mentions a discrepancy but the Figures item has no concrete numbers'))
    return must, note

def main():
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--lang', choices=['vi', 'en'], default=None)
    ap.add_argument('--declaration', action='store_true', help='kiểm khối Khai báo thực hiện trong câu trả lời đã lưu / check the Execution declaration block in a saved reply')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    LANG = a.lang or LANG
    if a.lang is None:
        try:
            import json
            LANG = json.load(io.open(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json'), encoding='utf-8')).get('language', 'vi')
        except (OSError, ValueError):
            pass
    bad = 0
    for f in a.files:
        ext = os.path.splitext(f)[1].lower()
        print('== %s ==' % f)
        if not os.path.isfile(f):
            print('  ' + L('Không thấy file.', 'File not found.')); bad += 1; continue
        if a.declaration:
            must, note = check_declaration(io.open(f, encoding='utf-8', errors='replace').read())
            for m_ in must: print('  ' + L('CẦN SỬA: ', 'FIX: ') + m_)
            for n_ in note: print('  ' + L('LƯU Ý: ', 'NOTE: ') + n_)
            if not must and not note: print('  ' + L('Khai báo đủ các mục.', 'Declaration has all items.'))
            bad += len(must); continue
        if ext in ('.csv', '.xlsx', '.xlsm'):
            sc = os.path.join(ROOT, 'skills', 'local', 'shared', 'spreadsheet-check', 'scripts', 'check_spreadsheet.py')
            r = subprocess.run([sys.executable, sc, f, '--lang', LANG], capture_output=True)
            print(r.stdout.decode('utf-8', 'replace').rstrip() or r.stderr.decode('utf-8', 'replace').rstrip())
            continue
        if ext not in ('.md', '.txt', '.html', '.docx'):
            print('  ' + L('Định dạng chưa hỗ trợ (%s).', 'Unsupported format (%s).') % ext); continue
        try:
            must, note = check_text(f, text_of(f), ext)
        except (zipfile.BadZipFile, KeyError, OSError) as e:
            print('  ' + L('Không đọc được file (%s).', 'Could not read the file (%s).') % e); bad += 1; continue
        for m in must: print('  ' + L('CẦN SỬA: ', 'FIX: ') + m)
        for n in note: print('  ' + L('LƯU Ý: ', 'NOTE: ') + n)
        if not must and not note:
            print('  ' + L('Không phát hiện vấn đề cơ học.', 'No mechanical problems found.'))
        bad += len(must)
    print('\n' + L('Kiểm tra cơ học, chưa thay việc đọc lại và đối chiếu số liệu với nguồn (xem delivery-checklist).',
                  'A mechanical check; it does not replace re-reading and checking figures against sources (see delivery-checklist).'))
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
