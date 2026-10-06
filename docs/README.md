# docs/

Hướng dẫn dành cho người dùng, đọc theo nhu cầu. Mở `START_HERE.html` ở project root
để xem trọn bộ cẩm nang; bốn hướng dẫn đều có bản `.html` cùng tên bên cạnh Markdown. Bản tiếng Anh của toàn bộ
cẩm nang nằm trong `en/` (mở `START_HERE.en.html`); mỗi trang có nút chuyển ngôn ngữ.

- `HUONG_DAN_SU_DUNG_VI.md`: dùng hằng ngày.
- `HUONG_DAN_TAO_PROJECT_MOI_VI.md`: tạo project mới, kèm đoạn hướng dẫn dán vào Project/cloud.
- `HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`: project có sẵn và nâng cấp package.
- `HUONG_DAN_SKILLS_VI.md`: lựa chọn skill và sử dụng mẫu.
- `NGUON_THAM_KHAO_VI.md`: nguồn ý tưởng, audit repo tham chiếu và phần không nhập.
- `en/`: bản tiếng Anh của năm tài liệu trên (`NEW_PROJECT_GUIDE`, `DAILY_USE_GUIDE`,
  `EXISTING_PROJECT_UPGRADE_GUIDE`, `SKILLS_GUIDE`, `SOURCES_AND_REFERENCES`), mỗi tài liệu có `.md` và `.html`
  (riêng nguồn tham khảo chỉ có `.md`).

Markdown là nội dung hướng dẫn dễ chỉnh; HTML là bản trình bày dựng từ Markdown bằng
`tools/build_guides_html.py`. Chỉ cập nhật HTML khi chủ động sửa bộ hướng dẫn, không trong
mỗi tác vụ. Agent không cần đọc cả hai dạng hoặc toàn bộ thư mục để làm việc văn phòng.
