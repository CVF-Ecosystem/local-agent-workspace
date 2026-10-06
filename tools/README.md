# tools/

Công cụ của package. Chỉ cần Python 3.8+, không cài thêm, không dùng mạng. Chạy từ thư mục gốc của project.
Khi làm việc văn phòng hằng ngày chỉ cần `init_project.py` (một lần); các công cụ còn lại dành cho người bảo trì.

## setup_wizard.py

Trình hướng dẫn cho người dùng không quen dòng lệnh. Bấm đúp `SETUP.bat` (Windows) hoặc `SETUP.command` (macOS) ở thư mục gốc,
hoặc chạy `python tools/setup_wizard.py`. Nó hỏi ngôn ngữ, tên project và năm thông tin ngắn (mục đích, đầu ra, văn phong,
nguồn, ràng buộc; Enter để bỏ qua), gọi `init_project.py` với các giá trị đó (điền `PROJECT.md`), rồi sao chép đoạn hướng dẫn
dán vào Project/cloud vào clipboard. Nếu có `setup_answers.json` ở thư mục gốc (tải từ form "Khởi tạo nhanh" trong `START_HERE.html`), nó dùng file này và không hỏi lại. Không làm gì nếu thư mục đã khởi tạo. Các giá trị cũng dùng được trực tiếp qua
`init_project.py --purpose --outputs --style --sources --constraints`.

## init_project.py

Khởi tạo project mới sau khi giải nén và đổi tên thư mục:

```text
python tools/init_project.py --name "Tên project" --lang vi
python tools/init_project.py --name "Project name" --lang en --dry-run
```

Điền tên vào `PROJECT.md`, đặt `.agent/STATE.md` sạch, ghi `.agent/PACKAGE_INFO.json` (phiên bản package, ngôn
ngữ, ngày khởi tạo). `--lang en` chép đè toàn bộ cây `en/` (trừ `en/PROJECT_INSTRUCTIONS_SNIPPET.md`) lên thư mục gốc: hướng dẫn agent,
ghi chú `.agent`, skill, README. File của package đã bị sửa được sao lưu thành `.bak-<ngày>`; file đã có nội dung của bạn
(PROJECT, STATE, HANDOFF, INDEX... đã điền) được giữ nguyên. Thông báo của script theo ngôn ngữ `--lang`.
`--dry-run` chỉ in việc sẽ làm; chạy lần hai cần `--force`. Script không xóa file nào.

## upgrade_package.py

Nâng cấp một project lên bản package mới mà không ghi đè việc của bạn. Mặc định chỉ báo cáo; thêm `--apply` mới ghi.

```text
python tools/upgrade_package.py --project "đường dẫn project cũ"        # chạy từ thư mục package MỚI
python tools/upgrade_package.py --from "đường dẫn package mới" --apply  # chạy từ project
```

So ba bên bằng `MANIFEST.sha256`: file chưa ai sửa thì cập nhật, file mới thì thêm, file bạn đã sửa thì giữ nguyên; nếu bạn sửa và
package cũng đổi thì lưu bản mới thành `<tên>.new`. Không đụng file của người dùng (PROJECT, STATE, INDEX, `references/`...), không xóa file nào.
Từ chối chạy trên thư mục chưa khởi tạo (có thể là thư mục nguồn của package) trừ khi có `--allow-uninitialized`.

## pack.py

Quản lý gói lĩnh vực (`packs/`): `list`, `add <tên>`, `update <tên> [--apply]`, `remove <tên>` (chuyển vào `archive/`), `check [<tên>]`,
`new <tên>` (tạo gói từ `packs/_template`). Gói cài vào `skills/local/packs/` và ghi trong `.agent/SKILL_INDEX.md` (Scope `PACK`). Xem `packs/README.md`.

## check_output.py

Kiểm tra cơ học một sản phẩm trước khi giao: `python tools/check_output.py <file>...` cho `.md`, `.txt`, `.html`, `.docx` (chỗ chưa điền, nhãn
mẫu minh họa, `isDemo`, tài nguyên mạng trong HTML) và chuyển `.csv`/`.xlsx` cho `spreadsheet-check`. Chỉ đọc; mã thoát 1 nếu có điều cần sửa.
`python tools/check_output.py --declaration <file>` kiểm một câu trả lời của agent đã lưu thành file: có khối "Khai báo thực hiện" / "Execution declaration" với đủ mục Cách làm, Nguồn, File, Chưa kiểm hay không; cảnh báo khi nói "sai lệch" mà không có con số.

## install_skills.py

Tùy chọn: sao chép skill của package vào thư mục skill của ứng dụng để hiện trong menu native, ví dụ
`python tools/install_skills.py --dest ~/.claude/skills --yes`. Mặc định chỉ xem trước; không ghi đè nếu không có `--overwrite`.

## check_package.py

```text
python tools/check_package.py                   kiểm tra chất lượng package
python tools/check_package.py --release         thêm kiểm tra sạch để phát hành
python tools/check_package.py --write-manifest  ghi MANIFEST.sha256
python tools/check_package.py --verify          file nào của package trong project đã bị sửa
```

Kiểm: `VERSION` và chuỗi phiên bản nhất quán, mục trong `CHANGELOG.md`, frontmatter và index của skill, đường dẫn
trong tài liệu, số mục khớp giữa bản Việt và bản Anh, HTML không tải từ mạng và khớp Markdown, cú pháp Python.
`--verify` bỏ qua các file người dùng sửa (PROJECT, `.agent/`, nguồn, đầu ra) và hiểu project dùng `--lang en`.

## build_release.py

```text
python tools/build_release.py                    kiểm, ghi MANIFEST, đóng dist/local-agent-workspace-v<VERSION>.zip
```

Đóng gói từ nguồn sạch (không có file project, không có `PACKAGE_INFO.json`), dòng kết thúc LF, thứ tự file cố định,
rồi giải nén ZIP vào thư mục tạm và chạy `--verify` để chắc ZIP khớp MANIFEST.

## Quy trình phát hành một phiên bản mới

1. Sửa nguồn; nâng số trong `VERSION`; thêm mục vào `CHANGELOG.md`; sửa các chuỗi "vX.Y" còn lại (script báo chỗ lệch).
2. `python tools/build_guides_html.py` rồi `python tools/check_package.py --release` cho đến khi đạt.
3. `python tools/build_release.py` và dùng file ZIP trong `dist/`.


## build_guides_html.py

Đồng bộ các trang HTML hướng dẫn với Markdown. Chỉ cần Python 3.8 trở lên, không cài thêm
thư viện, không dùng mạng.

```text
python tools/build_guides_html.py            # dựng lại HTML từ Markdown
python tools/build_guides_html.py --check    # chỉ kiểm tra; mã thoát 1 nếu HTML lệch Markdown
```

Chạy từ thư mục gốc của project. Mã thoát: `0` khớp hoặc đã dựng xong, `1` (khi `--check`) có
trang lệch, `2` có lỗi (ví dụ cú pháp Markdown chưa hỗ trợ hoặc khung HTML bị đổi).

### Script làm gì

Script xử lý hai bộ HTML, mỗi bộ gồm một `START_HERE` và bốn trang hướng dẫn riêng, đọc từ
Markdown tương ứng. Cấu hình hai bộ nằm trong danh sách `LOCALES` ở đầu script.

| Bộ | Markdown | Trang HTML |
|---|---|---|
| Tiếng Việt | `docs/HUONG_DAN_*_VI.md`, `docs/NGUON_THAM_KHAO_VI.md` | `docs/*.html`, `START_HERE.html` |
| Tiếng Anh | `docs/en/*.md` (`NEW_PROJECT_GUIDE`, `DAILY_USE_GUIDE`, `EXISTING_PROJECT_UPGRADE_GUIDE`, `SKILLS_GUIDE`, `SOURCES_AND_REFERENCES`) | `docs/en/*.html`, `START_HERE.en.html` |

Mỗi nguồn Markdown cập nhật cả trang riêng lẫn chương tương ứng trong `START_HERE` (nguồn tham
khảo chỉ có chương trong `START_HERE`). Với mỗi trang, script thay những vùng sau và giữ nguyên
phần còn lại:

- thân bài (`chapter-body`) và mục lục của phần (`chapter-toc`);
- tiêu đề `# ...` ở đầu file Markdown: `<h1>` của trang riêng, phần đầu của `<title>`, tiêu đề
  chương (`chapter-title`) trong `START_HERE`;
- thẻ `<meta name="source-sha256">`: SHA-256 của file Markdown (trang riêng) hoặc của các file
  Markdown nối bằng một dấu xuống dòng theo thứ tự trong cấu hình (`START_HERE`).

Ngôn ngữ chưa có file `START_HERE` thì bị bỏ qua.

### Script không làm gì

Khung trang, CSS, JavaScript, thanh bên, nút chuyển ngôn ngữ, dòng giới thiệu (`lead`), thẻ chọn
phần, số liệu tổng quan (ví dụ "11 skills"), tên mục trong thanh bên và chân trang không được
dựng lại; sửa trực tiếp trong HTML của từng bộ. Script không sửa Markdown và không dịch.

Thêm một hướng dẫn mới: viết Markdown cho từng ngôn ngữ, thêm mục tương ứng vào `docs` của từng
bộ trong `LOCALES`, thêm trang HTML (sao chép một trang có sẵn rồi sửa khung) và thẻ chương trong
`START_HERE`. Thêm một ngôn ngữ mới: thêm một phần tử vào `LOCALES`, tạo `START_HERE.<mã>.html`
và thư mục `docs/<mã>/` từ bộ có sẵn, sau đó dịch Markdown và khung.

### Phần Markdown được hỗ trợ

Tiêu đề đầu file `# ` (bỏ qua), mục `## `, đoạn văn (xuống dòng giữ nguyên), danh sách `- `,
bảng `|`, khối mã ``` (hiện thành ô có nút "Sao chép"), `mã nội tuyến`, `**đậm**`, và địa chỉ
`http(s)://` trần (thành liên kết). Cú pháp khác (`###`, danh sách đánh số, chữ nghiêng, ảnh,
liên kết `[chữ](url)`) chưa hỗ trợ; script dừng và báo dòng gây lỗi thay vì dựng sai. Để hỗ
trợ thêm cú pháp, sửa hàm `convert` và so sánh bằng cách chạy `--check` trên bản Markdown cũ.

### Quy trình gợi ý khi sửa hướng dẫn

1. Sửa file Markdown trong `docs/`.
2. Chạy `python tools/build_guides_html.py`.
3. Nếu thay đổi làm đổi số skill, tên phần hoặc thẻ chọn phần, sửa tay các chỗ đó trong HTML của cả hai ngôn ngữ.
   Khi sửa một quy tắc hoặc đoạn văn ở một ngôn ngữ, sửa đoạn tương ứng ở ngôn ngữ còn lại.
4. Chạy `python tools/build_guides_html.py --check` để xác nhận đồng bộ.
5. Mở `START_HERE.html` trong trình duyệt, xem mục vừa sửa. Nút "Sao chép" và liên kết trong
   trang nên hoạt động; không có yêu cầu mạng.

Script được thử trên bộ hướng dẫn hai ngôn ngữ của package (HTML dựng lại khớp từng byte với Markdown). Chưa thử
trên Markdown viết ngoài các cú pháp nêu trên.
