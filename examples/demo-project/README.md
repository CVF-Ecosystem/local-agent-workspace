# Project mẫu: thử trong 10 phút

Đây là project **giả** (dữ liệu bịa) để bạn thử package mà không cần chuẩn bị tài liệu thật. Mở thư mục `examples/demo-project/`
bằng ứng dụng AI bạn dùng (Claude, Codex, Gemini...), rồi gửi từng yêu cầu dưới đây. Mỗi yêu cầu dùng một skill khác nhau.

| File | Nội dung (giả) |
|---|---|
| `data/weekly_log.csv` | Nhật ký tiếp nhận và hoàn tất hồ sơ theo ngày, có vài lỗi cố ý |
| `notes/meeting_notes.txt` | Ghi chú họp chưa sắp xếp |
| `docs/procedure_v1.md`, `docs/procedure_v2.md` | Hai phiên bản của một quy trình ngắn |

## Thử 1: kiểm tra bảng số liệu (skill `spreadsheet-check`)

```text
Kiểm tra file data/weekly_log.csv trước khi tôi lấy số làm báo cáo. Chỉ báo phát hiện, không sửa file gốc.
```

Bạn nên thấy: ô chữ lẫn trong cột số, một dòng trùng, số dạng `1.234` mơ hồ, và dòng tổng không khớp.

## Thử 2: lập biên bản họp (skill `meeting-minutes`)

```text
Từ notes/meeting_notes.txt, lập biên bản họp: quyết định, việc cần làm (người phụ trách, hạn), vấn đề chưa chốt.
Chỗ nào thiếu thông tin thì ghi "cần xác nhận", đừng đoán.
```

Bạn nên thấy: ba nhóm tách rõ; việc thiếu người hoặc hạn được đánh dấu "cần xác nhận", không bị bịa.

## Thử 3: đối chiếu hai bản quy trình (skill `document-comparison`)

```text
So sánh docs/procedure_v1.md và docs/procedure_v2.md, lập bảng thay đổi có ý nghĩa và nêu ảnh hưởng.
```

Bạn nên thấy: bảng chỉ liệt kê thay đổi thật (bước thêm, bước đổi người phụ trách, thời hạn khác), không liệt kê khác biệt chỉ về câu chữ.

## Sau khi thử

Nếu kết quả hợp lý, bạn đã hiểu cách dùng: giao việc bằng lời thường, nêu file nguồn và đầu ra mong muốn. Rồi tạo project thật
bằng `SETUP.bat` / `SETUP.command` ở thư mục gốc package. Thư mục `examples/` có thể xóa nếu không cần.
