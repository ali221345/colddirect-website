"""Read-only smoke checks for critical served pages after deployment."""
import concurrent.futures
import json
from html.parser import HTMLParser
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.colddirect.co.uk"
SLUGS = ("services", "fridge-repair-london", "freezer-repair-london",
         "commercial-fridge-repair-london")


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.canonicals = []
        self.headings = []
        self.phones = set()
        self.in_h1 = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))
        if tag == "a" and attrs.get("href", "").startswith("tel:"):
            self.phones.add(attrs["href"])
        if tag == "h1":
            self.in_h1 = True
            self.headings.append("")

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_h1:
            self.headings[-1] += data


def verify(slug):
    expected = Page((ROOT / slug / "index.html").read_text(encoding="utf-8", errors="replace"))
    url = f"{ORIGIN}/{slug}/"
    failure = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "ColdDirect-release-check/1.0"})
            with urllib.request.urlopen(request, timeout=25) as response:
                if response.status != 200 or response.url != url:
                    raise ValueError("unexpected HTTP status or redirect")
                body = response.read(2_000_000).decode("utf-8")
            actual = Page(body)
            if len(actual.headings) != 1 or actual.headings != expected.headings:
                raise ValueError("page identity/H1 mismatch")
            if actual.canonicals != expected.canonicals or actual.canonicals != [url]:
                raise ValueError("canonical mismatch")
            required_phones = expected.phones | {"tel:+447983759320", "tel:08001123427", "tel:+442039524822"}
            if not required_phones <= actual.phones:
                raise ValueError("missing source telephone links")
            guards = json.loads((ROOT / "protected-pages.json").read_text(encoding="utf-8"))["pages"]
            for guard in guards:
                if guard["url"] == url and guard.get("must_contain") not in body:
                    raise ValueError("protected content missing")
            return f"PASS {url}"
        except Exception as exc:
            failure = exc
            if attempt < 2:
                time.sleep(3)
    raise RuntimeError(f"FAIL {url}: {failure}")


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(verify, SLUGS):
            print(result)
