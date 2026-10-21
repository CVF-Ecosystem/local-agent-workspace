# Đánh giá Roadmap LAW R2 hợp nhất và đề xuất hoàn thiện — 2026-10-17

> Bản tạm để Codex phản biện trước khi sửa. Chưa commit. Không phải roadmap mới, không thay `ROADMAP_HOAN_THIEN.md`.
> Người viết: Claude (Opus). Đầu vào: `LAW_ROADMAP_HOP_NHAT_R2_VI.md` (do operator gửi), báo cáo kiểm thử `BAO_CAO_KIEM_THU_VA_DANH_GIA_2026-10-17.md` và bằng chứng trong `roadmap/evidence/mo-phong-2026-10-17/`.

## 1. Tóm tắt

- Định hướng của roadmap đúng và nên giữ: người dùng không giỏi AI, model của host làm bộ não, các vai trò được lập sẵn như phòng ban ảo, sổ nguồn dùng lâu dài, dùng lại dữ liệu đã có mà không gọi AI.
- So với code hiện tại, khoảng cách lớn nhất nằm ở **sổ nguồn**. `tools/library.py` hiện chỉ đọc, kiểm và tìm; nó không ghi dòng, không có fingerprint, không có revision, và các cột thiên về văn bản pháp luật. Gần như toàn bộ R2–R3 là phần mới.
- Hai điều quyết định mô hình có chạy được không, nhưng roadmap chưa đặt lên trước:
  1. Host người dùng chọn có thật sự chạy mỗi vai bằng model và effort đã gán hay không.
  2. Model rẻ ghi sai thì có bị chặn trước khi vào sổ hay không.
- Nên làm theo đợt nhỏ, chạy pilot sớm trên một host, gom bớt sheet, giảm số tình huống phải làm ở đợt đầu. Các lỗi P1–P4 tìm được khi test nên sửa trước.

## 2. Hiểu đúng mô hình (để Codex và tôi cùng một nền)

- Mỗi người dùng chọn **một** host: Claude, Codex hoặc Antigravity, tùy tài khoản họ có. LAW hỗ trợ từng host riêng, không điều phối chéo giữa các host.
- Model mà người dùng mở phiên là **điều phối**. Các vai (ví dụ Scout quét nguồn, Worker làm việc, Reviewer đối chiếu, vai chuyên môn) được lập sẵn: quy tắc nghiệp vụ, đầu vào, đầu ra, model và mức effort cố định.
- Khi có yêu cầu, điều phối gọi đúng vai qua subagent native của host. Mục tiêu: việc hẹp chạy bằng model rẻ với effort cố định.
- Host không gọi được vai thì điều phối tự đóng vai đó và nói rõ là tự làm.

## 3. Căn cứ đã kiểm

| Việc | Kết quả |
|---|---|
| Bộ test của kho, Python 3.11, Windows 11 | 129/129 đạt, có 17 ca trình duyệt thật |
| Gate phát hành rc1 (`build_release.py --rc 1`) | Cả ba cổng đạt; ZIP tạm có 230 file |
| Mô phỏng ba nhiệm vụ của kịch bản nghiệm thu qua bảng điều khiển thật, dữ liệu giả | Cả ba đạt, 0 lỗi console; chạy lại bằng script đã khôi phục cho cùng kết quả |
| Đọc code để đối chiếu với roadmap | `library.py`, `pack.py`, `merge_center.py`, `upgrade_package.py`, `app.py`, `AGENTS.md` (chỉ đọc phần liên quan) |

**Chưa kiểm:**
- Agent của host nào chạy trên folder này.
- Subagent native, và việc model/effort theo vai có được áp dụng hay không.
- GitHub hiện tại: mốc `ecedb81` của roadmap không có trong clone local, vì `origin/main` local vẫn là `b887fc0`.

## 4. Đối chiếu roadmap với code hiện tại

| Mốc roadmap | Code hiện có | Khoảng cách |
|---|---|---|
| R1 — đầu phiên, quyền, thư mục | `AGENTS.md` dòng 35 dặn không biến việc đọc trạng thái thành nghi thức; dòng 104 cấm khởi chạy agent phụ khi chưa được yêu cầu | Nhỏ, nhưng phải viết lại cho nhất quán, không thêm câu vá. Phải bỏ hoặc đổi dòng 104, nếu không các vai sẽ không bao giờ được gọi. |
| R2 — quét và lập danh mục | `library.py` có `init`, `check`, `find`, `stats`. Nó chỉ đọc sheet "Danh mục" (tiêu đề ở hàng 4). Nó không ghi dòng; thông báo bảo người dùng tự thêm dòng. Các cột thiên về pháp luật: Cơ quan, Số ký hiệu, Ngày hiệu lực, Thay thế… | **Lớn.** Chưa có: writer, SourceID tự cấp, fingerprint, quét gia tăng, cột chung cho nguồn không phải pháp luật. |
| R2.7 — thư viện trên giao diện | Bảng điều khiển đã gọi `library_find`, `library_stats`, `library_check`; trang Công việc có danh sách nguồn và kết quả | Vừa. Có sẵn đường gọi, còn thiếu view dạng thẻ và lọc theo dữ liệu sổ. |
| R3 — nội dung, revision, bằng chứng | Không có | **Mới hoàn toàn.** |
| R4 — gói vai trò, gắn model | `pack.py` chỉ cho phép `pack.json`, `README.md`, `skills`, `templates`, `references`; `skills` bắt buộc không rỗng. `install_skills.py` chỉ xuất skill. | Vừa. Thêm `roles/` vào schema, cho phép gói chỉ có vai, sinh file vai cho host. Tái dùng được phần tiếp nhận (REVIEW, xác nhận, dấu vân tay nội dung). |
| R5 — điều phối, hủy, kết quả muộn | Không có, và phụ thuộc host | Mới. Phần lớn do host làm; LAW chỉ cần quy ước gắn revision và kiểm trước khi ghi. |
| R6 — trải nghiệm người mới | Bảng điều khiển đã có và qua test (bàn phím, focus, tương phản, 360/390 px). Chờ hợp nhất chỉ có `scan`, `set_state`, `diff`. | Có P4: không có nút giữ bản của tôi hay dùng bản mới. |
| R7 — phát hành | `build_release.py` có 4 cổng, ZIP tái lập được, `--verify` | Đã có nền tốt. |

## 4b. Khả năng host đã kiểm bằng tài liệu chính thức (2026-10-17)

Nguồn: trang tài liệu của từng host, tải bằng công cụ WebFetch. Công cụ này tóm tắt bằng model nhỏ, nên các câu trích có thể bị diễn đạt lại. Trước khi dùng làm căn cứ kỹ thuật cần đối chiếu nguyên văn.

| Khả năng | Claude Code | Codex | Antigravity |
|---|---|---|---|
| Vị trí file vai | `.claude/agents/` (đường dẫn này chưa xác nhận lại trong lần tải này) | `.codex/agents/*.toml`, `~/.codex/agents/` | `.agents/agents/`, `~/.gemini/config/agents/` |
| Model riêng cho từng vai | Có: `model` nhận sonnet, opus, haiku, fable, ID đầy đủ hoặc inherit | Có: `model` | Có, nhưng chỉ theo tier: `inherit`, `flash`, `pro` |
| Effort riêng cho từng vai | Có: `effort` nhận low, medium, high, xhigh, max (tùy model) | Có: `model_reasoning_effort` | Không có trường effort |
| Khi bỏ trống | Model: lấy theo thứ tự tham số lần gọi, frontmatter, biến `CLAUDE_CODE_SUBAGENT_MODEL`, rồi model chính. Effort: theo phiên. | Kế thừa model và effort của phiên cha | Model: `inherit` |
| Ghi đè toàn cục | `CLAUDE_CODE_EFFORT_LEVEL` ưu tiên hơn effort của vai. Thứ tự model có thay đổi theo phiên bản, nên phải ghim phiên bản host. | `[agents]` có `default_subagent_model` và `default_subagent_reasoning_effort`; giá trị lúc gọi ghi đè | Không kiểm |
| Giới hạn số luồng và độ sâu | Chưa kiểm | `agents.max_concurrent_threads_per_session` được nêu. `max_depth` không có trong trang tôi đọc, nên không khẳng định | Không kiểm |
| Hạn chế đáng chú ý | `permissionMode` bị bỏ qua khi phiên cha đang ở chế độ bypass, acceptEdits hoặc auto. Plugin subagent bỏ qua hooks và mcpServers. | `sandbox_mode`, `approval_policy`, `mcp_servers` không ghi đè được từ file vai | Tên tool sai có thể làm subagent treo. `commandExecutionPolicy` mặc định là sandbox. |

Các trang nguồn: [Claude Code, subagents](https://code.claude.com/docs/en/sub-agents); [Codex, subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) (trang `developers.openai.com/codex/subagents` chuyển hướng sang đây); [Antigravity, subagents](https://antigravity.google/docs/subagents).

**Kết quả pilot trên Claude Code CLI 2.1.81 (2026-10-17)** — chi tiết và bằng chứng ở [roadmap/evidence/pilot-host-claude-code-2026-10-17/README.md](roadmap/evidence/pilot-host-claude-code-2026-10-17/README.md):
- Model theo vai **có hiệu lực**: subagent chạy model khác phiên chính.
- Alias `haiku` trên bản này ra `claude-haiku-4-5`, không phải 5.5. Cần ghim ID đầy đủ, ví dụ `claude-haiku-5-5`, và ID này được tôn trọng.
- Effort: CLI nhận trường `effort` mà không kiểm tra giá trị (`ultra-bogus` vẫn qua). **Chưa chứng minh được effort có ảnh hưởng**: một cặp mẫu low/max cho token đầu ra gần như bằng nhau trên tác vụ nhỏ.
- Chi phí các lần thử: khoảng 0,36 USD.

**Kết luận cập nhật:**
- Claude Code và Codex có model và effort theo từng vai, đủ cho mô hình phòng ban ảo. Tài liệu không đảm bảo runtime, nên vẫn cần pilot.
- Antigravity chỉ chọn được tier flash hoặc pro, không cố định được effort. Mô hình tiết kiệm vẫn làm được nhưng thô hơn.
- Điều tôi nghi ngờ trước đó (host bỏ qua model và effort) không đúng với Claude Code và Codex theo tài liệu. Chỉ còn đúng với Antigravity phần effort.
- Chưa kiểm: Claude Desktop có nạp `.claude/agents/` không (tài liệu tôi đọc là của Claude Code), và Antigravity CLI.
- Tôi cũng đã sửa một ý trước đó: "max_depth mặc định 1" là thông tin từ nguồn thứ cấp, không có trong tài liệu chính thức của Codex.

## 5. Nhận xét về roadmap

### Nên giữ nguyên
- Native-first: không xây runtime, scheduler, vector store hay watcher.
- Một đầu mối ghi file chung; vai phụ chỉ trả đề xuất.
- Tách rõ các mức: file tồn tại, kiểm kỹ thuật, kết luận của agent, người dùng chấp nhận.
- Tra cứu và xem dữ liệu đã lưu không gọi AI (mục 10). Đây là giá trị dễ thấy nhất cho người dùng.
- Mỗi blocker chỉ chặn phần phụ thuộc vào nó; R1–R3 vẫn có ích khi chưa có đa agent.

### Còn thiếu
1. **Bảng khả năng của từng host, đặt trước khi thiết kế vai.** Mục tiêu tiết kiệm chỉ đạt nếu host áp dụng thật model và effort của từng vai. Nếu host bỏ qua, vai đó chạy bằng model chính và người dùng không biết. Đã kiểm bằng tài liệu chính thức (mục 4b): Claude Code và Codex có trường model và effort theo từng vai; Antigravity chỉ có model theo tier và không có effort. Vẫn cần pilot để xác nhận hành vi thực tế. Với mỗi host cần biết: gọi được vai không, model của vai có được áp dụng không, effort có được áp dụng không, có thấy model thực tế không, có dừng được vai không. Kết quả này quyết định cách viết file vai, nên phải có trước R4.
2. **Máy kiểm ở điểm ghi vào sổ.** Roadmap nói "một writer" nhưng chưa nói writer phải kiểm gì. Vai rẻ dễ sai, nên writer (`library.py`) phải từ chối đề xuất khi:
   - file không tồn tại, hoặc fingerprint không khớp;
   - thiếu locator, hoặc thiếu nhãn loại thông tin (trích, tính, suy luận);
   - lấy file trong `output/` hay `working/` làm nguồn gốc.

   Đã có bằng chứng hướng dẫn bằng chữ không đủ: STATE ghi qwen-max vẫn định tự đổi REVIEW thành AVAILABLE dù bị cấm.
3. **Các lỗi đã tìm thấy khi test** (chi tiết trong báo cáo kiểm thử, mục 4):
   - P1: báo cáo nâng cấp ghi `v1.8.0 -> v1.8.0` khi nội dung đã đổi.
   - P2: thông báo lỗi dòng lệnh thiếu bước tiếp theo.
   - P3: kịch bản nghiệm thu đặt project ngay trong bộ mẫu.
   - P4: hợp nhất `.new` phải sửa tay.
4. **Cột cho nguồn không phải pháp luật.** Sổ hiện chỉ hợp với văn bản pháp luật. Roadmap có nói trường pháp luật chỉ dùng khi cần (7.3), nhưng chưa nói cách chuyển: thêm cột chung, còn cột pháp luật để trống cho các loại nguồn khác.

### Nên đơn giản hóa
1. **Workbook: bớt sheet.** Thay vì ba sheet mới (Phiên bản, Nội dung, Đối chiếu):
   - R2 thêm cột vào "Danh mục": SourceID, loại nguồn, fingerprint, revision hiện hành, trạng thái đọc.
   - R3 thêm **một** sheet "Nội dung": ContentID, SourceID, revision, locator, loại thông tin, nội dung ngắn, kiểm bằng cách nào, ngày kiểm.
   - Lịch sử revision chỉ thêm khi cần.

   Ít sheet thì người dùng dễ đọc và writer ít chỗ hỏng.
2. **Excel là nơi lưu, chỉ `library.py` được ghi.** Vai phụ không bao giờ mở xlsx để ghi. Chúng ghi một file đề xuất tạm trong `working/<việc>/`, và writer kiểm rồi áp dụng. File đề xuất là đầu vào tạm, không phải kho thứ hai. Trên Windows, Excel khóa file khi đang mở, nên writer phải báo rõ "đóng Excel rồi thử lại", không ghi bừa. Cũng phải thử xem `openpyxl` ghi lại có làm mất validation hay định dạng của file mẫu thật không.
3. **Gộp profile vào vai.** Chưa cần `EXECUTION_PROFILE.json` riêng khi mỗi người dùng chỉ một host. Đặt model và effort trong file vai, có một phần cho mỗi host. Phần "host này hỗ trợ gì" lấy từ bảng khả năng ở mục "Còn thiếu". Chỉ tách thành file profile nếu thực tế cần.
4. **48 tình huống là danh mục tham chiếu, không phải việc của đợt đầu.** Đợt đầu chỉ cần khoảng 10 ca: T01, T02, T05, T06, T08, T10, T12, T13, T22, T27, T43.
5. **Không cần `TASK.md` trước R5.** Roadmap đã nói chỉ tạo khi cần; nên giữ đúng như vậy.

## 6. Đề xuất thứ tự làm

Mỗi đợt đều dùng được ngay, không chờ đợt sau.

| Đợt | Làm gì | Xong khi |
|---|---|---|
| 0. Dọn nền | Fetch và pin HEAD; push hoặc ghi rõ ba nhánh chưa có upstream; đồng bộ STATE. Sửa P1–P4: nút "giữ bản của tôi / dùng bản mới / mở để tự sửa" trong Chờ hợp nhất; thông báo lỗi dòng lệnh; nhãn phiên bản; sửa kịch bản mục 2.2. | Test xanh; mô phỏng ba nhiệm vụ lại đạt và không phải sửa tay. |
| 1. Quy tắc phiên và vai | Viết lại `AGENTS.md`: đầu phiên gọn; điều phối được gọi vai đã lập sẵn trong quyền người dùng cấp; vai phụ không ghi file chung. Sửa dòng 104. | Một phiên mới trên host pilot nắm đúng dự án và quy tắc vai. |
| 2. Writer của sổ nguồn | `library.py scan`: quét gia tăng, cấp SourceID, tính fingerprint, báo file sai chỗ. `library.py apply <đề xuất>`: kiểm như mục "Còn thiếu" rồi ghi an toàn. Thêm cột chung. View thư viện chỉ đọc trên bảng điều khiển. | Fixture đúng, sai, trùng, đổi tên, Excel đang mở đều được xử lý đúng; chạy lại không tạo dòng trùng. |
| 3. Pilot một host | Lập bảng khả năng cho host operator chọn. Tạo vai Scout bằng model rẻ, effort cố định, quét bộ nguồn giả và nộp đề xuất cho writer. Ghi số lần gọi, số lần làm lại, model thấy được. | Biết chắc host đó chạy vai đúng model hay không. Đề xuất sai của Scout bị writer chặn. |
| 4. Nội dung và hồ sơ tài liệu | Sheet "Nội dung"; gắn kết quả trong `output/` với nguồn và revision; đánh dấu cần xem lại khi nguồn đổi; thẻ hồ sơ tài liệu trên giao diện. | Mở được kết quả cũ từ hồ sơ mà không gọi AI; nguồn đổi thì đúng kết quả liên quan bị đánh dấu. |
| 5. Thêm vai | Worker, Reviewer, vai chuyên môn có người dùng thật. Hủy việc và kết quả muộn theo khả năng của host. | Một việc nhiều phần chạy hết trên host pilot. |
| 6. Phát hành | Migration, build sạch, hướng dẫn, bảng hỗ trợ theo host. | Gate đạt; bộ mẫu không mang dữ liệu dự án. |

Host thứ hai làm sau đợt 5, lặp lại đợt 3 cho host đó.

## 7. Câu hỏi để Codex phản biện

1. Gộp còn hai sheet ("Danh mục" thêm cột, cộng "Nội dung") có đủ để truy nguồn và giữ lịch sử không? Hay cần đủ ba sheet như roadmap?
2. File đề xuất tạm cho writer có vi phạm nguyên tắc "không kho thứ hai" của roadmap không? Có cách nào đơn giản hơn không?
3. Đặt model và effort theo host ngay trong file vai thay cho `EXECUTION_PROFILE.json`: có thiếu gì không?
4. Nút "giữ bản của tôi / dùng bản mới" có phá thiết kế "ứng dụng không tự hợp nhất" không? Nên ghi qua `transaction.py` như các thao tác ghi khác?
5. Thứ tự: pilot host (đợt 3) trước nội dung (đợt 4) có hợp lý không?
6. Có phần nào trong code mà tôi đánh giá sai (ví dụ `library.py` thật ra đã ghi dòng ở đâu đó)?

## 8. Giới hạn

- Đánh giá dựa trên test, mô phỏng giao diện và đọc code có chọn lọc; chưa chạy agent của bất kỳ host nào trên folder này.
- Các nhận định về Claude, Codex và Antigravity dựa trên mô tả trong roadmap; chưa kiểm tài liệu hay tài khoản thật.
- Chưa kiểm nội dung pháp lý của các gói.
