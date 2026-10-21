#!/usr/bin/env python3
"""Unified "job finished" report (success OR failure) for every automated ColdDirect job.

  python tools/send_job_report.py --job "Deploy to Plesk" --status success --metric "pages=14/14" --note "..."
  python tools/send_job_report.py --selftest

What it does (all best-effort: a reporting problem NEVER changes the job result, exit code is always 0 unless
--strict is given):
  1. posts ONE comment to the single rolling issue  "📊 [ColdDirect Autopilot] Automated Job Reports & SEO Log"
     (created on first use; reopened if someone closed it; owner assigned + @mentioned so GitHub e-mails the
     owner for every finished job; bilingual EN/فارسی). `[LIVE SITE ALERT]` issues stay separate and are NOT touched.
  2. appends the same entry to docs/ai-memory/WORK_LOG.md (CI: via the GitHub Contents API with retries, no git
     push from the runner; local: direct file append). Pushes made with GITHUB_TOKEN never trigger the deploy.
Safety: the repository is PUBLIC - text is scrubbed of tokens/keys/query-string secrets; only metadata the caller
passes (job, status, run URL, commit, metrics, short note) is ever posted. No response bodies, no log excerpts.
Needs: `gh` CLI + GH_TOKEN (issues: write; contents: write only for the WORK_LOG append).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ISSUE_TITLE = "📊 [ColdDirect Autopilot] Automated Job Reports & SEO Log"
LABEL = "autopilot-log"
WORKLOG_PATH = "docs/ai-memory/WORK_LOG.md"
ROOT = Path(__file__).resolve().parent.parent
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

STATUS = {
    "success": ("✅", "SUCCESS", "موفق"),
    "failure": ("❌", "FAILED", "ناموفق"),
    "cancelled": ("⚠️", "CANCELLED", "لغو شده"),
    "skipped": ("⏭️", "SKIPPED", "رد شد"),
}
SECRET_RX = [
    (re.compile(r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"), "[token]"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{20,}"), "[key]"),
    (re.compile(r"ya29\.[0-9A-Za-z_\-]{20,}"), "[token]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?(-----END [A-Z ]*PRIVATE KEY-----|$)"), "[private key]"),
    (re.compile(r"([?&](?:key|token|secret|password|pwd|apikey)=)[^&\s)\"']+", re.I), r"\1[redacted]"),
    (re.compile(r"((?:password|secret|token|apikey|api_key|auth_key)\s*[=:]\s*)[^\s,;\"']{6,}", re.I), r"\1[redacted]"),
]


def scrub(text: str) -> str:
    for rx, rep in SECRET_RX:
        text = rx.sub(rep, text)
    return text


def clip(text: str, n: int = 400) -> str:
    text = " ".join(scrub(str(text)).split())
    return text if len(text) <= n else text[: n - 1] + "…"


class Gh:
    """Thin wrapper over the gh CLI; replaceable in tests."""

    def run(self, args: list[str], input_text: str | None = None) -> str:
        p = subprocess.run(["gh", *args], input=input_text, capture_output=True, text=True, encoding="utf-8", timeout=120)
        if p.returncode != 0:
            raise RuntimeError(f"gh {' '.join(args[:3])} failed: {scrub(p.stderr.strip())[:200]}")
        return p.stdout


def build_entry(job: str, status: str, env: dict, metrics: list[str], notes: list[str], now: datetime) -> dict:
    emoji, en, fa = STATUS.get(status, ("ℹ️", status.upper(), status))
    repo = env.get("GITHUB_REPOSITORY", "")
    server = env.get("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server}/{repo}/actions/runs/{env['GITHUB_RUN_ID']}" if env.get("GITHUB_RUN_ID") and repo else ""
    sha = env.get("GITHUB_SHA", "")[:7]
    return {
        "job": clip(job, 120), "status": status, "emoji": emoji, "en": en, "fa": fa,
        "workflow": clip(env.get("GITHUB_WORKFLOW", "local run"), 120),
        "trigger": clip(env.get("GITHUB_EVENT_NAME", "manual"), 40),
        "time": now.strftime("%Y-%m-%d %H:%M:%S UTC"), "run_url": run_url, "sha": sha,
        "metrics": [clip(m, 200) for m in metrics], "notes": [clip(n, 400) for n in notes],
        "owner": env.get("GITHUB_REPOSITORY_OWNER", ""), "repo": repo,
    }


def comment_body(e: dict) -> str:
    lines = []
    if e["owner"]:
        lines.append(f"@{e['owner']}")
    lines += [f"### {e['emoji']} {e['job']} — {e['en']} / {e['fa']}", "",
              "| | |", "|---|---|",
              f"| Status / وضعیت | **{e['en']}** / **{e['fa']}** |",
              f"| Time / زمان | {e['time']} |",
              f"| Workflow | {e['workflow']} (trigger: {e['trigger']}) |"]
    if e["run_url"]:
        lines.append(f"| Run | {e['run_url']} |")
    if e["sha"]:
        lines.append(f"| Commit | `{e['sha']}` |")
    for m in e["metrics"]:
        k, _, v = m.partition("=")
        lines.append(f"| {k.strip()} | {v.strip() if v else '-'} |")
    for n in e["notes"]:
        lines += ["", f"> {n}"]
    if e["status"] == "failure":
        lines += ["", "Critical failures are also tracked in the separate `[LIVE SITE ALERT]` issue. Open the run link for details."]
    return "\n".join(lines) + "\n"


def worklog_line(e: dict) -> str:
    metrics = "; ".join(e["metrics"])
    notes = " ".join(e["notes"])
    parts = [f"\n## {e['time'][:16].replace(' ', ' ')} UTC - Autopilot: {e['job']} - {e['en']}"]
    parts.append(f"- Workflow: {e['workflow']} ({e['trigger']})" + (f" | run: {e['run_url']}" if e["run_url"] else "")
                 + (f" | commit {e['sha']}" if e["sha"] else ""))
    if metrics:
        parts.append(f"- Metrics: {metrics}")
    if notes:
        parts.append(f"- Note: {notes}")
    return "\n".join(parts) + "\n"


def ensure_issue(gh: Gh, repo: str, owner: str) -> str:
    raw = gh.run(["issue", "list", "--repo", repo, "--state", "all", "--limit", "200", "--json", "number,title,state"])
    for it in json.loads(raw or "[]"):
        if it["title"] == ISSUE_TITLE:
            if it["state"].upper() != "OPEN":
                gh.run(["issue", "reopen", str(it["number"]), "--repo", repo])
            return str(it["number"])
    try:
        gh.run(["label", "create", LABEL, "--repo", repo, "--color", "1D76DB", "--description", "Automated job reports"])
    except RuntimeError:
        pass  # already exists / no permission: continue without the label
    body = ("Single rolling log of every finished automated ColdDirect job (deploy, 24h SEO sync, 48h backup, weekly GSC).\n\n"
            "One comment per job - newest at the bottom. GitHub e-mails the owner for each comment.\n"
            "Critical failures additionally open/update the separate `[LIVE SITE ALERT]` issue.\n"
            "تمام گزارش‌های کارهای خودکار در همین یک Issue ثبت می‌شود.\n")
    args = ["issue", "create", "--repo", repo, "--title", ISSUE_TITLE, "--body", body]
    last = None
    for extra in (["--label", LABEL, "--assignee", owner], ["--label", LABEL], []):
        if "--assignee" in extra and not owner:
            continue
        try:
            url = gh.run(args + extra)
            return url.strip().rsplit("/", 1)[-1]
        except RuntimeError as exc:
            last = exc
    raise last  # type: ignore[misc]


def post_comment(gh: Gh, repo: str, number: str, body: str) -> None:
    gh.run(["issue", "comment", number, "--repo", repo, "--body-file", "-"], input_text=body)


def append_worklog_remote(gh: Gh, repo: str, line: str, sleeper=time.sleep) -> None:
    last = None
    for attempt in range(6):
        try:
            meta = json.loads(gh.run(["api", f"repos/{repo}/contents/{WORKLOG_PATH}?ref=main"]))
            raw = gh.run(["api", "-H", "Accept: application/vnd.github.raw+json", f"repos/{repo}/contents/{WORKLOG_PATH}?ref=main"])
            new = raw.rstrip("\n") + "\n" + line
            payload = json.dumps({"message": "docs: autopilot job report [skip ci]", "branch": "main",
                                  "sha": meta["sha"], "content": base64.b64encode(new.encode("utf-8")).decode()})
            gh.run(["api", "-X", "PUT", f"repos/{repo}/contents/{WORKLOG_PATH}", "--input", "-"], input_text=payload)
            return
        except RuntimeError as exc:  # 409/422 sha conflict from a concurrent job: re-read and retry
            last = exc
            sleeper(2 + attempt * 3)
    raise last  # type: ignore[misc]


def append_worklog_local(line: str, path: Path | None = None) -> None:
    p = path or ROOT / WORKLOG_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = p.read_bytes() if p.exists() else b""
    sep = b"" if existing.endswith(b"\n") or not existing else b"\n"
    p.write_bytes(existing + sep + line.encode("utf-8"))


def report(job, status, metrics, notes, env=None, gh=None, now=None, dry_run=False, no_issue=False, no_worklog=False,
           worklog_path=None, sleeper=time.sleep) -> list[str]:
    env = dict(os.environ if env is None else env)
    gh = gh or Gh()
    now = now or datetime.now(timezone.utc)
    e = build_entry(job, status, env, metrics, notes, now)
    body, line = comment_body(e), worklog_line(e)
    problems: list[str] = []
    if dry_run:
        print(body)
        print(line)
        return problems
    repo, in_ci = env.get("GITHUB_REPOSITORY", ""), env.get("GITHUB_ACTIONS") == "true"
    if not no_issue:
        if not repo:
            problems.append("issue: GITHUB_REPOSITORY not set (skipped)")
        else:
            try:
                post_comment(gh, repo, ensure_issue(gh, repo, e["owner"]), body)
            except Exception as exc:  # noqa: BLE001
                problems.append(f"issue: {clip(exc, 200)}")
    if not no_worklog:
        try:
            if in_ci and repo:
                append_worklog_remote(gh, repo, line, sleeper)
            else:
                append_worklog_local(line, worklog_path)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"worklog: {clip(exc, 200)}")
    return problems


def selftest():
    import tempfile
    # scrubbing
    dirty = "tok ghp_" + "a" * 36 + " url https://x/auto-seo.aspx?key=SECRETVALUE123&y=1 password=hunter22222 AIza" + "b" * 30
    clean = scrub(dirty)
    assert "SECRETVALUE123" not in clean and "hunter22222" not in clean and "ghp_" not in clean and "AIza" not in clean, clean

    class FakeGh(Gh):
        def __init__(self, issues=None, conflicts=0, deny_assignee=False):
            self.calls, self.issues, self.conflicts, self.deny = [], issues if issues is not None else [], conflicts, deny_assignee
            self.log = "# log\n"
            self.sha = 1

        def run(self, args, input_text=None):
            self.calls.append((args, input_text))
            if args[:2] == ["issue", "list"]:
                return json.dumps(self.issues)
            if args[:2] == ["issue", "create"]:
                if self.deny and "--assignee" in args:
                    raise RuntimeError("assignee denied")
                self.issues.append({"number": 7, "title": args[args.index("--title") + 1], "state": "OPEN"})
                return "https://github.com/o/r/issues/7\n"
            if args[:2] in (["label", "create"], ["issue", "comment"], ["issue", "reopen"]):
                return ""
            if args[0] == "api":
                if "-X" in args:
                    if self.conflicts > 0:
                        self.conflicts -= 1
                        raise RuntimeError("409 sha mismatch")
                    data = json.loads(input_text)
                    assert data["sha"] == str(self.sha)
                    self.log = base64.b64decode(data["content"]).decode()
                    self.sha += 1
                    return "{}"
                if any("raw" in a for a in args):
                    return self.log
                return json.dumps({"sha": str(self.sha)})
            raise AssertionError(args)

    env = {"GITHUB_REPOSITORY": "o/r", "GITHUB_REPOSITORY_OWNER": "o", "GITHUB_RUN_ID": "123", "GITHUB_SHA": "abcdef1234",
           "GITHUB_WORKFLOW": "Deploy", "GITHUB_EVENT_NAME": "push", "GITHUB_ACTIONS": "true"}
    now = datetime(2026, 10, 21, 3, 0, tzinfo=timezone.utc)
    # first run creates the issue, posts one comment, appends to WORK_LOG (with a simulated sha conflict)
    g = FakeGh(conflicts=1)
    pr = report("Deploy", "success", ["pages=14/14", "latency=avg 410 ms"], ["all good"], env, g, now, sleeper=lambda s: None)
    assert pr == [], pr
    kinds = [c[0][:2] for c in g.calls]
    assert kinds.count(["issue", "create"]) == 1 and kinds.count(["issue", "comment"]) == 1
    comment = [c for c in g.calls if c[0][:2] == ["issue", "comment"]][0][1]
    assert "@o" in comment and "SUCCESS" in comment and "موفق" in comment and "pages" in comment and "/actions/runs/123" in comment
    assert "Autopilot: Deploy - SUCCESS" in g.log and g.sha == 2
    # second run reuses the issue (no create), failure wording, reopens closed issue
    g.issues[0]["state"] = "CLOSED"
    pr = report("Backup", "failure", [], ["boom"], env, g, now, sleeper=lambda s: None)
    kinds = [c[0][:2] for c in g.calls]
    assert kinds.count(["issue", "create"]) == 1 and kinds.count(["issue", "reopen"]) == 1 and kinds.count(["issue", "comment"]) == 2
    assert "FAILED" in [c for c in g.calls if c[0][:2] == ["issue", "comment"]][1][1]
    # assignee denied -> falls back, still creates exactly one issue
    g2 = FakeGh(deny_assignee=True)
    assert report("x", "success", [], [], env, g2, now, no_worklog=True) == []
    assert sum(1 for c in g2.calls if c[0][:2] == ["issue", "create"]) == 2 and len(g2.issues) == 1
    # failures degrade to problems, never raise
    class Broken(FakeGh):
        def run(self, args, input_text=None):
            raise RuntimeError("network down")
    pr = report("x", "success", [], [], env, Broken(), now, sleeper=lambda s: None)
    assert len(pr) == 2 and all(isinstance(p, str) for p in pr)
    # local worklog append
    with tempfile.TemporaryDirectory() as td:
        wl = Path(td) / "w.md"
        wl.write_text("old text without newline", "utf-8")
        loc = {"GITHUB_ACTIONS": ""}
        assert report("Local", "success", ["a=b"], [], loc, FakeGh(), now, no_issue=True, worklog_path=wl) == []
        txt = wl.read_text("utf-8")
        assert txt.startswith("old text without newline\n") and "Autopilot: Local - SUCCESS" in txt and "a=b" in txt
    assert ISSUE_TITLE == "📊 [ColdDirect Autopilot] Automated Job Reports & SEO Log"
    print("send_job_report selftest OK (scrub, issue create/reuse/reopen, assignee fallback, 409 retry, graceful failure, local worklog)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--job")
    ap.add_argument("--status", default="success")
    ap.add_argument("--metric", action="append", default=[], help='"name=value" row (repeatable)')
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-issue", action="store_true")
    ap.add_argument("--no-worklog", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if not a.job:
        ap.error("--job is required")
    problems = report(a.job, a.status, a.metric, a.note, dry_run=a.dry_run, no_issue=a.no_issue, no_worklog=a.no_worklog)
    for p in problems:
        print(f"::warning::job report: {p}" if os.environ.get("GITHUB_ACTIONS") else f"WARN job report: {p}")
    return 1 if (problems and a.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
