# PROJECT STATE

<!-- local-agent-workspace: maintainer-state -->

## Goal

Phát triển LAW thành workspace local dùng lâu dài cho công việc văn phòng; agent native điều phối vai, giữ nguồn/skill và tiếp tục công việc gọn, tự đủ trong LAW.

## Current phase

21/10/2026: E07-A đã nhận ACCEPTED_WITH_LIMITS — READY_FOR_RC_PREPARATION; không review/test lại. Sau câu hỏi cụ thể về stage/commit phần bảo trì hiện tại và RC nội bộ, operator trả lời “vậy thì tiếp”: đã cho phép E07-B đúng scope đó. Chuẩn bị giao Claude; chưa stage/commit/build. C-02/M5 sau MVP; chưa RC/phát hành.

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

- Bàn giao hiện hành ở đầu HANDOFF và roadmap0.11; phạm vi MVP ở0.10, mock ở0.9, M3 verdict ở0.8. Diễn tập ở mock-rehearsal-20261021 dưới gốc M4: A/B riêng, 4MD và sổ/STATE riêng; không phiếu pilot người thật. Candidate261file/L-template/N-A/N-B giữ hash. Bản so sánh r2 dùng nguồn revision2; r1 và biên bản giữ bytes. Locator/hash đầy đủ ở HANDOFF.
- A-11/B-03 WITH_LIMITS: rolesREADME4ef708119400e59c/testc2ac1c912a96ab81. A-11 bodies AST giữ; B-03 revision/reconcile/identity/review gate/acceptance riêng. Reviewer33đạt trước sửa;14target đạt trước sửa oracle,4target sau/0skip; không fullmodule sourcecuối.
- B-02 ACCEPTED_WITH_LIMITS: artifactsbe315aff047b0d73/test4b6223acef58869e/sync3dae368d7d2c82b8;2sheet lazy/writer chung/3read routes+UI hồ sơ nguồn. Copy đủ basis/unknown giữ/link reader chặn/Pcn identity recheck/closure trước opener; HANDOFF đầu giữ evidence/limits.
- C-01 WITH_LIMITS: docsVIe05b7959154fbcf5/ENe59001cdfd3c0750/test367c252fb58298ce; grant đúng mẫu/bytes/index/baseline inventory/junction có probe;4HTML đồng bộ. README user96585b2a giữ, chưa renderGitHub.
- Repo chưa có profile maintainer thật (cố ý): `execution_profile.py status` ở repo báo PROFILE_ABSENT + dòng PROJECT còn văn xuôi cũ (LEGACY). PROJECT.md/en/PROJECT.md thật không sửa.
- Giữ nguyên: schema a550fcdb358a8df4/template 0c6510ae64d3304f; actual PROJECTs/CVF/transaction/pins/MANIFEST/READMEuser/binarytemplate/init. Library/sync có delta B-01/B-02 đã review; không .claude/profile/receipt maintainer hoặc _INDEX thật; dirty, chưa stage/commit/push.

## Open items

- A-09 capture nội bộ đúngbytes cho validate/plan/hash/backups. Config gắn toàn hash PROJECT chỉ đọc; bất kỳ dòng đổi làm token cũ PLAN_CHANGED, preview lại. Chấp nhận bảo thủ, không thêm permissionline projection; chưa kernel-race/atomic2file proof.
- Mọi giao dịch dở (không riêng owner path) chặn luồng profile; ghi PROJECT+profile là nhóm có phục hồi, không nguyên tử. Symlink file thật chưa đo (WinError1314), chỉ junction runtime đã đo.
- Upgrade bằng script cũ trong project không bootstrap profile; chạy lại bằng script mới. A-06/A-07 giữ giới hạn cũ; D4 chỉ bản lab6ee4cef2, không duyệt phát hành.
- A-10 core có3vai/preset candidate/retire đã review. Proof lab chỉ capability/model/locator: còn1finding diễn đạt nhỏ candidate dòng21, giữ CANDIDATE/chưa user acceptance; telemetry0.38191935USD không hóa đơn. Không nhận model quality/fullR4/enforcement.
- Adapter status vẫn NOT_INSPECTED cho host: receipt không chứng minh invocation. Proof riêng đã quan sát model/Read, chưa sandbox/tools enforcement. Native+receipt có journal nhưng không nguyên tử, còn TOCTOU cuối; parser identity subset/nested unknown từ chối.
- Candidate chỉ claim Windows26200/NTFS/Python3.11.9/jsonschema4.23.0/openpyxl3.1.5 đã đo. Gitclean/CI/official release còn chờ; Office output mới chưa visual QA.

## Waiting on user

- Không chờ người thử hoặc xin lại quyền E07-B đã cấp. Quyền gồm stage/commit phần bảo trì LAW hiện tại trong repo và dựng RC nội bộ1.9.0 để nghiệm thu trên bản sao.
- Chưa cấp push/official-release/CI network/host-global-admin/CVF cha; không mở rộng Git hoặc quyền profile. Worker Claude vẫn do operator giao/chọn model-effort; Codex điều phối/review.

## Decisions

- Operator amendment0.10: MVP trước/feedback sau; C-02/T37–T38 và phần người thật R6/T36/T48 chuyển sau MVP, không thành PASS. Giữ gate bảo toàn/quyền/nâng cấp/package/release; không mở thêm feature.
- A-09 diagnostic đã NOT_INSPECTED, không phủ định host chưa kiểm; authority_usable=False/profile_refUNSUPPORTED giữ. LEGACY cho xuất native nếu profile hợp lệ/owner nhất quán/lựa chọn rõ, không migrate hoặc suy quyền dispatch.
- A-10 một host/ba core role; factory candidate Haiku5.5/Sonnet5.5/Sonnet5.5 effortnull, không autofill profile. Effort/tier/fallback/limits chưa map UNSUPPORTED, không thêm vòng đo effort. Write không cưỡng chế new-only/path sandbox.
- Retire đã đo: một Windows no-replace rename→fixedinactive, receipt giữ/post-reconcile; RETIRE_CONFLICT chặn apply, không autoactivate/livecancel. Reviewer product không mang quyền sửa nhỏ maintainer; candidate_presets khác product_presets.
- A-11: current TASK/RESULT dùng v3 khi cần; so binding hiện hành và bytes thật trước writer. Publish task riêng bind raw TASK/RESULT/candidate/source/sổ đã dùng; staged lấy chính candidate bytes đã so hash. Một writer, không generic PASS/authority/acceptance hoặc native sandbox.
- Dòng PROJECT trống/placeholder bootstrap owner PROJECT không grant; mẫu sạch dùng con trỏ + owner PROFILE. Không tạo/migrate profile maintainer.
- B-02: version/quan hệ cùng sổ, không ContentID/engine/receipt/current-pointer mới. Mở cũ khác dùng mới: prepare kiểm closure/giữ unknown+inference+limits; stale sau publish từ chối register. x14 PARKED; không refresh pin/MANIFEST/RC3.

## Next milestone

Claude thi công E07-B theo roadmap0.11: kiểm scope Git, commit nguồn/metadata trước build, gate RC thật không skip/nested, giữ timeout900s; nghiệm thu verify/project/UI/upgrade/restore và ghi artifact/log/hash. Codex review RC sau bàn giao. Không tự clean/reset/amend/đổi gate hoặc dùng mock để tuyên bố usability.
