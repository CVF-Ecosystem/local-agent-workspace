# Đề xuất nâng cấp LAW rút từ một project người dùng: tiếp nhận và tải văn bản pháp luật

- Người lập: Claude (Main điều phối trong một project người dùng chạy LAW 1.9.0), 30/10/2026.
- Trạng thái: **ĐỀ XUẤT**, chưa phải brief giao thi công. Main bảo trì cần đối chiếu mục 8.3/8.4 của
  `ROADMAP_HOAN_THIEN.md` và lập brief theo quy tắc 10 trước khi giao.
- Riêng tư: kho nguồn này công khai. Phiếu không kèm dữ liệu nghiệp vụ, tên đơn vị, tài khoản hay hệ thống riêng của
  người dùng. Mã nguồn tham chiếu nằm trong project người dùng (operator giữ đường dẫn); dưới đây chỉ ghi đường dẫn
  tương đối trong project và SHA-256 để đối chiếu đúng bản.

## 1. Bối cảnh: lỗi thực tế đã gặp (29–30/10/2026)

Một agent khác trong project đã viết bộ script tải văn bản pháp luật và nhập vào sổ `references/_INDEX.xlsx`.
Khi rà soát, phát hiện các lỗi sau (đều đã sửa trong project):

| # | Lỗi | Hậu quả |
|---|---|---|
| L1 | Script nhập tự ghi "Đã đối chiếu toàn văn" cho 15 dòng ngay khi tải xong | Sổ khẳng định đã đọc đối chiếu khi chưa ai đọc; trái quy tắc "file mới vẫn Cần đối chiếu" của `source-library` |
| L2 | Một luật được gắn file của văn bản hợp nhất (trùng từng byte với dòng VBHN) | Sổ ghi có toàn văn bản gốc nhưng thực tế là bản khác |
| L3 | Một luật được gắn "tài liệu giới thiệu nội dung" thay cho toàn văn | Như trên |
| L4 | Một script dùng link đoán theo mẫu tên: 12/15 link trả về 404 | Script hỏng, báo cáo vẫn ghi "đã kiểm tra" |
| L5 | Tắt kiểm chứng chỉ TLS; ghi đè file đã có; trang báo lỗi HTML lớn hơn 1 KB vẫn tính là tải được | Rủi ro dữ liệu sai lọt vào thư viện mà không ai biết |
| L6 | Script nhập quét cả thư mục lĩnh vực và di chuyển file người dùng theo regex lỏng | Có thể đổi tên/ghi đè file đặt đúng chỗ |
| L7 | PDF tải về là bản quét ký số 200 dpi, không có lớp chữ (35 trang chỉ có 147 ký tự của con dấu) | Không tìm kiếm, không trích nguyên văn được |

`library.py check` báo **0 lỗi** trong suốt thời gian các lỗi L1–L3 tồn tại: check hiện không phát hiện được các loại sai này.

## 2. Đề xuất

### P1 — Quy tắc tiếp nhận an toàn cho file nguồn mới tải

- Tham chiếu: `working/tai-van-ban-phap-luat/scripts/import_legal_files.py`,
  SHA-256 `40f47f4abacc373d9b852650d25a272baff8712c578cb03d54019049a7369bfc`.
- Hành vi đề xuất: chỉ nhận file trong thư mục chờ (`references/legal/_moi_tai/`); mặc định xem trước, `--apply` mới
  ghi; không ghi đè (đích đã có thì báo "giống hệt" hay "khác nội dung" bằng SHA-256); nhận diện bằng regex chỉ khi
  **đúng một** mã khớp, nhiều file cùng mã thì bỏ qua; luôn ghi mức "Cần đối chiếu"; ghi sổ lỗi (ví dụ Excel đang mở)
  thì trả file về thư mục chờ; sau cùng gọi `library.py sync --apply` và `check` (không tự ghi ID/hash ngoài owner).
- Nơi đặt: script của skill `source-library` (hoặc một lệnh nhập của `library.py` nếu Main bảo trì thấy hợp hơn);
  DOC_CATALOG kiểu bảng mã → tên chuẩn phải là cấu hình của project, không nhúng trong mã.
- Nghiệm thu đề xuất: test trên bản sao project cho các ca: xem trước không ghi; tên khớp nhiều mã bị bỏ qua;
  đích đã có (giống/khác) không bị ghi đè; hai file cùng mã bị bỏ qua; sổ chỉ đọc → file trả về chỗ cũ, sổ không đổi;
  ca thường → sổ có đường dẫn, "Cần đối chiếu", sync ghi revision 1 + SHA, check 0 lỗi.
- Bằng chứng đã có trong project: các ca trên đã chạy trên bản sao và đạt (chưa chạy trong bộ test của kho nguồn).

### P2 — Tải bản chữ từ Công báo điện tử theo sổ

- Tham chiếu: `working/tai-van-ban-phap-luat/scripts/tai_tu_cong_bao.py`,
  SHA-256 `503cb840df08ca014222d58d9cb5f5136faa6e7c22dd8d8e783acaaf8c621748`.
- Vấn đề giải quyết: L7. Trang văn bản trên congbao.chinhphu.vn có PDF có lớp chữ (và thường kèm Word). Trong project,
  30/34 dòng sổ tìm được trên Công báo; sau khi chạy, 31/34 văn bản có bản chữ.
- Hành vi: đọc sổ; tìm qua API tìm kiếm mà chính trang Công báo dùng; chỉ nhận khi trùng số hiệu **và** trích yếu gần
  với sổ (cùng số hiệu có thể là văn bản khác, ví dụ một số hiệu vừa là Bộ luật vừa là một nghị quyết); ghép các phần
  đăng ở nhiều số Công báo theo thứ tự số; chỉ nhận PDF có lớp chữ và có đúng số hiệu ở hai trang đầu; dòng chưa có file
  thì đưa vào thư mục chờ rồi gọi P1; tùy chọn thay bản quét (bản cũ chuyển `archive/`, sync tăng revision); ghi nguồn
  tải vào cột Ghi chú. Kiểm chứng chỉ TLS luôn bật (dùng kho chứng chỉ hệ điều hành qua `truststore` vì máy chủ tải file
  gửi thiếu chứng chỉ trung gian).
- Nơi đặt: gói `phap-ly` (đang DEFER) hoặc `source-library`. Cần quyết định trước: điều khoản/quyền dùng nguồn,
  vì API không có tài liệu chính thức nên có thể đổi bất kỳ lúc nào (công cụ phải báo lỗi, không tải bừa).
- Giới hạn đã biết: văn bản cũ (khoảng trước 2006) và văn bản hợp nhất của bộ không có trên Công báo; có văn bản Công báo
  cũng chỉ có bản quét (công cụ từ chối đúng). Không vượt CAPTCHA/đăng nhập của bất kỳ trang nào (xem P4).

### P3 — `library.py check` cảnh báo các dấu hiệu sai mà hiện không bắt được

- Hành vi đề xuất (chỉ cảnh báo, không tự sửa):
  - PDF trong thư viện không có lớp chữ (trung bình dưới khoảng 300 ký tự/trang) → "bản quét, không trích nguyên văn được".
  - Hai dòng khác mã trỏ tới hai file trùng SHA-256 → nghi gắn nhầm (bắt được L2).
  - Dòng "Đã đối chiếu toàn văn" mà file có SHA đổi sau lần đối chiếu, hoặc file là bản quét → cảnh báo.
- Nơi đặt: `tools/library.py` (hàng F6 / R2 của `ROADMAP_HOAN_THIEN.md`). Cần quyết định phụ thuộc đọc PDF
  (PyMuPDF có sẵn ở máy người dùng nhưng chưa chắc trong gói); thiếu thì ghi "chưa kiểm lớp chữ", không giả đạt.
- Nghiệm thu đề xuất: fixture có PDF bản quét, PDF có chữ, hai dòng trùng file; check ra đúng cảnh báo, mã thoát
  không đổi so với quy ước hiện hành.

### P4 — Quy tắc tải nguồn an toàn (văn bản quy tắc, không cần mã mới)

Đưa vào `skills/README.md` (mục script) hoặc `source-library/SKILL.md`:
kiểm chứng chỉ TLS luôn bật; kiểm byte đầu file đúng định dạng (`%PDF`, `PK\x03\x04`, `{\rtf`, OLE) trước khi nhận;
tải vào thư mục chờ, không ghi thẳng vào thư mục lĩnh vực, không ghi đè; không dùng link đoán theo mẫu tên khi chưa thử;
"tải được" không phải "đúng văn bản": đối chiếu số hiệu/trích yếu và để "Cần đối chiếu"; không vượt CAPTCHA hay đăng nhập
của trang nguồn (trang có CAPTCHA thì người dùng tự tải bằng trình duyệt rồi đưa vào thư mục chờ).

## 3. Không đề xuất đưa lên LAW

Công cụ xuất dữ liệu từ hệ thống lưu trữ riêng của người dùng, kho SQLite tra cứu và trang xem của nó, dữ liệu nghiệp vụ,
hồ sơ và thư viện của project. Phần kho tra cứu SQLite + trang web chạy trên máy có thể thành mẫu chung sau này, nhưng cần
tách khỏi hệ thống riêng và qua tiếp nhận riêng.

## 4. Đối chiếu mốc (quy tắc 10)

- Mốc liên quan: `ROADMAP_VAN_PHONG_NGHIEP_VU.md` dòng `source-library` 1.1 (S175 code fix accepted bounded, chưa
  release) và `phap-ly` 0.2.0 (DEFER); `ROADMAP_HOAN_THIEN.md` R2 / A-03 (R2a ghi nhận file nguồn) / F6 (check).
- Phiếu này **không đóng** điều kiện nào của các mốc trên; chỉ cung cấp đầu vào có bằng chứng từ ca thật. Toàn bộ điều
  kiện còn mở giữ nguyên như roadmap ghi (kể cả PRERELEASE_NOT_READY, quyền nguồn của `phap-ly`, final gates).
- Đề nghị thứ tự: P3 và P4 trước (nhỏ, rủi ro thấp); P1 sau (đụng ghi dữ liệu thư viện, cần review độc lập);
  P2 sau khi chốt quyền nguồn của gói `phap-ly`. Mỗi phần qua chuẩn tiếp nhận `skills/README.md` và review độc lập
  vì đụng ranh giới nguồn và ghi dữ liệu.

## 5. Đã kiểm và chưa kiểm

- Đã kiểm trong project (bản sao, Windows, Python 3.11, SQLite 3.45): các ca của P1; P2 chạy thật trên sổ 34 dòng
  (18 tải mới, 11 thay bản quét, từ chối đúng 1 bản quét và 3 văn bản không có); thứ tự ghép nhiều số Công báo kiểm bằng
  số Công báo theo trang và số Điều tăng dần; `library.py check` 0 lỗi sau khi chạy.
- Chưa kiểm: bộ test và gate của kho nguồn; macOS/Linux; tính ổn định lâu dài của API Công báo; nội dung toàn văn
  từng văn bản (sổ vẫn "Cần đối chiếu"); P3 chưa viết mã.
