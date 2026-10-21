# Contract điều phối — thiết kế ngữ nghĩa G-00

File này giữ ngữ nghĩa. Biểu diễn cấu trúc ở `control.schema.json` (G-01 đã
review nhận ngày 17/10/2026); G-02 mới triển khai checker. Không có grant hay approval thật ở đây.

## Owner và giá trị tin cậy

| Đối tượng | Owner/nguồn cần có | Điều không được suy |
|---|---|---|
| Ý định và điều kiện user | Yêu cầu/decision user đã chốt, có locator/revision | Main ghi một bản tóm tắt không tự chứng minh user đã chốt bản đó |
| Grant/override | User hoặc issuer được user ủy quyền, trong giới hạn được cấp | Reviewer PASS hoặc file profile Main ghi không tạo grant |
| Task proposal | Main, gắn với ý định/grant và nguồn liên quan | Task tự đặt risk thấp không bỏ trigger thao tác thực |
| Review | Actor và phạm vi review quan sát được, verdict gắn binding | Role label/receipt JSON tự khai không chứng minh actor độc lập |
| Tác động thực tế | Điểm thực thi host/tool/OS đã tích hợp | Log Main tự ghi không chứng minh các đường bypass đã bị chặn |
| Terminal disposition | Tổng hợp kết quả bắt buộc, artifact và review còn hiệu lực | Main/Worker không tự chọn DONE khi còn blocked/failed/unknown bắt buộc |

Trong profile có cưỡng chế, issuer, policy và receipt có quyền mở tác động phải
ở ngoài quyền Main tự sửa/tạo. Cơ chế bảo vệ cụ thể thuộc G-03, chưa chọn một
loại token/chữ ký/daemon. Hash chỉ chứng minh liên kết bytes với expected value,
không chứng minh người cấp quyền hoặc tính đúng của ý định. Profile/policy/log
cùng quyền filesystem của Main chỉ được đánh giá ở mức hợp tác ADVISORY.

Trong profile có cưỡng chế, điểm nhận phải lấy căn cứ intent/điều kiện user đã
chốt và tính đủ điều kiện reviewer từ nguồn/receipt tin cậy mà Main không tự
tạo hoặc thay thế được. Grant theo nhóm có thể đáp ứng nguồn quyền này, không
yêu cầu user duyệt lại từng task đúng grant. Diễn giải của Main vẫn phải nằm
trong ý định/điều kiện đó; approval/review ràng buộc digest của intent và accepted
task/context, không chỉ các hash Main tự khai đồng nhất. Actor eligibility/
độc lập phải theo policy và observation phù hợp, không suy từ field reviewer_name
do Main ghi. Chưa có nguồn tin cậy/cơ chế cần thiết thì giữ UNVERIFIED/ADVISORY
và chặn tác động cần mức bảo vệ đó, không tự sinh receipt.

## Task/result dùng chung

Khi cần hồ sơ riêng, giữ tại working/<work-id>/ theo owner A-11 hiện có; một
record cấu trúc có thể sinh bản đọc cho người dùng, không duy trì hai SOT độc lập.
Việc đọc/nháp đơn giản không bắt tạo hồ sơ mới. Grant/effect receipt của công cụ
tham chiếu task revision hoặc operation binding tương đương, không dùng lược đồ
riêng cho từng vai/provider.

Task proposal tối thiểu có:

- Identity: work/task ID, revision và schema version, actor đề xuất.
- Intent: locator/revision/hash của yêu cầu/điều kiện đã chốt, acceptance và phần
  chưa xác nhận; không lưu toàn bộ dữ liệu nhạy cảm trong receipt.
- Authority: grant/issuer reference, subject, scope, action/tool/provider được
  phép, giới hạn/expiry nếu áp dụng; thiếu quyền không được tự điền mặc định mở.
- Inputs: SourceID/path, revision/digest và phạm vi context thực sự liên quan.
- Effects: thao tác, vùng đọc/ghi, protected targets, nguồn cần giữ, điều kiện
  từ chối/phục hồi, output dự kiến. Operation lúc chạy phải đối chiếu proposal;
  không dùng declaration Main làm bằng chứng thao tác thực tế.
- Acceptance: requirement ID → artifact/bằng chứng dự kiến, điều phải bảo toàn,
  review bắt buộc và trường hợp không đạt. Định nghĩa tiêu chí trước implementation.
- Envelope: role/model/effort hiệu lực, fallback, thời hạn, retry/concurrency/cost
  bounds được cấp; unsupported/unknown được giữ nguyên, không giả là applied.

Result tối thiểu có task/input binding đã dùng, artifact/digest thực, hành vi
thực hiện, evidence locator và phạm vi, requirement disposition và phần thiếu.
Worker không chọn terminal status thay điểm nhận kết quả có kiểm soát.

## Review ở hai điểm

**Trước giao/thực hiện khi risk trigger yêu cầu:** nhận task và căn cứ user;
kiểm task đủ, đúng quyền, bất biến, khả thi với tool/host và đường nhận kết quả.
**Trước tích hợp khi policy yêu cầu:** nhận task đã thống nhất, artifact/evidence
thực và input hiện hành; kiểm nội dung, preservation, revision và phần còn thiếu.

Mỗi verdict có binding/phạm vi, reviewer identity và mức độc lập quan sát được,
finding, điều kiện sửa/đạt và trạng thái PASS/BLOCKED/CHANGES_REQUIRED/UNKNOWN.
Chưa có actor độc lập khi task yêu cầu thì không thể dùng self-review để mở tác
động đó. Review không cấp quyền ngoài grant và không thay user acceptance.

Binding liên quan đổi thì cần kiểm lại phần bị ảnh hưởng. Không bắt review lại
toàn bộ nguồn hoặc lặp bằng chứng còn hiệu lực; phải chỉ ra phần đổi và phép
kiểm cần thiết. Main không loại finding bất lợi khỏi tập kết quả bắt buộc.

## Điều kiện trước tác động

Điểm thực thi phải xác định operation và actor thực rồi kiểm: policy version,
grant còn hợp lệ và đúng issuer/subject; task/context/artifact binding; phạm vi
path/tool/action; review bắt buộc; điều kiện preservation và envelope còn lại.

- Chỉ ALLOW sau khi mọi điều kiện bắt buộc có bằng chứng phù hợp.
- DENY cho quyền sai/hết hiệu lực, binding lệch hoặc hậu quả đã biết không an toàn.
- BLOCKED/UNSUPPORTED khi thiếu quyền, reviewer, integration hoặc observation
  cần thiết. Không diễn giải unknown thành allow; phần không phụ thuộc vẫn làm được.
- Log kết quả ngắn và tối thiểu: binding, operation, grant/policy/review reference,
  mức kiểm soát, disposition, actual outcome/artifact. Không chép bí mật/nội dung
  nguồn. Log dưới quyền Main không thành receipt issuer được tin cậy.

Một checker chỉ được gọi từ Main không tự tạo điểm thực thi. G-03 phải đo các
đường bỏ checker/ghi thẳng và xác định tác động nào thực sự không thể vượt.

## Biểu diễn G-01

`control.schema.json` (JSON Schema Draft 2020-12, `schema_version`
`law.cvf.control/1`) là một SOT cấu trúc cho task, grant, review, effect, result,
bundle và routing policy; `$defs` dùng chung binding, trusted_ref, action,
envelope, requirement. Version khác bị từ chối, không diễn giải.

- **Nguồn tin cậy:** intent, grant, reviewer eligibility, recipe acceptance và
  user acceptance là `trusted_ref` có `trust_anchor` và `verification`. Đó là
  lời khai trong record. `MAIN_DECLARED`/`MAIN_WRITABLE_FILE`/`UNKNOWN` không bao
  giờ đáp ứng hàng cần nguồn tin cậy; `VERIFIED` do Main ghi không thay kết quả
  của verifier ngoài quyền Main (G-02/G-03).
- **Binding:** task revision, digest intent, accepted task, context, input,
  output, action và policy version. Review/effect/result tham chiếu binding;
  lệch phần nào thì receipt cho phần đó hết hiệu lực.
- **Ràng buộc cấu trúc:** review PRE_EFFECT phải nêu intent ref đã đối chiếu;
  PASS cần ít nhất một đối tượng; worker/scout/reviewer chỉ đặt CANDIDATE;
  ACCEPTED_FOR_INTEGRATION cần mọi requirement bắt buộc MET; USER_ACCEPTED cần
  `user_acceptance_ref`; grant ví dụ chỉ được `EXAMPLE_INACTIVE`; enum đóng.
- **Recipe:** `recipe_ref` ghi version đã nhận và `user_decision_effect`
  (NONE/CHANGES/UNKNOWN) theo acceptance record. Chỉ NONE cùng version đã nhận
  mới vào route recipe; CHANGES cần review đủ hai pha; UNKNOWN bị chặn.
- **Delegation:** `subject` của grant là người giữ quyền; `delegate_callees` là
  vai được phép gọi. Vai được gọi là `callee_role` (core scout/worker/reviewer,
  hoặc registered/domain_accepted kèm `identity_ref` kind `role_acceptance`),
  không dùng nhãn actor như user/main/issuer. Lời gọi phải mang task cha/con có
  binding, phạm vi tool và envelope yêu cầu; so sánh phạm vi con với grant và
  task cha thuộc checker G-02/G-03.
  Ba trường `tool_scope.tools`/`operations`/`paths` luôn bắt buộc; mảng rỗng
  nghĩa là không cấp quyền ở chiều đó, không phải wildcard. Vai chỉ xử lý
  context đã truyền có cả ba mảng rỗng; quyền Main gọi vai qua công cụ native
  không truyền thành quyền dùng công cụ của vai con. G-02 phải chặn mọi yêu
  cầu vượt scope rỗng; không suy quyền từ việc descriptor hợp lệ cấu trúc.
- **Dữ kiện thao tác:** gửi ra ngoài/network write phải có payload (locator +
  digest); thao tác khác delegate phải có đích. Record hợp lệ cấu trúc nhưng vẫn
  thiếu dữ kiện checker cần thì bị chặn (`OPERATION_DESCRIPTOR_INCOMPLETE`).
- **Không suy:** schema hợp lệ chưa có nghĩa có quyền, review độc lập, host chặn
  được hay nội dung đúng. Verdict chặn, binding lệch và nguồn không tin cậy là
  việc của checker/điểm nhận, có kỳ vọng trong `examples/EXPECTED.json`.
- **Ai lập record:** Main và công cụ lập record, metadata và mặc định kiểm soát.
  User chốt mục tiêu, nguồn, phạm vi sửa và đích nhận bằng ngôn ngữ công việc;
  user không phải viết JSON, chọn trust_anchor/VERIFIED, tự phân loại rủi ro
  hay vá brief kỹ thuật. Quyền thật vẫn phải được công cụ/host xác minh, không
  suy từ lời khai của Main.
- **Version:** giữ `law.cvf.control/1` và `law.cvf.routing/1` cho bản sửa sau
  review G-01 vì version 1 chưa được nhận và ngoài ví dụ chưa có record nào;
  sau khi nhận, mọi thay đổi không tương thích phải tăng version.

## Nhận kết quả và trạng thái

Điểm nhận kiểm input hiện hành, actual output/digest, scope, toàn bộ requirement
bắt buộc và verdict liên quan. Thiếu/failed/blocked/unknown bắt buộc ngăn trạng
thái ACCEPTED_FOR_INTEGRATION; output đổi sau review không dùng verdict cũ.

REVIEW_PASSED, ACCEPTED_FOR_INTEGRATION, EFFECT_APPLIED và USER_ACCEPTED là các
ý nghĩa khác nhau, không dùng một chữ DONE cho cả bốn. Công cụ có thể xác nhận
điều kiện cấu trúc/binding mà chưa xác nhận được semantic correctness; khi đó
giữ verdict nội dung và mức assurance đúng phạm vi.

Timeout/retry/late-result phải reconcile operation ID và trạng thái tác động;
không phát lệnh lặp chỉ vì chưa thấy kết quả. Grant mở rộng/ngoại lệ phải có
owner được phép cấp, không tự phát sinh từ việc user copy prompt hay đưa nguồn.
