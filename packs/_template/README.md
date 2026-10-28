# Gói mẫu / Template pack

Đây là khung của một gói lĩnh vực. Không cài trực tiếp; dùng `python tools/pack.py new <tên>` để tạo gói thật.
This is the skeleton of a domain pack. Do not install it; use `python tools/pack.py new <name>` to create a real pack.

Hồ sơ [references/intake-record.md](references/intake-record.md) dành cho đội xây dựng tự đặt chuẩn và ghi bằng chứng trước khi giao. Điền tại chỗ, theo sáu điều kiện trong `skills/README.md`; mẫu chưa có verdict và chưa được nối vào `pack.json.intake`. Khi quyết định tiếp nhận đúng version đã có, dùng schema/mã hiện hành và trỏ `intake.record` tới hồ sơ này. Không dùng mẫu như bằng chứng đã kiểm.

The [record](references/intake-record.md) lets builders define standards and record evidence before delivery. Fill it in place against all six conditions in `skills/README.md`; the template has no verdict and is not wired into `pack.json.intake`. Once a version-bound intake decision exists, use the existing schema/codes and point `intake.record` here. A template is not test evidence.
