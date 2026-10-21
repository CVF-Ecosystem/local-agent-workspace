# Local Assistant Workspace v1.9

A local workspace for office work with Claude, Codex, Gemini or another assistant.

**Open `START_HERE.en.html` to read the handbook in English (or `START_HERE.html` for the Vietnamese version; every page has a language switch button).** The page opens directly
in a browser, with no installation, server, online font or network connection.

**Recommended trial: [1.9.0-rc2](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc2) (prerelease), not final.** RC2 replaces RC1 as the recommended download for feedback; RC1 remains available for reference. The current stable release is [1.8.0](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/latest). The RC package keeps `VERSION` at `1.9.0`; include the tag `v1.9.0-rc2` in feedback.

[Send feedback on GitHub](https://github.com/CVF-Ecosystem/local-agent-workspace/issues/new?template=phan-hoi.md) or use the [included feedback form](../docs/FEEDBACK_FORM_VI_EN.md). Include the RC tag, OS, Python version, AI app and steps to reproduce; remove names, figures and confidential information before sending.

## Getting started

1. **Keep one template:** download the ZIP from [Releases](https://github.com/CVF-Ecosystem/local-agent-workspace/releases/tag/v1.9.0-rc2) and unzip it once into its own folder. That folder is the template: keep it as is and do not work in it (nor inside the ZIP).
2. **Make a project for each piece of work:** double-click `APP.bat` (Windows) or `APP.command` (macOS) in the template and type a task name on the "New project" page, press "Preview project creation", then "Apply". A copy is created next to the template, already set up; the template does not change.
3. **Add sources and give the task:** copy documents into the project's `references/`, open the project folder in your AI app (Claude, Codex, Gemini) and send the message copied from the project's control panel (fill in the part in square brackets first). Results go to `output/`.
4. **Continue next time:** open `APP` in the project folder; the "Continue the work" box shows where things stand; the "Review unfinished work" message has the AI assistant summarise before carrying on.

The control panel needs Python 3.8+. Without Python: copy the whole template folder (including the hidden `.agent/` folder), rename it and open it in your AI app; see `docs/en/NEW_PROJECT_GUIDE.md`. Excel checking and the source library also need `openpyxl` (`python -m pip install openpyxl`); tools never install it. To try it first with synthetic data: `examples/demo-project/README.md`, in a trial project.

## What is it for?

A starter folder for every office-work project you do with an AI assistant, built to one standard. It helps the AI remember the
context between sessions (no explaining again), keeps files tidy and sets clear working rules (no invented figures, no
overwriting originals), with fourteen skills for common tasks; unzip it on any computer and get the same standard. The full
introduction is at the top of `START_HERE.en.html`.

Reading documents, drafting procedures, forms and reports; handling spreadsheets when needed; continuing
work across sessions; producing lightweight HTML reports. The workspace holds the documents and the project
context, and the assistant picks the way of working that fits the request.

The guides are working suggestions, not a mandatory process for every task. Small jobs can be done directly;
jobs that need a source or a template open only the useful part. This is not an application, an assistant
framework or a software development kit.

## Optional setup and reference guides

Besides the control panel there are two other ways to the same result. `SETUP.bat` / `SETUP.command` asks questions in a command window; run in the template, it asks whether to make a copy (recommended) or set up this folder itself. Or use the command in the template (needs Python 3.8+; nothing else to install):

```text
python tools/new_project.py --name "Task name" --apply
```

Add `--dest` to choose the location and `--lang en` for the English assistant instructions, skills and READMEs; leave out `--apply` to only preview. If you copied the folder yourself, set it up inside the copy with `python tools/init_project.py --name "Project name" --lang en`. The package version is in `VERSION`.

The control panel (`APP`) has one main job in the template: create a new project. In a project, **The work** page holds: continue the work (read from `.agent/STATE.md`), give your AI assistant a task (message to copy), source documents and results. Managing skills and domain packs, copying skills into apps, updating the package, pending merges, maintenance and app status sit in the "Manage and maintain" group. The panel is only an interface for the tools in `tools/`; it runs on your computer (no network) and stops when the page is closed. If a write was interrupted, the **App status** page lets you resume or roll it back (see `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`, section 9).

- New project: `docs/en/NEW_PROJECT_GUIDE.md` or the `.html` file of the same name.
- Existing project and package upgrade: `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md` or `.html`.
- Daily use: `docs/en/DAILY_USE_GUIDE.md` or `.html`.
- Choosing and using skills: `docs/en/SKILLS_GUIDE.md` or `.html`.

The Markdown and HTML versions have the same guide content. The assistant can read Markdown and
does not need the HTML version as well. HTML is for users, not default context.

## Resources in the package

| Resource | Useful when |
|---|---|
| `office-documents` | Drafting/editing business documents; reference templates for SOPs, forms, internal updates. |
| `html-reports` | Producing a periodic report or indicator overview page as one HTML file. |
| `vietnamese-editing` | Editing Vietnamese text when the style really needs adjusting; not run after every document. |
| `document-comparison` | Comparing two versions of a regulation/process/form into a change table. |
| `spreadsheet-check` | A quick check of Excel/CSV before taking figures for a report; does not edit the original file. |
| `meeting-minutes` | Meeting minutes: decisions, action items, open issues. |
| `process-mapping` | Step tables, RACI and flow diagrams for a process. |
| `internal-comms` | Progress reports, announcements, newsletters, FAQs, incident reports. |
| `doc-coauthoring` | Co-authoring a large document step by step; use only when you want to work through it in depth. |
| `data-charts` | Drawing charts from a data table into offline HTML (SVG), with templates and a chart selection guide. |
| `vn-admin-documents` | Vietnamese administrative documents in the proper format: official letter, submission, report, notice. |
| `excel-workbooks` | Building tracking workbooks, data-entry forms, self-summarising reports and calculation appendices in Excel. |
| `excel-html-viewer` | A single-file offline HTML tool that reads Excel files to show figures visually. |
| `source-library` | The source library in `references/` (legal documents, company rules, templates) with an Excel index; look up before quoting. |

The fourteen skills are in `skills/local/shared/` and are recorded as `AVAILABLE` in
`.agent/SKILL_INDEX.md`. The assistant uses its own capabilities and native skills; the package skills
only add what is missing (templates, sources, business rules). Not using a skill is also a valid choice.
Adding or importing skills and packs follows the intake standard in `skills/README.md`.

The HTML templates were written specifically for the package, with clearly labeled illustrative data.
No upstream template, script, font or skill was copied as a whole.
Sources of ideas and the scope of what was consulted are in `docs/en/SOURCES_AND_REFERENCES.md`.

## Files worth knowing

```text
project/
├── START_HERE.html          Guide for users (Vietnamese)
├── START_HERE.en.html       Guide for users (English)
├── SETUP.bat / SETUP.command  Double-click to create or set up a project (question-and-answer wizard)
├── APP.bat / APP.command      Control panel in the browser (optional)
├── README.md
├── AGENTS.md                General instructions for agents
├── PROJECT.md               Stable project context
├── CLAUDE.md / GEMINI.md     Thin adapters, depending on the environment
├── en/                      English tree, overlaid onto the root by init --lang en
├── tools/                   Initialization, upgrade, domain packs, output check, package check, packaging, HTML rebuild
├── CHANGELOG.md
├── LICENSE                  MIT license
├── VERSION                  Package version number (single source)
├── MANIFEST.sha256          Hashes of the package files, to check integrity
├── docs/                    Guides in Markdown + HTML, Vietnamese–English glossary
├── examples/demo-project/   Practice exercise (sample data) to try in 10 minutes
├── roles/                   Scout, Worker, Reviewer contracts; native integration pending
├── packs/                   Domain packs (installed on demand with tools/pack.py)
├── .agent/                  STATE, HANDOFF, INDEX, SKILL_INDEX, PENDING_LESSONS
├── skills/
│   ├── local/shared/        Eleven skills and their templates
│   ├── local/project/       Project-specific guidance, if needed
│   ├── external/            Outside skills added by the user
│   └── inbox/               A temporary place, optional
├── references/              Your business sources and templates
├── working/                 Work in progress
├── output/                  Current deliverables
└── archive/                 Old versions worth keeping
```

## The English tree and maintenance tools

The `en/` folder mirrors the Vietnamese files at the root: the assistant files (`AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, `PROJECT.md`), the `.agent/` notes, all fourteen skills with their references, templates and
script, the folder READMEs and this README. File and folder names are the same in both trees, so
`python tools/init_project.py --lang en` simply overlays `en/` onto the root (except
`en/PROJECT_INSTRUCTIONS_SNIPPET.md`, which you paste into the Project instructions). Keep the `en/` folder
in place: the English `CLAUDE.md`, `GEMINI.md` and `AGENTS.md` refer to `en/PROJECT_INSTRUCTIONS_SNIPPET.md`.

The English handbook is in `docs/en/` and `START_HERE.en.html`.

`tools/build_guides_html.py` rebuilds the HTML pages (both languages) from Markdown when you edit the guides
in `docs/` or `docs/en/` (see `tools/README.md`). It is not needed in everyday office work.
When you change a rule in one language, change it in the other too; `tools/check_package.py` compares their structure.

## Using it with an assistant

Open the project folder or grant access to it in the app you use. When the assistant does not yet
know the workspace, you can say:

> This folder uses Local Assistant Workspace. Refer to AGENTS.md and the relevant context in
> PROJECT.md. Use STATE if continuing unfinished work. Choose the tools and skills that best
> fit the request; work directly when there is enough information.

An adapter file name does not guarantee that every app loads it automatically. `skills/local/shared/` is a
file library for the assistant to consult; the package does not install these skills into the native catalog
of Claude, Codex or Antigravity. It does not change any app's global configuration.

## Quick try, upgrading and extending

- Try it in 10 minutes with sample data: `examples/demo-project/README.md`.
- Feedback after use: `docs/FEEDBACK_FORM_VI_EN.md` (a mostly tick-box form) or GitHub Issues.
- A newer package version exists: `python tools/upgrade_package.py` (three-way comparison, never overwrites your work; see `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md`).
- Knowledge specific to one domain: a domain pack in `packs/`, installed with `python tools/pack.py add <name>`.
- Before handing over a deliverable: `python tools/check_output.py <file>` and the checklist in `office-documents`.

## License

MIT, see `LICENSE`. The guides, skills and templates are under the same license.

## Keeping it light in use

Consult only the sources and skills that help. Update STATE only when the next session needs to know something.
Keep the original documents; do not reorganize folders or create extra products beyond the request.
A standard copy in a local project does not mean all AI processing happens offline.

For a project already in use, keep its STATE, sources, skills and own guides; compare same-named
files when upgrading, and do not overwrite everything with the new template.
