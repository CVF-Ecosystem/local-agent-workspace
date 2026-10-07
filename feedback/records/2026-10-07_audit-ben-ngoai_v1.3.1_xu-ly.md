# Xử lý bản audit độc lập v1.3.1

Nguồn: `2026-10-07_audit-ben-ngoai_v1.3.1.md` (cùng thư mục, nguyên văn). Phiên bản được audit: v1.3.1, commit `06e56ff`.
Xử lý ở v1.3.2. File này ghi cái đã sửa, cái chưa kiểm được và cái không đồng ý, để agent local audit tiếp.

## 1. Đã xác nhận bằng chạy mã thật rồi sửa

| Mã | Xác nhận | Sửa |
|---|---|---|
| F01 | Bảng 2–3 dòng có `Total = 999` không báo gì; 4 dòng thì báo. | `check_spreadsheet.py`: phép đối chiếu dòng Tổng tách khỏi điều kiện `>= 4` mẫu (chỉ phần âm/lệch xa giữ điều kiện). |
| F03 | `stack()` dùng `values[i]\|\|0`: thành phần thiếu thành 0, tổng vẫn hiện đủ. | `basic-charts.html` (VI+EN): thành phần thiếu không vẽ; cột thiếu ghi "≥ tổng phần đã biết", bảng dữ liệu cũng vậy. |
| F04 | Chuỗi hằng hoặc một kỳ: chia cho `hi-lo` và `n-1` ra NaN. | Mở khoảng trục khi `hi<=lo`; một kỳ thì đặt giữa khung; toàn null thì ghi "chưa có dữ liệu". Nhãn "tháng 6", "20 hồ sơ tồn" chuyển thành `period`/`note` trong dữ liệu. |
| F05 | `check_output.py` nhánh CSV/XLSX bỏ qua mã thoát của checker con. | Mã thoát khác 0 thì in "LỖI CÔNG CỤ ... KHÔNG kiểm được" và tính vào lỗi (mã thoát 1). |
| F06 | Thiếu một cột của khóa ghép vẫn báo trùng, không cảnh báo thiếu. | Thêm dòng "Cần hỏi": chỉ thấy cột X, thiếu Y; chưa kiểm được khóa ghép đầy đủ. |
| D03 (một phần) | Đoạn dán cloud ghi skill "không bắt buộc", thiếu khối khai báo, liệt kê 10/11 skill (thiếu `vn-admin-documents`), tên ZIP `v1.0.0` cứng. | Đồng bộ với AGENTS.md (đọc SKILL.md khi khớp, khối Khai báo thực hiện, đủ 11 skill, `vX.Y.Z`). |
| D01 (một phần) | Câu tuyệt đối "Không có vòng soát thứ hai", "Chỉ một lần tự sửa", "tối đa một vòng chỉnh" trong doc-coauthoring. | Thêm ngoại lệ: lỗi cụ thể thì sửa đúng chỗ và kiểm lại chỗ đó; người dùng muốn chỉnh thêm thì chỉnh. |
| F02 (hạ mức) | Có thật nhưng hẹp: chỉ xảy ra khi người dùng bỏ qua tên project, điền các mục khác rồi mới đổi sang tiếng Anh. | `init_project.py`: file khác bản gốc luôn được sao lưu `.bak-<giờ>` trước khi thay, kể cả file mẫu người dùng. |

Đã chạy lại: F01 (2, 3, 4 dòng; tổng đúng không báo), F06 (thiếu cột, đủ cột, bản EN), F05 (xlsx hỏng cho mã thoát 1, CSV có phát hiện vẫn mã 0), F03/F04 bằng node với DOM giả (ba ca: hằng, một kỳ, toàn null; ca thành phần null).

## 2. Không đồng ý hoặc đồng ý một phần

- **F02 xếp "sớm":** hạ xuống "vừa" (lý do ở trên). Nếu agent local muốn kiểm kỹ: `pristine()` coi PROJECT là bản mẫu khi còn dòng `- Tên dự án: [Tên]`; tên được điền ngay lúc `init`, nên ca lỗi cần bỏ qua bước đó.
- **F06 nặng hơn thực tế:** thông báo cũ đã ghi "trùng theo cột Ma", nên người đọc biết khóa thực dùng; thiếu là dòng cảnh báo.
- **D01, đề xuất thay đoạn hướng dẫn:** không nhận câu "Khi đã chọn một skill, đọc hướng dẫn". Ở v1.1.0 và v1.2.0 khi quy tắc chỉ là gợi ý, các mô hình bỏ qua skill (H1, `feedback/records/2026-10-06_gemini_demo-project_v1.2.0.md`). Chỉ nhận phần làm mềm các câu tuyệt đối.

## 3. Chưa kiểm được, cần agent local audit

1. **F07:** `/releases/latest` trả 404 vì bản v1.3.1 là pre-release. Không có quyền vào GitHub từ phiên làm việc này. Cần xem Release thật: ô "pre-release" đã bật chưa. Tùy chọn: bỏ dấu để thành stable, hoặc đổi link README sang trang Releases.
2. **D02 (bốn skill gốc external):** audit dựa vào cuộc trao đổi trước, không có trong phiên này. Chưa sửa gì. Lưu ý giấy phép: `lieflat-charts` ghi PolyForm Noncommercial License 1.0.0 (xem `docs/NGUON_THAM_KHAO_VI.md`), nên nhập vào gói phải giữ đúng điều khoản và ghi rõ giới hạn phi thương mại. Cần người dùng quyết định có nhập hay không.
3. **D03, phần còn lại:** audit nói mục giới hạn kiểm tra còn ghi "chưa thử trong ứng dụng" trong khi feedback đã có thử mô hình/môi trường cụ thể. Chưa đối chiếu câu chữ này; cần đọc lại và phân biệt đã thử (ba mô hình, một lần mỗi mô hình) với chưa thử (Codex, Windows `SETUP.bat`, người dùng thật).
4. **Chưa chạy thật:** tệp `.xlsx` có ô null trong biểu đồ, khóa ghép trên `.xlsx` nhiều sheet, giao diện HTML biểu đồ trong trình duyệt thật (chỉ chạy bằng node với DOM giả, chỉ kiểm không có NaN và có nhãn "≥").
5. **Chưa có bằng chứng:** việc agent thật, sau khi đã sửa, có đọc đúng dòng cảnh báo mới (F05, F06) hay không. Cần một lần thử mới ngoài dữ liệu demo: bảng ngắn có Tổng, bảng thiếu cột khóa, chuỗi số không đổi, biểu đồ thiếu thành phần, PROJECT điền dở khi đổi ngôn ngữ (đúng danh sách gợi ý của audit mục 5).
6. **Chất lượng audit:** tác giả audit không chạy end-to-end, chép logic ra; chỉ F01 và F06 được chạy lại trên bản thật trước khi sửa, F02–F04 mới xác nhận bằng đọc mã.
