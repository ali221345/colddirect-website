from pathlib import Path
from PIL import Image

src_dir = Path(r"C:\Users\khora\.cursor\projects\c-Users-khora-Documents-colddirect-website\assets")
dests = [
    Path(r"C:\Users\khora\Documents\colddirect-website\images\pro"),
    Path(r"C:\Users\khora\Documents\colddirect-website\colddirect-public-html\images\pro"),
]
names = [
    "commercial-fridge-installation-london.webp",
    "commercial-freezer-repair-london.webp",
    "walk-in-cold-room-maintenance.webp",
    "commercial-fridge-maintenance-london.webp",
    "emergency-fridge-repair-london.webp",
    "commercial-fridge-cleaning-service.webp",
    "commercial-refrigeration-service-london.webp",
    "walk-in-freezer-installation.webp",
    "display-fridge-repair-london.webp",
    "commercial-kitchen-cold-room.webp",
]
MAX_BYTES = 300 * 1024
MAX_W = 1600

for d in dests:
    d.mkdir(parents=True, exist_ok=True)

for name in names:
    src = src_dir / name
    if not src.exists():
        raise SystemExit(f"missing {src}")
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w > MAX_W:
        im = im.resize((MAX_W, int(h * MAX_W / w)), Image.Resampling.LANCZOS)
    quality = 82
    data = None
    while quality >= 55:
        tmp = dests[0] / name
        im.save(tmp, "WEBP", quality=quality, method=6)
        size = tmp.stat().st_size
        if size <= MAX_BYTES:
            data = tmp.read_bytes()
            break
        quality -= 4
    if data is None:
        tmp = dests[0] / name
        data = tmp.read_bytes()
    for d in dests:
        (d / name).write_bytes(data)
    size = len(data)
    print(f"{name:48} {im.size[0]}x{im.size[1]}  {size/1024:.1f} KB  q~{quality}  {'OK' if size <= MAX_BYTES else 'OVER'}")
