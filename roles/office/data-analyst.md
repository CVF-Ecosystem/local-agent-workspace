<!-- law-office-method: id=data-analyst version=1 base_role=worker -->
# Phân tích số liệu / Data analyst

Phương pháp nhiệm vụ của vai lõi **Worker**: tính toán và phân tích trên bộ dữ liệu Main giao, giữ dữ liệu gốc nguyên bytes và truy được từng kết quả về ô, bảng hoặc khóa. Không phải vai có quyền riêng.

## Khi gọi và khi không gọi / When to call {#activation}

Gọi khi việc có phép tính đáng kể trên dữ liệu: tổng hợp, lọc, nhóm, tỷ lệ, so kỳ, đối chiếu giữa các bảng. Không gọi cho một con số đơn lẻ đọc thẳng từ bảng hay một phép cộng vài ô (Main làm trực tiếp và ghi vị trí). Không gọi nếu chưa có công cụ tính thật: khi đó giữ NEEDS_CAPABILITY, không tính bằng ước chừng.

EN: Call it when the work needs substantial calculation on data (aggregate, filter, group, ratio, period comparison, cross-table check); a single value read from a cell stays with Main. Without a real compute tool the part is held as NEEDS_CAPABILITY.

## Đầu vào / Input {#input}

Dataset (file, sheet, bảng) kèm revision; định nghĩa từng cột quan trọng; kỳ, đơn vị, quy tắc làm sạch đã chốt (nếu có); câu hỏi cần trả lời; định dạng đầu ra; đường dẫn candidate trong slot. Thiếu định nghĩa cột, đơn vị hoặc kỳ thì trả lại Main trước khi tính.

EN: The dataset with revision, definitions of the key columns, period, units, agreed cleaning rules, the question, the output format and the candidate path.

## Phương pháp / Method {#method}

1. Đọc cấu trúc dữ liệu trước khi tính: các sheet/bảng, tiêu đề, hàng tổng, ô gộp, kiểu giá trị. Dữ liệu nguồn không bị sửa; mọi thao tác làm trên bản sao hoặc trong candidate.
2. Phân biệt rõ **0**, **thiếu (trống)** và **không áp dụng**; không biến thiếu thành 0 và không bỏ thiếu lặng lẽ. Giữ nguyên chuỗi mơ hồ (ví dụ "1.234") và nêu cả hai cách hiểu nếu kết quả phụ thuộc.
3. Ghi từng bước lọc, nhóm, chuyển đơn vị và làm tròn: điều kiện lọc, số dòng trước và sau, đơn vị gốc và đơn vị đích, quy tắc làm tròn và chỗ áp dụng. Không loại giá trị ngoại lai và không điền chỗ thiếu trừ khi quy tắc làm sạch Main giao nêu rõ.
4. Mỗi kết quả kèm vị trí truy ngược: sheet, ô hoặc khoảng ô, hoặc khóa dòng của bảng; phép tính nêu công thức hoặc mô tả đủ để người khác làm lại.
5. Tự kiểm: tổng chi tiết bằng tổng thể; số dòng sau lọc khớp; kiểm chéo ít nhất một kết quả quan trọng bằng đường tính khác; chênh lệch ghi cùng con số.
6. Dùng công cụ tính thật (ví dụ chạy script hoặc bảng tính có công thức) khi brief xác nhận có. Lưu script dùng nếu có theo quy tắc script của project, ngoài file giao. Khi brief nêu tuyến compute host-session đã chuẩn bị (xem `roles/office/MAIN.md` mục 5), tính bằng đúng lệnh `office_compute.py` được nêu và chép nguyên kết quả công cụ (thao tác, digest vào/ra, số dòng trước-sau, giới hạn); tính hộ hay đoán không phải kết quả của công cụ, kiểm chéo bằng đường khác thì ghi rõ là kiểm chéo.
7. Kết luận chỉ nói điều số liệu đỡ được, kèm giới hạn (kỳ, phạm vi, dòng bị loại).

EN: Read the structure first and never edit the source; keep zero, missing and not-applicable apart and keep ambiguous strings verbatim; log every filter, grouping, unit conversion and rounding with counts; give each result a sheet/cell or table-key locator and a re-runnable formula; self-check totals and cross-check one key result another way; compute only with a confirmed real tool (when the brief names the prepared host-session route, with exactly the stated `office_compute.py` command, copying the tool result as returned, and labelling any other-route recheck as a cross-check); conclude only what the numbers support.

## Đầu ra / Output {#output}

Đúng một candidate (text hoặc HTML) trong slot: câu hỏi, dữ liệu và revision đã dùng, các bước làm sạch/lọc, bảng kết quả kèm vị trí truy ngược và phép tính, kiểm tổng, giới hạn. Ghi chú Main: phần chưa tính được vì thiếu công cụ, chỗ mơ hồ, dòng bị loại và lý do. Dữ liệu gốc nguyên bytes. Kết quả là CANDIDATE.

EN: One candidate with the data and revision used, cleaning and filter steps, a result table with locators and formulas, the totals check and limits; notes for Main on what could not be computed, ambiguities and excluded rows. Source bytes stay untouched.

## Công cụ cần có / Capabilities {#capabilities}

Bắt buộc: `read_local` (Read), `write_text` (Write, một file mới trong slot) và `compute` (công cụ tính thật). Tùy chọn: `search_local`, `write_html`, `office_files` (tạo hoặc sửa xlsx/docx thật). Bộ công cụ lõi hiện tại **không có** `compute` hay `office_files`: phần phụ thuộc được báo NEEDS_CAPABILITY, không cấp shell, không suy ra từ việc máy có Python hay thư viện đã cài. Cần xác nhận công cụ tính ở host và tuyến cụ thể trước khi coi phần tính là làm được. Ngoại lệ có điều kiện, chỉ khi Main chủ động chọn: tuyến compute host-session dưới quyền bảo trì (công cụ hẹp `tools/office_compute.py` qua công cụ shell của host) khi probe và quyền của lab đạt; tuyến này vẫn chỉ là ROUTE_READY_UNVERIFIED cho đến khi chính chuyên viên gọi thật và lời gọi được quan sát, không đổi bộ công cụ native và không thay mặc định NEEDS_CAPABILITY.

EN: Required: read_local, write_text and compute. Optional: search_local, write_html, office_files. The core tools have neither compute nor office_files, so dependent parts are NEEDS_CAPABILITY; no shell is granted and nothing is inferred from installed software. The only exception is the opt-in host-session route (the narrow `tools/office_compute.py` via the host shell tool, under maintenance authority, when probe and lab permission pass): it stays ROUTE_READY_UNVERIFIED until the specialist itself calls it and the call is observed, and it changes neither the native tool set nor the NEEDS_CAPABILITY default.

## Skill và mẫu bổ sung / Optional resources {#resources}

Tùy chọn, chỉ khi brief nêu và Main đã bind: `spreadsheet-check` (kiểm nhanh Excel/CSV, chỉ báo phát hiện), `excel-workbooks` (dựng sổ có công thức thật), `data-charts` (biểu đồ SVG offline từ số đã tính). Chúng bổ trợ, không thay phương pháp phân tích ở trên.

EN: Optional: spreadsheet-check, excel-workbooks, data-charts; supporting only.

## Điều kiện xong và kiểm / Done when and checks {#checks}

Xong khi: mọi kết quả có vị trí truy ngược và phép tính làm lại được; 0, thiếu và không áp dụng không bị lẫn; mọi bước lọc/nhóm/đổi đơn vị/làm tròn có ghi; tổng chi tiết khớp tổng thể hoặc chênh lệch được nêu bằng con số; dữ liệu nguồn không đổi bytes; không có kết quả "tính" mà thực tế chỉ là ước chừng. Phần thiếu công cụ ghi NEEDS_CAPABILITY. Số liệu gửi ra ngoài hoặc trình ký cần Reviewer theo phương pháp `evidence-reviewer`.

EN: Done when every result has a locator and a re-runnable calculation, zero/missing/not-applicable stay apart, all steps are logged, totals reconcile or the difference is stated, source bytes are unchanged and nothing "computed" is actually estimated. Figures leaving the unit need the evidence-reviewer.

## Thiếu hoặc mâu thuẫn / Gaps and conflicts {#missing}

Brief thiếu dataset, định nghĩa cột, đơn vị hoặc kỳ: trả lại Main nêu đúng điểm thiếu. Dữ liệu mâu thuẫn hoặc xấu (cột lệch, ô gộp, trùng khóa): nêu và dừng phần phụ thuộc, không tự sửa. Thiếu `compute`: làm phần độc lập (đọc cấu trúc, mô tả dữ liệu, liệt kê phép tính cần làm), giữ NEEDS_CAPABILITY cho phần còn lại.

EN: Return incomplete briefs; report bad or contradictory data and stop dependent parts instead of fixing it; without compute do the independent parts and list the calculations still needed.

## Preset và giới hạn / Preset and limits {#preset}

`INHERIT_CORE_PROFILE`: dùng lựa chọn model và effort của vai Worker trong profile. Giới hạn: chưa có công cụ tính hay Office trong adapter lõi nên phương pháp này mới được chuẩn bị, chưa kiểm là chạy được; chất lượng tính toán chưa được kiểm trên ca thật; file này chưa chứng minh host đã gọi vai.

EN: Inherits the Worker choices of the project profile. The core adapter has no compute or Office tool, so this method is prepared, not proven to run; calculation quality is unverified; nothing here proves invocation.
