# docs/

Guides for users, to be read as needed. Open `START_HERE.html` at the project root to see the whole
handbook; the four guides each have a `.html` file of the same name next to the Markdown. The English version
of the whole handbook is in `en/` (open `START_HERE.en.html`); every page has a language switch button.

- `HUONG_DAN_SU_DUNG_VI.md`: daily use (Vietnamese).
- `HUONG_DAN_TAO_PROJECT_MOI_VI.md`: creating a new project, with a block of instructions to paste into the Project/cloud (Vietnamese).
- `HUONG_DAN_CHUYEN_DOI_PROJECT_CO_SAN_VI.md`: existing projects and package upgrades (Vietnamese).
- `HUONG_DAN_SKILLS_VI.md`: choosing skills and using templates (Vietnamese).
- `NGUON_THAM_KHAO_VI.md`: sources of ideas, audit of reference repos and what was not imported (Vietnamese).
- `en/`: the English version of the five documents above (`NEW_PROJECT_GUIDE`, `DAILY_USE_GUIDE`,
  `EXISTING_PROJECT_UPGRADE_GUIDE`, `SKILLS_GUIDE`, `SOURCES_AND_REFERENCES`), each with `.md` and `.html`
  (the references document has `.md` only).

Markdown is the easy-to-edit guide content; HTML is the presentation built from Markdown by
`tools/build_guides_html.py`. Update the HTML only when you deliberately edit the guides, not in
every task. The agent does not need to read both forms or the whole folder to do office work.
