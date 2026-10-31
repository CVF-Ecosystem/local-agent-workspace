---
name: container-yard-check
description: Dùng cho công cụ dữ liệu bãi từ TOS; quy tắc riêng cần project xác nhận/cấu hình. Không dùng cho báo cáo tàu/sà lan hoặc nghiên cứu pháp lý. / Use for TOS yard tools; excludes vessel reports and legal research.
metadata:
  version: "0.1.1"
---

# Công cụ kiểm tra bãi container từ dữ liệu TOS

Hướng dẫn này phục hồi các khái niệm và bài học kỹ thuật trong snapshot ứng viên đã ghi ở hồ sơ tiếp nhận. Ví dụ trạng thái, cách nhóm vị trí, mã ISO, mức cảnh báo và cách lấy mốc dữ liệu là mẫu tham khảo có điều kiện, không phải quy tắc chung cho mọi TOS. Quy tắc và giá trị riêng phải được project xác nhận rồi cấu hình.

## Phạm vi

- Dùng để xây dựng hoặc rà soát công cụ đọc file TOS, chuẩn hóa vị trí, kiểm tra chất lượng dữ liệu và tính cảnh báo bãi theo quy tắc đã xác nhận.
- Tách việc kiểm dữ liệu vị trí bãi khỏi báo cáo tàu, sà lan, năng suất và sự cố của skill port-operations-reports.
- Không suy ra block, tuyến tàu, hướng hàng, nhóm hàng hay ngưỡng từ ví dụ hoặc dữ liệu chưa xác nhận. Khi dữ liệu thiếu hoặc quy tắc chưa rõ, nêu phần cần xác nhận và dừng phép kiểm phụ thuộc.
- Giữ đơn vị riêng cho số cont, bay, vị trí và từng loại cảnh báo; không cộng các đơn vị khác nhau thành một tổng.
- Không đưa dữ liệu thật, mã nội bộ hoặc thông tin nhạy cảm vào skill dùng chung. Dùng dữ liệu giả hoặc đã che trong ca thử.

## Trước khi viết mã: chốt 5 điều

Ghi câu trả lời vào cấu hình hoặc tài liệu riêng của project. Nếu một câu trả lời còn thiếu, không tự chọn mặc định cho phép kiểm phụ thuộc.

1. **Ý nghĩa trạng thái TOS:** một số TOS dùng Stacking cho cont đang ở ô, Incoming cho cont đã làm thủ tục nhưng chưa hạ bãi, và Outgoing cho cont đã nâng khỏi ô nhưng chưa gate out. Đây là các nghĩa thường gặp trong snapshot, cần đối chiếu với TOS thực tế. Chỉ bản ghi đã xác nhận đang chiếm ô mới làm căn cứ cho phép kiểm theo vị trí. Trạng thái chưa rõ phải đưa vào danh sách cần xác nhận, không tự coi là đang ở hoặc đã rời bãi. Nhầm Incoming/Outgoing là lỗi nặng vì có thể tạo trùng ô, lót pháo hoặc lẫn tàu giả.
2. **Tên block và tiền tố:** xác nhận danh sách block, thứ tự Block-Bay-Row-Tier và cách TOS ghi. TOS có thể bỏ một tiền tố chữ đã có trong tên block; chỉ ánh xạ khi project xác nhận. Không loại vị trí chỉ vì block chỉ có số, và không tự thêm tiền tố.
3. **RTG và lót pháo:** xác nhận block nào dùng quy tắc RTG, nhóm theo Bay hay Row, block nào có quy tắc lót pháo, định nghĩa chân/Tier 1 và các trường hợp vi phạm. Các tên block, nhóm thiết bị và mức cảnh báo là cấu hình riêng.
4. **Hàng/rỗng và mã ISO:** xác nhận nguồn của F/E, hướng nhập/xuất, bảng quy đổi ISO và cách xử lý container đặc biệt. Snapshot nêu ví dụ 22T0/F thành FT20, 22T0/E thành ET20; cũng nêu 45R0 và 22R0 là ví dụ cont lạnh, không phải tank. Đây là ví dụ nguồn, không dùng làm bảng quy đổi của project nếu chưa đối chiếu tài liệu phù hợp. Xác nhận riêng quy ước cỡ và TEU.
5. **Mốc thời gian dữ liệu:** xác nhận trường thời gian nào có nghĩa nghiệp vụ và cách xử lý nguồn mâu thuẫn. Nếu project chấp nhận giờ trong tên file, có thể quy định mẫu như <du_lieu>_<dd-mm-yyyy>_<hhmm>.xlsx. Ngày sửa file chỉ là dấu thời gian kỹ thuật; không dùng làm giờ xuất nếu chưa được project xác nhận. Mọi ngưỡng trễ phải cấu hình.

## Quy trình

1. Xác nhận nguồn dữ liệu, phạm vi, đầu ra và quyền xử lý; chỉ đọc lượng dữ liệu cần thiết. Không dùng file thật để thử nếu chưa được cho phép.
2. Tạo một bảng chuẩn hóa duy nhất có liên kết về dòng nguồn. Giữ giá trị vị trí gốc, giá trị chuẩn hóa, trạng thái xác thực và lý do của thay đổi.
3. Tách đọc, chuẩn hóa, phân tích và xuất. Mọi phép kiểm theo chỗ container chiếm phải dùng cùng một tập bản ghi đã xác nhận là đang ở ô; trạng thái chưa rõ được báo riêng.
4. Đặt quy tắc riêng trong cấu hình có kiểm tra kiểu và giá trị. Không âm thầm dùng giá trị mặc định cho khóa bắt buộc còn thiếu hoặc sai; dừng phép kiểm phụ thuộc và nêu khóa cần xác nhận.
5. Excel và HTML phải lấy từ cùng kết quả phân tích. Ghi rõ đơn vị chỉ số; HTML ngoại tuyến phải hiển thị dữ liệu nguồn như văn bản an toàn.
6. Dùng dữ liệu giả kiểm ca bình thường, sai, thiếu dữ liệu, đơn vị không tương thích và ngoài phạm vi. Chỉ chạy trên dữ liệu thật, đóng gói hoặc sửa ứng dụng khi người dùng cho phép; đối chiếu cảnh báo với người am hiểu nghiệp vụ.
7. Bàn giao file đầu ra, phiên bản cấu hình, nguồn và mốc dữ liệu, kiểm tra đã chạy, phần chưa kiểm và mọi quy tắc còn cần xác nhận. Không ghi đè dữ liệu hoặc báo cáo gốc.

## Quy tắc nghiệp vụ có thể cấu hình

Các cách nhóm và mức màu dưới đây là ví dụ trong snapshot. Chỉ bật khi project xác nhận; mức ĐỎ, CAM và VÀNG cũng là cấu hình, không phải chuẩn áp dụng chung.

| Phép kiểm | Cách nhóm tham khảo | Ví dụ cần xác nhận |
|---|---|---|
| Lẫn tàu/chuyến và cảng đích | Block thường có thể nhóm theo Bay; block RTG có thể nhóm theo Row trong Bay | Mức tham khảo ĐỎ; dùng kế hoạch khai báo làm chuẩn nếu project xác nhận; thiếu tàu thì không tự gắn nhãn sai |
| Lẫn hướng hoặc hàng nhập | Cùng phạm vi nhóm đã xác nhận | Chỉ so sánh hướng từ các trường và bí danh đã được project duyệt |
| Lẫn nhóm trọng lượng H/M/L hoặc rỗng chung chân | Cùng phạm vi nhóm đã xác nhận | Mức tham khảo CAM; cách phân nhóm và xử lý cont đặc biệt cần cấu hình |
| RTG lẫn nhập/xuất | Có thể xét cùng Row và khác Row trong một Bay RTG | Mức tham khảo ĐỎ khi cùng Row, CAM khi khác Row; project xác nhận đơn vị kiểm và mức tương ứng |
| Lót pháo | Chân Block-Bay-Row trong block đã xác nhận | Ví dụ quy tắc nguồn xét Tier 1, trạng thái hàng/rỗng, hàng đặt trên rỗng ở tầng giữa và dữ liệu ô bên dưới. Snapshot nhắc năm loại ca kiểm nhưng không liệt kê đủ từng loại; project phải xác định danh sách trước khi bật |
| Trùng ô | Ô Block-Bay-Row-Tier | Chỉ xét các cont đã xác nhận đang chiếm ô; trạng thái chờ hoặc đã rời ô không được tính như cont đang ở |

Các quy tắc nhóm, trạng thái chiếm ô và mức cảnh báo phải được kiểm trên từng project. Không cộng số cont, bay, vị trí hoặc cảnh báo theo loại vào một tổng không có cùng đơn vị.

## Sai lầm đã gặp

- Coi mọi dòng trong file là cont đang ở ô; cần loại các trạng thái chờ hoặc đã rời ô theo mapping TOS đã xác nhận.
- Bỏ vị trí có block chỉ ghi số; tiền tố có thể bị TOS bỏ, nhưng chỉ được sửa theo ánh xạ đã cấu hình.
- Phân loại cont đặc biệt chỉ theo ISO; ví dụ tank hàng/rỗng có thể có nhãn khác nhau, còn mã lạnh cần đối chiếu bảng phù hợp.
- Cộng cont, bay và vị trí thành một tổng cảnh báo; mỗi loại có đơn vị riêng.
- Lấy ngày sửa file làm mốc dữ liệu mà không đối chiếu nguồn thời gian nghiệp vụ.
- Dùng dấu inch thay cho feet trong nhãn cỡ cont; ghi đúng ký hiệu đơn vị theo quy ước của project.
- Báo file đã xuất nhưng không nêu đường dẫn đầy đủ khi ứng dụng chuyển sang thư mục dự phòng.
- Coi bộ kiểm thử xanh là bằng chứng logic nghiệp vụ đúng; cần ca đối chiếu và đánh giá độc lập.

Chi tiết thuật ngữ, bộ ca kiểm và cách tách cấu hình nằm trong [Nghiệp vụ bãi](references/nghiep-vu-bai.md), [Kiểm thử, đánh giá và đóng gói](references/kiem-thu-dong-goi.md) và [Kiến trúc ứng dụng](references/kien-truc-ung-dung.md).
