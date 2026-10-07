#!/usr/bin/env python3
"""Nâng cấp một project lên bản package mới mà không ghi đè việc của bạn.
Upgrade a project to a newer package version without overwriting your work.

Cách dùng / Usage (mặc định chỉ BÁO CÁO, thêm --apply mới ghi / report only by default, --apply writes):
  # chạy từ project, chỉ tới thư mục package mới đã giải nén
  python tools/upgrade_package.py --from "D:\\goi-moi\\local-agent-workspace-v1.4.0"
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

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_EXT = ('.md', '.html', '.py', '.json', '.txt', '.sha256', '.css', '.js', '')
USER_FILES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
              '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md', '.agent/PACKAGE_INFO.json', 'setup_answers.json'}
OVERLAY_SKIP = {'en/PROJECT_INSTRUCTIONS_SNIPPET.md'}
LANG = 'vi'

def L(vi, en): return en if LANG == 'en' else vi

def sha(base, rel):
    data = open(os.path.join(base, *rel.split('/')), 'rb').read()
    if os.path.splitext(rel)[1] in TEXT_EXT:
        data = data.replace(b'\r\n', b'\n')
    return hashlib.sha256(data).hexdigest()

def read_manifest(base):
    p = os.path.join(base, 'MANIFEST.sha256')
    if not os.path.isfile(p):
        return None
    m = {}
    for l in io.open(p, encoding='utf-8').read().splitlines():
        if l.strip():
            h, r = l.split('  ', 1)
            m[r] = h
    return m

def read_version(base):
    try:
        return io.open(os.path.join(base, 'VERSION'), encoding='utf-8').read().strip()
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
                out['user_missing'].append((rel, src_rel))
            else:
                old_src = ('en/' + rel) if use_overlay(rel, old) else rel
                if old.get(old_src) not in (None, new_h):
                    out['user_changed'].append(rel)
            continue
        if not exists:
            out['add'].append((rel, src_rel)); continue
        cur_h = sha(project, rel)
        if cur_h == new_h:
            continue
        old_src = ('en/' + rel) if use_overlay(rel, old) else rel
        old_h = old.get(old_src)
        if old_h is not None and cur_h == old_h:
            out['update'].append((rel, src_rel))
        elif old_h is not None and old_h == new_h:
            out['kept'].append(rel)
        else:
            out['conflict'].append((rel, src_rel))
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
    have = {m.group(1) for m in ROW_RE.finditer(io.open(dst_i, encoding='utf-8').read())}
    adding = {rel for rel, _ in plan_['add']}
    out = []
    for m in ROW_RE.finditer(io.open(src_i, encoding='utf-8').read()):
        if m.group(1) in have:
            continue
        loc = m.group(2)
        if os.path.isfile(os.path.join(project, *loc.split('/'))) or loc in adding:
            out.append(m.group(0))
    return out

def write_index_rows(project, rows):
    dst_i = os.path.join(project, '.agent', 'SKILL_INDEX.md')
    txt = io.open(dst_i, encoding='utf-8').read()
    last = None
    for m in re.finditer(r'^\| [a-z0-9-]+ \| [A-Z]+ \| [A-Z]+ \|.*\n?', txt, re.M):
        last = m
    ins = ''.join(r + '\n' for r in rows)
    if last is None:
        txt = txt.rstrip('\n') + '\n' + ins
    else:
        end = last.end()
        if not txt[end - 1:end] == '\n':
            txt = txt[:end] + '\n' + txt[end:]; end += 1
        txt = txt[:end] + ins + txt[end:]
    io.open(dst_i, 'w', encoding='utf-8', newline='').write(txt)

def copy(source, src_rel, project, dst_rel, suffix=''):
    dst = os.path.join(project, *dst_rel.split('/')) + suffix
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(os.path.join(source, *src_rel.split('/')), dst)

def main():
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--from', dest='source', help='thư mục package MỚI / the NEW package folder')
    ap.add_argument('--project', help='thư mục project cần nâng cấp / the project folder to upgrade')
    ap.add_argument('--apply', action='store_true', help='ghi thay đổi (mặc định chỉ báo cáo) / write changes (default: report only)')
    ap.add_argument('--allow-uninitialized', action='store_true', help='cho phép project chưa có .agent/PACKAGE_INFO.json / allow a project without .agent/PACKAGE_INFO.json')
    ap.add_argument('--force', action='store_true', help='cho phép "nâng cấp" xuống bản thấp hơn / allow a downgrade')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    project = os.path.abspath(a.project) if a.project else HERE
    source = os.path.abspath(a.source) if a.source else HERE
    if os.path.normcase(project) == os.path.normcase(source):
        sys.exit('Cần --from (package mới) hoặc --project (project cần nâng cấp) trỏ tới một thư mục khác. / '
                 'Give --from (new package) or --project (project to upgrade) pointing at a different folder.')
    info_p = os.path.join(project, '.agent', 'PACKAGE_INFO.json')
    if not os.path.isfile(info_p) and not a.allow_uninitialized:
        sys.exit(L('%s chưa được khởi tạo (không có .agent/PACKAGE_INFO.json); có thể đây là thư mục nguồn của package, không nên nâng cấp tại chỗ. '
                   'Nếu chắc đây là project, thêm --allow-uninitialized.',
                   '%s is not initialized (no .agent/PACKAGE_INFO.json); it may be the package source folder, which should not be upgraded in place. '
                   'If you are sure it is a project, add --allow-uninitialized.') % project)
    info = {}
    if os.path.isfile(info_p):
        try:
            info = json.load(io.open(info_p, encoding='utf-8'))
        except ValueError:
            info = {}
    LANG = info.get('language', 'vi')
    for d, what in ((project, 'project'), (source, 'package')):
        if not os.path.isfile(os.path.join(d, 'VERSION')):
            sys.exit(L('Không thấy VERSION trong %s: %s', 'No VERSION in the %s folder: %s') % (what, d))
    if read_manifest(project) is None:
        sys.exit(L('Project chưa có MANIFEST.sha256 nên không so sánh an toàn được. Nâng cấp tay theo docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md.',
                   'The project has no MANIFEST.sha256, so a safe comparison is not possible. Upgrade by hand following docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md.'))
    if read_manifest(source) is None:
        sys.exit(L('Package mới không có MANIFEST.sha256.', 'The new package has no MANIFEST.sha256.'))
    ov, nv = read_version(project), read_version(source)
    if vt(nv) < vt(ov) and not a.force:
        sys.exit(L('Package mới (v%s) thấp hơn project (v%s). Thêm --force nếu thật sự muốn.', 'The new package (v%s) is older than the project (v%s). Add --force if you really mean it.') % (nv, ov))
    p = plan(project, source, LANG)

    print(('[%s] ' % L('BÁO CÁO, chưa ghi gì', 'REPORT ONLY, nothing written') if not a.apply else '') +
          L('Nâng cấp project: v%s -> v%s (ngôn ngữ %s)', 'Upgrading the project: v%s -> v%s (language %s)') % (ov, nv, LANG))
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
    if idx_rows:
        print('\n%s (%d):' % (L('Thêm vào .agent/SKILL_INDEX.md các dòng skill dùng chung còn thiếu (không sửa dòng đã có)',
                                'Added to .agent/SKILL_INDEX.md: shared-skill rows still missing (existing rows are not touched)'), len(idx_rows)))
        for r in idx_rows:
            print('  - ' + r.split('|')[1].strip())
    show('update', 'Cập nhật (bạn chưa sửa, package có bản mới)', 'Updated (untouched by you, newer in the package)')
    show('add', 'Thêm (file mới của package)', 'Added (new in the package)')
    show('user_missing', 'Thêm file mẫu của bạn còn thiếu', 'Added missing starter files of yours')
    show('user_changed', 'Mẫu của file BẠN ĐANG DÙNG có đổi trong package (không tự sửa, trừ dòng skill còn thiếu trong SKILL_INDEX ở trên; xem file mẫu mới trong package và hợp nhất nếu muốn)', 'The starter template of a file YOU OWN changed in the package (not touched, apart from the missing skill rows in SKILL_INDEX listed above; see the new template in the package and merge if you want)')
    show('conflict', 'XUNG ĐỘT: bạn đã sửa và package cũng đổi; lưu bản mới thành <tên>.new để hợp nhất', 'CONFLICT: you edited it and the package changed too; the new version is saved as <name>.new to merge')
    show('kept', 'Giữ nguyên (bạn đã sửa, package không đổi)', 'Kept (you edited it, the package did not change)')
    show('obsolete', 'Không còn trong package mới (giữ nguyên, bạn tự quyết định bỏ)', 'No longer in the new package (kept; you decide whether to drop it)')
    if not any(p[k] for k in ('update', 'add', 'user_missing', 'conflict')):
        print('\n' + L('Không có gì cần cập nhật.', 'Nothing to update.'))

    if a.apply:
        for rel, src in p['update'] + p['add'] + p['user_missing']:
            copy(source, src, project, rel)
        for rel, src in p['conflict']:
            copy(source, src, project, rel, '.new')
        if idx_rows:
            write_index_rows(project, idx_rows)
        shutil.copyfile(os.path.join(source, 'MANIFEST.sha256'), os.path.join(project, 'MANIFEST.sha256'))
        if info:
            info['version'] = nv
            info['upgraded'] = datetime.date.today().isoformat()
            io.open(info_p, 'w', encoding='utf-8', newline='').write(json.dumps(info, ensure_ascii=False, indent=2) + '\n')
        print('\n' + L('Đã ghi. MANIFEST.sha256 đã theo bản mới.', 'Written. MANIFEST.sha256 now follows the new version.'))
        if p['conflict']:
            print(L('Việc cần làm: mở từng file có <tên>.new, hợp nhất phần bạn muốn giữ, rồi xóa file .new.',
                    'To do: open each file that has a <name>.new, merge what you want to keep, then delete the .new file.'))
        print(L('Nếu dùng gói lĩnh vực: chạy "python tools/pack.py list" để xem gói nào có bản mới.',
                'If you use domain packs: run "python tools/pack.py list" to see which have a newer version.'))
    else:
        print('\n' + L('Thêm --apply để thực hiện.', 'Add --apply to carry it out.'))

if __name__ == '__main__':
    main()
