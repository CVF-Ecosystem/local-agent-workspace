# Kiểm soát điều phối LAW / LAW orchestration controls

Trạng thái G-00: **DESIGN_REVIEWED_NOT_IMPLEMENTED** — 17/10/2026.
G-01: **REVIEW_ACCEPTED_SCHEMA_ROUTING** — 17/10/2026. Ba P2 đã resolved,
kể cả scope rỗng=không cấp quyền. Đủ điều kiện bắt đầu G-02 checker local.
G-02: **REVIEW_ACCEPTED** trong phạm vi schema/routing/record consistency (17/10).
Bản cuối code f95bfc367bb7f470 có107 test G-02 đạt; Reviewer độc lập nhận delta cuối.
G-03 enforcement cũ: **NOT_ACHIEVED / hoãn theo quyết định phạm vi operator18/10**; không ghi PASS.
Operator đã nhận mặc định workflow hợp tác có kiểm tra/review bắt buộc, assurance toàn host ADVISORY.
G-03 baseline mới: **IMPLEMENTATION_PENDING**; chưa đổi checker v1 hoặc mở tác động từ chấp thuận phạm vi.
Brief lab2a đã preflight; operator xác nhận running Claude Code2.1.301 từ GUI ngày18/10 (chưa quan sát độc lập).
Worker Sonnet5.5 High, Reviewer Sol6.1 High; lab2a **REVIEWED_PARTIAL**, có trace/bytes thật Main và child.
Malformed exit0/silent/plain và indirect shell vẫn ghi được; T5default/hai lần, auto và effective policy chưa rõ.
Evidence/review ở roadmap/evidence/g03-2a-2026-10-18/ (chỉ kho nguồn). Không đồng nhất quan sát lab với enforcement.
Analyzer không tự VERIFIED, cleanup tắt, giữ lab. Khảo sát2b-00 đã review WITH_LIMITS;
ứng viên U-std/P0 CHANGES_REQUIRED, không chọn làm mặc định. Chưa cài account/helper/global/admin.
G-01-C1: **CONTRACT_CANDIDATE_REVIEW_ACCEPTED** (18/10), candidate contract/routing v2 ở contracts/v2 và rules/v2.
Worker báo24 test đạt; Main sửa hẹp sau review Sol6.1 High,13 test mục tiêu đạt (evidence trong roadmap, chỉ kho nguồn).
G-02-C2/S1: **REVIEW_ACCEPTED_FOUNDATION_ONLY**18/10, entry/loader/canon/router/output đã có; Worker58test snapshot, Main31target đạt sau2sửa hẹp.
S1 đọc/validate owner candidate v2 nhưng chưa evaluator; validstructure vẫn BLOCKED.
G-02-C2/S2: **REVIEW_ACCEPTED_HELPER_ONLY**18/10; thư viện refs/binding trong bộ nhớ, Worker157test snapshot/Main56target đạt sau sửa hẹp.
Helper chưa nối entry/API/output S1, không authority/gate/observer. S3–S5 còn amendment/thiết kế trước code.
EXPECTED v2 ex01/ex02 đã sửa errata BLOCKED vì time/preservation chưa hỗ trợ; không sửa grant hoặc22bundle, không là kết quả workflow.
v1 tại đường gốc giữ nguyên và là owner của checker hiện tại;
candidate v2 chỉ được nền S1 đọc, chưa kích hoạt/đóng gói, chưa có proof workflow.
Phiên bản mới phải giữ trigger/pha review/unknown và knownloss, không auto-migrate legacy hoặc đổi NoVerifier thành VERIFIED.
Owner kế hoạch bảo trì ở roadmap/HANDOFF; chấp thuận phạm vi không là grant cho project người dùng.
Checker so sánh record,
không cấp quyền, chưa có host enforcement; schema hợp lệ chỉ chứng minh cấu trúc.

**Mốc v3,18/10 — REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS:** contract/rules v3 và checker `checks/control_check_v3.py` có workflow cùng task cho một file mới trên Windows NTFS local, ADVISORY; không root vẫn diagnostic. Chi tiết ở `contracts/v3/CONTROL_CONTRACT.md` và `checks/v3/README.md`. Vẫn CANDIDATE_NOT_ACTIVE; chưa integration/G-03/G-04/activation, không tự thay owner v1 đang được hướng dẫn sản phẩm tham chiếu.

Reviewer độc lập Sol 6.1 High đã nhận thiết kế sau sửa hai finding về routing
review và trusted intent/reviewer binding. Chi tiết ở HANDOFF; bắt đầu G-01
không có nghĩa G-02/G-03/G-04 hoặc roadmap cũ đã được nghiệm thu.

## Mục đích

Giữ quyền, điều kiện bảo toàn và bằng chứng của công việc ổn định khi user thay
agent/model. Main cũng là actor chịu kiểm soát. Main được suy luận và tổ chức việc
trong grant; không tự tạo grant, bỏ review bắt buộc hoặc tự hạ acceptance.

## Cây và owner

```text
.cvf/
  README.md
  rules/CONTROL_RULES.md          # quy tắc sản phẩm, áp dụng cả Main
  rules/ROUTING_POLICY.json       # bảng routing canonical (law.cvf.routing/1)
  contracts/CONTROL_CONTRACT.md   # ngữ nghĩa task/grant/review/effect/result
  contracts/control.schema.json   # JSON Schema 2020-12 (law.cvf.control/1)
  contracts/examples/             # dữ liệu giả EXAMPLE + EXPECTED.json
  checks/README.md, control_check.py  # đặc tả + checker chỉ đọc (G-02, chờ review)
  PROVENANCE.md                  # nguồn thích nghi; không là dependency runtime
```

- Bộ khung sở hữu rules/contracts/checks và version của chúng. Chưa đặt quyền OS
  read-only, chưa có bằng chứng Main không sửa được những file này.
- `.agent/EXECUTION_PROFILE.json` vẫn là owner dự kiến cho lựa chọn host/model/
  effort/fallback và quyền project. Không tạo một profile thứ hai trong `.cvf/`.
  File profile cùng quyền ghi với Main chưa phải bằng chứng quyền do user cấp.
- Task/result và artifact khi cần nằm ở `working/<work-id>/`; tham chiếu đúng
  revision, không chép lại nội dung nguồn hoặc toàn bộ hội thoại cho đủ thủ tục.
- Evidence P-CN1 do owner quản lý trong thư mục publish dưới runtime của project;
  không tạo runtime thứ hai trong `.cvf/` hoặc đưa dữ liệu chạy, grant hay review
  của maintainer vào bộ mẫu người dùng. Nhật ký cùng quyền ghi Main chỉ có giá trị tự khai.

## Phân biệt mức bảo đảm

| Trạng thái | Có thể kết luận |
|---|---|
| UNVERIFIED | Chưa đo; không suy có hoặc thiếu khả năng host |
| ADVISORY | Có hướng dẫn/check theo đường hợp tác; chưa ngăn được mọi đường bypass |
| ENFORCED_FOR_NAMED_ACTIONS | Có proof host/tool/OS chặn tác động đã nêu; chỉ áp dụng đúng host/version/action/tool surface đã kiểm |

Không dùng file chỉ dẫn, checksum, agent tự nhận vai, hoặc checker PASS để nâng
mức bảo đảm. Main có file/shell/native tool cùng quyền sửa policy và đích thì
checker tùy chọn không tạo ranh giới cưỡng chế. Điểm cấp quyền và điểm thực thi
phải được bảo vệ khỏi việc Main tự thay/bỏ qua trước khi nhận mức cuối.

## Điểm vào và kế hoạch

Đọc CONTROL_RULES rồi phần contract liên quan khi thiết kế/giao việc có rủi ro.
AGENTS VI/EN và roles/ dẫn tới đây (G-01); không tuyên bố host đã tự nạp cây này.
Hiện chưa kích hoạt adapter hay quyền mới. Cây này chưa được kiểm có trong ZIP
phát hành; đóng gói và loại dữ liệu runtime thuộc G-04.

G-00→G-04 và điều kiện quay lại roadmap cũ nằm trong roadmap hiện hành, mục 6.2.
Thiếu Reviewer hoặc host chưa có quyền cần thiết không tự cho phép Main làm
thay một tác động vốn cần điều kiện đó. Việc đọc/tạo bản nháp trong grant có thể
tiếp tục; không bắt mọi việc gọi đủ ba vai hoặc hỏi lại quyền user đã cấp.

LAW phải dùng độc lập sau phân phối. Chỉ người bảo trì đối chiếu repo CVF qua
PROVENANCE; user không cần repo CVF để hiểu hoặc thực hiện các quy tắc này.
