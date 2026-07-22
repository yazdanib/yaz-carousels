#!/usr/bin/env python3
"""
fetch_fonts.py: Download a Google Fonts pairing and embed it as base64 CSS.

Produces a single fonts.css with @font-face rules pointing at data: URIs, so
the rendered slide HTML has zero external network dependency at screenshot
time (headless Chrome's screenshot mode does not reliably wait for a remote
font file to finish loading before it captures the page).

USAGE:
  python3 fetch_fonts.py --out fonts.css \
    --family "Fraunces:700" --family "Inter:400,600"

Each --family is "Name:weight1,weight2,...". Only latin-subset files are
kept (skips cyrillic/greek/vietnamese variants Google Fonts also serves).
"""

from __future__ import annotations

import argparse
import base64
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def parse_family_arg(arg: str) -> tuple[str, list[str]]:
    if ":" in arg:
        name, weights = arg.split(":", 1)
        return name.strip(), [w.strip() for w in weights.split(",") if w.strip()]
    return arg.strip(), ["400"]


def fetch_css(families: list[tuple[str, list[str]]]) -> str:
    parts = []
    for name, weights in families:
        parts.append(f"family={urllib.parse.quote(name)}:wght@{';'.join(weights)}")
    url = "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode()


def embed(css: str) -> str:
    """Keep only latin-subset @font-face blocks, download + base64 each,
    and rewrite src to a data: URI."""
    blocks = re.split(r"(/\*\s*[a-z0-9\- ]+\s*\*/)", css)
    out_blocks = []
    i = 1
    while i < len(blocks) - 1:
        comment = blocks[i].strip()
        block = blocks[i + 1]
        i += 2
        if "latin" not in comment or "latin-ext" in comment:
            continue
        m = re.search(r"url\((https://[^)]+)\)\s*format\('(\w+)'\)", block)
        if not m:
            continue
        font_url, fmt = m.group(1), m.group(2)
        req = urllib.request.Request(font_url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
        b64 = base64.b64encode(data).decode()
        mime = "font/woff2" if fmt == "woff2" else f"font/{fmt}"
        new_block = re.sub(
            r"url\(https://[^)]+\)\s*format\('\w+'\)",
            f"url(data:{mime};base64,{b64}) format('{fmt}')",
            block,
        )
        out_blocks.append(new_block.strip())
    return "\n".join(out_blocks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--family", action="append", required=True,
                     help='e.g. --family "Fraunces:700" (repeatable)')
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    families = [parse_family_arg(f) for f in args.family]
    print(f"[fetch_fonts] fetching {', '.join(n for n, _ in families)}...")
    raw_css = fetch_css(families)
    embedded = embed(raw_css)

    if not embedded.strip():
        print("ERROR: no latin @font-face blocks found, check family names", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(embedded)
    print(f"[fetch_fonts] -> {args.out} ({len(embedded) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
