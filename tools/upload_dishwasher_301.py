"""FTP dishwasher 301 + nav/sitemap/FAQ stubs to Plesk httpdocs."""
from __future__ import annotations

import os
import sys
import time
from ftplib import error_perm
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.upload_gsc_seo import close, connect, upload

FILES = [
    (ROOT / "faqs.html", "faqs.html"),
    (ROOT / "faqs" / "index.html", "faqs/index.html"),
    (ROOT / "commercial-dishwasher-repair-london.html", "commercial-dishwasher-repair-london.html"),
    (
        ROOT / "commercial-dishwasher-repair-london" / "index.html",
        "commercial-dishwasher-repair-london/index.html",
    ),
    (ROOT / "sitemap.xml", "sitemap.xml"),
]


def main() -> int:
    os.chdir(ROOT)
    remaining = [(local, remote) for local, remote in FILES if local.is_file()]
    missing = [str(local) for local, _ in FILES if not local.is_file()]
    for m in missing:
        print("MISSING", m, flush=True)
        return 1
    for local, remote in remaining:
        print("uploading", remote, flush=True)
        last_exc = None
        for attempt in range(1, 5):
            ftp, base = connect()
            try:
                upload(ftp, base, local, remote)
                last_exc = None
                break
            except error_perm as exc:
                last_exc = exc
                print("retry", attempt, remote, exc, flush=True)
                time.sleep(3 * attempt)
            finally:
                close(ftp)
        if last_exc is not None:
            print("FAILED", remote, last_exc, flush=True)
            return 1
    print("Done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
