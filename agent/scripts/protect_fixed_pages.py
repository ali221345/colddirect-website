#!/usr/bin/env python3
"""Stop overnight FTP deploys from reverting hand-fixed pages.

A page is protected in protected-pages.json (title + required phrase + min size).

Commands:
  check            Exit 1 if any local protected file fails the fingerprint
  github-excludes  Write skip globs for files that fail (used by FTP-Deploy-Action)
  restore-live     If live HTML fails and local git passes, FTP the local files
  register PATH    Pin a newly fixed page (also copies folder / public-html twins)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "protected-pages.json"
CTX = ssl._create_unverified_context()


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def load_manifest() -> dict:
    if not MANIFEST.is_file():
        return {"pages": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(data: dict) -> None:
    MANIFEST.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def html_title(text: str) -> str:
    p = _TitleParser()
    try:
        p.feed(text)
    except Exception:
        pass
    if p.title.strip():
        return re.sub(r"\s+", " ", p.title).strip()
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def fingerprint_ok(html: str, page: dict) -> bool:
    if len(html.encode("utf-8")) < int(page.get("min_bytes") or 0):
        return False
    title = html_title(html)
    expected = (page.get("expected_title") or "").strip()
    if expected and expected.casefold() not in title.casefold() and title.casefold() != expected.casefold():
        return False
    needle = page.get("must_contain") or ""
    if needle and needle not in html:
        return False
    return True


def read_local(rel: str) -> str | None:
    path = ROOT / rel
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def fetch_live(url: str) -> str | None:
    req = Request(url, headers={"User-Agent": "ColdDirect-protect-fixed-pages/1.0"})
    try:
        with urlopen(req, timeout=30, context=CTX) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError, OSError) as exc:
        print("LIVE_FETCH_FAIL", url, exc)
        return None


def _env_file() -> dict[str, str]:
    env: dict[str, str] = {}
    path = ROOT / ".env"
    if not path.is_file():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if not t or t.startswith("#") or "=" not in t:
            continue
        k, v = t.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def ftp_connect():
    from ftplib import FTP, FTP_TLS, error_perm

    file_env = _env_file()
    host = os.getenv("PLESK_FTP_HOST") or os.getenv("FTP_SERVER") or os.getenv("COLD_FTP_HOST") or file_env.get("PLESK_FTP_HOST") or file_env.get("COLD_FTP_HOST") or ""
    user = os.getenv("PLESK_FTP_USER") or os.getenv("FTP_USERNAME") or os.getenv("COLD_FTP_USER") or file_env.get("PLESK_FTP_USER") or file_env.get("COLD_FTP_USER") or ""
    password = os.getenv("PLESK_FTP_PASS") or os.getenv("FTP_PASSWORD") or os.getenv("COLD_FTP_PASS") or file_env.get("PLESK_FTP_PASS") or file_env.get("COLD_FTP_PASS") or ""
    path = os.getenv("PLESK_FTP_PATH") or os.getenv("COLD_FTP_PATH") or file_env.get("PLESK_FTP_PATH") or "/httpdocs"
    if not host or not user or not password:
        print("FTP_FAIL missing credentials")
        return None, None
    cfg = {"path": path}
    try:
        ftp = FTP_TLS()
        ftp.connect(host, 21, timeout=60)
        ftp.login(user, password)
        ftp.prot_p()
        ftp.set_pasv(True)
    except (error_perm, OSError, TimeoutError):
        ftp = FTP()
        ftp.connect(host, 21, timeout=60)
        ftp.login(user, password)
        ftp.set_pasv(True)
    ftp.cwd(path)
    return ftp, cfg


def ensure_remote_dir(ftp, remote: str) -> None:
    parts = [p for p in remote.replace("\\", "/").split("/")[:-1] if p]
    if not parts:
        return
    ftp.cwd("/")
    # start from current httpdocs after caller cwd
    for part in parts:
        try:
            ftp.cwd(part)
        except Exception:
            ftp.mkd(part)
            ftp.cwd(part)


def upload_file(ftp, local: Path, remote: str, base: str) -> None:
    remote = remote.replace("\\", "/")
    ftp.cwd(base)
    parent = remote.rsplit("/", 1)[0] if "/" in remote else ""
    if parent:
        for part in parent.split("/"):
            try:
                ftp.cwd(part)
            except Exception:
                ftp.mkd(part)
                ftp.cwd(part)
    with local.open("rb") as fh:
        ftp.storbinary("STOR " + local.name, fh)
    ftp.cwd(base)
    print("uploaded", remote)


def cmd_check() -> int:
    data = load_manifest()
    failed = 0
    for page in data.get("pages", []):
        for rel in page.get("files", []):
            html = read_local(rel)
            if html is None:
                print("MISSING", rel)
                failed += 1
                continue
            ok = fingerprint_ok(html, page)
            print(("OK" if ok else "FAIL"), rel)
            if not ok:
                failed += 1
    return 1 if failed else 0


def cmd_github_excludes() -> int:
    data = load_manifest()
    globs: list[str] = []
    for page in data.get("pages", []):
        for rel in page.get("files", []):
            html = read_local(rel)
            if html is None:
                continue
            if fingerprint_ok(html, page):
                continue
            globs.append(rel)
            globs.append("**/" + rel)
            print("SKIP_DEPLOY", rel, file=sys.stderr)
    text = "\n".join(dict.fromkeys(globs))
    out = os.getenv("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write("extra_exclude<<EOF\n")
            fh.write(text + ("\n" if text else ""))
            fh.write("EOF\n")
    else:
        print(text)
    return 0


def cmd_restore_live() -> int:
    data = load_manifest()
    to_upload: list[tuple[Path, str]] = []
    problems = 0
    for page in data.get("pages", []):
        url = page.get("url") or ""
        live = fetch_live(url) if url else None
        live_ok = bool(live) and fingerprint_ok(live, page)
        local_ok_files: list[tuple[Path, str]] = []
        local_fail = False
        for rel in page.get("files", []):
            if rel.startswith("colddirect-public-html/"):
                remote = rel.split("colddirect-public-html/", 1)[1]
            else:
                remote = rel
            html = read_local(rel)
            if html is None:
                continue
            if fingerprint_ok(html, page):
                local_ok_files.append((ROOT / rel, remote))
            else:
                local_fail = True
        print("PAGE", page.get("id"), "live_ok=" + str(live_ok), "local_good=" + str(bool(local_ok_files)))
        if live_ok:
            continue
        if local_ok_files:
            to_upload.extend(local_ok_files)
        elif local_fail or live is not None:
            print("PROTECTED_REVERTED_AND_GIT_STALE", page.get("id"))
            problems += 1
    if not to_upload:
        return 1 if problems else 0
    ftp, cfg = ftp_connect()
    if ftp is None:
        print("FTP_FAIL cannot restore protected pages")
        return 1
    try:
        seen: set[str] = set()
        for local, remote in to_upload:
            if remote in seen:
                continue
            seen.add(remote)
            upload_file(ftp, local, remote, cfg["path"])
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    return 1 if problems else 0


def sibling_files(primary: Path) -> list[Path]:
    rel = primary.relative_to(ROOT).as_posix()
    names = [primary]
    if rel.endswith(".html") and "/index.html" not in rel:
        folder = primary.with_suffix("")
        names.append(folder / "index.html")
        pub = ROOT / "colddirect-public-html" / rel
        names.append(pub)
        names.append(ROOT / "colddirect-public-html" / primary.stem / "index.html")
    elif rel.endswith("/index.html"):
        slug = primary.parent.name
        names.append(ROOT / f"{slug}.html")
        names.append(ROOT / "colddirect-public-html" / f"{slug}.html")
        names.append(ROOT / "colddirect-public-html" / slug / "index.html")
    out: list[Path] = []
    seen: set[str] = set()
    for p in names:
        key = str(p.resolve()) if p.exists() else str(p)
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return out


def cmd_register(path: str, url: str, reason: str) -> int:
    src = Path(path)
    if not src.is_absolute():
        src = ROOT / src
    if not src.is_file():
        print("MISSING", src)
        return 1
    html = src.read_text(encoding="utf-8", errors="replace")
    title = html_title(html)
    h2 = re.search(r"<h2[^>]*>(.*?)</h2>", html, re.I | re.S)
    must = re.sub(r"<[^>]+>", "", h2.group(1)).strip() if h2 else title
    must = re.sub(r"\s+", " ", must)
    if len(must) > 80:
        must = must[:80]
    copies = sibling_files(src)
    for twin in copies:
        if twin.resolve() == src.resolve():
            continue
        twin.parent.mkdir(parents=True, exist_ok=True)
        twin.write_text(html, encoding="utf-8")
        print("synced", twin.relative_to(ROOT).as_posix())
    files = []
    for p in copies:
        if p.is_file():
            files.append(p.relative_to(ROOT).as_posix())
    rel = src.relative_to(ROOT).as_posix()
    slug = src.stem if src.name != "index.html" else src.parent.name
    if not url:
        url = f"https://www.colddirect.co.uk/{slug}/"
    data = load_manifest()
    pages = [p for p in data.get("pages", []) if p.get("id") != slug]
    pages.append(
        {
            "id": slug,
            "url": url,
            "files": files or [rel],
            "expected_title": title,
            "must_contain": must,
            "min_bytes": max(1500, int(len(html.encode("utf-8")) * 0.7)),
            "protected_at": __import__("datetime").date.today().isoformat(),
            "reason": reason or "Hand-fixed page",
        }
    )
    data["pages"] = pages
    save_manifest(data)
    print("protected", slug, "files", len(files))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "github-excludes", "restore-live", "register"])
    parser.add_argument("path", nargs="?", help="HTML file for register")
    parser.add_argument("--url", default="")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()
    if args.command == "check":
        return cmd_check()
    if args.command == "github-excludes":
        return cmd_github_excludes()
    if args.command == "restore-live":
        return cmd_restore_live()
    if not args.path:
        print("register needs a file path")
        return 1
    return cmd_register(args.path, args.url, args.reason)


if __name__ == "__main__":
    raise SystemExit(main())
