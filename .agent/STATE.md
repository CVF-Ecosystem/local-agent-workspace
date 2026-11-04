# PROJECT STATE
<!-- local-agent-workspace: maintainer-state -->
## Goal

Hoàn thiện LAW thành văn phòng trung tâm: giao việc tự nhiên, đầu ra có căn cứ, sửa và tiếp đúng bản, giữ dữ liệu và quyền riêng.

## Current phase

04/11/2026: Local chốt roadmap r2 sau đối chiếu phản biện Claude và CI thực. Giữ nền hiện hữu; sản phẩm PRERELEASE_NOT_READY. Chỉ cập nhật kế hoạch, chưa sửa registry/code hoặc chạy ca sản phẩm.

## Completed

- Đã đọc bản hợp nhất nghiên cứu web, README, đính chính S04 và disposition S08; không biến prompt trong ZIP thành quyền thi công.
- HEAD hiện 32604fbd3d00da53cffff2a8d3735e372f05f23f, chỉ thêm catalog/README so baseline62c942e; ref lưu máy cùng SHA. PR10 đã merge. Hai CI runs41575566248/41794538743 đều 5/5 job lỗi Package check; hai log Ubuntu3.12 báo PACK target thiếu.
- Profile hợp cấu trúc, owner PROFILE; Scout/Worker/Reviewer đều NO_GRANT. Catalog có sáu phương pháp, chưa chứng minh mọi host/role hoạt động.
- ZIP50 hiện hữu khớp SHA trong receipt; bốn file chart khớp receipt. Không chạy lại tests hoặc nghiệm thu toàn artifact.
- Bằng chứng cũ được giữ: V1–V6 có các subset giới hạn, Antigravity nội dung/continuity bounded; P1 sáu ca và năm boundary riêng; CVF dev guidance đã nhận ở lớp tài liệu.

## Current artifact

- Roadmap hiện hành: roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md, mục Local 04/11, revision LOCAL-ROADMAP-20261104-r2; §7 xử lý F1–F9. Hash roadmap/HANDOFF r1 khớp phản biện; bản trước ở archive/maintainer/roadmap-local-r1-before-claude-review-20261104/.
- Brief và phạm vi kiểm: mục cùng revision ở đầu .agent/HANDOFF.md. Không có assignment mới cho Worker/Reviewer.
- ZIP50: working/release-closure-20261031/attempt2/artifacts/local-agent-workspace-v1.9.0-rc5.zip; SHA29fbeeed…713af, source8db7589f; receipt ACCEPTANCE-complete.json ở thư mục release-closure.
- Source/evidence mới: working/chart-quality-20261031/, panel-intake-20261031/, source-response-20261031/, delta-artifact-20261031/ và gate-runtime-20261031/. Source được nhận riêng không đồng nghĩa có ZIP mới đạt.
- Nghiên cứu gốc: C:/Users/DELL/Downloads/LAW_LOCAL_RESEARCH_HANDOFF_20261104.zip; SHA0baae123…75bede. Không giải nén/cài hoặc sửa nguồn này.

## Open items

- V1/V2/V4: routing, chất lượng nội dung/nguồn và kết hợp nghề ngoài ca đã kiểm; cần output dùng được, rubric/expected có căn cứ.
- V2/V5/V6: native protocol/context/Overwrite, lỗi/dừng/kết quả muộn và fresh-session; host enforcement chưa được chứng minh.
- V4/V7: QA Word/XLSX/HTML theo claim, host/support; Excel173 cause UNKNOWN/native QA chưa đạt. Chart còn giới hạn hiển thị theo receipt.
- V3/V7/P1: UI53, race thực, lưu/thay file, ngắt ghi/corruption/recovery/Undo/schema và W1–W4; nguồn/hiệu lực/provenance chưa đủ, root INDEX vắng trong snapshot đã kiểm.
- V7: clean source thiếu target của dòng PACK academic, chưa sửa; artifact54 timeout1800s vẫn cause/test totals UNKNOWN, release_tree/ZIP mới NOT_RUN; còn gates, fresh/adopt/upgrade, luồng bản giao và review đúng artifact.
- Năm gói DEFER; P2 inactive; D1–D5 DEFERRED_USER. Academic PAUSED/REVIEW/DEFER, intake1/4 thiếu và entry description drift chưa sync.
- V6/M5: feedback thật NOT_RUN, kit C-02 giữ chuẩn bị. M6/official/rollout còn điều kiện và quyền riêng; không nhận toàn roadmap từ các subset.

## Waiting on user

Không cần chốt lại lựa chọn kỹ thuật của roadmap. Quyền gọi vai, mở học thuật, mời/trả phí chuyên gia, dữ liệu ngoài phạm vi và publish chưa được mở bởi yêu cầu lập kế hoạch; chỉ hỏi khi phần thi công cụ thể thực sự phụ thuộc.

## Decisions

- Local chốt: preflight source 4.0 và chuẩn bị luồng báo cáo–số liệu–nháp thư 4.1 → sửa/tiếp phiên → nguồn/bảo toàn → định dạng → artifact. Output đã QA có thể giao và nhận góp ý tùy chọn sớm; không thay pilot hoặc QA dev.
- Giữ V0–V7/R/T và acceptance gốc; mỗi giao việc nêu toàn gap, phần sẽ đóng và phần còn lại. Không tạo roadmap/work order song song hoặc tự mở agent phụ.
- Dùng native/owner hiện hữu cho đợt này; upstream chỉ xét khi có gap cụ thể và phép so có thể đổi quyết định. Không thêm runtime/UI/database mới theo danh mục nghiên cứu.
- Chỉ định bảo trì 31/10 giữ làm requested: Terra6.1 High, việc khó Sol Medium; actual backend/effort phải ghi theo bằng chứng, không tự đổi profile sản phẩm hoặc mở quyền gọi vai.
- Không full retry artifact54/COM173 khi chưa có căn cứ nguyên nhân/phép phân biệt hữu hạn; giữ chi phí nhánh và lịch sử thất bại. Không hạ gate để có tiến độ.
- Kho pháp lý do project khác làm sạch; LAW dùng public inputs/DATAMOCK trong quyền. Giữ academic pause và các giới hạn intake/install/confirm/export/publish.

## Next milestone

Bắt đầu 4.0 V7/M4: chốt diff source/registry và reviewer áp dụng; chuẩn bị độc lập 4.1 V1/V2/V4: đọc nguồn/output ca đã chọn, khóa ba fixture/oracle/hash trước chạy. Roadmap r2 đã được Claude review đạt theo giao trực tiếp của operator (roadmap/REVIEW_DOC_LAP_CLAUDE_ROADMAP_LOCAL_R2_2026-11-04.md); review diff 4.0 cần operator giao riêng. Kiểm WIP/binding/quyền và toàn gap §3–5 trước thi công; không build lại hoặc mở campaign upstream.
