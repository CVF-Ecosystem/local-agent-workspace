# S3-C/D binding và routing hẹp — evidence (Worker, 18/10/2026)

Trạng thái: IMPLEMENTED_PENDING_REVIEW (BINDING_ROUTING_ONLY). Dữ liệu giả; không gate, observer, receipt/D4 runtime, pin entrypoint hay activation. Python 3.11.9, jsonschema 4.23.0, Windows 11. Không stage/commit/push.

Model/effort: model quan sát được trong phiên là `claude-haiku-5-5` (không phải preset Sonnet của brief B); effort không quan sát được. Không agent phụ, không AI CLI/API, không host/global/admin. Chưa kết luận chất lượng model từ một mẫu.

| File | Nội dung |
|---|---|
| test_control_v3_py311.log | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_check_v3 tests.test_control_v3_routing tests.test_control_v3_candidate`: 165 chạy, OK, 0 skip (~26s) |
| cli_ex04_accept.json | `python -B -I .cvf/checks/control_check_v3.py --contract v3 --phase accept <ex04>` chạy từ thư mục ngoài repo: BLOCKED, `CANDIDATE_EVALUATION_NOT_IMPLEMENTED`, `routing_evaluated=true`, route RESOLVED (A-NEW_TARGET không áp dụng ở accept), exit 1 |
| cli_ex13_effect.txt | `--phase effect --format text <ex13>`: BLOCKED, `REVIEW_REQUIRED_UNSUPPORTED`, route `R-HIGH_STAKES`, exit 1 |

Hồi quy cùng lượt (không cộng thành số ca duy nhất): `tests.test_control_check`, `tests.test_control_v2_candidate`, `tests.test_control_check_v2`, `tests.test_control_check_v2_s2` chạy chung 291 test, OK. `python tools/check_package.py`: 1 lỗi cũ `.cvf/README.md` (đường dẫn `.agent/runtime/governance/`, G-04) và 1 cảnh báo CRLF (36 file), không có lỗi mới.

Hash prefix 16 ký tự của file đã đổi trong lượt này:

| File | Trước (S3-B) | Sau (S3-C/D) |
|---|---|---|
| .cvf/checks/control_check_v3.py | ff93aace52cc77e7 | 4e82b4fa7daab12f |
| .cvf/checks/v3/loader.py | 6c3839e3a9c0d2b0 | fbe48846a02fc6c0 |
| .cvf/checks/v3/routing.py | (mới) | cdb93b2c562b9afd |
| .cvf/checks/v3/__init__.py | 7e1df833e9487a67 | 3e4d9f92ba71ea44 |
| .cvf/checks/v3/README.md | 6c2f989d9c6a3753 | d16b452b3a8c3edd |
| .cvf/contracts/v3/CONTROL_CONTRACT.md | (không ghi hash S3-B) | f0611d5ba5a148b1 |
| tests/test_control_check_v3.py | 8f959d2fe8381f84 | 9ba223e80a29e273 |
| tests/test_control_v3_routing.py | (mới) | 4a66da7c07d5a8f3 |

Không đổi (đã kiểm hash): `canon.py` 4e125bf0cf870b60, `refs.py` 33761fd35bd6b8f6, `binding.py` 2551d3f573669747; schema v3 `12becc373df364bd`; policy v3 `8c63bd03bbcdb733`; 22 ví dụ v3 `f53accb85fcd4ec8`; `tools/publish_new.py` SHA256 `f2b1b425690eacd5…c131f9d`; `control_check_v2.py` `5179e7091579c048`; cây v1/v2 giữ theo pin trong test.

Giới hạn: không gate, observer, receipt/D4, pin entrypoint, review verdict; route không kiểm `ENVELOPE_EXCEEDED` (gate ENVELOPE); Python 3.8/3.13 thật, CI, macOS/Linux, full suite chưa chạy; không đọc artifact/locator/mạng; screening miền canonical toàn bundle vẫn là nợ bảo thủ; mã reason ngoài enum schema là mã của checker.
