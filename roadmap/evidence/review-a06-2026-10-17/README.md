# Evidence Worker A-06 — lưu ngày 17/10/2026

Main chép nguyên byte 7 artifact từ scratchpad Worker được operator cung cấp;
SHA256 của từng bản chép khớp nguồn tại thời điểm lưu. Main/Reviewer đọc script
và log, không chạy lại Excel trong lượt đối chiếu này. Đây là bằng chứng do
Worker tạo, không phải một lần chạy Excel độc lập của Reviewer.

Nguồn: `C:\Users\DELL\AppData\Local\Temp\claude\d--UNG-DUNG-AI-TOOL-AI-2026-Controlled-Vibe-Framework-CVF\91d947d8-50ee-43ee-a0c1-f2a09baf2d58\scratchpad\`.

## Artifact

- `excel_proof.py` và `excel_ops.ps1`: script dữ liệu giả, Excel qua COM;
  `logs/excel_proof_E1-E3_after_fix.log` ghi E1 mở sổ/khóa, E2 lưu sau đọc,
  E3 Excel mở được sổ LAW ghi. Thông tin Office 16 do Worker khai trong HANDOFF.
- `excel_dv.py` và `logs/excel_dv_after_fix.log`: validation cổ điển 10 →
  Excel lưu thành x14 10 → LAW ghi lại còn 0; preview báo x14_data_validation.
  Log này chứng minh mất validation trong ca đã chạy, không chứng minh giữ
  nguyên các cấu trúc Excel khác hoặc mọi phiên bản Excel.
- `repro_lock_race.py` và `logs/lock_race_old_vs_new.log`: lịch xen kẽ khóa;
  giao thức cũ được script dựng lại từ code, không phải checkout nguyên snapshot cũ.

## Giới hạn

Script giữ nguyên đường LAW cố định và yêu cầu môi trường Windows/Excel của
Worker; không tự chạy script khi đọc evidence. Chỉ lưu artifact, không lưu
workbook tạm, dữ liệu người dùng hay cây source cũ. Log đỏ 8 FAIL + 5 ERROR
của test transaction mới không được Worker lưu: kết quả đó vẫn Worker-reported.

Prefix SHA256 source tại lúc Main đối chiếu: transaction.py `b36a8d39`,
library_sync.py `d389a32e`, library.py `d4088cb9`. Kết quả review và giới hạn
nghiệm thu thuộc `.agent/HANDOFF.md` và roadmap hiện hành; artifact không tự
đóng A-06 hoặc chứng minh hỗ trợ POSIX/symlink thật.
