# Chuẩn hóa biểu mẫu và tài liệu nội bộ hàng loạt

Dùng khi người dùng nhờ "chuẩn hóa luôn các biểu mẫu" trong một thư mục có nhiều file cũ (`.doc`, `.docx`, `.xlsx`). Chi tiết kỹ thuật Word: `word-technical-notes.md`.

## Trước khi sửa

1. **Không đụng vào file ngoại lai.** Xem dòng "Kính gửi", đầu trang và chữ ký: nếu văn bản do đơn vị khác phát hành gửi đến, giữ nguyên hiện trạng, không chuẩn hóa thể thức,
   chỉ ghi chú đã xác định là file ngoại lai. Kiểm tra lại mỗi lần đưa một file vào diện "cần chuẩn hóa".
2. **Soi từng file bằng ảnh** (render rồi xem từng trang) trước khi chọn cách xử lý; tóm tắt văn bản hay đếm từ không đủ.
3. Chia hai nhóm:
   - **Nhóm A, chỉnh nhẹ:** file đã có khung bảng và kết cấu tốt; chỉ ép phông, sửa lỗi chính tả hoặc đặt tên nhỏ. Một script nhẹ dùng chung cho cả nhóm, nhanh và an toàn hơn dựng lại.
   - **Nhóm B, dựng lại:** file dùng đường chấm thủ công thay bảng, thiếu quốc hiệu, hoặc còn dữ liệu giao dịch thật cần xóa để thành mẫu trắng. Giữ phần cố định của mẫu
     (như tên vật tư mặc định của một phiếu chuyên dụng), chỉ xóa số văn bản, ngày và số liệu của vụ việc cũ.

## Khi gặp tình huống đặc biệt

- Một file `.doc` cũ có thể gộp HAI biểu mẫu khác nhau (chỉ thấy khi xem từng trang): tách thành hai file theo chức năng.
- Hai file ở hai nơi cùng phục vụ một chức năng: hợp nhất về bản đã chuẩn hóa, không dựng thêm một bản chuẩn thứ hai; LUÔN báo người dùng đã hợp nhất thế nào, không tự quyết âm thầm.
- **Mỗi loại biểu mẫu chỉ cần một mẫu trắng và một ví dụ đã điền**, không nhân bản theo từng thư mục quy trình con. Chỉ thêm bản riêng khi nó mang số liệu thật của một vụ việc khác ví dụ đã có.
- Phát hiện số hiệu văn bản căn cứ sai ở nhiều file: dùng script tìm và thay (chuẩn hóa NFC) cả chú thích dưới quốc hiệu lẫn chân trang, rồi quét lại cả thư mục xác nhận không còn
  chuỗi cũ, kể cả file `.doc` cũ.

## Khung viền và thẩm mỹ: hai tiêu chí riêng

- **Có khung viền hay không phụ thuộc mẫu chính thức của từng loại giấy tờ**, không mặc định một kiểu cho tất cả. Công văn và tờ trình theo thể thức văn bản hành chính dùng bố cục không kẻ khung
  (xem `vn-admin-documents`); chứng từ kế toán theo mẫu số hiệu thường có bảng trường dữ liệu và bảng ký duyệt có viền. Trước khi quyết định, tra mẫu số hiệu và văn bản hiện hành, kiểm tra văn bản đó
  còn hiệu lực hay đã bị thay thế; không dựa vào trí nhớ về số hiệu. Mẫu chứng từ do doanh nghiệp tự thiết kế được thì khung viền là để thống nhất và dễ đọc, không phải bắt buộc cứng.
- **Đúng thể thức chưa chắc đẹp và chuyên nghiệp.** Tự soi cả hai: tiêu đề cùng một kiểu (màu, gạch chân mảnh) trong cả đợt; mọi khối ký của biểu mẫu nội bộ có khung bảng, không chữ nổi
  lơ lửng; không tự chế thêm kiểu khung hay màu viền khác tông khi đã có kiểu dùng chung. Làm đúng ngay từ đầu thay vì đợi người dùng phản hồi rồi đồng bộ lại.
- Biên bản ghi nhận sự việc tại hiện trường mang tính nội bộ có thể lược số văn bản và mục "Nơi nhận" cho gọn, nhưng phải báo người dùng đây là lựa chọn đã lược, không coi như đã đủ thể thức.

## Lưu file

Bản dự thảo đặt tên mới hoặc thư mục riêng; không ghi đè file gốc của người dùng. File do chính agent soạn trước đó có thể ghi đè khi sửa tiếp, nếu chắc chưa bị sửa tay.
Bản cũ chuyển vào thư mục lưu trữ bằng lệnh không ghi đè (`mv -n`) và kiểm tra lại kết quả; không xóa khi chưa được yêu cầu.
