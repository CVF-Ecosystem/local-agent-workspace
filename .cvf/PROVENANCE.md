# Nguồn thích nghi — chỉ dành cho người bảo trì

Ngày đối chiếu: 17/10/2026. Repo tham khảo local:
`D:\UNG DUNG AI\TOOL AI 2026\Controlled-Vibe-Framework-CVF`.
HEAD quan sát trong lượt G-00: `34318509b8937aaa39b7a0171ddd1366e9c276ff`.
Đây không phải chứng nhận cây CVF sạch, commit của LAW hoặc proof runtime.

| Owner CVF đã đọc phần liên quan | Phần thích nghi cho LAW |
|---|---|
| docs/reference/CVF_AGENT_DELEGATION_AND_SUBAGENT_BOUNDARY_STANDARD_2026-05-19.md | Delegation có giới hạn, không chuyển quyền quản trị cho worker |
| docs/reference/CVF_AGENT_ROLE_ASSIGNMENT_MATRIX_2026-05-19.md | Tách trách nhiệm/quyền/bằng chứng theo vai, topology không tạo quyền |
| docs/reference/CVF_GOVERNED_WORK_LIFECYCLE_AND_DESIGN_CONTROL_STANDARD_2026-06-11.md | Kiểm tính khả thi và điều kiện của pha trước tác động/approval |
| docs/reference/CVF_DISPATCH_RELEASE_READINESS_MACHINE_STANDARD_2026-09-25.md | Gắn dispatch vào đúng task/authority/revision, đưa kiểm lên trước handoff |
| docs/reference/CVF_TASK_PROPORTIONAL_GOVERNANCE_ROUTING_STANDARD_2026-08-17.md | Mức kiểm theo tác động/rủi ro, không tự hạ từ nhãn/độ nhỏ |
| docs/reference/CVF_AGENT_ERROR_TO_GOVERNANCE_LEARNING_PHILOSOPHY_2026-05-28.md | Truy chuỗi end-to-end, phân định lỗi Main/Worker/Reviewer/tool và điểm chặn sớm |
| docs/reviews/learnings/CVF_ORCHESTRATOR_PREAPPROVAL_FEASIBILITY_LEARNING_2026-10-08.md | Bài học packet/approval thuộc orchestrator; rule tồn tại khác với đã áp dụng/cưỡng chế |

LAW tự viết rules/contracts theo mục tiêu local của operator, chưa copy/import
code checker CVF. Không mang GC-ID, session state, work order, provider API gate,
hai-commit choreography hoặc registry CVF thành yêu cầu mặc định cho user LAW.
Mọi checker chọn đem sang sau này phải có phạm vi/dependency/license/proof được
đối chiếu, không nhận khả năng chỉ từ tên checker hoặc PASS trong repo nguồn.

User LAW không cần các đường dẫn trên. Rules/contracts phải tự đủ trong package;
thông tin này phục vụ truy nguồn khi bảo trì, không cấp authority cho Main hay
làm cho LAW tự nhận mức kiểm soát runtime của CVF.
