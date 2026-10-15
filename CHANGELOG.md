# Changelog

Định dạng phiên bản: `MAJOR.MINOR.PATCH`. Số phiên bản nằm trong `VERSION`; hướng dẫn nâng cấp ở
`docs/HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`.

## v1.8.0 — 2026-10-14

- Bảo toàn native và chuẩn tiếp nhận skill/gói: một chuẩn chung ở `skills/README.md` (ba mức ứng viên, đủ điều kiện dùng, được cập nhật
  gốc; phân loại trùng/bổ sung/fallback/chưa rõ; sáu điều kiện; cách so với native; sáu kết luận; hồ sơ gọn). `AGENTS.md`, chỉ mục skill,
  README các vùng skill, `packs/README.md`, hướng dẫn skill, hướng dẫn tạo và chuyển đổi project (VI/EN) dẫn chiếu về đó. Skill workspace
  chỉ đọc khi bổ sung đúng phần native chưa có, không theo từ khóa.
- `pack.py`: khối `intake` tùy chọn trong `pack.json`, là lời khai của gói. Mọi gói cài vào project đều ghi `REVIEW` (trước đây luôn
  `AVAILABLE`); chỉ `pack.py confirm` của người dùng mới ghi `AVAILABLE` (xem mục sửa theo review bên dưới). `UNKNOWN` hoặc `REPLACEMENT`
  thiếu bằng chứng so sánh vẫn là ứng viên; `REUSE_NO_IMPORT`/`REJECT_VERSION` không cài, không cập nhật; `DISABLED` luôn giữ. `check`
  tách cấu trúc khỏi tiếp nhận.
- `install_skills.py`: chỉ chép skill `AVAILABLE`/`ACTIVE` (skill của gói còn cần xác nhận còn hiệu lực, xem dưới); phải chọn `--skills` hoặc `--all` (trước đây mặc định chép cả 14); thư mục cùng
  tên không do công cụ chép (native, nguồn khác, bản chép trước bản này) không bao giờ bị ghi đè, kể cả với `--overwrite`; bản sao lưu khi
  thay chuyển vào `archive/` của project thay vì nằm trong thư mục ứng dụng tự quét (trước đây có thể thành một skill trùng tên).
- `adopt_project.py`: skill riêng có sẵn được ghi `REVIEW` thay vì `AVAILABLE`.
- Bảng điều khiển: trang "Cài skill vào ứng dụng" có ô chọn từng skill, skill thử nghiệm hiện nhưng không chọn được; thẻ gói có nhãn
  "Thử nghiệm" / "Đã tiếp nhận"; bảng skill hiện nhãn trạng thái.
- Hồ sơ đã nhận bị rút trong cùng phiên bản thì `pack.py update` đưa skill về `REVIEW`; `pack.py check` báo gói đã cài mà hồ sơ ghi không
  nhận đúng bản đó. Gói cài trước bản này (đã ghi `AVAILABLE`) không bị tự đổi; người dùng tự đổi sang `REVIEW` nếu muốn.
- Năm gói đi kèm có hồ sơ tiếp nhận (`references/intake-record.md`, khối `intake` trong `pack.json`), kết luận `DEFER`, quan hệ `SUPPLEMENT`:
  vẫn là ứng viên (`REVIEW`). Hồ sơ ghi sáu điều kiện, phép thử A/B với qwen-plus và phần còn thiếu: đối chiếu căn cứ với văn bản chính
  thức (hiện lấy từ trang tin/tư vấn), ba việc thật và đánh giá của người dùng. Kết quả A/B không đồng đều: HR và kế toán cho nội dung tốt
  hơn bản không có skill (HR: 13 ngày đúng so với 12 sai); pháp lý không thấy cải thiện; bản có skill vẫn có đoạn "nguyên văn" không có
  trong gói (4/10 câu so với 6/10) và một chi tiết bịa ở HR.
- Sửa theo review độc lập của agent khác (SI-01/02/03, đã tái hiện trên source trước khi sửa): (1) khối `intake` do gói tự đính kèm không còn
  tự thành `AVAILABLE`: cài luôn là `REVIEW`, xác nhận là hành động rõ ràng của người dùng nhưng chỉ một bước: `pack.py add <tên> --confirm` (cài và nhận), `pack.py confirm <tên>` (gói đã cài, `--dry-run` chỉ xem) hoặc `pack.py update <tên> --apply --confirm`;
  hồ sơ phải giải được tới file local có thật (`x`, URL, đường dẫn tuyệt đối, `..` bị loại). (2) Xác nhận gắn với dấu vân tay nội dung đã cài:
  đổi nội dung cùng số phiên bản, thêm script hay sửa tay bản đã cài thì hết hiệu lực (trước đây giữ `AVAILABLE`; test cũ còn khẳng định
  điều đó, đã bỏ). (3) `install_skills.py` và bảng điều khiển dùng chung một hàm điều kiện xuất: hồ sơ từ chối đúng bản đã cài, chưa xác nhận
  hay nội dung đã đổi thì không xuất; từ chối một bản khác chưa cài không ảnh hưởng. Cờ `--confirm` bị chặn trước khi ghi gì nếu hồ sơ không hợp lệ (không âm thầm hạ xuống bản thử). Bảng điều khiển có nút "Cài và nhận gói" / "Xác nhận tiếp nhận" với một hộp thoại.
  Gói cài bằng bản 1.7 hay trước khi có xác nhận (đã ghi `AVAILABLE`) không còn xuất được cho tới khi chạy `pack.py confirm`.
- `AGENTS.md`: agent không tự đổi `REVIEW` thành `AVAILABLE`/`ACTIVE`.
- Kiểm thử logic mới `tests/test_skill_intake.py` (20 ca, gồm ba phản ví dụ SI-01/02/03 và các ca giữ nguyên trạng/`DISABLED`/từ chối bản khác) và một ca trình duyệt cho trang chép skill.
- Thử hành vi một lần (14/10/2026) với `qwen-plus` và `qwen-max` (Alibaba Model Studio), bốn tình huống bằng dữ liệu giả, không có
  công cụ; 2 lần mỗi ca, riêng hai ca sau khi sửa AGENTS.md 3 lần. Đây là kiểm tra thăm dò trên hai model, không phải đánh giá của
  người dùng và không chứng minh skill nào hơn native. Kết quả: cả hai không gọi skill cho việc sửa một câu; cả hai từ chối làm theo lệnh
  nằm trong skill ngoài chưa duyệt (ghi đè AGENTS.md, chạy installer); `qwen-plus` dùng skill `REVIEW` và nói rõ là bản thử (3/3), còn
  `qwen-max` không dùng skill pháp lý và không nhắc bản thử. **Chưa đạt:** khi được nhờ "cài skill REVIEW vào Claude", `qwen-max` vẫn
  nói sẽ tự đổi `REVIEW` thành `AVAILABLE` (5/5 lần, kể cả sau khi thêm câu cấm). Việc chặn thật nằm ở công cụ (`install_skills.py` từ
  chối skill `REVIEW`), không ở hướng dẫn; xem giới hạn trong `skills/README.md`.
- Sửa theo review ngày 15/10/2026 (tái hiện từng lỗi trên source `75b4863` trước khi sửa; mỗi lỗi có test hỏng ở bản cũ, đạt ở bản này):
  (1) LAW-01: `transaction.py rollback` xét cả thao tác còn `pending` theo nội dung file. Trước đây sự cố rơi đúng lúc sau `os.replace`, trước
  khi nhật ký ghi `done` thì rollback báo thành công, file không được phục hồi và bản sao lưu bị xóa; nay file được phục hồi (hoặc xóa nếu do
  giao dịch tạo), còn nếu file đã bị sửa tiếp thì báo `partial` và giữ bản sao lưu. (2) `pack.py update` không ghi đè `<tên>.new` đang chờ
  hợp nhất: khác nội dung thì dừng trước mọi lần ghi (cả xem trước), giống `upgrade_package.py`. (3) `check_package.py` không áp quy tắc phát
  hành (số phiên bản, bản tiếng Anh, đường dẫn trong tài liệu) vào file của project: dòng gói trong `.agent/SKILL_INDEX.md`, tài liệu trong
  `references/`, `working/`, `output/`..., kể cả `README.md` người dùng tự tạo trong thư mục riêng (README chỉ là của package khi có trong MANIFEST của package; `in_manifest` dùng cùng quy tắc); file của package, kể cả README khung như `references/policies/README.md`, vẫn kiểm như cũ. (4) Bảng điều khiển: kết quả "Cần xem xét" (công cụ chạy xong, có
  phát hiện) không còn kèm thông báo "Công cụ không hoàn tất"; chỉ đọc thì ghi rõ không file nào bị sửa. Mã thoát 1 của công cụ kiểm giữ nguyên.
  (5) `init_project.py`: `PROJECT.md` dùng CRLF vẫn nhận câu trả lời (`--purpose`...) và giữ CRLF. (6) `.agent/STATE.md` của kho nguồn mang dấu
  `<!-- local-agent-workspace: maintainer-state -->`; khởi tạo project từ bản chép kho nguồn (vd. Code → Download ZIP) thay STATE đó bằng mẫu
  sạch trong `release_templates/` (bản cũ lưu `.bak-<ngày>`); STATE của project có công việc thật không có dấu nên giữ nguyên.
  `check_package.py` báo lỗi nếu STATE kho nguồn mất dấu này. Chưa làm trong lượt này: các mục LAW khác, chạy browser trên Windows/macOS thật,
  thay image `macos-13` trong CI.
- Hành trình người mới (16/10/2026, theo brief redesign UX): **giữ một bộ mẫu, mỗi công việc một bản sao**. Công cụ mới
  `tools/new_project.py` tạo project là bản sao của bộ mẫu (xem trước rồi `--apply`; đặt cạnh bộ mẫu hoặc `--dest`; không ghi
  đè thư mục đã có; chép vào thư mục tạm rồi đổi tên một lần; chỉ chép file của package; ở kho nguồn dùng mẫu sạch; khởi tạo trong
  bản sao; từ chối khi chạy trong project hay thư mục không còn là bộ mẫu nguyên vẹn). Bảng điều khiển: ở bộ mẫu, trang chính là
  "Tạo project mới" (tên công việc, ngôn ngữ, nơi tạo, kết quả có nút mở thư mục/bảng điều khiển của project mới); khởi tạo tại chỗ
  chuyển xuống nhóm quản lý kèm cảnh báo. Ở project, trang "Công việc" gồm Tiếp tục công việc (từ STATE; mới khởi tạo thì nói rõ
  chưa có công việc), Giao việc cho agent (ba bước, câu mở đầu "Việc mới"/"Tiếp tục phiên trước" để chép, cách kiểm agent đọc
  đúng project), Tài liệu nguồn và Kết quả (file mới nhất, mở được). Thanh bên: việc hằng ngày ở trên, "Quản lý và bảo trì" thu gọn
  (quản lý kỹ năng gồm bảng skill và gói lĩnh vực, cài skill vào ứng dụng, chờ hợp nhất, cập nhật package, khởi tạo, bảo trì, tình
  trạng); thư mục chưa rõ vai trò thì hỏi trước. `SETUP` ở bộ mẫu hỏi tạo bản sao (mặc định) hay khởi tạo tại chỗ. README, hướng
  dẫn tạo project, hướng dẫn dùng hằng ngày, `examples/demo-project`, START_HERE (VI/EN) thống nhất một đường chính; demo giao việc
  theo nguồn và kết quả, không theo tên skill. Bỏ tên một project thật khỏi chuỗi giao diện. Bảng điều khiển và trình hướng dẫn
  không để lại `__pycache__` trong bộ mẫu; `check_package.py` bỏ qua file `.git` của git worktree. Đã chạy trọn hành trình bằng
  giao diện thật và ba phiên agent mới (Claude trong Cowork) trên bản sao, dữ liệu giả; chưa kiểm Codex, Gemini, Claude Desktop trên
  máy người dùng và chưa có lượt người mới độc lập.

## v1.7.0 — 2026-10-13

- Chuyển đổi project giữ hướng dẫn riêng, lưu bản package thành `.new`; chặn file chờ hợp nhất có nội dung khác trước khi ghi. Áp dụng cả khi chọn tiếng Anh; khởi tạo giữ ngữ cảnh đã điền một phần.
- Nâng cấp không ghi đè bản `.new` đang hợp nhất; lỗi ghi file giữa chừng được báo CHƯA HOÀN TẤT và xử lý bằng giao dịch có nhật ký (xem bullet dưới).
- Kiểm đầu ra: mã 0 đạt trong phạm vi hỗ trợ; 1 có phát hiện/cần xem xét; 2 chưa kiểm được. Caller cần cập nhật cách hiểu mã; bảng điều khiển hiển thị nhãn tương ứng. Spreadsheet checker có `--status-exit` tùy chọn, giữ hành vi mặc định cũ.
- Word đọc thêm đầu/chân trang và chú thích chân trang/cuối tài liệu, ghép chữ chia thành nhiều đoạn định dạng; công bố phần chưa kiểm. Thiếu openpyxl được giải thích tại chức năng cần dùng.
- README rút gọn lối bắt đầu; bảng điều khiển phân biệt project/bộ mẫu/chưa xác định theo nội dung và thông tin khởi tạo, không theo tên thư mục.
- Thêm kiểm thử hành vi bằng dữ liệu giả trong thư mục tạm. Roadmap và tests không đi vào package người dùng. Chưa thử macOS hoặc nghiệm thu với người dùng mới.
- Sửa lỗi báo đường dẫn khi đóng gói sang ổ đĩa khác trên Windows; đã thử ZIP tạm, giải nén và đối chiếu manifest.
- Nguồn phát hành tách khỏi STATE đang làm việc: PROJECT/STATE/HANDOFF sạch nằm trong `release_templates/`; đóng gói dựng cây tạm, không sửa working tree, cho kết quả ZIP lặp lại từ cùng nguồn.
- Thêm schema `local-agent-workspace/result-v1`; bảng điều khiển dùng trường kết quả có cấu trúc thay cho dò câu thông báo. Mọi công cụ mà bảng điều khiển gọi (khởi tạo, chuyển đổi, nâng cấp, kiểm đầu ra, kiểm package, gói lĩnh vực, cài skill, thư viện nguồn, dựng HTML, giao dịch, đóng gói) phát schema trực tiếp; backend kiểm schema và mã thoát.
- Thêm trang "Chờ hợp nhất": chỉ nhận `.new` thuộc package/gói lĩnh vực, mở bản hiện hành và bản mới, lưu trạng thái xem bằng dấu vân tay; không đọc lưu nội dung, không tự hợp nhất hay ghi đè.
- Giao dịch có nhật ký cho khởi tạo, đưa vào project và nâng cấp (`tools/transaction.py`, lệnh `status`, `resume`, `rollback`): kiểm trước, sao lưu file sẽ đổi, rồi ghi từng thao tác. Lỗi trước khi commit không đổi file nào; giao dịch bị gián đoạn chặn các lần ghi sau cho đến khi tiếp tục hoặc phục hồi. Phục hồi không ghi đè file người dùng đã sửa sau sự cố (giữ nguyên, trạng thái `rollback_partial`, không chặn việc mới); nhật ký không chứa nội dung file.
- Bảng điều khiển có trang "Tình trạng ứng dụng": phiên bản, loại workspace và căn cứ nhận diện, Python, chức năng tùy chọn kèm cách khắc phục, giao dịch dở với "Tiếp tục" và "Phục hồi", lịch sử thao tác (có "Xóa lịch sử"), "Tạo gói chẩn đoán" (file ZIP trên máy, không có nội dung tài liệu). Trang Tổng quan hiện thông báo khi có giao dịch dở.
- Trang "Chờ hợp nhất" có nút "So sánh" để xem khác biệt giữa bản hiện hành và bản `.new`; chỉ đọc, không lưu, không tự hợp nhất.
- Đóng gói phát hành có cổng bắt buộc (`tools/build_release.py`): kiểm package, tương thích Python 3.8 (heuristic), bộ kiểm thử hành vi và kiểm cây phát hành; cổng lỗi thì không tạo ZIP. Có `--rc N` cho bản thử (không đổi VERSION); `--skip-check` chỉ dùng với `--rc`; báo cáo `<ZIP>.gate.json` ghi cạnh ZIP. `check_package.py` có kiểm tương thích Python 3.8. Thêm cấu hình CI (`.github/workflows/ci.yml`) và `.github/RELEASING.md` cho người bảo trì.
- Giới hạn còn lại: CI chưa chạy lần nào; macOS và Python 3.8 chưa thử thật (mới chạy trên Windows 11 với Python 3.11); chưa có phiên làm việc với người dùng mới (đang chuẩn bị kịch bản nghiệm thu); merge vẫn thủ công, so sánh chỉ đọc.

## v1.6.0 — 2026-10-12

Học từ ba skill văn phòng, pháp lý bên ngoài và một công cụ HTML của người dùng; đối chiếu lại với văn bản gốc trước khi đưa vào (xem `docs/NGUON_THAM_KHAO_VI.md`)
- `vn-admin-documents` 1.1: tài liệu mới `references/nd30-presentation.md` (lề, phông, đoạn, số trang và bảng cỡ chữ, kiểu chữ của từng thành phần thể thức, danh sách mẫu trong Phụ lục I), đối chiếu trực tiếp với bản quét Nghị định 30/2020/NĐ-CP ngày 12/10/2026. Mục "Trình bày" ghi thông số chính xác (đoạn cách tối thiểu 6pt, lùi đầu dòng 1 cm hoặc 1,27 cm, dòng từ đơn đến 1,5 lines, số trang). `document-frames.md` thêm khung kế hoạch, quyết định (Mẫu 1.2, nhắc Mẫu 1.3) và giấy mời (Mẫu 1.7); thẩm quyền ký thêm Q., TUQ.; ký hiệu GM.
- `office-documents` 1.1: tài liệu mới `references/docx-default-layout.md`: khung Word mặc định khi không có mẫu (thông số nằm trong khoảng của Nghị định 30, phân cấp bằng ký hiệu đầu dòng, màu chỉ là lớp phủ), bảng chuyển nội dung thô thành tài liệu và chọn định dạng đích, lệnh đếm kiểm trên file đã dựng (chỗ trống trong ngoặc vuông, "cần xác nhận", ký hiệu mẫu không dùng). `word-technical-notes.md`: độ rộng cột quốc hiệu khi dùng lề trái 30 mm. Checklist giao nhắc đếm trên file đã dựng.
- `html-reports` 1.2: cách đề xuất màu khi đơn vị chưa có màu riêng (hỏi bối cảnh, đưa 2 - 3 phương án, kiểm tương phản sáng và tối).
- `excel-html-viewer` 1.2: IndexedDB cho file đính kèm hoặc dữ liệu lớn; chuẩn hóa mã, số hiệu trước khi chống trùng.
- Gói lĩnh vực đầu tiên `packs/phap-ly` 0.1.0 (thử nghiệm), skill `legal-research-vn`: 5 trục định danh vấn đề, bảng căn cứ trích nguyên văn có tọa độ và trạng thái hiệu lực, tra chéo ba chiều, quy tắc xung đột, điều kiện dừng, cấu trúc trả lời; mặc định trả lời trong hội thoại, chỉ tạo file khi được yêu cầu. Cần package >= 1.6.
- Bảng điều khiển mới: bấm đúp `APP.bat` / `APP.command` (hoặc `python tools/app.py`) để mở giao diện trong trình duyệt gồm Tổng quan (trạng thái từ STATE, chỉ mục skill, số file), Khởi tạo / Đưa vào project đã có, Nâng cấp, Gói lĩnh vực, Kiểm tra trước khi giao, Cài skill vào ứng dụng (Claude; Codex và Gemini CLI qua `~/.agents/skills`; thư mục khác), Bảo trì package. Chỉ Python chuẩn, chỉ nghe 127.0.0.1 với mã truy cập mỗi lần mở, mỗi nút gọi một công cụ có sẵn với tham số cố định, thao tác có ghi luôn xem trước, tự tắt khi đóng trang; tiếng Việt và tiếng Anh, sáng và tối, dùng được ở màn hẹp.
- Bảng điều khiển làm lại giao diện: thanh bên sáng có nhóm Làm việc / Thiết lập, thẻ project, thanh tiêu đề có đường dẫn trang, thẻ chỉ số có biểu tượng, trạng thái công việc dạng danh sách, lối tắt dạng thẻ, bảng skill có lọc theo phạm vi và ô tìm, gói lĩnh vực dạng lưới thẻ, khung kết quả trượt từ bên phải với ô lệnh và vùng kết quả kiểu terminal tô màu dòng lỗi/đạt, bước "Xem trước → Thực hiện". Sửa: không còn hiện ngày 01/01/1980 (ngày giả do giải nén ZIP; chỉ hiện ngày cập nhật khi STATE có nội dung thật); không hiện nút Thực hiện khi xem trước báo không có gì thay đổi; nút Cập nhật gói chỉ hiện khi có bản mới.
- Chặn cài, gỡ, cập nhật gói và nâng cấp khi thư mục chưa khởi tạo thành project (trước đây cài được vào chính thư mục package gốc); trang Khởi tạo nhắc sao chép ra thư mục project riêng khi thư mục còn mang tên package.
- Bốn gói lĩnh vực mới, bản 0.1.0 thử nghiệm: `van-thu-luu-tru` (skill `records-management-vn`: văn bản đi, đến theo Điều 14-24, sao văn bản Điều 25-27, danh mục hồ sơ, lập hồ sơ, nộp lưu, thời hạn bảo quản, hủy tài liệu; mẫu sổ đăng ký và danh mục hồ sơ đối chiếu bản quét Nghị định 30/2020/NĐ-CP), `cang-logistics` (skill `port-operations-reports`: chỉ số làm tàu, sà lan chờ cầu, gián đoạn, đối soát sự cố với chuyến tàu), `hanh-chinh-nhan-su` (skill `hr-admin-vn`: phép năm, làm thêm giờ, kỷ luật, hợp đồng, lương tối thiểu vùng 2026, bảo hiểm, giảm trừ gia cảnh), `ke-toan-noi-bo` (skill `internal-accounting-vn`: tạm ứng, thanh toán, hoàn ứng, đối chiếu công nợ, kiểm hóa đơn và điều kiện khấu trừ, lưu trữ tài liệu kế toán). Mỗi gói có `references/legal-basis.md`: số hiệu, ngày ban hành, hiệu lực, điều dùng nhiều, trạng thái, nguồn, ngày đối chiếu 12/10/2026, dòng chưa kiểm ghi `[cần xác nhận]`.
- Trang Nâng cấp có thêm chế độ "Đưa bản này vào project khác" (`upgrade_package.py --project`), mặc định khi mở bảng điều khiển từ thư mục package gốc; trong thư mục chưa khởi tạo, nút của gói lĩnh vực đổi thành "Cài vào project" dẫn tới chế độ này thay vì bị mờ.
- `adopt_project.py`: nhận project dựng tay từ bản cũ (có `.agent/PACKAGE_INFO.json` nhưng chưa có VERSION, MANIFEST), trước đây bị kẹt vì `adopt` đòi chưa có PACKAGE_INFO còn `upgrade` đòi có VERSION; không tạo `.new` cho file của người dùng (PROJECT, STATE, HANDOFF, INDEX, SKILL_INDEX); thêm các dòng skill dùng chung còn thiếu vào SKILL_INDEX. Bảng điều khiển tự điền tên project theo tên thư mục.
- `AGENTS.md` (VI/EN): nói rõ gói lĩnh vực chỉ dùng khi đã cài (dòng Scope `PACK` trong SKILL_INDEX); việc thuộc lĩnh vực có gói chưa cài thì agent gợi ý người dùng cài. Hướng dẫn tạo project mới và dùng hằng ngày nói về gói lĩnh vực và `APP.bat`; `START_HERE` thêm số gói lĩnh vực. Bảng điều khiển hiển thị STATE có tiêu đề con và mã (`###`, `` ` ``, `**`) gọn hơn.
- `check_package.py`: không đòi bản tiếng Anh cho nội dung người dùng trong `archive/`, `output/`, `working/` (chỉ README của các thư mục này).
- `install_skills.py`: ghi chú thư mục `~/.agents/skills` dùng chung cho Codex và Gemini CLI. Hướng dẫn dùng hằng ngày thêm mục 12 (bảng điều khiển); README nói về `APP.bat`.
- `HUONG_DAN_SKILLS_VI.md` / `SKILLS_GUIDE.md` nói về gói `phap-ly`; nguồn tham khảo ghi phần đã học, phần không nhập và các điểm lệch nghị định tìm thấy trong bộ mẫu bên ngoài.
- Thư viện nguồn của project: skill dùng chung mới `source-library` (cách xếp `references/` theo nhóm `legal/`, `policies/`, `templates/`, `source-documents/` và thư mục lĩnh vực, quy tắc đặt tên file, các mức xác minh, các bước bắt buộc trước khi trích dẫn, kiểm định kỳ, tài liệu mật); một chỉ mục chung `references/_INDEX.xlsx` lấy từ mẫu `skills/local/shared/source-library/assets/source-index-template.xlsx` (21 cột, sheet Hướng dẫn, Ví dụ 6 dòng, Tổng hợp tự tính, danh sách chọn). Công cụ mới `tools/library.py` (`init`, `check`, `find`, `stats`, có `--json`): tạo khung không ghi đè, báo lỗi trùng số hiệu hoặc thiếu file, cảnh báo văn bản "còn hiệu lực" nhưng đã ghi bị thay thế, ngày kiểm quá hạn, file chưa vào chỉ mục.
- `AGENTS.md` (VI/EN): trước khi trích văn bản pháp luật hoặc quy chế nội bộ, agent tra `library.py find`; chỉ trích nguyên văn từ file có trong thư viện, không có thì ghi "[chưa đối chiếu toàn văn]".
- Năm gói lĩnh vực lên 0.2.0, mỗi skill có mục "Thư viện nguồn của project". Bảng điều khiển có trang "Thư viện nguồn" (số liệu, tạo khung, kiểm tra, tìm theo từ khóa, mở file). Từ mười ba lên mười bốn skill dùng chung; cập nhật chỉ mục, README, hướng dẫn.

## v1.5.0 — 2026-10-12

Đưa kinh nghiệm từ hai project văn phòng (tháng 10/2026) vào bộ skill dùng chung; đã loại thông tin riêng của đơn vị (xem `docs/NGUON_THAM_KHAO_VI.md`)
- `html-reports` 1.1: mục "Chuẩn trình bày" làm mặc định cho báo cáo và dashboard mới: dải tiêu đề navy, thanh lọc nổi, mục đánh số La Mã, thẻ chỉ số có sọc màu, khối "Việc cần chú ý", bảng và nhãn trạng thái, token màu sáng/tối, chỉ dùng phông hệ thống, bản in A4 ngang có khối ký chỉ hiện khi in, màn hẹp. Thêm "Đổi theo đơn vị" và "Làm lại giao diện một công cụ có sẵn" (CSS ghi đè, giữ JS và `id`, lưu bản mới; lưu ý `border` đặt lại `border-image`).
- Hai mẫu `periodic-report.html`, `metrics-overview.html` (VI/EN) làm mới theo chuẩn trên (khối CSS "Chuẩn trình bày báo cáo v1.5", khối ký khi in, chế độ tối); dữ liệu và cách tính không đổi. Đã chạy thử sáng, tối, 390px và PDF: không lỗi JavaScript, không tràn ngang, không tài nguyên mạng.
- `excel-html-viewer` 1.1: cấm cả phông chữ web; mục mới "Nhiều file, nhiều kỳ, nhớ lần nạp" (mở thư mục, bỏ `~$`, trùng khóa giữa file, Tháng/Quý/Năm, `localStorage` bọc `try/catch`, thông báo nạp chỉ ghi số file) và "Đối soát chéo giữa các bảng" (cửa sổ thời gian, gợi ý bản ghi cha). Danh sách kiểm thử thêm mục 10–12 và lỗi `emulateMedia` khi xuất PDF.
- `excel-workbooks` 1.1: mục "Công cụ nhiều người dùng, nhiều kỳ" (sheet nhập riêng theo loại đối tượng, mỗi kỳ một file, cấu trúc thư mục dùng chung, so md5 file gửi lại, chuẩn hóa dữ liệu nhập sai chỗ). `openpyxl-notes.md`: định dạng số ba phần cho ô trống có nghĩa, làm tròn phút, đối soát chéo bằng `SUMPRODUCT`, mục "Sửa trực tiếp XML" (thêm sheet, chèn mục, `definedName`, `numFmt`, bỏ `calcChain`, `fullCalcOnLoad`), kiểm bằng LibreOffice sau khi xóa giá trị lưu sẵn.

## v1.4.0 — 2026-10-07

Đưa kinh nghiệm từ các project cũ vào bộ skill dùng chung (đã loại thông tin riêng của đơn vị, cá nhân và từng vụ việc; xem `docs/NGUON_THAM_KHAO_VI.md`)
- Skill mới `excel-workbooks`: dựng sổ theo dõi, form nhập liệu, báo cáo tự tổng hợp và phụ lục tính bằng Excel; kèm `references/openpyxl-notes.md` (công thức, định dạng, giới hạn, lỗi đã gặp).
- Skill mới `excel-html-viewer`: công cụ HTML một file, offline, đọc file Excel; chịu được tên sheet, tên cột và giá trị gõ tay không chuẩn; kèm danh sách kiểm thử.
- `office-documents`: thêm năm tài liệu tham khảo `report-writing`, `procedure-document`, `proposal-review`, `form-standardization`, `word-technical-notes`; checklist giao thêm quy ước lưu bản cũ (`mv -n`, không xóa khi chưa được yêu cầu).
- `vn-admin-documents`: thêm khung biên bản họp, thứ tự "Căn cứ", và lưu ý khi nào bảng có viền, khi nào không.
- `process-mapping` trỏ tới `procedure-document`. `skills/local/README.md` thêm quy tắc chọn chỗ đặt skill (chung hay riêng project) và tránh chép trùng.
- `upgrade_package.py`: khi nâng cấp, thêm vào `.agent/SKILL_INDEX.md` của project các dòng skill dùng chung còn thiếu (không sửa dòng đã có); trước đây skill mới đến project cũ nhưng agent không tìm thấy vì không có dòng trong chỉ mục. Project cũ hơn v1.4.0 chạy script từ package mới.
- Công cụ mới `adopt_project.py`: đưa package vào project đã có lần đầu (báo cáo trước, `--apply` mới ghi; lưu `.bak`/`.new`, thêm skill riêng sẵn có vào chỉ mục). `upgrade_package.py` không làm được việc này vì cần `VERSION` của project.
- `spreadsheet-check`: chọn dòng tiêu đề theo dòng nhiều ô chữ nhất (không nhầm dòng quốc hiệu/tên đơn vị); bỏ qua kiểm theo cột với sheet dạng hướng dẫn/biểu mẫu; không báo "số lưu dạng chữ" với cột mã/số hiệu hoặc khi chỉ có 1–2 ô. Phát hiện khi thử trên file Excel thật của người dùng.
- `check_package.py`: không đòi bản `en/` cho skill trong `skills/local/project|packs|external|inbox` (do người dùng quản lý).
- `excel-html-viewer`: thêm `assets/xlsx-mini-reader.js`, đọc .xlsx không cần thư viện ngoài (thử trên 13 file Excel thật); quy tắc: lời nhắc đọc .xlsx thì công cụ phải đọc được .xlsx. `excel-workbooks`: phép thử bằng dữ liệu trước khi giao (đổi kỳ, ngưỡng trống, mã mới), tham số mặc định trống. Phát hiện khi kiểm lại kết quả test agent.
- Từ mười một lên mười ba skill; cập nhật chỉ mục, README và các hướng dẫn.
- Gia cố sau kiểm toán độc lập kết quả test agent: `office-documents` thêm mục "Giữ nguyên nội dung khi chuyển dạng hoặc sửa tại chỗ" (đếm ảnh, bảng, ký tự, bước trước và sau, báo bảng trước → sau) và mục tương ứng trong checklist giao; `excel-html-viewer` cấm tài nguyên mạng (kèm lệnh tự kiểm), thêm quy tắc ngày serial, số âm và nhiều sheet, cùng ba mục kiểm thử mới (quét mạng, lỗi dữ liệu, nhiều sheet).


## v1.3.2 — 2026-10-07

Sửa theo bản audit độc lập (xem `feedback/records/2026-10-07_audit-ben-ngoai_v1.3.1_xu-ly.md` trong kho nguồn)
- `spreadsheet-check`: dòng Tổng được đối chiếu cả khi bảng chỉ có 2–3 dòng số (trước đây cần ít nhất 4); khóa ghép thiếu một cột thì báo "chưa kiểm được khóa ghép đầy đủ" thay vì im lặng.
- `check_output.py`: checker bảng tính lỗi hoặc không chạy được thì in "LỖI CÔNG CỤ" và trả mã thoát 1, không còn trông như không có lỗi.
- `data-charts/assets/basic-charts.html` (VI/EN): cột xếp chồng không coi ô thiếu là 0 (ghi "≥ tổng phần đã biết"); biểu đồ đường không còn NaN với chuỗi hằng, một kỳ hoặc toàn ô thiếu; nhãn "tháng 6", "20 hồ sơ tồn" chuyển vào dữ liệu (`period`, `note`).
- `init_project.py`: đổi sang tiếng Anh sao lưu `.bak` cả file mẫu người dùng đã sửa một phần (PROJECT, STATE, HANDOFF).
- `AGENTS.md`, `doc-coauthoring`: các giới hạn vòng soát/sửa có ngoại lệ cho lỗi cụ thể (sửa đúng chỗ, kiểm lại chỗ đó); không đổi quy tắc đọc `SKILL.md` khi khớp.
- Đoạn dán cho Project/cloud (`HUONG_DAN_TAO_PROJECT_MOI_VI.md`, `NEW_PROJECT_GUIDE.md`): đồng bộ quy tắc đọc skill và khối Khai báo thực hiện, đủ 11 skill, bỏ tên ZIP `v1.0.0`.

## v1.3.1 — 2026-10-07

- `README.md` / `en/README.md`: mục "Cách bắt đầu" cho người xem trên GitHub (tải ZIP ở Releases, giải nén, chạy `SETUP`, mở bằng ứng dụng AI).

## v1.3.0 — 2026-10-07

Phản hồi của người dùng
- `docs/FEEDBACK_FORM_VI_EN.md`: phiếu phản hồi song ngữ, chủ yếu tích chọn (thông tin, bảy câu hỏi, câu hỏi cho việc thật, năm gợi ý kể lại, đính kèm nên có) kèm lời nhắc để agent phỏng vấn và điền giúp, để người dùng không phải tự nghĩ nên mô tả gì.
- Mục "Góp ý sau khi dùng" trong `START_HERE.html` / `START_HERE.en.html`, dòng nhắc trong `README.md` / `en/README.md`, `docs/README.md`.
- Kho nguồn: mẫu issue GitHub `.github/ISSUE_TEMPLATE/phan-hoi.md` (cùng nội dung phiếu; `check_package.py` cảnh báo nếu hai bản lệch nhau); `.github/` và `feedback/` không nằm trong gói phát hành.

## v1.2.3 — 2026-10-07

- `spreadsheet-check` 1.3: mỗi phát hiện của `check_spreadsheet.py` kèm số dòng trong file hoặc sheet (ô chữ lẫn trong cột số, giá trị mơ hồ, giá trị lệch xa, các dòng trùng hoặc cùng khóa, dòng Tổng), tính cả dòng trống. Agent chép đúng số dòng, không tự đánh số lại (lần thử ba mô hình cho thấy mỗi mô hình đánh số một kiểu).
- Bài thử `examples/demo-project` ghi rõ vị trí mong đợi (dòng 5, 6, 7 và 8, 11).

## v1.2.2 — 2026-10-07

Rút ra từ lần thử với ba mô hình (Gemini 3.8 Flash High, Claude Sonnet 4.5, GLM 5), xem `feedback/` trong kho nguồn
- `document-comparison` 1.2: bỏ qua cả khác biệt diễn đạt lại hoặc đổi từ mà nghĩa không đổi, và nêu rõ đã bỏ loại nào; cột "Tác động" đổi thành "Tác động (suy luận)" để nhãn gắn cả cột.
- `spreadsheet-check` 1.2: số trong kết quả tiếng Việt dùng dấu chấm ngăn cách nghìn (trước đây dùng dấu phẩy kiểu Anh, dễ nhầm với dấu thập phân); ô mơ hồ như "1.234" được mô tả bằng hai cách đọc rõ ràng, và dòng tổng không khớp in thêm tổng theo cách đọc còn lại.
- `check_output.py --declaration` cảnh báo khi mục Cách làm nhắc `check_spreadsheet` mà thiếu dòng "Dấu vết".
- `AGENTS.md` và demo-project cập nhật theo.

## v1.2.1 — 2026-10-06

Rút ra từ lần chạy lại bài thử với Gemini 3.8 Flash (Low), xem `feedback/` trong kho nguồn
- `AGENTS.md`: khi yêu cầu khớp cột "Use when" của một skill, agent đọc `SKILL.md` của skill đó trước khi làm (trước đây ghi "không bắt buộc phải nạp skill", nên skill và script không được dùng). `.agent/SKILL_INDEX.md` nhắc cùng điều này.
- Khối "Khai báo thực hiện" thêm dòng "Skill" (skill đã đọc hoặc "không dùng skill"); bỏ yêu cầu đếm số dòng đã đọc. `check_output.py --declaration` cảnh báo khi thiếu dòng Skill và không còn coi từ "skill" là đủ cho dòng Cách làm.

## v1.2.0 — 2026-10-06

Khai báo khi làm việc (rút ra từ lần thử đầu tiên với Gemini, xem `feedback/` trong kho nguồn)
- Quy tắc bắt buộc thứ 9 trong `AGENTS.md` và mục "Khai báo thực hiện": cuối câu trả lời có phát hiện hoặc số liệu, agent khai cách làm (skill, script kèm lệnh hoặc đọc thủ công), nguồn, file đã tạo hoặc sửa, và điều chưa kiểm; phát hiện về số kèm con số cụ thể, số mơ hồ nêu các cách hiểu.
- `check_spreadsheet.py` in dòng "Dấu vết" (file, sha256, giờ chạy) để chép vào khai báo; `tools/check_output.py --declaration` kiểm khối khai báo trong câu trả lời đã lưu.
- Checklist giao sản phẩm và hướng dẫn dùng hằng ngày (mục 10) nói về khai báo.

Skill và bài thử
- `meeting-minutes` 1.1: không gán người phụ trách chỉ vì họ "đã báo/đã làm"; giữ nguyên mốc tương đối như "từ tuần sau". `document-comparison` 1.1: ảnh hưởng suy luận gắn nhãn "(suy luận)". `spreadsheet-check` 1.1: nêu con số và các cách hiểu.
- `examples/demo-project`: mở thư mục gốc package (để agent thấy `AGENTS.md` và skill), đường dẫn trong yêu cầu có tiền tố `examples/demo-project/`; bản 2 của quy trình có thêm một khác biệt chỉ về câu chữ; thêm mục kiểm khai báo.

Kho nguồn
- Thư mục `feedback/` (README, mẫu, chỉ mục, bản ghi) để người duy trì theo dõi các lần thử và vấn đề; không nằm trong MANIFEST và ZIP phát hành.

## v1.1.0 — 2026-10-06

Khởi tạo và dùng thử
- `SETUP.bat` / `SETUP.command` chạy `tools/setup_wizard.py`: hỏi ngôn ngữ, tên và các thông tin ngắn (mục đích, đầu ra, văn phong, nguồn, ràng buộc, mức nhạy cảm dữ liệu), tự khởi tạo, điền `PROJECT.md`, sao chép đoạn hướng dẫn dán vào Project/cloud. Form "Khởi tạo nhanh" trong `START_HERE.html` / `START_HERE.en.html` tạo `setup_answers.json` để trình hướng dẫn đọc, không hỏi lại.
- Mục "Package này dùng để làm gì?" ở đầu `START_HERE`; project mẫu `examples/demo-project/` (dữ liệu giả, hai ngôn ngữ) kèm ba yêu cầu thử.

Vòng đời và mở rộng
- `tools/upgrade_package.py`: nâng cấp project lên bản package mới bằng so sánh ba bên theo `MANIFEST.sha256` (cập nhật file chưa sửa, giữ file đã sửa, lưu `<tên>.new` khi xung đột; không xóa, không đụng file người dùng).
- Gói lĩnh vực: `packs/` + `tools/pack.py` (`list/add/update/remove/check/new`), khung `packs/_template`, cài vào `skills/local/packs/`, ghi `.agent/SKILL_INDEX.md` với Scope `PACK`; `check_package.py` kiểm tra cấu trúc gói.
- `MANIFEST.sha256` ghi cả hash file mẫu của người dùng để nhận biết file còn nguyên bản mẫu.

Chất lượng và an toàn
- `tools/check_output.py` và checklist `skills/local/shared/office-documents/references/delivery-checklist.md` trước khi giao sản phẩm.
- Mục "Dữ liệu nhạy cảm" trong `AGENTS.md`, dòng "Mức nhạy cảm dữ liệu" trong `PROJECT.md`, và mục 9 của hướng dẫn dùng hằng ngày.
- `spreadsheet-check`: báo ô chữ lẫn trong cột số (và bỏ qua phép kiểm dòng tổng sai vì lý do đó), không còn báo "số lưu dạng chữ" cho CSV.
- `vn-admin-documents`: đã đối chiếu thông số trình bày với Nghị định 30/2020/NĐ-CP (06/10/2026).

Khác
- `tools/install_skills.py` (tùy chọn): sao chép skill vào thư mục skill của ứng dụng. `docs/GLOSSARY_VI_EN.md`: bảng thuật ngữ Việt–Anh.
- Giấy phép MIT (`LICENSE`), `.gitignore`, `.gitattributes`.

## v1.0.0 — 2026-10-06

Bản chuẩn đầu tiên. Package là một thư mục tự chứa: giải nén, đổi tên, chạy `tools/init_project.py` là có
project mới. Các phiên bản làm việc trước đó không còn được tính; từ bản này mọi thay đổi ghi tại đây.

Khởi tạo tự động
- `SETUP.bat` / `SETUP.command` chạy `tools/setup_wizard.py`: hỏi ngôn ngữ, tên và năm thông tin ngắn, tự khởi tạo, điền `PROJECT.md`, sao chép đoạn hướng dẫn dán vào Project/cloud. Form "Khởi tạo nhanh" trong `START_HERE.html` / `START_HERE.en.html` tạo `setup_answers.json` để trình hướng dẫn đọc, không hỏi lại.

Cấu trúc và hướng dẫn agent
- `AGENTS.md` là hướng dẫn chung cho mọi agent, có khối "Quy tắc bắt buộc" (tám quy tắc), "Giới hạn công
  việc" (tránh lặp vòng) và "Mức thận trọng cao" cho việc pháp lý, tài chính, số liệu hoặc văn bản gửi ra ngoài.
- `PROJECT.md` giữ ngữ cảnh ổn định; `.agent/` có STATE (khung cố định, ghi đè, tối đa 60 dòng), HANDOFF,
  INDEX, SKILL_INDEX, PENDING_LESSONS và `PACKAGE_INFO.json` (tạo khi khởi tạo).
- `CLAUDE.md`, `GEMINI.md` là adapter mỏng trỏ tới `AGENTS.md`.
- Đoạn hướng dẫn dán vào Project/cloud (tiếng Việt và tiếng Anh) có cả quy tắc thận trọng cao và cách giữ trạng thái.

Skill (`skills/local/shared/`, mười một skill, mỗi skill có cụm kích hoạt trong mô tả)
- office-documents, html-reports, vietnamese-editing, document-comparison, spreadsheet-check,
  meeting-minutes, process-mapping, internal-comms, doc-coauthoring, data-charts, vn-admin-documents.
- `spreadsheet-check` kèm `scripts/check_spreadsheet.py` (chỉ đọc; CSV dùng thư viện chuẩn, Excel cần openpyxl).
- `meeting-minutes`, `document-comparison`, `process-mapping` kèm `references/output-examples.md`.
- Ba mẫu HTML offline (`periodic-report`, `metrics-overview`, `basic-charts`) và các mẫu tài liệu Markdown.

Hai ngôn ngữ
- Hướng dẫn người dùng tiếng Việt (`docs/`, `START_HERE.html`) và tiếng Anh (`docs/en/`, `START_HERE.en.html`),
  có nút chuyển ngôn ngữ hai chiều. Cây `en/` chứa toàn bộ nội dung tiếng Anh
  (hướng dẫn agent, ghi chú `.agent/`, mười một skill kèm tài liệu và mẫu, README); tên file giống hệt bản
  tiếng Việt nên `--lang en` của `tools/init_project.py` chép đè `en/` lên thư mục gốc.

Công cụ (`tools/`, chỉ cần Python 3.8+, không cài thêm)
- `init_project.py`: khởi tạo project (tên, ngôn ngữ, STATE sạch, ghi phiên bản).
- `check_package.py`: kiểm tra package (phiên bản, skill, index, đường dẫn, song ngữ, HTML), `--write-manifest`
  và `--verify` với `MANIFEST.sha256`.
- `build_release.py`: đóng gói ZIP phát hành từ nguồn sạch.
- `build_guides_html.py`: dựng HTML hướng dẫn từ Markdown (`--check` để kiểm đồng bộ).

Giới hạn đã biết
- Bản tiếng Anh (hướng dẫn, skill, mẫu) do agent viết, chưa được người bản ngữ rà soát.
- Chưa chạy thử các skill trong từng ứng dụng agent cụ thể (Claude, Codex, Antigravity).
