# Changelog

Định dạng phiên bản: `MAJOR.MINOR.PATCH`. Số phiên bản nằm trong `VERSION`; hướng dẫn nâng cấp ở
`docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`.

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
