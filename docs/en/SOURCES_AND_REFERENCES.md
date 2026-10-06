# Sources and scope of authoring

## Foundation

Package version v1.1 was written from a workspace skeleton the user supplied earlier. It lightens the guides
and adds the office resources that were agreed.
The user's original files were not relabelled under a new blanket licence.

## Repo reviewed

Repo: https://github.com/sharkrebel/everything-everywhere-for-antigravity

Reference version: `68a4398e3dd32c83831bc4720024ed95a91c6757`, dated 02/10/2026.
Package authoring date: 06/10/2026. This is a content reference, not a claim that the repo
or every native skill was run on Claude/Codex/Antigravity.

| Component | Reference idea | How it is used in the package |
|---|---|---|
| How to write skills | skill-creator | Short guidance, load only the needed resources, keep the agent's judgment. |
| office-documents | doc-coauthoring, internal-comms (ideas about organising content) | Newly written in Vietnamese, adding SOP/form/update frames; the multi-round process was not copied. |
| html-reports | lieflat-charts and report-catalog | Took the single-file report need and choosing a template by content; the two HTML templates were written independently, with no code or layout from R04/R09/R12. |
| data-charts | lieflat-charts | Rewrote the rules for choosing and presenting charts; the offline SVG template was newly written. |
| internal-comms | internal-comms | Rewritten in Vietnamese, adding announcements and incident reports. |
| doc-coauthoring | doc-coauthoring | Rewritten with a limit on the number of rounds; used only when the user wants it. |
| vietnamese-editing | humanizer | Newly written for Vietnamese; the reference on formulaic-writing signs was written for Vietnamese, without copying the English list or punctuation rules. |
| HTML guides | The package's own Markdown guides | A presentation built from Markdown, inline CSS/JS, no theme, fonts or external scripts. |

## Source files for comparison

- skill-creator: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/skill-creator/SKILL.md
- doc-coauthoring: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/doc-coauthoring/SKILL.md
- internal-comms: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/internal-comms/SKILL.md
- humanizer: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/humanizer/SKILL.md
- lieflat-charts: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/lieflat-charts/SKILL.md
- Report catalogue: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/lieflat-charts/report-catalog.md
- Lieflat licence: https://github.com/sharkrebel/everything-everywhere-for-antigravity/blob/68a4398e3dd32c83831bc4720024ed95a91c6757/skills/lieflat-charts/LICENSE

## The four skills chosen from the repo and how they were rewritten

The four skills below were proposed by an agent after auditing the repo and were read directly at the
same commit `68a4398e`. The package did not import the originals: each original was heavy or did not
fit the goals (office work, Vietnamese, limiting agent loops, opening offline), so each was rewritten as
a short Vietnamese skill that keeps the useful ideas.

| Original skill | Observations | Version in the package |
|---|---|---|
| lieflat-charts | `SKILL.md` ~38 KB in Chinese; over 120 files (~20 MB); many mandatory rules; 31 HTML templates that need the network (CDN, fonts). Worth keeping: choosing charts by data shape, presentation rules, a pre-delivery checklist, no 3D. | `data-charts`: rewritten rules and chart selection; the template `basic-charts.html` is newly written in plain SVG, offline. |
| internal-comms | Small; examples follow one company's internal formats (3P, newsletter, FAQ). Worth keeping: Progress - Plans - Problems, readable in 30–60 seconds. | `internal-comms`: Vietnamese; adds announcements and incident reports; drops the automatic gathering from chat channels because it is not available in this environment. |
| doc-coauthoring | ~16 KB; three multi-round stages, including reader testing with a sub-agent. Worth keeping: gather context, settle the outline, draft section by section, final review. | `doc-coauthoring`: four steps, each with a round limit; only used when the user wants it; reader testing is optional and uses no sub-agent. |
| humanizer | ~31 KB; 35 patterns of AI-writing signs in English; many review passes. Worth keeping: do not add facts, keep the writer's voice, a "not an error" list. | Merged into `vietnamese-editing` as `references/machine-style-signs.md`: Vietnamese signs, a single editing pass. |

The five other skills (document-comparison, spreadsheet-check, meeting-minutes, process-mapping,
vn-admin-documents) were newly written from work needs and not copied from the repo. `vn-admin-documents` takes
the records-management rules (Decree 30/2020/ND-CP) as a reference only; it is a format suggestion, not legal
advice, and the rules may have been amended. `skills/external/` is still empty; if you
import an outside skill later, record the source, commit and licence following the guidance in that folder.

## What was not imported into the ZIP

The lieflat-charts LICENSE file states the **PolyForm Noncommercial License 1.0.0**. The package
includes none of that library's templates or code; the HTML templates of `html-reports` and `data-charts`
were newly written. This is a packaging choice, not a legal conclusion about any particular use.

No native formatting skills, global rules, SOUL, installers, hooks, plugins, fonts or dependencies from the
repo were copied. The new templates are not presented as Lieflat/Moxt products. The source paths are only
there for users to open when they want to compare; the bundled HTML files do not access these addresses
when opened or filtered.

## Limits of checking

Version v1.1 was checked for files, internal paths, skill metadata (name matching folder and index),
HTML pages rebuilt from Markdown (the Vietnamese and English sets, with two-way language links) and the
`basic-charts.html` template in a local Chromium browser (no console errors, no network requests, no
horizontal scrolling at phone width). The English translation was written by an agent and has not been
reviewed by a native speaker. The script `check_spreadsheet.py` was run on self-made sample files (xlsx and csv), not on real data. The new skills have not been
run in Claude Desktop, Codex Desktop or Antigravity, no token savings or loop reduction were measured, and
native compatibility on every version is not certified.
