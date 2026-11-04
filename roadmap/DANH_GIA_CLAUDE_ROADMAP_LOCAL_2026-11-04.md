# Đánh giá của Claude về roadmap Local 04/11/2026

**Đối tượng:** `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md`, mục "Quyết định và roadmap chi tiết của Local — 04/11/2026" (dòng 4–152), revision `LOCAL-ROADMAP-20261104-r1`, cùng brief đầu `.agent/HANDOFF.md`.
**Bản đã đọc (working tree, chưa commit):** roadmap SHA256 `d333bbac167ccbb6100b5955023d8007ca8b90fb7a8606fa998e68c555154805`; HANDOFF SHA256 `ec70cd0110e4262efc644ff89131cf7ab6b4076c569c22398e7a28b8d03bf0e7`.
**Người đánh giá:** Claude (Opus 5.5) trong Claude Code, theo yêu cầu của operator. Đây là ý kiến phản biện, không phải review độc lập theo mục 8.3, không cấp quyền và không thay quyết định của Local.

## Kết luận

**Đồng ý hướng, có điều kiện.** Chọn hoàn thiện một luồng hữu ích (báo cáo – số liệu – nháp thư) trên nền hiện có, không mở platform/upstream mới, là đúng. Trước khi bắt đầu 4.1 nên xử lý F1 và chốt F2–F3; các điểm còn lại có thể sửa trong revision kế tiếp.

## Điểm đồng ý

1. **Trọng tâm đúng.** Ưu tiên chất lượng đầu ra dùng được thay vì mở rộng khung; khớp bài học trong `roadmap/GHI_NHAN_PHAM_VI_CVF_VA_BAI_HOC_OVERENGINEERING_2026-10-18.md`.
2. **§5 tốt.** Mỗi nhánh upstream/gói hoãn có điều kiện mở lại cụ thể, không cấm vĩnh viễn, không buộc tích hợp.
3. **Artifact54 không retry mù.** Đòi giả thuyết và phép phân biệt hữu hạn trước khi chạy lại là đúng.
4. **Đúng quy tắc 10.** §3 đối chiếu toàn bộ gap V0–V7; mỗi gói có "Còn sau đó".
5. **Baseline trung thực và kiểm lại được.** Mình tính lại: ZIP50 SHA256 `29fbeeed…8713af` khớp; `execution_profile.py status` cho Scout/Worker/Reviewer đều `NO_GRANT`, owner `PROFILE`; kit `feedback/pilots/c02/` có `DIEU_PHOI.md`, `NGUOI_THU.md`, `PHIEU_GHI_NHAN.md`.

## Điểm cần sửa

### F1 — CI đỏ 5/5 job, roadmap chưa ghi (mức cao, nên làm trước 4.1)

- **Quan sát:** bốn lần chạy CI gần nhất đều `failure` (`36cfce9`, `972b569`, `62c942e` và `32604fb`, 01–04/11). Ở `62c942e` (run 41575566248) và `32604fb` (run 41794538743), cả 5 job đều failure. RC4 trước đó có 3/5 job đạt, nên đây là thoái lui.
- **Nguyên nhân (đã đọc log job Ubuntu/Python 3.12 của run 41575566248):** bước `python tools/check_package.py --release` báo đúng 1 lỗi: `.agent/SKILL_INDEX.md: law-academic-research trỏ tới file không có (skills/local/packs/academic-research/skills/law-academic-research/SKILL.md)`. Dòng này được thêm vào bản tracked ở commit `ce3407d`. Ở máy local, file tồn tại nhưng bị loại khỏi git bởi `.git/info/exclude:16` (`/skills/local/packs/`), nên kiểm local đạt còn CI thì không.
- **Vì sao quan trọng:** repo công khai và README vẫn ghi CI 3/5. Gate ở 4.5 và mọi review dựa vào CI. Bản thân roadmap ghi "chưa kiểm CI hiện hành".
- **Đề xuất:** thêm dòng 4.0 nhỏ: chọn cách xử lý dòng `law-academic-research` trong bản tracked (gói đang PAUSED/REVIEW) rồi kiểm lại CI. Bài học cần ghi: gate local phải chạy trên checkout sạch (worktree), không trên cây có file bị exclude. Mình chưa sửa vì đây là quyết định về SKILL_INDEX của owner Local.
- **Chưa kiểm:** log của 4 job còn lại ở từng run, và nguyên nhân thất bại ở `36cfce9`/`972b569`.

### F2 — 4.1 chưa có phép đo đóng được (mức cao)

- "Đối chiếu đúng ca V2/V4 hiện hữu" không nêu ca nào, rubric ở đâu, bao nhiêu ca mới. Điều kiện đóng ("output dùng được", "trace đúng claim") là phán đoán, nên khó biết khi nào xong.
- Các thư mục có sẵn có thể là ứng viên: `working/v2-report-loop/`, `working/v4-office/`, `working/numeric-report-quality-20261029/`, `working/communications-quality-20261029/`. Mình mới xác nhận chúng tồn tại, chưa đọc nội dung.
- **Đề xuất:** ghi ngay trong 4.1: (a) danh sách ca regression theo đường dẫn; (b) một bộ ca mới nhỏ chưa dùng để chỉnh (ví dụ ba ca: thường, thiếu/mâu thuẫn, dữ liệu xấu), với expected viết và ghi hash trước khi chạy; (c) nơi lưu rubric và người chấm.

### F3 — Người chấm nội dung độc lập đang bị chặn nhưng 4.1 không nêu (mức cao)

- 4.1 cấm dùng AI tự đồng ý làm căn cứ duy nhất, trong khi profile hiện `NO_GRANT` cho cả Reviewer và chưa có chuyên gia. Vì vậy 4.1 không thể đóng theo chính điều kiện của nó. Roadmap chỉ ghi `BLOCKED_AUTHORITY` ở 4.2.
- **Đề xuất:** hỏi operator một lần, ngay khi mở 4.1, chọn một trong ba: (a) cấp grant Reviewer cho nhóm việc 4.1; (b) operator tự chấm bộ ca nhỏ theo phiếu có sẵn; (c) chấp nhận đóng 4.1 ở mức WITH_LIMITS, ghi rõ phần nội dung chưa được chấm độc lập.

### F4 — Không có ngân sách/điểm dừng theo gói (mức trung bình)

Chỉ 4.5 có giới hạn chi phí. Với lịch sử overengineering, mỗi gói nên có trần (số phiên hoặc lượt trả phí) và điều kiện "dừng và báo". Roadmap đã nói không có số đo để cam kết ngày; trần công vẫn đặt được mà không cần ngày.

### F5 — Giá trị bị kẹt sau 4.5 (mức trung bình)

Người dùng chỉ nhận cải tiến khi có ZIP mới (4.5), nhưng 4.5 đứng cuối và artifact54 đang `BLOCKED_CAUSE`. Đề xuất mở song song một phép phân biệt rẻ, có trần công, cho artifact54, như đo thời gian theo từng module test trên cây sạch. Đây là gợi ý giả thuyết, mình chưa kiểm. Roadmap đã cho phép phần độc lập chạy song song; chỉ cần ghi tên và trần cho phép này.

### F6 — 4.3 rộng so với claim đang công bố (mức trung bình)

UI53, race thực, atomic save, corruption, Undo, schema và W1–W4 là một chương trình bảo toàn lớn. Đề xuất cắt theo claim README đang công bố (đúng tinh thần DA05). Phần không công bố thì ghi là chưa hỗ trợ, thay vì phải làm cho đủ.

### F7 — Phản hồi người thật đứng cuối (mức trung bình)

Từ RC4 (24/10) chưa có người dùng thật. Đề xuất: sau khi 4.1 có đầu ra, operator tự dùng luồng đó cho một việc thật của mình và chỉ ghi nhận quan sát. Việc này không phải pilot C-02, rẻ, và giảm rủi ro tối ưu theo tiêu chí giả định.

### F8 — Khó đọc với operator (mức thấp)

Mật độ mã viết tắt cao (UI53, Excel173, artifact54, ZIP50, W1–W4, D1–D5, DA01–05, T01–T48, AC, M4–M6) và không có chú giải trong mục. Đề xuất thêm 5 dòng tóm tắt bằng lời thường ở đầu mục và bảng chú giải mã, hoặc trỏ tới `roadmap/CATALOG_CAU_TRUC_VA_TIEN_DO.md`.

### F9 — Baseline lệch một commit (mức thấp, thông tin)

HEAD nay là `32604fb`: commit tài liệu thêm catalog, đã đẩy lên `origin/main` ngày 04/11. Commit này không chạm code; baseline `62c942e` vẫn dùng được, chỉ cần ghi khi đối chiếu WIP lúc mở 4.1.

## Chưa kiểm

- Không chạy test, build hay fullgate. Không đọc nội dung các ca V2/V4, receipts, log artifact54 hay ZIP nghiên cứu web.
- Không đọc toàn bộ HANDOFF, chỉ brief 04/11.
- Chưa đối chiếu §3 với từng tiêu chí gốc V0–V7 và T01–T48.
