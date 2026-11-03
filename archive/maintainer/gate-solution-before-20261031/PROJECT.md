# NGỮ CẢNH DỰ ÁN VÀ HƯỚNG DẪN LÀM VIỆC

File này giữ ngữ cảnh ổn định của project. Quy tắc vận hành chung nằm trong `AGENTS.md`.

## Thông tin dự án

Chỉ điền điều hữu ích và ổn định. Tiến độ hiện tại thuộc về STATE.

- Tên dự án: [Tên]
- Mục đích và người đọc: [Công việc này để làm gì; ai sẽ dùng]
- Đầu ra mong đợi: [Tài liệu, quy trình, biểu mẫu, báo cáo, khác]
- Ngôn ngữ và văn phong: [Ví dụ: tiếng Việt; dùng mẫu hiện có của đơn vị]
- Nguồn / mẫu đã duyệt chính: [Đường dẫn hoặc mục trong index nguồn]
- Ràng buộc quan trọng: [Ràng buộc nghiệp vụ đã xác nhận hoặc giới hạn xử lý dữ liệu]
- Mức nhạy cảm dữ liệu: [Công khai / Nội bộ / Có dữ liệu cá nhân hoặc mật; nêu cách xử lý]
- Kiểm host theo operator 27/10/2026: Main chuẩn bị thông số, prompt đầy đủ và vị trí file phản hồi riêng cho Claude Desktop/Codex Desktop/Antigravity; operator làm trung gian chuyển thủ công. Giai đoạn đầu thu readiness/tool/model/path trước khi chốt cấu hình/quyền và prompt roles thực. Việc user relay bên ngoài không là bằng chứng Main tự chia/ghép Worker–Reviewer. Bộ hiện hành ở working/academic-research/host-acceptance-20261027/; không chạy host hoặc đổi profile/grant chỉ vì đã có bộ prompt.
- Chuẩn nghiệm thu operator chốt 27/10/2026: prerelease phải tích hợp và sử dụng tốt theo chuẩn kỹ thuật/nghiệp vụ có sẵn; hoàn thiện đường dùng trong project gốc, roles trên host công bố, chất lượng cơ bản, sửa/tiếp phiên, bảo toàn và artifact/hướng dẫn trước khi giao user. Feedback người dùng là bước cuối để đánh giá độ phù hợp và chỉnh tiếp, không chặn việc chuẩn bị chuẩn hoặc làm lý do để lại lỗi tích hợp/chất lượng cơ bản. Danh sách đóng hữu hạn và ma trận host tại mục "Hoàn thiện prerelease và nghiệm thu" của roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md revision 4; không tạo tranche riêng theo mỗi test/host. Chỉ định này về đích sản phẩm/thứ tự nghiệm thu, không tự cấp quyền sửa profile/grant của project khác hoặc phát hành.
- Chỉ định operator ngày 27/10/2026 (ưu tiên khi điều phối bảo trì LAW): Codex là orchestrator; được gọi subagent Luna Max (`gpt-6-luna`, effort `max`) mặc định, dùng Sol Medium (`gpt-6.1-sol`, effort `medium`) khi việc khó. Bám roadmap và mốc sản phẩm đã chốt; trước mỗi lần giao đối chiếu toàn bộ điều kiện nghiệm thu, bằng chứng, phần lần giao đóng và phần còn lại. Mỗi tranche có mốc nghiệm thu rõ; giữ sửa nhỏ/kiểm bổ sung trong tranche hiện hành, chỉ tách khi phạm vi/owner hoặc rủi ro thực sự thay đổi và ghi lý do. Xong tranche hoặc test không tự là đạt mốc sản phẩm. Quyền này thuộc điều phối bảo trì kho nguồn, không tự thay profile/grant của sản phẩm hay project khác.
- Chỉ định operator ngày 23/10/2026 (ưu tiên hơn preset cũ bên dưới): Codex làm orchestrator/reviewer; được gọi subagent Luna effort Max mặc định, Sol effort Medium khi việc khó. Cập nhật operator mới nhất23/10: Codex tự thi công, điều phối/review và xử lý roadmap, không giao Claude nữa; quyền gọi reviewer Luna Max/Sol Medium khi cần vẫn giữ. Dùng dữ liệu giả lập (datamock) cho Prototype/MVP; chỉ thu thập feedback từ người dùng thật sau khi hoàn tất Prototype/MVP. Được sử dụng API key Alibaba hiện có khi cần live test trong phạm vi công việc; không chép key vào hồ sơ. Chỉ định này không tự biến dữ liệu giả thành bằng chứng vận hành hoặc usability thật.
- Vai trò khi phát triển LAW: Agent điều phối phiên bảo trì là **Orchestrator xây dựng LAW**, được operator giao audit, chọn phương án phù hợp, chốt thiết kế/amendment trong phạm vi phát triển đã giao, chia tranche, gọi Reviewer và nhận kết quả; không phải vai **Main vận hành trong sản phẩm LAW**. Các chỗ gọi "Main" trong quyền bảo trì/hồ sơ thi công được hiểu là Orchestrator phát triển. Không lấy quy tắc cấm Main sản phẩm tự cấp quyền/hạ gate làm lý do hỏi lại quyết định phát triển đã được giao; thay đổi sản phẩm vẫn phải được version, review và nghiệm thu đúng phạm vi trước khi có hiệu lực. Cách phối hợp hiện tại theo chỉ định mới nhất23/10: Codex trực tiếp thi công/tích hợp roadmap, không dispatch Claude; chủ động gọi Reviewer độc lập đúng quyền đã cấp và xử lý kết quả. Quyền này chỉ thuộc kho nguồn LAW, không chuyển vào release_templates hay project người dùng; giữ giới hạn không stage/commit/push, không sửa CVF cha hoặc host/global/admin. Ngoại lệ operator cấp mới nhất23/10/2026: được tạo nhánh/checkout riêng, stage và commit cục bộ đúng allowlist41file đã Reviewer nhận trong HANDOFF để tiếpV7, kiểm/fullgate trên clean commit; giữ main/index/workspace gốc, chưa cho push/tag/phát hành. Ngoại lệ tiếp theo operator xác nhận trong hội thoại23/10/2026: được push đúng commit9dc1763f6a2e0a692cbd7c36883b22dbfa46e749/41file đã review lên nhánh mới codex/office-prototype-source của origin CVF-Ecosystem/local-agent-workspace và chạy đúng một workflow_dispatch CI ci.yml trên nhánh đó (5job); operator đã được nêu payload gồm roadmap có2đường dẫn máy và chi phí lịch sử. Không cấp quyền merge/main/tag/phát hành hoặc rerun tự động. Ngoại lệ operator XÁC NHẬN tiếp theo23/10/2026: được tạo childcommit của9dc1763 với đúng5file/hash ci_fix_trace_proposal trong HANDOFF/observation (workflow, native_agents/library_sync/work_status/ui_browser tests), push fast-forward cùng nhánh codex/office-prototype-source và đúng1CI workflow_dispatch mới gồm5job để kiểm2sửa nhỏ/thu trace2UNKNOWN. Giữ main/index gốc; không force/merge/tag/release hoặc rerun tự động. Ngoại lệ operator xác nhận24/10/2026 ("xec nhan" trả lời proposal cụ thể): được tạo tag v1.9.0-rc4 tại đúng2552d7d79558ad360a886239e73df1122122dbcc và công bố prerelease Windows DATAMOCK đúng3asset ZIP/gate/checksum đãreview trong rc4_release_proposal; prerelease=true/latest=false. Được tạo draft, upload/kiểm3asset, publish và tải lại đối chiếu; giữ stable/latest1.8.0, RC1/RC2, main/index; không force/retag/clobber/merge/extraCI. Quyền dùng API key Alibaba cho live test khi cần tiếp tục có hiệu lực; không lưu key trong hồ sơ.
- Phạm vi được giao cho agent phụ: Xem .agent/EXECUTION_PROFILE.json (quyền gọi vai do profile giữ; chưa có grant thì chưa có quyền)
- Ngoại lệ thư mục nguồn cũ: [Không có / thư mục trong project, nhiều thư mục ngăn bằng dấu ; ví dụ: Tai-lieu-cu; Ho-so-2023]

- **Bổ sung quyền workspace — chỉ định tiếp theo 28/10/2026:** Operator yêu cầu đồng bộ ý kiến Claude sang WORKSPACE_RULES.md và public clone .Controlled-Vibe-Framework-CVF trong CVF-Workspace như lượt trước: được bổ sung đúng contract/hướng dẫn/template và nội dung sinh rules; giữ WIP khác. Chỉ định này mở lại phạm vi workspace/public clone đã tạm dừng ở rev158. Kho gốc TOOL AI 2026/Controlled-Vibe-Framework-CVF vẫn hoãn; không cho publish/updater/rollout sibling hoặc đổi runtime/grant. HANDOFF rev159 giữ scope, evidence và toàn gap mốc sản phẩm.

- **Điều chỉnh phạm vi rev158 28/10/2026:** Operator giao bổ sung ý kiến Claude vào chuẩn LAW đã làm; riêng nâng CVF nền để xử lý sau. Lượt tiếp này chỉ sửa LAW, không sửa thêm kho CVF gốc, public clone hoặc workspace-root rules. Quyền mở rộng CVF trong quyết định trước bên dưới được tạm dừng cho tới chỉ định mới; không rollback patch cũ, không coi patch public là upstream đã nhận. Academic vẫn PAUSED, các quyền Git/publish/profile không thay đổi.

- **Quyết định phát triển 28/10/2026:** Operator giao đồng bộ toàn LAW và CVF gốc: đội agents dev chịu roadmap theo mốc sản phẩm, chuẩn đầu ra, tự chuẩn bị test/expected có căn cứ, review và nghiệm thu bản dùng được trước feedback. Noncoder không là technical QA bắt buộc; chỉ cung cấp mục tiêu, quyết định nghiệp vụ/quyền cần thiết và phản hồi mức phù hợp. Chuẩn áp dụng cả core/packages/skills/templates. Được sửa canonical CVF và đường kế thừa/root workspace rules đúng phạm vi này; ngoại lệ mới này ưu tiên hơn giới hạn cũ không sửa CVF cha. Không cấp quyền Git/publish, triển khai hàng loạt project, runtime grant hoặc promote package. Academic vẫn tạm ngừng. Hướng dẫn và kết quả source phải review, không tự coi là enforcement hay nghiệm thu sản phẩm.

- Chỉ định operator29/10/2026: được stage/commit local để lưu checkpoint và làm sạch Git worktree LAW/publicclone CVF; WIP Gateway ghi commit riêng, không nhận chất lượng. Không push/tag/release/nâng CVF gốc. Profile và dữ liệu làm việc giữ local theo .git/info/exclude, không sửa grant/B7 hoặc promote gói học thuật đang PAUSED.

- **Tiếp nhận LAW sau CVF — chỉ định29/10/2026:** operator giao hoàn tất LAW C6/carrier adoption và kiểm bản đóng gói/fullsuite để tiếp roadmap. CVF acceptance source và workspace inheritance đã COMPLETE_BOUNDED (public15e3945, operator-local4043caf14); các ghi chú hoãn28/10 phía trên là lịch sử và không còn là trạng thái của learning đã nhận. LAW dùng chuẩn local tự đủ tại skills/README.md, không yêu cầu CVF sibling cho người nhận. Chỉ sửa tài liệu/hướng dẫn và kiểm trong lượt này, không runtime/schema/grant hoặc nâng trạng thái gói; academic PAUSED. Toàn gap V4/V6/V7 chưa đủ vẫn mở, không tự nhận prerelease/release hay cấp quyền push.

- Chỉ định operator30/10/2026: Codex làm orchestrator/reviewer, được tạo subagent Worker Terra 6.1 High (`gpt-6.1-terra`, `high`), việc khó dùng Sol Medium (`gpt-6.1-sol`, `medium`) để tiếp roadmap. Ưu tiên chỉ định này hơn preset Worker cũ; chỉ trong bảo trì LAW, không đổi grant/profile sản phẩm hoặc quyền Git/publish.

## Mục đích của workspace

Đây là workspace dựa trên file cho công việc văn phòng và vận hành: đọc tài liệu, viết quy
trình và biểu mẫu, phân tích bảng tính, thỉnh thoảng làm báo cáo HTML. Project cục bộ giữ hồ
sơ làm việc giữa các agent và các phiên. Điều này không có nghĩa mô hình xử lý offline hay file
tự đồng bộ.

## Mặc định hữu ích

Hiểu yêu cầu, dùng ngữ cảnh liên quan, giao kết quả được yêu cầu rồi dừng. Chọn cách làm theo
phán đoán. Hướng dẫn trong `AGENTS.md` dùng chung cho mọi provider và bổ sung, không thay thế,
khả năng native sẵn có. Giới hạn chống lặp vòng nằm trong mục "Giới hạn công việc" của `AGENTS.md`.

Không có chế độ làm việc bắt buộc. Chỉ hỏi điều còn thiếu và ảnh hưởng đến kết quả.

## Nguồn và đầu ra

Bắt đầu từ nguồn người dùng nêu. Cần thêm ngữ cảnh thì dùng index hoặc đọc phần liên quan của
nguồn khác. Dùng lại thông tin đã có khi phù hợp; đọc lại một đoạn nếu nó có thể đã đổi hoặc
kết luận phụ thuộc vào nó.

Dùng mẫu của người dùng khi phù hợp. Ví dụ đi kèm skill chỉ là điểm xuất phát, không phải chính
sách nghiệp vụ đã duyệt. Tách rõ dữ kiện từ nguồn với đề xuất.

Với việc rà soát nội dung, bản nháp trong hội thoại có thể đủ. Khi người dùng yêu cầu file, tạo
file bằng công cụ phù hợp và kiểm tra những điểm cần để dùng. Bản đang làm để trong `working/`,
bản giao hiện hành trong `output/`, bản cũ trong `archive/` khi cần giữ. Đường dẫn sẵn có của
dự án vẫn có thể giữ nguyên. Giữ nguyên nguồn gốc; không tạo thêm bản hay đầu ra khi chưa có lý do.

## Liên tục giữa các phiên

STATE là bản chụp hiện trạng: mục tiêu, đầu ra hiện tại, quyết định đã chốt, việc còn mở và bước
hữu ích tiếp theo. Ghi đè, giữ tối đa khoảng 60 dòng. Ghi điểm kiểm khi phiên sau sẽ bỏ lỡ một thay đổi có ý nghĩa.

HANDOFF giúp phiên khác tiếp tục với đúng file và bước tiếp theo; tùy chọn và thường chứa `None`.
PENDING_LESSONS cũng tùy chọn: chỉ ghi điều đáng dùng lại. Mẹo hoặc ví dụ ổn định có thể thành
skill khi người dùng đồng ý, không tự động sau một lỗi.

## Skills

Index skill là công cụ để tìm, không phải bộ định tuyến cố định hay danh sách phải nạp mỗi phiên.
Chọn theo độ phù hợp, gồm cả lựa chọn làm trực tiếp hoặc dùng khả năng native. Skill quen thuộc
không cần liệt kê lại mỗi lần dùng.

Người dùng quản lý việc thêm, bỏ và viết lại lớn thư viện. `skills/inbox/` vẫn là tùy chọn. Khả năng
riêng của provider có thể ghi chú khi hữu ích, nhưng không sao chép hay giả định có ở provider khác.

## Hoàn thành

Kết quả xong khi đáp ứng đúng phạm vi và định dạng yêu cầu với độ chính xác và khả năng dùng cần
thiết. Một vấn đề cụ thể là lý do để xem lại phần liên quan; còn dư sức hay có thể trau chuốt thêm
thì không phải lý do.

- **Chỉ định operator31/10/2026 — upstream learning kiểm soát tiến độ:** đã cho chuyển bài học tại LAW lên CVF nền, mở lại đúng phạm vi canonical của learning31/10 thay quyết định hoãn cũ. Đã cập nhật contract milestone, learning cùngfamily/README và hash registry trong kho CVF gốc; receipt tại archive/maintainer/cvf-learning-upstream-20261031/UPSTREAM_RECEIPT.json. Không tự cấp quyền commit/push/publicsync/rollout project/runtime/grant; M6/TypeSafe/academic và toàn gap sản phẩm giữ nguyên. Mục tiêu vẫn hoàn thiện roadmap, không mở thêm tranche thử learning.
