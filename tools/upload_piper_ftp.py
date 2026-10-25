"""Install the free on-server male voice engine (Piper) for /colddirect-voice-vault.aspx.

Downloads the official Piper Windows build and male voices into the git-ignored App_Data/piper/,
uploads that folder to Plesk /httpdocs/App_Data/piper/ over plain FTP (skipping files that are
already there with the same size), then checks the live vault speaks Persian with Ganji.

Usage: python tools/upload_piper_ftp.py [--no-upload] [--no-verify]
"""
import base64, ftplib, io, json, sys, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "App_Data" / "piper"
PIPER_ZIP = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
VOICES = [
    "fa/fa_IR/ganji/medium/fa_IR-ganji-medium",
    "en/en_GB/alan/medium/en_GB-alan-medium",
    "tr/tr_TR/dfki/medium/tr_TR-dfki-medium",
    "ar/ar_JO/kareem/medium/ar_JO-kareem-medium",
]
VAULT = "https://www.colddirect.co.uk/colddirect-voice-vault.aspx?mode=tts"
FA_TEXT = "سلام و درود، سرمهندس شرکت ColdDirect در لندن هستم، با سی سال تجربه‌ی تخصصی در تعمیرات تجهیزات برودتی."


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "colddirect-setup"}), timeout=300) as r:
        return r.read()


def install():
    if not (DEST / "piper.exe").is_file():
        print("downloading Piper for Windows ...", flush=True)
        with zipfile.ZipFile(io.BytesIO(fetch(PIPER_ZIP))) as z:
            for info in z.infolist():
                name = info.filename.split("/", 1)[1] if info.filename.startswith("piper/") else info.filename
                if not name or info.is_dir():
                    continue
                out = DEST / name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(z.read(info))
    (DEST / "voices").mkdir(parents=True, exist_ok=True)
    for v in VOICES:
        name = v.rsplit("/", 1)[1]
        for ext in (".onnx", ".onnx.json"):
            out = DEST / "voices" / (name + ext)
            if not out.is_file() or out.stat().st_size == 0:
                print("downloading", name + ext, flush=True)
                out.write_bytes(fetch(f"{HF}/{v}{ext}"))


def upload():
    cfg = json.load(open(ROOT / ".vscode" / "sftp.json", encoding="utf-8"))
    base = (cfg.get("remotePath") or "/httpdocs").rstrip("/") + "/App_Data/piper"
    ftp = ftplib.FTP()
    ftp.connect(cfg["host"], int(cfg.get("port", 21)), timeout=180)
    ftp.login(cfg["username"], cfg["password"])
    ftp.voidcmd("TYPE I")
    made = set()

    def ensure(remote_dir):
        if remote_dir in made:
            return
        parts, cur = remote_dir.strip("/").split("/"), ""
        for part in parts:
            cur += "/" + part
            if cur in made:
                continue
            try:
                ftp.cwd(cur)
            except ftplib.error_perm:
                ftp.mkd(cur)
            made.add(cur)

    sent = skipped = 0
    try:
        for f in sorted(p for p in DEST.rglob("*") if p.is_file()):
            rel = f.relative_to(DEST).as_posix()
            remote = base + "/" + rel
            ensure(remote.rsplit("/", 1)[0])
            try:
                if ftp.size(remote) == f.stat().st_size:
                    skipped += 1
                    continue
            except ftplib.error_perm:
                pass
            with f.open("rb") as fh:
                ftp.storbinary("STOR " + remote, fh, blocksize=262144)
            sent += 1
            if f.stat().st_size > 1_000_000:
                print(f"uploaded {rel} ({f.stat().st_size // 1_000_000} MB)", flush=True)
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()
    print(f"FTP done: {sent} uploaded, {skipped} already up to date")


def verify():
    body = json.dumps({"mode": "tts", "language": "fa", "text": FA_TEXT}).encode()
    req = urllib.request.Request(VAULT, data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Origin": "https://www.colddirect.co.uk"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.loads(r.read().decode("utf-8-sig"))
    audio = base64.b64decode(d.get("audio_base64") or "")
    print(f"live fa: ok={d.get('ok')} voice={d.get('voice')} mime={d.get('audio_mime')} bytes={len(audio)} {d.get('detail', '')}")
    return d.get("ok") is True and len(audio) > 20000 and d.get("voice") in ("Puck", "piper-fa_IR-ganji-medium")


if __name__ == "__main__":
    install()
    if "--no-upload" not in sys.argv:
        upload()
    if "--no-verify" not in sys.argv:
        sys.exit(0 if verify() else 1)
