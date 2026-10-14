# PROJECT STATE

## Goal
Hoàn thiện Local Agent Workspace: bảo toàn native của agent người dùng chọn, chuẩn tiếp nhận skill/gói chung (yêu cầu của operator, 14/10/2026).

## Current phase
VERSION 1.8.0 (MINOR): đợt "bảo toàn native và chuẩn tiếp nhận skill" đã kiểm thử và commit trên nhánh skill-intake-native-first-v1.8.0 (từ main b4453d7); chưa push, chưa merge, chưa tạo release.

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
- Năm gói đi kèm chưa có hồ sơ tiếp nhận nên cài thành REVIEW; muốn AVAILABLE thì cần hồ sơ thật (ba việc thật, thử trên ứng dụng agent thật), không tự điền.
- Bản chép skill sang ứng dụng bằng phiên bản cũ không có dấu nên không còn thay được bằng `--overwrite`.
- Thử thăm dò với qwen-plus/qwen-max (14/10/2026, dữ liệu giả): qwen-max vẫn tự nói sẽ đổi REVIEW→AVAILABLE khi được nhờ cài skill REVIEW; hướng dẫn không đủ chặn, công cụ chặn. Chưa có đánh giá của người dùng; CI chưa chạy; chưa thử macOS, Python 3.8 thật.

## Waiting on user
- Quyết định push/release; có ghi hồ sơ tiếp nhận cho gói đi kèm hay giữ thử nghiệm; đánh giá của người dùng (làm sau).

## Decisions
- Dữ liệu vận hành cục bộ nằm trong thư mục runtime dưới .agent, không vào MANIFEST, ZIP, git.
- tests/, roadmap/, .github/ chỉ dành cho kho nguồn, không vào package người dùng.
- Không tạo registry/checker/engine mới cho tiếp nhận; công cụ chỉ kiểm phần kiểm được bằng máy, không chấm "tốt hơn native".
- REVIEW vẫn dùng thử được trong project (nói rõ là bản thử); chỉ chặn xuất sang ứng dụng và đưa vào gốc.

## Next milestone
Người dùng duyệt diff và commit; sau đó chạy CI và chọn phiên bản phát hành.
