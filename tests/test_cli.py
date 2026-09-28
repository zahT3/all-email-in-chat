import json
import os
import subprocess
import sys
import tomllib

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from email_in_chat.config import init_config


def cli(config, *args):
    result = subprocess.run(
        [sys.executable, "-m", "email_in_chat", "--json", "--config", str(config), *args],
        cwd=config.parent,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result, json.loads(result.stdout)


def test_doctor_missing_is_useful_and_no_secret_lookup(tmp_path):
    result, value = cli(tmp_path / "absent.toml", "doctor")
    assert result.returncode == 0
    assert value["data"]["credential_lookup"] == "not_performed"
    assert value["data"]["config_exists"] is False


def test_demo_full_cli_read_path(tmp_path):
    config = tmp_path / "demo.toml"
    result, initialized = cli(config, "init", "--demo")
    assert result.returncode == 0 and initialized["ok"]
    result, report = cli(config, "doctor", "--smoke")
    assert result.returncode == 0 and report["data"]["mcp"]["ok"]
    assert report["data"]["mcp"]["provider_connection_verified"] is False
    result, found = cli(config, "messages", "search", "--account", "work", "--unread")
    assert result.returncode == 0
    assert found["data"]["structuredContent"]["emails"][0]["email_id"] == "101"
    result, read = cli(config, "messages", "read", "--account", "work", "--id", "101")
    assert result.returncode == 0
    assert read["data"]["structuredContent"]["mark_as_read_applied"] is False


def test_raw_call_cannot_bypass_read_only(tmp_path):
    config = tmp_path / "demo.toml"
    init_config(config, demo=True)
    result, value = cli(config, "tool-call", "send_email", "--arguments", "{}")
    assert result.returncode == 1
    assert value["data"]["structuredContent"]["error"] == "tool_not_allowed"


def test_auth_requires_terminal_and_does_not_accept_password_argument(tmp_path):
    config = tmp_path / "demo.toml"
    init_config(config, demo=True)
    result, value = cli(config, "accounts", "auth", "work")
    assert result.returncode == 2
    assert "private interactive terminal" in value["error"]["message"]


def test_empty_real_backend_handshake(tmp_path):
    config = tmp_path / "real.toml"
    init_config(config)
    result, report = cli(config, "doctor", "--smoke")
    assert result.returncode == 0
    assert report["data"]["mcp"]["ok"]
    assert report["data"]["mcp"]["accounts"] == []
    assert "send_email" not in report["data"]["mcp"]["tools"]


def test_send_defaults_to_local_preview(tmp_path):
    request = tmp_path / "request.json"
    request.write_text(
        json.dumps(
            {
                "account_name": "work",
                "recipients": ["test@example.test"],
                "subject": "Example",
                "body": "Fictional message",
            }
        )
    )
    result, value = cli(tmp_path / "not-required.toml", "send", "--request", str(request))
    assert result.returncode == 0
    assert value["data"]["preview"] and value["data"]["sent"] is False


def test_client_install_defaults_to_preview(tmp_path):
    target = tmp_path / "cursor.json"
    config = tmp_path / "demo.toml"
    result, report = cli(config, "clients", "install", "cursor", "--target", str(target))
    assert result.returncode == 0
    assert report["data"]["applied"] is False
    assert not target.exists()


@pytest.mark.parametrize(
    "client", ["claude-code", "claude-desktop", "cursor", "kimi-code", "chatgpt-desktop", "codex"]
)
async def test_exported_config_launches_real_mcp_bridge(tmp_path, client):
    """Config -> installed command -> bridge -> fixture MCP. Not a desktop UI test."""
    config = tmp_path / "demo.toml"
    init_config(config, demo=True)
    result, generated = cli(config, "clients", "config", client)
    assert result.returncode == 0
    profile = generated["data"]
    if profile["format"] == "json":
        entry = json.loads(profile["content"])["mcpServers"]["email-in-chat"]
    else:
        entry = tomllib.loads(profile["content"])["mcp_servers"]["email-in-chat"]
    params = StdioServerParameters(command=entry["command"], args=entry["args"])
    with open(os.devnull, "w") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                assert initialized.serverInfo.name == "email-in-chat"
                tools = await session.list_tools()
                assert "get_emails_content" in {t.name for t in tools.tools}
                accounts = await session.call_tool("list_available_accounts", {})
                assert not accounts.isError
                assert accounts.structuredContent["result"][0]["account_name"] == "work"
                message = await session.call_tool(
                    "get_emails_content", {"account_name": "work", "email_ids": ["101"]}
                )
                assert not message.isError and message.structuredContent["demo"]
