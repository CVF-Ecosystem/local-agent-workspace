# Hồ sơ nghiệm thu gói / Pack acceptance record

Mẫu chưa điền / UNFILLED TEMPLATE — không phải verdict hoặc bằng chứng đã chạy / not a verdict or execution evidence.
Điền vào hồ sơ này; không tạo thêm sổ. Bám đủ sáu điều kiện tại `skills/README.md`. / Complete this record against all six intake conditions; no separate ledger.

- Gói/skill, version/revision/hash / Pack/skill and revision: [cần điền / required]
- Owner tích hợp, người kiểm/reviewer và ngày / Integration owner, assessor/reviewer and date: [cần điền / required]
- Mốc sản phẩm, phạm vi cam kết, thiếu gì / Milestone, committed scope and remaining gaps: [cần điền / required]
- Quyết định intake / Intake decision: [chưa quyết định / not decided; use existing schema codes only]
- Quyền cài/confirm/publish riêng / Separate install/confirm/publish authority: [cần xác định / identify]

## 1. Làm việc gì, kích hoạt khi nào? / Job and trigger

Ghi yêu cầu user nào kích hoạt; đầu vào/đầu ra; lúc không dùng; đích project/shared; dữ liệu riêng phải tách. / State triggering user requests, inputs/outputs, exclusions, project/shared scope and private data to separate.

## 2. Thế nào là đầu ra đạt? / Output standard

Đặt tiêu chí nội dung trước khi thử; giới hạn và hành vi khi thiếu nguồn/thông tin/quyền hoặc sai dữ liệu. Ghi xuất xứ, version, điều khoản dùng, quyền đọc/ghi, script/dependency/network/cost. Nguồn có thể đổi: ngày đối chiếu, điều chưa xác minh và trigger/ngày kiểm lại; không tự nhận hiệu lực. Quá hạn mà chưa kiểm lại: đầu ra ghi "chưa kiểm lại từ <ngày>" (không biết ngày thì ghi chưa biết); nội dung thận trọng cao không coi đó là căn cứ hiện hành. / Set content criteria before testing, limits and missing-source/input/permission or invalid-data behaviour. Record provenance, revision, usage terms, read/write permissions, scripts/dependencies/network/cost. For changeable sources, record check date, unresolved verification and recheck trigger/date; do not assume validity. For overdue unchecked sources, state "not rechecked since <date>" in the output (unknown if unknown); do not treat them as current authority for high-consequence claims.

## 3. Đã chứng minh bằng gì? / Evidence

Mỗi ca: input/source revision → expected có căn cứ → actual/output locator → PASS/FAIL/NOT_TESTED và reviewer/giới hạn. Có ca đại diện, thiếu dữ liệu và lỗi theo rủi ro; đo số/định dạng khi áp dụng. Phân biệt regression với ca chưa dùng chỉnh skill; AI tự đồng ý không là oracle duy nhất. Chỉ phần cần phán đoán chuyên ngành cần thẩm định: dev chuẩn bị ca/nguồn/rubric; operator quyết định người duyệt/ngân sách khi thiếu quyền. Chưa đủ thì giữ claim bị chặn, không tự thuê hoặc tự chứng nhận. / For each case record revision-bound inputs, grounded expectations, actual output locator, verdict and review/limits. Cover representative, missing-input and risk-based failure cases, measurable numbers/formats where applicable. Separate regression from cases not used for tuning. AI self-agreement is not a sole oracle; developers prepare cases/sources/rubrics for qualified domain assessment; the operator decides the assessor/budget where authority is missing. Keep dependent claims blocked; do not self-hire or self-certify.

## 4. Phần tăng thêm cụ thể là gì? / Specific added value

Một câu giá trị so với cách hiện có; evidence đúng claim. Nếu trùng native, đối chiếu công bằng theo chuẩn hiện hành; không hạ năng lực baseline. / One concrete value claim over the current approach, with supporting evidence. Duplicates require the existing fair native comparison without weakening the baseline.

## 5. Bản giao dùng được ở đâu, qua luồng nào? / Delivered workflow and environment

Ghi artifact/revision, OS/Python/host/model/công cụ/format thật đã thử, requested khác observed. Chưa thử ghi NOT_TESTED. Ghi luồng project mới và nâng cấp nếu công bố hỗ trợ: cài gói → làm việc → kiểm đầu ra; bảo toàn file/quyền/native, xung đột và phục hồi theo phạm vi. Không lấy check cấu trúc làm bằng chứng toàn luồng. / Identify the exact artifact and tested OS/Python/host/model/tools/formats; distinguish requested from observed. Mark untested entries NOT_TESTED. Cover new and upgrade workflows when supported: install, perform the job, check output; preserve files/permissions/native state and assess scoped conflicts/recovery. Structure checks do not prove end-to-end readiness.

## Kết luận đủ sáu điều kiện / Six-condition disposition

Dùng PASS / FAIL / NOT ENOUGH EVIDENCE; mỗi hàng dẫn ca/nguồn thật. Không bỏ cả điều kiện; subcheck không áp dụng cần lý do. / Each row needs actual evidence; do not drop a whole condition. Inapplicable subchecks need reasons.

| Điều kiện / Condition | Kết quả / Result | Evidence và thiếu gì / Evidence and gaps |
|---|---|---|
| 1. Nhu cầu/phần tăng thêm / Need/value (Q1,Q4) | NOT ENOUGH EVIDENCE | [điền / fill] |
| 2. Xuất xứ / Origin (Q2) | NOT ENOUGH EVIDENCE | [điền / fill] |
| 3. Quyền/an toàn / Permissions/safety (Q2,Q5) | NOT ENOUGH EVIDENCE | [điền / fill] |
| 4. Hiệu quả / Effect (Q3,Q4) | NOT ENOUGH EVIDENCE | [điền / fill] |
| 5. Dùng được/bảo toàn / Usability/preservation (Q3,Q5) | NOT ENOUGH EVIDENCE | [điền / fill] |
| 6. Tái dùng / Reuse scope (Q1,Q5) | NOT ENOUGH EVIDENCE | [điền / fill] |

Kiểm kỹ thuật, nghiệm thu sản phẩm của dev, feedback nghiệp vụ và quyền tiếp nhận/phát hành ghi riêng; không lấy confirm thay QA hoặc thiếu feedback làm lý do chưa tự kiểm. Nêu phần đạt, còn thiếu, bị chặn/hoãn của toàn mốc; không tự bỏ scope để ship. / Keep technical checks, developer product acceptance, business feedback and adoption/release authority distinct. Confirmation is not QA; pending feedback does not excuse missing internal checks. State all milestone gaps without silently dropping committed scope to ship.
