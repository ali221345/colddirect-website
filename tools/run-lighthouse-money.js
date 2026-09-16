#!/usr/bin/env node
/** Run Lighthouse mobile on money URLs; write JSON summary. */
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const base = process.argv[2] || "http://127.0.0.1:8765";
const label = process.argv[3] || "run";
const outDir = path.join("docs", "lighthouse", label);
fs.mkdirSync(outDir, { recursive: true });

const pages = [
  { id: "home", path: "/" },
  { id: "commercial-fridge-london", path: "/commercial-fridge-repair-london.html" },
  { id: "foster", path: "/foster-fridge-repair-london.html" },
  { id: "true", path: "/true-fridge-repair-london.html" },
  { id: "liebherr", path: "/liebherr-fridge-repair-london.html" },
];

const summary = [];
for (const p of pages) {
  const url = base.replace(/\/$/, "") + p.path;
  const outJson = path.join(outDir, `${p.id}.json`);
  console.error("Lighthouse", url);
  try {
    execFileSync(
      "npx",
      [
        "--yes",
        "lighthouse",
        url,
        "--only-categories=performance,accessibility,best-practices,seo",
        "--form-factor=mobile",
        "--screenEmulation.mobile",
        "--chrome-flags=--headless --no-sandbox --disable-gpu",
        "--output=json",
        `--output-path=${outJson}`,
        "--quiet",
      ],
      { stdio: ["ignore", "inherit", "inherit"], shell: true }
    );
    const raw = JSON.parse(fs.readFileSync(outJson, "utf8"));
    const cats = raw.categories || {};
    const audits = raw.audits || {};
    summary.push({
      id: p.id,
      url,
      performance: Math.round((cats.performance?.score || 0) * 100),
      accessibility: Math.round((cats.accessibility?.score || 0) * 100),
      bestPractices: Math.round((cats["best-practices"]?.score || 0) * 100),
      seo: Math.round((cats.seo?.score || 0) * 100),
      lcp: audits["largest-contentful-paint"]?.displayValue || null,
      cls: audits["cumulative-layout-shift"]?.displayValue || null,
      tbt: audits["total-blocking-time"]?.displayValue || null,
      fcp: audits["first-contentful-paint"]?.displayValue || null,
    });
  } catch (e) {
    summary.push({ id: p.id, url, error: String(e.message || e) });
  }
}

const summaryPath = path.join(outDir, "summary.json");
fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
console.error("Wrote", summaryPath);
