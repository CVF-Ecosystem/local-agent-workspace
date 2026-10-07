# Kết quả test agent v1.4.0 — bản kiểm lại độc lập

Nguồn: thư mục `TEST_AGENT_v140_20261007-1032` (agent Claude Haiku 4.5 chạy nhiều bước con, tự chấm; Gemini chỉ từ chối thi hành khi bị dán cả file kế hoạch).
Báo cáo gốc của agent tự ghi 52/54 (96,3%), "sẵn sàng release". Bản kiểm lại này mở từng file đầu ra và chạy lại; kết quả KHÁC báo cáo gốc.

## Điều rút ra về cách test
- Agent chạy test đã được đưa sẵn "Đạt khi" nên tự chấm theo đáp án và ghi "đạt" cả khi file không đạt. Lần sau: agent chạy chỉ nhận lời nhắc; người kiểm độc lập mở file đầu ra.
- Cả 12 ca chạy bằng một mô hình (Claude). T12 (chéo mô hình) và T11 (tiếng Anh) không được thử đúng nghĩa: T11/T12 chạy trong thư mục nguồn của package và ghi `.agent/tasks/` vào đó (đã chuyển ra ngoài).
- Agent ghi thêm file ngoài yêu cầu (bản trùng, file thử, `node_modules` trong `02_Working`), trái quy tắc "không tạo file thêm".

## Kết quả đã kiểm lại
| Ca | Báo cáo gốc | Kiểm lại | Lý do |
|---|---|---|---|
| T1 | Đạt | Đạt (nhỏ) | Đọc đúng nguồn, không tạo file; nêu 4 việc ưu tiên trong khi `02_HANDOFF.md` có 3. |
| T2 | Đạt 6/6 | Đạt có điều kiện | Thể thức đúng, không bịa tên/ngày/ngưỡng. Nhưng tự thêm "cơ cấu sáp nhập", "Phòng Tài chính Kế toán", "Quy chế quản lý nội bộ", "Bến Nghé" không có trong nguồn; lưu hai bản (một trùng hệt). |
| T3 | Đạt 7/7 | KHÔNG ĐẠT | Ô "Tháng/Năm" không được công thức dùng: báo cáo cộng dồn mọi tháng nên "mỗi tháng đối chiếu định mức" sai từ tháng thứ hai (đã thử bằng LibreOffice). Ngưỡng 90 đặt sẵn; danh sách xe gõ tay trong sheet báo cáo; ghi chú mẫu vô nghĩa ("Cấp thường đặc nhân vật"). |
| T4 | Từng phần 8/9 | KHÔNG ĐẠT | Lời nhắc đòi đọc .xlsx; công cụ ghi "XLSX parsing disabled" dù ô chọn file nhận .xlsx. Hai file HTML trùng hệt. |
| T5 | Đạt 5/5 | Không đạt / lời nhắc có lỗi | File gốc đã có sẵn 20 bước dạng bảng nên lời nhắc vô nghĩa. Bản dựng lại 43 KB mất 4 hình sơ đồ (gốc 355 KB); thêm một bản chép lại thứ ba. |
| T6 | Đạt 5/5 | Chưa kiểm được | Báo cáo ghi "script v1.3" và hai cảnh báo nhiễu đã sửa ở bản mới; không rõ chạy bản nào. Chạy lại bản hiện tại: không còn hai cảnh báo đó. |
| T7 | Đạt 5/5 | Chưa kiểm lại | Không có file đầu ra để đối chiếu. |
| T8 | Đạt 7/7 | KHÔNG ĐẠT | File được báo cáo (`Bao_cao_danh_gia_...`) không có một Điều/Khoản/Điểm nào, trái với ghi "mọi nhận định có cite (Hiến pháp, Bộ luật Dân sự)". Một file thứ hai (`Bao_cao_phap_ly_...`) có số điều (Luật Đất đai 2024) chưa tra lại nguồn. Trích NĐ 100/2024 trong hồ sơ giả lập không ghi số điều: báo cáo đúng phải nói điều đó. |
| T9 | Đạt 5/5 | Một phần | Không có file `.bak` nào trong thư mục thử, trong khi báo cáo ghi có `AGENTS.md.bak`/`CLAUDE.md.bak`; project thử không có file điều hành cũ nên đường `.bak` chưa được thử. |
| T10 | Bỏ qua | Bỏ qua | Cần project có `CLAUDE.md` cũ. |
| T11 | Đạt | Chưa đạt yêu cầu | Chạy trong thư mục nguồn package, không phải project mới `--lang en`. |
| T12 | Đạt | Không hợp lệ | Không có mô hình khác Claude; chỉ "kiểm cấu trúc". |

## Đã sửa trong package sau lần kiểm lại
- `excel-html-viewer`: thêm `assets/xlsx-mini-reader.js` (đọc .xlsx không cần thư viện; thử trên 13 file Excel thật, giá trị khớp openpyxl từng ô); SKILL nói rõ lời nhắc đọc .xlsx thì công cụ phải đọc .xlsx; checklist thêm bước thử bằng .xlsx thật.
- `excel-workbooks`: mục "Trước khi giao" thêm phép thử bằng dữ liệu (đổi kỳ, ngưỡng trống, mã mới), tham số mặc định trống, danh sách lấy từ sheet danh mục, dữ liệu mẫu có nghĩa.
- Cách test: xem phần đầu file này.

## Việc còn mở
- Chạy lại T3, T4, T8 (agent khác, nhận chỉ lời nhắc; người kiểm mở file) sau khi sửa.
- T5: đổi lời nhắc sang một quy trình thật sự viết dạng văn xuôi.
- T9/T10: thử trên project có `AGENTS.md`/`CLAUDE.md` cũ khác bản package.
- T11, T12: mở phiên mới đúng nghĩa (project `--lang en`; mô hình khác Claude).
