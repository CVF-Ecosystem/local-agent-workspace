# skills/local/

Skill do user hoặc agent trong hệ thống này xây dựng/duy trì.

- `shared/`: có thể tái sử dụng ở nhiều project.
- `project/`: chỉ đúng cho project hiện tại.

## Chọn chỗ đặt khi thêm hoặc cập nhật skill

- **Dùng chung (`shared/`)**: không phụ thuộc đơn vị hay nghiệp vụ cụ thể: kỹ thuật, lỗi đã gặp, quy trình kiểm thử, quy ước file, bố cục mẫu.
- **Riêng project (`project/`)**: gắn với một đơn vị, người, hệ thống hay quy chế cụ thể: tên, chức danh, căn cứ nội bộ, mốc thời gian, mã, bố cục sổ riêng, thông tin nền công ty.
- Còn lưỡng lự thì để ở project; khi cùng một bài học lặp lại ở project thứ hai thì nâng phần chung lên `shared/`.
- Skill project nên trỏ tới skill chung thay vì chép lại nội dung (ví dụ trỏ tới `excel-workbooks` hay `office-documents`) và chỉ giữ phần riêng. Tránh hai bản của cùng một hướng dẫn.
- Skill riêng gắn với một vụ việc, một cá nhân hoặc dữ liệu bảo mật thì không đưa lên `shared/`; bài học lấy từ project thực chỉ đưa lên sau khi bỏ tên, số liệu và chức danh riêng. Một lĩnh vực mới chỉ thành gói khi đủ điều kiện trong `packs/README.md`.
- Trước khi tạo hoặc sửa skill: xem `.agent/SKILL_INDEX.md` và đọc kỹ skill liên quan (cả phần tham khảo) để dùng lại, không làm lại từ đầu; chỉ mượn kỹ thuật, không mượn nội dung đặc thù của đơn vị khác.
- Cuối mỗi lần cập nhật nêu một dòng: bài học là chung hay riêng, đã đưa vào đâu. Chưa chắc chắn thì ghi vào `.agent/PENDING_LESSONS.md`.

Khi một skill đổi phạm vi, cập nhật `.agent/SKILL_INDEX.md`. Không di chuyển skill chỉ vì agent suy đoán; nếu việc di chuyển ảnh hưởng cấu trúc user đang dùng, hỏi/xác nhận user.
