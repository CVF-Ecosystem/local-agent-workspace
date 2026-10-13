#!/usr/bin/env python3
"""Kiểm tra package và quản lý MANIFEST.sha256. Chỉ cần Python 3.8+, không dùng mạng.

Dùng (chạy từ thư mục gốc của package/project):
  python tools/check_package.py                  kiểm tra chất lượng package
  python tools/check_package.py --release        thêm kiểm tra "sạch để phát hành" (mẫu chưa điền, không dữ liệu project)
  python tools/check_package.py --write-manifest ghi MANIFEST.sha256 (người bảo trì package dùng)
  python tools/check_package.py --verify         so file của project với MANIFEST.sha256: file nào của package đã bị sửa

Mã thoát: 0 đạt; 1 có lỗi (chế độ kiểm tra) hoặc có file đã đổi/thiếu (--verify); 2 lỗi dùng.
Kiểm tra cũng gồm tương thích Python 3.8 (heuristic, xem check_py38). Cờ ẩn --result-json xuất envelope
có cấu trúc (local-agent-workspace/result-v1); mã trong envelope luôn bằng mã thoát.
"""
import argparse, ast, hashlib, io, json, os, re, subprocess, sys, tokenize
from result_schema import emit, make

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = ('.md', '.html', '.py', '.json', '.txt', '.sha256', '.css', '.js', '')
SKIP_DIRS = {'.git', '__pycache__', 'dist', 'node_modules'}
# Chỉ ở thư mục gốc: nơi quản lý feedback của người duy trì, không đưa vào gói phát hành
ROOT_ONLY_SKIP = {'feedback', '.github', 'roadmap', 'tests', 'release_templates'}
# Dữ liệu vận hành cục bộ (giao dịch, lịch sử thao tác): không vào MANIFEST hay ZIP / local runtime data, never packaged
RUNTIME_DIR = '.agent/runtime'
# File người dùng sửa trong project: không đưa vào MANIFEST
USER_FILES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
              '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md', '.agent/PACKAGE_INFO.json',
              '.agent/MERGE_STATUS.json', 'setup_answers.json'}
USER_DIRS = ('working/', 'output/', 'archive/', 'references/', 'skills/external/', 'skills/inbox/', 'skills/local/project/', 'skills/local/packs/')
OVERLAY_SKIP = {'en/PROJECT_INSTRUCTIONS_SNIPPET.md'}
PAIRS = [('AGENTS.md', 'en/AGENTS.md'), ('PROJECT.md', 'en/PROJECT.md'),
         ('docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md', 'docs/en/NEW_PROJECT_GUIDE.md'),
         ('docs/HUONG_DAN_SU_DUNG_VI.md', 'docs/en/DAILY_USE_GUIDE.md'),
         ('docs/HUONG_DAN_SKILLS_VI.md', 'docs/en/SKILLS_GUIDE.md'),
         ('docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md', 'docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md'),
         ('docs/NGUON_THAM_KHAO_VI.md', 'docs/en/SOURCES_AND_REFERENCES.md')]
GENERATED = {'.agent/PACKAGE_INFO.json', '.agent/MERGE_STATUS.json', 'MANIFEST.sha256'}
# Mỗi file trong en/ (trừ OVERLAY_SKIP) thay cho file cùng đường dẫn không có tiền tố en/

def P(rel): return os.path.join(ROOT, *rel.split('/'))
def rd(rel): return io.open(P(rel), encoding='utf-8', newline='').read()

def all_files():
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not (d == ROOT and x in ROOT_ONLY_SKIP)
                         and os.path.relpath(os.path.join(d, x), ROOT).replace(os.sep, '/') != RUNTIME_DIR)
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
    return len(lines)

def read_manifest():
    if not os.path.isfile(P('MANIFEST.sha256')):
        return None
    m = {}
    for l in rd('MANIFEST.sha256').splitlines():
        if l.strip():
            h, p = l.split('  ', 1)
            m[p] = h
    return m

def verify(findings=None):
    """Trả về mã thoát; findings (nếu có) nhận mỗi file đã sửa/thiếu dưới dạng finding lỗi."""
    findings = [] if findings is None else findings
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
    for x in changed: print('  ĐÃ SỬA : ' + x); findings.append({'severity': 'error', 'message': 'Đã sửa so với MANIFEST: ' + x})
    for x in missing: print('  THIẾU  : ' + x); findings.append({'severity': 'error', 'message': 'Thiếu so với MANIFEST: ' + x})
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

# ---------------------------------------------------------------- Python 3.8 (heuristic)
# Đây là kiểm tra GẦN ĐÚNG, không thay thế việc chạy trên Python 3.8 thật (CI làm việc đó).
# ast.parse(feature_version=(3, 8)) bắt cú pháp mới như `match`; các regex dưới đây chạy trên mã đã bỏ
# chuỗi và chú thích để bắt API và kiểu chú thích 3.9+. Có thể báo nhầm (ví dụ `: list[` không phải chú thích)
# hoặc bỏ sót (ví dụ toán tử `dict | dict`). Sửa cảnh báo bằng cách viết lại theo API 3.8.
PY38_DENY = [
    (r'\.removeprefix\s*\(', 'str.removeprefix() cần Python 3.9+'),
    (r'\.removesuffix\s*\(', 'str.removesuffix() cần Python 3.9+'),
    (r'\bfunctools\.cache\b', 'functools.cache cần Python 3.9+; dùng functools.lru_cache(maxsize=None)'),
    (r'\bfrom\s+functools\s+import\b.*\bcache\b', 'functools.cache cần Python 3.9+'),
    (r'^\s*@\s*cache\b', '@cache cần Python 3.9+; dùng @lru_cache(maxsize=None)'),
    (r'^\s*(?:import|from)\s+zoneinfo\b', 'zoneinfo cần Python 3.9+'),
    (r'\bmath\.lcm\s*\(', 'math.lcm() cần Python 3.9+'),
    (r'\bast\.unparse\s*\(', 'ast.unparse() cần Python 3.9+'),
    (r'\basyncio\.to_thread\s*\(', 'asyncio.to_thread() cần Python 3.9+'),
    (r'\.(?:is_relative_to|with_stem)\s*\(', 'Path.is_relative_to/with_stem cần Python 3.9+'),
    (r'\.bit_count\s*\(', 'int.bit_count() cần Python 3.10+'),
    (r'\bzip\s*\(.*\bstrict\s*=', 'zip(strict=...) cần Python 3.10+'),
    (r'^\s*with\s*\(\s*$', 'with (...) nhiều mục cần Python 3.9+; hãy tách thành with lồng nhau'),
    (r'^\s*with\s*\(.*\bas\s+\w.*,', 'with (...) nhiều mục cần Python 3.9+; hãy tách thành with lồng nhau'),
    (r'[\w\]]\s*\|\s*None\b', 'chú thích X | None cần Python 3.10+; dùng Optional[X]'),
    (r'(?:->|:)\s*(?:list|dict|tuple|set|frozenset|type)\s*\[', 'chú thích list[...]/dict[...] lúc chạy cần Python 3.9+; dùng typing.List/Dict'),
]

def _code_only(src):
    """Các dòng của src với chuỗi và chú thích thay bằng khoảng trắng (giữ nguyên số dòng và cột)."""
    lines = src.split('\n')
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type not in (tokenize.STRING, tokenize.COMMENT):
                continue
            (r1, c1), (r2, c2) = tok.start, tok.end
            for r in range(r1, r2 + 1):
                line = lines[r - 1]
                a = c1 if r == r1 else 0
                b = c2 if r == r2 else len(line)
                lines[r - 1] = line[:a] + ' ' * (b - a) + line[b:]
    except (tokenize.TokenError, SyntaxError):
        pass  # file lỗi cú pháp đã được check_all báo
    return lines

def py38_problems(src, name='<src>'):
    """Heuristic: [(dòng, mô tả)] các điểm có thể không chạy trên Python 3.8. Xem ghi chú trên PY38_DENY.
    Luôn phân tích với feature_version=(3, 8), nên kết quả giống nhau trên mọi phiên bản Python đang chạy
    (trên Python 3.8 thật, `match` là lỗi cú pháp thường và vẫn được báo)."""
    out = []
    code = _code_only(src)
    try:
        ast.parse(src, filename=name, feature_version=(3, 8))
    except SyntaxError as e:
        ln = e.lineno or 0
        if 'Pattern matching' in str(e.msg):  # CPython báo ở cuối khối match: lấy dòng `match` đầu tiên
            ln = next((i for i, l in enumerate(code, 1) if re.match(r'\s*match\s+[^=\n]+:\s*$', l)), ln)
        out.append((ln, 'không phân tích được bằng cú pháp Python 3.8 (%s)' % e.msg))
    for i, line in enumerate(code, 1):
        for pat, msg in PY38_DENY:
            if re.search(pat, line):
                out.append((i, msg))
    return out

def check_py38():
    """Heuristic cho mọi file .py của package: báo lỗi kèm đường dẫn file và số dòng (xem py38_problems)."""
    errs = []
    for f in all_files():
        if f.endswith('.py'):
            for ln, msg in py38_problems(rd(f), f):
                errs.append('%s:%d: không tương thích Python 3.8 — %s.' % (f, ln, msg))
    return errs

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
                 and '/scripts/' not in f and f not in ('.agent/PACKAGE_INFO.json',)
                 and not (f.startswith(('archive/', 'output/', 'working/')) and f.count('/') > 1)  # nội dung của người dùng, chỉ README cần bản en/
                 and not f.startswith(('skills/local/project/', 'skills/local/packs/', 'skills/external/', 'skills/inbox/'))]  # skill của project/pack do người dùng quản lý, không bắt buộc bản en/
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
    # mẫu issue GitHub (kho nguồn, không vào gói) phải cùng nội dung phiếu phản hồi
    tpl = '.github/ISSUE_TEMPLATE/phan-hoi.md'
    if os.path.isfile(P(tpl)) and os.path.isfile(P('docs/FEEDBACK_FORM_VI_EN.md')):
        tb = rd(tpl).replace('\r\n', '\n').split('\n## 1.', 1)[-1]
        fb = rd('docs/FEEDBACK_FORM_VI_EN.md').replace('\r\n', '\n').split('\n## 1.', 1)[-1]
        if tb.strip() != fb.strip():
            warns.append('%s khác nội dung từ mục 1 của docs/FEEDBACK_FORM_VI_EN.md; hãy đồng bộ.' % tpl)
    # 5. song ngữ
    for a, b in PAIRS:
        if a in USER_FILES and not release:  # file người dùng điền/mở rộng trong project: không bắt buộc khớp bản en
            continue
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
        prefix = 'release_templates/' if os.path.isdir(P('release_templates')) else ''
        templates = ((prefix + 'PROJECT.md', '[Tên]'),
                     (prefix + 'en/PROJECT.md', '[Name]'),
                     (prefix + '.agent/STATE.md', '[Phase/trạng thái hiện tại]'),
                     (prefix + 'en/.agent/STATE.md', '[Current phase/status]'))
        for f, marker in templates:
            if not os.path.isfile(P(f)) or marker not in rd(f):
                errs.append('%s thiếu hoặc không còn ở dạng mẫu (cần %s).' % (f, marker))
        handoffs = (prefix + '.agent/HANDOFF.md', prefix + 'en/.agent/HANDOFF.md')
        if any(not os.path.isfile(P(f)) or not rd(f).lstrip().startswith('# HANDOFF\n\nNone') for f in handoffs):
            errs.append('Mẫu HANDOFF phát hành thiếu hoặc không ở dạng "None".')
        for f in files:
            if f.startswith(USER_DIRS) and os.path.basename(f) != 'README.md':
                errs.append('Có file người dùng trong bản phát hành: %s.' % f)
    return errs, warns

def run_checks(release=False):
    """Mọi kiểm tra của chế độ kiểm tra: check_all (gồm HTML/Markdown) cộng tương thích Python 3.8."""
    errs, warns = check_all(release=release)
    return errs + check_py38(), warns

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--release', action='store_true')
    ap.add_argument('--write-manifest', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if a.verify:
        findings = []
        code = verify(findings)
        if a.result_json:
            msg = {0: 'Khớp MANIFEST', 1: 'Có file đã sửa hoặc thiếu so với MANIFEST', 2: 'Không có MANIFEST.sha256'}.get(code, 'Lỗi')
            emit(make({0: 'success', 1: 'issues'}.get(code, 'error'), code=code, message=msg, changes=False, findings=findings))
        sys.exit(code)
    if a.write_manifest:
        count = write_manifest()
        if a.result_json:
            emit(make('success', code=0, message='Đã ghi MANIFEST.sha256', changes=True,
                      files=[{'path': 'MANIFEST.sha256', 'action': 'written'}], file_count=count))
        return
    errs, warns = run_checks(release=a.release)
    for w in warns: print('Cảnh báo: ' + w)
    for e in errs: print('LỖI: ' + e)
    print('\n%s: %d lỗi, %d cảnh báo.' % ('KHÔNG ĐẠT' if errs else 'ĐẠT', len(errs), len(warns)))
    if a.result_json:
        findings = [{'severity': 'error', 'message': e} for e in errs]
        findings += [{'severity': 'warning', 'message': w} for w in warns]
        emit(make('issues' if errs else 'success', code=1 if errs else 0,
                  message=('Package chưa đạt kiểm tra (%d lỗi)' % len(errs)) if errs else 'Package đạt kiểm tra',
                  changes=False, findings=findings))
    sys.exit(1 if errs else 0)

if __name__ == '__main__':
    main()
