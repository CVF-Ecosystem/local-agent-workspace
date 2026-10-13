#!/usr/bin/env python3
"""Cài (sao chép) các skill của package vào thư mục skill của ứng dụng để chúng hiện trong menu native. TÙY CHỌN.
Optionally copy the package's skills into an app's skills folder so they show up in its native menu.

Mặc định chỉ BÁO CÁO việc sẽ làm; thêm --yes mới sao chép. Không xóa, không ghi đè (trừ khi có --overwrite).
Report-only by default; add --yes to copy. Nothing is deleted or overwritten unless --overwrite is given.

Dùng / Usage:
  python tools/install_skills.py --dest "%USERPROFILE%\\.claude\\skills"            # xem trước / preview
  python tools/install_skills.py --dest ~/.claude/skills --yes                        # sao chép / copy
  python tools/install_skills.py --dest <thư mục skill của ứng dụng> --skills meeting-minutes,data-charts --yes
  python tools/install_skills.py --dest <...> --include-packs --yes                   # kèm skill của gói đã cài

Không có --dest thì dùng ~/.claude/skills (Claude). Codex và Gemini CLI cùng đọc ~/.agents/skills (theo tài liệu của hai ứng dụng,
kiểm tháng 10/2026). Ứng dụng khác: chỉ --dest tới thư mục skill theo tài liệu của nó. Package không tự đổi cấu hình toàn cục. Cần Python 3.8+, không dùng mạng.
"""
import argparse, io, json, os, shutil, sys, traceback
from result_schema import emit, make

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = 'vi'
def L(vi, en): return en if LANG == 'en' else vi
RESULT_REQUESTED = '--result-json' in sys.argv  # cờ ẩn: phát một kết quả có cấu trúc / hidden flag: emit one structured result
LAST_RESULT = None
DONE = []  # file đã ghi trong lượt này / files written in this run, for partial results

def set_result(status, code, message, **kw):
    global LAST_RESULT
    LAST_RESULT = make(status, code=code, message=message, **kw)

def stop(msg, status='blocked', **kw):
    """Như sys.exit(msg) (mã 1), nhưng ghi kết quả có cấu trúc trước / Like sys.exit(msg) (code 1), recording the structured result first."""
    set_result(status, 1, msg, changes=False, **kw)
    sys.exit(msg)

def skill_dirs(include_packs):
    out = {}
    base = os.path.join(ROOT, 'skills', 'local', 'shared')
    for n in sorted(os.listdir(base)):
        if os.path.isfile(os.path.join(base, n, 'SKILL.md')):
            out[n] = os.path.join(base, n)
    if include_packs:
        pb = os.path.join(ROOT, 'skills', 'local', 'packs')
        if os.path.isdir(pb):
            for pk in sorted(os.listdir(pb)):
                sd = os.path.join(pb, pk, 'skills')
                if os.path.isdir(sd):
                    for n in sorted(os.listdir(sd)):
                        if os.path.isfile(os.path.join(sd, n, 'SKILL.md')):
                            out[n] = os.path.join(sd, n)
    return out

def copy_tree(src, dst):
    for d, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if x != '__pycache__']
        for f in files:
            if f.endswith(('.pyc', '.bak')):
                continue
            s = os.path.join(d, f)
            t = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copyfile(s, t)
            DONE.append({'path': t, 'action': 'copy'})

def main():
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dest', default=os.path.join('~', '.claude', 'skills'))
    ap.add_argument('--skills', help='danh sách skill, cách nhau bằng dấu phẩy (mặc định: tất cả) / comma-separated skills (default: all)')
    ap.add_argument('--include-packs', action='store_true', help='kèm skill của gói đã cài / include skills of installed packs')
    ap.add_argument('--overwrite', action='store_true', help='ghi đè skill đã có ở đích / overwrite skills already at the destination')
    ap.add_argument('--yes', action='store_true', help='thực hiện sao chép / actually copy')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        LANG = json.load(io.open(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json'), encoding='utf-8')).get('language', 'vi')
    except (OSError, ValueError):
        pass
    dest = os.path.abspath(os.path.expanduser(os.path.expandvars(a.dest)))
    sk = skill_dirs(a.include_packs)
    if a.skills:
        want = [x.strip() for x in a.skills.split(',') if x.strip()]
        miss = [x for x in want if x not in sk]
        if miss:
            stop(L('Không có skill: %s. Có sẵn: %s', 'No such skill: %s. Available: %s') % (', '.join(miss), ', '.join(sk)))
        sk = {k: sk[k] for k in want}
    print(('' if a.yes else L('[XEM TRƯỚC, chưa sao chép] ', '[PREVIEW, nothing copied] ')) + L('Đích: ', 'Destination: ') + dest)
    done = skipped = 0
    plan = []
    for n, src in sk.items():
        dst = os.path.join(dest, n)
        if os.path.exists(dst) and not a.overwrite:
            print('  - %s: %s' % (n, L('đã có ở đích, bỏ qua (dùng --overwrite để ghi đè)', 'already there, skipped (use --overwrite to replace)'))); skipped += 1
            plan.append({'path': dst, 'action': 'skip', 'reason': 'exists'})
            continue
        print('  - %s: %s' % (n, L('sẽ sao chép', 'will copy') if not a.yes else L('đã sao chép', 'copied')))
        bak = dst + '.bak-' + __import__('datetime').date.today().strftime('%Y%m%d')
        if os.path.exists(dst):
            plan += [{'path': dst, 'action': 'overwrite'}, {'path': bak, 'action': 'backup'}]
        else:
            plan.append({'path': dst, 'action': 'copy'})
        if a.yes:
            if os.path.exists(dst):
                shutil.copytree(dst, bak)
                DONE.append({'path': bak, 'action': 'backup'})
            copy_tree(src, dst)
        done += 1
    print(L('Tổng: %d skill, bỏ qua %d.', 'Total: %d skills, %d skipped.') % (done, skipped))
    if not a.yes:
        print(L('Thêm --yes để sao chép. Khởi động lại ứng dụng nếu skill chưa hiện.', 'Add --yes to copy. Restart the app if the skills do not show up.'))
    if a.yes:
        set_result('success', 0, L('Đã sao chép %d skill vào %s; bỏ qua %d.', 'Copied %d skills to %s; skipped %d.') % (done, dest, skipped),
                   changes=bool(done), dest=dest, files=plan,
                   next_actions=[L('Khởi động lại ứng dụng nếu skill chưa hiện.', 'Restart the app if the skills do not show up.')] if done else [])
    else:
        set_result('preview', 0, L('Xem trước: %d skill sẽ sao chép vào %s; bỏ qua %d. Chưa sao chép gì.', 'Preview: %d skills would be copied to %s; %d skipped. Nothing copied.') % (done, dest, skipped),
                   changes=bool(done), dest=dest, files=plan,
                   next_actions=[L('Thêm --yes để sao chép.', 'Add --yes to copy.')] if done else [])

def run_with_result():
    """Chạy lệnh và phát đúng một kết quả có cấu trúc; mã trong kết quả luôn bằng mã thoát / Run the command and emit exactly one structured result; its code always equals the exit code."""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    code, msg, fallback = 0, '', 'success'
    try:
        main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        fallback = 'success' if code == 0 else 'blocked'
        if isinstance(e.code, str):
            msg = e.code
            print(msg, file=sys.stderr)  # như sys.exit(msg) / same as sys.exit(msg)
        elif code:  # argparse đã in lỗi cú pháp / argparse has printed the usage error
            msg = L('Tham số không hợp lệ; xem trợ giúp của lệnh.', 'Invalid arguments; see the command help.')
    except OSError as e:
        code, msg, fallback = 1, str(e), 'error'
        if DONE:
            set_result('partial', 1, msg, changes=True, files=list(DONE),
                       next_actions=[L('Có thể còn một thư mục skill sao chép dở: xóa thư mục đó rồi chạy lại.', 'A skill folder may be half-copied: delete it, then run again.')])
            print('CHƯA HOÀN TẤT / INCOMPLETE: %s. Có thể đã sao chép một số file; chưa tự hoàn tác. / Some files may have been copied; no automatic rollback.' % e, file=sys.stderr)
        else:
            print('Lỗi / Error: %s' % e, file=sys.stderr)
    except Exception as e:  # lỗi bất ngờ vẫn phát kết quả / unexpected errors still emit a result
        traceback.print_exc()
        code, msg, fallback = 1, repr(e), 'error'
    res = LAST_RESULT
    if res is None:
        res = make(fallback, code=code, message=msg)
    elif res['code'] != code:
        res = make('error', code=code, message=L('Mã kết quả không khớp mã thoát.', 'Result code does not match the exit code.'))
    emit(res)
    return code

if __name__ == '__main__':
    if RESULT_REQUESTED:
        sys.exit(run_with_result())
    main()
