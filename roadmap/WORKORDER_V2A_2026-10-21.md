# Work order V2-A — Giao Worker đủ TASK, binding và RESULT

**Ngày:** 21/10/2026. **Trạng thái:** `ACCEPTED_WITH_LIMITS — V2A_COMPLETE_HANDOVER`; đã review subset chuẩn bị giao việc, chưa V2 end-to-end.  
**Worker:** Claude do operator chọn model/effort. **Orchestrator/reviewer:** Codex. Đây là sửa phần chuẩn bị giao việc cho luồng V2, chưa phải nghiệm thu văn phòng vận hành trọn vòng.

**Review kế hoạch:** `v1b_trace_review` (`gpt-6-sol/medium`) đọc toàn phiếu và owner/schema/test cần thiết, không thấy blocker. Đã làm rõ RESULT đầy đủ theo schema và `outputs` nằm trong binding. Luna Max audit owner/ranh giới V1–V2 độc lập; hai reviewer chỉ đọc, không chạy tests/CLI hoặc sửa file. Live V2 và grant sản phẩm chưa được chứng minh.

## 1. Căn cứ và mục tiêu

Audit lại đúng acceptance V1: V1-A đã có catalog/helper/guard và các ca việc nhỏ, thiếu capability, stale revision; V1-B/B2 có trace Main chọn phương pháp và native Worker/Reviewer dùng contract. Nhận V1 `ACCEPTED_WITH_LIMITS` cho phạm vi đó trên CLI2.1.81. Việc Main suy luận chọn nghề ở các tình huống khác vẫn chưa có cùng mức proof live. Không đòi thêm grant sản phẩm hoặc checkpoint tích hợp thật để đóng V1: đây là dependency/phần việc của V2, không phải tiêu chí V1 mới.

Gap cụ thể cần sửa trước lần giao Worker kế tiếp: `tools/office.py:_brief` hiện ghi OUTPUT chỉ một candidate; Main guide dẫn chung sang `roles/README.md`. Trong V1-B, Worker không được giao ghi RESULT hoặc nhận binding tính sẵn, nên chỉ có candidate. Recipe A-11 đã có đủ chức năng; **chưa có bằng chứng cần một engine/builder/schema mới**.

Kết quả mong muốn: Main vẫn chọn phương pháp qua helper chỉ đọc, nhưng biết hoàn thiện gói giao việc sau khi có TASK cuối cùng; Worker nhận đúng TASK/binding/slot và trả candidate **cùng metadata RESULT CANDIDATE**. Reviewer vẫn chỉ trả findings qua native; không được giao Write RESULT.

## 2. Owner và phạm vi sửa

| Owner | Việc được giao |
|---|---|
| `tools/office.py` — `_brief` | Bổ sung chỉ dẫn hợp tác theo vai: Worker tạo đúng một candidate và RESULT metadata trong slot Main giao, dùng binding Main tính; thiếu gói giao việc thì trả Main. Giữ đầu ra Scout/Reviewer chỉ phản hồi, không ghi file. Không thêm command/field, không tự tạo TASK/RESULT hoặc suy quyền. |
| `roles/office/MAIN.md` — mục4/6/7 | Làm rõ thứ tự hoàn thiện giao việc, nhận kết quả, sửa/tiếp việc, bằng VI và EN. Dẫn đúng recipe/owner có sẵn, không chép nguyên recipe hoặc tạo quy trình thứ hai. |
| `tests/test_office.py` | Tận dụng ca hiện có để kiểm role separation/compose readonly/VI–EN/binding không đổi; chỉ mở rộng ca khi cần xác minh hành vi thực đã đổi, không thêm test chỉ lặp văn bản hướng dẫn. |

`roles/README.md` và recipe `law-recipe: task-result-checkpoint` là owner giao thức **chỉ đọc/tái dùng** trong tranche này. Không sửa core role/native definitions, catalog/sáu method contracts, profile/grants, CVF/schema/policy/pin, writer/transaction, runtime, UI, source library, pack, VERSION hoặc MANIFEST. Giữ worktree dirty có trước, không reset/stash/clean.

Baseline kho nguồn HEAD `bcb5153b606bd47547fbc3dff9eb767826170413` + worktree hiện hành:

- office.py SHA256 `867c517dc0a2a2b7a7a4ef3895e30cf192821a8c7b037d1d5150c83c0ce6dfd4`
- MAIN.md `d7dbbe96d31554bd684754b56ac3d9c7193b6eecbdffd55981dcba4c81f670cb`
- Recipe owner roles/README.md giữ `5b7e846e208324aa37e9ad207f9cf7e6ee3b0a327e5b5acd8f84a9a4fea1817b`
- Native adapter giữ `e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e`

Hash khác thì đối chiếu delta thật trước sửa, không phục hồi theo bảng. Không sửa evidence V1-B/B2, các TASK attribution mâu thuẫn hoặc r2 để làm đẹp lịch sử.

## 3. Nội dung phải thể hiện

1. **Compose là bước chuẩn bị.** Method brief/context/input proposal có trước TASK cuối cùng; helper chưa có binding hợp lệ và không tự điền actor/grant/revision/slot. PREPARED không phải được phép dispatch. Main kiểm yêu cầu gốc, nguồn/SourceID/revision, capability, grant và host trong phạm vi thật; thiếu phần bắt buộc thì giữ phần phụ thuộc, không tự cấp quyền/model/tool.
2. **Main hoàn thiện gói giao Worker.** Tạo TASK hiện hành bằng schema v3 đang có, marker/context method, effects/slot cho lần giao riêng. Sau khi TASK chốt, dùng đúng `load_v3` và `binding_stub(v3, task)` của recipe A-11; chuyển binding nguyên vẹn cùng TASK path/revision, candidate path và RESULT path trong slot đó cho Worker. Binding từ TASK bản nháp hoặc binding tự bịa không dùng được. Không đưa giá trị hash mẫu, `[placeholder]` hoặc fixture USER_CONFIRMATION vào một brief được gọi là đủ để dispatch.
3. **Worker trả đúng dạng.** Đọc TASK/contract/nguồn; thiếu binding/slot/đầu vào hoặc brief mâu thuẫn thì trả Main. Ghi một candidate mới và RESULT đầy đủ theo schema v3/recipe A-11: `result_id`, `binding` giữ phần Main giao rồi thêm `outputs` theo bytes candidate thực, `produced_by`, `artifacts`, `evidence`, `requirements`, `gaps`, `acceptance_states=[CANDIDATE]`, `state_set_by`. RESULT là metadata, không tính thành candidate thứ hai. Worker không được giả định có công cụ hash khi host không cấp: không tự khai đã băm hoặc tự điền digest. Nếu không thể hoàn thiện digest/output metadata bằng công cụ thật hoặc đường ghi được giao không cho RESULT, báo thiếu/giữ candidate; Main không giả Worker đã ghi RESULT.
4. **Không giả hỗ trợ công cụ.** Tranche này không thêm shell/compute vào Worker native để giải quyết mục3, không thêm MAIN-generated RESULT rồi gán tác giả Worker. Hướng dẫn phải chỉ ra phần giữ chờ khi capability thực chưa đủ. Đường hoàn thiện RESULT phù hợp host/công cụ sẽ được kiểm ở lượt V2 có điều kiện thật; chỉ dẫn này chưa chứng minh nó đã chạy.
5. **Nhận và tích hợp là bước riêng.** Main đọc TASK hiện hành và RESULT bằng loader, chạy `checkpoint`, đối chiếu raw bytes/ledger khi có định danh và mandatory requirements. Binding khớp chưa là PASS; review bắt buộc phải đúng candidate/binding, không chỉ nhãn đã xong. Gọi `integration_gate` theo recipe; chỉ dùng writer đã có khi quyền bao phủ tác động. Reviewer chỉ Read và trả ROLE_REPORT; Main lưu đúng nguồn gốc, không ép Reviewer tạo RESULT. Không lấy P-CN1 workflow checker áp vào Worker Write/Reviewer Read rồi gọi PASS.
6. **Sửa hoặc mở lại.** Đổi yêu cầu/nguồn/scope: tăng revision và slot theo recipe, giữ RESULT/candidate cũ; `void_assignment` không phải stop proof. Phiên sau đọc STATE/TASK/bytes hiện hành rồi kiểm lại, không tạo lại chỉ để xem và không tái bind RESULT cũ. Bản Main sửa sau review là revision/candidate khác; không gán report của bản trước thành review của bản sau.

## 4. Kiểm vừa đủ

- Tự đọc brief thực do helper xuất cho Worker và Reviewer bằng cả VI/EN; phân biệt chỉ dẫn chuẩn bị với một gói giao đã hoàn thiện. Không dùng chữ “sẵn sàng” để che grant/host/binding chưa kiểm. Scout vẫn chỉ phản hồi như core exporter hiện tại.
- Chạy các ca liên quan đã có: `Compose.test_weekly_report_brief_is_concrete_binds_exact_bytes_and_keeps_roles_apart`, `Compose.test_english_brief_uses_the_english_lines_of_the_contract`, `Compose.test_composing_writes_nothing_uses_no_network_and_imports_nothing_from_project_data`, `Compose.test_format_and_declared_compute_raise_the_requirement_of_other_methods`, `OfficeBinding.test_a_valid_office_candidate_passes_and_publishes_the_checked_bytes`, `OfficeBinding.test_task_changes_void_the_old_result_which_keeps_its_bytes` trong `tests.test_office`. Test fixture/publish là mô phỏng, không grant/dispatch hoặc nghiệm thu thật.
- Nếu thêm/sửa test vì delta cụ thể, ghi rõ nó kiểm rủi ro gì; không cần test mới cho mỗi câu hướng dẫn. Không fullsuite/paid demo/release gate khi không có lỗi mới liên quan. Kiểm EOL từng file chạm bằng `check_package.py --check-eol` và `git diff --check`; file untracked kiểm riêng.

## 5. Acceptance và bàn giao

- Brief/guidance của Worker nhất quán với recipe có sẵn: phân biệt TASK, binding, candidate và RESULT; chỉ rõ Main tính binding trước giao và capability thiếu phải báo. Scout/Reviewer giữ readonly. Không có thay đổi machine schema/API/permission hoặc producer giả.
- Checkpoint/integration/việc sửa-mở lại dẫn về một owner đã có, không chép builder/validator mới; không gọi test/helper receipt là host enforcement hoặc đã chạy end-to-end.
- Test liên quan đạt hoặc báo đúng lỗi/skip chưa xử lý; tự xem diff, source giữ/đổi và VI–EN. Không đụng tài liệu/bytes người dùng hoặc evidence cũ.
- Trả `IMPLEMENTED_PENDING_REVIEW — V2A_COMPLETE_HANDOVER`, ghi model/effort requested/observed, file/hash, lệnh và phần đã kiểm/chưa kiểm trong HANDOFF; cập nhật STATE đúng8heading/≤60dòng. Codex review delta trước nhận subset V2-A.

Không chạy thêm Claude CLI/AI provider, không cài/đăng ký native/grant, không migrate PROJECT. Khi đủ một công việc nghiệp vụ cùng nguồn/host/grant thật mới giao lượt vận hành V2 tiếp theo; chuẩn bị hướng dẫn không thay điều kiện đó. Không tự đóng toàn V2, chấp nhận bản lab, stage/commit/push hoặc phát hành.

## 6. Review Codex — ACCEPTED_WITH_LIMITS, 21/10/2026

Nhận đúng subset: `_brief` thêm `_handover` hướng dẫn theo vai; Main guide mục4/6/7 dẫn A-11 để hoàn thiện TASK/binding/slot, nhận và tích hợp riêng, sửa/mở lại đúng revision. Helper không tạo record/ghi file/cấp quyền; Scout/Reviewer chỉ trả ROLE_REPORT. Worker thiếu công cụ hash hoặc quyền ghi RESULT phải báo giữ chờ. Không có bằng chứng native host đã chạy trọn protocol; V2 vẫn PARTIAL.

- **Review độc lập:** `v1b_trace_review` cấu hình `gpt-6-sol/medium`, đọc helper/guide/test/schema và không thấy blocker còn lại. Reviewer sửa trực tiếp đúng2string VI/EN trong office.py: bổ sung3header bắt buộc `schema_version`, `record_type`, `evaluation_basis` trước9trường riêng của RESULT. Không đổi logic/API/schema/native/MAIN/test; `ast.parse` đạt. Không thêm vòng reviewer cho sửa nhỏ này.
- **Root đã kiểm source cuối:**6target mục4 đạt/0skip/1.173s sau sửa header (6target trước sửa cũng đạt, không cộng thành12test khác nhau). Bao phủ compose/VI–EN/readonly/role separation và fixture binding/publish/revision. Không fullsuite hoặc paid demo. Suite33test Worker khai đạt là evidence Worker, không Root chạy lại.
- **Delta thật:** khi loại riêng hàm `_handover` và dòng gọi/khoảng cách chèn thêm trong bộ nhớ, office.py khớp hash V1-A; bỏ phần assertions mới trong bộ nhớ, test_office.py khớp baseline49cc42e7… đã có trong HANDOFF V1-A. Không ghi/revert file khi đối chiếu. Ba file source untracked nên `git diff --` không tự thể hiện delta này.
- **Identity source cuối:** office.py `d52e0fe73ceda01b75561e62ab2964dbe992561594b05bd405ef9f5524dce66a`; MAIN.md `6fb232cf52e034e64b20ffee506cf7e28b25497f90253d318dbecbf53fd60494`; test_office.py `30b21448f545ed190dc3437edd25607761c1bd0862c300df57cc6e7b06f22220`. Recipe roles/README.md và native adapter khớp hai hash giữ ở mục2; không sửa schema/profile/grant/catalog/contracts/UI/transaction/writer hoặc evidence B/B2.
- **Giới hạn giữ nguyên:** test fixture/publish là mô phỏng; chưa product grant/dispatch/RESULT-checkpoint thật, opener/resume trên host, hash capability Worker hoặc chất lượng báo cáo V2. Chỉ dẫn báo giữ chờ không cung cấp công cụ còn thiếu. Không retire lab/dọn D:\c, stage/commit/push hoặc release gate. Tranche vận hành tiếp cần task/nguồn/host/grant và đường digest thật trước khi gọi là trọn vòng; không lấy receipt/test PASS thay thế.
