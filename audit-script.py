import os
import json
import re
from pathlib import Path
from html.parser import HTMLParser

# Configuration
PROJECT_ROOT = r"C:\Users\khora\Documents\colddirect-website"
SKIP_FILES = {
    "index.html",
    "agent-status.html",
    "coverage.html",
    "sitemap.xml",
}
SKIP_PATTERNS = ["preview-", "_backup_"]

# Priority order
PRIORITY_ORDER = {
    "commercial-fridge": 1,
    "commercial-freezer": 2,
    "freezer-room": 3,
    "cold-room": 4,
}

class BodyExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.body_text = []
        self.in_seo = False
        self.seo_html = []
        
    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        elif tag == "section" and self.in_body:
            attrs_dict = dict(attrs)
            classes = attrs_dict.get("class", "").split()
            if "seo-article" in classes:
                self.in_seo = True
        elif tag == "img" and self.in_seo:
            attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs])
            self.seo_html.append(f"<img {attrs_str} />")
            
    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
        elif tag == "section" and self.in_seo:
            self.in_seo = False
            
    def handle_data(self, data):
        if self.in_body:
            self.body_text.append(data)

def extract_body_text(html):
    parser = BodyExtractor()
    try:
        parser.feed(html)
    except:
        pass
    return " ".join(parser.body_text), parser.seo_html

def count_words(text):
    words = text.strip().split()
    return len([w for w in words if w])

def has_seo_section(html):
    return 'seo-article' in html

def check_image_alt(seo_html, filename):
    if not seo_html:
        return False
    
    # Extract brand keyword from filename
    filename_no_ext = filename.replace(".html", "")
    
    for img_tag in seo_html:
        alt_match = re.search(r'alt="([^"]*)"', img_tag)
        if alt_match:
            alt_text = alt_match.group(1).lower()
            # Check if any key keyword appears in alt text
            keywords = filename_no_ext.lower().split("-")
            for kw in keywords:
                if kw in alt_text and kw not in ["repair", "london", "north"]:
                    return True
    return False

def get_priority(filename):
    for keyword, priority in PRIORITY_ORDER.items():
        if keyword in filename:
            return priority
    return 999

def should_skip(filename):
    if filename in SKIP_FILES:
        return True
    for pattern in SKIP_PATTERNS:
        if pattern in filename:
            return True
    return False

# Scan files
results = []
os.chdir(PROJECT_ROOT)

for filename in sorted(os.listdir(".")):
    if not filename.endswith(".html"):
        continue
    if should_skip(filename):
        continue
    
    filepath = os.path.join(PROJECT_ROOT, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
    except:
        continue
    
    body_text, seo_html = extract_body_text(html)
    word_count = count_words(body_text)
    has_seo = has_seo_section(html)
    image_ok = check_image_alt(seo_html, filename) if has_seo else False
    
    is_weak = word_count < 400 or not has_seo
    status = "WEAK" if is_weak else "OK"
    
    results.append({
        "file": filename,
        "words": word_count,
        "hasSeo": has_seo,
        "imageOk": image_ok,
        "status": status,
        "priority": get_priority(filename)
    })

# Sort by priority
results.sort(key=lambda x: (x["priority"], x["file"]))

# Filter weak pages
weak_pages = [r for r in results if r["status"] == "WEAK"]

# Write weak-list.json
weak_for_json = [{k: v for k, v in page.items() if k != "priority"} for page in weak_pages]
with open("weak-list.json", "w") as f:
    json.dump(weak_for_json, f, indent=2)

# Write AUDIT-REPORT.md
with open("AUDIT-REPORT.md", "w") as f:
    f.write("# Cold Direct SEO Audit Report\n\n")
    f.write(f"**Total Pages Scanned:** {len(results)}\n")
    f.write(f"**Weak Pages Found:** {len(weak_pages)}\n\n")
    f.write("| File | Words | Has SEO | Image OK | Priority |\n")
    f.write("|------|-------|---------|----------|----------|\n")
    
    for page in results:
        priority_map = {1: "Commercial Fridge", 2: "Commercial Freezer", 3: "Freezer Room", 4: "Cold Room", 999: "Other"}
        priority_label = priority_map.get(page["priority"], "Other")
        f.write(f"| {page['file']} | {page['words']} | {'Yes' if page['hasSeo'] else 'No'} | {'Yes' if page['imageOk'] else 'No'} | {priority_label} |\n")

print(f"Scan complete: {len(results)} pages, {len(weak_pages)} weak")
