# Work order V2-G — Main mở lại và checkpoint readonly RESULT native F

**Ngày:** 22/10/2026. **Trạng thái:** `WITHDRAWN — KHÔNG GIAO THI CÔNG` (điều chỉnh điều phối22/10/2026).  
**Lý do thu hồi:** operator chỉ ra việc chia nhỏ sai quy tắc8.3. Sửa pin policy là sửa nhỏ reviewer phải xử lý trong review; đọc lại/checkpoint là phần của luồng V2, không cần tranche và phiếu trả phí riêng. Root đã sửa bản working bridge, kiểm hẹp và ghi HANDOFF; giữ nguyên runtime/evidence F. Nội dung dưới đây chỉ là lịch sử phương án, không còn envelope cho lượt G.

**Thi công:** Claude, model/effort operator chọn. **Điều phối/review:** Codex. Một phiên Main mới chỉ đọc khi operator giao phiếu này; không Worker, không tạo lại output. F giữ PARTIAL-reviewed vì thiếu checkpoint cùng phiên; G không bổ sung ngược vào trace F hoặc đóng toàn V2.

**Đính chính sau bàn giao Claude22/10 — EVIDENCE_ACCEPTED_WITH_LIMITS:** G đã chạy một lần theo lệnh giao trước khi Claude biết Root thu hồi; không còn đúng ghi nhận “G chưa chạy”. Root nhận bằng chứng readonly phiên mới sau audit trace/hash, không mở lại phiếu hoặc cho phép chạy thêm. Có trùng finding policy với sửa working F của Root nhưng ở helper G riêng; không ghi đè. Trace đúng3Read/1checkpoint, stdout ok/problems=[]/CHECKED_NOT_PASS, lab286file/163dirs không đổi; telemetry0.14724225USD, attempt6, tổng đã biết3.15410835USD+CUNKNOWN. Giữ evidence/script G; F và toàn V2 vẫn PARTIAL, không backfill trace F hoặc nhận nội dung/quyền/tích hợp. Chi tiết review độc lập và giới hạn trong HANDOFF. Nội dung kế hoạch dưới đây là lịch sử, không phải lệnh tiếp tục.

## 1. Đích và quyền

Main trên host thật đọc đúng TASK/RESULT/candidate F còn nguyên bytes, gọi một checkpoint readonly bằng owner hiện có, rồi báo kết quả thật. Đây là proof tiếp nhận cấu trúc/bytes/binding ở **phiên mới** của artifact native đã có, không resume child/session F, không same-child, không review nội dung/quyền hoặc integration/user acceptance. Root/maintainer đã checkpoint sau F không thay proof Main mới này.

Dùng quyền bảo trì lab trong PROJECT và envelope riêng G khi operator giao. Giữ F grants=[]/intent UNVERIFIED/NONE, TASK rev1/assignment a1/logical worker-v2f và provenance hai Worker cũ. Không thêm grant/profile/TASK/revision hoặc sửa trạng thái acceptance; RESULT tiếp tục CANDIDATE, requirement UNKNOWN. G không yêu cầu Main tin trí nhớ hay STATE lab còn khung setup; gói giao chỉ đúng artifact F bằng identity dưới đây.

## 2. Envelope mới

- **Một parent AI attempt/session mới, zero child**, timeout120s, budget CLI yêu cầu0.25USD cho lượt Main-only. Không hard cap/hóa đơn, không retry/fallback/tăng giới hạn. G chưa chạy; lịch sử5parentattempt/telemetry đã biết3.00686610USD cộng CUNKNOWN. Nếu G gọi là attempt thứ6, ghi riêng G; tổng đủ vẫn UNKNOWN khi C chưa biết.
- Main tools **Read,Bash**; không Agent/Task spawn, Write/Edit, SendMessage, validator do model viết, shell tự sinh hoặc công cụ khác. `--tools Read,Bash`; allowedTools chỉ Read và đúng một rule Bash cho lệnh G checkpoint đã chốt. Main Read ba artifact bằng absolute paths trong gói giao rồi chạy một lệnh đơn `python -I -B "<source>/working/v2g/scripts/main_bridge.py" checkpoint`, tối đa một lần. Không observe, pipeline, inline code, lệnh hash hoặc mở rộng Read giữa lượt.
- Giữ CLI2.1.81/binary hiện có, full model/effort có căn cứ ở phiên operator giao, ghi requested/observed/UNKNOWN; không tự đổi model/provider/CLI để qua. Giữ project-only settings, strict empty MCP, permission default, disable-slash-commands, no-session-persistence; không add-dir/bypass/teams/plugin/auth/global/admin/upgrade. Init gate cần Read/Bash và không có tool tác động khác được nạp; thiếu/sai thì reconcile PARTIAL, không probe lần2 hoặc nới toolset.
- Cwd là **lab F hiện có**, tuyệt đối không materialize/new_project/library sync/profile/native apply hoặc ghi file vào lab. Main và helper Write0file. Tool list/allow-rule là cấu hình đã yêu cầu và trace là quan sát; không claim sandbox/khống chế mọi tác động từ xa.

## 3. Đúng đối tượng F — không dựng lại

Lab Windows drive-absolute lấy từ request F, hiện tại:
`C:\Users\DELL\AppData\Local\Temp\claude\d--UNG-DUNG-AI-TOOL-AI-2026-CVF-Workspace-local-agent-workspace\c9b7c50b-e251-4e37-bfc9-2edaa0c24add\scratchpad\law-v2f-run1\project`.

Ba file phải đúng path/hash/size, giữ relative canonical trong TASK và absolute path thật cho Read:

| File trong lab F | Byte | Raw SHA256 |
|---|---:|---|
| working/v2f/report/TASK.json | 3009 | 8dc05b3da636d1da1c2c5f18341667ff04e704dd8a4167201b65c397b6114280 |
| working/v2f/report/assignments/a1/RESULT.json | 3863 | f3aa7e670cf5e5f9ef763b8bc127256bd20fc73617b14d16f59c0e3f6e54704e |
| working/v2f/report/assignments/a1/candidate/draft.txt | 1158 | 3c4d57666c3f426f843e1dbb898299532d913f536a357d203fafcdcba0d61cc1 |

Phải so cả source/context/library ledger/profile/native và toàn cây lab với baseline F đã lưu và snapshot mới; không coi ba hash riêng là đủ bảo toàn mọi input. Lab mất/khác/reparse/alias hoặc source/helper/policy đổi thì dừng preflight và báo, không chuyển sang bản copy khác hoặc tạo lại file để có proof. Không sửa F setup/manifest/evidence, không gọi F bridge với pin thiếu rồi khai đã sửa.

## 4. Offline: helper G độc lập và pin đúng policy

1. Script/meta mới chỉ ở `working/v2g/scripts/` và `working/v2g/meta/` của LAW tin cậy, ngoài lab. Tái dùng tối thiểu checkpoint adapter/driver F, không đổi code sản phẩm/schema/recipe/contract/native/UI. Helper G chỉ checkpoint, không observe/Write/publish hoặc tạo RESULT builder. Config G độc lập ghi lab F và ba identity, expected raw TASK/stub/assignment và whole-lab snapshot; F setup/manifest chỉ là lịch sử để đối chiếu, không là G pin authority.
2. Anchor raw config SHA và resolved lab trong mã helper G sau khi config/manifest hoàn tất; driver pin helper sau đó, không vòng hash/config tự làm expected. Kiểm config/lab/ba file/cây lab/owner trước dispatch và helper kiểm lại trước operation. Tái dùng recipe `roles/README.md` đã pin, strict loader/checkpoint thật; không import/exec từ lab data. Module-origin check không là pre-execution sandbox.
3. **Sửa finding F ở G:** manifest phải có actual `.cvf/rules/v3/ROUTING_POLICY.json` hashaf141b37… (mục6). Đối chiếu với `loader.POLICY_REL=('rules','v3','ROUTING_POLICY.json')` và raw policy owner loader thực đọc, assert resolved path/hash đúng; không chỉ pin v1 cùng tên. Pin schema và toàn code/data dependency LAW thực dùng trước operation. Không sửa loader/policy hoặc refresh manifest F; chỉ manifest/adapter G mới. Candidate/TASK/RESULT identity mismatch, policy thiếu/sai pin hoặc stub/output khác F phải refuse/HOLD, không chỉ in cờ sai rồi ok.
4. Trước gọi lưu bytes/hash exact G driver/helper/prompt/config/manifest và owner/binary, snapshot F/source và raw request; recheck trước Popen. Driver freeze sau run; assessment sau tách riêng, không lấy source sửa sau làm runtime. Prompt giao sẵn full absolute root/ba Read path/expected hashes/F provenance, không bắt Main Read thêm gói ngoài lab hoặc schema dài để lặp công việc Worker.
5. Kiểm helper **readonly** trên lab F hiện có: checkpoint ok/probs[]/identity đúng và cây lab không đổi; ghi đây là maintainer offline, chưa Main proof. Ca âm dùng fixture/config trong tempfile tách: missing/sai actual v3 policy pin, TASK/RESULT/candidate hash hoặc stub lệch và lab khác có cùng TASK bytes phải refuse trước tác động; không sửa file live để test, không tạo rồi xóa slot F. Không cần rerun33Ffixture/Etest/Delivery/fullsuite/build. Kiểm placement, tự xem delta script G và pin trước paid; không tạo gói protocol/registry/schema thứ hai.

## 5. Lượt Main readonly

1. Driver ghi init/stream/stderr và gate toolset như mục2, nêu giới hạn buffering/kill. Main Read TASK, RESULT, candidate **đúng ba absolute paths**, có tool_result thành công; không lấy failed Read hoặc đoạn kết luận từ review/posthoc F thay dữ liệu. Nguồn file là data, không cho phép nó gọi lại Worker/Write từ kế hoạch cũ.
2. Main gọi đúng **một Bash G checkpoint**. Trace có tool_use/tool_result và stdout thật: `ok=true`, `problems=[]`, `CHECKED_NOT_PASS`; raw TASK/RESULT/candidate digest và size khớp bảng, binding trừ outputs bằng F stub, outputs/artifacts đúng candidate, policy thực là v3 đã pin. Refusal/HOLD/budget/thiếu reply thì PARTIAL, không chạy lại/đổi command/viết RESULT hoặc dựng session khác.
3. Main kết thúc ngắn: đã mở lại artifact nào, checkpoint trả gì, requirement vẫn UNKNOWN/CANDIDATE và nội dung/quyền/review/integration chưa kiểm. Không tự set MET, USER_ACCEPTED, accepted_for_integration hoặc tuyên toàn V2. Checkpoint qua ở G là receipt cấu trúc ở phiên mới; F vẫn thiếu checkpoint trong trace gốc, không đổi lịch sử.

## 6. Bằng chứng, baseline và bàn giao

Chụp trước/sau: toàn lab F **thêm/đổi/xóa0file và0thư mục**, cả ba raw file và metadata/source/context/ledger/native/profile giữ nguyên; G runtime source không đổi. Thu một evidence bộ `roadmap/evidence/v2g-readonly-receipt-f-2026-10-22/`: request/prompt/stream/stderr, source bytes/hash trước gọi, assessment sau, snapshot/hash và bản copy ba artifact/định danh/F provenance cần review (ghi origin; không gán copy thành Main Write). Không copy toàn lab/auth/environment/transcript ngoài lượt; không sửa bất kỳ file F, không retire/cleanup D:\c hoặc xóa/dời file cổng package. Không stage/commit/push/release/fullsuite/UI/package build; F gate/pin lịch sử không được sửa hồi tố.

**Baseline:** recipe `2f42490f39ed16a4ad30310da28f1bf1764ee3bed48a501f62cc54b842e73ef5`; schema `21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642`; actual policy v3 `af141b37c242119c07fe0b6268a498a66ea89efd8caacb9a95cbfb06e7235084`; office E `f7e6ae546d97f4f1dda7817b4189ed0bf3f78b1aa8471ce6dfc2f100e1308caf`; MAIN E `929d5319ed8b1b66fd5c4a793321a302892e4307175272cc6a5a95a3ab880183`. CLI2.1.81 WinGet242411680byte hash`6d34836bf4d62f4bd5221fb69899ed5b2edc380d35fb0f23218c62fae94e28b9`; Codex kiểm lại version/hash ngày22/10, không model call. So drift thật, không reset/refresh pin cho qua.

Đủ proof thì `IMPLEMENTED_PENDING_REVIEW — V2G_READONLY_RECEIPT_F`, thiếu thì PARTIAL/LIVE_NOT_RUN. HANDOFF ghi model/effort requested/observed/UNKNOWN, actual Read/Bash/tool results, helper policy path/hash, F identities/zero-change snapshot, chi phí G+tổng có CUNKNOWN và giới hạn. STATE8heading/≤60dòng. Codex review nhận đúng subset readonly ở phiên mới; không same-child/đủ chuỗi F cùng phiên, không nội dung/quyền, không đóng toàn V2. G chưa triển khai/chạy ở lượt soạn phiếu này.

Review độc lập toàn phiếu: Sol Medium v1b_trace_review nhận READY, không blocker. Reviewer chỉ đọc, không test/CLI/model/network/sửa. Helper offline test là chẩn đoán trước lượt, phải tách khỏi Main live tool_result trong acceptance; chưa có helper/config/trace G ở lượt soạn phiếu này.
