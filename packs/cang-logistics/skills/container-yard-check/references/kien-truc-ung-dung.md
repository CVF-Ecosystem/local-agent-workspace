# Kiến trúc tham khảo cho công cụ kiểm tra dữ liệu bãi

Đây là mẫu chia lớp, không bắt buộc một ngôn ngữ hoặc thư viện. Chọn công nghệ theo môi trường đã được project chấp thuận và kiểm tra dependency trước khi dùng.

## Luồng xử lý

File nguồn → đọc và nhận diện cấu trúc → chuẩn hóa cột, vị trí và trạng thái → bảng chuẩn hóa có liên kết dòng nguồn → các phép phân tích theo cấu hình đã xác nhận → báo cáo và sổ chất lượng dữ liệu.

Tách đọc, chuẩn hóa, phân tích và xuất. Một bảng chuẩn hóa giữ giá trị nguồn, giá trị đã chuẩn hóa, trạng thái xác thực và lý do thay đổi. Phân tích nhận bảng cùng cấu hình rồi trả kết quả; không ghi file bên trong từng phép kiểm.

## Các lớp gợi ý

| Lớp | Trách nhiệm |
|---|---|
| Đọc và nhận diện | Kiểm sheet, dòng tiêu đề, cột, kiểu giá trị và lỗi đọc; lưu locator về dòng nguồn |
| Chuẩn hóa | Chuẩn hóa bí danh cột, vị trí, trạng thái và mã theo quy tắc được duyệt; giữ nguyên giá trị gốc |
| Chất lượng dữ liệu | Ghi mã lỗi, mức, dòng nguồn, vị trí và lý do; không sửa lỗi âm thầm |
| Phân tích | Dùng cùng bảng chuẩn hóa và cùng tập cont đã xác nhận đang chiếm ô cho các phép kiểm phụ thuộc occupancy |
| Báo cáo | Tạo Excel/HTML từ cùng kết quả phân tích và giữ đơn vị cùng locator nguồn |
| Điều phối | Nhận cấu hình, gọi các bước, xử lý lỗi, ghi rõ đường dẫn output và trạng thái hoàn tất |

Nếu ứng dụng chia module riêng cho vị trí, RTG, lót pháo, thống kê hoặc lịch sử, các module phân tích vẫn nên đọc cùng bảng chuẩn hóa. Không lặp lại logic xác định trạng thái chiếm ô ở từng module.

## Cấu hình

Đặt quy tắc giữa các project trong cấu hình riêng, có schema hoặc kiểm tra kiểu. Tùy phạm vi, cấu hình có thể chứa:

- Bí danh cột và thứ tự thành phần vị trí.
- Bảng ánh xạ trạng thái, hướng hàng, F/E, mã đặc biệt và khu vực.
- Danh sách block theo vùng; quy tắc RTG, lót pháo và cách nhóm vị trí.
- Chính sách bản ghi trùng, trường thiếu và vị trí ngoài phạm vi.
- Nguồn mốc thời gian, ngưỡng cảnh báo và cách xử lý xung đột.
- Đường dẫn đầu ra, chính sách lịch sử và chế độ xuất báo cáo.

Thiếu khóa bắt buộc, kiểu sai hoặc mapping chưa xác nhận phải làm dừng phép kiểm phụ thuộc và nêu rõ câu hỏi. Không âm thầm dùng giá trị mặc định nghiệp vụ. Quy tắc khác nhau giữa các project không được suy ra từ tên block hay mẫu dữ liệu.

## Mốc thời gian dữ liệu

Ghi mốc thời gian cùng nguồn và mức tin cậy trong báo cáo. Dùng nguồn thời gian theo thứ tự do project xác nhận; có thể là thời gian do người dùng nhập, trường thời gian nghiệp vụ trong file, giờ trong tên file theo mẫu đã duyệt như <du_lieu>_<dd-mm-yyyy>_<hhmm>, hoặc ngày sửa file nếu được xác nhận rõ là fallback phù hợp.

Ngày sửa file có thể đổi khi sao chép, tải xuống hoặc lưu lại nên tự nó không chứng minh giờ xuất TOS. Nếu tên file cũ hơn dữ liệu, nguồn mâu thuẫn hoặc mốc bị trễ, ghi cảnh báo; mọi dung sai/ngưỡng phải do project cấu hình. Không tự chọn giữa các nguồn mâu thuẫn hoặc dùng mốc không có ý nghĩa nghiệp vụ đã xác nhận.

## Báo cáo

- Excel và HTML đọc từ cùng một kết quả; mọi chỉ số có đơn vị và cách đếm rõ.
- Báo cáo giữ khả năng lần về dòng nguồn và nêu phạm vi dữ liệu chưa kiểm.
- Nếu xuất HTML ngoại tuyến, mã hóa JSON an toàn và hiển thị giá trị nguồn bằng textContent; không đưa dữ liệu vào innerHTML.
- Đường dẫn đầu ra, hành vi khi file đã tồn tại và quyền lưu lịch sử phải được xác nhận; không ghi đè file gốc hoặc báo cáo cũ.
- Không cộng chỉ số có đơn vị khác nhau. Nếu dùng số tổng, ghi rõ đơn vị và cách khử trùng lặp.

## Đóng gói và môi trường

Chỉ chọn cách đóng gói sau khi biết hệ điều hành, cách chạy, quyền cài đặt và dependency được project chấp thuận. Với PyInstaller, spec có thể cần thu thập import nạp muộn và loại các thư viện chỉ sau khi xác minh ứng dụng không dùng chúng. Mẫu kỹ thuật nằm trong [Kiểm thử, đánh giá độc lập và đóng gói](kiem-thu-dong-goi.md).

Build và thử trong đường dẫn tạm riêng; đối chiếu kết quả với lần chạy trực tiếp cho cùng dữ liệu giả. Kiểm giao diện, CLI, thiếu file và cách báo lỗi nếu các chế độ đó được hỗ trợ. Ghi rõ phần chưa thử. Không đưa dữ liệu sản xuất, thông tin nhạy cảm hoặc cấu hình riêng vào bộ phân phối dùng chung.
