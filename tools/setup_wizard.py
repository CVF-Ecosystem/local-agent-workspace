#!/usr/bin/env python3
"""Trình hướng dẫn khởi tạo project: hỏi vài câu, rồi tự chạy tools/init_project.py và điền PROJECT.md.
Setup wizard: asks a few questions, then runs tools/init_project.py and fills in PROJECT.md.

Cách chạy / How to run: bấm đúp SETUP.bat (Windows) hoặc SETUP.command (macOS), hoặc: python tools/setup_wizard.py
Chỉ cần Python 3.8+. Không dùng mạng. Chỉ ghi file qua init_project.py (không xóa file nào).
"""
import io, json, os, re, subprocess, sys, webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TXT = {
 'vi': {
  'lang_q': 'Chọn ngôn ngữ cho project',
  'title': 'KHỞI TẠO PROJECT MỚI',
  'intro': 'Trả lời vài câu hỏi. Câu nào chưa biết thì nhấn Enter để bỏ qua, điền sau trong PROJECT.md.',
  'name': 'Tên project (bắt buộc)',
  'purpose': 'Công việc này để làm gì, ai sẽ dùng? (ví dụ: soạn quy trình cho phòng Vận hành)',
  'outputs': 'Đầu ra mong đợi (ví dụ: quy trình, biểu mẫu, báo cáo tuần)',
  'style': 'Ngôn ngữ và văn phong (ví dụ: tiếng Việt, trang trọng, theo mẫu hiện có)',
  'sources': 'Nguồn / mẫu chính đã duyệt (đường dẫn hoặc tên tài liệu)',
  'constraints': 'Ràng buộc quan trọng (ví dụ: không đưa số liệu khách hàng ra ngoài)',
  'sensitivity': 'Mức nhạy cảm dữ liệu (ví dụ: nội bộ; có dữ liệu cá nhân khách hàng thì ghi rõ)',
  'need_name': 'Cần nhập tên project.',
  'summary': 'Sẽ khởi tạo với thông tin sau:',
  'confirm': 'Tiếp tục? (Enter = Có, n = Hủy)',
  'cancel': 'Đã hủy, chưa ghi gì.',
  'done_head': 'XONG. Việc nên làm tiếp:',
  'next1': '1. Mở PROJECT.md, xem lại các dòng vừa điền và bổ sung nếu cần.',
  'next2': '2. Đặt tài liệu nguồn vào references/ (hoặc ghi đường dẫn vào .agent/INDEX.md).',
  'next3': '3. Mở thư mục này bằng ứng dụng bạn dùng (Claude, Codex, Gemini...) và giao việc đầu tiên.',
  'clip_ok': 'Đã sao chép đoạn hướng dẫn cho Project/cloud vào clipboard (nếu dùng Claude Project, dán vào phần hướng dẫn).',
  'clip_no': 'Nếu dùng Project/cloud, dán đoạn dưới đây vào phần hướng dẫn của Project:',
  'open_q': 'Mở bộ hướng dẫn (START_HERE) trong trình duyệt? (y/N)',
  'already': 'Thư mục này đã được khởi tạo trước đó (có .agent/PACKAGE_INFO.json). Không làm gì thêm.\nMuốn chạy lại: python tools/init_project.py --name "Tên" --force',
  'fail': 'Khởi tạo gặp lỗi, xem thông báo phía trên.',
  'ctx': 'Bối cảnh: %s.',
  'loaded': 'Đã đọc setup_answers.json (từ form Khởi tạo nhanh); dùng thông tin này, không hỏi lại.',
 },
 'en': {
  'lang_q': 'Choose the project language',
  'title': 'NEW PROJECT SETUP',
  'intro': 'Answer a few questions. Press Enter to skip any you do not know yet; fill it in later in PROJECT.md.',
  'name': 'Project name (required)',
  'purpose': 'What is this work for and who will use it? (e.g. writing procedures for the Operations team)',
  'outputs': 'Expected outputs (e.g. procedures, forms, weekly report)',
  'style': 'Language and house style (e.g. English, formal, follow the existing template)',
  'sources': 'Main approved sources / templates (paths or document names)',
  'constraints': 'Important constraints (e.g. do not share customer data externally)',
  'sensitivity': 'Data sensitivity (e.g. internal; say so if it holds customer personal data)',
  'need_name': 'A project name is required.',
  'summary': 'The project will be set up with:',
  'confirm': 'Continue? (Enter = Yes, n = Cancel)',
  'cancel': 'Cancelled, nothing was written.',
  'done_head': 'DONE. Suggested next steps:',
  'next1': '1. Open PROJECT.md, review the lines just filled in and add anything missing.',
  'next2': '2. Put source documents in references/ (or list their paths in .agent/INDEX.md).',
  'next3': '3. Open this folder in the app you use (Claude, Codex, Gemini...) and give it the first task.',
  'clip_ok': 'The Project/cloud instructions were copied to the clipboard (if you use a Claude Project, paste them into its instructions).',
  'clip_no': 'If you use a Project/cloud, paste the text below into the Project instructions:',
  'open_q': 'Open the handbook (START_HERE) in your browser? (y/N)',
  'already': 'This folder was already initialized (.agent/PACKAGE_INFO.json exists). Nothing more to do.\nTo run again: python tools/init_project.py --name "Name" --force',
  'fail': 'Setup failed; see the message above.',
  'ctx': 'Context: %s.',
  'loaded': 'Read setup_answers.json (from the Quick setup form); using it without asking again.',
 },
}
FIELDS = [('purpose', '--purpose'), ('outputs', '--outputs'), ('style', '--style'),
          ('sources', '--sources'), ('constraints', '--constraints'), ('sensitivity', '--sensitivity')]

def ask(prompt, required=False, t=None):
    while True:
        try:
            v = input('\n%s\n> ' % prompt).strip()
        except EOFError:
            sys.exit(1)
        if v or not required:
            return v
        print(t['need_name'])

def load_answers():
    """Đọc setup_answers.json (tải từ form trong START_HERE) nếu có và hợp lệ; ngược lại trả None."""
    path = os.path.join(ROOT, 'setup_answers.json')
    try:
        d = json.load(io.open(path, encoding='utf-8-sig'))
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or not str(d.get('name', '')).strip():
        return None
    out = {'lang': 'en' if d.get('lang') == 'en' else 'vi', 'name': str(d['name']).strip()}
    for k, _ in FIELDS:
        out[k] = str(d.get(k, '')).strip()
    return out

def snippet(lang, context):
    """Đoạn hướng dẫn dán vào Project/cloud, đã điền dòng bối cảnh nếu có."""
    try:
        if lang == 'en':
            src = io.open(os.path.join(ROOT, 'en', 'PROJECT_INSTRUCTIONS_SNIPPET.md'), encoding='utf-8').read()
        else:
            src = io.open(os.path.join(ROOT, 'docs', 'HUONG_DAN_TAO_PROJECT_MOI_VI.md'), encoding='utf-8').read()
        blocks = re.findall(r'```text\n(.*?)```', src, re.S)
        text = next(b for b in blocks if ('Rules:' in b or 'Nguyên tắc:' in b))
    except (OSError, StopIteration):
        return None
    if context:
        text = re.sub(r'(Bối cảnh|Context): \[[^\]]*\]\.?', lambda m: TXT[lang]['ctx'] % context.rstrip('.'), text, count=1)
    return text

def to_clipboard(text):
    try:
        if sys.platform.startswith('win'):
            subprocess.run(['clip'], input=text.encode('utf-16'), check=True)
        elif sys.platform == 'darwin':
            subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        else:
            subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
        return True
    except Exception:
        return False

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    if os.path.exists(os.path.join(ROOT, '.agent', 'PACKAGE_INFO.json')):
        lang0 = 'vi'
        print(TXT['vi']['already'] + '\n\n' + TXT['en']['already'])
        return
    print('=' * 60 + '\n  Local Agent Workspace\n' + '=' * 60)
    pre = load_answers()
    if pre:
        lang = pre['lang']; t = TXT[lang]; name = pre['name']; ans = {k: pre.get(k, '') for k, _ in FIELDS}
        print('\n' + t['loaded'])
    else:
        c = ask('Ngôn ngữ / Language:  1 = Tiếng Việt   2 = English  (Enter = 1)')
        lang = 'en' if c.strip() in ('2', 'en', 'EN', 'english', 'English') else 'vi'
        t = TXT[lang]
        print('\n' + t['title'] + '\n' + t['intro'])
        name = ask(t['name'], required=True, t=t)
        ans = {k: ask(t[k]) for k, _ in FIELDS}

    print('\n' + t['summary'])
    print('  - %s: %s' % (t['name'].split(' (')[0], name))
    for k, _ in FIELDS:
        if ans[k]:
            print('  - %s: %s' % (t[k].split(' (')[0].split('?')[0], ans[k]))
    if ask(t['confirm']).lower() in ('n', 'no', 'k', 'không', 'khong'):
        print(t['cancel']); return

    cmd = [sys.executable, os.path.join(ROOT, 'tools', 'init_project.py'), '--name', name, '--lang', lang]
    for k, flag in FIELDS:
        if ans[k]:
            cmd += [flag, ans[k]]
    print()
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print('\n' + t['fail']); sys.exit(r.returncode)

    print('\n' + '=' * 60 + '\n' + t['done_head'])
    for k in ('next1', 'next2', 'next3'):
        print(t[k])
    ctx = '; '.join(x for x in (ans['purpose'], ans['style']) if x)
    text = snippet(lang, ctx)
    if text:
        if to_clipboard(text):
            print('\n' + t['clip_ok'])
        else:
            print('\n' + t['clip_no'] + '\n\n' + text)
    if ask(t['open_q']).lower() in ('y', 'yes', 'c', 'có', 'co'):
        webbrowser.open('file:///' + os.path.join(ROOT, 'START_HERE.en.html' if lang == 'en' else 'START_HERE.html').replace(os.sep, '/'))

if __name__ == '__main__':
    main()
