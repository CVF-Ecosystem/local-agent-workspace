# Daily use guide

Local Assistant Workspace v1.9 keeps your documents, context and results in one folder. The assistant
still chooses the approach, tools and skills that fit.

## 1. Give work in plain language

Say what needs doing, the source if any, and the output you want. You do not need to remember
skill names, syntax or pick a mode before you start.

```text
Based on Intake_Regulation.docx, draft the file-intake procedure.
Use the project's existing procedure template. Mark anything without enough basis so I can confirm it.
No need to export to Word yet.
```

For small jobs, just say what to fix:

```text
Tighten this paragraph, keeping the figures and department names. Return the edited version straight away.
```

The assistant can work directly when the context is already enough. It does not need to read STATE,
look up skills or make a plan just because this is a workspace project.

## 2. Continue unfinished work

When the task depends on the project, `PROJECT.md` gives the stable information and
`.agent/STATE.md` shows how far you got. `HANDOFF.md` is only useful when something needs
handing over.

```text
Continue the work in progress in STATE. Finish the form-filling instructions;
do not rewrite the fields already decided. Use HANDOFF if it has content.
```

You do not need to ask the assistant to read the whole history. When you do not know where a source
is, the index can help; when you point to the exact file, it can be opened directly.

You can say “reply as before” or “the next weekly report”. The assistant reuses the suitable method, reads current sources and keeps still-applicable decisions in this project. Methods can be reused in another project; the previous project's documents, account information and authority do not travel with them.

## 3. A draft request and a file request are different

| What you need | How to ask |
|---|---|
| Review the content first | “Write a draft in the conversation, no file yet.” |
| A finished file to use | “Create a Word file from the template and save it in output/.” |
| A local edit | “Only edit section 3, keep the rest.” |
| An HTML report | “Create an offline HTML file from this table, with a filter by channel.” |

A request for a usable file includes finishing the file and checking what is needed to use it.
It does not default to stopping at a draft, and it does not default to a long test-and-fix loop.
There are no required work modes.

## 4. Use sources and templates

You can place sources in `references/` or leave them where they are. When useful,
`.agent/INDEX.md` records which source is where and what it is for.

Your organisation's templates and confirmed regulations carry business weight. Templates that
come with a skill are only examples to refer to; they do not become regulations. The assistant
should point out what is missing rather than add roles, deadlines or authority on its own.

Once a source has been read, the relevant part can be reused from context. If the source was
just edited, or a conclusion depends on one clause, check that part again.

## 5. Let the assistant pick the skill

The workspace has fourteen suggested skills, from drafting documents (`office-documents`,
`internal-comms`, `doc-coauthoring`), analysis (`document-comparison`, `spreadsheet-check`),
charts and reports (`data-charts`, `html-reports`), processes and meetings (`process-mapping`,
`meeting-minutes`), correctly formatted administrative documents (`vn-admin-documents`), Excel workbooks and tools (`excel-workbooks`, `excel-html-viewer`) to editing
(`vietnamese-editing`) and the source library (`source-library`). You do not have to call them by name.

There are also six trial domain packs to install when needed: legal, records management, ports and logistics, HR and administration,
internal accounting and academic research. Packs with legal requirements include a basis table to check; the research pack provides methods and source-checking rules. The assistant uses installed packs by itself and suggests installing a
missing one.

The assistant can use a native skill, a workspace skill, a combination, or no skill at all. The
criterion is fit with the work and what is actually available, not where it comes from.
`ACTIVE` in the index does not mean a skill must be loaded in every session.

Details and examples are in `SKILLS_GUIDE.md` in this folder.

## 6. Use with Claude, Codex and Gemini through Antigravity

Open the project folder or grant access with whatever the application supports. If the assistant has
not read the shared instructions, you can send:

```text
This folder uses Local Agent Workspace. Refer to AGENTS.md and the relevant information in
PROJECT.md. Use STATE when continuing unfinished work. Choose the tools or skills that fit the
request best; work directly when there is enough information.
```

`CLAUDE.md` and `GEMINI.md` are thin adapters for environments that support the matching way of
reading. Do not assume Gemini CLI and Antigravity load files the same way. When it is not loaded
automatically, pointing the assistant to the path of `AGENTS.md` is a clear way to start.

The skills in the package are looked up as files; unzipping does not install them into the
applications' native libraries. A native skill that exists in one session is not guaranteed to
exist in another. The package does not change any provider's global configuration.

If the assistant cannot read or write the folder, grant permission or bring the right file into the
session using the application's own mechanism; do not treat a line of instruction as having
created a connection.

## 7. Save results and end the session

`working/` holds work in progress; `output/` holds the current deliverable; `archive/` holds old
versions when needed. Keep source documents unchanged and only replace them when you have asked
for it.

You do not need a checkpoint after every answer. Write STATE when there is a decision, a new
output or a next step the next session needs to know. Use HANDOFF for a short handover; leave
it as `None` when unused. PENDING_LESSONS is only an optional place for experience that is
really reusable.

Say clearly if a file was not saved where intended. Keeping files local does not mean the model
processes everything offline, or that every cloud output comes back to your machine on its own.

## 8. When the assistant starts doing too much

Narrow it with a specific request, for example:

```text
Only finish the part I just asked for. No need to add options or standardise
other parts. Stop once that version is usable.
```

If the assistant lacks important information, let it read the right source or ask the right question.
The aim is to do just enough to get the job right, not to skip checks that are needed.

`AGENTS.md` has a "Work limits" block: small edits once, medium tasks one pass plus at most one
check, one self-correction only, one combined question. If the environment (especially a cloud
one) does not read `AGENTS.md` by itself, paste the text from section 5 of `NEW_PROJECT_GUIDE.md`
into the Project instructions.

For high-stakes work (legal, financial, figures or documents leaving the organisation or going for
signature) the assistant applies "High-caution mode" from `AGENTS.md`: check each figure, date, name and
clause against the source and state what could not be checked. You can remind it: "This goes out of
the organisation, use high-caution mode."

## 9. Sensitive data and recording AI assistance

Before giving a document to the AI, ask yourself: does this file contain passwords, access keys, personal data of customers or
staff, or confidential documents? If so, mask or remove that part first (replace real names with labels, delete identification
numbers) and record the level in the "Data sensitivity" line of `PROJECT.md`. Follow your organisation's security rules; the
package does not replace them.

The package keeps files on your computer, but when you open them with an AI app, what you hand over is still processed by that
app under its own terms. Do not use this project for data that your organisation's rules forbid sending to AI services.

For documents that go outside or to be signed, the signer is responsible for the content: read the whole text again and check the
figures against the sources. If your organisation requires recording AI assistance, add a line to the file (for example: "Draft prepared
with AI assistance, reviewed by [name]").

## 10. Reading the assistant's "Execution declaration"

When the assistant reads, checks, compares or calculates on your files, the end of its reply should carry an "Execution
declaration" block (rule 9 in `AGENTS.md`): the method (script run with its command, or manual reading), the skill read, the sources read,
the files created or changed, and what was not checked. Read this block before trusting the result. Findings about numbers should
carry the actual numbers; ambiguous values (such as `1.234`) should be given both readings. If the block is missing or vague, ask
the assistant to add it. The declaration is written by the assistant itself, so it is not absolute proof; for important work, the script's
"Trace" line (file, sha256, run time) lets you cross-check. Save the reply to a file and run
`python tools/check_output.py --declaration <file>` to check the declaration is complete.

## 11. The role of the HTML guides

`START_HERE.en.html` gathers the handbook for the user; each Markdown guide also has an HTML
version with the same name. You only need to read one form. The assistant does not need to load HTML,
read every README or update the HTML in each office task.

When you edit a Markdown guide yourself and want to update the presentation, run
`python tools/build_guides_html.py` from the project root (see `tools/README.md`), or ask the
assistant to run it. The HTML does not sync by itself when you edit Markdown; add `--check` to see
whether the HTML still matches.

## 12. The control panel (APP.bat)

The **Work record** page shows referenced assignments, results, decisions and waiting items saved by the assistant. Viewing it reads records without calling AI or replacing a draft. A match means the checked data still matches, not that the content was approved. Continue/stop buttons copy a request for you to give Main; they do not stop a running application. If no work is referenced, ask the assistant to update the current work record without regenerating results.

Double-click `APP.bat` (Windows) or `APP.command` (macOS) to open the control panel in the browser. Opened in the template,
its main page is "New project": type a task name and a copy is created next to the template (`tools/new_project.py`); the
template does not change. Opened in a project, **The work** page holds: "Continue the work" (read from `.agent/STATE.md`:
where things stand, what waits for you, the next step), "Give the assistant a task" (steps and a message to copy, with how
to check the assistant reads the right project), "Source documents" (files in `references/`) and "Results" (files in `output/`).
Check before delivery (`check_output.py`) and the source library come right below. The collapsed "Manage and maintain" group
holds the rest: managing skills and domain packs, copying skills into apps (`install_skills.py`), pending merges, updating the
package, setting up or bringing into an existing project, package maintenance. The **App status** page shows the version, Python, optional features still missing (with how to fix each), unfinished transactions and recent operations.

Actions that write files always run a preview first; read the result, then press "Apply". The panel runs on this computer
(address 127.0.0.1, with a new access code each time), uses no network, and stops about 3 minutes after the
page is closed. "Choose…" opens the computer's folder picker; if there is none, type or paste the path. The panel does not
replace giving work to the assistant; it only gathers the `python tools/...` commands in one place.

Output checks have three states: passed within supported scope; findings/review required; not checked. Missing files, unsupported formats and missing dependencies never count as a pass. Word checks cover body, headers/footers and footnotes/endnotes, not layout, image text, comments or tracked changes. Excel and the source library require `openpyxl`; if missing, run `python -m pip install openpyxl`. Tools never install it automatically.

The panel deletes none of your files, with two exceptions. "Roll back" on an unfinished transaction removes the new files that transaction created, if you have not edited them. "Clear history" removes only the operations log. Both ask for confirmation first. If a write was interrupted, see section 9 of `EXISTING_PROJECT_UPGRADE_GUIDE.md`.

**Operations history.** Each button press writes one line: the time, the action name, the result, the number of files affected and the transaction id if there is one. It never records document content, file names, names of people or typed values. The panel keeps the latest 500 lines; the App status page shows the latest 20. To delete the history, press "Clear history"; documents and transactions are not affected.

**Diagnostics bundle.** "Create diagnostics bundle" writes one ZIP file on this computer, to `.agent/runtime/diagnostics/diagnostics-<time>.zip`, for a helper to look at when something goes wrong. It contains the package version, workspace type, Python and operating system, the state of optional features, pending merge files (relative paths only), unfinished transactions, the operations history and the package integrity check. It contains no document content, project name, names of people or absolute paths; folder paths and the computer's user name are masked. It is never sent automatically. Press "Open the bundle folder" to review it; you decide whether to share it.

**Compare on the Pending merges page.** "Compare" shows the differences between the current file and its `.new` copy, as blocks with line numbers. It does not change either file, merge or overwrite; the action may be recorded in the operations history. Files over 256 KB, or files that are not UTF-8 text, are not shown in the panel; open both versions in their own app. It is for viewing only. Replacing the current file or storing the `.new` is a separate step that exists only for some files; how each kind of file is handled is in section 3 of "Use with an existing project and upgrade the package". For files outside that scope, merge by hand with whoever owns the file; do not delete the `.new` just to clear the warning.
