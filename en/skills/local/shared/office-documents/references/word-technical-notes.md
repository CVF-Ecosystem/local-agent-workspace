# Technical notes for building or editing Word files

Experience verified on `.docx`; open when building or editing a real file. It does not replace the guidance of the formatting tool you are using.

## Edit an existing file or build new

- If the user already has the file (proposal, procedure, form), **edit it in place** to keep images, tables, headers and footers; rebuild only when the old structure is broken.
- With `python-docx`: keep references to the elements to change from the start, clone (`copy.deepcopy`) a sample paragraph or row of the SAME kind and insert it with
  `addnext`; replace text at the `w:t` level to keep formatting. The sample table must have the same number of columns; add a row by cloning the last row.
- Each procedure step is usually a `ListParagraph` paragraph with ONE run like "Step n — …:". To add a step, clone the right kind of paragraph and renumber the steps.
  Do not renumber sections that have many cross-references: insert the new content as a sub-section or an appendix.
- After editing, still render and look at every newly added page, update the page count in the document-code table, remove wrong cross-references, and re-check the order of table row numbers.

## Vietnamese text

- Find and replace: a file converted from an old `.doc` through LibreOffice may store accents as Unicode NFD while the typed string is NFC; matching is always `False` and the
  replacement silently does not happen. Normalise both strings with `unicodedata.normalize("NFC", ...)` before comparing.
- Force a font (such as Times New Roman) through both `run.font.name` AND the XML `w:rFonts` (`ascii`, `hAnsi`, `eastAsia`, `cs`), plus the file's Normal style.
- Line break inside a table cell: a `"\n"` character in the string passed to `python-docx` shows as a real new line in Word (good for a short secondary line under a job-title label).

## Layout

- Align "Label: Value" with a two-column table (label column about 5.2 cm, bold), not with spaces or tabs.
- The national-motto and agency block is a two-column table without borders: left column about 6.5 cm, right column about 11 cm, left and right margins about 2 cm and 1.5 cm
  (verified to fit on one line for the motto at size 12 bold). Two lines in one cell should be two separate paragraphs. The issuing organisation's name takes its two lines;
  the department name goes into its own parameter and is not stuffed into the second line of the company name.
- Section headings: `keep_with_next = True` so they are not orphaned at the bottom of a page, especially right before a large diagram image.
- Long tables: repeat the header row when it breaks across pages (`w:tblHeader`) and do not let a row split across two pages (`w:cantSplit`).
- Right column widths: set `w:tblLayout` to `fixed` and edit `w:gridCol`; setting only `cell.width` makes LibreOffice split the columns equally. The No. column needs at least about 1.3 cm.
- The page count in the document-code table cannot be guessed: set a placeholder, build, render a PDF and count the real pages, fix it and build again. A document must not contradict its own file.

## Images

- Images embedded in the source file: `unzip file.docx "word/media/*"`, then LOOK AT EACH IMAGE (do not infer from file names or zip order) to match it to the right section; reuse the images, do not redraw diagrams.
- New build: use the library's image feature (for example `ImageRun` in `docx`, `add_picture` in `python-docx`), centred, with an italic caption.
- Inserting an image into an existing `.docx` by editing the XML (unzip, edit `word/document.xml`, zip again) has three easy mistakes: (1) add `<Default Extension="jpg" ContentType="image/jpeg"/>`
  to `[Content_Types].xml` if it is missing; (2) add the image relationship to `word/_rels/document.xml.rels`; (3) in `<w:pPr>`, `<w:spacing>` must come BEFORE `<w:jc>`, otherwise
  schema validation fails.

## Reading and checking

- Extract the source content to Markdown (for example `markitdown`) and read all of it before writing the rebuild script; without a tool, read `word/document.xml` with `zipfile` and a tag-stripping regex.
- Render to images (`soffice --convert-to pdf` then `pdftoppm`) and look at EVERY page, not just the first: is the motto aligned, does a table overflow the page, is the signature block split off alone,
  is a heading orphaned, is an image shrunk too small, do the page numbers match.
- A substitute font in the checking environment (no real Times New Roman) can draw a bold "Đ" at the start of a word so it looks struck through. Read that run's XML: if there is no
  `w:strike`, it is only a display quirk of the substitute font; do not change the text, remove bold or change the font to "fix" it.
