# Review độc lập — patch đồng bộ AN C2 (Codex, roadmap rev139)

**Ngày:** 28/10/2026. **Reviewer:** Claude (Opus 5.5, Claude Code trên Windows), theo yêu cầu operator "test cái này, xem ổn chưa".
Review và kiểm chỉ đọc trên kho nguồn; project thử tạo trong thư mục scratchpad của Claude. `git status --porcelain` trước và sau toàn bộ phép kiểm
giống hệt. File này là file duy nhất được thêm vào kho.
**Đối tượng:** working tree `main` (HEAD `b1ec507`, chưa commit) sau khi Codex báo đóng patch, theo [ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28.md](ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28.md) rev139.
Không đánh giá lượt host Cowork rev140; không đổi trạng thái nào trong roadmap/HANDOFF.

## 1. Kết luận

**Chưa ổn để coi S4 là PASS.** Phần CLI, pin `context_update`, docs/HTML, EOL và cấu trúc gói đạt. Nhưng full unittest có **58 lỗi**, trong đó
**57 lỗi do chính re-pin P-CTX1** (policy digest đổi mà vector/example/test control v3 chưa đổi). Roadmap ghi S4 dựa trên "targeted tests";
full suite chưa được chạy nên lỗi này không lộ ra. Ngoài ra có 3 điểm nội dung/đóng gói cần sửa (B2–B4).

## 2. Phần đạt

| Phép kiểm | Kết quả |
|---|---|
| `check_package.run_checks(release=False)` | 0 lỗi, 15 cảnh báo (14 README chưa nhắc tên skill, có trước; 1 CRLF ở `.pytest_cache/README.md`). Cảnh báo CRLF của file `-text` đã hết trong kho nguồn (10 → 0) |
| `pin_problems()` | `[]` |
| Pin P-CTX1 | `ROUTING_POLICY.json` ghi `sha256:65fd8792…148d` = SHA thật của `tools/context_update.py`; `tests/test_current_draft.py` cập nhật cùng lần |
| `current_draft.readiness('.')` | `usable: True` |
| `tools/publish_new.py` | bytes giữ nguyên (`8a4e5914…d852`), không có diff |
| `--help` dưới `PYTHONIOENCODING=cp1252`, stdin đóng, timeout 20s | 24/25 file có `__main__` exit 0, 0 `UnicodeEncodeError`; `publish_new.py` exit 2 (đúng như roadmap ghi, file đã pin) |
| `build_guides_html.py --check` | `HTML đã khớp Markdown (10 trang)` |
| `check_package.py --check-eol` trên mọi file đổi/mới (trừ `working/`) | `0 lỗi`; bỏ qua `tools/context_update.py` vì `-text` |
| `pack.py check` 6 gói | đều `cấu trúc OK`, tiếp nhận hoãn; `cang-logistics` 0.3.0, 2 skill, `DEFER`/`SUPPLEMENT` |
| Số liệu tài liệu | không còn "17 skill"; `skills/README.md` và `SKILLS_GUIDE.md` ghi 14 (mười bốn) |
| Rò tên đơn vị trong `container-yard-check` | grep Tân Thuận/SASTECO/K12/ET20/FT20/Cát Lái/ttport/Sài Gòn: 0 |
| Tạo project mới | `new_project.py --name "Thu AN C2" --dest <scratchpad> --apply` thành công; trong project đó `check_package` ĐẠT 0 lỗi; `pack.py add cang-logistics` cài 2 skill, ghi `REVIEW` vào index |

## 3. Finding

### B1 — Re-pin P-CTX1 làm hỏng 57 test control v3 (cao; đã xác nhận)

Lệnh: `python -X utf8 -B -m unittest discover -s tests -v` → `Ran 1667 tests in 1238.045s — FAILED (failures=58, skipped=6)`.

| Module | Số lỗi | Nguyên nhân thấy trong traceback |
|---|---|---|
| `test_control_check_v3` | 54 | `OwnersUntouched`: `rules/v3/ROUTING_POLICY.json` có prefix `4577f71406997acb`, test chờ `af141b37c242119c` (hash ở HEAD); 50 ca `test_valid_examples_are_blocked_never_pass_in_every_phase` và các ca CLI/BOM nhận thêm lý do `BINDING_MISMATCH` |
| `test_control_v3_*` (candidate, canonical_screening) | 3 | vector `policy_digest` = `sha256:1a4fd323…eaf3`, digest tính từ file hiện tại = `sha256:3fb735bb…6794` |
| `test_execution_profile` | 1 | xem B7, không do patch này |

- Đây đúng là quan hệ Codex đã mô phỏng ở phản biện điểm 1: đổi `entrypoint_sha256` làm đổi `policy_digest`. Patch cập nhật pin và test
  `current_draft`, nhưng chưa xử lý vector `policy_digest`, binding khai trong các example v3 và test `OwnersUntouched`.
- `OwnersUntouched` coi `ROUTING_POLICY.json` là owner v3 **đã nhận phải giữ đúng bytes**. Vì vậy cập nhật hash trong test chưa đủ: re-pin là một
  **revision của policy v3 đã nhận**, thuộc nhóm đổi policy/quyền cần quyết định và review độc lập (AGENTS.md, mục bảo trì).
- **Liên quan host:** roadmap ghi Cowork rev140 đã có "binding mới". Chưa kiểm binding đó dùng digest nào. Nếu là `3fb735bb…`, mọi cách sửa B1
  làm đổi policy lần nữa sẽ phá binding đang có hiệu lực; nếu là `1a4fd323…`, binding đó đã lệch với file hiện tại.
- **Đề xuất:** dừng gọi S4 là PASS; Main/operator chọn một trong hai hướng rồi review: (a) công nhận revision policy v3: tạo lại vector,
  binding example, cập nhật `OwnersUntouched`, ghi lý do; hoặc (b) tách pin `entrypoint_sha256` khỏi phần policy được tính digest để re-pin owner
  không đổi digest. Đối chiếu binding Cowork rev140 trước khi ghi.

### B2 — Project mới có dòng skill trỏ tới gói không có (trung bình–cao; đã xác nhận)

Project thử tạo bằng `new_project.py` có `.agent/SKILL_INDEX.md:22` =
`law-academic-research | LOCAL | PACK | skills/local/packs/academic-research/skills/law-academic-research/SKILL.md`, trong khi
`skills/local/packs/` của project chỉ có `README.md`. Đây là F2 của review gói học thuật, nay xác nhận trên project thật (trước đó là suy từ code).
Patch AN C2 có sửa `SKILL_INDEX.md` nhưng chưa làm sạch dòng này. Đề xuất giữ như F2: bản sạch trong `release_templates/` hoặc loại dòng `PACK`
khi chép, cộng kiểm trong `check_package`.

### B3 — `container-yard-check` mất phần kiến thức nghề làm nên giá trị của skill (trung bình; đã xác nhận)

| Từ khóa (grep không phân biệt hoa thường) | AN C2 | Bản trong `cang-logistics` |
|---|---|---|
| Outgoing | 13 | 0 |
| Incoming | 9 | 0 |
| lót pháo | 11 | 0 |
| RTG | 13 | 0 |
| ET20 (nhãn tank theo F/E) | 2 | 0 |
| Tier 1 | 4 | 0 |
| PyInstaller / .exe | 13 | 0 |

Tổng dòng: 247 → 162. Bản mới (`references/nghiep-vu-bai.md`) thành khung câu hỏi chung ("trạng thái nào chiếm ô", "vùng có quy tắc riêng").
Các mục bị bỏ phần lớn là **khái niệm chung của nghề khai thác bãi container**, không phải thông tin riêng đơn vị: Incoming/Outgoing không chiếm ô,
RTG lẫn hàng theo Row, cont rỗng lót Tier 1, nhãn tank theo F/E, kiểm đóng gói .exe. Đó cũng chính là các lỗi đã sửa thật ở V4.2.1 (bài học của skill).
Chỉ giá trị riêng (block nào là RTG/lót pháo, mã tàu, tiền tố) mới cần thành câu hỏi. Bỏ cả khái niệm làm yếu điều kiện 1 (phần tăng thêm so với
native) mà hồ sơ đang cần chứng minh.
**Đề xuất:** khôi phục khái niệm và quy tắc mặc định của nghề kèm nhãn "mặc định, xác nhận với project", giữ giá trị riêng dạng `[hỏi đơn vị]`
như bản AN C2; giữ checklist đóng gói .exe ở `kiem-thu-dong-goi.md`.

### B4 — Roadmap gốc bị viết đè, không còn bản sao (trung bình; đã xác nhận)

Roadmap 282 dòng (`d6857f11…2194`) nay là rev139, 70 dòng. File chưa từng được Git theo dõi; quét kho và thư mục Temp theo SHA: không có bản
nào. Mất: bằng chứng mục 2a (zip, asset GitHub, MANIFEST), bảng 6a, quy tắc R1–R6, script đo. File phản biện/trả lời chỉ trích một phần.
Điều này trái với yêu cầu truy vết của operator và với ghi chú "giữ diff trước/sau" của chính roadmap. Claude đã đọc đủ bản gốc trong phiên
28/10 nên có thể dựng lại thành file lưu trữ nếu operator yêu cầu.

### B5 — Project không có Git vẫn cảnh báo CRLF cho file đã pin (thấp; đã xác nhận)

`check_package.crlf_warning_paths` chỉ đọc `.gitattributes` qua `git check-attr` khi có `.git`; không có Git thì chỉ loại `BYTE_EXACT`. Project mới
báo `Có 3 file dùng CRLF (ví dụ .cvf/checks/v3/observer.py); nên dùng LF.` cho `observer.py`, `workflow.py` (đều `-text` trong `.gitattributes`).
Người dùng hoặc agent làm theo lời khuyên sẽ đổi bytes file `-text`. Đề xuất: khi không có Git, đọc dòng `-text` của `.gitattributes`
(cách bộ mẫu AN C2 đã làm) hoặc đưa các file này vào `BYTE_EXACT`.

### B6 — `.pytest_cache` bị chép vào project mới và MANIFEST (thấp; có từ trước)

`.pytest_cache/` trong kho nguồn tạo 24/10 (trước patch). `new_project.py` chép nó sang project thử và MANIFEST của project có 3 dòng
`.pytest_cache/...`. `SKIP_DIRS` của `check_package.py:20` chỉ có `.git`, `__pycache__`, `dist`, `node_modules`. Đề xuất thêm `.pytest_cache`.

### B7 — `test_execution_profile` lỗi vì kho nguồn đang có profile sống (thấp; WIP học thuật, không do patch này)

`the repository must not hold a live profile`: `.agent/EXECUTION_PROFILE.json` (untracked) tồn tại. Cần xử lý trước khi commit/phát hành, nhưng
thuộc owner nhánh học thuật/host.

## 4. Đối chiếu với roadmap rev139

| Mốc | Roadmap ghi | Sau phép kiểm này |
|---|---|---|
| S2 | ĐẠT CÓ GIỚI HẠN | Phần CLI đạt; phần pin chưa đủ (B1); nội dung candidate cần sửa (B3) |
| S3 | ĐẠT CÓ GIỚI HẠN | Khớp: 10 HTML khớp, số liệu đúng |
| S4 | PATCH PASS_WITH_LIMITS | **Chưa đạt**: full suite 58 lỗi, 57 do patch (B1); B2 còn mở |
| S5 | PATCH PASS_WITH_LIMITS | Review trước đó không có full suite; cần review lại phần B1 sau khi chọn hướng |

Mốc sản phẩm vẫn `PRERELEASE_NOT_READY`, không đổi.

## 5. Lệnh đã chạy, phần chưa kiểm

**Đã chạy:** script đo raw 45 đường dẫn so AN C2 (không file nào trùng hệt bản AN C2, đúng với hợp nhất tay; 8 file AN C2 không có ở nguồn theo
thiết kế mới: 7 file `packs/cang-bai-container/` và `tools/skill_regression.py`); `check_package.run_checks`, `pin_problems`; `--help` cp1252 cho
25 CLI; `build_guides_html.py --check`; `check_package.py --check-eol`; `pack.py check` 6 gói; `current_draft.readiness`; `git diff` của
`ROUTING_POLICY.json`, `tests/test_current_draft.py`, `.agent/SKILL_INDEX.md`; `new_project.py --apply` và `pack.py add cang-logistics` trong
scratchpad; `python -X utf8 -B -m unittest discover -s tests -v` (lần đầu bị `timeout 900` ngắt, lần hai chạy đủ 1238 giây).

**Chưa kiểm:** baseline full suite tại `b1ec507` (không checkout để khỏi đụng working tree; nguyên nhân B1 lấy từ traceback: hash chờ là hash HEAD);
binding Cowork rev140; `build_release.py` và release gates; `--verify`; `app.py` giao diện; `upgrade_package.py`/`adopt_project.py` trên project có
gói cài; nội dung sửa của `skills/README.md`, `packs/README.md` về làn builder (mới xem số liệu, chưa đọc đủ lời văn); file
`TRA_LOI_CLAUDE_6_DIEM_AN_C2_2026-10-28.md`.
