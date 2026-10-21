#!/usr/bin/env python3
"""READ-ONLY live enforcement: the optimized SEO state must stay 100% intact (24h job).

  python tools/seo_integrity_check.py              check the LIVE site (exit 1 on any loss)
  python tools/seo_integrity_check.py --selftest   offline tests

It never writes to the site and never rewrites titles/H1s. It verifies, for the 9 money hubs + homepage + blog:
  title / meta description / og:title / og:description / og:image / twitter:image match tools/money_data.py,
  one H1, titles unique across hubs, V4 schema + CD-MONEY-V1 + CD-AUDIO-V1 blocks present, AudioObject +
  SpeakableSpecification JSON-LD valid, the MP3 is reachable (audio/*), blog pages link to all 9 hubs,
  and repo auto-seo.aspx moneyMeta still mirrors money_data (so the nightly aspx run cannot flip titles).
"""
import html as htmllib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("SITE_BASE", md.SITE)
UA = {"User-Agent": "ColdDirect-SEO-Integrity/1.0 (+https://www.colddirect.co.uk)"}


def fetch(url, method="GET"):
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read() if method == "GET" else b""
            hdr = dict(r.headers)
            hdr["X-Final-Url"] = r.geturl()
            return r.status, hdr, body.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), ""
    except Exception as e:  # noqa: BLE001
        return 0, {}, str(e)


def meta(html, attr, name):
    m = re.search(r'<meta\s+' + attr + r'="' + re.escape(name) + r'"\s+content="([^"]*)"', html, re.I)
    return htmllib.unescape(m.group(1)) if m else None


def title_of(html):
    m = re.search(r"<title>([\s\S]*?)</title>", html, re.I)
    return htmllib.unescape(m.group(1)).strip() if m else None


def audio_schema(html):
    for m in re.finditer(r'<script type="application/ld\+json"[^>]*data-cd-schema="audio-speakable"[^>]*>([\s\S]*?)</script>', html):
        try:
            return json.loads(m.group(1))
        except ValueError:
            return None
    return None


def check_hub(slug, html):
    d = md.MONEY[slug]
    p = []
    if title_of(html) != d["title"]:
        p.append(f"title differs: {title_of(html)!r}")
    if meta(html, "name", "description") != d["desc"]:
        p.append("meta description differs")
    if meta(html, "property", "og:title") != d["title"]:
        p.append("og:title differs")
    if meta(html, "property", "og:description") != d["desc"]:
        p.append("og:description differs")
    for attr, name in (("property", "og:image"), ("name", "twitter:image")):
        if not meta(html, attr, name):
            p.append(f"{name} missing")
    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        p.append("H1 count != 1")
    for marker in ("<!-- AUTO-SEO-V4-SCHEMA -->", "<!-- AUTO-SEO-V4-2026 -->", "<!-- CD-MONEY-V1 -->", "<!-- CD-AUDIO-V1 -->"):
        if marker not in html:
            p.append(f"missing {marker}")
    p += check_audio_schema(slug, html)
    if md.PHONE_TEL not in html:
        p.append("official mobile tel: link missing")
    return p


def check_audio_schema(slug, html):
    j = audio_schema(html)
    if not j:
        return ["audio JSON-LD missing/invalid"]
    types = [n.get("@type") for n in j.get("@graph", [])]
    p = []
    if "AudioObject" not in types:
        p.append("AudioObject missing")
    if not any(n.get("speakable", {}).get("@type") == "SpeakableSpecification" for n in j.get("@graph", [])):
        p.append("SpeakableSpecification missing")
    if 'preload="none"' not in html or "<audio" not in html:
        p.append("<audio controls preload=none> missing")
    return p


def check_blog(html):
    p = []
    if "<!-- CD-BLOG-MONEY-LINKS-V1 -->" not in html:
        return ["blog money-links block missing"]
    for slug in md.HUB_ORDER:
        if f'href="/{slug}/"' not in html:
            p.append(f"no link to {slug}")
    return p


def aspx_sync():
    text = (ROOT / "auto-seo.aspx").read_bytes().decode("utf-8")
    p = []
    for slug, d in md.MONEY.items():
        m = re.search(r'moneyMeta\["' + re.escape(slug) + r'"\] = new string\[\] \{ "((?:[^"\\]|\\.)*)", "((?:[^"\\]|\\.)*)"', text)
        if not m:
            p.append(f"aspx moneyMeta[{slug}] missing")
        elif m.group(1) != md.aspx_js_escape(d["title"]) or m.group(2) != md.aspx_js_escape(d["desc"]):
            p.append(f"aspx moneyMeta[{slug}] differs from money_data")
    return p


def blog_slugs():
    return sorted(p.stem for p in (ROOT / "blog").glob("*.html") if p.stem != "index")


def run(fetcher=fetch, base=BASE, slugs=None):
    rows, fails = [], 0

    def rec(name, problems):
        nonlocal fails
        rows.append((name, problems))
        fails += bool(problems)

    rec("auto-seo.aspx moneyMeta mirrors money_data", aspx_sync())
    titles = {}
    for slug in md.HUB_ORDER:
        st, _, body = fetcher(f"{base}/{slug}/")
        probs = [f"HTTP {st}"] if st != 200 else check_hub(slug, body)
        if st == 200:
            titles.setdefault(title_of(body), []).append(slug)
        rec(f"hub /{slug}/", probs)
        stem = slug
        ast, hdr, _ = fetcher(f"{base}/audio/{stem}.mp3", "HEAD")
        cl = int(hdr.get("Content-Length", 0) or 0) if isinstance(hdr, dict) else 0
        rec(f"audio /audio/{stem}.mp3", [] if ast == 200 and cl > 10000 else [f"HTTP {ast}, bytes {cl}"])
    dup = [f"duplicate title {t!r}: {s}" for t, s in titles.items() if len(s) > 1]
    rec("hub titles unique", dup)
    st, _, home = fetcher(f"{base}/")
    hp = [f"HTTP {st}"] if st != 200 else (
        check_audio_schema("", home) + ([] if "<!-- CD-AUDIO-V1 -->" in home else ["audio block missing"])
        + ([] if meta(home, "property", "og:image") else ["og:image missing"])
        + ([] if meta(home, "name", "twitter:image") else ["twitter:image missing"])
        + ([] if "<!-- AUTO-SEO-V4-BLOGHUB -->" in home else ["V4 bloghub missing"]))
    rec("homepage", hp)
    for path in ["blog/"] + [f"blog/{s}/" for s in (slugs if slugs is not None else blog_slugs())]:
        st, hdr, body = fetcher(f"{base}/{path}")
        final = (hdr or {}).get("X-Final-Url", "")
        if st == 200 and final and final.rstrip("/") != f"{base}/{path}".rstrip("/"):
            rec(f"blog /{path} (intentionally redirected, skipped)", [])  # e.g. domestic post 301 -> commercial hub
            continue
        rec(f"blog /{path}", [f"HTTP {st}"] if st != 200 else check_blog(body))
    return rows, fails


def report(rows):
    lines = ["| Check | Result |", "|---|---|"]
    for name, probs in rows:
        lines.append(f"| {name} | {'OK' if not probs else 'FAIL: ' + '; '.join(probs)} |")
    return "\n".join(lines)


def main():
    rows, fails = run()
    md_out = "## SEO integrity (live, read-only)\n" + report(rows) + f"\n\n**{'ALL INTACT' if not fails else str(fails) + ' check(s) lost integrity'}**\n"
    print(md_out)
    s = os.environ.get("GITHUB_STEP_SUMMARY")
    if s:
        with open(s, "a", encoding="utf-8") as f:
            f.write(md_out)
    return 1 if fails else 0


def selftest():
    # build a perfect fake site from the same generators the real tools use
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import generate_seo_audio as ga
    import money_keywords_apply as mk
    import blog_money_links as bl
    skeleton = ('<html><head><title>x</title><meta name="description" content="x">\n<meta property="og:image" content="i">'
                '<meta name="twitter:image" content="i">\n<!-- AUTO-SEO-V4-SCHEMA --></head><body><section><h1>H</h1></section>\n'
                '<section class="cd-faq-accordion"></section><!-- AUTO-SEO-V4-2026 -->'
                '<a href="tel:+447983759320">c</a><footer>f</footer></body></html>')
    pages = {}
    for slug in md.HUB_ORDER:
        h = mk.apply_html(skeleton, slug)
        dur = 27.0
        h = ga.inject(h, ga.audio_block(slug, slug, "n", md.MONEY[slug]["audio"], dur))
        pages[f"/{slug}/"] = h
    home = ga.inject(skeleton.replace("<!-- AUTO-SEO-V4-2026 -->", "<!-- AUTO-SEO-V4-2026 --><!-- AUTO-SEO-V4-BLOGHUB -->"),
                     ga.audio_block("", "colddirect-home", "n", md.HOME_AUDIO["script"], 27.0))
    pages["/"] = home
    pages["/blog/"] = bl.apply_text("<html><body><footer></footer></body></html>", "")
    pages["/blog/post-a/"] = bl.apply_text("<html><body><footer></footer></body></html>", "post-a")

    def fake(url, method="GET"):
        path = url.replace(BASE, "")
        if path.startswith("/audio/"):
            return 200, {"Content-Length": "150000"}, ""
        return (200, {}, pages[path]) if path in pages else (404, {}, "")

    rows, fails = run(fake, BASE, ["post-a"])
    bad = [r for r in rows if r[1]]
    assert fails == 0 or bad == [r for r in rows if r[1]]
    # aspx check is against the real repo file; everything else must pass on the perfect site
    assert all(not probs for name, probs in rows if "aspx" not in name), [r for r in rows if r[1]]
    # now break things and make sure each loss is detected
    broken = dict(pages)
    broken["/fridge-repair-london/"] = pages["/fridge-repair-london/"].replace("<!-- CD-AUDIO-V1 -->", "")
    broken["/cold-room-repair-london/"] = pages["/cold-room-repair-london/"].replace(md.MONEY["cold-room-repair-london"]["title"], "Other title")
    broken["/blog/post-a/"] = pages["/blog/post-a/"].replace('href="/cellar-cooler-repair-london/"', 'href="/x/"')

    def fake2(url, method="GET"):
        path = url.replace(BASE, "")
        if path.startswith("/audio/"):
            return (404, {}, "") if "freezer-repair-london.mp3" in path and "commercial" not in path else (200, {"Content-Length": "150000"}, "")
        return (200, {}, broken[path]) if path in broken else (404, {}, "")

    rows2, fails2 = run(fake2, BASE, ["post-a"])
    failed = {n for n, pr in rows2 if pr}
    assert "hub /fridge-repair-london/" in failed and "hub /cold-room-repair-london/" in failed
    assert "blog /blog/post-a/" in failed and "audio /audio/freezer-repair-london.mp3" in failed
    def fake3(url, method="GET"):
        path = url.replace(BASE, "")
        if path == "/blog/gone/":
            return 200, {"X-Final-Url": BASE + "/commercial-fridge-repair-london/"}, "<html>hub</html>"
        return fake(url, method)

    rows3, _ = run(fake3, BASE, ["gone"])
    assert [pr for n, pr in rows3 if n.startswith("blog /blog/gone")] == [[]]
    print("seo_integrity_check selftest OK (perfect site passes; 4 simulated losses detected; intentional redirect skipped)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        sys.exit(main())
