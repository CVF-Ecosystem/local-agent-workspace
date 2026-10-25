# Sources and scope of authoring

## Foundation

Package version 1.6 was written from a workspace skeleton the user supplied earlier. It lightens the guides
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

## Skills drawn from practical experience (version 1.4.0)

`excel-workbooks`, `excel-html-viewer` and the five references in `office-documents` (`report-writing`, `procedure-document`, `proposal-review`, `form-standardization`,
`word-technical-notes`), plus the meeting-minutes and basis-order additions in `vn-admin-documents`, were drawn from the maintainer's practical experience on office projects.
Nothing was copied from an outside repo. Unit names, job titles, signatories, pay cut-offs, private legal bases and specific workbook layouts were removed; those stay in each project's own skill.
Not imported: skills tied to one unit, one person or one specific case.

## Additions from practical experience (version 1.5.0)

The presentation standard in `html-reports` (and both HTML templates restyled to it), the many-files / many-periods / cross-checking parts of `excel-html-viewer`,
and the shared-tool and direct-XML-editing parts of `excel-workbooks` were drawn from two of the maintainer's office projects (a ship-operations report and an
engineering-equipment control board), October 2026. Unit names, signatories, figures and business rules were removed; those stay in each project's own skill. Nothing was copied from an outside repo.

## Additions in 1.6.0

- `vn-admin-documents` 1.1 (`references/nd30-presentation.md`, three new frames in `document-frames.md`): the layout values,
  the size and style table for each component and the list of templates in the annex were checked by the maintainer directly
  against a scan of Decree 30/2020/ND-CP (Annex I) on 2026-10-12. The idea of adding decision, plan and invitation frames came
  from the template set of the `xu-ly-van-phong` version 2.0 skill (by Nguyễn Duy Tùng); the frames were rewritten from the decree's
  templates, not copied from that skill. The check found points where that set departs from the decree (3 pt paragraph
  spacing below the 6 pt minimum; a 1.25 cm first-line indent instead of 1 cm or 1.27 cm; the size of "Nơi nhận"), so its
  values were not used.
- `office-documents` 1.1 (`references/docx-default-layout.md`): a default Word layout, a table for turning raw content into a
  document, a counting command after building. Ideas from `xu-ly-van-phong` version 2.0 (default layout, content analysis, checks
  after generating); values adjusted to fall within Decree 30/2020/ND-CP and rewritten in the package's own words.
- `html-reports` 1.2 (how to propose colours when the unit has none, an idea from the colour-preset library of
  `xu-ly-van-phong` version 2.0) and `excel-html-viewer` 1.2 (IndexedDB for large data, normalising document numbers when
  de-duplicating, drawn from the user's own HTML tool for managing legal documents).
- Pack `phap-ly` 0.1.0: rewritten from ideas in the `tu-van-phap-luat` version 1.0 skill (Nguyễn Duy Tùng): 5 axes to frame the
  issue, a verbatim basis table with exact coordinates, three-way cross-checking, conflict rules, a stop condition. Not
  imported: creating a folder and log files for every question (against the rule of creating files only when asked), tool
  names of another app, the per-domain document lists (each number could not be verified), and the original's sample basis
  table (it cites the wrong article of the Labour Code).
- Four new domain packs (0.1.0): `van-thu-luu-tru` (registers and file lists checked directly against a scan of Decree
  30/2020/ND-CP), `cang-logistics` (calculation rules drawn from real work at a container operations team, private details
  removed), `hanh-chinh-nhan-su`, `ke-toan-noi-bo`. The legal basis was looked up on 2026-10-12 on Thu Vien Phap Luat,
  LuatVietnam, government news sites and advisory firms (the source is on each row of `legal-basis.md`); figures taken from
  summaries are marked as such and unverified rows say `[cần xác nhận]`.

- `xu-ly-van-phong-cli` version 1.0 was not imported (a Windows-only executable, overlapping existing tools).

- Source library (`source-library`, `tools/library.py`): the Excel index idea came from a systematisation file of civil judgment enforcement documents 2000-2026 that the user sent as a sample (full texts not downloaded). The package does not copy that file's data; the columns were redesigned for all source types (legal, internal rules, templates), adding verification level, full text, status check date and sensitivity. The six rows in the Example sheet only illustrate how to fill it in; the statuses shown there must be rechecked before use.

## What was not imported into the ZIP

The lieflat-charts LICENSE file states the **PolyForm Noncommercial License 1.0.0**. The package
includes none of that library's templates or code; the HTML templates of `html-reports` and `data-charts`
were newly written. This is a packaging choice, not a legal conclusion about any particular use.

No native formatting skills, global rules, SOUL, installers, hooks, plugins, fonts or dependencies from the
repo were copied. The new templates are not presented as Lieflat/Moxt products. The source paths are only
there for users to open when they want to compare; the bundled HTML files do not access these addresses
when opened or filtered.

## Limits of checking

Version 1.6 was checked for files, internal paths, skill metadata (name matching folder and index),
HTML pages rebuilt from Markdown (the Vietnamese and English sets, with two-way language links) and the
`basic-charts.html` template in a local Chromium browser (no console errors, no network requests, no
horizontal scrolling at phone width). The English translation was written by an agent and has not been
reviewed by a native speaker. The script `check_spreadsheet.py` was run on self-made sample files (xlsx and csv), not on real data. The new skills have not been
run in Claude Desktop, Codex Desktop or Antigravity, no token savings or loop reduction were measured, and
native compatibility on every version is not certified.

## Selected post-RC4 additions — 24 October 2026

The descriptions and activation scopes of the existing 14 skills were edited while preserving their business guidance.
The two Word skills gained optional checks/helpers. The source is the user-provided local working copy after RC4;
the original renderer before selection has SHA-256: c5b9c2f77b770596ec3296467660464f8f110b5119a15c43909cd1132c9d6020. It was read and adapted; downloaders, credentials, host configuration and three private skills were not imported.

Classification: **SUPPLEMENT**, adding business presentation settings/checks to native tools or the organisation's template.
This does not replace native tools or claim superiority over them.

| Intake condition | Outcome within the accepted scope |
|---|---|
| Need and added value | XML layout checks and paragraph/table helpers supplement the existing tools; routing distinguishes small edits from business documents. |
| Provenance | Local working copy dated 24 October 2026, selectively adapted and reviewed in the source repository; no private data or new licence imposed on user sources. |
| Authority and safety | The user authorised the source update; no network/install; outputs use exclusive creation by default and known unsupported structures refuse before writing. |
| Demonstrated effect | Synthetic positive/negative/out-of-scope cases, existing-output protection and missing dependencies were exercised; visual Word, current law and superiority over native tools were not tested. |
| Usability | DOCX checking uses stdlib; the generic python-docx helper works after export. ND30/renderer routes require LAW, with beautifulsoup4 additionally needed by the renderer; nothing installs itself. |
| Reuse | The shared text/table scope and source rules remain; no new skill ID, product grant or native registration was added. |

Conclusion: **ROOT_ELIGIBLE within this scope**, with the user's source-update authority. The existing 14 AVAILABLE statuses remain;
this grants no authority to a new project and proves no host auto-loading. Images, nested tables and unsupported structure need another tool.
Checks cover the final section and dominant font/size; PASS certifies neither full format/legal compliance nor visual rendering.

The local skill_regression grader version was not accepted: quotation/context checks, missing scenarios and Excel recalculation status
were not strong enough to serve as a reliable gate. Word checks/tests were accepted separately. Real AI-host routing and real users remain untested.
Installer host mappings, TVPL/ttport integrations, private skills and Excel-XML editing scripts were not accepted in this intake.
