# Workorder D-01a — Phân biệt nhãn phiên bản và baseline nội dung gói

Ngày giao: 20/10/2026. Trạng thái: READY_FOR_CLAUDE. Đây là phần đầu hữu hạn của D-01/P1, chưa toàn D-01/T39 hoặc xử lý P4.

## Giao việc và dependency

Claude thi công, operator chọn model/effort; đề xuất roadmap8.4 Sonnet5.5 High. Codex giữ Orchestrator/Reviewer, nhận bàn giao. Ghi cấu hình thực quan sát được, không quy effort thô thành mức có tên. Không gọi agent phụ, AI CLI/API/provider, host thật hoặc mạng trong lượt này.

A-09/B-02/C-01 đã nhận WITH_LIMITS, đủ dependency audit/thi công phần D-01 độc lập. C-02 chỉ nhận bộ chuẩn bị, chưa có người mới và T37–T38 vẫn NOT_RUN; D-01a không dùng việc đó làm bằng chứng usability hoặc mở release/D-02.

**Mục tiêu:** người dùng không còn phải hiểu một dòng `vX → vX` như thể nhãn version đã tăng. CLI và kết quả có cấu trúc phải phân biệt cùng nhãn nhưng baseline nội dung gói khác, cùng baseline, khác nhãn và chưa xác định; kế hoạch giữ/cập nhật/xung đột vẫn do owner hiện có quyết định. Panel đang hiển thị stdout của CLI nên không cần thêm UI hoặc status engine.

## Audit và ranh giới đã chốt

- Đọc AGENTS, STATE, đầu HANDOFF, roadmap D-01/P1/P4/T39 và mục8.3–8.4. Code owner: `tools/upgrade_package.py`; dependency chỉ đọc: `check_package.py`, `execution_profile.py`, `transaction.py`, `merge_center.py` và hướng dẫn nâng cấp.
- `upgrade_package.py` đã so ba bên qua MANIFEST và giữ file user, tạo `.new` khi hai bên đổi. Dòng thông báo hiện chỉ có from/to version; structured preview/apply cũng chỉ có hai nhãn đó. Không đổi thuật toán plan hoặc quy tắc ghi để sửa P1.
- Định danh là **baseline package đã ghi trong MANIFEST của project** so với package nguồn, không phải hash toàn bộ project hiện tại. File user sửa, overlay EN, profile/index hoặc bootstrap có thể khác mà baseline vẫn cùng; vẫn phải hiện đúng kế hoạch thực tế. Cùng identity không có nghĩa không còn việc phải làm.
- So identity trên tập entry path/hash hợp lệ đã sắp xếp; EOL và thứ tự dòng MANIFEST không làm baseline khác giả. Có thể dùng helper nhỏ tại owner để tính digest ổn định của entry, không thêm protocol/canonical engine/registry hoặc file metadata mới. Hash không chứng minh authority, an toàn hay hiệu lực nội dung.
- Manifest thiếu/hỏng/không đọc được/mơ hồ thì không suy identity từ VERSION, không tự sửa manifest. Giữ refusal hiện có; diagnostic bổ sung chỉ UNKNOWN/chưa xác định khi không đủ dữ kiện. Không làm lỗi cũ thành success hoặc bỏ compatibility guard. Không lấy map đã nuốt duplicate làm bằng chứng identity tin cậy nếu raw nguồn mơ hồ.
- P4 cần tranche sau: merge_center hiện chỉ scan/diff/trạng thái xem, không resolve. Transaction hiện ghi/create, không có delete; backup giao dịch bị dọn khi commit thành công. Không được tuyên có post-success undo hoặc thêm unlink ngoài transaction chỉ để xóa `.new`. D-01a không sửa writer hay mở chức năng keep/use-new/resolve; P4 vẫn OPEN.

## Phạm vi sửa

- `tools/upgrade_package.py`: helper identity/diagnostic nhỏ, thông báo VI/EN và metadata bổ sung ở preview/apply/no-op nơi đã có đủ dữ kiện. Giữ top-level `from_version`, `to_version`, status/code/changes/merge_required và API cũ; dùng một object bổ sung (ví dụ `package_identity`) cho baseline nguồn/đích và quan hệ version/manifest. Chốt shape ngắn trong HANDOFF trước code; metadata là mô tả, không token/grant hay acceptance.
- Một owner test upgrade: ưu tiên thêm lớp riêng trong `tests/test_workflows.py`; có thể chọn module chuyên biệt duy nhất nếu nhỏ/rõ hơn. Không nhân bản plan/transaction trong test.
- Giải thích gọn tại hướng dẫn nâng cấp VI/EN và/hoặc `tools/README.md` khi cần mô tả field. Nếu sửa Markdown hướng dẫn, được dựng đúng hai HTML nâng cấp và hai START_HERE nhúng cùng chương bằng generator hiện có; so skeleton để không đổi chương khác. Không dựng lại trang không đổi hoặc sửa generator.
- STATE/HANDOFF để bàn giao. Không sửa app.py/app_ui, merge_center, transaction, schema/.cvf/pins, profile/native/PROJECT thật, release_templates, nguồn/sổ thật, VERSION/MANIFEST repo/README người dùng. Không cài dependency hoặc sửa cấu hình global/admin/CVF cha.
- HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`, worktree dirty nhiều tranche; baseline Worker lấy trước sửa. Không reset/stash/clean/stage/commit/push/release. Manifest chỉ được dựng trong fixture sạch để tạo package đầu vào, không trên repo/project thật.

Baseline raw SHA-256 tại audit:

| File | SHA-256 |
|---|---|
| `tools/upgrade_package.py` | `7ff71fcd2addd92ac432aaaea956b94e96f46188af4027d3e7bbe9de9e3d19f1` |
| `tools/merge_center.py` | `9ff2f48731cb56e752d8dc7eb838267b1bfad2c284a3e56025b232fdca4ad9ec` |
| `tools/transaction.py` | `4328586a789298684c9b9fb748bbc5a64eab493bc59a336fd40be0252966cbc8` |
| `tests/test_workflows.py` | `343b7e0b20ff515479f3e83f4e6fd8b598a8e91c15e48fe99f6579c6a2bed13a` |
| `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md` | `8dc871e319af038887a7b8eaf009b37d0872970fe43de5f425cae11cc17b90f3` |
| `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md` | `fca6e7e3ea3a9e28a5695814143963950a8ae02b4de5aff8687b3c9e00953f88` |
| `MANIFEST.sha256` | `034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6` |

File khác baseline thì đối chiếu đúng delta, không khôi phục bản cũ theo bảng.

## Acceptance D-01a

| Ca | Bằng chứng cần có trên dữ liệu giả/thư mục tạm |
|---|---|
| Cùng version, khác package | Hai package cùng VERSION nhưng một file package đổi: real CLI preview nói rõ cùng nhãn/nội dung baseline khác; structured metadata phân biệt được. Preview không ghi; apply cập nhật đúng theo plan, không tăng VERSION giả. |
| Cùng baseline | Map entry như nhau, chỉ khác thứ tự/EOL của MANIFEST: identity bằng nhau, không báo nội dung package mới. Kiểm helper và ít nhất một luồng CLI hợp lệ; không monkeypatch compatibility guard để tạo ca dương. |
| Baseline bằng nhau, project có sửa riêng | Giữ đúng bản user và các kết luận kept/conflict hiện có; identity không gọi project sạch/đã đồng bộ hoặc bỏ qua bootstrap/index/file còn thiếu. Có ca cùng baseline nhưng thực sự còn thao tác, không short-circuit plan theo identity. |
| Khác nhãn/chưa xác định | Khác version hiển thị đúng; malformed/thiếu/duplicate manifest không được cấp identity đáng tin từ nhãn. Giữ refusal/no-write của owner, không migration hoặc rebaseline ngầm. |
| Bảo toàn khi upgrade thật | Fixture có nguồn/output/archive, STATE/HANDOFF/index, profile đã chọn hoặc hỏng, marker runtime user và private skill: so raw bytes trước/sau preview/apply. Chỉ package files/metadata/giao dịch đã dự kiến được đổi. Profile hiện có giữ nguyên, không reset hoặc tạo `.new`, không suy quyền từ prose. |
| Derivative shared của C-01 | Fixture có custom shared không còn trong package mới: ghi đúng điều hiện có (`obsolete`/giữ file/index nếu vậy), kiểm bytes còn. Không tuyên ownership/khả năng xuất/native/upgrade lâu dài đã được giải quyết chỉ vì file không bị xóa. Bất kỳ mất dữ liệu nào là blocker để trả amendment, không sửa ngoài scope. |
| Xung đột `.new`/compatibility | `.new` đang sửa khác bản package không bị ghi đè; keep/no-op/repeat giữ hành vi. Giữ refusal `.cvf`/schema không hỗ trợ dù --force. Không bắt upgrade parse/migrate workbook hoặc profile tương lai mà owner chỉ bảo toàn như dữ liệu opaque; tách “giữ bytes” khỏi “đọc được schema”. |

Tất cả apply/downgrade/manifest chỉ trên fixture. D-01a không thêm downgrade/migration support; không gọi một ca preview hoặc giữ bytes là đạt toàn T39. Nếu thiết kế helper đòi sửa parser/plan/transaction/quyền để đạt mục tiêu, trả ca cụ thể và amendment trước tác động đó; không hạ acceptance hoặc âm thầm mở scope.

## Kiểm và bàn giao

- Chạy test mới và hồi quy hẹp `tests.test_workflows.Workflows.test_upgrade_preview_apply_and_repeat`, `test_upgrade_preserves_pending_merge` cùng lớp; `tests.test_execution_profile.Delivery.test_upgrade_keeps_existing_profiles_and_bootstraps_missing_one`; `tests.test_package_v3.Lifecycle.test_upgrade_of_a_coherent_v3_project_is_a_no_op_and_takes_readable_changes_by_three_way` và `tests.test_package_v3.Lifecycle.test_upgrade_refuses_every_unsupported_target_even_with_force_and_changes_nothing`. Dùng `PYTHONPATH=tests` khi import trần cần; không chạy toàn module/fullsuite/fullgate/browser/Office/release chỉ để lặp evidence.
- Kiểm preview không tạo runtime bằng target hiện có `tests.test_transactions.Transactions.test_preview_and_dry_run_write_nothing_and_create_no_runtime` hoặc assertion tương đương trên real fixture mới; không dựng lại transaction suite.
- Tự xem delta so baseline, đối chiếu từng ca; lỗi cụ thể sửa đúng chỗ và kiểm đúng phần. Công cụ/file lỗi thử lại tối đa một lần rồi báo giới hạn. Phân biệt pass/skip và source trước/sau sửa; không cộng nhiều lượt thành fullsuite cuối.
- Giữ EOL từ đọc tới ghi, file mới theo .gitattributes; `git diff --check`, `python -B tools/check_package.py --check-eol <đúng file chạm> --result-json`. Nếu dựng HTML, `build_guides_html.py --check` và xác nhận chỉ trang/chương được phép thay đổi, không visual QA giả.
- HANDOFF: cấu hình thực, shape metadata đã chốt trước code, file/hash/delta trước–sau, lệnh/kết quả và giới hạn, điều chưa kiểm của ownership/P4/migration. STATE đúng8heading/khoảng60dòng. Bàn giao **IMPLEMENTED_PENDING_REVIEW — D01A_ONLY**; Worker không đóng D-01/P4/T39/R7, không đổi verdict roadmap.

C-02/T37–T38 vẫn PILOT_NOT_RUN; D-02/activation/release và x14 không mở từ đây. Sau review D-01a, Orchestrator mới chốt phạm vi thiết kế P4/D-01b theo bằng chứng writer, không hứa undo/xóa an toàn chưa có.
