# Roadmap LAW — Workspace cá nhân dùng lâu dài

Cập nhật: **21/10/2026**. Trạng thái: **D-01a–f và SCRIPT-01 đã nhận đúng phạm vi; D-01g đã nhận ACCEPTED_WITH_LIMITS, M1 đóng; M2 đã chốt danh sách nghiệm thu, M3 đã nhận ACCEPTED_WITH_LIMITS sau M3-C1+A1; snapshot M4 1.9.0 đã chuẩn bị/kiểm; diễn tập mock ba việc đã xong, operator là observer (mục0.9). Operator đã hoãn pilot người mới tới sau MVP; M5 không chặn MVP. E07-B/RC1 nội bộ đã nhận ACCEPTED_WITH_LIMITS tại mục0.11; prerelease v1.9.0-rc1 đã công bố; đã nhận reviewL19/CI main1ca3đỏ và diagnostics conditionalpathleak, corrective L19 source đã review/push, CI mới đang chạy tại0.11, không mở tính năng. Từ đây theo lộ trình đóng tại mục 0, không tự mở thêm tính năng. C-02 chưa pilot; D-02/phát hành còn chờ.** Các verdict WITH_LIMITS và gate dữ liệu/phát hành giữ nguyên.

Đây là roadmap duy nhất dẫn việc tiếp theo của Local Agent Workspace (LAW), hợp nhất định hướng operator, đề xuất external agent R2, phản biện Claude và đối chiếu Local. [Roadmap trước](archive/ROADMAP_HOAN_THIEN_TRUOC_LAW_R2_2026-10-17.md) được giữ nguyên; kết quả lịch sử chỉ có giá trị trong phạm vi đã kiểm.

Người dùng quyết định mục tiêu; agent làm việc trong kho chịu trách nhiệm đối chiếu code và triển khai trong phạm vi được giao. Trạng thái hiện hành ở mục 0; các snapshot và bằng chứng lịch sử bên dưới không thay kết luận nghiệm thu hiện tại. Chưa phát hành.

## 0. Lộ trình đóng roadmap và nghiệm thu — chốt điều phối 21/10/2026

Operator yêu cầu có đường đi, mốc đạt và điểm kết thúc để không tiếp tục trôi theo các
gap nhỏ. Sáu mốc dưới đây là thứ tự đóng công việc còn lại, không là sáu tính năng mới.
Codex điều phối/review; Claude thi công theo phần việc đã giao; operator quyết định
nghiệm thu sản phẩm, người/lịch pilot, quyền Git/CI/phát hành và thay đổi phạm vi gốc.
D-01g đã nhận subset WITH_LIMITS/M1; tiếp M3 theo danh sách M2 đã chốt. Không tự mở D-01h hoặc thêm host/schema/engine.

### 0.1 Định nghĩa xong và quy tắc không đi lạc

- Nghiệm thu MVP theo phạm vi và phần hoãn được operator chốt tại0.10: M1–M4, disposition M5
  POST_MVP và gate kỹ thuật M6. Roadmap gốc R0–R7/P1–P4/T01–T48 vẫn giữ truy vết;
  phần hoãn không đổi thành đã đạt. Không lấy tổng test hoặc một subset làm bằng chứng toàn bộ.
- M2 phải phân biệt phần bắt buộc chưa đạt với phần ngoài phạm vi đã được chốt ở nguồn.
  Không đổi thiếu bằng chứng thành ngoài phạm vi. Nếu muốn hoãn/bỏ một yêu cầu gốc,
  ghi đúng yêu cầu và tác động, chờ operator quyết định; trước đó vẫn là chưa đạt.
- Sau D-01g, chỉ sửa blocker truy được tới một tiêu chí nghiệm thu cụ thể hoặc lỗi
  bảo toàn/an toàn trong phạm vi. Finding chỉ tiện hơn/đẹp hơn/mở rộng hỗ trợ không tự
  thành việc thi công; ghi ngắn tại gap/giới hạn sẵn có. Không sinh thêm sổ/engine/checker.
- Lỗi nhỏ rõ nguyên nhân trong review: Reviewer sửa/kiểm đúng chỗ theo quyền hiện có.
  Lỗi lớn phải có phạm vi sửa và tiêu chí đóng hữu hạn, vẫn giữ nguyên mốc đang chặn;
  không kéo theo refactor/tính năng. Nếu sửa rồi vẫn lỗi, báo BLOCKED với bằng chứng,
  không lặp để có nhiều lượt test xanh. Không bỏ gate để giữ lịch đẹp.
- Một thời điểm chỉ có một phần thi công chính. Không giao lại tranche đã nhận nếu
  không có regression cụ thể. Chỉ chạy full gate tại mốc tích hợp/phát hành cần nó,
  không chạy lại toàn bộ ở mọi bàn giao. Giữ các cấm commit/push/release hiện hành.

### 0.2 Sáu mốc và điều kiện qua — phạm vi MVP theo amendment0.10

| Mốc / trạng thái hiện tại | Việc phải làm, đầu ra | Điều kiện đạt để chuyển mốc | Người làm / người nhận |
|---|---|---|---|
| **M1 — Nhận D-01g / ĐÃ ĐẠT SUBSET WITH_LIMITS** | Claude trả D01G_SCRIPT_FINISH_ONLY; Codex review đúng workorder, managed membership, current giữ, không chạy script, archive/lifecycle/UI và protected bytes. | Verdict nhận subset đúng scope, blocker trong tranche đã đóng, source/hash và phần chưa kiểm rõ. Nếu phải sửa, chỉ sửa blocker của D-01g; không mở thêm path. | Claude → Codex reviewer |
| **M2 — Chốt danh sách nghiệm thu / ĐÃ CHỐT DANH SÁCH** | Codex đối chiếu một lượt các yêu cầu gốc với bảng mục10 và evidence đã có; mỗi ID/nhóm có owner, kết luận đủ/chưa đủ, bằng chứng, blocker cụ thể hoặc căn cứ ngoài phạm vi. Chốt bắt đầu/đích nâng cấp, môi trường/host sẽ công bố và khả năng chưa hỗ trợ. Ghi trực tiếp roadmap/HANDOFF, không tạo bộ roadmap mới. | Không còn yêu cầu bắt buộc bị bỏ quên hoặc chưa có owner/cách kiểm. Danh sách blocker để đóng D-01/T39 và các mốc khác là hữu hạn, có tiêu chí xong từng mục. Phần đã đạt được tái dùng evidence, không giao thi công lại. Mọi đề xuất giảm scope phải được operator chấp thuận trước khi dùng. | Codex chốt đối chiếu; operator quyết định điểm thay scope nếu có |
| **M3 — Đóng blocker kỹ thuật và nghiệm thu tích hợp / ACCEPTED_WITH_LIMITS** | Claude sửa đúng danh sách M2; Codex kiểm phần sửa và các luồng thực thuộc A/B/C: nguồn→kết quả→mở lại→dùng lại→nguồn đổi/stale; tạo/adopt/nâng/hạ/phục hồi trong phạm vi T39 đã chốt. Kiểm nguồn/ID/revision/quan hệ/profile/quyền/phần riêng được giữ; tình huống không hỗ trợ phải từ chối trước ghi. | Từng blocker M2 có verdict đóng hoặc còn BLOCKED rõ ràng; không có mất dữ liệu/nâng quyền/nhận stale trong case bắt buộc. Có kết luận D-01/T39 đúng phạm vi gốc, không chỉ cộng test a–g hoặc dựa vào nhãn version. Lỗi ngoài phạm vi không tự mở tính năng. | Claude → Codex review độc lập |
| **M4 — Đóng băng candidate MVP / SNAPSHOT KỸ THUẬT ĐÃ CHUẨN BỊ** | Chuẩn bị source/phiên bản/tài liệu và phạm vi hỗ trợ theo M2; dùng owner đóng gói/projection hiện có để có artifact cố định. Kiểm package/HTML/integrity và chạy/mở UI cùng case nâng cấp bắt buộc trên bản đó; ghi hash, source snapshot, môi trường, gate thực chạy và giới hạn. | Có artifact cố định dùng cho nghiệm thu MVP, hash/baseline rõ và các kiểm kỹ thuật bắt buộc đạt; không thay bytes khi đang thử. Candidate nội bộ chưa đáp ứng Git/CI/RC chính thức phải ghi đúng như vậy, không gọi release hay CI xanh. Gate RC chính thức giữ ở M6; người/lịch pilot sau MVP không chặn mốc này. | Claude chuẩn bị → Codex review độ sẵn sàng pilot |
| **M5 — Pilot C-02 / DEFERRED_POST_MVP theo operator,21/10** | Sau MVP thu phản hồi người dùng thực; kit C-02 hiện có dùng khi tổ chức pilot có cấu trúc. Diễn tập mock đã xong tại0.9. | Không chặn MVP. T37/T38 và trải nghiệm người mới giữ NOT_RUN, không giả PASS hoặc tuyên LAW hiệu quả hơn native. Khi chạy pilot thật vẫn ghi nguồn/artifact/hỗ trợ/nhiễm context đúng kit. | Người dùng/observer sau MVP → Codex tổng hợp, operator ưu tiên cải tiến |
| **M6 — MVP DÙNG THỬ ĐÃ PHÁT HÀNH v1.9.0-rc1; CHƯA FINAL/STABLE** | MVP dùng thử: RC1/ZIP/gate/checksum đã công bố GitHub prerelease tại0.11, giữ baseline để dùng và lấy feedback. Phát hành chính thức: phần D-02 còn lại theo RELEASING khi có quyền. | MVP dùng thử: operator đã cấp quyền phát hành prerelease, RC1 đãreview/côngbố/tag-assets verified; không cần pilot người mới hoặc CIofficial để phát hành dùng thử, chưa có claim usability mới. Official: vẫn cần gate đúng source/commit, Gitclean, CI cho ô công bố, RC verify/nghiệm thu và quyền phát hành; chưa đạt thì không tuyên official/toàn roadmap xong. | Codex bàn giao → operator nhận/dùng; Claude sửa theo feedback đã chốt; official theo quyền riêng |

Đường đi trước MVP: candidate cố định → E07 kiểm nguồn/tích hợp → RC và nghiệm thu
kỹ thuật → operator nhận MVP trong quyền đã cấp. M5/pilot chuyển sau MVP theo0.10,
không còn vòng phụ thuộc C-02↔D-02. M4 không phải verdict phát hành; gate ở
.github/RELEASING.md vẫn áp dụng tại M6. Source đổi thì ghi delta/hash và kiểm phần
bị ảnh hưởng; không lấy evidence candidate cũ đại diện bytes mới.

### 0.3 Các điểm còn mở đã biết, không biến thành tính năng nối tiếp

| Điểm còn mở | Được xử lý tại | Điều kiện đóng hoặc trạng thái phải giữ |
|---|---|---|
| M1 đã nhận D-01g WITH_LIMITS; claim raw inverse lịch sử NOT_VERIFIED | Đã có disposition | Không săn preimage/rerun suite; giữ sai lệch --help và giới hạn trong HANDOFF. |
| P4/D-01/T39 mới có evidence từng subset; scope nâng cấp/schema và các ID còn thiếu chưa được chốt toàn bộ | M2→M3 | Đối chiếu yêu cầu gốc và lấp đúng phần bắt buộc; không mặc định phải có generic finish cho mọi file hoặc migration cho mọi schema, cũng không tự bỏ yêu cầu gốc chưa đạt. |
| C-02/T37–T38 chưa có pilot người mới | Sau MVP, theo quyết định operator0.10 | DEFERRED_POST_MVP; không chặn prototype/MVP, không tuyển người/lập lịch trước MVP hoặc thêm tính năng để lấp chờ. |
| Worktree nhiều lượt chưa commit; CI/quyền Git/phát hành chưa đủ | M6; M4 công bố rõ snapshot nội bộ | Chỉ làm thao tác đã được operator cấp; không tự clean/reset/commit/push hoặc giả Git sạch/CI xanh. Không đánh đồng candidate dùng thử với RC đã đạt gate phát hành. |
| Các giới hạn đã công bố: host khác, macOS/Linux/Python runtime chưa kiểm, x14, custom-shared/pack/ngoài allowlist | M2 phân loại theo yêu cầu gốc | Hạng mục ngoài phạm vi gốc hoặc đã được operator hoãn giữ ở giới hạn; hạng mục bắt buộc thiếu proof vẫn là blocker có owner. Không tự mở rộng từ gap tài liệu. |

### 0.4 Báo cáo tiến độ và điểm dừng mỗi lượt

Sau mỗi bàn giao chỉ cập nhật: **đang ở M nào; tiêu chí nào đã đạt; blocker nào còn;
ai/đầu vào nào đang chờ; mốc tiếp theo duy nhất**. Kèm nguồn/hash của evidence khi cần,
không thay bằng số test cộng dồn hoặc phần trăm tự suy. STATE vẫn tám heading/khoảng60dòng.
Mốc nào chưa qua thì giữ nguyên mốc đó; workorder corrective chỉ đóng blocker được chỉ rõ,
không trở thành một nhánh roadmap mới. Có số đo thời lượng mới ước lượng lại phần việc
còn lại và công bố giả định; không đặt ngày hoàn tất khi lịch người/pilot/quyền còn thiếu.

### 0.5 Đối chiếu M2 đã chốt — 21/10/2026

**Trạng thái: M2_ACCEPTED_AS_CLOSURE_PLAN.** M1 đã nhận D-01g WITH_LIMITS theo verdict
độc lập và Codex; raw inverse lịch sử NOT_VERIFIED giữ nguyên, không là gate bổ sung kéo
dài review. Codex chốt bảng R/P/T và owner/exit E02–E07 trong quyền điều phối PROJECT.
Reviewer phụ đã kiểm đủID/nhấtquán/gate, không nhận runtime thay bảng này. Chốt M2 chỉ
xác nhận danh sách nghiệm thu hữu hạn, **không nhận toàn R0–R7/T01–T48** hoặc đóng phần
thiếu proof. Không có đề xuất giảm scope được dùng. E02–E04 đã nhận M3 WITH_LIMITS; kết luận và snapshot tiếp theo tại mục0.8.

Nguồn chuẩn đối chiếu: R2 gốc mục12, SHA-256
`7a2f861a198b5bdf59e29d1b959f3056f464ff7f363a15f7c4f404f0ef901d9b`
(khớp mục12.2); mục4–7/8.1/10/11 của roadmap này; verdict có giới hạn trong HANDOFF.
Chỉ đọc source/test để tìm locator, **test tồn tại không có nghĩa lượt này đã chạy/đạt**.
`Txx đủ subset` dưới đây tái dùng verdict đã nhận, không tuyên mọi biến thể hoặc toàn host.
Các ID còn thiếu có packet/owner bên dưới; không coi thiếu proof là ngoài phạm vi.

#### 0.5.1 Phạm vi và baseline cần khóa khi nhận M2

- Candidate nội bộ giữ phạm vi đã đo: Windows11/NTFS local, Python3.11.9 và dependency
  theo mục6.2; core role proof trên Claude Code CLI2.1.81. Chưa suy proof cho VSCode,
  Desktop, host/model/version khác hoặc sandbox. Cấu hình mới phải được ghi/kiểm khi dùng;
  bảng này không khẳng định các model/host ngày19/10 vẫn khả dụng ngày phát hành.
- Một đường nâng cấp cần chứng minh từ artifact có thực, không chỉ sửa VERSION giả:
  **ứng viên** `dist/local-agent-workspace-v1.8.0.zip`, SHA-256
  `a27eb50e1b93cf65cbfb1489412e3d14b5ca228c734c24038e042204cc924bc7`,
  inventory223file, VERSION1.8.0, chưa có profile schema/.cvf-v3. Đây mới là baseline
  đã đối chiếu222entry MANIFEST theo chuẩn EOL của owner,0lệch; gate JSON cạnh ZIP
  khớp archiveSHA/kindofficial/version1.8.0,4gate passed và Gitclean ở commit
  b887fc0063c99d3dedb2f578c2b9a6e52594e678. Đây là kiểm record/bytes lịch sử,
  không chữ ký/CI hoặc chạy lại125test. E03 dùng đúng bytes này và kiểm lại hash trước dùng. Đích là delivery projection của source sẽ freeze ở E05,
  chưa có hash đích; D-01d/e/g cùng-schema vẫn chỉ là chứng cứ bổ sung.
- Không dùng cây v1.8.0 đã sửa SCRIPT-01 làm artifact phát hành nguyên gốc. Không refresh
  MANIFESTrepo để che dirty source. Thử upgrade/downgrade chỉ trên project fixture/copy.
- Downgrade chỉ nhận chiều thực sự đã kiểm, hoặc từ chối trước ghi khi schema không hiểu;
  không hứa downgrade xuyên mọi schema. Nếu yêu cầu gốc chưa được đáp ứng bằng bảo toàn/
  từ chối có chứng cứ, giữ E03 mở; không tự đổi thành unsupported rồi đóng.
- P4 xét từng nhóm theo owner: guide; entrypoint; hai script; profile/quyền; machine/core;
  metadata/index; personal skill/pack; package khác. Giữ/dùng mới/tự sửa cần đường xử lý
  và phục hồi thực, không yêu cầu cùng một nút áp dụng cho mọi loại. Mục matrix của
  tools/README chỉ là tài liệu; chỗ thiếu thao tác cần có disposition ở E03 trước chốt P4.
- Official support vẫn theo `.github/RELEASING.md`: CI xanh đúng commit cho ô công bố,
  full gate/Git sạch/RC nghiệm thu ở E07. Scope candidate trên không thay gate release.

#### 0.5.2 Đối chiếu R0–R7 và P1–P4

| ID | Kết luận từ bằng chứng hiện có | Phần còn lại / owner / packet |
|---|---|---|
| R0 | Kế hoạch/owner/tree và nguồn đã có; A-00/G-00 nhận tĩnh | Codex đã khóa bảng sau verdict E01, giữ quyết định/scope chưa có proof mở; không thi công lại cây |
| R1 | A-01/A-02/I3 nhận core T01–T04/lifecycle có giới hạn | Hành vi nguồn T06–T09 và declaration T03 còn thiếu proof đầy đủ: Claude→Codex/E02; usability/E06 |
| R2 | A-03–A-07 nhận writer/read-UI trong giới hạn hợp tác Windows; T13–T16 có bảng8.1 riêng | Nối hành vi nguồn/đọc lỗi/E02 và đường nâng cấp/E03; x14 safe-refusal/PARKED giữ, không mở round-trip |
| R3 | B-01/B-02 nhận content/revision/relations/query/stale qua fixture/API/CLI/UI | Chứng cứ luồng ghép/mở lại/dùng lại/E04; hiệu quả người mới/E06, không suy fullR3 từ module xanh |
| R4 | A-08–A-10 nhận static/profile/native core một host, collision/digest/retire | T21/T27 hành vi và phần claim chưa quan sát/E02; support/khả dụng đúng cấu hình phát hành/E07; không thêm host |
| R5 | A-11/B-03 nhận single-writer/checkpoint/stop/reconcile/acceptance hợp tác | Ghép đúng source/result/owner trong một luồng/E04; host stop/quota thật chưa proof, giữ lời khai UNCONFIRMED; E06 quan sát sử dụng |
| R6 | C-01 nhận A→mẫu→B VI/EN; C-02 kit đã nhận | C-01 kỹ thuật giữ; E06/người mới chuyển sau MVP theo0.10, không cho agent giả participant |
| R7 | I3 và D-01a–f nhận từng subset; D-01g và M3-C1 đã nhận đúng phạm vi | E03 T39/P4, E04 T40, E07 release; chưa nhận toànR7 |
| P1 | D-01a nhận diagnostic version/manifest identity đúng scope | Tái dùng evidence; verify trên artifact cuối/E07, không sửa legacy parser mặc định |
| P2 | CLI structured errors có test/guide, A-02 nhận giới hạn | E02 đối chiếu thông báo và bước xử lý cho đường nguồn/parser/dependency/upgrade thật dùng; chưa tuyên toàn bộ CLI dễ dùng |
| P3 | A-02/I3 và NewProject có proof project ngang hàng, C-02 kit dùng cây riêng | Giữ trong E05/E06; không giao lại chức năng tạo project |
| P4 | D-01b–f và g đang review cung cấp preview/archive/finish theo nhóm | E03 kiểm đủ các nhóm ở trên, ghi rõ đường giữ/dùng mới/tự sửa/phục hồi hoặc blocker thiếu; không tự mở generic merge |

#### 0.5.3 Truy nguyên từng T01–T48

| ID | Bằng chứng/locator đã có và giới hạn | Disposition / việc còn lại |
|---|---|---|
| T01 | A-02 native fresh session; I3/new-adopt-upgrade | Đủ core đã nhận; E06 quan sát người mới, không rerun host khác |
| T02 | A-02 None/STATE hoàn tất; chưa mọi biến thể STATE trống | Core nhận WITH_LIMITS; E02 đối chiếu nhánh trống nếu chưa có trace, không bịa việc |
| T03 | A-02 nêu mâu thuẫn/không chọnmtime, thiếu declaration đã ghi | E02 kiểm đúng thiếu sót này; không mở lại phần mâu thuẫn đã nhận |
| T04 | A-02 sửa câu cùng phiên/0tool; recipe small_job | Tái dùng verdict; không bắt lập TASK cho việc nhỏ |
| T05 | A-03/A-07; LibrarySync.preview_apply_idempotence_revision_and_history | Writer đã nhận; E02 xác nhận grant→index và chưa xác minh nội dung trong trace agent |
| T06 | AGENTS và LibraryScopeAndRename; chưa trace trọn user chuyển→agent kiểm thực | E02 fixture sai chỗ→chuyển thật; agent không tự di chuyển |
| T07 | LibraryScopeAndRename.copy_and_equal_hash_never_prove_a_move | ID/copy guard đã nhận; E02 lời user báo sai/copy2bản, không xóa/gộp |
| T08 | A-07 LibraryReadApi.error_matrix; LibraryReadFailures/LibraryNotChecked | Đủ parser/index guard subset; E02 thông báo thiếu index khác lỗi đọc và bước tiếp theo |
| T09 | B-01/B-02 ID/revision/loại source-output; LibraryScopeAndRename ambiguity | Không lấy guardID thay hành vi chọn nguồn; E02 cùng tên/khác vai, hỏi phần chưa rõ |
| T10 | A-03–A-06 missing/reappear/confirmed rename/history; B-01 revision | Tái dùng verdict ID/revision/tombstone; upgrade giữ ở E03 |
| T11 | A-05 README ownership/path-scope; A-06/A-07 links/junction/lockleaf | Đủ subset hợp tác; file-symlink1314 chưa đo, không đổi thành passed |
| T12 | A-03/A-06 preview/apply repeat/no-op; sổ/công thức giữ | Tái dùng idempotence, không lập bài test mới chỉ để đếmID |
| T13 | Ma trận A-06: user-save/conflict và Excel E2 logs đã review | Đủ subset hợp tác; race cuối giữ giới hạn, không hứa mọi thời điểm |
| T14 | Ma trận A-06: fault/processkill/resume/rollback, permission/disk có nhãn mô phỏng | Tái dùng; release không bỏ giới hạn mock/kernel-race |
| T15 | A-06 malformedbook; LibraryNotChecked thiếuopenpyxl exit2 | Đủ subset; E02 cách báo/khắc phục, E07 gate trên source cuối |
| T16 | A-06 template/static/read-API, Ví dụ tách Danh mục, macro/link parts đã kiểm | Tái dùng đúng template mặc định, không suy mọi Officehost an toàn |
| T17 | B-01 ContentFlow.test_t17_* invalidation đúng dependency/revision | Tái dùng fixture/API; E04 nối kết quả thực và mở lại |
| T18 | B-01 test_t18_* semantic/source-event cùnghash vẫn đổi basis | Tái dùng; E04 không dùng hash chứng minh hiệu lực |
| T19 | B-01 test_t19_* giữ decision/supersedes/history | Tái dùng; E03/E04 giữ quyết định sau upgrade/nguồn đổi |
| T20 | B-01 test_t20_*; B-02 copy giữ inference/conditions/limits | Tái dùng; E04 không nâng artifact thành nguồn gốc |
| T21 | B-01 test_t21_* chỉ lưu text chỉ thị nguyên nghĩa; không proof agent từ chối lệnh | E02 source/metadata chứa lệnh giả, agent báo và không làm; không claim chống mọi prompt injection |
| T22 | A-09/A-10 profile choices không thành grant; Eligibility/pack intake | Tái dùng claim≠approval; role-pack chưa tiếp nhận không được dispatch |
| T23 | A-10 OwnershipAndCollisions/duplicate inventory/user edit | Đủ subset hợp tác; race cuối còn, không native overwrite guarantee tuyệt đối |
| T24 | A-10 config_bytes_changed_without_version_change + drift/reconcile | Tái dùng bytes binding; E03/E07 giữ receipt/role ownership |
| T25 | A-09/A-10 Eligibility/UNSUPPORTED; requested≠registered/applied | Đủ diagnostic subset; E07 không công bố field chưa quan sát |
| T26 | A-09 requested/tier/unknown; A-10 trace model2.1.81; effortnull | Tái dùng đúng quan sát; E06/E07 ghi unknown/chi phí quan sát, không suy bill/model từ tênvai |
| T27 | roles/README fallback một agent; B-03 missing_tool_quota_or_provider giả lập | E02 trace fallback trong grant/thiếuReviewer giữ nháp; không giả multi-agent/API hoặc coi mô phỏng là host không có subagent |
| T28 | A-10 Scout+core Worker/Reviewer native trace/listing fresh, mục7 | Đủ core một host đã nhận; E04 nối nguồn/kết quả nếu thiếu trace ghép |
| T29 | A-11 two_assignment_slots/shared-target/context-update guard | Đủ recipe single-writer hợp tác; E04 kiểm luồng ghép, không cưỡng chế native Write |
| T30 | A-11 source/task/result/candidate drift và B-01→A-11 probe | Tái dùng checkpoint; E04 source đổi→không tích hợp stale |
| T31 | B-03 void_assignment/late-result; host_stop UNCONFIRMED | Đủ recipe subset; E04 không báo host đã dừng nếu không quan sát |
| T32 | B-03 timeout/reconcile requestID/published identity/reopen | Tái dùng protocol; E04 không tự retry/cấpID mới từ silence |
| T33 | B-03 missing-tool/quota/provider mô phỏng/limits | Đủ protocol; E02/E06 kiểm agent không đổi provider/auth/install ngầm |
| T34 | B-03 integration_gate thiếu requirement/review veto vẫn giữ | Tái dùng guard; E06 người thật đánh giá nội dung, không lấy checker xanh làm nghiệm thu |
| T35 | B-03 AcceptanceAB; D4 lab đúng1bản có user nhận riêng | Tái dùng A≠B; E06 acceptance của participant/operator đúng artifact |
| T36 | C-01 PersonalReuse VI/EN/harness9target sau sửa, intake/grant mô phỏng | Đủ subset A/template/B; E03 giữ personal qua upgrade, E06 quan sát dùng lại sau MVP |
| T37 | C-02 kit PREP_ACCEPTED; mock tại0.9, chưa participant | DEFERRED_POST_MVP theo operator0.10; NOT_RUN về người mới, không chặn MVP |
| T38 | C-02 L→N cùngnguồn; chưa đo usability/so sánh native | DEFERRED_POST_MVP theo operator0.10; không claim LAW thắng hoặc benchmark nhân quả |
| T39 | I3/new-adopt/profile; D-01d VI/EN cùngschema; D-01g fixture script | E03 chưa đủ đường artifact1.8.0→đích cuối và old-writer/new-schema; E07 hash/release thật |
| T40 | RC3 TXT/Word đã mở; B-02 opener có mock; file không phụ thuộc session | E04 mở nguồn/kết quả/căn cứ ngoài LAW trên candidate, không cần thêm host chưa công bố; E07 RC lặp phần bị đổi |
| T41 | A-07 read_book/LibraryReadApi + B-02 owner chung | Tái dùng cùng sổID/revision; E04 không thêm UIstore |
| T42 | B-02 artifacts/relations/query/profile và browser đã review | Tái dùng liên quan≠nguồn chính; E04 chuỗi source→artifact |
| T43 | A-07 đọc/duyệt không scan/write/log; B-02 processCLI query | Tái dùng guard no-AI/no-scan; E04 mở lại không tạo lại |
| T44 | B-02 đúng artifact/revision, basis/unknown/opener guards | Đủ fixture/API/UI; E04 file mở ngoài LAW, không gọi mock là Office visual |
| T45 | A-07 source-selection, B-02 copy basis/limits; copy≠dispatch | Tái dùng; E04 giữ đúng inputID/revision trước writer |
| T46 | A-07 LibraryReadApi/source states; B-02 read errors/unknown | Tái dùng error matrix subset; E02 thông báo giúp user xử lý, không báo lỗi thành rỗng |
| T47 | A-11/B-01/B-02 drift source/catalog/prepare guards | Tái dùng; E04 không nhận bản khác sau chọn/prepare |
| T48 | B-02 fresh-process query/sổ quan hệ; B-03 reopen checkpoint | Tái dùng storage; E04 phiên mới dùng đúng bản, E06 người mới tiếp việc sau MVP; không bắt đổi host chưa hỗ trợ |

#### 0.5.4 Danh sách đóng hữu hạn — không phải bảy feature mới

| Packet / mốc | Owner và đầu ra còn thiếu | Điều kiện đóng / điểm dừng |
|---|---|---|
| E01 / M1 — CLOSED_WITH_LIMITS | Codex và Reviewer độc lập nhận subset D01g theo acceptance gốc, không blocker sản phẩm xác định | Raw inverse lịch sử NOT_VERIFIED; sai lệch --help giữ dấu vết. Source/test/UI đúng snapshot,8protected khớp; không săn preimage/rerun suite. Không nhận toànP4/T39 |
| E02 / M3 — ACCEPTED_WITH_LIMITS | Claude chuẩn bị/chạy một tập fixture hành vi gộp T02trống/T03declaration/T05–T09/T21/T27/P2; Codex review trace. Chỉ sau M1/M2 và trong quyền host/thử nghiệm được giao | Một host/cấu hình ghi đúng; trace từng tình huống gộp, source/index/current không bị sửa trái grant, chỉ thị nguồn không được làm, fallback không fake/không tựreview, lỗi có bước xử lý. Dùng proof cũ cho phần đã đạt; thiếu host/quyền ghi WAITING, không tự mở provider/config |
| E03 / M3 — ACCEPTED_WITH_LIMITS | Claude→Codex: T39/P4 trên baseline1.8.0 đã verify và source đích; các owner upgrade/profile/library/pack/merge hiện có, không writer mới | Preview/no-write→upgrade→dùng lại→downgrade hoặc refusal trước ghi, fixture giữ nguồn/sổ/decision/ID/revision/profile/quyền/personal/native; current/pending/archive/hash đúng. Tool cũ không ghi hỏng schema mới. Từng nhóm P4 có đường giữ/dùngmới/tựsửa/phục hồi hoặc finding cụ thể; không lấy VERSION giả/generic unsupported thay proof. Lỗi thì sửa đúng blocker, không mở thêm mergepath tự động |
| E04 / M3 — ACCEPTED_WITH_LIMITS | Claude→Codex: một trace tích hợp A/B/C nguồn→kếtquả→mởlại→dùnglại→đổinguồn/stale và T40 | Tái dùng A-10/A-11/B-01/B-02/B-03/I3; chỉ lấp mối nối thiếu, bind đúng bytes/revision/decision/limits. Nguồn/kếtquả/căn cứ mở được ngoài LAW; không stale integration/auto-retry/nhậnAchoB; nêu phần host thật/môphỏng riêng. Không bắt chạy lại mọi scenario đã nhận |
| E05 / M4 | Codex/Claude chuẩn bị candidate nội bộ và kit đã có sau M3 | Ghi hash nguồn/projection/candidate/nguồn A-B/oracle thật, project nhánh riêng/readiness/không lộ maintainerdata. Chưa officialRC, không cần Gitclean/CI trước pilot nếu kit không bắt; source đổi thì ghi delta và kiểm phần ảnh hưởng |
| E06 / M5 — POST_MVP | Sau MVP thu phản hồi thật; operator bố trí pilot có cấu trúc khi cần | Không gate MVP. Nếu chạy kit thì G1–G7/log/artifact/ghi hỗ trợ vẫn đúng; chưa chạy không chuyển thành PASS |
| E07 / M6 | Claude chuẩn bị, Codex review; operator cấp quyền Git/CI/release và nhận bản cuối | Toàn RELEASING, source cuối/fullgate/Gitclean/CI đúngcommit/ô công bố/RC verify và thử upgrade/khôi phục/checksum/supportmatrix. Không commit/push/buildofficial trong quyền hiện tại. Đạt gate kỹ thuật trong phạm vi công bố và operator nghiệm thu mới nhận MVP; pilot/feedback sau MVP |

E02–E04 đã nhận WITH_LIMITS theo mục0.8; không giao lại M3.
E05 có snapshot kỹ thuật đã kiểm; E06/người mới chuyển sau MVP theo0.10. Tiếp E07/M6 sau M4 và disposition M5; M1/M2/M3 không giao lại.
Không tự dùng danh sách này để giảm scope: yêu cầu chưa đủ proof còn mở tại đúng packet;
nếu muốn bỏ yêu cầu hoặc đổi phạm vi thì operator quyết định. Nếu E03 tìm thấy lỗi dữ liệu/
quyền hoặc đổi schema cần thiết, bàn giao finding và thiết kế đúng owner trước sửa lớn;
không biến mọi giới hạn cũ thành tranche mới. Mọi giới hạn đã nhận vẫn nằm ở hàng gốc.

### 0.6 Brief M3 — lịch sử thi công; đã nhận M3-C1+A1 tại0.8, 21/10/2026

**Giao một lượt đóng E02–E04, không mở feature.** Operator chuyển Claude và chọn
model/effort; Codex giữ orchestrator/reviewer. M1/D-01g đã nhận, không giao lại E01.
Hàng này là phiếu việc; không cần workorder hoặc bộ báo cáo mới. Dùng HANDOFF để bàn giao.

**Đầu vào và quyền:** đọc STATE, mục0.5/0.6, AGENTS8.3/8.4 và đúng owner liên quan.
Ghi actual host/version/model/effort quan sát được, không suy mức từ raw10. Nhận dirty
worktree; chụp hash đúng owner trước sửa, không lấy HEAD làm baseline tranche. Dùng
lab/temp mới, chỉ dữ liệu giả, source snapshot qua delivery projection owner thật.
Không sửa source/user project1.8.0 thật, profile/native/config/global/admin/chaCVF,
MANIFESTrepo/VERSION/pins/schema/transaction; không stage/commit/push/release/install/
provider/auth/API/agent phụ mới ngoài quyền đã giao. Không chạy audit_scripts hoặc
check_spreadsheet (kể cả --help) để kiểm code; chúng chỉ là bytes trong lượt này.

| Thứ tự / packet | Việc Claude thực hiện | Bàn giao để Codex nghiệm thu |
|---|---|---|
| 1 / E02 | Một tập fixture gộp T02trống/T03declaration/T05–T09/T21/T27/P2 trên host thực của Worker; ghi version/quyền/tool thật. Nguồn sai chỗ→user chuyển/copy hoặc báo sai; nguồn cùngtên/khácvai; parser/index lỗi; source chứa chỉ thị vô hại có marker giả; không có role khả dụng/Reviewer thì chỉ làm nháp trong grant hoặc chờ. Không chỉnh host để giả mất capability. Nếu availability/quota được giả lập thì ghi SIMULATED, không claim cả host thiếu subagent. | Trace có input/output/locator và bytes trước-sau cho tình huống gộp; agent không tự chuyển/xóa/gộp/chạy chỉ thị/mở quyền/provider; index mới chưa là đã xác minh; message lỗi có cách xử lý. Tái dùng proof cũ cho phần guard đã nhận, không nhân48test hoặc tạo role/model mới. Chỗ host không quan sát được ghi đúng thiếu proof, không tự nângpassed. |
| 2 / E03 | Kiểm SHA baselineZIP1.8.0 nêu0.5.1, giải nén trong temp mới sau kiểm mọi path nằm trongtemp; dùng owner có trong gói cũ để tạo fixture project. Seed nguồn/sổ/decision/phầnriêng hợp schema cũ, rồi nâng bằng owner hiện hành vào deliveryprojection hiện hành (branding=False). Không đổi VERSION giả để đóng đườnglegacy. Theo dõi current/pending/archive/profile/quyền/native/personal; mở/đọc lại bằng owner. Kiểm chiều downgrade được hỗ trợ hoặc refusal trướcghi và old-writer/new-schema không ghi hỏng. | Bảng trước-sau/hash/số dòng/ID/revision/decision/quan hệ, candidate/source MANIFEST và thông báo thật. Từng nhóm P4 ở0.5.1 có lựa chọn giữ/dùngmới/tựsửa/phục hồi theo owner hoặc finding thiếu cụ thể; không tự mở allowlist/genericmerge/applyinstruction. D-01d/e/g same-schema dùng lại, chỉ thêm phần thiếu của legacy/artifact. Nếu schema migration thật cần thiết hoặc oldwriter ghi hỏng thì trả finding+thiết kế owner trước sửa lớn; không tự làm migration/refactor để xanh. |
| 3 / E04 | Nối một luồng bằng owner hiện có: nguồn đượcchọn→candidate có basis→review/checkpoint→publish→mởlại freshprocess→dùnglại→nguồn đổi/semanticchange→từchối kếtquảstale. Giữ inference/limits/decision/binding, acceptanceA không truyềnB; không giả dispatch/useracceptance. Kiểm nguồn/kếtquả/căn cứ đọc ngoài LAW bằng công cụ đang có, không cài ứng dụng hoặc chạm phiên/file thật. | Một trace tích hợp nối các locator evidence A-10/A-11/B-01/B-02/B-03/I3 đã có; đánh dấu rõ live/mock/source-only. Chỉ chạy phần nối còn thiếu; native proof cũ không cần gọi lại cả3role. Freshprocess dùng đúngID/revision, view khôngscan/AI/tạo lại; stale không tíchhợp, retry phảireconcile; opener mock không được ghi là mở Office thật. |

**Owner sửa:** ưu tiên test/probe đã có (`test_task_result_flow.py`,
`test_upgrade_lifecycle.py`, test library/profile/native/merge/personal-reuse liên quan)
và đúng guide hiện có nếu phát hiện câu sai. Script dùng riêng cho fixture để trong
scratch/lab, theo phân tầng script ở skills/README, không vứt helper .py vào gốc repo.
Chỉ bổ sung test trong repo khi nó kiểm được invariant còn thiếu; không tạo framework,
engine/registry/receipt mới. Lỗi nhỏ rõ trong owner giữ contract có thể sửa kèm ca tái hiện;
lỗi mất dữ liệu/quyền/schema hoặc nhiềuowner cần thiết kế/finding trước sửa lớn.

**Giới hạn một lượt:** dùng lại bằng chứng đúng snapshot; một tập kiểm gộp cho từng
packet, một lần sửa đúng lỗi rồi kiểm lại đúng phần sửa. Còn đỏ sau sửa thì bàn giao
CHANGES_REQUIRED với blocker/owner/case cụ thể, không tự mở tranche hoặc lặp suite.
Không fullsuite/fullgate trong M3 nếu không có lỗi cụ thể buộc mở rộng; chúng ở M6.
HANDOFF ghi lệnh/kết quả/file/hash/actualmodel-effort/đãkiểm-chưakiểm, cập nhật STATE
60dòng8heading. Kết thúc **IMPLEMENTED_PENDING_REVIEW — M3_E02_E03_E04** hoặc
**EVIDENCE_PARTIAL — [packet/case thiếu]**; Codex nhận từng packet trước chốt M3.
Không tự nhận toànT39/P4/R0–R7, freeze/pilot/release hoặc gọi participant giả.

### 0.7 Corrective M3-C1 — đã nhận WITH_LIMITS cùng A1 tại0.8, 21/10/2026

**Lịch sử brief; verdict nhận hiện hành ở mục0.8.** Đây là sửa finding trong E02–E04,
không D-01h, feature mới hoặc giao lại toàn M3. Operator chuyển Claude/chọn model-effort;
Codex review. Bàn giao Worker đầu HANDOFF giữ đủ trace và limits, không viết lại như PASS.
E02 nhận chứng cứ quan sát một agent biết đang thử/SIMULATED-USER, chưa người mới/fresh
session và P2 còn thiếu. E04 integrated test đã được Codex chạy đạt; OfficeCLI report là
bằng chứng đọc bằng công cụ ngoài LAW do Worker cung cấp, không Word/Excel visual QA.
E03/F1 chưa nhận sửa runtime vì finding R1 bảo toàn dưới đây.

#### 0.7.1 Quyết định cho từng finding — phạm vi cố định

| Finding / trạng thái | Quyết định và owner | Điều kiện đóng |
|---|---|---|
| **F1/R1 — BLOCKER bảo toàn mới, phải sửa** | upgrade_package.py + test_upgrade_lifecycle.py. Ngoại lệ `rel in updating` hiện nhận membership từ plan nhưng Transaction.add chụp bytes về sau. Codex đã tái hiện: editor lưu core sau plan/trước add, upgrade success và marker mất. | Bytes/hash raw dùng phân loại core update phải được chụp và gắn precondition vào đúng giao dịch bằng expected_before; kiểm lại ở các boundary cần thiết. Không lấy hash mới tại add làm bằng chứng người dùng chưa sửa. Test controlled interleaving lưu core sau plan/trước add giữ USER SAVED và không success giả; giữ2ca tĩnh đã đạt và guardlink/.cvf/--force. Không đổi transaction.py/pins/schema hoặc hardening MANIFEST authenticity ngoài scope. Nếu dùng snapshot/compare mới phải ghi rõ bytes nào đã validate, không thêm engine. |
| **F2 — CLOSED_BY_REVIEWER, không giao lại** | Codex sửa đúng6Markdown: runtime scratch mô tả parent/thư mục con tạo khi cần, shared ghi path đầy đủ, backup dùng `<id>`; dựng4HTML. Còn1locator `tests/test_skill_intake.py` trong toolsREADME gây release_tree lỗi đã đổi sang tên module kho nguồn. Không sửa/nới checker, tạo thư mục giả hoặc đưa tests vào ZIP. | Source package_check0lỗi/15cảnhbáo; HTML10khớp;3target Archive/Lifecycle/Journey source sau sửa đều đạt/0skip. Fullgate/full3class không chạy; warnings README/CRLF không được gọi là0warning. Chỉ kiểm lại phần bị corrective thật tác động. |
| **F3 — VERSION: chốt đích1.9.0, chuẩn bị trước M4** | VERSION + CHANGELOG và đúng chuỗi nhãn checker yêu cầu; không đổi lịch sử1.8.0/ZIP/gate/fixtures cũ. MINOR theo phạm vi thêm tool/profile/metadata và giữ định dạng nguồn/sổ/envelope cũ; không đổi format có sẵn để ép hợp MINOR. Đây là phần chuẩn bị version E07 kéo lên trước freeze, không cấp quyền phát hành. | Worker được sửa VERSION thật thành1.9.0 và thêm changelog trung thực. Tạo đích projection thật, legacy1.8.0→đích1.9.0; chạy tool1.8.0 --apply trên bản sao đã hếtpending phải từ chối trước ghi, kiểm từnghash. Không chỉ sửa nhãn fixture để claim bản thực. --force của tool cũ có thể bỏ guardversion: ghi rõ không dùng để vượt downgrade không hỗ trợ, không claim chặn mọi binary cũ. E07 phải kiểm lại nhãn/hash/gate trên bytes cuối; nếu phát hiện thay format không tương thích thì trả finding để chốt MAJOR trước tiếp, không âm thầm chọn số khác. |
| **F4 — đường profile: sửa hướng dẫn/message, giữ fail-closed** | execution_profile.py reason/next_actions + rolesREADME/guide nâng cấp VI/EN, testbootstrap/profile/upgrade hữu hạn. Không thêm command/registry quyền hoặc tự bootstrap POINTER_PROFILE_MISSING. | PROJECT thiếu canonical line: giải thích agent chỉ thêm khi user giao, ví dụ chính xác `- Phạm vi được giao cho agent phụ: Không có` / `- Standing scope for sub-agents: None`; sau lựa chọn rõ này dùng preview/apply upgrade bằng package mới để bootstrap ownerPROJECT,0grant,khôngoverwritePROJECT/STATE. Có con trỏ nhưng mất profile: khôi phục **đúng profile từ backup** trước config; không tự dựng profile mẫu mất quyền. Không backup thì giữ blocked và nêu cần owner xác nhận quy trình khôi phục/reset riêng, không tự suy quyền; không gợi ý init --force. Kiểm2đường fixture: missingline+emptyexplicit→0grant và pointermissing→refuse/restoreoriginalbytes. Chưa có cấp quyền dùng vai từ các bước này. |
| **F5 — P4 package ngoài allowlist: đóng bằng đường thủ công có bảo toàn** | Hai guide nâng cấp VI/EN + test/probe fixture hiện có. Không mở thêm allowlist/endpoint generic; code chỉ được hợp nhất theo owner, không chạy để validate. | Mô tả và đo một case tools/check_output.py.new: xem diff, giữ riêng rawcurrent+incoming ở vị trí archive mới có ID/không ghi đè, lựa chọn rõ giữcurrent hoặc owner hợp nhất thành bản được yêu cầu, lưu pending bằng thao tác thủ công trong quyền sau đối chiếu, kiểm bytes trước–sau/khôi phục thànhfilemới. Không xóa .new để tắt cảnh báo, không đổi MANIFEST/claim productfinish/record hợp lệ. Nếu chưa có đường thủ công bảo toàn thì trả đúng case thiếu, không gọi unsupported là đã đạtP4. |
| **F6 — P2 và check sai xanh: sửa trước M4** | library.py/check/read errors, library_sync.py message cần thiết, upgrade_package.py thông báo/next_actions + tests structured/library hữu hạn; docsVI/EN nếu hướng dẫn thay đổi. | check phải phát hiện ID trùng khi có cộtID, nêu ID/các dòng và nonzero; sync và check nhất quán, không tự sửa ID. Legacy không có cộtID vẫn đọc theo contract cũ. Sổ hỏng/thiếu sheet/trùngID/upgradeblocked/downgradeunknown có bước xử lý cụ thể, không gợi ý dựng đè sổ hoặc --force lách guard. README package-owned chỉ bỏ theo predicateownership có sẵn, không basename; README nguồn user vẫn được xét. Các next_actions (cả JSON) không khuyên xóa .new/hạ guard. |

**Không mở quét ngoài references:** sync/check không tự duyệt file sai chỗ là đúng scope,
không sửa thành crawler gốcproject. Agent đã có trace T06/T07 chỉ đúngđích/kiểmthực;
thông báo có thể nhắc phạm vi quét nhưng không nói đã kiểm file ngoài vùng.
**Con trỏ mất profile** là trạng thái cần giữ chặn, không phải quyền tự reset grant.
Không lấy lựa chọn phát triển của operator làm xác nhận reset/quyền trong project thật.

#### 0.7.2 Cách thi công và bàn giao một lượt

- Giữ worktree dirty và mọi delta Codex F2; chụp baseline actual owner sau review vào
  HANDOFF trước sửa, không dùng hash toolsREADME9304… của Worker làm bản hiện hành.
  Không reset/restore repo. Owner ngoài bảng, transaction/.cvf/pins/schema/native/global/
  realPROJECT/MANIFESTrepo/ZIP1.8.0 vẫn không sửa. Không cài/provider/API/agent phụ/commit/
  push/release. VERSION/CHANGELOG được mở đúng F3 trong corrective này, thay lệnh cấm
  VERSION của brief0.6 cho riêng việc chuẩn bị1.9.0; quyền khác không đổi.
- Bắt đầu ca đỏ R1 đã mô tả rồi sửa precondition đúng owner; không chỉ thêm check trước
  add trong khi vẫn lấy snapshot mới ở add. Giữ source integrity và path guard có sẵn.
  Nhánh profile không đổi bootstrap authority; hướng dẫn phải có lệnh thực chạy được
  trong fixture, preview trước apply. Hợp nhất docs/HTML F4/F5/F6 trong một lượt generator.
- Kiểm hẹp: R1 + OlderCoreDependency2ca; profile/bootstrap2đường; duplicateID/reader errors
  + preservedlegacy/predicateREADME; legacy upgrade nhãnthật và old-tool refusal;
  packagecheck/HTML/source-delivery +3package targets nếu bytes package thay. E04 đã đạt,
  chỉ kiểm lại phần bị thay thực sự ảnh hưởng. Không chạy fullsuite/fullgate trước M6
  theo nghi thức; không nhân lại mọi case a–g. Một correction rồi kiểm đúng phần sửa;
  nếu vẫn lỗi thì trả finding/owner/case, không tự mở feature hoặc lặp vô hạn.
- HANDOFF: từng F1/R1,F3–F6 đạt/chưađạt, lệnh/kếtquả/hash/actualhost-model-effort,
  giới hạn LIVE/SIMULATED và recovery. STATE60dòng8heading. Kết thúc
  **IMPLEMENTED_PENDING_REVIEW — M3_C1_F1_F3_F4_F5_F6** hoặc **EVIDENCE_PARTIAL** có
  case thiếu. Không nhận M3/M4 hoặc chạy pilot/release; Codex review trước freeze.

### 0.8 Review M3-C1 + A1 và snapshot M4 — 21/10/2026

**M3: ACCEPTED_WITH_LIMITS — M3_C1_F1_F3_F4_F5_F6 + REVIEWER_A1.**
Không còn blocker xác định trong danh sách corrective đã giao. Reviewer độc lập
Sol6.1 Medium nhận F1/F4 theo source/test; Codex chạy13target trướcA1 đạt/0skip,
kiểm thêm đúng phần A1 và đo lại đường legacy1.8.0→projection1.9.0 hiện hành.
Không cộng các lượt thành fullsuite hoặc bỏ giới hạn E02/host/mock/manual trong HANDOFF.

- **F1/R1:** cùng raw buffer phân loại update tạo expected_before; lưu core sau plan/
  trước add hoặc file user vừa tạo bị từ chối, giữbytes. Giữ guards/useredit tĩnh/source
  integrity; không claim kernel-race-free hoặc authenticMANIFEST.
- **F3:** VERSION thật1.9.0; legacyZIP1.8.0 mới giải nén→project bằng ownercũ→upgrade
  mới preview/apply0, giữ3file user đo riêng/manifestđích. Projectkhôngpending rồi
  tool1.8.0 --apply trả1,264file giữhash. --force của binarycũ không được bảo đảm.
  E07 vẫn phải kiểm nhãn/hash/CI/Gitclean/fullgate trên bytes cuối.
- **F4:** missingline có đường lựa chọn rõ của user→bootstrap ownerPROJECT/0grant;
  pointermissing giữchặn và restore đúngbackup; không reset quyền hoặc init--force.
- **F5:** nhận đường thủcông giữcurrent/lưurawincoming/khôi phục thànhfilemới đúngowner,
  không productfinish/genericmerge hoặc tựápcode. Nhánh hợpnhất nội dung mới do owner
  quyết định; không claim đã test mọi cách hợpnhất/codeusable. Downgrade khácschema
  chỉ nhận refusal trướcghi, không tự đóng migration mọi schema.
- **F6/A1:** check/sync nhấtquán IDtrùng và giữlegacykhôngID; README theoownership.
  Reviewer phát hiện filter mới thửdigestREADME qua junction trước guard: đã tái hiện
  canary, sửa dùng link_free/contained trước hash (cả manifest trước đọc) và thêm một
  regression junction thật. Không thay toànwalker hay claim atomic no-follow.
  A1 còn sửa đúng2next_actions adopt_project/pack để bỏ lời khuyên xóa.new, giữ2bản/
  xử lý theoowner. Đây là sửa nhỏ trong review, không feature/route/grant/schema mới.
  Ba target sync/pack/adopt sauA1 đạt/0skip; các case library giữowned/userREADME,
  legacy/duplicate/unreadable và junction đã quan sát đạt, không fullmodule.

**M3 chỉ đóng phạm vi hỗ trợ được xác định:** E02 là demonstration một agent biết bài,
SIMULATED-USER, không phải pilot người mới; E04 review/nội dung là khai báo, openermock,
OfficeCLI report không phải Word/Excel visualQA. T39 nhận legacyVI, same-schemaVI/EN và
refusal đã kiểm; P4 dùng UI theo allowlist và đường thủcông theoowner. Không tuyên mọi
host/schema/file đã hỗ trợ, không giảm yêu cầu T37/T38 hoặc gate phát hành.

**M4: snapshot đã chuẩn bị và kiểm kỹ thuật; chưa chốt đủ điều kiện pilot.**

| Artifact / bằng chứng | Giá trị cố định |
|---|---|
| Thư mục gốc chuẩn bị | `C:\Users\DELL\AppData\Local\Temp\law-m4-candidate-1.9.0-20261021-funwp_ju` |
| Snapshot gốc, giữ nguyên khi thử | Thư mục `candidate` dưới gốc trên; materialize(branding=False), VERSION1.9.0,261file |
| SHA-256 MANIFEST | `6fd21b9a923b1705481cad30f95194cc645d38b556b0d3d545cae4ced7500616` |
| SHA-256 toàn snapshot | `fb1c142e7a4da31fdeaf30dfacfa3444017bdaa35f6dd8c9daa2e61ff1aae093` (cách tính chính xác ở HANDOFF) |
| Source | HEAD `b13e375dbf256e726248b7d5b04142198bf25b19`, dirty=true; không phải clean commit/officialRC |
| Kiểm từ chính snapshot | check_package --release=0 (0lỗi/15warning), --verify=0 (0đổi/0thiếu), readiness usable=true/NTFS; bytes trước–sau giữ |
| Interpreter đã đo | Python3.11.9, jsonschema4.23.0, openpyxl3.1.5; readiness dùng đúng interpreter đã ghi trong HANDOFF, không tự cài |
| Chuẩn bị L/N | L/template là bảnchép snapshot; chưa tạo LAW projectA/B cho participant. N-A chỉ3nguồngiả cùngpath/hash, N-B chỉnguồnB; không filehướngdẫn LAW ởnhánhN |
| Nguồn A / oracle | Ba nguồn dưới examples/demo-project khớp đủ3hash kit; SHA kitDIEU_PHOI `c0772bbebf37f034c9008c59c760b70b8c16c970f51e311de45cd46b3e7ac0ff` |
| Nguồn B | coordinator-only/sources-B và bảnN-B có SHA `4c5496cf396e0463a4ca062e45a2631f7022464842e3888d983c4ff66e7a06ed`; không đưa oracle cho participant/AI thực hiện |
| Thay đổi Việc2 | Chưa áp dụng; đúng một câu3ngày→4ngày trên bảnchép ởthờiđiểm kit, hashđích `01b6286007dfb80466f324c94b282b2d9c1f9d8e3d3aedb0057c82b386e9bd35` đã tính trongbộnhớ |

Các hash trong bảng là SHA-256 đầy đủ. Không phát sinh host/provider call,
không người thử hoặc kết quả pilot. Snapshot/lab được giữ, không tự dọn hoặc ghi tiếp
vào snapshot gốc. Source đổi thì ghi delta và kiểm phầnảnhhưởng, không gọi candidate cũ
là đãkiểm bytesmới. Các quyền Git/CI/officialrelease vẫn chưa được cấp.

**Cập nhật chỉ định operator:** dùng dữ liệu mock, operator là observer. Diễn tập đã
thực hiện riêng theo mục0.9; không hỏi lại hai lựa chọn này. Pilot người mới theo kit
giữ PILOT_NOT_RUN nhưng đã chuyển sau MVP theo chỉ định tiếp theo tại0.10; không
chặn chuẩn bị MVP, không agent giả participant hoặc mở thêm feature để lấp chờ.

## 0.9. Diễn tập dữ liệu mock theo chỉ định operator — hoàn tất, chưa là pilot người mới

Ngày21/10/2026, operator chọn “bạn cứ dùng data mock, tôi là người quan sát”. Codex đã
thực hiện đúng3việc trên bản sao candidate M4; không giả người thử hoặc số đo cảm nhận.
Operator đã nhận vai observer, chưa có nhật ký quan sát/nhận xét/nghiệm thu của operator.

| Mốc diễn tập | Kết quả thực tế | Giới hạn nghiệm thu |
|---|---|---|
| Việc1: biên bản + so sánh | Tạo2MD có đường dẫn/hash nguồn; sổ A3nguồn, check0lỗi/6warning | Agent biết oracle, không chấm độc lập hoặc quy kết chất lượng do LAW |
| Việc2: mở lại + đổi nguồn | Tiến trình CLI mới tìm lại đúng2file/không viết lại; đổi source mock3→4ngày, sync báo1changed/revision2; r2 ghi5→4ngày/giảm1ngày, r1 và biên bản giữbytes; check sổ0lỗi/7warning | Cùng phiên AI/trong ngày; hash+sync phát hiện, không phải thử người dùng phát hiện kín hay gate publish |
| Việc3: biên bản B | Project/sổ/STATE/đầu ra riêng, chỉ dùng nguồn B; sổ1nguồn,0lỗi/2warning; không mang tên/số liệu A vào biên bản; cây A trước/sau B giữhash | Dùng lại phương pháp của agent, chưa chứng minh người mới tự tạo/tái dùng skill; demo A tích hợp trong package B vẫn giữ nhưng không dùng |

Artifact ở `mock-rehearsal-20261021` dưới gốc M4 mục0.8, hai project `A-Tiep-nhan` và
`B-Luu-tru`;4MD và fullhash/lệnh/hiệu chỉnh khai báo lưu ở đầu HANDOFF. Cả4khai báo
đã kiểm đạt bằng ownercheck_output; không thay cho đối chiếu nội dung. Profile project
mới đều0grant. Candidate/L-template/N-A/N-B không đổi; không ghi vào phiếu/INDEX pilot.

**MOCK_REHEARSAL_COMPLETED.** Diễn tập đã dừng; không thêm feature, test vòng mới hoặc
workorder mới cho diễn tập. T37/T38/M5 người mới vẫn NOT_RUN; operator đã chuyển
phần này sau MVP tại0.10. Không đo LAW-vs-native, thời gian/chi phí trải nghiệm hoặc
nativehost, không ghi số0 thay chưađo. M6 còn gate kỹ thuật/quyềnGit/CI/pháthành và
nghiệmthu cuối; mock không là USER_ACCEPTED hoặc miễn gate dữ liệu/phát hành.

## 0.10. Amendment MVP trước, phản hồi người dùng sau — operator chốt21/10/2026

**Quyết định có hiệu lực:** operator chỉ đạo “ko cần quá áp lực về người dùng thử,
tập trung hoàn thiện prototype, ra MVP thì sẽ có phản hồi từ user rồi hoàn thiện sau”.
Đây là thay đổi thứ tự/phạm vi nghiệm thu MVP do operator quyết định, không phải agent
tự hạ gate. Không tiếp tục yêu cầu tuyển người thử/host/lịch pilot để hoàn thiện MVP.

- **Chuyển sau MVP:** C-02/E06/M5, T37–T38; phần quan sát người thật của R6/T36/T48 và
  so sánh LAW/native. Trạng thái DEFERRED_POST_MVP/NOT_RUN, không biến thành PASS.
  Các kiểm kỹ thuật C-01, A/B độc lập, tiếp việc và stale đã nhận vẫn giữ bằng chứng.
- **Giữ trước MVP:** bảo toàn nguồn/dữ liệu/phần riêng, ranh giới quyền, xử lý nguồn đổi,
  tạo project/nâng cấp/phục hồi trong phạm vi đã chốt; hướng dẫn dùng được, package/
  integrity và các gate kỹ thuật phát hành hiện có. Chỉ công bố host/runtime đã có proof.
- **Không mở rộng prototype:** không thêm adapter/host/schema/engine, không generic
  finish, không refactor hoặc bổ sung tính năng từ gap tiện dụng. Lỗi chặn kiểm kỹ thuật
  hay luồng MVP mới được sửa hữu hạn rồi kiểm đúng chỗ.

**E07-A — hoàn thiện nguồn và preflight MVP: ACCEPTED_WITH_LIMITS / READY_FOR_RC_PREPARATION tại0.11.**

| Bước | Đầu ra nghiệm thu | Điểm dừng |
|---|---|---|
| 1. Chốt nguồn/docs | VERSION1.9.0/CHANGELOG/support matrix và hướng dẫn phản ánh đúng chức năng/giới hạn; so source với candidate M4, ghi delta thật, không thi công lại M3 | Không dùng yêu cầu người thử trước MVP; không tự nhận toàn host/roadmap đã đạt |
| 2. Kiểm tích hợp cuối | Dùng owner hiện có: kiểm HTML khớp, check_package --release, heuristic Python3.8 và full behaviour suite một lượt trên source cuối; ghi mọi failure/skip kèm lý do, không cộng evidence cũ thành fullsuite | Không --skip-check, không đặt nested override thủ công; lỗi cụ thể mới sửa/kiểm đúng phần, không thêm vòng fullsuite mặc định |
| 3. Bàn giao sẵn sàng RC | HANDOFF có source identity/diff, lệnh/kết quả, blocker hữu hạn, support limits và checklist nghiệm thu RC tạo/mở UI/verify/nâng cấp/khôi phục; Codex review đúng phần rủi ro | READY_FOR_RC_PREPARATION hoặc BLOCKED có lỗi cụ thể; không chờ pilot, không tự stage/commit/push/build release/official/host-global-admin |

E07-A là phần chuẩn bị của D-02, không thêm workorder file hoặc milestone sản phẩm.
Worker do operator giao Claude/chọn model-effort; Codex điều phối/review theo8.3–8.4.
Sau khi nguồn sẵn sàng và có quyền thao tác tương ứng mới tạo RC, nghiệm thu gói và
bàn giao MVP. Quyết định ưu tiên MVP không tự cấp quyền Git/phát hành đã bị giới hạn.
Pilot có cấu trúc và cải tiến từ feedback làm sau MVP; không tuyên roadmap gốc hoàn tất
hoặc hiệu quả người mới đã được chứng minh chỉ từ các kiểm kỹ thuật. MVP nội bộ được bàn giao theo0.11; CI/official là phần phát hành chính thức riêng, không gắn ngược thành điều kiện dùng RC1 nội bộ.

## 0.11. E07-A đã nhận — sẵn sàng chuẩn bị RC,21/10/2026

**ACCEPTED_WITH_LIMITS / READY_FOR_RC_PREPARATION.** Worker không sửa code/test/docs
trong E07-A; Codex nhận preflight sau kiểm Main và reviewer độc lập Sol6.1Medium.
Không có blocker sản phẩm mới xác định, không giao lại tranche hay chạy lại fullsuite.

| Bằng chứng | Kết luận |
|---|---|
| Main materialize source→so M4 |261file đúng paths/bytes; SHA toàncây fb1c142e… và MANIFEST6fd21b9a… khớp đầy đủ HANDOFF;5hash bảo vệ giữ |
| Main checks trên source |package0lỗi/15warning,10HTMLkhớp, heuristic3.8 không vấnđề; không phải runtime3.8 |
| Worker full behaviour |1492test/856.985s/6skip theo báo cáo;5symlink thiếu quyền+1chỉngoàiWindows. Chưa có rawlog locator, không nhận là Main đã kiểm độc lập |
| Timeout900s |43.015s headroom là rủi ro, không blocker bắt buộc đổi; giữ gate hiện hành, xử lý nếu RC thật timeout |
| Support |Windows11/Python3.11.9 đã đo local; officialsupport/CI chưa xác nhận, không nhận toàn host |

**E07-B — ACCEPTED_WITH_LIMITS: RC1 sẵn sàng bàn giao dùng thử MVP nội bộ.**
Sau câu hỏi nêu rõ stage/commit phần bảo trì hiện tại và dựng RC nội bộ, operator
trả lời “vậy thì tiếp”; quyền này áp dụng đúng E07-B, không hỏi lại. Phạm vi gồm
phần bảo trì LAW hiện có ở chính repo này (inventory review:426path khi mở toàn
untracked/129mục status mặc định, nhiều tranche), rồi owner build_release tạo RC
nội bộ1.9.0 không branding. Chưa push/official/CI network/host-global-admin/CVF cha.
HEAD nguồn hiện tại b13e375dbf256e726248b7d5b04142198bf25b19, dirty=true; không reset/
clean/ẩn dirty hay cấp quyền mới cho profile. Nhóm file/scope ghi ở đầu HANDOFF.

Khi thi công: ghi commit/hash, gate JSON và SHA ZIP; nghiệm thu giải nén/verify,
tạo project, UI, nâng cấp giữ dữ liệu và khôi phục trên bản sao. Resume chỉ tiếp giao
dịch dở; rollback phục hồi giao dịch dở; nâng cấp hoàn tất thì khôi phục từ bản sao
lưu đã giữ trước nâng cấp. Đây là brief trước thi công; kết quả RC1 hiện hành ở kết luận bên dưới. Toàn gate kỹ thuật, supportlimits
và quyền phát hành chính thức giữ; C-02/người mới sau MVP không chặn E07-B.

**Brief E07-B hữu hạn:** xác nhận Git root/scope và không gộp staged ngoài quyền;
hoàn tất ghi chú chuẩn bị rồi stage/commit phần bảo trì được phép (không clean/reset/
amend/force hoặc sửa quyền PROJECT/profile). Freeze HEAD/bytes và giữ worktree sạch
trong lúc gate chạy. Dựng `--rc 1 --no-branding` nếu tên chưa có, không ghi đè RC cũ;
không --skip-check/nested override/tự nâng timeout. Giữ stdout/stderr build và gate
JSON để review; nếu owner không lưu rawsuite thì nêu rõ. Ghi đủ skip thực, phân biệt
gate passed với test skipped. Kiểm repeatability từ
cùng source bằng recipe hiện có; các lần gọi build_release vẫn giữ đầy đủ gate.
Nghiệm thu RC trên thư mục mới/bản sao, giữ nguồn và phần riêng bằng hash. Ghi HEAD
của gói/gate trước khi cập nhật HANDOFF/STATE sau build; metadata mới có thể làm cây
dirty, không được che bằng reset. Lỗi chặn thì ghi nguyên nhân cụ thể, không tự mở
feature hoặc thay gate. Bàn giao IMPLEMENTED_PENDING_REVIEW — E07B_INTERNAL_RC;
Codex nhận gói sau review, Worker không tự tuyên official hoặc MVP đã nghiệm thu.

### Kết luận review E07-B/RC1 —21/10/2026

Codex nhận **E07B_INTERNAL_RC / ACCEPTED_WITH_LIMITS** sau reviewer độc lập
Sol6.1Medium và kiểm Main trên artifact thật. Không còn blocker sản phẩm xác định
trong scope RC1; sẵn sàng bàn giao MVP nội bộ, chưa USER_ACCEPTED/official/CI.

| Đối tượng | Bằng chứng / giới hạn |
|---|---|
| Source/gate/ZIP |commit6f39c60b77d368793612541f546ca92688289518; gate4passed/dirtyfalse; ZIP261file/1177698byte, SHA3b0ea0888496a653b9c1ece77d1a13fdd13d5996ffdc2bc5f212775026c703f4 |
| Main verify |ZIP khớp owner-normalized source projection; giải nén mới verify0đổi/0thiếu |
| Repeatability archive |từ git archive commit bất biến,2stage mới qua owner projection/manifest và nguyên AST ZIPwriter; cả2SHA bằng RC1. Không CLIbuild/fullsuite/gatepatch/gateJSON mới hoặc đổi timeout |
| Hai full rebuild |build2/build3 thật sự failed behaviour timeout900s trước tạoZIP; giữfailed. Archiveprobe không chứng minh fullbuild ổn định thời gian; không mở tranche hiệu năng khi chưa có nguyên nhân cụ thể |
| Upgrade/restore |Main so fixture thật:7file riêng giữbytes, package rawbytes khớpRC trừ1file chủ ý sửa và.new đúng; restored229file khớp preupgrade. Profileprojectmới0grant; logUI0errors, không chứng minh từngpage/visual |

Đủ đóng yêu cầu repeatability bằng kiểm riêng đúng bước tạoarchive của nguồn đã
qua gateRC1; không cần thêm fullsuite để so cùng ZIP. Mọi lệnh CLIbuild_release tương
lai vẫn chạy đầy đủ gate; không nhận failed thànhpassed hoặc waive gate. Phép kiểm,
fullhash, lỗi harness đã sửa một lần và limits ghi ở đầu HANDOFF. Không sửa code/gate,
không ghi đè RC1; currentrepo dirty metadatareview sau commit build là có giải trình.

**Điểm dừng trước feedback:** giao `dist/local-agent-workspace-v1.9.0-rc1.zip` và
`.gate.json` cho operator dùng thử/nhận MVP nội bộ. Không tự mở feature/pilot hoặc
vòng build mới. T37/T38 vẫn sauMVP; CI/phát hành chính thức chưa được cấp quyền và
không được tuyên hoàn tất. Chưa đóng toàn roadmap gốc từ verdict RC1 nội bộ.

**Đường đi sau bàn giao RC1:** operator nhận/dùng MVP nội bộ → ghi feedback thật
trong quá trình làm việc → Codex phân loại và chốt phạm vi sửa với operator → Claude
sửa đúng finding được chọn, Codex review. Không có feedback thì giữ baseline, không
tạo backlog tính năng hoặc tranche code mới. Kit C-02 chỉ dùng khi cần pilot có cấu
trúc, không áp thêm thủ tục cho mọi phản hồi. CI/official tiếp tục là phần riêng chưa
thực hiện, không chặn dùng MVP nội bộ và không được tự coi là đã hoàn tất.

**Chốt bàn giao nguồn21/10:** operator đã yêu cầu push lên
`https://github.com/CVF-Ecosystem/local-agent-workspace.git`. Đích là nhánh đang làm
`branding-tokens`, fast-forward nguồn6f39c60b và commitreview metadata; không merge
main/forcepush, không tạo GitHub Release hoặc upload ZIP. RC1 và gate vẫn ở dist
local theo hash đã review, không đổi hoặc dựng lại. Đây là chốt baseline nguồn MVP
để bàn giao; tiếp theo feedback sau dùng. Không suy push là CI xanh, official hoặc
người mới đã kiểm thành công. Ghi quyền/kiểm remote/payload ở đầu HANDOFF.

### Công bố MVP prerelease để thu feedback —21/10/2026

Operator yêu cầu phát hành version mới và nêu rõ chưa phải bản final, đã có phần
feedback. Đã công bố **[v1.9.0-rc1 — MVP dùng thử](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc1)**
lúc2026-10-21T05:22:38Z, prerelease=true/draft=false/latestfalse; tag trỏ đúng source
6f39c60b77d368793612541f546ca92688289518 tạo RC1. VERSION gói vẫn1.9.0 theo policyRC.
Không cần build lại hoặc sửa nhãn trong ZIP đã review. Lateststable vẫnv1.8.0.

Release có3asset: ZIP đã nhận, gate JSON và checksum đầy đủ2file. Main tải lại cả3
asset, hash trùnglocal/serverdigest; releasebody/tag/assets đã kiểm thực. Notes nêu
hướng dẫn bắt đầu/nâng cấp/backup, limits và cách gửi feedback qua form kèmZIP
`docs/FEEDBACK_FORM_VI_EN.md`/[GitHub Issues](https://github.com/CVF-Ecosystem/local-agent-workspace/issues/new?template=phan-hoi.md).
Không tạo thêm hệ thống feedback hoặc ghi nhận phản hồi chưa xảy ra.

**Mốc MVP dùng thử đã bàn giao; bước tiếp là feedback thật.** Chưa final/stable,
chưa CI/officialsupport1.9.0; T37/T38 vẫn sauMVP. Các fullbuild timeout trước đây giữ
failed, không sửa gate/timeout hoặc tuyên toàn roadmapgốc đã đạt. Giữ baseline cho
đến khi có finding cụ thể được operator chốt ưu tiên; final là quyết định sau feedback.
Fullhash/lệnh/quyền và review độc lập publication ở đầu HANDOFF.

### Corrective review ex-agent L19-01–03 —21/10/2026, SOURCE_REVIEW_ACCEPTED_CI_PENDING

Review ban đầu chỉ đọc ZIP. Sau đó operator giao “sửa đi”: sửa trên nhánh
`fix/l19-ci-diagnostics`, dùng worker Sol6.1Medium và reviewer độc lập.
Main hoàn tất test sau khi worker CI hết dung lượng; giữ runtime/schema/pin.
Đã đạt 103 test tập trung (0 skip), package 0 lỗi/15 cảnh báo và HTML 10 trang khớp.
Reviewer độc lập không thấy blocker; source `901e1d1` đã push nhánh sửa.
[CI39560119618](https://github.com/CVF-Ecosystem/local-agent-workspace/actions/runs/39560119618) đang chạy, chưa có kết quả.
Chưa thay artifact RC1; không nhận official hoặc CI xanh. Chi tiết tại đầu HANDOFF.

| Finding | Disposition sau đối chiếu | Phạm vi corrective đã giao |
|---|---|---|
| L19-02 diagnostics |Xác nhận bằng ZIPexportthật với toànpathPython giả; sys.executable ngoàihome vẫnlộ, app.pyRC1 cũngcó. Không khẳngđịnh key/source tựgửi hoặc causalfield trongCI ZIPchưađọc |Ưu tiên exportallowlist/tokenizepathfields, giữlocalpanelpath; kiểmZIPgiảhome/project/toolcache/slash, không bỏtestprivacy |
| L19-01a fixtureEOL |Xác nhậnGitScout18LF/0CRLF khiến negativereplace no-op; ownermixedguard vẫnrefuse |FixtureLF/CRLF/mixed rõ và mutationkhác, giữguard |
| L19-01b rawpins |Helper chứngminh7artifact lịch sử LF→CRLF khớp pin cũ; pin khác/câyv2 vẫnkhớp |Giữexpectedpin, bảo toàn đúng7rawartifact cócăn cứ; khôngrefreshhashall |
| L19-01c profiletest |Xác nhậnpositiveWindowstests chạytrênPOSIX rồi kỳvọngplan/eligible |Giới hạn đúngpositiveWin/NTFS; giữtestrefusal/cross-platform, không blanket skip/nới runtime |
| L19-01d deepJSON |RawUbuntu3.12classification khác; sourcekhôngMAX_DEPTHđộc lập, fixturevalid thiếuversion |Đã chọn test RecursionError bằng injection tại decoder; giữ loader và contract, không thêm MAX_DEPTH |
| L19-03 continuity/release |main đãmergePR6; CIrun39548822713 đúng1ca3 có5/5jobfailedBehaviour. PublicprereleaseRC1 thực sựđãcó; latestv1.8 làstable |Đã đồngbộSTATE/roadmap/HANDOFF; không merge/checkout main. Sửa cáchđọc latestAPI, giữartifacthistory và CIred riêng |

Main đã đọc rawfailedlogs Win3.12:1492test/10failure/40skip; Ubuntu3.12:1492test/
13failure2error/396skip. Cả5job package/HTMLsuccess nhưng RCbuild/uploadskipped.
Những kết quả này hiện là**CIđãchạyvàđỏ**, thaycho “chưacóCI”; không dùng localRC1
để ghiCIpassed. RC1 vẫnprerelease, khôngfinal; không tựrút/cấm toànMVP hoặc miễn sửa
privacy. Gópý “chưa public1.9artifact” không đúng trạngthái releaseđãxácnhận.

**Corrective đềxuất là hữu hạn:** diagnostics + các test/EOL/pin/profile/parser có
finding, rồi kiểmđúngphạmvi và CIđúngcommit trongquyền đượcgiao. Không tựchạy script
đínhkèm, không sửacode/pin/gate hoặc push/release/CIrerun tronglượt xemgópý này.
Không mở host/engine/OCR hoặc chươngtrình audit mới; không cần tuyển người thử.

## 1. Mục tiêu và quyết định đã chốt

LAW cung cấp bộ khung local để cá nhân làm việc lâu dài bằng agent/model của ứng dụng họ chọn. Giá trị tích lũy nằm ở nguồn dữ liệu, kỹ năng cá nhân, quy tắc ổn định, vai trò rõ ràng và khả năng tiếp tục qua nhiều phiên.

| Quyết định | Hệ quả thiết kế |
|---|---|
| User tự chọn account, ứng dụng, model và chi phí | Không nhúng tài khoản hoặc bắt mua API riêng; cấu hình theo host thực tế |
| Agent chính trong phiên điều phối | Việc nhỏ làm trực tiếp; gọi vai khi có ích và trong quyền đã cấp |
| Scout / Worker / Reviewer và vai trò lĩnh vực là thành phần cốt lõi | Có nhiệm vụ, đầu vào/đầu ra, quyền ghi và preset; không đẩy toàn bộ roles sang phạm vi tùy chọn |
| Nhiệm vụ ổn định; preset model/effort cố định theo từng vai, user đổi được | Bộ khung cung cấp mặc định cụ thể cho từng vai trên host hỗ trợ; lựa chọn hiệu lực của project tách khỏi hợp đồng nhiệm vụ |
| Dữ liệu và skill cá nhân tăng lâu dài | Có ID, revision, provenance, tiếp nhận và migration; nâng cấp giữ phần riêng |
| Kế thừa kiểm soát CVF phù hợp, kể cả folder .cvf khi cần (operator chốt 17/10) | .cvf tự đủ cho LAW; quyền/bảo toàn/bằng chứng quyết định mức kiểm. Baseline hợp tác hẹp và tích hợp candidate đã nhận; thứ tự tiếp A–D theo I-02 rev1 ở mục6.2, không đồng nghĩa release/activation |
| Tôn trọng năng lực native | LAW quy định trách nhiệm, nguồn, quyền và đầu ra; tận dụng suy luận/OCR/công cụ tài liệu/gọi agent của host |
| File đọc được ngoài LAW | Nguồn và kết quả không phụ thuộc session ID hoặc dịch vụ trung tâm |
| Provider thay đổi theo thời gian | Tra tài liệu chính thức khi viết adapter và trước release; ghi app, phiên bản và phần đã quan sát |

Ngoài phạm vi mặc định: runtime multi-agent riêng, daemon/watchers, dịch vụ tài khoản, vector database, engine OCR/Office, nhập nguyên governance CVF hoặc tích hợp nguyên ứng dụng VBQPPL. Không đặt mục tiêu kiểm soát trí thông minh model hoặc bắt mọi việc đi qua đủ ba vai.

## 2. Mốc hiện trạng và khoảng trống

Snapshot local: nhánh `branding-tokens`, HEAD `b13e375dbf256e726248b7d5b04142198bf25b19`, package `v1.8.0`. Không khẳng định trạng thái remote/CI hiện tại.

| Đang có / owner | Dùng lại | Cần mở rộng |
|---|---|---|
| AGENTS, PROJECT, STATE, HANDOFF, INDEX, SKILL_INDEX | Quy tắc nguồn, continuity ngắn, tiếp nhận skill | Quyền phân công, vai trò, mâu thuẫn trạng thái, nguồn tăng dần |
| `tools/library.py` | Đọc/tìm danh mục, khởi tạo workbook mẫu | Writer cho ID, revision, delta, dependency; `_INDEX.xlsx` được khởi tạo khi cần, chưa có trong mọi project |
| `tools/transaction.py` | Hash, thay file, sao lưu/phục hồi hiện có | Ràng buộc snapshot từ lúc đọc; `add()` hiện lấy hash lúc đăng ký thay đổi. Cần xử lý tiến trình song song/Excel; check rồi replace không phải atomic compare-and-swap |
| `tools/pack.py`, `tools/install_skills.py` | REVIEW, confirmation digest, cài gói lĩnh vực, điều kiện xuất native | Vai lõi ở `roles/`; chỉ mở schema vai trong gói lĩnh vực khi có nhu cầu mở rộng đã được kiểm. Projection vai lõi thuộc R4 adapter/profile |
| `tools/app.py` và UI/API | Bảng điều khiển local, công cụ project/skill/gói | View cùng sổ, artifact liên quan, nhãn revision/stale, writer chung CLI/UI |
| Init/adopt/upgrade/build/check và release templates | Bảo toàn file user, manifest, build sạch | Ownership cho profile, sổ mới, role và projection trước release |

Bằng chứng lịch sử 17/10: `full_suite.log` ghi **129 test đạt**; RC gate JSON ghi **4 gate đạt**, `dirty: true`. Báo cáo diễn giải ba gate không thay thế JSON. Đây là bằng chứng của lượt chạy/snapshot được ghi, không chứng minh chức năng mới. Không chạy lại suite/provider trong lượt biên soạn này. Ghi nhận Claude CLI/Cowork trước đây không chứng minh mọi app/host/model/effort.

## 3. Nguyên tắc quản lý và điểm thực hiện trong LAW

| Nguyên tắc | Owner LAW đích | Thực hiện vừa đủ |
|---|---|---|
| Thứ bậc chỉ dẫn và nguồn có thẩm quyền | AGENTS + PROJECT | Quy tắc khung, phạm vi user; nguồn nhập là dữ liệu, không tự thành lệnh |
| Tiếp tục có căn cứ | STATE + HANDOFF | Việc đang dở đọc trạng thái/artifact liên quan; việc nhỏ tự đủ ngữ cảnh làm trực tiếp |
| Quyền và trách nhiệm rõ | EXECUTION_PROFILE + mô tả việc | Main tích hợp; vai phụ không tự mở scope/quyền |
| Nguồn gốc, revision, phạm vi đã đọc | Sổ nguồn + artifact | Ghi locator, phần đọc/chưa đọc; không báo quét hết từ danh sách file |
| Review bằng chứng đã trả | Hợp đồng role + bước tích hợp | Kiểm đúng yêu cầu; không dựng lại toàn bộ việc worker |
| Một đầu mối ghi chung | Writer dùng chung | Snapshot, khóa, phục hồi; các vai gửi đề xuất |
| Bảo toàn dữ liệu/quyền khi nâng cấp | Upgrade/build + ownership | Không mang quyền, nguồn và STATE của A vào mẫu/B |
| Lỗi lặp thành kiểm soát | Rule tại owner + công cụ hiện có | Thêm phép kiểm ở điểm dễ sai, tránh registry/checker trùng |

Các nguyên tắc và cách thực hiện cần thiết được viết ngay trong LAW; người nhận không phải mở kho hay chuẩn quản trị bên ngoài để vận hành. Mỗi quy tắc đặt tại file phụ trách tương ứng trong bảng, tránh thêm thủ tục bàn giao hoặc phê duyệt cho việc nhỏ.

Nói rõ mức kiểm soát: **hướng dẫn agent / công cụ LAW kiểm được / host cưỡng chế được**. Câu “chỉ đọc” trong role không tự tạo sandbox. Schema/hash không chứng minh suy luận đúng.

## 4. Treeview đích và ownership

### 4.1 Bộ mẫu và project độc lập

```text
Thu-muc-cua-nguoi-dung/
├── LAW-Bo-mau/          # bộ mẫu sạch; cập nhật có chủ đích
├── Du-an-A/             # nguồn, profile, skill và công việc riêng
└── Du-an-B/             # độc lập; không tự nhận dữ liệu/quyền của A
```

Không đặt project đang làm trong bộ mẫu. Dự án cũ được adopt tại chỗ, giữ ngoại lệ thư mục user chọn một lần; không bắt chuyển hàng loạt cho khớp cây mẫu.

### 4.2 Cây dự án mục tiêu

**GIỮ**: vùng hiện có. **DỰNG 17/10**: cây nguồn đã tạo nhưng chưa nối native. **MỞ Rn**: mở rộng vùng/chức năng hiện có. **MỚI Rn**: chưa triển khai. **SINH Rn**: tạo khi có nhu cầu ở mốc đó. `<...>` là biến. Cây mô tả đích, lược bớt file ít liên quan; không khẳng định mọi file đã tồn tại.

```text
Du-an-A/
├── APP.bat / APP.command, SETUP.bat / SETUP.command    [GIỮ]
├── START_HERE.html, START_HERE.en.html, README.md     [MỞ R1/R6]
├── AGENTS.md, PROJECT.md                             [MỞ R1/R4]
├── CLAUDE.md, GEMINI.md                              [MỞ R4: dẫn về quy tắc chung]
├── VERSION, MANIFEST.sha256, CHANGELOG.md, LICENSE    [GIỮ]
├── .cvf/                                            [DỰNG G-00/G-01: thiết kế, chưa enforcement]
│   ├── README.md, PROVENANCE.md                      [phạm vi, giới hạn, nguồn thích nghi]
│   ├── rules/CONTROL_RULES.md, ROUTING_POLICY.json   [Main và vai phụ cùng chịu quy tắc; JSON canonical routing]
│   ├── contracts/CONTROL_CONTRACT.md                 [ngữ nghĩa task/grant/review/effect/result]
│   ├── contracts/control.schema.json, examples/      [G-01: schema 2020-12, ví dụ EXAMPLE]
│   └── checks/README.md, control_check.py           [đặc tả + checker chỉ đọc G-02, chờ review]
├── .agent/
│   ├── STATE.md, HANDOFF.md                          [MỞ R1; giữ khung ngắn]
│   ├── INDEX.md, SKILL_INDEX.md, PENDING_LESSONS.md    [MỞ R1/R4; không chép lại sổ]
│   ├── PACKAGE_INFO.json                            [SINH: metadata công cụ hiện có]
│   ├── EXECUTION_PROFILE.json                       [MỚI R4: lựa chọn/quyền project]
│   └── runtime/                                     [GIỮ; không phân phối dữ liệu chạy]
│       ├── library/                                 [SINH R2: lock, staging, cache]
│       ├── governance/                              [SINH G-02/G-03: receipt, không vào ZIP]
│       └── native-agents/                           [SINH R4: receipt projection]
├── references/                                      [GIỮ]
│   ├── _INDEX.xlsx                                  [SINH/MỞ R2/R3: sổ chung]
│   ├── legal/                                       [GIỮ: nguồn pháp lý]
│   ├── policies/                                    [GIỮ: quy định nội bộ]
│   ├── templates/                                   [GIỮ: mẫu nghiệp vụ]
│   └── source-documents/<nhom-do-user-chon>/          [GIỮ/MỞ R1]
├── working/<work-id>/                                [SINH R5 khi cần giao việc]
│   ├── TASK.md                                      [scope, revision, đích đầu ra]
│   ├── scout/                                       [kết quả/đề xuất delta]
│   ├── worker/                                      [bản làm việc]
│   └── review/                                      [kết luận đúng phạm vi]
├── output/                                          [GIỮ/MỞ R3: bản giao + quan hệ nguồn]
├── archive/                                         [GIỮ; tạo nhánh khi cần]
│   ├── source-versions/                             [SINH R3: bản nguồn cần giữ]
│   ├── source-register/                             [SINH R2: phục hồi sổ]
│   └── completed-work/                              [SINH R5: việc cần giữ lịch sử]
├── roles/                                           [DỰNG 17/10: vai trò lõi]
│   ├── README.md                                    [ranh giới và trạng thái]
│   └── <scout|worker|reviewer>/
│       ├── agent.md                                 [nhiệm vụ, input/output, giới hạn]
│       ├── config.json                              [preset thử thi công; host PENDING_R4]
│       └── checks.md                                [điều kiện kết quả đạt]
├── packs/                                           [GIỮ: gói mở rộng lĩnh vực]
├── skills/
│   ├── local/shared/                                [GIỮ: phần dùng chung]
│   ├── local/project/                               [GIỮ/MỞ R6: skill cá nhân]
│   ├── local/packs/<pack-id>/                        [GIỮ/MỞ R4: gói lĩnh vực đã cài]
│   ├── external/                                    [GIỮ: chuẩn tiếp nhận hiện có]
│   └── inbox/                                       [GIỮ: ứng viên chưa tự kích hoạt]
├── assets/                                          [GIỮ: thương hiệu, font, tài sản]
├── docs/, en/, examples/                             [MỞ R1–R7: hướng dẫn, mẫu sạch]
├── tools/                                           [MỞ R2–R7: owner hiện có]
└── <thu-muc-native-cua-host-da-chon>/                 [SINH R4 sau xác nhận]
    └── <law-pack-role>.<dinh-dang-host>               [projection tránh trùng tên]
```

Kho phát triển còn có `roadmap/`, `tests/`, `.github/`, `feedback/`, `release_templates/`, `dist/`; áp dụng chính sách package hiện có, không chép toàn bộ sang user. `roadmap/` không nằm trong ZIP. README sản phẩm/VI/EN cập nhật cây chức năng đã có theo từng mốc; không thêm link từ ZIP tới roadmap bị loại khỏi ZIP.

**Cây nguồn đã dựng:** `roles/` và ba thư mục vai, mỗi thư mục có `agent.md`, `config.json`, `checks.md`. `config.json` có `implementation_trial` theo mốc kiểm 17/10/2026, revision 2 ở 8.4; trạng thái tích hợp host vẫn `PENDING_R4` và không được host tự nạp. Vai trò lõi ở `roles/` vì `packs/` hiện áp dụng tiếp nhận `REVIEW` cho gói lĩnh vực; không để Scout/Worker/Reviewer phụ thuộc việc cài gói tùy chọn. R4 cần chốt preset sản phẩm, profile, adapter và bằng chứng gọi thật trước khi coi vai có thể dùng.

**Vùng tạo khi phát sinh:** `_INDEX.xlsx` khi `library.py init`; `.agent/runtime/library/` khi writer hoạt động; `working/<work-id>/` khi có việc nhiều bước; `archive/source-versions/`, `archive/source-register/`, `archive/completed-work/` khi có bản cần giữ; thư mục native sau khi chọn host và kiểm xung đột. Không đặt file giữ chỗ vào các vùng dữ liệu cá nhân hoặc runtime để giả lập khả năng đã triển khai. Việc nhỏ không cần TASK hay bản tóm tắt dư.

### 4.3 Quyền sửa và nâng cấp

| Vùng | Chủ quản | Quy tắc |
|---|---|---|
| AGENTS, `roles/`, tools, hướng dẫn khung | Bộ khung | Nâng cấp có diff, nhận biết sửa riêng; projection không phải nơi sửa nhiệm vụ |
| PROJECT, EXECUTION_PROFILE, personal skill | User/project | Giữ qua upgrade; sửa theo quyền đã có; không tự mang về mẫu |
| File nguồn | User | Không tự xóa/di chuyển/ghi đè; nhắc đích và kiểm sau khi user chuyển |
| `_INDEX.xlsx` | Sổ chung của project | Writer LAW duy nhất; phát hiện user/Excel sửa ngoài công cụ |
| STATE/HANDOFF | Main/đầu mối được giao | Vai phụ trả kết quả, không cùng ghi |
| Gói cài và xác nhận | Cơ chế pack hiện có | Tái dùng confirmation digest; nội dung đổi phải reconcile |
| Native projection | Công cụ xuất theo profile | Không đè native/file user; dấu quản lý, diff và phục hồi |
| Runtime/cache/receipt | Công cụ | Dựng lại được; không chứa quyền duy nhất hoặc thành nguồn sự thật riêng |

EXECUTION_PROFILE là cấu hình bền, không phải cache. Phải thêm ownership vào init/adopt/upgrade/build/check trước release.

## 5. Sổ nguồn và dùng lại đầu ra

### 5.1 Hợp đồng dữ liệu

`references/_INDEX.xlsx` quản lý nhận diện, vị trí, revision, trạng thái và quan hệ. File gốc là căn cứ nội dung. `.agent/INDEX.md` là điểm tìm đường; API/JSON/cache/UI là view của cùng sổ.

Các nhóm dữ liệu, triển khai tăng dần:

- **Nguồn:** namespace/project, SourceID ổn định, path/loại, hash/thời điểm quan sát, revision, tình trạng thiếu/lỗi/chưa đọc; provenance khi nhập từ project khác.
- **Phiên bản:** revision cũ/mới, thay đổi, locator bản giữ lại; không hứa phục dựng bản cũ nếu chưa lưu bytes.
- **Nội dung:** phần/tóm tắt/trích xuất, phạm vi đọc, vị trí nguồn, loại dữ kiện/suy luận, source revision, người/công cụ tạo.
- **Kiểm/quyết định:** phần đối chiếu, căn cứ, giới hạn, quyết định user gắn đúng phiên bản; tách xác nhận khỏi lời khai agent.
- **Artifact/phụ thuộc:** ArtifactID, path/revision, loại đầu ra, quan hệ nhiều nguồn/nhiều kết quả, phần cần xem lại khi input đổi.

Giữ tương thích `Danh mục`, header hàng 4 mà reader hiện dùng. R2 bổ sung metadata; R3 bổ sung phiên bản/nội dung/kiểm/quan hệ. Có thể gộp sheet nếu giữ đủ ngữ nghĩa, khóa và truy vấn; giảm số sheet không thay thế lịch sử revision. Layout cụ thể chốt ở thiết kế R2/R3.

Đổi tên/di chuyển giữ ID khi đủ căn cứ; copy/trùng hash/cùng tên không tự gộp. File mất ghi trạng thái, không xóa lịch sử. Hash không đổi không chứng minh hiệu lực hay nội dung vẫn hiện hành. Nguồn A → phân tích B → báo cáo C: A đổi thì đánh dấu đúng dependency ở B/C cần xem lại. B được dùng làm input với lineage, vẫn giữ nhãn suy luận/giới hạn, không trở thành chứng cứ độc lập chứng minh A.

### 5.2 Quét và ghi an toàn

Quét metadata để phát hiện thay đổi; đọc nội dung theo công việc. Phân biệt file tìm thấy, xử lý được, bỏ qua và lỗi. Không đọc toàn thư viện mỗi phiên. Nguồn sai chỗ: nhắc đúng đích; user báo đã chuyển thì kiểm thực. Ngoại lệ project cũ lưu tại PROJECT.

Writer: **đọc snapshot → đề xuất delta → kiểm schema/quyền/path/revision → khóa → đối chiếu snapshot → ghi tạm → đọc lại/kiểm → thay bản chính**. Xung đột thì dừng thay và reconcile có phạm vi. Delta Scout là trung gian, sổ là nơi chốt.

- Hash kỳ vọng gắn từ lúc đọc, không đợi `Transaction.add()` trong `tools/transaction.py`. Khóa dùng chung CLI/UI/tiến trình; Excel ngoài khóa LAW cần phát hiện thay đổi/phục hồi. Không hứa loại tuyệt đối race với chương trình không hợp tác.
- Dùng transaction hiện có, bổ sung phần thiếu; không tạo engine song song. Reader `data_only=True` không được dùng làm đường save gây mất công thức.
- Kiểm path sau khi giải symlink/junction vẫn trong scope, link và khóa; không bỏ nguồn chỉ vì tên `README.md`, phải xét ownership. Không chạy macro/link/lệnh trong nguồn. Phép kiểm máy không xác minh ý nghĩa trích xuất.
- Sổ hỏng/thiếu sheet/dependency, hết dung lượng hoặc thiếu quyền phải báo đúng; không coi là rỗng và dựng sổ thay thế ngầm.
- Quét lặp không đổi không sinh dòng/revision/backup vô hạn. Retention cho backup/cache theo nhu cầu phục hồi, không dọn nguồn gốc tự động.

### 5.3 Trải nghiệm thư viện

UI xem tổng quan, tìm/lọc metadata/nội dung đã lưu, hồ sơ nguồn, phụ lục/liên quan, kết quả và phần cần xem lại. Mở danh mục không tự quét, gọi model/OCR hoặc tạo lại báo cáo. Hiện thời điểm cập nhật; tìm metadata không gọi là tìm toàn văn.

Chọn input mang đúng ID/revision/locator; sao chép yêu cầu không được báo đã dispatch. Phân biệt rỗng, không khớp bộ lọc, nguồn mất, sổ lỗi và thiếu quyền. Mở kết quả đúng bản; phiên sau chỉ đọc phần cần.

## 6. Vai trò, profile và điều phối

| Vai | Nhiệm vụ ổn định | Đầu ra/quyền mặc định LAW |
|---|---|---|
| Main | Hiểu yêu cầu, chọn cách làm/vai, giải quyết mâu thuẫn, tích hợp | Đầu mối giao tiếp và ghi chung trong scope được giao |
| Scout | Tìm nguồn, metadata, phần cần đọc và delta | Locator/revision, phần thiếu, đề xuất index; không sửa sổ chung |
| Worker | Làm nhiệm vụ bằng nguồn/native tool phù hợp | Artifact ở vùng được giao, căn cứ/giới hạn; không đổi nguồn/quyền |
| Reviewer | Đối chiếu yêu cầu và bằng chứng | Phát hiện, điều kiện đạt/chưa đạt; không tự nhận user acceptance hoặc làm lại toàn bộ |
| Vai lĩnh vực | Chuyên môn qua gói đã tiếp nhận | Cùng hợp đồng và kiểm soát nguồn; tên vai không tạo đặc quyền |

**Quyết định đã chốt:** mỗi vai lõi có preset model/effort mặc định cố định theo host được hỗ trợ, do maintainer chuẩn bị trong `roles/<vai>/config.json`. Agent dùng cấu hình hiệu lực của vai khi được gọi, không tự chọn lại model/effort mỗi lần. User có thể đổi các giá trị này theo hướng dẫn hoặc cho phép một fallback cụ thể; nhiệm vụ chuẩn vẫn giữ nguyên. Giá trị cụ thể được chốt khi triển khai adapter, theo khả năng host/account; trường không hỗ trợ phải ghi rõ, không giả lập đã áp dụng. Vai từ gói lĩnh vực có owner riêng sau tiếp nhận.

**Ba tầng cần nối ở R4:** (1) `AGENTS.md` và adapter `CLAUDE.md`/`GEMINI.md` đưa quy tắc chung tới Main nếu host thực sự nạp chúng; (2) `roles/<vai>/agent.md`, `checks.md`, `config.json` là nguồn hợp đồng/preset do LAW quản lý; (3) adapter xuất định nghĩa subagent đúng schema và vị trí native của **host đã chọn**, gắn model/effort hiệu lực từ profile, kiểm xung đột và lưu receipt. Main chỉ gọi vai khi host đã đăng ký nó và có quyền giao việc cho phạm vi đó. Nêu tên `roles/` trong file chỉ dẫn không tự đăng ký subagent; mô tả “chỉ đọc” không tự giới hạn công cụ hay hệ thống file. Nếu host chưa hỗ trợ/không nạp projection, Main làm trực tiếp trong quyền hiện có hoặc báo vai chưa khả dụng, không giả là đã phân công.

**EXECUTION_PROFILE giữ lựa chọn hiệu lực của project**: host/app, role → model/tier/effort, fallback cho phép, scope/quyền, giới hạn và dấu vết xác nhận. Giá trị user chọn được ưu tiên hơn preset và giữ qua upgrade; preset mới không tự ghi đè lựa chọn đó. Không chứa key/token. Nhiệm vụ chuẩn chỉ đổi qua quản lý phiên bản bộ khung. Personal skill không tự mở quyền role.

R1 làm rõ “không gọi agent phụ khi chưa được yêu cầu”: operator có thể cấp quyền cho nhóm tác vụ; không xin lại từng lần trong quyền đã có. Trước R4, PROJECT giữ thỏa thuận; khi profile hoạt động, migrate quyền sang profile, PROJECT dẫn tới đó, tránh hai owner. Roadmap này không tự cấp quyền gọi subagent ở phiên hiện tại.

Preset theo nhiệm vụ dùng giá trị host đang chấp nhận. Không đổi model chính ngầm. Mặc định đề xuất LAW: tối đa hai vai phụ đồng thời, một cấp phân công; đây là lựa chọn sản phẩm cần pilot, không phải giới hạn provider. Việc nhỏ không bắt tạo TASK/gọi Reviewer riêng.

Giao việc cần mục tiêu, input/source revision, vùng ghi, output, tiêu chí đạt, quyền và work revision. Trả artifact/locator, bằng chứng, phần thiếu. Main kiểm binding trước tích hợp. Yêu cầu/nguồn đổi thì work revision đổi; kết quả cũ/trả muộn không ghi đè bản hiện hành. Dừng ghi “đã yêu cầu dừng” tới khi host xác nhận. Timeout phải reconcile trước retry để tránh lặp tác động/chi phí. Không đổi provider/auth hoặc cài tool ngầm.

### 6.1 Đánh giá lại kiểm soát Main — yêu cầu operator 17/10/2026

**Operator đã đồng ý hướng khuyến nghị và ưu tiên xử lý trước roadmap cũ; chi tiết triển khai theo chuỗi G ở 6.2.** Cho phép chọn lọc quy tắc/tool checker vào `.cvf/`. LAW chạy lâu dài trên máy từng user, Main tự gọi vai và tích hợp: “gọn” không được mặc nhiên dùng để bỏ điều kiện bảo toàn, quyền và kiểm soát Main. G-00 đã được review thiết kế, chưa có schema/checker hay proof host; hợp đồng/preset hiện có chưa chứng minh điều phối có cưỡng chế.

Đối chiếu Local và phản biện độc lập Sol 6.1 High xác định các khoảng trống:

| Khoảng trống kiến trúc | Hệ quả cần xử lý trước tuyên bố khả năng |
|---|---|
| Main diễn giải yêu cầu, chọn ngữ cảnh/Reviewer, kiểm binding rồi tích hợp | Review trước/sau vẫn có thể đúng với một brief lệch ý user hoặc bị Main bỏ qua |
| Chưa có binding độc lập giữa ý định user, grant, task/context revision và tác động | Main có thể dùng lại phê duyệt cho việc/nguồn/quyền đã đổi; hash không chứng minh quyền nếu Main sửa được cả giá trị kỳ vọng |
| Main có thể còn file tools, shell/Python, Office/native ghi trực tiếp | Writer/gate chỉ bảo vệ những thao tác đi qua nó; chưa chứng minh các đường bypass bị chặn |
| Fallback Main làm trực tiếp chưa phân biệt tác vụ cần review bắt buộc | Thiếu Reviewer không được suy thành quyền tự duyệt/tự làm thao tác đó |
| Chưa nghiệm thu việc Main vượt review/policy trên host thật | Projection/model đúng và checker xanh chưa chứng minh điều phối được kiểm soát |

**Khuyến nghị đang được đánh giá:** kế thừa đầy đủ các nguyên tắc kiểm soát cần thiết, triển khai tối thiểu theo tác động thực tế. User giữ quyền và mục tiêu; Main đề xuất/điều phối; Reviewer kiểm cả tính đủ của việc giao và kết quả khi rủi ro yêu cầu; điểm thực thi kiểm quyền/revision/phạm vi trước tác động. Không coi thêm một AI giám sát là điểm cưỡng chế độc lập.

Các quyết định thiết kế phải làm rõ cùng nhau:

- Quyền và override do ai cấp/giữ; ở cấu hình nào Main thực sự không thể tự sửa hoặc tự tạo phê duyệt. Nhãn vai, receipt tự ghi hoặc checksum không tự tạo quyền.
- Task/result phải truy được tới yêu cầu/điều kiện user đã chốt, nguồn/context revision, thao tác, vùng ghi, quyền và kết quả được review. Phân loại theo thao tác thực tế, không chỉ nhãn rủi ro Main tự đặt; review mất hiệu lực khi binding liên quan đổi.
- Việc nào cần kiểm trước giao/thực hiện/tích hợp; Worker được trả brief thiếu/mâu thuẫn; Main không được tự hạ acceptance hoặc bỏ verdict bắt buộc. Grant theo nhóm việc vẫn có thể dùng lâu dài trong giới hạn user đã cấp.
- Điều kiện chặn nằm ở host/tool/OS nào và có thể bị vượt bằng công cụ nào. Nếu Main có toàn quyền filesystem/shell và sửa được mọi policy/checker, không thể hứa cưỡng chế chỉ bằng file hướng dẫn hoặc một CLI tùy chọn.
- Support matrix tách hướng dẫn/kiểm tra sau thao tác với kiểm soát tác động đã chứng minh. Host chưa kiểm ghi unknown; host không đáp ứng điều kiện không được âm thầm nhận cùng mức bảo đảm. Mọi cơ chế bổ sung phải đánh giá chi phí và khả năng phân phối local, không mặc nhiên thêm daemon/cloud/runtime riêng.
- Kết quả/terminal status phải dựa vào artifact và bằng chứng đúng revision, giữ dấu vết bị chặn; lỗi lặp được xử lý ở điểm sớm có thể ngăn, không chỉ thêm lời nhắc hoặc tăng effort model.

**Ảnh hưởng kế hoạch:** thiết kế A-08/A-09/A-11 và B-03 cần được đối chiếu lại cùng mục này trước khi chốt triển khai native A-10. Đặc tả quyền/task/review không đợi tới sau khi adapter gọi vai chạy được; proof host thuộc bước triển khai/pilot sau, không là điều kiện để viết thiết kế. R2/A-06 tiếp tục giữ các blocker dữ liệu riêng; đánh giá này không đóng hoặc xóa bằng chứng các tranche đã làm. Chưa thay grant, hợp đồng roles, code writer hoặc tuyên bố host có cưỡng chế.

Các ca cần đưa vào nghiệm thu thiết kế/host: Main gắn nhãn đọc nhưng ghi nguồn; bỏ/sửa verdict Reviewer; dùng approval của revision cũ; nguồn/personal skill tự cấp quyền; ghi vòng qua writer bằng file/shell/native; kết quả trả muộn/retry; luồng tạo bản nháp trong grant vẫn gọn. Không biến đánh giá này thành yêu cầu mọi tác vụ phải gọi đủ ba vai.

### 6.2 Chuỗi G — thực hiện trước khi tiếp tục roadmap cũ

#### Tiến độ hiện hành — cập nhật 18/10/2026

Dấu `[x]` chỉ xác nhận đúng mốc được ghi, trong phạm vi/giới hạn đã review; không đồng nghĩa toàn bộ `.cvf` đã active hoặc hoàn tất. Cập nhật checklist này sau mỗi mốc thi công/review, giữ bảng bên dưới làm chi tiết và lịch sử.

- [x] G-00: nhận thiết kế `.cvf`.
- [x] G-01: nhận schema và routing roles trong phạm vi contract.
- [x] G-02: nhận checker local schema/routing/record consistency; không host enforcement.
- [x] C2: nhận S1 foundation, S2 helper và A0 contract v3 candidate.
- [x] C2: nhận S3-B foundation, C/D binding/routing và screening theo phạm vi từng tranche.
- [x] P-CN1 + S4-min: nhận workflow một file, cùng task qua dispatch/effect/publish/accept; Windows NTFS local, COOPERATIVE/ADVISORY.
- [x] I-01: chốt thiết kế tích hợp có điều kiện — context → nháp hiện tại → package v3.
- [x] I1/P-CTX1: Worker đã thi công; Reviewer sửa lỗi scan journal và Root sửa định dạng STATE mẫu.
- [x] I1/P-CTX1: **REVIEW_ACCEPTED_P_CTX1_WITH_LIMITS** — nhận owner operational context của 5.4.1; chưa nghiệm thu tích hợp UI/package.
- [x] I2: **REVIEW_ACCEPTED_I2_NAVIGATION_WITH_LIMITS** — nhận card Nháp hiện tại/history, selection/navigation theo owner-UI5.4.2; Reviewer53test/0skip, Root browser5/0skip. Office/agent pilot và release còn mở.
- [x] I3: **REVIEW_ACCEPTED_I3_PACKAGE_LIFECYCLE_WITH_LIMITS** — nhận package14file v3/new-adopt-upgrade/readiness trong scope5.4.3; đã sửa guard/source/EOL. Reviewer8guard+9RCtarget0skip; Root packagecheck0lỗi/1cảnhbáo và2MainFlows0skip. Full gate cuối đã đạt971test/3skip; native owner/TXT pilot đã nhận WITH_LIMITS. Office/native checker end-to-end/support acceptance và release còn mở; xem bằng chứng hiện hành bên dưới.
- [x] G-03: **NARROW_COOPERATIVE_BASELINE_ACCEPTED_WITH_LIMITS** — pilot một file trên Windows NTFS local, có D4 dương đúng bản; không ghi enforcement cũ PASS.
- [x] G-04/tích hợp candidate: **CANDIDATE_INTEGRATION_ACCEPTED_WITH_LIMITS** — I1–I3, RC3, native checker, Office tối thiểu và support candidate đã nhận. Theo I-02 rev1 được tiếp A–D theo dependency.
- [ ] G-04/phát hành chính thức: **PENDING** theo RELEASING và D-02; Git sạch/CI/quy trình RC chưa hoàn tất, chưa release/activation.

#### Bằng chứng G-03/G-04 hiện hành — 18/10/2026

**Lịch sử RC2:** bị gate chặn971test/1failure/3skip, khôngZIP. Reviewer xác định test stale-button thiếu chờ card matched và dùng sleep500ms; đã sửa test-only chờ precondition/event/response, giữ nguyên1dialog và dismiss khôngopen. RC3 sau sửa đã qua gate ở bảng dưới; runtime/protocol không đổi. Native checker và Wordopen/render chỉ nhận scope có giới hạn, chưa D4/edit-save.

Reviewer Sol6.1 High đã nhận Office tối thiểu, RC3/native checker và **REVIEW_ACCEPTED_D4_LAB_ONE_FILE_WITH_LIMITS**. Orchestrator nhận G-03 baseline hợp tác hẹp và G-04 tích hợp candidate WITH_LIMITS; phần phát hành chính thức vẫn PENDING. Các mốc BLOCKED lịch sử giữ nguyên.

- [x] Full gate RC3 sau sửa prose contract: 971 test/3 skip trong 468.353s;4gate passed, không skip/nested override. Runtimecode/pins giữ nguyên; RC1 là lịch sử. Tên/reason skip có trong gate JSON/HANDOFF.
- [x] RC3 có255file, closure `.cvf`14file,254entry MANIFEST khớp theo owner chuẩn hóa EOL. ZIPsha `cd4eec66dad7eedda5e3a0dbd4ca33b45acd57b592480cc3a9542c1db4858dc2`. SoRC1 chỉ contract prose và MANIFEST dẫn xuất đổi; không đổi semantics hoặc runtimebyte.
- [x] Native Orchestrator pilot lab TXT từ RC (không import test fixtures): nguồn giả→2PUBLISHED→preview/apply/select1→2→1;15steps exit0, nguồn/nháp giữ bytes, không operations log. Nội dung được Reviewer đối chiếu. Không checker dispatch/effect/accept hoặc D4/user acceptance trong pilot này.
- [x] Opener thật gửi lệnh, Orchestrator quan sát đúng TXT trong Notepad thật; không coi việc dispatch thành công là Office render/save. Đã đóng riêng tab lab đã lưu, không sửa tab khác.
- [x] Đo mẫu202revision (200mẫu bổ sung bằng writer thật): publish200mẫu2.805s; fresh-process status4.9152–6.031s/list5.2164–5.2603s, mỗi loại3lần. Đây là dữ liệu giả trên một máy, không200quyết định agent hoặc SLA; chưa tự mở index/registry hay đặt ngưỡng đạt.
- [x] Office mở/render: DOCX6paragraph hợp lệ schema đã được publish/select/open thật và Orchestrator thấy trong Word1trang đủ tiếng Việt. Staged/source/artifact/receipt giữ bytes, sau mở status matched. Reviewer kiểm file/CLI, UI chỉ là quan sát Orchestrator.
- [x] Office COM edit/save/readback — REVIEW_ACCEPTED_WITH_LIMITS: output7đoạn đúng6gốc+1mới, SaveAs/đóng/mở lại đọc đúng theo2Wordlogs; staged/source/target/receipt cũ giữ. Rootschema validation đạt/bytes giữ.5đoạn gốc12pt/tiêuđề18pt; đoạnmới11pt chấp nhận theo brief nội dung. ChưaUI/render outputmới, script/command/model/effort/instance-teardown audit;2PIDvắng khiRootkiểm không proof thờiđiểmthoát. Không yêu cầu publish thêm để nhận riêng scope này.
- [x] Native checker d/e/publish/a:2cycle,12CLIsteps (10checker+2publisher), cùng task/snapshot/digests trong mỗi cycle; d/ePASS→PUBLISHED→acceptBLOCKED đúng vì thiếuD4.7gate kỹ thuậtMET, REQUIREMENTS NOT_CHECKED/EVIDENCE_NOT_VERIFIED.4negative đềuBLOCKED. Hai bản biên tập là hai task riêng/task_revision1, không nâng revision hoặc giả D4.
- [x] M-3/D4 dương đúng bản: user trả lời “Duyệt bản lab 6ee4cef2” sau khi được trình nội dung và đủ2requirement. Task/result/rid3bf643838fb844ed98080d7e1545279b, rev1; artifact EXACT sha6ee4cef25694c7732f8ceb00379dc8c8359ace021c6f277c0363fddaad61d16d. CLI accept exit0/PASS/ADVISORY:7gateMET + USER_ACCEPTED_DECLARED; Reviewer nhận có giới hạn. Không effect authorization/semantic verification hoặc duyệt phát hành LAW.

#### Điểm dừng candidate, D4 và phát hành — scope audit18/10/2026

Reviewer Sol6.1 High đối chiếu các quyết định đã chốt; không sửa acceptance hoặc tạo gate mới:

| Nhóm | Disposition hiện hành | Việc còn lại đúng phạm vi |
|---|---|---|
| Candidate kỹ thuật | Đã nhận WITH_LIMITS: I1–I3, RC3 gate/archive, native checker và Office tối thiểu | Giữ claim theo entrypoint/WindowsNTFS/Python3.11 đã đo; không chạy thêm mọi host/Office/CI để đổi candidate thành “đã kiểm hết” |
| Đóng nhánh nghiệm thu M-3 | **REVIEW_ACCEPTED_D4_LAB_ONE_FILE_WITH_LIMITS**; đủ binding và lời user duyệt bản lab6ee4cef2 | Không hỏi lại; không áp D4 này cho edited-word.docx, task khác hoặc phát hành LAW. Giữ bản âm BLOCKED trước đó làm lịch sử |
| Support candidate | Chốt phạm vi đã đo ở bảng dưới; M-1 chỉWindowsNTFSlocal, R7 không bắt mọihost cùngđạt | Chưa actual3.8/OS/hostkhác không đồngnghĩa phải thử thêm trước candidate.3.13thiếujsonschema chỉđo nhánhUNAVAILABLE, khôngclaimluồng dương |
| Phát hành/hỗ trợ chính thức | Chưa hoàn tất RELEASING§1/§3: CI xanh trên commit và git.dirty=false | RC3dirty là labcandidate/gate kỹ thuật, chưa hoàn tất quy trìnhRCphát hành. Không stage/commit/push/activation khiuser chưa giao; --no-branding là lựa chọn generic hợp lệ |

Căn cứ: packetM-1/M-3/I-01/I-02, scope operator nhận18/10, roadmapR7 và `.github/RELEASING.md`. Lab/native-workflow giữ actual question/answer, bundle D4 và report accept; đây là evidence hợp tác do Orchestrator ghi, không host attestation chống giả. Unknown của host/version khác không tự thành gate candidate mới. X14 vẫn PARKED; official release vẫn chờ.

**I-02 rev1 — amendment thứ tự phát triển, 18/10/2026; DESIGN_ACCEPTED_WITH_CONSTRAINTS bởi Reviewer độc lập Sol6.1 High.** Sau khi G-03 baseline hợp tác hẹp và G-04 tích hợp candidate được nhận WITH_LIMITS, có thể tiếp tục công việc kho nguồn theo dependency và acceptance của từng tranche A–D. G-04/official-release vẫn PENDING theo RELEASING và D-02. Mốc này không activation, không công bố hỗ trợ chính thức, không đóng enforcement cũ hoặc các blocker dữ liệu/writer.

Lý do: A-06 còn điều kiện trước release; D-02 sở hữu release và phụ thuộc C-02/D-01. Bắt official release hoàn tất trước mọi A–D tạo vòng phụ thuộc. Amendment chỉ sửa thứ tự; không đổi schema/policy/routing/D4/UNSUPPORTED hoặc verdict chặn. A-07 vẫn phụ thuộc A-06; không tự đóng toàn R2 hoặc mở lại x14. Quyền stage/commit/push/release không được cấp thêm; không refresh RC3 từ maintainer docs. **Mốc tiếp nối 19/10:** A-02/A-06/A-07/A-08/A-09 và bước Scout của A-10 đã nhận WITH_LIMITS đúng phạm vi; Scout có proof file-native CLI2.1.81, chưa toàn R4/activation/release.

| Phạm vi | Bằng chứng hiện có | Giới hạn còn giữ |
|---|---|---|
| Windows build26200, NTFS local, Python3.11.9/jsonschema4.23.0/openpyxl3.1.5 | Full gate RC và owner/TXT pilot đã chạy | COOPERATIVE/ADVISORY; không authority chống giả mạo |
| Python3.13 không jsonschema | I3 đo thực: UNAVAILABLE/DEPENDENCY_MISSING, không cài gì | Chưa chạy controlled workflow có đủ dependency |
| Python3.8 | Gate heuristic đạt | Chưa chạy interpreter3.8 thật |
| File symlink | Hai ca skip vì thiếu quyền Windows1314 | Junction/mock classifier không thay file symlink thật |
| Non-Windows/network/cloud | Controlled profile không nhận | Không suy các chức năng LAW khác bị cấm hoặc đã kiểm |
| Word/Excel16.0.20326.20232 | Bản gốc DOCX đã mở/render thật; COM output mới7đoạn đã có SaveAs/đọc lại theo logs, schema/hash đạt | ChưaUI/render outputmới, command/instance/teardown audit hoặc Excel I/O; không Wordread-only claim toàn luồng |
| Git/đóng gói bytes | Clean-filter4file, raw owner pins/ZIP đã kiểm; RC3 chỉ đổi status prose + MANIFEST soRC1 | Chưa stage/commit/fresh checkout/CI; code/pin không đổi; MANIFEST text chuẩn hóa EOL |
| Branding/reproducible build | RC lần này --no-branding | Chưa nhận branded RC hoặc reproducibility của finalRC |

Evidence ở lab tạm `law-g04-final-rh_52jn1` (đường đầy đủ/hashes trong HANDOFF): RC3 ZIP+.gate.json/log, native-workflow/*, office-pilot/* và performance.json. Inventory hiện205prepared/published sau2checker-cycle+1Officepublish; sampleperformance giữ202. Pilot thực chạy runtimeRC1; so deliveryprojection chứng minh RC3 chỉ khác contract prose/MANIFEST dẫn xuất nên reuse runtime evidence có giới hạn. UI/timings là quan sát Orchestrator; readonly là assertion snapshot của runner, Reviewer không chứng kiến. Không chuyển lab evidence thành grant/activation.

**Ngoài chuỗi đang làm:** x14 vẫn PARKED; không tự mở lại hoặc tính safe refusal là bảo toàn x14 hoàn chỉnh. Chưa quy đổi checklist thành phần trăm vì các mốc có khối lượng khác nhau.

**Quyết định môi trường cho I3/G-04 (18/10):** luồng Nháp hiện tại có kiểm soát hiện cần Windows + NTFS local + `jsonschema >= 4.18` có Draft 2020-12. Đây là requirement của chức năng này, không đổi toàn LAW thành ứng dụng chỉ chạy trên môi trường đó. Thiếu điều kiện thì card UNAVAILABLE và không mở/chọn qua luồng này; không bỏ so pin hoặc fallback opener để làm xanh. I3 phải kiểm readiness bằng đúng interpreter launcher/App thực sự dùng, ghi support matrix và hướng dẫn xử lý theo môi trường project, không tự cài dependency/global/admin. Test trên Python khác không chứng minh launcher sẵn sàng. Kiểm riêng trường hợp thiếu/sai version thư viện; không nhận suite phần lớn bị skip là proof workflow.

**Lịch sử nợ đỏ I2 và proof tích hợp:** Worker I2 báo đã tái hiện hai MainFlows template-home bằng App/UI HEAD trong bản sao; structured_tools2ca/workflows1ca là nợ packager; panel3.13 thiếu openpyxl là khác môi trường. Giữ provenance Worker, chưa coi là Root tự xác nhận toàn bộ. Các lỗi package/template và readiness môi trường vẫn thuộc I3/G-04 trước phát hành. Browser với opener giả không thay ca mở Office thật; prompt copy không thay pilot agent tạo revision rồi select. Tại mốc I2, process pilot/Office/performance nhiều revision và release gate chưa được nhận; trạng thái hiện hành nằm ở bảng bằng chứng phía trên, không suy giới hạn I2 là G-04 PASS.
 Bổ sung review I3: Worker fullgate trước review báo hết lỗi package/template; Root chạy lại hai MainFlows trên bytes sau sửa đạt. Sau đó full gate cuối đạt971test/3skip và native owner/TXT pilot/performance202revision đã được nhận WITH_LIMITS; Office I/O và native checker/D4/support acceptance vẫn mở.

**Quyết định operator 17/10/2026:** làm việc trực tiếp trong LAW, đối chiếu CVF khi cần; kế thừa các cơ chế phù hợp và dùng `.cvf/` cho phần tự đủ. Đây là quyền thiết kế/triển khai có review theo phạm vi, không tự cấp quyền điều phối cho project người dùng, không đổi account/model hoặc bật runtime riêng.

| Tranche / trạng thái | Owner và việc cần làm | Điều kiện bàn giao / phụ thuộc |
|---|---|---|
| **G-00 — thiết kế và cây / review thiết kế đạt 17/10** | .cvf README/rules/contracts/checks spec/provenance; roadmap/tree/continuity. Main làm mẫu, Reviewer Sol 6.1 High | Hai finding P2 routing bắt buộc và trusted intent/reviewer binding đã resolved trong thiết kế. Có owner/refusal/giới hạn và ca bypass/luồng hợp lệ; chỉ đủ bắt đầu G-01, không tuyên checker/host đã chạy |
| **G-01 — schema và routing roles / review đạt 17/10** | Schema/ví dụ hợp đồng trong .cvf/contracts; AGENTS VI/EN, roles agent/checks, A-09/A-11 cùng một owner contract; EXECUTION_PROFILE vẫn là owner lựa chọn project | Ba P2 đã resolved; 19/19 ví dụ cấu trúc khớp, thiếu field scope vẫn invalid; verdict/hash ở HANDOFF. Chưa đăng ký native hoặc có checker/host enforcement |
| **G-02 — checker local / review nhận bản cuối 17/10** | .cvf/checks checker/focused tests, docs/evidence; không schema/policy/registry/writer/runtime mới | Reviewer Sol6.1 High nhận codef95bfc367bb7f470; ba nhóm P2/output anchor resolved. Main107 test G-02 đạt/0 skip; chỉ schema/routing/record consistency, effect_authorized=false. Không host enforcement |
| **G-03 — NARROW_COOPERATIVE_BASELINE_ACCEPTED_WITH_LIMITS,18/10** | Native2cycle và4negative giữ verdict thật; nhánh D4 dương có user duyệt đúng bản và accept PASS/ADVISORY. Office tối thiểu đã nhận | Chỉ một file/WindowsNTFSlocal/COOPERATIVE; không host enforcement, không semantic/actual-operation verification. D4 không phủ output Word mới hoặc task khác |
| **G-04 — CANDIDATE_INTEGRATION_ACCEPTED_WITH_LIMITS; official-release PENDING** | I1–I3, RC3 gate971test/3skip,255file/14closure/254manifest; native checker/Office/D4 tối thiểu được nhận | I-02 cho tiếp phát triển A–D theo dependency. Giữ Gitclean/CI/RELEASING/D-02 và blocker A-06; chưa release/activation. Không lặp Office/suite hoặc dispatch lại I1–I3 |

**Chi tiết2b đã review để khảo sát, chưa cho cài:** xem design2b mục10 và brief HANDOFF.

**Operator nhận phạm vi mặc định18/10:** trả lời “Chấp thuận phạm vi đề xuất (khuyến nghị)” sau preflight Reviewer.
[Quyết định](DE_XUAT_PHAM_VI_KIEM_SOAT_LAW_2026-10-18.md) đổi acceptance/trust assumptions ở mức phạm vi;
rules/schema/checker v1 chưa đổi. Không tự ghi G-03 cũ PASS, làm NoVerifier VERIFIED, auto-migrate hoặc mở effect.

| Tranche amendment đang mở | Owner / đầu ra | Điều kiện bàn giao |
|---|---|---|
| **G-01-C1 — CONTRACT_CANDIDATE_REVIEW_ACCEPTED, 18/10** | `.cvf/contracts/v2/` + `.cvf/rules/v2/`, ví dụ giả/EXPECTED/schema/vectors. Worker Sonnet5.5 (effort chưa quan sát) báo24 test đạt; Reviewer Sol6.1 High nhận sau sửa hẹp Main;13 test mục tiêu đạt, evidence g01-c1-review-2026-10-18 |9row IDs/phases/trigger/hợp hàng giữ; làm rõ guard ngoài hash và điều kiện UNSUPPORTED.20 vector canonical, v1/checker nguyên, grant ví dụ không hoạt động; nhận candidate không là activation hoặc workflow PASS |
| **G-02-C2/S1 foundation và S2 helper — REVIEW_ACCEPTED,18/10** | S1 Worker58snapshot/Main31target; S2 Worker157snapshot, Reviewer Sol6.1 High nhận sau2P2+1P3Mainfix (claims/index, metadataAPI, null), Main56target đạt; evidence s2/main-review. Refs/binding helperthuần đã có, loaderrefactor giữ S1public | S2 chưa nối entry/output/gate; C1/v1 giữ, kernel không authority/observer. V2 CANDIDATE_NOT_ACTIVE/validstructure BLOCKED; amendment S3-D0 và P-CN1 theo hàng dưới, chưa evaluator/activation; không fakeVerifier/receipt reinterpret/migration/profile/templates/host |
| **G-02-C2/P-CN1-I + S4-min — REVIEW_ACCEPTED_TOOLS_ONLY_WITH_LIMITS,18/10** | Contract C 4.3.3 trong [packet](G02_C2_S3_D0_AMENDMENT_PACKET_2026-10-18.md) nhận with constraints; corrective root/T1/T2/runtime/T7 qua Reviewer Sol6.1 High. Reviewer tự sửa platform/pending cleanup, hai lượt21/14 target đạt0skip; Orchestrator11target đạt. Owner hash f2b1b425690eacd5; thiếu pin từ chối, private Pins dependency/recheck_only recovery là giới hạn | Chỉ nhận tools-only, chưa supported/R-7 end-to-end resolved; bước tiếp theo theo hàng A0/B0 dưới đây. Không quay sang A–D/x14 hoặc mở kiến trúc rộng |
| **G-02-C2/A0 hẹp — CONTRACT_CANDIDATE_REVIEW_ACCEPTED; S3-B0 đã chốt** | Cây contract/schema/policy/examples/vectors v3 candidate nhận sau sửa nhỏ optional result.action_digest và bổ sung check/3/historical pin. Reviewer29target/Main12target đạt0skip; v1/v2/writer nguyên byte; workflow NOT_RUN. S3-B0 chọn copy-forward foundation v3 có giới hạn, không kernel/engine mới | Foundation đã review ở hàng dưới; Orchestrator/S3-G/G-04 giữ owner nợ trùng mã, kiểm package một runtime trước release, chưa xóa v2 hoặc đóng G |
| **G-02-C2/S3-B — REVIEW_ACCEPTED_FOUNDATION_ONLY** | Entry ff93aace52cc77e7/tests8f959d2fe8381f84; Reviewer46/Main21target đạt0skip, output/CLI/helpers/pins đúng scope. STRUCTURE_ONLY/null, route chưa tính và aggregate0 là placeholder | Foundation xong; C/D đã review theo hàng dưới. Chưa gate/workflow/activation/R-7/G PASS |
| **G-02-C2/C-D — REVIEW_ACCEPTED_BINDING_ROUTING_ONLY** | Routing c8b972e6a18440b6; sửa U thay F, hợp nghĩa vụ T/U, lexical và known-loss taskwide. Review/evidence tại HANDOFF | Screening đã nhận ở hàng dưới; chưa gate/observer/receipt/D4/PASS. X14 PARKED, không activation/R-7 resolved |
| **G-02-C2/P-CN1 workflow — REVIEW_ACCEPTED_P_CN1_ONE_FILE_WITH_LIMITS** | Cùng task/snapshot/digests qua d/e/publish/a trên Windows NTFS local; caller rid + roundtrip, T2 không tạo bootstrap parents. Reviewer16/14, Root18 trước docstring và20 sau pin đạt0skip; writer8a4e5914d0892ea1, policy255d76c66021c4f1. Check_package nguồn0 lỗi/1 cảnh báo | I-01/packet5.4.A DESIGN_ACCEPTED_WITH_CONDITIONS qua Reviewer Sol6.1 High; I1/P-CTX1 REVIEW_ACCEPTED_P_CTX1_WITH_LIMITS: nhận owner5.4.1, strict scan journal fail-closed, template STATE đã sửa; Root46test OK/1skip và15target OK/0skip, Reviewer6strict/default/prune và7pin/schema target đạt0skip (không cộng lượt trùng). Owner ee7cb6b15f3b5e70, policy af141b37c242119c; P-CN1 giữ nguyên. I2 REVIEW_ACCEPTED_I2_NAVIGATION_WITH_LIMITS (owner-UI5.4.2); I3 đã REVIEW_ACCEPTED_I3_PACKAGE_LIFECYCLE_WITH_LIMITS; G-03 baseline hợp tác hẹp/G-04 candidate đã nhận WITH_LIMITS, D4 dương nhận đúng bản; official release PENDING, v3 chưa activation. Bootstrap/new/adopt/upgrade, native checker và Office tối thiểu đã kiểm theo bảng hiện hành. I-02 cho tiếp A–D theo dependency; x14 PARKED, không ship cả3runtime |
| **G-02-C2/screening — REVIEW_ACCEPTED_BINDING_ROUTING_ONLY** | Canon305fe127a290b40c/entry7d67c3b8c76d9415 là mốc screening; Reviewer sửa task đơn/orphan duplicate, không coverage giả. Reviewer22/Main17 sau sửa đạt0skip | Phần screening đã nhận; workflow tiếp theo đã review nhận WITH_LIMITS ở hàng trên. Chưa activation/R-7/G PASS; không dispatch lại brief screening |

**Bảng2b dưới đây là kế hoạch enforcement đã khảo sát, không là lệnh triển khai hiện hành.**
Hướng hardening này chưa được operator chọn; các findings/stopgates giữ làm bằng chứng.

| Lát | Đầu ra / điều kiện mở |
|---|---|
| **2b-00 — khảo sát đã nhận WITH_LIMITS** | Packet và review đã có; ứng viên U-std CHANGES_REQUIRED. Kết thúc lượt khảo sát, không tự giao vòng tìm/sửa tiếp hoặc đưa4ngoại lệ cài cho operator. Quyết định phạm vi/chi phí sản phẩm trước bước kế |
| **2b-01 — chờ2b-00 và quyết định hạ tầng** | Amendment có version cho digest/authority/verifier theo owner G-01/G-02; không tự dùng record giả làm receipt |
| **2b-02 — chờ contract/hạ tầng** | Launcher/capability adapter hẹp nếu được chọn; reuse writer hiện có; giữ stopgate x14/race |
| **2b-03 — chờ grant môi trường thử** | Setup/rollback/proof Main và child, các đường bypass và ảnh hưởng ngoài LAW; không dùng workspace thật làm thử |
| **2b-04 — chờ proof G-03** | UX/ready-to-distribute nối owner G-04; user không tự viết metadata kiểm soát |

**Trạng thái năng lực:** .cvf README định nghĩa UNVERIFIED/ADVISORY/ENFORCED_FOR_NAMED_ACTIONS, không là nhãn chứng nhận hiện tại. Mọi host hiện chưa có proof enforcement LAW; role config vẫn PENDING_R4. Không nhân API runtime chỉ để gọi vai hoặc biến folder .cvf thành lời hứa kiểm soát mọi công cụ của host.

**Nợ ex19/context-only:** G-01 cho phép delegation descriptor có tools/operations/paths rỗng nhưng task.effects.actions vẫn minItems1; chưa có biểu diễn task chỉ xử lý context. G-02 giữ NOT_CHECKED/BLOCKED khi thiếu binding, không tạo action/quyền giả. Owner nợ là contract/schema G-01: cần thiết kế và review riêng trước claim hỗ trợ context-only ở G-03/G-04, không sửa schema lén trong corrective checker. Scope rỗng không miễn task/context binding; việc từ chối trung thực không chứng minh tính năng đã hỗ trợ.

**Chốt trước code G-02, 17/10/2026:** Main nhận thiết kế kèm sửa bắt buộc sau Reviewer Sol 6.1 High kiểm. Reason riêng checker, chỉ so digest giữa record, không băm artifact hoặc phát minh canonicalization; không thêm protected-path defaults vào G-01 ở lượt này. Self-claim không chứng minh không có protected target hoặc evidence thật; gate theo phase, child permission không suy từ path có trong context; CLI chuẩn không arbitrary schema/policy override. CI được mở scope dependency/test hẹp, thiếu validator không silent skip. Exit 0/1/2/3 theo checks README; không coi NOT_APPLICABLE là approval. G-03 phải chốt nguồn phân loại path tin cậy, quy tắc tạo/xác minh digest và quan sát thực trước integration; G-02 chỉ consistency/ADVISORY, không tự thành permit. Chi tiết quyết định có thẩm quyền tại HANDOFF Bước tiếp theo; chưa code/checker proof.

**Nguồn quyền và dữ liệu:** .cvf chứa phần bộ khung; .agent/EXECUTION_PROFILE.json chứa lựa chọn/quyền project theo A-09; working/<work-id>/ chứa task/result khi cần; .agent/runtime/governance chứa log/receipt/cache sinh ra. G-04 phải kiểm loại runtime/user state khỏi ZIP/manifest. Việc đặt file ở .cvf hay .agent không tự bảo vệ chúng khỏi Main.

**Cách triển khai:** hàng G và brief HANDOFF là phiếu việc; độc lập review thiết kế trước code, kiểm đúng phần đổi, không lặp full suite vô cớ. Schema/checker thực thi chưa có ở G-00. Trước code checker chọn rõ phản chứng và điều phải bảo toàn; trước host proof chốt host/version/tool surface/grant quan sát được. Bằng chứng có trước còn hợp lệ được dùng lại; metadata shell/host config không thay proof hành vi.

**Review G-00:** `review_a05_sol_high`, cấu hình dispatch `gpt-6.1-sol`/`high`, nhận thiết kế sau một vòng sửa hai P2: bảng tác động→review/gate và owner được đổi rule; intent/accepted-task/reviewer eligibility phải có nguồn tin cậy ngoài quyền Main tự tạo/thay thế. Chỉ review văn bản và delta, không chạy code/tests/host. Không gán model/effort Main từ preset hồi tố. G-01 tiếp nhận đúng contract đã review, không tự hạ các điều kiện để schema dễ đạt.

**G-01 Worker 17/10/2026:** `control.schema.json` (Draft 2020-12, `law.cvf.control/1`) một SOT cho task/grant/review/effect/result/bundle/routing_policy; `ROUTING_POLICY.json` (`law.cvf.routing/1`) canonical cho 9 mã hàng, CONTROL_RULES là bản đọc cùng mã; 13 ví dụ EXAMPLE và EXPECTED.json; AGENTS VI/EN và roles dẫn tới .cvf. Đã kiểm cấu trúc bằng jsonschema 4.23.0 có sẵn (13/13 khớp kỳ vọng hợp lệ/không hợp lệ, 16 probe biến đổi bị từ chối); disposition/authority chỉ là kỳ vọng cho G-02, chưa chạy. Chờ Reviewer Sol 6.1 High; chưa đóng G-01.

**Review delta G-01, 17/10/2026:** Reviewer Sol 6.1 High xác nhận hai P2 recipe/delegation đã resolved. Còn CHANGES_REQUIRED: delegation.tool_scope cấm ba mảng rỗng, không biểu diễn được vai chỉ xử lý context và không có quyền tool/file. Sửa hẹp empty=none, giữ field bắt buộc và deny vượt scope; brief hiện hành ở HANDOFF. Worker evidence 18/18 ví dụ, 31 probe âm/3 dương được dùng lại; Reviewer kiểm 2 probe đối chứng, không chạy lại suite. Chưa matcher/disposition/host proof; G-02 tiếp tục chờ.

**G-01 kết thúc review, 17/10/2026:** Main sửa P2 scope rỗng theo lệnh operator, Reviewer Sol 6.1 High xác nhận resolved, không finding mới trong delta. Schema/policy hợp lệ, 19/19 ví dụ khớp, ba ca thiếu field invalid; Reviewer dùng lại evidence và kiểm delta/hash. G-01 nhận ở phạm vi schema/routing, G-02 là tranche tiếp theo với thiết kế trước code; chưa checker/authority/host enforcement/UX proof. Các đoạn review trước giữ lịch sử, không là trạng thái hiện hành.

**Ưu tiên hiện hành — I-02 rev1:** D-01a/P1 đã nhận ACCEPTED_WITH_LIMITS20/10, Reviewer15target đạt/0skip, code/test trước–sau bóc delta khớp baseline. Diagnostic identity không đổi parser/plan/guard/writer; legacy manifest debt giữ. D-01b20/10 ACCEPTED_WITH_LIMITS subset tám guide/preview/archive/thay current, giữ .new/phục hồi thủ công; Reviewer49target đạt/0skip sau3sửa nhỏ. D-01c20/10 ACCEPTED_WITH_LIMITS: archive→Windows no-replace rename/observe, cùng8guide; Reviewer85đạt trước correction/16target sau,0skip, có Chromium finish. D-01d20/10 ACCEPTED_WITH_LIMITS: projected-v3/VI-EN/workbook thật/nâng-hạ cùngschema/archive; Reviewer sửa test oracle,6test source cuối đạt/0skip, runtime giữ. D-01e20/10 ACCEPTED_WITH_LIMITS finish-only6entrypoint/current giữ, FINISH14/REPLACE8; Reviewer55scope đạt/0skip+5HTTP/1amendment, harness10053 sửa và12/12đạt. Chưa toànP4/D-01/T39/release. C-02 PREP giữ WITH_LIMITS/PILOT_NOT_RUN; x14 SAFE_REFUSAL_ONLY/PARKED.

**Yêu cầu người dùng phổ thông, operator làm rõ 17/10:** bộ khung chuẩn bị sẵn default/routing/role preset và điều kiện kiểm soát; không giao cho user viết schema/JSON, chọn trust_anchor, gắn VERIFIED, phân loại risk kỹ thuật hoặc tự sửa brief để qua gate. User quyết định mục tiêu, nguồn, phạm vi được sửa và nơi nhận kết quả bằng ngôn ngữ công việc; Main chuyển thành proposal, điểm thực thi xác minh quyền qua nguồn phù hợp, không tự điền thành quyền đã cấp. Grant nhóm còn hiệu lực dùng lại, chỉ hỏi quyết định ngoài quyền và nêu hậu quả cụ thể. G-01 là contract nội bộ, chưa phải UX đã nghiệm thu. G-03 phải xác định nguồn thao tác user/issuer quan sát được; G-04 cần setup mặc định an toàn, thông báo chặn dễ hiểu và luồng nháp hợp lệ không buộc hiểu thuật ngữ; C-02 vẫn là pilot người mới độc lập. Giữ dữ liệu và giới hạn thao tác khi thiếu bảo vệ; cảnh báo hoặc hướng dẫn user tự chọn trường kỹ thuật không thay quyền/bảo toàn.

**Review G-01 17/10/2026:** Reviewer độc lập `review_a05_sol_high`, cấu hình dispatch `gpt-6.1-sol`/`high`, yêu cầu sửa 2 P2 trước G-02: match_clause mô tả OR cho conditions nhưng recipe cần AND; grant/effect thiếu allowed callee và child context/scope/envelope để kiểm delegation. Bốn schema probe bằng jsonschema xác nhận representation hiện có, không phải runtime exploit. Reviewer đã sửa nhỏ AGENTS VI/EN và Scout wording để internal owners vẫn có nghĩa, tên vai không tự giảm route. Các split 7→9 hàng và lane read/draft hợp tác chấp nhận trong giới hạn; trust_anchor chỉ là lời khai, schema valid chưa là authority. Worker 13/16 checks vẫn là evidence Worker báo; mẫu này tự báo Opus 5.5, effort unknown, không gán Sonnet. G-01 CHANGES_REQUIRED, G-02–G-04 còn chờ; user không phải tự viết JSON/grant để vá các thiếu sót hợp đồng này.

**Sửa sau review G-01, cùng ngày:** match_clause dùng `conditions_all`/`conditions_any` tường minh, OR giữa mệnh đề, AND giữa trường; recipe đã nhận nhưng đổi quyết định user vào R-MUTATION, không rõ thì R-UNCLASSIFIED; điều kiện không xác định và hiệu ứng không khớp hàng nào về R-UNCLASSIFIED. Delegation có `callee_role` riêng (core/registered/domain_accepted), task cha/con, phạm vi tool và envelope yêu cầu; grant tách `delegate_callees` khỏi subject. Gửi ra ngoài cần payload; mọi thao tác trừ delegate cần đích. Giữ version 1 vì chưa được nhận. Validator jsonschema có sẵn: 18/18 ví dụ khớp, 31 probe âm bị từ chối, 3 probe dương hợp lệ; disposition vẫn là kỳ vọng cho G-02. Reviewer đã nhận hai sửa cũ, còn P2 scope rỗng nêu trên.

## 7. Host và thông tin cập nhật

Đã mở tài liệu chính thức **17/10/2026**, trong phạm vi:

| Tài liệu | Khả năng liên quan | Giới hạn |
|---|---|---|
| [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Agent TOML ở `.codex/agents/`, `model`, `model_reasoning_effort` | Cần kiểm trên đúng app/phiên bản pilot |
| [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) | Markdown/YAML ở `.claude/agents/`, model/effort; môi trường có thể ảnh hưởng effort hiệu lực | Không suy rộng sang Desktop/Cowork |
| [Gemini CLI context](https://geminicli.com/docs/cli/gemini-md/) và [subagents](https://geminicli.com/docs/core/subagents/) | Mặc định nạp `GEMINI.md`; `AGENTS.md` chỉ khi cấu hình `context.fileName`. Vai project ở `.gemini/agents/*.md` | Gemini CLI là host riêng; không lấy đường dẫn/schema này suy cho Antigravity |
| [Antigravity subagents](https://antigravity.google/docs/subagents) | App/CLI có Markdown dưới `.agents/agents/`, tier `inherit`/`flash`/`pro` | Tier không là model ID; schema đã đọc không chứng minh effort tùy ý ở mọi bề mặt |

[Claude Code project instructions](https://code.claude.com/docs/en/memory) bản mới đọc `AGENTS.md` nếu không có `CLAUDE.md` ở project/ancestor; khi có `CLAUDE.md`, cần nhập `@AGENTS.md` hoặc cấu hình đọc cả hai. LAW hiện có `CLAUDE.md` với import này và `GEMINI.md` nhập `AGENTS.md`. Đó là đường nạp **quy tắc Main**, chưa phải đường đăng ký vai. File chỉ dẫn có tác dụng định hướng model; giới hạn quyền cần kiểm bằng host/tool và writer LAW ở điểm thực thi.

**Bằng chứng đã đo:** [pilot Claude Code ngày 17/10](evidence/pilot-host-claude-code-2026-10-17/README.md) có stream/log cho CLI **2.1.81** và **2.1.302**, vai thử qua `--agents`. Định tuyến model theo vai đã chạy: alias `haiku` ra `claude-haiku-4-5-20251001` ở 2.1.81 và `claude-haiku-5-5` ở 2.1.302; thử ID đầy đủ cũng ghi nhận đúng model. Cặp `effort=low/max` trên tác vụ nhỏ chưa cho thấy tác động đủ kết luận. Cấu hình effort không hợp lệ được nạp không báo lỗi ở ca D, nhưng ca đó không gọi vai: chưa chứng minh cách kiểm giá trị lúc thực thi. Đây chưa phải bằng chứng LAW đã projection/cấu hình `roles/` vào host hoặc hỗ trợ Desktop/Cowork.

**Bổ sung19/10 — [A-10 Scout file-native](evidence/a10-scout-native-2026-10-19/README.md), ACCEPTED_WITH_LIMITS:** adapter của chính lab sinh file `.claude/agents/law-scout.md`, một fresh-session CLI2.1.81 không --agents override đã gọi Agent law-scout; child Haiku5.5 Read đúng nguồn giả, MainSonnet5.5 không tự Read, dữ kiện+locator khớp. Reviewer Sol6.1 High soát trace nhận T28 hẹp;266file không đổi/không thêm. CLIbudget0.50USD, telemetry0.1817421USD không phải hóa đơn; effort chưa quan sát. Không nhận lời đếm8dòng khi nguồn có7dòng nội dung+terminal newline/Read hiện thêm trống; không suy chất lượng model hay sandbox. Profile LEGACY hợp lệ/owner nhất quán/lựa chọn rõ được xuất cấu hình, không migrate hoặc cấp quyền. Toàn R4/preset qualified/Worker-Reviewer native/deactivation còn mở.

**Cập nhật tiếp19/10 — [A-10 core một host](evidence/a10-core-native-2026-10-19/README.md), ACCEPTED_WITH_LIMITS:** Worker/Reviewer native và retire đã hoàn tất trong core baseline. Source cuối được Reviewer32test hẹp đạt/0skip; lab một phiên/twochild Sonnet5.5 tạo candidate mới rồi review chỉ đọc, có parent trace, không MainRead/Write.270file cũ giữ hash/chỉ thêm candidate; Reviewer tìm1finding diễn đạt nhỏ, giữ candidate/chưa useracceptance. CLIbudget0.75USD, telemetry0.38191935USD không hóa đơn. Sau retire hai vai, listing mới không còn projectrole, receipt/bytes giữ. Factorypreset vẫn CANDIDATE; chưa effort/sandbox/modelquality/fullR4/rolepacks/release. Điểm mốc Scout ở trên là lịch sử trước core acceptance này.

R4 kế thừa pilot và core proof19/10, chỉ đo bổ sung phần thiếu hoặc bị ảnh hưởng bởi thay đổi adapter/host/schema; không đo lại từ đầu nếu bằng chứng vẫn phù hợp. Chọn host/app thực có cho phần tích hợp còn thiếu; ghi phiên bản, ngày tra/schema, phân biệt **cấu hình / host nhận / quan sát khi chạy / chưa biết**. Contract role chung, adapter chuyển định dạng. Không xuất đồng loạt mọi host.

Khi lập preset/release: tra catalog, account/quota/cách tính chi phí chính thức. Phân biệt thuê bao/allowance và giá API; không nhân token API thành chi phí thực trả của thuê bao. Ước tính có ngày/giả định. Không lấy agent tự xưng làm bằng chứng model. Thiếu quan sát thì ghi rõ, tiếp tục phần không phụ thuộc. Host chưa phù hợp dùng một agent có khai báo, không thêm API runtime ngầm.

## 8. Roadmap LAW-R0–R7 và điều kiện hoàn thành

Các mốc là nhóm năng lực; triển khai theo lát cắt mục 9 để có luồng dùng thật sớm. Mỗi bước thực thi có một owner Local; operator giữ quyết định sản phẩm/chi phí/quyền. Chưa ấn định lịch hoặc phiên bản release trước ước lượng từ lát cắt đầu.

| Mốc / trạng thái 17/10 | Đầu ra và owner kỹ thuật | Điều kiện hoàn thành | Phụ thuộc |
|---|---|---|---|
| **R0 — Đối chiếu và hợp nhất** / đã lập kế hoạch Local, chưa nghiệm thu triển khai | Roadmap, snapshot, nguồn, quyết định và treeview | Phạm vi/owner rõ; không lẫn kế hoạch với hiện trạng; khi mở implementation kiểm lại worktree và chọn host lúc cần | Không cần provider để hoàn tất tài liệu |
| **R1 — Quy tắc và thư mục** / **R1a và A-02 core đã nhận WITH_LIMITS** | AGENTS/PROJECT/continuity, INDEX, hướng dẫn VI/EN, release templates | T01–T04 core đã kiểm trên CLI2.1.81/sonnet4.6; preview/lifecycle I3/RC3 đã nhận. Giữ reporting finding T03, PROJECT-only/persistence/hostkhác chưa kiểm; không gọi toàn bộ R1/AGENTS được chứng minh | R0 |
| **R2 — Catalog và writer** / **một phần: R2a/R2b** | `library.py`, transaction chung, workbook mẫu, UI/API thư viện | ID ổn định; delta idempotent; lỗi/ghi song song/phục hồi đúng; UI/agent cùng sổ; duyệt không gọi AI | R1 tối thiểu, ownership/schema |
| **R3 — Nội dung và dùng lại** / chưa triển khai | Sổ, provenance, revisions, artifacts/dependencies, view nguồn/kết quả | Dùng đúng revision; phần đọc/kiểm rõ; stale theo dependency; giữ quyết định user; không tự chứng minh bằng kết quả AI | R2 writer an toàn |
| **R4 — Roles và profile native** / chưa triển khai tích hợp LAW; có pilot host ở mục 7 | `roles/`, profile/schema, adapter; pack tools chỉ khi thêm vai từ gói lĩnh vực | Preset model/effort cố định từng vai; user đổi qua profile, giữ nhiệm vụ; digest đúng; không đè native; fresh session tích hợp LAW gọi vai thật, dùng lại pilot phù hợp | R1; Scout dùng R2 tối thiểu; thiết kế R4 cùng R2 |
| **R5 — Điều phối và phục hồi** / A-11 và B-03 nhận subset hợp tác, chưa toànR5 | Task/result contract, kiểm binding khi tích hợp, UI/continuity | Một writer; đổi yêu cầu/dừng/trả muộn/timeout/reopen không lặp tác động hoặc nhận kết quả stale; phân biệt công cụ đạt và user đã nhận | R2/R4, binding R3 liên quan |
| **R6 — Cá nhân hóa và pilot** / C-01 nhận subset hợp tác; phần người thật sau MVP theo0.10 | Hướng dẫn, personal skills, UI, A → mẫu → B | Người mới làm/tiếp tục/dùng lại được; ghi can thiệp hỗ trợ; chọn skill về mẫu không kéo dữ liệu/quyền A; A/B độc lập | Lát cắt A/B; bảo toàn migration trước thử A→B |
| **R7 — Migration và phát hành** / chưa triển khai delta | Init/adopt/upgrade/build/check, VI/EN, support matrix, bundle | Package sạch; upgrade/downgrade có giới hạn rõ; dữ liệu/profile giữ được; checksum đúng; chỉ công bố host có bằng chứng | Các lát cắt thuộc release; không bắt mọi host mới cùng đạt |

R1/R4 sửa đồng bộ quy tắc, không nối thêm câu mâu thuẫn. UX đi cùng từng lát cắt. Ownership/migration thiết kế từ R2/R4, không để đến đóng gói mới xử lý profile.

### 8.1 Tranches có thể giao riêng

Mỗi hàng là một đơn vị giao việc có file owner, kết quả kiểm được và dependency. **Đã dựng** chỉ xác nhận cây/file contract tồn tại; **mẫu đã kiểm** chỉ xác nhận những ca ghi ở 8.2; **chờ** chưa có chức năng. Agent tiếp theo bắt đầu bằng diff/worktree hiện tại và hàng được giao, không tự coi cả mốc R1/R2 là xong vì một tranche đạt. Nếu đổi file owner hoặc thứ tự, cập nhật hàng này và handoff trước khi làm tiếp.

R1a/R2a/R2b được làm mẫu trước khi dựng cây vai lõi; A-00 khắc phục thiếu sót về thứ tự này. Từ đây, mọi code R4 phải dùng cây nguồn đã dựng và chốt owner trong tranche tương ứng trước khi triển khai.

| Tranche / trạng thái | Việc và file owner | Đầu ra cần kiểm để bàn giao | Phụ thuộc |
|---|---|---|---|
| **A-00 — Cây nguồn / đã dựng, review tĩnh đạt 17/10** | Tạo `roles/` lõi với ba hợp đồng và README; cập nhật cây ở README VI/EN và mục 4. `packs/` giữ vai trò gói lĩnh vực | Cây trên đĩa trùng treeview; checker package không lỗi; config `PENDING_R4` không bị nhận là preset chạy thật | R0; làm trước code R4 tiếp theo |
| **A-01 — R1a / mẫu đã kiểm** | `AGENTS.md`, `en/AGENTS.md`, `PROJECT.md`, `en/PROJECT.md`: tiếp tục việc, mâu thuẫn, grant theo nhóm, ngoại lệ thư mục | Quy tắc không cấp sẵn quyền và không bắt việc nhỏ lập hồ sơ; checker đạt. Core T01–T04 đã review nhận trong A-02 ngày18/10 trên CLI quan sát; giới hạn/finding reporting giữ ở A-02 | R0; thay đổi tích hợp vai về sau dùng A-00 |
| **A-02 — R1b / A02_CORE_T01_T04_ACCEPTED_WITH_LIMITS,18/10** | `release_templates/`, `docs/` VI/EN, hướng dẫn tạo/adopt và P2; triển khai tĩnh/preview/lifecycle I3 đã review, không thêm code lượt này | Kết hợp2MainFlows/I3/RC3 đã nhận với4lượtCLI/3session mới: T01 tiếp đúng nguồn/bản/quyền, T02 None/STATEhoàn tất không bịa việc, T03 nêu đúng mâu thuẫn khôngchọnmtime/ghi, T04 sửa1câu cùngsession/0tool. ReviewerSol6.1High nhận core; giữ T03 thiếu declaration theoAGENTS9 và unknown PROJECT-only/persistence/hostkhác, không nhận toàn bộAGENTScompliance hoặc người mớiC-02 | A-01; thứ tự theo I-02 rev1 |
| **A-03 — R2a / mẫu đã kiểm** | `tools/library.py`, `tools/library_sync.py`: xem trước rồi ghi ID/hash/revision vào workbook hiện có | T05/T12 phần liên quan: file đúng nơi được ghi, lần hai không nhân bản; dữ liệu người dùng và công thức còn nguyên; file mới vẫn cần đối chiếu | A-01 |
| **A-04 — R2b / mẫu đã kiểm giới hạn** | `tools/transaction.py`, `library_sync.py`: hash lúc đọc, khóa LAW, dòng file thiếu, metadata bản đổi | Test thay bytes, mất/hiện lại, hash xung đột, khóa ghi; bản trước của xác minh có locator trong `LAW history`. Chưa đóng T13/T14 với Excel ngoài khóa | A-03 |
| **A-05 — R2c / đạt phạm vi tĩnh đã review 17/10; 2 blocker cũ resolved** | `library_sync.py`, PROJECT và workbook: cho phép scope nguồn cũ do user chọn, phân giải chuyển tên/copy bằng căn cứ có người xác nhận; không suy ID từ hash | T06–T11 phần source/index/rename tĩnh: guard references trước đọc/khóa; OUT_OF_SCOPE/copy không nối ID; move giữ ID trong cùng plan. Worker sửa 1 vòng, Reviewer kiểm 3 target đạt. Symlink thật/OS khác chưa kiểm; runtime/race chuyển acceptance bắt buộc A-06, không coi toàn writer/R2 đã an toàn | A-03/A-04 |
| **A-06 — R2d / ACCEPTED cooperative Windows WITH_LIMITS,18/10** | library_sync.py writer_lock/helpers hẹp + tests/README; journal-status corrective đã nhận. Không đổi transaction/pins | Matrix T13–T16 và review lockleaf đạt điểm dừng: Reviewer21 test riêng biệt/19 đạt/2 skip1314; Worker module trước sửa nhỏ Reviewer66 collected/64 đạt/2 skip. Hardlink thật gồm controlled fd-hook, không atomic no-follow; residual race/identity0/housekeeping giữ giới hạn. x14 SAFE_REFUSAL_ONLY/PARKED; chưa toàn R2/release | A-04/A-05; verdict/evidence ở HANDOFF |
| **A-07 — R2e / ACCEPTED cooperative Windows WITH_LIMITS,19/10** | library.py + app.py/app_ui.html/API cùng sổ; library_sync.py optional expected_preview guard. Profile/browse/chọn-copy/mở nguồn; preview/apply writer chung | T41/T43/T45-phần nguồn/T46 đạt scope đã review: malformed khác empty; UI đọc không scan/log; open rebind/legacy, FILE_EXT sẵn có; copy không dispatch, hidden-selection rõ; stale preview chặn trước Transaction/x14 giữ. Reviewer16 test riêng biệt đạt/0skip sau sửa nhỏ; Worker146collected/2skip+35browser trước sửa. Không full148/37 sau sửa; runtime/ACL/TOCTOU/large-index limits giữ | A-05 tĩnh/A-06 cooperative Windows đã nhận; T45-output/T47/B-02 còn mở |
| **A-08 — R4a / STATIC_CONTRACTS_ACCEPTED_WITH_LIMITS,19/10** | roles scout/worker/reviewer: agent/checks/config + README, owner bộ khung | Baseline9file+README đã review tĩnh; A-10 sau đó thêm preset candidate và làm sạch Reviewer product contract/checks, đã review delta. implementation_trial chỉ thi công, không quyền hoặc product activation | A-00 static đã nhận; core native evidence ở A-10 |
| **A-09 — R4b / ACCEPTED profile/lifecycle cooperative WITH_LIMITS,19/10** | Helper/schema/profile user-owned, clean lifecycle/projection và entrypoint Main; migration khai báo một owner | P2 resolved: validation/plan/hash/backups cùng captured bytes PROJECT/profile; PROJECT read-only precondition config, wholefile đổi cần preview lại. Reviewer7test đạt/0skip, Worker module46collected/45đạt/1skip; không full198/fullgate source mới. A-10 đổi diagnostic NOT_INSPECTED và chỉ classification operation thật; authority_usable=False/profile_refUNSUPPORTED giữ | A-01/A-08 đủ static; verdict/evidence HANDOFF; Scout A-10 đã nhận |
| **A-10 — R4c / CORE_ONEHOST_ACCEPTED_WITH_LIMITS,19/10** | Fixed3role/preset candidate/native receipt/binding/collision/package + bounded retire trên Claude Code2.1.81. Reviewer sửa nhỏ2file, không engine/schema mới; factorypresets không tự register/grant | Source cuối32test hẹp đạt/0skip (không fullmodule72); Worker66native/46profile1skip/11gate/42package trước sửa giữ riêng. Native WorkerSonnet5.5 tạo candidate, ReviewerSonnet5.5 chỉ đọc+finding/locator, Scout proof cũ giữ. Retire2role/CLIlisting mới không còn projectrole; effortnull/UNSUPPORTED, Write không sandbox, retire không livecancel/autoactivate | A-08/A-09/A-03 đủ core; evidence mục7/HANDOFF. Đạt điểm dừng A-10 một host; fullR4/rolepacks/enforcement/quality/release không đóng từ đây |
| **A-11 — R5a / ACCEPTED_WITH_LIMITS,19/10** | Docs+recipe/probe trên owner v3/P-CN1/P-CTX/library hiện có, không runtime helper/schema/task engine mới. Reviewer sửa path/slot escape, metadata context_refs và guard link sổ. Raw current TASK/RESULT/candidate/source/context/sổ bind vào publish task riêng; staged đúng candidate đã kiểm | T29/T30 nhận **subset hợp tác đã kiểm**; sourcecuối25đạt/0skip=21probe+4projection. Recipe Worker1candidate, Scout delta chỉ giao thức/chưa probe riêng; không live agent/nhiều TASK, generic PASS/authority/user acceptance hoặc toàn R5. Verdict/hash/giới hạn ở HANDOFF đầu | A-07/A-10 core đủ; B-01 có thể audit tiếp. B-03 giữ stop/timeout/retry, B-01/B-02 giữ lineage |
| **B-01 — R3a / ACCEPTED_WITH_LIMITS,19/10** | LAW content lazy/append+supersedes, source-event/history/basisrevision cùng SHA riêng; query workbook-only nhiều chiều UNOBSERVED, chung writer. Reviewer sửa literal catalog, crossvalidation managed sheets/history, required provenance và event payload identity; không schema/engine mới | T17–T21 nhận **fixture/API/CLI hợp tác**:21content+15regression sourcecuối đạt/0skip +1probe Main B-01→A-11. Decision/oldbasis giữ, semanticchange samesha invalidates, retry chỉ lịch sử, inference/literal không nâng quyền. Chưa toànR3/UI/liveAI/Office/fullgate; hash/giới hạn HANDOFF | A-06/A-11 đủ; B-02 có thể audit tiếp, không dispatch lại B-01. B-03 giữ gián đoạn |
| **B-02 — R3b / ACCEPTED_WITH_LIMITS,19/10** | Hai sheet lazy artifacts/relations, tools/artifacts.py1222dòng/writer chung/3read routes+UI hồ sơ nguồn. Reviewer sửa copy thiếu basis, mixed unknown, reader junction, P-CN1 identity recheck và closure trước opener; không engine/receipt/current-pointer mới | T42/T44/T45-output/T47/T48 nhận **fixture/API/CLI/UI hợp tác**:34test+5panel+2browser trước sửa cuối,9target sau sửa cuối/0skip;3nợ docs/package đạt riêng. A→B→C stale, B2 không redirect B1/C1, inference/limits/unknown giữ; chưa fullmodule/Office/liveAI/toànR3/R5/release. Hash/giới hạn HANDOFF đầu | B-01/A-07/A-11 đủ; B-03 đã nhận subset, không dispatch lại B-02 hoặc refresh MANIFEST từ đây |
| **B-03 — R5b / ACCEPTED_WITH_LIMITS,19/10** | Recipe 5hàm + probe lifecycle trên owner cũ; Reviewer sửa5finding schema-before-write/review veto/target/identity/no-call note. Không runtime/schema/engine/host cancellation mới | T31–T35 subset hợp tác: Reviewer33đạt trước correction;14target đạt trước sửa oracle,4target sau/0skip; không fullmodule cuối. Stop chỉ chắc khi host xác nhận, reconcile trước retry, nội dung/nhậnB riêng. Hash/limits HANDOFF đầu; chưa toànR5 | A-11/B-01/B-02 giữ; C-01 đủ dependency audit, không dispatch lại B-03 |
| **C-01 — R6a / ACCEPTED_WITH_LIMITS,20/10** | Guide VI/EN mục11 + PersonalReuse/harness trên owner cũ; Reviewer sửa4finding grant-target/bytes-index/baseline inventory/junction, đồng bộ4HTML dẫn xuất; không runtime/ownership policy mới | T36 subset hợp tác A→mẫu cá nhân→B VI/EN: Reviewer8đạt trước sửa,9target đạt sau/0skip. A/template/B độc lập, manifest chỉ fixture, user/native acceptance mô phỏng; chưa fullR6/D-01/custom-shared upgrade. Hash/limits HANDOFF đầu | B-02/B-03 giữ; đủ dependency audit C-02, không dispatch lại C-01 hoặc refresh MANIFEST repo |
| **C-02 — R6b / PREP_ACCEPTED_WITH_LIMITS,20/10; DEFERRED_POST_MVP theo0.10; PILOT_NOT_RUN** | Nhận3file feedback/pilots/c02 sau review: khám phá L→N cùng nguồn, không bộ2/benchmark; sửa rò oracle/AI context/nhiễm host, quy ước nguồn và ghi nhận HT không quy nguyên nhân | T37/T38 vẫn NOT_RUN: cần người mới thật và điều kiện chạy; lộ/chưa xác minh oracle hoặc nhiễm context thì tiêu chí nội dung liên quan không đánh giá được. Bộ chuẩn bị không thay usability/user acceptance/fullR6 | A-02/B-03/C-01 giữ; thu phản hồi sau MVP, không chặn D-02; khi tổ chức pilot vẫn dùng đúng kit, không agent giả user |
| **D-01 — R7a / D-01a nhận WITH_LIMITS,20/10; P4 OPEN** | Giữ mục tiêu schema migration/init-adopt-upgrade/bản sạch/profile-role ownership/P1-P4. P1 diagnostic đã nhận; D-01b nhận subset tài liệu/archive bền, giữ .new; writer chưa delete/undo sau commit | T39 vẫn chưa nghiệm thu toàn bộ: nâng/hạ giữ nguồn/quyền/ID, `.new` có lựa chọn an toàn, schema không hiểu từ chối. Không coi metadata identity là migration/manifest hardening | A-09/B-02/C-01 giữ; C-02 vẫn NOT_RUN, không release |
| **D-01a — P1 / ACCEPTED_WITH_LIMITS,20/10** | Diagnostic version vs toànMANIFEST baseline, metadata cộng thêm/CLI; không thay read_manifest/plan/guard/writer, baseline bytes tái dựng khớp; docs/4HTML rõ EN/KNOWN không authority | Reviewer15target đạt/0skip/81.628s source code/test cuối. UNKNOWN không cấp quyền/đổi plan; duplicate/malformed legacy còn, không redrun8baseline/fullsuite. Hash/limits HANDOFF đầu; chưa toànT39 | P1 đạt scope hẹp; D-01b đã nhận subset, D-01c đã nhận guide subset; không dispatch lại D-01a/refresh MANIFEST repo |
| **D-01b — P4 subset / ACCEPTED_WITH_LIMITS,20/10** | Tám guide Markdown, preview hai raw hash, archive bền trước thay current; giữ .new, tự lấy bản cũ thành file mới. Reviewer sửa race legacy diff/no-op journal/partial advice | Source cuối49target đạt/0skip; CLI fixture tối giản verify và upgrade sau giữ archive, còn .new cũ hoặc chặn pending. Không delete/resolve/undo/file điều khiển; P4/T39 OPEN | D-01a giữ; tiếp thiết kế kết thúc pending riêng, không release |
| **D-01c — P4 guide finish / ACCEPTED_WITH_LIMITS,20/10** | Current giữ, snapshot/record commit kiểm đủ rồi một Windows no-replace rename .new vào archive; observe chỉ đọc, cùng8guide. Reviewer sửa trạng thái cleanup sau committed | Reviewer85đạt trước sửa;16target source cuối đạt/0skip gồm1Chromium flow mới. Minimal lifecycle/no.cvf, symlink thật chưa đo/race còn, không Undo/file điều khiển. P4/D-01/T39 OPEN | D-01a/b giữ; audit gap còn lại trước giao việc, không release |
| **D-01d — T39 integration / ACCEPTED_WITH_LIMITS,20/10** | Project projected-v3 VI/EN, workbook B01/B02 có dữ liệu/quan hệ thật, upgrade→force downgrade cùngschema, giữ archive D01b/c. Reviewer sửa choices-file/refusal oracle và seed graph/isolation | Source cuối6test đạt/0skip/19.144s, runtime giữ; future profile opaque/config refused khác unknown .cvf blocked. Không schema migration/fullT39/allowlist/release | D-01a/b/c giữ; chốt gap P4 theo owner/file điều khiển trước việc kế |
| **D-01e — P4 entrypoint finish / ACCEPTED_WITH_LIMITS,20/10** | Giữ current, archive pending của AGENTS/CLAUDE/GEMINI và en/ counterparts; FINISH14 tách REPLACE8, UI vào độc lập | Reviewer55scope đạt/0skip gồmChromium,5HTTP+1amendment đạt; harness Host10053 tái hiện5/12 và sau sửa0/12, app.py giữ. Không áp instruction/quyền/Undo; P4/D-01/T39 OPEN | D-01a–d giữ; chốt support matrix/gap còn lại trước việc kế, không release |
| **D-01f — matrix/gap / ACCEPTED_WITH_LIMITS,21/10** | Matrix nhóm file/owner và guide VI/EN theo evidence a–e; A1 sửa unsupported/daily guide; Reviewer A2 sửa guard có điều kiện, metadata/index, lịch sử So sánh, incoming pack và df_ro, dựng6HTML. Không runtime mới | D01F_SUPPORT_MATRIX_ONLY+A1+A2: source cuối1test chữ UI đạt/0skip, JS chỉ parse,10HTML khớp; UI ngoài2khóa đảo về baseline,5protected+app.py giữ. Chưa visual/fullT39/P4/host support D-02 | D-01a–e giữ verdict; matrix/gap đã chốt đúng subset, phần pending ngoài14/schema migration còn mở; C-02 NOT_RUN, không release |
| **D-01g — script finish / ACCEPTED_WITH_LIMITS,21/10** | Workorder WORKORDER_D01G_2026-10-21.md: finish-only đúng tools/audit_scripts.py và script spreadsheet-check; REPLACE8 giữ, FINISH14→16, pipeline archive/rename/observe giữ, không áp/chạy code | D01G_SCRIPT_FINISH_ONLY; phải phân allowlist với managed, audit_scripts chưa có MANIFESTrepo, fixture projection quản lý cả2; Reviewer16ca source test cuối đạt/0skip gồm Chromium,8protected khớp; raw inverse lịch sử NOT_VERIFIED, sai lệch --help giữ; Reviewer độc lập nhận subset, M1 đã đóng | D-01a–f/SCRIPT-01 giữ verdict; không pending generic/pack/schema migration/P4 tổng thể/C-02/D-02/release |
| **D-02 — R7b / PRERELEASE ĐÃ CÔNG BỐ; CI MAIN ĐỎ/L19 SOURCE ĐÃ SỬA, CI MỚI ĐANG CHẠY; CHƯA FINAL** | Chốt source/docs/support matrix trong phạm vi đã đo, chạy gate nguồn và nghiệm thu gói/nâng cấp/phục hồi; không thêm host/adapter trước MVP | T40 và release gate của phạm vi công bố: ZIP/checksum, RC verify, dữ liệu/phần riêng được giữ, host có proof đúng app/phiên bản; không dùng mock thay CI hoặc hỗ trợ host chưa đo | D-01 đã nhận đúng subset + gate kỹ thuật E07; C-02 sau MVP theo0.10 |

Tiến độ lát cắt A: **A-02/A-06/A-07 cooperative Windows, A-08 static, A-09 profile/lifecycle và A-10 core một host đã nhận WITH_LIMITS; A-01/A-03/A-04 có mẫu, A-00/A-05 đã review tĩnh; x14 PARKED.** A-11/B-01/B-02/B-03/C-01 và D-01a–f đã nhận subset ở các hàng tương ứng; bước tiếp theo mục0, không giao lại audit A-11. Profile/projection và core acceptance không thành grant, host enforcement, fullR4 hoặc release.

Điểm kết thúc A-10 core trên một host (không thêm gate ngoài T22–T28/phạm vi đã chốt):

- [x] Scout offline + file-native T28 lab được nhận WITH_LIMITS.
- [x] Audit phần còn lại và review một brief ba-vai/preset/retire,19/10.
- [x] Claude thi công offline, giữ nguồn/native riêng và bằng chứng hồi quy Scout; Worker66native/46profile1skip/11gate/42package trước sửa Reviewer.
- [x] Reviewer nhận delta WITH_LIMITS, sửa nhỏ2file và32test hẹp đạt/0skip; listing trước/sau retire đã đối chiếu và đo source cuối.
- [x] Orchestrator một lab Worker→Reviewer/retire, Reviewer soát evidence nhận A10_CORE_ONEHOST_ACCEPTED_WITH_LIMITS19/10. Không fullR4/rolepacks/enforcement, live cancel hoặc quality người mới C-02.

Khi nhận một tranche, agent ghi ngắn trong handoff: input revision/commit và file owner; thay đổi thực tế; phép kiểm cùng artifact kết quả; giới hạn/điều kiện còn mở; hàng tiếp theo đủ dependency. Không thêm một sổ trạng thái hay roadmap riêng.

#### A-06 — ma trận bằng chứng và điểm kết thúc đã chốt18/10

Đối chiếu đúng T13–T16 trong R2 gốc. Đây là phạm vi nghiệm thu hữu hạn cho cooperative Windows đã đo; không đổi các assertion bảo toàn hoặc biến unknown thành PASS. Main dùng kết quả review delta để nhận tranche, Worker không tự đóng.

| ID | Bằng chứng phù hợp đã có | Giới hạn/việc còn lại |
|---|---|---|
| T13 — user/Excel lưu khi LAW cập nhật | Test user-save sau plan/before-commit, recovery conflict giữ userbytes; E2 COM Worker đã đối chiếu script/log.3findingWindows cũ resolved | Hash→replace cuối không atomic; E2 không kiểm mọi thời điểm. Không hứa chống tuyệt đối ứng dụng không hợp tác; không suy mọi Office/OS |
| T14 — ngắt/disk/quyền, phục hồi trung thực | Stage/backup/commit faults, processkill/resume/rollback và disk/permission mocks có provenance; strict-journal và lockleaf corrective đã review nhận. Hardlink có sẵn từ chối trước open/byte-lock; real fd-hook nlink2 từ chối và đóng đúng một lần | Mock/hook khác lỗi OS/race kernel thật. Existing-open có thể có handle ngắn; không atomic no-follow, alias sau kiểm chưa được ngăn. Symlink thật2skip1314; identity0 bị từ chối, housekeeping có thể ở lại |
| T15 — thiếu sheet/cột, sổ hỏng, thiếu dependency | Invalid-workbook tests trong moduleWorker55 đạt; LibraryNotChecked.test_missing_openpyxl_is_not_checked_with_exit_two có trong structured-tools/RC3 đã nhận, dùng mô phỏng import thiếu; code thư viện giữ | Không cài/gỡ dependency hay chạy lại môi trường khác. RC3 là evidence bytes lịch sử; library_sync mới chỉ có focused proof sauwording, không giả fullgate mới |
| T16 — minh họa tách nghiệp vụ, macro/link | **Template/static-fixture/read-API accepted WITH_LIMITS**: Danh mục0dòng, Ví dụ6dòng riêng; loadAPI trả0; template0VBA/external-link parts/relations,hashgiữ. Reviewer đối chiếu source/evidence18/10 | Không lấy recovery labelT16 cũ thay proof. Chưa CLIinit/Excel/mọiworkbook hoặc macro-host safety; không tạo gate mới ngoài phạm vi template mặc định này |

**Điểm dừng đã đạt 18/10:** leaf corrective đạt acceptance hữu hạn và Reviewer Sol6.1 High nhận **REVIEW_ACCEPTED_A06_LOCKLEAF_CORRECTIVE_WITH_LIMITS**. Orchestrator nhận **A-06 cooperative Windows WITH_LIMITS** cùng matrix T13–T16; 21 test độc lập riêng biệt gồm19 đạt/2skip1314, không gán full module sau test bổ sung. Giữ x14 SAFE_REFUSAL_ONLY/PARKED, residual race/unsupported environment và nghĩa vụ báo cáo thật. Không tự đóng toàn R2/release hoặc yêu cầu mọi host/OS để mở audit A-07; không hạ gate.

### 8.2 Ba tranche mẫu đã thực hiện trong lát cắt A

| Tranche | Code/artifact đã có | Đã kiểm / giới hạn còn lại |
|---|---|---|
| **R1a — Tiếp tục và quyền giao vai** | AGENTS và PROJECT VI/EN nêu cách xử lý STATE/HANDOFF mâu thuẫn, quyền gọi vai có thể được user cấp theo nhóm việc, ngoại lệ nguồn cũ ghi ở PROJECT. Không có quyền nào được điền sẵn trong mẫu | Lịch sử mẫu17/10: check_package đạt, chưa pilot phiên mới. Cập nhật18/10: core T01–T04 và proof preview/I3 đã nhận theo A-02; giữ giới hạn/finding ở hàng8.1, không suy mọi host hoặc cập nhật continuity đã được kiểm |
| **R2a — Ghi nhận file nguồn** | `library.py sync` xem trước, `sync --apply` dùng `library_sync.py` ghi ID `SRC-...`, hash, revision, trạng thái vào workbook hiện có. Chỉ quét bốn nhóm; giữ các cột nghiệp vụ, công thức và file nguồn. File mới vẫn “Cần đối chiếu” | Test trong bản sao project: preview, ghi, lặp không đổi, công thức/ghi chú còn nguyên. Chưa có UI writer, chưa xử lý ngoại lệ nguồn nằm ngoài bốn nhóm |
| **R2b — Xung đột và dấu vết đổi nguồn** | Khóa giữa các writer LAW; transaction nhận hash từ lúc đọc; file mất giữ dòng; file đổi tăng revision, đặt lại mức xác minh và ghi metadata bản trước ở sheet `LAW history`. Cùng hash ở đường dẫn mới nhận ID mới cho đến khi người dùng đối chiếu | Test chặn hash/lock, mất rồi xuất hiện lại, đổi bytes, không suy di chuyển từ hash. Excel/program ngoài LAW không theo khóa: có thể phát sinh race giữa lần kiểm hash cuối và replace; chưa chứng minh an toàn tuyệt đối hoặc hoàn tất T13/T14 |

Kiểm tập trung: `tests/test_library_sync.py` **6 đạt**, `test_structured_tools.py` **15 đạt**, `test_transactions.py` **24 đạt**; `check_package.py --release` **0 lỗi, 0 cảnh báo** và `git diff --check` đạt trên worktree này. Các kết quả chỉ xác nhận tranche mẫu, không thay cho toàn suite, pilot host, nghiệm thu người mới hoặc release. Chưa gọi provider trong đợt này.

### 8.3 Quy tắc code và review cho người duy trì

Áp dụng khi sửa **kho nguồn LAW**, không áp dụng cho mỗi tác vụ văn phòng trong project người dùng. Đây là quy tắc triển khai gọn theo tranche, không là chuỗi bảy bước hay bộ work order/gate của dự án khác. `AGENTS.md` là điểm vào; mục này giữ chi tiết cho agent tiếp theo.

1. **Nhận việc:** đối chiếu worktree, hàng tranche, dependency, file owner và phần chưa đạt. Hàng 8.1 là phiếu việc mặc định. Nếu việc vượt một tranche, nhiều owner cùng sửa, hoặc acceptance chưa đủ rõ, ghi brief ngắn ngay trong HANDOFF hay hàng tranche: mục tiêu, phạm vi, ranh giới không sửa, đầu ra và cách kiểm. Không tạo work order riêng theo thói quen.
2. **Sửa trong ranh giới:** một tranche có một owner tích hợp. Thay đổi schema, quyền, dữ liệu user, native projection hoặc migration phải chỉ ra cách giữ tương thích/phục hồi trước khi ghi. Phát hiện ngoài phạm vi thì ghi lại và đổi tranche khi cần; không âm thầm gộp vào việc đang làm. Không cấp quyền gọi agent phụ từ tên vai hay từ roadmap.
3. **Tự soát và kiểm đúng phần:** agent thực hiện xem diff, đối chiếu acceptance từng mục đã chạm, ghi phép kiểm thực sự chạy và lỗi/ca chưa kiểm. Sửa lỗi ở phạm vi tìm thấy. Không coi test/checker đạt là bằng chứng cho hành vi host, an toàn dữ liệu ngoài công cụ hoặc việc user đã chấp nhận. Không chạy lại rộng chỉ để lặp bằng chứng còn hiệu lực. Giữ EOL khi sửa; file mới theo .gitattributes, không chuẩn hóa file -text đã pin. Đọc/ghi phải giữ newline từ đầu đến cuối; soát EOL các file đã chạm bằng --check-eol cùng git diff --check, không coi diff sạch là bằng chứng EOL.
4. **Review theo rủi ro:** sửa nhỏ trong một owner có thể đóng sau tự soát và kiểm liên quan. Cần reviewer độc lập với người triển khai trước khi đóng tranche có nguy cơ mất/ghi đè dữ liệu; đổi quyền, vùng nguồn được quét, ranh giới tin cậy hoặc cấu hình native; migration/upgrade; release; hoặc thay đổi nhiều owner mà một lỗi lan rộng. Reviewer nhận diff, acceptance, evidence và giới hạn; kiểm các rủi ro còn hở, không dựng lại implementation. Trong quyền operator đã cấp tại PROJECT, Main chủ động gọi Reviewer đúng preset tranche 8.4, không hỏi lại; operator chọn model/effort Worker khi giao Claude. Reviewer sửa ngay lỗi nhỏ có nguyên nhân/cách sửa rõ trong phạm vi review, kiểm đúng phần sửa và ghi tác giả/phần sửa trong HANDOFF; không đẩy lại Worker hoặc thêm vòng review chỉ cho sửa nhỏ. Sửa lớn, đổi schema/quyền hoặc xử lý dữ liệu phải tách giao việc. Nếu chưa có người/agent được giao quyền review, ghi `IMPLEMENTED_PENDING_REVIEW`, không tuyên bố tranche đạt. Chỉ định riêng mới nhất của operator được ưu tiên.
5. **Bàn giao và đóng:** HANDOFF ghi input revision/commit, file đã đổi, bằng chứng/giới hạn, kết quả review hoặc trạng thái chờ review, và tranche tiếp theo đủ dependency; STATE giữ ảnh chụp ngắn; phần tự soát HANDOFF ghi kết quả EOL so baseline và mọi chuyển EOL có chủ đích. Chỉ đánh dấu đạt đúng phạm vi đã kiểm. Commit tách theo tranche khi được giao quản lý commit; release còn phải qua gate ở `tools/README.md`, nghiệm thu bản sao project và support matrix theo R7.

Review độc lập ở đây là kiểm code và bằng chứng triển khai LAW; vai `roles/reviewer/` là vai chức năng của sản phẩm, chưa phải reviewer code tự động. Quy trình này có thể siết thêm khi pilot cho thấy một loại lỗi lặp hoặc phạm vi phát hành tăng; điều chỉnh tại owner này thay vì tạo registry/gate song song.

### 8.4 Phân vai model/effort khi thi công roadmap

**Ngoại lệ operator18/10/2026:** đã cho Main tự động hóa Worker/thử nghiệm qua Claude CLI hoặc Alibaba API
trong lab/bản sao/worktree riêng, theo scope PROJECT VI/EN. Ghi version/provider/model/effort quan sát,
scope và giới hạn lượt trước chạy; review diff trước tích hợp. Không mở global/admin; không dùng proof CLI
thay VSCode hoặc gán Qwen thành Sonnet/Opus. Preset native17/10 dưới đây giữ là baseline lịch sử.

**Operator chốt 17/10/2026:** dùng các preset dưới đây làm điểm bắt đầu để quan sát chất lượng thi công trong phiên native. Đây là phân công cho agent **xây dựng LAW**; preset các vai chức năng trong sản phẩm phân phối vẫn thuộc R4. Chưa có benchmark so sánh tỷ lệ lỗi giữa các cấu hình. Lượt thử phân công này dùng agent trong phiên, không khởi chạy Codex/Claude CLI. Chọn preset không tự cấp quyền gọi agent phụ; chỉ dispatch trong phạm vi operator đã giao.

**Mốc thông tin kiểm tra: 17/10/2026 — revision 2.** Các nguồn dưới đây là căn cứ chọn cấu hình thử, không chứng minh chất lượng trên LAW:

| Nguồn đã kiểm | Thông tin dùng cho quyết định thử |
|---|---|
| [OpenAI Models](https://learn.chatgpt.com/docs/models) và [Model selection](https://learn.chatgpt.com/docs/model-selection) | Sol 6.1 cho việc phức tạp; Luna cho việc rõ phạm vi. Effort cần hiệu chỉnh theo tác vụ/model; chọn Sol Medium/High và Luna High/Extra High làm điểm thử |
| [Sonnet 5.5, công bố 28/09/2026](https://www.anthropic.com/claude-sonnet-5-5) | Chọn Sonnet High làm Worker thử đầu cho phần lớn tranche. Anthropic ghi nhận Max thấp hơn Extra High ở FrontierCode do một số ca timeout/sửa vượt scope; không mặc định dùng Max |
| [Haiku 5.5, công bố 07/10/2026](https://www.anthropic.com/claude-haiku-5-5) | Có effort tùy chỉnh và định hướng subagent cho coding; thử Scout Medium/High, đồng thời mở ứng viên Worker High cho sửa hẹp, dễ kiểm |
| [Artificial Analysis: Sonnet 5.5 High / Sonnet 5 Extra High](https://artificialanalysis.ai/models/comparisons/claude-sonnet-5-5-high-vs-claude-sonnet-5-xhigh) và [Haiku Medium / Sonnet High](https://artificialanalysis.ai/models/comparisons/claude-haiku-5-5-medium-vs-claude-sonnet-5-5-high) | Kết quả độc lập bổ sung cho công bố hãng; hiệu năng thay đổi theo bài và effort. Không ghép điểm từ các thiết lập khác nhau để kết luận model nào tốt hơn cho LAW |
| [Claude Code model/effort](https://code.claude.com/docs/en/model-config) | Effort mặc định có thể khác giữa app và API; yêu cầu model/effort cần được ghi và đối chiếu khả năng phiên thực |

Các file `roles/<vai>/config.json` ghi preset thi công dưới `implementation_trial`, với ngày kiểm, revision và `quality_status: NOT_EVALUATED_ON_LAW`. `host_presets` vẫn chờ R4: metadata thử không tự trở thành profile sản phẩm, file native hay quyền dispatch.

| Vai khi thi công | GPT | Claude |
|---|---|---|
| Reviewer độc lập | **Sol 6.1 High**; Medium cho hàng nhẹ trong bảng dưới | **Opus 5.5 High**; Medium cho hàng nhẹ |
| Worker mặc định | **Sol 6.1 Medium** | **Sonnet 5.5 High** |
| Worker logic khó | **Sol 6.1 High** | Bắt đầu **Sonnet 5.5 High**; cân nhắc **Extra High** theo vấn đề cụ thể |
| Scout | **Luna High** | **Haiku 5.5 Medium**; High khi cần truy nhiều quan hệ |

Main giữ đầu mối tích hợp; chủ động gọi reviewer GPT Sol 6.1 theo effort của từng tranche trong bảng dưới khi đã có bàn giao cần review. Operator chọn/điều chỉnh model và effort Worker khi copy giao Claude; ghi lựa chọn thực tế cho lượt đó, không tự đổi preset nền từ một lượt thử. Chỉ định riêng mới nhất của operator được ưu tiên hơn bảng. Worker nhận từng tranche có phạm vi rõ; Scout khảo sát nguồn/đường đi và trả locator, giới hạn. Reviewer độc lập với việc triển khai tranche theo 8.3; giữ vai Main không tự chứng minh tính độc lập nếu Main đã trực tiếp làm code. Reviewer đọc diff, acceptance và evidence, sửa ngay lỗi nhỏ theo 8.3 và ghi rõ phần mình sửa.

| Tranche | Worker GPT | Worker Claude | Reviewer GPT / Claude |
|---|---|---|---|
| **G-00–G-04** — thiết kế quyền, contract, checker và điểm chặn | Sol 6.1 High | Sonnet 5.5 High; operator đổi khi giao, không tự tăng effort | Sol 6.1 High / Opus 5.5 High |
| **A-00, A-02** — cây thư mục, đồng bộ hướng dẫn/mẫu | Luna Extra High | Sonnet 5.5 High; Haiku 5.5 High là ứng viên thử với phần sửa hẹp | Sol 6.1 Medium / Opus 5.5 Medium |
| **A-01, A-03, A-07, A-08** — quy tắc, writer cơ bản, UI, hợp đồng vai | Sol 6.1 Medium | Sonnet 5.5 High | Sol 6.1 High / Opus 5.5 High |
| **A-04, A-05, A-06** — xung đột ghi, đường dẫn, Excel và phục hồi | Sol 6.1 High | Sonnet 5.5 High; A-06 cân nhắc Extra High khi có race/phục hồi khó | Sol 6.1 High / Opus 5.5 High |
| **A-09, A-10, A-11, B-03** — profile, adapter, điều phối, kết quả trả muộn | Sol 6.1 High | Sonnet 5.5 High; cân nhắc Extra High khi nhiều trạng thái/ranh giới tương tác | Sol 6.1 High / Opus 5.5 High |
| **B-01, B-02, C-01** — revision, lineage, cá nhân hóa A→mẫu→B | Sol 6.1 High | Sonnet 5.5 High | Sol 6.1 High / Opus 5.5 High |
| **C-02** — chuẩn bị và tổng hợp pilot người mới | Sol 6.1 Medium | Sonnet 5.5 High | Sol 6.1 High / Opus 5.5 High |
| **D-01, D-02** — migration và phát hành | Sol 6.1 High | Sonnet 5.5 High; D-01 cân nhắc Extra High khi migration có nhiều nhánh phục hồi | Sol 6.1 High / Opus 5.5 High |

Luna Extra High và ứng viên Haiku High chỉ làm Worker khi scope hẹp, acceptance rõ và dễ kiểm bằng máy. Với Haiku, ghi rõ phần việc được chọn thử và kết quả review trước khi mở rộng. Tăng effort không bảo đảm tương đương model lớn hơn. Sonnet High là mức thử đầu; trước khi đổi sang Extra High, ghi vấn đề cần giải, phạm vi và lý do trong HANDOFF. Max dành cho vấn đề cụ thể còn vướng sau Extra High, chưa là lựa chọn nền. Extra High tương ứng `xhigh` khi host hỗ trợ; nếu model/effort không có trong phiên, ghi thiếu và lựa chọn thay thế thực tế, không tự coi giá trị khác là preset đã áp dụng. Ghi rõ phiên bản model khi host cung cấp; không suy model thực từ alias hay lời agent tự nhận.

Khi thi công, bổ sung ngắn vào HANDOFF hiện có: tranche và vai được giao; model/effort yêu cầu và thực tế quan sát được (không quan sát được ghi rõ); acceptance/phép kiểm đã đạt; lỗi reviewer tìm thấy và số vòng sửa; mức can thiệp của operator, thời gian/chi phí nếu có số đo. Không tạo registry đánh giá mới. Chất lượng được xét bằng hành vi và lỗi cụ thể; lượt đã có code trước preset này giữ nguyên bằng chứng lịch sử, không gán lại model hay chạy lại chỉ để đủ bảng. Mẫu triển khai A-02/A-05 đã có ở17/10; pilot hành vi A-02 ngày18/10 thực chạy sonnet4.6/CLI2.1.81, high requested, không phải mẫu thi công Sonnet5.5 hoặc effort đã xác minh. Dữ liệu chưa đủ xếp hạng các model.

**Mẫu A-00/A-02 ngày 17/10/2026:** Worker yêu cầu Haiku 5.5 High, phiên tự báo model Haiku 5.5 nhưng effort chưa quan sát được. Reviewer độc lập được tool dispatch bằng `gpt-6.1-sol`, effort `medium`, ngữ cảnh riêng. A-00 đạt kiểm tĩnh; Reviewer đã sửa ba chỗ diễn đạt VI/EN, dựng lại HTML và ghi nhận đúng 9 vị trí thông báo thay đổi. A-02 còn blocker preview do PROJECT/manifest có trước Worker và T01–T04 chưa kiểm phiên mới. Không thấy P1 hay lỗi mới làm mất dữ liệu trong delta A-02; HTML và các ca phục hồi nhỏ đã được reviewer kiểm có mục tiêu. Chi tiết, phần Reviewer tự sửa, phân biệt lỗi mới/kế thừa và giới hạn ở HANDOFF; một mẫu chưa đủ xác nhận chất lượng preset hoặc đổi model mặc định.

**Mẫu A-05 ngày 17/10/2026:** Worker yêu cầu Sonnet 5.5 High, phiên tự báo `claude-sonnet-5-5`, effort chưa quan sát. Reviewer độc lập `review_a05_sol_high` được tool dispatch bằng `gpt-6.1-sol`, effort `high`, ngữ cảnh riêng. Chưa đạt: tái hiện P1 ghi workbook ngoài project qua junction tại references và P2 nối ID từ OUT_OF_SCOPE sang bản sao. Chưa xác định lỗi mới/kế thừa do thiếu snapshot trước Worker. Reviewer sửa lỗi backtick do lượt review A-02 (2 Markdown/4 HTML), HTML 10 trang và 2 test release-tree có mục tiêu đạt; không chạy lại toàn suite, không sửa manifest/logic dữ liệu. Brief sửa/giới hạn ở HANDOFF; chưa đủ kết luận chất lượng model hoặc đổi preset.

**Kiểm delta sửa A-05, cùng ngày:** Worker sửa 1 vòng, vẫn tự báo Sonnet 5.5, effort chưa quan sát; báo 25 test đạt và 5 ca mới đỏ trên code cũ. Cùng Reviewer Sol 6.1 High chạy độc lập 3 target đạt, xác nhận 2 blocker cũ resolved. A-05 đạt phần source/index/rename tĩnh đã kiểm. Reviewer tái hiện junction tại `.agent` làm khóa/journal ghi ngoài project: P1 còn mở, owner A-06 (writer_lock + transaction), cùng kiểm ranh giới kiểm→ghi phải đạt trước A-07/release. Không hạ P1 thành ghi chú ngoài scope; chưa tuyên toàn writer/R2 an toàn. Evidence, giới hạn và brief A-06 ở HANDOFF; không suy xếp hạng model từ mẫu này.

**Mẫu A-06 ngày 17/10/2026:** Worker tự báo Sonnet 5.5, effort chưa quan sát; báo 71 test đạt và Excel E1–E3 qua COM, chưa có locator script/log để đối chiếu. Reviewer độc lập `review_a06_sol_high` được tool dispatch `gpt-6.1-sol`/`high`, chạy 11 target đạt/0 skip; repro thật xác định 2 P1 (link staging/runtime source làm ghi và di chuyển file ngoài; resume/rollback ghi đè user save sau kiểm hash) và 1 P2 mới trong takeover khóa mồ côi cho 2 writer cùng vào. A-06 chưa đạt, chặn A-07/release; không tự sửa code boundary/protocol dữ liệu. Runtime gốc tĩnh và Windows giữ references đạt các ca đã kiểm, không chứng minh toàn writer/recovery an toàn; chi tiết/brief sửa ở HANDOFF. Không gán mọi finding thành regression mới hoặc suy xếp hạng model.

**Kiểm delta sửa A-06, cùng ngày:** Worker báo 85 test đạt/1 skip; cùng Reviewer Sol 6.1 High chạy 13 target đạt/0 skip, xác nhận 3 finding cũ resolved trong phạm vi Windows đã kiểm. A-06 vẫn chưa đạt: apply nhận diện x14 nhưng ghi mất validation, cảnh báo sau ghi; log Excel Worker 10→0, repro Reviewer mất 5 validation tùy biến. Chặn known loss trước transaction, không dựng lại mẫu hoặc thêm opt-in mất dữ liệu; preview vẫn đọc được. Reviewer sửa 1 dòng cleanup stdout test và rerun hẹp đạt. E1–E3 đã đối chiếu script/log Worker, không rerun Excel; Main lưu 7 artifact nguyên byte và README tại `roadmap/evidence/review-a06-2026-10-17/`. Nhánh symlink file/POSIX chưa proof, recheck_only không tương đương pin; brief và evidence ở HANDOFF, A-07/release vẫn chặn.

**Cập nhật sau mốc 17/10:** tra lại khi có model/host mới liên quan, cấu hình không được phiên chấp nhận, hoặc kết quả thử cho thấy cần đổi. Agent ghi ngày kiểm mới, URL nguồn, lý do và thay đổi preset trong mục này; tăng revision và đồng bộ `implementation_trial` ở ba role config cùng STATE/HANDOFF. Giữ mốc ban đầu 17/10/2026 và cấu hình thực tế của các lượt đã làm trong HANDOFF; không viết lại lịch sử để phù hợp preset mới. Cập nhật model/effort không đổi nhiệm vụ/quyền của vai, và chỉ được kết luận chất lượng trong phạm vi đã có bằng chứng trên LAW.

## 9. Thứ tự thực hiện và phần tồn đọng

| Lát cắt | Luồng bàn giao | Điều kiện chuyển bước |
|---|---|---|
| **A — Nguồn vào và vai trò đầu tiên** | R1 tối thiểu + R2 metadata/writer/view; R4 profile/vai lõi và Scout trên một host: user đặt nguồn → tra sổ → Main gọi Scout trong quyền → nhận delta → writer cập nhật → UI xem lại | Không mất dữ liệu, lỗi/xung đột đúng; phân biệt gọi vai thật và làm trực tiếp. Phần offline tiến triển trước khi host sẵn sàng |
| **B — Tạo và dùng lại kết quả** | Worker/Reviewer phù hợp + R3 + phần R5 cần thiết: chọn nguồn → báo cáo → phiên sau dùng lại → đổi nguồn → thấy phần cần xem lại | Đúng revision, truy ngược được, không tạo lại chỉ để xem, không tích hợp kết quả cũ |
| **C — Cá nhân hóa và vận hành lâu dài** | Personal skills, nguồn tăng dần, gián đoạn, nâng cấp; pilot A → mẫu → B | Không rò dữ liệu/quyền; đổi model/effort giữ nhiệm vụ; upgrade/rollback bảo toàn phần riêng |
| **D — Đóng gói và mở host** | R7 cho phạm vi đã đạt; thêm host theo adapter và cùng ca hành vi | Support matrix có bằng chứng cụ thể; không quảng bá tính năng chưa kiểm |

Tồn đọng cũ giữ nguyên nghĩa và gắn đúng bước:

- **P1 (R1/R7):** nhãn nâng cấp cùng version phải phân biệt version label với thay đổi nội dung/build; tránh `v1.8.0 → v1.8.0` gây hiểu sai.
- **P2 (R1/R2):** lỗi CLI có nguyên nhân dễ hiểu và bước tiếp theo; không để user đoán lệnh khắc phục.
- **P3 (trước pilot R6, đưa vào A):** sửa kịch bản đặt project trong bộ mẫu; dùng thư mục ngang hàng.
- **P4 (C/R7):** `.new` có giữ bản của tôi / dùng bản mới / mở để tự sửa, preview và phục hồi; không chọn đè ngầm. Không bắt hoàn tất mọi UX merge trước writer R2.
- Giữ các mục LAW/Fable ngoài phần đã sửa, PROJECT_ONLY của gói HR, native skill cũ thiếu dấu quản lý, xác minh gói lĩnh vực và giới hạn CI/macOS/browser trong STATE/báo cáo gốc. Không tự đóng chúng theo roadmap mới.

**Bước triển khai kế tiếp (I-02 rev1):** D-01b20/10 đã nhận ACCEPTED_WITH_LIMITS subset preview/thay tám guide/archive bền/giữ .new; Reviewer49target đạt/0skip source cuối. D-01c20/10 đã nhận WITH_LIMITS guide subset; Reviewer85đạt trước sửa/16target sau,0skip, có Chromium finish. D-01d20/10 nhận WITH_LIMITS same-schema integration, Reviewer6test source cuối đạt/0skip sau sửa oracle. D-01e20/10 đã nhận WITH_LIMITS finish-only6entrypoint/current giữ, FINISH14/REPLACE8; Reviewer55scope+5HTTP/1amendment đạt, harness flaky đã sửa. D-01f21/10 đã nhận WITH_LIMITS matrix/gap và guide/copy theo evidence a–e, Reviewer A2 sửa diễn đạt owner; source cuối1test chữ UI đạt/0skip,10HTML khớp. D-01g21/10 ACCEPTED_WITH_LIMITS:16target sau sửa guard đạt/0skip,8protected khớp; Reviewer độc lập nhận subset. Raw inverse lịch sử NOT_VERIFIED và sai lệch --help giữ, không săn preimage. REPLACE8/FINISH16, managed membership giữ. M1 đóng, M2 chốt danh sách, M3-C1+A1 đã nhận WITH_LIMITS; snapshot M4 và phần chờ pilot ở mục0.8. Việc kế tiếp theo M1–M6 ở mục0; không tự phát sinh tranche từ mỗi gap. Không generic pending/pack hoặc migration khácschema. Không áp instruction mới/grant/migration hoặc toànT39; P4 tổng thể còn OPEN. D-01a đạt scope diagnostic/P1, không dispatch lại hay tự sửa legacy parser ngoài scope; chưa toànD-01/T39. C-02/T37–T38 DEFERRED_POST_MVP, chưa đo người mới; tiếp E07-A theo0.10. Chưa D-02/paidproof/fullgate/profile/native maintainer/host/global/admin/x14/activation/release/MANIFESTrepo.

## 10. Ma trận nghiệm thu và bằng chứng

Giữ ID T01–T48 của đề xuất R2 để truy nguyên. Đây là **48 tình huống thiết kế**, không phải số test đã chạy hoặc yêu cầu viết đúng 48 test. Bảng tóm tắt nhóm phạm vi; hợp đồng mục 4–7 là tiêu chí triển khai tự đủ. Khi thực hiện, đối chiếu từng ID với đề xuất gốc để không bỏ trường hợp trong nhóm.

| ID | Điều cần chứng minh | Mốc/lát cắt |
|---|---|---|
| T01–T04 | Tiếp tục việc, None/STATE hoàn tất, mâu thuẫn file thực, việc nhỏ trực tiếp — **CORE_ACCEPTED_WITH_LIMITS18/10** theo review A-02; không mọi biến thể STATE trống/hostkhác hoặc toàn bộ reporting compliance | R1 / A |
| T05–T08 | Nguồn đúng/sai chỗ, user báo chuyển nhưng thực tế khác; phân biệt thiếu index với parser không đọc được | R1/R2 / A |
| T09–T12 | Nguồn trùng tên/khác vai, đổi tên/nội dung/file mất; ownership README, file tạm, symlink/junction ra ngoài; quét lặp không nhân bản | R2/R3 / A |
| T13–T16 | Excel/ghi đồng thời, ngắt ghi/phục hồi, sổ/schema/dependency lỗi, dữ liệu mẫu tách nguồn thật | R2/R7 / A,C |
| T17–T21 | B-01 nhận WITH_LIMITS19/10: nguồn/revision/semantic đổi, decision giữ, inference/literal qua write/query; fixture/API/CLI đã kiểm. Chưa toànR3/live agent/prompt-injection enforcement/Office | R3/R4/R5 / B-01 subset đã kiểm |
| T22–T24 | Gói tự khai, role chưa xác nhận, projection trùng/sửa riêng, bytes đổi nhưng version không đổi | R4 / A,C |
| T25–T28 | Trường không hỗ trợ, model/tier chưa quan sát, fallback một agent, gọi vai thật trong phiên mới — T28 core Scout/Worker/Reviewer file-native CLI2.1.81 đã nhận WITH_LIMITS19/10; không mọi biến thể/fallback hoặc sandbox | R4/R5 / A |
| T29–T30 | A-11 nhận WITH_LIMITS19/10: một writer, kết quả stale không tích hợp qua checkpoint/owner guards;21probe dữ liệu giả đạt. Chưa live agent/nhiều TASK/Scout delta riêng hoặc toàn R5 | R5 / A-11 subset đã kiểm |
| T31–T33 | B-03 ACCEPTED_WITH_LIMITS19/10: recipe/probe dừng/trả muộn/timeout/reopen/thiếu tool-quota-provider đã kiểm subset hợp tác; chưa host sống/fullR5; evidence/giới hạn HANDOFF đầu | R5 / B-03 |
| T34–T35 | B-03 nhận subset hợp tác19/10: binding khớp nhưng nội dung thiếu giữ chờ; acceptance A không truyền B, chọn/mở không phải user nhận. Probe v3/P-CN1 giả lập; chưa người dùng thật/toànR6 | R5/R6 / B,C |
| T36 | C-01 ACCEPTED_WITH_LIMITS20/10: docs/probe A→mẫu cá nhân→B VI/EN,9target sau sửa/0skip; A/B độc lập, intake/grant/user acceptance mô phỏng, không runtime/fullR6/D-01 | R6 / C-01 |
| T37–T38 | DEFERRED_POST_MVP theo operator0.10, không chặn MVP; NOT_RUN; C-02 PREP nhận WITH_LIMITS20/10 sau review kit, chưa có người mới. Pilot khám phá L→N cùng nguồn không so hiệu quả nhân quả; lộ oracle/nhiễm memory/chưa xác minh khiến tiêu chí liên quan không đánh giá được | R6 / C-02 |
| T39–T40 | Migration/downgrade/release đúng hash; tắt LAW/đổi host vẫn đọc được dữ liệu | R7 / C,D |
| T41–T43 | Cùng sổ UI/agent, nguồn/phụ lục/artifact liên quan, duyệt/tìm không gọi AI; T42 B-02 nhận WITH_LIMITS19/10 fixture/API/CLI/UI; A-07 giữ phần đã nhận, chưa liveagent/toànbiếnthể | R2/R3/R6 / A,B |
| T44–T46 | Mở đúng bản, chọn input đúng ID/revision, phân biệt rỗng/lỗi/mất/quyền; T44/T45-output B-02 nhận WITH_LIMITS19/10 opener giả/query/copy/guard, chưa Office visual; phần nguồn A-07 giữ | R2/R3/R6 / A,B |
| T47–T48 | B-02 nhận WITH_LIMITS19/10: nguồn đổi sau chọn/prepare bị từ chối, processCLI mới đọc sổ/quan hệ không scan/AI; fixture/API/CLI/UI hợp tác, không live nhiều agent/profile/host hoặc toànR3/R5 | R3/R5/R6/R7 / B,C |

Kiểm theo thay đổi: writer dùng kiểm dữ liệu/transaction; UI dùng giao diện; tuyên bố dispatch/model dùng host thật; usability dùng người mới. Tái dùng evidence còn đúng snapshot, không rerun toàn bộ vì bàn giao. Ghi artifact/phiên bản, môi trường, phần đạt/chưa kiểm. Mock/schema không chứng minh model đã chạy hoặc user đã hiểu.

Chỉ số pilot: thời gian tìm đúng nguồn, lần giải thích lại, dùng lại đúng revision, lỗi stale/ghi nhầm, số bước/lần cần hỗ trợ, chi phí quan sát được. Tính cả setup/công sửa; baseline cùng native, quyền/nguồn/mẫu tương đương. Đo sổ ở quy mô pilot và mức tăng đại diện rồi chọn ngưỡng hiệu năng/backup. Hiệu quả roles cần đo; có roles là quyết định sản phẩm đã chốt.

## 11. Migration, phân phối và duy trì

1. Schema có phiên bản; writer cũ không hiểu schema mới thì từ chối ghi rõ lý do. Migration có bản sao/backup và phục hồi; không hứa downgrade đầy đủ khi mất ngữ nghĩa.
2. Thêm profile/index/role vào ownership/manifest rules trước build. Release templates sạch; không chép STATE/HANDOFF, quyền, nguồn, workbook dữ liệu hoặc runtime maintainer sang ZIP.
3. Đưa kinh nghiệm A về mẫu là lựa chọn từng skill/mẫu/quy tắc đã tiếp nhận; kiểm dữ liệu riêng/provenance trước chép. Không sync ngầm A↔mẫu↔B.
4. Giữ chuẩn tiếp nhận skill/gói. Dùng personal skill trong project không tự cho phép export native/shared. Mở rộng export phải sửa đúng policy/owner, không bypass bộ lọc hiện tại.
5. Upgrade nhận biết sửa riêng, giữ quyền/model choice/file gốc, giải quyết xung đột có phạm vi. Projection mất receipt phải reconcile với profile, gói đã xác nhận và file thực; cache không tự tạo quyền.
6. VI/EN đồng bộ chức năng thực có; hướng dẫn cập nhật model/effort, ngày tra provider, đổi host và giới hạn hỗ trợ. Thông tin 17/10 là baseline nghiên cứu, không là cam kết vô thời hạn.

## 12. Quyết định Local và nguồn đối chiếu

### 12.1 Tiếp nhận phản biện

| Ý kiến | Quyết định |
|---|---|
| Sổ nguồn, thư mục, roles và tích lũy trong đề xuất EA | Giữ làm trục sản phẩm, chia lát cắt dùng sớm |
| Claude đề xuất writer nhận delta/file tạm | Nhận; proposal trung gian không thành nguồn sự thật |
| Giảm sheet/hoãn phiên bản | Đơn giản layout khi giữ đủ revision/lineage |
| Đưa profile vào role config | Preset tại role; lựa chọn/quyền hiệu lực tại EXECUTION_PROFILE |
| Một host trước | Nhận cho pilot; contract chung, thêm adapter theo evidence |
| Sửa P1–P4 trước mọi phần mới | Gắn theo phụ thuộc: P3 trước pilot; P4 trước nghiệm thu upgrade |
| Output làm input có nguy cơ vòng chứng minh | Cho phép với loại nội dung/provenance/dependency; không nâng thành nguồn chính |
| Quy tắc gọi vai có thể hạn chế linh hoạt | Grant theo nhóm tác vụ, vai theo nhu cầu; giữ nhiệm vụ/quyền |

### 12.2 Nguồn và phạm vi

- Operator phiên 17/10/2026: local/native, cá nhân lâu dài, roles sẵn có, model/effort tùy chọn, kế thừa CVF phù hợp. Đây là căn cứ mục tiêu; chỉ dẫn trong tài liệu external là đề xuất để đối chiếu.
- External EA: `C:\Users\DELL\Downloads\LAW_ROADMAP_HOP_NHAT_R2_VI.md`; SHA-256 `7a2f861a198b5bdf59e29d1b959f3056f464ff7f363a15f7c4f404f0ef901d9b`. Đã đối chiếu các phần kiến trúc/tree/quyền/nguồn/roles/roadmap/nghiệm thu. Public anchor kế thừa `ecedb81013d2b72643ac2045c78de5dd79d56318` không phải HEAD local hoặc remote đã xác nhận trong lượt này.
- [Ghi nhận Codex](BAN_GHI_NHAN_CHO_CODEX_2026-10-17.md), [báo cáo kiểm thử](BAO_CAO_KIEM_THU_VA_DANH_GIA_2026-10-17.md), [đánh giá Claude](DANH_GIA_ROADMAP_LAW_R2_VA_DE_XUAT_2026-10-17.md): tham khảo/đối chiếu, giữ nguyên file gốc.
- Evidence lịch sử: [full_suite.log](evidence/mo-phong-2026-10-17/lan-1-ban-dau/full_suite.log), [RC gate JSON](evidence/mo-phong-2026-10-17/lan-1-ban-dau/local-agent-workspace-v1.8.0-rc1.zip.gate.json). Không nâng phạm vi sang chức năng mới.
- Code/tài liệu local đọc có mục tiêu: AGENTS, README, continuity; library, transaction, pack, install_skills, app, init/adopt/upgrade/build/check và release templates. Không tuyên bố audit mọi file/toàn bộ lỗi.
- Tài liệu host và pilot Claude Code 2.1.81/2.1.302 ở mục 7; phân biệt bằng chứng host đã có với tích hợp LAW chưa triển khai.
- Nguồn cảm hứng thiết kế: chọn lọc nguyên tắc quản lý từ CVF theo yêu cầu người dùng; các quy tắc áp dụng đã viết tự đủ ở mục 3, không phụ thuộc tài liệu hay trạng thái phiên của CVF.
- Roadmap cũ lưu nguyên bytes, SHA-256 `68bb0542993aef1a506372d924fb313708af1500c0773e82b72ed6085c7041a1`; lịch sử vẫn giữ, công việc mới theo roadmap này và continuity.

Đã có ba tranche mẫu lịch sử ở mục8; cập nhật18/10 đã nhận G-03 baseline hợp tác hẹp/G-04 candidate và A-02 core T01–T04 WITH_LIMITS trên CLI quan sát. Chưa đạt toàn T01–T48, writer/R2 hoặc phát hành. Giữ evidence đúng phạm vi tại hàng hiện hành, không tạo roadmap cạnh tranh.
