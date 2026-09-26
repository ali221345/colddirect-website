import re
import json
from pathlib import Path
from html.parser import HTMLParser

class BodyWordCounter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_body = False
        self.in_script = False
        self.text = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.in_body = True
        elif tag == 'script':
            self.in_script = True
    
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
        elif tag == 'script':
            self.in_script = False
    
    def handle_data(self, data):
        if self.in_body and not self.in_script:
            self.text.append(data)
    
    def get_words(self):
        full_text = ' '.join(self.text)
        words = re.findall(r'\b\w+\b', full_text)
        return len(words)

def audit_file(filepath):
    """Audit a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return None
    
    # Count words in body
    parser = BodyWordCounter()
    parser.feed(content)
    words = parser.get_words()
    
    # Check for seo-article section
    has_seo = bool(re.search(r'<section\s+class=["\']?seo-article', content))
    
    # Check for image in seo-article and alt text matching brand
    image_ok = False
    if has_seo:
        # Extract filename without .html to get brand keyword
        filename = Path(filepath).stem
        # Extract brand keyword (first part before hyphen typically)
        brand_match = re.search(r'^([a-z]+)-', filename)
        brand = brand_match.group(1) if brand_match else filename
        
        # Look for img tag within seo-article
        seo_section = re.search(r'<section\s+class=["\']?seo-article[^>]*>(.*?)</section>', content, re.DOTALL)
        if seo_section:
            img_match = re.search(r'<img[^>]+alt=["\']?([^"\'>\s]+)', seo_section.group(1))
            if img_match:
                alt_text = img_match.group(1).lower()
                # Check if brand keyword appears in alt text
                image_ok = brand.lower() in alt_text
    
    return {
        "words": words,
        "hasSeo": has_seo,
        "imageOk": image_ok
    }

# Files to skip
skip_files = {
    'index.html', 'agent-status.html', 'coverage.html', 'sitemap.xml'
}
skip_prefixes = {'preview-', '_backup_'}

# Audit all files
project_dir = Path('C:/Users/khora/Documents/colddirect-website')
results = {}

for html_file in sorted(project_dir.glob('*.html')):
    filename = html_file.name
    
    # Skip non-content files
    if filename in skip_files:
        continue
    if any(filename.startswith(p) for p in skip_prefixes):
        continue
    
    result = audit_file(str(html_file))
    if result:
        results[filename] = result

# Determine weak pages (words < 400 OR no seo-article)
weak_list = []
for filename, data in results.items():
    is_weak = data['words'] < 400 or not data['hasSeo']
    if is_weak:
        weak_list.append({
            'file': filename,
            'words': data['words'],
            'hasSeo': data['hasSeo'],
            'imageOk': data['imageOk'],
            'status': 'WEAK'
        })

# Define priority order
def get_priority(filename):
    if 'commercial-fridge-repair' in filename:
        return (1, filename)
    elif 'commercial-freezer-repair' in filename:
        return (2, filename)
    elif 'freezer-room-repair' in filename:
        return (3, filename)
    elif 'cold-room-repair' in filename:
        return (4, filename)
    else:
        return (5, filename)

weak_list.sort(key=lambda x: get_priority(x['file']))

# Write weak-list.json
output_dir = project_dir
with open(output_dir / 'weak-list.json', 'w') as f:
    json.dump(weak_list, f, indent=2)

# Create audit report
report_lines = [
    "# Cold Direct SEO Audit Report",
    "",
    f"Total pages audited: {len(results)}",
    f"Weak pages found: {len(weak_list)}",
    "",
    "| File | Words | Has SEO | Image OK | Priority |",
    "|------|-------|---------|----------|----------|"
]

priority_map = {1: 'P1 (Commercial Fridge)', 2: 'P2 (Commercial Freezer)', 
                3: 'P3 (Freezer Room)', 4: 'P4 (Cold Room)', 5: 'P5 (Other)'}

for item in weak_list:
    filename = item['file']
    priority_num, _ = get_priority(filename)
    priority_label = priority_map[priority_num]
    seo_status = '✓' if item['hasSeo'] else '✗'
    img_status = '✓' if item['imageOk'] else '✗'
    report_lines.append(
        f"| `{filename}` | {item['words']} | {seo_status} | {img_status} | {priority_label} |"
    )

report_content = '\n'.join(report_lines)

with open(output_dir / 'AUDIT-REPORT.md', 'w') as f:
    f.write(report_content)

print(f"Audit complete. Weak pages: {len(weak_list)}")
print(f"weak-list.json written to {output_dir / 'weak-list.json'}")
print(f"AUDIT-REPORT.md written to {output_dir / 'AUDIT-REPORT.md'}")
