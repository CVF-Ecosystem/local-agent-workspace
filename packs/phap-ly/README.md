# Gói pháp lý / Legal pack (phap-ly)

Phiên bản 0.2.0, thử nghiệm. Một skill: `legal-research-vn`, phương pháp tra cứu và áp dụng văn bản quy phạm pháp luật Việt
Nam (5 trục định danh vấn đề, bảng căn cứ trích nguyên văn có tọa độ, tra chéo ba chiều, xử lý xung đột, điều kiện dừng).

Version 0.2.0, trial. One skill: `legal-research-vn`, a method for researching and applying Vietnamese legal documents (5 axes
to frame the issue, a verbatim basis table with exact coordinates, three-way cross-checking, conflict rules, a stop condition).

Cài / Install: `python tools/pack.py add phap-ly`

Nguồn / Sources: viết lại từ ý tưởng của skill `tu-van-phap-luat` bản 1.0 (Nguyễn Duy Tùng) và kinh nghiệm tra cứu văn bản của
người duy trì; không chép danh mục văn bản theo lĩnh vực của skill gốc vì chưa đối chiếu được từng số hiệu (xem
`docs/NGUON_THAM_KHAO_VI.md`). Rewritten from ideas in the `tu-van-phap-luat` version 1.0 skill and the maintainer's experience; the
original per-domain document lists were not copied because each number could not be verified.

Trạng thái / Status: chưa qua lần thử trên ứng dụng agent thật sau khi viết; dùng trên một việc thật rồi ghi phản hồi trước khi
nâng lên 1.0. Not yet tried in a real agent app after writing; use it on a real task and record feedback before raising it to 1.0.

Skill riêng của project về một lĩnh vực hẹp (ví dụ hồ sơ đất đai của một đơn vị) đứng trước gói này cho nghiệp vụ đó; gói chỉ
cung cấp phương pháp chung. A project's own skill for a narrow domain comes before this pack for that work; the pack only
provides the general method.
