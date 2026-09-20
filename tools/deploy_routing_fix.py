"""Upload routing + Ice-O-Matic/asset files via existing Plesk FTPS helper."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import deploy_to_plesk as d
FILES = [
    (ROOT / "web.config", "web.config"),
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
    print("uploaded", remote, local.stat().st_size)


def main() -> int:
    os.chdir(ROOT)
    cfg = d.load_env()
    ftp = d.diagnose(cfg)
    if ftp is None:
        print("FTP login failed")
        return 1
    base = cfg["path"]
    try:
        ftp.cwd(base)
        for local, remote in FILES:
            if not local.is_file():
                print("MISSING", local)
                continue
            upload(ftp, base, local, remote)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
