# Hồ sơ tiếp nhận: gói van-thu-luu-tru bản 0.2.0

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
| 6 | Phạm vi tái dùng | CHƯA ĐỦ BẰNG CHỨNG | Quy tắc riêng đơn vị đã tách ra skill của project (theo README gói). Chưa có ba việc thật của người dùng trong lĩnh vực này theo làn nhận folder (`packs/README.md`); đây không phải ngưỡng của làn builder. Builder còn thiếu bằng chứng ca đại diện chứng minh phần chung dùng lại được, tách khỏi quy tắc/dữ liệu riêng. |

## Phép thử A/B (qwen-plus, Alibaba Model Studio, 14/10/2026)

Tiêu chí đặt trước khi chạy, chấm bằng quy tắc cơ học trên văn bản trả lời. A: cùng `AGENTS.md`, không có skill. B: A thêm SKILL.md và references của gói, ghi rõ là bản `REVIEW`.
Dữ liệu giả; không có công cụ; mỗi ô chạy 2 lần.

| Tiêu chí | A (không skill) | B (có skill) |
|---|---|---|
| Ghi chỗ chưa kiểm / cần xác nhận | 0/2 | 2/2 |
| Nêu số hiệu văn bản | 2/2 | 2/2 |
| Có khối "Khai báo thực hiện" | 1/2 | 0/2 |
| Có đoạn trình bày như trích nguyên văn (không có toàn văn trong gói) | 1/2 | 0/2 |

Nhận xét riêng của gói: Không có đáp án đã biết. Bản có skill ghi chỗ chưa kiểm tốt hơn (2/2 so với 0/2) nhưng không có khối khai báo thực hiện (0/2 so với 1/2).

## Còn thiếu để chuyển sang `ADD_MISSING_PART` (hoặc `PROJECT_ONLY`)

1. Người có thẩm quyền đối chiếu bảng căn cứ `packs/van-thu-luu-tru/skills/records-management-vn/references/legal-basis.md` với văn bản chính thức và ghi kết quả (điều kiện 2).
2. Theo làn builder: đội dev tự chuẩn bị và kiểm ca đại diện, thiếu nguồn/lỗi và ngoài phạm vi theo rủi ro trên bản/host công bố; expected có căn cứ và review phù hợp, có bằng chứng hiệu quả của skill và tái dùng phần chung (điều kiện 4 và 6), không ngưỡng số việc cứng. Nếu nhận theo làn folder, giữ điều kiện ít nhất ba việc thật trong ứng dụng agent và đánh giá người nhận; không dùng ngưỡng đó để chặn nghiệm thu nội bộ builder. Feedback mức phù hợp đến sau bản dùng được.
3. Đội dev sửa và kiểm hồi quy lỗi trình bày đoạn "nguyên văn" không có trong nguồn (điều kiện 4). Chưa sửa thì giữ claim phụ thuộc chưa đạt, gói thử nghiệm chỉ tham khảo/soạn nháp; không nhận khả năng sẵn dùng bằng cách ghi giới hạn cho trích dẫn sai. Đối chiếu phải dựa đúng toàn văn nguồn, không chỉ đối chiếu lời trong gói.
4. Chỉ khi 1-3 xong mới đổi `intake.decision` và nâng `intake.version` theo bản đã xét. Đó vẫn chỉ là lời khai của gói: người dùng ở từng project
   tự đọc hồ sơ rồi chạy một lệnh (`pack.py add <tên> --confirm` hoặc `pack.py confirm <tên>`) thì skill mới thành `AVAILABLE`.

Giới hạn của phép thử này: một model, mỗi ô 2 lần, tiêu chí cơ học nên bỏ sót chất lượng diễn đạt; agent tự chấm không phải nghiệm thu của người dùng. Kết quả không nói gì về model khác.

## Nghiệm thu nội bộ trước feedback — cập nhật 29/10/2026

Phần này làm rõ làn builder theo [chuẩn chung](../../../skills/README.md#developer-product-acceptance), không sửa kết quả A/B lịch sử phía trên hoặc tuyên bố đã có thử nghiệm mới. Sáu điều kiện, `DEFER`/phiên bản/quan hệ và quyền xác nhận từng project giữ nguyên. Đội dev sở hữu ca, nguồn, expected, kiểm/review và việc tổ chức thẩm định chuyên môn khi capability cần; quyền mời/trả phí vẫn cần được cấp. Người dùng quyết định nghiệp vụ và feedback mức phù hợp, không phải QA kỹ thuật.

| Câu hỏi | Hồ sơ hiện tại và phần còn phải đóng |
|---|---|
| 1. Làm việc gì, khi nào dùng? | Tổ chức sổ, hồ sơ và bản nháp văn thư theo nguồn/mẫu được giao; chưa dùng căn cứ gói để trình ký. |
| 2. Đầu ra đạt chuẩn nào? | Đúng nguồn/số/ngày/tên, tách đề xuất/quyết định và phần chưa kiểm; quote phải đối chiếu nguyên văn có locator. Không bịa người ký, thẩm quyền, hạn hoặc căn cứ. Format công bố phải được kiểm tương ứng trên bản giao. |
| 3. Đã chứng minh bằng gì? | Giữ nguyên phép thử A/B và giới hạn đã ghi trong hồ sơ; chưa có kết luận nghiệm thu nội bộ đầy đủ của phiên bản hiện tại. Source/metadata hay kiểm cấu trúc không thay content/host acceptance. Nguồn hoặc thẩm định chưa đủ vẫn chặn claim phụ thuộc, không chặn phép kiểm độc lập khác. |
| 4. Phần tăng thêm cụ thể là gì? | Mẫu sổ/danh mục và quy tắc tổ chức hồ sơ; đối chiếu mẫu lịch sử không chứng minh toàn bộ căn cứ hiện hành. Cần chứng minh đúng phần đó bằng ca/nguồn đối chiếu công bằng; không tuyên bố hơn native hoặc dùng số test của ứng dụng thay bằng chứng hiệu quả skill. |
| 5. Bản giao dùng ở đâu, bằng luồng nào? | Gói đi cùng package tại thư mục này; chỉ dùng thử trong project đã được người dùng đặt/cài theo quyền, status REVIEW. Dev còn phải chứng minh luồng nhận yêu cầu→đọc nguồn→soạn/kiểm→sửa/tiếp việc trên artifact/host công bố và bảo toàn phần riêng. Không confirm/promote từ lần bổ sung hồ sơ này. |

Điều kiện phát lại: nguồn/candidate/claim/host hoặc hướng dẫn đổi thì kiểm đúng phần bị ảnh hưởng. Lỗi quote thiếu nguồn là blocker nội dung, không xử lý bằng disclaimer; nguồn chưa đối chiếu ghi rõ chưa kiểm, không trình bày như căn cứ hiện hành. Ngưỡng ba việc thật của làn nhận folder vẫn giữ khi áp dụng; không biến nó thành quota thử nội bộ builder hoặc yêu cầu noncoder tìm người test.
