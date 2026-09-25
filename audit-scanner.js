const fs = require('fs');
const path = require('path');

// Skip these files
const skipFiles = new Set([
  'index.html',
  'agent-status.html',
  'coverage.html',
  'sitemap.xml'
]);

// Files starting with these prefixes are skipped
const skipPrefixes = ['preview-', '_backup_'];

// Priority order for sorting
const priorityOrder = {
  'commercial-fridge-repair': 1,
  'commercial-freezer-repair': 2,
  'freezer-room-repair': 3,
  'cold-room-repair': 4
};

function getPriority(filename) {
  for (const [pattern, priority] of Object.entries(priorityOrder)) {
    if (filename.includes(pattern)) return priority;
  }
  return 5; // Everything else
}

function stripHtml(html) {
  return html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}

function countWords(text) {
  return text.split(/\s+/).filter(w => w.length > 0).length;
}

function extractBody(html) {
  const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  return bodyMatch ? bodyMatch[1] : '';
}

function hasSeoArticle(html) {
  return /<section\s+class=["']seo-article["']/.test(html);
}

function getSeoArticleContent(html) {
  const match = html.match(/<section\s+class=["']seo-article["'][^>]*>([\s\S]*?)<\/section>/i);
  return match ? match[1] : '';
}

function getImageAlt(html) {
  const match = html.match(/<img[^>]+alt=["']([^"']*)/i);
  return match ? match[1] : '';
}

function imageAltMatchesKeyword(filename, altText) {
  // Extract brand/product keyword from filename
  // e.g., "williams-fridge-repair-london.html" -> keyword is "williams"
  const basename = path.basename(filename, '.html');
  const parts = basename.split('-');
  
  if (parts.length === 0) return false;
  
  // The first word is typically the brand/keyword
  const keyword = parts[0];
  
  return altText.toLowerCase().includes(keyword.toLowerCase());
}

function scanFiles() {
  const projectDir = 'C:/Users/khora/Documents/colddirect-website';
  const files = fs.readdirSync(projectDir).filter(f => {
    if (!f.endsWith('.html')) return false;
    if (skipFiles.has(f)) return false;
    if (skipPrefixes.some(prefix => f.startsWith(prefix))) return false;
    return true;
  });

  const results = [];

  for (const filename of files) {
    const filepath = path.join(projectDir, filename);
    const html = fs.readFileSync(filepath, 'utf8');

    const body = extractBody(html);
    const bodyText = stripHtml(body);
    const words = countWords(bodyText);

    const hasSeo = hasSeoArticle(html);
    const seoContent = getSeoArticleContent(html);
    const altText = getImageAlt(seoContent);
    const imageOk = hasSeo && altText.length > 0 && imageAltMatchesKeyword(filename, altText);

    const isWeak = words < 400 || !hasSeo;

    results.push({
      file: filename,
      words,
      hasSeo,
      imageOk,
      priority: getPriority(filename),
      status: isWeak ? 'WEAK' : 'OK'
    });
  }

  // Sort by priority, then alphabetically
  results.sort((a, b) => {
    if (a.priority !== b.priority) return a.priority - b.priority;
    return a.file.localeCompare(b.file);
  });

  return results;
}

const results = scanFiles();
const weakPages = results.filter(r => r.status === 'WEAK');

// Write weak-list.json
const weakListOutput = weakPages.map(r => ({
  file: r.file,
  words: r.words,
  hasSeo: r.hasSeo,
  imageOk: r.imageOk,
  status: r.status
}));

fs.writeFileSync('C:/Users/khora/Documents/colddirect-website/weak-list.json', JSON.stringify(weakListOutput, null, 2));

// Write AUDIT-REPORT.md
let reportMarkdown = '# Cold Direct SEO Audit Report\n\n';
reportMarkdown += '| File | Words | Has SEO | Image OK | Priority |\n';
reportMarkdown += '|------|-------|---------|----------|----------|\n';

for (const r of results) {
  const priorityLabel = {
    1: 'Commercial Fridge',
    2: 'Commercial Freezer',
    3: 'Freezer Room',
    4: 'Cold Room',
    5: 'Other'
  }[r.priority];

  reportMarkdown += `| ${r.file} | ${r.words} | ${r.hasSeo ? '✓' : '✗'} | ${r.imageOk ? '✓' : '✗'} | ${priorityLabel} |\n`;
}

reportMarkdown += '\n## Summary\n\n';
reportMarkdown += `- **Total pages scanned:** ${results.length}\n`;
reportMarkdown += `- **Weak pages found:** ${weakPages.length}\n`;
reportMarkdown += `- **Pages with <400 words:** ${results.filter(r => r.words < 400).length}\n`;
reportMarkdown += `- **Pages without SEO section:** ${results.filter(r => !r.hasSeo).length}\n`;

fs.writeFileSync('C:/Users/khora/Documents/colddirect-website/AUDIT-REPORT.md', reportMarkdown);

// Console output for summary
console.log(`✓ Audit complete. ${weakPages.length} weak pages found.`);
console.log(`\nTop priorities (weak pages):`);
weakPages.slice(0, 10).forEach(p => {
  console.log(`  - ${p.file} (${p.words} words, SEO: ${p.hasSeo ? 'yes' : 'no'})`);
});
