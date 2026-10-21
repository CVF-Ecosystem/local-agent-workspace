# PROJECT STATE

<!-- local-agent-workspace: maintainer-state -->

## Goal

Phát triển LAW thành workspace local dùng lâu dài cho công việc văn phòng; agent native điều phối vai, giữ nguồn/skill và tiếp tục công việc gọn, tự đủ trong LAW.

## Current phase

21/10/2026: Operator giao “sửa đi” sau review L19. Đã sửa diagnostics export và test portability trên nhánh fix/l19-ci-diagnostics; giữ runtime, schema và giá trị pin. Main hoàn tất phần worker CI bị hết dung lượng, reviewer độc lập đã nhận diff, không thấy blocker; 103 test tập trung đạt. Chưa nhận CI mới hoặc thay RC1 đã công bố.

## Completed

- G-00/G-01/G-02, C2/P-CN1 một file và G-03 baseline hợp tác hẹp/G-04 candidate đã nhận đúng phạm vi; COOPERATIVE/ADVISORY, không host enforcement.
- I1/P-CTX1, I2 navigation, I3 package/lifecycle và A-02 core T01–T04 đã nhận WITH_LIMITS; không dispatch lại.
- A-06 lockleaf, A-07 thư viện dùng chung/chọn nguồn và A-08 static contracts đã nhận WITH_LIMITS; T16 template/static/read-API nhận.
- A-09 accepted: Worker corrective module46collected/45đạt/1skip; Reviewer7test độc lập đạt/0skip, P2 resolved. Worker198test trước statusfix/corrective giữ riêng lịch sử; không full198/fullgate source cuối.
- A-10 Scout: Reviewer39test đạt trước sửa diagnostic cuối +2ca liên quan đạt sau sửa; không cộng thành fullsuite cuối. T28 hẹp: MainSonnet5.5→Agent law-scout→Haiku5.5 Read đúng nguồn giả; Reviewer soát trace nhận WITH_LIMITS.
- A-10 core: Reviewer32test hẹp đạt/0skip source cuối; lab2child Sonnet5.5 tạo candidate rồi review chỉ đọc,270file cũ không đổi/+1candidate; retire2role/listing mới không còn projectroles. Không fullmodule72/fullgate.
- A-11: Reviewer sửa3finding tại docs/test; sourcecuối25đạt/0skip=21probe+4projection. T29/T30 nhận subset hợp tác, không live Scout delta/nhiều TASK hoặc toàn R5.
- B-01: sourcecuối21content+15regression đạt/0skip; Main1probe source-event→A-11 tăngrev/giữbytes/chặn publish cũ. Worker94chạy=92đạt/2skip trước correction, không full94 sourcecuối.
- B-02: Reviewer34test+5panel+2browser đạt trước sửa opener cuối; sau sửa cuối9target đạt/0skip. Ba ca nợ docs/package đạt riêng; không cộng thành fullmodule/fullgate. Worker66artifact/61panel là trước correction.

## Current artifact

- Release: https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc1 ; published2026-10-21T05:22:38Z, prerelease=true/draft=false, target6f39c60b77d368793612541f546ca92688289518.
- Asset ZIP1177698byte/261file: SHA256 3b0ea0888496a653b9c1ece77d1a13fdd13d5996ffdc2bc5f212775026c703f4; gateJSON64cea39ce6e04cc892ce70705f908ede0488892f58d6bcf09d6caa6dd82165d0; checksumfile f8dcd28e1a25216559b90d22aecd9b76d316b029e389c610b3c6eba90195874a.
- Bản local ở dist/local-agent-workspace-v1.9.0-rc1*; ZIP/gate đã upload nguyên bytes. Gate4passed/1492test6skip ở source6f39;2fullrebuild sau timeout vẫnfailed,2archiveprobe đúngwriter bằngSHA.
- Release notes có tải/hướng dẫn/nâng cấp/backup/giới hạn và feedback. docs/FEEDBACK_FORM_VI_EN.md đã có trongZIP; GitHub Issue template phan-hoi.md tồn tại, Issues bật; chưa có feedback mới để ghi.
- Nhánh sửa fix/l19-ci-diagnostics từ ddd6118; origin/main1ca3f0c đã mergePR6(370ea81). Run39548822713:5jobfailedBehaviour,package/HTMLsuccess,RCbuild/uploadskipped. Review trước chỉ fetch; corrective hiện hành trên nhánh riêng, chưa có kết quả CI mới.

## Open items

- A-09 capture nội bộ đúngbytes cho validate/plan/hash/backups. Config gắn toàn hash PROJECT chỉ đọc; bất kỳ dòng đổi làm token cũ PLAN_CHANGED, preview lại. Chấp nhận bảo thủ, không thêm permissionline projection; chưa kernel-race/atomic2file proof.
- Mọi giao dịch dở (không riêng owner path) chặn luồng profile; ghi PROJECT+profile là nhóm có phục hồi, không nguyên tử. Symlink file thật chưa đo (WinError1314), chỉ junction runtime đã đo.
- Upgrade bằng script cũ trong project không bootstrap profile; chạy lại bằng script mới. A-06/A-07 giữ giới hạn cũ; D4 chỉ bản lab6ee4cef2, không duyệt phát hành.
- A-10 core có3vai/preset candidate/retire đã review. Proof lab chỉ capability/model/locator: còn1finding diễn đạt nhỏ candidate dòng21, giữ CANDIDATE/chưa user acceptance; telemetry0.38191935USD không hóa đơn. Không nhận model quality/fullR4/enforcement.
- Adapter status vẫn NOT_INSPECTED cho host: receipt không chứng minh invocation. Proof riêng đã quan sát model/Read, chưa sandbox/tools enforcement. Native+receipt có journal nhưng không nguyên tử, còn TOCTOU cuối; parser identity subset/nested unknown từ chối.
- CI main1ca3 hiệnfailed5/5; RC1 localWindows3.11.9 giữ evidence lịch sử, không chuyển CI thànhPASS. L19-02diagnostics appliesRC1; chưa nên coi ZIPchẩnđoán đãche sạch đườngdẫn. Parser test đã chốt injection RecursionError, không thêm depth policy; chưa visualQA/symlinkfile thật.

## Waiting on user

- Không còn quyết định chặn corrective L19: đã có quyền sửa và quyền GitHub từ phiên trước.
- RC1 vẫn là prerelease; chưa có yêu cầu stable/final hoặc thay asset/tag RC1.

## Decisions

- Operator amendment0.10: MVP trước/feedback sau; C-02/T37–T38 và phần người thật R6/T36/T48 chuyển sau MVP, không thành PASS. Giữ gate bảo toàn/quyền/nâng cấp/package/release; không mở thêm feature.
- A-09 diagnostic đã NOT_INSPECTED, không phủ định host chưa kiểm; authority_usable=False/profile_refUNSUPPORTED giữ. LEGACY cho xuất native nếu profile hợp lệ/owner nhất quán/lựa chọn rõ, không migrate hoặc suy quyền dispatch.
- A-10 một host/ba core role; factory candidate Haiku5.5/Sonnet5.5/Sonnet5.5 effortnull, không autofill profile. Effort/tier/fallback/limits chưa map UNSUPPORTED, không thêm vòng đo effort. Write không cưỡng chế new-only/path sandbox.
- Retire đã đo: một Windows no-replace rename→fixedinactive, receipt giữ/post-reconcile; RETIRE_CONFLICT chặn apply, không autoactivate/livecancel. Reviewer product không mang quyền sửa nhỏ maintainer; candidate_presets khác product_presets.
- A-11: current TASK/RESULT dùng v3 khi cần; so binding hiện hành và bytes thật trước writer. Publish task riêng bind raw TASK/RESULT/candidate/source/sổ đã dùng; staged lấy chính candidate bytes đã so hash. Một writer, không generic PASS/authority/acceptance hoặc native sandbox.
- Dòng PROJECT trống/placeholder bootstrap owner PROJECT không grant; mẫu sạch dùng con trỏ + owner PROFILE. Không tạo/migrate profile maintainer.
- B-02: version/quan hệ cùng sổ, không ContentID/engine/receipt/current-pointer mới. Mở cũ khác dùng mới: prepare kiểm closure/giữ unknown+inference+limits; stale sau publish từ chối register. x14 PARKED; không refresh pin/MANIFEST/RC3.

## Next milestone

Chốt review L19, commit/push nhánh sửa và kiểm ma trận CI thật. Không thêm tính năng, không bỏ gate hoặc sửa pin để làm xanh; RC1 giữ nguyên bytes và lịch sử. CI mới chưa có kết quả thì ghi đang chờ, không dùng local test thay thế.
