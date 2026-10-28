# packs/ — Gói lĩnh vực / Domain packs

Scout, Worker và Reviewer thuộc `roles/` ở gốc bộ mẫu. `packs/` chỉ chứa phần
mở rộng lĩnh vực theo cơ chế tiếp nhận riêng; cài gói không tự cấp quyền gọi vai.

Lõi của package chứa quy tắc, hợp đồng vai trò và skill dùng chung. Kiến thức riêng của từng lĩnh vực (cảng và logistics,
nhân sự, tài chính...) nằm trong **gói lĩnh vực**: bộ skill và mẫu cài theo nhu cầu vào từng project.

The package core holds the working rules, role contracts and shared skills. Knowledge specific to a domain (port and logistics,
HR, finance...) lives in a **domain pack**: a set of skills and templates installed per project on demand.

**Lưu ý:** các gói đi kèm hiện là bản thử nghiệm, chưa qua tiếp nhận. Căn cứ pháp lý ở các gói nghiệp vụ được tổng hợp từ trang tin và trang tư vấn, chưa đối chiếu từng điều với văn bản chính thức; thử nghiệm đã phát hiện câu "trích nguyên văn" không có trong nguồn. Đội phát triển chịu trách nhiệm khắc phục và kiểm trước khi công bố khả năng sẵn dùng. Khi chưa qua nghiệm thu, gói chỉ dùng để tham khảo và soạn nháp; không dùng căn cứ trong gói cho văn bản trình ký hoặc gửi ra ngoài. Khi làm tài liệu thực tế, agent phải đối chiếu đúng nguồn và nêu giới hạn; người có thẩm quyền quyết định việc ký/gửi, không bị giao nhiệm vụ QA sản phẩm.

**Note:** bundled packs remain trial candidates. Legal references in the office-domain packs were compiled from news/advisory sites and have not been checked article by article against official texts; trials found purported verbatim quotations absent from the source. Developers own correction and verification before claiming readiness. Until accepted, packs are for reference and drafting only; do not use their references as the basis for documents submitted for signature or sent externally. For actual documents, the agent checks the relevant sources and states limits; the authorized person decides signing/sending, without taking on product QA.

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
3. Gói gửi từ folder cho người nhận vẫn theo chuẩn chung ở `skills/README.md` (sáu điều kiện, đối chiếu native/cách đang có); riêng
   gói dùng chung cần ít nhất ba việc thật của lĩnh vực đó, được thử trong ứng dụng agent thật; skill id không trùng trong package;
   nghiệp vụ đặc thù đơn vị nằm trong skill của project. Đây là ngưỡng của làn phản hồi người nhận folder.
   Gói do người duy trì được operator giao xây dựng/cập nhật theo làn builder ở `skills/README.md`: không có ngưỡng cứng về số lần dùng,
   nhưng vẫn phải ghi đủ sáu điều kiện. Số việc thật hoặc kiểm ứng dụng không thay bằng chứng về hiệu quả của skill và phạm vi tái dùng.
   For a pack received from a folder, follow the shared intake standard in `skills/README.md` (six conditions, compared with native or
   the way currently used). A shared pack in this recipient-feedback lane also needs at least three real tasks in that domain and a trial
   in a real agent app; its skill ids must not clash with the package's skills, and unit-specific rules belong in project skills.
   A pack created/updated by a maintainer assigned by the operator follows the builder lane in `skills/README.md`: no hard use-count
   threshold, but all six conditions still apply. Task count or application tests cannot replace evidence of the skill's own effect or reuse scope.

Năm câu hỏi của hồ sơ nghiệm thu được chuẩn bị trong [mẫu intake](./_template/references/intake-record.md), tự đi cùng gói mới tạo bằng `pack.py new`. Gói đang có bổ sung vào hồ sơ hiện có khi đến lượt kiểm; không tạo sổ riêng. Kết luận chất lượng phải có evidence của đội dev; `pack.py confirm` là quyết định tiếp nhận vào project sau khi đọc hồ sơ, không thay kiểm chất lượng. Giữ các mã `intake.decision` và cơ chế hiện hành; mẫu chưa điền không phải quyết định tiếp nhận.

The [intake template](./_template/references/intake-record.md) supplies five questions and travels with packs created by `pack.py new`. Existing packs extend their existing records when reviewed, without a new ledger. Developer quality conclusions require evidence; `pack.py confirm` records project acceptance after reading that record and does not replace quality assurance. Existing decision codes and mechanisms remain unchanged; an unfilled template is not an intake decision.

## Chuẩn nội bộ trước feedback / Internal acceptance before feedback

Toàn bộ gói/skill đóng gói sẵn theo trách nhiệm dev ở `skills/README.md`: đội phát triển tự chuẩn bị chuẩn nội dung, ca/đáp án có căn cứ, review và kiểm luồng trên bản giao. Người nhận không phải viết test hoặc tìm người kiểm mới có sản phẩm dùng được. Ngưỡng ba việc của làn phản hồi người nhận không phải gate chặn đội xây dựng hoàn tất nghiệm thu nội bộ. Thành phần công bố sẵn dùng phải đạt đủ sáu điều kiện trong scope; các bản thử giữ giới hạn và status hiện hữu. Không tự bỏ scope đã cam kết hay dùng user confirm thay QA.

Every bundled pack/skill follows developer responsibility in `skills/README.md`: developers prepare content criteria, grounded cases/expected results, review and checks on the delivered workflow. Recipients need not write tests or recruit testers to obtain a usable product. The recipient-feedback lane's three-task threshold does not block builder internal acceptance. Ready-to-use claims require all six conditions within scope; trial candidates retain their limits/status. Never silently drop committed scope or substitute user confirmation for QA.

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
