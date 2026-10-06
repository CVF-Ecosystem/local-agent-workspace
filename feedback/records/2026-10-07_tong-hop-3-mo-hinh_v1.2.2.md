# Tổng hợp lần chạy lại v1.2.2 với ba mô hình (đối chiếu của người duy trì)

## Thông tin

- Ngày: 2026-10-07
- Phiên bản gói: 1.2.2
- Cùng prompt, cùng ba mô hình như lần v1.2.1; mỗi mô hình một lần chạy (n = 1).
- Bản ghi gốc: `2026-10-07_gemini38flashhigh_demo-project_v1.2.2.md`, `2026-10-07_claudesonnet45_demo-project_v1.2.2.md`, `2026-10-07_GLM5_demo-project_v1.2.2.md`
- Kiểm tự động: `check_output.py --declaration` trên 9 khối khai báo: 9/9 đủ mục, 0 cảnh báo (kể cả cảnh báo Dấu vết mới).
- File gốc không bị sửa: git chỉ thấy 3 file kết quả mới.

## Kết quả các sửa đổi ở v1.2.2

| Vấn đề | Kết quả |
|---|---|
| J1: bỏ khác biệt diễn đạt lại ở bước 1 | Hết: cả 3 mô hình bỏ bước 1 và nói rõ đã bỏ (lần trước 2/3 đưa vào bảng) |
| J2: nhãn suy luận | Hết: cả 3 mô hình dùng tiêu đề cột "Tác động (suy luận)" |
| J3: số mơ hồ `1.234` | Hết: cả 3 nêu hai cách đọc rõ ràng kèm hai tổng (1.802 và 569,23); không còn nhãn ghi ngược |
| J4: dòng Dấu vết | Hết: GLM 5 đã chép Dấu vết (lần trước bỏ sót); cả 3 khớp sha256 `41247a444b55` |

## Chấm theo tiêu chí

| Tiêu chí | Gemini High | Sonnet 4.5 | GLM 5 |
|---|---|---|---|
| Đọc AGENTS.md, SKILL_INDEX và SKILL.md đúng bài | Đạt | Đạt | Đạt |
| B1: chạy script, chép Dấu vết | Đạt | Đạt | Đạt |
| B1: 4 phát hiện, số cụ thể, hai cách đọc `1.234` kèm hai tổng | Đạt (còn đoán "có thể là 123 hoặc 134") | Đạt | Đạt (dòng Số liệu viết lại "1,234", lẫn dấu) |
| B2: không gán người, không bịa hạn, giữ mốc "từ tuần sau" | Đạt | Đạt (tốt nhất: Minh "chưa nêu") | Đạt (gán "từ tuần sau" cho hạn sắp lịch của Minh, hơi lẫn) |
| B3: bỏ bước 1, nêu rõ đã bỏ | Đạt | Đạt | Đạt (số thay đổi "4" khớp bảng) |
| B3: cột Tác động mang nhãn suy luận | Đạt (còn nói "SMS" khi nguồn ghi "tin nhắn") | Đạt | Đạt |
| Khai báo đủ mục, có Skill | Đạt | Đạt | Đạt |
| Không đếm sai số dòng đã đọc | Chưa đạt (9 và 10 dòng, thực tế 8 và 9; B2 "10", thực tế 9) | Đạt | Đạt |
| Mục "Chưa kiểm" có nội dung thật | Đạt | Đạt (tốt nhất) | Chưa đạt (ghi "không có" ở bài 2 và 3) |
| Không thêm chi tiết ngoài nguồn | Đạt (gần như) | Đạt | Đạt |

Kết luận: các lỗi ở v1.2.1 do skill và script gây ra đã hết. Phần còn lại là thói quen riêng của từng mô hình.

## Vấn đề phát hiện

| Mã | Mô tả | Thuộc về | Mức | Trạng thái |
|---|---|---|---|---|
| 2026-10-07-K1 | Script không in số dòng của từng phát hiện, nên mô hình tự đánh số theo quy ước khác nhau (Gemini dùng dòng trong file, Sonnet dùng thứ tự dòng dữ liệu, không nói rõ) | Script | Thấp | Mới (đề xuất: script in số dòng gốc trong file) |
| 2026-10-07-K2 | Gemini High vẫn đếm sai số dòng đã đọc dù `AGENTS.md` đã ghi không cần đếm (J5 lặp lại) | Mô hình | Thấp | Không làm, theo dõi |
| 2026-10-07-K3 | GLM 5 ghi "Chưa kiểm: không có" khi còn điều chưa rõ (J6 lặp lại); Gemini High thêm suy đoán "123 hoặc 134" và "SMS" | Mô hình | Thấp | Không làm, theo dõi |
