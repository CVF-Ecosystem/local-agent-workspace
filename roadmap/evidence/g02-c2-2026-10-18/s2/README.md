# Evidence G-02-C2/S2 — helper refs/binding trong bộ nhớ (18/10/2026)

Worker: Sonnet 5.5 (brief yêu cầu High; effort không xác nhận được). Python 3.11.9, jsonschema 4.23.0, Windows. Trạng thái: IMPLEMENTED_PENDING_REVIEW.
Chỉ chứng minh thư viện so sánh/tính lại trong bộ nhớ và refactor hẹp loader. Không nối entry, không route/gate/observer, không PASS/MET.

## Lệnh đã chạy và log

| Mục đích | Lệnh (cwd = gốc repo) | Log | Kết quả |
|---|---|---|---|
| Hash trước khi sửa | `git ls-files -c -o --exclude-standard -z \| xargs -0 sha256sum \| sort -k2`; `(cd .cvf && find . -type f -not -path '*/__pycache__/*' \| sort \| xargs sha256sum)` | `tree_hashes_before.txt` (464 file), `cvf_hashes_before.txt` | khớp hash ghi trong HANDOFF (loader b9a9439d5b5cfea5, test S1 93101be37f7121c2, README ecbd27910d8ca162, entry 5179e7091579c048, canon c593c6d070ccdf67, v1 f95bfc367bb7f470) |
| Test-first scaffolding (đỏ vì module/helper chưa tồn tại, **không phải** repro hành vi) | `python -B -W error::ResourceWarning -m unittest tests.test_control_check_v2_s2` | `red_scaffold.log` | 4 test chạy, 1 fail + 11 error (thiếu `refs.py`/`binding.py`/helper loader) |
| Hồi quy loader sau refactor, trước khi có refs/binding | `python -B -W error::ResourceWarning -m unittest tests.test_control_check_v2` | (chạy tay, kết quả ghi ở HANDOFF) | 63 test: 61 đạt; 2 đỏ đúng dự kiến vì kỳ vọng cây package mới (thêm 2 module) còn thiếu file |
| Kiểm S2 + hồi quy S1 | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_check_v2_s2 tests.test_control_check_v2` | `green.log` | **157 test, 157 đạt, 0 skip, 0 fail** (94 S2 + 63 S1), ~38 s |
| Phản chứng thủ công (bản sao tạm; repo thật không bị sửa) | script đột biến ở thư mục scratch (không nằm trong repo), mỗi đột biến chạy `tests.test_control_check_v2_s2` | `mutation_probe.log` | 23 đột biến ban đầu (M01–M23): 21 bị bắt, **M07 và M13 sống sót** → thêm test từ vựng locator và đột biến M07b (M07 gốc tương đương hành vi vì tập quan hệ bắt buộc không bao giờ rỗng; khi phần "không áp dụng" đổi thành complete=true thì 3 test bắt), rerun: M13 và M07b bị bắt. Lần rerun đầu của M07b/M13 hỏng cú pháp ở chính script đột biến, đã ghi trong log và chạy lại |
| Cú pháp Python 3.8 (chỉ ngữ pháp) | `ast.parse(..., feature_version=(3, 8))` + grep API mới hơn 3.8 | `py38_syntax.log` | ngữ pháp hợp lệ, không có API mới hơn 3.8 trong các file mới; **không phải** chạy trên Python 3.8 |
| Hash sau khi sửa | như lệnh hash trước | `tree_hashes_after.txt`, `cvf_hashes_after.txt`, `tree_diff.txt`, `HASHES_FINAL.txt` | chỉ đổi loader, README package, test S1; thêm `refs.py`, `binding.py`, test S2 và evidence. Entry, `__init__`, canon, v1, C1 owner, hai test pin: không đổi |

Không chạy: 24 test C1, 107 test G-02/`tests.test_control_check`, full suite, CI từ xa, model/AI CLI/API, host/admin. `tree_hashes_after.txt` chụp trước khi ghi README này (hash của chính nó là hash tệp rỗng).

## Bao phủ test S2 (94 test, 10 lớp)

`OwnersUntouched` (pin owner S1/C1/v1 và 2 test; cây package đúng 6 file; refs/binding không I/O/mạng/`sys.path`/import test), `LoaderHelpers` (hình dạng `parse_and_preflight`/`validate_structure`, `inspect_bundle` gọi đúng hai helper theo thứ tự, screen S1 vẫn từ chối cái mà đường S2 nhận, `policy_bytes` không bị lệch khi dict cache bị sửa tại chỗ, 13 ví dụ hợp lệ vẫn BLOCKED/`binding_evaluated=false`), `PolicyContext`, `IndexTests`, `ClaimTests`, `GrantLinkTests`, `KernelTests`, `ObjectSetTests`, `BindingTests`, `PointerTests`, `PurityTests` (không mutation, không alias container, không echo canary, không I/O/mạng, xác định, đảo thứ tự record, frozen, bề mặt S1 không đổi).

## Giới hạn

Không nối entry; không có evaluator. `refs.py` 548 dòng và `binding.py` 475 dòng, lớn hơn ước tính trong thiết kế (≤300/≤350); chưa tách thêm. Hàm tham chiếu C1 và canon sản phẩm cùng tác giả; đối chiếu chỉ qua vector C1 và hàm tham chiếu đã có. Chưa Python 3.8 thật, CI, jsonschema khác 4.23.0, Linux/macOS. Mọi quan hệ về digest object nghĩa là byte file thô chưa quan sát (`UNVERIFIED_RAW_BYTES`).
