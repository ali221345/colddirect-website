import ftplib, json, os, sys
from pathlib import Path
"""Upload repo files to Plesk /httpdocs with PLAIN ftplib.FTP() (FTPS hangs on this host).
Credentials come from the gitignored .vscode/sftp.json. Honors deploy_guard + html_preflight.
Usage: python tools/upload_plain.py <relative/path> [...]"""
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from deploy_guard import should_skip_upload
from html_preflight import preflight_ok

cfg = json.load(open(ROOT / ".vscode" / "sftp.json", encoding="utf-8"))
names = sys.argv[1:]
ftp = ftplib.FTP()
ftp.connect(cfg["host"], int(cfg.get("port", 21)), timeout=40)
ftp.login(cfg["username"], cfg["password"])
base = cfg.get("remotePath") or "/httpdocs"
ftp.cwd(base)
print("connected (plain FTP), base", base, flush=True)

def ensure(rel):
    ftp.cwd(base)
    for part in rel.split("/"):
        if not part:
            continue
        try:
            ftp.cwd(part)
        except Exception:
            ftp.mkd(part)
            ftp.cwd(part)
    ftp.cwd(base)

try:
    for rel in names:
        local = ROOT / rel
        assert local.is_file(), rel
        if should_skip_upload(rel):
            print("SKIPPED (deploy guard)", rel); continue
        if not preflight_ok(local, rel):
            print("SKIPPED (html preflight)", rel); continue
        parent = os.path.dirname(rel).replace("\\", "/")
        if parent:
            ensure(parent)
            ftp.cwd(base + "/" + parent)
        else:
            ftp.cwd(base)
        with local.open("rb") as fh:
            ftp.storbinary("STOR " + os.path.basename(rel), fh)
        ftp.cwd(base)
        print("uploaded", rel, local.stat().st_size, flush=True)
finally:
    try:
        ftp.quit()
    except Exception:
        ftp.close()
print("UPLOAD DONE")
