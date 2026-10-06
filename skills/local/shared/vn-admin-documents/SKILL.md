---
name: vn-admin-documents
description: >-
  Gợi ý soạn văn bản hành chính tiếng Việt đúng thể thức (công văn, tờ trình, báo cáo, thông báo,
  biên bản, quyết định): các thành phần thể thức, cách ghi số và ký hiệu, địa danh, ngày tháng, trích
  yếu, nơi nhận, và thông số trình bày thường gặp. Dùng khi đơn vị áp dụng thể thức theo quy định về
  công tác văn thư hoặc theo quy chế văn thư riêng; không thay thế quy định hiện hành hay ý kiến pháp chế.
  Kích hoạt khi người dùng nói: “soạn công văn”, “soạn tờ trình”, “đúng thể thức văn bản”, “số và ký hiệu”, “nơi nhận”.
metadata:
  version: "1.0"
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
3. Khung trong `references/document-frames.md` chỉ là điểm xuất phát, không phải mẫu đã được duyệt.

## Các thành phần thể thức

| Thành phần | Cách ghi |
|---|---|
| Quốc hiệu và tiêu ngữ | Hai dòng đầu bên phải; chỉ dùng với văn bản của cơ quan, tổ chức áp dụng thể thức nhà nước. |
| Tên cơ quan, tổ chức ban hành | Bên trái; ghi tên cơ quan chủ quản (nếu có) và tên đơn vị ban hành, theo đúng tên chính thức. |
| Số và ký hiệu | `Số: [số]/[ký hiệu loại văn bản]-[chữ viết tắt đơn vị]`. Công văn: `Số: [số]/[viết tắt đơn vị]-[viết tắt bộ phận soạn]`. Số do văn thư cấp: **không tự đặt**, ghi `[số]`. |
| Địa danh, thời gian | `[Địa danh], ngày [dd] tháng [mm] năm [yyyy]`; ngày nhỏ hơn 10 và tháng 1, 2 ghi thêm số 0. Ngày để trống khi chưa ban hành. |
| Tên loại và trích yếu | Văn bản có tên loại: tên loại in hoa, dưới là trích yếu. Công văn không có tên loại: `V/v [trích yếu]`. Trích yếu nêu đúng một ý chính, ngắn. |
| Nội dung | Căn cứ, nội dung, đề nghị hoặc kiến nghị; bố cục theo loại văn bản. |
| Chức vụ, họ tên, chữ ký | Do người có thẩm quyền ký; ghi thẩm quyền ký (TM., KT., TL.) theo thực tế. **Không tự điền** tên, chức vụ hay thẩm quyền. |
| Nơi nhận | Danh sách cơ quan, cá nhân nhận và "Lưu: VT" (hoặc theo quy chế); chỉ ghi nơi người dùng nêu. |

Ký hiệu loại văn bản thường gặp: BC (báo cáo), TTr (tờ trình), TB (thông báo), QĐ (quyết định),
KH (kế hoạch), BB (biên bản), HD (hướng dẫn). Đối chiếu với bảng ký hiệu trong quy định/quy chế áp dụng.

## Trình bày (thông số thường gặp)

Khổ A4, phông chữ tiếng Việt Unicode (thường Times New Roman), cỡ chữ nội dung 13 đến 14. Lề thường:
trên và dưới khoảng 20 đến 25 mm, trái khoảng 30 đến 35 mm, phải khoảng 15 đến 20 mm. Đây là mức phổ
biến theo phụ lục thể thức; đối chiếu bản hiện hành hoặc quy chế đơn vị trước khi in ban hành.

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
