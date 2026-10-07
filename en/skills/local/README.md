# skills/local/

Skills built/maintained by the user or by the agent in this system.

- `shared/`: reusable across many projects.
- `project/`: valid only for the current project.

## Where to put a skill when adding or updating it

- **Shared (`shared/`)**: independent of any unit or specific business: techniques, pitfalls met, test procedures, file conventions, sample layouts.
- **Project-only (`project/`)**: tied to one unit, person, system or regulation: names, job titles, internal bases, dates, codes, a specific workbook layout, company background.
- When unsure, keep it in the project; when the same lesson repeats in a second project, promote the common part to `shared/`.
- A project skill should point to the shared skill instead of copying its content (for example point to `excel-workbooks` or `office-documents`) and keep only the specific part. Avoid two copies of the same guidance.
- A skill tied to one case, one person or confidential data is not put in `shared/`; a lesson taken from a real project goes up only after the specific names, figures and titles are removed. A new domain becomes a pack only when it meets the conditions in `packs/README.md`.
- Before creating or editing a skill: read `.agent/SKILL_INDEX.md` and the related skill closely (including its references) to reuse rather than start over; borrow techniques only, not another unit's specific content.
- After each update state one line: whether the lesson is shared or project-specific and where it went. If unsure, record it in `.agent/PENDING_LESSONS.md`.

When a skill changes scope, update `.agent/SKILL_INDEX.md`. Do not move a skill on the agent's guess; if a move affects a structure the user is using, ask/confirm with the user.
