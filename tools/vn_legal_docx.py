#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render supported HTML text/tables using a local administrative presentation template.
A4, margins, Times New Roman, page field and semantic heading/signature heuristics
supplement native document tools; they do not verify current law or visual layout.
Only plain text, bold/italic, explicit line breaks and simple non-nested tables are
supported. Known unsupported content/spans and text loss refuse before writing.
Visible text inside the selected content is preserved. Decorative dash lines become borders.
Usage: python tools/vn_legal_docx.py INPUT.html OUTPUT.docx [--title TITLE] [--overwrite]
Optional dependencies: beautifulsoup4, python-docx. No network or installation. Python 3.8+.
"""
import argparse
import datetime
import os
import re
import sys
import tempfile
from pathlib import Path

FONT = 'Times New Roman'
BODY_PT = 13
TABLE_PT = 11
SMALL_PT = 11
INDENT_CM = 1.0
AFTER_PT = 6
LINE_SPACING = 1.15
MARGINS_CM = (2.0, 2.0, 3.0, 2.0)  # trên, dưới, trái, phải
TEXT_WIDTH_CM = 21.0 - 3.0 - 2.0

# Local presentation ranges; spec_check compares them with nd30-presentation.md.
# The stdlib checker keeps an independent mechanical subset; tests compare shared values.
ND30_RULES = {
    'margins_mm': {'top': (20, 25), 'bottom': (20, 25), 'left': (30, 35), 'right': (15, 20)},
    'font': 'Times New Roman',
    'body_pt': (13, 14),
    'indent_cm': (1.0, 1.27),
    'after_pt_min': 6,
    'line_spacing_max': 1.5,
}
SPEC_FILE = Path(__file__).resolve().parents[1] / 'skills' / 'local' / 'shared' / 'vn-admin-documents' / 'references' / 'nd30-presentation.md'

DOC_TYPES_UPPER = ('LUẬT', 'PHÁP LỆNH', 'NGHỊ QUYẾT', 'NGHỊ ĐỊNH', 'QUYẾT ĐỊNH', 'THÔNG TƯ LIÊN TỊCH', 'THÔNG TƯ',
                   'CHỈ THỊ', 'LỆNH', 'CÔNG ĐIỆN', 'THÔNG BÁO', 'KẾ HOẠCH', 'BÁO CÁO', 'HIẾN PHÁP',
                   'QUY CHẾ', 'QUY ĐỊNH', 'VĂN BẢN HỢP NHẤT', 'NGHỊ QUYẾT LIÊN TỊCH')

def _need_libs():
    """Load optional dependencies only when rendering; never install anything."""
    global BeautifulSoup, NavigableString, Comment, Document, WD_ALIGN_PARAGRAPH, WD_BREAK
    global OxmlElement, qn, Cm, Pt
    try:
        from bs4 import BeautifulSoup, NavigableString, Comment
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Cm, Pt
    except ImportError as exc:
        raise ImportError('Optional dependencies required: beautifulsoup4 and python-docx (%s)' % exc)


# ---------------------------------------------------------------- chữ / text
def norm(s):
    s = s.replace('\xa0', ' ').replace('​', '')
    return re.sub(r'\s+', ' ', s)


# Deliberately not a CSS engine: only monotone bold/italic declarations are
# accepted. Validation and every render path share this parsed representation.
_CSS_VALUES = {'font-weight': {'bold', '700'}, 'font-style': {'italic'}}
_CSS_SPACE = ' \t\r\n\f'


def _parse_inline_css(raw):
    raw = raw.strip(_CSS_SPACE)
    if not raw:
        return {}
    declarations = raw.split(';')
    if declarations[-1].strip(_CSS_SPACE) == '':
        declarations.pop()  # one optional trailing semicolon
    result = {}
    for declaration in declarations:
        match = re.fullmatch(r'[ \t\r\n\f]*([a-zA-Z-]+)[ \t\r\n\f]*:[ \t\r\n\f]*([a-zA-Z0-9]+)[ \t\r\n\f]*', declaration)
        if match is None:
            raise UnsupportedHTML('Unsupported/malformed inline CSS')
        key, value = (part.lower() for part in match.groups())
        if key in result or value not in _CSS_VALUES.get(key, set()):
            raise UnsupportedHTML('Unsupported/duplicate inline CSS: %s:%s' % (key, value))
        result[key] = value
    return result


def _inline_flags(node, bold, italic):
    # Private Python metadata, never an HTML attribute. Only validated nodes have
    # this field, so inheritance stops at the selected content boundary.
    css = node.__dict__.get('_law_inline_css', {})
    return (bold or node.name in ('b', 'strong') or 'font-weight' in css,
            italic or node.name in ('i', 'em') or 'font-style' in css)


def _visit(ch, bold, italic, out):
    if isinstance(ch, Comment):
        return
    if isinstance(ch, NavigableString):
        t = str(ch)
        if t:
            out.append([t, bold, italic])
        return
    name = (ch.name or '').lower()
    if name in ('script', 'style', 'noscript'):
        return
    if name == 'br':
        out.append(['\n', False, False])
        return
    b, i = _inline_flags(ch, bold, italic)
    for c in ch.children:
        _visit(c, b, i, out)
    if name in ('td', 'th', 'tr'):
        out.append([' ', False, False])


def collect_runs(nodes):
    out = []
    for n in nodes:
        bold, italic = False, False
        parent = n.parent
        while parent is not None and '_law_inline_css' in parent.__dict__:
            bold, italic = _inline_flags(parent, bold, italic)
            parent = parent.parent
        _visit(n, bold, italic, out)
    return finalize_runs(out)


def finalize_runs(raw):
    """Gộp khoảng trắng; chỉ giữ xuống dòng do <br>. Trả về danh sách [text, đậm, nghiêng]."""
    res = []
    prev_space = True
    for text, b, i in raw:
        if text == '\n':
            if res and res[-1][0] != '\n':
                res[-1][0] = res[-1][0].rstrip(' ')
                if res[-1][0] == '':
                    res.pop()
            res.append(['\n', False, False])
            prev_space = True
            continue
        t = norm(text)
        if prev_space:
            t = t.lstrip(' ')
        if not t:
            continue
        if res and res[-1][0] != '\n' and res[-1][1] == b and res[-1][2] == i:
            res[-1][0] += t
        else:
            res.append([t, b, i])
        prev_space = t.endswith(' ')
    while res and (res[-1][0] == '\n' or not res[-1][0].strip()):
        res.pop()
    if res and res[-1][0] != '\n':
        res[-1][0] = res[-1][0].rstrip(' ')
    return res


def plain(runs):
    return ''.join(r[0] for r in runs if r[0] != '\n').strip()


def lines_of(runs):
    lines, cur = [], []
    for t, b, i in runs:
        if t == '\n':
            lines.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(t)
    lines.append(''.join(cur).strip())
    return [ln for ln in lines if ln]


# ---------------------------------------------------------------- cây HTML / HTML tree
_BLOCKS = ['p', 'div', 'table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 'section',
           'article', 'center', 'form']
_CONTAINERS = ('div', 'section', 'article', 'center', 'blockquote', 'ul', 'ol', 'p', 'li', 'form',
               'h1', 'h2', 'h3', 'h4', 'h5', 'h6')


def _has_block(tag):
    return tag.find(_BLOCKS) is not None


def iter_blocks(node):
    """Duyệt khối theo thứ tự tài liệu, mỗi khối đúng một lần. Yield ('p'|'table'|'inline', nút hoặc danh sách nút).
    Bảng được yield nguyên khối và không duyệt vào trong, nên chữ trong bảng không bị xử lý hai lần."""
    pending = []

    def flush():
        if pending and any((not isinstance(x, NavigableString)) or str(x).strip() for x in pending):
            items = list(pending)
            del pending[:]
            return ('inline', items)
        del pending[:]
        return None

    for ch in node.children:
        if isinstance(ch, Comment):
            continue
        if isinstance(ch, NavigableString):
            if str(ch).strip():
                pending.append(ch)
            continue
        name = (ch.name or '').lower()
        if name in ('script', 'style', 'noscript', 'nav', 'iframe', 'img', 'input', 'button'):
            continue
        if name == 'br':
            f = flush()
            if f:
                yield f
            continue
        if name == 'table':
            f = flush()
            if f:
                yield f
            yield ('table', ch)
        elif name in _CONTAINERS:
            f = flush()
            if f:
                yield f
            if _has_block(ch):
                for x in iter_blocks(ch):
                    yield x
            else:
                yield ('p', ch)
        else:  # span, b, i, a, font...
            if _has_block(ch):
                f = flush()
                if f:
                    yield f
                for x in iter_blocks(ch):
                    yield x
            else:
                pending.append(ch)
    f = flush()
    if f:
        yield f


def block_runs(kind, node):
    return collect_runs(node if kind == 'inline' else [node])


def align_hint(node):
    if isinstance(node, list):
        return ''
    a = (node.get('align') or '').lower()
    return a


def rows_of(tbl):
    return [r for r in tbl.find_all('tr') if r.find_parent('table') is tbl]


def cells_of(row):
    return row.find_all(['td', 'th'], recursive=False)


HEADER_PAT = re.compile(r'CỘNG HÒA XÃ HỘI|Độc lập\s*-\s*Tự do', re.I)


def table_kind(tbl):
    rows = rows_of(tbl)
    if not rows:
        return 'empty'
    ncol = max(len(cells_of(r)) for r in rows)
    text = norm(tbl.get_text(' '))
    if ncol == 2 and len(rows) <= 3 and HEADER_PAT.search(text):
        return 'header'
    first = cells_of(rows[0])
    if ncol == 2 and len(rows) <= 8 and first and re.match(r'\s*Nơi nhận', first[0].get_text(' ', strip=True)):
        return 'sign'  # khối ký dàn nhiều hàng (Nơi nhận ở ô đầu) / signature block spread over several rows
    if ncol == 2 and len(rows) <= 2 and (re.search(r'Nơi nhận', text)
                                         or (len(rows) == 1 and re.search(r'Ký, ghi rõ họ tên|Xác nhận của', text))):
        return 'sign'
    return 'data'


# ---------------------------------------------------------------- định dạng docx / docx formatting
def _set_rfonts(rpr):
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts')
        rpr.insert(0, rf)
    for a in list(rf.attrib):
        if a.endswith('Theme'):
            del rf.attrib[a]
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
        rf.set(qn(a), FONT)


def new_document(title='', source_url=None):
    """Tài liệu Word theo thể thức Nghị định 30 (A4, lề, Times New Roman 13, cách đoạn 6 pt, số trang lề trên, trang đầu
    không số). Dùng chung cho mọi nơi dựng văn bản hành chính; xem thêm new_nd30_document.
    A Word document laid out per Decree 30; shared by every place that builds administrative documents."""
    _need_libs()
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.bottom_margin, sec.left_margin, sec.right_margin = (Cm(x) for x in MARGINS_CM)
    sec.header_distance = Cm(1.0)
    sec.footer_distance = Cm(1.0)
    sec.different_first_page_header_footer = True  # không hiện số trang ở trang đầu

    dd = doc.styles.element.find(qn('w:docDefaults'))
    if dd is not None:
        rpr = dd.find(qn('w:rPrDefault') + '/' + qn('w:rPr'))
        if rpr is not None:
            _set_rfonts(rpr)
            lang = rpr.find(qn('w:lang'))
            if lang is None:
                lang = OxmlElement('w:lang')
                rpr.append(lang)
            lang.set(qn('w:val'), 'vi-VN')
            lang.set(qn('w:eastAsia'), 'vi-VN')
    normal = doc.styles['Normal']
    normal.font.name = FONT
    normal.font.size = Pt(BODY_PT)
    _set_rfonts(normal.element.get_or_add_rPr())
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(AFTER_PT)
    pf.line_spacing = LINE_SPACING

    add_page_number_header(sec)
    cp = doc.core_properties
    cp.author = ''
    cp.last_modified_by = ''
    cp.title = (title or '')[:250]
    cp.subject = ''
    cp.comments = ('Nguồn: ' + source_url) if source_url else ''
    cp.language = 'vi-VN'
    now = datetime.datetime.now()
    cp.created = now
    cp.modified = now
    return doc


new_nd30_document = new_document  # tên gọi rõ nghĩa cho nơi gọi từ skill / explicit name for skill callers


def _field(par, instr, size):
    def mk(kind):
        r = par.add_run()
        r.font.size = Pt(size)
        el = OxmlElement('w:fldChar')
        el.set(qn('w:fldCharType'), kind)
        r._r.append(el)
        return r
    mk('begin')
    r = par.add_run()
    r.font.size = Pt(size)
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = ' %s ' % instr
    r._r.append(it)
    mk('separate')
    par.add_run('1').font.size = Pt(size)
    mk('end')


def add_page_number_header(sec):
    sec.header.is_linked_to_previous = False
    p = sec.header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    _field(p, 'PAGE', BODY_PT)
    sec.first_page_header.is_linked_to_previous = False  # để trống


_PPR_AFTER_BDR = ('w:shd', 'w:tabs', 'w:suppressAutoHyphens', 'w:kinsoku', 'w:wordWrap', 'w:overflowPunct',
                  'w:topLinePunct', 'w:autoSpaceDE', 'w:autoSpaceDN', 'w:bidi', 'w:adjustRightInd', 'w:snapToGrid',
                  'w:spacing', 'w:ind', 'w:contextualSpacing', 'w:mirrorIndents', 'w:suppressOverlap', 'w:jc',
                  'w:textDirection', 'w:textAlignment', 'w:textboxTightWrap', 'w:outlineLvl', 'w:divId',
                  'w:cnfStyle', 'w:rPr', 'w:sectPr', 'w:pPrChange')


def bottom_border(par):
    ppr = par._p.get_or_add_pPr()
    bdr = OxmlElement('w:pBdr')
    b = OxmlElement('w:bottom')
    for k, v in (('w:val', 'single'), ('w:sz', '4'), ('w:space', '1'), ('w:color', '000000')):
        b.set(qn(k), v)
    bdr.append(b)
    ppr.insert_element_before(bdr, *_PPR_AFTER_BDR)


def outline_level(par, lvl):
    ppr = par._p.get_or_add_pPr()
    el = OxmlElement('w:outlineLvl')
    el.set(qn('w:val'), str(lvl))
    ppr.insert_element_before(el, 'w:divId', 'w:cnfStyle', 'w:rPr', 'w:sectPr', 'w:pPrChange')


def _align(name):
    return {'left': WD_ALIGN_PARAGRAPH.LEFT, 'center': WD_ALIGN_PARAGRAPH.CENTER,
            'right': WD_ALIGN_PARAGRAPH.RIGHT, 'justify': WD_ALIGN_PARAGRAPH.JUSTIFY}[name]


def style_par(par, align='justify', first=INDENT_CM, before=0, after=AFTER_PT, keep_next=False, line=None):
    par.alignment = _align(align)
    pf = par.paragraph_format
    pf.first_line_indent = Cm(first) if first else Cm(0)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if line:
        pf.line_spacing = line
    if keep_next:
        pf.keep_with_next = True


def add_runs(par, runs, size=None, bold=None, italic=None):
    for t, b, i in runs:
        if t == '\n':
            par.add_run().add_break(WD_BREAK.LINE)
            continue
        r = par.add_run(t)
        if size and size != BODY_PT:
            r.font.size = Pt(size)
        if bold or b:
            r.bold = True
        if italic or i:
            r.italic = True


def add_text(par, text, size=None, bold=None, italic=None):
    add_runs(par, [[text, False, False]], size=size, bold=bold, italic=italic)


def spacer(doc, pt=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run('')
    r.font.size = Pt(pt)
    return p


def _no_split(row):
    row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))


def _repeat_header(row):
    row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))


def _shade(cell, fill):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    cell._tc.get_or_add_tcPr().append(shd)


def cell_par(cell, idx):
    return cell.paragraphs[0] if idx == 0 else cell.add_paragraph()


def has_lower(s):
    """Có chữ thường không (đúng với chữ Việt hoa có dấu như Ư, Ớ; không dùng khoảng ký tự)."""
    return any(c.islower() for c in s)


def set_col_widths(table, widths_cm):
    """Đặt bề rộng cột ở cả lưới cột (LibreOffice) và từng ô (Word)."""
    for ci, w in enumerate(widths_cm):
        table.columns[ci].width = Cm(w)
        for cell in table.columns[ci].cells:
            cell.width = Cm(w)


# ---------------------------------------------------------------- bảng đầu / khối ký / layout tables
_DASHES = re.compile(r'\s*[-–—_]{3,}\s*$')
_PLACE_DATE = re.compile(r'^[^,]{2,40},\s*ngày\s+[\d\[]')  # chấp nhận cả ngày còn để trống [dd] / also placeholder dates
_SIGN_START = re.compile(r'^(TM\.|KT\.|TL\.|TUQ\.|Q\.)')
_ROLE_WORDS = ('THỦ TƯỚNG', 'PHÓ THỦ TƯỚNG', 'CHỦ TỊCH', 'PHÓ CHỦ TỊCH', 'BỘ TRƯỞNG', 'THỨ TRƯỞNG', 'TỔNG GIÁM ĐỐC',
               'GIÁM ĐỐC', 'PHÓ GIÁM ĐỐC', 'TỔNG CỤC TRƯỞNG', 'CỤC TRƯỞNG', 'CHÁNH VĂN PHÒNG', 'TRƯỞNG PHÒNG',
               'VỤ TRƯỞNG', 'PHÓ VỤ TRƯỞNG', 'CHÁNH THANH TRA', 'TỔNG THƯ KÝ')
_ROLE_RE = re.compile(r'(?<!\S)(' + '|'.join(sorted(_ROLE_WORDS, key=len, reverse=True)) + r')(?!\S)')


def split_header_line(line):
    m = re.match(r'^(CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM)\s*(Độc lập\s*-\s*Tự do\s*-\s*Hạnh phúc.*)$', line)
    if m:
        return [m.group(1), m.group(2)]
    return [line]


def split_sign_line(line):
    """Tách khối ký nguồn dồn một dòng, vd:
    'TM. CHÍNH PHỦ THỦ TƯỚNG Nguyễn Văn A' -> ['TM. CHÍNH PHỦ', 'THỦ TƯỚNG', 'Nguyễn Văn A'];
    'TM. CHÍNH PHỦ KT. THỦ TƯỚNG PHÓ THỦ TƯỚNG Hồ Văn B' -> ['TM. CHÍNH PHỦ', 'KT. THỦ TƯỚNG', 'PHÓ THỦ TƯỚNG', 'Hồ Văn B']."""
    out = []
    for seg in re.split(r'\s(?=(?:TM|KT|TL|TUQ|Q)\.)', line):
        seg = seg.strip()
        m = re.search(r'\s(PHÓ\s)', seg)
        if _SIGN_START.match(seg) and m:
            out.extend([seg[:m.start()].strip(), seg[m.start():].strip()])
        elif seg.startswith('TM.'):
            m = _ROLE_RE.search(seg, 3)
            if m:
                out.extend([seg[:m.start()].strip(), seg[m.start():].strip()])
            else:
                out.append(seg)
        elif _SIGN_START.match(seg):
            # 'KT. BỘ TRƯỞNG THỨ TRƯỞNG Tên' / 'TL. BỘ TRƯỞNG VỤ TRƯỞNG ...': chức vụ thứ hai bắt đầu dòng mới
            roles = list(_ROLE_RE.finditer(seg))
            if len(roles) >= 2:
                out.extend([seg[:roles[1].start()].strip(), seg[roles[1].start():].strip()])
            else:
                out.append(seg)
        else:
            out.append(seg)
    toks = out[-1].split(' ')
    for k, tk in enumerate(toks):
        if k > 0 and has_lower(tk) and toks[k - 1].isupper() and tk[:1].isupper():
            out[-1] = ' '.join(toks[:k]).strip()
            out.append(' '.join(toks[k:]).strip())
            break
    return [x for x in out if x]


def layout_cell_lines(cell):
    lines = []
    for kind, node in iter_blocks(cell):
        lines.extend(lines_of(block_runs(kind, node)))
    return lines


def render_header_table(doc, tbl, stats):
    rows = rows_of(tbl)
    t = doc.add_table(rows=len(rows), cols=2)
    t.autofit = False
    widths = (6.0, 10.0)
    set_col_widths(t, widths)
    for ri, row in enumerate(rows):
        cells = cells_of(row)
        for ci in range(2):
            c = t.cell(ri, ci)
            if ci >= len(cells):
                continue
            lines = []
            for ln in layout_cell_lines(cells[ci]):
                ln2 = _DASHES.sub('', ln)
                stats['dashes'] += _nonspace_len(ln[len(ln2):])
                for part in split_header_line(ln2):
                    if part.strip():
                        lines.append(part.strip())
            upper_idx = [k for k, ln in enumerate(lines) if ln.isupper() and not re.search(r'\d', ln)]
            for k, ln in enumerate(lines):
                p = cell_par(c, k)
                style_par(p, 'center', first=0, after=0, line=1.0)
                if ci == 0:
                    is_agency = k in upper_idx
                    main = is_agency and k == upper_idx[-1]
                    add_text(p, ln, size=12 if is_agency else BODY_PT, bold=main)
                    if main:
                        # dòng kẻ dài bằng khoảng 1/3-1/2 dòng chữ: thụt hai bên theo độ dài tên, tối đa 1,5 cm
                        ind = max(0.1, min(1.5, (5.6 - 0.22 * len(ln)) / 2.0))
                        p.paragraph_format.left_indent = Cm(ind)
                        p.paragraph_format.right_indent = Cm(ind)
                        bottom_border(p)
                elif ln.startswith('CỘNG HÒA'):
                    add_text(p, ln, size=BODY_PT, bold=True)
                elif re.match(r'^Độc lập', ln):
                    add_text(p, ln, size=14, bold=True)
                    p.paragraph_format.left_indent = Cm(0.8)
                    p.paragraph_format.right_indent = Cm(0.8)
                    bottom_border(p)
                elif _PLACE_DATE.match(ln):
                    p.paragraph_format.space_before = Pt(6)
                    add_text(p, ln, size=14, italic=True)
                else:
                    add_text(p, ln, size=BODY_PT)
    spacer(doc, 6)


def render_sign_table(doc, tbl, stats):
    rows = rows_of(tbl)
    first = cells_of(rows[0])[0] if rows and cells_of(rows[0]) else None
    has_noi_nhan = bool(first is not None and re.search(r'Nơi nhận', first.get_text(' ', strip=True)))
    if has_noi_nhan and len(rows) > 1:
        # gộp các hàng thành một: cột trái là danh sách nơi nhận, cột phải là khối ký / merge rows into one block
        cols = [[], []]
        for row in rows:
            for ci, cell in enumerate(cells_of(row)[:2]):
                cols[ci].append(cell)
        row_cells = [cols]
    else:
        row_cells = [[[c] for c in cells_of(row)] for row in rows]
    t = doc.add_table(rows=len(row_cells), cols=2)
    t.autofit = False
    widths = (8.0, 8.0)
    set_col_widths(t, widths)
    for ri, cells in enumerate(row_cells):
        for ci in range(2):
            c = t.cell(ri, ci)
            if ci >= len(cells) or not cells[ci]:
                continue
            lines = []
            for src_cell in cells[ci]:
                for ln in layout_cell_lines(src_cell):
                    lines.extend(split_sign_line(ln) if (ci == 1 and has_noi_nhan) else [ln])
            if not has_noi_nhan:
                # khối xác nhận / ký của phụ lục: hai ô cân bằng, giữa trang / balanced form-signature block
                for k, ln in enumerate(lines):
                    p = cell_par(c, k)
                    style_par(p, 'center', first=0, after=0, line=1.0)
                    note = ln.startswith('(') and ln.endswith(')')
                    add_text(p, ln, size=BODY_PT, bold=not note, italic=note)
                gap = cell_par(c, len(lines))
                style_par(gap, 'center', first=0, after=0, line=1.0)
                gap.paragraph_format.space_before = Pt(40)  # chỗ ký / room to sign
                continue
            for k, ln in enumerate(lines):
                p = cell_par(c, k)
                if ci == 0:
                    style_par(p, 'left', first=0, after=0, line=1.0)
                    if re.match(r'^Nơi nhận', ln):
                        add_text(p, ln, size=12, bold=True, italic=True)
                    else:
                        add_text(p, ln, size=SMALL_PT)
                else:
                    style_par(p, 'center', first=0, after=0, line=1.0)
                    if k == len(lines) - 1 and len(lines) >= 2 and (has_lower(ln) or ln.startswith('[')):
                        p.paragraph_format.space_before = Pt(54)  # chỗ ký / room for the signature
                    add_text(p, ln, size=BODY_PT, bold=True)
    spacer(doc, 6)


# ---------------------------------------------------------------- bảng dữ liệu / data tables
def render_data_table(doc, tbl, stats):
    rows = rows_of(tbl)
    grid = []
    placed = []  # (hàng, cột, rowspan, colspan, thẻ)
    ncol = 0
    for ri, row in enumerate(rows):
        while len(grid) <= ri:
            grid.append([])
        ci = 0
        for cell in cells_of(row):
            while ci < len(grid[ri]) and grid[ri][ci]:
                ci += 1
            try:
                cs = max(1, int(cell.get('colspan', 1)))
                rs = max(1, int(cell.get('rowspan', 1)))
            except ValueError:
                cs, rs = 1, 1
            rs = min(rs, len(rows) - ri)
            for rr in range(ri, ri + rs):
                while len(grid) <= rr:
                    grid.append([])
                while len(grid[rr]) < ci + cs:
                    grid[rr].append(False)
                for cc in range(ci, ci + cs):
                    grid[rr][cc] = True
            placed.append((ri, ci, rs, cs, cell))
            ci += cs
            ncol = max(ncol, ci)
    if ncol == 0:
        return
    t = doc.add_table(rows=len(rows), cols=ncol)
    t.style = 'Table Grid'
    t.autofit = False
    weights = [4] * ncol
    for ri, ci, rs, cs, cell in placed:
        if cs == 1:
            weights[ci] = max(weights[ci], min(60, len(norm(cell.get_text(' ')))))
    widths = [max(1.3, TEXT_WIDTH_CM * w / float(sum(weights))) for w in weights]
    scale = TEXT_WIDTH_CM / sum(widths)
    widths = [w * scale for w in widths]
    set_col_widths(t, widths)
    header_rows = set()
    for ri, row in enumerate(rows):
        cs_ = cells_of(row)
        if cs_ and all(c.name == 'th' for c in cs_):
            header_rows.add(ri)
    for ri, ci, rs, cs, cell in placed:
        target = t.cell(ri, ci)
        if rs > 1 or cs > 1:
            target = target.merge(t.cell(ri + rs - 1, ci + cs - 1))
        k = 0
        for kind, node in iter_blocks(cell):
            runs = block_runs(kind, node)
            if not runs:
                continue
            p = cell_par(target, k)
            k += 1
            short_num = re.fullmatch(r'[\d.,/\-]{1,8}', plain(runs)) is not None
            style_par(p, 'center' if (short_num or ri in header_rows) else 'left', first=0, after=2, line=1.0)
            add_runs(p, runs, size=TABLE_PT, bold=(ri in header_rows))
        if ri in header_rows:
            _shade(target, 'D9D9D9')
    for ri, row in enumerate(t.rows):
        _no_split(row)
        if ri in header_rows:
            _repeat_header(row)
    stats['tables'] += 1
    spacer(doc, 6)


# ---------------------------------------------------------------- đoạn văn / paragraphs
RE_CHAPTER = re.compile(r'^(Phần thứ\s+\S+|Phần\s+[IVXLCDM\d]+|Chương\s+[IVXLCDM\d]+|Mục\s+\d+|Tiểu mục\s+\d+)\b')
RE_ARTICLE = re.compile(r'^Điều\s*\d+[a-zA-Zđ]?\s*[.:]')
RE_BASIS = re.compile(r'^(Căn cứ|Theo đề nghị|Xét đề nghị|Sau khi)\b')
RE_DOCTYPE_LINE = re.compile(r'^(' + '|'.join(sorted(DOC_TYPES_UPPER, key=len, reverse=True)) + r')(\s|$)')


def emit_paragraph(doc, runs, text, hint, st, stats):
    if re.fullmatch(r'[-–—_=\s]{3,}', text):
        stats['dashes'] += _nonspace_len(text)
        return
    m_chap = RE_CHAPTER.match(text)
    rest = text[m_chap.end():] if m_chap else ''
    # câu nội dung bắt đầu bằng "Chương II được sửa đổi...", "Mục 2 Chương III được bãi bỏ." không phải đề mục
    content_like = has_lower(rest) and (text.endswith(('.', ':')) or re.search(
        r'\b(được|bị|như sau|bãi bỏ|thay thế|sửa đổi|bổ sung|quy định tại)\b', rest) is not None)
    chap = (m_chap is not None and len(text) <= 120 and ' Điều ' not in text and not text.endswith(';')
            and not content_like)
    p = doc.add_paragraph()
    if chap:
        style_par(p, 'center', first=0, before=6, keep_next=True)
        add_runs(p, runs, bold=True)
        outline_level(p, 0 if re.match(r'^(Phần|Chương)', text) else 1)
        st['expect_title'] = True
        st['expect_sub'] = False
        return
    if st['expect_title']:
        st['expect_title'] = False
        if (not RE_ARTICLE.match(text) and not re.match(r'^\d+\.', text) and len(text) <= 250
                and (text.isupper() or len(text) <= 120)):
            style_par(p, 'center', first=0, keep_next=True)
            add_runs(p, runs, bold=True)
            return
    if not st['seen_doctype'] and RE_DOCTYPE_LINE.match(text) and text.isupper() and len(text) <= 120:
        st['seen_doctype'] = True
        st['expect_sub'] = text in DOC_TYPES_UPPER  # tên loại đứng riêng một dòng -> dòng sau là trích yếu
        style_par(p, 'center', first=0, before=6, keep_next=True)
        add_runs(p, runs, size=14, bold=True)
        return
    if st['expect_sub']:
        st['expect_sub'] = False
        if len(text) <= 400 and not RE_BASIS.match(text) and not RE_ARTICLE.match(text):
            style_par(p, 'center', first=0, after=AFTER_PT + 6, keep_next=True)
            add_runs(p, runs, bold=True)
            return
    if not st['seen_doctype'] and not st['seen_article']:  # phần đầu khi nguồn không dùng bảng
        if (text.isupper() and len(text) <= 90 and not re.search(r'\d', text)) or re.match(r'^Độc lập\s*-\s*Tự do', text):
            style_par(p, 'center', first=0, after=0, line=1.0)
            add_runs(p, runs, bold=True)
            return
        if re.match(r'^Số\s*:', text):
            style_par(p, 'left', first=0, after=0, line=1.0)
            add_runs(p, runs)
            return
        if _PLACE_DATE.match(text):
            style_par(p, 'right', first=0)
            add_runs(p, runs, italic=True)
            return
    if RE_ARTICLE.match(text):
        st['seen_article'] = True
        st['in_recipients'] = False
        if len(text) <= 300:
            style_par(p, 'left', first=INDENT_CM, before=6, keep_next=True)
            add_runs(p, runs, bold=True)
            outline_level(p, 2)
            return
    if not st['seen_doctype'] and not st['seen_article'] and re.match(r'^V/v\b', text) and len(text) <= 250:
        style_par(p, 'center', first=0, before=6)  # trích yếu công văn: cỡ 12-13, canh giữa dưới số
        add_runs(p, runs, size=12)
        return
    if not st['seen_article'] and re.match(r'^Kính gửi\s*:', text) and len(text) <= 300:
        style_par(p, 'center', first=0)
        add_runs(p, runs)
        return
    if st['seen_doctype'] and not st['seen_article'] and RE_BASIS.match(text) and len(text) <= 800:  # "Căn cứ" nghiêng chỉ với văn bản có tên loại
        style_par(p, 'justify', first=INDENT_CM)
        add_runs(p, runs, italic=True)
        return
    if re.match(r'^Nơi nhận\s*:', text):
        st['in_recipients'] = True
        style_par(p, 'left', first=0, after=0)
        add_runs(p, runs, size=12, bold=True, italic=True)
        return
    if st['in_recipients'] and len(text) <= 200 and re.match(r'^[-–•]|^Lưu\s*:', text):
        style_par(p, 'left', first=0, after=0)
        add_runs(p, runs, size=SMALL_PT)
        return
    st['in_recipients'] = False
    if hint == 'center' and len(text) <= 200:
        style_par(p, 'center', first=0)
    elif hint == 'right' and len(text) <= 200:
        style_par(p, 'right', first=0)
    else:
        style_par(p, 'justify', first=INDENT_CM)
    add_runs(p, runs)


# ---------------------------------------------------------------- đối chiếu / verification
def _nonspace_len(s):
    return len(re.sub(r'\s+', '', s.replace('\xa0', ' ')))


def docx_text_chars(doc):
    return sum(_nonspace_len(el.text or '') for el in doc.element.body.iter(qn('w:t')))


def docx_body_lines(path):
    """Các dòng chữ của thân văn bản (theo đoạn, kể cả trong bảng), dùng để rút metadata."""
    _need_libs()
    d = Document(str(path))
    lines = []
    for p in d.element.body.iter(qn('w:p')):
        parts = []
        for x in p.iter():
            if x.tag == qn('w:t'):
                parts.append(x.text or '')
            elif x.tag == qn('w:br') or x.tag == qn('w:tab'):
                parts.append(' ')  # ngắt dòng cũ của nguồn = khoảng trắng
        t = re.sub(r'\s+', ' ', ''.join(parts)).strip()
        if t:
            lines.append(t)
    return lines


# ---------------------------------------------------------------- hàm chính / main
class UnsupportedHTML(ValueError):
    """Known content/structure loss: refuse before creating the output."""


def _validate_content(box):
    allowed = set('html body div section article center blockquote form p h1 h2 h3 h4 h5 h6 table thead tbody tfoot tr td th caption colgroup col span b strong i em a font br'.split())
    # Only text and tables are supported. Lists, media, maths, annotations and form
    # controls have semantics this renderer cannot preserve.
    nodes = ([] if box.name == '[document]' else [box]) + box.find_all(True)
    for node in nodes:
        if node.name not in allowed:
            raise UnsupportedHTML('Unsupported HTML content: <%s>' % node.name)
        node.__dict__['_law_inline_css'] = _parse_inline_css(node.get('style') or '')
        if node.has_attr('hidden'):
            raise UnsupportedHTML('Hidden content cannot be preserved')
    for tbl in box.find_all('table'):
        if tbl.find('table') is not None:
            raise UnsupportedHTML('Nested tables are unsupported')
        if tbl.find(['caption', 'col', 'colgroup']) is not None:
            raise UnsupportedHTML('Table captions/column definitions are unsupported')
        rows = rows_of(tbl)
        if not rows or len(rows) > 1000:
            raise UnsupportedHTML('Table row limit: 1..1000')
        occupied = set()
        layout = table_kind(tbl) in ('header', 'sign')
        for ri, row in enumerate(rows):
            ci = 0
            for cell in cells_of(row):
                while (ri, ci) in occupied:
                    ci += 1
                spans = []
                for attr in ('rowspan', 'colspan'):
                    raw = str(cell.get(attr, '1'))
                    if not re.fullmatch(r'[1-9][0-9]*', raw) or int(raw) > 64:
                        raise UnsupportedHTML('Invalid/oversized %s: %s (1..64)' % (attr, raw))
                    spans.append(int(raw))
                rs, cs = spans
                if ri + rs > len(rows) or ci + cs > 64 or (layout and (rs != 1 or cs != 1)):
                    raise UnsupportedHTML('Unsupported table span geometry')
                slots = {(r, c) for r in range(ri, ri + rs) for c in range(ci, ci + cs)}
                if slots & occupied:
                    raise UnsupportedHTML('Overlapping table spans')
                occupied.update(slots)
                ci += cs
        if not occupied:
            raise UnsupportedHTML('Empty table')


def html_to_docx(html_content, target_path, doc_title='', source_url=None, quiet=False, overwrite=False):
    """Render supported HTML text/tables. Refuse known loss before any output write.
    Default exclusive creation preserves existing files. Optional overwrite is explicit.
    The presentation is a local mechanical template, not legal or visual certification.
    """
    target_path = Path(target_path)
    if target_path.exists() and not overwrite:
        raise FileExistsError('Output exists; choose a new path or explicitly pass overwrite=True')
    _need_libs()
    soup = BeautifulSoup(html_content, 'html.parser')
    box = (soup.find('div', id='toanvancontent') or soup.find('div', id='divContentDoc')
           or soup.find('div', class_='content1'))
    whole_page = box is None
    if whole_page:
        box = soup.body or soup
    _validate_content(box)
    src_chars = _nonspace_len(box.get_text(' '))

    doc = new_document(doc_title, source_url)
    stats = {'tables': 0, 'dashes': 0, 'paras': 0}
    st = {'seen_article': False, 'expect_title': False, 'expect_sub': False, 'seen_doctype': False,
          'in_recipients': False}
    for kind, node in iter_blocks(box):
        if kind == 'table':
            k = table_kind(node)
            if k == 'header':
                render_header_table(doc, node, stats)
            elif k == 'sign':
                render_sign_table(doc, node, stats)
            elif k == 'data':
                render_data_table(doc, node, stats)
            continue
        runs = block_runs(kind, node)
        text = plain(runs)
        if not text:
            continue
        emit_paragraph(doc, runs, text, align_hint(node), st, stats)
        stats['paras'] += 1

    out_chars = docx_text_chars(doc)
    expected = src_chars - stats['dashes']
    ratio = (out_chars / float(expected)) if expected > 0 else 1.0
    if out_chars != expected:
        raise UnsupportedHTML('Text preservation check failed before write: expected %d, got %d' % (expected, out_chars))
    if expected <= 0:
        raise UnsupportedHTML('No supported text content')
    import io
    payload = io.BytesIO()
    doc.save(payload)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    # Serialize first; exclusive open also protects against an output appearing during rendering.
    with target_path.open('wb' if overwrite else 'xb') as stream:
        stream.write(payload.getvalue())
    stats.update({'src_chars': src_chars, 'docx_chars': out_chars, 'ratio': ratio, 'whole_page': whole_page})
    if not quiet:
        print('[+] Đã lưu tệp Word: %s (%s đoạn văn, %s bảng dữ liệu)' % (target_path, format(stats['paras'], ','), stats['tables']))
        print('    Đối chiếu ký tự (không tính khoảng trắng): nguồn %s, trừ %s ký tự gạch trang trí; file %s (%.1f%%)'
              % (format(src_chars, ','), stats['dashes'], format(out_chars, ','), ratio * 100))
        if whole_page:
            print('[!] Cảnh báo: không thấy khung nội dung văn bản (toanvancontent/divContentDoc/content1); đã dựng từ cả trang, '
                  'có thể lẫn menu, quảng cáo, chân trang — cần mở xem và xóa phần thừa.')
    return stats['paras']


def spec_check():
    """Đối chiếu ND30_RULES và hằng số với nd30-presentation.md; trả về danh sách lỗi (rỗng nếu khớp hoặc không có file).
    Compare ND30_RULES and the constants with the specification file; returns a list of errors."""
    errs = []
    if not SPEC_FILE.is_file():
        return errs, False
    t = SPEC_FILE.read_text(encoding='utf-8')
    m = re.search(r'Trên và dưới (\d+)\s*-\s*(\d+) mm; trái (\d+)\s*-\s*(\d+) mm; phải (\d+)\s*-\s*(\d+) mm', t)
    if not m:
        errs.append('không tìm thấy dòng lề trong nd30-presentation.md (đổi định dạng file thông số?)')
    else:
        v = [int(x) for x in m.groups()]
        want = {'top': (v[0], v[1]), 'bottom': (v[0], v[1]), 'left': (v[2], v[3]), 'right': (v[4], v[5])}
        if want != ND30_RULES['margins_mm']:
            errs.append('lề trong ND30_RULES lệch file thông số: %r vs %r' % (ND30_RULES['margins_mm'], want))
    m = re.search(r'canh đều hai lề, đứng, cỡ (\d+)\s*-\s*(\d+); đầu dòng lùi ([\d,]+) cm hoặc ([\d,]+) cm; .*?tối thiểu (\d+)pt; .*?tối đa ([\d,]+) lines', t)
    if not m:
        errs.append('không tìm thấy dòng "Nội dung" trong nd30-presentation.md')
    else:
        f = lambda x: float(x.replace(',', '.'))
        got = ((int(m.group(1)), int(m.group(2))), (f(m.group(3)), f(m.group(4))), int(m.group(5)), f(m.group(6)))
        have = (ND30_RULES['body_pt'], ND30_RULES['indent_cm'], ND30_RULES['after_pt_min'], ND30_RULES['line_spacing_max'])
        if got != have:
            errs.append('cỡ chữ/đầu dòng/cách đoạn/cách dòng trong ND30_RULES lệch file thông số: %r vs %r' % (have, got))
    if ND30_RULES['font'] not in t:
        errs.append('file thông số không nhắc phông %s' % ND30_RULES['font'])
    # hằng số của công cụ phải nằm trong khoảng cho phép / the tool's constants must sit inside the ranges
    for k, mm in zip(('top', 'bottom', 'left', 'right'), MARGINS_CM):
        lo, hi = ND30_RULES['margins_mm'][k]
        if not lo <= mm * 10 <= hi:
            errs.append('lề %s %.0f mm ngoài khoảng %d-%d' % (k, mm * 10, lo, hi))
    if FONT != ND30_RULES['font'] or not ND30_RULES['body_pt'][0] <= BODY_PT <= ND30_RULES['body_pt'][1]:
        errs.append('phông/cỡ chữ ngoài khoảng cho phép')
    if INDENT_CM not in ND30_RULES['indent_cm'] or AFTER_PT < ND30_RULES['after_pt_min'] or LINE_SPACING > ND30_RULES['line_spacing_max']:
        errs.append('đầu dòng/cách đoạn/cách dòng ngoài khoảng cho phép')
    return errs, True


def selftest():
    """Synthetic smoke only; no claim about a legal source or visual layout."""
    _need_libs()
    errors, found = spec_check()
    if not found:
        print('NOT CHECKED: local nd30-presentation.md reference missing')
        return 2
    if errors:
        print('\n'.join(errors))
        return 1
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'sample.docx'
        html_to_docx('<p>Điều 1. Nội dung thử tổng hợp.</p>', out, quiet=True)
        d = Document(str(out))
        assert d.paragraphs[0].text == 'Điều 1. Nội dung thử tổng hợp.'
        assert d.core_properties.subject == ''
    print('OK: synthetic DOCX smoke and local presentation constants (not visual/legal verification)')
    return 0


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description='Render supported HTML text/tables with the local administrative layout (optional dependencies).')
    ap.add_argument('input', nargs='?', help='file .html nguồn')
    ap.add_argument('output', nargs='?', help='file .docx đầu ra (không ghi đè nếu đã có, trừ khi --overwrite)')
    ap.add_argument('--title', default='')
    ap.add_argument('--url', default=None, help='URL nguồn, ghi vào thuộc tính tài liệu')
    ap.add_argument('--overwrite', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        try:
            return selftest()
        except ImportError as exc:
            print('NOT CHECKED: %s' % exc, file=sys.stderr)
            return 2
    if not a.input or not a.output:
        ap.print_help()
        sys.exit(2)
    try:
        if Path(a.input).resolve() == Path(a.output).resolve():
            raise ValueError('Input and output must be different files')
        html = Path(a.input).read_text(encoding='utf-8')
        html_to_docx(html, a.output, a.title, a.url, overwrite=a.overwrite)
    except (ImportError, OSError, ValueError) as exc:
        print('NOT CHECKED / no conversion: %s' % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
