# Default DOCX layout and turning raw content into a document

Use when building a new Word file and the user gives no template. The unit's template or regulation always comes before this
layout. Documents in the state format: `vn-admin-documents` (`references/nd30-presentation.md`). The values below fall inside
the ranges of Annex I of Decree 30/2020/ND-CP, so one layout serves both internal documents and administrative documents.

## Page and paragraphs

| Item | Default |
|---|---|
| Page | A4; top margin 20 mm, bottom 20 mm, left 30 mm, right 15 - 20 mm |
| Font | Times New Roman (or the font the unit requires), black; body size 13 (14 if the unit is used to it) |
| Body | Justified; first line indented 1.27 cm; 6 pt after each paragraph; line spacing 1.15 - 1.3 lines (not above 1.5) |
| Headings | Bold, no first-line indent or less than the body; no italic or underline to show levels; `keep_with_next` |
| Tables | As wide as the text area; table text 1 - 2 sizes smaller than the body; bold header row repeated across pages; columns sized to content |
| Page numbers | Centred in the top margin (administrative documents) or in the footer (internal documents), not on the first page |

Show levels with leading markers, not by increasing the left indent: `I.` → `1.` → `a)` → `-` → `+`. Bullets in Vietnamese
documents use `-`, not `•`, unless the user's template uses another marker.

Colour is only a layer on top of the layout: header-row fill, heading colour, note boxes, cover page. Do not change margins,
sizes or spacing because of colour. Documents in the state format stay black and white.

## Turning raw content (notes, Markdown, chat content) into a document

Read the content and take stock of the signals below before building. For large jobs (many sections, many tables, or Word,
Excel and slides at once) show the user a 3 - 5 line presentation plan (sections, which tables stay, which figures to
highlight, target format) before building, as in the "settle the outline" step for large jobs in `AGENTS.md`. For medium jobs,
just build.

| Signal in the content | Suggested presentation |
|---|---|
| Number and depth of headings | Size of the document, how to split sections; add a table of contents above 10 pages |
| Table columns of numbers, %, money | Number formats; in Excel a total row with a formula; several periods may call for a chart (`data-charts`) |
| A striking figure in prose | Note box, or a metric card (HTML report) |
| A caution or warning sentence | Bordered note box |
| A chain of steps 1 → 2 → 3 | Step table or flow diagram (`process-mapping`) |
| Before/After, Problem/Solution pairs | Two-column table |

Choosing the target format when the user has not said: many tables to calculate or filter → Excel; text read in order or
printed → Word; presenting to an audience → slides. Do not stuff prose into Excel or slides; content with no table is not a fit
for Excel, so say so.

Edit while converting: add one or two lead-in sentences at the start of major sections; write continuous reasoning as
paragraphs and keep bullets for real lists; remove emoji, arrows and leftover Markdown syntax; do not change figures, dates or
proper names.

## Counting check after building

Count on the text extracted from the built file itself, not on the draft. The command below counts unfilled placeholders (any
text in square brackets), "cần xác nhận" (needs confirmation) notes, and marks the user or the template does not want (add or
remove patterns as required, for example the long dash when the template does not use it):

```text
python -c "import zipfile,re,sys;x=re.sub(r'<[^>]+>','',zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf8'));[print(p,len(re.findall(p,x))) for p in sys.argv[2:]]" file.docx "\[[^\]]*\]" "cần xác nhận" "•" "—"
```

Any non-zero result is fixed or stated in the handover (for example "3 places [needs confirmation] remain in section II"). Do
not change marks that the user's template uses.
