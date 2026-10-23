#!/usr/bin/env python3
"""Force a visible top-right welcome audio player onto every deployable HTML page.

  python tools/top_right_welcome_audio.py --apply
  python tools/top_right_welcome_audio.py --check
  python tools/top_right_welcome_audio.py --selftest

- Uses /audio/colddirect-welcome.mp3 (owner British welcome script).
- Injects <!-- CD-TOP-RIGHT-AUDIO --> immediately after <body>.
- Inline <style id="cd-top-right-audio"> with !important so cache/layout cannot hide it.
- Always TOP-RIGHT on desktop and mobile (never docks to the bottom).
- Strips older CD-AUDIO-SITEWIDE-V1 blocks (superseded).
- Leaves CD-AUDIO-V1 money-hub blocks in place for schema/integrity, but hides them visually
  so only one player shows (the top-right welcome widget).
- Does NOT touch <title>, <meta description>, <h1>, canonicals, redirects, or sitemap.xml.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_seo_audio as gsa  # noqa: E402
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
MP3 = "/audio/colddirect-welcome.mp3"
STEM = "colddirect-welcome"
START, END = "<!-- CD-TOP-RIGHT-AUDIO -->", "<!-- /CD-TOP-RIGHT-AUDIO -->"
BLOCK_RX = re.compile(r"(?:\r?\n)?" + re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")
SITEWIDE_RX = re.compile(
    r"(?:\r?\n)?<!-- CD-AUDIO-SITEWIDE-V1 -->[\s\S]*?<!-- /CD-AUDIO-SITEWIDE-V1 -->(?:\r?\n)?"
)
# Hide the older full/money audio cards so only the top-right welcome player is visible.
HIDE_LEGACY = (
    "<style id=\"cd-hide-legacy-audio\">"
    "section.cd-audio-summary,.cd-audio-summary,.cd-audio-summary *{"
    "display:none !important;visibility:hidden !important;pointer-events:none !important;"
    "position:absolute !important;width:0 !important;height:0 !important;max-height:0 !important;"
    "overflow:hidden !important;clip:rect(0,0,0,0) !important;opacity:0 !important;"
    "}"
    "</style>"
)

SKIP_DIR_PARTS = {
    "node_modules", ".git", ".github", ".cursor", ".vscode", "tools", "docs", "agent",
    "scripts", "audio", "images", "css", "js", "assets", "backups", "App_Data", "logs",
    "__pycache__", "plesk-hero-upload", "plesk-upload", "_wa_src",
}

CSS = """<style id="cd-top-right-audio">
#cd-audio-dock,#cd-audio-dock *{box-sizing:border-box !important;}
#cd-audio-dock{
  position:fixed !important;
  top:52px !important;
  right:24px !important;
  left:auto !important;
  bottom:auto !important;
  z-index:2147483000 !important;
  width:min(310px, calc(100vw - 24px)) !important;
  margin:0 !important;
  padding:10px 12px !important;
  background:linear-gradient(145deg,#0a2540 0%,#0d3a5c 100%) !important;
  color:#fff !important;
  border:1px solid rgba(0,169,157,.65) !important;
  border-radius:12px !important;
  box-shadow:0 12px 32px rgba(10,37,64,.45) !important;
  font:600 12px/1.35 system-ui,Segoe UI,sans-serif !important;
  display:block !important;
  visibility:visible !important;
  opacity:1 !important;
}
#cd-audio-dock .cd-audio-label{
  display:block !important;margin:0 0 6px !important;color:#9fe8e1 !important;letter-spacing:.02em !important;
}
#cd-audio-dock audio{
  width:100% !important;height:36px !important;display:block !important;margin:0 !important;
  border-radius:8px !important;background:#fff !important;
}
#cd-audio-dock details{margin-top:6px !important;}
#cd-audio-dock summary{
  cursor:pointer !important;font-weight:700 !important;color:#fff !important;list-style:none !important;
}
#cd-audio-dock summary::-webkit-details-marker{display:none !important;}
#cd-audio-dock .cd-transcript-text{
  margin:6px 0 0 !important;font-weight:400 !important;font-size:11.5px !important;line-height:1.5 !important;opacity:.95 !important;
}
@media (max-width:768px){
  #cd-audio-dock{
    position:relative !important;
    top:auto !important;
    right:auto !important;
    left:auto !important;
    bottom:auto !important;
    width:calc(100% - 24px) !important;
    max-width:320px !important;
    margin:8px 12px 8px auto !important;
    z-index:20 !important;
    float:none !important;
  }
}
</style>"""

TRANSCRIPT = (
    "Welcome to Cold Direct. We are a North London-based company with over 30 years of experience "
    "in commercial refrigeration, walk-in cold rooms, all types of cooling equipment, ice machines, "
    "ice cream machines, and full air conditioning systems. All of our work comes with a full guarantee, "
    "24/7 emergency response, and fair, competitive pricing. After your very first experience "
    "with us, you will become a lifelong customer. We would be delighted to hear from you—give us a call "
    "today and put our 30 years of expertise to work for you."
)


def page_url_from_path(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        rel = path.resolve().relative_to(MIRROR).as_posix()
    if rel.startswith("colddirect-public-html/"):
        rel = rel[len("colddirect-public-html/") :]
    if rel in ("index.html",):
        return md.SITE + "/"
    if rel.endswith("/index.html"):
        return md.SITE + "/" + rel[: -len("/index.html")] + "/"
    if rel.endswith(".html"):
        return md.SITE + "/" + rel[: -len(".html")] + "/"
    return md.SITE + "/" + rel.strip("/") + "/"


def block_for(path: Path, duration_sec: float) -> str:
    url = page_url_from_path(path)
    mp3_abs = md.SITE + MP3
    graph = [
        {
            "@type": "WebPage",
            "@id": url + "#top-right-audio-page",
            "url": url,
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": ["#cd-audio-dock .cd-transcript-text", "h1"],
            },
        },
        {
            "@type": "AudioObject",
            "@id": url + "#top-right-audio",
            "name": "Cold Direct welcome — 30 years of commercial refrigeration in North London",
            "description": TRANSCRIPT,
            "contentUrl": mp3_abs,
            "encodingFormat": "audio/mpeg",
            "duration": gsa.iso_duration(duration_sec),
            "uploadDate": "2026-10-22",
            "inLanguage": "en-GB",
            "transcript": TRANSCRIPT,
            "publisher": {"@id": md.SITE + "/#business"},
        },
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False).replace(
        "</", "<\\/"
    )
    return "\n".join(
        [
            START,
            HIDE_LEGACY,
            CSS,
            '<aside id="cd-audio-dock" aria-label="Cold Direct welcome audio">',
            '<span class="cd-audio-label">Listen · Welcome to Cold Direct</span>',
            f'<audio controls preload="none" src="{MP3}"><source src="{MP3}" type="audio/mpeg">'
            "Your browser does not support audio playback.</audio>",
            f'<details><summary>Transcript</summary><p class="cd-transcript-text">{md.esc(TRANSCRIPT)}</p></details>',
            "</aside>",
            '<script type="application/ld+json" data-cd-schema="top-right-welcome-audio">',
            ld,
            "</script>",
            END,
        ]
    ) + "\n"


def iter_html_files() -> list[Path]:
    out = []
    for base in (ROOT, MIRROR):
        for p in base.rglob("*.html"):
            if any(part in SKIP_DIR_PARTS for part in p.parts):
                continue
            # skip google verification stubs
            if re.fullmatch(r"google[0-9a-z]+\.html", p.name, re.I):
                continue
            out.append(p)
    return sorted(set(out))


def inject(html: str, block: str) -> str:
    html = BLOCK_RX.sub("", html)
    html = SITEWIDE_RX.sub("", html)
    # Drop any prior hide-legacy style if re-applying
    html = re.sub(
        r"<style id=\"cd-hide-legacy-audio\">[\s\S]*?</style>\s*",
        "",
        html,
        flags=re.I,
    )
    nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"
    insert = nl + block.replace("\n", nl)
    # Prefer after header so mobile relative audio sits under phone numbers/logo.
    for pat in (
        r'(<!--#include virtual="/includes/header-nav\.inc" -->)',
        r"(</header>)",
        r'(<header class="site">[\s\S]*?</header>)',
    ):
        hm = re.search(pat, html, re.I)
        if hm:
            return html[: hm.end()] + insert + html[hm.end() :]
    m = re.search(r"<body([^>]*)>", html, re.I)
    if not m:
        raise ValueError("no <body>")
    return html[: m.end()] + insert + html[m.end() :]


def ensure_mp3() -> float:
    f = ROOT / "audio" / f"{STEM}.mp3"
    if not f.is_file():
        raise SystemExit("MISSING " + str(f) + " — run sitewide_welcome_audio.py --generate first")
    data = f.read_bytes()
    _, dur = gsa.mp3_info(data)
    mirror = MIRROR / "audio" / f.name
    mirror.parent.mkdir(parents=True, exist_ok=True)
    if not mirror.is_file() or mirror.read_bytes() != data:
        mirror.write_bytes(data)
    return dur


def apply() -> int:
    dur = ensure_mp3()
    changed = problems = 0
    for p in iter_html_files():
        old = p.read_bytes().decode("utf-8", errors="replace")
        # Skip tiny non-page files without body
        if "<body" not in old.lower():
            continue
        try:
            new = inject(old, block_for(p, dur))
        except ValueError as e:
            print("SKIP", p.relative_to(ROOT), e)
            problems += 1
            continue
        if new != old:
            p.write_bytes(new.encode("utf-8"))
            changed += 1
            print("updated", p.relative_to(ROOT))
    print("top-right welcome: %d files updated, problems=%d" % (changed, problems))
    return 1 if problems else 0


def check() -> int:
    dur = ensure_mp3()
    bad = 0
    for p in iter_html_files():
        old = p.read_bytes().decode("utf-8", errors="replace")
        if "<body" not in old.lower():
            continue
        if inject(old, block_for(p, dur)) != old:
            print("pending", p.relative_to(ROOT))
            bad += 1
        if 'id="cd-top-right-audio"' not in old or 'id="cd-audio-dock"' not in old:
            print("missing dock", p.relative_to(ROOT))
            bad += 1
        if "colddirect-welcome.mp3" not in old:
            print("missing mp3", p.relative_to(ROOT))
            bad += 1
    print("top-right welcome check:", "OK" if not bad else "%d problem(s)" % bad)
    return bad


def selftest() -> None:
    page = (
        '<html><head><title>T</title></head><body class="x">\n'
        '<!--#include virtual="/includes/header-nav.inc" --><h1>H</h1></body></html>'
    )
    blk = block_for(ROOT / "about-us" / "index.html", 40)
    once = inject(page, blk)
    assert inject(once, blk) == once
    assert once.index(START) > once.index("header-nav.inc")
    assert "max-width:768px" in once
    assert "position:relative !important" in once
    assert "top:52px" in once
    assert 'id="cd-top-right-audio"' in once and "!important" in once
    assert "bottom:auto !important" in once
    assert "colddirect-welcome.mp3" in once
    # Fallback: after </header> when SSI include is absent
    page2 = '<html><body><header class="site">nav</header><h1>H</h1></body></html>'
    once2 = inject(page2, blk)
    assert once2.index(START) > once2.index("</header>")
    # sitewide marker stripped
    dirty = page.replace("<body class=\"x\">", "<body class=\"x\"><!-- CD-AUDIO-SITEWIDE-V1 -->old<!-- /CD-AUDIO-SITEWIDE-V1 -->")
    clean = inject(dirty, blk)
    assert "CD-AUDIO-SITEWIDE-V1" not in clean
    print("top_right_welcome_audio selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        selftest()
    elif "--check" in a:
        sys.exit(1 if check() else 0)
    else:
        sys.exit(apply())
