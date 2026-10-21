# Workorder D-01c — Lưu `.new` khỏi danh sách chờ, giữ bản hiện hành

Ngày giao: 20/10/2026. Trạng thái: ACCEPTED_WITH_LIMITS — D01C_GUIDES_ONLY (Codex review20/10; evidence và giới hạn tại HANDOFF đầu). Claude thi công, operator chọn model/effort (gợi ý roadmap8.4 Sonnet5.5 High); Codex điều phối/review độc lập. Ghi cấu hình thực, không quy effort thô thành mức có tên. Không gọi agent phụ, provider/AI CLI/API, mạng hoặc host thật trong lượt thi công.

## Mục tiêu và phạm vi nghiệm thu

D-01a/P1 và D-01b subset đã ACCEPTED_WITH_LIMITS. D-01b giữ `.new` nên sau dùng bản mới/tự sửa/giữ current, người dùng chưa kết thúc được pending trong ứng dụng. Nâng cấp sau có thể để lại candidate cũ hoặc bị chặn bởi pending khác nội dung. D-01c thêm một thao tác rõ: **giữ nguyên current, lưu nguyên file `.new` khỏi vị trí đang được scan**. Sau khi user chọn current cần giữ, pending được chuyển vào archive, không xóa bytes.

Chỉ đúng `REPLACE_ALLOWLIST` tám guide Markdown của D-01b; current và pending phải tồn tại, là text thường trong giới hạn reader/diff. Hỗ trợ cả cặp giống nhau sau replace và cặp khác nhau khi giữ/tự sửa current. Không áp dụng file điều khiển, code, HTML, profile, source/index, packs/skills, MANIFEST/VERSION hoặc native. Không tự xác minh nội dung current đúng, candidate mới nhất, MANIFEST sạch, quyền hay acceptance.

Đây là phần kết thúc pending **cho tám guide**. P4 toàn bộ/D-01/T39/R7 vẫn OPEN, gồm file điều khiển và các ca lifecycle chưa nghiệm thu; không đổi tiêu chí P4 để nhận subset. Không tự đóng D-02/C-02, release hoặc x14.

## Thiết kế đã chốt và file owner

- Đọc AGENTS/STATE/đầu HANDOFF, workorder này và roadmap8.3–8.4/P4. Owner `tools/merge_center.py`; adapter `tools/app.py`, `tools/app_ui.html`; test mới thành lớp riêng tại `tests/test_panel.py`; ghi chú gọn `tools/README.md`; STATE/HANDOFF để bàn giao. Không refactor các owner khác.
- Dependency chỉ đọc: transaction hỗ trợ ghi/create, không delete; commit dọn backup tạm. `native_agents.retire` đã có mẫu Windows no-replace `os.rename`, `transaction.held`, kiểm lại binding rồi quan sát source/destination kể cả khi lỗi. Không gọi/import lifecycle native để xử lý merge, không sửa native hoặc transaction.
- Chốt **hai bước có thể gián đoạn**: transaction lưu snapshot/record trước; sau verified commit mới thực hiện một rename `.new` vào archive. Không thêm operation delete/move vào transaction, generic journal/engine/registry hoặc rollback mới. Không tuyên hai bước nguyên tử hay chống mất điện bằng fsync.
- Tự động chuyển chỉ trên Windows, cùng filesystem, dùng đúng một `os.rename`. Không fallback `os.replace`, `shutil.move`, copy+xóa/unlink, move-back hoặc nâng quyền. Platform khác trả unsupported, vẫn xem/copy đường dẫn được. `os.rename` trên POSIX có thể thay đích nên tuyệt đối không chạy nhánh này ở đó.

## Hợp đồng preview, apply và quan sát

### Preview riêng, không tự nối sau replace

- Preview finish trả path/pending chính xác, hai raw SHA-256 từ chính buffer đã đọc, diff cùng buffer, eligibility/lý do và `finish_id`. ID server sinh dạng `finish-` + UUID hex32; preview không tạo file/runtime/log. ID chỉ để tìm lần thao tác, không grant, token bí mật hoặc bằng chứng đã được review. Hash cũng không cấp quyền.
- Dùng lại kiểm path chính xác/managed membership/regular UTF-8/NUL/size/row của D-01b, giữ từ chối alias/traversal/drive/UNC/ADS/link/junction. Cặp identical được finish nếu môi trường hợp lệ; khác với replace identical no-op. Lỗi đọc/kiểm không được coi là missing.
- Kiểm môi trường `incomplete(strict=True)`, archive/runtime boundary như owner; journal không đọc/không hiểu hoặc giao dịch dở chặn preview/apply finish. Observation đọc bên dưới vẫn dùng được để báo tình trạng, không tự resume. Không hash rồi đọc buffer khác để lưu.
- Tách nút **“Lưu .new và kết thúc chờ”** khỏi “Giữ bản của tôi” đang chỉ đóng preview và khỏi “Dùng bản mới” của D-01b. Màn xác nhận nói rõ current sẽ giữ nguyên, `.new` chuyển vào archive, vẫn lấy lại được bằng tay, MANIFEST/HTML không được cập nhật. Khi current khác candidate phải hiện diff đầy đủ trước xác nhận; không bắt hai hash phải bằng nhau.
- Sau replace hoặc tự sửa, phải preview finish **mới** rồi click xác nhận riêng; không dùng hash trước replace, không auto-finish, không đổi ý nghĩa nút Giữ cũ. Sequence guard cả legacy diff và route mới; cancel/đóng sheet/response cũ không bind nhầm cặp. Click một lần/in-flight guard; không tự retry vì mất kết nối.

### Apply: lưu snapshot rồi mới chuyển pending

1. Client chỉ echo path, hai hash và finish_id. Server coi tất cả là input không tin cậy: so path trong allowlist, validate ID khớp toàn bộ `finish-[0-9a-f]{32}`, tự dựng tên file cố định; không nhận absolute/relative archive path, bytes hoặc txid tùy chọn từ client. Không cần registry xác thực đã phát ID; ID đúng format cũng không thay các kiểm dữ liệu/quyền hiện có.
2. Server capture lại cặp/đối chiếu hai hash, strict journal và ranh giới; stale thì chặn trước snapshot write. Current không bị sửa bởi thao tác này ở bất cứ bước nào. Không tự tăng grant từ ready/MANIFEST/record/hash. Candidate có thể cũ hoặc đã sửa tay; user quyết giữ current, không gọi candidate là bản package mới nhất.
3. Archive riêng `.agent/merge-backups/<finish_id>/` với `current.txt`, `incoming.txt`, `record.json`, và slot **chưa tồn tại** `pending-retired.txt`. Record tối thiểu schema riêng mô tả finish, id/path/hai hash/archive transaction id, không nội dung/absolute path/user identity/quyền. Giữ schema record D-01b nguyên trạng; record mới không phải policy/receipt/acceptance.
4. Một Transaction hiện có `merge_finish_archive`, prune=False, tạo độc quyền ba file snapshot/record (`expected_before=None`, `create_exclusive`), **không thêm current hoặc pending vào ops**. Dùng đúng hai buffer đã kiểm. ID collision/slot chiếm trước phải chặn, không overwrite/autođổi ID/reuse archive. Được lập Transaction trước để lấy txid vào record, không chạy trước mọi preflight cần thiết.
5. Chỉ rename sau khi `run()` hoàn tất, journal quan sát được `committed` và snapshot/record kiểm raw hash/bytes đủ. Nếu fault dù đã ghi cả ba file nhưng journal còn dở hoặc commit không chứng minh được: không rename. Trả txid/finish_id/archive paths/trạng thái thật để user dùng recovery transaction hiện có; không tự resume/rollback. Resume archive chỉ hoàn tất archive, **không tự rename** về sau.
6. Sau confirmed commit, dùng `transaction.held` giữ parent của current, `.new`, archive/record/slot; guard đầy đủ. Kiểm lại cả hai raw hash, record/snapshot, slot vắng, same-filesystem ngay sát rename. Khi chặn ở bước này, báo snapshot đã lưu nhưng `.new` vẫn pending; không nói chưa ghi gì. Không lập transaction thứ hai để sửa receipt/trạng thái hoàn tất.
7. Một `os.rename(pending, pending-retired)` không replace. Kể cả OS/hook phát lỗi, phải quan sát thực source, slot và current sau tác động. Không suy kết quả chỉ từ ngoại lệ hoặc bool trả về. Nếu candidate đổi sát rename và bytes khác đã bị chuyển, giữ nguyên bytes đã chuyển, báo conflict/unknown; không move-back hoặc xóa cái vừa xuất hiện ở source. Đây vẫn có cửa sổ kiểm→rename, không khóa nội dung; không hứa stronger binding hơn primitive hiện có.

### Quan sát sau tác động và phục hồi chỉ đọc

| Quan sát source `.new` / slot archive | Kết luận tối đa |
|---|---|
| Source vắng, slot đúng candidate hash đã chọn, current vẫn đúng hash đã chọn, ba snapshot/record đúng | finished: pending đã lưu khỏi vị trí live, current giữ. Scan tự hết hàng; không cần sửa MERGE_STATUS. |
| Source còn đúng candidate, slot vắng, current/snapshot/record đúng | still_pending: chưa chuyển, archive đã lưu; không success/no-write. |
| Cả hai có, cả hai vắng, hash sai, current đổi muộn, journal/archive không kiểm được, link hoặc lỗi đọc | conflict/unknown/partial theo evidence; không finished. Giữ mọi file để kiểm tay; trả relative paths và observed state. |

- Sau snapshot commit, **không** hướng dẫn rollback transaction làm undo rename: transaction committed đã từ chối rollback. Chỉ giao dịch archive còn dở mới dùng Resume/Rollback; rollback lúc đó có thể gỡ snapshot đã ghi và pending live chưa được chuyển. UI phân biệt phase/tx state, không dùng một thông điệp partial cho mọi tình huống.
- Thêm route observation chỉ đọc nhận ID định dạng hợp lệ + binding cặp preview (path/hai hash), tự dựng vị trí cố định và kiểm record/buffers/journal/file thực; không lấy path trong record chưa kiểm làm locator tùy ý. Trả status/hash/relative locator, không nội dung; record không cấp quyền retry. Không mutate hoặc tự hoàn tất khi user mở status.
- UI giữ ID/locators từ preview để nếu mất response có thể **Kiểm lại kết quả** qua observation đúng lần thao tác, không gửi lại apply. Sau restart mất context, người dùng có thể tìm record dưới thư mục archive đã nêu và lấy file bằng tay; không hứa tự phục hồi mọi phiên hay thêm persistent registry/auto-discovery.
- Snapshot transaction dở hoặc chỉ mới chuẩn bị thư mục: observation phải báo đúng phase còn dở/chưa chuyển; source vẫn pending không suy “đã kết thúc”. File/journal thiếu/hỏng không tự coi là completed. Sau rename thành công rồi exception/mất response, observation có thể xác nhận finished nếu đủ tất cả evidence, không cần receipt cập nhật.
- Phục hồi phạm vi này vẫn là lấy current/incoming/pending-retired bằng editor rồi lưu thành file mới. Không tự đè current hoặc tái tạo `.new`; không Undo, xóa archive/retention hoặc cleanup MERGE_STATUS. Nếu `.new` mới xuất hiện sau finish, scan hiện lại theo bytes live; không dùng record cũ che hàng hoặc tự dọn.
- Route preview/observe không log/runtime/file-write, vẫn host/token checks chung. Apply có journal archive và kết quả phase rõ; không bắt thêm ops log. Map envelope `changes` theo thực tế: snapshot có thể đã ghi dù rename thất bại. Header UI không gọi nội dung đã merge/đúng hoặc toàn P4 resolved chỉ vì không còn `.new`.

## Acceptance trên fixture và kiểm hữu hạn

| Ca | Evidence bắt buộc |
|---|---|
| Keep/identical/manual | Cả tám guide: current != candidate và current == candidate đều finish được theo click; current nguyên raw bytes/EOL, pending chuyển vào slot nguyên bytes; hai snapshot/record kiểm đủ. Scan hết đúng hàng; MANIFEST/MERGE_STATUS/HTML/user markers giữ. |
| Luồng D-01b→finish | Replace còn .new như cũ; finish phải preview lại. Candidate thay sau replace, current sửa tay hoặc giữ current ban đầu đều phải thấy/đối chiếu đúng pair mới, không dùng token/hash cũ. Giữ cũ chỉ đóng vẫn 0write. |
| Stale/refusal | Hai hash stale riêng, alias/traversal/ADS/case/ID sai định dạng/path archive giả, missing/binary/large/truncated, scope ngoài8guide, runtime/archive/pair junction, unreadable/unfinished journal: chặn đúng phase, không ghi ngoài root; symlink không đo được báo giới hạn thật. |
| Platform/collision | Non-Windows/same-volume không chứng minh được: unsupported/refused không rename/fallback. Archive/retired slot đã có: giữ nguyên, không retry ID; file bị khóa và rename failure giữ live pending và archive đã commit. Không generic unlink/replace/move trong nhánh finish. |
| Archive fault | Fault sau snapshot đầu, sau cả3write nhưng trước journal committed, resume/rollback ở fixture riêng: pending live chưa rename, current không đổi; không return finished hoặc chỉ dẫn recovery sai phase. |
| Move/observation | Hook trước/sau rename, exception sau move, response mất: quan sát phân biệt các ô bảng trên. Candidate đổi ngay trước rename, current đổi muộn, source xuất hiện lại, destination bị chiếm sau preview: giữbytes thật, không xóa/move-back; không success giả. Một observation không đổi snapshot toàncây. |
| UI/API | Host/token/read-only route, cancel/slow legacy & finish response/cặp khác, apply chỉ click sau preview, doubleclick, network unknown→observe không resend, phase pending/partial/committed-unknown đều có lời đúng VI/EN. Chạy JS có dispatch/async thật bằng harness hoặc browser; không chỉ assert chuỗi. |
| Upgrade/verify thật | Fixture minimal package có MANIFEST nhất quán A→B conflict→replace hoặc keep→finish→C upgrade. Candidate B sau replace verify có thể khớp; keep/manual có thể lệch. Không còn stale .new B chặn C; nếu current user khác baseline thì C tạo candidate mới đúng engine cũ. Archive finish và D-01b trước đó giữbytes. Preview upgrade không ghi. Không monkeypatch compat guard để pass; nêu minimal/no.cvf chưa full lifecycle. |

Chỉ fixture/thư mục tạm; không apply/rename/archive/runtime trên repo/project thật. Không đổi upgrade/transaction/native để ép acceptance. Khó khăn cần đổi schema/quyền/native/generic engine hoặc mở allowlist thì trả blocker+amendment trước tác động.

Chạy lớp test finish mới + các lớp MergeReplaceApply/MergeReplaceUiScript/MergeComparison hiện có + `tests.test_workflows.Workflows.test_upgrade_preserves_pending_merge`. Reuse fault/helpers; chọn thêm target trực tiếp nếu có delta cần, không mặc định fullmodule/fullsuite/fullgate hoặc lặp evidence. Không network/provider/Office/release build; không claim visual QA từ node test.

## Bảo toàn và bàn giao

HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`, worktree dirty. Lấy baseline trước sửa từng owner, không dùng HEAD diff làm Worker delta; không reset/stash/clean/stage/commit/push/release. Không source/project/schema/.cvf/pins/native/global/admin/CVF cha/MANIFESTrepo/README người dùng. Archive id/record trong thiết kế là artifact tính năng trên fixture, không tạo grant/profile/receipt thật tại repo.

SHA-256 raw tại giao việc:

| File | Baseline |
|---|---|
| tools/merge_center.py | f053013771b6d1a12c7bca4d48f0b698219582a7187c2b3f310f8be47f19d36a |
| tools/app.py | a8d07704dbf6909c3ed39c829c029eef380b59849d466308446872e8e337a6e2 |
| tools/app_ui.html | 6b4a9bcb5d196594efb28d9260b83f66171516413984ee628712593304999d7d |
| tests/test_panel.py | 01c7369aec9a5cf5398711d4f2e2e646027650d52da344034f98f4e5ce4bf970 |
| tools/README.md | 1b0d2a3d99ca4959dd1905b41af9c1b6364b95afb85b2119c3be6d431bf6105c |
| tools/transaction.py — giữ | 4328586a789298684c9b9fb748bbc5a64eab493bc59a336fd40be0252966cbc8 |
| tools/native_agents.py — giữ | e5405e3a971739e0e44741a27d8d9f03ed3b9ed901972806faaa300d9a3aad8e |
| tools/upgrade_package.py — giữ | 13cf5d0cd6e3c2461e0fb1bdd4dd29579f4dbe4f0ad48422020979ab44951226 |
| README.md — giữ | 96585b2ae22cc8f145db1f5c4b04136babc43857ca3423d30bdf3ba397ad3c49 |
| MANIFEST.sha256 — giữ | 034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6 |

Khác hash thì đối chiếu đúng delta, không khôi phục theo bảng. Tự xem diff, kiểm đúng rủi ro; lỗi cụ thể sửa đúng chỗ/kiểm lại đúng chỗ, công cụ lỗi thử lại tối đa một lần rồi ghi phần chưa làm được. Giữ EOL cũ, file mới LF; `git diff --check` và `python -B tools/check_package.py --check-eol <đúng file chạm> --result-json`.

HANDOFF: model/effort thực, shape preview/observe/result đã chốt, phase và rule phân loại, before/after hash/delta, lệnh/pass/skip tại source cuối, fault/rename/read-only/lifecycle evidence và race/platform/manual-recovery limits. STATE giữ tám heading/khoảng60dòng. Bàn giao **IMPLEMENTED_PENDING_REVIEW — D01C_GUIDES_ONLY**; không tự nhận verdict hoặc đóng toàn P4/D-01/T39/R7. Reviewer độc lập soát archive→rename→observe trước khi nhận subset.
