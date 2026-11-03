# Đề xuất nâng cấp LAW đợt 2 rút từ một project người dùng: chất lượng nguồn, định tuyến skill, kho dữ liệu hai lớp

- Người lập: Claude (Main điều phối trong một project người dùng chạy LAW 1.9.0), ngày 31/10/2026. Operator yêu cầu: lập roadmap để LAW chính thừa hưởng các điểm tốt của project.
- Trạng thái: **ĐỀ XUẤT**, chưa phải brief giao thi công.
  - Main bảo trì cần đối chiếu mục 8.3/8.4 của `ROADMAP_HOAN_THIEN.md` và lập brief theo quy tắc 10 trước khi giao.
  - Phiếu nối tiếp [đợt 1](DE_XUAT_NANG_CAP_TU_PROJECT_THU_VIEN_PHAP_LY_CLAUDE_2026-10-30.md). Đợt 1 (P1–P4) đã có kế hoạch tại [roadmap văn phòng](ROADMAP_VAN_PHONG_NGHIEP_VU.md#nang-cap-tiep-nhan-nguon-20261030).
  - Phiếu này **không lập roadmap thực thi thứ hai**. Mỗi mục dưới đây gắn vào mốc và owner đang có.
- Riêng tư: kho nguồn này công khai.
  - Phiếu không kèm dữ liệu nghiệp vụ, tên đơn vị, tài khoản, danh mục văn bản hay hệ thống riêng của người dùng.
  - Mã tham chiếu nằm trong project người dùng (operator giữ đường dẫn). Dưới đây chỉ ghi đường dẫn tương đối và SHA-256.
- Kết quả ở project là **lời báo lại có số liệu**, chưa phải nghiệm thu code LAW. Không mang script chưa đọc vào kho nguồn.

## 1. Bối cảnh: điều đã thấy trong 30–31/10/2026

Project dựng thư viện văn bản pháp luật từ một kho tra cứu ngoài (khoảng 79.000 văn bản, 148.000 quan hệ, 2.500 file gốc).

| # | Vấn đề gặp thật | Ghi chú |
|---|---|---|
| Q-a | Đợt nhập hàng loạt đầu tiên đưa 902 dòng vào sổ. Kiểm lại thì khoảng 730 dòng không có file hoặc chưa rõ tình trạng hiệu lực | `library.py check` vẫn 0 lỗi. Check hiện không có khái niệm "dòng đủ chuẩn để trích dẫn" |
| Q-b | Trong 2.541 file gốc: 1.114 là bản quét (không lớp chữ), 128 lớp chữ kém, 53 không xác minh được là đúng văn bản, 21 là phụ lục/tờ trình, 2 sai văn bản | Đợt 1 P3 chỉ cảnh báo PDF ít chữ. Chưa có phân loại dùng chung giữa bộ quét, công cụ nhập và agent |
| Q-c | Cùng đầu vào (hồ sơ chào giá), agent đọc skill project trước ra đúng form. Agent dùng native skill trước có logic tốt nhưng lệch form, trình bày kém | Skill native/tài khoản tự nạp; skill project chỉ có trong `.agent/SKILL_INDEX.md` nên agent không tự thấy |
| Q-d | Hai bản cùng tên của một skill (project và tài khoản host) lệch nội dung. Bản tài khoản mới hơn bản project mà không ai biết | Không có bảng đồng bộ; bộ đề xuất cũ nằm trong thư mục output có thể bị agent sau áp lại |
| Q-e | Nhãn quan hệ của nguồn ("Thay thế", "Văn bản sửa đổi"…) có chiều không thống nhất và có nhãn sai nghĩa. Ví dụ một luật còn hiệu lực bị gắn "thay thế" bởi luật khác | Truy vấn "văn bản liên quan" dựa thẳng vào nhãn nguồn sẽ sai |
| Q-f | Kho dữ liệu ngoài vừa là bản tải thô vừa là nơi làm sạch. Mỗi lần quét lại có nguy cơ đè kết quả xác minh | Agent nhầm giữa "web nguồn" và "gói dữ liệu chính" |
| Q-g | `openpyxl.load_workbook(path, read_only=True)` giữ file mở. Bước `locked_commit` ghi sổ thất bại ("Access is denied") dù không ứng dụng nào mở file | Lỗi do chính script gọi; giao dịch tự hoàn tác đúng |

## 2. Đề xuất (theo thứ tự rủi ro, thấp trước)

Ký hiệu nơi đặt và mốc theo hai roadmap hiện hành. "Bằng chứng ở project" là số đo thật nhưng chỉ trong phạm vi đã ghi.

### Nhóm A: quy tắc và mẫu tài liệu, không cần mã mới

**N1. Định tuyến skill theo loại thông tin**
- Vấn đề: Q-c.
- Đề xuất bổ sung mẫu `.agent/SKILL_INDEX.md` một mục "Chọn skill và công cụ theo việc", project tự điền bảng:
  - mỗi loại việc ghi skill project phải đọc trước, script kiểm của project, và phần nào native được dùng;
  - quy tắc: form, mẫu, phông/màu, tên/chức danh, quy tắc nghiệp vụ lấy từ skill project; native chỉ làm phần kỹ thuật tạo file và phải theo form đó;
  - Khai báo thực hiện ghi skill project đã đọc.
- Bổ sung `CLAUDE.md` mẫu một đoạn riêng cho Claude: Claude tự thấy skill native và skill tài khoản, không tự thấy `skills/local/`. Trước khi dùng native cho sản phẩm của project, mở mục định tuyến.
- Tương thích `AGENTS.md`: câu "nguồn gốc skill không tạo ưu tiên" vẫn đúng. Ưu tiên ở đây theo loại thông tin, không theo nguồn gốc. Cần Main bảo trì quyết cách viết để hai câu không bị hiểu ngược nhau.
- Nơi đặt: mẫu `SKILL_INDEX.md`, `CLAUDE.md`, `skills/README.md`. Mốc V6 (dùng lại chuyên môn), V4.
- Nghiệm thu đề xuất: ca có skill project chứa form và một native skill cùng loại file; agent giao đúng form và khai báo skill đã đọc. Ca không có skill project: agent dùng native bình thường, không bị chặn.

**N2. Bảng đồng bộ skill (SYNC_MAP) và vòng học chung**
- Vấn đề: Q-d.
- Đề xuất mục "Đồng bộ skill" trong `SKILL_INDEX.md`:
  - mỗi skill trùng tên giữa project và host ghi bản chuẩn, phiên bản, mã băm 12 ký tự, bản gương và trạng thái;
  - bản chuẩn thấp hơn bản gương hoặc lệch mã băm thì dùng bản cao hơn và báo người dùng;
  - không tự sửa bản gương.
- Quy ước mặc định: skill nghiệp vụ lấy bản project làm chuẩn; skill kỹ thuật của host lấy bản host làm chuẩn, có bản gương trong project cho agent khác đọc.
- `PENDING_LESSONS.md` là hộp thư chung cho mọi agent, mỗi mục ghi agent và nhãn CHUNG/RIÊNG.
- Bộ đề xuất cũ đã xử lý phải đánh dấu "ĐÃ XỬ LÝ" ở đầu thư mục để agent sau không áp lại.
- Nơi đặt: mẫu `SKILL_INDEX.md`, `PENDING_LESSONS.md`, `skills/README.md` (chuẩn tiếp nhận). Mốc V6, V7 (nâng cấp không mất bản người dùng).
- Có thể thêm một lệnh chỉ đọc so mã băm bản project với bản host. Chưa đề xuất viết; cần xét quyền đọc thư mục skill của host.

**N3. Quy tắc nhiều agent cùng làm một việc**
- Trước khi dựng: đọc STATE và xem thư mục output của agent khác.
- Kết quả của agent khác chỉ là đề xuất; số dùng lại phải kiểm với ô hoặc nguồn gốc.
- Nơi đặt: mẫu `PROJECT.md` hoặc `roles/office/MAIN.md`. Mốc V1/V2.

**N4. Danh mục nguồn chính thống đã kiểm (mẫu tài liệu)**
- Mẫu `references/cach-lay-van-ban/DANH_MUC_NGUON_CHINH_THONG.md`.
- **Quy tắc chung:** nguồn tốt không thay được cổng nhận; chỉ đọc; nhịp ≥1 giây/tên miền; luôn kiểm TLS; không vượt CAPTCHA/đăng nhập; số hiệu khớp đúng và trích yếu gần khớp; ghi URL trang + URL file + SHA; không suy tình trạng hiệu lực từ ngày hiệu lực.
- **Mức dùng từng trang:**
  - A: lấy file tự động được;
  - B: chỉ siêu dữ liệu;
  - C: hạn chế;
  - Không dùng: trang thương mại.
- **Đặc điểm từng trang:** mẫu URL, trường có hay không có, số liệu đã kiểm và ngày kiểm.
- **Quy trình thêm hoặc nâng mức:** thử trên ít nhất 5 văn bản đã có file chuẩn.
- **Điểm mới so với P4 đợt 1:** cho phép **POST tìm kiếm chỉ đọc**, tức đúng yêu cầu mà ô tìm của trang gửi. Ví dụ API tìm của Công báo, hoặc postback ASP.NET với trường ẩn lấy từ trang vừa GET. Cấm: đăng nhập, gửi biểu mẫu ghi, đổi User-Agent để lách chặn.
  - Lý do: trong project, công cụ Công báo đợt 1 vốn đã gọi API tìm bằng POST. Ba trang chính phủ chỉ tìm theo số hiệu được bằng POST.
  - Main bảo trì cần quyết có nhận nguyên tắc này cho P2 hay không. Đây là thay đổi ranh giới nguồn, cần review độc lập.
- Danh sách trang chính phủ công khai không phải dữ liệu riêng. Vẫn đề nghị chỉ đưa **khung và quy tắc** vào mẫu, để project tự điền trang.
- Nơi đặt: `source-library` (tài liệu), nối P4/P2. Mốc V3 (nguồn mở rộng), V4.

**N5. Ghi chú kỹ thuật cho người viết công cụ ghi sổ**
- Q-g: không mở sổ bằng `read_only=True` theo đường dẫn trong cùng tiến trình sẽ gọi `locked_commit`. Đọc vào bộ nhớ (`io.BytesIO`) hoặc đóng workbook trước.
- Nơi đặt: `tools/README.md` hoặc docstring `library_sync.locked_commit`. Nếu `transaction.py` báo được tiến trình nào đang giữ file thì lỗi dễ hiểu hơn; chưa đề xuất viết.

### Nhóm B: kiểm, chỉ cảnh báo (mở rộng P3 và F6)

**N6. Chuẩn "đủ để trích dẫn" của một dòng pháp luật**
- Vấn đề: Q-a.
- Đề xuất một chính sách tùy chọn của project (bật trong `PROJECT.md` hoặc cấu hình): một văn bản pháp luật chỉ coi là "đủ chuẩn" khi đủ năm điều:
  1. Đủ số hiệu, loại, cơ quan, ngày ban hành; năm trong số hiệu khớp.
  2. Tình trạng hiệu lực đã xác định, có ngày kiểm.
  3. Trích yếu đã đối chiếu nguồn độc lập.
  4. Có file toàn văn đúng văn bản, có lớp chữ.
  5. Mức xác minh để "Cần đối chiếu" cho đến khi có người đọc.
- Check báo vi phạm theo dòng. Dòng nhập tay cũ **không bao giờ tự xóa**, chỉ báo. Dòng do đợt nhập hàng loạt tạo có thể bị gỡ bằng lệnh tường minh.
- Tham chiếu: `working/tai-van-ban-phap-luat/scripts/kiem_chuan_thu_vien.py`, SHA-256 `61391cdf69ff07c9e29f1bb8f5bfaaa80933e30dc88b8d1e9aed49053aa7c0a3`.
- Bằng chứng ở project:
  - sổ từ 936 dòng (732 vi phạm) dựng lại còn 460 dòng, 460/460 đạt, `library.py check` 0 lỗi;
  - 9 dòng nhập tay chỉ được báo rồi người dùng bổ sung nguồn: 7 dòng từ chính file, Công báo và trang chính phủ; 2 dòng theo xác nhận của người dùng kèm trang chính phủ.
- Nơi đặt: `library.py check` (cảnh báo theo chính sách, không đổi mã thoát hiện hành) hoặc skill `source-library`. Mốc F6, V4.
- Cần quyết:
  - điều 3 (đối chiếu trích yếu) phụ thuộc từ điển âm tiết dựng từ kho của project, không chuyển được nguyên trạng. Đề nghị điều 3 là tùy chọn;
  - chính sách này hợp với văn bản pháp luật; quy chế nội bộ và mẫu biểu cần tiêu chí riêng.

**N7. Phân loại file dùng chung (cổng nhận)**
- Vấn đề: Q-b.
- Đề xuất một phân loại dùng chung cho mọi đường nhận file:

  | Kết luận | Nghĩa |
  |---|---|
  | `dat` | Dùng được |
  | `ban_quet` | Không có lớp chữ |
  | `lop_chu_kem` | Lớp chữ kém: tỉ lệ âm tiết hợp lệ dưới ngưỡng |
  | `sai_van_ban` | Dòng "Số:" in năm khác siêu dữ liệu |
  | `khong_phai_phan_chinh` | Trang đầu không có quốc hiệu |
  | `chua_xac_minh` | Không đủ căn cứ kết luận |
  | `hong` | Không mở được |

- Áp ngay lúc tải, lưu kết luận kèm lý do. Chỉ `dat` mới được nhận vào thư viện.
- Tham chiếu: `working/tai-van-ban-phap-luat/<thư mục công cụ kho>/cong_nhan.py`, SHA-256 `dbd22eef5fb2f296d16fd1cd1817e73ffa0e42a57f33dd158f6ffe569faf5063`.
- Bằng chứng ở project:
  - 13 file đã biết vấn đề cho đúng kết luận;
  - chạy trên 2.541 file thật;
  - lần đầu, kết luận `sai_van_ban` dương tính giả với văn bản được trích dẫn trong file; đã sửa bằng cách chỉ đọc dòng "Số:" có dấu hai chấm.
- **Lưu ý giấy phép:** mã tham chiếu dùng PyMuPDF (AGPL/thương mại). LAW đã chốt `pdfminer.six` tùy chọn cho P3. Nếu nhận N7 phải viết lại trên engine đã chốt; không mang PyMuPDF vào.
- Nơi đặt: mở rộng P3 (cùng engine, cùng quy ước mã thoát). Mốc F6, V4. Kiểm "tỉ lệ âm tiết hợp lệ" cần từ điển/regex âm tiết tiếng Việt; regex thuần là đủ cho mức cảnh báo.

### Nhóm C: ghi dữ liệu, cần review độc lập

**N8. Cột nguồn gốc trong sổ**
- Bốn cột thêm vào cuối sheet Danh mục: "Toàn văn lấy từ", "Đã đọc toàn văn", "ID quét", "Siêu dữ liệu lấy từ".
- Danh sách thả xuống viết sẵn trong ô, không dùng validation trỏ sheet khác (x14) để `lossy_notices` không chặn ghi. Thêm hướng dẫn ở sheet Hướng dẫn. Ghi chú nguồn cũ chuyển nguyên văn sang cột mới.
- Không đổi tên, không đổi thứ tự cột cũ.
- Tham chiếu: `scripts/cap_nhat_cau_truc_index.py`, SHA-256 `c5a3d45c558bbfb3517d46484ad43908402bca42c43ce7a5e29abb22c464a24b` (chạy qua `locked_commit`).
- Nơi đặt: schema sổ của `tools/library.py` (KEYS theo tiền tố tiêu đề). Mốc R2/A-03, V7.
- Đây là **đổi schema**: cần thiết kế PRE/POST, nâng cấp sổ cũ, review độc lập. Liên quan câu hỏi binding đã nêu ở revision 28 của roadmap văn phòng (ý 2.1).

**N9. Nhập lại hàng loạt có kiểm soát**
- Lệnh gỡ toàn bộ dòng do đợt nhập hàng loạt tạo (nhận diện bằng dấu trong Ghi chú) rồi nhập lại, trong cùng một giao dịch:
  - giữ Mã cũ cho văn bản cùng số hiệu;
  - dòng có sẵn chỉ được đổi đúng các ô cho phép, kiểm theo Mã;
  - chỉ thay file thuộc riêng dòng nhập cũ và không dòng nhập tay nào dùng; file cũ để riêng, hoàn tác nếu ghi sổ lỗi;
  - xóa file nhập cũ không còn dùng sau khi commit.
- Tham chiếu: `scripts/nhap_ung_vien_vao_index.py`, SHA-256 `2b938467dfc29ef0e21b4941fa6127429db048c3da2e82669f51a274f84e1845`.
- Bằng chứng: chạy thật ba lần.
  - Lần 1 dừng đúng vì file đích khác nội dung.
  - Lần 2 bị chặn do lỗi Q-g, hoàn tác đúng, kiểm SHA file cũ trở lại.
  - Lần 3 ghi 327 rồi 426 dòng, giữ 327 Mã cũ.
- Nơi đặt: nối P1 (owner `transaction.py` + `library_sync.py`). Mốc V7 (bảo toàn), R2. Cần review độc lập vì xóa và thay file.

### Nhóm D: năng lực cho gói `phap-ly` (đang DEFER) hoặc mẫu kho dữ liệu ngoài

**N10. Mẫu kho dữ liệu ngoài hai lớp**
- Vấn đề: Q-f.
- Quy ước cho kho tra cứu ngoài thư viện (ví dụ SQLite trên ổ đồng bộ):

  | Tên gọi | Là gì |
  |---|---|
  | Gói chính | Nơi duy nhất làm sạch |
  | Bản làm việc cục bộ | Công cụ ghi vào đây trước, rồi xuất bản nguyên khối |
  | Web nguồn | Chỉ đọc |
  | Lớp thô | Bảng như đã tải; được làm mới khi quét lại; không sửa thẳng |
  | Lớp sạch | Bảng `sach_*`; mỗi dòng có bằng chứng, cách xác định (script, model, người) và ngày |
  | Dải id riêng | Cho văn bản lấy từ nguồn khác (≥ 900000000) |

- Ghi rõ ở `PROJECT.md`, README công cụ, hướng dẫn đi kèm gói, danh mục nguồn.
- Đợt 1 mục 3 đã nói kho SQLite "có thể thành mẫu chung sau này". Đề nghị chỉ nhận **quy ước tài liệu** trước, chưa nhận mã.
- Mốc V3.

**N11. Lô việc cho model nhỏ, kiểm trích nguyên văn khi nhập**
- Script đọc toàn văn và rút đoạn cần đọc (câu có số hiệu kèm câu dẫn danh sách, điều khoản hiệu lực, phần đầu, phần cuối, dãy số Điều, phụ lục) thành lô JSONL. Model nhỏ (Haiku) chỉ đọc lô và ghi JSONL.
- Script nhập chỉ nhận kết quả khi:
  - mọi đoạn trích có **nguyên văn** trong đoạn đã giao;
  - ngày hợp lệ;
  - khóa khớp lô vào.
- Tham chiếu: `<thư mục công cụ kho>/lo_haiku.py`, SHA-256 `a7e0e141112a6fe9cf0e0f1e4d29a15cf386286b8b0545370a4b5817afa9515d`.
- Bằng chứng thử 31/10 (3 lô):

  | Loại việc | Kết quả |
  |---|---|
  | Nhãn lĩnh vực | 78/79 hợp lệ; 14/14 mẫu đọc lại hợp lý (so theo khóa); 1 việc bị bỏ sót |
  | Kiểm toàn văn | 25/25 hợp lệ; chưa đọc lại nội dung |
  | Quan hệ | 39/40 hợp lệ; **1 bị chặn vì trích không nguyên văn**; 18/40 việc được giao không có đoạn nào (lỗi bộ xuất, sẽ sửa) |

- Bài học khi đọc kết quả: phải so theo khóa, không theo thứ tự dòng (một lần so theo thứ tự đã cho kết luận sai về chất lượng).
- Nơi đặt: phương pháp trong `roles/office` (Worker model nhỏ cho việc đọc lặp), nối mục 8.4 phân vai model. Mốc V4/V6.
- Cần quyết: đưa thành phương pháp chung hay chỉ ghi chú cho `phap-ly`.

**N12. Đối chiếu quan hệ văn bản bằng toàn văn; theo dõi tình trạng định kỳ**
- **Quy chiều nhãn quan hệ.** Quy mỗi nhãn của nguồn về (văn bản tác động, văn bản bị tác động, hành động):
  - nhãn không tiền tố là việc văn bản nguồn làm;
  - nhãn "Văn bản …" là vai trò của văn bản đích;
  - quy ước này kiểm bằng ví dụ có ngày ban hành.
- **Xác nhận bằng toàn văn.** Tìm trong toàn văn của văn bản tác động câu có số hiệu kia và đọc động từ:
  - chỉ tin động từ đứng trước số hiệu;
  - sau số hiệu chỉ tin "hết hiệu lực";
  - mục liệt kê đọc câu dẫn;
  - bỏ dạng "đã được sửa đổi tại X".
- **Kết luận** có bằng chứng: `xac_nhan`, `khac_hanh_dong`, `chi_dan_chieu`, `khong_thay`, `khong_toan_van`, `nguoc_ngay`.
- **Bằng chứng:** 23.235 quan hệ. Ở năm lĩnh vực ưu tiên, 75% (2.441/3.268) xác nhận bằng script. Đọc tay 10 ca ngẫu nhiên: 8 đúng rõ, 2 bằng chứng yếu; đã sửa 2 luật sau lần đọc đó.
- **Theo dõi tình trạng:** chụp tình trạng trước mỗi lần quét lại, so sau khi quét, ghi lịch sử, báo cáo văn bản trong thư viện bị đổi.
- Tham chiếu: `<thư mục công cụ kho>/doi_chieu_quan_he.py` SHA-256 `af2fdd03e378e755daea01fe2474af1c9f344f3a41e39f98bb8a225e9ff08542`; `<thư mục công cụ kho>/theo_doi_tinh_trang.py` SHA-256 `8d79eb8ec49cbf503ddde8da63136143caa04466706560a2f90652d9fcf8833a`.
- Nơi đặt: gói `phap-ly` (DEFER). Mốc theo hàng `phap-ly` ở roadmap văn phòng.

**N13. OCR tiếng Việt có tự kiểm lớp chữ**
- Tesseract `vie` qua engine PDF.
  - Lớp chữ ẩn ghi bằng font hệ thống; sửa bảng ToUnicode cho các glyph dùng chung (gạch nối mềm, khoảng trắng không ngắt…).
  - Tự kiểm từng trang: tập ký tự đọc lại bằng chữ có sẵn cộng chữ OCR, khác thì loại.
- Bằng chứng: 167 văn bản, 161 có kết quả, 6 bị chính bước tự kiểm loại (lệch 1 ký tự). Qua cổng N7: 137 đạt.
- Tham chiếu: `scripts/ocr_ban_quet.py`, SHA-256 `619109b265a74089a6892bf40e64af34d30551efdb6ac16a729b08d05cd325f0`.
- **Không đề xuất nhận mã:** phụ thuộc PyMuPDF (AGPL) và Tesseract cài ngoài. Chỉ đề xuất ghi vào `phap-ly` như **năng lực tùy chọn của host**, kèm quy tắc trích nguyên văn từ bản OCR phải soát với ảnh trang.

## 3. Không đề xuất đưa lên LAW

- Dữ liệu và danh mục văn bản của project, kể cả cấu hình phạm vi quét, từ khóa lĩnh vực và từ điển âm tiết.
- Gói dữ liệu, trang tra cứu, tài khoản nguồn.
- Skill riêng nghiệp vụ của đơn vị.
- Bộ lọc riêng theo cơ quan, lĩnh vực của người dùng.

## 4. Thứ tự và đối chiếu mốc (quy tắc 10)

| Thứ tự | Mục | Gắn mốc/owner | Rủi ro | Phụ thuộc |
|---|---|---|---|---|
| 1 | N1, N2, N3, N5 | V6, V4, V1/V2; mẫu `SKILL_INDEX`/`CLAUDE.md`/`PENDING_LESSONS`/`tools/README` | Thấp, tài liệu | Main bảo trì chốt cách viết N1 so với `AGENTS.md` |
| 2 | N4 | `source-library`, P4/P2, V3 | Trung bình: đổi ranh giới nguồn (POST) | Review độc lập |
| 3 | N6, N7 | F6, P3, V4 | Thấp đến trung bình: chỉ cảnh báo; N7 phải viết lại trên `pdfminer.six` | P3 đã nhận có giới hạn |
| 4 | N8, N9 | R2/A-03, P1, V7 | Cao: schema sổ và xóa/thay file | P1 PRE/protocol; review độc lập |
| 5 | N10–N13 | `phap-ly` (DEFER), V3, 8.4 | Theo từng mục; N13 vướng giấy phép | Quyết định mở lại `phap-ly` |

**Phiếu này không đóng** điều kiện nào của V1–V7, R2/A-03–A-06, F6 hay hàng `phap-ly`/`source-library`. Nó chỉ cung cấp đầu vào có bằng chứng từ ca thật.

Toàn bộ điều kiện còn mở giữ nguyên như hai roadmap ghi, gồm:
- `PRERELEASE_NOT_READY`;
- P1 `EXECUTION_PROTOCOL_NOT_MET`;
- P2 `PLANNED`;
- `phap-ly` DEFER;
- final gates;
- academic PAUSED.

Mỗi mục khi nhận phải qua chuẩn tiếp nhận `skills/README.md`. Mục đụng ranh giới nguồn, ghi dữ liệu hoặc schema (N4, N8, N9) cần review độc lập.

## 5. Đã kiểm và chưa kiểm

- **Đã kiểm trong project** (Windows, Python 3.11, SQLite qua thư viện chuẩn): các số liệu ở mục 1–2, trên dữ liệu thật của project.
  - Giao dịch ghi sổ qua `locked_commit`; `library.py check` 0 lỗi sau mỗi lần ghi.
  - Bước tự kiểm của OCR và bước kiểm trích nguyên văn của N11 đã chặn đúng ca lỗi thật.
- **Chưa kiểm:**
  - bộ test và gate của kho nguồn LAW; Python 3.8; macOS/Linux;
  - N7 trên `pdfminer.six`;
  - độ đúng nội dung của từng văn bản (sổ vẫn "Cần đối chiếu");
  - chất lượng đầy đủ của lô Haiku trên toàn bộ việc (mới thử 3 lô);
  - N1/N2 trên host khác ngoài Claude Code;
  - review độc lập cho các thay đổi ở project (bộ quét, cổng nhận, nhập lại, cột `origin_url`) chưa có.
