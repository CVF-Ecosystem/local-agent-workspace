---
name: hr-admin-vn
description: Gợi ý soạn, kiểm văn bản và phép tính nhân sự theo luật lao động hiện hành - quyết định nhân sự, nghỉ phép, hợp đồng, làm thêm giờ, kỷ luật, lương tối thiểu, bảo hiểm, thuế TNCN; căn cứ có ngày đối chiếu. Kích hoạt khi người dùng nói "quyết định nhân sự", "nghỉ phép năm", "làm thêm giờ", "kỷ luật lao động", "lương tối thiểu vùng", "hợp đồng lao động". / HR documents and calculations under current Vietnamese labour law. Triggers on personnel decisions, leave, overtime, discipline, minimum wage, labour contracts.
metadata:
  version: "0.2"
---

# Hành chính - nhân sự

Dùng khi soạn hoặc kiểm văn bản nhân sự và các phép tính đi kèm. Thể thức văn bản: `vn-admin-documents` (quyết định Mẫu 1.2,
giấy nghỉ phép Mẫu 1.10 của Nghị định 30/2020/NĐ-CP). Sổ theo dõi phép, chấm công bằng Excel: `excel-workbooks`. Nghiệp vụ
riêng của đơn vị (nội quy, quy chế lương, thang bảng lương, người ký) để trong skill riêng của project và đứng trước skill này.

**Căn cứ thay đổi thường xuyên** (lương tối thiểu, giảm trừ gia cảnh, mức đóng bảo hiểm, xử phạt). Mọi con số lấy từ
`references/legal-basis.md`, ghi kèm số hiệu văn bản và ngày đối chiếu; quá 6 tháng kể từ ngày đối chiếu thì tra lại trước khi
dùng. Không có trong bảng thì ghi `[cần xác nhận]`, không dùng số nhớ.

## Phép năm (Bộ luật Lao động 2019, Điều 113, 114)

- Đủ 12 tháng: 12 ngày làm việc (điều kiện bình thường); 14 ngày (người chưa thành niên, người khuyết tật, công việc nặng nhọc,
  độc hại); 16 ngày (đặc biệt nặng nhọc, độc hại). Chưa đủ 12 tháng: tính theo tỷ lệ số tháng làm việc.
- Cứ đủ 5 năm làm việc cho một người sử dụng lao động thì tăng thêm 1 ngày (Điều 114).
- Bảng tính phép: cột ngày vào làm, số tháng làm việc trong năm, phép theo luật, phép thâm niên, đã nghỉ, còn lại; công thức thật,
  không gõ tay kết quả. Quy chế đơn vị có thể có lợi hơn cho người lao động; ghi nguồn khi dùng.

## Làm thêm giờ (Điều 98, 107)

Giới hạn làm thêm và trường hợp được làm thêm đến 300 giờ một năm theo Điều 107; tiền lương làm thêm theo Điều 98 (ngày thường,
ngày nghỉ hằng tuần, ngày lễ; làm thêm ban đêm). Lấy đúng tỷ lệ từ văn bản khi tính, không viết theo trí nhớ.

## Kỷ luật lao động (Điều 118, 122 - 125; Nghị định 145/2020/NĐ-CP, Điều 70)

Trình tự: hành vi vi phạm phải có trong nội quy; chứng minh lỗi; có sự tham gia của tổ chức đại diện người lao động (nếu là thành
viên); người lao động có mặt, có quyền bào chữa; lập biên bản; trong thời hiệu. Hình thức kỷ luật theo Điều 124. Khi soạn hồ sơ:
thông báo họp, biên bản họp xử lý, quyết định kỷ luật; kiểm từng bước có chứng cứ. Trường hợp sa thải: đối chiếu Điều 125 và hỏi
pháp chế; skill chỉ hỗ trợ soạn hồ sơ.

## Hợp đồng lao động (Điều 20, 21, 24 - 25)

Loại hợp đồng (Điều 20), nội dung chủ yếu (Điều 21), thử việc (Điều 24, 25). Hợp đồng lao động điện tử: Nghị định 337/2025/NĐ-CP
(hiệu lực 01/01/2026). Checklist: đủ nội dung Điều 21; mức lương không thấp hơn lương tối thiểu vùng; thời gian thử việc trong giới
hạn; ghi đúng loại hợp đồng.

## Lương, bảo hiểm, thuế

- Lương tối thiểu vùng từ 01/01/2026: Nghị định 293/2025/NĐ-CP (mức trong bảng căn cứ). Vùng áp dụng theo địa bàn nơi làm việc
  ghi trong phụ lục của nghị định; sau sắp xếp đơn vị hành chính năm 2025 phải tra đúng tên xã, phường mới.
- Bảo hiểm xã hội: Luật 41/2024/QH15 (hiệu lực 01/07/2025), Nghị định 158/2025/NĐ-CP. Bảo hiểm thất nghiệp: Luật Việc làm
  74/2025/QH15 (hiệu lực 01/01/2026). Tỷ lệ đóng: tra văn bản, ghi rõ nguồn.
- Thuế thu nhập cá nhân: giảm trừ gia cảnh 15,5 triệu đồng/tháng bản thân, 6,2 triệu đồng/tháng mỗi người phụ thuộc từ kỳ tính
  thuế 2026 (Nghị quyết 110/2025/UBTVQH15). Luật Thuế TNCN 109/2025/QH15 hiệu lực 01/07/2026, áp dụng thu nhập từ tiền lương từ
  kỳ tính thuế 2026; biểu thuế: tra văn bản.

## Thư viện nguồn của project

Project có `references/_INDEX.xlsx` thì tra ở đó trước (`python tools/library.py find <số hiệu hoặc từ khóa>`): có toàn văn thì
đọc file và trích nguyên văn; không có thì ghi "[chưa đối chiếu toàn văn]". Chỉ mục của project đứng trước bảng
`references/legal-basis.md` của gói (bảng của gói là mốc tham khảo chung). Văn bản dùng thường xuyên mà chưa có trong thư viện:
đề xuất người dùng tải bản chính thống về và thêm dòng chỉ mục (skill `source-library`).

## Kiểm trước khi giao

- Mỗi con số pháp định có số hiệu văn bản, điều khoản và ngày đối chiếu; không quá 6 tháng hoặc đã tra lại.
- Phép tính có công thức và kiểm bằng ít nhất một trường hợp tính tay (người vào làm giữa năm, người đủ 5 năm).
- Văn bản kỷ luật, chấm dứt hợp đồng: thuộc "Mức thận trọng cao" trong `AGENTS.md`; nêu rõ cần pháp chế hoặc người có thẩm quyền xem.
