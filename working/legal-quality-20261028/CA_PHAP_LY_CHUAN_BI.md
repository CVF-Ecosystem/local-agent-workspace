# Bộ ca pháp lý — kiểm nội bộ do đội dev chuẩn bị

**Trạng thái: INTERNAL_TESTS_NOT_RUN / CORPUS_STAGED_FOR_TRIAL; đáp án chuyên môn NOT_APPROVED.** Đây là hồ sơ chuẩn bị thử nghiệm theo yêu cầu người dùng; không phải bộ đáp án chuẩn, không kết luận về hiệu lực hay áp dụng pháp luật, và không thay ý kiến pháp lý có thẩm quyền.

## Yêu cầu và người duyệt

Theo chỉ định mới nhất 28/10, đội agents dev tự chuẩn bị tình huống, dữ liệu, expected results có căn cứ, kiểm và review nội bộ để giao bản dùng được; không chờ người dùng tìm luật sư hoặc soạn đáp án mới tiếp tục. Người dùng duyệt mục tiêu/quyết định nghiệp vụ và đánh giá mức phù hợp sau đó. Việc người dùng dự kiến tìm luật sư thử là feedback bổ sung, không là dependency mặc định của toàn bộ ca.

Dev/reviewer có thể xác nhận expected results cơ học và kết quả đối chiếu trực tiếp nguồn trong phạm vi đã kiểm. Nhận định pháp lý sâu cần thẩm định: đội dev chuẩn bị ca/nguồn/rubric/câu hỏi, operator quyết định người duyệt và chi phí khi chưa có quyền; không tự mời/trả phí hoặc coi AI tự chấm là chứng nhận. Luật sư thử có thể cung cấp bằng chứng chuyên môn nếu phạm vi và kết quả thẩm định được ghi rõ; không tự mặc định phản hồi là đã duyệt. Chưa có gold chuyên môn được duyệt, chưa chỉ định chuyên gia; không tự gán người, thời hạn hoặc hạ scope đã cam kết.

## Nguồn đã chuẩn bị

Nguồn do người dùng chỉ định nằm ngoài kho LAW. Ba bản dưới đây chỉ là corpus làm việc để chuẩn bị ca thử, chưa được đưa vào references/ hoặc chỉ mục nguồn của project. Không trích dẫn chúng làm căn cứ cho tư vấn, không xác nhận hiệu lực, quan hệ sửa đổi/thay thế hay áp dụng cho tình huống cụ thể.

| Văn bản nhận diện từ tên/đầu trang DOCX | Đường dẫn nguồn người dùng | Bản sao làm việc | Bytes | SHA-256 nguồn và bản sao |
|---|---|---|---:|---|
| Luật số 31/2024/QH15, Luật Đất đai | D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\VanBanPhapLuat_DatDai\Van_Ban_Word\Luat_Dat_dai_2024_31_2024_QH15.docx | working/legal-quality-20261028/sources/Luat_Dat_dai_2024_31_2024_QH15.docx | 176853 | a4ace94b65643e463d564a491486428eefcfcd01b4a37eac2334337d9f0ff108 |
| Quyết định 100/2024/QĐ-UBND, về điều kiện tách/hợp thửa và diện tích tối thiểu tại TP Hồ Chí Minh | D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\VanBanPhapLuat_DatDai\Van_Ban_Word_TPHCM\Quyet_dinh_100_2024_QD_UBND_Dieu_kien_tach_thua_dat_TPHCM.docx | working/legal-quality-20261028/sources/Quyet_dinh_100_2024_QD_UBND_Dieu_kien_tach_thua_dat_TPHCM.docx | 40554 | 4c9516996eee83ae14688d491177df2f50900981c5204dc494786e123df69e0d |
| Quyết định 60/2017/QĐ-UBND, về diện tích tối thiểu được tách thửa tại TP Hồ Chí Minh | D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\VanBanPhapLuat_DatDai\Van_Ban_Word_TPHCM\Quyet_dinh_60_2017_QD_UBND_Tach_thua_dat_TPHCM.docx | working/legal-quality-20261028/sources/Quyet_dinh_60_2017_QD_UBND_Tach_thua_dat_TPHCM.docx | 43639 | 9d3a7e327fb6f43d3551cfe38ba6674e5fcd0d7b08d0816341b6394af32e2aeb |

Kiểm hash: đã so bytes nguồn và bản sao, cả ba cặp trùng khớp. Đã đọc cấu trúc ZIP/XML và các đoạn đầu để nhận diện số hiệu/tiêu đề; chưa đọc toàn văn để phân tích, chưa kiểm bảng/phụ lục, và chưa tạo bản trích xuất.

### Metadata trong CSV người dùng cung cấp

| Số hiệu | File CSV và LawID | Trường Link Chi Tiết (trang chi tiết) | Trường Link Tải Word (URL tab=7; chưa truy cập) | Trường Tình Trạng trong CSV |
|---|---|---|---|---|
| 31/2024/QH15 | Danh_muc_Van_ban_Dat_dai_Trung_uong.csv, LawID 523642 | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Luat-Dat-dai-2024-31-2024-QH15-523642.aspx | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Luat-Dat-dai-2024-31-2024-QH15-523642.aspx?tab=7 | Đang áp dụng |
| 100/2024/QĐ-UBND | Danh_muc_Van_ban_Dat_dai_TP_Ho_Chi_Minh.csv, LawID 629508 | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Quyet-dinh-100-2024-QD-UBND-dieu-kien-tach-thua-dieu-kien-hop-thua-dat-Ho-Chi-Minh-629508.aspx | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Quyet-dinh-100-2024-QD-UBND-dieu-kien-tach-thua-dieu-kien-hop-thua-dat-Ho-Chi-Minh-629508.aspx?tab=7 | Đang áp dụng |
| 60/2017/QĐ-UBND | Danh_muc_Van_ban_Dat_dai_TP_Ho_Chi_Minh.csv, LawID 369116 | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Quyet-dinh-60-2017-QD-UBND-quy-dinh-dien-tich-toi-thieu-duoc-tach-thua-Ho-Chi-Minh-369116.aspx | https://thuvienphapluat.vn/van-ban/Bat-dong-san/Quyet-dinh-60-2017-QD-UBND-quy-dinh-dien-tich-toi-thieu-duoc-tach-thua-Ho-Chi-Minh-369116.aspx?tab=7 | Đang áp dụng |

URL trên được chép từ hai trường trong CSV, chỉ ghi nhận trang chi tiết và trang tab=7 được liệt kê; không coi là đường tải trực tiếp, không xác nhận trang đã truy cập hoặc nội dung trang. Nhãn “Đang áp dụng” là claim của CSV, chưa đối chiếu nguồn chính thống. Các URL thuộc Thư Viện Pháp Luật, không được gắn nhãn nguồn chính thống.

## Kế hoạch sáu ca

Sáu ca dưới đây hiện chưa chạy. Đội dev chịu trách nhiệm điền đầu vào và expected results trước khi chạy: PL-Q1/Q2/Q3/S1 và phần giữ bản đúng của PL-R1 có thể dựng từ nguồn cố định/fixture được đánh dấu rõ, với đáp án cơ học và review ngữ cảnh theo nguồn; không cần end user làm oracle. PL-E1 và phần kết luận áp dụng pháp luật chỉ được công bố tới mức bằng chứng chuyên môn thực có. Không gắn nhãn ca đã đạt hoặc gold khi chưa kiểm; không dùng số ca làm ngưỡng nghiệm thu cố định.

| ID | Câu hỏi/đầu vào cần có | Lỗi cần phát hiện | Kiểm cơ học dự kiến | Trạng thái nội dung |
|---|---|---|---|---|
| PL-Q1 | Một nguồn đã vào thư viện, có phiên bản/hash và locator; yêu cầu trích đúng đoạn | Một ký tự bị đổi trong câu trích | Đoạn đúng khớp; bản đổi ký tự không khớp trong đúng range | Chưa có gold; chưa chạy |
| PL-Q2 | Hai đoạn trong cùng nguồn có câu chữ gần giống, mỗi đoạn có locator riêng | Trích đúng chữ nhưng dẫn sai điều/khoản/range | Không khớp nếu đoạn trích không nằm trong range đã khai báo; locator vẫn cần người kiểm | Chưa có gold; chưa chạy |
| PL-Q3 | Hai phiên bản nguồn cố định do đội dev chuẩn bị trong quyền đã cấp, có hash và lịch sử cần thiết | Dùng trích dẫn của phiên bản A như căn cứ cho phiên bản B | Phiên bản hoặc hash lệch phải UNVERIFIED; không gắn hash mới vào trích dẫn cũ | Chưa có đủ cặp phiên bản; chưa chạy |
| PL-E1 | Thời điểm vụ việc và các văn bản gốc, sửa đổi/thay thế/chuyển tiếp có thể liên quan | Nhầm ngày ban hành với ngày hiệu lực hoặc bỏ mốc thời gian | Công cụ quote không xác nhận hiệu lực; việc đó phải dừng ở review nguồn | Chưa có hồ sơ/gold; chưa chạy |
| PL-S1 | Nguồn thiếu, xung đột, OCR/bảng hoặc trích xuất chưa kiểm | Trình bày chắc chắn như trích nguyên văn từ dữ liệu không chắc | Phần không kiểm được phải UNVERIFIED; không nâng thành MATCH bằng fuzzy | Chưa có nguồn lỗi; chưa chạy |
| PL-R1 | Bản trả lời v1, lý do cần sửa và đúng phiên bản đầu vào | Sửa lỗi nhưng làm mất câu đúng hoặc mở nhầm bản | Giữ nguyên phần trích/range đúng; nhận diện revision đang dùng | Chưa có câu trả lời được duyệt; chưa chạy |

Bộ ca vẫn là kế hoạch, chưa tạo đáp án nội dung cho ba DOCX. Các đầu vào/expected còn thiếu do đội dev chuẩn bị trong mốc chất lượng V4/V7, không ghi thành chờ user. Review nội bộ phải chỉ ra căn cứ và phần chưa kiểm; gold chuyên môn/feedback thực tế vẫn chưa có.

## Cổng trước khi một ca được đánh giá

- Với ca phát triển, đội dev tự dựng câu hỏi, hành vi, địa bàn và thời điểm từ nguồn cố định hoặc fixture giả lập được ghi rõ; không trình bày thành vụ việc người dùng thật. Với công việc thực tế mới hỏi user dữ kiện nghiệp vụ còn thiếu.
- Nguồn được đưa vào thư viện project và có ID/revision/hash; phần văn bản dùng để kiểm đã đọc được, xác định locator và ngày kiểm.
- Nếu ca có khẳng định hiệu lực/áp dụng, đội dev đối chiếu nguồn chính thống tại thời điểm của ca và tổ chức review chuyên môn khi cần. Ca chỉ kiểm hash/locator/khớp chuỗi dùng nguồn cố định không cần khẳng định hiệu lực hiện hành. CSV, tên file hoặc hash không chứng minh hiệu lực hay quan hệ văn bản.
- Expected cơ học và các ý bắt buộc có căn cứ được dev lập, reviewer kiểm độc lập đúng revision trước chạy. Chuyên gia xác nhận phần kết luận cần chuyên môn khi capability đòi hỏi; chưa có thì phần ấy vẫn NOT_APPROVED. Không bắt user duyệt test hoặc coi review AI là duyệt chuyên môn.
- Tách kiểm exact quote, locator, số liệu và nguồn khỏi đánh giá ngữ cảnh, hiệu lực, ngoại lệ và suy luận pháp lý. MATCH của tools/check_quotes.py không thay các đánh giá này.
- Khi corpus có DOCX, PDF scan, bảng hoặc ảnh, chưa dùng làm nguồn trích chính thức cho checker đến khi quá trình trích xuất được kiểm; nếu chưa kiểm thì đánh dấu UNVERIFIED.

## Phạm vi chưa hoàn tất

Lần đồng bộ này sửa trách nhiệm và điều kiện chạy, chưa thực hiện sáu ca, đối chiếu hiệu lực hoặc thêm sổ nguồn. Đội dev phải tiếp phần corpus/expected/kiểm nguồn, chạy và review trong mốc hiện có; không chờ user để chuẩn bị nội bộ. Chuyên môn sâu chưa có bằng chứng giữ giới hạn tương ứng; không tự bỏ scope đã cam kết. Người dùng giữ quyết định nghiệp vụ, quyền cài/tiếp nhận/publish và feedback độ phù hợp sau bản dùng được. DEFER/REVIEW giữ nguyên; không có gold chuyên môn hoặc lawyer trial mới.
