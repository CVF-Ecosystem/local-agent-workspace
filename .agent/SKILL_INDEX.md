# SKILL INDEX

Danh mục để tìm skill theo công việc. Không phải thứ tự ưu tiên. Khi yêu cầu khớp cột "Use when" của một skill,
đọc `SKILL.md` của skill đó trước khi làm (xem `AGENTS.md`). Có thể dùng native skill, local skill, kết hợp hoặc xử lý trực tiếp.

| Skill ID | Origin | Scope | Location / Provider | Use when | Status | Provenance / Notes |
|---|---|---|---|---|---|---|
| office-documents | LOCAL | SHARED | skills/local/shared/office-documents/SKILL.md | Soạn hoặc sửa tài liệu nghiệp vụ có nguồn/mẫu; các ví dụ SOP, biểu mẫu, cập nhật nội bộ có ích. | AVAILABLE | Biên soạn mới; không có dependency riêng. |
| html-reports | LOCAL | SHARED | skills/local/shared/html-reports/SKILL.md | Cần báo cáo HTML hoặc trang tổng quan chỉ số; mẫu một-file offline có ích. | AVAILABLE | Biên soạn mới; hai mẫu HTML tự chứa, dữ liệu minh họa. |
| vietnamese-editing | LOCAL | SHARED | skills/local/shared/vietnamese-editing/SKILL.md | Có yêu cầu biên tập tiếng Việt, giảm sáo rỗng hoặc theo giọng văn cụ thể. | AVAILABLE | Tùy chọn; không tự dùng như bước hậu xử lý. Có references/machine-style-signs.md (viết lại từ ý tưởng skill humanizer). |
| internal-comms | LOCAL | SHARED | skills/local/shared/internal-comms/SKILL.md | Viết báo cáo tiến độ (3P), thông báo, bản tin, FAQ, báo cáo sự cố để người trong đơn vị đọc nhanh. | AVAILABLE | Viết lại bằng tiếng Việt từ ý tưởng skill internal-comms (repo tham chiếu, xem docs/NGUON_THAM_KHAO_VI.md); không dependency. |
| doc-coauthoring | LOCAL | SHARED | skills/local/shared/doc-coauthoring/SKILL.md | Tài liệu lớn, người dùng muốn trao đổi sâu từng bước (gom ngữ cảnh, dàn ý, soạn từng mục, soát cuối). Hỏi trước khi dùng. | AVAILABLE | Viết lại từ ý tưởng skill doc-coauthoring; giới hạn số vòng, không agent phụ; không dependency. |
| data-charts | LOCAL | SHARED | skills/local/shared/data-charts/SKILL.md | Vẽ biểu đồ từ bảng số liệu thành HTML offline (SVG); cần chọn dạng biểu đồ hoặc lấy mẫu dựng biểu đồ. | AVAILABLE | Viết lại từ ý tưởng skill lieflat-charts; mẫu SVG viết mới, không dùng mã hay mẫu của repo gốc; không dependency. |
| document-comparison | LOCAL | SHARED | skills/local/shared/document-comparison/SKILL.md | Đối chiếu hai phiên bản quy định, quy trình, biểu mẫu, hợp đồng; cần bảng thay đổi có ý nghĩa. | AVAILABLE | Biên soạn mới; không có dependency riêng. |
| spreadsheet-check | LOCAL | SHARED | skills/local/shared/spreadsheet-check/SKILL.md | Kiểm tra nhanh Excel/CSV trước khi lấy số cho báo cáo hoặc dashboard; chỉ báo phát hiện, không sửa gốc. | AVAILABLE | Biên soạn mới; kèm scripts/check_spreadsheet.py (CSV: thư viện chuẩn; Excel: cần openpyxl, tùy chọn). |
| meeting-minutes | LOCAL | SHARED | skills/local/shared/meeting-minutes/SKILL.md | Lập biên bản hoặc tóm tắt họp từ ghi chú/bản ghi; tách quyết định, việc cần làm, vấn đề chưa chốt. | AVAILABLE | Biên soạn mới; không dependency. |
| process-mapping | LOCAL | SHARED | skills/local/shared/process-mapping/SKILL.md | Mô tả quy trình bằng bảng bước, RACI, sơ đồ luồng khi cần. | AVAILABLE | Biên soạn mới; Mermaid/SVG tùy nơi dùng, không dependency cài đặt. |
| vn-admin-documents | LOCAL | SHARED | skills/local/shared/vn-admin-documents/SKILL.md | Soạn văn bản hành chính đúng thể thức (công văn, tờ trình, báo cáo, thông báo): số/ký hiệu, địa danh, trích yếu, nơi nhận, trình bày. | AVAILABLE | Biên soạn mới; căn cứ tham khảo là quy định về công tác văn thư, luôn kiểm bản hiện hành hoặc quy chế đơn vị; không dependency. |
| excel-workbooks | LOCAL | SHARED | skills/local/shared/excel-workbooks/SKILL.md | Dựng sổ theo dõi, form nhập liệu, báo cáo tự tổng hợp hoặc phụ lục tính bằng Excel (openpyxl, công thức thật). | AVAILABLE | Viết lại từ kinh nghiệm thực tế của người duy trì, đã bỏ dữ liệu riêng của đơn vị; kèm ghi chú kỹ thuật; cần openpyxl. |
| excel-html-viewer | LOCAL | SHARED | skills/local/shared/excel-html-viewer/SKILL.md | Dựng công cụ HTML một file, chạy offline, đọc file Excel của người dùng để xem số liệu (thẻ chỉ số, bộ lọc, tab kiểm tra dữ liệu). | AVAILABLE | Viết lại từ kinh nghiệm thực tế của người duy trì; đọc .xlsx cần thư viện đọc Excel nhúng vào file. |

## Cách đọc danh mục

`Use when` gợi ý phạm vi phù hợp; agent vẫn cân nhắc yêu cầu và công cụ thực có.
Khi biết rõ skill cần dùng, có thể mở trực tiếp. Chỉ đọc tài nguyên hỗ trợ liên quan.
`ACTIVE` nghĩa thường dùng trong dự án, không nghĩa tự nạp vào mọi phiên.

Origin: `LOCAL` (tự biên soạn), `EXTERNAL` (nhập ngoài), `PROVIDER` (native).
Scope: `SHARED` (dùng chung), `PROJECT` (riêng dự án), `GLOBAL` (theo provider), `PACK` (gói lĩnh vực cài bằng `tools/pack.py`).
Status: `AVAILABLE` (sẵn dùng), `ACTIVE` (thường dùng), `REVIEW` (đang xem xét),
`DISABLED` (người dùng đã chọn không dùng).

## Khi thay đổi thư viện

Ghi nhận mục đích, vị trí, nguồn gốc và dependency đáng chú ý khi thêm hoặc sửa lớn.
Không đánh giá/đăng ký lại cùng một skill mỗi lần dùng. Người dùng quyết định việc
thêm, bỏ hoặc sửa skill; lựa chọn tác nghiệp giữa những skill sẵn có không cần một
lượt xin duyệt riêng. Không tự chuyển/xóa skill của người dùng.

Có thể thêm capability native đã xác nhận hữu ích ở phiên/provider cụ thể. Không
điền tên skill giả định; mục native không bảo đảm provider khác có khả năng đó.
Nguồn tham khảo và kết quả audit của các skill mới: `docs/NGUON_THAM_KHAO_VI.md` (tính từ project root).
