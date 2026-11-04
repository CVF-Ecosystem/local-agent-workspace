# Review độc lập — roadmap Local r2

**Verdict: `REVIEW_PASSED` — chốt roadmap `LOCAL-ROADMAP-20261104-r2`.** Không có điểm chặn. Ba điểm không chặn ghi ở dưới để Local xử lý khi thi công.

## Quyền và phạm vi

- **Giao bởi:** operator, trực tiếp trong hội thoại Claude Code ngày 04/11/2026: "cho phép bạn làm reviewer chốt roadmap này".
- **Reviewer:** Claude (Opus 5.5), phiên khác với người viết roadmap (Main Local/Codex).
- **Phạm vi:** chỉ tài liệu roadmap r2, tức mục "Quyết định và roadmap chi tiết của Local — 04/11/2026" trong `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md`, cùng STATE và brief đầu HANDOFF tương ứng.
- **Ngoài phạm vi:** diff 4.0 (chưa có), fixture/ca 4.1 (chưa có), mọi thi công sau này. Quyền review này không mở grant gọi vai, không cấp quyền sửa registry, chạy trả phí, push hay phát hành.
- **Ý nghĩa của verdict:** review đạt chỉ chốt bản kế hoạch, **không đóng mốc sản phẩm nào**. Toàn bộ gap ở §3–5 còn nguyên.

## Binding

| File | SHA256 lúc review |
|---|---|
| `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` (r2) | `868fb510631efe38515b68ca500fbfaad7508cf07201968109fb273ba3cc49ab` |
| `.agent/HANDOFF.md` (trước khi thêm dấu vết review) | `725c19ad9b014f5f9c2675005361b26457e91f9a63dc4528f3ebe52dbeba01ae` |
| `.agent/STATE.md` (trước khi sửa câu reviewer) | `e86d8b8aedb95bea5b4e251a09793174359ec8e55ec8cbcd3100582056fabfa2` |
| Bản r1 giữ trong `archive/maintainer/roadmap-local-r1-before-claude-review-20261104/` | roadmap `d333bbac…`, HANDOFF `ec70cd01…`, đều khớp |

Nếu roadmap đổi bytes sau review này thì verdict không áp cho bản mới.

## Đã kiểm

1. **Đủ phạm vi đọc:** diff r1→r2 so với bản r1 lưu trong archive, đọc toàn bộ; phần không đổi đã đọc đủ ở lượt đánh giá trước (dòng 4–152 của r1).
2. **Quy tắc 10:** mỗi gói 4.0–4.6 nêu mốc, đầu ra, owner, điều kiện đóng và "Còn sau đó"; bảng §3 phủ V0–V7 và có ánh xạ R/T. Đạt.
3. **Dữ kiện mới của r2, kiểm lại bằng công cụ:**
   - `git rev-parse HEAD` = `32604fbd3d00da53cffff2a8d3735e372f05f23f`, khớp §2.
   - Run 41575566248: cả 5 job thất bại ở bước "Package check (release)". Run 41794538743: job Windows/3.8 thất bại cùng bước, và các bước Guides HTML, Behaviour tests, Release candidate build đều skipped. Khớp §2 ("behavior/build skipped").
   - Mười đường dẫn ca, rubric, oracle và output của 4.1 tồn tại.
4. **Không hạ acceptance:** r2 giữ V0–V7, R/T và toàn gap. Trần ở §6 là giới hạn mỗi lượt, ghi rõ không thay tiêu chí sản phẩm; số lượt trả phí được cấp là 0.
5. **Nhất quán:** STATE (52 dòng, đủ heading) và brief HANDOFF r2 khớp nội dung roadmap; không có chỗ khai đã sửa registry, đã chạy ca hay đã giao reviewer.
6. **Phản biện F1–F9:** mỗi điểm có quyết định ở §7. Các chỗ không nhận nguyên văn (F3, F5, F6) có lý do và không làm yếu tiêu chí.

## Điểm không chặn

- **N1 — Tách lỗi trong tình huống (c) của 4.1.** Tình huống (c) gộp ba kiểu lỗi: số xấu, chỉ thị nằm trong nguồn, yêu cầu vượt quyền. Khi chuẩn bị fixture, nên ghi assertion riêng cho từng kiểu để biết đúng chỗ hỏng. Không cần tách thành ca riêng.
- **N2 — Câu về quyền review.** STATE và §4.1 viết "NO_GRANT sản phẩm không tự phủ định quyền review bảo trì". Theo `PROJECT.md` (chưa có grant thì chưa có quyền) và mục bảo trì của AGENTS, quyền review thực tế đến từ việc operator giao trực tiếp, như lần này. Đề nghị Local ghi rõ nguồn quyền của từng lần review, thay vì suy từ câu trên. Mình đã sửa câu tương ứng trong STATE (xem dưới).
- **N3 — Review cho 4.0.** Diff 4.0 đổi ranh giới source/registry nên cần review độc lập riêng. Quyền lần này không bao gồm phần đó; operator cần giao lại khi diff sẵn sàng.

## Sửa nhỏ của reviewer

- **`.agent/STATE.md`, mục Next milestone:** thay "NO_GRANT sản phẩm không tự phủ định quyền review bảo trì; chưa giao reviewer mới" bằng câu ghi roadmap r2 đã được Claude review đạt theo giao trực tiếp của operator, và review cho diff 4.0 cần operator giao riêng. Không đổi phần nào khác.
- **`.agent/HANDOFF.md`:** thêm một mục ngắn ở đầu file ghi verdict, quyền, binding và hai sửa nhỏ này. Không sửa nội dung của Local.
- **Không sửa** roadmap của Local.

## Việc tiếp theo (không thuộc review)

- Catalog `roadmap/CATALOG_CAU_TRUC_VA_TIEN_DO.md` mục 5–6 chưa có dòng 4.0 và vẫn ghi r1. Theo quy ước, chỉ cập nhật khi operator nhắc.
- Không chạy test, build hay CI. Không đọc nội dung các ca 4.1. Không commit hay push.
