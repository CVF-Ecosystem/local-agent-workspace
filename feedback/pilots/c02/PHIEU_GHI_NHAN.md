# Phiếu ghi nhận pilot C-02 (biểu mẫu trống)

**Trạng thái: NOT_RUN.** Mọi ô để trống. Chưa có người thử, chưa có lượt chạy. Không điền thử, không điền mẫu, không suy số.
Chỉ người điều phối hoặc người quan sát của một lượt thật mới điền, và chỉ điều thật sự quan sát được. Ô không biết ghi "chưa đo" hoặc
"không quan sát được", không để 0 hay đoán.

Dùng một bản chép cho mỗi người thử và mỗi nhánh. Đây là phần ghi hành vi; lời nhắc nguyên văn và khai báo của agent ở bản ghi theo
[TEMPLATE](../../TEMPLATE.md) trong `feedback/records/`, nối qua đường dẫn ở mục A. Cách chạy và oracle: [DIEU_PHOI.md](DIEU_PHOI.md).
Phiếu này không đưa cho người thử.

## A. Định danh lượt

| Trường | Giá trị |
|---|---|
| Mã ẩn danh người thử (không tên thật) | |
| Nhánh (L = LAW, N = native) | |
| Thứ tự trong buổi (1 hoặc 2) và nhánh làm trước | |
| Ngày | |
| Người quan sát (mã hoặc vai) | |
| Host/ứng dụng và phiên bản (quan sát được) | |
| Loại account (không ghi key, tên đăng nhập hay email) | |
| Model quan sát được | |
| Effort quan sát được hoặc "không quan sát được" | |
| OS và dependency liên quan | |
| Artifact thực dùng: release/tag, source commit, ZIP và SHA-256; hash gate/checksum | |
| Cây đối chiếu đã giải nén: đường dẫn, SHA-256 `MANIFEST.sha256`, thời điểm kiểm; tách khỏi bản chép người thử | |
| Thư mục pilot của lượt (A, B) | |
| Mức quen với ứng dụng AI thông thường (tự khai) | |
| Đã từng dùng LAW? (phải là "chưa") | |
| Bản ghi feedback theo TEMPLATE (đường dẫn) | |

## B. Gate trước chạy

| # | Điều kiện | Trạng thái (đã đạt / chưa / không áp dụng) | Bằng chứng |
|---|---|---|---|
| G1 | Có người thử thật, đã đồng ý | | |
| G2 | Người/môi trường/giới hạn thực tế đã xác nhận (Q1–Q5; Q10 nếu ghi hình) | | |
| G3 | Snapshot và nguồn đã freeze, có hash | | |
| G4 | Thư mục pilot tách biệt | | |
| G5 | Oracle đã đối chiếu; thứ tự và phạm vi định tính theo DIEU_PHOI mục 5 | | |
| G6 | Người quan sát biết cách ghi hỗ trợ | | |
| G7 | Nguồn B đã tạo và có hash | | |

Kết luận gate: ☐ đủ, chạy được  ☐ thiếu, giữ **NOT_RUN** (không chi phí, không mời, không chạy host).

Hash nguồn lúc bắt đầu: `meeting_notes.txt` ____ · `procedure_v1.md` ____ · `procedure_v2.md` ____ · nguồn B ____

## C. Thời gian

Mỗi ô: số phút/giây và nguồn đo (đồng hồ người quan sát, log ứng dụng, khác); không có thì "chưa đo".

| Việc | Setup | Tìm nguồn | Thực hiện | Sửa | Gián đoạn | Nguồn đo |
|---|---|---|---|---|---|---|
| Làm quen (hướng dẫn, mở ứng dụng) | | | | | | |
| 1a Biên bản | | | | | | |
| 1b So sánh quy trình | | | | | | |
| 2 Mở lại, đúng revision | | | | | | |
| 3 Biên bản B | | | | | | |

## D. Hỗ trợ và can thiệp

Một dòng cho mỗi lần. Loại: làm rõ đề / chỉ nơi đọc / chỉ cách làm / làm thay / khác.

| # | Thời điểm | Việc | Ai nói | Loại | Nguyên văn nội dung hỗ trợ | Kết quả bị đánh dấu "có hỗ trợ"? |
|---|---|---|---|---|---|---|
| | | | | | | |

| Tổng hợp theo việc | 1a | 1b | 2 | 3 |
|---|---|---|---|---|
| Số lần người thử phải giải thích lại cho AI | | | | |
| Số lần người quan sát hỗ trợ | | | | |
| Số bước cần hỗ trợ | | | | |

## E. Lời nhắc của người thử (nguyên văn)

Dán nguyên văn hoặc ghi đường dẫn tới bản ghi. Không do điều phối soạn hộ.

| # | Việc | Nguyên văn lời nhắc | Có tham khảo ví dụ lời nhắc trong tài liệu? (tài liệu nào) | Có nêu rõ "cần xác nhận" hoặc "suy luận" trong lời nhắc? |
|---|---|---|---|---|
| | | | | |

Tiếp xúc ví dụ/đáp án (bao gồm README demo và oracle điều phối); ghi cả người thử và AI:

| Ai đọc / nguồn bằng chứng | File/đoạn đã thấy | Trước/sau việc nào | Tiêu chí bị ảnh hưởng | Đã lộ / xác minh chưa lộ / chưa xác minh |
|---|---|---|---|---|
| | | | | |

Đã lộ hoặc chưa xác minh thì tiêu chí nội dung liên quan **không đánh giá được về tính độc lập**; không coi ô NT/HT là bằng chứng không lộ. Thao tác không phụ thuộc đáp án ghi riêng.

Cách làm người thử muốn giữ (cuối Việc 1, nguyên văn):

## F. Artifact

| Việc | Đường dẫn file | Loại | SHA-256 khi người thử xác nhận | Tạo bởi (AI / người thử) |
|---|---|---|---|---|
| 1a | | | | |
| 1b | | | | |
| 2 (bản so sánh hiện hành) | | | | |
| 3 | | | | |

Hash lúc đóng phiên Việc 1: biên bản ____ · so sánh ____

## G. Chấm theo oracle

Mã và nội dung đầy đủ ở mục 6 của DIEU_PHOI. Mỗi dòng: **đạt / chưa đạt / không đánh giá được**, kèm bằng chứng (đường dẫn, câu trích, hash). Cột cuối: "NT" nếu người thử yêu cầu
rõ trong lời nhắc, "HT" nếu không thấy yêu cầu rõ nhưng đầu ra có, "?" nếu chưa rõ. HT chưa chứng minh nguyên nhân do LAW; áp dụng mục E và kiểm nhiễm chéo mục L trước khi chấm.

| Mã | Điều cần thấy (rút gọn) | Kết quả | NT / HT / ? | Bằng chứng |
|---|---|---|---|---|
| BB1 | Ba nhóm tách rõ | | | |
| BB2 | Hai quyết định đúng | | | |
| BB3 | Việc có người đúng; mốc "từ tuần sau" nguyên văn | | | |
| BB4 | Thu không bị gán mẫu phiếu | | | |
| BB5 | Việc hỏi anh Đức: người hỏi/hạn "cần xác nhận" | | | |
| BB6 | Lỗi 10 MB: không biến thành việc giao Hùng | | | |
| BB7 | Vấn đề chưa chốt: gộp kênh; không ngày | | | |
| BB8 | Không bịa số liệu, vai trò, hạn | | | |
| BB9 | Lưu file và nêu nguồn | | | |
| SS1 | Bảng gồm bước 4, 5, 6, 7 | | | |
| SS2 | Bước 1, 2, 3 không như thay đổi | | | |
| SS3 | Giá trị đúng từng bước | | | |
| SS4 | Ảnh hưởng gắn nhãn suy luận | | | |
| SS5 | Không thêm điều nguồn không nói | | | |
| SS6 | Lưu file và nêu nguồn đúng | | | |
| LT1 | Tìm lại đúng bản, không làm lại để xem | | | |
| LT2 | Nêu đúng nguồn mỗi bản | | | |
| LT3 | Nhận ra `procedure_v2.md` đã đổi (ai/cái gì, lúc nào) | | | |
| LT4 | Không dùng dòng bước 5 cũ như hiện hành | | | |
| LT5 | Bản hiện hành bước 5: 5 xuống 4 | | | |
| LT6 | Bản cũ còn nguyên; bản mới phân biệt được | | | |
| LT7 | Biên bản không bị báo sai hay tạo lại thừa | | | |
| LT8 | Không sửa hay ghi đè nguồn | | | |
| DL1 | Dùng đúng nguồn B | | | |
| DL2 | Không có dữ liệu A trong đầu ra B | | | |
| DL3 | Hai quyết định B đúng | | | |
| DL4 | Việc có người B; mốc nguyên văn | | | |
| DL5 | Không gán sai Nga, Quân, Trang | | | |
| DL6 | Vấn đề chưa chốt B | | | |
| DL7 | Cách làm đã chọn được áp dụng (bằng đường nào) | | | |
| DL8 | Không mang quyền/STATE/đầu ra A sang B; A không đổi | | | |
| DL9 | Ghi nhận: đường dùng lại, chênh lệch bộ mẫu so với snapshot | | | |

DL9 chỉ ghi nhận đường đi và bằng chứng, không chấm đạt/chưa đạt; các mã còn lại áp dụng điều kiện hợp lệ ở mục E và L.

Cơ chế phiên mới biết việc cũ ở Mốc 2: ☐ STATE/HANDOFF ☐ đọc thư mục ☐ sổ nguồn ☐ bộ nhớ hoặc lịch sử host ☐ người thử tự kể ☐ khác: ____
Cơ chế nhận ra thay đổi nguồn: ☐ UI ☐ chỉ mục ☐ so hash ☐ AI đọc lại nguồn ☐ người thử ☐ không có ☐ khác: ____

## H. Lỗi

| # | Loại (stale / ghi nhầm / báo sai / khác) | Việc | Mô tả | Bằng chứng |
|---|---|---|---|---|
| | | | | |

## I. Chi phí

Chỉ ghi số có nguồn quan sát được. Không có số thì "chưa đo".

| Phạm vi (phiên / việc / account) | Số | Đơn vị | Nguồn (hóa đơn, bảng sử dụng, telemetry) | Thời điểm đọc |
|---|---|---|---|---|
| | | | | |

## J. Phân loại theo mốc

Chọn một: hoàn thành độc lập / hoàn thành có hỗ trợ / chưa hoàn thành / không đánh giá được; gắn bằng chứng. Không có ngưỡng đạt trong phiếu này. Mốc lộ đáp án/nhiễm chéo không được gọi là độc lập hoàn thành nội dung; ghi phần thao tác còn quan sát được riêng.

| Mốc | Phân loại | Bằng chứng |
|---|---|---|
| 1 (1a, 1b) | | |
| 2 | | |
| 3 | | |

## K. Sự cố môi trường và phần chưa kiểm

| Việc | Thông báo người thử nhìn thấy (nguyên văn) | Cách báo bằng lời người dùng | Phần chưa kiểm |
|---|---|---|---|
| | | | |

## L. Điều kiện tương đương hai nhánh

| Điều kiện | Nhánh L | Nhánh N | Tương đương? |
|---|---|---|---|
| Host, account, model, effort | | | |
| Bộ nhớ/context/project đã kiểm (bằng chứng gì; chưa xác minh thì ghi rõ) | | | |
| Nguồn và hash | | | |
| Mục tiêu và quyền đọc/ghi | | | |
| Thứ tự, thời gian làm quen, hiệu ứng học | | | |
| Ghi chú khác | | | |

Lượt đầu L→N dùng cùng nguồn chỉ ghi nhận định tính, không tính chênh lệch như hiệu quả LAW. Có điều kiện không tương đương hoặc context chứa kết quả nhánh trước thì tiêu chí phụ thuộc không đánh giá được; ghi dấu nhiễm chéo, không chỉ một dòng ghi chú rồi chấm độc lập.

## M. Cảm nhận của người thử (riêng, nguyên văn)

Phiếu [FEEDBACK_FORM_VI_EN.md](../../../docs/FEEDBACK_FORM_VI_EN.md) hoặc lời nói đã che, do người thử tự điền hoặc nói. Không trộn với quan sát hành vi hay kết quả công cụ.

## N. Chấp nhận của người dùng

Chỉ người thử hoặc operator thật ghi. Agent không điền. ☐ chưa hỏi ☐ chấp nhận ☐ không chấp nhận ☐ chấp nhận có điều kiện: ____

## O. Khai báo thực hiện của agent

| Việc | Có khối khai báo? | Kết quả `check_output.py --declaration` (nhánh L, nếu chạy) | Đường dẫn bản lưu |
|---|---|---|---|
| | | | |

## P. Điều chưa kiểm và ghi chú

| Người điền (mã) | Ngày |
|---|---|
| | |
