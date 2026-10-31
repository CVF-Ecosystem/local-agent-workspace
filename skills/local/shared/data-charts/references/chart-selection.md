# Chọn biểu đồ theo dạng dữ liệu

Gợi ý để quyết định cách trình bày; không phải quy tắc bắt buộc.

| Muốn cho người đọc thấy | Thường phù hợp | Tránh |
|---|---|---|
| So sánh giữa các nhóm | Cột ngang (nhãn dài) hoặc cột dọc, sắp theo giá trị | Biểu đồ tròn nhiều lát |
| Thay đổi theo thời gian | Đường; cột nếu chỉ vài kỳ | Cột xếp chồng nhiều nhóm khó so sánh |
| Cơ cấu (từ 5 phần trở xuống) | Cột xếp chồng, vành khuyên hoặc tròn | 3D, quá nhiều lát |
| Cơ cấu thay đổi theo kỳ | Cột xếp chồng, ghi tổng trên đầu cột | Nhiều lớp màu gần nhau |
| Một con số quan trọng | Thẻ KPI kèm kỳ so sánh | Đồng hồ kim trang trí |
| Danh sách chi tiết, cần tra số | Bảng, thêm thanh nhỏ hoặc bộ lọc nếu cần | Biểu đồ khi người đọc cần số chính xác |
| Quan hệ giữa hai đại lượng | Biểu đồ phân tán, chỉ khi có nhiều điểm | Nối điểm bằng đường |

Mẫu `assets/basic-charts.html` có sẵn thẻ KPI, đường, cột ngang, cột xếp chồng,
vành khuyên và bảng kèm thanh. Dạng khác (phân tán, bản đồ, biểu đồ mạng) cần dựng riêng.

Chỉ so sánh trực tiếp khi cùng đơn vị, định nghĩa, cách xác định kỳ và phạm vi thu thập tương đương. Với tỷ lệ có mẫu số khác nhau, ghi n/N từng nhóm; tỷ lệ gộp bằng tổng n chia tổng N, không lấy trung bình các tỷ lệ. Ví dụ 1/2 và 9/10 cho tỷ lệ gộp 10/12 ≈ 83,3%, còn trung bình hai tỷ lệ là 70%. Thiếu căn cứ thì tách bảng hoặc ghi chưa so sánh được; không suy diễn nhân quả.

## Điểm dễ sai

- Cột bắt đầu từ 0. Biểu đồ đường có thể cắt trục nhưng phải ghi rõ điểm bắt đầu của trục.
- Mỗi biểu đồ nêu một thông điệp; tiêu đề cho biết điều cần thấy, không chỉ tên chỉ tiêu.
- Ghi đơn vị, kỳ báo cáo và nguồn. Ô thiếu dữ liệu hiện "—" và ngắt đường, không vẽ như 0.
- Dùng ít màu (khoảng 5 trở xuống) và thêm nhãn trực tiếp để không chỉ dựa vào màu.
- Số tồn cuối kỳ không cộng qua các kỳ; tỷ lệ tính từ tổng tử số chia tổng mẫu số.
- Tỷ lệ phần trăm trên mẫu nhỏ dễ gây hiểu nhầm: kèm số tuyệt đối.
- Biểu đồ cho thấy xu hướng, chưa chứng minh nguyên nhân.
