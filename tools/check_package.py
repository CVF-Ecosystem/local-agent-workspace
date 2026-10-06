#!/usr/bin/env python3
"""Kiểm tra package và quản lý MANIFEST.sha256. Chỉ cần Python 3.8+, không dùng mạng.

Dùng (chạy từ thư mục gốc của package/project):
  python tools/check_package.py                  kiểm tra chất lượng package
  python tools/check_package.py --release        thêm kiểm tra "sạch để phát hành" (mẫu chưa điền, không dữ liệu project)
  python tools/check_package.py --write-manifest ghi MANIFEST.sha256 (người bảo trì package dùng)
  python tools/check_package.py --verify         so file của project với MANIFEST.sha256: file nào của package đã bị sửa

Mã thoát: 0 đạt; 1 có lỗi (chế độ kiểm tra) hoặc có file đã đổi/thiếu (--verify); 2 lỗi dùng.
"""
import argparse, ast, hashlib, io, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = ('.md', '.html', '.py', '.json', '.txt', '.sha256', '.css', '.js', '')
SKIP_DIRS = {'.git', '__pycache__', 'dist', 'node_modules'}
# File người dùng sửa trong project: không đưa vào MANIFEST
USER_FILES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
              '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md', '.agent/PACKAGE_INFO.json', 'setup_answers.json'}
USER_DIRS = ('working/', 'output/', 'archive/', 'references/', 'skills/external/', 'skills/inbox/', 'skills/local/project/', 'skills/local/packs/')
OVERLAY_SKIP = {'en/PROJECT_INSTRUCTIONS_SNIPPET.md'}
PAIRS = [('AGENTS.md', 'en/AGENTS.md'), ('PROJECT.md', 'en/PROJECT.md'),
         ('docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md', 'docs/en/NEW_PROJECT_GUIDE.md'),
         ('docs/HUONG_DAN_SU_DUNG_VI.md', 'docs/en/DAILY_USE_GUIDE.md'),
         ('docs/HUONG_DAN_SKILLS_VI.md', 'docs/en/SKILLS_GUIDE.md'),
         ('docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md', 'docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md'),
         ('docs/NGUON_THAM_KHAO_VI.md', 'docs/en/SOURCES_AND_REFERENCES.md')]
GENERATED = {'.agent/PACKAGE_INFO.json', 'MANIFEST.sha256'}
# Mỗi file trong en/ (trừ OVERLAY_SKIP) thay cho file cùng đường dẫn không có tiền tố en/

def P(rel): return os.path.join(ROOT, *rel.split('/'))
def rd(rel): return io.open(P(rel), encoding='utf-8', newline='').read()

def all_files():
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/')
            if f.endswith(('.pyc', '.bak')) or '.bak-' in f:
                continue
            out.append(rel)
    return out

def in_manifest(rel):
    if rel in GENERATED:
        return False
    if rel.startswith(USER_DIRS):
        return os.path.basename(rel) == 'README.md'
    return True

def sha(rel):
    data = open(P(rel), 'rb').read()
    if os.path.splitext(rel)[1] in TEXT_EXT:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()

# ---------------------------------------------------------------- manifest
def write_manifest():
    lines = ['%s  %s' % (sha(r), r) for r in all_files() if in_manifest(r)]
    io.open(P('MANIFEST.sha256'), 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
    print('Đã ghi MANIFEST.sha256 (%d file).' % len(lines))

def read_manifest():
    if not os.path.isfile(P('MANIFEST.sha256')):
        return None
    m = {}
    for l in rd('MANIFEST.sha256').splitlines():
        if l.strip():
            h, p = l.split('  ', 1)
            m[p] = h
    return m

def verify():
    m = read_manifest()
    if m is None:
        print('Không có MANIFEST.sha256 trong thư mục này.')
        return 2
    lang = 'vi'
    if os.path.isfile(P('.agent/PACKAGE_INFO.json')):
        try:
            lang = json.loads(rd('.agent/PACKAGE_INFO.json')).get('language', 'vi')
        except ValueError:
            pass
    changed, missing = [], []
    for rel, h in sorted(m.items()):
        if rel in USER_FILES:
            continue  # file người dùng sửa: có trong MANIFEST chỉ để biết còn nguyên bản mẫu hay chưa
        if not os.path.isfile(P(rel)):
            missing.append(rel); continue
        ov = 'en/' + rel
        exp = m[ov] if (lang == 'en' and ov in m and ov not in OVERLAY_SKIP) else h
        if sha(rel) != exp:
            changed.append(rel)
    ver = rd('VERSION').strip() if os.path.isfile(P('VERSION')) else '?'
    print('So với MANIFEST của package v%s (ngôn ngữ %s): %d file đã đổi, %d file thiếu.' % (ver, lang, len(changed), len(missing)))
    for x in changed: print('  ĐÃ SỬA : ' + x)
    for x in missing: print('  THIẾU  : ' + x)
    if changed or missing:
        print('Gợi ý: file đã sửa có thể là chủ ý của bạn; khi nâng cấp hãy hợp nhất thay vì ghi đè.')
    return 1 if (changed or missing) else 0

# ---------------------------------------------------------------- checks
def frontmatter(text):
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        return None
    fm = {}
    cur = None
    for l in m.group(1).split('\n'):
        k = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', l)
        if k and not l.startswith(' '):
            cur = k.group(1); fm[cur] = k.group(2).strip().strip('>-').strip()
        elif cur and l.strip():
            fm[cur] = (fm.get(cur, '') + ' ' + l.strip()).strip()
    return fm

def strip_fences(t):
    return re.sub(r'```.*?```', '', t, flags=re.S)

def check_all(release=False):
    errs, warns = [], []
    files = all_files()
    md = [f for f in files if f.endswith('.md')]
    # 1. VERSION
    ver = rd('VERSION').strip() if os.path.isfile(P('VERSION')) else ''
    if not re.fullmatch(r'\d+\.\d+\.\d+', ver):
        errs.append('VERSION thiếu hoặc sai định dạng MAJOR.MINOR.PATCH (đang là %r).' % ver)
        return errs, warns
    maj_min = '.'.join(ver.split('.')[:2])
    # 2. chuỗi phiên bản nhất quán
    vre = re.compile(r'(?<![\w.])v(\d+)\.(\d+)(?:\.(\d+))?(?![\w.])')
    for f in files:
        if f in ('CHANGELOG.md', 'MANIFEST.sha256') or not f.endswith(('.md', '.html', '.py', '.json')):
            continue
        for m in vre.finditer(rd(f)):
            got = '%s.%s' % (m.group(1), m.group(2))
            if got != maj_min or (m.group(3) is not None and m.group(0)[1:] != ver):
                errs.append('%s: số phiên bản "%s" không khớp VERSION (%s).' % (f, m.group(0), ver)); break
    if not re.search(r'^## v%s - ' % re.escape(ver), rd('CHANGELOG.md'), re.M) and \
       not re.search(r'^## v%s — ' % re.escape(ver), rd('CHANGELOG.md'), re.M):
        errs.append('CHANGELOG.md chưa có mục cho v%s.' % ver)
    # 3. skill
    shared = 'skills/local/shared/'
    sk = sorted(d for d in os.listdir(P(shared)) if os.path.isfile(P(shared + d + '/SKILL.md')))
    for d in sk:
        fm = frontmatter(rd(shared + d + '/SKILL.md'))
        if fm is None:
            errs.append('%s%s/SKILL.md thiếu frontmatter.' % (shared, d)); continue
        if fm.get('name') != d: errs.append('%s%s: name "%s" không khớp tên thư mục.' % (shared, d, fm.get('name')))
        if len(fm.get('description', '')) < 40: errs.append('%s%s: description thiếu hoặc quá ngắn.' % (shared, d))
        if not any(k in fm.get('description', '') for k in ('Kích hoạt khi', 'Triggers when')): warns.append('%s%s: description chưa có cụm kích hoạt ("Kích hoạt khi" / "Triggers when").' % (shared, d))
        if not re.search(r'^\s+version:\s*"?\d', rd(shared + d + '/SKILL.md'), re.M): errs.append('%s%s: thiếu metadata.version.' % (shared, d))
        # bản tiếng Anh của skill
        en = 'en/' + shared + d + '/SKILL.md'
        if not os.path.isfile(P(en)):
            errs.append('Thiếu bản tiếng Anh %s.' % en); continue
        efm = frontmatter(rd(en)) or {}
        if efm.get('name') != d: errs.append('%s: name "%s" không khớp tên thư mục.' % (en, efm.get('name')))
        if len(efm.get('description', '')) < 40: errs.append('%s: description thiếu hoặc quá ngắn.' % en)
        if 'Triggers when' not in efm.get('description', ''): warns.append('%s: description chưa có cụm "Triggers when".' % en)
        if not re.search(r'^\s+version:\s*"?\d', rd(en), re.M): errs.append('%s: thiếu metadata.version.' % en)
        va, ve = re.search(r'^\s+version:\s*"?([\d.]+)', rd(shared + d + '/SKILL.md'), re.M), re.search(r'^\s+version:\s*"?([\d.]+)', rd(en), re.M)
        if va and ve and va.group(1) != ve.group(1): errs.append('%s: metadata.version khác bản tiếng Việt.' % en)
        ha, he = len(re.findall(r'^## ', rd(shared + d + '/SKILL.md'), re.M)), len(re.findall(r'^## ', rd(en), re.M))
        if ha != he: errs.append('Song ngữ: %s%s/SKILL.md có %d mục "##", bản en có %d.' % (shared, d, ha, he))
    for idxf in ('.agent/SKILL_INDEX.md', 'en/.agent/SKILL_INDEX.md'):
        idx = rd(idxf)
        rows = re.findall(r'^\| ([a-z0-9-]+) \| LOCAL \| SHARED \| (\S+) \|', idx, re.M)
        in_idx = {r[0] for r in rows}
        for d in sk:
            if d not in in_idx: errs.append('%s thiếu skill "%s".' % (idxf, d))
        for name, loc in rows:
            if not os.path.isfile(P(loc)): errs.append('%s: %s trỏ tới file không có (%s).' % (idxf, name, loc))
            if name not in sk: errs.append('%s liệt kê "%s" nhưng không có thư mục skill.' % (idxf, name))
    # cây en/ phủ đủ các file chỉ có nội dung tiếng Việt
    root_lang = [f for f in files if not f.startswith(('en/', 'docs/', 'tools/', 'dist/')) and f.endswith(('.md', '.html', '.csv', '.txt')) and
                 (f in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'PROJECT.md', 'README.md') or f.startswith(('.agent/', 'archive/', 'output/', 'working/', 'references/', 'skills/', 'examples/')))
                 and '/scripts/' not in f and f not in ('.agent/PACKAGE_INFO.json',)]
    root_lang.append('docs/README.md')
    for f in sorted(root_lang):
        if not os.path.isfile(P('en/' + f)): errs.append('Thiếu bản tiếng Anh en/%s.' % f)
    for f in [f for f in files if f.startswith('en/') and f not in OVERLAY_SKIP and not f.startswith('en/docs/en/')]:
        if not os.path.isfile(P(f[3:])): errs.append('%s không có file tiếng Việt tương ứng %s.' % (f, f[3:]))
    for doc in ('README.md', 'en/README.md', 'skills/local/shared/README.md', 'en/skills/local/shared/README.md', 'docs/HUONG_DAN_SKILLS_VI.md', 'docs/en/SKILLS_GUIDE.md'):
        t = rd(doc)
        for d in sk:
            if '`' + d + '`' not in t and '`' + d + '/`' not in t:
                warns.append('%s không nhắc tới skill "%s".' % (doc, d))
    # 4. đường dẫn trong tài liệu
    for f in md:
        if f == 'CHANGELOG.md': continue
        t = strip_fences(rd(f))
        base = os.path.dirname(f)
        anc = base
        while anc and not os.path.isfile(P(anc + '/SKILL.md')): anc = os.path.dirname(anc)
        for tok in set(re.findall(r'`([^`\n]+)`', t)):
            if '/' not in tok or re.search(r'[\[\]<>*{}|\s:~]|\.\.\.|^https?|^python|FILE|\.bak', tok): continue
            if not re.search(r'(\.(md|html|py|json|sha256|txt)|/)$', tok): continue
            cands = [tok, (base + '/' + tok if base else tok)]
            if anc: cands.append(anc + '/' + tok)
            cands += [shared + d + '/' + tok for d in sk]
            if tok in GENERATED or any(os.path.exists(P(c)) for c in cands): continue
            if tok.rstrip('/') in ('dist', 'dist/'): continue
            errs.append('%s: đường dẫn `%s` không tồn tại.' % (f, tok))
    # 5. song ngữ
    for a, b in PAIRS:
        ta, tb = rd(a), rd(b)
        ha = len(re.findall(r'^## ', ta, re.M)); hb = len(re.findall(r'^## ', tb, re.M))
        if ha != hb: errs.append('Song ngữ: %s có %d mục "##", %s có %d.' % (a, ha, b, hb))
        ca, cb = ta.count('```') // 2, tb.count('```') // 2
        if ca != cb: warns.append('Song ngữ: %s có %d khối mã, %s có %d.' % (a, ca, b, cb))
    for f in [f for f in files if f.startswith('skills/local/shared/') and f.endswith('.md') and '/SKILL.md' not in f]:
        e = 'en/' + f
        if os.path.isfile(P(e)):
            ta, tb = rd(f), rd(e)
            if ta.count('```') // 2 != tb.count('```') // 2: warns.append('Song ngữ: %s và %s khác số khối mã.' % (f, e))
    # 6. HTML
    for h in [f for f in files if f.endswith('.html')]:
        t = rd(h)
        if re.search(r'<(script|link|img|iframe)\b[^>]*(src|href)=["\']https?://', t, re.I) or re.search(r'@import|url\(\s*["\']?https?:', t):
            errs.append('%s: có tài nguyên tải từ mạng (phải mở được offline).' % h)
    r = subprocess.run([sys.executable, P('tools/build_guides_html.py'), '--check'], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        errs.append('build_guides_html.py --check: HTML lệch Markdown hoặc lỗi (%s).' % (r.stdout + r.stderr).decode('utf-8', 'replace').strip().splitlines()[-1][:120])
    # 7. Python và dòng kết thúc
    for f in [f for f in files if f.endswith('.py')]:
        try: ast.parse(rd(f))
        except SyntaxError as e: errs.append('%s: lỗi cú pháp Python (%s).' % (f, e))
    crlf = [f for f in files if f.endswith(('.md', '.html', '.py', '.json')) and '\r\n' in rd(f)]
    if crlf: warns.append('Có %d file dùng CRLF (ví dụ %s); nên dùng LF.' % (len(crlf), crlf[0]))
    # 7b. gói lĩnh vực
    if os.path.isdir(P('packs')):
        import pack as packmod
        for n in sorted(os.listdir(P('packs'))):
            if os.path.isdir(P('packs/' + n)):
                for e in packmod.validate_pack(P('packs/' + n), n):
                    errs.append('Gói: ' + e)
    # 8. phát hành
    if release:
        if os.path.exists(P('setup_answers.json')): errs.append('Bản phát hành không được có setup_answers.json.')
        if os.path.exists(P('.agent/PACKAGE_INFO.json')): errs.append('Bản phát hành không được có .agent/PACKAGE_INFO.json.')
        for f, marker in (('PROJECT.md', '[Tên]'), ('en/PROJECT.md', '[Name]'), ('.agent/STATE.md', '[Phase/trạng thái hiện tại]'), ('en/.agent/STATE.md', '[Current phase/status]')):
            if marker not in rd(f): errs.append('%s không còn ở dạng mẫu (thiếu %s).' % (f, marker))
        if not rd('.agent/HANDOFF.md').lstrip().startswith('# HANDOFF\n\nNone') or not rd('en/.agent/HANDOFF.md').lstrip().startswith('# HANDOFF\n\nNone'): errs.append('.agent/HANDOFF.md không ở dạng mẫu "None".')
        for f in files:
            if f.startswith(USER_DIRS) and os.path.basename(f) != 'README.md':
                errs.append('Có file người dùng trong bản phát hành: %s.' % f)
    return errs, warns

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--release', action='store_true')
    ap.add_argument('--write-manifest', action='store_true')
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if a.verify:
        sys.exit(verify())
    if a.write_manifest:
        write_manifest(); return
    errs, warns = check_all(release=a.release)
    for w in warns: print('Cảnh báo: ' + w)
    for e in errs: print('LỖI: ' + e)
    print('\n%s: %d lỗi, %d cảnh báo.' % ('KHÔNG ĐẠT' if errs else 'ĐẠT', len(errs), len(warns)))
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
