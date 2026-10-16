# Choosing and using skills

Whichever assistant you choose uses its own capabilities and native skills; the package neither replaces
nor edits them. Skills in the package are **extra** guidance and resources: templates, sources and
business rules that native skills lack. The assistant chooses by fit with the work and is not pushed to use
a package skill when the existing way is enough.

## 1. When is a skill useful?

A skill is worth using when it has a template, experience or method that helps finish the task
more clearly, faster or with less rework. There is no need to call a skill just because the
task contains a word similar to its name.

| Task | A choice that may fit |
|---|---|
| Fix one sentence in an announcement | Do it directly. |
| Draft a procedure from a regulation and an internal template | Use the project's sources/templates; consult `office-documents` when helpful. |
| Draft a long proposal or report that needs deep discussion | Consider `doc-coauthoring`; ask before using it. |
| Create Word/PDF from approved content | Use a suitable formatting tool or native skill; no need to rewrite the content. |
| Draw a chart from a table of figures | Consider `data-charts`; check the table with `spreadsheet-check` if the data is not clean. |
| Make an HTML report from data | Consider `html-reports`, a native skill or an existing report. |
| Polish the wording of a report | Consider `vietnamese-editing`; do not edit the whole document by default. |
| Compare a new regulation with the old version | Consider `document-comparison`. |
| Write minutes from meeting notes | Consider `meeting-minutes`. |
| Describe a process, roles, a diagram | Consider `process-mapping`, combined with `office-documents` when writing it up as a document. |
| Weekly update, announcement, newsletter, FAQ, incident report | Consider `internal-comms`. |
| Official letter, submission or report to another body or for signature | Consider `vn-admin-documents`; use the organisation's own records-management rules first if it has them. |
| Build a tracking workbook, data-entry form or calculation appendix in Excel | Consider `excel-workbooks`; check an existing file with `spreadsheet-check`. |
| An offline dashboard that reads the user's Excel files | Consider `excel-html-viewer`; charts follow `data-charts`. |

These are examples of choices, not a mandatory routing table. The assistant can combine skills when
they complement each other, or work directly if it is already capable.

## 2. The business documents skill

`skills/local/shared/office-documents/SKILL.md` offers suggestions and three short frames:
SOP/procedure, form, internal update. Pick the part that fits; you do not need to fill in all of it.

```text
From this regulation, create a request-recording form. Use the internal template if it fits;
you may consult office-documents. Do not add information to collect beyond what is needed.
```

The bundled frames contain no real regulations of your organisation. Facts and business terms
still come from sources or confirmed decisions, not from the examples in the skill.

## 3. The HTML reports skill

`skills/local/shared/html-reports/SKILL.md` comes with two files you can open and try:

| Template | Location inside the skill | Suggested use |
|---|---|---|
| Periodic report | `assets/periodic-report.html` | A monthly/weekly report with commentary, KPIs, trend and a data table. |
| Metrics overview | `assets/metrics-overview.html` | A KPI page with a filter by period/channel and a detail table. |

Both templates are self-contained HTML, newly written for the package, using system fonts and
needing no network. The data in the templates is **illustrative**, not project data.

```text
Use this table of figures to create an offline HTML report in output/.
Choose the template or presentation that fits best. Keep the figures exact and state the source and reporting period.
```

The assistant can replace the `report-data` block in the template and then adjust layout and
commentary. You do not need to edit code to use the skill: handing over the data and the request
is enough. The filter buttons only change how the data in the file is viewed; the templates are
not connected to live data.

Both templates support printing through the “In báo cáo” (Print report) button. Opening offline
does not mean the assistant's process of reading data and building the report is also fully offline.

## 4. The charts skill

`skills/local/shared/data-charts/SKILL.md` is for “draw a chart” requests from a table of
figures. It comes with `assets/basic-charts.html` (KPI cards, line chart, horizontal bars,
stacked columns, donut, a table with small bars) and `references/chart-selection.md` for choosing
the chart type from the data. Charts are plain SVG, open offline, and each one has a collapsible
data table next to it.

```text
Draw charts from this table of figures and save them as one offline HTML file in output/.
Choose the chart type that fits each message; state the unit, period and source clearly.
```

Unlike `html-reports` (a report page frame with commentary), `data-charts` focuses on the charts
themselves. The two skills work together when you need a report that contains charts.

## 5. The Vietnamese editing skill

`skills/local/shared/vietnamese-editing/SKILL.md` is useful when there is a clear request about
wording. It aims to keep meaning, figures, terms and level of certainty, and not to “de-AI” text
by swapping punctuation or stripping out business content. When you need to spot formulaic
writing, the skill has `references/machine-style-signs.md`. Both files are written for
Vietnamese text.

```text
Edit this summary to be clearer and less stock-phrase. Keep the figures and the level of
certainty of the statements; return only the edited version.
```

There is no need to run this skill after every report or SOP.

## 6. Skills for everyday work

These nine skills are short, and each has a “when to stop” part so the assistant does not go beyond scope.

| Skill | Use when | Typical output |
|---|---|---|
| `document-comparison` | There are two versions of a document. | A change table: section, old, new, type, impact (if there is a basis). |
| `spreadsheet-check` | You are about to take figures from Excel/CSV for a report. | A list of findings by impact level; the original file is not edited. |
| `meeting-minutes` | You have meeting notes or a record. | Decisions, action items (who/when if known), open points. |
| `process-mapping` | You need to describe or review a process. | A step table, RACI if needed, a Mermaid/SVG diagram if needed. |
| `internal-comms` | You need to write something people in the organisation read quickly. | A progress update (Progress - Plans - Problems), announcement, newsletter, FAQ, incident report. |
| `doc-coauthoring` | A large document where you want to work through it step by step. | An approved outline, sections drafted one at a time, one final review. |
| `vn-admin-documents` | You need a correctly formatted administrative document. | A draft with all format components; numbers, dates and signatory left as `[needs confirmation]`. |
| `excel-workbooks` | You need a tracking workbook, data-entry form or calculation appendix in Excel. | An Excel file with an input sheet, a formula-only report sheet and separate sample data; recalculated with no errors. |
| `excel-html-viewer` | You want to see figures from Excel files visually without installing software. | One HTML file that opens offline, reads Excel and has a data-check tab; limits stated on delivery. |
| `source-library` | Store and look up the project's legal documents, company rules and templates; know what is in force and how well it is verified. | A `references/` layout by group and domain, an `_INDEX.xlsx` index, the `tools/library.py` command (init, check, find); quotes only from files in the library. |

```text
Compare Old_Regulation.docx with New_Regulation.docx. Only build a table of meaningful changes,
prioritising figures, deadlines and roles. Where the impact is unclear, write "needs confirmation".
```

`spreadsheet-check` ships a script `scripts/check_spreadsheet.py` (read-only; CSV needs nothing installed,
Excel needs `openpyxl`; add `--lang en` for English output). `vn-admin-documents` is only a starting point for format: records-management rules may
have changed and an organisation may have its own, so check the current version before issuing.

`doc-coauthoring` is only used when you want it; the assistant will ask first, and if you decline it
simply drafts directly. The other skills do not need permission before use.

## 7. How the assistant finds skills

`.agent/SKILL_INDEX.md` describes when each skill is useful and gives its path. The assistant can
look there to discover skills, or open one directly when it already knows which fits.

`AVAILABLE` means accepted and ready to use, `ACTIVE` means commonly used in the project. Neither
requires loading at the start of a session. `REVIEW` means **trial**: not through intake yet; the assistant
only tries it in the project and says it is a trial, and the tools do not copy it into apps. Native notes
only describe the known capabilities of one environment; when you switch assistants, use what is really
available in the new session.

The package does not install the skills into the application's native menu. When needed, point to the path:

```text
The project's extra skills are described in .agent/SKILL_INDEX.md.
Only consult skills that help with this task; native skills or working directly are fine too.
```

## 8. Add other skills when needed

Put skills you write yourself in `skills/local/shared/` or `skills/local/project/`. Skills imported
from outside can go in `skills/external/`; `skills/inbox/` is only a temporary place if you want to
classify later.

Putting a file in a folder does not mean the skill is accepted. Skills learned while working and
skills or packs downloaded from outside share one intake standard (`skills/README.md`, section "Intake
of skills and packs"): it must add something native or the current way cannot do, with a clear origin,
clear permissions and evidence that it works. If your assistant already does the job well, no duplicate
skill is needed; concluding "not needed" is also a good result. While it is being assessed, the skill is
recorded as `REVIEW` and can still be tried in the project.

When adding or heavily changing one, ask the assistant to read enough to record `Use when`, location,
origin and notable dependencies in the index. There is no need to re-evaluate an accepted skill
when using it. The user keeps the right to add, remove or edit the library and to put skills into the
template root; the assistant chooses actively within the work. Updating the template root does not change
projects created earlier.

## 9. Domain packs and installing skills into an app

The package core only holds the working rules and the fourteen shared skills. Knowledge specific to a domain (port and logistics,
HR, finance...) belongs in a **domain pack** in `packs/`, installed into the projects that need it with
`python tools/pack.py add <name>` (see `python tools/pack.py list`). A pack installs into `skills/local/packs/` and is recorded in
`.agent/SKILL_INDEX.md` with Scope `PACK`; remove it with `pack.py remove <name>` (the folder is moved into `archive/`, not deleted).
The rule for accepting a pack and how to write a new one are in `packs/README.md`. Every installed pack is recorded `REVIEW` (trial; not copied into apps); the `intake` block inside a pack is only its own claim. After reading the record,
if you accept it for this project, install with `python tools/pack.py add <name> --confirm` (already installed: `pack.py confirm <name>`; in the control panel it is the "Install and accept" / "Confirm intake" button, one dialog and done); changing the pack content afterwards requires confirming again. The package ships five domain packs (trial,
version 0.2.0): `phap-ly` (researching and applying legal documents), `van-thu-luu-tru` (outgoing and incoming documents, copies,
filing, archiving), `cang-logistics` (ship, barge and equipment-incident reports), `hanh-chinh-nhan-su` (personnel decisions,
leave, overtime, discipline, pay, insurance) and `ke-toan-noi-bo` (advances, payments, vouchers, invoices, retention). Each pack
has a legal-basis table (the legal-basis.md file in the skill’s references folder) with numbers, articles, effective dates, sources and a check date so users can verify them.
Install with `python tools/pack.py add <name>` or on the control panel: "Manage and maintain" group → "Manage skills". There is also the `_template`
skeleton for writing new packs.

Each project keeps its own copy of the skills, so a project is always self-contained and portable; `tools/upgrade_package.py` keeps
these copies in sync with a new package when you upgrade. If you want a skill to show up in an app's menu (for example Claude), use
`python tools/install_skills.py --dest <the app's skills folder> --skills <name,name> --yes` (without `--yes` it only previews), or the
"Install skills into apps" page of the control panel (`APP.bat`), where you tick the skills to copy. Copy only the skills you really need:
if the app already has a similar capability there is no need. Only accepted skills can be copied; a same-name skill the app already has
(native or from another source) is always kept, and an older package copy being replaced is saved into `archive/`. The skills use the
common `SKILL.md` format: Claude reads `~/.claude/skills`; Codex and Gemini CLI both read `~/.agents/skills`, so one copy serves both.
This is optional; the assistant can still read the skills as files.

Vietnamese–English glossary for administrative documents: `docs/GLOSSARY_VI_EN.md`. Before handing over a deliverable you can use
`python tools/check_output.py <file>` and the checklist `skills/local/shared/office-documents/references/delivery-checklist.md`.

## 10. Scope of the reference repo

The skills in the package were newly written from the needs discussed. The repo
`sharkrebel/everything-everywhere-for-antigravity` was used for ideas (including the four skills
chosen through an audit); the package rewrites them as short Vietnamese versions, and does not
install or import the originals. No global rules, hooks, installers or proprietary format skills
are repackaged.

The source record, audit results and reasons are in `SOURCES_AND_REFERENCES.md` in this folder.
