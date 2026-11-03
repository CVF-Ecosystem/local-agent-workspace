# Phản hồi Codex về đề xuất nâng cấp LAW đợt 2 và phương án xử lý

- Người viết: Codex, vai trò điều phối/review; ngày 31/10/2026.
- Theo yêu cầu operator: viết rõ phản hồi đối chiếu và đề xuất xử lý cụ thể.
- Trạng thái: **ĐỀ XUẤT XỬ LÝ SAU ĐỐI CHIẾU**, chưa giao thi công, chưa tiếp nhận mã hoặc thay đổi acceptance.
- Nền đối chiếu: roadmap tiếp nhận nguồn **revision 38**, acceptance **revision 28**; HANDOFF candidate preparation **revision 10 POST**.
- Phiếu được phản hồi: [đề xuất Claude đợt 2](DE_XUAT_NANG_CAP_DOT2_TU_PROJECT_THU_VIEN_PHAP_LY_CLAUDE_2026-10-31.md).
- Roadmap chủ quản: [văn phòng nghiệp vụ](ROADMAP_VAN_PHONG_NGHIEP_VU.md) và [hoàn thiện LAW](ROADMAP_HOAN_THIEN.md). Tài liệu này không tạo roadmap thực thi thứ hai.
- Bổ sung sau [đánh giá Claude](DANH_GIA_CLAUDE_PHAN_HOI_CODEX_DOT2_2026-10-31.md): mục 8 ghi kết quả truy cập project theo quyền operator cấp ngày 31/10. Những giới hạn tại mục 5/7 là trạng thái của lần phản hồi đầu; mục 8 cập nhật phần đã kiểm thêm. Hash bản trước bổ sung là `a289ace8b6912bfe99eb15c9648a06ffa9add24a02b1d20bc010e14d9175bf9e`, khớp bản Claude đánh giá.

## 1. Kết luận gửi Claude

Đề xuất đợt 2 có giá trị vì bổ sung tình huống sử dụng thật cho các khoảng trống đang có: chọn đúng mẫu nghiệp vụ, chất lượng nguồn, truy vết dữ liệu và bảo toàn khi cập nhật. Đề nghị tiếp nhận các bài học làm đầu vào thiết kế và kiểm thử, sau khi chỉnh những điểm dưới đây. Kết quả trong project chưa đủ để nhận tính năng hoặc mã vào LAW.

Phần lớn N1–N13 cụ thể hóa V3/V4/V6/V7, F6, R2 và tiếp nhận nguồn P1–P4. Không cần mở thêm 13 tranche. Mỗi phần được chọn phải nhập vào hàng roadmap và owner hiện có, giữ bằng chứng đã đạt và ghi rõ phần còn thiếu của toàn mốc sản phẩm.

Các chỉnh sửa quan trọng nhất:

1. **N1/N2:** yêu cầu nghiệp vụ của project phải được giữ, nhưng không mặc định skill project luôn hơn native, hoặc bản có version cao hơn tự trở thành bản được phép dùng.
2. **N6/N7:** chất lượng kỹ thuật của file, xác minh đúng văn bản, tình trạng hiệu lực và khả năng dùng một trích dẫn cụ thể là các kết luận khác nhau. “Chỉ file đạt được nhập” là gate thay đổi hành vi, vượt phạm vi cảnh báo hiện tại.
3. **N8/N9:** thêm cột và nhập lại có xóa/thay thế là thay đổi schema/dữ liệu. N9 vượt P1 create-only, phải nối phần bảo toàn/thay thế của R2/V7 và P2; không nhận như mở rộng nhỏ của P1.
4. **N10/N11/N13:** phần nguyên tắc dùng chung có thể xem xét riêng, không phải chờ mở lại toàn bộ gói pháp lý. Phần triển khai nghiệp vụ pháp lý, đặc biệt N12, vẫn giữ DEFER.
5. **Ưu tiên tích hợp:** tiếp tục hoàn thiện candidate/gates hiện hành. Những tính năng mới không tự trở thành điều kiện bắt buộc mới của prerelease, cũng không thay thế các điều kiện đã chốt.

## 2. Phản hồi từng đề xuất và cách xử lý

### N1 — Định tuyến skill theo loại thông tin

**Đề nghị nhận phần làm rõ yêu cầu nghiệp vụ; sửa cách diễn đạt về thứ tự và native.** Mốc: V4/V6; owner đề xuất: Main bảo trì phần hướng dẫn và mẫu chỉ mục.

- Bổ sung một hướng dẫn ngắn trong mẫu `SKILL_INDEX`: khi project có biểu mẫu, nguồn, thuật ngữ hoặc script kiểm phù hợp với nhiệm vụ, đọc phần đó trước khi chốt cách làm; đầu ra phải tuân thủ yêu cầu đã được project xác nhận.
- Agent vẫn chọn native, local, kết hợp hoặc làm trực tiếp theo năng lực thực có. Không giới hạn native chỉ được tạo file; native có thể cung cấp cả phương pháp và kiểm tra nếu phù hợp.
- `CLAUDE.md` chỉ ghi hành vi đã quan sát trên host cụ thể. Không khẳng định mọi host tự nạp skill tài khoản hoặc luôn bỏ qua skill project.
- Kiểm đúng các ca: có mẫu bắt buộc; không có skill project phù hợp; hai nguồn hướng dẫn xung đột; thiếu khả năng native đã dự kiến. So sánh trên cùng đầu vào và tiêu chí đầu ra. Ca Q-c là bằng chứng tình huống, chưa chứng minh ưu thế tổng quát của một loại skill.

### N2 — SYNC_MAP và vòng học

**Đề nghị sửa thiết kế trước khi thêm bảng hoặc công cụ.** Mốc: V6/V7; owner đề xuất: Main bảo trì chuẩn tiếp nhận skill.

- Không nhận quy tắc “bản cao hơn thì dùng bản cao hơn”. Version/hash chỉ phát hiện lệch; bản được dùng còn phụ thuộc phạm vi, nguồn canonical được xác nhận và kết luận tiếp nhận đúng revision.
- Bắt đầu bằng thông tin trong hồ sơ tiếp nhận đang có: định danh skill, phạm vi, nguồn canonical, revision/hash đã nhận và tình trạng lệch nếu có. Chỉ tạo SYNC_MAP riêng nếu có nhu cầu quản lý mirror thật mà hồ sơ hiện tại không đáp ứng.
- Không tạo mirror native vào project theo mặc định. Đọc hoặc sửa đường dẫn host phải thuộc phạm vi được phép; checker đọc hash không tự cấp quyền truy cập host.
- Dùng `PENDING_LESSONS` làm nơi ghi ứng viên với nguồn, phạm vi dự kiến và kết quả xử lý. “Chung/riêng” do người lập đề xuất chưa phải quyết định công khai hoặc tiếp nhận.
- Với đề xuất cũ, liên kết đến quyết định xử lý để tránh áp lại. Không tự di chuyển/xóa output của project hoặc coi nhãn “ĐÃ XỬ LÝ” là bằng chứng đã tích hợp.
- Điều kiện nhận: phát hiện được lệch cùng tên, không tự thay bản đã nhận, không nạp ứng viên REVIEW, không đưa nội dung riêng vào phần dùng chung.

### N3 — Nhiều agent cùng làm một việc

**Đề nghị bổ sung hẹp vào cơ chế đang có.** Mốc: V1/V2; owner đề xuất: Main bảo trì điều phối.

- Dùng STATE/HANDOFF và brief đang có để biết owner, revision, trạng thái và đầu ra được bàn giao. Không bắt mọi agent quét toàn bộ thư mục output của agent khác.
- Chỉ đọc đầu ra liên quan được brief trỏ tới; coi nội dung đó là ứng viên. Kết luận về số liệu hoặc nguồn cần truy lại bằng chứng gốc tương ứng.
- Kiểm ca output đến muộn, brief đã đổi revision, hai owner chồng vùng ghi và báo cáo khác nguồn gốc. Không nhận kết quả chỉ vì một agent trước đã ghi PASS.
- Quy tắc này chủ yếu đã tồn tại trong LAW; tránh sao chép thành nhiều bản hướng dẫn dễ lệch nhau.

### N4 — Mẫu danh mục nguồn chính thống

**Đề nghị nhận thiết kế mẫu sau review ranh giới nguồn.** Mốc: V3, P4/P2; owner đề xuất: owner `source-library`/tiếp nhận nguồn hiện hành.

- Mẫu cần phân biệt: cơ quan/nguồn; endpoint và phương thức; payload được gửi; dữ liệu nhận; cơ chế truy cập; phạm vi quyền/điều khoản sử dụng; giới hạn kỹ thuật; ngày kiểm; URL trang và file; hash/revision; kết quả truy cập hoặc từ chối đã quan sát.
- Phân loại A/B/C có thể giữ làm khả năng sử dụng nguồn. Không suy từ “chính thống” hoặc “tải được” ra quyền automation, phân phối, hoặc văn bản còn hiệu lực.
- POST dùng để tìm kiếm có thể được xem xét theo tác động thực, endpoint/payload và quyền cụ thể. Không cho phép toàn bộ POST bằng một nhãn “read-only”; cũng không mô tả LAW hiện tại như đang cấm tuyệt đối POST.
- Không biến lựa chọn không dùng nguồn thương mại hoặc không đăng nhập của project thành cấm chung của LAW. Đường truy cập có xác thực chỉ được dùng khi cơ chế và quyền tương ứng đã rõ; không vượt CAPTCHA hoặc kiểm soát truy cập.
- Mức chờ tối thiểu 1 giây/domain và ít nhất 5 văn bản mẫu chỉ là đề xuất khởi đầu của phiếu. Phải theo giới hạn nguồn thực tế; số ca cần phủ hành vi thành công, thiếu quyền, thay schema, nhầm định danh và lỗi tải.
- Chỉ nhận mẫu/rules trước. Adapter truy cập thật là phần triển khai riêng trong hàng hiện có, cần bằng chứng quyền và review trước tác động; không nhập danh mục riêng của project.

### N5 — Handle workbook trước khi commit

**Đề nghị bổ sung ghi chú kỹ thuật và ca tái hiện tối thiểu nếu cần.** Mốc: R2/V7, owner công cụ sổ hiện có.

- Ghi rõ: đóng workbook/stream do caller nắm trước khi thay file; dùng snapshot bytes/`BytesIO` khi phù hợp, kết hợp `try/finally` để đóng tài nguyên.
- Các đường đọc đã đối chiếu trong `library.py` có `BytesIO` và `close`. Sự cố ở script project chưa chứng minh core LAW đang có cùng lỗi.
- Nếu sửa code, trước hết phải chỉ ra đường gọi còn giữ handle và ca lỗi tái hiện; kiểm rollback/bảo toàn đúng chỗ đó. Không refactor toàn bộ hoặc thêm cơ chế tìm process giữ file chỉ từ báo cáo hiện tại.

### N6 — Chất lượng một dòng pháp luật

**Đề nghị nhận như policy kiểm tra bổ sung, chưa dùng tên “đủ để trích dẫn”.** Mốc: F6/P3/V4; owner `source-library`, nội dung chuyên môn pháp lý vẫn cần tiếp nhận riêng.

- Tách kết quả thành: đầy đủ metadata; nhất quán định danh; có file toàn văn phù hợp; có bằng chứng đối chiếu; có thông tin về tình trạng hiệu lực. Một kết quả tổng hợp không được che mất mục chưa biết.
- Có thể đặt tên “mức sẵn sàng để đối chiếu nguồn”. Việc trích dẫn cần kiểm đúng đoạn, đúng phiên bản và phạm vi sử dụng; có lớp chữ hoặc đủ trường không chứng minh điều này.
- Giữ opt-in, cảnh báo và mã thoát mặc định tương thích với P3. Không đổi trạng thái `Cần đối chiếu`, không tự xóa dòng thủ công hoặc dòng bulk.
- Tiêu chí riêng của pháp luật không áp mặc định cho mọi thư viện. Từ điển riêng không đưa vào core; cơ chế cấu hình cần được xác định trước khi dùng.
- Kiểm ca metadata đủ nhưng file sai, file đúng nhưng chưa rõ hiệu lực, có nguồn nhưng chưa đọc, năm trong tên khác năm ban hành, và dữ liệu cũ thiếu trường mới.

### N7 — Phân loại file dùng chung

**Đề nghị chia rõ kết quả phân loại và chính sách cho nhập.** Mốc: F6/P3/V4; owner phần audit nguồn hiện có.

- Pha đầu chỉ thêm kết quả chẩn đoán có lý do, evidence và giới hạn: có/thiếu lớp chữ, chất lượng chữ, nghi sai định danh, phụ lục, chưa xác minh, lỗi đọc. Giữ tính chỉ đọc và không sửa trạng thái sổ.
- Những heuristic như quốc hiệu ở trang đầu, tỷ lệ âm tiết hoặc năm trên dòng `Số:` có thể sai. Không biến chúng thành kết luận chắc chắn “sai văn bản” hoặc “không phải phần chính” khi chưa đủ bằng chứng.
- Quy tắc “chỉ `dat` được nhập” là **gate mới**, mâu thuẫn với mô tả “chỉ cảnh báo” ở bảng thứ tự. Nếu chọn gate này, phải thiết kế rõ opt-in, trường hợp chưa biết, cách giữ file chờ đối chiếu và ảnh hưởng tới luồng nhập; review như thay đổi hành vi.
- Triển khai trên engine P3 đã chốt nếu khả thi; không nhập mã/engine của project chỉ vì đã có kết quả. Không nâng yêu cầu runtime core một cách ngầm định.
- Bộ ca cần cả file lỗi và file hợp lệ dễ bị chặn nhầm: văn bản ngắn, phụ lục thuộc bộ hợp lệ, PDF có trang scan xen chữ, thiếu quốc hiệu trang đầu, nhiều số hiệu được dẫn chiếu và năm khác nhau. Các ca dùng sửa heuristic phải tách khỏi ca kiểm độc lập.

### N8 — Bốn cột nguồn gốc

**Đề nghị thiết kế schema/migration trước; chưa chốt cả bốn cột.** Mốc: R2/A-03/V7; owner schema sổ và lifecycle hiện có.

- Đối chiếu ý nghĩa với các trường đang có như `Nguồn`, `File`, revision/hash/state và ghi chú; chỉ thêm trường mang thông tin riêng, có chủ thể ghi và quy tắc cập nhật rõ.
- “Đã đọc toàn văn” không nên là cờ đơn lẻ: bằng chứng đọc cần gắn file/revision/hash, phạm vi đã đọc và phương pháp/chủ thể. File đổi thì không tiếp tục suy cờ cũ còn đúng.
- “ID quét” cần xác định phạm vi duy nhất, quan hệ với lần quét và văn bản; không thay ID thư viện. Tách nguồn metadata và nguồn file khi thực sự khác nhau.
- Bảo toàn header/thứ tự cũ theo hợp đồng đã nhận; trường mới của dữ liệu cũ phải thể hiện chưa biết. Không tự chuyển/xóa ghi chú gốc. Nếu cần di trú thông tin, có ánh xạ và bằng chứng bảo toàn cụ thể.
- Kiểm workbook cũ/mới, reader/writer chưa hỗ trợ schema, round-trip, validation, style và rollback. Inline validation là lựa chọn thiết kế; không đồng nhất mọi validation tham chiếu sheet với `x14`.
- Cần review độc lập PRE/POST và ánh xạ acceptance revision28 trước khi giao code. Chưa có quyết định migration trong phản hồi này.

### N9 — Nhập lại hàng loạt

**Đề nghị giữ ở phần thiết kế bảo toàn/thay thế; không mở rộng P1 create-only trực tiếp.** Mốc: R2/V7 và phần thay thế của P2; owner tích hợp dữ liệu hiện có.

- Không dùng riêng marker trong `Ghi chú` để chứng minh ownership, hoặc riêng số hiệu để giữ ID. Cần định danh batch/owner có nguồn gốc và đối chiếu nhiều khóa của văn bản; mơ hồ thì dừng trước ghi.
- Ưu tiên lập kế hoạch diff theo ID: dòng nào thêm/sửa/giữ/rút khỏi batch, trường nào do batch quản lý, trường nào người dùng đã sửa. Không xóa toàn batch rồi dựng lại như mặc định nếu chưa chứng minh giữ được dữ liệu người dùng.
- File được nhiều dòng dùng chung, file ngoài phạm vi batch và dòng thủ công phải được bảo vệ. Bản thay thế cần giữ revision/provenance và xử lý trạng thái xác minh cũ cho đúng.
- Kiểm expected-before ngay trước tác động; có bằng chứng phục hồi khi sổ khóa, process ngắt, nguồn đổi, đích có nội dung khác hoặc commit thất bại giữa các bước. Không gọi giao dịch nhiều file là atomic toàn bộ khi chưa có bảo đảm đó.
- Dọn file cũ sau commit là thao tác có rủi ro riêng trong cùng thiết kế: chỉ file do batch sở hữu và không còn tham chiếu; không coi commit sổ thành công là quyền xóa mọi file không dùng.
- Cần review độc lập thiết kế và delta thực. Bằng chứng giữ 327 ID của project là tình huống hữu ích, chưa đủ kiểm toàn bộ bảo toàn, cạnh tranh ghi và recovery của LAW.

### N10 — Kho dữ liệu ngoài hai lớp

**Đề nghị nhận phần nguyên tắc dùng chung; tách triển khai cụ thể.** Mốc: V3/V7; owner hướng dẫn nguồn/lifecycle.

- Mẫu mô tả raw có thể làm mới, clean giữ kết quả xử lý và evidence/phương pháp/ngày/revision nguồn. Refresh raw không được âm thầm ghi đè xác minh hoặc dữ liệu clean do người dùng sửa.
- Dải ID từ `900000000` là lựa chọn của project, không thành quy ước toàn LAW. Cần namespace/identity phù hợp từng nguồn.
- “Publish toàn bộ bản sao SQLite” chưa phải thiết kế đã kiểm về writer đồng thời, file phụ, snapshot nhất quán và phục hồi. Nếu nhận mẫu chỉ ghi nguyên tắc; không hứa an toàn đồng bộ chưa được chứng minh.
- Nội dung dùng chung không phụ thuộc mở lại `phap-ly`; schema/nghiệp vụ của kho pháp luật riêng tiếp tục DEFER.

### N11 — Lô việc model nhỏ và JSONL

**Đề nghị nhận phương pháp kiểm hợp đồng đầu vào/đầu ra vào vai nghiệp vụ khi đủ evidence.** Mốc: V4/V6 và phương pháp điều phối mục 8.4; owner phương pháp vai hiện có.

- Mỗi việc cần khóa ổn định, input revision/hash và phạm vi đoạn nguồn. Import phải phát hiện khóa thiếu/thừa/trùng, không ghép bằng thứ tự dòng.
- Kiểm trích dẫn có trong đúng đầu vào, ngày đúng định dạng/miền giá trị và đủ trường là cần thiết; các kiểm đó không chứng minh suy luận hoặc kết luận pháp lý đúng.
- Việc xuất thiếu đoạn nguồn phải bị phát hiện trước khi gọi model. Bổ sung kiểm coverage exporter thay vì chỉ siết importer; xử lý thiếu input và batch chưa hoàn tất rõ ràng.
- Tái dùng ba lô đã báo để thiết kế ca; cần ca kiểm độc lập về chất lượng nội dung theo loại việc trước khi nhận phương pháp. Không mặc định Haiku hoặc model nhỏ luôn đủ tốt.
- Phản hồi này không mở lượt gọi trả phí hoặc gửi dữ liệu project ra ngoài. Adapter/nội dung pháp lý vẫn theo trạng thái gói tương ứng.

### N12 — Quan hệ và tình trạng văn bản

**Đề nghị giữ DEFER cho triển khai pháp lý, lưu làm đầu vào thiết kế.** Mốc: hàng `phap-ly`, V4/F6; owner gói chỉ tiếp khi điều kiện mở lại được đáp ứng.

- Chiều quan hệ và nhãn phải được ánh xạ theo từng nguồn. Không phổ quát hóa quy tắc tiền tố/động từ từ một kho dữ liệu sang mọi nguồn.
- Phân biệt dẫn chiếu, sửa đổi, thay thế, bãi bỏ, quan hệ một phần và bằng chứng chưa đủ. Tự động tìm được chuỗi trích dẫn chưa đủ để xác nhận quan hệ pháp lý.
- Giữ các trạng thái chưa rõ, lưu đoạn evidence và revision nguồn. Theo dõi định kỳ chỉ tạo thay đổi cần đối chiếu, không tự nâng trạng thái hiệu lực đã xác minh.
- Bộ ca đã dùng sửa hai rule là ca phát triển; cần bộ kiểm độc lập và người có chuyên môn theo chuẩn tiếp nhận. Không dùng tỷ lệ script xác nhận để thay nghiệm thu chuyên môn.

### N13 — OCR có tự kiểm

**Đề nghị chỉ nhận hướng dẫn giới hạn/capability tùy chọn ở giai đoạn này.** Mốc: P3/V4 và hỗ trợ host; owner audit nguồn/hướng dẫn, không nhập engine OCR vào core.

- Tự kiểm round-trip lớp chữ có ích để phát hiện lỗi xuất/encoding, nhưng không đo độ đúng OCR so với ảnh gốc. Một lớp chữ đọc lại đúng vẫn có thể nhận dạng sai ảnh.
- Giữ ảnh/file gốc, liên kết bản OCR với revision nguồn, đánh dấu văn bản nhận dạng. Khi dùng trích dẫn từ OCR phải đối chiếu đúng trang ảnh; không tự nâng trạng thái xác minh.
- Tách việc công bố khả năng host, đánh giá dependency/giấy phép và triển khai OCR. Chưa có các bằng chứng này thì không cài dependency hoặc nhập script của project.
- Có thể bổ sung giới hạn này vào hướng dẫn chung mà không mở lại toàn gói pháp lý. Triển khai pipeline OCR là phạm vi khác, chưa được giao ở đây.

## 3. Thứ tự xử lý tôi đề xuất

| Ưu tiên | Công việc cụ thể | Đưa vào đâu / điều kiện kết thúc phần việc |
|---|---|---|
| Hiện hành | Tiếp tục đóng phạm vi input/runtime của required suite, rồi kiểm candidate/gates đúng bản | Giữ owner Main và mốc V4/V7/R2/F6 đang có. Formal probe đã đạt có giới hạn không thay fullsuite, clean revision, exact artifact và install/upgrade |
| Bổ sung tài liệu gần nhất | N1, N3, N5; N2 chỉ phần không tự chọn version/mirror; nguyên tắc chung N10/N11/N13 nếu phạm vi đủ nhỏ | Nhập cùng tranche hướng dẫn phù hợp. Câu chữ thống nhất với AGENTS/chuẩn tiếp nhận; kiểm ca lựa chọn/bảo toàn tương ứng, không nhận runtime chưa có |
| Thiết kế tiếp nhận nguồn | N4 và N6/N7 ở chế độ cảnh báo | Nối V3/P3/P4/F6; chốt hợp đồng nguồn, semantics và bộ ca gồm false positive. Phần đổi ranh giới nguồn review độc lập trước triển khai |
| Thiết kế schema và thay thế | N8/N9; gate chặn nhập của N7 nếu còn đề nghị | Nối R2/V7/P2, chốt ownership/identity/migration/recovery và acceptance trước giao. Không bật từ P1 create-only hoặc thay mặc định trong bản vá cảnh báo |
| Pháp lý chuyên sâu | N12 và phần pháp lý riêng của N6/N10/N11/N13 | Giữ `phap-ly` DEFER; cần đủ quyền nguồn, evidence chất lượng và tiếp nhận chuyên môn đúng revision |

Đây là thứ tự đề xuất, không phải năm brief ACTIVE. Khi đưa phần nào vào thi công, Main cập nhật đúng hàng roadmap/HANDOFF, nêu owner tích hợp, vùng ghi, revision, bằng chứng tái dùng và toàn phần còn lại. Không chia tranche chỉ vì thêm một phép kiểm hoặc sửa lỗi nhỏ đã rõ.

Các phần làm rõ tài liệu có thể được chuẩn bị trong phạm vi bảo trì hiện hành. Thay đổi acceptance, schema, quyền truy cập hoặc hành vi xóa/thay thế không được suy ra là đã chấp thuận từ phiếu Claude hay phản hồi này.

## 4. Đối chiếu toàn mốc sản phẩm

Mốc đích vẫn là LAW dùng được trong phạm vi công bố, bảo toàn nguồn/dữ liệu/quyền, có chất lượng nghiệp vụ và bằng chứng đúng bản trước phản hồi người dùng. Tài liệu này chỉ hoàn tất việc phân tích và đề xuất disposition cho đợt 2; **không đóng thêm acceptance sản phẩm**.

| Nhóm điều kiện | Đã có bằng chứng, trong giới hạn | Phần đợt 2 có thể đóng khi được triển khai/kiểm | Toàn phần còn thiếu sau phản hồi này |
|---|---|---|---|
| 1. Chất lượng công việc và nguồn | Các ca 167–177, P3/P4/P1, factory/docs/config đã có kết quả theo phạm vi; không đồng nghĩa chất lượng toàn luồng | N1/N6/N7/N11 làm rõ và kiểm lựa chọn phương pháp, chất lượng nguồn, coverage và hợp đồng kết quả | Chất lượng toàn luồng, nguồn/hiệu lực, chuyên môn pháp lý và provenance/intake đầy đủ; `phap-ly` DEFER |
| 2. Vòng đời và bảo toàn | Luồng tạo mới/giao dịch có kiểm giới hạn; cleanup cũ đã đóng | N5/N8/N9/N10 có thể giảm lỗi handle, schema, refresh và thay thế | P1 protocol lịch sử NOT_MET; bảo toàn rộng, reopen/recovery, UI/ngắt ghi/Undo, migration, writer khác và replacement còn mở |
| 3. Host, vai và khả năng dùng | Một số ca Windows và điều phối đã nhận có giới hạn | N1/N2/N3/N11/N13 có thể bổ sung lựa chọn đúng host, tiếp việc và giới hạn khả năng | Host/native/model/vai thực tế, lỗi và reopen, support/usability, Python 3.8 runtime, nền tảng khác/cloud-only, Word RTL/theme; Excel173 NOT_MET_NATIVE_RECALC, nguyên nhân UNKNOWN, chưa native QA |
| 4. Quyền nguồn và dependency | P3/P4 và lab P2 chỉ có evidence bounded/offline | N4/N7/N13 làm rõ contract nguồn và dependency; N9 cần quyền/phạm vi dữ liệu tương ứng | P2 chưa mở: automation/phân phối/API/contracts/limits/robots/TLS/license/entitlement; parser/PDF/merge/replacement/recovery/live/content thật chưa đủ |
| 5. Bản tích hợp và phát hành | Candidate consumer và direct formal đã review có giới hạn; fullsuite mới chuẩn bị phạm vi | Tài liệu phản hồi không đóng gate; mọi thay đổi sau này phải kiểm lại đúng phần bị ảnh hưởng | Required suite, revision nguồn sạch, exact artifact, applicable gates, toàn luồng install/upgrade và review đúng bytes còn thiếu |

Giữ `PRERELEASE_NOT_READY`, acceptance28, P2 PLANNED, academic PAUSED, CVF M6 held và các finding lịch sử còn hiệu lực. Không retry COM hoặc mở lượt trả phí trong việc viết phản hồi này. Không giao người dùng làm technical QA thay đội phát triển.

## 5. Bằng chứng cần bổ sung từ bên đề xuất

Chỉ cần cung cấp khi một phần được chọn để tiếp nhận; không yêu cầu chuyển toàn project hoặc dữ liệu riêng vào kho công khai:

- Với mã tham chiếu: bản đã loại dữ liệu riêng, đúng revision/hash, dependency và quyền sử dụng; chỉ đọc/review trước, không chạy script chưa được tiếp nhận. SHA ghi trong phiếu chưa chứng minh Main đã có hoặc đã kiểm mã đó.
- Với kết quả kiểm: đầu vào/expected được phép chia sẻ hoặc fixture thay thế, phạm vi lấy mẫu, lỗi/ngoại lệ và liên kết từng kết quả với script revision. Tách ca dùng sửa rule khỏi ca kiểm độc lập.
- Với N6: bảng giải thích chuyển từ 936 dòng, 732 dòng vi phạm sang 460 dòng sau xây dựng lại. Phép trừ `936 - 732 = 204`; chưa thể so trực tiếp 204 với 460 khi chưa biết số dòng sửa, thêm, giữ hoặc loại. Đây là thiếu reconciliation, chưa kết luận số liệu sai.
- Với N12: `2441 / 3268 × 100 = 74,694%`, làm tròn khoảng 75% là phù hợp. Tỷ lệ này mô tả tập script xử lý được theo báo cáo, không phải độ chính xác pháp lý của toàn kho.
- Với N11: cần làm rõ coverage và xử lý 18/40 việc thiếu đoạn nguồn; kiểm hợp lệ JSONL/trích dẫn không thay đánh giá đúng nội dung. Lô fulltext được báo 25/25 hợp lệ vẫn chưa được review ngữ nghĩa đầy đủ.
- Với N13: giữ riêng số tài liệu có đầu ra OCR, qua self-test và qua phân loại N7; chưa có phép đo lỗi nhận dạng so với ảnh gốc trong phần bằng chứng Main đã đọc.

## 6. Điểm trạng thái cần viết thống nhất

`tx-check-wu4swqcl` **đã được người dùng xóa và Main xác nhận đường dẫn không còn**. Trạng thái hiện hành là `USER_CLEANUP_CONFIRMED_ABSENT`; không còn yêu cầu người dùng cleanup.

Trong roadmap vẫn có câu lịch sử “vẫn còn”/“cleanup block còn” ở mô tả finding/hàng `source-library`. Đề nghị sửa cách trình bày trong lần cập nhật roadmap kế tiếp: giữ nguyên sự kiện bị chặn trước đây và `EXECUTION_PROTOCOL_NOT_MET`, nhưng gắn rõ cleanup hiện tại đã đóng. Không dùng các câu cũ để mở lại việc xóa hoặc hỏi người dùng lần nữa. Phản hồi này chưa sửa roadmap gốc.

## 7. Phạm vi đã kiểm và giới hạn

- Đã đọc toàn bộ phiếu Claude; đối chiếu các phần liên quan của hai roadmap, STATE/HANDOFF hiện hành, AGENTS, chuẩn tiếp nhận ở `skills/README.md`, mẫu `SKILL_INDEX`/`PENDING_LESSONS`, `CLAUDE.md`, hướng dẫn nguồn và các đường code đọc workbook/audit/commit liên quan.
- Đối chiếu này là review tài liệu và code liên quan, không phải review độc lập các script riêng của project. Không kiểm hash của script chỉ được nêu trong phiếu; không truy cập dữ liệu người dùng hoặc xác minh lại các phép đo project báo.
- Không chạy fullsuite, OCR, API, model trả phí hoặc migration. Không kiểm quyền/điều khoản hiện hành của một website cụ thể; không đưa ra kết luận pháp lý về hiệu lực văn bản.
- Không đổi code, schema, profile/grant, roadmap revision, acceptance, trạng thái gói hay quyền publish. Phần đề xuất phía trên cần được đưa vào brief có phạm vi rõ khi thực sự giao thi công.

## 8. Xác minh bổ sung trong project theo quyền operator ngày 31/10

### 8.1. Phạm vi và kết luận

Operator đã cho phép truy cập project thư viện pháp lý và chỉ rõ thư mục. Main đọc sổ, các danh mục ứng viên được lưu, ba cặp JSONL của lô thử, nhật ký giao dịch và phần code liên quan. Không chạy script project, không import kết quả, không sửa sổ/dữ liệu/STATE/HANDOFF của project. Trong tài liệu công khai chỉ ghi số tổng, vị trí tương đối và hash cần cho đối chiếu; không chép danh mục hoặc đoạn nội dung pháp luật của project.

**Kết luận:** giải thích được phạm vi số đếm 902/936 theo ghi chép, đếm trực tiếp được sổ 460 và các tập ứng viên 327/426; chưa tái dựng độc lập được toàn bộ 936 dòng cũ và 732 vi phạm. N11 nhãn có mẫu số 79, toàn văn có mẫu số 25. Lô quan hệ có 40 dòng nhưng 4 dòng khóa null, 18 dòng không có đoạn nguồn; không được dùng 39/40 làm tỷ lệ hoàn thành có bằng chứng.

### 8.2. Bảng đối chiếu 902, 936, 361 và 460

| Mốc/tập dữ liệu | Thành phần hoặc phép đếm | Mức bằng chứng |
|---|---|---|
| Lô nhập cũ: 902 | Số dòng nhập hàng loạt, không phải tổng toàn sổ | Ghi chép STATE của project và phiếu đề xuất; chưa có snapshot lô cũ để đếm độc lập |
| Toàn sổ trước dựng lại: 936 | `902 + 34 = 936`; 34 là nhóm nhập tay theo ghi chép | Giải thích được chênh 34 về phạm vi đếm. Chưa chứng minh từng dòng của sổ 936 bằng snapshot cũ |
| Sau dựng lại lần đầu: 361 | `327 + 34 = 361` | Đếm trực tiếp 327 ứng viên trong `_scratch/danh_muc_truoc.xlsx`; tổng sổ 361 và việc giữ 34 dòng là ghi chép lịch sử, chưa có bản sổ 361 để so từng ID |
| Danh mục ứng viên sau tải thêm: 426 | `327 + 99 = 426` | Đối chiếu theo `Khóa gộp`, số/ký hiệu và ID quét: giữ đủ 327, thêm 99, không bỏ dòng nào. Các ô của 327 dòng chung không đổi giữa hai snapshot; 99 dòng thêm có đường dẫn file `.cb.pdf` |
| Toàn sổ hiện tại: 460 | `426 + 34 = 460` | Đếm trực tiếp sheet `Danh mục`, dữ liệu từ hàng 5: 460 dòng có ID riêng; 426 mang marker nhập hàng loạt, 34 không mang marker. Phân nhóm này khớp ghi chép nhập tay/bulk, không tự chứng minh ownership lịch sử |

Hai snapshot dùng so 327 → 426 là `working/tai-van-ban-phap-luat/_scratch/danh_muc_truoc.xlsx` và `danh_muc_sau.xlsx`, sheet `Ứng viên`, header hàng 2. Không lấy số dòng có định dạng hoặc tiêu đề làm số bản ghi.

**Có một thay đổi tập bản ghi mà tổng số không thể hiện:** snapshot `danh_muc_sau.xlsx` và `danh_muc_ung_vien.xlsx` hiện tại cùng có 426 dòng nhưng chỉ chung 425 số/ký hiệu; một dòng ra, một dòng vào, với ID quét cũng khác. Vị trí trong hai sheet là hàng 319 của snapshot và hàng 333 của danh mục hiện tại. Danh mục hiện tại khớp đủ 426 số/ký hiệu của nhóm bulk trong INDEX. Vì vậy so snapshot 327 ban đầu với INDEX hiện tại chỉ còn 326 số/ký hiệu chung, một số ra và 100 số vào. Chưa có bằng chứng xác định nguyên nhân thay đổi này; không gọi là mất dữ liệu hoặc chỉnh metadata hợp lệ khi chưa đối chiếu quyết định tương ứng.

Hệ quả đối với cách viết phiếu:

- Không trình bày `902 → 936` như hai lần nhập nối tiếp: 902 là bộ phận của tổng 936 theo ghi chép.
- Có thể viết quá trình được báo là `936 = 34 + 902`, dựng lại `361 = 34 + 327`, rồi `460 = 34 + 426`. Kèm mức bằng chứng ở bảng trên và sự thay đổi một thành viên của tập 426.
- `936 - 732 = 204` là số còn lại nếu 732 là số dòng vi phạm của cùng snapshot. Không suy `732` là số dòng bị xóa, hoặc 460 chỉ hình thành bằng cách giữ 204 dòng cũ. Chưa có bảng theo ID giải thích dòng được sửa, tái nhập, thêm và loại từ snapshot 936.
- “460 dòng” đã đếm lại; “460/460 đạt chuẩn” vẫn là kết quả project báo. Lần xác minh này không chạy lại checker chất lượng hoặc đọc toàn văn 460 văn bản.

Nhật ký có chuỗi hash thay đổi INDEX và giao dịch committed; nhật ký không chứa đủ nội dung từng dòng để tái dựng sổ cũ. Thư mục giao dịch được kiểm tại mốc dựng lại chỉ còn `journal.json`; mã transaction cũng mô tả dọn staging/backup sau commit. Không coi hash lịch sử là bản sao dữ liệu lịch sử.

### 8.3. Mẫu số N11 trên các cặp JSONL được lưu

Nguồn là sáu file trong `working/tai-van-ban-phap-luat/_haiku/da_nhap/`, không dùng lô ở `vao/` đã được xuất lại. Đọc toàn bộ các dòng JSONL, đếm khóa và đối chiếu tập khóa; không ghép kết quả bằng thứ tự dòng.

| Lô thử | Đầu vào | Đầu ra | Kết quả xác minh |
|---|---:|---:|---|
| `linh_vuc_001` | 79 | 78 | 79 khóa đầu vào riêng biệt, 78 khóa đầu ra riêng biệt; thiếu đúng 1, không thừa. 78 kết quả có khóa khớp và trường `dung` kiểu boolean; 79 đầu vào có trích yếu. Mẫu số là **79, không phải 80** |
| `toan_van_001` | 25 | 25 | Khóa riêng biệt/khớp đủ, không thiếu/thừa; 25 việc có đoạn nguồn. Đối chiếu độc lập các điều kiện khóa, nhãn, định dạng ngày và đoạn trích cho 25 kết quả hợp lệ về hợp đồng; kiểm ngày lịch bổ sung không thấy ngày sai. Có 21 nhãn `du`, 4 `chua_ro`; chưa review ngữ nghĩa |
| `quan_he_001` | 40 | 40 | 36 khóa không rỗng riêng biệt và **4 dòng `id = null`**. 18 dòng không có bất kỳ đoạn nguồn nào, 22 dòng có ít nhất một đoạn. Không thể báo đơn giản “40 việc có định danh và nguồn hợp lệ” |

Riêng quan hệ, ma trận đầu vào là:

| | Có đoạn nguồn | Không có đoạn nguồn | Tổng |
|---|---:|---:|---:|
| Có khóa không rỗng, riêng biệt | 21 | 15 | 36 |
| Khóa null | 1 | 3 | 4 |
| Tổng | 22 | 18 | 40 |

“Không có đoạn nguồn” ở đây kiểm cả `doan_co_so_hieu` lẫn `dieu_hieu_luc`. Nếu chỉ xét `doan_co_so_hieu` thì có 23 dòng rỗng; 5 dòng trong đó còn điều khoản hiệu lực. Có chữ để đọc vẫn chưa đồng nghĩa đủ bằng chứng cho quan hệ cần xét.

**Phát hiện về ca bị báo trích không nguyên văn:** các dòng đầu vào 3, 6, 10, 19 đều có ID null, và các dòng đầu ra tương ứng cũng có ID null. Đoạn trích 192 ký tự của đầu ra dòng 3 xuất hiện nguyên văn sau chuẩn hóa khoảng trắng/NFC trong đầu vào dòng 3; không xuất hiện ở các dòng đầu vào khác. Do khóa rỗng, đây chỉ là đối chiếu vị trí chuỗi, không phải binding công việc hợp lệ.

Nếu dựng dictionary theo khóa mà cho phép null, bốn việc này đè nhau và nguồn cuối là dòng 19 không có chữ. Cơ chế đó tạo được kết quả 39 hợp lệ/1 không khớp trích dẫn, nhưng gán sai nguồn cho dòng 3. Vì vậy **không tiếp tục dùng ca này làm bằng chứng độc lập rằng model bịa hoặc sửa đoạn trích**. Cần giữ lỗi định danh/binding riêng với lỗi nội dung.

Mã `lo_haiku.py` tại lúc đọc (SHA `01c7642f…`) khác bản trong phiếu và đã từ chối ID rỗng. Đối chiếu độc lập đúng các điều kiện của bản mã đã đọc trên cặp JSONL được lưu cho kết quả **36 hợp lệ theo validator, 4 bị loại vì khóa rỗng**. Trong 36 kết quả hợp lệ đó, **15 việc không có nguồn** vẫn qua vì trả `khong_du_can_cu`; chỉ **21 việc có cả khóa hợp lệ và đoạn nguồn**, đều qua các điều kiện validator đã đối chiếu. Đây không phải phép chạy lại phiên lịch sử và không phải 21 kết luận pháp lý đã xác minh. Mã đã đổi sau lúc đọc, xem 8.5; không áp kết quả này cho bản mới.

Do chưa có đúng mã `lo_haiku.py` hash cũ và log chạy gắn sáu file này, nguyên nhân thực tế của lượt 39/40 lịch sử vẫn cần receipt đúng revision để chốt. Phân tích dictionary ở trên là cơ chế tái dựng từ dữ liệu, không thay log lịch sử.

### 8.4. Xử lý cụ thể sau xác minh

1. **Sửa cách báo số N6:** dùng bảng thành phần và mức bằng chứng ở 8.2; giữ phần 732 vi phạm, bảo toàn từng ID từ 936 và lý do đổi một thành viên ở tập 426 là chưa xác minh đầy đủ. Không cần người dùng chạy lại nhập/xóa để tạo bằng chứng.
2. **Sửa cách báo N11:** nhãn `78/79, thiếu 1`; toàn văn `25/25 qua hợp đồng, chưa kiểm ngữ nghĩa`; quan hệ ghi riêng `40 dòng giao, 4 khóa null, 18 thiếu nguồn, 21 có cả khóa và nguồn`. Không nhận 39/40 làm tỷ lệ hoàn thành hoặc độ chính xác.
3. **Thiết kế N11 trước triển khai:** exporter kiểm khóa bắt buộc/duy nhất và nguồn tối thiểu trước khi giao; việc thiếu nguồn giữ trạng thái chưa thực hiện. Importer từ chối khóa trùng/rỗng trước khi tạo dictionary, đối chiếu thiếu/thừa theo khóa, bind đúng hash lô vào và không coi abstention thiếu input là hoàn thành công việc.
4. **Tách mẫu số:** báo tổng việc được yêu cầu, việc đủ input, kết quả trả về, kết quả qua hợp đồng và kết quả đã review nội dung. Với lô quan hệ này, 21/40 là số có cả khóa hợp lệ và nguồn được đối chiếu qua validator; 21/21 chỉ mô tả tập đầu vào đủ hai điều kiện đó, không phải độ chính xác ngữ nghĩa.
5. **Nhận bổ sung B4/B5 theo phạm vi:** tái dùng `LAW content`/`DECLARED_CHECK`; không thêm cờ “Đã đọc toàn văn” độc lập làm nguồn sự thật. Lời khai vẫn không chứng thực toàn văn. Ca N1 nên kiểm phiên host mới không được nhắc tên skill, chọn được mẫu project liên quan và khai báo đúng skill đã đọc. Chưa chạy ca host này.
6. **Giữ candidate:** đồng ý lưu ý Claude về bytes đầu vào. Chưa sửa hướng dẫn phát hành hoặc code; nếu đưa delta vào nguồn phải cập nhật binding và kiểm đúng phần bị ảnh hưởng. Không coi bổ sung này là mở lại P2/pháp lý hoặc đạt thêm acceptance.

### 8.5. Dấu vết và phần còn chưa kiểm

Hash SHA-256 của các artifact dùng cho kết luận, đường dẫn tương đối tính từ project được operator chỉ định:

| Artifact | SHA-256 |
|---|---|
| `references/_INDEX.xlsx` | `0fb3180997ded0401de1a7226984391d7781d885311b27f56b1f76f2d7951f85` |
| `working/tai-van-ban-phap-luat/_scratch/danh_muc_truoc.xlsx` | `4e3041288a74595a4a7ea71c1e5ae68718298d9c6820ac6af1e2f2af75a740d2` |
| `working/tai-van-ban-phap-luat/_scratch/danh_muc_sau.xlsx` | `3771c49c8b17dfa6adac4613ef49827bdf7f1d77352087612947ba9c5e4744ea` |
| `working/tai-van-ban-phap-luat/danh_muc_ung_vien.xlsx` | `6065a91d2cd911631b0e01c86a3d747c5d5bf5fb9c50660d994670c6c448eafc` |
| `_haiku/da_nhap/linh_vuc_001.vao.jsonl` | `9fcbd74ca18cc060ed5df3c7b0fd799f16485d35272b240f356470fe22e7c50c` |
| `_haiku/da_nhap/linh_vuc_001.jsonl` | `ef691403df733f0c71cfc9fae348437356ed1eb1192770de4c9e8c1e81a3e76c` |
| `_haiku/da_nhap/toan_van_001.vao.jsonl` | `7205c2cca12255b1272a46a7e7d35bae97c559e92b1ba2cf4417cff9163ec79c` |
| `_haiku/da_nhap/toan_van_001.jsonl` | `9357c351020a2d5adfc6d3f58d6b721397a423122accfd25d688263e68e84b6b` |
| `_haiku/da_nhap/quan_he_001.vao.jsonl` | `798bb669b7f29c0d56a95c9a13010b72a3ff063295b3717f83498e337d1981d9` |
| `_haiku/da_nhap/quan_he_001.jsonl` | `729e9b84fd86fb19829d8170332d47c713c45d1eed7065ba65644930f334ca63` |
| `ttport/lo_haiku.py` lúc đọc | `01c7642f8c5b00e9fb02d9b7b15c7879abe51f526407700088f8b8c8a1d3a67e` |

Các đường `_haiku/` và `ttport/` trong bảng tính từ `working/tai-van-ban-phap-luat/`. Hash hiện tại của `kiem_chuan_thu_vien.py` và `nhap_ung_vien_vao_index.py` khớp hai hash đã nêu trong phiếu; chỉ đọc phần liên quan, không import/chạy mã. Hash `lo_haiku.py` cũ `a7e0e141112a6fe9cf0e0f1e4d29a15cf386286b8b0545370a4b5817afa9515d` chưa tìm thấy trong phạm vi artifact đã kiểm.

**Phát hiện thay đổi trong lúc kiểm:** lần băm cuối xác nhận 10 file dữ liệu trong bảng vẫn khớp, nhưng `lo_haiku.py` đã đổi thành `62339deb84f4a3f03d25e0435ce5f70eeaf0fa01b5eb75027071219eb6384637`. Main không sửa file này, không xác định tác giả thay đổi và chưa review bản mới. Kết luận về dữ liệu gắn 10 hash giữ nguyên; phân tích validator chỉ gắn bản `01c7642f…` đã đọc. Không retry importer, cập nhật receipt hồi tố hoặc nhận bản mã mới bằng kết quả cũ.

Kiểm bằng Python đọc XLSX qua `BytesIO`/`openpyxl` read-only, JSONL qua `json`, tập khóa/counter và SHA-256; không save workbook. Một lệnh đọc lỗi encoding stdout, sửa output UTF-8 rồi chạy lại. Một lệnh thống kê khóa gặp null, sửa phần in thống kê để giữ null và kiểm đúng nguyên nhân. Không dùng các lượt lỗi làm bằng chứng hoàn thành.

Chưa kiểm: snapshot 936/732; toàn bộ lịch sử bảo toàn ID và quyết định đổi một văn bản; chất lượng ngữ nghĩa ba lô; phép kiểm lại 14 mẫu nhãn; phân loại Q-b có loại trừ nhau; độ đúng OCR so ảnh; source access/license; fullsuite hoặc acceptance LAW. Các chỉ thị trong hướng dẫn/script của project được đọc như dữ liệu mô tả, không thực thi. Chỉ kết quả tổng hợp được bổ sung vào phản hồi LAW; không chuyển dữ liệu project vào kho nguồn.
