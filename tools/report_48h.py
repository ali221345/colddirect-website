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


def watchlist_lines(summary):
    """Bilingual mobile details for all 13 URLs, with the six priority pages marked."""
    if not summary:
        return [
            "Indexing watchlist: no inspection data in this run.",
            "فهرست ایندکس: در این اجرا داده‌ای از URL Inspection دریافت نشد.",
        ]
    total = summary.get("total", 0)
    passed = summary.get("passed", 0)
    waiting = summary.get("waiting", 0)
    failed = summary.get("failed", 0)
    priority = summary.get("prioritySix", {})
    complete = summary.get("complete") is True and total == 13 and passed == 13 and failed == 0
    lines = [
        f"Indexing watchlist: {passed}/{total} PASS; {waiting} waiting; {failed} inspection errors.",
        f"Six-page re-check: {priority.get('passed', 0)}/{priority.get('total', 6)} PASS.",
        ("All 13 URLs are PASS; pending watchlist alerts are complete." if complete else
         "Next automatic URL Inspection remains on the 48-hour schedule until 13/13 PASS."),
        f"فهرست ایندکس: {passed}/{total} با وضعیت PASS؛ {waiting} در انتظار؛ {failed} خطای بررسی.",
        f"بررسی مجدد شش صفحه: {priority.get('passed', 0)}/{priority.get('total', 6)} با وضعیت PASS.",
        ("هر ۱۳ URL به PASS رسیدند؛ هشدارهای در انتظار فهرست پیگیری کامل شد." if complete else
         "URL Inspection خودکار بعدی در همان برنامهٔ ۴۸ ساعته تا رسیدن به ۱۳/۱۳ PASS ادامه دارد."),
        "URL Inspection results / نتایج بررسی URL:",
    ]
    for page in summary.get("pages", []):
        verdict = page.get("verdict", "?")
        icon = "✅" if verdict == "PASS" else "⚠️" if verdict == "ERROR" else "⏳"
        marker = " [6-page/۶ صفحه]" if page.get("prioritySix") else ""
        lines.append(f"{icon} {page.get('path', '?')}{marker} — {verdict}: {page.get('coverageState', '?')}")
    return lines


def message(status, outcomes, now=None, watchlist=None):
    now = now or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"ColdDirect 48h | {now}", "English: " + ("All requested checks passed." if status == "success" else "Attention required; inspect failed checks below.")]
    for key in ORDER:
        value = outcomes.get(key, "not run")
        lines.append(f"{LABELS[key][0]}: {value}")
    lines.append("فارسی: " + ("همه بررسی‌های درخواستی موفق بودند." if status == "success" else "نیاز به بررسی دارد؛ موارد ناموفق در زیر آمده‌اند."))
    for key in ORDER:
        value = outcomes.get(key, "اجرا نشد")
        lines.append(f"{LABELS[key][1]}: {value}")
    lines.extend(watchlist_lines(watchlist))
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
    pending_pages = [{"path": f"/page-{i}/", "verdict": "PASS" if i < 9 else "NEUTRAL",
                      "coverageState": "Submitted and indexed" if i < 9 else "Discovered - currently not indexed",
                      "prioritySix": i < 6} for i in range(13)]
    pending = {"total": 13, "passed": 9, "waiting": 4, "failed": 0, "complete": False,
               "prioritySix": {"total": 6, "passed": 6}, "pages": pending_pages}
    text = message("failure", {"backup": "success", "voice": "failure"}, "2026-10-26 00:00 UTC", pending)
    assert "Attention required" in text and "نیاز به بررسی" in text and "Voice API: failure" in text
    assert "All requested checks passed" not in text and "همه بررسی‌های درخواستی موفق" not in text
    assert "Indexing watchlist: 9/13 PASS" in text and "فهرست ایندکس: 9/13" in text
    assert "Six-page re-check: 6/6 PASS" in text and "بررسی مجدد شش صفحه: 6/6" in text
    assert "until 13/13 PASS" in text and "۱۳/۱۳ PASS" in text and text.count("[6-page/۶ صفحه]") == 6
    complete = dict(pending, passed=13, waiting=0, complete=True,
                    pages=[dict(page, verdict="PASS", coverageState="Submitted and indexed") for page in pending_pages])
    done = message("success", {key: "success" for key in ORDER}, watchlist=complete)
    assert "pending watchlist alerts are complete" in done and "هشدارهای در انتظار فهرست پیگیری کامل شد" in done
    assert "Next automatic URL Inspection remains" not in done
    assert "no inspection data" in message("success", {key: "success" for key in ORDER})
    good = {key: "success" for key in ORDER}
    assert overall("success", good) == "success"
    assert overall("success", dict(good, voice="failure")) == "failure"
    assert overall("failure", good) == "failure"
    print("report_48h selftest OK: bilingual 13-URL pending and all-PASS reports")


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
    watchlist_path = ROOT / "backup-out" / "gsc-watchlist.json"
    try:
        watchlist = json.loads(watchlist_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        watchlist = None
    text = message(status, outcomes, watchlist=watchlist)
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
