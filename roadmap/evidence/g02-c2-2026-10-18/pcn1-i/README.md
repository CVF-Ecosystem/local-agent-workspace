# P-CN1-I + S4-min — evidence (Worker, 18/10/2026)

Trạng thái: IMPLEMENTED_PENDING_REVIEW. Dữ liệu giả trong thư mục tạm mới; không đụng tài liệu thật. Máy: Windows 11
(10.0.26200), ổ project và %TEMP% là NTFS cố định; có thêm một ổ FAT32 cố định (G:) chỉ được đọc danh sách gốc.

| File | sha256 (16 ký tự đầu) | Nội dung |
|---|---|---|
| windows_proofs.py | dd635b092e786d41 | script proof Windows/NTFS (chạy `python -I`) |
| windows_proofs.log | d3786de3becee68a | 11 proof REQUESTED/OBSERVED/VERDICT, đều PASS |
| test_publish_new_py311.log | b41aef0708b33305 | `python -B -W error::ResourceWarning -m unittest -v tests.test_publish_new` trên Python 3.11.9: 35 chạy, OK, 1 skip (ca non-Windows) |
| test_publish_new_py313.log | f3c45b9f32e645fc | cùng lệnh trên CPython 3.13.12: OK, 1 skip |

Code được kiểm: tools/publish_new.py `c0f35aaf3d8280d1`, tests/test_publish_new.py `462c2786555e69d6`.

Giới hạn: không chạy Python 3.8 thật (chỉ `ast.parse(feature_version=(3,8))`); không thử ổ mạng, OneDrive/placeholder,
ReFS, exFAT, POSIX; chưa đo antivirus/indexer giữ staged; không có proof chống process có quyền ghi `.agent/runtime/`.
Log đã che đường dẫn có tên người dùng.

## Corrective 18/10/2026 (sau review CHANGES_REQUIRED) — IMPLEMENTED_PENDING_REVIEW

Phần trên là lịch sử lượt Worker đầu; code/test đã đổi, nên bảng hash trên không còn là hash hiện hành.

| File | sha256 (16 ký tự đầu) | Nội dung |
|---|---|---|
| corrective_proofs.py | 18e841c6959f9397 | đo lại đúng ba primitive đã đổi (chạy `python -I`) |
| corrective_proofs.log | d699a7b9262f893a | 3 proof PASS: xóa qua handle đã kiểm (chỉ bỏ tên staged, link đích còn, remove/rename bị chặn winerror 32, file khác identity ⇒ CHANGED); pin thư mục (rmdir/rename bị chặn, đường dẫn là junction ⇒ UNSAFE); root junction thấy là reparse |
| test_publish_new_corrective_py311.log | 55353366ddef5be1 | `python -B -W error::ResourceWarning -m unittest -v tests.test_publish_new`, Python 3.11.9: 49 chạy, OK, 1 skip |

Code được kiểm: tools/publish_new.py `971883b677bf4dd9`, tests/test_publish_new.py `278d1328062432d4`. Không chạy lại windows_proofs.py (khóa, share mode,
identity, NTFS, FAT32: primitive không đổi). Python 3.13 không có trên máy ở lượt này nên không chạy lại; Python 3.8 chỉ `ast.parse`.
