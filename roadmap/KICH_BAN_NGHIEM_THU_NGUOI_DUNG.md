# Kịch bản nghiệm thu trải nghiệm người dùng

> **Chỉ dành cho người duy trì.** Không đưa file này vào gói phát hành.
>
> **Trạng thái: chưa có phiên thử nào với người dùng mới thật sự diễn ra.** Đây là bộ hướng dẫn để chuẩn bị và
> ghi kết quả khi có người thử. Mọi nhận định về trải nghiệm người mới hiện chỉ là giả định cho đến khi có bản ghi thật.

Phần kỹ thuật (bàn phím, tương phản, màn hình hẹp, trạng thái đang chạy, thông báo lỗi) đã được kiểm bằng kiểm thử
tự động trong `tests/test_ui_browser.py`. Phiên thử này kiểm lại những điều đó với một người thật.

## 1. Mục tiêu

Theo `roadmap/ROADMAP_HOAN_THIEN.md`, Giai đoạn 13, người mới phải làm được ba nhiệm vụ:

1. tạo project;
2. kiểm một file trước khi giao;
3. xử lý một lần nâng cấp có xung đột.

Phiên thử đo việc người mới làm được gì khi chỉ có nội dung của ứng dụng, không có hướng dẫn miệng.

## 2. Chuẩn bị (trước phiên, do người duy trì làm)

### 2.1 Thiết bị và bản thử

- Thử trên Windows bằng `APP.bat`. macOS (`APP.command`) và Python 3.8 **chưa thử**; ghi điều này vào bản ghi.
- Dùng **bản ZIP phát hành** hoặc thư mục đã dựng sạch từ bản ZIP, không dùng kho nguồn. Kho nguồn có roadmap,
  tests và feedback mà người dùng thật không có.
- Ghi số trong file `VERSION` của bản thử vào bản ghi. Kết quả chỉ có giá trị với đúng phiên bản đó.

### 2.2 Dữ liệu giả (chỉ dùng dữ liệu này)

Tạo thư mục làm việc `Desktop\KTND-01\` với ba thư mục con:

| Thư mục | Nội dung |
|---|---|
| `goi\` | Giải nén bản ZIP phát hành vào đây. Thư mục này là nơi tạo project ở nhiệm vụ 1 và là project được nâng cấp ở nhiệm vụ 3. |
| `du-lieu-gia\` | Một file `bien-ban-thu.txt` với nội dung đúng như sau (dòng đầu tiên là một dòng riêng): |
| `goi-moi\` | Bản "gói mới" để nâng cấp (xem 2.3). |

Nội dung `bien-ban-thu.txt`:

```text
Biên bản thử nghiệm (dữ liệu giả)
Kính gửi [Tên khách hàng],
Tổng tiền: 1.250.000 đ.
```

Dòng `[Tên khách hàng]` là cố ý: ứng dụng phải báo file còn chỗ chưa điền.

### 2.3 Tạo bản "gói mới" cho nhiệm vụ 3

Nếu chưa có bản ZIP phát hành mới hơn, người duy trì tạo bản thử như sau:

1. Giải nén lại bản ZIP phát hành vào `goi-moi\`. Không sao chép từ `goi\` vì thư mục đó sẽ đã là project.
2. Trong `goi-moi\`, mở `.agent\README.md` và thêm một dòng cuối:
   `Dòng mới từ gói phát hành (dữ liệu giả).`
3. Trong `goi-moi\`, chạy: `python tools\check_package.py --write-manifest`
   (lệnh này ghi lại MANIFEST cho bản mới).

### 2.4 Chuẩn bị ngay trước nhiệm vụ 3 (người thử không được biết)

Sau khi người thử hoàn thành nhiệm vụ 1, người quan sát mở `goi\.agent\README.md` và thêm vào cuối một dòng:
`Ghi chú của người thử: dòng này do tôi tự viết (dữ liệu giả).`

Dòng này tạo xung đột: cả project lẫn gói mới đều đã đổi file đó.

## 3. Thẻ nhiệm vụ (đọc nguyên văn, không thêm gì)

- **Nhiệm vụ 1.** Thư mục đang mở chưa là project. Hãy tạo project cho nó: tên là `Du an thu 01`, mục đích là
  `Báo cáo nội bộ mẫu, dữ liệu giả`. Nhiệm vụ xong khi ứng dụng cho thấy project có tên đó.
- **Nhiệm vụ 2.** Trong thư mục `du-lieu-gia` có file `bien-ban-thu.txt`. Hãy kiểm file này trước khi giao, rồi cho
  biết file có vấn đề gì không và kết quả kiểm có đầy đủ không.
- **Nhiệm vụ 3.** Gói mới nằm trong thư mục `goi-moi`. Hãy nâng cấp project `Du an thu 01` lên gói mới. Nếu ứng dụng
  báo còn file cần xử lý, hãy xử lý cho đến khi không còn file nào chờ hợp nhất. Những gì bạn đã viết trong project
  phải còn nguyên sau khi xong.

## 4. Quy tắc cho người quan sát

### 4.1 Được làm

- Đọc thẻ nhiệm vụ đúng nguyên văn, một lần. Có thể đọc lại khi người thử hỏi.
- Hỏi mở, không đoán hộ: "Bạn đang nghĩ gì?", "Bạn định làm gì tiếp?", "Bạn hiểu dòng này thế nào?".
- Nếu ứng dụng hỏng thật (không mở được trang, cửa sổ treo), ghi lại và chỉ can thiệp để tiếp tục phiên.

### 4.2 Không được nói

- Tên nút, tên mục, vị trí ("bấm mục Khởi tạo bên trái", "nút ở góc trên").
- Nghĩa của thuật ngữ: *package*, *hợp nhất*, *giao dịch*, *xem trước*, *`.new`*, *skill*, *MANIFEST*, *phục hồi*.
  Ghi từ người thử hỏi vào mục "thuật ngữ khó hiểu" và không trả lời.
- Lời trấn an về dữ liệu ("không sao đâu, file vẫn an toàn"). Ứng dụng phải tự nói điều đó. Nếu người thử hỏi
  "có mất dữ liệu không?", ghi lại câu hỏi và hỏi lại: "Bạn đọc thấy gì trên màn hình?".
- Lời xác nhận đúng sai bằng cử chỉ hoặc lời ("đúng rồi", "gần đúng rồi").
- Gợi ý thao tác ("thử bấm Thực hiện", "thử xem trước trước").
- Đọc thông báo lỗi thay người thử. Người thử phải tự đọc.

### 4.3 Khi nào can thiệp

- Người thử bị kẹt quá 10 phút ở cùng một bước, hoặc đã nói muốn dừng: kết thúc nhiệm vụ, ghi "không hoàn thành".
- Ghi mọi lần người quan sát phải nói điều gì trái quy tắc 4.2, kèm thời điểm. Đây là một kết quả thử, không phải lỗi
  của người thử.

## 5. Ghi chép trong phiên

Dùng bảng này cho mỗi nhiệm vụ. Đồng hồ bắt đầu khi đọc xong thẻ nhiệm vụ.

| Nhiệm vụ | Bắt đầu | Hoàn thành | Thời gian | Điểm dừng (mô tả, thời điểm) | Thuật ngữ khó hiểu (nguyên văn) | Cần trợ giúp (nói gì, lúc nào) | Lỗi thấy (nguyên văn) | Kết quả |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | hoàn thành / có trợ giúp / không hoàn thành |
| 2 | | | | | | | | |
| 3 | | | | | | | | |

Quy ước:

- **Điểm dừng**: mỗi lần người thử đứng yên quá 30 giây, bấm sai, hoặc quay lại một bước.
- **Thuật ngữ khó hiểu**: ghi đúng chữ người thử đọc hoặc hỏi.
- **Lỗi thấy**: chép nguyên văn thông báo. Không chụp ảnh có tên người, số liệu hay đường dẫn thật.
- **Kết quả**: "có trợ giúp" khi người quan sát phải nói điều bị cấm ở 4.2 hoặc trả lời câu hỏi thuật ngữ.

## 6. Kiểm kỹ thuật kèm theo (người quan sát làm sau khi người thử xong)

Ghi "đạt", "chưa đạt" hoặc "chưa kiểm" cho từng dòng.

| Việc kiểm | Cách làm | Kết quả | Ghi chú |
|---|---|---|---|
| Bàn phím | Chỉ dùng Tab, Shift+Tab, Enter, Space, Esc trên mỗi trang. Mọi nút tới được và có viền rõ. | | |
| Hộp kết quả | Mở bằng Enter trên nút kiểm tra. Tab không ra khỏi hộp. Esc đóng; tiêu điểm quay về nút đã mở. | | |
| Trạng thái đang chạy | Bấm Enter trên nút xem trước; nút phải bị vô hiệu trong lúc chạy và có chữ "Đang chạy". | | |
| Màn hình hẹp | Trình duyệt ở chế độ thiết bị 390 px, rồi 360 px: không có thanh cuộn ngang trên mọi trang. | | |
| Tương phản | Hai chủ đề sáng và tối: chữ và nhãn đọc được rõ. Số tương phản do kiểm thử tự động tính (`ContrastAndWording`); người quan sát chỉ xác nhận bằng mắt. | | |
| Thông báo lỗi | Với mỗi thông báo người thử gặp: có nói điều đã xảy ra, dữ liệu có an toàn không, và bước tiếp theo không? | | |

## 7. Tiêu chí nghiệm thu (từ roadmap, Giai đoạn 13)

| Tiêu chí | Đạt khi | Cách ghi |
|---|---|---|
| C1. Người mới hoàn thành ba nhiệm vụ mà không cần hướng dẫn miệng ngoài nội dung ứng dụng. | Cả ba nhiệm vụ "hoàn thành" (không tính "có trợ giúp"). | Bảng mục 5, cột Kết quả. |
| C2. Mọi lỗi đều nói rõ điều đã xảy ra, dữ liệu có an toàn không và bước xử lý tiếp theo. | Mọi thông báo lỗi người thử gặp đủ ba phần. Thông báo thiếu phần nào thì chưa đạt và được ghi là vấn đề. | Bảng mục 6, dòng Thông báo lỗi. |
| C3. Các vấn đề nghiêm trọng từ lượt thử được sửa và kiểm lại đúng chỗ. | Mỗi vấn đề nghiêm trọng có mã, đã sửa, và đã chạy lại đúng bước gây lỗi (thử lại tay, kèm kiểm thử tự động nếu có). | Mục 8. |

**Vấn đề nghiêm trọng** là vấn đề làm người thử không hoàn thành nhiệm vụ, làm họ hiểu sai việc dữ liệu có an toàn
hay không, hoặc có thể làm mất hoặc ghi đè dữ liệu. Các điểm khác ghi là "thấp" hoặc "vừa" và xử lý theo lịch riêng.

Các mục ghi thêm (không phải tiêu chí đạt/chưa đạt): thời gian hoàn thành, điểm dừng, thuật ngữ khó hiểu, chỗ cần
trợ giúp trực tiếp, và toàn bộ mục 6.

## 8. Xử lý vấn đề sau phiên

Với mỗi vấn đề:

1. Đặt mã (ví dụ `UX-2026-10-20-01`) và mức (cao / vừa / thấp).
2. Sửa đúng chỗ (`tools/app_ui.html` cho giao diện, các công cụ khác theo nguồn của chúng).
3. Chạy lại: `PYTHONUTF8=1 python -B -m unittest discover -s tests` và thử lại đúng bước người thử đã gặp.
4. Ghi trạng thái: "đã sửa và kiểm lại", "hoãn" (kèm lý do) hoặc "không làm" (kèm lý do).

## 9. Lưu kết quả vào `feedback/records/`

1. Chép `feedback/TEMPLATE.md` thành `feedback/records/AAAA-MM-DD_nguoi-dung-NN_ung-dung-panel.md`
   (ví dụ `2026-10-20_nguoi-dung-01_ung-dung-panel.md`). Dùng số thứ tự người thử, không dùng tên thật.
2. Điền mục "Thông tin": ngày; người thử ghi **"người dùng"**; agent và ứng dụng ghi "không có (ứng dụng giao diện)";
   phiên bản lấy từ `VERSION`; thư mục mở là `Desktop\KTND-01\`; loại: "nghiệm thu trải nghiệm"; dữ liệu: "giả".
3. Mục "Yêu cầu đã gửi": ghi ba thẻ nhiệm vụ nguyên văn. Mục "Kết quả của agent": để "không áp dụng".
4. Mục "Chấm theo tiêu chí": điền C1, C2, C3 từ mục 7.
5. Mục "Vấn đề phát hiện": mỗi vấn đề một dòng theo mẫu của `TEMPLATE.md`.
6. Mục "Ghi chú thêm": giới hạn (chỉ Windows, chưa có macOS, chưa thử Python 3.8) và toàn bộ bảng mục 5 và 6.
7. Thêm một dòng vào `feedback/INDEX.md` theo đúng các cột có sẵn.

Không đưa dữ liệu thật, tên người, ảnh chụp có thông tin thật vào bản ghi. Mô tả thay thế nếu cần.

---

## English summary

Maintainer-only acceptance kit for the three roadmap tasks (create a project, check a file, handle an upgrade with a
conflict). It gives exact synthetic setup (folders, text file, a prepared "new package" with a manifest regenerated by
`tools/check_package.py --write-manifest`, and one conflicting line added just before task 3), the task cards to read
verbatim, the rules for the observer (what may and may not be said), a recording sheet (time, stop points, unclear
terms, help given, errors quoted verbatim), a keyboard, focus, contrast, narrow-screen, running-state and error-message
check, the three pass criteria from roadmap Stage 13, and how to file results into `feedback/records/` and
`feedback/INDEX.md`.

**No session with a real new user has taken place yet.** Tested so far on Windows only; macOS and Python 3.8 are untested.
