import json
import os
import unittest
from unittest.mock import patch

import cloud_email_triage as triage


class FakeAPI:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def execute(self, tool_slug, arguments, account):
        self.calls.append((tool_slug, arguments, account))
        if not self.responses:
            raise AssertionError(f"Unexpected tool call: {tool_slug}")
        expected_slug, response = self.responses.pop(0)
        if tool_slug != expected_slug:
            raise AssertionError(f"Expected {expected_slug}, got {tool_slug}")
        return response


class CloudEmailTests(unittest.TestCase):
    def test_execute_unwraps_mcp_tool_response(self):
        api = triage.Composio.__new__(triage.Composio)
        payload = {
            "content": [{
                "type": "text",
                "text": json.dumps({
                    "successful": True,
                    "data": {"results": [{"response": {"successful": True, "data": {"emailAddress": "colddirect22@gmail.com"}}}]},
                    "error": None,
                }),
            }],
            "isError": False,
        }
        api.rpc = lambda method, params: payload
        result = api.execute("GMAIL_GET_PROFILE", {"user_id": "me"}, "gmail_wayang-etamin")
        self.assertEqual(result["emailAddress"], "colddirect22@gmail.com")

    def test_parse_body_accepts_sse_event_prefix(self):
        raw = b'event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{"ok":true}}\n\n'
        self.assertEqual(triage.Composio.parse_body(raw)["result"], {"ok": True})

    def test_gmail_creates_unsent_html_draft_through_active_mcp_connection(self):
        api = FakeAPI([
            ("GMAIL_FETCH_EMAILS", {"messages": [{
                "messageId": "m1", "threadId": "t1", "sender": "Nicole <nicole@example.co.uk>",
                "subject": "Walk-in freezer repair", "labelIds": [],
                "preview": {"body": "Please help in London SW6 5HP."},
            }]}),
            ("GMAIL_BATCH_MODIFY_MESSAGES", {"success": True}),
            ("GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", {
                "threadId": "t1", "messageText": "Please help in London SW6 5HP.",
                "payload": {"headers": [{"name": "From", "value": "Nicole <nicole@example.co.uk>"}]},
            }),
            ("GMAIL_CREATE_EMAIL_DRAFT", {"id": "draft1"}),
            ("GMAIL_FETCH_EMAILS", {"messages": []}),
            ("GMAIL_FETCH_EMAILS", {"messages": []}),
        ])
        stats = triage.process_gmail("colddirect22@gmail.com", "gmail_wayang-etamin", api, set())
        self.assertEqual(stats["drafts"], 1)
        draft_call = next(call for call in api.calls if call[0] == "GMAIL_CREATE_EMAIL_DRAFT")
        self.assertTrue(draft_call[1]["is_html"])
        self.assertIn("Call out charge with Diagnose", draft_call[1]["body"])
        self.assertEqual(draft_call[1]["recipient_email"], "nicole@example.co.uk")

    def test_outlook_creates_and_updates_unsent_html_reply_draft(self):
        api = FakeAPI([
            ("OUTLOOK_LIST_MESSAGES", {"messages": [{
                "id": "m1", "subject": "Walk-in fridge repair", "bodyPreview": "Please help in London N9 0DX.",
                "from": {"emailAddress": {"name": "Nicole", "address": "nicole@example.co.uk"}},
                "replyTo": [], "flag": {"flagStatus": "notFlagged"},
            }]}),
            ("OUTLOOK_UPDATE_EMAIL", {"id": "m1"}),
            ("OUTLOOK_CREATE_DRAFT_REPLY", {"id": "draft1"}),
            ("OUTLOOK_UPDATE_EMAIL", {"id": "draft1"}),
            ("OUTLOOK_LIST_MESSAGES", {"messages": []}),
            ("OUTLOOK_LIST_MESSAGES", {"messages": []}),
        ])
        stats = triage.process_outlook("coldcom@hotmail.co.uk", "outlook_test", api, set())
        self.assertEqual(stats["drafts"], 1)
        update_call = api.calls[3]
        self.assertEqual(update_call[0], "OUTLOOK_UPDATE_EMAIL")
        self.assertEqual(update_call[1]["body"]["contentType"], "HTML")
        self.assertIn("Call out charge with Diagnose", update_call[1]["body"]["content"])

    def test_personal_outlook_draft_uses_plain_text(self):
        api = FakeAPI([
            ("OUTLOOK_LIST_MESSAGES", {"messages": [{
                "id": "p1", "subject": "Family visit", "bodyPreview": "Hi Ali, could you confirm the date?",
                "from": {"emailAddress": {"name": "Sarah", "address": "sarah@example.com"}},
                "replyTo": [], "flag": {"flagStatus": "notFlagged"},
            }]}),
            ("OUTLOOK_UPDATE_EMAIL", {"id": "p1"}),
            ("OUTLOOK_CREATE_DRAFT_REPLY", {"id": "personal-draft"}),
            ("OUTLOOK_UPDATE_EMAIL", {"id": "personal-draft"}),
            ("OUTLOOK_LIST_MESSAGES", {"messages": []}),
            ("OUTLOOK_LIST_MESSAGES", {"messages": []}),
        ])
        stats = triage.process_outlook("samsamry@hotmail.com", "outlook_test", api, set())
        self.assertEqual(stats["personal_drafts"], 1)
        update_call = api.calls[3]
        self.assertEqual(update_call[1]["body"]["contentType"], "Text")
        self.assertIn("Ali Khorani", update_call[1]["body"]["content"])
        self.assertNotIn("ColdDirect", update_call[1]["body"]["content"])

    def test_personal_reply_is_plain_text_without_business_identity(self):
        decision = triage.classify(
            "Sarah <sarah@example.com>", "Dinner on Friday",
            "Hi Ali, could you confirm whether you are available?",
            account="khoranialihossein@gmail.com",
        )
        self.assertTrue(decision["needs_reply"])
        self.assertEqual(decision["reply_kind"], "personal")
        body = triage.render_personal_draft(decision["customer_name"], "Dinner on Friday")
        self.assertIn("Ali Khorani", body)
        self.assertNotIn("<html", body.lower())
        for forbidden in ("ColdDirect", "Head Engineer", "Felixstowe", "07983 759320", "0203 952 4822"):
            self.assertNotIn(forbidden.lower(), body.lower())

    def test_refrigeration_inquiry_on_personal_account_remains_business(self):
        decision = triage.classify(
            "Nicole <nicole@example.co.uk>", "Walk-in fridge repair",
            "Please help in London SW6 5HP.", account="khoranialihossein@gmail.com",
        )
        self.assertEqual(decision["reply_kind"], "business")

    def test_non_customer_mail_on_business_account_is_not_personal_reply(self):
        decision = triage.classify(
            "Supplier <person@example.com>", "Account documents",
            "Could you confirm receipt?", account="info@colddirect.co.uk",
        )
        self.assertFalse(decision["needs_reply"])
        self.assertEqual(decision["reply_kind"], "")

    def test_personal_gmail_draft_uses_plain_text(self):
        api = FakeAPI([
            ("GMAIL_FETCH_EMAILS", {"messages": [{
                "messageId": "p1", "threadId": "pt1", "sender": "Sarah <sarah@example.com>",
                "subject": "Dinner on Friday", "labelIds": [],
                "preview": {"body": "Hi Ali, could you confirm whether you are available?"},
            }]}),
            ("GMAIL_BATCH_MODIFY_MESSAGES", {"success": True}),
            ("GMAIL_FETCH_MESSAGE_BY_MESSAGE_ID", {
                "threadId": "pt1", "messageText": "Hi Ali, could you confirm whether you are available?",
                "payload": {"headers": [{"name": "From", "value": "Sarah <sarah@example.com>"}]},
            }),
            ("GMAIL_CREATE_EMAIL_DRAFT", {"id": "personal-draft"}),
            ("GMAIL_FETCH_EMAILS", {"messages": []}),
            ("GMAIL_FETCH_EMAILS", {"messages": []}),
        ])
        stats = triage.process_gmail("khoranialihossein@gmail.com", "gmail_personal", api, set())
        self.assertEqual(stats["drafts"], 1)
        self.assertEqual(stats["personal_drafts"], 1)
        draft_call = next(call for call in api.calls if call[0] == "GMAIL_CREATE_EMAIL_DRAFT")
        self.assertFalse(draft_call[1]["is_html"])
        self.assertIn("Ali Khorani", draft_call[1]["body"])
        self.assertNotIn("ColdDirect", draft_call[1]["body"])
        self.assertEqual(stats["draft_notifications"][0]["body"], draft_call[1]["body"])

    def test_unavailable_outlook_connection_is_skipped_without_failing(self):
        class UnavailableAPI:
            def execute(self, tool_slug, arguments, account):
                raise RuntimeError("No active connection found for toolkit outlook")

        stats = triage.process_outlook_if_available("coldcom@hotmail.co.uk", "outlook_test", UnavailableAPI(), set())
        self.assertTrue(stats["skipped"])
        self.assertEqual(stats["errors"], [])

    def test_missing_imap_folder_returns_false_instead_of_raising(self):
        class MissingFolderClient:
            def select(self, folder, readonly=True):
                raise triage.imaplib.IMAP4.error("BAD unable to open folder index")

        self.assertFalse(triage.imap_exists(MissingFolderClient(), "Trash"))

    def test_config_requires_mcp_url(self):
        with patch.dict(os.environ, {
            "COMPOSIO_GMAIL_ACCOUNTS_JSON": json.dumps({email: email for email in triage.EXPECTED_GMAIL}),
            "COMPOSIO_OUTLOOK_ACCOUNTS_JSON": json.dumps({email: email for email in triage.EXPECTED_OUTLOOK}),
            "COMPOSIO_API_KEY": "test",
            "COLDDIRECT_IMAP_HOST": "mail.example.com",
            "COLDDIRECT_IMAP_USER": "info@colddirect.co.uk",
            "COLDDIRECT_IMAP_PASSWORD": "test",
            "COMPOSIO_MCP_URL": "",
        }, clear=True):
            with self.assertRaisesRegex(RuntimeError, "COMPOSIO_MCP_URL"):
                triage.validate_config(strict=True)


if __name__ == "__main__":
    unittest.main()
