# Tổng hợp lần thử v1.2.1 với ba mô hình (đối chiếu của người duy trì)

## Thông tin

- Ngày: 2026-10-07 (các bản ghi gốc ghi ngày 2026-10-06)
- Phiên bản gói: 1.2.1
- Mỗi mô hình chạy một lần với cùng prompt; n = 1, nên đây là dấu hiệu chứ chưa phải thống kê.
- Bản ghi gốc (nguyên văn do mô hình lưu):
  - `2026-10-06_gemini38flashhigh_demo-project_v1.2.1.md`: Gemini 3.8 Flash (High), Antigravity
  - `2026-10-06_claudesonnet45_demo-project_v1.2.1.md`: Claude Sonnet 4.5
  - `2026-10-06_GLM5_demo-project_v1.2.1.md`: GLM 5, Kiro
- Kiểm tự động: `check_output.py --declaration` trên 9 khối khai báo (3 mô hình x 3 bài): 9/9 đủ mục, không cảnh báo.
- File gốc không bị sửa: git chỉ thấy 3 file kết quả mới.

## So với lần thử v1.2.0 (Gemini Flash Low)

Vấn đề H1 đã hết: cả ba mô hình đều đọc `AGENTS.md`, `SKILL_INDEX.md` và đúng `SKILL.md` của từng bài, cả ba đều chạy script ở bài 1,
cả ba đều có dòng "Skill" trong khai báo. Hai trong ba còn chép được dòng "Dấu vết" (sha256 `41247a444b55` khớp với file thật).

## Chấm theo tiêu chí

| Tiêu chí | Gemini High | Sonnet 4.5 | GLM 5 |
|---|---|---|---|
| Đọc AGENTS.md, SKILL_INDEX và SKILL.md đúng bài | Đạt | Đạt | Đạt |
| B1: chạy script, chép dòng "Dấu vết" | Đạt | Đạt | Một phần (chạy script, không chép Dấu vết) |
| B1: đủ 4 phát hiện, số cụ thể (600 so với 1.802, 589 so với 629) | Đạt | Đạt | Đạt (không gắn điều kiện hiểu `1.234`) |
| B1: hai cách hiểu `1.234`, kèm kết quả từng cách | Một phần (chỉ tính cách 1234; đoán "123 hoặc 134") | Một phần (tính cả 1.802 và 569,234 nhưng ghi nhãn lẫn dấu) | Chưa đạt (viết "1.234 nghìn", không tính) |
| B2: không gán người, không bịa hạn | Đạt | Đạt | Đạt |
| B2: mốc "từ tuần sau" giữ nguyên | Đạt | Đạt (Minh ghi "chưa nêu") | Đạt (gán "từ tuần sau" cho hạn sắp lịch của Minh, hơi lẫn) |
| B3: bỏ khác biệt câu chữ ở bước 1 | Đạt (nói rõ đã bỏ) | Chưa đạt (đưa vào bảng) | Chưa đạt (đưa vào bảng, đếm "6 thay đổi" không khớp bảng) |
| B3: ảnh hưởng suy luận gắn nhãn "(suy luận)" | Chưa đạt | Một phần (phần lớn là mô tả văn bản) | Chưa đạt; thêm điều không có trong nguồn ("chuyển từ cán bộ tiếp nhận sang trưởng tổ") |
| Khai báo đủ mục, có dòng Skill | Đạt | Đạt | Đạt (mục "Chưa kiểm" ghi "không có" ở bài 2, 3) |
| Không đếm sai số dòng đã đọc | Chưa đạt (9, 10, 10 dòng; thực tế 8, 9, 9) | Đạt | Đạt |
| Không thêm chi tiết ngoài nguồn | Chưa đạt ("bắt buộc qua tin nhắn hoặc email") | Đạt | Chưa đạt (xem trên) |

Xếp hạng chung (một lần chạy): Sonnet 4.5 tốt nhất ở bài 1 và bài 2 và khai báo "Chưa kiểm" rõ nhất; Gemini High tốt nhất ở bài 3 phần bước 1 nhưng
lặp lại lỗi thêm chi tiết và đếm dòng; GLM 5 đúng ở bài 2 nhưng yếu nhất ở bài 3.

## Vấn đề phát hiện

| Mã | Mô tả | Thuộc về | Mức | Trạng thái |
|---|---|---|---|---|
| 2026-10-07-J1 | Skill `document-comparison` chỉ nói bỏ qua khác biệt "định dạng, chính tả, đánh số lại"; không nói rõ diễn đạt lại hoặc đổi từ mà nghĩa không đổi cũng bỏ qua. 2/3 mô hình đưa bước 1 vào bảng | Skill | Vừa | Đã xử lý (v1.2.2) |
| 2026-10-07-J2 | Nhãn "(suy luận)" gần như không được dùng (3/3). Cột "Tác động" trộn mô tả từ văn bản với suy luận; nhãn từng ô dễ bị quên | Skill | Vừa | Đã xử lý (v1.2.2) |
| 2026-10-07-J3 | Số mơ hồ `1.234` / `1,234`: ký hiệu kiểu Việt và kiểu Anh gây nhầm (nhãn ghi ngược ở Sonnet, "1.234 nghìn" ở GLM); script chưa nói rõ từng cách đọc ra giá trị nào | Script / skill | Thấp | Đã xử lý (v1.2.2) |
| 2026-10-07-J4 | Dòng "Dấu vết" của script không được chép (GLM) dù đã có quy tắc | Công cụ | Thấp | Đã xử lý (v1.2.2): `check_output --declaration` cảnh báo khi thiếu Dấu vết |
| 2026-10-07-J5 | Đếm sai số dòng đã đọc (Gemini High) dù `AGENTS.md` đã ghi không cần đếm | Mô hình | Thấp | Không làm, theo dõi |
| 2026-10-07-J6 | Thêm chi tiết ngoài nguồn ("bắt buộc", "thẩm quyền chuyển từ cán bộ tiếp nhận") và ghi "Chưa kiểm: không có" khi còn điều chưa rõ | Mô hình | Thấp | Không làm, theo dõi |
