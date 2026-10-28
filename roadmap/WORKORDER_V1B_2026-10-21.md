# Work order V1-B — Trace thật của Main và phương pháp nghiệp vụ

**Ngày:** 21/10/2026. **Trạng thái lượt gốc:** `REVIEWED_PARTIAL — V1B_LIVE_METHOD_PROOF`; V1 vẫn mở; không retry trong envelope V1-B gốc. V1-B2 ở mục8 là attempt mới khi operator giao Claude.  
**Worker tác nghiệp:** Claude do operator giao/chọn model-effort; **Orchestrator/reviewer:** Codex. Đây là bước sau [V1-A đã nhận nền](WORKORDER_V1A_VAN_PHONG_TRUNG_TAM_2026-10-21.md), không giao lại V1-A hoặc mở V2 trước nghiệm thu V1.

**Kết quả bổ sung:** **V1-B2 — ACCEPTED_WITH_LIMITS**, review tại mục8.6. Đã có terminal findings Reviewer và bản sửa Main trong lab; giữ V1-B gốc `REVIEWED_PARTIAL`, V1 tổng thể PARTIAL. Cả hai envelope đã dùng hết, không có lượt AI mới được giao ở review này.

**Phân kỳ cập nhật sau audit next 21/10:** V1 đã nhận `ACCEPTED_WITH_LIMITS — V1_MAIN_METHOD_ROUTING` theo bảng đối chiếu acceptance gốc ở roadmap riêng. Các phát biểu V1 còn PARTIAL vì thiếu product grant/checkpoint tích hợp dưới đây là lịch sử đã được sửa về phân kỳ: hai điều đó thuộc V2, không phải gate V1 mới. Verdict/evidence từng lượt giữ nguyên, không biến lab thành consent/grant hoặc RESULT thật. Việc kế tiếp ở WORKORDER_V2A_2026-10-21.md; không chạy lại phiếu này.

**Review kế hoạch:** `v1a_code_review`, tool dispatch `gpt-6-sol/medium`, đọc độc lập toàn phiếu và không thấy blocker trong phạm vi giao. Đã làm rõ inventory ở mục4 chỉ là trạng thái đĩa; chưa review evidence live hoặc cấp quyền sản phẩm.

**Disposition Codex 21/10/2026:** nhận proof Main đọc MAIN, tiếp cận catalog qua `office.py list`, tự chọn phương pháp/lý do; Worker native đọc contract/nguồn và tạo candidate; Reviewer native được gọi và đọc nhưng **không trả findings**. Main không Read trực tiếp catalog/hợp đồng. Không có RESULT nên không chạy checkpoint có RESULT; không dựng bù. Nhóm C/D còn thiếu, không đóng V1 hoặc chuyển V2 bằng việc chấp nhận giới hạn.

- Root đối chiếu cây lab còn tồn tại: 298 file khớp `after_tree`; so baseline 293 file thêm đúng 5, đổi/xóa 0 trong cây này. Loader v3 nhận TASK, `office.guard_task=[]`, ba input/context digest khớp. Đây là kiểm cấu trúc/bytes, không phải PASS nội dung, grant hoặc sandbox. Ba hash owner V1-A trong mục2 giữ nguyên.
- Hai điểm cần sửa trước khi nhận chất lượng nội dung/brief: candidate mục5 làm mất trạng thái M4 **ghi nhận đã thống nhất tại cuộc họp** vì mâu thuẫn M5. Cần giữ trạng thái ghi nhận đó, đồng thời chưa chốt ngày áp dụng (M4:20/10; M5:22/10/2026); chưa có căn cứ M5 thay thế M4 hoặc xác định thẩm quyền cuộc họp. Brief Reviewer chỉ giao nguồn/candidate và yêu cầu đối chiếu của Main, thiếu yêu cầu gốc đúng revision và phương pháp đã tạo candidate theo input contract. Không sửa candidate/evidence gốc trong lượt review này.
- CLI kết thúc `error_max_budget_usd` dù exit0/`is_error=false`; telemetry 0.7669449 USD so yêu cầu 0.75, vượt 0.0169449 USD, không phải hóa đơn. Effort và việc child Reviewer thực sự dừng chưa quan sát. Không xác nhận cơ chế kiểm cap giữa turn chỉ từ kết quả này. Lệnh Bash ghép ngoài allow-rule đã được thử và bị từ chối; sau đó Main chạy dạng đơn được phép. Không gọi toàn lượt là không có hành vi thử vượt envelope.
- `grants=[]`/`grant_refs=[]` chỉ chứng minh bài đo theo quyền bảo trì. Snapshot lab không bao phủ sự cố setup `materialize` ghi nhầm `D:\c\Users\…`; số 270 file và việc xóa nội dung là lời bàn giao, chưa có argv/inventory trước-sau để xác minh. Root thấy `D:\c` là thư mục thường, rỗng lúc kiểm, không xóa. Trước setup sau cần đích Windows tuyệt đối được resolve và kiểm nằm trong lab dự kiến trước ghi; xử lý guard giao đúng owner, không sửa code trong tranche evidence này.

Review độc lập: `v1b_trace_review` (`gpt-6-sol/medium`) và `v1b_content_review` (`gpt-6-luna/max`), chỉ đọc; Root đối chiếu có mục tiêu và ghi disposition. Review bảo trì này không phải phản hồi của child Reviewer bị thiếu. Không gọi AI lại, tăng budget, thay evidence hoặc phát hành. Phần dưới giữ yêu cầu gốc của lượt đã chạy; envelope một attempt đã dùng hết.

## 1. Mục tiêu và quyền

Lấy một trace host thật: người dùng giao việc bằng lời thường → Main đọc hướng dẫn và catalog → tự chọn phương pháp phù hợp → giao core role → role đọc đúng contract đã bind và nguồn → trả candidate → đối chiếu có mục tiêu. Chứng minh trách nhiệm và phương pháp đã đi vào lần gọi thật, không chỉ có file cấu hình hoặc người chạy gán sẵn method rồi gọi đó là Main biết chọn.

Thực hiện trong **lab riêng, chỉ dữ liệu giả**, theo ngoại lệ thử nghiệm Claude CLI trong PROJECT kho nguồn ngày18/10. Đây là quyền bảo trì thật cho bài đo, không phải grant sản phẩm, không cho sửa profile/native kho nguồn hoặc project thật. Profile lab có thể giữ `grants=[]`; nếu vậy phải ghi đúng: chỉ đo dispatch/phương pháp trong envelope bảo trì, chưa nghiệm thu đường cấp/xác thực grant sản phẩm. Không tạo USER_CONFIRMATION/grant giả hoặc migrate dòng PROJECT để làm proof đẹp.

Review kế hoạch này không cấp thêm quyền. Không sửa host/global/admin, account/provider/auth, CVF cha, schema/pin, native adapter hoặc runtime. Không dữ liệu thật, web/kho/mailbox/MCP bên ngoài, gửi nội dung hay phát hành. Mặc định không sửa code sản phẩm ở tranche này; lỗi có locator thì trả đúng owner, không âm thầm mở feature.

## 2. Preflight đã kiểm và điều chưa biết

- Kho nguồn hiện tại: `execution_profile.py status` báo `PROFILE_ABSENT/LEGACY_MIGRATION_REQUIRED`; native Worker `ABSENT`, không receipt. Không thử gọi vai sản phẩm ở đây hoặc tự thêm grant. Tình trạng này không chặn chuẩn bị lab theo quyền bảo trì riêng.
- `Get-Command claude`, `claude --version`, `claude --help` đã chạy thành công trong lượt soạn phiếu: Claude Code **2.1.81**, executable WinGet trên máy. Chỉ gọi version/help, chưa gọi model, chưa kiểm auth/quota/model khả dụng hoặc VS Code invocation.
- Help cục bộ có `--print`, `--model`, `--tools`, `--allowedTools`, `--setting-sources`, `--strict-mcp-config`, `--mcp-config`, `--no-session-persistence`, `--max-budget-usd`, `--output-format stream-json`, `--verbose`. Có flag không chứng minh mode/tool/quyền có hiệu lực; phải ghi argv thực và trace thực. Không nâng cấp/cài CLI để chạy phiếu.
- Bài đo core ngày19/10 ở `roadmap/evidence/a10-core-native-2026-10-19/README.md` đã có lab riêng/adapter owner/trace parent-child. Chỉ tái dùng cách tổ chức; evidence đó chưa có method V1-A nên không thay trace V1-B mới. Không chép receipt/native/budget verdict cũ thành lượt mới.
- Nguồn V1-A cần giữ: `tools/office.py` SHA256 `867c517dc0a2a2b7a7a4ef3895e30cf192821a8c7b037d1d5150c83c0ce6dfd4`; `roles/README.md` `5b7e846e208324aa37e9ad207f9cf7e6ee3b0a327e5b5acd8f84a9a4fea1817b`; native adapter `e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e`. HEAD tham chiếu `bcb5153`, worktree dirty có sẵn. Hash khác thì đối chiếu delta thật, không reset/khôi phục theo bảng.

## 3. Envelope một lượt

Ghi request/preflight trước gọi: version/path executable; model ID requested cho tester Main/Worker/Reviewer; effort requested hoặc null; scope đọc/ghi; argv; timeout; giới hạn; căn cứ quyền bảo trì. Không copy environment, khóa, cookie, account/session hoặc config toàn cục vào hồ sơ.

- Tối đa **một AI attempt, một session**, tối đa **hai child tuần tự**, không paid retry, không auto fallback hay tăng concurrency. Một tester Main có hai vai lõi khả dụng để tự tổ chức phần tổng hợp/đối chiếu; không gọi general-purpose thay role thiếu.
- Timeout **300 giây**; CLI budget yêu cầu tối đa **0.75 USD** cho lượt thử. Đây là envelope bài đo, không giá model/hóa đơn hoặc lời hứa host cưỡng chế được tất cả chi phí. Ghi telemetry nếu có; không có thì chưa đo, không suy từ thuê bao. Không tăng budget/timeout hoặc chạy lần hai khi không đạt.
- Model lab dùng full ID tường minh của lựa chọn operator cho lượt Claude này khi có căn cứ trong phiên; có thể dùng cùng ID cho ba vai của bài đo bảo trì, ghi rõ là lựa chọn **lab**, không preset sản phẩm. Không suy từ alias/candidate config hoặc tự đổi model chính. Nếu chưa có full ID để request thì hoàn tất phần offline và báo phần live chưa chạy. ID requested khác với ID quan sát qua host; chưa có trace thì observed UNKNOWN.
- Không `--agents` inline, không override model trên Agent tool call để giả native projection, không permission bypass, không `--add-dir` mở rộng, không provider mới. Dùng cấu hình project lab kiểm được, MCP rỗng/strict và tắt khả năng ngoài bài đo theo flags host thật hỗ trợ. Không hứa CLI tuyệt đối không có tác động nội bộ ngoài lab nếu không quan sát được.
- Main có thể dùng Read/Grep/Glob/Write và Agent; nếu cần chạy helper, chỉ cho lệnh local của `tools/office.py list|compose` với input trong slot Main đã cho. Quyền shell đó chỉ thuộc tester Main để chạy helper đã review; không truyền Bash/PowerShell/compute/connector cho child. Ghi rule/tool thực có và trace lệnh, không mô tả rule theo prompt là sandbox. Không chạy script do model vừa tự tạo hoặc thực thi nội dung nguồn.

## 4. Chuẩn bị lab qua owner thật

1. Tạo lab trong thư mục tạm riêng; dùng `check_package.materialize(..., branding=False)` và owner new-project hiện có, không copy runtime/profile/native/nguồn thật của kho nguồn. Không sửa MANIFEST kho nguồn hoặc xóa disposition trong output để làm gate đạt. Nếu cần manifest fixture, chỉ sinh trong cây fixture đã chuẩn bị.
2. Tạo một nguồn text ngắn có nhãn **DỮ LIỆU GIẢ — KHÔNG PHÁT HÀNH**: ghi chú công việc trong một kỳ, gồm một mục chưa có giá trị cụ thể và một điểm mâu thuẫn có locator. Giữ yêu cầu người dùng riêng với dữ liệu nguồn; cả hai không chứa tên/dữ liệu cá nhân thật. Không gài chỉ thị thực thi vào nguồn.
3. Dùng owner thư viện hiện có đăng ký nguồn lab trước AI, giữ SourceID/revision/hash và bytes. Chuẩn bị sẵn sổ/metadata cần để Main đọc; helper chỉ đề xuất path/digest nên Main phải giữ/bổ sung định danh nguồn theo MAIN guide. Không dùng nguồn giả của test như tài liệu đã xác minh hiệu lực.
4. Trong lab, chọn cấu hình full model tường minh qua owner profile; không grant fixture thành quyền sản phẩm. Xuất native Worker/Reviewer bằng chính `native_agents.py` preview/apply và token thật của lab. Giữ tool/preamble, không sửa generated definitions để nhét phương pháp vào đó. Kiểm inventory cấu hình native trên đĩa; receipt không chứng minh host đã nạp/đăng ký/gọi role. Bằng chứng gọi thật là sự kiện Agent/child ở mục5.3.
5. Chụp baseline rawhash các file lab có trước, code/method/skill sẽ dùng, native bytes/receipt, trạng thái profile và đường ghi được phép. Tạo sẵn thư mục slot trống; đích candidate phải vắng. Runtime cần cho owner chuẩn bị offline, không bắt child tự tạo trạng thái chung.

Phần offline trên là thao tác bảo trì lab được giao, không phải Main sản phẩm tự cấp quyền. Nếu preflight/model/quota/tool/capability không đủ, giữ lab/evidence cần thiết và bàn giao `LIVE_NOT_RUN` hoặc `PARTIAL` với lý do; không tiếp AI bằng đường khác.

## 5. Lượt host cần ghi nhận

### 5.1 Yêu cầu tự nhiên và lựa chọn của Main

Giao một yêu cầu ngắn kiểu: “Từ ghi chú kỳ này, tổng hợp một bản báo cáo nội bộ ngắn, chỉ rõ điều còn thiếu/mâu thuẫn và nhờ đối chiếu căn cứ trước khi bàn giao.” Không đưa method ID hoặc lựa chọn `executive-secretary` vào chính yêu cầu nghiệp vụ của user. Envelope và danh sách vai/tool được phép là hướng dẫn vận hành riêng, không phải lời user đã chọn chuyên môn.

Main đọc `roles/office/MAIN.md` và catalog bằng tool thật, nêu lý do chọn phương pháp và điều kiện xong. Không đòi Main gọi đủ bộ; không chèn một bản ghi chọn phương pháp do driver viết rồi gọi đó là quyết định tự nhiên của Main. Phiên này tối đa hai child; Main có thể tự đọc nguồn ngắn và lập brief, không phát sinh Scout thứ ba.

### 5.2 Brief, TASK và hai vai lõi

- Main chuẩn bị brief qua helper và/hoặc nội dung contract thật đã đọc, nhưng nếu không chạy helper thì ghi rõ cách lập brief; không nói đã chạy `office.py` khi chưa chạy. Method chọn, contract version/path/digest, nguồn/SourceID/revision, yêu cầu cụ thể và vùng ghi phải đi vào TASK/brief. TASK có marker requirement OFFICE-METHOD và context catalog/contract/skill thực dùng; không thêm field vào schema v3.
- Chỉ Main được tạo mới hồ sơ ở vùng `working/v1b/main/` và các TASK/metadata trong slot đã xác định; lập danh sách đích cụ thể trước AI. Main không tự viết candidate thay Worker, không sửa code/profile/native/sổ/STATE/HANDOFF của lab trong lượt AI. Helper shell chỉ đọc; nếu Main không dùng được helper theo tool/rule thì báo đúng, không cấp shell cho child.
- Worker thực được gọi bằng native core đã xuất; trace có parent tool ID/child model khi host cung cấp. Child phải dùng Read mở **đúng contract phương pháp đã bind** và nguồn được giao; sau đó Write đúng **một candidate text mới** trong `working/v1b/report/assignments/a1/candidate/draft.txt`. Giữ nhãn dữ liệu giả/CANDIDATE, phần thiếu và mâu thuẫn. RESULT/metadata theo workflow hiện hành; nếu host/role trả qua kênh native thì Main có thể lưu lời khai nguyên nghĩa trong đích đã khai, ghi ai lưu, không giả role đã Write file.
- Nếu Worker chưa tạo candidate đúng slot thì dừng, không gọi Reviewer hoặc Main viết bù. Nếu có candidate thì Main giao core Reviewer phương pháp đối chiếu; Reviewer Read đúng method/nguồn/candidate, trả finding/locator/phần chưa kiểm qua kênh native, không Write hay sửa artifact. Main lưu phản hồi với nguồn gốc ROLE_REPORT, không tạo verdict PASSED/user acceptance từ nhãn role.
- Đây là kiểm dispatch/phương pháp, không giao một báo cáo nghiệp vụ hoàn chỉnh V2. Không publish/select/accept kết quả, không đưa bản thử vào output dùng thật. Mọi review bắt buộc hoặc task type checker chưa hỗ trợ vẫn giữ giới hạn; không gọi checker PASS để chứng minh toàn workflow hay bỏ review để lấy PASS.

Scope/cách ghi TASK, RESULT, nguồn và candidate dùng đúng owner/recipe đã có. Đọc lại bản TASK hiện hành và chạy guard/binding/checkpoint có đối tượng áp dụng; trường hợp Reviewer chỉ trả qua kênh native không bịa một candidate ghi đĩa để ép checkpoint Worker. Không sửa protocol để khớp phép đo.

### 5.3 Trace và đối chiếu sau lượt gọi

Giữ stdout stream-json và stderr thật, exit/result status, parent-child IDs và tool use/result events; không chỉ lưu tóm tắt do model tự viết. Nhận dạng requested/observed/UNKNOWN riêng. Trace phải cho thấy child đọc contract hiện hành, không chỉ nhắc tên method trong câu trả lời.

Đối chiếu file sau AI với baseline: nguồn/method/skill/profile/native/sổ và mọi file ngoài write set giữ bytes; chỉ đúng đích mới đã giao được thêm. File nằm trong write set chưa chứng minh nội dung đúng: mở candidate/nguồn và so nhận định trọng yếu có mục tiêu. Không gọi snapshot này là sandbox hoặc chứng minh không có tác động trên toàn máy.

Timeout, thiếu reply hoặc lỗi không chứng minh chưa ghi. Kiểm candidate/hồ sơ/trace/owner evidence trước mọi kết luận; không thử AI lại. Không tự void bằng sửa RESULT cũ, không sửa hash để ghép bằng chứng, không ghi UNKNOWN thành không tác động. Nếu host/CLI không có stop proof thì ghi chưa quan sát dừng thật.

## 6. Acceptance và cách nhận kết quả

| Nhóm | Bằng chứng cần có |
|---|---|
| A — Quyền và preflight | Request ghi trước chạy, executable/version/model/scope/limits và căn cứ bảo trì; lab tách biệt, không grant sản phẩm giả. Model/host/tool thiếu được giữ chờ đúng. |
| B — Main chọn cách làm | User request tự nhiên, Main đọc MAIN/catalog, có lựa chọn/lý do cụ thể; driver không chọn sẵn rồi gọi là routing Main. File cấu hình/receipt không thay trace. |
| C — Đúng chuyên môn ở child | Một native Worker và một native Reviewer được gọi thật, các Read contract/nguồn/candidate gắn đúng parent-child; candidate do Worker tạo trong slot. Phương pháp/bytes trong TASK khớp artifact đã giao. Không override/inject named roles. |
| D — Kết quả và bảo toàn | Candidate giữ CANDIDATE/dữ liệu giả/thiếu/mâu thuẫn; Reviewer trả findings từ nguồn thật đã mở; Main không tự viết thay. Snapshot/owner guards chứng minh đúng phần đã quan sát, không biến thành enforcement. |
| E — Giới hạn và evidence | Một attempt trong envelope, không retry/bypass; logs và artifact đủ truy lại; chỉ đo CLI 2.1.81/host thực của lần này, không gán VSCode/host khác. Quyền bảo trì lab khác grant vận hành user, không hứa chất lượng chuyên môn/full V2. |

Trả **`IMPLEMENTED_PENDING_REVIEW — V1B_LIVE_METHOD_PROOF`** khi có lượt thật và evidence đủ, hoặc **`PARTIAL/LIVE_NOT_RUN`** đúng nguyên nhân nếu thiếu. Codex review rồi mới quyết định phần nào của V1 đạt trên một host; nếu còn tiêu chí V1 chưa đủ thì giữ PARTIAL, không tự đóng toàn V1/V2 từ một lab thành công.

Không mặc định rerun 21 target V1-A hoặc fullsuite/gate; tái dùng evidence còn đúng hash. Chỉ chạy test mới khi có bug/delta thực, không viết code/tests chỉ để một trace có tên mới. Điểm mốc kế tiếp chỉ là nhận proof V1-B; V2 sau khi dependency V1 được disposition rõ.

## 7. File bàn giao và kết thúc lab

Một bộ evidence tại `roadmap/evidence/v1b-live-method-2026-10-21/`: request/preflight cùng assessment thực, stream/stderr, nguồn giả và candidate nguyên bytes, snapshot native/receipt cần chứng minh lần gọi. Có thể gộp metadata vào một JSON; không lập báo cáo/ledger/registry riêng, không copy toàn bộ lab hoặc dữ liệu auth. Script hỗ trợ nếu thật sự cần đặt ở `working/v1b/scripts/`, theo AGENTS/skills README; không lẫn file giao, không thêm vào tools sản phẩm.

Giữ phạm vi và hash V1-A; chỉ ghi evidence, STATE/HANDOFF và hàng V1 theo kết quả thực, không tự đổi verdict nghiệm thu. Sau đo có thể retire native lab qua owner và kiểm đích/bằng chứng, không xóa recursive, không sửa native kho nguồn/global. Nếu lỗi khi retire thì observe đúng trạng thái, không dựng lại để làm sạch hồ sơ.

HANDOFF ghi model/effort requested/observed, scope/budget/timeout có đo và phần không đo; lệnh thật, source/artifact hash, kết quả/giới hạn, ai ghi hồ sơ. STATE tám heading/tối đa khoảng60dòng. Không stage/commit/push, không release, không ghi nhận thành công trước hành động.

## 8. V1-B2 — Hoàn thiện brief và proof Reviewer

**Trạng thái sau review:** `ACCEPTED_WITH_LIMITS — V1B2_REVIEW_COMPLETION`; yêu cầu giao gốc dưới đây giữ làm lịch sử, không cho chạy lại. Operator yêu cầu tiếp tục sau review V1-B. Tranche chỉ hoàn thiện đầu vào/kết quả của Reviewer và xử lý phát hiện; không dựng lại proof Worker, không mở V2. Quyền bảo trì lab PROJECT là căn cứ; không tạo grant sản phẩm. Các giới hạn của lượt cũ vẫn giữ nguyên với lượt cũ.

**Review kế hoạch:** `v1b_trace_review`, cấu hình `gpt-6-sol/medium`, đọc độc lập mục8/header và owner liên quan, không thấy blocker để giao Claude. Root đã làm rõ hai điểm reviewer đề nghị: khai attempt/cost lũy kế và TASK Reviewer read-only/task_id riêng. Đây là review kế hoạch; live B2/khả năng host/ngân sách thực chưa đo.

### 8.1 Đầu vào và owner

- Tái dùng bộ `roadmap/evidence/v1b-live-method-2026-10-21/` nguyên bytes: yêu cầu giả, nguồn SRC-000001/revision1, TASK Worker, candidate, worker report, trace và request có snapshot. Đọc disposition đầu phiếu, không lấy assessment làm verdict độc lập.
- Dùng lab còn tồn tại được chỉ đúng bởi `request.json.lab`; không tự dựng lại bằng `materialize`, không sao chép toàn lab. Nếu lab mất hoặc bytes liên quan lệch snapshot mà chưa giải thích được, chuẩn bị brief từ evidence rồi trả `OFFLINE_PREPARED/LIVE_NOT_RUN`; không tìm đường gọi khác.
- Owner cấu trúc: `tools/office.py`, recipe TASK/checkpoint trong `roles/README.md`, core native Reviewer đã xuất trong lab. Không sửa code sản phẩm, hợp đồng, profile/native/schema, thư viện nguồn, pin hoặc MANIFEST. Script hỗ trợ bài đo, nếu cần, đặt ở `working/v1b-review-completion/scripts/`; không gọi lại `run_v1b.py run`.

### 8.2 Chuẩn bị offline trước model call

1. Resolve và kiểm đường dẫn **trước mọi ghi trong lab**: đầu vào lab phải là đường Windows có drive tuyệt đối, không nhận `/c/...`, đường tương đối drive hoặc root-relative. So đích resolve với lab gốc trong request; kiểm tổ tiên không qua symlink/junction/reparse bằng owner đã có. Mọi đích AI mới phải nằm trong slot nêu dưới và chưa tồn tại; tạo mới không ghi đè. Evidence/script bảo trì chỉ ghi ở hai thư mục kho nguồn được giao tại mục8.1/8.4, kiểm đích tương tự. Kiểm path âm bằng thao tác chỉ đọc, không tạo file ngoài lab. Không sửa/xóa `D:\c` hoặc quét/xóa ngoài cây này.
2. Chụp baseline mới, đối chiếu snapshot sau V1-B và hashes nguồn/yêu cầu/candidate/Worker TASK/catalog/hai hợp đồng thực đọc/native Reviewer/profile. Có delta thì phân loại, ghi locator, không reset/sửa hash để làm khớp. Kiểm trước khi gọi rằng lượt cũ không còn tác vụ local được host báo đang chạy bằng quan sát sẵn có; không kill hoặc resume lượt cũ. Không có stop proof từ xa thì giữ UNKNOWN, không gọi là đã dừng; nếu host báo còn chạy thì giữ phần live chờ, không chồng lượt.
3. Chuẩn bị yêu cầu tiếp việc **có nhãn lab giả**: đã có bản nháp, cần đối chiếu với yêu cầu gốc/nguồn/phương pháp, trả phát hiện trước khi sửa, chưa bàn giao. Phân biệt yêu cầu giả của bài đo, diễn giải của Main và quyền bảo trì thật; không ghi fixture thành grant/consent thật.
4. Brief Reviewer phải có yêu cầu gốc đúng revision/digest; nguồn SRC-000001/revision1; candidate gốc đúng digest; Worker TASK và hợp đồng executive-secretary đã bind; hợp đồng evidence-reviewer/catalog hiện hành. Nêu đúng read set này, không giới hạn chỉ hai file như lượt trước. Dùng helper compose chỉ đọc và ghi rõ phần Main bổ sung; không coi input proposal của helper là nguồn đã có định danh.
5. Mỗi phần việc có TASK/slot riêng. Main tạo TASK v3 mới cho Reviewer với task_id riêng/revision1 (không sửa TASK Worker), marker `OFFICE-METHOD:evidence-reviewer:v1`, đúng actor/envelope Reviewer, giữ `grant_refs=[]` và ghi giới hạn lab. Effects chỉ `operation=read`, `write_zone=none`, targets là read set, `on_missing=RETURN_TO_MAIN`; bỏ `expected_outputs`, không gán Write cho Reviewer để lưu report. Bind yêu cầu/nguồn/candidate/Worker TASK làm input phù hợp; catalog/hợp đồng Reviewer qua context của compose. Hợp đồng thư ký được truy từ context của Worker TASK gốc, so riêng đúng bytes trước giao; không nhét hợp đồng office thứ hai vào context của TASK Reviewer làm sai guard. Chạy loader/guard và kiểm dependency bytes thực, không chỉ kiểm chuỗi digest.

### 8.3 Envelope mới, thu hẹp còn một Reviewer

**Tối đa một AI attempt / một session Main, một native child `law-reviewer`, tuần tự; timeout300s; CLI budget yêu cầu0.75 USD; không paid retry/fallback/tăng budget.** Envelope này chỉ có hiệu lực cho V1-B2 khi operator chuyển mục8 giao Claude; không gia hạn lượt V1-B đã hết. Đây là tham số yêu cầu CLI, không trần chi phí cứng hay cam kết hóa đơn. Nếu mô hình/host/quota không đủ, trả PARTIAL/LIVE_NOT_RUN, không đổi provider/model hoặc tăng giới hạn để hoàn tất.

Khai chi phí/lượt lũy kế minh bạch: hiện V1-B đã chạy1attempt, telemetry0.7669449 USD; V1-B2 **chưa chạy**. Nếu B2 được gọi thì tổng là2attempt, mỗi envelope yêu cầu0.75 USD (tổng tham số yêu cầu1.50 USD), telemetry B2 đo riêng rồi cộng khi có; không coi con số1.50 là hard cap/hóa đơn. “Không retry” ở đây áp dụng bên trong từng envelope, không che lượt bổ sung sau thất bại.

- Ghi request/version/executable/full model IDs/effort requested trước chạy; chọn model lab có căn cứ ở phiên operator giao, không suy preset sản phẩm. Requested/observed/UNKNOWN riêng. Không gọi Worker/Scout, không tạo lại báo cáo từ đầu, không override model ở Agent call hoặc dùng `--agents` inline.
- Giữ hạn chế host của V1-B: project-only settings, MCP rỗng/strict, không permission bypass/global/auth/admin/mạng ngoài/provider khác. Child chỉ Read/Grep/Glob; Main shell chỉ `office.py list|compose` dạng đơn đã được phép; không pipeline, `python -c`, `head` hoặc lệnh ghép. Quy tắc prompt/cấu hình vẫn cooperative, không gọi là sandbox.
- Main đọc MAIN và dùng catalog/helper để tự xác định phần đối chiếu, đọc hợp đồng Reviewer và input contract khi hoàn thiện brief. Native Reviewer phải thực sự Read yêu cầu gốc, source, candidate, Worker TASK, hợp đồng Worker và hợp đồng Reviewer/catalog; trả findings có vị trí hai phía, tác động, phạm vi/chưa kiểm qua kênh native. Không chỉ trả nhãn PASS. Không nhét đáp án M4 của Codex vào brief để thay việc mở nguồn và tự đối chiếu.
- Ghi đủ stream/stderr và kết quả terminal của Agent. Main lưu phản hồi **nguyên nghĩa**, nhãn ROLE_REPORT, ai lưu; không bịa findings từ tool reads hoặc lời Main. Nếu không có terminal reply thì PARTIAL, không sửa candidate để giả đã qua review và không chạy tiếp lượt khác.
- Sau khi có findings, Main xử lý đúng phần sửa rõ trong **một candidate mới**; không ghi đè candidate/Worker report/TASK/RESULT cũ. Ghi tác giả bản sửa là Main, liên kết digest bản gốc và findings. Với M4, cần giữ việc nguồn ghi đã thống nhất tại họp đồng thời không tự xác định ngày hiệu lực giữa M4/M5; giữ thiếu M2, đề xuất M6 và nhãn suy luận. Phát hiện đòi thêm nguồn/thẩm quyền thì giữ cần xác nhận. Không tự đổi sổ thành đã xác minh.

### 8.4 Write set và bằng chứng

Tạo sẵn thư mục slot trống bằng setup, rồi snapshot trước AI. Main chỉ được tạo mới trong lab:

```
working/v1b-review-completion/main/compose-review.json
working/v1b-review-completion/review/TASK.json
working/v1b-review-completion/main/reviewer-report.txt
working/v1b-review-completion/main/correction-note.txt
working/v1b-review-completion/candidate/draft-r2.txt
```

TASK nhận và slot candidate của Reviewer tách khỏi Worker cũ; Reviewer chỉ trả kênh native, không Write file. Bản sửa cuối vẫn **CANDIDATE / DỮ LIỆU GIẢ / CHƯA ĐƯỢC CHẤP NHẬN**; không publish/select/accept hoặc đưa vào output dùng thật. ROLE_REPORT không phải RESULT: không chế RESULT cho Worker cũ, không chạy checkpoint không có đối tượng rồi gọi PASS. Trước tích hợp thật vẫn cần đủ TASK/RESULT/binding/checkpoint của workflow; tranche này chưa tích hợp.

Một bộ evidence mới tại `roadmap/evidence/v1b-review-completion-2026-10-21/`: request/preflight/baseline-after/assessment, prompt/stream/stderr thật, brief/TASK/report và bản sửa/note cùng digest/dependency refs cần truy lại. Không sửa bộ V1-B hoặc copy toàn lab. Nếu CLI dừng trước lưu report mà stream có terminal native reply đầy đủ, maintainer được lưu nguyên phản hồi từ trace, ghi ai lưu/sau lượt; không gán là Main/Reviewer đã ghi trong lần live. Không có terminal reply thì không dựng report.

### 8.5 Kiểm và bàn giao

- Tự xem diff, source/dependency bytes, TASK loader/guard, report nguyên nghĩa và snapshot: chỉ write set mới đã khai; không file cũ đổi/xóa. Snapshot chỉ bao phủ lab, không chứng minh toàn máy. Ghi riêng stop proof, budget subtype/telemetry và các lệnh bị từ chối nếu có.
- Đối chiếu bản sửa đúng findings/nguồn/yêu cầu/phương pháp; đặc biệt M4/M5, thiếu M2, đề xuất M6, số/ngày/quote, không bịa owner/deadline. Note nêu từng finding đã sửa/chưa sửa và lý do. Không đổi bản sửa thành đã review chỉ vì report nói về bản gốc; Codex kiểm phần delta trước disposition.
- Không rerun fullsuite/21 target V1-A khi product bytes giữ nguyên. Kiểm path trước ghi và các phản ví dụ chỉ đọc, recipe/guard/digest, EOL/diff của file đã chạm là đủ cho bài đo; không viết test mirror hoặc thêm checker mới. Báo phần chưa kiểm đúng thực tế.
- Bàn giao `IMPLEMENTED_PENDING_REVIEW — V1B2_REVIEW_COMPLETION` khi có terminal findings và bản sửa có truy vết; thiếu thì PARTIAL/LIVE_NOT_RUN. HANDOFF ghi cấu hình/lệnh/evidence/giới hạn và tác giả từng artifact; STATE giữ8heading/≤60dòng. Codex review rồi mới disposition **phần còn thiếu V1-B**; không tự đóng toàn V1, nhận quyền sản phẩm hoặc chuyển V2 từ lab này. Không stage/commit/push/release.

### 8.6 Review Codex — ACCEPTED_WITH_LIMITS, 21/10/2026

Nhận **proof hẹp của B2**: Main chọn phương pháp đối chiếu/hoàn thiện brief, một native Reviewer Read đủ8file và trả findings F1–F8; Main lưu nguyên văn nội dung phản hồi rồi tạo r2/note mới. Không còn thiếu terminal findings như lượt V1-B gốc. Sol Medium rà trace/TASK, Luna Max rà report và delta nội dung; Root chạy loader/guard và đối chiếu bytes, không gọi CLI AI/test suite.

- **Sửa lời bàn giao bằng trace:** stream62event, Agent reply ở event50 (nội dung7.178ký tự; metadata agentId/usage tách riêng hợp lý). Write r2 event59 **có** tool_result success event60; Write note event61 mới thiếu tool_result trước budget event62. Cả hai file khớp chính xác content Write và tồn tại sau lượt; không suy thiếu phản hồi thành không ghi. Giữ request/assessment và HANDOFF Claude nguyên trạng lịch sử, đọc correction này khi dùng.
- **Cấu trúc/bảo toàn:** snapshot298→303file, thêm đúng5write-set, đổi/xóa0 trong lab; Sol so cây live khớp snapshot. Root đối chiếu cả5bản copy evidence khớp live; TASK được loader v3 nhận, `office.guard_task=[]`,6input/context digest khớp; TASK/candidate Worker cũ nguyên bytes. Ba hash owner V1-A mục2 không đổi. Không kiểm `_INDEX.xlsx` hoặc chạy checkpoint có RESULT; không coi guard là PASS nội dung/quyền.
- **Delta nội dung:** M4 giữ ghi nhận thống nhất tại họp, nguồn không nêu người có thẩm quyền chốt, ngày áp dụng giữa M4/M5 còn cần xác nhận; không chọn M5 thay thế M4. F3–F6 đã xử lý; F8 đủ cho subset lab với giới hạn trên. F1 ghi rõ dựa trên bản trích sổ, sổ gốc chưa mở; F7 chỉ rút gọn một phần, note nói gộp mục5–6 nhưng thực tế vẫn có hai mục. R2 dòng18 trích `lịch…` khác chữ hoa `Lịch…` trong M4: lỗi nhỏ còn giữ, phải sửa quote/paraphrase trước khi dùng; không gọi quote này chính xác từng chữ. M1/M3/48/6/K-07/ngày/M5 khớp fixture, thiếu M2 và đề xuất M6 vẫn giữ. Codex đã đọc delta r2; không có native Reviewer lượt hai hoặc user acceptance. Không sửa evidence để che residual.
- **F2 disposition:** hai nhãn attribution khác nhau cho cùng fixture/digest còn là sai lệch hồ sơ. USER_CONFIRMATION/USER_MESSAGE của TASK cũ chưa được fixture chứng minh là xác nhận người dùng thật; UNVERIFIED/NONE ở TASK mới khai đúng giới hạn dữ liệu giả. Không cần người dùng lựa chọn một nhãn để hợp thức hóa lab. Giữ hai TASK lịch sử, ghi F2 chưa sửa; không nhận provenance intent nhất quán/consent/grant sản phẩm. Điều này không xóa bằng chứng quan sát được về dispatch/Read/findings, nhưng không cho tích hợp theo chuỗi authority đó.
- **Giới hạn:** CLI2.1.81, observed `claude-sonnet-5-5`, effort chưa quan sát. B2 telemetry0.75837945 USD so yêu cầu0.75, vượt0.00837945; result `error_max_budget_usd` dù exit0/`is_error=false`. Lũy kế2attempt=1.52532435 USD telemetry, không hóa đơn/hard cap. Process inventory sau lượt trong request rỗng chỉ là quan sát local, không stop proof từ xa. Không RESULT/checkpoint, phép tính, grant sản phẩm, host khác, chất lượng nghề V2 hoặc tác động toàn máy. Không retire lab/native hoặc dọn D:\c.

**Kết luận:** B2 nhận WITH_LIMITS ở method proof và delta đã xem; V1 tổng thể vẫn PARTIAL, chưa V2/integration/release. Không mở một lượt AI hoặc phiếu mới chỉ để sửa quote/nhãn lab; phần intent/grant và workflow tích hợp thật vẫn phải có căn cứ riêng, không lấy report/candidate lab thay thế.
