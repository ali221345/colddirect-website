/* Offline behavioural regression checks: no credentials, network, or repository writes. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../scripts/daily-seo-update.js'), 'utf8');
const entry = source.lastIndexOf('\nmain().catch(');
assert.ok(entry > 0, 'Expected CLI entry point');

async function scenario(prepare) {
  const root = '/offline';
  const files = new Map([
    [path.join(root, 'colddirect-public-html', 'blog', 'why-commercial-fridge-not-cold-enough.html'), '<article><p>Useful original advice.</p></article>'],
    [path.join(root, 'seo-audit', 'daily-seo-state.json'), JSON.stringify({ titleRewrites: {}, queryHistory: {}, linksAdded: {} })],
  ]);
  const originalState = files.get(path.join(root, 'seo-audit', 'daily-seo-state.json'));
  const writes = [];
  let submissions = 0, uploads = 0;
  const fakeFs = {
    existsSync: p => files.has(p), mkdirSync: () => {},
    readFileSync: p => { assert.ok(files.has(p), `Unexpected read: ${p}`); return files.get(p); },
    writeFileSync: (p, data) => { writes.push(p); files.set(p, String(data)); },
    appendFileSync: (p, data) => files.set(p, (files.get(p) || '') + data),
  };
  const context = vm.createContext({
    __dirname: root + '/scripts', console: { log() {} }, URL,
    process: { platform: 'linux', env: { COLD_SEO_PREPARE_ONLY: prepare ? '1' : '0' } },
    require: id => {
      if (id === 'fs') return fakeFs;
      if (id === 'path') return path;
      if (id === 'os') return { homedir: () => '/offline-home' };
      if (id === 'url') return require('node:url');
      if (id === 'child_process') return { spawnSync(command) {
        assert.equal(command, 'python', 'Unexpected child process / network attempt');
        uploads++;
        return { status: 1, stderr: 'Simulated FTP failure' };
      } };
      throw Error(`Unexpected dependency: ${id}`);
    },
    fixtureClient: { sitemaps: {
      submit: async () => { submissions++; },
      get: async () => ({ data: { contents: [] } }),
    } },
  });
  vm.runInContext(source.slice(0, entry) + `
    gscClient = async () => ({ client: fixtureClient, siteUrl: SITE_URL, account: { alias: 'offline-test' } });
    queryAnalytics = async (client, site, body) => body.dimensions?.length === 1 && body.dimensions[0] === 'query'
      ? [{ keys: ['fridge repair london'], position: 15, impressions: 100, clicks: 2, ctr: .02 }] : [];
    curlHead = () => '200';
    curlGet = p => ({code: p === '/sitemap.xml' ? '500' : '200', body: ''});
    globalThis.run = main;
  `, context);
  if (prepare) {
    await context.run();
    assert.equal(uploads, 0, 'Prepare mode must not call FTP');
    assert.equal(submissions, 0, 'Prepare mode must not submit sitemap');
    assert.equal(files.get(path.join(root, 'seo-audit', 'daily-seo-state.json')), originalState);
    assert.ok(!writes.includes(path.join(root, 'seo-audit', 'daily-seo-state.json')), 'Applied state must not be saved');
    const reports = [...files.entries()].filter(([p]) => /daily-report-.*\.md$/.test(p));
    assert.equal(reports.length, 1, 'Prepare mode generates a report');
    assert.match(reports[0][1], /Proposed changes \(not published\)/);
    assert.match(reports[0][1], /mid-pack link:/, 'Fixture actually proposes a content change');
    assert.match(reports[0][1], /sitemap submission skipped/);
    assert.match(files.get(path.join(root, 'colddirect-public-html', 'blog', 'why-commercial-fridge-not-cold-enough.html')), /data-daily-seo=/);
  } else {
    await assert.rejects(context.run(), /FTP publication failed/);
    assert.equal(uploads, 1, 'Publishing attempted FTP and detected failure');
    assert.equal(submissions, 1, 'Fixture exercises sitemap submission branch');
    assert.ok(!writes.includes(path.join(root, 'seo-audit', 'daily-seo-state.json')), 'Failed publication must not advance state');
    assert.ok(!writes.some(p => /daily-report-.*\.md$/.test(p)), 'Failed publication must not write a success report');
  }
}
(async () => {
  await scenario(true);
  await scenario(false);
  console.log('PASS: prepare mode produces proposals without FTP, sitemap submit, or applied state writes; failed FTP rejects publication.');
})().catch(error => { console.error(error); process.exitCode = 1; });
