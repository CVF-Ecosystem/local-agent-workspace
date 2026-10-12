# Khung DOCX mặc định và chuyển nội dung thô thành tài liệu

Dùng khi dựng file Word mới mà người dùng không đưa mẫu. Mẫu hoặc quy chế của đơn vị luôn đứng trước khung này. Văn bản
theo thể thức nhà nước: `vn-admin-documents` (`references/nd30-presentation.md`). Các thông số dưới đây nằm trong khoảng
của Phụ lục I Nghị định 30/2020/NĐ-CP, nên một khung dùng được cho cả tài liệu nội bộ lẫn văn bản hành chính.

## Trang và đoạn

| Mục | Mặc định |
|---|---|
| Trang | A4; lề trên 20 mm, dưới 20 mm, trái 30 mm, phải 15 - 20 mm |
| Phông | Times New Roman (hoặc phông đơn vị quy định), màu đen; thân bài cỡ 13 (14 nếu đơn vị quen dùng) |
| Thân bài | Canh đều hai lề; đầu dòng lùi 1,27 cm; cách sau đoạn 6pt; cách dòng 1,15 - 1,3 lines (không quá 1,5) |
| Đề mục | Đậm, không thụt đầu dòng hoặc thụt ít hơn thân bài; không dùng nghiêng hay gạch chân để phân cấp; `keep_with_next` |
| Bảng | Rộng bằng vùng chữ; chữ trong bảng nhỏ hơn thân bài 1 - 2 cỡ; dòng tiêu đề đậm, lặp khi sang trang; cột rộng theo nội dung |
| Số trang | Giữa lề trên (văn bản hành chính) hoặc chân trang (tài liệu nội bộ), không hiện ở trang đầu |

Phân cấp bằng ký hiệu đầu dòng, không tăng lề trái theo cấp: `I.` → `1.` → `a)` → `-` → `+`. Gạch đầu dòng trong văn bản
tiếng Việt dùng `-`, không dùng `•`, trừ khi mẫu của người dùng dùng ký hiệu khác.

Màu chỉ là lớp phủ lên khung: tô dòng tiêu đề bảng, màu chữ đề mục, khung ghi chú, trang bìa. Không đổi lề, cỡ chữ, khoảng
cách vì màu. Văn bản theo thể thức nhà nước giữ đen trắng.

## Chuyển nội dung thô (ghi chú, Markdown, nội dung chat) thành tài liệu

Đọc nội dung, kiểm kê các tín hiệu dưới đây rồi mới dựng. Việc lớn (nhiều mục, nhiều bảng, hoặc cùng lúc Word, Excel và
slide): trình người dùng một kế hoạch trình bày 3 - 5 dòng (chia mục, bảng nào giữ, số nào làm nổi bật, định dạng đích)
trước khi dựng, đúng như bước "chốt dàn ý" của việc lớn trong `AGENTS.md`. Việc vừa thì dựng luôn.

| Tín hiệu trong nội dung | Gợi ý trình bày |
|---|---|
| Số đề mục và độ sâu | Quy mô tài liệu, cách chia mục; trên 10 trang thì thêm mục lục |
| Bảng có cột toàn số, %, tiền | Bảng có định dạng số; trong Excel thêm dòng tổng bằng công thức; nhiều kỳ thì cân nhắc biểu đồ (`data-charts`) |
| Con số nổi bật giữa văn xuôi | Khung ghi chú hoặc thẻ chỉ số (báo cáo HTML) |
| Câu lưu ý, cảnh báo | Khung ghi chú có viền |
| Chuỗi bước 1 → 2 → 3 | Bảng bước hoặc sơ đồ luồng (`process-mapping`) |
| Cặp Trước/Sau, Vấn đề/Giải pháp | Bảng hai cột |

Chọn định dạng đích khi người dùng chưa nói: nhiều bảng cần tính hoặc lọc → Excel; văn bản đọc tuần tự hoặc in → Word;
trình bày trước đám đông → slide. Không nhồi văn xuôi vào Excel hay slide; nội dung không có bảng thì báo là không hợp Excel.

Biên tập khi chuyển: thêm một hai câu dẫn đầu mục lớn; ý là lập luận liền mạch thì viết thành đoạn, chỉ dùng gạch đầu
dòng cho liệt kê thật; bỏ biểu tượng cảm xúc, mũi tên và cú pháp Markdown còn sót; không đổi số liệu, ngày, tên riêng.

## Đếm kiểm sau khi dựng

Đếm trên chữ bóc từ chính file đã dựng, không trên bản nháp. Mẫu dưới đây đếm chỗ trống chưa điền (mọi cụm trong ngoặc vuông), ghi chú "cần xác nhận"
và những ký hiệu người dùng hoặc mẫu không muốn có (thêm, bớt mẫu tìm theo yêu cầu, ví dụ dấu gạch dài khi mẫu không dùng):

```text
python -c "import zipfile,re,sys;x=re.sub(r'<[^>]+>','',zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf8'));[print(p,len(re.findall(p,x))) for p in sys.argv[2:]]" file.docx "\[[^\]]*\]" "cần xác nhận" "•" "—"
```

Kết quả khác 0 thì sửa hoặc nêu trong lời giao (ví dụ "còn 3 chỗ [cần xác nhận] ở mục II"). Không sửa ký hiệu mà mẫu của
người dùng đang dùng.
