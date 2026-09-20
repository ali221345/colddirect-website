"""Pretty-URL routing helpers, JPEG fallbacks, .html -> trailing-slash links."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    "node_modules",
    "_wa_src",
    "plesk-upload",
    "plesk-hero-upload",
    "images",
    "public",
    "tools",
    "scripts",
    ".cursor",
    "_backup",
}
EXTS = {".html", ".inc", ".xml", ".php"}
HREF_RE = re.compile(r'(href=")(/[a-zA-Z0-9_./-]+)\.html(")', re.I)
LOC_RE = re.compile(
    r"(<loc>https://www\.colddirect\.co\.uk)(/[a-zA-Z0-9_./-]+)\.html(</loc>)",
    re.I,
)
CANON_RE = re.compile(
    r'(<link rel="canonical" href="https://www\.colddirect\.co\.uk)(/[a-zA-Z0-9_./-]+?)(?:\.html)?(">)',
    re.I,
)


def to_jpg_and_rewebp(src: Path, max_w: int = 1200) -> Path:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w > max_w:
        nh = int(h * max_w / w)
        im = im.resize((max_w, nh), Image.Resampling.LANCZOS)
    jpg = src.with_suffix(".jpg")
    im.save(jpg, "JPEG", quality=85, optimize=True)
    im.save(src, "WEBP", quality=80, method=6)
    rel = jpg.relative_to(ROOT)
    if rel.parts[0] != "colddirect-public-html":
        dest_jpg = ROOT / "colddirect-public-html" / rel
        dest_jpg.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(jpg, dest_jpg)
        shutil.copy2(src, dest_jpg.with_suffix(".webp"))
    print("converted", jpg, jpg.stat().st_size)
    return jpg


def convert_text(text: str) -> str:
    text = HREF_RE.sub(r"\1\2/\3", text)
    text = LOC_RE.sub(r"\1\2/\3", text)
    text = text.replace(
        "https://www.colddirect.co.uk/blog/index/",
        "https://www.colddirect.co.uk/blog/",
    )
    text = CANON_RE.sub(r"\1\2/\3", text)
    return text


def picture_for(src_webp: str, src_jpg: str, rest: str) -> str:
    return (
        f'<picture><source type="image/webp" srcset="{src_webp}?v=20260918j">'
        f'<img src="{src_jpg}?v=20260918j" {rest}</picture>'
    )


def patch_hero_imgs(text: str) -> str:
    replacements = [
        (
            r'<img([^>]*?)src="/images/catering-repair-london\.webp[^"]*"([^>]*)>',
            lambda m: picture_for(
                "/images/catering-repair-london.webp",
                "/images/catering-repair-london.jpg",
                (m.group(1) + m.group(2)).strip(),
            )
            if "src=" not in (m.group(1) + m.group(2))
            else picture_for(
                "/images/catering-repair-london.webp",
                "/images/catering-repair-london.jpg",
                (m.group(1) + m.group(2)).replace('src="/images/catering-repair-london.webp"', "").strip(),
            ),
        )
    ]
    # Simpler line-level replacements
    text = re.sub(
        r'<img([^>]*?)src="/images/catering-repair-london\.webp(?:\?[^"]*)?"([^>]*)>',
        r'<picture><source type="image/webp" srcset="/images/catering-repair-london.webp?v=20260918j"><img\1src="/images/catering-repair-london.jpg?v=20260918j"\2></picture>',
        text,
    )
    text = re.sub(
        r'<img([^>]*?)src="/images/dairy-cabinet-repair-london\.webp(?:\?[^"]*)?"([^>]*)>',
        r'<picture><source type="image/webp" srcset="/images/dairy-cabinet-repair-london.webp?v=20260918j"><img\1src="/images/dairy-cabinet-repair-london.jpg?v=20260918j"\2></picture>',
        text,
    )
    text = re.sub(
        r'<img([^>]*?)src="/images/logo/colddirect-main\.webp(?:\?[^"]*)?"([^>]*)>',
        r'<picture><source type="image/webp" srcset="/images/logo/colddirect-main.webp"><img\1src="/images/logo/colddirect-main.jpg"\2></picture>',
        text,
    )
    return text


def main() -> None:
    for rel in (
        "images/catering-repair-london.webp",
        "images/dairy-cabinet-repair-london.webp",
        "images/dairy-cabinet-repair.webp",
        "images/logo/colddirect-main.webp",
        "images/ice-machine-repair.webp",
    ):
        src = ROOT / rel
        if src.exists():
            to_jpg_and_rewebp(src)

    pub_ice = ROOT / "colddirect-public-html/images/ice-machine-repair-london.jpg"
    if pub_ice.exists():
        shutil.copy2(pub_ice, ROOT / "images/ice-machine-repair-london.jpg")

    changed = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        updated = patch_hero_imgs(convert_text(original))
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
            print("updated", path.relative_to(ROOT))
    print("files-with-updates", changed)

    sitemap = ROOT / "sitemap.xml"
    extra = (
        "  <url><loc>https://www.colddirect.co.uk/ice-o-matic-fridge-repairs/</loc>"
        "<lastmod>2026-09-18</lastmod></url>\n"
    )
    if sitemap.exists():
        body = sitemap.read_text(encoding="utf-8")
        if "ice-o-matic-fridge-repairs" not in body:
            body = body.replace("</urlset>", extra + "</urlset>")
            sitemap.write_text(body, encoding="utf-8", newline="\n")
            print("sitemap ice-o-matic added")
    pub_map = ROOT / "colddirect-public-html/sitemap.xml"
    if pub_map.exists():
        body = pub_map.read_text(encoding="utf-8")
        if "ice-o-matic-fridge-repairs" not in body:
            body = convert_text(body)
            if "ice-o-matic-fridge-repairs" not in body:
                body = body.replace("</urlset>", extra + "</urlset>")
            pub_map.write_text(body, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
