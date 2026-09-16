from pathlib import Path
import re

p = Path("colddirect-public-html/sitemap.xml")
text = p.read_text(encoding="utf-8")
remove = {
    "https://www.colddirect.co.uk/about.html",
    "https://www.colddirect.co.uk/news.html",
    "https://www.colddirect.co.uk/index.html",
    "https://www.colddirect.co.uk/image-preview.html",
    "https://www.colddirect.co.uk/agent-status.html",
}
pat = re.compile(r"  <url><loc>(.*?)</loc><lastmod>.*?</lastmod></url>\n")
kept = []
removed = []
for m in pat.finditer(text):
    loc = m.group(1)
    if loc in remove:
        removed.append(loc)
    else:
        kept.append(m.group(0))
if not any("https://www.colddirect.co.uk/</loc>" in k for k in kept):
    kept.insert(0, "  <url><loc>https://www.colddirect.co.uk/</loc><lastmod>2026-09-16</lastmod></url>\n")
out = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(kept)
    + "</urlset>\n"
)
p.write_text(out, encoding="utf-8")
root = Path("sitemap.xml")
if root.exists():
    root.write_text(out, encoding="utf-8")
robots_root = Path("robots.txt")
robots_pub = Path("colddirect-public-html/robots.txt")
if robots_root.exists() and robots_pub.exists():
    robots_root.write_text(robots_pub.read_text(encoding="utf-8"), encoding="utf-8")
print("removed", removed)
print("kept", len(kept))
