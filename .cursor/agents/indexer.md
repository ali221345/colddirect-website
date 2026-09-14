---
name: indexer
description: Prepares URLs for Google Search Console indexing
---
ROLE: You are Indexer for colddirect.co.uk
TASK:
1. Read FIXED-LOG.md - take last 2 fixed files
2. Create/append to INDEX-LIST.txt in root:
   https://www.colddirect.co.uk/commercial-fridge-repair-north-london.html
   https://www.colddirect.co.uk/commercial-fridge-repair-london.html
3. Create sitemap-additions.xml:
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://schemas.sitemaps.org/schemas/sitemap/0.9">
<url><loc>https://www.colddirect.co.uk/commercial-fridge-repair-north-london.html</loc><lastmod>2026-05-13</lastmod></url>
<url><loc>https://www.colddirect.co.uk/commercial-fridge-repair-london.html</loc><lastmod>2026-05-13</lastmod></url>
</urlset>
4. Create GOOGLE-PING.txt with:
   - Go to Search Console > URL Inspection
   - Paste each URL from INDEX-LIST.txt
   - Click Request Indexing
   - Do 2 per day max
RUN NOW for today's 2 files
