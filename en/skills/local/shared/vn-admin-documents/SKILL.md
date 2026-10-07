---
name: vn-admin-documents
description: >-
  Suggestions for drafting Vietnamese administrative documents in the proper format (official letter,
  submission, report, notice, minutes, decision): the format components, how to write the number and
  symbol, place, date, summary line, recipients, and the usual layout parameters. Use when the
  organisation applies the format of the state records-management rules or its own records-management
  regulation; it does not replace current regulations or legal advice.
  Triggers when the user says: "draft an official letter", "draft a submission", "in the proper document format", "number and symbol", "recipients".
metadata:
  version: "1.0"
---

# Administrative documents in the proper format

Use when the user needs a document with an official format (sent to another body, put up for
signature, issued internally). When the content is short and needs no formal format, use
`internal-comms` or `office-documents`.

## Order of authority

1. **The organisation's own records-management regulation and document templates** (if the user has
   them): use these first, because enterprises and units often have their own rules.
2. **The state rules on records management** that the organisation applies. A common basis is
   Decree 30/2020/ND-CP (the format and layout parts are in its annex). Checked on 2026-10-06: the decree is still in force and the layout parameters below match its annex.
   Rules may be amended or replaced after that: before issuing, check the current version or say it was not checked. Do not assert which
   rule the unit must follow; ask or write "needs confirmation".
3. The frame in `references/document-frames.md` is only a starting point, not an approved template.

## Format components

| Component | How to write it |
|---|---|
| National title and motto | The first two lines on the right; use only for documents of bodies that apply the state format. |
| Issuing body | On the left; the parent body (if any) and the issuing unit, using the exact official name. |
| Number and symbol | `Số: [number]/[document-type symbol]-[unit abbreviation]`. An official letter: `Số: [number]/[unit abbreviation]-[drafting department abbreviation]`. The number is issued by the registry: **do not invent it**, write `[number]`. |
| Place and date | `[Place], ngày [dd] tháng [mm] năm [yyyy]` (written in Vietnamese in the document); days under 10 and months 1 and 2 take a leading 0. Leave the date empty until issued. |
| Document type and summary | For documents with a type name: the type in capitals, the summary below it. An official letter has no type name: `V/v [summary]`. The summary states one main point, briefly. |
| Content | Basis, content, request or recommendation; layout depends on the document type. |
| Title, name and signature | By the person with authority; write the signing authority (TM., KT., TL.: on behalf of, for, by authorisation) as it really is. **Do not fill in** the name, title or signing authority yourself. |
| Recipients | The list of bodies and persons receiving it, and "Lưu: VT" (or as the regulation requires); only list recipients the user names. |

Common document-type symbols: BC (báo cáo, report), TTr (tờ trình, submission), TB (thông báo, notice), QĐ
(quyết định, decision), KH (kế hoạch, plan), BB (biên bản, minutes), HD (hướng dẫn, guidance). Check them against the symbol table in the rule/regulation that applies.

## Layout (common parameters)

A4 paper, a Unicode Vietnamese font (usually Times New Roman), body size 13 to 14. Margins are usually:
top and bottom about 20 to 25 mm, left about 30 to 35 mm, right about 15 to 20 mm. These are the common
figures in the format annex; check the current version or the unit's regulation before printing for issue.

When building a Word file: the heading block (agency name on the left, national motto on the right) and the signature block use a two-column table without borders. Official letters and submissions in state format do not use ruled frames for the content; accounting vouchers and forms with their own numbered template usually have bordered tables. Look up the numbered template and the current legal document (including whether it is still in force or replaced) before choosing; see `office-documents` (`references/form-standardization.md`).

## How to work

1. Identify the document type, the signer, the recipients, the issuing unit and the basis. Ask once, in
   one message, if something is missing.
2. Draft to the frame, keeping exactly the facts the user supplied. Figures, names, deadlines, authority
   and the numbers of basis documents that are not in the source get `[needs confirmation]`; do not
   create document numbers, dates or signer names.
3. Style: short sentences, consistent terms, no colloquialisms; state the request or recommendation
   clearly at the end of the document.
4. Deliver the draft in the conversation. Create a Word file only when asked, with a suitable formatting tool.

## High-caution mode when issuing

A document going outside or for signature falls under "High-caution mode" in `AGENTS.md`: check each
figure, date, name, body name, and the number and date of basis documents against the source; state what
could not be checked. Legal observations in the document are suggestions for a person with authority to confirm.
