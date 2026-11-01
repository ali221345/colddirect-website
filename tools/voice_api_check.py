#!/usr/bin/env python3
"""Production voice API regression check; browser playback still needs a browser audit."""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = os.environ.get("VOICE_API_URL", "https://colddirect-website.vercel.app/api/voice-diagnose")
SILENT_WAV = base64.b64encode(b"RIFF" + (32036).to_bytes(4, "little") + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data" + (32000).to_bytes(4, "little") + b"\x00" * 32000).decode()


def request(payload, opener=urllib.request.urlopen):
    for attempt in range(2):
        req = urllib.request.Request(API, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (compatible; ColdDirect-Voice-Regression/1.0)", "Origin": "https://www.colddirect.co.uk", "Referer": "https://www.colddirect.co.uk/"}, method="POST")
        try:
            with opener(req, timeout=90) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 502, 503) or attempt == 1:
                raise
            time.sleep(3)


def check(opener=urllib.request.urlopen):
    status, body = request({"audio_base64": SILENT_WAV, "mime": "audio/wav"}, opener)
    problems = []
    audio_ok = body.get("ok") and len(body.get("display_text", "")) >= 40
    audio_fallback = body.get("code") == "VOICE_NOT_UNDERSTOOD"
    if status != 200 or not (audio_ok or audio_fallback):
        problems.append("microphone input must return HTTP 200 with a diagnosis or structured fallback, not 502")
    status, text = request({"text": "My commercial fridge is warm and the evaporator fan is not running."}, opener)
    if status != 200 or not text.get("ok") or len(text.get("display_text", "")) < 40:
        problems.append("typed diagnosis did not return a useful HTTP 200 answer")
    if problems:
        raise RuntimeError("; ".join(problems))
    return {"audioFallback": "HTTP 200 structured fallback", "typedDiagnosis": "HTTP 200 useful answer"}


def selftest():
    class Response:
        def __init__(self, body): self.status, self.body = 200, body
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return json.dumps(self.body).encode()
    calls = []
    def opener(req, timeout):
        payload = json.loads(req.data)
        calls.append(payload)
        return Response({"code": "VOICE_NOT_UNDERSTOOD"} if "audio_base64" in payload else {"ok": True, "display_text": "A sufficiently detailed typed diagnosis answer."})
    result = check(opener)
    assert len(calls) == 2 and result["typedDiagnosis"].startswith("HTTP 200")
    def bad(req, timeout): return Response({"code": "VOICE_NOT_UNDERSTOOD"})
    try: check(bad)
    except RuntimeError as exc: assert "typed diagnosis" in str(exc)
    else: raise AssertionError("typed failure was not detected")
    print("voice_api_check selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        try:
            print(json.dumps(check(), ensure_ascii=False))
        except Exception as exc:
            print("Voice API check failed: " + str(exc)[:300])
            sys.exit(1)
