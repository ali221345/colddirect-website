#!/usr/bin/env python3
"""Sitewide British welcome voiceover for pages that do not already have CD-AUDIO-V1.

  python tools/sitewide_welcome_audio.py --generate   synth MP3 (edge-tts) + inject
  python tools/sitewide_welcome_audio.py --inject      reinject from existing MP3
  python tools/sitewide_welcome_audio.py --check
  python tools/sitewide_welcome_audio.py --selftest

Does NOT touch <title>, <meta description>, <h1>, canonicals, redirects, or sitemap.xml.
Money hubs + homepage keep their existing CD-AUDIO-V1 blocks (repositioned by generate_seo_audio.py).
Marker: <!-- CD-AUDIO-SITEWIDE-V1 -->. Shared asset: /audio/colddirect-welcome.mp3
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_seo_audio as gsa  # noqa: E402
import html_preflight as hp  # noqa: E402
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
STEM = "colddirect-welcome"
MP3_NAME = STEM + ".mp3"
UPLOAD_DATE = "2026-10-21"
VOICE, RATE = "en-GB-SoniaNeural", "-4%"

START, END = "<!-- CD-AUDIO-SITEWIDE-V1 -->", "<!-- /CD-AUDIO-SITEWIDE-V1 -->"
BLOCK_RX = re.compile(r"(?:\r?\n)?" + re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")

# Exact owner message (British English welcome for every page without a money-hub audio summary).
WELCOME_SCRIPT = (
    "Welcome to Cold Direct. We are a North London-based company with over 30 years of experience "
    "in commercial refrigeration, walk-in cold rooms, all types of cooling equipment, ice machines, "
    "ice cream machines, and full air conditioning systems. All of our work comes with a full guarantee, "
    "twenty four seven emergency response, and fair, competitive pricing. After your very first experience "
    "with us, you will become a lifelong customer. We would be delighted to hear from you — give us a call "
    "today and put our 30 years of expertise to work for you."
)
WELCOME_DISPLAY = (
    "Welcome to Cold Direct. We are a North London-based company with over 30 years of experience "
    "in commercial refrigeration, walk-in cold rooms, all types of cooling equipment, ice machines, "
    "ice cream machines, and full air conditioning systems. All of our work comes with a full guarantee, "
    "24/7 emergency response, and fair, competitive pricing. After your very first experience "
    "with us, you will become a lifelong customer. We would be delighted to hear from you—give us a call "
    "today and put our 30 years of expertise to work for you."
)

SKIP_DIRS = {
    "colddirect-public-html", "node_modules", "tools", "docs", "agent", "scripts",
    "audio", "images", "css", "js", "assets", "backups", "App_Data", "logs",
    "public", ".git", ".github", ".cursor", ".vscode",
}


def script_hash():
    return hashlib.sha256((WELCOME_SCRIPT + "|" + VOICE + "|" + RATE).encode()).hexdigest()


def page_url(slug: str) -> str:
    if slug in ("", "/"):
        return md.SITE + "/"
    if slug == "blog":
        return md.SITE + "/blog/"
    if slug.startswith("blog/"):
        return md.SITE + "/" + slug.strip("/") + "/"
    return md.SITE + "/" + slug.strip("/") + "/"


def copies_for(slug: str) -> list[Path]:
    """Root + mirror copies for a directory slug or blog path. Skip homepage/money hubs."""
    if slug in ("", "/"):
        return []
    if slug == "blog":
        return [p for p in (ROOT / "blog" / "index.html", MIRROR / "blog" / "index.html") if p.is_file()]
    if slug.startswith("blog/"):
        rest = slug[5:]
        if rest in ("", "index"):
            return copies_for("blog")
        paths = []
        for base in (ROOT, MIRROR):
            flat = base / "blog" / (rest + ".html")
            folder = base / "blog" / rest / "index.html"
            if flat.is_file():
                paths.append(flat)
            if folder.is_file():
                paths.append(folder)
        return paths
    out = []
    for base in (ROOT, MIRROR):
        for p in (base / f"{slug}.html", base / slug / "index.html"):
            if p.is_file():
                out.append(p)
    return out


def eligible_slugs() -> list[str]:
    """Canonical directory + blog pages that need sitewide audio (no CD-AUDIO-V1 yet)."""
    found = []
    for d in sorted(ROOT.iterdir()):
        if not d.is_dir() or d.name in SKIP_DIRS or d.name.startswith((".", "_")):
            continue
        idx = d / "index.html"
        if not idx.is_file():
            continue
        html = idx.read_text(encoding="utf-8", errors="replace")
        if "CD-AUDIO-V1" in html:
            continue
        if hp.is_noindex(html) or hp.is_redirect_stub(html):
            continue
        if not re.search(r"<h1\b", html, re.I):
            continue
        found.append(d.name)
    blog = ROOT / "blog"
    if blog.is_dir():
        seen = set()
        candidates = list(blog.glob("*.html")) + [
            p / "index.html" for p in blog.iterdir() if p.is_dir() and (p / "index.html").is_file()
        ]
        for path in candidates:
            html = path.read_text(encoding="utf-8", errors="replace")
            if "CD-AUDIO-V1" in html or "CD-AUDIO-SITEWIDE-V1" in html:
                # still include if only sitewide (for reinject); skip money-style hub audio
                pass
            if "CD-AUDIO-V1" in html:
                continue
            if hp.is_noindex(html) or hp.is_redirect_stub(html):
                continue
            if not re.search(r"<h1\b", html, re.I):
                continue
            if path.name == "index.html" and path.parent.name == "blog":
                slug = "blog"
            elif path.name == "index.html":
                slug = "blog/" + path.parent.name
            elif path.parent.name == "blog":
                slug = "blog/" + path.stem
            else:
                continue
            if slug in seen:
                continue
            seen.add(slug)
            found.append(slug)
    # Deduplicate: top-level "blog" dir and blog/index.html are the same hub.
    return sorted(set(found), key=lambda s: (s != "blog", s))


def audio_block(slug: str, duration_sec: float) -> str:
    url = page_url(slug)
    mp3 = f"{md.SITE}/audio/{MP3_NAME}"
    graph = [
        {
            "@type": "WebPage",
            "@id": url + "#welcome-audio-page",
            "url": url,
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".cd-audio-summary .cd-transcript-text", "h1"],
            },
        },
        {
            "@type": "AudioObject",
            "@id": url + "#welcome-audio",
            "name": "Cold Direct welcome — 30 years of commercial refrigeration in North London",
            "description": WELCOME_DISPLAY,
            "contentUrl": mp3,
            "encodingFormat": "audio/mpeg",
            "duration": gsa.iso_duration(duration_sec),
            "uploadDate": UPLOAD_DATE,
            "inLanguage": "en-GB",
            "transcript": WELCOME_DISPLAY,
            "publisher": {"@id": md.SITE + "/#business"},
        },
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False).replace(
        "</", "<\\/"
    )
    return "\n".join(
        [
            START,
            '<aside class="cd-audio-summary" aria-label="Cold Direct welcome audio">',
            gsa.CSS,
            '<div class="cd-audio-wrap">',
            '<span class="cd-audio-label">Listen · Welcome to Cold Direct</span>',
            f'<audio controls preload="none" src="/audio/{MP3_NAME}">'
            f'<source src="/audio/{MP3_NAME}" type="audio/mpeg">'
            "Your browser does not support audio playback.</audio>",
            f'<details class="cd-transcript"><summary>Transcript</summary>'
            f'<p class="cd-transcript-text">{md.esc(WELCOME_DISPLAY)}</p></details>',
            "</div>",
            "</aside>",
            '<script type="application/ld+json" data-cd-schema="welcome-audio">',
            ld,
            "</script>",
            END,
        ]
    ) + "\n"


def inject(html: str, block: str) -> str:
    html = BLOCK_RX.sub("", html)
    h1 = re.search(r"</h1>", html, re.I)
    if not h1:
        raise ValueError("no </h1>")
    # Prefer end of the first section after H1 (hero), else right after H1.
    sec = re.search(r"</section>", html[h1.end() :], re.I)
    pos = h1.end() + sec.end() if sec else h1.end()
    nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"
    return html[:pos] + nl + block.replace("\n", nl) + html[pos:]


async def _synth(out: Path):
    import edge_tts

    await edge_tts.Communicate(WELCOME_SCRIPT, VOICE, rate=RATE).save(str(out))


def ensure_mp3(do_synth: bool) -> tuple[Path, float]:
    out = ROOT / "audio" / MP3_NAME
    man_path = ROOT / "tools" / "audio_manifest.json"
    man = json.loads(man_path.read_text("utf-8")) if man_path.is_file() else {}
    h = script_hash()
    if do_synth and (not out.is_file() or man.get(STEM, {}).get("hash") != h):
        out.parent.mkdir(exist_ok=True)
        asyncio.run(_synth(out))
        print("synthesised", out.name)
    if not out.is_file():
        raise SystemExit("MISSING " + str(out))
    data = out.read_bytes()
    br, dur = gsa.mp3_info(data)
    man[STEM] = {
        "hash": h,
        "bytes": len(data),
        "duration_s": round(dur, 1),
        "bitrate_kbps": br,
        "voice": VOICE,
        "kind": "sitewide-welcome",
    }
    man_path.write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", "utf-8")
    mirror = MIRROR / "audio" / MP3_NAME
    mirror.parent.mkdir(parents=True, exist_ok=True)
    if not mirror.is_file() or mirror.read_bytes() != data:
        mirror.write_bytes(data)
        print("mirrored", mirror.relative_to(ROOT))
    return out, dur


def generate(do_synth: bool) -> int:
    _, dur = ensure_mp3(do_synth)
    slugs = eligible_slugs()
    changed = 0
    problems = 0
    for slug in slugs:
        block = audio_block(slug, dur)
        paths = copies_for(slug)
        if not paths:
            print("NO COPIES", slug)
            problems += 1
            continue
        for p in paths:
            # Never overwrite a money-hub CD-AUDIO-V1 page with sitewide audio.
            old = p.read_bytes().decode("utf-8")
            if "CD-AUDIO-V1" in old:
                continue
            try:
                new = inject(old, block)
            except ValueError as e:
                print("SKIP", p.relative_to(ROOT), e)
                problems += 1
                continue
            if new != old:
                p.write_bytes(new.encode("utf-8"))
                print("injected", p.relative_to(ROOT))
                changed += 1
    print("sitewide welcome: %d file(s) updated, %d slug(s), problems=%d" % (changed, len(slugs), problems))
    return 1 if problems else 0


def check() -> int:
    bad = 0
    f = ROOT / "audio" / MP3_NAME
    if not f.is_file():
        print("MISSING", f)
        return 1
    try:
        br, dur = gsa.mp3_info(f.read_bytes())
    except ValueError as e:
        print("INVALID", f, e)
        return 1
    if not (MIRROR / "audio" / MP3_NAME).is_file():
        print("MIRROR MISSING", MP3_NAME)
        bad += 1
    for slug in eligible_slugs():
        block = audio_block(slug, dur)
        for p in copies_for(slug):
            old = p.read_bytes().decode("utf-8")
            if "CD-AUDIO-V1" in old:
                continue
            if inject(old, block) != old:
                print("pending", p.relative_to(ROOT))
                bad += 1
    print("sitewide welcome check:", "OK" if not bad else "%d problem(s)" % bad)
    return bad


def selftest() -> None:
    assert "24/7" in WELCOME_DISPLAY and "thirty" not in WELCOME_DISPLAY.lower()
    page = (
        '<html><head><title>T</title></head><body><section class="hero"><h1>Hello</h1>'
        "</section>\n<section>body</section></body></html>"
    )
    blk = audio_block("ice-machine-repair-london", 55.2)
    once = inject(page, blk)
    assert inject(once, blk) == once and once.count(START) == 1
    assert "cd-audio-summary" in once and 'position:fixed' in once
    assert once.index(START) > once.index("</h1>")
    m = re.search(
        r'<script type="application/ld\+json" data-cd-schema="welcome-audio">\s*([\s\S]*?)</script>', once
    )
    j = json.loads(m.group(1))
    assert [n["@type"] for n in j["@graph"]] == ["WebPage", "AudioObject"]
    assert j["@graph"][1]["contentUrl"].endswith("/audio/colddirect-welcome.mp3")
    assert j["@graph"][1]["duration"] == "PT55S"
    # money-hub marker must not be stripped by sitewide inject
    with_money = page.replace("</section>", "<!-- CD-AUDIO-V1 -->x<!-- /CD-AUDIO-V1 --></section>", 1)
    # eligible_slugs skips CD-AUDIO-V1 pages; inject itself only removes SITEWIDE marker
    assert "CD-AUDIO-V1" in inject(with_money + START + "old" + END, blk)
    print("sitewide_welcome_audio selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        selftest()
    elif "--check" in a:
        sys.exit(1 if check() else 0)
    elif "--inject" in a:
        sys.exit(generate(False))
    else:
        sys.exit(generate(True))
