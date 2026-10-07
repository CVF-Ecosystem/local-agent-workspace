# Testing an HTML tool that reads Excel

Run with an automated browser (for example Playwright with Chromium) when available; if not, say clearly that it was not run automatically.

0. Try a REAL `.xlsx` from the user (and one with reordered columns), not only CSV or the embedded sample data; if the file cannot be read the tool is not finished.
0b. Network scan: `grep -E 'src="https?:|href="https?:|fetch\(|XMLHttpRequest' file.html` must return nothing; if DevTools are available, the Network tab shows no outside request when the file opens.
0c. Data errors must be caught: real date cells (serial) show as `dd/mm/yyyy`; negative numbers in quantity columns; text in numeric cells; out-of-range dates; each error shows the right Excel row number.
0d. Several sheets: try a workbook with several sheets (guide, mock, main table, lookup); report the rows read per sheet; metric cards are not 0 when a sheet has data.
1. No JavaScript errors on any tab; take a screenshot of each tab, including dark mode and a narrow screen, and look at the images.
2. Figures match the source Excel. Export the sample Excel file and load it back: the metrics must be identical to those with the sample data.
3. Edited files: reorder columns; dates as text; numbers as Vietnamese-style text; blank threshold; inserted blank rows.
4. Rename sheets (no accents, mixed case, extra spaces, unrelated odd names, an extra sheet) and messy hand-typed values (code " gw 01", type " HU ", lower-case codes, decomposed
   Unicode): the result must be identical to the clean file. Compare the full string of the metric cards AND the "Needs attention" block, the grouping and the charts;
   comparing only metric totals will not show a mis-recognised lookup sheet that drops everything into "Ungrouped".
5. Load-time warnings: missing lookup, missing columns, missing main table, empty file, wrong file format: each must show the right message and never hang.
6. Metric cards, filter, sort, CSV export; changing a warning threshold re-parses the raw data and remembers the selected period.
7. PDF print: hide the control bar; cards and charts are not cut across pages (`break-inside: avoid`), but a card holding a long table must be allowed to break
   (`break-inside: auto`, `tr { break-inside: avoid }`, `thead { display: table-header-group }`), otherwise the whole card is pushed to a new page and leaves a blank one.
   Check with `page.pdf()` and a contact sheet of the pages.
8. Performance with a full file (measured: 200 main items and 2,000 detail records load in about 1.2 seconds).
9. A narrow screen does not overflow sideways; dark mode is readable.

## Pitfalls met

- A group-note row also contained the header phrases, so the header row was detected wrongly: use a distinctive phrase.
- The header-normalising function dropped text in brackets and lost a distinctive phrase inside them (for example "Cause (master list)"): the lookup sheet was not recognised.
  When looking for a distinctive phrase, use the normalised form WITHOUT dropping brackets.
- An empty sample file froze the browser because of an unbounded loop over a date range.
- The export button of the mini library build still has `book_new`, `aoa_to_sheet`, `book_append_sheet`, `writeFile`; export the standard sheet names so the tool can
  reopen the file. Export raw data only, without formulas or dropdowns.
- Categorical palette: the grey "ungrouped" colour is deliberately neutral so it does not meet the chroma threshold; low contrast is compensated with number labels and a number table.
