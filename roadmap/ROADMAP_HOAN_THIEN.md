# Roadmap hoàn thiện Local Agent Workspace

Roadmap ưu tiên: bảo toàn project đang dùng → làm rõ kết quả kiểm tra → kiểm thử các luồng quan trọng → đơn giản hóa trải nghiệm.

## 1. Mục tiêu và phạm vi

Hoàn thiện package để người dùng văn phòng có thể bắt đầu thuận lợi, giữ được hướng dẫn riêng khi chuyển đổi project và hiểu đúng mức độ tin cậy của kết quả kiểm tra.

Phạm vi gồm:
- Cơ chế đưa package vào project đã có.
- Công cụ kiểm tra đầu ra và phạm vi kiểm tra Word.
- Thành phần cần cài thêm cho từng chức năng.
- Kiểm thử khởi tạo, chuyển đổi và nâng cấp.
- Hướng dẫn bắt đầu và thông báo trên bảng điều khiển.

Chưa mở rộng số lượng skill hoặc gói lĩnh vực trong đợt này.

Người phụ trách, lịch bắt đầu và ngày hoàn thành: **cần xác nhận**. Các giai đoạn dưới đây là thứ tự triển khai đề xuất, không phải cam kết thời hạn.

## 2. Giai đoạn 1 — Bảo toàn hướng dẫn riêng của project

**Ưu tiên: cao nhất.**

### Việc cần làm

1. Điều chỉnh `adopt_project.py` khi gặp hướng dẫn trùng tên nhưng khác nội dung:
   - Giữ nguyên `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` đang có.
   - Đưa bản package vào file chờ hợp nhất, chỉ tạo khi thật sự có khác biệt.
   - Nếu file chờ hợp nhất đã tồn tại, không tự ghi đè; báo xung đột để xử lý.
2. Làm rõ kết quả chuyển đổi: những file đã thêm, những file được giữ nguyên, những hướng dẫn còn cần hợp nhất; trạng thái “đã đưa package vào, còn việc hợp nhất”, tránh thông báo hoàn tất gây hiểu nhầm.
3. Làm rõ kết quả xem trước trên bảng điều khiển: file sẽ bị tác động, hướng dẫn cũ vẫn có hiệu lực, cần hợp nhất trước khi chuyển sang hướng dẫn mới.
4. Đồng bộ mô tả trong hướng dẫn công cụ và hướng dẫn chuyển đổi, cả tiếng Việt và tiếng Anh.

### Tiêu chí nghiệm thu

- Nội dung hướng dẫn riêng không đổi sau thao tác chuyển đổi.
- Chạy chế độ xem trước không ghi file.
- Chạy lại không làm mất hoặc ghi đè bản đang chờ hợp nhất.
- Hướng dẫn giống hệt không tạo bản trùng không cần thiết.
- Người dùng biết rõ phần nào đã xong và phần nào còn phải xử lý.

**Điều kiện chuyển giai đoạn:** các tình huống bảo toàn hướng dẫn đều đạt kiểm thử.

## 3. Giai đoạn 2 — Làm rõ kết quả kiểm tra đầu ra

**Ưu tiên: cao; thực hiện sau khi chốt cách biểu diễn trạng thái.**

### Việc cần làm

1. Quy định ba kết quả thống nhất:

| Kết quả | Ý nghĩa |
|---|---|
| Đã kiểm — đạt | Đã thực hiện các kiểm tra được hỗ trợ, không phát hiện lỗi trong phạm vi đó |
| Đã kiểm — có vấn đề | Đã kiểm và phát hiện nội dung cần xử lý |
| Chưa kiểm được | Không hỗ trợ, không đọc được hoặc thiếu thành phần cần thiết |

2. Sửa `check_output.py`: định dạng chưa hỗ trợ không trả cùng mã thành công; báo riêng từng file; không kết luận chung đạt nếu có file chưa kiểm; nói cụ thể phạm vi kiểm tra cơ học.
3. Cập nhật bảng điều khiển: nhãn chữ rõ ràng; phân biệt lỗi tài liệu với lỗi công cụ; không diễn giải việc không chạy được thành “không phát hiện vấn đề”.
4. Kiểm tra các công cụ đang gọi checker để không còn hiểu theo mã kết quả cũ.

### Tiêu chí nghiệm thu

- File không hỗ trợ, không tồn tại và không đọc được đều hiện “chưa kiểm được”.
- Tập file gồm file đạt và file chưa kiểm được không hiện kết quả chung đạt.
- Kết quả dòng lệnh và giao diện thống nhất.
- Không nâng cảnh báo thành khẳng định tài liệu đúng nghiệp vụ.

## 4. Giai đoạn 3 — Cải thiện kiểm tra Word và thành phần phụ thuộc

### Nhánh A: Kiểm tra Word

**Việc cần làm:**
- Công bố rõ checker kiểm phần nào.
- Mở rộng lấy văn bản từ đầu trang, chân trang, chú thích chân trang và chú thích cuối tài liệu.
- Xử lý chữ chia thành nhiều đoạn định dạng để không bỏ sót dấu hiệu chưa điền.
- Liệt kê phần chưa hỗ trợ, như chữ trong ảnh.
- Tách kiểm tra nội dung khỏi kiểm tra bố cục khi mở hoặc in.

**Tiêu chí nghiệm thu:** phát hiện chỗ chưa điền trong các phần công bố hỗ trợ; đọc lỗi phải báo chưa kiểm được; không khẳng định đã kiểm trình bày hoặc chữ trong ảnh.

### Nhánh B: Thành phần cần cài thêm

**Việc cần làm:**
- Sửa “không cài thêm” thành mô tả theo từng chức năng.
- Nêu chức năng chỉ cần Python và chức năng cần `openpyxl`.
- Kiểm tra thành phần khi chọn chức năng; thiếu thì giải thích ảnh hưởng và cách khắc phục, không tự cài.
- Đồng bộ thông báo công cụ và bảng điều khiển.

**Tiêu chí nghiệm thu:** thiếu `openpyxl` không bị hiểu là dữ liệu đã kiểm; chức năng không phụ thuộc Excel vẫn chạy; hướng dẫn và thông báo thống nhất.

## 5. Giai đoạn 4 — Kiểm thử các luồng có thể thay đổi file

**Mục tiêu:** bổ sung bằng chứng về hành vi, bên cạnh kiểm tra cấu trúc package hiện có. Chạy trên dữ liệu giả trong môi trường tạm, không dùng project thật làm nơi thử.

| Luồng | Tình huống phải kiểm | Kết quả mong đợi |
|---|---|---|
| Khởi tạo | Mẫu sạch; đã điền một phần; chạy lại | Giữ nội dung đã có, chỉ thay phần được phép |
| Chuyển đổi | Hướng dẫn riêng; trùng tên; đã có bản chờ hợp nhất | Không mất hướng dẫn, báo rõ xung đột |
| Nâng cấp | File nguyên bản; người dùng đã sửa; hai bên cùng sửa | Cập nhật đúng trường hợp, giữ phần riêng |
| Xem trước | Các luồng hỗ trợ xem trước | Không ghi hoặc sửa file |
| Lỗi giữa chừng | Không ghi được file hoặc công cụ con thất bại | Báo phần đã làm và chưa làm, không báo hoàn tất |
| Kiểm đầu ra | Đạt; có lỗi; không hỗ trợ; thiếu thành phần | Phân loại đúng trạng thái |

### Cách nghiệm thu

- So sánh nội dung trước và sau của file cần bảo toàn.
- Kiểm cả thông báo và mã kết quả.
- Mỗi lỗi cụ thể có trường hợp kiểm thử chống tái diễn.
- Chạy cùng kiểm tra package và manifest.
- Chỉ công bố nền tảng đã thực sự thử; ghi rõ nền tảng chưa thử.

**Điều kiện chuyển giai đoạn:** không còn lỗi mất nội dung riêng hoặc báo thành công sai trong các tình huống trên.

## 6. Giai đoạn 5 — Rút gọn trải nghiệm bắt đầu

### Việc cần làm

1. Hợp nhất các phần bắt đầu lặp trong README: tạo project → thêm nguồn → giao việc đầu tiên.
2. Đưa nâng cấp, cài skill và bảo trì vào phần riêng để tra khi cần.
3. Phân biệt bộ package tạo/cập nhật project với project làm việc có ngữ cảnh, tài liệu riêng.
4. Bảng điều khiển hiển thị trạng thái và căn cứ; không đủ căn cứ thì báo chưa xác định, không đoán chỉ từ tên thư mục; đưa hành động phù hợp lên trước.
5. Dùng lại bài mẫu để thử với người mới: biết mở gì đầu tiên; phân biệt nguồn và đầu ra; hiểu “chưa kiểm được”; biết khi nào hợp nhất hướng dẫn chưa hoàn thành.

### Tiêu chí nghiệm thu

- Người mới tìm được đường bắt đầu mà không đọc phần bảo trì.
- Không cần giải thích trực tiếp thêm cho bước cơ bản trong lượt thử.
- Phản hồi gây nhầm lẫn được xử lý hoặc ghi nhận trước phát hành.

## 7. Giai đoạn 6 — Đồng bộ và chuẩn bị phát hành

### Việc cần làm

- Đồng bộ tiếng Việt, tiếng Anh và HTML.
- Cập nhật CHANGELOG theo hành vi thực tế.
- Ghi rõ thay đổi mã kết quả checker và cách xử lý hướng dẫn khi chuyển đổi.
- Chạy kiểm package, kiểm thử hành vi và bản đóng gói sau giải nén.
- Chọn phiên bản theo phạm vi cuối cùng; chưa ấn định trong roadmap.

### Điều kiện hoàn thành roadmap

- Hướng dẫn riêng được bảo toàn khi chuyển đổi.
- File chưa kiểm được không bị báo đạt.
- Phạm vi Word và phụ thuộc được công bố đúng.
- Luồng ghi file quan trọng có kiểm thử đạt.
- Hướng dẫn bắt đầu thống nhất với giao diện và công cụ.
- Giới hạn chưa xử lý được ghi rõ trong bản phát hành.

## 8. Nguyên tắc kiểm soát phạm vi

- Mỗi giai đoạn chỉ sửa thành phần phục vụ mục tiêu của nó.
- Không viết lại toàn bộ giao diện hoặc thư viện skill.
- Không dùng bổ sung tài liệu thay cho sửa hành vi sai.
- Không tuyên bố “an toàn tuyệt đối” hoặc “đã kiểm toàn bộ”.
- Nếu chia đợt phát hành, ưu tiên giai đoạn 1–2 và kiểm thử tương ứng; trải nghiệm làm sau.

## 9. Tiến độ triển khai — 2026-10-13

| Giai đoạn | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| 1 — Bảo toàn hướng dẫn | Đã triển khai | Giữ hướng dẫn cả VI/EN, chặn `.new` khác nội dung; kiểm thử chuyển đổi, xem trước, chạy lại |
| 2 — Trạng thái kiểm tra | Đã triển khai | Mã 0/1/2; bảng tính có phát hiện không báo đạt; kiểm tra giao diện với file không hỗ trợ |
| 3 — Word và phụ thuộc | Đã triển khai | Kiểm các phần Word bằng file giả có chữ chia đoạn; lỗi XML và thiếu openpyxl được báo chưa kiểm |
| 4 — Kiểm thử hành vi | Đạt phạm vi Windows hiện tại | 15 kiểm thử đạt; có kiểm chuyển đổi, khởi tạo, nâng cấp, lỗi công cụ con và giả lập lỗi ghi |
| 5 — Trải nghiệm | Đã sửa, chưa nghiệm thu với người mới | README VI/EN có lối bắt đầu thống nhất; trạng thái theo nội dung; chưa có thử nghiệm người dùng |
| 6 — Chuẩn bị phát hành | Đã đồng bộ và kiểm đóng gói; chưa phát hành | HTML đồng bộ; kiểm package 0 lỗi/0 cảnh báo; ZIP tạm được giải nén và xác minh, không giữ bản phát hành |

Lệnh kiểm thử hành vi: `python -B -m unittest discover -s tests -v`.
Kiểm cấu trúc: `python tools/check_package.py`; đối chiếu: `python tools/check_package.py --verify`.
Thử đóng gói bằng `tools/build_release.py --out` trong thư mục tạm, có kiểm loại roadmap/tests khỏi ZIP.
Phát hiện và sửa thêm lỗi hiển thị đường dẫn khi thư mục đóng gói nằm khác ổ đĩa trên Windows; thử lại đạt.

Giới hạn còn lại: chưa thử macOS/Python 3.8; chưa có nghiệm thu người dùng mới; chưa kiểm toàn bộ tính năng giao diện.
Chưa nâng VERSION hoặc phát hành. STATE ở kho làm việc đã ghi tiến độ; cần trả STATE về mẫu trong bản nguồn sạch trước lần đóng gói phát hành thực tế.

## 10. Roadmap nâng cấp mức độ chuyên nghiệp

Phần này nối tiếp các sửa đổi nền tảng đã hoàn thành. Thứ tự ưu tiên là: tách nguồn phát hành → quản lý hợp nhất → chuẩn hóa giao tiếp giữa công cụ và giao diện → phục hồi giao dịch → kiểm soát phát hành → hoàn thiện trải nghiệm.

### Giai đoạn 7 — Tách bộ nguồn phát triển, project làm việc và bản phát hành

**Ưu tiên: rất cao.**

#### Mục tiêu

Người duy trì không phải đưa STATE đang làm việc về mẫu bằng tay trước mỗi lần đóng gói. Bản phát hành chỉ chứa nội dung dành cho người dùng và luôn có PROJECT, STATE, HANDOFF sạch.

#### Việc cần làm

- Đặt các file mẫu phát hành ở một nguồn riêng hoặc dựng chúng trong thư mục tạm từ mẫu đã kiểm soát.
- Để `.agent/STATE.md` của kho nguồn tiếp tục ghi tiến độ phát triển mà không đi vào ZIP.
- Khai báo rõ nhóm file: nguồn phát triển, file project của người dùng, file phát hành và file chỉ dành cho người duy trì.
- Cho `build_release.py` từ chối đóng gói nếu file mẫu phát hành thiếu, sai cấu trúc hoặc chứa dữ liệu project.
- Kiểm ZIP sau giải nén: không có roadmap, tests, feedback, lịch sử thao tác, đường dẫn máy hoặc dữ liệu riêng.

#### Tiêu chí nghiệm thu

- Đóng gói không sửa working tree.
- STATE phát triển không xuất hiện trong ZIP; STATE mẫu đúng khung.
- Chạy đóng gói hai lần từ cùng nội dung tạo cùng danh sách file và cùng nội dung logic.
- Bản ZIP vượt qua kiểm release và kiểm manifest sau giải nén.

### Giai đoạn 8 — Trung tâm quản lý việc chờ hợp nhất

**Ưu tiên: rất cao.**

#### Mục tiêu

Người dùng nhìn thấy toàn bộ file `.new` cần xử lý ngay trên bảng điều khiển và biết file nào đang có hiệu lực.

#### Việc cần làm

- Quét có giới hạn các file chờ hợp nhất do chính công cụ tạo; không coi mọi file `.new` trong tài liệu người dùng là xung đột package.
- Hiển thị file hiện hành, bản package chờ hợp nhất, nguyên nhân và thao tác đã tạo ra nó.
- Có trạng thái: chưa xem, đang xử lý, đã hợp nhất cần xác nhận và đã giải quyết.
- Cho phép mở hai file từ bảng điều khiển; chưa tự động hợp nhất nội dung.
- Chỉ đánh dấu hoàn tất sau khi bản `.new` được xử lý và kết quả được kiểm lại.
- Giữ trạng thái qua lần mở ứng dụng tiếp theo mà không lưu nội dung tài liệu vào nhật ký.

#### Tiêu chí nghiệm thu

- Không bỏ sót xung đột do chuyển đổi hoặc nâng cấp tạo ra.
- Không báo nhầm file người dùng không thuộc quản lý package.
- Sau khi mở lại ứng dụng, danh sách và trạng thái vẫn đúng.
- Không có thao tác nào tự ghi đè file hiện hành.

### Giai đoạn 9 — Chuẩn hóa kết quả có cấu trúc

**Ưu tiên: rất cao.**

#### Mục tiêu

Giao diện không còn phải nhận diện câu chữ trong đầu ra của script để quyết định trạng thái hoặc hiện nút hành động.

#### Việc cần làm

- Xây dựng một schema kết quả dùng chung, có tối thiểu: phiên bản schema, trạng thái, mã kết quả, thông điệp, file bị tác động, phát hiện, phần chưa kiểm, việc cần làm và trạng thái hợp nhất.
- Thêm chế độ `--json` cho các công cụ được bảng điều khiển gọi; giữ đầu ra chữ cho người dùng dòng lệnh.
- Bảng điều khiển đọc dữ liệu cấu trúc, không dùng biểu thức nhận diện các câu như “không có gì cần thay đổi”.
- Phân biệt lỗi nhập liệu, lỗi tài liệu, lỗi thành phần phụ thuộc, lỗi công cụ và thao tác hoàn tất một phần.
- Kiểm tính tương thích khi schema thay đổi; schema không hợp lệ phải báo lỗi công cụ, không suy đoán.

#### Tiêu chí nghiệm thu

- Đổi ngôn ngữ hoặc sửa câu thông báo không làm thay đổi hành vi giao diện.
- Mỗi công cụ chính có kiểm thử đầu ra JSON hợp lệ và nhất quán với mã thoát.
- Giao diện xử lý được trạng thái đạt, cần xem xét, chưa kiểm, xung đột và hoàn tất một phần.
- Không còn logic nghiệp vụ quan trọng dựa vào tìm chuỗi trong `app_ui.html`.

### Giai đoạn 10 — Giao dịch file và phục hồi khi gián đoạn

**Ưu tiên: cao; triển khai sau schema kết quả có cấu trúc.**

#### Mục tiêu

Khởi tạo, chuyển đổi và nâng cấp có thể tiếp tục hoặc phục hồi rõ ràng khi lỗi giữa chừng.

#### Việc cần làm

- Kiểm trước toàn bộ điều kiện: quyền ghi, dung lượng cần thiết, xung đột `.new`, file nguồn và phiên bản.
- Lập kế hoạch thao tác có mã giao dịch trước khi ghi.
- Ghi vào thư mục tạm cùng ổ đĩa, xác minh rồi thay file theo từng bước có kiểm soát.
- Lưu nhật ký giao dịch tối thiểu: đường dẫn tương đối, hành động, dấu vân tay trước/sau và trạng thái; không lưu nội dung file.
- Khi mở lại, phát hiện giao dịch dang dở và đưa ra đúng hai khả năng khi có thể: tiếp tục hoặc phục hồi.
- Phục hồi chỉ chạm vào file thuộc giao dịch đó và phải kiểm dấu vân tay trước khi thay.

#### Tiêu chí nghiệm thu

- Mô phỏng lỗi tại từng bước không làm mất bản gốc.
- Không phục hồi đè lên file đã được người dùng sửa sau sự cố.
- Có thể xác định chính xác việc gì đã hoàn tất và việc gì chưa.
- Chạy lại an toàn, không nhân đôi file hoặc trạng thái.

### Giai đoạn 11 — Trang tình trạng và nhật ký vận hành tối thiểu

**Ưu tiên: cao.**

#### Việc cần làm

- Thêm trang “Tình trạng ứng dụng”: phiên bản, loại workspace và căn cứ nhận diện, Python, thành phần tùy chọn, khả năng đang dùng được, xung đột và giao dịch dang dở.
- Thêm lịch sử thao tác cục bộ: thời điểm, loại thao tác, trạng thái, số file tác động và mã giao dịch.
- Không ghi nội dung tài liệu, tên người, khóa truy cập hoặc dữ liệu nghiệp vụ.
- Có chức năng xuất gói chẩn đoán đã che đường dẫn người dùng và loại dữ liệu nhạy cảm.
- Cho phép người dùng xóa lịch sử vận hành cục bộ bằng thao tác rõ ràng, có phạm vi chính xác.

#### Tiêu chí nghiệm thu

- Người dùng biết vì sao một chức năng chưa dùng được và cách khắc phục.
- Gói chẩn đoán không chứa nội dung tài liệu hay đường dẫn tuyệt đối của máy.
- Nhật ký đủ để xác định lần thao tác gần nhất thành công, thất bại hay dang dở.

### Giai đoạn 12 — Cổng chất lượng và phát hành đa nền tảng

**Ưu tiên: cao.**

#### Việc cần làm

- Đặt ma trận hỗ trợ chính thức cho Windows, macOS và các phiên bản Python.
- Chạy tự động kiểm cú pháp, kiểm package, kiểm hành vi, dựng hướng dẫn, đóng gói và kiểm ZIP trên các nền tảng cam kết.
- Thêm kiểm thử giao diện cho luồng chính: khởi tạo, kiểm đầu ra, nâng cấp, quản lý hợp nhất và trạng thái thiếu dependency.
- Công bố checklist phát hành, chính sách phiên bản, ghi chú nâng cấp và giới hạn còn lại.
- Tạo release candidate để nghiệm thu trước khi phát hành chính thức.

#### Tiêu chí nghiệm thu

- Không thể tạo bản phát hành chính thức khi cổng bắt buộc chưa đạt.
- Kết quả kiểm thử ghi rõ hệ điều hành và phiên bản Python.
- Bản phát hành có hướng dẫn nâng cấp và khả năng quay lại phù hợp với thay đổi.

### Giai đoạn 13 — Nghiệm thu trải nghiệm người dùng

**Ưu tiên: vừa, nhưng bắt buộc trước khi gọi sản phẩm hoàn thiện.**

#### Việc cần làm

- Thử với người mới theo ba nhiệm vụ: tạo project, kiểm một file và xử lý một lần nâng cấp có xung đột.
- Ghi thời gian hoàn thành, điểm dừng, thuật ngữ gây khó hiểu và chỗ cần trợ giúp trực tiếp.
- Kiểm dùng bàn phím, trạng thái focus, tương phản, màn hình hẹp, trạng thái đang chạy và thông báo lỗi.
- Rút gọn màn hình theo phát hiện thực tế; không thêm tour dài nếu nhãn và luồng có thể tự giải thích.

#### Tiêu chí nghiệm thu

- Người mới hoàn thành ba nhiệm vụ mà không cần hướng dẫn miệng ngoài nội dung ứng dụng.
- Mọi lỗi đều nói rõ điều đã xảy ra, dữ liệu có an toàn không và bước xử lý tiếp theo.
- Các vấn đề nghiêm trọng từ lượt thử được sửa và kiểm lại đúng chỗ.

## 11. Thứ tự triển khai đề xuất cho đợt tiếp theo

1. Giai đoạn 7 — tách nguồn phát hành.
2. Giai đoạn 9 — chuẩn hóa kết quả có cấu trúc.
3. Giai đoạn 8 — trung tâm quản lý hợp nhất, dựa trên schema mới.
4. Giai đoạn 10 — giao dịch và phục hồi.
5. Giai đoạn 11–13 — chẩn đoán, cổng phát hành và nghiệm thu trải nghiệm.

Không mở rộng thêm skill, gói lĩnh vực, tài khoản hay đồng bộ đám mây trong đợt này. Mốc hoàn thành tiếp theo là Giai đoạn 7–9 đạt tiêu chí nghiệm thu và có kiểm thử hành vi tương ứng.

## 12. Tiến độ nhóm ưu tiên 1, 3 và 4 — 2026-10-13

| Hạng mục | Trạng thái | Bằng chứng / phạm vi |
|---|---|---|
| 1 — Tách nguồn phát hành | Đã triển khai | Mẫu sạch trong `release_templates/`; dựng và kiểm trong thư mục tạm; không sửa STATE/MANIFEST nguồn; hai lần dựng cùng nguồn cho ZIP cùng SHA-256 |
| 3 — Quản lý việc chờ hợp nhất | Đã triển khai | Trang riêng có badge, mở hai bản, ba trạng thái xem và lưu qua lần mở lại; chỉ nhận đường dẫn thuộc manifest hoặc gói cài đặt |
| 4 — Kết quả có cấu trúc | Đã triển khai cho toàn bộ `/api/run`; chi tiết native cho bốn luồng chính | Schema v1; chuyển đổi, nâng cấp, kiểm đầu ra, đóng gói phát chi tiết trực tiếp; backend chuẩn hóa công cụ còn lại và từ chối schema sai hoặc mã thoát lệch |

Đã bổ sung kiểm thử cho schema, ranh giới file hợp nhất, trạng thái bị đặt lại khi bản `.new` đổi, bản phát hành sạch và tính lặp lại. Giao diện đã được thử với một xung đột giả có trạng thái lưu qua reload và một file không hỗ trợ trả “Chưa kiểm được”; không ghi nhận lỗi JavaScript trong lượt thử. File giả và trạng thái thử đã được loại bỏ sau kiểm tra.

Giới hạn còn lại của ba hạng mục: chưa có trình so sánh nội dung trong giao diện; người dùng vẫn hợp nhất bằng công cụ chỉnh sửa hiện có. Các công cụ ít dùng được backend bọc schema tối thiểu, chưa phát chi tiết `files/findings` trực tiếp. Phục hồi giao dịch giữa chừng thuộc Giai đoạn 10, chưa nằm trong đợt này.

## 13. Tiến độ đợt hoàn thiện Giai đoạn 10–13 — 2026-10-13

Đợt này do orchestrator điều phối, các worker thi công theo phạm vi file tách biệt; orchestrator review và chạy lại kiểm tra độc lập. Trạng thái dưới đây chỉ ghi điều đã kiểm được trên máy phát triển.

| Giai đoạn | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| 9 — Kết quả có cấu trúc (phần còn lại) | Đã triển khai | Mọi công cụ bảng điều khiển gọi (11 công cụ) phát envelope trực tiếp; đầu ra cho người đọc không đổi (đối chiếu 117 lần chạy trước/sau) |
| 10 — Giao dịch và phục hồi | Đã triển khai | `tools/transaction.py`: kiểm trước, staging, sao lưu, commit từng thao tác, `status/resume/rollback`; khởi tạo, chuyển đổi, nâng cấp ghi qua giao dịch. Review vòng 1 sửa 4 lỗi (chặn vĩnh viễn sau phục hồi một phần, báo sai "chưa ghi gì" khi commit dở, nhật ký treo khi lỗi trước commit, khôi phục không nguyên tử). Orchestrator thử độc lập: kill giữa chừng → tiếp tục đúng trạng thái cuối; kill → phục hồi giống từng byte; nhật ký không có nội dung hay đường dẫn tuyệt đối |
| 11 — Trang tình trạng và nhật ký | Đã triển khai | Trang "Tình trạng ứng dụng", lịch sử thao tác `.agent/runtime/operations.jsonl` (không nội dung, tối đa 500 dòng), gói chẩn đoán đã che đường dẫn và tên người dùng (orchestrator kiểm: không lộ đường dẫn project, thư mục home, tên máy, tên project, dữ liệu đã gõ, mã truy cập), nút Tiếp tục/Phục hồi, xóa lịch sử có phạm vi rõ. Đóng thêm giới hạn của mục 12: trang Chờ hợp nhất có "So sánh" (chỉ đọc) |
| 12 — Cổng chất lượng và phát hành | Đã triển khai, CI chưa chạy | `build_release.py` có 4 cổng bắt buộc, `--rc N`, `--skip-check` chỉ với RC, báo cáo `.gate.json` ghi hệ điều hành và Python; kiểm tương thích Python 3.8 (heuristic); `.github/workflows/ci.yml` (Windows/Ubuntu/macOS × 3.8/3.12) và `.github/RELEASING.md`; kiểm thử giao diện bằng trình duyệt (Playwright, tự bỏ qua khi không có) |
| 13 — Nghiệm thu trải nghiệm | Phần kỹ thuật xong; nghiệm thu người dùng chưa làm | Bàn phím, bẫy focus hộp kết quả, tên truy cập, tương phản ≥ 4,5:1 cả hai giao diện, không tràn ngang ở 360/390 px, trạng thái đang chạy chặn bấm hai lần, thông báo lỗi nói việc đã xảy ra/dữ liệu có an toàn/bước tiếp theo. Kịch bản nghiệm thu: `roadmap/KICH_BAN_NGHIEM_THU_NGUOI_DUNG.md`. Chưa có phiên thử với người dùng mới thật |

Kiểm thử hành vi: 87 bài (bài giao diện bỏ qua khi thiếu Playwright). Lệnh: `python -B -m unittest discover -s tests -v`.

Giới hạn còn lại trước khi gọi là hoàn thiện:
- Workflow CI chưa chạy lần nào (cần đẩy lên remote, chưa được cấp quyền). Chưa thử macOS, Python 3.8 hay trình đọc màn hình; mới chạy trên Windows 11 với Python 3.11.
- Chưa nghiệm thu với người dùng mới theo kịch bản; tiêu chí của Giai đoạn 13 về người mới chưa đạt.
- Hợp nhất `.new` vẫn thủ công; so sánh chỉ đọc. Bước `init_project.py` sau khi chuyển đổi chạy ngoài giao dịch của chuyển đổi.
- Chưa nâng VERSION, chưa tạo bản phát hành; CHANGELOG ghi ở mục "Chưa phát hành".
