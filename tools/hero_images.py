#!/usr/bin/env python3
"""Make resized WebP copies of hero images so phones do not download the full-size file.

build.py picks these up automatically: for assets/img/NAME.ext it looks for
assets/img/NAME-<width>.webp and lists whatever it finds in the hero <img srcset>.

Run after adding or replacing a hero photo (needs Pillow: pip install Pillow):

    python3 tools/hero_images.py                 # homepage + every lounge page hero
    python3 tools/hero_images.py lounge-chairs.webp iv-bags.webp

Originals are never changed.
"""
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "docs", "assets", "img")
WIDTHS = (800, 1200, 1600)
QUALITY = 72


def default_images():
    src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
    lounges = src[src.index("LOCATIONS = ["):src.index("LOC_BY")]
    return ["nurse-iv-lounge.jpg"] + sorted(set(re.findall(r'img="([^"]+)"', lounges)))


def make(name):
    path = os.path.join(IMG_DIR, name)
    im = Image.open(path).convert("RGB")
    w, h = im.size
    widths = [x for x in WIDTHS if x <= w]
    if w < WIDTHS[-1] and w not in widths:
        widths.append(w)            # small original: keep one copy at its own width
    stem = os.path.splitext(name)[0]
    for old in os.listdir(IMG_DIR):  # drop copies from an earlier original
        if re.fullmatch(re.escape(stem) + r"-\d+\.webp", old):
            os.remove(os.path.join(IMG_DIR, old))
    out = []
    for x in widths:
        dest = os.path.join(IMG_DIR, f"{stem}-{x}.webp")
        im.resize((x, round(h * x / w)), Image.LANCZOS).save(dest, "WEBP", quality=QUALITY, method=6)
        out.append(f"{x}w {os.path.getsize(dest) // 1024} KB")
    print(f"{name} ({w}x{h}, {os.path.getsize(path) // 1024} KB) -> " + ", ".join(out))


if __name__ == "__main__":
    for image in sys.argv[1:] or default_images():
        make(image)
