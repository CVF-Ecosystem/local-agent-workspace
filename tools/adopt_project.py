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
import subprocess
import sys
from result_schema import emit, make
import transaction as tx
import upgrade_package as up

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'dist', '__pycache__', 'roadmap', 'tests', '.github'}
SKIP_PREFIX = ('feedback/records/', tx.RUNTIME_DIR + '/')
TX = {'id': None}  # mã giao dịch đang ghi / transaction id of the current write
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
        with open(path, encoding='utf-8') as f:
            t = f.read()
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

    open_tx = tx.incomplete(proj)
    if open_tx:
        txid = open_tx[0]['id']
        msg = tx.blocked_message(proj)
        LAST_RESULT = make('blocked', code=1, message=msg, changes=False, transaction=txid,
                           next_actions=up.tx_next_actions(txid))
        sys.exit(msg)

    missing_src = [rel for rel in add + new if not os.path.isfile(source(rel))]
    if missing_src:
        LAST_RESULT = make('blocked', code=1, message='Missing source files', changes=False,
                           files=[{'path': x, 'action': 'missing'} for x in missing_src[:40]],
                           next_actions=['Use a complete package folder, then retry.'])
        sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: thiếu file trong package / package files missing: %s' % ', '.join(missing_src[:5]))

    def data_of(rel):
        with open(source(rel), 'rb') as f:
            return f.read()

    t = tx.Transaction(proj, 'adopt')
    for rel in add:
        t.add(rel, data_of(rel), 'create')
    for rel in new:
        if not os.path.exists(os.path.join(proj, rel + '.new')):
            t.add(rel + '.new', data_of(rel), 'create_exclusive')

    # skill riêng sẵn có + dòng skill dùng chung -> một thao tác SKILL_INDEX / own and shared rows -> one SKILL_INDEX op
    idx = os.path.join(proj, '.agent', 'SKILL_INDEX.md')
    own_rows, shared_rows, new_idx = [], [], None
    if os.path.isfile(idx):
        with open(idx, encoding='utf-8') as f:
            text = f.read()
        new_idx = text
        rows = ''
        for d in own:
            if re.search(r'^\|\s*%s\s*\|' % re.escape(d), new_idx, re.M):
                continue
            desc = (frontmatter(os.path.join(pdir, d, 'SKILL.md')).get('description') or d).replace('|', '/')
            if len(desc) > 220:
                desc = desc[:217] + '...'
            rows += '| %s | LOCAL | PROJECT | skills/local/project/%s/SKILL.md | %s | AVAILABLE | Có sẵn trước khi đưa package vào (%s); rà lại mô tả và phần trùng với skill dùng chung. |\n' % (
                d, d, desc, datetime.date.today().isoformat())
        if rows:
            m = re.search(r'\n\n## ', new_idx)
            new_idx = (new_idx[:m.start()].rstrip('\n') + '\n' + rows + new_idx[m.start():]) if m else new_idx.rstrip('\n') + '\n' + rows
            own_rows = rows.splitlines()
        try:
            found = up.index_rows(proj, ROOT, a.lang, {'add': []})
            ids_in = {m.group(1) for m in up.ROW_RE.finditer(new_idx)}
            shared_rows = [r for r in found if r.split('|')[1].strip() not in ids_in]
            if shared_rows:
                new_idx = up.render_index_rows(new_idx, shared_rows)
        except Exception as e:
            shared_rows = []
            print('  Chưa thêm được dòng skill dùng chung vào SKILL_INDEX (%s); chạy upgrade_package.py sau.' % e)
        if new_idx != text:
            t.add('.agent/SKILL_INDEX.md', new_idx.encode('utf-8'), 'write')

    TX['id'] = t.txid if t.journal['ops'] else None
    try:
        t.run()
    except tx.TransactionError as e:
        TX['id'] = None
        LAST_RESULT = make('blocked', code=1, message=str(e), changes=False, merge_required=bool(bak),
                           next_actions=['Fix the problem above, then retry.'])
        sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: %s' % e)
    if own_rows:
        print('  Đã thêm %d dòng skill riêng vào .agent/SKILL_INDEX.md' % len(own_rows))
    if shared_rows:
        print('  Đã thêm %d dòng skill dùng chung vào .agent/SKILL_INDEX.md' % len(shared_rows))

    cmd = [sys.executable, os.path.join(proj, 'tools', 'init_project.py'), '--name', a.name, '--lang', a.lang]
    if partial:
        cmd.append('--force')  # đã có PACKAGE_INFO; init chỉ điền dòng trống, giữ STATE / keeps filled lines and STATE
    if a.purpose:
        cmd += ['--purpose', a.purpose]
    r = subprocess.run(cmd, cwd=proj)
    if r.returncode:
        rerun = 'python tools/init_project.py --name "%s" --lang %s --force' % (a.name, a.lang)
        LAST_RESULT = make('partial', code=1, message='Package files written; init_project.py failed (exit %d).' % r.returncode,
                           changes=bool(planned), merge_required=bool(bak), files=planned, transaction=TX['id'],
                           next_actions=['Read the init_project.py messages above; if it left a transaction, run its resume or rollback.',
                                         'Then run: ' + rerun] + (['Merge the .new instruction files.'] if bak else []))
        sys.exit('CHƯA HOÀN TẤT / INCOMPLETE: init_project.py lỗi; xem thông báo ở trên. / init_project.py failed; see the messages above.')
    print('\n' + ('Đã đưa package vào; CẦN HỢP NHẤT hướng dẫn .new / Package added; MERGE REQUIRED.' if bak else 'Đã đưa package vào / Package added.'))
    print('Việc tiếp theo: (1) hợp nhất bản .new nếu có; (2) điền .agent/INDEX.md trỏ tới nguồn sẵn có; '
          '(3) chạy python tools/check_package.py --verify trong project.')
    LAST_RESULT = make('success', message='Package adopted', changes=bool(planned),
                       merge_required=bool(bak), files=planned,
                       next_actions=(['Merge the .new instruction files.'] if bak else []),
                       transaction=TX['id'])


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
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
        if TX['id']:
            msg = ('CHƯA HOÀN TẤT / INCOMPLETE: %s. Giao dịch %s còn dở: chạy resume hoặc rollback. / Transaction %s is unfinished: run resume or rollback.'
                   % (e, TX['id'], TX['id']))
        else:
            msg = 'LỖI / ERROR: %s. Chưa ghi file nào / No file was written.' % e
        if RESULT_REQUESTED:
            emit(make('partial' if TX['id'] else 'error', code=1, message=msg, changes=None, transaction=TX['id'],
                      next_actions=up.tx_next_actions(TX['id']) if TX['id'] else ['Check the project folder, then retry.']))
        sys.exit(msg)
