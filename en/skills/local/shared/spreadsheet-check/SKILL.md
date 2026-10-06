---
name: spreadsheet-check
description: >-
  Suggestions for a quick check of an Excel/CSV file before its figures are used for a report,
  summary or HTML dashboard: structure, empty cells, duplicates, data types, units, totals that do
  not match. Reports findings only and never edits the original data.
  Triggers when the user says: "check the Excel/CSV file", "is the data clean", "check before making the report".
metadata:
  version: "1.0"
---

# Checking a spreadsheet before use

Use when you are about to take figures from a spreadsheet for a report or chart. If the user only asks
for one simple number, read the relevant cell/column and answer; do not check the whole file.

## How to work

1. **Understand the structure:** sheet names, the area with data, the header row, merged cells, hidden
   sheets. With many sheets, go deep only into the sheet relevant to the request.
2. **Check the columns that bear on the result:**
   - empty cells in key columns (date, code, quantity, status);
   - duplicate rows or codes;
   - numbers stored as text, dates in several formats, the same item written several ways;
   - mixed units (tonnes/kg, thousand/million) or mixed reporting periods;
   - a total row that does not equal the sum of the rows; formula errors (`#REF!`, `#DIV/0!`);
   - unusual values (negative, very large, outside the period) - only report, do not conclude they are wrong.
3. Use a calculation tool or a script when the table is large; compare a few rows by eye. If you only
   sampled, say what scope was checked.

## Bundled script (optional)

`scripts/check_spreadsheet.py` runs the checks above by machine, read-only, and does not edit the file:

```text
python skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py FILE.xlsx --key "Code" --lang en
python skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py FILE.csv --lang en
```

CSV needs only Python 3.8+. Excel needs `openpyxl` (`pip install openpyxl`); without it the script says so
and stops, and you can then export the sheet to CSV or check another way. `--sheet NAME` checks one
sheet only; `--key` names the code column used to find duplicates; `--lang vi` gives Vietnamese output.
Results are grouped into the three levels below; a person still has to judge the business meaning.
Numbers such as `1.234` or `1,234` are reported as "ambiguous" rather than guessed.

## Result

Return a short list ordered by impact, each item naming the sheet, a column or example row, and a count:

- **Affects the figures:** must be handled or confirmed before use.
- **To ask:** an unclear definition or unit.
- **Notes:** not affecting the current result.

If no problem is found within the scope checked, state that scope rather than declaring the file "correct".

## Limits

Do not edit, re-sort or overwrite the original file; if a cleaned copy is needed, make a new one in
`working/` when asked. Do not replace missing cells with 0 or a guessed value. Do not build a report or
chart unless asked; when it is needed, continue with `html-reports`. When the list of findings is done, stop.
