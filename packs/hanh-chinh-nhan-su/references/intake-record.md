# Hồ sơ tiếp nhận: gói hanh-chinh-nhan-su bản 0.2.0

Kết luận: **DEFER** (hoãn). Quan hệ với năng lực sẵn có: `SUPPLEMENT` (bổ sung căn cứ, mẫu và quy tắc nghiệp vụ mà native không có sẵn).
Gói tiếp tục là ứng viên (`REVIEW`): dùng thử trong project, không chép sang ứng dụng, không đưa vào bộ mẫu gốc.
Lập ngày 14/10/2026 bởi agent (Claude), chưa có người xác nhận. Hồ sơ này ghi bằng chứng đã có và phần còn thiếu; nó không phải nghiệm thu.

## Sáu điều kiện (theo `skills/README.md`)

| # | Điều kiện | Kết quả | Căn cứ |
|---|---|---|---|
| 1 | Nhu cầu và phần tăng thêm | ĐẠT MỘT PHẦN | Native không có bảng căn cứ có số hiệu và ngày đối chiếu cho lĩnh vực này. Phép thử A/B bên dưới cho thấy giá trị tăng thêm ở một số gói, không phải mọi gói. |
| 2 | Xuất xứ | CHƯA ĐỦ BẰNG CHỨNG | Bảng căn cứ lập ngày 12/10/2026 từ trang tin, tổng hợp và tư vấn (không phải văn bản chính thức); dòng chưa kiểm ghi `[cần xác nhận]`. Chưa đối chiếu toàn văn với nguồn chính thức. |
| 3 | Quyền và an toàn | ĐẠT | Kiểm máy ngày 14/10/2026: gói chỉ có `.md` và `pack.json`, không script, không dependency, không hook; URL chỉ là nguồn trích dẫn trong `legal-basis.md`; lệnh nhắc tới chỉ là công cụ có sẵn của workspace (`tools/library.py`, `tools/pack.py`). |
| 4 | Hiệu quả đã kiểm | CHƯA ĐỦ BẰNG CHỨNG | Xem phần "Phép thử A/B". Một model, một tác vụ, hai lần, tiêu chí cơ học, agent chấm; thiếu ca lỗi và ca thiếu nguồn; chưa thử trên ứng dụng agent thật. |
| 5 | Dùng được, không hại phần đã có | ĐẠT MỘT PHẦN | Id skill không trùng skill của package (`pack.py check`); ngoài phạm vi, cả hai bản chỉ trả bản dịch (10/10 và 10/10 câu): skill không chen vào việc không liên quan. Chưa thử trên ứng dụng thật. |
| 6 | Phạm vi tái dùng | CHƯA ĐỦ BẰNG CHỨNG | Quy tắc riêng đơn vị đã tách ra skill của project (theo README gói). Chưa có ba việc thật của người dùng trong lĩnh vực này, điều kiện riêng của gói dùng chung (`packs/README.md`). |

## Phép thử A/B (qwen-plus, Alibaba Model Studio, 14/10/2026)

Tiêu chí đặt trước khi chạy, chấm bằng quy tắc cơ học trên văn bản trả lời. A: cùng `AGENTS.md`, không có skill. B: A thêm SKILL.md và references của gói, ghi rõ là bản `REVIEW`.
Dữ liệu giả; không có công cụ; mỗi ô chạy 2 lần.

| Tiêu chí | A (không skill) | B (có skill) |
|---|---|---|
| Ghi chỗ chưa kiểm / cần xác nhận | 1/2 | 2/2 |
| Nêu số hiệu văn bản | 2/2 | 0/2 |
| Có khối "Khai báo thực hiện" | 2/2 | 2/2 |
| Có đoạn trình bày như trích nguyên văn (không có toàn văn trong gói) | 1/2 | 1/2 |
| Đáp án đã biết: 13 ngày (12 + 1 theo thâm niên 5 năm), Điều 113-114 BLLĐ 2019 | 0/2 | 2/2 |

Nhận xét riêng của gói: Có đáp án đã biết. Bản không có skill trả lời SAI (12 ngày, dẫn Điều 111); bản có skill đúng (13 ngày, Điều 113-114). Nhưng bản có skill đưa thêm một "văn bản hợp nhất 18/VBHN-VPQH" không có trong gói: chi tiết bịa.

## Còn thiếu để chuyển sang `ADD_MISSING_PART` (hoặc `PROJECT_ONLY`)

1. Người có thẩm quyền đối chiếu bảng căn cứ `packs/hanh-chinh-nhan-su/skills/hr-admin-vn/references/legal-basis.md` với văn bản chính thức và ghi kết quả (điều kiện 2).
2. Ít nhất ba việc thật của lĩnh vực này, chạy trên ứng dụng agent thật của người dùng, kèm đánh giá của người dùng; có ca thiếu nguồn và ca lỗi (điều kiện 4 và 6).
3. Xử lý hiện tượng B vẫn trình bày đoạn "nguyên văn" không có trong gói, hoặc chấp nhận và ghi vào giới hạn (điều kiện 4).
4. Chỉ khi 1-3 xong mới đổi `intake.decision` và nâng `intake.version` theo bản đã xét.

Giới hạn của phép thử này: một model, mỗi ô 2 lần, tiêu chí cơ học nên bỏ sót chất lượng diễn đạt; agent tự chấm không phải nghiệm thu của người dùng. Kết quả không nói gì về model khác.
