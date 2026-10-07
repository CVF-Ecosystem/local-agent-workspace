# Kiểm thử công cụ HTML đọc Excel

Chạy bằng trình duyệt tự động (ví dụ Playwright với Chromium) khi có; không có thì nói rõ chưa chạy tự động.

0. Thử với file `.xlsx` THẬT của người dùng (và một file đã đổi thứ tự cột), không chỉ CSV hay dữ liệu mẫu nhúng sẵn; file không đọc được thì công cụ chưa xong.
0b. Quét mạng: `grep -E 'src="https?:|href="https?:|fetch\(|XMLHttpRequest' file.html` phải trống; nếu mở được DevTools, tab Network khi mở file không có yêu cầu ra ngoài.
0c. Lỗi dữ liệu phải bị bắt: ô ngày thật (serial) hiển thị `dd/mm/yyyy`; số âm ở cột lượng; chữ trong ô số; ngày ngoài khoảng; mỗi lỗi hiện đúng số dòng Excel.
0d. Nhiều sheet: thử file có nhiều sheet (hướng dẫn, mock, bảng chính, danh mục); báo được số dòng đọc trên từng sheet; thẻ chỉ số không bằng 0 khi sheet có dữ liệu.
1. Không lỗi JavaScript ở mọi tab; chụp ảnh từng tab, cả chế độ tối và màn hình hẹp, rồi xem ảnh.
2. Số liệu khớp Excel gốc. Xuất file Excel mẫu rồi nạp lại: các chỉ số phải giống hệt lúc dùng dữ liệu mẫu.
3. File đã sửa: đổi thứ tự cột; ngày ở dạng chữ; số dạng chữ kiểu Việt; ngưỡng để trống; chèn dòng trống.
4. Đổi tên sheet (không dấu, hoa thường lẫn lộn, thừa khoảng trắng, tên lạ không liên quan, thêm sheet thừa) và giá trị gõ tay lộn xộn (mã " gw 01",
   loại " HU ", mã viết thường, Unicode tổ hợp): kết quả phải giống hệt file chuẩn. So nguyên chuỗi thẻ chỉ số VÀ cả khối "Việc cần chú ý",
   phân nhóm, biểu đồ; chỉ so tổng chỉ số thì không thấy lỗi nhận sai danh mục làm mọi thứ rơi vào "Chưa phân nhóm".
5. Cảnh báo khi nạp: thiếu danh mục, thiếu cột, thiếu bảng chính, file trống, file không đúng định dạng: mỗi trường hợp phải hiện đúng thông báo, không treo.
6. Thẻ chỉ số, lọc, sắp xếp, xuất CSV; đổi ngưỡng cảnh báo rồi dữ liệu thô được parse lại, nhớ kỳ đang chọn.
7. In PDF: ẩn thanh điều khiển; thẻ và biểu đồ không bị cắt ngang (`break-inside: avoid`), nhưng thẻ chứa bảng dài phải cho ngắt trang
   (`break-inside: auto`, `tr { break-inside: avoid }`, `thead { display: table-header-group }`), nếu không cả thẻ bị đẩy sang trang mới để trang trống.
   Kiểm bằng `page.pdf()` rồi xem ảnh ghép các trang.
8. Hiệu năng với file đầy tải (đã đo: 200 mục chính và 2.000 bản ghi phụ nạp khoảng 1,2 giây).
9. Màn hình hẹp không tràn ngang; chế độ tối đọc được.

## Lỗi đã gặp

- Dòng chú thích nhóm cũng chứa cụm từ tiêu đề nên dò nhầm dòng tiêu đề: dùng cụm đặc trưng.
- Hàm chuẩn hóa tiêu đề bỏ phần trong ngoặc làm mất cụm đặc trưng nằm trong ngoặc (ví dụ "Nguyên nhân (danh sách gốc)"): sheet danh mục không được nhận.
  Khi dò cụm đặc trưng, dùng bản chuẩn hóa KHÔNG bỏ ngoặc.
- File mẫu trống làm trình duyệt treo vì lặp theo khoảng ngày vô hạn.
- Nút xuất bằng bản mini của thư viện vẫn có `book_new`, `aoa_to_sheet`, `book_append_sheet`, `writeFile`; xuất tên sheet chuẩn để mở lại được
  bằng chính công cụ. Chỉ xuất dữ liệu thô, không có công thức hay dropdown.
- Bảng màu phân loại: màu xám "chưa phân nhóm" cố ý trung tính nên không đạt ngưỡng sắc độ; độ tương phản thấp bù bằng nhãn số và bảng số.
