# Roadmap LAW — Đồng bộ bộ mẫu `AN C2` về kho nguồn

**Lập:** 28/10/2026, Claude (Opus 5.5, Claude Code trên Windows), theo yêu cầu operator, sau phiên làm việc trực tiếp trên bộ mẫu `AN C2`.
**Trạng thái:** `PLANNED_NOT_STARTED`. Chưa chép file nào vào kho nguồn; roadmap này là file duy nhất được thêm. Khi bắt đầu, ghi trạng thái
và revision ở đây và trong `.agent/HANDOFF.md`.
**Quan hệ:** độc lập với [Roadmap văn phòng nghiệp vụ](ROADMAP_VAN_PHONG_NGHIEP_VU.md) và nhánh học thuật AC; không đổi verdict V0–V7/AC.
Không làm khi nhánh học thuật còn đang sửa dở trên cùng file (xem S0).

**Bắt đầu ở phiên mới:** đọc mục 5 (trạng thái quyết định) → 2a (vì sao AN C2 khác `main`) → 3 (bảng file) → 4 (bẫy) → 6 (các bước).
Hỏi operator các dòng còn "chờ" ở mục 5 trước khi ghi file. Chạy lại script mục 6 vì kho nguồn có thể đã đổi sau 28/10.

## 1. Bối cảnh: đã trao đổi gì ở phiên `AN C2`

Thư mục bộ mẫu `D:\UNG DUNG AI\TOOL AI 2026\AN C2\local-agent-workspace-v1.9.0` (gọi tắt **bộ mẫu AN C2**) là bản giải nén, **không có Git**,
trạng thái `clean` (chưa khởi tạo project), `VERSION` 1.9.0, CHANGELOG có mục "Chưa phát hành — Prototype văn phòng" khác kho nguồn.

Diễn biến phiên 28/10/2026:

1. Operator dựng ứng dụng "Kiểm tra vị trí bãi" (Python, Cảng Tân Thuận) ở `AN C2\KIEM_TRA_BAI_V4_2`; Claude đánh giá độc lập, sửa lên V4.2.1
   (Outgoing không còn ở ô, block TOS ghi thiếu tiền tố K12, nhãn tank ET20/FT20 theo F/E, chỉ số cảnh báo cùng đơn vị, mốc dữ liệu tự kiểm
   theo tên file/ngày sửa, đóng gói .exe). Ứng dụng không thuộc LAW.
2. Operator yêu cầu tổng hợp kinh nghiệm thành skill trong bộ mẫu AN C2 → gói mới **`cang-bai-container` 0.1.0**, skill `container-yard-check`
   (chỉ `.md` + `pack.json`; intake `DEFER`, `SUPPLEMENT`). Tạo gói bằng `tools/pack.py new`, kiểm `pack.py check`, thử cài vào project tạm.
3. Đánh giá độc lập bộ mẫu AN C2 và sửa các finding (chi tiết mục 3, nhóm B).
4. **Chỉ định của operator (giữ cho các phiên sau):** trung tâm tiếp nhận/hợp nhất và quy tắc "dùng thật vài lần mới nạp vào bộ skill gốc"
   dành cho **người nhận folder** gửi phản hồi skill, chống mở rộng skill tràn lan. Người xây dựng project (agent đang bảo trì theo chỉ định
   operator) **không bị các hạn chế này**: được sửa file package, hướng dẫn, công cụ và tính lại MANIFEST. Vẫn giữ bytes đã pin, giữ bộ mẫu
   tạo được project mới, và báo đúng phần đã đổi.
5. Operator: "fix ở đây, sẽ chỉ định update ở kho nguồn sau" → roadmap này.

Sao lưu: `AN C2\local-agent-workspace-v1.9.0\archive\MANIFEST.sha256.truoc-them-goi-bai-container-20261028` là MANIFEST gốc của bộ mẫu
trước mọi thay đổi ngày 28/10; MANIFEST hiện tại của bộ mẫu là sau thay đổi. So hai file này ra đúng tập file nhóm B.

## 2. Ba lớp khác biệt (đo ngày 28/10/2026, kho nguồn ở HEAD `b1ec507`, working tree có WIP)

| Lớp | Là gì | Quy mô | Hướng xử lý |
|---|---|---|---|
| **A — có sẵn trong bộ mẫu AN C2 trước 28/10** (nằm sẵn trong zip rc4, xem mục 2a) | Một dòng việc không có trong lịch sử Git của bất kỳ nhánh nào ở kho nguồn: `tools/skill_regression.py` + `docs/KIEM_HOI_QUY_SKILL_VI.md`, `examples/regression/`; skill `ra-soat-excel-sai-sot`, `ttport-lookup`, `tvpl-sync` (+ `tools/sync_tvpl.py`, `crawl_tvpl.py`, `sync_ttport.py`, `ttport_lookup.py`, `inspect_web.py`, `start_chrome_tvpl.bat`, hai `*_credentials.example.json`); `excel-workbooks/references/mo-hinh-gia-khung.md`, script `xlsx_xml_tools.py`, `check_offline_html.py`; mô tả SKILL.md viết lại theo "dùng khi", `install_skills.py --host/--scope`, `vn_legal_docx.py` bản khác | 306 file của bộ mẫu gốc: 198 giống kho nguồn hiện tại; **33 file không có ở kho nguồn**; **65 file khác cả HEAD**; 10 file chỉ khác vì kho nguồn đang sửa dở | **Quyết định operator trước** (mục 5): nguồn gốc, có đưa vào kho nguồn công khai không (ttport/TVPL là tích hợp riêng cần tài khoản) |
| **B — Claude sửa ngày 28/10** | Gói `cang-bai-container`; sửa công cụ; re-pin `.cvf`; số liệu tài liệu | 45 đường dẫn (bảng mục 3) | Theo các bước S2–S4 |
| **C — kho nguồn đang làm dở** | Gói `academic-research`, vai văn phòng, profile, test, `working/` | Working tree chưa commit tại thời điểm đo | Không đụng; chờ owner commit/khóa trước S2 |

Hệ quả quan trọng: **kho nguồn có 14 skill dùng chung** (thiếu 3 skill của lớp A), nên chữ "mười bốn" trong tài liệu kho nguồn **đang đúng**.
Phần sửa số "17 skill / 6 gói" của nhóm B chỉ đúng cho bộ mẫu AN C2; ở kho nguồn phải đếm lại sau khi quyết lớp A và cộng gói
`academic-research` (kho nguồn hiện có 6 gói thật; thêm `cang-bai-container` thành 7).

### 2a. Nguồn gốc lớp A (kiểm ngày 28/10/2026)

Operator cho biết quy trình: xuất từ kho gốc ra `D:\UNG DUNG AI\local-agent-workspace-v1.9.0-rc4.zip`, giữ nguyên zip, giải nén vào `AN C2`
để làm việc. Bằng chứng đo được:

- **AN C2 trước khi sửa = zip rc4:** MANIFEST trong zip trùng byte với MANIFEST gốc của AN C2 (sao lưu ở `archive/`); 304/306 file trùng nội dung,
  `APP.bat`/`SETUP.bat` chỉ khác EOL. Bản `D:\UNG DUNG AI\BICH TRANG 2026\local-agent-workspace-v1.9.0` cũng giải nén từ zip này (thư mục tạo
  12:52 25/10), sau đó bị sửa 12 file khi dùng làm project.
- **Zip rc4 không khớp commit nào của kho nguồn:** zip tạo 25/10 12:47:56 (định dạng `build_release.py`, ngày entry 1980-01-01), giữa
  `baa26c9` (11:47) và `b1ec507` (12:49); cả hai commit, thẻ `v1.9.0-rc4` (`2552d7d`, 23/10), `origin/main`, worktree
  `working/v7-internal/source-integration` (`codex/office-prototype-source`), stash và commit mồ côi đều **không có** `tools/skill_regression.py`,
  `ttport-lookup`, `tvpl-sync`, `ra-soat-excel-sai-sot`. `dist/` của kho nguồn chỉ có rc2. Không tìm thấy bản nào khác của các file này trong
  `D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace` (sâu 7 cấp) ngoài các bản giải nén từ zip.
- **Kho nguồn đã quyết không nhận lớp này:** nội dung `baa26c9` ghi lượt tiếp nhận chọn lọc từ bản local: nhận phần Word/ND30; "Installer host
  mappings, TVPL/ttport integrations, private skills and Excel-XML editing scripts were not accepted in this intake"; bản grader
  `skill_regression` local không được nhận; giữ 14 skill.

- **Đối chiếu GitHub (28/10, chỉ đọc):** `main` trên GitHub = `b1ec507` (chưa có phần học thuật, khớp `main` local); release `v1.9.0-rc4`
  trỏ `2552d7d`, asset `local-agent-workspace-v1.9.0-rc4.zip` 1.280.988 byte, sha256 `645fe02c…7129`, tải lên 23/10, 273 file, không có
  `skill_regression`/ttport/TVPL. Zip ở `D:\UNG DUNG AI` cùng tên nhưng sha256 `fccab52d…9433`, 1.425.386 byte, tạo 25/10, 308 file
  (thêm 35 file, khác nội dung 50 file). GitHub `main` cũng không có `tools/skill_regression.py`, `skills/local/shared/ttport-lookup/`.
  ⇒ Zip operator dùng **không phải** asset rc4 chính thức và **không dựng từ `main`**; chỉ trùng tên.

Kết luận: AN C2 khác kho nguồn **không chỉ ở gói học thuật**. Zip rc4 mang theo lớp A mà kho nguồn đã chủ ý không nhận. Chưa xác định được
thư mục đã dựng zip (có thể là workspace bảo trì/local trial còn giữ các ứng viên lúc đóng gói). Mặc định khi đồng bộ: **không đưa lớp A vào
kho nguồn**, giữ đúng quyết định của `baa26c9`, trừ khi operator chỉ định khác (mục 5). Các sửa nhóm B nằm trong file lớp A
(`tools/skill_regression.py`; số "17 skill" vì có 3 skill lớp A) không áp cho kho nguồn.

## 3. Nhóm B — thay đổi ngày 28/10 và cách đưa về

Phân loại so với kho nguồn tại thời điểm đo. **Đo lại ngay trước khi áp** (script mục 6), vì working tree kho nguồn đang đổi.

| Thay đổi | File | Trạng thái kho nguồn 28/10 | Cách đưa về |
|---|---|---|---|
| Gói mới `cang-bai-container` 0.1.0 | `packs/cang-bai-container/` (7 file: `pack.json`, `README.md`, `references/intake-record.md`, `skills/container-yard-check/SKILL.md` + 3 `references/*.md`) | Chưa có | Chép nguyên thư mục; `pack.py check cang-bai-container`; id không trùng `academic-research` |
| UTF-8 stdout/stderr **trước** `parse_args` (để `--help`, lỗi tham số không sập khi pipe cp1252) | `tools/check_output.py`, `context_update.py`, `current_draft.py`, `init_project.py`, `native_agents.py`, `office_compute.py`, `upgrade_package.py` | Bằng bản gốc | Áp thẳng |
| (như trên) | `tools/check_package.py`, `execution_profile.py`, `install_skills.py`, `office.py`, `pack.py`, `transaction.py` | **Đã đổi** (WIP và/hoặc lớp A) | Hợp nhất tay: chuyển khối `if hasattr(sys.stdout, 'reconfigure')` lên trước `parse_args`, thêm `sys.stderr` (giữ `errors='replace'` ở `execution_profile`/`native_agents`) |
| (như trên) | `tools/skill_regression.py` | Không có (lớp A) | Chỉ khi lớp A được nhận |
| `--help` chỉ in cách dùng | `tools/app.py` (không mở server), `tools/setup_wizard.py` (không hỏi đáp) | Bằng bản gốc | Áp thẳng |
| Cảnh báo CRLF bỏ qua đường dẫn khai `-text` trong `.gitattributes` (hàm `raw_byte_paths`), như kiểm EOL kho nguồn đã làm | `tools/check_package.py` | **Đã đổi** | Hợp nhất tay; cảnh báo cũ là báo nhầm với `tools/publish_new.py` (bytes CRLF đã pin trong policy v3) |
| Re-pin P-CTX1 | `.cvf/rules/v3/ROUTING_POLICY.json` (chỉ `operational_context_protocol.entrypoint_sha256`) | Bằng bản gốc | **Không chép hash**: tính lại từ bytes `tools/context_update.py` cuối cùng ở kho nguồn (mục 4) |
| Số skill/gói trong tài liệu, START_HERE (dải số liệu sửa tay), danh sách gói, câu "mỗi gói có căn cứ pháp lý" | `skills/README.md`, `en/skills/README.md`, `packs/README.md`, `docs/HUONG_DAN_SU_DUNG_VI.*`, `docs/HUONG_DAN_TAO_PROJECT_MOI_VI.*`, `docs/en/DAILY_USE_GUIDE.*`, `docs/en/NEW_PROJECT_GUIDE.*` | Bằng bản gốc | **Không chép số**: viết lại theo số đếm thật ở kho nguồn; rồi `build_guides_html.py` |
| (như trên) | `.agent/SKILL_INDEX.md`, `en/.agent/SKILL_INDEX.md`, `docs/HUONG_DAN_SKILLS_VI.*`, `docs/en/SKILLS_GUIDE.*`, `en/README.md`, `START_HERE.html`, `START_HERE.en.html` | **Đã đổi** | Hợp nhất tay, cùng nguyên tắc |
| Ghi chép | `CHANGELOG.md` | **Đã đổi** | Thêm mục mới vào "Chưa phát hành" của kho nguồn; không chép cả file |
| `MANIFEST.sha256` | — | — | Không chép; tính lại bằng quy trình người bảo trì của kho nguồn |

Không chép: `archive/` của bộ mẫu, `MANIFEST.sha256`, file người dùng (`PROJECT.md`, `.agent/STATE.md`, `HANDOFF.md`...), không chép cả thư mục.

## 4. Bẫy đã biết

- **Pin bytes thô.** `tools/publish_new.py` (CRLF, `-text`) và `tools/context_update.py` (`-text`) được pin trong
  `.cvf/rules/v3/ROUTING_POLICY.json`; `publish_new.py` còn được nhắc trong `CONTROL_CONTRACT.md`. Bộ mẫu AN C2 đổi pin P-CTX1 từ
  `sha256:ee7cb6b1…6248` sang `sha256:49dbeec4…` theo bytes mới. Pin này `VERSION_COMPARE_ADVISORY`, nhưng `current_draft.readiness`
  và `check_package.pin_problems` so đúng bytes: lệch ⇒ `CONTEXT_OWNER_PIN_MISMATCH` (thẻ Nháp hiện tại không dùng được). Đã thử trên
  bộ mẫu: pin mới ⇒ `usable: True`; đặt lại pin cũ ⇒ bị từ chối.
- **Test kho nguồn ghi cứng pin.** `tests/test_current_draft.py` có pin cũ của `context_update.py`; năm file test và `CONTROL_CONTRACT.md`
  có pin `publish_new.py` (không đổi). Bộ mẫu không giao `tests/` nên phiên AN C2 không kiểm được phần này: cập nhật cùng lần re-pin.
- **EOL.** `.gitattributes`: `* text=auto eol=lf`, ngoại lệ `-text` cho file đã pin. Giữ đúng EOL khi chép; chạy `check_package.py --check-eol`
  (chỉ chạy được ở kho nguồn có Git) cho mọi file đã sửa.
- **Đếm thư mục ẩn.** `glob('**/*')` của Python bỏ qua `.cvf/`; dùng `include_hidden=True` khi dò pin.
- **`grep -c $'\r'` trong Git Bash cho kết quả sai** (báo mọi file là CRLF); đếm bằng Python trên bytes.
- **Sửa chuỗi tiếng Việt bằng script**: kiểm số lần khớp trước khi ghi (đã gặp lệch Unicode khiến thay thế trượt).
- **Chạy thử công cụ.** `app.py`, `setup_wizard.py` bản cũ không hiểu `--help` (mở server/hỏi đáp); thử hàng loạt thì đặt timeout và `stdin=DEVNULL`.

## 5. Quyết định operator cần trước khi làm

Trạng thái cập nhật cuối phiên 28/10:

| # | Quyết định | Trạng thái |
|---|---|---|
| 0 | Làn "người xây dựng nhận skill" (6a) + quy tắc R1–R5 (6b) | **Operator đồng ý về nguyên tắc** (quét trước, chống phình thay cho đếm số lần dùng, vùng riêng theo đơn vị). Bảng áp ứng viên ở 6a: **chờ xác nhận từng dòng** khi bắt đầu |
| 1 | Lớp A | Operator cho rằng zip dựng từ `main`; bằng chứng 2a cho thấy không (asset GitHub khác mã băm). Mặc định: không đưa lớp A nguyên khối; xử lý từng ứng viên theo bảng 6a. `ttport-lookup`/`tvpl-sync` → vùng riêng R3, không lên GitHub |
| 2 | Thứ tự với nhánh học thuật | **Chưa trả lời.** Khuyến nghị: đồng bộ sau khi WIP học thuật được commit |
| 3 | Intake gói `cang-bai-container` | Đề xuất `ROOT_ELIGIBLE` + `root_grant` operator (6a); xác nhận cùng #0 |
| 4 | Vùng riêng không lên GitHub, sao lưu Google Drive, `.gitignore` | **Đã chốt** (6b R3) |

## 6. Các bước

| Bước | Việc | Điều kiện xong |
|---|---|---|
| S0 | Chờ/được xác nhận WIP lớp C đã commit; tạo nhánh riêng (gợi ý `sync/an-c2-20261028`) từ HEAD mới | Working tree sạch trên nhánh đồng bộ |
| S1 | Ghi quyết định mục 5 vào roadmap này | Có câu trả lời cho 1–3 |
| S2 | Đo lại bằng script dưới; áp các file "bằng bản gốc" của nhóm B và gói mới | Script báo các file đó `DA GIONG ban da sua` |
| S3 | Hợp nhất tay các file "đã đổi"; viết lại số skill/gói theo số đếm thật; `python tools/build_guides_html.py` | `build_guides_html.py --check` đạt; không còn chữ số cũ sai |
| S4 | Re-pin P-CTX1 theo bytes `context_update.py` cuối cùng; cập nhật `tests/test_current_draft.py`; tính lại MANIFEST theo quy trình kho nguồn | `check_package.py` 0 lỗi/0 cảnh báo; `--check-eol` các file đã sửa; `python -m unittest discover -s tests` đạt; `current_draft.readiness` `usable`; 36/36 `tools/*.py --help` chạy dưới `PYTHONIOENCODING=cp1252`; `new_project.py` xem trước được; `pack.py check` mọi gói |
| S5 | CHANGELOG, `.agent/HANDOFF.md`, cập nhật trạng thái roadmap này | Operator xác nhận; ghi revision |

Script đo (chạy từ bất kỳ đâu, chỉ đọc):

```python
import hashlib, os
T = r"D:\UNG DUNG AI\TOOL AI 2026\AN C2\local-agent-workspace-v1.9.0"
S = r"D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\local-agent-workspace"
def man(p):
    d = {}
    for line in open(p, encoding='utf-8'):
        if line.strip():
            h, r = line.rstrip('\n').split('  ', 1); d[r] = h
    return d
old = man(os.path.join(T, 'archive', 'MANIFEST.sha256.truoc-them-goi-bai-container-20261028'))
new = man(os.path.join(T, 'MANIFEST.sha256'))
def sha(p):
    return hashlib.sha256(open(p, 'rb').read().replace(b'\r\n', b'\n')).hexdigest()
for r in sorted(set(old) | set(new)):
    if old.get(r) == new.get(r):
        continue
    sp = os.path.join(S, r)
    if r not in old: st = 'MOI' if not os.path.exists(sp) else 'MOI nhung DA CO cung ten'
    elif not os.path.exists(sp): st = 'kho nguon KHONG CO'
    else:
        s = sha(sp); st = 'bang ban goc' if s == old[r] else ('DA GIONG ban da sua' if s == new[r] else 'DA DOI - hop nhat tay')
    print('%-28s %s' % (st, r))
```

## 6a. Quan điểm operator (28/10/2026) và đề xuất làn tiếp nhận của người xây dựng

**Quan điểm operator (nguyên ý):** project gốc nên nhận từ các folder local những skill mới như gói vừa tạo ở AN C2, vì operator và agent
bảo trì là **người xây dựng**, không phải người dùng cuối; làm giàu kho skill nếu skill hữu ích và **không trùng** skill native sẵn có của
provider/agent (Claude, Codex, Antigravity...). Chuẩn sáu điều kiện và trung tâm tiếp nhận vẫn giữ cho người nhận folder gửi phản hồi.

**Đề xuất (Claude, chờ operator chốt):** thêm một làn "người xây dựng nhận skill" vào `skills/README.md`, gọn hơn sáu điều kiện, đặt ở kho
nguồn; mỗi ứng viên qua năm câu, trả lời ngắn trong `CHANGELOG`/`SKILL_INDEX` Notes, không tạo sổ mới:

1. **Không trùng native:** native lo thao tác file (docx/xlsx/pptx/pdf, chart...); skill chỉ nhận phần native không có: quy tắc nghiệp vụ,
   mẫu, nguồn, script kiểm. Ghi rõ đã đối chiếu provider nào; provider chưa kiểm thì ghi chưa kiểm, không suy là thiếu.
2. **Chung hay riêng:** kiến thức lĩnh vực → gói (`packs/`); quy tắc của một đơn vị (tên block, người ký, tài khoản, site nội bộ) →
   skill riêng của project hoặc gói riêng không phát hành công khai.
3. **An toàn:** không credential/dữ liệu thật; script chỉ đọc hoặc ghi file mới; mạng và site bên thứ ba thì nêu rõ, kiểm điều khoản sử dụng.
4. **Đã dùng thật ít nhất một lần** bởi người xây dựng (việc thật, kết quả kiểm được); đủ thay cho yêu cầu "ba việc thật" của gói người dùng gửi.
5. **Kiểm cơ học đạt:** `pack.py check`, `check_package.py`, `build_guides_html.py --check`, selftest nếu có.

Đạt cả năm: skill vào kho nguồn với Status `AVAILABLE` (như 14 skill gốc do người duy trì đưa vào); gói ghi `intake.decision`
`ROOT_ELIGIBLE` + `root_grant` (operator, ngày). Ở từng project, người dùng vẫn tự `pack.py confirm` (giữ quyền của người dùng cuối).

**Áp vào các ứng viên hiện có (đề xuất):**

| Ứng viên | Đề xuất | Lý do |
|---|---|---|
| Gói `cang-bai-container` (AN C2, 28/10) | Nhận, `ROOT_ELIGIBLE` | Rút từ việc thật đã kiểm; quy tắc riêng Tân Thuận đã đưa thành câu hỏi/khóa cấu hình; chỉ `.md`; native không có quy tắc bãi container |
| `ra-soat-excel-sai-sot` (lớp A) | Nhận sau khi đọc lại, shared | Quy trình rà soát/sổ sai sót bổ sung cho skill xlsx native (native tạo/sửa file, không có quy trình audit); 3 script cần openpyxl, đọc lại phạm vi ghi |
| `skill_regression.py` local (lớp A) | Sửa rồi nhận | `baa26c9` đã nêu lỗi cụ thể (kiểm trích dẫn yếu, thiếu ca, Excel không tính lại); xử lý đúng các điểm đó |
| `excel-workbooks` extras (`mo-hinh-gia-khung.md`, `xlsx_xml_tools.py`), `check_offline_html.py` | Đọc lại từng file, nhận phần generic | Bổ sung skill đã có; script cần đọc phạm vi ghi |
| `install_skills.py --host/--scope` (lớp A) | Hoãn tới khi thử trên host thật | Tuyên bố đường dẫn native của từng host phải đo, không suy |
| `tvpl-sync` + công cụ | Không đưa vào kho công khai; gói riêng tùy chọn | Cần tài khoản; có cơ chế vượt Cloudflare Turnstile ⇒ rủi ro điều khoản site khi phát hành công khai |
| `ttport-lookup` + công cụ | Skill riêng của project Tân Thuận | Site nội bộ một đơn vị, cần tài khoản |

**Quy trình phát hành đi kèm:** zip phát hành chỉ dựng từ commit của `main` bằng `build_release.py`; bản dựng thử từ thư mục local đặt tên
khác (ví dụ `...-local-YYYYMMDD.zip`), không trùng tên rc. Đổi tên zip 25/10 ở `D:\UNG DUNG AI` để khỏi nhầm với rc4 chính thức (mục 2a).

## 6b. Chỉ định bổ sung của operator (28/10/2026) và quy tắc đề xuất hoàn chỉnh

**Chỉ định operator:**

1. Khi operator yêu cầu cập nhật skill vào project gốc, **agent/tool có trách nhiệm quét, rà soát, phân loại trước** khi nhập, tạo mới hay cập
   nhật. Project gốc đồng bộ với GitHub (`https://github.com/CVF-Ecosystem/local-agent-workspace.git`) để đối soát chéo. Tránh lộn xộn như
   lần zip 25/10 (mục 2a).
2. Dùng một lần hay nhiều lần **không phải rào cản** với người xây dựng. Điều cần giữ là tiêu chí kiểm soát: kho skill không phình, không
   sinh skill lặt vặt hoặc gần giống nhau.
3. Skill riêng của đơn vị để trong **thư mục nhỏ đặt theo tên đơn vị/tên gói**, dễ quản lý, truy xuất; khi đóng gói gửi người khác thì không
   lẫn vào kho chung; operator vẫn dùng chúng khi làm việc.

**Quy tắc đề xuất (Claude; điều chỉnh mục 6a, chờ operator chốt):**

**R1. Quét trước, ghi sau (bắt buộc với mọi lần cập nhật skill).** Agent chạy một lượt quét chỉ đọc và trình báo cáo phân loại trước khi ghi
bất kỳ file nào. Mỗi ứng viên nhận đúng một nhãn:

| Nhãn | Nghĩa | Hành động |
|---|---|---|
| `MOI` | Việc mới, không skill nào đang phục vụ | Tạo skill/gói mới |
| `CAP_NHAT` | Bản mới của skill đã có (cùng id) | Hợp nhất vào skill đó, nâng `metadata.version` |
| `BO_SUNG` | Gần một skill đã có (cùng loại đầu ra/tình huống dùng) | Thêm vào `references/` hoặc mục của skill có sẵn, **không tạo id mới** |
| `TRUNG_NATIVE` | Native của provider đã làm được | Không nhập; chỉ giữ phần quy tắc nghiệp vụ nếu có |
| `RIENG_DON_VI` | Quy tắc/tài khoản/site của một đơn vị | Vào vùng riêng (R3), không vào kho công khai |
| `DA_TU_CHOI` | Đã có quyết định không nhận trước đó (ví dụ `baa26c9`) | Chỉ nhận lại khi nêu được điều đã thay đổi |
| `TAM` | Thử nghiệm, chưa đủ để giữ | Để ngoài kho (`working/`), không ghi chỉ mục |

Báo cáo quét gồm: đường dẫn nguồn + mã băm MANIFEST/zip của nguồn; so với `main` local **và** GitHub (`git ls-remote`, release asset);
danh sách file mới/khác/thiếu theo mã băm; skill gần trùng theo tên, mô tả, "dùng khi"; dấu hiệu tài khoản, mạng, dữ liệu thật. Operator chỉ
cần quyết các dòng `RIENG_DON_VI`/`BO_SUNG` còn phân vân. Đề xuất thêm công cụ chỉ đọc `tools/skill_scan.py` để làm bước này lặp lại được
(tái dùng logic so MANIFEST ở mục 6 và kiểm cấu trúc của `pack.py check`).

**R2. Chống phình thay cho đếm số lần dùng.** Một id = một loại đầu ra/công việc rõ ràng. Mô tả có "dùng khi" và "không dùng khi". Ưu tiên
`BO_SUNG` hơn `MOI`. `SKILL.md` gọn (khung và quy tắc), chi tiết ở `references/`. Mọi skill mới phải chỉ ra skill gần nhất đã có và vì sao không
gộp được. Khi nhập, rà luôn chỉ mục: skill trùng chức năng thì gộp, skill không còn dùng thì chuyển `archive/`. Tiêu chí kiểm (không trùng
native, an toàn, kiểm cơ học đạt) giữ nguyên như mục 6a; bỏ yêu cầu số lần dùng với người xây dựng.

**R3. Vùng skill riêng theo đơn vị.** Cấu trúc đề xuất:

```text
skills/local/project/<don-vi-hoac-goi>/<skill-id>/SKILL.md   (+ references/, scripts/)
  ví dụ: skills/local/project/tan-thuan/ttport-lookup/
         skills/local/project/tan-thuan/doi-cont-bao-cao/
         skills/local/project/tvpl/tvpl-sync/
         skills/local/project/merck-bich-trang/...
skills/local/project/<don-vi>/README.md   đơn vị, phạm vi, tài khoản cần (không ghi giá trị), người phụ trách
```

- Đã kiểm 28/10: `skills/local/project/` nằm trong `USER_DIRS` của `tools/check_package.py`, **không vào bản giao** (chỉ README mẫu), nên
  gửi bộ mẫu cho người khác không lẫn skill riêng.
- **Quyết định operator (chốt 28/10):** skill riêng của project/đơn vị **không đưa lên GitHub** để hạn chế lộ thông tin; bản đầy đủ của
  project (kể cả vùng riêng) lưu ở **Google Drive cá nhân** của operator. Việc cần làm khi đồng bộ: thêm vào `.gitignore` của kho nguồn
  `skills/local/project/*/` (giữ `skills/local/project/README.md`) để chặn lỡ đẩy; trước mỗi lần push, báo cáo quét R1 kiểm thêm rằng
  không có file dưới `skills/local/project/<don-vi>/` hay file tài khoản trong `git ls-files`. Không lập kho GitHub riêng tư cho vùng này.
- Lưu ý khi lưu lên Drive: không để Drive đồng bộ trực tiếp thư mục đang làm việc có `.git` (đồng bộ dở có thể làm hỏng kho Git); sao lưu
  dạng zip có ngày hoặc thư mục bản sao. File tài khoản thật (`*credentials*.json`, `.env`) không chia sẻ thư mục Drive chứa chúng.
- *(Lịch sử trao đổi, đã thay bằng quyết định trên)* Operator từng nêu đẩy đầy đủ lên GitHub; dữ kiện kiểm 28/10 qua `gh`: `CVF-Ecosystem/local-agent-workspace` đang `PUBLIC`, 6 release, 381 lượt clone trong 14
  ngày. Đẩy vùng riêng lên kho này thì mọi người xem được (quy tắc nội bộ Tân Thuận, site ttport, cơ chế vượt Turnstile của TVPL, thông tin
  khách hàng/thuốc trong skill MERCK). Ba phương án đã nêu (operator chọn không đưa lên GitHub, xem quyết định trên):
  1. Đẩy đầy đủ lên kho công khai hiện tại, chấp nhận công khai (chỉ khi nội dung đơn vị không cần giữ kín).
  2. Đổi kho hiện tại thành `PRIVATE` để đồng bộ đầy đủ; phát hành công khai qua kho/release riêng dựng từ `main` (bản giao vẫn loại
     `skills/local/project/`). Hệ quả: link clone/release công khai hiện có ngừng hoạt động.
  3. Giữ kho công khai cho sản phẩm; vùng riêng là một kho Git riêng tư lồng tại `skills/local/project/` (kho ngoài bỏ qua thư mục con),
     đồng bộ thiết bị bằng hai lần clone. Ít đổi nhất cho kho hiện tại.
- Dù chọn cách nào, bản **giao đi** vẫn không chứa vùng riêng (`USER_DIRS`), nên gửi bộ mẫu cho người khác không lẫn.
- Khi làm việc: vùng riêng nằm ngay trong project của operator tại `skills/local/project/<don-vi>/` (bản lưu đầy đủ trên Google Drive),
  ghi `SKILL_INDEX` Scope `PROJECT`. Tránh hai bản sống: skill tài khoản Claude/Codex (ví dụ các skill đơn vị đã có trên tài khoản Claude)
  xuất ra từ vùng này, không sửa riêng ở hai nơi.
- `check_package.py --release` nên chặn nếu bản giao chứa đường dẫn dưới `skills/local/project/<don-vi>/` hoặc file tài khoản.

**R4. Một đường đồng bộ với GitHub.** Mọi lần nhập: nhánh riêng → commit ghi dòng xuất xứ (thư mục nguồn, mã băm MANIFEST/zip, nhãn R1) →
kiểm (mục 6, S4) → push → PR → `main`. Phát hành chỉ dựng từ `main`, ghi tên + mã băm asset vào CHANGELOG/roadmap; bản dựng local đặt tên
`...-local-YYYYMMDD.zip`. Đối soát chéo = so MANIFEST của bản đang dùng với asset/`main` trên GitHub (cách đã làm ở mục 2a).

**R5. Ghi chép một chỗ.** Kết luận nhập ghi ở `CHANGELOG.md` (kho nguồn) + cột Notes của `.agent/SKILL_INDEX.md`; vùng riêng ghi ở
`skills/local/project/<don-vi>/README.md` (không lên GitHub). Không tạo sổ tiếp nhận mới.

**R6. Gói sao lưu sạch (liên quan, làm ở CVF gốc).** Operator giao riêng cho CVF gốc (`D:\UNG DUNG AI\TOOL AI 2026\Controlled-Vibe-Framework-CVF`)
một chuẩn + công cụ "gói sao lưu sạch" để sao lưu thủ công lên Google Drive/OneDrive: tách ba loại đóng gói (phát hành từ `main` / giao người
khác / sao lưu cá nhân), tên `<ten>_saoluu_<YYYYMMDD-HHMM>.zip`, lịch sử Git dạng `git bundle`, loại thư mục dựng/cache và file tài khoản,
manifest + sha256, thử khôi phục. LAW nhận bản tương ứng **sau khi CVF chốt**, qua một lần cập nhật riêng; không làm trong roadmap này.

## 7. Đã kiểm trên bộ mẫu AN C2 (không phải bằng chứng cho kho nguồn)

`check_package.py`: 0 lỗi, 0 cảnh báo; `--verify`: 0 file đổi; `build_guides_html.py --check`: 10 trang khớp; `pin_problems`: OK;
selftest `vn_legal_docx`, `docx_helpers`, `skill_regression` đạt; 36/36 công cụ `--help` dưới cp1252; tạo project mới từ bộ mẫu, cài
`cang-bai-container` ghi `REVIEW`; `current_draft.readiness` `usable` (pin cũ bị từ chối). Không kiểm: test kho nguồn, `--check-eol`
(cần Git), giao diện `app.py`, luồng nâng cấp package, công cụ cần mạng/tài khoản.
