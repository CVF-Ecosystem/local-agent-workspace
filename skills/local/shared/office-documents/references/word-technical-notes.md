# Ghi chú kỹ thuật khi dựng hoặc sửa file Word

Kinh nghiệm đã kiểm chứng với `.docx`; mở khi dựng hoặc sửa file thật. Không thay hướng dẫn của công cụ định dạng bạn đang dùng.

## Sửa file có sẵn hay dựng mới

- File người dùng đã có (đề án, quy trình, biểu mẫu) thì **sửa trực tiếp** để giữ hình, bảng, đầu trang, chân trang; chỉ dựng lại khi kết cấu cũ hỏng.
- Với `python-docx`: giữ tham chiếu tới phần tử cần sửa ngay từ đầu, nhân bản (`copy.deepcopy`) một đoạn hoặc hàng mẫu CÙNG kiểu rồi chèn bằng
  `addnext`; thay chữ ở mức `w:t` để giữ định dạng. Bảng mẫu phải cùng số cột; thêm hàng bằng nhân bản hàng cuối.
- Mỗi bước quy trình thường là một đoạn `ListParagraph` có MỘT run dạng "Bước n — …:". Thêm bước thì nhân bản đúng loại đoạn này rồi đánh lại số bước.
  Không đánh số lại các mục có nhiều tham chiếu chéo: chèn thành tiểu mục mới hoặc phụ lục.
- Sửa xong vẫn render và xem từng trang mới thêm, cập nhật số trang trong bảng mã tài liệu, gạch bỏ tham chiếu chéo sai, kiểm lại thứ tự số hàng bảng.

## Chữ tiếng Việt

- Tìm và thay chữ: file chuyển từ `.doc` cũ qua LibreOffice có thể lưu dấu ở dạng Unicode NFD trong khi chuỗi gõ là NFC; so khớp luôn `False` và việc thay
  lặng lẽ không xảy ra. Chuẩn hóa cả hai chuỗi bằng `unicodedata.normalize("NFC", ...)` trước khi so.
- Ép phông (như Times New Roman) qua cả `run.font.name` VÀ XML `w:rFonts` (`ascii`, `hAnsi`, `eastAsia`, `cs`), cộng style Normal của cả file.
- Xuống dòng trong ô bảng: ký tự `"\n"` trong chuỗi truyền cho `python-docx` hiển thị đúng thành dòng mới trong Word (hợp cho dòng phụ ngắn dưới nhãn chức danh).

## Bố cục

- Căn "Nhãn: Giá trị" bằng bảng hai cột (cột nhãn khoảng 5,2 cm, in đậm), không canh bằng khoảng trắng hay tab.
- Khối quốc hiệu và tên cơ quan là bảng hai cột không viền: cột trái rộng khoảng 6,5 cm, cột phải khoảng 11 cm, lề trái và phải khoảng 2 cm và 1,5 cm (đã kiểm
  chứng vừa một dòng cho quốc hiệu cỡ 12 đậm). Hai dòng trong một ô nên là hai đoạn riêng. Tên cơ quan ban hành chiếm hai dòng của nó; tên phòng ban đặt ở tham số riêng,
  không nhét vào dòng thứ hai của tên công ty.
- Tiêu đề mục: `keep_with_next = True` để không mồ côi cuối trang, đặc biệt khi đứng ngay trước ảnh sơ đồ lớn.
- Bảng dài: lặp dòng tiêu đề khi tràn trang (`w:tblHeader`), không cho dòng bị cắt giữa hai trang (`w:cantSplit`).
- Cột đúng độ rộng: đặt `w:tblLayout` thành `fixed` và sửa `w:gridCol`; chỉ đặt `cell.width` thì LibreOffice chia đều cột. Cột STT tối thiểu khoảng 1,3 cm.
- Số trang trong bảng mã tài liệu không đoán trước: đặt giá trị tạm, build, render PDF đếm số trang thật, sửa rồi build lại. Tài liệu không được tự mâu thuẫn với chính file.

## Ảnh

- Ảnh nhúng sẵn trong file gốc: `unzip file.docx "word/media/*"`, rồi XEM TỪNG ẢNH (không suy theo tên file hay thứ tự trong zip) để ghép đúng mục; tái dùng ảnh, không vẽ lại sơ đồ.
- Dựng mới: dùng chức năng chèn ảnh của thư viện (ví dụ `ImageRun` của `docx`, `add_picture` của `python-docx`), căn giữa, caption nghiêng.
- Chèn ảnh vào `.docx` đã có bằng sửa XML (giải nén, sửa `word/document.xml`, nén lại) có ba điểm dễ sai: (1) thêm `<Default Extension="jpg" ContentType="image/jpeg"/>`
  vào `[Content_Types].xml` nếu chưa có; (2) thêm quan hệ ảnh vào `word/_rels/document.xml.rels`; (3) trong `<w:pPr>`, `<w:spacing>` phải đứng TRƯỚC `<w:jc>`, sai thì
  kiểm tra schema báo lỗi.

## Đọc và kiểm tra

- Trích nội dung gốc ra Markdown (ví dụ `markitdown`) và đọc kỹ toàn bộ trước khi viết script dựng lại; không có công cụ thì đọc `word/document.xml` bằng `zipfile` và regex bỏ thẻ.
- Render ra ảnh (`soffice --convert-to pdf` rồi `pdftoppm`) và xem TỪNG trang, không chỉ trang đầu: quốc hiệu có thẳng cột không, bảng có tràn trang không, khối ký có bị tách lẻ
  loi không, tiêu đề có mồ côi không, ảnh có bị co quá nhỏ không, số trang khớp chưa.
- Phông thay thế trong môi trường kiểm tra (không có Times New Roman thật) có thể vẽ chữ "Đ" đậm đứng đầu từ trông như bị gạch ngang. Đọc XML của run đó: nếu không có
  `w:strike` thì chỉ là lỗi hiển thị của phông thay thế; không đổi chữ, bỏ đậm hay đổi phông để "sửa".
