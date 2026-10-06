---
name: html-reports
description: >-
  Gợi ý tạo hoặc cập nhật báo cáo HTML tiếng Việt, báo cáo định kỳ và trang tổng quan
  KPI từ dữ liệu được cung cấp. Có hai mẫu một-file offline để tham khảo khi phù hợp;
  không dành cho xây ứng dụng web, backend hay hệ thống dashboard triển khai.
  Kích hoạt khi người dùng nói: “báo cáo HTML”, “dashboard”, “trang tổng quan chỉ số”, “báo cáo định kỳ dạng web”.
metadata:
  version: "1.0"
---

# Báo cáo HTML gọn nhẹ

Chọn cách làm theo mục đích, dữ liệu và môi trường đọc. Có thể dùng native skill,
công cụ sẵn có hoặc mẫu dưới đây; không có thứ tự ưu tiên bắt buộc.

## Chọn đầu ra

Hỏi một chỉ số hoặc cần một biểu đồ thì không tự mở rộng thành báo cáo đầy đủ.
Khi cập nhật báo cáo cũ, giữ bố cục phù hợp và sửa phần được giao. Với báo cáo mới,
tập trung vào những chỉ tiêu và nhận xét giúp người đọc hiểu hoặc ra quyết định.

Một file HTML tự chứa thường thuận tiện để mở local và chia sẻ. Không cần framework,
server, build pipeline hay thư viện ngoài chỉ vì đầu ra là HTML. Có thể dùng công cụ
khác khi thực sự phù hợp với yêu cầu; không phải mọi báo cáo đều cần cùng một mẫu.

## Hai mẫu tham khảo

- `assets/periodic-report.html`: nhận xét, KPI, diễn biến theo kỳ và bảng nguồn.
- `assets/metrics-overview.html`: tổng quan có bộ lọc kênh/kỳ, KPI và bảng chi tiết.

Hai mẫu được viết mới cho workspace, không phải bản sao mẫu Lieflat Charts.
Chúng dùng CSS/JavaScript nội tuyến, font hệ thống, không tải dependency từ mạng.
Nội dung và dữ liệu mẫu có nhãn minh họa; không phải số liệu thật của người dùng.
Mở mẫu phù hợp, sao chép sang đầu ra và điều chỉnh; không cần đọc hoặc so sánh cả hai.

Cần chọn loại biểu đồ hoặc dựng biểu đồ SVG riêng: dùng `data-charts` (có mẫu và hướng dẫn chọn biểu đồ).
Số liệu lấy từ bảng tính chưa kiểm tra: cân nhắc `spreadsheet-check` trước.

## Khi dùng mẫu

Dữ liệu nằm trong `<script id="report-data" type="application/json">`. Có thể sửa
khối này và bố cục theo yêu cầu. Mỗi mẫu ghi chú ý nghĩa các trường ngay trong file.
Giữ JSON hợp lệ; nếu chuỗi chứa `</script>`, mã hóa dấu `<` thành `\u003c` khi nhúng.

Thay cả số liệu, tiêu đề, kỳ báo cáo, nguồn và nhận xét minh họa. Chỉ chuyển
`isDemo` sang `false` khi đầu ra đã dùng dữ liệu thật được cung cấp; không bỏ nhãn
minh họa chỉ để bản mẫu trông như sản phẩm hoàn tất.

Với dữ liệu xử lý hồ sơ, `onTime` là số trong `closed` hoàn tất đúng hạn. Tỷ lệ tổng
được tính bằng tổng tử số / tổng mẫu số; ô thiếu dữ liệu không thay bằng 0 theo suy
đoán. Số tồn cuối kỳ không cộng qua các tuần. Thay cách tính khi định nghĩa nghiệp vụ
thực tế khác; biểu đồ là phương tiện trình bày, không tự cung cấp kết luận nguyên nhân.

## Khi giao

Xem các điểm ảnh hưởng trực tiếp đến sử dụng: số liệu/tỷ lệ khớp nguồn, bộ lọc được
yêu cầu hoạt động, tiếng Việt đọc được, file mở đúng môi trường dự kiến. Chỉ dùng
browser kiểm tra khi có công cụ phù hợp; nói rõ phần chưa kiểm tra, không tuyên bố giả.
Khi đầu ra đáp ứng yêu cầu, dừng thay vì thêm tính năng hoặc tiếp tục đánh bóng.
