# Catalog cấu trúc project và tiến độ

Một bản đồ dùng chung để mọi agent (Claude, Codex, Gemini) và operator đọc cấu trúc kho nguồn LAW giống nhau, kèm tiến độ theo tranche.
File này chỉ có ở kho nguồn (nằm trong `roadmap/`, không thuộc bản phân phối) và được đăng trên GitHub chủ yếu để agent bên ngoài đọc.
Nó là bản tra nhanh, không phải nguồn sự thật: khi lệch với file thực, STATE, HANDOFF hoặc roadmap thì file thực thắng; nêu chỗ lệch cho operator thay vì tự sửa.

**Cập nhật tiến độ:** 06/11/2026 · Local roadmap `LOCAL-ROADMAP-20261106-r7` chốt baseline/kết quả và chức năng LAW theo operator; tích hợp form kiểm soát tiến độ chung, bản sửa F1/N1–N5 sau review Claude trong r6.22, Main kiểm hẹp; verdict cũ giữ trên bytes r7/form1.0; không nhận mốc sản phẩm từ sửa roadmap. Mốc `main` tại `32604fb` và snapshot r2 là nền lịch sử; đối chiếu `.agent/STATE.md` và HANDOFF khi cần trạng thái mới nhất.

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

Dòng lấy từ mục 4 của `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` (revision hiện hành `LOCAL-ROADMAP-20261106-r7`; r3–r6 giữ lịch sử). Ưu tiên là luồng Main nhận–giao–nghiệm thu–trả kết quả ở 4.1, sửa/tiếp ở 4.2, với chuẩn nguồn/đầu ra xuyên suốt 4.3–4.4; 4.0/4.5 lo bản đóng gói. Năm kết quả và hành vi LAW ở roadmap §1.2–1.3; form CVF chung `CVF_ROADMAP_PROGRESS_FORM.md` v1.2 hiệu chỉnh1 đã tiếp nhận, phần áp dụng riêng LAW ở roadmap §6; giữ một bảng coverage chính, không biến bảng hướng dẫn thành trạng thái thứ hai. Điều kiện đóng và phần còn lại nằm ở roadmap/HANDOFF. Nhãn PLANNED/BLOCKED/DEFER/NOT_RUN không thay bằng số test code đã đạt.

| Dòng | Nội dung | Trạng thái | Ghi chú ngắn / con trỏ bằng chứng |
|---|---|---|---|
| 4.0 | V7/M4: khôi phục kiểm source sạch | W40/candidate đã nhận có giới hạn; CHƯA ĐÓNG | Candidate clean package đã kiểm, staged bỏ dòng PACK trỏ file Local; live registry và gói riêng giữ. Source/CI/gate hiện hành và toàn V7 chưa được nhận; xem STATE/HANDOFF W40 |
| 4.1 | V1/V2/V4: chất lượng luồng báo cáo–số liệu–nháp thư | Ba fixture PRE review; DATA_NOT_MET, report/thư chưa dispatch | OFFICE41-r1/r1a: actor native lỗi stdout rồi ghi evidence thiếu parent sau một sửa; không output được nhận, giữ failure/audit ở working/office-flow-quality-20261106/ và HANDOFF. Không suy product grant/adapter hoặc toàn luồng đạt |
| 4.2 | V2/V5/V6: sửa, tiếp phiên, UX trạng thái | PLANNED; phần gọi vai BLOCKED_AUTHORITY | R6.20 phân biệt claim đổi trong TASK binding trên fixture, chưa kiểm luồng sửa/tiếp thật. Profile hiện `NO_GRANT` cho Scout/Worker/Reviewer; phần đọc/nháp độc lập không bị chặn |
| 4.3 | V3/V7/P1: nguồn đúng phạm vi, bảo toàn dữ liệu | PLANNED | P2 INACTIVE; D1–D5 DEFERRED_USER |
| 4.4 | V4/V7: LAW kiểm soát đầu ra theo host và claim | ĐANG LÀM, CHƯA ĐẠT | R6.19 cho thư ký chuẩn bị brief DOCX qua host_session có capability khai báo, chưa chứng minh host/quyền/artifact. Còn proof actor/capability/quyền, nguồn/revision, QA artifact và skip/unsupported trên luồng thật. Word A và Excel173 là ca có giới hạn; nếu giao Excel173 thì rubric tính/lưu/in riêng vẫn thiếu. Harness/COM cũ không là gate chung |
| 4.5 | V7/M4/M6: đóng gói, gate, vòng đời, phát hành | PLANNED; nhánh artifact54 BLOCKED_CAUSE | Chưa có ZIP mới đạt gate; ZIP50 (rc5) chỉ là subset lịch sử; phát hành mới cần quyền riêng |
| 4.6 | V6/R6/M5: dùng lại và phản hồi người dùng | DEFERRED_POST_MVP; feedback NOT_RUN | Kit C-02 giữ chuẩn bị |
| §5 | Nghiên cứu, upstream, gói hoãn | DEFER / PAUSED | Năm gói lĩnh vực DEFER; academic PAUSED/REVIEW |

## 6. Nhật ký tranche (mới nhất ở trên)

Một dòng cho mỗi tranche đã đóng hoặc mốc kế hoạch đã chốt. Ghi: ngày, tên tranche/dòng roadmap, phần đã đóng, phần còn lại, bằng chứng, review (có/chưa/không áp dụng).

| Ngày | Tranche / dòng | Đã đóng | Còn lại | Bằng chứng | Review |
|---|---|---|---|---|---|
| 06/11/2026 | R6.22 / roadmap r7 và form1.1 | Chốt baseline; sau review Claude đã sửa F1/N1–N5, nối expected vào 4.1/4.2 | Toàn gap sản phẩm giữ; form CVF NOT_UPSTREAMED, hiệu quả chưa kiểm | HANDOFF r6.22; review Claude r7; roadmap §4.1/4.2; form1.1 | Astra/Claude review bản trước sửa; Main kiểm sửa nhỏ cùng lượt |
| 04/11/2026 | Review độc lập roadmap r2 (Claude, operator giao trực tiếp) | Verdict `REVIEW_PASSED`, chốt kế hoạch; không đóng mốc sản phẩm | Diff 4.0 và ca 4.1 chưa có, review riêng khi operator giao; lưu ý N1–N3 | `roadmap/REVIEW_DOC_LAP_CLAUDE_ROADMAP_LOCAL_R2_2026-11-04.md` | Có (độc lập, chỉ tài liệu) |
| 04/11/2026 | Local nhận phản biện F1–F9, nâng lên `LOCAL-ROADMAP-20261104-r2` | Thêm 4.0, đường ca và thước đo 4.1, trần từng gói (§6), bảng quyết định (§7) | Toàn 4.0–4.6 | `roadmap/DANH_GIA_CLAUDE_ROADMAP_LOCAL_2026-11-04.md`, `roadmap/XAC_NHAN_CLAUDE_ROADMAP_LOCAL_R2_2026-11-04.md` | Không áp dụng (kế hoạch) |
| 04/11/2026 | Lập kế hoạch Local, `LOCAL-ROADMAP-20261104-r1` (chưa thi công dòng sản phẩm) | Quyết định dùng nền hiện hữu; thứ tự 4.1→4.6; đối chiếu toàn bảng điều kiện | Toàn bộ 4.1–4.6 | `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` mục Local 04/11; đầu `.agent/HANDOFF.md` | Không áp dụng (kế hoạch) |
| 04/11/2026 | Tạo catalog này | File catalog và link từ README | Cập nhật ở mỗi tranche | `roadmap/CATALOG_CAU_TRUC_VA_TIEN_DO.md` | Chưa |
