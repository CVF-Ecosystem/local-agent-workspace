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
| `AGENTS.md`, `PROJECT.md` | Giữ ngữ cảnh/hướng dẫn riêng, kể cả ngoại lệ thư mục nguồn cũ và phạm vi agent phụ đã ghi; thay đoạn chung cũ chỉ khi phù hợp. |
| `CLAUDE.md`, `GEMINI.md` | Giữ phần riêng của provider; adapter chỉ nối đến hướng dẫn chung. |
| `.agent/STATE.md`, `HANDOFF.md` | Giữ trạng thái thật, không thay bằng mẫu rỗng của ZIP. |
| `INDEX.md`, `SKILL_INDEX.md` | Giữ mục hiện có, bổ sung mục mới; không tạo hàng trùng. |
| `.agent/EXECUTION_PROFILE.json` | Đã có thì giữ nguyên từng byte, không tạo `.new`. Chưa có thì công cụ chỉ tạo khi `PROJECT.md` có đúng một dòng quyền gọi agent phụ; dòng văn xuôi cũ không bị đổi thành grant, cần migration tường minh (`tools/execution_profile.py`). Thiếu dòng quyền hoặc mất profile: xem “Profile quyền gọi vai” ở mục 3. |
| `skills/`, nguồn, output | Giữ nguyên tài nguyên hiện hành; không di chuyển chỉ để giống cây mẫu. |
| `README.md`, `docs/`, `START_HERE.html` | Giữ nội dung riêng; thêm bộ hướng dẫn ở vị trí phù hợp, giữ liên kết nội bộ. |

Lần đầu đưa bộ công cụ vào dự án đã có (chưa có `VERSION` hay `.agent/`), dùng công cụ thay vì chép tay: từ thư mục bộ công cụ chạy
`python tools/adopt_project.py --project "đường dẫn" --name "Tên project"` để xem báo cáo, thêm `--apply` để ghi. Công cụ chỉ thêm file
còn thiếu; `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` cũ giữ nguyên và vẫn có hiệu lực; bản của bộ công cụ khác nội dung được lưu thành `<tên>.new` để hợp nhất, kể cả khi chọn tiếng Anh.
Nếu bản `.new` đã tồn tại và khác nội dung, công cụ dừng trước khi ghi. Kết quả có hướng dẫn chưa hợp nhất sẽ báo rõ “CẦN HỢP NHẤT”;
file khác bị trùng giữ nguyên của bạn và bản của bộ công cụ lưu thành `<tên>.new`; kỹ năng riêng sẵn có được thêm dòng vào `SKILL_INDEX.md` với Status `REVIEW` (trợ lý AI vẫn dùng được trong dự án; bạn xác nhận rồi đổi sang `AVAILABLE`). Cách xử lý các file `.new` xem ở mục 3. Nếu việc này bị gián đoạn, xem mục 9.
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
   được lưu thành `<tên>.new` để bạn xem và quyết định, cách xử lý tùy loại file (xem “Xử lý file `.new`” ngay dưới). Các file của bạn
   (`PROJECT.md`, STATE, HANDOFF, INDEX, `references/`, `working/`, `output/`, `archive/`, kỹ năng riêng) không bị thay bằng bản mẫu package. Các dòng skill index hiện có được giữ; công cụ có thể thêm dòng skill chung còn thiếu và cập nhật thông tin nâng cấp trong `PACKAGE_INFO.json`.
- Bước 4: Chạy `python tools/check_package.py --verify` và mở một phiên thử. Nếu dùng gói lĩnh vực, chạy
   `python tools/pack.py list` để xem gói nào có bản mới (`pack.py update <tên> --apply`).

**Xử lý file .new.** `<tên>.new` là bản của bộ công cụ được để cạnh file của bạn. Nó có thể cũ, hoặc đã được ai đó sửa tay; đừng mặc định đó là bản mới nhất.
Trang “Chờ hợp nhất” của bảng điều khiển liệt kê các file này; nút “So sánh” không sửa nội dung hai file, nhưng thao tác có thể được ghi vào lịch sử. Việc làm được tùy loại file:

- **Tám file hướng dẫn trong thư mục docs** (bốn file `HUONG_DAN_*_VI.md` và bốn file trong `docs/en/`: `NEW_PROJECT_GUIDE`, `DAILY_USE_GUIDE`, `SKILLS_GUIDE`, `EXISTING_PROJECT_UPGRADE_GUIDE`):
  “Dùng bản mới (giữ .new)” lưu bản của bạn vào `.agent/merge-backups/<id>/` rồi thay bằng bản mới; file `.new` vẫn còn chờ.
  “Lưu .new và kết thúc chờ” giữ nguyên file của bạn, lưu cả hai bản vào `.agent/merge-backups/<id>/` rồi chuyển `.new` khỏi danh sách chờ.
  “Giữ bản của tôi” chỉ đóng cửa sổ, không ghi gì và `.new` vẫn còn chờ. Mọi lựa chọn ghi đều có xem trước và chờ bạn xác nhận. Nếu bạn tự sửa file, hãy xem trước lại trước khi kết thúc.
- **File hướng dẫn cho trợ lý AI** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` và các file cùng tên trong `en/`): không có “Dùng bản mới”. Việc lưu `.new` làm bằng nút “Giữ bản hiện hành, lưu .new” ngay tại hàng của file.
  Việc này không đưa nội dung mới vào file đang dùng và không cấp thêm quyền cho trợ lý AI. Muốn dùng nội dung mới, tự sửa file hiện hành rồi xem trước lại.
  Danh sách hết `.new` không có nghĩa trợ lý nào cũng sẽ không đọc `.new` hay bản lưu, và không có nghĩa hướng dẫn đã được kiểm lại.
- **Hai script của bộ công cụ** (`tools/audit_scripts.py` và `skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py`): không có “Dùng bản mới”. Việc lưu `.new` làm bằng nút “Giữ bản hiện hành, lưu .new” ngay tại hàng của file, và chỉ khi file có trong `MANIFEST.sha256` của project.
  Công cụ chỉ lưu `.new` như văn bản: không mở, biên dịch hay chạy script, và không đưa nội dung mới vào script đang dùng. Danh sách hết `.new` không có nghĩa script đúng, an toàn, chạy được, đã được tiếp nhận hay được phép dùng.
  Muốn dùng nội dung mới, tự sửa script hiện hành rồi kiểm theo quy tắc script của bạn. Chỉ đúng hai file này; script khác không được suy theo thư mục hay theo số lần dùng.
- **File khác của bộ công cụ** (script khác trong `tools/`, ví dụ `tools/check_output.py`; kỹ năng dùng chung và các file khác của bộ công cụ): bảng điều khiển chỉ cho so sánh và chép đường dẫn, chưa có nút thay hay kết thúc, và công cụ không tự hợp nhất. Có một đường thủ công giữ nguyên cả hai bản, mô tả từng bước ngay dưới danh sách này. Chưa có cách nghiệm thu chính thức để kết thúc nhóm file này. Không coi cả thư mục `skills/` là của riêng bạn; kỹ năng dùng chung bạn tự thêm chỉ được giữ nguyên, chưa nghiệm thu việc quản lý lâu dài.
- **Thư mục .cvf và file công cụ lõi** (danh sách ở dưới): nếu không tương thích, thiếu hoặc đổi file máy đọc/lõi, hay tài liệu `.cvf` xung đột, công cụ dừng ở bước xem trước và không tạo `.new`. Nếu chưa có `.cvf` hoặc bản hiện tại tương thích, nâng cấp có thể tiếp tục; không có chuyển đổi schema tự động.
- **Gói lĩnh vực đã cài**: xem trước bằng `python tools/pack.py update <tên>`, thêm `--apply` để cập nhật. Khi xung đột, file bạn đã sửa được giữ, bản từ gói mới được lưu thành `.new`; chưa có nút kết thúc cho nhóm này trong bảng điều khiển.

**Cất .new của file khác bằng tay, giữ cả hai bản.** Đường này không phải việc “kết thúc chính thức”: không đổi `MANIFEST.sha256`, không làm bảng điều khiển ghi nhận đã xử lý và không là bằng chứng file đã được kiểm hay chấp nhận. Ví dụ với `tools/check_output.py.new`, đã đo trên một project 1.8.0 giả đã nâng cấp (Windows, PowerShell; đường dẫn dùng dấu `/`):

- Bước 1, so sánh `tools/check_output.py` (của bạn) với `tools/check_output.py.new` bằng công cụ bạn quen (trình soạn thảo, hoặc `fc tools/check_output.py tools/check_output.py.new`). `.new` có thể cũ hoặc đã bị sửa tay. Không chạy hay biên dịch script để “thử”: chỉ đọc như văn bản.
- Bước 2, tạo một thư mục riêng, **mới**, có mã, trong `archive/`, rồi chép cả hai bản vào. Lệnh dừng nếu thư mục đã có; khi đó đổi mã, không ghi đè:

```powershell
$id = Get-Date -Format yyyyMMdd-HHmmss
$dir = "archive/nang-cap/$id-check_output"
New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null
Copy-Item tools/check_output.py "$dir/check_output.py.hien-hanh" -ErrorAction Stop
Copy-Item tools/check_output.py.new "$dir/check_output.py.new" -ErrorAction Stop
```

- Bước 3, kiểm hai bản chép đúng từng byte: `Get-FileHash` của file gốc và của bản chép phải trùng nhau. Chưa trùng thì dừng, không làm tiếp.
- Bước 4, chọn rõ một trong hai. **Giữ bản của bạn**: chuyển (không xóa) `.new` vào thư mục vừa tạo rồi kiểm lại. Băm bản đã chuyển phải bằng băm `.new` lúc đầu, và băm `tools/check_output.py` phải bằng băm trước khi làm. **Dùng nội dung mới**: nhờ người phụ trách file đó (người bảo trì bộ công cụ) hợp nhất vào file hiện hành sau khi đối chiếu, rồi cất `.new` như trên. Không thay file hiện hành bằng `.new` khi chưa ai so sánh và xác nhận.

```powershell
Move-Item tools/check_output.py.new "$dir/check_output.py.new.da-chuyen" -ErrorAction Stop
Get-FileHash "$dir/check_output.py.new.da-chuyen", tools/check_output.py
```

- Bước 5, lấy lại `.new` sau này: chép từ thư mục lưu thành một **file mới**, không ghi đè (`Copy-Item` ghi đè file đã có, nên kiểm trước):

```powershell
if (Test-Path tools/check_output.py.new) { throw 'đã có .new, không ghi đè' }
Copy-Item "$dir/check_output.py.new" tools/check_output.py.new -ErrorAction Stop
```

Đã đo: bản chuyển và bản chép khớp từng byte, `tools/check_output.py` giữ nguyên; chạy lại nâng cấp cùng bản package thì báo “Giữ nguyên (bạn đã sửa, package không đổi)” và không tạo lại `.new`; chỉ khi một bản package sau lại đổi file đó mới có `.new` mới. Đừng xóa `.new` để tắt cảnh báo hay sửa `MANIFEST.sha256`.

Các lựa chọn ghi ở trang này mới được kiểm trên Windows 11, ổ đĩa cục bộ; riêng “lưu rồi chuyển” chỉ chạy trên Windows và gồm hai bước có thể bị gián đoạn nửa chừng. Lấy lại bản cũ bằng tay: mở file trong `.agent/merge-backups/<id>/` rồi lưu thành file mới; không có nút hoàn tác.
Đừng xóa `.new` hay sửa `MANIFEST.sha256` chỉ để vượt qua kiểm tra. Lần nâng cấp sau có thể giữ `.new` cũ, hoặc dừng khi `.new` khác với bản mới của bộ công cụ.

Dòng thứ hai của báo cáo cho biết quan hệ giữa “nhãn phiên bản” và “baseline nội dung gói” (các đường dẫn và hash trong `MANIFEST.sha256` đã cài so với bản mới), nên một dòng “vX -> vX” không còn bị hiểu là bản mới không có gì khác.
`SAME_LABEL_DIFFERENT_BASELINE` nghĩa là số phiên bản không tăng nhưng nội dung gói đã đổi. `SAME_LABEL_SAME_BASELINE` chỉ nói gói không đổi so với bản đã cài, không có nghĩa project đã sạch hay đồng bộ: các mục cập nhật, thêm, giữ nguyên, xung đột bên dưới vẫn là việc thực tế.
`UNKNOWN` nghĩa là manifest thiếu, hỏng, trùng đường dẫn hoặc mơ hồ nên không xác định được baseline; công cụ không suy từ nhãn phiên bản. Đây chỉ là mô tả, không đổi cách công cụ quyết định ghi hay giữ file. Baseline gồm toàn bộ manifest, kể cả overlay tiếng Anh (`en/`), nên có thể khác dù phần đang dùng bằng tiếng Việt không đổi. `KNOWN` chỉ nói metadata đọc được và không mơ hồ; không chứng minh file thật khớp, đường dẫn an toàn hay có quyền cập nhật.

Nếu lần chạy `--apply` bị gián đoạn (mất điện, máy tắt giữa chừng), có thể đã ghi một phần. Khi phát hiện giao dịch còn dở ở lần chạy sau, công cụ báo CHƯA HOÀN TẤT; xem mục 9 để tiếp tục hoặc phục hồi.

Project cũ chưa có `MANIFEST.sha256` (làm từ trước bản này) thì công cụ không so sánh an toàn được: nâng cấp tay, chép có chọn lọc
những file bộ công cụ bạn chưa sửa. Công cụ nâng cấp không xóa file nào (việc gỡ thay đổi khi phục hồi một giao dịch dở xem ở mục 9); file không còn trong bộ công cụ mới chỉ được liệt kê để bạn tự quyết định.

Không thay STATE, HANDOFF, nguồn và đầu ra thật của dự án
bằng các file mẫu của bản mới.

Bộ công cụ có thư mục ẩn `.cvf` (kiểm soát điều phối, bản ứng viên v3, chưa kích hoạt, không cấp quyền). Khi đưa vào hoặc nâng cấp, công cụ chỉ **thêm** bản ứng viên này nếu dự án chưa có `.cvf`,
hoặc cập nhật phần tài liệu nếu `.cvf` của dự án đã đúng bản đó. Nếu dự án có `.cvf` khác (phiên bản cũ, thiếu file, đã sửa tay), hoặc file công cụ lõi (`tools/publish_new.py`, `tools/context_update.py`,
`tools/transaction.py`, `tools/result_schema.py`, `tools/current_draft.py`) đã bị sửa, công cụ dừng ngay ở bước xem trước, nêu lý do và không thay đổi gì, kể cả khi thêm `--apply --force`; không có chuyển đổi tự động.
Dùng thư mục giải nén từ ZIP phát hành làm nguồn nâng cấp (MANIFEST phải khớp file thật); thư mục kho nguồn của người bảo trì không dùng được.

**Profile quyền gọi vai (.agent/EXECUTION_PROFILE.json).** Hai trường hợp công cụ không tự tạo profile và giữ chặn; mỗi trường hợp có bước xử lý riêng:

- *`PROJECT.md` chưa có dòng quyền gọi agent phụ* (thường gặp ở project làm từ bản 1.8): công cụ không đoán, và agent chỉ thêm dòng này khi bạn giao việc đó. Nếu bạn chọn không giao quyền gọi agent phụ, thêm vào `PROJECT.md` đúng một dòng `- Phạm vi được giao cho agent phụ: Không có` (bản tiếng Anh: `- Standing scope for sub-agents: None`). Rồi từ thư mục package MỚI chạy `python tools/upgrade_package.py --project "đường dẫn project"` để xem trước (thấy dòng “Tạo .agent/EXECUTION_PROFILE.json (owner quyền PROJECT, chưa có grant)”), thêm `--apply` để ghi. `PROJECT.md` và `STATE.md` không bị ghi đè; profile mới chưa có grant nào, nên chưa cấp quyền gọi vai nào. Đã đo trên project 1.8.0 giả: trước khi thêm dòng, `execution_profile.py status` báo `PROFILE_ABSENT` kèm các bước này; sau `--apply`, `status` báo `OK` với `NO_GRANT` cho cả ba vai.
- *`PROJECT.md` đã trỏ tới profile nhưng file profile không còn*: giữ chặn. Khôi phục **đúng file profile từ bản sao lưu** của chính project (giữ nguyên bytes) trước khi cấu hình; sau đó `python tools/execution_profile.py status` phải về `OK`. Không có bản sao lưu thì giữ nguyên trạng thái chặn: không dựng profile mẫu, không đổi dòng `PROJECT.md` thành “Không có” để lách (việc đó đặt lại quyền), không dùng `init_project.py --force` (chạy lại khởi tạo trên project đã có). Nhờ chủ sở hữu project xác nhận cách khôi phục hoặc đặt lại quyền; đó là một quyết định riêng, không phải việc của bước nâng cấp.

Dòng văn xuôi cũ (ví dụ “Reviewer được gọi cho mọi việc”) vẫn không bị đọc thành quyền; cần migration tường minh (`tools/execution_profile.py`). Các bước trên không cấp quyền dùng vai nào.

**Không hạ phiên bản.** Hạ project xuống package thấp hơn không được hỗ trợ: công cụ nâng cấp từ chối trước khi ghi, kể cả khi package nguồn không có `.cvf` mà project đã có, và không có bước chuyển đổi ngược. Muốn quay lại bản cũ, khôi phục từ bản sao lưu (mục 1 và 8). Công cụ nâng cấp của chính gói 1.8.0 từ chối project 1.9.0 (đã đo khi không còn file `.new` chờ: thoát mã 1, từng byte của cây project giữ nguyên). Đó là chốt so nhãn `VERSION`, không phải bảo đảm chặn mọi bản chạy cũ; cờ `--force` của công cụ cũ tắt chính chốt đó (đã đo trên bản sao: `--apply --force` ghi thành công và đưa `VERSION` cùng hàng chục file về bản 1.8.0). Vì vậy **không dùng `--force` để hạ phiên bản**. Công cụ 1.8.0 là bytes đã phát hành, không sửa lại được.

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

Nếu công cụ báo **CHƯA GHI GÌ**, các file đích của thao tác chưa bị thay đổi; nhật ký kỹ thuật trong .agent/runtime/ có thể đã được tạo. Nếu còn nghi ngờ trước khi phục hồi, hãy giữ một bản sao của thư mục dự án (mục 1).

## 10. Nền tảng đã kiểm và chính sách phiên bản

Đã kiểm: Windows 11 với Python 3.11. Chưa kiểm: macOS; Python 3.8 (công cụ được viết để chạy từ Python 3.8, nhưng chưa chạy thử trên 3.8); các hệ điều hành và phiên bản Python khác. Nếu gặp lỗi trên nền tảng chưa kiểm, báo lại kèm kết quả của `python tools/check_package.py --verify` và gói chẩn đoán từ bảng điều khiển.

Luồng nháp có kiểm soát (thẻ "Nháp hiện tại", bản ứng viên `.cvf` v3) chỉ chạy trên Windows, ổ NTFS cục bộ, bằng đúng Python đang mở bảng điều khiển và phải có thư viện `jsonschema` từ 4.18 trở lên.
Đã chạy thật: Windows 11, Python 3.11 với jsonschema 4.23.0. Python 3.13 không có jsonschema chỉ mới được kiểm là báo "chưa dùng được" (thẻ không làm gì); chưa chạy luồng thật trên 3.13. Chưa kiểm: macOS, Python 3.8, ổ mạng hoặc thư mục đồng bộ đám mây.
Công cụ không tự cài thư viện và không đổi Python: nếu thiếu, tự cài vào đúng Python hoặc venv của dự án rồi mở lại bảng điều khiển (trang "Tình trạng ứng dụng" ghi lệnh cho đúng Python đó). Các chức năng khác của workspace không phụ thuộc điều kiện này.

Số phiên bản có dạng MAJOR.MINOR.PATCH, nằm trong file VERSION:

- MAJOR tăng khi có thay đổi không tương thích ngược: đổi cấu trúc thư mục .agent hoặc của dự án, đổi định dạng MANIFEST.sha256, đổi định dạng kết quả của công cụ, hoặc bỏ một lệnh hay cờ đã có.
- MINOR tăng khi thêm tính năng tương thích ngược: công cụ, kỹ năng, cờ hoặc mục nội dung mới.
- PATCH tăng khi sửa lỗi, sửa tài liệu hoặc cập nhật mẫu mà không đổi dữ liệu của dự án.

Mỗi bản có mục riêng trong CHANGELOG.md. Hãy đọc mục đó trước khi nâng cấp.
