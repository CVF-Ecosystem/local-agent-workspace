# Pre-delivery checklist

Use it briefly and pick the parts that fit the deliverable. Do not turn it into a procedure for small tasks. A tool covers the mechanical part:
`python tools/check_output.py <file>` (finds unfilled places, illustrative-template labels, network resources in HTML; hands CSV/Excel to `spreadsheet-check`).

## Every deliverable

- [ ] It matches the request: kind of deliverable, audience, scope, format.
- [ ] No unfilled places (`[Name]`, `[...]`) and no "template / illustrative / fake data" label left.
- [ ] Places lacking a basis are marked "to be confirmed"; no invented figures, dates, names or deadlines.
- [ ] Facts taken from sources are kept apart from the agent's own proposals.
- [ ] The user's original files were not overwritten; the new file has a clear name (and a version suffix when it replaces an older one).
- [ ] The hand-over message says what was done, what was not checked, and what the user must confirm.
- [ ] Work with findings or figures ends with an "Execution declaration" block (method, sources, files, not checked); findings about numbers state the actual numbers (see `AGENTS.md`).

## Documents, procedures, forms

- [ ] Terms, unit names and job titles are consistent and match the source.
- [ ] Step numbers, section numbers and cross-references (for example "see section 3") are still right after edits.
- [ ] Roles, deadlines and conditions come from the source or are marked "to be confirmed".
- [ ] Forms: required fields, units, date format and filling instructions are clear.

## Administrative documents, going outside, for signature

- [ ] Apply "High-caution mode" in `AGENTS.md`: check every number, date, name, agency name, and the number and date of the basis documents against the source.
- [ ] The format follows the unit's rules or the applicable regulation (see `vn-admin-documents`); number, date, signature and signing authority are left for the authorised person to fill in.
- [ ] Legal remarks are only suggestions for the authorised person to confirm.
- [ ] The signer was reminded to read the whole text again.

## Data reports, spreadsheets

- [ ] `spreadsheet-check` was run on the source data; findings that affect the figures were handled or stated.
- [ ] Totals were recomputed and the details checked (each group, each row), not only the total figure.
- [ ] Unit, reporting period and data source are stated; missing data shows "—" or "not available", not a guessed 0.
- [ ] Figures in the explanation match the table and the charts.

## HTML reports/dashboards

- [ ] Opened offline (no network needed); `check_output.py` reports no network resources.
- [ ] `isDemo` is set correctly; title, period, source and comments were replaced with real content.
- [ ] Charts: bars start at 0, labels and units are complete, the accompanying data table matches.
- [ ] Tried with bad data (empty, missing, non-standard column names): the tool says what is wrong and where.
