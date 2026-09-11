def check_robots(site_folder):
    robots_path = f"{site_folder}/robots.txt"
    try:
        with open(robots_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        with open(robots_path, "w") as f:
            f.write("User-agent: *\nAllow: /\nSitemap: https://www.colddirect.co.uk/sitemap.xml\n")
