#!/usr/bin/env node
/**
 * Validate LD+JSON on static HTML (no bundler build for this site).
 * - Parses every application/ld+json block
 * - Flags duplicate org nodes (same @type + @id or same @type + name + url) per page
 * - Fails if template phrase remains
 */
const fs = require("fs");
const path = require("path");

const ROOTS = ["colddirect-public-html", "."];
const EXTS = new Set([".html", ".php", ".tsx", ".asp"]);
const TEMPLATE = "in London from Cold Direct";
const ORG_TYPES = new Set([
  "LocalBusiness",
  "ApplianceRepair",
  "HVACBusiness",
  "Store",
  "Organization",
  "HomeAndConstructionBusiness",
  "ProfessionalService",
]);

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ent.name === "node_modules" || ent.name === ".git" || ent.name === "templates") continue;
    const p = path.join(dir, ent.name);
    if (ent.isDirectory()) walk(p, out);
    else if (EXTS.has(path.extname(ent.name).toLowerCase())) out.push(p);
  }
  return out;
}

function collectTopLevelOrgNodes(data) {
  const roots = [];
  if (Array.isArray(data)) roots.push(...data);
  else if (data && typeof data === "object") {
    if (Array.isArray(data["@graph"])) roots.push(...data["@graph"]);
    else roots.push(data);
  }
  return roots.filter((n) => {
    if (!n || typeof n !== "object") return false;
    const type = n["@type"];
    const types = Array.isArray(type) ? type : [type];
    return types.some((t) => ORG_TYPES.has(t));
  });
}

function isRichOrgDefinition(n) {
  // Nested provider stubs ({@type,@id,name}) are references, not duplicate definitions.
  return Boolean(n.telephone || n.address || n.areaServed || n.openingHoursSpecification || n.priceRange);
}

function orgKey(n) {
  const type = n["@type"];
  const types = Array.isArray(type) ? type : [type];
  const orgType = types.find((t) => ORG_TYPES.has(t));
  if (!orgType) return null;
  if (n["@id"]) return `${orgType}::id::${n["@id"]}`;
  const name = n.name || "";
  const url = n.url || "";
  return `${orgType}::${name}::${url}`;
}

const seenFiles = new Set();
const files = [];
for (const root of ROOTS) {
  for (const f of walk(root)) {
    const abs = path.resolve(f);
    if (seenFiles.has(abs)) continue;
    seenFiles.add(abs);
    files.push(f);
  }
}

let templateHits = 0;
let parseErrors = 0;
let dupOrgPages = 0;
const templateFiles = [];
const parseFail = [];
const dupPages = [];

const scriptRe = /<script[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;

for (const file of files) {
  const html = fs.readFileSync(file, "utf8");
  if (html.includes(TEMPLATE)) {
    templateHits++;
    templateFiles.push(file);
  }

  let m;
  const orgKeys = [];
  scriptRe.lastIndex = 0;
  while ((m = scriptRe.exec(html))) {
    const raw = m[1].trim();
    if (!raw) continue;
    try {
      const data = JSON.parse(raw);
      const nodes = collectTopLevelOrgNodes(data).filter(isRichOrgDefinition);
      for (const n of nodes) {
        const k = orgKey(n);
        if (k) orgKeys.push(k);
      }
      // Still require full script parse; walk nested JSON for validity only
      JSON.stringify(data);
    } catch (e) {
      parseErrors++;
      parseFail.push({ file, error: String(e.message || e) });
    }
  }

  const counts = {};
  for (const k of orgKeys) counts[k] = (counts[k] || 0) + 1;
  const dups = Object.entries(counts).filter(([, c]) => c > 1);
  if (dups.length) {
    dupOrgPages++;
    dupPages.push({ file, dups });
  }
}

const report = {
  filesScanned: files.length,
  templateHits,
  templateFiles,
  ldjsonParseErrors: parseErrors,
  parseFail,
  pagesWithDuplicateOrgNodes: dupOrgPages,
  dupPages: dupPages.slice(0, 20),
};

console.log(JSON.stringify(report, null, 2));

if (templateHits !== 0 || parseErrors !== 0 || dupOrgPages !== 0) {
  console.error("\nVALIDATION FAILED");
  process.exit(1);
}
console.log("\nVALIDATION OK: 0 templates, LD+JSON parses, no duplicate org nodes per page");
