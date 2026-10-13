#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đưa package vào một project ĐÃ CÓ lần đầu (chưa có VERSION / .agent). / Adopt the package into an EXISTING project (first time).

Chạy từ thư mục package, chỉ tới project cũ. Mặc định chỉ BÁO CÁO; thêm --apply mới ghi.
Run from the package folder, point to the old project. Report only by default; --apply writes.

  python tools/adopt_project.py --project "D:\\cac-project\\ten-project" --name "Tên project" [--lang vi|en]
  python tools/adopt_project.py --project "D:\\cac-project\\ten-project" --name "Tên project" --apply

Quy tắc (không xóa, không ghi đè file của bạn / never deletes, never overwrites your files):
  - file package chưa có trong project              -> thêm;
  - file đã có và giống hệt                          -> bỏ qua;
  - AGENTS.md, CLAUDE.md, GEMINI.md đã có, khác bản package
                                                     -> giữ nguyên; bản package lưu thành <tên>.new để hợp nhất;
  - file khác đã có và khác bản package               -> giữ của bạn, bản package lưu thành <tên>.new;
  - skill riêng sẵn có trong skills/local/project/    -> thêm dòng vào .agent/SKILL_INDEX.md (nếu chưa có), không sửa skill;
  - cuối cùng chạy init_project.py (điền tên, ghi PACKAGE_INFO.json).
Không dùng mạng. Python 3.8+.
"""
import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from result_schema import emit, make

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'dist', '__pycache__', 'roadmap', 'tests', '.github'}
SKIP_PREFIX = ('feedback/records/',)
SKIP_FILES = {'.agent/PACKAGE_INFO.json', '.agent/MERGE_STATUS.json', 'setup_answers.json'}
USER_KEEP = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md', '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md'}
ADAPTERS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md')
ROW_HEAD = '| Skill ID | Origin | Scope |'
RESULT_REQUESTED = '--result-json' in sys.argv
LAST_RESULT = None


def package_files():
    out = []
    for r, ds, fs in os.walk(ROOT):
        ds[:] = [d for d in ds if d not in SKIP_DIRS]
        for n in fs:
            rel = os.path.relpath(os.path.join(r, n), ROOT).replace(os.sep, '/')
            if rel.startswith(SKIP_PREFIX) or rel in SKIP_FILES or n.endswith(('.pyc', '.bak')) or '.bak-' in n:
                continue
            out.append(rel)
    return sorted(out)


def same(a, b):
    with open(a, 'rb') as x, open(b, 'rb') as y:
        return x.read() == y.read()


def frontmatter(path):
    try:
        t = open(path, encoding='utf-8').read()
    except OSError:
        return {}
    m = re.match(r'---\r?\n(.*?)\r?\n---', t, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(':')
            if v and not line.startswith(' '):
                fm[k.strip()] = v.strip().strip('"\'')
    return fm


def main():
    global LAST_RESULT
    ap = argparse.ArgumentParser(description='Đưa package vào project đã có / adopt the package into an existing project')
    ap.add_argument('--project', required=True, help='thư mục project cũ / the existing project folder')
    ap.add_argument('--name', required=True, help='tên project / project name')
    ap.add_argument('--lang', choices=('vi', 'en'), default='vi')
    ap.add_argument('--purpose', default='', help='điền dòng "Mục đích và người đọc" trong PROJECT.md')
    ap.add_argument('--apply', action='store_true', help='ghi thay đổi (mặc định chỉ báo cáo)')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    if not os.path.isdir(proj):
        sys.exit('Không thấy thư mục project: %s' % proj)
    if os.path.samefile(proj, ROOT):
        sys.exit('Project trùng thư mục package; chọn project cần đưa package vào.')
    # Project dựng tay từ bản cũ: có .agent/PACKAGE_INFO.json nhưng không có VERSION, MANIFEST, tools/ -> upgrade_package.py
    # không chạy được (cần VERSION), nên coi như đưa package vào lần đầu. / A hand-built project with PACKAGE_INFO but no VERSION.
    partial = (os.path.isfile(os.path.join(proj, '.agent', 'PACKAGE_INFO.json'))
               and not os.path.isfile(os.path.join(proj, 'VERSION')) and not os.path.isfile(os.path.join(proj, 'MANIFEST.sha256')))
    if os.path.isfile(os.path.join(proj, 'VERSION')) or (os.path.isfile(os.path.join(proj, '.agent', 'PACKAGE_INFO.json')) and not partial):
        sys.exit('Project này đã có package (VERSION hoặc .agent/PACKAGE_INFO.json). Dùng tools/upgrade_package.py để nâng cấp.')
    if partial:
        print('Project có .agent/PACKAGE_INFO.json nhưng chưa có VERSION, MANIFEST: đưa package vào như lần đầu; PACKAGE_INFO sẽ được ghi lại.')

    add, skip, bak, new = [], [], [], []
    def source(rel):
        overlay = os.path.join(ROOT, 'en', rel)
        if a.lang == 'en' and rel in ADAPTERS and os.path.isfile(overlay):
            return overlay
        return os.path.join(ROOT, rel)

    for rel in package_files():
        s, d = source(rel), os.path.join(proj, rel)
        if not os.path.exists(d):
            add.append(rel)
        elif same(s, d):
            skip.append(rel)
        elif rel in ADAPTERS:
            bak.append(rel)
            new.append(rel)
        elif rel in USER_KEEP:
            skip.append(rel)  # file của người dùng: giữ nguyên, không tạo .new / user-owned: kept, no .new
        else:
            new.append(rel)

    pdir = os.path.join(proj, 'skills', 'local', 'project')
    own = []
    if os.path.isdir(pdir):
        own = sorted(d for d in os.listdir(pdir) if os.path.isfile(os.path.join(pdir, d, 'SKILL.md')))

    with open(os.path.join(ROOT, 'VERSION'), encoding='utf-8') as version_file:
        version = version_file.read().strip()
    print('[%s] Đưa package v%s vào project: %s' % ('GHI' if a.apply else 'BÁO CÁO, chưa ghi gì', version, proj))
    print('  Thêm %d file; bỏ qua (giống hệt hoặc file của bạn) %d.' % (len(add), len(skip)))
    blocked = []
    for rel in new:
        print('  GIỮ của bạn, bản package lưu thành %s.new: %s' % (rel, rel))
        candidate = os.path.join(proj, rel + '.new')
        if os.path.exists(candidate) and (not os.path.isfile(candidate) or not same(source(rel), candidate)):
            blocked.append(rel + '.new')
    for d in own:
        print('  Skill riêng sẵn có: skills/local/project/%s (sẽ thêm vào SKILL_INDEX nếu chưa có)' % d)
    if bak:
        print('\nCẦN HỢP NHẤT / MERGE REQUIRED: %s. Hướng dẫn cũ vẫn được giữ và có hiệu lực; '
              'xem bản .new và hợp nhất trước khi dùng hướng dẫn mới. / Existing instructions remain active; merge .new before switching.' % ', '.join(bak))
    if blocked:
        LAST_RESULT = make('blocked', code=1, message='Pending merge conflict', changes=False,
                           merge_required=True, files=[{'path': x, 'action': 'blocked'} for x in blocked],
                           next_actions=['Resolve or remove the existing .new file, then retry.'])
        sys.exit('XUNG ĐỘT / CONFLICT: bản chờ hợp nhất đã có nội dung khác; chưa ghi file nào / nothing written: ' + ', '.join(blocked))
    planned = ([{'path': x, 'action': 'add'} for x in add] +
               [{'path': x + '.new', 'action': 'merge'} for x in new])
    LAST_RESULT = make('preview', message='Adoption preview', changes=bool(planned),
                       merge_required=bool(bak), files=planned,
                       next_actions=(['Merge the .new instruction files.'] if bak else []))
    if not a.apply:
        print('\nThêm --apply để thực hiện.')
        return

    for rel in add:
        d = os.path.join(proj, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(source(rel), d)
    for rel in new:
        candidate = os.path.join(proj, rel + '.new')
        if not os.path.exists(candidate):
            with open(source(rel), 'rb') as src, open(candidate, 'xb') as dst:
                shutil.copyfileobj(src, dst)

    # skill riêng sẵn có -> SKILL_INDEX
    idx = os.path.join(proj, '.agent', 'SKILL_INDEX.md')
    if own and os.path.isfile(idx):
        t = open(idx, encoding='utf-8').read()
        rows = ''
        for d in own:
            if re.search(r'^\|\s*%s\s*\|' % re.escape(d), t, re.M):
                continue
            desc = (frontmatter(os.path.join(pdir, d, 'SKILL.md')).get('description') or d).replace('|', '/')
            if len(desc) > 220:
                desc = desc[:217] + '...'
            rows += '| %s | LOCAL | PROJECT | skills/local/project/%s/SKILL.md | %s | AVAILABLE | Có sẵn trước khi đưa package vào (%s); rà lại mô tả và phần trùng với skill dùng chung. |\n' % (
                d, d, desc, datetime.date.today().isoformat())
        if rows:
            m = re.search(r'\n\n## ', t)
            t = (t[:m.start()].rstrip('\n') + '\n' + rows + t[m.start():]) if m else t.rstrip('\n') + '\n' + rows
            open(idx, 'w', encoding='utf-8').write(t)
            print('  Đã thêm %d dòng skill riêng vào .agent/SKILL_INDEX.md' % rows.count('\n'))

    # dòng skill dùng chung còn thiếu trong SKILL_INDEX của project / shared-skill rows missing from the project index
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import upgrade_package as up
        rows = up.index_rows(proj, ROOT, a.lang, {'add': []})
        if rows:
            up.write_index_rows(proj, rows)
            print('  Đã thêm %d dòng skill dùng chung vào .agent/SKILL_INDEX.md' % len(rows))
    except Exception as e:
        print('  Chưa thêm được dòng skill dùng chung vào SKILL_INDEX (%s); chạy upgrade_package.py sau.' % e)

    cmd = [sys.executable, os.path.join(proj, 'tools', 'init_project.py'), '--name', a.name, '--lang', a.lang]
    if partial:
        cmd.append('--force')  # đã có PACKAGE_INFO; init chỉ điền dòng trống, giữ STATE / keeps filled lines and STATE
    if a.purpose:
        cmd += ['--purpose', a.purpose]
    r = subprocess.run(cmd, cwd=proj)
    if r.returncode:
        sys.exit('init_project.py lỗi; xem thông báo ở trên.')
    print('\n' + ('Đã đưa package vào; CẦN HỢP NHẤT hướng dẫn .new / Package added; MERGE REQUIRED.' if bak else 'Đã đưa package vào / Package added.'))
    print('Việc tiếp theo: (1) hợp nhất bản .new nếu có; (2) điền .agent/INDEX.md trỏ tới nguồn sẵn có; '
          '(3) chạy python tools/check_package.py --verify trong project.')
    LAST_RESULT = make('success', message='Package adopted', changes=bool(planned),
                       merge_required=bool(bak), files=planned,
                       next_actions=(['Merge the .new instruction files.'] if bak else []))


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
        if RESULT_REQUESTED:
            emit(LAST_RESULT or make('success', message='Package adopted', changes=None))
    except SystemExit as e:
        if RESULT_REQUESTED:
            code = e.code if isinstance(e.code, int) else 1
            emit(LAST_RESULT or make('blocked', code=code, message=str(e), changes=False))
        raise
    except OSError as e:
        if RESULT_REQUESTED:
            emit(make('partial', code=1, message=str(e), changes=None,
                      next_actions=['Inspect files already added before retrying.']))
        sys.exit('CHƯA HOÀN TẤT / INCOMPLETE: %s. Có thể đã thêm một số file; chưa tự hoàn tác. / Some files may have been added; no automatic rollback.' % e)
