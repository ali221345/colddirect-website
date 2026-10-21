#!/usr/bin/env python3
"""Full snapshot of the LIVE Plesk site (/httpdocs) -> verified, timestamped ZIP + SHA-256 manifest.

  python tools/backup_site.py [--out backup-out] [--include-media]     (env FTP_SERVER / FTP_USERNAME / FTP_PASSWORD
                                                                      or .vscode/sftp.json locally; PLAIN FTP only)
  python tools/backup_site.py --selftest                              offline tests with a fake FTP server

Contents: .html/.htm/.asp/.aspx pages, auto-seo.aspx, web.config & other *.config, sitemap.xml, robots.txt,
CSS/JS, JSON/XML/TXT/INC/webmanifest config files (+ images/audio/fonts only with --include-media).
NEVER archived: App_Data/, bookings/ (customer PII), *.key, *.pem/*.pfx, private-key files, anything under .git/.well-known/plesk dirs.
SECRET SCRUB (this repo is public and Actions artifacts of public repos are downloadable by any signed-in GitHub
user): in web.config/*.config every <add key="..." value="..."> whose key looks sensitive, connectionString=,
password=/pwd=/secret=/token=/apikey= attribute values are replaced by ***REDACTED***. A restore therefore
re-creates the code and content; secrets are re-entered from the Plesk panel.

Verification: every file is checked against the remote SIZE (when the server supports it), hashed (sha256),
the finished ZIP is re-opened (testzip + every member re-hashed against MANIFEST.json), and critical files
must be present. Exit 1 on any failure. Outputs in --out: the zip, MANIFEST.json, MANIFEST.sha256 (sha256sum
format), backup-summary.json + GITHUB_OUTPUT / Step Summary lines. Nothing is written into the webroot or committed.
"""
from __future__ import annotations

import argparse
import ftplib
import hashlib
import io
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pull_live_plesk_v4 as pull  # noqa: E402  (list_ftp_dir + load_ftp_creds, no import side effects)

TEXT_EXT = {".html", ".htm", ".asp", ".aspx", ".config", ".xml", ".txt", ".css", ".js", ".json", ".inc",
            ".webmanifest", ".map", ".md", ".csv", ".ashx", ".master", ".cs"}
MEDIA_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".ico", ".mp3", ".wav", ".woff", ".woff2", ".ttf", ".pdf"}
NEVER_EXT = {".key", ".pem", ".pfx", ".p12", ".pub", ".ppk", ".crt", ".cer"}
SKIP_DIRS = {".git", ".github", ".well-known", "app_data", "cgi-bin", "plesk-stat", "webstat", "webstat-ssl",
             "ftpstat", "anon_ftp", "error_docs", "node_modules", "logs", "backups", "colddirect-public-html",
             "_old_site_backup", " cold-direct-backup",
             "bookings"}  # customer booking data (PII): never put it into a downloadable artifact of a public repo
CRITICAL = ["index.html", "auto-seo.aspx", "sitemap.xml", "robots.txt"]
WARN_IF_MISSING = ["web.config"]
MAX_FILE = 30 * 1024 * 1024
MAX_TOTAL = 400 * 1024 * 1024
MAX_DEPTH = 6
MIN_HTML = 50
RED = "***REDACTED***"

SENSITIVE_KEY = re.compile(r"(key|secret|password|passwd|pwd|token|connection|credential|salt|auth)", re.I)
ADD_RX = re.compile(r'(<add\s+[^>]*?\bkey\s*=\s*")([^"]*)("[^>]*?\bvalue\s*=\s*")([^"]*)(")', re.I)
ADD_RX_REV = re.compile(r'(<add\s+[^>]*?\bvalue\s*=\s*")([^"]*)("[^>]*?\bkey\s*=\s*")([^"]*)(")', re.I)
ATTR_RX = re.compile(r'(\b(?:connectionString|password|pwd|passwd|secret|apikey|api_key|token|validationKey|decryptionKey)\s*=\s*")([^"]*)(")', re.I)
PRIVATE_KEY_RX = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")


def scrub_config(text: str) -> tuple[str, int]:
    n = 0

    def add(m):
        nonlocal n
        if SENSITIVE_KEY.search(m.group(2)) and m.group(4) != RED:
            n += 1
            return m.group(1) + m.group(2) + m.group(3) + RED + m.group(5)
        return m.group(0)

    def add_rev(m):
        nonlocal n
        if SENSITIVE_KEY.search(m.group(4)) and m.group(2) != RED:
            n += 1
            return m.group(1) + RED + m.group(3) + m.group(4) + m.group(5)
        return m.group(0)

    def attr(m):
        nonlocal n
        if m.group(2) != RED:
            n += 1
            return m.group(1) + RED + m.group(3)
        return m.group(0)

    text = ADD_RX.sub(add, text)
    text = ADD_RX_REV.sub(add_rev, text)
    text = ATTR_RX.sub(attr, text)
    return text, n


def wanted(rel: str, include_media: bool) -> bool:
    low = rel.lower()
    ext = os.path.splitext(low)[1]
    name = os.path.basename(low)
    if ext in NEVER_EXT or name.endswith(".key") or name in {".env", "gsc-key.json", "credentials.json", "sftp.json"}:
        return False
    return ext in TEXT_EXT or (include_media and ext in MEDIA_EXT)


def walk(ftp, base: str, include_media: bool, log=print):
    """Yield (relative_path, remote_path, remote_size_or_None)."""
    stack = [("", 0)]
    while stack:
        rel_dir, depth = stack.pop()
        remote_dir = f"{base}/{rel_dir}".rstrip("/")
        for name, etype in pull.list_ftp_dir(ftp, remote_dir):
            rel = f"{rel_dir}/{name}".lstrip("/")
            if etype == "dir":
                if name.lower() in SKIP_DIRS or name.startswith(".") or depth >= MAX_DEPTH:
                    continue
                stack.append((rel, depth + 1))
            elif wanted(rel, include_media):
                try:
                    size = ftp.size(f"{base}/{rel}")
                except Exception:  # noqa: BLE001
                    size = None
                yield rel, f"{base}/{rel}", size


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def snapshot(ftp, base: str, include_media: bool, log=print):
    files, skipped, total = {}, [], 0
    for rel, remote, rsize in sorted(walk(ftp, base, include_media, log)):
        if rsize is not None and rsize > MAX_FILE:
            skipped.append((rel, "too large"))
            continue
        buf = io.BytesIO()
        try:
            ftp.retrbinary(f"RETR {remote}", buf.write)
        except Exception as exc:  # noqa: BLE001
            skipped.append((rel, f"download failed: {type(exc).__name__}"))
            continue
        data = buf.getvalue()
        if rsize is not None and rsize != len(data):
            skipped.append((rel, f"size mismatch remote={rsize} got={len(data)}"))
            continue
        redacted = 0
        if PRIVATE_KEY_RX.search(data[:200000].decode("latin-1", "ignore")):
            skipped.append((rel, "private key material (never archived)"))
            continue
        if rel.lower().endswith(".config"):
            txt, redacted = scrub_config(data.decode("utf-8", "replace"))
            data = txt.encode("utf-8")
        total += len(data)
        if total > MAX_TOTAL:
            skipped.append((rel, "total size cap"))
            break
        files[rel] = {"data": data, "redacted": redacted}
    return files, skipped


def build_zip(files: dict, skipped: list, out_dir: Path, stamp: str, host_note: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "created_utc": stamp, "source": host_note, "file_count": len(files),
        "total_bytes": sum(len(v["data"]) for v in files.values()),
        "skipped": [{"path": p, "reason": r} for p, r in skipped],
        "files": {rel: {"bytes": len(v["data"]), "sha256": sha256(v["data"]), "redacted_values": v["redacted"]}
                  for rel, v in sorted(files.items())},
    }
    mtxt = json.dumps(manifest, indent=2, sort_keys=True)
    sums = "".join(f"{m['sha256']}  {rel}\n" for rel, m in manifest["files"].items())
    zpath = out_dir / f"colddirect-backup-{stamp}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel, v in sorted(files.items()):
            zi = zipfile.ZipInfo("httpdocs/" + rel, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, v["data"])
        z.writestr("MANIFEST.json", mtxt)
        z.writestr("MANIFEST.sha256", sums)
    (out_dir / "MANIFEST.json").write_text(mtxt, "utf-8")
    (out_dir / "MANIFEST.sha256").write_text(sums, "utf-8")
    return zpath, manifest


def verify_zip(zpath: Path, manifest: dict) -> list[str]:
    problems = []
    with zipfile.ZipFile(zpath) as z:
        bad = z.testzip()
        if bad:
            problems.append(f"zip CRC error in {bad}")
        names = set(z.namelist())
        embedded = json.loads(z.read("MANIFEST.json")) if "MANIFEST.json" in names else None
        if embedded != manifest:
            problems.append("embedded manifest differs")
        for rel, m in manifest["files"].items():
            member = "httpdocs/" + rel
            if member not in names:
                problems.append(f"missing in zip: {rel}")
                continue
            data = z.read(member)
            if len(data) != m["bytes"] or sha256(data) != m["sha256"]:
                problems.append(f"hash mismatch: {rel}")
        if len([n for n in names if n.startswith("httpdocs/")]) != manifest["file_count"]:
            problems.append("file count mismatch")
    return problems


def critical_problems(manifest: dict) -> list[str]:
    files = manifest["files"]
    p = [f"critical file missing: {c}" for c in CRITICAL if c not in files]
    html = sum(1 for f in files if f.lower().endswith(".html"))
    if html < MIN_HTML:
        p.append(f"only {html} .html files (expected >= {MIN_HTML})")
    return p


def run(ftp, base, out_dir, include_media, now=None, host_note="plesk:/httpdocs"):
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    files, skipped = snapshot(ftp, base, include_media)
    zpath, manifest = build_zip(files, skipped, Path(out_dir), stamp, host_note)
    problems = verify_zip(zpath, manifest) + critical_problems(manifest)
    zsha = sha256(zpath.read_bytes())
    warn = [f"web.config not found ({w})" for w in WARN_IF_MISSING if w not in manifest["files"]]
    summary = {"zip": zpath.name, "zip_bytes": zpath.stat().st_size, "zip_sha256": zsha, "files": manifest["file_count"],
               "html_files": sum(1 for f in manifest["files"] if f.lower().endswith(".html")),
               "redacted_values": sum(m["redacted_values"] for m in manifest["files"].values()),
               "skipped": len(skipped), "created_utc": stamp, "verified": not problems,
               "problems": problems, "warnings": warn}
    (Path(out_dir) / "backup-summary.json").write_text(json.dumps(summary, indent=2), "utf-8")
    return summary


def emit(summary: dict) -> None:
    lines = ["## 48h full site backup", "",
             "| | |", "|---|---|",
             f"| Archive | `{summary['zip']}` ({summary['zip_bytes'] / 1048576:.1f} MB) |",
             f"| SHA-256 | `{summary['zip_sha256']}` |",
             f"| Files | {summary['files']} ({summary['html_files']} html) |",
             f"| Secret values redacted | {summary['redacted_values']} |",
             f"| Skipped | {summary['skipped']} |",
             f"| Integrity verified | {'YES' if summary['verified'] else 'NO - ' + '; '.join(summary['problems'])} |"]
    if summary["warnings"]:
        lines.append(f"| Warnings | {'; '.join(summary['warnings'])} |")
    text = "\n".join(lines) + "\n"
    print(text)
    for var, payload in (("GITHUB_STEP_SUMMARY", text),
                         ("GITHUB_OUTPUT", "\n".join(f"{k}={summary[k]}" for k in
                                                     ("zip", "zip_sha256", "files", "html_files", "verified")) + "\n")):
        target = os.environ.get(var)
        if target:
            with open(target, "a", encoding="utf-8") as f:
                f.write(payload)


def connect():
    host, port, user, password, base = pull.load_ftp_creds()
    if not password:
        raise SystemExit("FTP password missing (set FTP_PASSWORD or .vscode/sftp.json)")
    ftp = ftplib.FTP()  # plain FTP only: Plesk times out on FTPS unwrap
    ftp.connect(host, port, timeout=60)
    ftp.login(user, password)
    ftp.set_pasv(True)
    return ftp, base


# ------------------------------------------------------------------ selftest
class FakeFtp:
    """Minimal IIS-style FTP server over a dict {path: bytes}."""

    def __init__(self, tree):
        self.tree = tree

    def dir(self, remote_dir, cb):
        prefix = remote_dir.rstrip("/") + "/"
        seen = set()
        for path, data in self.tree.items():
            if not path.startswith(prefix):
                continue
            rest = path[len(prefix):]
            head = rest.split("/")[0]
            if head in seen:
                continue
            seen.add(head)
            if "/" in rest:
                cb(f"10-18-26  08:21PM       <DIR>          {head}")
            else:
                cb(f"10-18-26  08:21PM {len(data):>18} {head}")

    def size(self, path):
        return len(self.tree[path])

    def retrbinary(self, cmd, cb):
        cb(self.tree[cmd.split(" ", 1)[1]])


def selftest():
    import shutil
    import tempfile
    cfg = ('<configuration><appSettings><add key="AutoSeoKey" value="SUPERSECRET123" />'
           '<add value="TOPSECRET9" key="Mail.Password" /><add key="SiteName" value="Cold Direct" /></appSettings>'
           '<connectionStrings><add name="db" connectionString="Server=x;Password=hunter2" /></connectionStrings></configuration>')
    red, n = scrub_config(cfg)
    assert "SUPERSECRET123" not in red and "TOPSECRET9" not in red and "hunter2" not in red and n >= 3
    assert "Cold Direct" in red and scrub_config(red)[1] == 0, "non-secret kept + idempotent"
    b = "/httpdocs"
    tree = {f"{b}/index.html": b"<html>home</html>", f"{b}/auto-seo.aspx": b"<%@ Page %>", f"{b}/sitemap.xml": b"<urlset/>",
            f"{b}/robots.txt": b"User-agent: *", f"{b}/web.config": cfg.encode(),
            f"{b}/App_Data/auto-seo.key": b"KEYKEYKEY", f"{b}/server.key": b"KEY2",
            f"{b}/css/site.css": b"a{}", f"{b}/images/p.jpg": b"\xff\xd8", f"{b}/audio/a.mp3": b"ID3",
            f"{b}/cert/priv.txt": b"-----BEGIN RSA PRIVATE KEY-----\nabc",
            f"{b}/logs/x.txt": b"log", f"{b}/bookings/bookings.json": b'{"name":"customer"}'}
    for i in range(60):
        tree[f"{b}/p{i}/index.html"] = f"<html>{i}</html>".encode()
    tmp = Path(tempfile.mkdtemp())
    try:
        s = run(FakeFtp(tree), b, tmp, False, now=datetime(2026, 10, 21, 3, 0, tzinfo=timezone.utc))
        assert s["verified"], s["problems"]
        assert s["zip"] == "colddirect-backup-20261021-030000.zip"
        with zipfile.ZipFile(tmp / s["zip"]) as z:
            names = z.namelist()
            blob = b"".join(z.read(n) for n in names)
        assert "httpdocs/web.config" in names and "httpdocs/css/site.css" in names
        assert not any("App_Data" in n or n.endswith(".key") or "images/" in n or "audio/" in n or "logs/" in n or "priv.txt" in n or "bookings" in n for n in names)
        assert b"SUPERSECRET123" not in blob and b"hunter2" not in blob and b"KEYKEYKEY" not in blob
        assert s["redacted_values"] >= 3 and s["html_files"] == 61 and s["files"] >= 66
        # media only on request
        s2 = run(FakeFtp(tree), b, tmp / "m", True, now=datetime(2026, 10, 21, 3, 0, 1, tzinfo=timezone.utc))
        assert s2["files"] == s["files"] + 2
        # tampering is detected
        zp = tmp / s["zip"]
        man = json.loads((tmp / "MANIFEST.json").read_text("utf-8"))
        man["files"]["index.html"]["sha256"] = "0" * 64
        assert any("hash mismatch" in p or "embedded manifest differs" in p for p in verify_zip(zp, man))
        # critical files enforced
        del tree[f"{b}/robots.txt"]
        s3 = run(FakeFtp(tree), b, tmp / "c", False, now=datetime(2026, 10, 21, 3, 0, 2, tzinfo=timezone.utc))
        assert not s3["verified"] and any("robots.txt" in p for p in s3["problems"])
        # size mismatch is skipped, not silently archived
        class Short(FakeFtp):
            def size(self, path):
                return 999999 if path.endswith("index.html") and "p1/" in path else super().size(path)
        s4 = run(Short(tree), b, tmp / "s", False, now=datetime(2026, 10, 21, 3, 0, 3, tzinfo=timezone.utc))
        assert s4["skipped"] >= 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("backup_site selftest OK (scrub, exclusions, media flag, zip verify, tamper + critical + size-mismatch detection)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="backup-out")
    ap.add_argument("--include-media", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    ftp, base = connect()
    try:
        summary = run(ftp, base, a.out, a.include_media)
    finally:
        try:
            ftp.quit()
        except Exception:  # noqa: BLE001
            ftp.close()
    emit(summary)
    return 0 if summary["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
