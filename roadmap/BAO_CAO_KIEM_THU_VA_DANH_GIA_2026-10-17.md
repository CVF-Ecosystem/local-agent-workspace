# Báo cáo kiểm thử và đánh giá dự án — 2026-10-17

> Bản tạm. Chưa commit. Thư mục `roadmap/` chỉ dành cho kho nguồn, không đi vào ZIP phát hành.

Written for: người duy trì Local Agent Workspace (kho nguồn).

## 1. Phạm vi và cách chạy

- Kho: `local-agent-workspace`, branch `branding-tokens`, HEAD `b13e375`. Cây làm việc sạch trước khi chạy.
- Môi trường: Windows 11, Python 3.11.9.
- Lệnh: `python -B -m unittest discover -s tests -v`, đặt `PYTHONUTF8=1` để log ghi UTF-8.
- Các ca giao diện chạy bằng trình duyệt thật (Playwright và Chromium) và các ca Excel dùng `openpyxl` thật. Không có ca nào bị bỏ qua.

## 2. Kết quả kiểm thử tự động

**129 ca, 0 lỗi, 0 thất bại, 0 bỏ qua. Thời gian 124,7 giây. Thoát với mã 0.**

| Module | Số ca | Ghi chú |
|---|---|---|
| `test_panel.py` | 23 | |
| `test_release_gate.py` | 10 | Kiểm các cổng đóng gói và ZIP |
| `test_skill_intake.py` | 20 | Luồng tiếp nhận skill và gói |
| `test_structured_tools.py` | 15 | Có ca Excel, chạy vì đã có `openpyxl` |
| `test_transactions.py` | 24 | Giao dịch, phục hồi, rollback |
| `test_ui_browser.py` | 17 | Trình duyệt thật: bàn phím, tương phản, màn hình hẹp |
| `test_workflows.py` | 20 | Luồng khởi tạo, chuyển đổi, nâng cấp |
| **Tổng** | **129** | |

**Đối chiếu số ca.** `grep` thấy 130 chỗ `def test_`. Một chỗ (`test_release_gate.py`, dòng 135) nằm trong chuỗi mã của ca giả lập, không phải ca thật, nên còn 129 ca. Các con số khác trong tài liệu là ảnh chụp ở thời điểm khác nhau: release notes v1.8.0 ghi 125/125 (16/10), STATE ghi 109 (trên máy cũ), roadmap mục 13 ghi 87 (13/10). Con số hiện tại là 129.

**Hiển thị tiếng Việt.** Khi chạy không đặt `PYTHONUTF8`, log trên terminal hiện lỗi font. Khi đặt `PYTHONUTF8=1`, log ghi đúng tiếng Việt. Đây có vẻ là do encoding của môi trường, không phải lỗi của test. Chưa xác minh trên terminal Windows của người dùng.

**Gate phát hành (rc1).** `build_release.py --rc 1` đạt cả ba cổng: `package_check` (0 lỗi, 0 cảnh báo), `python38_compat` (0 vấn đề, heuristic), `behaviour_tests` (129 ca OK). ZIP tạm `local-agent-workspace-v1.8.0-rc1.zip` có 230 file, SHA-256 `fcfed6d2…213800`, lưu trong thư mục scratch, không vào kho.

## 3. Mô phỏng ba nhiệm vụ của kịch bản nghiệm thu (dữ liệu giả, không phải người thật)

Mục này thay cho nghiệm thu người mới ở mức kỹ thuật. Một script tự động điều khiển Chromium trên bảng điều khiển thật (`tools/app.py`), đi theo thẻ nhiệm vụ trong `roadmap/KICH_BAN_NGHIEM_THU_NGUOI_DUNG.md` mục 3. Dữ liệu theo mục 2.2 và 2.3 của kịch bản. Dòng "ghi chú của người thử" được thêm theo mục 2.4.

| Nhiệm vụ | Kết quả mô phỏng | Ứng dụng nói gì |
|---|---|---|
| 1. Tạo project `Du an thu 01` | Đạt. Project được tạo cạnh bộ mẫu; bộ mẫu không đổi. | Xem trước, rồi Thực hiện: "Đã ghi thay đổi. Bước tiếp: kiểm lại kết quả ở trang tương ứng." |
| 2. Kiểm `bien-ban-thu.txt` | Đạt. Phát hiện `[Tên khách hàng]` chưa điền và nhãn "dữ liệu giả"; kiểm đủ (0 chưa kiểm được). | "Đã kiểm xong và có điểm cần xem… Chỉ đọc: Không file nào bị sửa. Bước tiếp: xử lý từng điểm rồi kiểm lại." |
| 3. Nâng cấp, hợp nhất | Đạt sau khi hợp nhất thủ công: giữ cả dòng gói mới và dòng của người thử, xóa `.new`. Báo cáo cuối "Không có gì cần thay đổi"; Chờ hợp nhất trống. | "Còn file cần hợp nhất: bản hiện có được giữ nguyên, bản mới nằm cạnh với đuôi .new." |

Chi tiết:

- Chờ hợp nhất hiện đúng một file `.agent/README.md` với trạng thái "Chưa xem". So sánh (diff) hiện đúng dòng thêm và dòng bị thay.
- Bước hợp nhất do script làm bên ngoài ứng dụng, đúng như cách người dùng phải làm. Ứng dụng không có nút "giữ bản của tôi" hay "dùng bản mới" (xem P4).
- Console trình duyệt không có lỗi JavaScript nào (đã bỏ qua 404 của favicon).

**Ca lỗi qua giao diện (tiêu chí C2: nói rõ đã xảy ra, dữ liệu có an toàn không, bước tiếp theo):**

| Tình huống | Thông báo | Đủ ba phần? |
|---|---|---|
| Tạo project trùng tên | "Nơi lưu đã có thư mục…; thư mục đó được giữ nguyên, không ghi đè… Chưa tạo gì." | Đủ |
| Nâng cấp từ thư mục không tồn tại | "Không thấy thư mục… Chưa ghi gì. Bước tiếp: sửa thông tin đã nêu ở trên, rồi xem trước lại." | Đủ, nhưng bước tiếp còn chung chung |
| Kiểm file không tồn tại | "Chưa kiểm được đầy đủ: không phải kết quả đạt. Bước tiếp: đọc lại file và đối chiếu bằng tay." | Gần đủ |

**Cùng các lỗi trên qua dòng lệnh** (không thuộc kịch bản, chỉ để so sánh):

- Nâng cấp từ thư mục không tồn tại: "Không thấy VERSION trong package: <đường dẫn>". Thiếu bước tiếp theo và không nói dữ liệu có an toàn.
- Kiểm file không tồn tại: "Không thấy file. CHƯA KIỂM ĐƯỢC." Thiếu bước tiếp theo.

**Bố cục:** hộp kết quả rộng 640 px trên màn hình 1280 px, và chiếm toàn màn hình 390 px. Nút đóng nằm trong vùng hiển thị ở cả hai kích thước; không có cuộn ngang. Ảnh chụp đầu tiên bị cắt ở mép phải là do chụp lúc hoạt ảnh đóng đang chạy, không phải lỗi bố cục.

**Bằng chứng nằm trong kho:** [roadmap/evidence/mo-phong-2026-10-17/](roadmap/evidence/mo-phong-2026-10-17/), gồm script, log, JSON và ảnh chụp. Xem `README.md` trong thư mục đó để biết đầu vào và cách chạy lại. Lần chạy lại bằng script đã khôi phục cho cùng kết quả: `steps` của `result.json` và `errors.json` giống lần đầu từng bước.

**Lưu ý về script:** `journey.py` gốc đã bị xóa do lỗi của tôi: hàm dọn thư mục đầu chạy xóa luôn cả thư mục chứa script. Script đã được khôi phục từ nội dung đã chạy lần đầu, nằm ngoài thư mục `ui`, và đã được chạy lại thành công. Các đường dẫn trong script vẫn là đường dẫn scratch của phiên 2026-10-17; `README.md` trong thư mục bằng chứng nêu cách chạy ở phiên khác.

## 4. Phát hiện

| Mã | Phát hiện | Mức |
|---|---|---|
| P1 | Báo cáo nâng cấp ghi "v1.8.0 -> v1.8.0" khi nội dung đã đổi. Gây hiểu nhầm là không có gì thay đổi. | Thấp |
| P2 | Thông báo lỗi dòng lệnh (`upgrade_package`, `check_output`) thiếu bước tiếp theo và không nói dữ liệu có an toàn. Giao diện đã tốt hơn. | Thấp đến vừa |
| P3 | Kịch bản mục 2.2 đặt project trong `goi\`, tức chính thư mục bộ mẫu. Điều này trái với README ("bộ mẫu giữ nguyên, không làm việc trong đó") và với cách ứng dụng làm (tạo bản sao cạnh bộ mẫu). Kịch bản cần sửa trước khi chạy thật; mô phỏng này làm theo cách ứng dụng làm. | Vừa, vì làm sai kịch bản sẽ đo sai |
| P4 | Chờ hợp nhất chỉ có So sánh, Mở bản hiện hành, Mở bản mới, Đánh dấu đã xem. Không có nút "giữ bản của tôi" hay "dùng bản mới", nên người dùng phải tự sửa file `.md`. Thiết kế hiện tại là có chủ đích (ứng dụng không tự hợp nhất), nhưng đây là bước người mới dễ vướng nhất. | Vừa; mô phỏng không đo được điều này |

## 5. Đánh giá

**Điểm mạnh**

- Định vị rõ cho người làm văn phòng; hướng dẫn có tiếng Việt và tiếng Anh.
- Ít phụ thuộc: script chủ yếu dùng thư viện chuẩn Python, chạy cục bộ. Chỉ `openpyxl` là tùy chọn cho kiểm Excel.
- Quản trị an toàn: tài liệu nguồn là dữ liệu chứ không phải lệnh; không ghi đè file gốc; skill ngoài ở trạng thái `REVIEW`; có giao dịch với phục hồi; có mã băm kiểm tra toàn vẹn.
- Vòng kiểm thử đầy đủ: 129 ca, có kiểm trình duyệt thật; có cổng đóng gói đã đạt ở rc1, ZIP kèm báo cáo `.gate.json`, CHANGELOG.
- Ba nhiệm vụ của kịch bản chạy đúng qua giao diện thật, không lỗi console, thông báo lỗi chính ở giao diện đạt C2.

**Điểm yếu và rủi ro**

- Độ phức tạp vượt quy mô bộ mẫu: khoảng 20 script trong `tools/`, máy trạng thái xác nhận, giao dịch, gộp bản, 5 gói lĩnh vực, 14 skill, bản tiếng Anh song song, nhiều hướng dẫn có cả `.md` lẫn `.html`. `AGENTS.md` lại dặn "làm vừa đủ". Chi phí bảo trì do đó cao.
- Chưa có bằng chứng dùng thật: `PROJECT.md` còn placeholder; các thư mục `references/`, `working/`, `output/` trống.
- Mô phỏng chứng minh luồng kỹ thuật chạy đúng, không chứng minh người mới làm được. Bước hợp nhất thủ công (P4) là chỗ rủi ro nhất và chưa có người thật thử.
- Trạng thái lệch: STATE ghi nhánh `ux-language-r2`, nhưng repo đang checkout `branding-tokens`. Nhiều nhánh chưa push nên có rủi ro mất công việc.
- Rủi ro pháp lý: các gói `phap-ly`, `hanh-chinh-nhan-su`, `ke-toan-noi-bo` có căn cứ chưa đối chiếu toàn văn (STATE ghi rõ). Các gói này giữ `REVIEW` là đúng.

**Kết luận.** Kỹ thuật và quản trị ở mức tốt; test xanh, gate rc1 đạt, và ba nhiệm vụ chạy đúng qua giao diện thật khi mô phỏng. Phù hợp để thử nghiệm nội bộ hoặc beta. Chưa nên gọi là hoàn thiện hay phát hành rộng cho người dùng văn phòng khi chưa có người thật thử bước hợp nhất và chưa thu gọn.

## 6. Việc còn lại (theo ưu tiên)

1. Đồng bộ STATE với branch và số liệu thực tế (129 ca, rc1 đã đạt gate).
2. Sửa kịch bản mục 2.2 theo P3 trước khi chạy với người thật.
3. Cân nhắc P4: thêm lựa chọn "giữ bản của tôi" và "dùng bản mới" cho từng file `.new`, hoặc hướng dẫn rõ hơn ở Chờ hợp nhất.
4. Sửa P1 và P2: đổi cách ghi phiên bản khi nội dung đổi, và thêm bước tiếp theo cùng câu nói về dữ liệu cho thông báo lỗi dòng lệnh.
5. Nghiệm thu với 1–3 người thật theo kịch bản đã sửa (Giai đoạn 13). Mô phỏng không thay thế bước này.
6. Đưa các nhánh chưa push lên remote, hoặc ghi rõ nhánh nào chỉ nằm ở máy này.
7. Đối chiếu căn cứ pháp lý trong các gói trước khi nhận chúng.
8. Kiểm Python 3.8 và macOS trên máy thật hoặc qua CI. Roadmap ghi chưa thử.
9. Xem xét thu gọn: bản HTML và bản tiếng Anh nào thực sự cần.
10. Kiểm hiển thị tiếng Việt trên terminal Windows của người dùng.

## 7. Giới hạn của báo cáo này

- Kiểm thử tự động và mô phỏng chỉ chạy trên một máy Windows 11 với Python 3.11.9 và Chromium headless.
- Mô phỏng dùng script, không phải người thật: không đo được thời gian hoàn thành, sự bối rối, thuật ngữ khó hiểu hay chỗ người mới cần trợ giúp.
- Không chạy CI, không thử macOS hay Python 3.8, không kiểm nội dung pháp lý.
- Không đọc hết `tools/*.py`, `docs/` và các skill; chỉ liệt kê và đọc các phần liên quan.

---

Khai báo thực hiện
- Cách làm:
  - Chạy `python -B -m unittest discover -s tests -v` với `PYTHONUTF8=1` (129 ca).
  - Chạy `python -B tools/build_release.py --rc 1 --out <scratch>` (cổng và ZIP tạm).
  - Giải nén ZIP vào thư mục scratch; chạy `init_project.py`, `check_package.py --write-manifest`, `check_output.py`, `upgrade_package.py` (báo cáo rồi `--apply`), `new_project.py`.
  - Chạy Chromium headless qua `tests/test_ui_browser.py` (lớp `Panel` để khởi động `tools/app.py`) theo ba nhiệm vụ, hai ca lỗi và một lần đo bố cục.
  - Chạy `git status` trước và sau.
- Skill: không dùng skill.
- Nguồn:
  - Log chạy đầy đủ; `tests/*.py`; `tools/README.md` (mục gate); kết quả JSON và ảnh chụp trong scratch.
  - `roadmap/ROADMAP_HOAN_THIEN.md` (mục 9, 13); `roadmap/KICH_BAN_NGHIEM_THU_NGUOI_DUNG.md` (mục 2–3, 6–7).
  - `.agent/STATE.md`; `dist/release_notes.md`; tiêu đề `CHANGELOG.md`.
- Thay đổi trong kho: file báo cáo này và thư mục `roadmap/evidence/mo-phong-2026-10-17/`. ZIP rc1 và dự án mô phỏng vẫn nằm trong scratch, không vào kho.
- Chưa kiểm: CI, macOS, Python 3.8, nội dung pháp lý trong các gói, người dùng thật, toàn bộ `tools/*.py` và `docs/`.
