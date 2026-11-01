#!/usr/bin/env python3
"""Submit the deployed sitemap URLs to IndexNow using the public verification key."""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.colddirect.co.uk"
HOST = "www.colddirect.co.uk"
KEY_FILE = ROOT / "09f0efc65468d3e8598408ac29953023.txt"
SITEMAP_FILE = ROOT / "sitemap.xml"
ENDPOINT = "https://api.indexnow.org/indexnow"


def parse_sitemap(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    return [node.text.strip() for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc") if node.text]


def build_payload(key: str, urls: list[str]) -> dict:
    if not re.fullmatch(r"[0-9a-f]{32}", key):
        raise ValueError("IndexNow key must be exactly 32 lowercase hexadecimal characters")
    unique = list(dict.fromkeys(urls))
    if not unique or any(not url.startswith(SITE + "/") for url in unique):
        raise ValueError("URL list must contain only Cold Direct URLs and cannot be empty")
    return {
        "host": HOST,
        "key": key,
        "keyLocation": f"{SITE}/{key}.txt",
        "urlList": unique,
    }


def submit_indexnow(payload: dict, urlopen=urllib.request.urlopen) -> int:
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "ColdDirect-IndexNow/1.0"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"IndexNow returned HTTP {exc.code}") from exc
    if status not in (200, 202):
        raise RuntimeError(f"IndexNow returned HTTP {status}")
    return status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Build and validate the payload without sending it")
    parser.add_argument("--url", action="append", default=[], help="Additional URL to submit (may be repeated)")
    args = parser.parse_args()

    key = KEY_FILE.read_text(encoding="ascii").strip()
    payload = build_payload(key, parse_sitemap(SITEMAP_FILE) + args.url)
    print(f"IndexNow URLs: {len(payload['urlList'])}")
    if args.dry_run:
        print("Dry run: payload valid; no request sent")
        return 0
    status = submit_indexnow(payload)
    print(f"IndexNow submit: HTTP {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
