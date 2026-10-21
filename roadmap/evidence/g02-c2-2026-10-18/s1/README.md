# Evidence G-02-C2/S1 (FOUNDATION_ONLY) — 18/10/2026

Worker: Sonnet 5.5 (brief yêu cầu High; effort không xác nhận được). Python 3.11.9, jsonschema 4.23.0, Windows. Trạng thái: IMPLEMENTED_PENDING_REVIEW.
Chỉ chứng minh nền S1 (entry, loader strict, canon, router CLI v1, output FOUNDATION_ONLY). Không chứng minh evaluator binding/route/gate nào tồn tại.

## Lệnh đã chạy và log

| Mục đích | Lệnh (cwd = gốc repo trừ ghi chú) | Log | Kết quả |
|---|---|---|---|
| Hash trước khi sửa | `git ls-files -c -o --exclude-standard -z \| xargs -0 sha256sum \| sort -k2`; `(cd .cvf && find . -type f -not -path '*/__pycache__/*' \| sort \| xargs sha256sum)` | `tree_hashes_before.txt`, `cvf_hashes_before.txt` | 438 file; khớp hash đã ghi ở HANDOFF (checker v1 f95bfc367bb7f470, EXPECTED v2 3b463f654d51a9ec, schema v2 4c6dd3dae50596b5, policy v2 20cff567afe4fa0f) |
| Test-first scaffolding (đỏ vì entry/package chưa có, **không phải** repro hành vi) | `python -B -W error::ResourceWarning -m unittest tests.test_control_check_v2` | `red_scaffold.log` | 4 test chạy, 1 fail + 8 error (FileNotFoundError / cây package chưa có) |
| Kiểm S1 | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_check_v2` | `green.log` | **58 test, 58 đạt, 0 skip, 0 fail**, ~28 s |
| Phản chứng (thủ công, trong bản sao tạm; repo thật không bị sửa) | sao chép `.cvf` + 3 file test ra thư mục tạm, sửa sản phẩm, chạy lớp test liên quan | `mutation_probe.log` | 6 đột biến đều bị bắt (fullmatch→match, bỏ VERSION_MIXED, v1 thêm output/ép exit 0, BLOCKED exit 0, router không đặt argv/prog, bỏ quét miền canonical). Lần đầu M3 hỏng cú pháp ở chính đột biến (ghi rõ trong log), chạy lại đạt kết quả bắt được |
| Smoke ngoài repo bằng `python -I` | chạy tay từ thư mục tạm, đường tuyệt đối tới entry | `smoke.log` | v2 JSON/text BLOCKED exit 1; v1-bundle ở v2 UNSUPPORTED kèm gợi ý; `--contract v1` byte-identical với chạy trực tiếp; thiếu `--contract` exit 2; bundle không đọc được exit 2 |
| Cú pháp Python 3.8 (chỉ ngữ pháp) | `ast.parse(..., feature_version=(3, 8))` + grep API mới hơn 3.8 | `py38_syntax.log` | ngữ pháp hợp lệ; **không phải** chạy trên Python 3.8 |
| Hash sau khi sửa | như lệnh hash trước | `tree_hashes_after.txt`, `cvf_hashes_after.txt`, `tree_diff.txt` | chỉ thêm 5 file sản phẩm, 1 file test và evidence; không file hiện có nào đổi (HANDOFF/STATE đổi sau bước này, xem HASHES_FINAL.txt) |

Không chạy: 24 test C1, 107 test G-02/`tests.test_control_check`, full suite, CI từ xa, model/AI CLI/API, host/admin (owner không đổi; đúng brief).
`tree_hashes_after.txt` chụp trước khi ghi README này nên không chứa file này và hash của chính nó là hash tệp rỗng.

## Bao phủ test S1 (58 test, 8 lớp)

- `OwnersUntouched`: pin hash 6 owner v1 + 2 test v1/C1; cây package chỉ README/`__init__`/canon/loader; sản phẩm không import test, không đụng đường nạp module, không có cờ `--root/--basis/--trust/--schema/--policy`.
- `OutputContract`: 13 ví dụ hợp lệ × 3 pha → BLOCKED/`CANDIDATE_EVALUATION_NOT_IMPLEMENTED`, đúng 17 trường theo thứ tự, không PASS/N/A; hash owner = hash byte đã đọc; một record đơn; lỗi tham số API (TypeError/ValueError); bề mặt public chỉ `check_bytes/exit_code/main`.
- `RefusalMatrix`: 9 ví dụ không hợp lệ của EXPECTED + biến thể version/basis/binding literal/schema/`routing_policy`/malformed/miền canonical; không chép giá trị payload vào output.
- `LoaderInit`: owner thiếu, remote `$ref`, literal sai, schema/policy không hợp lệ, khóa trùng ở owner, jsonschema thiếu/quá cũ → init_error + exit 2, hash những gì đã đọc.
- `NoObservation`: bundle trỏ vào file canary thật + URL `file:///`: canary không bao giờ được mở, chỉ hai owner (và dò phiên bản jsonschema) được đọc, không dùng mạng.
- `CliV2`: JSON/text cùng disposition/exit, exit code từng loại, file quá 8 MiB, lỗi tùy chọn argparse, `python -I` từ ngoài repo với `PYTHONPATH` và `json.py` bị gài.
- `ContractRouter`: parity stdout/stderr/exit với v1 (3 bundle × 3 pha × json/text, vị trí cờ, dạng `=`, lỗi forward, `-h`), lỗi `--contract` thiếu/lạ/trùng/viết tắt, v1 không import package v2 và ngược lại (tiến trình riêng), khôi phục `sys.argv`.
- `Canon`: 20 vector canonical, 4 vector bytes, projection fixture, digest policy, đối chiếu từng đầu vào/ví dụ với hàm tham chiếu C1 (`tests/test_control_v2_candidate.py`, nạp theo đường dẫn), loại trừ/bao gồm trường, set vs sequence, missing vs null, `domain_violations`.

## Giới hạn

Không có evaluator; mọi bundle hợp lệ cấu trúc là BLOCKED. Chưa Python 3.8 thật, chưa CI. Hàm canon sản phẩm và hàm tham chiếu C1 cùng một tác giả nên "độc lập" chỉ nhờ vector và đối chiếu C1 đã có `sha256sum`; test S1 không bổ sung kiểm độc lập mới.
Quét miền canonical áp cho **toàn bộ bundle** (không chỉ phần sẽ được băm) vì S1 chưa biết phần nào vào projection: đây là lựa chọn của Worker cần Reviewer xét.
