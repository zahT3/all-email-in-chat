"""Fictional, in-memory MCP mailbox. No sockets, providers, secrets, or SMTP.

Every tool result is marked demo. Drafts exist only for this process lifetime.
Run with ``python -m email_in_chat.demo`` for an offline teaching backend.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from mcp.server.fastmcp import FastMCP

DEMO_ACCOUNTS = {
    "demo-work": "team@example.test",
    "demo-personal": "reader@example.test",
}
_MESSAGES = {
    "demo-work": [
        {
            "email_id": "101",
            "subject": "Design review on Thursday",
            "sender": "maya@example.test",
            "recipients": ["team@example.test"],
            "date": "2026-09-27T09:00:00Z",
            "body": "Fictional demo: please review the two mockups before Thursday. No actual meeting exists.",
            "seen": False,
            "mailbox": "INBOX",
            "attachments": [],
        },
        {
            "email_id": "102",
            "subject": "Example invoice for discussion",
            "sender": "billing@example.test",
            "recipients": ["team@example.test"],
            "date": "2026-09-26T08:00:00Z",
            "body": "Fictional demo invoice: 120 demo units. This is not a payment request.",
            "seen": True,
            "mailbox": "INBOX",
            "attachments": [],
        },
    ],
    "demo-personal": [
        {
            "email_id": "201",
            "subject": "Book club reading notes",
            "sender": "bookclub@example.test",
            "recipients": ["reader@example.test"],
            "date": "2026-09-25T07:00:00Z",
            "body": "Fictional demo: bring one question about the first chapter.",
            "seen": False,
            "mailbox": "INBOX",
            "attachments": [],
        },
    ],
}


def create_server() -> FastMCP:
    server = FastMCP(
        "email-in-chat-demo",
        instructions="All accounts and emails are fictional offline demo data.",
    )
    messages = deepcopy(_MESSAGES)

    def account(name: str) -> list[dict[str, Any]]:
        if name not in messages:
            raise ValueError("Unknown fictional demo account.")
        return messages[name]

    @server.tool()
    async def list_available_accounts() -> dict[str, Any]:
        """List two fictional accounts; no real account or credential is read."""
        return {
            "demo": True,
            "result": [
                {
                    "account_name": name,
                    "account_type": "email",
                    "description": "Fictional offline demo",
                    "email_address": address,
                    "can_receive": True,
                    "can_send": False,
                }
                for name, address in DEMO_ACCOUNTS.items()
            ],
        }

    @server.tool()
    async def list_mailboxes(account_name: str) -> dict[str, Any]:
        """List fictional folders including a server-declared Drafts folder."""
        account(account_name)
        return {
            "demo": True,
            "account_name": account_name,
            "result": [
                {"name": "INBOX", "delimiter": "/", "flags": []},
                {"name": "Drafts", "delimiter": "/", "flags": [r"\Drafts"]},
                {"name": "Archive", "delimiter": "/", "flags": [r"\Archive"]},
            ],
        }

    @server.tool()
    async def list_emails_metadata(
        account_name: str,
        page: int = 1,
        page_size: int = 20,
        subject: str | None = None,
        from_address: str | None = None,
        text: str | None = None,
        seen: bool | None = None,
        mailbox: str = "INBOX",
    ) -> dict[str, Any]:
        """Search fictional mail by subject, sender, text, unread status, or folder."""
        if page < 1 or not 1 <= page_size <= 100:
            raise ValueError("Invalid demo page size.")
        selected = [message for message in account(account_name) if message["mailbox"] == mailbox]
        if subject:
            selected = [m for m in selected if subject.casefold() in m["subject"].casefold()]
        if from_address:
            selected = [m for m in selected if from_address.casefold() in m["sender"].casefold()]
        if text:
            selected = [
                m for m in selected if text.casefold() in (m["subject"] + m["body"]).casefold()
            ]
        if seen is not None:
            selected = [m for m in selected if m["seen"] == seen]
        start = (page - 1) * page_size
        return {
            "demo": True,
            "account_name": account_name,
            "page": page,
            "page_size": page_size,
            "total": len(selected),
            "emails": [
                {key: value for key, value in message.items() if key != "body"}
                for message in selected[start : start + page_size]
            ],
        }

    @server.tool()
    async def get_emails_content(
        account_name: str,
        email_ids: list[str],
        mailbox: str = "INBOX",
        mark_as_read: bool = False,
        body_offset: int = 0,
        max_body_length: int = 20000,
    ) -> dict[str, Any]:
        """Read fictional mail; mark_as_read can only affect this in-memory demo."""
        if body_offset < 0 or not 1 <= max_body_length <= 100000 or len(email_ids) > 100:
            raise ValueError("Invalid demo content request.")
        selected = [
            m
            for m in account(account_name)
            if m["mailbox"] == mailbox and m["email_id"] in email_ids
        ]
        if mark_as_read:
            for message in selected:
                message["seen"] = True
        return {
            "demo": True,
            "account_name": account_name,
            "mark_as_read_applied": mark_as_read,
            "emails": [
                dict(m, body=m["body"][body_offset : body_offset + max_body_length])
                for m in selected
            ],
            "requested_count": len(email_ids),
            "retrieved_count": len(selected),
            "failed_ids": [
                uid for uid in email_ids if not any(m["email_id"] == uid for m in selected)
            ],
        }

    @server.tool()
    async def save_to_mailbox(
        account_name: str,
        recipients: list[str],
        subject: str,
        body: str,
        mailbox: str = "Drafts",
        flags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Save a fictional draft in memory; it is never sent or persisted."""
        existing = account(account_name)
        if mailbox != "Drafts":
            raise ValueError("Demo drafts may only be saved in Drafts.")
        uid = str(1000 + len(existing))
        existing.append(
            {
                "email_id": uid,
                "subject": subject,
                "body": body,
                "sender": DEMO_ACCOUNTS[account_name],
                "recipients": recipients,
                "date": "2026-09-28T00:00:00Z",
                "mailbox": mailbox,
                "seen": False,
                "attachments": [],
                "flags": flags or [r"\Draft"],
            }
        )
        return {
            "demo": True,
            "account_name": account_name,
            "email_id": uid,
            "mailbox": mailbox,
            "flags": flags or [r"\Draft"],
            "status": "demo_draft_only",
            "sent": False,
            "persistent": False,
        }

    return server


if __name__ == "__main__":
    create_server().run(transport="stdio")
