# Standardising forms and internal documents in bulk

Use when the user asks to "standardise the forms" in a folder that holds many old files (`.doc`, `.docx`, `.xlsx`). Word technical detail: `word-technical-notes.md`.

## Before editing

1. **Do not touch foreign files.** Look at the "To:" line, the letterhead and the signature: if the document was issued by another organisation and sent to this one, leave it as it is,
   do not standardise its format, only note that it was identified as a foreign file. Check again every time a file is put into the "to standardise" set.
2. **Look at each file as an image** (render, then view every page) before choosing how to handle it; a text summary or word count is not enough.
3. Split into two groups:
   - **Group A, light touch:** the file already has a good table frame and structure; only force the font, fix small typos or naming. One light script for the whole group is quicker and safer than rebuilding.
   - **Group B, rebuild:** the file uses hand-drawn dotted lines instead of a table, lacks the national motto, or still holds real transaction data that must be cleared to make a blank template.
     Keep the fixed parts of the template (such as the default material name of a special-purpose slip) and clear only the document number, date and figures of the old case.

## Special situations

- One old `.doc` can combine TWO different forms (visible only when you look page by page): split it into two files by function.
- Two files in two places serve the same function: merge into the standardised version and do not build a second standard one; ALWAYS tell the user how it was merged, never decide silently.
- **Each form type needs only one blank template and one filled example**, not copies for every sub-process folder. Add a separate copy only when it carries the real figures of a different case from the example.
- When a wrong reference number of a legal basis is found in many files: use a find-and-replace script (NFC-normalised) on both the note under the motto and the footer, then rescan the whole
  folder to confirm the old string is gone, including old `.doc` files.

## Table borders and polish: two separate criteria

- **Whether a form has bordered frames depends on the official template of that kind of paper**, never a single default for all. Official letters and submissions in administrative format use a layout without ruled
  frames (see `vn-admin-documents`); accounting vouchers following a numbered template usually have bordered field tables and sign-off tables. Before deciding, look up the numbered template and the current
  legal document, and check whether it is still in force or has been replaced; do not rely on memory for document numbers. Where a business may design its own voucher, borders are for consistency and readability, not a hard requirement.
- **Correct format is not automatically attractive and professional.** Check both yourself: the same title style (colour, thin underline) across the whole batch; every sign-off block of an internal form in a bordered table,
  not floating text; do not invent another frame style or off-tone border colour when a shared one exists. Do it right from the start instead of waiting for feedback and then re-syncing.
- An internal on-site incident record may drop the document number and the "Recipients" line for brevity, but tell the user it is a dropped item and do not treat it as fully formatted.

## Saving

Draft versions get a new name or their own folder; never overwrite the user's original. A file the agent itself drafted earlier may be overwritten when revised, if you are sure it has not been hand-edited.
Move old versions to an archive folder with a non-overwriting command (`mv -n`) and check the result; do not delete unless asked.
