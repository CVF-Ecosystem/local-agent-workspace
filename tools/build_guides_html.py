#!/usr/bin/env python3
"""Dựng lại phần nội dung các trang HTML hướng dẫn từ Markdown (tiếng Việt và tiếng Anh).

Chỉ dùng thư viện chuẩn của Python 3.8+. Không cần cài đặt, không dùng mạng.

    python tools/build_guides_html.py            # ghi lại HTML
    python tools/build_guides_html.py --check    # chỉ kiểm tra; thoát mã 1 nếu HTML lệch Markdown

Với mỗi ngôn ngữ trong LOCALES, script cập nhật các trang HTML có sẵn ở những vùng sau và giữ
nguyên mọi thứ còn lại (khung trang, CSS, JavaScript, thanh bên, thẻ chọn phần, số liệu tổng
quan, chân trang; những phần này sửa tay, xem tools/README.md):
    - thân bài ("chapter-body") và mục lục của phần ("chapter-toc");
    - tiêu đề "# ..." đầu file Markdown: <h1> của trang riêng, <title>, tiêu đề chương
      ("chapter-title") trong START_HERE;
    - thẻ <meta name="source-sha256">: mã băm SHA-256 của nguồn Markdown (trang riêng: file
      Markdown của trang đó; START_HERE: các file Markdown nối bằng "\\n" theo thứ tự trong cấu hình).

Phần Markdown được hỗ trợ (đủ cho các hướng dẫn hiện có):
    "# " tiêu đề đầu file, "## " mục, đoạn văn, danh sách "- ", bảng "|", khối mã ```,
    `mã nội tuyến`, **đậm**, địa chỉ http(s) trần thành liên kết.
Cú pháp khác (### , danh sách đánh số, *nghiêng*, ảnh, liên kết [chữ](url)) chưa được hỗ trợ;
script dừng và báo dòng gây lỗi thay vì dựng sai.
"""
import hashlib
import io
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Mỗi ngôn ngữ: file START_HERE, thư mục trang riêng, các hướng dẫn (tên file Markdown không đuôi,
# tiền tố id chương trong START_HERE), file nguồn tham khảo và các chuỗi do script sinh ra.
LOCALES = [
    {
        'code': 'vi',
        'start': 'START_HERE.html',
        'docs_dir': 'docs',
        'docs': [
            ('HUONG_DAN_TAO_PROJECT_MOI_VI', 'project-moi'),
            ('HUONG_DAN_SU_DUNG_VI', 'hang-ngay'),
            ('HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI', 'project-cu'),
            ('HUONG_DAN_SKILLS_VI', 'skills'),
        ],
        'sources': ('NGUON_THAM_KHAO_VI', 'nguon'),
        'strings': {
            'code_label': 'Ví dụ để sử dụng',
            'copy_aria': 'Sao chép nội dung ví dụ',
            'copy_btn': 'Sao chép',
            'table_aria': 'Bảng tham khảo, có thể cuộn ngang trên màn hình nhỏ',
            'toc_summary': 'Nội dung trong phần này',
        },
    },
    {
        'code': 'en',
        'start': 'START_HERE.en.html',
        'docs_dir': 'docs/en',
        'docs': [
            ('NEW_PROJECT_GUIDE', 'new-project'),
            ('DAILY_USE_GUIDE', 'daily-use'),
            ('EXISTING_PROJECT_UPGRADE_GUIDE', 'existing-project'),
            ('SKILLS_GUIDE', 'skills'),
        ],
        'sources': ('SOURCES_AND_REFERENCES', 'sources'),
        'strings': {
            'code_label': 'Example to use',
            'copy_aria': 'Copy the example text',
            'copy_btn': 'Copy',
            'table_aria': 'Reference table, scrolls horizontally on small screens',
            'toc_summary': 'In this section',
        },
    },
]


class BuildError(Exception):
    pass


def slug(text):
    s = unicodedata.normalize('NFD', text.replace('đ', 'd').replace('Đ', 'D'))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


URL_RE = re.compile(r'https?://[^\s<>`]+')


def inline(s):
    out = []
    for part in re.split(r'(`[^`]+`)', s):
        if len(part) > 1 and part.startswith('`') and part.endswith('`'):
            out.append('<code>' + esc(part[1:-1]) + '</code>')
            continue
        e = esc(part)
        e = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', e)
        e = URL_RE.sub(lambda m: '<a href="%s" rel="noopener noreferrer" target="_blank">%s</a>' % (m.group(0), m.group(0)), e)
        out.append(e)
    return ''.join(out)


def split_row(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def convert(md, prefix, heading_tag, source, strings):
    """Markdown -> (tiêu đề H1, html thân bài, danh sách (id, tiêu đề) các mục)."""
    lines = md.replace('\r\n', '\n').split('\n')
    blocks, heads, para = [], [], []
    title = ''
    i = 0
    if lines and lines[0].startswith('# '):
        title = lines[0][2:].strip()
        i = 1
    if not title:
        raise BuildError('%s: thiếu tiêu đề "# " ở dòng đầu' % source)

    def flush():
        if para:
            blocks.append('<p>' + inline('\n'.join(para)) + '</p>')
            para.clear()

    def fail(n, why):
        raise BuildError('%s, dòng %d: %s: %r' % (source, n + 1, why, lines[n][:60]))

    while i < len(lines):
        ln = lines[i]
        if ln.startswith('```'):
            flush()
            start = i
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i])
                i += 1
            if i >= len(lines):
                fail(start, 'khối mã không đóng')
            i += 1
            blocks.append(
                '<div class="code-box"><span class="code-label">%s</span>'
                '<button aria-label="%s" class="copy-btn" type="button">%s</button>'
                '<pre><code class="language-text">%s\n</code></pre></div>'
                % (strings['code_label'], strings['copy_aria'], strings['copy_btn'], esc('\n'.join(buf))))
            continue
        if ln.startswith('## '):
            flush()
            text = ln[3:].strip()
            hid = prefix + '-' + slug(text)
            heads.append((hid, text))
            blocks.append('<%s id="%s">%s</%s>' % (heading_tag, hid, inline(text), heading_tag))
            i += 1
            continue
        if ln.startswith('#'):
            fail(i, 'cấp tiêu đề chưa hỗ trợ')
        if ln.startswith('|'):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i])
                i += 1
            if len(rows) < 3:
                fail(i - 1, 'bảng thiếu dòng')
            head = split_row(rows[0])
            h = ('<div aria-label="%s" class="table-scroll" role="region" tabindex="0"><table>\n<thead>\n<tr>\n'
                 % strings['table_aria'])
            h += ''.join('<th scope="col">%s</th>\n' % inline(c) for c in head)
            h += '</tr>\n</thead>\n<tbody>\n'
            for r in rows[2:]:
                cells = split_row(r)
                if len(cells) != len(head):
                    raise BuildError('%s: hàng bảng có %d ô, tiêu đề có %d: %r' % (source, len(cells), len(head), r[:60]))
                h += '<tr>\n' + ''.join('<td>%s</td>\n' % inline(c) for c in cells) + '</tr>\n'
            blocks.append(h + '</tbody>\n</table></div>')
            continue
        if ln.startswith('- '):
            flush()
            items = []
            while i < len(lines) and (lines[i].startswith('- ') or (lines[i].startswith('  ') and items and lines[i].strip())):
                if lines[i].startswith('- '):
                    items.append(lines[i][2:])
                else:
                    items[-1] += '\n' + lines[i].strip()
                i += 1
            blocks.append('<ul>\n' + ''.join('<li>%s</li>\n' % inline(it) for it in items) + '</ul>')
            continue
        if re.match(r'\d+\. ', ln):
            fail(i, 'danh sách đánh số chưa hỗ trợ (viết thành đoạn hoặc danh sách "- ")')
        if re.search(r'(?<!\*)\*(?!\*)', ln.replace('`', '')) and not re.search(r'`[^`]*\*[^`]*`', ln):
            fail(i, 'chữ nghiêng "*" chưa hỗ trợ')
        if re.search(r'\]\(', ln):
            fail(i, 'liên kết [chữ](url) chưa hỗ trợ; dùng địa chỉ trần')
        if ln.strip() == '':
            flush()
        else:
            para.append(ln)
        i += 1
    flush()
    return title, '\n'.join(blocks) + '\n', heads


def toc_html(heads, strings):
    return ('<details class="chapter-toc"><summary>%s</summary><ul>' % strings['toc_summary']
            + ''.join('<li><a href="#%s">%s</a></li>' % (h, inline(t)) for h, t in heads) + '</ul></details>')


def read(path):
    return io.open(path, encoding='utf-8', newline='').read()


def read_bytes(path):
    return Path(path).read_bytes()


def find(t, marker, start, path):
    k = t.find(marker, start)
    if k < 0:
        raise BuildError('%s: không tìm thấy mốc %r (khung HTML đã bị đổi?)' % (path, marker))
    return k


def set_meta_hash(t, digest, path):
    new, n = re.subn(r'(<meta name="source-sha256" content=")[0-9a-f]*(">)', r'\g<1>%s\g<2>' % digest, t, count=1)
    if n != 1:
        raise BuildError('%s: thiếu thẻ <meta name="source-sha256">' % path)
    return new


def set_title(t, title, path):
    new, n = re.subn(r'(<title>)[^<]*?( · [^<]*</title>)', lambda m: m.group(1) + esc(title) + m.group(2), t, count=1)
    if n != 1:
        raise BuildError('%s: không nhận ra <title>' % path)
    return new


def rebuild_standalone(loc, md_name, prefix):
    """Trang riêng <docs_dir>/<tên>.html."""
    path = ROOT / loc['docs_dir'] / (md_name + '.html')
    md_path = ROOT / loc['docs_dir'] / (md_name + '.md')
    t = read(path)
    title, body, heads = convert(read(md_path), prefix, 'h2', md_name + '.md', loc['strings'])
    a = find(t, '<details class="chapter-toc">', 0, path)
    b = find(t, '</article>', a, path) + len('</article>')
    new = (toc_html(heads, loc['strings'])
           + '<article class="chapter-body single-body" data-source-md="%s.md">\n' % md_name + body + '</article>')
    t = t[:a] + new + t[b:]
    # tiêu đề: <h1> trong single-hero và <title>
    h0 = find(t, '<header class="single-hero">', 0, path)
    h1a = find(t, '<h1>', h0, path)
    h1b = find(t, '</h1>', h1a, path)
    t = t[:h1a] + '<h1>' + inline(title) + t[h1b:]
    t = set_title(t, title, path)
    return path, set_meta_hash(t, hashlib.sha256(read_bytes(md_path)).hexdigest(), path)


def rebuild_start_here(loc):
    path = ROOT / loc['start']
    t = read(path)
    strings = loc['strings']
    sources = []
    for md_name, prefix in loc['docs']:
        md_path = ROOT / loc['docs_dir'] / (md_name + '.md')
        title, body, heads = convert(read(md_path), prefix, 'h3', md_name + '.md', strings)
        sources.append(read_bytes(md_path))
        start = find(t, '<section class="chapter" id="%s"' % prefix, 0, path)
        ta = find(t, '<h2 class="chapter-title">', start, path)
        tb = find(t, '</h2>', ta, path)
        t = t[:ta] + '<h2 class="chapter-title">' + inline(title) + t[tb:]
        a = find(t, '<details class="chapter-toc">', start, path)
        b = find(t, '</div></section>', a, path) + len('</div></section>')
        t = t[:a] + toc_html(heads, strings) + '<div class="chapter-body">\n' + body + '</div></section>' + t[b:]
    src_name, src_prefix = loc['sources']
    md_path = ROOT / loc['docs_dir'] / (src_name + '.md')
    _, body, _ = convert(read(md_path), src_prefix, 'h2', src_name + '.md', strings)
    sources.append(read_bytes(md_path))
    start = find(t, '<details class="references-block"', 0, path)
    a = find(t, '<div class="chapter-body">', start, path)
    b = find(t, '</div></details>', a, path) + len('</div></details>')
    t = t[:a] + '<div class="chapter-body">\n' + body + '</div></details>' + t[b:]
    return path, set_meta_hash(t, hashlib.sha256(b'\n'.join(sources)).hexdigest(), path)


def main(argv):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    unknown = [a for a in argv if a not in ('--check',)]
    if unknown:
        print('Tham số không hợp lệ: %s\nDùng: python tools/build_guides_html.py [--check]' % ' '.join(unknown))
        return 2
    check = '--check' in argv
    outputs = {}
    skipped = []
    try:
        for loc in LOCALES:
            if not (ROOT / loc['start']).exists():
                skipped.append(loc['code'])
                continue
            for md_name, prefix in loc['docs']:
                p, new = rebuild_standalone(loc, md_name, prefix)
                outputs[p] = new
            p, new = rebuild_start_here(loc)
            outputs[p] = new
    except (BuildError, OSError) as e:
        print('LỖI:', e)
        return 2
    if skipped:
        print('Bỏ qua ngôn ngữ chưa có START_HERE: ' + ', '.join(skipped))
    stale = [p for p, new in outputs.items() if read(p) != new]
    if check:
        if stale:
            print('HTML lệch Markdown ở: ' + ', '.join(str(p.relative_to(ROOT)) for p in stale))
            print('Chạy: python tools/build_guides_html.py')
            return 1
        print('HTML đã khớp Markdown (%d trang).' % len(outputs))
        return 0
    for p in stale:
        io.open(p, 'w', encoding='utf-8', newline='').write(outputs[p])
    print('Đã cập nhật %d trang; %d trang không đổi.' % (len(stale), len(outputs) - len(stale)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
