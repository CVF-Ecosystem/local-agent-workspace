---
name: excel-html-viewer
description: >-
  Suggestions for building a single-file, offline HTML tool that reads the user's Excel files to show figures visually
  (metric cards, filters, charts, a list of items needing attention, a data-check tab). Tolerates non-standard sheet names, column
  names and hand-typed values. Not for reports from fixed data (see `html-reports`) or for checking a file (see `spreadsheet-check`).
  Triggers when the user says: "dashboard that reads an Excel file", "see Excel figures visually", "offline HTML tool", "control board that reads Excel".
metadata:
  version: "1.0"
---

# HTML tool that reads Excel files

Use when the user wants to see figures from Excel files without installing software and without sending data to an outside service.
The agreed architecture: **Excel is the input layer, HTML is the viewing layer**; the data stays in the user's browser. For building the
input workbook see `excel-workbooks`; for charts see `data-charts`; for a report from data you already have see `html-reports`.

## How to build

- One HTML file, CSS and JavaScript embedded, no CDN. **Forbidden**: `<script src="http...">`, `<link href="http...">`, `fetch`, `XMLHttpRequest` and any network resource: the user opens the file without internet. Do not deliver a "CDN" version next to an "offline" one; deliver only the offline one. Self-check before handing over: `grep -E 'src="https?:|href="https?:|fetch\(' file.html` must return nothing (`http://` strings that are XML namespaces inside the library do not count). Reading `.xlsx` needs an Excel-reading library (for example the mini build of SheetJS)
  embedded in the file; when embedding, replace the string `</script` inside the library with `<\/script`. Embed it as a plain `<script>` block (no base64 needed). Reading CSV only needs no library.
- No library and no network to fetch one: embed `assets/xlsx-mini-reader.js` (reads `.xlsx` with no external library; needs a browser with `DecompressionStream`,
  tried on many real Excel files). Values only: dates are serial numbers to convert yourself, formulas without a calculated value come back empty. The .xlsx export button still needs a writing library.
- If the request is to read `.xlsx`, the tool MUST read `.xlsx`. Do not let the file picker accept `.xlsx` while the code says "not supported"; if you cannot, say plainly it is not met rather than calling it done.
- Write the source as separate files and use a build script to merge the library and sample data; do not hand-edit a large file.
  Keep the build source next to the product (or tell the user to back it up), because a temporary working folder can be lost.
- Do not trust formula values stored in the file (a file created with openpyxl has no cached values): recompute from the raw data and
  skip formula cells that have no value. The tool is read-only and never writes back to the file.

## Tolerate non-standard data and names

People rename sheets, mix upper and lower case, use accents or not, leave extra spaces. So:

1. Every text comparison (sheet name, column header, cell value, code) goes through ONE normalising function: lower-case, strip accents (NFD),
   map đ to d, unify dash types, collapse whitespace including NBSP, trim both ends.
2. Do not pick sheets by a fixed name: scan every sheet and score it by how many header columns match; a sheet takes whichever role it fits
   and extra sheets are ignored. After loading, show "Sheets recognised: role → sheet name" so the user can check.
3. Read columns by header name: exact match first, then prefix match; detect the header row within the first ~12 rows. Column names are the only
   fixed condition, so ask users to keep them.
4. Normalise hand-typed values too before comparing or looking up: codes ("gw 01" and "gw-01" both become "GW01"), types and statuses, Yes/No flags,
   link codes between two sheets. A value that is still unknown after normalising raises a warning and is never skipped silently.
5. Dates and numbers are read in many forms (Excel serial, `dd/mm/yyyy`, ISO, "1.234,5", "hh:mm"). Record the Excel row number on each record so an error points
   at the exact row to fix.
6. **Serial dates**: real Excel date cells arrive as numbers (for example `46296`). Convert `serial → date` (epoch 1899-12-30; treat as a date only inside a sane range such as 1990–2100 and in a date column) and show `dd/mm/yyyy`; never show the bare number. Date checks must run for serials and strings alike: a string without `/` or `-` must still be tried.
7. **Negative numbers and absurd values**: quantity, volume, money and hours columns must not be negative (unless the workbook says otherwise); report a negative as a row error with its row number, not only text in a numeric cell. Also report text in numeric cells, blanks in required columns, duplicate voucher codes.
8. **Several sheets**: scan every sheet and detect the header row per sheet (not only the first sheet, do not assume the first sheet is the main table); read several tables at once (for example a fuel log and a vehicle list) and show "Sheets recognised: role → sheet name". Guide sheets, formula-only sheets and sample/mock sheets are not counted in the figures. KPI figures come from the tables actually read: never leave a metric card at 0 because the code does not read that kind of data. If the real file's column heading differs from the planned phrase (for example "Quantity issued (litres)" instead of "Litres"), accept both; after building, try the user's real workbook and report the rows read per sheet: 0 rows means it is not finished.

## Missing data, errors, thresholds

- Three-level warnings, shown in the check tab and the "Needs attention" block: whole file (no table found, saying which columns are needed); each table (which columns
  are missing, with the consequence); each row (with its row number). Row-level warnings alone do not let the user guess the root cause.
- Thresholds come from parameter cells in the workbook and can be tried on the filter bar (never written back). A blank cell means "not defined yet": show a notice and raise no
  flag; a proposed threshold is labelled "awaiting approval".
- Avoid hangs: never loop over an unbounded date range when the file is empty or no period is chosen.
- Embedded sample data (if random, use a fixed seed and plant a few deliberate errors to illustrate the checks), a "Sample data / File: name" badge that is always visible, and a button
  that exports a sample Excel file in the right layout so the enter-then-view loop can be tried.

## Interface

Clickable metric cards and a "Needs attention" block at the top; clicking a number or column opens a detail table with filter, sort and CSV export (add a BOM so Excel reads Vietnamese correctly);
switch between chart and number table; light and dark themes; print or save as PDF; usable on a narrow screen. Charts follow `data-charts`: status colours always come with an icon
and text, one axis, a legend and a number table.

## Testing and limits when delivering

Test list: `references/test-checklist.md`. When delivering, say clearly: the tool is view-only, does not edit files, does not update itself (reopen each time),
and keeps no history; the figures only mean something once the entered data has been inventoried and normalised; and what was not tried (which browser, real Excel).
