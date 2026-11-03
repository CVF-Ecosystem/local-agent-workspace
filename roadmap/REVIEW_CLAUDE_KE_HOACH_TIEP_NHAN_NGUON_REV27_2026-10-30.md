# Review của Claude: kế hoạch tiếp nhận nguồn trong roadmap văn phòng revision 27

- Người review: Claude (Opus 5.5), 30/10/2026, theo yêu cầu của operator. Không sửa roadmap, HANDOFF hay code. Lượt 2
  (cùng ngày): operator đồng ý chuyển hai script tham chiếu; Claude chép nguyên bytes vào `working/` (mục 5) và bổ sung
  phản biện script cùng đề xuất xử lý (mục 5–6).
- Đối tượng: `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` mục "Nâng cấp tiếp nhận nguồn — kế hoạch cụ thể 30/10/2026"
  (dòng 23–104), SHA-256 `e7bbaaeba48b767ae74dad8f5b3707f0068b274f8b0205f17e48542eebf67009`.
- Đối chiếu với: phiếu đầu vào `roadmap/DE_XUAT_NANG_CAP_TU_PROJECT_THU_VIEN_PHAP_LY_CLAUDE_2026-10-30.md`
  (`9254a811…7794d`), `tools/library.py` (`3144e937…dafd`, đọc `cmd_check` và tên cột `law_*`), danh sách hàm của
  `tools/transaction.py`, đầu `.agent/HANDOFF.md`.

## Kết luận

**Đồng ý hướng đi và thứ tự P3/P4 → P1 → P2.** Kế hoạch có đối chiếu mốc theo quy tắc 10, không mở tranche mới và
giữ nguyên các blocker. Nó cũng sửa đúng một số điểm yếu của phiếu. Trước khi giao thi công P3/P4 cần làm rõ năm điểm
(mục 2). Các điểm này đều nhỏ, có thể sửa ngay trong brief/HANDOFF; không cần lập kế hoạch lại.

## 1. Những điểm kế hoạch làm tốt hơn phiếu (đồng ý)

1. P1 ghi rõ "copy rồi gọi sync rời rạc không phải nguyên tử" và yêu cầu PRE review thiết kế giao dịch file+sổ. Phiếu
   đề xuất "lỗi thì trả file về thư mục chờ, sau cùng gọi `sync --apply`", cách này có khe hở khi tiến trình dừng giữa
   hai bước. Đồng ý với cách sửa này.
2. Ngưỡng 300 ký tự/trang chỉ là dấu hiệu, xét theo từng trang. Đúng: ca L7 (35 trang, 147 ký tự của con dấu) bị bắt
   theo bất kỳ ngưỡng nào, nhưng PDF hỗn hợp (vài trang có chữ, phụ lục là ảnh quét) sẽ lọt nếu chỉ tính trung bình.
3. Magic bytes chỉ là một lớp kiểm. Đồng ý: HTML báo lỗi thì bắt được bằng `%PDF`, nhưng PDF cắt dở hoặc ZIP không phải
   OOXML thì vẫn qua.
4. Việc thay bản quét được tách khỏi importer create-only và chuyển sang P2, kèm quyền riêng. Đúng, đây là thao tác thay
   nguồn đang dùng, rủi ro khác hẳn việc nhập file mới.
5. Không ép cài `truststore`/PyMuPDF, và không nhận báo cáo chạy thật trong phiếu như raw evidence của LAW. Đúng phạm vi.

## 2. Điểm cần làm rõ trước khi giao P3/P4

**2.1. P3 so hash: nói rõ là dùng cột đã có, không đổi schema sổ.** `library.py` đã có các cột `LAW SHA-256`,
`LAW revision`, `LAW file state`. `check` đã cảnh báo "file đã đổi; cần đối chiếu revision mới" khi
`law_state == NEEDS_REVIEW`, tức phần "bytes chưa đồng bộ" đã được báo một phần qua sync. Còn thiếu hai việc:
(a) so các Mã khác nhau có cùng `LAW SHA-256`, làm được ngay trên cột đã ghi mà không cần đọc file; (b) gắn nhãn
"Đã đối chiếu toàn văn" với một revision/SHA cụ thể. Việc (b) cần thêm cột, tức đổi schema sổ, nằm ngoài "chế độ chỉ đọc"
của P3. Đề nghị ghi rõ trong brief: P3 chỉ cảnh báo "Đã đối chiếu toàn văn" + `NEEDS_REVIEW`/revision > 1 là "thiếu căn cứ
binding". Cột binding, nếu cần, để thành quyết định riêng ở P1 và qua review schema.

**2.2. Quy ước mã thoát khi thiếu PDF engine.** Kế hoạch ghi "giữ quy ước exit" nhưng chưa nói ca này. Hiện thiếu openpyxl
trả exit 2 (LibraryNotChecked). Đề nghị: phần kiểm cơ bản đã chạy được thì exit giữ theo lỗi/cảnh báo của phần đó; thiếu
engine chỉ thêm finding "chưa kiểm lớp chữ" kèm lý do, không trả 2. Nếu không chốt trước, Worker sẽ phải tự đoán.

**2.3. L3 (gắn tài liệu giới thiệu thay toàn văn) không có cách bắt cơ học.** Fixture của P3 không có ca L3. P1 chỉ ghi
nguyên tắc "bản giới thiệu không tự mang nhãn toàn văn", chưa có cơ chế phát hiện. Đề nghị ghi thẳng: L3 do P2 (đối chiếu
danh tính nhiều trường) và người đọc xử lý, P3 không tuyên bố bắt được. Như vậy không ai hiểu nhầm rằng P3 xong là đã che
cả L1–L7. Bảng đúng phải là: P3 bắt L2 và L7, bắt một phần L1; P4 là quy tắc cho L4/L5; P1 xử lý L1/L6; P2 xử lý L3/L7.

**2.4. Lựa chọn PDF engine nằm trên đường găng của P3.** Máy dev có PyMuPDF 1.27.2.2, chưa có `pypdf`. PyMuPDF dùng giấy
phép AGPL/thương mại, nên đóng gói kèm bản phân phối là vấn đề license chứ không chỉ là vấn đề kỹ thuật. Đề nghị Main
quyết trước khi code, chọn một trong ba: (a) engine thuần Python giấy phép dễ dãi (ví dụ `pypdf` BSD hoặc `pdfminer.six`
MIT), cài theo hướng dẫn và không vendored nếu chưa xét; (b) dùng engine khi máy có, thiếu thì báo chưa kiểm; (c) hoãn
phần lớp chữ. Tôi đề xuất (b) cho lần giao đầu, đúng với dòng "chưa có extractor thì không nhận capability" đã ghi. Brief
cần nói rõ engine nào được thử trong test để kết quả không phụ thuộc máy.

**2.5. Chữ dính trong phần tóm tắt.** Dòng 3 và dòng 7 của roadmap có nhiều cụm thiếu dấu cách ("đóng3printfindings",
"cầncleanrevision/exactartifact/gates", "CLIcodefixbounded/contentlimited/protocolscopeNOT_MET"). Đây là phần operator đọc
đầu tiên. Đề nghị sửa khoảng trắng ở hai dòng này khi cập nhật roadmap lần tới; không cần lượt riêng.

## 3. Góp ý không chặn

- **Phạm vi fixture P3/P4 hơi rộng so với "nhỏ, rủi ro thấp".** Ca junction ra ngoài scope và ca ZIP không đúng loại Office
  là hợp lý cho `--content-audit`. Nhưng nếu thời gian có hạn, đề nghị đóng P3 theo lõi (PDF có chữ/quét/hỗn hợp, trùng
  SHA khác Mã, đối chiếu thiếu binding, engine thiếu, HTML giả PDF), các ca còn lại ghi NOT_TESTED đúng tên. Không hạ tiêu
  chí đã ghi; đây chỉ là gợi ý thứ tự trong cùng bước.
- **Hai script tham chiếu:** operator đã quyết định chuyển (30/10/2026). Vị trí, SHA và phản biện ở mục 5.
- **P1 dùng `tools/transaction.py`:** file đã có `sha_file`, `CommitConflict` và fault injection. Brief P1 nên nêu đích
  danh owner này để PRE review đánh giá việc dùng lại, tránh viết journal thứ hai.

## 5. Hai script tham chiếu: vị trí, phản biện của Claude

**Vị trí và custody.** Operator đồng ý 30/10/2026. Claude chép nguyên bytes (`cp -p`) từ project người dùng
(`working/tai-van-ban-phap-luat/scripts/`) sang `working/source-intake-20261030/reference-scripts/` của kho nguồn.
`/working/` nằm trong `.git/info/exclude` (đã kiểm bằng `git check-ignore -v`), nên không vào commit hay bản công khai.

| File | SHA-256 sau khi chép | Khớp phiếu |
|---|---|---|
| `import_legal_files.py` (203 dòng) | `40f47f4abacc373d9b852650d25a272baff8712c578cb03d54019049a7369bfc` | Có |
| `tai_tu_cong_bao.py` (303 dòng) | `503cb840df08ca014222d58d9cb5f5136faa6e7c22dd8d8e783acaaf8c621748` | Có |

Claude đã đọc đủ hai file trước khi chép: không có mật khẩu, token hay tài khoản. `DOC_CATALOG` chỉ có số hiệu và tên văn bản
pháp luật công khai, nhưng danh sách lĩnh vực cho thấy nghiệp vụ của đơn vị. Vì vậy catalog không được đưa vào LAW, kể cả
fixture công khai; muốn dùng làm fixture thì lập catalog giả. Hai file là **đầu vào thiết kế, không phải code được nhận**:
chưa có license/provenance riêng ngoài việc người dùng và agent của họ viết trong project.

**Phản biện script, đồng thời là ca hồi quy cho P1/P2.** Ca có ghi "đã chạy" là do Claude chạy thử logic đúng như trong
script (hàm `fold`/`num_key`/regex sao lại), Python 3.11, trên chuỗi mẫu, không trên PDF thật.

| # | Script / vị trí | Vấn đề | Đề xuất cho LAW |
|---|---|---|---|
| S1 | `tai_tu_cong_bao.py:173` | Kiểm "đúng số hiệu ở hai trang đầu" bằng chuỗi con. **Đã chạy:** `22/2023/QH15` khớp trong `122/2023/QH15`, và khớp cả câu "Căn cứ Luật Đấu thầu số 22/2023/QH15" của một nghị định. Văn bản hướng dẫn luôn trích số luật ở phần căn cứ, nên phép kiểm này yếu đúng ở ca hay gặp nhất. | P2: so số hiệu theo ranh giới token, ở vùng tiêu đề/số hiệu của văn bản chứ không ở phần căn cứ; chỉ là bằng chứng hỗ trợ, kết hợp loại + cơ quan + ngày. Thêm fixture nghị định có căn cứ luật. |
| S2 | `import_legal_files.py:87–93` | Regex bắt theo chủ đề, không theo danh tính. **Đã chạy:** file `38-2019-QH14_luat-quan-ly-thue.pdf` (luật cũ) khớp đúng một mã `PL-TK-003` (Luật 2025) qua nhánh `quan.*ly.*thue`, nên được nhận. Nhánh `startswith(std_name)` còn nhận cả `<tên chuẩn>_ban-gioi-thieu.pdf` (nguồn gốc kiểu lỗi L3). | P1: "đúng một mã" chỉ là phân loại; nhận chỉ khi tên khớp chính xác tên chuẩn hoặc người dùng chọn mã. Nhánh chủ đề chỉ được gợi ý trong preview, không tự apply. |
| S3 | `import_legal_files.py:178–179` | Ghi đè `Đường dẫn file` của dòng đã có file khác, và đặt `Có toàn văn = Có` không cần điều kiện. | P1 create-only theo cả dòng: dòng đã có đường dẫn thì từ chối, chuyển sang luồng thay thế của P2. "Có toàn văn" không được suy ra từ việc có file. |
| S4 | `import_legal_files.py:172–188` | Rollback trong `except` có thể tự lỗi, để lại nửa trạng thái. `wb.save` ghi thẳng vào sổ, không qua file tạm. `sync` chạy sau như một bước rời; sync lỗi thì file đã chuyển, sổ đã đổi nhưng chưa có hash. | Đúng như roadmap đã nhận định. Dùng owner `transaction.py`/`library_sync`, journal trước khi chuyển; không gọi subprocess `sync` như bước hoàn tất. |
| S5 | `tai_tu_cong_bao.py:276–278` | Thay bản quét: `move` bản cũ ra archive rồi mới ghi bản mới. Ghi lỗi thì dòng trỏ vào file không còn. Không đặt lại `Mức độ xác minh`: dòng đang "Đã đối chiếu toàn văn" giữ nguyên nhãn với bytes mới (chỉ còn cờ NEEDS_REVIEW của sync). | P2: ghi bản mới vào staging, kiểm xong mới đổi chỗ; hạ mức xác minh về "Cần đối chiếu" trong cùng giao dịch với tăng revision. |
| S6 | `tai_tu_cong_bao.py:156–168` | Thứ tự ghép dựa trên tên file `<năm>_<số>`; không khớp mẫu thì về `(0,0)` mà không báo. Không kiểm đủ phần. PDF ghép được nén lại (`tobytes(garbage=3, deflate=True)`), nên hash trong sổ là của bản dẫn xuất; các phần gốc không được giữ. | Đúng như roadmap (giữ raw từng phần, manifest). Thêm: tên phần không parse được thì dừng, không mặc định thứ tự. |
| S7 | `tai_tu_cong_bao.py:94–99, 171` | Mật độ chữ tính trung bình trên cả bản ghép, nên PDF có phụ lục quét vẫn qua. | Đúng như roadmap (xét theo trang). |
| S8 | `tai_tu_cong_bao.py:54, 84–91` | Giả User-Agent Chrome; `resp.read()` không giới hạn dung lượng; không kiểm Content-Type; sau redirect không giữ URL cuối. | P2/P4: User-Agent trung thực (tên công cụ), giới hạn bytes, giữ URL cuối và mã HTTP. Việc giả trình duyệt cần Main xét cùng điều khoản nguồn. |
| S9 | `tai_tu_cong_bao.py:39`, `:191–201` | `import fitz` bắt buộc (PyMuPDF, AGPL). Ghi cột Ghi chú bằng `openpyxl` load/save riêng, ngoài owner. | Đúng như roadmap về dependency. Ghi provenance phải qua owner, có thể vào cột/journal riêng thay vì nối chuỗi vào Ghi chú. |
| S10 | `import_legal_files.py:155–163` | Sheet `Danh mục` và dòng tiêu đề 4 viết cứng, đọc cột theo cách riêng. | Dùng loader của `library.py`. |

**Phần nên giữ làm ý tưởng:** preview mặc định; staging riêng; báo "giống hệt / khác nội dung" khi đích đã có; bỏ qua khi nhiều
file cùng mã; nguyên tắc từ chối khi nhiều candidate có điểm gần nhau (`tai_tu_cong_bao.py:143`); ghi số Công báo/id vào nguồn;
từ chối bản chỉ có ảnh quét. Kết quả 31/34 văn bản trong phiếu vẫn là bằng chứng người dùng khai, chưa phải raw run của LAW.

## 6. Đề xuất xử lý: đoạn có thể đưa thẳng vào brief/HANDOFF

Claude đề xuất, Main Codex quyết và tự ghi vào HANDOFF/roadmap (Claude không sửa hai file đó).

**Bổ sung cho P3/P4 (trước khi giao):**

1. "P3 dùng cột `LAW SHA-256`/`LAW revision`/`LAW file state` đã có. Không thêm cột, không đổi schema sổ. Cảnh báo mới:
   (a) hai Mã khác nhau cùng `LAW SHA-256`; (b) 'Đã đối chiếu toàn văn' trên dòng `NEEDS_REVIEW` hoặc revision > 1: thiếu
   căn cứ binding; (c) với `--content-audit`: PDF có trang dưới ngưỡng chữ (báo số trang/tổng trang), file khai `.pdf`/OOXML
   mà nội dung không đúng định dạng. Cột binding verification là quyết định riêng ở P1, qua review schema."
2. "Thiếu PDF engine, PDF mã hóa hoặc PDF hỏng: thêm finding 'chưa kiểm lớp chữ: <lý do>'; mã thoát giữ theo kết quả kiểm cơ
   bản, không trả 2. Mã 2 vẫn chỉ dùng khi không đọc được sổ (như thiếu openpyxl hiện nay)."
3. "Engine lần giao đầu: dùng khi có, thiếu thì báo chưa kiểm; không vendored, không thêm vào requirements bắt buộc. Main ghi
   tên engine đã thử trong test. PyMuPDF (AGPL) không đóng gói; ứng viên phân phối là `pypdf` (BSD) hoặc `pdfminer.six` (MIT),
   quyết trước khi đặt vào hướng dẫn cài."
4. "Độ phủ: P3 bắt L2, L7 và một phần L1; P4 là quy tắc cho L4/L5; P1 xử lý L1/L6; P2 xử lý L3 bằng đối chiếu danh tính và
   người đọc. P3 không tuyên bố bắt L3."
5. Sửa khoảng trắng dòng 3 và dòng 7 của roadmap khi cập nhật lần tới.

**Bổ sung cho P1 (khi lập brief P1):** đưa S2, S3, S4, S10 vào acceptance; nêu đích danh `tools/transaction.py` +
`library_sync` là owner; thêm ca "luật cũ cùng chủ đề" và "`<tên chuẩn>_ban-gioi-thieu`" vào fixture từ chối.

**Bổ sung cho P2 (khi đủ điều kiện mở):** đưa S1, S5, S6, S8, S9 vào acceptance; thêm fixture "nghị định có căn cứ trích số
luật" và "tên phần Công báo không parse được".

## 4. Chưa kiểm

- Chưa đọc `library_sync.py` và `transaction.py` ngoài tên hàm. Nhận định ở 2.1 dựa trên `cmd_check` và tên cột.
- Chưa chạy hai script tham chiếu trên project hay mạng. S1/S2 chỉ chạy lại logic so khớp trên chuỗi mẫu; S3–S10 là đọc mã.
- Chưa đọc phần roadmap ngoài dòng 1–104 và mục 8.3/8.4 của `ROADMAP_HOAN_THIEN.md`. Chưa chạy test nào.
- Chưa kiểm license PyMuPDF trên bản cài cụ thể. Nhận định AGPL dựa trên giấy phép công khai của dự án, cần Main xác nhận.
