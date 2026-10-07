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
                                                     -> lưu bản cũ thành <tên>.bak-<ngày>, dùng bản package.
                                                        PHẢI hợp nhất phần riêng của bản cũ vào PROJECT.md (script nhắc);
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'dist', '__pycache__'}
SKIP_PREFIX = ('feedback/records/',)
SKIP_FILES = {'.agent/PACKAGE_INFO.json', 'setup_answers.json'}
ADAPTERS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md')
ROW_HEAD = '| Skill ID | Origin | Scope |'


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
    ap = argparse.ArgumentParser(description='Đưa package vào project đã có / adopt the package into an existing project')
    ap.add_argument('--project', required=True, help='thư mục project cũ / the existing project folder')
    ap.add_argument('--name', required=True, help='tên project / project name')
    ap.add_argument('--lang', choices=('vi', 'en'), default='vi')
    ap.add_argument('--purpose', default='', help='điền dòng "Mục đích và người đọc" trong PROJECT.md')
    ap.add_argument('--apply', action='store_true', help='ghi thay đổi (mặc định chỉ báo cáo)')
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    if not os.path.isdir(proj):
        sys.exit('Không thấy thư mục project: %s' % proj)
    if os.path.samefile(proj, ROOT):
        sys.exit('Project trùng thư mục package; chọn project cần đưa package vào.')
    if os.path.isfile(os.path.join(proj, 'VERSION')) or os.path.isfile(os.path.join(proj, '.agent', 'PACKAGE_INFO.json')):
        sys.exit('Project này đã có package (VERSION hoặc .agent/PACKAGE_INFO.json). Dùng tools/upgrade_package.py để nâng cấp.')

    today = datetime.date.today().strftime('%Y%m%d')
    add, skip, bak, new = [], [], [], []
    for rel in package_files():
        s, d = os.path.join(ROOT, rel), os.path.join(proj, rel)
        if not os.path.exists(d):
            add.append(rel)
        elif same(s, d):
            skip.append(rel)
        elif rel in ADAPTERS:
            bak.append(rel)
        else:
            new.append(rel)

    pdir = os.path.join(proj, 'skills', 'local', 'project')
    own = []
    if os.path.isdir(pdir):
        own = sorted(d for d in os.listdir(pdir) if os.path.isfile(os.path.join(pdir, d, 'SKILL.md')))

    print('[%s] Đưa package v%s vào project: %s' % ('GHI' if a.apply else 'BÁO CÁO, chưa ghi gì', open(os.path.join(ROOT, 'VERSION')).read().strip(), proj))
    print('  Thêm %d file; giống hệt (bỏ qua) %d.' % (len(add), len(skip)))
    for rel in bak:
        print('  THAY (lưu bản cũ thành %s.bak-%s): %s' % (rel, today, rel))
    for rel in new:
        print('  GIỮ của bạn, bản package lưu thành %s.new: %s' % (rel, rel))
    for d in own:
        print('  Skill riêng sẵn có: skills/local/project/%s (sẽ thêm vào SKILL_INDEX nếu chưa có)' % d)
    if bak:
        print('\nLƯU Ý: %s là hướng dẫn riêng của project cũ. Sau khi ghi, hợp nhất phần riêng của bản .bak vào PROJECT.md '
              '(không nhân bản nội dung chung đã có trong AGENTS.md).' % ', '.join(bak))
    if not a.apply:
        print('\nThêm --apply để thực hiện.')
        return

    for rel in bak:
        shutil.copy2(os.path.join(proj, rel), os.path.join(proj, rel + '.bak-' + today))
    for rel in add + bak:
        d = os.path.join(proj, rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel), d)
    for rel in new:
        shutil.copy2(os.path.join(ROOT, rel), os.path.join(proj, rel + '.new'))

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

    cmd = [sys.executable, os.path.join(proj, 'tools', 'init_project.py'), '--name', a.name, '--lang', a.lang]
    if a.purpose:
        cmd += ['--purpose', a.purpose]
    r = subprocess.run(cmd, cwd=proj)
    if r.returncode:
        sys.exit('init_project.py lỗi; xem thông báo ở trên.')
    print('\nXong. Việc tiếp theo: (1) hợp nhất bản .bak vào PROJECT.md nếu có; (2) điền .agent/INDEX.md trỏ tới nguồn sẵn có; '
          '(3) chạy python tools/check_package.py --verify trong project.')


if __name__ == '__main__':
    main()
