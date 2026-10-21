#!/usr/bin/env python3
"""Tạo project mới là một BẢN SAO của bộ mẫu; bộ mẫu giữ nguyên. / Create a new project as a COPY of the template.

Dùng / Usage (chạy từ bộ mẫu / run from the template folder):
  python tools/new_project.py --name "Tên công việc" [--dest THƯ_MỤC_CHA] [--lang vi|en] [--apply]

- Không có --apply: chỉ xem trước (in thư mục sẽ tạo), không ghi gì. / Without --apply: preview only, nothing written.
- --dest: nơi đặt project (mặc định: cùng chỗ với bộ mẫu). Project nằm ở <dest>/<tên>. / Default: next to the template.
- Không bao giờ ghi đè: thư mục đích đã có thì dừng. / Never overwrites: stops if the target folder exists.
- Bộ mẫu không bị sửa: chỉ đọc file của package, chép sang thư mục tạm cạnh đích rồi đổi tên một lần,
  sau đó chạy tools/init_project.py BÊN TRONG bản sao. / The template is only read; files go to a temp folder next to
  the target, which is renamed in one step; tools/init_project.py then runs INSIDE the copy.
- Chỉ chép file của package (theo MANIFEST/quy tắc của check_package.py) và logo, tên đơn vị, font trong assets/, không chép file
  người dùng trong references/, working/, output/... của bộ mẫu. / Only package files and the assets/ branding and fonts are copied.
Mã thoát / exit codes: 0 xong hoặc xem trước, 1 bị chặn/lỗi, 2 sai tham số. Chỉ cần Python 3.8+, không dùng mạng.
"""
import argparse, io, json, os, re, shutil, subprocess, sys, uuid
sys.dont_write_bytecode = True  # không để lại __pycache__ trong bộ mẫu / leave no __pycache__ in the template
from result_schema import emit, make
import check_package as cp

ROOT = cp.ROOT
LANG = 'vi'
LAST = {'result': None}
BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
TEMPLATE_OVERLAYS = cp.TEMPLATE_OVERLAYS  # một nguồn sự thật trong check_package / one source of truth in check_package

def L(vi, en):
    return en if LANG == 'en' else vi


def finish(status, code, message, **kw):
    LAST['result'] = make(status, code=code, message=message, **kw)
    print(message)
    for n in kw.get('next_actions') or []:
        print('  - ' + n)
    return code


def folder_name(name):
    """Tên thư mục từ tên công việc: giữ chữ có dấu, bỏ ký tự hệ điều hành cấm. / Folder name from the task name."""
    n = BAD_CHARS.sub(' ', name)
    n = re.sub(r'\s+', ' ', n).strip().strip('.').strip()
    return n[:80].rstrip('. ')


def template_role():
    """'template' (bộ mẫu nguyên vẹn hoặc kho nguồn có mẫu sạch), 'project' (đã khởi tạo) hoặc 'unknown'.
    Dựa vào nội dung file, không dựa vào tên thư mục. / From file evidence, never from the folder name."""
    return {'initialized': 'project', 'maintainer': 'template', 'clean': 'template'}.get(cp.source_state(), 'unknown')


def main(argv):
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', required=True)
    ap.add_argument('--dest', default='')
    ap.add_argument('--lang', choices=['vi', 'en'], default='vi')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--result-json', action='store_true')
    a = ap.parse_args(argv)
    LANG = a.lang
    name = a.name.strip()
    folder = folder_name(name)
    if not folder:
        return finish('blocked', 1, L('Cần nhập tên công việc (có chữ hoặc số). Chưa tạo gì.', 'A task name (with letters or digits) is required. Nothing was created.'),
                      changes=False)
    role = template_role()
    if role == 'project':
        return finish('blocked', 1, L('Thư mục này đã là một dự án, không phải bộ mẫu. Hãy tạo dự án mới từ bộ mẫu gốc (thư mục giải nén từ file ZIP, chưa dùng để làm việc). Chưa tạo gì.',
                                      'This folder is already a project, not the template. Create new projects from the original template (the folder unzipped from the ZIP and not used for work). Nothing was created.'),
                      changes=False, role=role)
    if role == 'unknown':
        return finish('blocked', 1, L('Chưa rõ đây là bộ mẫu hay dự án: PROJECT.md đã được sửa nhưng thư mục chưa được thiết lập thành dự án. Nếu đây là dự án của bạn: dùng "Thiết lập thư mục này". Nếu cần bộ mẫu: giải nén lại file ZIP. Chưa tạo gì.',
                                      'It is not clear whether this is the template or a project: PROJECT.md was edited but the folder was never set up as a project. If it is your project: use "Set up this folder". If you need the template: unzip the ZIP file again. Nothing was created.'),
                      changes=False, role=role)
    dest = os.path.abspath(os.path.expanduser(a.dest.strip().strip('"'))) if a.dest.strip() else os.path.dirname(ROOT)
    target = os.path.join(dest, folder)
    info = dict(name=name, target=target, dest=dest, folder=folder, template=ROOT, role=role)
    if not os.path.isdir(dest):
        return finish('blocked', 1, L('Không tìm thấy thư mục nơi lưu: %s. Chọn một thư mục có sẵn. Chưa tạo gì.', 'The location folder was not found: %s. Choose an existing folder. Nothing was created.') % dest,
                      changes=False, **info)
    real_t, real_root = os.path.realpath(target), os.path.realpath(ROOT)
    if real_t == real_root or real_t.startswith(real_root + os.sep):
        return finish('blocked', 1, L('Không tạo dự án bên trong bộ mẫu. Chọn nơi lưu khác (mặc định: cùng cấp với bộ mẫu). Chưa tạo gì.',
                                      'A project cannot be created inside the template. Choose another place (default: next to it). Nothing written.'),
                      changes=False, **info)
    if os.path.lexists(target):
        return finish('blocked', 1, L('Nơi lưu đã có thư mục "%s"; thư mục đó được giữ nguyên, không ghi đè. Đặt tên công việc khác hoặc chọn nơi lưu khác. Chưa tạo gì.',
                                      'A folder "%s" already exists there; it is never overwritten. Pick another name or place. Nothing written.') % folder,
                      changes=False, **info)
    problems = cp.delivery_problems()  # projection chung với build/adopt; bất thường thì chưa tạo gì, cả khi xem trước / shared with build/adopt; refused before anything is created
    if problems:
        return finish('blocked', 1, L('Bộ mẫu chưa giao được thành dự án mới: %s Chưa tạo gì.', 'The template cannot be delivered as a new project: %s Nothing was created.') % problems[0],
                      changes=False, findings=[{'severity': 'error', 'message': x} for x in problems], **info)
    files = cp.delivery_selection() + ['MANIFEST.sha256']
    if not a.apply:
        print(L('[XEM TRƯỚC, chưa tạo gì] Dự án mới từ bộ mẫu:', '[PREVIEW, nothing created yet] New project from the template:'))
        print('  ' + L('Tên công việc', 'Task name') + ': ' + name)
        print('  ' + L('Thư mục sẽ được tạo', 'Folder to be created') + ': ' + target)
        print('  ' + L('Sẽ chép %d file của bộ công cụ vào thư mục này rồi thiết lập dự án; bộ mẫu không bị thay đổi.', 'Will copy %d package files into this folder, then set up the project; the template is not changed.') % len(files))
        LAST['result'] = make('preview', code=0, message=L('Xem trước dự án mới; chưa tạo gì.', 'New project preview; nothing created yet.'),
                              changes=True, files=[{'path': target, 'action': 'create'}], file_count=len(files), **info)
        return 0
    tmp = os.path.join(dest, '.%s.creating-%s' % (folder, uuid.uuid4().hex[:8]))
    try:
        cp.materialize(tmp)  # đúng bytes và MANIFEST của bản giao, không chép MANIFEST kho nguồn / the shipped bytes and MANIFEST, not the source MANIFEST
        if os.path.lexists(target):  # xuất hiện trong lúc chép / appeared while copying
            raise FileExistsError(target)
        os.rename(tmp, target)
    except (OSError, cp.ProjectionError) as e:
        shutil.rmtree(tmp, ignore_errors=True)
        return finish('blocked' if isinstance(e, FileExistsError) else 'error', 1,
                      L('Không tạo được dự án (%s). Phần đã chép dở đã được xóa; bộ mẫu không bị thay đổi.', 'Could not create the project (%s). The partly copied files were removed; the template is unchanged.') % e,
                      changes=False, **info)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, os.path.join(target, 'tools', 'init_project.py'), '--name', name, '--lang', a.lang],
                       cwd=target, capture_output=True, env=env, stdin=subprocess.DEVNULL)
    out = (r.stdout + r.stderr).decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        return finish('partial', 1, L('Đã tạo bản sao tại %s nhưng bước thiết lập dự án chưa xong:\n%s', 'A copy was made at %s but the project setup did not finish:\n%s') % (target, out),
                      changes=True, files=[{'path': target, 'action': 'created'}],
                      next_actions=[L('Mở bảng điều khiển trong thư mục mới và dùng "Thiết lập thư mục này".', 'Open the panel in the new folder and use "Set up this folder".')], **info)
    return finish('success', 0, L('Đã tạo dự án "%s" tại %s. Bộ mẫu gốc giữ nguyên.', 'Created project "%s" at %s. The original template is unchanged.') % (name, target),
                  changes=True, files=[{'path': target, 'action': 'created'}],
                  next_actions=[L('Chép tài liệu nguồn vào thư mục references/ của dự án mới.', 'Copy source documents into the new project\'s references/ folder.'),
                                L('Mở thư mục dự án mới bằng ứng dụng AI bạn dùng (Claude, Codex, Gemini) và giao việc.', 'Open the new project folder in your AI app (Claude, Codex, Gemini) and give it the task.')],
                  **info)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    try:
        code = main(sys.argv[1:])
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 2
        if LAST['result'] is None:
            LAST['result'] = make('error', code=code, message=str(e.code or ''), changes=False)
    if '--result-json' in sys.argv and LAST['result'] is not None:
        emit(LAST['result'])
    sys.exit(code)
