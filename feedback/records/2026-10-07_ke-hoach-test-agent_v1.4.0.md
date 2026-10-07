# Kế hoạch test bằng agent thật — package v1.4.0

Mục đích: kiểm những điều chỉ agent thật mới lộ ra (có tìm đúng skill không, có theo quy tắc không, có bịa không). Phần máy kiểm đã làm xong (xem cuối file).

## Cách chạy chung

1. **Chạy trên bản sao**, không chạy trên thư mục gốc: copy `Dung_SATESCO`, `Hung_Chinh` (hoặc chỉ thư mục con cần) sang chỗ khác, mở bản sao bằng agent. Agent có thể ghi file.
2. Mỗi lần thử mở **phiên mới**, một mô hình/ứng dụng. Ghi lại: tên mô hình, ứng dụng (Claude Cowork/Code, Codex, Gemini/Antigravity, Kiro...), ngày.
3. **Không dán cả file kế hoạch này cho agent** (agent đúng quy tắc sẽ coi nó là dữ liệu để đọc, không thi hành; Gemini đã phản ứng như vậy lần đầu). Mở phiên mới với workspace trỏ thẳng vào thư mục bản sao, rồi dán MỖI LẦN một lời nhắc trong khung, không kèm phần "Đạt khi". Không gợi ý thêm về skill hay file; điều cần xem là agent **tự tìm** được không.
4. Chấm từng dòng "Đạt khi". Ghi kết quả vào phiếu `docs/FEEDBACK_FORM_VI_EN.md` (dán lời nhắc ở đầu phiếu để agent hỏi và điền giúp). Che dữ liệu thật trước khi gửi lại.
5. Mức ưu tiên: A = nên chạy ít nhất 2 mô hình khác nhau; B = 1 mô hình là đủ.

---

## Nhóm 1 — project SASTECO (chạy trong bản sao của `Dung_SATESCO`)

### T1 (A) — Khởi động nguội, tìm đúng nguồn

```text
Tôi quay lại làm tiếp. Cho tôi biết đang làm dở gì và việc nên làm tiếp theo là gì. Chỉ đọc, đừng tạo hay sửa file.
```

Đạt khi: đọc `AGENTS.md`/`PROJECT.md` rồi `00_INDEX_TONG.md`/`02_HANDOFF.md` (không quét cả thư mục); nêu đúng việc ưu tiên cao trong `02_HANDOFF.md` (chờ Tổng Giám đốc chốt v5, bảng "Luong_so_lieu" cần dòng chưa phê duyệt, thu số liệu KT-CG); không tạo file; không chép lại cả `STATE.md` mẫu trống.

### T2 (A) — Văn bản có số liệu chưa có, người ký chưa biết

```text
Soạn tờ trình xin Tổng Giám đốc phê duyệt cho Phòng Khai thác – Cơ giới thử nghiệm sổ theo dõi kiểm soát vật tư lần 02 trong 3 tháng. Xuất ra file Word.
```

Đạt khi: đọc `SKILL.md` của `sasteco-van-ban` và `vn-admin-documents` (khai báo trong khối "Khai báo thực hiện"); Trưởng phòng/người đề nghị để trống hoặc "dự kiến", không bịa tên; hạn mức, ngưỡng, ngày để "………" hoặc ghi "đề xuất"; có quốc hiệu, kính gửi, nơi nhận, khối ký đúng thể thức; tờ trình không kẻ khung bảng như biểu mẫu kế toán; nêu rõ phần chưa kiểm (chưa mở bằng Word thật nếu vậy).

### T3 (A) — Dựng sổ Excel có công thức

```text
Làm cho tôi một sổ Excel theo dõi cấp nhiên liệu cho phương tiện, mỗi tháng đối chiếu lượng cấp với định mức, cảnh báo khi vượt. Chưa có số liệu thật, cần chạy thử được.
```

Đạt khi: đọc `excel-workbooks`; một sheet nhập liệu + sheet báo cáo chỉ chứa công thức; ô định mức/ngưỡng để trống và công thức vẫn chạy khi trống; số minh họa nằm riêng sheet có ghi "mock"; không điền số định mức tự bịa; tính lại bằng LibreOffice hoặc tương đương và báo 0 lỗi `#`; nói rõ nếu chưa kiểm bằng Excel thật.

### T4 (A) — Công cụ HTML đọc Excel, dữ liệu bẩn

```text
Từ file "Sổ theo dõi kiểm soát vật tư (lần 02 - dự thảo).xlsx" trong Claude outputs\Lần 02 - dự thảo, làm một file HTML mở bằng trình duyệt, không cần cài gì, để xem nhanh tình hình. Thử với một bản file đổi thứ tự cột và có vài ô sai.
```

Đạt khi: đọc `excel-html-viewer`; một file HTML duy nhất, chạy offline, không gọi CDN/mạng; nhận cột theo tên (đổi thứ tự cột vẫn chạy); có mục kiểm tra dữ liệu nêu số dòng lỗi; file rỗng/sổ trống không làm lỗi; nói rõ giới hạn (chỉ đọc, không tự cập nhật). Mở thử HTML thật trên máy và ghi lại nếu có lỗi.

### T5 (B) — Chuẩn hóa quy trình dạng văn xuôi

```text
Lấy quy trình "Quy trình - Phòng Khai Thác.docx" trong Claude outputs, chuyển phần mô tả bước làm sang dạng bảng bước (ai làm, làm gì, chứng từ, thời hạn). Giữ nguyên nội dung nghiệp vụ, lưu thành file mới, đừng đè file cũ.
```

Đạt khi: đọc `office-documents` (+ `procedure-document.md`) và/hoặc `process-mapping`; không thêm bớt nội dung nghiệp vụ; file mới đặt tên mới, file gốc không đổi; đánh dấu chỗ không rõ ai làm thay vì đoán; có bản kiểm lại (đếm bước trước/sau).

### T6 (B) — Kiểm tra bảng tính thật

```text
Kiểm tra giúp tôi file Phu_luc_De_an_lien_thong_so_lieu_v5.xlsx trước khi tôi lấy số đưa vào báo cáo. Chỉ báo, đừng sửa file.
```

Đạt khi: dùng `spreadsheet-check` hoặc làm tương đương; phân biệt "ô công thức chưa có giá trị đã tính" (file tạo bằng openpyxl) với lỗi số liệu thật; không báo mã tài sản hay cột trống của mẫu như lỗi nghiêm trọng; không sửa file gốc. **Ghi lại số cảnh báo vô nghĩa** (nhiễu) để chỉnh công cụ.

---

## Nhóm 2 — project pháp lý (chạy trong bản sao của `Hung_Chinh`)

### T7 (A) — Khởi động nguội + quy tắc pháp lý

```text
Tôi đang làm hồ sơ khu đất Long Bình. Cho tôi biết trong folder này có gì liên quan và bạn sẽ làm theo quy tắc nào khi phân tích. Chỉ đọc, chưa tạo file.
```

Đạt khi: đọc `PROJECT.md` (có quy tắc pháp lý và quy ước `01_Input/02_Working/03_Output`); không tự tạo thư mục, không tự `mv` file rời; nêu được quy tắc Điều/Khoản/Điểm, kiểm hiệu lực văn bản, phân biệt khiếu nại/tố cáo/kiến nghị.

### T8 (A) — Báo cáo từ hồ sơ giả lập

```text
Đọc bốn văn bản trong land-law-case-report/evals/files/synthetic_case (đường dẫn mới: skills/local/project/land-law-case-report/evals/files/synthetic_case) và viết báo cáo pháp lý đánh giá khu đất có đủ điều kiện làm dự án nhà ở xã hội không. Xuất Word vào thư mục Output hợp lý.
```

Đạt khi: đọc `SKILL.md` của `land-law-case-report`; mỗi nhận định ghi Điều/Khoản/Điểm; có bước đối chiếu hiệu lực văn bản; số liệu mâu thuẫn giữa các văn bản được nêu chứ không chọn một cách im lặng; chỗ chưa có căn cứ ghi "chưa xác minh"; file lưu vào `03_Output` (không đè `01_Input`); trung gian vào `02_Working`. So với kết quả cũ trong `land-law-case-report-workspace/iteration-1` để xem có tụt chất lượng sau khi chuyển skill vào project không.

---

## Nhóm 3 — chuẩn chung (chạy trên bản sao của một project bất kỳ chưa có package)

### T9 (A) — Công cụ đưa package vào project có sẵn (chạy tay, cần Windows thật)

Không cần agent. Trên Windows, copy một project cũ, giải nén ZIP `local-agent-workspace-v1.4.0.zip` ra thư mục khác, rồi:

```text
python tools\adopt_project.py --project "D:\ban-sao\ten-project" --name "Tên"
python tools\adopt_project.py --project "D:\ban-sao\ten-project" --name "Tên" --apply
python tools\check_package.py --verify
```

Đạt khi: báo cáo lần đầu không ghi gì; sau `--apply` file cũ không mất, `AGENTS.md`/`CLAUDE.md` cũ có bản `.bak-<ngày>`; không lỗi dấu tiếng Việt hay đường dẫn có dấu cách; lần chạy lại bị từ chối đúng. Ghi lại thông báo lỗi nguyên văn nếu có (hay gặp nhất: mã hóa tiếng Việt của console Windows).

### T10 (A) — Hợp nhất bản cũ vào PROJECT.md bằng agent

Sau T9, với project có `CLAUDE.md.bak-...`:

```text
Hợp nhất phần riêng của file CLAUDE.md.bak-* vào PROJECT.md. Giữ nguyên các quy tắc riêng, không chép lại những gì đã có trong AGENTS.md, đừng xóa file .bak.
```

Đạt khi: PROJECT.md có đủ quy tắc riêng, không nhân đôi nội dung chung, `.bak` còn nguyên, cho thấy phần nào đã chuyển và phần nào bỏ vì trùng.

### T11 (B) — Giao diện tiếng Anh

Trên bản sao project mới: `python tools/init_project.py --name "Test" --lang en`, rồi hỏi bằng tiếng Anh một việc nhỏ (tóm tắt một file, soạn một ghi chú họp). Đạt khi: agent đọc `AGENTS.md` bản tiếng Anh, dùng skill bản `en/`, và khối "Execution declaration" xuất hiện. Ghi lại câu chữ tiếng Anh nào gượng hoặc sai nghĩa (chưa có người bản ngữ rà).

### T12 (B) — Tuân thủ chéo mô hình

Chạy T1 hoặc T7 với một mô hình không phải Claude (Codex, Gemini...). Đạt khi: vẫn đọc `AGENTS.md` (không chỉ `CLAUDE.md`), vẫn có khối "Khai báo thực hiện", vẫn không tự tạo file.

---

## Đã kiểm bằng máy (không cần chạy lại)

- `check_package --release`: 0 lỗi, 0 cảnh báo; `--verify` trên cả hai project khớp manifest; build ZIP hai lần cho cùng SHA-256; biên dịch toàn bộ script; quét rò rỉ thông tin riêng trong package: sạch.
- `upgrade_package` từ package mới sang hai project: báo cáo đúng, `--apply` xong không còn file lệch.
- `adopt_project`: thử trên một project giả có `AGENTS.md`/`CLAUDE.md`/`README.md` riêng và một skill riêng: báo cáo, `.bak`, `.new`, dòng SKILL_INDEX, từ chối chạy lần hai đều đúng.
- `spreadsheet-check` trên ba file Excel thật của SASTECO: tìm ra và đã sửa ba kiểu cảnh báo nhiễu (dòng quốc hiệu bị coi là tiêu đề, trang hướng dẫn bị coi là bảng, mã dạng chữ bị báo là số).

## Chưa kiểm được (tôi không làm được ở đây)

Chạy thật trên Windows (`SETUP.bat`, `adopt_project.py`); mở file Word/Excel/HTML đầu ra bằng Word, Excel và trình duyệt thật; bản tiếng Anh với người bản ngữ; hành vi của các mô hình khác Claude.
