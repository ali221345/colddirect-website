/**
 * ColdDirect daily SEO updater. 24h cycle (GitHub Actions 05:00 UTC / 06:00 London BST, or local Task Scheduler).
 * Usage: node scripts/daily-seo-update.js
 * Auth: GSC_CREDENTIALS_JSON env, or ./gsc-key.json / ./credentials.json, or Cursor MCP (local).
 * Never rewrite titles more than once per 7 days per page.
 * Never change homepage H1 more than once per 30 days.
 * Fridge/freezer H1 locked 14 days from 2026-09-14.
 */
const { spawnSync } = require("child_process");
const { existsSync, mkdirSync, readFileSync, writeFileSync, appendFileSync } = require("fs");
const { join, dirname } = require("path");
const { homedir } = require("os");
const { pathToFileURL } = require("url");

const ROOT = join(__dirname, "..");
const PUBLIC = join(ROOT, "colddirect-public-html");
const AUDIT = join(ROOT, "seo-audit");
const STATE_PATH = join(AUDIT, "daily-seo-state.json");
const CSV_PATH = join(AUDIT, "daily-positions.csv");
const LOG_PATH = join(AUDIT, "cron.log");
const BACKUP_DIR = join(AUDIT, "title-backups");
const HOST = "www.colddirect.co.uk";
const IP = "5.77.41.163";
const CURL = process.platform === "win32" ? "curl.exe" : "curl";
const DEVNULL = process.platform === "win32" ? "NUL" : "/dev/null";
const SITE_URL = process.env.GSC_SITE_URL || "https://www.colddirect.co.uk/";
const ACCOUNT_ALIAS = "colddirect22@gmail.com";
const SITEMAP_EXPECT = 115;
const TITLE_COOLDOWN_DAYS = 7;
const HOMEPAGE_H1_DAYS = 30;
const FRIDGE_FREEZER_H1_UNTIL = "2026-09-28";

const PRIORITY_QUERIES = [
  { query: "fridge repair london", baseline: 21.6, file: "fridge-repair-london.html", href: "/fridge-repair-london.html", anchor: "fridge repair london" },
  { query: "freezer repair london", baseline: 29.9, file: "freezer-repair-london.html", href: "/freezer-repair-london.html", anchor: "freezer repair london" },
  { query: "commercial fridge repair london", baseline: 11.7, file: "commercial-fridge-repair-london.html", href: "/commercial-fridge-repair-london.html", anchor: "commercial fridge repair london" },
  { query: "cold room repair london", baseline: 4.9, file: "cold-room-repair-london.html", href: "/cold-room-repair-london.html", anchor: "cold room repair london" },
  { query: "chiller repair near me", baseline: 9.8, file: "chiller-repair-london.html", href: "/chiller-repair-london.html", anchor: "chiller repair near me" },
  { query: "commercial freezer repair london", baseline: 8.2, file: "commercial-freezer-repair-london.html", href: "/commercial-freezer-repair-london.html", anchor: "commercial freezer repair london" },
  { query: "ice machine repair london", baseline: null, file: "ice-machine-repair-london.html", href: "/ice-machine-repair-london.html", anchor: "ice machine repair london" },
];

const BLOG_DONORS = [
  "blog/why-commercial-fridge-not-cold-enough.html",
  "blog/why-commercial-freezer-not-freezing.html",
  "blog/different-types-of-ice.html",
  "blog/types-of-cold-storage.html",
  "blog/smeg-fridge-freezer-control-panel.html",
  "blog/commercial-fridge-repair-cost-london.html",
];

const HEALTH_URLS = [
  "/",
  "/sitemap.xml",
  "/commercial-fridge-repair-london.html",
  "/commercial-freezer-repair-london.html",
  "/fridge-repair-london.html",
  "/freezer-repair-london.html",
  "/cold-room-repair-london.html",
  "/chiller-repair-london.html",
  "/ice-machine-repair-london.html",
  "/blog/types-of-cold-storage",
  "/blog/smeg-fridge-freezer-control-panel",
  "/cold-room-repairs-london",
  "/commercial-fridge-repairs-london",
];

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  mkdirSync(AUDIT, { recursive: true });
  appendFileSync(LOG_PATH, line + "\n", "utf8");
}

function todayLondon() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
}

function daysBetween(a, b) {
  const pa = Date.parse(a + "T00:00:00Z");
  const pb = Date.parse(b + "T00:00:00Z");
  return Math.round((pb - pa) / 86400000);
}

function loadState() {
  const seed = {
    lastHomepageH1Change: "2026-09-14",
    h1Locks: {
      "commercial-fridge-repair-london.html": FRIDGE_FREEZER_H1_UNTIL,
      "commercial-freezer-repair-london.html": FRIDGE_FREEZER_H1_UNTIL,
      "fridge-repair-london.html": FRIDGE_FREEZER_H1_UNTIL,
      "freezer-repair-london.html": FRIDGE_FREEZER_H1_UNTIL,
    },
    titleRewrites: {},
    queryHistory: {},
    pageDaily: {},
    linksAdded: {},
  };
  if (!existsSync(STATE_PATH)) return seed;
  try {
    return { ...seed, ...JSON.parse(readFileSync(STATE_PATH, "utf8")) };
  } catch {
    return seed;
  }
}

function saveState(state) {
  writeFileSync(STATE_PATH, JSON.stringify(state, null, 2), "utf8");
}

function curlHead(path) {
  const url = path.startsWith("http") ? path : `https://${HOST}${path}`;
  const r = spawnSync(
    CURL,
    ["-sS", "-o", DEVNULL, "-w", "%{http_code}", "--resolve", `${HOST}:443:${IP}`, "-I", "--max-time", "25", url],
    { encoding: "utf8" }
  );
  return (r.stdout || "").trim();
}

function curlGet(path) {
  const url = path.startsWith("http") ? path : `https://${HOST}${path}`;
  const r = spawnSync(
    CURL,
    ["-sS", "-w", "\n__CODE__%{http_code}", "--resolve", `${HOST}:443:${IP}`, "--max-time", "40", url],
    { encoding: "utf8", maxBuffer: 2 * 1024 * 1024 }
  );
  const out = r.stdout || "";
  if (!out.includes("__CODE__")) return { code: "000", body: out };
  const [body, code] = out.split("__CODE__");
  return { code: (code || "").trim(), body };
}

function pageToFile(pageUrl) {
  try {
    const u = new URL(pageUrl);
    let p = u.pathname;
    if (p === "/" || p === "") return "index.html";
    if (p.endsWith("/")) p += "index.html";
    if (!p.endsWith(".html") && !p.endsWith(".asp")) p += ".html";
    return p.replace(/^\//, "");
  } catch {
    return null;
  }
}

function canRewriteTitle(state, rel, today) {
  if (!rel) return false;
  if (rel === "index.html") return false;
  const last = state.titleRewrites[rel];
  if (last && daysBetween(last, today) < TITLE_COOLDOWN_DAYS) return false;
  const lock = state.h1Locks[rel];
  if (lock && today < lock) return false;
  return true;
}

function backupTitle(rel, html) {
  mkdirSync(BACKUP_DIR, { recursive: true });
  const m = html.match(/<title>[^<]*<\/title>/i);
  const d = html.match(/<meta name="description"[^>]*>/i);
  const stamp = `${todayLondon()}-${rel.replace(/[\\/]/g, "_")}`;
  writeFileSync(join(BACKUP_DIR, stamp + ".txt"), `${m ? m[0] : ""}\n${d ? d[0] : ""}\n`, "utf8");
}

function rewriteTitleMeta(rel, html) {
  const nextTitle = html.replace(/<title>[^<]*<\/title>/i, (t) => {
    const inner = t.replace(/<\/?title>/gi, "");
    if (/24\/7/i.test(inner)) return t;
    return `<title>${inner.replace(/\s*\|\s*ColdDirect\s*$/i, "").replace(/\s*\|\s*Cold Direct\s*$/i, "")} | 24/7 | ColdDirect</title>`;
  });
  return nextTitle.replace(/<meta name="description" content="([^"]*)"/i, (full, content) => {
    if (/24\/7/.test(content)) return full;
    const trimmed = content.replace(/^⚡\s*/, "").slice(0, 140);
    return `<meta name="description" content="${trimmed} 24/7 trade only."`;
  });
}

function addBlogLink(relBlog, href, anchor, marker) {
  const full = join(PUBLIC, relBlog);
  if (!existsSync(full)) return false;
  let html = readFileSync(full, "utf8");
  if (html.includes(marker) || html.includes(`href="${href}"`)) return false;
  const snippet = ` Need <a href="${href}" data-daily-seo="${marker}">${anchor}</a>?`;
  const re = /(<article[^>]*>[\s\S]*?<p>)/i;
  if (!re.test(html)) return false;
  html = html.replace(re, `$1${snippet}`);
  writeFileSync(full, html, "utf8");
  return true;
}

function ftpUpload(relPaths) {
  const py = `
import ftplib, os
from pathlib import Path
root = Path(r${JSON.stringify(ROOT)})
env = {}
p = root / ".env"
if p.exists():
    for line in p.read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if not t or t.startswith("#") or "=" not in t: continue
        k, v = t.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
host = os.environ.get("COLD_FTP_HOST") or os.environ.get("FTP_HOST") or env.get("COLD_FTP_HOST") or env.get("FTP_HOST") or env.get("PLESK_FTP_HOST") or "5.77.41.163"
user = os.environ.get("COLD_FTP_USER") or os.environ.get("FTP_USERNAME") or env.get("COLD_FTP_USER") or env.get("FTP_USER") or env.get("PLESK_FTP_USER")
pw = os.environ.get("COLD_FTP_PASS") or os.environ.get("FTP_PASSWORD") or env.get("COLD_FTP_PASS") or env.get("FTP_PASS") or env.get("PLESK_FTP_PASS")
remote = (os.environ.get("COLD_FTP_PATH") or env.get("COLD_FTP_PATH") or env.get("FTP_PATH") or env.get("PLESK_FTP_PATH") or "/httpdocs").rstrip("/")
if not user or not pw:
    raise SystemExit("no ftp credentials")
ftp = ftplib.FTP(); ftp.connect(host, 21, timeout=45); ftp.login(user, pw); ftp.set_pasv(True)
files = ${JSON.stringify(relPaths)}
local = root / "colddirect-public-html"
for rel in files:
    lp = local.joinpath(*rel.replace("\\\\","/").split("/"))
    rp = remote + "/" + rel.replace("\\\\", "/")
    parent = rp.rsplit("/", 1)[0]
    cur = ""
    for part in parent.strip("/").split("/"):
        cur += "/" + part
        try: ftp.cwd(cur)
        except Exception:
            try: ftp.mkd(cur)
            except Exception: pass
            ftp.cwd(cur)
    with open(lp, "rb") as f:
        ftp.storbinary("STOR " + rp, f)
    print("UPLOADED", rel)
ftp.quit()
`;
  const r = spawnSync("python", ["-c", py], { encoding: "utf8" });
  if (r.status !== 0) {
    log("FTP_FAIL " + (r.stderr || r.stdout || "").slice(0, 400));
    return false;
  }
  log("FTP_OK " + (r.stdout || "").trim().replace(/\n/g, " | "));
  return true;
}

function add404Redirect(path) {
  const key = path.replace(/^\//, "").replace(/\/$/, "");
  if (!key) return false;
  const guess = key.replace(/s-london$/, "-london");
  const htmlGuess = guess.endsWith(".html") ? guess : guess + ".html";
  const targetFile = join(PUBLIC, htmlGuess);
  const value = existsSync(targetFile) ? "/" + htmlGuess.replace(/\\/g, "/") : "/";
  const cfg = join(PUBLIC, "web.config");
  let xml = readFileSync(cfg, "utf8");
  if (xml.includes(`key="${key}"`)) return false;
  xml = xml.replace(
    '<rewriteMap name="GscJunkRedirects" defaultValue="">',
    `<rewriteMap name="GscJunkRedirects" defaultValue="">\n          <add key="${key}" value="${value}" />`
  );
  writeFileSync(cfg, xml, "utf8");
  log("ALERT 404 auto-map " + key + " -> " + value);
  return true;
}

function loadGscCredentials() {
  if (process.env.GSC_CREDENTIALS_JSON) {
    return JSON.parse(process.env.GSC_CREDENTIALS_JSON);
  }
  const candidates = [
    process.env.GSC_KEY_FILE,
    join(ROOT, "gsc-key.json"),
    join(ROOT, "credentials.json"),
    join(ROOT, "seo-audit", "gsc-key.json"),
  ].filter(Boolean);
  for (const p of candidates) {
    if (existsSync(p)) return JSON.parse(readFileSync(p, "utf8"));
  }
  return null;
}

function searchconsoleFromCredentials(credentials) {
  const { google } = require("googleapis");
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: [
      "https://www.googleapis.com/auth/webmasters",
      "https://www.googleapis.com/auth/webmasters.readonly",
    ],
  });
  return google.searchconsole({ version: "v1", auth });
}

function searchconsoleFromOauth() {
  const { google } = require("googleapis");
  const id = process.env.GOOGLE_CLIENT_ID;
  const secret = process.env.GOOGLE_CLIENT_SECRET;
  const refresh = process.env.GSC_REFRESH_TOKEN;
  if (!id || !secret || !refresh) return null;
  const oauth2 = new google.auth.OAuth2(id, secret);
  oauth2.setCredentials({ refresh_token: refresh });
  return google.searchconsole({ version: "v1", auth: oauth2 });
}

async function resolveSite(client, preferred) {
  const sites = await client.sites.list();
  return (sites.data.siteEntry || []).find((e) => (e.siteUrl || "").includes("colddirect"))?.siteUrl || preferred;
}

async function gscClient() {
  const preferred = SITE_URL;
  const credentials = loadGscCredentials();
  if (credentials) {
    const client = searchconsoleFromCredentials(credentials);
    const siteUrl = await resolveSite(client, preferred);
    return { client, siteUrl, account: { alias: credentials.client_email || "service-account" } };
  }
  const oauthClient = searchconsoleFromOauth();
  if (oauthClient) {
    const siteUrl = await resolveSite(oauthClient, preferred);
    return { client: oauthClient, siteUrl, account: { alias: ACCOUNT_ALIAS } };
  }
  const mcpPath = join(homedir(), ".cursor", "mcp.json");
  if (!existsSync(mcpPath)) {
    throw new Error("No GSC_CREDENTIALS_JSON, no local gsc-key.json/credentials.json, and no Cursor MCP tokens");
  }
  const mcp = JSON.parse(readFileSync(mcpPath, "utf8"));
  const env = mcp.mcpServers["google-search-console"].env;
  process.env.GOOGLE_CLIENT_ID = env.GOOGLE_CLIENT_ID;
  process.env.GOOGLE_CLIENT_SECRET = env.GOOGLE_CLIENT_SECRET;
  const pkgRoot = join(homedir(), "AppData", "Local", "Temp", "search-console-mcp-install");
  const { getSearchConsoleClient } = await import(
    pathToFileURL(join(pkgRoot, "node_modules", "search-console-mcp", "dist", "google", "client.js")).href
  );
  const { loadConfig } = await import(
    pathToFileURL(join(pkgRoot, "node_modules", "search-console-mcp", "dist", "common", "auth", "config.js")).href
  );
  const config = await loadConfig();
  const account = Object.values(config.accounts).find((a) => a.alias === ACCOUNT_ALIAS && a.engine === "google");
  if (!account) throw new Error("missing GSC account " + ACCOUNT_ALIAS);
  const probe = await getSearchConsoleClient(preferred, account.id);
  const siteUrl = await resolveSite(probe, preferred);
  const client = await getSearchConsoleClient(siteUrl, account.id);
  return { client, siteUrl, account };
}

async function queryAnalytics(client, siteUrl, body) {
  const res = await client.searchanalytics.query({
    siteUrl,
    requestBody: { type: "web", dataState: "all", ...body },
  });
  return res.data.rows || [];
}

function ymdOffset(endYmd, daysBack) {
  const d = new Date(endYmd + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() - daysBack);
  return d.toISOString().slice(0, 10);
}

async function main() {
  mkdirSync(AUDIT, { recursive: true });
  mkdirSync(BACKUP_DIR, { recursive: true });
  const today = todayLondon();
  const changes = [];
  const alerts = [];
  log("START daily-seo-update " + today);

  const endDate = ymdOffset(today, 1);
  const startDate = ymdOffset(endDate, 6);
  log("GSC window " + startDate + " .. " + endDate);

  const { client, siteUrl, account } = await gscClient();
  log("GSC siteUrl " + siteUrl + " account " + (account && account.alias));

  const totalsRows = await queryAnalytics(client, siteUrl, { startDate, endDate, rowLimit: 5 });
  const totals = totalsRows[0] || { clicks: 0, impressions: 0, ctr: 0, position: 0 };

  const queryRows = await queryAnalytics(client, siteUrl, {
    startDate,
    endDate,
    dimensions: ["query"],
    rowLimit: 5000,
  });
  const qMap = new Map(queryRows.map((r) => [r.keys[0], r]));

  const dateQueryRows = await queryAnalytics(client, siteUrl, {
    startDate,
    endDate,
    dimensions: ["date", "query"],
    rowLimit: 25000,
  });

  const pageRows = await queryAnalytics(client, siteUrl, {
    startDate,
    endDate,
    dimensions: ["page"],
    rowLimit: 250,
  });

  const datePageRows = await queryAnalytics(client, siteUrl, {
    startDate,
    endDate,
    dimensions: ["date", "page"],
    rowLimit: 25000,
  });

  const csvHeader = "date,query,clicks,impressions,ctr,position,window_start,window_end\n";
  let csv = existsSync(CSV_PATH) ? readFileSync(CSV_PATH, "utf8") : csvHeader;
  if (!csv.startsWith("date,query")) csv = csvHeader + csv;
  for (const item of PRIORITY_QUERIES) {
    const row = qMap.get(item.query) || { clicks: 0, impressions: 0, ctr: 0, position: 0 };
    csv += `${today},${JSON.stringify(item.query)},${row.clicks || 0},${row.impressions || 0},${(row.ctr || 0).toFixed(6)},${(row.position || 0).toFixed(2)},${startDate},${endDate}\n`;
  }
  writeFileSync(CSV_PATH, csv, "utf8");
  log("WROTE " + CSV_PATH);

  const state = loadState();
  const prevQueries = state.queryHistory || {};
  const deploy = [];

  for (const item of PRIORITY_QUERIES) {
    const row = qMap.get(item.query) || { clicks: 0, impressions: 0, ctr: 0, position: 0 };
    const pos = row.position || 0;
    const hist = prevQueries[item.query] || [];
    const last = hist[hist.length - 1];
    if (last && last.position && pos && pos - last.position > 5) {
      const msg = `ALERT position drop >5 in ~48h: "${item.query}" ${last.position.toFixed(1)} -> ${pos.toFixed(1)}`;
      alerts.push(msg);
      log(msg);
      let added = 0;
      for (const blog of BLOG_DONORS) {
        if (added >= 2) break;
        const marker = `drop-${item.query}`;
        if (addBlogLink(blog, item.href, item.anchor, marker)) {
          added += 1;
          deploy.push(blog);
          changes.push(`+2-link drop: ${blog} -> ${item.href} (${item.query})`);
        }
      }
    }
    if (pos >= 11 && pos <= 20) {
      const marker = `mid-${item.query}`;
      const already = Object.keys(state.linksAdded || {}).some((k) => k.startsWith(marker) && daysBetween(state.linksAdded[k], today) < 7);
      if (!already) {
        for (const blog of BLOG_DONORS) {
          if (addBlogLink(blog, item.href, item.anchor, marker)) {
            state.linksAdded = state.linksAdded || {};
            state.linksAdded[marker + "|" + blog] = today;
            deploy.push(blog);
            changes.push(`mid-pack link: ${blog} -> ${item.href} (${item.query} pos ${pos.toFixed(1)})`);
            break;
          }
        }
      }
    }
    hist.push({ date: today, position: pos, clicks: row.clicks || 0, impressions: row.impressions || 0, ctr: row.ctr || 0 });
    prevQueries[item.query] = hist.slice(-30);
  }
  state.queryHistory = prevQueries;

  const byPageDate = {};
  for (const r of datePageRows) {
    const [date, page] = r.keys;
    byPageDate[page] = byPageDate[page] || {};
    byPageDate[page][date] = r;
  }
  for (const [page, days] of Object.entries(byPageDate)) {
    const dates = Object.keys(days).sort();
    if (dates.length < 7) continue;
    const last7 = dates.slice(-7);
    const ok = last7.every((d) => days[d].impressions > 1000 && days[d].ctr < 0.005);
    if (!ok) continue;
    const rel = pageToFile(page);
    if (!canRewriteTitle(state, rel, today)) {
      log("SKIP title rewrite cooldown/lock " + rel);
      continue;
    }
    const full = join(PUBLIC, rel);
    if (!existsSync(full)) continue;
    const html = readFileSync(full, "utf8");
    backupTitle(rel, html);
    const next = rewriteTitleMeta(rel, html);
    if (next === html) continue;
    writeFileSync(full, next, "utf8");
    state.titleRewrites[rel] = today;
    deploy.push(rel);
    changes.push("title/meta rewrite (low CTR 7d): " + rel);
    log("TITLE_REWRITE " + rel);
  }

  const broken = [];
  for (const path of HEALTH_URLS) {
    const code = curlHead(path);
    const final = curlGet(path).code;
    if (code === "404" || final === "404") {
      broken.push(path);
      if (add404Redirect(path)) {
        deploy.push("web.config");
        changes.push("404 auto-redirect " + path);
      }
      alerts.push("ALERT 404 " + path);
      log("ALERT 404 " + path + " head=" + code + " get=" + final);
    }
  }

  let sm = curlGet("/sitemap.xml");
  let locCount = (sm.body.match(/<loc>/g) || []).length;
  log("SITEMAP http=" + sm.code + " locs=" + locCount);
  if (sm.code === "500") {
    alerts.push("ALERT sitemap 500 — pass-through rule + FTP web.config + GSC resubmit");
    log("SITEMAP_500 attempting web.config FTP and GSC resubmit");
    deploy.push("web.config");
    try {
      await client.sitemaps.submit({ siteUrl, feedpath: `https://${HOST}/sitemap.xml` });
      changes.push("GSC sitemap resubmit after 500");
    } catch (e) {
      log("SITEMAP_RESUBMIT_FAIL " + e.message);
    }
  }
  let submittedGsc = null;
  try {
    const listed = await client.sitemaps.get({ siteUrl, feedpath: `https://${HOST}/sitemap.xml` });
    submittedGsc = listed.data?.contents?.[0]?.submitted || listed.data?.contents?.[0]?.submitted === 0 ? listed.data.contents[0] : listed.data;
    log("SITEMAP_GSC " + JSON.stringify(listed.data?.contents || listed.data));
  } catch (e) {
    log("SITEMAP_GSC_FAIL " + e.message);
  }

  const uniqueDeploy = [...new Set(deploy)];
  if (uniqueDeploy.length) {
    ftpUpload(uniqueDeploy);
  }

  const ranked = queryRows
    .filter((r) => r.impressions >= 20)
    .map((r) => ({ query: r.keys[0], ...r }));
  const winners = [...ranked].sort((a, b) => (a.position || 99) - (b.position || 99)).slice(0, 3);
  const losers = [...ranked].sort((a, b) => (b.position || 0) - (a.position || 0)).slice(0, 3);

  const report = [
    `# Daily SEO report ${today}`,
    "",
    `Window: ${startDate} to ${endDate} (Europe/London). Account: ${(account && account.alias) || ACCOUNT_ALIAS}.`,
    "",
    "## Totals",
    `- Clicks: ${totals.clicks || 0}`,
    `- Impressions: ${totals.impressions || 0}`,
    `- CTR: ${((totals.ctr || 0) * 100).toFixed(2)}%`,
    `- Avg position: ${(totals.position || 0).toFixed(1)}`,
    "",
    "## Priority queries",
    "| Query | Clicks | Impr | CTR | Pos | Baseline |",
    "|---|---:|---:|---:|---:|---:|",
    ...PRIORITY_QUERIES.map((item) => {
      const row = qMap.get(item.query) || {};
      return `| ${item.query} | ${row.clicks || 0} | ${row.impressions || 0} | ${(((row.ctr || 0) * 100).toFixed(2))}% | ${(row.position || 0).toFixed(1)} | ${item.baseline ?? "—"} |`;
    }),
    "",
    "## Top 3 winners (best position, impr≥20)",
    ...winners.map((w) => `- ${w.query}: pos ${(w.position || 0).toFixed(1)}, ${w.clicks} clicks, ${w.impressions} impr`),
    "",
    "## Top 3 losers (worst position, impr≥20)",
    ...losers.map((w) => `- ${w.query}: pos ${(w.position || 0).toFixed(1)}, ${w.clicks} clicks, ${w.impressions} impr`),
    "",
    "## Sitemap",
    `- Live HTTP: ${sm.code}`,
    `- \`<loc>\` count: ${locCount} (expect ~${SITEMAP_EXPECT})`,
    `- GSC: ${JSON.stringify(submittedGsc)}`,
    "",
    "## What changed",
    changes.length ? changes.map((c) => `- ${c}`).join("\n") : "- No title, link, or 404 changes today (guards held).",
    "",
    "## Alerts",
    alerts.length ? alerts.map((a) => `- ${a}`).join("\n") : "- None",
    "",
    "## Guards",
    `- Title rewrite: max once per ${TITLE_COOLDOWN_DAYS} days per page`,
    `- Homepage H1: last changed ${state.lastHomepageH1Change} (min ${HOMEPAGE_H1_DAYS} days)`,
    `- Fridge/freezer H1 lock until ${FRIDGE_FREEZER_H1_UNTIL} (links only)`,
    "",
  ].join("\n");

  const reportPath = join(AUDIT, `daily-report-${today}.md`);
  writeFileSync(reportPath, report, "utf8");
  saveState(state);
  log("WROTE " + reportPath);
  log("DONE changes=" + changes.length + " alerts=" + alerts.length);
}

main().catch((err) => {
  log("FATAL " + (err && err.stack ? err.stack : String(err)));
  process.exit(1);
});
