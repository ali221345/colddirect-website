from pathlib import Path
import hashlib
import re

ROOT = Path(r"C:\Users\khora\Documents\colddirect-website\colddirect-public-html")
CSS_LINK = '<link rel="stylesheet" href="/css/pro-images.css">'

CATALOG = [
    ("commercial-fridge-installation-london.webp", "Commercial fridge installation in a London restaurant kitchen"),
    ("commercial-freezer-repair-london.webp", "Commercial freezer repair in a London catering kitchen"),
    ("walk-in-cold-room-maintenance.webp", "Walk-in cold room maintenance for a London trade kitchen"),
    ("commercial-fridge-maintenance-london.webp", "Commercial fridge maintenance in a London restaurant"),
    ("emergency-fridge-repair-london.webp", "24/7 emergency commercial fridge repair callout in London"),
    ("commercial-fridge-cleaning-service.webp", "Commercial fridge cleaning service for London kitchens"),
    ("commercial-refrigeration-service-london.webp", "Cold Direct commercial refrigeration engineers in London"),
    ("walk-in-freezer-installation.webp", "Walk-in freezer installation for a London warehouse"),
    ("display-fridge-repair-london.webp", "Supermarket display fridge repair in London"),
    ("commercial-kitchen-cold-room.webp", "Luxury commercial kitchen cold room in London"),
]

POOLS = {
    "fridge": [0, 3, 5, 6],
    "freezer": [1, 7, 4, 6],
    "coldroom": [2, 9, 7, 6],
    "display": [8, 3, 0],
    "emergency": [4, 6, 0],
    "cleaning": [5, 3, 0],
    "kitchen": [9, 6, 0],
    "general": [6, 9, 0, 2, 1, 8, 4, 5],
}


def category(stem: str) -> str:
    s = stem.lower()
    if "clean" in s or "dishwasher" in s:
        return "cleaning"
    if s in {"contact", "index", "coverage", "write-a-review"} or "emergency" in s:
        return "emergency"
    if any(k in s for k in ("freezer", "blast-freez", "blast-freezing")):
        return "freezer"
    if any(
        k in s
        for k in (
            "cold-room",
            "cold-storage",
            "walk-in-chiller",
            "walk-in-cold",
            "walk-in-fridge",
            "fridge-room",
            "chiller",
        )
    ):
        return "coldroom"
    if any(
        k in s
        for k in ("display", "multideck", "supermarket", "cabinet", "open-front", "dairy")
    ):
        return "display"
    if any(k in s for k in ("ice-machine", "ice-cream", "catering", "kitchen")):
        return "kitchen"
    if any(k in s for k in ("fridge", "cooler", "bottle", "wine", "polar", "foster", "gram", "true", "empire", "adexa", "subzero", "williams")):
        return "fridge"
    return "general"


HERO = {
    "fridge": 0,
    "freezer": 1,
    "coldroom": 2,
    "display": 8,
    "emergency": 4,
    "cleaning": 5,
    "kitchen": 9,
    "general": 6,
}


def pick_three(stem: str) -> list[int]:
    cat = category(stem)
    hero = HERO[cat]
    pool = [i for i in POOLS[cat] if i != hero]
    seed = int(hashlib.md5(stem.encode()).hexdigest(), 16)
    rot = seed % max(len(pool), 1)
    rotated = pool[rot:] + pool[:rot] if pool else []
    extras = [i for i in POOLS["general"] if i not in {hero, *rotated}]
    ordered = [hero] + rotated + extras
    chosen = []
    for i in ordered:
        if i not in chosen:
            chosen.append(i)
        if len(chosen) == 3:
            break
    return chosen


def section_html(stem: str) -> str:
    idxs = pick_three(stem)
    imgs = []
    for i in idxs:
        file, alt = CATALOG[i]
        imgs.append(
            f'      <img src="/images/pro/{file}" alt="{alt}" class="pro-image" width="800" height="450" loading="lazy">'
        )
    grid = "\n".join(imgs)
    return (
        '<section class="pro-trust-section">\n'
        "  <div class=\"container\">\n"
        "    <h2>Trusted Commercial Refrigeration Experts in London</h2>\n"
        '    <div class="pro-image-grid">\n'
        f"{grid}\n"
        "    </div>\n"
        '    <p class="pro-trust-badge">✅ 500+ London Businesses Trust Cold Direct | 24/7 Emergency Callout</p>\n'
        "  </div>\n"
        "</section>\n"
    )


def ensure_css(html: str) -> str:
    if "css/pro-images.css" in html:
        return html
    if re.search(r"</head>", html, re.I):
        return re.sub(r"</head>", f"  {CSS_LINK}\n</head>", html, count=1, flags=re.I)
    return html


def inject(html: str, block: str) -> str:
    if 'class="pro-trust-section"' in html:
        html = re.sub(
            r'<section class="pro-trust-section">.*?</section>\s*',
            "",
            html,
            count=1,
            flags=re.S,
        )
    for marker in (
        r"<footer\b",
        r"<!--#include virtual=\"/includes/footer-services\.inc\" -->",
        r"</body>",
    ):
        m = re.search(marker, html, flags=re.I)
        if m:
            return html[: m.start()] + block + "\n" + html[m.start() :]
    return html + "\n" + block


def main() -> None:
    files = sorted(ROOT.rglob("*.html"))
    print("html files", len(files))
    cats = {}
    for path in files:
        stem = path.stem
        if path.parent.name == "blog" and stem == "index":
            stem = "blog-index"
        cat = category(stem)
        cats[cat] = cats.get(cat, 0) + 1
        text = path.read_text(encoding="utf-8")
        text = ensure_css(text)
        text = inject(text, section_html(stem))
        path.write_text(text, encoding="utf-8", newline="\n")
    print("categories", cats)


if __name__ == "__main__":
    main()
