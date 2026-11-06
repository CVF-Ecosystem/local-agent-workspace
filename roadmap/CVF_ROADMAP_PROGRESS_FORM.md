# Biểu mẫu kiểm soát roadmap và tiến độ project

Memory class: FULL_RECORD
Status: ACTIVE_REFERENCE
docType: reference
Date: 2026-11-06

**Phiên bản:** 1.2 (hiệu chỉnh 1) — 06/11/2026; làm rõ F1–F7 sau đối chiếu chuẩn.

**Bản tiếp nhận tại LAW:** nguồn CVF commit `feb691726a3be5bd4b3ac4dc402d22c69bc79235`, SHA-256 `3f0917927e46f24212f80e1b6a8579067c2e0c21fad9d17ec34f719f77733c78`; bản sao v1.2 hiệu chỉnh 1 với liên kết trỏ tới kho CVF cục bộ. Core pin/profile/quyền hiện hữu không đổi.

## Purpose

Mẫu CVF dùng chung để nối **kết quả người dùng → thiếu hụt thực tế → năng lực tái dùng →
điều kiện nhận/dừng** trong hồ sơ project. Tiếp nhận từ form LAW v1.1 theo yêu cầu operator;
v1.2 bổ sung chi phí lũy kế, vai trò/thời điểm quyết định, tham chiếu tiêu chí và căn cứ chất lượng.

## Scope / Owner

Maintainer/orchestrator áp dụng trong roadmap/HANDOFF hiện hữu theo quyền của project.
Đây là mẫu thực hành dưới các chuẩn CVF được dẫn ở cuối, không phải chuẩn quản trị độc lập.
Hiệu quả sử dụng chưa được chứng minh; tiếp nhận mẫu không đồng nghĩa mọi project đã áp dụng.

## Cách dùng

Người điều phối duy trì baseline, ánh xạ mốc và bằng chứng trong roadmap, hồ sơ thiết kế hoặc
HANDOFF hiện có. Dùng một đoạn ngắn cho việc nhỏ, bảng khi có nhiều rủi ro; không cần tạo file
hay sổ mới cho từng việc. Điền theo yêu cầu và quyền thực tế của project; không áp số lượng
mốc, phép thử hay chức năng của một project cho project khác. Quy tắc, gate và quyền hiện hữu
tiếp tục áp dụng; biểu mẫu này không tự cấp quyền, kích hoạt runtime hoặc thay tiêu chí đã chốt.

Nối ba lớp: **quy tắc chung → kiểm soát cụ thể của project → bằng chứng công việc**. Ghi nguồn,
phiên bản và phạm vi; không chép toàn bộ quy tắc chung. Chức năng nghiệp vụ riêng, tiêu chí và
chủ sở hữu của chúng nằm tại roadmap project. Người dùng quyết định nghiệp vụ; đội phát triển
chịu trách nhiệm thiết kế, QA và review cần thiết trước khi giao kết quả dùng được.

## 1. Baseline project

| Nội dung | Điền theo nguồn đã xác nhận |
|---|---|
| Kết quả người dùng cần và cách nhận biết | [kết quả, người dùng và nguồn yêu cầu] |
| Phạm vi / ngoài phạm vi | [bao gồm; không bao gồm; phần đang giữ hoặc hoãn] |
| Hỗ trợ và môi trường dự kiến | [host, provider, nền tảng, giới hạn đã xác nhận; chưa biết ghi rõ] |
| Chuẩn, tiêu chí và quyền áp dụng | [nguồn, revision, phạm vi, tiêu chí nhận, authority quyết định] |
| Thời hạn / ngân sách đã duyệt | [giá trị, đơn vị, phạm vi và nguồn quyết định nếu có; chưa có ghi rõ, không suy thành quyền chi hoặc giới hạn vô hạn] |
| Người chịu trách nhiệm và revision | [owner tích hợp, chủ sở hữu từng mốc, revision, trạng thái] |
| Điều kiện thay đổi | [ai có quyền chốt, cách ghi tác động và giữ quyết định cũ] |
| Điểm rà soát | [trigger: ngày/đầu ra/hết ngân sách/thay đổi lớn; evidence cần có; owner quyết định; lựa chọn: tiếp tục, sửa trong quyền, đổi qua scope owner, giữ hoặc dừng] |

Baseline là điểm đối chiếu, không phải bằng chứng sản phẩm đã đạt. Không tự hạ tiêu chí,
thay ngân sách, mở quyền hoặc mở lại phần đang giữ. Thiếu lựa chọn nghiệp vụ quan trọng thì
ghi cần xác nhận; quyết định kỹ thuật và QA thông thường thực hiện trong quyền đã có.
Tại mỗi điểm rà soát, ghi quyết định thực tế và căn cứ. Trễ hạn phải công bố; không âm thầm dời ngày.

## 2. Bảng mốc và ánh xạ kiểm soát

Mỗi mốc mô tả kết quả người dùng nhận và **toàn bộ** điều kiện đạt theo nguồn đã chốt, kể cả
điều kiện ngoài phạm vi việc đang chọn. Gán ID ổn định cho mốc/tiêu chí (ví dụ M1/C1), kèm
nguồn và revision. Project chưa có bảng coverage thì dùng bảng dưới đây làm bảng chính
trong roadmap/HANDOFF hiện hữu. Đã có bảng chính thì mục này chỉ dẫn ID, revision/section
và liên kết tới bảng đó; bổ sung trường thiếu ngay tại bảng chính, không chép thành bảng thứ hai.
Mỗi tiêu chí xuất hiện một lần trong bảng chính; brief dẫn ID và delta. Nhiều việc cùng
tham chiếu một tiêu chí phải phân biệt bằng chứng và trách nhiệm còn lại của từng việc.
Khi nguồn đổi, đánh giá lại các bằng chứng và công việc bị ảnh hưởng; tách hàng khi cần,
nhưng không tạo bản sao trạng thái cho cùng tiêu chí.

| ID tiêu chí / mốc; kết quả, nguồn và toàn bộ điều kiện đạt | Quy tắc chung → kiểm soát project; trigger / owner | Bằng chứng, phiên bản và phạm vi | Gap; owner phần còn; nơi chuyển / điều kiện quay lại | Trạng thái tiêu chí; việc đang xử lý; phụ thuộc |
|---|---|---|---|---|
| [ID tiêu chí; ID mốc; kết quả; nguồn/revision/link; đủ điều kiện] | [quy tắc → lỗi cụ thể cần ngăn, hành động và kết quả kỳ vọng] | [đường dẫn hoặc định danh, kết quả thực tế, giới hạn] | [từng gap và lý do hoặc không còn gap kèm căn cứ; owner chịu trách nhiệm; ID/link việc hoặc checkpoint cụ thể và trigger quay lại] | [một trạng thái chuẩn; ID việc đang xử lý hoặc ngoài lượt này; phụ thuộc thực] |

Phần còn ngoài việc đang chọn vẫn phải có owner và đích cụ thể; chỉ ghi tên vai trò hoặc
“để sau/backlog” là chưa đủ. Nơi chuyển không làm tiêu chí biến mất khỏi mốc.

Trạng thái tiêu chí chỉ dùng: `NOT_STARTED` (chưa bắt đầu), `IMPLEMENTED_UNPROVED` (đã làm,
chưa đủ chứng minh), `VERIFIED` (đủ evidence đúng phiên bản và vai trò nghiệm thu yêu cầu),
`BLOCKED` (bị chặn), `UNKNOWN` (chưa xác định). “Đạt” là cách đọc `VERIFIED` sau khi người
có quyền đã nhận theo quy trình áp dụng; kiểm kỹ thuật không thay nghiệm thu nghiệp vụ.
`NOT_RUN`, `SKIP`, `FAILED` là kết quả của lần kiểm, không phải trạng thái tiêu chí;
ghi riêng trong evidence, rồi xác định trạng thái tiêu chí theo toàn bộ bằng chứng hiện còn hợp lệ.
`DEFERRED` là disposition hoãn việc/phạm vi theo quyền hiện hữu, không phải trạng thái tiêu chí.
Hoãn việc vẫn giữ tiêu chí và gap trong mốc; chỉ loại khỏi phạm vi đã chốt khi có quyết định của scope owner,
qua mục 4. Không dùng hoãn hoặc đổi tranche để xóa điều kiện bắt buộc.

Nêu lý do, owner và hành động phụ thuộc bị giữ. Việc khác chỉ được tiếp tục khi Local đã
quyết định và ghi căn cứ nguồn chứng minh gap/unknown không ảnh hưởng tới kết quả, điều kiện
trước, phạm vi, quyền hoặc nghiệm thu của việc đó; thiếu căn cứ thì giữ phần thi công phụ thuộc.
Bằng chứng cục bộ chỉ chứng minh phạm vi đã kiểm: hash, kiểm tĩnh hoặc fixture không tự
chứng minh hành vi host thật, năng lực provider, toàn sản phẩm hay phát hành.

`Đạt có giới hạn` (`ACCEPT_WITH_LIMITS`/`WITH_LIMITS`) là verdict nhận phần có evidence
trong phạm vi nêu rõ, không phải trạng thái tiêu chí thứ sáu. Phần ngoài giới hạn ghi vào gap;
mốc còn bất kỳ điều kiện bắt buộc nào thiếu thì chưa đạt. Verdict không tự thu hẹp tiêu chí
hoặc thay quyết định đổi baseline.

Với kết luận chất lượng, ghi hoặc dẫn căn cứ của **kết quả kỳ vọng** đã xác lập trước khi
kiểm (yêu cầu, nguồn đã kiểm hoặc chuyên môn phù hợp), artifact/revision thực giao,
môi trường và luồng đã kiểm, kết quả thực tế so với kỳ vọng và người nhận theo quyền hiện có.
Không lấy sự đồng ý giữa các AI làm căn cứ duy nhất; chỗ thiếu căn cứ giữ `UNKNOWN`.
Dẫn lại evidence hợp lệ trong hồ sơ hiện có; không tạo sổ kiểm riêng hoặc chạy lại chỉ để điền form.

<a id="chon-va-giao-viec"></a>
## 3. Chọn và giao việc

**Trước khi giao hoặc tự nhận việc**, Main agent trong vai Orchestrator quyết định sự cần thiết,
đóng góp vào mốc và phạm vi trong quyền hiện có; ghi ngắn trong hàng roadmap/HANDOFF.
Reviewer đối chiếu lại quyết định này cùng chất lượng và chứng cứ khi nhận kết quả.
Review trước thi công chỉ khi rủi ro hoặc gate hiện hữu yêu cầu; không thêm vòng xin phép mặc định.
Nêu người review/người nhận theo quy trình áp dụng, hoặc lý do tự kiểm khi được phép.

**Điều kiện giao thi công:** chưa có bảng coverage thì không giao triển khai. Intake/lập
kế hoạch vẫn theo quyền hiện có; thiếu coverage hoặc tiêu chí được chọn còn `UNKNOWN`
chỉ cho phép kiểm tra hữu hạn để làm rõ: câu hỏi, ranh giới nguồn, đầu ra, owner, trần công
sức/lượt chạy, điểm dừng và quyết định theo kết quả. Hết trần trả phần chưa rõ về người
quyết định, không tự gia hạn hoặc mở tranche kế tiếp. Tiêu chí `UNKNOWN` ngoài lượt này
chỉ cho phép thi công phần khác khi đã ghi quyết định độc lập có căn cứ nguồn như mục 2.
Project đã áp Machine Contract giữ cả khai báo độc lập và evidence pin theo contract đó.

Trả lời bốn câu hỏi sau bằng ID/liên kết tới bảng coverage hiện hành và delta của lần này:

1. **Kết quả:** Việc này phục vụ kết quả người dùng và mốc nào? Nguồn và toàn bộ điều kiện đạt là gì?
2. **Khoảng thiếu:** Điều gì đã đạt có bằng chứng, điều gì còn thiếu, bị chặn, hoãn hoặc chưa kiểm?
   Lần này đóng phần nào và toàn bộ phần nào vẫn còn sau bàn giao, kể cả ngoài phạm vi lần này?
3. **Dùng lại:** Bằng chứng, công cụ, skill hoặc khả năng native nào đã có và phù hợp? Hỗ trợ phát triển
   nào thực sự còn thiếu? Nêu giới hạn phiên bản, môi trường và quyền; không dựng trùng chỉ vì chưa tìm.
4. **Dừng và nhận:** Đầu ra và bằng chứng nào đủ để kết thúc, nghiệm thu phần được giao? Điều gì
   khiến công việc phụ thuộc phải dừng, chờ quyết định hoặc chuyển review? Phần nào
   độc lập vẫn tiếp tục được? Không tự đổi tiêu chí, quyền, ngân sách hay trạng thái bị giữ.

**Brief ngắn:** `[ID mốc/tiêu chí + nguồn/revision/link coverage] / [gap được chọn + delta;
link toàn phần còn] / [native/bằng chứng dùng lại + thiếu hụt cần làm] / [scope, đầu ra,
kiểm/review/người nhận] / [owner tích hợp, người thực hiện, revision, trạng thái] /
[chi phí nhánh, trần thêm, phương án đủ dùng rẻ hơn, điểm dừng] / [phụ thuộc, quyền]`. Khi có ghi đồng thời hoặc lượt tốn phí, thêm phạm vi
sole writer, trạng thái các owner, cách kiểm revision ngay trước tác động, giới hạn retry và chi phí
được duyệt. Revision đổi, bị thu hồi hoặc phạm vi ghi chồng thì dừng phần phụ thuộc và báo owner;
không mặc định người đang chạy đã dừng. Không retry mù hoặc tự tăng ngân sách.

**Giá trị và chi phí khi tiếp tục:** ghi công sức/chi phí đã quan sát trên cùng nhánh kết quả
(gồm chuẩn bị, thực hiện, retry và review), trần bổ sung cho lần này, đơn vị/phạm vi và nguồn
quyết định; phần chưa đo ghi `UNKNOWN`, không tự quy đổi thành tiền. Nêu ngắn vì sao chọn
cách này so với phương án đủ dùng ít tốn hơn. Không cần sổ ROI riêng.
Dừng kéo dài nhánh khi hết trần, không tạo đóng góp đã hứa, chuẩn bị nối tiếp chuẩn bị hoặc
giá trị không còn tương xứng. Giữ lịch sử thất bại/chi phí; mở lại cần bằng chứng mới hoặc
cách làm đổi đúng nguyên nhân dừng, đóng góp dự kiến và trần thêm trong cùng brief, theo
quyền hiện hữu. Đổi tên tranche không làm mới ngân sách; phần độc lập được phép vẫn tiếp tục.

Người thực hiện chủ động chọn cách làm trong phạm vi và quyền được giao, trả lại brief thiếu hoặc
mâu thuẫn trước tác động phụ thuộc; báo kết quả thực tế, giới hạn và phần còn. Review theo rủi ro
và gate hiện hữu, có độc lập khi được yêu cầu; reviewer xét việc có cần thiết cho kết quả hay không
cùng tính đúng kỹ thuật và chứng cứ. Review không cấp quyền hoặc thay quyết định nghiệp vụ.

## 4. Đề nghị thay đổi

| Giá trị / quyết định cũ và nguồn | Đề nghị mới; lý do | Tác động tới kết quả, tiêu chí, phạm vi, bằng chứng, phụ thuộc, quyền và chi phí | Authority và trạng thái |
|---|---|---|---|
| [baseline/revision] | [đề nghị và căn cứ] | [ảnh hưởng; phần giữ, việc bị giữ hoặc cần kiểm lại] | [ai có quyền; pending / đã quyết định; nguồn quyết định] |

Đề nghị `PENDING` chưa có hiệu lực. Chỉ cập nhật baseline khi có quyết định của đúng authority;
giữ dấu vết, bằng chứng và trạng thái cũ, đánh giá lại các phần phụ thuộc. Không biến ngoại lệ
thành thay đổi đã được chấp nhận chỉ vì công việc đã chạy.

## 5. Kết thúc và tiếp nối

| Cấp kết luận | Ghi nhận |
|---|---|
| Việc / tranche | [đã làm, kết quả và revision, bằng chứng, kiểm/review, phần chưa kiểm] |
| Sẵn sàng nội bộ của mốc / sản phẩm | [đội phát triển đối chiếu tiêu chí kỹ thuật/chất lượng với evidence đúng bản, luồng dùng thực và review cần thiết; owner xác nhận; toàn gap và trạng thái] |
| Người dùng nhận / nghiệm thu nghiệp vụ | [feedback về phù hợp nhu cầu; người có quyền và quyết định/evidence thực tế hoặc chưa nhận; gap còn lại] |
| Phát hành | [gate, artifact chính xác, lifecycle, quyền và quyết định phát hành theo project; phần chưa đạt] |

Đội phát triển phải chứng minh sẵn sàng nội bộ trước khi xin feedback sử dụng sản phẩm;
noncoder không chịu QA kỹ thuật thay đội phát triển. Sẵn sàng nội bộ, nghiệm thu nghiệp vụ
và quyền phát hành là ba quyết định riêng; không suy quyết định này từ quyết định kia.
Kết luận mốc vẫn đối chiếu toàn bộ điều kiện bắt buộc và mọi lớp nghiệm thu áp dụng.
Hoàn thành một việc hoặc một phép kiểm không tự đóng mốc; đạt một mốc không tự cho phép phát hành.
Không lấy số test, file, lượt gọi hoặc tranche hoàn thành làm phần trăm sản phẩm. Nếu dùng phần trăm,
phải có tập điều kiện và cách tính đã chốt; luôn kèm phần bắt buộc còn thiếu, không để điểm tổng che blocker.
Giữ bằng chứng cũ còn hợp lệ theo đúng phạm vi, ghi hành động tiếp theo có căn cứ và owner trong
roadmap/HANDOFF hiện hữu. Không suy `PASS` từ thiếu dữ liệu hoặc từ tuyên bố của host chưa được kiểm.

## Source Lineage / Nguồn và tiếp nhận

- Operator yêu cầu tiếp nhận vào CVF và tạo v1.2 ngày 06/11/2026. Local maintainer nhận
  dưới dạng mẫu áp dụng; authority vẫn ở các chuẩn bên dưới. Bản LAW v1.1 được giữ nguyên
  bytes tại [snapshot v1.1](<D:/UNG DUNG AI/TOOL AI 2026/Controlled-Vibe-Framework-CVF/docs/reference/archive/LAW_ROADMAP_PROGRESS_FORM_v1.1_2026-11-06.md.txt>),
  SHA-256 `fcb92c850f1a296e222bb03ab76dc15020943ef6d474dc1a880607773c117164`.
- Hiệu chỉnh 1 xử lý F1–F7: thống nhất trạng thái tiêu chí, đích phần còn, một bảng chính,
  điều kiện độc lập/kiểm hữu hạn, checkpoint, tách quyết định nghiệm thu và sửa tham chiếu.
  Bản v1.2 trước hiệu chỉnh giữ trong Git tại commit `23a27ba62797e1f5fb4efd0f671de91ab3d293e0`.
- Định danh nguồn v1.2: `docs/reference/downstream_gate_profile/CVF_ROADMAP_PROGRESS_FORM.md`.
  Project ghi phiên bản, commit/hash thực nhận trong hồ sơ hiện có; đây là nguồn bổ sung,
  không tự thay Core pin, profile, quyền hoặc bằng chứng nghiệm thu của project.
- Đối chiếu nội dung: baseline/ánh xạ/brief dùng Project Development Application;
  ID/toàn coverage, chi phí/điểm dừng và căn cứ chất lượng dùng Product Milestone Coverage;
  quyền và mức sẵn sàng theo hành động dùng Lifecycle/Design Control. Phần bổ sung là cách
  trình bày các nghĩa vụ đã có; không thêm checker, phase hay lớp phê duyệt.

## Related Artifacts

- [Project Development Application](<D:/UNG DUNG AI/TOOL AI 2026/Controlled-Vibe-Framework-CVF/docs/reference/downstream_gate_profile/CVF_PROJECT_DEVELOPMENT_APPLICATION_STANDARD.md>).
- [Product Milestone Coverage](<D:/UNG DUNG AI/TOOL AI 2026/Controlled-Vibe-Framework-CVF/docs/reference/CVF_PRODUCT_MILESTONE_COVERAGE_CONTRACT_2026-10-23.md>),
  các mục Milestone Coverage Reconciliation, Continuation Value And Cumulative Cost Decision và
  Development-Owned Internal Readiness Before User Feedback.
- [Milestone Coverage Machine Contract](<D:/UNG DUNG AI/TOOL AI 2026/Controlled-Vibe-Framework-CVF/docs/reference/downstream_gate_profile/CVF_MILESTONE_COVERAGE_MACHINE_CONTRACT.md>),
  khi project áp dụng registry/coverage block dạng máy đọc.
- [Lifecycle / Design Control](<D:/UNG DUNG AI/TOOL AI 2026/Controlled-Vibe-Framework-CVF/docs/reference/CVF_GOVERNED_WORK_LIFECYCLE_AND_DESIGN_CONTROL_STANDARD_2026-06-11.md>),
  Agent Continuation And Action Readiness.

## Claim Boundary

Tiếp nhận tài liệu không chứng minh host tự nạp, agent tuân thủ, hiệu quả giảm chi phí,
runtime hay sản phẩm đạt. Các kết luận cần evidence riêng theo phạm vi đã kiểm.

## Public Export Disposition

DEFERRED_PRIVATE_ONLY

## Text Encoding Exception

UTF-8 tiếng Việt để giữ ngôn ngữ form gốc và đáp ứng yêu cầu operator; snapshot là dữ liệu
nguồn lịch sử, không phải chỉ thị hiện hành.
