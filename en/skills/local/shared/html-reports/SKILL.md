---
name: html-reports
description: >-
  Suggestions for creating or updating Vietnamese HTML reports, periodic reports and KPI overview
  pages from supplied data. Two single-file offline templates are included as references when they
  fit; not for building web apps, backends or deployed dashboard systems.
  Triggers when the user says: "HTML report", "dashboard", "metrics overview page", "periodic report as a web page".
metadata:
  version: "1.0"
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

## When delivering

Look at what directly affects use: figures/rates match the source, requested filters work, Vietnamese
is readable, the file opens in the intended environment. Use a browser check only when a suitable
tool exists; say what was not checked and do not claim otherwise. When the output meets the request,
stop rather than adding features or further polishing.
