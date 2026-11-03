# Gói Kế toán nội bộ / Internal accounting pack (ke-toan-noi-bo)

Phiên bản 0.2.0, thử nghiệm. Một skill: `internal-accounting-vn`: đề nghị tạm ứng, thanh toán, hoàn ứng, đối chiếu công nợ, kiểm chứng từ và hóa đơn, điều kiện khấu trừ, lưu trữ tài liệu kế toán.
Version 0.2.0, trial. One skill: `internal-accounting-vn`: advance, payment and settlement requests, balance confirmations, voucher and invoice checks, deduction conditions, retention of accounting records.

Cài / Install: `python tools/pack.py add ke-toan-noi-bo` (hoặc trang "Gói lĩnh vực" của bảng điều khiển / or the "Domain packs" page of the control panel).

**Căn cứ pháp lý / Legal basis:** `skills/internal-accounting-vn/references/legal-basis.md` ghi số hiệu, điều khoản, ngày ban hành, hiệu lực,
trạng thái và nguồn của lượt tham khảo ngày 12/10/2026; đây không phải xác nhận đã đối chiếu toàn bộ văn bản chính thức hoặc hiệu lực hiện hành. Đội dev chịu kiểm nguồn trước khi công bố sẵn dùng; khi làm việc, agent đối chiếu đúng nguồn và nêu phần chưa kiểm. Dòng chưa kiểm được giữ `[cần xác nhận]`.
Lists the metadata and sources of the 2026-10-12 reference pass; it does not certify all official texts or current legal validity. Developers verify sources before claiming readiness; the agent checks the relevant sources during work and states unverified parts. Unverified rows retain `[cần xác nhận]`.

Không thay việc hạch toán, lập báo cáo tài chính hay tư vấn thuế. Does not replace bookkeeping, financial statements or tax advice.

Trạng thái / Status: gói vẫn thử nghiệm `DEFER`, chưa có kết luận sẵn dùng cho phiên bản này. Trước khi công bố sẵn dùng hoặc nâng lên 1.0, đội dev chuẩn bị ca đại diện, thiếu nguồn/lỗi/ngoài phạm vi theo rủi ro, expected có căn cứ, review và kiểm luồng trên bản/host công bố. Feedback mức phù hợp đến sau bản đã đạt chuẩn nội bộ; không giao người nhận viết test hoặc tìm người kiểm thay dev.
The pack remains a `DEFER` trial candidate with no readiness conclusion for this version. Before a ready-to-use claim or 1.0, developers prepare representative and risk-based missing-source/error/out-of-scope cases, grounded expected results, review and checks on the announced artifact/host. Fit feedback follows internal acceptance; recipients do not write tests or recruit testers for developers.

Chuẩn làn nhận folder vẫn giữ điều kiện ba việc thật riêng biệt và đánh giá người nhận khi làn đó áp dụng; đây không phải ngưỡng chặn làn builder. Sáu điều kiện, quyền cài/confirm và phạm vi riêng của project giữ nguyên. Không tự cài, xác nhận hoặc nâng trạng thái. Xem [hồ sơ hiện có](references/intake-record.md) và [chuẩn chung](../../skills/README.md#developer-product-acceptance).
The recipient-folder lane retains its three distinct real tasks and recipient evaluation when applicable; this does not block the builder lane. All six conditions, install/confirm authority and project-specific scope remain. Do not install, confirm or promote automatically. See the existing record and shared standard linked above.

Skill riêng của project về quy chế, mẫu và người ký của đơn vị vẫn được ưu tiên cho nghiệp vụ đó. A project-specific skill for unit rules, templates and signatories retains precedence for that work.
