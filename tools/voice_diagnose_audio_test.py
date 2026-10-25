"""POST diagnose to the live vault and require audio_base64 in the JSON."""
import json, sys, urllib.request

URL = "https://www.colddirect.co.uk/colddirect-voice-vault.aspx"
MARK = "CD-UK-IP-2026-994821-VOICE-AI"
CASES = [
    ("fa", "یخچال تجاری خنک نمی‌کند و کد E1 دارد"),
    ("en", "Foster fridge E1 not cooling"),
    ("tl", "Hindi lumalamig ang commercial fridge namin"),
]


def post(lang, text):
    body = json.dumps({
        "mode": "diagnose",
        "text": text,
        "language": lang,
        "langHint": lang,
        "watermark": MARK,
    }).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-CD-IP": MARK,
            "Accept": "application/json",
            "Origin": "https://www.colddirect.co.uk",
            "Referer": "https://www.colddirect.co.uk/",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=40) as res:
        return json.loads(res.read().decode("utf-8", "replace"))


def main():
    failed = 0
    for lang, text in CASES:
        try:
            data = post(lang, text)
        except Exception as e:
            print("FAIL", lang, "request", e)
            failed += 1
            continue
        b64 = data.get("audio_base64") or ((data.get("audio") or {}).get("data") if isinstance(data.get("audio"), dict) else "")
        n = len(b64 or "")
        spoken = data.get("spoken") or ""
        print("LANG", lang, "audio_bytes", n, "spoken_prefix", spoken[:80].replace("\n", " "))
        if n < 80:
            print("FAIL", lang, "missing audio_base64")
            failed += 1
        if lang == "fa" and "سرمهندس" not in spoken and "کُلد" not in spoken:
            print("WARN", lang, "greeting not obvious in spoken")
    if failed:
        sys.exit(1)
    print("OK diagnose audio for", len(CASES), "languages")


if __name__ == "__main__":
    main()
