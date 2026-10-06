# Quản lý feedback (dành cho người duy trì package)

Thư mục này **không nằm trong gói phát hành**: không có trong `MANIFEST.sha256`, không vào file ZIP và không được
chép vào project của người dùng. Nó chỉ nằm trong kho git để người duy trì theo dõi các lần thử, lỗi và đề xuất.

## Dùng để làm gì

Mỗi lần có người (hoặc một agent) thử package, ghi lại một **bản ghi** ngắn: đã thử gì, agent nào, kết quả ra sao,
phát hiện vấn đề gì, và vấn đề đó được xử lý ở phiên bản nào. Nhờ vậy, mọi chỉnh sửa skill hoặc quy tắc đều có căn cứ
thực tế thay vì cảm tính.

## Cách ghi một lần thử

1. Chép `TEMPLATE.md` thành `records/AAAA-MM-DD_<agent>_<chủ-đề>.md` (ví dụ `2026-10-06_gemini_demo-project.md`).
2. Điền phần thông tin, dán **nguyên văn** yêu cầu và câu trả lời của agent. Không tóm tắt thay cho nguyên văn.
3. Dán khối "Khai báo thực hiện" của agent (quy tắc 9 trong `AGENTS.md`). Agent không có khối này thì ghi
   "không có": đó là một phát hiện, không phải thiếu sót của người thử.
4. Chạy `python tools/check_output.py --declaration <file chứa câu trả lời>` để kiểm khai báo đủ mục hay chưa.
5. Ghi các vấn đề vào bảng của bản ghi, rồi thêm một dòng vào `INDEX.md`.

## Vòng đời của một vấn đề

`Mới` → `Đã xử lý (vX.Y.Z)` hoặc `Hoãn` hoặc `Không làm (kèm lý do)`. Khi sửa skill, quy tắc hay hướng dẫn vì một vấn đề,
ghi mã vấn đề (ví dụ `2026-10-06-G1`) vào `CHANGELOG.md` của gói.

## Quy tắc

- Không dán dữ liệu thật, thông tin cá nhân hoặc tài liệu mật vào bản ghi; che hoặc mô tả thay thế.
- Một bản ghi nên ghi rõ **phiên bản gói** (xem `VERSION`) đã được thử, vì kết quả chỉ có giá trị với phiên bản đó.
- Cần đánh giá khách quan: mỗi tiêu chí "Bạn nên thấy" trong bài thử được chấm đạt/chưa đạt riêng, kèm bằng chứng.
- Nguồn feedback từ người dùng thật (khi gói được đưa ra sử dụng): chép vào cùng mẫu, đánh dấu người thử là "người dùng".
