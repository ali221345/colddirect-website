#!/usr/bin/env python3
"""Verify real spoken-audio transcription and TTS against production Vercel APIs.

Fixtures are supplied by the caller and are never committed. No credentials are used.
"""
import argparse
import base64
import json
import urllib.request

API = "https://colddirect-website.vercel.app"


def post(path, payload, timeout=90):
    request = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Origin": "https://www.colddirect.co.uk",
            "Referer": "https://www.colddirect.co.uk/",
            "User-Agent": "ColdDirect-Spoken-Format-Regression/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def check(path, mime):
    audio = base64.b64encode(path.read_bytes()).decode("ascii")
    status, body = post("/api/voice-diagnose", {"audio_base64": audio, "mime": mime, "mode": "transcribe"})
    transcript = body.get("transcript", "")
    diagnosis = body.get("display_text", "")
    spoken = body.get("spoken_text", "")
    result = {
        "file": path.name,
        "mime": mime,
        "bytes": path.stat().st_size,
        "http": status,
        "ok": body.get("ok") is True,
        "code": body.get("code", ""),
        "diagnostic": body.get("diagnostic", {}),
        "transcript": transcript,
        "diagnosis_chars": len(diagnosis),
        "spoken_chars": len(spoken),
    }
    if status != 200 or not body.get("ok") or len(transcript) < 10 or len(diagnosis) < 40 or len(spoken) < 40:
        return result, False
    tts_status, tts = post("/api/voice-tts", {"text": spoken, "language": body.get("language", "en-GB")})
    result["tts_http"] = tts_status
    result["tts_audio_bytes"] = len(base64.b64decode(tts.get("audio_base64", "")))
    result["tts_mime"] = tts.get("audio_mime", "")
    return result, tts_status == 200 and result["tts_audio_bytes"] > 1000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mp4", type=str)
    parser.add_argument("--webm", type=str)
    args = parser.parse_args()
    from pathlib import Path
    cases = [(Path(args.mp4), "audio/mp4"), (Path(args.webm), "audio/webm")]
    failed = False
    for path, mime in cases:
        result, ok = check(path, mime)
        print(json.dumps(result, ensure_ascii=False))
        failed = failed or not ok
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
