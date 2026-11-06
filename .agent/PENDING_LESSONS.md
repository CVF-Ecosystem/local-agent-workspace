# Bài học chờ xem xét

## 06/11/2026 — Giữ mục tiêu sản phẩm khi điều phối roadmap

Operator đã chấp thuận tích hợp tại LAW và yêu cầu form dùng chung cho CVF. Phân loại: APPLICATION_GAP của Project Development Application và milestone coverage hiện hữu; không dựng thêm framework/checker hay coi việc bổ sung tài liệu đã ngăn tái diễn.

Quan sát ở LAW: kiến trúc văn phòng còn đúng nhưng điều phối lệch sang Excel/COM, rồi code kiểm soát rời luồng. Bản r7 đặt năm kết quả người dùng nhận ở đầu roadmap, giữ toàn acceptance/gap; chức năng LAW nằm riêng §1.3. Form `roadmap/CVF_ROADMAP_PROGRESS_FORM.md` chuẩn hóa baseline, mốc/đủ điều kiện, brief bốn câu hỏi, đổi phạm vi có authority và kết luận nhiệm vụ/mốc/phát hành. Dùng ngay trong hồ sơ hiện hữu, không thêm sổ cho từng việc; reviewer kiểm giá trị đối với mục tiêu cùng tính đúng.

Nguồn chung đã đối chiếu: Project Development Application, operator-local manifest commit f8175616c, SHA256 d06b62387e015160a77658f333882a2a316d54ffd0421071354cf63a3730dd7a. Đích CVF tiếp nhận là owner chuẩn đó và Product Milestone Coverage Contract; ưu tiên hợp nhất phần thiếu, không nhân đôi quy tắc. Trạng thái ban đầu LOCAL_APPLIED_DOCUMENTATION / NOT_UPSTREAMED được giữ như lịch sử; hiện CVF đã tiếp nhận form v1.2 hiệu chỉnh1, nguồn commit feb691726a3be5bd4b3ac4dc402d22c69bc79235 và giao lại bản LAW. Hiệu quả vẫn EFFECTIVENESS_NOT_PROVEN. Operator làm rõ form là chung: mỗi project bổ sung nội dung riêng theo nhu cầu/tiêu chí đã chốt trong hồ sơ project, không sửa form chung chỉ để khớp nghiệp vụ một project. LAW áp dụng riêng tại roadmap §6, tái dùng LAW-DA01..05 và source/role/artifact owners đã có; không suy việc nhận form là activation, rollout hay nghiệm thu sản phẩm.

Bổ sung từ review Claude r7 ngày 06/11: tiêu chí đã ghi ở mục đích vẫn có thể bị bỏ sót nếu chưa nối tới hàng giao việc/điều kiện đóng và ca cụ thể. Main đã gắn năm hành vi vào 4.1/4.2, gộp bất đồng vào ca (b); form1.1 làm rõ đạt có giới hạn và thời hạn/ngân sách gốc. Đây là sửa áp dụng trong cùng hồ sơ, không tạo thêm chuẩn/learning riêng; chưa có bằng chứng chạy đạt.

Kiểm hiệu quả ở lần thi công kế tiếp: Main dùng form trước giao, reviewer xét liên hệ mục tiêu, và kết quả thực cập nhật đúng mốc/còn thiếu. Mỗi failure phải xác định dependency bị chặn, không thay bằng coverage harness hay tự hạ chuẩn. Đo bằng việc chọn/giao/nhận có giữ mục tiêu trên thực tế; chưa có phép chạy mới cho kết luận này.

## 05/11/2026 — Excel173: sửa component chưa hội tụ thành artifact dùng được

Phân loại: APPLICATION_GAP của learning hội tụ sửa lỗi đã có; bổ sung bằng chứng và cách áp dụng, không tạo framework/skill hay luật nền mới. Phạm vi: phát triển/bảo trì sản phẩm có nhiều component và kiểm native; không thêm thủ tục cho việc văn phòng nhỏ. Theo làm rõ của operator 06/11, đây là bài học của ca artifact Excel173, không biến Excel desktop, COM, số lượt xuất hoặc môi trường test cụ thể thành điều kiện chung của LAW. LAW kiểm soát agent/capability/quyền/nguồn/revision/claim và nghiệm thu kết quả trong host; nó không xây engine Office hay làm thay agent của host.

Nguồn: `working/excel-workflow-quality-20261029/native-final-20261104/evidence/EXCEL173_DANH_GIA_TOAN_DIEN_20261105.md`, revision AUDIT-EXCEL173-20261105-r1, SHA256 `61bc33d4c738db47a9826636d28c9331d4eac9b017701316c5ab77c41b43e1de`; Terra/Sol audit, Astra ACCEPT_AUDIT_AND_PROPOSED_PLAN_WITH_LIMITS. Main chịu trách nhiệm tích hợp và cách giao việc.

Quan sát: shared reader/checker đã sửa nhưng artifact đang giao còn bản cũ; nâng reader thiếu adaptation có thể làm mất guard formula-input. Workbook còn gap công thức đầu vào/vùng in/chuẩn mã trong khi nhiều lượt tập trung harness. Các lỗi lịch sử khác tầng, không chứng minh một nguyên nhân1004 chung. Sổ thời gian còn trộn tầng đo. Đây là counterexample của việc có quy tắc nhưng chưa áp dụng đủ, không chỉ là thiếu lời nhắc.

Cách áp dụng ngay vào brief/HANDOFF hiện hữu của lần sửa tiếp theo:

- Theo đúng kết quả người dùng: một owner tích hợp, một candidate revision cho workbook/viewer/validator/oracle; đối chiếu toàn điều kiện mốc và phần còn thiếu. Không đóng tiến độ sản phẩm theo số API/tranche đã sửa.
- Truy từ source đã sửa đến artifact thật và kết quả engine: chỉ rõ fix đã/chưa được build vào bản nào, phụ thuộc/adaptation nào phải giữ, phép kiểm chạy trên đúng bytes nào. Source test và HTML thử riêng không thay acceptance artifact giao.
- Trước native phải có phép đối chứng tối giản và nhánh kết quả/dừng hữu hạn. Lỗi khác tầng thì phân loại lại; không tiếp tục chỉ thêm logging cùng đường chưa phân biệt được nguyên nhân. Thiếu UI của agent không tự là nguyên nhân lỗi COM.
- Giữ nguyên lịch sử và đo chi phí đúng tầng/đơn vị; helper kết thúc không chứng minh Excel đã thoát. Không đổi tên lỗi, agent hoặc tranche để reset lịch sử, ngân sách hay unknown cleanup.
- Reviewer kiểm giá trị phân biệt của phép thử, tính tích hợp và toàn đầu ra theo claim, bên cạnh source/hash. Giữ technical QA thuộc đội dev, không chuyển debug cho noncoder hoặc hạ tiêu chí.

Điểm kiểm hiệu quả: khi tiếp tục giao chính file Excel173, brief phải thể hiện các điều trên và cần bằng chứng trên đúng candidate về tính/lưu-mở lại/export/viewer/bảo toàn theo claim. Với mốc LAW chung, kiểm hiệu quả của đường kiểm soát actor/capability/quyền/nguồn/revision/claim và cách ghi giới hạn giữa các host; không dùng sự cố một harness làm đại diện. Có báo cáo hoặc sửa hướng dẫn chưa chứng minh ngăn tái diễn. Hiện trạng: LOCAL_RECORDED / BRIEF_APPLIED_W44_r6.13 / EFFECTIVENESS_NOT_PROVEN; Excel173 vẫn NOT_MET, cause/cleanup UNKNOWN.

Quan hệ upstream: bổ sung cho `LAW_REPAIR_CONVERGENCE_LEARNING_2026-11-04.md` đang ở CVF cha dạng candidate. Lượt này không sửa hoặc gửi thêm file sang CVF, không suy đã được parent tiếp nhận/triển khai, không đổi rule/checker/registry/grant. Khi tiếp nhận dùng owner hiện hữu, tránh tạo learning trùng.

Khi có ứng viên, ghi nguồn, phạm vi dự kiến và kết quả xử lý hoặc liên kết quyết định. Đề xuất chung/riêng hay nhãn đã xử lý không tự chứng minh đã tích hợp hoặc tiếp nhận; không tự chuyển, xóa đầu ra project.

Operator05/11 xác nhận CVF gốc tự nâng learning, LAW tự ghi nhớ và tiếp sửa. Brief W44/r6.13 đã áp dụng tích hợp đúng pair/giữ adaptation/manifest không cấp whitelist/control hữu hạn/đơn vị chi phí; Astra PRE nhận sau làm rõ. Đây mới là bằng chứng áp dụng ở giao việc, chưa phải kết quả sản phẩm hoặc chứng minh ngăn tái diễn.
