# Checker v2 (candidate) — G-02-C2/S1 FOUNDATION_ONLY + S2 helper refs/binding (chưa nối entry)

Trạng thái review: **REVIEW_ACCEPTED_FOUNDATION_ONLY** (18/10/2026), sau hai sửa hẹp Main theo review Sol6.1 High.
Vòng đời vẫn **CANDIDATE_NOT_ACTIVE**, giai đoạn **S1_FOUNDATION_ONLY** của entry/API/output; nhận S1 không mở S2–S5.
**S2 (18/10/2026, IMPLEMENTED_PENDING_REVIEW)** chỉ thêm hai module thư viện trong bộ nhớ `refs.py`, `binding.py` và refactor hẹp `loader.py` (mục "Helper S2" bên dưới). Entry/API/output/screen S1 **không đổi** và **không** gọi S2; `binding_evaluated` của output S1 vẫn `false`.
Đây không phải checker đầy đủ: S1 chỉ có nền entrypoint, loader strict, canonicalization và router CLI v1.
Không có evaluator binding/route/gate/guard nguồn nào; kết quả hợp lệ về cấu trúc **luôn BLOCKED**. Không PASS, không quyền, không chống giả.
Checker v1 (`../control_check.py`) giữ nguyên và không đọc cây này. Chưa có activation, profile, template, writer hay integration nào gọi entry v2.

## Cây package

| File | Vai trò S1 | Ghi chú |
|---|---|---|
| `../control_check_v2.py` | entry CLI/API, router `--contract`, bootstrap package, dựng output | chỉ nạp package v2 khi `--contract v2`/API |
| `__init__.py` | hằng literal (version, basis, `$id`, policy status, giới hạn) | không logic |
| `loader.py` | đọc bundle và hai owner cố định, parse strict, preflight version/basis/binding literal, validate Draft 2020-12 | chỉ đọc |
| `canon.py` | LAW-CJ/2, projection, digest theo C1 | không import từ `tests/` |
| `refs.py` (S2) | index record, nhóm lời khai inline, liên kết grant, kiểu kết quả chung | thuần, không I/O |
| `binding.py` (S2) | `PolicyContext`, kernel projection theo phần, comparator binding/set/pointer | thuần, không I/O |
| `README.md` | tài liệu này | |

Chưa tạo (thuộc lát sau, không mở trong S2): `pathing.py`, `route.py`, `gates.py`, `delegation.py`, `observe.py`, `engine.py`.
Owner canonical đọc cố định theo vị trí của package: `../../contracts/v2/control.schema.json` và `../../rules/v2/ROUTING_POLICY.json`.
Hash byte đã nạp chỉ để ghi nhận: `owner_protection = NOT_PROVEN`; tên file đúng không chống sửa.

## Entrypoint

```text
python -I <tuyệt đối>/control_check_v2.py --contract {v1,v2} --phase {dispatch,effect,accept} [--format json|text] bundle.json
```

- `--contract` bắt buộc, không mặc định, không suy từ record, không auto-discover, không fallback. Thiếu/lạ/trùng/thiếu giá trị: lỗi của wrapper, stderr, exit 2, stdout trống.
- Không có `--root`, `--basis`, `--trust`, `--schema`, `--policy`. Không có observer: nguồn dữ liệu được đánh giá chỉ gồm bundle và hai owner. Runtime còn nạp code/dependency, đọc METADATA của jsonschema; Python có thể tạo pycache khi không dùng `-B`. Những việc đó không là đọc artifact/locator hoặc quan sát thao tác của user.
- `--contract v1`: chỉ tách cờ `--contract`, chuyển phần còn lại **nguyên văn** tới `main()` của `control_check.py` v1 (đặt `sys.argv`/`prog` như chạy trực tiếp, khôi phục sau gọi). Không parse bundle, không áp basis/số học v2, không import package v2, không bọc stdout/stderr. Stdout/stderr/exit phải giống chạy trực tiếp. V1 chặn thì vẫn chặn, không thử lại v2.
- `--contract v2`: argparse riêng (`prog=control_check_v2.py`); lỗi cú pháp/tùy chọn = stderr argparse, exit 2.
- API: `check_bytes(data, phase, contract)`. `data` phải là `bytes` (khác: `TypeError`); `contract` chỉ `"v2"` và `phase` ∈ `dispatch/effect/accept` (khác: `ValueError`). Không `check_records`, không tiêm schema/policy/verifier. Tương thích v1 chỉ ở CLI. Chọn contract tường minh chỉ là diagnostic candidate, không phải profile activation hay quyền.

## Hợp đồng output S1 (`law.cvf.check/2`, JSON object)

Đúng các trường sau, theo thứ tự này, không trường ngầm nào về verified/permit:

| Trường | Giá trị |
|---|---|
| `check_version` | `"law.cvf.check/2"` |
| `contract` | `"v2"` |
| `selection` | `"CLI_EXPLICIT"` (CLI) hoặc `"API_EXPLICIT"` (API) |
| `candidate_status` | `"CANDIDATE_NOT_ACTIVE"` |
| `implementation_stage` | `"S1_FOUNDATION_ONLY"` |
| `evaluation_basis` | `"COOPERATIVE_WORKFLOW"` chỉ sau khi basis đã validate; còn lại `null` |
| `phase` | pha được yêu cầu |
| `disposition` | `BLOCKED` / `DENY` / `UNSUPPORTED` (không bao giờ `PASS` hoặc `NOT_APPLICABLE` trong S1) |
| `effect_authorized` | `false` |
| `assurance_level` | `"UNVERIFIED"` |
| `init_error` | boolean |
| `reasons` | mảng mã duy nhất, đã sắp |
| `details` | mảng chuỗi chẩn đoán; không chép payload/secret (không giá trị trường, không tên khóa trùng) |
| `owners` | `{schema_sha256, policy_sha256}`: hex SHA-256 của byte thực đã nạp, hoặc `null` |
| `coverage` | `record_structure_checked` (boolean: `true` chỉ khi mọi kiểm cấu trúc S1 đều đạt — literal, schema, miền canonical; mọi từ chối là `false`; `false` không có nghĩa chưa thử kiểm), `binding_evaluated=false`, `routing_evaluated=false`, `gates_evaluated=false`, `artifact_bytes_observed=false`, `actual_operation_observed=false`, `requirements_semantic_verified=false`, `owner_protection="NOT_PROVEN"` |
| `objects` | `[]` |
| `gates` | `[]` |

Disposition và exit (CLI):

| Tình huống | Disposition | Reasons (S1) | Exit |
|---|---|---|---|
| cấu trúc và policy hợp lệ, chưa có evaluator | `BLOCKED` | `CANDIDATE_EVALUATION_NOT_IMPLEMENTED` | 1 |
| input hỏng: không phải JSON/UTF-8/object, khóa trùng, nonfinite, quá 8 MiB | `DENY` | `INPUT_MALFORMED` | 1 |
| literal đúng nhưng sai cấu trúc schema; `routing_policy` trong input | `DENY` | `SCHEMA_INVALID` | 1 |
| version/basis/binding literal thiếu, lạ hoặc trộn | `UNSUPPORTED` | `VERSION_MISSING`, `SCHEMA_VERSION_UNKNOWN`, `VERSION_MIXED`, `BASIS_MISSING`, `BASIS_UNKNOWN`, `BASIS_MIXED`, `BASIS_MISMATCH`, `BINDING_VERSION_UNKNOWN` | 1 |
| số thập phân/ngoài ±(2^53−1), chuỗi không NFC hoặc surrogate đơn, khóa sai mẫu: ngoài miền LAW-CJ/2 | `UNSUPPORTED` | `UNSUPPORTED_BINDING_PART` | 1 |
| lỗi khởi tạo: thiếu/quá cũ `jsonschema` (< 4.18), owner không đọc/parse/validate được hoặc sai literal, không đọc được bundle | `UNSUPPORTED`, `init_error=true` | `DEPENDENCY_MISSING`, `PACKAGE_UNAVAILABLE`, `OWNER_UNREADABLE`, `OWNER_INVALID`, `SCHEMA_VERSION_UNKNOWN`, `POLICY_VERSION_UNKNOWN`, `BUNDLE_UNREADABLE` | 2 |
| lỗi cú pháp/tùy chọn CLI | stderr argparse, không có JSON | — | 2 |

Thứ tự kiểm: owner/dependency → parse strict → version → basis → literal của binding → schema (Draft 2020-12 thật) → miền canonical → (S1 dừng, BLOCKED).
Version/basis/binding literal sai là `UNSUPPORTED` (từ chối, không diễn giải, không migrate); sai cấu trúc còn lại là `DENY`.
Bundle ở `law.cvf.control/1` hợp lệ không được thử ở v2: `details` gợi ý chọn `--contract v1` tường minh.
`--format text` cho cùng disposition/exit/giới hạn; chỉ khác cách trình bày.

## Các quyết định chỉ áp dụng cho S1

- Quét miền LAW-CJ/2 trên **toàn bundle** là screening bảo thủ tạm thời của S1, không là định nghĩa hợp lệ C1. Nó có thể từ chối metadata bị loại khỏi projection nhưng vẫn hợp lệ theo C1. Kiểm schema/literal trước đó vẫn có thể trả DENY trước khi tới screening. Trước S2/S3 phải chốt và review phạm vi projection-aware; không tự giữ restriction này thành contract mới hoặc tự nới để lấy PASS.
- Mã lý do thuộc output checker, không sửa enum effect C1 hay routing. `VERSION_MIXED` là có ít nhất hai giá trị version hiện diện khác nhau; thiếu version báo riêng. `BASIS_MIXED` xét các giá trị hiện diện ở record và binding; `BASIS_MISMATCH` là basis của một binding khác basis record chứa nó. Một lỗi có thể đồng thời có MISSING/UNKNOWN/MIXED/MISMATCH, không suy các mã này là độc quyền hoặc là kiểm nguồn tin.
- Loader đọc lại bytes owner và tính hash trước khi dùng cache; cache key là hash schema, hash policy và phiên bản dependency major/minor. Cache validator/mutable owner chỉ là chi tiết embedding trong tiến trình, không là khóa chống sửa hoặc quyền. Nguồn owner vẫn cố định tại entry; không public owner override qua API.
- BOM UTF-8 đầu input được chấp nhận ở tầng vận chuyển JSON, không đổi LAW-CJ/2 xuất bytes không BOM hoặc digest byte file nguyên văn. `ensure_ascii=True` chỉ là cách xuất JSON kết quả v2; không là canonicalization của binding, không đổi nhánh v1.
- Schema được quét các reference keywords `$ref`, `$dynamicRef`, `$recursiveRef` để từ chối URI không-local. Validator còn dùng registry từ chối retrieval rõ ràng, không dựa vào resolver mặc định; reference không giải được không được tải qua mạng hoặc file ngoài. Details chỉ ghi index record, không echo `record_type` do input khai; regex cho đường chẩn đoán kiểm toàn chuỗi.

## Helper S2: refs/binding trong bộ nhớ (hợp đồng, viết trước code)

Thư viện hàm thuần; **không** nối vào entry/API/output S1. Mọi trạng thái chỉ mô tả *so sánh/tính lại*; không có PASS/MET/permit/receipt/stale/eligible/allowed. Mọi `Relation`, `ClaimGroup`, `GrantLink` và `BindingReport` mang hằng `bytes_observed=false`, `authenticity_observed=false`, `semantic_verified=false` trong `as_dict()`. Digest TÍNH MỚI từ record đã resolve được trả ở `Part`/`PolicyContext`; digest khai báo trong input không bao giờ được chép lại như bằng chứng.

**Tiền điều kiện (người gọi bảo đảm):** `loader.parse_and_preflight(data, owners)` trả `bundle` khác `None`, rồi `loader.validate_structure(bundle, owners)` trả `ok=True`, rồi `refs.records_of(bundle)`. Helper **không** gọi `inspect_bundle` và không dùng screen miền canonical toàn bundle của S1; schema-valid không có nghĩa canonical-supported. Miền canonical chỉ được xét *trong đúng phần được băm*, từng phần độc lập. Helper không tự nạp owner/file/mạng; policy đi vào bằng `Owners.policy_bytes` (bytes bất biến, snapshot lúc đọc), không bằng `owners.policy` dùng chung từ cache.

**Loader (refactor giữ nguyên hành vi S1):**
- `Owners.policy_bytes`: `bytes` đúng bytes đã hash `policy_sha256`.
- `parse_and_preflight(data, owners) -> (bundle|None, Outcome)`: strict parse → version → basis → literal binding, đúng thứ tự/lý do/details như S1. `bundle=None` khi từ chối; `Outcome.record_structure_checked` luôn `False` ở đây; `Outcome.evaluation_basis` đặt khi basis hợp lệ.
- `validate_structure(bundle, owners) -> (ok: bool, reasons: tuple, details: tuple)`: `details` luôn bắt đầu bằng `owners.notes`, rồi (nếu lỗi) dòng schema/`routing_policy`; `ok=False` ứng với DENY (`SCHEMA_INVALID` hoặc `INPUT_MALFORMED` do lồng quá sâu). `inspect_bundle` gọi hai hàm này rồi chạy screen cũ; output/thứ tự/coverage S1 không đổi.

**Kiểu trả về** (dataclass `frozen`, chỉ `str/int/bool/None/tuple`, mọi kiểu có `as_dict()` JSON-safe; không chia sẻ container mutable với đầu vào, primitive bất biến có thể chia sẻ; không echo id, path, digest thô, tên khóa; diagnostics chỉ là vị trí nguồn, locator đóng, tên trường đóng, reason đóng, số đếm):

| Kiểu | Trường |
|---|---|
| `Relation` | `name`, `state` ∈ `MATCH MISMATCH ONE_SIDED INCOMPLETE AMBIGUOUS UNSUPPORTED NOT_BOUND NOT_APPLICABLE`, `basis` ∈ `RECOMPUTED PEER_CLAIM LITERAL DECLARED_SET`, `locator`, `reason` (đóng hoặc `None`), `fields` (tên trường lệch), `indexes` (chỉ số action khớp), `counts` (cặp tên/số), `limitations` |
| `Lookup` | `record_type`, `status` ∈ `FOUND MISSING AMBIGUOUS`, `positions` (thứ tự nguồn) |
| `Occurrence` | `position`, `locator`, `role`, `group_no` |
| `ClaimGroup` | `group_no`, `status` ∈ `AGREE CONFLICT`, `occurrences`, `kind` (chỉ khi AGREE và thuộc enum đóng), `conflict_fields`, `metadata_differs`, `locators`, `resolution="INLINE_CLAIM_ONLY"` |
| `GrantLink` | `source_locator`, `source_role` ∈ `task_grant_ref effect_grant_ref_id`, `state` ∈ `LINKED NO_GRANT_RECORD AMBIGUOUS CONFLICT INCOMPLETE UNSUPPORTED`, `reasons`, `candidate_positions` (mọi ứng viên), `claim_status`, `claim_conflict_fields`, `kind_is_grant`, `in_task_grant_refs`, `link_is_authority=false` |
| `Part` / `TaskDigests` | `Part(state COMPUTED/UNSUPPORTED, digest, reason)`; `TaskDigests(intent, accepted_task, context, actions, actions_malformed)` |
| `PolicyContext` | `state` ∈ `COMPUTED UNSUPPORTED`, `digest`, `literals_ok`, `reason` |
| `BindingReport` | `position`, `applicable`, `relations`, `recomputation_complete` |

**Hàm** (đối số sai kiểu container ⇒ `TypeError`; position ngoài khoảng, `mode`/`record_type` lạ, metadata API sai hoặc claims khác index ⇒ `ValueError`; nội dung lệch dạng trả `UNSUPPORTED`/`MALFORMED_RECORD`/`INCOMPLETE`, ngoại trừ depth>64 ngoài tiền điều kiện schema-valid của build_index ⇒ `ValueError`):
- `refs.records_of(bundle) -> list`: `bundle["records"]` nếu `record_type == "bundle"`, ngược lại `[bundle]`. Position = thứ tự nguồn (một record đơn = 0), không sắp lại.
- `refs.build_index(records) -> RecordIndex`: snapshot riêng (deep-copy container); `lookup(record_type, *key)`, `collisions()`, `positions_of(record_type)`, `malformed_positions`, `count`, `as_dict()` (chỉ số đếm/vị trí). Khóa có kiểu, không ép: task `(task_id, task_revision)` (revision integer, `True`≠1, `"1"`≠1); grant `(grant_id, grant_revision)` hoặc `(grant_id,)` trả mọi revision; review `review_id`; effect `effect_id`; result `result_id`. Mỗi loại một namespace. Trùng khóa ⇒ `AMBIGUOUS`, không chọn bản đầu/mới nhất, kể cả `work_id` khác.
- `refs.collect_claims(index) -> ClaimTable`: tám vị trí inline (intent ref, grant ref, `issuer_ref`, recipe acceptance, identity ref, eligibility ref, receipt ref, user acceptance ref). Nhóm theo `ref_id` toàn bundle. Lặp giống nhau = occurrence hợp lệ (AGREE). Khác ở `kind`, `locator`, `revision` (có/không và giá trị), `digest`, `issuer` (mọi trường actor), `source_class`, `channel`, `evidence_locator` (có/không), `observed_by` (mọi trường actor) ⇒ CONFLICT. `recorded_by`, `note` chỉ là `metadata_differs`. Vắng ≠ null; so chuỗi nguyên văn theo kiểu JSON. AGREE không chứng minh nguồn hay quyền; không có record nguồn nào được bịa ra.
- `refs.link_grants(index, claims, position) -> tuple[GrantLink]`: task ⇒ `authority.grant_refs`; effect ⇒ `grant_ref_ids` (là `ref_id`, không phải `grant_id`) và so thành viên với `authority.grant_refs` của task resolve từ `binding` của chính effect; record khác hoặc không có ref ⇒ `()`. Ứng viên = record grant có `issuer_ref.ref_id` bằng ref_id (không bao giờ so với `grant_id`). Ưu tiên trạng thái chính: `UNSUPPORTED` (malformed) > `CONFLICT` (nhóm CONFLICT, kind không phải `grant`, hoặc effect ref ngoài task refs) > `AMBIGUOUS` (≥2 ứng viên, hoặc task của effect AMBIGUOUS) > `NO_GRANT_RECORD` (0 ứng viên) > `INCOMPLETE` (effect không resolve được task) > `LINKED` (đúng 1 ứng viên, AGREE, kind `grant`, thuộc task refs). Mọi lý do áp dụng đều nằm trong `reasons`; không trả `LINKED` kèm cờ phụ. Liên kết chỉ nối hai lời khai (`link_is_authority=false`); không kiểm ACTIVE/subject/scope/tool/path/thời gian.
- `binding.make_policy_context(policy_bytes: bytes) -> PolicyContext`: parse riêng bằng parser strict, kiểm literal (`policy_version`, `schema_version`, `evaluation_basis`, `status`), tính `policy_part`. Bytes sai kiểu ⇒ `TypeError`.
- `binding.recompute_task(task: dict) -> TaskDigests`: gọi đúng `intent_part`, `context_part`, `task_part`, từng `action_part`; `Unsupported` của phần nào chỉ làm phần đó `UNSUPPORTED`. Không canonicalize metadata ngoài projection.
- `binding.compare_binding(index, position, policy_ctx) -> BindingReport`. Quan hệ (tên, basis): `B-REF` (task tra đúng khóa; `MATCH`=tìm thấy đúng 1) · `B-LIT.bind_version/evaluation_basis/policy_version` (LITERAL) · `B-INTENT`, `B-TASK`, `B-CONTEXT`, `B-POLICY` (RECOMPUTED) · `B-INPUTS` (DECLARED_SET, `EXACT_QUALIFIED` với `task.inputs`) · review/result có `action_digest`: `B-ACTION-CLAIM` (các chỉ số action cùng digest; một action_digest không phủ toàn result) · effect: `B-ACTION-OWN` (digest `effect.action` tính lại vs `action_digest`) và `B-ACTION-IN-TASK` (chỉ số action của task có cùng projection) · result: `B-OUT-RESULT` (`outputs` vs `artifacts`, `EXACT_QUALIFIED`) · review/effect: `B-OUTPUTS` (`NOT_BOUND` nếu vắng, ngược lại `NOT_APPLICABLE`: không có đối ứng để tính lại, không suy `outputs` từ `artifacts`). Trường tùy chọn (`outputs`, `action_digest`) vắng ⇒ `NOT_BOUND`; hiện diện ⇒ phải so đầy đủ. Task không tra được ⇒ `INCOMPLETE`, trùng khóa ⇒ `AMBIGUOUS` cho mọi quan hệ phụ thuộc. Record không có `binding` ⇒ `applicable=false`.
- `recomputation_complete`: `true` chỉ khi tập quan hệ cần thiết — `B-REF`, `B-INTENT`, `B-TASK`, `B-CONTEXT`, `B-POLICY`, `B-INPUTS` cùng mọi quan hệ tùy chọn đang hiện diện — **không rỗng** và **mọi** quan hệ trong đó có trạng thái `MATCH` hoặc `MISMATCH` (đã tính đủ). Còn `INCOMPLETE/AMBIGUOUS/UNSUPPORTED` ⇒ `false`. `MISMATCH` trên digest đã tính đủ vẫn cho `true`: nó nghĩa là "tính xong", không phải nhất quán, PASS hay đã quan sát byte. Hai bản echo hash của peer không bao giờ làm nó `true`.
- `binding.compare_peer_bindings(a: dict, b: dict) -> tuple[Relation]`: theo từng trường binding (`PEER_CLAIM`): cả hai vắng `NOT_BOUND`, một phía `ONE_SIDED`, cả hai có `MATCH`/`MISMATCH` (`inputs`/`outputs` qua `EXACT_QUALIFIED`). Không bao giờ cộng vào `recomputation_complete`.
- `binding.compare_object_sets(left, right, mode, name="object_sets") -> Relation` (`mode` ∈ `EXACT_QUALIFIED`, `COVER_REQUIRED_QUALIFIERS`): khóa phần tử = bytes canonical của `obj_proj` (path, digest, `source_id`, `revision`, `scope` có-mặt-đúng); trùng phần tử ⇒ `UNSUPPORTED DUPLICATE_SET_ELEMENT`, không dedupe; phần tử ngoài miền ⇒ `UNSUPPORTED` kèm reason; `COVER`: path+digest bắt buộc, qualifier đã khai phải khớp, hai chiều phủ đủ. Mọi quan hệ tập mang `limitations=("UNVERIFIED_RAW_BYTES",)`: digest object nghĩa là byte file thô chưa quan sát; không có kiểu "task-projection scope" nào được định nghĩa hay thử.
- `binding.compare_pointers(index, position, policy_ctx) -> tuple[Relation]`: cho từng action `delegate` của task hoặc effect: `P-RESOLVE`, `P-TASK-DIGEST`, `P-CONTEXT-DIGEST`, `P-SELF` (pointer cha so với **task chứa action** ⇒ `MATCH`/`MISMATCH`, không trung tính; với effect, task chứa = task theo `binding` của effect), `P-EFFECT` (chỉ effect; PEER_CLAIM), `C-RESOLVE`, `C-TASK-DIGEST`, `C-CONTEXT-DIGEST`, `C-BASIS` (PEER_CLAIM; không record nào bind task con ⇒ `INCOMPLETE`), `C-INPUTS`. Thiếu task con ⇒ `INCOMPLETE` (không MISMATCH); cha, effect, con là các quan hệ độc lập. Record khác ⇒ `()`.

**Không có trong S2:** route, gate, acceptance, review/eligibility verdict, ACTIVE/subject/scope grant, đủ/thiếu bắt buộc của `outputs`/`action_digest` theo pha, thời gian, đọc artifact/locator, quan sát byte/nguồn/ngữ cảnh vai, bất kỳ thay đổi entry/`__init__`/`canon`/owner C1/v1.

## Review S2 helper-only — 18/10/2026

**REVIEW_ACCEPTED_HELPER_ONLY**, lifecycle vẫn CANDIDATE_NOT_ACTIVE. Reviewer Sol6.1 High nhận sau sửa hẹp Main; entry/API/output S1 không tích hợp helper, `binding_evaluated=false`. Worker157test là snapshot bàn giao; Main56test mục tiêu đạt sau sửa, không rerun toàn157.

- `ClaimTable` gắn private token của `RecordIndex` tạo nó. `link_grants` chỉ nhận claims cùng snapshot index; ghép khác index (kể cả nội dung trông giống) là lỗi caller ValueError. Token không là verifier hoặc quyền; không có trong `as_dict()`.
- Thứ tự grant-link UNSUPPORTED > CONFLICT > AMBIGUOUS > NO_GRANT_RECORD > INCOMPLETE > LINKED chỉ chọn chẩn đoán chính; giữ mọi reason xác định được, không thay policy hoặc quyết gate S3. `LINKED` vẫn không là authority.
- `recomputation_complete` gồm tập bắt buộc đã liệt kê (có B-INPUTS) và optional hiện diện, không gồm B-LIT. Nó nói các phép tính/so cần thiết đã hoàn tất; phải đọc từng relation để biết mismatch/literal lỗi, không dùng bool này làm đủ gate hay nhất quán.
- `build_index` nhận records đã qua strict parse/literal/schema; depth>64 có ValueError là giới hạn phòng thủ ngoài tiền điều kiện, không phải kết quả schema checker hoặc rule C1 mới. Container đầu vào được deep-copy; primitive bất biến có thể chia sẻ.
- Chữ ký đầy đủ: `compare_object_sets(left, right, mode, name="object_sets", locator="", basis="DECLARED_SET")`. Basis chỉ DECLARED_SET hoặc PEER_CLAIM; không được gắn RECOMPUTED/LITERAL cho tập khai báo. Name chỉ object_sets, scope, B-INPUTS, B-OUT-RESULT, C-INPUTS, peer.inputs, peer.outputs; locator phải dùng source-position/field vocabulary đóng, không newline hoặc label tùy ý. Sai metadata API là TypeError/ValueError, không echo giá trị lỗi.
- COVER_REQUIRED_QUALIFIERS bất đối xứng: **trái=summary, phải=artifact**. Path+digest phải khớp và phủ đủ hai tập; qualifier summary khai phải khớp artifact, qualifier chỉ ở artifact có thể vắng trong summary. Đảo hai phía có thể đổi kết quả. EXACT_QUALIFIED vẫn so cả presence/value qualifier; chưa có quyết định coverage/review pha S3.
- `compare_object_sets(None, None)` standalone vẫn biểu diễn hai phía vắng; khi field inputs/outputs có mặt trong record nhưng null thì wrapper peer/binding báo UNSUPPORTED/MALFORMED_RECORD, không NOT_BOUND. Schema tiền điều kiện vẫn là lớp kiểm đầu tiên.
- Import binding→loader chỉ tái dùng parser/InputError trong bộ nhớ; không gọi load_owners hoặc mở file. Nạp code/dependency khi import là runtime như S1, không là observer nguồn.
- refs/binding vượt ước tính dòng ban đầu là nợ maintainability, chưa có bằng chứng cần tách cơ học; không thêm gate/engine vào hai module này trong S3. Không claim Python3.8 thật/CI/khácOS hoặc S2 helper đã tích hợp.

## Ngoài phạm vi entry S1 (không suy ra đã có)

Tính lại binding và guard nguồn hiện hành, route, gate, delegation, review, observer/`--root`, định nghĩa vùng nhẹ/nặng, recipe, ánh xạ vai không-core, nghĩa của REQUIREMENTS/SOURCE_SCOPE, output gate/aggregate đầy đủ (phải review trước S3), CI, Python 3.8 thật, integration, activation, migration.
Hàm canon trong `canon.py` chỉ phục vụ kiểm vector và nền cho lát sau; entry S1 không dùng chúng để đánh giá binding của bundle.
