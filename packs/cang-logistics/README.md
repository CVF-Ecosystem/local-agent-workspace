# Gói Cảng - logistics / Ports and logistics pack (cang-logistics)

Phiên bản 0.2.0, thử nghiệm. Một skill: `port-operations-reports`: báo cáo khai thác tàu và sà lan, chờ cầu, năng suất, gián đoạn và sự cố thiết bị, đối soát sự cố với chuyến tàu.
Version 0.2.0, trial. One skill: `port-operations-reports`: ship and barge operation reports, berth waiting, productivity, stoppages and equipment incidents, incident-to-voyage matching.

Cài / Install: `python tools/pack.py add cang-logistics` (hoặc trang "Gói lĩnh vực" của bảng điều khiển / or the "Domain packs" page of the control panel).

**Căn cứ pháp lý / Legal basis:** `skills/port-operations-reports/references/legal-basis.md` ghi số hiệu, điều khoản, ngày ban hành, hiệu lực,
trạng thái và nguồn, đối chiếu ngày 12/10/2026, để người dùng tự kiểm lại. Dòng chưa kiểm được ghi `[cần xác nhận]`.
Lists numbers, articles, dates, status and sources, checked on 2026-10-12, so users can verify them; unverified rows say `[cần xác nhận]`.

Quy tắc tính rút từ việc thật của một đội khai thác container (đã bỏ tên đơn vị, mã thiết bị, số liệu). Calculation rules drawn from real work at a container operations team (unit names, equipment codes and figures removed).

Trạng thái / Status: chưa qua lần thử trên ứng dụng agent thật sau khi viết; dùng trên một việc thật rồi ghi phản hồi trước khi
nâng lên 1.0. Skill riêng của project (quy chế, mẫu, người ký của đơn vị) đứng trước gói này.
Not yet tried in a real agent app after writing; use it on a real task and record feedback before 1.0. A project's own skill
(the unit's rules, templates, signatories) comes before this pack.
