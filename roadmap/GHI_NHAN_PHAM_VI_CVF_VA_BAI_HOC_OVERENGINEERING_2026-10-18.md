# Ghi nhận phạm vi .cvf và bài học overthinking/overengineering

Ngày: 18/10/2026.
Trạng thái: **RECORDED_PENDING_SCOPE_REVIEW** — ghi nhớ để xử lý, chưa thay acceptance, policy hoặc roadmap.
Phạm vi: LAW; các bài học có khả năng chuyển về CVF cha sau đối chiếu.

Đây là hồ sơ nhận định/quyết định theo từng mốc; trạng thái implementation hiện hành xem STATE và checklist mục6.2 của ROADMAP_HOAN_THIEN, không suy từ nhận định lịch sử bên dưới.

## 1. Bài học operator nhấn mạnh

> Tuy đã có roadmap chi tiết, nhưng khi triển khai code, vẫn vướng phải việc overthinking/overengineering quá mức cần thiết.

Roadmap chi tiết chưa đủ ngăn phạm vi và độ phức tạp tăng trong lúc triển khai.
Mỗi tranche có thể hợp lý xét riêng, nhưng tổng các tranche có thể vượt nhu cầu sản phẩm.
Review correctness cần đi cùng câu hỏi: chức năng/kiểm soát đang xây có thực sự cần cho người dùng này không?

Main chịu trách nhiệm giữ mức đầu tư tương xứng với mục tiêu và rủi ro; không chuyển toàn bộ chi phí
brief/acceptance chưa rõ thành yêu cầu Worker sửa tiếp hoặc cơ chế tổng quát mới.
Chưa có căn cứ từ các vòng sửa này để kết luận model Worker yếu hoặc nâng model sẽ giải quyết gốc vấn đề.

## 2. Bối cảnh và nhận định cần giữ

- Mục tiêu ban đầu LAW: soạn văn bản; mở rộng sang lưu trữ, tra cứu và công việc văn phòng liên quan.
- User thường có thể đọc, sửa và quyết định sử dụng đầu ra. Mức tự động hóa và hậu quả khác với agent tự thay đổi hệ thống code.
- Vẫn cần bảo vệ những lỗi khó thấy: nguồn/trích dẫn thiếu căn cứ, số liệu sai, ghi đè bản gốc,
  mất đặc tính workbook và tự nâng trạng thái xác minh/quyền.
- Operator đã nhận workflow hợp tác, assurance toàn host ADVISORY. Chưa có yêu cầu mặc định
  chống Main có toàn quyền OS cố ý đi vòng mọi công cụ.
- Trong quá trình triển khai roadmap, phạm vi .cvf đã mở rộng sang schema/version/binding,
  occurrence, veto/coverage nhiều pha và proof lịch sử. S3 hiện vẫn là thiết kế candidate,
  chưa có evaluator v3 hoặc activation; không mô tả đây là tính năng đã vận hành.

**Nhận định Main:** có dấu hiệu đầu tư quá mức cho LAW hiện tại. Cần đánh giá lại sự cần thiết
của từng nhóm kiểm soát trước khi mở rộng implementation; không dùng độ chi tiết của roadmap làm bằng chứng đủ về giá trị sản phẩm.
Đây là đánh giá kiến trúc, chưa phải kết quả đo chi phí hoặc thử nghiệm người dùng.

## 3. Ba việc cần xử lý sau ghi nhận

### A. Thu gọn phạm vi phù hợp LAW

Đối chiếu từng nhóm kiểm soát với công việc thực, hậu quả, khả năng user kiểm tra và phương án đơn giản hơn.
Phân biệt phần cần ngay, phần chỉ cần ở thao tác rủi ro cao và phần hoãn tới khi có nhu cầu thật.

Hướng Main đề xuất để đánh giá:

- Đọc/soạn/sửa nháp trong phạm vi đã giao: luồng gọn, user duyệt đầu ra.
- Kiểm soát nguồn, bảo vệ bản gốc và an toàn writer: giữ tại owner trực tiếp.
- Brief đủ và review theo rủi ro, có kiểm việc Main giao; không mặc định đủ mọi vai cho mọi việc.
- State/runtime có giao thức cập nhật thường xuyên, không mặc định gọi Reviewer mỗi lần ghi STATE.
- Chứng minh một luồng dùng thật từ yêu cầu tới bàn giao trước khi mở rộng thành engine tổng quát.

Đầu ra cần có: quyết định phạm vi/acceptance được nhận và danh sách giữ/hoãn cho roadmap.
Không tự bỏ gate hiện hành hoặc dùng chữ “nhẹ” để mở thao tác chưa an toàn.

### B. Xem xét khả năng tái sử dụng nhiều domain

Lõi quy tắc/checker có thể dùng chung; profile nghiệp vụ, adapter host và dữ liệu cá nhân cần tách rõ.
Khả năng tái sử dụng không tự biện minh cho việc xây đầy đủ ngay.
Ưu tiên cơ chế đã dùng được trong LAW; kiểm ở một domain tương tự rồi mới quyết định tách thành bộ khung chung.
Chưa tạo repo/package mới hoặc công bố đây là framework đa domain đã được chứng minh.

### C. Chuẩn bị bài học cho CVF cha

Ứng viên cần đối chiếu với owner CVF hiện có:

1. Roadmap chi tiết vẫn cần kiểm sự cần thiết và chi phí phát sinh trong lúc thực hiện.
2. Quản trị phải theo hậu quả, khả năng đảo ngược và khả năng user kiểm tra đầu ra.
3. Đánh giá chất lượng brief/acceptance và orchestration cùng với chất lượng Worker.
4. Chốt ý nghĩa nghiệp vụ trước schema; tách record consistency, bytes hiện tại và proof thao tác/lịch sử.
5. Ưu tiên sửa tại owner gây lỗi; cân nhắc nhu cầu lặp lại trước khi thêm abstraction/quy tắc/checker.

CVF đã có tiêu chuẩn quản trị theo rủi ro; cần kiểm khoảng cách áp dụng, không khẳng định nguyên tắc này còn thiếu.
Đây mới là candidate learning. Chưa chuyển file, tiếp nhận, sửa rule hoặc chạy checker ở CVF cha.
Không mặc định giải quyết overengineering bằng cách thêm một tầng quản trị mới.

## 4. Đánh giá độc lập về phạm vi

Ngày 18/10/2026, Reviewer độc lập Sol 6.1 High được giao đọc ghi nhận này, đề xuất phạm vi LAW, PROJECT,
STATE và phần Bước tiếp theo trong HANDOFF. Review chỉ đánh giá phạm vi; không sửa file, code, test,
acceptance hoặc gate.

**Kết luận:** Hướng assurance ADVISORY và phân tầng theo rủi ro phù hợp, nhưng baseline trong đề xuất hiện tại
vẫn nặng về cơ chế quản trị trước khi chứng minh một luồng văn phòng dùng thật. Các thành phần như checker task,
binding artifact/revision, metadata quyền, giữ verdict, onboarding, orchestration nhiều vai và support matrix
đa host có thể vượt nhu cầu trước mắt. Nên bắt đầu từ hành vi người dùng nhìn thấy: làm nháp trong yêu cầu,
nêu nguồn và phần chưa xác minh, giữ nguyên bản gốc, hỏi khi thiếu quyết định quan trọng, và báo rõ việc đã làm/chưa kiểm.

**Ranh giới cần giữ:** x14 và race của writer vẫn mở. Chưa cho luồng ghi workbook thành công cho tới khi writer
từ chối known-loss x14 trước transaction và giới hạn tuyên bố về race đúng theo bằng chứng. Đây là an toàn tại
owner ghi dữ liệu, áp dụng cả tác vụ văn phòng thông thường; đọc và soạn nháp độc lập vẫn có thể tiếp tục.
Không dùng đánh giá phạm vi này để mở đường vòng hoặc thay gate hiện hành.

**Chỉ tăng kiểm soát theo hậu quả:** đối chiếu nguồn và review độc lập cho nội dung pháp lý, tài chính, an toàn,
trình ký/gửi ngoài; xác nhận rõ trước gửi ngoài, đổi quyền/nguồn tin cậy, hoặc ghi/xóa hàng loạt hay khó đảo ngược.
Không bắt đủ ba vai hoặc nhiều pha review cho nháp thường và tác vụ đọc nếu routing hiện hành không yêu cầu.

**Nên hoãn:** occurrence/retry/duplicate semantics; dependency graph hoặc veto tinh; coverage/proof lịch sử nhiều
pha phổ quát; checker tổng quát cho mọi task; orchestration nhiều vai đầy đủ; onboarding/metadata đa host.
Các phần này có thể cần khi có tự động hóa nhiều action hoặc tích hợp host cụ thể, nhưng chưa cần để bàn giao
bản nháp cho người dùng duyệt. Packet S3-D0 Rev 3 vẫn `DESIGN_PENDING_MAIN_REVIEW`; review phạm vi này không
mở A0/code và không đổi acceptance.

**Tái sử dụng và bài học CVF:** ưu tiên tái dùng nguyên tắc/owner nhỏ như provenance, bảo vệ bản gốc, writer từ
chối an toàn và kiểm đầu ra theo yêu cầu. Giữ riêng policy nghiệp vụ, nguồn, dữ liệu cá nhân và phê duyệt.
Chỉ tách capability chung sau khi nhu cầu lặp lại được chứng minh trong LAW và một domain tương tự. Với CVF cha,
đây là candidate learning để retrospective xem xét nhu cầu/chi phí tổng thể và orchestration cùng correctness,
ưu tiên sửa tại owner gây lỗi, không sinh abstraction/checker từ từng finding. Chưa có căn cứ thêm schema, rule
hay gate mới; không chuyển bài học hoặc sửa CVF cha trong lượt này.

Reviewer đề xuất dùng một lát cắt thực tế làm mốc: soạn nháp từ nguồn được chỉ định, giữ nguyên nguồn, nêu trích dẫn/
điểm chưa chắc và bàn giao kèm khai báo thực hiện. Đây là khuyến nghị, chưa phải quyết định phạm vi hay kết quả
thử nghiệm người dùng. Reviewer chưa kiểm runtime, thử nghiệm người dùng mới hoặc writer ngoài bằng chứng đã ghi
trong STATE/HANDOFF.

## 5. Bổ sung từ phản hồi Claude về S3-D0 Rev 3

Operator cung cấp các điểm còn thiếu định nghĩa và phần chưa kiểm từ phản hồi Claude. Đây là thông tin thiết kế
được báo lại, chưa được Main kiểm chứng độc lập trong lượt này; không phải bằng chứng implementation hay căn cứ
để đổi trạng thái packet.

- **R-1:** V-3 mới cần Main xác nhận trước schema. Giữ trạng thái chờ; không mở schema hoặc A0 khi chưa có xác nhận.
- **R-7:** Chưa rõ owner/biểu diễn của proof lịch sử precondition và liên kết `E_req`↔`E_out`. Theo phản hồi,
  thao tác ghi chưa có căn cứ accept PASS và phải là `UNSUPPORTED`/BLOCKED; S4 read-only không giải quyết được
  phần ghi. Nếu phạm vi LAW cần accept thao tác ghi, phải định nghĩa owner/phạm vi proof trước khi tuyên bố hỗ trợ.
  Điểm này độc lập với blocker bảo toàn dữ liệu x14/race: giải proof không làm writer an toàn, và ngược lại.
- **R-8:** Chưa có mô hình dependency giữa action; veto `TASK_WIDE` có thể chặn rộng hơn cần thiết. Đây là vấn đề
  về phạm vi tác động, nhưng chưa tự biện minh cho dependency engine tổng quát nếu luồng dùng thật chưa cần nhiều action.
- **Chưa kiểm theo phản hồi:** chuẩn hóa path của checker v1; tính `context_digest` khi thiếu `context_refs`;
  xử lý `coverage` mới trong `COVER` của S2; quan sát file trên Windows và Python 3.8. Ma trận 40 ca là kỳ vọng
  thiết kế chưa chạy, không phải kết quả kiểm.

**Quyết định Main sau khi audit mục tiêu và routing:** có, tạo file nháp mới theo yêu cầu rõ của người dùng thuộc
baseline sản phẩm. PROJECT hướng dẫn tạo file khi user yêu cầu; routing hiện hành xếp `create_new` ở `working/`/
`output/` trong `R-READ_DRAFT`, không yêu cầu Reviewer cho từng nháp. Phạm vi này chỉ gồm đầu ra mới: không ghi đè
nguồn hay file đã tồn tại; target đang tồn tại thì dừng để người dùng chọn cách tiếp tục. Đây là quyết định sản phẩm,
không phải tuyên bố capability đã nghiệm thu.

**Điều kiện kỹ thuật giữ nguyên:** R-7 chưa có owner/proof cho precondition và liên kết `E_req`↔`E_out`; vì vậy
accept thao tác ghi tiếp tục `UNSUPPORTED`/BLOCKED. Không hạ gate để biến yêu cầu sản phẩm thành khả năng hiện có.
x14/race của writer workbook vẫn là blocker riêng; không lấy proof của file mới thay bảo toàn workbook. Giữ thiết kế
R-7 hẹp theo `create_new` cho đầu ra yêu cầu, và không thêm full binding/reconcile/dependency engine nếu use case
không cần.

### Review độc lập Rev 3 và disposition Main

Ngày 18/10/2026, Reviewer Sol 6.1 High xác minh hash Rev 3 có prefix `ee3731bed01c93d1` và review tĩnh packet
cùng các nguồn liên quan. Kết luận: D1–D4 nhất quán ở mức thiết kế, đủ cho Main quyết định disposition thiết kế;
chưa đủ căn cứ mở A0, chốt schema hay bắt đầu evaluator.

- Main xác nhận V-3 ở mức thiết kế: mọi non-PASS veto dùng fallback `TASK_WIDE`; không suy độc lập từ target rời.
  Đây là lựa chọn bảo thủ có thể chặn rộng; không phải nhận schema hay thay acceptance.
- R-2: giữ các phân biệt thiết kế D1–D4 để tránh lẫn occurrence, coverage và staged/actual; hoãn full binding/
  reconcile nhiều record cho tới khi workflow nhiều action/pha chứng minh nhu cầu.
- R-3/D4: xem user acceptance gắn task/revision/requirements/artifact là ứng viên cho workflow có accept hoặc
  tích hợp tự động; chưa đưa thành capability bắt buộc cho nháp người dùng trực tiếp xem/sửa.
- R-7 vẫn chặn accept PASS cho ghi; R-8 giữ fallback `TASK_WIDE`, hoãn dependency model. x14/race/ex19 vẫn là
  blocker riêng, không được coi là đã giải khi R-7 có thiết kế.
- Đọc và soạn trong hội thoại vẫn khả thi; lưu nháp thành file là nhu cầu baseline khi người dùng yêu cầu, nhưng
  chưa có đường đến accept PASS. Main đã chốt phạm vi hẹp `create_new`; chưa đổi acceptance để cho phép thao tác.

Review không chạy test/checker/probe, không kiểm runtime hay thử nghiệm người dùng. Các mục path v1, context
digest khi thiếu refs, `COVER`/coverage, Windows, Python 3.8 và ma trận 40 ca vẫn chưa kiểm. Packet chuyển sang
`MAIN_REVIEWED_SCOPE_DECISION_PENDING`; chưa schema/implementation.

### Đánh giá độc lập R-7 và disposition Main

Ngày 18/10/2026, Reviewer Sol 6.1 High được giao phản biện thiết kế hẹp cho `create_new` trong `working/` và
`output/`, không sửa file, code hay test. Kết luận: `Transaction` hiện tại có thể là ứng viên owner cho thao tác
publish vật lý, nhưng chưa phải owner proof cho R-7 và không đủ để đóng R-7.

- No-clobber là điều kiện cần: transaction hiện kiểm tra đích rồi dùng `os.replace`, nên file xuất hiện trong
  khoảng race vẫn có thể bị thay thế. Tuy nhiên, chỉ thêm no-clobber chưa giải quyết request/action↔effect,
  crash giữa publish và ghi journal, hay xác minh nguồn gốc output sau phục hồi.
- Journal hiện không gắn task/revision/action occurrence với effect; chỉ giữ 20 giao dịch đã hoàn tất gần nhất,
  và dùng `transaction-v1`. Mở rộng nó kéo theo quyết định schema, tương thích giao dịch cũ và thời hạn lưu bằng
  chứng. Reviewer cũng chỉ ra giới hạn path/parent race theo OS; không được mô tả là race-free.
- Routing `R-READ_DRAFT` không yêu cầu hồ sơ task riêng cho mỗi nháp. Bắt buộc tạo record/receipt cho từng lần
  lưu có thể làm nặng baseline văn phòng. Kiểm bytes hiện tại ở S4 không chứng minh file được tạo bởi đúng request.

**Chọn của Main:** giữ nhu cầu sản phẩm `create_new` khi user yêu cầu, nhưng tiếp tục BLOCKED/UNSUPPORTED ở
accept; không triển khai receipt engine, không mở A0/schema/code, không đổi gate. `Transaction` chỉ được ghi nhận
là ứng viên owner publish, chưa là owner proof. Chỉ xem lại R-7 nếu một workflow thực tế cần accept thao tác ghi
và có giao thức hẹp giải quyết no-clobber, request/effect linkage, crash/conflict, vòng đời evidence và giới hạn
OS/path. Nếu các điểm đó đòi thêm schema/lifecycle lớn, hoãn thay đổi thay vì biến thành hạ tầng mặc định.
R-8 vẫn hoãn dependency model với fallback `TASK_WIDE`; x14/race workbook vẫn là blocker riêng. Phạm vi được
dùng chung giữa domain hiện dừng ở nguyên tắc (giữ nguồn, provenance, từ chối ghi không an toàn); chưa có căn cứ
tạo abstraction/framework đa domain.

## 6. Điểm tiếp tục và nguồn đối chiếu

**Bổ sung review I3 (18/10):** đúng hash ở workspace chưa đủ bảo đảm package dùng được. Git clean filter và ZIP có thể đổi CRLF thành LF, làm owner raw-byte pin không còn khớp; MANIFEST chuẩn hóa EOL vẫn có thể báo khớp. Chọn sửa hữu hạn ở đường vận chuyển bytes (attributes đúng file và ZIP giữ bytes machine/owner), giữ nguyên pin/protocol đã nhận, không thêm abstraction hoặc đổi nghĩa proof. Review cũng phải kiểm nguồn bootstrap thực sự được chạy khi adopt và tính nhất quán source/manifest, bên cạnh từng schema. Đây là bài học orchestration về kiểm trọn luồng phân phối; chưa chuyển thành quy tắc hoặc sửa CVF cha, chưa chứng minh luồng Office thật.

**Bổ sung pilot native và Office (18/10):** hai chu kỳ CLI thật giữ cùng task/rid trong từng chu kỳ đã đạt dispatch/effect, publish được và accept bị chặn đúng vì chưa có người dùng duyệt artifact. Không tạo lời duyệt giả từ quyền “tiếp tục”; cũng không coi BLOCKED có căn cứ là lỗi cần thêm cơ chế. DOCX hợp lệ đã mở/hiển thị đúng trong Word, nhưng focus của công cụ chưa đủ để sửa/lưu có kiểm chứng: ghi đúng giới hạn công cụ, không tự suy là lỗi LAW hoặc tạo adapter mới. Review phát hiện prose contract còn trạng thái cũ trái phần đã triển khai; sửa ngay tại tài liệu hiện có và gắn bằng chứng với đúng RC, không thêm checker quản lý trạng thái. Bài học là kiểm hành trình, tính nhất quán tài liệu và chất lượng bằng chứng cùng correctness của code; chưa chuyển bài học sang CVF cha.

**Bổ sung review Word COM (18/10):** đã nhận sửa/lưu/đọc lại đúng7đoạn theo bằng chứng hợp tác, giữ đầu vào; không nâng thành quan sát UI hoặc audit vòng đời instance khi thiếu command transcript. Khác11pt ở đoạn mới không chặn brief chỉ yêu cầu nội dung (bản gốc có5đoạn12pt và tiêuđề18pt); publish bổ sung không trở thành tiêu chí bắt buộc sau khi làm. Định nghĩa rõ điểm dừng và giữ giới hạn bằng chứng giúp tránh thêm vòng sửa, gate hoặc infrastructure không phục vụ yêu cầu. Chưa D4/user approval hoặc chuyển bài học sang CVF cha.

**Bổ sung scope audit điểm kết thúc (18/10):** mỗi ô chưa kiểm phải được đặt đúng lớp candidate kỹ thuật, tác vụ nghiệm thu, hỗ trợ hoặc phát hành. M-3 đã chọn một ca D4 dương nên vẫn cần user duyệt đúng artifact; quyền “tiếp tục” không thay được. M-1/R7 không bắt mọi host cùng đạt, nên CI/actual3.8/branding/freshcheckout không tự biến thành việc bắt buộc mới trước candidate hẹp. Release vẫn giữ Gitclean/CI theo RELEASING; không đổi các gate đó bằng cách gọi archive lab là bản đã phát hành. Orchestrator phải chốt một bước còn lại cụ thể, không lặp lại cả bộ kiểm hoặc mở thêm framework để lấp mọi unknown.

**Mốc đánh giá độc lập sau C/D,18/10/2026:** C/D được nhận BINDING_ROUTING_ONLY sau sửa trực tiếp unknown/union, path và known-loss priority; vẫn CANDIDATE_NOT_ACTIVE, chưa gate/observer/PASS hoặc đóng R-7/G. Bước tiếp được ghi trong STATE/HANDOFF và roadmap: đóng nợ canonical screening theo đúng projection trước gate/workflow PASS. Mục này ghi bài học tại mốc review, không thay bảng tiến độ hiện hành; các nhận định chưa code/owner ở phần trước là lịch sử thiết kế.

**Bài học mới để đề xuất đối chiếu CVF cha (chưa chuyển sang cha):** đánh dấu một kiểm soát NOT_EVALUATED không cho phép logic bên dưới coi điều kiện đó là False. C/D từng ghi ENVELOPE chưa kiểm nhưng gán F, làm mất hàng và nghĩa vụ R-EXTERNAL; sửa đúng là giữ Unknown cùng hợp nghĩa vụ chắc chắn/có thể áp dụng, không thêm checker hay abstraction khác. Known-loss không được bị nhánh unsupported che; review cần so cả code và schema thực — preservation có target, khác tiền đề trong bàn giao. Đây là lỗi orchestration giữa các phần, dù từng phần có test xanh; không suy đã hoàn tất workflow từ số test hoặc nhãn coverage.

**Bài học kiểm chứng thêm:** 11 proof Windows/NTFS về primitive và bộ test Worker xanh chưa đủ chứng minh toàn vòng đời ghi/khôi phục/dọn an toàn. Review cần theo tác động thật tới ranh giới nguồn và từng mutation. Các lỗi đã tìm được sửa bằng guard/Pins và xóa qua handle tại owner hiện có, không thêm schema/rule/checker để vá lỗi writer. Lỗi nhỏ rõ nguyên nhân thì Reviewer tự sửa+kiểm ngay; không trả Worker thêm vòng chỉ vì sai diagnostic. Chỉ chuyển A0 khi corrective đã review đạt; không mở lại khảo sát kiến trúc hoặc suy đã hoàn tất `.cvf` từ số test/proof.

**Bài học orchestration ở S3-B0:** tái dùng không đồng nghĩa phải mở kernel/config tổng quát. Các helper v2 đang gắn owner/literal v2; chọn copy-forward foundation v3 để giữ phạm vi sửa và hồi quy hữu hạn, nhưng phải tính cả chi phí mã trùng. Nợ này do Orchestrator/S3-G và G-04 sở hữu: trước release chọn một runtime version hiệu lực, loại v2 candidate runtime chưa activated khỏi package v3 và kiểm package thực. Không gọi nợ đã giải nếu vẫn ship cả hai; chưa xóa v2 trong S3-B, không copy engine v1 hoặc biến test helper thành sản phẩm. Đây là lựa chọn cụ thể của tranche, không quy tắc dùng chung mặc định cho mọi domain.

**Bài học mới từ audit workflow P-CN1 (18/10):** test dispatch → effect → publish → accept xanh vẫn có thể chạy trên hai task khác nhau; phải so cùng task_id/revision và đủ digest intent/context/accepted_task/action qua snapshot thực, không dựng task mới để làm accept xanh. Orchestrator phải kiểm capability của writer với task đã duyệt, cùng toàn bộ đường dẫn thật sự bị tác động: T2 tạo thư mục publish còn kéo theo hai bootstrap parents chưa được grant prefix phủ. Remedy caller rid và precondition parents có sẵn/pin tại owner hiện có đã thi công và review nhận trong luồng hẹp, không thêm schema/framework hoặc mở rộng grant. Audit dependency bootstrap cũng tìm thấy init/transaction đã tạo runtime; probe project giả đạt. Cần kiểm cơ chế sẵn có và hành trình trước khi đề xuất helper mới; chưa suy từ probe init rằng G-04 đã hoàn tất. Đây là bài học đề xuất đối chiếu CVF cha, chưa chuyển sang cha.

- Căn cứ chính: trao đổi operator/Main ngày 18/10/2026, đặc biệt yêu cầu ghi riêng bài học overthinking/overengineering.
- Mục tiêu sản phẩm: `../PROJECT.md`.
- Phạm vi đã nhận: `DE_XUAT_PHAM_VI_KIEM_SOAT_LAW_2026-10-18.md`.
- Kế hoạch và lịch sử triển khai: `ROADMAP_HOAN_THIEN.md`, `../.agent/HANDOFF.md`.
- Thiết kế đang chờ review: `G02_C2_S3_D0_AMENDMENT_PACKET_2026-10-18.md` và các review D0/R2.
- Phản hồi Claude về R-1/R-7/R-8 do operator cung cấp; R-7 đã được Main đối chiếu độc lập với transaction owner và routing, phần còn lại chưa kiểm chứng độc lập.
- Owner CVF đã đối chiếu một phần: `docs/reference/CVF_TASK_PROPORTIONAL_GOVERNANCE_ROUTING_STANDARD_2026-08-17.md`
  trong repo CVF cha; đường này là tham chiếu bảo trì, không là dependency vận hành của LAW.

**Bổ sung sau nghiệm thu lab và review I-02 rev1 (18/10):** user đã duyệt đúng bản6ee4cef2/đủ2requirement; accept PASS/ADVISORY và Reviewer nhận D4 trong phạm vi một file. G-03 baseline hợp tác hẹp/G-04 tích hợp candidate đã có điểm dừng; official release vẫn chờ Gitclean/CI/RELEASING. I-02 cho tiếp A–D theo dependency vì A-06/D-02 chính là điều kiện của release; bắt release trước mọi A–D sẽ tạo vòng phụ thuộc. Bài học orchestration mới: ghi rõ mốc kết thúc kỹ thuật, nghiệm thu tác vụ và phát hành ngay trong dependency; giữ gate đúng owner thay vì lặp thêm pilot hoặc dựng checker để giải một vướng mắc về thứ tự. Không đổi acceptance, không đóng writer/R2/x14, không chuyển bài học sang CVF cha.

**Bổ sung audit A-10 (19/10):** contract/checks Reviewer hiện chứa ngoại lệ cho Reviewer bảo trì được sửa lỗi nhỏ; nhúng nguyên văn vào native Reviewer sản phẩm sẽ mang sai quyền. Thiết kế được review chọn bỏ ngoại lệ khỏi contract sản phẩm, giữ quyền bảo trì ở AGENTS/PROJECT/roadmap; chưa sửa code/contract trong lượt audit này. Sửa tại owner nội dung, không tạo parser lọc heading hoặc tầng quyền mới. Đồng thời chốt một brief gộp phần adapter còn lại, effort chưa hỗ trợ thì công bố UNSUPPORTED/null; không biến mỗi role/unknown thành packet hoặc đưa stop/timeout/task-result của A-11/B-03 vào receipt A-10. Đây là bài học có thể đề xuất đối chiếu CVF cha về tách vai phát triển với vai sản phẩm và giữ đúng owner của việc còn thiếu; chưa chuyển hoặc sửa cha.

**Bổ sung audit độc lập A-11 (19/10):** Reviewer Sol6.1 High nhận thiết kế docs+probe trên owner hiện hữu, chưa nhận implementation/T29/T30. Bundle cũ tự nhất quán không chứng minh yêu cầu user hiện hành: phải so RESULT với current TASK do Main quản lý. Tuy nhiên không cần dựng task engine/helper mới chỉ để chặn yêu cầu đổi; raw TASK/RESULT/candidate và source/context/snapshot sổ đã dùng có thể đưa vào inputs của task publish P-CN1 riêng, tận dụng guard bytes trước ghi và accept hiện hữu. `work_id` chung chưa đủ mapping; hash candidate trong inputs cũng chưa chứng minh staged bytes chính là candidate đã review — phải đọc/so hash rồi dùng đúng bytes đó. Đây là hai nối kết orchestration giữa owner cần chứng minh bằng probe, thay vì thêm schema/checker. Task/source checkpoint vẫn hợp tác, không grant hoặc native enforcement; một writer giữ ở library/P-CTX/P-CN1, full R5/gián đoạn và lineage giữ tranche B. Chưa chạy probe mới hoặc chuyển bài học sang CVF cha.

**Sau review thi công A-11 (19/10):** đã nhận WITH_LIMITS sau3finding nhỏ và25test sourcecuối đạt/0skip (21probe+4projection). Mẫu code nằm trong docs vẫn có chi phí kiểm code: `link_free` không phải containment và prefix slot không chặn `..`; metadata trong `context_refs` cũng cần qua sổ; `read_book` không tự guard link. Sửa tại recipe bằng primitive owner hiện có và probe chạy đúng code docs, không thêm checker/path engine hoặc đổi writer. “Không helper mới” không có nghĩa sample miễn review. Giữ mẫu hữu hạn Worker1candidate, công bố Scout delta/nhiều task/live orchestration chưa kiểm thay vì mở generic engine để lấp mọi unknown. Đây là bài học orchestration và chi phí tổng thể, chưa chuyển CVF cha.

**Audit B-01 (19/10):** scope write+lookup trong một sheet workbook và source-event explicit đã được Sol6.1 High review có điều kiện, chưa thi công/T17–T21. Không thể bỏ thao tác version hóa semantic chỉ để bớt code: bytes giữ nguyên vẫn có thể có thông tin thay thế/trạng thái mới. Chọn LAW revision là basis version, SHA riêng; history ObservedBefore không giả metadata của prior revision sau user sửa Excel. Cắt chi phí ở register/graph/UI/auto migration, dùng một writer và view tính trạng thái thay vì ghi đè bằng chứng/user decision. Idempotence chỉ chứng minh yêu cầu cũ đã ghi, không cấp phép dùng căn cứ hiện tại; query không đọc source phải nói bytes UNOBSERVED, tách basis/superseded/file-state. Đây là các nối kết ngữ nghĩa cần chốt trước code, không finding nào tự sinh framework. Chưa chuyển CVF cha.

**Sau review B-01 (19/10):** đã nhận WITH_LIMITS sau4sửa nhỏ/21content+15regression sourcecuối đạt. Lỗi cần sửa ở owner: query căn cứ không được dùng cache formula che thay đổi literal; header5cột chưa đủ nhận history legacy; từng đường ghi phải kiểm cả managed content/history; event retry chỉ dùng lịch sử nhất quán với canonical payload/identity/revision. Giữ1commit helper nội bộ hữu hạn thay vì refactor chỉ vì có callable. Main còn kiểm nối API source-event→A-11: revision tăng, bytes giữ nhưng checkpoint và publish request cũ vẫn bị chặn đúng. Đây là kiểm orchestration giữa owner, không thêm rule/schema/checker hoặc gọi lại AI. Evidence chỉ fixture/API/CLI, không toànR3 hay xác minh pháp lý; chưa chuyển CVF cha.

**Audit B-02 (19/10):** Reviewer Sol6.1 High nhận scope có điều kiện, chưa code/test/nghiệm thu. Khả năng mở/chọn Nháp hiện tại đã có owner; thêm lineage phải dùng chung sổ/writer, không sinh con trỏ hoặc receipt thứ hai. Cắt nhánh late historical registration: nguồn/sổ đổi sau publish thì giữ file và báo chưa đăng ký, không dựng cơ chế chứng minh lại lịch sử. Mở bản cũ và dùng làm input mới có yêu cầu khác nhau: bản đúng bytes vẫn được xem khi nguồn stale; consumer mới phải kiểm closure hữu hạn. Historical basis khác catalog là trạng thái cần xem lại, không phải sổ malformed làm writer không thể tăng revision. Tài liệu không khai căn cứ vẫn có thể dùng với nhãn unknown/giới hạn giữ xuyên downstream, không giả verified hoặc xóa basis đã biết để vượt kiểm. Một module theo chức năng và hai sheet trực tiếp đủ cho tranche; chưa cần graph engine/cache/ContentID hoặc packet riêng cho UI. Đây là lựa chọn thiết kế cần kiểm bằng implementation, không bằng chứng LAW đã có chức năng; chưa chuyển CVF cha.

**Sau review B-02 (19/10):** đã nhận WITH_LIMITS sau5sửa P2 tại owner hiện có, không thêm engine/gate. Copy một aggregate state chưa đủ chuyển căn cứ sang agent/phiên khác: phải giữ ID/revision/hash/semantic basis, kind/limits và unknown xuyên chuỗi. Một nhánh có nguồn rõ không làm tổ tiên chưa rõ thành CURRENT. Binding output cũng cần identity owner ở lần recheck cuối khi contract đã nhận identity, không chỉ bằng bytes. Mọi phép kiểm có thể từ chối thao tác mở phải xong trước opener; báo lỗi sau side effect là kết quả sai dù parser đúng. Test xanh Worker không thay các nối kết này; dùng probe có mục tiêu và sửa nhỏ trực tiếp, không gọi lại AI. Nợ path trong docs được xác minh bằng baseline/projection và sửa prose tại chỗ, không sửa checker hoặc hạ release gate. Bằng chứng34test/7UI trước sửa cuối,9target sau sửa cuối và3nợ docs đạt giữ riêng thời điểm, không cộng thành fullsuite. Module1222dòng có chi phí thật nhưng vẫn một chức năng/sổ/writer; chưa cần refactor chỉ vì dài. Chưa toànR3/R5/Office/release hoặc chuyển CVF cha.
