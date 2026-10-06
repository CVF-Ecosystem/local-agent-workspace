# Local Agent Workspace v1.3

A local workspace for office work with Claude, Codex, Gemini or another agent.

**Open `START_HERE.en.html` to read the handbook in English (or `START_HERE.html` for the Vietnamese version; every page has a language switch button).** The page opens directly
in a browser, with no installation, server, online font or network connection.

## What is it for?

A starter folder for every office-work project you do with an AI assistant, built to one standard. It helps the AI remember the
context between sessions (no explaining again), keeps files tidy and sets clear working rules (no invented figures, no
overwriting originals), with eleven skills for common tasks; unzip it on any computer and get the same standard. The full
introduction is at the top of `START_HERE.en.html`.

Reading documents, drafting procedures, forms and reports; handling spreadsheets when needed; continuing
work across sessions; producing lightweight HTML reports. The workspace holds the documents and the project
context, and the agent picks the way of working that fits the request.

The guides are working suggestions, not a mandatory process for every task. Small jobs can be done directly;
jobs that need a source or a template open only the useful part. This is not an application, an agent
framework or a software development kit.

## Getting started

Unzip the whole ZIP, rename the folder to the project name, then open `START_HERE.en.html`. Do not work
directly inside the ZIP. The easiest way: double-click `SETUP.bat` (Windows) or `SETUP.command` (macOS); the wizard asks a few questions, then initializes the project and fills in `PROJECT.md`. Or use the command (once, needs Python 3.8+; nothing else to install):

```text
python tools/init_project.py --name "Project name" --lang en
```

`--lang vi` keeps the Vietnamese version of the files. Without Python, follow
`docs/en/NEW_PROJECT_GUIDE.md` by hand. The package version is in `VERSION`.

- New project: `docs/en/NEW_PROJECT_GUIDE.md` or the `.html` file of the same name.
- Existing project and package upgrade: `docs/en/EXISTING_PROJECT_UPGRADE_GUIDE.md` or `.html`.
- Daily use: `docs/en/DAILY_USE_GUIDE.md` or `.html`.
- Choosing and using skills: `docs/en/SKILLS_GUIDE.md` or `.html`.

The Markdown and HTML versions have the same guide content. The agent can read Markdown and
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

The eleven skills are in `skills/local/shared/` and are recorded as `AVAILABLE` in
`.agent/SKILL_INDEX.md`. The agent chooses a skill by fit, with no fixed preference for
native or local. Not using a skill is also a valid choice.

The HTML templates were written specifically for the package, with clearly labeled illustrative data.
No upstream template, script, font or skill was copied as a whole.
Sources of ideas and the scope of what was consulted are in `docs/en/SOURCES_AND_REFERENCES.md`.

## Files worth knowing

```text
project/
├── START_HERE.html          Guide for users (Vietnamese)
├── START_HERE.en.html       Guide for users (English)
├── SETUP.bat / SETUP.command  Double-click to set up the project (the wizard runs by itself)
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
├── examples/demo-project/   Demo project (fake data) to try in 10 minutes
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

The `en/` folder mirrors the Vietnamese files at the root: the agent files (`AGENTS.md`, `CLAUDE.md`,
`GEMINI.md`, `PROJECT.md`), the `.agent/` notes, all eleven skills with their references, templates and
script, the folder READMEs and this README. File and folder names are the same in both trees, so
`python tools/init_project.py --lang en` simply overlays `en/` onto the root (except
`en/PROJECT_INSTRUCTIONS_SNIPPET.md`, which you paste into the Project instructions). Keep the `en/` folder
in place: the English `CLAUDE.md`, `GEMINI.md` and `AGENTS.md` refer to `en/PROJECT_INSTRUCTIONS_SNIPPET.md`.

The English handbook is in `docs/en/` and `START_HERE.en.html`.

`tools/build_guides_html.py` rebuilds the HTML pages (both languages) from Markdown when you edit the guides
in `docs/` or `docs/en/` (see `tools/README.md`). It is not needed in everyday office work.
When you change a rule in one language, change it in the other too; `tools/check_package.py` compares their structure.

## Using it with an agent

Open the project folder or grant access to it in the app you use. When the agent does not yet
know the workspace, you can say:

> This folder uses Local Agent Workspace. Refer to AGENTS.md and the relevant context in
> PROJECT.md. Use STATE if continuing unfinished work. Choose the tools and skills that best
> fit the request; work directly when there is enough information.

An adapter file name does not guarantee that every app loads it automatically. `skills/local/shared/` is a
file library for the agent to consult; the package does not install these skills into the native catalog
of Claude, Codex or Antigravity. It does not change any app's global configuration.

## Quick try, upgrading and extending

- Try it in 10 minutes with fake data: `examples/demo-project/README.md`.
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
