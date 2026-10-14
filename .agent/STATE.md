# PROJECT STATE

## Goal
Hoàn thiện Local Agent Workspace: bảo toàn native của agent người dùng chọn, chuẩn tiếp nhận skill/gói chung (yêu cầu của operator, 14/10/2026).

## Current phase
PR #2 (v1.8.0) đã merge vào main (35994e6); chưa tag, chưa release. Nhánh skill-intake-claim-vs-approval (từ main) sửa 3 phát hiện của review độc lập; commit cục bộ, chưa push.

## Completed
- Chuẩn tiếp nhận chung tại `skills/README.md` (VI/EN); AGENTS, SKILL_INDEX, README vùng skill, packs/README, hướng dẫn skill/tạo/chuyển đổi project dẫn chiếu về đó.
- `pack.py`: khối `intake` trong pack.json; ứng viên cài thành REVIEW; REUSE_NO_IMPORT/REJECT_VERSION không cài; đổi phiên bản về REVIEW; giữ trạng thái người dùng đặt trong cùng phiên bản.
- `install_skills.py`: chỉ chép AVAILABLE/ACTIVE, phải chọn rõ, không đè thư mục cùng tên không có dấu `.workspace-skill.json`, sao lưu vào archive/.
- `adopt_project.py`: skill có sẵn ghi REVIEW. Bảng điều khiển: ô chọn skill, nhãn "Thử nghiệm"/"Đã tiếp nhận".
- `tests/test_skill_intake.py` (12 test logic) + 1 test trình duyệt; toàn bộ 100 test đạt; check_package (thường và --release) 0 lỗi; MANIFEST, HTML hướng dẫn đã dựng lại.
- Audit lần 2: sửa hồ sơ bị rút trong cùng phiên bản vẫn giữ AVAILABLE; `pack.py check` báo gói đã cài bị hồ sơ ghi không nhận; sửa trợ giúp `--skills`; README và SKILL_INDEX ghi rõ cơ sở AVAILABLE của 14 skill dùng chung.

## Current artifact
- Thay đổi trong working tree (40 file sửa, 1 file mới); xem git status/diff. CHANGELOG mục "Chưa phát hành".

## Open items
- Review độc lập (agent khác, 14/10/2026) có SI-01/02/03: đã tái hiện và sửa (lời khai gói ≠ xác nhận; xác nhận gắn dấu vân tay nội dung; xuất dùng chung hàm điều kiện). Chưa chạy lại browser test với Playwright ngoài máy này; CI macOS-13/Python 3.8 lúc review còn queued.
- File LAW_V180_NATIVE_INTAKE_FOLLOWUP_20261014.zip (báo cáo reviewer) nằm ở thư mục gốc, không thuộc repo: không commit; coi chừng `check_package --write-manifest` ghi nhầm nó vào MANIFEST.
- Năm gói đi kèm đã có hồ sơ tiếp nhận (DEFER, SUPPLEMENT) kèm A/B qwen-plus; vẫn REVIEW. Muốn nhận cần: người đối chiếu legal-basis với văn bản chính thức, ba việc thật trên ứng dụng thật, đánh giá của người dùng; bản có skill vẫn có "nguyên văn" không có trong gói.
- Bản chép skill sang ứng dụng bằng phiên bản cũ không có dấu nên không còn thay được bằng `--overwrite`.
- Thử thăm dò với qwen-plus/qwen-max (14/10/2026, dữ liệu giả): qwen-max vẫn tự nói sẽ đổi REVIEW→AVAILABLE khi được nhờ cài skill REVIEW; hướng dẫn không đủ chặn, công cụ chặn. Chưa có đánh giá của người dùng; CI chưa chạy; chưa thử macOS, Python 3.8 thật.

## Waiting on user
- Nhánh skill-intake-native-first-v1.8.0 đã push (b090a21, 64fd18f); chưa có PR, chưa merge, chưa release.
- Người review là user/agent khác, không phải người giao việc hay agent đã làm. Họ quyết định merge/release và có tự kiểm căn cứ pháp lý hay không; hồ sơ gói ghi sẵn phần còn thiếu.
- CI có sẵn và là tùy chọn của người review: chạy khi mở PR vào main, push vào main hoặc kích tay (workflow_dispatch). Push nhánh không tự kích CI; hiện chưa có lượt chạy nào cho nhánh này.

## Decisions
- Dữ liệu vận hành cục bộ nằm trong thư mục runtime dưới .agent, không vào MANIFEST, ZIP, git.
- tests/, roadmap/, .github/ chỉ dành cho kho nguồn, không vào package người dùng.
- Không tạo registry/checker/engine mới cho tiếp nhận; công cụ chỉ kiểm phần kiểm được bằng máy, không chấm "tốt hơn native".
- REVIEW vẫn dùng thử được trong project (nói rõ là bản thử); chỉ chặn xuất sang ứng dụng và đưa vào gốc.

## Next milestone
Người dùng duyệt diff và commit; sau đó chạy CI và chọn phiên bản phát hành.
