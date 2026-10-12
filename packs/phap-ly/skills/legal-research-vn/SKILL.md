---
name: legal-research-vn
description: Gợi ý tra cứu và áp dụng văn bản quy phạm pháp luật Việt Nam: 5 trục vấn đề, văn bản áp dụng đúng thời điểm, tra chéo sửa đổi và thay thế, trích nguyên văn có tọa độ, xung đột, phương án; không thay thế ý kiến pháp lý. Kích hoạt khi người dùng hỏi "luật quy định thế nào", "căn cứ pháp lý", "văn bản nào còn hiệu lực", "xử lý tình huống này theo quy định", "khiếu nại", "bồi thường". / Suggestions for researching and applying Vietnamese legal documents to a concrete situation. Triggers when the user asks what the law says, for the legal basis, which document is in force, or how to handle a situation under the rules.
metadata:
  version: "0.2"
---

# Tra cứu và áp dụng văn bản quy phạm pháp luật

Văn bản pháp luật Việt Nam là các bản ghi rời: luật, nghị định, thông tư sửa đổi, thay thế, bãi bỏ lẫn nhau. Không đọc hết;
tra đúng chỗ và ghép đúng thứ tự. Mọi kết luận phải truy được về một câu trích nguyên văn có tọa độ. Skill hỗ trợ nghiên cứu
và tư vấn sơ bộ, không thay thế ý kiến của luật sư hoặc cơ quan có thẩm quyền.

## 1. Định danh vấn đề theo 5 trục

| Trục | Câu hỏi |
|---|---|
| Đối tượng | Ai, cái gì (chủ thể, tài sản, hợp đồng, hồ sơ)? |
| Hành vi | Làm gì (chấm dứt, chuyển nhượng, xử phạt, khai báo)? |
| Tác động | Hệ quả gì (quyền, nghĩa vụ, trách nhiệm, chế tài)? |
| Phạm vi | Ở đâu, loại hình nào (địa phương, loại doanh nghiệp, lĩnh vực chuyên ngành)? |
| Thời điểm | Khi nào sự việc xảy ra hoặc hồ sơ được nộp? Trục này quyết định văn bản nào áp dụng. |

Thiếu trục nào ảnh hưởng tới kết luận (thường là thời điểm) thì hỏi gộp một lần. Ghi luôn **câu hỏi đích** (điều người dùng
cần biết) và **điều kiện đủ** (có căn cứ nào thì trả lời được), để biết khi nào dừng.

## 2. Tìm văn bản và trích nguyên văn

1. Bắt đầu từ văn bản người dùng có (thư mục văn bản, file PDF, bản chụp). PDF quét không có lớp chữ thì xem ảnh từng trang
   cần đọc, không đoán nội dung; công cụ OCR thiếu tiếng Việt cho kết quả sai dấu, chỉ dùng để định vị trang.
2. Chưa có văn bản thì tra nguồn chính thống (`references/sources-and-search.md`); bài phân tích trên mạng chỉ dùng để gợi
   từ khóa, câu trích phải lấy từ văn bản gốc.
3. Mỗi câu trích ghi đủ: tọa độ (loại văn bản, số hiệu, Điều, khoản, điểm), nguyên văn (dùng `[...]` cho phần lược), trạng
   thái hiệu lực tại thời điểm của vụ việc, ngày có hiệu lực (không phải ngày ban hành). Mẫu bảng: `references/citation-and-basis-table.md`.
4. Không tự viết lại hoặc tóm tắt rồi đặt trong ngoặc kép. Không nhớ chắc số hiệu, điều khoản thì ghi `[cần xác nhận]`.

## 3. Tra chéo ba chiều

Với mỗi văn bản đưa vào bảng căn cứ (chi tiết: `references/cross-reference.md`):

- **Xuống**: luật giao Chính phủ hoặc bộ quy định chi tiết thì tìm nghị định, thông tư tương ứng.
- **Ngang**: văn bản đã bị sửa đổi, thay thế, bãi bỏ (toàn bộ hay một phần) chưa; có luật sửa nhiều luật cùng lúc không.
- **Thời gian**: bản nào có hiệu lực tại thời điểm của vụ việc; có điều khoản chuyển tiếp không.

## 4. Xử lý xung đột

Hai văn bản quy định khác nhau về cùng một việc: văn bản cấp cao hơn được áp dụng trước; cùng cấp thì văn bản ban hành sau;
văn bản chuyên ngành đứng trước văn bản chung khi cùng cấp. Không phân xử được thì nêu hai hướng, mỗi hướng kèm căn cứ, chấm
1 - 5 về độ chắc của căn cứ, rủi ro, khả thi, và khuyến nghị hỏi ý kiến cơ quan có thẩm quyền. Thứ bậc văn bản theo Luật Ban
hành văn bản quy phạm pháp luật hiện hành; tra điều quy định hệ thống văn bản trước khi viện dẫn thứ bậc (`references/cross-reference.md`).

## 5. Khi nào dừng

Dừng khi đạt điều kiện đủ ở mục 1, hoặc khi hai lượt tra liên tiếp không ra văn bản hay câu trích mới. Áp dụng giới hạn công
việc trong `AGENTS.md`: câu hỏi ngắn trả lời ngắn kèm căn cứ; không mở thêm lĩnh vực chỉ vì còn có thể tra.

## 6. Trình bày kết quả

Mặc định trả lời trong hội thoại. Chỉ tạo file (báo cáo, bảng căn cứ, nhật ký tra cứu) khi người dùng yêu cầu; khi đó lưu theo
quy ước thư mục của project. Bài trả lời đầy đủ gồm:

1. **Tình huống và vấn đề pháp lý**: 5 trục, câu hỏi đích; giả định nào chưa xác nhận thì ghi `[Giả định]` kèm ảnh hưởng.
2. **Căn cứ**: bảng căn cứ, sắp theo thứ bậc văn bản; đánh dấu xung đột.
3. **Phương án** (khi có từ hai cách xử lý): mỗi phương án kèm căn cứ (trỏ số dòng trong bảng), ưu, nhược, rủi ro.
4. **Khuyến nghị và lộ trình**: hồ sơ cần chuẩn bị, cơ quan thụ lý, thời hạn, theo chuỗi điều kiện → thẩm quyền → hồ sơ →
   trình tự → thời hạn → kết quả → hệ quả. Chỉ ghi những mắt xích có căn cứ.
5. **Cảnh báo**: điểm chưa rõ, trường hợp cần luật sư hoặc cơ quan có thẩm quyền, nguồn đã dùng; câu "Nội dung mang tính tham
   khảo, không thay thế ý kiến pháp lý chính thức."

Văn bản gửi ra ngoài hoặc trình ký có viện dẫn pháp lý thuộc "Mức thận trọng cao" trong `AGENTS.md`. Soạn văn bản hành chính
từ kết quả tra cứu: `vn-admin-documents`.

## Thư viện nguồn của project

Project có `references/_INDEX.xlsx` thì tra ở đó trước (`python tools/library.py find <số hiệu hoặc từ khóa>`): có toàn văn thì
đọc file và trích nguyên văn; không có thì ghi "[chưa đối chiếu toàn văn]". Chỉ mục của project là nơi tra
đầu tiên, trước nguồn trên mạng; cột Ngày kiểm tình trạng và Mức độ xác minh cho biết cần tra lại tới đâu. Văn bản dùng thường xuyên mà chưa có trong thư viện:
đề xuất người dùng tải bản chính thống về và thêm dòng chỉ mục (skill `source-library`).

## Kiểm trước khi giao

- Thời điểm của vụ việc đã xác định; mỗi văn bản trong bảng có trạng thái hiệu lực đúng thời điểm đó và ngày có hiệu lực.
- Mỗi câu trích có đủ tọa độ và là nguyên văn; văn bản sửa đổi đã ghép với văn bản gốc.
- Kết luận nào cũng trỏ được về một dòng trong bảng căn cứ; phần suy luận ghi rõ là suy luận.
- Đã nêu điều chưa kiểm được (ví dụ chưa xem bản hợp nhất, chưa có văn bản địa phương).
