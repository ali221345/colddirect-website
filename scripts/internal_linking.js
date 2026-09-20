/**
 * ColdDirect internal linking map for overnight SEO 2026-09-20.
 * Trailing-slash IIS URLs only. No .html in live anchors.
 */
const links = [
  {
    from: "/",
    to: "/fridge-repair-london/",
    anchor: "fridge repair london",
    reason: "GSC LEAK: fridge repair london clicks were landing on homepage (daily 2026-09-19: 10 clicks, pos 13.9, 33% CTR)",
  },
  {
    from: "/",
    to: "/supermarket-fridge-repair-london/",
    anchor: "supermarket fridge repair london",
    reason: "GSC NOINDEX TRAP: live /supermarket-fridge-repair-london/ had robots noindex,nofollow",
  },
  {
    from: "/",
    to: "/commercial-dishwasher-repair-london/",
    anchor: "commercial dishwasher repair london",
    reason: "Thin service page now expanded; exact-match homepage support",
  },
  {
    from: "/supermarket-fridge-repair-london/",
    to: "/multideck-fridge-repair-london/",
    anchor: "multideck fridge repair London",
    reason: "Related aisle case",
  },
  {
    from: "/supermarket-fridge-repair-london/",
    to: "/supermarket-freezer-repair-london/",
    anchor: "supermarket freezer repair London",
    reason: "Related shop-floor frozen cases",
  },
  {
    from: "/supermarket-fridge-repair-london/",
    to: "/commercial-dishwasher-repair-london/",
    anchor: "Commercial Dishwasher Repair London",
    reason: "Day pair two-way",
  },
  {
    from: "/commercial-dishwasher-repair-london/",
    to: "/catering-repair-london/",
    anchor: "catering repair London",
    reason: "Related trade kitchen plant",
  },
  {
    from: "/commercial-dishwasher-repair-london/",
    to: "/commercial-fridge-repair-london/",
    anchor: "commercial fridge repair London",
    reason: "Same-call kitchen refrigeration",
  },
  {
    from: "/commercial-dishwasher-repair-london/",
    to: "/supermarket-fridge-repair-london/",
    anchor: "Supermarket Fridge Repair London",
    reason: "Day pair two-way",
  },
];

function trailingSlashOk(href) {
  return href === "/" || (href.startsWith("/") && href.endsWith("/") && !href.includes(".html"));
}

if (require.main === module) {
  const bad = links.filter((l) => !trailingSlashOk(l.to) || (l.from !== "/" && !trailingSlashOk(l.from)));
  console.log("internal_linking.js 2026-09-20");
  console.log("links", links.length);
  links.forEach((l) => console.log(`${l.from} --${l.anchor}--> ${l.to} | ${l.reason}`));
  if (bad.length) {
    console.error("FAIL non-trailing-slash", bad);
    process.exit(1);
  }
  console.log("GSC Live Test: pending deploy — repo anchors use trailing slash");
}

module.exports = { links, trailingSlashOk };
