# Ý kiến của Claude — nguyên tắc nghiệm thu chung cho LAW (core, package, skill)

**Ngày:** 28/10/2026. **Người lập:** Claude (Opus 5.5), theo câu hỏi của operator "Ý bạn thế nào?".
**Đối tượng:** nguyên tắc operator nêu trong hội thoại 28/10: đội phát triển giao sản phẩm đã tự kiểm, người dùng không phải làm nốt việc kiểm thử;
bảng ba thành phần (core, package/skill, bản phân phối) và năm câu hỏi của hồ sơ nghiệm thu từng gói.
**Trạng thái:** góp ý, không thay quyết định operator; Codex đang được giao đồng bộ nguyên tắc vào roadmap, chuẩn tiếp nhận và hồ sơ gói.

## 1. Kết luận

**Đồng ý.** Nguyên tắc sửa đúng chỗ lệch hiện nay: hàng rào quy trình đã dày, còn chuẩn "đầu ra đạt" chưa có chủ. Năm câu hỏi đủ và không đòi
benchmark lớn. Claude đề nghị thêm bảy điểm để khi áp vào không bị hiểu sai hoặc tự sinh thêm thủ tục.

## 2. Bảy điểm đề nghị làm rõ

### 2.1. Mức bằng chứng theo rủi ro, ghi thẳng vào nguyên tắc

Nếu không ghi, mỗi skill sẽ bị kéo về mức nặng nhất (đúng điều đang muốn tránh). Đề xuất dùng lại mục "Mức thận trọng cao" của `AGENTS.md`, không
tạo thang mới:

| Nhóm | Ví dụ | Câu 3 "đã chứng minh bằng gì" tối thiểu |
|---|---|---|
| Thường | `vietnamese-editing`, `meeting-minutes`, `internal-comms` | Vài ca đại diện + ca thiếu dữ liệu; review đầu ra |
| Có số liệu/định dạng ràng buộc | `excel-workbooks`, `spreadsheet-check`, `vn-admin-documents`, `container-yard-check` | Kiểm tự động phần đo được (công thức, số, thể thức) + ca lỗi điển hình |
| Thận trọng cao | `phap-ly`, `ke-toan-noi-bo`, `academic-research`, `source-library` khi trích dẫn | Đáp án do người có chuyên môn duyệt, ca gài lỗi, kiểm trích dẫn tự động, ca ngoài mẫu |

### 2.2. Áp cả cho những gì đang có, và nói thật trạng thái hiện nay

Theo nguyên tắc mới, **hiện chưa có gói nào đạt "sẵn dùng"**:
- Cả 6 gói đang `DEFER`. `packs/README.md:14` tự ghi "five bundled packs are trial versions that have not been through intake. Their legal basis was
  compiled from news and advisory sites and has not been checked article by article…".
- 14 skill dùng chung `AVAILABLE` có từ **trước** chuẩn tiếp nhận; index ghi "chưa kiểm routing host thật". Theo nguyên tắc, nhãn `AVAILABLE` phải
  được đổi nghĩa thành "đã qua nghiệm thu nội bộ", nên 14 skill này cần hồ sơ năm câu (mức theo 2.1), hoặc chuyển sang nhóm thử nghiệm.
- Hệ quả cho bản phát hành tới: các gói chỉ được giới thiệu là thử nghiệm; tài liệu (`START_HERE`, `HUONG_DAN_SKILLS_VI`, `packs/README.md`) không
  dùng chữ "sẵn dùng" cho chúng.

Đề xuất làm theo thứ tự rủi ro: gói thận trọng cao đang được dùng thật trước (`phap-ly`), skill dùng chung nhóm thường sau.

### 2.3. Tách "chất lượng" khỏi "đồng ý dùng" bằng hai trường khác nhau

Hiện `intake.decision` trong `pack.json` là lời khai của gói, còn `pack.py confirm` của người dùng ghi `AVAILABLE` trong index project
(`packs/README.md:54-60`). Hai việc đang dùng chung một chữ, dễ hiểu nhầm là người dùng xác nhận chất lượng. Theo nguyên tắc:
- **Chất lượng** do đội phát triển kết luận, đi kèm gói: ví dụ `intake.decision = ACCEPTED` + hồ sơ năm câu + ngày.
- **Bật dùng** là quyết định của người dùng trong project: `pack.py add/confirm` chỉ ghi "đã bật", không đổi kết luận chất lượng.
Cần một câu trong `packs/README.md` và hướng dẫn: người dùng xác nhận là đồng ý dùng, không phải nghiệm thu.

### 2.4. Gói pháp lý: đội phát triển bảo đảm gì, không bảo đảm gì

Pháp luật đổi sau ngày phát hành, nên nghiệm thu không thể là "đáp án đúng mãi". Đề xuất câu 2 của gói pháp lý ghi rõ:
- Đội phát triển bảo đảm: skill dẫn đúng nguồn có trong thư viện, trích nguyên văn đúng (kiểm tự động), ghi ngày đối chiếu và tình trạng hiệu lực,
  từ chối kết luận khi thiếu nguồn hoặc nguồn chưa kiểm, và không trình bày gợi ý như ý kiến pháp lý.
- Kết quả đúng tại **ngày đối chiếu** được người có chuyên môn duyệt (luật sư thử mà operator định mời là một phần nghiệm thu nội bộ, **không phải**
  phản hồi người dùng).
- Hồ sơ gói có **ngày kiểm lại** và danh sách văn bản cần theo dõi; quá hạn thì gói tự hạ về thử nghiệm hoặc cảnh báo khi dùng.
- Căn cứ lấy từ báo/tư vấn (như ghi chú hiện tại ở `packs/README.md:14`) không đủ cho nhóm thận trọng cao; phải đối chiếu văn bản chính thức.

### 2.5. Câu 4 "có ích hơn cách sẵn có": đo đúng giá trị đã tuyên bố

Với nhiều skill văn phòng, giá trị là đúng mẫu, đúng thể thức, nhất quán, không phải "thông minh hơn native". Đề xuất mỗi hồ sơ ghi **một câu
tuyên bố giá trị**, rồi chỉ chứng minh câu đó. Nếu không nêu được phần tăng thêm so với native thì gói nên thu hẹp hoặc bỏ (đúng tinh thần R2 chống phình).
Gói học thuật là ví dụ: hồ sơ hiện ghi chưa chứng minh được lợi ích; theo nguyên tắc, gói đó ở nhóm thử nghiệm cho tới khi có.

### 2.6. "Môi trường được công bố hỗ trợ" phải là một danh sách cụ thể

Câu 5 và hàng "LAW core" phụ thuộc danh sách này (hệ điều hành, phiên bản Python, host: Claude Code, Codex, Cowork, Antigravity...). Danh sách đó là
support matrix của V7, đang còn mở. Đề xuất: chưa kiểm host nào thì không ghi host đó là hỗ trợ; ghi "chưa kiểm" thay vì để trống. Bản phân phối
kiểm cả **tạo mới** lẫn **nâng cấp** từ bản trước (đợt này mới thử tạo mới).

### 2.7. Đặt vào chỗ đã có, không tạo sổ mới

- Năm câu hỏi → thành khung của `packs/_template/references/intake-record.md` và mục tiếp nhận trong `skills/README.md` (thay cho phần đang viết
  rời "sáu điều kiện" + "ba việc thật"; sáu điều kiện vẫn dùng làm nội dung chi tiết của câu 2–5).
- Kết luận từng gói → `pack.json` `intake` + hồ sơ gói; skill dùng chung → cột Notes của `SKILL_INDEX.md` trỏ tới hồ sơ.
- Mốc → V7 (core, bản phân phối) và V4/AC (chất lượng gói), như operator nêu; không tách tranche cho từng phép kiểm.
- Bản phân phối → thêm vào kiểm phát hành hiện có một luồng trọn: tạo project từ zip, cài một gói, làm một ca, kiểm đầu ra. Không thêm cổng phê duyệt.

## 3. Rủi ro khi áp

- **Tồn đọng lớn:** 14 skill + 6 gói cần hồ sơ. Không làm hết trước phát hành thì phải chấp nhận ghi "thử nghiệm" cho phần chưa đạt; không được hạ
  chuẩn để kịp.
- **Nguy cơ thành thủ tục:** nếu năm câu bị điền cho có, nó thành thêm một lớp giấy tờ. Đo bằng việc hồ sơ có ca thật, kết quả có căn cứ và lỗi đã bắt
  được, không bằng số trang.
- **Người duyệt nội dung:** nhóm thận trọng cao cần người có chuyên môn; chưa có thì gói ở lại nhóm thử nghiệm, không thay bằng AI review.

## 4. Đã xem, chưa xem

Đã đọc lướt `working/legal-quality-20261028/CA_PHAP_LY_CHUAN_BI.md` (57 dòng; trạng thái `NOT_APPROVED`, 6 ca, 3 nguồn DOCX có hash, chưa đưa vào
`references/`): hướng đi khớp nguyên tắc (giữ đáp án trống tới khi người có chuyên môn duyệt, tách kiểm cơ học khỏi đánh giá pháp lý). Đã grep
`packs/README.md` và `.agent/SKILL_INDEX.md` để dẫn các dòng trên. Chưa review `tools/check_quotes.py` mà file đó nhắc tới, chưa đọc đủ các hồ sơ
gói, chưa kiểm phần Codex đang đồng bộ.
