#!/usr/bin/env python3
"""
48-Hour Automated Plesk Live Snapshot Backup for Cold Direct.
Downloads key production configuration and core landing pages from WHUK Plesk FTP (/httpdocs)
so every 48-hour backup archive includes both the Git repository and the live Plesk state.
"""
from __future__ import annotations

import ftplib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "backup-output" / "plesk-live-httpdocs"

CRITICAL_REMOTE_FILES = [
    "web.config",
    ".htaccess",
    "robots.txt",
    "sitemap.xml",
    "index.html",
    "index.php",
    "booking.asp",
    "services.html",
    "services/index.html",
    "coverage.html",
    "coverage/index.html",
    "commercial-fridge-repair-london.html",
    "commercial-fridge-repair-london/index.html",
    "commercial-freezer-repair-london.html",
    "commercial-freezer-repair-london/index.html",
    "fridge-repair-london.html",
    "fridge-repair-london/index.html",
    "freezer-repair-london.html",
    "freezer-repair-london/index.html",
    "cold-room-repair-london.html",
    "cold-room-repair-london/index.html",
    "freezer-room-repair-london.html",
    "freezer-room-repair-london/index.html",
    "commercial-appliances-repair-london.html",
    "commercial-appliances-repair-london/index.html",
    "chiller-repairs-london.html",
    "chiller-repairs-london/index.html",
    "chiller-repair-london.html",
    "ice-machine-repair-london.html",
    "catering-repair-london.html",
    "appliances-repair-london.html",
    "includes/header-nav.inc",
    "includes/footer-services.inc",
]


def main() -> int:
    host = os.environ.get("FTP_SERVER") or os.environ.get("COLD_FTP_HOST") or "5.77.41.163"
    user = os.environ.get("FTP_USERNAME") or os.environ.get("COLD_FTP_USER") or ""
    password = os.environ.get("FTP_PASSWORD") or os.environ.get("COLD_FTP_PASS") or ""
    base = (os.environ.get("COLD_FTP_PATH") or "/httpdocs").rstrip("/")

    if not user or not password:
        print("[PLESK-BACKUP] Missing FTP credentials; skipping live FTP snapshot.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ftp = ftplib.FTP()
    ftp.connect(host, 21, timeout=60)
    ftp.login(user, password)
    ftp.set_pasv(True)

    downloaded = 0
    for rel in CRITICAL_REMOTE_FILES:
        remote_path = f"{base}/{rel}"
        local_file = OUT_DIR / rel
        local_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(local_file, "wb") as fh:
                ftp.retrbinary(f"RETR {remote_path}", fh.write)
            downloaded += 1
        except Exception as exc:
            print(f"[PLESK-BACKUP] Warning skipping {rel}: {exc}")

    try:
        ftp.quit()
    except Exception:
        ftp.close()

    print(f"[PLESK-BACKUP] Downloaded {downloaded}/{len(CRITICAL_REMOTE_FILES)} live files from Plesk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
