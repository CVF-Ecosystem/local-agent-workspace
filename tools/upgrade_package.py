#!/usr/bin/env python3
"""Nâng cấp một project lên bản package mới mà không ghi đè việc của bạn.
Upgrade a project to a newer package version without overwriting your work.

Cách dùng / Usage (mặc định chỉ BÁO CÁO, thêm --apply mới ghi / report only by default, --apply writes):
  # chạy từ project, chỉ tới thư mục package mới đã giải nén
  python tools/upgrade_package.py --from "D:\\goi-moi\\local-agent-workspace-v1.9.0"
  # hoặc chạy từ package mới, chỉ tới project cần nâng cấp (dùng cho lần nâng cấp đầu tiên)
  python tools/upgrade_package.py --project "D:\\cac-project\\ten-project" --apply

Quy tắc so sánh ba bên (bản gốc cũ trong MANIFEST của project, bản hiện tại của project, bản mới):
  - file chưa ai sửa và package có bản mới   -> cập nhật;
  - file mới của package                      -> thêm;
  - file bạn đã sửa, package không đổi        -> giữ nguyên của bạn;
  - file bạn đã sửa và package cũng đổi       -> KHÔNG ghi đè, lưu bản mới thành <tên>.new để bạn hợp nhất;
  - file của bạn (PROJECT, STATE, INDEX...), thư mục references/working/output/archive/skills riêng: không đụng.
Script không xóa file nào. Cần Python 3.8+, không dùng mạng.
"""
import argparse, datetime, hashlib, io, json, os, re, shutil, sys
from result_schema import emit, make
import transaction as tx
import check_package as cp
import execution_profile as ep
from check_package import branding_files

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TX = {'id': None}  # mã giao dịch đang ghi / transaction id of the current write
TEXT_EXT = ('.md', '.html', '.py', '.json', '.txt', '.sha256', '.css', '.js', '')
USER_FILES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
              '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md', '.agent/PACKAGE_INFO.json',
              '.agent/MERGE_STATUS.json', 'setup_answers.json', ep.PROFILE_REL}
OVERLAY_SKIP = {'en/PROJECT_INSTRUCTIONS_SNIPPET.md'}
LANG = 'vi'
RESULT_REQUESTED = '--result-json' in sys.argv
LAST_RESULT = None

def L(vi, en): return en if LANG == 'en' else vi

def sha_data(rel, data):
    if os.path.splitext(rel)[1] in TEXT_EXT:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()

def read_manifest(base):
    p = os.path.join(base, 'MANIFEST.sha256')
    if not os.path.isfile(p):
        return None
    m = {}
    with io.open(p, encoding='utf-8') as f:
        for l in f.read().splitlines():
            if l.strip():
                h, r = l.split('  ', 1)
                m[r] = h
    return m

IDENTITY_LINE = re.compile(r'^([0-9a-f]{64})  (.+)$')

def _unknown_side(reason):
    return {'state': 'UNKNOWN', 'entries': None, 'digest': None, 'reason': reason}

def manifest_identity(base):
    """Baseline nội dung gói ghi trong MANIFEST.sha256 của `base`: digest của các entry (path, hash) hợp lệ đã sắp theo path, không đổi theo EOL hay thứ tự dòng.
    Thiếu/không đọc được/hỏng dòng/trùng path/mơ hồ so với read_manifest thì UNKNOWN kèm lý do, không suy từ VERSION. Chỉ đọc, không ghi.
    The package baseline recorded in `base`'s MANIFEST.sha256: a digest of the sorted valid (path, hash) entries, independent of EOL and line order.
    A missing, unreadable, malformed, duplicate-path or ambiguous manifest is UNKNOWN with a reason; the version label is never used as a stand-in."""
    try:
        with open(os.path.join(base, 'MANIFEST.sha256'), 'rb') as f:
            raw = f.read()
    except FileNotFoundError:
        return _unknown_side('MANIFEST_MISSING')
    except OSError:
        return _unknown_side('MANIFEST_UNREADABLE')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        return _unknown_side('MANIFEST_UNREADABLE')
    entries = {}
    for line in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        if not line.strip():
            continue
        m = IDENTITY_LINE.match(line)
        if not m:
            return _unknown_side('MANIFEST_MALFORMED_LINE')
        if m.group(2) in entries:
            return _unknown_side('MANIFEST_DUPLICATE_PATH')
        entries[m.group(2)] = m.group(1)
    try:
        if read_manifest(base) != entries:
            return _unknown_side('MANIFEST_AMBIGUOUS')
    except (ValueError, OSError):
        return _unknown_side('MANIFEST_AMBIGUOUS')
    entries.pop('MANIFEST.sha256', None)
    if not entries:
        return _unknown_side('MANIFEST_EMPTY')
    body = ''.join('%s  %s\n' % (entries[r], r) for r in sorted(entries))
    return {'state': 'KNOWN', 'entries': len(entries), 'digest': 'sha256:' + hashlib.sha256(body.encode('utf-8')).hexdigest(), 'reason': None}

def package_identity(project, source, ov, nv):
    """Quan hệ giữa nhãn phiên bản và baseline nội dung gói của project (đã cài) với package nguồn. Chỉ mô tả; không quyết định kế hoạch.
    Relation between the version labels and the package-content baselines of the project (installed) and the source package. Descriptive only."""
    inst, src = manifest_identity(project), manifest_identity(source)
    same_label = ov == nv
    known = inst['state'] == 'KNOWN' and src['state'] == 'KNOWN'
    same_base = (inst['digest'] == src['digest']) if known else None
    relation = 'UNKNOWN' if not known else '%s_LABEL_%s_BASELINE' % ('SAME' if same_label else 'DIFFERENT', 'SAME' if same_base else 'DIFFERENT')
    return {'relation': relation, 'version': {'installed': ov, 'source': nv, 'same': same_label},
            'baseline': {'installed': inst, 'source': src, 'same': same_base}}

def identity_text(pi):
    """Dòng thông báo cho người dùng: nhãn phiên bản không đồng nghĩa nội dung gói. / The user-facing line: a version label is not the package content."""
    b, v = pi['baseline'], pi['version']
    short = lambda side: side['digest'][7:19] if side['digest'] else '?'
    rel = pi['relation']
    if rel == 'SAME_LABEL_DIFFERENT_BASELINE':
        body = L('Nhãn phiên bản không đổi (v%s) nhưng NỘI DUNG baseline của gói đã khác (đã cài %s, package mới %s). Nhãn không tăng; danh mục dưới đây mới là việc thực tế.',
                 'The version label is unchanged (v%s) but the package CONTENT baseline differs (installed %s, new package %s). The label did not go up; the lists below are the real work.') % (v['source'], short(b['installed']), short(b['source']))
    elif rel == 'SAME_LABEL_SAME_BASELINE':
        body = L('Nhãn phiên bản và baseline nội dung gói đều giống nhau (%s). Chỉ nói về baseline gói ghi trong MANIFEST, không có nghĩa project đã sạch hay đồng bộ: các mục dưới đây (nếu có) vẫn là việc thực tế.',
                 'The version label and the package content baseline are both the same (%s). This is only about the package baseline recorded in the MANIFEST, not a claim that the project is clean or in sync: the lists below (if any) are still the real work.') % short(b['source'])
    elif rel == 'DIFFERENT_LABEL_SAME_BASELINE':
        body = L('Nhãn phiên bản đổi (v%s -> v%s) nhưng baseline nội dung gói giống nhau (%s). Các mục dưới đây vẫn là việc thực tế.',
                 'The version label changed (v%s -> v%s) but the package content baseline is the same (%s). The lists below are still the real work.') % (v['installed'], v['source'], short(b['source']))
    elif rel == 'DIFFERENT_LABEL_DIFFERENT_BASELINE':
        body = L('Nhãn phiên bản đổi (v%s -> v%s) và baseline nội dung gói khác (đã cài %s, package mới %s).',
                 'The version label changed (v%s -> v%s) and the package content baseline differs (installed %s, new package %s).') % (v['installed'], v['source'], short(b['installed']), short(b['source']))
    else:
        why = '; '.join('%s: %s' % (L(vi, en), b[k]['reason']) for k, vi, en in (('installed', 'đã cài', 'installed'), ('source', 'package mới', 'new package')) if b[k]['state'] != 'KNOWN')
        body = L('Chưa xác định baseline nội dung gói (%s). Không suy từ nhãn phiên bản; kế hoạch dưới đây theo nội dung file thực.',
                 'The package content baseline is not determined (%s). It is not inferred from the version label; the plan below follows the real file contents.') % why
    return '[%s] %s' % (rel, body)

def read_version(base):
    try:
        with io.open(os.path.join(base, 'VERSION'), encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return '0.0.0'

def vt(v):
    try:
        return tuple(int(x) for x in v.split('.'))
    except ValueError:
        return (0, 0, 0)

def plan(project, source, lang):
    """Trả về dict danh mục việc: add, update, conflict, obsolete, same, kept, user_template."""
    old, new = read_manifest(project), read_manifest(source)
    out = {k: [] for k in ('add', 'update', 'conflict', 'obsolete', 'kept', 'user_missing', 'user_changed')}
    # Hash THÔ của đúng bytes đã dùng để phân loại từng file sẽ ghi (None = chưa có file); main() gắn nó vào Transaction.add làm expected_before,
    # nên file lưu lại sau lúc lập kế hoạch bị từ chối thay vì bị ghi đè.
    # Raw hash of the exact bytes each file to be written was classified on (None = absent); main() binds it to Transaction.add as
    # expected_before, so a file saved after planning is refused instead of overwritten.
    out['snapshot'] = {}
    def use_overlay(rel, mf):
        ov = 'en/' + rel
        return lang == 'en' and not rel.startswith('en/') and ov in mf and ov not in OVERLAY_SKIP
    for rel in sorted(new):
        if rel == 'MANIFEST.sha256':
            continue
        src_rel = ('en/' + rel) if use_overlay(rel, new) else rel
        new_h = new[src_rel]
        dst = os.path.join(project, *rel.split('/'))
        exists = os.path.isfile(dst)
        if rel in USER_FILES:
            if not exists:
                out['user_missing'].append((rel, src_rel)); out['snapshot'][rel] = None
            else:
                old_src = ('en/' + rel) if use_overlay(rel, old) else rel
                if old.get(old_src) not in (None, new_h):
                    out['user_changed'].append(rel)
            continue
        if not exists:
            out['add'].append((rel, src_rel)); out['snapshot'][rel] = None; continue
        raw = read_bytes(project, rel)  # một lần đọc: vừa phân loại vừa làm snapshot / one read serves both the classification and the snapshot
        cur_h = sha_data(rel, raw)
        if cur_h == new_h:
            continue
        old_src = ('en/' + rel) if use_overlay(rel, old) else rel
        old_h = old.get(old_src)
        if old_h is not None and cur_h == old_h:
            out['update'].append((rel, src_rel)); out['snapshot'][rel] = hashlib.sha256(raw).hexdigest()
        elif old_h is not None and old_h == new_h:
            out['kept'].append(rel)
        else:
            out['conflict'].append((rel, src_rel))
    # Nhận diện đơn vị của bản mới (logo, tên, font): chỉ thêm khi dự án còn thiếu, không ghi đè nhận diện riêng của dự án.
    # Organization branding in the new package: added only where the project lacks it, never overwriting its own.
    src_brand, own_brand = branding_files(source), branding_files(project)
    if not any(not r.startswith('assets/fonts/') for r in own_brand):
        out['user_missing'] += [(r, r) for r in src_brand if not r.startswith('assets/fonts/')]
    out['user_missing'] += [(r, r) for r in src_brand if r.startswith('assets/fonts/') and r not in own_brand]
    for rel, _ in out['user_missing']:
        out['snapshot'].setdefault(rel, tx.sha_file(os.path.join(project, *rel.split('/'))))
    for rel in sorted(old):
        if rel not in new and rel != 'MANIFEST.sha256' and rel not in USER_FILES and os.path.isfile(os.path.join(project, *rel.split('/'))):
            out['obsolete'].append(rel)
    return out

ROW_RE = re.compile(r'^\| ([a-z0-9-]+) \| LOCAL \| SHARED \| (\S+) \|.*$', re.M)

def index_rows(project, source, lang, plan_):
    """Dòng skill dùng chung có trong SKILL_INDEX của package nhưng chưa có trong SKILL_INDEX của project.
    Shared-skill rows present in the package SKILL_INDEX but missing from the project's SKILL_INDEX."""
    src_i = os.path.join(source, *(('en/.agent/SKILL_INDEX.md') if lang == 'en' else '.agent/SKILL_INDEX.md').split('/'))
    dst_i = os.path.join(project, '.agent', 'SKILL_INDEX.md')
    if not (os.path.isfile(src_i) and os.path.isfile(dst_i)):
        return []
    with io.open(dst_i, encoding='utf-8') as f:
        have = {m.group(1) for m in ROW_RE.finditer(f.read())}
    adding = {rel for rel, _ in plan_['add']}
    out = []
    with io.open(src_i, encoding='utf-8') as f:
        for m in ROW_RE.finditer(f.read()):
            if m.group(1) in have:
                continue
            loc = m.group(2)
            if os.path.isfile(os.path.join(project, *loc.split('/'))) or loc in adding:
                out.append(m.group(0))
    return out

def render_index_rows(txt, rows):
    """Nội dung SKILL_INDEX sau khi thêm dòng (không ghi file). / SKILL_INDEX text with rows appended (no write)."""
    last = None
    for m in re.finditer(r'^\| [a-z0-9-]+ \| [A-Z]+ \| [A-Z]+ \|.*\n?', txt, re.M):
        last = m
    ins = ''.join(r + '\n' for r in rows)
    if last is None:
        return txt.rstrip('\n') + '\n' + ins
    end = last.end()
    if not txt[end - 1:end] == '\n':
        txt = txt[:end] + '\n' + txt[end:]; end += 1
    return txt[:end] + ins + txt[end:]

def read_bytes(base, rel):
    with open(os.path.join(base, *rel.split('/')), 'rb') as f:
        return f.read()

def compat_blocks(project, source, p):
    """[(mã, chi tiết)] khiến PHẢI chặn trước mọi mutation, kể cả --apply --force. Chỉ đọc cấu trúc và bytes, không chạy mã của đích.
    Nguồn: package đầy đủ, MANIFEST nhất quán, `.cvf` đúng closure v3. Đích: không `.cvf` (thêm candidate) hoặc cùng v3 đúng byte máy đọc;
    owner/phụ thuộc không được ở trạng thái xung đột; `.cvf` do người dùng sửa mà package cũng đổi thì chặn, không tạo .new rồi coi là xong.
    Blocks that must stop everything before any mutation, even with --apply --force. Static reads only: the target's code is never run."""
    out = list(cp.source_package_problems(source))
    if cp.cvf_inventory(source)[0] == 'ABSENT':
        if cp.cvf_inventory(project)[0] != 'ABSENT':
            out.append(('SOURCE_CVF_MISSING_FOR_TARGET', 'Đích đã có .cvf nhưng package mới không có runtime tương thích'))
        return out  # package mới không mang .cvf: không có gì để thêm hay so / the new package carries no .cvf: nothing to add or compare
    def src(rel):
        try:
            return read_bytes(source, rel)
        except OSError:
            return None
    out += cp.cvf_target_problems(project, src)
    updating = {r for r, _ in p['update']}  # đúng bytes của một bản package cũ, chưa ai sửa: chính giao dịch này thay bằng bytes bản giao / untouched bytes of an older package, replaced by this very transaction
    for rel in cp.CVF_DEPENDENCIES:
        path = os.path.join(project, *rel.split('/'))
        if os.path.lexists(path) and (cp._is_link(path) or not os.path.isfile(path) or (rel not in updating and read_bytes(project, rel) != src(rel))):
            out.append(('CVF_OWNER_DEPENDENCY_DIFFERS', rel))
    stuck = {r for r, _ in p['conflict']} | set(p['kept'])
    out += [('CVF_OWNER_DEPENDENCY_CONFLICT', '%s đã bị sửa trong project nên không khớp bộ giao' % r) for r in cp.CVF_DEPENDENCIES if r in stuck]
    out += [('CVF_USER_EDIT_CONFLICT', '%s đã bị sửa và package cũng đổi' % r) for r, _ in p['conflict'] if r.startswith(cp.CVF_DIR + '/')]
    return out

SOURCE_BAD = ('SOURCE_MANIFEST_MISSING', 'SOURCE_MANIFEST_INCONSISTENT', 'SOURCE_MANIFEST_INCOMPLETE', 'SOURCE_MANIFEST_USER_DATA', 'SOURCE_OWNER_PIN_MISMATCH', 'SOURCE_CVF_NOT_V3_CLOSURE')
CVF_BAD = ('CVF_NOT_A_DIRECTORY', 'CVF_PARTIAL', 'CVF_MACHINE_DIFFERS')

def block_steps(codes):
    """Bước xử lý cụ thể cho từng loại chặn (không bước nào dùng --force hay sửa MANIFEST để lách). / A concrete next step per kind of block; none uses --force or edits a MANIFEST to get around it."""
    out = []
    if any(c in SOURCE_BAD for c in codes):
        out.append(L('Nguồn nâng cấp không phải package phát hành nguyên vẹn. Giải nén lại từ ZIP phát hành (kiểm SHA-256 nếu có) vào thư mục mới rồi dùng thư mục đó; không dùng thư mục kho nguồn, không sửa MANIFEST cho khớp.',
                     'The upgrade source is not an intact release package. Extract the release ZIP again (check its SHA-256 if you have it) into a new folder and use that folder; do not use a source-repo folder or edit a MANIFEST to match.'))
    if 'SOURCE_CVF_MISSING_FOR_TARGET' in codes:
        out.append(L('Package nguồn không có .cvf trong khi project đã có: hạ xuống schema cũ không được hỗ trợ. Dùng package có phiên bản bằng hoặc cao hơn bản đã cài. --force không bỏ chặn này.',
                     'The source package has no .cvf while the project has one: going back to an older schema is not supported. Use a package whose version is equal to or higher than the installed one. --force does not lift this block.'))
    if any(c in CVF_BAD for c in codes):
        out.append(L('.cvf của project thiếu file, bị sửa hoặc khác bộ giao. Giữ nguyên project; khôi phục thư mục .cvf từ bản sao lưu hoặc từ package cùng phiên bản đã cài (đừng sửa tay), rồi xem trước lại. Công cụ không tự chuyển đổi.',
                     'The project .cvf is missing files, edited or different from the shipped set. Leave the project as it is; restore the .cvf folder from your backup or from the package of the version you installed (do not edit by hand), then preview again. The tool does not convert it.'))
    if 'CVF_OWNER_DEPENDENCY_DIFFERS' in codes or 'CVF_OWNER_DEPENDENCY_CONFLICT' in codes:
        out.append(L('Một file công cụ lõi (tên ở dòng CHẶN) đã bị sửa hoặc không phải file thường. Giữ bản sửa của bạn ở nơi riêng, đưa file về bản của package đã cài rồi xem trước lại, hoặc nhờ người bảo trì bộ công cụ.',
                     'A core tool file (named in the BLOCKED line) was edited or is not a plain file. Keep your edit somewhere else, put the file back to the installed package version and preview again, or ask the maintainer of the toolkit.'))
    if 'CVF_USER_EDIT_CONFLICT' in codes:
        out.append(L('Một tài liệu trong .cvf đã bị sửa và package cũng đổi. Giữ bản sửa của bạn ở nơi riêng, đưa file về bản của package đã cài rồi xem trước lại.',
                     'A document inside .cvf was edited and the package changed it too. Keep your edit somewhere else, put the file back to the installed package version and preview again.'))
    if not out:
        out.append(L('Đọc các dòng CHẶN ở trên. Project giữ nguyên, không có chuyển đổi tự động.', 'Read the BLOCKED lines above. The project is left as it is; there is no automatic conversion.'))
    out.append(L('Không dùng --force để vượt các chặn này: nó không bỏ chúng.', 'Do not use --force to get past these blocks: it does not lift them.'))
    return out

def pending_steps():
    """Khi đã có <tên>.new khác bản mới: giữ riêng bản đó bằng đường thủ công có sao lưu, không xóa. / When an existing <name>.new differs: set it aside by the manual, backed-up route; never delete."""
    return [L('Làm theo hướng dẫn nâng cấp, mục “Xử lý file .new”, đoạn “Cất .new của file khác bằng tay”: so sánh, chép file hiện hành và .new vào một thư mục mới trong archive/, kiểm hash, rồi chuyển (không xóa) .new vào đó và chạy lại. Không xóa .new hay sửa MANIFEST để vượt qua.',
              'Follow the upgrade guide, section “Handling .new files”, paragraph “Setting a .new of another file aside by hand”: compare, copy the current file and the .new into a new folder under archive/, check the hashes, then move (not delete) the .new there and run again. Do not delete the .new or edit the MANIFEST to get past this.')]

def merge_steps():
    """Sau khi ghi có <tên>.new: so sánh và quyết định theo hướng dẫn, giữ .new tới khi xử lý xong. / After writing a <name>.new: compare and decide per the guide, keep the .new until handled."""
    return [L('Với từng file có <tên>.new: so sánh với file của bạn rồi hợp nhất phần bạn muốn giữ theo hướng dẫn nâng cấp, mục “Xử lý file .new”. Giữ .new tới khi xử lý xong; không xóa .new để tắt cảnh báo.',
              'For each file that has a <name>.new: compare it with your file and merge what you want to keep as the upgrade guide, section “Handling .new files”, describes. Keep the .new until you are done; do not delete it to silence the warning.')]

def tx_next_actions(txid):
    return ['python tools/transaction.py resume %s' % txid, 'python tools/transaction.py rollback %s' % txid]


def main():
    global LANG, LAST_RESULT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--from', dest='source', help='thư mục package MỚI / the NEW package folder')
    ap.add_argument('--project', help='thư mục project cần nâng cấp / the project folder to upgrade')
    ap.add_argument('--apply', action='store_true', help='ghi thay đổi (mặc định chỉ báo cáo) / write changes (default: report only)')
    ap.add_argument('--allow-uninitialized', action='store_true', help='cho phép project chưa có .agent/PACKAGE_INFO.json / allow a project without .agent/PACKAGE_INFO.json')
    ap.add_argument('--force', action='store_true', help='cho phép "nâng cấp" xuống bản thấp hơn / allow a downgrade')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    project = os.path.abspath(a.project) if a.project else HERE
    source = os.path.abspath(a.source) if a.source else HERE
    if os.path.normcase(project) == os.path.normcase(source):
        sys.exit('Cần --from (package mới) hoặc --project (project cần nâng cấp) trỏ tới một thư mục khác. / '
                 'Give --from (new package) or --project (project to upgrade) pointing at a different folder.')
    info_p = os.path.join(project, '.agent', 'PACKAGE_INFO.json')
    if not os.path.isfile(info_p) and not a.allow_uninitialized:
        sys.exit(L('%s chưa được khởi tạo (không có .agent/PACKAGE_INFO.json); có thể đây là thư mục nguồn của package, không nên nâng cấp tại chỗ. Chưa ghi gì. '
                   'Nếu chắc đây là project, thêm --allow-uninitialized.',
                   '%s is not initialized (no .agent/PACKAGE_INFO.json); it may be the package source folder, which should not be upgraded in place. Nothing written. '
                   'If you are sure it is a project, add --allow-uninitialized.') % project)
    info = {}
    if os.path.isfile(info_p):
        try:
            with io.open(info_p, encoding='utf-8') as f:
                info = json.load(f)
        except ValueError:
            info = {}
    LANG = info.get('language', 'vi')
    for d, what in ((project, 'project'), (source, 'package')):
        if not os.path.isfile(os.path.join(d, 'VERSION')):
            sys.exit(L('Không thấy VERSION trong %s: %s. Chưa ghi gì. Chọn đúng thư mục có file VERSION (bản đã giải nén đầy đủ).',
                   'No VERSION in the %s folder: %s. Nothing written. Choose the folder that contains the VERSION file (a fully extracted copy).') % (what, d))
    if read_manifest(project) is None:
        sys.exit(L('Project chưa có MANIFEST.sha256 nên không so sánh an toàn được. Chưa ghi gì. Nâng cấp tay theo docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md.',
                   'The project has no MANIFEST.sha256, so a safe comparison is not possible. Nothing written. Upgrade by hand following docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md.'))
    if read_manifest(source) is None:
        sys.exit(L('Package mới không có MANIFEST.sha256. Chưa ghi gì. Dùng thư mục package đầy đủ từ ZIP rồi thử lại.',
                   'The new package has no MANIFEST.sha256. Nothing written. Use a complete package folder from the ZIP and try again.'))
    ov, nv = read_version(project), read_version(source)
    pi = package_identity(project, source, ov, nv)
    if vt(nv) < vt(ov) and not a.force:
        steps = [L('Dùng package có phiên bản bằng hoặc cao hơn project (kiểm lại thư mục --from). Hạ phiên bản không được hỗ trợ; muốn quay lại bản cũ thì khôi phục từ bản sao lưu của project (hướng dẫn nâng cấp, mục 8).',
                   'Use a package whose version is equal to or higher than the project (check the --from folder). Downgrading is not supported; to go back, restore the project from your own backup (upgrade guide, section 8).')]
        LAST_RESULT = make('blocked', code=1, message='Package is older than the project', changes=False, next_actions=steps,
                           from_version=ov, to_version=nv, package_identity=pi)
        sys.exit(L('Package mới (v%s) thấp hơn project (v%s). Chưa ghi gì.', 'The new package (v%s) is older than the project (v%s). Nothing written.') % (nv, ov) + ' ' + steps[0])
    p = plan(project, source, LANG)
    blocks = compat_blocks(project, source, p)
    if blocks:
        for code, detail in blocks:
            print('CHẶN / BLOCKED [%s] %s' % (code, detail))
        steps = block_steps([c for c, _ in blocks])
        for line in steps:
            print('  > ' + line)
        LAST_RESULT = make('blocked', code=1, message='Upgrade blocked: .cvf or package is not compatible', changes=False,
                           findings=[{'severity': 'error', 'message': '%s: %s' % x} for x in blocks],
                           next_actions=steps,
                           from_version=ov, to_version=nv, package_identity=pi)
        sys.exit(L('Chưa ghi gì: nâng cấp bị chặn vì .cvf hoặc package không tương thích (xem các dòng CHẶN ở trên). Project giữ nguyên, không tự chuyển đổi.',
                   'Nothing written: the upgrade is blocked because .cvf or the package is not compatible (see the BLOCKED lines above). The project is unchanged; there is no automatic migration.'))

    print(('[%s] ' % L('BÁO CÁO, chưa ghi gì', 'REPORT ONLY, nothing written') if not a.apply else '') +
          L('Nâng cấp project: v%s -> v%s (ngôn ngữ %s)', 'Upgrading the project: v%s -> v%s (language %s)') % (ov, nv, LANG))
    print(identity_text(pi))
    def show(key, vi, en):
        items = p[key]
        if not items:
            return
        print('\n%s (%d):' % (L(vi, en), len(items)))
        for it in items[:40]:
            print('  - ' + (it[0] if isinstance(it, tuple) else it))
        if len(items) > 40:
            print('  ... +%d' % (len(items) - 40))
    idx_rows = index_rows(project, source, LANG, p)
    # profile: không nằm trong MANIFEST nên không bao giờ bị ghi đè; project chưa có thì bootstrap đúng quy tắc (không suy quyền từ văn xuôi)
    # the profile is not in any MANIFEST so it is never overwritten; a project without one is bootstrapped by rule (never from prose)
    ep.LANG = LANG
    boot = None
    if not os.path.lexists(os.path.join(project, *ep.PROFILE_REL.split('/'))):
        ptxt, _ = ep.read_plain(os.path.join(project, 'PROJECT.md'))
        try:
            boot = ep.bootstrap_plan(ptxt.decode('utf-8')) if ptxt is not None else None
        except UnicodeDecodeError:
            boot = None
    # Profile chưa tạo được (thiếu dòng quyền, nhiều dòng, con trỏ mất profile): nêu bước xử lý cụ thể, không tự đoán quyền.
    # Profile not creatable (no line, several lines, pointer without profile): say what to do, never guess authority.
    boot_steps = ep.next_steps(boot['reasons'][0], project, source) if boot and boot['bytes'] is None else []
    result_files = []
    for key in ('update', 'add', 'user_missing'):
        result_files += [{'path': x[0], 'action': key} for x in p[key]]
    result_files += [{'path': x[0] + '.new', 'action': 'merge'} for x in p['conflict']]
    result_files += [{'path': '.agent/SKILL_INDEX.md', 'action': 'append'} for _ in idx_rows[:1]]
    if boot and boot['bytes'] is not None:
        result_files.append({'path': ep.PROFILE_REL, 'action': 'add'})
    LAST_RESULT = make('preview', message='Upgrade preview', changes=bool(result_files),
                       merge_required=bool(p['conflict']), files=result_files,
                       next_actions=(merge_steps() if p['conflict'] else []) + boot_steps,
                       from_version=ov, to_version=nv, package_identity=pi)
    if idx_rows:
        print('\n%s (%d):' % (L('Thêm vào .agent/SKILL_INDEX.md các dòng skill dùng chung còn thiếu (không sửa dòng đã có)',
                                'Added to .agent/SKILL_INDEX.md: shared-skill rows still missing (existing rows are not touched)'), len(idx_rows)))
        for r in idx_rows:
            print('  - ' + r.split('|')[1].strip())
    if os.path.lexists(os.path.join(project, *ep.PROFILE_REL.split('/'))):
        print('\n' + L('Giữ nguyên %s (đã có; không nằm trong MANIFEST nên không bị ghi đè).', 'Kept %s (already present; not in any MANIFEST so never overwritten).') % ep.PROFILE_REL)
    elif boot and boot['bytes'] is not None:
        print('\n' + L('Tạo %s (owner quyền PROJECT, chưa có grant).', 'Create %s (authority owner PROJECT, no grants).') % ep.PROFILE_REL)
        if boot['reasons']:
            print('  ' + L('CẦN MIGRATION: ', 'MIGRATION REQUIRED: ') + ep.reason_text(boot['reasons'][0]))
    elif boot:
        print('\n' + L('Chưa tạo %s: %s', 'Did not create %s: %s') % (ep.PROFILE_REL, ep.reason_text(boot['reasons'][0])))
        for line in boot_steps:
            print('  > ' + line)
    show('update', 'Cập nhật (bạn chưa sửa, package có bản mới)', 'Updated (untouched by you, newer in the package)')
    show('add', 'Thêm (file mới của package)', 'Added (new in the package)')
    show('user_missing', 'Thêm file mẫu của bạn còn thiếu', 'Added missing starter files of yours')
    show('user_changed', 'Mẫu của file BẠN ĐANG DÙNG có đổi trong package (không tự sửa, trừ dòng skill còn thiếu trong SKILL_INDEX ở trên; xem file mẫu mới trong package và hợp nhất nếu muốn)', 'The starter template of a file YOU OWN changed in the package (not touched, apart from the missing skill rows in SKILL_INDEX listed above; see the new template in the package and merge if you want)')
    show('conflict', 'XUNG ĐỘT: bạn đã sửa và package cũng đổi; lưu bản mới thành <tên>.new để hợp nhất', 'CONFLICT: you edited it and the package changed too; the new version is saved as <name>.new to merge')
    show('kept', 'Giữ nguyên (bạn đã sửa, package không đổi)', 'Kept (you edited it, the package did not change)')
    show('obsolete', 'Không còn trong package mới (giữ nguyên, bạn tự quyết định bỏ)', 'No longer in the new package (kept; you decide whether to drop it)')
    if not any(p[k] for k in ('update', 'add', 'user_missing', 'conflict')) and not (boot and boot['bytes'] is not None):
        print('\n' + L('Không có gì cần cập nhật.', 'Nothing to update.'))

    if a.apply:
        open_tx = tx.incomplete(project)
        if open_tx:
            txid = open_tx[0]['id']
            msg = tx.blocked_message(project)
            LAST_RESULT = make('blocked', code=1, message=msg, changes=False, transaction=txid,
                               next_actions=tx_next_actions(txid), from_version=ov, to_version=nv, package_identity=pi)
            sys.exit(msg)
        missing_src = [s for _, s in p['update'] + p['add'] + p['user_missing'] + p['conflict']
                       if not os.path.isfile(os.path.join(source, *s.split('/')))]
        if missing_src:
            LAST_RESULT = make('blocked', code=1, message='Missing source files', changes=False,
                               files=[{'path': x, 'action': 'missing'} for x in missing_src[:40]],
                               next_actions=['Use a complete package folder, then retry.'], from_version=ov, to_version=nv, package_identity=pi)
            sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: thiếu file trong package / package files missing: %s' % ', '.join(missing_src[:5]))
        for rel, src in p['conflict']:
            pending = os.path.join(project, rel + '.new')
            if os.path.exists(pending):
                conflict_differs = not os.path.isfile(pending)
                if not conflict_differs:
                    with open(pending, 'rb') as f1, open(os.path.join(source, src), 'rb') as f2:
                        conflict_differs = (f1.read() != f2.read())
                if conflict_differs:
                    LAST_RESULT = make('blocked', code=1, message='Pending merge conflict', changes=False,
                                       merge_required=True, files=[{'path': rel + '.new', 'action': 'blocked'}],
                                       next_actions=pending_steps(),
                                       from_version=ov, to_version=nv, package_identity=pi)
                    sys.exit('XUNG ĐỘT / CONFLICT: %s đã có nội dung khác; chưa ghi gì / pending merge differs; nothing written. %s' % (pending, pending_steps()[0]))
        t = tx.Transaction(project, 'upgrade')
        try:
            # expected_before = hash thô của đúng bytes plan() đã dùng để phân loại: file đổi từ lúc đó thì giao dịch từ chối, chưa ghi gì
            # expected_before = raw hash of the exact bytes plan() classified on: a file changed since then is refused and nothing is written
            for rel, src in p['update'] + p['add'] + p['user_missing']:
                t.add(rel, read_bytes(source, src), 'create' if not os.path.exists(os.path.join(project, *rel.split('/'))) else 'write',
                      expected_before=p['snapshot'][rel])
            for rel, src in p['conflict']:
                pending = rel + '.new'
                if not os.path.exists(os.path.join(project, *pending.split('/'))):
                    t.add(pending, read_bytes(source, src), 'create_exclusive')
            if idx_rows:
                dst_i = os.path.join(project, '.agent', 'SKILL_INDEX.md')
                with io.open(dst_i, encoding='utf-8') as f:
                    new_i = render_index_rows(f.read(), idx_rows)
                t.add('.agent/SKILL_INDEX.md', new_i.encode('utf-8'), 'write')
            if boot and boot['bytes'] is not None:
                t.add(ep.PROFILE_REL, boot['bytes'], 'create', expected_before=None)
            t.add('MANIFEST.sha256', read_bytes(source, 'MANIFEST.sha256'), 'write')
            if info:
                info['version'] = nv
                info['upgraded'] = datetime.date.today().isoformat()
                t.add('.agent/PACKAGE_INFO.json', (json.dumps(info, ensure_ascii=False, indent=2) + '\n').encode('utf-8'), 'write')
        except tx.TransactionError as e:
            LAST_RESULT = make('blocked', code=1, message=str(e), changes=False,
                               next_actions=['Save your work and close the file in your editor, then run the preview again (without --apply) and apply again.'],
                               from_version=ov, to_version=nv, package_identity=pi)
            sys.exit(L('CHƯA GHI GÌ: %s. Không file nào bị ghi đè. Nếu file vừa được lưu sau lúc xem trước: lưu xong việc đang làm, chạy lại bản xem trước (không --apply) rồi áp dụng lại.',
                       'NOTHING WRITTEN: %s. No file was overwritten. If a file was saved after the preview: finish saving your work, run the preview again (without --apply) and apply again.') % e)
        TX['id'] = t.txid if t.journal['ops'] else None
        try:
            t.run()
        except tx.TransactionError as e:
            TX['id'] = None
            LAST_RESULT = make('blocked', code=1, message=str(e), changes=False,
                               next_actions=['Fix the problem above, then retry.'], from_version=ov, to_version=nv, package_identity=pi)
            sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: %s' % e)
        print('\n' + L('Đã ghi. MANIFEST.sha256 đã theo bản mới.', 'Written. MANIFEST.sha256 now follows the new version.'))
        if p['conflict']:
            for line in merge_steps():
                print(L('Việc cần làm: ', 'To do: ') + line)
        print(L('Nếu dùng gói lĩnh vực: chạy "python tools/pack.py list" để xem gói nào có bản mới.',
                'If you use domain packs: run "python tools/pack.py list" to see which have a newer version.'))
        LAST_RESULT = make('success', message='Upgrade applied', changes=bool(result_files),
                           merge_required=bool(p['conflict']), files=result_files,
                           next_actions=(merge_steps() if p['conflict'] else []) + boot_steps,
                           from_version=ov, to_version=nv, package_identity=pi, transaction=TX['id'])
    else:
        print('\n' + L('Thêm --apply để thực hiện.', 'Add --apply to carry it out.'))

if __name__ == '__main__':
    try:
        main()
        if RESULT_REQUESTED:
            emit(LAST_RESULT or make('success', message='Upgrade completed', changes=None))
    except SystemExit as e:
        if RESULT_REQUESTED:
            code = e.code if isinstance(e.code, int) else 1
            emit(LAST_RESULT or make('blocked', code=code, message=str(e), changes=False))
        raise
    except OSError as e:
        msg = ('CHƯA HOÀN TẤT / INCOMPLETE: %s. Giao dịch %s còn dở: chạy resume hoặc rollback. / Transaction %s is unfinished: run resume or rollback.'
               % (e, TX['id'], TX['id'])) if TX['id'] else ('CHƯA HOÀN TẤT / INCOMPLETE: %s. / %s' % (e, e))
        if RESULT_REQUESTED:
            emit(make('partial', code=1, message=msg, changes=None, transaction=TX['id'],
                      next_actions=tx_next_actions(TX['id']) if TX['id'] else ['Inspect the project folder before retrying.']))
        sys.exit(msg)
