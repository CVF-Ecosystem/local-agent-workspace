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

Không có --dest thì dùng ~/.claude/skills (Claude). Với Codex, Gemini/Antigravity... hãy chỉ --dest tới thư mục skill
của ứng dụng đó theo tài liệu của nó. Package không tự đổi cấu hình toàn cục. Cần Python 3.8+, không dùng mạng.
"""
import argparse, io, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = 'vi'
def L(vi, en): return en if LANG == 'en' else vi

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

def main():
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dest', default=os.path.join('~', '.claude', 'skills'))
    ap.add_argument('--skills', help='danh sách skill, cách nhau bằng dấu phẩy (mặc định: tất cả) / comma-separated skills (default: all)')
    ap.add_argument('--include-packs', action='store_true', help='kèm skill của gói đã cài / include skills of installed packs')
    ap.add_argument('--overwrite', action='store_true', help='ghi đè skill đã có ở đích / overwrite skills already at the destination')
    ap.add_argument('--yes', action='store_true', help='thực hiện sao chép / actually copy')
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
            sys.exit(L('Không có skill: %s. Có sẵn: %s', 'No such skill: %s. Available: %s') % (', '.join(miss), ', '.join(sk)))
        sk = {k: sk[k] for k in want}
    print(('' if a.yes else L('[XEM TRƯỚC, chưa sao chép] ', '[PREVIEW, nothing copied] ')) + L('Đích: ', 'Destination: ') + dest)
    done = skipped = 0
    for n, src in sk.items():
        dst = os.path.join(dest, n)
        if os.path.exists(dst) and not a.overwrite:
            print('  - %s: %s' % (n, L('đã có ở đích, bỏ qua (dùng --overwrite để ghi đè)', 'already there, skipped (use --overwrite to replace)'))); skipped += 1; continue
        print('  - %s: %s' % (n, L('sẽ sao chép', 'will copy') if not a.yes else L('đã sao chép', 'copied')))
        if a.yes:
            if os.path.exists(dst):
                shutil.copytree(dst, dst + '.bak-' + __import__('datetime').date.today().strftime('%Y%m%d'))
            copy_tree(src, dst)
        done += 1
    print(L('Tổng: %d skill, bỏ qua %d.', 'Total: %d skills, %d skipped.') % (done, skipped))
    if not a.yes:
        print(L('Thêm --yes để sao chép. Khởi động lại ứng dụng nếu skill chưa hiện.', 'Add --yes to copy. Restart the app if the skills do not show up.'))

if __name__ == '__main__':
    main()
