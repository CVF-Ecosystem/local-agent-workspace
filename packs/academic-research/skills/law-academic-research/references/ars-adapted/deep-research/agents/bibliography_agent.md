# I03 — Chiến lược tìm và chú giải tài liệu

**Nguồn điều chỉnh:** ARS `ARS:deep-research/agents/bibliography_agent.md`, Core và Search Steps 1–4, phần đầu Step 5. Không mang API Semantic Scholar, resolver, corpus passport hay quota tìm kiếm. Main là đầu mối duy nhất mở nguồn ngoài theo scope/quyền được giao.

1. **Thông số:** từ RQ xác định khái niệm đồng nghĩa, phạm vi thời gian/ngôn ngữ/loại tài liệu, database/domain **được phép**, từ khóa/Boolean nếu phù hợp. Grey literature, preprint hoặc luận văn được phân loại theo mục đích, không tự động loại chỉ vì kém chuẩn hơn bài journal.
2. **Thực thi có dấu vết:** nếu được mở tìm kiếm, ghi nơi tìm, câu truy vấn, thời điểm, filters và kết quả quan sát; nếu chỉ corpus local thì ghi “tìm trong corpus đã cung cấp”, không nói đã tìm database. Lỗi truy cập/zero hit/metadata chỉ là trạng thái quan sát, không tự thành không tồn tại hoặc giả mạo.
3. **Tiêu chí chọn:** áp tiêu chí đã thống nhất cho phạm vi này; nếu là tổng quan hệ thống cần protocol và record screening riêng. Với narrative review, ghi lý do chọn tài liệu theo RQ và giới hạn độ bao phủ, không dùng nhãn PRISMA/systematic một cách ngầm định.
4. **Hai lượt xem:** metadata/title/abstract cho ứng viên, rồi toàn văn/phần đọc thực nếu có quyền. Ghi mức đọc và lý do chưa đọc; không dùng abstract làm chứng cứ cho claim chỉ thấy trong full text. Trùng DOI/title chỉ là ứng viên dedup, xem phiên bản/preprint/published và cùng dữ liệu nghiên cứu trước khi gộp.
5. **Chú giải:** mỗi mục có SourceID/bản, citation metadata kiểm được, RQ liên quan, phương pháp/mẫu/bối cảnh, phát hiện được đọc, giới hạn, locator và trạng thái claim. Giữ mục chưa dùng tách khỏi danh mục trích trong bản viết.

Đầu ra: strategy thực tế, danh sách đã xem ở từng mức, annotated bibliography có locator và khoảng trống nguồn cần Main quyết. Không tự lấp gap bằng web search hoặc tải paper vì gợi ý từ ARS.
