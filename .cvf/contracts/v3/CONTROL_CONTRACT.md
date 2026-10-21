# Contract điều phối v3 — CANDIDATE_NOT_ACTIVE (A0 hẹp, G-02-C2)

Trạng thái: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED / CANDIDATE_NOT_ACTIVE** (18/10/2026). Chỉ là candidate cho **một action `create_new` do owner protocol P-CN1 publish, trên Windows NTFS local**.
Entry v3 hỗ trợ luồng hẹp `P_CN1_ONE_FILE` khi có root tường minh: binding, routing, gates, observer, receipt và kiểm tính nhất quán D4 theo mục 11; không root giữ `BINDING_ROUTING_ONLY`. I1/P-CTX1, I2 navigation và I3 package/lifecycle đã review nhận WITH_LIMITS; G-03/G-04 tổng thể vẫn PARTIAL, chưa activation.
Bản phân phối chọn v3 tường minh; v1 và v2 giữ ở kho nguồn. Candidate không là policy thứ hai cùng có hiệu lực, không tạo grant hoặc quyền vượt BLOCKED; mức bảo đảm toàn host vẫn ADVISORY.
Tài liệu này và `control.schema.json` cạnh nó là owner của `law.cvf.control/3`. Ví dụ giả + kỳ vọng và vectors chỉ có trong kho nguồn (không có trong bản phân phối); policy: `../../rules/v3/ROUTING_POLICY.json`;
bản đọc: `../../rules/v3/CONTROL_RULES.md`. Không có grant, receipt, issuer hay quyền thật ở đây. Schema hợp lệ **không** là quyền, không là bằng chứng độc lập, không là chống giả.

Nguồn thiết kế (kho bảo trì, không có trong bản phân phối): roadmap/G02_C2_S3_D0_AMENDMENT_PACKET_2026-10-18.md, mục 4.3.3 (API/evidence P-CN1) và bảng 5.4 (phần dùng/hoãn).
Owner thi công: `tools/publish_new.py`, SHA256 đầy đủ `8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852` (revision corrective 18/10/2026, **REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS**; pin đã nhận trước đó `f2b1b425690eacd5…` không còn là pin hiện hành và bằng chứng/receipt mang pin cũ không tự được diễn giải theo revision này, không auto-migrate).
Revision corrective giữ wire `publish-v1`/P-CN1 version 1 và hình evidence (không thêm trường): API `publish(project_root, request, staged, *, request_id=None)` và CLI `publish --rid`; `request_id` do người gọi chọn (đúng 32 hex thường) làm `task_id = pcn1-<rid>`, không đưa vào JSON request; không truyền thì tự sinh UUID như cũ. Rid không hợp lệ ⇒ REFUSED `REQUEST_ID_INVALID`; rid đã có bất kỳ file nào dưới thư mục publish (prepared, terminal hoặc staged mồ côi) ⇒ REFUSED `RID_TAKEN`, không ghi đè hay xóa. Precondition mới: `.agent` và `.agent/runtime` phải có sẵn là thư mục thường, không link, được pin trước mutation; thiếu ⇒ REFUSED `RUNTIME_PARENT_MISSING`, owner chỉ tạo thư mục `publish` (T2) dưới runtime đang pin. Hai thư mục cha do init/transaction hiện có tạo khi thiết lập package project (probe init giả đã đạt); G-04 còn phải kiểm hành trình new/adopt/upgrade đầy đủ, không thêm bootstrap helper chỉ để đáp ứng precondition.

## 1. Cơ sở đánh giá, version và những gì bị từ chối

| Literal | Giá trị | Ghi chú |
|---|---|---|
| `schema_version` | `law.cvf.control/3` | `const` ở mọi record |
| `policy_version` | `law.cvf.routing/3` | `const` ở binding, effect.routing, route_proposal |
| `evaluation_basis` | `COOPERATIVE_WORKFLOW` | không đổi so với v2; bắt buộc ở mọi record và trong binding |
| `bind_version` | `law.cvf.bind/3` | digest của bind/2 và bind/3 **không bao giờ** so sánh được; không migrate receipt v2 |
| `check_version` | `law.cvf.check/3` | output checker cho phạm vi được hỗ trợ ở mục 11 |
| `assurance_level` (effect) | `UNVERIFIED` \| `ADVISORY` | không có `ENFORCED_*` |

Bị từ chối, không diễn giải, không chuyển đổi: version khác (v1, v2), thiếu hoặc lạ `evaluation_basis`, binding không có `bind_version`, record v2 trong bundle v3, receipt/binding v2 dùng cho v3.
Không có "tự nâng cấp". Grant v3 do user xác nhận lại theo nhóm việc; không dùng grant ví dụ.

## 2. Nguồn tin: attribution

Giữ nguyên v2: `source_class` ∈ `USER_CONFIRMATION`, `MAIN_PROPOSAL`, `ROLE_REPORT`, `TOOL_OBSERVATION`, `UNVERIFIED`; `channel` đi cùng theo schema (`MAIN_AUTHORED` chỉ với `MAIN_PROPOSAL`/`UNVERIFIED`,
`USER_CONFIRMATION` bắt buộc `evidence_locator`). Mọi attribution là lời khai hợp tác, không chống giả: hash, locator, tên, `issuer` hay nhiều record khớp nhau không nâng lớp nguồn và không tạo grant.
Review không cấp quyền. Thêm ở v3 (chỉ cho nghiệm thu D4, mục 8): `result.user_acceptance.ref` phải là `USER_CONFIRMATION` với kênh `USER_MESSAGE` hoặc `HOST_CONFIRMATION_UI`;
`USER_AUTHORED_FILE` **không** đủ vì file đó agent ghi được.

## 3. Phần dùng và phần hoãn (bảng 5.4 của packet)

| Δ | Nội dung | Trong v3 candidate |
|---|---|---|
| Δ01–Δ02 | vùng ghi, `light_write_zones`, `NO_PROTECTED_TARGET` | **Dùng phần cần:** thêm đúng một vùng `agent_runtime`; policy có `zone_map` (3 tiền tố), `write_zone_rank`, `light_write_zones`, `authority_name_patterns`, `unmapped_path_handling = UNCLASSIFIED`. `agent_state`, `package_content`, `overlay_rules` hoãn |
| Δ03 | tách R-READ_DRAFT | **Dùng:** ba mệnh đề (A) `read`/`none`, (B) `create_new`/`working`, (C) `create_new`/`output_new` + `CONTENT_USE_INTERNAL_ONLY`; (B),(C) kèm `NO_PROTECTED_TARGET` |
| Δ04 | R-MUTATION cho `create_new` ở vùng không nhẹ | **Dùng một mệnh đề:** `create_new` ở `agent_runtime` (nhánh ghi runtime trực tiếp). Các vùng khác hoãn |
| Δ05 | R-AUTHORITY_CHANGE cho `create_new` ở `framework` | **Hoãn:** tên khớp mẫu authority nâng đích lên `framework`, nhưng không có hàng nào khớp ⇒ R-UNCLASSIFIED ⇒ BLOCKED |
| Δ06 | `CONTENT_USE_INTERNAL_ONLY` | **Dùng** |
| Δ07, Δ14 | overlay | **Hoãn:** không có record `protection_overlay`, không có `overlay_digest` |
| Δ08 | bỏ `action_digest` khỏi review/result | **Hoãn:** một action giữ `action_digest` |
| Δ09–Δ10 | scope review có tag, kết luận từng yêu cầu | **Hoãn:** review giữ cấu trúc v2; luồng hẹp không có pha review |
| Δ11 | `result.user_acceptance` đủ D4 | **Dùng** (mục 8) |
| Δ12 | `role` của artifact | **Dùng chỉ `ACTUAL_BYTES`**; `STAGED_BYTES`/`relation` hoãn |
| Δ13 | mã lý do | **Dùng:** thêm vào enum `reason_code`: `INPUT_CHANGED_SINCE_READ`, `PRECONDITION_PROOF_MISSING`, `CHANGED_AFTER_PUBLISH`, `REVIEW_REQUIRED_UNSUPPORTED`. `USER_ACCEPTANCE_INCOMPLETE`, `USER_ACCEPTANCE_STALE` và các mã khác của packet 4.8 là mã do checker sở hữu, ngoài enum, chưa có checker |
| Δ17 | `completion`, `action_index`, `extra_review_phases`, occurrence | **Hoãn:** schema từ chối các trường này |
| `effect.receipt_ref` | kind `effect_receipt` | **Dùng**, chỉ ở effect `OUTCOME` |
| `owner_protocols` | M-2: protocol, entrypoint, envelope T1–T7 | **Dùng** (mục 6) |
| `operational_context_protocol` | I-01.1: P-CTX1, cập nhật ghi chú vận hành STATE/HANDOFF có sẵn | **Chỉ khai báo** (mục 6.1); checker, workflow và observer không đánh giá |

Ngoài phạm vi, giữ BLOCKED/UNSUPPORTED: `overwrite` và input là target, sổ/provenance (x14/race), recipe, vai không-core, ex19 (task chỉ context), gửi ngoài, POSIX/mạng/cloud/FAT/exFAT,
sinh DOCX hay kiểm định dạng, enforcement của host, dependency model giảm veto (R-8), và **mọi task có pha review bắt buộc** (chưa hỗ trợ trong luồng hẹp; không lặng bỏ review để nhận nháp).

## 4. Vùng ghi, điều kiện nhẹ và giả định mở

Tập ghi của action = `targets` nếu `operation` ≠ `read`/`delegate`, ngược lại rỗng. Vùng hiệu lực của một đường dẫn = hạng cao nhất trong các nguồn **đã phân loại** áp dụng
(`zone_map` theo tiền tố dài nhất, vùng khai của action — chỉ nâng, `authority_name_patterns` ⇒ `framework`, `protected_targets` của task ⇒ nâng tối thiểu lên `original_source`).
Đường dẫn không nguồn nào phân loại ⇒ **UNCLASSIFIED** (trạng thái, không phải hạng) ⇒ R-UNCLASSIFIED ⇒ BLOCKED. Vùng khai `unknown` cũng là UNCLASSIFIED. Mâu thuẫn (ghi mà khai `none`; `read` mà khai khác `none`) ⇒ UNCLASSIFIED.
So khớp lexical, không quan sát: tồn tại, alias, link, hoa/thường thật thuộc S4/writer.

- `NO_PROTECTED_TARGET`: mọi đích ghi có vùng hiệu lực ∈ `light_write_zones`, không khớp mẫu authority, không giao với `protected_targets`. Với `read`: tập ghi rỗng.
- `CONTENT_USE_INTERNAL_ONLY`: đúng khi `content_use` được khai và mọi phần tử = `internal_draft`; sai khi có `sign`/`send_external`/`decision_basis`/`verified_claim`; vắng ⇒ chưa xác định ⇒ UNCLASSIFIED.
- Giả định mở **A-NEW_TARGET** (đích `create_new` chưa tồn tại): route `CONDITIONAL`, mà route CONDITIONAL/UNRESOLVED luôn là `BLOCKED` ở mọi pha. Chỉ observer S4 trong **cùng lượt đánh giá** đóng được, và chỉ ở dispatch/effect,
  chỉ là quan sát tại thời điểm (`limits`: `EXCLUSIVE_WRITE_NOT_PROVEN`, `RACE_NOT_EXCLUDED`). Ở **accept** không kiểm "đích hiện không tồn tại" và không re-route thành `overwrite` chỉ vì file nay có thật: cần proof lịch sử (mục 6).
- Hàng thắng/hợp giữ nguyên v2: `UNION_OF_REQUIREMENTS`, `main_may_downgrade=false`, `unmatched_effect_route=R-UNCLASSIFIED`. R-UNCLASSIFIED không bao giờ rơi về nhẹ.

## 5. Routing

Chín `row_id` của v2 giữ nguyên (cùng gate, pha review, `attributed_refs_required`, `forced_disposition`), chỉ hai hàng đổi:

- **R-READ_DRAFT:** ba mệnh đề A/B/C như bảng mục 3; `required_gates` không đổi (GRANT_SCOPE, PATH_SCOPE, TOOL_SCOPE, ENVELOPE). BINDING, ACTUAL_OUTCOME và REQUIREMENTS đến hạn theo task và pha, không theo cột `required_gates`:
  REQUIREMENTS ở accept; ACTUAL_OUTCOME ở accept khi task có action ghi; BINDING từ effect.
- **R-MUTATION:** thêm mệnh đề `create_new` + `write_zones [agent_runtime]`.

Tác động ghi runtime khác mệnh đề trên chỉ đi theo hàng hiện hành. Không hàng nào dùng tên tool làm điều kiện.

## 6. Owner protocol P-CN1 (M-2)

`owner_protocols` trong policy là nơi duy nhất khai báo ngoại lệ. Một mục khớp **chỉ khi đồng thời** có đúng protocol id, version, `entrypoint`, `entrypoint_sha256` quan sát được bằng pin, và các điều kiện theo pha. Chuỗi `tool: publish_new`,
`protocol: P-CN1` tự khai hay việc file nằm trong thư mục runtime **không** đủ. Pin là so sánh version/bytes hợp tác (ADVISORY): không chứng minh tool không bị giả mạo hoặc process thật là tool đó, và không cấp grant.

**Envelope (đúng bảy tác động của một lần gọi, theo thứ tự — schema cố định):**

| # | Tác động | Phạm vi |
|---|---|---|
| T1 | mkdir | tổ tiên của `target` dưới `working/` hoặc `output/` |
| T2 | mkdir | chỉ thư mục `publish` dưới `.agent/runtime` đã có sẵn (owner không tạo `.agent` hay `.agent/runtime`) |
| T3 | create | file prepared của rid |
| T4 | create | file staged của rid |
| T5 | link | `target` |
| T6 | create | đúng một file kết thúc của rid (published, conflict, abandoned hoặc unknown) |
| T7 | delete | chỉ file staged của chính rid |

Ngoài danh sách (sửa/xóa evidence, file runtime khác, STATE/HANDOFF, đổi tên, overwrite) không được miễn và theo route hiện hành (`not_exempt`). Grant phải phủ **toàn bộ T1–T7 áp dụng**: `tools ⊇ {publish_new}`,
`operations ⊇ {create_new, delete}`, `paths` phủ tổ tiên/target (T1, T5) và thư mục runtime publish (T2–T4, T6, T7). `delete` chỉ được tiêu thụ ở T7 (staged của cùng rid), không thành quyền xóa nơi khác.

**Điều kiện theo pha** (`required_by_phase`):

- **dispatch/effect:** version+entrypoint được nhận; hash entrypoint quan sát = pin; route (B)/(C); grant phủ envelope; không pha review nào bị đòi (`review_phases_supported` rỗng); S4 quan sát tại thời điểm đích vắng và `.agent`, `.agent/runtime` đã có sẵn là thư mục thường (cùng precondition owner áp dụng; thiếu ⇒ `RUNTIME_PARENT_MISSING`, không PASS); task biểu diễn được đúng bởi owner (`build_task(request_from_task(task), rid)` cho cùng projection C1 intent/context/accepted_task/action, nếu không ⇒ `TASK_NOT_OWNER_REPRESENTABLE`, TOOL_SCOPE UNSUPPORTED); riêng effect thêm input hiện tại khớp digest công cụ soạn đã đọc (chính `publish` cũng kiểm).
  **Không đòi và không nhận receipt** ở hai pha này: chưa có published; không tạo receipt trước để mở effect.
- **accept:** ngoài các điều kiện còn áp dụng, `effect.receipt_ref` resolve tới bằng chứng `published` duy nhất của rid (cùng task snapshot), các file runtime của rid nằm trong envelope, bytes hiện tại của đích bằng nội dung đã publish
  (lệch ⇒ `CHANGED_AFTER_PUBLISH`), và D4 đủ (mục 8). Thiếu/hỏng/nhiều bằng chứng ⇒ `PRECONDITION_PROOF_MISSING` dù hash khớp. Kết quả accept không dùng để mở dispatch/effect.

**Ánh xạ bằng chứng `publish-v1` sang record** (công cụ dựng trong bộ nhớ khi chạy checker, không lưu): task ← task snapshot trong prepared (hình đúng `build_task` của owner, `schema_version` v3); effect REQUEST ← prepared;
effect OUTCOME `APPLIED` ← published, `outcome.artifacts = [{path, digest, role: ACTUAL_BYTES}]`, `binding.outputs` bằng nhau; `receipt_ref` kind `effect_receipt`, `locator` trỏ published, `digest` = SHA-256 của **raw bytes** file published
(LAW-CJ/2, không xuống dòng cuối), attribution `TOOL_OBSERVATION`/`TOOL_OUTPUT` do tool ghi và quan sát. Các trường identity/nlink/protection/recovered/at, `supersedes`, `inputs_observed_at_publish`, `platform`, `entrypoint_sha256` của bằng chứng
là chẩn đoán, **không** nằm trong projection. `supersedes` chỉ là lineage, không chứng minh bản hiệu lực.

Lịch sử ≠ hiện tại: published là proof lịch sử do writer ghi lúc thao tác; S4 đọc bytes hiện tại. Hash hiện tại trùng không chứng minh nguồn gốc. Bằng chứng nằm trong vùng agent ghi được, `tamper_resistance = NONE`: P-CN1 chống nhầm bản và tai nạn, không chống giả mạo.

Điều kiện `PROTOCOL_VERSION_ENTRYPOINT_ACCEPTED` tại accept (mục6) bao gồm so protocol/version và `prepared.entrypoint_sha256` với owner protocol/pin đã được nhận, cùng liên kết snapshot/receipt đúng rid. Hash script đang có khi accept không thay cho pin lịch sử trong prepared. Không kiểm lại đích vắng ở accept; không suy lịch sử từ bytes hiện tại. Đây vẫn là kiểm nhất quán hợp tác ADVISORY, không chứng minh process thật đã chạy đúng code.

### 6.1 Ghi chú vận hành P-CTX1 (`operational_context_protocol`, không phải artifact)

Một field riêng của policy, **tách khỏi** `owner_protocols` và envelope T1–T7 của P-CN1 (không dùng lại record, thao tác, vùng hay evaluator). Khai: owner `tools/context_update.py`, version 1, pin `entrypoint_sha256` (ADVISORY như P-CN1), Windows NTFS local,
đúng hai đường dẫn `.agent/STATE.md` và `.agent/HANDOFF.md`, **một file mỗi lần gọi**, chỉ file có sẵn (thiếu thì từ chối, init riêng), hash expected-before bắt buộc, thư mục .agent và .agent/runtime có sẵn và được pin trước mọi probe/ghi.
Envelope C1–C5: đọc bytes hiện tại của đích; probe ghi trong runtime; tạo journal/staging/backup của chính giao dịch; thay đúng một đích; xóa staging/backup của chính giao dịch. Giao dịch dùng `prune=False`: không xóa journal khác, không tạo hay xóa thư mục runtime cha.
Điều kiện grant: actor kiểm group grant của user/session còn hiệu lực **trước khi gọi**; nội dung STATE/HANDOFF không phải nguồn grant. Ghi trực tiếp/native, đường dẫn khác, journal khác hay tạo/xóa runtime cha không được miễn và đi theo route hiện hành.

Đây là ghi chú vận hành, không phải sản phẩm giao người dùng: không task/effect/result/receipt/D4 cho mỗi lần lưu, không PASS, không là grant, policy, review verdict hay nghiệm thu, và ghi đường dẫn artifact vào context không chứng minh artifact đã đạt.
Metadata này đưa vào checker artifact vẫn UNSUPPORTED (`unsupported_in_candidate`: `OPERATIONAL_CONTEXT_P_CTX1_CHECKER_EVALUATION`); các vùng `.agent/STATE.md`/`HANDOFF.md` vẫn chưa có zone (`AGENT_STATE_AND_PACKAGE_CONTENT_ZONES`).
Hash guard chỉ phát hiện bytes đã đọc bị đổi (single-writer hợp tác, ADVISORY), không phải CAS của filesystem; một file mỗi lần nên không có atomic hai file. Kết quả công cụ: WRITTEN, UNCHANGED, CONFLICT, ERROR, UNKNOWN theo hành động thực.

**Giới hạn I1 được Orchestrator chốt 18/10/2026:** nội dung phải không rỗng, UTF-8, không NUL, tối đa 8 MiB (STATE vẫn tối đa 60 dòng và đúng khung). Đây là giới hạn đọc/ghi của owner, không phải tiêu chí nghiệm thu nội dung. Có transaction dở thì từ chối lần ghi mới bằng `TRANSACTION_UNFINISHED`; không quét/đọc được journal thì từ chối trước writer, không coi là không có giao dịch dở. Không tự resume/rollback; no-op không tạo transaction. Journal `committed` được giữ lại, không tự dọn; dung lượng tăng theo số lần ghi, không hứa retention hữu hạn hay undo lâu dài.

Pin P-CTX1 chỉ nhận diện bytes của entrypoint `context_update.py`, không pin toàn bộ dependency `transaction.py`/`publish_new.py`, không chứng minh dependency đã nạp đúng hoặc process đã chạy đúng owner. Review độc lập áp dụng cả delta Transaction và các helper được dùng; pin P-CN1 không thay cho kiểm dependency lúc gọi P-CTX1. I1 giữ mức COOPERATIVE/ADVISORY và chưa có evaluator P-CTX1; không gọi pin này là bằng chứng toàn chuỗi hay quyền thực thi.

## 7. Binding `law.cvf.bind/3`

Canonical JSON `LAW-CJ/2` và các projection **giữ nguyên định nghĩa của v2** (`intent`, `task`, `context`, `action`, `policy`; trường set; loại trừ; các kiểm tra độc lập với digest ở mỗi pha), chỉ đổi literal `bind` thành `law.cvf.bind/3`
và `schema_version` của task thành `law.cvf.control/3` (nằm trong projection `task`). Vì vậy mọi digest đổi so với v2 dù nội dung giống hệt. Không có `overlay_digest`, `completion`, `action_index` trong v3 candidate.
Quy tắc vắng/một phía/`null`/trùng phần tử của v2 giữ nguyên. Digest của review/effect/result không được định nghĩa: tham chiếu bằng id và binding.

| Record | `outputs` | `action_digest` |
|---|---|---|
| effect REQUEST | vắng | có |
| effect OUTCOME | có, `ACTUAL_BYTES`, = `outcome.artifacts` | có |
| result | có, `ACTUAL_BYTES`, = `result.artifacts` (EXACT) | tùy chọn như v2; nếu có phải so đúng action, không bỏ một phía để né mismatch |

Mọi phần tử `outputs`/`artifacts` phải có `role: ACTUAL_BYTES` (schema `output_object`). Vectors tính lại digest bằng hàm tham chiếu và bằng chính `build_task` của owner (projection_fixture).

**Screening miền canonical của bundle** (checker, không đổi định nghĩa trên): chỉ dữ liệu thật sự đi vào projection `intent`/`context`/`task`/`action` hoặc khóa `obj_proj` của comparator mới bị từ chối khi ngoài miền LAW-CJ/2 (`UNSUPPORTED_BINDING_PART`). Metadata bị loại khỏi projection (ví dụ `note`, `locator`/`attribution` của ref, `proposed_by`, các record `grant`) không bị từ chối vì lý do canonical; schema, strict parse, literal, kích thước và độ sâu vẫn áp cho chúng. Policy vẫn là projection của **toàn object policy** (owner cố định). Bảng đường dữ liệu → projection ở README của checker v3 trong kho nguồn (không có trong bản phân phối); API canonical thuần LAW-CJ/2, vectors và digest không đổi.

## 8. Nghiệm thu D4 (`result.user_acceptance`)

Công cụ dựng từ bằng chứng, user không gõ metadata. Các trường: `ref` (kind `user_acceptance`, `USER_CONFIRMATION`, kênh `USER_MESSAGE`/`HOST_CONFIRMATION_UI`, có `evidence_locator`), `task_id`, `task_revision`,
`accepted_task_digest` (tính lại từ projection `task` của task hiện hành), `accepted_requirements` (tập `req_id`), `result_id`, `accepted_artifacts` (`ACTUAL_BYTES`) và `presented_summary {locator, digest}`.
Schema chỉ cố định hình và lớp nguồn; checker so khớp với task/result hiện hành trong luồng P-CN1 một file ở mục 11. Quy tắc: `accepted_requirements` ⊇ mọi requirement `mandatory` (thiếu ⇒ `USER_ACCEPTANCE_INCOMPLETE`, phần chưa phủ `NOT_CHECKED`);
digest/task/artifact không khớp bản hiện hành ⇒ `USER_ACCEPTANCE_STALE`; `accepted_artifacts` = `result.artifacts` EXACT. Im lặng, mở file, "ok" không nêu bản, grant làm việc, xác nhận bản cũ: không đủ.
`USER_ACCEPTED` trong `acceptance_states` đòi object này. Chỉ dùng cho REQUIREMENTS khi **không** có pha review bắt buộc. Nó là DECLARED: không thay review, veto, bytes, proof thao tác hay bảo toàn; `requirements_semantic_verified` luôn `false`.

## 9. UNSUPPORTED

Giữ các mục của v2 (alias đường dẫn, đối tượng không phải file, ngữ cảnh thực của role, digest review/effect/result, thời gian/hết hạn, tính xác thực của attribution, bằng nhau ngữ nghĩa giữa định dạng, so với digest v1)
và thêm: tương đương digest `bind/2` ↔ `bind/3`; `STAGED_BYTES`/`relation`; overlay; occurrence nhiều action; tính xác thực của receipt và của pin entrypoint; suy "đích từng chưa tồn tại" từ trạng thái file hiện tại. Xem `vectors.json`, nhóm `unsupported`.

## 10. Phạm vi của candidate này

Đã làm: schema, policy, bản đọc, 22 bundle giả (15 hợp lệ cấu trúc, 7 bị schema từ chối) + EXPECTED, vectors, test `test_control_v3_candidate.py` trong thư mục tests của kho nguồn (cấu trúc, định nghĩa binding, pin, hoán vị mutation, đối chiếu với `tools/publish_new.py`).
Entry/loader/canon, helpers refs/binding và routing thuần S3-C/D (`routing.py`) đã nối vào entry ở mức binding/route một action (không root: không gate, observer, receipt, D4 runtime, pin entrypoint hay review verdict). Với root tường minh, luồng P-CN1 một file (mục 11, `observer.py` + `workflow.py`, REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS) thêm đúng các phần đó cho một task/action/target/grant; chưa review verdict, shape khác, activation.
**Đã review nhận WITH_LIMITS:** I1/P-CTX1 operational context, I2 navigation và I3 package/lifecycle/readiness; bản phân phối mang closure v3 tường minh và MANIFEST theo owner đóng gói. Đây là các mốc tích hợp có giới hạn, không tự kích hoạt candidate.
**Chưa được suy ra:** nghiệm thu G-03/G-04 đầy đủ, profile/host ngoài phạm vi đã kiểm, activation, migration, grant hoặc issuer proof chống giả, D4/user acceptance từ pilot chưa được user nghiệm thu, host/native enforcement hoặc đóng R-7 end-to-end. Mọi `expected_design` trong EXPECTED.json của các ví dụ giả (chỉ có trong kho nguồn) vẫn là kỳ vọng tình huống giả định (`workflow_status: NOT_RUN`), không là verdict của bundle nguyên trạng.

## 11. Output tối thiểu `law.cvf.check/3` (candidate)

Đây là phần output của packet4.8 thực sự dùng cho luồng hẹp, không phải record trong `control.schema.json`, không tạo schema output hoặc checker mới ở A0.
Entry foundation đã sinh output kiểm cấu trúc, chưa verdict workflow; EXPECTED và test fixture không được giả làm output checker. Khi mới có foundation mà chưa có evaluator, input đúng cấu trúc vẫn BLOCKED với `CANDIDATE_EVALUATION_NOT_IMPLEMENTED`, không PASS/NOT_APPLICABLE.

**S3-C/D đã review nhận BINDING_ROUTING_ONLY:** `phase_scope` là nhãn phạm vi đã chạy, không phải pha: null khi cấu trúc không đạt, còn lại STRUCTURE_ONLY/STRUCTURE_BINDING/STRUCTURE_ROUTING/STRUCTURE_BINDING_ROUTING theo cờ coverage (kể cả DENY/UNSUPPORTED sau khi cấu trúc đạt). `route={evaluated,rows,status,assumptions}`: evaluated chỉ true khi đã route đúng một task/một action; mỗi row có row_id, match_state (T chắc chắn, U có thể áp dụng), required_gates/required_review_phases, write_zones, not_evaluated_conditions. Hợp nghĩa vụ của cả T/U, U giữ route UNRESOLVED; không gán ENVELOPE_EXCEEDED=F khi chưa đo, không bỏ nghĩa vụ R-EXTERNAL hoặc kết luận review đã có/thiếu. Chỉ T mới forced DENY; known-loss task-wide đã khai ưu tiên cả trước unsupported nhiều task/action. Preservation có target bắt buộc, chưa map sang action nên veto bảo thủ ở task; không suy thiếu content_use là nội dung high-stakes. `gates=[]`, aggregate NOT_EVALUATED/count0/open_assumptions rỗng là placeholder, không chứng minh không có nghĩa vụ/gate/giả định. Chỉ coverage binding/routing thực chạy được bật; coverage gate/quan sát/semantic vẫn false, assurance UNVERIFIED. Không suy PASS/quyền từ route resolved hoặc giá trị rỗng; README v3 là output/error mapping chi tiết.

**Luồng P-CN1 một file (`implementation_stage = P_CN1_ONE_FILE`, review 18/10/2026 REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS):** chỉ chạy khi người gọi đưa **root tường minh** (`--root` / `project_root`, root chỉ chứa dữ liệu; code owner nạp từ cây nguồn LAW cố định, không từ root). Không root = diagnostic `BINDING_ROUTING_ONLY` ở trên, không gate, không PASS. Phạm vi hỗ trợ: đúng một task, một action `create_new` tool `publish_new`, một target dưới `working/`/`output/`, một `grant_ref`, không pha review, không overwrite/input trùng target; ngoài phạm vi vẫn UNSUPPORTED/BLOCKED theo route, không hạ gate.
- `phase_scope` ghép theo cờ thực chạy: `STRUCTURE` + `_BINDING` + `_ROUTING` + `_GATES` + `_OBSERVER` (theo thứ tự này, chỉ token đã chạy). `gates_evaluated` true chỉ khi shape được hỗ trợ và gate được tính; `target_existence_observed` / `artifact_bytes_observed` true chỉ khi observer thực đọc trong lần kiểm này (đích ở dispatch/effect; bytes đích hoặc input ở effect/accept); `actual_operation_observed` và `requirements_semantic_verified` luôn false.
- `gates[]`: `GRANT_SCOPE`, `PATH_SCOPE` (có `subchecks` lexical / observed_at_time / precondition_history), `TOOL_SCOPE`, `ENVELOPE` (d e a); `BINDING`, `INPUT_REVISION` (e a; d `NOT_YET_DUE`); `ACTUAL_OUTCOME`, `REQUIREMENTS` (a; d e `NOT_YET_DUE`). Trạng thái: `MET`, `NOT_MET`, `NOT_CHECKED`, `UNSUPPORTED`, `NOT_YET_DUE`, `NOT_REQUIRED`, `USER_ACCEPTED_DECLARED` (chỉ REQUIREMENTS). Gate đến hạn không thuộc {MET, USER_ACCEPTED_DECLARED, NOT_REQUIRED} ⇒ BLOCKED. ENVELOPE chỉ so số học DECLARED (`REQUESTED`/`APPLIED`) với `grant.limits`; thiếu/UNKNOWN/UNSUPPORTED/đơn vị không so được ⇒ U ⇒ `NOT_CHECKED`, `expires_at` ⇒ `UNSUPPORTED`; T/F/U được nối vào `ENVELOPE_EXCEEDED` của routing rồi tính lại hợp nghĩa vụ.
- A-NEW_TARGET chỉ đóng bởi quan sát đích-vắng của observer trong **cùng lượt** ở dispatch/effect (`CLOSED_BY_OBSERVATION`, kèm `limits` EXCLUSIVE_WRITE_NOT_PROVEN, RACE_NOT_EXCLUDED); accept không kiểm đích-vắng và không re-route thành overwrite.
- **Review 18/10 — REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS, corrective đã nhận trong luồng một-file:** writer từng tự sinh rid làm đổi task giữa trước/sau publish, và T2 từng tạo hai thư mục cha ngoài prefix grant publish. Nay: (1) caller chọn rid trước dispatch (xem đầu tài liệu) và dùng cùng request/rid cho dựng task, effect, publish, accept; (2) mọi pha kiểm task biểu diễn được đúng bởi owner qua `request_from_task` + `build_task` (hàm thuần, checker không gọi hàm ghi) và so bằng projection C1 sẵn có; task có context/envelope/effects mà owner bỏ hoặc không hỗ trợ ⇒ TOOL_SCOPE UNSUPPORTED `TASK_NOT_OWNER_REPRESENTABLE` (gate khác giữ chẩn đoán đã tính, không dựng task khác lúc accept); (3) dispatch/effect quan sát `.agent`, `.agent/runtime` có sẵn (`runtime_parents_ready`) ở PATH_SCOPE.observed_at_time, thiếu ⇒ NOT_MET `RUNTIME_PARENT_MISSING`, không quan sát được ⇒ NOT_CHECKED. Không mở rộng grant. INPUT_REVISION ở effect/accept phải đọc input không-target hiện tại; accept còn so bằng chứng lịch sử. `profile_ref` chưa giải giữ ENVELOPE UNSUPPORTED/U; không cho PASS chỉ vì có tên profile. Workflow cùng task đã được nhận trong phạm vi một-file Windows NTFS local, COOPERATIVE/ADVISORY; chưa integration hoặc activation.
- `PASS` ⇔ shape hỗ trợ ∧ route `RESOLVED` chỉ hàng R-READ_DRAFT (T) ∧ không giả định OPEN ∧ không lý do DENY/UNSUPPORTED/BLOCKED ∧ mọi gate đến hạn ∈ {MET, USER_ACCEPTED_DECLARED, NOT_REQUIRED}. Khi đó `assurance_level = ADVISORY`, exit 0, `effect_authorized = false`; PASS một pha không mở pha khác. Mã lý do do checker sở hữu thêm cho luồng này: `P_CN1_SHAPE_UNSUPPORTED`, `ENVELOPE_UNMEASURED`, `ENVELOPE_ROLE_MISMATCH`, `ENTRYPOINT_PIN_MISMATCH`, `OBSERVATION_UNAVAILABLE`, `TARGET_EXISTS_OBSERVED`, `RID_EVIDENCE_PRESENT`, `EFFECT_RECORD_MISSING`, `OUTCOME_RECORD_MISSING`, `RESULT_RECORD_MISSING`, `DUPLICATE_EFFECT_RECORD`, `DUPLICATE_RESULT_RECORD`, `ACTION_UNREPORTED`, `ACCEPTANCE_CLAIM_NOT_SUPPORTED`, `USER_ACCEPTANCE_INCOMPLETE`, `USER_ACCEPTANCE_STALE`, `EVIDENCE_NOT_VERIFIED`, `EXPIRES_AT_UNSUPPORTED`, `PATH_ZONE_UNDETERMINED`, `OPERATION_MISMATCH`, `ACTION_INCOMPLETE`, `ROUTE_NOT_P_CN1_LIGHT`, `ROUTE_DECLARED_MISMATCH`, `TASK_NOT_OWNER_REPRESENTABLE`, `RUNTIME_PARENT_MISSING`, `GATE_NOT_SATISFIED`, `WORKFLOW_ERROR`, `ROOT_UNUSABLE` (cùng các mã enum `INPUT_CHANGED_SINCE_READ`, `PRECONDITION_PROOF_MISSING`, `CHANGED_AFTER_PUBLISH`, `BINDING_MISMATCH`...). Chúng không thuộc enum `reason_code` của record.

| Trường | Quy tắc tối thiểu |
|---|---|
| `check_version`, `contract` | `law.cvf.check/3`, `v3`; chọn version tường minh, không tự dò/fallback/migrate |
| `selection`, `candidate_status`, `implementation_stage` | ghi lựa chọn và tranche thực chạy; candidate vẫn CANDIDATE_NOT_ACTIVE, không tự activation |
| `evaluation_basis`, `phase`, `phase_scope` | COOPERATIVE_WORKFLOW; dispatch/effect/accept; nêu đúng phạm vi đã kiểm |
| `disposition` | PASS/BLOCKED/DENY/UNSUPPORTED/NOT_APPLICABLE; PASS chỉ sau evaluator được nhận, route RESOLVED, không giả định mở và mọi gate đến hạn thỏa trong phase_scope |
| `effect_authorized`, `assurance_level`, `init_error` | luôn false; UNVERIFIED hoặc ADVISORY theo căn cứ thực; init_error là boolean, không giả thiếu dependency thành PASS |
| `reasons`, `details` | mã duy nhất đã sắp và chẩn đoán; không chép payload/secret. USER_ACCEPTANCE_INCOMPLETE/STALE là mã checker, không bổ sung vào enum record |
| `owners` | schema_sha256/policy_sha256 của bytes thực đã đọc (hex SHA256 hoặc null khi chưa có); không chứng minh owner được bảo vệ |
| `route` | rows, status RESOLVED/CONDITIONAL/UNRESOLVED và assumptions. A-NEW_TARGET chỉ đóng bằng quan sát S4 cùng lượt ở dispatch/effect, không kiểm đích-vắng tại accept |
| `gates` | mỗi gate có gate, due_in, status, evidence.required/provided (D/C/R/O), limits, reasons, owner_of_proof; chưa đánh giá thì không ghi MET |
| `aggregate` | tách due_gates/met/not_required/not_yet_due/not_checked/unsupported/not_met, user_accepted_declared và open_assumptions; conclusion_scope RECORD_CONSISTENCY_IN_MEMORY, không ngầm kiểm ngữ nghĩa nội dung |
| `coverage` | phản ánh đúng cấu trúc/binding/routing/gates thực đã đánh giá; artifact_bytes_observed/target_existence_observed chỉ true khi observer thực chạy cùng lượt. Foundation không observer để false; actual_operation_observed và requirements_semantic_verified không nâng thành true chỉ từ receipt/D4; owner_protection NOT_PROVEN |

PATH_SCOPE khi được evaluator triển khai phải báo riêng `lexical`, `observed_at_time`, `precondition_history`: lexical không thay quan sát filesystem, quan sát hiện tại không thay lịch sử published. Thiếu proof lịch sử ở accept là PRECONDITION_PROOF_MISSING; bytes đổi là CHANGED_AFTER_PUBLISH; input khác bytes công cụ soạn đã đọc là INPUT_CHANGED_SINCE_READ. Review bắt buộc của task ngoài luồng hẹp là REVIEW_REQUIRED_UNSUPPORTED trước tác động, không bỏ review để nhận nháp.
Các cấu trúc output cho overlay, review scope mới và occurrence nhiều action của packet4.8 vẫn hoãn như mục3; không cần dựng chúng để nhận A0 hoặc foundation.
