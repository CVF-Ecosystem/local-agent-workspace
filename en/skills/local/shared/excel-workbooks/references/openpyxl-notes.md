# Technical notes for building Excel with openpyxl

Verified experience; open when actually building.

## Formulas

- Use classic functions only (`IFERROR`, `COUNTIFS`, `SUMIFS`...). Avoid `IFS`, `XLOOKUP`, `TEXTJOIN`, `MAXIFS`: openpyxl does not add the `_xlfn`
  prefix, so Excel shows `#NAME?`. Scan all formulas with a regex to list the function names.
- No array formulas. Take the k-th item of a period with a hidden helper key (value + `ROW()/1e7`) using `SMALL`/`COUNTIF`/`MATCH`; rank with
  `SUMPRODUCT(SUMIFS(...))` plus a tie-break.
- Filtering by month: add a helper month-key column and then `COUNTIFS`/`SUMIFS`; avoid comparing dates directly with text cells. The string
  `TEXT(date,"MM/YYYY")` depends on the Excel language; machines using a dot for thousands and a comma for decimals can differ. For numbers use
  `FIXED(number, n)` instead of `TEXT(...,"#,##0")`. A cell's `number_format` is not affected.
- Sheet names with spaces must be wrapped in single quotes: `'CASE LIST'!$B:$B`.
- Avoid `OR()` or `INDEX` on empty cells (`#VALUE!`): nest `IF` instead.
- A note string that starts with "=" is read as a formula (`#NAME?`). Write "Calc: ..." instead of "= ...".
- Multi-sheet formulas easily get a sheet or column name wrong without the code showing it, and a file created with openpyxl has no cached values. Recalculate with
  `recalc.py` (if available) or `soffice --convert-to xlsx`, then read it back with `openpyxl` using `data_only=True`; require 0 errors.

## Entry and formatting

- Dropdown: `DataValidation(type="list", formula1='"A,B"')`, `ws.add_data_validation(dv)`, `dv.add("B2:B200")`. Limits: prompt and error message up to
  255 characters, title 32, `formula1` 255; formulas under 8000 characters.
- Dependent dropdown: `OFFSET`/`MATCH`. Type times as `hh:mm`, roll over to the next day when the end time is earlier than the start; an empty Date/Code cell takes the row above through a hidden helper column.
- Status colours: `CellIsRule` (one rule per value) or `FormulaRule` when the condition depends on another cell (such as a threshold cell).
- Colour codes used: input `FFF2CC`; red `F8CBAD`, yellow `FFE699`, green `C6E0B4`; sample data `DDEBF7`.
- Row height does NOT grow with `wrap_text` when the file is created by openpyxl (text is cut at the bottom of the cell, visible only when rendered). Set it by hand:
  `height = max(30, ceil(characters / characters_per_line) * 15 + 10)`.
- Merged cells: if the merged area used to centre a national-motto line is too narrow, the text is cut at both ends; verified thresholds: total column width ≥ 54 for the motto,
  ≥ 42 for the company name. `fitToWidth` and `print_area` only scale the whole page when printing and do not fix this.
- The open-file error "found a problem with some content" is usually overlapping or duplicate merged cells; check before delivery.
- Printing: landscape, `fitToWidth`, repeat the header row; set `print_area` on sheets with hundreds of empty rows to avoid printing dozens of pages.
- Sheet protection without a password: lock formula cells, leave input cells open, allow filter and sort.
- openpyxl charts: one axis, colours as in the chart skill, anchor carefully so they do not overlap, and check the rendered image.

## Adding to an existing file

- Add the new block at the bottom of the sheet; `insert_rows` shifts rows while formulas on other sheets still point at the old addresses.
- When changing a user's file, save the new version under a new name and do not overwrite the original.

## Checks before delivery

1. Formulas recalculated, 0 errors; figures in Word and Excel match.
2. Render to PDF or image (`soffice --convert-to pdf`, `pdftoppm`); look at the widest table and the table with totals.
3. Try exceeding the report table's limit: there must be a clear warning line ("showing only N, see the full figures on the summary sheet") and no formula errors.
4. With a blank threshold cell the formulas still run and raise no flag.
5. State clearly what was not tried in real Excel.
