---
name: data-charts
description: >-
  Suggestions for choosing and building charts from tabular data as a single offline-openable HTML
  file (plain SVG): bars, lines, stacked bars, donuts, KPI cards, tables with bars. Includes a chart
  library template to take structure from. Use when asked to "draw a chart"; for multi-section
  reports also use html-reports.
  Triggers when the user says: "draw a chart", "visualise the figures", "bar/line/pie chart", "KPI card".
metadata:
  version: "1.0"
---

# Charts from data

Turns a table of figures into a chart that reads well, has the right numbers and opens without a
network. Not for web applications or deployed dashboard systems.

## Output scope

- The user supplies data and says "draw a chart" or "visualise": deliver **charts** (one to a few
  figures); do not expand them into a report on your own.
- The user says "report", "dashboard" or "overview": consider `html-reports` for the page frame and
  still take the chart construction from this skill.
- With only one or two numbers or a few data points, say it plainly with a number card or a table;
  do not force a chart.

## How to work

1. **Decide the message** each chart must show (comparison, trend, composition, detail). Choose the
   type with `references/chart-selection.md`.
2. **Check the data before drawing**: missing cells, units, period, totals. Excel data of unclear
   quality: consider `spreadsheet-check`. Never replace missing cells with 0.
3. **Build** from `assets/basic-charts.html`: open the file, take the matching drawing function,
   replace the `report-data` block and the title. Keep only the charts used; drop the rest of the template.
4. **Presentation:** a title that says what to see, units, period and source, direct labels, and a
   data table alongside for exact figures.

## Presentation rules

- Bars start at 0. No 3D, no shadows, no decoration that carries no data.
- At most about 5 colours; colour is never the only way to tell series apart (add labels or line styles).
- One figure, one message; to compare many groups, split the figures instead of cramming one chart.
- A chart shows a trend, it does not prove a cause; do not write causal conclusions.
- Keep the `isDemo` label until real data is in; set `isDemo` to `false` only when the figures, title,
  period and source all belong to the user.

## Technique

Plain SVG and inline JavaScript, system fonts, no CDN. Use an outside library only for complex
interaction (for example network charts, maps); then embed the library in the file or say plainly
that the file needs a network. Ordinary interaction (filter by period, show the number on hover) is
enough for most reports.

## When to say no

Too little data or not comparable; the user wants a chart to "prove" something the data does not
show; the request needs advanced graphic design or a specialised map. Give the reason and propose a
table or a simpler chart.

## When delivering

Numbers on the figure match the source table, Vietnamese text displays correctly, it prints, and
nothing needs a network. Open it in a browser if a tool is available; if not, say it was not viewed on
screen. When it passes, stop; do not add charts or effects.
