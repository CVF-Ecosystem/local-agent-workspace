# Workorder D-01b — Preview và thay một tài liệu, giữ `.new` và bản lưu

Ngày giao: 20/10/2026. Trạng thái: ACCEPTED_WITH_LIMITS — D01B_SUBSET_ONLY (Codex review20/10; evidence/giới hạn tại HANDOFF đầu). Codex điều phối/review; Claude thi công, operator chọn model/effort (gợi ý roadmap8.4: Sonnet5.5 High). Ghi cấu hình thực trong HANDOFF. Không gọi agent phụ/provider/AI CLI/API hoặc mạng trong lượt thi công.

## Mục tiêu và điểm dừng

D-01a/P1 đã ACCEPTED_WITH_LIMITS; không làm lại diagnostic identity. D-01b cung cấp một lựa chọn có ích nhưng hữu hạn: xem đúng cặp tài liệu, chủ động chọn dùng bytes bản mới đã preview, lưu bền cả hai bản trước khi thay current. Giữ `.new`; người dùng có đường dẫn lấy lại bản cũ. Không gọi đây là resolve, undo sau commit, migration hoàn chỉnh hoặc hoàn tất P4/D-01/T39/R7.

P4 gốc vẫn yêu cầu giữ của tôi/dùng bản mới/mở tự sửa, preview và phục hồi. Tranche này chỉ nhận subset bên dưới; việc kết thúc pending an toàn, hỗ trợ file điều khiển và phục hồi tự động vẫn OPEN. Không đổi tiêu chí P4 để khớp subset. C-02/T37–T38 PILOT_NOT_RUN; không mở D-02/release/x14 từ đây.

## Bằng chứng thiết kế và owner

- Đọc AGENTS, STATE, đầu HANDOFF, roadmap8.3–8.4/P4/D-01 và workorder này. Owner tích hợp `tools/merge_center.py`; adapters `tools/app.py`, `tools/app_ui.html`; test tại `tests/test_panel.py` (lớp riêng mới). `transaction.py`, upgrade và lifecycle khác chỉ đọc.
- `merge_center.scan/diff/set_state` hiện quản lý xem và trạng thái unseen/reviewing/ready; ready không phải quyền ghi hoặc kết luận đã resolve. `_pair` chuẩn hóa alias, `_inside` chỉ kiểm lexical; không dùng chúng làm toàn bộ kiểm ranh giới của writer mới.
- Transaction hiện chỉ ghi/create, không delete; backup/staging bị dọn sau commit. Phải tạo **file archive riêng như đích ghi bình thường**, ngoài `.agent/runtime/transactions`, không dựa vào backup tạm. Không sửa transaction/schema/journal, không unlink hoặc rename `.new` ngoài owner.
- `app.open_path` gọi ứng dụng mặc định (`os.startfile` trên Windows); mở script không đồng nghĩa mở trình soạn thảo. Trong bảng merge, dùng xem/copy đường dẫn để tự mở bằng editor; không bổ sung gọi default opener cho loại file tùy ý. Giới hạn sửa opener chỉ tại bảng merge, không đổi endpoint hay các màn khác.
- Helper Sol6.1 Medium chỉ đọc đã phản biện thiết kế: allowlist chính xác thay vì đuôi Markdown; archive create-exclusive kèm expected_before=None; hash trên chính buffer; không giả giảm pending. Chưa có probe runtime cho thiết kế này; Claude phải cung cấp evidence bên dưới.

## Hợp đồng hành vi đã chốt

### 1. Phạm vi tài liệu tự động thay

Chỉ tám path sau, so khớp chính xác, đồng thời phải còn là managed path có `.new` theo owner hiện hành:

```text
docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md
docs/HUONG_DAN_SU_DUNG_VI.md
docs/HUONG_DAN_SKILLS_VI.md
docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md
docs/en/NEW_PROJECT_GUIDE.md
docs/en/DAILY_USE_GUIDE.md
docs/en/SKILLS_GUIDE.md
docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md
```

Current và candidate phải là file thường hiện có, UTF-8 như reader hiện tại chấp nhận, không NUL, trong giới hạn byte/row của diff hiện tại; thiếu current/binary/quá lớn/truncated thì không apply. Không HTML/đuôi thực thi, không khái quát từ `.md`, không tự tìm thêm tài liệu. File hướng dẫn nguồn thay đổi không làm HTML đã dựng tự đồng bộ: nói rõ UI và HANDOFF; không chạy generator trong project đích.

Ngoài allowlist: vẫn có thể xem bằng chức năng diff hiện có; writer mới trả unsupported/read-only. Không coi MANIFEST, ready, grant prose, tên file, input từ client hoặc digest preview là quyền. Tuyệt đối không thay AGENTS/CLAUDE/GEMINI, PROJECT/profile, `.agent` state/quyền, `.cvf`, tools/script, roles, skills/packs, schema, thư viện nguồn/sổ, MANIFEST/VERSION hoặc native qua chức năng này. Archive là ngoại lệ đích mới duy nhất bên dưới.

### 2. Preview chỉ đọc và lựa chọn rõ

- Một helper preview nhỏ trả path chuẩn, raw SHA-256 của current/candidate, eligibility/lý do và các field diff cần dùng. Đọc mỗi file thành buffer có giới hạn; hash và hiển thị từ chính buffer đó. Không hash một lần rồi lấy bytes khác để hiển thị/ghi. Object preview là mô tả snapshot, không receipt/grant hoặc token bảo mật.
- Validate input mới độc lập: từ chối absolute/drive/UNC, `..`, dấu phân cách ngược/alias/segment rỗng, case alias và Windows ADS; không tự strip/lstrip/normalize input bất thường thành path hợp lệ. Kiểm file và parent/runtime/archive không qua symlink/junction bằng owner hiện có; lỗi đọc/kiểm không được coi là missing an toàn. Có thể dùng guard/held, không tự nhận đóng mọi TOCTOU.
- Expose preview qua route chỉ đọc riêng theo mẫu route library/draft đã có: vẫn kiểm host/token như handler chung, không qua `_record`/ops_log. Không tạo runtime, MERGE_STATUS, archive hoặc log khi preview; không sửa endpoint merge_diff cũ ngoài nhu cầu tích hợp được nêu rõ.
- UI ở bảng merge cho preview rồi nút **“Dùng bản mới (giữ .new)”** nếu eligible; phải hiển thị current sẽ bị thay, cả hai bản sẽ được lưu, `.new` còn chờ và HTML chưa được dựng lại. Apply chỉ từ click rõ sau preview; không autoapply khi chọn ready, refresh hoặc mở diff. VI/EN đồng nghĩa.
- “Giữ bản của tôi” chỉ đóng preview/giữ nguyên cả hai file, không gọi merge_state hoặc writer, không báo resolved. “Tự sửa” hiển thị/copy đường dẫn current/candidate và hướng dẫn mở bằng trình soạn thảo; không khởi chạy script. Thay các nút default-open tại riêng bảng merge bằng copy path, giữ các chức năng khác.

### 3. Apply một cặp và archive bền

- Server tự kiểm lại path, allowlist, managed membership, file/size/type, ranh giới và `transaction.incomplete(..., strict=True)`. Thiếu/hỏng journal hoặc có giao dịch dở thì chặn apply, không bỏ qua bằng non-strict. Không nhận archive path/bytes đích từ client.
- Client gửi path + hai hash từ preview. Server lấy current/candidate thành buffer mới, so cả hai hash; stale thì yêu cầu preview lại, không ghi current/archive. Giữ raw bytes/EOL; không merge nội dung hay encode lại.
- Nếu hai buffer giống nhau: no-op, không archive/runtime/đổi MERGE_STATUS; `.new` vẫn pending. API phải phân biệt no-op và đã thay.
- Sinh id mới phía server; archive dưới `.agent/merge-backups/<id>/`, với `current.txt`, `incoming.txt`, `record.json`. Record tối thiểu path chuẩn, hai raw hash và phiên bản record; không nội dung, absolute path, user identity, grant/acceptance hay expiry tự đặt. Không dùng archive làm authority hay registry mới. Đích archive không do client chọn và không bị transaction prune dọn.
- Trong **cùng Transaction**, thêm current.txt, incoming.txt, record.json bằng `action='create_exclusive', expected_before=None`; thêm thay current **cuối cùng**, `expected_before` đúng hash buffer current vừa đọc. Dùng chính hai buffer đã kiểm, không đọc lại để ghi. Collision phải chặn, không overwrite và không vòng đổi id để né lỗi quan sát được. Giữ guards/held hiện có; ghi rõ giới hạn hash-check/replace của transaction.
- Candidate là bản snapshot user đã chọn, không khóa nội dung file `.new` suốt giao dịch. Kiểm lại candidate sát trước run; thay đổi quan sát được thì chặn. Nếu candidate đổi muộn sau capture, tuyệt đối giữ file live đó và archive đúng snapshot đã chọn; không tuyên current luôn bằng candidate live hay cặp file được cập nhật nguyên tử. Không mở engine read-set/lock/delete để che giới hạn này.
- Sau thành công: trả đúng path archive và hash để lấy lại bản cũ; giữ `.new`, MANIFEST, MERGE_STATUS và metadata package nguyên bytes. Scan vẫn liệt kê pending; UI refresh và giải thích rõ. Không sửa entry hash MANIFEST thành bytes user vừa chọn.
- Khi lỗi sau một số archive đã commit: trả trạng thái giao dịch dở/txid/đường phục hồi thật theo transaction, không báo all-or-nothing hoặc no-write. Không tự resume/rollback rồi tuyên success. Resume/rollback do owner hiện có thực hiện; không thêm logic rollback sau commit thành công.
- Phục hồi tranche này là **lấy bản cũ từ archive để tự sửa/lưu thành bản mới**, với hướng dẫn đường dẫn cụ thể; không nút Undo hoặc tự overwrite current. Archive cũng giữ candidate snapshot. Test phải thực sự lấy current cũ thành một file mới trong fixture rồi so raw bytes. Không nói đã nghiệm thu toàn cơ chế phục hồi P4.

## File được sửa và điều cấm

- Chỉ owner/adapters/test nêu trên và ghi chú tính năng gọn tại `tools/README.md` nếu cần; STATE/HANDOFF để bàn giao. Không sửa nội dung tám guide hoặc dựng HTML chỉ vì chúng là allowlist. Không thêm dependency, CLI riêng, protocol chung, file cấu hình/grant/receipt thật, engine hoặc schema mới.
- Chỉ chạy apply, archive, fault/recovery trong thư mục tạm dữ liệu giả; không tạo `.new`/archive/runtime trên repo hay project thật. Không gọi host/provider/paidproof/Office; không fullgate/release. Không sửa các file pinned, native, PROJECT thật, sổ thật, VERSION/MANIFEST repo, README người dùng hoặc CVF cha/global/admin.
- Worktree dirty, HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`. Lấy baseline đúng file trước sửa; không coi HEAD diff là delta của lượt này. Không reset/stash/clean/stage/commit/push.

Baseline SHA-256 raw tại giao việc:

| File | SHA-256 |
|---|---|
| tools/merge_center.py | 9ff2f48731cb56e752d8dc7eb838267b1bfad2c284a3e56025b232fdca4ad9ec |
| tools/app.py | d030b4bc5846937984b04dceb54619e803738299c2b79fccf6bc9eecc7954c32 |
| tools/app_ui.html | 5d165ec7ae3cbd85c1cfd2fea615d5587b38fdf2e25559176b94688da9931774 |
| tests/test_panel.py | a429ed957aef1066890caed1b7d29f191a6077d25f13c9b0381566f28afc87d1 |
| tools/transaction.py — giữ | 4328586a789298684c9b9fb748bbc5a64eab493bc59a336fd40be0252966cbc8 |
| tools/upgrade_package.py — giữ | 13cf5d0cd6e3c2461e0fb1bdd4dd29579f4dbe4f0ad48422020979ab44951226 |
| README.md — giữ | 96585b2ae22cc8f145db1f5c4b04136babc43857ca3423d30bdf3ba397ad3c49 |
| MANIFEST.sha256 — giữ | 034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6 |

Khác baseline thì kiểm delta liên quan, không khôi phục theo bảng. Nếu thiết kế cần sửa transaction/schema/authority hoặc loại file ngoài allowlist, trả ca blocker và amendment trước khi sửa; không âm thầm mở scope.

## Acceptance và kiểm hữu hạn

| Nhóm | Bằng chứng trên fixture thật |
|---|---|
| Preview/giữ/tự sửa | Snapshot toàn cây không đổi, gồm HTTP preview không log/runtime; keep không state-write; copy path không gọi launch. Test dispatch/JS đủ chứng minh click apply phải có preview, không chỉ tìm chuỗi nút. |
| Apply thành công | Cặp guide đủ điều kiện khác raw bytes/EOL: current đúng candidate snapshot; archive giữ đủ bytes cũ/mới và record hash; `.new`/MANIFEST/MERGE_STATUS/nguồn-output-user markers giữ. Scan vẫn pending. Lấy lại current cũ thành file mới, so raw bytes. |
| Scope/refusal | File managed tùy ý ngoài tám path, script/authority/HTML, missing current, binary/quá lớn/truncated, unrecognized path đều không apply; forged hashes/eligibility từ client không vượt kiểm server. No-op không tạo runtime/archive. |
| Stale/ranh giới | Đổi current và candidate riêng sau preview; path alias/traversal/ADS, junction tại pair/archive/runtime, read error, archive collision và journal lỗi/giao dịch dở. Không ghi ngoài project; current không bị đè khi mismatch. Symlink cần privilege mà không chạy được thì ghi skip/reason, không gọi đã đo. |
| Giao dịch dở | Fault sau archive đầu và trước/ở replace current: không mất hai bản, status/txid trung thực. Dùng resume và rollback hiện có ở các fixture riêng; trường hợp user sửa sau lỗi không bị rollback đè. Kiểm bytes cuối và không sửa transaction để làm test pass. |
| Candidate đổi muộn | Hook fixture cho đổi candidate sau capture: giữ nguyên candidate live mới; chỉ apply snapshot đã bind hoặc từ chối nếu quan sát được; archive không pha bytes giữa hai lần đọc, UI không tuyên cặp nguyên tử/đã resolve. |
| UI VI/EN | Eligible và unsupported, success/no-op/stale/partial/error có thông điệp phù hợp; không label Reviewed/ready=resolved, không giảm pending giả, không execute script khi chọn tự sửa. Không tự claim browser visual QA từ test HTML. |

Chạy lớp test mới + `tests.test_panel.MergeComparison` + `tests.test_workflows.Workflows.test_upgrade_preserves_pending_merge` + `tests.test_transactions.Transactions.test_preview_and_dry_run_write_nothing_and_create_no_runtime`. `PYTHONPATH=tests`/UTF-8 khi cần. Reuse fault fixtures/helpers thay vì nhân bản transaction. Chỉ thêm target hồi quy nếu thay đổi cụ thể cần; không fullmodule/fullsuite hoặc red-run hàng loạt.

Tự xem delta thật; giữ EOL file cũ, file mới LF theo attributes. `git diff --check` và `python -B tools/check_package.py --check-eol <đúng file chạm> --result-json`. Lỗi cụ thể sửa đúng chỗ, kiểm lại đúng phần; lỗi công cụ thử lại tối đa một lần rồi báo giới hạn.

HANDOFF ghi cấu hình thực, shape preview/result, delta/hash trước–sau, lệnh/pass/skip ở source cuối, archive/partial/recovery evidence, giới hạn race/HTML/manual recovery và P4 còn mở. STATE giữ tám heading/khoảng60dòng. Bàn giao **IMPLEMENTED_PENDING_REVIEW — D01B_SUBSET_ONLY**. Claude không tự nhận tranche hoặc đổi verdict roadmap; Codex review độc lập writer trước nghiệm thu subset.
