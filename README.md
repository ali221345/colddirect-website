# Cold Direct website

Static HTML for [colddirect.co.uk](https://www.colddirect.co.uk), deployed to Plesk `httpdocs`.

## Deploy to Plesk (FTP)

1. Copy `.env.example` to `.env`.
2. In Plesk: **Websites & Domains → FTP Access**. Fill:

```
PLESK_FTP_HOST=ftp.colddirect.co.uk
PLESK_FTP_USER=...
PLESK_FTP_PASS=...
PLESK_FTP_PATH=/httpdocs
```

3. Never commit `.env`. It is listed in `.gitignore`.
4. Install deps and upload the current chiller files (WebP, HTML, and `web.config` only if the remote size differs):

```
pip install -r requirements.txt
python deploy_to_plesk.py
```

On Windows, `py -m pip install -r requirements.txt` then `py deploy_to_plesk.py` if `python` is not on PATH.

The script prefers files under `colddirect-public-html/` (the live tree), then the repo root copies.

If login returns **530 User cannot log in**, copy the current username and password from Plesk **FTP Access** into `.env` and run the script again. The FTP certificate may not match `ftp.colddirect.co.uk`; the script falls back to FTPS without hostname verification.
