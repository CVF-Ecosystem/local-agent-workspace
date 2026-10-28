# Chọn và sử dụng kỹ năng

Bạn chọn trợ lý AI nào thì trợ lý AI đó dùng năng lực và kỹ năng sẵn có của ứng dụng (native) của nó; bộ công cụ không thay
hay sửa chúng. Kỹ năng trong bộ công cụ là hướng dẫn và tài nguyên **bổ sung**: mẫu, nguồn, quy tắc nghiệp
vụ mà native chưa có. Trợ lý AI chọn theo độ phù hợp với công việc, không ép dùng kỹ năng của bộ công cụ khi
cách sẵn có đã đủ.

## 1. Khi nào một kỹ năng có ích?

Một kỹ năng đáng dùng khi có mẫu, kinh nghiệm hoặc cách xử lý giúp hoàn thành yêu cầu
rõ hơn, nhanh hơn hoặc ít phải làm lại hơn. Không cần gọi kỹ năng chỉ vì nhiệm vụ có
một từ khóa giống tên kỹ năng.

| Công việc | Cách lựa chọn có thể phù hợp |
|---|---|
| Sửa một câu trong thông báo | Làm trực tiếp. |
| Soạn SOP từ quy định và mẫu nội bộ | Dùng nguồn/mẫu của dự án; tham khảo `office-documents` khi hữu ích. |
| Soạn đề xuất hoặc báo cáo dài cần trao đổi sâu | Cân nhắc `doc-coauthoring` khi người dùng muốn cùng trao đổi và soạn từng phần; nếu đã đủ nguồn có thể soạn trực tiếp. |
| Tạo Word/PDF từ nội dung đã duyệt | Dùng công cụ hoặc kỹ năng sẵn có (native) định dạng phù hợp; không phải soạn lại nội dung. |
| Vẽ biểu đồ từ bảng số liệu | Cân nhắc `data-charts`; kiểm tra bảng bằng `spreadsheet-check` nếu dữ liệu chưa sạch. |
| Làm báo cáo HTML từ dữ liệu | Cân nhắc `html-reports`, kỹ năng sẵn có (native) hoặc báo cáo cũ đang có. |
| Chỉnh văn phong một báo cáo | Cân nhắc `vietnamese-editing`; không mặc định sửa toàn bộ tài liệu. |
| So bản quy định mới với bản cũ | Cân nhắc `document-comparison`. |
| Lập biên bản từ ghi chú họp | Cân nhắc `meeting-minutes`. |
| Mô tả quy trình, phân vai, sơ đồ | Cân nhắc `process-mapping`, kết hợp `office-documents` khi viết thành tài liệu. |
| Báo cáo tuần, thông báo, bản tin, FAQ, báo cáo sự cố | Cân nhắc `internal-comms`. |
| Công văn, tờ trình, báo cáo gửi cơ quan khác hoặc trình ký | Cân nhắc `vn-admin-documents`; dùng quy chế văn thư của đơn vị trước nếu có. |
| Dựng sổ theo dõi, form nhập liệu hoặc phụ lục tính bằng Excel | Cân nhắc `excel-workbooks` khi cần công thức và báo cáo tự cập nhật; kiểm tra dữ liệu có sẵn bằng `spreadsheet-check`. |
| Dashboard offline đọc file Excel của người dùng | Cân nhắc `excel-html-viewer`; biểu đồ theo `data-charts`. |

Đây là ví dụ lựa chọn, không phải bảng định tuyến bắt buộc. Trợ lý AI có thể kết hợp
kỹ năng khi chúng bổ sung nhau hoặc xử lý trực tiếp nếu đã đủ khả năng.

## 2. Kỹ năng tài liệu nghiệp vụ

`skills/local/shared/office-documents/SKILL.md` cung cấp gợi ý và ba khung ngắn:
SOP/quy trình, biểu mẫu, cập nhật nội bộ. Chọn phần phù hợp, không cần điền tất cả.

```text
Từ tài liệu quy định này, tạo biểu mẫu ghi nhận yêu cầu. Dùng mẫu nội bộ nếu phù hợp;
có thể tham khảo office-documents. Không tự thêm thông tin phải thu thập ngoài nhu cầu.
```

Khung đi kèm không chứa quy định thật của đơn vị. Dữ kiện và điều khoản nghiệp vụ
vẫn đến từ nguồn hoặc quyết định được xác nhận, không từ ví dụ trong kỹ năng.

## 3. Kỹ năng báo cáo HTML

`skills/local/shared/html-reports/SKILL.md` đi kèm hai file có thể mở thử:

| Mẫu | Vị trí bên trong kỹ năng | Gợi ý sử dụng |
|---|---|---|
| Báo cáo định kỳ | `assets/periodic-report.html` | Báo cáo tháng/tuần có nhận xét, KPI, diễn biến và bảng số liệu. |
| Tổng quan chỉ số | `assets/metrics-overview.html` | Trang KPI có lọc theo kỳ/kênh và bảng chi tiết. |

Cả hai mẫu là HTML tự chứa, viết mới cho bộ công cụ, dùng font hệ thống và không cần
mạng. Dữ liệu trong bản mẫu là **minh họa**, không phải dữ liệu của dự án.

```text
Dùng bảng số liệu này để tạo một báo cáo HTML mở offline trong output/.
Chọn mẫu hoặc cách trình bày phù hợp nhất. Giữ đúng số liệu, ghi nguồn và kỳ báo cáo.
```

Trợ lý AI có thể thay khối `report-data` trong file mẫu rồi chỉnh bố cục và nhận xét.
Bạn không cần sửa mã để sử dụng kỹ năng: giao dữ liệu và yêu cầu cho trợ lý AI là đủ.
Nút lọc chỉ thay cách xem dữ liệu trong file; mẫu không kết nối dữ liệu sống.

Hai mẫu hỗ trợ in qua nút “In báo cáo”. Mở được offline không có nghĩa quá trình
trợ lý AI đọc dữ liệu và tạo báo cáo cũng diễn ra hoàn toàn offline.

## 4. Kỹ năng biểu đồ

`skills/local/shared/data-charts/SKILL.md` dành cho yêu cầu “vẽ biểu đồ” từ một bảng số
liệu. Kỹ năng đi kèm `assets/basic-charts.html` (thẻ KPI, biểu đồ đường, cột ngang, cột
xếp chồng, vành khuyên, bảng kèm thanh) và `references/chart-selection.md` để chọn dạng biểu
đồ theo dữ liệu. Biểu đồ là SVG thuần, mở offline, mỗi hình có bảng dữ liệu gập kèm theo.

```text
Vẽ biểu đồ từ bảng số liệu này, lưu thành một file HTML mở offline trong output/.
Chọn dạng biểu đồ phù hợp cho từng thông điệp; ghi rõ đơn vị, kỳ và nguồn.
```

Khác với `html-reports` (khung trang báo cáo có nhận xét), `data-charts` tập trung vào
chính biểu đồ. Hai kỹ năng dùng được cùng nhau khi cần một báo cáo có biểu đồ.

## 5. Kỹ năng biên tập tiếng Việt

`skills/local/shared/vietnamese-editing/SKILL.md` hữu ích khi có yêu cầu rõ về văn
phong. Nó hướng đến giữ nghĩa, số liệu, thuật ngữ và mức độ chắc chắn, không “khử
AI” bằng cách thay dấu câu hoặc làm nội dung mất tính nghiệp vụ. Khi cần nhận ra văn
phong khuôn mẫu, kỹ năng có `references/machine-style-signs.md`.

```text
Biên tập phần tóm tắt này cho rõ và bớt sáo rỗng. Giữ nguyên số liệu và mức độ
chắc chắn của nhận định; chỉ trả bản đã chỉnh.
```

Không cần tự chạy kỹ năng này sau mọi báo cáo hoặc SOP.

## 6. Các kỹ năng cho công việc hằng ngày

Chín kỹ năng này ngắn, mỗi kỹ năng có phần “khi nào dừng” để trợ lý AI không làm quá phạm vi.

| Kỹ năng | Dùng khi | Đầu ra điển hình |
|---|---|---|
| `document-comparison` | Có hai phiên bản của một tài liệu. | Bảng thay đổi: mục, cũ, mới, loại, tác động (nếu có căn cứ). |
| `spreadsheet-check` | Sắp lấy số từ Excel/CSV cho báo cáo. | Danh sách phát hiện theo mức ảnh hưởng; không sửa file gốc. |
| `meeting-minutes` | Có ghi chú hoặc bản ghi cuộc họp. | Quyết định, việc cần làm (ai/hạn nếu có), vấn đề chưa chốt. |
| `process-mapping` | Cần mô tả hoặc rà soát quy trình. | Bảng bước, RACI khi cần, sơ đồ Mermaid/SVG khi cần. |
| `internal-comms` | Cần viết cho người trong đơn vị đọc nhanh. | Báo cáo tiến độ (Tiến độ - Kế hoạch - Vấn đề), thông báo, bản tin, FAQ, báo cáo sự cố. |
| `doc-coauthoring` | Tài liệu lớn, muốn trao đổi sâu từng bước. | Dàn ý đã duyệt, các mục soạn theo từng phần, một lượt soát cuối. |
| `vn-admin-documents` | Cần văn bản hành chính đúng thể thức. | Bản nháp có đủ thành phần thể thức; số, ngày, người ký để `[cần xác nhận]`. |
| `excel-workbooks` | Cần sổ theo dõi, form nhập liệu hoặc phụ lục tính bằng Excel. | File có sheet nhập, báo cáo bằng công thức và dữ liệu mẫu tách riêng; cần tính lại và kiểm không lỗi. Nếu chưa tính lại, ghi rõ chưa kiểm, không coi file đã đạt. |
| `excel-html-viewer` | Muốn xem số liệu trực quan từ file Excel mà không cài phần mềm. | Một file HTML mở offline, đọc Excel, có tab kiểm tra dữ liệu; nêu rõ giới hạn khi giao. |
| `source-library` | Lưu và tra văn bản pháp luật, quy chế, mẫu biểu của dự án; cần biết văn bản còn hiệu lực, đã xác minh tới đâu. | Khung `references/` theo nhóm và lĩnh vực, chỉ mục `_INDEX.xlsx`, lệnh `tools/library.py` (init, check, find); trích dẫn chỉ từ file có trong thư viện. |

```text
Đối chiếu Quy_dinh_cu.docx với Quy_dinh_moi.docx. Chỉ lập bảng thay đổi có ý nghĩa,
ưu tiên số liệu, thời hạn, vai trò. Chỗ chưa rõ tác động thì ghi "cần xác nhận".
```

`spreadsheet-check` có kèm script `scripts/check_spreadsheet.py` (chỉ đọc; CSV không cần cài gì, Excel cần
`openpyxl`; thêm `--lang en` để báo cáo bằng tiếng Anh). `vn-admin-documents` chỉ là điểm xuất phát về thể thức: quy định văn thư có thể đã đổi và đơn vị
có thể có quy chế riêng, nên kiểm bản hiện hành trước khi ban hành.

`doc-coauthoring` phù hợp khi bạn muốn trao đổi sâu và soạn từng phần; nếu yêu cầu đã đủ nguồn, trợ lý AI có thể soạn thẳng.
Nếu cách làm này chưa được chọn, trợ lý chỉ đề xuất một lần để bạn chọn; không hỏi lại khi bạn đã chọn cùng soạn từng phần.
Các kỹ năng khác chỉ được dùng khi phù hợp với yêu cầu và trong phạm vi đã giao.

## 7. Cách trợ lý AI tìm kỹ năng

`.agent/SKILL_INDEX.md` có mô tả khi nào hữu ích và đường dẫn đến từng kỹ năng. Trợ lý AI
có thể tra khi cần khám phá hoặc mở trực tiếp khi đã biết kỹ năng phù hợp.

`AVAILABLE` nghĩa đã được nhận và sẵn dùng, `ACTIVE` nghĩa thường dùng trong dự án. Cả hai đều
không yêu cầu nạp đầu phiên. `REVIEW` là **thử nghiệm**: chưa qua tiếp nhận, trợ lý AI chỉ dùng thử trong
dự án và nói rõ là bản thử, công cụ không chép nó sang ứng dụng. Ghi chú native chỉ mô tả khả năng
đã biết của một môi trường; khi chuyển trợ lý AI, dùng những khả năng thực có trong phiên mới.

Bộ công cụ không tự cài các kỹ năng vào menu native của ứng dụng. Khi cần, chỉ đường dẫn:

```text
Skill bổ sung của project được mô tả trong .agent/SKILL_INDEX.md.
Chỉ tham khảo skill có ích cho việc này; native skills hoặc làm trực tiếp đều được.
```

## 8. Thêm kỹ năng khác khi có nhu cầu

Đặt kỹ năng tự biên soạn vào `skills/local/shared/` hoặc `skills/local/project/`.
Kỹ năng nhập từ ngoài có thể đặt trong `skills/external/`; `skills/inbox/` chỉ là chỗ
tạm nếu bạn muốn phân loại sau.

Đặt file vào thư mục chưa có nghĩa kỹ năng đã được nhận. Kỹ năng tự rút ra khi làm việc và kỹ năng
hay gói tải từ ngoài dùng chung một chuẩn tiếp nhận (`skills/README.md`, mục "Tiếp nhận kỹ năng và gói"):
nó phải bổ sung điều native hoặc cách đang có chưa làm được, rõ nguồn, rõ quyền, có bằng chứng dùng
được. Nếu trợ lý AI của bạn đã làm tốt việc đó thì không cần thêm kỹ năng trùng; kết luận "không cần" cũng
là kết quả tốt. Trong lúc xét, kỹ năng được ghi `REVIEW` và vẫn có thể dùng thử trong dự án.

Khi thêm hoặc sửa lớn, nhờ trợ lý AI đọc đủ để ghi `Use when`, vị trí, nguồn gốc và
dependency đáng chú ý vào index. Không cần đánh giá lại khi dùng kỹ năng đã được nhận.
Người dùng giữ quyền thêm/bỏ/sửa thư viện và quyền đưa kỹ năng vào bộ mẫu gốc; trợ lý AI chủ động
lựa chọn trong tác nghiệp. Cập nhật bộ mẫu gốc không tự đổi các dự án đã tạo trước đó.

## 9. Gói lĩnh vực và cài kỹ năng vào ứng dụng

Lõi của bộ công cụ chỉ giữ quy tắc làm việc và mười bốn kỹ năng dùng chung. Kiến thức riêng của một lĩnh vực (cảng và logistics,
nhân sự, tài chính...) nên nằm trong **gói lĩnh vực** trong `packs/`, cài vào dự án nào cần bằng
`python tools/pack.py add <tên>` (xem `python tools/pack.py list`). Gói cài vào `skills/local/packs/` và được ghi trong
`.agent/SKILL_INDEX.md` với Scope `PACK`; gỡ bằng `pack.py remove <tên>` (thư mục được chuyển vào `archive/`, không xóa).
Quy tắc nhận một gói và cách viết gói mới ở `packs/README.md`. Mọi gói cài vào đều ghi `REVIEW` (dùng thử, không được chép sang ứng dụng); khối `intake` trong gói chỉ là lời khai. Đọc hồ sơ rồi muốn nhận cho dự án
này thì cài kèm `python tools/pack.py add <tên> --confirm` (đã cài rồi thì `pack.py confirm <tên>`; trong bảng điều khiển là nút "Cài và cho phép dùng" / "Cho phép dùng trong dự án", một hộp thoại là xong); sửa nội dung gói sau đó thì phải xác nhận lại. Bộ công cụ kèm sáu gói lĩnh vực thử nghiệm (phiên bản từng gói ghi trong `pack.json`): `phap-ly` (tra cứu, áp dụng văn bản quy phạm pháp luật), `van-thu-luu-tru`
(văn bản đi, đến, sao văn bản, lập hồ sơ, nộp lưu), `cang-logistics` (báo cáo khai thác tàu, sà lan, sự cố thiết bị và công cụ kiểm dữ liệu bãi container),
`hanh-chinh-nhan-su` (quyết định nhân sự, phép năm, làm thêm giờ, kỷ luật, lương, bảo hiểm) và `ke-toan-noi-bo` (tạm ứng, thanh
toán, chứng từ, hóa đơn, lưu trữ) và `academic-research` (tìm, đối chiếu và tổng hợp nguồn học thuật). Gói có nội dung pháp lý kèm bảng căn cứ (tệp legal-basis.md trong thư mục references của kỹ năng) ghi số hiệu, điều khoản, hiệu lực, nguồn và ngày đối
chiếu để người dùng kiểm lại; gói nghiên cứu có phương pháp và quy tắc nguồn tương ứng. Cài bằng `python tools/pack.py add <tên>` hoặc trong bảng điều khiển: nhóm "Quản lý và bảo trì" → "Quản lý kỹ năng". Ngoài ra
là khung `_template` để viết gói mới.

**Lưu ý:** các gói đi kèm hiện là bản thử nghiệm, chưa được nhận làm mặc định. Gói nghiên cứu học thuật vẫn ở mức dùng thử, cần kiểm nguồn và chất lượng theo từng việc. Căn cứ pháp lý trong các gói có nội dung pháp lý được tổng hợp từ trang tin và trang tư vấn, chưa đối chiếu từng điều với văn bản chính thức (Công báo, cổng văn bản của Nhà nước); khi thử, trợ lý AI vẫn có lúc đưa ra câu "trích nguyên văn" không có trong gói. Dùng để tham khảo và soạn nháp; với văn bản trình ký hoặc gửi ra ngoài, tự đối chiếu căn cứ với văn bản chính thức trước khi dùng.

Mỗi dự án giữ bản sao kỹ năng của riêng mình, nên dự án luôn tự đủ và mang đi được; công cụ `tools/upgrade_package.py` giữ
các bản sao này đồng bộ với bộ công cụ mới khi bạn nâng cấp. Nếu muốn một kỹ năng hiện trong menu của ứng dụng (ví dụ Claude), dùng
`python tools/install_skills.py --dest <thư mục skill của ứng dụng> --skills <tên,tên> --yes` (không có `--yes` thì chỉ xem trước), hoặc
trang "Cài kỹ năng vào ứng dụng" của bảng điều khiển (`APP.bat`), nơi bạn đánh dấu kỹ năng cần chép. Chỉ chép kỹ năng bạn thật sự cần: ứng dụng
đã có khả năng tương tự thì không cần. Chỉ kỹ năng đã được nhận mới chép được; kỹ năng cùng tên mà ứng dụng đã có (native hoặc nguồn khác)
luôn được giữ nguyên, và bản cũ do bộ công cụ chép khi thay sẽ được lưu vào `archive/`. Kỹ năng viết theo định dạng `SKILL.md` chung: Claude
đọc `~/.claude/skills`; Codex và Gemini CLI cùng đọc `~/.agents/skills`, nên một lần chép dùng được cho cả hai. Việc này là tùy chọn;
trợ lý AI vẫn đọc được kỹ năng như file.

Bảng thuật ngữ Việt–Anh cho văn bản hành chính: `docs/GLOSSARY_VI_EN.md`. Trước khi giao sản phẩm, có thể dùng
`python tools/check_output.py <file>` và checklist `skills/local/shared/office-documents/references/delivery-checklist.md`.

## 10. Phạm vi tham khảo repo

Các kỹ năng trong bộ công cụ được biên soạn mới dựa trên nhu cầu đã trao đổi. Repo
`sharkrebel/everything-everywhere-for-antigravity` được dùng để tham khảo ý tưởng (kể cả
bốn kỹ năng được chọn qua audit); bộ công cụ viết lại thành bản tiếng Việt gọn, không cài hay
nhập nguyên bản. Không có global rules, hook, installer hoặc kỹ năng định dạng proprietary
được đóng gói lại.

Ghi nhận nguồn, kết quả audit và lý do nằm trong `NGUON_THAM_KHAO_VI.md` cùng thư mục.

## 11. Dùng lại kinh nghiệm từ dự án này cho dự án khác (mẫu cá nhân)

Dự án A (dự án bạn đang làm) có một cách làm hữu ích và bạn muốn dự án B (tạo sau) cũng có. Đừng chép cả A:
chỉ chuyển phần dùng lại được, qua bộ mẫu cá nhân của bạn (bản giải nén ZIP chưa dùng để làm việc). Không có
công cụ đồng bộ tự động; mỗi bước do bạn hoặc trợ lý AI làm khi bạn yêu cầu. Tiêu chí nhận vẫn chỉ nằm ở
`skills/README.md`, mục "Tiếp nhận skill và gói".

- **Bước 1, giữ ở A.** Nguồn, quyết định và kỹ năng riêng (`skills/local/project/`, của bạn, không vào bản giao) ở lại A. Chỉ rút phần thật sự tăng thêm; trợ lý AI làm được rồi thì không tạo kỹ năng trùng.
- **Bước 2, làm bản dẫn xuất.** Tạo kỹ năng mới **khác ID** trong một thư mục nháp ngoài A và ngoài bộ mẫu. Chọn rõ `SKILL.md` và tài nguyên cần. Bỏ tên và số liệu riêng, đường dẫn của A, SourceID/revision/biên nhận, prompt và quyền đã cấp, STATE/HANDOFF, cấu hình provider, nguồn chưa được phép chia sẻ. Chỗ cần dữ liệu thì viết "lấy nguồn của dự án đang dùng". Giữ xuất xứ có thể công khai, không giả nguồn đã xác minh. **Dừng nếu** file được chọn đi qua symlink/junction, thoát thư mục nháp, hoặc còn liên kết ra ngoài hay phụ thuộc về A; quét chuỗi không chứng minh đã làm sạch mọi dữ liệu riêng, bạn đọc lại bản này.
- **Bước 3, tiếp nhận.** Theo chuẩn ở `skills/README.md`: bạn xem đúng bản dẫn xuất và danh sách file sẽ vào bộ mẫu rồi xác nhận (đã có quyền cấp sẵn đúng phạm vi thì dùng, không hỏi lại từng file). Kết luận "dùng chung được" và quyền ghi vào bộ mẫu là hai việc riêng; quyền phải gắn đúng ID, bản đã xem và đúng bộ mẫu đích. **Dừng nếu** kết luận là `REVIEW`, `PROJECT_ONLY`, `DEFER`, hoặc chưa có quyền ghi bộ mẫu. Nhãn `AVAILABLE` gõ tay không phải xác nhận của bạn; bản sửa sau khi bạn đã xem thì xác nhận cũ hết hiệu lực.
- **Bước 4, cập nhật bộ mẫu cá nhân.** Chỉ trên bộ mẫu cá nhân sạch, cách ly (chưa khởi tạo thành dự án, `python tools/check_package.py --verify` đạt và xem trước `new_project.py --name "Kiem tra mau"` với tên chưa tồn tại cũng đạt trước khi sửa; chỉ xem trước, không thêm `--apply`). Thêm đúng file đã chọn vào `skills/local/shared/<id>/` và một dòng vào `.agent/SKILL_INDEX.md`; bản tiếng Anh vào `en/skills/local/shared/<id>/` và `en/.agent/SKILL_INDEX.md`. **Dừng trước khi ghi, giữ nguyên bộ mẫu** nếu ID hoặc đường dẫn trùng kỹ năng có sẵn, hoặc bộ mẫu không còn khớp MANIFEST trước khi sửa; báo phần còn thiếu. Sau khi ghi, so mọi thay đổi của bộ mẫu với danh sách đã nhận, cả đường dẫn lẫn bytes của payload và toàn bộ index sau phép chèn dự kiến; có gì ngoài danh sách thì dừng tại đó, không sang bước 5 và báo cho bạn phần khác danh sách (MANIFEST chưa dựng lại nên máy cũng chưa cho tạo B).
- **Bước 5, dựng lại manifest.** Sau khi thay đổi đã khớp danh sách, chạy `python tools/check_package.py --write-manifest` rồi `--verify` **trong bộ mẫu cá nhân đó**. Manifest chỉ là dấu toàn vẹn, không phải bằng chứng đã tiếp nhận: chạy khi chưa so danh sách sẽ hợp thức hóa luôn cả file thừa. Không chạy lệnh này trong dự án A hay trong kho nguồn của người bảo trì. `--verify` không đạt thì dừng, không sửa mã băm tay.
- **Bước 6, tạo B.** Trong bộ mẫu: `python tools/new_project.py --name "B"` để xem trước, thêm `--apply` để tạo (`--lang en` cho bản tiếng Anh). Bộ mẫu giữ nguyên. B có kỹ năng dùng lại và dòng index tương ứng, nguồn và quyết định của riêng B, không có nguồn, quyền, STATE hay đầu ra đã nhận của A. Không tạo B bằng cách chép A rồi đổi tên: `new_project.py` từ chối thư mục đã là dự án.
- **Bước 7, dùng ở B.** Trợ lý AI chỉ dùng kỹ năng khi hợp việc. Kỹ năng đã được nhận vào thư viện không có nghĩa đầu ra của B đã được nhận. Chép sang menu ứng dụng là quyết định khác (`install_skills.py`), không thuộc luồng này.

```text
Từ kỹ năng riêng <tên> của dự án này, làm bản dẫn xuất tên <id-mới> để dùng cho các dự án khác của tôi:
bỏ dữ liệu riêng, đường dẫn và nguồn của dự án này. Cho tôi xem bản đó và danh sách file sẽ vào bộ mẫu cá nhân
trước khi ghi; chưa ghi gì vào bộ mẫu khi tôi chưa xác nhận.
```

Sau bước 6, A, bộ mẫu và B độc lập: sửa nguồn hay kỹ năng riêng ở A không đổi B; sửa B không đổi A hay bộ mẫu; kết quả
bạn đã nhận ở A không truyền sang B. Bộ mẫu cá nhân đổi cũng không làm dự án đã tạo trước đó đổi theo (xem mục 8). Kỹ năng
dẫn xuất khi đã vào bộ mẫu thuộc phần dùng chung của bộ công cụ, khác kỹ năng riêng ở A; giữ nó qua mọi lần nâng cấp hay hạ
cấp bộ công cụ chưa được bảo đảm ở đây. Muốn giữ bản bộ mẫu trước khi sửa thì bạn tự chép hoặc nhờ trợ lý AI; trợ lý AI không tự
tạo bản sao lưu ngoài yêu cầu.

Điều máy kiểm và điều chỉ là quy ước hợp tác: luồng tạo dự án từ chối khi file thuộc package/shared trong tập giao lệch MANIFEST. `--verify` riêng lẻ chỉ kiểm file đã ghi trong manifest; bước xem trước còn kiểm tập file giao, nên không bỏ qua nó khi có file thừa. Manifest không xác nhận dữ liệu riêng đã sạch. Máy
từ chối lấy dự án đã khởi tạo làm bộ mẫu, và `install_skills.py` không bao giờ chép `skills/local/project/`. Việc tách dữ liệu
riêng, tiếp nhận, quyền ghi bộ mẫu và so danh sách (bước 2 đến 5) là thỏa thuận giữa bạn và trợ lý AI; không có công cụ chặn nếu
bạn chép tay, và công cụ cũng không đánh giá chất lượng kỹ năng.
