import os
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(AGENT_DIR))

from scripts.sitemap import generate_sitemap
from scripts.robots import check_robots
from scripts.seo_score import score_page

SITE = AGENT_DIR.parent


def score_all_html(site_folder):
    scores = []
    for root, dirs, files in os.walk(site_folder):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules")]
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, site_folder).replace("\\", "/")
            try:
                score = score_page(path)
            except Exception as exc:
                print(f"SCORE_ERROR {rel}: {exc}")
                continue
            scores.append((rel, score))
            print(f"SCORE {score:3d}  {rel}")
    return scores


print("SEO Agent started")
site = str(SITE)
generate_sitemap(site)
check_robots(site)
score_all_html(site)
print("Agent finished")
