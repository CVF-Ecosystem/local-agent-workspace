# G-02-C2/S3-D0 — Amendment packet (thiết kế, chưa phải schema) — Rev 3

**Trạng thái hiện hành G-03/G-04 (18/10/2026): G-03 NARROW_COOPERATIVE_BASELINE_ACCEPTED_WITH_LIMITS; G-04 CANDIDATE_INTEGRATION_ACCEPTED_WITH_LIMITS, official-release PENDING.** M-3 đủ D4: user duyệt bản lab6ee4cef2, accept thực PASS/ADVISORY, Reviewer nhận REVIEW_ACCEPTED_D4_LAB_ONE_FILE_WITH_LIMITS. Chỉ task/rid3bf643838fb844ed98080d7e1545279b rev1/2requirement/artifact EXACT; không phát hành LAW/semantic verification/host enforcement. RC3/native checker/Office tối thiểu nhận có giới hạn như roadmap6.2/đầuHANDOFF; output Word mới chưa publish/D4 và không bắt làm thêm để khép scope Office. I-02 rev1 dưới5.4.A cho tiếp phát triển A–D theo dependency, giữ gate phát hành và x14 PARKED. Các mốc dưới là lịch sử, không dispatch lại I1–I3/Office.

**I3 — REVIEW_ACCEPTED_I3_PACKAGE_LIFECYCLE_WITH_LIMITS (18/10/2026):** Reviewer Sol6.1 High nhận owner package/lifecycle/readiness của5.4.3 sau guard/source/manifest/bootstrap và raw-EOL fixes. Closure giao14file v3; pinned owners/schema/policy/vectors không đổi. Attributes giữ bytes4file; ZIP giữ raw machine/dependencies, không đổi nghĩa pin. Reviewer8guard+9RCtarget0skip; Root packagecheck0lỗi/1cảnhbáo,2MainFlows+3ownerpins0skip. Worker962/3skip/fullRC ở HANDOFF là trước review, không gắn cho bytes cuối. Fullgate cuối, Office/agent pilot/support matrix/G-03/G-04/release/activation còn mở. Hash/lệnh/giới hạn ở review đầu HANDOFF.

**I2 — REVIEW_ACCEPTED_I2_NAVIGATION_WITH_LIMITS (18/10/2026):** Reviewer Sol6.1 High nhận owner-UI5.4.2 sau4fix helper (pointer path khi mở, pin lịch sử, cap trước validation, heading malformed). Reviewer53test0skip, Root browser5/0skip và ownerpins3/0skip; helperfinal d3de931ec0686aa3, App/UI/acceptedowners giữ. Chưa Office/agent pilot, I3/package/5.4.3/G-03/G-04/activation. Môi trường controlled-card và readiness actual launcher chốt trong roadmap6.2; không đổi requirement toàn LAW. Review đầu HANDOFF giữ hashes/evidence đầy đủ.

**I1/P-CTX1 — REVIEW_ACCEPTED_P_CTX1_WITH_LIMITS (18/10/2026):** Reviewer Sol6.1 High nhận owner operational context của5.4.1 sau strict journal scan fail-closed và template STATE fix. Pin owner ee7cb6b15f3b5e70; policy af141b37c242119c/vectors79d63454f1143c41/22vídụ deb1ae93824126f3 đã refresh dẫn xuất. Bounds/retention/entrypoint-only assurance chốt ở contract v3 §6.1; không dependency closure/enforcement. I2/I3/G-03/G-04 và activation chưa nhận. Chi tiết evidence/hash trong review đầu HANDOFF.

**P-CN1 workflow một file — REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS (18/10/2026):** cùng task_id/revision và4C1 digest qua dispatch/effect/publish/accept trên Windows NTFS local; COOPERATIVE/ADVISORY, candidate chưa active. Corrective caller rid + task roundtrip TOOL_SCOPE + required/pinned runtime parents đã nhận. Reviewer chỉ sửa docstring refusal/wrote, owner final pin `8a4e5914d0892ea1d28566f96f7114afd857b441e2013d8534dc9cb93e4bd852`; pin policy255d76c66021c4f1/vectors27b926d8f7ed21b4/22vídụ b21356009951872d đã refresh đúng dẫn xuất, schema/projection/acceptance/v1/v2 giữ. Reviewer16/14, Root18 trước docstring/20 sau pin targeted đạt0skip. Bootstrap init/transaction hiện có đã probe đạt; chưa kiểm đủ user journey/package. Chưa integration/activation/G-03/G-04; I-01/§5.4.A đã nhận thiết kế có điều kiện; I1/P-CTX1 READY_FOR_OPERATOR_DISPATCH, I2/I3 chưa giao. Các gate vẫn mở, không dispatch lại corrective.

**Mốc trước workflow — C/D và SCREENING REVIEW_ACCEPTED_BINDING_ROUTING_ONLY:** code/lịch sử và bằng chứng ở HANDOFF; không dispatch lại brief C/D/screening. Trạng thái hiện hành ở đoạn trên. Các đoạn tiếp theo là lịch sử thiết kế, không mở S3 rộng.

**A0 hẹp — CONTRACT_CANDIDATE_PENDING_REVIEW (Worker Claude, 18/10/2026):** đã dựng cây candidate `.cvf/contracts/v3/` và `.cvf/rules/v3/` (schema, policy `law.cvf.routing/3`, bản đọc, 22 ví dụ giả + EXPECTED, vectors) và `tests/test_control_v3_candidate.py` đúng bảng 5.4; pin writer SHA256 `f2b1b425690eacd57ae5971910e7e492c0e2bd70613190d8c7b146ca5c131f9d`. v1/v2 và writer nguyên byte. Chưa evaluator/checker (S3-B0), integration, activation; R-7 end-to-end vẫn BLOCKED. Tên trường owner protocol trong candidate là `protocol_id`/`protocol_version`/`owner_tool`/`entrypoint`/`entrypoint_sha256` (thay `id`/`version` của đề xuất ở 4.3.2); `reason_code` thêm bốn mã `INPUT_CHANGED_SINCE_READ`, `PRECONDITION_PROOF_MISSING`, `CHANGED_AFTER_PUBLISH`, `REVIEW_REQUIRED_UNSUPPORTED` (mã thứ tư ngoài ba mã nêu ở 5.4 vì C-4 dùng nó cho task đòi review); `USER_ACCEPTANCE_*` và các mã 4.8 khác giữ là mã do checker sở hữu, ngoài enum.

**S3-B foundation v3 hẹp — IMPLEMENTED_PENDING_REVIEW (FOUNDATION_ONLY, Worker Claude, 18/10/2026):** đã thêm entrypoint `.cvf/checks/control_check_v3.py`, package `.cvf/checks/v3/` (loader, canon, refs, binding, README) và `tests/test_control_check_v3.py` theo B0 copy-forward; output `law.cvf.check/3` nền ở `.cvf/checks/v3/README.md`. Cấu trúc hợp lệ vẫn BLOCKED/CANDIDATE_EVALUATION_NOT_IMPLEMENTED; chưa evaluator, route/gate, observer, S4-min, integration hay activation; R-7 end-to-end vẫn BLOCKED. Không sửa v1/v2, schema/policy/vectors v3, writer.

Trạng thái: **MAIN_SCOPE_DECIDED_R7_DESIGN_PENDING** (Rev 3 = Rev 2 sau ba sửa nhỏ của Main, hash `1f819c8c6aa3d27d`, cộng delta D1–D4 và disposition R-1…R-6 theo `roadmap/G02_C2_S3_D0_REVIEW_R2_2026-10-18.md`; Rev 2 sửa theo `roadmap/G02_C2_S3_D0_REVIEW_2026-10-18.md`: F1–F7, Q-1…Q-11). Main quyết định baseline cần tạo file nháp mới khi người dùng yêu cầu; R-7 proof/owner chưa có nên chưa nhận acceptance/implementation. Chưa đổi gate; chưa A0/code. Ngày 18/10/2026.
**Delta D0 (18/10/2026, P-CN1-C DESIGN_ACCEPTED_WITH_CONSTRAINTS; READY_FOR_DISPATCH P-CN1-I):** Orchestrator/Reviewer đã review contract 4.3.3 bản `584fcba93ef7255e`; Orchestrator sửa các lệch xác định về serialization identity, terminal/khóa, bootstrap/wrote, cleanup và wire errors trong mục đó. 4.3.3 là owner API/evidence cho tools-only I. Chưa implementation được nhận, chưa A0/integration/activation; R-7 vẫn `UNSUPPORTED`/BLOCKED. M-1…M-5 giữ; M-2 scope amendment đã nhận nhưng chưa ngoại lệ runtime có hiệu lực. Các review bản `692978f4bef93f24` và `c7c7e49dcdcca535` giữ lịch sử.
**P-CN1-C (Worker Claude Opus 5.5, 18/10/2026, DESIGN_PENDING_MAIN_REVIEW):** thêm mục 4.3.3 (signature C-1, shape `publish-v1`/snapshot/mapping C1-D4 C-2, khóa/chuyển trạng thái C-3, eligibility theo pha C-4, ví dụ C-5, ca P-21…P-26 C-6); mapping ở mục 11 (C-1…C-5).
**Sửa theo review (Worker Claude Opus 5.5, 18/10/2026, DESIGN_PENDING_MAIN_REVIEW):** viết lại thân 4.3.2 theo năm sửa bắt buộc (snapshot, mapping C1, recovery, envelope/routing versioned, kế hoạch một action/Windows NTFS local); cập nhật 5.1–5.4, 7.2 R-2/R-3/R-7, 8, 11 (Sửa 1–5). Disposition Main giữ nguyên.
Worker: Claude Sonnet 5.5 (yêu cầu High; effort quan sát được: không xác nhận). Brief: `roadmap/G02_C2_S3_D0_BRIEF_2026-10-18.md`.
Hash: Rev 1 `f35a2f52165c112d`; Rev 2 `b09f02143eac9e34`; Rev 2 sau Main sửa `1f819c8c6aa3d27d`. Bảng F1–F7 → mục ở **mục 9**; bảng D1–D4 → mục ở **mục 10**. Ba sửa nhỏ của Main (coverage dương chỉ từ review PASS; bảng enum INCONSISTENT; DENY cưỡng bức ưu tiên trước CONDITIONAL→BLOCKED) được giữ nguyên.

**Cách đọc.** Mọi tên field, enum, mã, version trong tài liệu này là **đề xuất**. Packet không sửa byte nào của contract/schema/policy/vectors/ví dụ/checker/test/pin v1–v2,
không tạo cây v3, không là chấp thuận schema, migration hay kích hoạt. v2 vẫn CANDIDATE_NOT_ACTIVE; entry/API chưa nối helper S2; bundle đúng cấu trúc vẫn BLOCKED.
Không phần nào là bằng chứng workflow, quyền tác động hay quan sát bytes. **[K]** = kế thừa nguyên từ owner đã nhận; **[P]** = đề xuất mới.
Điểm Main đã chốt trong file review ghi **[M]**; điểm còn mở thật sự nằm ở mục 7.2.

Mức căn cứ (các chiều độc lập, **không** phải thang nâng cấp):

| Mức | Nghĩa | Ai tạo | Giới hạn |
|---|---|---|---|
| DECLARED | lời khai trong record kèm attribution | người ghi record | không chống giả; không đọc nguồn |
| COMPARED | so record với record / tập khai báo | checker (S2 helper) | hai digest tự khai trùng nhau chưa là đã kiểm bytes |
| RECOMPUTED | tính lại digest bằng canon từ trường record / bytes policy | checker (canon + S2) | chỉ nói về projection logic, không về file thật |
| OBSERVED | đọc bytes/thao tác thật bởi owner khác | observer S4, writer | **S3 không có**; coverage `artifact_bytes_observed`, `actual_operation_observed` giữ `false` |

---

## 0. Tóm tắt quyết định thiết kế

1. **Version [M].** Hướng bốn version `law.cvf.control/3`, `routing/3`, `bind/3`, `check/3` và **cây owner v3 candidate riêng** được nhận về thiết kế (mục 1.1). Chưa nhận cây code copy-forward, chưa activation; một version hiệu lực được chọn tường minh ở bước tích hợp, không hai nguồn policy cùng có hiệu lực.
2. **Vùng bảo vệ.** Bảng đường dẫn → `write_zone` nằm trong policy `routing/3` (thêm 3 giá trị `write_zone`); phép toán ở các hàng routing (tách R-READ_DRAFT, thêm một mệnh đề cho R-MUTATION và một cho R-AUTHORITY_CHANGE). *Chưa phân loại* là **trạng thái**, không phải hạng bảo vệ; overlay chỉ phân loại phần baseline thật sự chưa phân loại (mục 2).
3. **Route điều kiện ⇒ BLOCKED [M].** Route `CONDITIONAL`/`UNRESOLVED` luôn cho disposition `BLOCKED`, kể cả dispatch; báo phần record đã kiểm, giả định, pha cần proof và owner S4. Đọc có route đã resolve vẫn PASS trong phạm vi pha. Không có nhãn dương thay thế.
4. **Review.** Tách *đủ tư cách của từng review* khỏi *độ phủ của cả tập* (mục 3.3). Có bảng phạm vi tối thiểu từng pha; PRE_EFFECT bắt buộc phủ accepted task, ánh xạ intent→yêu cầu và các action occurrence được xét. Review chỉ được đòi khi có trong hợp policy hoặc yêu cầu review đã nhận cho task (mục 3.3.4).
5. **Anchor theo pha.** REQUEST → review PRE_EFFECT → OUTCOME → result → review PRE_INTEGRATION/PRE_DELIVERY, mỗi bước có anchor và tập binding riêng; staged→actual có quan hệ khai báo và owner proof (mục 4.2–4.3). Veto xác định theo phase/anchor/full binding; **trong D0 mọi non-PASS veto TASK_WIDE**, không suy độc lập từ target khác nhau (D3), không supersession (mục 3.4).
6. **Occurrence và tính đủ.** Action được định danh theo `(task_id, task_revision, index, digest)`; tập action bắt buộc lấy từ task đã chấp nhận, không từ khai của result (mục 4.4).
7. **Accept không bị claim tắt gate.** Gate bắt buộc ở accept do task + route + pha quyết; claim `CANDIDATE` không tắt ACTUAL_OUTCOME/REQUIREMENTS. Có ma trận diagnostic-only vs accept (mục 3.5).
8. **Đường nháp.** Dispatch/effect ghi mới vào `working/` hay `output/` là `BLOCKED` (route CONDITIONAL) cho tới khi S4 quan sát “đích chưa tồn tại” trong cùng lượt đánh giá; quan sát đó chỉ nói về **thời điểm quan sát** (D1). **Accept** không kiểm “đích hiện không tồn tại” mà đòi **proof lịch sử** gắn request/occurrence + liên kết thao tác do writer/protocol (chưa có owner) cùng bytes hiện tại (S4); thiếu ⇒ `UNSUPPORTED`/BLOCKED, không hứa S4 read-only là đủ (mục 4.3.1). Đọc không phụ thuộc S4. Đây là phụ thuộc UX có thật, không bị che (mục 6, AC-01/36). **Delta D0:** owner đề xuất cho proof lịch sử và liên kết là protocol P-CN1 (`tools/publish_new.py`, owner mới, mục 4.3.2); quan sát tại d/e là chế độ đọc S4-min của cùng owner. Chưa thi công ⇒ trạng thái trên giữ nguyên.
9. **Chặn, không giải trong D0:** recipe, vai không-core, thời gian, ex19, x14/race, host enforcement (mục 5.2). Điều kiện **trước tích hợp** [M]: protocol ghi STATE/runtime (Q-3) và thiết kế sửa nháp lặp (Q-4) (mục 5.4).
10. **Rev 3 (D1–D4).** (D1) tách proof precondition lịch sử khỏi quan sát file hiện tại (4.3.1); (D2) `OPTIONAL` chỉ bỏ nghĩa vụ thực hiện, không bỏ kiểm outcome/reconcile (4.4); (D3) không suy độc lập từ target khác nhau, thiếu căn cứ thì veto TASK_WIDE (3.4 V-3); (D4) user acceptance gắn đúng task/revision/digest, tập requirement bắt buộc và artifact (4.7.3, 3.2). Mapping ở mục 10.

**Đã đọc (đúng phạm vi):** AGENTS, PROJECT, STATE, HANDOFF (S3-D0, S2 hiện hành, thiết kế C2 bước 1 gồm bảng gate × pha và Q1–Q8, Bước tiếp theo, mục review mới nhất), brief, hai file review (Rev 1, R2); `.cvf/contracts/v2/CONTROL_CONTRACT.md`, `control.schema.json`, `ex02`, `.cvf/rules/v2/ROUTING_POLICY.json` và `CONTROL_RULES.md`, `.cvf/checks/v2/README.md`, `roadmap/DE_XUAT_PHAM_VI_KIEM_SOAT_LAW_2026-10-18.md` (đều toàn văn);
README của `.cvf`, `roles`, `references`, `working`, `output`, `archive`, `assets`, `.agent`; cây thư mục gốc LAW (38 mục), `.gitignore`; tên pin trong ba file test control (không đọc assertion); `MANIFEST.sha256` (chỉ grep `.cvf`, `roles/`), `.github/workflows/ci.yml` (dòng lệnh test), `skills/README.md` (dòng `inbox/`, `external/`).
**Không đọc:** code `.cvf/checks/**` (chỉ README), vectors.json, 21 ví dụ còn lại, `control_check.py` v1, hàm chuẩn hóa path v1 (S3-C phải đối chiếu, mục 2.2), evidence S1/S2. Không chạy test/checker/probe, agent phụ, AI CLI/API.

---

## 1. Delta so với owner v2

### 1.1 Version nào cần, và tương thích nào bị cấm

| Version | Cần? | Vì sao (không chỉ đổi literal) | Không được làm |
|---|---|---|---|
| `law.cvf.control/3` | **Cần** | `write_zone` thêm giá trị, thêm `condition`, thêm record `protection_overlay`, đổi `review.scope`, thêm trường task/review/result/effect (mục 4.7). Schema v2 có `const` literal và `unevaluatedProperties:false`: record v3 không hợp lệ dưới v2 và ngược lại | sửa tại chỗ schema v2; coi record v2 là v3 vì “gần giống” |
| `law.cvf.routing/3` | **Cần** | policy thêm `zone_map`, `write_zone_rank`, `authority_name_patterns`, `overlay_rules`; tách mệnh đề R-READ_DRAFT, thêm mệnh đề R-MUTATION/R-AUTHORITY_CHANGE. `policy_digest` băm toàn object policy ⇒ mọi binding đổi | giữ literal `/2` rồi thêm field; dùng hash policy cũ làm tương đương |
| `law.cvf.bind/3` | **Cần** | đổi **nghĩa** binding: anchor và tập phần so theo pha (4.2–4.3), `overlay_digest`, `outputs` có `role`, scope có tag; `action_digest` chỉ còn ở effect **với điều kiện Q-9** (1.3). Literal `bind` nằm trong từng projection nên digest đổi dù nội dung task giống hệt | so digest `bind/2` với `bind/3`; “nâng cấp” receipt v2 |
| `law.cvf.check/3` | **Cần** | từ vựng trạng thái gate, disposition `PASS` có phạm vi pha, `route`, `zones`, `actions`, `reviews`, `aggregate` (4.8). `check/2` của S1 không có `PASS` | bật `PASS` trong `check/2`; đổi nghĩa trường S1 |
| `evaluation_basis` | **Không đổi** `COOPERATIVE_WORKFLOW` [K] | Main không đổi cơ sở theo lần chạy | thêm basis mới trong D0 |

Quy tắc tương thích [P], cùng tinh thần [K] “từ chối, không diễn giải, không migrate”:
- Checker v3 chỉ nhận `schema_version = law.cvf.control/3`; bundle v2/v1/trộn ⇒ `UNSUPPORTED` (`SCHEMA_VERSION_UNKNOWN`/`VERSION_MIXED`), `details` gợi ý chọn `--contract v2`. Checker v2 đã nhận giữ nguyên và từ chối bundle v3 theo cùng đường.
- Chọn contract luôn tường minh, không suy từ record, không auto-discover, không fallback v2 khi v3 chặn **[M: một version hiệu lực được chọn tường minh ở tích hợp; không hai nguồn policy cùng có hiệu lực]**.
- Không migrate record/receipt/grant v2 sang v3; ví dụ v3 là bộ mới, không sửa `ex01–ex23` v2, không dùng lại `EXPECTED.json` v2. Grant v3 do user xác nhận lại theo nhóm việc (một lần, mục 2.7).
- Sửa v2 tại chỗ (vì chưa active) **không** khuyến nghị: mất baseline C1/S1/S2 và vi phạm D2.

### 1.2 Bảng delta

| # | Điều khoản hiện tại (v2) | Đề xuất (v3) | Lý do | Owner / version |
|---|---|---|---|---|
| Δ01 | `write_zone` ∈ {none, working, output_new, original_source, shared_register, framework, external, unknown} | thêm `agent_state`, `agent_runtime`, `package_content`. `archive/`, `assets/`, nguồn của user gộp `original_source` (nghĩa: dữ liệu user/project). `unknown` giữ trong enum chỉ như **khai** “Main không biết” ⇒ UNCLASSIFIED; **không** là hạng (mục 2.1) | tách authority/config khỏi state/runtime (brief D3) | schema `$defs/write_zone`, policy → control/3, routing/3 |
| Δ02 | `NO_PROTECTED_TARGET` chưa có định nghĩa vùng (C2-Q3) | policy v3 thêm `zone_map`, `write_zone_rank`, `light_write_zones=[working,output_new]`, `authority_name_patterns`, `overlay_rules`. `NO_PROTECTED_TARGET` tính trên **tập ghi** (read: rỗng) | thiếu thì R-READ_DRAFT không bao giờ khớp | policy, contract, rules → routing/3 |
| Δ03 | R-READ_DRAFT: một mệnh đề `ops [read,create_new]`, `zones [none,working,output_new]` | tách (A) read/`none`; (B) create_new/`working`; (C) create_new/`output_new` + `CONTENT_USE_INTERNAL_ONLY`; mỗi mệnh đề kèm `NO_PROTECTED_TARGET` | output không mặc định là nháp nội bộ [K] | policy → routing/3 |
| Δ04 | R-MUTATION không khớp `create_new` ở vùng không nhẹ ⇒ rơi R-UNCLASSIFIED | thêm mệnh đề `ops [create_new]`, `write_zones [agent_runtime, agent_state, package_content, original_source, shared_register]` | tạo mới nguồn/sổ/state cần đường hợp lệ có review | policy → routing/3 |
| Δ05 | R-AUTHORITY_CHANGE chỉ khớp theo `operations` | thêm mệnh đề `ops [create_new, overwrite, delete]`, `write_zones [framework]`; `authority_name_patterns` nâng bất kỳ ghi nào (kể cả `working/`) lên `framework` | sửa policy/code/entrypoint/profile dưới nhãn `overwrite` phải là authority | policy → routing/3 |
| Δ06 | `condition` thiếu điều kiện mục đích nội bộ | thêm `CONTENT_USE_INTERNAL_ONLY` (T: khai và mọi phần tử = `internal_draft`; F: có `sign/send_external/decision_basis/verified_claim`; U: vắng ⇒ UNCLASSIFIED) | Δ03(C) | schema `condition`, policy |
| Δ07 | không có record mở rộng bảo vệ theo project | `protection_overlay` (4.7.1) với quy tắc F5: `protect_more` chỉ nâng; `classify` chỉ cho phần baseline chưa phân loại, cần căn cứ user phù hợp | brief D3 | schema, contract → control/3 |
| Δ08 | binding v2: `action_digest` tùy chọn ở review/effect/result | `action_digest` **chỉ ở effect**; review/result khai coverage bằng occurrence (4.4). **Có điều kiện [M Q-9]:** chỉ có hiệu lực khi Main nhận biểu diễn coverage thay thế ở 3.3, 4.3, 4.4, 4.7; chưa nhận thì giữ `action_digest` tùy chọn như v2 (ngữ nghĩa S2) và veto theo 3.4 vẫn áp dụng | tách định danh phiên bản khỏi phạm vi phủ | contract 4.2, schema `binding` → bind/3, control/3 |
| Δ09 | `review.scope.objects` luôn là `object_digest` bytes file; ex02 gắn `accepted_task_digest` vào `path` | `scope.items[]` có tag `FILE_BYTES` \| `TASK_PROJECTION` (4.1); PASS cần phủ tối thiểu theo pha (3.3.3) | brief D5 | schema `review` |
| Δ10 | review không có kết luận từng yêu cầu | `requirement_conclusions[]`, `intent_mapping[]`, `source_scope_conclusions[]`, `scope.subject`, `scope.actions_checked` (occurrence) (4.7.2) | brief D4, F2, F4 | schema `review` |
| Δ11 | `result.user_acceptance_ref` chỉ có digest của lời xác nhận | `result.user_acceptance` gắn `task_id`/`task_revision`/`accepted_task_digest`, `accepted_requirements[]`, `result_id`, `accepted_artifacts[]` và tóm tắt đã trình (4.7.3); chỉ nhận cho REQUIREMENTS khi không đòi pha review | tiếp nhận phải gắn đúng task, đủ requirement bắt buộc, đúng bản; không thay review (D4) | schema `result` |
| Δ12 | `binding.outputs`/`artifacts` không phân biệt dự kiến/staged/thực | `role` ∈ `STAGED_BYTES` \| `ACTUAL_BYTES`; staged có `relation` (4.3); đường dẫn dự kiến chỉ ở `task.effects.expected_outputs` | không dùng kết quả dự kiến làm ACTUAL_OUTCOME | schema `effect`/`binding`/`result` |
| Δ13 | `reason_code` thiếu mã vùng/coverage/quan sát | thêm `PATH_ZONE_UNDETERMINED`, `REVIEW_COVERAGE_INCOMPLETE`, `OBSERVATION_UNAVAILABLE`; mã khác thuộc danh sách **do checker sở hữu** (4.8) | tránh phình enum [K S1] | schema `reason_code`; checks README → check/3 |
| Δ14 | contract 4.2 chỉ có projection `intent/task/context/action/policy` | thêm projection `overlay` (tập), `scope_item`; cập nhật UNSUPPORTED (4.9) | Δ07, Δ09 | contract v3 |
| Δ15 | rules v2 không nói vùng, review ngữ nghĩa, xác nhận user | rules v3: quy tắc 14–17 + bảng routing đọc theo Δ03–Δ05 | policy và bản đọc đổi cùng nhau [K] | rules v3 |
| Δ16 | output S1 `check/2` | `check/3` (4.8) | D6 | checks README v3, entry |
| Δ17 | `task.effects.actions[]` không có cờ hoàn thành; action không có định danh occurrence ở effect/result; `result.actions_performed` là mảng action đầy đủ | action thêm `completion ∈ {REQUIRED, OPTIONAL}` (vắng = `REQUIRED`, nằm trong projection ⇒ được bind); `effects.extra_review_phases[]` (chỉ siết, trong projection); `effect.action_index`; `result.actions_performed[]` = `{action_index, action_digest, effect_id}` (4.4, 4.7.3) | F2, F3, F6 | schema task/effect/result |

**Không đổi:** chín `row_id` và trigger gốc, `combine=UNION_OF_REQUIREMENTS`, `main_may_downgrade=false`, `unknown_handling=NEVER_ALLOW`, `unmatched_effect_route=R-UNCLASSIFIED`, `review_grants_authority=false`, `missing_required_reviewer`, `assurance_ceiling=ADVISORY`, `tamper_resistance=NONE`, `basis_change_per_run=FORBIDDEN`, `legacy_and_unknown_handling`, `unsupported_binding_part_handling`, `attributed_refs_required` của chín hàng, LAW-CJ/2, các projection `intent/task/context/action/policy` (chỉ đổi literal `bind`; `task` thêm hai trường tùy chọn Δ17), KNOWN_LOSS ⇒ DENY trước giao dịch, R-UNCLASSIFIED không bao giờ rơi về nhẹ. Không thêm digest riêng cho review/effect/result [K, F2].

### 1.3 Điều kiện nhận Δ08 (Q-9)

Bỏ `action_digest` khỏi binding review/result chỉ được nhận khi Main chấp nhận **cùng lúc**: occurrence (4.4), `scope.actions_checked`/`scope.subject` (4.7.2), phạm vi tối thiểu theo pha (3.3.3), anchor (4.2–4.3) và quy tắc veto theo phạm vi (3.4). Thiếu một trong các phần đó ⇒ giữ `action_digest` như v2.

---

## 2. Vùng bảo vệ và phép toán (C2-Q3)

### 2.1 Nguyên tắc (hạn chế thiết kế, không mô tả hiện trạng)

1. **Lexical ≠ quan sát.** S3 chỉ ra *kết luận lexical dựa policy* (`basis = POLICY_LEXICAL`, `fs_observation = NOT_OBSERVED`). Tồn tại, alias, link, hoa/thường thật thuộc S4/writer. Không claim S3 đóng race/TOCTOU.
2. **Đọc ≠ ghi.** Tập ghi của action = `targets` nếu `operation` ∉ {`read`, `delegate`}, ngược lại rỗng. Bảo vệ chỉ áp trên tập ghi; đọc nguồn trong `references/` không bị vùng chặn (vẫn qua GRANT_SCOPE/PATH_SCOPE).
3. **Chạy tool ≠ sửa tool.** `action.tool` là tên công cụ; `targets` mới là chỗ bị tác động. Grant chạy `tools/library.py` trên `references/` không phủ ghi `tools/**`. Grant liệt kê `tools/`, `.cvf/`… trong `scope.paths` với phép ghi **không** hạ vùng (grant chỉ thu hẹp hoặc bổ sung bảo vệ).
4. **Hạng chỉ xét giữa các phân loại có thật.** Thứ tự hạng: `none < working < output_new < agent_runtime < agent_state < package_content < original_source < shared_register < framework < external`. Vùng hiệu lực của một đường dẫn = hạng cao nhất trong các nguồn *đã phân loại* áp dụng: baseline, khai của action (chỉ nâng), `authority_name_patterns`, `protected_targets` của task (nâng tối thiểu lên `original_source`), `protect_more` của overlay. Hạng chỉ chọn “chặt hơn”; route do hàng routing quyết.
5. **UNCLASSIFIED/UNKNOWN là trạng thái chưa có phân loại, không phải hạng [M].** Nếu *không có nguồn phân loại nào* áp dụng cho một đường dẫn ghi ⇒ `UNCLASSIFIED` ⇒ R-UNCLASSIFIED (BLOCKED). Không có căn cứ user phù hợp thì vẫn BLOCKED. Chỉ overlay hợp lệ (2.7) mới được phân loại phần baseline thật sự chưa phân loại. Khai `write_zone = unknown` của action cũng là UNCLASSIFIED.
6. **Baseline là sàn.** Task, grant, overlay không hạ phân loại nào đã có; không thay phân loại vùng đã có; không đè bảo vệ ở descendant, mẫu tên authority, `protected_targets`, `protect_more`.
7. **Mâu thuẫn ⇒ UNCLASSIFIED:** op ghi mà vùng khai `none`; `read` mà vùng khai khác `none`.
8. **Dạng đường dẫn không chuẩn hóa được ⇒ UNSUPPORTED/UNKNOWN**, không suy an toàn từ chuỗi (2.2, 2.8).
9. **Vùng nhẹ chỉ là ứng viên** khi đủ mọi điều kiện ở 2.5.
10. **Output không mặc định được gửi đi.** Gửi/ký/dùng làm căn cứ vẫn theo R-EXTERNAL/R-HIGH_STAKES.

### 2.2 Chuẩn hóa đường dẫn (lexical)

Kế thừa đã nhận: dạng nào checker v1 từ chối chuẩn hóa thì v3 từ chối; **S3-C phải đối chiếu hàm chuẩn hóa v1 trước khi chốt** (D0 chưa đọc lại code v1). Đề xuất thêm ⇒ `PATH_UNSUPPORTED_FORM`: đoạn kết thúc `.` hoặc khoảng trắng; đoạn 8.3 (`~<số>`); tên thiết bị Windows; dấu `:` (ADS/ổ đĩa); `\\` đầu (UNC); đường tuyệt đối hoặc ra ngoài gốc project. So khớp theo **đoạn nguyên** sau `casefold`. Hai chuỗi khác nhau không coi là cùng file (contract 4.5).

### 2.3 Bảng A — đường dẫn → `write_zone` (đối chiếu từng mục gốc của cây LAW)

“Gói”: **U** = trong gói người dùng (dự kiến); **S** = chỉ kho nguồn. Khớp theo *cụ thể nhất thắng* **bên trong baseline**.

| Mẫu đường dẫn | Gói | `write_zone` | Owner nội dung | Cơ sở |
|---|---|---|---|---|
| `references/_INDEX.xlsx` | U | `shared_register` | `tools/library*.py`, skill `source-library` | sổ nguồn/ID/revision |
| `references/**` (còn lại), `archive/**`, `assets/**` | U | `original_source` | user/project | nguồn, bản cũ, tùy biến; không xóa archive khi chưa yêu cầu |
| `.cvf/**` | U | `framework` | bộ khung | quy tắc/quyền/cấu hình; `owner_protection = NOT_PROVEN` |
| `roles/**` | U | `framework` | bộ khung | hợp đồng vai, preset |
| `AGENTS.md`, `PROJECT.md`, `CLAUDE.md`, `GEMINI.md`, `en/AGENTS.md`, `en/PROJECT.md`, `en/CLAUDE.md`, `en/GEMINI.md`, `en/PROJECT_INSTRUCTIONS_SNIPPET.md` | U | `framework` | bộ khung / user (PROJECT) | chỉ dẫn agent và quyền theo project **[M Q-10: cấp file; hoãn tách theo mục]** |
| `skills/local/**`, `skills/README.md`, `packs/**`, `en/skills/**` | U | `framework` | bộ khung / user | skill/pack là chỉ dẫn hành vi; cài/export là `skill_install`/`skill_export` [K] |
| `skills/inbox/**`, `skills/external/**` | U | `package_content` | user | vùng tạm “không phải bước duyệt, không tự cách ly”; đặt file ≠ kích hoạt nhưng không coi nhẹ |
| `tools/**`, `APP.bat`, `APP.command`, `SETUP.bat`, `SETUP.command` | U | `framework` | bộ khung | mã chạy; sửa mã ≠ chạy mã |
| `MANIFEST.sha256`, `VERSION`, `.agent/PACKAGE_INFO.json`, `.agent/MERGE_STATUS.json` | U | `framework` | công cụ nâng cấp | nhận diện gói/nâng cấp |
| `.agent/SKILL_INDEX.md`, `.agent/EXECUTION_PROFILE.json` (dự kiến R4) | U | `framework` | bộ khung / user | trạng thái skill, cấu hình host/quyền là authority |
| `.agent/STATE.md`, `.agent/HANDOFF.md`, `.agent/PENDING_LESSONS.md`, `.agent/INDEX.md` | U | `agent_state` | agent (AGENTS quy tắc 8) | trạng thái/nhật ký; không authority (2.4) |
| `.agent/runtime/**` | U | `agent_runtime` | công cụ LAW | dữ liệu vận hành cục bộ |
| `.agent/**` (mọi file còn lại) | U | `framework` | bộ khung | mặc định bảo thủ của thư mục `.agent`, để overlay không phân loại nhầm file lạ trong đó |
| `.agent/README.md`, `docs/**`, `examples/**`, `README.md`, `CHANGELOG.md`, `LICENSE`, `START_HERE.html`, `START_HERE.en.html`, `en/**` (còn lại) | U | `package_content` | bộ khung | tài liệu/mẫu phân phối; không authority |
| `.github/**`, `tests/**`, `.gitignore`, `.gitattributes`, `release_templates/**` | S | `framework` | người duy trì | CI, mã kiểm, cấu hình repo; `release_templates` seed `PROJECT.md` (quyền) nên xếp authority **[M Q-10]** |
| `.git/**` | S | `framework` | VCS | ghi trực tiếp không được kỳ vọng; thao tác git là operation riêng |
| `roadmap/**`, `feedback/**`, `dist/**` | S | `package_content` | người duy trì | bảo trì/evidence/build; bảo trì LAW theo AGENTS/roadmap 8.3 |
| `working/**` | U | `working` | agent/user | nháp trung gian; ứng viên nhẹ **chỉ khi tạo mới** |
| `output/**` | U | `output_new` | agent/user | deliverable hiện hành; ứng viên nhẹ **chỉ khi tạo mới** và khai nội bộ |
| thư mục user khai “Ngoại lệ thư mục nguồn cũ” trong PROJECT | U | `original_source` (qua overlay, 2.7) | user | nguồn cũ giữ tại chỗ |
| mọi đường dẫn khác (thư mục mới ở gốc, file lẻ ở gốc) | — | **UNCLASSIFIED** (không có phân loại) | — | BLOCKED cho ghi; đọc theo grant; chỉ overlay hợp lệ mới phân loại |
| ngoài thư mục gốc project (kể cả thư mục skill của host, cấu hình global) | — | `PATH_UNSUPPORTED_FORM` | — | host/global/ACL ngoài phạm vi; export skill qua `skill_export` [K] |

Ghi chú phân phối: `.cvf/**` và `roles/**` hiện **chưa** nằm trong `MANIFEST.sha256` (quyết định phân phối thuộc G-04/Integration); bảng áp cho project có các cây đó.
Thay đổi PROJECT/entrypoint do adapter dựng cho user hiểu (mô tả việc đổi bằng lời thường); adapter **không** tự cấp thêm grant **[M Q-10]**.

**Mẫu tên authority** (so basename sau `casefold`, áp dụng ở mọi vùng kể cả `working/`, `output/`, nâng lên `framework`): `agents.md`, `project.md`, `claude.md`, `gemini.md`, `routing_policy*.json`, `*.schema.json`, `control_rules*.md`, `control_contract*.md`, `execution_profile*.json`, `skill.md`, `pack.json`, `manifest.sha256`, `*.grant.json`, `grant*.json`. Sàng lexical bảo thủ (có thể chặn nhầm tên trùng ⇒ user đổi tên); không phát hiện nội dung.

### 2.4 `.agent/` — tách authority/config khỏi state, runtime, evidence

| Nhóm | Ví dụ | Vùng | Route |
|---|---|---|---|
| Authority/config | `EXECUTION_PROFILE.json`, `SKILL_INDEX.md`, `PACKAGE_INFO.json`, `MERGE_STATUS.json`, file lạ trong `.agent/` | `framework` | R-AUTHORITY_CHANGE |
| State | `STATE.md`, `HANDOFF.md`, `PENDING_LESSONS.md`, `INDEX.md` | `agent_state` | R-MUTATION (hai pha review) |
| Runtime | `.agent/runtime/**` | `agent_runtime` | R-MUTATION; ghi đè/xóa evidence đã có luôn nặng |
| Evidence/receipt | `.agent/runtime/governance` (dự kiến), `roadmap/evidence/**` (S) | `agent_runtime` / `package_content` | như nhóm tương ứng; receipt thật chưa tồn tại |

**[M Q-3] Giới hạn candidate tạm thời.** State/runtime đi R-MUTATION vì chưa có protocol/recipe; D0 **không** tự nhận recipe và không miễn gate. Hệ quả: nếu checker v3 nối vào ghi STATE/HANDOFF thì mọi ghi đè phải qua hai pha review. Vì vậy **protocol/recipe cho state/runtime là phụ thuộc bắt buộc trước khi tích hợp luồng đó**; không phát hành mặc định gọi Reviewer cho mỗi lần ghi STATE (mục 5.4). Cho tới lúc đó AGENTS quy tắc 8 là quy tắc hợp tác, checker chưa nối vào công cụ nào.

### 2.5 Bảng B — `write_zone` × operation → route

`NPT` = `NO_PROTECTED_TARGET`, `CUI` = `CONTENT_USE_INTERNAL_ONLY`.

| Vùng hiệu lực | `read` | `create_new` | `overwrite` / `delete` | `register_write` / `provenance_write` |
|---|---|---|---|---|
| `none` | R-READ_DRAFT | — (mâu thuẫn ⇒ UNCLASSIFIED) | — | — |
| `working` | — | **R-READ_DRAFT nếu NPT** (route CONDITIONAL, 3.1) | R-MUTATION | R-MUTATION |
| `output_new` | — | **R-READ_DRAFT nếu NPT ∧ CUI** (CONDITIONAL); vắng content_use ⇒ UNCLASSIFIED; có `sign/send/decision/verified` ⇒ không nhẹ, hợp thêm R-HIGH_STAKES | R-MUTATION | R-MUTATION |
| `agent_runtime`, `agent_state`, `package_content` | — | R-MUTATION (Δ04) | R-MUTATION | R-MUTATION |
| `original_source`, `shared_register` | — | R-MUTATION (Δ04) | R-MUTATION | R-MUTATION |
| `framework` | — | **R-AUTHORITY_CHANGE (Δ05)** | **R-AUTHORITY_CHANGE + R-MUTATION** (hợp) | R-MUTATION (+ AUTHORITY nếu op thuộc danh sách authority) |
| `external` | — | UNCLASSIFIED (D0 không mở rộng R-EXTERNAL) | UNCLASSIFIED | UNCLASSIFIED |
| UNCLASSIFIED | — | R-UNCLASSIFIED ⇒ BLOCKED | R-UNCLASSIFIED | R-UNCLASSIFIED |
| mọi vùng | `skill_install`/`skill_export`/`grant_write`/`schema_or_policy_write`/`verification_status_write` ⇒ R-AUTHORITY_CHANGE; `external_send`/`network_write`/`irreversible_other` ⇒ R-EXTERNAL; `delegate` ⇒ R-DELEGATE; `unknown` ⇒ R-UNCLASSIFIED; `KNOWN_PRESERVATION_LOSS` ⇒ R-KNOWN_LOSS (DENY) | | | |

Hợp hàng giữ [K].

**Điều kiện đường nhẹ cho ghi — đồng thời:**
(1) operation hiệu lực `create_new` — khai, *chưa quan sát* ⇒ giả định mở **A-NEW_TARGET** (route `CONDITIONAL`, 3.1); (2) mọi `targets` chuẩn hóa được, vùng hiệu lực ∈ {`working`, `output_new`};
(3) đích chưa tồn tại — *quan sát* của S4 (chỉ nói về thời điểm quan sát; proof lịch sử cho accept: 4.3.1) và writer; S3 để `UNKNOWN`; (4) có grant `USER_CONFIRMATION` phủ op/tool/path;
(5) không tạo/sửa authority: tên không khớp mẫu authority, `operation` không thuộc danh sách authority, nguồn quyền không đặt trong vùng ghi được (2.6);
(6) `output_new` ⇒ `content_use` khai và chỉ `internal_draft` — **[M Q-5]** dùng lại ý định user đã biết từ hội thoại/grant, không hỏi lại nếu đã đủ rõ; (7) không điều kiện route nặng khác (KNOWN_LOSS, ENVELOPE_EXCEEDED, UNCLASSIFIED, protected_targets).
Thiếu bất kỳ điều kiện nào ⇒ không nhẹ. Điều kiện (3) chưa quan sát ⇒ route `CONDITIONAL` ⇒ **BLOCKED** (3.1), không PASS có điều kiện.

### 2.6 Authority nằm trong vùng ghi được

- Lời khai nguồn quyền có `channel = USER_AUTHORED_FILE` mà `locator`/`evidence_locator` nằm dưới `working/`, `output/`, `.agent/` state/runtime (nơi Main/Worker ghi được) **không** được nhận là `USER_CONFIRMATION` ⇒ `USER_CONFIRMATION_MISSING` (grant/intent) hoặc `REVIEWER_NOT_ELIGIBLE` (eligibility). `source_class` và `channel` là hai thuộc tính khác nhau: bảng/phác thảo luôn ghi riêng. `USER_MESSAGE`, `HOST_CONFIRMATION_UI` không bị ảnh hưởng.
- Tạo/sửa file có tên khớp mẫu authority ở bất kỳ vùng nào ⇒ `framework`.

### 2.7 Mở rộng theo project (overlay) và UX người dùng phổ thông

**Phân biệt hai tác dụng của `protection_overlay` [P, F5]:**

| Tác dụng | Điều kiện | Căn cứ nguồn |
|---|---|---|
| `protect_more`: nâng hạng đường dẫn lên `original_source`/`shared_register`/`framework` | luôn hợp lệ (chỉ siết); đè được phân loại baseline ở hạng thấp hơn | `source_class` bất kỳ ngoại trừ `UNVERIFIED` (Main đề xuất siết là được); guard nguồn hiện hành vẫn chạy |
| `classify`: cấp phân loại `working`/`output_new` cho đường dẫn **chưa có phân loại baseline** | (a) prefix không rỗng, không là tổ tiên hay nằm trong baseline reserved root (`.agent/`, `.cvf/`, `roles/`, `references/`, `skills/`, `packs/`, `tools/`, `docs/`, `en/`, `assets/`, `archive/`, `examples/`, `release_templates/`, `tests/`, `roadmap/`, `feedback/`, `dist/`, `.git/`, `.github/`, `working/`, `output/` và file lẻ ở gốc có tên trong bảng A); (b) không có phân loại *nặng hơn* từ bất kỳ nguồn nào áp lên đường dẫn hoặc descendant của nó (authority pattern, `protected_targets`, `protect_more`) — nguồn nặng hơn thắng theo 2.1.4; (c) không đổi hạng nào đã có | **bắt buộc** `source_class = USER_CONFIRMATION` với `channel ∈ {USER_MESSAGE, HOST_CONFIRMATION_UI}` và `evidence_locator`. `USER_AUTHORED_FILE` **không** đủ để mở vùng nhẹ (file ghi được bởi Main). Main ghi overlay **không** thành quyền tự mở vùng nhẹ |

Entry `classify` vi phạm (a)–(c) bị **bỏ qua** (không hạ), ghi `OVERLAY_ENTRY_IGNORED(OVERLAY_LOWERS_BASELINE | OVERLAY_PREFIX_RESERVED)`; đường dẫn vẫn nặng/BLOCKED như trước. Overlay bị bỏ qua một entry không làm các entry hợp lệ khác mất hiệu lực.

**Nhiều overlay / mâu thuẫn / prefix chồng (không chọn “mới nhất”):**
- Overlay xác định bởi `overlay_id`; hai record cùng `overlay_id` (kể cả khác `overlay_revision`) ⇒ **AMBIGUOUS** ⇒ toàn bộ tập overlay `UNSUPPORTED` ⇒ phần phụ thuộc BLOCKED [K S2: không latest].
- Các overlay `overlay_id` khác nhau được hợp: `protect_more` hợp tập; `classify` cho cùng đường dẫn: prefix dài nhất áp dụng; hai entry cùng độ dài prefix khác `write_zone` ⇒ hạng cao hơn; `protect_more` luôn thắng `classify` ở chỗ giao.
- `overlay_digest` băm **tập** các overlay hợp lệ (id, revision, projection); đổi tập ⇒ đổi digest.

**Luồng cho người dùng phổ thông** (agent/công cụ dựng record; user trả lời câu hỏi nghiệp vụ, không đọc tên gate/JSON):

| Tình huống | Agent/công cụ làm | User chỉ phải trả lời |
|---|---|---|
| đọc/khảo sát tài liệu | route đã resolve, không hỏi | không |
| “Soạn bản nháp” (ghi mới) | dựng task tối thiểu + grant nhóm sẵn có; chờ S4 xác nhận đích chưa tồn tại (3.1) | (có grant) không hỏi gì; (chưa có) “Cho phép tôi tạo bản nháp trong thư mục làm việc từ nay chứ?” một lần |
| bản giao vào `output/` | lấy `content_use` từ ý định đã biết **[M Q-5]** | chỉ hỏi khi chưa rõ: “nội bộ xem hay trình ký/gửi ra ngoài?” |
| việc đụng `references/` hoặc sổ | nêu phạm vi, cần xác nhận + soát độc lập | “Việc này sửa tài liệu nguồn/sổ nguồn, bạn đồng ý chứ? Tôi sẽ nhờ một lượt soát độc lập” |
| việc đụng chỉ dẫn/quy tắc/hồ sơ dự án | dừng, mô tả việc đổi bằng lời thường **[M Q-10]** | “Việc này đổi quy tắc/quyền của dự án; cần bạn xác nhận riêng và soát độc lập” |
| thư mục lạ chưa phân loại | không đoán | “Thư mục X là tài liệu gốc cần giữ, hay là nơi làm nháp?” → overlay (`classify` chỉ khi trả lời trực tiếp của user) |
| thiếu Reviewer | báo phần chờ, không tự duyệt | “Chưa có người soát độc lập nên phần này chờ; phần đọc độc lập vẫn làm tiếp” |
| bản mới trùng tên bản có sẵn | dùng tên mới (AGENTS quy tắc 3) | không hỏi — **nhưng** xem **[M Q-4]** ở 5.4: đây chưa phải UX cuối cho sửa nháp lặp |

Ánh xạ mã lý do → lời cho user thuộc lớp tích hợp (mục 5), checker không sinh văn bản hướng dẫn.

### 2.8 UNKNOWN/UNSUPPORTED và tách lexical khỏi quan sát

| Điều kiện | S3 (lexical, bộ nhớ) | S4/writer (quan sát, sau) |
|---|---|---|
| vùng của đường dẫn | `zone` + `basis=POLICY_LEXICAL` | đoạn đúng hoa/thường, không reparse |
| đích đã tồn tại? | `target_existence = UNKNOWN` ⇒ giả định A-NEW_TARGET mở | quan sát read-only **tại thời điểm d/e** (lstat); mâu thuẫn tại d/e ⇒ route lại `overwrite`. **Không** áp cho accept sau khi tạo thành công: proof lịch sử + liên kết thao tác do writer/protocol (4.3.1) |
| alias, link, junction, 8.3, ADS, UNC, `..` | `UNSUPPORTED` (hình thức) hoặc `UNKNOWN` (tồn tại) ⇒ chặn phần phụ thuộc | quan sát thật |
| gốc project | chuỗi tương đối so với gốc đã khai | root/ancestors |
| đọc ra ngoài gốc / qua link | grant + `PATH_UNSUPPORTED_FORM`; `limits=[ALIAS_NOT_EXCLUDED]` | quan sát thật |
| race kiểm–ghi | **không claim** | writer protocol (ngoài D0) |

---

## 3. Gate × pha, mức căn cứ, semantic review

### 3.1 Từ vựng, route và quy tắc tổng hợp

Trạng thái gate (check/3): `MET`, `NOT_MET`, `NOT_CHECKED` (đến hạn nhưng thiếu quan sát/dữ kiện), `UNSUPPORTED`, `NOT_YET_DUE`, `NOT_REQUIRED`, và hai trạng thái dương chỉ cho gate ngữ nghĩa: `REVIEW_COVERED` (REQUIREMENTS, SOURCE_SCOPE_AND_CONCLUSION) và `USER_ACCEPTED_DECLARED` (chỉ REQUIREMENTS khi route/task **không** đòi pha review — 3.5). Cả hai nghĩa là có căn cứ hợp tác phủ đủ phạm vi **theo lời khai**; không là máy xác minh nội dung.

**Route.** `route.status`:
- `RESOLVED`: mọi điều kiện route xác định từ record + policy, không giả định mở.
- `CONDITIONAL`: route tính được **với** ít nhất một giả định mở có chủ quan sát (ví dụ A-NEW_TARGET).
- `UNRESOLVED`: có điều kiện không xác định (⇒ R-UNCLASSIFIED).

**Quy tắc tổng hợp [M F1]:**

**Main sửa hẹp sau review Rev 2, 18/10:** bảng dưới liệt kê điều kiện, không phải thứ tự ưu tiên từ trên xuống.
Sau khi qua preflight cấu trúc/version/basis để đánh giá được policy, một lý do cưỡng bức DENY
đã được xác định (`KNOWN_PRESERVATION_LOSS` hoặc veto áp dụng) luôn ưu tiên trước BLOCKED
do route CONDITIONAL/UNRESOLVED hoặc gate thiếu. Lỗi init/version/structure vẫn theo nhánh preflight,
không đoán verdict policy trên dữ liệu chưa đánh giá được.

| Điều kiện | Disposition |
|---|---|
| route `CONDITIONAL` hoặc `UNRESOLVED` | **BLOCKED**, ở **mọi pha kể cả dispatch** |
| gate đến hạn `NOT_MET` | BLOCKED; DENY khi lý do cưỡng bức (`REVIEW_BLOCKING_VERDICT`, `KNOWN_PRESERVATION_LOSS`) |
| gate đến hạn `NOT_CHECKED`/`UNSUPPORTED` | BLOCKED; `UNSUPPORTED` cấp *record* (version/basis/canonical) ⇒ aggregate `UNSUPPORTED` [K S1] |
| route `RESOLVED` ∧ mọi gate đến hạn ∈ {`MET`, `REVIEW_COVERED`, `USER_ACCEPTED_DECLARED`, `NOT_REQUIRED`} | `PASS` với `phase_scope` = pha đang xét; `effect_authorized=false`; `assurance_level=ADVISORY`. PASS ở một pha không là căn cứ cho pha khác |

Khi BLOCKED vì route điều kiện, output vẫn báo riêng: phần record đã kiểm (`records_checked_state`, từng gate), danh sách giả định mở, pha cần proof, owner proof (`S4`). **Không tạo nhãn dương khác** thay cho BLOCKED. Một giả định chỉ được đóng bởi **observer S4 chạy trong cùng lượt đánh giá** (kết quả OBSERVED), không bởi record `TOOL_OBSERVATION` hay khai báo trong bundle; sau khi S4 đóng, checker tính lại route (có thể thành `RESOLVED`).

Disposition tính **theo từng action** (`actions[]`) rồi tổng hợp. Một action bị chặn bởi **gate riêng của nó** (grant/path/tool/envelope/precondition) không đổi kết luận gate riêng của action khác, nhưng aggregate không PASS. Việc đọc/nháp *thực sự* độc lập tiếp tục [K `independent_read_draft_continues`] khi độc lập có **căn cứ dương**: giữa các task khác nhau, hoặc ở gate riêng của từng action. Veto và thiếu review mức task (3.4) chặn **toàn task ở pha đó**; không suy độc lập từ target/payload khác nhau (D3).

### 3.2 Bảng gate × pha

d = dispatch, e = effect, a = accept. Mức: D/C/R/O như đầu tài liệu. “S3 cung cấp” = mức đạt được không cần S4. **Gate nào đến hạn do task + route + pha quyết (mục 3.5), không do claim của result.**

| Gate | Đến hạn | Căn cứ cần để `MET` | S3 cung cấp | Không có thì | Proof ngoài S3 |
|---|---|---|---|---|---|
| GRANT_SCOPE, GRANT_EXACT_COVERAGE | d e a (chạy lại mỗi pha) | C: mỗi `grant_ref` resolve đúng 1 grant ACTIVE (không `example_only`); subject chứa **actor của pha**; op/tool/target ⊂ scope. D: `source_class` ∈ policy (`USER_CONFIRMATION`) + kênh + `evidence_locator` | C + D | `GRANT_MISSING/INACTIVE/OUT_OF_SCOPE`, `USER_CONFIRMATION_MISSING`, `ATTRIBUTION_INSUFFICIENT` ⇒ BLOCKED; `limits.expires_at` ⇒ `UNSUPPORTED` (thời gian) | attribution `NOT_PROVEN` |
| PATH_SCOPE | d e a | R: vùng lexical (2.3) + C: target ⊂ grant paths. **Ghi:** O (thời điểm quan sát): `target_existence`, dạng path thật; **a:** proof lịch sử precondition gắn request/occurrence (4.3.1) | R + C; `target_existence=UNKNOWN` | **ghi** (create_new): route `CONDITIONAL` (A-NEW_TARGET) ⇒ BLOCKED ở d e a cho tới khi S4 đóng **ở d/e** (observation-at-time, kèm `limits=[EXCLUSIVE_WRITE_NOT_PROVEN, RACE_NOT_EXCLUDED]`). Ở **a** không kiểm “đích hiện không tồn tại” cho action đã tạo thành công; đòi proof lịch sử, thiếu ⇒ `UNSUPPORTED(PRECONDITION_PROOF_MISSING)` ⇒ BLOCKED. **Đọc [M Q-7]:** `MET` lexical/declared kèm `limits=[ALIAS_NOT_EXCLUDED, EXISTENCE_NOT_OBSERVED, SOURCE_READ_NOT_OBSERVED]`; **không** suy nguồn đã đọc thật/đúng revision hay mở quyền gửi dữ liệu; gate cần bytes/nguồn thật vẫn chặn khi thiếu proof | S4 (thời điểm d/e); writer/protocol (proof lịch sử cho a) |
| TOOL_SCOPE | d e a | C: `action.tool` ∈ `grant.scope.tools` (chuỗi) | C | tool lạ ⇒ `GRANT_OUT_OF_SCOPE`; tên tool không là năng lực/recipe | — |
| ENVELOPE | d e a | C: số học `max_retries`, `max_concurrency`, `cost_limit`, vai ∈ nhóm; D: giá trị khai | C + D | thiếu envelope khi có limit ⇒ `NOT_CHECKED(ENVELOPE_UNMEASURED)`; `expires_at` ⇒ `UNSUPPORTED`; `RETRY_UNRECONCILED` (4.4) | host đo (ngoài) |
| BINDING | e a (d: `NOT_YET_DUE`) | R: `intent/accepted_task/context/policy/overlay` tính lại; C: `inputs/outputs/action_digest` theo anchor (4.2–4.3); literal `bind_version/evaluation_basis/policy_version` | R + C (S2) | lệch ⇒ `BINDING_MISMATCH`+`parts`; phần chưa định nghĩa ⇒ `UNSUPPORTED_BINDING_PART`. `MET` luôn kèm `limits=[FILE_BYTES_DECLARED_ONLY]` | bytes thật: INPUT_REVISION/ACTUAL_OUTCOME |
| INPUT_REVISION | e a | C: `binding.inputs` = `task.inputs` (và inputs của review theo anchor); **O**: input *không* là target: bytes hiện tại khớp digest; input **là target** của action: bytes *trước tác động* gắn `E_req`/occurrence khớp digest (proof lịch sử, mang sang accept — 4.3.1), bytes sau ghi so với output riêng | C | hàng đòi (R-MUTATION, R-AUTHORITY_CHANGE, R-RECIPE) ⇒ `NOT_CHECKED(OBSERVATION_UNAVAILABLE)`; input là target thiếu proof trước ghi ⇒ `NOT_CHECKED`/`UNSUPPORTED(PRECONDITION_PROOF_MISSING)`; **không** thay bằng lời khai C | S4 + writer/protocol |
| PRESERVATION | e a (KNOWN_LOSS ⇒ DENY từ route) | D: `known_loss_state`; **O/writer**: biên bản bảo toàn | D; `create_new` vùng nhẹ: không liệt kê ở R-READ_DRAFT | `KNOWN_LOSS` ⇒ DENY trước giao dịch; ghi đè/sổ/provenance không quan sát ⇒ `UNSUPPORTED(PRESERVATION_UNKNOWN)`; `NONE_KNOWN` tự khai không đủ | writer A-06 (x14), S4 |
| RECIPE_VERSION_ACCEPTED | d e a | định dạng bản recipe đã nhận chưa tồn tại (C2-Q4) | — | có `action.recipe` ⇒ `UNSUPPORTED`; không recipe ⇒ `NOT_MET`; R-RECIPE không PASS | tranche recipe |
| DELEGATE_SCOPE | d e (a: `NOT_YET_DUE`) | C+R: callee ∈ `delegate_callees`; `tool_scope` đủ 3 mảng; con ⊂ grant ∩ cha; pointer cha/con resolve và tính lại | C + R (core) | `registered`/`domain_accepted` ⇒ `UNSUPPORTED`; thiếu binding effect/record con ⇒ `NOT_CHECKED(DELEGATE_SCOPE_UNVERIFIED)`; task chỉ-context (ex19) ⇒ `UNSUPPORTED` | Q5, ex19 |
| REVIEW[PRE_EFFECT] | e a — **chỉ khi** pha có trong hợp policy áp dụng ∪ `effects.extra_review_phases` (3.3.4) | `REVIEW_SUFFICIENT` (3.3) | C + D | `REVIEW_MISSING`, `REVIEWER_NOT_ELIGIBLE`, `REVIEW_COVERAGE_INCOMPLETE`, `REVIEW_BLOCKING_VERDICT`; Main không tự duyệt | Reviewer thật |
| REVIEW[PRE_INTEGRATION], REVIEW[PRE_DELIVERY] | a — cùng điều kiện đòi | như trên, phase tương ứng | C + D | như trên | Reviewer thật |
| REQUIREMENTS (checker-owned) | **a, mọi task có yêu cầu `mandatory`** (task nào cũng có ≥1 requirement) | `REVIEW_COVERED` theo 3.3 nếu pha review áp dụng; nếu **không** pha review nào được đòi (policy ∪ extra): `USER_ACCEPTED_DECLARED` **chỉ khi** `result.user_acceptance` đạt đủ D4 (4.7.3): gắn đúng `task_id`/`task_revision`/`accepted_task_digest` hiện hành, `accepted_requirements` ⊇ mọi requirement `mandatory` hiện hành, `result_id` và `accepted_artifacts` = `result.artifacts` đúng bản | D | thiếu ⇒ `NOT_CHECKED(EVIDENCE_NOT_VERIFIED)`; chỉ phủ một phần ⇒ phần chưa phủ `NOT_CHECKED` ⇒ BLOCKED (`USER_ACCEPTANCE_INCOMPLETE`); gắn task/artifact cũ ⇒ `USER_ACCEPTANCE_STALE`; grant làm việc, lời “đã nhận file”, im lặng ⇒ không đủ; claim cao hơn bằng chứng ⇒ `ACCEPTANCE_CLAIM_NOT_SUPPORTED`; **không bao giờ** `requirements_semantic_verified=true`; không thay review/veto/bytes/preservation | review/user thật |
| SOURCE_SCOPE_AND_CONCLUSION | a (R-HIGH_STAKES) | PRE_DELIVERY `REVIEW_SUFFICIENT` + `source_scope_conclusions` phủ mọi mục nguồn nội dung dựa vào | D (qua review) | `NOT_MET`/`NOT_CHECKED`; `REVIEW_COVERED` kèm `not_checked` của review | review; thư viện nguồn (`source-library`) |
| ACTUAL_OUTCOME (+ tính đủ/reconcile action, 4.4) | a, **khi** task có action ghi `REQUIRED`, **hoặc** bất kỳ occurrence (kể cả `OPTIONAL`) có OUTCOME hoặc được khai đã thực hiện, **hoặc** hàng route liệt kê | C: effect OUTCOME ↔ `result.actions_performed` ↔ `result.artifacts` ↔ `binding.outputs` (EXACT, 4.4); hoàn tất mọi occurrence `REQUIRED`; **O**: bytes artifact hiện tại; **proof lịch sử + liên kết thao tác** (4.3.1) | C | `NOT_CHECKED(OBSERVATION_UNAVAILABLE)`; thiếu proof lịch sử/liên kết ⇒ `UNSUPPORTED(PRECONDITION_PROOF_MISSING)`; REQUIRED chưa làm ⇒ `ACTION_INCOMPLETE`; OPTIONAL đã làm/khai ⇒ kiểm đầy đủ như REQUIRED; external ⇒ `UNSUPPORTED` | S4 (bytes hiện tại); writer/protocol (lịch sử, liên kết); external không có |
| SKILL_INTAKE_STANDARD | e a (R-AUTHORITY_CHANGE) | owner `skills/README.md`, `pack.py`, `install_skills.py` | — | luôn `NOT_CHECKED(OUT_OF_CHECKER_SCOPE)` | người dùng |
| Guard hiện hành mỗi pha: lớp attribution, actor, reviewer, context, parent, policy, overlay | d e a | contract 4.2 “các kiểm tra độc lập với digest” | C + R + D | BLOCKED; `host/session_ref` chỉ điều kiện khi envelope/profile ràng buộc tường minh (khi đó `UNSUPPORTED`) | — |

### 3.3 Review ngữ nghĩa (C2-Q7, D4, F2, F3)

**3.3.1 Phạm vi nhận.** Review hợp tác độc lập là căn cứ có giới hạn cho REQUIREMENTS và SOURCE_SCOPE; là *lời khai review có attribution*, không phải xác minh máy. `verdict=PASS`, `ROLE_REPORT` hay digest khớp tự chúng không đủ.

**3.3.2 Hai lớp tách biệt.**

*Lớp 1 — đủ tư cách của từng review (QUAL).* Review R là **component hợp lệ đóng góp coverage dương** cho chủ thể S, pha P khi và chỉ khi `R.verdict = PASS` và đạt **tất cả** điều kiện a–f dưới đây. Non-PASS vẫn được xét veto theo 3.4; việc không đạt QUAL không làm mất veto còn áp dụng.

| # | Điều kiện | Kiểm gì | Mức |
|---|---|---|---|
| a | đúng pha | `R.phase = P` | C |
| b | đúng task | `task_id`, `task_revision` khớp record task resolve đúng 1 | C |
| c | **anchor + binding đúng pha** | tập phần binding của pha P khớp (4.2–4.3): phần chung bắt buộc (task id/revision, intent, accepted_task, context, policy, overlay (cả vắng/có), inputs) **và** phần riêng theo anchor của P. Một phần lệch ⇒ review *không áp dụng* (không phải stale theo thời gian) | R + C |
| d | đúng actor | `role=reviewer`; khác `proposed_by`, `effect.actor`, `produced_by`, `state_set_by`; khác `session_ref` khi cả hai có | D + C |
| e | căn cứ vai riêng (**khác** `context_digest`) | `eligibility_ref.attribution.source_class` ∈ {`USER_CONFIRMATION`, `TOOL_OBSERVATION`} theo policy **và** `independence_observed = OBSERVED_SEPARATE_CONTEXT`. Hai bậc: **TOOL** (`TOOL_OBSERVATION`, `observed_by` role tool/host) hoặc **USER** (user chỉ định, kể cả Reviewer ngoài host). Output ghi `reviewer_basis ∈ {TOOL_ATTRIBUTED, USER_DESIGNATED, NONE}`; vẫn `semantic_verified=false` | D |
| f | nhất quán nội bộ | `verdict=PASS` nhưng có kết luận phủ định/unknown trong phần khai đã kiểm theo bảng dưới ⇒ `REVIEW_INCONSISTENT`, tính như non-PASS. Không chỉ kiểm enum của requirement rồi bỏ sót enum intent/source. | C |

**Main làm rõ enum sau review Rev 2 (chỉ phạm vi review khai đã kiểm):**

| Trường | Phủ định/không xác định làm PASS mâu thuẫn | Chưa phủ, không tự là veto |
|---|---|---|
| `requirement_conclusions.conclusion` | `NOT_MET`, `UNKNOWN` | `NOT_CHECKED` |
| `intent_mapping.mapping` | `NOT_FAITHFUL`, `UNKNOWN` | `PARTIAL` |
| `source_scope_conclusions.status` | `NOT_SUPPORTED` | `NOT_CHECKED` |
| source `examined` / item `coverage` | Khai đồng thời đã FULL/MET/FAITHFUL/SUPPORTED trọn mục nhưng dữ liệu cùng mục chỉ PARTIAL/NOT_READ là mâu thuẫn; không đoán UNKNOWN không tồn tại trong enum | `PARTIAL`, `NOT_READ` không đóng góp phủ trọn mục |

Phần chưa phủ phải xuất hiện trong chẩn đoán coverage, không bị đổi thành bằng chứng dương.
Review PASS khác có thể bù phần NOT_CHECKED/PARTIAL hợp lệ; không bù để gỡ INCONSISTENT/veto.

Review không thỏa a–f **không tạo PASS** và không đóng góp coverage. Review thỏa a–f chỉ đóng góp **phần nó khai đã kiểm** (mục 3.3.3): kết luận `MET` cho yêu cầu trong `requirements_checked`, item scope hợp lệ, occurrence trong `actions_checked`, mục nguồn `SUPPORTED`. `NOT_CHECKED`/`UNKNOWN` không đóng góp coverage (cũng không phải mâu thuẫn nếu review đó không khai đã kiểm phần ấy).

*Lớp 2 — độ phủ của cả tập (COVERAGE).* `REVIEW_SUFFICIENT(S, P)` đúng khi **hợp** đóng góp của mọi component hợp lệ cho P phủ **đủ** phạm vi bắt buộc của P (bảng 3.3.3) **và** không có veto áp dụng (3.4). **Không** đòi mỗi review tự phủ mọi yêu cầu. Coverage dư không bù coverage thiếu; thiếu một phần bắt buộc ⇒ `REVIEW_COVERAGE_INCOMPLETE`. S2 `COVER` chỉ là nguyên liệu so sánh path/digest/qualifier, không tự kết luận review đủ.

**3.3.3 Phạm vi tối thiểu theo pha** (union của component hợp lệ phải phủ **tất cả**):

| Pha | Bắt buộc phủ | Cách phủ | Không đủ |
|---|---|---|---|
| PRE_EFFECT | (1) **accepted task**: item `TASK_PROJECTION(part=accepted_task)` đúng task_id/revision; (2) **ánh xạ intent→yêu cầu**: `intent_refs_checked` ⊇ mọi `task.intent.refs[].ref_id`, và `intent_mapping[]` có entry `FAITHFUL` cho **mỗi** requirement `mandatory`; nếu `intent.unconfirmed` không rỗng thì `unconfirmed_checked` ⊇ mọi chỉ số; (3) **action**: `actions_checked` ⊇ occurrence của action được xét (4.4); (4) staged outputs (nếu có ở request): item `FILE_BYTES` FULL cho từng staged | như cột “Bắt buộc” | một `TASK_PROJECTION(context)` hoặc `FILE_BYTES` bất kỳ; binding khớp một mình (nhận dạng phiên bản, không chứng minh đã xét mapping ý định→task) |
| PRE_INTEGRATION | (1) **artifact thực**: item `FILE_BYTES` FULL phủ **từng** artifact ở `binding.outputs` ∧ `result.artifacts`; (2) `requirement_conclusions` có `MET` cho **mỗi** requirement `mandatory`; (3) occurrence đã thực hiện (`actions_performed`) được review xét (`actions_checked` ⊇ occurrence `REQUIRED`) | như trên | artifact thừa ngoài outputs không cộng coverage |
| PRE_DELIVERY | (1) item `FILE_BYTES` FULL phủ từng artifact giao; (2) `source_scope_conclusions` `SUPPORTED` cho mọi mục nguồn nội dung dựa vào, `limits` nêu phần chưa đối chiếu | như trên | `examined=PARTIAL` cho nguồn dựa vào ⇒ chưa phủ |

Binding khớp chỉ nhận dạng phiên bản; ánh xạ intent→yêu cầu và độ phủ luôn do **nội dung review** chứng, ở mức DECLARED.

**3.3.4 Review nào được đòi [M F3].** Pha review đòi = hợp `required_review_phases` của mọi hàng route áp dụng ∪ `effects.extra_review_phases` của task (chỉ siết, nằm trong projection nên được bind). R-READ_DRAFT/R-DELEGATE không đòi review; **không** thêm yêu cầu review ngầm; lời gọi Reviewer không bị review (không đệ quy). Mọi phần khác (grant, scope, binding/guard, quan sát) vẫn kiểm khi áp dụng. Câu “mỗi effect cần PRE_EFFECT” của Rev 1 bị bỏ.

**3.3.5 Hợp nhiều review.** Không “review mới nhất thắng”, không quy tắc thời gian/supersession. Output liệt kê từng review với `role_in_decision` ∈ `SUFFICIENT_COMPONENT | VETO | NOT_APPLICABLE(differs_in:[parts]) | NOT_ELIGIBLE | INCONSISTENT | NOTED`.

### 3.4 Veto và review cũ (F4, Q-8)

**Quy tắc veto V-1…V-6 — cần Main/Reviewer chốt trước schema (7.2 R-1); không tự thu hẹp veto hiện hành trong code.**

- **V-1 (khớp).** Review `R_np` có verdict ≠ PASS (`BLOCKED`, `CHANGES_REQUIRED`, `UNKNOWN`) hoặc `INCONSISTENT` **veto** khi: cùng **pha**, cùng **anchor** (4.2) và **full binding** của pha (phần chung + phần riêng) bằng binding hiện hành. Khác ở bất kỳ phần nào ⇒ không veto; ghi `related_nonpass` (task_id + phase trùng, `differs_in`), **không** coi là đã sửa.
- **V-2 (không phụ thuộc eligibility).** Non-PASS của reviewer không đủ tư cách vẫn veto (chỉ thêm thận trọng); reviewer không đủ tư cách **không** tạo PASS.
- **V-3 (subject/phạm vi) [sửa theo D3].** Review có thể khai `scope.subject ∈ {TASK_WIDE, PARTIAL}`, nhưng **trong D0 mọi non-PASS/INCONSISTENT thỏa V-1 veto TASK_WIDE**: chặn mọi occurrence, artifact và phần của task thuộc pha đó, bất kể `subject`, `actions_checked`, `scope.items`. **Không suy độc lập từ target/payload không giao nhau**: hai action có thể truyền dữ liệu qua `inputs`, `context_refs`, artifact trung gian hoặc đầu ra của nhau dù target khác nhau. `scope.subject=PARTIAL` chỉ là dữ liệu ghi nhận cho chẩn đoán, **chưa** giảm veto. Giảm veto PARTIAL hoãn tới khi có mô hình dependency/owner được nhận (7.2 R-8); mô hình đó phải khai độc lập theo cách *dương* (không suy từ việc thiếu giao nhau). Fallback cho tới lúc đó: TASK_WIDE.
- **V-4 (so giao, không so bằng).** Veto xét bằng **giao** với phạm vi chủ thể, không bằng phép so scope “bằng nhau”. Review PASS có phạm vi hẹp hơn, hoặc đổi danh sách coverage, **không** bỏ veto còn áp dụng; veto không phụ thuộc scope của PASS.
- **V-5 (không gỡ).** Không supersession theo thời gian; xác nhận user không gỡ veto; đổi reviewer không gỡ; PASS sau cùng binding không gỡ.
- **V-6 (đóng vòng sửa).** Sửa thật làm binding đổi ⇒ cần review mới đạt QUAL + COVERAGE; non-PASS cũ chỉ còn `related_nonpass`.

Rủi ro thừa nhận: Main có thể đổi một byte để thoát V-1 rồi xin review lại; cooperative không chặn được. Giảm nhẹ bằng `related_nonpass` và yêu cầu review mới đạt đủ phủ (7.2 R-1).

**Giới hạn D3 (ghi rõ).** Trong cùng một task, ở pha có veto hoặc thiếu review mức task, D0 không công nhận phần nào là “độc lập” để tiếp tục; hậu quả là veto rộng hơn mức tối thiểu có thể có. Đây là fallback có chủ ý, không phải kết luận rằng mọi action phụ thuộc nhau. Nguyên tắc “đọc/nháp thực sự độc lập được tiếp tục” giữ nguyên nhưng chỉ áp dụng khi độc lập có căn cứ dương (giữa task khác nhau; gate riêng từng action — 3.1).

**Review cũ** = review có binding khác ở bất kỳ phần nào của pha: `NOT_APPLICABLE(differs_in)`; thiếu review hợp lệ ⇒ `REVIEW_MISSING` (+ ghi chú `STALE_REVIEW`); không dùng thời gian.

User xác nhận được là căn cứ *nhu cầu/ý định/tiếp nhận*; không thay review bắt buộc, không gỡ veto, không thay PRESERVATION, ACTUAL_OUTCOME, quan sát bytes hoặc quyền nguồn.

### 3.5 Ma trận record-only diagnostic vs accept (F7)

Nguyên tắc: **task, route và pha quyết gate bắt buộc; bỏ sót hoặc claim thấp hơn không tắt gate [M].** Claim trong result (`acceptance_states`) chỉ có thể **thêm** kiểm tra (claim cao hơn bằng chứng ⇒ `ACCEPTANCE_CLAIM_NOT_SUPPORTED`), không bao giờ bớt.

| Mục | Diagnostic (báo trong mọi pha) | Điều kiện để disposition `PASS` ở **accept** |
|---|---|---|
| Cấu trúc/nhất quán record | `aggregate.records_checked_state ∈ {CONSISTENT_IN_CHECKED_SCOPE, INCONSISTENT, NOT_EVALUATED}`; liệt kê gate đã kiểm | cần nhưng **không đủ** |
| Route | `route.status`, giả định mở | `RESOLVED` (3.1) |
| Pha review | liệt kê pha đòi (policy ∪ extra) và `role_in_decision` | từng pha đòi phải `REVIEW_SUFFICIENT`, không veto |
| REQUIREMENTS | luôn tính (task có requirement `mandatory`) | `REVIEW_COVERED`, hoặc (không đòi pha review nào) `USER_ACCEPTED_DECLARED` **đúng D4**: gắn task_id/revision/accepted_task_digest hiện hành, đủ tập requirement bắt buộc, đúng artifact/result; phủ một phần ⇒ phần còn lại `NOT_CHECKED` ⇒ BLOCKED |
| ACTUAL_OUTCOME + tính đủ/reconcile | luôn tính nếu có action ghi `REQUIRED` **hoặc** bất kỳ occurrence (kể cả `OPTIONAL`) có OUTCOME/được khai đã thực hiện | bytes hiện tại (S4) + proof lịch sử precondition và liên kết thao tác (writer/protocol, 4.3.1) + mọi occurrence `REQUIRED` hoàn tất + occurrence `OPTIONAL` đã thực hiện được kiểm như `REQUIRED` + reconcile PARTIAL/UNKNOWN (4.4) |
| SOURCE_SCOPE | khi R-HIGH_STAKES | `REVIEW_COVERED` |
| Claim `CANDIDATE` | chấp nhận làm trạng thái | **không** miễn bất kỳ dòng nào ở trên |

Result chỉ `CANDIDATE` thiếu outcome/proof/coverage bắt buộc ⇒ `BLOCKED`, kèm `records_checked_state=CONSISTENT_IN_CHECKED_SCOPE` nếu record nhất quán. `aggregate` luôn đếm riêng `not_checked`, `unsupported`, `not_yet_due`, `open_assumptions`, không dùng tổng che gate thiếu.

---

## 4. Scope/binding theo pha và record mới

### 4.1 Hai loại đối tượng scope (có tag)

| `kind` | Định danh | Digest nghĩa gì | Qualifier | Coverage | Pha | Mức |
|---|---|---|---|---|---|---|
| `FILE_BYTES` | `path` + `digest` | SHA-256 **bytes file nguyên văn** [K] | `source_id?`, `revision?`, `coverage ∈ {FULL, PARTIAL}` (+`part_description` nếu PARTIAL) | cover artifact khi path+digest khớp, qualifier khai trong review phải khớp artifact, qualifier chỉ ở artifact được vắng ở review [K S2 COVER]; **chỉ `FULL`** tính phủ artifact | `binding.inputs/outputs`, `result.artifacts`, review mọi pha | D/C; **O chỉ khi S4** |
| `TASK_PROJECTION` | `part ∈ {accepted_task, intent, context, action}` + `task_id` + `task_revision` (+ `action_index` khi `part=action`) | digest **tính lại** từ record theo projection contract 4.2 | không | phủ phần task khi digest khai = digest tính lại | review PRE_EFFECT (và pha khác nếu nêu) | R |

`coverage` của `FILE_BYTES` là trường riêng của scope item, **không** phải qualifier của so sánh `COVER` (S2): S3 xét `coverage` trước, rồi dùng `COVER` cho path/digest/qualifier.

Quy tắc phân biệt (D5):
- Digest `TASK_PROJECTION` không bao giờ là bytes file; không có `path` làm định danh.
- `FILE_BYTES` có digest *bằng* digest projection task (hình ex02) **không** thành `TASK_PROJECTION`, không chứng minh bytes: coi là `FILE_BYTES` chưa quan sát, note `PROJECTION_DIGEST_AS_FILE`, **không** thỏa phủ task ở PRE_EFFECT.
- Checker không đồng nhất digest bytes `task.json` với `accepted_task_digest`; nối parse→project cần thiết kế riêng (S4, ngoài D0).
- Ex02 giữ nguyên ở v2; ví dụ v3 là bộ mới.

### 4.2 Chuỗi quan hệ và tập phần so theo pha (F4)

Chuỗi: **Task T** → **Effect REQUEST `E_req`** (một occurrence) → **Review PRE_EFFECT `V1`** → *(tác động)* → **Effect OUTCOME `E_out`** → **Result `R`** → **Review PRE_INTEGRATION `V2`** → **Review PRE_DELIVERY `V3`**.

*Phần chung bắt buộc* (CP) = `bind_version`, `evaluation_basis`, `policy_version`, `task_id`, `task_revision`, `intent_digest`, `accepted_task_digest`, `context_digest`, `policy_digest`, `overlay_digest` (O: vắng cả hai = `NOT_BOUND`; một phía = lệch), `inputs`. **CP được tính lại và so ở mọi pha và cho mọi record, kể cả khi accept; anchor cũ không miễn CP.** Grant/actor/reviewer/context/parent vẫn kiểm độc lập (3.2).

| Record | Anchor (record nó được kiểm cùng) | CP | `outputs` | `action_digest` | `scope` |
|---|---|---|---|---|---|
| `E_req` | T (resolve đúng 1) | R | O, chỉ `STAGED_BYTES` | **R** (digest action của occurrence; phải = projection `task.effects.actions[action_index]`) | — |
| `V1` PRE_EFFECT | **`E_req` đã resolve** (và T) | R | O, chỉ `STAGED_BYTES`; có ⇒ phải = `E_req.outputs` staged và được phủ bằng item `FILE_BYTES` FULL | — (Δ08 có hiệu lực) | R: `items` (có `TASK_PROJECTION(accepted_task)`), `actions_checked` ∋ occurrence của `E_req`, `intent_refs_checked`, `intent_mapping`, `subject` |
| `E_out` | `E_req` cùng occurrence (quan hệ khai báo 4.4) | R | **R**, chỉ `ACTUAL_BYTES` (`outcome.artifacts`) | R | — |
| `R` | `E_out` của các occurrence trong `actions_performed`; T | R | **R**, `ACTUAL_BYTES`; `artifacts` **=** `binding.outputs` (EXACT) | — | `actions_performed[]` (4.7.3) |
| `V2` PRE_INTEGRATION | **`E_out` + `R`** (và T) | R | **R**, `ACTUAL_BYTES`, = `R.artifacts` | — | R: `items` FILE_BYTES FULL phủ outputs, `requirement_conclusions`, `actions_checked`, `subject` |
| `V3` PRE_DELIVERY | **`R`** (+ `E_out`) | R | R, `ACTUAL_BYTES` | — | R: `items` FILE_BYTES FULL, `source_scope_conclusions`, `subject` |

Hệ quả: `V1` được so với `E_req` **ở mọi pha mà nó được dùng**, không so `outputs` của `V1` (staged) với `outputs` thực của `V2/R` — hai tập không được yêu cầu bằng nhau. Tại accept, `V1` vẫn cần hiện diện nếu policy ∪ extra đòi PRE_EFFECT: nó được kiểm với `E_req` + CP hiện hành.

Ngữ nghĩa vắng/một phía/null [K S2, làm tường minh]:
- Trường **O** vắng cả hai phía ⇒ `NOT_BOUND`; một phía ⇒ `ONE_SIDED` ⇒ review không áp dụng.
- Hiện diện nhưng `null`/sai kiểu ⇒ `UNSUPPORTED(MALFORMED_RECORD)`.
- `outputs: []` ≠ vắng: “bind với không output”; với task có `expected_outputs` không rỗng ⇒ `NO_OBJECT`/`COVERAGE_INCOMPLETE`.
- Trùng phần tử trong tập ⇒ `UNSUPPORTED(DUPLICATE_SET_ELEMENT)`; không dedupe.
- Trường **—** mà có ⇒ `BINDING_FIELD_NOT_APPLICABLE` (mismatch).
- Quan hệ chỉ so hai peer (không tính lại) không cộng vào “tính lại đủ”.
- Không thêm digest riêng cho review/effect/result.

### 4.3 Dự kiến → staged → thực, và input bị ghi đè

| Giai đoạn | Biểu diễn | Ràng buộc bởi | Dùng làm ACTUAL_OUTCOME? |
|---|---|---|---|
| dự kiến | đường dẫn ở `task.effects.expected_outputs` (không digest) | `accepted_task_digest` | **không** |
| staged (bytes đã tồn tại trước tác động) | `FILE_BYTES` `role=STAGED_BYTES` ở `E_req.outputs`/`V1.outputs` | binding | **không** |
| thực (sau tác động) | `FILE_BYTES` `role=ACTUAL_BYTES` ở `E_out.outcome.artifacts`, `R.artifacts`, `V2/V3.outputs` | binding + (S4) quan sát | chỉ khi **O** |

Không đòi output chưa tồn tại: ở `create_new` trực tiếp, `E_req.outputs` vắng là hợp lệ; chỉ `E_out`/`R` đòi bytes thực.

**Quan hệ staged→actual (phải khai, có owner proof).** Mỗi entry `STAGED_BYTES` mang `relation`:

| `relation` | Nghĩa | S3 | Owner proof |
|---|---|---|---|
| `COPY_IDENTICAL` | actual artifact có cùng bytes với staged (promote/copy; path có thể khác) | C: `actual.digest = staged.digest`, lệch ⇒ `BINDING_MISMATCH`; đóng ở mức O cần S4 | S4 quan sát bytes |
| `TRANSFORM_BY_OWNER_TOOL` | actual là kết quả công cụ owner áp staged lên đích (ví dụ cập nhật sổ như ex02) | **`UNSUPPORTED`** cho phần phụ thuộc ⇒ BLOCKED | giao thức bảo toàn của writer (A-06) |
| không có staged | tạo trực tiếp | không áp dụng | S4 cho bytes thực |

Chưa có relation hoặc owner proof ⇒ phần phụ thuộc `BLOCKED`/`UNSUPPORTED`. Không so bytes **đầu vào trước sửa** với **output sau sửa** như thể phải bằng nhau.

### 4.3.1 Proof precondition lịch sử ≠ quan sát file hiện tại (D1)

**Nguyên tắc.** Một quan sát read-only chỉ nói về *thời điểm quan sát*. Nó không chứng minh (i) ghi sau đó là exclusive-create hay không có race, (ii) đích *từng* chưa tồn tại ngay trước thao tác của occurrence đã thực hiện, (iii) bytes hiện tại do chính occurrence đó tạo. Ba điều này cần **proof lịch sử gắn request/occurrence và liên kết `E_req`↔`E_out`** do writer/protocol tạo; owner chưa có (7.2 R-7). D0 **chỉ nêu điều kiện và owner còn thiếu**, không thiết kế/cài writer hay receipt thật. Tại accept **không** kiểm “đích hiện không tồn tại” cho action đã tạo thành công và **không** route lại thành `overwrite` chỉ vì file nay có thật.

| Pha | Điều kiện kiểm | Anchor | Căn cứ nhận | Owner proof | Chưa có proof |
|---|---|---|---|---|---|
| d | phân loại lexical (R); grant/tool/envelope (C); precondition hiện hành: nếu có observer, “đích vắng / input khớp” **tại thời điểm d** | T | observation-at-time; không chứng minh ghi sau đó exclusive | S4 | giả định A-NEW_TARGET mở ⇒ route `CONDITIONAL` ⇒ BLOCKED |
| e | như d, ngay trước thao tác; INPUT_REVISION (O) cho input, kể cả input là target, gắn `E_req` | `E_req` | observation-at-time gắn `E_req`; `limits=[EXCLUSIVE_WRITE_NOT_PROVEN, RACE_NOT_EXCLUDED]` | S4 + writer | `NOT_CHECKED(OBSERVATION_UNAVAILABLE)` ⇒ BLOCKED |
| a — `create_new` | (1) proof lịch sử: đích chưa tồn tại ngay trước thao tác của occurrence; (2) `E_out` `APPLIED` liên kết cùng occurrence; (3) bytes hiện tại = `E_out.artifacts` = `R.artifacts` (`ACTUAL_BYTES`). **Không** kiểm “đích hiện không tồn tại”; không route lại `overwrite` vì file nay có thật | `E_req`→`E_out`→`R` | (1)+(2) writer/protocol; (3) S4 | đề xuất: P-CN1 (1,2), S4-min cùng owner (3) — 4.3.2, chưa thi công | thiếu (1) hoặc (2) ⇒ `UNSUPPORTED(PRECONDITION_PROOF_MISSING)` ⇒ BLOCKED. S4 read-only chỉ cho (3): **không đủ** |
| a — input là target (`overwrite` …) | (1) bytes input *trước tác động* khớp `inputs[X].digest`, gắn `E_req`/occurrence (đã có ở e, mang sang accept bằng proof lịch sử); (2) sau ghi: output riêng so `E_out`/`R`; **không** so bytes hiện tại với `inputs[X]` | `E_req`→`E_out` | không dùng lời khai C thay proof O đã đòi; không miễn INPUT_REVISION | writer/protocol; S4 | thiếu (1) ⇒ `NOT_CHECKED`/`UNSUPPORTED` ⇒ BLOCKED |
| a — `overwrite`/sổ/provenance | như trên **và** PRESERVATION (3.2) | — | — | writer A-06 | `UNSUPPORTED(PRESERVATION_UNKNOWN)` |

Hệ quả: triển khai observer read-only S4 **không** đủ để accept `PASS` cho ghi mới hay ghi đè; S4 cho observation-at-time (d/e) và bytes hiện tại (a), phần lịch sử/liên kết thuộc owner chưa có. Không đổi trần ADVISORY.

### 4.3.2 Protocol P-CN1 — publish một file mới (delta D0 sửa theo review, đề xuất, chưa thi công)

**Trạng thái mục này:** Orchestrator/Reviewer Sol 6.1 High nhận DESIGN_ACCEPTED_WITH_CONSTRAINTS để mở P-CN1-C sau các sửa tài liệu rõ nguyên nhân trong lượt review này. Hướng protocol được nhận để đặc tả API/evidence; chưa contract implementation-ready hoặc proof runtime. Scope M-2 đã nhận cho amendment có version; policy/gate/routing hiện hành giữ nguyên tới khi amendment, implementation và integration được review/nhận đúng bước (M-4).

**Phạm vi.** Một luồng, một action: user yêu cầu tạo **một** file nháp mới từ nguồn đã nêu; công cụ soạn (ngoài D0) đưa staged bytes; P-CN1 publish đúng một lần vào `working/` hoặc `output/` (`content_use` chỉ `internal_draft`), không ghi đè, rồi agent bàn giao đúng bản. Môi trường bản đầu: **Windows, volume NTFS local**; POSIX, ổ mạng, OneDrive/thư mục đồng bộ, FAT/exFAT là capability sau và giữ `UNSUPPORTED` (M-1). Không áp dụng cho overwrite, sổ/provenance, nhiều file, gửi ngoài, output có sign/send_external/decision_basis/verified_claim, task có pha review bắt buộc, sinh DOCX hay kiểm định dạng. Nếu policy ∪ extra_review_phases đòi review thì bản đầu UNSUPPORTED/BLOCKED ở dispatch/effect trước mọi ghi phụ thuộc, không publish rồi chặn accept. Không thay behavior v1/legacy, dùng D4 gỡ veto hoặc thay review. User không gõ metadata: công cụ dựng snapshot từ yêu cầu đã trình.

**Owner.** Owner **cần bổ sung**: `tools/publish_new.py` (P-CN1 + chế độ đọc S4-min). Tái dùng helper của `tools/transaction.py` (`guard`/`link_free`/`runtime_problem`, `held`/`Pins`, `sha_bytes`/`sha_file`); **không** dùng `Transaction`, journal `transaction-v1`, `prune`/`KEEP_JOURNALS`. Code `tools/` là `framework`: thêm owner là R-AUTHORITY_CHANGE, review độc lập ở tranche thi công.

**Primitive no-clobber.** `os.link(staged, target)` (Windows: `CreateHardLinkW`): tên đích có sẵn ⇒ lỗi, không đè; đích chưa có ngay trước thao tác được thực thi bởi chính thao tác, không kiểm-rồi-thay. Không dùng `os.replace`/`shutil.move`/`os.rename`; không `O_CREAT|O_EXCL` ghi thẳng vào đích (lộ file dở khi crash). Hard link **không** làm bytes bất biến: staged và đích là cùng một file nên sửa tại chỗ qua tên nào cũng thấy ở tên kia; vì vậy identity chỉ dùng cùng kiểm size/hash (recovery). Trước publish, kiểm volume chứa project là NTFS local (loại ổ cố định, tên hệ file `NTFS`); không xác định được, khác loại, `EXDEV` hay hard link lỗi ⇒ `UNSUPPORTED_FS`, không fallback copy/replace.

**Path, thư mục cha, alias.** (1) Lexical theo 2.2 trước mọi ghi: đường dẫn tương đối POSIX dưới `working/` hoặc `output/`; từ chối `..`, ổ đĩa, UNC, `:` (ADS), đoạn kết thúc `.`/khoảng trắng, mẫu `~<số>`, tên thiết bị Windows, tên khớp mẫu authority ⇒ `PATH_UNSUPPORTED_FORM`/framework. (2) Thư mục cha: chỉ tạo đoạn còn thiếu dưới `working/` hoặc `output/` bằng `os.mkdir`; đoạn đã có phải là thư mục thường, không link/junction. (3) Giữ handle thư mục từ gốc tới cha bằng `held`/`Pins` suốt lúc kiểm→link (cơ chế A-06); không giữ được ⇒ `protection=recheck_only`, ghi đúng mức, không claim race-free. (4) Tên chỉ khác hoa/thường với file có sẵn ⇒ link báo đã có ⇒ conflict. Chuẩn hóa Unicode/8.3 tự sinh chưa kiểm ⇒ không claim.

**Snapshot task/yêu cầu/input, chốt trước publish (sửa 1, 2).** API của owner nhận các tham số dưới đây; công cụ dựng **một** record task theo hình C1 (`task` của contract v2 + Δ17), ghi nguyên vào `<rid>.prepared.json` trước khi stage. Sau đó snapshot không được dựng lại hay diễn giải lại; mọi binding, M-3 và checker dùng đúng bytes này. Tham số thiếu hoặc không ánh xạ được ⇒ từ chối trước PREPARED.

| Tham số API | Trường canonical trong task | Ghi chú/mức |
|---|---|---|
| `work_id` | `work_id` | id theo `$defs/id` |
| (sinh) `rid` uuid4 hex | `task_id = "pcn1-<rid>"`, `task_revision = 1` | một task cho một lần publish; sửa nháp = task mới (`supersedes`) |
| `intent_ref {locator, digest, recorded_by}` | `intent.refs = [{ref_id:"intent-1", kind:"user_intent", locator, digest, attribution:{source_class:"USER_CONFIRMATION", channel:"USER_MESSAGE"\|"HOST_CONFIRMATION_UI", recorded_by, evidence_locator}}]` | `digest` = sha256 của đúng chuỗi tin nhắn user mà agent ghi lại; DECLARED, công cụ không xác minh host |
| `main_interpretation`, `unconfirmed[]` | `intent.main_interpretation`, `intent.unconfirmed` | lời đọc của agent; DECLARED, không chứng minh model đã hiểu |
| `requirements[] {req_id, statement, mandatory}` | `acceptance.requirements` (thứ tự giữ) | ≥1 `mandatory`; chính là danh sách đã trình user trước khi soạn |
| `grant_ref` | `authority.grant_refs = [attributed_ref kind "grant"]` (set) | `USER_CONFIRMATION`; P-CN1 không thực thi grant |
| `subject {actor_id, role}` | `proposed_by`, `authority.subject`; `envelope = {role}` | — |
| `inputs[] {path, digest, source_id?, revision?}` | `inputs` (set of `obj_proj`) | `digest` = sha256 bytes **công cụ soạn thực sự đọc** khi tạo staged (TOOL_OUTPUT, DECLARED); không thay bằng hash đọc lại lúc publish |
| `target` (một chuỗi) | `effects.actions = [{operation:"create_new", tool:"publish_new", targets:[target], write_zone, content_use?}]`, `effects.expected_outputs = [target]`, `effects.on_missing = "STOP_DEPENDENT_EFFECT"` | `targets`, `content_use` là **set** (C1 4.3); `write_zone` do công cụ suy từ bảng A (`working`\|`output_new`), không nhận từ caller; `completion` vắng = `REQUIRED` |
| `content_use[]` | `actions[0].content_use` | bắt buộc với `output_new`, chỉ `["internal_draft"]`; với `working` vắng |
| — | `schema_version`, `evaluation_basis = "COOPERATIVE_WORKFLOW"` | version là bản được chọn ở A0; trước A0 snapshot ghi `schema_version` đề xuất và chỉ dùng làm thiết kế |

`action_proj` = đúng object `actions[0]` ở trên, `action_digest = digest({bind, part:"action", action: action_proj})`; `accepted_task_digest` theo projection `task` của C1 trên snapshot. `tool` chỉ là chuỗi trong projection, **không** là căn cứ đủ điều kiện M-2. Payload `target` đơn của bản trước không phải `action_proj` và bị bỏ. Snapshot có thể chứa lời yêu cầu, tên file và đường dẫn có tên người: không claim ẩn danh (M-5); không chép nội dung nguồn.

**Thứ tự request → precondition → publish → evidence → kiểm/bàn giao** (thư mục evidence `.agent/runtime/publish/`, kiểm `runtime_problem`/`link_free`; mọi file evidence create-only `O_EXCL`, không bao giờ sửa/đè; mỗi `rid` có **tối đa một** file kết thúc trong `published`/`conflict`/`abandoned`/`unknown`):

| # | Bước | Ghi gì | Lỗi ⇒ |
|---|---|---|---|
| 1 | Nhận tham số, kiểm lexical/vùng/authority/`content_use`/volume NTFS local, dựng snapshot | — | từ chối, chưa ghi |
| 2 | Kiểm input: sha256 hiện tại của từng `inputs[].path` (observation-at-time) phải = digest công cụ soạn đã đọc | — | lệch/không đọc được ⇒ từ chối `INPUT_CHANGED_SINCE_READ`, chưa ghi |
| 3 | PREPARED: tạo `<rid>.prepared.json` (`O_EXCL`, mở đọc-ghi), lấy khóa một byte nonblocking ở offset cố định ngoài nội dung và giữ fd tới bước 7. **Sau khi lấy khóa**, kiểm lại terminal/ownership của rid: nếu recover đã ghi trạng thái kết thúc hoặc không còn đúng trạng thái chuẩn bị của lần gọi thì dừng trước stage/link. Chỉ sau kiểm này mới seek 0, ghi snapshot + `content{sha256,size}` + `inputs_observed_at_publish`, fsync | `prepared` | không tạo/khóa được hoặc recheck không đạt ⇒ từ chối, chưa stage/publish |
| 4 | Stage `<rid>.staged` (`O_EXCL`, fsync), so sha256/size | `staged` | lệch/lỗi ⇒ `abandoned` (trong tiến trình, chắc chắn chưa link); staged lỗi giữ lại, không tự xóa |
| 5 | Tạo cha còn thiếu; `os.link(staged, target)` | thư mục cha, tên đích | đã có ⇒ `conflict`, đích giữ nguyên; lỗi khác ⇒ `abandoned` |
| 6 | Kiểm sau link: `lstat(target)` file thường, identity khả dụng và = staged, size/sha256 = `prepared.content` | — | lệch ⇒ `unknown`, không xóa đích, giữ staged |
| 7 | `published`, rồi xóa staged của chính `rid` (chỉ khi identity staged = `published.identity`), nhả khóa | `published`; xóa staged | không ghi được ⇒ `PUBLISHED_EVIDENCE_PENDING`, giữ staged, không publish lại |
| 8 | Bàn giao candidate: đường dẫn, 8 ký tự đầu sha256, `rid`, nguồn và revision đã dùng, phần chưa kiểm | — | — |

**Evidence `publish-v1` (đề xuất):** `prepared` = `{schema, protocol:"P-CN1", protocol_version:1, state:"PREPARED", request_id, created, task:<snapshot>, content:{sha256,size}, inputs_observed_at_publish:[{path, sha256}], supersedes?}`; `published` = `{schema, state:"PUBLISHED", request_id, target, content:{sha256,size}, identity:{volume_serial, file_index}, protection ∈ {held, recheck_only}, recovered:bool, at}`; `conflict`/`abandoned`/`unknown` = `{request_id, reason, at}`. Không nội dung file, không đường dẫn tuyệt đối.

**Resolve liên kết.** Khóa là `request_id`, resolve bằng tên file chính xác `<rid>.<state>.json` (không quét “mới nhất”, không suy từ hash). `E_req`↔`E_out` hợp lệ khi: đúng một `prepared` parse được, `request_id` bên trong = tên file; đúng một file kết thúc và đó là `published`; `published.target` = `task.effects.actions[0].targets[0]`; `published.content` = `prepared.content`. Thiếu, hỏng, `schema` lạ, nhiều file kết thúc ⇒ `UNSUPPORTED(PRECONDITION_PROOF_MISSING)`. Ánh xạ record khi chạy checker (công cụ dựng trong bộ nhớ, không lưu bởi P-CN1): task ← `prepared.task`; `E_req` ← `prepared` (REQUEST, `action` = `action_proj`, binding `accepted_task_digest`/`action_digest`/`inputs`); `E_out` ← `published` (OUTCOME `APPLIED`, `artifacts=[{path, digest, role:"ACTUAL_BYTES"}]`, `receipt_ref` = `attributed_ref` kind `effect_receipt` trỏ `published` với digest bytes của file đó); `R` ← bàn giao (`CANDIDATE`, artifacts EXACT); `user_acceptance` theo M-3.

**Lịch sử ≠ hiện tại.** `published` là proof lịch sử do writer ghi lúc thao tác (link thành công ⇒ tên chưa có ngay trước; identity + hash ⇒ đích là bytes của staged này). Tại accept, S4-min đọc **hiện tại**: sha256 đích so `published.content` (`CHANGED_AFTER_PUBLISH` nếu khác); identity hiện tại chỉ để báo (`OBJECT_REPLACED_SAME_BYTES`). Hash hiện tại trùng **không** chứng minh nguồn gốc; không có `published` hợp lệ ⇒ `PRECONDITION_PROOF_MISSING` dù hash khớp. Evidence nằm trong vùng Main ghi được, `tamper_resistance=NONE` [K]: P-CN1 chống tai nạn/nhầm bản, không chống giả mạo.

**Phục hồi (sửa 3; chỉ process crash, không claim mất điện/độ bền đĩa; không auto-resume/retry).** Lệnh tay `publish_new.py status|recover <rid>`. `recover` mở `<rid>.prepared.json` đọc-ghi và lấy **cùng khóa byte đó, không chờ**; đang bị giữ (publish hay recover khác của cùng `rid` còn chạy) ⇒ `BUSY`, không ghi gì. Có file kết thúc ⇒ chỉ báo, không ghi thêm.

| Còn lại (đã giữ khóa, chưa có file kết thúc) | Kết luận | Ghi |
|---|---|---|
| `prepared` + staged; đích là file thường, identity khả dụng = staged, size/sha256 đích = `prepared.content` | link đã xảy ra và bytes đúng ⇒ `PUBLISHED`, `recovered:true`; rồi xóa staged | `published` |
| `prepared` + staged; đích cùng identity nhưng size/hash khác (đã bị sửa tại chỗ) | không chứng minh bytes đã publish ⇒ `UNKNOWN` | `unknown` |
| `prepared` + staged; đích khác identity (kể cả cùng hash), là link/junction, hoặc identity không đọc được | `UNKNOWN`, không xóa/đè đích | `unknown` |
| `prepared` + staged; không có đích | không chứng minh “chưa từng publish” (đích có thể đã bị xóa) ⇒ `UNKNOWN` (`TARGET_ABSENT`) | `unknown` |
| `prepared` không có staged (có hay không có đích) | không đủ căn cứ ⇒ `UNKNOWN` | `unknown` |
| `prepared` rỗng/hỏng, hoặc evidence mất/bị dọn | nguồn gốc không xác định ⇒ accept `UNSUPPORTED(PRECONDITION_PROOF_MISSING)`; không đụng đích | `unknown` nếu `prepared` còn tạo được khóa, ngược lại không ghi |

`abandoned` chỉ do chính tiến trình publish ghi khi biết chắc chưa gọi link hoặc link thất bại. `UNKNOWN` ⇒ OUTCOME `UNKNOWN` ⇒ `RETRY_UNRECONCILED` ⇒ BLOCKED. Thử lại dùng rid mới; tên đích mới nếu conflict. Staged của lần lỗi chứa toàn nội dung: giữ tới lệnh rõ `discard-staged <rid>` (chỉ khi có terminal khác published), không tự xóa (M-5). Recover có thể thấy prepared rỗng, tạo unknown rồi nhả khóa **trước** khi publisher lấy khóa; vì vậy publisher phải kiểm lại terminal/ownership sau khi lấy khóa, không chỉ dựa vào lấy khóa thành công. Mọi ghi trạng thái và cleanup cùng rid dùng cùng serialization, kể cả discard-staged; trạng thái mâu thuẫn giữ BLOCKED.

P-CN1-C chốt một offset khóa chung, giới hạn kích thước JSON nhỏ hơn offset; nonblocking, seek 0 trước đọc/ghi và seek lại offset trước unlock; không ghi dummy byte ngoài EOF. Khóa chỉ phối hợp giữa các lượt gọi đúng protocol, không freeze JSON/staged/target. Microsoft cho phép khóa ngoài EOF: [_locking](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/locking?view=msvc-170), [LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex). Share mode/đọc JSON khi khóa/giải phóng sau process crash là proof runtime ở P-CN1-I, chưa được coi là đã kiểm.

**Envelope tác động và routing versioned (sửa 4, scope M-2 Main đã chọn).** Toàn bộ tác động của một lần gọi P-CN1:

| # | Tác động | Đường | Điều kiện |
|---|---|---|---|
| T1 | tạo thư mục cha còn thiếu | dưới `working/` hoặc `output/`, chỉ tổ tiên của `target` | `os.mkdir`, không link |
| T2 | tạo `.agent/runtime/publish/` nếu thiếu — **chỉ `publish`**: `.agent` và `.agent/runtime` phải có sẵn (revision corrective 18/10; thiếu ⇒ REFUSED `RUNTIME_PARENT_MISSING`) | runtime | `link_free`, như A-06 |
| T3 | tạo `<rid>.prepared.json` | runtime | `O_EXCL`; chứa snapshot |
| T4 | tạo `<rid>.staged` | runtime | `O_EXCL`; chứa toàn nội dung |
| T5 | tạo tên `target` (action `create_new`) | `working/`\|`output/` | `os.link` |
| T6 | tạo đúng một `<rid>.{published,conflict,abandoned,unknown}.json` | runtime | `O_EXCL`; publish hoặc recover |
| T7 | xóa `<rid>.staged` | runtime | sau `published`, identity khớp; hoặc `discard-staged` có lệnh rõ |

Ngoài danh sách (sửa/xóa JSON evidence, ghi file khác, `STATE.md`/HANDOFF, đổi tên) không thuộc envelope và theo route hiện hành.

Mapping routing **đề xuất cho version routing được chọn ở A0**, chưa có hiệu lực:
- policy thêm `owner_protocols: [{id:"P-CN1", version:1, entrypoint:"tools/publish_new.py", entrypoint_sha256:<pin lúc nhận implementation>, platform:"windows-ntfs-local", envelope:[T1…T7]}]`;
- **Trước tác động (dispatch/effect):** T2–T4, T6, T7 gắn vào T5, không sinh hàng R-MUTATION riêng, chỉ khi protocol/version/entrypoint và envelope được nhận, T5 đủ điều kiện R-READ_DRAFT theo Δ03/2.5, grant phủ **toàn bộ T1–T7 áp dụng**, S4-min cùng lượt quan sát pin entrypoint khớp và các gate đến hạn đạt. Chưa có published ở pha này; không đòi receipt tương lai hoặc tạo receipt giả để mở effect. Trước mỗi ghi, owner giữ đúng path/envelope và precondition protocol.
- **Sau publish/ở accept:** ngoài các điều kiện còn áp dụng, E_out.receipt_ref phải resolve tới published hợp lệ, cùng request/snapshot và các runtime file đúng envelope. Receipt thiếu/sai/mâu thuẫn ⇒ accept BLOCKED; không hồi tố một effect chưa được cấp quyền thành hợp lệ. P-CN1-C chốt gate theo pha, không dùng kết quả accept để mở dispatch/effect.
- Thiếu bất kỳ điều kiện nào (kể cả chỉ có `tool:"publish_new"`/`protocol:"P-CN1"` tự khai, hay file chỉ nằm trong `.agent/runtime/publish/`) ⇒ các ghi runtime theo route hiện hành (R-MUTATION, Δ04) ⇒ thiếu review ⇒ BLOCKED. Không suy điều kiện từ vị trí file.
- Không đổi: grant/path/tool/binding/known-loss/review của tác động khác, `main_may_downgrade=false`, ADVISORY. Amendment này **đổi** nghĩa vụ review hiện hành cho T2–T4, T6, T7 trong đúng điều kiện trên, nên phải đi qua version/review/nghiệm thu như mọi amendment. STATE/HANDOFF vẫn theo 5.4.1.

**Hoàn tất kỹ thuật ≠ candidate ≠ nghiệm thu (M-3).** (i) Hoàn tất kỹ thuật = published hợp lệ. (ii) Candidate = bàn giao bước 8; CANDIDATE không tắt gate (3.5). (iii) Nghiệm thu = result.user_acceptance **đủ D4 hiện hành** (4.7.3): task_id/task_revision/accepted_task_digest của snapshot, accepted_requirements phủ mọi mandatory, result_id, accepted_artifacts đúng path/digest EXACT, presented_summary {locator,digest}, ref user_acceptance có USER_CONFIRMATION + USER_MESSAGE/HOST_CONFIRMATION_UI và evidence_locator resolve tới căn cứ xác nhận hợp tác đã quan sát. Không thêm yêu cầu ACL/store ngoài quyền OS của Main; attribution/locator không tự chứng minh nguồn hoặc cấp quyền. Agent trình tóm tắt bằng lời thường (yêu cầu, tên file, 8 ký tự hash); user xác nhận một lần, không gõ metadata. Im lặng, mở/sửa file, “ok” không nêu bản ⇒ không đủ. Thiếu ⇒ accept BLOCKED; không bỏ trường bắt buộc.

**Gate của luồng (khi amendment + P-CN1 + S4-min đã được nhận; trước đó như AC-01/36):**

| Pha | GRANT/TOOL/ENVELOPE | PATH_SCOPE | BINDING | ACTUAL_OUTCOME | REQUIREMENTS | Disposition |
|---|---|---|---|---|---|---|
| d/e | C+D (3.2) | lexical R + S4-min cùng lượt đóng A-NEW_TARGET (`limits=[EXCLUSIVE_WRITE_NOT_PROVEN, RACE_NOT_EXCLUDED]`) | e: snapshot R/C | `NOT_YET_DUE` | `NOT_YET_DUE` | PASS phạm vi pha; không S4-min ⇒ BLOCKED như cũ |
| a | C+D | `MET` từ `published` + liên kết `rid`; không kiểm “đích hiện không tồn tại” | R/C trên snapshot | `MET` khi bytes hiện tại = `published`; khác ⇒ `NOT_MET(CHANGED_AFTER_PUBLISH)` | `USER_ACCEPTED_DECLARED` khi đủ D4; thiếu ⇒ `NOT_CHECKED` | đủ ⇒ PASS ADVISORY, `effect_authorized=false`; thiếu ⇒ BLOCKED |

**Sửa nháp lặp (5.4.2).** P-CN1 chỉ cho bản mới: task mới, file mới (`bao-cao-nhap-v2.docx`). Supersedes của prepared là lineage metadata chẩn đoán trỏ rid trước; C1 không băm trường root này, không gọi nó là bound hoặc dùng một mình để chứng minh bản hiệu lực/nghiệm thu. Nếu cần binding bắt buộc, P-CN1-C nêu amendment canonical tương ứng để A0 review, không lén đổi projection. Nhánh/mâu thuẫn lineage giữ AMBIGUOUS; không chọn theo thời gian. Điều kiện UX sửa nháp lặp 5.4.2 vẫn mở; sửa đè nhẹ chưa được nhận (Q-4).

**Ví dụ đầu-cuối (dữ liệu giả, Windows NTFS local).** User: “Soạn báo cáo ngắn từ `references/source-documents/team/quy-che-gia.pdf`, lưu nháp.” Agent trình hai yêu cầu (REQ-1 tóm tắt mục giá, REQ-2 nêu điểm chưa chắc) trước khi soạn. Công cụ soạn đọc nguồn (`a90d…`), đưa staged 18 432 byte `b7e1…`. Grant nhóm việc ở PROJECT (`USER_MESSAGE`).

```text
publish_new(work_id="w-20261018-01", target="working/w-20261018-01/bao-cao-nhap.docx",
            intent_ref={locator:"<host msg ref>", digest:"sha256:51c0…"}, main_interpretation:"Báo cáo ngắn về mục giá",
            requirements=[{req_id:"REQ-1", statement:"Tóm tắt mục giá", mandatory:true},
                          {req_id:"REQ-2", statement:"Nêu điểm chưa chắc", mandatory:true}],
            inputs=[{path:"references/source-documents/team/quy-che-gia.pdf", digest:"sha256:a90d…"}],
            grant_ref={…USER_CONFIRMATION/USER_MESSAGE…}, subject={actor_id:"main", role:"main"}, staged=<18432 bytes>)
→ rid 4c2f9e0a…; prepared.task.effects.actions[0] =
  {operation:"create_new", tool:"publish_new", targets:["working/w-20261018-01/bao-cao-nhap.docx"], write_zone:"working"}
→ inputs_observed_at_publish = [{path:"references/…/quy-che-gia.pdf", sha256:"a90d…"}]  (khớp ⇒ tiếp)
→ os.link(.agent/runtime/publish/4c2f9e0a….staged, working/w-20261018-01/bao-cao-nhap.docx)  OK
→ published {target:"working/w-20261018-01/bao-cao-nhap.docx", content:{sha256:"b7e1…", size:18432},
             identity:{volume_serial:…, file_index:…}, protection:"held", recovered:false}; xóa staged
Bàn giao: "Đã tạo working/w-20261018-01/bao-cao-nhap.docx (b7e1…, mã 4c2f9e0a) từ quy-che-gia.pdf (a90d…); nguồn giữ nguyên; chưa kiểm: …"
User: "Đồng ý bản b7e1… đáp ứng REQ-1, REQ-2" ⇒ user_acceptance {task_id:"pcn1-4c2f9e0a…", task_revision:1,
      accepted_task_digest:<tính từ snapshot>, accepted_requirements:["REQ-1","REQ-2"], result_id:"r-4c2f9e0a",
      accepted_artifacts:[{path:"working/…/bao-cao-nhap.docx", digest:"sha256:b7e1…", role:"ACTUAL_BYTES"}],
      presented_summary:{locator:"<host msg ref>", digest:"sha256:…"}}
```

**Bảng kỳ vọng (Windows NTFS local; chưa chạy; không schema/fixture/test):**

| Ca | Thiết lập | P-CN1 | Evidence | Checker d/e | Checker a | User thấy |
|---|---|---|---|---|---|---|
| P-01 happy | như ví dụ | publish | prepared+published | PASS khi S4-min | PASS ADVISORY khi đủ D4; chưa xác nhận ⇒ BLOCKED | đường dẫn, mã, phần chưa kiểm |
| P-02 thiếu quyền | không grant/grant không phủ path | không thực thi grant | prepared+published nếu bị gọi | BLOCKED `GRANT_MISSING`/`OUT_OF_SCOPE` | BLOCKED | agent hỏi quyền một lần trước khi gọi |
| P-03 đích có sẵn | file trùng tên (kể cả khác hoa/thường) | link lỗi, không đụng file | prepared+conflict | S4-min ⇒ `OPERATION_MISMATCH` | BLOCKED | “Đã có file cùng tên, chưa ghi” |
| P-04 cạnh tranh | file xuất hiện giữa S4-min và link | như P-03 | prepared+conflict | PASS tại thời điểm quan sát | BLOCKED | như P-03 |
| P-05 path/cha lạ | cha là junction; `..`; `AGENTS.md`; `output/` không `internal_draft` | từ chối bước 1 | không | BLOCKED/UNSUPPORTED | — | lý do bằng lời thường |
| P-06 ngoài NTFS local | FAT/exFAT, ổ mạng, OneDrive, POSIX | `UNSUPPORTED_FS` bước 1 | không | UNSUPPORTED | — | “Thư mục này chưa hỗ trợ ghi an toàn” |
| P-07 snapshot thiếu | không `requirements` mandatory / không `intent_ref` / không `inputs` digest khi có nguồn | từ chối bước 1 | không | BLOCKED | — | agent bổ sung từ hội thoại, không bắt user gõ |
| P-08 nguồn đổi sau khi soạn | sha256 nguồn lúc publish ≠ digest công cụ soạn đọc | từ chối `INPUT_CHANGED_SINCE_READ` | không | — | — | “Nguồn vừa đổi, cần soạn lại” |
| P-09 crash trước link | kill sau bước 4 | — | prepared+staged | — | `recover`: không đích ⇒ `unknown(TARGET_ABSENT)` ⇒ BLOCKED | việc dở; thử lại bằng lần mới |
| P-10 crash sau link | kill sau bước 5/6 | — | prepared+staged, đích cùng identity, bytes đúng | — | `recover` ⇒ published `recovered:true` ⇒ như P-01 | như P-01 sau recover |
| P-11 sửa tại chỗ trong cửa sổ | P-10 nhưng đích bị sửa trước recover (cùng identity, hash khác) | — | prepared+staged | — | `unknown` ⇒ BLOCKED | “Không xác định được bản đã tạo” |
| P-12 đích bị thay | P-10 nhưng đích khác identity (kể cả cùng hash) | — | prepared+staged | — | `unknown` ⇒ BLOCKED, không xóa đích | như P-11 |
| P-13 evidence thiếu/sai | `published` mất/hỏng; `request_id` trong file khác tên; `target`/`content` lệch; hai file kết thúc | — | — | — | `UNSUPPORTED(PRECONDITION_PROOF_MISSING)` | file vẫn dùng được, không nghiệm thu máy |
| P-14 hai recover / recover khi publish chạy | cùng `rid` | lần sau `BUSY` | không thêm | — | — | “Đang xử lý, thử lại sau” |
| P-15 entrypoint đổi | `tools/publish_new.py` khác pin, hay chỉ khai `tool:"publish_new"` | (không biết) | bất kỳ | ghi runtime theo R-MUTATION ⇒ BLOCKED | BLOCKED | “Công cụ ghi chưa được nhận” |
| P-16 stale sau bàn giao | user sửa file; hoặc xác nhận nêu bản cũ | — | published | — | `NOT_MET(CHANGED_AFTER_PUBLISH)`; `USER_ACCEPTANCE_STALE` | nghiệm thu bản đang có = task mới |
| P-17 ghi evidence thất bại | đầy ổ ở bước 3 / 7 | bước 3 từ chối; bước 7 `PUBLISHED_EVIDENCE_PENDING` | prepared(+staged) | — | BLOCKED đến `recover` | đã tạo file nhưng bằng chứng chưa xong |
| P-18 review bắt buộc | policy ∪ extra_review_phases đòi review hoặc content_use=sign | UNSUPPORTED/BLOCKED trước mọi ghi phụ thuộc | không | BLOCKED, không publish rồi chặn accept | review ngoài capability bản đầu; non-PASS/veto và behavior v1/legacy giữ nguyên, D4 không thay review | không tự duyệt |
| P-19 nghiệm thu không đủ | im lặng, mở file, “ok” không nêu bản, thiếu REQ-2 | — | — | — | `NOT_CHECKED`/`USER_ACCEPTANCE_INCOMPLETE` ⇒ BLOCKED | không bị hỏi lại nếu không cần accept |
| P-20 bản sửa lặp | v2 `supersedes` v1; hai v2 cùng supersede | publish file mới | chuỗi | — | đầu chuỗi duy nhất; nhánh ⇒ `AMBIGUOUS` | “Có hai bản sửa song song, bản nào dùng?” |

**Đề xuất Worker ban đầu cho M-1…M-5 (lịch sử, đã có disposition Main ngay dưới; các câu khác chiều trong đề xuất cũ không còn hiệu lực):** M-1 owner mới; M-2 evidence là tác động nội bộ; M-3 tập con D4; M-4 P-CN1 trước/song song A0; M-5 không tự dọn.

#### Disposition Main và review độc lập M-1…M-5 (18/10/2026)

Reviewer độc lập `roadmap_independent_audit` (`gpt-6.1-sol`, effort High) xác minh bản đầu vào `692978f4bef93f24`, review thiết kế và nguồn chính thức; verdict **CHANGES_REQUIRED**, không code/test/probe. Main chốt như sau; các câu trong đề xuất Worker chưa khớp phải được sửa theo disposition này trước dispatch implementation.

| M | Quyết định Main | Điều kiện/giới hạn |
|---|---|---|
| M-1 | Chọn hướng owner riêng `tools/publish_new.py` cho một output create_new, tái dùng helper thay vì mở rộng Transaction; nhận hướng kỹ thuật, chưa nhận protocol hoàn chỉnh hoặc đóng R-7 | Bản đầu chỉ Windows + NTFS local đã kiểm; không bắt POSIX/network/cloud trong tranche này. Phải sửa linkage và recovery dưới đây; hệ chưa có proof giữ UNSUPPORTED/BLOCKED. |
| M-2 | **SCOPE_ACCEPTED_FOR_VERSIONED_AMENDMENT.** Main chọn amendment hẹp dưới đây theo quyền operator giao audit kỹ và tự chọn phương án ngày18/10; không hỏi lại điểm này | Chỉ entrypoint/version P-CN1 và envelope được nhận, không miễn bằng nhãn tool/nội bộ. Worker thiết kế amendment versioned; policy hiện hành giữ nguyên tới khi amendment, implementation và integration được review/nhận đúng bước. Chưa activation hoặc miễn route đang hiệu lực. |
| M-3 | Chọn nghiệm thu cho use case một action với **đủ binding D4 hiện hành**, không chọn dừng vĩnh viễn ở candidate để gọi G hoàn tất | Phải có task_id/revision/accepted_task_digest, result_id, đủ mandatory requirements, accepted_artifacts EXACT đúng path/digest và presented_summary cùng nguồn xác nhận rõ. Cố định snapshot task/yêu cầu/input trước publish; user không phải gõ metadata. Chưa có các phần này thì accept BLOCKED; không nhận subset bỏ điều kiện bắt buộc. |
| M-4 | Chọn thứ tự **tuần tự**: contract API/evidence P-CN1 được nhận → implementation P-CN1 + S4-min tools-only có review → A0/checker theo mapping đã chốt | Chưa dispatch code trước khi sửa thiết kế và giải M-2. Tools-only không activation hay cấp quyền bằng checker chưa có. Bỏ claim “A0 chỉ hai field” cho tới khi bảng 5.1 chỉ rõ amendment thực sự dùng/hoãn; không dựng hai owner policy hiệu lực. |
| M-5 | Không auto-GC metadata evidence trong prototype; không thêm GC engine | Staged chứa toàn nội dung, có vòng đời riêng: dọn bản thành công theo protocol được cấp quyền; lỗi/pending chỉ giữ khi cần phục hồi, không tự xóa dữ liệu/evidence chưa được phép. Mất/hỏng evidence ⇒ accept BLOCKED. Đường dẫn tương đối có thể chứa tên người; không claim metadata tự động vô danh hoặc staged không chứa nội dung. Chưa nhận chính sách retention phân phối mặc định. |

**M-2 — phạm vi Main đã chọn để thiết kế amendment có version; chưa có hiệu lực runtime.** Operator giao Main “audit kỹ và chọn phương án phù hợp, đừng có quay lại hỏi tôi” sau khi đã trình tradeoff M-2. Main chọn protocol P-CN1/version được nhận khai một envelope create_new gồm đúng một output trong working/output, tạo thư mục cha cần thiết, và housekeeping giới hạn dưới `.agent/runtime/publish/`: tạo mới `<rid>.prepared.json`, `.published.json`, `.conflict.json`, `.abandoned.json`, `.unknown.json`, `.staged`; chỉ dọn staged của chính rid theo điều kiện an toàn. Grant phải phủ envelope này, path/tool/binding/format/known-loss và review mà các tác động khác đòi vẫn giữ. Housekeeping đúng owner/version/envelope không phát sinh hai pha R-MUTATION riêng cho mỗi lần lưu nháp; agent ghi trực tiếp, ghi ngoài envelope hoặc sửa/xóa evidence vẫn đi route hiện hành. Không miễn toàn vùng runtime, không cấp quyền từ receipt, không claim chống giả owner trong ADVISORY. Amendment này thay nghĩa vụ review hiện hành đối với một số ghi runtime, nên **không** được mô tả là “không đổi routing/acceptance”. Policy hiện hành giữ nguyên cho tới khi amendment, implementation và integration được review/nhận đúng bước; không tự dịch evidence sang vùng khác để né route.

Phạm vi amendment chỉ áp dụng cho hành vi P-CN1 qua entrypoint/version và envelope đã được nhận; trường `tool`/`protocol` tự khai hoặc việc file nằm trong thư mục publish không đủ điều kiện. Không xác định được sự phù hợp thì phần phụ thuộc giữ BLOCKED; evidence không cấp grant, không thay recipe acceptance hoặc review bắt buộc khác. Reviewer độc lập Sol 6.1 High đã audit hẹp lựa chọn này, verdict READY_FOR_DESIGN_CORRECTION; việc nhận scope M-2 không nhận toàn P-CN1 hoặc giải năm finding còn lại.

**Sửa thiết kế bắt buộc, dùng owner hiện có, không thêm framework:**

1. PREPARED giữ hoặc resolve chính xác snapshot task/yêu cầu/requirements đã trình và revision input công cụ soạn thực sự dùng; hash đọc lại lúc publish chỉ là quan sát hiện tại, không thay digest input tạo staged. Nêu rõ DECLARED, không tự chứng minh model đã hiểu/đọc. Không resolve được thì gate phụ thuộc BLOCKED.
2. Viết mapping API → canonical task/action tường minh: `targets` và `content_use` theo đúng kiểu/tập C1, đủ accepted-task projection; không gọi payload `target` đơn là `action_proj`. Cố định binding trước publish, không dựng lại REQ-1 sau publish theo diễn giải mới. M-3 phải dùng snapshot này.
3. Recovery chỉ nhận PUBLISHED khi file thường, identity khả dụng, size/hash khớp PREPARED và không trạng thái mâu thuẫn; identity không thay kiểm bytes. Thiếu staged/published hoặc storage/evidence loss không đủ để kết luận NOT_PUBLISHED: giữ UNKNOWN/BLOCKED nếu không chứng minh được. Chặn/serialize publish–recover và recover–recover cùng rid; không giả hard link làm bytes bất biến. Chỉ scope process crash, không thêm durability/mất điện engine.
4. Liệt kê toàn bộ tác động trong envelope (tạo cha, JSON/staged, cleanup/recover) và thiết kế mapping routing versioned đúng phạm vi M-2 Main đã chọn. Chưa amendment/implementation/integration được nhận thì không áp route nhẹ mới. STATE/HANDOFF ngoài envelope vẫn giữ điều kiện 5.4.1; không chờ thêm quyết định operator cho phạm vi M-2 này.
5. Sửa ngay bảng 5.1–5.4 và 7.2 thành phần thực sự dùng cho một action và phần hoãn. Giữ các điều kiện 5.4 về STATE/runtime, sửa nháp lặp và một version hiệu lực; không ngầm nhận UX “luôn file mới” là hoàn tất. Chưa đủ mở A0 chỉ bằng việc chọn M-1…M-5. Dùng Windows/NTFS local làm môi trường đầu, POSIX là capability sau; sửa bảng kỳ vọng tương ứng, chưa chạy ca nào.

Căn cứ kỹ thuật đối chiếu: [Python 3.8 os.link](https://docs.python.org/3.8/library/os.html#os.link), [Microsoft — hard links](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions) (cùng file/cùng volume, thay nội dung qua một link thấy qua link khác), [Microsoft — file identity](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle) (giới hạn thông tin trên network). Chưa thử primitive, identity, handle hoặc crash trên môi trường thật; đây là review thiết kế, không proof implementation.

### 4.3.3 Contract P-CN1-C — API, evidence `publish-v1`, khóa, eligibility (design-only, chưa thi công)

**Trạng thái:** DESIGN_ACCEPTED_WITH_CONSTRAINTS cho P-CN1-I sau review bản `584fcba93ef7255e` và các sửa trực tiếp của Orchestrator trong mục này. Đây là contract tools-only, chưa schema/policy/vectors A0 được nhận, không đổi projection/version đang active (v2 vẫn CANDIDATE_NOT_ACTIVE). 4.3.3 là owner API/evidence mới hơn 4.3.2; chỉ dùng `at` và `inputs_observed_at_publish[].digest`, không nhận song song alias `created`/`sha256` của mô tả cũ. Snapshot control/3 và bind/3 vẫn candidate, không đưa qua schema v2 rồi gọi hợp lệ (từ A0 hẹp, snapshot đúng hình `build_task` hợp lệ dưới schema v3 candidate, kiểm bằng test; v3 chưa hiệu lực); đối chiếu vectors v2 chỉ chứng minh LAW-CJ/2 bytes. Phạm vi: Windows NTFS local, một action create_new, một output. Runtime chưa được kiểm; Proof ở I vẫn bắt buộc, chưa R-7 resolved/activation.

#### C-1. Signature (module `tools/publish_new.py`)

Kết quả protocol **không** dùng exception: mọi hàm trả `dict` có `outcome`, `reason` (hoặc `null`), `request_id` (hoặc `null`), `wrote` (danh sách đường dẫn tương đối project đã tạo/xóa trong lần gọi, theo thứ tự, mỗi phần tử `{path, op:"mkdir"|"create"|"link"|"delete", envelope:"T1".."T7"}`). Chỉ lỗi lập trình (sai kiểu tham số) ném `TypeError`/`ValueError`. Không hàm nào ghi ngoài T1–T7.

| Hàm | Input | Ghi | `outcome` có thể | Ghi chú |
|---|---|---|---|---|
| `publish(project_root: str, request: dict, staged: bytes, *, request_id: str = None) -> dict` (revision corrective 18/10: `request_id` 32 hex thường do caller chọn, ngoài JSON request; sai ⇒ REFUSED `REQUEST_ID_INVALID`, đã có file của rid ⇒ REFUSED `RID_TAKEN`; CLI `--rid`) | `request` theo C-2.1; `staged` ≤ `MAX_STAGED_BYTES` | T1–T7 | `PUBLISHED`, `CONFLICT`, `REFUSED`, `ABANDONED`, `UNKNOWN`, `PUBLISHED_EVIDENCE_PENDING` | `wrote` ghi đúng mọi T2/T3 đã xảy ra kể cả REFUSED/lock/evidence lỗi (T2 nay chỉ là mkdir `publish`); từ chối trước mutation (request, rid, thiếu `.agent`/`.agent/runtime`, link) chắc wrote rỗng. Trả thêm target, content và protection khi có; không báo chưa ghi gì nếu đã tạo runtime/prepared |
| `observe(project_root: str, *, target: str \| None = None, inputs: list \| None = None, request_id: str \| None = None) -> dict` | S4-min, chỉ đọc | không | `OBSERVED`, `UNSUPPORTED` | trả `{volume:{fs,local}, target:{exists, regular, identity?, sha256?, size?}, parents_link_free, inputs:[{path, sha256 \| null}], entrypoint_sha256, at}`; observation-at-time, không giữ handle sau khi trả |
| `status(project_root: str, request_id: str \| None = None) -> dict` | — | không, không khóa | `STATUS` | mỗi rid: `{request_id, files:[state…], staged_present, terminal \| null, consistent:bool}`; không kết luận nguồn gốc |
| `recover(project_root: str, request_id: str) -> dict` | rid 32 hex | T6, T7 | PUBLISHED (recovered:true), UNKNOWN, BUSY, REFUSED, NO_ACTION | Terminal phải hợp lệ/duy nhất mới báo NO_ACTION hoặc cleanup PUBLISHED khi staged identity khớp. Terminal hỏng/nhiều terminal ⇒ UNKNOWN(EVIDENCE_INCONSISTENT), không tạo terminal mới hoặc cleanup; theo C-3 |
| `discard_staged(project_root: str, request_id: str) -> dict` | rid | T7 | DISCARDED, BUSY, REFUSED (NO_TERMINAL, TERMINAL_IS_PUBLISHED, STAGED_ABSENT), UNKNOWN | Chỉ terminal duy nhất/hợp lệ ∈ {conflict, abandoned, unknown}; terminal hỏng/nhiều ⇒ UNKNOWN(EVIDENCE_INCONSISTENT), không ghi/xóa. Không tạo file discarded; lần hai REFUSED(STAGED_ABSENT) không lặp tác động |

CLI (bao quanh API, theo mẫu --result-json của tools/): publish --request <file.json> --staged <file>, observe --target <rel> [--input <rel>…] [--rid <rid>], status [<rid>], recover <rid>, discard-staged <rid>. File staged chỉ đọc, kiểm kích thước trước nạp. Mã thoát: 0 PUBLISHED/OBSERVED/STATUS/NO_ACTION/DISCARDED; 3 CONFLICT; 4 REFUSED/UNSUPPORTED; 5 ABANDONED/UNKNOWN/PUBLISHED_EVIDENCE_PENDING; 6 BUSY; 2 lỗi dùng. Status envelope: 0 success, 3/4/6 blocked, 5 partial. **Mọi mã thoát đều tính changes = bool(wrote)**; exit/status không chứng minh chưa tác động. STATUS thành công chỉ là query đã chạy, consistent=false không phải artifact/accept PASS.

`reason` theo `outcome` (đóng, chuỗi hoa):
- `REFUSED`: `REQUEST_INVALID`, `SNAPSHOT_INCOMPLETE`, `PATH_UNSUPPORTED_FORM`, `ZONE_NOT_LIGHT`, `AUTHORITY_NAME`, `CONTENT_USE_NOT_INTERNAL`, `REVIEW_REQUIRED_UNSUPPORTED`, `UNSUPPORTED_FS`, `INPUT_CHANGED_SINCE_READ`, `STAGED_TOO_LARGE`, `SNAPSHOT_TOO_LARGE`, `RUNTIME_LINKED`, `PARENT_UNSAFE`, `LOCK_UNAVAILABLE`, `RID_TAKEN`, `EVIDENCE_WRITE_FAILED`, `NO_TERMINAL`, `TERMINAL_IS_PUBLISHED`, `STAGED_ABSENT`.
- `ABANDONED` (ghi `<rid>.abandoned.json`): `STAGE_FAILED`, `STAGE_HASH_MISMATCH`, `PARENT_CREATE_FAILED`, `LINK_FAILED`.
- `CONFLICT`: `TARGET_EXISTS`.
- `UNKNOWN`: `POST_LINK_MISMATCH`, `TARGET_ABSENT`, `STAGED_ABSENT`, `IDENTITY_MISMATCH`, `IDENTITY_UNAVAILABLE`, `TARGET_MODIFIED`, `TARGET_NOT_REGULAR`, `PREPARED_UNREADABLE`, `EVIDENCE_INCONSISTENT`, `EVIDENCE_WRITE_FAILED`. Chỉ tạo unknown.json khi chuyển trạng thái cho phép và chưa có terminal; evidence hỏng/multiple terminal không tạo file mới/cleanup. Outcome trả về không đồng nhất với state file đã ghi thành công.
- `UNSUPPORTED` của observe: `PATH_UNSUPPORTED_FORM`, `UNSUPPORTED_FS`, `RUNTIME_LINKED`, `PARENT_UNSAFE`, `IDENTITY_UNAVAILABLE`, `EVIDENCE_INCONSISTENT`, `OBSERVATION_UNAVAILABLE`. `BUSY`: `LOCK_BUSY`; lỗi khóa không phải contention dùng REFUSED(LOCK_UNAVAILABLE), không giả BUSY.
- `PUBLISHED_EVIDENCE_PENDING`: `PUBLISHED_WRITE_FAILED` (link đã xảy ra; có thể chưa có terminal hoặc có published rỗng/hỏng sau O_EXCL). Không rewrite file để sửa lịch sử; recover chỉ đóng khi không có terminal filename và đủ proof. Terminal hỏng ⇒ BLOCKED/UNKNOWN, giữ nguyên để chẩn đoán.

Lỗi ghi terminal khác sau O_EXCL cũng có thể để file hỏng: trả UNKNOWN(EVIDENCE_WRITE_FAILED) với wrote thực tế, không tạo terminal thứ hai để che lỗi. PUBLISHED/NO_ACTION có proof published hợp lệ nhưng T7 chưa dọn được dùng reason STAGED_CLEANUP_PENDING và cleanup_pending:true; giữ proof/output, wrote không chứa delete nếu chưa yêu cầu xóa thành công. Nếu disposition xóa qua handle đã được đặt nhưng tên staged còn tới khi reader share-delete đóng, wrote vẫn ghi T7 và cleanup_pending:true; DISCARDED cũng dùng STAGED_CLEANUP_PENDING trong đúng trường hợp này (effect xóa đã yêu cầu, chưa hoàn tất dọn tên). Đây là diagnostic được Orchestrator/Reviewer nhận sau corrective I, không thêm reason/state/version hay nới điều kiện xóa. Các kết quả thành công khác reason=null. Không phát minh thao tác bù xóa output.

**Giới hạn implementation I được nhận:** trên Windows NTFS local, publish/recover/discard đòi pin thư mục trước mutation, không lấy được ⇒ từ chối; publish không chạy fallback recheck_only như hướng thiết kế cũ4.3.2. REFUSED có thể thêm `detail:ROOT_LINKED` hoặc `PIN_UNAVAILABLE` trong kết quả API/JSON đầy đủ; không đổi schema evidence. Recover chỉ đọc target và vẫn công bố protection=recheck_only, không claim race-free. Reader/status/observe không cần pin ghi. Đây là thu hẹp capability an toàn trong prototype, không hạ route/grant/review.

Hằng số đề xuất: `MAX_STAGED_BYTES = 104 857 600` (100 MiB); `MAX_JSON_BYTES = 1 048 576` (1 MiB); `LOCK_OFFSET = 1 073 741 824` (2^30, > `MAX_JSON_BYTES`, < 2^31); `LOCK_LEN = 1`.

#### C-2. Shape dữ liệu

**C-2.1 `request` của `publish`** (object, khóa ngoài danh sách ⇒ `REQUEST_INVALID`):

| Khóa | Bắt buộc | Kiểu | Đi vào |
|---|---|---|---|
| `work_id` | có | `$defs/id` | `task.work_id` |
| `target` | có | path POSIX tương đối, NFC | `actions[0].targets = [target]`, `expected_outputs = [target]` |
| `content_use` | có khi target dưới `output/` | `["internal_draft"]` | `actions[0].content_use`; dưới `working/` phải vắng |
| `intent_ref` | có | `{ref_id, locator, digest, attribution}` (`attributed_ref`, `kind` do công cụ đặt `user_intent`) | `intent.refs = [..]` |
| `main_interpretation` | có | chuỗi ≥1 | `intent.main_interpretation` |
| `unconfirmed` | không | mảng chuỗi | `intent.unconfirmed` |
| `requirements` | có | mảng `requirement` (≥1 `mandatory:true`) | `acceptance.requirements` |
| `grant_refs` | có, ≥1 | mảng `attributed_ref` (`kind` do công cụ đặt `grant`) | `authority.grant_refs` |
| `subject` | có | `actor` | `proposed_by`, `authority.subject`, `envelope.role = subject.role` |
| `inputs` | có (có thể rỗng nếu không có nguồn) | mảng `object_digest` | `inputs`; `digest` là bytes công cụ soạn đã đọc |
| `supersedes` | không | 32 hex | root `prepared.supersedes` (metadata, không bound) |

Công cụ **tự đặt**, không nhận từ caller: `task_id`, `task_revision`, `record_type`, `schema_version`, `evaluation_basis`, `actions[0].operation/tool/write_zone`, `effects.on_missing`, `kind` của ref. Không có trường cho `extra_review_phases`, `completion`, `protected_targets`, `preservation`, `context_refs`, `delegation`, `recipe`, `payload` trong v1 ⇒ có ⇒ `REQUEST_INVALID`.

**C-2.2 Serialization file evidence.** UTF-8 không BOM; LAW-CJ/2 giữ đúng C1 4.1, số nguyên trong ±(2^53−1), không trailing newline, ≤ MAX_JSON_BYTES. Reader parse strict rồi serialize lại và so **đúng raw bytes**: whitespace/key order khác vẫn parse JSON được nhưng không phải wire canonical; khóa trùng, số ngoài miền, chuỗi không NFC, schema/key lạ đều bị từ chối. Không chuẩn hóa hộ. Receipt digest băm raw published bytes. I cài serializer private trong owner tools/, đối chiếu cả vector hợp lệ/UNSUPPORTED v2; không import .cvf/checks hoặc sửa canonical spec/vectors. Việc này không nhận schema/binding v3.

**C-2.3 Các state `publish-v1`** (mọi state: `schema = "local-agent-workspace/publish-v1"`, `protocol = "P-CN1"`, `protocol_version = 1`, `request_id` = 32 hex thường trùng tên file, `state`, `at` = UTC `YYYY-MM-DDTHH:MM:SSZ`; khóa lạ, version khác ⇒ `UNSUPPORTED`):

| State (file) | Bắt buộc thêm | Tùy chọn | Ràng buộc |
|---|---|---|---|
| `PREPARED` (`<rid>.prepared.json`) | `task` (C-2.4), `content {sha256: digest, size: int ≥0}`, `inputs_observed_at_publish [{path, digest}]` (cùng tập path với `task.inputs`, digest bằng nhau), `platform: "windows-ntfs-local"`, `entrypoint_sha256: digest` (hash file script đang chạy, tự đo, ADVISORY) | `supersedes` | ghi một lần sau recheck; file rỗng = đang chuẩn bị hoặc hỏng |
| `PUBLISHED` (`<rid>.published.json`) | target, content, identity {volume_serial: chuỗi 8 hex thường, file_index: chuỗi 16 hex thường}, nlink_at_check: int ≥2, protection ∈ {held, recheck_only}, recovered: bool | — | target/content khớp prepared; adapter OS→hex giữ đủ 32/64 bit, không truncate. API observe/evidence dùng cùng biểu diễn; identity không khả dụng/không xác minh được ⇒ không dùng cho recovery |
| `CONFLICT` | `reason = "TARGET_EXISTS"` | `detail` ≤200 ký tự | không đường dẫn tuyệt đối/tên người ngoài path tương đối |
| `ABANDONED` | `reason` (C-1) | `detail` | chỉ tiến trình publish ghi |
| `UNKNOWN` | `reason` (C-1), `by ∈ {publish, recover}` | `detail` | — |

Tối đa một file trong `{published, conflict, abandoned, unknown}` mỗi rid (bảo đảm bằng `O_EXCL` từng tên **và** kiểm terminal dưới khóa trước khi tạo, C-3).

**C-2.4 `task` snapshot và mapping canonical.** Shape = record `task` của C1 (`$defs/task` v2) với `schema_version = "law.cvf.control/3"` **đề xuất**: snapshot này không hợp lệ dưới schema v2 (`const`) và chỉ là thiết kế tới khi A0 chọn version; không đổi `/2`. Trường và projection:

| Trường task | Giá trị P-CN1 v1 | Trong projection `task` (C1 4.2)? |
|---|---|---|
| `record_type` | `"task"` | không (loại trừ) |
| `schema_version`, `evaluation_basis` | `/3` đề xuất, `COOPERATIVE_WORKFLOW` | có |
| `work_id`, `task_id = "pcn1-<rid>"`, `task_revision = 1` | — | có |
| `proposed_by` | = `subject` | không (loại trừ) |
| `intent.refs` | 1 ref `user_intent` | qua `intent_digest` (`set(ref_proj)` = `{digest, kind, revision?}`) |
| `intent.main_interpretation`, `unconfirmed?` | — | có |
| `authority.subject` | `{actor_id, role}` | có; `host`/`session_ref` loại trừ |
| `authority.grant_refs` | ≥1 | `set(ref_proj)`; locator/attribution loại trừ |
| `inputs` | set `obj_proj` | có |
| `effects.actions[0]` | `{operation:"create_new", tool:"publish_new", targets:[target], write_zone:"working"\|"output_new", content_use?:["internal_draft"]}` | có (`action_proj`); `targets`/`content_use` là set |
| `effects.expected_outputs` | `[target]` | có (set) |
| `effects.on_missing` | `"STOP_DEPENDENT_EFFECT"` | có |
| `acceptance.requirements` | như request, thứ tự giữ | có |
| `envelope` | `{role: subject.role}` | có |

**Không bound** (metadata chẩn đoán/quan sát, không vào `accepted_task_digest`): root `prepared.supersedes`, `at`, `inputs_observed_at_publish`, `platform`, `entrypoint_sha256`; các trường `published` ngoài `target`/`content` (identity, nlink, protection, recovered). `content` gắn qua `E_out.outcome.artifacts`/`result.artifacts` và `receipt_ref.digest`. Alias created của mô tả cũ không thuộc wire contract. Muốn bind supersedes thì cần amendment canonical ở A0 (không làm ở đây).

**Mapping D4 (M-3)** — `result.user_acceptance` (4.7.3), công cụ dựng từ evidence, user không gõ:

| Trường D4 | Lấy từ |
|---|---|
| `task_id`, `task_revision` | `prepared.task` |
| `accepted_task_digest` | projection `task` C1 trên `prepared.task` (tính lại, không lưu sẵn) |
| `accepted_requirements` | tập `req_id` user xác nhận; phải ⊇ mọi `mandatory` trong `prepared.task.acceptance.requirements` |
| `result_id` | `"pcn1-r-<rid>"` |
| `accepted_artifacts` | `[{path: published.target, digest: published.content.sha256}]` + `role:"ACTUAL_BYTES"`; EXACT với `result.artifacts` |
| `presented_summary` | `{locator, digest}` của tin nhắn tóm tắt agent đã trình (yêu cầu, tên file, 8 ký tự hash) |
| `ref` | `attributed_ref` kind `user_acceptance`, `USER_CONFIRMATION`, channel `USER_MESSAGE`/`HOST_CONFIRMATION_UI`, `evidence_locator` resolve được tới lời xác nhận hợp tác đã quan sát |

`E_out.receipt_ref` = `attributed_ref {ref_id:"receipt-<rid>", kind:"effect_receipt", locator:".agent/runtime/publish/<rid>.published.json", digest, attribution:{source_class:"TOOL_OBSERVATION", channel:"TOOL_OUTPUT", recorded_by:{actor_id:"publish_new", role:"tool"}, observed_by:{actor_id:"publish_new", role:"tool"}}}`; field `receipt_ref` trên `effect` là đề xuất cho A0.

#### C-3. Khóa, handle và chuyển trạng thái

**Khóa chung mỗi rid** = byte `[LOCK_OFFSET, LOCK_OFFSET+1)` trên `<rid>.prepared.json`, lấy bằng `os.lseek(fd, LOCK_OFFSET, SEEK_SET)` rồi `msvcrt.locking(fd, LK_NBLCK, 1)` (nonblocking; lỗi ⇒ `LOCK_UNAVAILABLE`/`BUSY`, không chờ, không thử lại). Trước mọi đọc/ghi nội dung: `os.lseek(fd, 0, SEEK_SET)`. Nhả: `lseek(LOCK_OFFSET)` → `msvcrt.locking(fd, LK_UNLCK, 1)` → `os.close(fd)`. Không ghi byte nào ngoài `MAX_JSON_BYTES`; không ghi dummy byte để mở rộng file. Mở bằng `os.open(path, O_RDWR | O_BINARY [| O_CREAT | O_EXCL])`. Reader không khóa (`status`, `observe`, checker) mở chỉ đọc và chỉ đọc `[0, size)`. Khóa chỉ phối hợp các lần gọi đúng protocol; không chặn người/ứng dụng khác sửa JSON, staged hay target.

**Ai giữ khóa khi nào:**

| Lời gọi | Lấy khóa | Giữ tới | Mọi ghi T3/T4/T6/T7 của rid chỉ khi đang giữ |
|---|---|---|---|
| `publish` | ngay sau `O_EXCL` tạo `prepared` (file rỗng) | sau bước 7 (hoặc khi trả lỗi) | có |
| `recover` | mở `prepared` sẵn có | khi trả | có |
| `discard_staged` | như recover | khi trả | có |
| T1 (mkdir cha), T5 (link) | dưới khóa publish | — | — |
| T2 (runtime bootstrap), bootstrap O_EXCL tạo PREPARED rỗng | **trước** khóa rid vì cần đường dẫn/file để lấy khóa | kiểm path/link/volume và grant/envelope trước tác động | chỉ ngoại lệ bootstrap này; wrote ghi mọi directory/file thực sự tạo, không gọi là chưa ghi gì |

**Recheck sau khóa theo operation:** publish phải chưa có terminal, fstat(fd) khớp identity prepared hiện tại và size=0 đúng file vừa tạo; không đạt ⇒ REFUSED(RID_TAKEN), không stage/link. Recover/discard đọc lại dưới khóa, không dùng snapshot trước khóa: recover có thể đọc terminal duy nhất/hợp lệ để báo hoặc cleanup PUBLISHED; discard bắt buộc terminal duy nhất/hợp lệ trong tập cho phép. Terminal hỏng/nhiều/không nhất quán ⇒ UNKNOWN(EVIDENCE_INCONSISTENT), status consistent=false, không NO_ACTION thành công, không ghi terminal mới/cleanup. Chỉ recover không có terminal filename mới xét tạo terminal theo proof.

**T7:** chỉ unlink đúng `.agent/runtime/publish/<rid>.staged` dưới khóa rid, sau kiểm path/file hiện tại là file thường, không symlink/junction/reparse point và đúng điều kiện nhánh; hard link staged↔output hợp lệ không bị nhầm là symlink. PUBLISHED cleanup cần staged identity khớp published; discard cần lệnh rõ và terminal hợp lệ. Không theo đường dẫn khác, xóa output hoặc JSON evidence; grant delete chỉ được tiêu thụ trong T7, không thành quyền delete rộng trên các path khác của grant. Discard không cần file discarded. Khóa bootstrap không tự freeze nội dung; mọi nhánh không chứng minh được giữ BLOCKED và báo wrote trung thực.

**Chuyển trạng thái** (chỉ các cạnh này; mọi tổ hợp khác ⇒ `consistent:false` ở `status`, accept BLOCKED):

```text
∅ ──publish: O_EXCL+lock+recheck──▶ PREPARED(rỗng) ──ghi snapshot──▶ PREPARED
PREPARED ──stage lỗi──────────────▶ ABANDONED (staged có thể còn)
PREPARED ──mkdir/link lỗi─────────▶ ABANDONED | CONFLICT(TARGET_EXISTS)
PREPARED ──kiểm sau link lệch────▶ UNKNOWN(by=publish), staged giữ
PREPARED ──published ghi được────▶ PUBLISHED, rồi T7 xóa staged
PREPARED ──published ghi lỗi─────▶ (không terminal) outcome PUBLISHED_EVIDENCE_PENDING
PREPARED(không khóa, không terminal) ──recover──▶ PUBLISHED(recovered) | UNKNOWN(by=recover)
PREPARED(rỗng, không khóa) ──recover──▶ UNKNOWN(PREPARED_UNREADABLE)
terminal ∈ {CONFLICT, ABANDONED, UNKNOWN} + staged ──discard_staged──▶ (staged xóa, không file mới)
PUBLISHED + staged còn (crash giữa published và T7) ──recover──▶ T7 xóa staged nếu identity staged = published.identity, NO_ACTION nếu không
```

Proof ở I (chưa kiểm, không coi là đã đạt): khóa ngoài EOF thực sự không chặn đọc `[0,size)` khi file mở từ process khác; khóa tự nhả khi process chết (kill); `os.open` mở với share mode cho phép reader; `msvcrt.locking` nhận offset 2^30; `os.fstat`/`os.stat` trên Windows trả `st_dev`/`st_ino` tương ứng volume serial/file index ổn định; `os.link` báo `FileExistsError` cả khi chỉ khác hoa/thường; cách đọc `fs=NTFS`, `local` (loại ổ cố định) từ Python.

#### C-4. Eligibility trước tác động ≠ receipt/bytes sau publish

| Điều kiện | d (dispatch) | e (effect, ngay trước gọi `publish`) | a (accept) | Nguồn |
|---|---|---|---|---|
| Route T5 = R-READ_DRAFT (B)/(C), đủ 7 điều kiện 2.5 | cần | cần | cần | policy + snapshot |
| Không pha review nào đòi (policy ∪ extra) | cần; có ⇒ `UNSUPPORTED(REVIEW_REQUIRED_UNSUPPORTED)` **trước mọi ghi** | cần | cần | policy + snapshot (v1 không có `extra_review_phases`) |
| Grant phủ toàn envelope áp dụng: `tools ⊇ {publish_new}`; `operations ⊇ {create_new, delete}`; `paths` phủ tổ tiên/target (T1, T5) và `.agent/runtime/publish/` (T2–T4, T6, T7) | cần | cần | cần (chạy lại) | grant record |
| Protocol/version/entrypoint trong `owner_protocols` được nhận | cần | cần | cần | policy |
| S4-min cùng lượt: `entrypoint_sha256` hiện tại = pin; volume NTFS local; cha link-free; target vắng (observation-at-time) | cần | cần | — (không kiểm “đích hiện vắng”) | `observe()` |
| Snapshot đủ (C-2.1), input hiện tại = digest đã đọc | — | cần (chính `publish` cũng kiểm bước 1–2) | — | `observe()` / `publish` |
| `published` hợp lệ + `receipt_ref` resolve + liên kết rid/snapshot + runtime file của rid ⊂ T3/T4/T6 | **không đòi** (chưa có) | **không đòi** | cần | evidence |
| Bytes hiện tại của target = `published.content` | — | — | cần (S4-min) | `observe()` |
| D4 đủ (C-2.4) | — | — | cần cho REQUIREMENTS | result + user |

Grant có `delete` chỉ để phủ T7; envelope giới hạn T7 vào staged của chính rid, còn agent tự xóa/sửa evidence vẫn theo route hiện hành (R-MUTATION) dù grant có `delete`. Không dùng kết quả a để mở d/e; không tạo receipt trước để mở effect. Thiếu điều kiện ở d/e ⇒ ghi runtime theo route hiện hành (R-MUTATION) ⇒ BLOCKED; P-CN1 không tự kiểm grant/route (agent/integration kiểm trước khi gọi). Hash entrypoint và receipt là ADVISORY: không chứng minh process nào thực sự đã ghi, không chống giả.

#### C-5. Ví dụ mapping minh họa (dữ liệu giả, có placeholder; không phải fixture JSON hợp lệ; I phải dựng fixture đầy đủ từ dữ liệu giả và băm thật theo C-1…C-4)

```text
request (publish --request):
{"grant_refs":[{"attribution":{"channel":"USER_MESSAGE","evidence_locator":"host:msg/0007","recorded_by":{"actor_id":"main","role":"main"},"source_class":"USER_CONFIRMATION"},
                "digest":"sha256:1111111111111111111111111111111111111111111111111111111111111111","locator":"PROJECT.md#pham-vi","ref_id":"grant-1"}],
 "inputs":[{"digest":"sha256:a90d000000000000000000000000000000000000000000000000000000000000","path":"references/source-documents/team/quy-che-gia.pdf"}],
 "intent_ref":{"attribution":{"channel":"USER_MESSAGE","evidence_locator":"host:msg/0012","recorded_by":{"actor_id":"main","role":"main"},"source_class":"USER_CONFIRMATION"},
               "digest":"sha256:51c0000000000000000000000000000000000000000000000000000000000000","locator":"host:msg/0012","ref_id":"intent-1"},
 "main_interpretation":"Báo cáo ngắn về mục giá",
 "requirements":[{"mandatory":true,"req_id":"REQ-1","statement":"Tóm tắt mục giá"},{"mandatory":true,"req_id":"REQ-2","statement":"Nêu điểm chưa chắc"}],
 "subject":{"actor_id":"main","role":"main"},
 "target":"working/w-20261018-01/bao-cao-nhap.docx","work_id":"w-20261018-01"}
staged: 18432 bytes, sha256 b7e1000000000000000000000000000000000000000000000000000000000000

.agent/runtime/publish/4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a.prepared.json:
{"at":"2026-10-18T09:15:02Z","content":{"sha256":"sha256:b7e1000000000000000000000000000000000000000000000000000000000000","size":18432},
 "entrypoint_sha256":"sha256:e0e0000000000000000000000000000000000000000000000000000000000000",
 "inputs_observed_at_publish":[{"digest":"sha256:a90d000000000000000000000000000000000000000000000000000000000000","path":"references/source-documents/team/quy-che-gia.pdf"}],
 "platform":"windows-ntfs-local","protocol":"P-CN1","protocol_version":1,"request_id":"4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a",
 "schema":"local-agent-workspace/publish-v1","state":"PREPARED",
 "task":{"acceptance":{"requirements":[…như request…]},
         "authority":{"grant_refs":[{…như request, "kind":"grant"…}],"subject":{"actor_id":"main","role":"main"}},
         "effects":{"actions":[{"operation":"create_new","targets":["working/w-20261018-01/bao-cao-nhap.docx"],"tool":"publish_new","write_zone":"working"}],
                    "expected_outputs":["working/w-20261018-01/bao-cao-nhap.docx"],"on_missing":"STOP_DEPENDENT_EFFECT"},
         "envelope":{"role":"main"},"evaluation_basis":"COOPERATIVE_WORKFLOW",
         "inputs":[{"digest":"sha256:a90d…(như trên)","path":"references/source-documents/team/quy-che-gia.pdf"}],
         "intent":{"main_interpretation":"Báo cáo ngắn về mục giá","refs":[{…intent_ref, "kind":"user_intent"…}]},
         "proposed_by":{"actor_id":"main","role":"main"},"record_type":"task","schema_version":"law.cvf.control/3",
         "task_id":"pcn1-4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a","task_revision":1,"work_id":"w-20261018-01"}}

projection để băm (đối chiếu C1 4.2; giá trị digest không tính ở đây):
 action_digest       ← {"action":{"operation":"create_new","targets":["working/w-20261018-01/bao-cao-nhap.docx"],"tool":"publish_new","write_zone":"working"},"bind":"law.cvf.bind/3 (đề xuất)","part":"action"}
 intent_digest       ← {"bind":…,"part":"intent","refs":[{"digest":"sha256:51c0…","kind":"user_intent"}]}
 accepted_task_digest← {"acceptance":…,"bind":…,"effects":{"actions":[action_proj],"expected_outputs":[…],"on_missing":"STOP_DEPENDENT_EFFECT"},"envelope":{"role":"main"},
                        "evaluation_basis":…,"grant_refs":[{"digest":"sha256:1111…","kind":"grant"}],"inputs":[{"digest":"sha256:a90d…","path":"references/…/quy-che-gia.pdf"}],
                        "intent_digest":…,"main_interpretation":…,"part":"task","schema_version":…,"subject":{"actor_id":"main","role":"main"},
                        "task_id":"pcn1-4c2f…","task_revision":1,"work_id":"w-20261018-01"}

os.link(.agent/runtime/publish/4c2f….staged, working/w-20261018-01/bao-cao-nhap.docx) → OK; kiểm sau link đạt

.agent/runtime/publish/4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a.published.json:
{"at":"2026-10-18T09:15:03Z","content":{"sha256":"sha256:b7e1…","size":18432},"identity":{"file_index":"0001000000000242","volume_serial":"abcdef01"},
 "nlink_at_check":2,"protection":"held","protocol":"P-CN1","protocol_version":1,"recovered":false,
 "request_id":"4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a","schema":"local-agent-workspace/publish-v1","state":"PUBLISHED",
 "target":"working/w-20261018-01/bao-cao-nhap.docx"}
→ T7 xóa staged; publish trả {outcome:"PUBLISHED", reason:null, wrote:[T2 mkdir .agent/runtime/publish (nếu thiếu), T3 create prepared, T4 create staged, T1 mkdir working/w-20261018-01, T5 link target, T6 create published, T7 delete staged]}

result (bộ nhớ) {result_id:"pcn1-r-4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a", artifacts:[{path:"working/w-20261018-01/bao-cao-nhap.docx", digest:"sha256:b7e1…"}], acceptance_states:["CANDIDATE"], …}
user: "Đồng ý bản b7e1 đáp ứng REQ-1, REQ-2" (host:msg/0031)
user_acceptance {ref:{ref_id:"ua-1", kind:"user_acceptance", locator:"host:msg/0031", digest:"sha256:…", attribution:{source_class:"USER_CONFIRMATION", channel:"USER_MESSAGE", evidence_locator:"host:msg/0031", recorded_by:{actor_id:"main",role:"main"}}},
  task_id:"pcn1-4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a", task_revision:1, accepted_task_digest:<tính lại từ projection trên>,
  accepted_requirements:["REQ-1","REQ-2"], result_id:"pcn1-r-4c2f9e0a4c2f9e0a4c2f9e0a4c2f9e0a",
  accepted_artifacts:[{path:"working/w-20261018-01/bao-cao-nhap.docx", digest:"sha256:b7e1…", role:"ACTUAL_BYTES"}],
  presented_summary:{locator:"host:msg/0030", digest:"sha256:…"}}
```

Ví dụ dùng `bind/3` đề xuất vì snapshot là `/3`; với `/2` đang active, projection giữ literal `law.cvf.bind/2` và snapshot `/3` không hợp lệ — đúng ý “không đổi version đang active”.

#### C-6. Bổ sung bảng kỳ vọng (chưa chạy)

| Ca | Thiết lập | Kỳ vọng |
|---|---|---|
| P-21 recover chen trước publisher | recover lấy khóa khi `prepared` vừa tạo rỗng, ghi `unknown(PREPARED_UNREADABLE)` | publisher lấy khóa, recheck thấy terminal ⇒ `REFUSED(RID_TAKEN)`, không stage/link; accept BLOCKED |
| P-22 request có trường v1 không hỗ trợ | `extra_review_phases`, `protected_targets`, `context_refs` | `REFUSED(REQUEST_INVALID)`, `wrote=[]` |
| P-23 staged quá lớn / JSON vượt 1 MiB | `staged` > 100 MiB; snapshot serialize > 1 MiB | `REFUSED(STAGED_TOO_LARGE)` / `REFUSED(SNAPSHOT_TOO_LARGE)` trước PREPARED |
| P-24 discard sai lúc | `discard_staged` khi chưa terminal hoặc terminal là `published` | `REFUSED(NO_TERMINAL / TERMINAL_IS_PUBLISHED)`, không xóa |
| P-25 crash giữa published và T7 | `published` có, staged còn | `recover` xóa staged nếu identity khớp ⇒ `NO_ACTION`/dọn; accept như P-01 |
| P-26 file JSON không canonical/khóa lạ | sửa tay published.json | strict parse + serialize so raw bytes/schema; whitespace/key order khác cũng từ chối, không chỉ dựa JSON parse; receipt digest lệch ⇒ BLOCKED |
| P-27 identity vượt miền integer LAW-CJ/2 | OS file index >2^53−1 và tới biên 64 bit | hex16 round-trip đúng; evidence không chứa số integer vượt miền, serializer không nới chuẩn |
| P-28 terminal hỏng/nhiều | recover/discard dưới khóa thấy evidence không nhất quán | UNKNOWN(EVIDENCE_INCONSISTENT), wrote=[], không terminal mới/cleanup/NO_ACTION thành công |
| P-29 bootstrap rồi khóa/ghi lỗi | T2/T3 đã xảy ra trước lỗi | wrote/changes ghi đúng mọi tạo/xóa; không nói REFUSED luôn chưa ghi; terminal partial giữ BLOCKED, không rewrite |
| P-30 cleanup đúng phạm vi | staged sai identity/reparse hoặc discard lần hai | không xóa nhầm output/evidence; identity sai dừng cleanup, lần hai REFUSED(STAGED_ABSENT) không lặp tác động |

### 4.4 Occurrence, tập action phải hoàn thành, coverage nhiều action/output (F6)

**Occurrence.** `occurrence = (task_id, task_revision, action_index, action_digest)`; trong record đã gắn task thì ghi `{index, digest}`. Hai action cùng digest ở hai index là **hai occurrence**. `actions_checked`, `effect.action_index`, `result.actions_performed[]` đều dùng occurrence; **không dùng tập digest trần**. Một effect/outcome thuộc đúng một occurrence, không suy ra đã thực hiện occurrence khác cùng digest. Index không resolve, hoặc `projection(task.actions[index]) ≠ effect.action` ⇒ `BINDING_MISMATCH`.

**Nghĩa vụ thực hiện ≠ nghĩa vụ kiểm outcome (D2).** `completion` chỉ quyết occurrence có *bắt buộc phải thực hiện* hay không; tập `REQUIRED` lấy từ **task đã chấp nhận** (vắng = REQUIRED; `accepted_task_digest` đã bind cờ; PRE_EFFECT phải phủ `accepted_task` nên Reviewer thấy cờ). Result/Main **không** khai tập con nhỏ hơn để bỏ yêu cầu. Nhưng mọi occurrence — **kể cả `OPTIONAL`** — mà (i) có effect OUTCOME ở bất kỳ trạng thái, hoặc (ii) được khai đã thực hiện (có trong `result.actions_performed`, hoặc `acceptance_states` chứa `EFFECT_APPLIED` gắn tới occurrence, hoặc artifact của nó nằm trong `result.artifacts`), **đều đến hạn ACTUAL_OUTCOME và reconcile**. Bỏ claim hoặc bỏ record không phải bằng chứng “không có tác động” khi bằng chứng mâu thuẫn đã có ở nơi khác.

**Cách đối chiếu (C), EXACT, không dùng số lần xuất hiện record làm proof số lần thao tác thật:**
1. mọi occurrence `REQUIRED` phải có đúng một OUTCOME `APPLIED`; thiếu ⇒ `ACTION_INCOMPLETE`.
2. `result.actions_performed` = tập occurrence có OUTCOME `APPLIED` (cả `OPTIONAL`): thiếu một ⇒ `ACTION_UNREPORTED`; liệt kê mà không có OUTCOME `APPLIED` ⇒ `ACTION_CLAIM_WITHOUT_OUTCOME`; occurrence ngoài task ⇒ `BINDING_MISMATCH`.
3. `result.artifacts` = hợp `outcome.artifacts` của các OUTCOME `APPLIED` (EXACT); artifact không quy được về OUTCOME ⇒ `ARTIFACT_UNATTRIBUTED`; artifact của OUTCOME `PARTIAL`/`UNKNOWN` không được tính vào result và là phần chưa reconcile.
4. task **không có** occurrence `REQUIRED`: hợp lệ về cấu trúc; ACTUAL_OUTCOME là `NOT_REQUIRED` **chỉ khi** không có OUTCOME, không claim thực hiện và `result.artifacts` rỗng; có bất kỳ cái nào ⇒ đến hạn đầy đủ. REQUIREMENTS vẫn đến hạn nên task “không làm gì” không tự đạt.

| Trạng thái occurrence | `REQUIRED` | `OPTIONAL` |
|---|---|---|
| không OUTCOME, không claim | `ACTION_INCOMPLETE` | bỏ qua (không có nghĩa vụ thực hiện) |
| đúng 1 OUTCOME `APPLIED` | hoàn tất; ACTUAL_OUTCOME đến hạn đầy đủ (4.3.1) | **ACTUAL_OUTCOME đến hạn đầy đủ như `REQUIRED`** (bytes, proof lịch sử/liên kết, review coverage nếu pha đòi) |
| OUTCOME `NOT_APPLIED` | `ACTION_INCOMPLETE` | bỏ qua; nếu bị khai đã thực hiện ⇒ `ACTION_CLAIM_WITHOUT_OUTCOME` |
| OUTCOME `PARTIAL`/`UNKNOWN` | `RETRY_UNRECONCILED` ⇒ BLOCKED | `RETRY_UNRECONCILED` ⇒ BLOCKED (**không** bỏ qua vì `OPTIONAL`) |
| ≥2 OUTCOME `APPLIED` cùng occurrence | `DUPLICATE_EFFECT_RECORD` ⇒ BLOCKED | như `REQUIRED` |
| OUTCOME hỗn hợp (APPLIED + UNKNOWN/PARTIAL) | unreconciled ⇒ BLOCKED (không dùng thứ tự/thời gian) | như `REQUIRED` |
| khai đã thực hiện mà không có OUTCOME | `ACTION_CLAIM_WITHOUT_OUTCOME` | như `REQUIRED` |
| OUTCOME mâu thuẫn `artifacts`/`result` | `BINDING_MISMATCH` | như `REQUIRED` |

Retry: số OUTCOME vượt `max_retries` là chỉ báo record (ENVELOPE), không proof thao tác thật.

**Review phủ action.** Mỗi effect REQUEST chỉ cần coverage cho **occurrence của chính nó** (khi pha đòi, 3.3.4): `actions_checked` của component hợp lệ chứa occurrence đó; thiếu ⇒ `REVIEW_COVERAGE_INCOMPLETE` cho effect đó. Đây là yêu cầu theo occurrence, **không** phải suy rằng các occurrence độc lập nhau: không suy dataflow giữa occurrence (D3). Veto và thiếu review mức task: 3.4.

**Output.** PRE_INTEGRATION/PRE_DELIVERY đòi `∪ FILE_BYTES FULL` phủ **từng** artifact ở `binding.outputs` ∧ `result.artifacts`; thiếu một ⇒ chặn; thừa ngoài outputs không bù thiếu. Qualifier hiện diện/vắng theo COVER (trái=review, phải=artifact).

### 4.5 Thay đổi sau review

| Thay đổi | Phần lệch | S3 báo | Quan sát sâu |
|---|---|---|---|
| input khai báo đổi | `inputs` | review không áp dụng; `STALE_REVIEW` ghi chú | bytes thật đổi mà record không đổi: INPUT_REVISION **O** (S4) |
| `task_revision` tăng | `task_revision`, `accepted_task_digest` | mọi review cũ không áp dụng; non-PASS cũ chỉ `related_nonpass` | — |
| `context_refs` khai báo đổi | `context_digest` | `BINDING_MISMATCH(parts=[context])` | không suy prompt thực |
| policy đổi | `policy_digest` | không áp dụng | — |
| overlay thêm/đổi/bỏ | `overlay_digest` | không áp dụng | — |
| output sau review đổi | `outputs` | review PRE_INTEGRATION/DELIVERY cũ không áp dụng | bytes thật: S4 |
| grant/actor/reviewer đổi | không đổi digest | **kiểm lại độc lập mỗi pha** | — |

### 4.6 Task-bound context khác với căn cứ Reviewer có context riêng

- **Task-bound context** (`context_digest` ↔ `context_refs` khai báo): mismatch ⇒ `BINDING_MISMATCH(parts=[context])`; chỉ nói về khai báo.
- **Căn cứ Reviewer có context riêng** (3.3.2.e): thiếu ⇒ `REVIEWER_NOT_ELIGIBLE`; chỉ là lời khai có attribution.
Khác bản chất, khác mã, không thay nhau.

### 4.7 Kiểu record/trường mới (phác thảo; không phải schema)

**4.7.1 `protection_overlay`**
```text
record_type: "protection_overlay"      header như các record (schema_version=/3, evaluation_basis)
overlay_id, overlay_revision (int ≥1)
source_ref: attributed_ref kind "user_condition"
            attribution: source_class (USER_CONFIRMATION | MAIN_PROPOSAL cho protect_more), channel (riêng, xem 2.7), evidence_locator
protect_more[]: { path_prefix, write_zone ∈ {original_source, shared_register, framework}, note? }   # tập
classify[]:     { path_prefix, write_zone ∈ {working, output_new} }                                  # tập; điều kiện 2.7
```
`overlay_digest` = digest của **tập** projection `{bind, part:"overlay", overlay_id, overlay_revision, protect_more:set, classify:set}`; loại `source_ref`, `note` khỏi băm; nguồn xác nhận kiểm lớp nguồn riêng mỗi pha.

**4.7.2 Review (thêm)**
```text
scope.subject:           "TASK_WIDE" | "PARTIAL"            (vắng = TASK_WIDE khi xét veto)
scope.items[]:           { kind:"FILE_BYTES", path, digest, source_id?, revision?, coverage:"FULL"|"PARTIAL", part_description? }
                       | { kind:"TASK_PROJECTION", part, task_id, task_revision, digest, action_index? }
scope.actions_checked[]: { index, digest }                  (occurrence, task id/revision lấy từ binding)
scope.intent_refs_checked[], scope.unconfirmed_checked[]    ([K] intent_refs_checked; thêm chỉ số unconfirmed)
intent_mapping[]:        { req_id, intent_ref_ids[], mapping:"FAITHFUL"|"PARTIAL"|"NOT_FAITHFUL"|"UNKNOWN", note? }
requirement_conclusions[]: { req_id, conclusion:"MET"|"NOT_MET"|"NOT_CHECKED"|"UNKNOWN", basis_note?, evidence_locator?, limits[] }
source_scope_conclusions[]: { source: FILE_BYTES|ref nguồn thư viện, examined:"FULL"|"PARTIAL"|"NOT_READ", conclusion_ids[], status:"SUPPORTED"|"NOT_SUPPORTED"|"NOT_CHECKED", limits[] }
```
`requirements_checked`, `not_checked`, `findings` giữ. Không thêm `verified`/`truth` vào tên trường.

**4.7.3 Task / effect / result (thêm)**
```text
task.effects.actions[].completion:   "REQUIRED" | "OPTIONAL"        (vắng = REQUIRED; trong projection)
task.effects.extra_review_phases[]:  review_phase                   (chỉ siết; trong projection)
effect.action_index:                 int                            (occurrence; effect.action phải = projection actions[index])
binding.outputs[] / effect.outcome.artifacts[] / result.artifacts[]:  + role:"STAGED_BYTES"|"ACTUAL_BYTES"; STAGED có relation:"COPY_IDENTICAL"|"TRANSFORM_BY_OWNER_TOOL"
result.actions_performed[]:          { action_index, action_digest, effect_id }
result.user_acceptance:              {
    ref: attributed_ref kind "user_acceptance" — attribution.source_class = USER_CONFIRMATION, channel ∈ {USER_MESSAGE, HOST_CONFIRMATION_UI}, evidence_locator (ngoài vùng ghi được, 2.6),
    task_id, task_revision, accepted_task_digest,            (phải = task hiện hành, tính lại)
    accepted_requirements[]: req_id (tập),                    (phải ⊇ mọi requirement mandatory hiện hành; do công cụ lập từ tóm tắt đã trình, user không viết)
    result_id, accepted_artifacts[]: FILE_BYTES(ACTUAL_BYTES),   (phải = result.artifacts, EXACT)
    presented_summary: { locator, digest }                    (tóm tắt bằng lời thường mà agent/công cụ đã trình để user xác nhận)
  }
```
`acceptance_states` giữ nghĩa [K]. `USER_ACCEPTED` / `USER_ACCEPTED_DECLARED` đòi `user_acceptance` đạt **đủ** các ràng buộc ở sơ đồ trên; là DECLARED, không thay review bắt buộc, veto, bytes/operation proof hay preservation.
**Quy tắc D4.** (1) Đối chiếu `task_id`/`task_revision`/`accepted_task_digest` với task hiện hành (tính lại): lệch ⇒ `USER_ACCEPTANCE_STALE`. (2) `accepted_requirements` so với tập `mandatory` hiện hành: thiếu ⇒ phần chưa phủ `NOT_CHECKED` ⇒ BLOCKED (`USER_ACCEPTANCE_INCOMPLETE`); requirement thêm/đổi sau xác nhận (task_revision/digest đổi) ⇒ stale. (3) `result_id`/`accepted_artifacts` = result/artifact hiện hành, đúng bản; artifact cũ ⇒ stale. (4) **Không đủ:** grant làm việc, lời “đã nhận file”, im lặng, xác nhận task/artifact cũ, xác nhận chỉ nêu file không nêu requirement. (5) Không tự điền kết luận đủ yêu cầu thay user: agent/công cụ trình tóm tắt bằng lời thường (yêu cầu, tên/bản file) để user xác nhận; **một xác nhận theo nhóm đủ nếu tóm tắt đã trình liệt kê đủ tập** — không bắt user viết JSON hay xác nhận từng dòng. Checker chỉ kiểm tính nhất quán các trường với task/result hiện hành, không kiểm user hiểu gì. (6) Chỉ dùng cho REQUIREMENTS khi **không** có pha review bắt buộc (policy ∪ extra); route đòi review thì không dùng được. Lời xác nhận chỉ phủ một phần ⇒ phần chưa phủ `NOT_CHECKED`/BLOCKED ở accept.

### 4.8 Output `law.cvf.check/3`

```text
check_version "law.cvf.check/3" · contract "v3" · selection · candidate_status · implementation_stage
evaluation_basis · phase · phase_scope · disposition ∈ {PASS, BLOCKED, DENY, UNSUPPORTED, NOT_APPLICABLE}
effect_authorized: false (luôn) · assurance_level: "UNVERIFIED"|"ADVISORY" · init_error · reasons[] · details[]
owners { schema_sha256, policy_sha256 }
route { rows[], status: RESOLVED|CONDITIONAL|UNRESOLVED,
        assumptions[]: {id, closed_by:"S4_OBSERVER", due_phase, state: OPEN|CLOSED_BY_OBSERVATION} }
zones[]   { locator, write_zone_declared, write_zone_derived, write_zone_effective|"UNCLASSIFIED", basis:"POLICY_LEXICAL", fs_observation:"NOT_OBSERVED", promoted_by[] }
actions[] { occurrence:{index,digest}, completion, route_rows, disposition, independent_continue, reasons[] }
gates[]   { gate, due_in[], status, evidence:{required:[D|C|R|O], provided:[...]}, limits[], reasons[], owner_of_proof }
reviews[] { position, phase, anchor, binding_relation:{state, differs_in[]}, reviewer_basis, subject, coverage_contribution, verdict, role_in_decision }
aggregate { records_checked_state, due_gates, met, review_covered, user_accepted_declared, not_required, not_yet_due,
            not_checked, unsupported, not_met, open_assumptions[], conclusion_scope:"RECORD_CONSISTENCY_IN_MEMORY" }
coverage  { record_structure_checked, binding_evaluated, routing_evaluated, gates_evaluated,
            artifact_bytes_observed:false, actual_operation_observed:false,
            requirements_semantic_verified:false, review_semantic_basis:"COOPERATIVE_REVIEW_DECLARED",
            target_existence_observed:false, owner_protection:"NOT_PROVEN" }
```
`gates[PATH_SCOPE]` báo riêng ba tiểu mục: `lexical`, `observed_at_time`, `precondition_history` (D1). `actions[].independent_continue=true` chỉ khi không có veto/thiếu review mức task và các gate riêng của action đạt; không suy từ target rời nhau (D3).
Quy tắc tên: không `verified`, `safe`, `allowed`, `authorized` (ngoài `effect_authorized=false`), `semantic_truth`. `PASS` chỉ nghĩa: route `RESOLVED`, mọi gate đến hạn thỏa ở mức căn cứ đã nêu, record nhất quán trong bộ nhớ, trong `phase_scope`. `open_assumptions` còn ⇒ không PASS (3.1).
Mã lý do do checker sở hữu (ngoài enum schema): `PATH_ZONE_UNDETERMINED`, `PATH_UNSUPPORTED_FORM`, `ROUTE_ASSUMPTION_OPEN`, `OBSERVATION_UNAVAILABLE`, `OPERATION_MISMATCH`, `REVIEW_COVERAGE_INCOMPLETE`, `REVIEW_INCONSISTENT`, `REVIEW_NOT_APPLICABLE`, `ACTION_INCOMPLETE`, `ACTION_UNREPORTED`, `ACTION_CLAIM_WITHOUT_OUTCOME`, `ARTIFACT_UNATTRIBUTED`, `PRECONDITION_PROOF_MISSING`, `USER_ACCEPTANCE_INCOMPLETE`, `USER_ACCEPTANCE_STALE`, `DUPLICATE_EFFECT_RECORD`, `BINDING_FIELD_NOT_APPLICABLE`, `SCOPE_KIND_MISMATCH`, `PROJECTION_DIGEST_AS_FILE` (note), `OVERLAY_LOWERS_BASELINE`, `OVERLAY_PREFIX_RESERVED`, `OVERLAY_AMBIGUOUS`, `OVERLAY_ENTRY_IGNORED`, cùng mã S1, mã `reason_code` hiện có và mã của thiết kế C2 bước 1 được nhận (`ACCEPTANCE_CLAIM_NOT_SUPPORTED`, `ENVELOPE_UNMEASURED`, `RETRY_UNRECONCILED`, `OUT_OF_CHECKER_SCOPE`).

### 4.9 UNSUPPORTED (contract 4.5 → v3)

Giữ: alias path, đối tượng không phải file, ngữ cảnh thực của role, digest của review/effect/result, so với digest v1, thời gian/hết hạn, authenticity attribution, bằng nhau ngữ nghĩa giữa định dạng.
Thêm: equivalence digest `bind/2` ↔ `bind/3`; đồng nhất digest bytes file task với projection task; suy tồn tại file từ chuỗi path; recipe format; vai không-core; `relation=TRANSFORM_BY_OWNER_TOOL` khi chưa có owner proof; đếm số lần thao tác thật từ số record; suy precondition lịch sử (“từng chưa tồn tại”) từ lstat/bytes hiện tại; suy độc lập giữa action từ target/payload khác nhau.

---

## 5. Kế hoạch triển khai

### 5.1 Lát cắt (mỗi lát tự soát diff; không gom nhiều owner vào một lượt Worker)

| Lát | Nội dung | File / owner | Phụ thuộc | Proof | Review |
|---|---|---|---|---|---|
| **A0** (tranche amendment, chưa code S3) | cây owner **v3 candidate riêng**: contract, schema, policy, rules đọc, ví dụ v3 + `EXPECTED` mới, vectors v3 (projection `overlay`/`scope_item`, bind/3) | `.cvf/contracts/v3/**`, `.cvf/rules/v3/**`; `tests/test_control_v3_candidate.py` | Main nhận packet + chốt 7.2 (R-1…R-3, R-7, R-8 còn mở; R-4…R-6 đã có disposition) | schema/vectors/ví dụ tự nhất quán; pin v1+v2 không đổi | **bắt buộc** độc lập (AGENTS, “Bảo trì bộ khung LAW”) |
| **S3-B0 — STRUCTURE_DECIDED,18/10** | copy-forward foundation v3 có giới hạn, không engine v1/kernel config/monkeypatch; entry/loader/canon/refs/binding thuần | brief HANDOFF; Orchestrator/S3-G và G-04 sở hữu nợ trùng mã, loại v2 candidate runtime khỏi package v3 trước release và kiểm package thực; chưa xóa v2 ở B | A0 đã nhận candidate | inventory/imports v2 và phạm vi output/helper | Main chọn, Reviewer nhận; không cần tranche thiết kế mới |
| **S3-B — REVIEW_ACCEPTED_FOUNDATION_ONLY,18/10** | copy-forward có giới hạn theo B0: entry/loader/canon/refs/binding; structure-valid vẫn BLOCKED, helper chưa nối entry | `.cvf/checks/control_check_v3.py`, `.cvf/checks/v3/**`, tests/test_control_check_v3.py | A0/B0 nhận | Reviewer46/Main21target đạt0skip; pins và -I; nợ canonical/copy-forward giữ | Reviewer Sol6.1 High nhận foundation, không workflow |
| **C/D hẹp — REVIEW_ACCEPTED_BINDING_ROUTING_ONLY,18/10** | một routing.py + refs/binding/route entry; sửa unknown T/U union, strict path, knownloss priority; chưa gate/observer/PASS | routing.py/entry/README/tests/contract11; hash ở review HANDOFF | S3-B nhận | canonical regressions khác oracle phản thực tế; Main22 target sau sửa đạt0skip, Reviewer routing38 và rerun8 đạt | Reviewer Sol6.1 High nhận diagnostic; không mở C/D/E rộng |
| **Screening projection-aware — REVIEW_ACCEPTED_BINDING_ROUTING_ONLY (18/10)** | đóng nợ quét canonical toàn bundle; metadata vẫn qua strict parse/schema/guard; task đơn/orphan duplicate đã sửa bằng helper sẵn có | canon/loader/entry/README/tests; hash/review trong HANDOFF | C/D nhận | Reviewer22/Main17 sau sửa đạt0skip; digest/vectors/schema/policy/writer nguyên | Workflow đã có code nhưng CHANGES_REQUIRED; corrective rid/T2 theo brief HIỆN HÀNH HANDOFF, chưa e2e/R-7/G |
| **S3-C** | `pathing`/`zones`: chuẩn hóa lexical, bảng vùng, hạng, mẫu authority, overlay (F5) | `pathing.py`, `zones.py` | S3-B; đối chiếu chuẩn hóa v1 | AC-03, 13–16, 18–20, 31 | độc lập |
| **S3-D** | `route`: điều kiện T/F/U, hợp hàng, giả định mở, **route CONDITIONAL ⇒ BLOCKED**, per-action | `route.py` | S3-C | ma trận route; AC-01/02/24 | độc lập |
| **S3-E** | `review`: QUAL, COVERAGE, phạm vi tối thiểu, veto V-1…V-6, extra_review_phases | `review.py` | S3-B, A0 | AC-05…10, 17, 22, 23, 25–30, 38–40 | độc lập |
| **S3-F** | `gates`, `delegation`, `engine`, occurrence/hoàn tất action, nối entry + `check/3` | các file đó | S3-C/D/E | toàn ma trận 6 (cột “chỉ S3”) | **bắt buộc** độc lập |
| **S3-G** | hồi quy + evidence + packet review | `roadmap/evidence/g02-c2-<ngày>/s3/**` | S3-F | v2 byte-identical, v1 parity | độc lập |
| S4 | observer **read-only**: root/ancestors/reparse/identity/size/race fail-closed; quan sát *tại thời điểm* `target_existence` (đóng A-NEW_TARGET ở d/e), bytes input/artifact hiện tại; **không** thay proof lịch sử | `observe.py` | thiết kế riêng được review | AC-01/02/12/27/36 nhánh “có S4” | độc lập, bắt buộc |
| **P-CN1-C — DESIGN_ACCEPTED_WITH_CONSTRAINTS, 18/10** | contract API/evidence owner **4.3.3**, sửa trực tiếp theo review bản 584fcba93ef7255e; không mới canonical spec | packet này | đủ mở I tools-only, chưa nhận implementation/runtime | review độc lập + Orchestrator sửa rõ một lượt, không thêm vòng thiết kế | Sol 6.1 High |
| **P-CN1-I + S4-min — REVIEW_ACCEPTED_TOOLS_ONLY_WITH_LIMITS,18/10** (M-4 bước2) | publish create-only, publish-v1, API/CLI, khóa EOF, status/recover/discard-staged/observe; corrective root/path/T7 đã nhận, thiếu pin từ chối; final hash f2b1b425690eacd5 | tools/publish_new.py, tests/test_publish_new.py; tools/README.md/evidence; transaction.py nguyên | P-CN1-C nhận; đủ chuyển A0 hẹp, chưa activation/cấp quyền | Worker proof + Reviewer focused checks; không full suite/Python3.8/3.13 corrective hoặc môi trường khác; checker/d-e-a chưa triển khai | Reviewer Sol6.1 High nhận tools-only, Orchestrator đồng bộ diagnostic hẹp |
| **A0 hẹp cho một action — CONTRACT_CANDIDATE_REVIEW_ACCEPTED,18/10** (M-4 bước3) | đúng phần bảng5.4; có output check/3 tối thiểu, historical pin accept, result.action_digest optional giữ v2 | `.cvf/contracts/v3/**`, `.cvf/rules/v3/**`, tests/test_control_v3_candidate.py | P-CN1-I nhận tools-only | Reviewer29target/Main12target đạt0skip; v1/v2/writer nguyên byte, workflow NOT_RUN | Reviewer Sol6.1 High nhận candidate, chưa evaluator/activation |
| Writer/protocol proof cho `overwrite`/input là target/sổ | proof bytes trước ghi gắn `E_req`; bảo toàn | owner writer (A-06) | tranche riêng | AC-28, 37 | độc lập, bắt buộc — vẫn chưa có thiết kế |
| S5 | tương thích + regression + CI | tests | S3-F, S4 | — | độc lập |
| Integration | nối công cụ/entry/native role; chọn **một** version hiệu lực; CI pin jsonschema, Python 3.8; quyết định `.cvf` vào gói; điều kiện trước ở 5.4 | CI, `tools/`, AGENTS, roles | S3–S5 nhận + 5.4 | — | độc lập |
| Activation | EXECUTION_PROFILE chọn contract tường minh; đổi `policy status`; AGENTS/templates/PROJECT | — | integration | — | độc lập + operator |

Ước lượng dòng không cam kết.

### 5.2 Gate bị chặn bởi phần ngoài D0

| Phần ngoài D0 | Gate/hàng bị chặn | Trạng thái trong S3 |
|---|---|---|
| recipe format (C2-Q4) | RECIPE_VERSION_ACCEPTED; R-RECIPE; đường nhẹ cho ghi STATE/sổ | `UNSUPPORTED`/`NOT_MET` |
| vai không-core (Q5) | DELEGATE_SCOPE `registered`/`domain_accepted` | `UNSUPPORTED` |
| thời gian/hết hạn (Q1) | GRANT_*, ENVELOPE khi có `expires_at` | `UNSUPPORTED` |
| ex19 | DELEGATE_SCOPE/dispatch task chỉ-context | `UNSUPPORTED`, không action giả |
| writer x14 / race / atomic | PRESERVATION ghi đè workbook/sổ/provenance; `TRANSFORM_BY_OWNER_TOOL` | `UNSUPPORTED` |
| observer (S4) | PATH_SCOPE ghi ở d/e (A-NEW_TARGET), INPUT_REVISION, bytes ACTUAL_OUTCOME | route CONDITIONAL/`NOT_CHECKED` ⇒ BLOCKED |
| writer/protocol proof lịch sử (D1) | PATH_SCOPE ghi ở accept, INPUT_REVISION cho input là target, ACTUAL_OUTCOME | `UNSUPPORTED(PRECONDITION_PROOF_MISSING)` ⇒ BLOCKED. `create_new` một file: owner đề xuất P-CN1 (4.3.2), giữ trạng thái này tới khi thi công + review; `overwrite`/input là target: chưa có thiết kế |
| nghiệm thu D4 đủ (M-3, R-3) | REQUIREMENTS ở accept của luồng không review | `NOT_CHECKED` ⇒ BLOCKED cho tới khi D4 đủ trường gắn snapshot (4.3.2); không nhận tập con |
| amendment routing P-CN1 (M-2) | ghi runtime T2–T4, T6, T7 gắn vào action | chưa nhận ⇒ R-MUTATION ⇒ thiếu review ⇒ BLOCKED |
| mô hình dependency giữa action (D3) | giảm veto PARTIAL, độc lập trong cùng task | không giảm: TASK_WIDE |
| host enforcement | mọi claim “enforced” | không có; ADVISORY |
| skill intake | SKILL_INTAKE_STANDARD | `NOT_CHECKED` |

### 5.3 Consumer và pin sẽ phải đổi ở tranche tương lai (D0 **không** sửa)

| Consumer / pin | Ghi chú |
|---|---|
| `tests/test_control_v2_candidate.py` (`V1_PINS` sáu file v1) | giữ nguyên |
| `tests/test_control_check_v2.py`, `tests/test_control_check_v2_s2.py` (`V1_PINS`, `OWNER_PINS`, `TEST_PINS`, cây package v2 qua `os.listdir(PKG)`) | không đổi nếu v3 là cây riêng; **phải đổi** nếu S3-B0 chọn dùng chung module v2 |
| `tests/test_control_check.py` (v1) | không đổi |
| `tests/test_control_v3_candidate.py`, `tests/test_control_check_v3*.py` (mới) | pin sáu v1 + owner v2 (schema `4c6dd3da…`, policy `20cff567…`, contract `d3ad993f…`, rules `53738f25…`, checks README `a03c56f2…`) |
| `.cvf/README.md`, `.cvf/checks/README.md`, `.cvf/PROVENANCE.md` | thêm mục v3, trạng thái |
| `AGENTS.md`/`en/AGENTS.md` (dẫn `.cvf/rules/CONTROL_RULES.md`, `ROUTING_POLICY.json`), `roles/README.md`, `roles/*/config.json` | chỉ đổi ở Activation |
| `.github/workflows/ci.yml` | tự nhặt test mới; cần jsonschema ≥4.18 pin và Python 3.8 ở Integration |
| `MANIFEST.sha256`, `tools/check_package.py`, `tools/build_release.py`, `upgrade_package.py` | `.cvf`, `roles/` hiện không có trong MANIFEST; phân phối thuộc G-04/Integration |
| `roadmap/ROADMAP_HOAN_THIEN.md`, `.agent/STATE|HANDOFF`, `roadmap/evidence/**` | cập nhật theo tranche |
| hàm tham chiếu và `vectors.json` v3 | mới; không sửa vectors v2 |

### 5.4 Điều kiện trước tích hợp [M Q-3, Q-4, Q-1]

1. **Protocol/recipe ghi STATE/runtime** có owner và đã nhận trước khi tích hợp luồng đó; không phát hành mặc định gọi Reviewer cho mỗi lần ghi STATE; D0 không tự nhận recipe. *Delta D0:* runtime của P-CN1 có owner, envelope T1–T7 và mapping routing versioned đề xuất (4.3.2, scope M-2) — chỉ phần đó, chưa hiệu lực; `STATE.md`/HANDOFF ngoài envelope vẫn chưa có protocol và vẫn chặn tích hợp luồng ghi STATE.
2. **Sửa nháp lặp** trong phạm vi được giao: D0 chưa mở đường nhẹ sửa đè; trước tích hợp phải có thiết kế/owner. “Luôn tạo file mới” (AGENTS quy tắc 3) **không** được coi là UX cuối đã nhận. Chưa thay quy tắc bảo vệ bản gốc. *Delta D0:* P-CN1 tạo bản mới; supersedes chỉ là lineage metadata chưa bound trong C1, không chứng minh bản hiệu lực hoặc đóng điều kiện này. Nhánh giữ AMBIGUOUS, không chọn theo thời gian. UX sửa nháp lặp/owner vẫn mở trước tích hợp; sửa đè nhẹ chưa được nhận.
3. **Một version hiệu lực** chọn tường minh; v2 và v3 không cùng có hiệu lực; nợ trùng mã có owner và đường xóa trước release. *Delta D0:* `publish-v1` là schema evidence của owner `tools/`; mapping routing P-CN1 chỉ nằm trong version routing được chọn ở A0, không thêm nguồn policy thứ hai hay bảng miễn route trong `tools/`.
4. **Đường nháp ghi mới phụ thuộc proof [M R-6]:** quan sát S4 cho d/e **và** proof lịch sử/precondition/liên kết thao tác cho accept (4.3.1); trước đó chỉ luồng đọc PASS. Không hứa S4 read-only là đủ; không hạ acceptance để mở nháp trước proof. *Delta D0:* proof đề xuất là P-CN1 `published` + S4-min trên Windows NTFS local; điều kiện giữ nguyên tới khi contract, implementation và integration được nhận đúng bước.

#### 5.4.A Quyết định tích hợp I-01 — Orchestrator,18/10/2026

**DESIGN_ACCEPTED_WITH_CONDITIONS, IMPLEMENTATION_PENDING.** Reviewer độc lập Sol6.1 High đã phản biện hướng và các điều kiện bên dưới. Đây là amendment phạm vi có version trước hiệu lực, không ghi đạt 5.4.1/5.4.2/5.4.3 từ việc chốt thiết kế. Các gate cũ vẫn giữ tới khi owner/implementation tương ứng được review nhận; không activation trong lượt quyết định này.

**I-02 rev1 — amendment thứ tự phát triển, 18/10/2026; DESIGN_ACCEPTED_WITH_CONSTRAINTS bởi Reviewer Sol6.1 High.** G-03 baseline hợp tác hẹp và G-04 tích hợp candidate đã nhận WITH_LIMITS, gồm M-3/D4 dương đúng bản. Từ mốc này được tiếp công việc kho nguồn A–D theo dependency và acceptance từng tranche; G-04/official-release vẫn PENDING theo RELEASING và D-02. Không activation, không công bố official support; giữ Gitclean/CI/quy trình RC, blocker A-06, dependency A-07→A-06 và x14 PARKED. Không đổi schema/policy/routing/D4/UNSUPPORTED, không nâng verdict BLOCKED lịch sử; không đóng A-02/R2 hoặc thêm quyền Git/release. Mốc tiếp nối đã cập nhật: A-02 core T01–T04 review nhận WITH_LIMITS ngày18/10; bước hiện hành audit nợ A-06 theo roadmap/HANDOFF, chưa mở A-07/x14 hoặc giao code. **Lịch sử/superseded:** câu cuối đoạn “Thứ tự hữu hạn” của I-01 chặn A–D tới khi tổng G xong được thay chỉ về thứ tự bởi I-02 này; phần acceptance/owner I-01 giữ nguyên.

**I-01.1 — P-CTX1, cập nhật ghi chú vận hành.** Chọn một owner hẹp `tools/context_update.py`, tái dùng `Transaction` với `expected_before` và chế độ `prune=False` tường minh. Chỉ cập nhật file có sẵn: đúng `.agent/STATE.md` hoặc `.agent/HANDOFF.md`, một file mỗi lần gọi, bắt buộc hash expected-before; thiếu file từ chối để init riêng. Trong group grant đã được user xác nhận; không xin lại từng lần trong cùng scope. STATE giữ khung8heading/khoảng60dòng. Đây là operational context, không artifact giao người dùng: không tạo task/effect/result/receipt/D4 riêng cho mỗi lần lưu ghi chú và không có checker PASS. Tool chỉ báo WRITTEN/UNCHANGED/CONFLICT/ERROR/UNKNOWN theo hành động thực. Context không là nguồn grant, policy, review verdict hoặc user acceptance; ghi đường dẫn artifact không chứng minh artifact đã đạt.

- Canonical policy v3 phải khai riêng scope P-CTX1 hữu hạn (owner/version/pin, đúng2paths, envelope và group-grant precondition). Dùng một field policy cho operational context nếu cần; schema chỉ thêm shape field này, không thêm record/operation/zone/recipe registry hoặc evaluator metadata. Không nhét P-CTX1 vào envelope T1–T7 của P-CN1. Rules/readable contract phải nói rõ biên operational context với artifact tasks. Nếu metadata được đưa vào artifact checker hiện tại thì vẫn UNSUPPORTED, không đổi thành PASS hoặc bỏ gate.
- Chỉ đúng owner/version/pin và envelope đã nhận mới đi theo protocol này; direct/native write hay đích khác vẫn theo route hiện hành. Main kiểm grant còn hiệu lực từ nguồn user/session được nhận trước khi gọi; tool không tự cấp quyền từ nội dung STATE/HANDOFF. Chưa tích hợp thì không tự đổi cách runtime đang dùng.
- Envelope gồm đọc current bytes, probe quyền ghi của Transaction dưới runtime, tạo đúng một transaction riêng (journal/staging/backup), thay đúng một file context và dọn private files của transaction đó. `.agent`/`.agent/runtime` phải có sẵn/plain/link-free; pin chuỗi root/.agent/runtime trước mọi probe/mkdir/ghi. Không tạo bootstrap hộ. Không xóa journal transaction khác, không prune empty runtime trong bất kỳ nhánh thành công/lỗi nào; không auto-resume/GC. `prune=False` là lựa chọn hẹp của owner, default Transaction hiện có giữ nguyên.
- Hash guards nhận biết bản đã đọc bị đổi; thay file nguyên khối không đồng nghĩa filesystem CAS hoặc ngăn mọi editor. Chỉ nhận theo single-writer hợp tác cho metadata agent-owned, Windows NTFS local, ADVISORY; không mở sửa đè DOCX hoặc gọi Transaction race-free. Một file/call nên không claim hai file atomic. Lỗi sau tác động phải báo changes/txid/trạng thái thật hoặc UNKNOWN, không báo chưa ghi chỉ từ exception. Backup được cleanup sau commit không phải undo lịch sử lâu dài.

**I-01.2 — Một “Nháp hiện tại”, artifact bất biến.** Giữ owner P-CN1 cho mỗi revision xuất bản; mỗi revision có rid/task riêng, nhưng cùng một revision giữ snapshot xuyên các pha. Không dùng Transaction overwrite tài liệu người dùng đang mở. Người dùng làm việc theo một tên việc/work_id và một thẻ “Nháp hiện tại”, không tự đặt tên v2/v3 hoặc quản lý rid/digest. Lịch sử hiển thị tối đa5bản liên quan cùng work_id, có đường xem thêm/mở thư mục; giữ nguyên mọi artifact cũ, không tự GC. Chi phí dung lượng tăng được ghi là giới hạn, không gọi5bản hiển thị là retention5bản.

- Persist lựa chọn `{path,rid,digest}` ở đúng một comment có version trong mục Current artifact của STATE, ví dụ marker `law-current-draft/1`; user chỉ thấy nhãn/link dễ đọc. Không thêm heading hoặc file registry/pointer mới; UI/agent tạo metadata, user không gõ JSON. Parser chỉ nhận đúng một tuple hợp lệ trong section này; thiếu/trùng/hỏng không tự chọn theo mtime/supersedes.
- Tuple chỉ điều hướng, không chứng minh hiệu lực/nghiệm thu. Trước mở, kiểm path/link/bytes và evidence P-CN1 cùng rid bằng owner/observer đã nhận; không dựng thêm evaluator đọc file. Nội dung/proof đổi thì báo chưa đối chiếu/đã thay đổi, không tự đổi hash hoặc chọn bản khác để làm xanh. Việc user chủ động mở file trong scope đọc vẫn tách khỏi acceptance; tuyệt đối không gắn nhãn “đã nhận” hoặc “đúng bản ghi nhận” khi mismatch. Path không an toàn/outside scope thì từ chối mở.
- `supersedes` chỉ là lời khai lineage, không bằng chứng chọn current hoặc tuyến tính. Năm bản liên quan không được quảng cáo là chain đã xác minh. User chọn một bản qua UI hoặc agent ghi lựa chọn theo yêu cầu; không thêm xác nhận kỹ thuật mỗi lần mở. D4 vẫn riêng, đủ trường và đúng bytes khi nghiệm thu thật.
- Publish thành công nhưng cập nhật context thất bại: giữ file/receipt, báo đã tạo nhưng chưa cập nhật lựa chọn; không xóa artifact hoặc gọi chưa publish, không tự publish lại. Source/user edit làm đổi bytes vẫn không được tái sử dụng receipt/D4 cũ như bằng chứng cho bản mới.

*Delta I2 (18/10/2026, IMPLEMENTED_PENDING_REVIEW, chưa đóng 5.4.2):* `tools/current_draft.py` + route `/api/draft/*` + thẻ Nháp hiện tại thực hiện các ràng buộc trên bằng owner đã nhận (P-CN1 qua observer đúng pin, P-CTX1 qua adapter so pin policy). Phụ thuộc mới cần chốt ở I3/G-04: so pin dùng `load_owners` của checker v3 nên cần `jsonschema` >= 4.18; thiếu ⇒ thẻ UNAVAILABLE (không mở, không chọn). Chi tiết, hash và phần chưa kiểm ở HANDOFF.

**I-01.3 — Một runtime v3 cho project mới.** Chọn v3 làm đích tích hợp/phân phối, chưa active trong source hoặc project hiện tại. Giữ v1/v2 source/fixtures để đối chiếu, nhưng package mới không ship cả ba runtime hoặc mã foundation v2 trùng. Onboarding dùng init/transaction hiện có cho bootstrap; kiểm new/adopt/upgrade thật, không viết helper mới theo suy đoán. Không tự migrate records/policy/grant/receipt của project legacy; upgrade phải phát hiện khác version, trình preview và giữ nguyên khi chưa có đường chuyển được nhận. Source check_package đạt không thay release gate hoặc kiểm ZIP thực.

**I2 dispatch constraints (18/10, DESIGN_ACCEPTED_WITH_CONSTRAINTS qua Reviewer Sol6.1 High):** brief implementation hiện hành ở HANDOFF. Helper `tools/current_draft.py` chỉ điều phối owner đã nhận, không sửa owners/schema/policy. Parser strict toàn marker ứng viên và đúng section; apply bound cả STATE đã đọc lẫn tuple/proof/target snapshot đã preview, không derive pointer khác âm thầm. Open reobserve safety riêng: thiếu proof có thể mở theo yêu cầu khi safety còn đo được, thiếu owner/pin/safety thì từ chối; không fallback generic opener. `os.startfile` không bảo đảm ứng dụng mở read-only. P-CTX1 phải so pin với đúng bytes code được gọi; không claim dependency closure. History cap candidate kèm cảnh báo chưa đầy đủ, không claim hard bounded enumeration/I/O của owner. Dedicated authenticated selection/open tránh generic operations log nằm ngoài envelope; preview/status/open không ghi. I2 chỉ navigation/selection và prompt cho agent-native revision workflow, chưa editor/chat/publisher mới, chưa đạt5.4.2 từ thiết kế.

**Thứ tự hữu hạn:** I1 owner metadata + amendment scope được review → I2 thẻ current/history dùng owner đó + UX kiểm thực → I3 package một runtime và lifecycle → pilot/support matrix G-03/G-04. Mỗi tranche một brief trong HANDOFF, không mở lại S3 framework/recipe/review engine. 5.4.1/5.4.2/5.4.3 chỉ đóng sau bằng chứng tranche tương ứng. **Lịch sử:** tại mốc I-01 chưa chuyển A–D/x14; thứ tự hiện hành theo I-02 rev1 phía trên, x14 vẫn PARKED.

**I3 — DESIGN_ACCEPTED_WITH_CONSTRAINTS / READY_FOR_OPERATOR_DISPATCH (18/10, Reviewer Sol6.1 High).** Brief hiện hành ở HANDOFF: projection chung trong check_package.py cho actual selection/bytes/manifest của build/new/adopt; closure v3 tường minh (schema/policy, readable contract/rules, entry và tám module), không v1/v2/fixtures/maintainer/runtime. Dùng sáu templates sạch hiện có + một release_templates/.cvf/README.md mới; project references AGENTS VI/EN và roles bằng exact replacement hữu hạn/idempotent/failclosed, source v1/v2 vẫn giữ. Không sửa pinned machine bytes hoặc nới path/extra-file/release gates.

Guard trước mutation đọc cả source và target: nguồn giao phải nhất quán, target absent có thể thêm candidate không diễn giải legacy data; same-v3 chỉ nâng bình thường khi machine closure/owner dependencies/canonical bytes tương thích và không conflict `.cvf`. Version lạ/mixed/partial/changed policy/closure/conflict chặn cả --force, không `.new` rồi coi coherent, không exec target hoặc migration. MANIFEST dựa bytes projected ở stage/target, không thay source MANIFEST. Readiness dựa actual interpreter App, giữ failclosed và không cài host/global; chỉ controlled card chịu Windows/NTFS/jsonschema requirement. Runtime selection không activation. I3 chưa code/build/test,5.4.3/G-03/G-04 chưa đạt; RC tạm với gate thật không thay pilot/release acceptance.

*Delta I3 (18/10/2026, IMPLEMENTED_PENDING_REVIEW, chưa đóng 5.4.3):* `tools/check_package.py` là owner chung của bản giao (`delivery_selection/bytes/manifest`, `materialize`) cho build/new/adopt; closure `.cvf` v3 14 file; phép thay tham chiếu hữu hạn; guard `.cvf` trước mọi mutation (kể cả `--force`); readiness theo `sys.executable`; owner đã pin (`publish_new`, `context_update`) đóng gói nguyên byte. Cảnh báo cho amendment sau: pin hash bytes thô phụ thuộc EOL, mâu thuẫn `.gitattributes eol=lf` khi commit. Chi tiết, hash và phần chưa kiểm ở HANDOFF.

**Phân loại theo mốc (delta D0):**

| Mốc | Cần | Ghi chú |
|---|---|---|
| Dispatch implementation P-CN1-I | Main/Reviewer nhận 4.3.2 + contract 4.3.3 (P-CN1-C) | M-1…M-5 đã có disposition; chọn M chưa đủ |
| Mở A0 hẹp | P-CN1-I + S4-min thi công và review độc lập đạt | A0 dùng: vùng `working`/`output_new` + `light_write_zones` + `NO_PROTECTED_TARGET` (Δ01–Δ02, chỉ phần cần), mệnh đề R-READ_DRAFT (B)/(C) (Δ03), mệnh đề `create_new` ở `agent_runtime` ⇒ R-MUTATION (Δ04, cho nhánh fallback), `CONTENT_USE_INTERNAL_ONLY` (Δ06), `user_acceptance` đủ D4 (Δ11), `role:"ACTUAL_BYTES"` (Δ12, không `STAGED_BYTES`/`relation`), `effect.receipt_ref` kind `effect_receipt`, policy `owner_protocols` + mệnh đề routing P-CN1, mã `PRECONDITION_PROOF_MISSING`/`CHANGED_AFTER_PUBLISH`/`INPUT_CHANGED_SINCE_READ`, `check/3` phần gate của luồng. **Hoãn:** Δ04 cho vùng khác, Δ05, overlay (Δ07/Δ14), Δ08, review scope/kết luận (Δ09/Δ10), occurrence nhiều action/`completion`/`extra_review_phases`/`action_index` (Δ17; một action giữ `action_digest`), R-8 |
| Trước tích hợp luồng nháp | A0 hẹp + checker theo mapping được nhận; 5.4.1 cho STATE/HANDOFF; 5.4.2; 5.4.3 một version hiệu lực | grant vẫn do Main kiểm (P-02); không auto-resume |
| Vẫn BLOCKED/UNSUPPORTED | `overwrite`/sổ/provenance (x14/race A-06), INPUT_REVISION input là target, `TRANSFORM_BY_OWNER_TOOL`, external, recipe, vai không-core, ex19, task có pha review bắt buộc trong luồng P-CN1 (review scope hoãn), POSIX/mạng/cloud, giảm veto (R-8, TASK_WIDE), host enforcement | không đổi bởi P-CN1 |

---

## 6. Ma trận ca nghiệm thu dự kiến

“Chỉ S3” = chỉ có checker bộ nhớ. “Có proof” chỉ áp dụng khi owner nêu đã có proof; chưa có ⇒ kỳ vọng có điều kiện, **không PASS**. Mọi PASS: `effect_authorized=false`, `assurance ADVISORY`, `phase_scope` = pha. Kỳ vọng thiết kế, **chưa chạy**.

| AC | Ca | Đầu vào chính | Chỉ S3 | Có proof (điều kiện) | Căn cứ | Owner proof |
|---|---|---|---|---|---|---|
| 01 | Nháp mới có grant (F1, F7, D1) | `create_new` `working/w1/bao-cao-nhap.docx`, tool ∈ grant, grant ACTIVE `USER_CONFIRMATION` không hạn, không Reviewer, task tối thiểu do công cụ dựng; result chỉ `CANDIDATE` | **d: BLOCKED** `ROUTE_ASSUMPTION_OPEN` (A-NEW_TARGET); output vẫn báo `records_checked_state=CONSISTENT_IN_CHECKED_SCOPE`, gate GRANT/TOOL/ENVELOPE `MET`, PATH_SCOPE ghi chưa đóng, owner S4. **e: BLOCKED** cùng lý do. **a: BLOCKED** (CANDIDATE không tắt ACTUAL_OUTCOME/REQUIREMENTS; thiếu proof lịch sử) | S4 đóng A-NEW_TARGET ở d/e (observation-at-time, `limits=[EXCLUSIVE_WRITE_NOT_PROVEN, RACE_NOT_EXCLUDED]`) ⇒ d/e PASS khi gate khác đạt. **a: PASS chỉ khi** có proof lịch sử precondition + liên kết `E_req`↔`E_out` (writer/protocol) **và** bytes hiện tại khớp artifact (S4) **và** tính đủ action **và** `USER_ACCEPTED_DECLARED` đúng D4. Chỉ S4 read-only: không đủ | 2.5, 3.1, 3.5, 4.3.1 | S3-D/F; S4; writer |
| 02 | Path nhẹ nhưng file đã tồn tại | như 01, file có sẵn trước thao tác, khai `create_new` | giống 01 (S3 không phát hiện): BLOCKED vì giả định mở; `target_existence=UNKNOWN`; không bao giờ PASS | S4 quan sát **tại d/e**: tồn tại ⇒ `OPERATION_MISMATCH`, route lại `overwrite` ⇒ R-MUTATION ⇒ BLOCKED `MISSING_REQUIRED_REVIEW`; tên mới là đường đúng. (Khác AC-36: file tồn tại *sau* khi tạo thành công không phải mismatch) | 2.8, 4.3.1 | S4 + writer exclusive-create |
| 03 | Authority trong `working/` | (a) `create_new` `working/w1/ROUTING_POLICY.json`/`AGENTS.md`; (b) `grant_ref` `source_class=USER_CONFIRMATION`, `channel=USER_AUTHORED_FILE`, `evidence_locator` `working/w1/grant.json`; (c) khai `create_new` nhưng thực `grant_write` | (a) nâng `framework` ⇒ R-AUTHORITY_CHANGE ⇒ BLOCKED `REVIEW_MISSING`; (b) `USER_CONFIRMATION_MISSING`; (c) R-AUTHORITY_CHANGE. Không đường nhẹ | — | 2.3, 2.6 | S3-C/D |
| 04 | Thiếu grant | không grant / `grant_refs` rỗng / ref không resolve / INACTIVE / ngoài scope / actor khác | BLOCKED `GRANT_MISSING`/`GRANT_INACTIVE`/`GRANT_OUT_OF_SCOPE`; action độc lập có grant riêng `independent_continue` | — | 3.2 | S3-F |
| 05 | Task-bound context thiếu/mismatch | review/effect `context_digest` ≠ tính lại từ `context_refs`; hoặc `context_refs` đổi sau review | review `NOT_APPLICABLE(differs_in:[context])`; `REVIEW_MISSING` ⇒ BLOCKED; `BINDING_MISMATCH(parts=[context])`. Task chỉ-context ⇒ `UNSUPPORTED` | — | 4.5, 4.6 | S3-E |
| 06 | Thiếu căn cứ Reviewer context riêng | (i) `eligibility_ref` `ROLE_REPORT`; (ii) `independence_observed` SELF_DECLARED/NOT_OBSERVED/SAME_ACTOR; (iii) `actor_id` = worker; (iv) TOOL_OBSERVATION nhưng `observed_by` không tool/host | BLOCKED `REVIEWER_NOT_ELIGIBLE`; review `NOT_ELIGIBLE` không tạo PASS (non-PASS của nó vẫn veto, V-2); không Main tự duyệt; `context_digest` khớp không cứu | — | 3.3.2.e | S3-E |
| 07 | Non-PASS cùng binding | R1 `CHANGES_REQUIRED` + R2 PASS cùng pha/anchor/full binding, `TASK_WIDE`; hoặc PASS có kết luận `NOT_MET` | **DENY** `REVIEW_BLOCKING_VERDICT`/`REVIEW_INCONSISTENT`; PASS sau không gỡ; user không gỡ | — | 3.4 V-1…V-5 | S3-E |
| 08 | Review cũ | review khác ở `task_revision`/`inputs`/`outputs`/`overlay_digest`/`context`/`policy` | `NOT_APPLICABLE(differs_in)`; `REVIEW_MISSING` ⇒ BLOCKED (+`STALE_REVIEW`); non-PASS cũ chỉ `related_nonpass`; không thời gian | — | 3.4 V-1, 4.5 | S3-E |
| 09 | Task projection ≠ raw file | review PRE_EFFECT có `FILE_BYTES` path `task.json`, digest = `accepted_task_digest` (hình ex02) | note `PROJECTION_DIGEST_AS_FILE`; không thỏa phủ accepted task ⇒ `REVIEW_COVERAGE_INCOMPLETE`. `TASK_PROJECTION(accepted_task)` đúng ⇒ phủ (R). Không kết luận digest bytes file task đúng/sai | S4 chỉ bytes file | 4.1, 3.3.3 | S3-E |
| 10 | Nhiều action/output thiếu coverage | task 3 action, 2 output; review `actions_checked` phủ 2 occurrence, `items` phủ 1 output | effect của occurrence thứ 3: `REVIEW_COVERAGE_INCOMPLETE`; effect của occurrence 1–2 chỉ cần coverage của chính chúng (không suy độc lập, D3); accept: thiếu output ⇒ BLOCKED. Hai review PASS qualified, phủ bù nhau ⇒ hợp đủ | — | 3.3.2, 4.4 | S3-E/F |
| 11 | x14 known loss | overwrite `.xlsx` với `KNOWN_LOSS`; hoặc `NONE_KNOWN` bằng writer chưa bảo toàn x14 | khai KNOWN_LOSS ⇒ **DENY** trước giao dịch; `NONE_KNOWN` ⇒ BLOCKED `PRESERVATION_UNKNOWN`; không nhận “hỗ trợ x14” | sửa writer A-06 ngoài D0 | 3.2 | writer A-06 |
| 12 | Bytes/operation chưa quan sát | result `EFFECT_APPLIED`, artifact digest khai, `evidence.kind=TOOL_OBSERVED`; hoặc `external_send` | a: BLOCKED `NOT_CHECKED(OBSERVATION_UNAVAILABLE)`/`ACCEPTANCE_CLAIM_NOT_SUPPORTED`; external ⇒ `UNSUPPORTED`; coverage bytes/operation `false` | S4 (bytes hiện tại) + writer (proof lịch sử/liên kết); chỉ `create_new` file thường | 3.2, 4.3.1 | S4 + writer |
| 13 | Đọc nguồn bảo vệ | `read` `references/…`, grant đọc | R-READ_DRAFT, route `RESOLVED`; **PASS** d/e (vùng không chặn đọc) với `limits=[ALIAS_NOT_EXCLUDED, EXISTENCE_NOT_OBSERVED, SOURCE_READ_NOT_OBSERVED]` | — | 2.1.2, Q-7 | S3-C |
| 14 | `.agent` state không tự là AUTHORITY | ghi đè `STATE.md`; `create_new` `.agent/runtime/x`; ghi `SKILL_INDEX.md` | STATE/runtime ⇒ R-MUTATION (không AUTHORITY); `SKILL_INDEX.md`/file lạ trong `.agent/` ⇒ `framework`; thiếu review ⇒ BLOCKED; không recipe | protocol STATE (5.4) | 2.4 | S3-C/D |
| 15 | Config/quy tắc | ghi `.cvf/rules/…`, `roles/…`, `PROJECT.md`, `EXECUTION_PROFILE.json`, `MANIFEST.sha256` | R-AUTHORITY_CHANGE | — | 2.3 | S3-C/D |
| 16 | Chạy tool ≠ sửa tool | grant tools `[library.py]` paths `[references/]`; overwrite `tools/library.py` | `GRANT_OUT_OF_SCOPE` và R-AUTHORITY_CHANGE; grant liệt kê `tools/` không hạ vùng | — | 2.1.3 | S3-C/F |
| 17 | User không thay review | result `[ACCEPTED_FOR_INTEGRATION, USER_ACCEPTED]`, `user_acceptance` đúng artifact, route R-MUTATION thiếu PRE_INTEGRATION | BLOCKED `REVIEW_MISSING`; `USER_ACCEPTED_DECLARED` **không** dùng được vì route đòi review | — | 3.2 REQUIREMENTS, 3.4 | S3-E |
| 18 | Dạng path không hỗ trợ | `..`, `C:`, UNC, ADS, `PROGRA~1`, đoạn kết thúc `.`/khoảng trắng, ngoài gốc | `PATH_UNSUPPORTED_FORM` ⇒ `UNSUPPORTED` phần phụ thuộc | quan sát: S4 | 2.2 | S3-C |
| 19 | Overlay cơ bản | (a) thêm `Ho-so-2023/` `protect_more` `original_source`; (b) `classify` `references/x/` thành `working`; (c) overlay đổi sau review | (a) `create_new` ở đó ⇒ R-MUTATION; (b) entry bị bỏ qua `OVERLAY_ENTRY_IGNORED(OVERLAY_PREFIX_RESERVED)`, vẫn nặng; (c) review cũ `NOT_APPLICABLE` (`overlay_digest`) | nguồn bền (Q-6) | 2.7 | S3-C/E |
| 20 | Output: content_use | `create_new` `output/b.docx`: (a) vắng, (b) `internal_draft`, (c) `sign` | (a) UNCLASSIFIED ⇒ BLOCKED; (b) R-READ_DRAFT nhưng CONDITIONAL ⇒ BLOCKED như 01; (c) không nhẹ + R-HIGH_STAKES (`PRE_DELIVERY`) | S4 cho (b) | Δ03, 2.5 | S3-D |
| 21 | Chéo version | bundle `/2` vào `--contract v3`; `/3` vào v2; trộn | `UNSUPPORTED` (`SCHEMA_VERSION_UNKNOWN`/`VERSION_MIXED`), gợi ý chọn contract tường minh; v2 byte-identical | — | 1.1 | S3-B |
| 22 | Hợp nhiều review (F2) | RA PASS khai `requirements_checked=[REQ-1]` `MET`; RB PASS khai `[REQ-2]` `MET`; cùng pha/anchor/full binding; RC PASS khác binding; RE PASS khai `[REQ-3]` nhưng conclusion `UNKNOWN` | RA∪RB phủ REQ-1,2 ⇒ `REVIEW_COVERED` khi mọi phần min-scope khác cũng phủ; RC `NOT_APPLICABLE`; RE `INCONSISTENT` ⇒ veto ⇒ DENY. Review chỉ `NOT_CHECKED` REQ-2 không đóng góp, không mâu thuẫn | — | 3.3.2 | S3-E |
| 23 | SOURCE_SCOPE | R-HIGH_STAKES: PRE_DELIVERY (a) thiếu `source_scope_conclusions`, (b) có, `examined=PARTIAL` cho nguồn dựa vào | (a) `NOT_MET`; (b) chưa phủ ⇒ `REVIEW_COVERAGE_INCOMPLETE`; đủ ⇒ `REVIEW_COVERED` kèm `limits`; không `verified` | — | 3.2, 3.3.3 | S3-E |
| 24 | Giả định mở không được hạ khi đổi pha | draft AC-01 chuyển d→e→a | BLOCKED ở mọi pha cho tới khi S4 đóng ở d/e; không PASS “theo pha” khi `open_assumptions` còn; ở a còn thiếu proof lịch sử | S4 đóng d/e; writer cho a | 3.1, 4.3.1 | S3-D/F |
| 25 | PRE_EFFECT min-scope (F2) | review binding khớp nhưng `items` chỉ có `TASK_PROJECTION(context)` hoặc một `FILE_BYTES` bất kỳ; thiếu `TASK_PROJECTION(accepted_task)` | `REVIEW_COVERAGE_INCOMPLETE`; binding khớp không cứu | — | 3.3.3 | S3-E |
| 26 | Ánh xạ intent→yêu cầu | review khớp binding, có accepted_task nhưng thiếu `intent_mapping` cho một requirement `mandatory`, hoặc `unconfirmed` không rỗng mà `unconfirmed_checked` thiếu | `REVIEW_COVERAGE_INCOMPLETE`; `mapping=PARTIAL/UNKNOWN` không đủ | — | 3.3.3 | S3-E |
| 27 | Staged→actual (F4) | V1 bind `STAGED_BYTES` S; V2/R bind `ACTUAL_BYTES` A khác S; (a) `relation=COPY_IDENTICAL` A≠S; (b) `TRANSFORM_BY_OWNER_TOOL`; (c) không staged | V1 và V2 mỗi cái so với anchor của mình, **không** so S với A; (a) `BINDING_MISMATCH`; (b) `UNSUPPORTED` ⇒ BLOCKED; (c) V1 `outputs` vắng hợp lệ. CP vẫn so ở accept cho cả V1, V2 | O cho A: S4 | 4.2, 4.3 | S3-E/F; S4 |
| 28 | Input bị ghi đè (D1) | `inputs=[X]`, action `overwrite` X; accept; có proof bytes X trước ghi gắn `E_req` | `inputs` khai so (C) với nhau; **không** đòi bytes hiện tại của X = `inputs[X].digest`; bytes sau ghi so với output riêng (`E_out`/`R`); proof trước ghi vẫn bắt buộc (xem AC-37) | O bytes sau ghi: S4; proof trước ghi: writer | 4.3.1 | S3-F; S4; writer |
| 29 | Veto TASK_WIDE (F4, D3) | non-PASS cho occurrence A; (a) occurrence B target rời nhau; (b) B chung target với A; (c) PASS hẹp hơn che A; (d) non-PASS không khai `subject`/list rỗng; (e) non-PASS khai `subject=PARTIAL` | (a) B **vẫn bị veto** (không suy độc lập từ target rời); (b) B bị veto; (c) veto A vẫn áp dụng (so giao, không so bằng); (d) `TASK_WIDE` ⇒ chặn cả task; (e) vẫn `TASK_WIDE` trong D0 (`PARTIAL` chỉ ghi nhận). Task khác không chịu veto này | — | 3.4 V-3, V-4 | S3-E |
| 30 | Review không đòi (F3) | task R-READ_DRAFT không Reviewer; (a) không `extra_review_phases`; (b) `extra_review_phases=[PRE_EFFECT]`; (c) R-DELEGATE gọi Reviewer | (a) không `REVIEW_MISSING`; (b) PRE_EFFECT đòi; (c) lời gọi Reviewer không bị review; mọi guard khác vẫn chạy | — | 3.3.4 | S3-E/F |
| 31 | Overlay đa bản/chồng (F5) | (a) hai record cùng `overlay_id` khác revision; (b) hai `overlay_id` classify chồng prefix; (c) `classify` do Main ghi (`MAIN_PROPOSAL`) hoặc `channel=USER_AUTHORED_FILE`; (d) classify prefix gốc rộng bao `references/`; (e) `classify` thư mục có descendant `protected_targets` | (a) AMBIGUOUS ⇒ tập overlay UNSUPPORTED ⇒ BLOCKED, không latest; (b) prefix dài nhất, bằng nhau lấy hạng cao hơn, `protect_more` thắng; (c) không mở vùng nhẹ; (d) bị bỏ qua; (e) descendant giữ nặng | nguồn bền Q-6 | 2.7 | S3-C/E |
| 32 | Hai occurrence cùng digest (F6) | task 2 action cùng projection ở index 0,1; review `actions_checked` chỉ index 0; một effect ghi index 0 | index 1 không được phủ ⇒ `REVIEW_COVERAGE_INCOMPLETE`; effect index 0 không tính cho index 1; không suy đã thực hiện cả hai | — | 4.4 | S3-E/F |
| 33 | Tính đủ & retry (F6, D2) | thiếu OUTCOME cho occurrence `REQUIRED`; `actions_performed` chỉ liệt kê tập con; OUTCOME `PARTIAL`+`APPLIED`; 2 OUTCOME `APPLIED` cùng occurrence; occurrence `OPTIONAL` không OUTCOME/không claim | `ACTION_INCOMPLETE`; tập bắt buộc lấy từ task, không từ result; `RETRY_UNRECONCILED`; `DUPLICATE_EFFECT_RECORD` (không là proof số lần thật); `OPTIONAL` không OUTCOME/không claim bỏ qua được | thao tác thật: owner ngoài | 4.4 | S3-F |
| 34 | Candidate không né accept (F7) | result `CANDIDATE`, thiếu outcome/yêu cầu/coverage bắt buộc | accept **BLOCKED**; `records_checked_state=CONSISTENT_IN_CHECKED_SCOPE` nếu nhất quán; aggregate đếm `not_checked` | — | 3.5 | S3-F |
| 35 | REQUIREMENTS review-free, xác nhận đủ đúng bản (D4) | route R-READ_DRAFT, không pha review đòi; `user_acceptance` có `task_id`/`task_revision`/`accepted_task_digest` = hiện hành, `accepted_requirements` ⊇ mọi `mandatory`, `result_id` + `accepted_artifacts` = `result.artifacts`, `presented_summary` | `USER_ACCEPTED_DECLARED` (DECLARED); các gate khác (ACTUAL_OUTCOME, proof lịch sử…) vẫn đến hạn; route đòi review ⇒ không dùng được (AC-17) | — | 3.2, 4.7.3 | S3-E/F |
| 36 | Accept sau create thành công (D1) | `create_new` `working/w1/a.docx` đã `APPLIED`; file nay tồn tại; có `E_out`, `R`, artifact digest | a: BLOCKED `UNSUPPORTED(PRECONDITION_PROOF_MISSING)` (thiếu proof lịch sử + liên kết); **không** báo `OPERATION_MISMATCH`, **không** route lại `overwrite` vì file có thật; `records_checked_state` nhất quán | writer proof (đích chưa tồn tại ngay trước thao tác, liên kết `E_req`↔`E_out`) + S4 bytes hiện tại khớp artifact ⇒ ACTUAL_OUTCOME/PATH_SCOPE-a đạt; chỉ S4 lstat hiện tại (file tồn tại) ⇒ không đủ | 4.3.1 | writer + S4 |
| 37 | Input bị ghi đè thiếu proof trước ghi (D1) | `inputs=[X]`, action `overwrite` X, `E_out` `APPLIED`, **không** có proof bytes X trước ghi gắn `E_req` (chỉ lời khai `inputs[X].digest` khớp ở các record) | e: INPUT_REVISION `NOT_CHECKED`; a: `UNSUPPORTED(PRECONDITION_PROOF_MISSING)` ⇒ BLOCKED; lời khai C khớp **không** thay proof O; bytes sau ghi không được so với `inputs[X]` | proof trước ghi gắn đúng `E_req`/occurrence (writer) + S4 bytes sau ghi so output ⇒ phần này đạt | 3.2 INPUT_REVISION, 4.3.1 | writer + S4 |
| 38 | OPTIONAL đã thực hiện (D2) | (a) occurrence `OPTIONAL` OUTCOME `APPLIED` có artifact; (b) `OPTIONAL` OUTCOME `UNKNOWN`/`PARTIAL`; (c) `OPTIONAL` `APPLIED` nhưng `actions_performed` bỏ sót; (d) result khai `EFFECT_APPLIED` cho `OPTIONAL` không có OUTCOME; (e) task không có `REQUIRED` nào, không OUTCOME/claim/artifact | (a) ACTUAL_OUTCOME đến hạn đầy đủ như `REQUIRED` (thiếu O/proof ⇒ BLOCKED); (b) `RETRY_UNRECONCILED` ⇒ BLOCKED, không bỏ qua; (c) `ACTION_UNREPORTED` ⇒ BLOCKED (không coi là “không có tác động”); (d) `ACTION_CLAIM_WITHOUT_OUTCOME`; (e) ACTUAL_OUTCOME `NOT_REQUIRED` nhưng REQUIREMENTS vẫn đến hạn | thao tác thật: owner ngoài | 4.4 | S3-F |
| 39 | Target rời nhưng có dataflow (D3) | occurrence A ghi `a.docx`; occurrence B ghi `b.docx` nhưng đọc `a.docx` qua `inputs`/`context_refs` hoặc artifact trung gian; A bị `CHANGES_REQUIRED` | B **bị veto** cùng A (TASK_WIDE); checker không cố phát hiện dataflow và không suy B độc lập từ target rời; B không bị chặn chỉ khi ở **task khác** | mô hình dependency được nhận (R-8) mới giảm veto | 3.4 V-3 | S3-E |
| 40 | User acceptance: các biến thể (D4) | (a) chỉ “đã nhận file”/im lặng/grant làm việc; (b) xác nhận gắn `task_revision`/`accepted_task_digest` cũ; (c) `accepted_requirements` thiếu một `mandatory`; (d) `accepted_artifacts` là bản cũ hoặc thiếu `result_id`; (e) xác nhận theo nhóm, tóm tắt đã trình liệt kê đủ tập, mọi trường đúng hiện hành | (a) không đủ ⇒ `USER_ACCEPTANCE_INCOMPLETE`, REQUIREMENTS `NOT_CHECKED` ⇒ BLOCKED; (b) `USER_ACCEPTANCE_STALE`; (c) phần thiếu `NOT_CHECKED` ⇒ BLOCKED; (d) `USER_ACCEPTANCE_STALE`; (e) `USER_ACCEPTED_DECLARED` (DECLARED) — user không viết JSON/xác nhận từng dòng; mọi biến thể: không thay review/veto/bytes/preservation | — | 3.2, 4.7.3 | S3-E/F |

---

## 7. Quyết định

### 7.1 Disposition Main đã chốt (Q-1…Q-11) và nơi áp dụng trong packet

| Q | Quyết định Main [M] | Áp dụng |
|---|---|---|
| Q-1 | Nhận hướng bốn version + cây owner v3 candidate riêng; chưa nhận cây code copy-forward/activation; một version hiệu lực chọn tường minh ở tích hợp; nợ trùng mã có owner trước release | 0.1, 1.1, 5.1 (S3-B0), 5.4 |
| Q-2 | Nhận bảng vùng trong policy, tách ba loại vùng sau F5; không suy folder membership thành authority change | 2.1.5, 2.3, 2.4, Δ01–Δ02 |
| Q-3 | Nhận R-MUTATION cho state/runtime như giới hạn candidate tạm; protocol/recipe là phụ thuộc bắt buộc trước tích hợp; không mặc định Reviewer mỗi lần ghi STATE; D0 không tự nhận recipe | 2.4, 5.4.1, AC-14 |
| Q-4 | Chưa mở đường nhẹ sửa đè draft; cần thiết kế/owner trước tích hợp; “vô hạn file mới” không là UX cuối; chưa thay bảo vệ bản gốc | 2.7 (dòng cuối), 5.4.2 |
| Q-5 | Nhận khai `content_use` cho output, dùng lại ý định đã biết, không hỏi lại nếu đã rõ | Δ03, 2.5(6), 2.7 |
| Q-6 | Nhận overlay có điều kiện theo F5; chưa chốt nguồn bền R4; chưa kích hoạt record bundle thành cấu hình project | 2.7, 4.7.1; còn mở: nguồn bền (7.2 R-4) |
| Q-7 | PATH_SCOPE đọc dựa lexical/declared trong ADVISORY, có giới hạn công khai; không suy nguồn đã đọc thật/đúng revision hay mở quyền gửi dữ liệu | 3.2 PATH_SCOPE, AC-13 |
| Q-8 | Hướng full-binding veto đúng pha/anchor và subject/scope theo F4, không supersession; reviewer không đủ tư cách không tạo PASS, non-PASS còn áp dụng vẫn chặn; chưa nhận phép so scope thu hẹp veto; user acceptance không gỡ veto | 3.4 V-1…V-6, AC-06/07/29 |
| Q-9 | Nhận hướng scope có tag, kết luận từng yêu cầu, REVIEW_COVERED; bỏ `action_digest` chỉ nhận sau khi F2/F4/F6 có biểu diễn thay thế đầy đủ; chưa nhận cả gói schema | 1.3, Δ08–Δ12, Δ17, 4.7 |
| Q-10 | Phân loại cấp file PROJECT và release_templates; hoãn tách theo mục; adapter dựng thay đổi cho user hiểu, không tự cấp grant | 2.3, 2.7 |
| Q-11 | Không nhận dispatch PASS khi route CONDITIONAL; effect/accept chờ proof tương ứng; không nhận tool claim tự khai thay quan sát | 3.1, AC-01/02/24 |

### 7.2 Disposition R-1…R-6 (Main, review R2) và điểm còn mở

| R | Vấn đề | Disposition Main [M] | Còn mở / khuyến nghị | Nếu không nhận |
|---|---|---|---|---|
| R-1 | Quy tắc veto V-1…V-6 phải chốt trước schema | V-1/V-2/V-4/V-5/V-6 nhận về hướng; **V-3 xác nhận ở mức thiết kế** — không nhận “disjoint ⇒ independent”; non-PASS veto `TASK_WIDE`, `PARTIAL` chỉ ghi nhận | Main xác nhận fallback V-3 bảo thủ và giới hạn TASK_WIDE; đây không phải nhận schema hoặc mở implementation. Mô hình giảm veto vẫn hoãn theo R-8 | Giữ veto v2 nguyên; Δ08 không hiệu lực |
| R-2 | Gói coverage thay `action_digest` | Nhận các phân biệt D1–D4 ở mức thiết kế; hướng `completion`, `extra_review_phases` (chỉ siết, không review đệ quy lời gọi Reviewer), `action_index`, `scope.subject`, `intent_mapping`, staged `relation`; chưa nhận triển khai cả gói | Rev 3 nhất quán ở mức thiết kế theo review Main/Reviewer; full binding/reconcile nhiều record vượt baseline trước khi có workflow nhiều action/pha được chứng minh. *Delta D0 (sau review):* luồng P-CN1 dùng một action `REQUIRED` (vắng `completion`), giữ `action_digest` v2, `role:"ACTUAL_BYTES"`, `effect.receipt_ref` và snapshot task chốt trước publish; Δ08, occurrence nhiều action, `STAGED_BYTES`/`relation`, review scope hoãn (bảng mốc 5.4) | Giữ `action_digest` v2; REQUIREMENTS/SOURCE_SCOPE không PASS |
| R-3 | `USER_ACCEPTED_DECLARED` | D4 là ứng viên cho workflow có bước accept tự động/nghiệm thu; chưa nhận schema/implementation cho baseline nháp người dùng trực tiếp xem/sửa | Giá trị với nháp thường còn thấp nếu không có bước tích hợp tự động; chỉ xem xét khi use case cần xác nhận gắn task/revision/requirements/artifact. *Delta D0 (M-3 Main):* luồng một action dùng **đủ D4 hiện hành** gắn snapshot P-CN1 (4.3.2), không tập con; thiếu ⇒ accept BLOCKED | Accept luồng review-free không PASS (chỉ diagnostic) |
| R-4 | Nguồn bền của overlay | **Hoãn tới R4 trước activation**; D0 chỉ record candidate trong bundle, không tự ghi profile/PROJECT hay cấp vùng nhẹ bền | không | `classify`/nguồn cũ ngoài `references/` chưa có chỗ ở lâu dài |
| R-5 | Cấu trúc code S3 | **S3-B0 đã chốt sau A0,18/10:** copy-forward foundation v3 có giới hạn; v1/v2 nguyên byte, không engine/kernel mới, không monkeypatch. Orchestrator/S3-G và G-04 sở hữu nợ trùng mã/kiểm packaging trước release; brief S3-B ở HANDOFF | Implementation B chưa có; chưa xóa v2, không tự ship cả hai runtime hoặc coi một version hiệu lực đã trả nợ | Không mở evaluator trước nhận foundation |
| R-6 | Proof đường nháp | Nhận phụ thuộc proof theo D1 (lịch sử, precondition, thao tác khi cần); **không** hứa read-only S4 đủ; không hạ acceptance để mở nháp trước proof | Chi tiết 4.3.1, 5.4.4 | Muốn nháp trước proof phải hạ acceptance — không nhận |
| R-7 (mới) | Biểu diễn và owner của proof lịch sử precondition + liên kết `E_req`↔`E_out` (D1) | Reviewer/Main giữ `UNSUPPORTED`/BLOCKED; `Transaction` chỉ là ứng viên owner publish, chưa đủ owner proof | Baseline chọn `create_new` đầu ra khi user yêu cầu. Review hẹp 18/10 kết luận thiết kế này chưa nhỏ trong owner hiện có: cần no-clobber; linkage request/action↔effect; xử lý crash/conflict; retention/tương thích journal; giới hạn OS/path. Không mở A0/schema/code hay receipt engine. Chặn accept PASS cho `create_new`/`overwrite` và INPUT_REVISION của input là target. Không ghi đè file có sẵn; A-06 không tự cung cấp proof lịch sử. *Delta D0 (sau review, DESIGN_PENDING_MAIN_REVIEW):* P-CN1 (4.3.2) cho `create_new` một file trên Windows NTFS local: no-clobber bằng `os.link`; snapshot task/yêu cầu/input chốt trong `prepared` trước publish; linkage `request_id` + đúng một file kết thúc; recovery chỉ nhận PUBLISHED khi identity + size + hash khớp, còn lại UNKNOWN, serialize bằng khóa byte trên `prepared`; envelope T1–T7 và mapping routing versioned theo scope M-2. M-1…M-5 đã có disposition Main; protocol chưa nhận, R-7 vẫn `UNSUPPORTED` tới khi P-CN1-C/I và A0 hẹp được nhận đúng bước. `overwrite`/input là target chưa có thiết kế | Mọi ghi chỉ BLOCKED ở accept; xem lại khi workflow thực tế cần accept ghi và có giao thức hẹp đủ bằng chứng |
| R-8 (mới) | Mô hình dependency giữa action để giảm veto PARTIAL (D3) | — (chưa chốt) | Hoãn; cần owner nhận mô hình khai độc lập **dương**; fallback TASK_WIDE. Không cần DAG ở D0 | Veto luôn TASK_WIDE (an toàn, rộng) |

**Không phải quyết định (vẫn mở, ngoài D0):** recipe, vai không-core, thời gian, ex19, x14/race, host enforcement (5.2); `effect_authorized=false` luôn; không receipt/grant thật; ADVISORY là trần.

---

## 8. Giới hạn của packet này

- Không byte schema/policy/contract/vectors/ví dụ/checker/test/pin nào bị sửa. JSON/pseudo-schema chỉ là phác thảo.
- Chưa kiểm: hàm chuẩn hóa path v1; `canon.py` tính `context_digest` khi `context_refs` vắng; tương tác S2 `COVER` với trường `coverage`; quan sát reparse/tồn tại trên Windows (S4); Python 3.8; số dòng module; thư mục con (`examples/demo-project`, `skills/*`, `packs/*`) chưa liệt kê từng file.
- UX là kịch bản đề xuất, chưa thử với người dùng/agent phiên mới. Ma trận 40 ca là kỳ vọng thiết kế chưa chạy.
- Chưa có mô hình dependency giữa action: D0 dùng fallback TASK_WIDE cho veto (3.4 V-3), nên có thể chặn rộng hơn mức tối thiểu cần thiết (R-8).
- Chưa có owner/biểu diễn cho proof lịch sử precondition và liên kết thao tác (R-7); các ca accept PASS cho ghi phụ thuộc phần đó và đang `UNSUPPORTED`/BLOCKED.
- Reviewer độc lập Sol 6.1 High đã review Rev 3, báo packet đủ để Main quyết định disposition thiết kế nhưng chưa đủ mở A0/schema/evaluator. Chưa chạy test/checker/probe, kiểm runtime hay thử nghiệm người dùng; path v1, context digest khi thiếu refs, `COVER`/coverage, Windows, Python 3.8 và ma trận 40 ca vẫn chưa kiểm.
- Review hẹp R-7 xác nhận `Transaction` chưa cung cấp request/effect linkage hoặc proof lịch sử; journal retention 20 và recovery/crash semantics làm thay đổi lớn hơn việc thêm một receipt field. Không thực hiện test/runtime review. Main giữ R-7 BLOCKED, không mở A0/code.
- **Delta D0 sau review — chưa kiểm thêm:** khóa byte ngoài EOF bằng `msvcrt.locking`/`LockFile` trên file đã ghi và không chặn đọc phần nội dung; cách đọc loại ổ/tên hệ file (NTFS local) từ Python; `st_dev`/`st_ino` trên Windows tương ứng volume serial/file index; độ dài API và cách công cụ soạn cung cấp digest input thật. POSIX bỏ khỏi tranche đầu.
- **Delta D0 (P-CN1, 4.3.2) chưa kiểm:** `os.link` trên NTFS báo `FileExistsError` khi đích có sẵn (kể cả khác hoa/thường) và giữ `st_ino` ổn định qua `os.stat` trên Windows/Python 3.8; hành vi trên FAT/exFAT, ổ mạng, OneDrive/thư mục đồng bộ; `held` có chặn đổi tên cha đúng trong luồng `os.link` như trong `Transaction`; POSIX `dir_fd` cho `os.link`; chuẩn hóa Unicode và 8.3 tự sinh; phần mềm diệt virus/indexer giữ file staged; Word/Excel lưu đè đổi identity (chỉ ảnh hưởng báo `OBJECT_REPLACED_SAME_BYTES`). Thông tin duy nhất đã chạy: một lệnh Python in `os.supports_dir_fd` trên máy này cho thấy `os.link` không hỗ trợ `dir_fd` (Windows) — không phải test hay probe hành vi ghi. Không tạo schema/fixture/test; P-01…P-15 là kỳ vọng.
- P-CN1 không thực thi grant, không chống giả mạo evidence (Main ghi được `.agent/runtime/`), không chứng minh nội dung đúng yêu cầu; công cụ soạn DOCX và kiểm định dạng ngoài phạm vi.

---

## 9. Mapping finding → mục đã sửa (Rev 1 → Rev 2)

| Finding | Sửa gì | Mục |
|---|---|---|
| **F1** PASS khi route còn điều kiện | Route `CONDITIONAL`/`UNRESOLVED` ⇒ BLOCKED mọi pha kể cả dispatch; giả định chỉ đóng bởi S4 trong cùng lượt; báo riêng record đã kiểm/giả định/pha/owner; bỏ dispatch PASS có điều kiện; AC-01/02/24 viết lại | 0.3, 0.8, 2.5, 3.1, 3.2 (PATH_SCOPE), 4.8, AC-01/02/20/24, 7.1 Q-11, 5.4.4 |
| **F2** Hợp review & phạm vi tối thiểu | Tách QUAL từng review khỏi COVERAGE của tập; chỉ phần review khai đã kiểm đóng góp; `NOT_CHECKED` không là coverage; PASS mâu thuẫn ⇒ non-PASS; bảng phạm vi tối thiểu PRE_EFFECT/PRE_INTEGRATION/PRE_DELIVERY (accepted_task, intent→requirement mapping, action); binding khớp không chứng minh mapping; không thêm digest review/effect/result; AC-10/22 sửa, AC-25/26 mới | 0.4, 3.3.2, 3.3.3, 3.3.5, 4.7.2, Δ09–Δ10, AC-10/22/25/26 |
| **F3** Review bị đòi cho mọi effect | Chỉ đòi pha có trong hợp policy ∪ `extra_review_phases`; không review đệ quy; không yêu cầu ngầm cho R-READ_DRAFT; bỏ câu Rev 1 4.4 | 3.3.4, 3.2 (REVIEW), Δ17, AC-30 |
| **F4** Anchor staged/actual và veto | Chuỗi REQUEST→V1→OUTCOME→result→V2/V3 với anchor và tập phần so từng pha; CP so lại ở accept; quan hệ staged→actual (`COPY_IDENTICAL`/`TRANSFORM_BY_OWNER_TOOL`) với owner proof; input bị ghi đè; veto V-1…V-6 theo phase/anchor/full binding + subject/occurrence/phạm vi, so giao, không supersession/user gỡ; chưa tự thu hẹp veto; cần chốt trước schema | 0.5, 3.4, 4.2, 4.3, 4.7.2–4.7.3, Δ08/Δ12, 1.3, AC-27/28/29, 7.2 R-1 |
| **F5** Overlay vừa cấm vừa hạ | Unknown là trạng thái UNCLASSIFIED, bỏ khỏi thứ tự hạng; overlay chỉ phân loại phần baseline chưa phân loại, không đè baseline/descendant/authority pattern/protected_targets/protect_more; reserved roots + `.agent/**` mặc định `framework`; xử lý nhiều overlay/mâu thuẫn/prefix chồng (AMBIGUOUS, không “mới nhất”); tách `source_class` khỏi `channel`; Main ghi overlay không tự mở vùng nhẹ; AC-19/31 | 0.2, 2.1.4–2.1.6, 2.3, 2.6, 2.7, 4.7.1, Δ01/Δ07, AC-19/31 |
| **F6** Occurrence & tính đủ | Occurrence `(task_id, revision, index, digest)`; tập action phải hoàn thành lấy từ task (`completion`), không từ result; trạng thái hoàn tất/partial/unknown/retry/duplicate; coverage dư không bù thiếu; không dùng số record làm proof số lần thật; phác thảo `result.actions_performed` | 0.6, 4.4, 4.7.3, Δ17, 3.2 (ACTUAL_OUTCOME), AC-32/33 |
| **F7** CANDIDATE né accept | Gate bắt buộc do task + route + pha; claim chỉ thêm kiểm; ma trận diagnostic vs accept; `records_checked_state`; aggregate đếm riêng; thêm `USER_ACCEPTED_DECLARED` cho luồng không đòi review | 0.7, 3.1, 3.2 (REQUIREMENTS, ACTUAL_OUTCOME), 3.5, 4.8, AC-01/34/35, 7.2 R-3 |
| **Q-1…Q-11** | Áp dụng như bảng 7.1; phần còn mở ở 7.2 | 7.1, 7.2, 5.1, 5.4 |

---

## 10. Mapping D1–D4 → mục đã sửa (Rev 2 → Rev 3)

| Residual | Sửa gì | Mục |
|---|---|---|
| **D1** proof lịch sử ≠ quan sát hiện tại | Ma trận pha × điều kiện × anchor × owner proof; quan sát read-only chỉ nói thời điểm quan sát, không chứng minh exclusive/race; accept không kiểm “đích hiện không tồn tại” và không route lại `overwrite`; input là target vẫn cần proof trước ghi gắn `E_req`, sau ghi so output riêng, không dùng lời khai C thay O; thiếu proof ⇒ `UNSUPPORTED`/BLOCKED; không hứa S4 đủ; thêm R-7 | 0.8, 2.5(3), 2.8, 3.2 (PATH_SCOPE, INPUT_REVISION, ACTUAL_OUTCOME), 3.5, **4.3.1**, 4.8, 4.9, 5.1, 5.2, 5.4.4, AC-01/02/12/24/28/36/37, 7.2 R-6/R-7 |
| **D2** OPTIONAL đã thực hiện | `completion` chỉ quyết nghĩa vụ thực hiện; mọi occurrence có OUTCOME hoặc được khai đã thực hiện (kể cả OPTIONAL) đến hạn ACTUAL_OUTCOME/reconcile; cách đối chiếu `actions_performed`/outcomes/artifacts (EXACT); PARTIAL/UNKNOWN không bỏ qua; task không có REQUIRED; không dùng việc bỏ claim/record làm chứng minh “không tác động” | 3.2 (ACTUAL_OUTCOME), 3.5, **4.4**, 4.8, AC-33/38 |
| **D3** không suy độc lập từ target | V-3: mọi non-PASS veto TASK_WIDE trong D0; `PARTIAL` chỉ ghi nhận; hoãn giảm veto tới khi có mô hình dependency/owner; ghi limitation + fallback; giữ veto theo pha/anchor/full binding, so giao; “review phủ action” là yêu cầu theo occurrence, không suy dataflow; nguyên tắc độc lập chỉ khi có căn cứ dương; thêm R-8 | 0.5, 3.1, **3.4 V-3**, 4.4, 5.2, AC-10/29/39, 7.2 R-1/R-8 |
| **D4** user acceptance đúng task/requirements/artifacts | `result.user_acceptance` gắn `task_id`/`task_revision`/`accepted_task_digest`, `accepted_requirements`, `result_id`, `accepted_artifacts`, `presented_summary`; đối chiếu với task hiện hành; một phần ⇒ phần còn lại `NOT_CHECKED`/BLOCKED; grant/“đã nhận file”/im lặng/task cũ không đủ; xác nhận theo nhóm bằng tóm tắt lời thường; chỉ cho REQUIREMENTS khi không đòi review; DECLARED | Δ11, 3.2 (REQUIREMENTS), 3.5, **4.7.3**, 4.8, AC-35/40, 7.2 R-3 |
| **R-1…R-6** | Áp dụng disposition Main; thêm R-7, R-8 | **7.2** |

---

## 11. Mapping brief delta D0 → mục đã sửa (Rev 3 → delta D0, 18/10/2026)

| Yêu cầu brief | Sửa gì | Mục |
|---|---|---|
| Một protocol được chọn, owner, thứ tự request → precondition → publish → evidence → kiểm/bàn giao | P-CN1, owner mới `tools/publish_new.py` tái dùng helper `transaction.py`; bảng 8 bước | 4.3.2, 0.8, 4.3.1 |
| Dữ liệu tối thiểu nối yêu cầu/action với file/digest thực; resolve liên kết | `prepared`/`published` theo `request_id`; resolve bằng tên file chính xác; ánh xạ sang record v3 | 4.3.2 |
| Lịch sử ≠ hiện tại; hash trùng không chứng minh nguồn gốc | `published` + identity là lịch sử; S4-min đọc hiện tại; `OBJECT_REPLACED_SAME_BYTES` | 4.3.2 |
| No-clobber, cha/alias, crash, evidence mất/hỏng, không auto-retry | `os.link`; `held`/`dir_fd`/`recheck_only`; bảng phục hồi tay | 4.3.2, 8 |
| R-2/R-3 tối thiểu; tách hoàn tất kỹ thuật/candidate/nghiệm thu | một action, giữ `action_digest`; (bản đầu: tập con D4 — đã thay bằng đủ D4 theo M-3 Main, xem Sửa 1/2) | 4.3.2, 7.2 R-2/R-3 |
| Ghi proof/runtime là tác động | owner, đường ghi, route và M-2; không giải STATE/HANDOFF | 4.3.2, 5.4.1 |
| Kế hoạch khớp phạm vi; 5.4 không âm thầm bỏ | 5.1 hàng P-CN1 + S4-min; 5.2; 5.4 delta từng mục + bảng mốc | 5.1, 5.2, 5.4 |
| Ví dụ đầu-cuối + bảng kỳ vọng | ví dụ giả và P-01…P-15 | 4.3.2 |
| Điểm Main quyết | M-1…M-5 | 4.3.2, 7.2 R-7 |
| **Sửa 1** snapshot yêu cầu/input trước publish | snapshot task trong `prepared`; bước 2 `INPUT_CHANGED_SINCE_READ`; hash lúc publish chỉ là quan sát | 4.3.2 (Snapshot, bảng bước, P-07/P-08) |
| **Sửa 2** API → canonical | bảng tham số → trường task; `targets`/`content_use` là set, `write_zone` do công cụ suy; bỏ payload `target` đơn | 4.3.2 (Snapshot, ví dụ) |
| **Sửa 3** recovery | PUBLISHED chỉ khi identity + size + hash; thiếu staged/đích ⇒ UNKNOWN; `abandoned` chỉ trong tiến trình; khóa byte serialize publish/recover; process crash | 4.3.2 (Phục hồi, P-09…P-14) |
| **Sửa 4** envelope + routing versioned | T1–T7; `owner_protocols` + mệnh đề gắn ghi runtime vào action với pin entrypoint; thiếu ⇒ R-MUTATION | 4.3.2 (Envelope), 5.2, 5.4.1, P-15 |
| **Sửa 5** kế hoạch một action/Windows NTFS local | 5.1 tách P-CN1-C / P-CN1-I / A0 hẹp; bảng mốc dùng/hoãn; 7.2 R-2/R-3/R-7; P-01…P-20 | 5.1–5.4, 7.2, 4.3.2 |
| **P-CN1-C (1)** signature publish/observe/status/recover/discard-staged | input/return/`outcome`/`reason` đóng, `wrote` theo T1–T7, CLI + mã thoát, hằng số | 4.3.3 C-1 |
| **P-CN1-C (2)** shape/version/serialization/size | request C-2.1; LAW-CJ/2 + strict parse C-2.2; bảng state C-2.3; snapshot + phần không bound + mapping D4/receipt C-2.4 | 4.3.3 C-2 |
| **P-CN1-C (3)** khóa/handle/state | offset 2^30, 1 byte, JSON ≤1 MiB, nonblocking/seek/unlock; ai giữ khóa; recheck sau khóa; sơ đồ chuyển trạng thái; proof ở I | 4.3.3 C-3 |
| **P-CN1-C (4)** eligibility trước tác động ≠ receipt sau | bảng d/e/a; grant phủ T1–T7; review đòi ⇒ UNSUPPORTED trước ghi | 4.3.3 C-4 |
| **P-CN1-C (5)** ví dụ request→prepared→published→D4 | JSON đầy đủ dữ liệu giả, projection để đối chiếu; P-21…P-26 | 4.3.3 C-5, C-6 |
