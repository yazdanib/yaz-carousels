---
name: yaz-carousels
description: Write and design a high-performing Instagram carousel from a short brief. Uses the AIDA structure with a double hook (cover + a second hook on slide 2), renders every slide at Instagram's current 4:5 carousel size (1080x1350, not square), and applies the user's brand colours/fonts/logo or a clean default when they don't have one. Use when the user wants to create, design, or write an Instagram carousel post.
metadata:
  type: skill
---

# Instagram Carousels

Turns a topic into a finished, ready-to-upload Instagram carousel: real copy (not generic tips) plus rendered slide images at the correct size. Two phases: **write it** (the hook and copy principles below), then **render it** (a script, not hand-drawn images).

## Hook and copy principles (apply these while writing)

- **Never reveal the answer in slide 1 or slide 2.** A hook that gives away the payoff kills the reason to swipe. Describe the tension, not the resolution.
- **Negative or curiosity framing consistently outperforms flat positive statements.** "The reason your carousels get seen once and never saved" pulls harder than "How to make better carousels." Stakes and contrast, not toxicity.
- **One idea per slide, never a paragraph.** If it takes more than one or two short sentences, it's two slides.
- **Say something specific, not generic.** A real mechanism, a real opinion, a real number beats a platitude every time. If the brief doesn't give you enough to be specific, ask a follow-up rather than writing filler.
- **The CTA is never "follow for more."** It's a specific action: comment a keyword, save it, share it with someone, click a link. Always confirm the exact wording with the user before it renders (step 5 below), it's the one slide tied to their actual funnel.
- **Word counts are hard caps, not suggestions.** The renderer sizes text large by default; a headline that's actually short is what makes that large size work. Over these caps and count as a rewrite, not a font-size problem:
  - Cover headline: **8 words max.** This is the biggest text on the whole carousel, it needs to be the shortest. If your draft is longer, cut it, don't shrink the font to fit it.
  - Hook2 headline: 10 words max, no body text unless it's genuinely one short clause.
  - Content headline: 8 words max. Body: one sentence, 12 words max. If you need two sentences, that's two slides.
  - CTA headline: 8 words max. Body: one sentence, 10 words max.
- **When in doubt, cut the sentence in half and check it still means the same thing.** If it doesn't, the first draft was carrying two ideas that belong on separate slides.

## The structure (this is fixed, don't deviate from the shape)

| Slide | Type | Job |
|---|---|---|
| 1 | `cover` | Attention. The largest text in the whole carousel and the fewest words. Withholds the answer, never states the topic flatly. Shows the handle/name or logo. |
| 2 | `hook2` | Attention/Interest bridge. A SECOND hook, sharper or more specific than slide 1. Never just restates slide 1, it escalates the tension. This is the slide most carousels skip, and it's the one that decides if people swipe past slide 2 or keep going. |
| 3 to N-1 | `content` | Interest, then Desire. One idea per slide, never a paragraph. Early content slides build interest (name the problem, the mechanism, the mistake). Later ones build desire (the payoff, the result, why it matters). |
| N | `cta` | Action. One specific, concrete ask. Never "follow for more." |

That's AIDA: Attention (1-2), Interest (early content), Desire (late content), Action (last slide).

## Layout convention (the renderer already does this, don't fight it)

- **The kicker is a pill-shaped chip, not plain coloured text.** Pinned near the top of the slide, on its own, not stacked as part of the centred headline group.
- **The headline and body sit lower in the frame, not dead-centre.** There's a deliberate gap between the top-pinned pill and the headline block below it. This is what gives a slide breathing room instead of looking like a wall of centred text.
- **Page numbers sit bottom-left, small and muted.** Not top-right.
- **CTA buttons and swipe hints are bottom-anchored**, with real margin above the true edge, not flush against it.
- **Use a genuinely bright, saturated colour for the cover/hook2/cta slides, never near-black.** A dark neutral reads as heavy and downbeat; a bright colour reads as energetic and is what makes a text-only slide still feel designed. If a brand's actual colour is dark, that's fine, but don't default to near-black when nothing else was specified.

## Format facts (don't guess these, they're checked)

- **1080x1350 pixels, 4:5 portrait.** Not square. This is Instagram's current default carousel size and it fills more of the feed than square does.
- Instagram's profile grid crops a 4:5 post to 3:4 for the grid view (1012x1350, centered), trimming roughly 34px off each side. The renderer's safe margin is already wider than that, so this only matters if you're placing something unusually close to the edge yourself.
- 6 to 9 slides total is the sweet spot for this structure (1 cover + 1 second hook + 3-6 content + 1 CTA). Don't pad it out with filler slides just to hit a number.

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

## Setup

No pip packages required, this skill only uses Python's standard library plus headless Chrome. You need:

- **Google Chrome** (or Chromium) installed. That's the only real dependency.
- **Internet access** the first time you fetch a font pairing (Google Fonts), none after that, the fonts get embedded locally as base64 so nothing re-fetches on every render.

If Chrome isn't found, `render_carousel.py` says so and tells you to install it or pass `--chrome-path`.

## Common mistakes this skill exists to prevent

- **Square images.** 1080x1080 is the old default. Don't use it here.
- **A cover slide that states the topic instead of hooking it.** "5 Tips For Better Carousels" is a topic. "The reason your carousels get seen once and never saved" is a hook.
- **Slide 2 that just repeats slide 1 in different words.** It has to escalate, not restate.
- **A paragraph crammed onto one slide.** If it doesn't fit in one or two short sentences, it's two slides, not one.
- **"Follow for more" as the CTA.** Always ask what the actual next action should be.
- **Rendering the CTA before the user has confirmed it.** See step 5, this is not optional.
