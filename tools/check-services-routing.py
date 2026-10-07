"""Verify the live Services route and aliases without submitting any forms."""
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ORIGIN = "https://www.colddirect.co.uk"
CANONICAL = ORIGIN + "/services/"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirect)
cases = {
    "/services/": (200, None),
    "/services/?routingcheck=20261007": (200, None),
    "/services": (301, CANONICAL),
    "/services.html": (301, CANONICAL),
    "/services/index.html": (200, None),
    "/": (200, None),
    "/fridge-repair-london/": (200, None),
    "/freezer-repair-london/": (200, None),
    "/commercial-fridge-repair-london/": (200, None),
    "/cold-room-repair-london/": (200, None),
}
results = []
for path, (status, location) in cases.items():
    try:
        response = opener.open(ORIGIN + path, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        actual_status = response.code
        actual_location = response.headers.get("Location")
        body = response.read().decode("utf-8", errors="replace")
    assert (actual_status, actual_location) == (status, location), (
        path, actual_status, actual_location
    )
    if path.startswith("/services") and status == 200:
        assert re.search(r'<h1\b[^>]*>\s*Services\s*</h1>', body, re.I)
        assert CANONICAL in re.search(
            r'<link\b[^>]*rel=[\"\']canonical[\"\'][^>]*>', body, re.I
        ).group(0)
        assert not re.search(r'noindex|nofollow', body, re.I)
        for schema in re.findall(
            r'<script\b[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>',
            body, re.I | re.S
        ):
            json.loads(schema)
    results.append({"path": path, "status": actual_status, "location": actual_location})

report = {"checked_at": datetime.now(timezone.utc).isoformat(), "results": results,
          "services_content": "H1, canonical, indexing directives and JSON-LD checked"}
destination = Path("reports/services-routing-2026-10-07.json")
destination.parent.mkdir(exist_ok=True)
destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"PASS: {len(results)} live routes; Services content and schema verified")
