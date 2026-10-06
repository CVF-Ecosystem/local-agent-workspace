# Dùng với project có sẵn và nâng cấp package

Giữ cấu trúc đang hoạt động. Thêm phần hữu ích trước; tổ chức lại chỉ khi thực sự
có lợi. Không cần tạo project mới trong ứng dụng chỉ để sử dụng bộ thư mục này.

## 1. Giữ một bản sao trước khi thay đổi

Sao lưu thư mục hoặc các file sẽ sửa. Xác định file hướng dẫn, trạng thái, đầu ra
và skills đang dùng để không làm mất phần riêng của dự án.

Không cần dùng Git hoặc công cụ coding để làm việc này; một bản sao thư mục là đủ
cho nhu cầu đối chiếu và quay lại khi cần.

## 2. Thêm có chọn lọc, không chép đè toàn bộ

Giải nén bản package cần dùng ra thư mục riêng để so sánh. Khi có file trùng tên, hợp nhất phần
hữu ích thay vì chấp nhận ghi đè hàng loạt.

| Đang có trong project | Cách xử lý gợi ý |
|---|---|
| `AGENTS.md`, `PROJECT.md` | Giữ ngữ cảnh/hướng dẫn riêng; thay đoạn chung cũ chỉ khi phù hợp. |
| `CLAUDE.md`, `GEMINI.md` | Giữ phần riêng của provider; adapter chỉ nối đến hướng dẫn chung. |
| `.agent/STATE.md`, `HANDOFF.md` | Giữ trạng thái thật, không thay bằng mẫu rỗng của ZIP. |
| `INDEX.md`, `SKILL_INDEX.md` | Giữ mục hiện có, bổ sung mục mới; không tạo hàng trùng. |
| `skills/`, nguồn, output | Giữ nguyên tài nguyên hiện hành; không di chuyển chỉ để giống cây mẫu. |
| `README.md`, `docs/`, `START_HERE.html` | Giữ nội dung riêng; thêm bộ hướng dẫn ở vị trí phù hợp, giữ liên kết nội bộ. |

Nếu đổi vị trí thư mục package hoặc tài liệu hướng dẫn, nhờ agent cập nhật những
đường dẫn liên quan; không cần ép project cũ vào cây thư mục mới.

## 3. Nâng cấp lên bản package mới

Mỗi project ghi phiên bản package đang dùng trong `.agent/PACKAGE_INFO.json` (file này do
`tools/init_project.py` tạo; project có sẵn chưa có thì tạo tay, ghi `"version"` theo bản đã dùng). Bản package
nằm trong file `VERSION`; `CHANGELOG.md` cho biết điều gì đổi giữa các bản.

Cách nhanh và an toàn: dùng công cụ nâng cấp. Nó so ba bên (bản gốc cũ, bản hiện tại của project, bản mới), chỉ báo cáo
trước rồi mới ghi khi bạn thêm `--apply`.

- Bước 1: Giải nén bản mới ra thư mục riêng; đọc `CHANGELOG.md` từ bản đang dùng đến bản mới.
- Bước 2: Từ thư mục bản mới, chạy `python tools/upgrade_package.py --project "đường dẫn project cũ"` để xem báo cáo.
   File chưa ai sửa sẽ được cập nhật, file mới được thêm, file bạn đã sửa được giữ nguyên.
- Bước 3: Nếu báo cáo ổn, chạy lại kèm `--apply`. File mà bạn đã sửa và package cũng đổi sẽ không bị ghi đè: bản mới
   được lưu thành `<tên>.new` để bạn hợp nhất, rồi xóa file `.new`. Các file của bạn (`PROJECT.md`, STATE, HANDOFF, INDEX,
   `SKILL_INDEX.md`, `references/`, `working/`, `output/`, `archive/`, skill riêng) không bao giờ bị đụng tới.
- Bước 4: Chạy `python tools/check_package.py --verify` và mở một phiên thử. Nếu dùng gói lĩnh vực, chạy
   `python tools/pack.py list` để xem gói nào có bản mới (`pack.py update <tên> --apply`).

Project cũ chưa có `MANIFEST.sha256` (làm từ trước bản này) thì công cụ không so sánh an toàn được: nâng cấp tay, chép có chọn lọc
những file package bạn chưa sửa. Công cụ không xóa file nào; file không còn trong package mới chỉ được liệt kê để bạn tự quyết định.

Không thay STATE, HANDOFF, nguồn và đầu ra thật của project
bằng các file mẫu của bản mới.

## 4. Rút gọn ngữ cảnh cũ khi hữu ích

Nội dung ổn định về mục đích, người đọc, mẫu và giới hạn có thể giữ trong PROJECT.
Trạng thái hiện tại vào STATE; việc bàn giao vào HANDOFF; nguồn vào index hoặc giữ
vị trí cũ. Không cần chia lại tất cả tài liệu ngay trong một lần.

Nếu có nhật ký dài, chỉ đưa trạng thái hiện tại và quyết định đã xác nhận vào STATE.
Giữ lịch sử gốc để tham khảo khi cần, không nạp toàn bộ vào mỗi phiên.

## 5. Giữ nguồn và skills đang hoạt động

INDEX có thể trỏ đến nguồn ở vị trí hiện tại. Không cần dời cả kho vào `references/`.

Skill native đang có không cần copy vào package. Skill tự xây và external skill
có thể giữ nguyên vị trí, chỉ ghi nơi tìm và khi nào hữu ích. Với skill thêm mới,
xem đủ mục đích, nguồn gốc, dependency và điểm đáng chú ý; không làm lại việc nhập
skill mỗi lần dùng.

Nếu sao chép tài nguyên từ ngoài, giữ nguồn và điều khoản của phần được nhập. Khi
chỉ biên soạn mới theo ý tưởng tham khảo, ghi rõ thay vì gọi đó là bản sao upstream.

## 6. Kết nối với phiên làm việc hiện tại

Giữ project hiện có trong ứng dụng. Cấp quyền thư mục bằng khả năng ứng dụng đang
hỗ trợ; không coi một đoạn instruction là đã tạo quyền truy cập file.

Có thể dùng đoạn mở đầu ngắn:

```text
Project này dùng thư mục local để giữ tài liệu và ngữ cảnh làm việc.
Tham khảo AGENTS.md và PROJECT.md khi cần; dùng STATE để tiếp tục việc đang dở.
Chọn nguồn, công cụ và skill phù hợp, gồm cả native skills đang có.
Giữ các quyết định đã chốt và chỉ làm phần tôi giao.
```

Với Gemini qua Antigravity, không giả định cách nạp `GEMINI.md` giống Gemini CLI.
Với mọi agent, có thể yêu cầu mở `AGENTS.md` trực tiếp khi hướng dẫn chưa được nạp.
Không sửa file cấu hình global hay thay toàn bộ thư viện skill của provider.

## 7. Thử một phiên và điều chỉnh đúng chỗ

Mở phiên mới, giao một việc nhỏ đang cần làm. Khi cần kiểm tra khả năng tiếp tục,
có thể hỏi:

```text
Dựa vào STATE và HANDOFF nếu có, cho tôi biết ngắn gọn việc đang dở và bước tiếp theo.
Sau đó thực hiện [việc cụ thể]. Chưa cần đọc những nguồn không liên quan.
```

Quan sát việc dùng đúng nguồn, giữ quyết định cũ và hoàn thành đúng phạm vi.
Agent biết rõ file hoặc skill thì có thể mở trực tiếp, không cần chứng minh đã đi
qua mọi index. Nếu hướng dẫn mới làm rườm rà, chỉnh hoặc bỏ đúng đoạn gây nhiễu.

## 8. Quay lại khi cần

Dùng bản sao đã giữ để phục hồi phần không phù hợp. Có thể chỉ giữ một skill hoặc
bộ hướng dẫn HTML hữu ích, không cần nâng mọi phần cùng lúc. Không xóa trạng thái
hoặc tài liệu mới phát sinh trong quá trình thử khi chưa xem lại.
