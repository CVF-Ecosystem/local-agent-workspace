# Work order V1-A — Nền nghiệp vụ của văn phòng trung tâm

**Ngày:** 21/10/2026. **Trạng thái:** `ACCEPTED_WITH_LIMITS — V1A_OFFICE_FOUNDATION`; review implementation hoàn tất ở phạm vi nền bên dưới, V1 tổng thể vẫn PARTIAL.  
**Trục sản phẩm:** một Main nhận và tổ chức công việc, dùng chuyên môn có phương pháp/công cụ, kiểm và tích hợp, sửa/tiếp việc và dùng lại. Mở nguồn là năng lực hỗ trợ.  
**Thi công:** Claude, operator chọn model/effort. **Điều phối và review:** Codex theo PROJECT và roadmap nền 8.3–8.4; quyền trợ lý phiên này Luna Max, Sol Medium khi khó. Không tự chạy Claude CLI hoặc cấp quyền sản phẩm từ quyền bảo trì.

**Review phiếu giao:** reviewer độc lập `office_architecture_review`, tool dispatch `gpt-6-sol/medium`, nhận `READY_FOR_CLAUDE` sau sửa một blocker marker/context ở mục4.3 và acceptance D. Chỉ nhận kế hoạch/V0 design-only; chưa review implementation hoặc live proof. Cấu hình dispatch không chứng minh suy luận nội bộ hay chi phí.

**Review implementation 21/10/2026:** Codex nhận phần nền sau khi tự xem diff/code/bằng chứng, Sol Medium kiểm helper/guard và Luna Max kiểm hợp đồng/UX/bảo toàn. Reviewer đã sửa hai P2 JSON sai kiểu gây traceback, làm rõ input proposal chỉ bind bytes và Main bổ sung SourceID/revision qua owner thư viện, cùng một lỗi readiness khi thiếu MAIN guide. Các sửa nhỏ có regression đúng phần; không đổi schema/quyền/logic writer. Root chạy 16 target guard/delivery/readonly/legacy đạt/0skip (17.134s) và 5 browser flow đạt/0skip (17.205s); reviewer chạy riêng 3 regression JSON/CLI và 2 status tests đạt. Không cộng với test lịch sử thành fullsuite.

**Giới hạn còn giữ:** chưa live Main→core role đọc phương pháp, chưa chất lượng nghiệp vụ/compute/Office/connector hoặc host enforcement. Package check ngay kho vẫn 1 lỗi/15 cảnh báo vì file disposition điều phối trong output đã có trước V1-A; không xóa/di chuyển file hoặc gọi release gate đạt. Fixture projection/new VI–EN/upgrade của V1-A qua owner thật đạt, không phải nghiệm thu release. Generator 10 trang khớp; hướng dẫn bổ sung metadata nguồn vẫn là nghĩa vụ Main, helper không tự tra sổ. Tiếp theo là proof V1-B trong quyền/host thực có, không đóng V1 hoặc mở V2 sớm.

Phần dưới giữ phạm vi giao gốc làm căn cứ review, không giao lại thi công V1-A.

## 1. Đầu ra được giao

Xây nền để Main của host nhận yêu cầu tự nhiên, nhận diện loại việc, chọn phương pháp nghiệp vụ chuẩn bị sẵn và lập brief đúng nguồn/công cụ/đầu ra cho core role. Chuẩn bị hợp đồng cả bộ chuyên môn; làm sâu thư ký tổng hợp và đối chiếu để bước V2 dùng được. Có công cụ kiểm cấu trúc/soạn brief dùng chung, binding thật với TASK và đường giao việc VI/EN. Người dùng không phải tự chọn agent hoặc viết prompt nghề.

Đây là **V1-A trong V1 revision 2**, không thay toàn bộ acceptance V1. `PREPARED` chỉ có nghĩa đã chuẩn bị giao việc. Thiếu live trace thì V1 vẫn `PARTIAL`, chưa chứng minh chuyên viên đã chạy; phần xác nhận gọi vai thật V1-B phải đủ trước đóng V1. V2 kiểm văn phòng đầu tiên trọn vòng và chất lượng kết quả. Không đổi roadmap để gọi một bộ Markdown/prompt là văn phòng hoạt động.

[Roadmap hiện hành](ROADMAP_VAN_PHONG_NGHIEP_VU.md) và phản hồi trực tiếp của operator giữ mục tiêu. [Work order chọn nguồn cũ](WORKORDER_V1_2026-10-21.md) đã thu hồi, không ghép vào phiếu này.

## 2. Audit hiện trạng và disposition V0

Audit có mục tiêu trên HEAD `bcb5153b606bd47547fbc3dff9eb767826170413` cùng worktree dirty của phiên điều phối. Chưa audit toàn repo/host hoặc coi source cũ là capability hiện hành của mọi môi trường.

| Phát hiện có locator | Dùng lại / khoảng trống / quyết định |
|---|---|
| `roles/README.md:82–124`, recipe `checkpoint`/`binding_stub`/`publish_inputs` | Có TASK hiện hành, slot/candidate, so binding và bytes input/context, single writer. Dùng lại; không thêm task engine, state machine hoặc writer mới. Chuyên môn là phương pháp của task, không phải quyền. |
| `.cvf/contracts/v3/control.schema.json:219–242,765–967`; `.cvf/checks/v3/canon.py:240–269` | `context_refs` bind path/digest bytes được; TASK đóng field. Bind catalog/phương pháp/skill đã dùng qua context hiện có; không thêm key chuyên môn tùy ý vào TASK/profile. `object_digest.scope` không phải ACL. |
| `tools/native_agents.py:35–49,104–148`; `roles/README.md:63–78` | Exporter chỉ ba core role, disk config; Scout/Reviewer Read/Grep/Glob, Worker thêm Write. Không có Python/Office/remote hoặc dispatcher trong adapter này. Method cần đến child bằng brief/context và được đọc, không tự được native nạp từ catalog. |
| `.agent/EXECUTION_PROFILE.schema.json:4–49`; `tools/execution_profile.py:36,220–233,787–795` | Profile /1 giữ requested choices cho ba core role và grants. Kế thừa lựa chọn của core role; không khai preset/model riêng từng chuyên môn đã applied. Không lấy grant delegation làm quyền đọc nguồn/chuyển dữ liệu. |
| `tools/pack.py:34,126–127`; `skills/README.md` phần tiếp nhận | Pack chưa nhận `roles`. Không mở pack hoặc dùng `domain_accepted` để đặt sáu cái tên. Catalog dưới đây là phương pháp nhiệm vụ do package quản lý, không callable identity/skill/recipe đã tiếp nhận. Skill mới thật sự thì theo intake riêng, không lách bằng thư mục roles. |
| `tools/app_ui.html:427–434,697–701,1389–1396`; `tools/app.py:262–286` | Mặt giao việc hiện copy prompt chung và liệt kê file gần đây; chưa có chọn chuyên môn theo công việc hoặc quan sát dispatch. Cần Main guide và đường chuẩn bị yêu cầu cụ thể, nhãn trạng thái trung thực. |
| `tools/check_package.py:149–161,306–339`; `tools/upgrade_package.py` owner ba bên | File roles/tools mới có đường projection chung, không tự thêm vào MANIFEST kho nguồn. Phải thử package thực và giữ tùy chỉnh user; không tự đồng nghĩa catalog đã được native activate. |
| Chỉ mục skill và nội dung `html-reports`, `spreadsheet-check`, `office-documents` | Có tài nguyên nghiệp vụ dùng lại theo nhu cầu. Chưa là bộ sáu chuyên viên. Không sao chép native hoặc tạo skill mới cho đủ bộ; method trỏ tài nguyên hữu ích và khai thiếu tool thật. |

**Quyết định V0 ở mức thiết kế:** specialization layer trên core roles, Main điều phối bằng năng lực native; catalog/phương pháp là context có version; model/quyền đi theo owner hiện hành; chưa mở schema/pack/runtime. Bộ hợp đồng thiết kế ở mục 3 là spec cho implementation. Review thiết kế không nghiệm thu code/native hoặc hứa chức năng V1/V2 đã chạy.

**Kiểm nền đã chạy trong lượt audit:** sáu target độc lập của `tests.test_execution_profile.SchemaAndStatus` (defaults, requested-vs-observed), `tests.test_native_agents.CreateAndUpdate` (preview/status không ghi) và `tests.test_task_result_flow.Flow` (hai slot, task revision, generic context bytes): **6 đạt/0 skip, 0.892s**, Windows/Python của phiên. Tên lệnh đầy đủ ở HANDOFF. Đây chỉ là kiểm lại phần tái dùng, không phải test chuyên môn V1 mới/fullsuite/host.

## 3. Hợp đồng thiết kế của bộ chuyên môn

Mỗi hợp đồng implementation phải có: kích hoạt/không kích hoạt; input; phương pháp; output; capability bắt buộc và tùy chọn; skill/mẫu bổ sung; checks; cách trả phần thiếu/mâu thuẫn; preset policy và giới hạn. Không rút thành một câu “hãy đóng vai”. Giữ song ngữ VI/EN như contract lõi; có thể dùng một file song ngữ để tránh thêm overlay không cần thiết.

| Method ID / base role | Kích hoạt, input và phương pháp | Output / checks / công cụ |
|---|---|---|
| `research-assistant` / scout | Khi cần khảo sát độ đủ/phù hợp của căn cứ; nhận câu hỏi, kỳ, scope và file Main giao. Phân biệt nguồn chính/phụ/trích; kiểm phần đã đọc và điểm thiếu; gom yêu cầu bổ sung có lý do về Main. Không tự truy xuất ngoài. | Source refs, phần đã/chưa đọc, mâu thuẫn và nhu cầu bổ sung. Read/tìm local đủ cho phạm vi tài liệu đọc được; không nhận snippet là toàn văn. Tham chiếu source-library khi đúng việc; không tự ghi sổ. |
| `executive-secretary` / worker | Khi tổng hợp báo cáo/biên bản; nhận kỳ, người đọc, mẫu, source revision, quyết định cần giữ. Phân biệt quyết định/đề xuất/việc chờ; gộp có căn cứ; không bịa owner/deadline. Đổi một câu đơn giản thì Main làm trực tiếp. | Một candidate text/HTML theo assignment, căn cứ trọng yếu, thiếu/mâu thuẫn và phần cần xác nhận. Read/tìm + Write text, HTML offline/escape và đúng kỳ. `html-reports` hoặc mẫu nghiệp vụ hiện có là tùy chọn theo đầu ra, không bắt mọi báo cáo một mẫu. |
| `correspondence` / worker | Khi soạn trả lời từ tập thư Main cấp; nhận message/quote/attachment, người nhận và giới hạn cam kết. Tách yêu cầu mới/quote, đề xuất/quyết định; giữ giọng và tập người nhận. | Nháp local gồm subject/body và đề xuất người nhận/attachment, điều cần xác nhận. Read/Write text; không send/forward/label/draft mailbox. Skill hành văn/mẫu hiện có tùy nhu cầu; không nhét private citation vào thư gửi ngoài. Live mail chưa thuộc V1-A. |
| `market-analyst` / worker | Khi so sánh/nhận định thị trường; nhận phân khúc/địa bàn/kỳ/câu hỏi và bộ căn cứ. So cùng đơn vị/điều kiện/loại giá; tách quan sát/ước lượng/dự báo, nêu độ bao phủ. | Một candidate phân tích có bảng căn cứ, giả định và giới hạn; không tuyên khảo sát toàn thị trường từ bộ nguồn hẹp. Dữ liệu ngoài do Main lấy; cần tính/biểu đồ thì capability tính thật là bắt buộc cho phần đó, không giả từ Read/Write. Thực thi nghề sâu kiểm tại V4. |
| `data-analyst` / worker | Khi việc có phép tính đáng kể; nhận dataset/revision, định nghĩa cột, kỳ/đơn vị/quy tắc làm sạch. Giữ 0/thiếu/không áp dụng; ghi lọc/nhóm/chuyển đơn vị/làm tròn; không tự điền thiếu hoặc loại outlier. | Candidate có phép tính và locator sheet/ô/table-key, kiểm tổng và giới hạn; source nguyên bytes. Capability compute phải được xác nhận ở host/tuyến cụ thể; adapter hiện tại thiếu thì giữ NEEDS_CAPABILITY, không cấp shell. `spreadsheet-check` tùy chọn, không thay phương pháp phân tích. |
| `evidence-reviewer` / reviewer | Khi cần kiểm candidate/claim quan trọng; nhận yêu cầu hiện hành, candidate, cùng source revision và phương pháp. Mở nguồn, đối chiếu kỳ/đơn vị/nội dung; giữ nhãn suy luận; không viết lại báo cáo. | Findings có locator/tác động/sửa cần thiết hoặc phạm vi đã kiểm và phần chưa kiểm; trả qua kênh native để Main lưu. Core Reviewer không Write/compute; đối chiếu text có thể làm, phép tính cần tool chưa có thì báo thiếu. Review không tự thành PASSED/user acceptance. |

**Preset chung:** `INHERIT_CORE_PROFILE`; giữ full model requested của base role. Trường per-method model/tier/effort và capability chưa hỗ trợ phải được báo `UNSUPPORTED`/`NOT_INSPECTED`, không tự thêm vào profile hoặc dùng bảng model của agent xây LAW. Không tự chọn model dự phòng/đắt hơn. Capability được yêu cầu, tool có trong exporter, grant và quan sát host là các chiều khác nhau.

## 4. Phạm vi sửa và luồng triển khai

### 4.1 Catalog và hợp đồng

Thêm `roles/office/catalog.json` và sáu file method ID ở mục 3, cùng `roles/office/MAIN.md`. Catalog `law.office-methods/1` lưu ID, nhãn VI/EN, base_role, đường contract, method version, required capability, optional resource refs và `preset_mode=INHERIT_CORE_PROFILE`. Không lưu observed state, grant, account hoặc live connection. Validator từ chối unknown version/field/ID, duplicate ID/JSON key, base role lạ, path ra ngoài cây method hoặc link; không có plugin loader/auto-import tùy ý.

Catalog là danh mục phương pháp, không là trạng thái công việc hoặc sổ nguồn thứ hai. Contract có phương pháp nghề trong file; không nhân bản toàn bộ skill/native guide vào đó. MAIN guide giữ cách nhận mục tiêu/đầu ra, chọn nghiệp vụ theo ý nghĩa, lập việc vừa đủ, dùng tool, yêu cầu bổ sung, xử lý kết quả và tiếp việc. Không bắt mọi yêu cầu chạy đủ sáu chuyên viên.

### 4.2 Helper soạn giao việc, không thay suy luận của Main

Thêm `tools/office.py` với API và CLI chỉ đọc: đọc/validate catalog, trả mô tả cho Main chọn, và compose **một** brief theo method ID Main đã chọn, lý do chọn, yêu cầu/nguồn/đầu ra/giới hạn cụ thể. Không dùng từ khóa hoặc classifier tự viết để tự nhận đã hiểu yêu cầu tự nhiên. Quyết định chuyên môn thuộc Main native; helper không cấp quyền hoặc dispatch.

- Đầu ra có method/version/base_role, brief chứa phương pháp và điều kiện xong, `context_refs` raw SHA của catalog/contract/skill thực sự dùng, checklist capability và missing items. Không tự scan/tìm nguồn hoặc thực thi script/skill. Thiếu tool/căn cứ không trả trạng thái ready cho phần phụ thuộc.
- Không nhận đường catalog/script tùy ý từ UI; dùng fixed package owner và canonical relative paths qua kiểm link/path hiện có. Input JSON có giới hạn kích thước và strict parse; không import code từ project data, không mạng, không ghi file/log/receipt/cache. Người dùng không cần nhập JSON; Main gọi helper trong workflow.
- V1-A chỉ cam kết hỗ trợ định dạng đầu ra text/HTML và đối chiếu text với bộ tool core hiện tại. Method vẫn nêu nhu cầu compute/Office thật và trả đúng NEEDS_CAPABILITY khi thiếu, không suy tool từ máy có Python hoặc thư viện đã cài.

### 4.3 Main và TASK/checkpoint thật

Cập nhật `roles/README.md`, hướng dẫn core role cần thiết và Main guide để Main dùng method khi phù hợp. Thêm chỉ dẫn ngắn trong `AGENTS.md`/`en/AGENTS.md` dẫn MAIN guide khi làm việc nghiệp vụ nhiều bước, giữ quy tắc việc nhỏ làm trực tiếp. Không đổi PROJECT/grant hoặc tự tạo profile.

Main ghi lý do chọn và yêu cầu nghề trong `intent.main_interpretation`/`acceptance` hiện có; bind catalog/contract/tài nguyên đã dùng qua `context_refs`. Thêm đúng một requirement bắt buộc với `req_id=OFFICE-METHOD:<method-id>:v<method-version>` trong `acceptance.requirements`, statement mô tả điều kiện nghiệp vụ có ý nghĩa. Đây là quy ước ID cấu trúc hợp lệ của trường hiện có, không field/schema hay quyền mới. Child nhận brief và context cụ thể, phải mở đúng method/file nguồn được giao; không chỉ nhận một method ID trống. Actor/callee vẫn core role; không dùng `domain_accepted`, `profile_ref` hoặc `recipe` để suy capability/PASS.

Tích hợp guard cấu trúc của helper vào recipe checkpoint hiện có: chỉ cần thấy marker `OFFICE-METHOD:` hoặc một context path office là phải kiểm cả hai phía. Phải đúng một marker hợp lệ/bắt buộc, đúng catalog và contract tương ứng, method/role/locator/version tương thích, context đủ và raw bytes còn khớp. Marker lạ/trùng, marker mất nhưng refs còn, hoặc toàn refs mất nhưng marker còn đều chặn, không fallback legacy. Không dùng keyword parser đọc intent để đoán chuyên môn. Task legacy chỉ là task không marker và không context office; guard không kiểm đúng ngữ nghĩa nghề hoặc grant. Nếu xóa đồng thời cả marker và refs thì binding TASK/RESULT hiện có phải chặn RESULT cũ; người có thể viết lại toàn record và binding vẫn thuộc giới hạn hợp tác hiện hành, không phải chống giả mạo hoặc host enforcement. Task đổi method/nguồn/yêu cầu thì tăng revision trước nhận kết quả, slot mới khi giao lại, giữ RESULT/candidate cũ.

Giữ một candidate cho mỗi assignment và quy trình Main single writer. Task soạn candidate và phần Reviewer read-only là hai phần việc có căn cứ/assignment phù hợp, không ép Reviewer ghi candidate hoặc RESULT file. Ràng buộc review bắt buộc, checkpoint và nội dung vẫn theo owner cũ; chưa đủ review thì giữ chờ. Helper có thể xuất bản đề xuất fragment cho Main, không có API tạo/lưu TASK mới hoặc job engine.

### 4.4 Mặt giao việc và đóng gói

- `tools/app_ui.html` và `tools/app.py`: thêm vùng mô tả công việc tự nhiên trong mặt giao việc hiện có, kèm yêu cầu Main dùng catalog/phương pháp và giữ nguồn/đầu ra. Người dùng không phải chọn ID agent. Nếu UI gọi helper thì route chỉ đọc dùng cùng validator; chỉ các trường cần thiết, không arbitrary file read. Không ghi mô tả vào ops history/diagnostics. Trạng thái “đã chuẩn bị/đã sao chép”, không “đã phân công/đang chạy”. Không làm UI ngữ nghĩa/router hoặc backend AI mới.
- Giữ cách tiếp việc cũ, current draft và trang thư viện. Không bắt chọn nguồn ngoài trong V1-A; source local cụ thể do Main xác định/bind bằng owner thư viện đang có.
- `tools/README.md` và hướng dẫn Main/core cập nhật đúng năng lực. File role mới song ngữ; thay Markdown có HTML owner thì dùng generator hiện có, chỉ output liên quan. Không tự viết lại guide khác hoặc đưa trạng thái bảo trì vào bản phát hành.
- Kiểm projection/new project/upgrade trên fixture qua owner thật. Giữ lựa chọn/profile/grant/project riêng; package mới không chứa mô tả việc/sources/grants của maintainer. Contract method user đã sửa phải đi qua conflict/pending hiện có, không tự overwrite. Không sửa `check_package.py`/`upgrade_package.py`/`native_agents.py` để mở scope khác; gặp blocker có locator thì trả amendment nhỏ trước phần sửa đó.

**Owner ghi được:** các file mới nêu trên; `roles/README.md`; core `roles/*/agent.md`/`checks.md` nếu cần hướng dẫn đọc method; `AGENTS.md`/`en/AGENTS.md`; `tools/app.py`/`app_ui.html`/`README.md`; tests tương ứng; STATE/HANDOFF. Không sửa role config/preset, profile/schema, `.cvf/`, pin/vector, transaction/writer, pack/intake, VERSION/MANIFESTrepo hoặc native file thật. Không mở web/kho/mailbox, cài dependency/skill mới, provider/CLI AI, host/global/admin, Git stage/commit/push hoặc release.

## 5. Acceptance V1-A và bằng chứng còn thiếu để đóng V1

| Nhóm | Điều phải chứng minh |
|---|---|
| A — Đủ bộ và đúng nghề | Sáu hợp đồng ở mục3 có phương pháp/trigger/input/output/tool/preset/check/thiếu nguồn khác nhau có ý nghĩa. Thư ký và đối chiếu đủ cụ thể cho V2; không chỉ kiểm tồn tại file hay label. Reviewer đọc nội dung hợp đồng, test máy chỉ nhận phần cấu trúc. |
| B — Main tổ chức việc | Ba yêu cầu tự nhiên minh họa: sửa một câu → Main trực tiếp; báo cáo tuần → thư ký + đối chiếu; phân tích dataset cần compute → chọn data method và giữ phần thiếu tool. Main nêu lý do/cách làm, nguồn/đầu ra và phần chờ, không giao user phân vai. Nếu chưa có phiên Main thật thì đánh dấu walkthrough/mô phỏng, không gọi test helper là routing ngữ nghĩa đã chạy. |
| C — Compose và từ chối | Helper sinh một brief cụ thể và context đúng bytes, role/profile/capability tách rõ. Field/version/ID/path lạ, duplicate, link, contract/skill bị thiếu/lỗi phải báo và không làm gì ngoài scope. Thiếu profile không tạo model/grant; compute không được giả available từ core tool list. Không thao tác mạng/ghi khi chỉ xem/copy. |
| D — Binding và tương thích | Probe dùng recipe checkpoint và loader/binding thật: candidate hợp lệ với marker/context phương pháp; đổi contract/catalog/skill đã dùng, input hoặc TASK làm bản cũ bị chặn. Thiếu marker khi còn refs, mất toàn refs khi còn marker, marker trùng/lạ/sai version hoặc sai base_role đều chặn; mất đồng thời marker và refs làm RESULT cũ không khớp binding. Giữ candidate/RESULT cũ; task legacy không office vẫn hoạt động. Test không tự cài checkpoint giả hoặc bỏ assertions cũ. |
| E — UI/HTTP | Một browser flow nhập yêu cầu → chuẩn bị → copy có mô tả công việc và Main guide/context cần đọc; input markup được escape, không lỗi JS và không claim chạy agent. Một HTTP refusal payload/path sửa bằng tay nếu có route mới; không ops-history/diagnostics lưu nội dung. Tiếp việc và bản nháp hiện hành giữ hành vi cũ. |
| F — Delivery/bảo toàn | Fixture materialize VI/EN qua owner thật có method/tool/guide dùng được và profile sạch; upgrade project cũ có file riêng và method đã tùy chỉnh giữ bytes/pending đúng owner, không thêm grant/model/nguồn ngoài. Không refresh MANIFESTrepo để làm test đạt. Không gọi fixture là release được nghiệm thu. |
| G — Claim và điểm dừng | Evidence nêu PREPARED vs invoked vs content-checked. V1-A nhận chỉ foundation đã kiểm; V1 chưa đóng nếu thiếu live Main→core role đọc đúng method và dùng tool trong grant. Không coi test/native receipt là trace. V2 còn full report, review, sửa và mở lại. |

Việc user thật hiểu/dùng được, chất lượng chuyên môn thị trường/số liệu/thư tín, model/preset riêng, compute/Office/connector và host enforcement chưa được nhận ở V1-A. Có ca thiếu quyền/tool thì làm phần độc lập và ghi tuyến chờ, không thêm grant/tool hoặc hạ tiêu chí để demo thành công.

## 6. Kiểm và bàn giao

Trước sửa: đọc AGENTS/STATE, work order này, roadmap revision2 và đúng owner; chụp `git status --short`, diff và raw hash các file sẽ sửa. Worktree không sạch do tài liệu điều phối; giữ nguyên, không reset/stash/clean. Đọc phần HANDOFF audit V0 hiện hành, không toàn lịch sử.

Chạy tests mới cho helper/catalog/office context, các target ảnh hưởng trong `tests/test_task_result_flow.py` và legacy tương ứng, HTTP/browser flow mới, fixture projection/upgrade. Dùng harness hiện có, mọi dữ liệu giả/tempfile. Đọc code/test liên quan trước chọn lệnh; không chạy toàn suite/module lớn chỉ để lặp bằng chứng. Không sửa expected/pin/guard hoặc thêm skip để xanh; công cụ lỗi thử lại tối đa một lần rồi báo.

Chạy package check `python -B tools/check_package.py --release`; generator `--check` trước/sau, dựng lại khi Markdown thuộc generator đổi; `git diff --check -- <file-chạm>` và `python -B tools/check_package.py --check-eol <file-chạm>`. Không build/publish release ở phiếu này. Chỉ test cần thiết cho delta; lỗi cụ thể sửa và kiểm lại đúng phần, không audit lan sang tranche đã nhận.

Claude tự xem diff cuối và đối chiếu A–G; HANDOFF ghi model/effort requested/quan sát được, delta/baseline/hash/EOL, test thật/pass/skip/reason, phần walkthrough/host chưa chạy và giới hạn từng method. Bàn giao **`IMPLEMENTED_PENDING_REVIEW — V1A_OFFICE_FOUNDATION`**. Không tự đánh dấu V1 hoặc V2 đạt.

Codex review cấu trúc, nội dung phương pháp, binding/compatibility, đường đọc UI và bảo toàn upgrade; review độc lập boundary liên quan theo8.3. Thiếu phần bắt buộc thì nhận subset hoặc giữ chờ đúng evidence; không tự phát sinh feature để bù. Sau nhận V1-A, chỉ hoàn thiện bằng chứng còn thiếu của V1 trước V2; không quay lại selector nguồn như trục sản phẩm.

## 7. Baseline để đối chiếu delta

Raw SHA256 trước thi công; đây không phải pin mới hoặc quyền khôi phục ghi đè:

| Owner | SHA256 |
|---|---|
| roles/README.md | 58dfa146ceb5e3d93383e7cbe6240c34e8992e6b82079c833c537ed0c7f90f88 |
| tools/native_agents.py — giữ | e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e |
| tools/execution_profile.py — giữ | 74a9ff58cfd26c3df9beeefe4edebf5bfdc6e19ccb81ef1bca3a0e5fa4e1e331 |
| .agent/EXECUTION_PROFILE.schema.json — giữ | a550fcdb358a8df4f4bd7905836e3af4df1544b090c1ec93e0e5cafac0169225 |
| .cvf/contracts/v3/control.schema.json — giữ | 21d3b192151b84f6d999d17bf0ed8e209678e6db39fc685c7c9c26918b2a3642 |
| tools/app.py | 2d08d3d71149fca5007f760c6dcba125aa25f53ed4b05f8230eb790b23f60838 |
| tools/app_ui.html | 972e6777b933d78147d198dc60f032e8e5e95d6219e362eb402c397c472c4bb0 |
| AGENTS.md | a4b02982f15e6de19c3b705695f64bdf58f58cb501142b3fae2dd2d45dcc7d1f |

Nguồn mục tiêu: operator sửa định hướng trong hội thoại; external R1 ở Downloads mục1/3/5/9/12 và phản hồi hội tụ mục1–3/5, chỉ dùng làm dữ liệu thiết kế. Native model/version/khả năng của host tương lai phải kiểm khi thực thi trong quyền; audit này không nghiên cứu lại provider hoặc gán cấu hình maintainer thành preset sản phẩm.
