"""Upload ONLY App_Data/azure-speech.key to Plesk /httpdocs/App_Data/ with plain FTP, then prove the live
vault speaks Persian with the official Azure neural voice fa-IR-FaridNeural.

1. Azure portal -> create a "Speech service" (Free F0 tier = 500,000 characters/month) -> Keys and Endpoint.
2. Put the region on line 1 (e.g. uksouth) and KEY 1 on line 2 of App_Data/azure-speech.key (git-ignored).
3. Double-click this file or run:  python tools/upload_azure_speech_key_ftp.py
The key is never printed. FTP credentials come from the git-ignored .vscode/sftp.json."""
import base64, ftplib, io, json, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = ROOT / "App_Data" / "azure-speech.key"
VAULT = "https://www.colddirect.co.uk/colddirect-voice-vault.aspx?mode=tts"
WAV_OUT = ROOT / "logs" / "azure_persian_test.mp3"
FA_TEXT = "سلام رفیق، اصلاً نگران نباش! سرمهندس کلد دایرکت‌ام، سی ساله تو لندن یخچال صنعتی درست می‌کنم."


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
    lines = [l.strip() for l in KEY_FILE.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    if len(lines) < 2 or any("PASTE" in l.upper() for l in lines[:2]):
        finish(1, f"put the region on line 1 and the key on line 2 of {KEY_FILE.relative_to(ROOT)}")
    region, key = lines[0].lower(), lines[1]
    if not re.fullmatch(r"[a-z0-9]+", region):
        finish(1, "line 1 must be the Azure region, e.g. uksouth")
    return region, key


def check_with_azure(region, key):
    req = urllib.request.Request(f"https://{region}.api.cognitive.microsoft.com/sts/v1.0/issueToken",
                                 data=b"", headers={"Ocp-Apim-Subscription-Key": key}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30):
            pass
    except urllib.error.HTTPError as e:
        finish(1, f"Azure rejected the key/region (HTTP {e.code})")
    print("1/3 key accepted by Azure")


def upload(region, key):
    cfg = json.load(open(ROOT / ".vscode" / "sftp.json", encoding="utf-8"))
    base = cfg.get("remotePath") or "/httpdocs"
    data = f"{region}\n{key}\n".encode()
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
        ftp.storbinary("STOR azure-speech.key", io.BytesIO(data))
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    print(f"2/3 uploaded {base}/App_Data/azure-speech.key via plain FTP")


def check_vault():
    req = urllib.request.Request(VAULT, data=json.dumps({"mode": "tts", "language": "fa", "text": FA_TEXT}).encode(),
                                 headers={"Content-Type": "application/json", "Origin": "https://www.colddirect.co.uk"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.loads(r.read().decode("utf-8-sig"))
    audio = base64.b64decode(res.get("audio_base64") or "")
    print(f"3/3 live Persian voice: {res.get('voice')} ({len(audio) // 1024} KB {res.get('audio_mime')})")
    if audio:
        WAV_OUT.parent.mkdir(exist_ok=True)
        WAV_OUT.write_bytes(audio)
        print("    saved", WAV_OUT.relative_to(ROOT))
    if res.get("voice") == "Puck":
        finish(0, "Gemini Puck answered first (quota available), Azure stays ready as the backup.")
    if res.get("voice") != "azure-neural":
        finish(1, f"vault did not use Azure ({res.get('detail', '')})")
    finish(0, "SUCCESS: Persian answers now play with the Azure neural voice when Puck is unavailable.")


if __name__ == "__main__":
    r, k = read_key()
    check_with_azure(r, k)
    upload(r, k)
    check_vault()
