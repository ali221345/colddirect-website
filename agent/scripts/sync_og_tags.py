"""
Syncs og:title / og:description with the (now updated) <title> and
meta name="description" on each page that got the same-day tag applied.
Run AFTER add_sameday_tag.py --apply. Idempotent.
"""
import re
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def sync_og(html):
    changed = False
    tm = re.search(r'<title>(.*?)</title>', html, re.S)
    if tm:
        title = tm.group(1)
        ogt = re.search(r'(<meta property="og:title" content=")(.*?)("\s*/?>)', html, re.S)
        if ogt and ogt.group(2) != title:
            html = html[:ogt.start(2)] + title + html[ogt.end(2):]
            changed = True

    mm = re.search(r'<meta name="description" content="(.*?)"\s*/?>', html, re.S)
    if mm:
        desc = mm.group(1)
        ogd = re.search(r'(<meta property="og:description" content=")(.*?)("\s*/?>)', html, re.S)
        if ogd and ogd.group(2) != desc:
            html = html[:ogd.start(2)] + desc + html[ogd.end(2):]
            changed = True
    return html, changed


def find_copies(slug_html_filename):
    slug = slug_html_filename[:-5]
    paths = []
    for p in (
        os.path.join(ROOT, slug_html_filename),
        os.path.join(ROOT, slug, "index.html"),
        os.path.join(ROOT, "colddirect-public-html", slug_html_filename),
    ):
        if os.path.exists(p):
            paths.append(p)
    return paths


def main():
    report_path = os.path.join(ROOT, "agent", "sameday-tag-report.json")
    with open(report_path, encoding="utf-8") as fh:
        report = json.load(fh)

    total_files_changed = 0
    for entry in report:
        for path in find_copies(entry["file"]):
            with open(path, encoding="utf-8", errors="ignore") as fh:
                html = fh.read()
            new_html, changed = sync_og(html)
            if changed:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new_html)
                total_files_changed += 1
    print(f"og tags synced in {total_files_changed} files")


if __name__ == "__main__":
    main()
