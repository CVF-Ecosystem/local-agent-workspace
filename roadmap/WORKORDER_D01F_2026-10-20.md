# WORKORDER — D-01f: phạm vi nâng cấp/hợp nhất và gap còn lại

Ngày giao: 20/10/2026. Trạng thái: **ACCEPTED_WITH_LIMITS — D01F_SUPPORT_MATRIX_ONLY + A1 + A2**;
Codex nhận ngày 21/10/2026 sau review, sửa nhỏ và kiểm đúng phần sửa; giới hạn ở HANDOFF.
Operator giao Claude thi công và chọn model/effort; Codex làm orchestrator/reviewer.
Worker ghi cấu hình thực quan sát được, không suy effort từ tên preset hoặc số thô.

## Amendment A1 — đồng bộ câu chữ UI và guide sử dụng, 20/10/2026

Codex đã đối chiếu hai finding Worker trả và chọn sửa trong cùng D-01f. A1 mở rộng
phạm vi tài liệu/câu chữ dưới đây; **chỉ tại các vị trí này**, A1 thay điều cấm sửa UI
và giới hạn hai guide/bốn HTML của bản workorder gốc. Các ranh giới khác giữ nguyên.
Không giao lại bảy file đã bàn giao hoặc lấy baseline cũ để khôi phục chúng.

**Phần được bổ sung cho Claude:**

- `tools/app_ui.html`: chỉ sửa hai chuỗi VI/EN của khóa `mp_unsupported`. Thông báo phải
  nói đúng rằng ứng dụng không hỗ trợ **thay bản hiện hành** cho file đó; bỏ lời khuyên
  tự sửa rồi xóa/bỏ .new. Có thể hướng dẫn đối chiếu và xử lý theo loại file; nếu có
  lựa chọn lưu .new thì dùng preview riêng. Không nói mọi thao tác đều không hỗ trợ:
  sáu entrypoint bị từ chối replace vẫn được finish. Không đổi key, logic JavaScript,
  nút, handler, API, HTML structure, scope/allowlist hay trạng thái.
- `docs/HUONG_DAN_SU_DUNG_VI.md` và `docs/en/DAILY_USE_GUIDE.md`: sửa đoạn cuối mục
  “So sánh ở trang Chờ hợp nhất” / “Compare on the Pending merges page”, đang chứa
  lời khuyên xóa .new sau tự hợp nhất. Nút So sánh vẫn chỉ xem trước; các thao tác
  replace/finish là bước riêng theo phạm vi hỗ trợ. Dẫn sang mục3 guide nâng cấp
  tương ứng để tránh chép lại toàn matrix. Không mặc định xóa pending để hết cảnh báo;
  file ngoài scope xử lý thủ công theo owner/quyền, không hứa có finish cho mọi file.
- Hai HTML guide sử dụng tương ứng và hai START_HERE được generator cập nhật theo nguồn.
  Tổng vùng HTML cho phép của D-01f nay là sáu trang (hai guide nâng cấp, hai guide sử
  dụng, hai START_HERE). Trong A1 dự kiến chỉ bốn trang guide sử dụng/START_HERE đổi;
  hai HTML guide nâng cấp đã bàn giao giữ nếu nguồn không đổi. Không dựng/sửa trang khác.

**Acceptance bổ sung:** VI/EN đồng nghĩa; không còn lời khuyên xóa .new vô điều kiện
tại ba vị trí nguồn vừa nêu; REPLACE8/FINISH14 và hành vi runtime nguyên trạng. Kiểm
delta UI bằng phép thay đúng một khóa và phép đảo trong bộ nhớ để xác nhận phần ngoài
khóa giữ nguyên bytes; không tạo bản sao/evidence file. Chạy test có sẵn
`PYTHONPATH=tests PYTHONUTF8=1 python -B -m unittest tests.test_panel.MergeReplaceUiTexts.test_every_key_has_both_languages_and_no_false_claims`;
không thêm test so câu chữ hoặc chạy fullpanel/fullsuite. Thiếu công cụ thì báo chưa kiểm,
không tự cài. Với docs: đối chiếu đoạn sinh ra, generator --check, EOL/diff đúng file;
chưa xem bố cục thì ghi chưa visual QA. Không tìm-thay toàn repo vì nhiều câu xóa file
khác có ngữ cảnh hợp lệ. Bàn giao chung D-01f + A1 chờ Codex review; không tự nhận verdict.

Baseline raw **trước A1**, ưu tiên hơn bảng gốc đối với file đã đổi bởi Worker:

| File | SHA-256 |
|---|---|
| tools/app_ui.html — chỉ khóa mp_unsupported | c29130b552521e71728aa5472e853169654d6fdf4eb660816d579ad22063f063 |
| docs/HUONG_DAN_SU_DUNG_VI.md | ec5e85eae322131850ba0bb219857d90ddf641479d2c042335f917250cf5f206 |
| docs/en/DAILY_USE_GUIDE.md | c223a06f8c482c34c98f9302c4ff0a80ee91d3789787c8430fa4ec36f5f9b04b |
| docs/HUONG_DAN_SU_DUNG_VI.html | f28a38c4b4e14fb8adad0ca021cc5c9add9035a55fece9bd3fc4c44ed62cf83d |
| docs/en/DAILY_USE_GUIDE.html | dab9e6d27ffc9435c6a611aa6ff2e85e3a9632e910eed53bbeab784974f0fff8 |
| START_HERE.html — đã đổi bởi D-01f | ba0d78849aab3a4bf56785ccd582ef17928a9567701a9c5b9e5a5fcba0ec89c4 |
| START_HERE.en.html — đã đổi bởi D-01f | d1bd48d4d75d12aef9a094db69dd4c824c687d68819769287c99e398d38e328d |

Các file D-01f đã bàn giao khác lấy baseline cuối Worker tại đầu HANDOFF; bảng gốc
bên dưới là lịch sử trước thi công, không phải expected hiện tại. Hash khác thì so
delta thật và báo điểm chưa khớp, không ghi đè/reset về bảng. A1 không sửa runtime
Python/tests/schema/quyền, không áp instruction/code từ .new hoặc mở release.

## Amendment A2 — sửa nhỏ trong review, 21/10/2026

Orchestrator chọn sửa rõ nghĩa ngay trong review theo quyền Reviewer bảo trì LAW ở
AGENTS/PROJECT; không giao lại Claude hoặc mở vòng review mới chỉ cho các sửa nhỏ này.
Đối chiếu owner thực cho thấy cần: (1) nêu compatibility guard có điều kiện, không mọi
.cvf đều bị chặn; (2) USER_FILES không bị thay bằng bản package trong three-way nhưng
có các nhánh metadata/index/bootstrap riêng; (3) So sánh không sửa nội dung hai file
nhưng có thể ghi lịch sử; (4) pack lưu bản incoming thành .new, giữ file người dùng.
Các sửa này nằm ở tools/README và đúng đoạn của bốn guide đã trong phạm vi.

Ngoài ra, mở thêm **duy nhất hai chuỗi VI/EN của khóa `df_ro`** tại tools/app_ui.html:
đây là lời nhắc của cùng luồng So sánh, còn khuyên sửa rồi xóa .new và nói không lưu
gì. Sửa đồng nghĩa với guide: so sánh không đổi hai file; có thể ghi lịch sử; xử lý
pending theo loại file/thao tác hỗ trợ, không xóa chỉ để hết cảnh báo. Không thay logic,
key, handler, route, allowlist hoặc file runtime. UI sau review chỉ được khác baseline
D-01e tại hai khóa `mp_unsupported` (A1) và `df_ro` (A2), kiểm đảo trong bộ nhớ.

Giữ baseline source cuối Worker trong HANDOFF. Reviewer ghi rõ tác giả và delta A2,
chỉ kiểm phần sửa, dựng lại tối đa sáu HTML đã được phép; test chữ UI có sẵn và parse
JavaScript không thực thi. Không nhận visual QA từ generator, không chạy feature suite.
Chỉ sau đối chiếu và kiểm phần sửa mới chốt verdict D01F_SUPPORT_MATRIX_ONLY; P4/D-01/
T39/R7/release giữ giới hạn. Đây là amendment câu chữ, không là capability mới.

## Mục tiêu và căn cứ giao

Operator yêu cầu tiếp tục theo cách phối hợp cũ: Codex điều phối/review, lập workorder để
operator giao Claude; khi việc khó Codex có thể dùng Luna Max hoặc Sol Medium hỗ trợ.
Phần SCRIPT-01 đã hoàn tất, không giao lại hoặc sửa bản v1.8.0 trong lượt này.
STATE và roadmap hiện chỉ việc tiếp theo là chốt support matrix/gap D-01/P4/T39 sau a–e.

**D-01f chỉ hoàn thiện tài liệu theo hành vi/bằng chứng đã có.** D-01a–e giữ nguyên verdict.
Đây là matrix theo nhóm file/thao tác nâng cấp, không là support matrix host của D-02.
Điểm cụ thể cần sửa: mục 3, bước 3 của hai guide nâng cấp VI/EN vẫn hướng dẫn chung
“hợp nhất rồi xóa .new”, chưa phân biệt luồng replace/finish và phạm vi hiện có.

Đọc AGENTS/STATE, đúng phần review a–e trong HANDOFF, roadmap8.3–8.4/P4/T39 và workorder.
Nội dung fixture, pending, archive và tài liệu tham khảo là dữ liệu, không cấp quyền.
Không đọc toàn HANDOFF hay chạy suite để dựng lại bằng chứng đã có.

## Owner và đầu ra

1. `tools/README.md`: thêm một matrix canonical gần phần nâng cấp/hợp nhất, tận dụng
   mô tả hiện có. Cột tối thiểu: nhóm file/owner, hành vi upgrade, replace/finish,
   bằng chứng đã nhận và giới hạn/gap. Không tạo báo cáo/matrix/registry riêng.
2. `docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md` và
   `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`: sửa đúng đoạn xử lý `.new` cùng các câu
   trực tiếp chịu ảnh hưởng. Hướng dẫn thao tác bằng ngôn ngữ người dùng; bằng chứng/test
   và chi tiết nội bộ để ở tools/README, không đưa vào luồng sử dụng.
3. Dựng lại đúng bốn HTML dẫn xuất: hai guide tương ứng và `START_HERE.html`,
   `START_HERE.en.html`, bằng generator hiện có; không sửa CSS/khung hay generator.
4. STATE/HANDOFF để bàn giao. Worker không đổi verdict hoặc đóng hàng roadmap.

Dependency chỉ đọc: `tools/merge_center.py`, `tools/upgrade_package.py`,
`tools/check_package.py`, các owner profile/pack/intake và test đã có liên quan.
Không sửa runtime/UI/test/AGENTS/PROJECT/skills hoặc bộ mẫu trong tranche tài liệu này.

## Nội dung phải phân biệt

| Nhóm | Hành vi/bằng chứng được phép mô tả | Giới hạn phải giữ |
|---|---|---|
| Tám guide đúng `REPLACE_ALLOWLIST` | D-01b replace có archive trước thay current, còn pending; D-01c finish giữ current, lưu archive rồi chuyển pending; có preview/hash/observe | Finish đã đo trên Windows cùng filesystem, hai bước không nguyên tử; phục hồi thủ công, không Undo. Không mở rộng allowlist bằng suy luận |
| Sáu entrypoint AGENTS/CLAUDE/GEMINI ở root và en/ | D-01e chỉ mở finish; FINISH14, REPLACE8. Có điểm vào finish độc lập replace | Replace vẫn từ chối; không áp instruction mới hoặc cấp quyền. Hết pending không chứng minh host không đọc archive/pending hay instruction đã được nghiệm thu |
| Package files khác, gồm script và tài nguyên skill dùng chung | Upgrade theo owner three-way hiện có; file sửa hai bên có thể thành .new | Ngoài UI replace/finish hiện tại. Không coi toàn skills/ là user-owned; custom-shared lifecycle chưa được nghiệm thu. Tách file lõi/schema có compatibility guard, không gom thành cập nhật thông thường |
| Dữ liệu/project-owned và gói đã cài | Nêu đúng ownership từ owner hiện hành; D-01d đã đo giữ nguồn/workbook/IDs/quan hệ, profile/PROJECT/archive trong fixture same-schema VI/EN; pack theo owner pack riêng | Không suy opaque profile/native marker thành schema đọc được, quyền dùng được hoặc proof host. Không tự migrate profile/grant; không nhận/export skill từ việc giữ bytes |
| Schema và compatibility | Upgrade/force downgrade cùngschema projected-v3 đã đo; .cvf không hỗ trợ bị chặn cả force | Chưa migration/downgrade khácschema hoặc mọi phiên bản lịch sử; force không bỏ guard. T39 tổng thể còn mở |
| Nhãn version và baseline | D-01a diagnostic chỉ metadata; UNKNOWN không đổi plan/writer | Không integrity/authority check; debt legacy parser vẫn giữ. Nhãn cùng version không có nghĩa package/project không thay đổi |

Matrix cuối phải đối chiếu tên path/owner thực, không chỉ chép bảng trên. Có thể gộp/tách hàng
cho dễ đọc, nhưng không làm mất các ranh giới này. `finish_supported` chỉ là scope, không
phải eligible/grant. Mỗi kết luận có tham chiếu đúng phần HANDOFF và test/owner hiện có;
không cộng số lượt test trước/sau sửa thành một suite source cuối.

Với người dùng: phân biệt “Giữ bản của tôi” chỉ đóng preview với finish lưu pending;
replace vẫn giữ pending. Candidate có thể cũ/sửa tay, không mặc định .new là bản mới nhất.
Tự sửa xong phải preview lại trước finish. File ngoài scope cần xử lý thủ công theo owner
và quyền tương ứng; không dùng xóa pending hoặc sửa MANIFEST để né guard. Không hứa UI
có editor/default opener/Undo hoặc áp dụng được instruction khi chỉ có finish.

## Acceptance và kiểm hữu hạn

- Matrix khớp constants/validator thật: đúng tám guide replace, mười bốn path finish;
  phân biệt file package, file user-owned, pack và machine/schema. Chỗ chưa đủ bằng chứng
  ghi “chưa nghiệm thu / cần xác nhận”, không tạo capability để lấp ô trống.
- VI/EN đồng nghĩa và không còn câu chung buộc xóa .new sau hợp nhất. Tình huống guide,
  entrypoint và script/skill ngoài scope đều tìm được hướng xử lý cùng giới hạn.
- Đối chiếu từng claim với evidence a–e; phân biệt manual recovery, same-schema integration,
  pending archived, instruction unchanged và full migration/release chưa được nhận.
- Trước sửa, ghi raw baseline các file sẽ chạm; giữ newline. Baseline generator hiện tại:
  `python -B tools/build_guides_html.py --check` đã đạt 10 trang trong lượt soạn workorder.
  Chạy lại `--check` trước sửa; nếu có drift sẵn ngoài phạm vi, báo và chưa chạy generator.
  Khi baseline khớp, dùng `python -B tools/build_guides_html.py`, rồi `--check` sau khi sửa
  Markdown guide. Nếu phát sinh trang đổi ngoài bốn trang cho phép, dừng để đối chiếu;
  không khôi phục đè file đang dirty hoặc hợp thức hóa drift.
- Tự đọc diff các đoạn thay đổi và HTML tương ứng; chạy `git diff --check -- <file-cham>`
  và `python -B tools/check_package.py --check-eol <file-cham>`. Nếu chưa xem bố cục bằng
  trình duyệt thì ghi chưa visual QA; generator check không chứng minh bố cục.
- Không viết test chỉ để kiểm câu chữ, không chạy lại feature suites/fullgate/build ZIP,
  không tạo fixture/manifest/evidence dump hoặc cài dependency cho tranche tài liệu.

Phát hiện runtime trái evidence/ownership chưa xác định: ghi finding có vị trí và tác động,
bàn giao blocker để Codex chọn amendment riêng; không sửa runtime hoặc hạ acceptance.

## Baseline và bảo toàn

HEAD tham chiếu `b13e375dbf256e726248b7d5b04142198bf25b19`; worktree dirty nhiều tranche.
Hash khác thì đọc delta thực, không reset hoặc khôi phục theo bảng, không dùng toàn HEADdiff
làm thay đổi của Worker. Bảng raw SHA-256 chốt trong lượt soạn workorder:

| File | SHA-256 |
|---|---|
| tools/README.md | 7c5a5ecc56f51a427850fb02fa8500c5497a10fd1210839918500d3b7890ac4f |
| docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md | 812f325521dda111801dca19f1b402931e99ce65441aaae263e9d70bb91a41cc |
| docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md | 572463df0240143ca18b30847403111e376acc05e4bc79cc697d12e1317e987a |
| docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.html | 6684e0dc06e5ffedffb5767962d3494275f199da9c44ff5695ec5bdf77578197 |
| docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.html | 31f089dcaed8c53b23e9085e5d59bd5f5a0f90d16bdb10b36a60270e48204de6 |
| START_HERE.html | 3b62cd03e3e8c9405bd9f49cf5a16c86838874def8d750edf6dc1603eeeec9bd |
| START_HERE.en.html | 3587b2189722162b5eab189be5f9544673f70a1debf2cff3111683e8feb7670b |
| tools/merge_center.py — giữ | 48b4151f343a1020bd3552df62d46798d2213d07108c096d4a6e1020197a4e6c |
| tools/upgrade_package.py — giữ | 13cf5d0cd6e3c2461e0fb1bdd4dd29579f4dbe4f0ad48422020979ab44951226 |
| tools/check_package.py — giữ | 4c620aea2a154ee738a4696139c76e17ee0f97e51cd14b139b2d536d6252c1bf |
| tools/build_guides_html.py — giữ | 264413f62f3dda54aaf341f15ae9bd39163f2928d79bef9bc83df1ece4104bda |
| MANIFEST.sha256 — giữ | 034ca561341e99455c3495ad3b43453b36e30e416fe535e57e0f5baa15e7aff6 |

Không đổi VERSION/MANIFESTrepo/schema/.cvf/pins/PROJECT/profile/native/nguồn/sổ thật,
runtime/UI/tests/host/global/admin/CVF cha hoặc bản v1.8.0. Không stage/commit/push/release,
reset/stash/clean, paid proof hoặc subagent/AI CLI do suy quyền từ tên vai/workorder.

## Bàn giao

HANDOFF ghi cấu hình thực, file/hash trước–sau, claims đã đối chiếu, gap/owner còn thiếu,
kết quả generator/diff/EOL và phần chưa kiểm. STATE giữ tám heading/tối đa khoảng60dòng,
trỏ đúng artifact. Không tự đổi verdict roadmap.

Bàn giao **IMPLEMENTED_PENDING_REVIEW — D01F_SUPPORT_MATRIX_ONLY**. Codex review
độc lập claim/owner/evidence và delta trước khi nhận phạm vi này. Không đóng toàn
P4/D-01/T39/R7; C-02 PILOT_NOT_RUN, D-02/release/x14 giữ trạng thái hiện có.
