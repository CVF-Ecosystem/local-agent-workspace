#!/usr/bin/env python3
"""Khởi tạo project mới từ package (chạy một lần sau khi giải nén và đổi tên thư mục).

Dùng:
  python tools/init_project.py --name "Tên project" [--lang vi|en] [--dry-run] [--force]

Việc script làm:
  - điền tên project vào PROJECT.md;
  - với --lang en: chép đè toàn bộ cây en/ (hướng dẫn agent, ghi chú .agent, skill, README) lên thư mục
    gốc, trừ en/PROJECT_INSTRUCTIONS_SNIPPET.md. File của package bị thay mà đã bị sửa được sao lưu thành
    <tên>.bak-<ngày>; file của người dùng (PROJECT, STATE, HANDOFF, INDEX...) đã điền thì giữ nguyên;
  - nếu có --purpose/--outputs/--style/--sources/--constraints/--sensitivity: điền các dòng tương ứng trong PROJECT.md;
  - đặt .agent/STATE.md sạch;
  - ghi .agent/PACKAGE_INFO.json (phiên bản package, ngôn ngữ, ngày khởi tạo).
Script không xóa file nào và không dùng mạng. Chỉ cần Python 3.8+.
"""
import argparse, datetime, io, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERLAY_SKIP = {'en/PROJECT_INSTRUCTIONS_SNIPPET.md'}

def overlay_pairs():
    """Mọi file trong en/ (trừ OVERLAY_SKIP) và đường dẫn đích ở thư mục gốc."""
    out = []
    base = P('en')
    for d, dirs, files in os.walk(base):
        dirs.sort()
        for f in sorted(files):
            src = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/')
            if src in OVERLAY_SKIP or f.endswith('.bak') or '.bak-' in f:
                continue
            out.append((src, src[3:]))
    return out
FIELDS = [('purpose', ('Mục đích và người đọc', 'Purpose and audience')),
          ('outputs', ('Đầu ra mong đợi', 'Expected outputs')),
          ('style', ('Ngôn ngữ và văn phong', 'Language and house style')),
          ('sources', ('Nguồn / mẫu đã duyệt chính', 'Main sources / approved templates')),
          ('constraints', ('Ràng buộc quan trọng', 'Important constraints')),
          ('sensitivity', ('Mức nhạy cảm dữ liệu', 'Data sensitivity'))]
USER_TEMPLATES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
                  '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md'}
NAME_LINE = {'vi': '- Tên dự án: [Tên]', 'en': '- Project name: [Name]'}
PHASE_PLACEHOLDER = {'vi': '[Phase/trạng thái hiện tại]', 'en': '[Current phase/status]'}
PHASE_TEXT = {'vi': 'Mới khởi tạo từ package v%s ngày %s; chưa có công việc.',
              'en': 'Just initialised from package v%s on %s; no work yet.'}

LANG = 'vi'
def L(vi, en): return en if LANG == 'en' else vi

def P(rel): return os.path.join(ROOT, *rel.split('/'))
def rd(rel): return io.open(P(rel), encoding='utf-8', newline='').read()
def wr(rel, text):
    os.makedirs(os.path.dirname(P(rel)), exist_ok=True)
    io.open(P(rel), 'w', encoding='utf-8', newline='').write(text)

def is_original(rel):
    """True nếu file còn đúng như trong package (theo MANIFEST), nên không cần sao lưu khi thay."""
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import check_package as cp
        m = cp.read_manifest()
        return bool(m) and rel in m and cp.sha(rel) == m[rel]
    except Exception:
        return False

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', required=True, help='tên project / project name')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    for k, labels in FIELDS:
        ap.add_argument('--' + k, default='', help='điền dòng "%s" trong PROJECT.md / fill the "%s" line' % labels)
    ap.add_argument('--dry-run', action='store_true', help='chỉ in việc sẽ làm, không ghi')
    ap.add_argument('--force', action='store_true', help='chạy lại trên project đã khởi tạo')
    a = ap.parse_args()
    global LANG
    LANG = a.lang
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    name = a.name.strip()
    if not name:
        sys.exit(L('Tên project không được để trống.', 'The project name must not be empty.'))
    if not os.path.isfile(P('VERSION')) or not os.path.isfile(P('PROJECT.md')):
        sys.exit(L('Không thấy VERSION hoặc PROJECT.md: hãy chạy script trong thư mục package đã giải nén.', 'VERSION or PROJECT.md not found: run the script inside the unzipped package folder.'))
    info_path = '.agent/PACKAGE_INFO.json'
    if os.path.exists(P(info_path)) and not a.force:
        sys.exit(L('Project đã được khởi tạo (có %s). Thêm --force nếu thật sự muốn chạy lại.', 'The project is already initialized (%s exists). Add --force if you really want to run again.') % info_path)
    ver = rd('VERSION').strip()
    today = datetime.date.today().isoformat()
    stamp = today.replace('-', '')
    log = []

    def do(msg, fn):
        log.append(msg)
        if not a.dry_run:
            fn()

    def do_quiet(fn):
        if not a.dry_run:
            fn()

    def pristine(dst):
        """File còn ở dạng mẫu (chưa điền) thì được thay bằng bản tiếng Anh."""
        cur = rd(dst)
        if is_original(dst):
            return True
        if dst == 'PROJECT.md':
            return any(l in cur for l in NAME_LINE.values())
        if dst == '.agent/STATE.md':
            return any(p in cur for p in PHASE_PLACEHOLDER.values())
        if dst == '.agent/HANDOFF.md':
            return '\nNone' in cur[:40]
        if dst in USER_TEMPLATES:
            return False
        return True

    if a.lang == 'en':
        pairs = overlay_pairs()
        if not pairs:
            sys.exit(L('Thiếu thư mục en/ trong package.', 'The en/ folder is missing from the package.'))
        swapped = 0
        for src, dst in pairs:
            new = rd(src)
            old = rd(dst) if os.path.isfile(P(dst)) else None
            if old == new:
                continue
            if old is not None and not pristine(dst):
                log.append(L('Giữ nguyên %s (đã có nội dung của bạn).', 'Kept %s (it has your own content).') % dst)
                continue
            keep = old is not None and dst not in USER_TEMPLATES and not is_original(dst)
            def swap(src=src, dst=dst, new=new, keep=keep):
                if keep:
                    shutil.copyfile(P(dst), P(dst) + '.bak-' + stamp)
                wr(dst, new)
            swapped += 1
            if keep or dst in USER_TEMPLATES or swapped <= 6:
                log.append(L('Chép %s -> %s', 'Copied %s -> %s') % (src, dst) +
                           (L(' (sao lưu bản cũ .bak-%s)', ' (old copy saved as .bak-%s)') % stamp if keep else ''))
            do_quiet(swap)
        if swapped > 6:
            log.append(L('... và %d file khác trong en/ (tổng %d file đã chép).', '... and %d more files from en/ (%d copied in total).') % (max(swapped - 6, 0), swapped))

    # Nội dung PROJECT.md / STATE.md như sẽ có sau bước chép (để --dry-run báo đúng)
    def future(dst):
        if a.lang == 'en' and a.dry_run and os.path.isfile(P('en/' + dst)) and pristine(dst):
            return rd('en/' + dst)
        return rd(dst)

    line = NAME_LINE[a.lang]
    if line in future('PROJECT.md'):
        def fill():
            cur = rd('PROJECT.md')
            if line in cur:
                wr('PROJECT.md', cur.replace(line, line.split('[')[0] + name, 1))
        do(L('Điền tên project vào PROJECT.md', 'Fill the project name into PROJECT.md'), fill)
    else:
        log.append(L('Cảnh báo: PROJECT.md không còn dòng "%s" (đã điền tay?); bỏ qua bước điền tên.', 'Warning: PROJECT.md no longer has the line "%s" (filled in by hand?); skipping the name step.') % line)

    for k, labels in FIELDS:
        val = getattr(a, k).strip().replace('\n', ' ')
        if not val:
            continue
        label = labels[0 if a.lang == 'vi' else 1]
        pat = re.compile(r'^(- %s: )\[[^\n]*\]$' % re.escape(label), re.M)
        if pat.search(future('PROJECT.md')):
            def fill_field(pat=pat, val=val):
                cur = rd('PROJECT.md')
                wr('PROJECT.md', pat.sub(lambda m: m.group(1) + val, cur, count=1))
            do(L('Điền "%s" vào PROJECT.md', 'Fill "%s" into PROJECT.md') % label, fill_field)
        else:
            log.append(L('Bỏ qua "%s": dòng này trong PROJECT.md đã có nội dung.', 'Skipped "%s": that line in PROJECT.md already has content.') % label)

    ph = PHASE_PLACEHOLDER[a.lang]
    if ph in future('.agent/STATE.md'):
        def state():
            cur = rd('.agent/STATE.md')
            if ph in cur:
                wr('.agent/STATE.md', cur.replace(ph, PHASE_TEXT[a.lang] % (ver, today), 1))
        do(L('Đặt trạng thái khởi đầu trong .agent/STATE.md', 'Set the starting state in .agent/STATE.md'), state)
    else:
        if L('Giữ nguyên .agent/STATE.md (đã có nội dung của bạn).', 'Kept .agent/STATE.md (it has your own content).') not in log:
            log.append(L('Giữ nguyên .agent/STATE.md (đã có nội dung của bạn).', 'Kept .agent/STATE.md (it has your own content).'))

    info = {'package': 'local-agent-workspace', 'version': ver, 'language': a.lang,
            'project_name': name, 'initialized': today}
    do(L('Ghi %s', 'Wrote %s') % info_path, lambda: wr(info_path, json.dumps(info, ensure_ascii=False, indent=2) + '\n'))

    print((L('[CHẠY THỬ, chưa ghi gì] ', '[DRY RUN, nothing written] ') if a.dry_run else '') + L('Khởi tạo project "%s" (package v%s, ngôn ngữ %s):', 'Initializing project "%s" (package v%s, language %s):') % (name, ver, a.lang))
    for m in log:
        print(' - ' + m)
    if not a.dry_run:
        print(L('\nXong. Việc tiếp theo: mở PROJECT.md điền mục đích, người đọc, đầu ra; sau đó giao việc đầu tiên cho agent.', '\nDone. Next: open PROJECT.md and fill in the purpose, readers and outputs; then give the agent the first task.'))
        print('Nếu dùng Project/cloud: dán đoạn hướng dẫn trong mục 5 của docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md'
              if a.lang == 'vi' else
              'If you use a Project/cloud: paste the text in section 5 of docs/en/NEW_PROJECT_GUIDE.md')

if __name__ == '__main__':
    main()
