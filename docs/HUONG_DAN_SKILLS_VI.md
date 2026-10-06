# Chọn và sử dụng skills

Skill trong package là hướng dẫn và tài nguyên bổ sung. Agent chọn theo độ phù hợp
với công việc, không theo thứ tự native → local hoặc local → native.

## 1. Khi nào một skill có ích?

Một skill đáng dùng khi có mẫu, kinh nghiệm hoặc cách xử lý giúp hoàn thành yêu cầu
rõ hơn, nhanh hơn hoặc ít phải làm lại hơn. Không cần gọi skill chỉ vì nhiệm vụ có
một từ khóa giống tên skill.

| Công việc | Cách lựa chọn có thể phù hợp |
|---|---|
| Sửa một câu trong thông báo | Làm trực tiếp. |
| Soạn SOP từ quy định và mẫu nội bộ | Dùng nguồn/mẫu của dự án; tham khảo `office-documents` khi hữu ích. |
| Soạn đề xuất hoặc báo cáo dài cần trao đổi sâu | Cân nhắc `doc-coauthoring`; hỏi trước khi dùng. |
| Tạo Word/PDF từ nội dung đã duyệt | Dùng công cụ hoặc native skill định dạng phù hợp; không phải soạn lại nội dung. |
| Vẽ biểu đồ từ bảng số liệu | Cân nhắc `data-charts`; kiểm tra bảng bằng `spreadsheet-check` nếu dữ liệu chưa sạch. |
| Làm báo cáo HTML từ dữ liệu | Cân nhắc `html-reports`, native skill hoặc báo cáo cũ đang có. |
| Chỉnh văn phong một báo cáo | Cân nhắc `vietnamese-editing`; không mặc định sửa toàn bộ tài liệu. |
| So bản quy định mới với bản cũ | Cân nhắc `document-comparison`. |
| Lập biên bản từ ghi chú họp | Cân nhắc `meeting-minutes`. |
| Mô tả quy trình, phân vai, sơ đồ | Cân nhắc `process-mapping`, kết hợp `office-documents` khi viết thành tài liệu. |
| Báo cáo tuần, thông báo, bản tin, FAQ, báo cáo sự cố | Cân nhắc `internal-comms`. |
| Công văn, tờ trình, báo cáo gửi cơ quan khác hoặc trình ký | Cân nhắc `vn-admin-documents`; dùng quy chế văn thư của đơn vị trước nếu có. |

Đây là ví dụ lựa chọn, không phải bảng định tuyến bắt buộc. Agent có thể kết hợp
skills khi chúng bổ sung nhau hoặc xử lý trực tiếp nếu đã đủ khả năng.

## 2. Skill tài liệu nghiệp vụ

`skills/local/shared/office-documents/SKILL.md` cung cấp gợi ý và ba khung ngắn:
SOP/quy trình, biểu mẫu, cập nhật nội bộ. Chọn phần phù hợp, không cần điền tất cả.

```text
Từ tài liệu quy định này, tạo biểu mẫu ghi nhận yêu cầu. Dùng mẫu nội bộ nếu phù hợp;
có thể tham khảo office-documents. Không tự thêm thông tin phải thu thập ngoài nhu cầu.
```

Khung đi kèm không chứa quy định thật của đơn vị. Dữ kiện và điều khoản nghiệp vụ
vẫn đến từ nguồn hoặc quyết định được xác nhận, không từ ví dụ trong skill.

## 3. Skill báo cáo HTML

`skills/local/shared/html-reports/SKILL.md` đi kèm hai file có thể mở thử:

| Mẫu | Vị trí bên trong skill | Gợi ý sử dụng |
|---|---|---|
| Báo cáo định kỳ | `assets/periodic-report.html` | Báo cáo tháng/tuần có nhận xét, KPI, diễn biến và bảng số liệu. |
| Tổng quan chỉ số | `assets/metrics-overview.html` | Trang KPI có lọc theo kỳ/kênh và bảng chi tiết. |

Cả hai mẫu là HTML tự chứa, viết mới cho package, dùng font hệ thống và không cần
mạng. Dữ liệu trong bản mẫu là **minh họa**, không phải dữ liệu của dự án.

```text
Dùng bảng số liệu này để tạo một báo cáo HTML mở offline trong output/.
Chọn mẫu hoặc cách trình bày phù hợp nhất. Giữ đúng số liệu, ghi nguồn và kỳ báo cáo.
```

Agent có thể thay khối `report-data` trong file mẫu rồi chỉnh bố cục và nhận xét.
Bạn không cần sửa mã để sử dụng skill: giao dữ liệu và yêu cầu cho agent là đủ.
Nút lọc chỉ thay cách xem dữ liệu trong file; mẫu không kết nối dữ liệu sống.

Hai mẫu hỗ trợ in qua nút “In báo cáo”. Mở được offline không có nghĩa quá trình
agent đọc dữ liệu và tạo báo cáo cũng diễn ra hoàn toàn offline.

## 4. Skill biểu đồ

`skills/local/shared/data-charts/SKILL.md` dành cho yêu cầu “vẽ biểu đồ” từ một bảng số
liệu. Skill đi kèm `assets/basic-charts.html` (thẻ KPI, biểu đồ đường, cột ngang, cột
xếp chồng, vành khuyên, bảng kèm thanh) và `references/chart-selection.md` để chọn dạng biểu
đồ theo dữ liệu. Biểu đồ là SVG thuần, mở offline, mỗi hình có bảng dữ liệu gập kèm theo.

```text
Vẽ biểu đồ từ bảng số liệu này, lưu thành một file HTML mở offline trong output/.
Chọn dạng biểu đồ phù hợp cho từng thông điệp; ghi rõ đơn vị, kỳ và nguồn.
```

Khác với `html-reports` (khung trang báo cáo có nhận xét), `data-charts` tập trung vào
chính biểu đồ. Hai skill dùng được cùng nhau khi cần một báo cáo có biểu đồ.

## 5. Skill biên tập tiếng Việt

`skills/local/shared/vietnamese-editing/SKILL.md` hữu ích khi có yêu cầu rõ về văn
phong. Nó hướng đến giữ nghĩa, số liệu, thuật ngữ và mức độ chắc chắn, không “khử
AI” bằng cách thay dấu câu hoặc làm nội dung mất tính nghiệp vụ. Khi cần nhận ra văn
phong khuôn mẫu, skill có `references/machine-style-signs.md`.

```text
Biên tập phần tóm tắt này cho rõ và bớt sáo rỗng. Giữ nguyên số liệu và mức độ
chắc chắn của nhận định; chỉ trả bản đã chỉnh.
```

Không cần tự chạy skill này sau mọi báo cáo hoặc SOP.

## 6. Các skill cho công việc hằng ngày

Bảy skill này ngắn, mỗi skill có phần “khi nào dừng” để agent không làm quá phạm vi.

| Skill | Dùng khi | Đầu ra điển hình |
|---|---|---|
| `document-comparison` | Có hai phiên bản của một tài liệu. | Bảng thay đổi: mục, cũ, mới, loại, tác động (nếu có căn cứ). |
| `spreadsheet-check` | Sắp lấy số từ Excel/CSV cho báo cáo. | Danh sách phát hiện theo mức ảnh hưởng; không sửa file gốc. |
| `meeting-minutes` | Có ghi chú hoặc bản ghi cuộc họp. | Quyết định, việc cần làm (ai/hạn nếu có), vấn đề chưa chốt. |
| `process-mapping` | Cần mô tả hoặc rà soát quy trình. | Bảng bước, RACI khi cần, sơ đồ Mermaid/SVG khi cần. |
| `internal-comms` | Cần viết cho người trong đơn vị đọc nhanh. | Báo cáo tiến độ (Tiến độ - Kế hoạch - Vấn đề), thông báo, bản tin, FAQ, báo cáo sự cố. |
| `doc-coauthoring` | Tài liệu lớn, muốn trao đổi sâu từng bước. | Dàn ý đã duyệt, các mục soạn theo từng phần, một lượt soát cuối. |
| `vn-admin-documents` | Cần văn bản hành chính đúng thể thức. | Bản nháp có đủ thành phần thể thức; số, ngày, người ký để `[cần xác nhận]`. |

```text
Đối chiếu Quy_dinh_cu.docx với Quy_dinh_moi.docx. Chỉ lập bảng thay đổi có ý nghĩa,
ưu tiên số liệu, thời hạn, vai trò. Chỗ chưa rõ tác động thì ghi "cần xác nhận".
```

`spreadsheet-check` có kèm script `scripts/check_spreadsheet.py` (chỉ đọc; CSV không cần cài gì, Excel cần
`openpyxl`; thêm `--lang en` để báo cáo bằng tiếng Anh). `vn-admin-documents` chỉ là điểm xuất phát về thể thức: quy định văn thư có thể đã đổi và đơn vị
có thể có quy chế riêng, nên kiểm bản hiện hành trước khi ban hành.

`doc-coauthoring` chỉ dùng khi bạn muốn; agent sẽ hỏi trước, và nếu bạn từ chối thì soạn
thẳng. Các skill còn lại không cần xin phép trước khi dùng.

## 7. Cách agent tìm skills

`.agent/SKILL_INDEX.md` có mô tả khi nào hữu ích và đường dẫn đến từng skill. Agent
có thể tra khi cần khám phá hoặc mở trực tiếp khi đã biết skill phù hợp.

`AVAILABLE` nghĩa sẵn dùng, `ACTIVE` nghĩa thường dùng trong project. Cả hai đều
không yêu cầu nạp đầu phiên. Ghi chú native chỉ mô tả khả năng đã biết của một môi
trường; khi chuyển agent, dùng những khả năng thực có trong phiên mới.

Package không tự cài các skill vào menu native của ứng dụng. Khi cần, chỉ đường dẫn:

```text
Skill bổ sung của project được mô tả trong .agent/SKILL_INDEX.md.
Chỉ tham khảo skill có ích cho việc này; native skills hoặc làm trực tiếp đều được.
```

## 8. Thêm skill khác khi có nhu cầu

Đặt skill tự biên soạn vào `skills/local/shared/` hoặc `skills/local/project/`.
Skill nhập từ ngoài có thể đặt trong `skills/external/`; `skills/inbox/` chỉ là chỗ
tạm nếu bạn muốn phân loại sau.

Khi thêm hoặc sửa lớn, nhờ agent đọc đủ để ghi `Use when`, vị trí, nguồn gốc và
dependency đáng chú ý vào index. Không cần đánh giá lại khi dùng skill quen thuộc.
Người dùng giữ quyền thêm/bỏ/sửa thư viện; agent chủ động lựa chọn trong tác nghiệp.

## 9. Phạm vi tham khảo repo

Các skill trong package được biên soạn mới dựa trên nhu cầu đã trao đổi. Repo
`sharkrebel/everything-everywhere-for-antigravity` được dùng để tham khảo ý tưởng (kể cả
bốn skill được chọn qua audit); package viết lại thành bản tiếng Việt gọn, không cài hay
nhập nguyên bản. Không có global rules, hook, installer hoặc skill định dạng proprietary
được đóng gói lại.

Ghi nhận nguồn, kết quả audit và lý do nằm trong `NGUON_THAM_KHAO_VI.md` cùng thư mục.
