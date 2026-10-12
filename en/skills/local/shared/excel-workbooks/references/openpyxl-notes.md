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
- An empty cell with business meaning (for example "no adjustment = on time"): the formula returns 0 and a three-part number format `0;"Early "0;"On time"`; the cell shows text, the value stays a number for sums and filters.
- Date-times written into cells: round to the minute `round(x*1440)/1440` (rounding by decimals shows 11:00 as 10:59). In formulas: `TEXT(ROUND(t*1440,0)/1440,"hh:mm")`.
- Cross-checking with formulas (no arrays): the number of parent records containing time x is `SUMPRODUCT((col_from<=x)*(col_to>=x))`; when it is 1 get the code with
  `INDEX(col_code,SUMPRODUCT((col_from<=x)*(col_to>=x)*(ROW(col_code)-first_row+1)))`; membership in a list with `ISERROR(SEARCH(code,list))`.

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

## Editing the XML directly (books in use)

An `.xlsx` file is a zip. Use this when everything openpyxl might drop must be kept (`x14` dropdowns, modern conditional formats).

- Find a sheet's file through `xl/workbook.xml` and `xl/_rels/workbook.xml.rels`; the `sheetN.xml` order can differ between files made from the same template.
- Replacing a cell: write the full formula in `<f>` and drop `<v>`; for a shared-formula column (`t="shared"`) replace the whole group; text uses `t="inlineStr"` or an existing `sharedStrings.xml` entry.
- Adding a sheet: create `sheetN.xml` (reuse style indexes of a similar sheet), add the relationship in rels, an `Override` in `[Content_Types].xml`, a `<sheet>` element in the workbook;
  when inserting before the last sheet shift the `localSheetId` of defined names from that position on; update `docProps/app.xml`. Dropdowns fed from another sheet: define a name (`definedName`) and use it.
- Inserting a section in the middle of a report sheet: shift every following row (row numbers, cell references, merged ranges, `dimension`, page breaks, print area); assert no formula or range further down still points at old addresses.
- Styles: add a `numFmt` and clone an `xf` in `styles.xml`. Remove `calcChain.xml` (with its rel and `Override`) and set `fullCalcOnLoad="1"` so Excel recalculates on opening.
- Rewrite the zip keeping entry order; count dropdowns before and after; the patch script asserts each replaced string (exactly one match) and runs on the blank template and every period file.

## Checks before delivery

1. Formulas recalculated, 0 errors; figures in Word and Excel match.
2. Render to PDF or image (`soffice --convert-to pdf`, `pdftoppm`); look at the widest table and the table with totals.
3. Try exceeding the report table's limit: there must be a clear warning line ("showing only N, see the full figures on the summary sheet") and no formula errors.
4. With a blank threshold cell the formulas still run and raise no flag.
5. State clearly what was not tried in real Excel.
6. LibreOffice does not recalculate cells that still hold a cached value: for an XML-edited file make a test copy with every `<v>` after `</f>` removed, then `soffice --convert-to xlsx`, read with `data_only=True`, require 0 error cells. Use that copy only for checking; deliver the XML-edited file. Also test negative cases (deliberately wrong data must be flagged by the Check column).
