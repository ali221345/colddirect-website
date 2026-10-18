#!/usr/bin/env python3
"""
Pulls the latest live files modified by `auto-seo.aspx` from WHUK Plesk FTP (/httpdocs)
into the local workspace root and mirrors them into `colddirect-public-html/`.
Downloads:
- auto-seo.aspx
- sitemap.xml
- all .html and .asp files in /httpdocs and its live page subdirectories (e.g. <slug>/index.html, blog/<slug>/index.html)
"""
from __future__ import annotations

import ftplib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "colddirect-public-html"

SKIP_REMOTE_DIRS = {
    ".git",
    ".github",
    ".cursor",
    ".well-known",
    "node_modules",
    "images",
    "assets",
    "css",
    "js",
    "fonts",
    "vendor",
    "cgi-bin",
    "plesk-stat",
    "webstat",
    "webstat-ssl",
    "ftpstat",
    "anon_ftp",
    "error_docs",
    " cold-direct-backup",
    "colddirect-public-html",
    "_old_site_backup",
    "_wa_src",
    "plesk-upload",
    "plesk-hero-upload",
    "preview-colddirect-homepage",
    "templates",
    "reports",
    "seo-audit",
    "logs",
    "mnt",
    "public",
    "agent",
    "tools",
    "scripts",
    "App_Data",
    "app",
    "bookings",
    "includes",
}

SKIP_ROOT_FILES = {
    "_backup_index_old.html",
    "preview-colddirect-homepage.html",
}


def load_ftp_creds() -> tuple[str, int, str, str, str]:
    sftp_path = ROOT / ".vscode" / "sftp.json"
    if sftp_path.exists():
        data = json.loads(sftp_path.read_text(encoding="utf-8"))
        return (
            data.get("host", "5.77.41.163"),
            int(data.get("port", 21)),
            data.get("username", "colddir"),
            data.get("password", ""),
            data.get("remotePath", "/httpdocs").rstrip("/"),
        )
    return (
        os.environ.get("FTP_SERVER", "5.77.41.163"),
        21,
        os.environ.get("FTP_USERNAME", "colddir"),
        os.environ.get("FTP_PASSWORD", ""),
        "/httpdocs",
    )


def list_ftp_dir(ftp: ftplib.FTP, remote_dir: str) -> list[tuple[str, str]]:
    """Parses Windows IIS FTP (`MM-DD-YY HH:MMAM <DIR>|size name`) or Unix (`drwxr-xr-x ... name`) listings."""
    lines: list[str] = []
    ftp.dir(remote_dir, lines.append)
    entries: list[tuple[str, str]] = []
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        # Windows IIS FTP format: "10-18-26  08:21PM       <DIR>          about" or "10-18-26  08:21PM                 8733 about-us.html"
        parts_win = line_str.split(None, 3)
        if len(parts_win) == 4 and "-" in parts_win[0] and (parts_win[1].endswith("AM") or parts_win[1].endswith("PM")):
            name = parts_win[3]
            if name in (".", ".."):
                continue
            etype = "dir" if parts_win[2] == "<DIR>" else "file"
            entries.append((name, etype))
            continue
        # Unix format fallback
        parts_unix = line_str.split(None, 8)
        if len(parts_unix) >= 9:
            name = parts_unix[8]
            if name in (".", ".."):
                continue
            etype = "dir" if line_str.startswith("d") else "file"
            entries.append((name, etype))
    return entries


def download_file(ftp: ftplib.FTP, remote_path: str, local_path: Path) -> bool:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = local_path.with_suffix(local_path.suffix + ".tmp")
    try:
        with open(tmp_path, "wb") as f:
            ftp.retrbinary(f"RETR {remote_path}", f.write)
        tmp_path.replace(local_path)
        return True
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink()
        print(f"[WARN] Could not download {remote_path}: {exc}")
        return False


def mirror_to_public_html(rel_path: str) -> None:
    src = ROOT / rel_path
    dst = MIRROR / rel_path
    if not src.exists():
        return
    if dst.exists() or dst.parent.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    host, port, user, password, base_dir = load_ftp_creds()
    print(f"Connecting to {host}:{port} as {user} (base: {base_dir})...")
    ftp = ftplib.FTP()
    ftp.connect(host, port, timeout=60)
    ftp.login(user, password)
    ftp.set_pasv(True)

    downloaded_files: list[str] = []

    def walk_remote(rel_dir: str, depth: int = 0) -> None:
        if depth > 3:
            return
        remote_dir = f"{base_dir}/{rel_dir}".rstrip("/")
        entries = list_ftp_dir(ftp, remote_dir)
        for name, etype in entries:
            rel_item = f"{rel_dir}/{name}".lstrip("/")
            if etype == "dir":
                if name in SKIP_REMOTE_DIRS or name.startswith("."):
                    continue
                walk_remote(rel_item, depth + 1)
            elif etype == "file":
                if depth == 0 and name in SKIP_ROOT_FILES:
                    continue
                lower = name.lower()
                if (
                    lower.endswith(".html")
                    or lower.endswith(".asp")
                    or lower.endswith(".aspx")
                    or (depth == 0 and lower == "sitemap.xml")
                ):
                    remote_file = f"{base_dir}/{rel_item}"
                    local_file = ROOT / rel_item
                    if download_file(ftp, remote_file, local_file):
                        downloaded_files.append(rel_item)
                        mirror_to_public_html(rel_item)

    walk_remote("", 0)

    try:
        ftp.quit()
    except Exception:
        ftp.close()

    html_count = sum(1 for f in downloaded_files if f.lower().endswith(".html"))
    asp_count = sum(1 for f in downloaded_files if f.lower().endswith((".asp", ".aspx")))
    print(
        f"Sync complete! Downloaded {len(downloaded_files)} total files "
        f"({html_count} .html, {asp_count} .asp/.aspx, plus sitemap.xml) and mirrored to colddirect-public-html/."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
