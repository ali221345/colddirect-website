#!/usr/bin/env python3
"""Outcome-driven bilingual 48-hour report and mobile delivery. No invented health claims."""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPIC = "colddirect-seo-khora-8492"
LABELS = {
    "backup": ("Backup", "پشتیبان‌گیری"),
    "health": ("Live health", "سلامت سایت"),
    "redirects": ("Redirects and config", "ریدایرکت‌ها و پیکربندی"),
    "schema": ("Schema and SEO integrity", "اسکیما و یکپارچگی سئو"),
    "voice": ("Voice API", "سرویس صوتی"),
    "gsc": ("Search Console", "سرچ کنسول"),
}
ORDER = tuple(LABELS)


def overall(job_status, outcomes):
    return "success" if job_status == "success" and all(outcomes.get(key) == "success" for key in ORDER) else "failure"


def message(status, outcomes, now=None):
    now = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"ColdDirect 48h | {now}", "English: " + ("All requested checks passed." if status == "success" else "Attention required; inspect failed checks below.")]
    for key in ORDER:
        value = outcomes.get(key, "not run")
        lines.append(f"{LABELS[key][0]}: {value}")
    lines.append("فارسی: " + ("همه بررسی‌های درخواستی موفق بودند." if status == "success" else "نیاز به بررسی دارد؛ موارد ناموفق در زیر آمده‌اند."))
    for key in ORDER:
        value = outcomes.get(key, "اجرا نشد")
        lines.append(f"{LABELS[key][1]}: {value}")
    lines.append("Rankings are measured, never guaranteed. | رتبه‌ها اندازه‌گیری می‌شوند و تضمین نیستند.")
    return "\n".join(lines)


def deliver(text, topic=None):
    topic = topic or os.environ.get("NTFY_TOPIC", DEFAULT_TOPIC)
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=text.encode(), headers={"Title": "ColdDirect 48h FA/EN", "Tags": "chart_with_upwards_trend"}, method="POST")
    with urllib.request.urlopen(req, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"ntfy HTTP {response.status}")
        return response.status


def selftest():
    text = message("failure", {"backup": "success", "voice": "failure"}, "2026-10-26 00:00 UTC")
    assert "Attention required" in text and "نیاز به بررسی" in text and "Voice API: failure" in text
    assert "All requested checks passed" not in text and "همه بررسی‌های درخواستی موفق" not in text
    good = {key: "success" for key in ORDER}
    assert overall("success", good) == "success"
    assert overall("success", dict(good, voice="failure")) == "failure"
    assert overall("failure", good) == "failure"
    print("report_48h selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        raise SystemExit(0)
    if "--send-test" in sys.argv:
        status = deliver(message("success", {key: "test delivery" for key in ORDER}))
        print(f"Bilingual ntfy test accepted: HTTP {status}")
        raise SystemExit(0)
    outcomes = {key: os.environ.get("S_" + key.upper(), "not run") for key in ORDER}
    # job.status ignores continue-on-error step failures; derive the headline from every real outcome.
    status = overall(os.environ.get("JOB_STATUS"), outcomes)
    text = message(status, outcomes)
    out = ROOT / "backup-out" / "48h-report-fa-en.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write("## 48-hour bilingual report\n\n```text\n" + text + "\n```\n")
    try:
        print(f"Mobile report accepted by ntfy: HTTP {deliver(text)}")
    except Exception as exc:
        print("Mobile delivery failed: " + str(exc)[:200])
        sys.exit(1)
