# Mẫu ghi nhận truy cập nguồn

Mẫu thiết kế, không phải quyền truy cập hay bằng chứng đã xác minh. Ghi “chưa biết” khi thiếu; không ghi mật khẩu, khóa hoặc payload nhạy cảm.

- Cơ quan/nguồn gốc và URL trang:
- Endpoint, phương thức, payload gửi và dữ liệu nhận:
- Cơ chế truy cập và quyền/điều khoản, phạm vi sử dụng, automation và phân phối:
- Capability và giới hạn kỹ thuật, tốc độ, byte, redirect và host:
- TLS và cơ chế xác thực được phép:
- Evidence, URL file/cuối, revision/hash, ngày kiểm và kết quả thực tế hoặc lý do từ chối:
- Mục chưa kiểm hoặc cần xác nhận:

Nguồn chính thống, quyền dùng và nội dung/hiệu lực đã xác minh là các điều riêng. Xét POST theo tác động, endpoint, payload và quyền cụ thể; không mặc định cho phép hay cấm mọi POST. Không vượt kiểm soát truy cập. Mẫu không tạo endpoint hay adapter.
