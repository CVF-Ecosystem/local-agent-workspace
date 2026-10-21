# Candidate routing v2 — chưa kích hoạt

Trạng thái: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED** (G-01-C1, 18/10/2026). Phần routing của amendment, cùng schema/contract candidate trong `.cvf/contracts/v2/`.
Chỉ nhận định nghĩa candidate; nền G-02-C2/S1 đã đọc/validate policy v2, chưa evaluator routing/gate hoặc kích hoạt.

`ROUTING_POLICY.json` (`law.cvf.routing/2`, status `CANDIDATE_NOT_ACTIVE`) và `CONTROL_RULES.md` có cùng row IDs/trigger/gate/pha review/version.
Policy v1 ở thư mục cha giữ nguyên cho checker hiện tại. Không dùng candidate để tự hạ route hoặc tạo permit.
Chỉ trường quyền đổi (lớp nguồn chấp nhận thay cho trusted refs); `assurance_ceiling = ADVISORY`. Hiệu lực triển khai và mọi grant user phải được giải quyết qua owner tương ứng; cây này chưa cấp quyền.
