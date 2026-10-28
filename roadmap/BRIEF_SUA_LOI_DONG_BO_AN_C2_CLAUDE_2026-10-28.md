# Brief sửa lỗi — patch đồng bộ AN C2 (gửi Codex)

**Ngày:** 28/10/2026. **Người lập:** Claude (Opus 5.5), theo yêu cầu operator "viết phản hồi chi tiết để Codex fix".
**Căn cứ:** [REVIEW_DOC_LAP_DONG_BO_AN_C2_CLAUDE_2026-10-28.md](REVIEW_DOC_LAP_DONG_BO_AN_C2_CLAUDE_2026-10-28.md) (B1–B7) và
[REVIEW_DOC_LAP_GOI_ACADEMIC_RESEARCH_CLAUDE_2026-10-28.md](REVIEW_DOC_LAP_GOI_ACADEMIC_RESEARCH_CLAUDE_2026-10-28.md) (F2, F4).
**Owner tích hợp đề xuất:** Main Codex. **Revision brief:** r1. Brief này là đề xuất của reviewer; operator giao mới có hiệu lực.
Mọi số dòng/hash dưới đây đo lúc 28/10/2026 trên working tree `main` HEAD `b1ec507` chưa commit; đo lại trước khi ghi.

## 0. Gắn mốc (quy tắc 10)

- **Mốc sản phẩm:** V7 (nhập, áp dụng, nâng cấp có provenance; giữ sạch nguồn và artifact). Trạng thái hiện hành `PRERELEASE_NOT_READY`, không đổi.
- **Lần giao này đóng:** S4 của roadmap AN C2 ở mức "patch đạt full suite" (B1), index bản giao sạch (B2/F2), nội dung `container-yard-check`
  (B3), mô tả trong index (B8, F4), cảnh báo CRLF ở project không Git (B5), cache lọt vào project (B6), sửa dòng S2/S4/S5 của roadmap.
- **Vẫn còn sau lần này (không thuộc brief):** F1 license gói học thuật, F3/F5/F6 gói học thuật, B7 profile sống (owner nhánh học thuật/host),
  host 2/3 và stable quality, revise/error lifecycle, MANIFEST và release gates trên tree phát hành, hướng dẫn VI/EN support matrix, user feedback,
  toàn bộ mục "Điều kiện còn mở" của roadmap rev139. B4 (dựng lại roadmap gốc) do Claude làm nếu operator đồng ý, không phải Codex.

## 1. Ràng buộc khi thi công

1. **Host:** HANDOFF đầu file ghi Cowork rev143 `COWORK_CLOSED_WITH_FINDINGS`; Antigravity chưa phát. Trước khi ghi file nào thuộc binding
   (`.cvf/**`, `tools/context_update.py`, `tools/publish_new.py`, owner đang pin), đọc lại 3 dòng đầu HANDOFF; có lượt host đang mở thì dừng phần đó.
   Lưu ý: DISPATCH Cowork 28/10 18:50 (`working/academic-research/host-acceptance-20261027/stage1/claude/DISPATCH.json`) và
   `working/host-academic-20261027/claude/assignments/a1/RESULT.json` đã bind digest mới `3fb735bb…`; các bản Codex 27/10 bind digest cũ `1a4fd323…`.
2. **Bytes:** giữ EOL từng file; file `-text` ghi ở chế độ nhị phân; không đổi `tools/publish_new.py` (`8a4e5914…d852`).
3. **Không stage/commit/push** khi operator chưa cho; giữ diff trước/sau theo owner như roadmap đã ghi.
4. **Kiểm full suite** cho mọi thay đổi chạm owner/pin/policy: `python -X utf8 -B -m unittest discover -s tests -v`. Suite chạy khoảng
   21 phút trên máy này (1238 giây); đặt timeout ≥ 2400 giây, không dùng 900 giây.
5. B1 đổi policy v3 đã nhận nên **phải có review độc lập** trước khi gọi xong (AGENTS.md, mục bảo trì). Các mục khác: Main tự kiểm + reviewer
   theo preset hiện hành.

## 2. Việc sửa

### B1 — Re-pin P-CTX1 làm 57 test control v3 lỗi (cao) — **cần operator chọn hướng trước**

**Hiện trạng:** `tools/context_update.py` đổi bytes (sửa UTF-8) → `ROUTING_POLICY.json` đổi `operational_context_protocol.entrypoint_sha256`
thành `sha256:65fd8792…148d` (đúng) → digest policy đổi từ `sha256:1a4fd3233dcf4b8571d9fa2249faf060216b3e530ca7d8dcf976dc5df880eaf3` sang
`sha256:3fb735bbb88087fcd3c76bd23851609d93e57fc4f8c43194b29d61b0466d6794`. Chưa cập nhật:

| Chỗ | Giá trị cũ còn lại |
|---|---|
| `.cvf/contracts/v3/vectors.json` (`policy_digest.digest`) | `1a4fd323…eaf3` |
| 22 file `.cvf/contracts/v3/examples/*.json` (binding policy; ex01–ex19 thấy rõ bằng grep, mỗi file 1–3 chỗ) | `1a4fd323…eaf3` |
| `tests/test_control_check_v3.py:53` `FILE_PINS[('rules','v3','ROUTING_POLICY.json')]` | `af141b37c242119c` (hash HEAD) |
| `tests/test_control_check_v3.py` `FILE_PINS[('contracts','v3','vectors.json')]`, `V3_EXAMPLES_PIN = ('deb1ae93824126f3', 22)` | sẽ đổi nếu chọn hướng (a) |

Test lỗi: `test_control_check_v3` 54 ca (`OwnersUntouched`, 50 ca `test_valid_examples_are_blocked_never_pass_in_every_phase`, CLI `-I`, BOM,
`test_expected_design_is_never_turned_into_a_verdict`, `test_single_effect_without_its_task_is_not_bound_or_routed`), `test_control_v3_candidate`
và `test_control_v3_canonical_screening` 3 ca. Các ca example nhận thêm lý do `BINDING_MISMATCH` (và `UNCLASSIFIED_OPERATION` ở một ca CLI).

**Ba hướng:**

| Hướng | Làm gì | Được | Mất |
|---|---|---|---|
| **(a) Công nhận revision policy v3** (Claude khuyến nghị) | Tạo lại `vectors.json` và binding của 22 example theo digest mới; cập nhật `FILE_PINS`, `V3_EXAMPLES_PIN` kèm comment lý do + ngày; ghi revision policy trong CHANGELOG/HANDOFF | Giữ sửa cp1252 cho `context_update`; khớp với bằng chứng Cowork 28/10 đã bind `3fb735bb…` | Đổi bộ owner v3 đã nhận ⇒ bắt buộc review độc lập; bằng chứng Codex 27/10 bind digest cũ trở thành bằng chứng của revision trước |
| (b) Tách pin khỏi digest | Sửa phép chiếu digest để bỏ `entrypoint_sha256` | Lần sửa owner sau không kéo theo đổi digest | Trái `test_policy_projection_is_still_the_whole_policy_object` (thiết kế cố ý); đổi ngữ nghĩa binding ⇒ việc thiết kế riêng, không làm trong brief này |
| (c) Hoàn tác | Trả `tools/context_update.py` và `ROUTING_POLICY.json` về bytes HEAD, trả `tests/test_current_draft.py` về pin cũ; ghi `context_update --help` dưới cp1252 là giới hạn đã biết (như `publish_new`) | Không đụng hợp đồng v3 đã nhận | Mất sửa cp1252 cho 1 công cụ; bằng chứng Cowork 28/10 bind digest không còn khớp file |

**Bước làm nếu chọn (a):**
1. Tìm cách vector/example v3 được sinh khi nhận v3 (HANDOFF/roadmap V7 hoặc script trong `working/v7-internal/`); dùng lại đúng cách đó. Không sửa
   tay 22 file bằng thay chuỗi mù.
2. Sau khi sinh lại, chạy một script so JSON từng example cũ/mới: **chỉ** được khác ở đường dẫn chứa policy digest. Bất kỳ khác biệt nào khác
   (reasons, expected, thứ tự khóa, EOL) ⇒ dừng.
3. Giữ EOL/bytes của từng file theo `.gitattributes` (các file `.cvf/contracts/**` có dòng `-text` thì ghi nhị phân).
4. Cập nhật `FILE_PINS` (ROUTING_POLICY, vectors.json) và `V3_EXAMPLES_PIN` trong `tests/test_control_check_v3.py`, comment ghi
   "revision P-CTX1 28/10/2026, xem HANDOFF revN".
5. Grep toàn kho (trừ `working/`) không còn `1a4fd3233dcf4b85` ngoài hồ sơ lịch sử (HANDOFF).

**Nghiệm thu B1:**
- `python -X utf8 -B -m unittest tests.test_control_check_v3 tests.test_control_v3_candidate tests.test_control_v3_canonical_screening -v`: 0 lỗi.
- Full suite: 0 lỗi ngoài B7 (hoặc 0 nếu B7 đã xử lý); số skip không tăng (hiện 6).
- `check_package.run_checks(release=False)`: 0 lỗi; `pin_problems()` = `[]`; `current_draft.readiness('.')` `usable: True`.
- Review độc lập ghi nhận hướng đã chọn và diff đã giới hạn ở digest.

### B2 (= F2) — Index bản giao trỏ tới gói không có (trung bình–cao)

**Hiện trạng:** project tạo bằng `new_project.py` có `.agent/SKILL_INDEX.md:22` dòng `law-academic-research | LOCAL | PACK | skills/local/packs/...`
trong khi `skills/local/packs/` chỉ có `README.md`. `TEMPLATE_OVERLAYS` (`tools/check_package.py:222-229`) thay PROJECT/STATE/HANDOFF bằng mẫu
sạch nhưng không có `SKILL_INDEX.md`; `check_package.py:828-837` chỉ kiểm dòng `SHARED`.

**Bước làm:**
1. Tạo `release_templates/.agent/SKILL_INDEX.md` và `release_templates/en/.agent/SKILL_INDEX.md` = index hiện hành **bỏ mọi dòng `| PACK |`**
   (giữ đủ dòng SHARED và phần chữ đã sửa ở patch này).
2. Thêm hai cặp vào `TEMPLATE_OVERLAYS`.
3. Trong `check_package`: (i) bản mẫu trong `release_templates/` không được có dòng `PACK`; (ii) khi chạy trong project, dòng `PACK` trỏ tới file
   không có ⇒ lỗi (hoặc cảnh báo, chọn một và ghi lý do).
4. Giữ index của kho nguồn (bản cài thử ở root) như hiện tại theo ý Codex đã nêu.
5. Thêm test: project dựng từ nguồn có 0 dòng PACK; sau `pack.py add <gói>` có đúng dòng của gói đó.

**Nghiệm thu B2:** `new_project.py --name X --dest <tạm> --apply` → `grep -c "| PACK |" <tạm>/X/.agent/SKILL_INDEX.md` = 0 (cả `en/` nếu
`--lang en`); `pack.py add cang-logistics` trong project đó → 2 dòng PACK; `check_package` trong project 0 lỗi.

### B3 — Khôi phục kiến thức nghề cho `container-yard-check` (trung bình)

**Hiện trạng:** bản ở `packs/cang-logistics/skills/container-yard-check/` (162 dòng) bỏ gần hết khái niệm nghề của bản AN C2 (247 dòng):
Outgoing 13→0, Incoming 9→0, lót pháo 11→0, RTG 13→0, ET20 2→0, Tier 1 4→0, PyInstaller/.exe 13→0. Các khái niệm này là chung của khai thác bãi
container, không phải thông tin riêng đơn vị, và chính là bài học của lần sửa V4.2.1. Nguồn đối chiếu:
`D:\UNG DUNG AI\TOOL AI 2026\AN C2\local-agent-workspace-v1.9.0\packs\cang-bai-container\skills\container-yard-check\` (fingerprint 7 file
`8c5be172…b01` như roadmap ghi).

**Nguyên tắc:** khái niệm + quy tắc mặc định của nghề **giữ lại**, gắn nhãn "mặc định thường gặp — xác nhận với project"; chỉ **giá trị riêng**
(block nào RTG/lót pháo, tiền tố thật, mã tàu, tên file, ngưỡng) thành `[hỏi đơn vị]`/khóa cấu hình.

**Cần khôi phục (từ bản AN C2):**

| Nội dung | Nơi trong bản AN C2 | Cách viết lại |
|---|---|---|
| 5 câu hỏi trước khi viết mã (trạng thái TOS, tên block/tiền tố, block RTG và lót pháo, ISO theo F/E, mốc thời gian dữ liệu) | `SKILL.md` mục "Trước khi viết mã" | Giữ nguyên ý; ví dụ `K12`/`12` đổi thành ví dụ trung tính (block có tiền tố chữ bị TOS ghi thiếu); ví dụ tên file dùng dạng `<du_lieu>_<dd-mm-yyyy>_<hhmm>.xlsx` |
| Nghĩa mặc định Stacking/Incoming/Outgoing và quy tắc "chỉ cont đang ở ô làm căn cứ chiếm ô" | `SKILL.md` câu hỏi 1; `nghiep-vu-bai.md` bảng thuật ngữ | Giữ là mặc định thường gặp + bắt buộc xác nhận; nêu đây là lỗi nặng nhất từng gặp (trùng ô giả, lót pháo giả, lẫn tàu giả) |
| Bảng quy tắc cốt lõi (lẫn tàu theo Bay/Row RTG, lẫn cảng đích, H/M/L, RTG lẫn nhập/xuất, 5 loại lót pháo, trùng ô) | `SKILL.md` "Quy tắc nghiệp vụ cốt lõi" | Giữ bảng; mức ĐỎ/CAM/VÀNG ghi là mặc định cấu hình được |
| Nhãn tank theo ISO + F/E (`22T0`: hàng FT20, rỗng ET20), cont lạnh không phải tank, 40' = 2 TEU | `SKILL.md` câu hỏi 4; `nghiep-vu-bai.md` mục ISO | Giữ là ví dụ ISO chuẩn; bảng quy đổi thật do project xác nhận |
| "Sai lầm đã gặp" (8 mục) | `SKILL.md` | Giữ nguyên, bỏ con số riêng nếu có |
| Kiểm thử tối thiểu (bảng 8 nhóm ca), đánh giá độc lập 7 bước, lượng hóa nghi vấn bằng chạy có/không điều kiện | `references/kiem-thu-dong-goi.md` | Giữ; con số ví dụ (44 → 36, 6 → 0) ghi "ví dụ" hoặc bỏ |
| Mẫu spec PyInstaller và cách thử `.exe` (`--input`, `--auto`, thiếu file, giao diện, `console=False`) | `references/kiem-thu-dong-goi.md` | Giữ; tên `Kiem_tra_bai.py` đổi thành `<entry>.py` |
| Bẫy kỹ thuật (Unicode NFC/NFD, `cp -p`, pandas FutureWarning, cp1252) | `references/kiem-thu-dong-goi.md` | Giữ |
| Kiến trúc một bảng chuẩn hóa, HTML nhúng JSON không tính lại, cấu hình có kiểm hợp lệ, mốc dữ liệu theo tên file/ngày sửa có cảnh báo | `references/kien-truc-ung-dung.md` | Đối chiếu bản mới (45 dòng) và bổ sung phần thiếu |

**Phải sửa thêm:** `SKILL.md` bản AN C2 dẫn tới `ra-soat-excel-sai-sot` (lớp A, không có ở nguồn): thay bằng `spreadsheet-check` hoặc bỏ.
Giữ phần bản mới làm tốt (khung câu hỏi xác nhận, "khi dữ liệu không đủ", không cộng cảnh báo khác đơn vị) và ghép với nội dung khôi phục, không
tạo hai bản song song.

**Nghiệm thu B3:**
- Grep trong `packs/cang-logistics/skills/container-yard-check/`: Outgoing, Incoming, lót pháo, RTG, ET20, PyInstaller đều > 0.
- Grep tên đơn vị/site (Tân Thuận, SASTECO, K12, Cát Lái, ttport, Sài Gòn, `Kiem_tra_bai`) = 0; không có số cont/số liệu sản xuất thật.
- `pack.py check cang-logistics` đạt; `pack.json` giữ `DEFER`/`SUPPLEMENT`; nâng `metadata.version` của skill (ví dụ 0.1.1) và ghi trong
  `references/intake-record.md` lý do khôi phục; không đổi kết luận điều kiện 4/6.
- Mô tả skill ≤ 220 ký tự (xem B8).

### B8 (mới, = F4) — Mô tả skill dài hơn giới hạn index (trung bình)

`tools/pack.py:327` ghi `desc[:220]`. Đo 28/10: `container-yard-check` **675** ký tự, `port-operations-reports` **457**, `law-academic-research` **277**.
Cả ba bị cắt giữa chữ khi `pack.py add` ghi index.

**Bước làm:** (1) viết lại mô tả ba skill ≤ 220 ký tự, câu "không dùng khi" nằm trong 220 ký tự; phần dài chuyển vào thân `SKILL.md`;
(2) `pack.py check` báo lỗi hoặc cảnh báo khi mô tả > 220; (3) nếu vẫn cắt, cắt ở ranh giới từ và thêm "…".
**Nghiệm thu:** `pack.py check` 6 gói không có cảnh báo độ dài; project thử sau `pack.py add` có dòng index kết thúc trọn câu.

### B5 — Cảnh báo CRLF cho file `-text` ở project không có Git (thấp)

**Hiện trạng:** `tools/check_package.py:754-773` chỉ dùng `git check-attr` khi có `.git`; không có thì chỉ loại `BYTE_EXACT`
(`check_package.py:221`, 2 file). Project mới báo `Có 3 file dùng CRLF (ví dụ .cvf/checks/v3/observer.py); nên dùng LF.` cho
`observer.py`, `workflow.py` là file `-text` (`.gitattributes` dòng 9–10). Làm theo lời khuyên sẽ đổi bytes file đã pin.

**Bước làm:** khi không có Git, đọc `.gitattributes` của gói: dòng dạng `<đường dẫn> -text` (không wildcard) đưa vào `raw_byte_paths`; dòng có
wildcard thì bỏ qua và giữ cảnh báo (bảo thủ). Thêm test cho nhánh không Git.
**Nghiệm thu:** project mới (sau B6) `check_package` không còn cảnh báo CRLF; kho nguồn vẫn như hiện tại.

### B6 — `.pytest_cache` lọt vào project mới và MANIFEST (thấp, có từ 24/10)

`SKIP_DIRS = {'.git', '__pycache__', 'dist', 'node_modules'}` (`check_package.py:20`). Project thử có `.pytest_cache/` và 3 dòng
`.pytest_cache/...` trong `MANIFEST.sha256`.
**Bước làm:** thêm `.pytest_cache` (cân nhắc `.mypy_cache`, `.ruff_cache`) vào `SKIP_DIRS`; kiểm `new_project.py`, `build_release.py`,
`upgrade_package.py` cùng dùng tập này. **Không** xóa `.pytest_cache` của kho nguồn trong brief này.
**Nghiệm thu:** project mới không có `.pytest_cache`, MANIFEST không có dòng đó; cảnh báo CRLF `.pytest_cache/README.md` ở kho nguồn hết.

### Roadmap rev139 — sửa trạng thái

Sau khi làm B1–B8, cập nhật bảng "Đối chiếu các mốc": S2 ghi B3; S4 ghi kết quả full suite (số test, lỗi, skip, thời gian) thay cho "targeted tests";
S5 ghi review độc lập cho B1. Trước khi B1 xong, S4 phải ghi **CHƯA ĐẠT — full suite 58 lỗi (57 do re-pin P-CTX1)**, không giữ "PASS_WITH_LIMITS".

## 3. Thứ tự đề xuất

1. Operator chọn hướng B1 (a/b/c).
2. B1 → full suite → review độc lập.
3. B2, B5, B6 (cùng owner công cụ, kiểm chung một lần `new_project` + full suite).
4. B3 + B8 (owner gói), `pack.py check`, thử `pack.py add` trong project tạm.
5. Cập nhật roadmap/HANDOFF/CHANGELOG một lần ở cuối.

## 4. Kiểm cuối (một lượt, sau khi xong cả brief)

```text
python -X utf8 -B -m unittest discover -s tests -v                 # 0 lỗi (trừ B7 nếu chưa xử lý), skip ≤ 6
python -X utf8 -B -c "import sys;sys.path.insert(0,'tools');import check_package as c;e,w=c.run_checks(release=False)[:2];print(len(e),len(w))"
python -X utf8 -B tools/check_package.py --check-eol <mọi file đã đổi>
python -X utf8 -B tools/build_guides_html.py --check
python -X utf8 -B tools/pack.py check <từng gói>
PYTHONIOENCODING=cp1252: --help cho 25 file tools/*.py có __main__, stdin đóng, timeout   # 24/25 exit 0; publish_new exit 2 (đã biết)
new_project.py --apply vào thư mục tạm → 0 dòng PACK, không .pytest_cache, check_package 0 lỗi 0 cảnh báo CRLF;
  pack.py add cang-logistics → 2 dòng PACK, dòng index trọn câu
```

Ghi kết quả từng lệnh (số liệu, mã thoát) vào HANDOFF. Phần nào chưa chạy được thì ghi rõ, không gộp thành PASS.

## 5. Ngoài brief (để operator biết)

- **B4:** roadmap gốc 282 dòng (`d6857f11…2194`) đã bị viết đè, không còn bản sao. Claude đã đọc đủ bản này trong phiên 28/10 và có thể dựng lại
  thành `roadmap/archive/` hoặc file lưu trữ có ghi rõ "dựng lại từ phiên, không phải bytes gốc" khi operator đồng ý.
- **B7:** `test_execution_profile` lỗi vì `.agent/EXECUTION_PROFILE.json` sống trong kho nguồn; thuộc owner nhánh học thuật/host, cần xử lý trước commit.
- **F1, F3, F5, F6** của gói học thuật theo [phản hồi đã xác nhận](XAC_NHAN_PHAN_HOI_REVIEW_ACADEMIC_RESEARCH_CLAUDE_2026-10-28.md).
