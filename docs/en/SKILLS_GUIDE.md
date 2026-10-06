# Choosing and using skills

Skills in the package are extra guidance and resources. The agent chooses by fit with the work,
not in a native → local or local → native order.

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

These are examples of choices, not a mandatory routing table. The agent can combine skills when
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

The agent can replace the `report-data` block in the template and then adjust layout and
commentary. You do not need to edit code to use the skill: handing over the data and the request
is enough. The filter buttons only change how the data in the file is viewed; the templates are
not connected to live data.

Both templates support printing through the “In báo cáo” (Print report) button. Opening offline
does not mean the agent's process of reading data and building the report is also fully offline.

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

These seven skills are short, and each has a “when to stop” part so the agent does not go beyond scope.

| Skill | Use when | Typical output |
|---|---|---|
| `document-comparison` | There are two versions of a document. | A change table: section, old, new, type, impact (if there is a basis). |
| `spreadsheet-check` | You are about to take figures from Excel/CSV for a report. | A list of findings by impact level; the original file is not edited. |
| `meeting-minutes` | You have meeting notes or a record. | Decisions, action items (who/when if known), open points. |
| `process-mapping` | You need to describe or review a process. | A step table, RACI if needed, a Mermaid/SVG diagram if needed. |
| `internal-comms` | You need to write something people in the organisation read quickly. | A progress update (Progress - Plans - Problems), announcement, newsletter, FAQ, incident report. |
| `doc-coauthoring` | A large document where you want to work through it step by step. | An approved outline, sections drafted one at a time, one final review. |
| `vn-admin-documents` | You need a correctly formatted administrative document. | A draft with all format components; numbers, dates and signatory left as `[needs confirmation]`. |

```text
Compare Old_Regulation.docx with New_Regulation.docx. Only build a table of meaningful changes,
prioritising figures, deadlines and roles. Where the impact is unclear, write "needs confirmation".
```

`spreadsheet-check` ships a script `scripts/check_spreadsheet.py` (read-only; CSV needs nothing installed,
Excel needs `openpyxl`; add `--lang en` for English output). `vn-admin-documents` is only a starting point for format: records-management rules may
have changed and an organisation may have its own, so check the current version before issuing.

`doc-coauthoring` is only used when you want it; the agent will ask first, and if you decline it
simply drafts directly. The other skills do not need permission before use.

## 7. How the agent finds skills

`.agent/SKILL_INDEX.md` describes when each skill is useful and gives its path. The agent can
look there to discover skills, or open one directly when it already knows which fits.

`AVAILABLE` means ready to use, `ACTIVE` means commonly used in the project. Neither requires
loading at the start of a session. Native notes only describe the known capabilities of one
environment; when you switch agents, use what is really available in the new session.

The package does not install the skills into the application's native menu. When needed, point to the path:

```text
The project's extra skills are described in .agent/SKILL_INDEX.md.
Only consult skills that help with this task; native skills or working directly are fine too.
```

## 8. Add other skills when needed

Put skills you write yourself in `skills/local/shared/` or `skills/local/project/`. Skills imported
from outside can go in `skills/external/`; `skills/inbox/` is only a temporary place if you want to
classify later.

When adding or heavily changing one, ask the agent to read enough to record `Use when`, location,
origin and notable dependencies in the index. There is no need to re-evaluate a familiar skill
when using it. The user keeps the right to add, remove or edit the library; the agent chooses
actively within the work.

## 9. Scope of the reference repo

The skills in the package were newly written from the needs discussed. The repo
`sharkrebel/everything-everywhere-for-antigravity` was used for ideas (including the four skills
chosen through an audit); the package rewrites them as short Vietnamese versions, and does not
install or import the originals. No global rules, hooks, installers or proprietary format skills
are repackaged.

The source record, audit results and reasons are in `SOURCES_AND_REFERENCES.md` in this folder.
