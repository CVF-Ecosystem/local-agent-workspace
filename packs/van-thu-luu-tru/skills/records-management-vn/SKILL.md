---
name: records-management-vn
description: Gợi ý tổ chức công tác văn thư - lưu trữ của đơn vị - văn bản đi, văn bản đến, sổ đăng ký, sao văn bản, danh mục hồ sơ, lập hồ sơ, nộp lưu, thời hạn bảo quản, hủy tài liệu, tài liệu lưu trữ số; căn cứ có ngày đối chiếu. Kích hoạt khi người dùng nói "sổ công văn đi đến", "đăng ký văn bản", "sao y", "danh mục hồ sơ", "lập hồ sơ", "nộp lưu", "thời hạn bảo quản", "hủy tài liệu". / Records management for a unit: registers, copies, file lists, filing, archiving, retention, destruction. Triggers on document registers, copies, file lists, archiving.
metadata:
  version: "0.2"
---

# Văn thư - lưu trữ

Dùng khi người dùng cần dựng hoặc kiểm việc quản lý văn bản và hồ sơ của đơn vị: sổ hoặc bảng theo dõi văn bản đi, đến;
sao văn bản; danh mục hồ sơ năm; lập hồ sơ và nộp lưu; bảng thời hạn bảo quản; hồ sơ hủy tài liệu. Soạn nội dung và thể thức
một văn bản cụ thể thì dùng `vn-admin-documents`.

## Căn cứ

Bảng căn cứ đầy đủ (số hiệu, điều, hiệu lực, nguồn, ngày đối chiếu): `references/legal-basis.md`. Thứ tự áp dụng: quy chế
văn thư, lưu trữ của đơn vị; văn bản của cơ quan cấp trên; Nghị định 30/2020/NĐ-CP (văn thư); Luật Lưu trữ 2024 và văn bản
hướng dẫn (lưu trữ). Doanh nghiệp không thuộc khu vực nhà nước thường chỉ "tham khảo" Nghị định 30; hỏi đơn vị áp dụng ở mức nào.
Trước khi dùng một con số (thời hạn, số ngày), mở dòng tương ứng trong bảng căn cứ và nói rõ ngày đối chiếu.

## Văn bản đi (Nghị định 30/2020/NĐ-CP, Điều 14 - 19)

Trình tự: kiểm tra thể thức trước khi ban hành, cấp số và thời gian ban hành, đăng ký, nhân bản, đóng dấu hoặc ký số, phát hành
và theo dõi chuyển phát, lưu văn bản. Số văn bản do văn thư cấp theo hệ thống số của đơn vị, liên tục trong năm; không tự đặt số
khi soạn nháp (ghi `[số]`). Sổ đăng ký văn bản đi tối thiểu 10 cột (mẫu: `references/registers.md`).

## Văn bản đến (Điều 20 - 24)

Trình tự: tiếp nhận, đăng ký (đóng dấu "Đến", ghi số đến và ngày đến), trình và chuyển giao, giải quyết và theo dõi, đôn đốc.
Sổ đăng ký văn bản đến tối thiểu 10 cột; sổ theo dõi giải quyết văn bản đến có hạn giải quyết và tiến độ. Khi dựng sổ bằng
Excel: dùng `excel-workbooks` (danh mục thả xuống cho đơn vị nhận, cột hạn và cột trễ hạn tính bằng công thức).

## Sao văn bản (Điều 25 - 27; Phụ lục I Phần II)

Ba hình thức: sao y, sao lục, trích sao; sao từ giấy sang điện tử và ngược lại. Bản sao đúng thể thức có giá trị pháp lý như
bản chính. Bản sao điện tử từ giấy: PDF bản 1.4 trở lên, ảnh màu, độ phân giải tối thiểu 200 dpi, tỷ lệ 100%; chữ ký số của
cơ quan ở góc trên bên phải trang đầu. Thẩm quyền sao do người đứng đầu quyết định hoặc theo quy chế.

## Hồ sơ và nộp lưu

- **Danh mục hồ sơ** (Điều 28; mẫu Phụ lục V): lập đầu năm, gồm số và ký hiệu hồ sơ, tên đề mục và tiêu đề hồ sơ, thời hạn bảo
  quản, người lập hồ sơ, ghi chú; cuối danh mục ghi số hồ sơ vĩnh viễn và có thời hạn.
- **Lập hồ sơ** (Điều 29): mở hồ sơ theo danh mục, thu thập văn bản trong quá trình giải quyết công việc, kết thúc hồ sơ khi
  việc xong; sắp xếp theo trình tự giải quyết.
- **Nộp lưu**: Luật Lưu trữ 2024 (Điều 17) yêu cầu nộp hồ sơ vào lưu trữ hiện hành trong 01 năm kể từ năm công việc kết thúc;
  hồ sơ nộp là bản gốc hoặc bản chính, đủ và theo trình tự. Đối chiếu với Điều 30 Nghị định 30 và quy chế đơn vị.
- **Thời hạn bảo quản**: vĩnh viễn hoặc có thời hạn từ 2 đến 70 năm tính từ năm công việc kết thúc; hồ sơ lấy thời hạn dài nhất
  của văn bản bên trong (Luật Lưu trữ 2024, Điều 15). Bảng thời hạn cụ thể theo ngành, lĩnh vực: tra văn bản của bộ ngành;
  không tự đặt thời hạn ngắn hơn mức tối thiểu.
- **Hủy tài liệu hết thời hạn**: lập danh mục, thành lập hội đồng, thẩm định, quyết định hủy; hủy hoàn toàn, không khôi phục
  được; hồ sơ về việc hủy giữ ít nhất 20 năm (Thông tư 06/2025/TT-BNV, theo bảng căn cứ). Không đề xuất hủy khi chưa có
  danh mục được duyệt.

## Cách làm

1. Hỏi gộp: đơn vị thuộc khu vực nào, có quy chế văn thư riêng không, dùng sổ giấy, Excel hay phần mềm.
2. Dựng sổ, danh mục hoặc quy trình theo mẫu trong `references/registers.md`, giữ tên cột như mẫu để người kiểm tra nhận ra.
3. Số liệu, thời hạn, thẩm quyền lấy từ căn cứ có trong bảng; thiếu thì ghi `[cần xác nhận]`.
4. Cuối lời giao: nêu văn bản căn cứ đã dùng, ngày đối chiếu, và điều chưa kiểm (ví dụ quy chế riêng của đơn vị).

## Thư viện nguồn của project

Project có `references/_INDEX.xlsx` thì tra ở đó trước (`python tools/library.py find <số hiệu hoặc từ khóa>`): có toàn văn thì
đọc file và trích nguyên văn; không có thì ghi "[chưa đối chiếu toàn văn]". Chỉ mục của project đứng trước bảng
`references/legal-basis.md` của gói (bảng của gói là mốc tham khảo chung). Văn bản dùng thường xuyên mà chưa có trong thư viện:
đề xuất người dùng tải bản chính thống về và thêm dòng chỉ mục (skill `source-library`).

## Kiểm trước khi giao

- Cột sổ đăng ký đủ tối thiểu theo mẫu; số văn bản không tự đặt.
- Thời hạn bảo quản có nguồn; không có thời hạn ngắn hơn mức tối thiểu của bảng ngành.
- Mỗi con số dẫn từ văn bản pháp luật có trong `references/legal-basis.md`, kèm ngày đối chiếu.
