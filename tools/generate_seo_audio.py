#!/usr/bin/env python3
"""Spoken audio summaries for the 9 money hubs + homepage (idempotent, deterministic).

  python tools/generate_seo_audio.py --generate   synthesise missing/changed MP3s (edge-tts) + inject HTML/schema
  python tools/generate_seo_audio.py --inject     only (re)inject HTML + JSON-LD from existing MP3s (offline)
  python tools/generate_seo_audio.py --check      read-only: files exist/valid, blocks present in all copies
  python tools/generate_seo_audio.py --selftest

MP3s go to /audio/ (root = production, mirrored into colddirect-public-html/audio/).
Text comes from tools/money_data.py (script + hash in tools/audio_manifest.json: unchanged text => no re-synthesis).
Injected per page (marker `<!-- CD-AUDIO-V1 -->`): HTML5 <audio controls preload="none">, a transcript <details>,
and JSON-LD WebPage+SpeakableSpecification and AudioObject. Offline: existing MP3s are reused; nothing breaks.
"""
import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIRROR = ROOT / "colddirect-public-html"
MANIFEST = ROOT / "tools" / "audio_manifest.json"
VOICE, RATE = "en-GB-SoniaNeural", "-4%"
UPLOAD_DATE = "2026-10-21"

START, END = "<!-- CD-AUDIO-V1 -->", "<!-- /CD-AUDIO-V1 -->"
BLOCK_RX = re.compile(r"(?:\r?\n)?" + re.escape(START) + r"[\s\S]*?" + re.escape(END) + r"(?:\r?\n)?")
SPOKEN_PHONE = "zero seven nine eight three, seven five nine, three two zero"

# Compact floating player: top-right on desktop, bottom dock on small screens (does not cover H1/CTAs).
CSS = (
    "<style>"
    ".cd-audio-summary{position:fixed;top:max(72px,calc(env(safe-area-inset-top,0px)+64px));"
    "right:max(12px,calc(env(safe-area-inset-right,0px)+12px));z-index:95;"
    "width:min(300px,calc(100vw - 24px));background:linear-gradient(145deg,#0a2540 0%,#0d3a5c 100%);"
    "color:#fff;padding:10px 12px;border-radius:12px;box-shadow:0 10px 28px rgba(10,37,64,.38);"
    "border:1px solid rgba(0,169,157,.5);font:600 12px/1.35 system-ui,Segoe UI,sans-serif}"
    ".cd-audio-summary .cd-audio-wrap{margin:0;padding:0;max-width:none}"
    ".cd-audio-summary .cd-audio-label{display:block;margin:0 0 6px;letter-spacing:.02em;color:#9fe8e1}"
    ".cd-audio-summary audio{width:100%;height:32px;display:block;margin:0;border-radius:8px}"
    ".cd-audio-summary details{margin-top:6px}"
    ".cd-audio-summary summary{cursor:pointer;font-weight:700;color:#fff;list-style:none}"
    ".cd-audio-summary summary::-webkit-details-marker{display:none}"
    ".cd-audio-summary .cd-transcript-text{margin:6px 0 0;line-height:1.5;font-weight:400;font-size:11.5px;opacity:.95}"
    "@media (max-width:720px){.cd-audio-summary{top:auto;bottom:max(12px,env(safe-area-inset-bottom,0px));"
    "right:12px;left:12px;width:auto;max-width:none}}"
    "</style>"
)


def pages():
    return md.audio_pages()


def copies(slug):
    if slug == "":
        return [ROOT / "index.html", MIRROR / "index.html"]
    return [ROOT / f"{slug}.html", ROOT / slug / "index.html", MIRROR / f"{slug}.html", MIRROR / slug / "index.html"]


def page_url(slug):
    return md.SITE + "/" + (slug + "/" if slug else "")


def display_text(script):
    t = script.replace(SPOKEN_PHONE, md.PHONE_DISPLAY).replace("twenty four seven", "24/7").replace("twenty four hours a day, seven days a week", "24 hours a day, 7 days a week")
    return t.replace("twenty four hour", "24 hour")


def script_hash(script):
    return hashlib.sha256((script + "|" + VOICE + "|" + RATE).encode()).hexdigest()


# ---- MP3 inspection (CBR frame header) ----
_BR1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
_BR2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]


def mp3_info(data):
    """Return (bitrate_kbps, duration_seconds) or raise ValueError."""
    i = 0
    if data[:3] == b"ID3":
        size = (data[6] << 21) | (data[7] << 14) | (data[8] << 7) | data[9]
        i = 10 + size
    while i + 4 < len(data):
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            ver = (data[i + 1] >> 3) & 3
            layer = (data[i + 1] >> 1) & 3
            bi = data[i + 2] >> 4
            if ver != 1 and layer == 1 and 0 < bi < 15:
                br = (_BR1 if ver == 3 else _BR2)[bi]
                return br, (len(data) - i) * 8 / (br * 1000.0)
        i += 1
    raise ValueError("no MP3 frame found")


def iso_duration(sec):
    sec = max(1, int(round(sec)))
    m, s = divmod(sec, 60)
    return "PT" + (f"{m}M" if m else "") + f"{s}S"


# ---- HTML ----
def audio_block(slug, stem, name, script, duration_sec):
    url = page_url(slug)
    mp3 = f"{md.SITE}/audio/{stem}.mp3"
    text = display_text(script)
    graph = [
        {"@type": "WebPage", "@id": url + "#audio-page", "url": url,
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".cd-audio-summary .cd-transcript-text", "h1"]}},
        {"@type": "AudioObject", "@id": url + "#audio", "name": name, "description": text,
         "contentUrl": mp3, "encodingFormat": "audio/mpeg", "duration": iso_duration(duration_sec),
         "uploadDate": UPLOAD_DATE, "inLanguage": "en-GB", "transcript": text,
         "publisher": {"@id": md.SITE + "/#business"}},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False).replace("</", "<\\/")
    return "\n".join([
        START,
        '<section class="cd-audio-summary" aria-label="Audio summary">',
        CSS,
        '<div class="cd-audio-wrap">',
        '<span class="cd-audio-label">Listen · Cold Direct</span>',
        f'<audio controls preload="none" src="/audio/{stem}.mp3"><source src="/audio/{stem}.mp3" type="audio/mpeg">Your browser does not support audio playback.</audio>',
        f'<details class="cd-transcript"><summary>Transcript</summary><p class="cd-transcript-text">{md.esc(text)}</p></details>',
        "</div>",
        "</section>",
        '<script type="application/ld+json" data-cd-schema="audio-speakable">',
        ld,
        "</script>",
        END,
    ]) + "\n"


def inject(html, block):
    html = BLOCK_RX.sub("", html)
    h1 = re.search(r"</h1>", html, re.I)
    if not h1:
        raise ValueError("no <h1>")
    sec = re.search(r"</section>", html[h1.end():], re.I)
    pos = h1.end() + sec.end() if sec else h1.end()
    nl = "\r\n" if html.count("\r\n") * 2 > html.count("\n") else "\n"  # keep the file's own line-ending style
    return html[:pos] + nl + block.replace("\n", nl) + html[pos:]


def read(p):
    return p.read_bytes().decode("utf-8")


# ---- synthesis ----
async def _synth(script, out):
    import edge_tts
    await edge_tts.Communicate(script, VOICE, rate=RATE).save(str(out))


def synth(script, out):
    asyncio.run(_synth(script, out))


def load_manifest():
    return json.loads(MANIFEST.read_text("utf-8")) if MANIFEST.exists() else {}


def generate(do_synth):
    man = load_manifest()
    problems = 0
    for slug, stem, name, script in pages():
        f = ROOT / "audio" / f"{stem}.mp3"
        h = script_hash(script)
        new_hash, synthed = h, False
        if do_synth and (not f.exists() or man.get(stem, {}).get("hash") != h):
            f.parent.mkdir(exist_ok=True)
            try:
                synth(script, f)
                synthed = True
                print("synthesised", f.name)
            except Exception as e:  # network/edge-tts failure: keep any existing file, never break the build
                print("WARN synth failed for", stem, "-", type(e).__name__, str(e)[:120])
        if not f.exists():
            print("MISSING audio (skipped inject):", stem)
            problems += 1
            continue
        data = f.read_bytes()
        br, dur = mp3_info(data)
        man[stem] = {"hash": new_hash if synthed else man.get(stem, {}).get("hash", ""), "bytes": len(data),
                     "duration_s": round(dur, 1), "bitrate_kbps": br, "voice": VOICE}
        mirror = MIRROR / "audio" / f.name
        mirror.parent.mkdir(parents=True, exist_ok=True)
        if not mirror.exists() or mirror.read_bytes() != data:
            mirror.write_bytes(data)
        block = audio_block(slug, stem, name, script, dur)
        for p in copies(slug):
            old = read(p)
            new = inject(old, block)
            if new != old:
                p.write_bytes(new.encode("utf-8"))
                print("injected", p.relative_to(ROOT))
    MANIFEST.write_text(json.dumps(man, indent=2, sort_keys=True) + "\n", "utf-8")
    return problems


def check():
    bad = 0
    for slug, stem, name, script in pages():
        f = ROOT / "audio" / f"{stem}.mp3"
        if not f.exists():
            print("MISSING", f); bad += 1; continue
        try:
            br, dur = mp3_info(f.read_bytes())
        except ValueError as e:
            print("INVALID", f, e); bad += 1; continue
        if not (MIRROR / "audio" / f.name).exists():
            print("MIRROR MISSING", f.name); bad += 1
        block = audio_block(slug, stem, name, script, dur)
        for p in copies(slug):
            if inject(read(p), block) != read(p):
                print("pending", p.relative_to(ROOT)); bad += 1
    print("audio check:", "OK" if not bad else f"{bad} problem(s)")
    return bad


def selftest():
    assert iso_duration(0) == "PT1S" and iso_duration(65) == "PT1M5S" and iso_duration(60) == "PT1M0S"
    # synthetic CBR frame: MPEG1 L3 128kbps 44.1kHz header FF FB 90 00
    fake = b"ID3\x04\x00\x00\x00\x00\x00\x00" + (b"\xff\xfb\x90\x00" + b"\x00" * 413) * 10
    br, dur = mp3_info(fake)
    assert br == 128 and 0.0 < dur < 1.0
    page = "<html><head></head><body><section class=\"hero\"><h1>T</h1></section>\n<section>b</section></body></html>"
    blk = audio_block("fridge-repair-london", "fridge-repair-london", "N", md.MONEY["fridge-repair-london"]["audio"], 42.4)
    once = inject(page, blk)
    assert inject(once, blk) == once and once.count(START) == 1
    assert once.index(START) > once.index("</h1>") and once.index(START) < once.index("<section>b")
    m = re.search(r'<script type="application/ld\+json" data-cd-schema="audio-speakable">\s*([\s\S]*?)</script>', once)
    j = json.loads(m.group(1))
    types = [n["@type"] for n in j["@graph"]]
    assert types == ["WebPage", "AudioObject"] and j["@graph"][0]["speakable"]["@type"] == "SpeakableSpecification"
    assert j["@graph"][1]["duration"] == "PT42S" and "07983 759320" in j["@graph"][1]["transcript"]
    assert 'preload="none"' in once and "controls" in once
    assert SPOKEN_PHONE in md.MONEY["fridge-repair-london"]["audio"]
    print("generate_seo_audio selftest OK")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--selftest" in a:
        selftest()
    elif "--check" in a:
        sys.exit(1 if check() else 0)
    elif "--inject" in a:
        sys.exit(1 if generate(False) else 0)
    else:
        sys.exit(1 if generate(True) else 0)
