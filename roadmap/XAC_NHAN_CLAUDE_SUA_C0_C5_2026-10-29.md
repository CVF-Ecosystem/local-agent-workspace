# Xác nhận của Claude — Codex sửa C0–C5 theo review hấp thu nguyên tắc nghiệm thu

**Ngày:** 29/10/2026. **Người lập:** Claude (Opus 5.5). Kiểm chỉ đọc; chỉ thêm file này.
**Căn cứ:** [REVIEW_CLAUDE_HAP_THU_NGUYEN_TAC_NGHIEM_THU_2026-10-29.md](REVIEW_CLAUDE_HAP_THU_NGUYEN_TAC_NGHIEM_THU_2026-10-29.md) và báo cáo của Codex (operator chuyển trong hội thoại).

## Kết luận

**C0–C5 đạt.** Full suite do Claude tự chạy lại chỉ còn B7. C6 và tranche CVF gốc vẫn hoãn theo quyết định của operator. Sản phẩm vẫn
`PRERELEASE_NOT_READY` vì B7 và các khoảng trống roadmap; xác nhận này không đổi điều đó.

## Từng mục

| Mục | Kết quả | Bằng chứng Claude kiểm |
|---|---|---|
| C0 | ĐẠT | `PROJECT.md` và `en/PROJECT.md` đều 7 mục `##`. Full suite: `Ran 1712 tests in 1069.697s — FAILED (failures=1, skipped=8)`, lỗi duy nhất là B7 `test_execution_profile.Delivery.test_selection_ownership_and_bytes_without_a_source_profile`; 8 lỗi song ngữ đã hết. Trùng log của Codex `working/acceptance-repair-20261029/fullsuite.log` (1712 test, 1 failure, 8 skip; SHA `83dd620b…831c`) |
| C1 | ĐẠT | `cvf-workspace-rules-20261029.patch` (SHA `511b96da…beee`, có trong HANDOFF) gồm đúng 8 file quy tắc, không lẫn file model gateway; `git apply --check -R` sạch trên bản clone, tức patch khớp đúng thay đổi hiện có. `WORKSPACE_RULES_20261029.md` (SHA `1424b6ba…dd03`) trùng hash `WORKSPACE_RULES.md` hiện tại |
| C2 | ĐẠT | Contract (clone) dòng 159–162: thành phần thử nghiệm được giao kèm tiêu chí chưa đạt và giới hạn dùng, không tuyên bố sẵn dùng; cấm đổi nhãn tiêu chí thành optional/N/A/accepted để giao |
| C3 | ĐẠT | LAW `AGENTS.md` và contract dòng 202–206: đội dev chuẩn bị ca/nguồn/rubric/câu hỏi; chưa có quyền mời/trả phí thì hỏi operator một lần bằng lời công việc về người duyệt và ngân sách; không tự liên hệ hay trả phí; claim phụ thuộc giữ bị chặn |
| C4 | ĐẠT | `packs/README.md:12`: "Khi chưa qua nghiệm thu, gói chỉ dùng để tham khảo và soạn nháp; không dùng căn cứ trong gói cho văn bản trình ký hoặc gửi ra ngoài." Giữ câu trách nhiệm QA thuộc đội dev |
| C5 | ĐẠT | `skills/README.md`, bản `en`, contract dòng 214–216: dùng nguồn quá hạn thì ghi "chưa kiểm lại từ <ngày>" trong đầu ra; không trình bày như căn cứ hiện hành với nội dung thận trọng cao |
| C6 | HOÃN | Theo quyết định operator, cùng tranche CVF gốc |

Kiểm thêm: `check_package` 0 lỗi, 14 cảnh báo (14 README chưa nhắc tên skill, có từ trước); `build_guides_html.py --check` 10 trang khớp.

## Còn mở (không thuộc lượt sửa này)

- B7: profile sống trong kho nguồn (owner nhánh học thuật/host).
- Số skip 8 (trước đây 6): đã xem, xem mục "Hai ca skip mới" bên dưới.
- Patch CVF trong clone vẫn chưa upstream về governance; không push từ clone.
- Các mục còn mở của roadmap V7/V4 như Codex đã liệt kê.

## Hai ca skip mới (đọc từ log verbose của Codex `working/acceptance-repair-20261029/fullsuite.log`)

Sáu ca skip cũ không đổi (5 ca cần file symlink, 1 ca `publish_new` chỉ chạy ngoài Windows). Hai ca mới đều thuộc công cụ mới `tools/check_quotes.py`:

| Test | Lý do skip |
|---|---|
| `test_check_quotes.QuoteChecks.test_file_link_is_not_followed` | `Host does not permit symlink fixture: [WinError 1314] A required privilege is not held by the client` |
| `test_check_quotes.QuoteChecks.test_parent_link_not_followed` | như trên (dùng `symlink_to(..., target_is_directory=True)`, `tests/test_check_quotes.py:158`) |

Ý nghĩa: trên máy này, phần "không đi theo liên kết" của `check_quotes.py` chưa được test tự động. Trên Windows, liên kết người dùng thường tạo được
không cần quyền admin là **junction**, nên Claude thử tay trong scratchpad (thư mục `root\real\src.txt` và `root\linked` là junction trỏ ra ngoài root,
nội dung file giống nhau, cùng `--expected-sha256`, `--source-kind plain-text`):

| Nguồn | Kết quả |
|---|---|
| `real\src.txt` | exit 0, `status: success`, "Quote found within claimed lines." |
| `linked\src.txt` (qua junction) | exit 2, `status: not_checked`, "Symlink/junction/reparse point is not supported." |

Mã ở `tools/check_quotes.py:35-38` (`_plain_stat` từ chối `S_ISLNK` hoặc `FILE_ATTRIBUTE_REPARSE_POINT`) và `_root` kiểm cả thư mục cha. Hành vi đúng.

**Đề nghị Codex:** (1) cho `test_parent_link_not_followed` dùng junction (`cmd /c mklink /J`) khi không tạo được symlink, như
`tests/test_artifacts.py:815-825` đã làm, để ca này chạy được trên Windows không quyền admin; (2) ca file symlink chỉ được kiểm trên CI Ubuntu/macOS
(`.github/workflows/*.yml` có ma trận ubuntu/windows/macos), ghi rõ điều đó khi báo kết quả local.

**Rủi ro cần kiểm (chưa thử, PLAUSIBLE):** vì từ chối mọi reparse point ở nguồn và mọi thư mục cha, project đặt trong thư mục có reparse point hợp lệ
(ví dụ file "chỉ trên mây" của OneDrive, thư mục được chuyển hướng) có thể luôn bị `not_checked`. Đúng hướng an toàn (không báo MATCH sai), nhưng nên
thử một lần và ghi vào giới hạn của công cụ nếu đúng.

## Chưa kiểm

Chưa đọc đủ toàn văn các đoạn đã sửa ở `en/AGENTS.md`, `en/skills/README.md` (chỉ grep đúng câu C3–C5); chưa chạy hai script sinh hướng dẫn CVF; chưa
chạy test của CVF.
