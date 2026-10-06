# Nguồn tham khảo và phạm vi biên soạn

## Nền tảng

Package bản v1.3 được biên soạn từ một bộ khung workspace do người dùng cung cấp trước đó, làm gọn
hướng dẫn và bổ sung tài nguyên văn phòng đã thống nhất.
Các file gốc của người dùng không được gán lại một giấy phép chung mới.

## Repo được xem xét

Repo: https://github.com/sharkrebel/everything-everywhere-for-antigravity

Bản tham chiếu: `68a4398e3dd32c83831bc4720024ed95a91c6757`, ngày 02/10/2026.
Ngày biên soạn package: 06/10/2026. Đây là tham chiếu nội dung, không phải tuyên bố
repo hoặc mọi native skill đã được chạy thử trên Claude/Codex/Antigravity.

| Thành phần | Ý tưởng tham khảo | Cách sử dụng trong package |
|---|---|---|
| Cách viết skill | skill-creator | Hướng dẫn ngắn, chỉ nạp tài nguyên cần, giữ quyền phán đoán của agent. |
| office-documents | doc-coauthoring, internal-comms (ý tưởng về tổ chức nội dung) | Biên soạn mới bằng tiếng Việt, bổ sung khung SOP/biểu mẫu/cập nhật; không chép quy trình nhiều vòng. |
| html-reports | lieflat-charts và report-catalog | Tham khảo nhu cầu báo cáo một-file và chọn mẫu theo nội dung; hai mẫu HTML được viết độc lập, không lấy mã hoặc bố cục R04/R09/R12. |
| data-charts | lieflat-charts | Viết lại quy tắc chọn và trình bày biểu đồ; mẫu SVG offline viết mới. |
| internal-comms | internal-comms | Viết lại bằng tiếng Việt, thêm thông báo và báo cáo sự cố. |
| doc-coauthoring | doc-coauthoring | Viết lại, giới hạn số vòng; chỉ dùng khi người dùng muốn. |
| vietnamese-editing | humanizer | Biên soạn mới cho tiếng Việt; tham chiếu dấu hiệu văn phong viết riêng cho tiếng Việt, không chép danh sách tiếng Anh hay quy định dấu câu. |
| Hướng dẫn HTML | Các hướng dẫn Markdown của package | Bản trình bày dựng từ Markdown, CSS/JS nội tuyến, không dùng theme, font hay script ngoài. |

## Các file nguồn để đối chiếu

- skill-creator: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/skill-creator/SKILL.md
- doc-coauthoring: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/doc-coauthoring/SKILL.md
- internal-comms: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/internal-comms/SKILL.md
- humanizer: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/humanizer/SKILL.md
- lieflat-charts: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/lieflat-charts/SKILL.md
- Danh mục báo cáo: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/lieflat-charts/report-catalog.md
- Giấy phép Lieflat: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/lieflat-charts/LICENSE

## Bốn skill được chọn từ repo và cách viết lại

Bốn skill dưới đây được một agent đề xuất sau khi audit repo và đã được đọc trực tiếp ở cùng
commit `68a4398e`. Package không nhập nguyên bản: mỗi skill gốc nặng hoặc không khớp mục tiêu
(việc văn phòng, tiếng Việt, hạn chế vòng lặp của agent, mở offline), nên được viết lại thành
skill ngắn tiếng Việt, giữ phần ý tưởng hữu ích.

| Skill gốc | Quan sát | Bản trong package |
|---|---|---|
| lieflat-charts | `SKILL.md` ~38 KB bằng tiếng Trung; hơn 120 file (~20 MB); nhiều quy tắc bắt buộc; 31 mẫu HTML cần mạng (CDN, font). Điểm đáng giữ: chọn biểu đồ theo hình dạng dữ liệu, quy tắc trình bày, danh sách kiểm tra trước khi giao, không dùng 3D. | `data-charts`: quy tắc và cách chọn biểu đồ viết lại; mẫu `basic-charts.html` viết mới bằng SVG thuần, offline. |
| internal-comms | Nhỏ; ví dụ theo định dạng nội bộ của một công ty (3P, bản tin, FAQ). Điểm đáng giữ: Tiến độ - Kế hoạch - Vấn đề, đọc trong 30–60 giây. | `internal-comms`: tiếng Việt; thêm thông báo và báo cáo sự cố; bỏ phần tự thu thập từ kênh chat vì không có trong môi trường này. |
| doc-coauthoring | ~16 KB; ba giai đoạn nhiều vòng, gồm kiểm tra người đọc bằng agent phụ. Điểm đáng giữ: gom ngữ cảnh, chốt dàn ý, soạn từng mục, soát cuối. | `doc-coauthoring`: bốn bước, mỗi bước giới hạn số vòng; chỉ dùng khi người dùng muốn; kiểm tra người đọc là tùy chọn và không dùng agent phụ. |
| humanizer | ~31 KB; 35 mẫu dấu hiệu văn phong AI trong tiếng Anh; nhiều lượt rà soát. Điểm đáng giữ: không thêm dữ kiện, giữ giọng người viết, danh sách "không coi là lỗi". | Gộp vào `vietnamese-editing` dưới dạng `references/machine-style-signs.md`: dấu hiệu tiếng Việt, một lượt sửa. |

Năm skill khác (document-comparison, spreadsheet-check, meeting-minutes, process-mapping,
vn-admin-documents) được viết mới theo nhu cầu công việc, không sao chép từ repo. Riêng
`vn-admin-documents` lấy căn cứ tham khảo là quy định về công tác văn thư (Nghị định 30/2020/NĐ-CP); đây là
gợi ý về thể thức, không phải ý kiến pháp lý, và quy định có thể đã được sửa đổi. `skills/external/` vẫn để
trống; nếu sau này nhập skill ngoài, ghi nguồn, commit và giấy phép theo hướng dẫn trong
thư mục đó.

## Phần không nhập vào ZIP

File LICENSE của lieflat-charts ghi **PolyForm Noncommercial License 1.0.0**. Package không
đưa template hay mã của thư viện đó vào; các mẫu HTML của `html-reports` và `data-charts`
được viết mới. Đây là lựa chọn đóng gói, không phải kết luận pháp lý về một trường hợp
sử dụng cụ thể.

Không sao chép native skill định dạng, global rules, SOUL, installer, hook, plugin,
font hoặc dependency của repo. Không tuyên bố các mẫu mới là sản phẩm Lieflat/Moxt.
Các đường dẫn nguồn chỉ để người dùng mở khi muốn đối chiếu; file HTML đi kèm không
truy cập các địa chỉ này khi mở hoặc lọc dữ liệu.

## Giới hạn kiểm tra

Bản v1.3 được kiểm tra file, đường dẫn nội bộ, metadata skill (tên khớp thư mục và index),
các trang HTML dựng lại từ Markdown (bộ tiếng Việt và bộ tiếng Anh, kèm nút chuyển ngôn ngữ hai chiều)
và mẫu `basic-charts.html` trong trình duyệt Chromium local (không lỗi console, không yêu cầu mạng,
không cuộn ngang ở chiều rộng điện thoại). Bản dịch tiếng Anh do agent viết, chưa được người bản ngữ rà soát.
Script `check_spreadsheet.py` được chạy thử trên file mẫu tự tạo (xlsx và csv), chưa trên dữ liệu thật. Chưa chạy thử các skill mới trong Claude Desktop, Codex Desktop hay Antigravity, không đo mức
giảm token hay mức giảm vòng lặp, và không chứng nhận tương thích native trên mọi phiên bản.
