# Hướng dẫn điều phối pilot C-02 (chỉ người điều phối và quan sát; không đưa cho người thử)

**Trạng thái: PREPARATION_ONLY, PILOT_NOT_RUN.** Chưa có người thử. Bộ này chưa là kết quả T37–T38, chưa chứng minh người mới dùng được
hay LAW tốt hơn native, và không thay cho nghiệm thu của người dùng. Phạm vi và giới hạn của lượt chuẩn bị:
[WORKORDER_C02_PREP_2026-10-20.md](../../../roadmap/WORKORDER_C02_PREP_2026-10-20.md). Thư mục `feedback/` nằm ngoài gói phát hành
([README](../../README.md)). Ba file của bộ: [NGUOI_THU.md](NGUOI_THU.md) (đưa cho người thử), file này, [PHIEU_GHI_NHAN.md](PHIEU_GHI_NHAN.md) (trống).

**Tiếp V6 sau Prototype/MVP — 24/10/2026:** dùng lại bộ C-02 này trên RC4 Windows DATAMOCK đã công bố, không mở pilot/tranche hoặc benchmark mới. Operator trả lời "chưa có" người thử; giữ `PILOT_NOT_RUN`, không mời, không chạy host hoặc phát sinh chi phí. Operator đã là observer; người thử phải là người thật chưa từng dùng LAW, không lấy agent hoặc observer thay. Liên kết acceptance V6: Việc2 ghi khả năng tiếp phiên/đúng revision; Việc3 và DL7–DL9 ghi cách dùng lại và cách ly B; cảm nhận/nghiệm thu chỉ do người thật cung cấp. Các bằng chứng kỹ thuật V6/V7 đã nhận được tái dùng, không chạy mock lại. Chưa có dữ liệu hành vi hoặc kết luận usability.

## 1. Gate trước khi chạy

Thiếu một dòng dưới đây thì trạng thái giữ NOT_RUN: không mời, không chạy host, không phát sinh chi phí.

| # | Điều kiện | Hiện tại |
|---|---|---|
| G1 | Có người thử thật, chưa từng dùng LAW, đã đồng ý bằng ngôn ngữ dễ hiểu (xem NGUOI_THU) | Operator24/10: chưa có người |
| G2 | Môi trường và giới hạn đã xác nhận (mục 2) | Cần xác nhận |
| G3 | Snapshot candidate và nguồn đã freeze, có hash (mục 3) | RC4/3nguồnA đã đối chiếu; chưa tạo/freeze cây pilot, nguồnB chưa tạo |
| G4 | Thư mục pilot tách biệt cho từng nhánh và việc (mục 4) | Chưa tạo |
| G5 | Oracle đã đối chiếu, thứ tự và phạm vi diễn giải theo mục 5; người quan sát đã hiểu | Chưa phổ biến |
| G6 | Người quan sát biết cách ghi hỗ trợ (mục 8) | Chưa phổ biến |
| G7 | Tệp nguồn B (mục 3) đã tạo trong thư mục pilot và có hash | Chưa tạo |

File profile hoặc receipt không chứng minh host đã nhận vai; không bảo người thử viết schema, grant hay trust anchor để vượt gate.
Môi trường bị chặn (ví dụ thiếu Python, ứng dụng không mở được thư mục): người quan sát ghi lại đúng thông báo người thử nhìn thấy,
bằng lời của họ, cùng phần chưa kiểm, và mốc đó là "chưa đánh giá". Không sửa sản phẩm để vượt chặn trong buổi thử.

## 2. Điều kiện triển khai và quyết định thiết kế

Orchestrator đã chốt thiết kế khám phá bên dưới. Chưa có người thử nên không chạy; operator chỉ cần cung cấp lựa chọn thực tế về người, môi trường và giới hạn. Không yêu cầu xác nhận lại từng quy ước kỹ thuật. Quyết định thiết kế không cấp quyền chạy host hay phát sinh chi phí.

| # | Nội dung | Đã chốt hoặc còn cần xác nhận |
|---|---|---|
| Q1 | Người thử: tuyển ai, mã ẩn danh, mức quen tự khai | Không tự gán người; không thu dữ liệu cá nhân |
| Q2 | Host/ứng dụng, loại account, model, effort, OS | Dùng cùng cấu hình cho hai nhánh nếu khả dụng; effort chỉ ghi nếu quan sát được |
| Q3 | Người quan sát và lịch chạy | Operator là observer theo chỉ định đã chốt; lịch chưa có, không hỏi lại vai này |
| Q4 | Giới hạn thời lượng và chi phí cho phép | Operator chốt trước chạy. Pilot khám phá không có ngưỡng điểm tổng hoặc quyết định LAW thắng native; chấm theo bằng chứng từng tiêu chí |
| Q5 | Thư mục gốc pilot và freeze artifact | Chọn vị trí thuộc quyền chạy; điều phối ghi thời điểm/hash thực tế, ngoài kho nguồn và snapshot; không cần user phê duyệt từng hash |
| Q6 | Thiết kế hai nhánh | Đã chốt lượt đầu là khám phá định tính: L trước, N sau, dùng cùng nguồn; không soạn bộ thứ hai trong PREP này. Không tính chênh lệch thành hiệu quả LAW. Nghiên cứu so sánh mạnh hơn cần scope và oracle mới trước khi chạy |
| Q7 | Vị trí nguồn | Đã chốt: A ở `examples/demo-project/`, B ở `references/source-documents/`, cùng đường dẫn tương đối và bytes cho L/N. Điều phối kiểm thực trước mỗi lượt |
| Q8 | Rò đáp án qua tài liệu | Không sửa/xóa README mẫu. Nếu người thử hoặc AI đã thấy phần đáp án trong README hoặc tài liệu điều phối, tiêu chí nội dung liên quan phải ghi không đánh giá được về tính độc lập (mục 5); không chỉ ghi đã mở rồi chấm như bình thường |
| Q9 | Cách ly host giữa L/N | Phiên/workspace độc lập, không nạp nguồn/kết quả nhánh trước. Kiểm context/memory quan sát được; phiên mới không tự chứng minh sạch. Không xác minh được thì tiêu chí phụ thuộc giữ không đánh giá được; không xóa hay đổi cấu hình global để làm sạch |
| Q10 | Quay màn hình/ghi âm | Mặc định không; chỉ khi người thử đồng ý riêng |
| Q11 | Phiếu cảm nhận sau buổi thử | Dùng [FEEDBACK_FORM_VI_EN.md](../../../docs/FEEDBACK_FORM_VI_EN.md), người thử tự chọn; lời nhắc để agent điền hộ trong phiếu không dùng ở pilot này |
| Q12 | Đồng hồ và cách bấm giờ | Dùng log có timestamp nếu có, nếu không dùng đồng hồ người quan sát; ghi nguồn từng số theo mục 7, không đặt 0 khi thiếu |

## 3. Artifact, nguồn và hash

**Artifact chọn cho lượt người thật kế tiếp: RC4 Windows DATAMOCK.** Dùng đúng [prerelease v1.9.0-rc4](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc4) đã công bố; không materialize từ source dirty đang phát triển và không build lại để tổ chức pilot.

| Binding đã đối chiếu24/10/2026 | Giá trị |
|---|---|
| Source/tag | `2552d7d79558ad360a886239e73df1122122dbcc` / `v1.9.0-rc4` |
| ZIP local đã phát hành | `working/v7-internal/clean-source-2552d7d/local-agent-workspace-v1.9.0-rc4.zip` |
| ZIP SHA-256 | `645fe02c5d36f0dd6726cf44bc6f0313083eae2d331f9b6c88d6d34274057129` |
| Gate JSON SHA-256 | `fc0ebf33875735050d7c26ce0b58fb5f3f1afb95e643b875d5f4b8608e22667e` |
| File checksum SHA-256 | `c6d281e8ba308c4c66dfdb66f625afdeb984d3009501a146ae95198e413fc766` |
| `MANIFEST.sha256` bên trong ZIP | `56843b7234301b1c637caec064f602caa87ff2b5351e65651ff7da273b075979` |
| Cây gốc trong ZIP | `local-agent-workspace-v1.9.0/`; nguồn VI dưới `examples/`, không lấy bản dịch trong `en/examples/` |

Ba nguồn A đúng bytes/hash ở bảng dưới; oracle vẫn khớp. Mẫu B và hash thay đổi có kiểm soát cũng đã tính lại, không tạo file B hoặc áp thay đổi khi chưa có lượt thật. RC4 đã qua4/4gate; CI toàn run39985758160 vẫn FAILURE3/5, Windows3.8/macOS chưa được nhận hỗ trợ. Kết quả đó không thay cho gate người/môi trường của pilot.

Khi đủ G1/G2 và vị trí Q5: kiểm lại hash ZIP/gate/checksum, giải nén vào cây đối chiếu ngoài kho nguồn, ghi đường dẫn và hash MANIFEST thực tế vào phiếu; giữ ZIP và cây đối chiếu nguyên trạng. Người thử chỉ làm trên bản chép ("bộ mẫu của người thử"); Việc3 có thể sửa bản chép đó. Không ghi đè snapshot/lab lịch sử hoặc nhận source Git sạch cho thư mục pilot đã sửa.

**Lịch sử chuẩn bị20/10:** dùng source dirty `b13e375d`/materialize. Các dry-run mục10 chỉ thuộc snapshot cũ, không phải đã chạy pilot RC4. Không refresh MANIFEST kho, không build release/fullsuite hoặc giả Git sạch để thay lịch sử.

**Ba nguồn giả của mẫu** (raw SHA-256 đã so lúc chuẩn bị, trùng với bảng trong workorder; bản dự án tạo từ kho dirty trong thư mục tạm
giữ đúng bytes này). Nếu hash đổi khi chạy thì đối chiếu lại oracle từ file thật, không khôi phục nguồn theo bảng.

| File dưới `examples/demo-project/` | SHA-256 |
|---|---|
| [notes/meeting_notes.txt](../../../examples/demo-project/notes/meeting_notes.txt) | `b88d37364f57dba0b661060e7a9f196a7d6ad3b2511cdfd591cc40842384cc58` |
| [docs/procedure_v1.md](../../../examples/demo-project/docs/procedure_v1.md) | `90b4429f6a582df32274b092c5ee4f50a8e245b512eadd6522cc4888efb2a169` |
| [docs/procedure_v2.md](../../../examples/demo-project/docs/procedure_v2.md) | `b57ff1782b4deded41886f487c96016f312526a634a6142957631b46f1023101` |

**Thay đổi kiểm soát cho Việc 2 (kế hoạch, chỉ trên bản sao pilot).** Đây không phải dữ kiện của nguồn hiện có. Trong
`docs/procedure_v2.md` của thư mục A (cả hai nhánh), đổi đúng một câu và không đổi gì khác (file gốc dùng LF, sửa theo bytes):

| | Trước | Sau (dữ kiện giả của bản sao pilot) |
|---|---|---|
| Bước 5 | `Bộ phận xử lý hoàn tất trong 3 ngày làm việc.` | `Bộ phận xử lý hoàn tất trong 4 ngày làm việc.` |
| SHA-256 file | `b57ff1782b4deded41886f487c96016f312526a634a6142957631b46f1023101` | `01b6286007dfb80466f324c94b282b2d9c1f9d8e3d3aedb0057c82b386e9bd35` |

Hash "sau" được tính trên bản sao trong thư mục tạm lúc chuẩn bị; tính lại trên file thật khi áp dụng. Giữ một bản chép của file "trước"
ngoài thư mục người thử để đối chiếu. Thời điểm áp dụng: sau khi đóng phiên Việc 1 và trước khi mở phiên Việc 2, không có người thử
tham gia và không báo trước. Chỉ một thay đổi này; không sửa `meeting_notes.txt` hay `procedure_v1.md`, không dùng kết quả của người thử làm đáp án.

**Nguồn B (soạn cho pilot; dữ liệu giả; không phải file có sẵn của repo).** Repo chưa có ghi chú họp thứ hai nên điều phối tạo file
này khi chạy, từ đúng nội dung dưới đây (UTF-8, LF, có dòng trống thứ ba và xuống dòng ở cuối). Tên file đề nghị
`hop_to_luu_tru_2026-09-18.txt`, đặt ở `references/source-documents/` của thư mục B (nhánh native: cùng đường dẫn tương đối). SHA-256
tính lúc chuẩn bị với đúng bytes này: `4c5496cf396e0463a4ca062e45a2631f7022464842e3888d983c4ff66e7a06ed`; lệch thì tính lại và ghi.
Tên người của B không trùng tên người của A, để dò dữ liệu A lọt sang B.

```text
Họp rà soát Tổ Lưu trữ - 18/09/2026 (dữ liệu giả)
Có mặt: Hoa, Quân, Nga, Sơn (vắng: Trang)

- Hoa báo kho tầng 2 đã hết chỗ để hồ sơ. Quân nói đã báo phòng hành chính, chưa nhận được trả lời.
- Chốt: từ tháng sau hồ sơ đã đóng quá 12 tháng chuyển xuống kho tầng 1. Sơn lập danh sách trước thứ Tư tuần sau.
- Nga đề nghị đánh số lại hộp hồ sơ theo mã mới. Chưa ai nhận làm. Cần hỏi chị Trang xem mã cũ có đang dùng ở nơi khác không.
- Chốt: phiếu mượn hồ sơ nộp qua email thay vì giấy. Hoa gửi hướng dẫn cho các tổ từ tuần sau.
- Còn bàn: có nên cho mượn hồ sơ gốc ra ngoài tổ không? Chưa thống nhất, hẹn họp sau.
```

Chưa đưa CSV mơ hồ (`weekly_log.csv`), Office hay căn cứ pháp lý thật vào pilot đầu, để không thêm biến số.

## 4. Thư mục và hai nhánh

Mọi thư mục dưới một gốc pilot ngoài kho nguồn (Q5). Mỗi nhánh có thư mục riêng cho A (Việc 1–2) và B (Việc 3), phiên riêng, không dùng
lại kết quả của nhánh kia.

| Nhánh | Chuẩn bị | Người thử được dùng |
|---|---|---|
| **L (LAW)** | Bộ mẫu của người thử (bản chép của snapshot). Dự án A và B là thư mục ngang hàng với bộ mẫu, tạo từ bảng điều khiển hoặc đường chính trong [HUONG_DAN_TAO_PROJECT_MOI_VI.md](../../../docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md); không đặt dự án trong bộ mẫu | Mọi hướng dẫn có trong bộ mẫu ([README](../../../README.md), START_HERE, [dùng hằng ngày](../../../docs/HUONG_DAN_SU_DUNG_VI.md), [kỹ năng](../../../docs/HUONG_DAN_SKILLS_VI.md)); cho Việc 3, hướng dẫn C-01 là mục 11 của hướng dẫn kỹ năng |
| **N (native)** | Hai thư mục thường, không có file nào của LAW (không `AGENTS.md`, `PROJECT.md`, `.agent/`, `.cvf/`, `skills/`). N-A chứa bản chép đúng bytes ba nguồn giả ở cùng đường dẫn tương đối `examples/demo-project/...`; N-B chứa nguồn B ở cùng đường dẫn tương đối như nhánh L | Khả năng thật sự có của ứng dụng (đọc/ghi file, kỹ năng, bộ nhớ nếu có). Không tắt file tools, không làm yếu baseline, không dạy thao tác của LAW |

Giữ nguyên giữa hai nhánh: host, loại account, model và effort (nếu khả dụng), OS, nguồn và hash, mục tiêu trong NGUOI_THU, quyền đọc/ghi
trong thư mục được giao. Khác nhau: phần LAW (mẫu, hướng dẫn, kỹ năng, quy tắc trong thư mục). Nếu một điều kiện khác nhau giữa hai
nhánh thì ghi vào PHIEU_GHI_NHAN mục L và không tính chênh lệch đó là hiệu quả của LAW.

Việc 3 không ép baseline làm thao tác riêng của LAW. Ở nhánh N, người thử dùng cách quen thuộc của họ (nhắc lại bằng lời, ghi chú,
hướng dẫn riêng của ứng dụng nếu có). Ở nhánh L, họ có thể theo mục 11, hoặc chỉ tạo B rồi nói lại, hoặc cách khác; ghi đường nào họ chọn.
Nếu họ theo mục 11, bộ mẫu của người thử là phần bị sửa: ghi chênh lệch so với snapshot gốc làm dấu chân công sửa.

## 5. Thứ tự thử, học và so sánh

- Lượt đầu là pilot khám phá định tính, mặc định L trước để quan sát lần đầu dùng LAW, N sau trên cùng nguồn. Không soạn bộ nguồn thứ hai trong phạm vi chuẩn bị này. Người đã làm L sẽ biết đáp án khi làm N: không tính tỷ lệ nhanh hơn, chênh lệch điểm hay chi phí như hiệu quả của LAW. Một người hoặc một thứ tự không chứng minh quan hệ nhân quả hay tính phổ quát.
- Nếu sau này cần so sánh có kiểm soát, chốt thiết kế riêng trước chạy: nguồn mới và oracle đã đối chiếu, độ khó/tương đương chưa được chứng minh chỉ vì đổi tên; tách người hoặc đổi thứ tự khi có đủ người. Bộ hiện tại không tự trở thành benchmark sau khi đổi thứ tự.
- Ghi thứ tự, thời gian làm quen và hiệu ứng học. Mỗi nhánh có thư mục, phiên/workspace riêng; không nhập transcript/kết quả của nhánh trước. Trong cùng một nhánh, Việc 1→2 vẫn giữ cơ chế tiếp tục tự nhiên của host và ghi rõ cơ chế đó; không nhầm với cách ly giữa hai nhánh.
- Trước N, điều phối kiểm context/project/memory quan sát được. Người thử tự nói còn nhớ đáp án cũng được ghi. Nếu không kiểm được hoặc có kết quả nhánh trước trong context thì đánh dấu nhiễm chéo/không xác minh được; tiêu chí phụ thuộc không đánh giá được. Không thay account hay sửa memory/global settings ngầm. Quan sát điều hướng độc lập còn ghi được thì lưu riêng, không dùng để khôi phục giá trị so sánh nội dung.
- `examples/demo-project/README.md` có cả bài và đáp án; tài liệu điều phối cũng có oracle. Không đưa tài liệu điều phối cho người thử hoặc AI thực hiện. Giữ README của mẫu để không đổi sản phẩm thử; ghi người thử VÀ AI có đọc đoạn nào, trước/sau tiêu chí nào, với bằng chứng nếu có. Phải xem cả log đọc file/ngữ cảnh quan sát được, không chỉ hỏi người thử có mở không.
- Đã tiếp xúc đáp án: tiêu chí nội dung bị ảnh hưởng ghi **không đánh giá được về tính độc lập**, nguồn lộ và thời điểm. Không biết đã đọc phần nào hoặc không quan sát được thì ghi **chưa xác minh**, không tự chấm tự phát hiện/độc lập. Những thao tác không phụ thuộc đáp án (tìm file, đóng/mở, lưu đúng chỗ) có thể ghi riêng; không lấy kết quả đó suy LAW tạo nội dung đúng. Nhãn NT/HT ở phiếu không đủ để xác định nguyên nhân: HT chỉ là không thấy user yêu cầu rõ, chưa chứng minh do quy tắc LAW.
- Không ép baseline tắt kỹ năng/file tools bình thường; nếu môi trường khác nhau hoặc kết quả nhiễm chéo, không quy chênh lệch cho LAW. Không benchmark trả phí trong tranche này; mọi chi phí chỉ ghi khi có lượt thật trong giới hạn được phép.

## 6. Kịch bản và oracle

Đối chiếu từ nội dung đầy đủ của ba file nguồn ở mục 3. Ba mốc: **Mốc 1** (Việc 1) làm từ mẫu sạch; **Mốc 2** (Việc 2) đóng rồi mở lại phiên;
**Mốc 3** (Việc 3) dùng lại cho B. Mỗi mốc ghi: người thử được nhận gì, điều quan sát được, nguồn oracle, điều được và chưa được kết luận,
bằng chứng giữ. Mã tiêu chí dưới đây dùng nguyên trong phiếu ghi nhận.

Mỗi tiêu chí chấm riêng: đạt / chưa đạt / không đánh giá được, kèm bằng chứng; áp dụng quy tắc lộ đáp án/nhiễm chéo ở mục 5 trước khi chấm. Không cộng thành điểm hay ngưỡng đạt. Ghi thêm tiêu chí đó
có được người thử yêu cầu rõ trong lời nhắc của họ hay không. Không yêu cầu rõ chưa chứng minh do hệ thống hoặc quy tắc mang lại; năng lực native, nguồn đã đọc và đáp án bị lộ đều có thể ảnh hưởng.

### Mốc 1: làm từ mẫu sạch

- Người thử nhận: mục Việc 1 trong NGUOI_THU, thư mục của lượt, tài liệu hướng dẫn tùy nhánh. Không nhận prompt.
- Quan sát: cách tìm nguồn, lời nhắc nguyên văn, hai file bản nháp, thao tác sửa, hỗ trợ.
- Chưa được kết luận: người mới dùng được LAW, hay LAW tốt hơn native. Chỉ kết luận trên phạm vi một người, một thứ tự, dữ liệu giả.

**Việc 1a, biên bản họp.** Nguồn: [meeting_notes.txt](../../../examples/demo-project/notes/meeting_notes.txt). Dữ kiện nguồn: họp 04/09/2026; có mặt Lan, Hùng, Minh, Thu, vắng Đức.

| Mã | Điều cần thấy |
|---|---|
| BB1 | Ba nhóm tách rõ: quyết định; việc cần làm; vấn đề chưa chốt hoặc chưa có người/hạn |
| BB2 | Đúng hai quyết định "Chốt": thêm một người trực chiều thứ Ba và thứ Năm từ tuần sau; báo cáo tuần gửi vào thứ Sáu thay vì thứ Hai |
| BB3 | Việc có người: Minh sắp lịch trực, Lan gửi báo cáo từ tuần sau. "Từ tuần sau" ghi nguyên văn, không đổi thành ngày lịch; hạn riêng cho việc sắp lịch của Minh không có trong nguồn nên ghi "cần xác nhận" hoặc nguyên văn mốc, không tự đặt ngày |
| BB4 | Thu chỉ là người đề nghị mẫu phiếu tiếp nhận mới; nguồn ghi "chưa ai nhận làm", nên người phụ trách và hạn là "cần xác nhận", không gán cho Thu |
| BB5 | Việc hỏi anh Đức về quy định bắt buộc giữ trường cũ: người hỏi và hạn là "cần xác nhận"; có nêu Đức vắng họp |
| BB6 | Lỗi tải file trên 10 MB: ghi Hùng đã báo bên kỹ thuật, chưa có hạn trả lời. Không biến thành việc giao Hùng theo dõi và không đặt hạn |
| BB7 | Vấn đề chưa chốt: có gộp kênh Trực tiếp vào Điện thoại khi báo cáo hay không; hẹn họp sau, không có ngày |
| BB8 | Không bịa số liệu, vai trò hoặc hạn (ví dụ không thêm số hồ sơ tồn, không đặt ngày); chỗ thiếu ghi "cần xác nhận" |
| BB9 | Lưu thành file trong thư mục được giao (ghi đường dẫn) và nêu nguồn đã dùng |

**Việc 1b, đối chiếu quy trình.** Nguồn: [procedure_v1.md](../../../examples/demo-project/docs/procedure_v1.md) và [procedure_v2.md](../../../examples/demo-project/docs/procedure_v2.md). Bước 2 và bước 3 giống hệt nhau ở hai bản; bước 1 chỉ diễn đạt lại.

| Mã | Điều cần thấy |
|---|---|
| SS1 | Bảng thay đổi có ý nghĩa gồm bước 4, bước 5, bước 6 và bước 7 (mới) |
| SS2 | Bước 1 (diễn đạt lại), bước 2 và 3 (giống hệt) không bị liệt kê như thay đổi; nếu nhắc đến thì nêu rõ không đổi nghĩa |
| SS3 | Giá trị đúng: bước 5 từ 5 xuống 3 ngày làm việc (rút 2 ngày); bước 4 vẫn trong vòng 1 ngày làm việc nhưng nay là trưởng tổ phân công người xử lý, thay cho chuyển hồ sơ cho bộ phận xử lý; bước 6 thêm kênh tin nhắn hoặc email; bước 7 mới: hồ sơ trễ hạn báo trưởng tổ vào cuối ngày |
| SS4 | Phần ảnh hưởng mang nhãn "(suy luận)" ở tiêu đề cột hoặc từng ý; phần nhắc lại nội dung nguồn không bị gắn nhãn đó |
| SS5 | Không thêm điều nguồn không nói: bản 1 không nêu ai chuyển hồ sơ ở bước 4, nên "đổi người phụ trách" chỉ đúng khi ghi là suy luận hoặc nêu cả hai cách hiểu; không có ngày hiệu lực hay người duyệt bản 2; "trễ hạn" tính theo hạn bước nào là "cần xác nhận" |
| SS6 | Lưu thành file (ghi đường dẫn) và nêu nguồn là hai file đúng |

Bằng chứng giữ: đường dẫn và SHA-256 hai file bản nháp lúc người thử xác nhận xong, lời nhắc nguyên văn, bản trao đổi đã che, thời điểm từng sự kiện (mục 7).

### Mốc 2: đóng phiên, mở lại, đúng revision

- Trình tự: người thử xác nhận xong Việc 1 → đóng phiên (ghi SHA-256 hai bản nháp và các nguồn) → điều phối áp dụng thay đổi ở mục 3 → mở phiên mới → người thử làm Việc 2. Không báo trước thay đổi; sau buổi thử, giải thích đầy đủ.
- Người thử nhận: mục Việc 2. Không nhận gợi ý rằng có tài liệu đổi.
- Chưa được kết luận: LAW có luôn nhận ra nguồn đổi, hay khả năng nhớ của host nói chung; chỉ quan sát một thay đổi, một đường dẫn.
- Ghi cơ chế mà phiên mới dùng để biết việc cũ (đọc STATE/HANDOFF, đọc thư mục, sổ nguồn, bộ nhớ hay lịch sử trò chuyện của host, người thử tự kể) và cơ chế nhận ra thay đổi (UI, chỉ mục, so hash, AI đọc lại nguồn, người thử, không có).

| Mã | Điều cần thấy |
|---|---|
| LT1 | Tìm lại đúng file biên bản và file so sánh của Việc 1 (đường dẫn đúng) mà không tạo lại chỉ để xem; ghi nếu AI đọc lại cả ba nguồn hoặc viết lại bản nháp |
| LT2 | Nêu đúng nguồn mỗi bản nháp dựa vào (file đúng; mốc thời gian hoặc hash nếu có) |
| LT3 | Nhận ra `procedure_v2.md` khác lúc lập bản so sánh; ghi ai hoặc cái gì nhận ra (hệ thống, AI, người thử, không ai) và lúc nào |
| LT4 | Sau khi nhận ra, không dùng dòng bước 5 cũ (5 xuống 3) như hiện hành, hoặc nêu rõ đó là bản cũ |
| LT5 | Bản so sánh hiện hành ghi bước 5 từ 5 xuống 4 ngày làm việc (rút 1 ngày); các dòng khác giữ nội dung đúng |
| LT6 | Bản so sánh cũ còn nguyên (SHA-256 như lúc đóng phiên); bản hiện hành là file riêng hoặc revision phân biệt được |
| LT7 | Biên bản (nguồn không đổi) không bị báo là cần xem lại và không bị tạo lại không cần thiết |
| LT8 | AI không sửa hay ghi đè file nguồn nào (so SHA-256 với mục 3, trong đó `procedure_v2.md` ở trạng thái "sau") |

Nếu không ai nhận ra thay đổi và người thử đưa bản cũ, ghi là lỗi stale (mục 7) của nhánh đó; không coi là lỗi của người thử.
Nếu thay đổi bị báo ở file khác (báo nhầm), ghi là cảnh báo sai.

### Mốc 3: dùng lại cho việc B

- Người thử nhận: mục Việc 3 và nguồn B. Không nhận dữ liệu, quyền, STATE hay đầu ra đã nhận của A; không nhận câu lệnh.
- Nguồn oracle: nguồn B ở mục 3. Danh sách dò dữ liệu A (so từng từ nguyên, không phân biệt hoa thường; xem ngữ cảnh khi từ trùng một từ thường như "thu"): Lan, Hùng, Minh, Thu, Đức, "10 MB", "trực chiều", "thứ Sáu", "phiếu tiếp nhận".
- Nhánh L: B chứa cả bản chép của ví dụ trong mẫu (cùng bytes với nguồn A). Dùng chúng thay cho nguồn B là lỗi nguồn sai.
- Chưa được kết luận: LAW làm dùng lại dễ hơn native, hoặc đường mục 11 phù hợp người mới; chỉ quan sát đường người thử chọn.

| Mã | Điều cần thấy |
|---|---|
| DL1 | Dùng đúng nguồn B (SHA-256 khớp mục 3), không dùng nguồn A hay ví dụ trong mẫu |
| DL2 | Đầu ra B không chứa dữ liệu A theo danh sách dò ở trên |
| DL3 | Hai quyết định "Chốt": hồ sơ đã đóng quá 12 tháng chuyển xuống kho tầng 1 từ tháng sau; phiếu mượn hồ sơ nộp qua email thay vì giấy |
| DL4 | Việc có người: Sơn lập danh sách "trước thứ Tư tuần sau"; Hoa gửi hướng dẫn cho các tổ "từ tuần sau". Mốc ghi nguyên văn, không đổi thành ngày lịch |
| DL5 | Không gán sai: Nga chỉ đề nghị đánh số lại hộp (chưa ai nhận); Quân đã báo phòng hành chính, chưa trả lời, không có hạn, không thành việc giao Quân theo dõi; việc hỏi chị Trang: người hỏi là "cần xác nhận", Trang vắng họp |
| DL6 | Vấn đề chưa chốt: có cho mượn hồ sơ gốc ra ngoài tổ không; hẹn họp sau, không có ngày |
| DL7 | Cách làm người thử đã ghi ở cuối Việc 1 được áp dụng hoặc ghi rõ không áp dụng được; ghi bằng đường nào (hệ thống mang lại, người thử nhắc lại bằng lời, không áp dụng) |
| DL8 | Không mang quyền, STATE hay đầu ra đã nhận của A sang B; A không đổi so với cuối Mốc 2 (SHA-256) và B không chứa file của A |
| DL9 | Ghi nhận, không chấm đạt/chưa đạt: đường dùng lại người thử chọn và, nếu có sửa bộ mẫu của người thử, danh sách chênh lệch so với snapshot gốc |

## 7. Ghi nhận số đo

- **Thời gian.** Tách: setup (từ lúc nhận thư mục tới lời nhắc đầu tiên đúng việc), tìm nguồn (từ lúc bắt đầu việc tới lúc nguồn đúng được mở hoặc dùng,
  có bằng chứng trong trao đổi hoặc log công cụ), thực hiện, sửa (người thử sửa tay hoặc nhắc lại sau kết quả sai hoặc thiếu), gián đoạn (lỗi công cụ, chờ, tạm dừng,
  hỏi người quan sát). Mỗi số ghi nguồn đo (đồng hồ người quan sát, log ứng dụng, khác); không đo được thì "chưa đo".
- **Giải thích lại và hỗ trợ.** Đếm lần người thử phải nói lại cùng ý cho AI, lần người quan sát hỗ trợ, và bước cần hỗ trợ; mỗi lần ghi nguyên văn (mục 8).
- **Lỗi.** Stale: nội dung dựa trên nguồn đã đổi được trình bày như hiện hành. Ghi nhầm: ghi/ghi đè file sai chỗ, sửa nguồn gốc hoặc đưa dữ liệu A vào B. Đúng revision: Mốc 2 theo LT2–LT6.
- **Artifact.** Đường dẫn, loại, SHA-256 lúc người thử xác nhận; file thật thay vì mô tả.
- **Chi phí.** Chỉ theo nguồn quan sát được (hóa đơn, bảng sử dụng, telemetry của ứng dụng). Ghi nguồn, đơn vị, phạm vi (phiên, mốc, account) và thời điểm đọc.
  Không có số thì "chưa đo", không coi là 0, không suy từ token hay thời gian thành tiền.
- **Phân loại mốc** (chỉ ghi nhận hành vi, không phải ngưỡng đạt): hoàn thành độc lập (người thử tự tuyên bố xong, có artifact, không có hỗ trợ ghi trong mục 8);
  hoàn thành có hỗ trợ (có artifact và có ít nhất một hỗ trợ ghi nguyên văn); chưa hoàn thành (dừng, bỏ, hết giới hạn đã xác nhận hoặc không ra artifact); không đánh giá được
  (môi trường chặn, thiếu dữ liệu, điều kiện nhánh không tương đương). Mỗi phân loại gắn bằng chứng. Việc các tiêu chí oracle đạt bao nhiêu được báo riêng ở mục 6,
  không trộn vào phân loại này. Nếu mốc bị lộ oracle hoặc nhiễm chéo làm mất khả năng đánh giá độc lập, ghi mốc không đánh giá được về nội dung; thao tác còn quan sát được ghi riêng, không gọi đó là độc lập hoàn thành nội dung.

## 8. Quy tắc cho người quan sát

- Chỉ ghi. Không gõ thay, không sửa lời nhắc, không chỉ nút hay lệnh, không cho câu mẫu.
- Khi người thử hỏi hoặc bị kẹt: có thể nhắc "bạn có thể đọc tài liệu trong thư mục" hoặc cho biết mốc đang bàn; mọi lời hỗ trợ ghi nguyên văn kèm thời điểm, mốc và loại
  (làm rõ đề, chỉ nơi đọc, chỉ cách làm, làm thay). Kết quả có hỗ trợ không gọi là hoàn thành độc lập.
- Nếu người thử hoặc AI đọc ví dụ/đáp án trong hướng dẫn (kể cả `examples/demo-project/README.md`), ghi nguồn, đoạn, thời điểm và tiêu chí ảnh hưởng; áp dụng mục 5. Phân biệt người tự tìm, AI tự đọc và điều phối cung cấp, không gộp thành nội dung hoàn thành độc lập.
- Dừng khi: người thử muốn dừng; hết giới hạn đã xác nhận; môi trường chặn; xuất hiện dữ liệu thật hoặc bí mật (không chép vào ghi nhận; che); AI bắt đầu gửi dữ liệu ra ngoài thư mục hoặc dịch vụ không thuộc buổi thử.
- Không liên hệ người thử hay gửi feedback ra ngoài khi chưa được yêu cầu. Không bật quay màn hình hay gửi dữ liệu nếu chưa có đồng ý riêng (Q10).
- Ý kiến cảm nhận, kết quả công cụ, quan sát hành vi và chấp nhận của người dùng là các loại bằng chứng khác nhau; ghi ở các mục riêng. `USER_ACCEPTED` chỉ do người dùng thật xác nhận.

## 9. Sau buổi thử

1. Điều phối giải thích đầy đủ, kể cả thay đổi nguồn ở Mốc 2.
2. Lưu lời nhắc nguyên văn và khối "Khai báo thực hiện" của agent (hoặc ghi "không có") theo [README feedback](../../README.md) và [TEMPLATE](../../TEMPLATE.md) trong một bản ghi
   ở `feedback/records/` cho từng lượt. Nhánh native không có khối khai báo là điều bình thường, ghi nhận mà không coi là lỗi của native. Nhánh L: có thể kiểm bằng `python tools/check_output.py --declaration <file>`.
3. Điền PHIEU_GHI_NHAN (một bản cho mỗi người thử và nhánh). Thêm dòng vào `feedback/INDEX.md` chỉ khi có bản ghi thật; chuẩn bị này không thêm dòng nào.
4. Báo cáo cho operator: phần đã đánh giá, phần "chưa đánh giá" và vì sao, điều cần người dùng xác nhận. Không kết luận T37–T38, C-02 hay R6.

## 10. Lịch sử lượt chuẩn bị20/10 và cập nhật24/10

- Đã đối chiếu: ba hash nguồn giả với workorder; toàn bộ nội dung ba file nguồn cho oracle; EOL ba nguồn (LF); hash dự kiến của file đã đổi ở Mốc 2 và của nguồn B.
- Đã dry-run trong thư mục tạm (không phải pilot, không gọi AI, không người thử): xem trước và tạo một dự án từ kho dirty bằng `new_project.py`, kiểm bytes ba nguồn trong dự án; `materialize` một snapshot,
  `check_package.py --verify` đạt trên snapshot, và xem trước `new_project.py` từ snapshot.
- Chưa kiểm: chạy `APP.bat` hay bảng điều khiển ở snapshot, UI trong trình duyệt, mở bằng ứng dụng AI thật, mục 11 hướng dẫn kỹ năng với người thật, và mọi thứ cần người thử. Không chạy full suite, browser, Office hay release gate.

**Cập nhật24/10 (chỉ chuẩn bị):** đã kiểm hash3asset RC4 và MANIFEST, đọc đủ3nguồnVI và đối chiếu bytes vớiZIP, giữ oracle A/B và phép đổi3→4ngày. Chưa có người thử theo trả lời operator; chưa tạo cây pilot/B, chưa chạy APP/host/L-N, chưa có thời gian/chi phí/cảm nhận/nghiệmthu. PHIEU_GHI_NHAN giữtrống/NOT_RUN; không thêm feedback record hoặc INDEX. Source/artifact/CI/notes RC4 giữnguyên.
