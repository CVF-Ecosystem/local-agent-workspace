# Catalog cấu trúc project và tiến độ

Một bản đồ dùng chung để mọi agent (Claude, Codex, Gemini) và operator đọc cấu trúc kho nguồn LAW giống nhau, kèm tiến độ theo tranche.
File này chỉ có ở kho nguồn (nằm trong `roadmap/`, không thuộc bản phân phối) và được đăng trên GitHub chủ yếu để agent bên ngoài đọc.
Nó là bản tra nhanh, không phải nguồn sự thật: khi lệch với file thực, STATE, HANDOFF hoặc roadmap thì file thực thắng; nêu chỗ lệch cho operator thay vì tự sửa.

**Cập nhật lần cuối:** 04/11/2026 · nền: `main` tại `62c942e` · Local roadmap `LOCAL-ROADMAP-20261104-r1`. Dữ liệu tiến độ chỉ mới đến mốc này; nếu ngày hiện tại muộn hơn nhiều, coi mục 5–6 có thể đã cũ và đối chiếu `.agent/STATE.md`.

## 1. Cách dùng và cách cập nhật

- **Agent bên ngoài (chỉ đọc):** đọc `AGENTS.md` trước, rồi file này để nắm bố cục và tiến độ. Không sửa file này, không suy quyền thi công từ nó; muốn đề xuất thay đổi thì báo operator.
- **Đọc:** mục 2–3 để biết thư mục/tool nào làm gì và ai được ghi; mục 4 để biết mở gì khi gặp tình huống; mục 5–6 để biết đang ở đâu.
- **Cập nhật chỉ khi operator nhắc** (thường sau khi đóng một tranche), do agent local làm: ghi một dòng vào mục 6, sửa dòng tương ứng ở mục 5, và sửa mục 2–4 chỉ khi cấu trúc thật sự đổi (thư mục, tool, vai, owner mới/bỏ). Không tự cập nhật khi chưa được nhắc.
- **Giữ ngắn:** không chép điều kiện đóng từ roadmap, không dán log, không ghi số đếm file/dòng/test (chóng lỗi thời; cần số thì chạy lệnh và ghi kèm ngày). Mục 6 giữ tối đa khoảng 10 dòng mới nhất, dòng cũ hơn đã có ở `.agent/HANDOFF.md` và `archive/`.
- **Không thay** `.agent/STATE.md` (hiện trạng ngắn), `.agent/HANDOFF.md` (bàn giao và brief) hay roadmap (điều kiện đạt mốc). Catalog trỏ tới chúng.
- **Quy tắc 10 của `AGENTS.md`:** đóng một tranche không tự có nghĩa đã đạt mốc sản phẩm. Cột trạng thái ở mục 5 theo bằng chứng, không theo số tranche đã xong.
- Không ghi mật khẩu, khóa hay dữ liệu cá nhân vào đây (quy tắc 5).

## 2. Bản đồ thư mục

Cột "Ghi" cho biết ai thường được sửa: **BT** = người bảo trì kho nguồn theo tranche; **ND** = dữ liệu của người dùng/project, agent không tự ghi đè (quy tắc 3); **SINH** = sinh bằng công cụ, không sửa tay; **GHIM** = bytes đã ghim bằng hash/EOL, xem `.gitattributes` và `MANIFEST.sha256`.

| Đường dẫn | Vai trò | Giao cho người dùng? | Ghi |
|---|---|---|---|
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `en/` cùng tên | Điểm vào chung cho agent; CLAUDE/GEMINI chỉ là adapter | Có | BT, GHIM theo allowlist merge |
| `README.md`, `START_HERE*.html`, `CHANGELOG.md`, `VERSION`, `LICENSE` | Giới thiệu, lịch sử, nhãn phiên bản | Có | BT; `MANIFEST.sha256` tính lại lúc phát hành |
| `PROJECT.md` | Ngữ cảnh ổn định của project (ở kho nguồn là mẫu còn placeholder) | Có (mẫu) | ND |
| `.agent/` | `STATE.md`, `HANDOFF.md`, `INDEX.md` (sổ nguồn), `SKILL_INDEX.md`, `EXECUTION_PROFILE.json` (+ schema), `PENDING_LESSONS.md`; `runtime/`, `private/` | Mẫu sạch từ `release_templates/` | ND; STATE/HANDOFF qua `tools/context_update.py` khi cần |
| `.cvf/` | Quy tắc kiểm soát (`rules/` v2, v3; bảng routing), hợp đồng (`contracts/` v1, v2, v3), checker (`checks/`) | Chỉ phần closure v3 | BT; v1/v2 là lịch sử, GHIM |
| `roles/` | Hợp đồng Scout / Worker / Reviewer (`agent.md`, `checks.md`, `config.json`); `roles/office/` giữ `MAIN.md`, `catalog.json` và sáu phương pháp văn phòng | Có | BT |
| `tools/` | Công cụ Python vận hành/bảo trì (mục 3) | Có | BT; một số file GHIM (`publish_new.py`, `context_update.py`) |
| `tests/` | Bộ kiểm unittest cho tools, `.cvf`, panel, vòng đời nâng cấp, phát hành | Không | BT |
| `skills/` | `local/shared/` (14 skill dùng chung), `local/project/`, `local/packs/`; chuẩn tiếp nhận ở `skills/README.md` | Có | BT cho shared; project/packs thuộc ND |
| `packs/` | Gói lĩnh vực: `phap-ly`, `van-thu-luu-tru`, `ke-toan-noi-bo`, `hanh-chinh-nhan-su`, `cang-logistics`, `academic-research`, `_template` | Có (cài bằng `tools/pack.py`) | BT; gói cài vào project ghi `REVIEW` đến khi người dùng xác nhận |
| `references/` | Thư viện nguồn của project (`legal`, `policies`, `templates`, `source-documents`) và sổ `_INDEX.xlsx` | README mẫu | ND; sổ chỉ ghi qua `tools/library*.py` |
| `working/` | Việc đang làm; ở kho nguồn là thư mục làm việc của từng tranche (nhiều thư mục `*-2026MMDD`) và `_scratch` | README mẫu | ND/BT; hầu hết không vào git |
| `output/` | Bản giao hiện hành | README mẫu | ND |
| `archive/` | Bản cũ, bằng chứng lịch sử (`maintainer/` giữ bytes trước khi thay) | README mẫu | ND/BT; chỉ thêm, không sửa lại |
| `examples/demo-project/` | Dữ liệu mẫu cho bài thực hành | Có | BT |
| `docs/` (+ `docs/en/`) | Hướng dẫn người dùng; `*.html` là bản dựng | Có | BT; HTML là SINH bằng `tools/build_guides_html.py` |
| `en/` | Cây tiếng Anh của các file có nội dung ngôn ngữ | Có | BT; phải khớp cây tiếng Việt |
| `assets/` | Logo, `branding.*`, chỗ đặt font riêng (`assets/fonts/`) | Có | ND cho font |
| `release_templates/` | Mẫu sạch (PROJECT, `.agent`, `.cvf/README`) dùng khi dựng bản giao | Không | BT |
| `feedback/` | Phiếu và bản ghi phản hồi từ các lượt thử | Không | BT |
| `roadmap/` | Roadmap, brief, review, quyết định operator, `evidence/` theo tranche; file này | Không | BT; roadmap hiện hành: `ROADMAP_VAN_PHONG_NGHIEP_VU.md` (mục Local 04/11) liên kết từ `ROADMAP_HOAN_THIEN.md` |
| `.github/` | `RELEASING.md` (gate phát hành), `workflows/ci.yml`, mẫu issue phản hồi | Không | BT |
| `dist/` | ZIP phát hành, `.gate.json`, `.sha256`, log dựng | Không (không vào git) | SINH |

## 3. Bản đồ code `tools/`

Chạy từ thư mục gốc. Dùng `python -X utf8 -B tools/<file>.py ...`; không dùng `-I` với CLI trong `tools/`. Thiếu `openpyxl` thì báo thiếu, không tự cài. Chi tiết lệnh: `tools/README.md`.

| Nhóm | File | Việc chính |
|---|---|---|
| Giao diện | `app.py`, `app_ui.html`, `APP.bat`/`APP.command` | Bảng điều khiển trình duyệt cục bộ; mỗi nút gọi một tool với tham số cố định |
| Tạo / chuyển / nâng cấp project | `new_project.py`, `init_project.py`, `adopt_project.py`, `upgrade_package.py`, `setup_wizard.py` | Tạo bản sao từ bộ mẫu, nhận project có sẵn, nâng cấp ba bên theo MANIFEST |
| Đóng gói / phát hành | `check_package.py`, `build_release.py`, `build_guides_html.py` | Danh sách file giao, kiểm closure và tài liệu, dựng ZIP và gate |
| Ghi file an toàn | `transaction.py`, `publish_new.py`, `context_update.py`, `current_draft.py`, `merge_center.py` | Giao dịch có phục hồi, ghi file mới không đè, ghi STATE/HANDOFF theo `expected_before`, con trỏ nháp hiện tại, hợp nhất `.new` |
| Thư viện nguồn | `library.py`, `library_sync.py`, `library_audit.py`, `library_intake.py`, `check_quotes.py`, `source_response.py` | Sổ `_INDEX.xlsx`, đồng bộ ID/revision, nhập file chờ, kiểm trích dẫn, phản hồi theo nguồn |
| Vai và điều phối | `office.py`, `office_compute.py`, `task_checkpoint.py`, `native_agents.py`, `execution_profile.py`, `artifacts.py`, `work_status.py` | Soạn brief theo phương pháp, tính số bằng Decimal, kiểm TASK/RESULT, xuất vai native Claude Code, profile quyền, lineage artifact, trạng thái việc cho APP |
| Kiểm đầu ra / script | `check_output.py`, `audit_scripts.py`, `result_schema.py`, `ops_log.py` | Kiểm Word/khai báo thực hiện, vị trí script, schema `result-v1`, nhật ký thao tác |
| Skill và gói | `pack.py`, `install_skills.py` | Cài/xác nhận gói lĩnh vực, chép skill đã nhận sang ứng dụng |
| Văn bản pháp lý Word | `vn_legal_docx.py` | Renderer thể thức văn bản hành chính |

## 4. Mở gì khi gặp tình huống

| Tình huống | Mở trước |
|---|---|
| Nhận việc văn phòng thường | `AGENTS.md`, rồi `PROJECT.md`; việc tự đủ ngữ cảnh thì làm thẳng |
| Tiếp việc dở | `.agent/STATE.md`, rồi `.agent/HANDOFF.md` đúng đoạn cần |
| Cần nguồn / trích dẫn | `python tools/library.py find <từ khóa>`, skill `source-library` |
| Chọn skill | `.agent/SKILL_INDEX.md` cột "Use when" |
| Giao việc cho Scout/Worker/Reviewer | `roles/README.md`, `roles/office/MAIN.md`, `.cvf/rules/CONTROL_RULES.md`, `.agent/EXECUTION_PROFILE.json` (`python tools/execution_profile.py status`) |
| Sửa code/tool | Hàng roadmap tương ứng ở mục 5, `tools/README.md`, test cùng tên trong `tests/`, diff thật |
| Đóng gói / phát hành | `.github/RELEASING.md`, `tools/check_package.py`, `tools/build_release.py` |
| Thêm/nhập skill hoặc gói | `skills/README.md` (chuẩn tiếp nhận), `packs/README.md` |
| Cần điều kiện đạt mốc | `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` mục 3–4 và `roadmap/ROADMAP_HOAN_THIEN.md` mục 8.3–8.4 |

## 5. Tiến độ theo dòng roadmap

Dòng và thứ tự lấy từ mục 4 của `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` (revision `LOCAL-ROADMAP-20261104-r1`). Điều kiện đóng, phần còn lại sau mỗi dòng và bằng chứng chi tiết nằm ở roadmap/HANDOFF, không chép lại ở đây. Nhãn trạng thái giữ đúng nghĩa của roadmap: PLANNED, BLOCKED_*, DEFERRED_*, NOT_RUN.

| Dòng | Nội dung | Trạng thái | Ghi chú ngắn / con trỏ bằng chứng |
|---|---|---|---|
| 4.1 | V1/V2/V4: chất lượng luồng báo cáo–số liệu–nháp thư | PLANNED, ưu tiên đầu | Bước đầu: đối chiếu nguồn/output ca V2/V4 sẵn có, khóa gap và expected |
| 4.2 | V2/V5/V6: sửa, tiếp phiên, UX trạng thái | PLANNED; phần gọi vai BLOCKED_AUTHORITY | Profile hiện `NO_GRANT` cho Scout/Worker/Reviewer; phần đọc/nháp độc lập không bị chặn |
| 4.3 | V3/V7/P1: nguồn đúng phạm vi, bảo toàn dữ liệu | PLANNED | P2 INACTIVE; D1–D5 DEFERRED_USER |
| 4.4 | V4/V7: nội dung và định dạng Word/XLSX/HTML | PLANNED | Excel173 cause UNKNOWN, native QA chưa đạt; chart chỉ theo receipt |
| 4.5 | V7/M4/M6: đóng gói, gate, vòng đời, phát hành | PLANNED; nhánh artifact54 BLOCKED_CAUSE | Chưa có ZIP mới đạt gate; ZIP50 (rc5) chỉ là subset lịch sử; phát hành mới cần quyền riêng |
| 4.6 | V6/R6/M5: dùng lại và phản hồi người dùng | DEFERRED_POST_MVP; feedback NOT_RUN | Kit C-02 giữ chuẩn bị |
| §5 | Nghiên cứu, upstream, gói hoãn | DEFER / PAUSED | Năm gói lĩnh vực DEFER; academic PAUSED/REVIEW |

## 6. Nhật ký tranche (mới nhất ở trên)

Một dòng cho mỗi tranche đã đóng hoặc mốc kế hoạch đã chốt. Ghi: ngày, tên tranche/dòng roadmap, phần đã đóng, phần còn lại, bằng chứng, review (có/chưa/không áp dụng).

| Ngày | Tranche / dòng | Đã đóng | Còn lại | Bằng chứng | Review |
|---|---|---|---|---|---|
| 04/11/2026 | Lập kế hoạch Local, `LOCAL-ROADMAP-20261104-r1` (chưa thi công dòng sản phẩm) | Quyết định dùng nền hiện hữu; thứ tự 4.1→4.6; đối chiếu toàn bảng điều kiện | Toàn bộ 4.1–4.6 | `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` mục Local 04/11; đầu `.agent/HANDOFF.md` | Không áp dụng (kế hoạch) |
| 04/11/2026 | Tạo catalog này | File catalog và link từ README | Cập nhật ở mỗi tranche | `roadmap/CATALOG_CAU_TRUC_VA_TIEN_DO.md` | Chưa |
