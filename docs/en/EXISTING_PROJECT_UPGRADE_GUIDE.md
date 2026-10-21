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
| `AGENTS.md`, `PROJECT.md` | Keep your own context and instructions, including any source-folder exception and sub-agent scope you recorded; replace the old shared text only where it fits. |
| `CLAUDE.md`, `GEMINI.md` | Keep provider-specific parts; the adapter only points to the shared guide. |
| `.agent/STATE.md`, `HANDOFF.md` | Keep the real state; do not replace it with the empty template from the ZIP. |
| `INDEX.md`, `SKILL_INDEX.md` | Keep existing entries and add the new ones; do not create duplicate rows. |
| `.agent/EXECUTION_PROFILE.json` | If present, keep it byte for byte and create no `.new`. If absent, the tools create it only when `PROJECT.md` has exactly one sub-agent scope line; an old prose line is never turned into a grant and needs an explicit migration (`tools/execution_profile.py`). Missing scope line or lost profile: see “Sub-agent profile” in section 3. |
| `skills/`, sources, output | Keep current resources as they are; do not move them just to match the sample tree. |
| `README.md`, `docs/`, `START_HERE.html` | Keep your own content; add the guides in a suitable place and keep internal links working. |

If you move the package folder or the guides, ask the assistant to update the related paths; you do
not need to force an old project into the new folder tree.

The first time you bring the package into an existing project (no `VERSION` or `.agent/` yet), use the tool instead of copying by hand: from the package
folder run `python tools/adopt_project.py --project "path" --name "Project name"` for a report, add `--apply` to write. It only adds missing files; an old
`AGENTS.md`, `CLAUDE.md` or `GEMINI.md` is preserved and remains active; the differing package version is saved as `<name>.new` to merge, including when selecting English.
If a differing `.new` already exists, the tool stops before writing. Unmerged instructions are explicitly reported as “MERGE REQUIRED”;
any other conflicting file stays yours and the package version is saved as `<name>.new`; existing project skills get a row in `SKILL_INDEX.md` with Status `REVIEW` (the assistant can still use them in the project; confirm, then change it to `AVAILABLE`). See section 3 for handling `.new` files. If this step is interrupted, see section 9.
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
   overwritten: the new version is saved as `<name>.new` for you to review and decide on; what you can do depends on the kind of file
   (see "Handling `.new` files" just below). Your own files (`PROJECT.md`, STATE, HANDOFF, INDEX, `references/`, `working/`, `output/`, `archive/`, project skills) are not replaced with package templates. Existing skill-index rows are kept; the tool may add missing shared-skill rows and record the upgrade in `PACKAGE_INFO.json`.
- Step 4: Run `python tools/check_package.py --verify` and open a trial session. If you use domain packs, run
   `python tools/pack.py list` to see which have a newer version (`pack.py update <name> --apply`).

**Handling .new files.** `<name>.new` is the package's version, left next to your file. It may be out of date, or someone may have edited it by hand; do not assume it is the latest.
The "Pending merges" page of the control panel lists these files; "Compare" does not change either file, but the action may be recorded in the operations history. What you can do depends on the kind of file:

- **The eight guides under the docs folder** (the four `HUONG_DAN_*_VI.md` files and the four in `docs/en/`: `NEW_PROJECT_GUIDE`, `DAILY_USE_GUIDE`, `SKILLS_GUIDE`, `EXISTING_PROJECT_UPGRADE_GUIDE`):
  "Use the new copy (keep .new)" stores your file in `.agent/merge-backups/<id>/` and then replaces it with the new copy; the `.new` file stays pending.
  "Save .new and end the pending item" keeps your file as it is, stores both copies in `.agent/merge-backups/<id>/` and moves the `.new` out of the pending list.
  "Keep mine" only closes the window, writes nothing and the `.new` stays pending. Every option that writes shows a preview and waits for your confirmation. If you edit the file yourself, preview again before ending the item.
- **Instruction files for the AI assistant** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and the same-named files in `en/`): there is no "Use the new copy". Storing the `.new` is done with the "Keep current, store .new" button on the file's own row.
  It does not put the new text into the file in use and grants the AI assistant no extra permission. To use the new text, edit the current file yourself and preview again.
  An empty pending list does not mean no assistant will read the `.new` or the stored copy, and it does not mean the instructions have been re-checked.
- **Two package scripts** (`tools/audit_scripts.py` and `skills/local/shared/spreadsheet-check/scripts/check_spreadsheet.py`): there is no "Use the new copy". Storing the `.new` is done with the "Keep current, store .new" button on the file's own row, and only when the file is listed in the project's `MANIFEST.sha256`.
  The tool stores the `.new` as text only: it does not open, compile or run the script, and it does not put the new text into the script in use. An empty pending list does not mean the script is correct, safe, runnable, accepted or allowed to be used.
  To use the new text, edit the current script yourself and check it under your own script rules. These are the only two files; no other script is inferred from its folder or from how often it is used.
- **Other toolkit files** (other scripts in `tools/`, for example `tools/check_output.py`; shared skills and other package files): the panel only compares and copies the path; there is no button to replace or end these, and the tool does not merge them. There is one manual route that keeps both copies, described step by step just below this list. There is no accepted way to end this group officially. Do not treat the whole `skills/` folder as yours alone; a shared skill you added yourself is only kept as it is, and its long-term management has not been verified.
- **The .cvf folder and the core tool files** (listed below): incompatible, missing or changed machine/core files, or conflicting `.cvf` documentation, stop the tool at preview without creating `.new`. If `.cvf` is absent or the existing version is compatible, the upgrade may proceed; there is no automatic schema migration.
- **Installed domain packs**: preview with `python tools/pack.py update <name>` and add `--apply` to update. On conflict, your edited file is kept and the incoming pack version is saved as `.new`; the control panel has no button to end these pending items.

**Setting a .new of another file aside by hand, keeping both copies.** This is not an "official finish": it does not change `MANIFEST.sha256`, does not make the panel record the item as handled, and is not evidence that the file was checked or accepted. Example with `tools/check_output.py.new`, measured on a fake 1.8.0 project that had been upgraded (Windows, PowerShell; paths use `/`):

- Step 1, compare `tools/check_output.py` (yours) with `tools/check_output.py.new` using a tool you know (an editor, or `fc tools/check_output.py tools/check_output.py.new`). The `.new` may be out of date or hand-edited. Do not run or compile the script to "try it": read it as text only.
- Step 2, create a separate, **new**, numbered folder under `archive/` and copy both versions into it. The command stops if the folder already exists; then change the id, never overwrite:

```powershell
$id = Get-Date -Format yyyyMMdd-HHmmss
$dir = "archive/nang-cap/$id-check_output"
New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null
Copy-Item tools/check_output.py "$dir/check_output.py.hien-hanh" -ErrorAction Stop
Copy-Item tools/check_output.py.new "$dir/check_output.py.new" -ErrorAction Stop
```

- Step 3, check both copies byte for byte: `Get-FileHash` of each original and of its copy must match. If they do not, stop.
- Step 4, choose one explicitly. **Keep yours**: move (do not delete) the `.new` into the folder you just made, then check again. The hash of the moved file must equal the original `.new` hash, and the hash of `tools/check_output.py` must equal what it was before. **Use the new content**: ask the person who owns that file (the toolkit maintainer) to merge it into the current file after comparing, then set the `.new` aside as above. Do not replace the current file with the `.new` before someone has compared and confirmed.

```powershell
Move-Item tools/check_output.py.new "$dir/check_output.py.new.da-chuyen" -ErrorAction Stop
Get-FileHash "$dir/check_output.py.new.da-chuyen", tools/check_output.py
```

- Step 5, to get the `.new` back later, copy it from the archive folder as a **new file**, never over an existing one (`Copy-Item` overwrites an existing file, so check first):

```powershell
if (Test-Path tools/check_output.py.new) { throw 'a .new already exists, not overwriting' }
Copy-Item "$dir/check_output.py.new" tools/check_output.py.new -ErrorAction Stop
```

Measured: the moved file and the copy match byte for byte and `tools/check_output.py` is unchanged; running the upgrade again with the same package reports "Kept (you edited it, the package did not change)" and does not recreate the `.new`; a new `.new` appears only if a later package changes that file again. Do not delete a `.new` to silence the warning or edit `MANIFEST.sha256`.

The writing options on this page have been checked only on Windows 11 with a local drive; "store and move" runs only on Windows and is two steps that can be interrupted half-way. To get an old copy back by hand, open the file in `.agent/merge-backups/<id>/` and save it as a new file; there is no undo button.
Do not delete a `.new` or edit `MANIFEST.sha256` just to get past a check. The next upgrade may keep an old `.new`, or stop when the `.new` differs from the new package version.

The second line of the report tells the "version label" apart from the "package content baseline" (the paths and hashes in the installed `MANIFEST.sha256` compared with the new one), so a "vX -> vX" line is no longer read as "the new package has nothing different".
`SAME_LABEL_DIFFERENT_BASELINE` means the version number did not go up but the package content changed. `SAME_LABEL_SAME_BASELINE` only says the package is unchanged compared with the installed one, not that the project is clean or in sync: the update, add, keep and conflict lists below are still the real work.
`UNKNOWN` means the manifest is missing, damaged, has a duplicate path or is ambiguous, so the baseline cannot be determined; the tool does not infer it from the version label. This is a description only and does not change how the tool decides what to write or keep. The baseline covers the whole manifest, including the English overlay (`en/`), so it can differ even when the active Vietnamese files do not change. `KNOWN` only means readable, unambiguous metadata; it does not establish matching files, safe paths or permission to update.

If the `--apply` run is interrupted (power cut, computer shut down part-way), some files may already have been written. On the next run, the tool reports INCOMPLETE if it detects an unfinished transaction; section 9 explains how to resume or roll back.

A project without `MANIFEST.sha256` (made before this version) cannot be compared safely: upgrade by hand, copying selectively the
package files you have not edited. The upgrade tool deletes nothing (undoing an interrupted run is covered in section 9); files no longer in the new package are only listed for you to decide.

Do not replace the project's real STATE, HANDOFF,
sources and outputs with the sample files of the new version.

The package has a hidden `.cvf` folder (orchestration controls, candidate v3, not active, grants nothing). When adopting or upgrading, the tools only **add** this candidate if the project has no `.cvf`,
or update its documents if the project's `.cvf` already is exactly that version. If the project has a different `.cvf` (an older version, missing files, hand-edited), or a core tool file (`tools/publish_new.py`,
`tools/context_update.py`, `tools/transaction.py`, `tools/result_schema.py`, `tools/current_draft.py`) was edited, the tool stops at the preview, explains why and changes nothing, even with `--apply --force`; there is no automatic migration.
Use the folder unzipped from the release ZIP as the upgrade source (its MANIFEST must match the real files); the maintainers' source folder cannot be used.

**Sub-agent profile (.agent/EXECUTION_PROFILE.json).** Two cases where the tool does not create a profile and stays blocked; each has its own next step:

- *`PROJECT.md` has no sub-agent scope line* (common for projects made with 1.8): the tool does not guess, and an agent adds this line only when you assign that. If you choose to grant no sub-agent scope, add exactly one line to `PROJECT.md`: `- Standing scope for sub-agents: None` (the Vietnamese label `- Phạm vi được giao cho agent phụ: Không có` is accepted too). Then, from the NEW package folder, run `python tools/upgrade_package.py --project "path of the project"` to preview (you should see "Create .agent/EXECUTION_PROFILE.json (authority owner PROJECT, no grants)"), and add `--apply` to write. `PROJECT.md` and `STATE.md` are not overwritten; the new profile has no grants, so it grants no role. Measured on a fake 1.8.0 project: before the line is added, `execution_profile.py status` reports `PROFILE_ABSENT` with these steps; after `--apply`, `status` reports `OK` with `NO_GRANT` for all three roles.
- *`PROJECT.md` points to the profile but the profile file is gone*: stay blocked. Restore **exactly that profile from your own backup** (same bytes) before configuring anything; afterwards `python tools/execution_profile.py status` must return `OK`. With no backup, stay blocked: do not build a sample profile, do not change the `PROJECT.md` line to "None" to get around it (that resets the authority), and do not use `init_project.py --force` (it re-runs initialisation on an existing project). Ask the project owner to confirm how to restore or reset the authority; that is a separate decision, not part of the upgrade step.

An old prose line (for example "the Reviewer may be called for everything") is still never read as authority; it needs an explicit migration (`tools/execution_profile.py`). None of these steps grants any role.

**No downgrade.** Moving a project down to a lower package is not supported: the upgrade tool refuses before writing, including when the source package has no `.cvf` while the project does, and there is no reverse conversion. To go back, restore from your backup (sections 1 and 8). The upgrade tool of the 1.8.0 package itself refuses a 1.9.0 project (measured with no `.new` pending: exit code 1, every byte of the project tree unchanged). That is a `VERSION` label comparison, not a guarantee that every older binary is stopped; the old tool's `--force` switches that very check off (measured on a copy: `--apply --force` succeeded and put `VERSION` and dozens of files back to 1.8.0). So **do not use `--force` to downgrade**. The 1.8.0 tool is already-released bytes and cannot be changed.

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
With any assistant, you can ask it to open `AGENTS.md` directly when the instructions have not been loaded.
Do not edit global configuration files or replace a provider's whole skill library.

## 7. Try one session and adjust the right place

Open a new session and give it a small piece of work you actually need. To check that it can
continue, you can ask:

```text
Based on STATE and HANDOFF if present, tell me briefly what is in progress and the next step.
Then do [specific task]. No need to read unrelated sources.
```

Watch whether it uses the right sources, keeps earlier decisions and finishes within scope. An
assistant that knows the file or skill can open it directly, without proving it went through every
index. If the new guidance makes things cumbersome, change or remove exactly the passage that
causes the noise.

## 8. Go back when needed

Use the copy you kept to restore any part that does not fit. You can keep only one skill or one
useful HTML guide set; you do not need to upgrade everything at once. Do not delete state or new
documents created during the trial without reviewing them.

## 9. When a write is interrupted

The tools write through a journaled transaction: they check first, back up the files that will change, then write each file. If the computer shuts down, loses power or the disk fails part-way, the next run reports **INCOMPLETE** and writes nothing more until you deal with that transaction.

Choose one of two ways:

- Command line, from the project folder: `python tools/transaction.py status` shows the id of the unfinished transaction. Then run `python tools/transaction.py resume <id>` to finish it, or `python tools/transaction.py rollback <id>` to roll it back.
- Control panel: open the "App status" page, section "Unfinished transactions", and press "Resume" or "Roll back". The Overview page also shows a notice when a transaction is unfinished.

Rolling back does the following:

- Files you have not edited since the interruption return to their originals. New files that the interrupted run created are removed if you have not edited them.
- Files you have edited since the interruption are kept and never overwritten. Their originals are in `.agent/runtime/transactions/<id>/backup/`. The transaction then has the status `rollback_partial`: compare the files and restore by hand if needed. This status does not block other work.
- A completed transaction cannot be rolled back, because no backups remain. To get a different result, run the operation again.

If the tool reports **NOTHING WRITTEN**, the operation has not changed its target files; a technical journal may have been created in .agent/runtime/. If in doubt before rolling back, keep a copy of the project folder (section 1).

## 10. Tested platforms and version policy

Tested: Windows 11 with Python 3.11. Not yet tested: macOS; Python 3.8 (the tools are written to run on Python 3.8, but have not been run on 3.8); other operating systems and Python versions. If you hit a problem on an untested platform, report it with the output of `python tools/check_package.py --verify` and a diagnostics bundle from the control panel.

The controlled draft flow (the "Current draft" card, candidate `.cvf` v3) runs only on Windows with a local NTFS drive, using the exact Python that opened the control panel, and needs the `jsonschema` library 4.18 or newer.
Actually run: Windows 11, Python 3.11 with jsonschema 4.23.0. Python 3.13 without jsonschema was only checked to report "not usable" (the card does nothing); the real flow has not been run on 3.13. Not tested: macOS, Python 3.8, network drives or cloud-synced folders.
The tools never install a library or change your Python: if it is missing, install it yourself into the Python or venv this project uses, then reopen the control panel (the "App status" page shows the command for that exact Python). The rest of the workspace does not depend on this.

Version numbers have the form MAJOR.MINOR.PATCH and are stored in the VERSION file:

- MAJOR changes when a change breaks compatibility: the layout of the .agent folder or the project folder, the MANIFEST.sha256 format, the format of tool results, or removing an existing command or flag.
- MINOR changes when new features are added compatibly: tools, skills, flags or new content sections.
- PATCH changes for fixes, documentation or template updates that do not change your project data.

Each version has its own entry in CHANGELOG.md. Read that entry before you upgrade.
