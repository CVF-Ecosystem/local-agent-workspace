# Contract điều phối v2 — CANDIDATE_NOT_ACTIVE (G-01-C1)

Trạng thái: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED** (18/10/2026). Chỉ nhận candidate C1, chưa kích hoạt; checker G-02 v1 không đọc cây này.
Cơ sở đánh giá: workflow hợp tác có kiểm tra/review bắt buộc (operator nhận 18/10/2026). Mỗi version có một owner:
v1 (`../CONTROL_CONTRACT.md`, `../control.schema.json`) giữ nguyên; tài liệu này và `control.schema.json` cạnh nó là owner của
`law.cvf.control/2`. Biểu diễn cấu trúc: `control.schema.json`; ví dụ giả + kỳ vọng: `examples/`; vectors: `vectors.json`.
Không có grant, receipt, issuer hay quyền thật ở đây. Schema hợp lệ **không** là quyền, không là bằng chứng độc lập, không là chống giả.

## 1. Cơ sở đánh giá, version và những gì bị từ chối

| Literal | Giá trị | Ghi chú |
|---|---|---|
| `schema_version` | `law.cvf.control/2` | `const` ở mọi record |
| `policy_version` | `law.cvf.routing/2` | `const` ở binding, effect.routing, route_proposal |
| `evaluation_basis` | `COOPERATIVE_WORKFLOW` | bắt buộc ở mọi record và trong binding; do profile được nhận cố định, Main không chọn theo lần chạy |
| `bind_version` | `law.cvf.bind/2` | bắt buộc trong binding (mục 4) |
| `assurance_level` (effect) | `UNVERIFIED` \| `ADVISORY` | v2 không có `ENFORCED_FOR_NAMED_ACTIONS`; muốn nhãn đó phải có version và proof riêng |

Bị từ chối, không diễn giải, không chuyển đổi: version khác (kể cả v1), thiếu hoặc lạ `evaluation_basis`, binding không có `bind_version`,
record v1 trong bundle v2, receipt v1 dùng cho binding v2. Hệ quả cho C2: không có "tự nâng cấp" record cũ; project/profile thiếu cơ sở đánh giá giữ
hành vi v1 (dừng) cho tới khi profile/template/integration mới được nhận; Main không đổi cơ sở để vượt BLOCKED.

## 2. Nguồn tin: attribution thay cho trust_anchor/verification

v1 có `trust_anchor` và `verification.status=VERIFIED` do chính người ghi record viết ra. v2 bỏ cả hai và chỉ nêu **lời khai nguồn**, kèm kênh và người ghi:

| `source_class` | Nghĩa | Ràng buộc schema |
|---|---|---|
| `USER_CONFIRMATION` | lời hoặc xác nhận của chính user | `channel` ∈ `USER_MESSAGE`, `HOST_CONFIRMATION_UI`, `USER_AUTHORED_FILE`; bắt buộc `evidence_locator` |
| `MAIN_PROPOSAL` | đề xuất/diễn giải của Main | `channel` = `MAIN_AUTHORED` |
| `ROLE_REPORT` | báo cáo của Scout/Worker/Reviewer/vai miền | `channel` = `ROLE_OUTPUT`; `observed_by.role` là một vai |
| `TOOL_OBSERVATION` | đầu ra do tool/host quan sát | `channel` = `TOOL_OUTPUT`; `observed_by.role` ∈ `tool`, `host` |
| `UNVERIFIED` | không nêu cơ sở | — |

`channel = MAIN_AUTHORED` chỉ đi với `MAIN_PROPOSAL` hoặc `UNVERIFIED`: schema từ chối lời khai vừa có nguồn Main vừa mang lớp `USER_CONFIRMATION`.
Main được ghi lại xác nhận thật của user (`recorded_by.role = main`) với kênh và căn cứ nguồn tương ứng; schema không xác thực lời khai đó.
Nhưng đây là lời khai hợp tác, không chống giả: ai ghi được record thì ghi được `attribution`. Mục đích là (a) cho người và checker thấy lớp nguồn
được khai, (b) từ chối hàng routing cần lớp khác (`attributed_refs_required`, mục 6), (c) giữ phân biệt giữa user, Main, vai và tool.

Không suy: hash, locator, tên, `ref_id`, `issuer` hoặc việc nhiều record khớp nhau **không** nâng lớp nguồn và không tạo grant. Review không cấp quyền.
Worker/Scout/Reviewer chỉ đặt `CANDIDATE`; `USER_ACCEPTED` bắt buộc `user_acceptance_ref` có `attribution.source_class = USER_CONFIRMATION`.
Nguồn quyền thật là user trong phạm vi đã xác nhận; v2 không thêm issuer, helper, account, server hay bí mật.
Grant theo nhóm việc đã được user xác nhận được dùng lại trong phạm vi còn hiệu lực, không hỏi lại mỗi bản nháp và không yêu cầu user viết JSON.
User có thể chỉ định Reviewer ngoài host bằng xác nhận theo nhóm việc; tên model/host không thay bằng chứng lượt review và tư cách vai riêng.

## 3. Task, review, effect, result (giữ nghĩa v1, nêu phần đổi)

Giữ nguyên v1: nội dung tối thiểu của task (identity, intent, authority, inputs, effects, acceptance, envelope), review ở hai điểm (PRE_EFFECT khi risk yêu cầu,
PRE_INTEGRATION/PRE_DELIVERY khi policy yêu cầu), điều kiện trước tác động, nhận kết quả (REVIEW_PASSED, ACCEPTED_FOR_INTEGRATION, EFFECT_APPLIED,
USER_ACCEPTED là các ý nghĩa khác nhau), veto non-PASS cùng binding, timeout/retry phải reconcile, delegation (mục 5). Chỉ khác:

- Mọi chỗ v1 dùng `trusted_ref` nay là `attributed_ref` (`ref_id`, `kind`, `locator`, `revision?`, `digest`, `issuer?`, `attribution`).
- `reason_code` bỏ `TRUSTED_VERIFICATION_UNAVAILABLE`, `INTENT_NOT_TRUSTED`, `REVIEWER_ELIGIBILITY_UNTRUSTED`; thêm `USER_CONFIRMATION_MISSING`, `ATTRIBUTION_INSUFFICIENT`,
  `REVIEWER_NOT_ELIGIBLE`, `UNSUPPORTED_BINDING_PART`, `BASIS_MISMATCH`.
- Reviewer eligibility chỉ được nhận từ `USER_CONFIRMATION` (user chỉ định reviewer) hoặc `TOOL_OBSERVATION` (host/tool quan sát vai riêng). `ROLE_REPORT`
  và `independence_observed` = `SELF_DECLARED`/`NOT_OBSERVED`/`SAME_ACTOR` không đạt reviewer bắt buộc. Thiếu reviewer thì phần phụ thuộc chờ, không Main tự duyệt.
- Review/effect/result không có digest riêng: tham chiếu nhau bằng id và bằng `binding` (mục 4).
- Quy tắc cấu trúc còn giữ: PRE_EFFECT phải nêu `intent_refs_checked`; PASS cần ≥1 đối tượng; ACCEPTED_FOR_INTEGRATION cần mọi requirement bắt buộc MET.
- Ex19/context-only (task chỉ context, `actions` minItems 1) vẫn là nợ biểu diễn của G-01: v2 không thêm action giả và không có ví dụ cho luồng đó.

## 4. Binding `law.cvf.bind/2`

**Nguyên tắc.** Digest chỉ nhận dạng *bytes đã định nghĩa*; nó không chứng minh nguồn gốc, quyền hay tính đúng. Hai digest tự khai trùng nhau trong hai record **không**
là đã kiểm bytes: chỉ công cụ đọc bytes hoặc projection thật mới thiết lập được điều đó (C2). Phần chưa định nghĩa dưới đây là **UNSUPPORTED**: phần phụ thuộc bị chặn
(`UNSUPPORTED_BINDING_PART`), không tự đoán, không thay bằng hash request thô.

### 4.1 Canonical JSON `LAW-CJ/2`

Đầu vào là giá trị JSON đã parse từ văn bản **không có khóa trùng**. Kết quả là byte UTF-8 (không BOM):

- object: khóa sắp tăng dần theo byte UTF-8; khóa phải khớp `^[A-Za-z0-9_.-]{1,64}$`; `{"k":v,...}` không khoảng trắng;
- array: giữ thứ tự (ngoại lệ "set" ở 4.3); `[a,b]` không khoảng trắng;
- chuỗi: phải ở dạng NFC; ký tự ghi thô UTF-8; chỉ escape `\"` `\\` `\b` `\t` `\n` `\f` `\r` và các ký tự U+0000–U+001F còn lại dạng `\u00xx` chữ thường; U+007F, U+2028… ghi thô; `/` không escape;
- số: chỉ số nguyên thập phân trong ±(2^53−1), không `+`, không số 0 đứng đầu; `true` `false` `null`;
- vắng ≠ `null`: trường tùy chọn vắng thì bỏ khỏi projection; mảng rỗng và object rỗng vẫn ghi.

Từ chối (UNSUPPORTED, không chuẩn hóa hộ): số có phần thập phân/mũ (kể cả `1.0`, `1e3`), số ngoài khoảng, chuỗi không NFC, surrogate đơn, khóa trùng, khóa sai mẫu, `NaN`/`Infinity`.
`digest = "sha256:" + hex(SHA-256(bytes))`.

### 4.2 Projection (cái gì được băm)

Mỗi projection là object có `bind` = `law.cvf.bind/2` và `part`. `ref_proj` = `{digest, kind, revision?}`; `obj_proj` = object_digest đầy đủ (`path`, `digest`, `source_id?`, `revision?`, `scope?`).

| Trường binding | Băm cái gì | Loại trừ / trường tự tham chiếu |
|---|---|---|
| `intent_digest` | `{part:intent, refs: set(ref_proj của task.intent.refs)}` | `ref_id`, `locator`, `issuer`, `attribution`, `main_interpretation`, `unconfirmed` |
| `accepted_task_digest` | `{part:task, schema_version, evaluation_basis, work_id, task_id, task_revision, intent_digest, main_interpretation, unconfirmed?, subject{actor_id,role}, grant_refs:set(ref_proj), inputs:set(obj_proj), effects{actions:[action_proj], protected_targets?:set, preservation?, expected_outputs?:set, on_missing}, acceptance, envelope}` | `record_type`, `note`, `example_only`, `proposed_by`, `route_proposal`, `context_refs` (có `context_digest` riêng), `authority.subject.host/session_ref`, attribution/locator/ref_id của grant_refs; trong action: `delegation.parent_task` (tự tham chiếu task chứa nó) |
| `context_digest` | `{part:context, context_refs: set(obj_proj)}` | chỉ phần *khai báo* trong `context_refs`; không phải thứ role thực sự thấy |
| `action_digest` | `{part:action, action: action_proj}` | như trên; `payload`→obj_proj, `recipe.acceptance_ref` và `delegation.callee.identity_ref`→ref_proj |
| `policy_digest` | `{part:policy, policy: toàn bộ object policy đã parse}` | không băm bytes file nên không phụ thuộc xuống dòng; đổi nội dung policy là đổi digest |
| `object_digest.digest` (inputs/outputs/artifacts) | SHA-256 **bytes file nguyên văn** tại `path` | không chuẩn hóa xuống dòng/BOM/Unicode/định dạng; CRLF ≠ LF |

Task không chứa chính digest của nó (digest xuất hiện ở binding/pointer của record khác), nên không có trường tự tham chiếu ngoài `delegation.parent_task`
đã loại ở trên; pointer cha được so riêng với binding của effect.

**Các kiểm tra độc lập với digest — C2 bắt buộc thực hiện tại mỗi phase áp dụng.** Digest bằng nhau không giữ nguyên quyền hoặc tư cách từ lượt trước.
Không dùng các trường đã loại khỏi projection để ngầm mở quyền mới.

| Phần không được hash thay thế | Kiểm tra hiện hành |
|---|---|
| `ref_id`, `locator`, `issuer`, `attribution` | Resolve tham chiếu hiện tại, từ chối thiếu/trùng/mâu thuẫn; đối chiếu nội dung/digest theo loại nguồn, revision, lớp nguồn, kênh và căn cứ được yêu cầu. Không thực thi locator hoặc dùng tên/issuer làm quyền. Thiếu căn cứ bắt buộc thì BLOCKED, không nhận chỉ vì digest cũ khớp. |
| Grant, actor, reviewer eligibility | Tại dispatch/effect/accept khi áp dụng, kiểm grant đang hoạt động, subject, scope, tool, envelope và lớp nguồn; kiểm Reviewer khác actor/context có căn cứ hợp tác, đúng pha/phạm vi/verdict. Không thừa kế một kết quả kiểm quyền cũ qua hash. |
| `authority.subject.host/session_ref` | Metadata quan sát danh tính, không tự là điều kiện cấp quyền. Nếu có ràng buộc host/session tường minh, nó phải nằm trong envelope/profile constraint đã được binding bao phủ; chưa biểu diễn/kiểm được thì chặn phần phụ thuộc, không coi review cũ đã phủ constraint mới ngoài hash. |
| `context_refs` | Luôn tính và so `context_digest` riêng khi binding yêu cầu; accepted-task digest bằng nhau không thay kiểm context. Không suy prompt/lịch sử thực từ context khai báo. |
| `delegation.parent_task` | So riêng pointer đầy đủ với binding effect và task cha đã resolve; kiểm task con, scope và envelope theo mục 5. Không cho vòng tự tham chiếu bỏ qua đối chiếu. |

Các kiểm tra này không đổi projection hoặc tạo gốc tin cậy mới. C2 phải công bố phần đã quan sát, phần chỉ là lời khai và phần chưa kiểm.

### 4.3 Trường "set"

Các mảng sau được sắp theo byte canonical của từng phần tử trước khi băm và không được trùng (trùng ⇒ UNSUPPORTED): `refs`, `grant_refs`, `inputs`, `context_refs`,
`protected_targets`, `expected_outputs`, `targets`, `content_use`, `tool_scope.tools|operations|paths`. Mọi mảng khác có thứ tự có nghĩa (`actions`, `requirements`, `preservation`, `expected_evidence`…).

### 4.4 Vectors và kiểm

`vectors.json`: 20 vector canonical (9 hợp lệ, 11 UNSUPPORTED có lý do), 4 vector bytes (rỗng, LF, CRLF, BOM), một fixture task cho intent/context/action/task, digest policy
của `../../rules/v2/ROUTING_POLICY.json`, và danh sách UNSUPPORTED. `tests/test_control_v2_candidate.py` tính lại tất cả bằng hàm tham chiếu; digest của chuỗi canonical nhỏ đã đối chiếu bằng `sha256sum`.
Binding trong mọi ví dụ được tính từ record, không phải nhãn giả; ví dụ cố ý sai (`ex08`) ghi `binding_stale_or_mismatched = true`. Hàm tham chiếu là bằng chứng
định nghĩa tự nhất quán, **không** phải loader hay checker và không được hệ thống nào gọi.

### 4.5 UNSUPPORTED (C2 phải chặn phần phụ thuộc, không đoán)

| Phần | Lý do |
|---|---|
| tương đương alias đường dẫn | `path` so như chuỗi; hoa/thường, dấu phân cách, `..`, 8.3, dấu chấm cuối, ADS, UNC, link không được coi là bằng nhau; khác chuỗi là `BINDING_MISMATCH` |
| đối tượng không phải file | thư mục, link, placeholder đám mây, thiết bị chưa có định nghĩa bytes (`ex14`) |
| ngữ cảnh thực role thấy | không có điểm quan sát cho prompt/lịch sử/đầu ra tool; chỉ `context_refs` khai báo |
| digest của review/effect/result | không định nghĩa; chỉ tham chiếu bằng id và binding |
| so sánh với digest v1 | v1 không có định nghĩa đầu vào |
| thời gian/hết hạn | nguồn đồng hồ và cách xét chưa được C1 định nghĩa |
| tính xác thực của attribution | cooperative, xem mục 2 |
| bằng nhau về ngữ nghĩa giữa các định dạng | khác bytes là khác đối tượng |

**Khi nào chặn:** `BLOCK_DEPENDENT_GATE` áp dụng khi một gate hiện hành thực sự cần phần chưa hỗ trợ, không biến mọi giới hạn assurance thành yêu cầu xác thực mạnh.

| Giới hạn | Áp dụng cho COOPERATIVE_WORKFLOW |
|---|---|
| Tính xác thực attribution | Là giới hạn assurance không được chứng minh; không tự tạo gate xác thực mật mã cho mọi xác nhận hợp tác. Vẫn phải kiểm lớp nguồn/kênh/căn cứ/resolve hiện tại ở mục 2 và 4.2; thiếu hoặc mâu thuẫn thì chặn. Nếu yêu cầu riêng đòi chứng minh xác thực mạnh thì phần đó UNSUPPORTED/BLOCKED. |
| Ngữ cảnh thực role thấy | Context khai báo vẫn phải khớp. Review độc lập thông thường vẫn cần căn cứ hợp tác về Reviewer riêng và context riêng; không miễn review. Gate đòi proof chính xác prompt/lịch sử thực mà không quan sát được thì UNSUPPORTED/BLOCKED. |
| Thời gian/hết hạn | Không tự tạo hạn cho grant không có ràng buộc thời gian. Có expires/deadline hoặc gate yêu cầu đánh giá thời gian thì phần phụ thuộc UNSUPPORTED/BLOCKED cho tới khi có định nghĩa được nhận. |
| Các phần còn lại | Gate cần bytes của đối tượng chưa hỗ trợ, digest chưa định nghĩa hoặc so sánh chưa định nghĩa vẫn bị chặn. Dùng id + binding đã định nghĩa cho review/effect/result không đòi digest riêng của các record đó. |

## 5. Delegation

Như v1: `subject` của grant là người giữ quyền, `delegate_callees` là vai được gọi; vai được gọi là `callee_role` (core scout/worker/reviewer, hoặc registered/domain_accepted
kèm `identity_ref` kind `role_acceptance`, khai bằng attribution). Lời gọi mang task cha/con, `tool_scope` đủ ba mảng (rỗng = không cấp quyền, không phải wildcard) và `requested_envelope`;
phạm vi con phải nằm trong grant và task cha (so sánh thuộc C2). Quyền Main dùng native-subagent để dispatch không là quyền tool của con. `parent_task` trong action của task
nằm ngoài `accepted_task_digest` (mục 4.2); pointer ở effect phải khớp binding của effect.

## 6. Policy và hàng routing

`../../rules/v2/ROUTING_POLICY.json` (`law.cvf.routing/2`, status `CANDIDATE_NOT_ACTIVE`) giữ nguyên chín row ID, `match_any`, `required_gates`, `required_review_phases`,
`forced_disposition`, hợp nhiều hàng, `main_may_downgrade=false`, `unknown_handling=NEVER_ALLOW`. Chỉ đổi trường quyền: `trusted_refs_required` thành `attributed_refs_required`
= danh sách {`kind`, `accepted_source_classes`}; bản đọc ở `../../rules/v2/CONTROL_RULES.md`. Thêm hằng: `assurance_ceiling=ADVISORY`, `tamper_resistance=NONE`,
`basis_change_per_run=FORBIDDEN`, `legacy_and_unknown_handling=REFUSE_NO_AUTO_MIGRATION`, `binding_definition=law.cvf.bind/2`, `unsupported_binding_part_handling=BLOCK_DEPENDENT_GATE`.

## 7. Phạm vi của candidate này

Đã làm ở C1: định nghĩa cấu trúc, attribution, binding + vectors, policy, ví dụ giả (22 bundle: 13 hợp lệ cấu trúc, 9 bị schema từ chối) và kiểm schema/vectors.
**Chưa làm và không được suy ra:** loader/checker đọc v2 (C2), coverage/basis/compatibility, activation plan, migration, profile/template/AGENTS, receipt thật, bằng chứng workflow
(`workflow_status: NOT_RUN`), host/native enforcement, sửa x14/race của writer. Mọi `expected_design` trong `examples/EXPECTED.json` là kỳ vọng tình huống giả định cho C2, chưa chạy; không là verdict của bundle nguyên trạng có grant EXAMPLE_INACTIVE.
