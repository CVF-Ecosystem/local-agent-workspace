# Checker v3 (candidate) — binding/routing (REVIEW_ACCEPTED) và luồng P-CN1 một file (REVIEW_ACCEPTED_WITH_LIMITS)

Trạng thái: giai đoạn `BINDING_ROUTING_ONLY` **REVIEW_ACCEPTED**; giai đoạn `P_CN1_ONE_FILE` (chỉ khi có `--root`) **REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS**. Vòng đời **CANDIDATE_NOT_ACTIVE**.
Đây **không** phải checker đầy đủ. Không `--root`: entrypoint, loader strict, canonicalization, helper refs/binding đã **nối** vào entry và routing thuần `routing.py` cho luồng một action; chưa gate/observer, không PASS, không NOT_APPLICABLE.
Có `--root` (mục "Luồng P-CN1 một file" cuối tài liệu): thêm observer chỉ đọc và gate + receipt + D4 cho đúng một task/action/target/grant; chỉ khi đó mới có PASS (ADVISORY). Chưa review verdict, delegation hay engine nào. `effect_authorized` luôn `false`.
Contract: `../../contracts/v3/CONTROL_CONTRACT.md` (output mục 11); owner cố định: `../../contracts/v3/control.schema.json` và `../../rules/v3/ROUTING_POLICY.json`.
Entry cũ `../control_check.py` (v1) và `../control_check_v2.py` (v2) giữ nguyên và không đọc cây này; entry v3 không gọi chúng, không chọn, không fallback. Chưa activation, profile, template, writer hay integration nào gọi entry v3.

## Provenance và nợ trùng mã

Foundation S3-B (đã nhận) là **copy-forward có giới hạn** của S1/S2 v2 (không phải engine v1, không đưa hàm tham chiếu từ test thành sản phẩm, không kernel/config tổng quát, không monkeypatch globals):

| File v3 | Gốc | Thay đổi so với gốc v2 |
|---|---|---|
| `__init__.py` | `../v2/__init__.py` | literal v3 (`urn:law:cvf:control:3`, `law.cvf.control/3`, `routing/3`, `bind/3`); `V2_SCHEMA_VERSION` chỉ cho gợi ý chẩn đoán |
| `loader.py` | `../v2/loader.py` | đường owner v3; thông điệp v3; gợi ý khi input là v1 hoặc v2; **S3-C/D:** tách `inspect_structure` (trả bundle đã qua cấu trúc), `inspect_bundle` giữ dạng bọc cũ |
| `canon.py` | `../v2/canon.py` | `BIND_VERSION = law.cvf.bind/3`; LAW-CJ/2 và projection giữ nguyên định nghĩa (contract v3 mục 7) |
| `refs.py` | `../v2/refs.py` | `effect.receipt_ref` và `result.user_acceptance.ref` thay `user_acceptance_ref`; từ vựng locator thêm `outcome`, `user_acceptance`, `ref` |
| `binding.py` | `../v2/binding.py` | thêm quan hệ `B-OUT-EFFECT` (`binding.outputs` = `outcome.artifacts` của effect OUTCOME); `action_digest` vẫn tùy chọn như v2 (Δ08 hoãn) |
| `routing.py` | **mới (S3-C/D)** | không có gốc v2; viết theo `ROUTING_POLICY.json` v3 canonical, không sao chép từ v1/v2 |
| `../control_check_v3.py` | `../control_check_v2.py` | không router `v1`/`v2`; chỉ `--contract v3`; output `law.cvf.check/3`; S3-C/D nối refs/binding/routing vào `_evaluate` |

**Nợ trùng mã.** Mã v2 foundation chưa kích hoạt và mã v3 này giống nhau ở phần lớn dòng. Owner xử lý: Orchestrator/S3-G và G-04. Trước release phải chọn **một** runtime version hiệu lực và loại foundation v2 chưa activated khỏi package có v3, kiểm nội dung package thực; chọn một version hiệu lực không tự giải nợ nếu vẫn ship cả hai runtime. Chưa xóa file v2; chưa tạo module dùng chung để trả nợ.

## Cây package

| File | Vai trò | Ghi chú |
|---|---|---|
| `../control_check_v3.py` | entry CLI/API, bootstrap package, `_evaluate` (binding, liên kết grant, routing), `_decide`, dựng output | chỉ nạp package v3 |
| `__init__.py` | hằng literal và giới hạn | không logic |
| `loader.py` | đọc bundle và hai owner cố định, parse strict, preflight version/basis/binding literal, schema Draft 2020-12, miền LAW-CJ/2 | chỉ đọc |
| `canon.py` | LAW-CJ/2, projection, digest theo contract v3 | không import từ `tests/` |
| `refs.py` | index record, nhóm lời khai inline, liên kết grant, kiểu kết quả | thuần, không I/O |
| `binding.py` | `PolicyContext`, kernel projection theo phần, comparator binding/set/pointer | thuần, không I/O |
| `routing.py` | đường dẫn lexical, vùng ghi, điều kiện T/F/U, hàng theo policy, kết quả route một action | thuần, không I/O, không đọc artifact; `external` (T/F/U của ENVELOPE, giả định do observer đóng) chỉ do workflow có root truyền vào |
| `observer.py` | observer chỉ đọc: gọi `observe`/`status`/`validate_evidence` của `tools/publish_new.py` (nạp từ cây LAW cố định) | chỉ nạp khi có `--root`; không ghi, không fetch |
| `workflow.py` | luồng P-CN1 một file: shape, gate, envelope T/F/U, lineage receipt, D4 | chỉ nạp khi có `--root`; không general engine |
| `README.md` | tài liệu này | |

Hash byte owner đã nạp chỉ để ghi nhận (`owner_protection = NOT_PROVEN`): tên file đúng không chống sửa. Loader **không** kiểm pin entrypoint của `tools/publish_new.py`: không đọc tool, không đọc file ngoài hai owner. Pin chỉ được so trong workflow có root (gate TOOL_SCOPE).

## Entrypoint và API

```text
python -B -I <tuyệt đối>/control_check_v3.py --contract v3 --phase {dispatch,effect,accept} [--format json|text] bundle.json
```

- `--contract` bắt buộc, chỉ nhận `v3`, không mặc định, không suy từ record, không auto-discover, không fallback. `v1`/`v2`/giá trị lạ/thiếu/trùng: lỗi argparse, stderr, exit 2, stdout trống.
- Chỉ một tùy chọn mở rộng: `--root DIR` (một lần, không rỗng), bật luồng P-CN1 một file; không có `--basis`, `--trust`, `--schema`, `--policy`, `--owner`, `--facts`, `--observer`, không router sang entry cũ, không override. Không `--root`: không observer, nguồn được đánh giá chỉ gồm bundle và hai owner (có test: không đọc `tools/`). Runtime còn nạp code/dependency và đọc METADATA của jsonschema; việc đó không là đọc artifact/locator.
- API: `check_bytes(data, phase, contract, *, project_root=None)`. `data` phải là `bytes` (khác: `TypeError`); `contract` chỉ `"v3"` và `phase` ∈ `dispatch/effect/accept` (khác: `ValueError`); `project_root` là `str` không rỗng hoặc `None` (khác: `TypeError`), chỉ keyword. Không `check_records`, không tiêm schema/policy/verifier/facts/observer. `exit_code(result)`: 2 lỗi khởi tạo/root; 0 chỉ khi `disposition=PASS`; 1 còn lại.

## Hợp đồng output (`law.cvf.check/3`, JSON object)

Đúng các trường sau, theo thứ tự này; không trường ngầm nào về verified/permit.

| Trường | Giá trị |
|---|---|
| `check_version`, `contract` | `"law.cvf.check/3"`, `"v3"` |
| `selection` | `"CLI_EXPLICIT"` hoặc `"API_EXPLICIT"` |
| `candidate_status`, `implementation_stage` | `"CANDIDATE_NOT_ACTIVE"`, `"BINDING_ROUTING_ONLY"` (không root) hoặc `"P_CN1_ONE_FILE"` (có root, kể cả khi cấu trúc/root lỗi) |
| `evaluation_basis` | `"COOPERATIVE_WORKFLOW"` chỉ sau khi basis đã validate; còn lại `null` |
| `phase` | pha được yêu cầu |
| `phase_scope` | `null` khi cấu trúc không đạt; khi cấu trúc đạt: `STRUCTURE` + các token `_BINDING`, `_ROUTING`, `_GATES`, `_OBSERVER` (theo thứ tự này, chỉ token thực chạy; ví dụ `STRUCTURE_ONLY`, `STRUCTURE_BINDING_ROUTING`, `STRUCTURE_BINDING_ROUTING_GATES_OBSERVER`). Nhãn phạm vi đã chạy, không phải pha; DENY/UNSUPPORTED sau đánh giá vẫn có thể có nhãn |
| `disposition` | `DENY` / `UNSUPPORTED` / `BLOCKED`; `PASS` **chỉ** ở stage `P_CN1_ONE_FILE` (mục cuối). **Không bao giờ** `NOT_APPLICABLE` |
| `effect_authorized`, `assurance_level`, `init_error` | `false`; `"UNVERIFIED"` (`"ADVISORY"` chỉ khi PASS); boolean |
| `reasons`, `details` | mã duy nhất đã sắp; chẩn đoán không chép payload/secret (không giá trị trường, không đường dẫn, không tên khóa trùng); `details` có tên quan hệ binding và trạng thái, không có giá trị |
| `owners` | `{schema_sha256, policy_sha256}`: hex SHA-256 byte thực đã nạp, hoặc `null` |
| `route` | `{evaluated, rows, status, assumptions}`. Xem mục Routing. Khi không tính được (không task, hoặc nhiều action): `{evaluated: false, rows: [], status: null, assumptions: []}` |
| `gates` | `[]` khi gate chưa chạy (không root, hoặc shape P-CN1 không hỗ trợ; không MET/NOT_CHECKED giả); với root và shape hỗ trợ: 8 gate theo mục cuối |
| `aggregate` | khi gate chưa chạy: `records_checked_state = "NOT_EVALUATED"`, mọi bộ đếm `0`, `open_assumptions = []`, `conclusion_scope = "RECORD_CONSISTENCY_IN_MEMORY"` (placeholder, không phải kết luận về route); khi gate chạy: `CONSISTENT_IN_CHECKED_SCOPE`/`INCONSISTENT` và bộ đếm tính từ `gates` |
| `coverage` | `record_structure_checked`; `binding_evaluated` (true khi ít nhất một quan hệ binding đã tính đủ); `routing_evaluated` (true khi route một action đã được tính); `gates_evaluated`, `artifact_bytes_observed`, `target_existence_observed` chỉ true khi workflow có root thực sự đánh giá/quan sát trong lần kiểm này; `actual_operation_observed`, `requirements_semantic_verified` luôn `false`; `owner_protection="NOT_PROVEN"` |

Cờ `binding_evaluated` và `routing_evaluated` chỉ bật khi đã tính thật trong lần kiểm này. Helper chạy riêng trong tiến trình không bật cờ của entry (có test).

## Routing (`routing.py`)

Route được tính từ **task/action trong bundle** (`operation`, `targets`, `write_zone` khai, `content_use`, `recipe`, task preservation/protected_targets/authority.grant_refs) và bảng `ROUTING_POLICY.json`. `effect.routing` tự khai **không** là nguồn; nếu có và khác route đã tính thì báo `ROUTE_DECLARED_MISMATCH`.

- **Đường dẫn (lexical).** POSIX tương đối, casefold để so khớp theo đoạn nguyên. **Từ chối, không normalize:** rỗng, tuyệt đối, `\`, `:`, ký tự điều khiển, đoạn rỗng (`//`, `/` cuối), `.`/`..`, đoạn có khoảng trắng đầu/cuối hoặc kết thúc bằng `.`, tên 8.3 (`~<số>`), tên thiết bị Windows (gồm conin$/conout$) và ký tự `<>"|?*`. Dạng không hỗ trợ ⇒ `PATH_UNSUPPORTED_FORM` ⇒ UNSUPPORTED, trừ known-loss đã khai vẫn ưu tiên DENY. Đã đối chiếu `_segments` v1 vốn bỏ đoạn rỗng; Orchestrator/Reviewer nhận v3 từ chối rõ theo packet/path contract, không sửa v1 hoặc claim quan sát filesystem.
- **Vùng.** Hạng cao nhất trong các nguồn đã phân loại: `zone_map` theo tiền tố dài nhất (ranh giới đoạn); tên khớp `authority_name_patterns` ⇒ `framework`; liên quan `protected_targets` (kể cả tổ tiên của đích) ⇒ tối thiểu `original_source`. **Vùng khai chỉ nâng, không hạ, không tự phân loại đường dẫn**: đường dẫn không nguồn nào phân loại ⇒ `UNCLASSIFIED`, kể cả khi khai `working`. Khai `unknown` ⇒ `UNCLASSIFIED`. Thao tác ghi khai `none` hoặc không có đích ⇒ `UNCLASSIFIED`; `read`/`delegate` khai khác `none` ⇒ `UNCLASSIFIED`. Tập ghi của `read`/`delegate` rỗng.
- **Điều kiện, logic Kleene T/F/U.** `U` không bao giờ là `F`. Một hàng có `U` làm route thành `UNCLASSIFIED` (TREAT_AS_UNCLASSIFIED).
  - `NO_PROTECTED_TARGET`: tập ghi rỗng ⇒ T; có `UNCLASSIFIED`/`UNSUPPORTED` ⇒ U; mọi vùng thuộc `light_write_zones` ⇒ T; còn lại F.
  - `CONTENT_USE_INTERNAL_ONLY`: `content_use` vắng/rỗng ⇒ U; mọi phần tử `internal_draft` ⇒ T; còn lại F.
  - Recipe: không có `recipe` ⇒ `RECIPE_ACCEPTED_VERSION` F, `RECIPE_ABSENT_OR_CHANGED` T; có `recipe` ⇒ các điều kiện recipe U và `RECIPE_NOT_IN_CANDIDATE` (UNSUPPORTED).
  - `KNOWN_PRESERVATION_LOSS`: có mục `KNOWN_LOSS` ⇒ T; có `UNKNOWN` ⇒ U; vắng ⇒ F (không có điều biết được thì không phải "đã biết mất"). Schema preservation **có target bắt buộc**; veto task-wide là fallback bảo thủ khi chưa ánh xạ preservation→action, không phải do thiếu trường target. Known-loss đã khai vẫn DENY khi nhiều task/action chưa được hỗ trợ; không dùng early UNSUPPORTED để che veto.
  - `MISSING_AUTHORITY`: `grant_refs` rỗng ⇒ T. `UNCLASSIFIED`: có vùng/ hợp đồng/ thao tác không phân loại được.
  - `ENVELOPE_EXCEEDED`: thuộc gate ENVELOPE (so với grant), chưa đánh giá nên **U, không F**; ghi trong `not_evaluated_conditions`. Hàng có thể áp dụng vẫn góp gate/pha review vào hợp bảo thủ, không bỏ R-EXTERNAL chỉ vì gate chưa làm. `MISSING_REQUIRED_REVIEW` là U khi có pha phải review nhưng chưa kiểm verdict, không tự kết luận REVIEW_MISSING; nếu không có pha cần review thì F.
- **Hàng.** Một mệnh đề T làm hàng chắc chắn khớp; chưa có T nhưng còn U thì hàng có thể áp dụng (OR giữa mệnh đề, AND trong mệnh đề). Route diagnostic giữ cả T/U và ghi `match_state` từng hàng, hợp gate/pha review của cả hai; chỉ F bị loại. Có U ⇒ R-UNCLASSIFIED và route UNRESOLVED, không rơi về nhánh nhẹ. Không xóa nghĩa vụ của R-READ_DRAFT hay hàng khác chỉ vì thêm R-UNCLASSIFIED; các hàng còn hiện không có nghĩa được phép. Forced DENY chỉ do hàng T, không do U.
- **A-NEW_TARGET.** Nếu một mệnh đề `create_new` khớp, giả định mở: ở `dispatch`/`effect` trạng thái `OPEN` ⇒ route `CONDITIONAL` ⇒ BLOCKED; ở `accept` `NOT_APPLICABLE_IN_PHASE` (accept không kiểm đích-vắng). Không có S4 observer nên không bao giờ đóng ở đây.
- **Trạng thái route.** `UNRESOLVED` khi có `R-UNCLASSIFIED` khớp; `CONDITIONAL` khi còn giả định OPEN; `RESOLVED` khi còn lại.
- **Đánh giá một action.** Task đúng một action mới được route. Nhiều action ⇒ `MULTI_ACTION_UNSUPPORTED` (không bịa action); nhiều task ⇒ `MULTI_TASK_UNSUPPORTED`; không có task ⇒ không tính route, không bịa.

EXPECTED giữ nguyên là kỳ vọng phản thực tế. Test oracle giả định ENVELOPE_EXCEEDED=F bằng policy copy chỉ trong test và ghi rõ điều kiện; đây không phải bằng chứng route runtime. Regression với **policy canonical thực** chứng minh ENVELOPE chưa kiểm là U, R-EXTERNAL vẫn giữ nghĩa vụ gate/review; vì vậy ngay cả fixture dự kiến happy path hiện cũng có route UNRESOLVED. Không sửa policy/vectors/EXPECTED để làm xanh.

## Binding và liên kết grant (đã nối vào entry)

- Với mọi record `review`/`effect`/`result` có `binding`: `binding.compare_binding` ở đúng vị trí; `MISMATCH` ⇒ `BINDING_MISMATCH` (BLOCKED); `UNSUPPORTED` ⇒ `UNSUPPORTED_BINDING_PART` (UNSUPPORTED); `INCOMPLETE`/`AMBIGUOUS`/`ONE_SIDED` ⇒ `BINDING_INCOMPLETE` (BLOCKED).
- Liên kết grant cho `task` và `effect` (`refs.link_grants`): `CONFLICT` ⇒ `REF_CONFLICT`; `AMBIGUOUS` ⇒ `REF_AMBIGUOUS`; `NO_GRANT_RECORD` ⇒ `GRANT_MISSING`; `INCOMPLETE` ⇒ `REF_INCOMPLETE`; `UNSUPPORTED` ⇒ `REF_UNSUPPORTED` (UNSUPPORTED). `LINKED` chỉ là lời khai nối, không phải quyền. Mâu thuẫn lời khai inline cùng `ref_id` ⇒ `REF_CONFLICT`.
- Bundle một record đứng riêng (ví dụ effect không kèm task) được nêu rõ: binding không đủ, không bịa.

## Hợp đồng disposition và reason

Thứ tự: **DENY** (known-loss) > **UNSUPPORTED** (phần không hỗ trợ) > **BLOCKED**. Mọi lý do đã tính đều nằm trong `reasons`.

| Tình huống | Disposition | Reasons | Exit |
|---|---|---|---|
| cấu trúc hợp lệ, không có lý do chặn khác, **không root** | `BLOCKED` | `CANDIDATE_EVALUATION_NOT_IMPLEMENTED` (gate chưa đánh giá) | 1 |
| root + shape P-CN1 hỗ trợ + route `RESOLVED` + mọi gate đến hạn đạt | `PASS` (`ADVISORY`, `effect_authorized=false`) | — | 0 |
| root + shape không hỗ trợ | `UNSUPPORTED` | `P_CN1_SHAPE_UNSUPPORTED` (cộng lý do khác đã tính) | 1 |
| root + gate đến hạn `NOT_MET`/`NOT_CHECKED`/`UNSUPPORTED` hoặc route chưa `RESOLVED` | `BLOCKED` | mã của gate (xem mục cuối) | 1 |
| root không phải thư mục | `UNSUPPORTED`, `init_error=true` | `ROOT_UNUSABLE` | 2 |
| hàng `R-KNOWN_LOSS` khớp (mục `KNOWN_LOSS` của task) | `DENY` | `KNOWN_PRESERVATION_LOSS` | 1 |
| path dạng không hỗ trợ; action có `recipe`; nhiều action; nhiều task; lỗi UNSUPPORTED của binding/ref | `UNSUPPORTED` | `PATH_UNSUPPORTED_FORM`, `RECIPE_NOT_IN_CANDIDATE`, `MULTI_ACTION_UNSUPPORTED`, `MULTI_TASK_UNSUPPORTED`, `UNSUPPORTED_BINDING_PART`, `REF_UNSUPPORTED` | 1 |
| `R-UNCLASSIFIED` khớp; `PRESERVATION_UNKNOWN`; đòi review chưa hỗ trợ; giả định A-NEW_TARGET OPEN; lệch binding/ref/khai báo route | `BLOCKED` | `UNCLASSIFIED_OPERATION`, `PRESERVATION_UNKNOWN`, `REVIEW_REQUIRED_UNSUPPORTED`, `ROUTE_ASSUMPTION_OPEN`, `BINDING_MISMATCH`, `BINDING_INCOMPLETE`, `REF_CONFLICT`, `REF_AMBIGUOUS`, `REF_INCOMPLETE`, `GRANT_MISSING`, `ROUTE_DECLARED_MISMATCH` (cùng `CANDIDATE_EVALUATION_NOT_IMPLEMENTED`) | 1 |
| schema sai; cấu trúc sai; input hỏng; vượt 8 MiB | `DENY` (`SCHEMA_INVALID`, `INPUT_MALFORMED`) | như bảng cũ | 1 |
| dữ liệu **bound** ngoài miền LAW-CJ/2 (chuỗi không NFC, surrogate đơn, số thập phân hoặc ngoài ±(2^53−1), khóa sai mẫu), xem mục Screening | `UNSUPPORTED` | `UNSUPPORTED_BINDING_PART` | 1 |
| version/basis/binding literal sai, bundle v1/v2 hoặc trộn | `UNSUPPORTED` | như bảng cũ | 1 |
| lỗi khởi tạo (dependency, owner, package không nạp, bundle không đọc được) | `UNSUPPORTED`, `init_error=true` | như bảng cũ | 2 |
| lỗi cú pháp/tùy chọn CLI | stderr argparse, không có JSON | — | 2 |

Exit 0 chỉ khi PASS của luồng có root; không có exit 3. Lỗi khởi tạo không bao giờ thành DENY/PASS của user. Mã `PATH_UNSUPPORTED_FORM`, `RECIPE_NOT_IN_CANDIDATE`, `MULTI_*`, `REF_*`, `ROUTE_*`, `BINDING_INCOMPLETE`, `GRANT_MISSING` do checker phát ra; không sửa enum `reason_code` của schema.

Thứ tự kiểm: owner/dependency → parse strict → version → basis → literal binding → schema → screening canonical theo projection (`canon.bound_violations`) → binding/liên kết grant → routing → disposition. `--format text` cho cùng disposition/exit/giới hạn.

## Screening miền canonical theo projection

Trước đây loader quét **mọi** giá trị của bundle theo LAW-CJ/2 (`canon.domain_violations`), nên một chuỗi không NFC trong `note` hay một số lớn trong `grant.limits` bị từ chối dù không bao giờ đi vào digest. Nay `canon.bound_violations(records)` chỉ kiểm dữ liệu **thật sự được canonicalize**, bằng cách gọi lại đúng các builder C1 và khóa object của comparator (`_object_keys`): `intent_part`, `context_part`, `task_part`, `action_part`, `ref_proj`, `obj_proj`, `sorted_set`. Không có projection, phép băm hay normalize mới; `domain_violations` và mọi builder giữ nguyên (API canonical thuần vẫn LAW-CJ/2 như cũ).

Phân loại theo **vai trò trường** của loại record, không theo việc bundle này có đủ record đối ứng.

| Record | Được screening (đi vào) | Qua | Không screening (metadata bị loại hoặc so thô) |
|---|---|---|---|
| `task` | `intent.refs`; `context_refs`; `schema_version`, `evaluation_basis`, `work_id`, `task_id`, `task_revision`, `intent.main_interpretation`, `intent.unconfirmed`, `authority.subject`, `authority.grant_refs`, `inputs`, `effects.*` (actions, on_missing, protected_targets, preservation, expected_outputs), `acceptance`, `envelope` | `intent_part`, `context_part`, `task_part` (gồm `action_proj`) | `proposed_by`, `note`, `example_only`, `route_proposal`; trong mỗi ref: `ref_id`, `locator`, `attribution`, `issuer`; trong mỗi object: mọi khóa ngoài `path`, `digest`, `source_id`, `revision`, `scope` |
| `effect` | `action`; `binding.inputs`; chỉ khi OUTCOME và `binding.outputs` có mặt: `binding.outputs`, `outcome.artifacts` | `action_part`, `obj_proj` | các trường `binding` khác (so thô: literal, digest, `task_id`, `task_revision` là khóa tra cứu, `action_digest`), `actor`, `routing`, `grant_ref_ids`, `review_ids`, `assurance_level`, `disposition`, `reasons`, `decided_by`, `receipt_ref`, `note`; `outputs` của REQUEST (NOT_APPLICABLE) |
| `review` | `binding.inputs` | `obj_proj` | các trường `binding` khác, `scope`, `reviewer`, `findings`, `receipt_ref`, `verdict`, `phase`, `note` |
| `result` | `binding.inputs`; khi `binding.outputs` có mặt: `binding.outputs`, `artifacts`; khi có `user_acceptance`: `user_acceptance.accepted_artifacts` (so EXACT với `artifacts` ở D4, quan hệ `D4-ARTIFACTS`) | `obj_proj` | các trường `binding` khác, `acceptance_states`, `actions_performed`, `evidence`, `gaps`, `requirements`, `produced_by`, `state_set_by`, `note`; trong `user_acceptance`: `ref` (so thô theo nhóm lời khai), `task_id`, `task_revision`, `accepted_task_digest`, `accepted_requirements`, `result_id`, `presented_summary` (so thô theo chuỗi/tập id, không canonicalize) |
| `grant` | không có | — | toàn record (kể cả `limits`) |
| policy | toàn object policy | `policy_part` (owner cố định, `binding.make_policy_context`) | bundle không chứa policy (`routing_policy` bị schema loại) nên không thuộc hàm này |

Ghi chú:

- `bound_violations` không được dùng để chọn "có hỗ trợ không" bằng tên trường: danh sách trên suy từ chính builder và comparator, và test sweep (`tests/test_control_v3_canonical_screening.py`) kiểm từng lá của ví dụ: một lá là bound khi đổi nó sang giá trị trong miền làm đổi digest hoặc quan hệ binding.
- Vẫn do schema và guard của loader áp cho mọi trường, kể cả metadata: strict JSON/UTF-8/khóa trùng/nonfinite, literal version/basis/bind, schema Draft 2020-12, giới hạn 8 MiB và độ sâu. "Ngoài digest" không có nghĩa miễn kiểm.
- Trùng phần tử của một tập (`DUPLICATE_SET_ELEMENT`) **không** là vi phạm miền: helper projection/comparator báo UNSUPPORTED theo từng phần và không dedupe; helper thuần gặp hình dữ liệu sai báo `MALFORMED_RECORD`. Screening không chuyển hai việc đó lên sớm hơn. Ở entry, hình sai schema đã bị DENY/SCHEMA_INVALID trước screening; không đổi thành lỗi canonical.
- Entry kiểm phần projection của từng task và tính hợp lệ riêng của `binding.inputs` kể cả thiếu record đối ứng. Kiểm riêng một tập không chứng minh binding: thiếu task vẫn giữ BINDING_INCOMPLETE, không bật `binding_evaluated` chỉ vì recompute hoặc so tập với chính nó.
- Vi phạm miền trong phần bound ⇒ `UNSUPPORTED` / `UNSUPPORTED_BINDING_PART` như trước, `details` chỉ ghi tên phần (từ vựng đóng) và số đếm theo mã lý do, không chép giá trị; chưa binding/routing nào chạy. Digest của dữ liệu vốn được hỗ trợ không đổi (vectors giữ byte).
- Delegation pointers (`compare_pointers`) chưa nối entry nên chưa được screening; khi nối phải bổ sung vào bảng này.
- Workflow có root nối thêm các so sánh: `accepted_artifacts` ↔ `result.artifacts` (đã thêm vào bảng, có paired test và đã vào `fingerprint` của sweep), `task.inputs` ↔ `prepared.inputs_observed_at_publish`, artifacts ↔ published. Hai so sánh sau dùng dữ liệu bundle đã screening và evidence do owner xác nhận canonical LAW-CJ/2 (`validate_evidence`), nên không thêm đường dữ liệu chưa screening; `receipt_ref.digest`, `task_id`, id yêu cầu so thô. Không canonicalize toàn metadata.

## Các quyết định và giới hạn của candidate

1. `ENVELOPE_EXCEEDED` chưa đo nên giữ U trong route và ghi `not_evaluated_conditions`; mọi hàng T/U cùng nghĩa vụ của chúng đều được giữ. Không coi chưa kiểm là F; canonical policy hiện có thể cho route UNRESOLVED cùng nghĩa vụ R-EXTERNAL.
2. Khi hợp hàng T/U đòi review, checker báo `REVIEW_REQUIRED_UNSUPPORTED` (BLOCKED), chưa kết luận review đã có hay thiếu. `MISSING_REQUIRED_REVIEW` giữ U khi có pha review cần kiểm, F khi không có; không bỏ hàng R-UNCLASSIFIED có thể áp dụng.
3. `KNOWN_PRESERVATION_LOSS` là veto mức task: `preservation.target` có trong schema, nhưng chưa có mapping preservation → action. Một mục `KNOWN_LOSS` vì vậy chặn cả task theo fallback bảo thủ, kể cả khi nhiều task/action khiến routing UNSUPPORTED. Vắng mục ⇒ F.
4. `content_use` vắng không làm `R-HIGH_STAKES` không xác định (không khớp). Vắng `content_use` vẫn làm nhánh C (`output_new`) của R-READ_DRAFT là U ⇒ UNCLASSIFIED (ex15). Đây là đọc luật theo EXPECTED ex01/ex15.
5. Khai `write_zone` không nâng được đường dẫn chưa phân loại; khai `none` trên thao tác ghi là mâu thuẫn ⇒ UNCLASSIFIED và không để hàng nhẹ đi cùng.
6. Đường dẫn: từ chối dạng không hỗ trợ thay vì bỏ đoạn rỗng như v1 (`_segments`); khác biệt này đã được nhận trong review C/D. Không sửa hành vi v1.
7. `phase_scope` là nhãn phạm vi đã chạy, không phải pha; ghép tên theo cờ coverage.
8. Screening miền canonical đã chuyển từ quét toàn bundle sang **projection-aware** (mục "Screening miền canonical theo projection"): nợ này đóng ở đúng phạm vi đó. Không đóng R-7/G-03/G-04, không mở gate/PASS; vượt qua screening không chứng minh grant, nguồn, route hay effect được phép.
9. `aggregate` vẫn là placeholder (`NOT_EVALUATED`) vì bộ đếm là của gate; route không được đọc qua đó.

## Helper trong bộ nhớ: refs/binding (đã nối vào entry, không là evaluator)

- `refs.build_index(records) -> RecordIndex`; `refs.collect_claims(index) -> ClaimTable`; `refs.link_grants(index, claims, position)` trả tuple `GrantLink`; `link_is_authority=false`.
- `binding.make_policy_context(policy_bytes)`, `recompute_task(task)`, `compare_binding(index, position, policy_ctx) -> BindingReport`. Quan hệ: `B-REF`, `B-LIT.*`, `B-INTENT`, `B-TASK`, `B-CONTEXT`, `B-POLICY`, `B-INPUTS`, `B-ACTION-OWN`, `B-ACTION-IN-TASK`, `B-ACTION-CLAIM`, `B-OUT-RESULT`, `B-OUT-EFFECT`. `action_digest` và `outputs` tùy chọn: vắng ⇒ `NOT_BOUND`; hiện diện ⇒ phải so đầy đủ.
- Mọi `Relation`, `ClaimGroup`, `GrantLink`, `BindingReport` mang `bytes_observed=false`, `authenticity_observed=false`, `semantic_verified=false`. Digest được tính mới từ record đã resolve; digest khai báo không bao giờ là bằng chứng.
- Không đọc artifact/locator, không gọi publish/observe, không đọc receipts/project filesystem.

## Luồng P-CN1 một file (`--root`, `P_CN1_ONE_FILE`, REVIEW_ACCEPTED_WITH_LIMITS)

Review mới nhất18/10: **REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS**, cùng một task/snapshot/digests xuyên dispatch → effect → publish → accept trên Windows NTFS local; COOPERATIVE/ADVISORY, vẫn CANDIDATE_NOT_ACTIVE. Reviewer sửa docstring về collision muộn/wrote và pin/digest dẫn xuất đã đồng bộ. Các dependency từng tìm thấy đã khép trong luồng hẹp; chưa integration/activation/G-03/G-04. Khởi tạo runtime dùng cơ chế init/transaction hiện có (probe init trên project giả đạt), còn kiểm hành trình đầy đủ ở G-04.

Caller dùng: chọn rid 32 hex thường → `pn.build_task(request, rid)` → dispatch/effect → `publish(root, request, staged, request_id=rid)` (hoặc CLI `--rid`) → accept với đúng task đó. Không chọn rid thì writer tự sinh UUID và task tại accept là task khác với task đã lập kế hoạch (không còn là cùng snapshot).

Chỉ chạy khi có **root tường minh**: CLI `--root DIR` (một lần), API `check_bytes(data, phase, contract, *, project_root=None)`. Không root: mọi phần ở trên giữ nguyên (diagnostic `BINDING_ROUTING_ONLY`, `gates=[]`, không PASS, không đọc `tools/`). Có root: `implementation_stage = P_CN1_ONE_FILE`, và observer + gate chạy cho đúng **một task / một action `create_new` (tool `publish_new`) / một target / một `grant_ref`**. Ngoài shape đó ⇒ `UNSUPPORTED` + `P_CN1_SHAPE_UNSUPPORTED` (chi tiết đóng, không giá trị): nhiều task/action/grant_ref, tool/operation khác, đích ngoài `working/`/`output/` hoặc dạng path không hỗ trợ, `recipe`/`delegation`/`payload`, input trùng đích (overwrite), `task_id` không dạng `pcn1-<rid 32 hex>`, không có mục `owner_protocols` khớp. Task đúng shape nhưng owner không dựng lại được (custom `envelope`, `context_refs`, `protected_targets`, `preservation`... mà `build_task` bỏ) **không** là shape lỗi: gate vẫn tính và giữ chẩn đoán, còn TOOL_SCOPE `UNSUPPORTED` + `TASK_NOT_OWNER_REPRESENTABLE` chặn PASS. Thiếu/nhiều/xung đột record grant là kết quả gate GRANT_SCOPE, không phải shape.

**Root là dữ liệu.** Root không phải thư mục tồn tại ⇒ `UNSUPPORTED` + `ROOT_UNUSABLE`, `init_error=true`, exit 2, không echo đường dẫn; root là junction/symlink hoặc runtime/cha bị link ⇒ owner báo `RUNTIME_LINKED`/`PARENT_UNSAFE`, quan sát không có (`NOT_CHECKED`), không PASS. Code owner (`tools/publish_new.py`) và `tools/transaction.py` chỉ nạp từ cây nguồn LAW cố định tính từ vị trí `observer.py` (`.cvf/checks/v3/` lên ba cấp); **không** import, exec hay đọc cấu hình từ root. Không tùy chọn owner/schema/policy/basis/facts/observer; không đường tiêm facts (API và CLI). Chỉ nạp khi có root (lazy), nên đường không-root vẫn chứng minh không đọc `tools/`.

**Observer (`observer.py`, chỉ đọc).** Mỏng, gọi lại `publish_new.observe`/`status`/`validate_evidence` và đọc raw tới `MAX_JSON_BYTES`; không gọi `publish`/`recover`/`discard_staged`, không mkdir, không ghi evidence, không fetch locator/URL (evidence chỉ ở thư mục publish cố định của owner (thư mục runtime publish dưới `.agent`, tên file theo rid) của đúng rid). Giới hạn của owner được giữ: Windows NTFS local, `tamper_resistance=NONE`, quan sát tại thời điểm. Lỗi/thiếu quan sát ⇒ `NOT_CHECKED`/`UNSUPPORTED` kèm `OBSERVATION_UNAVAILABLE` (hoặc mã owner đã đóng như `UNSUPPORTED_FS`, `RUNTIME_LINKED`), **không** coi là "vắng file". Mọi ngoại lệ từ owner bị bắt và không echo thông điệp.

**Gate (đến hạn theo pha; không đến hạn ⇒ `NOT_YET_DUE`).** `due_in`: d = dispatch, e = effect, a = accept.

| Gate | d | e | a | MET khi (tất cả) |
|---|---|---|---|---|
| GRANT_SCOPE | ✓ | ✓ | ✓ | `grant_ref` resolve duy nhất (qua `issuer_ref.ref_id`, link LINKED); grant `ACTIVE` (không `example_only`/EXAMPLE_INACTIVE); cả ref ở task và `issuer_ref` của grant là `USER_CONFIRMATION`; `subject.roles` ∋ vai và `actor_ids` (nếu có) ∋ actor; actor của record pha (`effect.actor`, `result.produced_by`, `task.proposed_by`) trùng `task.authority.subject`; `operations ⊇ {create_new, delete}` (delete chỉ để phủ T7 staged cùng rid, checker không thể ép thêm), `tools ∋ publish_new`; `scope.paths` phủ **mọi tổ tiên và đích** (T1, T5) và thư mục runtime publish của owner (thư mục con publish của runtime dưới `.agent`) (T2–T4, T6, T7) theo đoạn nguyên, không tiền tố chuỗi, không glob; dạng path chưa hỗ trợ trong grant không phủ gì. `task_classes` là mô tả tự do: không kiểm ngữ nghĩa (limit `TASK_CLASSES_NOT_CHECKED`) |
| PATH_SCOPE | ✓ | ✓ | ✓ | `lexical`: đích ∈ vùng nhẹ theo route và path nằm trong grant; `observed_at_time` (d e): observer thấy volume NTFS local, cha link-free, `.agent` và `.agent/runtime` **có sẵn** là thư mục thường (`runtime_parents_ready`; thiếu ⇒ `NOT_MET` + `RUNTIME_PARENT_MISSING`, không quan sát được ⇒ `NOT_CHECKED`), rid chưa có evidence và đích **vắng** (limits `EXCLUSIVE_WRITE_NOT_PROVEN`, `RACE_NOT_EXCLUDED`); `precondition_history` (a): đúng một evidence `published` hợp lệ cùng một `prepared` hợp lệ cho rid, file runtime của rid ⊂ {prepared, published, staged}, snapshot task trong `prepared` khớp task hiện hành (intent/task/context/action tính lại), `prepared.content` = `published.content` |
| TOOL_SCOPE | ✓ | ✓ | ✓ | `action.tool` ∈ `grant.scope.tools`; owner protocol P-CN1/v1 khớp `owner_protocols` (operation, vùng, nền tảng); **mọi pha:** task roundtrip qua owner — `build_task(request_from_task(task), rid)` (hàm thuần, chạy qua `observer.rebuild_task`, không gọi hàm ghi) cho cùng digest intent/context/accepted_task/action theo comparator C1 sẵn có, lệch hoặc owner từ chối ⇒ `UNSUPPORTED` + `TASK_NOT_OWNER_REPRESENTABLE`, owner không nạp được ⇒ `NOT_CHECKED` (limit `OWNER_BUILD_TASK_ROUNDTRIP_C1_PROJECTION`); d e: `entrypoint_sha256` của owner hiện tại do observer đo = pin; a: `prepared.entrypoint_sha256` lịch sử = pin (hash script hiện tại không thay pin lịch sử). Pin là so version/bytes hợp tác, không chứng minh process |
| ENVELOPE | ✓ | ✓ | ✓ | `task.envelope.role` = vai chủ thể; so số học `max_retries`/`max_concurrency` (giá trị khai `REQUESTED`/`APPLIED`, số nguyên) với `grant.limits`; `cost_limit` chỉ MET khi chuỗi bằng nhau; không có giới hạn áp dụng thì không vượt (sau khi đã kiểm). Thiếu/`UNKNOWN`/`UNSUPPORTED`/đơn vị không so được ⇒ U ⇒ `NOT_CHECKED` (`ENVELOPE_UNMEASURED`); `limits.expires_at`, `envelope.expires_at` hoặc `profile_ref` chưa giải ⇒ `UNSUPPORTED` và U. Giá trị DECLARED (limits `ENVELOPE_DECLARED_NOT_HOST_OBSERVED`), không phải host đã áp dụng |
| BINDING | – | ✓ | ✓ | đúng một effect `REQUEST` (e) / `OUTCOME` (a) và, ở a, đúng một `result`; mọi quan hệ bắt buộc của `compare_binding` là `MATCH` (tính lại, không phải echo ngang hàng); `REQUEST` không có `outputs`; routing tự khai của effect khớp route đã tính. Thiếu record ⇒ `NOT_CHECKED`; lệch ⇒ `NOT_MET` + `BINDING_MISMATCH`; trùng ⇒ `DUPLICATE_*` |
| INPUT_REVISION | – | ✓ | ✓ | e và a: bytes input không-target hiện tại do observer băm = digest `task.inputs` (đổi ⇒ `NOT_MET` + `INPUT_CHANGED_SINCE_READ`; không đọc được ⇒ `NOT_CHECKED`); a còn đòi `prepared.inputs_observed_at_publish` = `task.inputs`. Lịch sử không thay quan sát hiện tại; input trùng target ngoài luồng hẹp |
| ACTUAL_OUTCOME | – | – | ✓ | effect OUTCOME `APPLIED` có `receipt_ref` loại `effect_receipt`, locator = đường published cố định của rid, digest = SHA-256 **raw bytes** published, `TOOL_OBSERVATION`/`TOOL_OUTPUT`; `outcome.artifacts`, `binding.outputs` (cả effect và result) và `result.artifacts` bằng EXACT `[{target, published.content.sha256}]`; `result.actions_performed` = action của task; **bytes đích hiện tại** (observer) = nội dung published và cùng identity file với published (lệch ⇒ `CHANGED_AFTER_PUBLISH`); thiếu/hỏng/nhiều evidence ⇒ `NOT_CHECKED` + `PRECONDITION_PROOF_MISSING`. Hash đích trùng không thay lineage |
| REQUIREMENTS | – | – | ✓ | `USER_ACCEPTED_DECLARED` khi D4 đủ (dưới). Thiếu `user_acceptance` ⇒ `NOT_CHECKED` (EVIDENCE_NOT_VERIFIED); thiếu một phần ⇒ `NOT_CHECKED` + `USER_ACCEPTANCE_INCOMPLETE`; gắn task/artifact/result khác ⇒ `NOT_MET` + `USER_ACCEPTANCE_STALE`; claim `ACCEPTED_FOR_INTEGRATION` ⇒ `ACCEPTANCE_CLAIM_NOT_SUPPORTED`. Luôn `requirements_semantic_verified=false` |

PRESERVATION không liệt kê ở R-READ_DRAFT; known-loss vẫn DENY từ route, `UNKNOWN` vẫn `PRESERVATION_UNKNOWN`. Mỗi gate có `gate`, `due_in`, `status`, `evidence {required, provided}` (D = khai báo, C = nhất quán chéo record, R = tính lại, O = quan sát), `limits`, `reasons`, `owner_of_proof`; `PATH_SCOPE` thêm `subchecks`.

**D4 (`result.user_acceptance`).** Đủ khi: `ref` là `USER_CONFIRMATION` kênh `USER_MESSAGE`/`HOST_CONFIRMATION_UI` có `evidence_locator`; `task_id`/`task_revision` = task; `accepted_task_digest` = digest `task` tính lại; `result_id` = result; `accepted_requirements` ⊇ mọi `req_id` mandatory (thiếu ⇒ INCOMPLETE; id lạ ⇒ STALE); `accepted_artifacts` EXACT = `result.artifacts` = `[{target, digest published}]` (so bằng `compare_object_sets`, quan hệ `D4-ARTIFACTS`); `presented_summary` đủ hình (schema). Mandatory requirement mà `result.requirements` ghi `NOT_MET`/`MISSING`/`BLOCKED` ⇒ `MANDATORY_REQUIREMENT_NOT_MET`. Im lặng, grant, receipt, "ok" không nêu bản: không đủ. Không `semantic_verified`.

**Routing nối gate.** `routing.evaluate_task(task, policy, phase, external=...)`: `external['envelope_exceeded']` ∈ T/F/U do gate ENVELOPE tính (không có ⇒ U như cũ) và `external['closed_assumptions']` chỉ gồm `A-NEW_TARGET` khi observer thấy đích vắng **trong lần kiểm này** ở dispatch/effect. Tính lại hợp nghĩa vụ; không gán F mặc định. Giả định đóng ghi `status: CLOSED_BY_OBSERVATION` kèm `limits`; không đóng ⇒ `CONDITIONAL` ⇒ BLOCKED như cũ. Route phải chỉ gồm R-READ_DRAFT (T) và `review_phases` rỗng, nếu không `ROUTE_NOT_P_CN1_LIGHT` (BLOCKED).

**PASS.** Shape hỗ trợ ∧ route `RESOLVED` ∧ không lý do DENY/UNSUPPORTED/BLOCKED ∧ mọi gate đến hạn ∈ {MET, USER_ACCEPTED_DECLARED, NOT_REQUIRED}. `assurance_level=ADVISORY`, exit 0, `effect_authorized=false`; PASS một pha không mở pha khác. Ví dụ frozen `EXAMPLE_INACTIVE` không bao giờ PASS. `aggregate.records_checked_state`: `INCONSISTENT` nếu có gate `NOT_MET` hoặc lý do DENY/mismatch/duplicate, ngược lại `CONSISTENT_IN_CHECKED_SCOPE`; bộ đếm tính từ `gates`; `open_assumptions` là các giả định route còn OPEN.

**Pin và code đã nạp (sửa tại review).** Observer so raw bytes source LAW với pin trong policy bytes cố định trước khi thực thi, nạp đúng bytes đó và kiểm lại pin trước dùng cache. Dependency `transaction`/`result_schema` trùng tên từ nơi khác trong host bị từ chối; `sys.path` được khôi phục nguyên trạng. Đây là kiểm nhất quán COOPERATIVE/ADVISORY, không attestation hoặc chống sửa process.

**Coverage khi có root.** `gates_evaluated` (shape hỗ trợ và gate tính được), `target_existence_observed` (observer trả thông tin đích), `artifact_bytes_observed` (observer băm bytes input/đích trong lần này) bật theo quan sát thật; `actual_operation_observed=false`, `requirements_semantic_verified=false`, `owner_protection=NOT_PROVEN`. `phase_scope` = `STRUCTURE` + token `BINDING`/`ROUTING`/`GATES`/`OBSERVER` đã chạy.

**Giới hạn đã biết.** Chỉ Windows NTFS local; `tamper_resistance=NONE` (ai ghi được `.agent/runtime/` đều sửa được evidence); quan sát đích-vắng/bytes là tại thời điểm, không chứng minh ghi độc quyền hay loại race; pin là so hợp tác; không review nào được hỗ trợ trong luồng này; ENVELOPE là DECLARED; `task_classes` chưa có classifier; chưa chạy CI, Python 3.8/3.13 thật, POSIX/mạng/cloud/FAT.

## Ngoài phạm vi (không suy ra đã có)

Ngoài luồng P-CN1 một file ở trên: gate cho shape khác (overwrite, nhiều action/grant/task, recipe, delegation, vai không-core), PRESERVATION như gate, kiểm pin tại runtime của host, review verdict và pha review, delegation pointers, overlay, pathing/zones ngoài bảng policy, CI, Python 3.8/3.13 thật, integration, activation, migration, dọn mã v2, G-04.
