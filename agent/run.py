import os
from scripts.sitemap import generate_sitemap
from scripts.robots import check_robots
from scripts.seo_score import score_page
print("SEO Agent started")
generate_sitemap("../colddirect-public-html")
check_robots("../colddirect-public-html")
print("Agent finished")
