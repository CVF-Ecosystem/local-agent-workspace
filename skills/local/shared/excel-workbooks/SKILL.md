---
name: excel-workbooks
description: >-
  Gợi ý dựng sổ theo dõi, form nhập liệu, báo cáo tự tổng hợp và phụ lục tính bằng Excel
  (openpyxl, công thức thật): bố cục nhập → báo cáo, dropdown, tô màu trạng thái, ô tham số,
  dữ liệu mẫu tách riêng, kiểm tra trước khi giao. Không dùng để kiểm tra dữ liệu có sẵn
  (xem `spreadsheet-check`) hay vẽ biểu đồ HTML (xem `data-charts`).
  Kích hoạt khi người dùng nói: “sổ theo dõi”, “form nhập liệu Excel”, “báo cáo tự tổng hợp”, “phụ lục Excel”, “bảng điều hành trong Excel”.
metadata:
  version: "1.0"
---

# Dựng sổ và báo cáo bằng Excel

Dùng khi cần một file Excel SỐNG (người dùng nhập tiếp, báo cáo tự cập nhật) hoặc phụ lục tính đi kèm
đề án. Biểu mẫu điền một lần rồi in thì xem `office-documents`. Kỹ thuật chi tiết, giới hạn và lỗi đã
gặp: `references/openpyxl-notes.md` (mở khi dựng thật).

## Bố cục: nhập → báo cáo

- **Sheet log là nguồn số liệu duy nhất.** Mỗi dòng một vụ việc, thêm dòng mới chứ không sửa lịch sử,
  có cột mã/khóa riêng; cố định dòng tiêu đề và bật lọc.
- **Sheet báo cáo chỉ chứa công thức** (`COUNTIFS`, `SUMIFS` trỏ về log) và một hai ô chọn kỳ; không bao giờ
  có số nhập tay. Đặt kỳ mặc định trùng dữ liệu mẫu để không hiện toàn số 0 khiến người dùng tưởng công thức hỏng.
- **Sheet danh mục** giữ danh sách chọn và bảng ánh xạ; **sheet hướng dẫn** đặt đầu tiên.
- Sheet tổng quan chỉ liên kết sang sheet chi tiết, không tính lại số đã có ở nơi khác.
- Khối tính mới thêm xuống CUỐI sheet, không chèn giữa: công thức ở sheet khác trỏ địa chỉ cố định sẽ lệch
  âm thầm mà kiểm tra công thức không phát hiện.
- Cập nhật bản sau thì giữ tên sheet, tên cột, dòng tiêu đề; công cụ khác (như `excel-html-viewer`) có thể đọc theo các tên này.

## Dễ nhập, khó sai

Dropdown phủ cả vùng trống phía dưới dữ liệu mẫu; tô màu trạng thái theo giá trị; thêm cột "Kiểm tra" (OK/lỗi)
cho các ràng buộc hay sai (trùng mã, thiếu ngày, khoảng giờ chồng nhau). Khóa sheet không mật khẩu: ô công
thức khóa, ô nhập mở, vẫn cho lọc và sắp xếp; không khóa cấu trúc workbook nếu quy trình cần sao chép sheet.

## Tham số, ngưỡng và dữ liệu mẫu

- Ô tham số và ngưỡng đặt ở vị trí cố định, có nhãn. **Ô ngưỡng để trống nghĩa là chưa quy định**: công thức
  vẫn chạy và không gắn cờ.
- Số liệu chưa có thì để trống hoặc ghi "………"; không tự điền. Mọi ngưỡng, định mức do agent đề xuất ghi rõ
  "đề xuất, chờ người có thẩm quyền quyết định".
- Số minh họa chỉ nằm trong một sheet riêng "DỮ LIỆU MẪU", tô nền khác và ghi giả định; sheet dữ liệu thật để trống.
- Quy ước màu (dùng nhất quán trong cả file): ô nhập vàng nhạt, trạng thái đỏ/vàng/xanh nhạt, dữ liệu mẫu xanh dương nhạt;
  trong mô hình tính, chữ xanh dương là đầu vào, đen là công thức, xanh lá là liên kết sang sheet khác.

## Phụ lục tính cho đề án

Mọi ô kết quả là công thức thật, kể cả khi đầu vào là giả định; giả định ghi "giả định, cần xác nhận" ngay tại ô
(hoặc tên sheet kèm "(giả định)"). Số trong Word và Excel phải khớp nhau; sửa một bên thì rà bên kia. Bài toán
năng lực nhiều khâu (A → B → C) tính theo chiều xuôi từ sản lượng hoặc nhu cầu thực tế, nên hỏi người dùng số liệu
vận hành thật thay vì chọn thông số "đẹp" rồi khớp ngược; một thông số đổi thì tính lại cả chuỗi, không chỉ một sheet.
Cấu trúc gợi ý (bỏ hoặc đổi theo đề án): Tổng quan; chi phí đầu tư theo hạng mục; cấu hình kỹ thuật liên kết số lượng
từ sheet chi phí; phân tích năng lực; chi phí vận hành; điểm hòa vốn; lộ trình có lưới Gantt bằng công thức.
Phân biệt rõ hạng mục đầu tư mới với tài sản đã có; tên gọi rút gọn dễ đọc nhầm là "đã có sẵn" thì ghi đầy đủ.

## Trước khi giao

Tính lại công thức và xác nhận không còn lỗi (`#NAME?`, `#REF!`...), render ra ảnh hoặc PDF để xem bảng nhiều cột nhất,
kiểm tra khi dữ liệu đầy tải. Nói rõ phần chưa thử (ví dụ chưa mở bằng Excel thật).
Thử bằng chính dữ liệu: chép vài dòng dữ liệu mẫu vào sheet nhập, rồi (1) đổi ô kỳ sang tháng khác, số báo cáo phải đổi đúng theo kỳ, không cộng dồn mọi tháng;
(2) để ô ngưỡng/định mức trống, báo cáo vẫn chạy và không gắn cờ; (3) thêm một dòng với mã mới, báo cáo phải bắt được. Ô tham số mặc định để trống, không đặt sẵn
số "cho đẹp" (90, 100...). Danh sách phương tiện, hạng mục ở sheet báo cáo lấy từ sheet danh mục bằng công thức, không gõ tay. Dữ liệu mẫu phải là câu chữ có nghĩa. Chi tiết: `references/openpyxl-notes.md`.
