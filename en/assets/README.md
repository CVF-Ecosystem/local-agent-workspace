# assets/

Place your logo and organization name here so the control panel (`APP.bat` / `APP.command`) and the guide pages (`START_HERE.html`, `docs/*.html`) show them instead of the default "LW" icon and the *Local Agent Workspace* title. Optional.

## 1. Logo

Put an image here named `logo.png` (or `logo.svg`, `logo.jpg`, `logo.webp`), up to 2 MB. The logo sits in a white square tile, so a square or near-square image works best.

## 2. Organization name (optional)

Create `branding.json` in this folder with:

```json
{
  "title": "Organization name",
  "subtitle": "Agent Workspace",
  "logo": "logo.png"
}
```

- `title`: organization or author name, replacing *Local Agent Workspace*. Long names are shrunk to fit one line.
- `subtitle`: the smaller line below, replacing *Control panel*.
- `logo`: the logo file name, when it is not named `logo.*`.

## 3. Guide pages

Guide pages are opened straight from disk and cannot read `branding.json`. Each time the control panel opens, it rewrites `assets/branding.js` from `branding.json` for the guide pages to use. After editing `branding.json`, open APP once, then reload the guide page.

New projects created from the template ("Create a new project") carry over its `branding.json`, `branding.js`, `logo.*` and the fonts in `assets/fonts/`; other files in `assets/` are not copied.

## 4. Custom fonts

Put the organization's font files in `assets/fonts/`. See `assets/fonts/README.md` for how the AI agent uses them and the limits for Word and Excel files.

*This folder belongs to you: package upgrades never overwrite files here.*
