# Đánh giá độc lập — Local Agent Workspace v1.3.1

**Ngày audit:** 07/10/2026  
**Repo:** https://github.com/CVF-Ecosystem/local-agent-workspace  
**Commit được đọc:** `06e56ff555c91d1003bd39d8a7296486d18e9a45`  
**Phạm vi:** workspace tác nghiệp văn phòng trên file; không đánh giá như một ứng dụng coding hoặc hệ thống quản trị agent.

## Kết luận

Bản hiện tại tiến bộ về khả năng bắt đầu sử dụng, sự cụ thể của skills và cách ghi nhận thử nghiệm. Không cần xây lại, không cần thêm tầng quản lý, và sự tồn tại của vài script phụ trợ không làm package thành một ứng dụng coding.

Tuy nhiên, cần sửa một số lỗi số liệu/khởi tạo đã xác định từ nguồn; không nên coi các script và mẫu hiện tại là đã vững trên những dữ liệu văn phòng thông thường. Đồng thời, hướng dẫn đã siết khá rõ so với định hướng ban đầu: từ gợi ý cách làm sang bắt buộc đọc skill, giới hạn số vòng và khai báo theo mẫu.

Một khoảng cách riêng về phạm vi bàn giao: repo vẫn dùng các skill viết lại, chưa chứa bốn skill gốc và tài nguyên external mà người dùng đã yêu cầu tải bổ sung trong cuộc trao đổi. Đây không phải kết luận rằng các skill viết lại kém; hai loại tài nguyên không thay thế hoàn toàn cho nhau.

**Khuyến nghị:** sửa các lỗi cụ thể, làm nhất quán hướng dẫn theo mức độ công việc, hoàn tất hoặc xác nhận lại lựa chọn external skills. Chưa cần tăng số skill hoặc thêm cơ chế kiểm soát.

## 1. Cách kiểm tra và giới hạn

Đã đọc cả 11 `SKILL.md` trong `skills/local/shared/`; các file chính README, AGENTS, PROJECT, SKILL_INDEX, CHANGELOG; hướng dẫn tạo project và nguồn tham khảo; tài liệu công cụ; các script khởi tạo, nâng cấp, cài skill, kiểm đầu ra, kiểm bảng tính, đóng gói; phần mã liên quan trong các mẫu HTML; chỉ mục feedback và bản tổng hợp thử ba mô hình. Có đối chiếu metadata commit và release qua GitHub API.

Không tải được toàn bộ repo/ZIP vào môi trường thực thi trong lượt audit này. Các phép thử độc lập dùng hàm/nhánh logic chép từ nguồn đã đọc, không phải chạy end-to-end bản phát hành. `reproduce_core.py` giữ logic kiểm tra nhưng rút gọn thông báo; `reproduce_charts.js` giữ hàm tính/vẽ nhưng dùng DOM mô phỏng. Hai file JSON ghi kết quả đã thực chạy với Python 3.13.5 và Node.js 22.16.0.

Chưa kiểm trực tiếp trên Claude Desktop, Codex Desktop hoặc Antigravity; chưa mở toàn bộ giao diện HTML của commit này trong trình duyệt; chưa kiểm hash của ZIP phát hành sau khi tải; chưa chạy parser Excel thực trong các ca tái hiện. Không tuyên bố tiết kiệm token, an toàn tuyệt đối hoặc tương thích native đã được chứng nhận.

Các bản ghi thử của người duy trì là bằng chứng được repo cung cấp, không phải những phiên chạy do người audit tự thực hiện. Đối chiếu với v2.2 trong báo cáo này là theo phạm vi và quyết định đã thống nhất trong cuộc trao đổi, không phải diff từng byte với ZIP cũ.

## 2. Những điểm nên giữ

### 2.1. Skills đã gắn với việc thật

`meeting-minutes` xử lý đúng một lỗi hay gặp: người phát biểu hoặc người từng làm việc không mặc nhiên là người được giao việc tiếp theo. `document-comparison` tập trung vào thay đổi có nghĩa và tách tác động suy luận khỏi nội dung văn bản. `vietnamese-editing` giữ nghĩa, mức chắc chắn và thuật ngữ; không biến biên tập thành bước hậu xử lý mọi nhiệm vụ.

Đây là những bổ sung có giá trị hơn việc viết dài các lời khuyên chung. Không cần giảm từ 11 skill xuống một con số nhỏ chỉ để package trông nhẹ hơn; quan trọng là chỉ mở phần liên quan.

Nguồn: [meeting-minutes](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/skills/local/shared/meeting-minutes/SKILL.md), [document-comparison](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/skills/local/shared/document-comparison/SKILL.md), [vietnamese-editing](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/skills/local/shared/vietnamese-editing/SKILL.md).

### 2.2. Phân biệt ngữ cảnh với khả năng của provider

PROJECT giữ ngữ cảnh ổn định, STATE giữ việc đang dở; README nói rõ bản chuẩn local không có nghĩa xử lý AI offline. Tên adapter và thư mục skill không được mô tả như bảo đảm tự động nhận diện trên mọi ứng dụng. Đây là cách diễn đạt trung thực nên giữ.

Nguồn: [PROJECT.md](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/PROJECT.md), [README.md](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/README.md).

### 2.3. Công cụ phụ trợ có lý do tồn tại

Khởi tạo, nâng cấp kiểu so sánh ba bên và dựng lại HTML giải quyết thao tác lặp của người dùng/người duy trì. Các mặc định xem trước, giữ file sửa riêng và tách bản xung đột là hữu ích. Không cần loại bỏ chúng chỉ vì có mã Python; điều cần giữ là không biến chúng thành thủ tục cho từng yêu cầu văn phòng.

Nguồn: [tools/README.md](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/tools/README.md), [upgrade_package.py](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/tools/upgrade_package.py).

### 2.4. Feedback có đầu vào và tiêu chí cụ thể

Repo có ba bài thử, bản ghi và bảng tổng hợp thay vì chỉ nói "đã test". Sửa số dòng từ script thay vì để mô hình tự đếm là một cải tiến đúng chỗ. Tuy nhiên, phải giữ đúng mức kết luận của những phép thử này — xem mục 5.

Nguồn: [feedback/INDEX.md](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/feedback/INDEX.md), [tổng hợp v1.2.2](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/feedback/records/2026-10-07_tong-hop-3-mo-hinh_v1.2.2.md).

## 3. Các lỗi chức năng cần sửa

Ưu tiên dưới đây theo ảnh hưởng đến công việc văn phòng, không phải phân loại sự cố bảo mật.

### F01 — Bỏ sót tổng sai khi bảng chỉ có ít dòng số

**Ưu tiên: sớm.**  
**Nguồn:** `skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py`, hàm `check_sheet`, nhánh `if numcol and len(allnum) >= 4 ...`.

Phép đối chiếu dòng Tổng đang nằm trong cùng nhánh cần ít nhất bốn giá trị số để tính tứ phân vị/outlier. Điều kiện đủ dữ liệu cho outlier không cần thiết đối với phép cộng.

Ca tái hiện ở cấp hàm:

```csv
Item,Quantity
A,10
B,20
Total,999
```

Kết quả: không báo tổng sai. Đúng ra tổng là 30, chênh lệch với 999 là 969. Ca đối chứng có bốn dòng 10, 20, 30, 40 thì cảnh báo tổng 100 và chênh 899 xuất hiện.

**Sửa tối thiểu:** tách phép kiểm Tổng khỏi điều kiện số mẫu của outlier. Chỉ tính khi đủ dữ kiện và cùng đơn vị; chưa đủ thì nêu chưa kiểm, không bỏ qua im lặng. Giữ cách xử lý số mơ hồ.

**Kiểm lại:** bảng 1, 2, 3, 4 dòng; tổng đúng và sai. Không cần thêm framework test.

[Đường dẫn nguồn](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py). Kết quả: `python_reproductions.json`, `total_2_rows` và `total_4_rows`.

### F02 — Khởi tạo tiếng Anh có thể mất PROJECT đã điền một phần

**Ưu tiên: sớm.**  
**Nguồn:** `tools/init_project.py`, `pristine`, vòng overlay `en/`, biến `keep`.

Khi tên dự án còn nguyên `[Tên]`, hàm `pristine` coi PROJECT là file mẫu, ngay cả khi người dùng đã điền mục đích hoặc trường khác. Nhánh overlay cho phép thay file. PROJECT lại thuộc USER_TEMPLATES nên không bật sao lưu trong biến `keep`.

Fixture dùng để kiểm nhánh:

```text
- Tên dự án: [Tên]
- Mục đích và người đọc: Báo cáo riêng đã điền
```

Với giả định hash không còn khớp mẫu, kết quả vẫn là `pristine=True`, `backup=False`. Theo nhánh mã đã đọc, đổi sang EN trong tình huống này có thể ghi đè phần đã điền. Đây là kiểm logic quyết định, chưa chạy toàn bộ initializer trên checkout.

**Sửa tối thiểu:** không dùng một placeholder còn sót để kết luận toàn bộ file chưa sửa. File người dùng thay đổi nên được giữ hoặc sao lưu trước khi overlay; tận dụng hash/logic bảo toàn đã có, không cần thêm hệ thống quản lý phiên bản.

**Kiểm lại:** giữ tên mẫu nhưng điền mục đích; giữ phase mẫu nhưng điền quyết định trong STATE; đổi ngôn ngữ; lần chạy lại có `--force`.

[Đường dẫn nguồn](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/tools/init_project.py). Kết quả: `init_partial_project_en_overlay`.

### F03 — Cột xếp chồng biến dữ liệu thiếu thành 0

**Ưu tiên: sớm.**  
**Nguồn:** `skills/local/shared/data-charts/assets/basic-charts.html`, `stack()`.

Tổng và từng phần cột dùng `s.values[i] || 0`. Khi một thành phần là `null`, mẫu coi nó như số 0, trái hướng dẫn không thay ô thiếu bằng 0.

Ca tái hiện: kỳ T1 có A=10, B=null. Bảng chi tiết ghi B=“—”, nhưng Tổng=10; tooltip phần B lại ghi 0. Đây không chỉ là nhãn trình bày: thiếu số liệu không cho phép khẳng định tổng đầy đủ bằng 10.

**Sửa tối thiểu:** tổng có thành phần thiếu thì hiển thị chưa đủ dữ liệu, hoặc ghi rõ tổng phần đã biết. Không dùng toán tử mặc định 0 cho giá trị chưa biết. Dữ liệu 0 thật vẫn phải hiển thị và tính bình thường.

[Đường dẫn nguồn](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/skills/local/shared/data-charts/assets/basic-charts.html). Kết quả: `javascript_reproductions.json`, `stack_null_component`.

### F04 — Biểu đồ đường hỏng với chuỗi hằng hoặc chỉ một kỳ

**Ưu tiên: vừa.**  
**Nguồn:** cùng file trên, `line()`, hàm `x` và `y`.

Trục x chia cho `n-1`; trục y chia cho `hi-lo`. Ca `[100,100,100]` làm `hi==lo` và sinh tọa độ NaN. Ca một kỳ làm mẫu số trục x bằng 0, cũng sinh NaN. Ca đối chứng `[100,110,120]` không có NaN.

Ví dụ chuỗi SVG thực sinh từ hàm:

```text
<path d="M44 NaNL250 NaNL456 NaN" ... />
```

**Sửa tối thiểu:** tạo khoảng trục hợp lệ cho chuỗi không đổi; một kỳ thì vẽ điểm/thẻ số hoặc vị trí giữa khung. Tập rỗng/toàn null nên có trạng thái thiếu dữ liệu. Không cần nhập một framework biểu đồ để sửa trường hợp này.

Đồng thời, một số nhãn phụ hiện ghi cứng “tháng 6” và “20 hồ sơ tồn từ kỳ trước” ngoài `report-data`. Đây là điểm nhỏ cần đưa vào cấu hình hoặc xóa khi tái dùng để tránh sót nội dung minh họa.

Kết quả: `constant_line`, `single_period_line`, `varied_line_control`.

### F05 — Công cụ kiểm đầu ra nuốt trạng thái thất bại của checker con

**Ưu tiên: vừa.**  
**Nguồn:** `tools/check_output.py`, nhánh `.csv/.xlsx/.xlsm`.

Script chạy `check_spreadsheet.py`, in stdout/stderr rồi `continue`, không cộng lỗi vào `bad` và không xử lý `r.returncode`. Trong mô phỏng nhánh này, tiến trình con trả mã 2 vì không đọc được workbook nhưng wrapper vẫn dẫn tới mã 0.

Đây là khác biệt giữa “không thấy lỗi trong phần đã kiểm” và “không kiểm được”. Agent/công cụ dựa vào exit code có thể hiểu nhầm.

**Sửa tối thiểu:** ít nhất truyền nhận trạng thái không thực thi/không đọc được. Tách rõ cảnh báo nghiệp vụ với lỗi công cụ; không bắt buộc mọi cảnh báo phải có mã lỗi. Trường hợp tái hiện dùng checker con giả lập thất bại, không chứng minh đã thử mọi lỗi Excel thực.

[Đường dẫn nguồn](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/tools/check_output.py). Kết quả: `check_output_child_error`.

### F06 — Thiếu một phần khóa ghép nhưng vẫn kiểm như khóa đã đủ

**Ưu tiên: vừa.**  
**Nguồn:** `check_spreadsheet.py`, phần `kidx` và `if keys and not kidx`.

Yêu cầu khóa Mã + Ngày, nhưng bảng chỉ có Mã và Số lượng. Vì tìm thấy ít nhất một cột khóa, script không báo thiếu Ngày và tiếp tục báo trùng theo Mã. Hai dòng trùng Mã chưa chắc trùng tổ hợp Mã + Ngày.

**Sửa tối thiểu:** xác định danh sách cột được yêu cầu nhưng còn thiếu. Báo rõ chưa kiểm được khóa ghép; có thể trình bày kiểm một phần nhưng không thay đổi định nghĩa khóa một cách im lặng.

Nguồn cùng F01. Kết quả: `partial_composite_key`.

### F07 — Đường “bắt đầu” dùng latest trong khi release đang là prerelease

**Ưu tiên: vừa, sửa rất nhỏ.**

README dẫn người dùng mới đến `/releases/latest`. Trong lần kiểm này, GitHub API `/releases/latest` trả 404; danh sách `/releases` có đúng bản `v1.3.1` với `prerelease: true`, kèm ZIP đã upload. Vì vậy không được kết luận repo chưa có bản tải xuống — có bản tải, nhưng đường latest không phù hợp với trạng thái phát hành hiện tại.

GitHub định nghĩa latest là bản phát hành không phải draft/prerelease. Nên dẫn tới danh sách Releases hoặc tag v1.3.1 trong giai đoạn thử. Chỉ chuyển trạng thái stable khi tác giả thực sự muốn công bố stable, không chỉ để chữa liên kết.

Nguồn: [README](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/README.md), [release list](https://api.github.com/repos/CVF-Ecosystem/local-agent-workspace/releases), [GitHub Get latest release](https://docs.github.com/en/rest/releases/releases#get-the-latest-release). Release là dữ liệu có thể thay đổi sau thời điểm audit.

## 4. Những điểm thiết kế cần điều chỉnh, không phải lỗi thực thi

### D01 — Hướng dẫn đang chuyển dần thành quy trình bắt buộc

AGENTS vừa nói chọn native/local/direct linh hoạt, vừa buộc đọc SKILL.md khi yêu cầu khớp Use when. Kèm theo đó là số vòng làm/soát/sửa cố định, và khối khai báo nhiều mục cho kết quả từ file. `doc-coauthoring` còn giới hạn mỗi mục một vòng sửa theo phản hồi.

Changelog cho thấy đây không phải thay đổi vô cớ: người duy trì đã quan sát mô hình bỏ qua skill hoặc khai báo không đủ rồi bổ sung hướng dẫn. Phần xác thực, không bịa, không ghi đè nguồn là cần giữ. Tuy nhiên, “có đọc skill” không tự chứng minh đầu ra đúng, cũng không phải lúc nào là phương án hiệu quả hơn công cụ/native skill.

**Điểm cần nói công bằng:** mục giới hạn có ngoại lệ khi người dùng yêu cầu hoặc có vấn đề cụ thể; không phải lệnh cấm mọi lần sửa thêm. Vấn đề là các câu tuyệt đối như “không có vòng soát thứ hai” và “chỉ một lần tự sửa” gây khó hiểu khi chính lần soát phát hiện lỗi sửa được ngay. Giới hạn vòng phản hồi của người dùng trong đồng soạn càng dễ cản trở công việc hợp lý.

Gợi ý thay đổi nhỏ:

> Chọn công cụ hoặc skill phù hợp với yêu cầu. Khi đã chọn một skill, đọc hướng dẫn và phần tài nguyên cần dùng. Có thể xử lý trực tiếp hoặc dùng khả năng native nếu đã đáp ứng nhiệm vụ. Hạn chế đọc/kiểm tra lặp không có thông tin mới; lỗi cụ thể ảnh hưởng đầu ra là lý do để sửa đúng phần, không cần làm lại toàn bộ. Trình bày nguồn, cách làm và phần chưa kiểm ở mức cần thiết cho người dùng hiểu kết quả.

Giữ nguyên quyền người dùng yêu cầu chỉnh tiếp. Không cần thêm “mode”, bộ định tuyến hay bộ đo token.

Nguồn: [AGENTS.md](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/AGENTS.md), [SKILL_INDEX](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/.agent/SKILL_INDEX.md), [doc-coauthoring](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/skills/local/shared/doc-coauthoring/SKILL.md), [CHANGELOG](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/CHANGELOG.md).

### D02 — Các bản viết lại chưa đáp ứng yêu cầu thêm bản gốc external

Repo ghi rõ `skills/external/` còn trống; `data-charts` viết mới từ ý tưởng Lieflat, `internal-comms` và `doc-coauthoring` viết lại tiếng Việt, Humanizer được tham khảo trong `vietnamese-editing`. Các mô tả này trung thực.

Nhưng trong cuộc trao đổi, yêu cầu gần nhất của người dùng là tải bổ sung các skill gốc có ích, bao gồm tài nguyên/mẫu và giấy phép, cho mục đích cá nhân phi thương mại. Bản local viết lại và thư viện gốc có giá trị khác nhau: một bên ngắn, sát tiếng Việt; một bên có chiều sâu, mẫu và cách triển khai đã có. Không nên coi bên thứ nhất là hoàn thành tự động yêu cầu bên thứ hai.

Giữ 11 skill hiện có. Nếu quyết định bổ sung gốc vẫn còn hiệu lực, đặt bốn skill chọn lọc trong external cùng tài nguyên liên quan và ghi nhận nguồn, giấy phép. Mô tả rõ khác nhau giữa bản local và external để agent chọn theo nhiệm vụ. Không chạy installer toàn repo, không nhập global rules/hooks, và không tự nạp tất cả các tài nguyên đó đầu phiên. Đây là hoàn tất phần đã được yêu cầu, không phải đề nghị mở rộng kho tùy ý.

Nguồn: [NGUON_THAM_KHAO_VI.md](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/docs/NGUON_THAM_KHAO_VI.md). Không đưa ra kết luận pháp lý mới về phạm vi thương mại; điều khoản của từng nguồn vẫn phải được giữ đúng khi nhập.

### D03 — Hướng dẫn cloud và hướng dẫn local chưa đồng nhất

Đoạn để dán vào Project/cloud trong hướng dẫn tạo project vẫn gọi skill là tùy chọn và không có khối khai báo mới. AGENTS và SKILL_INDEX lại buộc đọc skill khi khớp. Hai đường bắt đầu có thể dẫn tới hành vi khác nhau mà người dùng không hiểu vì sao.

Một số chi tiết phụ cũng cũ: hướng dẫn giải nén còn ghi v1.0.0; đoạn cloud liệt kê 10 skill thay vì 11; mục giới hạn kiểm tra nói chưa thử trong ứng dụng trong khi feedback đã ghi các lần thử mô hình/môi trường cụ thể. Cần phân biệt chính xác: phần nào đã được người duy trì thử, phần nào chưa thử end-to-end.

Không cần đồng bộ mọi nội dung thành một tài liệu khổng lồ. Chỉ đối chiếu những nguyên tắc ảnh hưởng hành vi và bỏ các con số/tên phiên bản viết cứng không cần thiết. Sau khi sửa Markdown, dùng công cụ dựng HTML sẵn có. Công cụ hiện giữ nguyên phần shell/nav/các số tổng quan, nên --check không thay thế việc nhìn lại phần shell có thay đổi.

Nguồn: [hướng dẫn tạo project](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/docs/HUONG_DAN_TAO_PROJECT_MOI_VI.md), [tools/README](https://github.com/CVF-Ecosystem/local-agent-workspace/blob/06e56ff555c91d1003bd39d8a7296486d18e9a45/tools/README.md).

## 5. Bằng chứng thử nghiệm nên được hiểu tới đâu?

Bản tổng hợp v1.2.2 ghi mỗi mô hình một lần chạy, cùng ba bài. Đây là kiểm hồi quy hữu ích cho những lỗi đã biết: bỏ thay đổi câu chữ không đổi nghĩa; ghi nhãn suy luận; xử lý số mơ hồ; chép dấu vết.

Chưa có cơ sở từ những bản ghi đó để nói đã chứng minh mức tiết kiệm token, mức giảm loop, ưu thế so với không dùng package, hoặc tương thích mọi phiên bản Claude/Codex/Antigravity. Trong chỉ mục đã đọc không có ca Codex; các kết quả đều là bản ghi của người duy trì, không phải đánh giá độc lập trên từng ứng dụng.

Không nên dùng “đủ mục khai báo” hoặc “đã đọc skill” làm đại diện cho độ đúng. Script/mẫu cũng có thể sai; agent lặp lại nguyên kết quả của một script có lỗi thì vẫn sai. Các ca F01–F06 cho thấy cần kiểm ví dụ mới ngoài dữ liệu demo, nhưng không cần xây một hệ thống benchmark lớn.

Gợi ý thử tiếp vừa đủ: một bảng ngắn có Tổng, một bảng thiếu cột khóa ghép, một chuỗi số không đổi, một biểu đồ thiếu thành phần, một PROJECT điền dở khi đổi ngôn ngữ. Với phiên agent, chọn thêm một yêu cầu sửa nhỏ và một công việc văn phòng thật ngoài bộ demo; quan sát đúng kết quả và công người dùng phải sửa, không chỉ số lượt gọi skill.

## 6. Thứ tự xử lý đề nghị

1. Sửa F01, F02, F03 trước: số liệu sai hoặc nguy cơ mất phần người dùng đã điền.
2. Sửa F04–F07: biểu đồ trường hợp đơn giản, mã lỗi checker, khóa ghép, đường bắt đầu.
3. Làm nhẹ và nhất quán D01/D03; giữ trung thực và bảo toàn nguồn, bỏ giới hạn cơ học gây cản trở.
4. Hoàn tất hoặc xác nhận lại D02 theo lựa chọn của người dùng; chưa cần thêm skill thứ 12 hay tầng quản trị.

Không phải tất cả cần một bản tái cấu trúc. Phần lớn là thay điều kiện hoặc diễn đạt ngắn trong các file đã có. Những phép kiểm trong báo cáo phục vụ người duy trì sửa đúng lỗi, không phải thêm thủ tục bắt người dùng văn phòng làm mỗi ngày.

**Đánh giá cuối:** nền tảng phù hợp và đáng tiếp tục sử dụng thử; đã hữu ích hơn bản khung ban đầu. Điều cần làm tiếp là sửa đúng vài chỗ và giảm sự cứng nhắc, thay vì bổ sung thêm tính năng hoặc thêm lệnh bắt buộc cho agent.
