# assets/fonts/

Put the organization's own font files in this folder when some documents must use that font. The AI agent uses them when you ask (for example, "use font X for this document") or when PROJECT.md names the standard font.

## How to use

1. Copy the font files (.ttf, .otf, .woff2) into this folder. If there are bold or italic files, copy them too.
2. When you give the task, name the font in your request. Or write the standard font in the style line of `PROJECT.md`.
3. Check the result.

## What the font covers

| File type | What happens |
|---|---|
| HTML | The font is embedded in the file. It shows correctly on any computer. |
| PDF | The font is embedded in the file. It shows correctly on any computer. |
| Word, Excel | The file only stores the font name. The recipient's computer must have the font installed, otherwise a substitute font is shown. |

## Font licensing

Only add fonts that the organization is allowed to use and distribute. Embedding a font in an HTML or PDF file that you send outside the organization also distributes the font. If you are not sure, ask the IT or admin department.

*This folder belongs to you: package upgrades never overwrite files here. New projects created from the template ("Create a new project") carry over the font files here.*
