#!/usr/bin/env python3
"""READ-ONLY live enforcement: the optimized SEO state must stay 100% intact (24h job).

  python tools/seo_integrity_check.py              check the LIVE site (exit 1 on any loss)
  python tools/seo_integrity_check.py --selftest   offline tests

It never writes to the site and never rewrites titles/H1s. It verifies, for the 9 money hubs + homepage + blog:
  title / meta description / og:title / og:description / og:image / twitter:image match tools/money_data.py,
  one H1, titles unique across hubs, V4 schema + CD-MONEY-V1 + CD-AUDIO-V1 blocks present,
  blog pages link to all 9 hubs, and repo auto-seo.aspx moneyMeta still mirrors money_data
  (so the nightly aspx run cannot flip titles).

SEO AUDIO ASSETS (also imported by tools/live_smoke_test.py, so every post-deploy run enforces it too):
  for the homepage + the 9 hubs (10 targets) the live HTML must contain an <audio>/<source> with a local
  /audio/*.mp3 URL, a JSON-LD AudioObject whose contentUrl is that same URL and a SpeakableSpecification;
  every de-duplicated MP3 is then fetched and must be HTTP 200, Content-Type audio/mpeg|audio/mp3 (never the
  IIS text/html soft-404), > 10 000 bytes, complete (Content-Length == body) and start with an ID3 tag or an
  MPEG sync frame (0xFF 0xEx). Row: "🔊 SEO Audio Assets".
"""
import html as htmllib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import money_data as md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("SITE_BASE", md.SITE)
UA = {"User-Agent": "ColdDirect-SEO-Integrity/1.0 (+https://www.colddirect.co.uk)"}

AUDIO_ROW = "🔊 SEO Audio Assets"
AUDIO_MIN_BYTES = 10000
AUDIO_MAX_BYTES = 8 * 1024 * 1024
AUDIO_TYPES = ("audio/mpeg", "audio/mp3")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


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


def fetch_bin(url, tries=2):
    """GET one URL without following redirects. Returns (status, headers, raw bytes)."""
    for _ in range(tries):
        try:
            r = _OPENER.open(urllib.request.Request(url, headers=dict(UA, **{"Cache-Control": "no-cache"})), timeout=40)
            return r.status, dict(r.headers), r.read(AUDIO_MAX_BYTES)
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), b""
        except Exception:  # noqa: BLE001 - network blip, retry once
            pass
    return 0, {}, b""


def meta(html, attr, name):
    m = re.search(r'<meta\s+' + attr + r'="' + re.escape(name) + r'"\s+content="([^"]*)"', html, re.I)
    return htmllib.unescape(m.group(1)) if m else None


def title_of(html):
    m = re.search(r"<title>([\s\S]*?)</title>", html, re.I)
    return htmllib.unescape(m.group(1)).strip() if m else None


# ------------------------------------------------------------------ SEO audio assets
def audio_targets():
    """[(page path, expected mp3 stem)] - homepage + the 9 money hubs (10 targets)."""
    return [("/", md.HOME_AUDIO["file"])] + [(f"/{s}/", s) for s in md.HUB_ORDER]


_SRC_RX = re.compile(r"""\bsrc\s*=\s*("[^"]*"|'[^']*'|[^\s"'>]+)""", re.I)
_COMMENT_RX = re.compile(r"<!--.*?-->", re.S)
_HOST = urllib.parse.urlsplit(BASE).netloc.lower()


def _local_mp3_path(ref, page_url):
    """Path ('/audio/x.mp3') when ref is a same-origin .mp3 under /audio/, else None."""
    ref = (ref or "").strip().strip("\"'")
    if not ref:
        return None
    parts = urllib.parse.urlsplit(urllib.parse.urljoin(page_url, ref))
    if parts.scheme not in ("http", "https") or parts.netloc.lower() != _HOST:
        return None
    path = urllib.parse.unquote(parts.path)
    return path if path.startswith("/audio/") and path.lower().endswith(".mp3") else None


def audio_embed_paths(html, page_url):
    """Local /audio/*.mp3 paths referenced by <audio src> and nested <source src> (ordered, de-duplicated)."""
    src = _COMMENT_RX.sub("", html or "")
    out = []
    for block in re.finditer(r"<audio\b[^>]*>([\s\S]*?)</audio>", src, re.I):
        tags = re.findall(r"<audio\b[^>]*>", block.group(0)[:block.group(0).find(">") + 1], re.I)
        tags += re.findall(r"<source\b[^>]*>", block.group(1), re.I)
        for tag in tags:
            m = _SRC_RX.search(tag)
            p = _local_mp3_path(m.group(1), page_url) if m else None
            if p and p not in out:
                out.append(p)
    return out


def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def _types(node):
    t = node.get("@type", [])
    return [t] if isinstance(t, str) else [x for x in t if isinstance(x, str)]


def jsonld_nodes(html):
    nodes, bad = [], 0
    for m in re.finditer(r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', html or "", re.I):
        try:
            nodes += list(_walk(json.loads(m.group(1))))
        except ValueError:
            bad += 1
    return nodes, bad


def audio_schema_info(html, page_url):
    """(content paths of AudioObject nodes, has SpeakableSpecification, invalid JSON-LD blocks)."""
    nodes, bad = jsonld_nodes(html)
    paths = []
    for n in nodes:
        if "AudioObject" in _types(n):
            p = _local_mp3_path(str(n.get("contentUrl", "")), page_url)
            paths.append(p or ("?" + str(n.get("contentUrl", ""))))
    speak = any("SpeakableSpecification" in _types(n) for n in nodes) or \
        any(isinstance(n.get("speakable"), (dict, list)) and any("SpeakableSpecification" in _types(s) for s in _walk(n["speakable"])) for n in nodes)
    return paths, speak, bad


def check_audio_page(path, html, expected_stem=None, base=BASE):
    """(mp3 path or None, [problems]) for one page's HTML."""
    page_url = base + path
    probs = []
    embeds = audio_embed_paths(html, page_url)
    paths, speak, bad = audio_schema_info(html, page_url)
    mp3 = embeds[0] if embeds else None
    if not embeds:
        probs.append("no <audio>/<source> with a local /audio/*.mp3 URL")
    if not paths:
        probs.append("AudioObject JSON-LD missing" + (" (invalid JSON-LD present)" if bad else ""))
    elif mp3 and mp3 not in paths:
        probs.append(f"AudioObject.contentUrl {paths[0].lstrip('?')} does not match <audio> {mp3}")
    if not speak:
        probs.append("SpeakableSpecification missing")
    if mp3 and expected_stem and mp3 != f"/audio/{expected_stem}.mp3":
        probs.append(f"unexpected audio file {mp3} (expected /audio/{expected_stem}.mp3)")
    return mp3, probs


def verify_mp3(url, get_bin):
    """None when the MP3 is live and playable, otherwise a short reason."""
    status, headers, data = get_bin(url)
    if status != 200:
        return f"HTTP {status}"
    h = {k.lower(): v for k, v in (headers or {}).items()}
    ctype = h.get("content-type", "").split(";")[0].strip().lower()
    head = (data or b"")[:1024].lstrip(b"\xef\xbb\xbf \t\r\n").lower()
    if "html" in ctype or head.startswith((b"<!doctype", b"<html", b"<head", b"<body", b"<title")):
        return f"HTML page served instead of audio (soft-404, Content-Type {ctype or 'none'})"
    if ctype not in AUDIO_TYPES:
        return f"Content-Type {ctype or 'missing'} (expected audio/mpeg)"
    if len(data) <= AUDIO_MIN_BYTES:
        return f"only {len(data)} bytes (<= {AUDIO_MIN_BYTES}: empty/truncated)"
    cl = h.get("content-length", "")
    if cl.isdigit() and int(cl) != len(data):
        return f"truncated: Content-Length {cl} but received {len(data)} bytes"
    if not (data[:3] == b"ID3" or (data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)):
        return "not an MP3 (no ID3 tag / MPEG sync frame at the start)"
    return None


def audio_check(get_html, get_bin, targets=None, base=BASE):
    """Verify the SEO audio summaries. get_html(path) -> (status, html); get_bin(url) -> (status, headers, bytes).
    Returns (ok, ok_text, problems [str]) where problems are 'path -> reason' strings."""
    targets = targets if targets is not None else audio_targets()
    per_page, urls = [], []
    for path, stem in targets:
        st, html = get_html(path)
        if st != 200:
            per_page.append((path, None, [f"page HTTP {st}" if st else "page not fetched"]))
            continue
        mp3, probs = check_audio_page(path, html, stem, base)
        per_page.append((path, mp3, probs))
        if mp3 and mp3 not in urls:
            urls.append(mp3)
    verdict = {u: verify_mp3(base + u, get_bin) for u in urls}          # each unique MP3 fetched exactly once
    problems, healthy = [], 0
    for path, mp3, probs in per_page:
        probs = list(probs)
        if mp3 and verdict.get(mp3):
            probs.append(f"{mp3}: {verdict[mp3]}")
        if probs:
            problems.append(f"{path} -> " + "; ".join(probs))
        else:
            healthy += 1
    n = len(targets)
    if not problems:
        return True, f"{n}/{n} MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact", []
    return False, f"{healthy}/{n} healthy, FAILING: " + " | ".join(problems), problems


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
    if md.PHONE_TEL not in html:
        p.append("official mobile tel: link missing")
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


def run(fetcher=fetch, base=BASE, slugs=None, binfetcher=fetch_bin):
    """rows: [(name, [problems], ok_text_or_None)]; fails = number of failing rows."""
    rows, fails = [], 0

    def rec(name, problems, ok_text=None):
        nonlocal fails
        rows.append((name, problems, ok_text))
        fails += bool(problems)

    rec("auto-seo.aspx moneyMeta mirrors money_data", aspx_sync())
    titles, bodies = {}, {}
    for slug in md.HUB_ORDER:
        st, _, body = fetcher(f"{base}/{slug}/")
        probs = [f"HTTP {st}"] if st != 200 else check_hub(slug, body)
        if st == 200:
            titles.setdefault(title_of(body), []).append(slug)
            bodies[f"/{slug}/"] = body
        rec(f"hub /{slug}/", probs)
    dup = [f"duplicate title {t!r}: {s}" for t, s in titles.items() if len(s) > 1]
    rec("hub titles unique", dup)
    st, _, home = fetcher(f"{base}/")
    if st == 200:
        bodies["/"] = home
    hp = [f"HTTP {st}"] if st != 200 else (
        ([] if "<!-- CD-AUDIO-V1 -->" in home else ["audio block missing"])
        + ([] if meta(home, "property", "og:image") else ["og:image missing"])
        + ([] if meta(home, "name", "twitter:image") else ["twitter:image missing"])
        + ([] if "<!-- AUTO-SEO-V4-BLOGHUB -->" in home else ["V4 bloghub missing"]))
    rec("homepage", hp)
    ok, ok_text, problems = audio_check(lambda p: (200, bodies[p]) if p in bodies else (0, ""), binfetcher, base=base)
    rec(AUDIO_ROW, problems, ok_text)
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
    for name, probs, ok_text in rows:
        lines.append(f"| {name} | {('PASS — ' + ok_text) if (not probs and ok_text) else 'OK' if not probs else 'FAIL: ' + '; '.join(probs)} |")
    return "\n".join(lines)


def main():
    try:  # the audio row contains an emoji; Windows consoles may be cp1252
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    rows, fails = run()
    md_out = "## SEO integrity (live, read-only)\n" + report(rows) + f"\n\n**{'ALL INTACT' if not fails else str(fails) + ' check(s) lost integrity'}**\n"
    print(md_out)
    s = os.environ.get("GITHUB_STEP_SUMMARY")
    if s:
        with open(s, "a", encoding="utf-8") as f:
            f.write(md_out)
    return 1 if fails else 0


# ------------------------------------------------------------------ self-tests
def _fake_mp3(n=20000, head=b"ID3\x04\x00\x00\x00\x00\x00\x00"):
    return head + b"\xff\xfb\x90\x00" + b"\x00" * (n - len(head) - 4)


def audio_selftest():
    """Offline scenarios shared by this script's and live_smoke_test.py's --selftest. Returns the number of scenarios."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import generate_seo_audio as ga
    targets = audio_targets()
    assert len(targets) == 10 and targets[0] == ("/", "colddirect-home")
    skeleton = "<html><head></head><body><section><h1>H</h1></section><footer>f</footer></body></html>"
    scripts = {s: (n, sc) for s, _, n, sc in ga.md.audio_pages()}
    pages = {}
    for path, stem in targets:
        slug = path.strip("/")
        name, script = scripts[slug]
        pages[path] = ga.inject(skeleton, ga.audio_block(slug, stem, name, script, 27.0))
    mp3 = {f"{BASE}/audio/{stem}.mp3": (200, {"Content-Type": "audio/mpeg", "Content-Length": "20000"}, _fake_mp3()) for _, stem in targets}
    calls = []

    def run_case(pages_=None, mp3_=None):
        p, m = dict(pages_ or pages), dict(mp3_ or mp3)
        calls.clear()

        def gb(url):
            calls.append(url)
            return m.get(url, (404, {}, b""))
        return audio_check(lambda path: (200, p[path]) if path in p else (404, ""), gb)

    def sub(url_stem, **kw):
        d = dict(mp3)
        d[f"{BASE}/audio/{url_stem}.mp3"] = kw.get("resp")
        return d

    # 1. 10/10 valid MP3s (ID3 header) + matching AudioObject + Speakable; each unique MP3 fetched once
    ok, txt, probs = run_case()
    assert ok and probs == [] and txt == "10/10 MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact", txt
    assert len(calls) == 10 == len(set(calls)), "MP3s must be de-duplicated and fetched once"
    # MPEG sync frame instead of ID3 is also valid
    sync = sub("cold-room-repair-london", resp=(200, {"Content-Type": "audio/mp3", "Content-Length": "20000"}, _fake_mp3(head=b"")))
    sync[f"{BASE}/audio/cold-room-repair-london.mp3"] = (200, {"Content-Type": "audio/mp3"}, b"\xff\xfb\x90\x00" + b"\x00" * 19996)
    assert run_case(mp3_=sync)[0]
    # two pages sharing one MP3 -> still a single fetch
    shared = dict(pages)
    shared["/freezer-repair-london/"] = pages["/fridge-repair-london/"]
    run_case(shared)
    assert len(calls) == len(set(calls)) and len(calls) <= 9

    def must_fail(res, *needles):
        ok_, t_, p_ = res
        assert not ok_ and p_ and all(n in t_ for n in needles), (t_, p_)

    # 2. missing <audio> tag
    broken = dict(pages)
    broken["/cold-room-repair-london/"] = re.sub(r"<audio\b[\s\S]*?</audio>", "", pages["/cold-room-repair-london/"])
    must_fail(run_case(broken), "/cold-room-repair-london/", "no <audio>", "9/10 healthy")
    # 3. AudioObject.contentUrl mismatch
    broken = dict(pages)
    broken["/fridge-repair-london/"] = pages["/fridge-repair-london/"].replace(
        f'"contentUrl": "{BASE}/audio/fridge-repair-london.mp3"', f'"contentUrl": "{BASE}/audio/other.mp3"')
    must_fail(run_case(broken), "/fridge-repair-london/", "does not match")
    # missing AudioObject / missing Speakable / invalid JSON-LD
    for needle, repl, expect in (('"AudioObject"', '"CreativeWork"', "AudioObject JSON-LD missing"),
                                 ('"SpeakableSpecification"', '"Thing"', "SpeakableSpecification missing")):
        broken = dict(pages)
        broken["/"] = pages["/"].replace(needle, repl)
        must_fail(run_case(broken), expect)
    # <source> inside <audio> is accepted when <audio> has no src
    nested = dict(pages)
    nested["/"] = re.sub(r'<audio controls preload="none" src="[^"]*">', '<audio controls preload="none">', pages["/"])
    assert run_case(nested)[0]
    # 4. HTTP 404 on the MP3
    d = dict(mp3)
    del d[f"{BASE}/audio/catering-repair-london.mp3"]
    must_fail(run_case(mp3_=d), "/audio/catering-repair-london.mp3: HTTP 404")
    # 5. truncated < 10 KB file (also: Content-Length larger than the received body)
    must_fail(run_case(mp3_=sub("freezer-repair-london", resp=(200, {"Content-Type": "audio/mpeg"}, _fake_mp3(8000)))), "8000 bytes")
    must_fail(run_case(mp3_=sub("freezer-repair-london", resp=(200, {"Content-Type": "audio/mpeg", "Content-Length": "150000"}, _fake_mp3(20000)))), "truncated")
    # 6. HTML soft-404 served with HTTP 200 instead of audio/mpeg
    soft = b"<!DOCTYPE html><html><head><title>Not found</title></head><body>" + b"x" * 20000 + b"</body></html>"
    must_fail(run_case(mp3_=sub("air-conditioning-repair-london", resp=(200, {"Content-Type": "text/html"}, soft))), "soft-404")
    must_fail(run_case(mp3_=sub("air-conditioning-repair-london", resp=(200, {"Content-Type": "audio/mpeg"}, soft))), "soft-404")
    # wrong Content-Type / bad magic bytes / redirect (301) / network failure
    must_fail(run_case(mp3_=sub("cellar-cooler-repair-london", resp=(200, {"Content-Type": "application/octet-stream"}, _fake_mp3()))), "Content-Type")
    must_fail(run_case(mp3_=sub("cellar-cooler-repair-london", resp=(200, {"Content-Type": "audio/mpeg"}, b"RIFF" + b"\x00" * 20000))), "not an MP3")
    must_fail(run_case(mp3_=sub("cellar-cooler-repair-london", resp=(301, {"Location": "/"}, b""))), "HTTP 301")
    must_fail(run_case(mp3_=sub("cellar-cooler-repair-london", resp=(0, {}, b""))), "HTTP 0")
    # page itself failing / not fetched
    must_fail(audio_check(lambda p: (500, ""), lambda u: (404, {}, b"")), "page HTTP 500")
    return 17


def selftest():
    # build a perfect fake site from the same generators the real tools use
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import generate_seo_audio as ga
    import money_keywords_apply as mk
    import blog_money_links as bl
    n_audio = audio_selftest()
    skeleton = ('<html><head><title>x</title><meta name="description" content="x">\n<meta property="og:image" content="i">'
                '<meta name="twitter:image" content="i">\n<!-- AUTO-SEO-V4-SCHEMA --></head><body><section><h1>H</h1></section>\n'
                '<section class="cd-faq-accordion"></section><!-- AUTO-SEO-V4-2026 -->'
                '<a href="tel:+447983759320">c</a><footer>f</footer></body></html>')
    pages = {}
    for slug in md.HUB_ORDER:
        h = mk.apply_html(skeleton, slug)
        h = ga.inject(h, ga.audio_block(slug, slug, "n", md.MONEY[slug]["audio"], 27.0))
        pages[f"/{slug}/"] = h
    home = ga.inject(skeleton.replace("<!-- AUTO-SEO-V4-2026 -->", "<!-- AUTO-SEO-V4-2026 --><!-- AUTO-SEO-V4-BLOGHUB -->"),
                     ga.audio_block("", "colddirect-home", "n", md.HOME_AUDIO["script"], 27.0))
    pages["/"] = home
    pages["/blog/"] = bl.apply_text("<html><body><footer></footer></body></html>", "")
    pages["/blog/post-a/"] = bl.apply_text("<html><body><footer></footer></body></html>", "post-a")
    good_bin = lambda url: (200, {"Content-Type": "audio/mpeg", "Content-Length": "20000"}, _fake_mp3())  # noqa: E731

    def fake(url, method="GET"):
        path = url.replace(BASE, "")
        return (200, {}, pages[path]) if path in pages else (404, {}, "")

    rows, fails = run(fake, BASE, ["post-a"], good_bin)
    # aspx check is against the real repo file; everything else must pass on the perfect site
    assert all(not probs for name, probs, _ in rows if "aspx" not in name), [r for r in rows if r[1]]
    audio_rows = [r for r in rows if r[0] == AUDIO_ROW]
    assert len(audio_rows) == 1 and audio_rows[0][2].startswith("10/10 MP3 audio summaries")
    assert "PASS — 10/10 MP3 audio summaries HTTP 200, audio/mpeg & AudioObject schema intact" in report(rows)
    # now break things and make sure each loss is detected
    broken = dict(pages)
    broken["/fridge-repair-london/"] = pages["/fridge-repair-london/"].replace("<!-- CD-AUDIO-V1 -->", "")
    broken["/cold-room-repair-london/"] = pages["/cold-room-repair-london/"].replace(md.MONEY["cold-room-repair-london"]["title"], "Other title")
    broken["/blog/post-a/"] = pages["/blog/post-a/"].replace('href="/cellar-cooler-repair-london/"', 'href="/x/"')

    def fake2(url, method="GET"):
        path = url.replace(BASE, "")
        return (200, {}, broken[path]) if path in broken else (404, {}, "")

    def bin2(url):
        if url.endswith("/audio/freezer-repair-london.mp3"):
            return 404, {}, b""
        return good_bin(url)

    rows2, fails2 = run(fake2, BASE, ["post-a"], bin2)
    failed = {n for n, pr, _ in rows2 if pr}
    assert "hub /fridge-repair-london/" in failed and "hub /cold-room-repair-london/" in failed
    assert "blog /blog/post-a/" in failed and AUDIO_ROW in failed
    detail = [pr for n, pr, _ in rows2 if n == AUDIO_ROW][0]
    assert any("/freezer-repair-london/" in x and "HTTP 404" in x for x in detail)

    def fake3(url, method="GET"):
        path = url.replace(BASE, "")
        if path == "/blog/gone/":
            return 200, {"X-Final-Url": BASE + "/commercial-fridge-repair-london/"}, "<html>hub</html>"
        return fake(url, method)

    rows3, _ = run(fake3, BASE, ["gone"], good_bin)
    assert [pr for n, pr, _ in rows3 if n.startswith("blog /blog/gone")] == [[]]
    print(f"seo_integrity_check selftest OK (perfect site passes; hub/blog/audio losses detected; intentional redirect skipped; "
          f"{n_audio} audio scenarios: 10/10 ID3 valid, missing <audio>, mismatched contentUrl, 404, truncated, HTML soft-404, bad type/magic, redirect)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        sys.exit(main())
