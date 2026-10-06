# SKILL INDEX

A catalog that suggests skills by task. It is not a priority order or a list to load.
You may use a native skill, a local skill, a combination, or handle the task directly.

| Skill ID | Origin | Scope | Location / Provider | Use when | Status | Provenance / Notes |
|---|---|---|---|---|---|---|
| office-documents | LOCAL | SHARED | skills/local/shared/office-documents/SKILL.md | Drafting or editing business documents that have a source or template; the SOP, form and internal update examples help. | AVAILABLE | Newly written; no dependencies of its own. |
| html-reports | LOCAL | SHARED | skills/local/shared/html-reports/SKILL.md | An HTML report or indicator overview page is needed; the one-file offline templates help. | AVAILABLE | Newly written; two self-contained HTML templates with illustrative data. |
| vietnamese-editing | LOCAL | SHARED | skills/local/shared/vietnamese-editing/SKILL.md | A request to edit Vietnamese text, reduce boilerplate, or follow a specific voice. | AVAILABLE | Optional; not applied automatically as a post-processing step. Has references/machine-style-signs.md (rewritten from the idea of the humanizer skill). |
| internal-comms | LOCAL | SHARED | skills/local/shared/internal-comms/SKILL.md | Writing progress reports (3P), announcements, newsletters, FAQs and incident reports that people in the unit can read quickly. | AVAILABLE | Rewritten from the idea of the internal-comms skill (reference repo, see docs/en/SOURCES_AND_REFERENCES.md); no dependencies. |
| doc-coauthoring | LOCAL | SHARED | skills/local/shared/doc-coauthoring/SKILL.md | A large document where the user wants to work through it step by step (gather context, outline, draft each section, final check). Ask before using. | AVAILABLE | Rewritten from the idea of the doc-coauthoring skill; limited rounds, no sub-agents; no dependencies. |
| data-charts | LOCAL | SHARED | skills/local/shared/data-charts/SKILL.md | Drawing charts from a data table into offline HTML (SVG); choosing a chart type or taking a chart template. | AVAILABLE | Rewritten from the idea of the lieflat-charts skill; SVG templates newly written, no code or templates from the original repo; no dependencies. |
| document-comparison | LOCAL | SHARED | skills/local/shared/document-comparison/SKILL.md | Comparing two versions of a regulation, process, form or contract; a table of meaningful changes is needed. | AVAILABLE | Newly written; no dependencies of its own. |
| spreadsheet-check | LOCAL | SHARED | skills/local/shared/spreadsheet-check/SKILL.md | A quick check of Excel/CSV before taking figures for a report or dashboard; reports findings only, does not edit the original. | AVAILABLE | Newly written; includes scripts/check_spreadsheet.py (CSV: standard library; Excel: needs openpyxl, optional; use `--lang en` for English output). |
| meeting-minutes | LOCAL | SHARED | skills/local/shared/meeting-minutes/SKILL.md | Writing minutes or a summary of a meeting from notes/a transcript; separating decisions, action items and open issues. | AVAILABLE | Newly written; no dependencies. |
| process-mapping | LOCAL | SHARED | skills/local/shared/process-mapping/SKILL.md | Describing a process with a step table, RACI and a flow diagram when needed. | AVAILABLE | Newly written; Mermaid/SVG depending on where it is used, no install dependencies. |
| vn-admin-documents | LOCAL | SHARED | skills/local/shared/vn-admin-documents/SKILL.md | Drafting Vietnamese administrative documents in the proper format (official letter, submission, report, notice): number/symbol, place, subject line, recipients, layout. | AVAILABLE | Newly written; the reference basis is the rules on clerical work, always check the current version or the unit's regulations; no dependencies. |

## How to read the catalog

`Use when` suggests the suitable scope; the agent still weighs the request and the tools it actually has.
When you know which skill to use, you can open it directly. Read only the supporting resources that are relevant.
`ACTIVE` means commonly used in the project, not automatically loaded in every session.

Origin: `LOCAL` (self-written), `EXTERNAL` (imported), `PROVIDER` (native).
Scope: `SHARED` (common), `PROJECT` (project-specific), `GLOBAL` (per provider), `PACK` (domain pack installed with `tools/pack.py`).
Status: `AVAILABLE` (ready to use), `ACTIVE` (commonly used), `REVIEW` (under review),
`DISABLED` (the user chose not to use it).

## When the library changes

Record the purpose, location, origin and notable dependencies when adding or substantially editing a skill.
Do not re-evaluate or re-register the same skill each time it is used. The user decides on adding,
removing or editing skills; an operational choice among the skills already present does not need a
separate approval round. Do not move or delete the user's skills on your own.

You may add native capabilities confirmed useful in a specific session/provider. Do not fill in assumed
skill names; a native entry does not guarantee that another provider has the same capability.
References and audit results for the new skills: `docs/en/SOURCES_AND_REFERENCES.md` (from the project root).
