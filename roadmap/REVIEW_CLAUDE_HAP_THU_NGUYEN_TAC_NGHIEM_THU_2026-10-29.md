# Review của Claude — Codex hấp thu nguyên tắc "dev tự nghiệm thu sản phẩm" vào LAW, WORKSPACE_RULES và bản CVF trong workspace

**Ngày:** 29/10/2026 (bắt đầu tối 28/10). **Reviewer:** Claude (Opus 5.5), theo yêu cầu operator "Đánh giá xem thế nào". Review chỉ đọc; chỉ thêm file này.
**Phạm vi:** (1) LAW: `AGENTS.md`, `en/AGENTS.md`, `skills/README.md`, `en/skills/README.md`, `packs/README.md`, `packs/_template/references/intake-record.md` (mới),
`PROJECT.md`; (2) `CVF-Workspace/WORKSPACE_RULES.md`; (3) `CVF-Workspace/.Controlled-Vibe-Framework-CVF`: contract mốc, learning philosophy, `AGENTS.md`,
`CVF_PUBLIC_CORE_AGENTS.md`, `CVF_DOWNSTREAM_AGENTS_TEMPLATE.md`, `CVF_WORKSPACE_RULES.md`, `new-cvf-workspace.ps1`, `install_cvf_workspace_root_wrappers.ps1`.
**Căn cứ so:** nguyên tắc operator (hội thoại 28/10), [Y_KIEN_CLAUDE_NGUYEN_TAC_NGHIEM_THU_CHUNG_2026-10-28.md](Y_KIEN_CLAUDE_NGUYEN_TAC_NGHIEM_THU_CHUNG_2026-10-28.md),
[LEARNING_CVF_DOI_DEV_TU_NGHIEM_THU_SAN_PHAM_2026-10-28.md](LEARNING_CVF_DOI_DEV_TU_NGHIEM_THU_SAN_PHAM_2026-10-28.md).

## 1. Kết luận

**Nội dung tốt, nhưng bản hiện tại chưa giao được:** full suite LAW có **8 lỗi mới** do chính lượt này (C0), và chính nguyên tắc vừa ghi đòi đội dev tự
kiểm trước khi báo xong. Ngoài ra có 4 điểm nội dung cần chỉnh (C2–C5) và 1 rủi ro cấu trúc ở bản CVF trong workspace (C1).

Phần nội dung bám đúng nguyên tắc operator và hấp thu đủ các ý của Claude: ba lớp (kiểm kỹ thuật → dev nghiệm thu sản phẩm → feedback nghiệp vụ),
năm câu hỏi, bằng chứng theo rủi ro, một câu tuyên bố giá trị, ngày đối chiếu nguồn, ma trận hỗ trợ ghi `NOT_TESTED`, luồng tạo mới và nâng cấp,
tách chất lượng khỏi `confirm`. Khung `intake-record.md` gọn, ánh xạ năm câu vào sáu điều kiện, ghi rõ "mẫu chưa điền không phải verdict", và đi theo
`pack.py new` (hàm tạo gói chép toàn bộ `packs/_template`, `tools/pack.py:667-673`). Văn bản tiếng Anh ở contract chặt hơn bản Claude đề xuất ở
nhiều chỗ (không dùng AI tự đồng ý làm oracle, tách regression khỏi ca đánh giá việc mới).

## 2. Kiểm đã chạy

| Phép kiểm | Kết quả |
|---|---|
| `check_package.run_checks(release=False)` (LAW) | 0 lỗi, 14 cảnh báo (14 README chưa nhắc tên skill, có từ trước). Cảnh báo CRLF/`.pytest_cache` lần trước đã hết |
| `build_guides_html.py --check` | 10 trang khớp |
| `check_package.py --check-eol` 6 file LAW đã đổi | 0 lỗi |
| Khối chèn ở CVF clone | `AGENTS.md`, `CVF_PUBLIC_CORE_AGENTS.md`, `CVF_DOWNSTREAM_AGENTS_TEMPLATE.md`: cùng 20 dòng, giống hệt; hai `.ps1`: cùng 26 dòng, giống hệt |
| **Full suite LAW** `python -X utf8 -B -m unittest discover -s tests` | **Ran 1688 tests in 1184.310s — FAILED (failures=6, errors=3, skipped=8)** |

## 3. Finding

### C0 — Full suite: 8 lỗi mới cùng một gốc, do `PROJECT.md` thêm 3 mục `##` (cao; đã xác nhận)

| Lỗi | Test |
|---|---|
| 3 error `setUpClass` | `test_package_v3.Archive`, `.Journey`, `.Lifecycle` (mỗi class chứa nhiều test, nên số test thực sự không chạy lớn hơn 3) |
| 4 fail | `test_release_gate`: `test_behaviour_report_keeps_skipped_test_names_and_reasons`, `test_branding_ships_in_zip_and_can_be_left_out`, `test_gate_report_platform_python_hash_and_reproducible_zip`, `test_other_user_files_in_assets_still_block_release` |
| 1 fail | `test_workflows.Workflows.test_release_uses_clean_templates_without_changing_worktree` |
| 1 fail (cũ) | B7 `test_execution_profile...without_a_source_profile` |

Cả 8 lỗi mới có cùng thông báo (đếm 8/8 trong log): `LỖI: Song ngữ: PROJECT.md có 10 mục "##", en/PROJECT.md có 7.` → `Không đóng gói: cổng bắt buộc
chưa đạt (package_check). Không tạo ZIP.`

Nguyên nhân: `PROJECT.md` (sửa 28/10 23:55, `+16 -1`) thêm ba heading mới để ghi quyền/phạm vi: `## Bổ sung quyền workspace — chỉ định tiếp theo 28/10/2026`,
`## Điều chỉnh phạm vi rev158 28/10/2026`, `## Quyết định phát triển 28/10/2026`. Kiểm song ngữ (`check_package.py:48` cặp `PROJECT.md`/`en/PROJECT.md`)
chạy trên cây dựng bản giao nên chặn đóng gói; `release_templates/PROJECT.md` và bản `en` vẫn 7 mục. Nghĩa là **bộ mẫu hiện tại không đóng gói được**.

**Sửa:** chuyển ba nội dung đó thành gạch đầu dòng trong mục có sẵn (ví dụ mục đang chứa các "Chỉ định operator"), giữ 7 mục `##`; chạy lại full suite.
Không sửa test hay nới kiểm song ngữ. Số skip tăng 6 → 8: chưa kiểm hai ca skip mới, cần Codex ghi rõ.

### C1 — Sửa ở bản CVF trong workspace là sửa ở mắt xích cuối của chuỗi đồng bộ (trung bình–cao; đã xác nhận)

Đã kiểm:
- `.Controlled-Vibe-Framework-CVF` là bản clone của `https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`; commit cuối
  `aa672d1 sync: public surface update from governance@52c11fa22`; đang `behind 2` so với `origin/main` (hai commit sync 26/10 không đụng các file vừa sửa).
- Chiều đồng bộ: kho governance `D:\...\Controlled-Vibe-Framework-CVF` → `scripts/cvf-public-sync.ps1` (`Copy-Item -Force`, dòng 478, 505) →
  `Controlled-Vibe-Framework-CVF-public-sync` → GitHub → bản clone trong workspace. `AGENTS.md` công khai được sinh từ
  `governance/toolkit/05_OPERATION/CVF_PUBLIC_CORE_AGENTS.md` (`cvf-public-sync.ps1:184-185`).
- Kho governance **chưa có** quy tắc này (`grep -c "Development-Owned Internal Readiness"` contract = 0).

Hệ quả:
1. Lần đồng bộ sau mà governance đổi các file này sẽ ghi đè hoặc xung đột với bản sửa; quy tắc có thể mất mà không ai biết.
2. Bản clone có quyền push lên kho công khai và đang có thay đổi chưa commit lẫn với WIP khác (ví dụ `EXTENSIONS/CVF_MODEL_GATEWAY/...`,
   `CVF_ALIBABA_FREE_QUOTA_MODEL_LEDGER.*`): dễ commit/push nhầm.
3. `AGENTS.md` và `CVF_PUBLIC_CORE_AGENTS.md` trong clone cùng được sửa, trong khi file thứ nhất là sản phẩm sinh từ file thứ hai ở governance.
4. `WORKSPACE_RULES.md` ở gốc `CVF-Workspace` không có Git, không thấy bản sao trước khi sửa; file này được `install_cvf_workspace_root_wrappers.ps1`
   sinh lại và có hiệu lực ngay với mọi project trong `CVF-Workspace`.

`PROJECT.md` ghi operator đã cho phép lượt sửa này (mục "Bổ sung quyền workspace"), và mục rev158 ghi lượt sau chỉ sửa LAW. Claude không cho đây là
sửa trái quyền. Điểm cần xử lý là **giữ được** thay đổi tới khi tranche CVF gốc làm.

**Đề xuất:** (a) lưu ngay `git diff` của đúng 8 file quy tắc trong clone thành một patch có hash (không gồm file model gateway), ghi vào HANDOFF làm
đầu vào cho tranche CVF gốc; (b) lưu bản `WORKSPACE_RULES.md` hiện tại và ghi rõ đây là bản sinh từ script đã sửa; (c) không commit/push trong clone; (d) ở
tranche CVF gốc, áp vào file nguồn ở governance (`docs/reference/...CONTRACT...`, `governance/toolkit/05_OPERATION/CVF_PUBLIC_CORE_AGENTS.md`,
`CVF_DOWNSTREAM_AGENTS_TEMPLATE.md`, `CVF_WORKSPACE_RULES.md`, script sinh hướng dẫn) rồi đồng bộ xuôi; sau đó bỏ bản sửa tay ở clone.

### C2 — "experimental" trong contract mâu thuẫn với lựa chọn operator đã cho (trung bình)

Contract (clone) viết: "Do not mark an approved criterion optional, N/A, **experimental** or accepted merely to ship". Nguyên tắc operator cho phép
rõ: "Package chưa đạt thì sửa, thu hẹp phạm vi **hoặc để riêng trong nhóm thử nghiệm**". Câu contract có thể hiểu là cấm cả việc giao một gói dưới
nhãn thử nghiệm. **Sửa:** tách hai ý: được giao thành phần chưa đạt dưới nhãn thử nghiệm ghi rõ phần chưa đạt, không giới thiệu là sẵn dùng; cấm đổi
nhãn tiêu chí (optional/N/A) để tuyên bố đã đạt. LAW (`skills/README.md`, `packs/README.md`) đang viết đúng ý ("thành phần chưa đủ giữ candidate"),
nên chỉ contract cần sửa.

### C3 — "Đội dev tổ chức thẩm định chuyên môn" cần ranh giới thực tế (trung bình)

LAW `AGENTS.md` ("không bị yêu cầu... tìm người kiểm thay đội dev"), `skills/README.md` ("Không chờ end user... tìm chuyên gia"; "đội dev tổ chức việc đó")
và contract ("do not make recruitment by the non-coder a development gate"). Agent không tự mời hay trả phí cho luật sư/chuyên gia được; operator cũng đã
nói sẽ tìm luật sư thử (`working/legal-quality-20261028/CA_PHAP_LY_CHUAN_BI.md`). Nếu giữ câu chữ hiện tại, agent dễ rơi vào một trong hai: chặn mãi, hoặc
tự chấm thay chuyên gia. **Sửa:** đội dev chuẩn bị đủ để chuyên gia chỉ việc thẩm định (ca, nguồn, rubric, câu hỏi, chỗ cần phán đoán); việc **mời ai, chi
phí** là quyết định nghiệp vụ hỏi operator một lần bằng lời thường; khi chưa có, claim bị chặn và gói giữ nhãn thử nghiệm (đã có ở contract).

### C4 — `packs/README.md` bỏ mất giới hạn dùng cho người dùng trong khi gói còn lỗi đã biết (trung bình; thận trọng cao)

Bản cũ: "Dùng để tham khảo và soạn nháp; với văn bản trình ký hoặc gửi ra ngoài, tự đối chiếu căn cứ…". Bản mới: "agent phải đối chiếu đúng nguồn và nêu
giới hạn; người có thẩm quyền quyết định việc ký/gửi, không bị giao nhiệm vụ QA sản phẩm." Bản mới đúng về trách nhiệm, nhưng các gói **vẫn** là thử nghiệm
và **đã ghi nhận** câu "trích nguyên văn" không có trong nguồn. Không bắt người dùng làm QA không có nghĩa là bỏ thông báo giới hạn của sản phẩm.
**Sửa:** giữ câu trách nhiệm mới, thêm lại giới hạn dùng dưới dạng đặc tính sản phẩm: "Khi chưa qua nghiệm thu, gói chỉ dùng để tham khảo và soạn nháp;
không dùng căn cứ trong gói cho văn bản trình ký hoặc gửi ra ngoài." Bản `en` tương ứng.

### C5 — Hạn kiểm lại quá ngày: cần nói agent làm gì (thấp)

Cả ba nơi ghi "hạn kiểm lại là trigger xem xét, không tự đổi status". Hợp lý, nhưng chưa nói khi quá hạn mà chưa ai xem xét thì agent dùng nguồn đó thế nào.
**Sửa:** thêm một câu: khi dùng nguồn đã quá hạn kiểm lại, agent nêu rõ "chưa kiểm lại từ <ngày>" ngay trong đầu ra; với nhóm thận trọng cao, không trình
bày như căn cứ hiện hành.

### C6 — Cùng một quy tắc được chép khoảng 11 nơi (thấp; rủi ro trôi về sau)

Contract, learning philosophy, 3 file AGENTS ở clone, `CVF_WORKSPACE_RULES.md`, 2 `.ps1`, `WORKSPACE_RULES.md`, LAW `AGENTS.md` vi/en, `skills/README.md`
vi/en, `packs/README.md`, mẫu intake. Khối 20 dòng trong mỗi `AGENTS.md` là dài so với vai trò file điểm vào. Chính phản biện của Codex đã đề xuất "gộp
hướng dẫn lặp về canonical owner". **Đề xuất (không gấp, làm cùng tranche CVF gốc):** contract là nguồn duy nhất đầy đủ; các `AGENTS.md`/rules giữ 3–5
dòng trỏ về contract; LAW giữ bản đầy đủ ở `skills/README.md` và mẫu intake, `AGENTS.md` chỉ trỏ.

## 4. Thứ tự đề xuất

1. C0 (chặn đóng gói) → full suite lại.
2. C1 (a)–(c): lưu patch và bản `WORKSPACE_RULES.md`, ghi HANDOFF; không push.
3. C4, C2, C3, C5: sửa câu chữ; C2 chỉ ở clone/contract, phần còn lại ở LAW và cùng lúc ở clone để không lệch, hoặc để tranche CVF gốc.
4. C6 cùng tranche CVF gốc.

## 5. Chưa kiểm

Chưa đọc đủ diff của `CVF_AGENT_ERROR_TO_GOVERNANCE_LEARNING_PHILOSOPHY_2026-05-28.md` và `CVF_WORKSPACE_RULES.md` trong clone (chỉ so khối chèn);
chưa chạy `new-cvf-workspace.ps1`/`install_cvf_workspace_root_wrappers.ps1` để xem `WORKSPACE_RULES.md` sinh ra có khớp file hiện tại; chưa chạy test của CVF;
chưa xem hai ca skip mới; chưa đọc `en/skills/README.md` đủ để so nghĩa với bản vi (chỉ đếm dòng). `check_package` lần này chạy trước khi full suite báo lỗi,
ở chế độ `release=False`, nên không bắt lỗi song ngữ trên cây bản giao.
