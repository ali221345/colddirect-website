# AGENT-INVENTORY.md

Scan date: 2026-09-13  
Scope: local repo `colddirect-website` + live `/httpdocs` via FTPS listing. **Nothing was changed.**

Host is **Windows Plesk/IIS**, not Linux. `crontab -l` is not available on this workstation or on that host model. Plesk uses **Scheduled Tasks** in the control panel (not readable over FTP).

---

## 1. Cursor Agents (Local)

**Folder `.cursor/agents/` does not exist** in this repo. No `*.md` Cursor agent files were found.

Related local automation (not Cursor agent markdown):

| Path | Role |
|---|---|
| `agent/run.py` | Local “SEO Agent”: rebuilds sitemap, checks/writes `robots.txt`, scores HTML (title / meta description / H1 only). |
| `agent/scripts/sitemap.py` | Walks `colddirect-public-html/**/*.html` and writes `sitemap.xml`. |
| `agent/scripts/robots.py` | Ensures `robots.txt` has `Allow: /` + sitemap URL. |
| `agent/scripts/seo_score.py` | Very thin page scorer (BeautifulSoup). |
| `agent.py` (repo root) | One-shot generator of short `cold-room-repair-{area}.html` stubs. Not scheduled. |
| `scripts/seo-freezer-pass.ps1` | One-off PowerShell SEO pass (canonicals / internal `.html` links). Not an agent. |
| `.github/workflows/seo-agent.yml` | GitHub Action named **Daily SEO Agent**. |
| `.github/workflows/deploy.yml` | FTP deploy of `colddirect-public-html/` → `/httpdocs/` on push to main/master. |
| `n8n-workflow.json` | **“ColdDirect Full Auto Agent”** — `active: false`. Gemini + Claude + `cold-agent-v3.asp` page create. |

Cursor **Skills** on this machine are the global Cursor/Vercel skill packs (unrelated to Cold Direct SEO). They are not project agents.

---

## 2. Host Robots (On Server)

### Folders requested

| Path | Live `/httpdocs` |
|---|---|
| `/agents/` | **Missing** (FTP 550) |
| `/bot/` | **Missing** (FTP 550) |
| `/cron/` | **Missing** (FTP 550) |
| `/api/` | **Missing** (FTP 550) |
| `/robots/` | **Missing** (FTP 550) |
| `/agent/` | **Missing** (FTP 550) |
| `/.cursor/agents/` | **Missing** (FTP 550) |
| `/robots.txt` | **Present** (file, not a folder) |

### Live root scripts that behave like robots

| File path | Language | What it does | Last modified (FTP listing) | Cron schedule |
|---|---|---|---|---|
| `/httpdocs/cold-agent-v3.asp` | Classic ASP / VBScript | Keyed site API: ping, read/write/list/create files, sitemap, stats, branding replace. Used by n8n “create page”. | 2026-09-10 22:16 | None in-file. Triggered by HTTP if something calls it. |
| `/httpdocs/cold-agent.php` | PHP | Keyed `create_page`: writes `/{slug}/index.html`. | 2026-09-08 20:12 | None in-file. HTTP trigger. |
| `/httpdocs/cold-agent.asp` | Classic ASP | **Not seen** in the live root listing (exists in git). Old deploy/cleanup actions. | n/a on live listing | n/a |
| `/httpdocs/daily-job.php` | PHP | Image fixer: checks 10 hero/brand webps, restores from `_restore`, aliases, or GitHub raw. Writes `agent-daily.log`. | Present in git (`colddirect-public-html/`). **Live file not in the filtered FTP snippet; log file is live.** | **Inferred:** Plesk scheduled task. `agent-daily.log` on live was written **2026-09-13 13:00**. |
| `/httpdocs/keepalive.php` | PHP | Warms homepage + those image URLs; writes `keepalive.log`. | In git. **Not confirmed in the filtered live listing.** | Unknown. Likely a second Plesk task if deployed. |
| `/httpdocs/agent-daily.log` | log | Output of daily-job. | 2026-09-13 13:00 (19 514 bytes) | Produced by daily-job. |
| `/httpdocs/robots.txt` | text | `User-agent: *` / `Allow: /` / sitemap URL. | 2026-09-11 18:12 | n/a |
| `/httpdocs/book.php`, `booking.php`, `booking-config.php`, `index.php` | PHP | Booking / homepage — **not** agents. | various | n/a |
| `/httpdocs/js/booking.js`, `/assets/booking.js`, `js/main.js`, `assets/slider.js` | JS | Front-end booking + UI. **Not** bots. | various | n/a |

No OpenAI SDK usage was found in repo code. LLM calls exist only in **inactive** `n8n-workflow.json` (Gemini + Anthropic).

---

## 3. Cron Jobs

### This PC / SSH

`crontab -l` → **not installed** (Windows PowerShell). Cannot read Plesk Scheduled Tasks over FTP.

### Evidence of schedules

| Schedule | Command / target | Where defined | Active? |
|---|---|---|---|
| `0 2 * * *` (02:00 UTC daily) | `python agent/run.py` then optional git commit of sitemap/robots then FTP whole `colddirect-public-html/` to `/httpdocs/` | `.github/workflows/seo-agent.yml` | **Only if** GitHub Actions is enabled on the remote and FTP secrets exist. Not verified from this scan. |
| Daily 09:00 Europe/London | n8n: pick next area → Gemini → Claude → POST `cold-agent-v3.asp?a=create` | `n8n-workflow.json` | **No** (`"active": false`) |
| ~13:00 Europe/London (observed 2026-09-13) | Almost certainly `https://www.colddirect.co.uk/daily-job.php` (or a PHP CLI equivalent) | Plesk Scheduled Tasks (not in git) | **Yes** — live `agent-daily.log` updated at 13:00 |
| On push to `main`/`master` | FTP deploy `colddirect-public-html/` → `/httpdocs/` | `.github/workflows/deploy.yml` | CI, not cron |

**Plesk panel must be opened** to list the exact scheduled-task times for `daily-job.php` / `keepalive.php`.

---

## 4. Gap Analysis

Ideal team = **SEO Writer, Image Fixer, Auto Auditor, Indexer, Internal Linker**

| Role | Status | What exists |
|---|---|---|
| **SEO Writer** | **Partial / off** | Inactive n8n Claude writer; Cursor chat used manually; `agent.py` only writes tiny area stubs. GitHub SEO agent does **not** write articles. |
| **Image Fixer** | **Present** | `daily-job.php` restores missing/tiny webps. Log proves it ran today. |
| **Auto Auditor** | **Weak** | `seo_score.py` only checks title, description, H1. No word-count, keyword cap, duplicate-content, or noindex checks. |
| **Indexer** | **Present (blunt)** | `sitemap.py` + `cold-agent-v3` `a=sitemap` + GitHub 02:00 job. Rebuilds from all HTML (does not respect temporary noindex removals unless someone edits by hand). |
| **Internal Linker** | **Missing** | No agent walks pages to add related-repair links. Only manual inserts + old `seo-freezer-pass.ps1`. |

---

## 5. Recommendation

**Team is not complete.**

You have a working **Image Fixer** and a crude **Indexer**. You do **not** have a dedicated Cursor agent pack, the n8n **SEO Writer** is switched off, the **Auto Auditor** is too thin to catch duplicate/short pages, and **Internal Linker** does not exist.

**Add next: Internal Linker.**  
Reason: new `seo-article` blocks are being written by hand; related URLs are inconsistent (`/page` vs `/page.html`). A linker agent would systematically add 2 related repair links per thin page without another full rewrite pass.

After that: a real **Auto Auditor** (word count &lt; 400, exact-keyword 3–4, noindex vs sitemap). Re-enable or replace the **SEO Writer** only when you want unattended page creation again (n8n is currently the right place, but it is inactive on purpose).

---

## Appendix A — Local root `*.php` / `*.js` (git repo)

PHP at repo root: `book.php`, `booking.php`, `booking-config.php`, `cold-agent.php`, `index.php`.  
JS at repo root: none (JS lives in `js/` and `assets/`).  
Also at root: `agent.py`, `cold-agent.asp`, `cold-agent-v3.asp`.

`colddirect-public-html/` extra PHP: `daily-job.php`, `keepalive.php` (plus the booking set).

## Appendix B — Name/content hits (openai, agent, bot, cron, auto, seo)

- **openai**: none in code. Anthropic + Gemini only in inactive n8n JSON.
- **agent**: `agent/`, `agent.py`, `agent-data.json`, `cold-agent*.php/*.asp`, `agent-daily.log`, n8n workflow.
- **bot**: GitHub `github-actions[bot]` commit identity in `seo-agent.yml`; `robots.txt`.
- **cron**: GitHub `cron: "0 2 * * *"`, n8n cron node 09:00 (inactive).
- **auto**: n8n name “Full Auto Agent”; no other auto-* robots.
- **seo**: `agent/scripts/seo_score.py`, `seo-agent.yml`, `scripts/seo-freezer-pass.ps1`, `seo-cleanup-report.txt`.

## Appendix C — Scan limits

- No SSH to Plesk → **cannot dump the real Scheduled Tasks list**.
- Live FTP listing was filtered; `daily-job.php` inferred from `agent-daily.log`.
- Did not invoke keyed agent URLs (would be a write-capable API).
