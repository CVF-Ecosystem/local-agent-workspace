---
name: html-reports
description: >-
  Suggestions for creating or updating Vietnamese HTML reports, periodic reports and KPI overview
  pages from supplied data. Two single-file offline templates are included as references when they
  fit; not for building web apps, backends or deployed dashboard systems.
  Triggers when the user says: "HTML report", "dashboard", "metrics overview page", "periodic report as a web page".
metadata:
  version: "1.2"
---

# Lightweight HTML reports

Choose the approach by purpose, data and reading environment. You can use a native skill, tools at
hand or the templates below; there is no mandatory order of preference.

## Choosing the output

If asked for one metric or one chart, do not expand it into a full report. When updating an old
report, keep the layout that still fits and change the part you were given. For a new report, focus on
the indicators and comments that help the reader understand or decide.

A self-contained HTML file is usually convenient to open locally and share. No framework, server,
build pipeline or outside library is needed just because the output is HTML. Other tools are fine
when they really suit the request; not every report needs the same template.

## Two reference templates

- `assets/periodic-report.html`: comments, KPIs, development over periods and a source table.
- `assets/metrics-overview.html`: an overview with channel/period filters, KPIs and a detail table.

Both templates were newly written for this workspace and are not copies of Lieflat Charts templates.
They use inline CSS/JavaScript, system fonts and no network dependencies. The content and sample data
are labelled as illustrative; they are not the user's real figures. Open the fitting template, copy it
to the output and adapt it; there is no need to read or compare both.

Need to choose a chart type or build your own SVG chart: use `data-charts` (it has a template and a
guide to choosing charts). Figures taken from an unchecked spreadsheet: consider `spreadsheet-check` first.

## When using a template

The data sits in `<script id="report-data" type="application/json">`. You may edit this block and the
layout as requested. Each template documents the meaning of its fields inside the file. Keep the JSON
valid; if a string contains `</script>`, encode the `<` as `\u003c` when embedding.

Replace the figures, title, reporting period, source and the sample comments together. Switch `isDemo`
to `false` only when the output uses real data supplied by the user; do not remove the illustrative
label merely to make a template look finished.

For case-processing data, `onTime` is the number within `closed` finished on time. An overall rate is
total numerator / total denominator; a missing cell is not replaced with 0 on a guess. Closing
balances are not added across weeks. Change the calculation when the real business definition is
different; a chart is a means of presentation and does not itself supply a causal conclusion.

## Presentation standard (default for new reports and dashboards)

Goal: look like a report for management, not a technical tool. Both templates in `assets/` follow this standard
(the CSS block "Chuẩn trình bày báo cáo"); copy that block when building a new page.

- **Title band**: navy gradient (`--band1` → `--band2`), white text: a small letter-spaced uppercase line with the unit name
  or period, a 26px bold title, one description or "Reporting period: …" line updated automatically with a data-source badge; Print button on the right.
- **Filter bar / first card**: white card, 12px radius, light shadow, overlapping the title band; the filter bar sticks to the top
  while scrolling (wide screens only).
- **Roman-numbered sections** (I, II, III…): a navy rounded number badge next to a 16px heading. Suggested order: overview →
  trend → summary table → analysis → detail → data check (always last).
- **Metric cards**: 4px coloured stripe on the left (one category colour per card), 11px uppercase label, 30px figure with
  `tabular-nums`, sub-line under a dashed rule.
- **"⚠ Needs attention" block**: amber left border; each item is one sentence with a number, ideally linking to the detail section.
- **Tables**: 11px uppercase header on a light background, zebra rows, right-aligned numbers, light total row. Status as rounded
  pills with symbol and text (▲ red, ● green); never colour alone.
- **Colours**: tokens on `:root` plus a dark-mode set. Chart categories `#2a78d6 #eb6834 #1baf7a #eda100 #a8a7a1`;
  status red `#d03b3b`/`#fdecec`, green `#0e8f4f`/`#e6f6ee`, amber `#b97a00`/`#fff5df`.
- **Fonts**: system fonts only (`"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`). Do not load web fonts
  (Google Fonts…): the page must open offline and make no outside request when opened.
- **Print** A4 landscape (`@page{size:A4 landscape;margin:10mm}`): white background, navy title with an underline, buttons and
  filters hidden, colours kept (`print-color-adjust:exact`), cards not split but long tables allowed to break (`tr{break-inside:avoid}`,
  `thead{display:table-header-group}`), a signature block shown only in print ("Prepared by" / approver title, "(Signature, full name)").
- **Narrow screens** (≤860px): 2-column cards, 1-column grid, non-sticky filters, no horizontal scroll.
- **Restraint**: no repeated information (with a period and a source badge, do not add a line listing file names; for many files
  show only the count); messages only when action is needed; an empty cell with business meaning gets clear words ("On time") instead of "–".

### Adapting to an organisation

Change only: the unit name in the small line, the main colour (`--band1`, `--band2`, `--navy`), the print font if the organisation
requires one (for example Times New Roman), the table-header colour if it should match the organisation's Excel books, and the titles
in the signature block. Organisation-specific details (names, signatories) stay in the project's own skill, not here.

When the organisation has no colours of its own, do not ask an open "which colour do you like". Ask about the context (formal,
for management; modern internal; technical; projected on screen), then offer 2 - 3 options with one line each: navy (default,
formal), bright blue (internal, modern), neutral grey (technical, legal), burgundy (analysis, review). When the user gives colour
codes or a logo, use exactly those colours and check text-on-background contrast in both light and dark mode.

### Restyling an existing tool

Add one overriding CSS block after the old CSS and change only the header and footer; keep the calculating JavaScript and element
`id`s. Save as a new file ("… (v2).html"); do not overwrite the version in use. Note: the `border` shorthand resets `border-image`, so an
older higher-specificity rule with `border:none` removes a band painted with `border-image`. Check every tab, dark mode, a 390px screen and the PDF.

## When delivering

Look at what directly affects use: figures/rates match the source, requested filters work, Vietnamese
is readable, the file opens in the intended environment. Use a browser check only when a suitable
tool exists; say what was not checked and do not claim otherwise. When the output meets the request,
stop rather than adding features or further polishing.
