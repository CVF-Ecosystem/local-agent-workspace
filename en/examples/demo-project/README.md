# Demo project: try it in 10 minutes

This is a **fake** project (invented data) so you can try the package without preparing real documents. Open the
**package root folder** (not just this folder) in the AI app you use (Claude, Codex, Gemini...), so the agent can read `AGENTS.md` and the skills, then send the requests below one at a time.
Each uses a different skill.

| File | Contents (fake) |
|---|---|
| `data/weekly_log.csv` | A daily log of files received and completed, with a few deliberate errors |
| `notes/meeting_notes.txt` | Unsorted meeting notes |
| `docs/procedure_v1.md`, `docs/procedure_v2.md` | Two versions of a short procedure |

## Try 1: check a data table (skill `spreadsheet-check`)

```text
Check examples/demo-project/data/weekly_log.csv before I take figures for a report. Report findings only, do not edit the original file.
```

You should see: a text cell inside a number column, a duplicate row, an ambiguous number like `1.234`, and a total row that does not match. Each finding about a total carries the actual numbers (value recorded versus recalculated value), and the cell "1.234" is given both readings (1234, or one point two three four) with the total under each. Locations use the row numbers in the file: "n/a" in row 5, "1.234" in row 6, the duplicate rows are 7 and 8, the total row is row 11.

## Try 2: write meeting minutes (skill `meeting-minutes`)

```text
From examples/demo-project/notes/meeting_notes.txt, write meeting minutes: decisions, action items (owner, deadline), open issues.
Where information is missing write "to be confirmed"; do not guess.
```

You should see: three clearly separated groups; actions missing an owner or a deadline are marked "to be confirmed", not invented. Something merely reported or done by a person (for example Hùng reported the error to the technical team) is not turned into a task assigned to that person; a milestone such as "from next week" is kept verbatim.

## Try 3: compare two versions of a procedure (skill `document-comparison`)

```text
Compare examples/demo-project/docs/procedure_v1.md and examples/demo-project/docs/procedure_v2.md, build a table of the meaningful changes and state their impact.
```

You should see: a table listing real changes only (an added step, a changed owner, a different deadline), not differences of wording alone (step 1 of version 2 is only reworded and should not be in the table). The impact column carries the label "(inferred)" (in the column header or per item).

## Check how the agent worked

At the end of each reply the agent should give an **"Execution declaration"** (method, skill, sources, files, not checked; see `AGENTS.md`).
For Try 1 the package ships a `spreadsheet-check` script: the declaration should give the command run and the script's "Trace" line, or say
why the work was done manually. A missing block is a sign the agent did not follow the package guidance. For a quick check, save the
reply to a file and run `python tools/check_output.py --declaration <file>`.

## After trying

If the results look sensible you have understood the way of working: give tasks in plain words, name the source file and the output you want.
Then create your real project with `SETUP.bat` / `SETUP.command` in the package root. You can delete the `examples/` folder if you do not need it.
