# Đánh giá và sửa đề án, quy chế nội bộ có sẵn

Dùng khi người dùng đưa một đề án hoặc quy chế (`.docx`) và nhờ đánh giá, trình lãnh đạo lý do sửa, rồi trình bày lại. Đối chiếu hai phiên bản: `document-comparison`.

## Quy trình

1. **Đối chiếu với nguồn gốc trước khi chấm.** Đọc toàn bộ đề án, rồi đọc các quy trình của những đơn vị nó nhắc đến để kiểm tra từng nhận định về hiện trạng. Chấm theo ba lớp:
   chẩn đoán có đúng không; thiết kế có tự thỏa nguyên tắc của chính nó không (như đòi khóa dòng, nhật ký, phân quyền nhưng chọn công cụ không làm được); phần quản trị dự án
   (mục tiêu đo được, chi phí, rủi ro, người chủ trì, lịch có khả thi).
2. **Hỏi người dùng điều chỉ họ biết** (cách tính, mốc thời gian) bằng câu hỏi ngắn có lựa chọn, thay vì đoán rồi dựng thiết kế trên giả định. Khi người dùng đính chính sau đó, sửa đúng phần bị
   ảnh hưởng, bỏ các điều kiện và cảnh báo đã thêm dựa trên giả định sai, và cập nhật đồng bộ mọi file liên quan (đề án, bảng đánh giá, phụ lục).
3. **Bảng đánh giá trình lãnh đạo**: Word A4 nằm ngang, một đến hai trang; đầu trang và tiêu đề; một đoạn kết luận chung; bảng sáu cột (STT, Nội dung, Hiện trạng trong bản cũ, Nếu không sửa
   hậu quả là, Đề xuất kèm mục tương ứng trong bản mới, Ưu tiên; ô ưu tiên tô nhạt theo mức); đoạn "Đề nghị" liệt kê việc cần quyết định; dòng tài liệu kèm theo. Đánh số STT bằng code để thêm bớt dòng không lệch số.
4. **Sửa trực tiếp file gốc** để giữ hình, bảng, đầu trang, chân trang (kỹ thuật: `word-technical-notes.md`). Mục có nhiều tham chiếu chéo thì không đánh số lại: chèn nội dung mới thành tiểu mục hoặc phụ lục.
   Sau khi sửa: render, xem từng trang mới thêm, đếm trang, gạch bỏ tham chiếu chéo sai.
5. **Không bịa số.** Mọi ngưỡng, tỷ lệ, mốc do agent đề xuất ghi rõ "đề xuất, người có thẩm quyền quyết định"; chỉ tiêu chưa đo ghi "chưa thống kê, đo trong giai đoạn thí điểm đầu"; chi phí chưa có thì nói
   chưa ước tính được và lý do; số liệu lấy từ hồ sơ chưa xác minh ghi "theo hồ sơ hiện có, chưa xác minh".
6. **Phụ lục Excel đi kèm** là mẫu dữ liệu, không chỉ mô tả bằng chữ: dòng mẫu tô xám ghi "DÒNG MẪU"; sheet chỉ minh họa ghi rõ "DỮ LIỆU MẪU" ở dòng mô tả đầu sheet và trong danh sách sheet của đề án
   (xem `excel-workbooks`). Kiểm tra bằng cách tính lại bằng LibreOffice rồi đọc lại, bảo đảm không có lỗi `#`.
7. **Căn cứ pháp lý** (luật, thông tư kế toán...): tra cứu để xác nhận điều khoản và văn bản còn hiệu lực rồi mới trích; ghi ngắn trong đề án là "căn cứ cần rà soát khi ban hành quy chế",
   không viết như kết luận pháp lý. Không dùng văn bản đã bị thay thế làm căn cứ cho tài liệu mới.
8. Lưu ghi chú ngắn (đã làm gì, đề xuất còn để mở, điều chưa đối chiếu) vào `.agent/STATE.md` hoặc ghi chú của project; cập nhật khi có thay đổi, tránh để ghi chú cũ nói "chưa ghi file" khi file đã xong.
