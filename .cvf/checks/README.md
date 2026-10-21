# Checker và điểm nối dự kiến

Trạng thái: **G-02 REVIEW_ACCEPTED** trong phạm vi schema/routing/record consistency
(17/10/2026), code f95bfc367bb7f470,107 test G-02 đạt. `control_check.py` là
checker thuần chỉ đọc, so sánh record với nhau; **không phải gate, không cấp quyền, không
ngăn được Main**. Mọi kết quả có `effect_authorized=false`. Các mục acceptance bên dưới
vẫn là yêu cầu cho G-03, không phải điều G-02 đã chứng minh.

Main đã sửa ba nhóm P2 và output anchor, Reviewer độc lập đã nhận delta cuối. Full binding
vẫn nghiêm; scope coverage là projection riêng, không làm mất veto cùng binding.
Result artifacts phải khớp own binding.outputs trước khi summary được bỏ optional
metadata. Child basis đối chiếu inputs/provenance/revision với resolved task;
registered cần accepted role_name/class/group mapping. Peer digest echo không
xác minh task body, danh sách nhóm hợp cú pháp không cấp mapping cho identity.

## Đã triển khai ở G-02

- Gọi: `python .cvf/checks/control_check.py --phase {dispatch,effect,accept} [--format json|text] bundle.json`
  hoặc `control_check.check(bundle, phase)`. Chỉ đọc bundle và hai file canonical cố định
  cạnh script (schema, policy); không có `--schema/--policy/--trust-*`. Cần `jsonschema` >= 4.18
  (Draft 2020-12); thiếu thì kết quả UNSUPPORTED + `DEPENDENCY_MISSING`, không fallback.
- Exit: 0 PASS; 1 DENY/BLOCKED/UNSUPPORTED sau đánh giá dữ liệu (JSON/schema lỗi là DENY, không
  phải N/A); 2 lỗi tham số/khởi tạo/dependency; 3 NOT_APPLICABLE (hợp lệ nhưng không có object
  ở phase). Exit 3 không phải chấp thuận.
- Đối tượng: dispatch = từng action của task; effect = từng effect REQUEST; accept = từng result.
  Output `law.cvf.check/1`: `disposition`, `effect_authorized`, `reasons`, `routes`
  (matched/possible/claimed_by_main), `gates` (MET/UNMET/NOT_CHECKED/NOT_YET_DUE theo phase),
  `trusted_refs` (lời khai trong record và kết quả kiểm), `record_consistency`
  (CONSISTENT/INCONSISTENT, ADVISORY, chỉ là so sánh record) và `coverage`.
- Route: tự tính từ descriptor, điều kiện 3 trị (đúng/sai/không biết); hàng không biết vẫn được
  hợp yêu cầu và thêm R-UNCLASSIFIED. `NO_PROTECTED_TARGET` không bao giờ đúng từ lời khai
  zone/protected_targets, nên nháp trong grant báo CONSISTENT nhưng BLOCKED
  `PROTECTED_TARGET_UNDETERMINED` cho tới G-03. Lời khai "nhẹ" (recipe đã nhận, NONE, NONE_KNOWN)
  không hạ route; chỉ attestation của verifier mới làm được, mà production chưa có verifier.
- Verifier: mặc định không có (`NoVerifier`); `SimulatedVerifier` chỉ để test logic, kết quả bị
  chặn ở BLOCKED `SIMULATED_VERIFIER_NOT_AUTHORITY`. Gate quan sát (INPUT_REVISION, PRESERVATION,
  ACTUAL_OUTCOME, REQUIREMENTS) luôn NOT_CHECKED vì không đọc byte hay thao tác thật.
- Mã lý do thuộc kết quả checker (không phải enum `effect.reasons` G-01), lớp: RECORD (record
  mâu thuẫn), GATE (thiếu bước), AUTHORITY, OBSERVATION, SAFETY. Danh mục nằm ở
  `REASON_CLASS` trong `control_check.py`.
- Checker-owned ngoài policy: result luôn xét thêm gate REQUIREMENTS và ACTUAL_OUTCOME ở accept,
  Main đã nhận guard này trên căn cứ contract/Amendment A (không đổi policy G-01).
- Binding: full binding so cả object key (path, digest, source_id, revision, scope);
  result.artifacts phải khớp result.binding.outputs theo cùng key. Scope summary là
  projection path/digest, qualifier tường minh phải khớp; optional metadata thiếu không
  tự là stale khi full binding/output anchor đã khớp. Coverage thiếu không đủ nhận PASS.
  Review cùng binding mà không PASS luôn chặn, review ở binding khác chỉ là stale (ghi chú, không phủ
  quyết binding hiện hành). Delegation: parent pointer khớp effect binding (task, revision,
  accepted_task_digest, context_digest); child pointer phải khớp một review/effect/result thật
  sự bind task con trong bundle và inputs/provenance/revision khớp resolved task;
  thiếu thì NOT_CHECKED, mâu thuẫn thì BINDING_MISMATCH. Vì mọi
  task có ≥1 action, ủy quyền scope rỗng (ex19 context-only) chưa thể đạt MET: G-01 chưa có
  biểu diễn task context-only. Ghi nợ G-01, không giả action và không đổi schema ở G-02.
- Nhóm vai: core ⇒ envelope.role bằng role_name; domain_accepted ⇒ `domain_role`; registered ⇒
  scout/worker/reviewer/domain_role chỉ là các nhóm ứng viên, không tự cấp mapping.
  Registered cần verifier facts role_name/role_class/role_group đúng callee và envelope;
  mapping thiếu NOT_CHECKED, sai UNMET. Facts là đầu ra verifier/test-double, không nhận
  lời khai mapping từ record làm attestation. User/main/issuer/host/tool/unknown không hợp lệ.
- Giới hạn: không đọc/băm artifact; digest chỉ so giữa record; `canonical_bytes_verified=false`,
  `owner_protection=NOT_PROVEN`; không chứng minh path/link/envelope bị host chặn; CI phải cài
  jsonschema (bước Install dependencies) và chưa chạy remote; Python 3.8 chỉ kiểm cú pháp.
- Test/bằng chứng: `tests/test_control_check.py`; log, probe đột biến và bảng ví dụ ở
  `roadmap/evidence/g02-2026-10-17/` (kho nguồn).

## Phạm vi tối thiểu

Một entrypoint checker chung được ưu tiên nếu đủ; không dựng nhiều registry hay
workflow engine cho cùng contract. G-01 chốt đầu vào: `.cvf/contracts/control.schema.json`,
`.cvf/rules/ROUTING_POLICY.json` và kỳ vọng `.cvf/contracts/examples/EXPECTED.json`.
Entrypoint G-02 đã review nhận: `.cvf/checks/control_check.py`. Kiểm
schema là bước đầu, không thay kiểm binding/nguồn tin cậy/verdict.

Delegation luôn có đủ `tool_scope.tools`/`operations`/`paths`. Mảng rỗng là
không cấp quyền tương ứng, không phải wildcard; thiếu field là sai cấu trúc.
G-02 phải có ca context-only hợp lệ cấu trúc và ca child yêu cầu tool, thao tác
hoặc file vượt scope rỗng bị chặn. Quyền Main dùng native-subagent để dispatch
không là quyền tool của child. Kiểm cấu trúc đã chạy ở G-01, logic checker đã nhận
đúng phạm vi G-02; nợ biểu diễn task context-only của ex19 vẫn chưa giải quyết.

| Điểm kiểm | Đọc gì / chặn gì | Giới hạn |
|---|---|---|
| Trước dispatch/tác động | Schema, intent/grant binding, actual action/path trigger, input revision, acceptance/giới hạn, review cần thiết | Không xác minh toàn bộ ý nghĩa yêu cầu chỉ từ field có mặt |
| Trước nhận/tích hợp | Result/artifact thực, digest/revision, requirement→evidence, verdict và phạm vi, receipt còn hiệu lực | Bằng chứng tự khai phải giữ nhãn, không tự thành semantic PASS |
| Trước effect tại owner | Grant/actor/action/target, binding, preservation, repeat/expiry/envelope và điều kiện bắt buộc | Chỉ cưỡng chế khi điểm này không thể bị actor bỏ qua hoặc tự sửa |

Kết quả cần chỉ rõ object/phase/schema được xét, coverage và trạng thái:
PASS/DENY/BLOCKED/UNSUPPORTED/NOT_APPLICABLE. Không có đối tượng áp dụng trả
NOT_APPLICABLE, không báo PASS cho việc chưa kiểm. Checker chỉ đọc mặc định;
không cấp grant, sửa policy, gọi model hay thực thi tác động để làm xanh.

## Baseline quyết định trước code G-02 — 17/10/2026

- Reason codes là của output `law.cvf.check/1`, không mở enum effect của G-01.
- Chỉ kiểm record consistency; không đọc/băm bytes artifact. Coverage nêu rõ
  artifact bytes/actual operation chưa quan sát, digest chưa tái tính từ task.
  Mọi output G-02 có `effect_authorized=false`; consistency PASS ADVISORY không
  thay gate-readiness bị chặn do thiếu căn cứ an toàn. Không suy protected-target
  safety từ write_zone hoặc danh sách Main tự khai hẹp/rỗng; UNKNOWN chặn effect.
- Gate xét theo object/phase; field evidence kind hoặc verifier giả không biến
  current bytes, preservation, actual outcome thành đã quan sát. Gate bắt buộc
  chưa kiểm vẫn chặn. Không ép simulated positives thành terminal PASS.
- Child scope là giao grant và approved parent effect scope theo operation/tool/path;
  có source trong input/context không cấp write. Thiếu binding/scope thì chặn.
- CLI chuẩn dùng schema/policy canonical cố định, không arbitrary override.
  Test/diagnostic injection không chứng minh owner tin cậy, không mở effect.
- CI phải thực chạy dedicated G-02 tests với dependency tương thích ma trận;
  thiếu validator phải fail rõ, không silent skip. G-04 vẫn sở hữu dependency
  phân phối. Không tự cài dependency local để vượt lỗi.
- Exit: 0 PASS đúng phạm vi; 1 DENY/BLOCKED/UNSUPPORTED sau đánh giá; 2 lỗi dùng/
  khởi tạo/dependency (dependency thiếu output UNSUPPORTED/DEPENDENCY_MISSING);
  3 NOT_APPLICABLE chỉ khi validate thành công và không có object đúng phase.
  N/A không cấp quyền, không chứng minh checks bắt buộc đã đạt.

## Nối owner hiện có

- Rules/contracts: .cvf; không đưa nguồn CVF repo vào dependency runtime.
- Profile/quyền user: A-09, một owner .agent/EXECUTION_PROFILE.json; trust/issuer
  protection phải do host/OS/integration chứng minh, không do file vị trí quyết định.
- Task/result: A-11 thiết kế cùng G-01; không chờ adapter chạy rồi mới chốt contract.
- Writer: R2 transaction/library và các owner pack/install/export/upgrade liên quan;
  không tạo writer thứ hai. Bypass ngoài các owner phải thuộc host/OS proof G-03.
- Runtime receipt/cache: .agent/runtime/governance, theo rule loại khỏi manifest/ZIP
  hiện có; không tạo .cvf/runtime. Không bật watcher/daemon/network.
- Model/effort: giữ role config/profile owner; checker không tự chọn/nâng model.

## Ca phản chứng phải có khi triển khai

Main gọi việc là read-only nhưng operation ghi nguồn; Main thiếu/đổi grant; task
hoặc input/output đổi sau review; Reviewer BLOCKED nhưng Main thử tích hợp; nguồn/
skill tự cấp quyền; Main dùng file/shell/native bỏ writer; retry/late-result gây
lặp tác động; checker không có object; tình huống preservation đã biết bị mất.

Thêm hai phản chứng authority: Main thay user intent bằng bản tự viết và Main
tự khai reviewer hợp lệ dù các hash nội bộ khớp. Checker không thể tự chứng minh
nguồn quyền từ các field đó; G-01/G-03 phải giữ binding tới issuer/intent/reviewer
eligibility được xác nhận độc lập và không do Main tự tạo hoặc sửa.

Có cả luồng hợp lệ: nháp mới trong grant không xin lại user, model preference
trong grant được giữ, receipt hợp lệ được dùng lại đúng binding. G-03 báo rõ
đường nào bị chặn thật, đường nào chỉ phát hiện hoặc vẫn chưa đo.

G-04 phải nối init/adopt/upgrade/build/check: templates sạch, không sao chép grant/
log/source của project A, giữ lựa chọn riêng khi upgrade, schema lạ từ chối an toàn,
hướng dẫn VI/EN và support matrix đúng mức proof. Quy tắc này chưa được công cụ
đóng gói thực thi ở G-00; không phát hành cây source hiện tại như tính năng hoàn tất.
