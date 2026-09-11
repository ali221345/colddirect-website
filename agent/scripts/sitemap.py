import os
from datetime import datetime
def generate_sitemap(site_folder):
    base_url = "https://www.colddirect.co.uk"
    pages = []
    for root, dirs, files in os.walk(site_folder):
        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file).replace(site_folder, "").replace("\\", "/")
                pages.append(f"{base_url}{path}")
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        sitemap_content += f"  <url><loc>{page}</loc><lastmod>{datetime.now().date()}</lastmod></url>\n"
    sitemap_content += '</urlset>'
    with open(f"{site_folder}/sitemap.xml", "w") as f:
        f.write(sitemap_content)
