# Evidence — luồng P-CN1 một file (gate + observer + receipt + D4), IMPLEMENTED_PENDING_REVIEW

Worker Claude, 18/10/2026. Model quan sát được: `claude-sonnet-5-5` (VS Code extension); effort không quan sát được. Không agent phụ, không AI CLI/API, không host/global/admin, không stage/commit/push. Python 3.11.9, jsonschema 4.23.0, Windows 11 NTFS local (thư mục tạm). Python 3.13 có trên máy nhưng không có jsonschema nên **chưa chạy**; Python 3.8 chỉ kiểm cú pháp bằng `ast.parse(feature_version=(3, 8))`.

## File trong thư mục này

| File | Nội dung |
|---|---|
| `workflow_tests_py311.log` | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_v3_workflow` → 58 test, OK, 0 skip |
| `regression_v3_py311.log` | cùng cờ, `tests.test_control_check_v3 tests.test_control_v3_routing tests.test_control_v3_canonical_screening tests.test_control_v3_candidate` → 189 test, OK (trước lượt này cũng 189 test, OK) |
| `mutation_probe.py`, `mutation_probe.log` | 16 đột biến sản phẩm trên **bản sao** (không chạm repo); cả 16 làm ít nhất một test workflow đỏ |

## Hash (sha256, 16 ký tự đầu; trước → sau)

| File | Trước | Sau |
|---|---|---|
| `.cvf/checks/control_check_v3.py` | `7d67c3b8c76d9415` | `e4bcbf35faa3392d` |
| `.cvf/checks/v3/routing.py` | `c8b972e6a18440b6` | `37845b6bc357ad24` |
| `.cvf/checks/v3/canon.py` | `305fe127a290b40c` | `7ab1bf8e6b94e2b0` |
| `.cvf/checks/v3/binding.py` | `2551d3f573669747` | `f227eda4a8f73e5e` |
| `.cvf/checks/v3/observer.py` | mới | `33651946d7a04672` |
| `.cvf/checks/v3/workflow.py` | mới | `99da26befb06a239` |
| `.cvf/checks/v3/README.md` | `69d38a3f1ee2fe7d` | `7409ed33ffc5d9fb` |
| `.cvf/contracts/v3/CONTROL_CONTRACT.md` | `f521f8b2c047c929` | `50b2c598d1dd8496` |
| `tests/test_control_v3_workflow.py` | mới | `8a173114299e6e97` |
| `tests/test_control_v3_canonical_screening.py` | `5b2fd8a415c0f839` | `db46b3b5f25a24b9` |
| `tests/test_control_check_v3.py` | `3695412e254c74a6` | `e18cac2629d450c9` |

Không đổi (đã đối chiếu): `loader.py` `0a50424e8e767ce8`, `refs.py` `33761fd35bd6b8f6`, `tests/test_control_v3_routing.py` `3ef02b58f8b6d43f`, schema `12becc373df364bd`, policy `8c63bd03bbcdb733`, vectors `3846b50d652ae097`, 22 ví dụ `f53accb85fcd4ec8`, writer `tools/publish_new.py` `f2b1b425690eacd5` (SHA256 đầy đủ `f2b1b425690eacd57ae5971910e7e492c0e2bd70613190d8c7b146ca5c131f9d`), v1/v2.

## Ba test cũ phải đổi vì chính chúng khóa phạm vi tranche trước

`tests/test_control_check_v3.py`: (1) cây package đúng là các module đã nhận + `observer.py` + `workflow.py`; (2) guard "không `--root`" chỉ còn áp cho `--basis/--trust/--schema/--policy`, và thêm guard cho hai module mới (không import test/checker cũ, không `subprocess`/socket, không gọi `.publish(`/`.recover(`/`.discard_staged(`, không ghi/xóa/mkdir); (3) argv `--root DIR` không còn là lỗi, thay bằng `--root` hai lần, `--root ''`, `--owner`. Không giảm assertion nào khác. Thêm paired test + dòng `fingerprint` D4 vào `test_control_v3_canonical_screening.py` (screening `user_acceptance.accepted_artifacts`).

## Kết quả cần Reviewer biết

1. **Lệch vòng đời task/rid (dependency, không sửa writer):** `publish_new.publish` tự sinh `rid` bên trong, nên task dự kiến ở dispatch/effect (agent dựng bằng `build_task(request, rid_dự_kiến)`) có `task_id` khác task trong `prepared` sau publish. Hai task khác `task_id` ⇒ khác `accepted_task_digest`. Checker xử lý đúng hướng an toàn: accept chỉ nhận bundle của task cuối (từ `prepared`); bundle accept giữ task dự kiến ⇒ `PRECONDITION_PROOF_MISSING`; record effect REQUEST của task dự kiến lẫn trong bundle accept ⇒ `BINDING_INCOMPLETE`. PASS ở dispatch/effect vì vậy áp cho task dự kiến, không chứng minh task cuối. Muốn một task xuyên cả ba pha phải cho owner nhận `rid` do người gọi chọn (thay đổi writer/contract, ngoài brief). Test `HappyLoop.test_real_loop_*` khẳng định `task_id` khác nhau.
2. Quyết định tôi đã chọn trong vùng brief mơ hồ (cần Reviewer xác nhận): (a) T1 đòi grant phủ **mọi** tổ tiên của đích, chặt hơn "grant phủ thư mục con"; (b) accept so cả **identity** file với published (cùng bytes khác file object ⇒ `CHANGED_AFTER_PUBLISH`); (c) mandatory requirement được `result.requirements` ghi `NOT_MET/MISSING/BLOCKED` ⇒ gate REQUIREMENTS `NOT_MET`; (d) `cost_limit` chỉ MET khi hai chuỗi bằng nhau; (e) INPUT_REVISION ở accept dùng bằng chứng lịch sử (`inputs_observed_at_publish`), không đọc lại input hiện tại; (f) pin hiện tại được đo bằng cách băm `tools/publish_new.py` đang được nạp từ cây LAW, rồi so với pin policy.
3. Observer gọi `publish_new.observe` **không** kèm `request_id` (owner coi "chưa có prepared" là `EVIDENCE_INCONSISTENT` và hủy toàn quan sát), rồi gọi `status` riêng; phát hiện khi test đầu tiên chạy đỏ.
4. Owner khi nạp tự chèn `tools/` vào `sys.path`; `observer.load_owner` gỡ mục thêm vào sau khi nạp. `transaction`/`result_schema` vẫn nằm trong `sys.modules` theo tên cũ.

## Chưa kiểm / không claim

CI, Python 3.8 và 3.13 chạy thật, POSIX/ReFS/exFAT/FAT/mạng/OneDrive, antivirus giữ staged, race giữa quan sát và `publish`, host enforcement, review verdict và mọi task có pha review, shape ngoài một-file (overwrite, nhiều action/grant/task, recipe, delegation, vai không-core), semantic của `task_classes`, `expires_at` (UNSUPPORTED), profile/host constraint (không đo), mọi activation/integration/G-04. Không full suite, không chạy lại `windows_proofs.py` hay `tests.test_publish_new` (writer không đổi, pin khớp). `python tools/check_package.py` chạy một lần: 1 lỗi có từ trước (`.cvf/README.md` nhắc `.agent/runtime/governance/`, thuộc G-04) + cảnh báo CRLF; lỗi đường dẫn runtime do README v3 của lượt này tạo ra đã sửa.

## Corrective P-CN1: cùng snapshot xuyên ba pha + T2 bootstrap đúng phạm vi — IMPLEMENTED_PENDING_REVIEW (18/10/2026)

Worker Claude, model quan sát được `claude-sonnet-5-5` (VS Code extension), effort không quan sát được; không agent phụ/AI CLI/API, không stage/commit/push/host/global/admin. Python 3.11.9 + jsonschema 4.23.0, Python 3.13.12 (chỉ writer, thiếu jsonschema), Windows 11 NTFS local, thư mục tạm, dữ liệu giả.

| File | Nội dung |
|---|---|
| `corrective_tests_py311.log` | `python -B -W error::ResourceWarning -m unittest -v tests.test_publish_new tests.test_control_v3_workflow` → 141 test, OK, 1 skip (`NotWindows`, đúng nền) |
| `corrective_regression_v3_py311.log` | cùng cờ, `tests.test_control_check_v3 tests.test_control_v3_routing tests.test_control_v3_canonical_screening tests.test_control_v3_candidate` → 189 test, OK, 0 skip (gồm pin writer/policy/vectors/22 ví dụ đã refresh) |
| `corrective_writer_py313.log` | `py -V:Astral/CPython3.13.12 ... -m unittest -v tests.test_publish_new` → 67 test, OK, 1 skip |
| `corrective_mutation_probe.py/.log` | 6 đột biến sản phẩm tại chỗ (khôi phục từng byte sau mỗi lần, đã đối chiếu hash): bỏ guard snapshot, bỏ kiểm bootstrap của checker, cho writer tạo lại cha, bỏ kiểm rid trước khi mở prepared, nhận rid sai kiểu, bỏ kiểm staged mồ côi dưới khóa; cả 6 làm ít nhất một test đỏ. Đột biến thứ 7 (bỏ kiểm va chạm sớm) sống sót nên kiểm tra sớm thừa đó đã bị **xóa**; kiểm tra có thẩm quyền nằm dưới pin |

**Thay đổi (hash 16 ký tự đầu, trước → sau).** Writer `tools/publish_new.py` `f2b1b425690eacd5` → `a9378680e5bd9eb6`: `publish(..., *, request_id=None)` và CLI `--rid`; rid sai ⇒ `REQUEST_ID_INVALID` trước mọi mutation; mọi file của rid (prepared, terminal, staged mồ côi) ⇒ `RID_TAKEN`, không ghi đè/xóa, kiểm lại dưới pin, dưới khóa và khi O_EXCL; `_walk(..., required=n)` với `.agent`, `.agent/runtime` bắt buộc có sẵn (`RUNTIME_PARENT_MISSING`, không tạo hộ) và T2 chỉ tạo `publish` dưới runtime đã pin; hàm thuần `request_from_task` (dùng chung với `_snapshot_ok`, hành vi đó giữ nguyên); `runtime_parents_problem`; `observe` thêm `runtime_parents_ready`. Wire `publish-v1`, version 1 và hình evidence không đổi. Observer `691c3bc424a9cf11` → `7c0a089e5eb03475` (`rebuild_task`, chuyển tiếp `runtime_parents_ready`). Workflow `dc06bc4e5e3f2165` → `3019bd55a70281d0` (`_snapshot` ở mọi pha → TOOL_SCOPE; precondition bootstrap ở PATH_SCOPE.observed_at_time). Không đổi: entry `e4bcbf35faa3392d`, routing, canon, binding, loader, refs, schema `12becc373df364bd`, v1/v2.
**Pin/digest dẫn xuất (chỉ refresh, tính từ file thật bằng script, không hạ assertion):** policy `8c63bd03bbcdb733` → `abcef5c8fdb413ea` (chỉ dòng `entrypoint_sha256`); `binding.policy_digest` `f850801833bfb62c…` → `1474a4c3fe3b42d5…` trong vectors (`3846b50d652ae097` → `9474940980d02c47`) và 22 ví dụ (`f53accb85fcd4ec8` → `4bb0388e388b9565`); hằng pin trong `test_control_check_v3.py`, `test_control_v3_candidate.py`, `test_control_v3_workflow.py`. Receipt/proof mang pin cũ không tự migrate.
**Test đổi có chủ đích:** fixture writer/workflow tạo `.agent/runtime` rõ ràng (precondition mới); `wrote` của T2 còn một mkdir; hai test envelope (`max_retries` bằng hạn mức, `cost_limit` bằng chuỗi) từng PASS giờ BLOCKED vì owner bỏ envelope tùy chỉnh (ENVELOPE vẫn MET, TOOL_SCOPE UNSUPPORTED `TASK_NOT_OWNER_REPRESENTABLE`); `HappyLoop` dùng một task xuyên dispatch → effect → `publish(request_id=rid)` → accept và so task_id, task_revision, digest intent/context/accepted_task/action/policy của task dự kiến, prepared và mọi record binding của bundle accept (thay assertion cũ "task_id khác nhau"). Test mới: writer `CallerRid` (10) + `RuntimeBootstrap` (6); workflow `StableSnapshot` (9).

**Chưa kiểm / không claim.** CI, Python 3.8 chạy thật, test workflow trên 3.13 (thiếu jsonschema), POSIX/ReFS/exFAT/FAT/mạng/OneDrive, race thật giữa quan sát và `publish`, host enforcement, task có pha review, shape ngoài một-file, `task_classes` ngữ nghĩa, `expires_at`; full suite, `check_package.py`, review verdict. Hai script proof I cũ (`pcn1-i/windows_proofs.py` 22 PASS, `pcn1-i/corrective_proofs.py` 6 PASS) chạy lại một lần trên writer mới: không dòng FAIL, exit 0 (chỉ stdout, không ghi file); chưa đọc kỹ từng proof để nói chúng có chạm precondition bootstrap mới hay không. Dependency còn lại cho integration/G-04: **khởi tạo `.agent` và `.agent/runtime`** cho root mới (root này đã có `.agent/runtime`); tên mã lý do writer mới (`REQUEST_ID_INVALID`, `RUNTIME_PARENT_MISSING`) chưa vào enum nào ngoài tài liệu.
