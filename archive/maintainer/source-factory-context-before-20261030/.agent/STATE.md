# PROJECT STATE
<!-- local-agent-workspace: maintainer-state -->
## Goal

Phát triển LAW thành văn phòng trung tâm: Main tổ chức nghiệp vụ, dùng công cụ phù hợp, giữ nguồn và tiếp việc lâu dài.

## Current phase

30/10/2026: roadmap revision30; P1 source/CLI FUNCTIONAL_REVIEWED_WITH_LIMITS. Lượt thực thi còn EXECUTION_PROTOCOL_NOT_MET và TEMP_CLEANUP_BLOCKED_BY_POLICY; chưa đóng toànP1. P2 chưa mở, V4/V7 PRERELEASE_NOT_READY.

## Completed

- P1 có intake preview mặc định/apply bound plan, cấu hình project, create-only file+sổ qua library_sync/transaction, staging giữ nguyên, fulltext mới để trống và verification Cần đối chiếu.
- Chỉ intake opt-in create_only/v2; owner mới đọc v1/v2, owner cũ từ chối v2. Defaultv1/create/create_exclusive và luồng upgrade/adopt giữ. Có recovery identity+SHA và chặn ghi sổ sau file conflict.
- P1:42ca chạy41đạt/1skip; sau sửa entrypoint thêm1ca và kiểm lại2CLI,3/3đạt. Tổng43ca duy nhất42đạt/1skip1314. Transaction rawlog48ca47đạt/1skip1314; wrapper in log lỗi mã hóa sau lưu, childexit UNKNOWN, không phải finalgate.
- P3/P4 đã nhận bounded: content-audit chỉ đọc và chuẩn tải an toàn; helper/test giữ hash. Các receipt167–177, V0–V6 và CVF/LawC6 bounded giữ ở roadmap, không nhận bytes mới bằng ZIP167.

## Current artifact

- working/source-intake-20261030/p1/{REVIEW.md,custody.json,incident.json,worker-evidence.md,worker-custody.json}; raw transaction-tests.log giữ failure/incident, transaction-review-safe.log giữ48ca sau sửa fixture.
- HANDOFF P1 revision6 đã kết thúc writer/review, không assignment ACTIVE. Worker Sol6.1 Medium đã FINAL; Main Codex tự sửa nhỏ và kiểm đúng phần. Hai module/test mới library_intake.py và test_library_intake.py cần có trong artifact sau.
- Main sửa safe fixture/read guard/mockINDEX-LESSONS, newrow thật trống/blankfulltext, config duplicatekeys/codecol, knownContentError/partialeffects và standalone __main__ result binding. Đủ3ca fixture gốc được giữ, không skip để xanh.
- Proof helper init/preview/backup4/4đạt. Packagecheck0lỗi14cảnhbáoREADME cũ trước finalCLI nhỏ; finalstatic/EOL/diff và HTML tạiHANDOFF. Baseline846mục chỉ theo tracked/explicit, không chứng minh toànignoreduserdata.

## Open items

- Sự cố runner: oldtesthelper copytreeROOT đã sao chép workspace vào C:/Users/DELL/AppData/Local/Temp/tx-check-wu4swqcl. Main chỉ khảo sát metadata10.000file/167.788.409bytes rồi dừngcap; không phải tổng, chưa đối chiếu nội dung/phạm vi từngfile.
- PID11256 đã dừng. Exacttempdelete bị automatic approval review chặn blocked by policy trước thực thi; không retry/bypass. Thư mục tạm VẪN CÒN, cleanup chưa đóng. Không nói cả lượt giữ phạm vi/bảo toàn sạch.
- Fixture mới dùng consumer factory nhưng mockINDEX/LESSONS vì thiếu cleanoverlay; sourcefactory usercontext ngoài overlay cần xét trước artifact mới. Không sửa factory hoặc nhận fullprojection từ fixture này.
- P2 cần điều kiện P1 và audit nguồn/API/quyền/dependency trước live. Phap-ly vẫn DEFER. P1 functionalproof không xóa protocolfinding hoặc mở mạng/P2.
- Source170+172+175+177+P3/P4+P1 cần cleanrevision/exactartifact/applicable gates/install-upgrade smoke/review; chưa fullsuite hoặc ZIP mới. ZIP167/source27761d1b chỉ proof cũ.
- Actual host/native/model/roles/errors/reopen/support/usability, widerrecovery/UI/ngắtghi/Undo/schema, Python3.8runtime/mac/filelink/cloud-only/WordRTL/theme còn thiếu. Excel173 NOT_MET_NATIVE_RECALC/causeUNKNOWN/0QA không retry COM.
- Academic PAUSED/REVIEW/DEFER, CVFM6held, các finding168/172/175 và failure history giữ. Profile12grant REVOKEDrev2, không native route/FUSE write mới hoặc đổi runtime/grant.

## Waiting on user

Không chờ user viết test/debug. Bản sao tạm do test còn vì policy chặn dọn, chưa có bằng chứng cleanup; thông báo rõ trong hội thoại. Không xin quyền install/promote/publish hoặc coi user đã nhận bản.

## Decisions

- Quyền30/10: Codex orchestrator/reviewer, Terra6.1 High mặc định; việc khó Sol Medium. Lượt P1 dùng1Worker Sol6.1 Medium, không agent khác; requested cấu hình không chứng thực backend/effort actual.
- P1 preview/apply chỉ trong staging đã khai và quyền đã cấp; config không grant, không tự tạo configroot. Không suy danh tính/toànvăn/hiệu lực từ tên/mã/hash hoặc tự nâng verification.
- Multi-file là giao dịch có phục hồi, không atomic toàn bộ; create no-clobber thật, index compare-before và source/path check vẫn cooperativewindow, không sandbox/hard enforcement.
- Giữ WIP, userdata, profiles, Gitindex và P3/P4 bytes theo receipt; rootignoreduserdata không kiểm nội dung. Không network/API/install/CVF/grant/stage/commit/push/tag/phát hành trong lượt này.

## Next milestone

Giữ P1 executionfinding/cleanup block để disposition, không nhận toànP1 hoặc activateP2. Các việc độc lập tiếp theo là audit nguồn/dependency theo roadmap và chuẩn bị sourcefactory/context/cleanartifact; cần brief đầy đủ trước giao. Toàn gaps V4/V7 vẫn mở.
