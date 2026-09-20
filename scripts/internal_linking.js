/**
 * Idempotent homepage internal links for GSC high-click queries.
 * Usage: node scripts/internal_linking.js
 *
 * SEO-safe: fridge/freezer query anchors point at dedicated pages.
 * Only cold-room query anchors point at /cold-room-repairs-london.
 */
const { existsSync, readFileSync, writeFileSync } = require("fs");
const { join } = require("path");

const ROOT = join(__dirname, "..");
const HOMES = [
  join(ROOT, "index.html"),
  join(ROOT, "colddirect-public-html", "index.html"),
];

const LINKS = [
  {
    href: "/cold-room-repairs-london",
    anchor: "cold room repair london",
    count: 3,
    note: "Priority #1 — homepage already ranks for this query; pass juice to the winning URL",
  },
  {
    href: "/commercial-fridge-repair-london",
    anchor: "commercial fridge repair london",
    count: 1,
    note: "Dedicated page is not ranking; homepage currently takes the clicks",
  },
  {
    href: "/fridge-repair-london",
    anchor: "fridge repair london",
    count: 1,
    note: "Dedicated page is not ranking; homepage currently takes the clicks",
  },
  {
    href: "/freezer-repair-london",
    anchor: "freezer repair london",
    count: 1,
    note: "Clicks currently leak to /fridge-freezer-repairs-london",
  },
  {
    href: "/commercial-freezer-repair-london",
    anchor: "commercial freezer repair london",
    count: 1,
    note: "Clicks currently go to /commercial-freezer-repair-north-london",
  },
];

function countExact(html, href, anchor) {
  const re = new RegExp(
    `<a[^>]*href=["']${href.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}[/]?["'][^>]*>\\s*${anchor.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\s*</a>`,
    "gi"
  );
  return (html.match(re) || []).length;
}

function insertFooterLink(html, href, anchor) {
  const needle = '<h3>Services</h3>';
  const block = `<h3>Services</h3>\n          <p>\n            <a href="${href}">${anchor}</a><br>`;
  if (!html.includes(needle)) return html;
  if (countExact(html, href, anchor) > 0) return html;
  return html.replace(needle, block);
}

function main() {
  for (const file of HOMES) {
    if (!existsSync(file)) {
      console.log("skip missing", file);
      continue;
    }
    let html = readFileSync(file, "utf8");
    let changed = false;
    for (const link of LINKS) {
      let n = countExact(html, link.href, link.anchor);
      while (n < link.count) {
        const before = html;
        html = insertFooterLink(html, link.href, link.anchor);
        if (html === before) break;
        changed = true;
        n = countExact(html, link.href, link.anchor);
      }
      console.log(`${file}: ${n}/${link.count} "${link.anchor}" -> ${link.href}`);
    }
    if (changed) {
      writeFileSync(file, html, "utf8");
      console.log("updated", file);
    }
  }
}

main();
