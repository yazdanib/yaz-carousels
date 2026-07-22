#!/usr/bin/env python3
"""
pexels_photo.py: Search and download a vertical stock photo from Pexels, for
use as a slide's background_image in a carousel spec.

USAGE:
  python3 pexels_photo.py "person doing a pull up in a gym" --out slide-03.jpg

  # see a few options before downloading one:
  python3 pexels_photo.py "person doing a pull up in a gym" --list

WHY portrait orientation by default: this is built for a 1080x1350 (4:5)
carousel slide. Pass --orientation landscape or square if you need something
else, though a portrait source crops far more naturally into a 4:5 frame.

SELECTION: picks the highest-resolution portrait result from the top
matches, so there's plenty of source resolution to crop down from rather
than upscaling a small file.

ENV:
  PEXELS_API_KEY: required. pexels.com/api, free, no card needed. Same key
  as the yaz-video-editing skill's pexels_broll.py, if you already have one.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def load_api_key() -> str:
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        return key
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip().startswith("PEXELS_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
    raise SystemExit(
        "No Pexels key found. Set PEXELS_API_KEY in your shell or in a .env "
        "file in this folder. Get one free at pexels.com/api."
    )


# Pexels sits behind Cloudflare, which blocks urllib's default User-Agent
# ("Python-urllib/3.x") outright with a 403 (Cloudflare error 1010), before
# the request ever reaches Pexels or the API key is even checked. A normal
# browser User-Agent gets through fine.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def search(query: str, orientation: str, per_page: int, api_key: str) -> list[dict]:
    qs = urllib.parse.urlencode({
        "query": query,
        "orientation": orientation,
        "per_page": per_page,
    })
    url = f"https://api.pexels.com/v1/search?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": api_key, "User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return data.get("photos", [])


def best_src(photo: dict, orientation: str) -> str | None:
    w, h = photo.get("width", 0), photo.get("height", 0)
    if orientation == "portrait" and not (h > w):
        return None
    if orientation == "landscape" and not (w > h):
        return None
    srcs = photo.get("src", {})
    # "original" is full resolution; fall back down the chain if missing
    return srcs.get("original") or srcs.get("large2x") or srcs.get("large")


def download(url: str, out: Path) -> None:
    # urlretrieve can't set headers, and the image CDN sits behind the same
    # Cloudflare rules as the API, so this needs the same User-Agent fix.
    out.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        out.write_bytes(resp.read())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("query")
    ap.add_argument("--out", type=Path, help="where to save the downloaded photo")
    ap.add_argument("--orientation", default="portrait",
                     choices=["portrait", "landscape", "square"])
    ap.add_argument("--list", action="store_true",
                     help="print candidates instead of downloading")
    ap.add_argument("--per-page", type=int, default=8)
    args = ap.parse_args()

    api_key = load_api_key()
    photos = search(args.query, args.orientation, args.per_page, api_key)

    if not photos:
        print(f"[pexels_photo] no results for {args.query!r}", file=sys.stderr)
        return 1

    if args.list:
        print(f"[pexels_photo] {len(photos)} result(s) for {args.query!r}:")
        for p in photos:
            src = best_src(p, args.orientation)
            tag = f"{p['width']}x{p['height']}" if src else "no matching orientation"
            print(f"  id={p['id']:>9}  {tag}  photographer={p.get('photographer','')}  {p.get('url','')}")
        return 0

    for p in photos:
        src = best_src(p, args.orientation)
        if src:
            if not args.out:
                print(f"[pexels_photo] best match: id={p['id']} {p['width']}x{p['height']} {src}")
                print("[pexels_photo] pass --out <path> to download it")
                return 0
            print(f"[pexels_photo] downloading id={p['id']} {p['width']}x{p['height']} -> {args.out}")
            download(src, args.out)
            print(f"[pexels_photo] saved -> {args.out}")
            print(f"[pexels_photo] credit (not required by Pexels, but decent form): "
                  f"Photo by {p.get('photographer','')} on Pexels")
            return 0

    print(f"[pexels_photo] found results but none matched --orientation", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
