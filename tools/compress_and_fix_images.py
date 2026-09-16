#!/usr/bin/env python3
"""Compress site images and point page content photos at professional /images/pro/ shots."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:\Users\khora\Documents\colddirect-website")
IMG_ROOT = ROOT / "colddirect-public-html" / "images"
HTML_ROOT = ROOT / "colddirect-public-html"
PRO = "/images/pro"

SKIP_DIR_NAMES = {"logo", "_restore"}
MAX_W = 1280
TARGET = 100 * 1024
MAX_KEEP = 80 * 1024

PRO_FILES = {
    "fridge_install": f"{PRO}/commercial-fridge-installation-london.webp",
    "fridge_maint": f"{PRO}/commercial-fridge-maintenance-london.webp",
    "fridge_clean": f"{PRO}/commercial-fridge-cleaning-service.webp",
    "freezer": f"{PRO}/commercial-freezer-repair-london.webp",
    "walkin_freezer": f"{PRO}/walk-in-freezer-installation.webp",
    "coldroom": f"{PRO}/walk-in-cold-room-maintenance.webp",
    "kitchen": f"{PRO}/commercial-kitchen-cold-room.webp",
    "service": f"{PRO}/commercial-refrigeration-service-london.webp",
    "display": f"{PRO}/display-fridge-repair-london.webp",
    "emergency": f"{PRO}/emergency-fridge-repair-london.webp",
    "catering_eq": f"{PRO}/catering-equipment-repair-london.webp",
    "catering_fr": f"{PRO}/catering-fridge-repair-london.webp",
}

GENERIC_SRC = {
    "cold-room.webp",
    "display-cabinets.webp",
    "pub-cellar.webp",
    "commercial-freezer-repair-london.webp",
    "commercial-fridge.webp",
    "commercial-freezer.webp",
    "bottle-cooler.webp",
    "homepage-hero-chiller.webp",
}


def compress_one(path: Path) -> str | None:
    if any(part in SKIP_DIR_NAMES for part in path.parts):
        return None
    try:
        size = path.stat().st_size
    except OSError:
        return None
    try:
        im = Image.open(path)
    except Exception as exc:
        return f"SKIP {path.name}: {exc}"
    w, h = im.size
    if size <= MAX_KEEP and w <= MAX_W:
        return None
    im = im.convert("RGB")
    if w > MAX_W:
        im = im.resize((MAX_W, int(h * MAX_W / w)), Image.Resampling.LANCZOS)
    ext = path.suffix.lower()
    quality = 80
    tmp = path.with_suffix(path.suffix + ".tmp")
    while quality >= 52:
        if ext in {".jpg", ".jpeg"}:
            im.save(tmp, "JPEG", quality=quality, optimize=True)
        else:
            im.save(tmp, "WEBP", quality=quality, method=6)
        if tmp.stat().st_size <= TARGET or quality <= 52:
            break
        quality -= 4
    new_size = tmp.stat().st_size
    if new_size >= size and w <= MAX_W:
        tmp.unlink(missing_ok=True)
        return None
    tmp.replace(path)
    return f"{path.relative_to(IMG_ROOT)}  {size/1024:.0f}KB -> {new_size/1024:.0f}KB  {im.size[0]}x{im.size[1]}"


def category(stem: str) -> str:
    s = stem.lower()
    if "catering" in s:
        return "catering"
    if any(k in s for k in ("freezer", "blast-freez", "blast-freezing")):
        return "freezer"
    if any(k in s for k in ("cold-room", "cold-storage", "walk-in-chiller", "walk-in-cold", "walk-in-fridge", "fridge-room", "chiller")):
        return "coldroom"
    if any(k in s for k in ("display", "multideck", "supermarket", "cabinet", "open-front", "dairy")):
        return "display"
    if s in {"contact", "index", "coverage", "write-a-review"}:
        return "emergency"
    if "ice-cream" in s:
        return "kitchen"
    if any(k in s for k in ("ice-machine", "hoshizaki")):
        return "kitchen"
    if any(k in s for k in ("fridge", "cooler", "bottle", "wine")):
        return "fridge"
    return "general"


def pool_for(cat: str) -> list[str]:
    return {
        "fridge": [PRO_FILES["fridge_install"], PRO_FILES["fridge_maint"], PRO_FILES["fridge_clean"], PRO_FILES["service"]],
        "freezer": [PRO_FILES["freezer"], PRO_FILES["walkin_freezer"], PRO_FILES["service"], PRO_FILES["emergency"]],
        "coldroom": [PRO_FILES["coldroom"], PRO_FILES["kitchen"], PRO_FILES["walkin_freezer"], PRO_FILES["service"]],
        "display": [PRO_FILES["display"], PRO_FILES["fridge_maint"], PRO_FILES["fridge_install"], PRO_FILES["service"]],
        "emergency": [PRO_FILES["emergency"], PRO_FILES["service"], PRO_FILES["fridge_install"]],
        "catering": [PRO_FILES["kitchen"], PRO_FILES["catering_eq"], PRO_FILES["catering_fr"], PRO_FILES["fridge_maint"]],
        "kitchen": [PRO_FILES["kitchen"], PRO_FILES["service"], PRO_FILES["fridge_install"]],
        "general": [PRO_FILES["service"], PRO_FILES["kitchen"], PRO_FILES["fridge_install"], PRO_FILES["coldroom"]],
    }[cat]


def src_filename(src: str) -> str:
    src = src.split("?")[0].replace("\\", "/")
    return Path(src).name.lower()


def should_remap(src: str, page_stem: str) -> bool:
    name = src_filename(src)
    if "/images/pro/" in src.replace("\\", "/"):
        return False
    if name in GENERIC_SRC:
        return True
    # Wrong pairing: bottle cooler on a display-fridge page
    if "display" in page_stem and name.startswith("bottle"):
        return True
    if "supermarket-freezer" in page_stem and "display-cabinet" in name:
        return True
    return False


def upgrade_tag(tag: str, page_stem: str, slot: list[int]) -> str:
    low = tag.lower()
    if "logo" in low or "favicon" in low or "apple-touch" in low:
        return tag
    src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag, re.I)
    if not src_m:
        return tag
    src = src_m.group(1)
    if should_remap(src, page_stem):
        pool = pool_for(category(page_stem))
        i = slot[0] % len(pool)
        slot[0] += 1
        tag = tag[: src_m.start(1)] + pool[i] + tag[src_m.end(1) :]
    if not re.search(r"\bclass=", tag, re.I):
        tag = re.sub(r"<img\b", '<img class="pro-image"', tag, count=1, flags=re.I)
    elif "pro-image" not in tag:
        tag = re.sub(r'\bclass=(["\'])', r"class=\1pro-image ", tag, count=1, flags=re.I)
    if not re.search(r"\bloading=", tag, re.I):
        tag = re.sub(r"<img\b", '<img loading="lazy"', tag, count=1, flags=re.I)
    return tag


def process_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    stem = path.stem
    if path.parent.name == "blog" and stem == "index":
        stem = "blog-index"
    slot = [0]
    new, n = re.subn(
        r"<img\b[^>]*>",
        lambda m: upgrade_tag(m.group(0), stem, slot),
        text,
        flags=re.I,
    )
    if new != text:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed_img = []
    for path in sorted(IMG_ROOT.rglob("*")):
        if path.suffix.lower() not in {".webp", ".jpg", ".jpeg", ".png"}:
            continue
        msg = compress_one(path)
        if msg:
            changed_img.append(msg)
    html_n = 0
    for path in sorted(HTML_ROOT.rglob("*.html")):
        if process_html(path):
            html_n += 1
    print("compressed", len(changed_img))
    for line in changed_img[:40]:
        print(" ", line)
    if len(changed_img) > 40:
        print(f"  ... {len(changed_img) - 40} more")
    print("html files updated", html_n)


if __name__ == "__main__":
    main()
