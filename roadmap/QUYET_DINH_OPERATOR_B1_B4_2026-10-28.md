# Quyết định operator — B1 và B4 của brief sửa lỗi đồng bộ AN C2

**Ngày:** 28/10/2026. **Ghi bởi:** Claude (Opus 5.5), chép nguyên ý trả lời của operator trong hội thoại Claude Code.
**Liên quan:** [BRIEF_SUA_LOI_DONG_BO_AN_C2_CLAUDE_2026-10-28.md](BRIEF_SUA_LOI_DONG_BO_AN_C2_CLAUDE_2026-10-28.md) r1.

| Mục | Câu hỏi | Operator trả lời |
|---|---|---|
| B1 | Chọn hướng (a) công nhận revision policy v3, (b) tách pin khỏi digest, hay (c) hoàn tác | **(a)** |
| B4 | Claude dựng lại roadmap gốc 282 dòng (`d6857f11…2194`) đã bị viết đè | **Có** |

**Với Codex (B1 hướng a):** làm theo mục B1 "Bước làm nếu chọn (a)" của brief: sinh lại `vectors.json` và binding 22 example bằng đúng cách đã dùng khi
nhận v3, script so JSON chứng minh chỉ đổi ở đường dẫn policy digest, giữ EOL/`-text`, cập nhật `FILE_PINS` và `V3_EXAMPLES_PIN` có comment lý do,
full suite và **review độc lập** trước khi gọi xong. Đọc lại 3 dòng đầu HANDOFF trước khi ghi `.cvf/**`; có lượt host đang mở thì dừng phần đó.
Hướng (b) không làm trong brief này; có thể đề xuất riêng sau phản biện về lớp quy trình.

**Với B4:** Claude làm, không giao Codex. Bản dựng lại lưu ở `roadmap/archive/` dưới tên mới, không thay roadmap rev139 hiện hành. Kết quả đối chiếu
hash ghi ở mục dưới.

## Kết quả B4

- File: [archive/ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28_BAN_GOC_rev0.md](archive/ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28_BAN_GOC_rev0.md).
- Cách làm: Claude chép lại nội dung đã đọc đủ (công cụ Read) ở đầu phiên 28/10, ghi vào scratchpad, tính SHA-256 rồi mới chép vào kho.
- Kết quả: SHA-256 `d6857f1148cc8fc8329db6297f5307519bea3312da111be092ae64771fbd2194`, **trùng** hash bản gốc đã ghi trong
  [PHAN_BIEN_ROADMAP_AN_C2_2026-10-28.md](PHAN_BIEN_ROADMAP_AN_C2_2026-10-28.md) (Codex đo) và
  [PHAN_HOI_PHAN_BIEN_ROADMAP_AN_C2_2026-10-28.md](PHAN_HOI_PHAN_BIEN_ROADMAP_AN_C2_2026-10-28.md); 282 dòng, 30.294 byte, LF, không CRLF.
  Vì hash trùng, đây là đúng bytes bản gốc, không phải bản phỏng lại.
- File lưu trữ không mang header (thêm header sẽ đổi hash); nguồn gốc ghi tại đây. Không sửa file này; roadmap hiện hành vẫn là
  [ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28.md](ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28.md) rev139.
- Đề nghị Codex: thêm một dòng ở roadmap rev139 trỏ tới bản lưu trữ này (bản rev0, hash trên); lần sau thay roadmap thì lưu bản cũ vào
  `roadmap/archive/` trước khi ghi đè.
