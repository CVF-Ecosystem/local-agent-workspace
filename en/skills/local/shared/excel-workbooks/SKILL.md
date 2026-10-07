---
name: excel-workbooks
description: >-
  Suggestions for building tracking workbooks, data-entry forms, self-summarising reports and calculation
  appendices in Excel (openpyxl, real formulas): an input → report layout, dropdowns, status colours, parameter
  cells, separate sample data, checks before delivery. Not for checking existing data (see `spreadsheet-check`)
  or drawing HTML charts (see `data-charts`).
  Triggers when the user says: "tracking workbook", "Excel data-entry form", "self-summarising report", "Excel appendix", "dashboard inside Excel".
metadata:
  version: "1.0"
---

# Building workbooks and reports in Excel

Use when you need a LIVE Excel file (people keep entering data, the report updates itself) or a calculation appendix that
accompanies a proposal. A form filled once and printed belongs to `office-documents`. Technical detail, limits and known
pitfalls: `references/openpyxl-notes.md` (open it when actually building).

## Layout: input → report

- **One log sheet is the only source of figures.** One row per case; add new rows rather than editing history;
  give it its own code/key column; freeze the header row and turn on the filter.
- **The report sheet holds formulas only** (`COUNTIFS`, `SUMIFS` pointing back to the log) and one or two period-selector cells; it never
  contains typed numbers. Set the default period to match the sample data so the sheet does not show all zeros and look broken.
- **A lookup sheet** holds the pick lists and mapping tables; **a guide sheet** comes first.
- An overview sheet only links to the detail sheets; it does not recompute figures that exist elsewhere.
- Add a new calculation block at the END of a sheet, never in the middle: formulas on other sheets that point at fixed addresses shift
  silently, and a formula check will not catch it.
- When updating a later version, keep sheet names, column names and header rows; other tools (such as `excel-html-viewer`) may read by these names.

## Easy to enter, hard to get wrong

Dropdowns cover the empty area below the sample data; colour statuses by value; add a "Check" column (OK/error) for the constraints people
often break (duplicate code, missing date, overlapping time ranges). Sheet protection without a password: lock formula cells, leave input
cells open, still allow filter and sort; do not lock the workbook structure if the process needs to copy sheets.

## Parameters, thresholds and sample data

- Put parameter and threshold cells at fixed, labelled positions. **A blank threshold cell means "not defined yet"**: the formulas
  still run and raise no flag.
- Figures not available stay blank or show "………"; do not fill them in. Any threshold or norm the agent proposes is labelled
  "proposal, to be decided by the person with authority".
- Illustrative numbers live only in a separate "SAMPLE DATA" sheet with its own fill colour and a stated assumption; the real data sheets stay empty.
- Colour convention (consistent across the whole file): input cells light yellow, statuses red/yellow/light green, sample data light blue;
  in a calculation model, blue text is input, black is formula, green is a link to another sheet.

## Calculation appendix for a proposal

Every result cell is a real formula, even when the inputs are assumptions; write "assumption, to be confirmed" in the cell (or add "(assumption)" to the
sheet name). Figures in Word and Excel must match; when one side changes, re-check the other. For multi-stage capacity problems (A → B → C), calculate
forwards from the actual output or demand, and ask the user for real operating figures instead of picking tidy parameters and fitting backwards; when one
parameter changes, recompute the whole chain, not just one sheet. Suggested structure (drop or change per proposal): overview; investment cost by item;
technical configuration linking quantities from the cost sheet; capacity analysis; operating cost; break-even; a roadmap with a formula-driven Gantt grid.
Separate new investment from assets already owned; a shortened label that can be read as "already available" is written out in full.

## Before delivery

Recalculate and confirm there are no errors (`#NAME?`, `#REF!`...), render to an image or PDF and look at the widest table, test with a full load.
State what was not tried (for example, not opened in real Excel).
Test with the data itself: copy a few sample rows into the input sheet, then (1) change the period cell to another month: the report must follow the period, not add up every month;
(2) leave the threshold/norm cell blank: the report still runs and raises no flag; (3) add a row with a new code: the report must catch it. Parameter cells stay blank by default; do not
preset a "nice" number (90, 100...). Lists of vehicles or items in the report sheet come from the lookup sheet by formula, not typed by hand. Sample data must be meaningful text. Detail: `references/openpyxl-notes.md`.
