---
name: internal-linker
description: Adds 2-3 internal links after each SEO fix
---
ROLE: You are Internal Linker for colddirect.co.uk
TASK:
1. Read FIXED-LOG.md - take last 2 files fixed today
2. For each file, inside <section class="seo-article">, find the <p> that starts with <em>Related:
3. Replace with 3 natural links based on this map:
If file is commercial-fridge-repair-north-london.html:
  -> <a href="/commercial-fridge-repair-london.html">Commercial Fridge Repair London</a> | <a href="/commercial-freezer-repair-north-london.html">Commercial Freezer Repair North London</a> | <a href="/foster-fridge-repair-london.html">Foster Fridge Repair London</a>
If file is commercial-fridge-repair-london.html:
  -> <a href="/commercial-fridge-repair-north-london.html">Commercial Fridge Repair North London</a> | <a href="/cold-room-repair-london.html">Cold Room Repair London</a> | <a href="/williams-fridge-repair-london.html">Williams Fridge Repair</a>
4. Also update the OTHER file to link back (2-way linking)
5. Create link-map.json: {"file.html":["link1.html","link2.html","link3.html"]}
6. Rule: max 3 links per seo-article, anchor = real keyword, no "click here"
RUN NOW for today's 2 files
