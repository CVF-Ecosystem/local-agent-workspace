# .agent/

Ngữ cảnh làm việc gọn cho project.

- `STATE.md`: trạng thái hiện tại, không phải nhật ký.
- `HANDOFF.md`: việc cần bàn giao; để `None` khi không dùng.
- `INDEX.md`: tìm nguồn khi cần.
- `SKILL_INDEX.md`: gợi ý skill phù hợp, không phải thứ tự gọi cố định.
- `PENDING_LESSONS.md`: nơi tùy chọn để ghi bài học có khả năng dùng lại.
- `PACKAGE_INFO.json`: phiên bản package, ngôn ngữ và ngày khởi tạo (do `tools/init_project.py` tạo; đừng sửa tay).

Chỉ checkpoint khi có thay đổi mà phiên sau cần biết. Không lưu credentials hoặc
thông tin nhạy cảm không cần thiết. Việc độc lập đủ ngữ cảnh có thể làm trực tiếp,
không phải đọc/ghi thư mục này sau mọi yêu cầu.
