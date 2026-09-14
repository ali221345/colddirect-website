#!/usr/bin/env python3
"""Check 26 hero-fixed ASP pages plus 3 sample WebP URLs (29 checks)."""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://www.colddirect.co.uk"
PAGES = [
    "adexa-fridge-repair-london.asp",
    "appliances-repair-london.asp",
    "bottle-cooler-repair-london.asp",
    "catering-repair-london.asp",
    "cellar-cooler-repair-london.asp",
    "chiller-repair-london.asp",
    "cold-room-repair-london.asp",
    "commercial-appliances-repair-london.asp",
    "commercial-freezer-repair-london.asp",
    "commercial-fridge-repair-london.asp",
    "dairy-cabinet-repair-london.asp",
    "display-fridge-repair-london.asp",
    "empire-fridge-repair-london.asp",
    "foster-fridge-repair-london.asp",
    "freezer-repair-london.asp",
    "freezer-room-repair-london.asp",
    "fridge-repair-london.asp",
    "ice-cream-machine-repair-london.asp",
    "ice-machine-repair-london.asp",
    "polar-fridge-repair-london.asp",
    "subzero-fridge-repair-london.asp",
    "walk-in-cold-room-repair-london.asp",
    "walk-in-freezer-repair-london.asp",
    "walk-in-fridge-repair-london.asp",
    "williams-fridge-repair-london.asp",
    "wine-cooler-repair-london.asp",
]
WEBP = [
    "images/polar-fridge-repair.webp",
    "images/williams-fridge-repair.webp",
    "images/hoshizaki-ice-machine.webp",
]
UNSPLASH = "images.unsplash.com/photo-1578916171728"


def fetch(path):
    req = Request(BASE + "/" + path, headers={"User-Agent": "colddirect-check/1.0"})
    try:
        with urlopen(req, timeout=25) as r:
            body = r.read()
            return r.status, body
    except HTTPError as e:
        return e.code, e.read() if e.fp else b""
    except URLError as e:
        return 0, str(e).encode()


def main():
    ok = 0
    total = 0
    for page in PAGES:
        total += 1
        status, body = fetch(page)
        text = body.decode("utf-8", "replace")
        has_webp = "images/" in text and ".webp" in text
        no_unsplash = UNSPLASH not in text
        passed = status == 200 and has_webp and no_unsplash
        if passed:
            ok += 1
            print("OK ", page)
        else:
            print("FAIL", page, "status=%s webp=%s unsplash=%s" % (status, has_webp, not no_unsplash))
    for img in WEBP:
        total += 1
        status, body = fetch(img)
        passed = status == 200 and len(body) > 1000
        if passed:
            ok += 1
            print("OK ", img, len(body), "bytes")
        else:
            print("FAIL", img, "status=%s bytes=%s" % (status, len(body)))
    print("%s/%s success" % (ok, total))
    raise SystemExit(0 if ok == total else 1)


if __name__ == "__main__":
    main()
