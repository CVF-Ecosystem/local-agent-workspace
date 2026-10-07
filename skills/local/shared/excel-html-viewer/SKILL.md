---
name: excel-html-viewer
description: >-
  Gợi ý dựng công cụ HTML một file, chạy offline, đọc file Excel của người dùng để xem số liệu trực quan
  (thẻ chỉ số, bộ lọc, biểu đồ, danh sách việc cần chú ý, tab kiểm tra dữ liệu). Chịu được tên sheet, tên cột
  và giá trị gõ tay không chuẩn. Không dành cho báo cáo từ dữ liệu cố định (xem `html-reports`) hay kiểm tra file (xem `spreadsheet-check`).
  Kích hoạt khi người dùng nói: “dashboard đọc file Excel”, “xem số liệu trực quan từ Excel”, “công cụ HTML chạy offline”, “bảng điều hành đọc Excel”.
metadata:
  version: "1.0"
---

# Công cụ HTML đọc file Excel

Dùng khi người dùng muốn xem số liệu từ các file Excel mà không cài phần mềm và không đưa dữ liệu lên dịch vụ ngoài.
Kiến trúc thống nhất: **Excel là lớp nhập, HTML là lớp xem**; dữ liệu ở lại trình duyệt của người dùng. Dựng sổ nhập
thì xem `excel-workbooks`; biểu đồ xem `data-charts`; báo cáo từ dữ liệu có sẵn xem `html-reports`.

## Cách dựng

- Một file HTML duy nhất, CSS và JavaScript nhúng sẵn, không CDN. **Cấm** `<script src="http...">`, `<link href="http...">`, `fetch`, `XMLHttpRequest` và mọi tài nguyên mạng: người dùng mở file khi không có mạng. Bản "có CDN" và bản "offline" không được giao song song; chỉ giao bản offline. Giao xong tự kiểm: `grep -E 'src="https?:|href="https?:|fetch\(' file.html` phải trống (chuỗi `http://` trong tên miền XML của thư viện thì không tính). Đọc `.xlsx` cần thư viện đọc Excel (ví dụ bản mini của SheetJS)
  nhúng vào file; nhúng thì thay chuỗi `</script` trong thư viện bằng `<\/script`. Nhúng thẳng thành thẻ `<script>` thường (không cần mã hóa base64). Chỉ đọc CSV thì không cần thư viện.
- Không có thư viện và không có mạng để tải: nhúng `assets/xlsx-mini-reader.js` (đọc `.xlsx` không cần thư viện ngoài; cần trình duyệt có `DecompressionStream`,
  đã thử với nhiều file Excel thật). Chỉ đọc giá trị: ngày là số serial cần tự đổi, công thức chưa có giá trị đã tính trả về trống. Nút xuất .xlsx vẫn cần thư viện ghi.
- Lời nhắc yêu cầu đọc `.xlsx` thì công cụ PHẢI đọc được `.xlsx`. Không để ô chọn file nhận `.xlsx` mà bên trong báo "chưa hỗ trợ"; không thể thì nói thẳng là chưa đáp ứng, đừng gọi là hoàn thành.
- Viết mã nguồn thành các file rời rồi dùng script build để ghép thư viện và dữ liệu mẫu; không sửa tay file lớn.
  Giữ mã nguồn dựng cạnh sản phẩm (hoặc nói người dùng sao lưu), vì thư mục làm việc tạm có thể mất.
- Không tin giá trị công thức lưu trong file (file tạo bằng openpyxl không có giá trị tính sẵn): tự tính lại từ dữ liệu gốc,
  bỏ qua ô công thức chưa có giá trị. Công cụ chỉ đọc, không ghi ngược vào file.

## Chịu được dữ liệu và tên gọi không chuẩn

Người dùng hay đổi tên sheet, gõ hoa thường lẫn lộn, có dấu hoặc không dấu, thừa khoảng trắng. Vì vậy:

1. Mọi so khớp chữ (tên sheet, tiêu đề cột, giá trị ô, mã) đi qua MỘT hàm chuẩn hóa: hạ chữ, bỏ dấu (NFD), đổi đ thành d,
   đổi các loại gạch ngang về một loại, gộp khoảng trắng kể cả NBSP, cắt hai đầu.
2. Không nhận sheet theo tên cố định: quét mọi sheet và chấm điểm theo số cột tiêu đề khớp; sheet nào đúng vai trò nào thì nhận
   vai trò đó, sheet thừa bỏ qua. Sau khi nạp hiển thị "Đã nhận sheet: vai trò → tên sheet" để người dùng kiểm tra.
3. Đọc cột theo tên tiêu đề: khớp chính xác trước, khớp đầu chuỗi sau; tự dò dòng tiêu đề trong khoảng 12 dòng đầu. Tên cột là điều kiện
   cố định duy nhất, nên dặn người dùng giữ tên cột.
4. Chuẩn hóa cả giá trị gõ tay trước khi so hoặc tra: mã ("gw 01" và "gw-01" cùng thành "GW01"), loại và trạng thái, cờ Có/Không, mã liên kết
   giữa hai sheet. Giá trị vẫn lạ sau chuẩn hóa thì báo cảnh báo, không bỏ qua lặng lẽ.
5. Ngày và số đọc được nhiều dạng (số serial Excel, `dd/mm/yyyy`, ISO, "1.234,5", "hh:mm"). Ghi số dòng Excel vào mỗi bản ghi để lỗi chỉ đúng dòng cần sửa.
6. **Ngày serial**: ô ngày thật của Excel đến dạng số (ví dụ `46296`). Đổi `serial → ngày` (mốc 1899-12-30; chỉ coi là ngày khi nằm trong khoảng hợp lý như 1990–2100 và cột là cột ngày) rồi hiển thị `dd/mm/yyyy`; không để số trần ra bảng. Kiểm ngày phải chạy cả cho serial lẫn chuỗi: chuỗi không có dấu `/` hoặc `-` vẫn phải thử đọc.
7. **Số âm và giá trị vô lý**: cột lượng, số lượng, tiền, giờ không được âm (trừ khi sổ quy định); số âm báo lỗi từng dòng kèm số dòng, không chỉ bắt chữ trong ô số. Báo thêm ô số chứa chữ, ô trống ở cột bắt buộc, trùng mã phiếu.
8. **Nhiều sheet**: quét mọi sheet, mỗi sheet dò dòng tiêu đề riêng (không chỉ sheet đầu, không giả định sheet đầu là bảng chính), đọc được nhiều bảng cùng lúc (ví dụ nhật ký cấp phát và danh mục phương tiện) và hiện "Đã nhận sheet: vai trò → tên sheet". Sheet hướng dẫn, sheet chỉ có công thức và sheet mẫu/mock không được tính vào số liệu. Số liệu của KPI lấy từ chính các bảng đã đọc: không để thẻ chỉ số luôn bằng 0 vì mã không đọc loại dữ liệu đó. Nếu tên đầu cột trong file thật khác cụm đã định (ví dụ "Lượng cấp (lít)" thay "Số lít"), chấp nhận cả hai; sau khi dựng, thử với sổ thật của người dùng và báo số dòng đọc được trên từng sheet, đọc ra 0 dòng thì chưa xong.

## Dữ liệu thiếu, lỗi, ngưỡng

- Cảnh báo ba cấp, hiển thị ở tab kiểm tra và khối "Việc cần chú ý": cả file (không tìm thấy bảng nào, nêu cần cột gì); từng bảng (thiếu cột nào,
  hậu quả gì); từng dòng (kèm số dòng). Chỉ cảnh báo từng dòng thì người dùng không đoán được nguyên nhân gốc.
- Ngưỡng lấy từ ô tham số trong sổ, cho nhập thử trên thanh lọc (không ghi ngược). Ô trống là "chưa quy định", hiện thông báo và không gắn cờ;
  ngưỡng đề xuất ghi rõ "chờ phê duyệt".
- Chống treo: không lặp theo khoảng thời gian vô hạn khi file rỗng hoặc chưa chọn kỳ.
- Dữ liệu mẫu nhúng sẵn (nếu sinh ngẫu nhiên thì dùng hạt giống cố định, có vài lỗi cố ý để minh họa kiểm tra), huy hiệu "Dữ liệu mẫu / File: tên-file"
  luôn hiện, và nút xuất file Excel mẫu đúng bố cục để thử vòng nhập rồi xem lại.

## Giao diện

Thẻ chỉ số bấm được, khối "Việc cần chú ý" ở đầu trang; bấm số hoặc cột mở bảng chi tiết có lọc, sắp xếp, xuất CSV (thêm BOM để Excel đọc đúng tiếng Việt);
chuyển biểu đồ và bảng số; giao diện sáng và tối; in hoặc lưu PDF; dùng được trên màn hình hẹp. Biểu đồ theo `data-charts`: màu trạng thái luôn kèm
biểu tượng và chữ, một trục, có chú giải và bảng số.

## Kiểm thử và giới hạn khi giao

Danh sách kiểm thử: `references/test-checklist.md`. Khi giao, nói rõ: công cụ chỉ xem, không sửa file, không tự cập nhật (mở lại mỗi lần),
không lưu lịch sử; số liệu chỉ có ý nghĩa sau khi dữ liệu nhập đã được kiểm kê và chuẩn hóa; phần chưa thử (trình duyệt nào, Excel thật).
