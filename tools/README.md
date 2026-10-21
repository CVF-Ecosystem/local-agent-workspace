# tools/

Công cụ của package, chạy từ thư mục gốc project. Khởi tạo, chuyển đổi, nâng cấp và kiểm tra văn bản/CSV chỉ cần Python 3.8+.
Kiểm tra Excel và thư viện nguồn cần `openpyxl`: `python -m pip install openpyxl`. Công cụ không tự cài thêm;
cài thư viện có thể cần mạng, còn các thao tác trên file chạy cục bộ. Bảng điều khiển hỗ trợ cả người dùng hằng ngày và người bảo trì.

## audit_scripts.py

Kiểm vị trí lưu script theo `skills/README.md`, mục "Script hỗ trợ skill và công việc".
Python 3.8+, chỉ thư viện chuẩn; chỉ đọc bytes, không import/chạy mã tìm thấy, không ghi,
di chuyển, xóa hoặc tự nhận script vào skill.

```text
python tools/audit_scripts.py <thu-muc>                 có script lẻ là báo cần xem xét
python tools/audit_scripts.py <thu-muc> --max-loose 3   ngưỡng cũ: hơn 3 file trong từng thư mục
```

Mặc định quét thư mục hiện tại. Nhận `.py` không phân biệt hoa/thường. Mã thoát 0: không
thư mục nào vượt ngưỡng trong phạm vi đã quét; 1: vượt ngưỡng; 2: đối số sai hoặc chưa kiểm
đủ (root thiếu/không là thư mục, lỗi đọc, liên kết/reparse point trong vùng cần quét).
Lỗi/chưa kiểm ưu tiên hơn cảnh báo. Từ bản công cụ này, mặc định đổi từ 3 sang 0; cờ cũ
vẫn dùng được. Ngưỡng không làm script lẻ trở thành được chấp thuận.

Bỏ qua ở ngay dưới root được chỉ định: `skills`, `tools`, `.agent`, `.cvf`, `en`, `archive`,
`tests`, `roadmap`, `packs`, `release_templates`, `dist`. Bỏ qua ở mọi độ sâu: `scripts`,
`_scratch`, `_nguon_dung`, `__pycache__`, `.git`, `.venv`, `venv`, `node_modules`.
Kết quả in cả quy tắc bỏ qua và các thư mục thực sự bỏ qua; không đọc/hash nội dung trong
các vùng đó, kể cả liên kết tại vùng được bỏ qua. Muốn kiểm riêng một vùng, truyền chính
thư mục đó làm root. Root và các thư mục cha phải không qua symlink/junction/reparse point.
Liên kết trong vùng cần quét được báo chưa kiểm, không theo tới đích.

Gợi ý dùng một lần dựa vào tên file, cần người xem quyết định. Nhóm trùng so SHA-256 toàn
bộ bytes của các script lẻ đã đọc, kể cả ở thư mục khác nhau; không so tên hàm, không chứng
minh tương đương thuật toán hay an toàn. Không kiểm dependency, chất lượng mã hoặc đầy đủ
tài nguyên skill. Có kiểm lại file khi đọc nhưng không bảo đảm chống thay đường dẫn đồng
thời; đây là công cụ hỗ trợ sắp xếp, không là ranh giới bảo mật. Không gọi kết quả 0 là
"workspace sạch" hoặc "skill đã đạt".

## new_project.py

Tạo project mới là **bản sao** của bộ mẫu; bộ mẫu chỉ được đọc. Chạy trong bộ mẫu:
`python tools/new_project.py --name "Tên công việc" [--dest THƯ_MỤC_CHA] [--lang vi|en] --apply` (bỏ `--apply` để xem trước).
Project nằm ở `<dest>/<tên>` (mặc định cạnh bộ mẫu). Chỉ chép file của package theo **bản giao chung** của `check_package.py` (cùng danh sách và cùng bytes với `build_release.py` và `adopt_project.py`,
xem mục check_package.py; ở kho nguồn dùng mẫu sạch của thư mục release_templates và MANIFEST tính lại từ bytes thực giao), không chép file người dùng của bộ mẫu.
Nguồn không phải kho nguồn có mẫu sạch hay bộ mẫu chưa khởi tạo nhất quán (hoặc có `.cvf` sai closure) thì bị từ chối, cả khi xem trước, trước khi tạo bất cứ thứ gì. Chép vào thư mục tạm cạnh đích rồi đổi
tên một lần, sau đó chạy `init_project.py` trong bản sao. Thư mục đích đã có thì dừng, không ghi đè; thư mục đã là project hoặc
không còn là bộ mẫu nguyên vẹn thì từ chối. Bảng điều khiển dùng công cụ này ở trang "Tạo project mới".

## setup_wizard.py

Trình hướng dẫn cho người dùng không quen dòng lệnh. Bấm đúp `SETUP.bat` (Windows) hoặc `SETUP.command` (macOS) ở thư mục gốc,
hoặc chạy `python tools/setup_wizard.py`. Ở bộ mẫu, nó hỏi trước: tạo bản sao (mặc định, gọi `new_project.py`) hay dùng chính thư mục này. Khi khởi tạo tại chỗ, nó hỏi ngôn ngữ, tên project và năm thông tin ngắn (mục đích, đầu ra, văn phong,
nguồn, ràng buộc; Enter để bỏ qua), gọi `init_project.py` với các giá trị đó (điền `PROJECT.md`), rồi sao chép đoạn hướng dẫn
dán vào Project/cloud vào clipboard. Nếu có `setup_answers.json` ở thư mục gốc (tải từ form "Khởi tạo nhanh" trong `START_HERE.html`), nó dùng file này và không hỏi lại. Không làm gì nếu thư mục đã khởi tạo. Các giá trị cũng dùng được trực tiếp qua
`init_project.py --purpose --outputs --style --sources --constraints`.

## app.py, app_ui.html

Bảng điều khiển trong trình duyệt. Bấm đúp `APP.bat` (Windows) hoặc `APP.command` (macOS), hoặc chạy `python tools/app.py`
(`--no-browser` để tự mở địa chỉ được in ra, `--port N` để chọn cổng). Máy chủ nhỏ chỉ nghe trên 127.0.0.1, mỗi lần mở có mã truy
cập riêng, không dùng mạng. Mỗi nút gọi một công cụ có sẵn trong thư mục này với tham số cố định (`new_project`, `init_project`, `adopt_project`,
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

Với đúng tám tài liệu hướng dẫn Markdown (`merge_center.REPLACE_ALLOWLIST`: bốn file `docs/HUONG_DAN_*_VI.md` và bốn file `docs/en/*.md`),
cùng cửa sổ so sánh có thêm lựa chọn **Dùng bản mới (giữ .new)** / **Giữ bản của tôi** / **Tự sửa** (D-01b, phạm vi hẹp).
`merge_center.preview_replace()` chỉ đọc và trả hai hash thô của đúng hai buffer vừa đọc; `apply_replace()` chỉ chạy khi gửi lại hai
hash đó, rồi ghi trong một Transaction: lưu `current.txt`, `incoming.txt`, `record.json` vào `.agent/merge-backups/<id>/` và thay bản
hiện hành **sau cùng**. File `.new`, `MERGE_STATUS.json`, MANIFEST và bản HTML đã dựng không đổi, mục vẫn nằm trong danh sách chờ
(không phải "đã giải quyết"). Lấy lại bản cũ là thủ công: mở `current.txt` bằng trình soạn thảo rồi lưu thành file mới; không có nút
hoàn tác. Giao dịch dở thì dùng Tiếp tục/Phục hồi ở trang Tình trạng; Phục hồi bỏ phần sao lưu vừa ghi. Hai route
`/api/merge/preview` và `/api/merge/replace` nằm ngoài lịch sử thao tác. Các nút mở file mặc định trong bảng này đã thay bằng chép
đường dẫn.
Nếu `.new` đúng bytes của baseline đã ghi sau upgrade, chọn bản đó có thể đưa `--verify` về khớp; candidate sửa tay thì vẫn có thể lệch.
Lần upgrade tiếp có thể giữ `.new` cũ dù current đã lên bản sau, hoặc chặn khi pending khác nội dung package mới. Luôn xem lại đúng
hai bản, không coi tên `.new` là bằng chứng đây là package mới nhất. Không tự sửa MANIFEST hoặc xóa pending để bỏ qua kiểm tra.

Cùng tám tài liệu đó còn có nút riêng **Lưu .new và kết thúc chờ** (D-01c, phạm vi hẹp), tách khỏi "Giữ bản của tôi" (chỉ đóng, không ghi) và
"Dùng bản mới". Việc này **giữ nguyên bản hiện hành** (không ghi vào nó) và đưa `.new` khỏi vị trí đang được quét. Cần xem trước riêng
(`merge_center.preview_finish()`, route `/api/merge/finish-preview`): trả hai hash thô, diff từ đúng hai buffer đó và một `finish_id` do máy chủ sinh
(chỉ để tìm lại lần thao tác, không phải quyền). Sau khi thay hoặc tự sửa phải xem trước lại; cặp giống nhau cũng kết thúc được. `apply_finish()`
(route `/api/merge/finish`) làm **hai bước tách rời, không nguyên tử**: (1) một Transaction `merge_finish_archive` lưu `current.txt`, `incoming.txt`,
`record.json` vào `.agent/merge-backups/<finish_id>/` (chỉ tạo file mới); (2) chỉ khi nhật ký đọc được `committed` và ba file đúng hash, MỘT
`os.rename` không thay thế (Windows, cùng ổ đĩa) đưa `.new` thành `pending-retired.txt` trong thư mục đó. Không có xóa, không chuyển ngược, không
`os.replace`/copy; hệ điều hành khác báo không hỗ trợ và vẫn xem/chép đường dẫn được. Kết quả luôn do quan sát file thật quyết định, không suy từ
ngoại lệ: `finished` (nguồn vắng, ô lưu đúng bytes đã chọn, current đúng), `still_pending` (snapshot đã lưu, `.new` chưa chuyển), `partial` (giao dịch
lưu còn dở hoặc chưa chứng minh được; không rename), `conflict`/`unknown` (giữ mọi file để kiểm tay). Route chỉ đọc
`/api/merge/finish-observe` (theo `finish_id` + cặp đã xem) cho phép "Kiểm lại kết quả" khi mất response mà không gửi lại lệnh. Giao dịch lưu còn
dở thì dùng Tiếp tục/Phục hồi ở trang Tình trạng (Tiếp tục không tự chuyển `.new`); giao dịch lưu đã hoàn tất thì Phục hồi không hoàn tác việc
chuyển file. Lấy lại `.new` hoặc bản hiện hành cũ là thủ công: mở file trong thư mục lưu trữ rồi lưu thành file mới. MANIFEST, HTML và
`MERGE_STATUS.json` không đổi; thao tác này không xác nhận nội dung bản hiện hành. Ba route nằm ngoài lịch sử thao tác.

D-01e mở **riêng finish** (không mở replace) thêm sáu file hướng dẫn cho agent: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` và ba file cùng tên trong `en/`.
Máy chủ có hai danh sách tách nhau: `REPLACE_ALLOWLIST` vẫn đúng tám tài liệu, `FINISH_ALLOWLIST` lúc D-01e là tám tài liệu cộng sáu file này (mười bốn path, kiểm
chính xác từng ký tự, không gấp hoa/thường). `preview_replace`/`apply_replace` vẫn từ chối sáu file kể cả khi gửi hash lấy từ finish-preview. `scan()` thêm
`finish_supported` cho mỗi hàng: chỉ là cờ phạm vi để vẽ nút **Giữ bản hiện hành, lưu .new** ngay tại hàng đó (mở thẳng finish-preview, không cần
replace-preview); cờ không phải eligible hay quyền, và máy chủ kiểm lại danh sách của chính nó ở cả ba route. Nội dung `.new` vẫn không được áp vào bản
hiện hành; muốn dùng nội dung mới thì tự sửa bản hiện hành rồi xem trước lại. Nâng cấp vẫn do `upgrade_package` quyết định cập nhật/giữ/xung đột.

D-01g mở **riêng finish** thêm đúng hai script package: `tools/audit_scripts.py` và `skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py`. `FINISH_ALLOWLIST`
nay là mười sáu path (tám tài liệu + sáu entrypoint + hai script), `REPLACE_ALLOWLIST` vẫn tám; hai path này là tuple cố định, không wildcard theo thư mục, không bản `en/`.
Danh sách cho phép **không thay** `managed_paths`: path đúng tên nhưng MANIFEST của project chưa liệt kê vẫn trả `not_managed` trước khi đọc script (MANIFEST
kho nguồn hiện chưa có `tools/audit_scripts.py`, nên ở kho nguồn path này chưa thành managed; MANIFEST không bị làm mới để cho test đạt). Cặp `.new` chỉ được đọc như văn bản
(UTF-8, không NUL, tối đa 256 KiB, như mọi path khác); `.py` chỉ là đuôi tên, không import, biên dịch hay chạy script để xem trước hoặc kết thúc. Kết thúc pending
không chứng minh script đúng, an toàn, chạy được, đã tiếp nhận hay được phép dùng, và không cấp quyền mới. Archive, rename một lần và observe giữ nguyên như D-01c/e.

**Ma trận phạm vi nâng cấp/hợp nhất (D-01f, cập nhật D-01g).** Tổng hợp theo nhóm file và thao tác từ hành vi cùng bằng chứng đã nhận ở D-01a–e (mục tương ứng trong
`.agent/HANDOFF.md` và các test nêu tên; cả hai chỉ có ở kho nguồn). Đây không phải support matrix host của D-02, không phải migration và không đóng P4/D-01/T39.
`finish_supported` chỉ là phạm vi, không phải eligible hay quyền. Số test của từng lượt là lượt riêng, không cộng thành một suite cuối.

| Nhóm file / owner | Hành vi upgrade | Replace / finish | Bằng chứng đã nhận | Giới hạn / gap |
|---|---|---|---|---|
| **Tám guide** đúng `REPLACE_ALLOWLIST`: `docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md`, `HUONG_DAN_SU_DUNG_VI.md`, `HUONG_DAN_SKILLS_VI.md`, `HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md` và bốn file `docs/en/` (`NEW_PROJECT_GUIDE`, `DAILY_USE_GUIDE`, `SKILLS_GUIDE`, `EXISTING_PROJECT_UPGRADE_GUIDE`). File package; owner `merge_center` | `upgrade_package`: ba bên theo MANIFEST; sửa cả hai bên thì lưu `<tên>.new` | **Replace** (D-01b): archive `current.txt`/`incoming.txt`/`record.json` trước, thay current sau cùng, `.new` còn pending. **Finish** (D-01c): giữ current, archive rồi một `os.rename` không thay thế đưa `.new` sang `pending-retired.txt`. Cả hai cần preview (hai hash thô) và xác nhận; finish có observe chỉ đọc | HANDOFF D-01b: `tests.test_panel.MergeReplace*`; D-01c: `tests.test_panel.MergeFinish*`; D-01d: `tests.test_upgrade_lifecycle` (VI replace→finish, EN giữ→finish, cùng schema) | Finish chỉ đo trên Windows/NTFS cùng ổ đĩa; hai bước không nguyên tử; phục hồi thủ công (mở file trong archive, lưu thành file mới), không Undo, không xóa/resolve; MANIFEST và HTML không đổi nên guide đã thay có thể lệch `--verify`. Symlink file thật chưa đo. Không mở allowlist bằng suy luận |
| **Sáu entrypoint**: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` ở gốc và ba file cùng tên trong `en/`. File package; owner `merge_center` | Như file package thường: ba bên theo MANIFEST, xung đột lưu `<tên>.new` | **Replace: từ chối** kể cả khi gửi hash thật. **Finish: có** (D-01e): `FINISH_ALLOWLIST` lúc D-01e = tám guide + sáu path (14; nay 16, xem hàng kế), hàng có nút riêng **Giữ bản hiện hành, lưu .new**, không cần replace-preview | HANDOFF D-01e: `tests.test_merge_entrypoints` (REPLACE8/FINISH14, sáu path preview/finish/observe, replace từ chối), một luồng Chromium (`AGENTS.md`), lifecycle projected-v3 VI+EN ở `AGENTS.md` gốc và `en/AGENTS.md` | Finish không áp instruction mới và không cấp quyền; hết pending không chứng minh host không đọc archive/`.new` hay instruction đã được nghiệm thu. Muốn dùng nội dung mới thì tự sửa current rồi xem trước lại. Cùng hạn chế Windows như guide. Áp instruction mới (P4) chưa nhận; browser và lifecycle chỉ đo `AGENTS.md`, đủ sáu path ở backend; chưa visual QA |
| **Hai script package** (D-01g): `tools/audit_scripts.py` và `skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py`. File package; owner `merge_center` | Như file package thường: ba bên theo MANIFEST, xung đột lưu `<tên>.new`. Path phải có trong MANIFEST của project (managed) | **Replace: từ chối** kể cả khi gửi hash thật. **Finish: có, chỉ hai path này**: `FINISH_ALLOWLIST` = tám guide + sáu entrypoint + hai script (16); allowlist không thay `managed_paths` nên đúng tên mà chưa managed vẫn `not_managed`. Hàng có nút riêng **Giữ bản hiện hành, lưu .new**; chỉ lưu `.new` theo bytes, không import/biên dịch/chạy | D-01g (chờ review, chưa nhận): `tests.test_merge_scripts` (scope và managed, hai script khác/identical, payload không thực thi, từ chối, HTTP, lifecycle VI A→B→finish→C), một luồng Chromium (`tools/audit_scripts.py`), amendment `tests.test_merge_entrypoints` | Hết pending không chứng minh script đúng/an toàn/chạy được/đã tiếp nhận hay được phép dùng; không áp nội dung mới vào current. Đúng hai path: script khác, thư mục `scripts/` khác, bản `en/`, pack, `.cvf` và file lõi không theo suy luận. Cùng hạn chế Windows như guide; lifecycle chỉ VI/projected-v3, browser chỉ `audit_scripts.py`; chưa visual QA |
| **File package khác**: script `tools/*.py` còn lại, tài nguyên skill dùng chung `skills/local/shared/` (gồm script, mẫu, `references/`) trừ `check_spreadsheet.py`, tài liệu và README mẫu trong MANIFEST | Ba bên: cập nhật / thêm / giữ / xung đột → `<tên>.new`. File không còn trong package chỉ được liệt kê (obsolete), không xóa | **Ngoài UI replace/finish hiện tại** (`finish_supported` false; replace và finish từ chối `unsupported`). Chỉ So sánh (chỉ đọc) và chép đường dẫn; xử lý thủ công theo owner và quyền của file. Đường thủ công có sao lưu (M3-C1/F5, không là finish chính thức): so sánh, chép current và `.new` vào thư mục mới `archive/nang-cap/<mã>-<tên>/`, kiểm hash, chuyển (không xóa) `.new` vào đó, khôi phục thành file mới; mô tả và lệnh đã đo ở mục 3 hướng dẫn nâng cấp, đoạn “Cất .new của file khác bằng tay” | HANDOFF D-01a: `tests.test_workflows.UpgradeIdentity` (tập file đổi đúng, skill shared không còn trong package được giữ bytes); D-01d: `tests.test_upgrade_lifecycle` (skill shared tự thêm giữ bytes); D-01b/e: test từ chối path ngoài danh sách | Không coi toàn `skills/` là của người dùng. Lifecycle skill dùng chung do người dùng thêm (ownership, xuất, native) **chưa nghiệm thu**: giữ bytes không giải quyết. Chưa có cách nghiệm thu chính thức để kết thúc `.new` của nhóm này: đường thủ công không đổi MANIFEST, không ghi record hợp lệ, không phải product finish; không có UI hay endpoint mới. Đã đo trên fixture `tools/check_output.py.new` (project 1.8.0 giả đã nâng cấp, Windows/PowerShell): bản chuyển và bản chép khớp byte, current giữ nguyên, nâng cấp lại cùng package báo “Giữ nguyên” và không tạo lại `.new`. Không xóa pending hay sửa MANIFEST để né kiểm tra |
| **File lõi và schema có compatibility guard**: `.cvf/` (closure v3 `CVF_CLOSURE`, máy đọc `CVF_MACHINE`) và năm file `CVF_DEPENDENCIES` (`publish_new`, `context_update`, `transaction`, `result_schema`, `current_draft`). Owner `check_package`, `upgrade_package` | Chưa có `.cvf` thì có thể thêm bản ứng viên; closure v3 cùng bytes máy đọc thì phần tài liệu được so ba bên. Machine/closure không tương thích, phụ thuộc lõi khác bản giao hoặc tài liệu `.cvf` xung đột thì **chặn** cả `--apply --force`, giữ nguyên toàn cây. Tài liệu người dùng sửa mà package không đổi có thể được giữ; không gom thành cập nhật thông thường | Ngoài allowlist UI. Khi guard chặn thì upgrade không ghi hoặc tạo `.new`; không kết luận mọi `.cvf` đều bị chặn | HANDOFF D-01d: `.cvf` lệch + `AGENTS.md.new` giả → preview, `--apply`, `--apply --force` đều rc1 `blocked`, cây giữ; `tests.test_package_v3` (`block_cases`) | Chỉ upgrade và `--force` downgrade **cùng schema** projected-v3 đã đo (nhãn giả, chưa qua ZIP/release/fullgate); chưa migration/downgrade khác schema hay mọi phiên bản lịch sử; force không bỏ guard. T39 tổng thể còn mở |
| **Dữ liệu và file của project**: `USER_FILES` (`PROJECT.md`, `.agent/STATE.md`, `HANDOFF.md`, `INDEX.md`, `SKILL_INDEX.md`, `PENDING_LESSONS.md`, `PACKAGE_INFO.json`, `MERGE_STATUS.json`, `setup_answers.json`, profile `.agent/EXECUTION_PROFILE.json`); nội dung bạn thêm vào `references/`, `working/`, `output/`, `archive/`, `skills/local/project/` (chỉ README mẫu nằm trong MANIFEST); sổ nguồn và artifact. Owner PROJECT / profile / library / artifacts | `USER_FILES` không bị thay bằng bản package trong so ba bên, không tạo `.new`; chỉ thêm mẫu thiếu nếu source MANIFEST khai báo. Nhánh riêng có thể bổ sung dòng skill chung còn thiếu vào `SKILL_INDEX`, cập nhật version/ngày trong `PACKAGE_INFO`; profile thiếu bootstrap theo `PROJECT.md` khi đủ điều kiện (không đổi văn xuôi cũ thành grant). Không tự sao chép nội dung ngoài MANIFEST từ package | Không áp dụng | HANDOFF D-01d: `tests.test_upgrade_lifecycle` (VI/EN) — sổ nguồn raw + projection (2 nguồn/1 entry/2 artifact/2 cạnh), profile/PROJECT/STATE/HANDOFF/INDEX/skill riêng/archive giữ raw; profile `law.execution-profile/2` giữ bytes, `status` UNSUPPORTED, config bị từ chối | Giữ bytes không có nghĩa đọc được schema hay đã migrate; marker native opaque (`RECEIPT_INVALID`) không chứng minh quyền dùng được, STALE hay host. Không tự migrate profile/grant, không nhận hay xuất skill từ việc giữ bytes. Dữ liệu trong bằng chứng là fixture tạm, không phải dữ liệu thật |
| **Gói lĩnh vực đã cài** `skills/local/packs/<tên>/`. Owner `pack.py` | `pack.py update <tên>` xem trước, thêm `--apply` để ghi: khi xung đột, giữ file bạn sửa và lưu bản incoming của gói thành `<tên>.new`; `.new` đang chờ khác bản mới thì dừng trước khi ghi. Ngoài ba bên MANIFEST của `upgrade_package` | Hiện trong Chờ hợp nhất (`origin` domain_pack) nhưng ngoài cả hai allowlist | Test pack/intake riêng (module `tests.test_skill_intake` trong kho nguồn, không vào gói phát hành), ngoài D-01a–e | Chưa nghiệm thu trong D-01. Pending của pack xử lý thủ công theo owner pack |
| **Nhãn version và baseline** (`package_identity`). Owner `upgrade_package` | D-01a: chỉ báo cáo quan hệ nhãn/baseline; `UNKNOWN` không đổi kế hoạch hay writer | Không áp dụng | HANDOFF D-01a: `tests.test_workflows.UpgradeIdentity` | Chỉ metadata: không kiểm toàn vẹn, đường dẫn hay quyền; không ràng buộc apply. Nợ parser legacy (dòng trùng cùng hash, manifest hỏng có thể không có envelope) giữ nguyên. Cùng nhãn version không có nghĩa package/project không đổi |

**Gap chưa nghiệm thu / cần xác nhận.** (1) P4: áp nội dung instruction mới, kết thúc pending ngoài mười sáu path, Undo hay xóa sau commit — chưa có. (2) T39: migration/downgrade khác schema,
project hoặc ZIP thật (D-01d dùng projected-v3 trong thư mục tạm). (3) Vòng đời skill dùng chung do người dùng thêm và pending của pack. (4) Nền tảng: chỉ Windows 11/NTFS/Python 3.11
đã đo; macOS, Linux, Python 3.8 runtime, symlink file thật và visual QA UI chưa. (5) Host support là việc của D-02; C-02 pilot và release chưa mở.

Trang **Tình trạng ứng dụng** đọc phiên bản và loại workspace (`project`, `template` hoặc `unknown`, nhận diện từ nội dung file
chứ không từ tên thư mục), Python, các chức năng tùy chọn kèm lý do và cách khắc phục (`components()`), giao dịch dở (`transaction.incomplete()`)
và 20 dòng lịch sử gần nhất (`ops_log.summary()`). Nút "Tiếp tục" gọi `transaction.py resume`; "Phục hồi" gọi
`transaction.py rollback` và có hộp xác nhận; "Xóa lịch sử" xóa file nhật ký (có xác nhận); "Tạo gói chẩn đoán" ghi một
ZIP trong `.agent/runtime/diagnostics/diagnostics-<thời điểm>.zip`, với đường dẫn thư mục và tên người dùng đã được che, không
có nội dung tài liệu, tên project hay đường dẫn tuyệt đối. Tổng quan hiện một banner khi có giao dịch dở. Mỗi thao tác
bấm từ bảng điều khiển ghi một dòng vào lịch sử (`ops_log.py`); riêng đọc thư viện (`library_find`, `library_stats` và các route `/api/library/*`) không ghi dòng nào.

Trang **Thư viện nguồn** (A-07) dùng đúng bộ phân tích của `library.py` (`read_book`), nên ID, revision, tình trạng và trạng thái file đã ghi giống CLI.
Danh sách, tìm không dấu, lọc nhóm, hồ sơ một dòng và các con số đều lấy từ **sổ đã lưu** qua `/api/library/browse` (từ khóa rỗng thì duyệt hết):
một lần đọc sổ, không quét thư mục, không hash hay đọc nội dung nguồn, không ghi gì. "Có toàn văn" là điều sổ ghi, "Đã ghi: có mặt/không thấy file…" là giá trị
của lần đồng bộ trước; cả hai chưa phải kiểm tra lúc này và chưa xác minh nội dung hay revision hiện tại. Sổ thiếu, không đọc được (hỏng, quyền, bị khóa), thiếu sheet,
thiếu dòng tiêu đề hoặc cột bắt buộc, thiếu openpyxl, lỗi truyền tải và sổ hợp lệ 0 dòng là các trạng thái khác nhau; không trạng thái hỏng nào hiện như "chưa có sổ" hay đề nghị tạo khung. Nút "Mở" và "Sao chép nguồn đã chọn"
gửi lựa chọn gắn với snapshot (SHA-256 các byte của sổ đã đọc), số dòng, ID, revision và đường dẫn đã thấy; máy chủ đọc lại sổ, từ chối khi sổ hoặc dòng đã đổi, rồi mới tiếp tục (`/api/library/open` không nhận đường dẫn thô).
Mở nguồn chỉ cho đường dẫn nằm trong `references/` hoặc thư mục nguồn cũ PROJECT.md đang khai, từ chối đường dẫn tuyệt đối, `..`, liên kết, file thiếu/không quyền/không phải file thường, mỗi lý do một thông báo; đây là kiểm tại lúc mở, không phải mở nguyên tử không theo liên kết,
chỉ nhận phần mở rộng trong `library.FILE_EXT` giống bộ quét nguồn (không đưa script/chương trình/shortcut vào opener); chưa chứng minh quyền đọc ACL thực hoặc hành vi của ứng dụng mặc định với tài liệu Office/HTML được hỗ trợ,
và ứng dụng Office mở file có thể tự sinh file tạm. Sao chép chỉ nhận dòng có ID duy nhất và revision đã ghi; kết quả là văn bản (ID, revision, đường dẫn, tình trạng, xác minh, trạng thái file đã ghi, nhắc đối chiếu), không phải gửi, giao việc hay duyệt, và lựa chọn chỉ tạm trong trang. Lựa chọn giữ qua bộ lọc; trang hiện tổng số đã chọn, số đang ẩn và nút bỏ chọn tất cả.
Mở chi tiết một nguồn còn đọc thêm (B-02) phần "Phụ lục và kết quả liên quan" qua `/api/library/links` (nguồn/phụ lục `RELATED`, các kết quả có `DERIVED_FROM` tới nguồn này kèm trạng thái căn cứ),
rồi "Mở bản này" (`/api/library/artifact-open`) và "Sao chép làm đầu vào" (`/api/library/artifact-copy`); ba route chỉ đọc sổ đã lưu, gắn lại đúng snapshot + ID/revision + đường dẫn + hash đã thấy, không quét, không AI, không ghi sổ hay lịch sử (xem mục `artifacts.py`).
Nút "Cập nhật sổ" chạy `library_sync.plan` (xem trước, không ghi); "Thực hiện" gọi đúng `library_sync.apply` kèm `expected_preview` của bản đã xem (xem mục `library.py`). Khi preview đã biết có x14 hoặc kiểm x14 chưa xong, vẫn xem được kết quả nhưng không hiện "Thực hiện"; guard của writer vẫn giữ. Giao diện chưa hỗ trợ đổi tên (`--rename` vẫn là CLI).

## library.py

Thư viện nguồn trong `references/` (xem skill `source-library`). `init` tạo các thư mục nhóm (legal, policies, templates,
source-documents) kèm README và chép mẫu chỉ mục thành `references/_INDEX.xlsx` nếu chưa có (không ghi đè). `check [--days 180]`
kiểm chỉ mục, báo theo số dòng: thiếu file, file chưa vào chỉ mục, trùng số hiệu, trùng Mã (khi sổ có cột Mã: nêu mã và các dòng, cùng quy tắc với `sync`; sổ cũ không có cột Mã đọc như trước), "Còn hiệu lực" nhưng đã ghi bị thay thế, ngày
kiểm tình trạng quá cũ, mức "Cần đối chiếu", văn bản Mật; mã thoát 1 khi có lỗi. `find <từ khóa> [--group "Pháp luật"] [--all]`
tìm không phân biệt dấu và cho biết có toàn văn hay không. `stats` đếm theo nhóm, tình trạng. `--json` cho bảng điều khiển.
`sync` xem trước file mới, file đổi và file mất trong bốn nhóm nguồn; `sync --apply` ghi ID, hash, revision và trạng thái
vào chính sheet "Danh mục" qua transaction. File đổi làm mức xác minh về "Cần đối chiếu"; sheet "LAW history" giữ metadata
revision trước. Có khóa ghi giữa các lần LAW cập nhật: quyền sở hữu do hệ điều hành giữ trên file index.lock (khóa không chặn), tự nhả khi tiến trình kết thúc hay bị ngắt cứng;
công cụ không đọc hay tin mã tiến trình trong file, không xóa hay ghi đè file khóa để lấy khóa (file khóa cũ của bản trước vẫn dùng được), nên không có bước nào để hai lần chạy xóa khóa của nhau. Trước khi khóa, `index.lock` phải là đúng một file thường có một tên duy nhất (không symlink/điểm phân tích lại, không hard link tới đường dẫn khác, định danh đọc được): chưa có thì tạo mới độc quyền (`O_EXCL`), đã có thì mở không `O_CREAT`/`O_TRUNC` rồi đối chiếu file đang mở, đường dẫn hiện tại và định danh ban đầu, kiểm lại sau khi khóa. Sai ở lần kiểm trước khóa thì dừng trước byte-lock; sai ở lần kiểm sau khóa thì nhả khóa và đóng file trước khi lập kế hoạch hay tạo giao dịch. Cả hai đều dừng với `index.lock`, không xóa hay sửa file khóa (thư mục khóa hoặc file khóa vừa tạo vẫn có thể còn). Existing-open có thể giữ handle ngắn trước khi kiểm và từ chối; đây không phải mở file nguyên tử không theo liên kết. Việc thay file được kiểm tại các lần đối chiếu, không bị ngăn nguyên tử; không bảo đảm phát hiện mọi alias được tạo sau lần kiểm cuối.
Sổ đang mở trong Excel hoặc bị khóa: `sync --apply` dừng, báo "Chưa ghi gì", không để giao dịch dở. Sổ bị sửa và lưu ngoài công cụ giữa lúc đọc và lúc ghi:
không ghi đè (giao dịch dở, `rollback` giữ phần người dùng đã lưu). Nhật ký giao dịch trong `.agent/runtime/transactions` không đọc hoặc không diễn giải được (JSON hỏng, sai schema, trạng thái hay thao tác lạ, lỗi đọc/liệt kê thư mục): `sync --apply` dừng với "Không xác định được…" (mã khác 0, `blocked`, `changes=false`), chưa lập kế hoạch hay tạo giao dịch, không xóa, đổi hay tự phục hồi nhật ký; kiểm hồ sơ rồi mới chạy lại. Xem trước vẫn chạy (chỉ đọc). Giao dịch hợp lệ đang dở vẫn chặn như cũ; không có thư mục giao dịch hoặc chỉ có nhật ký kết thúc hợp lệ (kể cả `rollback_partial`) không chặn. Excel lưu lại làm danh sách thả xuống chuyển sang dạng mở rộng (x14) mà openpyxl không đọc được và sẽ bỏ khi ghi lại sổ; giá trị ô không bị đụng.
`sync` nhận ra dạng này (chỉ chuỗi `x14:dataValidation` trong sheet; bí danh namespace hay phần mở rộng khác chưa nhận ra), xem trước vẫn đọc được và in lưu ý (`notices`), còn `sync --apply` **từ chối trước khi ghi** (mã khác 0, `blocked`, chưa tạo giao dịch hay đổi sổ). Kiểm không hoàn tất cũng từ chối (`x14_scan_incomplete`), không coi là "không có x14". Đây chỉ là từ chối an toàn: công cụ chưa ghi bảo toàn được dạng này, và không tự dựng lại danh sách vì không phân biệt được danh sách bị xóa cố ý với danh sách không đọc được.
Thư mục nguồn cũ chỉ được quét khi người dùng ghi vào dòng "Ngoại lệ thư mục nguồn cũ" của `PROJECT.md` (thư mục trong project,
ngăn bằng `;`; `sync` không bao giờ ghi `PROJECT.md`). Dòng sổ dùng đường dẫn `../<thư mục>/<file>`; thư mục bị bỏ khỏi dòng đó thì
file cũ ghi `OUT_OF_SCOPE`, không bị xóa. Đường dẫn đi qua symlink/junction không được quét; nếu thư mục references hoặc sổ _INDEX.xlsx là
hoặc đi qua symlink/junction thì `sync` (cả xem trước lẫn `--apply`) từ chối trước khi đọc hoặc ghi. README của gói còn nguyên (khớp hash trong
`MANIFEST.sha256`) không vào sổ và `check` cũng không báo nó là “chưa có trong chỉ mục” (cùng điều kiện ownership của `sync`, không loại theo tên file); README do người dùng viết hoặc sửa là một nguồn ở cả hai lệnh. File trùng nội dung ở đường dẫn mới vẫn được ghi
ID mới: cùng hash hay cùng tên chưa đủ chứng minh là file cũ được chuyển. `sync` chỉ in ứng viên đổi tên (đánh dấu mơ hồ nếu một hash
khớp nhiều file); `sync --apply --rename "<ID>=<đường dẫn mới>#<hash>"` (mã in ở bản xem trước, có thể lặp) nối lại ID khi ID đang
MISSING, đường dẫn mới đã được quét và chưa thuộc ID khác, và hash khớp; sai một điều kiện thì không ghi gì. "MISSING" ở đây nghĩa là file
đã mất khỏi phạm vi hiện hành và không còn gì ở đường dẫn cũ: dòng `OUT_OF_SCOPE`, hoặc file cũ vẫn còn nhưng bị bỏ qua (liên kết, file của gói),
không được in ứng viên và không nhận mã `--rename`. Đổi tên kèm đổi nội dung chưa có luồng xem trước → áp dụng.
`sync` không đọc nội dung để xác minh và không chuyển/xóa file nguồn. Cần openpyxl.
`find`, `stats` và bảng điều khiển đọc sổ qua một bộ phân tích (`read_book`): sổ thiếu, không đọc được, thiếu sheet "Danh mục", thiếu dòng tiêu đề (dòng 4) hoặc thiếu cột bắt buộc
(Nhóm, Số/ký hiệu, Trích yếu, Tình trạng, Có toàn văn, Đường dẫn file) dừng với mã khác 0 và `reason` riêng (`index_unreadable`, `index_denied`, `index_missing_sheet`, `index_no_header`, `index_missing_columns`),
không còn thành công với 0 dòng (trước A-07 sổ thiếu dòng tiêu đề cho `find`/`stats` thành công rỗng). Sổ hợp lệ không có dòng và lọc ra 0 kết quả vẫn thành công. Cột `LAW` và ID không bắt buộc để xem sổ cũ. `check` giữ cách báo thiếu cột thành phát hiện.
`library_sync.apply(root, renames=(), expected_preview=None)`: `None` giữ hành vi CLI. Bảng điều khiển luôn truyền `expected_preview` = `{snapshot, sources, scopes}` lấy từ bản xem trước (`preview_binding`: SHA-256 sổ,
hash nguồn theo đường dẫn, phạm vi nguồn cũ; không chứa bytes, ổn định qua JSON). Writer kiểm cấu trúc trước khi chạm khóa, rồi so với kế hoạch tính lại **dưới khóa, trước mọi Transaction**, kể cả khi kế hoạch mới không còn gì để ghi;
thiếu, sai hoặc lệch thì `PreviewMismatch` (`invalid|snapshot|sources|scopes`): LAW không sửa sổ hoặc file nguồn, chưa tạo giao dịch file mới; runtime/khóa và log thao tác có thể đã được tạo. Người dùng xem trước lại. Đây là điều kiện hợp tác để Apply đúng bản đã xem, không phải quyền hay biên nhận; nguồn vẫn đổi trong lúc apply
thì các kiểm tra hiện có tiếp tục áp dụng. Từ chối x14, `x14_scan_incomplete`, nhật ký giao dịch không đọc được, khóa và phục hồi giữ nguyên.

### Nội dung theo phiên bản nguồn và source-event (B-01)

Ghi lại **điều đã đọc** từ một nguồn, gắn với đúng phiên bản nguồn làm căn cứ, rồi tra lại sau này mà không phải đọc lại nguồn. Cùng một sổ `references/_INDEX.xlsx`, cùng writer với `sync`
(`library_sync.locked_commit`: khóa, nhật ký strict, từ chối x14, Transaction `expected_before`); không có database, cache, đồ thị hay giao diện riêng.

- `content preview --request FILE` / `content apply --request FILE --expect-plan TOKEN` ghi **một** entry (`entry_id` do người gọi chọn) vào sheet `LAW content` (A1 = `law.source-content/1`, tiêu đề ở dòng 4, dữ liệu từ dòng 5; sheet chỉ được tạo ở lần `apply` đầu tiên, xem trước và tra không tạo). Request là JSON dữ liệu thuần, khóa lạ bị từ chối:
  `entry_id, source_id, source_revision, source_sha256, locator, read_scope, kind (EXTRACT|FACT|CALCULATION|INFERENCE), text, limits, recorded_by`, tùy chọn `check_level (NOT_CHECKED|DECLARED_CHECK)` kèm `check_scope, check_evidence_ref, checked_by, checked_at`, `user_decision`+`user_confirmation_ref` (đi cùng nhau), `supersedes`.
  Công cụ tự thêm `source_path`, `recorded_at` và ảnh chụp 4 trường ngữ nghĩa của sổ (`basis_status/replaces/replaced_by/effective`). `kind` là loại lời khai, không chứng minh đúng; `DECLARED_CHECK` là lời khai kiểm theo phạm vi, không phải công cụ đã xác minh; công cụ không chứng thực `user_confirmation_ref` và không cấp quyền hay nghiệm thu.
  Điều kiện ghi: SourceID duy nhất, `source_revision`/`source_sha256` kỳ vọng khớp sổ **và** bytes file đang đọc (chỉ file được khai, không quét thư viện); cùng revision mà ngữ nghĩa/SHA trong sổ đã khác lúc entry cũ được ghi thì `UNVERSIONED_SEMANTIC_CHANGE`, cần source-event trước.
  Cùng `entry_id` + cùng payload → `already_recorded` (không ghi); khác payload → `ENTRY_CONFLICT`. Sửa, kiểm lại hay đổi quyết định = `entry_id` mới với `supersedes` trỏ entry trước cùng SourceID chưa bị thay; dòng cũ không bị sửa, dòng mới không kế thừa kiểm hay quyết định.
- `source-event preview|apply --request FILE [--expect-plan TOKEN]`: `event_id, source_id, expected_revision, expected_sha256, mode, changes, reason, evidence_ref, recorded_by`. `mode=semantic_update` chỉ nhận `changes` trong `status/replaces/replaced_by/effective` và không đổi giá trị thì là `no_change` (không tăng revision);
  `mode=reconcile_manual_edit` version hóa phần người dùng đã sửa tay trong Excel (có thể `changes` rỗng). Có event thật thì revision tăng đúng 1 dù SHA giữ nguyên, mức xác minh về "Cần đối chiếu" và `LAW file state` về `NEEDS_REVIEW`. Lịch sử ghi ở `LAW history`: giữ 5 cột cũ và dòng cũ, thêm cột
  EventID/loại/revision mới/lý do/chứng cứ/người/payload literal/**ObservedBefore** (4 trường ngữ nghĩa nhìn thấy lúc event, không phải metadata chắc chắn của revision trước). Cùng `event_id` + cùng payload → `already_recorded` kèm revision lịch sử (`current_basis_validated=false`: không xác nhận căn cứ hiện tại); khác payload → `EVENT_CONFLICT`.
  Layout lịch sử lạ hoặc EventID trùng → `UNSUPPORTED_HISTORY`, không ghi đè. `sync` thường giữ định dạng đã mở rộng (dòng `BYTES_CHANGED`) và các event.
- `TOKEN` của `apply` là SHA-256 của payload chuẩn hóa + bytes sổ lúc xem trước + quan sát nguồn/revision/ngữ nghĩa; dưới khóa kế hoạch được tính lại, lệch (sổ, file khai báo hoặc yêu cầu đổi) thì `PreviewMismatch(reason='plan')`, chưa tạo Transaction. Token không phải quyền hay biên nhận.
- `content find [từ khóa] [--source-id ID] [--entry-id ID] [--json]` **chỉ đọc sổ**: không quét, không hash, không mở nguồn, không OCR, không model, không mạng. Mỗi entry trả đủ provenance, kiểm, giới hạn, quyết định và các chiều độc lập `basis_state`
  (`CURRENT_CATALOG_BASIS | NEEDS_REVIEW | BASIS_CONFLICT | MISSING_BASIS | MISSING_SOURCE`, kèm `basis_reason`), `superseded_by`, `recorded_file_state`, `bytes_observation` (luôn `UNOBSERVED`), `source_path` đã ghi và `current_source_path` hiện tại. `CURRENT_CATALOG_BASIS` chỉ nghĩa là khớp sổ hiện tại,
  không chứng minh bytes hiện tại, hiệu lực hay nội dung đúng; dùng lại hay trích dẫn vẫn mở và kiểm file thật theo skill `source-library`. Trạng thái là view tính từ SourceID + revision/SHA/ảnh chụp ngữ nghĩa, không có cờ "stale" ghi đè. Nguồn A đổi chỉ làm entry của A cần xem lại; đổi tên thuần qua `sync --rename` giữ căn cứ.
- Văn bản trong request (kể cả bắt đầu bằng `=`, `+`, `-`, `@`, URL, câu như chỉ thị) lưu và đọc **literal**: không công thức, hyperlink, macro, mạng hay lệnh. Sheet `LAW content` thiếu marker/cột đúng, có công thức ở ô được quản lý, trùng khóa hoặc `supersedes` sai → `MALFORMED_CONTENT_SHEET`, không coi là rỗng rồi dựng lại; ô quá giới hạn Excel hoặc ký tự điều khiển bị từ chối, không cắt bớt.
- API tương ứng (không cần phân tích stdout): `library.content_find(root, query, source_id, entry_id)`, `library_sync.content_plan/content_apply(root, request, expect_plan)`, `library_sync.event_plan/event_apply`, `library_sync.load_request(path)`; lỗi là `library.ContentError` (có `.code`) hoặc `SyncError`.
  Chưa có: giao diện nội dung B-01 trên bảng điều khiển, đọc lại bytes của revision cũ, kiểm nội dung hay chống prompt injection của agent đang chạy. Phiên bản kết quả và quan hệ nhiều nguồn/nhiều output xem B-02 bên dưới.

## artifacts.py (B-02: phiên bản kết quả và quan hệ nguồn–phụ lục–kết quả)

Giúp phiên sau tìm và mở đúng báo cáo đã lưu, thấy nguồn, phụ lục và kết quả nối với nhau thế nào, dùng kết quả làm đầu vào mới mà không mất căn cứ và giới hạn, và biết khi nguồn đổi thì kết quả nào cần xem lại.
Không có database, graph engine, cache, sidecar hay ContentID: chỉ **hai sheet lazy** trong chính `references/_INDEX.xlsx` và một module. Ghi qua đúng `library_sync.locked_commit` (khóa writer, Pins, nhật ký strict, từ chối x14, Transaction `expected_before`) với plan token; các writer khác (`sync`, `content`, `source-event`) giữ nguyên và từ chối ghi khi hai sheet này hỏng cấu trúc.

```text
python tools/artifacts.py find [từ khóa] [--artifact-id ID] [--source-id ID] [--revision N] [--json]      chỉ đọc sổ
python tools/artifacts.py register preview --request FILE | apply --request FILE --expect-plan TOKEN         một phiên bản kết quả + phụ thuộc trực tiếp
python tools/artifacts.py relate   preview --request FILE | apply --request FILE --expect-plan TOKEN         RELATED nguồn↔nguồn
python tools/artifacts.py prepare --request FILE [--json]       đọc/hash lại closure để dùng làm đầu vào mới (không ghi)
python tools/artifacts.py open --artifact-id ID --revision N [--expect-snapshot HEX]
python tools/artifacts.py copy --artifact-id ID --revision N [--expect-snapshot HEX] [--lang vi|en]
```

Thêm `--project DIR` để trỏ project khác. API tương ứng: `artifacts.find/links/prepare`, `register_plan/register_apply`, `relate_plan/relate_apply`, `open_artifact`, `copy_input`, `load_book`; lỗi là `library.ContentError` (có `.code`) hoặc `SyncError`, ngoại lệ `PreviewMismatch` khi plan token lệch.
Mã thoát CLI: 0 xong; 1 từ chối hoặc lỗi; 2 sai cách dùng.

**Layout (lựa chọn thi công).** Sheet tạo ở lần `apply` đầu tiên, cả hai cùng lúc; sổ cũ thiếu cả hai là legacy hợp lệ (xem trước, `find`, `links`, `prepare` không tạo gì). Chỉ có một trong hai sheet là lỗi cấu trúc `ARTIFACT_SHEETS_INCOMPLETE`, không coi là rỗng.
A1 = marker, tiêu đề ở dòng 4, dữ liệu từ dòng 5, chỉ thêm dòng:

- `LAW artifacts` (marker `law.artifacts/1`): `artifact_id, revision, predecessor, path, sha256, size, title, kind, limits, origin, publish_rid, publish_identity, recorded_by, recorded_at`. Khóa duy nhất `(artifact_id, revision)`; `revision` là số nguyên dương nối tiếp từng bước (`revision = bản mới nhất + 1`, `predecessor` là bản đó), `path` dưới `working/` hoặc `output/`, mỗi phiên bản một file riêng (không dùng lại path của bản cũ kể cả khác hoa thường), tên file quyền như `AGENTS.md` bị từ chối.
  `kind ∈ REPORT|APPENDIX|OTHER|EXTRACT|FACT|CALCULATION|INFERENCE` và `limits` (bắt buộc) do người gọi **khai**; không xác minh nội dung. `origin ∈ P_CN1|USER_FILE`.
- `LAW relations` (marker `law.relations/1`): `relation_key, type, from_kind, from_id, from_revision, to_kind, to_id, to_revision, to_sha256, basis_status, basis_replaces, basis_replaced_by, basis_effective, recorded_by, recorded_at`.
  Chỉ hai loại tham chiếu: `SOURCE` (SourceID) và `ARTIFACT` (ID + revision). `RELATED` chỉ nối hai SourceID (ghi theo thứ tự tăng dần, không mang revision hay căn cứ, không truyền stale). `DERIVED_FROM` nối một phiên bản kết quả tới nguồn (chụp revision, SHA-256 và 4 trường ngữ nghĩa của sổ lúc đăng ký, như B-01) hoặc tới phiên bản kết quả đã đăng ký (khóa đúng ID/revision/SHA);
  nhiều input cho một output là nhiều dòng, nhiều output là nhiều lần đăng ký. Mỗi cạnh `DERIVED_FROM` được tạo cùng lúc với phiên bản của nó và bất biến; thêm/sửa/xóa quan hệ của phiên bản đã đăng ký là `ARTIFACT_CONFLICT` (B-02 chưa có xóa hay sửa lịch sử quan hệ). `relation_key` là JSON chuẩn hóa của khóa cạnh, công cụ kiểm lại khi đọc.
- Giá trị chữ lưu **literal** (kể cả bắt đầu bằng `=`, `+`, `-`, `@`); ô quá giới hạn Excel hoặc ký tự điều khiển bị từ chối, không cắt bớt.

**Đọc và kiểm cấu trúc.** `parse_registry` kiểm marker, tiêu đề, khóa, giá trị bắt buộc, literal (công thức trong ô quản lý là lỗi), cấu trúc cạnh, trùng, chu trình và phiên bản bị treo (`MALFORMED_ARTIFACT_SHEET`, `MALFORMED_RELATION_SHEET`, `ARTIFACT_DANGLING`, `ARTIFACT_CYCLE`); không dedupe dữ liệu hỏng để biến thành hợp lệ.
SourceID hoặc căn cứ **lịch sử không còn khớp sổ hiện tại chỉ là diagnostic** (không làm sổ hỏng, không chặn `sync` hay source-event tăng revision). Closure duyệt hữu hạn (`MAX_DEPTH`=32, `MAX_NODES`=200); vượt giới hạn là lỗi `CLOSURE_LIMIT`, không cắt.

**`find` (chỉ đọc sổ một lần: không quét, không hash nguồn hay file, không mở file, `bytes_observation` luôn `UNOBSERVED`).** Mỗi phiên bản trả khóa `ID@revision`, các trường đã ghi, `superseded_by`/`latest_revision`, `dependency_state` và các cạnh từng bước (`state`, `reason`), `diagnostics` (cạnh không còn hiện hành), `lineage` (từng tổ tiên với `kind`, `limits`, `origin`, có khai căn cứ hay không), `unknown_basis`, `inference`, `openable` và `pick` (lựa chọn gắn snapshot).
`dependency_state`: `CURRENT_CATALOG_BASIS` (căn cứ đã khai còn khớp sổ và không có tổ tiên chưa khai căn cứ, chưa kiểm bytes), `NEEDS_REVIEW` (nguồn có revision mới hơn, hoặc kết quả nguồn đã có bản mới: `upstream_superseded`), `BASIS_CONFLICT`, `MISSING_BASIS`, `MISSING_SOURCE`, `NO_DECLARED_BASIS` (cả kết quả hoặc một tổ tiên chưa khai căn cứ: xem `unknown_basis`; **không** là verified hay CURRENT). Căn cứ stale/missing/conflict đã biết vẫn ưu tiên hơn unknown, không được hạ xuống unknown.
Một source-event giữ nguyên SHA vẫn tăng revision nên A→B→C vẫn `NEEDS_REVIEW`. B1 được C1 tham chiếu vẫn là B1 khi có B2: cạnh không chuyển sang B2, B1 hiện `superseded_by` và C1 `NEEDS_REVIEW`. C mang `kind=REPORT` không xóa nhãn `INFERENCE`, `limits` hay phần chưa khai căn cứ của B; đây là khai báo và dấu vết, không phải xác minh nội dung, hiệu lực hay duyệt.

**Đăng ký (`register`).** Request JSON thuần, khóa lạ bị từ chối: `artifact_id, revision, path, title, kind, limits, origin, recorded_by`, tùy chọn `predecessor`, `sha256` (phải khớp bytes quan sát), `rid` (chỉ `P_CN1`, 32 hex) và `dependencies` (tối đa 50 mục `{kind, id, revision, sha256}` trực tiếp).
`preview` chỉ đọc sổ, file kết quả và closure đã khai; `apply --expect-plan TOKEN` tính lại dưới khóa, token buộc payload, bytes sổ và quan sát (file, nguồn, closure), lệch thì `PreviewMismatch` trước mọi Transaction; `recheck` có kiểu đọc lại hash nguồn và file kết quả ngay trước ghi (`library_sync.commit_planned.recheck` chỉ hỗ trợ nguồn nên không dùng).
Cùng khóa + cùng payload → `already_recorded` (không thêm dòng, không đọc nguồn, `current_basis_validated=false`); khác payload → `ARTIFACT_CONFLICT`. Đăng ký không ghi bytes kết quả, không đổi grant, nghiệm thu, TASK, RESULT hay Nháp hiện tại.
- `origin=P_CN1`: dùng `rid` và bằng chứng của owner đã pin (`current_draft`), không tạo receipt hay đổi pins. Phải khớp đúng đường dẫn/digest của lần xuất bản, file hiện tại vẫn khớp bằng chứng, và mọi input của closure cùng **snapshot sổ thô** (`references/_INDEX.xlsx`) đã nằm trong `prepared.inputs` của lần xuất bản với đúng digest/`source_id`/revision.
  Sổ hoặc nguồn đổi sau đó (`STALE_SOURCE_BASIS`, `REGISTRY_CHANGED_SINCE_PREPARE`, `INPUT_NOT_IN_PREPARED`, `WORKBOOK_NOT_IN_PREPARED`, `TARGET_NOT_MATCHING`, `OWNER_UNAVAILABLE`…) thì **từ chối đăng ký**, giữ file và receipt, thông báo "đã tạo, chưa đăng ký"; không rebase, không dựng lịch sử, không publish lại. Sau khi đăng ký làm đổi sổ, `find` so căn cứ thực thể đã lưu, không đòi digest sổ thô trước đăng ký.
- `origin=USER_FILE`: đăng ký file báo cáo đã có bằng quan sát bytes/đường dẫn hiện tại (từ chối thiếu, liên kết/reparse, không phải file thường, file nhiều tên), không giả lịch sử tạo, receipt hay nguồn đã dùng. Không khai `dependencies` thì `NO_DECLARED_BASIS`.
- `relate`: `source_a, source_b, recorded_by`; hai SourceID phải có đúng một dòng trong sổ; cùng cặp là `already_recorded`.

**Dùng làm đầu vào (`prepare`, `copy`, `open`).**
- `prepare --request FILE` với `{"inputs": [{"kind":"ARTIFACT","id","revision"[, "sha256"]}, {"kind":"SOURCE","id"}], "expected_snapshot"?}` đọc/hash lại **finite closure ngay lúc dùng** (bắt cả nguồn đổi bytes mà chưa sync sau khi chọn). Căn cứ đã biết cũ/thiếu/xung đột, phiên bản đã có bản mới hơn (`UPSTREAM_SUPERSEDED`), file kết quả đổi hoặc mất đều bị từ chối, không hạ thành "unknown" để vượt kiểm.
  Trả `snapshot` sổ và `inputs` (path/digest/`source_id`/revision, cùng dòng `references/_INDEX.xlsx` của snapshot) đúng dạng `request.inputs` của P-CN1/A-11, kèm `unknown_basis`, `inference`, `limits`. Không có store hay receipt prepare; guard publish (`INPUT_CHANGED_SINCE_READ`) bắt thay đổi sau prepare; checkpoint và quyền vẫn hợp tác, không phải enforcement.
  `NO_DECLARED_BASIS` có thể dùng như tài liệu do người dùng cung cấp nếu bytes/đường dẫn còn đúng, nhưng unknown/limits được truyền xuống và không bao giờ gọi là CURRENT hay verified.
- `copy` gắn khóa, đường dẫn, hash đầy đủ, snapshot, căn cứ, `kind` và `limits` của cả dòng tổ tiên vào văn bản sao chép; chỉ sao chép, không giao việc, không chọn Nháp hiện tại, không ghi gì. Nhắc chạy `prepare` ngay trước khi dùng.
- `open` rebind snapshot + ID/revision + đường dẫn + hash, rồi **quan sát file đích ngay trước khi gọi opener**. Bản lịch sử có nguồn đã cũ vẫn mở nếu file còn đúng; thiếu/đổi/liên kết/file nhiều tên/identity khác thì từ chối kèm lý do (`stale`, `changed`, `file_changed`, `missing`, `link`, `hardlink`, `identity_conflict`, `owner_unavailable`, `unsupported_type`…), không có `ack`, không tự chạy AI.
  Với P-CN1 dùng bằng chứng và identity của owner; với `USER_FILE` chỉ khẳng định đã quan sát đúng bytes. Danh sách mở giữ `.docx .xlsx .pptx .pdf .txt .md .csv` như `current_draft` (`.html` lưu được nhưng `unsupported_type`, không thêm opener). `OPENED` chỉ nghĩa đã yêu cầu hệ điều hành mở, không phải kiểm Office hay chỉ-đọc. Biến TEST ONLY `LOCAL_AGENT_WORKSPACE_TEST_OPEN_LOG` của `current_draft` cũng áp dụng.

**Giới hạn đã biết.** Windows + NTFS cục bộ, hợp tác/ADVISORY: quan sát tại thời điểm, không chống đua hay sửa ngoài và không nguyên tử giữa đọc file và ghi sổ (cửa sổ ngắn còn lại ở bước kiểm trước Transaction). Dùng hàm riêng tư của `current_draft` (`Env`, `_candidate`, `_judge`, `_facts`) cho bằng chứng P-CN1, nên đổi chúng phải kiểm lại đây.
Chưa có: ghi/sửa/xóa lịch sử quan hệ, đăng ký muộn có dựng lịch sử, giao diện đồ thị hay ghi registry trên bảng điều khiển, kiểm nội dung hay Office, stop/timeout/retry (B-03), migration (D-01).

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
Profile `.agent/EXECUTION_PROFILE.json` (xem `execution_profile.py`): đã có thì giữ nguyên từng byte, kể cả lỗi hoặc phiên bản lạ, chạy lại không đặt lại; chưa có thì chỉ tạo khi `PROJECT.md` có đúng một dòng quyền gọi agent phụ (owner PROJECT, chưa có grant; dòng văn xuôi cũ được báo cần migration, không bị đọc thành quyền). Dòng thiếu, trùng hoặc đã là con trỏ mà thiếu profile thì không tạo gì, nêu lý do và bước xử lý cụ thể (`execution_profile.next_steps`, in cả ở `status`/`preview-config` và trong `next_actions` JSON): thiếu dòng thì người dùng chọn dòng “Không có”/“None” rồi xem trước và áp dụng upgrade bằng package mới; con trỏ mất profile thì khôi phục đúng profile từ bản sao lưu, không có bản sao lưu thì giữ chặn và chờ chủ sở hữu quyết định riêng. Không bước nào tạo profile mẫu, đặt lại grant hoặc dùng `init_project.py --force`.

## upgrade_package.py

Nâng cấp một project lên bản package mới mà không ghi đè việc của bạn. Mặc định chỉ báo cáo; thêm `--apply` mới ghi.

```text
python tools/upgrade_package.py --project "đường dẫn project cũ"        # chạy từ thư mục package MỚI
python tools/upgrade_package.py --from "đường dẫn package mới" --apply  # chạy từ project
```

So ba bên bằng `MANIFEST.sha256`: file chưa ai sửa thì cập nhật, file mới thì thêm, file bạn đã sửa thì giữ nguyên; nếu bạn sửa và
package cũng đổi thì lưu bản mới thành `<tên>.new`. Không đụng file của người dùng (PROJECT, STATE, INDEX, `references/`...), không xóa file nào.
Từ chối chạy trên thư mục chưa khởi tạo (có thể là thư mục nguồn của package) trừ khi có `--allow-uninitialized`.
**Kiểm tương thích `.cvf` trước mọi thay đổi** (chạy cả khi xem trước; `--apply`/`--force` không vượt qua được; chỉ đọc cấu trúc và bytes, không chạy mã của đích): nguồn phải là package đầy đủ có MANIFEST khớp file thật
(dùng thư mục giải nén từ ZIP, không dùng kho nguồn) và `.cvf` đúng closure v3; đích hoặc chưa có `.cvf` (thêm bản ứng viên) hoặc đã đúng closure v3 cùng byte máy đọc. `.cvf` thuộc phiên bản khác/trộn/thiếu file/đã đổi chính sách
hay module, file công cụ lõi (`publish_new`, `context_update`, `transaction`, `result_schema`, `current_draft`) đã bị sửa, hoặc tài liệu `.cvf` bạn sửa mà package cũng đổi ⇒ chặn, giải thích, giữ nguyên toàn cây; không tạo `.new` rồi coi là xong, không chuyển đổi tự động.
File lõi còn nguyên bytes của một bản package cũ (project cũ như 1.8.0 chưa ai sửa; thuộc nhóm "cập nhật") không bị chặn: chính giao dịch nâng cấp thay nó bằng bytes bản giao; file đã bị sửa vẫn chặn kể cả `--force`.
Mọi file sẽ ghi gắn `expected_before` = hash thô của đúng bytes `plan()` đã đọc để phân loại (file chưa có thì `None`): file lưu lại sau lúc lập kế hoạch và trước `Transaction.add` bị từ chối ("CHƯA GHI GÌ", `blocked`, chưa tạo giao dịch), không bị ghi đè. Đã đo bằng controlled interleaving (không phải race kernel): `tests.test_upgrade_lifecycle.OlderCoreDependency`.
Thông báo chặn và `next_actions` (cả `--result-json`) nêu bước xử lý từng loại (nguồn không nguyên vẹn, hạ phiên bản, `.cvf`/file lõi bị sửa, `.new` đang chờ khác nội dung); không khuyên xóa `.new`, sửa MANIFEST hay dùng `--force`: `--force` chỉ bỏ so nhãn phiên bản, không bỏ các chặn `.cvf`/nguồn.
Project chưa có `MANIFEST.sha256` bị từ chối khi so sánh (nâng cấp tay theo hướng dẫn). Việc ghi (`--apply`) chạy qua một giao dịch
có nhật ký: nếu bị gián đoạn, công cụ báo CHƯA HOÀN TẤT và các lần chạy sau bị chặn cho đến khi `transaction.py` resume hoặc rollback.
`.agent/EXECUTION_PROFILE.json` không nằm trong MANIFEST nên không bao giờ bị cập nhật hay tạo `.new`; project chưa có thì được bootstrap theo `PROJECT.md` như `init_project.py` (không đổi văn xuôi cũ thành grant). Schema `.agent/EXECUTION_PROFILE.schema.json` và `tools/execution_profile.py` là file package, cập nhật như file thường.

Báo cáo in thêm một dòng `[QUAN_HỆ]` và kết quả có cấu trúc (`--result-json`: preview, success và blocked sau khi đã đọc MANIFEST) mang thêm đối tượng `package_identity`; `from_version`, `to_version` và các trường cũ giữ nguyên.
`relation` là một trong `SAME_LABEL_DIFFERENT_BASELINE`, `SAME_LABEL_SAME_BASELINE`, `DIFFERENT_LABEL_SAME_BASELINE`, `DIFFERENT_LABEL_DIFFERENT_BASELINE`, `UNKNOWN`; `version` có `installed`, `source`, `same`; `baseline` có `installed`, `source` (mỗi bên `state` KNOWN/UNKNOWN, `entries`, `digest` `sha256:...`, `reason`) và `same` (true/false/null).
Baseline là digest của tập entry (đường dẫn, hash) hợp lệ trong `MANIFEST.sha256`, sắp theo đường dẫn, nên không đổi theo EOL hay thứ tự dòng; nó không phải hash cả project, không chứng minh nguồn, an toàn hay hiệu lực nội dung, và cùng baseline vẫn có thể còn file thiếu, bootstrap hoặc dòng index cần thêm. Manifest thiếu/không đọc được/hỏng dòng/trùng đường dẫn/mơ hồ so với bộ đọc của công cụ thì `UNKNOWN` kèm `reason`, `relation` là `UNKNOWN` và `baseline.same` là `null`; không suy từ nhãn. Chỉ là mô tả: không đổi kế hoạch, quy tắc ghi hay kiểm tương thích. Baseline gồm cả `en/`; KNOWN không là integrity/path/authority check. Dòng trùng cùng hash hiện có thể vẫn được owner cũ nhận dù identity UNKNOWN. Manifest hỏng có thể lỗi trước khi có envelope/identity; tranche này không đổi parser. `DIFFERENT_LABEL_SAME_BASELINE` chủ yếu dành cho manifest tùy biến không ghi VERSION; package thường có VERSION trong manifest. Identity không phải snapshot ràng buộc apply.

Từ bản 1.4.0, `.agent/SKILL_INDEX.md` (file của bạn, không bị ghi đè) được **thêm** các dòng skill dùng chung còn thiếu của package mới để agent tìm thấy skill mới; dòng đã có không bị sửa. Project đang ở bản cũ hơn bản 1.4.0 nên chạy script từ thư mục package MỚI (cách thứ nhất ở trên), vì bản script nằm trong project còn cũ.

## adopt_project.py

Đưa package vào một project ĐÃ CÓ lần đầu (chưa có `VERSION`/`.agent/`). Mặc định chỉ báo cáo; thêm `--apply` mới ghi.

```text
python tools/adopt_project.py --project "đường dẫn project cũ" --name "Tên project" [--lang vi|en] [--purpose "..."] [--apply]   # chạy từ thư mục package
```

Chỉ thêm file còn thiếu; không xóa, không ghi đè file của bạn. Danh sách và bytes lấy từ **bản giao chung** của `check_package.py` (không còn duyệt thư mục riêng): không đưa `release_templates`, `roadmap`, `tests`, dữ liệu người bảo trì
hay `.cvf` v1/v2 vào project; nhận diện đơn vị có sẵn của bạn trong `assets/` được giữ. Cùng quy tắc kiểm tương thích `.cvf` như `upgrade_package.py` (chạy trước mọi thay đổi; chặn cả `--apply`). Nguồn là project đã khởi tạo thì bị từ chối.
`AGENTS.md`/`CLAUDE.md`/`GEMINI.md` cũ vẫn giữ nguyên và có hiệu lực;
bản package khác nội dung được lưu `<tên>.new` để hợp nhất. Áp dụng cả khi chọn tiếng Anh. File `.new` đã có nội dung khác sẽ chặn thao tác trước khi ghi.
File khác trùng tên và khác cũng giữ của bạn, bản package lưu `<tên>.new`. Skill riêng sẵn có trong
`skills/local/project/` được thêm dòng vào `.agent/SKILL_INDEX.md` với Status `REVIEW` (công cụ ghi nhận, không tự tiếp nhận; người dùng xác nhận rồi đổi sang `AVAILABLE`). Cuối cùng chạy `init_project.py`. Từ chối chạy nếu project đã có package (dùng `upgrade_package.py`). Việc ghi chạy qua một giao dịch có nhật ký; sau đó công cụ
chạy `init_project.py` (nằm ngoài giao dịch). Nếu `init_project.py` lỗi, kết quả là `partial`: chạy lại
`python tools/init_project.py --name "Tên project" --lang vi --force`.
Profile `.agent/EXECUTION_PROFILE.json` của project đã có thì giữ nguyên từng byte, không tạo `.new`; chưa có thì mẫu sạch chỉ được thêm cùng `PROJECT.md` mẫu (con trỏ), còn lại `init_project.py` bootstrap theo `PROJECT.md` hiện có.

## execution_profile.py

Profile project (A-09): lựa chọn **được yêu cầu** (host, model hoặc tier, effort, fallback chỉ khi người dùng chọn, giới hạn) và chủ sở hữu quyền gọi vai. Chỉ xem và chỉnh qua công cụ này; chưa có adapter nên không có gì được báo là đã đăng ký, đã áp dụng hay gọi được.

```text
python tools/execution_profile.py status [--project DIR]
python tools/execution_profile.py preview-config    --choices FILE
python tools/execution_profile.py apply-config      --choices FILE [--expect-plan SHA]
python tools/execution_profile.py preview-migration --grants FILE
python tools/execution_profile.py apply-migration   --grants FILE --expect-plan SHA
```

- **File.** `.agent/EXECUTION_PROFILE.json` thuộc project (không vào MANIFEST; bản giao luôn là mẫu sạch: owner `PROFILE`, không lựa chọn, không grant). `.agent/EXECUTION_PROFILE.schema.json` và công cụ này thuộc package, một schema dùng chung cho VI/EN. Công cụ chỉ dùng schema cố định của package đang chạy (`.agent/EXECUTION_PROFILE.schema.json` và `.cvf/contracts/v3/control.schema.json`), không nhận `$schema`/`$ref`/đường dẫn schema từ dữ liệu, không dùng mạng; thiếu `jsonschema>=4.18` thì báo `UNVALIDATED` và không ghi gì phụ thuộc việc kiểm.
- **`status`** chỉ đọc. Trạng thái: `OK`, `LEGACY` (còn dòng quyền dạng văn xuôi cũ, cần migration), `PROFILE_ABSENT`, `INVALID`, `UNSUPPORTED` (phiên bản lạ/tương lai), `UNVALIDATED`, `OWNER_CONFLICT`, `PROJECT_LINE_MISSING`/`PROJECT_LINE_AMBIGUOUS`, `TRANSACTION_UNFINISHED`/`TRANSACTION_UNKNOWN` (mọi giao dịch dở chặn luồng profile; nhật ký không đọc được không được coi là "không có"). Mỗi vai lõi hiện `config` (yêu cầu/chưa cấu hình), `applied` và `registration` (luôn `NOT_INSPECTED`: helper không đo host nên không phủ định cũng không khẳng định), `permission` (`NO_GRANT`, `GRANT_CLAIMED`, `LEGACY_UNMIGRATED`, `BLOCKED`). `GRANT_CLAIMED` chỉ là lời khai trong profile: không chứng thực, không xét hạn, không có nghĩa host cho phép.
- **Một owner quyền.** `authority_owner` là `PROJECT` (quyền nằm ở dòng "Phạm vi được giao cho agent phụ" của `PROJECT.md`, `grants` phải rỗng) hoặc `PROFILE` (grant nằm trong profile, dòng `PROJECT.md` chỉ còn con trỏ). Hai nơi cùng giữ quyền hoặc con trỏ lệch owner ⇒ `OWNER_CONFLICT`, không dùng nơi nào. Grant là record `grant` v3 chuẩn của `.cvf` (không có `allow_*` hay bộ đánh giá phạm vi thứ hai); `profile_ref` của checker vẫn `UNSUPPORTED`.
- **Giữ nguyên.** Profile lỗi, phiên bản lạ hoặc mâu thuẫn owner luôn giữ nguyên bytes: công cụ không sửa, chuẩn hóa hay đặt lại, và `init/adopt/upgrade` không đặt lại. Không có khóa, token, tài khoản, phiên, `observed`/receipt trong profile (schema đóng; giá trị giống khóa bị từ chối).
- **Config** (`preview-config`/`apply-config`): `--choices` là JSON chỉ có `host`, `roles` (từng vai lõi: `model` hoặc `tier`, `effort`), `fallback`, `requested_limits`. `grants`, `authority_owner`, `schema_version` hay trường lạ bị từ chối; sửa lựa chọn không đụng `roles/*/agent.md|checks.md|config.json`. Lựa chọn là yêu cầu, không phải xác nhận host đã áp dụng; `requested_limits` không mở rộng grant. Preview gắn hash toàn bộ `PROJECT.md` làm precondition chỉ đọc: sửa bất kỳ dòng nào sau preview thì `--expect-plan` cũ bị từ chối với `PLAN_CHANGED`; xem trước lại. Config không ghi `PROJECT.md`.
- **Migration** (`preview-migration`/`apply-migration`): chuyển quyền từ dòng `PROJECT.md` sang grant trong profile. `--grants` là mảng record grant v3 chuẩn, mỗi record đã có `issuer_ref.attribution` `USER_CONFIRMATION` (kênh `USER_MESSAGE`/`HOST_CONFIRMATION_UI`/`USER_AUTHORED_FILE`, kèm `evidence_locator`), `status` `ACTIVE`, không `example_only`. Công cụ **không** tạo, dịch hay xác nhận hộ: v1/v2, văn xuôi, ví dụ, vô hiệu, nguồn Main/role hay thiếu khai báo đều bị từ chối trước mọi thay đổi. Evidence chỉ là lời khai hợp tác do người gọi cung cấp. Xem trước nêu đúng thay đổi profile và dòng `PROJECT.md` sẽ thành con trỏ; `apply-migration` bắt buộc `--expect-plan` (mã `plan_sha256` của lần xem trước) và từ chối nếu kế hoạch tính lại khác. Chỉ chạy khi profile hợp lệ, owner `PROJECT`, chưa có grant và `PROJECT.md` có đúng một dòng quyền; không tự chạy lúc init/adopt/upgrade.
- **Ghi.** Qua `transaction.py` (một giao dịch nhóm gồm profile, `PROJECT.md` và hai bản sao lưu `*.bak-<ngày>` khi migration; từ chối trước khi ghi nếu có giao dịch dở hoặc không rõ, runtime/đích là liên kết, hay sao lưu đã tồn tại). **Không nguyên tử** giữa hai file và không chống race: bị ngắt giữa chừng hoặc người dùng sửa file trong lúc ghi thì kết quả nêu đúng file nào đã/chưa ghi (`PARTIAL`/`CONFLICT`), giữ bytes của người dùng và hướng dẫn `status`/`resume`/`rollback`; không xóa nhật ký hay đặt lại profile để vượt chặn.
- **Chưa kiểm/không có:** host áp dụng lựa chọn, đăng ký native, tính xác thực và hạn của grant, thực thi giới hạn, hệ điều hành ngoài Windows 11/NTFS, liên kết tệp thật khi không có quyền tạo symlink.


## native_agents.py

Adapter mỏng A-10 (host **Claude Code** duy nhất, **ba vai lõi cố định** Scout/Worker/Reviewer): xuất mỗi vai một file native `<project>/.claude/agents/law-<vai>.md` cùng biên nhận `<project>/.agent/runtime/native-agents/claude-code/law-<vai>.json`, có xem trước, và cho ngừng (`retire`) có kiểm. Chỉ là **cấu hình trên đĩa**: công cụ không chạy Claude Code, không gọi model, không đăng ký, không cấp quyền. Không có vai, đường dẫn hay mẫu tùy ý.

```text
python tools/native_agents.py status  [--role scout|worker|reviewer] [--project DIR]
python tools/native_agents.py preview [--role ...] [--project DIR]
python tools/native_agents.py apply   [--role ...] --expect-plan SHA [--project DIR]
python tools/native_agents.py preview-retire [--role ...] [--project DIR]
python tools/native_agents.py retire  [--role ...] --expect-plan SHA [--project DIR]
```

`--role` mặc định `scout` (lệnh đã nhận không đổi).

- **Điều kiện.** Profile hợp lệ (A-09, owner nhất quán; `LEGACY` được giữ khi quyền vẫn ở PROJECT, không xác thực hay cấp grant), `host` = `claude-code`, vai được xuất có **model full ID** (`claude-...-<phiên bản>`, không alias hay inherit), tier/effort của vai đó để null, fallback tắt, `requested_limits` đều null (effort/tier/giới hạn chưa map: `<VAI>_CHOICE_UNSUPPORTED`/`LIMITS_UNSUPPORTED`, không hứa đã áp dụng). Thiếu hoặc chưa hỗ trợ thì từ chối kèm lý do, không bootstrap, migrate hay sửa gì; mỗi vai tự kiểm lựa chọn của riêng nó. Chỉnh lựa chọn bằng `execution_profile.py`. `host_presets` trong `roles/*/config.json` chỉ là **ứng viên** (`CANDIDATE`: Scout `claude-haiku-5-5`, Worker và Reviewer `claude-sonnet-5-5`, effort null, chưa đánh giá chất lượng trên LAW): `status` hiển thị làm gợi ý, **không bao giờ** tự điền vào profile, đăng ký, cấp quyền hay làm `model` null thành đã chọn; lựa chọn rõ của người dùng luôn thắng.
- **Nội dung native.** Frontmatter chỉ `name`, `description`, `model`, `tools`; thân gồm lời mở đầu của vai cộng hợp đồng và kiểm đầu ra lấy từ `roles/<vai>/agent.md`, `checks.md` của chính project. Công cụ: Scout và Reviewer chỉ `Read, Grep, Glob`; Worker thêm `Write` (không Edit/Bash/Agent/MCP/mạng). Worker chỉ được tạo MỘT bản ứng viên (CANDIDATE) mới trong vùng được giao và phải trả lại brief thiếu căn cứ hoặc dừng khi đích đã tồn tại; **nhưng `Write` không giới hạn đường dẫn và không chặn ghi đè, nên đó là nghĩa vụ hợp tác chứ không phải cưỡng chế của host**, và chưa qualified cho file Office nhị phân/COM hay gửi ra ngoài. Reviewer sản phẩm chỉ đọc và trả phát hiện kèm vị trí, không sửa artifact; quyền sửa lỗi nhỏ của Reviewer bảo trì LAW nằm ở AGENTS/PROJECT/roadmap, không ở native sản phẩm. Không đưa grant, profile hay STATE vào prompt. Danh sách công cụ **không** phải rào chắn đường dẫn.
- **Biên nhận** chỉ là nguồn gốc/hash và lời khai hợp tác "đã xem trước rồi apply" của người gọi; không xác thực người dùng, không phải grant. Native cùng tên không có biên nhận hợp lệ, bị sửa tay, biên nhận hỏng hoặc native mất đều được coi là của người dùng: báo `FOREIGN`/`MODIFIED`/`RECEIPT_INVALID`/`NATIVE_MISSING`, không ghi đè, không tự nhận quản lý, không khôi phục. Marker trong file không chứng minh quyền sở hữu.
- **status/preview** chỉ đọc: không tạo thư mục, runtime hay file thăm dò, không chạy host. Trạng thái: `CURRENT`, `STALE` (nguồn/profile đã đổi, có thể cập nhật), `ABSENT`, `FOREIGN`, `MODIFIED`, `RECEIPT_INVALID`, `NATIVE_MISSING`, `RETIRED` (đã cho ngừng, xem dưới), `RETIRE_CONFLICT` (ô retire có file không khớp), `INTERRUPTED_OR_UNKNOWN` (có giao dịch dở hoặc không rõ: dùng `transaction.py status/resume/rollback`), `UNSAFE_PATH` (liên kết hoặc không phải file thường).
- **apply** bắt buộc `--expect-plan` từ preview; hash bytes của profile, `PROJECT.md`, hợp đồng/kiểm/config Scout, schema profile, adapter, PACKAGE_INFO chọn ngôn ngữ, inventory native project và native/biên nhận hiện có phải đúng bytes đã dùng lập kế hoạch, nếu không `PLAN_CHANGED`/`EXPECTED_BEFORE_MISMATCH` và chưa ghi gì. Tạo mới yêu cầu cả native và biên nhận chưa tồn tại; cập nhật chỉ khi cặp do công cụ ghi còn nguyên. Ghi qua `transaction.py` (một nhóm có nhật ký và phục hồi, **không** nguyên tử; khoảng hở cuối của `os.replace` còn, không phải no-clobber). Biên nhận Scout của adapter cũ (`scout-1`) vẫn là của công cụ: chỉ `STALE` vì hash adapter đổi, cập nhật sau preview mới; biên nhận sai hoặc mất không bao giờ được tự nhận. Bytes native của vai khác không vào hash kiểm kê, nên ghi vai này không làm vai kia `STALE`.
- **Trùng tên và binding.** Chỉ kiểm definitions `.md` trực tiếp trong `<project>/.claude/agents/`, không đọc global. File khác có đúng tên native của vai (`law-scout`/`law-worker`/`law-reviewer`) → từ chối; frontmatter ngoài subset key/scalar đơn giản (name slug có thể có nháy) hoặc thư mục con → `NATIVE_DEFINITION_UNSUPPORTED`, giữ nguyên. Marker đầy đủ cùng biên nhận và hash native đều phải khớp. Bất kỳ input hash đổi đều làm `STALE` và cần preview/apply mới, kể cả native bytes không đổi; không dùng confirmation cũ cho nguồn mới.
- **retire** (chỉ Windows; nơi khác `RETIRE_OS_UNSUPPORTED`, không có phương án thay thế). `preview-retire` chỉ đọc; `retire --expect-plan` thực hiện **một** `os.rename` không thay thế đưa đúng file native đang được quản lý sang ô cố định `<project>/.agent/runtime/native-agents/claude-code/law-<vai>.retired.md` (ra khỏi thư mục host tự quét; bytes và biên nhận giữ nguyên). Chỉ nhận cặp native + biên nhận hợp lệ + marker + hash đúng; nguồn người dùng sửa, biên nhận thiếu/hỏng, foreign, liên kết, giao dịch dở hoặc ô retire đã có file đều bị từ chối và giữ nguyên mọi byte. Retire **không** đòi profile còn đủ điều kiện projection (model chưa chọn, host đổi, profile hỏng/phiên bản mới vẫn retire được); raw bytes profile và `PROJECT.md` chỉ được **buộc** vào mã kế hoạch (vắng thì ghi `ABSENT`, không đọc được thì từ chối). Kế hoạch tính lại và đối chiếu mã trước khi chuyển, rồi xem lại ngay sát thao tác dưới guard/pin thư mục sẵn có của `transaction.py`; không tạo thư mục, không dùng `os.replace`/`shutil.move`/sao chép-xóa. Sau chuyển (kể cả khi lỗi hoặc kết quả không chắc) đọc lại hai đường dẫn cố định và báo trạng thái quan sát: `RETIRED` chỉ khi native vắng và ô retire đúng bytes biên nhận; cả hai cùng có → `CONFLICT`; cả hai vắng hoặc không đổi mà không lỗi → `UNKNOWN`; không chọn theo thời gian sửa, không tự retry hay khôi phục. Retire chỉ nghĩa là định nghĩa đã rời thư mục tự quét: phiên mới cần liệt kê lại để xác minh, phiên đang chạy **không** bị dừng hay thu hồi quyền (hủy thuộc B-03). Không tự kích hoạt lại: `apply` thường báo `NATIVE_RETIRED`; muốn dùng lại, người dùng tự chuyển đúng file về `.claude/agents/law-<vai>.md` (đích phải vắng) rồi chạy `status`/`preview`. Không xóa ô retire hay dọn lịch sử. Còn khoảng TOCTOU hợp tác giữa lần xem lại cuối và `os.rename`; destination xuất hiện đúng lúc thì Windows từ chối thay, không có chứng minh race ở mức kernel.
- **Không đo:** host có nạp file ở phiên mới, có gọi vai, model thực tế dùng, hạn chế đường dẫn, hạn/xác thực grant, thực thi giới hạn đều ghi `NOT_INSPECTED`. Windows 11/NTFS/Python 3.11.9 là môi trường đã đo; symlink file thật chưa đo.
- **Đóng gói.** `<project>/.claude/` ở thư mục gốc project là trạng thái native riêng của project: không vào MANIFEST, cây/ZIP phát hành hay project mới tạo từ bản này (`check_package.all_files`); biên nhận nằm trong `<project>/.agent/runtime/` vốn không đóng gói. `adopt_project`/`upgrade_package` chỉ ghi file thuộc package nên không đọc, xóa hay ghi `<project>/.claude/` của người dùng. Mô-đun `native_agents.py` là code package, đi theo MANIFEST như file thường.

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
Liên kết: thư mục runtime (.agent, runtime, transactions, thư mục giao dịch, staging, backup) và mọi đích ghi không được là hoặc đi qua symlink/junction;
vi phạm thì chưa ghi gì, `resume`/`rollback`/`prune` không đọc, ghi hay xóa qua liên kết, và `status` báo lỗi (mã thoát 2). Trên Windows, giữ mở handle thư mục
chặn việc đổi tên/thay thế thư mục đó và mọi thư mục cha trong lúc ghi, nên không thể đổi nó thành junction giữa lúc kiểm và lúc ghi; nơi không có handle,
chỉ kiểm lại sát trước khi ghi (thu hẹp cửa sổ, không đóng) và nhật ký/kết quả ghi mức `recheck_only` thay vì `held`; công cụ không coi hai mức là tương đương. Hash lúc đọc chỉ phát hiện nội dung đổi, không thay cho kiểm này. Chưa có đường POSIX dir_fd.
Vùng bảo vệ bao đường dẫn đầy đủ của mọi file được đọc, băm, ghi, thay hoặc xóa: đích trong project, bản staging và backup (kể cả thư mục con), `journal.json` và file tạm của nó. `resume`/`rollback` băm và quyết định bên trong vùng đó, sát trước khi thay/xóa:
file người dùng vừa lưu giữa hai bước bị giữ nguyên và báo xung đột. Khoảng giữa lần băm cuối và `os.replace` vẫn không nguyên tử.
Nếu `os.replace` lỗi khi chưa ghi file nào (file đang mở, chỉ đọc, bị khóa) thì giao dịch tự hủy sạch và báo "Chưa ghi gì"; nếu đã ghi một phần thì giữ nhật ký để resume/rollback.

- Trạng thái `prepared` và `committing` là còn dở. Lúc đó các công cụ ghi và bảng điều khiển từ chối ghi thêm (mã thoát 1, báo mã giao dịch) cho đến khi `resume` hoặc `rollback`. Trạng thái `rollback_partial` là kết thúc và không chặn.
- `resume` chỉ áp thao tác còn chờ khi file đích vẫn ở bản gốc và bản tạm khớp hash; file đã có bản mới thì đánh dấu xong; file bị đổi khác thì bỏ qua và ghi `skipped_conflict`. Không tiếp tục được khi trạng thái là `rollback_partial`.
- `rollback` đưa về bản gốc các thao tác đã xong, nếu file hiện tại vẫn là bản đã ghi. File do người dùng sửa sau sự cố được giữ nguyên (trạng thái `rollback_partial`) và bản gốc của chúng được giữ trong `.agent/runtime/transactions/<mã>/backup/` để khôi phục tay. Thao tác tạo file mới: file đó bị gỡ nếu chưa bị sửa. Giao dịch đã commit không phục hồi được vì không còn bản sao lưu.

Nhật ký `journal.json` nằm trong `.agent/runtime/transactions/<mã>/` (không vào MANIFEST, ZIP hay git). Nhật ký không chứa nội dung file, tên người hay đường dẫn tuyệt đối; chỉ có đường dẫn tương đối của các file trong project. Khi commit xong, thư mục tạm và thư mục sao lưu bị xóa; giữ 20 giao dịch đã hoàn tất gần nhất.

`Transaction(project, operation, prune=False)` (chỉ tham số từ khóa, owner tự chọn; mặc định `True` giữ hành vi cũ): không xóa nhật ký của giao dịch khác và không xóa thư mục runtime ở nhánh nào (kể cả preflight lỗi), vẫn dọn staging/backup của chính giao dịch; nhật ký đã `committed` ở lại, không tự dọn. Dùng bởi `context_update.py`.

Biến `LOCAL_AGENT_WORKSPACE_TEST_FAULT` gây lỗi giả có kiểm soát, chỉ dùng trong kiểm thử; không đặt khi dùng thật.
Mã thoát: `status` 0 không có việc dở, 1 có; `resume` và `rollback` 0 hoàn tất, 1 còn việc hoặc xung đột, 2 lỗi cách dùng.

## publish_new.py (prototype P-CN1, chưa tích hợp)

Tạo **một** file nháp mới trong `working/` hoặc `output/` mà không bao giờ ghi đè (protocol P-CN1, hợp đồng ở mục 4.3.3 của
tài liệu G02_C2_S3_D0_AMENDMENT_PACKET trong thư mục roadmap của kho nguồn). Bản đầu chỉ chạy trên **Windows, ổ NTFS cục bộ**; nơi khác báo
`UNSUPPORTED_FS` và không ghi. Công cụ chỉ ghi lại sự kiện vật lý: không kiểm quyền (grant), không chạy checker, không thay việc người dùng nghiệm thu.
Chưa được nối vào bảng điều khiển, agent hay checker; chưa có policy nào dựa vào nó.

```text
python tools/publish_new.py publish --request <request.json> --staged <file> [--rid <mã>]   tạo file đích từ bản đã soạn
python tools/publish_new.py observe --target <đường dẫn> [--input <đường dẫn>…] [--rid <mã>]   chỉ đọc, quan sát tại thời điểm gọi
python tools/publish_new.py status [<mã>]                                     liệt kê bằng chứng, không khóa, không ghi
python tools/publish_new.py recover <mã>                                      đóng một lần publish bị gián đoạn
python tools/publish_new.py discard-staged <mã>                               xóa bản tạm của một lần không thành công
```

`--rid` (API: `request_id=`) cho người gọi chọn mã trước (32 ký tự hex thường, chính là phần sau `pcn1-` của `task_id`) để cùng một ảnh chụp task đi từ lập kế hoạch tới nghiệm thu; không truyền thì công cụ tự sinh như cũ. Mã sai ⇒ `REQUEST_ID_INVALID`; mã đã có bất kỳ file nào dưới thư mục publish ⇒ `RID_TAKEN`, không ghi đè hay xóa gì. `.agent` và `.agent/runtime` phải **có sẵn** (thư mục thường, không link): thiếu ⇒ `RUNTIME_PARENT_MISSING`, công cụ không tạo hộ và chỉ tạo thư mục `publish` bên dưới; khởi tạo hai thư mục này thuộc bước tích hợp chưa làm.

Tùy chọn chung: `--project <thư mục>`, `--result-json`. API Python cùng tên (`publish`, `observe`, `status`, `recover`, `discard_staged`) trả `dict`
có `outcome`, `reason`, `request_id`, `wrote` (mọi thư mục/file đã tạo, link hay xóa trong lần gọi, theo thứ tự, gắn nhãn T1–T7); kết quả protocol không dùng exception.

Luồng `publish`: kiểm request, đường dẫn (chỉ dưới `working/`/`output/`; từ chối `..`, ổ đĩa, `:`, đoạn kết thúc `.`/khoảng trắng, `~<số>`, tên thiết bị,
tên kiểu chỉ dẫn/quyền như `AGENTS.md`, `*.schema.json`), ổ NTFS cục bộ và nguồn (hash hiện tại phải bằng hash công cụ soạn đã đọc) → tạo
`.agent/runtime/publish/<mã>.prepared.json` rỗng và khóa → ghi ảnh chụp yêu cầu → ghi bản tạm `<mã>.staged` → tạo thư mục cha còn thiếu → `os.link`
(tên đích đã có, kể cả chỉ khác hoa/thường, thì dừng và ghi `conflict`, không đụng file có sẵn) → kiểm file đích cùng identity/size/hash →
ghi `<mã>.published.json` → xóa bản tạm. Không có đường copy/replace dự phòng.

Bằng chứng (`publish-v1`) nằm trong thư mục runtime publish (.agent/runtime/publish, tạo khi dùng lần đầu), mỗi file chỉ tạo một lần, không sửa, không tự dọn; JSON canonical LAW-CJ/2, tối đa
1 MiB; bản tạm tối đa 100 MiB. Mỗi mã có tối đa một file kết thúc (`published`, `conflict`, `abandoned`, `unknown`). Ảnh chụp có thể chứa lời yêu cầu
và đường dẫn có tên người; bản tạm chứa toàn nội dung. Không có nội dung nguồn hay đường dẫn tuyệt đối.

Khóa mỗi mã: một byte ở offset 2^30 trên chính `prepared.json` (`msvcrt.locking`, không chờ); `recover`/`discard-staged` cùng mã khi đang khóa trả `BUSY`.
`recover` chỉ công nhận đã publish khi đích là file thường, cùng identity với bản tạm và size/hash đúng; mọi trường hợp khác ghi `unknown`, không đoán
“chưa từng publish”. Bằng chứng hỏng hoặc nhiều file kết thúc ⇒ `UNKNOWN(EVIDENCE_INCONSISTENT)`, không ghi hay xóa thêm.

| Kết quả | Mã thoát | Status | Ghi chú |
|---|---|---|---|
| `PUBLISHED`, `OBSERVED`, `STATUS`, `NO_ACTION`, `DISCARDED` | 0 | success | `PUBLISHED`/`NO_ACTION`/`DISCARDED` có thể kèm `STAGED_CLEANUP_PENDING` |
| `CONFLICT` | 3 | blocked | file có sẵn giữ nguyên |
| `REFUSED`, `UNSUPPORTED` | 4 | blocked | có thể đã tạo thư mục runtime/`prepared` rỗng: xem `wrote` |
| `ABANDONED`, `UNKNOWN`, `PUBLISHED_EVIDENCE_PENDING` | 5 | partial | cần `status`/`recover` |
| `BUSY` | 6 | blocked | lần gọi khác cùng mã đang giữ khóa |
| lỗi cách dùng | 2 | blocked | — |

Bảo vệ đường dẫn khi ghi: thư mục gốc phải là thư mục thường (junction/symlink/reparse ⇒ `REFUSED(PARENT_UNSAFE)`, `detail: ROOT_LINKED`, không ghi gì). Từ trước
thao tác ghi đầu tiên tới khi xong bằng chứng kết thúc và xóa bản tạm, `publish` giữ handle thư mục từ gốc → thư mục cha của đích → chuỗi runtime;
mỗi thư mục được giữ và chứng minh đúng là thư mục đó (handle và đường dẫn cùng identity, không phải liên kết) rồi mới tạo gì bên trong, nên cha đã bị
thay thì dừng trước khi `mkdir`. `recover`/`discard-staged` giữ chuỗi runtime trước khi mở `prepared`, và sau khi khóa kiểm lại identity descriptor so với
đường dẫn. Không lấy được handle ⇒ dừng an toàn (`detail: PIN_UNAVAILABLE`, `wrote` ghi đúng phần đã tạo), không chạy tiếp ở mức `recheck_only`. Bản tạm chỉ
bị xóa qua một handle đã kiểm là file thường đúng identity, không cho người khác đổi tên/xóa đối tượng đó trong lúc xóa; chỉ tên `<mã>.staged` bị bỏ, link
của đích giữ nguyên. File khác identity thì giữ lại và báo `STAGED_CLEANUP_PENDING` (publish/recover) hoặc `UNKNOWN(EVIDENCE_INCONSISTENT)` (discard).
Nếu Windows đã nhận yêu cầu xóa nhưng reader khác còn giữ handle cho phép share-delete, tên staged có thể còn tới khi reader đóng: báo
`cleanup_pending: true`, reason `STAGED_CLEANUP_PENDING` (kể cả `DISCARDED`), vẫn ghi T7 trong `wrote` vì disposition xóa đã được đặt.
Mọi mã thoát: `changes = bool(wrote)`. Evidence do `recover` ghi vẫn ghi `protection: recheck_only` (nó không chứng minh được lúc link); không coi là chống
race tuyệt đối. Hash entrypoint và bằng chứng chỉ ở mức hợp tác (ADVISORY): ai ghi được thư mục `.agent/runtime` cũng sửa được. Kết quả đo trên Windows/NTFS và phần
chưa kiểm của bản prototype nằm trong thư mục roadmap/evidence của kho nguồn (không có trong bản phân phối).

## context_update.py (prototype P-CTX1, chưa tích hợp)

Cập nhật ghi chú vận hành **có sẵn** `.agent/STATE.md` hoặc `.agent/HANDOFF.md`, một file mỗi lần gọi. Đây là ghi chú vận hành, không phải tài liệu giao người dùng:
không task, receipt hay D4 cho mỗi lần lưu và không có kết quả PASS. Nội dung context không cấp quyền, không là policy, review hay nghiệm thu.

```text
python tools/context_update.py --project <thư mục> --target state|handoff --content <file> --expected sha256:<hash>            xem trước, không ghi
python tools/context_update.py --project <thư mục> --target state|handoff --content <file> --expected sha256:<hash> --apply    ghi
```

`--expected` là SHA256 của chính bytes bạn đã đọc; file đã đổi từ lúc đọc thì `CONFLICT`, không ghi. Chỉ cập nhật file có sẵn (thiếu thì từ chối, `init_project.py` tạo riêng).
Bytes mới được ghi nguyên văn, công cụ không sửa hay chuẩn hóa. STATE phải giữ đúng tám heading chuẩn, có dòng trống sau mỗi heading, tối đa 60 dòng; HANDOFF không áp giới hạn dòng;
nội dung rỗng, không phải UTF-8, chứa NUL hoặc lớn hơn 8 MiB bị từ chối. Bản xem trước chỉ đọc, nêu `planned_changes` và không bao giờ báo `WRITTEN`. Nội dung giống hệt hiện tại là `UNCHANGED`:
không probe, nhật ký, staging hay backup.

Chỉ chạy trên **Windows, ổ NTFS cục bộ**. Thư mục gốc, .agent và .agent/runtime phải có sẵn, là thư mục thường (không junction/symlink) và được giữ handle trước mọi probe,
thư mục tạm hay ghi; thiếu hoặc không giữ được handle thì từ chối, công cụ không tạo hộ. Ghi qua `Transaction(prune=False)`: không xóa nhật ký khác, không xóa thư mục runtime, không tự resume/rollback;
có giao dịch dở thì từ chối (`TRANSACTION_UNFINISHED`). Kết quả: `WRITTEN` (0), `UNCHANGED` (0), `CONFLICT` (3), `ERROR` (4), `UNKNOWN` (5; `changes: null`); `usage` lỗi là 2.
Lỗi sau khi thay file được xác định bằng hash của file thật, không chỉ từ ngoại lệ: bản mới đã nằm trên đĩa thì vẫn báo `WRITTEN` kèm `COMPLETION_ERROR`; không chứng minh được thì `UNKNOWN`.
Nhật ký của mỗi lần ghi còn lại trong thư mục transactions dưới .agent/runtime (không tự dọn, không chứa nội dung file). Hash chỉ nhận ra bản đã đọc bị đổi (single-writer hợp tác, ADVISORY), không phải CAS của
filesystem, không chặn mọi editor và không cho hai file nguyên tử. Công cụ không kiểm quyền: người gọi phải kiểm group grant còn hiệu lực trước khi gọi. Khai báo phạm vi ở `operational_context_protocol`
của `.cvf/rules/v3/ROUTING_POLICY.json`; checker artifact không đánh giá nó.

## Task/RESULT và checkpoint trước tích hợp (A-11, hướng dẫn: không có công cụ mới)

Không có script, helper hay schema mới dưới `tools/`. A-11 chỉ là hướng dẫn trình tự ở mục "TASK, RESULT và checkpoint trước tích hợp (A-11)" của `roles/README.md`
(kèm khối mã mẫu `law-recipe`, ví dụ Worker một candidate; không phải bộ kiểm Scout delta chung) trên các owner đã có; mỗi owner giữ nguyên giới hạn của nó:

| Owner | Dùng cho | Chỉ bảo vệ | Không bảo vệ |
|---|---|---|---|
| `.cvf/checks/v3` (`loader.inspect_structure`, `binding.compare_binding`) | đọc TASK/RESULT, so binding RESULT với TASK **hiện hành** | digest khai báo khớp task | PASS, quyền, bytes thật, nghiệm thu (checker candidate, helper nội bộ, không phải API ổn định) |
| `library.read_book`, `record`, `id_counts` | ID, locator, revision của inputs/context_refs đã ghi trong sổ; `snapshot` là SHA-256 bytes sổ đã đọc | metadata sổ tại lúc đọc | nguồn đổi mà sổ chưa sync (phải tự hash bytes nguồn); `sha12` không phải SHA đầy đủ |
| `publish_new.path_form_problem` | cú pháp đường dẫn trước đọc checkpoint | từ chối `..`, tuyệt đối và alias không hỗ trợ | không là khóa/chống TOCTOU; kiểm link vẫn riêng |
| `publish_new.publish` (P-CN1) | tạo file mới; `request.inputs` ghi digest bytes thô của TASK, RESULT, candidate, nguồn/context và sổ nếu dùng | input phải đúng digest lúc publish (`INPUT_CHANGED_SINCE_READ`, chưa ghi gì); không ghi đè | `staged` là bytes tự do, không tự trùng candidate; không kiểm review, nội dung, nghiệm thu |
| `context_update.update` (P-CTX1) | STATE/HANDOFF | `expected_before` của chính bytes đích | không phải CAS của TASK hay nguồn; không kiểm quyền |
| `library.content_find`, `library_sync.content_*`/`event_*` (B-01) | nội dung đã đọc theo SourceID + revision/SHA; lịch sử source-event | chỉ ghi khi file khai báo khớp sổ và bytes; plan token buộc sổ, payload và quan sát nguồn | không đọc lại nguồn khi tra (`UNOBSERVED`); `CURRENT_CATALOG_BASIS` không là hiệu lực hay nội dung đúng; không PASS/quyền |
| `artifacts.prepare`, `register_*`, `open_artifact`, `copy_input` (B-02) | phiên bản kết quả và quan hệ nguồn–phụ lục–kết quả trong sổ; `prepare` đọc/hash lại closure rồi trả `snapshot` + `inputs` cho `request.inputs` của P-CN1 | `prepare` từ chối căn cứ cũ/thiếu/xung đột, phiên bản đã bị thay, file đổi; guard publish bắt đổi sau `prepare`; đăng ký chỉ khi khớp `prepared.inputs` và bằng chứng owner; plan token buộc sổ, file, nguồn và yêu cầu | không xác minh nội dung, hiệu lực hay nghiệm thu; `UNOBSERVED` khi query; không chọn Nháp hiện tại, không ghi TASK/RESULT/STATE; hợp tác, không chống đua |
| `library_sync.apply(..., expected_preview=...)` | sổ nguồn | plan tính lại dưới khóa phải khớp bản đã xem (`PreviewMismatch`) | CLI `library.py sync` không truyền `expected_preview` |

Kiểm lại task, nguồn và quyền ngay trước **mỗi** lần gọi writer; điều kiện của owner này không thay cho owner kia, và không có giao dịch nguyên tử nhiều owner. Native Write
của host không giới hạn đường dẫn và không chặn ghi đè nên quy ước slot và "chỉ file mới" là nghĩa vụ hợp tác. Probe `test_task_result_flow.py` trong thư mục tests của kho nguồn (không có trong
bản phân phối) trích đúng khối mã từ `roles/README.md` và chạy nó với API thật trên dữ liệu giả; các ca "người khác ghi chen" là xen kẽ có điều khiển trong test, không phải bằng chứng chống mọi agent
hay race ở mức nhân hệ điều hành. Dừng/timeout/kết quả muộn/mở lại phiên dùng đúng các owner này (trình tự ở mục B-03 của `roles/README.md`, không nhân bản ở đây): khi mất phản hồi
của `publish`, đọc lại bằng `status`/`observe` cho đúng request ID trước mọi lần giao lại, và nhớ `recover` **ghi** evidence/dọn file tạm (khai là phép ghi, gọi riêng trong quyền của tác động đó); `status`/`observe`
không thay `recover` và ngược lại. `native_agents.py retire` chỉ chuyển file cấu hình, không xác nhận tiến trình đang chạy đã dừng. Lineage thuộc B-01/B-02.

## current_draft.py (I2, chưa tích hợp ngoài bảng điều khiển)

Chọn và mở "Nháp hiện tại" cho luồng nháp P-CN1, cùng một helper cho bảng điều khiển và agent. **Chỉ điều hướng, không phải nghiệm thu**: không PASS, không D4, không nhãn "đã nghiệm thu".

`readiness(project)` (chỉ đọc) đo điều kiện chạy bằng **đúng Python đang chạy**: Windows, ổ NTFS cục bộ, `jsonschema` từ 4.18 (Draft 2020-12), và hai owner P-CN1/P-CTX1 nạp đúng pin. Bảng điều khiển hiện kết quả ở trang "Tình trạng ứng dụng"
(chức năng "Nháp hiện tại có kiểm soát"). Thiếu hoặc sai ⇒ thẻ báo không dùng được với mã đóng (`PLATFORM_UNSUPPORTED`, `DEPENDENCY_MISSING`, `FS_UNSUPPORTED`, `OWNER_UNAVAILABLE`, `CONTEXT_OWNER_PIN_MISMATCH`...) và không chọn/mở gì, không có đường
bỏ pin hay dùng bộ mở file chung. Công cụ không cài thư viện, không đổi Python, không sửa `APP.bat`; chỉ in lệnh cài cho đúng Python đang chạy để người dùng tự chạy. Chỉ thẻ này chịu các điều kiện trên; các chức năng khác có điều kiện riêng.

```text
python tools/current_draft.py status [--project <thư mục>]                    thẻ hiện tại + tối đa 5 bản liên quan, chỉ đọc
python tools/current_draft.py list                                            các bản có bằng chứng xuất bản hợp lệ, chỉ đọc
python tools/current_draft.py select --rid <mã>                               xem trước, không ghi (in hash STATE và selection_fingerprint)
python tools/current_draft.py select --rid <mã> --apply --expected-state <hash> --expected-selection <hash>
python tools/current_draft.py open --rid <mã> [--ack changed|unverified]      mở bằng ứng dụng liên kết
```

Con trỏ duy nhất là một dòng chú thích có version trong mục "Current artifact" của .agent/STATE.md (dạng `law-current-draft/1` kèm JSON ba khóa path, rid, digest). Mọi marker khác cùng từ khóa, marker hỏng
hoặc sai mục, mục thiếu hoặc trùng đều là UNRESOLVED: công cụ không chọn marker "còn hợp lệ", không chọn theo mtime hay `supersedes`, không tự sửa mà hướng dẫn nhờ agent sửa STATE qua `context_update.py` theo quyền đã cấp.
Chọn bản chỉ cho bản còn khớp bằng chứng; xem trước chỉ đọc, apply đọc lại toàn bộ snapshot (bản, bằng chứng prepared/published, bytes và identity của file) và dừng `CONFLICT` nếu khác xem trước hoặc STATE đã đổi,
rồi ghi đúng một marker bằng `context_update.update` (giữ nguyên mọi byte và kiểu xuống dòng khác, không tự cắt STATE xuống 60 dòng). Trạng thái ghi lấy nguyên từ P-CTX1. Publish thành công mà chọn thất bại thì file và receipt vẫn còn:
nói rõ "đã tạo, chưa cập nhật lựa chọn", không xóa hay publish lại.

Nhãn: `matched` (bytes và identity hiện tại bằng bản đã ghi nhận), `changed` (đã khác), `unverified` (không đối chiếu được nhưng file an toàn, ví dụ thiếu bằng chứng), `unopenable` (liên kết, ngoài phạm vi, thiếu, không quan sát được).
`open` quan sát lại mỗi lần: `matched` mở ngay; `changed`/`unverified` chỉ mở khi lời gọi mang `--ack` đúng trạng thái vừa quan sát (bảng điều khiển: nút có nhãn cảnh báo, hoặc hộp xác nhận nếu trạng thái đổi sau khi vẽ thẻ).
Chỉ các đuôi .docx .xlsx .pptx .pdf .txt .md .csv; HTML, SVG, file chạy được, liên kết, macro bị từ chối. Không dùng opener chung. Mở file không hứa Office mở chỉ-đọc và không chống người dùng sửa; hash chỉ nhận ra file đã khác.

Code owner nạp từ cây LAW cố định cạnh helper, đúng bytes đã so với pin trong policy (P-CN1 qua observer của checker v3, P-CTX1 qua `operational_context_protocol`); `--project` chỉ là dữ liệu. Cần Windows, ổ NTFS cục bộ và `jsonschema` >= 4.18
(checker v3 so pin); thiếu một trong ba thì kết quả `UNAVAILABLE` và không làm gì. Quan sát là tại thời điểm (ADVISORY): không chống đua với trình khác, và pin là so sánh version, không chứng minh tool thật.
Chi phí: kiểm tối đa 512 bản mới nhất theo mtime file published (mtime chỉ để chọn phần kiểm); `owner.status` vẫn đọc tên toàn bộ thư mục publish nên đây không phải I/O bị chặn cứng, và danh sách có thể báo chưa đầy đủ.
Bảng điều khiển dùng các route riêng `/api/draft/status|list|select|open` (có token và kiểm Host như các route khác), không qua `/api/run` nên không ghi lịch sử thao tác; chỉ `select` kèm `apply` ghi, và chỉ marker STATE.
Biến `LOCAL_AGENT_WORKSPACE_TEST_OPEN_LOG` chỉ dùng kiểm thử (ghi đường dẫn thay vì mở ứng dụng); không đặt khi dùng thật.

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
python tools/check_package.py --check-eol FILE...  kho nguồn có Git: kiểm EOL các file vừa sửa (chỉ đọc)
```

Kiểm: `VERSION` và chuỗi phiên bản nhất quán, mục trong `CHANGELOG.md`, frontmatter và index của skill, đường dẫn
trong tài liệu, số mục khớp giữa bản Việt và bản Anh, HTML không tải từ mạng và khớp Markdown, cú pháp Python.

`--check-eol` là tự kiểm riêng của người bảo trì, chỉ nhận đường dẫn tương đối của các file trong lượt sửa,
kể cả file mới chưa theo dõi. Công cụ hỏi `git check-attr` để dùng attributes hiệu lực, báo lỗi kèm tên file
nếu lệch LF/CRLF hoặc lẫn dòng kết thúc; file `-text` được nêu rõ là không kiểm EOL và giữ bytes.
Không tự chuẩn hóa, không kiểm toàn kho hoặc đổi gate hiện có; chế độ kiểm package thông thường không cần Git.
Sau mỗi tranche ghi kết quả kiểm EOL cùng `git diff --check` trong phần tự soát HANDOFF; không coi diff sạch
là đã chứng minh EOL. Đọc/ghi bằng Python phải giữ newline từ lúc đọc đến lúc ghi; file mới theo attributes (thường LF, riêng .bat dùng CRLF).

**Bản giao (projection, I3).** `check_package.py` là owner chung của "file nào được giao" và "giao bytes nào" cho `build_release.py`, `new_project.py`, `adopt_project.py` và MANIFEST của bản giao
(`delivery_selection`, `delivery_bytes`, `delivery_manifest`, `materialize`). Một runtime duy nhất được giao: `.cvf` chỉ gồm closure v3 liệt kê tên file (schema, policy, quy tắc/hợp đồng đọc được, entry, tám module và một README
mới dành cho package); không v1/v2, vectors/ví dụ, bằng chứng đánh giá, `PROVENANCE`, dữ liệu vận hành hay tests/roadmap. Kho nguồn giữ nguyên v1/v2 và fixtures. PROJECT/STATE/HANDOFF (VI/EN) lấy từ mẫu sạch; `AGENTS.md`, `en/AGENTS.md` và `roles/`
đổi các tham chiếu `.cvf` sang v3 bằng phép thay đúng chuỗi, đúng số lần, lặp lại không đổi (idempotent); số lần lạ, EOL lẫn hoặc không phải UTF-8 ⇒ từ chối trước khi ghi. MANIFEST tính trên bytes thực giao. Hai entrypoint đã pin bằng
hash bytes trong policy v3 (`tools/publish_new.py`, `tools/context_update.py`) được đóng gói **nguyên từng byte** (ZIP không đổi CRLF thành LF cho riêng hai file này); `--release` đối chiếu bytes giao với pin.
`--release` trên cây phát hành (không có release_templates) còn báo đỏ khi có file `.cvf` ngoài closure, thiếu file closure, dữ liệu vận hành `.agent/runtime`, hoặc tham chiếu `.cvf` không rõ phiên bản/không có trong bản giao.
`--verify` bỏ qua các file người dùng sửa (PROJECT, `.agent/`, nguồn, đầu ra) và hiểu project dùng `--lang en`.
**Profile.** `.agent/EXECUTION_PROFILE.json` là file người dùng và **không** vào MANIFEST; bản giao luôn là mẫu sạch (`release_templates/.agent/EXECUTION_PROFILE.json` phải đúng mặc định, nguồn có profile riêng cũng không bị mang đi). Schema `.agent/EXECUTION_PROFILE.schema.json` và `tools/execution_profile.py` là file package thường. Chế độ kiểm tra tự kiểm schema và mặc định; project đã khởi tạo có profile thiếu/hỏng/phiên bản lạ/mâu thuẫn owner hoặc còn cần migration chỉ bị **cảnh báo** (dữ liệu người dùng, không tự sửa).

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

Dựng cây phát hành trong thư mục tạm và không sửa working tree, bằng bản giao chung của `check_package.py` (mục trên). PROJECT, STATE và HANDOFF sạch lấy từ bộ mẫu phát hành
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
