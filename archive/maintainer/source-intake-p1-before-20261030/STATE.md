# PROJECT STATE
<!-- local-agent-workspace: maintainer-state -->
## Goal

Phát triển LAW thành văn phòng trung tâm: Main tổ chức nghiệp vụ, dùng công cụ phù hợp, giữ nguồn và tiếp việc lâu dài.

## Current phase

30/10/2026: roadmap văn phòng revision29; P3/P4 được review và nhận có giới hạn ở CLI cục bộ. P1/P2 chưa mở. Toàn V4/V7 vẫn PRERELEASE_NOT_READY.

## Completed

- P3 có `library.py check --content-audit` chỉ đọc: SHA ghi/thực, binding khai báo theo scope, dấu hiệu PDF từng trang, kiểm cấu trúc OOXML có giới hạn. P4 chuẩn tải an toàn đã ghi VI/EN.
- Worker Terra6.1 High đã bàn giao/dừng. Codex review độc lập và tự sửa nhỏ trong cùng bước; 12 ca audit đạt, 73 ca sync có 2 skip file-symlink/error1314, 22 ca content đạt. Package check 0 lỗi/14 cảnh báo README cũ; 10 HTML khớp, EOL/diff và Python3.8 heuristic đạt.
- V0–V5 cùng các subset G/A/B/D đã nhận WITH_LIMITS; V6 kỹ thuật nhận giới hạn, chưa pilot/người thật. ZIP167/4gates thuộc source27761d1b và bytes cũ, không nhận bản vá mới.
- CVF acceptance source và workspace inheritance COMPLETE_BOUNDED; LAW C6/carrier adoption nhận giới hạn. Không còn chờ CVF learning hoặc user viết test để tiếp kiểm nội bộ.

## Current artifact

- P3/P4: working/source-intake-20261030/p3-p4/{REVIEW.md,custody.json,worker-evidence.md,baseline.json}; brief revision3 và acceptance map trong HANDOFF. Core helper mới tools/library_audit.py phải có trong artifact mới sau này.
- Proof mặc định: JSON khớp từng byte trên fixture với exact-before library SHA3144e937…f3dafd; nguồn/sổ fixture giữ bytes. Có actual junction/open-spy, PDF raster/mixed/encrypted và timeout child thật; chưa native file-symlink.
- Review sửa nhỏ: stdlib/raster fixtures, Office root relationship/DTD, byte cap trước child, giới hạn đúng100trang và giữ kết quả partial. Raw Worker evidence giữ findings ban đầu; không xóa failure history.
- Các receipt167–177 vẫn tại roadmap và working tương ứng: recovery169, inventory170, numeric171, Word172, Excel173, coauthoring174, library175, comms176, HTML177. Case177 rev2 đóng3finding bản in bounded; incidents/findings168/172/175 giữ.
- RC4 Windows DATAMOCK đã công bố tại source2552d7d; stable/latest1.8.0 giữ. ZIP/FHTML local trước đây không chứa HOST-SESSION mới; không suy nhận source hiện tại.

## Open items

- P1 importer staging create-only còn thiết kế/PRE với transaction+library_sync, concurrent save và phục hồi file+sổ. P2 sauP1 và audit quyền nguồn/API/dependency; phap-ly vẫn DEFER.
- Source patches170+172+175+177+P3/P4 cần cleanrevision/exactartifact/applicable finalgates/install-upgrade smoke/review. Chưa fullsuite hoặc ZIP mới trong lượt30/10.
- Actual host/native/model/roles/errors/reopen/support/usability và wider recovery/UI/ngắt ghi/Undo/schema còn thiếu. Python3.8 runtime/mac/file-link/cloud-only/WordRTL/theme chưa đủ evidence.
- Excel173 NOT_MET_NATIVE_RECALC, nguyên nhân UNKNOWN, nativeQA chưa chạy; giữ failure/rawlog/metadata giới hạn, không retry COM hoặc giao user debug.
- Academic PAUSED/REVIEW/DEFER; AC-A/B/C/D và fresh-host/intake gaps giữ tại roadmap. CVF M6 held; Gateway tests thiếu dependency, không có runtime AI enforcement/bridge/grant proof tổng quát.
- Profile product 12grant REVOKEDrev2, root Codex trial/lab grants giữ trạng thái đã thu hồi. Không native route mới/Cowork/FUSE writes hoặc đổi profile/runtime/grant.

## Waiting on user

Không chờ user viết test/gold hoặc debug để tiếp dev nội bộ. User quyết nghiệp vụ/quyền và feedback sau bản dùng được. Chưa có yêu cầu install/confirm/promote/rollout/publish mới; không mở các tác động đó.

## Decisions

- Chỉ định30/10: Codex orchestrator/reviewer; Worker Terra6.1 High, việc khó dùng Sol Medium. Lượt này chỉ gọi1Worker Terra; requested model/effort theo dispatch, backend thực tế chưa chứng thực độc lập.
- P3/P4 không đổi schema/cột/sheet/result envelope; default check và basic exit0/1/existing2 giữ. PDFminer.six optional20250506 đã đo trên Windows/Python3.11.9; không auto-install/vendor/fallbackfitz hoặc nâng core3.8.
- Hash/receipt chỉ gắn bytes; DECLARED_CHECK là lời khai trong scope, không chứng thực toàn văn/hiệu lực. Ít chữ là dấu hiệu, không tự kết luận scan hay nâng verification. P4 là quy tắc, chưa downloader/live.
- Giữ userdata/profiles/TVPL17skills haiđích, Git index và WIP khác. Không sync nguyên cây, tự cài hoặc mở quyền host; không stage/commit/push/tag/phát hành trong lượt này.

## Next milestone

Tiếp thiết kế/PRE P1 theo roadmap revision29 và acceptance28: create-only staging dùng owner transaction/library_sync, preview/apply, bảo toàn concurrent edits và phục hồi file+sổ. Chưa có brief P1 ACTIVE. Sau P1 còn P2 và toàn gaps V4/V7 nêu trên.
