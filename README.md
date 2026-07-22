# yaz-carousels

A [Claude Code](https://claude.com/claude-code) skill that writes and designs a high-performing Instagram carousel from a short brief: real hook-driven copy in an AIDA structure, plus fully rendered slide images at Instagram's current 4:5 carousel size, 1080x1350, not square.

No design software, no Canva template. You describe the topic, Claude writes the copy and renders it.

## What makes this different from a generic template

- **Two hooks, not one.** Slide 1 hooks, slide 2 hooks again, sharper. Most carousels only do the first one and lose people on slide 2.
- **AIDA end to end.** Attention (the two hooks) into Interest and Desire (the body slides) into a single, specific Action (the CTA), not a pile of tips with a "follow me" tacked on.
- **The CTA gets confirmed with you before anything renders.** It's the one slide tied to your actual funnel, so it's the one thing this skill won't guess at.
- **Correct format by default.** 1080x1350, Instagram's current carousel size. Square carousels are the old default.

## Install

Clone this into your Claude Code skills folder:

```bash
git clone https://github.com/yazdanib/yaz-carousels.git ~/.claude/skills/yaz-carousels
```

No `pip install` needed, this only uses Python's standard library. The one real requirement is **Google Chrome** (or Chromium) installed, since that's what renders each slide to an exact-pixel image.

If you want real stock photos on any slides instead of text-only, set `PEXELS_API_KEY` (free at pexels.com/api, no card needed). Not required if you're only using your own images or going text-only.

## Use it

Open Claude Code and just describe the carousel:

> I want a carousel about [topic]. My brand colours are [hex codes] and my handle is [@yours].
> No specific images, text-only slides are fine.

Claude will ask a couple of clarifying questions (goal, brand assets if you have them, whether you want images), draft the copy, show you the CTA slide specifically to confirm before rendering, then render every slide as a numbered PNG ready to upload.

## Or drive it directly

```bash
# 1. fetch a font pairing once (skip if you already have a fonts.css)
python3 scripts/fetch_fonts.py --out fonts.css \
  --family "Fraunces:700" --family "Inter:400,600"

# 2. write a spec.json (see templates/example-spec.json for the schema)

# 3. render every slide
python3 scripts/render_carousel.py spec.json --out slides/
```

## Scripts

| Script | Does |
|---|---|
| `fetch_fonts.py` | Downloads a Google Fonts pairing and embeds it as self-contained base64 CSS, no external requests at render time |
| `pexels_photo.py` | Searches and downloads a matching vertical stock photo from Pexels, for slides that want a real image instead of text-only |
| `render_carousel.py` | Turns a spec JSON into numbered 1080x1350 PNG slides via headless Chrome screenshot mode |

## Spec schema

See [`templates/example-spec.json`](templates/example-spec.json) for a complete, working example. The short version:

```json
{
  "palette": {"bg": "#...", "ink": "#...", "accent": "#...", "accent2": "#...", "on_accent": "#..."},
  "fonts_css": "fonts.css",
  "headline_font": "Fraunces",
  "body_font": "Inter",
  "handle": "@yourhandle",
  "display_name": "Your Name",
  "logo": null,
  "slides": [
    {"type": "cover", "kicker": "...", "headline": "...", "swipe_hint": "Swipe →"},
    {"type": "hook2", "kicker": "...", "headline": "..."},
    {"type": "content", "headline": "...", "body": "..."},
    {"type": "cta", "kicker": "...", "headline": "...", "body": "...", "cta_text": "..."}
  ]
}
```

All file paths in a spec (`fonts_css`, `logo`, any slide's `background_image`) are relative to the spec file itself, not to whatever directory you happen to run the script from.

## Why 1080x1350 and not 1080x1080

Instagram's current default and best-performing carousel size is 4:5 portrait, 1080x1350, it takes up noticeably more vertical space in the feed than the old 1080x1080 square. The profile grid view crops a 4:5 post down to 3:4 (1012x1350, centered), so this renderer keeps a safe margin wider than that crop zone by default, nothing important ever ends up trimmed off in the grid.

## License

MIT, see [LICENSE](LICENSE).
