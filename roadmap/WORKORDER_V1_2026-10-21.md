# Work order V1 revision 1 — ĐÃ THU HỒI

**Ngày giao cũ:** 21/10/2026. **Trạng thái hiện hành:** `WITHDRAWN_WRONG_PRODUCT_SCOPE`; không giao Claude thi công.  
**Lý do thu hồi:** operator xác nhận mục tiêu là văn phòng trung tâm. Work order này đã đưa lựa chọn nguồn thành tranche đầu khi chưa thiết kế đủ Main điều phối, bộ chuyên môn, tool/preset và cách vận hành công việc. Roadmap revision 2 thay cách chia cũ; phần dưới chỉ giữ lịch sử, không còn là chỉ thị triển khai. Chỉ tái dùng chi tiết scope khi work order mới ánh xạ đúng nghiệp vụ và quyền.

---

**Hồ sơ giao cũ — không còn hiệu lực:**

**Owner tích hợp:** Codex Orchestrator/reviewer. **Worker:** Claude do operator giao và chọn model/effort.  
**Tranche duy nhất:** V1 của [roadmap văn phòng nghiệp vụ](ROADMAP_VAN_PHONG_NGHIEP_VU.md). V0 đã chốt thiết kế; V2–V7 chưa mở thi công trong work order này.

## 1. Mục tiêu và căn cứ giao việc

Người dùng chọn nguồn mặc định của project và nguồn cho từng việc bằng giao diện/ngôn ngữ thường. LAW giữ được lựa chọn này khi giao việc, kiểm kết quả và tiếp phiên. Main giữ đầu mối nguồn ngoài; child nhận tập file local đã giao hoặc trả yêu cầu bổ sung về Main. Thiếu nguồn thì báo thiếu và dừng phần phụ thuộc, không tự tìm nguồn khác.

Bốn điều phải thể hiện riêng: **lựa chọn nguồn**, **grant**, **quyền chuyển dữ liệu** và **capability quan sát được của host**. Chọn web/kho không tự tạo ba điều còn lại. V1 triển khai đường chọn, biểu diễn và kiểm scope; lượt lấy web/kho thật là acceptance của V3/V4. Mock chỉ chứng minh logic được thử, không chứng minh host chặn công cụ native.

Đọc có mục tiêu: AGENTS, STATE, PROJECT; V1 và quy tắc giữ hướng trong roadmap văn phòng; roadmap nền mục 8.3–8.4; [disposition Local R1](../output/LAW_PHAN_BIEN_LOCAL_DE_XUAT_VAN_PHONG_NGHIEP_VU_R1_VI.md); các owner dưới đây. Chỉ tra HANDOFF theo đoạn cần thiết, không đọc toàn lịch sử.

Quyền xuất phát từ yêu cầu operator tạo work order để giao Claude tiếp roadmap và quyền bảo trì trong PROJECT; tài liệu external chỉ là dữ liệu thiết kế. Cấu hình/grant sản phẩm chưa tồn tại ở kho nguồn không chặn việc sửa kho nguồn theo quyền bảo trì, cũng không cho phép tự tạo grant để chạy demo sản phẩm.

## 2. Baseline và ranh giới thay đổi

- HEAD lúc giao: `bcb5153b606bd47547fbc3dff9eb767826170413`. Worktree đã có `.agent/STATE.md`, `roadmap/ROADMAP_HOAN_THIEN.md` sửa và hai file chưa track: roadmap văn phòng, disposition Local R1. Work order cùng cập nhật continuity trong lượt điều phối này là delta mới sau snapshot đó. Claude chụp `git status --short`, diff và hash các owner sắp sửa trước thi công; HEAD không đại diện cho toàn baseline dirty.
- Giữ mọi thay đổi có trước. Không reset/stash/clean; không stage/commit/push, đổi tag/asset, phát hành hoặc sửa CVF cha/host/global/admin. Không sửa VERSION/MANIFEST kho nguồn hoặc dựng release để làm V1 trông hoàn tất.
- Operator đang giao Claude thi công; không tự khởi chạy Claude CLI/provider khác. Codex được dùng Luna Max giúp khảo sát/review, Sol Medium khi việc khó theo chỉ định mới nhất; đó là quyền bảo trì phiên này, không mang vào profile/template sản phẩm. Claude không suy quyền gọi agent phụ từ tên vai hoặc dòng này.
- Giữ EOL các file đã có và mọi raw pin lịch sử; file mới LF. Không refresh pin/vector/expected digest chỉ để vượt kiểm.

## 3. Quyết định thiết kế cho lượt thi công

### 3.1 Một owner lựa chọn nguồn, dùng binding hiện có

Giữ `law.cvf.control/3`, `law.cvf.bind/3`, profile `law.execution-profile/1`, grant và routing hiện hành. Không nhét field mới vào TASK/profile strict hoặc diễn giải prose thành grant. TASK đã có `inputs` và `context_refs`; recipe trong `roles/README.md` đã kiểm bytes, revision và nguồn trước tích hợp. Tái dùng các đường này.

`object_digest.scope` là qualifier của object, `library.read_scope` mô tả phần đã đọc; cả hai không phải ACL hay lựa chọn nguồn. TASK v3 cũ thiếu descriptor vẫn đọc theo đường local hợp tác hiện hành, không tự thêm quyền web/kho và không được gắn bằng chứng V1 mới. Khi giao mới theo V1 phải có descriptor và context đầy đủ; không tự sửa TASK/RESULT lịch sử. Kiểm riêng cả đường tương thích này lẫn đường V1 thiếu context phải bị từ chối.

Thêm descriptor nhỏ có version cho **lựa chọn nguồn**, không thêm workflow/state machine/sổ nguồn mới. Mặc định project đặt trong một khối đánh dấu rõ của `PROJECT.md`; phần chọn cho một task đặt trong `working/<work-id>/<task-id>/source-selection.json`, chỉ Main ghi. Module owner có thể là `tools/source_selection.py`, chứa parser/validator/resolver dùng chung bởi UI/CLI và checkpoint, không chứa downloader hoặc credential store. Ghi grammar, field và ý nghĩa version ngay tại owner/hướng dẫn; không rải parser theo ngôn ngữ VI/EN.

- Project mô tả loại nguồn được chọn: LAW, web công khai, kho chỉ định hoặc kết hợp; locator phạm vi phải đủ cụ thể để so sánh. LAW dùng thư viện hiện hành và ngoại lệ đã chỉ định, không đồng nghĩa mọi file trên máy. Web/kho dùng locator công khai/định danh tài liệu hoặc folder đã chọn; không lưu account/session/token hoặc dò toàn tài khoản.
- Task khai lựa chọn hẹp hơn hoặc bằng project và các input thực tế được giao. Resolver tính tập hiệu lực; không tin cờ `effective`/`allowed` do client hoặc child tự khai. Không hợp tập để nới scope. Thiếu locator thì báo thiếu, không coi wildcard/ngôn ngữ tự nhiên mơ hồ là toàn web/toàn kho.
- Project cũ chưa có khối mới: đọc ở chế độ `LEGACY_LOCAL_ONLY`, **chỉ-LAW, chưa có nguồn ngoài được chọn**; không tự sửa PROJECT hoặc tạo block/grant khi đọc hay nâng cấp. New project dùng template có mặc định LAW-only; không sao lựa chọn của maintainer. Chỉ hành động lưu lựa chọn rõ ràng của user mới thêm/đổi block trong project đang dùng. Không suy nguồn ngoài từ trường prose “Nguồn / mẫu chính đã duyệt”. Đã có block nhưng sai, trùng, version lạ hoặc field chưa hỗ trợ thì từ chối rõ; không rơi về mặc định để che lỗi.
- Phân biệt task không ghi lựa chọn riêng (kế thừa mặc định được giải quyết và chụp lại khi giao) với task chủ động chọn tập rỗng (báo thiếu nguồn). Mặc định project rộng không làm một việc LAW-only được gọi web/kho. Yêu cầu vượt mặc định cần lựa chọn mới rõ ràng của user, không được tự nới project.
- Bind bytes descriptor task và `PROJECT.md` hiện hành qua `TASK.context_refs`; input local giữ path/SourceID/revision/hash theo owner thư viện. Project dùng làm context quản lý thì không tự gán SourceID của thư viện. Đổi lựa chọn phải tăng `task_revision` trước nhận kết quả; checkpoint cũng phải từ chối khi descriptor/PROJECT đổi mà người ghi quên tăng revision. Cách invalidation bảo thủ theo toàn bytes PROJECT được chấp nhận và phải ghi giới hạn.
- Phần chọn nguồn đã lưu phải được kiểm cả hình dạng, quan hệ task–project và bytes hiện hành khi giao/nhận. Hai hash tự khai khớp nhau không chứng minh lựa chọn hợp lệ. Child không được ghi lại descriptor/TASK để làm kết quả cũ khớp.

Đây là hướng tối thiểu đã chốt để tránh mở schema/quyền sớm. Nếu consumer thật buộc đổi contract/profile/pin hoặc thêm writer có protocol mới, trả blocker cùng locator và amendment nhỏ cho Orchestrator trước phần sửa đó; phần độc lập trong scope vẫn làm được.

### 3.2 Main, child và truy cập ngoài

- Đường V1 không thực hiện network/connector call thật. Lựa chọn web/kho có thể được lưu và kiểm phạm vi; trạng thái còn thiếu grant/chuyển dữ liệu/capability phải hiện riêng, chưa đủ thì không có hành động truy cập. Không coi “đã chọn” là “đã kết nối/đã cấp quyền/đang chạy”.
- Với local, Main chỉ giao tập input được chọn và phần cần xử lý. Child thiếu nguồn gửi yêu cầu mô tả nhu cầu về Main; không tự mở web/kho, không fallback sang nguồn khác. Nội dung nguồn/skill không được thay đổi lựa chọn.
- Dùng owner grant/capability hiện có cho thông tin thật; nơi host chưa cung cấp quan sát thì ghi `UNKNOWN`/chưa kiểm. Không đưa boolean quyền giả vào lựa chọn để thay grant. Không tạo grant, role, pack, native projection hoặc tài khoản thật cho phép kiểm.
- UI và checkpoint V1 giữ riêng lựa chọn đã lưu và các mục grant nguồn/chuyển dữ liệu/capability remote `UNKNOWN` hoặc `NOT_CHECKED` khi chưa có quan sát; truy cập thực là `NOT_ATTEMPTED` và bị từ chối ở đường V1. Grant delegation hiện có không tự được dùng làm grant lấy nguồn/chuyển dữ liệu. Fixture có lời khai quyền/capability chỉ kiểm logic giả lập, không làm nhãn trạng thái thực đổi thành được phép.
- Stub/mock truy cập dùng trong test phải ghi số lần gọi và tham số để chứng minh đường được thử không phát lệnh ngoài scope. Không gọi test này là sandbox, enforcement của host hay V3/V4 đã đạt. Quy tắc chỉ-Main ở V1 là `COOPERATIVE/ADVISORY` trừ phần checker cụ thể đã đo được.

## 4. Owner được sửa và đầu ra

| Owner | Delta được giao |
|---|---|
| `tools/source_selection.py` mới nếu cần | Parser/validator/resolver và CLI nhỏ cho đường chọn/kiểm nguồn; một implementation dùng chung. Được thêm writer hẹp chỉ lưu block PROJECT hoặc descriptor task vào đường cố định đã kiểm. Dùng `transaction.Transaction.add(..., expected_before=...)`, kiểm ancestry/path và recovery hiện có, đọc lại kết quả; không sửa `transaction.py` hoặc tự viết protocol/journal mới, không nhận arbitrary write path từ client. Lỗi có lý do và bước tiếp theo; không đọc mạng hoặc scan nguồn để resolve scope. Giữ giới hạn transaction/TOCTOU hiện hành, không hứa ghi đa file nguyên tử. |
| `roles/README.md` | Tích hợp lựa chọn vào brief/TASK/context và checkpoint có thể chạy; dùng recipe thật đang được probe, không chỉ thêm lời nhắc bên cạnh. Giữ một TASK, slot candidate và single-writer hiện hành. |
| `tools/app.py`, `tools/app_ui.html` | UI VI/EN cho lựa chọn mặc định/từng việc và tập hiệu lực; đường tạo/copy brief hiện có phải dùng resolver chung. Server kiểm payload, scope và stale; không chỉ checkbox phía client. Nếu chỉ tạo prompt thì ghi rõ chưa giao/chưa chạy. Ghi PROJECT/descriptor phải có preview và so preimage trước ghi qua owner hiện có; lỗi không để file ghi dở. Không refactor các trang/route khác. |
| `AGENTS.md`, `en/AGENTS.md`; mẫu PROJECT VI/EN và `release_templates/PROJECT.md`, `release_templates/en/PROJECT.md` | Hướng dẫn lựa chọn và trách nhiệm Main/child, mẫu mặc định an toàn, cùng chức năng VI/EN. Giữ các dòng quyền bảo trì riêng ở PROJECT nguồn; không đưa chúng vào template. Không thay giá trị project thật để diễn tập UI. |
| `tools/init_project.py` và owner tạo project liên quan | Chỉ sửa nếu đường khởi tạo thật cần hiểu block mới; giữ lựa chọn đã có, không overwrite prose hoặc profile. Không mở cơ chế upgrade/grant mới. |
| `tools/README.md`, guide VI/EN có đường chọn nguồn thật | Hướng dẫn ngắn và giới hạn đã kiểm; HTML chỉ dựng bằng generator hiện có cho các trang có nguồn đổi. |
| Tests hiện hành và `tests/test_source_selection.py` mới | Fixture giả/tempfile; unit resolver + probe checkpoint thật + HTTP/browser/lifecycle theo ma trận dưới. Không dùng dữ liệu người dùng, grant hoặc nguồn ngoài thật. |
| `.agent/STATE.md`, `.agent/HANDOFF.md` | Bàn giao tiến độ, bằng chứng và giới hạn; không tự đánh dấu V1 đạt trong roadmap. |

Không mở pack/vai chuyên môn, engine Office/OCR, daemon, runtime multi-agent, connector tự viết, sổ/memory/database mới hoặc V2 báo cáo HTML. Không sửa writer đã pin (`publish_new.py`, `context_update.py`), `.cvf/contracts`, `.cvf/checks`, routing hoặc schema profile. Writer hẹp mới nêu trên là consumer của transaction hiện hành, không thay protocol đã pin. Nếu không thể bảo toàn bằng API hiện có thì báo blocker; không ghi trực tiếp từ app để lách.

## 5. Acceptance hữu hạn

| Mã | Điều phải chứng minh trên dữ liệu giả |
|---|---|
| V1-A | Project LAW-only và task LAW-only: resolver/brief chỉ chứa nguồn local đã chọn; spy web/kho đều **0 lần gọi**. Thiếu file/nguồn báo thiếu, không tự thay bằng nguồn khác. |
| V1-B | Fixture project default đã chứa web/kho cần thử; mỗi task chọn web, kho hoặc kết hợp với locator cụ thể trong default: giữ đúng tập, yêu cầu ngoài tập bị từ chối trước điểm gọi stub. Không tự tìm kiếm toàn web/kho. Trạng thái grant, chuyển dữ liệu và capability thiếu/UNKNOWN không bị đổi thành được phép. Test stub không phải live proof; truy cập thực V1 vẫn NOT_ATTEMPTED. |
| V1-C | Project cho LAW+web+kho, task chỉ LAW hoặc subset locator: tập hẹp được giữ trong resolver, UI/brief và checkpoint; task rỗng không thành kế thừa, task rộng hơn bị từ chối. Child yêu cầu thêm nguồn trở về Main, không làm scope tự nới. |
| V1-D | Một TASK/RESULT đang khớp và một candidate có bytes thật. Đổi descriptor task, đổi mặc định PROJECT hoặc nguồn local: checkpoint từ chối bản cũ, kể cả cố giữ revision/hash khai báo cũ. Giao lại tăng revision/slot đúng cách thì bản mới đi tiếp; không sửa RESULT cũ để ghép. Mở process mới vẫn kiểm cùng lựa chọn từ đĩa. |
| V1-E | Version lạ, field lạ, block trùng, JSON lỗi/khóa trùng, locator thiếu/sai scope, path thoát project hoặc link/junction bị từ chối trước đọc/ghi ngoài vùng. Project cũ thiếu block chỉ tương thích LAW-only, giữ nguyên bytes; không diễn giải prose thành nguồn ngoài/quyền. |
| V1-F | Một HTTP flow thật qua harness và một browser flow có chọn nguồn → xem tập hiệu lực → tạo/copy brief. Chưa xác nhận lưu thì không ghi; stale preimage bị từ chối; nhãn VI/EN không tuyên grant, host invocation hoặc kết nối từ lựa chọn/prompt. Đối chiếu request do client sửa, không chỉ click happy path. |
| V1-G | New project VI/EN không nhận nguồn/account refs/grant của maintainer hoặc project A. Một bản sao project cũ có PROJECT riêng, nguồn, profile/grant fixture và kết quả: upgrade qua owner thật giữ raw bytes phần riêng, không tự thêm grant/source ngoài. Sau upgrade resolver đọc đúng trạng thái cũ/mới; không rebaseline để giấu conflict. Schema/field chưa hỗ trợ không được hiểu như hợp lệ. |

V1 đủ khi cả các hàng áp dụng đạt và review độc lập nhận đúng source/delta. Chưa có browser hoặc môi trường lifecycle thì giữ `PARTIAL`/`IMPLEMENTED_PENDING_REVIEW` cùng phần chưa kiểm, không tự bỏ điều kiện. V1 không cần live web/kho/Worker/Reviewer mới; những bằng chứng đó giữ ở đúng V2–V4. Không lấy test RC2 làm test V1, không cộng các nhóm trùng thành fullsuite.

## 6. Kiểm, review và điểm dừng

Trước sửa, xem `git diff` đúng owner và `python -B tools/build_guides_html.py --check`. Có drift ngoài phạm vi thì ghi nhận, không dựng lại hàng loạt. Chụp hash/preimage vào HANDOFF, không lập thêm baseline/report riêng.

Chạy module scope mới và các target thực sự chạm trong `tests/test_task_result_flow.py` (đặc biệt checkpoint, stale, reopen), `tests/test_panel.py`, `tests/test_ui_browser.py`, `tests/test_execution_profile.py`, `tests/test_upgrade_lifecycle.py` hoặc `tests/test_package_v3.py`. Chọn test theo delta thực, ghi tên đầy đủ, pass/skip/reason và thời gian có đo. Không mặc định chạy toàn các module trên, fullsuite/fullgate/release hoặc cài thêm tool. Target mới phải lái resolver/checkpoint/HTTP/upgrade thật, không tự cài checkpoint giả trong test để làm oracle.

Sau sửa chạy `python -B tools/check_package.py --release`, `python -B tools/build_guides_html.py --check`, `git diff --check -- <file-chạm>` và `python -B tools/check_package.py --check-eol <file-chạm>`. Nếu Markdown đổi cần HTML, dựng bằng generator rồi xác nhận chỉ output tương ứng đổi. Package check không cho phép tự đổi manifest/pin/gate; báo lỗi có owner. Khi sửa lỗi cụ thể chỉ kiểm lại phần bị ảnh hưởng; lỗi công cụ thử lại tối đa một lần rồi báo giới hạn.

Claude tự đọc diff cuối và đối chiếu từng hàng acceptance. Bàn giao **`IMPLEMENTED_PENDING_REVIEW — V1_SOURCE_SELECTION`**, gồm baseline/delta, model-effort yêu cầu và quan sát được, grammar/version lựa chọn, các đường đã tích hợp, lệnh/kết quả thật, file bảo toàn, phần mock/hợp tác/chưa kiểm và blocker. Không nhận thay operator; không tự đóng V1 hoặc chuyển thi công V2.

Codex nhận diff và evidence rồi review ranh giới scope, tương thích/upgrade, dữ liệu ghi và claim UI theo mục 8.3. Review này chưa diễn ra ở lúc giao work order. Độc lập với Claude; nếu Codex đã sửa implementation thì phần rủi ro đó cần reviewer độc lập. Chỉ sau verdict phù hợp mới cập nhật trạng thái V1; mốc tiếp theo duy nhất là V2 khi dependency/grant/host của V2 đủ.
