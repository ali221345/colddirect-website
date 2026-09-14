# ColdDirect live deploy

**Date deployed:** 10 September 2026 (Europe/London)

## Files deployed

Uploaded to Plesk `httpdocs` on `ftp.colddirect.co.uk`:

| Local file | Live path |
|---|---|
| `cold-agent-v3.asp` | `/httpdocs/cold-agent-v3.asp` |
| `commercial-freezer-repair-tottenham.asp` | `/httpdocs/commercial-freezer-repair-tottenham.asp` |
| `sitemap.xml` | `/httpdocs/sitemap.xml` |

Agent ping was updated to return `READY v3`. A first upload of the agent returned HTTP 500 (broken VBScript string in `replace_branding`); a fixed copy was re-uploaded.

Backup zip (manual Plesk upload if needed): `DEPLOY_PACKAGE.zip`

## Live test results

| Check | Result |
|---|---|
| `GET https://www.colddirect.co.uk/cold-agent-v3.asp?k=CD2026-SECURE&a=ping` | **200** body `READY v3` |
| `GET https://colddirect.co.uk/cold-agent-v3.asp?k=CD2026-SECURE&a=ping` | **200** body `READY v3` |
| `GET …/cold-agent-v3.asp?k=CD2026-SECURE&a=stats` | **200** `{"total_files":122,"commercial_pages":12,"last_modified":"2026-09-10"}` |
| `GET https://www.colddirect.co.uk/commercial-freezer-repair-tottenham.asp` | **200** title and copy show **ColdDirect**, phone **07983 759320** |
| `GET https://www.colddirect.co.uk/sitemap.xml` | **200** (14933 bytes), contains Tottenham URL |

Wrong key still returns `forbidden`.

## Next step

1. Import `n8n-workflow.json` into [n8n.cloud](https://n8n.cloud).
2. Set environment / credentials:
   - `GEMINI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `WHATSAPP_WEBHOOK_URL`
3. Confirm the Create Page node posts to  
   `https://colddirect.co.uk/cold-agent-v3.asp?a=create&f={{filename}}&k=CD2026-SECURE`  
   with form field `html`.
4. Keep `agent-data.json` and `templates/page-template.asp` with the n8n host (they are not required in `httpdocs` for ping/create).

## Notes

- No `.env` in the repo; FTP used the existing Plesk account for this domain.
- Do not commit FTP passwords.
- Sitemap live URL: `https://colddirect.co.uk/commercial-freezer-repair-tottenham.asp`.
