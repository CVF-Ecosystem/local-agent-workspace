# PROJECT STATE

<!-- local-agent-workspace: maintainer-state -->

## Goal

Phát triển LAW thành workspace local dùng lâu dài cho công việc văn phòng; agent native điều phối vai, giữ nguồn/skill và tiếp tục công việc gọn, tự đủ trong LAW.

## Current phase

21/10/2026: RC1/MVP nội bộ đã qua review ACCEPTED_WITH_LIMITS. Operator chốt đẩy nguồn lên GitHub CVF-Ecosystem/local-agent-workspace; nhánh bàn giao branding-tokens. Commit nguồn RC1 vẫn6f39c60b; commit review/roadmap sau đó chỉ metadata, không đổi ZIP/code hoặc dựng lại. Chốt baseline để dùng và lấy feedback; chưa official/CI.

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

- RC1: dist/local-agent-workspace-v1.9.0-rc1.zip,1177698byte/261file; SHA256 3b0ea0888496a653b9c1ece77d1a13fdd13d5996ffdc2bc5f212775026c703f4. Gate cùng tên+.gate.json:4passed, commit6f39c60b77d368793612541f546ca92688289518/dirty=false lúc build.
- Verdict/lệnh/hash/phạm vi ở đầu HANDOFF và roadmap0.11. Buildstdout1/2/3 giữ ở dist;2/3 timeout trước đóng ZIP, không chuyển failed thànhpassed.
- Main đã verify giải nén mới0đổi/0thiếu; archive probe từ git archive HEAD,2stage độc lập bằng owner projection/manifest+nguyên ZIPwriter đều trùng RC1. Không fullsuite/gate patch/newgateJSON hay thay RC1.
- Worker nghiệm thu UI headless/newproject/upgrade/restore; Main so log và filesystem: profile0grant, rawbytes gói khớp trừ tools/check_output.py chủ ý sửa, incoming.new đúng;7file riêng giữ,229file restored khớp.
- Source RC1 commit6f39c60b; review/roadmap/STATE được commit bổ sung để bàn giao GitHub. Remote origin=https://github.com/CVF-Ecosystem/local-agent-workspace.git; nhánh branding-tokens. dist vẫn gitignored, không upload ZIP/Release. Maintainerprofile thật vắng, không sửa global/native grants.

## Open items

- A-09 capture nội bộ đúngbytes cho validate/plan/hash/backups. Config gắn toàn hash PROJECT chỉ đọc; bất kỳ dòng đổi làm token cũ PLAN_CHANGED, preview lại. Chấp nhận bảo thủ, không thêm permissionline projection; chưa kernel-race/atomic2file proof.
- Mọi giao dịch dở (không riêng owner path) chặn luồng profile; ghi PROJECT+profile là nhóm có phục hồi, không nguyên tử. Symlink file thật chưa đo (WinError1314), chỉ junction runtime đã đo.
- Upgrade bằng script cũ trong project không bootstrap profile; chạy lại bằng script mới. A-06/A-07 giữ giới hạn cũ; D4 chỉ bản lab6ee4cef2, không duyệt phát hành.
- A-10 core có3vai/preset candidate/retire đã review. Proof lab chỉ capability/model/locator: còn1finding diễn đạt nhỏ candidate dòng21, giữ CANDIDATE/chưa user acceptance; telemetry0.38191935USD không hóa đơn. Không nhận model quality/fullR4/enforcement.
- Adapter status vẫn NOT_INSPECTED cho host: receipt không chứng minh invocation. Proof riêng đã quan sát model/Read, chưa sandbox/tools enforcement. Native+receipt có journal nhưng không nguyên tử, còn TOCTOU cuối; parser identity subset/nested unknown từ chối.
- RC1 chỉ có evidence local Windows/NTFS/Python3.11.9; CI/official chưa có. GateRC1 đo gitclean tại commit6f39; hiện dirty metadata sau build. UI log không chứng minh nội dung từng trang/visual; Office visualQA và symlink file thật chưa đo.

## Waiting on user

- Operator đã chốt baseline và cho push nguồn MVP lên repo chỉ định; không chờ xác nhận lại quyền này. Feedback trải nghiệm thật được ghi sau khi dùng, chưa có bằng chứng usability mới.
- Chưa cấp official-release/upload ZIP, merge main hoặc host-global-admin/CVF cha; không tự mở scope. CI chưa có kết quả cho nguồn1.9.0, không suy push thành CI xanh.

## Decisions

- Operator amendment0.10: MVP trước/feedback sau; C-02/T37–T38 và phần người thật R6/T36/T48 chuyển sau MVP, không thành PASS. Giữ gate bảo toàn/quyền/nâng cấp/package/release; không mở thêm feature.
- A-09 diagnostic đã NOT_INSPECTED, không phủ định host chưa kiểm; authority_usable=False/profile_refUNSUPPORTED giữ. LEGACY cho xuất native nếu profile hợp lệ/owner nhất quán/lựa chọn rõ, không migrate hoặc suy quyền dispatch.
- A-10 một host/ba core role; factory candidate Haiku5.5/Sonnet5.5/Sonnet5.5 effortnull, không autofill profile. Effort/tier/fallback/limits chưa map UNSUPPORTED, không thêm vòng đo effort. Write không cưỡng chế new-only/path sandbox.
- Retire đã đo: một Windows no-replace rename→fixedinactive, receipt giữ/post-reconcile; RETIRE_CONFLICT chặn apply, không autoactivate/livecancel. Reviewer product không mang quyền sửa nhỏ maintainer; candidate_presets khác product_presets.
- A-11: current TASK/RESULT dùng v3 khi cần; so binding hiện hành và bytes thật trước writer. Publish task riêng bind raw TASK/RESULT/candidate/source/sổ đã dùng; staged lấy chính candidate bytes đã so hash. Một writer, không generic PASS/authority/acceptance hoặc native sandbox.
- Dòng PROJECT trống/placeholder bootstrap owner PROJECT không grant; mẫu sạch dùng con trỏ + owner PROFILE. Không tạo/migrate profile maintainer.
- B-02: version/quan hệ cùng sổ, không ContentID/engine/receipt/current-pointer mới. Mở cũ khác dùng mới: prepare kiểm closure/giữ unknown+inference+limits; stale sau publish từ chối register. x14 PARKED; không refresh pin/MANIFEST/RC3.

## Next milestone

Giữ baseline RC1 và nguồn bàn giao GitHub trên branding-tokens; nhận feedback thật khi dùng MVP nội bộ. Codex chốt finding cần sửa, Claude thi công/Codex review; chưa có finding thì không mở tranche hoặc build mới. Official/merge main là công việc riêng khi được giao.
