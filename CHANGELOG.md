# Changelog

Định dạng phiên bản: `MAJOR.MINOR.PATCH`. Số phiên bản nằm trong `VERSION`; hướng dẫn nâng cấp ở
`docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`.

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
