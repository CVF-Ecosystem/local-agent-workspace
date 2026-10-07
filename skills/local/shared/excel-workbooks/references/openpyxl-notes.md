# Ghi chú kỹ thuật dựng Excel bằng openpyxl

Kinh nghiệm đã kiểm chứng; mở khi dựng thật.

## Công thức

- Chỉ dùng hàm cổ điển (`IFERROR`, `COUNTIFS`, `SUMIFS`...). Tránh `IFS`, `XLOOKUP`, `TEXTJOIN`, `MAXIFS`: openpyxl không
  tự thêm tiền tố `_xlfn`, Excel hiện `#NAME?`. Quét toàn bộ công thức bằng regex để liệt kê tên hàm.
- Không dùng công thức mảng. Lấy phần tử thứ k trong kỳ bằng khóa phụ ẩn (giá trị + `ROW()/1e7`) với `SMALL`/`COUNTIF`/`MATCH`;
  xếp hạng bằng `SUMPRODUCT(SUMIFS(...))` kèm tie-break.
- Lọc theo tháng: thêm cột phụ khóa tháng rồi `COUNTIFS`/`SUMIFS`, tránh so sánh ngày trực tiếp với ô chữ. Chuỗi `TEXT(ngày,"MM/YYYY")`
  phụ thuộc ngôn ngữ Excel; máy dùng dấu chấm nghìn, dấu phẩy thập phân có thể ra khác. Với số, dùng `FIXED(số, n)` thay
  `TEXT(...,"#,##0")`. Định dạng số của ô (`number_format`) không bị ảnh hưởng.
- Tên sheet có khoảng trắng phải bọc nháy đơn: `'DANH MỤC VỤ VIỆC'!$B:$B`.
- Tránh `OR()` hoặc `INDEX` trên ô rỗng (`#VALUE!`): dùng `IF` lồng.
- Chuỗi ghi chú bắt đầu bằng dấu "=" bị hiểu thành công thức (`#NAME?`). Viết "Tính: ..." thay vì "= ...".
- Công thức nhiều sheet dễ sai tên sheet hoặc cột mà đọc mã không thấy; file tạo bằng openpyxl không có giá trị tính sẵn. Tính lại bằng
  `recalc.py` (nếu có) hoặc `soffice --convert-to xlsx` rồi đọc lại bằng `openpyxl` với `data_only=True`; yêu cầu 0 lỗi.

## Nhập liệu và định dạng

- Dropdown: `DataValidation(type="list", formula1='"A,B"')`, `ws.add_data_validation(dv)`, `dv.add("B2:B200")`. Giới hạn: lời nhắc và
  thông báo lỗi tối đa 255 ký tự, tiêu đề 32, `formula1` 255; công thức dưới 8000 ký tự.
- Dropdown phụ thuộc: `OFFSET`/`MATCH`. Giờ gõ `hh:mm`, tự sang ngày khi giờ đến nhỏ hơn giờ đi; ô Ngày/Mã để trống lấy dòng trên bằng cột phụ ẩn.
- Tô màu trạng thái: `CellIsRule` (một luật cho mỗi giá trị) hoặc `FormulaRule` khi điều kiện phụ thuộc ô khác (như ô ngưỡng).
- Mã màu đã dùng: nhập `FFF2CC`; đỏ `F8CBAD`, vàng `FFE699`, xanh `C6E0B4`; dữ liệu mẫu `DDEBF7`.
- Chiều cao dòng KHÔNG tự co theo `wrap_text` khi tạo bằng openpyxl (chữ bị cắt đáy ô, chỉ thấy khi render). Đặt thủ công:
  `height = max(30, ceil(số_ký_tự / ký_tự_mỗi_dòng) * 15 + 10)`.
- Ô gộp: vùng gộp để căn giữa dòng quốc hiệu quá hẹp thì chữ bị cắt hai đầu; ngưỡng đã kiểm chứng: tổng độ rộng cột ≥ 54 cho quốc hiệu,
  ≥ 42 cho tên công ty. `fitToWidth` và `print_area` chỉ co cả trang khi in, không sửa lỗi này.
- Lỗi mở file "found a problem with some content" thường do ô gộp chồng hoặc trùng; kiểm tra trước khi giao.
- In ấn: khổ ngang, `fitToWidth`, cố định dòng tiêu đề; đặt `print_area` cho sheet có hàng trăm dòng trống để khỏi in hàng chục trang.
- Khóa sheet không mật khẩu: ô công thức khóa, ô nhập mở, cho phép lọc và sắp xếp.
- Biểu đồ openpyxl: một trục, màu theo skill vẽ biểu đồ, neo kỹ để không chồng nhau, xem lại bằng ảnh render.

## Chèn thêm vào file đã có

- Thêm khối mới xuống cuối sheet; `insert_rows` đẩy lệch dòng mà công thức sheet khác vẫn trỏ địa chỉ cũ.
- Sửa file người dùng: lưu bản mới tên mới, không ghi đè bản gốc.

## Kiểm tra trước khi giao

1. Công thức tính lại, 0 lỗi; số liệu Word và Excel khớp.
2. Render ra PDF hoặc ảnh (`soffice --convert-to pdf`, `pdftoppm`), xem bảng nhiều cột nhất và bảng có tổng.
3. Nhập thử vượt giới hạn bảng báo cáo: phải có dòng cảnh báo rõ ("chỉ hiển thị N, xem số đủ ở sheet tổng hợp"), không lỗi công thức.
4. Ô ngưỡng để trống thì công thức vẫn chạy, không gắn cờ.
5. Nói rõ phần chưa thử với Excel thật.
