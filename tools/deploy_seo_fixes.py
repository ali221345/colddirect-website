"""Upload GSC SEO HTML fixes to Plesk httpdocs."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import deploy_to_plesk as d

FILES = [
    (ROOT / "index.html", "index.html"),
    (ROOT / "cold-room-repairs-london" / "index.html", "cold-room-repairs-london/index.html"),
    (ROOT / "commercial-fridge-repair-london" / "index.html", "commercial-fridge-repair-london/index.html"),
    (ROOT / "fridge-repair-london" / "index.html", "fridge-repair-london/index.html"),
    (ROOT / "freezer-repair-london" / "index.html", "freezer-repair-london/index.html"),
    (ROOT / "commercial-freezer-repair-london" / "index.html", "commercial-freezer-repair-london/index.html"),
    (ROOT / "colddirect-public-html" / "index.html", "index.html"),
    (ROOT / "colddirect-public-html" / "commercial-fridge-repair-london.html", "commercial-fridge-repair-london.html"),
    (ROOT / "colddirect-public-html" / "fridge-repair-london.html", "fridge-repair-london.html"),
    (ROOT / "colddirect-public-html" / "freezer-repair-london.html", "freezer-repair-london.html"),
    (ROOT / "colddirect-public-html" / "commercial-freezer-repair-london.html", "commercial-freezer-repair-london.html"),
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


def connect():
    cfg = d.load_env()
    ftp = d.diagnose(cfg)
    if ftp is None:
        raise RuntimeError("FTP login failed")
    ftp.cwd(cfg["path"])
    return ftp, cfg["path"]


def close(ftp) -> None:
    try:
        ftp.quit()
    except Exception:
        try:
            ftp.close()
        except Exception:
            pass


def main() -> int:
    os.chdir(ROOT)
    # Upload folder/index.html first, then public-html .html twins.
    # Skip the second index.html overwrite if we already uploaded root index.html first.
    remaining = [(local, remote) for local, remote in FILES if local.is_file()]
    # Prefer pretty-URL folder pages and root index.html from repo root, not public-html overwrite of index.
    remaining = [
        (local, remote)
        for local, remote in remaining
        if not (remote == "index.html" and "colddirect-public-html" in str(local))
    ]
    for local, remote in remaining:
        print("uploading", remote, "from", local.relative_to(ROOT), flush=True)
        ftp, base = connect()
        try:
            upload(ftp, base, local, remote)
        finally:
            close(ftp)
    print("Done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
