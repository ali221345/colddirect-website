"""Upload ONLY App_Data/openai-voice.key to Plesk /httpdocs/App_Data/ with plain FTP.

Optional: when this key is present the vault uses OpenAI gpt-4o-mini-tts (onyx, male)
for every language including Persian and Tagalog.

1. Paste your OpenAI API key on one line into App_Data/openai-voice.key (git-ignored).
2. Run:  python tools/upload_openai_key_ftp.py
The key is never printed. FTP credentials come from the git-ignored .vscode/sftp.json."""
import base64, ftplib, io, json, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "App_Data" / "openai-voice.key"
VAULT = "https://www.colddirect.co.uk/colddirect-voice-vault.aspx?mode=tts"
TL_TEXT = "Kamusta kaibigan! Head Engineer ako dito sa ColdDirect sa London."


def finish(code, msg=None):
    if msg:
        print(("FAILED: " if code else "") + msg)
    if "--no-pause" not in sys.argv and sys.stdin and sys.stdin.isatty():
        try:
            input("\nPress Enter to close...")
        except EOFError:
            pass
    sys.exit(code)


def read_key():
    if not KEY_FILE.is_file():
        finish(1, f"{KEY_FILE.relative_to(ROOT)} not found")
    key = KEY_FILE.read_text(encoding="utf-8-sig").strip().strip("'\"").strip()
    if not key or "PASTE" in key.upper():
        finish(1, f"paste your OpenAI API key into {KEY_FILE.relative_to(ROOT)} first")
    if re.search(r"\s", key):
        finish(1, "the key file must contain the key on a single line with no spaces")
    return key


def check_openai(key):
    req = urllib.request.Request(
        "https://api.openai.com/v1/models",
        headers={"Authorization": "Bearer " + key},
    )
    try:
        with urllib.request.urlopen(req, timeout=30):
            pass
    except urllib.error.HTTPError as e:
        finish(1, f"OpenAI rejected the key (HTTP {e.code})")
    print("1/3 key accepted by OpenAI")


def upload(key):
    cfg = json.load(open(ROOT / ".vscode" / "sftp.json", encoding="utf-8"))
    base = cfg.get("remotePath") or "/httpdocs"
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
        ftp.storbinary("STOR openai-voice.key", io.BytesIO((key + "\n").encode()))
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    print("2/3 uploaded /httpdocs/App_Data/openai-voice.key via plain FTP")


def check_vault():
    req = urllib.request.Request(
        VAULT,
        data=json.dumps({"mode": "tts", "language": "tl", "text": TL_TEXT}).encode(),
        headers={"Content-Type": "application/json", "Origin": "https://www.colddirect.co.uk"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode("utf-8-sig"))
    audio = base64.b64decode(d.get("audio_base64") or "")
    print(f"3/3 live tl: ok={d.get('ok')} voice={d.get('voice')} bytes={len(audio)}")
    if d.get("voice") != "openai-onyx" or len(audio) < 20000:
        finish(1, "vault did not switch to OpenAI onyx")


if __name__ == "__main__":
    key = read_key()
    check_openai(key)
    if "--no-upload" not in sys.argv:
        upload(key)
    if "--no-verify" not in sys.argv:
        check_vault()
    finish(0, "OK")
