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
import check_package as cp
import execution_profile as ep
import transaction as tx
import upgrade_package as up

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TX = {'id': None}  # mã giao dịch đang ghi / transaction id of the current write
USER_KEEP = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md', '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md', ep.PROFILE_REL}
ADAPTERS = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md')
ROW_HEAD = '| Skill ID | Origin | Scope |'
RESULT_REQUESTED = '--result-json' in sys.argv
LAST_RESULT = None


def same(path, data):
    """File ở path có đúng bytes data không. / Whether the file at path holds exactly these bytes."""
    with open(path, 'rb') as f:
        return f.read() == data


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
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
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

    # Nguồn giao và đích được kiểm CHỈ BẰNG ĐỌC trước mọi mutation (Transaction, probe, .new, backup, thư mục); chặn cả khi --apply.
    # Source and target are checked read-only before any mutation (transaction, probe, .new, backup, folder); blocked even with --apply.
    problems = [('SOURCE', x) for x in cp.delivery_problems()]
    if problems:
        LAST_RESULT = make('blocked', code=1, message='Source is not deliverable', changes=False,
                           findings=[{'severity': 'error', 'message': m} for _, m in problems],
                           next_actions=['Use the original template folder (unzipped release) or the clean source tree, then retry.'])
        sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: nguồn giao không hợp lệ / source cannot be delivered: ' + problems[0][1])
    selection = cp.delivery_selection()
    pkg_rels = selection + ['MANIFEST.sha256']
    brand = set(cp.branding_files()) | {'assets/branding.js'}
    cache = {}

    def data_of(rel):
        """Bytes sẽ giao của rel (cùng projection với build/new); bản en/ cho hướng dẫn agent khi --lang en. / the shipped bytes of rel."""
        key = ('en/' + rel) if (a.lang == 'en' and rel in ADAPTERS) else rel
        if key not in cache:
            cache[key] = cp.delivery_manifest(selection) if key == 'MANIFEST.sha256' else cp.delivery_bytes(key)
        return cache[key]

    add, skip, bak, new = [], [], [], []
    for rel in pkg_rels:
        d = os.path.join(proj, rel)
        if rel == ep.PROFILE_REL:
            # profile của project: có rồi thì giữ nguyên byte, không .new; chưa có thì mẫu sạch CHỈ đi cùng PROJECT.md mẫu (con trỏ);
            # nếu không init_project.py bootstrap theo PROJECT.md hiện có (không suy quyền từ văn xuôi)
            # an existing profile is kept byte for byte, no .new; a clean one is added only together with the template PROJECT.md (pointer);
            # otherwise init_project.py bootstraps from the existing PROJECT.md (never from prose)
            if os.path.lexists(d):
                skip.append(rel)
            elif not os.path.lexists(os.path.join(proj, 'PROJECT.md')):
                add.append(rel)
            continue
        if not os.path.exists(d):
            add.append(rel)
        elif same(d, data_of(rel)):
            skip.append(rel)
        elif rel in ADAPTERS:
            bak.append(rel)
            new.append(rel)
        elif rel in USER_KEEP or rel in brand:
            skip.append(rel)  # file của người dùng (kể cả nhận diện đơn vị): giữ nguyên, không tạo .new / user-owned (incl. branding): kept, no .new
        else:
            new.append(rel)

    # runtime .cvf: đích không có thì thêm candidate; đích có chỉ khi đúng closure v3 cùng byte máy đọc và không xung đột (không .new rồi coi là coherent)
    cvf_block = [('TARGET_' + code, msg) for code, msg in cp.cvf_target_problems(proj, lambda r: data_of(r))]
    cvf_block += [('DEPENDENCY_CONFLICT', r) for r in new if r in cp.CVF_DEPENDENCIES]
    cvf_block += [('CVF_USER_EDIT_CONFLICT', r) for r in new if r.startswith(cp.CVF_DIR + '/')]
    for rel in ('tools/init_project.py', 'tools/check_package.py', 'tools/transaction.py', 'tools/result_schema.py', 'tools/execution_profile.py'):
        target_code = os.path.join(proj, *rel.split('/'))
        if os.path.lexists(target_code) and (cp._is_link(target_code) or not os.path.isfile(target_code) or not same(target_code, data_of(rel))):
            cvf_block.append(('BOOTSTRAP_CODE_DIFFERS', rel))
    if cvf_block:
        LAST_RESULT = make('blocked', code=1, message='Existing .cvf or owner files are not compatible with the v3 candidate', changes=False,
                           findings=[{'severity': 'error', 'message': '%s: %s' % x} for x in cvf_block],
                           next_actions=['Leave the project as is; no automatic migration. Move the conflicting .cvf or owner files yourself, then retry.'])
        sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: .cvf hoặc file owner của project không tương thích candidate v3 / incompatible: ' +
                 '; '.join('%s %s' % x for x in cvf_block[:3]))

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
        if os.path.exists(candidate) and (not os.path.isfile(candidate) or not same(candidate, data_of(rel))):
            blocked.append(rel + '.new')
    for d in own:
        print('  Skill riêng sẵn có: skills/local/project/%s (sẽ thêm vào SKILL_INDEX nếu chưa có)' % d)
    if bak:
        print('\nCẦN HỢP NHẤT / MERGE REQUIRED: %s. Hướng dẫn cũ vẫn được giữ và có hiệu lực; '
              'xem bản .new và hợp nhất trước khi dùng hướng dẫn mới. / Existing instructions remain active; merge .new before switching.' % ', '.join(bak))
    if blocked:
        LAST_RESULT = make('blocked', code=1, message='Pending merge conflict', changes=False,
                           merge_required=True, files=[{'path': x, 'action': 'blocked'} for x in blocked],
                           next_actions=['Compare the existing .new with the current file and follow the upgrade guide for that file owner. Preserve both copies for comparison and recovery; do not delete the .new merely to clear the warning.'])
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
            # công cụ chỉ ghi nhận skill có sẵn, không tự tiếp nhận: REVIEW cho tới khi người dùng xác nhận (skills/README.md)
            # the tool only records an existing skill, never accepts it: REVIEW until the user confirms (skills/README.md)
            rows += '| %s | LOCAL | PROJECT | skills/local/project/%s/SKILL.md | %s | REVIEW | Có sẵn trước khi đưa package vào (%s); rà mô tả, phần trùng với skill dùng chung hoặc native, rồi đổi sang AVAILABLE khi người dùng xác nhận. |\n' % (
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
