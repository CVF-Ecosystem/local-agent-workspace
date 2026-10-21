# Kiểm đầu ra Scout / Scout result checks

- Có mục tiêu đã khảo sát và phạm vi thực đọc; không tự mở rộng quyền.
- Mỗi nguồn nêu path/locator, SourceID và revision khi tồn tại; thiếu thì ghi thiếu.
- Tách dữ kiện quan sát, suy luận và đề xuất cập nhật sổ.
- Ghi rõ file không đọc được, link ra ngoài phạm vi hoặc nguồn có thể đã đổi.
- Main kiểm snapshot nguồn trước khi giao delta cho writer.
- Khi thử thi công LAW, ghi model/effort yêu cầu và thực tế quan sát được, phạm vi/thiếu sót của khảo sát; không coi preset trong config là bằng chứng chất lượng.

The result must identify its scope, source locations and unresolved gaps.
