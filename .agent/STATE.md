# PROJECT STATE

## Goal
Hoàn thiện Local Agent Workspace: bảo toàn native của agent người dùng chọn, chuẩn tiếp nhận skill/gói chung (yêu cầu của operator, 14/10/2026).

## Current phase
PR #2 (v1.8.0) đã merge vào main (35994e6); chưa tag, chưa release. Nhánh skill-intake-claim-vs-approval (từ main) sửa 3 phát hiện của review độc lập; commit cục bộ, chưa push.

## Completed
- Chuẩn tiếp nhận chung tại `skills/README.md` (VI/EN); AGENTS, SKILL_INDEX, README vùng skill, packs/README, hướng dẫn skill/tạo/chuyển đổi project dẫn chiếu về đó.
- `pack.py`: khối `intake` trong pack.json là lời khai của gói; mọi gói cài là REVIEW; chỉ `pack.py confirm` của người dùng (gắn dấu vân tay nội dung) ghi AVAILABLE; hồ sơ phải giải được tới file local có thật; REUSE_NO_IMPORT/REJECT_VERSION không cài; DISABLED luôn giữ.
- `install_skills.py`: chỉ chép AVAILABLE/ACTIVE (skill của gói còn cần xác nhận còn hiệu lực), phải chọn rõ, không đè thư mục cùng tên không có dấu `.workspace-skill.json`, sao lưu vào archive/; bảng điều khiển dùng chung hàm điều kiện.
- `adopt_project.py`: skill có sẵn ghi REVIEW. Bảng điều khiển: ô chọn skill, nhãn "Thử nghiệm"/"Đã tiếp nhận".
- `tests/test_skill_intake.py` (18 test logic, gồm 3 phản ví dụ SI-01/02/03) + 1 test trình duyệt; 106 test đạt trên máy này; check_package (thường và --release) 0 lỗi.

## Current artifact
- Commit 4ce5c6d trên nhánh skill-intake-claim-vs-approval (từ main 35994e6); chưa push. CHANGELOG mục v1.8.0.

## Open items
- Review độc lập (agent khác, 14/10/2026) có SI-01/02/03: đã tái hiện và sửa (lời khai gói ≠ xác nhận; xác nhận gắn dấu vân tay nội dung; xuất dùng chung hàm điều kiện). Chưa chạy lại browser test với Playwright ngoài máy này; CI macOS-13/Python 3.8 lúc review còn queued.
- File LAW_V180_NATIVE_INTAKE_FOLLOWUP_20261014.zip (báo cáo reviewer) nằm ở thư mục gốc, không thuộc repo: không commit; coi chừng `check_package --write-manifest` ghi nhầm nó vào MANIFEST.
- Năm gói đi kèm đã có hồ sơ tiếp nhận (DEFER, SUPPLEMENT) kèm A/B qwen-plus; vẫn REVIEW. Muốn nhận cần: người đối chiếu legal-basis với văn bản chính thức, ba việc thật trên ứng dụng thật, đánh giá của người dùng; bản có skill vẫn có "nguyên văn" không có trong gói.
- Bản chép skill sang ứng dụng bằng phiên bản cũ không có dấu nên không còn thay được bằng `--overwrite`.
- Thử thăm dò với qwen-plus/qwen-max (14/10/2026, dữ liệu giả): qwen-max vẫn tự nói sẽ đổi REVIEW→AVAILABLE khi được nhờ cài skill REVIEW; hướng dẫn không đủ chặn, công cụ chặn. Chưa có đánh giá của người dùng; chưa thử macOS thật. CI GitHub đã chạy trên main (xem báo cáo review); các job Python 3.8 và macOS ở đó là bằng chứng của reviewer, không phải của lượt này.

## Waiting on user
- PR #2 đã merge vào main (35994e6); chưa tag/release. Nhánh sửa SI-01/02/03 chưa push, chưa có PR.
- Người review là user/agent khác, không phải người giao việc hay agent đã làm. Họ quyết định merge/release và có tự kiểm căn cứ pháp lý hay không; hồ sơ gói ghi sẵn phần còn thiếu.
- CI có sẵn và là tùy chọn của người review: chạy khi mở PR vào main, push vào main hoặc kích tay (workflow_dispatch). Push nhánh không tự kích CI; hiện chưa có lượt chạy nào cho nhánh này.

## Decisions
- Dữ liệu vận hành cục bộ nằm trong thư mục runtime dưới .agent, không vào MANIFEST, ZIP, git.
- tests/, roadmap/, .github/ chỉ dành cho kho nguồn, không vào package người dùng.
- Không tạo registry/checker/engine mới cho tiếp nhận; công cụ chỉ kiểm phần kiểm được bằng máy, không chấm "tốt hơn native".
- REVIEW vẫn dùng thử được trong project (nói rõ là bản thử); chỉ chặn xuất sang ứng dụng và đưa vào gốc.

## Next milestone
Người dùng duyệt diff và commit; sau đó chạy CI và chọn phiên bản phát hành.
