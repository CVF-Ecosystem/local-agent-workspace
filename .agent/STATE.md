# PROJECT STATE

## Goal
Hoàn thiện Local Agent Workspace theo roadmap đã được người dùng yêu cầu triển khai.

## Current phase
Đã hoàn thành nhóm ưu tiên 1, 3 và 4; đang ở bước kiểm tra cuối, chưa phát hành phiên bản mới.

## Completed
- Lưu roadmap và tiến độ trong roadmap/ROADMAP_HOAN_THIEN.md.
- Bảo toàn hướng dẫn riêng VI/EN; chặn ghi đè bản chờ hợp nhất khi chuyển đổi/nâng cấp.
- Checker phân loại 0/1/2; mở rộng Word; báo thiếu thành phần; giao diện hiển thị tương ứng.
- Giữ ngữ cảnh điền một phần khi đổi ngôn ngữ; rút gọn README; đồng bộ hướng dẫn HTML VI/EN.
- 15 kiểm thử hành vi đạt; kiểm package 0 lỗi, 0 cảnh báo.
- Đã thử giao diện với file không hỗ trợ; không ghi nhận lỗi JavaScript trong lượt thử.
- ZIP tạm đã tạo, giải nén và xác minh; không giữ bản phát hành. Sửa lỗi output khác ổ đĩa Windows.
- Tách mẫu phát hành khỏi STATE phát triển; build dựng trong cây tạm, không sửa working tree.
- Thêm schema kết quả v1 và bỏ quyết định giao diện dựa trên dò câu chữ ở luồng chạy công cụ.
- Thêm trang Chờ hợp nhất, giới hạn file theo manifest/gói và lưu trạng thái bằng dấu vân tay.

## Current artifact
- roadmap/ROADMAP_HOAN_THIEN.md
- tests/test_workflows.py
- Thay đổi công cụ, bảng điều khiển, tài liệu và MANIFEST trong working tree; xem git diff.

## Open items
- Các công cụ ít dùng mới có envelope do backend chuẩn hóa, chưa phát chi tiết native; chưa có trình so sánh nội dung.
- Chưa thử macOS/Python 3.8, chưa nghiệm thu với người dùng mới, chưa kiểm toàn bộ giao diện.
- VERSION giữ nguyên; CHANGELOG ghi phần chưa phát hành.
- STATE hiện là tiến độ công việc: cần khôi phục mẫu trong bản nguồn sạch trước phát hành, không bỏ qua kiểm release.

## Waiting on user
- None

## Decisions
- Người dùng yêu cầu lưu roadmap và tiến hành fix; không khởi chạy agent phụ.
- Người dùng đồng ý đưa nhóm đề xuất nâng cấp mức độ chuyên nghiệp vào roadmap; ưu tiên đợt tiếp theo là Giai đoạn 7, 9 rồi 8.
- Người dùng yêu cầu xử lý trước mục 1, 3 và 4; ba mục đã được triển khai trong working tree.
- tests/ và roadmap/ chỉ dành cho kho nguồn, không đưa vào package người dùng.
- Chưa commit, đẩy lên remote hoặc phát hành.

## Next milestone
Triển khai phục hồi giao dịch giữa chừng (Giai đoạn 10) sau khi nghiệm thu ba hạng mục vừa hoàn thành.
