#!/usr/bin/env python3
"""Build the 1200x630 JPEG social preview image (og:image / twitter:image) from the homepage hero.

    python tools/make_og_image.py            # writes images/og-colddirect-london.jpg (+ the colddirect-public-html mirror)
    python tools/make_og_image.py --check    # verify the files exist, are identical, valid 1200x630 JPEGs < 300 KB

Source: images/commercial-refrigeration-kitchen-20261014.webp (1279x720, the live homepage hero).
The hero is centre-cropped to the 1.905:1 Open Graph ratio and resized with LANCZOS; JPEG (not WebP) because
Facebook / LinkedIn / WhatsApp / X crawlers render JPEG most reliably. Pure asset tooling - touches no HTML.
"""
import os
import shutil
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "images", "commercial-refrigeration-kitchen-20261014.webp")
NAME = "og-colddirect-london.jpg"
DEST = os.path.join(ROOT, "images", NAME)
MIRROR = os.path.join(ROOT, "colddirect-public-html", "images", NAME)
W, H = 1200, 630
MAX_BYTES = 300 * 1024


def jpeg_size(path):
    """(width, height) from the JPEG SOF marker, or None if the file is not a JPEG. No third-party libraries."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:3] != b"\xff\xd8\xff":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def check():
    problems = []
    for p in (DEST, MIRROR):
        rel = os.path.relpath(p, ROOT)
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            problems.append("%s missing or empty" % rel)
            continue
        if os.path.getsize(p) > MAX_BYTES:
            problems.append("%s is %d KB (> %d KB)" % (rel, os.path.getsize(p) // 1024, MAX_BYTES // 1024))
        if jpeg_size(p) != (W, H):
            problems.append("%s is not a %dx%d JPEG (%s)" % (rel, W, H, jpeg_size(p)))
    if not problems and open(DEST, "rb").read() != open(MIRROR, "rb").read():
        problems.append("root and mirror copies differ")
    return problems


def build():
    from PIL import Image
    im = Image.open(SRC).convert("RGB")
    sw, sh = im.size
    target = W / H
    if sw / sh > target:                      # too wide: crop the sides
        nw = int(round(sh * target))
        box = ((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh)
    else:                                     # too tall: crop top/bottom, keep a little more of the upper part
        nh = int(round(sw / target))
        top = max(0, int((sh - nh) * 0.4))
        box = (0, top, sw, top + nh)
    out = im.crop(box).resize((W, H), Image.LANCZOS)
    for q in (88, 85, 82, 78, 74):
        out.save(DEST, "JPEG", quality=q, optimize=True, progressive=True, subsampling=0 if q >= 85 else 2)
        if os.path.getsize(DEST) <= MAX_BYTES:
            break
    os.makedirs(os.path.dirname(MIRROR), exist_ok=True)
    shutil.copyfile(DEST, MIRROR)
    return (sw, sh), box, os.path.getsize(DEST)


def main():
    if "--check" in sys.argv:
        probs = check()
        print("og image: " + ("OK (%s, %dx%d, %d KB, mirror identical)" % (NAME, W, H, os.path.getsize(DEST) // 1024) if not probs
                              else "PROBLEMS: " + "; ".join(probs)))
        return 1 if probs else 0
    src, box, size = build()
    print("source %dx%d -> crop %s -> %dx%d JPEG, %d KB" % (src[0], src[1], box, W, H, size // 1024))
    probs = check()
    print("check: " + ("OK" if not probs else "; ".join(probs)))
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main())
