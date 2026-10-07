# Reviewing and revising an existing proposal or internal regulation

Use when the user hands over a proposal or regulation (`.docx`) and asks you to assess it, explain to leadership why it should change, then present it again. Comparing two versions: `document-comparison`.

## Process

1. **Check against the source before scoring.** Read the whole proposal, then read the procedures of the units it mentions to check each statement about the current situation. Score in three layers:
   is the diagnosis right; does the design meet the proposal's own principles (for example it demands row locking, logs and permissions but chooses a tool that cannot do them); the project-management part
   (measurable goals, cost, risks, owner, a feasible schedule).
2. **Ask the user what only they know** (how something is calculated, time cut-offs) with short multiple-choice questions, instead of guessing and building the design on an assumption. When the user corrects you
   later, fix exactly the affected part, remove the conditions and warnings added on the wrong assumption, and update every related file consistently (proposal, evaluation table, appendix).
3. **Evaluation table for leadership**: landscape A4 Word, one to two pages; header and title; one general conclusion paragraph; a six-column table (No., Item, Situation in the old version, If not changed the
   consequence is, Proposal with the matching section in the new version, Priority; priority cells lightly shaded by level); a "Requests" paragraph listing the decisions needed; an attachments line. Number
   the rows in code so adding or removing a row does not break the numbering.
4. **Edit the source file directly** to keep images, tables, headers and footers (technique: `word-technical-notes.md`). Sections with many cross-references are not renumbered: insert new content as sub-sections or
   an appendix. After editing: render, look at each newly added page, count pages, remove wrong cross-references.
5. **Do not invent numbers.** Every threshold, rate or date the agent proposes is marked "proposal, to be decided by the person with authority"; an unmeasured indicator is "not yet counted, to be measured in the
   first pilot period"; a missing cost is stated as not yet estimable, with the reason; a figure taken from records not yet verified is "per the records on hand, not verified".
6. **The accompanying Excel appendix** is a data template, not just a text description: sample rows shaded grey and marked "SAMPLE ROW"; a sheet that is only illustrative is marked "SAMPLE DATA" in the first description row and in the proposal's
   sheet list (see `excel-workbooks`). Check by recalculating in LibreOffice and reading it back, making sure there are no `#` errors.
7. **Legal basis** (laws, accounting circulars...): look it up to confirm the provision and that the document is still in force before citing; in the proposal write briefly "basis to be reviewed when the regulation is issued",
   not as a legal conclusion. Do not use a replaced document as the basis for a new one.
8. Save a short note (what was done, proposals still open, what was not cross-checked) in `.agent/STATE.md` or the project's notes; update it when things change so an old note does not say "file not written" after the file is done.
