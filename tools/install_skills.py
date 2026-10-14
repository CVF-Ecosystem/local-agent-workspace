#!/usr/bin/env python3
"""Cài (sao chép) các skill của package vào thư mục skill của ứng dụng để chúng hiện trong menu native. TÙY CHỌN.
Optionally copy the package's skills into an app's skills folder so they show up in its native menu.

Mặc định chỉ BÁO CÁO việc sẽ làm; thêm --yes mới sao chép. Không xóa, không ghi đè (trừ khi có --overwrite).
Report-only by default; add --yes to copy. Nothing is deleted or overwritten unless --overwrite is given.

Chỉ chép skill đã được nhận (Status AVAILABLE hoặc ACTIVE trong .agent/SKILL_INDEX.md); ứng viên (REVIEW), skill đã tắt,
skill ngoài (skills/external/, skills/inbox/) không bao giờ được chép. Phải chọn skill (--skills) hoặc ghi rõ --all: ứng dụng
đã có khả năng tương tự thì không cần chép. Thư mục cùng tên ở đích không do công cụ này chép (có thể là skill native hoặc của
nguồn khác) không bao giờ bị ghi đè, kể cả với --overwrite.
Only accepted skills (Status AVAILABLE or ACTIVE in .agent/SKILL_INDEX.md) are copied; candidates (REVIEW), disabled skills and
outside skills (skills/external/, skills/inbox/) never are. Choose skills (--skills) or say --all: if the app already has a
similar capability there is no need to copy. A same-name folder at the destination that this tool did not copy (it may be a
native skill or come from another source) is never overwritten, not even with --overwrite.

Dùng / Usage:
  python tools/install_skills.py --dest "%USERPROFILE%\\.claude\\skills"                     # liệt kê skill chép được / list
  python tools/install_skills.py --dest ~/.claude/skills --skills meeting-minutes,data-charts # xem trước / preview
  python tools/install_skills.py --dest ~/.claude/skills --skills meeting-minutes --yes        # sao chép / copy
  python tools/install_skills.py --dest <...> --all --include-packs --yes                     # mọi skill đã nhận, kèm gói

Không có --dest thì dùng ~/.claude/skills (Claude). Codex và Gemini CLI cùng đọc ~/.agents/skills (theo tài liệu của hai ứng dụng,
kiểm tháng 10/2026). Ứng dụng khác: chỉ --dest tới thư mục skill theo tài liệu của nó. Package không tự đổi cấu hình toàn cục,
không sửa skill native, không chạy script của skill. Cần Python 3.8+, không dùng mạng.
"""
import argparse, datetime, io, json, os, re, shutil, sys, traceback
from result_schema import emit, make

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = '.workspace-skill.json'  # dấu nhận bản do công cụ này chép / marks a copy made by this tool
ACCEPTED = ('AVAILABLE', 'ACTIVE')
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
    """Skill dùng chung và (tùy chọn) skill của gói đã cài: {id: (thư mục, đường dẫn SKILL.md tương đối, nhóm)}.
    Không bao giờ gồm skills/external/, skills/inbox/ hay skills/local/project/ / never outside or project skills."""
    out = {}
    base = os.path.join(ROOT, 'skills', 'local', 'shared')
    for n in sorted(os.listdir(base)):
        if os.path.isfile(os.path.join(base, n, 'SKILL.md')):
            out[n] = (os.path.join(base, n), 'skills/local/shared/%s/SKILL.md' % n, 'shared')
    if include_packs:
        pb = os.path.join(ROOT, 'skills', 'local', 'packs')
        if os.path.isdir(pb):
            for pk in sorted(os.listdir(pb)):
                sd = os.path.join(pb, pk, 'skills')
                if os.path.isdir(sd):
                    for n in sorted(os.listdir(sd)):
                        if os.path.isfile(os.path.join(sd, n, 'SKILL.md')) and n not in out:
                            out[n] = (os.path.join(sd, n), 'skills/local/packs/%s/skills/%s/SKILL.md' % (pk, n), 'pack')
    return out

def index_status():
    """{skill id: (Location, Status)} từ .agent/SKILL_INDEX.md / from the project's skill index."""
    out = {}
    try:
        with io.open(os.path.join(ROOT, '.agent', 'SKILL_INDEX.md'), encoding='utf-8') as f:
            text = f.read()
    except OSError:
        return out
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('| ') and len(cells) >= 6 and cells[0] != 'Skill ID' and not set(line) <= set('|- '):
            out[cells[0]] = (cells[3], cells[5])
    return out

def eligibility(sid, rel, idx):
    """None khi chép được; còn lại là lý do / None when the skill may be copied; otherwise the reason."""
    if sid not in idx or idx[sid][0] != rel:
        return 'not_in_index'
    if idx[sid][1] not in ACCEPTED:
        return 'status_' + idx[sid][1].lower()
    # skill của gói: nhãn trong chỉ mục chưa đủ; cần xác nhận còn hiệu lực cho đúng nội dung đã cài và hồ sơ không từ chối bản này
    # a pack skill: the index label is not enough; a confirmation must hold for the exact installed content, and no record may refuse it
    m = re.match(r'skills/local/packs/([^/]+)/', rel)
    if m:
        try:
            import pack
            why = pack.installed_eligibility(m.group(1))
        except Exception:  # không kiểm được thì không chép / cannot verify: do not copy
            why = 'unverifiable'
        if why:
            return 'pack_' + why
    return None

def reason_text(r):
    if r == 'not_in_index':
        return L('không có dòng khớp trong .agent/SKILL_INDEX.md', 'no matching row in .agent/SKILL_INDEX.md')
    if r == 'status_review':
        return L('ứng viên (REVIEW), chưa qua tiếp nhận', 'candidate (REVIEW), not through intake')
    if r == 'status_disabled':
        return L('người dùng đã tắt (DISABLED)', 'disabled by the user (DISABLED)')
    if r == 'pack_not_confirmed':
        return L('gói chưa được xác nhận tiếp nhận ở project này (python tools/pack.py confirm <tên> --apply)', 'the pack is not confirmed in this project (python tools/pack.py confirm <name> --apply)')
    if r == 'pack_content_changed':
        return L('nội dung gói đã cài khác bản đã xác nhận: xét lại rồi xác nhận lại', 'the installed pack content differs from what was confirmed: review, then confirm again')
    if r == 'pack_refused':
        return L('hồ sơ tiếp nhận từ chối đúng bản đã cài', 'its intake record refuses the installed version')
    if r == 'pack_claim_withdrawn':
        return L('hồ sơ tiếp nhận của gói không còn ở mức đã nhận', 'the pack intake record no longer claims acceptance')
    if r.startswith('pack_'):
        return L('không kiểm được xác nhận của gói (%s)', 'cannot verify the pack confirmation (%s)') % r[5:]
    return L('trạng thái không cho chép (%s)', 'status does not allow copying (%s)') % r[7:].upper()

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
    ap.add_argument('--skills', help='danh sách skill đã nhận, cách nhau bằng dấu phẩy (hoặc dùng --all) / comma-separated accepted skills (or use --all)')
    ap.add_argument('--all', action='store_true', help='mọi skill đã được nhận / every accepted skill')
    ap.add_argument('--include-packs', action='store_true', help='kèm skill của gói đã cài / include skills of installed packs')
    ap.add_argument('--overwrite', action='store_true', help='thay bản do công cụ này chép trước đó / replace copies this tool made earlier')
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
    sk = skill_dirs(a.include_packs or bool(a.skills))  # tên chọn rõ có thể là skill của gói / named skills may come from a pack
    idx = index_status()
    excluded = [{'skill': k, 'reason': eligibility(k, v[1], idx)} for k, v in sk.items() if eligibility(k, v[1], idx)]
    choose = L('Chọn skill cần chép bằng --skills a,b (hoặc --all cho mọi skill đã nhận). Ứng dụng đã có khả năng tương tự thì không cần chép.',
               'Choose the skills to copy with --skills a,b (or --all for every accepted skill). If the app already has a similar capability there is no need to copy.')
    if a.skills:
        want = [x.strip() for x in a.skills.split(',') if x.strip()]
        miss = [x for x in want if x not in sk]
        if miss:
            stop(L('Không có skill: %s. Có sẵn: %s', 'No such skill: %s. Available: %s') % (', '.join(miss), ', '.join(sk)))
        bad = [(x, eligibility(x, sk[x][1], idx)) for x in want if eligibility(x, sk[x][1], idx)]
        if bad:
            stop(L('Không chép skill chưa được nhận: %s', 'Not copying skills that are not accepted: %s') % '; '.join('%s: %s' % (x, reason_text(r)) for x, r in bad),
                 excluded=[{'skill': x, 'reason': r} for x, r in bad])
        sk = {k: sk[k] for k in want}
        excluded = []
    elif a.all:
        sk = {k: v for k, v in sk.items() if not eligibility(k, v[1], idx)}
    else:
        ok = sorted(k for k, v in sk.items() if not eligibility(k, v[1], idx))
        if a.yes:
            stop(choose, eligible=ok, excluded=excluded)
        print(L('Chưa chọn skill. Skill chép được: ', 'No skill chosen. Skills that can be copied: ') + (', '.join(ok) or L('(không có)', '(none)')))
        for x in excluded:
            print('  - %s: %s' % (x['skill'], reason_text(x['reason'])))
        print(choose)
        set_result('preview', 0, L('Chưa chọn skill; %d skill chép được. Chưa sao chép gì.', 'No skill chosen; %d skills can be copied. Nothing copied.') % len(ok),
                   changes=False, dest=dest, files=[], eligible=ok, excluded=excluded, next_actions=[choose])
        return
    print(('' if a.yes else L('[XEM TRƯỚC, chưa sao chép] ', '[PREVIEW, nothing copied] ')) + L('Đích: ', 'Destination: ') + dest)
    for x in excluded:
        print('  - %s: %s' % (x['skill'], L('không chép: ', 'not copied: ') + reason_text(x['reason'])))
    done = skipped = 0
    plan = []
    version = ''
    try:
        with io.open(os.path.join(ROOT, 'VERSION'), encoding='utf-8') as f:
            version = f.read().strip()
    except OSError:
        pass
    for n, (src, rel, _) in sk.items():
        dst = os.path.join(dest, n)
        if os.path.exists(dst) and not os.path.isfile(os.path.join(dst, MARK)):
            print('  - %s: %s' % (n, L('ứng dụng đã có skill cùng tên không do package chép (có thể là native hoặc nguồn khác): giữ nguyên, không ghi đè',
                                       'the app already has a same-name skill this package did not copy (maybe native or another source): kept, not overwritten'))); skipped += 1
            plan.append({'path': dst, 'action': 'skip', 'reason': 'not_from_package'})
            continue
        if os.path.exists(dst) and not a.overwrite:
            print('  - %s: %s' % (n, L('đã có ở đích, bỏ qua (dùng --overwrite để thay bản package đã chép)', 'already there, skipped (use --overwrite to replace the package copy)'))); skipped += 1
            plan.append({'path': dst, 'action': 'skip', 'reason': 'exists'})
            continue
        print('  - %s: %s' % (n, L('sẽ sao chép', 'will copy') if not a.yes else L('đã sao chép', 'copied')))
        # sao lưu vào archive/ của project, không để trong thư mục ứng dụng tự quét (tránh một skill trùng tên)
        # back up into the project's archive/, never inside the app's scanned folder (avoids a duplicate skill name)
        bak_base = os.path.join(ROOT, 'archive', 'app-skills-backup-' + datetime.date.today().strftime('%Y%m%d'))
        bak, k = os.path.join(bak_base, n), 1
        while os.path.exists(bak):
            k += 1
            bak = os.path.join(bak_base, '%s-%d' % (n, k))
        if os.path.exists(dst):
            plan += [{'path': dst, 'action': 'overwrite'}, {'path': bak, 'action': 'backup'}]
        else:
            plan.append({'path': dst, 'action': 'copy'})
        if a.yes:
            if os.path.exists(dst):
                shutil.copytree(dst, bak)
                DONE.append({'path': bak, 'action': 'backup'})
            copy_tree(src, dst)
            with io.open(os.path.join(dst, MARK), 'w', encoding='utf-8') as f:
                f.write(json.dumps({'package': 'local-agent-workspace', 'version': version, 'skill': n, 'source': rel,
                                    'copied': datetime.date.today().isoformat()}, ensure_ascii=False, indent=2) + '\n')
            DONE.append({'path': os.path.join(dst, MARK), 'action': 'mark'})
        done += 1
    print(L('Tổng: %d skill, bỏ qua %d.', 'Total: %d skills, %d skipped.') % (done, skipped))
    if not a.yes:
        print(L('Thêm --yes để sao chép. Khởi động lại ứng dụng nếu skill chưa hiện.', 'Add --yes to copy. Restart the app if the skills do not show up.'))
    if a.yes:
        set_result('success', 0, L('Đã sao chép %d skill vào %s; bỏ qua %d.', 'Copied %d skills to %s; skipped %d.') % (done, dest, skipped),
                   changes=bool(done), dest=dest, files=plan, excluded=excluded,
                   next_actions=[L('Khởi động lại ứng dụng nếu skill chưa hiện.', 'Restart the app if the skills do not show up.')] if done else [])
    else:
        set_result('preview', 0, L('Xem trước: %d skill sẽ sao chép vào %s; bỏ qua %d. Chưa sao chép gì.', 'Preview: %d skills would be copied to %s; %d skipped. Nothing copied.') % (done, dest, skipped),
                   changes=bool(done), dest=dest, files=plan, excluded=excluded,
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
