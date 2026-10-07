# Hướng dẫn sử dụng hằng ngày

Local Agent Workspace v1.4 giúp giữ tài liệu, ngữ cảnh và kết quả công việc trên
cùng một thư mục. Agent vẫn chủ động chọn cách làm, công cụ và skill phù hợp.

## 1. Giao việc bằng ngôn ngữ tự nhiên

Nói rõ việc cần làm, nguồn nếu có và dạng đầu ra mong muốn. Bạn không cần nhớ tên
skill, cú pháp hay chọn một chế độ trước khi làm việc.

```text
Dựa vào Quy_dinh_tiep_nhan.docx, soạn bản nháp quy trình tiếp nhận hồ sơ.
Dùng mẫu quy trình hiện có của project. Chỗ chưa đủ căn cứ thì đánh dấu để tôi xác nhận.
Chưa cần xuất Word.
```

Với việc nhỏ, chỉ cần nói điều cần sửa:

```text
Sửa đoạn này cho gọn, giữ nguyên số liệu và tên bộ phận. Trả ngay bản đã chỉnh.
```

Agent có thể làm trực tiếp nếu ngữ cảnh đã đủ. Không cần đọc STATE, tìm skill hay
lập kế hoạch chỉ vì đây là một project có workspace.

## 2. Tiếp tục công việc đang dở

Khi nhiệm vụ phụ thuộc vào dự án, `PROJECT.md` cung cấp thông tin ổn định và
`.agent/STATE.md` cho biết đang làm đến đâu. `HANDOFF.md` chỉ có ích khi cần bàn giao.

```text
Tiếp tục việc đang dở trong STATE. Hoàn thiện phần hướng dẫn điền biểu mẫu;
đừng viết lại các trường đã chốt. Dùng HANDOFF nếu có nội dung bàn giao.
```

Không cần yêu cầu agent đọc toàn bộ lịch sử. Khi chưa biết nguồn nằm ở đâu, index
có thể giúp tìm; khi bạn chỉ đúng file, có thể mở file đó trực tiếp.

## 3. Yêu cầu nháp và yêu cầu file là hai việc khác nhau

| Bạn cần | Cách giao việc |
|---|---|
| Duyệt nội dung trước | “Soạn bản nháp trong hội thoại, chưa xuất file.” |
| File hoàn chỉnh để dùng | “Tạo file Word theo mẫu, lưu vào output/.” |
| Sửa cục bộ | “Chỉ sửa mục 3, giữ phần còn lại.” |
| Báo cáo HTML | “Tạo một file HTML mở offline từ bảng này, có bộ lọc theo kênh.” |

Yêu cầu file dùng được bao gồm việc hoàn thành file và kiểm tra những điểm cần cho
việc sử dụng. Không mặc định dừng ở bản nháp, cũng không mặc định mở vòng test/sửa dài.
Không có chế độ làm việc bắt buộc.

## 4. Dùng nguồn và mẫu

Có thể đặt nguồn trong `references/` hoặc giữ nguyên vị trí đang dùng. Khi hữu ích,
`.agent/INDEX.md` ghi nguồn nào nằm ở đâu và dùng cho việc gì.

Mẫu của đơn vị và quy định đã xác nhận có giá trị nghiệp vụ. Mẫu đi kèm skill chỉ
là ví dụ để tham khảo, không tự trở thành quy định. Agent nên nêu điểm thiếu, thay
vì tự đặt thêm vai trò, thời hạn hoặc thẩm quyền.

Khi nguồn đã được đọc, có thể tận dụng phần liên quan trong ngữ cảnh. Nếu nguồn
vừa sửa hoặc kết luận phụ thuộc một điều khoản, đối chiếu lại đúng phần cần thiết.

## 5. Để agent chọn skill phù hợp

Workspace có mười ba skill gợi ý, từ soạn tài liệu (`office-documents`, `internal-comms`,
`doc-coauthoring`), phân tích (`document-comparison`, `spreadsheet-check`), biểu đồ và báo cáo
(`data-charts`, `html-reports`), quy trình và họp (`process-mapping`, `meeting-minutes`), văn bản
hành chính đúng thể thức (`vn-admin-documents`), sổ và công cụ Excel (`excel-workbooks`, `excel-html-viewer`) đến biên tập (`vietnamese-editing`). Bạn không phải gọi chúng bằng tên.

Agent có thể dùng native skill, skill của workspace, kết hợp hoặc không dùng skill.
Tiêu chí là độ phù hợp với công việc và khả năng thực có, không phải nơi cung cấp.
`ACTIVE` trong index không có nghĩa skill cần nạp ở mọi phiên.

Chi tiết và ví dụ nằm trong `HUONG_DAN_SKILLS_VI.md` cùng thư mục.

## 6. Dùng với Claude, Codex và Gemini qua Antigravity

Mở hoặc cấp quyền thư mục dự án bằng khả năng hiện có của ứng dụng. Nếu agent chưa
đọc hướng dẫn chung, có thể gửi:

```text
Thư mục này dùng Local Agent Workspace. Tham khảo AGENTS.md và thông tin liên quan
trong PROJECT.md. Dùng STATE khi tiếp tục công việc đang dở. Chọn công cụ hoặc skill
phù hợp nhất với yêu cầu; có thể làm trực tiếp khi đã đủ thông tin.
```

`CLAUDE.md` và `GEMINI.md` là adapter mỏng cho môi trường hỗ trợ cách đọc tương ứng.
Không giả định Gemini CLI và Antigravity nạp file giống nhau. Khi chưa tự nạp,
chỉ đường dẫn `AGENTS.md` cho agent là cách bắt đầu rõ ràng.

Các skill trong package được tra cứu như file; giải nén không tự cài chúng vào
thư viện native của các ứng dụng. Một native skill có ở phiên này không bảo đảm
có ở phiên khác. Package không sửa cấu hình toàn cục của provider.

Nếu agent không có quyền đọc/ghi thư mục, cần cấp quyền hoặc đưa đúng file vào phiên
bằng cơ chế của ứng dụng; không xem một câu hướng dẫn là đã tạo kết nối.

## 7. Lưu kết quả và kết thúc phiên

`working/` giữ bản đang làm; `output/` giữ bản giao hiện hành; `archive/` giữ bản cũ
khi cần. Giữ nguyên tài liệu nguồn và chỉ thay thế khi bạn đã yêu cầu.

Không cần checkpoint sau mỗi câu trả lời. Ghi STATE khi có quyết định đã chốt,
đầu ra mới hoặc bước tiếp theo mà phiên sau cần biết. Dùng HANDOFF khi cần bàn giao
ngắn; để `None` khi không dùng. PENDING_LESSONS chỉ là chỗ tùy chọn cho kinh nghiệm
thực sự có thể dùng lại.

Báo rõ nếu file chưa lưu thành công vào nơi dự kiến. Giữ file ở local không có
nghĩa mô hình xử lý hoàn toàn offline hoặc mọi đầu ra cloud tự trở về máy.

## 8. Khi agent bắt đầu làm quá nhiều

Thu hẹp lại bằng một yêu cầu cụ thể, chẳng hạn:

```text
Chỉ hoàn thiện phần tôi vừa yêu cầu. Không cần thêm phương án hoặc chuẩn hóa
phần khác. Khi bản đó đã dùng được thì dừng.
```

Nếu agent thiếu thông tin quan trọng, để nó đọc thêm đúng nguồn hoặc hỏi đúng điểm.
Mục tiêu là làm vừa đủ để đúng việc, không phải bỏ qua kiểm tra cần thiết.

`AGENTS.md` có khối "Giới hạn công việc": việc nhỏ làm một lần, việc vừa một lượt kèm tối đa một
lần soát (lỗi cụ thể thì sửa đúng chỗ), không lặp vô hạn, hỏi gộp một lần. Nếu môi trường (đặc biệt là cloud) không
tự đọc `AGENTS.md`, dán đoạn hướng dẫn trong mục 5 của `HUONG_DAN_TAO_PROJECT_MOI_VI.md`
vào phần hướng dẫn của Project.

Với việc có hậu quả cao (pháp lý, tài chính, số liệu hoặc văn bản gửi ra ngoài, trình ký), agent
áp dụng "Mức thận trọng cao" trong `AGENTS.md`: đối chiếu từng số, ngày, tên, điều khoản với nguồn,
nêu phần chưa kiểm được. Bạn có thể nhắc: "Việc này gửi ra ngoài, áp dụng mức thận trọng cao."

## 9. Dữ liệu nhạy cảm và ghi nhận phần AI hỗ trợ

Trước khi đưa tài liệu cho AI, tự hỏi: file này có mật khẩu, khóa truy cập, dữ liệu cá nhân của khách hàng hoặc nhân sự, hay
tài liệu mật không? Nếu có, che hoặc bỏ phần đó trước (thay tên thật bằng ký hiệu, xóa số định danh), và ghi mức nhạy cảm vào
dòng "Mức nhạy cảm dữ liệu" trong `PROJECT.md`. Tuân thủ quy định bảo mật của đơn vị; package không thay thế các quy định đó.

Package giữ file ở máy bạn, nhưng khi mở bằng ứng dụng AI thì nội dung bạn giao vẫn được ứng dụng đó xử lý theo điều khoản của
nó. Không dùng project này cho dữ liệu mà quy định của đơn vị cấm đưa vào dịch vụ AI.

Với văn bản gửi ra ngoài hoặc trình ký, người ký chịu trách nhiệm về nội dung: nên đọc lại toàn bộ và đối chiếu số liệu với nguồn.
Nếu đơn vị yêu cầu ghi nhận phần AI hỗ trợ, thêm một dòng vào hồ sơ (ví dụ: "Bản nháp có hỗ trợ của AI, đã được [tên] rà soát").

## 10. Đọc "Khai báo thực hiện" của agent

Khi agent đọc, kiểm tra, đối chiếu hoặc tính toán trên file của bạn, cuối câu trả lời nên có khối "Khai báo thực hiện"
(quy tắc 9 trong `AGENTS.md`): cách làm (script đã chạy kèm lệnh, hay đọc thủ công), skill đã đọc, nguồn đã đọc, file đã tạo hoặc sửa,
và điều chưa kiểm. Hãy đọc khối này trước khi tin kết quả. Phát hiện về số nên kèm con số cụ thể; chỗ mơ hồ (như `1.234`) nên được
nêu cả hai cách hiểu. Thiếu khối này, hoặc khai báo chung chung, thì yêu cầu agent bổ sung. Khai báo do agent tự ghi nên không phải
bằng chứng tuyệt đối; với việc quan trọng, dòng "Dấu vết" của script (file, sha256, giờ chạy) giúp bạn đối chiếu được.
Lưu câu trả lời thành file rồi chạy `python tools/check_output.py --declaration <file>` để kiểm khai báo đủ mục hay chưa.

## 11. Vai trò của các hướng dẫn HTML

`START_HERE.html` tập hợp cẩm nang cho người dùng; mỗi hướng dẫn Markdown cũng có
bản HTML cùng tên. Chỉ cần đọc một dạng. Agent không cần nạp HTML, đọc toàn bộ README
hoặc cập nhật bản HTML trong mỗi công việc văn phòng.

Khi bạn chủ động sửa hướng dẫn Markdown và muốn cập nhật bản trình bày, chạy
`python tools/build_guides_html.py` từ thư mục gốc của project (xem `tools/README.md`), hoặc nhờ
agent chạy giúp. Bản HTML không tự đồng bộ khi sửa Markdown; thêm `--check` để kiểm tra HTML
có còn khớp không.
