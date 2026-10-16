#!/usr/bin/env python3
"""Trình hướng dẫn khởi tạo project: hỏi vài câu, rồi tự chạy tools/init_project.py và điền PROJECT.md.
Setup wizard: asks a few questions, then runs tools/init_project.py and fills in PROJECT.md.

Cách chạy / How to run: bấm đúp SETUP.bat (Windows) hoặc SETUP.command (macOS), hoặc: python tools/setup_wizard.py
Chỉ cần Python 3.8+. Không dùng mạng. Chỉ ghi file qua init_project.py (không xóa file nào).
"""
import io, json, os, re, subprocess, sys, webbrowser
sys.dont_write_bytecode = True  # không để lại __pycache__ trong bộ mẫu / leave no __pycache__ in the template

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TXT = {
 'vi': {
  'lang_q': 'Chọn ngôn ngữ hướng dẫn cho dự án',
  'title': 'THIẾT LẬP THƯ MỤC NÀY LÀM DỰ ÁN',
  'intro': 'Trả lời vài câu hỏi. Câu nào chưa biết thì nhấn Enter để bỏ qua, bổ sung sau trong PROJECT.md.',
  'name': 'Tên dự án (bắt buộc)',
  'purpose': 'Công việc này để làm gì, ai sẽ dùng? (ví dụ: soạn quy trình cho phòng Vận hành)',
  'outputs': 'Bạn muốn nhận được gì? (ví dụ: quy trình, biểu mẫu, báo cáo tuần)',
  'style': 'Ngôn ngữ và văn phong (ví dụ: tiếng Việt, trang trọng, theo mẫu hiện có)',
  'sources': 'Tài liệu nguồn hoặc mẫu chính đã được duyệt (tên tài liệu hoặc đường dẫn)',
  'constraints': 'Ràng buộc quan trọng (ví dụ: không đưa số liệu khách hàng ra ngoài)',
  'sensitivity': 'Thông tin cần bảo mật (chỉ nêu loại thông tin, ví dụ: dữ liệu cá nhân khách hàng; không ghi mật khẩu hay dữ liệu thật)',
  'need_name': 'Cần nhập tên dự án.',
  'summary': 'Sẽ thiết lập thư mục này với thông tin sau:',
  'confirm': 'Tiếp tục? (Enter = Có, n = Hủy)',
  'cancel': 'Đã hủy, chưa ghi gì.',
  'done_head': 'XONG. Việc nên làm tiếp:',
  'next1': '1. Mở PROJECT.md, xem lại các dòng vừa điền và bổ sung nếu cần.',
  'next2': '2. Đặt tài liệu nguồn vào references/ (hoặc ghi đường dẫn vào .agent/INDEX.md).',
  'next3': '3. Mở thư mục này bằng ứng dụng AI bạn dùng (Claude, Codex, Gemini...) và giao việc đầu tiên.',
  'clip_ok': 'Đã sao chép đoạn hướng dẫn vào bộ nhớ tạm. Nếu ứng dụng AI có phần hướng dẫn riêng cho Project (ví dụ Claude Project), dán vào đó.',
  'clip_no': 'Nếu ứng dụng AI có phần hướng dẫn riêng cho Project (ví dụ Claude Project), dán đoạn dưới đây vào đó:',
  'open_q': 'Mở bộ hướng dẫn (START_HERE) trong trình duyệt? (y/N)',
  'already': 'Thư mục này đã được thiết lập thành dự án (có .agent/PACKAGE_INFO.json). Không làm gì thêm.\nMuốn chạy lại: python tools/init_project.py --name "Tên" --force',
  'fail': 'Thiết lập gặp lỗi, xem thông báo phía trên.',
  'ctx': 'Bối cảnh: %s.',
  'loaded': 'Đã đọc setup_answers.json (từ form Khởi tạo nhanh); dùng thông tin này, không hỏi lại.',
  'role_q': 'Thư mục này là BỘ MẪU GỐC (chưa dùng cho công việc nào). Bạn muốn:\n  1 = Tạo dự án mới là một bản sao, đặt cùng cấp với bộ mẫu (khuyên dùng; bộ mẫu gốc giữ nguyên)\n  2 = Dùng chính thư mục này làm dự án (thư mục này sẽ không còn là bộ mẫu)\n(Enter = 1)',
  'task': 'Tên công việc (dùng làm tên thư mục dự án, bắt buộc)',
  'dest': 'Nơi lưu dự án (Enter = cùng cấp với bộ mẫu: %s)',
  'copy_done': 'Dự án mới nằm ở thư mục nêu trên. Bộ mẫu gốc không thay đổi. Việc nên làm tiếp:',
  'copy1': '1. Chép tài liệu nguồn vào thư mục references/ của dự án mới.',
  'copy2': '2. Mở thư mục dự án mới bằng ứng dụng AI bạn dùng (Claude, Codex, Gemini...) và giao việc.',
  'copy3': '3. Bấm đúp APP.bat / APP.command trong thư mục dự án để lấy lời nhắc cho trợ lý AI và theo dõi công việc.',
 },
 'en': {
  'lang_q': 'Choose the guidance language for the project',
  'title': 'SET UP THIS FOLDER AS A PROJECT',
  'intro': 'Answer a few questions. Press Enter to skip any you do not know yet; fill it in later in PROJECT.md.',
  'name': 'Project name (required)',
  'purpose': 'What is this work for and who will use it? (e.g. writing procedures for the Operations team)',
  'outputs': 'What do you want to receive? (e.g. procedures, forms, weekly report)',
  'style': 'Language and house style (e.g. English, formal, follow the existing template)',
  'sources': 'Main approved sources / templates (paths or document names)',
  'constraints': 'Important constraints (e.g. do not share customer data externally)',
  'sensitivity': 'Information to keep confidential (name the kind only, e.g. customer personal data; never write passwords or real data)',
  'need_name': 'A project name is required.',
  'summary': 'This folder will be set up with:',
  'confirm': 'Continue? (Enter = Yes, n = Cancel)',
  'cancel': 'Cancelled, nothing was written.',
  'done_head': 'DONE. Suggested next steps:',
  'next1': '1. Open PROJECT.md, review the lines just filled in and add anything missing.',
  'next2': '2. Put source documents in references/ (or list their paths in .agent/INDEX.md).',
  'next3': '3. Open this folder in your AI app (Claude, Codex, Gemini...) and give it the first task.',
  'clip_ok': 'The instructions were copied to the clipboard. If your AI app has its own Project instructions (for example a Claude Project), paste them there.',
  'clip_no': 'If your AI app has its own Project instructions (for example a Claude Project), paste the text below there:',
  'open_q': 'Open the handbook (START_HERE) in your browser? (y/N)',
  'already': 'This folder is already set up as a project (.agent/PACKAGE_INFO.json exists). Nothing more to do.\nTo run again: python tools/init_project.py --name "Name" --force',
  'fail': 'Setup failed; see the message above.',
  'ctx': 'Context: %s.',
  'loaded': 'Read setup_answers.json (from the Quick setup form); using it without asking again.',
  'role_q': 'This folder is the ORIGINAL TEMPLATE (not used for any work yet). Do you want to:\n  1 = Create a new project as a copy beside the template (recommended; the original template stays as is)\n  2 = Use this folder itself as the project (it will no longer be a template)\n(Enter = 1)',
  'task': 'Task name (becomes the project folder name, required)',
  'dest': 'Project location (Enter = beside the template: %s)',
  'copy_done': 'The new project is in the folder above. The original template is unchanged. Suggested next steps:',
  'copy1': '1. Copy source documents into the new project\'s references/ folder.',
  'copy2': '2. Open the new project folder in your AI app (Claude, Codex, Gemini...) and give it the task.',
  'copy3': '3. Double-click APP.bat / APP.command in the project folder to get the message for your AI assistant and follow the work.',
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
        # bộ mẫu: hỏi vai trò trước khi ghi gì; mặc định tạo bản sao / template: ask its role before writing; default is a copy
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        try:
            import new_project
            role = new_project.template_role()
        except Exception:
            role = 'unknown'
        if role == 'template' and ask(t['role_q']).strip() not in ('2',):
            task = ask(t['task'], required=True, t=t)
            dest = ask(t['dest'] % os.path.dirname(ROOT))
            cmd = [sys.executable, os.path.join(ROOT, 'tools', 'new_project.py'), '--name', task, '--lang', lang, '--apply']
            if dest:
                cmd += ['--dest', dest]
            print()
            r = subprocess.run(cmd, cwd=ROOT)
            if r.returncode != 0:
                print('\n' + t['fail']); sys.exit(r.returncode)
            print('\n' + '=' * 60 + '\n' + t['copy_done'])
            for k in ('copy1', 'copy2', 'copy3'):
                print(t[k])
            return
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
