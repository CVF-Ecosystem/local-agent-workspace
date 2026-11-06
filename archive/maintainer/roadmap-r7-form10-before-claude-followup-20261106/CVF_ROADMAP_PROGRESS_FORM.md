# Biểu mẫu kiểm soát roadmap và tiến độ project

**Phiên bản:** 1.0 — 06/11/2026.

**Trạng thái:** dùng tại LAW theo chỉ định operator; ứng viên CVF `NOT_UPSTREAMED`.
Chưa là chuẩn canonical hoặc được tiếp nhận cho mọi project. Hiệu quả sử dụng chưa được chứng minh.

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
| Người chịu trách nhiệm và revision | [owner tích hợp, chủ sở hữu từng mốc, revision, trạng thái] |
| Điều kiện thay đổi | [ai có quyền chốt, cách ghi tác động và giữ quyết định cũ] |

Baseline là điểm đối chiếu, không phải bằng chứng sản phẩm đã đạt. Không tự hạ tiêu chí,
thay ngân sách, mở quyền hoặc mở lại phần đang giữ. Thiếu lựa chọn nghiệp vụ quan trọng thì
ghi cần xác nhận; quyết định kỹ thuật và QA thông thường thực hiện trong quyền đã có.

## 2. Bảng mốc và ánh xạ kiểm soát

Mỗi mốc mô tả kết quả người dùng nhận và **toàn bộ** điều kiện đạt theo nguồn đã chốt, kể cả
điều kiện ngoài phạm vi việc đang chọn. Tách hàng nếu nguồn, owner hoặc rủi ro cần theo dõi khác nhau.

| Kết quả / mốc; nguồn và toàn bộ điều kiện đạt | Quy tắc chung → kiểm soát project; trigger / owner | Bằng chứng, phiên bản và phạm vi | Thiếu / bị chặn / hoãn / chưa kiểm | Trạng thái; owner; phụ thuộc |
|---|---|---|---|---|
| [kết quả; nguồn; đủ điều kiện] | [quy tắc → lỗi cụ thể cần ngăn, hành động và kết quả kỳ vọng] | [đường dẫn hoặc định danh, kết quả thực tế, giới hạn] | [liệt kê từng phần còn lại và lý do] | [trạng thái, owner, phụ thuộc thực] |

`Đạt` chỉ khi mọi điều kiện tương ứng có bằng chứng phù hợp và người có trách nhiệm đã nhận
theo quy trình hiện hữu. `UNKNOWN`, `NOT_RUN`, `SKIP`, `FAILED`, `BLOCKED` và `DEFERRED` không
phải đạt. Nêu lý do, owner và hành động phụ thuộc bị giữ; blocker chỉ giữ phần thực sự phụ thuộc,
không tự chặn việc độc lập. Bằng chứng cục bộ chỉ chứng minh phạm vi đã kiểm: hash, kiểm tĩnh
hoặc fixture không tự chứng minh hành vi host thật, năng lực provider, toàn sản phẩm hay phát hành.

## 3. Chọn và giao việc

Trước mỗi lần giao hoặc tự nhận việc theo roadmap, trả lời trong hàng roadmap/HANDOFF hiện hữu:

1. **Kết quả:** Việc này phục vụ kết quả người dùng và mốc nào? Nguồn và toàn bộ điều kiện đạt là gì?
2. **Khoảng thiếu:** Điều gì đã đạt có bằng chứng, điều gì còn thiếu, bị chặn, hoãn hoặc chưa kiểm?
   Lần này đóng phần nào và toàn bộ phần nào vẫn còn sau bàn giao, kể cả ngoài phạm vi lần này?
3. **Dùng lại:** Bằng chứng, công cụ, skill hoặc khả năng native nào đã có và phù hợp? Hỗ trợ phát triển
   nào thực sự còn thiếu? Nêu giới hạn phiên bản, môi trường và quyền; không dựng trùng chỉ vì chưa tìm.
4. **Dừng và nhận:** Đầu ra và bằng chứng nào đủ để kết thúc, nghiệm thu phần được giao? Điều gì
   khiến công việc phụ thuộc phải dừng, chờ quyết định hoặc chuyển review? Phần nào
   độc lập vẫn tiếp tục được? Không tự đổi tiêu chí, quyền, ngân sách hay trạng thái bị giữ.

**Brief ngắn:** `[mốc + nguồn + toàn điều kiện] / [bằng chứng đã có và toàn gap] / [phần đóng +
toàn phần còn] / [scope, đầu ra, kiểm và review] / [owner tích hợp, người thực hiện, revision,
trạng thái] / [phụ thuộc, điểm dừng, quyền]`. Khi có ghi đồng thời hoặc lượt tốn phí, thêm phạm vi
sole writer, trạng thái các owner, cách kiểm revision ngay trước tác động, giới hạn retry và chi phí
được duyệt. Revision đổi, bị thu hồi hoặc phạm vi ghi chồng thì dừng phần phụ thuộc và báo owner;
không mặc định người đang chạy đã dừng. Không retry mù hoặc tự tăng ngân sách.

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
| Mốc sản phẩm | [đối chiếu từng điều kiện với bằng chứng; toàn gap và trạng thái hiện tại] |
| Phát hành | [gate, artifact chính xác, lifecycle, quyền và quyết định phát hành theo project; phần chưa đạt] |

Hoàn thành một việc hoặc một phép kiểm không tự đóng mốc; đạt một mốc không tự cho phép phát hành.
Không lấy số test, file, lượt gọi hoặc tranche hoàn thành làm phần trăm sản phẩm. Nếu dùng phần trăm,
phải có tập điều kiện và cách tính đã chốt; luôn kèm phần bắt buộc còn thiếu, không để điểm tổng che blocker.
Giữ bằng chứng cũ còn hợp lệ theo đúng phạm vi, ghi hành động tiếp theo có căn cứ và owner trong
roadmap/HANDOFF hiện hữu. Không suy `PASS` từ thiếu dữ liệu hoặc từ tuyên bố của host chưa được kiểm.

## Nguồn và tiếp nhận ứng viên

- Nguồn bổ sung đã tham chiếu: `CVF_PROJECT_DEVELOPMENT_APPLICATION_STANDARD.md`, operator-local
  manifest, source commit `f8175616c`; SHA-256
  `d06b62387e015160a77658f333882a2a316d54ffd0421071354cf63a3730dd7a` (theo brief W44/r6.22).
- Chuẩn chung giữ authority tại lifecycle/design-control và product milestone coverage hiện hữu;
  mapping do maintainer/orchestrator project sở hữu. Đích đề nghị tiếp nhận: owner
  `docs/reference/downstream_gate_profile/CVF_PROJECT_DEVELOPMENT_APPLICATION_STANDARD.md`
  cùng `docs/reference/CVF_PRODUCT_MILESTONE_COVERAGE_CONTRACT_2026-10-23.md` trong CVF;
  maintainer CVF đối chiếu trùng/gap và quyết định hợp nhất hoặc tham chiếu form. Chưa có quyết định
  tiếp nhận hoặc cập nhật nguồn canonical; file này không tự upstream.
- Đây là quy tắc hợp tác và mẫu sử dụng cục bộ, không chứng minh host tự nạp, thực thi toàn bộ,
  hay LAW runtime hoặc sản phẩm đã đạt. Việc tiếp nhận ở project khác cần theo authority của project đó.
