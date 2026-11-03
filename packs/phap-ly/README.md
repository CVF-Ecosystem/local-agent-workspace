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

Trạng thái / Status: gói vẫn thử nghiệm `DEFER`, chưa có kết luận sẵn dùng cho phiên bản này. Trước khi công bố sẵn dùng hoặc nâng lên 1.0, đội dev chuẩn bị ca đại diện, thiếu nguồn/lỗi/ngoài phạm vi theo rủi ro, expected có căn cứ, review và kiểm luồng trên bản/host công bố. Feedback mức phù hợp đến sau bản đã đạt chuẩn nội bộ; không giao người nhận viết test hoặc tìm người kiểm thay dev.
The pack remains a `DEFER` trial candidate with no readiness conclusion for this version. Before a ready-to-use claim or 1.0, developers prepare representative and risk-based missing-source/error/out-of-scope cases, grounded expected results, review and checks on the announced artifact/host. Fit feedback follows internal acceptance; recipients do not write tests or recruit testers for developers.

Chuẩn làn nhận folder vẫn giữ điều kiện ba việc thật riêng biệt và đánh giá người nhận khi làn đó áp dụng; đây không phải ngưỡng chặn làn builder. Sáu điều kiện, quyền cài/confirm và phạm vi riêng của project giữ nguyên. Không tự cài, xác nhận hoặc nâng trạng thái. Xem [hồ sơ hiện có](references/intake-record.md) và [chuẩn chung](../../skills/README.md#developer-product-acceptance).
The recipient-folder lane retains its three distinct real tasks and recipient evaluation when applicable; this does not block the builder lane. All six conditions, install/confirm authority and project-specific scope remain. Do not install, confirm or promote automatically. See the existing record and shared standard linked above.

Skill riêng của project về một lĩnh vực hẹp (ví dụ hồ sơ đất đai của một đơn vị) đứng trước gói này cho nghiệp vụ đó; gói chỉ
cung cấp phương pháp chung. A project's own skill for a narrow domain comes before this pack for that work; the pack only
provides the general method.
