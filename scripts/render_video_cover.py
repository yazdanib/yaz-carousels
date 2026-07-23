#!/usr/bin/env python3
"""
render_video_cover.py: Build a video cover slide (Style B), a source video,
cropped to the carousel's 4:5 frame, with a text headline and the handle/name
overlaid, inside a light frame border. This is slide 1 of a Style B carousel;
scripts/render_carousel.py still renders slides 2+ as normal PNGs.

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
      "position": "upper-left",    // upper-left, upper-center, center, lower-left
      "frame": true,               // white rounded border, like a polaroid edge
      "duration": null             // seconds to trim to, null = full source
    }
  }

WHY this is a separate script from render_carousel.py: that script only ever
produces a static image via a headless Chrome screenshot. A video cover needs
an actual video pipeline (crop, scale, mux), which means ffmpeg. Keeping this
in its own script means the plain PNG path never needs ffmpeg at all, only a
Style B carousel with a video cover does.

The text/frame overlay itself is still built the same way as every other
piece of text in this skill: an HTML page rendered by headless Chrome, this
time to a transparent PNG, which ffmpeg then composites onto the video in a
single pass. Not ffmpeg's drawtext, same rendering engine as everywhere else.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_carousel import CANVAS_W, CANVAS_H, SAFE_MARGIN, find_chrome, esc, render_badge  # noqa: E402


def probe_duration(path: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


POSITION_CSS = {
    "upper-left": "align-items:flex-start; justify-content:flex-start; text-align:left; padding-top:18%;",
    "upper-center": "align-items:center; justify-content:flex-start; text-align:center; padding-top:14%;",
    "center": "align-items:center; justify-content:center; text-align:center;",
    "lower-left": "align-items:flex-start; justify-content:flex-end; text-align:left; padding-bottom:16%;",
}


def build_overlay_html(spec: dict, cv: dict) -> str:
    pal = spec["palette"]
    fonts_css = Path(spec["fonts_css"]).read_text() if spec.get("fonts_css") else ""
    position = cv.get("position", "upper-left")
    pos_css = POSITION_CSS.get(position, POSITION_CSS["upper-left"])
    frame = cv.get("frame", True)
    text_color = cv.get("text_color", "#FFFFFF")
    shadow = "" if text_color.upper() == "#FFFFFF" else "text-shadow:0 2px 10px rgba(0,0,0,.35);"

    badge = render_badge(spec, text_color) if (spec.get("handle") or spec.get("logo")) else ""
    headline = esc(cv.get("headline", ""))

    frame_css = ""
    frame_html = ""
    if frame:
        frame_css = f"""
.frame{{ position:absolute; inset:22px; border:14px solid rgba(255,255,255,.92);
         border-radius:28px; box-sizing:border-box; }}
"""
        frame_html = '<div class="frame"></div>'

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
{fonts_css}
*{{ margin:0; padding:0; box-sizing:border-box; }}
html,body{{ width:{CANVAS_W}px; height:{CANVAS_H}px; overflow:hidden; background:transparent;
            font-family:'{spec.get("body_font","Inter")}',-apple-system,sans-serif; }}
.wrap{{ position:relative; width:100%; height:100%; }}
.pad{{ position:absolute; inset:0; padding:{SAFE_MARGIN}px; display:flex; flex-direction:column; {pos_css} }}
.badge{{ position:absolute; top:{SAFE_MARGIN}px; left:{SAFE_MARGIN}px; display:flex; align-items:center;
         gap:14px; color:{text_color}; {shadow} }}
.badge .names{{ display:flex; flex-direction:column; line-height:1.25; }}
.badge .handle{{ font-weight:700; font-size:24px; }}
.badge .display-name{{ font-size:19px; opacity:.85; }}
.badge img{{ width:52px; height:52px; border-radius:50%; object-fit:cover; }}
.headline{{ font-family:'{spec.get("headline_font","Fraunces")}',Georgia,serif; font-weight:700;
            font-size:{cv.get('headline_size', 84)}px; line-height:1.12; color:{text_color};
            max-width:80%; {shadow} }}
{frame_css}
</style></head>
<body>
<div class="wrap">
  {frame_html}
  {badge}
  <div class="pad"><div class="headline">{headline}</div></div>
</div>
</body></html>"""


def screenshot_overlay(chrome: str, html_path: Path, png_path: Path) -> None:
    abs_html = html_path.resolve()
    cmd = [
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--default-background-color=00000000",
        f"--window-size={CANVAS_W},{CANVAS_H}",
        f"--screenshot={png_path}",
        f"file://{abs_html}",
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    if not png_path.exists() or png_path.stat().st_size < 500:
        raise SystemExit(f"ERROR: overlay screenshot failed for {abs_html}")


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
        html_path = Path(td) / "overlay.html"
        png_path = Path(td) / "overlay.png"
        html_path.write_text(build_overlay_html(spec, cv))
        screenshot_overlay(chrome, html_path, png_path)

        args.out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", str(args.source),
            "-i", str(png_path),
            "-t", f"{duration:.3f}",
            "-filter_complex",
            f"[0:v]scale={CANVAS_W}:{CANVAS_H}:force_original_aspect_ratio=increase,"
            f"crop={CANVAS_W}:{CANVAS_H},setsar=1[base];"
            f"[base][1:v]overlay=0:0[vout]",
            "-map", "[vout]", "-map", "0:a?",
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
