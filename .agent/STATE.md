# PROJECT STATE

## Goal
Hoàn thiện Local Agent Workspace theo roadmap/ROADMAP_HOAN_THIEN.md.

## Current phase
Đã triển khai Giai đoạn 9 (phần còn lại), 10, 11, 12 và phần kỹ thuật của 13 đã gộp vào main (PR #1); đang phát hành v1.7.0.

## Completed
- Giao dịch có nhật ký cho khởi tạo/chuyển đổi/nâng cấp; `tools/transaction.py` status/resume/rollback; đã thử kill giữa chừng rồi tiếp tục và phục hồi.
- Trang "Tình trạng ứng dụng", lịch sử thao tác, gói chẩn đoán đã che dữ liệu, nút Tiếp tục/Phục hồi, "So sánh" ở trang Chờ hợp nhất.
- Mọi công cụ bảng điều khiển gọi phát kết quả có cấu trúc.
- Cổng phát hành bắt buộc, `--rc`, báo cáo cổng, kiểm Python 3.8 (heuristic), CI workflow, `.github/RELEASING.md`.
- Rà truy cập (bàn phím, focus, tương phản, màn hẹp), kiểm thử giao diện bằng Playwright; kịch bản nghiệm thu người dùng.
- Tài liệu VI/EN, CHANGELOG, tools/README, HTML hướng dẫn đồng bộ; roadmap mục 13 ghi tiến độ.
- 87 kiểm thử hành vi đạt; kiểm package 0 lỗi; MANIFEST đã ghi lại.

## Current artifact
- roadmap/ROADMAP_HOAN_THIEN.md (mục 13), roadmap/KICH_BAN_NGHIEM_THU_NGUOI_DUNG.md
- Thay đổi trong working tree; xem git status/diff.

## Open items
- CI chưa chạy (cần push, chưa được phép); chưa thử macOS, Python 3.8, trình đọc màn hình.
- Chưa nghiệm thu với người dùng mới theo kịch bản.
- Hợp nhất `.new` vẫn thủ công; bước init sau chuyển đổi nằm ngoài giao dịch.
- VERSION 1.7.0 (MINOR: tính năng mới tương thích ngược); CHANGELOG mục v1.7.0.

## Waiting on user
- Xem kết quả CI trên PR và quyết định gộp vào main; tổ chức một phiên nghiệm thu với người dùng mới; xem kết quả CI sau khi phát hành.

## Decisions
- Người dùng giao hoàn thiện roadmap; orchestrator/reviewer điều phối subagent Haiku (xhigh) thi công theo phạm vi file tách biệt.
- Dữ liệu vận hành cục bộ nằm trong thư mục runtime dưới .agent, không vào MANIFEST, ZIP, git.
- tests/, roadmap/, .github/ chỉ dành cho kho nguồn, không vào package người dùng.
- Người dùng đồng ý commit và push để chạy CI: commit trên nhánh roadmap-giai-doan-10-13, mở PR vào main; chưa gộp, chưa phát hành.

## Next milestone
Chạy CI trên ma trận đa nền tảng và một phiên nghiệm thu với người dùng mới; sau đó chọn phiên bản và tạo release candidate.
