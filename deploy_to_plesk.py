#!/usr/bin/env python3
"""Upload selected Cold Direct files to Plesk httpdocs over FTP/FTPS."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent


def load_config() -> dict[str, str]:
    load_dotenv(ROOT / ".env")
    cfg = {
        "host": os.environ.get("PLESK_FTP_HOST", "").strip(),
        "user": os.environ.get("PLESK_FTP_USER", "").strip(),
        "password": os.environ.get("PLESK_FTP_PASS", "").strip(),
        "base": os.environ.get("PLESK_FTP_PATH", "/httpdocs").strip() or "/httpdocs",
    }
    missing = [k for k in ("host", "user", "password") if not cfg[k]]
    if missing:
        print("Missing in .env:", ", ".join(f"PLESK_FTP_{m.upper() if m != 'password' else 'PASS'}" for m in missing))
        print("Copy .env.example to .env and fill Plesk FTP Access values.")
        sys.exit(1)
    if not cfg["base"].startswith("/"):
        cfg["base"] = "/" + cfg["base"]
    return cfg


def pick_local(*candidates: Path) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path
    return None


def remote_join(base: str, *parts: str) -> str:
    bits = [base.strip("/")] + [p.strip("/").replace("\\", "/") for p in parts if p]
    return "/" + "/".join(bits)


def _ssl_ctx(insecure: bool):
    import ssl

    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def connect(host: str, user: str, password: str):
    import ftplib

    timeout = 12

    def fail_login(exc: Exception) -> None:
        print("Connect failed:", exc)
        print("530 login: update PLESK_FTP_USER / PLESK_FTP_PASS in .env from Plesk FTP Access.")
        sys.exit(1)

    def try_ftps(insecure: bool):
        label = "FTPS (cert not verified)" if insecure else "FTPS"
        ftp = ftplib.FTP_TLS(context=_ssl_ctx(insecure), timeout=timeout)
        try:
            ftp.connect(host, 21)
            ftp.auth()
            ftp.login(user, password)
            ftp.prot_p()
            ftp.set_pasv(True)
            ftp.encoding = "utf-8"
            print(f"Connected {label} {host} as {user}")
            return ftp
        except ftplib.error_perm as exc:
            try:
                ftp.close()
            except Exception:
                pass
            fail_login(exc)
        except Exception as exc:
            try:
                ftp.close()
            except Exception:
                pass
            print(f"{label} skipped: {exc}")
            return None

    ftp = try_ftps(True) or try_ftps(False)
    if ftp:
        return ftp

    ftp = ftplib.FTP(timeout=timeout)
    try:
        ftp.connect(host, 21)
        ftp.login(user, password)
        ftp.set_pasv(True)
        ftp.encoding = "utf-8"
        print(f"Connected FTP {host} as {user}")
        return ftp
    except Exception as exc:
        try:
            ftp.close()
        except Exception:
            pass
        fail_login(exc)


def ensure_dir(ftp, remote_dir: str) -> None:
    import ftplib

    ftp.cwd("/")
    for part in remote_dir.strip("/").split("/"):
        try:
            ftp.cwd(part)
        except ftplib.error_perm:
            ftp.mkd(part)
            ftp.cwd(part)


def remote_size(ftp, remote_path: str) -> int | None:
    import ftplib

    try:
        return ftp.size(remote_path)
    except (ftplib.error_perm, ftplib.error_temp, OSError):
        try:
            name = remote_path.rsplit("/", 1)[-1]
            parent = remote_path.rsplit("/", 1)[0] or "/"
            ftp.cwd(parent)
            for entry in ftp.nlst():
                if entry == name or entry.endswith("/" + name):
                    try:
                        return ftp.size(name)
                    except (ftplib.error_perm, ftplib.error_temp, OSError):
                        return 0
        except (ftplib.error_perm, ftplib.error_temp, OSError):
            return None
    return None


def upload(ftp, local: Path, remote: str) -> None:
    ensure_dir(ftp, remote.rsplit("/", 1)[0])
    with local.open("rb") as fh:
        ftp.storbinary("STOR " + remote.rsplit("/", 1)[-1], fh)


def jobs(base: str) -> list[tuple[Path, str, bool]]:
    """(local, remote, only_if_changed)."""
    html = pick_local(
        ROOT / "colddirect-public-html" / "chiller-repair-london.html",
        ROOT / "chiller-repair-london.html",
    )
    webp = pick_local(
        ROOT / "colddirect-public-html" / "images" / "chiller-repair-london.webp",
        ROOT / "images" / "chiller-repair-london.webp",
    )
    webconfig = pick_local(
        ROOT / "colddirect-public-html" / "web.config",
        ROOT / "web.config",
    )
    out: list[tuple[Path, str, bool]] = []
    if webp:
        out.append((webp, remote_join(base, "images", webp.name), False))
    if html:
        out.append((html, remote_join(base, html.name), False))
    if webconfig:
        out.append((webconfig, remote_join(base, "web.config"), True))
    return out


def main() -> int:
    cfg = load_config()
    planned = jobs(cfg["base"])
    if not planned:
        print("No local files to deploy.")
        return 1

    print("Local vs remote")
    ftp = connect(cfg["host"], cfg["user"], cfg["password"])
    uploaded = 0
    skipped = 0
    try:
        for local, remote, only_if_changed in planned:
            local_size = local.stat().st_size
            rsize = remote_size(ftp, remote)
            remote_label = "MISSING" if rsize is None else f"{rsize} bytes"
            changed = rsize is None or rsize != local_size
            action = "UPLOAD" if (changed or not only_if_changed) else "skip"
            if only_if_changed and not changed:
                action = "skip (unchanged)"
            print(f"  {local.relative_to(ROOT)}")
            print(f"    -> {remote}")
            print(f"    local {local_size} bytes | remote {remote_label} | {action}")
            if action.startswith("skip"):
                skipped += 1
                continue
            upload(ftp, local, remote)
            uploaded += 1
            print("    uploaded")
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()

    print(f"Done. uploaded={uploaded} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
