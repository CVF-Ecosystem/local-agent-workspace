# Learning đề xuất cho CVF gốc — đội agent phát triển tự nghiệm thu sản phẩm dùng được trước khi giao noncoder

**Ngày:** 28/10/2026. **Nguồn:** project LAW (`local-agent-workspace`), operator chỉ định trong hội thoại 28/10/2026.
**Người lập:** Claude (Opus 5.5). **Đích:** CVF gốc `D:\UNG DUNG AI\TOOL AI 2026\Controlled-Vibe-Framework-CVF`, sau đó các workspace thừa hưởng (LAW và project sau).
**Trạng thái:** **ĐỀ XUẤT — chưa nộp vào CVF.** Claude không ghi vào kho CVF (ngoài phạm vi phiên, và LAW cấm sửa CVF cha khi chưa được giao).
Operator chuyển file này cho agent bảo trì CVF; CVF tự xét theo `CVF_FINDING_TO_GOVERNANCE_LEARNING_TRIGGER_STANDARD.md`.

## 1. Chỉ định của operator (nguyên ý)

CVF có trách nhiệm kiểm soát agent **thay cho noncoder**, từ dựng roadmap đến luồng và cách kiểm tra sản phẩm. Không thể cứ yêu cầu noncoder trả
lời hoặc test theo kiểu kỹ thuật. Phải có sản phẩm cho họ dùng thì mới có feedback. Đội agent phát triển phải có trách nhiệm làm ra sản phẩm, test
và nghiệm thu dùng được theo chuẩn. Áp cho CVF gốc trước, rồi workspace thừa hưởng, cho mọi project phát triển về sau.

Nguyên tắc chi tiết operator đã nêu cho LAW (bảng ba thành phần core/package/bản phân phối, năm câu hỏi hồ sơ nghiệm thu) và góp ý của Claude:
[Y_KIEN_CLAUDE_NGUYEN_TAC_NGHIEM_THU_CHUNG_2026-10-28.md](Y_KIEN_CLAUDE_NGUYEN_TAC_NGHIEM_THU_CHUNG_2026-10-28.md).

## 2. Chỗ hở trong CVF hiện hành

`docs/reference/CVF_PRODUCT_MILESTONE_COVERAGE_CONTRACT_2026-10-23.md` (ACTIVE_STANDARD) là nguồn của quy tắc 10 trong LAW. Hợp đồng phân hai lớp:

- kiểm kỹ thuật: "a technical check does not supply human/business acceptance";
- nghiệm thu nghiệp vụ: "Business acceptance remains with the operator or the explicitly authorized acceptance role"; "the operator owns product
  scope, business acceptance and changes to authority".

Không có lớp **nghiệm thu sản phẩm do đội phát triển chịu trách nhiệm** nằm giữa hai lớp đó: chứng minh sản phẩm làm được việc đã hứa, đầu ra đạt
chuẩn, chạy được trên bản đóng gói, trước khi giao người dùng. Khi thiếu lớp này, mọi thứ vượt quá kiểm kỹ thuật đều rơi về "acceptance của operator",
tức noncoder phải tự làm nốt việc kiểm.

## 3. Bằng chứng từ LAW (28/10/2026)

| # | Hiện tượng | Locator |
|---|---|---|
| E1 | Chuẩn gói dùng chung yêu cầu "ít nhất ba việc thật" và "phản hồi người nhận"; gói học thuật ghi trial `HOLD_USER_TRIAL`, điều kiện hiệu quả chờ dùng thật: phép kiểm chất lượng bị đặt lên người dùng | `packs/README.md:41-46`; `packs/academic-research/references/intake-record.md` |
| E2 | Năm gói đi kèm ghi "trial versions… legal basis compiled from news and advisory sites… not checked article by article", vẫn nằm trong bản giao | `packs/README.md:14` |
| E3 | Patch được ghi `PATCH PASS_WITH_LIMITS` dựa trên test chọn lọc; full suite thật có 58 lỗi (57 do chính patch) | [REVIEW_DOC_LAP_DONG_BO_AN_C2_CLAUDE_2026-10-28.md](REVIEW_DOC_LAP_DONG_BO_AN_C2_CLAUDE_2026-10-28.md) B1 |
| E4 | Skill bãi container mất phần kiến thức nghề khi chuyển gói; cấu trúc và review đều đạt, không phép kiểm nào đo đầu ra | cùng file, B3 |
| E5 | Project mới tạo từ bộ mẫu có dòng skill trỏ tới gói không có: lỗi chỉ lộ khi thử trên bản thật, không lộ ở kho nguồn | cùng file, B2 |
| E6 | Operator (noncoder) phải trực tiếp hỏi "test cái này đi, xem ổn chưa" và tự đặt câu hỏi về chất lượng project | hội thoại 28/10 |

Các tác nhân gồm cả Claude và Codex; đây là lỗi lặp lại của cách làm, không phải của một agent (đúng tiêu chí "repeated, future-agent, systemic" của
trigger standard).

## 4. Quy tắc đề xuất

### 4.1. Ba lớp nghiệm thu

| Lớp | Ai chịu trách nhiệm | Nội dung | Không thay được lớp khác |
|---|---|---|---|
| L-KT Kiểm kỹ thuật | Worker / Reviewer agent | Test, cấu trúc, bytes, quyền, gate | Đạt L-KT không phải sản phẩm dùng được |
| **L-SP Nghiệm thu sản phẩm (mới)** | **Đội agent phát triển** (orchestrator chịu trách nhiệm cuối) | Sản phẩm làm đúng việc đã hứa; đầu ra đạt chuẩn chất lượng đặt trước; xử lý thiếu dữ liệu, sửa bản, lỗi điển hình; kiểm một luồng trọn **trên bản đóng gói** ở môi trường công bố hỗ trợ; bằng chứng theo mức rủi ro | Không thay quyết định nghiệp vụ hay khẩu vị của người dùng |
| L-NV Nghiệm thu nghiệp vụ | Operator / người dùng | Có đúng nhu cầu, có hữu ích, có muốn dùng; quyết định phạm vi, quyền, cài đặt | Không dùng làm nơi phát hiện lỗi kỹ thuật hay lỗi chất lượng đã biết |

Thứ tự bắt buộc: L-KT → L-SP → giao sản phẩm → L-NV. Chưa đạt L-SP thì sửa, thu hẹp phạm vi, hoặc giao dưới nhãn **thử nghiệm** ghi rõ phần chưa đạt;
không gọi là sẵn dùng.

### 4.2. Hồ sơ L-SP (dùng chỗ đã có, không tạo sổ mới)

Năm câu: (1) giúp làm việc gì, đầu vào/đầu ra/giới hạn; (2) chất lượng tối thiểu, lỗi không được mắc, cách xử lý khi thiếu thông tin; (3) đã chứng minh
bằng gì: bộ ca đại diện do đội phát triển chuẩn bị, kết quả mong đợi có căn cứ, kiểm tự động phần đo được, review nội dung phần cần phán đoán; (4) có ích
hơn cách sẵn có ở đâu (chỉ chứng minh phần đã tuyên bố); (5) bản đóng gói dùng được thật không. Mức bằng chứng theo rủi ro; nội dung pháp lý, tài chính,
an toàn, học thuật cần người có chuyên môn duyệt kết quả mong đợi, và việc đó là một phần L-SP, không phải phản hồi người dùng.

### 4.3. Quy tắc giao tiếp với noncoder

- **Được hỏi:** phạm vi và mục tiêu sản phẩm, quyết định nghiệp vụ, dữ kiện chỉ họ biết, khẩu vị đầu ra, cấp/thu quyền, chỉ định người có chuyên môn.
- **Không được đẩy sang họ:** chạy lệnh, đọc log test, chọn phương pháp kỹ thuật, làm người thử đầu tiên, phát hiện lỗi mà đội phát triển kiểm được.
- Câu hỏi kỹ thuật buộc phải hỏi thì viết bằng lời thường, nêu hậu quả của từng lựa chọn và **khuyến nghị** của đội phát triển.
- Báo trạng thái theo "người dùng làm được gì", không theo số tranche, test hay commit (đã có trong hợp đồng mốc; nhắc lại cho lớp L-SP).

### 4.4. Văn bản chuẩn đề xuất chèn vào hợp đồng mốc (tiếng Anh, để CVF owner chỉnh)

> **Developer product acceptance.** Between technical checks and business acceptance, the development agents own product acceptance: before an
> output, package or release is offered to a user as usable, the orchestrator records evidence that it performs the promised job, meets
> predefined quality criteria, handles missing data, revision and typical errors, and works end-to-end from the packaged artifact on the published
> support matrix. Evidence is proportional to risk; legal, financial, safety and academic content requires expected results approved by a
> qualified person. Business acceptance and user feedback follow delivery and must not be used to discover defects the developers could have
> found. Work that has not passed product acceptance is narrowed, fixed, or delivered only under an explicit experimental label. Questions to a
> noncoder operator are limited to scope, business decisions, domain facts, preferences and authority; technical choices are presented with
> consequences and a recommendation.

## 5. Thừa hưởng xuống workspace

| Nơi | Việc |
|---|---|
| CVF gốc | Cập nhật hợp đồng mốc (4.4); template roadmap/work order: thêm cột lớp L-SP vào bảng acceptance hiện có, không thêm ledger |
| Bộ overlay/bootstrap cho workspace (`workspace_overlay_catalog.json`, các standard downstream) | Mang quy tắc 4.1 và 4.3 xuống mọi workspace mới |
| LAW | Quy tắc 10 trong `AGENTS.md` (thừa hưởng hợp đồng mốc) thêm lớp L-SP; chuẩn tiếp nhận `skills/README.md`, `packs/README.md`, khung `packs/_template/references/intake-record.md` dùng năm câu; Codex đang đồng bộ theo chỉ định operator |
| Project sau | Nhận qua overlay; roadmap đầu tiên phải có tiêu chí L-SP cho từng mốc người dùng |

## 6. Finding-To-Governance Learning Disposition

| Finding | Defect class (đề xuất) | Learning lane | Disposition | Next control action | Batch |
|---|---|---|---|---|---|
| Thiếu lớp nghiệm thu sản phẩm do đội phát triển chịu trách nhiệm; chất lượng dồn sang noncoder (E1, E2, E6) | Phase-gate placement / acceptance-role gap | Standard | `STANDARD_UPDATED` (hợp đồng mốc) + `TEMPLATE_UPDATED` (bảng acceptance) | CVF owner xét admission: source confidence, dedup, giá trị tăng thêm | Deferred tới CVF |
| Ghi PASS dựa trên test chọn lọc khi thay đổi chạm owner/pin (E3) | Verification scope gap | Rule + machine check | `RULE_EXISTS` nếu CVF đã có quy tắc full suite cho owner change; nếu không: `MACHINE_CHECK_CANDIDATE` | Đối chiếu Review Cost standard, MFRP | Deferred tới CVF |
| Không có phép kiểm đầu ra nội dung; lỗi nội dung lọt qua kiểm cấu trúc (E4) | Content-quality evidence gap | Standard | Gộp vào hàng 1 (L-SP câu 2–3) | — | Deferred tới CVF |
| Lỗi chỉ lộ trên bản đóng gói (E5) | Packaged-artifact verification gap | Template / machine check | `MACHINE_CHECK_CANDIDATE`: luồng trọn trên artifact là điều kiện L-SP câu 5 | CVF xét chung với release gates hiện có | Deferred tới CVF |

## 7. Ranh giới

- Không chuyển quyền: cài đặt, ghi dữ liệu, xuất sang ứng dụng vẫn là quyết định của người dùng; L-SP không cấp quyền nào.
- Không đòi benchmark lớn hay cuộc thi model cho mọi skill; mức bằng chứng theo rủi ro.
- Không thêm lifecycle phase, ledger song song hay quy trình phê duyệt cho từng phép kiểm; dùng mốc và bảng acceptance đã có.
- **Cần CVF tự dedup:** CVF có thể đã có nội dung gần (ví dụ `docs/reference/CVF_CI2_T4_PRODUCT_READINESS_PILOT_CORPUS_PACK_2026-06-02.md`,
  `CVF_MSEA_R35_T2_CVF_CURRENT_PRODUCT_CAPABILITY_SNAPSHOT_2026-07-05.md`, các mục "noncoder interaction gaps" trong hợp đồng mốc). Claude chỉ đọc
  đoạn đầu hợp đồng mốc và phần Protocol của trigger standard; chưa đọc các file này, chưa kiểm `docs/reviews/learnings/` của CVF.

## 9. Cập nhật 29/10/2026 — đầu vào cho tranche nâng nền CVF gốc

Operator mở tranche riêng cho CVF gốc. Mục này thay mục 4.4 và mục 5 ở chỗ chúng khác nhau; mục 1–3, 4.1–4.3, 6–7 vẫn dùng.

### 9.1. Dùng bản nháp đã có, không viết lại từ mục 4.4

Codex đã soạn câu chữ trong bản clone công khai `CVF-Workspace\.Controlled-Vibe-Framework-CVF` (operator cho phép, ghi ở LAW `PROJECT.md`), đã sửa
theo review C2–C5 và được review độc lập. Bản này chặt hơn mục 4.4 (oracle không dựa vào AI tự đồng ý, tách regression khỏi ca đánh giá việc mới,
giao thử nghiệm kèm giới hạn, hỏi một lần về người duyệt/ngân sách, nguồn quá hạn ghi "not rechecked since"). **Tranche lấy bản này làm nguồn.**

- Patch: `local-agent-workspace\working\acceptance-repair-20261029\cvf-workspace-rules-20261029.patch`, SHA-256
  `511b96da4c994c5b59f203e13614d5d1c6bf24775b2a58052be63c8d0b71beee`, đúng 8 file; `git apply --check -R` sạch trên clone lúc 29/10.
- Bản chụp `WORKSPACE_RULES.md` gốc workspace: `...\WORKSPACE_RULES_20261029.md`, SHA-256 `1424b6bae254a86b74f3dc55f7179f12198fe02c4ed3e2dea83e1a823ba8dd03`.
- Review và xác nhận: [REVIEW_CLAUDE_HAP_THU_NGUYEN_TAC_NGHIEM_THU_2026-10-29.md](REVIEW_CLAUDE_HAP_THU_NGUYEN_TAC_NGHIEM_THU_2026-10-29.md),
  [XAC_NHAN_CLAUDE_SUA_C0_C5_2026-10-29.md](XAC_NHAN_CLAUDE_SUA_C0_C5_2026-10-29.md).

### 9.2. Áp vào file nguồn ở governance, đúng ánh xạ của `scripts/cvf-public-sync.ps1`

Chuỗi đồng bộ: governance `D:\UNG DUNG AI\TOOL AI 2026\Controlled-Vibe-Framework-CVF` → `cvf-public-sync.ps1` (`Copy-Item -Force`) →
`Controlled-Vibe-Framework-CVF-public-sync` → GitHub `Blackbird081/Controlled-Vibe-Framework-CVF` → bản clone trong workspace.

| File trong patch (clone) | File nguồn phải sửa ở governance | Ghi chú |
|---|---|---|
| `docs/reference/CVF_PRODUCT_MILESTONE_COVERAGE_CONTRACT_2026-10-23.md` | cùng đường dẫn | Nguồn đầy đủ duy nhất (canonical) |
| `docs/reference/CVF_AGENT_ERROR_TO_GOVERNANCE_LEARNING_PHILOSOPHY_2026-05-28.md` | cùng đường dẫn | |
| `docs/reference/CVF_WORKSPACE_RULES.md` | cùng đường dẫn | Trong danh sách file đồng bộ |
| `AGENTS.md` | **`governance/toolkit/05_OPERATION/CVF_PUBLIC_CORE_AGENTS.md`** | `AGENTS.md` công khai sinh từ file này (`cvf-public-sync.ps1`, mục Source/Destination); không sửa trùng hai nơi |
| `governance/toolkit/05_OPERATION/CVF_PUBLIC_CORE_AGENTS.md` | như trên | Một nguồn |
| `governance/toolkit/05_OPERATION/CVF_DOWNSTREAM_AGENTS_TEMPLATE.md` | cùng đường dẫn | |
| `scripts/new-cvf-workspace.ps1` | cùng đường dẫn | Sinh hướng dẫn cho workspace mới |
| `scripts/install_cvf_workspace_root_wrappers.ps1` | **`scripts/install_cvf_workspace_root_wrappers_public.ps1`** | Bản công khai sinh từ file `_public`; xét thêm bản riêng `install_cvf_workspace_root_wrappers.ps1` của governance |

Ngoài patch, tranche cần xét thêm (chưa có trong bản clone):
- `AGENTS.md` **riêng của governance** (khác bản công khai): agent bảo trì CVF gốc cũng phải theo quy tắc này.
- `docs/reference/downstream_gate_profile/CVF_MILESTONE_COVERAGE_MACHINE_CONTRACT.md` (cũng đồng bộ ra công khai): nếu hợp đồng máy có trường
  acceptance, cần trường hoặc ghi chú cho lớp L-SP để validator không lệch với văn bản.
- Template work order/roadmap và `CVF_WORK_ORDER_ACCEPTANCE_LEDGER_ADDENDUM.md`: thêm lớp L-SP vào bảng acceptance có sẵn, không thêm ledger.

### 9.3. Gộp bản chép (C6) trong cùng tranche

Hiện cùng một quy tắc nằm khoảng 11 nơi. Đề xuất: contract giữ bản đầy đủ; `CVF_PUBLIC_CORE_AGENTS.md`, `AGENTS.md` riêng, `CVF_DOWNSTREAM_AGENTS_TEMPLATE.md`,
`CVF_WORKSPACE_RULES.md` và hai script chỉ giữ 3–5 dòng trỏ về mục "Development-Owned Internal Readiness Before User Feedback" của contract.
LAW đã có bản đầy đủ ở `skills/README.md` và mẫu intake; khi LAW nhận bản CVF mới, rút `AGENTS.md` của LAW về đoạn trỏ ngắn.

### 9.4. Bằng chứng bổ sung từ LAW (28–29/10)

| # | Hiện tượng | Learning | Locator |
|---|---|---|---|
| E7 | Ngay sau khi ghi quy tắc mới, Codex báo xong khi mới chạy test liên quan; full suite có 8 lỗi (ghi quyền thành mục `##` mới trong `PROJECT.md` làm hỏng kiểm song ngữ, chặn đóng gói) | Thay đổi chạm file được đóng gói phải chạy full suite trước khi báo xong; L-KT không phải tùy chọn của người làm | [REVIEW_CLAUDE_HAP_THU_NGUYEN_TAC_NGHIEM_THU_2026-10-29.md](REVIEW_CLAUDE_HAP_THU_NGUYEN_TAC_NGHIEM_THU_2026-10-29.md) C0 |
| E8 | Hai ca test mới bị skip vì máy không tạo được symlink; hành vi Windows thật (junction) chưa được test tới khi Claude thử tay | Báo kết quả phải nêu tên và lý do từng ca skip, không gộp vào "đạt"; khi môi trường thiếu quyền, dùng cơ chế tương đương có thật trên môi trường đó (junction) thay vì chỉ skip | [XAC_NHAN_CLAUDE_SUA_C0_C5_2026-10-29.md](XAC_NHAN_CLAUDE_SUA_C0_C5_2026-10-29.md), mục "Hai ca skip mới" |
| E9 | Roadmap chưa theo dõi bằng Git bị viết đè, mất bản gốc; phải dựng lại từ phiên đọc trước và chứng minh bằng hash | Trước khi thay một tài liệu điều phối chưa có trong Git, lưu bản cũ vào `archive/` kèm hash | [QUYET_DINH_OPERATOR_B1_B4_2026-10-28.md](QUYET_DINH_OPERATOR_B1_B4_2026-10-28.md) |
| E10 | Sửa quy tắc ở bản clone công khai (mắt xích cuối) trước nguồn governance | Quy tắc CVF chỉ sửa ở nguồn governance rồi đồng bộ xuôi; sửa tạm ở bản sinh ra phải lưu patch và ghi "chưa upstream" | mục 9.2 |

Bổ sung vào bảng mục 6: E7 → `RULE_EXISTS` nếu CVF đã buộc full suite cho thay đổi chạm artifact đóng gói, nếu không `MACHINE_CHECK_CANDIDATE`;
E8 → `TEMPLATE_UPDATED` (mẫu báo cáo test có danh sách skip và lý do), có thể CVF đã có (LAW có `test_release_gate...keeps_skipped_test_names_and_reasons`);
E9, E10 → `RULE_ADDED` nếu chưa có, cần CVF dedup.

### 9.5. Tranche này cũng phải tự qua L-SP

Quy tắc nói về nghiệm thu sản phẩm, nên tranche áp nó phải tự chứng minh bằng luồng thật, không chỉ sửa văn bản:
1. Sau khi sửa governance và đồng bộ, chạy `new-cvf-workspace.ps1` vào thư mục tạm: workspace mới phải có quy tắc ở đúng file sinh ra.
2. Chạy script cài wrapper vào thư mục tạm; so `WORKSPACE_RULES.md` sinh ra với bản chụp `1424b6ba…dd03` (khác ở đâu thì giải thích).
3. Chạy các test/validator CVF liên quan contract và machine contract; full suite theo quy định của CVF cho thay đổi chạm public surface.
4. Sau khi bản clone nhận bản mới từ GitHub, bỏ bản sửa tay: `git apply -R` đúng patch, rồi pull; kiểm clone không còn khác `origin/main` ở 8 file.
5. LAW nhận lại bản CVF mới ở lượt riêng (C6 cho LAW), chạy lại full suite LAW.

### 9.6. Điều phối

- Governance đang có việc khác (commit `618caaba2`, 29/10 00:42, "operator hold" M6). Trước khi sửa, đọc handoff/brief hiện hành của governance;
  không chen vào file đang có owner.
- Không commit/push từ bản clone; bản clone còn WIP khác (`EXTENSIONS/CVF_MODEL_GATEWAY/...`) không thuộc tranche này.
- Dedup trước khi viết (mục 7): `CVF_CI2_T4_PRODUCT_READINESS_PILOT_CORPUS_PACK_2026-06-02.md`, `CVF_MSEA_R35_T2_CVF_CURRENT_PRODUCT_CAPABILITY_SNAPSHOT_2026-07-05.md`,
  mục "noncoder interaction gaps" của contract, `docs/reviews/learnings/`.

## 8. Phần chưa kiểm

Đã đọc chỉ đọc: `AGENTS.md` CVF dòng 85–125; hợp đồng mốc dòng 1–45 và các dòng có từ user/operator/acceptance/noncoder; trigger standard dòng 48–80.
Chưa đọc đủ hai standard đó, chưa đọc `CVF_PROJECT_LEARNING_LOOP_STANDARD.md`, chưa kiểm cách overlay mang quy tắc xuống workspace.
