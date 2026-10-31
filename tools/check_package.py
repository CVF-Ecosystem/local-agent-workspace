#!/usr/bin/env python3
"""Kiểm tra package và quản lý MANIFEST.sha256. Chỉ cần Python 3.8+, không dùng mạng.

Dùng (chạy từ thư mục gốc của package/project):
  python tools/check_package.py                  kiểm tra chất lượng package
  python tools/check_package.py --release        thêm kiểm tra "sạch để phát hành" (mẫu chưa điền, không dữ liệu project)
  python tools/check_package.py --write-manifest ghi MANIFEST.sha256 (người bảo trì package dùng)
  python tools/check_package.py --verify         so file của project với MANIFEST.sha256: file nào của package đã bị sửa
  python tools/check_package.py --check-eol FILE...  chỉ kho nguồn có Git: kiểm EOL các file vừa sửa, không tự đổi bytes

Mã thoát: 0 đạt; 1 có lỗi (chế độ kiểm tra) hoặc có file đã đổi/thiếu (--verify); 2 lỗi dùng.
Kiểm tra cũng gồm tương thích Python 3.8 (heuristic, xem check_py38). Cờ ẩn --result-json xuất envelope
có cấu trúc (local-agent-workspace/result-v1); mã trong envelope luôn bằng mã thoát.
"""
import argparse, ast, hashlib, io, json, ntpath, os, re, subprocess, sys, tokenize
from result_schema import emit, make

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = ('.md', '.html', '.py', '.json', '.txt', '.sha256', '.css', '.js', '')
SKIP_DIRS = {'.git', '__pycache__', '.pytest_cache', 'dist', 'node_modules'}
# Chỉ ở thư mục gốc: nơi quản lý feedback của người duy trì, không đưa vào gói phát hành
ROOT_ONLY_SKIP = {'feedback', '.github', 'roadmap', 'tests', 'release_templates'}
# Native của host trong project (A-10: .claude/agents/...) là trạng thái riêng của project/người dùng: không vào MANIFEST, ZIP hay project mới tạo từ bản này.
# Chỉ ở thư mục gốc; adopt/upgrade không đọc, không xóa, không ghi nó vì chỉ ghi file trong selection. / Host-native state of a project: never packaged or copied.
NATIVE_DIR = '.claude'
ROOT_ONLY_SKIP = ROOT_ONLY_SKIP | {NATIVE_DIR}
# Dữ liệu vận hành cục bộ (giao dịch, lịch sử thao tác): không vào MANIFEST hay ZIP / local runtime data, never packaged
RUNTIME_DIR = '.agent/runtime'
# File người dùng sửa trong project: không đưa vào MANIFEST
PROFILE_REL = '.agent/EXECUTION_PROFILE.json'  # cùng hằng với tools/execution_profile.py (có test); import lười để --verify chạy độc lập / same constant, lazy import
INTAKE_CONFIG_REL = '.agent/SOURCE_INTAKE.json'  # private choices, never a starter template
USER_FILES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
              '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md', '.agent/PACKAGE_INFO.json',
              '.agent/MERGE_STATUS.json', 'setup_answers.json', PROFILE_REL, INTAKE_CONFIG_REL}
# Profile hiệu lực của project (lựa chọn + quyền): của người dùng, KHÔNG vào MANIFEST; bản giao luôn là mẫu sạch / the live profile is user-owned,
# never in a MANIFEST; what ships is always the clean template. Schema và helper là của package, vào MANIFEST như file thường.
PROFILE_TEMPLATE = 'release_templates/' + PROFILE_REL  # bản sao kiểm được của mẫu sạch trong kho nguồn / checked mirror of the clean profile
USER_DIRS = ('working/', 'output/', 'archive/', 'references/', 'assets/', 'skills/external/', 'skills/inbox/', 'skills/local/project/', 'skills/local/packs/')
# Exact factory paths; project basenames, mirrors and old manifests confer no ownership.
SCAFFOLD_READMES = frozenset((
    'archive/README.md', 'assets/README.md', 'assets/fonts/README.md',
    'output/README.md', 'references/README.md', 'references/legal/README.md',
    'references/policies/README.md', 'references/source-documents/README.md',
    'references/templates/README.md', 'skills/external/README.md',
    'skills/inbox/README.md', 'skills/local/packs/README.md',
    'skills/local/project/README.md', 'working/README.md',
))
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


LOGO_EXT = ('.png', '.svg', '.jpg', '.jpeg', '.webp')
FONT_EXT = ('.ttf', '.otf', '.woff', '.woff2')


def branding_config(base=None):
    """(title, subtitle, đường dẫn logo hoặc None) từ assets/ / from assets/."""
    adir = os.path.join(base or ROOT, 'assets')
    cfg = {}
    try:
        with io.open(os.path.join(adir, 'branding.json'), encoding='utf-8') as f:
            raw = json.load(f)
        cfg = raw if isinstance(raw, dict) else {}
    except (OSError, ValueError):
        pass
    logo = cfg.get('logo')
    path = os.path.join(adir, logo) if isinstance(logo, str) and logo == os.path.basename(logo) else None
    if not path or not os.path.isfile(path):
        path = next((os.path.join(adir, 'logo' + e) for e in LOGO_EXT if os.path.isfile(os.path.join(adir, 'logo' + e))), None)
    title, sub = cfg.get('title'), cfg.get('subtitle')
    return (title if isinstance(title, str) else ''), (sub if isinstance(sub, str) else ''), path


def branding_js(base=None):
    """Nội dung assets/branding.js cho các trang hướng dẫn mở từ file; None khi không có nhận diện.
    Content of assets/branding.js for guide pages opened from disk; None without branding."""
    title, sub, logo = branding_config(base)
    if not (title or sub or logo):
        return None
    return 'window.WORKSPACE_BRANDING = %s;\n' % json.dumps(
        {'title': title, 'subtitle': sub, 'logo': ('assets/' + os.path.basename(logo)) if logo else ''}, ensure_ascii=False, indent=2)


def branding_files(base=None):
    """File nhận diện của đơn vị trong assets/: branding.json, branding.js, logo (logo.* hoặc tên ghi trong branding.json)
    và font trong assets/fonts/. Thuộc người dùng (không vào MANIFEST, nâng cấp không ghi đè) nhưng được phép đi theo
    bộ mẫu: vào ZIP phát hành, sang dự án mới. / Organization branding in assets/: user-owned, yet carried by the template."""
    base = base or ROOT
    adir = os.path.join(base, 'assets')
    if not os.path.isdir(adir):
        return []
    named = set()
    try:
        with io.open(os.path.join(adir, 'branding.json'), encoding='utf-8') as f:
            logo = json.load(f).get('logo')
        if isinstance(logo, str) and logo == os.path.basename(logo) and logo.lower().endswith(LOGO_EXT):
            named.add(logo)
    except (OSError, ValueError, AttributeError):
        pass
    out = []
    for n in sorted(os.listdir(adir)):
        if os.path.isfile(os.path.join(adir, n)) and (n in ('branding.json', 'branding.js') or n in named
                                                      or (n.lower().startswith('logo.') and n.lower().endswith(LOGO_EXT))):
            out.append('assets/' + n)
    fdir = os.path.join(adir, 'fonts')
    if os.path.isdir(fdir):
        out += ['assets/fonts/' + n for n in sorted(os.listdir(fdir))
                if os.path.isfile(os.path.join(fdir, n)) and n.lower().endswith(FONT_EXT)]
    return out
def rd(rel):
    with io.open(P(rel), encoding='utf-8', newline='') as f:
        return f.read()

def private_file(name):
    """Tên file tài khoản/khóa thật không được giao. Mẫu kết thúc .example.json hoặc .example vẫn được giữ.
    Real credentials/key filenames are never shipped; public example templates remain eligible."""
    n = name.lower()
    if n.endswith(('.example.json', '.example')):
        return False
    return ('credentials' in n and n.endswith('.json')) or n == '.env' or n.startswith('.env.') or n.endswith(('.pem', '.key'))


def _walk(base, skip_private=True):
    base = os.fspath(base)
    out = []
    for d, dirs, files in os.walk(base):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not (d == base and x in ROOT_ONLY_SKIP)
                         and os.path.relpath(os.path.join(d, x), base).replace(os.sep, '/') != RUNTIME_DIR)
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(d, f), base).replace(os.sep, '/')
            if f.endswith(('.pyc', '.bak')) or '.bak-' in f or f == '.git':  # '.git' là file khi dùng git worktree / a file in a git worktree
                continue
            if skip_private and private_file(f):
                continue
            out.append(rel)
    return out


def all_files():
    return _walk(ROOT)


def private_files(base=None):
    """Các file riêng trong cây được duyệt, bỏ qua runtime/native như selection chung.
    Private files from the shared traversal, with the same runtime/native exclusions."""
    return [r for r in _walk(base or ROOT, skip_private=False) if private_file(r.rsplit('/', 1)[-1])]

_SCAFFOLD = {}

def package_readme(rel):
    """README.md trong thư mục người dùng có phải của package không: dựa vào đường dẫn thực, không chỉ tên file.
    Chỉ các đường dẫn factory tường minh, kể cả mirror en/, là khung của package.
    README do người dùng tự tạo trong thư mục riêng (vd. references/khach-hang-a/README.md) thuộc project.
    Only explicit factory paths are scaffold. A project README cannot become
    package content through its name, an English mirror or an old MANIFEST."""
    return (rel[3:] if rel.startswith('en/') else rel) in SCAFFOLD_READMES


def in_user_dir(rel):
    """Project data directories and their English overlay counterparts."""
    return (rel[3:] if rel.startswith('en/') else rel).startswith(USER_DIRS)

def intake_config(rel):
    """Only the private config and its English mirror, including Windows path aliases. No file access."""
    path = ntpath.normpath(rel).replace('\\', '/').casefold()
    return path in (INTAKE_CONFIG_REL.casefold(), ('en/' + INTAKE_CONFIG_REL).casefold())


def user_owned(rel):
    """File do người dùng/project sở hữu (không phải của package): không áp quy tắc phát hành như số phiên bản,
    bản tiếng Anh hay đường dẫn trong tài liệu. Cùng một quy tắc với in_manifest.
    User/project-owned file (not the package's): release rules such as version strings, the English mirror and doc paths
    do not apply. Same ownership rule as in_manifest."""
    if intake_config(rel) or rel in USER_FILES:
        return True
    return in_user_dir(rel) and not package_readme(rel)

def in_manifest(rel):
    if intake_config(rel) or rel in GENERATED or rel == PROFILE_REL:
        return False
    if in_user_dir(rel):
        return package_readme(rel)
    return True

def _ep():
    """Module profile, nạp khi cần (bytes sạch, kiểm schema). / The profile module, loaded when needed."""
    import execution_profile
    return execution_profile


def sha(rel):
    with open(P(rel), 'rb') as f:
        data = f.read()
    if os.path.splitext(rel)[1] in TEXT_EXT:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()

def sha_bytes(rel, data):
    """Cùng quy tắc với sha() nhưng trên bytes đã có (bytes sau projection). / Same rule as sha(), on bytes already in hand."""
    if os.path.splitext(rel)[1] in TEXT_EXT:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()

# ---------------------------------------------------------------- projection giao đi (I3) / delivery projection
# MỘT owner chung cho "file nào được giao" và "giao bytes nào" của build_release, new_project, adopt_project và MANIFEST của bản giao.
# Không phải registry: chỉ là danh sách tường minh và vài phép thay tham chiếu hữu hạn. Kho nguồn giữ nguyên v1/v2/fixtures/evidence.
# ONE owner for "which files ship" and "which bytes ship" for build, new, adopt and the shipped MANIFEST. Not a registry: an explicit list
# and a few finite reference replacements. The source tree keeps v1/v2, fixtures and evidence untouched.
CVF_DIR = '.cvf'
CVF_MACHINE = ('.cvf/contracts/v3/control.schema.json', '.cvf/rules/v3/ROUTING_POLICY.json', '.cvf/checks/control_check_v3.py',
               '.cvf/checks/v3/__init__.py', '.cvf/checks/v3/canon.py', '.cvf/checks/v3/loader.py', '.cvf/checks/v3/refs.py',
               '.cvf/checks/v3/binding.py', '.cvf/checks/v3/routing.py', '.cvf/checks/v3/observer.py', '.cvf/checks/v3/workflow.py')
CVF_READABLE = ('.cvf/README.md', '.cvf/contracts/v3/CONTROL_CONTRACT.md', '.cvf/rules/v3/CONTROL_RULES.md')
CVF_CLOSURE = tuple(sorted(CVF_MACHINE + CVF_READABLE))
CVF_OVERLAY = {'.cvf/README.md': 'release_templates/.cvf/README.md'}  # README của kho nguồn là của người bảo trì / the source README is the maintainers'
# Owner và phụ thuộc mà machine closure cần cùng bytes (đã pin trong policy hoặc nạp bởi owner) / owners and dependencies the machine closure needs
CVF_DEPENDENCIES = ('tools/publish_new.py', 'tools/context_update.py', 'tools/transaction.py', 'tools/result_schema.py', 'tools/current_draft.py')
# Entrypoint đã pin bằng hash bytes trong policy v3: ZIP giữ nguyên từng byte (không đổi CRLF thành LF) / pinned by raw bytes: shipped byte for byte
BYTE_EXACT = ('tools/publish_new.py', 'tools/context_update.py')
TEMPLATE_OVERLAYS = {  # kho nguồn: thay file người bảo trì bằng mẫu sạch / source repo: clean templates for maintainer files
    'PROJECT.md': 'release_templates/PROJECT.md',
    '.agent/STATE.md': 'release_templates/.agent/STATE.md',
    '.agent/HANDOFF.md': 'release_templates/.agent/HANDOFF.md',
    '.agent/INDEX.md': 'release_templates/.agent/INDEX.md',
    '.agent/SKILL_INDEX.md': 'release_templates/.agent/SKILL_INDEX.md',
    '.agent/PENDING_LESSONS.md': 'release_templates/.agent/PENDING_LESSONS.md',
    'en/PROJECT.md': 'release_templates/en/PROJECT.md',
    'en/.agent/STATE.md': 'release_templates/en/.agent/STATE.md',
    'en/.agent/HANDOFF.md': 'release_templates/en/.agent/HANDOFF.md',
    'en/.agent/INDEX.md': 'release_templates/en/.agent/INDEX.md',
    'en/.agent/SKILL_INDEX.md': 'release_templates/en/.agent/SKILL_INDEX.md',
    'en/.agent/PENDING_LESSONS.md': 'release_templates/en/.agent/PENDING_LESSONS.md',
}
_P_RULES, _P_POLICY, _P_CONTRACTS = '`.cvf/rules/CONTROL_RULES.md`', '`.cvf/rules/ROUTING_POLICY.json`', '`.cvf/contracts/`'
_V_RULES, _V_POLICY, _V_CONTRACTS = '`.cvf/rules/v3/CONTROL_RULES.md`', '`.cvf/rules/v3/ROUTING_POLICY.json`', '`.cvf/contracts/v3/`'
# (cũ, mới, số lần xuất hiện đúng): lệch số lần là bất thường ⇒ từ chối trước khi ghi. / (old, new, exact count): any other count is refused.
REF_REPLACEMENTS = {
    'AGENTS.md': ((_P_RULES, _V_RULES, 1), (_P_POLICY, _V_POLICY, 1), (_P_CONTRACTS, _V_CONTRACTS, 1)),
    'en/AGENTS.md': ((_P_RULES, _V_RULES, 1), (_P_POLICY, _V_POLICY, 1), (_P_CONTRACTS, _V_CONTRACTS, 1)),
    'roles/README.md': ((_P_RULES, _V_RULES, 2), (_P_POLICY, _V_POLICY, 1), (_P_CONTRACTS, _V_CONTRACTS, 1)),
    'roles/scout/agent.md': ((_P_RULES, _V_RULES, 1),),
    'roles/worker/agent.md': ((_P_RULES, _V_RULES, 1),),
    'roles/reviewer/agent.md': ((_P_RULES, _V_RULES, 1),),
}
_NO_DELIVERY = {'.agent/PACKAGE_INFO.json', '.agent/MERGE_STATUS.json', 'setup_answers.json', 'MANIFEST.sha256'}
_NO_DELIVERY.add(INTAKE_CONFIG_REL)
_NO_DELIVERY |= {'en/' + r for r in _NO_DELIVERY} | {'en/' + PROFILE_REL}


def _check_user_file_mapping():
    classified = {r for r in TEMPLATE_OVERLAYS if not r.startswith('en/')} | _NO_DELIVERY | {PROFILE_REL}
    missing = USER_FILES - classified
    if missing:
        raise ProjectionError('UNCLASSIFIED_USER_FILES', ', '.join(sorted(missing)))


class ProjectionError(Exception):
    """Projection hoặc nguồn giao bất thường: từ chối trước khi ghi bất cứ thứ gì. / abnormal projection or source: refused before any write."""

    def __init__(self, code, detail=''):
        Exception.__init__(self, ('%s: %s' % (code, detail)) if detail else code)
        self.code = code
        self.detail = detail


def _walk_key(rel):
    """Thứ tự duyệt của all_files(): file của một thư mục trước thư mục con, mỗi nhóm theo tên. / os.walk order used by all_files()."""
    parts = rel.split('/')
    return tuple((0 if i == len(parts) - 1 else 1, part) for i, part in enumerate(parts))


def source_state():
    """'initialized' | 'maintainer' (kho nguồn có mẫu sạch) | 'clean' (bộ mẫu chưa khởi tạo) | 'unknown'. Từ bằng chứng trong file.
    From file evidence: an initialized project is never a package source."""
    if os.path.exists(P('.agent/PACKAGE_INFO.json')):
        return 'initialized'
    if os.path.lexists(P('release_templates')):
        return 'maintainer' if os.path.isdir(P('release_templates')) and all(os.path.isfile(P(s)) for s in TEMPLATE_OVERLAYS.values()) else 'unknown'
    m = read_manifest() or {}
    if os.path.isfile(P('PROJECT.md')) and (m.get('PROJECT.md') == sha('PROJECT.md') or m.get('en/PROJECT.md') == sha('PROJECT.md')):
        return 'clean'
    return 'unknown'


def _is_link(path):
    if os.path.islink(path):
        return True
    try:
        return bool(getattr(os.lstat(path), 'st_file_attributes', 0) & 0x400)  # Windows reparse point (junction)
    except OSError:
        return False


def cvf_inventory(base):
    """('ABSENT'|'NOT_DIR'|'DIR', {rel}) của `.cvf` dưới base, đọc cấu trúc thật (kể cả thư mục link), bỏ __pycache__/.pyc.
    Real structure of `.cvf` under base; links count as files outside the closure."""
    top = os.path.join(base, CVF_DIR)
    if not os.path.lexists(top):
        return 'ABSENT', set()
    if _is_link(top) or not os.path.isdir(top):
        return 'NOT_DIR', set()
    found = set()
    for d, dirs, files in os.walk(top, followlinks=False):
        keep = []
        for x in sorted(dirs):
            full = os.path.join(d, x)
            if x == '__pycache__':
                continue
            if _is_link(full):
                found.add(os.path.relpath(full, base).replace(os.sep, '/') + '@link')
            else:
                keep.append(x)
        dirs[:] = keep
        for f in files:
            if f.endswith('.pyc'):
                continue
            full = os.path.join(d, f)
            found.add(os.path.relpath(full, base).replace(os.sep, '/') + ('@link' if _is_link(full) else ''))
    return 'DIR', found


def project_refs(rel, data):
    """Bytes của rel sau phép thay tham chiếu hữu hạn. Idempotent (đã thay thì giữ nguyên); số lần xuất hiện bất thường, EOL lẫn hoặc
    không phải UTF-8 ⇒ ProjectionError. Giữ EOL gốc. / Finite reference replacement: idempotent, and any odd count is refused."""
    rules = REF_REPLACEMENTS.get(rel)
    if not rules:
        return data
    crlf = b'\r\n' in data
    if crlf and re.search(rb'(?<!\r)\n', data):
        raise ProjectionError('MIXED_LINE_ENDINGS', rel)
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        raise ProjectionError('NOT_UTF8', rel)
    if crlf:
        text = text.replace('\r\n', '\n')
    for old, new, count in rules:
        n_old, n_new = text.count(old), text.count(new)
        if n_old == count and n_new == 0:
            text = text.replace(old, new)
        elif not (n_old == 0 and n_new == count):
            raise ProjectionError('REFERENCE_ANOMALY', '%s: %s đang %d (cũ) / %d (mới), cần đúng %d' % (rel, old, n_old, n_new, count))
    return (text.replace('\n', '\r\n') if crlf else text).encode('utf-8')


def delivery_selection(branding=True):
    """Danh sách file giao đi (đường dẫn tương đối, thứ tự duyệt thư mục), KHÔNG gồm MANIFEST.sha256. Dùng chung cho build/new/adopt.
    Mọi `.cvf/` của kho nguồn bị thay bằng đúng closure v3 tường minh. / The shipped file list; `.cvf/` is replaced by the explicit v3 closure."""
    _check_user_file_mapping()
    brand = set(branding_files()) if branding else set()
    rels = {f for f in all_files() if not intake_config(f) and f not in _NO_DELIVERY and not f.startswith(CVF_DIR + '/')
            and (in_manifest(f) or f in USER_FILES or f in brand)}
    rels.update(CVF_CLOSURE)
    if source_state() == 'maintainer':
        rels.update(TEMPLATE_OVERLAYS)
    rels.add(PROFILE_REL)  # luôn giao mẫu sạch, kể cả khi nguồn không có file profile / always the clean profile, even if the source has none
    if branding and branding_js() is not None:
        rels.add('assets/branding.js')  # dựng lại từ branding.json để trang hướng dẫn đúng ngay / rebuilt from branding.json
    return sorted(rels, key=_walk_key)


def delivery_bytes(rel):
    """Bytes sẽ giao của rel: mẫu sạch (kho nguồn), overlay `.cvf/README.md`, phép thay tham chiếu; còn lại là bytes gốc."""
    _check_user_file_mapping()
    if intake_config(rel) or rel in _NO_DELIVERY:
        raise ProjectionError('EXCLUDED_FILE', rel)
    if rel == 'assets/branding.js':
        js = branding_js()
        if js is not None:
            return js.encode('utf-8')
    if rel == PROFILE_REL:
        return _ep().clean_profile_bytes()  # không bao giờ mang profile sống (lựa chọn, grant) của nguồn / never a live profile of the source
    src = None
    state = source_state()
    if state not in ('maintainer', 'clean'):
        raise ProjectionError('SOURCE_STATE_INVALID', state)
    if state == 'maintainer':
        src = TEMPLATE_OVERLAYS.get(rel) or CVF_OVERLAY.get(rel)
    path = P(src or rel)
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except OSError as e:
        raise ProjectionError('SOURCE_FILE_MISSING', '%s (%s)' % (src or rel, e.__class__.__name__))
    return project_refs(rel, data)


def delivery_manifest(rels, branding=True):
    """MANIFEST.sha256 của bản giao, tính trên bytes THỰC giao (không chép MANIFEST kho nguồn đã cũ).
    Bộ mẫu sạch đã có MANIFEST nhất quán thì giữ nguyên MANIFEST đó (để biết file nào người dùng đã sửa trong bộ mẫu).
    The shipped MANIFEST is computed from the bytes that ship; a clean template keeps its own consistent MANIFEST."""
    wanted = [r for r in rels if in_manifest(r)]
    if source_state() == 'clean':
        m = read_manifest()
        if m is None or set(m) != set(wanted):
            raise ProjectionError('MANIFEST_SET_MISMATCH', 'MANIFEST của bộ mẫu không khớp tập file giao')
        return rd('MANIFEST.sha256').encode('utf-8')
    lines = ['%s  %s' % (sha_bytes(r, delivery_bytes(r)), r) for r in sorted(wanted, key=_walk_key)]
    return ('\n'.join(lines) + '\n').encode('utf-8')


def _cvf_token_problems(rels, read):
    """Tham chiếu `.cvf/...` trong văn bản giao đi phải trỏ vào file/thư mục thực sự giao; gốc `rules|contracts|checks` trần không rõ phiên bản.
    `.cvf/...` references in shipped text must resolve to what ships; the bare version-less roots are ambiguous."""
    files, out = set(rels), []
    for rel in rels:
        if os.path.splitext(rel)[1] not in ('.md', '.html', '.json', '.txt'):
            continue
        try:
            text = read(rel).decode('utf-8')
        except (UnicodeDecodeError, ProjectionError):
            continue
        seen = set()
        for m in re.finditer(r'(?<![\w.])\.cvf(?:/[A-Za-z0-9_.*-]+)*/?', text):
            tok = m.group(0).rstrip('/.')
            if tok in seen or '*' in tok or tok == CVF_DIR:
                continue
            seen.add(tok)
            if tok in ('.cvf/contracts', '.cvf/rules', '.cvf/checks'):
                out.append('%s: tham chiếu `%s` không nói rõ phiên bản (cần v3).' % (rel, tok))
            elif tok not in files and not any(f.startswith(tok + '/') for f in files):
                out.append('%s: tham chiếu `%s` không có trong bản giao.' % (rel, tok))
    return out


def profile_template_problems(base=None):
    """Mẫu profile sạch của kho nguồn phải tồn tại và đúng bằng mặc định của helper (so sánh sau khi chuẩn hóa CRLF). / The source's clean profile mirror."""
    base = base or ROOT
    try:
        with open(os.path.join(base, *PROFILE_TEMPLATE.split('/')), 'rb') as f:
            data = f.read()
    except OSError:
        return ['Thiếu mẫu profile sạch %s.' % PROFILE_TEMPLATE]
    if data.replace(b'\r\n', b'\n') != _ep().clean_profile_bytes():
        return ['%s không phải profile sạch (owner PROFILE, không lựa chọn, không grant).' % PROFILE_TEMPLATE]
    return []


def delivery_problems(branding=True):
    """Lỗi của chính projection/nguồn giao (rỗng = giao được). Chỉ đọc. Nguồn phải là kho nguồn có mẫu sạch hoặc bộ mẫu chưa khởi tạo.
    Problems with the projection or the source itself ([] = deliverable). Read only."""
    state = source_state()
    if state not in ('maintainer', 'clean'):
        return ['Nguồn giao không phải kho nguồn có mẫu sạch hay bộ mẫu chưa khởi tạo nhất quán (trạng thái: %s); không xuất như package.' % state]
    errs = []
    for rel in CVF_CLOSURE:
        src = CVF_OVERLAY.get(rel) if state == 'maintainer' else None
        if not os.path.isfile(P(src or rel)):
            errs.append('Thiếu file của closure .cvf v3: %s.' % (src or rel))
    if state == 'maintainer':
        errs += profile_template_problems()
    kind, found = cvf_inventory(ROOT)
    if state == 'clean' and (kind != 'DIR' or found != set(CVF_CLOSURE)):
        errs.append('.cvf của bộ mẫu không đúng closure v3: thừa %s, thiếu %s.' % (
            sorted(found - set(CVF_CLOSURE))[:5], sorted(set(CVF_CLOSURE) - found)[:5]))
    if errs:
        return errs
    try:
        rels = delivery_selection(branding)
        cache = {}
        def read(rel):
            if rel not in cache:
                cache[rel] = delivery_bytes(rel)
            return cache[rel]
        errs += _cvf_token_problems(rels, read)
        for rel in REF_REPLACEMENTS:
            read(rel)
        if state == 'clean':
            delivery_manifest(rels, branding)
            errs += ['%s: %s' % item for item in source_package_problems(ROOT)]
        else:
            errs += pin_problems()
    except ProjectionError as e:
        errs.append('Projection: %s.' % e)
    return errs


def materialize(dest, branding=True, manifest=True):
    """Ghi bản giao (bytes sau projection) vào thư mục dest. Trả danh sách đường dẫn đã ghi. Lỗi nguồn/projection ⇒ ProjectionError
    trước khi tạo gì dưới dest. / Write the shipped bytes under dest. A projection error is raised before anything is written."""
    problems = delivery_problems(branding)
    if problems:
        raise ProjectionError('DELIVERY_PROBLEMS', problems[0] + (' (+%d)' % (len(problems) - 1) if len(problems) > 1 else ''))
    rels = delivery_selection(branding)
    data = {rel: delivery_bytes(rel) for rel in rels}
    if manifest:
        rels = sorted(rels + ['MANIFEST.sha256'], key=_walk_key)
        data['MANIFEST.sha256'] = delivery_manifest([r for r in rels if r != 'MANIFEST.sha256'], branding)
    for rel in rels:
        dst = os.path.join(dest, *rel.split('/'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(data[rel])
        if rel.endswith(('.command', '.sh')) and os.path.isfile(P(rel)) and os.access(P(rel), os.X_OK):
            os.chmod(dst, 0o755)
    return rels


# ---------------------------------------------------------------- guard tương thích trước mọi mutation (I3)
def _same_machine(a, b):
    return a == b


def cvf_target_problems(project, source_bytes):
    """Tương thích `.cvf` của ĐÍCH với bộ giao; chỉ đọc cấu trúc và bytes (không chạy mã đích, không lấy policy đích làm quyền).
    source_bytes(rel) → bytes giao hoặc None. Trả [(mã, chi tiết)]; rỗng = đích không `.cvf` (thêm candidate) hoặc cùng v3 đúng machine bytes.
    Compatibility of the TARGET's `.cvf` with the shipped set: static bytes only. [] means absent (a candidate may be added) or the same v3 machine bytes."""
    kind, found = cvf_inventory(project)
    if kind == 'ABSENT':
        return []
    if kind == 'NOT_DIR':
        return [('CVF_NOT_A_DIRECTORY', '.cvf không phải thư mục thường')]
    out = []
    outside = sorted(f for f in found if f not in CVF_CLOSURE)
    if outside:
        out.append(('CVF_OUTSIDE_V3_CLOSURE', 'v1/v2/không rõ hoặc thừa: ' + ', '.join(outside[:5]) + (' ...' if len(outside) > 5 else '')))
    present = [m for m in CVF_MACHINE if m in found]
    missing = sorted(set(CVF_CLOSURE) - found)
    if missing:
        out.append(('CVF_PARTIAL', 'thiếu closure file: ' + ', '.join(missing)[:200]))
    differ = []
    for m in present:
        want = source_bytes(m)
        try:
            with open(os.path.join(project, *m.split('/')), 'rb') as f:
                have = f.read()
        except OSError:
            differ.append(m)
            continue
        if want is None or not _same_machine(have, want):
            differ.append(m)
    if differ:
        out.append(('CVF_MACHINE_DIFFERS', 'khác bytes của bộ giao: ' + ', '.join(differ[:5]) + (' ...' if len(differ) > 5 else '')))
    return out


def source_package_problems(source):
    """Nguồn của nâng cấp phải là bộ package đầy đủ, MANIFEST nhất quán với file thật, `.cvf` (nếu có) đúng closure v3.
    The upgrade source must be a complete package with a consistent MANIFEST and an exact v3 `.cvf` closure (when it has one)."""
    out = []
    path = os.path.join(source, 'MANIFEST.sha256')
    if not os.path.isfile(path):
        return [('SOURCE_MANIFEST_MISSING', 'Package mới không có MANIFEST.sha256')]
    bad, declared, private = [], set(), []
    with io.open(path, encoding='utf-8', newline='') as f:
        for line in f.read().splitlines():
            if not line.strip() or '  ' not in line:
                continue
            h, rel = line.split('  ', 1)
            declared.add(rel)
            if intake_config(rel) or (in_user_dir(rel) and not package_readme(rel)):
                private.append(rel)
                continue
            if rel in USER_FILES or rel == 'MANIFEST.sha256':
                continue
            full = os.path.join(source, *rel.split('/'))
            try:
                with open(full, 'rb') as g:
                    data = g.read()
            except OSError:
                bad.append(rel)
                continue
            if sha_bytes(rel, data) != h:
                bad.append(rel)
    if private:
        out.append(('SOURCE_MANIFEST_USER_DATA', 'MANIFEST của package mới chứa đường dẫn dữ liệu project ngoài khung: ' + ', '.join(private[:5])))
    if bad:
        out.append(('SOURCE_MANIFEST_INCONSISTENT', 'MANIFEST của package mới lệch file thật (dùng ZIP hoặc bản dựng RC, không dùng kho nguồn): ' + ', '.join(bad[:5]) + (' ...' if len(bad) > 5 else '')))
    kind, found = cvf_inventory(source)
    if kind != 'ABSENT' and (kind != 'DIR' or found != set(CVF_CLOSURE)):
        out.append(('SOURCE_CVF_NOT_V3_CLOSURE', '.cvf của package mới không đúng closure v3: thừa %s, thiếu %s' % (
            sorted(found - set(CVF_CLOSURE))[:5], sorted(set(CVF_CLOSURE) - found)[:5])))
    if kind != 'ABSENT':
        missing = sorted(set(CVF_CLOSURE + CVF_DEPENDENCIES) - declared)
        if missing:
            out.append(('SOURCE_MANIFEST_INCOMPLETE', 'MANIFEST thiếu runtime/owner: ' + ', '.join(missing[:5])))
        out += [('SOURCE_OWNER_PIN_MISMATCH', msg) for msg in pin_problems(source)]
    return out


def tree_problems():
    """Cây phát hành (không có release_templates/): `.cvf` đúng closure, không dữ liệu vận hành, bytes pin khớp policy.
    A release tree: exact `.cvf` closure, no runtime data, pinned bytes equal to the policy pins."""
    out = []
    kind, found = cvf_inventory(ROOT)
    if kind != 'DIR':
        out.append('Bản phát hành thiếu thư mục .cvf (cần closure v3).')
    else:
        extra, missing = sorted(found - set(CVF_CLOSURE)), sorted(set(CVF_CLOSURE) - found)
        if extra:
            out.append('Bản phát hành có file .cvf ngoài closure v3 (v1/v2, fixtures, evidence hoặc runtime): %s.' % ', '.join(extra[:8]))
        if missing:
            out.append('Bản phát hành thiếu file closure .cvf v3: %s.' % ', '.join(missing[:8]))
    for rel in private_files():
        out.append('Bản phát hành có file tài khoản/khóa thật %s (không được đóng gói).' % rel)
    rt = P(RUNTIME_DIR)
    if os.path.lexists(rt):
        out.append('Bản phát hành có dữ liệu vận hành %s (không được đóng gói).' % RUNTIME_DIR)
    if os.path.lexists(P(NATIVE_DIR)):
        out.append('Bản phát hành có native của host %s/ (trạng thái riêng của project, không được đóng gói).' % NATIVE_DIR)
    try:
        with open(P(PROFILE_REL), 'rb') as f:
            shipped = f.read().replace(b'\r\n', b'\n')
        if shipped != _ep().clean_profile_bytes():
            out.append('Bản phát hành mang profile không sạch %s (chỉ được giao mẫu sạch).' % PROFILE_REL)
    except OSError:
        out.append('Bản phát hành thiếu %s (mẫu profile sạch).' % PROFILE_REL)
    return out


def pin_problems(base=None):
    """Bytes giao của owner đã pin trong policy v3 phải đúng pin (hash bytes thô). Chỉ đọc, không chạy mã. / Pinned owner bytes must equal the policy pin."""
    out = []
    base = base or ROOT
    policy = os.path.join(base, '.cvf', 'rules', 'v3', 'ROUTING_POLICY.json')
    try:
        with open(policy, 'rb') as f:
            doc = json.loads(f.read().decode('utf-8-sig'))
    except (OSError, ValueError):
        return ['Không đọc được policy v3 để đối chiếu pin owner.']
    pins = list(doc.get('owner_protocols') or []) + ([doc['operational_context_protocol']] if isinstance(doc.get('operational_context_protocol'), dict) else [])
    for pin in pins:
        rel, want = pin.get('entrypoint'), pin.get('entrypoint_sha256')
        if not isinstance(rel, str) or not isinstance(want, str):
            out.append('Policy v3: một pin owner thiếu entrypoint hoặc hash.')
            continue
        if rel not in BYTE_EXACT:
            out.append('Policy v3 pin %s nhưng bản giao chưa liệt kê file đó là giữ nguyên từng byte (BYTE_EXACT).' % rel)
            continue
        try:
            with open(os.path.join(base, *rel.split('/')), 'rb') as f:
                got = 'sha256:' + hashlib.sha256(f.read()).hexdigest()
        except OSError:
            out.append('Thiếu owner đã pin: %s.' % rel)
            continue
        if got != want:
            out.append('Bytes của %s không khớp pin trong policy v3 (EOL hoặc nội dung đã đổi).' % rel)
    return out

# ---------------------------------------------------------------- manifest
def write_manifest():
    lines = ['%s  %s' % (sha(r), r) for r in all_files() if in_manifest(r)]
    with io.open(P('MANIFEST.sha256'), 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines) + '\n')
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
        if intake_config(rel) or rel in USER_FILES:
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
        if f.endswith('.py') and not user_owned(f):
            for ln, msg in py38_problems(rd(f), f):
                errs.append('%s:%d: không tương thích Python 3.8 — %s.' % (f, ln, msg))
    return errs

def crlf_warning_paths(files):
    """Warn on ordinary text only; byte-exact owners and Git -text retain raw bytes.

    Packaged checks do not require Git. In a source checkout Git supplies effective
    attributes (including local overrides). Without Git, only literal root paths
    declared -text are exempt; wildcard rules stay conservative.
    """
    candidates = [f for f in files if f.endswith(('.md', '.html', '.py', '.json')) and '\r\n' in rd(f)]
    raw_byte_paths = set(BYTE_EXACT)
    git_attributes = False
    if candidates and os.path.isdir(P('release_templates')) and os.path.exists(P('.git')):
        try:
            result = subprocess.run(['git', 'check-attr', '-z', '--stdin', 'text'], cwd=ROOT,
                                    input=b''.join(os.fsencode(p) + b'\0' for p in candidates),
                                    capture_output=True, timeout=10)
            parts = result.stdout.split(b'\0')
            if result.returncode == 0 and parts[-1:] == [b''] and len(parts[:-1]) == len(candidates) * 3:
                git_attributes = True
                raw_byte_paths.update(os.fsdecode(parts[i]) for i in range(0, len(parts) - 1, 3)
                                      if parts[i + 1:i + 3] == [b'text', b'unset'])
        except (OSError, subprocess.TimeoutExpired):
            pass  # conservative fallback: ordinary CRLF still warns
    if not git_attributes and os.path.isfile(P('.gitattributes')):
        for line in rd('.gitattributes').splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[1] == '-text':
                path = fields[0]
                if not any(c in path for c in '*?[]\\"') and not path.startswith(('#', '!', '/')) and '..' not in path.split('/'):
                    raw_byte_paths.add(path)
    return [f for f in candidates if f not in raw_byte_paths]


def pack_index_problems():
    """Installed PACK rows must resolve; clean delivery templates cannot install packs.

    A dangling declared target is an error: the index would otherwise advertise
    an unavailable capability. Live user index choices are never rewritten.
    """
    errors = []
    for rel in ('.agent/SKILL_INDEX.md', 'en/.agent/SKILL_INDEX.md'):
        for index, template in ((rel, False), ('release_templates/' + rel, True)):
            if not os.path.isfile(P(index)):
                continue
            for line in rd(index).splitlines():
                cells = [s.strip() for s in line.strip().strip('|').split('|')]
                if len(cells) < 4 or cells[2] != 'PACK':
                    continue
                if template:
                    errors.append('%s: mẫu sạch không được có dòng PACK (%s).' % (index, cells[0]))
                elif not os.path.isfile(P(cells[3])):
                    errors.append('%s: %s trỏ tới file không có (%s).' % (index, cells[0], cells[3]))
    return errors


def check_all(release=False):
    errs, warns = [], []
    raw_files = all_files()
    # Private config is diagnosed by path only, never by parsing or hashing choices.
    files = [f for f in raw_files if not intake_config(f)]
    source_tree = os.path.isdir(P('release_templates'))
    if release and not source_tree:
        errs += ['Có file người dùng trong bản phát hành: %s.' % f for f in raw_files if intake_config(f)]
    if source_tree or not release:
        # Parse package code/docs only. A staged release retains the complete list
        # so unexpected project data still fails the release boundary below.
        files = [f for f in files if not user_owned(f) or f in USER_FILES]
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
        if f in ('CHANGELOG.md', 'MANIFEST.sha256') or not f.endswith(('.md', '.html', '.py', '.json')) or user_owned(f):
            continue  # file của project (SKILL_INDEX có dòng gói, tài liệu trong references/...) có số phiên bản riêng / project files carry their own versions
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
    errs += pack_index_problems()
    # cây en/ phủ đủ các file chỉ có nội dung tiếng Việt
    root_lang = [f for f in files if not f.startswith(('en/', 'docs/', 'tools/', 'dist/')) and f.endswith(('.md', '.html', '.csv', '.txt')) and
                 (f in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md', 'PROJECT.md', 'README.md') or f.startswith(('.agent/', 'archive/', 'output/', 'working/', 'references/', 'skills/', 'examples/')))
                 and '/scripts/' not in f and f not in ('.agent/PACKAGE_INFO.json',)
                 and not (user_owned(f) and f not in USER_FILES)  # mẫu PROJECT/STATE... vẫn cần bản en/ cho lớp phủ; nội dung của người dùng (kể cả references/, working/...): chỉ README cần bản en/ / user content: only READMEs need en/
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
    source_tree = os.path.isdir(P('release_templates'))
    for f in md:
        if f == 'CHANGELOG.md' or user_owned(f): continue  # tài liệu của project có thể nhắc file của chính project / project docs may name project files
        if source_tree and f.startswith(CVF_DIR + '/') and f not in CVF_CLOSURE:
            continue  # tài liệu v1/v2 của người bảo trì không được giao: nhắc tests/, roadmap/ là đúng ở kho nguồn / the maintainers' own .cvf docs are not delivered
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
            if tok.endswith('.json') and private_file(tok.rsplit('/', 1)[-1]) and os.path.isfile(P(tok[:-5] + '.example.json')):
                continue  # Link tài liệu tới credentials thật chỉ hợp lệ khi có mẫu .example.json tương ứng.
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
    crlf = crlf_warning_paths(files)
    if crlf: warns.append('Có %d file dùng CRLF (ví dụ %s); nên dùng LF.' % (len(crlf), crlf[0]))
    # 7a. schema profile và mặc định / profile schema and its default
    errs += _ep().schema_problems()
    # profile sống của một project đã khởi tạo: chỉ cảnh báo (dữ liệu của người dùng, không tự sửa); thiếu/hỏng/phiên bản lạ/mâu thuẫn không bị coi là đạt
    # the live profile of an initialised project: a warning only (user data, never repaired); missing, damaged, future or conflicting is not "fine"
    if os.path.exists(P('.agent/PACKAGE_INFO.json')):
        rep = _ep().inspect(ROOT)
        if rep['state'] != 'OK':
            warns.append('Profile project (%s): %s' % (rep['state'], ' '.join(_ep().reason_text(r) for r in rep['reasons'][:2]) or '-'))
    # 7b. gói lĩnh vực
    if os.path.isdir(P('packs')):
        import pack as packmod
        for n in sorted(os.listdir(P('packs'))):
            if os.path.isdir(P('packs/' + n)):
                for e in packmod.validate_pack(P('packs/' + n), n):
                    errs.append('Gói: ' + e)
    # 7c. kho nguồn chưa khởi tạo: STATE phải là mẫu sạch hoặc mang dấu người bảo trì, để init_project.py không mang sang project
    # source tree not initialised: STATE is the clean template or carries the maintainer marker, so init does not carry it over
    if os.path.isdir(P('release_templates')) and not os.path.exists(P('.agent/PACKAGE_INFO.json')) and os.path.isfile(P('.agent/STATE.md')):
        st = rd('.agent/STATE.md')
        if '[Phase/trạng thái hiện tại]' not in st and '<!-- local-agent-workspace: maintainer-state -->' not in st:
            errs.append('.agent/STATE.md của kho nguồn thiếu dấu "<!-- local-agent-workspace: maintainer-state -->" (init_project.py dựa vào dấu này để không mang trạng thái người bảo trì sang project).')
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
        branding = set(branding_files())  # logo, tên đơn vị, font được phép vào ZIP / organization branding may ship
        boundary_files = (f for f in raw_files if not source_tree or f.startswith(('assets/', 'en/assets/')))
        for f in boundary_files:
            if in_user_dir(f) and not package_readme(f) and f not in branding:
                errs.append('Có file người dùng trong bản phát hành: %s.' % f)
        # runtime v3: kho nguồn phải giao được (projection áp dụng sạch); cây phát hành phải có đúng closure, không runtime, tham chiếu .cvf thật
        # v3 runtime: the source must be deliverable; a release tree must hold exactly the closure, no runtime data, and resolvable .cvf references
        if os.path.isdir(P('release_templates')):
            errs += delivery_problems()
        else:
            errs += tree_problems()
            errs += _cvf_token_problems(files, lambda r: open(P(r), 'rb').read())
        errs += pin_problems()
    return errs, warns

def run_checks(release=False):
    """Mọi kiểm tra của chế độ kiểm tra: check_all (gồm HTML/Markdown) cộng tương thích Python 3.8."""
    errs, warns = check_all(release=release)
    return errs + check_py38(), warns

def source_eol_problems(paths):
    """Maintainer-only, explicit files: ask Git for effective attributes, then check raw bytes.
    This scoped check uses effective Git attributes; ordinary package warnings use a conservative literal -text fallback.
    """
    if not os.path.isdir(P('release_templates')) or not os.path.exists(P('.git')):
        return ['--check-eol chỉ dùng trong kho nguồn LAW có Git; không áp vào project người dùng.'], []
    rels = list(dict.fromkeys(p.replace('\\', '/') for p in paths))
    for rel in rels:
        if os.path.isabs(rel) or ':' in rel or any(p in ('', '.', '..') for p in rel.split('/')):
            return ['Đường dẫn EOL phải tương đối từ gốc kho nguồn: %r.' % rel], []
        try:
            inside = os.path.commonpath((os.path.realpath(ROOT), os.path.realpath(P(rel)))) == os.path.realpath(ROOT)
        except (OSError, ValueError):  # e.g. a Windows junction resolving onto another drive
            inside = False
        if not inside:
            return ['File EOL nằm ngoài kho nguồn: %r.' % rel], []
    try:
        result = subprocess.run(['git', 'check-attr', '-z', '--stdin', 'text', 'eol'], cwd=ROOT,
                                input=b''.join(os.fsencode(p) + b'\0' for p in rels), capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return ['Không đọc được attributes Git; chưa kiểm EOL.'], []
    if result.returncode:
        return ['git check-attr không thành công; chưa kiểm EOL.'], []
    parts = result.stdout.split(b'\0')
    if not parts or parts[-1] != b'' or len(parts[:-1]) != len(rels) * 6:
        return ['Kết quả git check-attr không đầy đủ; chưa kiểm EOL.'], []
    attrs = {}
    for i in range(0, len(parts) - 1, 3):
        path, name, value = (os.fsdecode(p) for p in parts[i:i + 3])
        attrs.setdefault(path, {})[name] = value
    errs, skipped = [], []
    for rel in rels:
        attr = attrs.get(rel, {})
        if not os.path.isfile(P(rel)):
            errs.append('%s: không đọc được file để kiểm EOL.' % rel)
            continue
        if attr.get('text') == 'unset':
            skipped.append(rel)  # raw-byte owners/binary: do not infer LF from the inherited eol attribute
            continue
        expected = attr.get('eol')
        if expected not in ('lf', 'crlf'):
            errs.append('%s: không có attributes eol=lf/crlf được hỗ trợ; chưa kiểm EOL.' % rel)
            continue
        try:
            with open(P(rel), 'rb') as f:
                raw = f.read()
        except OSError:
            errs.append('%s: không đọc được file để kiểm EOL.' % rel)
            continue
        if b'\0' in raw:
            errs.append('%s: dữ liệu nhị phân/encoding không hỗ trợ; chưa kiểm EOL.' % rel)
            continue
        rest = raw if expected == 'lf' else raw.replace(b'\r\n', b'')
        if b'\r' in rest or (expected == 'crlf' and b'\n' in rest):
            errs.append('%s: EOL lệch attributes eol=%s (có CRLF/LF lẫn hoặc CR đơn); giữ đúng EOL, không tự sửa file đã pin.' % (rel, expected))
    return errs, skipped


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--release', action='store_true')
    ap.add_argument('--write-manifest', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--check-eol', nargs='+', metavar='FILE', help='kho nguồn có Git: kiểm EOL đúng các file được nêu, chỉ đọc')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.check_eol is not None:
        if a.release or a.verify or a.write_manifest:
            ap.error('--check-eol dùng riêng, không kết hợp --release/--verify/--write-manifest')
        errs, skipped = source_eol_problems(a.check_eol)
        for rel in skipped:
            print('Giữ raw bytes (-text), không kiểm EOL: ' + rel)
        for error in errs:
            print('LỖI: ' + error)
        print('Kiểm EOL: %d lỗi; không sửa file.' % len(errs))
        if a.result_json:
            emit(make('issues' if errs else 'success', code=1 if errs else 0, message='Kiểm EOL kho nguồn', changes=False,
                      findings=[{'severity': 'error', 'message': e} for e in errs],
                      unchecked=[{'path': rel, 'reason': 'text=unset; giữ raw bytes, không kiểm EOL'} for rel in skipped]))
        sys.exit(1 if errs else 0)
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
