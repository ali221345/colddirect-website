#!/usr/bin/env python3
"""Inject CD-INTERNAL-ANCHOR-MESH-V5 on supporting (non-money) pages.

Links into the 9 money hubs with rotated high-intent anchors. Canonical trailing-slash URLs only.

  python tools/internal_anchor_mesh_v5.py --apply | --check | --selftest
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
START, END = "<!-- CD-INTERNAL-ANCHOR-MESH-V5 -->", "<!-- /CD-INTERNAL-ANCHOR-MESH-V5 -->"
BLOCK_RX = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")

MONEY_SLUGS = set(md.MONEY) | {""}  # homepage treated separately as money target, not mesh source skip by slug
SKIP_SLUGS = set(md.MONEY) | {
    "index",
    "about",
    "news",  # redirect stubs often thin
}
SKIP_DIR_PARTS = {
    "node_modules", ".git", ".github", ".cursor", ".vscode", "tools", "docs", "agent",
    "scripts", "audio", "images", "css", "js", "assets", "backups", "App_Data", "logs",
    "__pycache__", "plesk-hero-upload", "plesk-upload", "_wa_src",
}

# Rotating high-intent anchors per hub (exact + partial match).
ANCHORS = {
    "commercial-fridge-repair-london": [
        "same day commercial fridge repairs London",
        "emergency commercial fridge repair London",
        "cheap commercial fridge repair & servicing London",
        "24/7 commercial fridge repairs & services London",
    ],
    "fridge-repair-london": [
        "London fridge repair",
        "same day fridge repairs London",
        "emergency fridge repair service London",
        "24/7 fridge repair near me London",
    ],
    "commercial-freezer-repair-london": [
        "24/7 commercial freezer repairs & services London",
        "same day commercial freezer repair London",
        "emergency commercial freezer repair London",
        "affordable commercial freezer service London",
    ],
    "freezer-repair-london": [
        "same day freezer repairs London",
        "emergency freezer repair London",
        "cheap freezer repair London",
        "London freezer service",
    ],
    "cold-room-repair-london": [
        "emergency cold room repair service London",
        "same day cold room repairs London",
        "24/7 cold room repair London",
        "cheap cold room service London",
    ],
    "catering-repair-london": [
        "catering equipment repair services London",
        "same day catering repair London",
        "emergency catering refrigeration repair London",
        "affordable catering service London",
    ],
    "commercial-appliances-repair-london": [
        "commercial catering repair services London",
        "24/7 commercial appliances repair London",
        "same day commercial catering repair London",
        "commercial appliance engineers London",
    ],
    "air-conditioning-repair-london": [
        "air conditioning service & emergency repairs London",
        "same day air conditioning repair London",
        "24/7 commercial AC service London",
        "cheap air conditioning repairs London",
    ],
    "cellar-cooler-repair-london": [
        "cellar cooler repair services London",
        "same day cellar cooler repair London",
        "emergency pub cellar cooling repair London",
        "beer cellar cooler service London",
    ],
}

INSERT_BEFORE = [
    r"<!-- CD-BLOG-MONEY-LINKS-V1 -->",
    r"<!-- CD-9-MONEY-KEYWORD-SILO-V47 -->",
    r"<!-- CD-LINK-BOOST-",
    r"<footer\b",
    r"</body>",
]

CSS = (
    "<style>.cd-anchor-mesh-v5{max-width:1140px;margin:24px auto;padding:18px 16px;background:#f1f7ff;"
    "border:1px solid #dbeafe;border-radius:10px}.cd-anchor-mesh-v5 h2{margin:0 0 8px;font-size:18px;color:#0a2540}"
    ".cd-anchor-mesh-v5 ul{margin:0;padding-left:18px}.cd-anchor-mesh-v5 li{margin:4px 0;line-height:1.45}"
    ".cd-anchor-mesh-v5 a{color:#0369a1;font-weight:600}</style>"
)


def page_slug(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        rel = path.resolve().relative_to(MIRROR).as_posix()
    if rel.startswith("colddirect-public-html/"):
        rel = rel[len("colddirect-public-html/") :]
    if rel in ("index.html",):
        return "index"
    if rel.endswith("/index.html"):
        return rel[: -len("/index.html")]
    if rel.endswith(".html"):
        return rel[: -len(".html")]
    return rel


def is_mesh_target(path: Path) -> bool:
    if any(part in SKIP_DIR_PARTS for part in path.parts):
        return False
    if path.suffix.lower() != ".html":
        return False
    if re.fullmatch(r"google[0-9a-z]+\.html", path.name, re.I):
        return False
    if path.name.startswith("_"):
        return False
    slug = page_slug(path)
    # skip money hubs and homepage (they get TOP3 booster instead)
    if slug in md.MONEY or slug == "index":
        return False
    # skip noindex / redirect stubs
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if re.search(r'name=["\']robots["\'][^>]*noindex', text, re.I):
        return False
    if re.search(r'http-equiv=["\']refresh["\']', text, re.I):
        return False
    return True


def variant(seed: str) -> int:
    return sum(map(ord, seed)) % 4


def block_for(seed: str) -> str:
    v = variant(seed)
    items = []
    # rotate hub order by seed
    hubs = list(md.HUB_ORDER)
    rot = v % len(hubs)
    hubs = hubs[rot:] + hubs[:rot]
    for i, slug in enumerate(hubs):
        anchors = ANCHORS[slug]
        a = anchors[(v + i) % len(anchors)]
        items.append(f'<li><a href="/{slug}/">{md.esc(a)}</a></li>')
    return "\n".join(
        [
            START,
            '<section class="cd-anchor-mesh-v5" aria-label="London commercial refrigeration repair services">',
            CSS,
            "<h2>Related London commercial repair &amp; service hubs</h2>",
            "<ul>",
            *items,
            "</ul>",
            "</section>",
            END,
        ]
    ) + "\n"


def inject(html: str, block: str) -> str:
    html = BLOCK_RX.sub("", html)
    for pat in INSERT_BEFORE:
        m = re.search(pat, html, re.I)
        if m:
            nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"
            return html[: m.start()] + block.replace("\n", nl) + html[m.start() :]
    raise ValueError("no insertion point")


def iter_targets() -> list[Path]:
    out, seen = [], set()
    for base in (ROOT, MIRROR):
        for p in base.rglob("*.html"):
            if not is_mesh_target(p):
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
    return sorted(out)


def run(apply: bool) -> int:
    pending = 0
    targets = iter_targets()
    for p in targets:
        seed = page_slug(p)
        old = p.read_bytes().decode("utf-8")
        try:
            new = inject(old, block_for(seed))
        except ValueError:
            print("SKIP no-insert", p.relative_to(ROOT).as_posix())
            continue
        if new != old:
            pending += 1
            if apply:
                p.write_bytes(new.encode("utf-8"))
    print(f"anchor-mesh targets={len(targets)} pending={pending} apply={apply}")
    return pending


def selftest() -> None:
    b = block_for("blog/test")
    assert START in b and "/cold-room-repair-london/" in b
    assert "/fridge-repair-london/" in b and "London" in b
    assert "</a></li>" in b
    assert all(f'href="/{s}/")' in b.replace("'", '"') or f'href="/{s}/"' in b for s in md.HUB_ORDER)
    assert "London fridge repair" in ANCHORS["fridge-repair-london"]
    assert "London freezer service" in ANCHORS["freezer-repair-london"]
    assert "beer cellar cooler service London" in ANCHORS["cellar-cooler-repair-london"]
    assert "commercial appliance engineers London" in ANCHORS["commercial-appliances-repair-london"]
    print("internal_anchor_mesh_v5 selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check" in sys.argv:
        sys.exit(1 if run(False) else 0)
    elif "--apply" in sys.argv:
        run(True)
        selftest()
    else:
        print("Usage: --apply | --check | --selftest")
        sys.exit(2)
