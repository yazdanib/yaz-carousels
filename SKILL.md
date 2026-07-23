---
name: yaz-carousels
description: Write and design a high-performing Instagram carousel from a short brief. Uses the AIDA structure with a double hook (cover + a second hook on slide 2) and a closure beat before the CTA, renders every slide at Instagram's current 4:5 carousel size (1080x1350, not square), and applies the user's brand colours/fonts/logo or a clean default when they don't have one. Also supports Style B, a video cover with an overlaid headline instead of a text-only one. Use when the user wants to create, design, or write an Instagram carousel post.
metadata:
  type: skill
---

# Instagram Carousels

Turns a topic into a finished, ready-to-upload Instagram carousel: real copy (not generic tips) plus rendered slide images at the correct size. Two phases: **write it** (the hook and copy principles below), then **render it** (a script, not hand-drawn images).

## Hook and copy principles (apply these while writing)

- **Never reveal the answer in slide 1 or slide 2.** A hook that gives away the payoff kills the reason to swipe. Describe the tension, not the resolution.
- **Negative or curiosity framing consistently outperforms flat positive statements.** "The reason your carousels get seen once and never saved" pulls harder than "How to make better carousels." Stakes and contrast, not toxicity.
- **Say something specific, not generic.** A real mechanism, a real opinion, a real number beats a platitude every time. If the brief doesn't give you enough to be specific, ask a follow-up rather than writing filler.
- **The CTA is never "follow for more."** It's a specific action: comment a keyword, save it, share it with someone, click a link. Always confirm the exact wording with the user before it renders (step 5 below), it's the one slide tied to their actual funnel.
- **Storytelling and open loops are welcome, this isn't a strict one-idea-per-slide rule anymore.** A slide can introduce a new headline, or it can continue/build on the previous slide's thought, deliberately leaving something unresolved to pull the swipe forward. Real detail, a specific anecdote, or a small narrative arc beats a compressed platitude, even if it runs longer.
- **The cover is the one place brevity still matters most.** It renders as the largest text on the whole carousel (see layout rules below), so a long cover headline doesn't just read worse, it visually doesn't fit. Keep it to a single sharp line, roughly 8 words.
- **Everywhere else, length follows the story, not a word-count table.** A hook2 or content slide can run to two or three sentences if the story needs it. The test isn't "is it short enough", it's "does every sentence on this slide earn its place, and would splitting it into two slides lose the thread." If a slide is doing two unrelated jobs, that's still two slides. If it's one continuous thought, let it breathe.
- **Use `"punch": true` on a content slide for a single big centred statement**, a plot twist, a reveal, a "here's the thing" moment. It renders alone, large, dead-centre of the frame, no pill, no body text. Use it sparingly, once or twice per carousel, it works because it's rare.

## The structure (this is fixed, don't deviate from the shape)

| Slide | Type | Job |
|---|---|---|
| 1 | `cover` | Attention. The largest text in the whole carousel and the fewest words. Withholds the answer, never states the topic flatly. Shows the handle/name or logo. |
| 2 | `hook2` | Attention/Interest bridge. A SECOND hook, sharper or more specific than slide 1. Never just restates slide 1, it escalates the tension. This is the slide most carousels skip, and it's the one that decides if people swipe past slide 2 or keep going. |
| 3 to N-2 | `content` | Interest, then Desire. Each slide either opens a new headline or continues the previous one, storytelling and open loops are fine here. Early ones build interest (name the problem, the mechanism, the mistake, a specific moment). Later ones build desire (the payoff, the result, why it matters). Use `punch:true` for a standout single-statement beat. |
| N-1 | `content` (closure) | Resolve the loop. Whatever tension or story has been running since slide 1 gets an answer or a landing point here, before the ask. A `punch:true` slide often works well for this, since a resolution is usually one clean statement. |
| N | `cta` | Action. One specific, concrete ask. Never "follow for more." |

That's AIDA: Attention (1-2), Interest (early content), Desire (late content), Action (last slide), with an explicit closure beat between Desire and Action so the CTA doesn't land on an unresolved thought.

## Layout convention (the renderer already does this, don't fight it)

- **The kicker is a pill-shaped chip, not plain coloured text**, sitting directly above the headline with a small gap, as one left-aligned group, not stranded at the top of the slide.
- **Headline and body text are left-aligned by default.** Multi-line centred paragraphs read worse than left-aligned ones; centring is reserved for `punch` slides, where a single short statement genuinely looks better dead-centre.
- **The handle/account name is the one element that's always left-aligned and pinned to the top**, on every slide type that shows it, regardless of how the rest of that slide is arranged.
- **The cover headline fills roughly 75% of the frame.** It's not just "the biggest text", the layout gives it almost the whole page, centred both ways, so a short line reads as a real visual statement rather than a slightly-larger heading.
- **Page numbers sit bottom-left, small and muted.** Not top-right.
- **CTA buttons and swipe hints are bottom-anchored**, with real margin above the true edge, not flush against it. The CTA button is left-aligned with the headline/body above it, not centred.
- **Use a genuinely bright, saturated colour for the cover/hook2/cta slides, never near-black.** A dark neutral reads as heavy and downbeat; a bright colour reads as energetic and is what makes a text-only slide still feel designed. If a brand's actual colour is dark, that's fine, but don't default to near-black when nothing else was specified.

## Format facts (don't guess these, they're checked)

- **1080x1350 pixels, 4:5 portrait.** Not square. This is Instagram's current default carousel size and it fills more of the feed than square does.
- Instagram's profile grid crops a 4:5 post to 3:4 for the grid view (1012x1350, centered), trimming roughly 34px off each side. The renderer's safe margin is already wider than that, so this only matters if you're placing something unusually close to the edge yourself.
- 7 to 10 slides total is the sweet spot for this structure (1 cover + 1 second hook + 3-6 content + 1 closure + 1 CTA). Don't pad it out with filler slides just to hit a number, and don't skip the closure beat just to hit a lower one.

## Workflow

### 1. Get the brief

Ask (in one message, not five separate ones):
- What's the carousel about, and who is it for?
- What's the goal: reach (new followers), nurture (existing audience), or convert (drive an action)?

### 2. Ask about brand assets, don't assume them

- **Colours:** do they have brand hex codes? If not, say you'll pick a clean default pairing and show it to them before finalizing, don't just silently apply something.
- **Fonts:** do they have specific font names/files? If not, default to a strong pairing (this skill defaults to Fraunces for headlines, Inter for body, both fetched automatically, no install needed). If they have brand fonts already in use elsewhere (e.g. from a previous skill/PDF), ask if they want those reused instead.
- **Logo or handle:** do they have a logo file? If yes, use it on the cover and CTA slide. If no, use their handle + display name instead, that's the default and it's completely fine.

### 3. Ask about images, but don't block on it

"Do you have any photos you want used on specific slides, or should I pull matching stock photos from Pexels, or keep it text-only?" All three are fine, don't treat this as a blocker.

- **Their own photos:** use the file path directly as a slide's `background_image`.
- **Pexels stock photos:** `scripts/pexels_photo.py "search terms" --list` to see a few candidates before committing, then `--out path/to/image.jpg` to download one. Always look at more than one candidate. Check each for: no competing brand's logo visible in the shot, a background that isn't distractingly cluttered, and that it actually shows the specific thing being described, not just a generic vibe. Needs `PEXELS_API_KEY` (same free key as any other Pexels use).
- **Neither:** text-only slides on the brand-coloured background. This is a completely normal, high-performing carousel style, not a fallback to apologise for.

Only use an image where it earns its place, e.g. demonstrating a physical position or a visual comparison. A slide that's just restating the headline over a generic stock photo is worse than the same slide in plain text.

### 4. Write the copy

Apply the hook and copy principles at the top of this file. This is where most of the actual work is, the render step is mechanical once the copy is right.

### 5. Draft the CTA, then confirm it before rendering

**Do not render a final CTA slide without showing the drafted CTA copy to the user and getting a yes first.** This is the one thing on the whole carousel that's tied to their actual funnel (a comment keyword, a link, a DM prompt), and guessing wrong here is the costliest mistake to ship. Ask something like: "Here's the CTA slide I'd use: '[headline]' / '[cta_text]'. Is that the exact action you want, or is there a specific keyword/link/offer this should point to instead?"

### 6. Build the spec and render

Write a spec JSON (see `templates/example-spec.json` for the schema) with the palette, fonts, handle/logo, and all slides, then:

```bash
# only needed once per project, or when the font pairing changes
python3 scripts/fetch_fonts.py --out fonts.css --family "Fraunces:700" --family "Inter:400,600"

# renders every slide as a numbered PNG
python3 scripts/render_carousel.py spec.json --out slides/
```

`fonts_css` in the spec is a path relative to the spec file itself, not to wherever you happen to run the command from. Same for `logo` and any per-slide `background_image`.

### 7. Show the result

Read the rendered PNGs back and actually look at them before telling the user it's done, don't just report the exit code. Check: text isn't clipped, the badge/logo is legible against its background, nothing important sits right at the edge.

## Style B: a video cover instead of a text-only one

Style A (everything above) is the default: every slide is a rendered PNG. Style B swaps just the cover for a real video, cropped to the carousel frame, with the headline and handle overlaid on top, inside a light frame border, then continues as normal PNG slides from slide 2 onward. This is the "video carousel" pattern some creators use, a short clip with a handwritten-style hook overlaid as slide one.

**Ask before assuming Style B.** Default to Style A. Only switch when the user has an actual video clip they want as the cover, or explicitly asks for a video-first carousel.

### How it's built

1. Slide 1 is produced by `scripts/render_video_cover.py`, not `render_carousel.py`. It crops the source video to 1080x1350, builds the same kind of transparent text overlay this skill always uses (an HTML page shot by headless Chrome, not ffmpeg's own text rendering), and composites it onto the video in one ffmpeg pass.
2. Slides 2 onward render exactly as Style A, through `render_carousel.py`, numbered starting from 2 so they sit correctly after the video in the final upload order.
3. The user uploads the resulting `.mp4` as position 1 and the `.png` files as the rest, directly in Instagram's own carousel composer. This skill doesn't merge them into one file, Instagram doesn't need that, it mixes media types in a carousel natively.

### Spec addition

Add a `cover_video` block to the spec (same top-level `palette`/`fonts_css`/`handle`/`display_name` apply to it):

```json
{
  "cover_video": {
    "source": "raw/cover.mp4",
    "headline": "start here",
    "position": "upper-left",
    "frame": true
  },
  "slides": [
    {"type": "hook2", "...": "..."},
    {"type": "content", "...": "..."}
  ]
}
```

`position` is `upper-left` (matches the reference pattern most creators use), `upper-center`, `center`, or `lower-left`. `frame` toggles the white rounded border, on by default, it's what makes a video read as a considered cover rather than a random clip.

```bash
python3 scripts/render_video_cover.py raw/cover.mp4 --spec spec.json --out slides/slide-01.mp4
python3 scripts/render_carousel.py spec.json --out slides/   # slides 2+
```

Same word-count and hook principles apply to the overlaid headline as to a normal cover, short, no answer given away.

## Setup

Style A (the default) needs no pip packages, only Python's standard library plus headless Chrome:

- **Google Chrome** (or Chromium) installed. That's the only real dependency for text-only/image carousels.
- **Internet access** the first time you fetch a font pairing (Google Fonts), none after that, the fonts get embedded locally as base64 so nothing re-fetches on every render.

If Chrome isn't found, `render_carousel.py` says so and tells you to install it or pass `--chrome-path`.

**Style B additionally needs `ffmpeg` on PATH** (`brew install ffmpeg` / your distro's package manager), only for the video cover step. Nothing else in this skill touches ffmpeg.

## Common mistakes this skill exists to prevent

- **Square images.** 1080x1080 is the old default. Don't use it here.
- **A cover slide that states the topic instead of hooking it.** "5 Tips For Better Carousels" is a topic. "The reason your carousels get seen once and never saved" is a hook.
- **Slide 2 that just repeats slide 1 in different words.** It has to escalate, not restate.
- **Two unrelated ideas crammed onto one slide.** Storytelling and longer sentences are fine now, but a slide still does one job. If it's doing two, split it.
- **"Follow for more" as the CTA.** Always ask what the actual next action should be.
- **Rendering the CTA before the user has confirmed it.** See step 5, this is not optional.
- **Going straight from the last content slide to the CTA with no closure.** The ask lands better when the story actually resolved first.
- **Centring headline/body text on a normal content slide.** That's reserved for `punch` slides. Everything else is left-aligned.
