# S3-B foundation v3 hẹp — evidence (Worker, 18/10/2026)

Trạng thái: IMPLEMENTED_PENDING_REVIEW (FOUNDATION_ONLY). Dữ liệu giả; không evaluator, route/gate, observer hay activation. Python 3.11.9, jsonschema 4.23.0, Windows 11.

| File | sha256 (16 ký tự đầu) | Nội dung |
|---|---|---|
| test_control_check_v3_py311.log | 9b4a10cf9b57a030 | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_check_v3`: 73 chạy, OK, 0 skip |
| cli_ex04_accept.json | c53623a0876b792c | `python -B -I .cvf/checks/control_check_v3.py --contract v3 --phase accept <ex04>` chạy từ thư mục ngoài repo: BLOCKED, `CANDIDATE_EVALUATION_NOT_IMPLEMENTED`, `binding_evaluated=false` (exit 1) |

Hash các file sản phẩm/kiểm (khớp lúc ghi log):

| File | sha256 (16 ký tự đầu) |
|---|---|
| .cvf/checks/control_check_v3.py | ff93aace52cc77e7 |
| .cvf/checks/v3/README.md | 6c2f989d9c6a3753 |
| .cvf/checks/v3/__init__.py | 7e1df833e9487a67 |
| .cvf/checks/v3/loader.py | 6c3839e3a9c0d2b0 |
| .cvf/checks/v3/canon.py | 4e125bf0cf870b60 |
| .cvf/checks/v3/refs.py | 33761fd35bd6b8f6 |
| .cvf/checks/v3/binding.py | 2551d3f573669747 |
| tests/test_control_check_v3.py | 8f959d2fe8381f84 |

Nguyên byte (test pin): v1 (6 owner), cây v2 contracts+rules (30 file, `e154e1db4438adb9`), cây checks v2 (6 file, `3a4895ec9979faaa`), `control_check_v2.py` `5179e7091579c048`, schema v3 `12becc373df364bd`, policy v3 `8c63bd03bbcdb733`, vectors v3 `3846b50d652ae097`, 22 ví dụ v3 (`f53accb85fcd4ec8`), `tools/publish_new.py` SHA256 `f2b1b425690eacd57ae5971910e7e492c0e2bd70613190d8c7b146ca5c131f9d`, ba test v2/v1 và `test_control_v2_candidate.py`.

Hồi quy cùng lượt: `tests.test_control_check_v3 tests.test_control_v3_candidate tests.test_control_v2_candidate tests.test_control_check_v2` 216 chạy OK; `tests.test_control_check_v2_s2` 97 chạy OK. Đột biến thử (đã hoàn nguyên): đổi `bind/3` thành `bind/2` trong canon ⇒ 8 test đỏ; bỏ vị trí `user_acceptance.ref` trong refs ⇒ test refs đỏ.

Giới hạn: Python 3.8 chỉ `ast.parse`, chưa chạy 3.8/3.13 thật, CI, macOS/Linux; không full suite. Foundation không kiểm pin writer, receipt, D4, vùng hay route; không đọc `tools/`.
