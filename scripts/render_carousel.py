#!/usr/bin/env python3
"""
render_carousel.py: Turn a carousel spec (JSON) into numbered slide PNGs at
Instagram's current carousel size, 1080x1350 (4:5 portrait).

USAGE:
  python3 render_carousel.py spec.json --out slides/

Each slide is built as its own self-contained HTML page (fonts, colours,
and any images embedded inline, no external requests) and captured with
headless Chrome in screenshot mode, which is what actually produces an
exact 1080x1350 pixel image with no scrollbars or browser chrome.

SPEC SCHEMA: see templates/example-spec.json for a full worked example.
Top level:
  {
    "palette": {"bg": "#...", "ink": "#...", "accent": "#...",
                 "on_accent": "#...", "muted": "#..."},
    "fonts_css": "fonts.css",            // pre-built, see fetch_fonts.py
    "headline_font": "Fraunces",
    "body_font": "Inter",
    "handle": "@yourhandle",
    "display_name": "Your Name",
    "logo": null,                          // path to a logo image, or null
    "slides": [ {...}, {...}, ... ]
  }

Slide "type" values: cover, hook2, content, cta. See the template for the
fields each type expects. "background_image" (path) is optional on any
slide type; when present it's used as a cover-fit background with a dark
scrim behind the text for legibility.

SAFE MARGIN: Instagram's profile grid crops a 4:5 post to 3:4 (1012x1350,
centered), which trims 34px off each side. This renderer keeps all text
inside a wider safe margin than that by default, so nothing important is
ever in the crop zone.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import shutil
import subprocess
import sys
from pathlib import Path

CANVAS_W = 1080
CANVAS_H = 1350
SAFE_MARGIN = 84  # comfortably wider than IG's 34px grid-crop margin


def find_chrome() -> str:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    raise SystemExit(
        "Couldn't find Chrome/Chromium. Install Google Chrome, or pass "
        "--chrome-path pointing at a Chromium binary."
    )


def embed_image(path: str | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"ERROR: image not found: {path}")
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def build_base_css(spec: dict) -> str:
    pal = spec["palette"]
    fonts_css = Path(spec["fonts_css"]).read_text() if spec.get("fonts_css") else ""
    return f"""
{fonts_css}
*{{ margin:0; padding:0; box-sizing:border-box; }}
html,body{{
  width:{CANVAS_W}px; height:{CANVAS_H}px; overflow:hidden;
  font-family:'{spec.get("body_font","Inter")}',-apple-system,sans-serif;
  background:{pal["bg"]}; color:{pal["ink"]};
}}
.slide{{ position:relative; width:100%; height:100%; display:flex; flex-direction:column;
         padding:{SAFE_MARGIN}px; overflow:hidden; }}
.bg-image{{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0; }}
.scrim{{ position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.15), rgba(0,0,0,.55)); z-index:1; }}
.content{{ position:relative; z-index:2; height:100%; display:flex; flex-direction:column; }}
.headline{{ font-family:'{spec.get("headline_font","Fraunces")}',Georgia,serif; font-weight:700;
            line-height:1.06; letter-spacing:-.5px; }}
.body-text{{ font-size:34px; line-height:1.45; font-weight:400; }}
.kicker{{ font-size:24px; font-weight:600; letter-spacing:.14em; text-transform:uppercase; }}
.badge{{ display:flex; align-items:center; gap:14px; }}
.badge img{{ width:52px; height:52px; border-radius:50%; object-fit:cover; }}
.badge .names{{ display:flex; flex-direction:column; line-height:1.25; }}
.badge .handle{{ font-weight:700; font-size:24px; }}
.badge .display-name{{ font-size:19px; opacity:.75; }}
.pagecount{{ position:absolute; top:{SAFE_MARGIN}px; right:{SAFE_MARGIN}px; font-size:22px;
             font-weight:600; z-index:2; }}
.cta-pill{{ display:inline-block; padding:20px 40px; border-radius:100px; font-weight:700;
            font-size:30px; }}
.swipe-hint{{ font-size:22px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; opacity:.8; }}
"""


def render_badge(spec: dict, text_color: str) -> str:
    logo = spec.get("logo")
    if logo:
        logo_data = embed_image(logo)
        return f'<div class="badge"><img src="{logo_data}" alt=""></div>'
    handle = esc(spec.get("handle", ""))
    name = esc(spec.get("display_name", ""))
    if not handle and not name:
        return ""
    return (f'<div class="badge" style="color:{text_color};"><div class="names">'
            f'<div class="handle">{handle}</div>'
            f'<div class="display-name">{name}</div>'
            f'</div></div>')


def render_slide_html(spec: dict, slide: dict, index: int, total: int) -> str:
    pal = spec["palette"]
    stype = slide.get("type", "content")
    bg_image_data = embed_image(slide.get("background_image"))
    bg_layer = ""
    if bg_image_data:
        bg_layer = f'<img class="bg-image" src="{bg_image_data}"><div class="scrim"></div>'
        text_color = pal.get("on_image", "#FFFFFF")
    else:
        text_color = pal["ink"] if slide.get("light_bg", stype not in ("cover", "hook2", "cta")) else pal.get("on_accent", "#FFFFFF")

    slide_bg = pal["bg"] if slide.get("light_bg", stype not in ("cover", "hook2", "cta")) else pal["accent"]
    if bg_image_data:
        slide_bg = "transparent"

    body_html = ""

    if stype == "cover":
        badge = render_badge(spec, text_color)
        body_html = f"""
          <div style="margin-top:auto;">{badge}</div>
          <div style="margin-top:auto;">
            <div class="kicker" style="color:{pal.get('accent2', text_color)}; margin-bottom:18px;">{esc(slide.get('kicker',''))}</div>
            <div class="headline" style="font-size:{slide.get('headline_size',86)}px; color:{text_color};">{slide['headline']}</div>
          </div>
          <div style="margin-top:36px;">
            <div class="swipe-hint" style="color:{text_color};">{esc(slide.get('swipe_hint','Swipe →'))}</div>
          </div>
        """
    elif stype == "hook2":
        body_html = f"""
          <div style="margin-top:auto; margin-bottom:auto;">
            <div class="kicker" style="color:{pal.get('accent2', text_color)}; margin-bottom:18px;">{esc(slide.get('kicker',''))}</div>
            <div class="headline" style="font-size:{slide.get('headline_size',68)}px; color:{text_color};">{slide['headline']}</div>
            {"<div class='body-text' style='margin-top:26px; color:" + text_color + ";'>" + esc(slide.get('body','')) + "</div>" if slide.get('body') else ""}
          </div>
        """
    elif stype == "cta":
        badge = render_badge(spec, text_color)
        body_html = f"""
          <div style="margin-top:auto; margin-bottom:auto;">
            <div class="kicker" style="color:{pal.get('accent2', text_color)}; margin-bottom:18px;">{esc(slide.get('kicker',''))}</div>
            <div class="headline" style="font-size:{slide.get('headline_size',64)}px; color:{text_color}; margin-bottom:24px;">{slide['headline']}</div>
            <div class="body-text" style="color:{text_color}; margin-bottom:38px;">{esc(slide.get('body',''))}</div>
            <div class="cta-pill" style="background:{pal.get('on_accent','#FFFFFF')}; color:{pal['accent']};">{esc(slide['cta_text'])}</div>
          </div>
          <div style="margin-top:auto;">{badge}</div>
        """
    else:  # content
        num_label = f'{index:02d}' if slide.get("show_number", True) else ""
        body_html = f"""
          <div class="pagecount" style="color:{text_color}; opacity:.55;">{num_label}/{total-1:02d}</div>
          <div style="margin-top:auto; margin-bottom:auto;">
            {"<div class='kicker' style='color:" + pal.get('accent2', pal['accent']) + "; margin-bottom:18px;'>" + esc(slide.get('kicker','')) + "</div>" if slide.get('kicker') else ""}
            <div class="headline" style="font-size:{slide.get('headline_size',56)}px; color:{text_color}; margin-bottom:28px;">{slide['headline']}</div>
            {"<div class='body-text' style='color:" + text_color + ";'>" + esc(slide.get('body','')) + "</div>" if slide.get('body') else ""}
          </div>
        """

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{build_base_css(spec)}</style></head>
<body>
<div class="slide" style="background:{slide_bg};">
  {bg_layer}
  <div class="content">{body_html}</div>
</div>
</body></html>"""


def screenshot(chrome: str, html_path: Path, png_path: Path) -> None:
    # file:// URLs need an absolute path. A relative one silently resolves
    # to Chrome's own "site can't be reached" page, which screenshot mode
    # then happily captures as a normal-looking PNG, no error, no crash.
    abs_html = html_path.resolve()
    cmd = [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={CANVAS_W},{CANVAS_H}",
        f"--screenshot={png_path}",
        f"file://{abs_html}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not png_path.exists():
        raise SystemExit(f"ERROR: screenshot failed for {abs_html}\n{result.stderr}")
    # A blank or error page screenshots as a tiny, near-empty PNG. A real
    # 1080x1350 slide with text and colour never comes out this small, so
    # this catches "file:// URL was wrong" and similar silent failures.
    if png_path.stat().st_size < 5000:
        raise SystemExit(
            f"ERROR: {png_path} is only {png_path.stat().st_size} bytes, that's "
            f"almost certainly a blank or error page, not a real slide. "
            f"Source: {abs_html}"
        )


def resolve_spec_paths(spec: dict, base_dir: Path) -> None:
    """All file paths in a spec (fonts_css, logo, per-slide background_image)
    are relative to the spec file itself, not to whatever directory the
    script happens to be run from. Rewrite them to absolute paths in place."""
    def resolve(p: str | None) -> str | None:
        if not p:
            return p
        path = Path(p)
        return str(path if path.is_absolute() else (base_dir / path))

    if spec.get("fonts_css"):
        spec["fonts_css"] = resolve(spec["fonts_css"])
    if spec.get("logo"):
        spec["logo"] = resolve(spec["logo"])
    for slide in spec.get("slides", []):
        if slide.get("background_image"):
            slide["background_image"] = resolve(slide["background_image"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--chrome-path", default=None)
    args = ap.parse_args()

    if not args.spec.exists():
        print(f"ERROR: not found: {args.spec}", file=sys.stderr)
        return 2

    spec = json.loads(args.spec.read_text())
    resolve_spec_paths(spec, args.spec.parent)
    slides = spec["slides"]
    if not slides:
        print("ERROR: spec has no slides", file=sys.stderr)
        return 2

    chrome = args.chrome_path or find_chrome()
    args.out.mkdir(parents=True, exist_ok=True)

    for i, slide in enumerate(slides):
        html = render_slide_html(spec, slide, i, len(slides))
        html_path = args.out / f"_slide-{i+1:02d}.html"
        png_path = args.out / f"slide-{i+1:02d}.png"
        html_path.write_text(html)
        screenshot(chrome, html_path, png_path)
        html_path.unlink()
        print(f"[render] slide {i+1}/{len(slides)} ({slide.get('type','content')}) -> {png_path}")

    print(f"\n[render] {len(slides)} slides -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
