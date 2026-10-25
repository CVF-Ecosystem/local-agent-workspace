---
name: html-reports
description: >-
  Tạo hoặc cập nhật báo cáo HTML tiếng Việt, báo cáo định kỳ hoặc trang tổng quan KPI từ
  dữ liệu được cung cấp; có hai mẫu một-file offline để tham khảo khi phù hợp. Dùng cho
  báo cáo nhiều phần, không phải ứng dụng web hoặc dashboard triển khai. Kích hoạt khi
  người dùng nói: “báo cáo HTML”, “dashboard”, “trang tổng quan chỉ số”, “báo cáo định kỳ
  dạng web”.
metadata:
  version: "1.3"
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

## Chuẩn trình bày (mặc định cho báo cáo và dashboard mới)

Mục tiêu: trông như báo cáo trình lãnh đạo, không như công cụ kỹ thuật. Hai mẫu trong `assets/` đã theo chuẩn này
(khối CSS "Chuẩn trình bày báo cáo"); dựng trang mới thì chép khối đó.

- **Dải tiêu đề** nền navy chuyển màu (`--band1` → `--band2`), chữ trắng: dòng nhỏ viết hoa giãn chữ là tên đơn vị
  hoặc kỳ, tiêu đề 26px đậm, một dòng mô tả hoặc "Kỳ báo cáo: …" tự cập nhật kèm nhãn nguồn dữ liệu; nút In bên phải.
- **Thanh lọc / thẻ đầu trang** là thẻ trắng bo 12px, bóng nhẹ, chồm lên dải tiêu đề; thanh lọc dính đầu trang khi cuộn
  (chỉ màn rộng).
- **Mục đánh số La Mã** (I, II, III…): nhãn số nền navy bo góc cạnh tiêu đề 16px. Thứ tự gợi ý: tổng quan → diễn biến →
  bảng tổng hợp → phân tích → chi tiết → kiểm tra dữ liệu (luôn cuối).
- **Thẻ chỉ số**: sọc màu 4px bên trái (mỗi thẻ một màu nhóm), nhãn viết hoa 11px, số 30px chữ số đều (`tabular-nums`),
  dòng phụ dưới đường gạch chấm.
- **Khối "⚠ Việc cần chú ý"**: viền trái vàng; mỗi mục là một câu có số, nên dẫn tới mục chi tiết.
- **Bảng**: tiêu đề viết hoa 11px nền nhạt, dòng xen màu, số căn phải, dòng tổng nền nhạt. Trạng thái dạng nhãn bo tròn có
  ký hiệu và chữ (▲ đỏ, ● xanh); không dựa riêng vào màu.
- **Màu**: khai báo token trên `:root` và một bộ cho chế độ tối. Màu nhóm biểu đồ `#2a78d6 #eb6834 #1baf7a #eda100 #a8a7a1`;
  trạng thái đỏ `#d03b3b`/`#fdecec`, xanh `#0e8f4f`/`#e6f6ee`, vàng `#b97a00`/`#fff5df`.
- **Phông**: chỉ phông có sẵn trên máy (`"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`). Không tải phông web
  (Google Fonts…): trang phải mở offline và không gọi ra ngoài khi mở.
- **Bản in** A4 ngang (`@page{size:A4 landscape;margin:10mm}`): nền trắng, tiêu đề chữ navy có gạch dưới, ẩn nút và thanh lọc,
  giữ màu (`print-color-adjust:exact`), thẻ không bị cắt ngang nhưng bảng dài được ngắt trang (`tr{break-inside:avoid}`,
  `thead{display:table-header-group}`), khối ký chỉ hiện khi in ("Người lập" / chức danh duyệt, "(Ký, ghi rõ họ tên)").
- **Màn hẹp** (≤860px): thẻ 2 cột, lưới 1 cột, thanh lọc không dính, không tràn ngang.
- **Tiết chế**: không lặp thông tin (đã có kỳ và nhãn nguồn thì không thêm dòng liệt kê tên file; nhiều file chỉ ghi số lượng);
  thông báo chỉ khi có việc cần làm; ô trống có nghĩa nghiệp vụ thì ghi chữ rõ ("Đúng giờ") thay vì "–".

### Đổi theo đơn vị

Chỉ đổi: tên đơn vị ở dòng nhỏ, màu chủ đạo (`--band1`, `--band2`, `--navy`), phông bản in nếu đơn vị quy định
(ví dụ Times New Roman), màu tiêu đề bảng nếu muốn khớp sổ Excel của đơn vị, và chức danh trong khối ký. Thông tin riêng
của đơn vị (tên, người ký) để ở skill riêng của project, không đưa vào skill này.

Đơn vị chưa có màu riêng thì không hỏi mở "thích màu gì". Hỏi bối cảnh (trang trọng gửi lãnh đạo, nội bộ hiện đại, kỹ thuật,
trình chiếu) rồi đưa 2 - 3 phương án, mỗi phương án một dòng mô tả: xanh navy (mặc định, trang trọng), xanh dương sáng (nội
bộ, hiện đại), xám trung tính (kỹ thuật, pháp lý), đỏ rượu (phân tích, phản biện). Người dùng đưa mã màu hoặc logo thì dùng
đúng màu đó và kiểm độ tương phản chữ trên nền ở cả chế độ sáng và tối.

### Làm lại giao diện một công cụ có sẵn

Thêm một khối CSS ghi đè đặt sau CSS cũ và chỉ sửa phần đầu trang, chân trang; giữ nguyên JavaScript tính toán và `id`
các phần tử. Lưu thành file mới ("… (bản 2).html"), không ghi đè bản đang dùng. Lưu ý: thuộc tính rút gọn `border` đặt lại
`border-image`, nên quy tắc cũ có `border:none` với độ ưu tiên cao hơn sẽ xóa dải nền làm bằng `border-image`. Kiểm tra mọi tab,
chế độ tối, màn 390px và bản PDF.

## Khi giao

Xem các điểm ảnh hưởng trực tiếp đến sử dụng: số liệu/tỷ lệ khớp nguồn, bộ lọc được
yêu cầu hoạt động, tiếng Việt đọc được, file mở đúng môi trường dự kiến. Chỉ dùng
browser kiểm tra khi có công cụ phù hợp; nói rõ phần chưa kiểm tra, không tuyên bố giả.
Khi đầu ra đáp ứng yêu cầu, dừng thay vì thêm tính năng hoặc tiếp tục đánh bóng.
