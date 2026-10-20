#!/usr/bin/env python3
"""Verify the live site after the 2026-10-21 de-cannibalisation pass (read-only GETs)."""
import json
import re
import sys
import urllib.request
import urllib.error

BASE = "https://www.colddirect.co.uk"
UA = {"User-Agent": "Mozilla/5.0 (ColdDirect verify)"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def get(url, follow=True):
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(urllib.request.Request(url, headers=UA), timeout=40)
        return r.status, r.headers, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers, ""


EXPECT = {
    "/": ("Commercial Refrigeration & Air Conditioning Engineers London | ColdDirect", "Commercial Refrigeration &amp; Air Conditioning Engineers London"),
    "/commercial-fridge-repair-london/": ("Commercial Fridge Repair London | 24/7 Emergency Same-Day Engineers", "Commercial Fridge Repair London – Same-Day Walk-In &amp; Display Chiller Engineers"),
    "/fridge-repair-london/": ("Fridge Repair & Service London", "Fridge Repair London"),
    "/freezer-repair-london/": ("Freezer Repair & Service London", "Freezer Repair London"),
    "/commercial-freezer-repair-london/": ("Commercial Freezer Repair London | 24/7 Emergency Same-Day Engineers", "Commercial Freezer Repair London – Same-Day Walk-In &amp; Kitchen Freezer Engineers"),
    "/cold-room-repair-london/": ("Cold Room Repair London | 24/7 Cold Room Repairs, No Hidden Fees", "Cold Room Repair London"),
    "/ice-machine-repair-london/": ("Ice Machine Repairs & Service London | 24/7 Commercial Engineers", "Ice Machine Repairs &amp; Service London"),
    "/ice-cream-machine-repair-london/": ("Commercial Ice Cream & Soft Serve Machine Repair London | 24/7", "Commercial Ice Cream &amp; Soft Serve Machine Repair London"),
}
bad = 0
for path, (title, h1) in EXPECT.items():
    st, _, body = get(BASE + path)
    t = re.search(r"<title>(.*?)</title>", body, re.S)
    t = t.group(1).strip() if t else ""
    h = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    h = h.group(1).strip() if h else ""
    ok = st == 200 and t.startswith(title) and h.startswith(h1) and "ColdDirect London Refrigeration Engineers" in body or (path == "/" and st == 200 and t.startswith(title) and h.startswith(h1))
    ld = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', body, re.S)]
    types = set()

    def walk(o):
        if isinstance(o, dict):
            if "@type" in o:
                types.add(str(o["@type"]))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(ld)
    if path != "/":
        ok = ok and "Service" in types and "FAQPage" in types
    print(("OK  " if ok else "BAD ") + f"{st} {path} | {t[:78]} | H1: {h[:70]} | Service={'Service' in types} FAQ={'FAQPage' in types}")
    bad += 0 if ok else 1

st, hd, _ = get(BASE + "/blog/best-ice-cream-makers/", follow=False)
loc = hd.get("Location", "")
ok = st == 301 and loc.rstrip("/").endswith("/ice-cream-machine-repair-london")
print(("OK  " if ok else "BAD ") + f"{st} /blog/best-ice-cream-makers/ -> {loc}")
bad += 0 if ok else 1
st, hd, _ = get(BASE + "/blog/best-ice-cream-makers.html", follow=False)
print(f"info {st} /blog/best-ice-cream-makers.html -> {hd.get('Location', '')}")
sm = get(BASE + "/sitemap.xml")[2]
print("sitemap urls:", sm.count("<loc>"), "| best-ice-cream in sitemap:", "best-ice-cream" in sm)
sys.exit(1 if bad else 0)
