"""Upload robots-tag fixes to live IIS httpdocs."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import deploy_to_plesk as d

LIVE = ROOT / "logs" / "live-download"
FILES = [
    (LIVE / "air-conditioning-repair-london.html", "air-conditioning-repair-london.html"),
    (LIVE / "air-conditioning-repair-london__index.html", "air-conditioning-repair-london/index.html"),
    (LIVE / "ice-machine-repair-london.html", "ice-machine-repair-london.html"),
    (LIVE / "ice-machine-repair-london__index.html", "ice-machine-repair-london/index.html"),
    (ROOT / "air-conditioning-repairs-london.html", "air-conditioning-repairs-london.html"),
    (ROOT / "chiller-repairs-london.html", "chiller-repairs-london.html"),
]


def ensure_remote_dir(ftp, base: str, rel: str) -> None:
    ftp.cwd(base)
    for part in rel.replace("\\", "/").split("/"):
        if not part:
            continue
        try:
            ftp.cwd(part)
        except Exception:
            ftp.mkd(part)
            ftp.cwd(part)
    ftp.cwd(base)


def upload(ftp, base: str, local: Path, remote: str) -> None:
    remote = remote.replace("\\", "/")
    parent = os.path.dirname(remote)
    if parent:
        ensure_remote_dir(ftp, base, parent)
        ftp.cwd(base + "/" + parent)
    else:
        ftp.cwd(base)
    with local.open("rb") as fh:
        ftp.storbinary("STOR " + os.path.basename(remote), fh)
    ftp.cwd(base)
    print("uploaded", remote, local.stat().st_size, flush=True)


def main() -> int:
    missing = [str(p) for p, _ in FILES if not p.is_file()]
    if missing:
        print("missing", missing)
        return 1
    cfg = d.load_env()
    ftp = d.diagnose(cfg)
    if ftp is None:
        print("FTP login failed")
        return 1
    try:
        ftp.cwd(cfg["path"])
        base = cfg["path"]
        for local, remote in FILES:
            print("uploading", remote, flush=True)
            upload(ftp, base, local, remote)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    print("Done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
