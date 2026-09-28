"""Real SDK stdio tests against a fictional backend, plus policy boundaries."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

from email_in_chat.bridge import (
    _Bridge,
    _environment,
    _payload,
    invoke_tool,
    run_smoke,
)

SOURCE = Path(__file__).resolve().parents[1] / "src"
ALIASES = {"work": "demo-work", "personal": "demo-personal"}


@asynccontextmanager
async def bridge_client(mode="read"):
    script = (
        "import asyncio; from pathlib import Path; "
        "from email_in_chat.bridge import run_stdio; "
        f"asyncio.run(run_stdio(Path('unused-demo.toml'), mode={mode!r}, "
        f"aliases={ALIASES!r}, demo=True))"
    )
    env = {key: value for key, value in os.environ.items() if not key.startswith("MCP_")}
    env["PYTHONPATH"] = str(SOURCE)
    params = StdioServerParameters(command=sys.executable, args=["-c", script], env=env)
    with open(os.devnull, "w") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                initialization = await session.initialize()
                yield initialization, session


def test_stdio_handshake_aliases_and_non_mutating_read():
    async def scenario():
        async with bridge_client() as (initialization, session):
            assert initialization.serverInfo.name == "email-in-chat"
            tools = (await session.list_tools()).tools
            assert "save_to_mailbox" not in {tool.name for tool in tools}
            reader = next(tool for tool in tools if tool.name == "get_emails_content")
            assert reader.annotations.readOnlyHint is True
            accounts = _payload(await session.call_tool("list_available_accounts", {}))
            assert accounts["demo"] is True
            assert {item["account_name"] for item in accounts["result"]} == set(ALIASES)
            result = await session.call_tool(
                "get_emails_content",
                {
                    "account_name": "work",
                    "email_ids": ["101"],
                    "mark_as_read": True,
                },
            )
            assert not result.isError
            data = _payload(result)
            assert data["account_name"] == "work"
            assert data["mark_as_read_applied"] is False
            assert data["emails"][0]["seen"] is False
            unread = _payload(
                await session.call_tool(
                    "list_emails_metadata",
                    {
                        "account_name": "work",
                        "seen": False,
                    },
                )
            )
            assert "101" in {item["email_id"] for item in unread["emails"]}
            namespace_bypass = await session.call_tool(
                "list_emails_metadata", {"account_name": "demo-work"}
            )
            assert namespace_bypass.isError

    asyncio.run(scenario())


@pytest.mark.parametrize(
    "operation", ["send_email", "delete_emails", "add_email_account", "save_to_mailbox"]
)
def test_direct_stdio_call_cannot_bypass_read_policy(operation):
    async def scenario():
        async with bridge_client() as (_, session):
            # Deliberately skip tools/list: invocation must enforce the boundary.
            result = await session.call_tool(operation, {"account_name": "work"})
            assert result.isError
            assert _payload(result)["error"] == "tool_not_allowed"

    asyncio.run(scenario())


def test_draft_mode_is_constrained_and_never_sends():
    async def scenario():
        async with bridge_client("draft") as (_, session):
            names = {tool.name for tool in (await session.list_tools()).tools}
            assert "save_to_mailbox" in names
            assert "send_email" not in names
            arguments = {
                "account_name": "work",
                "recipients": ["maya@example.test"],
                "subject": "Fictional reply",
                "body": "Thanks for the mockups.",
            }
            wrong_folder = await session.call_tool(
                "save_to_mailbox", dict(arguments, mailbox="INBOX")
            )
            assert wrong_folder.isError
            draft = await session.call_tool("save_to_mailbox", arguments)
            assert not draft.isError
            data = _payload(draft)
            assert data["demo"] is True and data["sent"] is False
            assert data["flags"] == [r"\Draft"]
            deleted = await session.call_tool(
                "save_to_mailbox", dict(arguments, flags=[r"\Deleted"])
            )
            assert deleted.isError

    asyncio.run(scenario())


def test_manage_rejects_deleted_flags_before_backend_call():
    async def scenario():
        session = AsyncMock()
        bridge = _Bridge(session, "manage", None)
        bridge.catalog["set_email_flags"] = types.Tool(
            name="set_email_flags", inputSchema={"type": "object"}
        )
        result = await bridge.call("set_email_flags", {"flags": [r"\dElEtEd"]})
        assert result.isError
        session.call_tool.assert_not_awaited()

    asyncio.run(scenario())


def test_upstream_error_text_is_not_exposed_and_not_retried():
    async def scenario():
        session = AsyncMock()
        session.call_tool.return_value = types.CallToolResult(
            isError=True,
            content=[types.TextContent(type="text", text="secret-password: do-not-print")],
        )
        bridge = _Bridge(session, "read", None)
        bridge.catalog["list_mailboxes"] = types.Tool(
            name="list_mailboxes", inputSchema={"type": "object"}
        )
        result = await bridge.call("list_mailboxes", {})
        assert result.isError
        assert "secret-password" not in result.model_dump_json()
        assert session.call_tool.await_count == 1

    asyncio.run(scenario())


def test_config_environment_cannot_inject_accounts_or_transport(monkeypatch, tmp_path):
    monkeypatch.setenv("MCP_EMAIL_SERVER_PASSWORD", "not-a-real-password")
    monkeypatch.setenv("MCP_EMAIL_SERVER_CONFIG_PATH", "wrong.toml")
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("MCP_EMAIL_SERVER_CREDENTIAL_STORAGE", "plaintext")
    config = tmp_path / "private.toml"
    environment = _environment(config)
    assert "MCP_EMAIL_SERVER_PASSWORD" not in environment
    assert "MCP_TRANSPORT" not in environment
    assert environment["MCP_EMAIL_SERVER_CONFIG_PATH"] == str(config.resolve())
    assert environment["MCP_EMAIL_SERVER_CREDENTIAL_STORAGE"] == "keyring"


def test_smoke_and_single_invocation_use_real_demo_mcp(monkeypatch, tmp_path):
    monkeypatch.setenv("PYTHONPATH", str(SOURCE))

    async def scenario():
        report = await run_smoke(tmp_path / "unused.toml", aliases=ALIASES, demo=True)
        assert report["ok"] is True and report["demo"] is True
        assert report["sent_mail"] is False
        assert report["provider_connection_verified"] is False
        assert report["demo_read"]["demo"] is True
        result = await invoke_tool(
            tmp_path / "unused.toml",
            "list_available_accounts",
            {},
            aliases={"only-work": "demo-work"},
            demo=True,
        )
        data = _payload(result)
        assert [item["account_name"] for item in data["result"]] == ["only-work"]
        # Both JSON text and structured output use the user alias.
        assert "demo-personal" not in json.dumps(data)

    asyncio.run(scenario())
