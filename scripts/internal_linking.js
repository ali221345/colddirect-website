#!/usr/bin/env node
/**
 * Ensures homepage footer links for priority service pages exist in both root and colddirect-public-html.
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..");

const LINKS = [
  { href: "/freezer-repair-london/", text: "Freezer Repair London" },
  { href: "/fridge-repair-london/", text: "Fridge Repair London" },
  { href: "/commercial-freezer-repair-london/", text: "Commercial Freezer Repair London" },
  { href: "/cold-room-repair-london/", text: "Cold Room Repair" },
  { href: "/freezer-room-repair-london/", text: "Freezer Room Repair London" },
  { href: "/commercial-appliances-repair-london/", text: "Commercial Appliances Repair London" },
  { href: "/chiller-repair-london/", text: "Chiller Repair London" },
  { href: "/supermarket-fridge-repair-london/", text: "Supermarket Fridge Repair London" },
  { href: "/air-conditioning-repair-london/", text: "Air Conditioning Repair London" }
];

const TARGET_FILES = [
  path.join(ROOT, "index.html"),
  path.join(ROOT, "index.php"),
  path.join(ROOT, "colddirect-public-html", "index.html"),
  path.join(ROOT, "colddirect-public-html", "index.php")
];

const line = LINKS.map((l) => `<a href="${l.href}">${l.text}</a>`).join(" | ");
let updatedCount = 0;

for (const filePath of TARGET_FILES) {
  if (!fs.existsSync(filePath)) continue;
  const orig = fs.readFileSync(filePath, "utf8");
  let html = orig;
  const re = /<p>\s*<a href="\/freezer-repair-london\/?"[\s\S]*?<\/p>/i;
  if (re.test(html)) {
    html = html.replace(re, `<p>\n            ${line}\n          </p>`);
  }
  if (html !== orig) {
    fs.writeFileSync(filePath, html, "utf8");
    updatedCount++;
  }
}

console.log(updatedCount ? `internal_linking: updated ${updatedCount} file(s)` : "internal_linking: already present");
