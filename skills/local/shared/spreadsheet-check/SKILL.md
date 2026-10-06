---
name: spreadsheet-check
description: >-
  Gợi ý kiểm tra nhanh một file Excel/CSV trước khi dùng số liệu cho báo cáo, tổng hợp
  hoặc dashboard HTML: cấu trúc, ô trống, trùng lặp, kiểu dữ liệu, đơn vị, tổng không khớp.
  Chỉ báo phát hiện, không tự sửa dữ liệu gốc.
  Kích hoạt khi người dùng nói: “kiểm tra file Excel/CSV”, “dữ liệu có sạch không”, “kiểm trước khi làm báo cáo”.
metadata:
  version: "1.3"
---

# Kiểm tra bảng tính trước khi dùng

Dùng khi sắp lấy số từ một bảng tính để làm báo cáo hoặc biểu đồ. Nếu người dùng chỉ hỏi
một con số đơn giản, đọc đúng ô/cột liên quan và trả lời; không kiểm tra cả file.

## Cách làm

1. **Nắm cấu trúc:** tên sheet, vùng có dữ liệu, dòng tiêu đề, ô gộp, sheet ẩn. Nếu có
   nhiều sheet, chỉ đi sâu vào sheet liên quan tới yêu cầu.
2. **Kiểm tra các cột liên quan tới kết quả:**
   - ô trống ở cột then chốt (ngày, mã, số lượng, trạng thái);
   - dòng hoặc mã trùng;
   - số lưu dạng chữ, ngày nhiều định dạng, cùng một mục viết nhiều cách;
   - đơn vị lẫn lộn (tấn/kg, nghìn/triệu) hoặc lẫn kỳ báo cáo;
   - dòng tổng cộng không bằng tổng các dòng; công thức lỗi (`#REF!`, `#DIV/0!`);
   - giá trị bất thường (âm, quá lớn, ngoài kỳ) — chỉ nêu, không kết luận là sai.
3. Dùng công cụ tính toán hoặc script khi bảng lớn; đối chiếu một vài dòng bằng mắt thường.
   Nếu chỉ lấy mẫu, nói rõ phạm vi đã kiểm.

## Script kèm theo (tùy chọn)

`scripts/check_spreadsheet.py` chạy các kiểm tra trên bằng máy, chỉ đọc, không sửa file:

```text
python skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py FILE.xlsx --khoa "Mã"
python skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py FILE.csv
```

CSV chỉ cần Python 3.8+. Excel cần `openpyxl` (`pip install openpyxl`); không có thì script báo rõ và
dừng, khi đó xuất sheet sang CSV hoặc kiểm bằng cách khác. `--sheet TÊN` chỉ kiểm một sheet; `--khoa`
chỉ định cột mã để tìm trùng. Kết quả chia ba nhóm như bên dưới; vẫn cần người đọc đánh giá ý nghĩa
nghiệp vụ. Số dạng `1.234` hoặc `1,234` được ghi là "mơ hồ" thay vì đoán. Script in cuối một dòng "Dấu vết" (file, sha256, giờ chạy); khi báo cáo, chép dòng đó vào khối "Khai báo thực hiện" của `AGENTS.md`, và nêu con số cụ thể của từng phát hiện (giá trị ghi, giá trị tính lại, chênh lệch) cùng các cách hiểu của chỗ mơ hồ. Với ô mơ hồ như `1.234`, viết đúng chuỗi như trong file và nêu hai cách đọc (là 1234, hoặc là một phẩy hai trăm ba mươi bốn) kèm tổng theo từng cách; script in cả hai tổng. Số trong kết quả tiếng Việt dùng dấu chấm ngăn cách nghìn. Mỗi phát hiện kèm số dòng trong file hoặc sheet (dòng đầu tiên là dòng 1); khi nêu vị trí, dùng đúng số dòng đó và không tự đánh số lại.

## Kết quả

Trả danh sách ngắn theo mức ảnh hưởng, mỗi mục nêu sheet, cột hoặc dòng ví dụ và số lượng:

- **Ảnh hưởng đến số liệu:** cần xử lý hoặc xác nhận trước khi dùng.
- **Cần hỏi:** định nghĩa hoặc đơn vị chưa rõ.
- **Lưu ý:** không ảnh hưởng kết quả hiện tại.

Nếu không phát hiện vấn đề trong phạm vi đã kiểm, nói rõ phạm vi đó thay vì khẳng định
file "đúng".

## Giới hạn

Không sửa, sắp xếp lại hay lưu đè file gốc; nếu cần bản đã làm sạch thì tạo bản mới
trong `working/` khi được yêu cầu. Không thay ô thiếu bằng 0 hoặc giá trị đoán. Không tự
dựng báo cáo hay biểu đồ nếu chưa được yêu cầu; khi cần, tiếp tục với `html-reports`.
Hết danh sách phát hiện thì dừng.
