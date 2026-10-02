#!/usr/bin/env python3
"""
Cold Direct bi-daily backup: creates a dated git tag on the current main HEAD and a
local zip archive of the full working tree, pruning zips older than 30 days so the
backups directory doesn't grow forever.

Run every 2 days via the "ColdDirect Backup" cron job.
"""
import subprocess
import zipfile
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(r"C:\Users\khora\Documents\colddirect-website")
BACKUP_DIR = ROOT / "backups"
RETENTION_DAYS = 30

# Directories/patterns to exclude from the zip (git metadata, node_modules, prior
# backups themselves — no point zipping the backups folder into a new backup)
EXCLUDE_DIRS = {".git", "node_modules", "backups", "__pycache__"}


def run(cmd, cwd=ROOT):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def main():
    BACKUP_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. Git tag on current HEAD (cheap, durable, pushed to GitHub — survives even if
    #    the local disk is lost, as long as the remote is intact)
    tag_name = f"backup-{today}"
    code, head, _ = run("git rev-parse --short HEAD")
    code, out, err = run(f'git tag -a {tag_name} -m "Automated backup {today}"')
    tag_created = code == 0
    if not tag_created and "already exists" not in err:
        print(f"WARNING: tag creation failed: {err}")

    code, out, err = run(f"git push origin {tag_name}")
    tag_pushed = code == 0

    # 2. Local zip archive of the full working tree (second safety net — covers a
    #    GitHub outage or account-level issue, not just a bad commit)
    zip_path = BACKUP_DIR / f"colddirect-backup-{today}.zip"
    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            for fn in filenames:
                full = Path(dirpath) / fn
                rel = full.relative_to(ROOT)
                zf.write(full, rel)
                file_count += 1

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)

    # 3. Prune zips older than RETENTION_DAYS (git tags are kept forever — they're
    #    cheap; only the local zips need pruning)
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    pruned = []
    for f in BACKUP_DIR.glob("colddirect-backup-*.zip"):
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            pruned.append(f.name)
            f.unlink()

    print(f"Git tag: {tag_name} (created={tag_created}, pushed={tag_pushed}, HEAD={head})")
    print(f"Zip backup: {zip_path.name} ({file_count} files, {zip_size_mb:.1f} MB)")
    print(f"Pruned {len(pruned)} old zip(s): {pruned}")


if __name__ == "__main__":
    main()
