---
name: office-documents
description: >-
  Draft or edit Vietnamese business documents from sources and templates: procedures/SOPs,
  forms, internal guidance or structured reports, as Word files or text. Use when content
  needs structure around its readers and tasks; short edits can be done directly. For
  administrative format, consider vn-admin-documents. Triggers when the user says: “draft
  a procedure”, “SOP”, “form”, “internal guidance”, “adjust the document to the template”.
metadata:
  version: "1.2"
---

# Business documents

Adds ways to organise content and reference templates; it does not replace the ability to read
documents or to create DOCX/PDF/Excel that you already have. Stay flexible with the real purpose and sources.

## Suggested approach

Start from the document/template the user names and the part to be done. Use what is already known
about the reader, purpose and output; clarify only the gaps that affect the result. If the sources are
already enough, draft right away instead of opening a new round of gathering requirements.

For a procedure, help the performer understand who does what, when, with which inputs/outputs. Add
exceptions or handover points when the source states them or the work needs them. For a form, favour
the fields that serve actual recording and use. For an internal update, put the key information and
what the reader must do first.

When editing a document, keep what is settled and change only the scope given. Distinguish the basis
in the source, confirmed decisions and what is only proposed. Do not invent deadlines, roles,
conditions or authority to fill gaps.

A short update that the reader takes in within a minute (weekly report, announcement, FAQ, incident)
belongs to `internal-comms`. Use this skill when the document has many sections, needs structure or
will become a lasting procedure/form.

## Templates when needed

Choose a fitting template or the project's own; there is no need to open them all:

- `references/procedure-template.md`: a suggested frame for an SOP/procedure.
- `references/form-template.md`: a recording, request or handling slip.
- `references/internal-update-template.md`: an update on progress, problems and decisions needed.
- `references/delivery-checklist.md`: a short pre-delivery checklist (with `tools/check_output.py` for the mechanical part).
- `references/report-writing.md`: style and outlines for periodic reports, investment proposals, letters and submissions.
- `references/procedure-document.md`: a procedure document with a department organisation chart (document code, sign-off, table of contents).
- `references/proposal-review.md`: reviewing and revising an existing proposal or internal regulation.
- `references/form-standardization.md`: standardising old forms and documents in bulk.
- `references/word-technical-notes.md`: technical notes for building or editing Word files.
- `references/docx-default-layout.md`: the default Word layout when there is no template (within the ranges of Decree 30/2020/ND-CP), turning raw content into a document, a counting command to run after building.
- Tracking workbooks, data-entry forms and calculation appendices in Excel: `excel-workbooks`; an HTML tool that reads Excel files: `excel-html-viewer`.

The frames use blanks and contain no approved policy. You may drop, change or combine sections as
asked; do not make the document longer just to fill the frame.

## Keeping content intact when converting or editing in place

When the user asks to "keep the content" (turn prose into a table, change a template, standardise formatting, edit in place), do all three:

1. **Count before**: record the number of images, tables, text characters and steps/sections/rows in the source file. For Word you can use:
   `python -c "import zipfile,re,sys;z=zipfile.ZipFile(sys.argv[1]);x=z.read('word/document.xml').decode('utf8');print('anh',len([n for n in z.namelist() if n.startswith('word/media/')]),'bang',x.count('<w:tbl>'),'ky_tu',len(re.sub(r'<[^>]+>','',x)))" file.docx`
2. **Count after** on the new file the same way. If images or tables differ, or characters differ by more than about 10%, find the cause: if something was lost, rebuild it from the source (copy back the images, tables, notes); do not hand it over.
3. **State in the hand-over** a "before → after" table (images, tables, characters, steps) and say which parts were removed on purpose. Counting steps only inside the extracted part does not prove nothing was lost; count on the whole source file.

Rebuilding a file by copying only the text easily drops images, nested tables, headers/footers and notes; prefer editing a copy of the source file directly.

## Suitable output

A draft request gets a draft; a request for a usable file gets a suitable formatting tool and a look at
the points needed for use. Check the exact part of the source when important content depends on it. No
reader-testing with another agent or multi-option brainstorming is needed if the task does not need it.

When the content fits the scope, the reader can use it and the gaps are stated, stop. Do not add an
explanatory note, a comparison or a round of style editing on your own.

## Supplementary Word tools

Use native tools or the unit's template when suitable. Optional `scripts/docx_helpers.py` uses
`python-docx` for paragraphs/tables and can be copied or exported with the skill. `new_document()`
works independently. `new_nd30_document()` is LAW-workspace-only and requires `tools/vn_legal_docx.py`;
for standalone export, use native tools/a verified template. The generic helper does not provide
all ND30 settings.

Inside LAW, `python tools/vn_legal_docx.py INPUT.html OUTPUT.docx` converts supported HTML text and
simple tables with the local administrative template. Optional dependencies are `beautifulsoup4`
and `python-docx`; nothing is installed automatically. Images, nested tables, automatically numbered
lists, unsupported structure and invalid/oversized spans refuse before writing. This is not a way
to preserve every structure of an existing document. Existing output is refused by default;
`--overwrite` requires the user's permission. No inferred document type/issuer is added to metadata.

Before delivery run `python tools/check_output.py FILE.docx`: text checks use stdlib; `auto` applies
A4/margins/font/size only when the national title is present, `nd30` forces those checks, `none` skips
layout checks. Final-section dimensions/margins, dominant font/size with style inheritance, suspicious
line breaks/duplicate text and page-number warnings on long files are mechanical checks only.
Other sections, per-paragraph spacing/alignment, images, comments, tracked changes and visual rendering
are not verified. Resolve findings and open/render the result; PASS does not certify legal compliance,
current validity or visual quality. See `references/word-technical-notes.md`.
