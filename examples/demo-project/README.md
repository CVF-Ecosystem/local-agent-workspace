# Bài thực hành: thử trong 10 phút

Bài thực hành này dùng **dữ liệu minh họa**, không phải hồ sơ thật; bạn không cần chuẩn bị tài liệu riêng. Thử trong **một dự án thử**,
không thử trong bộ mẫu: ở bảng điều khiển của bộ mẫu, trang "Tạo dự án mới", tạo dự án tên "Thử demo"; mở thư mục dự án
đó (không phải riêng thư mục `examples/`) bằng ứng dụng AI bạn dùng (Claude, Codex, Gemini...), rồi gửi từng yêu cầu dưới đây.
Mỗi yêu cầu chỉ nêu nguồn và kết quả cần nhận; không cần nêu tên kỹ năng, trợ lý AI tự chọn khả năng sẵn có của ứng dụng hoặc phần
bổ sung của bộ công cụ khi cần.

| File | Nội dung (minh họa) |
|---|---|
| `data/weekly_log.csv` | Nhật ký tiếp nhận và hoàn tất hồ sơ theo ngày, có vài lỗi cố ý |
| `notes/meeting_notes.txt` | Ghi chú họp chưa sắp xếp |
| `docs/procedure_v1.md`, `docs/procedure_v2.md` | Hai phiên bản của một quy trình ngắn |

## Thử 1: kiểm tra bảng số liệu

```text
Kiểm tra file examples/demo-project/data/weekly_log.csv trước khi tôi lấy số làm báo cáo. Chỉ báo phát hiện, không sửa file gốc.
```

Bạn nên thấy: ô chữ lẫn trong cột số, một dòng trùng, số dạng `1.234` mơ hồ, và dòng tổng không khớp. Mỗi phát hiện về tổng có con số cụ thể (giá trị ghi so với giá trị tính lại), và ô "1.234" được nêu cả hai cách hiểu (1234, hoặc một phẩy hai trăm ba mươi bốn) kèm tổng theo từng cách. Vị trí ghi theo số dòng trong file: "n/a" ở dòng 5, "1.234" ở dòng 6, hai dòng trùng là dòng 7 và 8, dòng Tổng là dòng 11.

## Thử 2: lập biên bản họp

```text
Từ examples/demo-project/notes/meeting_notes.txt, lập biên bản họp: quyết định, việc cần làm (người phụ trách, hạn), vấn đề chưa chốt.
Chỗ nào thiếu thông tin thì ghi "cần xác nhận", đừng đoán. Lưu biên bản vào output/.
```

Bạn nên thấy: file biên bản trong `output/` (hiện ở ô "Kết quả" của bảng điều khiển); ba nhóm tách rõ; việc thiếu người hoặc hạn được đánh dấu "cần xác nhận", không bị tự đặt ra. Việc chỉ nói ai "đã báo" hoặc "đã làm" (ví dụ Hùng đã báo bên kỹ thuật) không bị biến thành việc giao cho người đó theo dõi; mốc như "từ tuần sau" được ghi nguyên văn.

## Thử 3: đối chiếu hai bản quy trình

```text
So sánh examples/demo-project/docs/procedure_v1.md và examples/demo-project/docs/procedure_v2.md, lập bảng thay đổi có ý nghĩa và nêu ảnh hưởng.
```

Bạn nên thấy: bảng chỉ liệt kê thay đổi thật (bước thêm, bước đổi người phụ trách, thời hạn khác), không liệt kê khác biệt chỉ về câu chữ (bước 1 của bản 2 chỉ diễn đạt lại, không nên có trong bảng). Cột ảnh hưởng mang nhãn "(suy luận)" (ở tiêu đề cột hoặc từng ý).

## Kiểm tra cách trợ lý AI làm việc

Cuối mỗi câu trả lời, trợ lý AI nên có khối **"Khai báo thực hiện"** (cách làm, kỹ năng, nguồn, file, chưa kiểm; xem `AGENTS.md`). Với bài 1,
bộ công cụ có sẵn script kiểm bảng tính: nếu trợ lý AI dùng nó, khai báo nên ghi lệnh đã chạy và dòng "Dấu vết" của script, hoặc nói rõ vì sao đọc thủ công.
Thiếu khối này là dấu hiệu trợ lý AI chưa làm theo hướng dẫn của bộ công cụ. Muốn kiểm nhanh, lưu câu trả lời thành file rồi chạy
`python tools/check_output.py --declaration <file>`.

## Sau khi thử

Nếu kết quả hợp lý, bạn đã hiểu cách dùng: giao việc bằng lời thường, nêu file nguồn và đầu ra mong muốn. Rồi tạo dự án thật
từ bộ mẫu (trang "Tạo dự án mới"); dự án thử có thể xóa khi không cần. Bộ mẫu không bị ảnh hưởng.
