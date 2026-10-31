# Gói Cảng - logistics / Ports and logistics pack (cang-logistics)

Phiên bản 0.3.0, vẫn là ứng viên `DEFER`. Hai skill có phạm vi riêng:

- `port-operations-reports`: báo cáo khai thác tàu và sà lan, thời gian chờ cầu, năng suất, gián đoạn và sự cố thiết bị.
- `container-yard-check`: xây dựng hoặc rà soát công cụ kiểm tra dữ liệu vị trí bãi từ TOS. Quy tắc và ngưỡng riêng phải được project xác nhận, đặt trong cấu hình riêng.

Version 0.3.0, still a `DEFER` candidate. Two skills with separate scopes:

- `port-operations-reports`: ship and barge operations, berth waiting, productivity, stoppages, and equipment incidents.
- `container-yard-check`: build or review a tool that checks yard-position data from a TOS. Project-specific rules and thresholds must be confirmed and kept in project configuration.

Cài / Install: `python tools/pack.py add cang-logistics` (hoặc trang "Gói lĩnh vực" của bảng điều khiển / or the "Domain packs" page of the control panel).

**Căn cứ pháp lý / Legal basis:** `skills/port-operations-reports/references/legal-basis.md` ghi số hiệu, điều khoản, ngày ban hành, hiệu lực,
trạng thái và nguồn của lượt tham khảo ngày 12/10/2026; đây không phải xác nhận đã đối chiếu toàn bộ văn bản chính thức hoặc hiệu lực hiện hành. Đội dev chịu kiểm nguồn trước khi công bố sẵn dùng; khi làm việc, agent đối chiếu đúng nguồn và nêu phần chưa kiểm. Dòng chưa kiểm được giữ `[cần xác nhận]`.
Lists the metadata and sources of the 2026-10-12 reference pass; it does not certify all official texts or current legal validity. Developers verify sources before claiming readiness; the agent checks the relevant sources during work and states unverified parts. Unverified rows retain `[cần xác nhận]`.

Các quy tắc trong gói không thay cho cấu hình và xác nhận nghiệp vụ của từng project. Không suy tên block, mã thiết bị, thời điểm hoặc ngưỡng từ ví dụ.
Pack guidance does not replace project-specific configuration and domain confirmation. Do not infer block names, equipment codes, timestamps, or thresholds from examples.

Trạng thái / Status: gói vẫn thử nghiệm `DEFER`, chưa có kết luận sẵn dùng cho phiên bản này. Trước khi công bố sẵn dùng hoặc nâng lên 1.0, đội dev chuẩn bị ca đại diện, thiếu nguồn/lỗi/ngoài phạm vi theo rủi ro, expected có căn cứ, review và kiểm luồng trên bản/host công bố. Feedback mức phù hợp đến sau bản đã đạt chuẩn nội bộ; không giao người nhận viết test hoặc tìm người kiểm thay dev.
The pack remains a `DEFER` trial candidate with no readiness conclusion for this version. Before a ready-to-use claim or 1.0, developers prepare representative and risk-based missing-source/error/out-of-scope cases, grounded expected results, review and checks on the announced artifact/host. Fit feedback follows internal acceptance; recipients do not write tests or recruit testers for developers.

Chuẩn làn nhận folder vẫn giữ điều kiện ba việc thật riêng biệt và đánh giá người nhận khi làn đó áp dụng; đây không phải ngưỡng chặn làn builder. Sáu điều kiện, quyền cài/confirm và phạm vi riêng của project giữ nguyên. Không tự cài, xác nhận hoặc nâng trạng thái. Xem [hồ sơ hiện có](references/intake-record.md) và [chuẩn chung](../../skills/README.md#developer-product-acceptance).
The recipient-folder lane retains its three distinct real tasks and recipient evaluation when applicable; this does not block the builder lane. All six conditions, install/confirm authority and project-specific scope remain. Do not install, confirm or promote automatically. See the existing record and shared standard linked above.

Skill riêng của project đứng trước gói này. Project-specific skills take precedence.
