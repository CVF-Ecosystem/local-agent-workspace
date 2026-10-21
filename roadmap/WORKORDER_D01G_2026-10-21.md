# Workorder D-01g — Giữ script hiện hành, lưu pending của hai script package

Ngày giao: 21/10/2026. Trạng thái: **ACCEPTED_WITH_LIMITS — D01G_SCRIPT_FINISH_ONLY, M1 CLOSED**; verdict Codex và review độc lập ngày21/10, giới hạn dưới đây giữ nguyên. Scope/baseline trước thi công bên dưới giữ nguyên.
Claude thi công; operator chọn model/effort, ghi cấu hình thực quan sát được.
Codex giữ orchestrator/reviewer theo PROJECT/roadmap8.3–8.4. Không suy effort từ số thô.

## Verdict Codex 21/10 — M1 đã đóng đúng subset

**ACCEPTED_WITH_LIMITS — D01G_SCRIPT_FINISH_ONLY.** Reviewer độc lập d01_gap_scope
(Sol6.1 Medium, theo quyền operator) xác nhận không có blocker sản phẩm đã xác định
ngăn nhận phạm vi workorder. Codex nhận: REPLACE8/FINISH16, managed split, giữ current,
archive/committed/rename/observe, product không thực thi hai script, lifecycle/UI đã kiểm.
Evidence Reviewer16pass/0skip sau sửa guard;38pass trước sửa test-only giữ riêng, không
cộng thành fullsuite. Source/test/UI còn đúng snapshot đã kiểm;8protected hash khớp.

**NOT_VERIFIED:** raw inverse merge_center về baseline48b4151f; không có toàn preimage.
Lượt đảo trong bộ nhớ cuối vẫn không khớp; không sửa source hay tiếp tục đoán. Đây là
claim lịch sử chưa xác minh, không phải finding product pipeline đổi. Điều kiện phải
trả literal đảo do Codex thêm sau review được kết thúc bằng disposition này; không đổi
acceptance gốc về bảo toàn/hành vi. Không cần Claude săn preimage hoặc chạy lại suite.

Sai lệch Worker gọi `python -B tools/audit_scripts.py --help` vẫn được ghi nhận;
hash/pyc không chứng minh toàn phiên không có tác động phụ. Không gọi lượt thi công
là tuân thủ hoàn toàn. Giữ giới hạn Windows/NTFS/race/phục hồi thủ công/guard in-process;
không nhận toàn P4/T39/schema migration/release hoặc script usable/intake.

Việc kế tiếp theo roadmap mục0.6/M3, không mở D-01h. Phần bàn giao gốc và baseline dưới
đây giữ làm lịch sử, không giao lại D-01g. MANIFESTrepo vẫn không refresh.

## Quyết định phạm vi

D-01f đã nhận WITH_LIMITS bảng phạm vi/gap sau D-01a–e. Bước kế tiếp mở **finish-only**
cho đúng hai script package được giao trong projection hiện tại:

```text
tools/audit_scripts.py
skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py
```

Giữ nguyên current raw bytes; lưu/move pending theo pipeline D-01c/e. Không áp dụng,
import, compile, chạy Python hoặc gọi --help của script current/pending được kiểm.
REPLACE_ALLOWLIST vẫn đúng8guide; FINISH_ALLOWLIST =14path đã nhận + đúng2path trên =16.
Không wildcard tools/skills, không en/ counterparts, không gói đã cài hoặc script tùy ý.
Kết thúc pending không chứng minh script đúng/an toàn/chạy được/đã tiếp nhận hoặc được
phép dùng. Không cấp quyền mới từ finish/scan/manifest hoặc mở cơ chế apply code.

Hai file actual hiện6.877 và23.965bytes, dưới giới hạn262.144bytes/file; không thuộc
CVF_MACHINE/CVF_DEPENDENCIES. Đây là căn cứ phù hợp scope text hiện có, không đánh giá mã.
`delivery_selection()` chọn cả2, nhưng MANIFESTrepo hiện chưa có audit_scripts.py.
**Allowlist không thay managed membership**: current_rel vẫn phải thuộc managed_paths.
Ca allowed-but-unmanaged phải trả not_managed; không refresh MANIFESTrepo để làm test đạt.

Các nhóm khác (pending ngoài16path, pack/custom-shared nói chung, áp instruction mới,
file quyền/native/core/.cvf/schema) vẫn ngoài tranche. D-01f không giao lại; không mở
migration khácschema/P4 tổng thể/D-02/release/x14 hoặc sửa bản v1.8.0.

## Owner và ranh giới sửa

- Đọc AGENTS/STATE, đầu HANDOFF review D-01f và các contract D-01c/e liên quan, workorder
  này và roadmap8.3–8.4. Không đọc toàn HANDOFF/suite hoặc coi HEADdiff dirty là delta.
- `tools/merge_center.py`: thêm tuple scope cố định cho đúng2path, nối vào FINISH list;
  cập nhật docstring/comment mô tả scope. Giữ default replace đúng8, validator strict và
  scan flag finish_supported theo server; flag chỉ scope, không eligible/grant. Không
  refactor capture/environment/archive/rename/observe hoặc đổi schema/record/ID.
- `tools/app_ui.html`: luồng direct finish hiện có dùng scan flag, không cần logic UI mới.
  Chỉ được sửa hai chuỗi VI/EN mp_unsupported để mô tả theo nút hỗ trợ ở hàng, thay cho
  câu chỉ nêu AGENTS/CLAUDE/GEMINI rồi nói mọi file khác phải làm tay. Giữ df_ro đã nhận;
  không đổi DOM/handler/nút/API/state/async sequence. Nếu thật sự cần logic mới, trả
  finding/amendment trước sửa. `tools/app.py` chỉ đọc, không route mới.
- Thêm `tests/test_merge_scripts.py`: fixture độc lập/tempfile, kiểm hai script và một
  lifecycle thật; reuse helper nhỏ nếu không kéo release build/fullgate hoặc test không
  liên quan. Được thêm một browser case vào `tests/test_ui_browser.py` bằng harness có sẵn.
- Amendment hẹp `tests/test_merge_entrypoints.py`: exact allowlist assertion nay16path,
  thêm tuple2script độc lập với code owner; giữ đúng14path cũ và replace8. Scan fixture
  cũ chỉ seed guide+entrypoint thì vẫn chỉ có14row hỗ trợ: giữ inventory/assertions cũ,
  không buộc bằng toàn FINISH_ALLOWLIST. Test mới riêng kiểm script flags/managed state.
  Không cần thêm script vào Base chung để rồi sửa hàng loạt count/negative/lifecycle.
  Sửa tên/comment test14→scope hiện hành khi cần; giữ mọi negative helper/roles/pack cũ.
- `tools/README.md` và hai guide nâng cấp VI/EN: ngoại lệ finish-only đúng hai script,
  mọi script khác vẫn ngoài scope; cập nhật matrix/gap hiện tại16path, giữ14 của D-01e
  là evidence lịch sử. Không suy scope theo toàn thư mục hoặc số lần tái dùng skill.
  Dựng lại hai HTML guide nâng cấp và hai START_HERE bằng generator, không trang khác.
- STATE/HANDOFF để bàn giao. Không sửa hai script đích thật hoặc skills/AGENTS/PROJECT,
  schema/.cvf/pins/transaction/upgrade/check_package/build_guides_html/pack/native/runtime
  thật, VERSION/MANIFESTrepo hoặc verdict roadmap. Không thêm dependency/helper/registry.

## Hợp đồng giữ nguyên

1. Preview/hash/diff dùng cùng captured buffers; UTF-8/NUL/max bytes/max rows giữ nguyên.
   .py chỉ là tên đường dẫn. Cả text Python cố ý sai cú pháp cũng có thể preview/finish
   nếu đạt điều kiện text; không dùng AST/compiler/interpreter để quyết định eligibility.
2. Finish dùng đúng server validator, quản lý scope và môi trường hiện có. Client cờ
   scope/allowed/eligible giả không mở quyền; path alias/case/traversal/ADS/backslash sai
   từ chối trước đọc ngoài vùng. Không tự thêm path vào manifest/scan để biến nó thành managed.
3. Pipeline D-01c/e giữ: archive current.txt/incoming.txt/record.json, verify committed
   trước một Windows same-filesystem no-replace rename pending vào pending-retired.txt,
   observe đúng ID. Current không ghi; không sửa MANIFEST/MERGE_STATUS/profile/PROJECT.
   Không overwrite slot/retry apply/copy+xóa/move-back/Undo hoặc coi exception là finished.
4. Record có path/hash hai script nhưng không thêm nội dung mã vào JSON/log/result.
   Diff là response có chủ đích như hiện có; snapshot chứa bytes cần phục hồi bằng tay.
   Chưa confirm không ghi; mất response thì observe ID cũ, không tự resend apply.
5. Không tự chạy script trước/sau finish, không thực thi để validate hoặc hiện preview.
   Hành vi package upgrade vẫn do owner cũ; guard/core/schema/intake không thay đổi.

## Acceptance hữu hạn trên dữ liệu giả

| Nhóm | Evidence phải có |
|---|---|
| Scope và quản lý | Exact REPLACE8/FINISH16, giữ14path cũ; hai script đúng tên có scope flag nhưng allowed+unmanaged vẫn not_managed, không đọc script/ghi. Managed giả hợp lệ trong fixture mới eligible; helper.py, scripts khác/pack/core/.cvf vẫn unsupported, không wildcard. |
| Hai script, khác/identical | Mỗi path preview→finish→observe; current raw EOL nguyên, incoming snapshot/retired đúng bytes, path/hash record đúng, chỉ pending đã chọn hết scan. Replace-preview/apply vẫn từ chối dù dùng hash thật từ finish. Có cặp identical; không suy script usable/intake accepted. |
| Không thực thi | Payload UTF-8 với side-effect sentinel/raise và text Python không hợp lệ; finish không tạo sentinel hoặc bytecode từ chúng. Không import/run/compile current/pending. Snapshot toàncây trước–sau chứng minh current và file ngoài tác động giữ; không chỉ nhìn returncode. |
| Refusal/state | Một tập hữu hạn đại diện: malformed path/case, unmanaged, NUL/binary/too-large hoặc truncated, stale token/candidate, journal dở/link trong ancestry. Chọn target guard/cleanup/observe đã có để giữ semantics; không nhân toàn fault matrix D-01c cho từng script. Sau archive committed lỗi cleanup/rename không báo finished giả. |
| API và UI | Một kiểm qua adapter HTTP có Host/token thật của harness; client flag không làm replace thành hỗ trợ. Một browser direct-entry flow cho một script mới: có diff/xác nhận, chưa xác nhận không ghi, finish giữ current/không chạy payload, row hết pending, không lỗi JS/console. Không cần replace-preview để vào finish; không gọi functional case là visual QA. |
| Lifecycle thật | Một project VI projected-v3 trong tempfile, source A/B/C và MANIFEST fixture qua owner thật. Cả2path được source manifest quản lý; current user sửa, B tạo đúng pending qua upgrade thật; finish giữ current/archive B; C tiếp tạo pending mới, không bị B đã lưu chặn. Manifest sau upgrade phải đúng source B/C; finish không đổi manifest. Profile/PROJECT và current scripts giữ bytes, không thực thi. Không rebaseline project để giấu conflict. |

Lifecycle dùng `check_package.materialize(..., branding=False)` như D-01d/e, không copy
thô repo làm package. Nhãn VERSION fixture là giả; giữ machine/core bytes cùngschema và
source integrity checks thật. Chỉ sửa payload script ở fixture A/B/C rồi dựng MANIFEST
source fixture trước tạo project/upgrade. Không bypass guard/--skip-check hoặc chỉnh
MANIFESTrepo. Với target có overlay EN thật, không nhầm nguồn root/overlay khi tạo fixture;
lượt này chỉ cần VI để chứng minh đúng2path root, không nhận proof VI/EN mới.

Không cần workbook/full T39 mới: evidence D-01d đã có, lifecycle này tập trung pending
script. Profile/quyền trong fixture nếu cần chỉ là dữ liệu giả, không authority thật.
Thiếu Windows/jsonschema/Chromium thì báo NOT_CHECKED/skip đúng phần, không tự cài hoặc
gọi acceptance đạt đủ. Test không được thay script user thật hoặc mở host ngoài harness.

## Kiểm và bàn giao

Chạy module mới, `tests.test_merge_entrypoints.EntrypointScope`,
`tests.test_merge_entrypoints.EntrypointUiScript`, `tests.test_panel.MergeFinishObserve`,
hai ca có sẵn `tests.test_panel.MergeFinishPreview.test_identical_pair_can_finish_while_replace_keeps_its_noop`
và `tests.test_panel.MergeFinishApply.test_cleanup_failure_after_committed_archive_reports_saved_and_never_renames`,
cùng browser case mới. Dùng `PYTHONPATH=tests PYTHONUTF8=1 python -B -m unittest ...`.
Không toànpanel/fullsuite/fullgate/release/Office/paidproof. Chọn thêm target chỉ khi
delta cụ thể cần; lỗi công cụ thử lại tối đa một lần, không lặp để cộng bằng chứng.

Trước sửa kiểm generator --check; nếu drift ngoài scope thì báo, chưa dựng. Sau sửa
Markdown dùng generator hiện có, xác nhận chỉ4HTML dự kiến đổi rồi --check. Giữ EOL;
`git diff --check -- <file-cham>` và `python -B tools/check_package.py --check-eol <file-cham>`.
Tự đọc diff thực, so baseline và protected; file mới LF. Không sửa test thành bỏ assertion
hoặc tạo skip để đạt; không đổi schema/quyền/transaction khi gặp blocker.

HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`, worktree dirty nhiều tranche.
Hash khác thì đối chiếu delta thật, không reset/stash/clean hoặc khôi phục theo bảng.

| File | SHA-256 raw trước thi công |
|---|---|
| tools/merge_center.py | 48b4151f343a1020bd3552df62d46798d2213d07108c096d4a6e1020197a4e6c |
| tools/app_ui.html — chỉ mp_unsupported | 828327105842d6966a4a60f5d4a3bb66b54558d4d3e601b49551a255f9242ad8 |
| tests/test_merge_entrypoints.py — amendment nêu trên | aed0e9fd93b0709d90ede6929476316ca0f6908b1950058b61c95f7def77873c |
| tests/test_ui_browser.py — thêm case | 70f2f2ee27cecb1e038abee21662dbe2a8dabb71acc798474bffbd82ca0df17f |
| tools/README.md | 439f5fdcb72d41eeda8a0f8e4c7706c5306683821f861ccf7169be5c42c8b031 |
| docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md | b55649ed4a9880c60e765704ba78981fee47dd9861cb62e02b80de4f4ec5d69c |
| docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md | 7e14200a298e5169a6aa1c3f801765958de0a169e69e1e7556fc73b48c064ffa |
| tools/app.py — giữ | 976c150dfcb01fa8feff9548c1fededf1a3b4a7e08e5bddff9dd2cbb70c391d4 |
| tools/upgrade_package.py — giữ | 13cf5d0cd6e3c2461e0fb1bdd4dd29579f4dbe4f0ad48422020979ab44951226 |
| tools/transaction.py — giữ | 4328586a789298684c9b9fb748bbc5a64eab493bc59a336fd40be0252966cbc8 |
| tools/check_package.py — giữ | 4c620aea2a154ee738a4696139c76e17ee0f97e51cd14b139b2d536d6252c1bf |
| tools/build_guides_html.py — giữ | 264413f62f3dda54aaf341f15ae9bd39163f2928d79bef9bc83df1ece4104bda |
| tools/audit_scripts.py — giữ | 32da7f7168132d1baa097d22ac675f9d1bf0b886c0131917d70b112996f7dcb5 |
| skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py — giữ | 9fb586b9c16fe9cf3f6a16961d5560f47a47fb3a2daa3361750c893f1803a81b |
| MANIFEST.sha256 — giữ | 034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6 |

Worker tự chụp thêm hash bốn HTML và test mới (chưa tồn tại trước thi công) trong HANDOFF;
không cần file baseline/evidence mới. Không stage/commit/push/release, host/global/admin,
CVF cha, AI CLI/provider/subagent do suy quyền từ tên vai; chỉ tạo fixture/tempfile cần thiết.

HANDOFF ghi model/effort thực, split allowlist/managed, delta/hash và bảo toàn bytes,
source cuối pass/skip, proof không thực thi, lifecycle/UI và mọi race/platform/visual limits.
STATE tám heading/tối đa khoảng60dòng. Bàn giao **IMPLEMENTED_PENDING_REVIEW —
D01G_SCRIPT_FINISH_ONLY** để Codex review trước khi nhận subset. Không tự đổi verdict
roadmap hoặc đóng P4/D-01/T39/R7/C-02/D-02/release.
