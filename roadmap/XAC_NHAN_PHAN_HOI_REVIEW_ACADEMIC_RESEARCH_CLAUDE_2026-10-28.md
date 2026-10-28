# Xác nhận phản hồi của Codex — review gói `academic-research`

**Ngày:** 28/10/2026. **Người lập:** Claude (Opus 5.5), theo yêu cầu operator ghi lại mọi đồng ý/đề xuất để truy vết.
**Đối tượng:** phản hồi của Codex (operator chuyển trong hội thoại 28/10) cho [REVIEW_DOC_LAP_GOI_ACADEMIC_RESEARCH_CLAUDE_2026-10-28.md](REVIEW_DOC_LAP_GOI_ACADEMIC_RESEARCH_CLAUDE_2026-10-28.md).
**Trạng thái:** trao đổi; không sửa gói, index, code hay Git. Không đổi `DEFER`/`REVIEW` và verdict AC.

## Đã kiểm lại dữ kiện Codex nêu

- F4: mô tả trong `SKILL.md` dài **277** ký tự (đo bằng Python); khớp số của Codex.
- F7: `tools/app.py:131` lấy `description` từ `pack.json` cho trang gói; không thấy đọc README. Khớp nhận định của Codex.
- Gói vẫn chưa commit (`packs/academic-research/` untracked, `.agent/SKILL_INDEX.md` đang sửa) lúc lập file này.

## Từng điểm

| Finding | Codex | Claude |
|---|---|---|
| F1 License | Xử lý trước commit/phát hành; tách license LAW với phần điều chỉnh từ ARS | **Đồng ý.** Lưu ý khi tách: các file `ars-adapted/`, `modules/`, `common-standard.md`, mẫu matrix là bản dịch/thu gọn từ ARS nên là *adapted material*; cách đơn giản và an toàn là ghi cả cây `packs/academic-research/` (và bản cài) theo CC BY-NC 4.0, phần MIT chỉ áp cho phần LAW tách riêng được. Phạm vi dùng ở đơn vị kinh doanh vẫn chờ người có thẩm quyền xác nhận |
| F2 Index | Làm sạch index bản giao, giữ index bản cài thử tại root | **Đồng ý**, thêm một điều kiện: cần **cơ chế** để không tái diễn (bản sạch `SKILL_INDEX.md` trong `release_templates/` hoặc bước dựng loại dòng `PACK`), cộng một kiểm trong `check_package` báo dòng `PACK` trỏ tới file không có trong bản giao. Làm sạch tay một lần thì lần cài thử sau sẽ lặp lại lỗi |
| F3 Id | Chưa đủ căn cứ đổi; ưu tiên làm rõ mô tả | **Chấp nhận** hoãn đổi id, với hai ghi chú: (1) chi phí migration chỉ tăng theo số bản cài, hiện mới có root và Pilot A/B, nên nếu sẽ đổi thì đổi sớm rẻ nhất; (2) thay tranh luận bằng một phép thử nhỏ: sau khi sửa mô tả, đưa 2–3 yêu cầu nghiên cứu pháp luật (ví dụ "phân tích điều kiện chuyển nhượng theo Luật Đất đai") cho agent có index đã cài gói, ghi agent có chọn `law-academic-research` không. Chọn nhầm ⇒ đổi id; không nhầm ⇒ giữ. Mô tả mới nên nói thẳng "không dùng cho tra cứu/phân tích văn bản pháp luật" thay cho "không nhận diện luật" |
| F4 Mô tả | Đúng, 277 → cắt 220 | **Đồng ý.** Viết ≤220 ký tự, câu "không dùng khi" đặt trong 220 ký tự đầu; nên gộp với sửa mô tả của F3 thành một lần |
| F5–F6 | Xử lý trước phép đo chất lượng mới | **Đồng ý.** Đây là điều kiện để phép đo điều kiện 4 sau này không bị nhiễm bởi quy tắc rút từ ca thử |
| F7 README | Giảm ưu tiên vì trang gói dùng `pack.json` | **Đồng ý**, đóng ở mức thấp. Mô tả `pack.json` hiện đã dễ hiểu với người dùng |
| F8 Hồ sơ | Giữ provenance, không tạo bản sao | **Đồng ý.** Chỉ cần quyết nơi lưu lâu dài trước khi dọn `working/` |

## Thứ tự

Đồng ý với Codex: sửa gói và owner sau khi reconcile và đóng lượt Cowork đang có hiệu lực. Trước khi commit gói vào `main`: F1, F2 (kèm cơ chế), F4
cùng mô tả của F3. Trước phép đo chất lượng mới: F5, F6. Phép thử chọn nhầm của F3 chạy sau khi có mô tả mới.

## Chưa kiểm

Chưa xem phần Codex đã ghi vào roadmap/STATE/HANDOFF cho các finding này; chưa review phần "sửa gói cũ" (đồng bộ AN C2) Codex báo đã hoàn tất.
