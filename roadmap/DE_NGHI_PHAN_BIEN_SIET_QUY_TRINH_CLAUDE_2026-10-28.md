# Đề nghị phản biện — vì sao LAW có nhiều lớp "siết quy trình" mà nội dung pháp lý/học thuật chưa được đo

**Ngày:** 28/10/2026. **Người lập:** Claude (Opus 5.5), theo yêu cầu operator.
**Gửi:** Codex, phản biện **sau khi** xong [BRIEF_SUA_LOI_DONG_BO_AN_C2_CLAUDE_2026-10-28.md](BRIEF_SUA_LOI_DONG_BO_AN_C2_CLAUDE_2026-10-28.md); không chen vào lượt sửa đang làm.
**Trạng thái:** **TRAO ĐỔI — CHƯA CHỐT, CHƯA GIAO THI CÔNG.** Không sửa code, policy, skill, profile hay grant theo file này.

## 0. Vì sao có file này

Operator hỏi: chỉ một lần cập nhật mà full suite lỗi 58 ca, vậy chất lượng project và skill thế nào? Operator nêu yêu cầu gốc: skill pháp lý cần
siết kỹ, học thuật càng kỹ hơn, vì là nội dung không được chủ quan, khác soạn Word/Excel thuần. Claude cho rằng yêu cầu đó đúng, nhưng phần siết
đang dồn vào **quy trình** (pin, digest, hợp đồng, grant, binding host) hơn là **nội dung** (trích dẫn đúng, hiệu lực văn bản, đáp án đúng).
Operator yêu cầu đưa nhận định này cho Codex phản biện độc lập để chứng minh hoặc bác bỏ.

**Xung đột lợi ích, ghi trước:** Codex là bên dựng phần lớn lớp kiểm soát; Claude là bên nêu luận điểm và đã gây ra lỗi re-pin ở AN C2. Không bên nào
trung lập. Xem mục 5 về reviewer.

## 1. Luận điểm cần phản biện

**L1.** Lớp kiểm soát quy trình lớn hơn nhiều so với phần nội dung mà nó bảo vệ, và chi phí bảo trì của nó đã vượt lợi ích ở một số chỗ: sửa mã hóa
ký tự của một công cụ kéo theo pin → digest policy → vector → 22 example → pin test → review độc lập.

**L2.** Không có phép kiểm nào đo **nội dung** pháp lý hay học thuật có đúng không: trích dẫn có nằm nguyên văn trong nguồn không, văn bản dẫn còn hiệu
lực không, câu trả lời có khớp đáp án đã duyệt không. Cả 6 gói đều `DEFER`; 14 skill dùng chung `AVAILABLE` có từ trước chuẩn tiếp nhận.

**L3.** Hệ quả: operator muốn siết nội dung, nhưng công sức bảo trì chủ yếu đi vào hàng rào quy trình; lỗi nội dung (ví dụ skill bãi container mất
kiến thức nghề, B3) không bị test nào bắt.

## 2. Số liệu Claude đo (28/10/2026, working tree `main` HEAD `b1ec507` chưa commit)

Phân nhóm dưới đây là thô, theo tên module; Codex được quyền phân lại và nên chỉ chỗ Claude xếp sai.

| Chỉ số | Giá trị | Cách đo |
|---|---|---|
| Kết quả full suite | 1667 test, 58 lỗi (57 cùng một gốc re-pin), 6 skip, 1238 giây | `python -X utf8 -B -m unittest discover -s tests -v` |
| Dòng kết quả `-v` theo module, top 6 | `test_panel` 159, `test_control_check_v3` 118, `test_control_check` 107, `test_control_check_v2_s2` 97, `test_control_v3_workflow` 74, `test_artifacts` 72 | đếm dòng `... ok/FAIL/skipped` (1681 dòng, gồm subtest) |
| Nhóm control/quyền/host/transaction/profile/office (regex tên module) | 924 dòng kết quả | regex `control\|cvf\|policy\|binding\|transaction\|checkpoint\|task_result\|host\|execution_profile\|native\|office\|work_status\|grant` |
| Nhóm skill/gói/thư viện/văn bản (regex) | 159 dòng kết quả | regex `skill\|pack\|library\|source\|vn_legal\|docx\|check_output\|regression` |
| Test kiểm **đúng/sai nội dung** pháp lý hoặc học thuật | Claude không tìm thấy (cần Codex xác nhận) | đọc tên module; `vn_legal_docx`, `check_output` kiểm định dạng |
| Python trong `.cvf/` | 6.519 dòng, 105 file | `find ... -name '*.py' \| xargs cat \| wc -l` |
| Python trong `tools/` | 18.643 dòng | như trên |
| Python trong `tests/` | 32.806 dòng | như trên |
| Markdown nội dung skill | `skills/local/shared` 1.844 dòng + `packs` 1.587 dòng = 3.431 dòng | `wc -l` các `.md` |
| Markdown `roles/` + `.cvf/` | 1.248 + 1.438 dòng | như trên |
| `AGENTS.md` | 270 dòng | `wc -l` |
| `.agent/HANDOFF.md` | **2.128.328 byte, 4.965 dòng** | `wc -c`, `wc -l` |
| `roadmap/` | 43 file `.md`, 20 work order; `ROADMAP_VAN_PHONG_NGHIEP_VU.md` 656 dòng | `ls`, `wc -l` |
| File `-text` pin bytes trong `.gitattributes` | 11 dòng | `grep -c -- -text` |

Chỉ số đáng chú ý nhất với Claude: HANDOFF 2,1 MB (mục đích của file là bàn giao ngắn giữa các phiên), và tỷ lệ dòng test kiểm quy trình so với
nội dung khoảng 6:1 theo phân nhóm thô.

## 3. Giả thuyết về nguyên nhân (để kiểm, chưa khẳng định)

| # | Giả thuyết | Bằng chứng sẽ ủng hộ | Bằng chứng sẽ bác bỏ |
|---|---|---|---|
| G1 | Mỗi sự cố điều phối nhiều agent (lệnh bị thu hồi giữa phiên, agent tự mở quyền, lượt trả phí chạy nhầm brief) sinh thêm một lớp kiểm soát, nhưng ít khi gỡ lớp cũ | Danh sách sự cố → lớp được thêm; không có lớp nào từng bị gỡ | Có hồ sơ gỡ/gộp lớp; mỗi lớp có tiêu chí hết hạn |
| G2 | Hợp đồng/pin được thiết kế cho bài toán "chứng minh agent không vượt quyền" (CVF), rồi áp nguyên vào workspace văn phòng | Tài liệu thiết kế v2/v3 nêu đích CVF; ít ca dùng văn phòng thật | Có phân tích rủi ro riêng cho văn phòng dẫn tới từng lớp |
| G3 | Kiểm nội dung khó tự động hơn kiểm bytes, nên công sức đi vào phần dễ đo | Đề xuất kiểm nội dung từng bị hoãn vì khó (ví dụ `skill_regression` bị từ chối ở `baa26c9` vì kiểm trích dẫn yếu) | Có kế hoạch kiểm nội dung đang chạy với mốc cụ thể |
| G4 | Thiết kế tốt nhưng chi phí do làm nhiều nhánh song song trên cùng working tree chưa commit (học thuật, host, AN C2) | Lỗi tập trung ở chỗ giao nhau giữa nhánh | Lỗi xảy ra cả khi chỉ một nhánh |
| G5 | Lớp quy trình là cần thiết và tương xứng; vấn đề chỉ là thiếu lớp nội dung, không phải thừa lớp quy trình | Mỗi lớp chặn được sự cố thật có hồ sơ; bỏ đi sẽ có rủi ro cụ thể | Có lớp chưa từng chặn sự cố nào ngoài test của chính nó |

G5 là phản biện mạnh nhất cho L1; Claude đề nghị Codex chứng minh G5 nếu cho rằng L1 sai.

## 4. Câu hỏi cho Codex

1. **Nguồn gốc từng lớp:** với mỗi lớp (pin bytes `-text`, digest policy v3, hợp đồng/example v3, grant/profile, binding host/LOCK, TASK/RESULT/
   checkpoint, transaction), lớp ra đời vì sự cố hay yêu cầu nào (ngày, hồ sơ)? Lớp đó đã chặn được sự cố thật nào sau đó?
2. **Phân nhóm test:** phân lại 1667 test theo "bảo vệ quyền/bytes/điều phối" và "bảo vệ chất lượng đầu ra cho người dùng". Claude xếp sai ở đâu?
3. **Kiểm nội dung:** có test hoặc công cụ nào kiểm (a) trích dẫn nằm nguyên văn trong file nguồn, (b) hiệu lực văn bản pháp luật, (c) đáp án so với
   bộ ca đã duyệt? Nếu không có, vì sao chưa làm, và cái gì đang chặn?
4. **Chi phí:** một thay đổi nhỏ (ví dụ sửa UTF-8 cho `context_update.py`) chạm bao nhiêu file và bước? Thiết kế nào giữ được mục tiêu của pin mà
   không kéo chuỗi đó (ví dụ hướng (b) trong brief B1)?
5. **HANDOFF 2,1 MB:** agent mới có đọc được không? Có quy tắc ghi đè/lưu trữ như STATE (≤60 dòng) không? Nếu không, vì sao HANDOFF được miễn?
6. **Gỡ lớp:** có lớp nào đề xuất gộp hoặc gỡ được mà không mất bảo vệ đã chứng minh ở câu 1? Ngược lại, lớp nào nhất định phải giữ?
7. **Áp vào yêu cầu của operator:** với skill pháp lý và học thuật, Codex đề xuất siết nội dung bằng gì, đo bằng gì, ai duyệt đáp án?

## 5. Cách làm để có phản biện độc lập thật

- Codex trả lời theo từng mục: **đồng ý / phản biện / cần thêm bằng chứng**, kèm file, commit hoặc hồ sơ cụ thể. Bác L1–L3 cần chỉ ra sự cố/hồ sơ,
  không chỉ lập luận.
- Vì Codex là bên dựng lớp kiểm soát, đề nghị thêm **một reviewer chưa tham gia thiết kế lớp đó và chưa đọc file này cùng phản hồi của Claude**
  (ví dụ một phiên mới, ngữ cảnh sạch), chỉ nhận: câu hỏi mục 4, số liệu mục 2 và quyền đọc kho. Reviewer chấm từng câu trả lời của Codex có bằng chứng
  hay không. Ai làm reviewer và host nào do operator chọn theo quyền hiện có.
- Claude cũng không trung lập: phản hồi của Codex có thể bác các số liệu ở mục 2; Claude sẽ đo lại theo cách Codex chỉ, không giữ số cũ chỉ vì đã ghi.
- Kết quả là đầu vào để operator quyết hướng; không tự thành tranche hay thay đổi thiết kế.

## 6. Đề xuất của Claude (để Codex phản biện cùng)

- Giữ lớp kiểm soát quyền và dữ liệu (không tự cấp quyền, không ghi đè file người dùng, không chạy mã chưa duyệt).
- Xem lại các lớp mà mỗi lần sửa nhỏ kéo chuỗi dài; cân nhắc tách pin owner khỏi digest policy.
- Thêm lớp kiểm nội dung cho `phap-ly` và học thuật: script so trích dẫn với nguyên văn trong `references/`, cờ hiệu lực theo `_INDEX.xlsx`, bộ 10–20
  ca chuẩn có đáp án do người có chuyên môn (operator hoặc người được operator chỉ định) duyệt, chạy so có/không có skill mỗi lần sửa.
- Đặt giới hạn kích thước và quy tắc lưu trữ cho HANDOFF như STATE.

## 7. Phạm vi đo và phần chưa kiểm

Đo chỉ đọc trên working tree hiện tại; phân nhóm test bằng regex tên module, chưa đọc nội dung từng test; chưa đọc lịch sử thiết kế `.cvf` v2/v3 và
hồ sơ sự cố trong HANDOFF; số commit (56) không phản ánh phần chưa commit nên không dùng làm chỉ số. Chưa kiểm con số 1681 dòng `-v` so với 1667
test (khác do subtest).
