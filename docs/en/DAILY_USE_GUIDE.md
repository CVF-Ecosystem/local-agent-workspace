# Daily use guide

Local Agent Workspace v1.1 keeps your documents, context and results in one folder. The agent
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

The agent can work directly when the context is already enough. It does not need to read STATE,
look up skills or make a plan just because this is a workspace project.

## 2. Continue unfinished work

When the task depends on the project, `PROJECT.md` gives the stable information and
`.agent/STATE.md` shows how far you got. `HANDOFF.md` is only useful when something needs
handing over.

```text
Continue the work in progress in STATE. Finish the form-filling instructions;
do not rewrite the fields already decided. Use HANDOFF if it has content.
```

You do not need to ask the agent to read the whole history. When you do not know where a source
is, the index can help; when you point to the exact file, it can be opened directly.

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
come with a skill are only examples to refer to; they do not become regulations. The agent
should point out what is missing rather than add roles, deadlines or authority on its own.

Once a source has been read, the relevant part can be reused from context. If the source was
just edited, or a conclusion depends on one clause, check that part again.

## 5. Let the agent pick the skill

The workspace has eleven suggested skills, from drafting documents (`office-documents`,
`internal-comms`, `doc-coauthoring`), analysis (`document-comparison`, `spreadsheet-check`),
charts and reports (`data-charts`, `html-reports`), processes and meetings (`process-mapping`,
`meeting-minutes`), correctly formatted administrative documents (`vn-admin-documents`) to editing
(`vietnamese-editing`). You do not have to call them by name.

The agent can use a native skill, a workspace skill, a combination, or no skill at all. The
criterion is fit with the work and what is actually available, not where it comes from.
`ACTIVE` in the index does not mean a skill must be loaded in every session.

Details and examples are in `SKILLS_GUIDE.md` in this folder.

## 6. Use with Claude, Codex and Gemini through Antigravity

Open the project folder or grant access with whatever the application supports. If the agent has
not read the shared instructions, you can send:

```text
This folder uses Local Agent Workspace. Refer to AGENTS.md and the relevant information in
PROJECT.md. Use STATE when continuing unfinished work. Choose the tools or skills that fit the
request best; work directly when there is enough information.
```

`CLAUDE.md` and `GEMINI.md` are thin adapters for environments that support the matching way of
reading. Do not assume Gemini CLI and Antigravity load files the same way. When it is not loaded
automatically, pointing the agent to the path of `AGENTS.md` is a clear way to start.

The skills in the package are looked up as files; unzipping does not install them into the
applications' native libraries. A native skill that exists in one session is not guaranteed to
exist in another. The package does not change any provider's global configuration.

If the agent cannot read or write the folder, grant permission or bring the right file into the
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

## 8. When the agent starts doing too much

Narrow it with a specific request, for example:

```text
Only finish the part I just asked for. No need to add options or standardise
other parts. Stop once that version is usable.
```

If the agent lacks important information, let it read the right source or ask the right question.
The aim is to do just enough to get the job right, not to skip checks that are needed.

`AGENTS.md` has a "Work limits" block: small edits once, medium tasks one pass plus at most one
check, one self-correction only, one combined question. If the environment (especially a cloud
one) does not read `AGENTS.md` by itself, paste the text from section 5 of `NEW_PROJECT_GUIDE.md`
into the Project instructions.

For high-stakes work (legal, financial, figures or documents leaving the organisation or going for
signature) the agent applies "High-caution mode" from `AGENTS.md`: check each figure, date, name and
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

## 10. The role of the HTML guides

`START_HERE.en.html` gathers the handbook for the user; each Markdown guide also has an HTML
version with the same name. You only need to read one form. The agent does not need to load HTML,
read every README or update the HTML in each office task.

When you edit a Markdown guide yourself and want to update the presentation, run
`python tools/build_guides_html.py` from the project root (see `tools/README.md`), or ask the
agent to run it. The HTML does not sync by itself when you edit Markdown; add `--check` to see
whether the HTML still matches.
