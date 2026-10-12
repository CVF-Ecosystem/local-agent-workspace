---
name: source-library
description: >-
  Suggestions for organising and searching the project's source library in `references/` (legal documents, company rules and
  regulations, internal decisions, templates, source documents) with one Excel index `references/_INDEX.xlsx`: where files go,
  naming, filling the index, checking whether a document is in force, looking it up before quoting. Triggers when the user says
  "document library", "store legal documents", "document index", "company regulations", "which documents are in force", or
  before quoting a legal document or internal regulation.
metadata:
  version: "1.0"
---

# Project source library

Goal: the agent quotes from **a file that really is in the library**, knows whether the document is in force and as of which
date, and knows how well it has been verified. With no file, say so; do not quote from memory.

## Layout

```text
references/
  _INDEX.xlsx              one index for every group (create with: python tools/library.py init)
  README.md                general rules, naming
  legal/<domain>/          external legal documents (group "Pháp luật")
  policies/<area>/         the organisation's rules, regulations, internal decisions (group "Nội bộ")
  templates/<area>/        approved templates (group "Mẫu biểu")
  source-documents/        other source documents (group "Tài liệu nguồn")
```

One shared index, not one per folder: one lookup finds everything and there are no two copies drifting apart. A domain folder
may have a short README (scope, who updates it, official source). An older project with sources elsewhere does not need to
move them: index paths are relative to `references/` and may use `../`; `.agent/INDEX.md` is still used for general sources.

## File names

No accents, no spaces, words joined by hyphens; the description after an underscore.
- Legal: `<year>-<number>-<symbol>_<short-name>.pdf`, for example `2020-30-ND-CP_cong-tac-van-thu.pdf`.
- Internal: `NB_<type>-<short-name>_<yyyy-mm-dd>.pdf`, for example `NB_noi-quy-lao-dong_2025-01-15.pdf`.
- Templates: `MB_<short-name>.<ext>`. A revised version keeps the old one and adds the date to the name; never overwrite.

## The `_INDEX.xlsx` index

Sheets "Danh mục" (the only sheet the tool and the agent read), "Ví dụ" (how to fill it in, not data), "Tổng hợp" (formula
counts), "Danh sách" (drop-down values). Main columns: ID, Group, Domain, Issuer, Number, Type, Issued, Effective, Title,
Replaces, Replaced by (from), Status, **Status checked**, **Verification**, **Full text**, **File path**, Key articles,
**Sensitivity**, Used by, Source URL, Notes.

Verification: "Đã đối chiếu toàn văn" (read the very file in the library) > "Đã xác minh nguồn chính thống" (checked on an
official source) > "Theo bản tóm tắt" (from a summary) > "Cần đối chiếu" (needs checking). Never raise the level without doing that check.

## Before quoting (required for legal documents and internal regulations)

1. `python tools/library.py find "<number or keyword>"` (or open the index).
2. Full text available: open the file, quote verbatim with article and clause; say "per the library copy, status checked on ...".
3. No full text: state the content only as the indexed source gives it, mark "[not checked against full text]"; no quotation marks.
4. Not in the index: look it up on an official source (the `phap-ly` pack if installed), tell the user and propose a new row.
5. Status checked more than 6 months ago: say so, and check again before using it in a document sent outside.

The `legal-basis.md` tables in domain packs are a general baseline; when the project has an index, the project index comes first.

## Adding or updating a document

Put the file in the right folder, name it by the rule, add a row to "Danh mục", then `python tools/library.py check`. A replaced
document: do not delete its row; change Status and record what replaced it (still needed for older cases). The agent writes to
the index only when the user asks; edit with an Excel library while keeping the formatting, then run `check` again.

## Regular checks

`python tools/library.py check` reports missing files, files not in the index, duplicate numbers, "in force" rows that record a
replacement, status checks older than 180 days, rows that need checking, confidential documents. `stats` gives counts by group and status.

## Sensitive data

Internal and confidential documents: do not upload them to a cloud Project or outside service; the agent works with the files on
the computer. Record this in the Sensitivity column.
