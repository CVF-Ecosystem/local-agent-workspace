---
name: port-operations-reports
description: Dùng dựng/kiểm báo cáo khai thác tàu, sà lan, năng suất, gián đoạn, sự cố; căn cứ pháp lý cần đối chiếu. Không dùng kiểm vị trí bãi. / Ship/barge operations reports; excludes yard-position checks.
metadata:
  version: "0.2"
---

# Báo cáo khai thác cảng

Rút từ việc thật ở một đội khai thác container (đã bỏ tên đơn vị, mã thiết bị, số liệu). Quy tắc riêng của đơn vị (mã thiết bị,
danh sách cầu bến, người ký, mẫu đã duyệt) để trong skill riêng của project; skill riêng đứng trước skill này.
Dựng sổ Excel: `excel-workbooks`; dashboard HTML đọc Excel: `excel-html-viewer` và `html-reports`.

## Phạm vi

Dùng cho báo cáo khai thác tàu/sà lan, năng suất, chờ cầu, gián đoạn và sự cố thiết bị. Các ghi chú căn cứ hàng hải, hải quan và an toàn là tài liệu tham khảo cần đối chiếu với nguồn chính thức trước khi dùng làm căn cứ; không dùng skill này để kiểm dữ liệu vị trí bãi.

## Dữ liệu cần cho mỗi lượt tàu

Mã tàu, chuyến, cầu bến, giờ vào (cập cầu), bắt đầu và kết thúc làm hàng, sản lượng nhập, xuất, đảo chuyển (container hoặc tấn),
số cẩu làm tàu, giờ chạy dự kiến và giờ chạy điều chỉnh. Tàu thuộc kỳ báo cáo theo **ngày tàu vào** (ghi rõ quy ước này).

## Chỉ số và cách tính

| Chỉ số | Cách tính | Lưu ý |
|---|---|---|
| Thời gian làm tàu | Kết thúc - Bắt đầu làm hàng | Giờ kết thúc nhỏ hơn giờ bắt đầu nghĩa là sang ngày sau |
| Năng suất tàu | Sản lượng / thời gian làm tàu | Nêu rõ tính theo giờ gộp hay đã trừ gián đoạn |
| Năng suất cẩu | Sản lượng của cẩu / giờ cẩu làm việc | Theo từng cẩu; cẩu thay thế tính phần giờ của nó |
| Trễ giờ chạy | Điều chỉnh - Dự kiến | Ô điều chỉnh trống là đúng giờ (ghi "Đúng giờ"), âm là "Sớm"; có tỷ lệ đúng giờ |
| Gián đoạn | Cộng phút theo thiết bị, sự kiện | Hai sự kiện đồng thời vẫn cộng riêng, nói rõ là cộng chồng |
| Chờ cập (sà lan) | Thực tế cập - Dự kiến cập | Lượt xuất ngay sau lượt nhập: dự kiến cập = giờ dứt nhập |
| Chờ làm hàng (sà lan) | Bắt đầu làm hàng - Thực tế cập | Tổng chờ = chờ cập + chờ làm hàng |

## Sự cố, gián đoạn thiết bị

- Mỗi sự cố một dòng: thiết bị, chuyến tàu, từ giờ, đến giờ, loại (hư, bảo dưỡng, tạm ngưng, chờ hàng, dời cẩu, dời tàu, ngưng toàn
  tàu), nguyên nhân, nhóm trách nhiệm (thiết bị; bãi, đảo chuyển; điều phối, kế hoạch; ngoại cảnh; chưa phân nhóm), cách xử lý.
- Thiết bị hư rồi nghỉ luôn: đến giờ = từ giờ (0 phút), ghi chú "nghỉ luôn". Có thiết bị thay sau khi chờ: đến giờ = giờ thiết bị
  thay bắt đầu làm. Hư ngay khi vào ca và được thay: ghi nhận nhưng có cờ không tính vào báo cáo tàu.
- **Đối soát sự cố với chuyến tàu (bắt buộc)**: giờ bắt đầu sự cố phải nằm trong khoảng [giờ vào - 3 giờ; max(giờ chạy áp dụng,
  hết làm hàng) + 3 giờ] của chuyến được gắn; ngoài khoảng thì báo lỗi và gợi ý chuyến đang ở cầu lúc đó. Lỗi hay gặp: dòng trống
  mã chuyến bị lấy theo dòng trên, gắn nhầm chuyến cũ. Không tự sửa mã chuyến khi chưa được xác nhận.
- Thiết bị tiền phương không có trong danh sách cẩu làm tàu của chuyến: cảnh báo (bỏ qua sự kiện toàn tàu, dời cẩu, dời tàu).

## Sà lan chờ cầu

Nguyên nhân chờ chọn từ danh sách: cầu bận (tàu chưa rời), tàu chạy trễ, ưu tiên làm tàu, thiếu cẩu, chờ hàng hoặc chứng từ,
ra phao chờ hàng xuất, thời tiết hoặc triều, thiết bị hư, khác. Chờ trên 1 giờ phải có nguyên nhân; nguyên nhân do tàu phải ghi
tàu gây ảnh hưởng. Chưa ghi thì gợi ý tàu đang ở cầu trong khoảng chờ (tàu trùng thời gian lớn nhất) và đánh dấu "cần xác nhận".

## Bố cục báo cáo gợi ý

I Tổng quan (thẻ chỉ số: số lượt tàu, sản lượng, năng suất, tỷ lệ đúng giờ, tổng phút gián đoạn) · II Dòng thời gian tàu ở cầu ·
III Tổng hợp theo tàu · IV Phân tích gián đoạn (theo thiết bị, nhóm trách nhiệm) · V Theo ngày · VI Sà lan chờ cầu ·
VII Chi tiết sự cố · VIII Kiểm tra dữ liệu (lỗi đối soát, thiếu dữ liệu). Thiếu dữ liệu thì cảnh báo, không tự điền.

## Căn cứ pháp lý

`references/legal-basis.md`: Bộ luật Hàng hải, nghị định quản lý hoạt động hàng hải, biểu khung giá dịch vụ cảng biển, hải quan,
an toàn lao động; có ngày đối chiếu. Báo cáo nội bộ thường không cần viện dẫn; chỉ dẫn khi báo cáo gửi cơ quan quản lý (cảng vụ,
hải quan) hoặc khi nêu nghĩa vụ báo cáo tai nạn, sự cố.

## Thư viện nguồn của project

Project có `references/_INDEX.xlsx` thì tra ở đó trước (`python tools/library.py find <số hiệu hoặc từ khóa>`): có toàn văn thì
đọc file và trích nguyên văn; không có thì ghi "[chưa đối chiếu toàn văn]". Chỉ mục của project đứng trước bảng
`references/legal-basis.md` của gói (bảng của gói là mốc tham khảo chung). Văn bản dùng thường xuyên mà chưa có trong thư viện:
đề xuất người dùng tải bản chính thống về và thêm dòng chỉ mục (skill `source-library`).

## Kiểm trước khi giao

- Tổng sản lượng, tổng phút gián đoạn khớp giữa bảng chi tiết và thẻ tổng; kiểm cả từng tàu.
- Không còn lỗi đối soát sự cố - chuyến chưa xử lý, hoặc đã nêu rõ trong mục kiểm tra dữ liệu.
- Quy ước tính (kỳ theo ngày tàu vào, giờ gộp hay trừ gián đoạn, cộng chồng) ghi ở chân báo cáo.
