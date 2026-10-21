# Workorder C-02 — Chuẩn bị pilot người mới, chưa chạy pilot

Ngày giao: 20/10/2026. Trạng thái: READY_FOR_CLAUDE_PREPARATION. Operator xác nhận: **chưa có người mới; chuẩn bị bộ pilot trước**. T37–T38 chưa được thực hiện hoặc nghiệm thu.

## Mục tiêu và phân vai

Claude chuẩn bị bộ pilot; Codex điều phối/review, operator chọn model/effort Claude. Theo roadmap8.4 có thể bắt đầu Sonnet5.5 High; ghi cấu hình thực quan sát được, không suy effort. Không gọi agent phụ/provider/AI CLI/API hoặc người tham gia trong lượt này.

Đầu ra phải đủ cụ thể để sau này quan sát người mới dùng hướng dẫn/UI thật, làm việc → mở lại phiên → dùng lại kết quả/cách làm; so với native cùng điều kiện nghiệp vụ và ghi cả setup/công sửa/can thiệp. Chuẩn bị không chứng minh usability hoặc LAW tốt hơn native. Không agent đóng vai người mới, không tạo số đo hay USER_ACCEPTED thay người.

## Căn cứ và giới hạn đã audit

- Đọc AGENTS, STATE, đầu HANDOFF, roadmap C-02/T37–T38, P3, chỉ số pilot mục10 và quy tắc8.3–8.4. A-02/B-03/C-01 đã nhận trong phạm vi giới hạn; không chạy lại tranche cũ để chuẩn bị pilot.
- Entry point người dùng hiện có: README, START_HERE, hướng dẫn tạo project/sử dụng hằng ngày/kỹ năng. Project phải ngang hàng với mẫu, không nằm bên trong mẫu. Không sửa hướng dẫn sản phẩm trong workorder này.
- Nguồn giả dùng lại: `examples/demo-project/notes/meeting_notes.txt`, `docs/procedure_v1.md`, `docs/procedure_v2.md` dưới cùng demo-project. Đọc đầy đủ nguồn khi lập đáp án quan sát; không đưa CSV mơ hồ, Office hoặc căn cứ pháp lý thật vào pilot đầu để tránh mở thêm biến số.
- `feedback/README.md`, `feedback/TEMPLATE.md` giữ quy tắc lưu feedback; `docs/FEEDBACK_FORM_VI_EN.md` là phiếu cảm nhận sẵn có, không thay log hành vi. Không ghi bản thử/điền INDEX feedback khi chưa có lần thử thật.
- Candidate hiện là source dirty, chưa official release. Pilot tương lai phải ghi đúng artifact/snapshot giao, app/model/effort quan sát, OS/dependency; version label không đủ. Không refresh MANIFEST repo, build release hoặc giả Git sạch để chuẩn bị. Có thể dùng materialize trong thư mục tạm để kiểm kỹ thuật, phải gọi đúng là fixture/dry-run.

Snapshot nguồn giả tại audit (raw SHA-256; nếu đổi thì đối chiếu lại oracle, không khôi phục nguồn theo bảng):

| File dưới `examples/demo-project/` | SHA-256 |
|---|---|
| `notes/meeting_notes.txt` | `b88d37364f57dba0b661060e7a9f196a7d6ad3b2511cdfd591cc40842384cc58` |
| `docs/procedure_v1.md` | `90b4429f6a582df32274b092c5ee4f50a8e245b512eadd6522cc4888efb2a169` |
| `docs/procedure_v2.md` | `b57ff1782b4deded41886f487c96016f312526a634a6142957631b46f1023101` |

## File được tạo/sửa

Tạo đúng ba file trong `feedback/pilots/c02/` (vùng maintainer, không vào package):

1. `NGUOI_THU.md`: phiếu giao mục tiêu bằng tiếng Việt dễ hiểu cho người mới; không đáp án, không prompt AI soạn sẵn hay lệnh kỹ thuật để vượt gate.
2. `DIEU_PHOI.md`: chuẩn bị môi trường, kịch bản/đáp án quan sát, thiết kế so sánh, điều kiện bắt đầu/dừng và cách chấm. Tách khỏi phiếu người thử để không lộ đáp án.
3. `PHIEU_GHI_NHAN.md`: biểu mẫu trống cho từng lượt, có thể điền về sau; không giả participant, thời gian, chi phí, kết quả hoặc chấp nhận.

Cập nhật STATE/HANDOFF để bàn giao. Không sửa runtime/UI, schema/pins, roles/profile/native, product docs/HTML, demo sources thật, release_templates, VERSION/MANIFEST/README hoặc feedback INDEX/records. Không tạo thêm báo cáo, dashboard, schema, script/harness/fixture lâu dài, test file hay bản ghi thử đã điền. HEAD tham chiếu b13e375d; nhận worktree dirty, không reset/stash/clean/stage/commit/push/release.

## Nội dung bộ pilot cần có

**Người thử:** chưa có; trường danh tính dùng mã ẩn danh khi thực sự tuyển được, không tự gán người hoặc thu dữ liệu cá nhân. Nêu điều kiện chưa từng dùng LAW và mức quen app/native do họ tự khai. Host/account/model, thời lượng/chi phí được phép, người quan sát và lịch chạy đều **cần xác nhận trước khi chạy**, không điền mặc định thành quyết định của operator.

**Bài thử:** chọn số bước vừa đủ cho ba mốc, dùng dữ liệu giả đang có:

- Bắt đầu từ mẫu sạch/hướng dẫn/UI thật, tìm nguồn đúng và tạo bản nháp hữu ích. Tiêu chí nguồn: ghi chú họp phân biệt quyết định, việc đã giao và đề nghị chưa có người/hạn; không biến người đã báo việc thành người được giao theo dõi. Đối chiếu quy trình phải phân biệt đổi nghĩa với diễn đạt lại và gắn nhãn suy luận. Đáp án chi tiết chỉ ở tài liệu điều phối, đối chiếu đúng file nguồn.
- Đóng phiên/mở phiên mới, tìm lại đúng bản và nguồn mà không làm lại chỉ để xem. Có một thay đổi nguồn giả có kiểm soát trong **bản sao pilot** để kiểm nhận biết bản cần xem lại và chọn đúng revision. Người điều phối phải chuẩn bị nội dung trước/sau, thứ tự đưa vào và oracle rõ ràng; không sửa nguồn repo hoặc dùng kết quả của người thử làm đáp án.
- Dùng lại cách làm đã chọn cho việc/project B với nguồn của B, không mang dữ liệu/quyền/STATE/output acceptance A. Với LAW dùng hướng dẫn C-01 hiện có; với native giữ cùng mục tiêu nghiệp vụ và tài nguyên đầu vào tương đương, để người thử dùng cách bình thường của họ. Không ép baseline làm thao tác riêng của LAW chỉ để so số click.

Mỗi mốc cần: điều người thử được nhận, kết quả quan sát được, nguồn oracle, điều được/chưa được kết luận và bằng chứng cần giữ. Nếu một mốc không làm được trong môi trường thì ghi chưa đánh giá, không tự loại khỏi acceptance hoặc sửa sản phẩm trong lượt chuẩn bị.

**Không viết prompt hộ:** người thử tự diễn đạt yêu cầu cho AI. Phiếu chỉ giao việc/kết quả mong muốn; không có block “dán vào AI”, walkthrough theo nút/lệnh hay JSON/grant/trust anchor. Người thử có thể tự đọc tài liệu được cung cấp cho nhánh đó; nếu tự tìm ví dụ/prompt trong hướng dẫn thì ghi việc đã tham khảo, phân biệt với người điều phối đưa prompt. Người quan sát không chạm thay bàn phím hoặc sửa prompt; nếu đã trợ giúp thì lưu nguyên văn nội dung trợ giúp và đánh dấu kết quả có hỗ trợ, không gọi độc lập hoàn thành.

**So native công bằng:** cùng host/account/model/effort nếu khả dụng, nguồn/phiên bản, mẫu nghiệp vụ, quyền và mục tiêu tương đương; LAW là phần can thiệp, native vẫn dùng khả năng/skill bình thường thực sự có, không tắt file tools hoặc cố làm yếu baseline. Tách thư mục và phiên để không dùng kết quả arm trước. Ghi thứ tự thử, thời gian làm quen và hiệu ứng học; nếu có nhiều người thì đề xuất đổi thứ tự trước khi chạy. Một người hoặc một thứ tự không chứng minh quan hệ nhân quả/tính phổ quát; môi trường không tương đương thì không tính chênh lệch như hiệu quả do LAW. Không benchmark trả phí trong tranche này.

**Ghi nhận:** phân biệt thời gian setup, tìm nguồn, thực hiện, sửa và gián đoạn; số lần giải thích lại/trợ giúp, bước cần hỗ trợ, dùng đúng revision, lỗi stale/ghi nhầm và artifact thật. Chi phí chỉ theo công cụ/billing/telemetry quan sát được, ghi nguồn/đơn vị/phạm vi; không có số thì “chưa đo”, không coi là 0 hoặc suy token thành tiền. Tiêu chí phân loại: hoàn thành độc lập / hoàn thành có hỗ trợ / chưa hoàn thành / không đánh giá được, gắn từng bằng chứng. Không tự đặt ngưỡng đạt/thời hạn/giới hạn tiền như thể đã được user chốt.

**Gate trước chạy:** có người mới thực, xác nhận môi trường/giới hạn, artifact và nguồn đã freeze/hash, thư mục pilot tách biệt, oracle và thứ tự thử đã chốt, người quan sát biết cách ghi hỗ trợ; không có thì trạng thái NOT_RUN, không phát sinh chi phí/gửi lời mời/chạy host. File profile hoặc receipt không chứng minh host nhận vai; không bắt người dùng viết schema để khắc phục. Chặn môi trường phải có cách báo bằng ngôn ngữ người dùng và phần chưa kiểm.

**Bằng chứng/riêng tư:** dùng đường dẫn artifact và log tối thiểu đã che, giữ yêu cầu người thử và khai báo thực hiện của agent theo feedback hiện có; không ghi key/account hoặc danh tính không cần thiết, không tự bật quay màn hình/gửi dữ liệu. Không liên hệ người thử hoặc gửi feedback ra ngoài khi chưa được yêu cầu. Ý kiến cảm nhận, kết quả công cụ, quan sát hành vi và chấp nhận của người dùng là các loại bằng chứng riêng.

## Acceptance của lượt chuẩn bị

- Ba file phân vai rõ: phiếu người thử không chứa đáp án/prompt soạn hộ; hướng dẫn điều phối có oracle đối chiếu nguồn, hai nhánh công bằng, tiếp tục phiên và reuse; phiếu ghi nhận còn trống, có mục NOT_RUN/chưa đo và provenance của số đo.
- Mọi nguồn/link local trỏ tới file có thật; số, ngày, tên hoặc thay đổi dùng trong oracle phải đối chiếu nguồn. Thay đổi giả chỉ là kế hoạch trên bản sao, ghi rõ không phải dữ kiện nguồn hiện có. Không đưa số liệu/cảm nhận từ fixture C-01 hoặc test kỹ thuật thành kết quả pilot.
- Chưa có người thử: không tạo feedback record, không log thời gian/chi phí/kết quả giả, không kết luận T37/T38 đạt hay C-02/R6 hoàn tất. Ghi đủ các trường cần xác nhận trước chạy, không dừng việc chuẩn bị để hỏi lại điều user đã chốt.
- Worker tự soát một lượt các tên/link/oracle, tính nhất quán giữa ba file và quyền/giới hạn; có thể dry-run chỉ thao tác file bằng owner hiện có trong thư mục tạm nếu có nghi vấn cụ thể. Dry-run không gọi AI/provider, không đóng vai novice, không được chấm là pilot. Không chạy fullsuite/browser/Office/release gate hoặc viết test chỉ soi câu chữ tài liệu.
- Kiểm `git diff --check` và `python -B tools/check_package.py --check-eol <đúng file chạm> --result-json`. File mới LF theo .gitattributes; giữ EOL các file hiện có, không normalize cây.
- Bàn giao **IMPLEMENTED_PENDING_REVIEW — PREPARATION_ONLY, PILOT_NOT_RUN**: file/hash, cấu hình thực, phần đã đối chiếu/chưa kiểm, lệnh thực chạy, câu hỏi còn chờ trước pilot. STATE đúng8heading/khoảng60dòng. Worker không đổi verdict roadmap hoặc tự viết kế hoạch triển khai D-01.

Orchestrator review bộ chuẩn bị rồi mới chốt readiness cho lần thử thực. D-01/fullR6/activation/release, native benchmark, đo hiệu năng sổ quy mô lớn và nghiệm thu người dùng vẫn ngoài phạm vi lượt này; x14 PARKED.
