#!/usr/bin/env python3
"""
render_video_cover.py: Build a video cover slide (Style B): a source video
cropped and inset into a smaller, rounded-corner frame within the carousel's
4:5 canvas, with the display name pinned top-left in the margin, the handle
bottom-left, a swipe hint bottom-right, and the hook headline overlaid on the
video itself. This is slide 1 of a Style B carousel; scripts/render_carousel.py
still renders slides 2+ as normal PNGs.

USAGE:
  python3 render_video_cover.py source.mp4 --spec spec.json --out slide-01.mp4

  # override anything from the spec's cover_video block on the command line:
  python3 render_video_cover.py source.mp4 --headline "start here" --out slide-01.mp4

SPEC: reads the same top-level "palette", "fonts_css", "headline_font",
"handle", "display_name", "logo" fields as a normal carousel spec.json, plus
a "cover_video" block:
  {
    "cover_video": {
      "source": "raw/cover.mp4",
      "headline": "start here",
      "position": "upper-left",    // where the headline sits ON the video: upper-left, upper-center, center, lower-left
      "frame_color": "#F7FAF9",    // margin colour, defaults to the palette's bg
      "duration": null             // seconds to trim to, null = full source
    }
  }

WHY this is a separate script from render_carousel.py: that script only ever
produces a static image via a headless Chrome screenshot. A video cover needs
an actual video pipeline (crop, scale, mask, mux), which means ffmpeg. Keeping
this in its own script means the plain PNG path never needs ffmpeg at all,
only a Style B carousel with a video cover does.

All text (name/handle/swipe hint/headline) is still built the same way as
every other piece of text in this skill: HTML pages rendered by headless
Chrome, composited onto the video by ffmpeg. Not ffmpeg's drawtext.

LAYOUT: the video is inset from the canvas edge by SAFE_MARGIN on the sides,
with a text band above (display name) and below (handle + swipe hint) it, so
it reads like a photo in a frame rather than a full-bleed video with text
stamped on top. The video's corners are rounded via an alpha mask (a
black/white rounded-rect PNG merged onto the cropped video with alphamerge),
since ffmpeg has no built-in rounded-corner filter.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_carousel import (  # noqa: E402
    CANVAS_W, CANVAS_H, SAFE_MARGIN, find_chrome, esc, embed_image, render_mixed_headline,
)

TOP_TEXT_H = 140
BOTTOM_TEXT_H = 140
CORNER_RADIUS = 32

VIDEO_X = SAFE_MARGIN
VIDEO_Y = SAFE_MARGIN + TOP_TEXT_H
VIDEO_W = CANVAS_W - 2 * SAFE_MARGIN
VIDEO_H = CANVAS_H - SAFE_MARGIN - BOTTOM_TEXT_H - VIDEO_Y

POSITION_CSS = {
    "upper-left": "align-items:flex-start; justify-content:flex-start; text-align:left;",
    "upper-center": "align-items:center; justify-content:flex-start; text-align:center;",
    "center": "align-items:center; justify-content:center; text-align:center;",
    "lower-left": "align-items:flex-start; justify-content:flex-end; text-align:left;",
}


def probe_duration(path: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def build_frame_html(spec: dict, cv: dict) -> str:
    """Opaque base layer: margin colour, display name top-left, handle
    bottom-left, swipe hint bottom-right. The video sits on top of this at
    render time, so the video's rect here is left blank."""
    pal = spec["palette"]
    fonts_css = Path(spec["fonts_css"]).read_text() if spec.get("fonts_css") else ""
    frame_color = cv.get("frame_color", pal.get("bg", "#FFFFFF"))
    ink = pal.get("ink", "#12151C")
    muted = pal.get("muted", ink)

    logo = spec.get("logo")
    avatar_html = f'<img class="avatar" src="{embed_image(logo)}" alt="">' if logo else ""
    display_name = esc(spec.get("display_name", ""))
    handle = esc(spec.get("handle", ""))
    swipe = esc(cv.get("swipe_hint", "Swipe →"))

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{fonts_css}
*{{ margin:0; padding:0; box-sizing:border-box; }}
html,body{{ width:{CANVAS_W}px; height:{CANVAS_H}px; overflow:hidden; background:{frame_color};
            font-family:'{spec.get("body_font","Inter")}',-apple-system,sans-serif; }}
.wrap{{ position:relative; width:100%; height:100%; }}
.top{{ position:absolute; top:{SAFE_MARGIN}px; left:{SAFE_MARGIN}px; height:{TOP_TEXT_H - SAFE_MARGIN}px;
       display:flex; align-items:center; gap:12px; }}
.avatar{{ width:44px; height:44px; border-radius:50%; object-fit:cover; }}
.display-name{{ font-weight:700; font-size:28px; color:{ink}; }}
.bottom-left{{ position:absolute; bottom:{SAFE_MARGIN}px; left:{SAFE_MARGIN}px; height:{BOTTOM_TEXT_H - SAFE_MARGIN}px;
               display:flex; align-items:center; font-weight:700; font-size:24px; color:{ink}; }}
.bottom-right{{ position:absolute; bottom:{SAFE_MARGIN}px; right:{SAFE_MARGIN}px; height:{BOTTOM_TEXT_H - SAFE_MARGIN}px;
                display:flex; align-items:center; font-weight:600; font-size:22px; letter-spacing:.04em; color:{muted}; }}
</style></head>
<body>
<div class="wrap">
  <div class="top">{avatar_html}<div class="display-name">{display_name}</div></div>
  <div class="bottom-left">{handle}</div>
  <div class="bottom-right">{swipe}</div>
</div>
</body></html>"""


def build_scrim_html(cv: dict) -> str:
    """A soft dark gradient, transparent PNG the same size as the video crop,
    composited onto the video before the headline so light/busy footage
    doesn't swallow the text. Direction follows where the headline sits."""
    position = cv.get("position", "upper-left")
    if position in ("upper-left", "upper-center"):
        gradient = "linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,0) 48%)"
    elif position == "lower-left":
        gradient = "linear-gradient(0deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,0) 48%)"
    else:
        gradient = "radial-gradient(ellipse at center, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 62%)"
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{ margin:0; padding:0; }}
html,body{{ width:{VIDEO_W}px; height:{VIDEO_H}px; overflow:hidden; background:transparent; }}
.scrim{{ position:absolute; inset:0; background:{gradient}; }}
</style></head>
<body><div class="scrim"></div></body></html>"""


def build_mask_html() -> str:
    """A white rounded-rect on black, exactly the video's crop size. Used as
    an alpha channel via ffmpeg's alphamerge to round the video's corners."""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
*{{ margin:0; padding:0; }}
html,body{{ width:{VIDEO_W}px; height:{VIDEO_H}px; background:#000; overflow:hidden; }}
.hole{{ position:absolute; inset:0; background:#FFF; border-radius:{CORNER_RADIUS}px; }}
</style></head>
<body><div class="hole"></div></body></html>"""


def build_headline_html(spec: dict, cv: dict) -> str:
    """Transparent layer, headline positioned within the video's rect,
    composited on top of the video so it reads as text over footage."""
    fonts_css = Path(spec["fonts_css"]).read_text() if spec.get("fonts_css") else ""
    position = cv.get("position", "upper-left")
    pos_css = POSITION_CSS.get(position, POSITION_CSS["upper-left"])
    text_color = cv.get("text_color", "#FFFFFF")
    headline_font = spec.get("headline_font", "Fraunces")
    punch_font = spec.get("punch_font", headline_font)
    headline = render_mixed_headline(cv.get("headline", ""), punch_font, headline_font)
    pad = 36

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{fonts_css}
*{{ margin:0; padding:0; box-sizing:border-box; }}
html,body{{ width:{CANVAS_W}px; height:{CANVAS_H}px; overflow:hidden; background:transparent;
            font-family:'{spec.get("body_font","Inter")}',-apple-system,sans-serif; }}
.video-pad{{ position:absolute; left:{VIDEO_X}px; top:{VIDEO_Y}px; width:{VIDEO_W}px; height:{VIDEO_H}px;
             padding:{pad}px; display:flex; flex-direction:column; {pos_css} }}
.headline{{ font-family:'{spec.get("headline_font","Fraunces")}',Georgia,serif; font-weight:700;
            font-size:{cv.get('headline_size', 72)}px; line-height:1.12; color:{text_color};
            text-shadow:0 2px 14px rgba(0,0,0,.45), 0 1px 4px rgba(0,0,0,.6); }}
</style></head>
<body>
<div class="video-pad"><div class="headline">{headline}</div></div>
</body></html>"""


def screenshot(chrome: str, html_path: Path, png_path: Path, width: int, height: int) -> None:
    abs_html = html_path.resolve()
    cmd = [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        f"--window-size={width},{height}",
        f"--screenshot={png_path}",
        f"file://{abs_html}",
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    if not png_path.exists() or png_path.stat().st_size < 500:
        raise SystemExit(f"ERROR: screenshot failed for {abs_html}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("source", type=Path, help="source video file")
    ap.add_argument("--spec", type=Path, required=True, help="carousel spec.json (palette/fonts/handle + cover_video block)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--headline", default=None, help="override cover_video.headline from the spec")
    ap.add_argument("--position", default=None, choices=list(POSITION_CSS.keys()))
    ap.add_argument("--duration", type=float, default=None, help="trim to this many seconds")
    ap.add_argument("--chrome-path", default=None)
    args = ap.parse_args()

    if not args.source.exists():
        print(f"ERROR: not found: {args.source}", file=sys.stderr)
        return 2
    if not args.spec.exists():
        print(f"ERROR: not found: {args.spec}", file=sys.stderr)
        return 2

    spec = json.loads(args.spec.read_text())
    base_dir = args.spec.parent
    if spec.get("fonts_css"):
        p = Path(spec["fonts_css"])
        spec["fonts_css"] = str(p if p.is_absolute() else base_dir / p)
    if spec.get("logo"):
        p = Path(spec["logo"])
        spec["logo"] = str(p if p.is_absolute() else base_dir / p)

    cv = dict(spec.get("cover_video", {}))
    if args.headline:
        cv["headline"] = args.headline
    if args.position:
        cv["position"] = args.position
    if args.duration:
        cv["duration"] = args.duration
    if not cv.get("headline"):
        print("ERROR: no headline (pass --headline or set cover_video.headline in the spec)", file=sys.stderr)
        return 2

    chrome = args.chrome_path or find_chrome()
    src_duration = probe_duration(args.source)
    duration = min(cv["duration"], src_duration) if cv.get("duration") else src_duration

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        frame_png = td / "frame.png"
        mask_png = td / "mask.png"
        headline_png = td / "headline.png"
        scrim_png = td / "scrim.png"

        (td / "frame.html").write_text(build_frame_html(spec, cv))
        screenshot(chrome, td / "frame.html", frame_png, CANVAS_W, CANVAS_H)

        (td / "mask.html").write_text(build_mask_html())
        screenshot(chrome, td / "mask.html", mask_png, VIDEO_W, VIDEO_H)

        (td / "scrim.html").write_text(build_scrim_html(cv))
        screenshot(chrome, td / "scrim.html", scrim_png, VIDEO_W, VIDEO_H)

        (td / "headline.html").write_text(build_headline_html(spec, cv))
        screenshot(chrome, td / "headline.html", headline_png, CANVAS_W, CANVAS_H)

        args.out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(args.source),
            "-i", str(frame_png),
            "-i", str(mask_png),
            "-i", str(headline_png),
            "-i", str(scrim_png),
            "-t", f"{duration:.3f}",
            "-filter_complex",
            f"[0:v]scale={VIDEO_W}:{VIDEO_H}:force_original_aspect_ratio=increase,"
            f"crop={VIDEO_W}:{VIDEO_H},setsar=1[vcrop];"
            f"[vcrop][4:v]overlay=0:0[vscrim];"
            f"[vscrim][2:v]alphamerge[vround];"
            f"[1:v][vround]overlay={VIDEO_X}:{VIDEO_Y}[vbase];"
            f"[vbase][3:v]overlay=0:0[vout]",
            "-map", "[vout]", "-map", "0:a:0?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(args.out),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not args.out.exists():
            raise SystemExit(f"ERROR: ffmpeg failed\n{result.stderr[-2000:]}")

    print(f"[video-cover] {duration:.2f}s, headline={cv['headline']!r} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
