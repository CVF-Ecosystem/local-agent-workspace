# Phản biện đề nghị siết quy trình — Codex, 28/10/2026

**Trạng thái: TRAO ĐỔI — chưa giao thi công quy trình.** Cùng V7/V4; không tạo tranche, gate hoặc quyền mới.
Phản hồi [đề nghị Claude](DE_NGHI_PHAN_BIEN_SIET_QUY_TRINH_CLAUDE_2026-10-28.md).
Main là bên đã xây dựng nhiều lớp và đã gây thiếu sót B1/B3/B4; phản hồi này không tự được coi là trung lập.
Reviewer Sol Medium ở ngữ cảnh mới nhận câu hỏi và số liệu thô, audit source trước draft; chưa đọc nguyên bản đề nghị/phản hồi Claude trước hoặc trong review. Sau đó Reviewer kiểm claim của Main trong draft, nên phần đó không còn mù với cách Main diễn giải L1–L3/G1–G5.

## Kết luận đề xuất

- **L1 — đồng ý một phần:** chuỗi đổi pin có chi phí lan truyền thật; HANDOFF quá lớn và hướng dẫn bị lặp.
  Chưa đủ bằng chứng để kết luận tổng chi phí đã vượt tổng lợi ích. LOC, số test và số file không đo thời gian bảo trì hay tổn thất tránh được.
- **L2 — bác cách nói tuyệt đối, đồng ý khoảng trống cốt lõi:** đã có review nội dung học thuật, ca cài lỗi và so sánh có/không skill.
  Chưa có bằng chứng về một bộ gold pháp lý/học thuật được duyệt, tái chạy ổn định và chứng minh chất lượng trước prerelease.
  Chưa tìm thấy bộ kiểm tự động quote–file hoặc tự xác minh hiệu lực pháp luật trong các tool/test được rà; không suy điều đó từ tên module đơn thuần.
- **L3 — đồng ý về kết quả B3:** kiểm cấu trúc và review trước đã để lọt việc mất kiến thức nghề. Đây là thiếu cả kiểm nội dung lẫn chất lượng review,
  không phải chỉ thiếu thêm một test. Không có phép đo thời gian để khẳng định phần lớn công sức toàn dự án đi vào hàng rào.
- **G5 chưa chứng minh:** không có bảng bằng chứng đủ để nói mọi lớp hiện hành đều tương xứng. Nhưng chưa thấy sự cố cũng không chứng minh một bảo vệ là thừa.

Đề xuất ưu tiên: giữ bảo vệ dữ liệu/quyền, giảm thông tin và thao tác lặp ở owner hiện có, dùng các acceptance chất lượng V4/AC đã có để đo nội dung.
Không chữa tình trạng nhiều quy trình bằng một engine, registry hoặc chuỗi nghiệm thu mới.

## 0. Hai quyết định B1/B4 và trạng thái sản phẩm

**B4 đã đóng về phục hồi bytes.** Main trực tiếp tính lại:
[archive bản gốc rev0](archive/ROADMAP_DONG_BO_BO_MAU_AN_C2_2026-10-28_BAN_GOC_rev0.md)
có 30.294 byte, 282 LF, 0 CRLF, SHA-256
`d6857f1148cc8fc8329db6297f5307519bea3312da111be092ae64771fbd2194`.
Hash trùng [phản biện gốc](PHAN_BIEN_ROADMAP_AN_C2_2026-10-28.md), dòng 11–14, và phản hồi Claude dòng 12.
Nhận định rev147 của tôi rằng chưa có bytes đối chiếu đã hết hiệu lực. Không thêm header hay sửa archive.
Quyết định nhắc rev139 là mốc cũ; roadmap hiện hành đã qua rev147, không thay nó bằng rev0.

**B1(a) đã được operator xác nhận; cần phân biệt kết quả với cách sinh.**

| Điều kiện quyết định | Bằng chứng thực tế | Trạng thái |
|---|---|---|
| Sinh theo cách đã dùng khi nhận v3 | Lượt sửa tính digest bằng `canon.digest_of(canon.policy_part(policy))`, đối chiếu hàm tham chiếu; refresh đúng JSON paths và giữ serialization/EOL. Có dùng `pn.build_task` để kiểm fixture projection, không dùng để sinh 22 example. Không dùng `cj_dumps` để ghi toàn bộ vector/example. | Đã theo pattern refresh dẫn xuất được hồ sơ 18/10 mô tả; **chưa chứng minh đã chạy lại nguyên generator hoặc sinh lại toàn bộ fixture theo generator cũ**. Không gọi yêu cầu này hoàn tất nguyên văn. |
| Script so JSON chỉ đổi policy digest | 23 JSON/43 digest leaves; chỉ `policy_digest.digest` của vector và `records[i].binding.policy_digest` của example. Đảo digest mới về cũ cho bytes bằng HEAD; expected/reasons/thứ tự khóa/EOL giữ. Worker chunks `eb2e39`, `36bb19`; Reviewer kiểm độc lập cùng kết quả. | ĐẠT trong phạm vi này. |
| Full suite và review độc lập | Main `unittest discover`: 1.674 test/1.095,719s, 1 failure B7, 0 error, 6 skip; Reviewer độc lập nhận delta B1. Không có lỗi B1 còn lại. | ĐẠT có giới hạn; **suite vẫn FAILED**, không allgreen. |

README lịch sử `working/v7-internal/source-integration/roadmap/evidence/g02-c2-2026-10-18/a0-narrow/README.md:26`
ghi generator tạm đã bị bỏ khỏi kho. README `pcn1-workflow:58` ghi pattern refresh digest/vector/22 example/test pins từ file thật,
không hạ assertion. Không được đánh đồng hai ghi nhận này với việc đã chạy một executable generator lịch sử còn nguyên.
Worker đã xác nhận lại thuật toán thực tế chỉ từ log lượt cũ; không ghi hoặc chạy lại test trong lần giải trình này.
**Đề xuất làm rõ:** chấp nhận phương pháp refresh bằng owner/reference và proof không đổi nghĩa theo pattern đã nhận, hoặc phục dựng generator tái lập nếu operator vẫn yêu cầu.
Đây là đề xuất diễn giải acceptance, **chưa thay điều kiện operator**; B1 còn giới hạn phương pháp nêu trên, không cần đổi ngược code đúng để che giới hạn.

Log Main: `working/an-c2-repair-20261028/fullsuite-final.log`, SHA-256
`522ff6294c155f2e2260e2cc9c2fdee0d1e25bf70bf169e2dac409384581da86`.
B7 là `test_execution_profile.Delivery.test_selection_ownership_and_bytes_without_a_source_profile`: profile thật trong source, không bị xóa/skip.
Sáu skip gồm năm ca file-symlink thiếu quyền và một non-Windows refusal không áp dụng; không phải sáu ca nội dung đã đạt.

**Toàn mốc:** V7 còn source cleanliness B7, exact artifact/MANIFEST/full gates, provenance/license và support matrix.
V4 còn license F1, guidance F5/F6, quyết định ID F3, chất lượng/intake, host/revise/error/reopen/lifecycle và đồng bộ bản cài đúng quyền.
Academic nguồn 25 file lệch installed một description; không tự sync. B3 đã phục hồi, taxonomy đủ năm loại lót pháo chưa có nguồn liệt kê.
Codex fresh context chưa nhận, Cowork scope không đạt đã đóng, Antigravity chưa phát; user feedback vẫn cuối sau chuẩn nội bộ.
B4 khôi phục bytes và phản biện này không đóng V7/V4: **PRERELEASE_NOT_READY**.

## 1. Nguồn gốc từng lớp: có yêu cầu, có test và có sự cố là ba loại bằng chứng khác nhau

| Lớp | Nguồn/ngày và mục đích có thể truy | Đã chặn/tái hiện được gì; giới hạn |
|---|---|---|
| Pin bytes và `-text` | Contract v3 P-CN1/P-CTX1 và lịch sử corrective 18/10; `.gitattributes` giữ bytes owner để checksum không đổi do EOL. Contract §P-CTX1 nói rõ không pin cả dependency. | Có lỗi EOL/pin và corrective trong hồ sơ, có regression phát hiện owner đổi. Chưa có bằng chứng nhờ pin đã ngăn một tiến trình độc hại hay thiệt hại thật của người dùng. |
| Digest policy | `G02_C2_S3_D0_AMENDMENT_PACKET_2026-10-18.md:68`; `canon.py:policy_part`; contract v3: policy là toàn object, đổi policy làm binding cũ không còn khớp. | Phát hiện binding cũ với revision mới, gồm B1 vừa qua. Đây là kiểm nhất quán version; không xác minh policy đúng ý user hoặc process thực chạy đúng owner. |
| Contract/vector/example v3 | Packet 18/10 §4–5 và `.cvf/contracts/v3/README.md`: định nghĩa shape, pha, revision/coverage và expected tình huống giả. | Corrective ghi writer tự sinh rid làm đổi task và tạo parent ngoài prefix: cần biểu diễn cùng task và parent precondition. Có tái hiện/kiểm thử trong hồ sơ; không gọi đó là tổn thất người dùng thực. Không có bằng chứng mỗi trong 22 example là một rủi ro độc lập. |
| Grant/profile | `.cvf/README.md`: G00/G01 ngày 17/10 theo yêu cầu giữ quyền user, kiểm cả Main; `execution_profile.py` phân requested/observed. | Có kiểm scope rỗng/delegation và profile migration. Profile cùng quyền sửa với Main không chứng thực consent hay cưỡng chế host; test không chứng minh chống mọi tự cấp quyền. |
| Host binding/LOCK | Kit `stage1/APPROVAL_SCOPE.md:28,53` và `stage1/scripts/README.md:21`, 27/10: nối đúng host/revision, concurrency/budget được yêu cầu, release và before-byte backups. | Cowork có checkpoint khớp binding nhưng scope vẫn NOT_MET nên không nhận host PASS. LOCK hỗ trợ điều phối/không phát tiếp; **không chặn được mọi ghi ngoài scope hoặc dừng tiến trình**. Chưa truy được sự cố đầu tiên làm phát sinh LOCK. |
| TASK/RESULT/checkpoint | `WORKORDER_V2A_2026-10-21.md`, `WORKORDER_V2B_2026-10-21.md:12,30–40`: V1-B chỉ giao candidate, thiếu RESULT/binding; tái dùng A-11 thay vì engine mới. `task_checkpoint.py` tự giới hạn bytes/binding, không content. | Tái hiện stale revision, nhầm slot, candidate thay bytes và từ chối trong tests. Lỗi thật Codex S06 TOO_LARGE cũng cho thấy giới hạn đọc sai nhu cầu có thể tạo false block; đã sửa streaming. Không có semantic verdict từ checkpoint. |
| Transaction/path boundary/expected-before | Git `2d546bb` ngày 13/10, corrective `3efecab` 15/10; roadmap A06 ngày 17/10; `transaction.py` và `test_transactions.py`. | Hồ sơ reviewer tái hiện junction `.agent` ghi ngoài project, crash/resume/rollback và giữ file user sửa sau crash. Đây là bảo vệ dữ liệu đầu ra trực tiếp, không chỉ điều phối. Fault/repro không đồng nghĩa đã quan sát mất dữ liệu sản xuất thật. |

Chưa có inventory đầy đủ chi phí/lợi ích và lịch sử mọi gate. Tôi **không chứng minh được G5** “mọi lớp đều tương xứng”.
G2 có căn cứ về provenance CVF, nhưng LAW có yêu cầu văn phòng riêng về giữ file/sổ/upgrade; nguồn gốc CVF không tự làm lớp đó sai.
G4 có bằng chứng ở giao điểm WIP/host/pin và lỗi B7, nhưng không đủ nói mọi lỗi chỉ do nhiều nhánh; B3 là lỗi làm sạch nội dung.
G1/G3 vẫn là giả thuyết về nhân quả/ưu tiên, chưa có time log hoặc truy nguyên đủ để kết luận tâm lý người xây dựng.

## 2. Phân nhóm test và đo lại số liệu

Không nhận tỷ lệ 6:1 là tỷ lệ “quy trình so với nội dung”: tên `office`, `transaction`, `library` không xác định mục đích từng assertion.
Một ca bảo toàn file có thể vừa kiểm quyền vừa bảo vệ kết quả cho người dùng; ép hai nhóm loại trừ nhau sẽ gây sai nghĩa.
`test_office_compute.py` có 45 ca, trong đó kiểm Decimal chính xác và từ chối quy đổi đơn vị thiếu căn cứ.
`test_word_output.py` có 15 ca cơ học DOCX; kiểm format có giá trị nhưng không phải đáp án pháp lý/học thuật.
`test_artifacts.py` có 72 ca, không vào hai regex được nêu, dù liên quan trực tiếp kết quả người dùng.

Main parse **log mới đã có**, không chạy lại suite: đếm dòng bắt đầu `test_` và có `(test_<module>.<...>)`, mỗi test đầu dòng một lần, bỏ traceback/summary/subtest.
Kết quả 1.674 ID đầu dòng ở 40 module, khớp tổng unittest; không dùng số dòng `... FAIL` làm mẫu số.
Áp lại regex tên module cho log mới: 893 nhóm thứ nhất, 175 nhóm thứ hai, 0 giao, 606 ngoài cả hai.
Đây chỉ là đếm **nhãn tên**, không phải phân loại ngữ nghĩa mới. Không có raw log cũ được định vị để tái lập chính xác 924/159/1.681;
không coi số mới bác số cũ vì khác revision và cách đếm subtest.

| Chỉ số | Claude ghi | Đo lại trước khi tạo phản hồi | Nhận xét |
|---|---:|---:|---|
| `.cvf` Python | 6.519 dòng/105 file | 6.519 LF/**16 file .py** | LOC khớp; 105 không phải số Python file theo recursive `*.py`. |
| `tools` Python | 18.643 | 18.688 LF/30 file | +45 sau patch; không suy chi phí từ LOC. |
| `tests` Python | 32.806 | 32.938 LF/40 file | +132 sau sửa/test mới. |
| Markdown shared + packs | 1.844 +1.587 | 1.844 +1.691 =3.535 LF | +104 ở packs; không đồng nghĩa nội dung đã đúng. |
| Markdown roles + `.cvf` | 1.248 +1.438 | 1.248 +1.438 LF | Khớp. |
| `AGENTS.md` | 270 | 270 LF | Khớp. |
| HANDOFF | 2.128.328 byte/4.965 dòng | 2.136.366 byte/4.970 LF tại rev148 | Số đo thời điểm; chính lượt tôi ghi tiếp đã làm file lớn hơn. |
| Roadmap | 43 MD/20 work order | 45 MD ở root,85 recursive;20 tên có WORKORDER | Khác thời điểm/phạm vi. Không dùng 85 để bác số root43. |
| `-text` | 11 | 11 dòng quy tắc | Khớp; không phải 11 bảo vệ độc lập. |

Đếm file/LF bằng `Path.rglob(pattern)`, bytes thô, không tính `__pycache__` vì không khớp `.py`/`.md`; số liệu là working tree, không HEAD sạch.
Chưa gắn nhãn từng assertion của toàn suite. Không cần mở một dự án phân loại 1.674 test chỉ để có tỷ lệ đẹp.
Khi sửa đúng nhóm việc, ghi rõ nó bảo vệ **nội dung / format / provenance / bảo toàn / quyền-điều phối** và bằng chứng mock/live/gold.

## 3. Kiểm nội dung hiện có và khoảng trống

| Câu hỏi | Hiện có | Chưa được chứng minh |
|---|---|---|
| (a) Quote có trong file nguồn? | Source-library yêu cầu trích từ file đã lập chỉ mục; bảng claim/locator và review thủ công học thuật. | Chưa tìm bộ so nguyên văn end-to-end. `library.ContentFlow` còn cho ghi EXTRACT theo text được cung cấp; lưu provenance không phải xác minh chuỗi đó có trong nguồn. |
| (b) Văn bản còn hiệu lực? | `library.py:391–404` cảnh báo status mâu thuẫn, thiếu/ngày kiểm cũ; event/revision giữ và đánh dấu nội dung cần review. | Không truy nguồn hiện hành tự động, không xác nhận điều khoản áp dụng/ngoại lệ. “CURRENT_CATALOG_BASIS” chỉ khớp sổ, không đồng nghĩa hiệu lực hiện tại. |
| (c) Đáp án đúng và lợi ích skill? | AC-A/A7 có fixture gài lỗi; AC-D có so sánh blind có/không skill. Hồ sơ S05/S06 tại `working/academic-research/AC_D_MVP_INTERNAL_CASE_2026-10-26.md` rubric cho thấy direct tốt hơn candidate ở hai tiêu chí. | Chưa có gold pháp lý/học thuật được duyệt và tập ngoài mẫu đủ chứng minh ổn định. Hồ sơ một ca không là nhận toàn gói. Lượt này không đọc lại PDF để xác nhận lại đáp án khoa học. |

Vì vậy L2 “không có phép kiểm nội dung nào” quá mạnh nếu tính cả đánh giá thủ công. Nếu giới hạn là **automated gold regression đáng tin**, khoảng trống là có thật.
`check_output.py:14` tự nhận là kiểm cơ học; không lấy nó hay 1.674 test làm bảo chứng nội dung nghiệp vụ.
Cả sáu pack DEFER là lựa chọn chưa nhận; nhãn này không tự chứng minh chất lượng cao hoặc thấp.
14 shared AVAILABLE cũng không thay một hồ sơ chất lượng theo chuẩn mới.

Về “vì sao chưa làm”: có bằng chứng harness `skill_regression` từng được xem xét trong HANDOFF của commit `baa26c9`, dòng100–105:
so quote theo ngưỡng40 yếu, cần negative control và không được nhận provenance/ngữ nghĩa từ lexical match. File harness không có trong tools/tests hiện hành.
Điều đó chứng minh rào cản chất lượng thiết kế từng được nêu, **không chứng minh nhân quả duy nhất là việc khó nên bị né**.
Gold approver chưa được chỉ định, phạm vi corpus/hiệu lực cần chốt, và các ca dùng sửa guidance bị nhiễm làm hạn chế phép đo ngoài mẫu.
Đây là dependency sản phẩm cần xử lý trong V4/AC hiện có, không lý do hoãn vô hạn đến user feedback.

## 4. Chi phí B1 và cách giảm lan truyền

Lượt B1 mới chạm 25 file: vector+22 example+2 file test. Bản sửa gốc `context_update.py` và policy pin có trước đó; gộp nguyên chuỗi ít nhất **27 file**, chưa tính metadata/receipt.
Không gọi 58 failures là 58 lỗi thiết kế độc lập: 57 được quy về cùng gốc dẫn xuất trong review cũ.
Các bước thực tế: sửa owner → pin → tính digest toàn policy → refresh fixtures → pin fixture → kiểm hẹp → review → full suite tích hợp.
Số bước không là số lượt host/agent bắt buộc; lần sửa này chỉ một full suite cuối sau gộp, không một suite cho mỗi owner.
Không có time log riêng từng bước để định giá công sức hoặc suy phần trăm overhead.

Có thể giảm ngay ở mức tổ chức đề xuất: một thủ tục/script dẫn xuất có thể tái lập và kiểm no-op/diff chỉ vùng cho phép, không chỉnh tay nhiều pin;
gom cùng source cuối để review/kiểm một lượt. Chưa tạo script hoặc quy tắc mới trong lần phản biện này.

Tách pin vận hành khỏi digest route có thể giảm phạm vi đổi, nhưng **không chỉ xóa field khỏi phép hash**:
phải giữ cả định danh policy và định danh implementation/dependency trong binding/receipt, phát hiện thay pin, giữ proof lịch sử và xử lý compatibility/version.
Nếu bỏ pin khỏi policy rồi không bind nơi khác, task cũ có thể đi với owner mới mà không bị phát hiện.
Contract v3 hiện cố ý hash toàn policy; hướng(b) cần thiết kế và review riêng **nếu operator chọn**, không chen vào sửa B1(a).
Không đề xuất pin AST bỏ câu help hoặc lờ EOL để làm test xanh: đó cũng là đổi mục tiêu bảo vệ.

## 5. HANDOFF hơn 2 MB: không có lý do để miễn giới hạn sử dụng

AGENTS giữ STATE tối đa khoảng60 dòng; HANDOFF là bàn giao và `None` nếu không dùng, không quy định append-only hay miễn ngắn gọn.
`context_update.py` cho STATE tám heading/60 dòng, HANDOFF không line cap, nhưng có giới hạn nội dung8MiB. Cap8MiB là giới hạn parser/write, không phải ngân sách đọc của agent.
Đọc ba dòng đầu hiện giúp tìm brief nhưng dòng thứ ba rất dài; không đảm bảo context đủ, không thay giải pháp handoff ngắn.
Chính tôi đã tiếp tục tích lịch sử trong file này, góp phần làm nó tăng; không thể đẩy hết nguyên nhân sang multi-agent hay Claude.

Đề xuất: HANDOFF chỉ giữ brief hiện hành, revision/owner, acceptance đầy đủ, evidence locator và phần cần tiếp;
chuyển lịch sử đã đóng sang archive với hash và link, giữ bytes/đường dẫn mà proof đang tham chiếu.
Chưa chọn số dòng/KiB cứng chỉ để có thêm gate. Nghiệm thu theo việc một agent mới đọc được brief hiện hành gọn, tìm đúng việc tiếp và giữ được evidence cũ;
nếu cần budget định lượng thì operator chốt sau đo trên host dùng thật.
**Lần này không dọn/chia file, sửa STATE schema hay thay policy.**

## 6. Giữ, gộp và xem xét gỡ

| Quyết định đề xuất | Phạm vi | Điều kiện không được làm mất |
|---|---|---|
| Giữ | Quyền user, path/link boundary, expected-before, transaction/recovery, source identity/revision, từ chối script chưa tin cậy. | Không ghi đè file user, không tự grant, không chấp nhận stale bytes, không tự cài/chạy nguồn. |
| Giữ theo đúng tuyến cần | TASK/RESULT/checkpoint, review độc lập cho thay đổi rủi ro, binding host khi đang kiểm host có scope/cost. | Không áp thêm vào bản nháp nhỏ đã có quyền; không coi checkpoint/LOCK là host enforcement hay content verdict. |
| Gộp | Hướng dẫn lặp về canonical owner, brief hiện hành, receipt; tách bàn giao đang làm khỏi lịch sử đã đóng. | Giữ authority gốc, acceptance và khả năng truy bằng chứng; không đổi verdict chặn thành PASS. |
| Xem xét thiết kế | Tách operational code pin khỏi route-policy digest; giảm fixture regeneration tự tay. | Cần chứng minh thay pin vẫn bị phát hiện, proof cũ không được hồi tố, lỗi/migration/version bị từ chối đúng. Chưa được chọn thay B1(a). |
| Không gỡ chỉ theo LOC/số test | Pin, grant, transaction hay review rủi ro. | Đối chiếu threat→control→owner thay thế→negative case trước khi bỏ. Chưa có mapping đủ để công bố gate nào vô dụng. |

Có bằng chứng đã từng thu hẹp cách áp quy trình: roadmap V1 ngày21/10 ghi Main suy rộng product grant/checkpoint thành acceptance V1 rồi phải sửa phân kỳ,
không tạo RESULT hồi tố; V2B chủ động không dựng engine mới. Vì thế G1 “chỉ thêm không bao giờ gỡ” cũng chưa thể khẳng định nguyên dạng.
Không mặc định chạy review cho mỗi sửa câu, mỗi lệnh/checkpoint hoặc mỗi lượt host; giữ rule10 và việc nhỏ trong tranche hiện hành.

## 7. Siết nội dung pháp lý/học thuật trong acceptance đã có

Không chốt “10–20 ca” như một gate mới. Bộ ca ban đầu cần phủ rủi ro sản phẩm; số lượng phụ thuộc nội dung và trường hợp thất bại.

| Phần đo | Có thể tự động đến đâu | Ai nhận kết quả và tiêu chí |
|---|---|---|
| Quote ↔ source revision/locator | Exact substring trên văn bản trích xuất đã kiểm; khai báo NFC/whitespace/hyphenation. Không fuzzy match rồi tuyên nguyên văn. Scan/OCR/bảng chưa chắc trả UNVERIFIED để đọc tay. | Người kiểm đối chiếu đúng file/trang; quote sai hoặc nguồn thiếu không được PASS. Chuỗi có trong file vẫn chưa chứng minh quote đủ ngữ cảnh. |
| Citation ↔ danh mục ↔ nguồn | Kiểm liên kết hai chiều, nguồn/bản/locator tồn tại, citation thiếu/thừa, nguồn đã đổi. | Reviewer nội dung kiểm nguồn thực hỗ trợ claim, không coi DOI/hash là entailment. |
| Hiệu lực pháp luật | Cờ ngày kiểm/trạng thái từ sổ và nguồn đối chiếu giúp cảnh báo; không tự biến metadata thành legal opinion. | Operator chỉ định người có chuyên môn duyệt căn cứ theo thời điểm, điều khoản sửa đổi/chuyển tiếp/ngoại lệ và phạm vi áp dụng. Chưa được chỉ định thì gold NOT_APPROVED. |
| Đáp án học thuật | Tính lại số/đơn vị, đối chiếu claim–evidence–điều kiện/model/metric, kiểm rubric lỗi có chủ đích và giữ câu đúng. | Người am hiểu lĩnh vực duyệt gold; reviewer AI hỗ trợ, không tự phong human peer review. Thiếu bằng chứng phải nêu đúng giới hạn, không thưởng đáp án tự tin mà sai. |
| Lợi ích tăng thêm và vòng đời | Cùng task/corpus/pages/tools/budget và model yêu cầu; ghi actual nếu quan sát được. Ca có/không skill chấm ẩn, có phần ngoài mẫu. Sửa rồi mở lại đúng bản và giữ nội dung đúng. | Tách độ đúng tuyệt đối khỏi việc skill có hơn cách làm trực tiếp. Ca dùng debug là regression, không đem làm bằng chứng tổng quát hóa ngoài mẫu. |

Báo số claim/quote/case đã kiểm, số critical error, false-confident pass, lỗi bỏ sót/lỗi báo nhầm và phần chưa đọc; không chỉ một điểm tổng hoặc số lần dùng.
Đề xuất chuẩn trước prerelease: không còn lỗi nội dung trọng yếu chưa xử lý trong phạm vi đã nhận; negative controls bị bắt, phần đúng giữ được;
những giới hạn host/nguồn/format và quality/intake được công bố đúng. Đây là cụ thể hóa acceptance AC/V4 đã có, không tự nhận toàn ngành từ một bộ ca nhỏ.
User feedback cuối đánh giá hợp nhu cầu và chất lượng dùng thật; không chờ feedback mới sửa lỗi kỹ thuật/nội dung đã biết.

## Phạm vi phản biện và phần chưa kiểm

Đã đối chiếu code có mục tiêu, test bodies đại diện, inventory40 module/log đã chạy, các đoạn hồ sơ gốc và hash archive.
Chưa đọc mọi assertion của1.674 test; chưa audit mọi gate hoặc tính thời gian từng việc; chưa xác minh lại PDF/nghiệp vụ/hiệu lực pháp luật.
Không chạy lại full suite, host, installer hay mạng; không sửa code/policy/skill/profile/grant/AGENTS hoặc archive gốc.
Số đo trong bảng là trước khi tạo file này và trước metadata receipt tiếp theo, không phải snapshot bất biến toàn repo.
Kết quả review độc lập bản phản hồi: **ACCEPTABLE_WITH_LIMITS**. Reviewer trực tiếp kiểm lại số đo, archive/hash B4, log/counts, hồ sơ A0/P-CN1/V2A-B/AC-D; không thấy P2 trong claim đã đối chiếu. Main sửa hai P3 trong cùng lượt: phạm vi mù của reviewer và locator AC-D đầy đủ. Không có vòng review hay test suite mới. Chưa được gọi phản biện độc lập nhà cung cấp/host; model/effort Sol Medium là cấu hình yêu cầu, backend thực chưa chứng thực. Review không cấp quyền thi công.
