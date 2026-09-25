"""
Adds "Same-Day"/"same-day" phrasing naturally into title, meta description,
and H1/lead of Cold Direct service pages that don't already mention it.
Applies identically across all copies of each page: root .html, slug/index.html,
and colddirect-public-html/slug.html.

Never removes or deletes existing content -- only inserts a word.
"""
import re
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

EXCLUDE = {
    "about.html", "about-us.html", "agent-status.html", "contact.html",
    "coverage.html", "faqs.html", "news.html", "services.html",
    "write-a-review.html", "_backup_index_old.html",
    "preview-colddirect-homepage.html", "gsc-analysis-2026-09-19.html",
    "commercial-dishwasher-repair-london.html",
}

REPAIR_RE = re.compile(r'\b(Repairs?)\b', re.IGNORECASE)


def has_sameday(text):
    t = text.lower()
    return "same-day" in t or "same day" in t


def insert_sameday_before_repair(text):
    """Insert Same-Day/same-day immediately before the first standalone
    Repair/Repairs word. Returns (new_text, changed_bool)."""
    m = REPAIR_RE.search(text)
    if not m:
        return text, False
    word = m.group(1)
    prefix = "Same-Day " if word[0].isupper() else "same-day "
    new_text = text[:m.start()] + prefix + text[m.start():]
    return new_text, True


def process_title(html):
    m = re.search(r'(<title>)(.*?)(</title>)', html, re.S)
    if not m:
        return html, False
    title = m.group(2)
    if has_sameday(title):
        return html, False
    new_title, changed = insert_sameday_before_repair(title)
    if not changed:
        return html, False
    new_html = html[:m.start(2)] + new_title + html[m.end(2):]
    return new_html, True


def process_meta(html):
    m = re.search(r'(<meta name="description" content=")(.*?)("\s*/?>)', html, re.S)
    if not m:
        return html, False
    desc = m.group(2)
    if has_sameday(desc):
        return html, False
    new_desc, changed = insert_sameday_before_repair(desc)
    if not changed:
        return html, False
    new_html = html[:m.start(2)] + new_desc + html[m.end(2):]
    return new_html, True


def process_h1_or_lead(html):
    # Try H1 first
    m = re.search(r'(<h1[^>]*>)(.*?)(</h1>)', html, re.S)
    if m and not has_sameday(m.group(2)):
        new_text, changed = insert_sameday_before_repair(m.group(2))
        if changed:
            new_html = html[:m.start(2)] + new_text + html[m.end(2):]
            return new_html, True, "h1"
    # Fall back to <p class="lead">
    m = re.search(r'(<p class="lead">)(.*?)(</p>)', html, re.S)
    if m and not has_sameday(m.group(2)):
        new_text, changed = insert_sameday_before_repair(m.group(2))
        if changed:
            new_html = html[:m.start(2)] + new_text + html[m.end(2):]
            return new_html, True, "lead"
    return html, False, None


def find_copies(slug_html_filename):
    """Return list of existing file paths for this page: root, folder/index, public_html."""
    slug = slug_html_filename[:-5]
    paths = []
    root_path = os.path.join(ROOT, slug_html_filename)
    if os.path.exists(root_path):
        paths.append(root_path)
    folder_path = os.path.join(ROOT, slug, "index.html")
    if os.path.exists(folder_path):
        paths.append(folder_path)
    pub_path = os.path.join(ROOT, "colddirect-public-html", slug_html_filename)
    if os.path.exists(pub_path):
        paths.append(pub_path)
    return paths


def main():
    dry_run = "--apply" not in sys.argv
    root_htmls = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
    report = []

    for fname in root_htmls:
        if fname in EXCLUDE:
            continue
        root_path = os.path.join(ROOT, fname)
        with open(root_path, encoding="utf-8", errors="ignore") as fh:
            orig = fh.read()

        html = orig
        changes = []

        html, t_changed = process_title(html)
        if t_changed:
            changes.append("title")

        html, m_changed = process_meta(html)
        if m_changed:
            changes.append("meta")

        html, h_changed, where = process_h1_or_lead(html)
        if h_changed:
            changes.append(where)

        if not changes:
            continue

        # Extract before/after snippets for report
        new_title = re.search(r'<title>(.*?)</title>', html, re.S)
        old_title = re.search(r'<title>(.*?)</title>', orig, re.S)
        new_meta = re.search(r'<meta name="description" content="(.*?)"\s*/?>', html, re.S)
        old_meta = re.search(r'<meta name="description" content="(.*?)"\s*/?>', orig, re.S)

        report.append({
            "file": fname,
            "changes": changes,
            "title_before": old_title.group(1) if old_title else None,
            "title_after": new_title.group(1) if new_title else None,
            "meta_before": old_meta.group(1) if old_meta else None,
            "meta_after": new_meta.group(1) if new_meta else None,
        })

        if not dry_run:
            copies = find_copies(fname)
            for path in copies:
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    copy_html = fh.read()
                copy_html, _ = process_title(copy_html)
                copy_html, _ = process_meta(copy_html)
                copy_html, _, _ = process_h1_or_lead(copy_html)
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(copy_html)

    mode = "APPLIED" if not dry_run else "DRY RUN"
    print(f"=== {mode}: {len(report)} pages changed ===")
    for r in report:
        print(f"\n--- {r['file']} ({', '.join(r['changes'])}) ---")
        if "title" in r["changes"]:
            print(f"  TITLE before: {r['title_before']}")
            print(f"  TITLE after:  {r['title_after']}")
        if "meta" in r["changes"]:
            print(f"  META before: {r['meta_before']}")
            print(f"  META after:  {r['meta_after']}")

    with open(os.path.join(ROOT, "agent", "sameday-tag-report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)


if __name__ == "__main__":
    main()
