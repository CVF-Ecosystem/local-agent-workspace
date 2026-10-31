---
name: internal-accounting-vn
description: Dùng lập, kiểm chứng từ nội bộ, căn cứ có ngày; không thay hạch toán, báo cáo tài chính, tư vấn thuế. / Internal vouchers with dated legal checks; not bookkeeping, financial statements or tax advice.
metadata:
  version: "0.2"
---

# Kế toán nội bộ

Dùng cho chứng từ và kiểm tra ở phía bộ phận nghiệp vụ và kế toán: lập đề nghị, kiểm hồ sơ thanh toán, đối chiếu công nợ, lưu
trữ. Không thay việc hạch toán, lập báo cáo tài chính hay tư vấn thuế. Quy chế tài chính, quy chế chi tiêu nội bộ, hạn mức phê
duyệt của đơn vị để trong skill riêng của project và đứng trước skill này. Sổ, bảng kê bằng Excel: `excel-workbooks`.

Mọi điều kiện, ngưỡng, thời hạn lấy từ `references/legal-basis.md`, ghi số hiệu và ngày đối chiếu; quá 6 tháng thì tra lại.

## Chế độ áp dụng

Từ năm tài chính bắt đầu 01/01/2026, doanh nghiệp đang theo Thông tư 200/2014/TT-BTC chuyển sang Thông tư 99/2025/TT-BTC; doanh
nghiệp nhỏ và vừa vẫn có thể theo Thông tư 133/2016/TT-BTC; đơn vị hành chính, sự nghiệp theo chế độ riêng. Hỏi đơn vị đang
theo chế độ nào trước khi dùng mẫu. Theo Thông tư 99/2025, doanh nghiệp được tự thiết kế mẫu chứng từ, sổ nhưng phải có quy chế
hạch toán kế toán ghi rõ; vì vậy dùng mẫu trong quy chế của đơn vị nếu có.

## Nội dung tối thiểu của chứng từ (Luật Kế toán 2015, Điều 16)

Tên và số hiệu chứng từ; ngày, tháng, năm lập; tên, địa chỉ của đơn vị hoặc người lập, người nhận; nội dung nghiệp vụ; số lượng,
đơn giá, số tiền bằng số và bằng chữ; chữ ký, họ tên người lập, người duyệt và những người liên quan. Ký chứng từ theo Điều 19.

## Mẫu nội bộ gợi ý (khung, thay bằng mẫu của đơn vị)

- **Đề nghị tạm ứng**: người đề nghị, bộ phận; số tiền (số và chữ); lý do, công việc; thời hạn hoàn ứng; hình thức nhận (chuyển
  khoản ưu tiên); ký: người đề nghị, trưởng bộ phận, kế toán, người duyệt.
- **Đề nghị thanh toán**: nội dung; số tiền; chứng từ kèm theo (hóa đơn, hợp đồng, biên bản nghiệm thu, bảng kê); người hưởng và
  tài khoản; đã tạm ứng bao nhiêu; ký như trên.
- **Hoàn ứng (thanh toán tạm ứng)**: số đã tạm ứng; số đã chi theo chứng từ; chênh lệch nộp lại hoặc chi thêm.
- **Biên bản đối chiếu công nợ**: hai bên, thời điểm chốt số; số dư đầu kỳ, phát sinh tăng, giảm, số dư cuối kỳ theo từng bên;
  chênh lệch và nguyên nhân; xác nhận của hai bên.

## Kiểm hồ sơ trước khi trình ký

1. Đủ chữ ký theo hạn mức phê duyệt của quy chế đơn vị.
2. Hóa đơn: đủ nội dung theo Nghị định 123/2020/NĐ-CP đã sửa bởi Nghị định 70/2025/NĐ-CP; thông tin người mua đúng; tra cứu hóa đơn
   điện tử trên hệ thống của cơ quan thuế.
3. Khấu trừ thuế giá trị gia tăng đầu vào: hàng hóa, dịch vụ từ 5 triệu đồng trở lên (giá đã có thuế) phải có chứng từ thanh
   toán không dùng tiền mặt (Luật Thuế GTGT 48/2024/QH15; Nghị định 181/2025/NĐ-CP). Nhiều lần mua trong ngày của cùng người bán
   cộng lại để xét ngưỡng.
4. Số tiền bằng số và bằng chữ khớp; tổng bảng kê khớp chứng từ gốc; không tẩy xóa.
5. Thiếu chứng từ hoặc lệch số: ghi rõ dòng nào, lệch bao nhiêu; không tự sửa số trên chứng từ của người khác.

## Lưu trữ tài liệu kế toán (Luật Kế toán, Điều 41; Nghị định 174/2016/NĐ-CP, Điều 12 - 15)

Tối thiểu 5 năm: tài liệu không dùng trực tiếp để ghi sổ (ví dụ phiếu thu, phiếu chi không lưu kèm sổ). Tối thiểu 10 năm: chứng
từ dùng trực tiếp ghi sổ, sổ kế toán, báo cáo tài chính. Vĩnh viễn: tài liệu có tính sử liệu, ý nghĩa đặc biệt (người đứng đầu
quyết định). Thời điểm tính: từ khi kết thúc kỳ kế toán năm hoặc theo Điều 15. Khi dựng danh mục hồ sơ kế toán: dùng mẫu của gói
`van-thu-luu-tru` nếu đã cài.

## Thư viện nguồn của project

Project có `references/_INDEX.xlsx` thì tra ở đó trước (`python tools/library.py find <số hiệu hoặc từ khóa>`): có toàn văn thì
đọc file và trích nguyên văn; không có thì ghi "[chưa đối chiếu toàn văn]". Chỉ mục của project đứng trước bảng
`references/legal-basis.md` của gói (bảng của gói là mốc tham khảo chung). Văn bản dùng thường xuyên mà chưa có trong thư viện:
đề xuất người dùng tải bản chính thống về và thêm dòng chỉ mục (skill `source-library`).

## Kiểm trước khi giao

- Chế độ kế toán đơn vị áp dụng đã xác định; mẫu chứng từ khớp quy chế.
- Mỗi ngưỡng, thời hạn có số hiệu văn bản và ngày đối chiếu.
- Bảng kê, đối chiếu có tổng kiểm tra bằng công thức, kiểm cả từng dòng.
