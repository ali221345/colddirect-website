"""Download live IIS files for money-page noindex check."""
from __future__ import annotations

import os
import sys
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import deploy_to_plesk as d

REMOTE = [
    "air-conditioning-repair-london.html",
    "air-conditioning-repair-london/index.html",
    "air-conditioning-repair-london/default.asp",
    "air-conditioning-repair-london.asp",
    "chiller-repair-london.html",
    "chiller-repair-london/index.html",
    "chiller-repair-london.asp",
    "ice-machine-repair-london.html",
    "ice-machine-repair-london/index.html",
    "ice-machine-repair-london.asp",
    "web.config",
    "includes/header-nav.inc",
]


def main() -> int:
    cfg = d.load_env()
    ftp = d.diagnose(cfg)
    if ftp is None:
        print("FTP login failed")
        return 1
    base = cfg["path"]
    out = ROOT / "logs" / "live-download"
    out.mkdir(parents=True, exist_ok=True)
    try:
        ftp.cwd(base)
        print("CWD", ftp.pwd())
        try:
            print("NLST air-conditioning-repair-london*")
            for name in ftp.nlst("air-conditioning-repair-london*"):
                print(" ", name)
        except Exception as e:
            print(" nlst err", e)
        try:
            print("NLST dir air-conditioning-repair-london")
            ftp.cwd(base + "/air-conditioning-repair-london")
            print("  in dir", ftp.pwd())
            for name in ftp.nlst():
                print(" ", name)
            ftp.cwd(base)
        except Exception as e:
            print(" dir err", e)
            ftp.cwd(base)
        for remote in REMOTE:
            buf = BytesIO()
            try:
                ftp.retrbinary("RETR " + remote, buf.write)
            except Exception as e:
                print("MISS", remote, e)
                continue
            data = buf.getvalue()
            dest = out / remote.replace("/", "__")
            dest.write_bytes(data)
            text = data.decode("utf-8", errors="replace")
            robots = [ln.strip() for ln in text.splitlines() if "robots" in ln.lower() or "noindex" in ln.lower()]
            print("GOT", remote, len(data), robots[:8])
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
