# Dùng với dự án có sẵn và nâng cấp bộ công cụ

Giữ cấu trúc đang hoạt động. Thêm phần hữu ích trước; tổ chức lại chỉ khi thực sự
có lợi. Không cần tạo dự án mới trong ứng dụng chỉ để sử dụng bộ thư mục này.

## 1. Giữ một bản sao trước khi thay đổi

Sao lưu thư mục hoặc các file sẽ sửa. Xác định file hướng dẫn, trạng thái, đầu ra
và kỹ năng đang dùng để không làm mất phần riêng của dự án.

Không cần dùng Git hoặc công cụ coding để làm việc này; một bản sao thư mục là đủ
cho nhu cầu đối chiếu và quay lại khi cần.

## 2. Thêm có chọn lọc, không chép đè toàn bộ

Giải nén bản của bộ công cụ cần dùng ra thư mục riêng để so sánh. Khi có file trùng tên, hợp nhất phần
hữu ích thay vì chấp nhận ghi đè hàng loạt.

| Đang có trong dự án | Cách xử lý gợi ý |
|---|---|
| `AGENTS.md`, `PROJECT.md` | Giữ ngữ cảnh/hướng dẫn riêng; thay đoạn chung cũ chỉ khi phù hợp. |
| `CLAUDE.md`, `GEMINI.md` | Giữ phần riêng của provider; adapter chỉ nối đến hướng dẫn chung. |
| `.agent/STATE.md`, `HANDOFF.md` | Giữ trạng thái thật, không thay bằng mẫu rỗng của ZIP. |
| `INDEX.md`, `SKILL_INDEX.md` | Giữ mục hiện có, bổ sung mục mới; không tạo hàng trùng. |
| `skills/`, nguồn, output | Giữ nguyên tài nguyên hiện hành; không di chuyển chỉ để giống cây mẫu. |
| `README.md`, `docs/`, `START_HERE.html` | Giữ nội dung riêng; thêm bộ hướng dẫn ở vị trí phù hợp, giữ liên kết nội bộ. |

Lần đầu đưa bộ công cụ vào dự án đã có (chưa có `VERSION` hay `.agent/`), dùng công cụ thay vì chép tay: từ thư mục bộ công cụ chạy
`python tools/adopt_project.py --project "đường dẫn" --name "Tên project"` để xem báo cáo, thêm `--apply` để ghi. Công cụ chỉ thêm file
còn thiếu; `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` cũ giữ nguyên và vẫn có hiệu lực; bản của bộ công cụ khác nội dung được lưu thành `<tên>.new` để hợp nhất, kể cả khi chọn tiếng Anh.
Nếu bản `.new` đã tồn tại và khác nội dung, công cụ dừng trước khi ghi. Kết quả có hướng dẫn chưa hợp nhất sẽ báo rõ “CẦN HỢP NHẤT”;
file khác bị trùng giữ nguyên của bạn và bản của bộ công cụ lưu thành `<tên>.new`; kỹ năng riêng sẵn có được thêm dòng vào `SKILL_INDEX.md` với Status `REVIEW` (trợ lý AI vẫn dùng được trong dự án; bạn xác nhận rồi đổi sang `AVAILABLE`). Nếu việc này bị gián đoạn, xem mục 9.
Kỹ năng dùng chung ở `skills/local/shared/`, kỹ năng chứa thông tin riêng của đơn vị ở `skills/local/project/`; không chép nội dung chung vào kỹ năng riêng.

Nếu đổi vị trí thư mục bộ công cụ hoặc tài liệu hướng dẫn, nhờ trợ lý AI cập nhật những
đường dẫn liên quan; không cần ép dự án cũ vào cây thư mục mới.

## 3. Cập nhật lên phiên bản mới của bộ công cụ

Mỗi dự án ghi phiên bản của bộ công cụ đang dùng trong `.agent/PACKAGE_INFO.json` (file này do
`tools/init_project.py` tạo; dự án có sẵn chưa có thì tạo tay, ghi `"version"` theo bản đã dùng). Bản bộ công cụ
nằm trong file `VERSION`; `CHANGELOG.md` cho biết điều gì đổi giữa các bản.

Cách nhanh và an toàn: dùng công cụ nâng cấp. Nó so ba bên (bản gốc cũ, bản hiện tại của dự án, bản mới), chỉ báo cáo
trước rồi mới ghi khi bạn thêm `--apply`.

- Bước 1: Giải nén bản mới ra thư mục riêng; đọc `CHANGELOG.md` từ bản đang dùng đến bản mới.
- Bước 2: Từ thư mục bản mới, chạy `python tools/upgrade_package.py --project "đường dẫn project cũ"` để xem báo cáo.
   File chưa ai sửa sẽ được cập nhật, file mới được thêm, file bạn đã sửa được giữ nguyên.
- Bước 3: Nếu báo cáo ổn, chạy lại kèm `--apply`. File mà bạn đã sửa và bộ công cụ cũng đổi sẽ không bị ghi đè: bản mới
   được lưu thành `<tên>.new` để bạn hợp nhất, rồi xóa file `.new`. Các file của bạn (`PROJECT.md`, STATE, HANDOFF, INDEX,
   `SKILL_INDEX.md`, `references/`, `working/`, `output/`, `archive/`, kỹ năng riêng) không bao giờ bị đụng tới.
- Bước 4: Chạy `python tools/check_package.py --verify` và mở một phiên thử. Nếu dùng gói lĩnh vực, chạy
   `python tools/pack.py list` để xem gói nào có bản mới (`pack.py update <tên> --apply`).

Nếu lần chạy `--apply` bị gián đoạn (mất điện, máy tắt giữa chừng), công cụ báo CHƯA HOÀN TẤT và không ghi thêm gì; xem mục 9.

Project cũ chưa có `MANIFEST.sha256` (làm từ trước bản này) thì công cụ không so sánh an toàn được: nâng cấp tay, chép có chọn lọc
những file bộ công cụ bạn chưa sửa. Công cụ nâng cấp không xóa file nào (việc gỡ thay đổi khi phục hồi một giao dịch dở xem ở mục 9); file không còn trong bộ công cụ mới chỉ được liệt kê để bạn tự quyết định.

Không thay STATE, HANDOFF, nguồn và đầu ra thật của dự án
bằng các file mẫu của bản mới.

## 4. Rút gọn ngữ cảnh cũ khi hữu ích

Nội dung ổn định về mục đích, người đọc, mẫu và giới hạn có thể giữ trong PROJECT.
Trạng thái hiện tại vào STATE; việc bàn giao vào HANDOFF; nguồn vào index hoặc giữ
vị trí cũ. Không cần chia lại tất cả tài liệu ngay trong một lần.

Nếu có nhật ký dài, chỉ đưa trạng thái hiện tại và quyết định đã xác nhận vào STATE.
Giữ lịch sử gốc để tham khảo khi cần, không nạp toàn bộ vào mỗi phiên.

## 5. Giữ nguồn và kỹ năng đang hoạt động

INDEX có thể trỏ đến nguồn ở vị trí hiện tại. Không cần dời cả kho vào `references/`.

Kỹ năng native đang có không cần copy vào bộ công cụ. Kỹ năng tự xây và external kỹ năng
có thể giữ nguyên vị trí, chỉ ghi nơi tìm và khi nào hữu ích. Với kỹ năng thêm mới,
xem đủ mục đích, nguồn gốc, dependency và điểm đáng chú ý; không làm lại việc nhập
kỹ năng mỗi lần dùng.

Nếu sao chép tài nguyên từ ngoài, giữ nguồn và điều khoản của phần được nhập. Khi
chỉ biên soạn mới theo ý tưởng tham khảo, ghi rõ thay vì gọi đó là bản sao upstream.

## 6. Kết nối với phiên làm việc hiện tại

Giữ dự án hiện có trong ứng dụng. Cấp quyền thư mục bằng khả năng ứng dụng đang
hỗ trợ; không coi một đoạn instruction là đã tạo quyền truy cập file.

Có thể dùng đoạn mở đầu ngắn:

```text
Project này dùng thư mục local để giữ tài liệu và ngữ cảnh làm việc.
Tham khảo AGENTS.md và PROJECT.md khi cần; dùng STATE để tiếp tục việc đang dở.
Chọn nguồn, công cụ và skill phù hợp, gồm cả native skills đang có.
Giữ các quyết định đã chốt và chỉ làm phần tôi giao.
```

Với Gemini qua Antigravity, không giả định cách nạp `GEMINI.md` giống Gemini CLI.
Với mọi trợ lý AI, có thể yêu cầu mở `AGENTS.md` trực tiếp khi hướng dẫn chưa được nạp.
Không sửa file cấu hình global hay thay toàn bộ thư viện kỹ năng của provider.

## 7. Thử một phiên và điều chỉnh đúng chỗ

Mở phiên mới, giao một việc nhỏ đang cần làm. Khi cần kiểm tra khả năng tiếp tục,
có thể hỏi:

```text
Dựa vào STATE và HANDOFF nếu có, cho tôi biết ngắn gọn việc đang dở và bước tiếp theo.
Sau đó thực hiện [việc cụ thể]. Chưa cần đọc những nguồn không liên quan.
```

Quan sát việc dùng đúng nguồn, giữ quyết định cũ và hoàn thành đúng phạm vi.
Trợ lý AI biết rõ file hoặc kỹ năng thì có thể mở trực tiếp, không cần chứng minh đã đi
qua mọi index. Nếu hướng dẫn mới làm rườm rà, chỉnh hoặc bỏ đúng đoạn gây nhiễu.

## 8. Quay lại khi cần

Dùng bản sao đã giữ để phục hồi phần không phù hợp. Có thể chỉ giữ một kỹ năng hoặc
bộ hướng dẫn HTML hữu ích, không cần nâng mọi phần cùng lúc. Không xóa trạng thái
hoặc tài liệu mới phát sinh trong quá trình thử khi chưa xem lại.

## 9. Khi việc ghi bị gián đoạn

Công cụ ghi qua một giao dịch có nhật ký: kiểm tra trước, sao lưu các file sẽ đổi, rồi mới ghi từng file. Nếu máy tắt, mất điện hoặc ổ đĩa lỗi giữa chừng, lần chạy sau sẽ báo **CHƯA HOÀN TẤT** và không ghi thêm gì cho đến khi bạn xử lý giao dịch đó.

Chọn một trong hai cách:

- Dòng lệnh, chạy trong thư mục dự án: `python tools/transaction.py status` để xem mã giao dịch còn dở. Sau đó chạy `python tools/transaction.py resume <mã>` để hoàn tất, hoặc `python tools/transaction.py rollback <mã>` để phục hồi.
- Bảng điều khiển: mở trang "Tình trạng ứng dụng", mục "Thao tác lưu file bị gián đoạn", rồi bấm "Tiếp tục" hoặc "Phục hồi". Trang Tổng quan cũng hiện thông báo khi có giao dịch dở.

Phục hồi làm như sau:

- File bạn chưa sửa sau sự cố được đưa về bản gốc. File mới do lần chạy dở tạo ra, nếu bạn chưa sửa, sẽ bị gỡ.
- File bạn đã sửa sau sự cố được giữ nguyên, không bị ghi đè. Bản gốc của các file này nằm trong `.agent/runtime/transactions/<mã>/backup/`. Giao dịch khi đó có trạng thái `rollback_partial`: bạn so sánh và khôi phục tay nếu cần. Trạng thái này không chặn các việc khác.
- Giao dịch đã hoàn tất thì không phục hồi được, vì không còn bản sao lưu. Muốn có kết quả khác, chạy lại thao tác.

Nếu công cụ báo **CHƯA GHI GÌ**, không file nào trong dự án đã bị đổi. Nếu còn nghi ngờ trước khi phục hồi, hãy giữ một bản sao của thư mục dự án (mục 1).

## 10. Nền tảng đã kiểm và chính sách phiên bản

Đã kiểm: Windows 11 với Python 3.11. Chưa kiểm: macOS; Python 3.8 (công cụ được viết để chạy từ Python 3.8, nhưng chưa chạy thử trên 3.8); các hệ điều hành và phiên bản Python khác. Nếu gặp lỗi trên nền tảng chưa kiểm, báo lại kèm kết quả của `python tools/check_package.py --verify` và gói chẩn đoán từ bảng điều khiển.

Số phiên bản có dạng MAJOR.MINOR.PATCH, nằm trong file VERSION:

- MAJOR tăng khi có thay đổi không tương thích ngược: đổi cấu trúc thư mục .agent hoặc của dự án, đổi định dạng MANIFEST.sha256, đổi định dạng kết quả của công cụ, hoặc bỏ một lệnh hay cờ đã có.
- MINOR tăng khi thêm tính năng tương thích ngược: công cụ, kỹ năng, cờ hoặc mục nội dung mới.
- PATCH tăng khi sửa lỗi, sửa tài liệu hoặc cập nhật mẫu mà không đổi dữ liệu của dự án.

Mỗi bản có mục riêng trong CHANGELOG.md. Hãy đọc mục đó trước khi nâng cấp.
