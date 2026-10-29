#!/usr/bin/env python3
"""ColdDirect cloud-only email triage. Standard library only; no local files or GUI required."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import email
import email.utils
import html
import imaplib
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage
from pathlib import Path

COLDDIRECT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ColdDirect Test Email</title>
</head>
<body style="margin:0; padding:24px; background:#eef5fa; font-family:Arial,Helvetica,sans-serif; color:#1d2b3a;">
<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" width="100%" style="max-width:680px; background:#ffffff; border-collapse:separate; border-spacing:0; border:1px solid #cfdeeb; border-radius:10px; overflow:hidden; box-shadow:0 4px 16px rgba(8,45,74,0.10);">
  <tr>
    <td align="center" style="background:#082f53; background:linear-gradient(135deg,#082f53 0%,#0b527f 100%); padding:24px 28px 20px 28px;">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin:0 auto 16px auto; background:#ffffff; border-radius:7px;">
        <tr><td style="padding:9px 18px;"><img src="https://www.colddirect.co.uk/images/logo/colddirect-main.jpg" width="248" height="54" alt="ColdDirect London" style="display:block; width:248px; max-width:100%; height:auto; border:0;"></td></tr>
      </table>
      <div style="font-size:23px; line-height:30px; font-weight:700; letter-spacing:1.2px; color:#ffffff;">COLDDIRECT</div>
      <div style="font-size:12px; line-height:19px; font-weight:700; letter-spacing:1px; color:#bfeaff; text-transform:uppercase;">Commercial Refrigeration &amp; HVAC Specialists</div>
    </td>
  </tr>
  <tr>
    <td align="center" style="background:#dff3ff; border-bottom:1px solid #bddff2; padding:11px 18px; font-size:12px; line-height:19px; color:#164c70;">
      27 Felixstowe Road, London N9 0DX &nbsp;|&nbsp; Tel: 0203 952 4822 &nbsp;|&nbsp; Mobile: 07983 759320<br>
      <a href="https://www.colddirect.co.uk" style="color:#006b9d; text-decoration:none; font-weight:700;">www.colddirect.co.uk</a>
    </td>
  </tr>
  <tr>
    <td style="padding:30px 34px 26px 34px; font-size:15px; line-height:24px; color:#243746;">
      <p style="margin:0 0 18px 0;">Dear [Customer Name],</p>
      <p style="margin:0 0 18px 0;">Thank you for contacting <strong style="color:#083e66;">ColdDirect</strong>. We have received your email and we are glad to do your job regarding your <strong>[Equipment Type]</strong>.</p>
      <p style="margin:0 0 18px 0;">To ensure we assign the right engineer and get more details about your <strong>[Equipment Type]</strong>, please contact our <strong>Head Engineer</strong> directly on our mobile or landline number below for further inquiry and to book your visit:</p>
      <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f2f9fd; border-left:4px solid #1494cf; border-radius:4px;">
        <tr>
          <td style="padding:16px 20px; font-size:15px; line-height:27px; color:#102f47;">&#128241; <strong>Head Engineer Mobile:</strong> <a href="tel:07983759320" style="color:#006b9d; text-decoration:none; font-weight:700;">07983 759320</a><br>
          &#9742;&#65039; <strong>Office Landline:</strong> <a href="tel:02039524822" style="color:#006b9d; text-decoration:none; font-weight:700;">0203 952 4822</a></td>
        </tr>
      </table>
      <p style="margin:20px 0 18px 0;">Please note that appointments are not automatically booked via email&mdash;a quick phone consultation is required first. <em>(Our standard engineer attendance includes a <strong>Call out charge with Diagnose</strong>).</em></p>
      <p style="margin:0 0 18px 0;">We look forward to speaking with you.</p>
      <p style="margin:0;">Best regards,</p>
    </td>
  </tr>
  <tr>
    <td style="background:#082f53; padding:22px 28px; color:#ffffff;">
      <div style="font-size:17px; line-height:24px; font-weight:700; color:#ffffff; padding-bottom:5px;">ColdDirect Engineering Team</div>
      <div style="font-size:12px; line-height:20px; color:#bfeaff; padding-bottom:13px;">Commercial Refrigeration &bull; Cold Rooms &bull; Ice Machines &bull; Air Conditioning</div>
      <div style="font-size:12px; line-height:21px; color:#ffffff;">&#128205; 27 Felixstowe Road, London N9 0DX<br>
      &#128222; Landline: 0203 952 4822 &nbsp;|&nbsp; &#128241; Mobile: 07983 759320<br>
      &#9993;&#65039; <a href="mailto:info@colddirect.co.uk" style="color:#bfeaff; text-decoration:none;">info@colddirect.co.uk</a> &nbsp;|&nbsp; &#127760; <a href="https://www.colddirect.co.uk" style="color:#bfeaff; text-decoration:none;">www.colddirect.co.uk</a></div>
    </td>
  </tr>
</table>
</body>
</html>"""

EXPECTED_GMAIL = {
    "colddirect22@gmail.com", "alikhorani6@gmail.com", "colddirect.api.uk@gmail.com",
    "khoranialihossein@gmail.com", "alihosseinkhorani@gmail.com",
}
EXPECTED_OUTLOOK = {"coldcom@hotmail.co.uk", "samsamry@hotmail.com"}
STATE_PATH = Path(os.environ.get("CLOUD_EMAIL_STATE_FILE", ".cloud-email-state/state.json"))
COMPOSIO_URL = "https://backend.composio.dev/api/v3.1/tools/execute/proxy"
NO_REPLY_RE = re.compile(r"no[-_ ]?reply|donotreply|do-not-reply|mailer-daemon|postmaster|businessprofile|updates-mail\.gumtree\.com", re.I)
EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.I)
POSTCODE_RE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b", re.I)
PHONE_RE = re.compile(r"(?:\+44\s?\d{4}\s?\d{6}|0\d{3}\s?\d{3}\s?\d{4})")
MARKETING_RE = re.compile(r"unsubscribe|newsletter|cold\s*seo|backlink|guest\s*post|marketing\s*agency|special\s*offer|promotion|social\s*media|nextdoor|daily\s*digest", re.I)
IMPORTANT_RE = re.compile(r"invoice|receipt|github|vercel|search\s*console|security|sign[- ]?in|server|domain|tax|payment|supplier", re.I)
INQUIRY_RE = re.compile(r"repair|fault|broken|not\s*working|issue|help|quote|booking|service|attend|emergency", re.I)


def env_json(name: str) -> dict[str, str]:
    raw = os.environ.get(name, "").strip() or "{}"
    value = json.loads(raw)
    if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
        raise ValueError(f"{name} must be a JSON object of email -> connected account ID")
    return value


def validate_config(strict: bool = True) -> tuple[dict[str, str], dict[str, str]]:
    gmail = env_json("COMPOSIO_GMAIL_ACCOUNTS_JSON")
    outlook = env_json("COMPOSIO_OUTLOOK_ACCOUNTS_JSON")
    if strict:
        missing = []
        if set(gmail) != EXPECTED_GMAIL:
            missing.append("COMPOSIO_GMAIL_ACCOUNTS_JSON must contain exactly the five Gmail accounts")
        if set(outlook) != EXPECTED_OUTLOOK:
            missing.append("COMPOSIO_OUTLOOK_ACCOUNTS_JSON must contain exactly the two Hotmail accounts")
        if not os.environ.get("COMPOSIO_API_KEY", "").strip():
            missing.append("COMPOSIO_API_KEY")
        if not os.environ.get("COMPOSIO_MCP_URL", "").strip():
            missing.append("COMPOSIO_MCP_URL")
        for name in ("COLDDIRECT_IMAP_HOST", "COLDDIRECT_IMAP_USER", "COLDDIRECT_IMAP_PASSWORD"):
            if not os.environ.get(name, "").strip():
                missing.append(name)
        if missing:
            raise RuntimeError("Cloud mail configuration incomplete: " + "; ".join(missing))
    return gmail, outlook


def classify(sender: str, subject: str, body: str, protected: bool = False) -> dict:
    text = f"{sender}\n{subject}\n{body[:10000]}"
    recipient = ""
    reply_to = email.utils.parseaddr(sender)[1]
    if EMAIL_RE.match(reply_to or "") and not NO_REPLY_RE.search(reply_to):
        recipient = reply_to
    equipment = ""
    equipment_patterns = [
        (r"walk[- ]?in\s*freezer", "Walk-in Freezer"),
        (r"walk[- ]?in\s*fridge", "Walk-in Fridge"),
        (r"fridge[- ]?freezer|samsung\s+fridge", "Fridge-Freezer"),
        (r"ice\s*machine|ice[- ]?maker", "Ice Machine"),
        (r"air\s*condition|\bAC\b|HVAC", "Air Conditioning"),
        (r"cold\s*room", "Cold Room"),
        (r"freezer", "Commercial Freezer"),
        (r"fridge|refrigeration", "Commercial Fridge"),
    ]
    for pattern, label in equipment_patterns:
        if re.search(pattern, text, re.I):
            equipment = label
            break
    postcode_match = POSTCODE_RE.search(text)
    phone_match = PHONE_RE.search(text)
    london = bool(postcode_match or re.search(r"\blondon\b", text, re.I))
    needs_reply = bool(
        not protected and recipient and equipment and london and INQUIRY_RE.search(text)
        and not NO_REPLY_RE.search(sender) and not MARKETING_RE.search(text)
    )
    important = bool(protected or needs_reply or IMPORTANT_RE.search(text))
    cleanup = bool(not important and MARKETING_RE.search(text))
    name = email.utils.parseaddr(sender)[0].strip() or "Customer"
    return {
        "recipient": recipient, "customer_name": name[:120], "equipment_type": equipment,
        "postcode": postcode_match.group(0) if postcode_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "needs_reply": needs_reply, "important": important, "cleanup": cleanup,
    }


def render_draft(customer_name: str, equipment_type: str) -> str:
    return COLDDIRECT_HTML.replace("[Customer Name]", html.escape(customer_name)).replace("[Equipment Type]", html.escape(equipment_type))


def reply_subject(subject: str) -> str:
    subject = subject.strip() or "ColdDirect customer inquiry"
    return subject if re.match(r"^re\s*:", subject, re.I) else "Re: " + subject


class Composio:
    def __init__(self) -> None:
        self.key = os.environ.get("COMPOSIO_API_KEY", "").strip()
        self.url = os.environ.get("COMPOSIO_MCP_URL", "").strip()
        self.session = None
        self.next_id = 1
        self.rpc("initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "colddirect-cloud", "version": "1.0"},
        })
        self.notify("notifications/initialized", {})

    def headers(self) -> dict:
        result = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "x-consumer-api-key": self.key,
        }
        if self.session:
            result["Mcp-Session-Id"] = self.session
        return result

    @staticmethod
    def parse_body(raw: bytes):
        text = raw.decode("utf-8", errors="replace").strip()
        if not text:
            return None
        if "data:" in text:
            events = [json.loads(line[5:].strip()) for line in text.splitlines() if line.startswith("data:") and line[5:].strip() not in {"", "[DONE]"}]
            return events[-1] if events else None
        return json.loads(text)

    def rpc(self, method: str, params: dict):
        request_id = self.next_id
        self.next_id += 1
        body = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        req = urllib.request.Request(self.url, data=json.dumps(body).encode("utf-8"), headers=self.headers(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                session = response.headers.get("Mcp-Session-Id")
                if session:
                    self.session = session
                result = self.parse_body(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Composio MCP HTTP {exc.code}: {detail}") from exc
        if result and result.get("error"):
            raise RuntimeError(str(result["error"])[:500])
        return result.get("result") if result else None

    def notify(self, method: str, params: dict) -> None:
        body = {"jsonrpc": "2.0", "method": method, "params": params}
        req = urllib.request.Request(self.url, data=json.dumps(body).encode("utf-8"), headers=self.headers(), method="POST")
        with urllib.request.urlopen(req, timeout=45) as response:
            response.read()

    def execute(self, tool_slug: str, arguments: dict, account: str) -> dict:
        result = self.rpc("tools/call", {
            "name": "COMPOSIO_MULTI_EXECUTE_TOOL",
            "arguments": {
                "tools": [{"tool_slug": tool_slug, "arguments": arguments, "account": account}],
                "sync_response_to_workbench": False,
                "current_step": "CLOUD_EMAIL_TRIAGE",
                "session_id": "cloud",
            },
        }) or {}
        if result.get("isError"):
            raise RuntimeError(str(result.get("content") or "Composio tool error")[:500])
        text = next((part.get("text") for part in result.get("content") or [] if part.get("type") == "text"), "")
        payload = json.loads(text or "{}")
        if payload.get("error") or not payload.get("successful", False):
            raise RuntimeError(str(payload.get("error") or payload)[:500])
        results = (payload.get("data") or {}).get("results") or []
        response = (results[0] or {}).get("response") or {}
        if not response.get("successful", False):
            raise RuntimeError(str(response.get("error") or response)[:500])
        data = response.get("data")
        return data if isinstance(data, dict) else {}


def gmail_text(payload: dict) -> str:
    chunks: list[str] = []
    def walk(part: dict) -> None:
        if part.get("mimeType") == "text/plain" and (part.get("body") or {}).get("data"):
            raw = part["body"]["data"] + "=" * (-len(part["body"]["data"]) % 4)
            chunks.append(base64.urlsafe_b64decode(raw).decode("utf-8", errors="replace"))
        for child in part.get("parts") or []:
            walk(child)
    walk(payload)
    return "\n".join(chunks)


def process_gmail(account: str, ca: str, api: Composio, drafted: set[str]) -> dict:
    stats = {"account": account, "cleanup": 0, "starred": 0, "drafts": 0, "purged": {}, "errors": []}
    messages = []
    token = ""
    while True:
        arguments = {
            "user_id": "me", "query": "is:unread in:inbox newer_than:7d",
            "max_results": 100, "include_payload": False, "verbose": False,
        }
        if token:
            arguments["page_token"] = token
        listing = api.execute("GMAIL_FETCH_EMAILS", arguments, ca)
        messages.extend(listing.get("messages") or [])
        token = listing.get("nextPageToken") or ""
        if not token:
            break
    for item in messages:
        mid = item.get("messageId") or item.get("id")
        if not mid:
            continue
        preview = item.get("preview") or {}
        sender = item.get("sender") or preview.get("sender") or ""
        subject = item.get("subject") or preview.get("subject") or ""
        labels = item.get("labelIds") or []
        decision = classify(sender, subject, preview.get("body") or "", "STARRED" in labels or "IMPORTANT" in labels)
        source_id = f"gmail:{account}:{mid}"
        if decision["cleanup"]:
            api.execute("GMAIL_BATCH_MODIFY_MESSAGES", {
                "userId": "me", "messageIds": [mid],
                "addLabelIds": ["TRASH"], "removeLabelIds": ["INBOX", "UNREAD"],
            }, ca)
            stats["cleanup"] += 1
            continue
        if decision["important"]:
            api.execute("GMAIL_BATCH_MODIFY_MESSAGES", {"userId": "me", "messageIds": [mid], "addLabelIds": ["STARRED"]}, ca)
            stats["starred"] += 1
        if decision["needs_reply"] and source_id not in drafted:
            message = api.execute("GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", {"message_id": mid, "user_id": "me", "format": "full"}, ca)
            headers = {str(h.get("name", "")).lower(): str(h.get("value", "")) for h in (message.get("payload") or {}).get("headers") or []}
            sender = headers.get("reply-to") or headers.get("from") or message.get("sender") or sender
            decision = classify(sender, subject, message.get("messageText") or preview.get("body") or "", "STARRED" in labels or "IMPORTANT" in labels)
            if not decision["needs_reply"]:
                continue
            result = api.execute("GMAIL_CREATE_EMAIL_DRAFT", {
                "user_id": "me", "recipient_email": decision["recipient"],
                "subject": reply_subject(subject), "thread_id": message.get("threadId") or item.get("threadId"),
                "body": render_draft(decision["customer_name"], decision["equipment_type"]),
                "is_html": True, "include_signature": False,
            }, ca)
            draft_id = result.get("id") or (result.get("draft") or {}).get("id")
            if not draft_id:
                raise RuntimeError(f"Gmail draft returned no ID for {account}")
            drafted.add(source_id)
            stats["drafts"] += 1
    for label in ("TRASH", "SPAM"):
        deleted = 0
        for _ in range(20):
            listing = api.execute("GMAIL_FETCH_EMAILS", {
                "user_id": "me", "label_ids": [label], "include_spam_trash": True,
                "ids_only": True, "verbose": False, "max_results": 500,
            }, ca)
            ids = [m.get("messageId") or m.get("id") for m in listing.get("messages") or []]
            ids = [mid for mid in ids if mid]
            if not ids:
                break
            api.execute("GMAIL_BATCH_DELETE_MESSAGES", {"userId": "me", "messageIds": ids}, ca)
            deleted += len(ids)
        stats["purged"][label] = {"deleted": deleted, "empty_verified": not ids}
    return stats


def process_outlook(account: str, ca: str, api: Composio, drafted: set[str]) -> dict:
    stats = {"account": account, "cleanup": 0, "starred": 0, "drafts": 0, "purged": {}, "errors": []}
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    messages = []
    token = ""
    while True:
        arguments = {
            "user_id": "me", "folder": "inbox", "top": 100,
            "filter": f"isRead eq false and receivedDateTime ge {since}",
            "select": ["id", "subject", "from", "replyTo", "receivedDateTime", "bodyPreview", "flag", "internetMessageId"],
        }
        if token:
            arguments["page_token"] = token
        listing = api.execute("OUTLOOK_LIST_MESSAGES", arguments, ca)
        messages.extend(listing.get("messages") or listing.get("value") or [])
        token = listing.get("next_page_token") or listing.get("nextPageToken") or ""
        if not token:
            break
    for message in messages:
        mid = message.get("id")
        if not mid:
            continue
        sender_info = (message.get("from") or {}).get("emailAddress") or {}
        sender = f"{sender_info.get('name', '')} <{sender_info.get('address', '')}>"
        reply_to = message.get("replyTo") or []
        if reply_to and (reply_to[0].get("emailAddress") or {}).get("address"):
            rt = reply_to[0]["emailAddress"]
            sender = f"{rt.get('name', '')} <{rt.get('address', '')}>"
        decision = classify(sender, message.get("subject") or "", message.get("bodyPreview") or "", (message.get("flag") or {}).get("flagStatus") == "flagged")
        source_id = f"outlook:{account}:{mid}"
        if decision["cleanup"]:
            api.execute("OUTLOOK_MOVE_MESSAGE", {"user_id": "me", "message_id": mid, "destination_id": "deleteditems"}, ca)
            stats["cleanup"] += 1
            continue
        if decision["important"]:
            api.execute("OUTLOOK_UPDATE_EMAIL", {"user_id": "me", "message_id": mid, "flag": {"flagStatus": "flagged"}}, ca)
            stats["starred"] += 1
        if decision["needs_reply"] and source_id not in drafted:
            draft = api.execute("OUTLOOK_CREATE_DRAFT_REPLY", {"user_id": "me", "message_id": mid}, ca)
            draft_id = draft.get("id") or (draft.get("message") or {}).get("id")
            if not draft_id:
                raise RuntimeError(f"Outlook createReply returned no draft ID for {account}")
            api.execute("OUTLOOK_UPDATE_EMAIL", {
                "user_id": "me", "message_id": draft_id,
                "body": {"contentType": "HTML", "content": render_draft(decision["customer_name"], decision["equipment_type"])},
            }, ca)
            drafted.add(source_id)
            stats["drafts"] += 1
    for folder in ("deleteditems", "junkemail"):
        deleted = 0
        for _ in range(20):
            listing = api.execute("OUTLOOK_LIST_MESSAGES", {"user_id": "me", "folder": folder, "top": 100, "select": ["id"]}, ca)
            ids = [m.get("id") for m in listing.get("messages") or listing.get("value") or [] if m.get("id")]
            if not ids:
                break
            for mid in ids:
                api.execute("OUTLOOK_PERMANENT_DELETE_MESSAGE", {"user_id": "me", "message_id": mid, "mail_folder_id": folder}, ca)
                deleted += 1
        stats["purged"][folder] = {"deleted": deleted, "empty_verified": not ids}
    return stats


def process_outlook_if_available(account: str, ca: str, api: Composio, drafted: set[str]) -> dict:
    try:
        api.execute("OUTLOOK_GET_PROFILE", {"user_id": "me", "select": ["mail", "userPrincipalName"]}, ca)
    except RuntimeError as exc:
        if "No active connection" in str(exc) or "not connected" in str(exc).lower():
            return {
                "account": account, "cleanup": 0, "starred": 0, "drafts": 0,
                "purged": {}, "errors": [], "skipped": True,
                "note": "Outlook connection is not active; left to the Kimi scheduled task.",
            }
        raise
    return process_outlook(account, ca, api, drafted)


def imap_folder(name: str) -> str:
    return '"' + name.replace('\\', '\\\\').replace('"', '\\"') + '"'


def imap_exists(client: imaplib.IMAP4_SSL, folder: str) -> bool:
    try:
        status, _ = client.select(imap_folder(folder), readonly=True)
        return status == "OK"
    except imaplib.IMAP4.error:
        return False


def process_corporate(drafted: set[str]) -> dict:
    account = os.environ.get("COLDDIRECT_IMAP_USER", "info@colddirect.co.uk")
    stats = {"account": account, "cleanup": 0, "starred": 0, "drafts": 0, "purged": {}, "errors": []}
    host = os.environ["COLDDIRECT_IMAP_HOST"]
    port = int(os.environ.get("COLDDIRECT_IMAP_PORT", "993"))
    client = imaplib.IMAP4_SSL(host, port, ssl_context=ssl.create_default_context(), timeout=45)
    try:
        client.login(os.environ["COLDDIRECT_IMAP_USER"], os.environ["COLDDIRECT_IMAP_PASSWORD"])
        trash_candidates = [x.strip() for x in os.environ.get("COLDDIRECT_TRASH_FOLDERS", "Deleted Items,Trash").split(",") if x.strip()]
        trash = next((x for x in trash_candidates if imap_exists(client, x)), trash_candidates[0])
        drafts_folder = os.environ.get("COLDDIRECT_DRAFTS_FOLDER", "Drafts")
        client.select("INBOX")
        since = (dt.datetime.now() - dt.timedelta(days=7)).strftime("%d-%b-%Y")
        status, data = client.uid("search", None, "UNSEEN", "SINCE", since)
        if status != "OK":
            raise RuntimeError("IMAP INBOX UID search failed")
        for num in data[0].split():
            status, fetched = client.uid("fetch", num, "(FLAGS RFC822)")
            if status != "OK" or not fetched or not isinstance(fetched[0], tuple):
                continue
            flags = fetched[0][0].decode("ascii", errors="ignore") if isinstance(fetched[0][0], bytes) else str(fetched[0][0])
            message = email.message_from_bytes(fetched[0][1])
            sender = message.get("Reply-To") or message.get("From") or ""
            subject = str(message.get("Subject") or "")
            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="replace")[:10000]
            else:
                body = message.get_payload(decode=True).decode(message.get_content_charset() or "utf-8", errors="replace")[:10000]
            decision = classify(sender, subject, body, "\\Flagged" in flags)
            source_id = f"imap:{account}:uid:{num.decode()}"
            if decision["cleanup"]:
                status, _ = client.uid("copy", num, imap_folder(trash))
                if status == "OK":
                    client.uid("store", num, "+FLAGS.SILENT", "(\\Deleted)")
                    stats["cleanup"] += 1
                continue
            if decision["important"]:
                client.uid("store", num, "+FLAGS.SILENT", "(\\Flagged)")
                stats["starred"] += 1
            if decision["needs_reply"] and source_id not in drafted:
                mime = EmailMessage()
                mime["To"] = decision["recipient"]
                mime["Subject"] = reply_subject(subject)
                mime["X-ColdDirect-Source-ID"] = source_id
                if message.get("Message-ID"):
                    mime["In-Reply-To"] = message["Message-ID"]
                    mime["References"] = message["Message-ID"]
                mime.set_content("Please contact the ColdDirect Head Engineer on 07983 759320 or 0203 952 4822.")
                mime.add_alternative(render_draft(decision["customer_name"], decision["equipment_type"]), subtype="html")
                status, _ = client.append(imap_folder(drafts_folder), "(\\Draft \\Seen)", None, mime.as_bytes())
                if status != "OK":
                    raise RuntimeError("IMAP draft append failed")
                drafted.add(source_id)
                stats["drafts"] += 1
        client.expunge()
        junk_candidates = [x.strip() for x in os.environ.get("COLDDIRECT_JUNK_FOLDERS", "Junk E-mail,Spam").split(",") if x.strip()]
        for folder in dict.fromkeys(trash_candidates + junk_candidates):
            if not imap_exists(client, folder):
                stats["purged"][folder] = {"deleted": 0, "empty_verified": False, "note": "folder not present"}
                continue
            client.select(imap_folder(folder))
            status, data = client.search(None, "ALL")
            ids = data[0].split() if status == "OK" else []
            if ids:
                client.store(ids[0] + b":" + ids[-1] if len(ids) > 1 else ids[0], "+FLAGS.SILENT", "(\\Deleted)")
                client.expunge()
            status, data = client.search(None, "ALL")
            stats["purged"][folder] = {"deleted": len(ids), "empty_verified": status == "OK" and not data[0].split()}
    finally:
        try:
            client.logout()
        except Exception:
            pass
    return stats


def load_state() -> set[str]:
    try:
        return set(json.loads(STATE_PATH.read_text(encoding="utf-8")).get("drafted_source_ids") or [])
    except Exception:
        return set()


def save_state(drafted: set[str]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps({"drafted_source_ids": sorted(drafted)}, ensure_ascii=False), encoding="utf-8")


def notify(summary: str) -> None:
    topic = os.environ.get("NTFY_TOPIC", "").strip() or "colddirect-seo-khora-8492"
    try:
        req = urllib.request.Request(
            "https://ntfy.sh/" + topic, data=summary.encode("utf-8"), method="POST",
            headers={"Title": "ColdDirect Cloud Email", "Priority": "default", "Tags": "e-mail,white_check_mark"},
        )
        with urllib.request.urlopen(req, timeout=20):
            pass
    except Exception as exc:
        print(f"ntfy notification warning: {exc}")
    webhook = os.environ.get("WHATSAPP_WEBHOOK_URL", "").strip()
    if webhook:
        try:
            req = urllib.request.Request(webhook, data=json.dumps({"text": summary}).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=20):
                pass
        except Exception as exc:
            print(f"WhatsApp webhook warning: {exc}")


def self_test() -> None:
    assert "07983 759320" in COLDDIRECT_HTML and "0203 952 4822" in COLDDIRECT_HTML
    assert "Call out charge with Diagnose" in COLDDIRECT_HTML
    assert "+15°C" not in COLDDIRECT_HTML and "-15°C" not in COLDDIRECT_HTML
    customer = classify("Nicole <nicole@example.co.uk>", "Walk-in freezer repair", "Please help, unit in London SW6 5HP. Call 07983 759320.")
    assert customer["needs_reply"] and customer["equipment_type"] == "Walk-in Freezer"
    assert classify("SEO <sales@example.com>", "Backlinks and newsletter", "Unsubscribe from this promotion")["cleanup"]
    assert not classify("Vercel <no-reply@vercel.com>", "Deployment", "Build completed")["needs_reply"]
    rendered = render_draft(customer["customer_name"], customer["equipment_type"])
    assert "Dear Nicole," in rendered and "Walk-in Freezer" in rendered and "Call out charge with Diagnose" in rendered
    print("Self-test passed: embedded template, conservative classification, and draft rendering are valid.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    strict = os.environ.get("EMAIL_TRIAGE_STRICT", "true").lower() != "false"
    gmail, outlook = validate_config(strict=strict)
    if args.validate_config:
        print("Cloud configuration is complete for all eight accounts.")
        return 0
    self_test()
    drafted = load_state()
    api = Composio()
    reports = []
    for account, ca in gmail.items():
        try:
            reports.append(process_gmail(account, ca, api, drafted))
            save_state(drafted)
        except Exception as exc:
            reports.append({"account": account, "errors": [str(exc)[:500]]})
    for account, ca in outlook.items():
        try:
            reports.append(process_outlook_if_available(account, ca, api, drafted))
            save_state(drafted)
        except Exception as exc:
            reports.append({"account": account, "errors": [str(exc)[:500]]})
    if os.environ.get("COLDDIRECT_IMAP_HOST", "").strip():
        try:
            reports.append(process_corporate(drafted))
            save_state(drafted)
        except Exception as exc:
            reports.append({"account": os.environ.get("COLDDIRECT_IMAP_USER", "info@colddirect.co.uk"), "errors": [str(exc)[:500]]})
    save_state(drafted)
    totals = {
        "cleanup": sum(r.get("cleanup", 0) for r in reports),
        "starred": sum(r.get("starred", 0) for r in reports),
        "drafts": sum(r.get("drafts", 0) for r in reports),
        "skipped": sum(bool(r.get("skipped")) for r in reports),
        "errors": sum(bool(r.get("errors")) for r in reports),
    }
    summary = f"🔔 گزارش ابری ایمیل ColdDirect\n🗑️ انتقال به Trash: {totals['cleanup']} | ⭐ مهم: {totals['starred']}\n✅ پیش‌نویس ارسال‌نشده: {totals['drafts']} | ⏭️ رد شده: {totals['skipped']} | ⚠️ حساب با خطا: {totals['errors']}\nهیچ پاسخ مشتری بدون تأیید ارسال نشده است."
    print(json.dumps({"generatedAt": dt.datetime.now(dt.timezone.utc).isoformat(), "totals": totals, "accounts": reports}, ensure_ascii=False, indent=2))
    notify(summary)
    return 1 if totals["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
