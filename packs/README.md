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
2. `python tools/pack.py check <ten-goi>` để kiểm tra cấu trúc. / to validate the structure.
3. Quy tắc nhận một gói: chỉ thêm khi đã có ít nhất ba việc thật của lĩnh vực đó; skill phải qua thử trong ứng dụng agent thật;
   skill id không trùng skill của package; nghiệp vụ đặc thù đơn vị nằm trong skill của project, không trong gói dùng chung.
   Rule for accepting a pack: add it only after at least three real tasks in that domain; its skills must be tried in a real agent app;
   skill ids must not clash with the package's skills; unit-specific rules belong in the project's own skills, not in a shared pack.
