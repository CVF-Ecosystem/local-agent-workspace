# Demo project: try it in 10 minutes

This is a **fake** project (invented data) so you can try the package without preparing real documents. Open the
`examples/demo-project/` folder in the AI app you use (Claude, Codex, Gemini...), then send the requests below one at a time.
Each uses a different skill.

| File | Contents (fake) |
|---|---|
| `data/weekly_log.csv` | A daily log of files received and completed, with a few deliberate errors |
| `notes/meeting_notes.txt` | Unsorted meeting notes |
| `docs/procedure_v1.md`, `docs/procedure_v2.md` | Two versions of a short procedure |

## Try 1: check a data table (skill `spreadsheet-check`)

```text
Check data/weekly_log.csv before I take figures for a report. Report findings only, do not edit the original file.
```

You should see: a text cell inside a number column, a duplicate row, an ambiguous number like `1.234`, and a total row that does not match.

## Try 2: write meeting minutes (skill `meeting-minutes`)

```text
From notes/meeting_notes.txt, write meeting minutes: decisions, action items (owner, deadline), open issues.
Where information is missing write "to be confirmed"; do not guess.
```

You should see: three clearly separated groups; actions missing an owner or a deadline are marked "to be confirmed", not invented.

## Try 3: compare two versions of a procedure (skill `document-comparison`)

```text
Compare docs/procedure_v1.md and docs/procedure_v2.md, build a table of the meaningful changes and state their impact.
```

You should see: a table listing real changes only (an added step, a changed owner, a different deadline), not differences of wording alone.

## After trying

If the results look sensible you have understood the way of working: give tasks in plain words, name the source file and the output you want.
Then create your real project with `SETUP.bat` / `SETUP.command` in the package root. You can delete the `examples/` folder if you do not need it.
