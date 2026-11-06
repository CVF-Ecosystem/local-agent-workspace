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
- Mức nhạy cảm dữ liệu: [Công khai / Nội bộ / Có dữ liệu cá nhân hoặc mật; nêu cách xử lý]
- Phạm vi được giao cho agent phụ: Xem .agent/EXECUTION_PROFILE.json (quyền gọi vai do profile giữ; chưa có grant thì chưa có quyền)
- Ngoại lệ thư mục nguồn cũ: [Không có / thư mục trong project, nhiều thư mục ngăn bằng dấu ; ví dụ: Tai-lieu-cu; Ho-so-2023]

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

## Quyết định operator về sửa lỗi khi bảo trì LAW — 04/11/2026

Áp dụng cho công việc phát triển/bảo trì LAW tại kho nguồn, không thêm quy trình cho việc văn phòng thông thường.

- Nếu sau một tranche sửa lỗi mà lỗi chưa được giải quyết, tập trung audit để xác định chính xác nguyên nhân, sửa và kiểm được kết quả rồi mới chuyển việc. Không chuyển sang việc khác để né lỗi hoặc chia mỗi lỗi kỹ thuật thành tranche mới.
- Audit toàn luồng liên quan, đối chiếu đúng API/môi trường/dữ liệu và bằng chứng thất bại; nếu code chưa đạt thì viết lại phần cần thiết. Review tĩnh hoặc sửa một lệnh chưa thay bằng chứng chạy hết luồng và kiểm đầu ra.
- Giữ lịch sử thất bại, dữ liệu gốc, quyền và tiêu chí đã chốt. Không retry mù hoặc tăng timeout để thay việc tìm nguyên nhân. Nếu cần quyền hay điều kiện ngoài phạm vi, báo đúng blocker; không tự nhận lỗi đã sửa hoặc chuyển QA/debug cho người dùng.

### Đích sản phẩm LAW do operator chốt lại — 06/11/2026

Phần này là ngữ cảnh phát triển kho nguồn. LAW là **văn phòng ảo trung tâm**: Main nhận và đánh giá việc từ user, chọn AI/Agents chuyên trách theo roles/subagents, giao việc, nhận/kiểm/nghiệm thu rồi tích hợp báo cáo hoặc kết quả trước khi giao user. Chuyên viên tự thực hiện chi tiết trong phạm vi, công cụ/quyền và chuẩn đã giao; Main chịu trách nhiệm điều hành và chất lượng bản giao.

CVF hỗ trợ điểm kiểm yêu cầu, phạm vi/quyền, nguồn/revision, bằng chứng và nghiệm thu theo rủi ro; không thay suy luận hay điều khiển từng thao tác của agent. User chọn provider/model; cách diễn đạt, chi tiết và cách làm có thể khác nhưng chuẩn mục tiêu/căn cứ/độ đúng/bảo toàn/quyền/khả năng dùng không được hạ theo model. Kết quả chưa đạt phải sửa hoặc giữ chờ đúng lý do trước khi giao như bản đã nghiệm thu.

Skills/tools/chuyên môn được tích hợp theo packages đã tiếp nhận; tận dụng native thực có, không dựng thêm bản trùng khi native đã đáp ứng. Chỉ bổ sung gap được chứng minh, không tự kích hoạt gói REVIEW/DEFER. DEV chịu code, ca thử, expected, QA và review; khi cần phép thử host thật, DEV chuẩn bị đủ input/thao tác/expected/bằng chứng/điều kiện dừng để operator trung chuyển. Trục roadmap là luồng văn phòng trọn vòng và tiếp việc; sửa tool/checker hay tạo được một file chỉ là phần hỗ trợ có phạm vi.

Operator đã đồng ý chốt baseline r7: năm kết quả là Main tổ chức việc, chuyên viên hoàn thành việc, Main nghiệm thu/giao, sửa/tiếp việc và bản cài dùng được. Roadmap §1.1–1.3 giữ phạm vi, năm hành vi LAW và tiêu chí; §6 áp dụng `roadmap/CVF_ROADMAP_PROGRESS_FORM.md` trong hồ sơ hiện có. Mỗi giao việc phải nối kết quả–gap thực–native/owner tái dùng–điểm nhận/dừng, reviewer xét cả sự cần thiết lẫn tính đúng. Đổi scope/chuẩn phải có quyết định đúng quyền, không tự đóng mốc bằng test xanh. Form CVF chung v1.2 hiệu chỉnh1 đã được tiếp nhận và giao về LAW; giữ nguyên form, bổ sung cách điền riêng theo nhu cầu LAW tại roadmap §6 và dùng các owner/chuẩn nghề hiện hữu. Các phần riêng của LAW không áp đặt sang project khác; việc nhận form không chứng minh runtime, rollout hoặc sản phẩm đã đạt.
