# Đóng nợ canonical screening projection-aware — evidence (Worker, 18/10/2026)

Trạng thái: IMPLEMENTED_PENDING_REVIEW. Giữ BINDING_ROUTING_ONLY, CANDIDATE_NOT_ACTIVE; không gate, observer, receipt/D4 runtime, PASS hay activation. Dữ liệu giả. Python 3.11.9, jsonschema 4.23.0, Windows 11. Không stage/commit/push.

Model/effort: model quan sát được `claude-sonnet-5-5` (phiên chuyển sang bằng `/model sonnet` sau lượt C/D do `claude-haiku-5-5` làm); effort không quan sát được. Không agent phụ, không AI CLI/API, không host/global/admin.

| File | Nội dung |
|---|---|
| test_control_v3_py311.log | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_check_v3 tests.test_control_v3_routing tests.test_control_v3_canonical_screening tests.test_control_v3_candidate`: 185 chạy, OK, 0 skip |
| cli_baseline_ex04_accept.json | `python -B -I .cvf/checks/control_check_v3.py --contract v3 --phase accept <ex04>` từ thư mục ngoài repo: BLOCKED, exit 1 |
| cli_unbound_note_nfd_accept.json | cùng bundle, `records[0].note` đổi thành chuỗi không NFC (metadata bị loại khỏi projection): đầu ra **giống hệt** baseline (`cmp` không khác) |
| cli_bound_main_interpretation_nfd_accept.txt | cùng giá trị không NFC đặt ở `intent.main_interpretation` (vào `task_part`): UNSUPPORTED / `UNSUPPORTED_BINDING_PART`, `phase_scope=null`, binding/routing chưa chạy, `details` chỉ nêu tên phần và số đếm theo mã |

Kiểm đối chứng:

- Sweep từng lá của 4 ví dụ (EX01, EX02, EX04, EX11): 52 lá bound, 65 lá unbound. "Bound" xác định bằng độ nhạy digest/quan hệ do builder và comparator thật tính (đổi lá sang giá trị trong miền), không bằng `bound_violations`. Screening mới khớp tập bound; quét toàn bundle cũ từ chối cả 65 biến thể unbound. Ngoại lệ có ghi: `binding.task_revision` (khóa tra cứu, so thô).
- Bảng cặp mutation viết tay: 11 dòng unbound (nhận, đầu ra không đổi ở cả ba pha, fingerprint digest không đổi) và 15 dòng bound (từ chối, đúng tập locator kỳ vọng). Có cả số nguyên ngoài ±(2^53−1) và thập phân `2.0` ở trường kiểu integer.
- Đột biến thử trên sản phẩm (đã hoàn nguyên, hash khôi phục đúng): quay về `domain_violations` toàn bundle ⇒ 44 lỗi; bỏ `context` ⇒ 1; bỏ đối ứng `artifacts` ⇒ 7; bỏ `effect.action` ⇒ 12; quét thêm `note` ⇒ 25.

Hash prefix 16 ký tự (trước ⇒ sau):

| File | Trước | Sau |
|---|---|---|
| .cvf/checks/v3/canon.py | 4e125bf0cf870b60 | 305fe127a290b40c |
| .cvf/checks/v3/loader.py | fbe48846a02fc6c0 | 9880148ead018257 |
| .cvf/checks/v3/README.md | d16b452b3a8c3edd (Worker C/D; Reviewer sửa sau, không ghi hash giữa chừng) | d1a41c1d2ad0c848 |
| .cvf/contracts/v3/CONTROL_CONTRACT.md | f0611d5ba5a148b1 (như trên) | f521f8b2c047c929 |
| tests/test_control_v3_canonical_screening.py | (mới) | e9f76e7a007f226f |

Không đổi: `control_check_v3.py` 24d2928ae64270a8, `routing.py` c8b972e6a18440b6, `binding.py` 2551d3f573669747, `refs.py` 33761fd35bd6b8f6, `__init__.py` 3e4d9f92ba71ea44, `tests/test_control_check_v3.py` 3695412e254c74a6, `tests/test_control_v3_routing.py` 3ef02b58f8b6d43f; schema 12becc373df364bd; policy 8c63bd03bbcdb733; vectors 3846b50d652ae097; 22 ví dụ f53accb85fcd4ec8; `tools/publish_new.py` SHA256 `f2b1b425…c131f9d`; `control_check_v2.py` 5179e7091579c048; v1/v2 theo pin test.

`python tools/check_package.py`: 1 lỗi cũ `.cvf/README.md` (đường dẫn `.agent/runtime/governance/`, G-04) và cảnh báo CRLF 36 file có sẵn, không lỗi mới.

Giới hạn: không gate/observer/receipt/D4/pin/review verdict; hồi quy v1/v2 không chạy lại riêng (các file này không đổi, pin byte nằm trong bộ v3); Python 3.8/3.13 thật, CI, macOS/Linux, full suite chưa chạy; delegation pointers (`compare_pointers`) chưa nối entry nên chưa nằm trong screening; hình dữ liệu sai và trùng phần tử do comparator báo, không do screening; khóa tra cứu (`binding.task_revision`, `grant_revision`) và so thô của nhóm lời khai ref (REF_CONFLICT) là guard riêng, không thuộc screening canonical.
