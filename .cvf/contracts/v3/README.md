# Candidate contract v3 — chưa kích hoạt

Trạng thái: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED / CANDIDATE_NOT_ACTIVE** (A0 hẹp, G-02-C2, 18/10/2026). Phạm vi chỉ **một action `create_new` do owner protocol P-CN1 publish, Windows NTFS local**.
Đã có entry/loader S3-B foundation đọc owner khi chọn v3 tường minh, chỉ kiểm cấu trúc và luôn BLOCKED; chưa evaluator workflow, tích hợp hay kích hoạt.

- `control.schema.json` — schema `law.cvf.control/3` (Draft 2020-12), cơ sở `COOPERATIVE_WORKFLOW`, binding `law.cvf.bind/3`.
- `CONTROL_CONTRACT.md` — ngữ nghĩa, phần dùng/hoãn so với v2, owner protocol, D4, danh sách UNSUPPORTED.
- `vectors.json` — vectors canonical/bytes/projection/policy/receipt cho binding; test tính lại.
- `examples/` — 22 bundle dữ liệu giả (`example_only`, grant `EXAMPLE_INACTIVE`) + `EXPECTED.json` tách `schema_valid` với kỳ vọng workflow `NOT_RUN`.
- Policy cùng version ở `.cvf/rules/v3/ROUTING_POLICY.json`, bản đọc `CONTROL_RULES.md`.
- v1 ở các đường gốc và v2 ở `.cvf/contracts/v2/` giữ nguyên từng byte; checker hiện có không tự tìm/chọn thư mục này.
- Một owner mỗi version; v3 candidate không là policy thay thế để vượt BLOCKED, không dùng cho effect hoặc đóng gói. Một version hiệu lực được chọn tường minh ở tích hợp.
- Pin `owner_protocols[0].entrypoint_sha256` là SHA256 của `tools/publish_new.py` đã được review nhận; pin là so sánh version hợp tác (ADVISORY), không chứng minh tool thật và không cấp quyền. Hash thực lệch pin thì kiểm delta và báo, không tự repin. Revision corrective 18/10 (caller `request_id`, precondition `.agent`/`.agent/runtime` có sẵn) đã đổi byte và pin; refresh pin kèm digest dẫn xuất (`binding.policy_digest`, vectors, 22 ví dụ) được operator cho phép riêng, đã được Reviewer độc lập nhận WITH_LIMITS (18/10); chưa activation.
- Field `operational_context_protocol` (P-CTX1, `tools/context_update.py`, I1 18/10/2026): chỉ khai báo phạm vi ghi chú vận hành STATE/HANDOFF có sẵn, pin ADVISORY của owner mới; không dùng `owner_protocols`/T1–T7, không evaluator, không PASS (mục 6.1 của contract). Thêm field này đổi policy digest nên đã refresh `binding.policy_digest`, vectors và 22 ví dụ; writer P-CN1 và pin `8a4e5914…` giữ nguyên.
- Không grant/receipt/authority thật; hash chỉ nhận dạng bytes. Test: `tests/test_control_v3_candidate.py`.
