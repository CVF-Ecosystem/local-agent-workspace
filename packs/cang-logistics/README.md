# Gói Cảng - logistics / Ports and logistics pack (cang-logistics)

Phiên bản 0.3.0, vẫn là ứng viên `DEFER`. Hai skill có phạm vi riêng:

- `port-operations-reports`: báo cáo khai thác tàu và sà lan, thời gian chờ cầu, năng suất, gián đoạn và sự cố thiết bị.
- `container-yard-check`: xây dựng hoặc rà soát công cụ kiểm tra dữ liệu vị trí bãi từ TOS. Quy tắc và ngưỡng riêng phải được project xác nhận, đặt trong cấu hình riêng.

Version 0.3.0, still a `DEFER` candidate. Two skills with separate scopes:

- `port-operations-reports`: ship and barge operations, berth waiting, productivity, stoppages, and equipment incidents.
- `container-yard-check`: build or review a tool that checks yard-position data from a TOS. Project-specific rules and thresholds must be confirmed and kept in project configuration.

Cài / Install: `python tools/pack.py add cang-logistics` (hoặc trang "Gói lĩnh vực" của bảng điều khiển / or the "Domain packs" page of the control panel).

**Căn cứ pháp lý / Legal basis:** `skills/port-operations-reports/references/legal-basis.md` ghi số hiệu, điều khoản, ngày ban hành, hiệu lực,
trạng thái và nguồn, đối chiếu ngày 12/10/2026, để người dùng tự kiểm lại. Dòng chưa kiểm được ghi `[cần xác nhận]`.
Lists numbers, articles, dates, status and sources, checked on 2026-10-12, so users can verify them; unverified rows say `[cần xác nhận]`.

Các quy tắc trong gói không thay cho cấu hình và xác nhận nghiệp vụ của từng project. Không suy tên block, mã thiết bị, thời điểm hoặc ngưỡng từ ví dụ.
Pack guidance does not replace project-specific configuration and domain confirmation. Do not infer block names, equipment codes, timestamps, or thresholds from examples.

Trạng thái / Status: chưa có xác nhận dùng trên ứng dụng agent thật cho phiên bản hiện tại. Phản hồi người nhận gói vẫn cần ba việc thật riêng biệt; số kiểm thử của ứng dụng nguồn không thay bằng chứng hiệu quả của skill. Căn cứ pháp lý và hiệu quả/reuse của hai skill còn phải được đánh giá theo hồ sơ. Skill riêng của project đứng trước gói này. Không tự cài, xác nhận hay nâng trạng thái.
The current version has not been confirmed in a real agent app. Recipient feedback still requires three distinct real tasks; application test counts do not prove skill effectiveness. Legal-source review and evidence of both skills' effect and reuse remain open in the intake record. Project-specific skills take precedence. Do not install, confirm, or promote this candidate automatically.
