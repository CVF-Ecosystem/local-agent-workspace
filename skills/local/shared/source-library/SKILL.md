---
name: source-library
description: >-
  Gợi ý tổ chức và tra cứu thư viện nguồn của project trong `references/` (văn bản pháp luật, quy chế, nội quy, quy định nội bộ,
  mẫu biểu, tài liệu nguồn) với một chỉ mục Excel `references/_INDEX.xlsx`: đặt file, đặt tên, điền chỉ mục, kiểm tình trạng hiệu
  lực, tra trước khi trích dẫn. Kích hoạt khi người dùng nói "thư viện văn bản", "lưu văn bản pháp luật", "chỉ mục tài liệu",
  "quy chế công ty", "văn bản nào còn hiệu lực", hoặc trước khi trích dẫn một văn bản pháp luật hay quy định nội bộ.
metadata:
  version: "1.0"
---

# Thư viện nguồn của project

Mục tiêu: agent trích dẫn từ **file có thật trong thư viện**, biết văn bản còn hiệu lực hay không tính đến ngày nào, và biết
mức độ đã xác minh. Không có file thì nói rõ, không trích theo trí nhớ.

## Cấu trúc

```text
references/
  _INDEX.xlsx              chỉ mục duy nhất cho mọi nhóm (tạo bằng: python tools/library.py init)
  README.md                quy tắc chung, đặt tên
  legal/<linh-vuc>/        văn bản pháp luật bên ngoài (nhóm "Pháp luật")
  policies/<mang>/         quy chế, nội quy, quy định, quyết định nội bộ (nhóm "Nội bộ")
  templates/<mang>/        mẫu biểu đã duyệt (nhóm "Mẫu biểu")
  source-documents/        tài liệu nguồn khác (nhóm "Tài liệu nguồn")
```

Một chỉ mục chung, không mỗi thư mục một chỉ mục: tra một lần ra hết, không có hai bản lệch nhau. Thư mục lĩnh vực có thể
có README ngắn (phạm vi, người cập nhật, nguồn chính thống). Project cũ đã có thư mục nguồn ở chỗ khác thì không cần dời:
đường dẫn trong chỉ mục tính từ `references/`, có thể dùng `../` để trỏ ra ngoài; `.agent/INDEX.md` vẫn dùng cho nguồn chung.

## Đặt tên file

Không dấu, không khoảng trắng, nối bằng gạch ngang; phần mô tả sau dấu gạch dưới.
- Pháp luật: `<năm>-<số>-<ký hiệu>_<ten-ngan>.pdf`, ví dụ `2020-30-ND-CP_cong-tac-van-thu.pdf`, `2024-33-QH15_luat-luu-tru.pdf`.
- Nội bộ: `NB_<loai>-<ten-ngan>_<yyyy-mm-dd>.pdf`, ví dụ `NB_noi-quy-lao-dong_2025-01-15.pdf`.
- Mẫu biểu: `MB_<ten-ngan>.<đuôi>`. Bản sửa đổi giữ bản cũ, thêm ngày vào tên; không ghi đè.

## Chỉ mục `_INDEX.xlsx`

Sheet "Danh mục" (công cụ và agent chỉ đọc sheet này), "Ví dụ" (cách điền, không phải dữ liệu), "Tổng hợp" (đếm bằng công
thức), "Danh sách" (giá trị thả xuống). Cột chính: Mã, Nhóm, Lĩnh vực, Cơ quan ban hành, Số ký hiệu, Loại, Ngày ban hành,
Ngày có hiệu lực, Trích yếu, Thay thế, Bị thay thế bởi (từ ngày), Tình trạng, **Ngày kiểm tình trạng**, **Mức độ xác minh**,
**Có toàn văn**, **Đường dẫn file**, Điều hay dùng, **Mức nhạy cảm**, Gói/skill dùng, Nguồn tra cứu, Ghi chú.

Mức độ xác minh: "Đã đối chiếu toàn văn" (đã đọc chính file trong thư viện) > "Đã xác minh nguồn chính thống" > "Theo bản
tóm tắt" > "Cần đối chiếu". Không nâng mức khi chưa làm đúng việc đó.

## Trước khi trích dẫn (bắt buộc với văn bản pháp luật, quy định nội bộ)

1. `python tools/library.py find "<số hiệu hoặc từ khóa>"` (hoặc mở chỉ mục).
2. Có toàn văn: mở file, trích nguyên văn kèm điều, khoản; ghi "theo bản trong thư viện, kiểm tình trạng ngày ...".
3. Không có toàn văn: chỉ nêu nội dung theo nguồn ghi trong chỉ mục, ghi "[chưa đối chiếu toàn văn]"; không đặt trong ngoặc kép.
4. Không có trong chỉ mục: tra nguồn chính thống (gói `phap-ly` nếu đã cài), báo người dùng và đề xuất thêm dòng.
5. Ngày kiểm tình trạng quá 6 tháng: nói rõ, tra lại trước khi dùng cho văn bản gửi ra ngoài.

Bảng `legal-basis.md` trong các gói lĩnh vực là mốc tham khảo chung; khi project có chỉ mục, chỉ mục của project được ưu tiên.

## Thêm hoặc cập nhật văn bản

Đặt file đúng thư mục, đặt tên theo quy tắc, thêm một dòng vào "Danh mục", rồi `python tools/library.py check`. Văn bản bị
thay thế: không xóa dòng, đổi Tình trạng và ghi văn bản thay thế (còn cần cho vụ việc cũ). Agent chỉ ghi vào chỉ mục khi người
dùng yêu cầu; sửa bằng thư viện Excel nhưng giữ định dạng, kiểm lại bằng `check`.

## Kiểm định kỳ

`python tools/library.py check` báo: thiếu file, file chưa vào chỉ mục, trùng số hiệu, "Còn hiệu lực" nhưng đã ghi bị thay
thế, ngày kiểm quá 180 ngày, mức "Cần đối chiếu", văn bản Mật. `stats` cho số lượng theo nhóm và tình trạng.

## Dữ liệu nhạy cảm

Văn bản nội bộ, Mật: không tải lên Project đám mây hay dịch vụ ngoài; agent làm việc với file trên máy. Ghi rõ ở cột Mức nhạy cảm.
