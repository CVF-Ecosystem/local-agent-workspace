# I04 — Xác minh nguồn và claim

**Nguồn điều chỉnh:** ARS `ARS:deep-research/agents/source_verification_agent.md`, Core, factual claims, existence/outcome và limitations. Không dùng hierarchy I–VII chung, DOI/API lookup mặc định, tỷ lệ spot check hay nhãn `FABRICATED` tự động.

Đánh giá bốn trục tách biệt:

| Trục | Câu hỏi kiểm | Kết quả trung thực |
|---|---|---|
| Nhận diện | Bản này là tài liệu nào, tác giả/năm/venue/DOI có khớp? | Đã đối chiếu trên bản cụ thể, chỉ metadata match, lệch metadata, chưa xác minh hoặc lỗi truy cập |
| Mức đọc | Có metadata, abstract, snippet, trang/đoạn full text nào? | Ghi phần đã đọc và phần chưa đọc; không giả trang/phụ lục |
| Hỗ trợ claim | Đoạn/figure/table nào thực sự nói gì? | Trực tiếp, suy luận có điều kiện, phản chứng, không hỗ trợ hoặc chưa đủ đọc; kèm locator |
| Chất lượng/phù hợp | Phương pháp, mẫu, bối cảnh, giới hạn, xung đột lợi ích/tình trạng nguồn có ảnh hưởng? | Nhận định theo RQ và chứng cứ đã có; điều chưa kiểm tách riêng |

Không tìm thấy trong một chỉ mục, ngày xuất bản lạ hoặc DOI lỗi không đủ để kết luận giả. Nếu có bằng chứng mâu thuẫn về danh tính, ghi cụ thể và giữ nhiều giả thuyết cho tới khi kiểm. Venue hoặc danh tiếng tác giả không thay đánh giá claim/method. Đính chính/rút bài/bản thay thế là observation có nguồn thông báo, thời điểm và claim bị ảnh hưởng; không sửa âm thầm bản đã lưu.

Mẫu finding: `Claim + bản thảo/revision → SourceID/revision + locator + mức đọc → điều nguồn thực nói → verdict có giới hạn → phần cần kiểm/sửa`. Review thiếu nguồn thì nói chưa kiểm; không dựng citation hoặc quote từ metadata.
