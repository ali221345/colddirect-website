#!/usr/bin/env python3
"""Compress mapped page images, fix HTML, optional Plesk FTPS upload."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = "20260913f"
MAX_BYTES = 100 * 1024
CWEBP_CANDIDATES = [
    Path(os.environ.get("TEMP", "/tmp"))
    / "libwebp-1.5.0"
    / "libwebp-1.5.0-windows-x64"
    / "bin"
    / "cwebp.exe",
    Path("/usr/bin/cwebp"),
    Path("/usr/local/bin/cwebp"),
]

MAP = [
    {
        "sources": [
            "commercial_vrf_rooftop_units.webp",
            "air-conditioning-repair-london.webp",
        ],
        "dest": "air-conditioning-repair-london.webp",
    },
    {
        "sources": [
            "supermarket_dairy_drinks_display.webp",
            "supermarket-fridge-repair-london.webp",
        ],
        "dest": "supermarket-fridge-repair-london.webp",
    },
    {
        "sources": [
            "supermarket_island_freezer.webp",
            "supermarket-island-freezer.webp",
        ],
        "dest": "supermarket-island-freezer.webp",
    },
]

HTML_PAIRS = [
    ROOT / "air-conditioning-repair-london.html",
    ROOT / "colddirect-public-html" / "air-conditioning-repair-london.html",
    ROOT / "supermarket-fridge-repair-london.html",
    ROOT / "colddirect-public-html" / "supermarket-fridge-repair-london.html",
]


def find_cwebp() -> Path | None:
    for p in CWEBP_CANDIDATES:
        if p.is_file():
            return p
    found = shutil.which("cwebp")
    return Path(found) if found else None


def source_dirs() -> list[Path]:
    home = Path.home()
    return [
        Path("/mnt/data"),
        ROOT / "mnt" / "data",
        Path(r"C:\mnt\data"),
        Path(
            r"C:\Users\khora\.cursor\projects\c-Users-khora-Documents-colddirect-website\assets"
        ),
        ROOT / "images",
        ROOT / "colddirect-public-html" / "images",
        home / "Downloads",
    ]


def find_source(names: list[str]) -> Path | None:
    for folder in source_dirs():
        if not folder.is_dir():
            continue
        for name in names:
            p = folder / name
            if p.is_file():
                return p
    return None


def encode_cwebp(cwebp: Path, src: Path, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    last = 0
    for q in (75, 65, 55, 45):
        subprocess.run(
            [str(cwebp), "-q", str(q), "-resize", "800", "0", str(src), "-o", str(dest)],
            check=True,
            capture_output=True,
        )
        last = dest.stat().st_size
        if last <= MAX_BYTES:
            return last
    return last


def encode_pil(src: Path, dest: Path) -> int:
    from PIL import Image

    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGB")
    w, h = im.size
    if w > 800:
        im = im.resize((800, max(1, int(h * 800 / w))), Image.Resampling.LANCZOS)
    last = 0
    for q in (75, 65, 55, 45):
        im.save(dest, "WEBP", quality=q, method=6)
        last = dest.stat().st_size
        if last <= MAX_BYTES:
            return last
    return last


def encode(src: Path, dest_name: str, cwebp: Path | None) -> tuple[Path, Path, int]:
    a = ROOT / "images" / dest_name
    b = ROOT / "colddirect-public-html" / "images" / dest_name
    tmp = ROOT / "images" / (dest_name + ".tmp.webp")
    if cwebp:
        size = encode_cwebp(cwebp, src, tmp)
    else:
        size = encode_pil(src, tmp)
    shutil.copy2(tmp, a)
    shutil.copy2(tmp, b)
    tmp.unlink(missing_ok=True)
    return a, b, size


AIRCON_STYLE = """  <style>
    section.cd-seo-hero{position:relative;background:#0a2540 !important;background-image:none !important;color:#fff !important;min-height:0 !important;padding:24px 20px 36px !important}
    section.cd-seo-hero::before{display:none !important;content:none !important;background:none !important}
    section.cd-seo-hero .wrap{position:relative;z-index:1;padding:12px 0 8px !important}
    section.cd-seo-hero h1,section.cd-seo-hero p,section.cd-seo-hero .kicker,section.cd-seo-hero .lead{color:#fff !important}
    section.cd-seo-hero .cta-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
    section.cd-seo-hero .btn{background:#0a2540 !important;color:#fff !important;border:1px solid #fff}
    section.cd-seo-hero .btn-light{background:#fff !important;color:#0a2540 !important}
    section.cd-seo-hero img{display:block;margin:18px auto 0;max-width:800px;width:100%;height:auto;object-fit:cover;border-radius:8px}
    .faults li{margin:0 0 10px}
    .area-list{display:flex;flex-wrap:wrap;gap:8px 18px;padding:0;list-style:disc inside}
  </style>"""

AIRCON_IMG = (
    f'  <img src="/images/air-conditioning-repair-london.webp?v={CACHE}" '
    'alt="Commercial Air Conditioning Repair London - VRF rooftop units" '
    'style="max-width:800px;width:100%;height:auto;object-fit:cover;border-radius:8px" loading="lazy">'
)


def patch_aircon(text: str) -> str:
    text = re.sub(
        r"url\(['\"]?/images/(?:display-cabinets|pub-cellar|catering-repair|commercial-freezer)[^'\"]*['\"]\)",
        "none",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"<style>.*?</style>",
        AIRCON_STYLE,
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"<img[^>]*air-conditioning-repair-london\.webp[^>]*>",
        AIRCON_IMG.strip(),
        text,
        flags=re.I,
    )
    if "air-conditioning-repair-london.webp" not in text:
        text = text.replace(
            "</div></section>\n<section class=\"section\">",
            AIRCON_IMG + "\n</div></section>\n<section class=\"section\">",
            1,
        )
    text = text.replace("?v=20260913e", f"?v={CACHE}")
    return text


def patch_supermarket(text: str) -> str:
    text = re.sub(
        r"url\(['\"]?/images/(?:display-cabinets|pub-cellar|dairy-cabinet-repair)[^'\"]*['\"]\)",
        "none",
        text,
        flags=re.I,
    )
    text = text.replace("?v=20260913e", f"?v={CACHE}")
    if f"supermarket-fridge-repair-london.webp?v={CACHE}" not in text:
        text = re.sub(
            r"<img[^>]*supermarket-fridge-repair-london\.webp[^>]*>",
            (
                f'<img src="/images/supermarket-fridge-repair-london.webp?v={CACHE}" '
                'alt="Supermarket fridge repair London - dairy and drinks display cabinet" '
                'style="max-width:800px;width:100%;height:auto;object-fit:cover;border-radius:8px" loading="lazy">'
            ),
            text,
            count=1,
            flags=re.I,
        )
    if f"supermarket-island-freezer.webp?v={CACHE}" not in text:
        text = re.sub(
            r"<img[^>]*supermarket-island-freezer\.webp[^>]*>",
            (
                f'<img class="seo-inline-img" src="/images/supermarket-island-freezer.webp?v={CACHE}" '
                'alt="Supermarket island freezer repair London" '
                'style="max-width:800px;width:100%;height:auto;object-fit:cover;border-radius:8px" loading="lazy">'
            ),
            text,
            count=1,
            flags=re.I,
        )
    if "background-image:none" not in text:
        text = text.replace(
            "section.cd-seo-hero{",
            "section.cd-seo-hero{background-image:none !important;",
            1,
        )
    return text


def ftp_creds() -> tuple[str, str, str] | None:
    host = os.environ.get("PLESK_FTP_HOST") or os.environ.get("FTP_HOST")
    user = (
        os.environ.get("PLESK_FTP_USER")
        or os.environ.get("FTP_USER")
        or (os.environ.get("USER") if host else None)
    )
    password = (
        os.environ.get("PLESK_FTP_PASS")
        or os.environ.get("PLESK_FTP_PASSWORD")
        or os.environ.get("FTP_PASS")
        or os.environ.get("PASS")
    )
    if host and user and password:
        return host, user, password
    return None


def ftp_upload(files: list[tuple[Path, str]]) -> list[str]:
    import ftplib
    import ssl

    creds = ftp_creds()
    if not creds:
        return ["FTP skipped: set PLESK_FTP_HOST, PLESK_FTP_USER, PLESK_FTP_PASS"]
    host, user, password = creds
    ctx = ssl.create_default_context()
    ftp = ftplib.FTP_TLS(context=ctx, timeout=60)
    log = []
    try:
        ftp.connect(host, 21)
        ftp.auth()
        ftp.login(user, password)
        ftp.prot_p()
        for local, remote in files:
            remote = remote.replace("\\", "/")
            dirname = remote.rsplit("/", 1)[0]
            try:
                ftp.cwd("/")
                for part in dirname.strip("/").split("/"):
                    try:
                        ftp.cwd(part)
                    except ftplib.error_perm:
                        ftp.mkd(part)
                        ftp.cwd(part)
            except ftplib.error_perm as exc:
                log.append(f"FTP cwd failed {remote}: {exc}")
                continue
            with local.open("rb") as fh:
                ftp.storbinary("STOR " + remote.rsplit("/", 1)[-1], fh)
            log.append(f"uploaded {local.name} -> {remote}")
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    return log


def write_report(rows: list[str], ftp_log: list[str], html_notes: list[str]) -> None:
    report = ROOT / "ALL-IMAGES-FIXED.md"
    block = [
        "",
        f"## image-deploy-agent run (`scripts/deploy_images.py`) cache `{CACHE}`",
        "",
        *rows,
        "",
        "### HTML",
        *[f"- {n}" for n in html_notes] or ["- (no HTML notes)"],
        "",
        "### FTP",
        *[f"- {n}" for n in ftp_log],
        "",
    ]
    prev = report.read_text(encoding="utf-8") if report.exists() else "# ALL-IMAGES-FIXED\n"
    report.write_text(prev.rstrip() + "\n" + "\n".join(block), encoding="utf-8")


def main() -> int:
    cwebp = find_cwebp()
    print("cwebp:", cwebp or "NOT FOUND (will try PIL)")
    rows: list[str] = []
    produced: list[Path] = []
    for item in MAP:
        src = find_source(item["sources"])
        if not src:
            rows.append(f"- MISSING source for {item['dest']} (looked for {item['sources']})")
            print("MISSING", item["dest"])
            continue
        a, b, size = encode(src, item["dest"], cwebp)
        kb = size / 1024
        ok = "OK" if size <= MAX_BYTES else "OVER 100KB"
        line = f"- `{item['dest']}` from `{src}` -> {kb:.1f} KB ({ok}) both trees"
        rows.append(line)
        print(line)
        produced.extend([a, b])

    html_notes: list[str] = []
    html_changed: list[Path] = []
    for path in HTML_PAIRS:
        if not path.is_file():
            continue
        orig = path.read_text(encoding="utf-8")
        text = orig
        if "air-conditioning" in path.name:
            text = patch_aircon(text)
            bad = []
            for needle in ("display-cabinets", "pub-cellar"):
                if needle in text:
                    bad.append(needle)
            html_notes.append(
                f"{path.name}: air-con img cache {CACHE}; leftover kitchen filenames={bad or 'none'}"
            )
        elif "supermarket-fridge" in path.name:
            text = patch_supermarket(text)
            html_notes.append(f"{path.name}: supermarket cache {CACHE}, 800px img")
        if text != orig:
            path.write_text(text, encoding="utf-8")
            html_changed.append(path)

    ftp_files: list[tuple[Path, str]] = []
    for p in produced:
        if p.exists() and "colddirect-public-html" not in str(p):
            ftp_files.append((p, "/httpdocs/images/" + p.name))
    for p in html_changed:
        if "colddirect-public-html" not in str(p):
            ftp_files.append((p, "/httpdocs/" + p.name))
    ftp_log = ftp_upload(ftp_files) if ftp_files else ["FTP skipped: nothing to upload"]
    for line in ftp_log:
        print(line)
    write_report(rows, ftp_log, html_notes)
    overs = [p for p in produced if p.exists() and p.stat().st_size > MAX_BYTES]
    return 1 if overs else 0


if __name__ == "__main__":
    sys.exit(main())
