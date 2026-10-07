# Checklist trước khi giao

Dùng ngắn gọn, chọn phần phù hợp với sản phẩm. Không biến thành thủ tục cho việc nhỏ. Công cụ hỗ trợ phần cơ học:
`python tools/check_output.py <file>` (tìm chỗ chưa điền, nhãn mẫu minh họa, tài nguyên mạng trong HTML; chuyển CSV/Excel cho `spreadsheet-check`).

## Mọi sản phẩm

- [ ] Đúng yêu cầu: loại sản phẩm, người đọc, phạm vi, định dạng.
- [ ] Không còn chỗ chưa điền (`[Tên]`, `[...]`) và không còn nhãn "mẫu/minh họa/dữ liệu giả".
- [ ] Chỗ thiếu căn cứ đã ghi "cần xác nhận"; không có số liệu, ngày, tên, thời hạn bịa.
- [ ] Dữ kiện lấy từ nguồn tách khỏi đề xuất của agent.
- [ ] File gốc của người dùng không bị ghi đè; bản mới có tên rõ (và hậu tố phiên bản khi thay bản cũ). Thư mục kết quả chỉ chứa bản đang dùng; bản cũ chuyển vào thư mục lưu trữ bằng lệnh không ghi đè (`mv -n`) và kiểm tra lại; không xóa khi chưa được yêu cầu.
- [ ] Nêu trong lời giao: đã làm gì, chưa kiểm gì, cần người dùng xác nhận gì.
- [ ] Việc có phát hiện hoặc số liệu: kết thúc bằng khối "Khai báo thực hiện" (cách làm, skill, nguồn, file, chưa kiểm); phát hiện về số nêu con số cụ thể (xem `AGENTS.md`).
- [ ] Yêu cầu "giữ nguyên nội dung": đã đếm ảnh, bảng, ký tự, bước của file gốc và file mới, và nêu bảng "trước → sau" (xem `SKILL.md`, mục "Giữ nguyên nội dung").

## Văn bản, quy trình, biểu mẫu

- [ ] Thuật ngữ, tên đơn vị, chức danh nhất quán và đúng với nguồn.
- [ ] Số bước, số mục, tham chiếu chéo (ví dụ "xem mục 3") còn đúng sau khi sửa.
- [ ] Vai trò, thời hạn, điều kiện đều có trong nguồn hoặc được đánh dấu "cần xác nhận".
- [ ] Biểu mẫu: trường bắt buộc, đơn vị, định dạng ngày, hướng dẫn điền rõ ràng.

## Văn bản hành chính, gửi ra ngoài, trình ký

- [ ] Áp dụng "Mức thận trọng cao" trong `AGENTS.md`: đối chiếu từng số, ngày, tên, tên cơ quan, số và ngày văn bản căn cứ với nguồn.
- [ ] Thể thức đúng quy chế đơn vị hoặc quy định áp dụng (xem `vn-admin-documents`); số, ngày, chữ ký, thẩm quyền ký để người có thẩm quyền điền.
- [ ] Nhận định pháp lý chỉ là gợi ý để người có thẩm quyền xác nhận.
- [ ] Người ký đã được nhắc đọc lại toàn bộ.

## Báo cáo số liệu, bảng tính

- [ ] Đã chạy `spreadsheet-check` trên dữ liệu gốc; các phát hiện ảnh hưởng số liệu đã xử lý hoặc nêu rõ.
- [ ] Tính lại tổng và kiểm cả phần chi tiết (từng nhóm, từng dòng), không chỉ con số tổng.
- [ ] Đơn vị, kỳ báo cáo, nguồn dữ liệu ghi rõ; thiếu dữ liệu hiện "—" hoặc "chưa có", không điền 0 theo suy đoán.
- [ ] Số liệu trong lời giải thích khớp với bảng và biểu đồ.

## Báo cáo/dashboard HTML

- [ ] Mở thử offline (không cần mạng); `check_output.py` không báo tài nguyên mạng.
- [ ] `isDemo` đã đặt đúng; tiêu đề, kỳ, nguồn, nhận xét đã thay bằng nội dung thật.
- [ ] Biểu đồ: trục bắt đầu từ 0 với cột, nhãn và đơn vị đủ, bảng số liệu đi kèm khớp.
- [ ] Thử với dữ liệu xấu (trống, thiếu, tên cột gõ không chuẩn): công cụ báo rõ lỗi gì ở đâu.
