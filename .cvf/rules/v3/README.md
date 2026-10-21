# Candidate routing v3 — chưa kích hoạt

Trạng thái: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED / CANDIDATE_NOT_ACTIVE** (A0 hẹp, G-02-C2, 18/10/2026). Phần routing của amendment, cùng schema/contract candidate trong `.cvf/contracts/v3/`.
Chỉ nhận định nghĩa candidate; chưa evaluator routing/gate, chưa kích hoạt.

`ROUTING_POLICY.json` (`law.cvf.routing/3`, status `CANDIDATE_NOT_ACTIVE`) và `CONTROL_RULES.md` có cùng row IDs/trigger/gate/pha review/version.
Policy v1 ở thư mục cha và v2 ở `.cvf/rules/v2/` giữ nguyên. Không dùng candidate để tự hạ route hoặc tạo permit.
So với v2 chỉ đổi: R-READ_DRAFT (ba mệnh đề), R-MUTATION (thêm một mệnh đề), vùng/`light_write_zones`/mẫu authority, giả định mở A-NEW_TARGET và `owner_protocols` cho P-CN1, cộng một field khai báo `operational_context_protocol` cho P-CTX1 (ghi chú vận hành STATE/HANDOFF, không phải artifact, không evaluator). `assurance_ceiling = ADVISORY`, `tamper_resistance = NONE`.
Hiệu lực triển khai và mọi grant user phải được giải quyết qua owner tương ứng; cây này chưa cấp quyền.
