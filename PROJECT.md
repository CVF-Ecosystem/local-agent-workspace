# NGỮ CẢNH DỰ ÁN VÀ HƯỚNG DẪN LÀM VIỆC

File này giữ ngữ cảnh ổn định của project. Quy tắc vận hành chung nằm trong `AGENTS.md`.

## Thông tin dự án

Chỉ điền điều hữu ích và ổn định. Tiến độ hiện tại thuộc về STATE.

- Tên dự án: [Tên]
- Mục đích và người đọc: [Công việc này để làm gì; ai sẽ dùng]
- Đầu ra mong đợi: [Tài liệu, quy trình, biểu mẫu, báo cáo, khác]
- Ngôn ngữ và văn phong: [Ví dụ: tiếng Việt; dùng mẫu hiện có của đơn vị]
- Nguồn / mẫu đã duyệt chính: [Đường dẫn hoặc mục trong index nguồn]
- Ràng buộc quan trọng: [Ràng buộc nghiệp vụ đã xác nhận hoặc giới hạn xử lý dữ liệu]

## Mục đích của workspace

Đây là workspace dựa trên file cho công việc văn phòng và vận hành: đọc tài liệu, viết quy
trình và biểu mẫu, phân tích bảng tính, thỉnh thoảng làm báo cáo HTML. Project cục bộ giữ hồ
sơ làm việc giữa các agent và các phiên. Điều này không có nghĩa mô hình xử lý offline hay file
tự đồng bộ.

## Mặc định hữu ích

Hiểu yêu cầu, dùng ngữ cảnh liên quan, giao kết quả được yêu cầu rồi dừng. Chọn cách làm theo
phán đoán. Hướng dẫn trong `AGENTS.md` dùng chung cho mọi provider và bổ sung, không thay thế,
khả năng native sẵn có. Giới hạn chống lặp vòng nằm trong mục "Giới hạn công việc" của `AGENTS.md`.

Không có chế độ làm việc bắt buộc. Chỉ hỏi điều còn thiếu và ảnh hưởng đến kết quả.

## Nguồn và đầu ra

Bắt đầu từ nguồn người dùng nêu. Cần thêm ngữ cảnh thì dùng index hoặc đọc phần liên quan của
nguồn khác. Dùng lại thông tin đã có khi phù hợp; đọc lại một đoạn nếu nó có thể đã đổi hoặc
kết luận phụ thuộc vào nó.

Dùng mẫu của người dùng khi phù hợp. Ví dụ đi kèm skill chỉ là điểm xuất phát, không phải chính
sách nghiệp vụ đã duyệt. Tách rõ dữ kiện từ nguồn với đề xuất.

Với việc rà soát nội dung, bản nháp trong hội thoại có thể đủ. Khi người dùng yêu cầu file, tạo
file bằng công cụ phù hợp và kiểm tra những điểm cần để dùng. Bản đang làm để trong `working/`,
bản giao hiện hành trong `output/`, bản cũ trong `archive/` khi cần giữ. Đường dẫn sẵn có của
dự án vẫn có thể giữ nguyên. Giữ nguyên nguồn gốc; không tạo thêm bản hay đầu ra khi chưa có lý do.

## Liên tục giữa các phiên

STATE là bản chụp hiện trạng: mục tiêu, đầu ra hiện tại, quyết định đã chốt, việc còn mở và bước
hữu ích tiếp theo. Ghi đè, giữ tối đa khoảng 60 dòng. Ghi điểm kiểm khi phiên sau sẽ bỏ lỡ một thay đổi có ý nghĩa.

HANDOFF giúp phiên khác tiếp tục với đúng file và bước tiếp theo; tùy chọn và thường chứa `None`.
PENDING_LESSONS cũng tùy chọn: chỉ ghi điều đáng dùng lại. Mẹo hoặc ví dụ ổn định có thể thành
skill khi người dùng đồng ý, không tự động sau một lỗi.

## Skills

Index skill là công cụ để tìm, không phải bộ định tuyến cố định hay danh sách phải nạp mỗi phiên.
Chọn theo độ phù hợp, gồm cả lựa chọn làm trực tiếp hoặc dùng khả năng native. Skill quen thuộc
không cần liệt kê lại mỗi lần dùng.

Người dùng quản lý việc thêm, bỏ và viết lại lớn thư viện. `skills/inbox/` vẫn là tùy chọn. Khả năng
riêng của provider có thể ghi chú khi hữu ích, nhưng không sao chép hay giả định có ở provider khác.

## Hoàn thành

Kết quả xong khi đáp ứng đúng phạm vi và định dạng yêu cầu với độ chính xác và khả năng dùng cần
thiết. Một vấn đề cụ thể là lý do để xem lại phần liên quan; còn dư sức hay có thể trau chuốt thêm
thì không phải lý do.
