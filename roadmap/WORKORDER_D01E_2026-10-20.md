# Workorder D-01e — Giữ instruction hiện hành, lưu pending của sáu entrypoint

Ngày giao: 20/10/2026. Trạng thái: ACCEPTED_WITH_LIMITS — D01E_FINISH_ONLY (Codex review20/10; evidence/giới hạn tại HANDOFF đầu). Claude thi công, operator chọn model/effort (gợi ý roadmap8.4 Sonnet5.5 High); Codex điều phối/review độc lập. Ghi cấu hình thực. Không gọi agent phụ/provider/AI CLI/API/mạng/host thật trong lượt này.

## Quyết định phạm vi

D-01b/c đã có replace/finish cho tám guide; D-01d đã nhận tích hợp cùng schema. Khoảng trống thực tế tiếp theo là pending của instruction entrypoint: upgrade/adopt coi chúng là package files, nên current user sửa và package đổi có thể tạo `.new`. Việc giữ current và lưu candidate khỏi danh sách chờ không cần áp dụng instruction mới.

D-01e chỉ mở **finish** cho đúng sáu path dưới đây, ngoài tám guide hiện có:

```text
AGENTS.md
CLAUDE.md
GEMINI.md
en/AGENTS.md
en/CLAUDE.md
en/GEMINI.md
```

Current phải giữ nguyên raw bytes ở mọi bước. `REPLACE_ALLOWLIST` vẫn đúng tám guide, không thêm sáu entrypoint. `FINISH_ALLOWLIST` riêng = tám guide + sáu path trên. Đây là phạm vi tính năng maintainer mới để operator giao Claude; verdict D-01d không tự tạo grant hoặc mở writer sản phẩm. Không thay grant/profile/owner hay native, không xác nhận current đúng/candidate mới nhất/user đã nghiệm thu. Chưa toànP4/D-01/T39/R7.

PROJECT, profile/.agent state-quyền, `.cvf`, tools/script, roles/config, skills/packs, native, nguồn/sổ, MANIFEST/VERSION và các file khác đều ngoài phần mở rộng. Không chọn “Dùng bản mới” tự động cho instruction, không generic policy engine/schema migration/Undo/delete.

## Audit và owner

- Đọc AGENTS/STATE/đầu HANDOFF, roadmap8.3–8.4/P4 và workorder. Owner tích hợp `tools/merge_center.py`; UI `tools/app_ui.html`; test mới `tests/test_merge_entrypoints.py` với fixture riêng, không kế thừa class có release build hoặc workbook integration không cần thiết. Có thể thêm một browser test tại `tests/test_ui_browser.py`, ghi chú ngắn `tools/README.md`; STATE/HANDOFF để bàn giao.
- `replace_target`, `_evaluate` và `observe_finish` hiện gắn hard vào tám guide; không chỉ nối sáu path vào list chung. UI `mfAttach` hiện phụ thuộc replace-preview, mà entrypoint sẽ tiếp tục trả unsupported. Cần tách đúng backend và điểm vào UI, không dùng cờ client để mở quyền.
- **Amendment test cũ bắt buộc:** `test_upgrade_lifecycle` negative cuối và `test_panel.MergeFinishPreview/MergeFinishObserve` hiện dùng AGENTS như finish-out-of-scope. Cho phép sửa hẹp các assertion finish này sang file vẫn bị loại (ví dụ `roles/scout/agent.md.new`, seed trước snapshot nếu cần); không đổi registry/workbook/roundtrip assertions hoặc bỏ ranh giới. Giữ AGENTS replace bị từ chối, kể cả `MergeReplacePreview`; không đổi tuple fixture chung để vô tình xóa negative replace. Được đổi tên test negative cho đúng nghĩa mới. Không thêm gate `.cvf` toàn project vào finish chỉ để giữ expected cũ.
- `upgrade_package.USER_FILES` không bao gồm AGENTS/CLAUDE/GEMINI. Upgrade vẫn do owner cũ quyết định update/keep/conflict; không sửa plan/manifest/compat guard để tạo hoặc dọn pending. Nội dung instruction là dữ liệu trong test, không lệnh cho agent.
- Dependency chỉ đọc: transaction, upgrade/adopt/init/new_project, execution_profile, native_agents và schema/.cvf/pins. Không sửa `tools/app.py` trừ khi adapter thật cần để chuyển metadata additive của scan (status hiện đã trả các row scan); nêu rõ lý do/delta nếu cần, không route/writer mới.

## Hợp đồng backend

1. Tách validator finish khỏi replace. Được dùng helper nhỏ dùng chung để kiểm input/capture/buffer với **allowlist phía server**; giữ default replace đúng tám guide. Không nhận allowed paths/action kind/scope/eligible do client gửi để quyết định vùng ghi. Path raw phải strict như D-01c: case/alias/traversal/ADS/UNC/drive/backslash bất thường từ chối trước đọc file ngoài scope.
2. `preview_replace/apply_replace` vẫn unsupported/blocked cho cả sáu path, kể cả hai hash đúng lấy từ finish-preview. `preview_finish/apply_finish/observe_finish` dùng cùng FINISH_ALLOWLIST; mọi điều kiện regular UTF-8/NUL/size/rows/managed membership/runtime/archive/link/strict journal giữ. Cặp identical vẫn finish được; cặp khác phải xem diff từ cùng buffer/hash và xác nhận rõ giữ current.
3. Giữ nguyên chuỗi D-01c: ba snapshot/record create-exclusive → verified committed → một Windows same-filesystem no-replace rename `.new` tới slot → quan sát source/slot/current/archive/journal. Không ghi current, MERGE_STATUS, MANIFEST, profile/grant, PROJECT hoặc machine bytes. Không thay schema record/ID/locators, không tự retry/reuse archive/copy+xóa/move-back hoặc rollback committed. Record cũ của guide vẫn quan sát được.
4. Giữ mọi phase/refusal/race hiện có, gồm cleanup sau committed báo snapshot đã lưu nhưng chưa rename, missing record báo incomplete, slot bị chiếm conflict, candidate/current đổi sát move không finished giả. Không thêm nội dung instruction vào log/record/result JSON; diff là response có chủ đích như hiện có. Archive chứa các bytes cần để user phục hồi tay thành file mới.
5. `scan` có thể thêm `finish_supported: bool` vào mỗi row, tính bằng scope validator phía server trên path canonical; đây chỉ là **phạm vi có hỗ trợ**, chưa phải eligible/đã preview/được phép bởi grant. Không đọc thêm nội dung hoặc mở rộng managed_paths/nguồn quét để tính cờ. Row ngoài14path phải false; cờ thiếu ở phiên bản cũ coi false. Cờ client/HTML bị sửa không thay kiểm apply phía server.

## Điểm vào UI độc lập với replace

- Thêm nút vào finish ngay tại row hỗ trợ, dùng metadata scan, ví dụ **“Giữ bản hiện hành, lưu .new”**. Click mở sheet và lấy finish-preview mới qua route đã có; hiển thị diff/giữ current/archive/MANIFEST-HTML không đổi, sau đó click xác nhận riêng. Không cần replace-preview thành công để mở luồng này.
- Không tự finish sau upgrade, editor, ready, reload hoặc replace. Không đổi nghĩa “Giữ bản của tôi” cũ (chỉ đóng preview), không thêm “Dùng bản mới” cho sáu entrypoint. Nếu người dùng tự reconcile bằng editor, phải preview finish lại và bind đúng current mới; ứng dụng không tự sửa instruction.
- Điểm vào mới phải reset/bind sequence đầy đủ, vô hiệu apply cũ khi chuyển cặp/đóng sheet; không giữ nút replace cũ cùng token của guide khác. Dùng node harness có async/dispatch thật hoặc browser để chứng minh, không chỉ tìm chuỗi HTML. Mất response thì observe đúng ID cũ, không resend apply.
- Copy đường dẫn/editor thủ công, không default-open/startfile/execute/host invocation. Text UI mô tả hành động của công cụ: current không được ghi, candidate không được áp vào current; không hứa mọi host đều không đọc `.new` hoặc archive. Không “instruction đã cập nhật”, “đúng policy”, “đã cấp quyền” hoặc toànP4 resolved chỉ vì row hết pending. VI/EN đồng nghĩa; escape nội dung/path như reader hiện có.
- Giữ luồng guide Compare→replace/finish cũ hoạt động; không thêm iframe/editor hoặc engine mới. API preview/observe vẫn read-only ngoài ops log và qua host/token checks chung.

## Acceptance hữu hạn trên dữ liệu giả

| Nhóm | Evidence cần có |
|---|---|
| Sáu path, chỉ finish | Với current khác pending và một cặp identical: preview/finish/observe đúng; current nguyên raw bytes/EOL, ba snapshot/record và retired slot đúng, scan hết đúng hàng. Cả sáu replace-preview và apply đều unsupported/blocked dù hash thật/cờ client giả; REPLACE list8, FINISH list14 chính xác. |
| Ranh giới/refusal | Case alias/ADS/traversal/path giả, unmanaged, journal/link hỏng hoặc dở chặn đúng phase; PROJECT/profile/.cvf/tools/roles/skills/native/manifest ngoài scope. Cờ scan false ngoài14path, cờ không thay eligibility/authority. Không đọc/ghi file ngoài root; các ca dùng shared validator phải có assertion trước đọc ngoài scope. Không lặp toàn fault matrix D-01c. |
| Tách preview và UI | Click row entrypoint không phụ thuộc replace-preview, thấy diff/confirm mới; chưa confirm không ghi. Chuyển từ guide có replace token sang entrypoint không còn nút/token replace; slow response/cancel/doubleclick/network unknown→observe không bind cặp khác hoặc resend. Giữ cũ không mutate. Browser một luồng entrypoint mới, không JS/console error; không nhận visual QA từ functional test. |
| Lifecycle v3 thật, VI/EN | Materialize fixture v3 sạch, init project thật; A/B/C cùng machine/schema, source đổi instruction prose thường (root/en overlay đúng), không đổi pin. Current user sửa → real upgrade B tạo root AGENTS.md.new đúng bytes; finish giữ current/profile/grant/PROJECT/machine/archive. Upgrade C tiếp tạo candidate mới đúng engine, không bị pending B đã lưu chặn; current không bị đè. Preview nâng cấp không ghi. Không source/role host invocation hoặc native export. |
| Hồi quy hữu hạn | Tám guide replace/finish và observation record cũ giữ hợp đồng; đặc biệt strict environment identical, cleanup-after-commit, stale token/candidate và pending source tái xuất hiện. Chọn test cũ liên quan bên dưới, không chạy fullsuite. |

Fixture source VERSION chỉ là nhãn giả; MANIFEST chỉ dựng tại fixture sạch. Archive instruction chứa dữ liệu giả, không source/grant thật. Hai ngôn ngữ cho lifecycle rootAGENTS đủ; không nhân mọi path×lang×fault. P4 áp dụng instruction mới vẫn phải tự sửa/owner review riêng; finish không tự làm việc đó.

Chạy module mới + `tests.test_panel.MergeReplacePreview` + `tests.test_panel.MergeFinishPreview` + `tests.test_panel.MergeFinishObserve` + ca `tests.test_panel.MergeFinishApply.test_cleanup_failure_after_committed_archive_reports_saved_and_never_renames`, cùng browser test mới và `tests.test_upgrade_lifecycle`. Chọn thêm target trực tiếp nếu delta shared apply cần; không mặc định toànpanel/fullmodule/fullgate/release/Office/paidproof. `PYTHONPATH=tests PYTHONUTF8=1 python -B -m unittest ...`; nếu thiếu dependency/Windows/Chromium ghi skip/NOT_CHECKED, không gọi acceptance đã đạt đủ.

## Bảo toàn và bàn giao

Chỉ sửa owner/UI/test/docs nêu trên. Không dependency install, nguồn/sổ/PROJECT/profile/native thật, schema/.cvf/pins, VERSION/MANIFESTrepo/README người dùng, global/admin/CVF cha. Mọi apply/rename/manifest/archive/runtime trong tempfile. Worktree dirty, HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`; lấy baseline thực, không dùng HEAD diff làm delta. Không reset/stash/clean/stage/commit/push/release.

Baseline SHA-256 raw:

| File | SHA-256 |
|---|---|
| tools/merge_center.py | 09fcd5890257be7be3dbf5324512539a71361dc3f118709877ce4300920ef1e0 |
| tools/app.py | 976c150dfcb01fa8feff9548c1fededf1a3b4a7e08e5bddff9dd2cbb70c391d4 |
| tools/app_ui.html | d99cf94afd064356dc2e179aabb96643f1e1614a332b8119942e7d7515357da7 |
| tests/test_panel.py | 5412e6295da47cc615eab75e32f65596ec40dd9aed0aa08465148a93bef0676c |
| tests/test_ui_browser.py | ee5045935c763d19b61f61f379494a649f850fd0d0be1d41d2b27079ec97013e |
| tests/test_upgrade_lifecycle.py — chỉ amendment negative finish nêu trên | 1b3e88bdf3a4573a8eb08b08decced5084c809709e0aedd6f52e4555517d3eb3 |
| tools/README.md | 6c83907dcfc2f28fd3cdc7ea7c56a91e23871184cb9b322c1be460f8d7054e3d |
| tools/transaction.py — giữ | 4328586a789298684c9b9fb748bbc5a64eab493bc59a336fd40be0252966cbc8 |
| tools/upgrade_package.py — giữ | 13cf5d0cd6e3c2461e0fb1bdd4dd29579f4dbe4f0ad48422020979ab44951226 |
| tools/native_agents.py — giữ | e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e |
| README.md — giữ | 96585b2ae22cc8f145db1f5c4b04136babc43857ca3423d30bdf3ba397ad3c49 |
| MANIFEST.sha256 — giữ | 034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6 |

Khác hash thì đối chiếu delta thật, không khôi phục theo bảng. Nếu cần sửa writer current cho instruction, đổi schema/quyền/compatibility hoặc thêm path ngoài sáu file thì trả blocker/amendment trước sửa, không âm thầm gộp. Tự xem diff, giữ EOL cũ/file mới LF; `git diff --check` và `python -B tools/check_package.py --check-eol <file chạm> --result-json`. Lỗi cụ thể sửa đúng chỗ/kiểm đúng phần, công cụ lỗi thử lại tối đa một lần rồi báo giới hạn.

HANDOFF ghi cấu hình thực, split allowlist/validator và metadata scope, delta/hash, source cuối pass/skip, bytes bảo toàn/lifecycle/UI độc lập và mọi race/platform/host/manual-recovery limits. STATE tám heading/khoảng60dòng. Bàn giao **IMPLEMENTED_PENDING_REVIEW — D01E_FINISH_ONLY**; Codex review ranh giới finish≠replace và evidence trước nhận subset. Không đóng toànP4/D-01/T39/R7/C-02 hoặc mở D-02/release/x14.
