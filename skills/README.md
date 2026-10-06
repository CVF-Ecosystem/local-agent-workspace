# skills/

Thư viện hướng dẫn và tài nguyên bổ sung do người dùng quản lý.

## Chọn theo công việc

Native, local, external hay làm trực tiếp đều có thể là lựa chọn tốt. Cân nhắc
độ phù hợp với nguồn, đầu ra, ngôn ngữ và công cụ thực có; không cần ưu tiên một
nhóm chỉ vì nơi cung cấp. Tra `.agent/SKILL_INDEX.md` (tính từ project root) khi cần
khám phá; nếu đã biết skill hữu ích, có thể mở thẳng hướng dẫn của nó.

Một skill không phải toàn bộ quy trình phải chạy. Ví dụ, sửa một câu thường không
cần đọc skill soạn tài liệu; tạo file Word có thể kết hợp hướng dẫn nghiệp vụ với
công cụ định dạng sẵn có. Không cần đọc toàn bộ thư viện hay tất cả ví dụ.

## Các vùng

- `local/shared/`: hướng dẫn dùng lại cho nhiều dự án; mười một skill biên soạn mới.
- `local/project/`: hướng dẫn riêng của dự án khi thật sự cần.
- `external/`: skill nhập từ nguồn ngoài, giữ nguồn gốc và điều khoản đi kèm.
- `inbox/`: nơi tạm tùy chọn, không phải bước duyệt bắt buộc.
- `local/packs/`: gói lĩnh vực cài bằng `tools/pack.py` (xem `packs/README.md`).

Khi thêm hoặc sửa lớn, cập nhật index với mục đích và dependency đáng chú ý.
Không lặp lại việc này khi chỉ dùng lại skill. Người dùng giữ quyền quản lý thư
viện; agent chủ động chọn cách dùng phù hợp trong phạm vi được giao.

Thư viện này được đọc như file project, không tự đăng ký native với ứng dụng nào.
Không cần sao chép native skill vào đây chỉ để đủ bộ. Chi tiết dành cho người dùng:
`docs/HUONG_DAN_SKILLS_VI.md` (tính từ project root).
