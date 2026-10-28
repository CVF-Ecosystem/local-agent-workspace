# Khái niệm nghiệp vụ và câu hỏi xác nhận

Đây là khung tham khảo, không phải đặc tả của một cảng. Các nghĩa trạng thái, phép nhóm, mã và mức cảnh báo dưới đây là mẫu đã xuất hiện trong snapshot nguồn; project phải đối chiếu chúng với TOS, tài liệu nghiệp vụ hoặc người phụ trách trước khi bật.

## Thuật ngữ

| Khái niệm | Nghĩa tham khảo | Việc cần xác nhận |
|---|---|---|
| Block-Bay-Row-Tier | Các thành phần thường dùng để nhận diện vị trí bãi | Thứ tự, dấu phân cách, số bắt đầu, định dạng hợp lệ và mã ngoài bãi |
| Hướng hàng | Ví dụ: Export, Import, Storage Empty | Cột nguồn, bí danh và ý nghĩa từng giá trị |
| F/E | Nhãn hàng/rỗng trong một số nguồn TOS | Cột nguồn, quy tắc viết hoa và cách xử lý giá trị lạ |
| Stacking | Một số TOS dùng cho cont đang nằm tại ô | Chỉ dùng làm trạng thái chiếm ô khi project xác nhận |
| Incoming | Ví dụ trạng thái cho cont đã làm thủ tục nhưng chưa hạ bãi; vị trí có thể chỉ là kế hoạch | Xác nhận trạng thái, thời điểm nhập thực tế và cách đưa vào phạm vi |
| Outgoing | Ví dụ trạng thái cho cont đã nâng khỏi ô nhưng chưa gate out | Xác nhận khi nào ô được coi là trống và cách đưa bản ghi vào phạm vi |
| RTG | Cẩu khung bánh lốp; block RTG có thể cần phép nhóm theo Row trong Bay khác vùng thường | Block nào thuộc vùng RTG, quy tắc Bay/Row nào áp dụng |
| Lót pháo | Ví dụ thường gặp là cont rỗng ở Tier 1 làm đế cho chân hàng ở khu vực được chỉ định | Block áp dụng, yêu cầu Tier, trạng thái hàng/rỗng và danh sách ca vi phạm |
| Tàu chuẩn của vị trí | Tàu/chuyến được phân cho một phạm vi vị trí | Nguồn kế hoạch, thời điểm áp dụng và cách xử lý thiếu tàu |
| Trọng lượng H/M/L | Nhóm nặng/vừa/nhẹ trong một số quy tắc xếp | Nguồn trường, ranh giới nhóm và phạm vi phải đồng nhất |
| Chuyến nhập/xuất | Các trường chuyến vào và ra có thể cùng hoặc khác nhau | Cột dùng để gom nhóm, bí danh và cách xử lý lệch chuyến |
| Thời điểm dữ liệu | Mốc báo cáo hoặc mốc xuất file | Nguồn có ý nghĩa nghiệp vụ, múi giờ, thứ tự ưu tiên và cách xử lý mâu thuẫn |

## Hàng hóa, ISO và cỡ container

Snapshot nguồn nêu một số ví dụ có điều kiện: 22T0/F được ánh xạ sang FT20, 22T0/E sang ET20; 45R0 và 22R0 được nêu làm ví dụ container lạnh, không phải tank. Chỉ dùng các mã này khi bảng ISO phù hợp và project xác nhận ánh xạ. Không suy nhãn từ một phần mã.

Snapshot cũng dùng quy ước 20 feet = 1 TEU, 40/45 feet = 2 TEU và gộp 45 feet vào nhóm 40 feet. Đây là ví dụ quy ước đếm trong nguồn, cần project xác nhận đơn vị báo cáo và bảng mã đang dùng. Ký hiệu feet cần giữ đúng quy ước trình bày của project.

## Tiền tố block bị thiếu

TOS có thể xuất block mà thiếu một tiền tố chữ. Nếu project xác nhận một quy tắc như “12-...” tương ứng một block bắt đầu bằng tiền tố chữ, hãy lưu ánh xạ hẹp trong cấu hình và giữ nguyên vị trí gốc. Không tự thêm tiền tố chỉ vì block chỉ có số; không biến đổi chuỗi không thuộc mẫu đã duyệt, chẳng hạn một mã bắt đầu bằng “120”. Mã ngoài bãi cũng cần được phân biệt với vị trí sai.

## Phạm vi phân tích và đối chiếu dòng

Tách các nhóm nghiệp vụ theo cấu hình đã xác nhận, có thể gồm hàng xuất đủ điều kiện, Incoming, Outgoing, hàng lưu lâu, ngoài bãi, vị trí lỗi, thiếu mã container và nhóm còn lại. Ngưỡng lưu lâu, cách khử trùng lặp và thứ tự phân loại đều cần project xác nhận. Một dòng chỉ thuộc nhóm theo đúng điều kiện đã định nghĩa; bảng đối chiếu phải cho thấy dòng nguồn được phân loại hoặc loại trừ thế nào. Không dùng ngưỡng ví dụ của project khác.

## Khảo sát dữ liệu trước khi viết mã

Tạo bảng mô tả có thể đối chiếu: danh sách cột và sheet; bảng chéo Trạng thái × Hướng × F/E; các tiền tố block; ISO × F/E; vị trí không phân tích được; và các mốc thời gian có thể dùng. Mỗi giá trị lạ là câu hỏi cần xác nhận, không phải căn cứ để tự đoán quy tắc.

## Nhóm phép kiểm có thể cấu hình

Chỉ bật phép kiểm khi định nghĩa và nguồn dữ liệu đủ để kiểm chứng:

- Vị trí hoặc định dạng không hợp lệ; giữ giá trị gốc và ghi lý do.
- Nhiều container ở cùng ô, chỉ theo tập trạng thái đã xác nhận đang chiếm ô.
- Pha trộn tàu, chuyến, cảng đích hoặc hướng hàng trong phạm vi do project chọn.
- Quy tắc RTG, lót pháo hoặc vùng xếp chồng theo cấu hình riêng.
- Nhãn hàng phụ thuộc mã, loại container, F/E hoặc tổ hợp trường.
- Dữ liệu trễ, thiếu hoặc không nhất quán theo ngưỡng và mốc đã xác nhận.

Định nghĩa riêng từng cảnh báo và đơn vị đếm. Không cộng số container, vị trí, bay hoặc nhóm cảnh báo vào một tổng không cùng đơn vị. Nếu dữ liệu thiếu hoặc đơn vị không tương thích, giữ kết quả ở trạng thái chưa đủ căn cứ và nêu phần cần xác nhận.

## Taxonomy lót pháo tham khảo từ ứng dụng đã dùng

Nguồn bổ sung là ứng dụng V4.2.1, module dunnage.py trong thư mục analysis của ứng dụng nguồn, bảng `REASON_TITLES` (dòng18–23); các ca liên quan ở hai file test_core.py và test_v421_fixes.py trong bộ test của ứng dụng. Đây là taxonomy của công cụ, **không phải chuẩn ngành**. Chỉ áp dụng sau khi project xác nhận block lót pháo, tập trạng thái thực sự chiếm ô, F/E và quy tắc Tier.

| Mã mẫu | Ý nghĩa trong ứng dụng nguồn | Điểm phải xác nhận trước dùng |
|---|---|---|
| T1_DIRECT | Hạ thẳng Tier1, chưa kê pháo | Vùng/tình huống nào yêu cầu có đế rỗng |
| T1_CARGO | Bản ghi Tier1 là container hàng | Cột F/E và tập bản ghi đang chiếm ô có đúng không |
| T1_MISSING | Tier1 trống dữ liệu trong tập đang kiểm | Là thiếu bản ghi, không tự kết luận ngoài thực địa không có container |
| MID_EMPTY | Hàng đè lên rỗng ở Tier giữa | Cách xác định chân/đỉnh và các Tier nằm giữa trong vùng áp dụng |
| MID_MISSING | Khuyết dữ liệu Tier giữa | Phạm vi dữ liệu đủ tới đâu; phân biệt thiếu dữ liệu với kết luận vị trí thực |

Không dùng bản ghi Outgoing làm bằng chứng đang chiếm ô nếu project đã xác nhận trạng thái ấy đã nâng khỏi ô. Trường hợp nhiều điều kiện đồng thời phải đối chiếu thứ tự ưu tiên của công cụ và yêu cầu project; bảng này không tự quy định cách gộp mã hoặc mức màu cho mọi bãi.
