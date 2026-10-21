# Workorder D-01d — Kiểm chứng nâng/hạ cùng schema trên project v3 có dữ liệu

Ngày giao: 20/10/2026. Trạng thái: ACCEPTED_WITH_LIMITS — D01D_INTEGRATION_ONLY (Codex review20/10; evidence/giới hạn tại HANDOFF đầu). Claude thực hiện, operator chọn model/effort (gợi ý roadmap8.4 Sonnet5.5 High); Codex review độc lập. Ghi cấu hình thực quan sát được, không suy effort. Không agent phụ/provider/AI CLI/API/mạng/host thật trong lượt này.

## Khoảng trống và điểm dừng

D-01a/b/c đã nhận WITH_LIMITS đúng subset. Hiện có lifecycle v3 riêng (`tests/test_package_v3.py`, fixture qua release build), bảo toàn D-01a trên package tối thiểu/workbook opaque, và D-01c A→B→C tối thiểu không `.cvf`. Chưa có bằng chứng kết hợp **package projected v3 thật + project VI/EN + workbook B-01/B-02 có dữ liệu thực của fixture + nâng/hạ cùng schema + archive merge đã tạo bởi owner**.

D-01d chỉ thêm kiểm tích hợp và ghi kết quả, không triển khai migration, mở writer/allowlist P4 hay sửa runtime để làm test đạt. Khi hoàn tất vẫn chưa toàn T39/D-01/P4/R7; schema khác, file điều khiển, host và release giữ giới hạn. Phát hiện mất dữ liệu/vi phạm quyền thật thì bàn giao blocker để tách tranche sửa, không bỏ assertion hoặc né compatibility guard.

## Owner, fixture và phạm vi sửa

- Đọc AGENTS/STATE/đầu HANDOFF, workorder này, roadmap8.3–8.4/T39. Tạo **một** module `tests/test_upgrade_lifecycle.py`, lớp độc lập, không kế thừa `Rc` hoặc fixture tự chạy release build/fullgate. Reuse shape/helper nhỏ khi phù hợp, không chép engine hay sửa hàng loạt test cũ.
- Dependency chỉ đọc: check_package.materialize, new_project/init/upgrade, execution_profile, library/library_sync/artifacts, merge_center, native_agents; test tham khảo `test_execution_profile.Delivery`, `test_artifacts.Base`, `test_panel.MergeFinishLifecycle`, `test_workflows.UpgradeIdentity`. Không chạy tất cả các module này chỉ để lấy fixture.
- Được sửa module mới và STATE/HANDOFF. Có thể thêm một ghi chú ngắn tại `tools/README.md` nếu kết quả cần diễn giải; không đổi hướng dẫn agent/gate/roadmap verdict, không dựng HTML. Không fixture binary/manifest/evidence dump mới trong repo. Dữ liệu, workbook, request JSON, package và archive đều ở tempfile.
- Cài dependency không thuộc lượt này. Nếu thiếu openpyxl/jsonschema hoặc Windows cần cho finish, ghi NOT_CHECKED/skip rõ; không gọi đó là pass đủ acceptance. Không gọi host thật, tạo/export role native thật hoặc đánh giá chất lượng model.

## Hợp đồng fixture projected v3

1. Dùng `check_package.materialize(..., branding=False)` trong tempfile, với delivery/compatibility checks thật. Đây là package bytes sau projection, **không** phải official release/ZIP hoặc bằng chứng đã qua fullgate. Không copy thô repo làm package, không đưa release_templates/runtime maintainer/logo/font riêng sang fixture, không `--skip-check`/monkeypatch guard.
2. Từ package đó tạo A/B sạch, nhãn version giả phân biệt được thứ tự (ví dụ `90.0.0`/`90.0.1`, chỉ là fixture). B chỉ thay VERSION và một cặp guide VI/EN thông thường; giữ toàn `CVF_MACHINE` và `CVF_DEPENDENCIES` đúng raw bytes, pin/closure vẫn khớp. MANIFEST chỉ được dựng lại bằng owner trong A/B fixture; không rebaseline project đã có dữ liệu để giấu thay đổi.
3. Chạy `new_project.py` từ A để tạo project VI và EN thật, init theo owner hiện có; chạy upgrade bằng CLI package nguồn sạch (không chạy code tùy ý của project đích). Kiểm project có closure v3 hợp lệ và PACKAGE_INFO.language đúng, profile/PROJECT owner hợp lệ theo khung hiện có. Không đếm label version hoặc file `.cvf` tồn tại là đủ proof compatibility.
4. Seed dữ liệu giả qua owner thật trước preview upgrade: thư viện nguồn + nội dung B-01 + registry/quan hệ B-02; profile valid có lựa chọn rõ; STATE/HANDOFF/index, private/custom shared skill; nguồn, nháp/output/archive và marker runtime. Nội dung nguồn chỉ là fixture trung tính, không dữ liệu cá nhân/pháp lý thật.

## Bộ dữ liệu cần bảo toàn

- Workbook thật từ template của package fixture, không bytes giả có tên `.xlsx`. Dùng sync/content/artifact writers hiện có để có ít nhất hai SourceID, một nguồn revision tăng sau đổi bytes, một Content EntryID và quan hệ nguồn → phụ lục → kết quả (hai ArtifactID/revision thực từ owner). Attestation/user confirmation nếu fixture cần chỉ là mô phỏng; không suy đã có user acceptance thật.
- Trước nâng/hạ, chốt raw SHA-256 workbook và projection dữ liệu đọc bằng owner: source ID/revision/hash, content EntryID/source revision/basis/limits, artifact ID/revision/hash và dependencies. Sau mỗi thao tác đọc lại bằng reader thật, không chỉ assert workbook mở được hoặc số dòng bằng nhau; reader không được save lại workbook rồi tự làm đổi bytes.
- Profile/PROJECT/STATE/HANDOFF/INDEX/SKILL_INDEX và private/shared skill giữ đúng raw bytes trong các ca không có thao tác được plan. Nếu owner có append index rows thì phải nêu rõ delta dự kiến; không mặc định đòi file không đổi trong khi đã chủ động thêm skill package mới. Fixture A/B không cần thay inventory skill để tạo delta đó.
- Tạo ít nhất một archive D-01b và một archive D-01c bằng owner thật **trước** A→B; được seed cặp giả trên guide thứ hai không đổi giữa A/B, ghi rõ cặp đó không do upgrade tạo. Chụp archive files/raw hashes, giữ xuyên upgrade/downgrade. Không sửa lại record hoặc giả receipt để tạo ca dương. Trong ca guide A→B chính có thể tiếp tục dùng replace/finish như mục acceptance.
- Native candidate/receipt của fixture, nếu seed, chỉ là marker opaque phục vụ giữ bytes; không gọi đó là native đã đăng ký/usable hoặc proof R4. Có thể đọc status của owner để ghi giới hạn, không kích hoạt/đổi grant.
- Bảo toàn marker runtime/native receipt và merge-backups cụ thể; không assert toàn runtime bất biến sau apply vì transaction được thêm journal và có prune. Preview/refusal thì snapshot **toàn cây**, kể cả runtime, phải không đổi.

## Ma trận kiểm hữu hạn

| Nhóm | Evidence bắt buộc |
|---|---|
| **A→B, VI/EN** | Hai subcase project thật có bộ dữ liệu trên. Preview CLI không ghi toàn cây. Apply đi qua compat guard thật; VERSION/PACKAGE_INFO/MANIFEST theo plan, workbook raw và semantic projection giữ; user files/skills/markers/archive giữ. Guide có thay user + package thì sinh `.new` đúng bytes, không đè current. Dùng D-01b replace rồi D-01c preview mới/finish, kiểm raw archive/current/pending đúng. `--verify` dùng như diagnostic MANIFEST, không ép toàn project sạch khi có user/shared chỉnh riêng. |
| **B→A, cùng schema** | Trước hết preview và apply **không --force** đều từ chối downgrade, snapshot toàn cây giữ. Có --force: preview không ghi, apply dùng plan hiện có; compat/pins vẫn giữ, dữ liệu user và mọi archive giữ bytes. Guide đã bằng baseline B có thể update về A, guide user khác baseline có thể tạo `.new`; assert đúng nhánh từ dữ liệu fixture, không đòi force là overwrite/migration. Đọc lại workbook IDs/revisions/links và so raw bytes sau downgrade. |
| **Future user profile, một clone** | Trên clone có dữ liệu, dùng profile tương lai theo shape test owner hiện có. Upgrade cùng v3 giữ nguyên opaque profile, không tạo profile `.new`/grant/reset; `execution_profile` status/config thật nhận unsupported/refused và không ghi. Không bắt upgrade từ chối mọi file user schema lạ; giữ bytes không chứng minh schema được đọc/đã migrate. Không chế workbook schema tương lai không có contract để bịa kết quả. |
| **Ranh giới hỗ trợ, một clone** | Clone project giàu dữ liệu có một `.cvf` không hỗ trợ/mixed hoặc machine bytes lệch; preview và --apply --force vẫn từ chối, snapshot toàn cây giữ. Reuse một ca rõ từ test_package_v3, không lặp ma trận exhaustive. Chỉ thêm pending `AGENTS.md.new` giả nếu cần kiểm scope: replace/finish vẫn unsupported, current/pending giữ; không mở allowlist hoặc coi manual editor là native authority. |

Không nhân mọi biến thành tổ hợp. Hai subcase VI/EN cho roundtrip và hai clone negative là đủ. Giữ nhãn liệu có phải schema migration: đây chỉ **same-schema version upgrade/downgrade**, không T39 tổng thể hoặc nâng/hạ tùy phiên bản lịch sử.

## Kỳ vọng trạng thái phải trung thực

- Native owner bind cả PACKAGE_INFO (`native_agents._inputs`): upgrade thay metadata có thể làm status **STALE** dù bytes native/receipt/profile giữ. Không ép status bất biến, sửa receipt hoặc tự tái kích hoạt để test đạt. Ghi trạng thái đã đo và phần chỉ suy từ owner; marker opaque không chứng minh status thật.
- Observe D-01c cũ bind current hash và journal committed: sau guide đổi/downgrade hoặc journal bị prune, kết quả có thể không còn finished. Acceptance là archive nguyên bytes + observation conservative đúng binding hiện tại, không phải record cũ vĩnh viễn xác nhận project đã xử lý xong.
- Custom shared bị bỏ khỏi package mới hiện được giữ/obsolete; không gọi giữ bytes là đã giải quyết ownership lifecycle hoặc quyền export/native. Không thêm ca bỏ shared rồi hứa automatic migration.
- Workbook/profile/source opaque khác với dùng được: workbook positive phải đọc dữ liệu thật sau upgrade; profile future chỉ nhận bằng chứng bảo toàn/refusal. Nguồn/nội dung/attestation của fixture không chứng minh dữ liệu thật đã được kiểm hay user chấp nhận.
- P4 ngoài tám guide vẫn read-only/copy/manual theo owner; `.cvf` machine đổi có thể bị guard từ chối trước khi có `.new`. Không dùng evidence guide để nhận resolve AGENTS/CLAUDE/PROJECT/quyền/pin hoặc Undo.

## Chạy, kiểm và bàn giao

- Chạy module mới duy nhất qua `PYTHONPATH=tests PYTHONUTF8=1 python -B -m unittest -v tests.test_upgrade_lifecycle`. Dùng CLI thật trong fixture cho new/init/upgrade/downgrade/verify; owner API thật được dùng để seed/read workbook và merge snapshot. Không chạy lại full package_v3 hoặc build_release/fullgate/browser/Office/paidproof. Target cũ chỉ thêm nếu đã sửa helper cũ theo amendment được chốt.
- Tự xem test assertions để không tự nuốt lỗi/skip, sửa expected theo output hay monkeypatch compatibility để qua. Nếu lộ blocker sản phẩm: lưu testcase có thể chạy lại, ghi source/hash/reproducer/expected vs actual trong HANDOFF, bàn giao **BLOCKER_FOUND — D01D_INTEGRATION_ONLY**; không sửa runtime/schema/quyền ngoài scope hoặc đổi verdict đã nhận trước.
- Giữ EOL, file mới LF theo attributes; `git diff --check` và `python -B tools/check_package.py --check-eol <file chạm> --result-json`. Công cụ/file lỗi thử lại tối đa một lần rồi báo phần chưa làm được; lỗi cụ thể sửa đúng chỗ/kiểm đúng phần, không vòng test vô hạn.
- HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`, worktree dirty; lấy baseline trước sửa, không coi HEAD diff là delta lượt này. Không reset/stash/clean/stage/commit/push/release. Không nguồn/sổ thật, schema/.cvf/pins/PROJECT/profile/native thật, global/admin/CVF cha hoặc MANIFEST repo/README người dùng.

SHA-256 raw owner **chỉ đọc/giữ** tại giao việc:

| File | Baseline |
|---|---|
| tools/check_package.py | 4c620aea2a154ee738a4696139c76e17ee0f97e51cd14b139b2d536d6252c1bf |
| tools/upgrade_package.py | 13cf5d0cd6e3c2461e0fb1bdd4dd29579f4dbe4f0ad48422020979ab44951226 |
| tools/merge_center.py | 09fcd5890257be7be3dbf5324512539a71361dc3f118709877ce4300920ef1e0 |
| tools/execution_profile.py | cbfa5ad1b4272b9601e30dbce01694de9fab1a3ed3478b4d97f188bc4f84a323 |
| tools/library.py | ab712f699da37277f8693aa1ffa8c3cf2899a8c60af550f17a44bfe5c7e70756 |
| tools/library_sync.py | 3dae368d7d2c82b8a2e7021c8c7e3a2ee592bb2693abb1ceb593418e8904ced2 |
| tools/artifacts.py | be315aff047b0d73d0a9d15693ac72049edfbb15e9499bb0163687906f782c1a |
| tools/native_agents.py | e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e |
| README.md | 96585b2ae22cc8f145db1f5c4b04136babc43857ca3423d30bdf3ba397ad3c49 |
| MANIFEST.sha256 | 034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6 |

Khác baseline thì đối chiếu delta thực, không khôi phục theo bảng. HANDOFF ghi model/effort thực, fixture materialize/closure/versions giả, seed qua owner nào, before/after raw và projection workbook, lệnh/pass/skip source cuối, nhánh downgrade/guard/status đã đo và giới hạn. STATE giữ tám heading/khoảng60dòng. Positive đủ thì bàn giao **IMPLEMENTED_PENDING_REVIEW — D01D_INTEGRATION_ONLY**; Codex nhận evidence rồi mới chốt verdict subset. Không tự đóng D-01/T39/P4 hoặc mở D-02/C-02/release/x14.
