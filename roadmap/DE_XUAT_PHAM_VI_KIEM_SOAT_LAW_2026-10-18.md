# Đề xuất chốt phạm vi kiểm soát mặc định LAW

Ngày18/10/2026. **OPERATOR_ACCEPTED_SCOPE — IMPLEMENTATION_PENDING**.
Operator trả lời câu hỏi quyết định: “Chấp thuận phạm vi đề xuất (khuyến nghị)”. Đây là chấp thuận mặc định
workflow hợp tác có kiểm tra/review bắt buộc và giới hạn bypass, mở việc amendment có version.
Chưa thay rules/schema/policy/checker v1 hoặc mở tác động. G-03 enforcement cũ chưa đạt, được hoãn theo thay đổi phạm vi;
G-03 baseline hợp tác mới chưa triển khai/nghiệm thu. Không dùng chấp thuận này làm grant của project người dùng.
Reviewer độc lập `review_g03_2a_prep`, Sol6.1 High đã đối chiếu cả9hàng routing/contract; Main sửa2câu
về legacy migration/NoVerifier và PARTIAL theo review. Đây là preflight quyết định, chưa nghiệm thu implementation.

## 1. Quyết định operator đã chốt

**Khuyến nghị:** LAW mặc định vận hành theo **quy trình có kiểm tra và review bắt buộc**, mức bảo đảm ADVISORY
ở cấp toàn host. Các công cụ LAW tự kiểm và từ chối điều kiện không an toàn trong đường xử lý của chúng.
Không yêu cầu account Windows riêng, admin/helper nâng quyền, managed policy toàn máy hoặc VM để dùng mặc định.
Chưa bảo đảm ngăn Main cố ý bỏ qua quy trình qua mọi file/shell/Office/MCP của host.

Thay đổi này thu hẹp rõ acceptance cưỡng chế toàn host đã đặt cho G-03. Operator đã chấp nhận giới hạn đó
ngày18/10, mở việc sửa contract/routing theo version. Không đánh dấu G-03 cũ đạt hoặc dùng evidence2a làm proof mới.

Phương án còn lại: giữ acceptance cưỡng chế đầy đủ; G-03 tiếp tục BLOCKED cho tới khi chọn và chứng minh boundary
phù hợp, có thể phải nhận chi phí hạ tầng/giới hạn công cụ khác. U-std/P0 hiện chưa được chọn cho phương án này.

## 2. LAW mặc định sẽ làm gì

| Kiểm soát | Cách thực hiện đề xuất | Có thể khẳng định sau nghiệm thu | Giới hạn phải công bố |
|---|---|---|---|
| Main giao việc đủ | Mẫu task tự dựng từ yêu cầu user; requirement→nguồn→đầu ra→proof, scope và điều giữ nguyên; checker trước dispatch | Phát hiện các trường/binding/scope thiếu, mâu thuẫn; Worker trả brief lỗi | Trường đủ không chứng minh hiểu đúng toàn bộ ý định |
| Kiểm chính Main | Reviewer nhận cả yêu cầu/điều kiện gốc và task trước tác động khi route yêu cầu, rồi xem kết quả trước tích hợp/giao khi đến pha | Có reviewer khác Worker, verdict/binding và finding được giữ trong luồng đã quan sát | Không có nguồn identity chống giả ngoài Main thì chỉ là bằng chứng quy trình; Main còn khả năng bỏ qua |
| Quyền user theo nhóm | User chọn mục tiêu/nguồn/vùng ghi/đích nhận bằng lời thường; bộ khung ghi nguồn xác nhận, scope/version/expiry nếu có | Không hỏi lại mỗi việc trong grant; ngoài scope dừng và nêu quyết định thiếu | Record cùng quyền Main sửa không là kho quyền chống giả; proposal Main chưa là user confirmation |
| Nhận kết quả | Kiểm artifact thật/revision/requirement→evidence, giữ verdict bất lợi cùng binding, không nhận kết quả trễ/stale | Không báo đạt từ lời Worker hoặc checksum tự khai; thiếu proof ghi chưa kiểm | Nội dung đúng vẫn cần review phù hợp, không bảo đảm model luôn đúng |
| An toàn tại tool LAW | Dùng owner writer hiện có; kiểm path/link/hash/lock/format/recovery; known loss/conflict chặn bắt buộc thì từ chối trước effect. PARTIAL chỉ báo lỗi runtime bất ngờ sau tác động được cấp quyền, không thay từ chối trước effect | Chỉ khẳng định hành vi đúng entrypoint/version/case đã đo | Shell/native tool khác còn có thể bỏ qua owner; không gọi đây là host enforcement |
| Onboarding/tích lũy | Khung tạo metadata/index/record; giữ source ID/revision, personal skill và quyền user qua upgrade | User không viết JSON, chọn trust_anchor, vá prompt hay hiểu ACL | Host/role tích hợp chưa kiểm giữ UNVERIFIED/PENDING; không nhận tự khai là callable |

ADVISORY mô tả mức bảo đảm của cơ chế trước khả năng actor bỏ qua. Quy tắc trong workflow vẫn bắt buộc:
Main không được tự bỏ review, nhận finding bị chặn, mở scope hoặc chọn chế độ nhẹ để vượt điều kiện.
User phải được biết còn giới hạn bypass; không mô tả mô hình mặc định là “đã khóa được Main”.

## 3. Trust assumptions cần đổi, nghĩa vụ cần giữ

**Đề xuất đổi:** mặc định không yêu cầu mọi user grant/reviewer record phải có issuer/store nằm ngoài quyền OS
của Main mới dùng được workflow. Chấp nhận nguồn xác nhận hợp tác của user và bằng chứng vai/phiên được quan sát
với attribution rõ, mà không nâng chúng thành trusted authority/receipt chống giả. Mức này không thay semantic review.

Đây là amendment thật, không phải thêm cờ assume-verified hoặc cho NoVerifier tự trả VERIFIED.
Schema/routing/checker cần version và phân biệt evaluation basis/coverage; policy cũ hoặc mode không hiểu vẫn dừng.
Không lấy verdict BLOCKED hiện tại rồi đổi tên thành “được phép”; cần triển khai và nghiệm thu baseline mới.
Checker consistency/coverage không tự cấp quyền; quyền thực vẫn đến từ user trong phạm vi đã xác nhận.

**Giữ nguyên:** trigger theo thao tác thật, hợp nhiều hàng, phạm vi grant/child, các pha review, binding và veto
cùng binding; grant không có/ngoài scope, reviewer bắt buộc thiếu/BLOCKED, preservation lỗi hoặc classification chưa rõ
đều dừng phần phụ thuộc trong workflow. Phần đọc/nháp độc lập còn đúng grant được tiếp tục.
Không tự điền ý định, không dùng source/personal skill để tạo quyền, không coi Main tự nhận reviewer là độc lập.

## 4. Tác động từng hàng routing — chỉ là đề xuất

| Hàng hiện có | Giữ | Amendment cần thiết nếu operator chọn mặc định đề xuất |
|---|---|---|
| R-READ_DRAFT | Grant hợp tác, scope/tool/envelope; không bắt Reviewer cho mọi nháp | Tool quan sát path thật để phân loại trong luồng; không coi protected_targets Main khai là chứng minh an toàn |
| R-RECIPE | Đúng recipe/version đã nhận, grant, input/preservation/outcome; không tự xin lại trong scope | Ghi nhận acceptance của user theo cơ sở hợp tác; không trusted-verify giả, không allow arbitrary script theo tên recipe |
| R-MUTATION | PRE_EFFECT + PRE_INTEGRATION, grant/binding/current revision/preservation | User confirmation + review có nguồn/attribution theo cơ sở hợp tác; scope mơ hồ và lỗi an toàn vẫn dừng |
| R-AUTHORITY_CHANGE | Hai pha review, skill intake và user nhận mở/sửa quyền; không tự sửa policy của framework | Phân biệt proposal với acceptance; local record không chống sửa. Template/policy amendment của maintainer vẫn review/version riêng |
| R-HIGH_STAKES | PRE_DELIVERY, nguồn/phạm vi kết luận; không nói đã đối chiếu khi chưa có | Review quy trình và căn cứ được ghi rõ mức quan sát; không hứa máy chứng minh chuyên môn/độc lập chống giả |
| R-EXTERNAL | Grant đúng payload/đích/chi phí, hai pha review, actual outcome | Flow xác nhận và bằng chứng gửi/cost có attribution; không gửi khi thiếu quyền hoặc endpoint/chi phí chưa rõ |
| R-DELEGATE | Child trong scope cha/grant, callee/task/context/tool/envelope; không kéo thêm review đệ quy | Cho native role theo quyền user đã xác nhận ở cơ sở hợp tác; ghi requested/observed, không suy model alias thành identity proof |
| R-UNCLASSIFIED | BLOCKED phần tác động, không fallthrough về nháp | Không thay bằng mặc định cho phép; làm rõ operation/scope trước |
| R-KNOWN_LOSS | DENY trước effect | Không đổi; x14 phải chặn ở writer trước transaction, không cho opt-in mất dữ liệu để vượt nghiệm thu |

Mọi thay đổi bảng này cần đồng bộ canonical policy/readable rules/schema/checker/docs theo owner,
không tạo policy thứ hai cho từng provider hoặc bản “nhẹ” để Main tùy chọn khi gặp BLOCKED.

## 5. Người dùng phổ thông trải qua luồng nào

1. User nói việc cần làm, chọn nguồn/vùng ghi/đích nhận; khung tự chuẩn bị metadata và tóm tắt phạm vi.
2. Đọc/nháp trong grant làm ngay; việc ngoài grant hỏi đúng quyết định nghiệp vụ còn thiếu, không hỏi trust fields.
3. Khi policy cần review, Main gửi role đúng nhiệm vụ kèm căn cứ gốc và task. Reviewer phản biện cả brief Main;
   Worker trả thiếu/mâu thuẫn. Lỗi nhỏ rõ trong scope Reviewer sửa ngay, đổi lớn tách owner.
4. Công cụ xử lý artifact/bằng chứng; dữ liệu đổi/định dạng có known loss thì dừng, giữ gốc và báo cách tiếp tục.
5. Main chỉ giao kết quả sau các kiểm đến hạn; thông báo ngắn điều đã làm/chưa kiểm, không ép user điều hành agent.

Nếu host không có Reviewer cần thiết, quota hết hoặc role chưa callable: báo rõ phần phụ thuộc đang chờ,
không fallback thành Main tự duyệt. Chưa chứng minh role integration thì không quảng cáo chức năng đã có.
Chỉ xin lại user khi quyền/mục tiêu chưa có, thay đổi hoặc tác động cần quyết định mới; không xin mỗi tool call.

## 6. Cách triển khai sau quyết định — chưa mở code

1. **Amendment theo owner G-01/G-02:** version/assurance basis/coverage và quy tắc nhận nguồn hợp tác;
   raw bytes/canonical binding/ex19 giải đúng owner, không giả receipt hoặc đổi simulated verifier thành production.
   Legacy default và NoVerifier chưa đổi trước khi amendment được review/kiểm đúng scope.
   Không tự chuyển project/profile/record cũ hoặc thiếu evaluation basis sang mặc định mới; migration cần quy tắc
   được nhận rõ. Receipt cũ không được nâng mức/diễn giải lại; NoVerifier không tự thành VERIFIED/effect_authorized.
   Main không được đổi basis theo từng lần để vượt BLOCKED; baseline mới chỉ áp dụng trong phạm vi đã được nhận.
2. **Tích hợp workflow:** nối task→preflight→role→review→artifact acceptance bằng công cụ/native đã chọn;
   một EXECUTION_PROFILE và runtime governance hiện có. Không SDK orchestration mới, daemon hoặc supervisor agent.
3. **Owner dữ liệu:** sửa A-06 x14 riêng trước capability ghi workbook; xử lý race/retention đúng claim.
   Không tạo writer P0 mới; không tự đóng các blocker dữ liệu theo amendment về trust.
4. **Nghiệm thu + G-04:** proof đúng luồng và phản chứng orchestration, support matrix từng host, UX người mới,
   template sạch, ownership/packaging/dependency. Chỉ khi baseline mới đạt mới xét tiếp roadmap A–D.

Lát/brief code phải có phạm vi hẹp, tiêu chí và phần kiểm trước giao; không gom4owner thành một lượt Worker.
API/CLI đã được operator cho thử trong lab/bản sao/worktree, ghi model/effort/scope/giới hạn và review trước tích hợp.
Không gọi model/test trong bước đề xuất này. Bằng chứng CLI không tự chứng minh VSCode.

## 7. Nghiệm thu đề xuất và điều chưa hứa

- Main giao brief thiếu nguồn/đầu ra/preservation: preflight/Worker trả lại trước tác động trong luồng.
- Main hạ route/bỏ review/verdict/đổi acceptance: checker/review nhận ra theo artifact đã quan sát, giữ BLOCKED.
- Source đổi, artifact khác revision, late result/duplicate effect: phát hiện đúng trong entrypoint tích hợp.
- Grant nhóm đúng và nháp đơn giản: luồng thành công, không hỏi lại hoặc bắt đủ ba vai.
- Writer từ chối x14/link/conflict đúng case; không báo nguyên tử nếu còn hash→replace race.
- Người mới dùng không sửa metadata, tự gọi role hoặc viết prompt kỹ thuật; ghi số lần cần hỗ trợ/overhead.
- Một ca bypass native/shell được giữ như bằng chứng giới hạn ADVISORY, không sửa log để tính đạt enforcement.

Các mục này là tiêu chí chưa chạy, không kết quả PASS. Không hứa chống agent ác ý có toàn quyền OS, bảo mật
trước mọi ứng dụng khác, ngăn mọi sai sót semantic, hoặc hard-cap chi phí chưa có cơ chế đã đo.
ENFORCED_FOR_NAMED_ACTIONS chỉ dùng sau proof boundary tương ứng; proposal không cấp nhãn đó cho native hoặc tool LAW.

## 8. Disposition cần ghi sau quyết định

Nếu operator nhận đề xuất: ghi rõ chấp nhận giới hạn hợp tác/bypass, sửa acceptance G-03 bằng amendment được review,
giữ mục tiêu enforcement cũ như yêu cầu mạnh hơn chưa đạt/hoãn với lý do; không ghi “G-03 enforcement PASS”.
U-std/managed/OS isolation là nghiên cứu hardening tùy chọn, chưa cài hoặc tính vào tính năng mặc định.
Nếu operator giữ acceptance mạnh: giữ G-03 BLOCKED và trình phương án boundary/chi phí cụ thể, không tự mở roadmap cũ.

Nguồn: mục tiêu operator17/10; DESIGN_G03_2B_2026-10-18.md; REVIEW_G03_2B_00_2026-10-18.md;
LIVE_REVIEW.md trong evidence2a; owners contract/rules/checks và roles/README. Đây là đề xuất sản phẩm,
không nghiên cứu thêm host/OS hoặc claim đã đọc mọi tài liệu/kho nguồn.
