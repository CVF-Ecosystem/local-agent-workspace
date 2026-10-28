# Hồ sơ tiếp nhận: gói cang-logistics bản 0.2.0

Kết luận: **DEFER** (hoãn). Quan hệ với năng lực sẵn có: `SUPPLEMENT` (bổ sung căn cứ, mẫu và quy tắc nghiệp vụ mà native không có sẵn).
Gói tiếp tục là ứng viên (`REVIEW`): dùng thử trong project, không chép sang ứng dụng, không đưa vào bộ mẫu gốc.
Lập ngày 14/10/2026 bởi agent (Claude), chưa có người xác nhận. Hồ sơ này ghi bằng chứng đã có và phần còn thiếu; nó không phải nghiệm thu.

## Sáu điều kiện (theo `skills/README.md`)

| # | Điều kiện | Kết quả | Căn cứ |
|---|---|---|---|
| 1 | Nhu cầu và phần tăng thêm | ĐẠT MỘT PHẦN | Native không có bảng căn cứ có số hiệu và ngày đối chiếu cho lĩnh vực này. Phép thử A/B bên dưới cho thấy giá trị tăng thêm ở một số gói, không phải mọi gói. |
| 2 | Xuất xứ | CHƯA ĐỦ BẰNG CHỨNG | Bảng căn cứ lập ngày 12/10/2026 từ trang tin, tổng hợp và tư vấn (không phải văn bản chính thức); dòng chưa kiểm ghi `[cần xác nhận]`. Chưa đối chiếu toàn văn với nguồn chính thức. |
| 3 | Quyền và an toàn | ĐẠT | Kiểm máy ngày 14/10/2026: gói chỉ có `.md` và `pack.json`, không script, không dependency, không hook; URL chỉ là nguồn trích dẫn trong `legal-basis.md`; lệnh nhắc tới chỉ là công cụ có sẵn của workspace (`tools/library.py`, `tools/pack.py`). |
| 4 | Hiệu quả đã kiểm | CHƯA ĐỦ BẰNG CHỨNG | Xem phần "Phép thử A/B". Một model, một tác vụ, hai lần, tiêu chí cơ học, agent chấm; thiếu ca lỗi và ca thiếu nguồn; chưa thử trên ứng dụng agent thật. |
| 5 | Dùng được, không hại phần đã có | ĐẠT MỘT PHẦN | Id skill không trùng skill của package (`pack.py check`); ngoài phạm vi, cả hai bản chỉ trả bản dịch (10/10 và 10/10 câu): skill không chen vào việc không liên quan. Chưa thử trên ứng dụng thật. |
| 6 | Phạm vi tái dùng | CHƯA ĐỦ BẰNG CHỨNG | Quy tắc riêng đơn vị đã tách ra skill của project (theo README gói). Chưa có ba việc thật của người dùng trong lĩnh vực này, điều kiện riêng của gói dùng chung (`packs/README.md`). |

## Phép thử A/B (qwen-plus, Alibaba Model Studio, 14/10/2026)

Tiêu chí đặt trước khi chạy, chấm bằng quy tắc cơ học trên văn bản trả lời. A: cùng `AGENTS.md`, không có skill. B: A thêm SKILL.md và references của gói, ghi rõ là bản `REVIEW`.
Dữ liệu giả; không có công cụ; mỗi ô chạy 2 lần.

| Tiêu chí | A (không skill) | B (có skill) |
|---|---|---|
| Ghi chỗ chưa kiểm / cần xác nhận | 0/2 | 2/2 |
| Nêu số hiệu văn bản | 0/2 | 0/2 |
| Có khối "Khai báo thực hiện" | 0/2 | 1/2 |
| Có đoạn trình bày như trích nguyên văn (không có toàn văn trong gói) | 0/2 | 0/2 |

Nhận xét riêng của gói: Tác vụ đại diện: tính thời gian làm tàu, năng suất cẩu và sự cố từ số liệu giả. Không có đáp án đã biết, nên không chấm đúng/sai; chỉ chấm việc ghi chỗ chưa kiểm. Quy tắc tính lấy từ việc thật của một đội khai thác container; chưa ai ngoài người duy trì kiểm lại.

## Còn thiếu để chuyển sang `ADD_MISSING_PART` (hoặc `PROJECT_ONLY`)

1. Người có thẩm quyền đối chiếu bảng căn cứ `packs/cang-logistics/skills/port-operations-reports/references/legal-basis.md` với văn bản chính thức và ghi kết quả (điều kiện 2).
2. Ít nhất ba việc thật của lĩnh vực này, chạy trên ứng dụng agent thật của người dùng, kèm đánh giá của người dùng; có ca thiếu nguồn và ca lỗi (điều kiện 4 và 6).
3. Xử lý hiện tượng B vẫn trình bày đoạn "nguyên văn" không có trong gói, hoặc chấp nhận và ghi vào giới hạn (điều kiện 4).
4. Chỉ khi 1-3 xong mới đổi `intake.decision` và nâng `intake.version` theo bản đã xét. Đó vẫn chỉ là lời khai của gói: người dùng ở từng project
   tự đọc hồ sơ rồi chạy một lệnh (`pack.py add <tên> --confirm` hoặc `pack.py confirm <tên>`) thì skill mới thành `AVAILABLE`.

Giới hạn của phép thử này: một model, mỗi ô 2 lần, tiêu chí cơ học nên bỏ sót chất lượng diễn đạt; agent tự chấm không phải nghiệm thu của người dùng. Kết quả không nói gì về model khác.

## Đánh giá bổ sung: `container-yard-check` trong bản 0.3.0 (28/10/2026)

Kết luận riêng cho skill mới: **DEFER**; quan hệ **SUPPLEMENT**. Giữ `port-operations-reports` và hồ sơ lịch sử 0.2.0 ở phạm vi cũ. Skill mới chỉ hướng dẫn xây dựng hoặc rà soát công cụ kiểm tra dữ liệu vị trí bãi từ TOS; nó không thay báo cáo khai thác và căn cứ pháp lý của skill hiện có.

Nguồn được đọc là snapshot 7 file của ứng viên `cang-bai-container` 0.1.0, nhãn nguồn tổng quát “AN C2 candidate package 0.1.0, 28/10/2026”. SHA-256 tổng hợp: `8c5be17211ecaf090eeb238c9e6dfc7ff86c87960476d596ea5caf4aad405b01`. Cách tính: sắp xếp đường dẫn tương đối đã chuẩn hóa; ghép từng SHA-256 bytes thô và đường dẫn theo dạng `<hash>  <relative path>\n`; băm UTF-8 của danh sách đó. Đây là fingerprint của snapshot đã đọc, không phải mã Git hay xác nhận bản phát hành. Hồ sơ không lưu đường dẫn máy hoặc tên đơn vị.

| # | Điều kiện | Kết quả hiện tại | Căn cứ và giới hạn |
|---|---|---|---|
| 1 | Nhu cầu và phần tăng thêm | ĐẠT MỘT PHẦN | Có nhu cầu riêng về kiểm tra dữ liệu vị trí bãi; phạm vi khác báo cáo khai thác hiện có. Chưa có phép so sánh cho thấy skill làm tăng chất lượng hoặc giảm lỗi trong một việc mới. |
| 2 | Xuất xứ | ĐẠT MỘT PHẦN | Có snapshot và lịch sử về một ứng dụng nguồn; các block, mã, mốc thời gian và chỉ số gắn với đơn vị đã được bỏ khỏi skill. Chưa có đánh giá độc lập trên nguồn nghiệp vụ khác; fingerprint chỉ nhận diện snapshot đã đọc. |
| 3 | Quyền và an toàn | ĐẠT CÓ GIỚI HẠN | Candidate chỉ gồm Markdown và metadata, không có script, dependency, hook hoặc credential. Đã đọc để đánh giá; không chạy code, cài đặt hoặc xuất dữ liệu. Cần đánh giá lại nếu thành phần thay đổi. |
| 4 | Hiệu quả đã kiểm | UNKNOWN — CHƯA ĐỦ BẰNG CHỨNG | Chưa có thử nghiệm A/B của skill, chưa có tác vụ mới trên ứng dụng agent thật và phản hồi người dùng. Số liệu kiểm thử của ứng dụng nguồn, nếu có trong provenance lịch sử, chỉ mô tả ứng dụng; không chứng minh hiệu quả của skill. |
| 5 | Dùng được, không hại phần đã có | ĐẠT MỘT PHẦN | Id mới không trùng skill của gói; phạm vi xây công cụ kiểm tra bãi tách khỏi báo cáo khai thác. Chưa kiểm chứng trên ứng dụng agent thật hoặc đủ hệ native; năng lực provider chưa kiểm trong mọi host. |
| 6 | Phạm vi tái dùng | UNKNOWN — CHƯA ĐỦ BẰNG CHỨNG | Mọi block, trạng thái, mã và ngưỡng riêng được chuyển thành câu hỏi/cấu hình cần project xác nhận. Chưa có bằng chứng sử dụng lại qua nhiều project hoặc người nhận. |

Gói vẫn `DEFER`/`SUPPLEMENT`. `pack.json` ghi phiên bản gói 0.3.0 nhưng trạng thái chưa thay đổi thành `AVAILABLE` hoặc `ROOT_ELIGIBLE`. Không có `root_grant`; không chạy `pack.py confirm`, không cài hoặc quảng bá ứng viên. Sáu điều kiện vẫn áp dụng cho làn builder; không dùng số lượng tác vụ hay kiểm thử của ứng dụng thay cho điều kiện 4 và 6. Làn phản hồi người nhận folder vẫn yêu cầu ba việc thật riêng biệt và đánh giá của người nhận.

## Cập nhật nội dung container-yard-check 0.1.1 (28/10/2026)

Bản skill và ba tài liệu tham khảo được bổ sung lại từ snapshot ứng viên đã fingerprint ở trên. Phần phục hồi gồm năm câu hỏi trước khi viết mã; nghĩa Stacking/Incoming/Outgoing như ví dụ có điều kiện; phép nhóm Bay/Row, RTG và lót pháo; ví dụ ISO theo F/E; tám sai lầm đã gặp; tám nhóm test; bảy bước đánh giá độc lập; khung spec PyInstaller, kiểm .exe và kiến trúc bảng chuẩn hóa. Snapshot nhắc năm loại ca lót pháo nhưng không liệt kê đủ từng loại, nên skill yêu cầu project xác nhận danh sách thay vì tự đặt tên.

Block, tiền tố, trạng thái TOS, mã ISO, ngưỡng và quy ước thời gian riêng vẫn cần project xác nhận; ví dụ ISO được ghi là ví dụ nguồn, không phải bảng quy đổi phổ quát. Việc phục hồi chỉ thay đổi nội dung hướng dẫn và version skill lên 0.1.1; không tạo bằng chứng mới về hiệu quả hoặc phạm vi tái dùng. Điều kiện 4 và 6 tiếp tục UNKNOWN/chưa đủ bằng chứng; quyết định gói vẫn DEFER/SUPPLEMENT, không cài đặt, confirm hay quảng bá.

## Còn thiếu trước khi cân nhắc tiếp nhận

1. Đối chiếu nguồn pháp lý của `port-operations-reports` với văn bản chính thức và ghi kết quả trong hồ sơ đó.
2. Thử từng skill trên ứng dụng agent thật với tác vụ đại diện, ca lỗi/thiếu nguồn và tác vụ ngoài phạm vi; ghi app/model/điều kiện, kết quả có thể đối chiếu và phản hồi người dùng.
3. Đánh giá riêng điều kiện 4 (hiệu quả của skill) và điều kiện 6 (phạm vi tái dùng); giữ `UNKNOWN`/chưa đủ nếu bằng chứng không phân biệt được tác dụng của skill.
4. Chỉ cập nhật quyết định intake sau khi người có thẩm quyền đọc hồ sơ và xác nhận. Mỗi project vẫn cần quyết định của người dùng; không suy quyền cài/confirm từ lần ghi vào bộ mẫu này.

### Bổ sung taxonomy nguồn ứng dụng, 28/10/2026

Bổ sung năm mã T1_DIRECT/T1_CARGO/T1_MISSING/MID_EMPTY/MID_MISSING vào reference nghiệp vụ từ bảng REASON_TITLES của ứng dụng V4.2.1. Đây là mẫu có điều kiện project xác nhận, không chuẩn ngành; chưa chạy lại app nguồn. Không nhập mã/installer hoặc thông tin block riêng. Giữ DEFER/SUPPLEMENT và điều kiện4/6 UNKNOWN; không cài/confirm/promote hoặc cập nhật bản cài.
