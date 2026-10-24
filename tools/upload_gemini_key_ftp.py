"""Upload ONLY App_Data/gemini-voice.key to Plesk /httpdocs/App_Data/ with plain FTP, then prove
/colddirect-voice-vault.aspx answers through Gemini with the Puck voice.

1. Paste your Gemini API key (one line) into App_Data/gemini-voice.key  (git-ignored, never deployed).
2. Double-click this file or run:  python tools/upload_gemini_key_ftp.py
The key itself is never printed. FTP credentials come from the git-ignored .vscode/sftp.json."""
import base64, ftplib, io, json, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "App_Data" / "gemini-voice.key"
SITE = "https://www.colddirect.co.uk"
VAULT = SITE + "/colddirect-voice-vault.aspx"
WAV_OUT = ROOT / "logs" / "puck_voice_test.wav"


def fail(msg):
    print("FAILED:", msg)
    finish(1)


def finish(code):
    if "--no-pause" not in sys.argv and sys.stdin and sys.stdin.isatty():
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass
    sys.exit(code)


def read_key():
    if not KEY_FILE.is_file():
        fail(f"{KEY_FILE.relative_to(ROOT)} not found")
    key = KEY_FILE.read_text(encoding="utf-8-sig").strip().strip("'\"").strip()
    if not key or "PASTE" in key.upper():
        fail(f"paste your Gemini API key into {KEY_FILE.relative_to(ROOT)} first")
    if re.search(r"\s", key):
        fail("the key file must contain the key on a single line with no spaces")
    return key


def check_key_with_google(key):
    url = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1&key=" + key
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            ok = r.status == 200
    except urllib.error.HTTPError as e:
        fail(f"Google rejected the key (HTTP {e.code}) - check it in Google AI Studio")
    except Exception as e:
        fail(f"could not reach Google to check the key: {type(e).__name__}")
    print("1/4 key accepted by Google:", "yes" if ok else "no")


def upload(key):
    cfg = json.load(open(ROOT / ".vscode" / "sftp.json", encoding="utf-8"))
    base = cfg.get("remotePath") or "/httpdocs"
    data = (key + "\n").encode("utf-8")
    ftp = ftplib.FTP()
    try:
        ftp.connect(cfg["host"], int(cfg.get("port", 21)), timeout=40)
        ftp.login(cfg["username"], cfg["password"])
        ftp.cwd(base)
        try:
            ftp.cwd("App_Data")
        except ftplib.error_perm:
            ftp.mkd("App_Data")
            ftp.cwd("App_Data")
        ftp.storbinary("STOR gemini-voice.key", io.BytesIO(data))
        try:
            ftp.voidcmd("TYPE I")
            size = ftp.size("gemini-voice.key")
        except Exception:
            size = None
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    if size is not None and size != len(data):
        fail(f"uploaded size {size} != local size {len(data)}")
    print(f"2/4 uploaded {base}/App_Data/gemini-voice.key via plain FTP ({len(data)} bytes)")


def check_not_public(key):
    try:
        with urllib.request.urlopen(SITE + "/App_Data/gemini-voice.key", timeout=30) as r:
            body = r.read(4000).decode("utf-8", "replace")
        if key in body:
            fail("the key file is publicly downloadable - delete it from Plesk now")
        print(f"3/4 key is NOT public: /App_Data/gemini-voice.key does not serve the key (HTTP {r.status})")
    except urllib.error.HTTPError as e:
        print(f"3/4 key is NOT public: /App_Data/gemini-voice.key returns HTTP {e.code}")


def check_vault():
    req = urllib.request.Request(
        VAULT,
        data=json.dumps({"text": "Hi mate, my fridge freezer is making a loud buzzing noise"}).encode(),
        headers={"Content-Type": "application/json", "Origin": SITE, "User-Agent": "ColdDirect-KeyCheck/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=150) as r:
            res = json.loads(r.read().decode("utf-8-sig"))
    except urllib.error.HTTPError as e:
        fail(f"vault returned HTTP {e.code}")
    except Exception as e:
        fail(f"vault call failed: {type(e).__name__}")

    source, voice = res.get("source"), res.get("voice")
    audio = (res.get("audio") or {}).get("data") or ""
    wav = base64.b64decode(audio) if audio else b""
    print("4/4 live vault check")
    print("    answer engine :", source, "(want: gemini)")
    print("    voice         :", voice, "(want: Puck)")
    print("    audio         :", f"{len(wav) // 1024} KB WAV" if wav[:4] == b"RIFF" else "none")
    print("    summary       :", (res.get("summary") or "")[:160])
    if wav:
        WAV_OUT.parent.mkdir(exist_ok=True)
        WAV_OUT.write_bytes(wav)
        print("    saved sample  :", WAV_OUT.relative_to(ROOT), "(play it to hear Puck)")

    if voice == "browser-no-key":
        fail("vault cannot see the key - check the file landed in /httpdocs/App_Data/")
    if voice != "Puck" or wav[:4] != b"RIFF":
        fail("Gemini TTS (Puck) did not return audio - the key may lack access to gemini-2.5-flash-preview-tts")
    if source != "gemini":
        print("NOTE: voice is Puck, but the text came from the built-in engine (Gemini text model busy or quota hit).")
    print("\nSUCCESS: the live homepage voice bar now speaks with Gemini Puck.")


if __name__ == "__main__":
    k = read_key()
    check_key_with_google(k)
    upload(k)
    check_not_public(k)
    check_vault()
    finish(0)
