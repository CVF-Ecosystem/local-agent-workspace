# packs/ — Gói lĩnh vực / Domain packs

Lõi của package chỉ chứa quy tắc làm việc và các skill dùng chung. Kiến thức riêng của từng lĩnh vực (cảng và logistics,
nhân sự, tài chính...) nằm trong **gói lĩnh vực**: bộ skill và mẫu cài theo nhu cầu vào từng project.

The package core only holds the working rules and the shared skills. Knowledge specific to a domain (port and logistics,
HR, finance...) lives in a **domain pack**: a set of skills and templates installed per project on demand.

**Lưu ý:** năm gói đi kèm hiện là bản thử nghiệm, chưa qua tiếp nhận. Căn cứ pháp lý trong gói được tổng hợp từ trang tin và trang tư vấn, chưa đối chiếu từng điều với văn bản chính thức (Công báo, cổng văn bản của Nhà nước); khi thử, trợ lý AI vẫn có lúc đưa ra câu "trích nguyên văn" không có trong gói. Dùng để tham khảo và soạn nháp; với văn bản trình ký hoặc gửi ra ngoài, tự đối chiếu căn cứ với văn bản chính thức trước khi dùng.

**Note:** the five bundled packs are trial versions that have not been through intake. Their legal basis was compiled from news and advisory sites and has not been checked article by article against official texts (the Official Gazette, government legal portals); in tests the AI assistant still sometimes produced "verbatim quotes" that are not in the pack. Use them for reference and drafting; for documents to be signed or sent outside, check the legal basis against the official texts yourself first.

## Cách dùng / Usage

```text
python tools/pack.py list
python tools/pack.py add <ten-goi>
python tools/pack.py update <ten-goi> --apply
python tools/pack.py remove <ten-goi>
```

Gói cài vào `skills/local/packs/<tên>/` và được ghi trong `.agent/SKILL_INDEX.md` với Scope `PACK`.
A pack installs into `skills/local/packs/<name>/` and is recorded in `.agent/SKILL_INDEX.md` with Scope `PACK`.

## Cấu trúc một gói / Pack layout

```text
packs/<ten-goi>/
├── pack.json          name, version, requires_core, title, description (vi/en), skills
├── README.md          mô tả ngắn / short description
└── skills/<skill-id>/SKILL.md   (+ references/, assets/ nếu cần)
```

## Viết gói mới / Writing a new pack

1. `python tools/pack.py new <ten-goi>` rồi sửa `pack.json`, đổi tên và viết skill. / then edit `pack.json`, rename and write the skills.
2. `python tools/pack.py check <ten-goi>` để kiểm tra cấu trúc. Cấu trúc đạt không phải tiếp nhận. / to validate the structure. A passing structure is not intake.
3. Quy tắc nhận một gói: theo chuẩn tiếp nhận chung ở `skills/README.md` (sáu điều kiện, so với native hoặc cách đang có). Riêng gói
   dùng chung còn cần: ít nhất ba việc thật của lĩnh vực đó; skill qua thử trong ứng dụng agent thật; skill id không trùng skill của
   package; nghiệp vụ đặc thù đơn vị nằm trong skill của project, không trong gói dùng chung.
   Rule for accepting a pack: follow the shared intake standard in `skills/README.md` (six conditions, compared with native or the way
   currently used). A shared pack also needs: at least three real tasks in that domain; its skills tried in a real agent app; skill ids
   that do not clash with the package's skills; unit-specific rules kept in the project's own skills, not in a shared pack.

## Tiếp nhận gói / Pack intake

Khối `intake` trong `pack.json` là **lời khai của gói** (người viết gói nói gì về hồ sơ của nó), không phải quyết định của người dùng.
`pack.py add` mặc định ghi Status `REVIEW` (dùng thử); `tools/install_skills.py` không chép skill của nó sang ứng dụng.
Muốn nhận gói cho project này, người dùng xem hồ sơ rồi chỉ cần **một lệnh**: `python tools/pack.py add <tên> --confirm` (cài và nhận), hoặc
`python tools/pack.py confirm <tên>` với gói đã cài (`--dry-run` chỉ xem). Chỉ chạy khi lời khai hợp lệ (nếu không thì dừng trước khi ghi gì);
nó ghi `AVAILABLE` và gắn xác nhận với dấu vân tay nội dung đang cài. Gói đổi nội dung: `pack.py update <tên> --apply --confirm` xét xong là
nhận lại luôn. Trong bảng điều khiển là nút "Cài và nhận gói" với một hộp thoại.
The `intake` block in `pack.json` is **the pack's own claim** (what the pack author says about its record), not the user's decision.
`pack.py add` records `REVIEW` by default (trial); `tools/install_skills.py` does not copy its skills into apps. To accept a pack for this
project, the user reads the record and needs just **one command**: `python tools/pack.py add <name> --confirm` (install and accept), or
`python tools/pack.py confirm <name>` for an installed pack (`--dry-run` only shows). It runs only for a valid claim (otherwise it stops
before writing anything); it records `AVAILABLE` and binds the confirmation to a fingerprint of the installed content. A pack whose content
changed: `pack.py update <name> --apply --confirm` accepts it again right after you reviewed. In the control panel it is the "Install and
accept" button with one dialog.

```json
"intake": {
  "decision": "ADD_MISSING_PART",
  "version": "0.2.0",
  "relation": "SUPPLEMENT",
  "record": "references/intake-record.md",
  "comparison": "",
  "root_grant": ""
}
```

- `decision`: `ADD_MISSING_PART`, `PROJECT_ONLY`, `ROOT_ELIGIBLE` (có thể xác nhận / can be confirmed), `DEFER` (vẫn là ứng viên / stays a candidate),
  `REUSE_NO_IMPORT`, `REJECT_VERSION` (không cài / not installed). Ý nghĩa ở / meaning in `skills/README.md`.
- `version`: bản mà quyết định áp dụng; đổi `version` của gói mà chưa xét lại thì lời khai không còn hợp lệ cho bản mới. / the version the
  decision covers; a new pack version that has not been reviewed makes the claim invalid for it.
- `relation`: `SUPPLEMENT`, `REPLACEMENT`, `FALLBACK`, `UNKNOWN`. `UNKNOWN` không thể xác nhận; `REPLACEMENT` cần `comparison` (bằng
  chứng so với native hoặc cách đang dùng). / `UNKNOWN` cannot be confirmed; `REPLACEMENT` needs `comparison` (evidence against native
  or the way currently used).
- `record`, `comparison`: đường dẫn local tương đối (trong gói hoặc project), không thoát thư mục, tới một file có thật. Chuỗi khác
  (`x`, URL, đường dẫn tuyệt đối, `..`) chưa giải được nên gói vẫn là ứng viên. / a relative local path (inside the pack or project) that
  stays inside and points to a real file. Anything else (`x`, a URL, an absolute path, `..`) does not resolve, so the pack stays a candidate.
- `root_grant`: chỉ với `ROOT_ELIGIBLE`, ghi ai cấp quyền đưa vào bộ mẫu gốc và khi nào; chỉ là khai báo, không chứng minh đã có hành động
  ghi gốc. / only with `ROOT_ELIGIBLE`: who granted putting it into the template root and when; it is metadata and does not prove a root write.

Công cụ chỉ kiểm các điểm trên và gắn xác nhận với nội dung; nó không đánh giá chất lượng bằng chứng (dấu vân tay chỉ nhận ra thay đổi).
Xác nhận hết hiệu lực khi: nội dung gói đã cài đổi (kể cả cùng số phiên bản, kể cả sửa tay bản đã cài hay thêm script), gói lên phiên bản
mới, hoặc hồ sơ không còn ở mức đã nhận. Khi đó skill về `REVIEW` (cập nhật) hoặc bị chặn xuất (sửa tay) cho tới khi người dùng xét phần đổi
rồi xác nhận lại. Hồ sơ từ chối đúng bản đã cài thì bản đó không còn xuất được và `pack.py check` báo; từ chối một bản khác chưa cài không
ảnh hưởng bản đã xác nhận. Gõ tay `AVAILABLE` vào `.agent/SKILL_INDEX.md` không thay cho xác nhận: skill của gói vẫn không xuất được. Gói cài
bằng bản cũ của công cụ (đã ghi `AVAILABLE`, chưa có xác nhận) cũng vậy: chạy `pack.py confirm <tên>` hoặc để nguyên là bản thử.
The tool checks only these points and binds the confirmation to content; it does not judge the quality of the evidence (the fingerprint only
detects change). The confirmation lapses when: the installed pack content changes (even under the same version number, even a hand edit of the
installed copy or an added script), the pack moves to a new version, or the record no longer claims acceptance. The skills then return to
`REVIEW` (update) or are blocked from export (hand edit) until the user reviews the change and confirms again. A record that refuses the
installed version stops that version from being exported and `pack.py check` reports it; refusing a different, not-installed version does not
affect the confirmed one. Typing `AVAILABLE` into `.agent/SKILL_INDEX.md` is no substitute for confirming: the pack skills still cannot be
exported. The same goes for a pack installed by an older tool version (recorded `AVAILABLE`, never confirmed): run `pack.py confirm`, or leave
it as a trial.
