# Learning đề xuất cho CVF gốc — đội agent phát triển tự nghiệm thu sản phẩm dùng được trước khi giao noncoder

**Ngày:** 28/10/2026. **Nguồn:** project LAW (`local-agent-workspace`), operator chỉ định trong hội thoại 28/10/2026.
**Người lập:** Claude (Opus 5.5). **Đích:** CVF gốc `D:\UNG DUNG AI\TOOL AI 2026\Controlled-Vibe-Framework-CVF`, sau đó các workspace thừa hưởng (LAW và project sau).
**Trạng thái hiện hành31/10:** phần bổ sung mục10 đã nhập vào source canonical CVF nền theo chỉ định mới của operator; contract/learning/registry đã kiểm bounded (mục10.5). Chưa commit/push hoặc đồng bộ public. Nhãn đề xuất/chưa nộp trong các phần28/10 là lịch sử của bản ban đầu.
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
4. Sau khi bản clone nhận bản mới từ GitHub, bỏ bản sửa tay rồi đồng bộ lại; kiểm clone không còn khác `origin/main` ở 8 file. **Hiện trạng 29/10
   01:46:** bản sửa tay đã được commit cục bộ trong clone (`64edd93 docs: define developer-owned product acceptance`), kèm
   `aea3ea5 chore: checkpoint local model gateway WIP`; clone `ahead 2, behind 2`, chưa push. Không push hai commit này. Khi đến bước này, tách
   commit model gateway ra (thuộc owner khác) trước, rồi bỏ `64edd93` (ví dụ `git revert` hoặc đặt lại nhánh về `origin/main` sau khi đã giữ
   commit model gateway ở nhánh riêng); patch `511b96da…beee` vẫn là bản lưu nội dung.
5. LAW nhận lại bản CVF mới ở lượt riêng (C6 cho LAW), chạy lại full suite LAW.

### 9.6. Điều phối

- Governance đang có việc khác (commit `618caaba2`, 29/10 00:42, "operator hold" M6). Trước khi sửa, đọc handoff/brief hiện hành của governance;
  không chen vào file đang có owner.
- Không push từ bản clone. Clone đã có 2 commit cục bộ chưa push (xem 9.5 bước 4), trong đó một commit là WIP model gateway
  (`EXTENSIONS/CVF_MODEL_GATEWAY/...`) không thuộc tranche này; người làm tranche hỏi owner của WIP đó trước khi đụng tới nhánh.
- Dedup trước khi viết (mục 7): `CVF_CI2_T4_PRODUCT_READINESS_PILOT_CORPUS_PACK_2026-06-02.md`, `CVF_MSEA_R35_T2_CVF_CURRENT_PRODUCT_CAPABILITY_SNAPSHOT_2026-07-05.md`,
  mục "noncoder interaction gaps" của contract, `docs/reviews/learnings/`.

## 8. Phần chưa kiểm

Đã đọc chỉ đọc: `AGENTS.md` CVF dòng 85–125; hợp đồng mốc dòng 1–45 và các dòng có từ user/operator/acceptance/noncoder; trigger standard dòng 48–80.
Chưa đọc đủ hai standard đó, chưa đọc `CVF_PROJECT_LEARNING_LOOP_STANDARD.md`, chưa kiểm cách overlay mang quy tắc xuống workspace.

## 10. Bổ sung 31/10/2026 — kiểm soát giá trị tiến độ và chi phí

**Chỉ định mới:** operator xác nhận công việc kỹ thuật có giá trị, nhưng quy tắc bám roadmap phải giữ; thời gian/chi phí bỏ ra phải tương xứng với mức tiến tới sản phẩm XONG. Chính operator phải yêu cầu kiểm tra vì roadmap kéo dài. Không diễn giải thành cho phép bỏ gate hoặc coi công việc trước là vô ích.

**Trạng thái tiếp nhận trước upstream31/10 (lịch sử):** learning28–29/10 đã được LAW ghi nhận tiếp nhận CVF bounded tại PROJECT.md (public15e3945/operator-local4043caf14); nhãn “chưa nộp” đầu tài liệu là lịch sử của đề xuất28/10. Phần bổ sung31/10 này được áp vào hướng dẫn LAW §8.3; **chưa đối chiếu/ghi/tiếp nhận ở CVF gốc**, chưa kiểm hiệu quả thực thi. CVF owner cần dedup và nhập vào contract/cơ chế hiện hữu, không tạo thêm ledger hay tầng phê duyệt. Không suy cập nhật LAW thành upstream COMPLETE.

### 10.1. Lỗi tái diễn và nguyên nhân kiểm soát

Quy tắc10 và §8.3 đã yêu cầu mốc, toàn gap, phần lần giao đóng và phần còn lại. Sai ở thực thi: Main liệt kê đủ gap nhưng vẫn lấy việc kỹ thuật gần nhất làm việc tiếp theo; đối chiếu mốc không chi phối quyết định tiếp/dừng. Reviewer tập trung đúng nguồn/hash/phạm vi/test mà chưa phản biện mức đóng góp sản phẩm và tổng chi phí. Worker làm theo brief; trách nhiệm lựa chọn và kiểm soát ưu tiên thuộc Main.

| Bằng chứng trong LAW | Kết luận đúng phạm vi |
|---|---|
| HANDOFF11.4: chuỗi public admission → checkpoint → builder → timeout diagnostic; các nhóm gap V4/V7 vẫn mở | Nguồn sạch và diagnostic hữu ích, nhưng chưa tạo thêm bằng chứng sản phẩm dùng trọn luồng; tên mốc và danh sách gap không tự ngăn lệch ưu tiên |
| public-checkpoint/build-run/exit.json: wrapper quan sát1803.079s, behaviour gate quá1800s, không ZIP; số test/skip/fail UNKNOWN vì chưa giữ partial output | Budget từng lệnh không quản được chi phí toàn nhánh; phép chạy dài phải có khả năng trả bằng chứng dùng được khi dừng. 1803.079s chỉ là một lần quan sát, không phải tổng thời gian nhánh hay số tiền |
| timeout-diagnostics/MAIN_REVIEW.json: sửa giữ log,6mock đạt; fullgate bản mới NOT_RUN | Kiểm hẹp có giá trị kỹ thuật, không đóng nghiệm thu artifact hoặc toàn mốc; sửa nhỏ rõ nguyên nhân lẽ ra Reviewer xử lý theo §8.3, tránh giao lại Worker |
| STATE trước sửa31/10 vẫn chọn chẩn đoán runtime → artifact làm bước tiếp | Hướng đi được truyền theo trạng thái tác nghiệp thay vì xét lại thứ tự project → host/chất lượng → sửa/tiếp phiên/bảo toàn → artifact/review |

Locator receipt tương đối: `working/source-intake-20261030/fullsuite-candidate-20261031/public-checkpoint/`. Không có dữ liệu billing/token toàn nhánh để quy tiền hoặc kết luận mọi chi phí đều lãng phí. Bản STATE/HANDOFF trước sửa và SHA nằm tại `archive/maintainer/roadmap-value-control-before-20261031/`.

### 10.2. Nâng learning tại điểm ra quyết định

Quy tắc đầy đủ của LAW nằm duy nhất tại ROADMAP_HOAN_THIEN.md §8.3, mục “Quyết định tiếp tục theo giá trị và chi phí”; AGENTS.md đã dẫn tới §8.3. Phần tăng thêm là: quyết định tiếp/dừng dựa trên điều kiện sản phẩm cụ thể; chẩn đoán phải là dependency hữu hạn; tính chi phí tích lũy cùng nhánh; dừng khi không đạt đóng góp hoặc lại phát sinh chuẩn bị; chỉ mở lại với căn cứ/cách làm thay đổi; báo tiến độ bằng khả năng sử dụng và phần nghiệm thu thực đóng. Giữ nguyên authority, acceptance và gate phát hành.

**Disposition đề xuất cho CVF:** `RULE_EXISTS / EXECUTION_GAP`; bổ sung điều kiện ra quyết định vào hợp đồng mốc/template brief hiện có sau dedup. Không kết luận thiếu standard, không chỉ thêm lời nhắc hoặc tăng effort/model. Chưa triển khai machine checker; kiểm sự hiện diện trường trong brief cũng chưa chứng minh lựa chọn có giá trị.

### 10.3. Đối chiếu quy tắc trên tình huống đã gặp

Đây là kiểm nội dung bằng tình huống lịch sử, không phải phép thử host hay chứng minh đã ngăn được hành vi:

| Tình huống | Quyết định quy tắc mới yêu cầu |
|---|---|
| Brief ghi V4/V7 và đủ gap nhưng chỉ hứa thêm log/checkpoint | Chưa đủ mở lượt; chỉ rõ dependency chặn điều kiện nào, câu hỏi cần trả lời, giới hạn tích lũy và hành động sau kết quả |
| Builder timeout, chưa có ZIP; sửa diagnostic xong rồi muốn chạy lại dài | Không tự nối lượt. Giữ failure; xem lại toàn mốc/chi phí và khả năng thu evidence. Chỉ tiếp với căn cứ mới, đóng góp/giới hạn rõ; gate vẫn bắt buộc trước release |
|6mock đạt nhưng chưa có luồng người dùng trọn vẹn | Báo kỹ thuật đã đạt đúng phạm vi, chưa đóng thêm điều kiện sản phẩm; không coi revision mới là tiến độ mốc |
| Một sửa log nhỏ đã rõ cách sửa trong review | Reviewer sửa/kiểm hẹp trong cùng tranche; không thêm Worker hoặc vòng review chỉ vì sửa nhỏ |

**Điều kiện đóng learning về hiệu quả:** ở lần giao sản phẩm tiếp theo, đối chiếu quyết định trước giao với kết quả thật: đã đóng gì so cam kết, đã tốn bao nhiêu theo đơn vị quan sát được, còn gì, và có thực sự dừng/đổi hướng khi chạm điều kiện hay không. Chưa có kết quả đó thì ghi **HIỆU QUẢ CHƯA KIỂM**, không gọi văn bản mới là vấn đề đã được giải quyết. Không mở riêng một tranche chỉ để chứng minh learning.

### 10.4. Thử tại LAW ngày31/10 — LOCAL_PILOT_WITH_LIMITS

Operator yêu cầu thử tại LAW trước upstream. Gắn V4/V6/V7/acceptance28; Main chọn ca báo cáo từ nguồn → thiếu/NA/0/kỳ khác → sửa khi mở fresh context, thay mặc định chạy tiếp runtime. Tái dùng orders.csv/definitions.md và internal-comms/spreadsheet-check, không dựng framework/corpus mới. Fixture cũ chỉ là regression kết hợp sửa-tiếp việc, không holdout hoặc chứng minh chất lượng ổn định. Hồ sơ tại HANDOFF “V4/V6/V7 kiểm báo cáo và tiếp phiên” revision2 POST và `working/v4-office/acceptance-20261031/RESULT.json`.

- Hai child native độc lập fresh/fork none, requested Terra6.1High, actualbackendUNKNOWN; Main đọc đủ report/state và tính lại bằng Python CSV/Decimal. V1 có18pack/2.190.000VND NET; xác nhận mô phỏng O04=4 làm v2 thành22pack/2.670.000VND, tăng4pack/480.000VND. Giữ NA khác0/thiếu và loại dòng kỳ khác; không giả nguồn đã đổi. Hash2nguồn/2skill/index và2filev1 giữ.
- Dùng2call/0retry, dừng sau kết quả đã định, không mở thêm benchmark hoặc chạy lại builder. Thời gian quan sát177.384s từ PREreceipt tới review2, không gồm scoping trước và tài liệu cuối; billing/tokenUNKNOWN. Đây là evidence bước đầu của việc giữ giới hạn và bàn giao nội dung có ích, không phải tỷ lệ ROI hay tổng chi phí project.
- **Finding mới phải giữ:** chỉ dẫn Main tránh lộ oracle đã cấm đọc HANDOFF trong khi quy tắc bắt Worker đọc brief trước ghi; chỉ dẫn cho đọc đoạn giới hạn đến sau khi actor1 đã tạo file. Stage1 protocol NOT_MET; đọc sau không chữa hồi tố. Main chịu lỗi thiết kế brief; Worker chưa trả lại mâu thuẫn. Main sửa hẹp ngay cùng lần giao, lưu nguyênrevision1/SHA, tách oracle sang RESULT Main-only. Actor2 báo đọc revision2 trước ghi; không chứng minh host khóa tác động.
- **Bổ sung thực thi tại §8.3:** brief/quyền/revision cần dùng phải đọc được theo chính phạm vi đã giao; tách oracle khỏi brief; Main kiểm bản Worker thực nhận trước dispatch. Không tăng lượt chạy để xóa finding, không thêm tầng giám sát. Ca nội dung đạt có giới hạn không xóa vi phạm quy trình.

**Kết luận:** LOCAL_PILOT_WITH_LIMITS; nội dung/sửa-tiếp việc đạt đúng ca, toàn protocol không PASS và chưa đóng toàn mốc sản phẩm. Learning đã được thử trong công việc thật của đội dev trên DATAMOCK, chưa chứng minh hiệu quả bền vững hoặc tự cưỡng chế. Khi xét upstream phải mang cả finding/lần sửa và giới hạn, không chỉ báo “test đạt”; chưa ghi CVF gốc trong lượt này. Không mở thêm lượt thử chỉ để hoàn thiện hồ sơ learning.

### 10.5. Đã chuyển vào CVF nền ngày31/10 — CANONICAL_SOURCE_UPDATED_BOUNDED

Operator yêu cầu chuyển bài học lên CVF nền sau các lượt làm tại LAW. Đã cập nhật
nguồn canonical `D:/UNG DUNG AI/TOOL AI 2026/Controlled-Vibe-Framework-CVF`,
không sửa ngược từ public clone hoặc tạo learning family mới:

- `docs/reference/CVF_PRODUCT_MILESTONE_COVERAGE_CONTRACT_2026-10-23.md`, mục
  `Continuation Value And Cumulative Cost Decision`: quyết định tiếp/dừng theo
  đóng góp sản phẩm, chi phí toàn nhánh, dependency hữu hạn, giữ sửa nhỏ trong
  tranche, brief đọc được và lưu bằng chứng khi dừng; mục tiêu là hoàn thiện
  roadmap, không mở phép thử chỉ để chứng minh learning.
- Learning cùng family23/10 ghi recurrence LAW, năm điều kiện tiếp nhận, các
  failure của Main và bằng chứng ZIP/lifecycle thật; README thêm trigger đọc.
  Registry hiện có được rebind hash đúng finding, giữ nguyên proof máy lịch sử
  và trạng thái HTML/M6 đang giữ. Disposition RULE_EXISTS + STANDARD_UPDATED;
  không thêm schema/checker/ledger hoặc suy hướng dẫn thành tự cưỡng chế.
- Năm guard hiện có (F2G, read-ahead, Markdown, operation trace, file-size) exit0;
  diffcheck đạt, đúng bốn file CVF thay đổi, HEAD không đổi. Không chạy lại LAW
  hoặc provider/fullsuite vì chỉ chuyển văn bản/binding, không đổi artifact.

Receipt và before-bytes/SHA: `archive/maintainer/cvf-learning-upstream-20261031/UPSTREAM_RECEIPT.json`.
Bản nguồn mục10 trước upstream được giữ nguyên trong archive này. Hai builder
LAW quan sát1641.078+1264.562=2905.640s; lượt đầu thất bại và lỗi checker raw-vs-LF
được giữ, không tính thành PASS. ZIP hiện hành/13CLI/freshVIEN/two upgrades đạt
bounded, không chứng minh ngăn tái diễn bền vững hay ROI toàn project. Không mở
thêm learningtrial. Phần chưa làm: commit/push/public-sync/rollout sibling và
machine semantic enforcement; toàn gap roadmap50/PRERELEASE_NOT_READY giữ.
