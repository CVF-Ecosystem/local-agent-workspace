# packs/ — Gói lĩnh vực / Domain packs

Lõi của package chỉ chứa quy tắc làm việc và các skill dùng chung. Kiến thức riêng của từng lĩnh vực (cảng và logistics,
nhân sự, tài chính...) nằm trong **gói lĩnh vực**: bộ skill và mẫu cài theo nhu cầu vào từng project.

The package core only holds the working rules and the shared skills. Knowledge specific to a domain (port and logistics,
HR, finance...) lives in a **domain pack**: a set of skills and templates installed per project on demand.

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

Gói không có khối `intake` hợp lệ cho đúng phiên bản là **ứng viên**: `pack.py add` vẫn cài để dùng thử nhưng ghi Status `REVIEW`, và
`tools/install_skills.py` không chép skill của nó sang ứng dụng. Khi đã có hồ sơ tiếp nhận, thêm vào `pack.json`:
A pack without a valid `intake` block for its exact version is a **candidate**: `pack.py add` still installs it for trial but records
Status `REVIEW`, and `tools/install_skills.py` does not copy its skills into apps. Once an intake record exists, add to `pack.json`:

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

- `decision`: `ADD_MISSING_PART`, `PROJECT_ONLY`, `ROOT_ELIGIBLE` (dùng được / usable), `DEFER` (vẫn là ứng viên / stays a candidate),
  `REUSE_NO_IMPORT`, `REJECT_VERSION` (không cài / not installed). Ý nghĩa ở / meaning in `skills/README.md`.
- `version`: bản mà quyết định áp dụng; đổi `version` của gói mà chưa xét lại thì skill về `REVIEW`. / the version the decision covers;
  a new pack version that has not been reviewed puts the skills back to `REVIEW`.
- `relation`: `SUPPLEMENT`, `REPLACEMENT`, `FALLBACK`, `UNKNOWN`. `UNKNOWN` không bao giờ được nhận; `REPLACEMENT` cần `comparison` (bằng
  chứng so với native hoặc cách đang dùng). / `UNKNOWN` is never accepted; `REPLACEMENT` needs `comparison` (evidence against native or
  the way currently used).
- `record`, `comparison`: chỗ đặt hồ sơ; là đường dẫn trong gói hoặc project thì phải có thật. / where the record is; a path inside the
  pack or project must exist.
- `root_grant`: chỉ với `ROOT_ELIGIBLE`, ghi ai cấp quyền đưa vào bộ mẫu gốc và khi nào; bỏ trống là chưa được cập nhật gốc. / only with
  `ROOT_ELIGIBLE`: who granted putting it into the template root and when; empty means no root update.

Công cụ chỉ kiểm các điểm trên, không đánh giá chất lượng bằng chứng. Trong một project, người dùng cũng có thể nhận một gói chỉ cho
project đó bằng cách đổi Status từ `REVIEW` sang `AVAILABLE` trong `.agent/SKILL_INDEX.md` (ghi chỗ đặt hồ sơ ở cột Notes); trạng thái
này được giữ khi cập nhật trong cùng phiên bản, và trở về `REVIEW` khi gói lên phiên bản mới hoặc khi hồ sơ đã nhận bị rút. Gói cài
trước khi có chuẩn này (đã ghi `AVAILABLE`) không bị công cụ tự đổi, vì cập nhật gốc không tự sửa project cũ; muốn coi là thử nghiệm thì
tự đổi Status sang `REVIEW`. `pack.py check` báo khi bản đang cài bị hồ sơ ghi không nhận.
The tool checks only these points, not the quality of the evidence. In a project, the user may also accept a pack for that project only by
changing its Status from `REVIEW` to `AVAILABLE` in `.agent/SKILL_INDEX.md` (noting where the record is in the Notes column); that status
survives updates within the same version and returns to `REVIEW` when the pack moves to a new version or an accepted record is
withdrawn. Packs installed before this standard (recorded as `AVAILABLE`) are not changed by the tool, because updating the root does
not edit earlier projects; to treat one as a trial, change its Status to `REVIEW` yourself. `pack.py check` reports an installed
version that its intake record refuses.
