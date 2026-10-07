"""Check utility exclusions and public crawl access in both deployment trees."""
from pathlib import Path
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parents[1]
BOTS = ("Googlebot", "Bingbot", "ChatGPT-User", "GPTBot", "ClaudeBot",
        "PerplexityBot", "Google-Extended", "UnknownBot")
BLOCKED = ("/agent-status.html", "/agent-status/", "/agent-status/index.html",
           "/image-preview.html", "/agent-status-full-report.txt")
PUBLIC = ("/", "/commercial-fridge-repair-london/", "/cold-room-repairs-london/",
          "/contact/", "/assets/css/style.css", "/images/logo.webp", "/sitemap.xml")


def check():
    copies = [ROOT / "robots.txt", ROOT / "colddirect-public-html/robots.txt"]
    assert copies[0].read_bytes() == copies[1].read_bytes(), "robots mirrors differ"
    checks = 0
    for path in copies:
        parser = RobotFileParser()
        parser.parse(path.read_text().splitlines())
        assert parser.site_maps() == ["https://www.colddirect.co.uk/sitemap.xml"]
        for bot in BOTS:
            for url in BLOCKED:
                assert not parser.can_fetch(bot, url), f"{path}: {bot} can crawl {url}"
                checks += 1
            for url in PUBLIC:
                assert parser.can_fetch(bot, url), f"{path}: {bot} blocked from {url}"
                checks += 1
    print(f"Robots policy OK: {checks} crawl checks across both copies")


if __name__ == "__main__":
    check()
