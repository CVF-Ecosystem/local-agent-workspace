---
name: vn-admin-documents
description: >-
  Draft or review the format of Vietnamese administrative documents (official letters,
  submissions, reports, notices, minutes and decisions) under the organisation’s rules or
  the government rules it applies. Use for documents to be signed or sent formally; this
  does not replace checking current rules or legal advice. Triggers when the user says:
  “draft an official letter”, “draft a submission”, “in the proper document format”,
  “number and symbol”, “recipients”.
metadata:
  version: "1.2"
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
3. The frames in `references/document-frames.md` (official letter, submission, report, notice, plan, decision, invitation,
   meeting minutes) are only a starting point, not approved templates.

## Format components

| Component | How to write it |
|---|---|
| National title and motto | The first two lines on the right; use only for documents of bodies that apply the state format. |
| Issuing body | On the left; the parent body (if any) and the issuing unit, using the exact official name. |
| Number and symbol | `Số: [number]/[document-type symbol]-[unit abbreviation]`. An official letter: `Số: [number]/[unit abbreviation]-[drafting department abbreviation]`. The number is issued by the registry: **do not invent it**, write `[number]`. |
| Place and date | `[Place], ngày [dd] tháng [mm] năm [yyyy]` (written in Vietnamese in the document); days under 10 and months 1 and 2 take a leading 0. Leave the date empty until issued. |
| Document type and summary | For documents with a type name: the type in capitals, the summary below it. An official letter has no type name: `V/v [summary]`. The summary states one main point, briefly. |
| Content | Basis, content, request or recommendation; layout depends on the document type. |
| Title, name and signature | By the person with authority; write the signing authority (TM., Q., KT., TL., TUQ.: on behalf of, acting, for, by authorisation, by delegated authorisation) as it really is. **Do not fill in** the name, title or signing authority yourself. |
| Recipients | The list of bodies and persons receiving it, and "Lưu: VT" (or as the regulation requires); only list recipients the user names. |

Common document-type symbols: BC (báo cáo, report), TTr (tờ trình, submission), TB (thông báo, notice), QĐ
(quyết định, decision), KH (kế hoạch, plan), BB (biên bản, minutes), HD (hướng dẫn, guidance), GM (giấy mời, invitation). Check them against the symbol table in the rule/regulation that applies.

## Layout (common parameters)

A4 paper; Times New Roman (Unicode TCVN 6909:2001), black; body size 13 to 14, justified, first line indented 1 cm or
1.27 cm, at least 6 pt between paragraphs, line spacing from single to 1.5 lines. Margins: top and bottom 20 to 25 mm, left
30 to 35 mm, right 15 to 20 mm. Page numbers centred in the top margin, not shown on the first page. Size and style of each
component (national title, agency name, summary, basis, articles and clauses, signature block, recipients...) and the list of
templates in the annex: `references/nd30-presentation.md` (checked against a scan of Decree 30/2020/ND-CP on 2026-10-12).
Check the current version or the unit's regulation before printing for issue.

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

## Building and checking Word inside LAW

Use native tools/the unit's template or the optional Word helpers in `office-documents` (see
Supplementary Word tools). `new_nd30_document()` and the HTML renderer are LAW-workspace-only;
the portable generic helper does not provide every ND30 setting. The renderer supports simple
text/tables, refusing images, nested tables and unsupported spans before writing. No overwrite by default.

Run `python tools/check_output.py FILE.docx --profile nd30` to force the administrative profile.
`auto` detects the national title; `none` skips layout checks for another template. Mechanical checks
cover the final section and dominant font/size; they do not replace checking each component,
opening/rendering every page, or checking current law. PASS does not certify legal compliance or the full format.
