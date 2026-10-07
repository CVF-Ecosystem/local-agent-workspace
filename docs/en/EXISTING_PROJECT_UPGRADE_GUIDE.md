# Use with an existing project and upgrade the package

Keep the structure that already works. Add the useful parts first; reorganise only when it truly
helps. You do not need to create a new project in the application just to use this folder set.

## 1. Keep a copy before changing anything

Back up the folder or the files you will edit. Identify the instruction files, state, outputs
and skills in use so you do not lose what is specific to the project.

You do not need Git or coding tools for this; a copy of the folder is enough for comparing and
going back when needed.

## 2. Add selectively; do not overwrite everything

Unzip the package version you want into a separate folder to compare. When files share a name, merge the useful parts
instead of accepting a blanket overwrite.

| What the project already has | Suggested handling |
|---|---|
| `AGENTS.md`, `PROJECT.md` | Keep your own context and instructions; replace the old shared text only where it fits. |
| `CLAUDE.md`, `GEMINI.md` | Keep provider-specific parts; the adapter only points to the shared guide. |
| `.agent/STATE.md`, `HANDOFF.md` | Keep the real state; do not replace it with the empty template from the ZIP. |
| `INDEX.md`, `SKILL_INDEX.md` | Keep existing entries and add the new ones; do not create duplicate rows. |
| `skills/`, sources, output | Keep current resources as they are; do not move them just to match the sample tree. |
| `README.md`, `docs/`, `START_HERE.html` | Keep your own content; add the guides in a suitable place and keep internal links working. |

If you move the package folder or the guides, ask the agent to update the related paths; you do
not need to force an old project into the new folder tree.

The first time you bring the package into an existing project (no `VERSION` or `.agent/` yet), use the tool instead of copying by hand: from the package
folder run `python tools/adopt_project.py --project "path" --name "Project name"` for a report, add `--apply` to write. It only adds missing files; an old
`AGENTS.md`, `CLAUDE.md` or `GEMINI.md` that differs from the package version is saved as `<name>.bak-<date>` (merge its project-specific parts into `PROJECT.md`);
any other conflicting file stays yours and the package version is saved as `<name>.new`; existing project skills get a row in `SKILL_INDEX.md`.
Shared skills live in `skills/local/shared/`; skills with an organisation's own details live in `skills/local/project/`; do not copy shared content into a project skill.

## 3. Upgrade to a newer package version

Each project records the package version it uses in `.agent/PACKAGE_INFO.json` (created by
`tools/init_project.py`; for an existing project without it, create it by hand with `"version"` set to the
version you used). The package version is in the `VERSION` file; `CHANGELOG.md` says what changed between versions.

The quick and safe way is the upgrade tool. It compares three sides (the old original, the project's current file, the new version),
reports first and writes only when you add `--apply`.

- Step 1: Unzip the new version into a separate folder; read `CHANGELOG.md` from your version to the new one.
- Step 2: From the new version's folder run `python tools/upgrade_package.py --project "path of the old project"` to see the report.
   Files nobody edited are updated, new files are added, and files you edited are kept.
- Step 3: If the report looks right, run it again with `--apply`. A file that you edited and the package also changed is not
   overwritten: the new version is saved as `<name>.new` for you to merge, then delete the `.new` file. Your own files (`PROJECT.md`,
   STATE, HANDOFF, INDEX, `SKILL_INDEX.md`, `references/`, `working/`, `output/`, `archive/`, project skills) are never touched.
- Step 4: Run `python tools/check_package.py --verify` and open a trial session. If you use domain packs, run
   `python tools/pack.py list` to see which have a newer version (`pack.py update <name> --apply`).

A project without `MANIFEST.sha256` (made before this version) cannot be compared safely: upgrade by hand, copying selectively the
package files you have not edited. The tool deletes nothing; files no longer in the new package are only listed for you to decide.

Do not replace the project's real STATE, HANDOFF,
sources and outputs with the sample files of the new version.

## 4. Slim down old context when useful

Stable content about purpose, readers, templates and limits can stay in PROJECT. Current state
goes in STATE; handover goes in HANDOFF; sources go in the index or stay where they are. You do
not need to re-split all documents in one go.

If there is a long log, put only the current state and confirmed decisions into STATE. Keep the
original history for reference when needed, and do not load all of it into every session.

## 5. Keep the sources and skills that already work

INDEX can point to sources at their current location. There is no need to move the whole
library into `references/`.

Native skills that already exist do not need to be copied into the package. Self-built and
external skills can stay where they are; just record where to find them and when they are
useful. For a newly added skill, read enough to record its purpose, origin, dependencies and
notable points; do not redo the import every time it is used.

If you copy resources from outside, keep the source and the terms of the part you imported.
When you only write something new from a reference idea, say so instead of calling it an upstream
copy.

## 6. Connect to the current working session

Keep the existing project in the application. Grant folder access using whatever the application
supports; do not treat a block of instructions as having created file access.

You can use a short opening:

```text
This project uses a local folder to keep documents and working context.
Refer to AGENTS.md and PROJECT.md when needed; use STATE to continue unfinished work.
Choose sources, tools and skills that fit, including native skills already available.
Keep decisions already made and only do the part I assign.
```

With Gemini through Antigravity, do not assume `GEMINI.md` is loaded the way Gemini CLI loads it.
With any agent, you can ask it to open `AGENTS.md` directly when the instructions have not been loaded.
Do not edit global configuration files or replace a provider's whole skill library.

## 7. Try one session and adjust the right place

Open a new session and give it a small piece of work you actually need. To check that it can
continue, you can ask:

```text
Based on STATE and HANDOFF if present, tell me briefly what is in progress and the next step.
Then do [specific task]. No need to read unrelated sources.
```

Watch whether it uses the right sources, keeps earlier decisions and finishes within scope. An
agent that knows the file or skill can open it directly, without proving it went through every
index. If the new guidance makes things cumbersome, change or remove exactly the passage that
causes the noise.

## 8. Go back when needed

Use the copy you kept to restore any part that does not fit. You can keep only one skill or one
useful HTML guide set; you do not need to upgrade everything at once. Do not delete state or new
documents created during the trial without reviewing them.
