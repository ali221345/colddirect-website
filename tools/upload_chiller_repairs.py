"""Upload chiller-repairs-london money page + sitemap after GSC content pass."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import deploy_to_plesk as d
from tools.upload_gsc_seo import close, connect, upload

FILES = [
    (ROOT / "chiller-repairs-london.html", "chiller-repairs-london.html"),
    (ROOT / "chiller-repairs-london.asp", "chiller-repairs-london.asp"),
    (ROOT / "chiller-repairs-london" / "index.html", "chiller-repairs-london/index.html"),
    (ROOT / "colddirect-public-html" / "sitemap.xml", "sitemap.xml"),
    (ROOT / "colddirect-public-html" / ".htaccess", ".htaccess"),
]


def main() -> int:
    os.chdir(ROOT)
    ftp, base = connect()
    try:
        for local, remote in FILES:
            if not local.is_file():
                print("missing", local)
                return 1
            print("uploading", remote, flush=True)
            upload(ftp, base, local, remote)
    finally:
        close(ftp)
    print("Done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
