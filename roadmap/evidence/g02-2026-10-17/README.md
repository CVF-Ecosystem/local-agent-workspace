# Bằng chứng G-02 (17/10/2026)

Do Worker (phiên tự báo claude-sonnet-5-5, effort không quan sát được) lưu để Reviewer kiểm lại; không phải bằng chứng host hay xác minh nguồn.

- `test_control_check.log` — `python -B -m unittest tests.test_control_check -v` chạy trên máy Windows, Python 3.11.9, jsonschema 4.23.0. Chỉ tái hiện logic checker trên record tổng hợp.
- `mutation_probe.py` / `mutation_probe.log` — phá cố ý 12 điểm trọng yếu (7 ban đầu + 5 cho lượt sửa: bỏ actor_ids, binding chỉ path+hash, action_digest một phía, role_name so thẳng với nhóm, mọi non-PASS chặn) của checker (trong 7 điểm đầu: NO_PROTECTED_TARGET thành TRUE, tin `verification.status` trong record, so đường dẫn bằng tiền tố chuỗi, verifier mặc định luôn VERIFIED, delegation luôn MET, đổi điều kiện UNKNOWN thành FALSE, nhận attestation từ lời khai); mỗi đột biến phải làm đỏ ít nhất một test. Chạy: `python -B roadmap/evidence/g02-2026-10-17/mutation_probe.py .` từ gốc repo.
- `examples_run.log` — kết quả checker trên 19 ví dụ G-01 (disposition, exit, reasons).

Chưa chạy: Python 3.8 thật, CI remote, macOS, full suite, check_package.

## Sửa nhỏ của Main trong review

Ngày 17/10/2026, sau snapshot log Worker ở trên: sửa ex01 effect tham chiếu
grant-ref-1 đúng grant có sẵn; sửa ex17 actor từ worker thành main đúng subject
của grant. Đây là sửa dữ liệu giả, không thay schema/policy/EXPECTED hoặc active grant.
Hash SHA256 (16 ký tự đầu): ex01 fef26cba7f610bd2 → 5547713982ab9741;
ex17 0ccdb606dfc854c4 → 3729bc3f4a133ca2. Log Worker giữ nguyên, không coi kết quả
71 test/7 mutation là lần chạy trên hai fixture sau sửa.

Main thực chạy `python -B -m unittest` với ba target:
`tests.test_control_check.ExamplesOracle.test_examples_match_current_expectations`,
`tests.test_control_check.SafetyAndRouting.test_cooperative_draft_is_consistent_but_not_a_safety_pass`,
`tests.test_control_check.Delegation.test_shipped_example_stays_blocked_for_inactive_grant`:
3 đạt, 0 skip. Kiểm jsonschema và assertions riêng cho hai fixture đạt: ref đúng,
actor nằm trong grant subject và grant vẫn EXAMPLE_INACTIVE. Lệnh/kết quả nằm trong
tool transcript Main; không chạy lại full suite hoặc mutation probe.

## Lượt sửa 4 nhóm P2 (Worker, 17/10/2026)

- `corrective_red_before_fix.log` — 93 test chạy trên code chưa sửa (hash 7aebb666586ef261): 16 đỏ, đúng bốn nhóm
  (subject, binding, delegation task/context, namespace vai) cộng hai test cũ có kỳ vọng đổi.
- `corrective_green_after_fix.log` — cùng 93 test sau sửa: OK. Probe 12 đột biến: 0 sống sót, baseline 0 lỗi/93.
- `test_control_check.log`, `examples_run.log` là lượt đầu, giữ làm lịch sử.
- Chưa chạy: Python 3.8 thật, CI remote, macOS, full suite, check_package.

## Main sửa trực tiếp delta 3 P2, 17/10/2026

Theo lệnh operator; không gán lượt này cho Claude Worker hay preset model.

- `main_delta_red.log`: 12 test mới trên source9599be2e89e9e588 trước sửa, 14
  assertion/subtest fail; `main_delta_green.log`: bản sửa đầu có105 test G-02 đạt.
- Trong review độc lập,1 probe chỉ đổi artifact.revision (binding.outputs giữ cũ)
  phát hiện thiếu output anchor. Main thêm kiểm strict binding.outputs↔artifacts
  ở generic BINDING và trước PASS projection; veto cùng binding vẫn trước coverage.
- `main_output_anchor_red.log`:2 test mới/7 subtest fail trên bản trung gian;
  `main_delta_anchor_green.log`: bản cuối107 test đạt/0 skip/41.080s.
- Lệnh green: `python -B -m unittest tests.test_control_check -v` (chỉ bộ G-02).
  Red chạy riêng lớp MainDeltaProjection/MainDeltaChild/MainDeltaRegistered, và
  hai test output anchor mới. Test fixtures giả, không live governance/host proof.
- Hash16 trước→sau: code9599be2e89e9e588→f95bfc367bb7f470;
  tests29e6cc8f68cbd2d4→454e3f4944825809. Schema/policy/EXPECTED G-01 giữ nguyên.
- Shared positive child fixture nay có basis.inputs bằng child.inputs; phản ví dụ
  thiếu/sai input được giữ tường minh. Registered positive thêm group attestation;
  scope qualifier sai báo coverage thiếu thay vì binding stale.
- Không project full suite hoặc mutation rerun.12 mutation Worker/log cũ giữ
  attribution/snapshot cũ; không suy đã kiểm trên bản Main. Chưa CI remote,
  Python3.8 thật/macOS/package/release hoặc source-byte/host observation.

Reviewer độc lập Sol6.1 High đã nhận bản cuối f95bfc367bb7f470/tests454e3f4944825809
ngày17/10: đọc anchor delta, hai test mới và log đỏ/xanh107, không rerun suite/probe.
Ba P2/output anchor resolved trong phạm vi record checks. G-03 stage1 brief đã được
preflight để thiết kế/khả thi; acceptance này không phải host enforcement, không đóng
nợ ex19 hoặc A-06 x14. Verdict có attribution tại HANDOFF.
