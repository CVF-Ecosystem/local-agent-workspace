# A0 hẹp — candidate v3 (một action P-CN1) — evidence (Worker, 18/10/2026)

Trạng thái: CONTRACT_CANDIDATE_PENDING_REVIEW. Dữ liệu giả; không đụng tài liệu thật; không evaluator/checker; không activation. Python 3.11.9, jsonschema 4.23.0, Windows 11.

| File | sha256 (16 ký tự đầu) | Nội dung |
|---|---|---|
| test_control_v3_candidate_py311.log | 04dc45cb6fc6aa27 | `python -B -W error::ResourceWarning -m unittest -v tests.test_control_v3_candidate`: 55 chạy, OK, 0 skip |

Hash các file được kiểm (khớp lúc ghi log):

| File | sha256 (16 ký tự đầu) |
|---|---|
| .cvf/contracts/v3/control.schema.json | 12becc373df364bd |
| .cvf/contracts/v3/CONTROL_CONTRACT.md | 9696c0644c9bb698 |
| .cvf/contracts/v3/README.md | 5772677a7fb1b1aa |
| .cvf/contracts/v3/vectors.json | 3846b50d652ae097 |
| .cvf/contracts/v3/examples/EXPECTED.json | 2551b6e41ecd55fa |
| 22 file ex01–ex22 (hash gộp: các dòng `tên:sha256` sắp xếp) | f53accb85fcd4ec8 |
| .cvf/rules/v3/ROUTING_POLICY.json | 8c63bd03bbcdb733 |
| .cvf/rules/v3/CONTROL_RULES.md | 940049a57dd6cc56 |
| .cvf/rules/v3/README.md | f07b5bd99c7f546f |
| tests/test_control_v3_candidate.py | 193b23bd0424807b |

Writer đã nhận (không đổi): tools/publish_new.py SHA256 `f2b1b425690eacd57ae5971910e7e492c0e2bd70613190d8c7b146ca5c131f9d`. v1 (6 pin) và v2 (6 file chính + cây 30 file, hash gộp `e154e1db4438adb9`) nguyên byte, kiểm bằng test.

Giới hạn: không có checker nên không có verdict workflow; `expected_design` là kỳ vọng tình huống giả định. Python 3.8 chỉ `ast.parse`, chưa chạy thật. Ví dụ và vectors do script tạm sinh rồi bị bỏ (không nằm trong kho); test tính lại digest độc lập bằng hàm tham chiếu và bằng `build_task`/`cj_dumps` của owner.
