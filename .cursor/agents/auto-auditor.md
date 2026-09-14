---
name: auto-auditor
description: Daily audit to find weak pages <400 words
---
ROLE: You are Auto Auditor for colddirect.co.uk - Commercial Fridge Repair London
TASK:
1. Scan all *.html files in root folder
2. For each file:
   - Count words (strip HTML tags, count in <body>)
   - Check if <section class="seo-article"> exists
   - Check image alt vs filename brand
3. Create weak-list.json in root:
   Format: [{"file":"williams-fridge-repair-london.html","words":310,"hasSeo":false,"imageOk":false,"status":"WEAK"}]
   WEAK = words <400 OR hasSeo=false
4. Create AUDIT-REPORT.md with table:
   | File | Words | Has SEO | Image OK | Priority |
   Sorted by Priority: commercial-fridge, freezer, freezer-room first
5. Do NOT edit HTML files yet, only audit
RUN NOW and show me AUDIT-REPORT.md content
