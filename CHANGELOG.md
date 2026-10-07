# Changelog

Định dạng phiên bản: `MAJOR.MINOR.PATCH`. Số phiên bản nằm trong `VERSION`; hướng dẫn nâng cấp ở
`docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`.

## v1.4.0 — 2026-10-07

Đưa kinh nghiệm từ các project cũ vào bộ skill dùng chung (đã loại thông tin riêng của đơn vị, cá nhân và từng vụ việc; xem `docs/NGUON_THAM_KHAO_VI.md`)
- Skill mới `excel-workbooks`: dựng sổ theo dõi, form nhập liệu, báo cáo tự tổng hợp và phụ lục tính bằng Excel; kèm `references/openpyxl-notes.md` (công thức, định dạng, giới hạn, lỗi đã gặp).
- Skill mới `excel-html-viewer`: công cụ HTML một file, offline, đọc file Excel; chịu được tên sheet, tên cột và giá trị gõ tay không chuẩn; kèm danh sách kiểm thử.
- `office-documents`: thêm năm tài liệu tham khảo `report-writing`, `procedure-document`, `proposal-review`, `form-standardization`, `word-technical-notes`; checklist giao thêm quy ước lưu bản cũ (`mv -n`, không xóa khi chưa được yêu cầu).
- `vn-admin-documents`: thêm khung biên bản họp, thứ tự "Căn cứ", và lưu ý khi nào bảng có viền, khi nào không.
- `process-mapping` trỏ tới `procedure-document`. `skills/local/README.md` thêm quy tắc chọn chỗ đặt skill (chung hay riêng project) và tránh chép trùng.
- `upgrade_package.py`: khi nâng cấp, thêm vào `.agent/SKILL_INDEX.md` của project các dòng skill dùng chung còn thiếu (không sửa dòng đã có); trước đây skill mới đến project cũ nhưng agent không tìm thấy vì không có dòng trong chỉ mục. Project cũ hơn v1.4.0 chạy script từ package mới.
- Công cụ mới `adopt_project.py`: đưa package vào project đã có lần đầu (báo cáo trước, `--apply` mới ghi; lưu `.bak`/`.new`, thêm skill riêng sẵn có vào chỉ mục). `upgrade_package.py` không làm được việc này vì cần `VERSION` của project.
- `spreadsheet-check`: chọn dòng tiêu đề theo dòng nhiều ô chữ nhất (không nhầm dòng quốc hiệu/tên đơn vị); bỏ qua kiểm theo cột với sheet dạng hướng dẫn/biểu mẫu; không báo "số lưu dạng chữ" với cột mã/số hiệu hoặc khi chỉ có 1–2 ô. Phát hiện khi thử trên file Excel thật của người dùng.
- `check_package.py`: không đòi bản `en/` cho skill trong `skills/local/project|packs|external|inbox` (do người dùng quản lý).
- `excel-html-viewer`: thêm `assets/xlsx-mini-reader.js`, đọc .xlsx không cần thư viện ngoài (thử trên 13 file Excel thật); quy tắc: lời nhắc đọc .xlsx thì công cụ phải đọc được .xlsx. `excel-workbooks`: phép thử bằng dữ liệu trước khi giao (đổi kỳ, ngưỡng trống, mã mới), tham số mặc định trống. Phát hiện khi kiểm lại kết quả test agent.
- Từ mười một lên mười ba skill; cập nhật chỉ mục, README và các hướng dẫn.
- Gia cố sau kiểm toán độc lập kết quả test agent: `office-documents` thêm mục "Giữ nguyên nội dung khi chuyển dạng hoặc sửa tại chỗ" (đếm ảnh, bảng, ký tự, bước trước và sau, báo bảng trước → sau) và mục tương ứng trong checklist giao; `excel-html-viewer` cấm tài nguyên mạng (kèm lệnh tự kiểm), thêm quy tắc ngày serial, số âm và nhiều sheet, cùng ba mục kiểm thử mới (quét mạng, lỗi dữ liệu, nhiều sheet).


## v1.3.2 — 2026-10-07

Sửa theo bản audit độc lập (xem `feedback/records/2026-10-07_audit-ben-ngoai_v1.3.1_xu-ly.md` trong kho nguồn)
- `spreadsheet-check`: dòng Tổng được đối chiếu cả khi bảng chỉ có 2–3 dòng số (trước đây cần ít nhất 4); khóa ghép thiếu một cột thì báo "chưa kiểm được khóa ghép đầy đủ" thay vì im lặng.
- `check_output.py`: checker bảng tính lỗi hoặc không chạy được thì in "LỖI CÔNG CỤ" và trả mã thoát 1, không còn trông như không có lỗi.
- `data-charts/assets/basic-charts.html` (VI/EN): cột xếp chồng không coi ô thiếu là 0 (ghi "≥ tổng phần đã biết"); biểu đồ đường không còn NaN với chuỗi hằng, một kỳ hoặc toàn ô thiếu; nhãn "tháng 6", "20 hồ sơ tồn" chuyển vào dữ liệu (`period`, `note`).
- `init_project.py`: đổi sang tiếng Anh sao lưu `.bak` cả file mẫu người dùng đã sửa một phần (PROJECT, STATE, HANDOFF).
- `AGENTS.md`, `doc-coauthoring`: các giới hạn vòng soát/sửa có ngoại lệ cho lỗi cụ thể (sửa đúng chỗ, kiểm lại chỗ đó); không đổi quy tắc đọc `SKILL.md` khi khớp.
- Đoạn dán cho Project/cloud (`HUONG_DAN_TAO_PROJECT_MOI_VI.md`, `NEW_PROJECT_GUIDE.md`): đồng bộ quy tắc đọc skill và khối Khai báo thực hiện, đủ 11 skill, bỏ tên ZIP `v1.0.0`.

## v1.3.1 — 2026-10-07

- `README.md` / `en/README.md`: mục "Cách bắt đầu" cho người xem trên GitHub (tải ZIP ở Releases, giải nén, chạy `SETUP`, mở bằng ứng dụng AI).

## v1.3.0 — 2026-10-07

Phản hồi của người dùng
- `docs/FEEDBACK_FORM_VI_EN.md`: phiếu phản hồi song ngữ, chủ yếu tích chọn (thông tin, bảy câu hỏi, câu hỏi cho việc thật, năm gợi ý kể lại, đính kèm nên có) kèm lời nhắc để agent phỏng vấn và điền giúp, để người dùng không phải tự nghĩ nên mô tả gì.
- Mục "Góp ý sau khi dùng" trong `START_HERE.html` / `START_HERE.en.html`, dòng nhắc trong `README.md` / `en/README.md`, `docs/README.md`.
- Kho nguồn: mẫu issue GitHub `.github/ISSUE_TEMPLATE/phan-hoi.md` (cùng nội dung phiếu; `check_package.py` cảnh báo nếu hai bản lệch nhau); `.github/` và `feedback/` không nằm trong gói phát hành.

## v1.2.3 — 2026-10-07

- `spreadsheet-check` 1.3: mỗi phát hiện của `check_spreadsheet.py` kèm số dòng trong file hoặc sheet (ô chữ lẫn trong cột số, giá trị mơ hồ, giá trị lệch xa, các dòng trùng hoặc cùng khóa, dòng Tổng), tính cả dòng trống. Agent chép đúng số dòng, không tự đánh số lại (lần thử ba mô hình cho thấy mỗi mô hình đánh số một kiểu).
- Bài thử `examples/demo-project` ghi rõ vị trí mong đợi (dòng 5, 6, 7 và 8, 11).

## v1.2.2 — 2026-10-07

Rút ra từ lần thử với ba mô hình (Gemini 3.8 Flash High, Claude Sonnet 4.5, GLM 5), xem `feedback/` trong kho nguồn
- `document-comparison` 1.2: bỏ qua cả khác biệt diễn đạt lại hoặc đổi từ mà nghĩa không đổi, và nêu rõ đã bỏ loại nào; cột "Tác động" đổi thành "Tác động (suy luận)" để nhãn gắn cả cột.
- `spreadsheet-check` 1.2: số trong kết quả tiếng Việt dùng dấu chấm ngăn cách nghìn (trước đây dùng dấu phẩy kiểu Anh, dễ nhầm với dấu thập phân); ô mơ hồ như "1.234" được mô tả bằng hai cách đọc rõ ràng, và dòng tổng không khớp in thêm tổng theo cách đọc còn lại.
- `check_output.py --declaration` cảnh báo khi mục Cách làm nhắc `check_spreadsheet` mà thiếu dòng "Dấu vết".
- `AGENTS.md` và demo-project cập nhật theo.

## v1.2.1 — 2026-10-06

Rút ra từ lần chạy lại bài thử với Gemini 3.8 Flash (Low), xem `feedback/` trong kho nguồn
- `AGENTS.md`: khi yêu cầu khớp cột "Use when" của một skill, agent đọc `SKILL.md` của skill đó trước khi làm (trước đây ghi "không bắt buộc phải nạp skill", nên skill và script không được dùng). `.agent/SKILL_INDEX.md` nhắc cùng điều này.
- Khối "Khai báo thực hiện" thêm dòng "Skill" (skill đã đọc hoặc "không dùng skill"); bỏ yêu cầu đếm số dòng đã đọc. `check_output.py --declaration` cảnh báo khi thiếu dòng Skill và không còn coi từ "skill" là đủ cho dòng Cách làm.

## v1.2.0 — 2026-10-06

Khai báo khi làm việc (rút ra từ lần thử đầu tiên với Gemini, xem `feedback/` trong kho nguồn)
- Quy tắc bắt buộc thứ 9 trong `AGENTS.md` và mục "Khai báo thực hiện": cuối câu trả lời có phát hiện hoặc số liệu, agent khai cách làm (skill, script kèm lệnh hoặc đọc thủ công), nguồn, file đã tạo hoặc sửa, và điều chưa kiểm; phát hiện về số kèm con số cụ thể, số mơ hồ nêu các cách hiểu.
- `check_spreadsheet.py` in dòng "Dấu vết" (file, sha256, giờ chạy) để chép vào khai báo; `tools/check_output.py --declaration` kiểm khối khai báo trong câu trả lời đã lưu.
- Checklist giao sản phẩm và hướng dẫn dùng hằng ngày (mục 10) nói về khai báo.

Skill và bài thử
- `meeting-minutes` 1.1: không gán người phụ trách chỉ vì họ "đã báo/đã làm"; giữ nguyên mốc tương đối như "từ tuần sau". `document-comparison` 1.1: ảnh hưởng suy luận gắn nhãn "(suy luận)". `spreadsheet-check` 1.1: nêu con số và các cách hiểu.
- `examples/demo-project`: mở thư mục gốc package (để agent thấy `AGENTS.md` và skill), đường dẫn trong yêu cầu có tiền tố `examples/demo-project/`; bản 2 của quy trình có thêm một khác biệt chỉ về câu chữ; thêm mục kiểm khai báo.

Kho nguồn
- Thư mục `feedback/` (README, mẫu, chỉ mục, bản ghi) để người duy trì theo dõi các lần thử và vấn đề; không nằm trong MANIFEST và ZIP phát hành.

## v1.1.0 — 2026-10-06

Khởi tạo và dùng thử
- `SETUP.bat` / `SETUP.command` chạy `tools/setup_wizard.py`: hỏi ngôn ngữ, tên và các thông tin ngắn (mục đích, đầu ra, văn phong, nguồn, ràng buộc, mức nhạy cảm dữ liệu), tự khởi tạo, điền `PROJECT.md`, sao chép đoạn hướng dẫn dán vào Project/cloud. Form "Khởi tạo nhanh" trong `START_HERE.html` / `START_HERE.en.html` tạo `setup_answers.json` để trình hướng dẫn đọc, không hỏi lại.
- Mục "Package này dùng để làm gì?" ở đầu `START_HERE`; project mẫu `examples/demo-project/` (dữ liệu giả, hai ngôn ngữ) kèm ba yêu cầu thử.

Vòng đời và mở rộng
- `tools/upgrade_package.py`: nâng cấp project lên bản package mới bằng so sánh ba bên theo `MANIFEST.sha256` (cập nhật file chưa sửa, giữ file đã sửa, lưu `<tên>.new` khi xung đột; không xóa, không đụng file người dùng).
- Gói lĩnh vực: `packs/` + `tools/pack.py` (`list/add/update/remove/check/new`), khung `packs/_template`, cài vào `skills/local/packs/`, ghi `.agent/SKILL_INDEX.md` với Scope `PACK`; `check_package.py` kiểm tra cấu trúc gói.
- `MANIFEST.sha256` ghi cả hash file mẫu của người dùng để nhận biết file còn nguyên bản mẫu.

Chất lượng và an toàn
- `tools/check_output.py` và checklist `skills/local/shared/office-documents/references/delivery-checklist.md` trước khi giao sản phẩm.
- Mục "Dữ liệu nhạy cảm" trong `AGENTS.md`, dòng "Mức nhạy cảm dữ liệu" trong `PROJECT.md`, và mục 9 của hướng dẫn dùng hằng ngày.
- `spreadsheet-check`: báo ô chữ lẫn trong cột số (và bỏ qua phép kiểm dòng tổng sai vì lý do đó), không còn báo "số lưu dạng chữ" cho CSV.
- `vn-admin-documents`: đã đối chiếu thông số trình bày với Nghị định 30/2020/NĐ-CP (06/10/2026).

Khác
- `tools/install_skills.py` (tùy chọn): sao chép skill vào thư mục skill của ứng dụng. `docs/GLOSSARY_VI_EN.md`: bảng thuật ngữ Việt–Anh.
- Giấy phép MIT (`LICENSE`), `.gitignore`, `.gitattributes`.

## v1.0.0 — 2026-10-06

Bản chuẩn đầu tiên. Package là một thư mục tự chứa: giải nén, đổi tên, chạy `tools/init_project.py` là có
project mới. Các phiên bản làm việc trước đó không còn được tính; từ bản này mọi thay đổi ghi tại đây.

Khởi tạo tự động
- `SETUP.bat` / `SETUP.command` chạy `tools/setup_wizard.py`: hỏi ngôn ngữ, tên và năm thông tin ngắn, tự khởi tạo, điền `PROJECT.md`, sao chép đoạn hướng dẫn dán vào Project/cloud. Form "Khởi tạo nhanh" trong `START_HERE.html` / `START_HERE.en.html` tạo `setup_answers.json` để trình hướng dẫn đọc, không hỏi lại.

Cấu trúc và hướng dẫn agent
- `AGENTS.md` là hướng dẫn chung cho mọi agent, có khối "Quy tắc bắt buộc" (tám quy tắc), "Giới hạn công
  việc" (tránh lặp vòng) và "Mức thận trọng cao" cho việc pháp lý, tài chính, số liệu hoặc văn bản gửi ra ngoài.
- `PROJECT.md` giữ ngữ cảnh ổn định; `.agent/` có STATE (khung cố định, ghi đè, tối đa 60 dòng), HANDOFF,
  INDEX, SKILL_INDEX, PENDING_LESSONS và `PACKAGE_INFO.json` (tạo khi khởi tạo).
- `CLAUDE.md`, `GEMINI.md` là adapter mỏng trỏ tới `AGENTS.md`.
- Đoạn hướng dẫn dán vào Project/cloud (tiếng Việt và tiếng Anh) có cả quy tắc thận trọng cao và cách giữ trạng thái.

Skill (`skills/local/shared/`, mười một skill, mỗi skill có cụm kích hoạt trong mô tả)
- office-documents, html-reports, vietnamese-editing, document-comparison, spreadsheet-check,
  meeting-minutes, process-mapping, internal-comms, doc-coauthoring, data-charts, vn-admin-documents.
- `spreadsheet-check` kèm `scripts/check_spreadsheet.py` (chỉ đọc; CSV dùng thư viện chuẩn, Excel cần openpyxl).
- `meeting-minutes`, `document-comparison`, `process-mapping` kèm `references/output-examples.md`.
- Ba mẫu HTML offline (`periodic-report`, `metrics-overview`, `basic-charts`) và các mẫu tài liệu Markdown.

Hai ngôn ngữ
- Hướng dẫn người dùng tiếng Việt (`docs/`, `START_HERE.html`) và tiếng Anh (`docs/en/`, `START_HERE.en.html`),
  có nút chuyển ngôn ngữ hai chiều. Cây `en/` chứa toàn bộ nội dung tiếng Anh
  (hướng dẫn agent, ghi chú `.agent/`, mười một skill kèm tài liệu và mẫu, README); tên file giống hệt bản
  tiếng Việt nên `--lang en` của `tools/init_project.py` chép đè `en/` lên thư mục gốc.

Công cụ (`tools/`, chỉ cần Python 3.8+, không cài thêm)
- `init_project.py`: khởi tạo project (tên, ngôn ngữ, STATE sạch, ghi phiên bản).
- `check_package.py`: kiểm tra package (phiên bản, skill, index, đường dẫn, song ngữ, HTML), `--write-manifest`
  và `--verify` với `MANIFEST.sha256`.
- `build_release.py`: đóng gói ZIP phát hành từ nguồn sạch.
- `build_guides_html.py`: dựng HTML hướng dẫn từ Markdown (`--check` để kiểm đồng bộ).

Giới hạn đã biết
- Bản tiếng Anh (hướng dẫn, skill, mẫu) do agent viết, chưa được người bản ngữ rà soát.
- Chưa chạy thử các skill trong từng ứng dụng agent cụ thể (Claude, Codex, Antigravity).
