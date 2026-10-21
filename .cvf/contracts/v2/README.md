# Candidate contract v2 — chưa kích hoạt

Trạng thái: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED** (G-01-C1, 18/10/2026). Nền loader G-02-C2/S1 đã đọc/validate cây này; chưa evaluator workflow hoặc host integration, chưa kích hoạt.

Operator nhận phạm vi workflow hợp tác có kiểm tra/review bắt buộc ngày 18/10/2026 (nguồn quyết định trong kho maintainer:
roadmap/DE_XUAT_PHAM_VI_KIEM_SOAT_LAW_2026-10-18.md).

- `control.schema.json` — schema `law.cvf.control/2` (Draft 2020-12), cơ sở `COOPERATIVE_WORKFLOW`, binding `law.cvf.bind/2`.
- `CONTROL_CONTRACT.md` — ngữ nghĩa, attribution, định nghĩa binding, danh sách UNSUPPORTED.
- `vectors.json` — vectors canonical/bytes/projection/policy cho binding; test tính lại.
- `examples/` — 22 bundle dữ liệu giả (`example_only`, grant `EXAMPLE_INACTIVE`) + `EXPECTED.json` tách `schema_valid` với kỳ vọng workflow `NOT_RUN`.
- Policy cùng version ở `.cvf/rules/v2/ROUTING_POLICY.json`, bản đọc `CONTROL_RULES.md`.
- v1 ở các đường gốc vẫn là owner active của checker hiện tại; checker không tự tìm/chọn thư mục này.
- Một owner mỗi version; v2 candidate không là policy thay thế để vượt BLOCKED, không dùng cho effect hoặc đóng gói.
- Chỉ kích hoạt sau review contract/schema, amendment checker/integration (G-02-C2) và nghiệm thu baseline mới.
- Không grant/receipt/authority thật; hash chỉ nhận dạng bytes, không cấp quyền; không tự chuyển hồ sơ v1/unknown sang cơ sở hợp tác.
