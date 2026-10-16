# assets/fonts/

Đặt file font riêng của đơn vị vào thư mục này khi có văn bản phải dùng đúng font đó; trợ lý AI sẽ dùng các font này khi bạn yêu cầu (ví dụ "dùng font X cho văn bản này") hoặc khi `PROJECT.md` ghi font chuẩn của đơn vị.

## Cách dùng

1. Chép file font (`.ttf`, `.otf`, `.woff2`) vào thư mục này. Nếu có bản chữ đậm hoặc chữ nghiêng, chép cả các file đó.
2. Khi giao việc, ghi tên font trong yêu cầu. Hoặc ghi font chuẩn vào dòng về kiểu trình bày trong `PROJECT.md`.
3. Mở văn bản kết quả và kiểm tra font đã đúng chưa.

## Font áp dụng được đến đâu

| Loại file | Cách font được xử lý |
|---|---|
| HTML | Font được nhúng trong file. Mở trên máy nào cũng hiển thị đúng. |
| PDF | Font được nhúng trong file. Mở trên máy nào cũng hiển thị đúng. |
| Word, Excel | File chỉ lưu tên font. Máy người nhận phải cài sẵn font đó, nếu không sẽ thấy font thay thế. |

## Bản quyền font

Chỉ đưa vào thư mục này font mà đơn vị được phép dùng và được phép phân phát. Nhúng font vào file HTML hoặc PDF rồi gửi ra ngoài cũng là phân phát font đó. Nếu không chắc, hỏi bộ phận IT hoặc bộ phận quản trị của đơn vị.

*Thư mục này thuộc về người dùng: nâng cấp bộ công cụ không ghi đè file ở đây. Dự án mới tạo từ bộ mẫu (nút "Tạo dự án mới") mang theo các file font ở đây.*
