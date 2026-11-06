# Review độc lập — roadmap LAW r7 và form kiểm soát roadmap/tiến độ v1.0

**Verdict: `REVIEW_PASSED_WITH_CONDITION`.** Nhận cả hai tài liệu làm baseline và form dùng tại LAW.
Có một điều kiện (F1) phải xử lý **trước khi giao thi công 4.1/4.2**. Năm điểm còn lại không chặn.

## Quyền và phạm vi

- **Giao bởi:** operator, trong hội thoại Claude Code ngày 06/11/2026: "Đánh giá độc lập 2 phần trên do codex làm".
- **Reviewer:** Claude (Opus 5.5), khác phiên và khác agent với người viết (Main/Codex, Worker Terra 6.1, reviewer Astra).
- **Phạm vi:** (1) phần thay đổi r6→r7 của `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md`, gồm câu trạng thái, "Đọc nhanh", §1.1–1.3, câu ưu tiên ở §4 và đoạn form/bốn câu hỏi/review ở §6; đọc thêm §3, §4.1, §4.2 và §6 để kiểm tính nhất quán. (2) toàn văn `roadmap/CVF_ROADMAP_PROGRESS_FORM.md`.
- **Ngoài phạm vi:** phần roadmap không đổi từ r6; PROJECT, catalog, PENDING_LESSONS (chỉ grep các chỗ dẫn tới form); mọi code, test, host, CVF gốc.
- **Ý nghĩa:** chỉ chốt tài liệu. Review này **không đóng mốc sản phẩm nào**, không cấp quyền và không tiếp nhận form thành chuẩn CVF. Toàn bộ gap ở §1.2/§3 còn nguyên.

## Binding

| File | SHA256 lúc review |
|---|---|
| `roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md` (r7) | `9b6368aa51f12d51c3f970edbb8cfbee794fbdb3301fc820a7364a78dc90e094` |
| `roadmap/CVF_ROADMAP_PROGRESS_FORM.md` (v1.0) | `de514e1b92f4a0293ac929c77bfd423f2e43f96d7dbd3e1938b174139f26e499` |
| `archive/maintainer/roadmap-local-r6-before-baseline-20261106/ROADMAP_VAN_PHONG_NGHIEP_VU.md` (r6) | `d083d197b2d5c9f56d74057fd62c146306a87687a1745828a427ea658ef5037f` |

Ba hash khớp với HANDOFF r6.22 và STATE. Nếu file đổi bytes sau review này thì verdict không áp cho bản mới.

## Đã kiểm

1. **Không mất tiêu chí.** `git diff --no-index` r6→r7 có 5 hunk (+55/−3). Các từ bị xóa chỉ là nhãn r6 và câu trạng thái cũ ("Hoàn tất tài liệu hoặc một sửa code không đóng mốc sản phẩm" được thay bằng "Chốt roadmap không phải nghiệm thu sản phẩm hoặc cấp quyền phát hành"). V0–V7, R/T, §3, các điều kiện đóng 4.0–4.6 và trần §6 giữ nguyên.
2. **Trung thực về trạng thái.** Cả năm hàng §1.2 ghi CHƯA ĐẠT. §1.3 ghi rõ năm hành vi là yêu cầu nghiệm thu, chưa phải phát hiện có/thiếu code. Câu trạng thái giữ `PRERELEASE_NOT_READY`. Không chỗ nào lấy số test làm tỷ lệ.
3. **Baseline §1.1** có owner, authority đổi (operator quyết định mục tiêu và cam kết), phần không mở, điều kiện kết thúc và thủ tục đổi baseline. Đề xuất chưa duyệt không có hiệu lực. Đạt.
4. **Form tách khỏi LAW.** Phần chuẩn không chứa tên năm chức năng LAW, không áp số mốc/phép thử. Có ba lớp chung → project → bằng chứng; các trạng thái UNKNOWN/NOT_RUN/SKIP/FAILED/BLOCKED/DEFERRED không phải đạt; blocker chỉ giữ phần phụ thuộc; task ≠ mốc ≠ phát hành; phần trăm phải có tập điều kiện đã chốt. Ghi rõ `NOT_UPSTREAMED`, chưa canonical. Đạt.
5. **Kỹ thuật file.** Cả ba file CRLF đồng nhất (r7 621/621 dòng, form 112/112, r6 569/569). `git diff --check` trên r7 và form: không cảnh báo. Liên kết `CVF_ROADMAP_PROGRESS_FORM.md` ở §6 trỏ đúng file. STATE 60 dòng/8 heading.
6. **Vị trí form.** `tools/check_package.py:22` loại `roadmap/` khỏi gói phát hành, nên form không đến tay người dùng LAW. Đúng với trạng thái ứng viên; đường đến project khác là qua CVF tiếp nhận, không qua bản LAW.

## Điều kiện — xử lý trước khi giao 4.1/4.2

**F1 — Năm hành vi §1.3 chưa vào điều kiện đóng của 4.1/4.2.** §1.3 ghi "tích hợp vào 4.1/4.2", và dòng 84 yêu cầu ánh xạ expected trước khi chạy. Nhưng mục "Đóng phần này khi" của 4.1 (dòng 154) và "Điều kiện đóng" của 4.2 (dòng 164) không nhắc §1.3. AGENTS coi hàng roadmap là phiếu việc mặc định, nên Worker đọc đúng mục 4.1 có thể đóng phần việc mà bỏ sót hai hành vi.

Cụ thể hơn: ba tình huống (a)(b)(c) của 4.1 (dòng 148) không có tình huống nào có hai kết luận khác nhau. Như vậy hành vi "Main xử lý kết quả bất đồng" hiện **chưa có ca nào để kiểm**. Hành vi "Main biết năng lực thực của phiên" cũng chỉ được phủ một phần qua cụm "giao đúng người".

Đề nghị, sửa trong cùng r7 hoặc ghi vào brief 4.1 đầu tiên:
- Thêm vào dòng 154: "kèm expected §1.3 cho hành vi 1 và 3".
- Thêm vào dòng 164: "kèm expected §1.3 cho hành vi 2, 4 và 5".
- Với ca bất đồng: hoặc gộp vào (b) (hai chuyên viên kết luận khác nhau vì nguồn mâu thuẫn), hoặc ghi rõ là gap còn mở của 4.1. Không cần thêm tình huống thứ tư nếu gộp được; dòng 84 đã cho phép.

## Điểm không chặn

- **N1 — Form chưa nói cách ghi "đạt có giới hạn".** Form chỉ định nghĩa `Đạt` và các trạng thái không đạt. LAW dùng `ACCEPT_WITH_LIMITS`/`WITH_LIMITS` rất nhiều, kể cả cho chính hai tài liệu này. Không có quy tắc thì người dùng form ở project khác dễ đọc "đạt có giới hạn" thành `Đạt`. Đề nghị thêm một câu ở form §2: "Đạt có giới hạn chỉ áp cho phạm vi đã nêu; phần ngoài giới hạn ghi ở cột Thiếu và không tính là đạt mốc."
- **N2 — Phần đầu roadmap vẫn nặng chi tiết Excel/COM.** Mục đích r7 là kéo trọng tâm về luồng văn phòng, nhưng dòng 8 và 10 (ngay dưới câu trạng thái) vẫn là các đoạn dài về Excel173, COM Open 1004, 0/7 và 0/5. Người mở roadmap thấy Excel/COM trước khi thấy §1.1–1.3. Đề nghị chuyển hai đoạn này xuống sau §1.3 hoặc sang HANDOFF, chỉ để lại một câu trỏ tới đó.
- **N3 — Bốn câu hỏi chọn việc đang nằm ở bốn chỗ:** quy tắc 10 của AGENTS, mục "Kiểm soát bắt buộc khi điều phối" của AGENTS, roadmap §6 (dòng 240) và form §3. Nội dung hiện khớp nhau nhưng câu chữ khác, nên dễ lệch khi sửa một chỗ. Đề nghị §6 chỉ giữ phần riêng của LAW (câu 1 trỏ §1.2) và dẫn sang form §3 cho phần còn lại.
- **N4 — Form còn dấu vết riêng của LAW.** Phần "Nguồn và tiếp nhận ứng viên" ghi "(theo brief W44/r6.22)" và "operator-local manifest". Hai cụm này cần bỏ hoặc đổi khi CVF tiếp nhận. Thêm một lệch nhỏ: §6 gọi là "CVF — Form kiểm soát roadmap và tiến độ", còn tiêu đề file là "Biểu mẫu kiểm soát roadmap và tiến độ project".
- **N5 — Bảng baseline của form thiếu dòng thời hạn/ngân sách đã duyệt.** Lời dẫn §1 có "không tự thay ngân sách" và bảng §4 có cột chi phí, nhưng §1 không có chỗ ghi giá trị gốc để đối chiếu. Đề nghị thêm dòng "Thời hạn / ngân sách đã duyệt (nếu có; chưa có ghi rõ)".

## Không sửa, chưa kiểm

- Reviewer **không sửa** roadmap, form, STATE hay HANDOFF. Brief r6.22 giao Main làm sole writer các file này, nên Main quyết định cách xử lý F1, N1–N5 và ghi dấu vết review vào HANDOFF.
- Không chạy `check_package.py --check-eol`; tái dùng kết quả Main đã ghi, cộng với phép đếm CRLF và `git diff --check` ở trên.
- Không đối chiếu nội dung PROJECT.md dòng 88, catalog dòng 81/100 và PENDING_LESSONS với r7, chỉ xác nhận các file này có dẫn tới r7/form.
- Không đọc chuẩn CVF gốc (`CVF_PROJECT_DEVELOPMENT_APPLICATION_STANDARD.md`), không kiểm hash d06b6238…; form có trùng hay lệch với chuẩn đó là việc của maintainer CVF khi tiếp nhận.
- Không chứng minh form có hiệu quả chống lệch hướng. Việc đó chỉ thấy được qua các brief thi công tiếp theo.
- Không commit, không push.
