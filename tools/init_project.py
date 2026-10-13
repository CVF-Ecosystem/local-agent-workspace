#!/usr/bin/env python3
"""Khởi tạo project mới từ package (chạy một lần sau khi giải nén và đổi tên thư mục).

Dùng:
  python tools/init_project.py --name "Tên project" [--lang vi|en] [--dry-run] [--force]

Việc script làm:
  - điền tên project vào PROJECT.md;
  - với --lang en: chép đè toàn bộ cây en/ (hướng dẫn agent, ghi chú .agent, skill, README) lên thư mục
    gốc, trừ en/PROJECT_INSTRUCTIONS_SNIPPET.md. File của package bị thay mà đã bị sửa được sao lưu thành
    <tên>.bak-<ngày>; file của người dùng (PROJECT, STATE, HANDOFF, INDEX...) đã điền thì giữ nguyên;
  - nếu có --purpose/--outputs/--style/--sources/--constraints/--sensitivity: điền các dòng tương ứng trong PROJECT.md;
  - đặt .agent/STATE.md sạch;
  - ghi .agent/PACKAGE_INFO.json (phiên bản package, ngôn ngữ, ngày khởi tạo).
Mọi thay đổi ghi qua một giao dịch có nhật ký (tools/transaction.py); nếu bị gián đoạn, chạy resume hoặc rollback.
All changes go through one journaled transaction; if interrupted, run resume or rollback.
Script không xóa file nào và không dùng mạng. Chỉ cần Python 3.8+.
"""
import argparse, datetime, io, json, os, re, sys
from result_schema import emit, make
import transaction as tx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERLAY_SKIP = {'en/PROJECT_INSTRUCTIONS_SNIPPET.md'}

def overlay_pairs():
    """Mọi file trong en/ (trừ OVERLAY_SKIP) và đường dẫn đích ở thư mục gốc."""
    out = []
    base = P('en')
    for d, dirs, files in os.walk(base):
        dirs.sort()
        for f in sorted(files):
            src = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, '/')
            if src in OVERLAY_SKIP or f.endswith('.bak') or '.bak-' in f:
                continue
            out.append((src, src[3:]))
    return out
FIELDS = [('purpose', ('Mục đích và người đọc', 'Purpose and audience')),
          ('outputs', ('Đầu ra mong đợi', 'Expected outputs')),
          ('style', ('Ngôn ngữ và văn phong', 'Language and house style')),
          ('sources', ('Nguồn / mẫu đã duyệt chính', 'Main sources / approved templates')),
          ('constraints', ('Ràng buộc quan trọng', 'Important constraints')),
          ('sensitivity', ('Mức nhạy cảm dữ liệu', 'Data sensitivity'))]
USER_TEMPLATES = {'PROJECT.md', '.agent/STATE.md', '.agent/HANDOFF.md', '.agent/INDEX.md',
                  '.agent/SKILL_INDEX.md', '.agent/PENDING_LESSONS.md'}
NAME_LINE = {'vi': '- Tên dự án: [Tên]', 'en': '- Project name: [Name]'}
PHASE_PLACEHOLDER = {'vi': '[Phase/trạng thái hiện tại]', 'en': '[Current phase/status]'}
PHASE_TEXT = {'vi': 'Mới khởi tạo từ package v%s ngày %s; chưa có công việc.',
              'en': 'Just initialised from package v%s on %s; no work yet.'}

LANG = 'vi'
RESULT_REQUESTED = '--result-json' in sys.argv
LAST_RESULT = None
TX = {'id': None}  # mã giao dịch đang ghi / transaction id of the current write
def L(vi, en): return en if LANG == 'en' else vi

def P(rel): return os.path.join(ROOT, *rel.split('/'))
def rd(rel): return io.open(P(rel), encoding='utf-8', newline='').read()

def is_original(rel):
    """True nếu file còn đúng như trong package (theo MANIFEST), nên không cần sao lưu khi thay."""
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import check_package as cp
        m = cp.read_manifest()
        return bool(m) and rel in m and cp.sha(rel) == m[rel]
    except Exception:
        return False

def main():
    global LANG, LAST_RESULT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', required=True, help='tên project / project name')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    for k, labels in FIELDS:
        ap.add_argument('--' + k, default='', help='điền dòng "%s" trong PROJECT.md / fill the "%s" line' % labels)
    ap.add_argument('--dry-run', action='store_true', help='chỉ in việc sẽ làm, không ghi')
    ap.add_argument('--force', action='store_true', help='chạy lại trên project đã khởi tạo')
    ap.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    LANG = a.lang
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    name = a.name.strip()
    if not name:
        sys.exit(L('Tên project không được để trống.', 'The project name must not be empty.'))
    if not os.path.isfile(P('VERSION')) or not os.path.isfile(P('PROJECT.md')):
        sys.exit(L('Không thấy VERSION hoặc PROJECT.md: hãy chạy script trong thư mục package đã giải nén.', 'VERSION or PROJECT.md not found: run the script inside the unzipped package folder.'))
    info_path = '.agent/PACKAGE_INFO.json'
    if os.path.exists(P(info_path)) and not a.force:
        sys.exit(L('Project đã được khởi tạo (có %s). Thêm --force nếu thật sự muốn chạy lại.', 'The project is already initialized (%s exists). Add --force if you really want to run again.') % info_path)
    ver = rd('VERSION').strip()
    today = datetime.date.today().isoformat()
    stamp = today.replace('-', '')
    log = []
    virt = {}    # rel -> nội dung text sau khi ghi / text content after the write
    baks = []    # (đường dẫn .bak, bytes cũ) / (backup path, old bytes)

    def cur(rel):
        return virt[rel] if rel in virt else rd(rel)

    def pristine(dst):
        """File còn ở dạng mẫu (chưa điền) thì được thay bằng bản tiếng Anh."""
        if is_original(dst):
            return True
        if dst in USER_TEMPLATES or dst in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md'):
            return False
        return True

    if a.lang == 'en':
        pairs = overlay_pairs()
        if not pairs:
            sys.exit(L('Thiếu thư mục en/ trong package.', 'The en/ folder is missing from the package.'))
        swapped = 0
        for src, dst in pairs:
            new = rd(src)
            old = rd(dst) if os.path.isfile(P(dst)) else None
            if old == new:
                continue
            if old is not None and not pristine(dst):
                log.append(L('Giữ nguyên %s (đã có nội dung của bạn).', 'Kept %s (it has your own content).') % dst)
                continue
            keep = old is not None and not is_original(dst)  # file đã sửa (kể cả mẫu người dùng) luôn được sao lưu trước khi thay
            swapped += 1
            if keep or dst in USER_TEMPLATES or swapped <= 6:
                log.append(L('Chép %s -> %s', 'Copied %s -> %s') % (src, dst) +
                           (L(' (sao lưu bản cũ .bak-%s)', ' (old copy saved as .bak-%s)') % stamp if keep else ''))
            if keep:
                with open(P(dst), 'rb') as f:
                    baks.append((dst + '.bak-' + stamp, f.read()))
            virt[dst] = new
        if swapped > 6:
            log.append(L('... và %d file khác trong en/ (tổng %d file đã chép).', '... and %d more files from en/ (%d copied in total).') % (max(swapped - 6, 0), swapped))

    line = next((v for v in (NAME_LINE[a.lang], NAME_LINE['vi'], NAME_LINE['en'])
                 if v in cur('PROJECT.md')), NAME_LINE[a.lang])
    if line in cur('PROJECT.md'):
        log.append(L('Điền tên project vào PROJECT.md', 'Fill the project name into PROJECT.md'))
        virt['PROJECT.md'] = cur('PROJECT.md').replace(line, line.split('[')[0] + name, 1)
    else:
        log.append(L('Cảnh báo: PROJECT.md không còn dòng "%s" (đã điền tay?); bỏ qua bước điền tên.', 'Warning: PROJECT.md no longer has the line "%s" (filled in by hand?); skipping the name step.') % line)

    for k, labels in FIELDS:
        val = getattr(a, k).strip().replace('\n', ' ')
        if not val:
            continue
        label = next((v for v in labels if re.search(r'^- %s:' % re.escape(v), cur('PROJECT.md'), re.M)),
                     labels[0 if a.lang == 'vi' else 1])
        pat = re.compile(r'^(- %s: )\[[^\n]*\]$' % re.escape(label), re.M)
        if pat.search(cur('PROJECT.md')):
            log.append(L('Điền "%s" vào PROJECT.md', 'Fill "%s" into PROJECT.md') % label)
            virt['PROJECT.md'] = pat.sub(lambda m, val=val: m.group(1) + val, cur('PROJECT.md'), count=1)
        else:
            log.append(L('Bỏ qua "%s": dòng này trong PROJECT.md đã có nội dung.', 'Skipped "%s": that line in PROJECT.md already has content.') % label)

    ph = next((v for v in PHASE_PLACEHOLDER.values() if v in cur('.agent/STATE.md')), PHASE_PLACEHOLDER[a.lang])
    if ph in cur('.agent/STATE.md'):
        log.append(L('Đặt trạng thái khởi đầu trong .agent/STATE.md', 'Set the starting state in .agent/STATE.md'))
        virt['.agent/STATE.md'] = cur('.agent/STATE.md').replace(ph, PHASE_TEXT[a.lang] % (ver, today), 1)
    else:
        kept = L('Giữ nguyên .agent/STATE.md (đã có nội dung của bạn).', 'Kept .agent/STATE.md (it has your own content).')
        if kept not in log:
            log.append(kept)

    info = {'package': 'local-agent-workspace', 'version': ver, 'language': a.lang,
            'project_name': name, 'initialized': today}
    log.append(L('Ghi %s', 'Wrote %s') % info_path)
    virt[info_path] = json.dumps(info, ensure_ascii=False, indent=2) + '\n'

    # chỉ những file thật sự đổi / only files whose bytes really change
    writes = []
    for rel, text in virt.items():
        data = text.encode('utf-8')
        old = open(P(rel), 'rb').read() if os.path.isfile(P(rel)) else None
        if old != data:
            writes.append((rel, data))
    files = ([{'path': rel, 'action': 'write'} for rel, _ in writes] +
             [{'path': bak, 'action': 'backup'} for bak, _ in baks])
    header = ((L('[CHẠY THỬ, chưa ghi gì] ', '[DRY RUN, nothing written] ') if a.dry_run else '') +
              L('Khởi tạo project "%s" (package v%s, ngôn ngữ %s):', 'Initializing project "%s" (package v%s, language %s):') % (name, ver, a.lang))

    if a.dry_run:
        print(header)
        for m in log:
            print(' - ' + m)
        LAST_RESULT = make('preview', message='Initialization preview', changes=bool(files), files=files,
                           next_actions=[])
        return

    blocker = tx.blocked_message(ROOT)
    if blocker:
        open_tx = tx.incomplete(ROOT)[0]['id']
        LAST_RESULT = make('blocked', code=1, message=blocker, changes=False, transaction=open_tx,
                           next_actions=['python tools/transaction.py resume %s' % open_tx,
                                         'python tools/transaction.py rollback %s' % open_tx])
        sys.exit(blocker)
    for bak, data in baks:
        if os.path.exists(P(bak)) and open(P(bak), 'rb').read() != data:
            msg = L('Đã có %s khác nội dung; không ghi đè bản sao lưu cũ. Chưa ghi gì.',
                    '%s already exists with other content; will not overwrite an old backup. Nothing written.') % bak
            LAST_RESULT = make('blocked', code=1, message=msg, changes=False, next_actions=['Move or rename the existing .bak file, then retry.'])
            sys.exit(msg)
    t = tx.Transaction(ROOT, 'init')
    for bak, data in baks:
        t.add(bak, data, 'create_exclusive')
    for rel, data in writes:
        t.add(rel, data, 'write')
    TX['id'] = t.txid if t.journal['ops'] else None
    try:
        t.run()
    except tx.TransactionError as e:
        TX['id'] = None
        LAST_RESULT = make('blocked', code=1, message=str(e), changes=False, next_actions=['Fix the problem above, then retry.'])
        sys.exit('CHƯA GHI GÌ / NOTHING WRITTEN: %s' % e)
    print(header)
    for m in log:
        print(' - ' + m)
    print(L('\nXong. Việc tiếp theo: mở PROJECT.md điền mục đích, người đọc, đầu ra; sau đó giao việc đầu tiên cho agent.', '\nDone. Next: open PROJECT.md and fill in the purpose, readers and outputs; then give the agent the first task.'))
    print('Nếu dùng Project/cloud: dán đoạn hướng dẫn trong mục 5 của docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md'
          if a.lang == 'vi' else
          'If you use a Project/cloud: paste the text in section 5 of docs/en/NEW_PROJECT_GUIDE.md')
    LAST_RESULT = make('success', message='Project initialized', changes=bool(files), files=files,
                       transaction=TX['id'])

if __name__ == '__main__':
    try:
        main()
        if RESULT_REQUESTED:
            emit(LAST_RESULT or make('success', message='Project initialized', changes=None))
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
                      next_actions=['python tools/transaction.py resume %s' % TX['id'],
                                    'python tools/transaction.py rollback %s' % TX['id']] if TX['id'] else ['Check the project folder, then retry.']))
        sys.exit(msg)
