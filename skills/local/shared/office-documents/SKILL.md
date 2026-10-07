---
name: office-documents
description: >-
  Gợi ý soạn hoặc chỉnh tài liệu nghiệp vụ tiếng Việt từ nguồn và mẫu có sẵn:
  quy trình/SOP, biểu mẫu, hướng dẫn, thông báo hoặc báo cáo tiến độ. Hữu ích khi
  cần tổ chức nội dung theo người đọc và công việc; sửa câu đơn giản có thể làm trực tiếp.
  Kích hoạt khi người dùng nói: “soạn quy trình”, “SOP”, “biểu mẫu”, “hướng dẫn nội bộ”, “chỉnh tài liệu theo mẫu”.
metadata:
  version: "1.0"
---

# Tài liệu nghiệp vụ

Bổ sung cách tổ chức nội dung và mẫu tham khảo, không thay thế năng lực đọc tài liệu
hay tạo DOCX/PDF/Excel sẵn có. Linh hoạt theo mục đích và nguồn thực tế.

## Cách tiếp cận gợi ý

Bắt đầu từ tài liệu/mẫu người dùng chỉ định và phần việc cần làm. Tận dụng thông tin
về người đọc, mục đích, đầu ra đã có; chỉ làm rõ điểm thiếu ảnh hưởng đến kết quả.
Nếu đã có đủ nguồn, có thể soạn ngay thay vì mở một vòng thu thập yêu cầu mới.

Với quy trình, giúp người thực hiện hiểu ai làm gì, khi nào, với đầu vào/đầu ra nào.
Thêm ngoại lệ hoặc điểm chuyển tiếp khi nguồn có quy định hoặc công việc cần làm rõ.
Với biểu mẫu, ưu tiên những trường phục vụ việc ghi nhận và sử dụng thực tế.
Với cập nhật nội bộ, đưa thông tin quan trọng và việc cần người đọc hành động lên trước.

Khi chỉnh tài liệu, giữ phần đã chốt và sửa đúng phạm vi. Phân biệt căn cứ trong
nguồn, quyết định đã xác nhận, và nội dung đang đề xuất. Không tự đặt thêm thời hạn,
vai trò, điều kiện hay thẩm quyền để lấp chỗ trống.

Bản cập nhật ngắn người đọc xem trong một phút (báo cáo tuần, thông báo, FAQ, sự cố) thuộc
`internal-comms`. Dùng skill này khi tài liệu có nhiều mục, cần cấu trúc hoặc sẽ trở thành
quy trình/biểu mẫu dùng lâu dài.

## Mẫu khi cần

Chọn mẫu phù hợp hoặc dùng mẫu của dự án; không cần mở hết:

- `references/procedure-template.md`: khung gợi ý cho SOP/quy trình.
- `references/form-template.md`: phiếu ghi nhận, yêu cầu hoặc xử lý.
- `references/internal-update-template.md`: cập nhật tiến độ, vấn đề và việc cần quyết định.
- `references/delivery-checklist.md`: checklist ngắn trước khi giao (kèm `tools/check_output.py` cho phần cơ học).
- `references/report-writing.md`: văn phong và khung báo cáo định kỳ, đề án đầu tư, công văn, tờ trình.
- `references/procedure-document.md`: tài liệu quy trình kèm sơ đồ tổ chức cấp phòng ban (mã tài liệu, ký duyệt, mục lục).
- `references/proposal-review.md`: đánh giá và sửa đề án hoặc quy chế nội bộ có sẵn.
- `references/form-standardization.md`: chuẩn hóa hàng loạt biểu mẫu và tài liệu cũ.
- `references/word-technical-notes.md`: lưu ý kỹ thuật khi dựng hoặc sửa file Word.
- Sổ theo dõi, form nhập liệu và phụ lục tính bằng Excel: `excel-workbooks`; công cụ HTML đọc file Excel: `excel-html-viewer`.

Các khung dùng chỗ trống, không chứa chính sách được phê duyệt. Có thể bỏ, đổi hoặc
kết hợp mục theo yêu cầu; không cần làm tài liệu dài hơn chỉ để điền đủ khung.

## Giữ nguyên nội dung khi chuyển dạng hoặc sửa tại chỗ

Khi người dùng yêu cầu "giữ nguyên nội dung" (chuyển văn xuôi sang bảng, đổi mẫu, chuẩn hóa định dạng, sửa tại chỗ), làm đủ ba việc:

1. **Đếm trước**: ghi số ảnh, số bảng, số ký tự chữ, số bước/mục/dòng của file gốc. Với Word có thể dùng:
   `python -c "import zipfile,re,sys;z=zipfile.ZipFile(sys.argv[1]);x=z.read('word/document.xml').decode('utf8');print('anh',len([n for n in z.namelist() if n.startswith('word/media/')]),'bang',x.count('<w:tbl>'),'ky_tu',len(re.sub(r'<[^>]+>','',x)))" file.docx`
2. **Đếm sau** trên file mới bằng đúng cách đó. Lệch ảnh, bảng hoặc quá khoảng 10% ký tự thì tìm nguyên nhân: nếu là phần bị mất thì dựng lại từ file gốc (chép lại ảnh, bảng, ghi chú), không giao.
3. **Báo trong lời giao** một bảng "trước → sau" (ảnh, bảng, ký tự, bước) và nói rõ phần nào chủ ý bỏ. Đếm số bước chỉ trong phần đã trích ra thì không chứng minh được "không mất nội dung"; phải đếm trên toàn file gốc.

Dựng file mới bằng cách chỉ chép lại phần chữ dễ làm rơi ảnh, bảng lồng, đầu trang/chân trang và ghi chú; ưu tiên sửa trực tiếp bản sao của file gốc.

## Đầu ra phù hợp

Yêu cầu nháp thì giao nháp; yêu cầu file dùng được thì chọn công cụ định dạng phù
hợp và xem những điểm cần cho việc sử dụng. Đối chiếu đúng phần nguồn khi nội dung
quan trọng phụ thuộc vào nó. Không cần reader-testing bằng agent khác hoặc vòng
brainstorm nhiều phương án nếu nhiệm vụ không cần.

Khi nội dung đúng phạm vi, người đọc sử dụng được và điểm thiếu đã nêu rõ, dừng.
Không tự thêm bản giải trình, bản so sánh hoặc vòng biên tập văn phong.
