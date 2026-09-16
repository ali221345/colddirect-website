from pathlib import Path
import re

files = [
    Path(r"C:\Users\khora\Documents\colddirect-website\colddirect-public-html\index.html"),
    Path(r"C:\Users\khora\Documents\colddirect-website\colddirect-public-html\image-preview.html"),
]


def fix(tag: str) -> str:
    if not re.search(r"\bclass=", tag, re.I):
        tag = re.sub(r"<img\b", '<img class="pro-image"', tag, count=1, flags=re.I)
    elif "pro-image" not in tag:
        tag = re.sub(r'\bclass=(["\'])', r"class=\1pro-image ", tag, count=1, flags=re.I)
    if not re.search(r"\bloading=", tag, re.I):
        tag = re.sub(r"<img\b", '<img loading="lazy"', tag, count=1, flags=re.I)
    return tag


for p in files:
    t = p.read_text(encoding="utf-8")
    n = re.sub(r"<img\b[^>]*>", lambda m: fix(m.group(0)), t, flags=re.I)
    p.write_text(n, encoding="utf-8", newline="\n")
    print("updated", p.name)
