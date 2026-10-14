# tools/

Công cụ của package, chạy từ thư mục gốc project. Khởi tạo, chuyển đổi, nâng cấp và kiểm tra văn bản/CSV chỉ cần Python 3.8+.
Kiểm tra Excel và thư viện nguồn cần `openpyxl`: `python -m pip install openpyxl`. Công cụ không tự cài thêm;
cài thư viện có thể cần mạng, còn các thao tác trên file chạy cục bộ. Bảng điều khiển hỗ trợ cả người dùng hằng ngày và người bảo trì.

## setup_wizard.py

Trình hướng dẫn cho người dùng không quen dòng lệnh. Bấm đúp `SETUP.bat` (Windows) hoặc `SETUP.command` (macOS) ở thư mục gốc,
hoặc chạy `python tools/setup_wizard.py`. Nó hỏi ngôn ngữ, tên project và năm thông tin ngắn (mục đích, đầu ra, văn phong,
nguồn, ràng buộc; Enter để bỏ qua), gọi `init_project.py` với các giá trị đó (điền `PROJECT.md`), rồi sao chép đoạn hướng dẫn
dán vào Project/cloud vào clipboard. Nếu có `setup_answers.json` ở thư mục gốc (tải từ form "Khởi tạo nhanh" trong `START_HERE.html`), nó dùng file này và không hỏi lại. Không làm gì nếu thư mục đã khởi tạo. Các giá trị cũng dùng được trực tiếp qua
`init_project.py --purpose --outputs --style --sources --constraints`.

## app.py, app_ui.html

Bảng điều khiển trong trình duyệt. Bấm đúp `APP.bat` (Windows) hoặc `APP.command` (macOS), hoặc chạy `python tools/app.py`
(`--no-browser` để tự mở địa chỉ được in ra, `--port N` để chọn cổng). Máy chủ nhỏ chỉ nghe trên 127.0.0.1, mỗi lần mở có mã truy
cập riêng, không dùng mạng. Mỗi nút gọi một công cụ có sẵn trong thư mục này với tham số cố định (`init_project`, `adopt_project`,
`upgrade_package`, `pack`, `check_output`, `install_skills`, `check_package`, `build_guides_html`, `build_release`, `library`, `transaction`); thao tác có ghi
luôn xem trước rồi mới thực hiện. Nút "Chọn…" dùng hộp chọn thư mục của `tkinter` nếu Python có. Tự tắt khoảng 3 phút sau khi
đóng trang. Giao diện nằm trong `app_ui.html` (một file, không tài nguyên ngoài, tiếng Việt và tiếng Anh, sáng và tối).

Mọi phản hồi từ `/api/run` có trường `result` theo schema `local-agent-workspace/result-v1`: trạng thái, mã kết quả,
có thay đổi hay không, file liên quan, phần chưa kiểm và việc cần làm. Mọi công cụ mà bảng điều khiển gọi (kể cả khởi tạo, kiểm package, gói lĩnh vực, cài skill, thư viện nguồn, dựng HTML và
giao dịch) đều phát schema trực tiếp. Backend kiểm schema và mã thoát trước khi chuyển cho giao diện; nếu công cụ không trả
kết quả hợp lệ, backend báo lỗi, không đoán kết quả từ câu chữ trong output.

Trang **Chờ hợp nhất** liệt kê `.new` thuộc manifest package hoặc gói đã cài. Trạng thái xem được lưu trong
`.agent/MERGE_STATUS.json`, chỉ gồm đường dẫn tương đối, dấu vân tay và trạng thái; không lưu nội dung tài liệu. File `.new`
ngoài phạm vi package không bị đưa vào danh sách. Ứng dụng không tự hợp nhất hoặc xóa file. Nút "So sánh" gọi
`merge_center.diff()`: chỉ đọc, không lưu; mỗi file tối đa 256 KB, tối đa 4000 dòng kết quả; file nhị phân hoặc không phải
UTF-8 không hiện nội dung.

Trang **Tình trạng ứng dụng** đọc phiên bản và loại workspace (`project`, `template` hoặc `unknown`, nhận diện từ nội dung file
chứ không từ tên thư mục), Python, các chức năng tùy chọn kèm lý do và cách khắc phục (`components()`), giao dịch dở (`transaction.incomplete()`)
và 20 dòng lịch sử gần nhất (`ops_log.summary()`). Nút "Tiếp tục" gọi `transaction.py resume`; "Phục hồi" gọi
`transaction.py rollback` và có hộp xác nhận; "Xóa lịch sử" xóa file nhật ký (có xác nhận); "Tạo gói chẩn đoán" ghi một
ZIP trong `.agent/runtime/diagnostics/diagnostics-<thời điểm>.zip`, với đường dẫn thư mục và tên người dùng đã được che, không
có nội dung tài liệu, tên project hay đường dẫn tuyệt đối. Tổng quan hiện một banner khi có giao dịch dở. Mỗi thao tác
bấm từ bảng điều khiển ghi một dòng vào lịch sử (`ops_log.py`).

## library.py

Thư viện nguồn trong `references/` (xem skill `source-library`). `init` tạo các thư mục nhóm (legal, policies, templates,
source-documents) kèm README và chép mẫu chỉ mục thành `references/_INDEX.xlsx` nếu chưa có (không ghi đè). `check [--days 180]`
kiểm chỉ mục, báo theo số dòng: thiếu file, file chưa vào chỉ mục, trùng số hiệu, "Còn hiệu lực" nhưng đã ghi bị thay thế, ngày
kiểm tình trạng quá cũ, mức "Cần đối chiếu", văn bản Mật; mã thoát 1 khi có lỗi. `find <từ khóa> [--group "Pháp luật"] [--all]`
tìm không phân biệt dấu và cho biết có toàn văn hay không. `stats` đếm theo nhóm, tình trạng. `--json` cho bảng điều khiển.
Chỉ đọc sheet "Danh mục". Cần openpyxl.

## init_project.py

Khởi tạo project mới sau khi giải nén và đổi tên thư mục:

```text
python tools/init_project.py --name "Tên project" --lang vi
python tools/init_project.py --name "Project name" --lang en --dry-run
```

Điền tên vào `PROJECT.md`, đặt `.agent/STATE.md` sạch, ghi `.agent/PACKAGE_INFO.json` (phiên bản package, ngôn
ngữ, ngày khởi tạo). `--lang en` chép đè toàn bộ cây `en/` (trừ `en/PROJECT_INSTRUCTIONS_SNIPPET.md`) lên thư mục gốc: hướng dẫn agent,
ghi chú `.agent`, skill, README. File của package đã bị sửa được sao lưu thành `.bak-<ngày>`; file đã có nội dung của bạn
(PROJECT, STATE, HANDOFF, INDEX... kể cả điền một phần) và hướng dẫn agent đã sửa được giữ nguyên. Thông báo của script theo ngôn ngữ `--lang`.
`--dry-run` chỉ in việc sẽ làm; chạy lần hai cần `--force`. Script không xóa file nào. Mọi lần ghi chạy qua một giao dịch có nhật ký (xem `transaction.py`); nếu bị gián đoạn, lần chạy sau báo CHƯA HOÀN TẤT và không ghi thêm cho đến khi `resume` hoặc `rollback`.

## upgrade_package.py

Nâng cấp một project lên bản package mới mà không ghi đè việc của bạn. Mặc định chỉ báo cáo; thêm `--apply` mới ghi.

```text
python tools/upgrade_package.py --project "đường dẫn project cũ"        # chạy từ thư mục package MỚI
python tools/upgrade_package.py --from "đường dẫn package mới" --apply  # chạy từ project
```

So ba bên bằng `MANIFEST.sha256`: file chưa ai sửa thì cập nhật, file mới thì thêm, file bạn đã sửa thì giữ nguyên; nếu bạn sửa và
package cũng đổi thì lưu bản mới thành `<tên>.new`. Không đụng file của người dùng (PROJECT, STATE, INDEX, `references/`...), không xóa file nào.
Từ chối chạy trên thư mục chưa khởi tạo (có thể là thư mục nguồn của package) trừ khi có `--allow-uninitialized`.
Project chưa có `MANIFEST.sha256` bị từ chối khi so sánh (nâng cấp tay theo hướng dẫn). Việc ghi (`--apply`) chạy qua một giao dịch
có nhật ký: nếu bị gián đoạn, công cụ báo CHƯA HOÀN TẤT và các lần chạy sau bị chặn cho đến khi `transaction.py` resume hoặc rollback.

Từ bản 1.4.0, `.agent/SKILL_INDEX.md` (file của bạn, không bị ghi đè) được **thêm** các dòng skill dùng chung còn thiếu của package mới để agent tìm thấy skill mới; dòng đã có không bị sửa. Project đang ở bản cũ hơn bản 1.4.0 nên chạy script từ thư mục package MỚI (cách thứ nhất ở trên), vì bản script nằm trong project còn cũ.

## adopt_project.py

Đưa package vào một project ĐÃ CÓ lần đầu (chưa có `VERSION`/`.agent/`). Mặc định chỉ báo cáo; thêm `--apply` mới ghi.

```text
python tools/adopt_project.py --project "đường dẫn project cũ" --name "Tên project" [--lang vi|en] [--purpose "..."] [--apply]   # chạy từ thư mục package
```

Chỉ thêm file còn thiếu; không xóa, không ghi đè file của bạn. `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` cũ vẫn giữ nguyên và có hiệu lực;
bản package khác nội dung được lưu `<tên>.new` để hợp nhất. Áp dụng cả khi chọn tiếng Anh. File `.new` đã có nội dung khác sẽ chặn thao tác trước khi ghi.
File khác trùng tên và khác cũng giữ của bạn, bản package lưu `<tên>.new`. Skill riêng sẵn có trong
`skills/local/project/` được thêm dòng vào `.agent/SKILL_INDEX.md` với Status `REVIEW` (công cụ ghi nhận, không tự tiếp nhận; người dùng xác nhận rồi đổi sang `AVAILABLE`). Cuối cùng chạy `init_project.py`. Từ chối chạy nếu project đã có package (dùng `upgrade_package.py`). Việc ghi chạy qua một giao dịch có nhật ký; sau đó công cụ
chạy `init_project.py` (nằm ngoài giao dịch). Nếu `init_project.py` lỗi, kết quả là `partial`: chạy lại
`python tools/init_project.py --name "Tên project" --lang vi --force`.

## transaction.py

Giao dịch có nhật ký cho mọi lần ghi của `init_project.py`, `adopt_project.py` và `upgrade_package.py`.

```text
python tools/transaction.py status               liệt kê giao dịch còn dở (mã thoát 1 nếu có)
python tools/transaction.py resume <mã>          tiếp tục: áp các thao tác còn lại
python tools/transaction.py rollback <mã>        phục hồi: đưa file về bản gốc
```

Tùy chọn: `--project <thư mục>` (mặc định là project chứa thư mục `tools`), `--result-json`, `--lang vi|en`.

Luồng ghi: kiểm trước (quyền ghi, dung lượng, đích không phải thư mục), ghi bản tạm vào thư mục giao dịch, sao lưu file sẽ đổi,
rồi commit từng thao tác và đánh dấu xong. Lỗi trước khi commit thì không file nào của project bị đổi.

- Trạng thái `prepared` và `committing` là còn dở. Lúc đó các công cụ ghi và bảng điều khiển từ chối ghi thêm (mã thoát 1, báo mã giao dịch) cho đến khi `resume` hoặc `rollback`. Trạng thái `rollback_partial` là kết thúc và không chặn.
- `resume` chỉ áp thao tác còn chờ khi file đích vẫn ở bản gốc và bản tạm khớp hash; file đã có bản mới thì đánh dấu xong; file bị đổi khác thì bỏ qua và ghi `skipped_conflict`. Không tiếp tục được khi trạng thái là `rollback_partial`.
- `rollback` đưa về bản gốc các thao tác đã xong, nếu file hiện tại vẫn là bản đã ghi. File do người dùng sửa sau sự cố được giữ nguyên (trạng thái `rollback_partial`) và bản gốc của chúng được giữ trong `.agent/runtime/transactions/<mã>/backup/` để khôi phục tay. Thao tác tạo file mới: file đó bị gỡ nếu chưa bị sửa. Giao dịch đã commit không phục hồi được vì không còn bản sao lưu.

Nhật ký `journal.json` nằm trong `.agent/runtime/transactions/<mã>/` (không vào MANIFEST, ZIP hay git). Nhật ký không chứa nội dung file, tên người hay đường dẫn tuyệt đối; chỉ có đường dẫn tương đối của các file trong project. Khi commit xong, thư mục tạm và thư mục sao lưu bị xóa; giữ 20 giao dịch đã hoàn tất gần nhất.

Biến `LOCAL_AGENT_WORKSPACE_TEST_FAULT` gây lỗi giả có kiểm soát, chỉ dùng trong kiểm thử; không đặt khi dùng thật.
Mã thoát: `status` 0 không có việc dở, 1 có; `resume` và `rollback` 0 hoàn tất, 1 còn việc hoặc xung đột, 2 lỗi cách dùng.

## ops_log.py

Module không có lệnh riêng. Ghi lịch sử thao tác của bảng điều khiển vào `.agent/runtime/operations.jsonl` (JSON Lines): mỗi lần bấm một nút là một dòng gồm thời điểm UTC, tên thao tác (danh sách cố định; tên lạ thành `unknown`), trạng thái, mã thoát, số file tác động, mã giao dịch và thời gian chạy. Chỉ giữ 500 dòng mới nhất; dòng hỏng bị bỏ qua khi đọc. Không bao giờ ghi nội dung tài liệu, đường dẫn, tên file, tên người, tên project, dữ liệu đã gõ hay khóa truy cập. `clear()` chỉ xóa đúng file này; `summary()` cho trang Tình trạng biết lần thành công, lần lỗi và lần dở gần nhất. File không vào MANIFEST, ZIP hay git.

## pack.py

Quản lý gói lĩnh vực (`packs/`): `list`, `add <tên>`, `update <tên> [--apply]`, `remove <tên>` (chuyển vào `archive/`), `check [<tên>]`,
`new <tên>` (tạo gói từ `packs/_template`). Gói cài vào `skills/local/packs/` và ghi trong `.agent/SKILL_INDEX.md` (Scope `PACK`). Xem `packs/README.md`.
Khối `intake` trong `pack.json` chỉ là lời khai của gói. Cài, cập nhật hay `check` không bao giờ nhận gói: mọi gói cài vào project đều ghi
`REVIEW`. `add <tên> --confirm` (cài và nhận một lệnh), `update <tên> --apply --confirm` (cập nhật và nhận lại nội dung mới) và `confirm <tên> [--dry-run]` (gói đã cài; chạy luôn, `--dry-run` chỉ xem) là hành động xác nhận của người dùng, không có mặc định âm thầm; chỉ chạy khi lời khai hợp lệ (hồ sơ giải được
tới file local có thật, `UNKNOWN`/`REPLACEMENT` thiếu `comparison`/`DEFER`/bản không khớp đều bị chặn), ghi `AVAILABLE` và gắn xác nhận với
dấu vân tay nội dung đã cài. Nội dung đổi (kể cả cùng số phiên bản hay sửa tay bản đã cài), phiên bản mới hay hồ sơ không còn ở mức đã nhận
thì xác nhận hết hiệu lực. `REUSE_NO_IMPORT`/`REJECT_VERSION` thì không cài, không cập nhật; từ chối đúng bản đã cài thì `check` báo và
`install_skills.py` không xuất. `DISABLED` luôn được giữ. `list`, `check`, `confirm` và kết quả có cấu trúc có trường `intake`
(`accepted`/`candidate`/`refused` kèm lý do; `accepted` ở đây nghĩa là lời khai hợp lệ, chưa phải xác nhận). Không chạy script nào của gói.
Chuẩn chung: `skills/README.md`.

## check_output.py

Kiểm tra cơ học một sản phẩm trước khi giao: `python tools/check_output.py <file>...` cho `.md`, `.txt`, `.html`, `.docx` (chỗ chưa điền, nhãn
mẫu minh họa, `isDemo`, tài nguyên mạng trong HTML) và chuyển `.csv`/`.xlsx` cho `spreadsheet-check`. Chỉ đọc.
Mã thoát: **0** đã kiểm đạt trong phạm vi hỗ trợ; **1** đã kiểm có vấn đề/cần xem xét; **2** có file chưa kiểm được.
Kiểm nhiều file lấy trạng thái nghiêm trọng nhất, đồng thời báo từng file. Caller cũ cần cập nhật cách hiểu mã 1 và 2.
Word: đọc thân bài, đầu/chân trang, chú thích chân trang/cuối tài liệu, kể cả chữ chia thành nhiều đoạn định dạng.
Chưa kiểm bố cục, chữ trong ảnh, bình luận và thay đổi được theo dõi. File lỗi hoặc định dạng không hỗ trợ không được báo đạt.
The same exit codes apply in English: 0 passed within scope, 1 findings/review, 2 not fully checked.
`python tools/check_output.py --declaration <file>` kiểm một câu trả lời của agent đã lưu thành file: có khối "Khai báo thực hiện" / "Execution declaration" với đủ mục Cách làm, Nguồn, File, Chưa kiểm hay không; cảnh báo khi nói "sai lệch" mà không có con số.

## install_skills.py

Tùy chọn: sao chép skill đã được nhận vào thư mục skill của ứng dụng để hiện trong menu native, ví dụ
`python tools/install_skills.py --dest ~/.claude/skills --skills meeting-minutes --yes`. Không có `--yes` thì chỉ xem trước; không chọn
`--skills` hay `--all` thì chỉ liệt kê skill chép được (thêm `--yes` lúc đó bị chặn). Chỉ chép skill dùng chung hoặc của gói đã cài có Status
`AVAILABLE`/`ACTIVE` (skill của gói còn cần xác nhận `pack.py confirm` còn hiệu lực cho đúng nội dung đã cài và hồ sơ không từ chối bản đó); ứng viên `REVIEW`, skill `DISABLED`, `skills/external/`, `skills/inbox/`, `skills/local/project/` không bao giờ được chép.
Mỗi bản chép có file dấu `.workspace-skill.json`. `--overwrite` chỉ thay bản có dấu đó (bản cũ lưu vào `archive/app-skills-backup-<ngày>/`,
không để trong thư mục ứng dụng tự quét); thư mục cùng tên không có dấu (native hoặc nguồn khác, kể cả bản chép bằng phiên bản package cũ
chưa có dấu) không bao giờ bị ghi đè: muốn thay thì tự xử lý thư mục đó. Kết quả có cấu trúc có `eligible` và `excluded` (kèm lý do).

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

Kiểm tương thích Python 3.8 là heuristic, không thay thế việc chạy thật trên Python 3.8: mọi file `.py` được phân tích bằng
`ast.parse(feature_version=(3, 8))`, cộng một danh sách mẫu API và chú thích của phiên bản mới (ví dụ `str.removeprefix`,
`functools.cache`, `zip(strict=...)`, chú thích `list[...]` lúc chạy, `X | None`). Kết quả có thể báo nhầm hoặc bỏ sót (ví dụ
toán tử `dict | dict`). Sửa cảnh báo bằng cách viết lại theo API của Python 3.8. Chạy thật trên 3.8 là việc của CI; CI chưa chạy lần nào.

Cờ ẩn `--result-json` xuất envelope `local-agent-workspace/result-v1`; mã trong envelope luôn bằng mã thoát. Bảng điều khiển dùng cờ này.

## build_release.py

```text
python tools/build_release.py                       bản chính thức: chạy đủ cổng rồi đóng dist/local-agent-workspace-v<VERSION>.zip
python tools/build_release.py --rc 1                bản thử: dist/local-agent-workspace-v<VERSION>-rc1.zip (VERSION không đổi)
python tools/build_release.py --rc 1 --skip-check   RC không chạy cổng; báo cáo ghi các cổng là skipped (bản chính thức không dùng cờ này)
```

Dựng cây phát hành trong thư mục tạm và không sửa working tree. PROJECT, STATE và HANDOFF sạch lấy từ bộ mẫu phát hành
riêng của kho nguồn; STATE phát triển không đi vào ZIP. Công cụ tạo MANIFEST trong cây tạm, đóng file theo thứ tự cố định,
rồi giải nén ZIP vào thư mục tạm khác và chạy `--verify`. Bộ mẫu nguồn, roadmap, tests, feedback và dữ liệu project không
đi vào package người dùng. Công cụ này chỉ dùng tại kho nguồn; bảng điều khiển tự ẩn nút đóng gói trong package đã phát hành.

Trước khi đóng gói, bốn cổng sau được chạy. Nếu một cổng `failed`, công cụ thoát mã 1, không tạo ZIP và không tạo báo cáo
cổng; ZIP và báo cáo cũ cùng tên bị xóa.

- `package_check`: `check_package --release` (cấu trúc, mẫu phát hành sạch, song ngữ, phiên bản, HTML khớp Markdown).
- `python38_compat`: kiểm tương thích Python 3.8 bằng heuristic (xem mục check_package.py bên dưới).
- `behaviour_tests`: `python -B -m unittest discover -s tests`; chỉ chạy khi có thư mục tests, tức ở kho nguồn.
- `release_tree`: `check_package --release` trên cây phát hành tạm; luôn chạy, kể cả với `--skip-check`.

Trạng thái cổng: `passed`, `failed`, `skipped` (bỏ qua vì `--skip-check` hoặc không có tests), `nested` (xem dưới).
`--skip-check` chỉ dùng với `--rc N`; bản chính thức bị từ chối với mã thoát 2.

Build lồng nhau: khi `behaviour_tests` chạy bộ kiểm thử, nó đặt biến môi trường `LOCAL_AGENT_WORKSPACE_GATE_NESTED=1`. Một build
được gọi từ trong bộ kiểm thử với biến này chỉ ghi `behaviour_tests` là `nested` (không phải `passed`) và không chạy lại bộ
kiểm thử, để tránh đệ quy; các cổng khác vẫn chạy.

Sau khi đóng ZIP, công cụ giải nén vào thư mục tạm và chạy `--verify`; nếu không khớp, ZIP bị xóa và công cụ thoát mã 1. ZIP
không chứa dấu thời gian, nên hai lần dựng từ cùng một nguồn cho cùng SHA-256.

Báo cáo cổng `<ZIP>.gate.json` (schema `local-agent-workspace/release-gate-v1`) nằm cạnh ZIP, gồm: phiên bản, loại (`official`
hoặc `rc`), số RC, `skip_check`, tên ZIP và SHA-256, từng cổng với trạng thái và thời gian chạy, nền tảng, Python, commit git
và cờ `dirty` (`null` nếu không có git).

Mã thoát: 0 thành công; 1 cổng không đạt hoặc lỗi đóng gói; 2 lỗi cách dùng.

## result_schema.py, merge_center.py

`result_schema.py` định nghĩa envelope kết quả ổn định giữa công cụ và bảng điều khiển. `merge_center.py` nhận diện file
chờ hợp nhất từ manifest và gói đã cài, lưu trạng thái xem mà không lưu nội dung file. Hai module chỉ dùng thư viện chuẩn.

## Quy trình phát hành một phiên bản mới

Quy trình đầy đủ (bản thử RC, nghiệm thu, bản chính thức, ma trận hỗ trợ, báo cáo cổng và các giới hạn còn lại) nằm trong file
RELEASING.md của thư mục .github ở kho nguồn. Thư mục này không vào ZIP. Tóm tắt:

1. Sửa nguồn; nâng số trong `VERSION`; thêm mục vào `CHANGELOG.md` có tiêu đề khớp `VERSION`; sửa các chuỗi "vX.Y" còn lại (script báo chỗ lệch). Chạy `python tools/build_guides_html.py`.
2. `python tools/check_package.py --release` và `python -B -m unittest discover -s tests -v` (trong kho nguồn) đều phải đạt. Thư mục tests và roadmap chỉ dành cho người duy trì, không đưa vào package người dùng.
3. `python tools/build_release.py --rc 1`: mở `<ZIP>.gate.json` cạnh ZIP trong `dist/`; mọi cổng phải `passed` và `git.dirty` phải `false`.
4. Nghiệm thu RC: giải nén vào thư mục mới, chạy `python tools/check_package.py --verify` (phải thoát 0), thử nâng cấp một bản sao project. Nếu lỗi, sửa nguồn rồi quay lại bước 1 với RC mới.
5. `python tools/build_release.py` (không có `--rc`): lưu ZIP cùng báo cáo cổng và ghi SHA-256 trong ghi chú phát hành.


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
