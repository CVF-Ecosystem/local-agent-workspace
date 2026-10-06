---
name: data-charts
description: >-
  Gợi ý chọn và dựng biểu đồ từ dữ liệu bảng thành một file HTML mở offline (SVG thuần):
  cột, đường, cột xếp chồng, vành khuyên, thẻ KPI, bảng kèm thanh. Có mẫu thư viện biểu đồ
  để lấy cấu trúc. Dùng khi cần "vẽ biểu đồ"; báo cáo nhiều phần dùng thêm html-reports.
  Kích hoạt khi người dùng nói: “vẽ biểu đồ”, “trực quan hóa số liệu”, “biểu đồ cột/đường/tròn”, “thẻ KPI”.
metadata:
  version: "1.0"
---

# Biểu đồ từ dữ liệu

Giúp biến một bảng số liệu thành biểu đồ đọc được, đúng số và mở được không cần mạng.
Không dành cho ứng dụng web hoặc hệ thống dashboard triển khai.

## Phạm vi đầu ra

- Người dùng đưa dữ liệu và nói "vẽ biểu đồ", "trực quan hóa": giao **biểu đồ** (một đến vài
  hình), không tự mở rộng thành báo cáo.
- Người dùng nói "báo cáo", "dashboard", "tổng quan": cân nhắc `html-reports` cho khung
  trang; vẫn lấy cách dựng biểu đồ từ skill này.
- Chỉ có một hai con số hoặc vài điểm dữ liệu: nói thẳng bằng thẻ số hoặc bảng, không ép
  thành biểu đồ.

## Cách làm

1. **Xác định thông điệp** mỗi biểu đồ cần cho thấy (so sánh, xu hướng, cơ cấu, chi tiết).
   Chọn loại theo `references/chart-selection.md`.
2. **Kiểm tra dữ liệu trước khi vẽ**: ô thiếu, đơn vị, kỳ, tổng. Dữ liệu từ Excel chưa rõ chất
   lượng: cân nhắc `spreadsheet-check`. Không thay ô thiếu bằng 0.
3. **Dựng** từ `assets/basic-charts.html`: mở file, lấy hàm vẽ phù hợp, thay khối dữ liệu
   `report-data` và tiêu đề. Chỉ giữ biểu đồ được dùng; bỏ phần còn lại của mẫu.
4. **Trình bày:** tiêu đề nêu điều cần thấy, ghi đơn vị, kỳ và nguồn, nhãn trực tiếp, bảng dữ
   liệu đi kèm để tra số chính xác.

## Quy tắc trình bày

- Cột bắt đầu từ 0. Không dùng 3D, không đổ bóng, không trang trí không mang dữ liệu.
- Tối đa khoảng 5 màu; màu không là cách duy nhất phân biệt (thêm nhãn hoặc dạng nét).
- Một hình chỉ một thông điệp; so sánh nhiều nhóm thì tách hình thay vì nhồi một biểu đồ.
- Biểu đồ cho thấy xu hướng, chưa chứng minh nguyên nhân; không viết kết luận nhân quả.
- Giữ nhãn `isDemo` cho tới khi dữ liệu thật thay vào; chỉ đổi `isDemo` sang `false` khi
  số liệu, tiêu đề, kỳ và nguồn đều là của người dùng.

## Kỹ thuật

SVG thuần và JavaScript nội tuyến, font hệ thống, không CDN. Chỉ dùng thư viện ngoài khi
cần tương tác phức tạp (ví dụ biểu đồ mạng, bản đồ); khi đó nhúng thư viện vào file hoặc
nói rõ file cần mạng. Tương tác thông thường (lọc theo kỳ, hiện số khi rê chuột) đã đủ cho
hầu hết báo cáo.

## Khi nào nói không

Dữ liệu quá ít hoặc không so sánh được; người dùng muốn biểu đồ để "chứng minh" điều dữ liệu
không cho thấy; yêu cầu cần thiết kế đồ họa nâng cao hoặc bản đồ chuyên dụng. Nói rõ lý do và
đề xuất bảng hoặc biểu đồ đơn giản hơn.

## Khi giao

Số trên hình khớp bảng nguồn, tiếng Việt hiển thị đúng, in được, và không có yêu cầu mạng.
Mở bằng trình duyệt nếu có công cụ; nếu không, nói rõ chưa xem trên màn hình. Đạt thì dừng,
không thêm biểu đồ hoặc hiệu ứng.
