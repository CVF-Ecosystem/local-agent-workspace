---
name: vn-admin-documents
description: >-
  Soạn hoặc rà soát thể thức văn bản hành chính tiếng Việt (công văn, tờ trình, báo cáo,
  thông báo, biên bản, quyết định) theo quy chế của đơn vị hoặc quy định nhà nước mà đơn
  vị áp dụng. Dùng khi cần trình ký hoặc gửi chính thức; không thay thế việc kiểm tra quy
  định hiện hành hay ý kiến pháp chế. Kích hoạt khi người dùng nói: “soạn công văn”, “soạn
  tờ trình”, “đúng thể thức văn bản”, “số và ký hiệu”, “nơi nhận”.
metadata:
  version: "1.2"
---

# Văn bản hành chính đúng thể thức

Dùng khi người dùng cần một văn bản có thể thức chính thức (gửi cơ quan khác, trình ký, ban hành nội
bộ). Việc nội dung ngắn không cần thể thức thì dùng `internal-comms` hoặc `office-documents`.

## Thứ tự căn cứ

1. **Quy chế văn thư, mẫu văn bản của chính đơn vị** (nếu người dùng có): dùng trước, vì doanh nghiệp
   và đơn vị thường có quy định riêng.
2. **Quy định nhà nước về công tác văn thư** mà đơn vị áp dụng. Căn cứ phổ biến là Nghị định
   30/2020/NĐ-CP (phần thể thức và kỹ thuật trình bày ở phụ lục). Đã đối chiếu ngày 06/10/2026: nghị định này vẫn hiện hành, thông số trình bày dưới đây khớp phụ lục.
   Quy định có thể được sửa đổi hoặc thay thế sau đó: trước khi ban hành, kiểm bản hiện hành hoặc nói rõ chưa kiểm. Không tự khẳng định đơn
   vị bắt buộc phải theo quy định nào; hỏi hoặc ghi "cần xác nhận".
3. Khung trong `references/document-frames.md` (công văn, tờ trình, báo cáo, thông báo, kế hoạch, quyết định, giấy mời, biên bản họp)
   chỉ là điểm xuất phát, không phải mẫu đã được duyệt.

## Các thành phần thể thức

| Thành phần | Cách ghi |
|---|---|
| Quốc hiệu và tiêu ngữ | Hai dòng đầu bên phải; chỉ dùng với văn bản của cơ quan, tổ chức áp dụng thể thức nhà nước. |
| Tên cơ quan, tổ chức ban hành | Bên trái; ghi tên cơ quan chủ quản (nếu có) và tên đơn vị ban hành, theo đúng tên chính thức. |
| Số và ký hiệu | `Số: [số]/[ký hiệu loại văn bản]-[chữ viết tắt đơn vị]`. Công văn: `Số: [số]/[viết tắt đơn vị]-[viết tắt bộ phận soạn]`. Số do văn thư cấp: **không tự đặt**, ghi `[số]`. |
| Địa danh, thời gian | `[Địa danh], ngày [dd] tháng [mm] năm [yyyy]`; ngày nhỏ hơn 10 và tháng 1, 2 ghi thêm số 0. Ngày để trống khi chưa ban hành. |
| Tên loại và trích yếu | Văn bản có tên loại: tên loại in hoa, dưới là trích yếu. Công văn không có tên loại: `V/v [trích yếu]`. Trích yếu nêu đúng một ý chính, ngắn. |
| Nội dung | Căn cứ, nội dung, đề nghị hoặc kiến nghị; bố cục theo loại văn bản. |
| Chức vụ, họ tên, chữ ký | Do người có thẩm quyền ký; ghi thẩm quyền ký (TM., Q., KT., TL., TUQ.) theo thực tế. **Không tự điền** tên, chức vụ hay thẩm quyền. |
| Nơi nhận | Danh sách cơ quan, cá nhân nhận và "Lưu: VT" (hoặc theo quy chế); chỉ ghi nơi người dùng nêu. |

Ký hiệu loại văn bản thường gặp: BC (báo cáo), TTr (tờ trình), TB (thông báo), QĐ (quyết định),
KH (kế hoạch), BB (biên bản), HD (hướng dẫn), GM (giấy mời). Đối chiếu với bảng ký hiệu trong quy định/quy chế áp dụng.

## Trình bày (thông số thường gặp)

Khổ A4; phông Times New Roman (Unicode TCVN 6909:2001), màu đen; nội dung cỡ 13 đến 14, canh đều hai lề, đầu dòng lùi 1 cm
hoặc 1,27 cm, cách đoạn tối thiểu 6pt, cách dòng từ dòng đơn đến 1,5 lines. Lề trên và dưới 20 đến 25 mm, trái 30 đến 35 mm,
phải 15 đến 20 mm. Số trang ở giữa lề trên, không hiện ở trang đầu. Cỡ chữ, kiểu chữ của từng thành phần (quốc hiệu, tên cơ
quan, trích yếu, căn cứ, điều khoản, khối ký, nơi nhận...) và danh sách mẫu trong phụ lục: `references/nd30-presentation.md`
(đã đối chiếu với bản quét Nghị định 30/2020/NĐ-CP ngày 12/10/2026). Đối chiếu bản hiện hành hoặc quy chế đơn vị trước khi
in ban hành.

Khi dựng file Word: phần đầu (tên cơ quan bên trái, quốc hiệu bên phải) và khối ký dùng bảng hai cột không viền. Công văn và tờ trình theo thể thức nhà nước không dùng bảng kẻ khung cho nội dung; chứng từ kế toán và biểu mẫu theo mẫu số hiệu riêng thường có bảng viền. Tra mẫu số hiệu và văn bản hiện hành (kể cả còn hiệu lực hay đã bị thay thế) trước khi chọn; xem `office-documents` (`references/form-standardization.md`).

## Cách làm

1. Xác định loại văn bản, người ký, nơi nhận, đơn vị ban hành và căn cứ. Hỏi gộp một lần nếu thiếu.
2. Soạn theo khung, giữ đúng dữ kiện người dùng cung cấp. Số liệu, tên, thời hạn, thẩm quyền, số văn
   bản căn cứ không có trong nguồn thì ghi `[cần xác nhận]`; không tạo số hiệu, ngày hay tên người ký.
3. Văn phong: câu ngắn, thuật ngữ nhất quán, tránh khẩu ngữ; nêu rõ đề nghị hoặc kiến nghị cuối văn bản.
4. Giao bản nháp trong hội thoại. Chỉ tạo file Word khi được yêu cầu, bằng công cụ định dạng phù hợp.

## Mức thận trọng cao khi ban hành

Văn bản gửi ra ngoài hoặc trình ký thuộc "Mức thận trọng cao" trong `AGENTS.md`: đối chiếu từng số,
ngày, tên, tên cơ quan, số và ngày của văn bản căn cứ với nguồn; nêu rõ phần chưa đối chiếu được.
Nhận định pháp lý trong văn bản chỉ là gợi ý để người có thẩm quyền xác nhận.

## Dựng và kiểm Word trong workspace

Có thể dùng native/mẫu đơn vị hoặc helper Word của `office-documents` (xem mục Công cụ Word bổ sung).
`new_nd30_document()` và renderer HTML là tùy chọn chỉ trong workspace LAW; helper generic export
độc lập không tự cung cấp đầy đủ cấu hình ND30. Renderer chỉ nhận chữ/bảng đơn giản, từ chối ảnh,
bảng lồng và span không hỗ trợ trước ghi; không ghi đè mặc định.

Chạy `python tools/check_output.py FILE.docx --profile nd30` khi cần ép kiểm mẫu hành chính. `auto`
nhận qua Quốc hiệu; `none` bỏ kiểm bố cục khi dùng mẫu khác. Đây là kiểm cơ học section cuối và
phông/cỡ chủ đạo, không thay đối chiếu từng thành phần, mở/render xem từng trang hoặc kiểm văn bản
hiện hành. Kết quả ĐẠT không xác nhận pháp lý hay toàn thể thức.
