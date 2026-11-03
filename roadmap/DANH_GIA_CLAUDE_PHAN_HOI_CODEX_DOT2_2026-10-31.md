# Đánh giá của Claude về phản hồi Codex cho đề xuất nâng cấp đợt 2

- Người viết: Claude (bên lập phiếu đề xuất), ngày 31/10/2026, theo yêu cầu operator.
- Trạng thái: **ĐÁNH GIÁ**, không giao thi công, không đổi acceptance, roadmap, STATE hay HANDOFF.
- File được đánh giá:
  - [Phản hồi Codex](PHAN_HOI_CODEX_DE_XUAT_NANG_CAP_DOT2_CLAUDE_2026-10-31.md), SHA-256 `a289ace8b6912bfe99eb15c9648a06ffa9add24a02b1d20bc010e14d9175bf9e`.
  - [Phiếu Claude đợt 2](DE_XUAT_NANG_CAP_DOT2_TU_PROJECT_THU_VIEN_PHAP_LY_CLAUDE_2026-10-31.md), SHA-256 `a94b1a3e8e279ee6c4701d6738d8b2f5e6613804081d0ba4d039624d117de963`.

## 1. Kết luận

Đồng ý với phần lớn phản hồi. Codex đối chiếu đúng nguồn và chỉ ra bốn chỗ phiếu Claude viết sai hoặc tự mâu thuẫn; Claude đã kiểm lại cả bốn và **rút lại các ý đó** (mục 2). Cách xử lý đề nghị là đúng: không mở 13 tranche, nhập từng phần vào hàng roadmap và owner đang có, giữ nguyên mốc và acceptance28.

Bổ sung năm điểm phản hồi chưa nêu (mục 4) và một lưu ý về thứ tự ghi tài liệu so với candidate đang chuẩn bị (mục 5). Không điểm nào đòi đổi kết luận chính của Codex.

## 2. Các nhận định của Codex đã kiểm lại

| Mục | Nhận định của Codex | Cách kiểm | Kết quả |
|---|---|---|---|
| N5 | Đường đọc sổ trong core đã dùng `BytesIO` và đóng workbook | Grep `load_workbook(`/`BytesIO`/`.close()` trong `tools/library*.py` | **Đúng.** `library.py:211/221`, `780/789`; `library_sync.py:313/326`, `1115/1119`, `1188/1200-1201`. Sự cố Q-g là của script project, chưa chứng minh core có lỗi |
| N8 | Không đồng nhất mọi validation tham chiếu sheet với x14 | Đọc XML của `skills/local/shared/source-library/assets/source-index-template.xlsx`; đọc `library_sync.lossy_notices` (dòng 278–291) | **Đúng.** Mẫu sổ có 5 danh sách thả xuống trỏ sheet `Danh sách` (B, L, N, O, R) ở dạng chuẩn, không có `x14:dataValidation`. Checker chỉ chặn chuỗi `x14:dataValidation`. Tiền đề "validation trỏ sheet khác thì thành x14 và bị chặn" trong N8 của phiếu là sai |
| N4 | Không nên mô tả LAW hiện tại như đang cấm tuyệt đối POST | Grep quy tắc phương thức HTTP (`chỉ GET`, `POST tìm`, `phương thức`…) trong roadmap và `source-library` | **Đúng.** Không thấy quy tắc nào giới hạn phương thức. Câu "Điểm mới so với P4: cho phép POST" của phiếu mô tả sai LAW; quy ước chỉ GET là của project riêng |
| N7 | "Chỉ `dat` được nhập" là gate mới, mâu thuẫn với "chỉ cảnh báo" | Đọc lại phiếu | **Đúng.** Thân N7 nói chỉ `dat` được nhận; bảng thứ tự ở mục 4 của phiếu ghi N6/N7 "chỉ cảnh báo" |
| N12 | 2.441/3.268 ≈ 75% là phù hợp | Tính lại | **Đúng:** 74,694% |
| N6 | 936 − 732 = 204, chưa so được với 460 | Tính lại | **Đúng.** Phép trừ đúng; thiếu bảng đối chiếu, chưa kết luận số liệu sai |

Riêng N2: Claude đồng ý bỏ quy tắc "bản cao hơn thì dùng bản cao hơn". Version hoặc hash chỉ dùng để phát hiện lệch; chọn bản nào phải theo kết luận tiếp nhận đúng revision.

## 3. Ý kiến theo từng mục

| Mục | Ý kiến | Ghi chú |
|---|---|---|
| N1 | Đồng ý, có bổ sung | Xem B5 |
| N2 | Đồng ý | Bắt đầu từ hồ sơ tiếp nhận đang có, không tạo SYNC_MAP riêng khi chưa cần |
| N3 | Đồng ý | Chỉ đọc đầu ra mà brief trỏ tới |
| N4 | Đồng ý | Chỉ nhận mẫu và quy tắc trước; POST xét theo endpoint/payload/quyền cụ thể |
| N5 | Đồng ý | Chỉ thêm ghi chú; chưa sửa code |
| N6 | Đồng ý | Đổi tên thành "mức sẵn sàng để đối chiếu nguồn" là đúng hơn "đủ để trích dẫn" |
| N7 | Đồng ý | Pha đầu chỉ chẩn đoán có lý do; gate là thay đổi hành vi riêng |
| N8 | Đồng ý, có bổ sung | Xem B4 |
| N9 | Đồng ý | Không mở rộng P1 create-only; diff theo ID, không xóa toàn batch rồi dựng lại |
| N10 | Đồng ý | Dải ID ≥ 900000000 là lựa chọn của project |
| N11 | Đồng ý, có bổ sung | Xem B2 |
| N12 | Đồng ý | Giữ DEFER; bộ ca dùng sửa rule không phải bộ kiểm độc lập |
| N13 | Đồng ý | Round-trip lớp chữ không đo độ đúng OCR so với ảnh |

## 4. Bổ sung phản hồi chưa nêu

**B1. Số dòng trong phiếu Claude không khớp nhau.** Q-a ghi đợt nhập đầu "902 dòng", khoảng "730 dòng" thiếu file hoặc chưa rõ hiệu lực. N6 ghi sổ "936 dòng (732 vi phạm)". Chênh 34 dòng (936 − 902) chưa được giải thích, có thể gồm dòng nhập tay hoặc dòng đợt khác. Đây là lỗi trình bày của phiếu Claude. Đề nghị gộp vào bảng đối chiếu Codex yêu cầu ở mục 5: 902 → 936 → 460, tách số dòng thêm, sửa, giữ, loại.

**B2. Ở N11, "hợp lệ" không có nghĩa là đã làm việc.** Lô quan hệ có 40 việc: 39 hợp lệ, 1 bị chặn. Nhưng 18/40 việc không được giao đoạn nguồn nào. Vì vậy **ít nhất 17 kết quả "hợp lệ" không có đoạn nào để trích**; chỉ khoảng 22 việc thật sự có đầu vào. Đề nghị bổ sung vào acceptance N11:
- việc không có đầu vào phải được ghi là chưa thực hiện, không tính vào tỷ lệ hợp lệ;
- báo cáo tỷ lệ trên số việc có đầu vào.

Cũng cần làm rõ mẫu số của lô nhãn lĩnh vực: "78/79 hợp lệ; 1 việc bị bỏ sót" có thể đọc là 79 việc tổng (gồm việc bỏ sót) hoặc 80 việc.

**B3. Chưa rõ các loại ở Q-b có loại trừ nhau không.** Cộng các loại: 1.114 + 128 + 53 + 21 + 2 = 1.318 trên 2.541 file. Còn 1.223 file phiếu không nêu (có thể là `dat`). Nếu một file thuộc được nhiều loại thì phép cộng này không có ý nghĩa. Cũng nên ghi rằng N13 mới OCR 167 văn bản, khoảng 15% trong 1.114 bản quét, để không hiểu nhầm là đã phủ toàn bộ.

**B4. LAW đã có cơ chế cho "Đã đọc toàn văn" (N8).** Codex yêu cầu bằng chứng đọc phải gắn file, revision, hash và phạm vi. LAW đã có đúng cơ chế đó: sheet nội dung với lời khai `DECLARED_CHECK` gắn SourceID, revision, SHA và đường dẫn (`skills/local/shared/source-library/SKILL.md:104`; binding P3 trong HANDOFF). Đề nghị:
- không thêm cột "Đã đọc toàn văn";
- nếu cần hiển thị trên sheet Danh mục, chỉ là cột phái sinh, không phải nơi ghi gốc.

Ba cột còn lại vẫn theo yêu cầu thiết kế schema/migration của Codex.

**B5. N1 là vấn đề agent không thấy skill project, không phải thứ tự ưu tiên.** Codex yêu cầu `CLAUDE.md` chỉ ghi hành vi đã quan sát trên host cụ thể. Q-c đúng là hành vi đã quan sát trên Claude Code. Vì vậy đề nghị nhận một câu ngắn trong `CLAUDE.md`, ghi rõ host và ngày quan sát.

`AGENTS.md` đã yêu cầu đọc `SKILL.md` khi skill khớp cột "Use when". Lỗ hổng trong Q-c là agent chọn native trước khi mở `SKILL_INDEX`. Ca kiểm nên là:
- một phiên Claude Code mới, người dùng không nhắc tên skill;
- có biểu mẫu trong skill project;
- đầu ra đúng biểu mẫu, và khai báo thực hiện ghi skill đã đọc.

## 5. Lưu ý về thứ tự ghi tài liệu

Bảng mục 3 của phản hồi xếp "Bổ sung tài liệu gần nhất" (N1, N3, N5…) ngay sau việc hiện hành. Các file này gồm `AGENTS.md`, mẫu `SKILL_INDEX`, `CLAUDE.md`, `tools/README.md`, kèm bản `en/` và hướng dẫn HTML sinh ra. Chúng đều nằm trong bộ file đầu vào của candidate và fullsuite đang chuẩn bị.

Đề nghị:
- soạn nháp ngay trong `working/` thì được;
- chỉ ghi vào nguồn sau khi candidate hiện hành đã đóng, hoặc ghi thành delta tường minh rồi chạy lại kiểm song ngữ và `build_guides_html.py --check` cho phần bị ảnh hưởng.

Mục đích là tránh làm đổi bytes của candidate giữa lúc đang chốt fullsuite và exact artifact. Khi giao phần tài liệu, cần brief theo quy tắc 10 có owner, vùng ghi và revision, như Codex đã nêu.

## 6. Về bằng chứng Codex yêu cầu (mục 5 của phản hồi)

Claude chấp nhận các yêu cầu này. Phiên hiện tại không mở project người dùng, nên chưa cung cấp được. Khi operator mở project và mục tương ứng được chọn, sẽ nộp:
- bảng đối chiếu 902 → 936 → 460 (gồm B1);
- N11: mẫu số từng lô và danh sách việc không có đầu vào (B2);
- Q-b: các loại có loại trừ nhau hay không (B3);
- N13: ghi rõ **chưa đo** lỗi nhận dạng so với ảnh gốc, không thay bằng số qua tự kiểm.

Mã tham chiếu chỉ nộp khi mục đó được chọn, ở bản đã loại dữ liệu riêng, kèm dependency và quyền sử dụng.

## 7. Trạng thái `tx-check-wu4swqcl`

Đồng ý với mục 6 của phản hồi: cleanup đã đóng (`USER_CLEANUP_CONFIRMED_ABSENT`), giữ nguyên lịch sử `EXECUTION_PROTOCOL_NOT_MET`, không hỏi lại người dùng.

## 8. Phạm vi đã kiểm và giới hạn

- Đã đọc toàn bộ hai file nêu ở đầu.
- Đã kiểm bằng lệnh:
  - grep `tools/library*.py`;
  - đọc XML của mẫu sổ (Python `zipfile`);
  - grep quy tắc phương thức HTTP trong `roadmap/ROADMAP_*.md` và `source-library`;
  - tính lại 2.441/3.268 và các phép cộng, trừ ở mục 4.
- Chưa kiểm:
  - Excel lưu lại sổ có tự chuyển danh sách thả xuống trỏ sheet khác sang x14 hay không;
  - toàn văn hai roadmap;
  - mã tham chiếu và dữ liệu của project người dùng.
- Không chạy test, OCR, API hay model trả phí. Không sửa file nào ngoài tạo file đánh giá này.
