# Luồng Main cho nghiên cứu nhiều bước

Phần này điều chỉnh ý định stage map và exclusions của ARS `ARS:academic-pipeline/SKILL.md`; không nhập entry, ledger, passport, hook hay script gốc. Đây là đường dùng theo LAW hiện có, không tạo bộ điều phối thứ hai.

## Ánh xạ phương pháp vào vai của project

Main chọn gói từ chỉ mục skill của project khi yêu cầu cần nguồn/phương pháp học thuật; đọc entry, common-standard và module cần dùng. Không cần thêm một vai native cho mỗi tên phương pháp trong tài nguyên ARS. Gói là chuyên môn bổ sung cho các vai có thật, không đăng ký vai hoặc cấp quyền gọi.

| Vai thực tế | Phần việc và module được giao | Bằng chứng cần giữ |
|---|---|---|
| Main | Chốt yêu cầu/nguồn/phạm vi, chọn research/writing/review; giữ quyết định, phiên bản và tích hợp. Việc nhỏ xử lý trực tiếp đúng module. | Yêu cầu hiện hành, lý do chọn phương pháp, quyền/tool/path có thật và bản kết quả hiện hành. |
| Scout, chỉ khi cần | Khảo sát/kiểm nguồn theo research và common-standard; chỉ đọc/tìm trong scope được cấp, đề nghị Main bổ sung khi thiếu. | Nguồn/bản/phần đã đọc, locator, mâu thuẫn và giới hạn. Không mặc nhiên có mạng hoặc quyền ghi. |
| Worker | Tổng hợp chứng cứ, đề cương/viết/sửa theo research/writing, dùng nguồn và quyết định Main giao; trả bản mới trong vùng output được phép. | Candidate, revision nguồn, module đã đọc/được cấp, phần thiếu/suy luận và tác giả phần sửa thực tế. |
| Reviewer riêng | Kiểm candidate đúng revision cùng căn cứ theo review/common-standard, trả finding có locator và phần đúng cần giữ; không nhận thay user. | Invocation/return của reviewer thực, input revision, finding/giới hạn. Một lượt Main/Worker tự soát chỉ ghi self-review. |

Model/effort và quyền lấy từ cấu hình/quyền hợp lệ của chính project và khả năng host quan sát được, không từ tên module hoặc cấu hình agent bảo trì. Main giao cùng binding entry/module, source/candidate revision, vùng đọc/ghi và điều phải giữ; dùng TASK/RESULT/owner hiện có khi đường thực thi yêu cầu, không tự tạo schema riêng. Scope/revision đổi phải đối chiếu lại phần phụ thuộc. Thiếu role/tool/quyền thì giữ phần đó chờ và báo rõ; không giả lập nhiều vai trong một lời trả lời để nhận review độc lập.

Chỉ mục có gói cài không chứng minh host tự nạp hoặc dispatch được. Đọc tường minh entry/module ở chế độ REVIEW chỉ là dùng thử trong project đã được giao; native export vẫn theo eligibility/confirm. Operator có thể chuyển prompt/phản hồi giữa các host để kiểm thử; việc họ chuyển kết quả giữa Worker và Reviewer bằng tay không chứng minh Main tự điều phối vòng đó.

## Các bước công việc

1. **Nhận việc:** ghi câu hỏi/đầu ra, corpus và scope quyền, chuẩn chung hoặc profile trường/tạp chí được xác nhận, citation/format, revision ứng viên và owner. Yêu cầu nhỏ thì xử lý thẳng ở module tương ứng.
2. **Lập nghiên cứu:** dùng research question và architect khi câu hỏi/phương pháp chưa rõ. Đề xuất cần quyết định thực của người nghiên cứu thì trả Main; không tự coi gợi ý FINER hay thiết kế là phê duyệt.
3. **Đọc và tổng hợp:** giữ bản nguồn/mức đọc/locator, kiểm claim, matrix và mâu thuẫn. Nguồn local-only không tạo lượt tìm ngoài; nguồn chưa đọc đủ không được nói như full text.
4. **Viết:** chọn cấu trúc theo loại bài, map luận điểm tới evidence, viết đúng trạng thái phương pháp, citation hai chiều và phần còn thiếu. Không lấp số liệu giả để tròn bài.
5. **Review và sửa:** review có căn cứ trên đúng revision và nguồn. Lưu finding, response và v2 riêng nếu v1 đã là evidence; giữ phần đã chốt, sửa đúng phạm vi. Một lần self-review phải được ghi đúng là self-review.
6. **Tiếp phiên:** bàn giao binding candidate/module, source revision, bản thảo hiện hành, quyết định, vấn đề mở và owner theo hồ sơ LAW; phiên mới đối chiếu trước khi tiếp. Kết quả đến muộn, timeout hoặc cancel phải đối soát trước retry.

Chỉ nhận một mốc sản phẩm khi toàn acceptance của mốc có bằng chứng. Xong một bước hoặc một tranche không đồng nghĩa xong pilot. Danh mục phép thử và mốc thuộc roadmap AC của LAW, không sao chép vào project như một quy trình bắt buộc.
