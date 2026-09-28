"""Render MCP client entries and merge them without exposing existing secrets."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.exceptions import ParseError

SERVER_NAME = "email-in-chat"
EVIDENCE_STATUS = "official_docs_verified; desktop_e2e_not_verified"
_CLAUDE_DESKTOP_SOURCE = "https://modelcontextprotocol.io/docs/develop/connect-local-servers"
_OPENAI_SOURCE = "https://learn.chatgpt.com/docs/extend/mcp"
_PROFILES: dict[str, dict[str, Any]] = {
    "claude-code": {
        "target_path": "~/.claude.json",
        "format": "json",
        "source_url": "https://code.claude.com/docs/en/desktop",
        "instructions": [
            "Add the entry at user scope; Claude Code CLI and local Desktop Code sessions share it.",
            "Start a new local session and check the MCP server list.",
        ],
    },
    "claude-desktop": {
        "target_path": "~/Library/Application Support/Claude/claude_desktop_config.json",
        "format": "json",
        "source_url": _CLAUDE_DESKTOP_SOURCE,
        "instructions": [
            "This profile uses the documented macOS path. On Windows use claude-desktop-windows.",
            "Use Claude Settings > Developer > Edit Config to verify your installation's actual path.",
            "Restart Claude Desktop after saving, then check its MCP tools.",
        ],
    },
    "claude-desktop-windows": {
        "target_path": r"%APPDATA%\Claude\claude_desktop_config.json",
        "format": "json",
        "source_url": _CLAUDE_DESKTOP_SOURCE,
        "instructions": [
            "Expand %APPDATA% on Windows and verify the actual path via Settings > Developer > Edit Config.",
            "Supply an absolute Windows executable path, then restart Claude Desktop after saving.",
        ],
    },
    "cursor": {
        "target_path": "~/.cursor/mcp.json",
        "format": "json",
        "source_url": "https://cursor.com/docs/mcp",
        "instructions": [
            "This is global configuration; a project can instead use .cursor/mcp.json.",
            "Open Cursor MCP settings and verify that email-in-chat is enabled and its tools load.",
        ],
    },
    "kimi-code": {
        "target_path": "~/.kimi-code/mcp.json",
        "format": "json",
        "source_url": "https://www.kimi.com/code/docs/en/kimi-code-desktop/settings-and-extensions.html",
        "instructions": [
            "Kimi Code Desktop shares this MCP configuration with Kimi Code CLI.",
            "Start a new session after saving; already-open sessions do not pick up the change.",
            "This profile does not claim support for the ordinary Kimi chat application.",
        ],
    },
    "chatgpt-desktop": {
        "target_path": "~/.codex/config.toml",
        "format": "toml",
        "source_url": _OPENAI_SOURCE,
        "instructions": [
            "Current OpenAI documentation describes shared MCP configuration for ChatGPT desktop and Codex on the same host.",
            "In Settings > MCP servers, verify the server and restart; availability depends on your app version and policy.",
        ],
    },
    "codex": {
        "target_path": "~/.codex/config.toml",
        "format": "toml",
        "source_url": _OPENAI_SOURCE,
        "instructions": [
            "This targets the default Codex configuration; pass your actual target when using a different CODEX_HOME.",
            "Check the MCP server list in a new local Codex session.",
        ],
    },
    "chatgpt-web": {
        "target_path": None,
        "format": "instructions",
        "source_url": "https://developers.openai.com/plugins/deploy/connect-chatgpt",
        "instructions": [
            "ChatGPT web does not read local MCP configuration files or directly launch this stdio process.",
            "For developer testing, connect the local stdio server through Secure MCP Tunnel, subject to account/workspace availability.",
            "Alternatively provide an authenticated remote Streamable HTTP endpoint over HTTPS; public plugin submission requires a public HTTPS endpoint.",
            "The local installer does not deploy an HTTP service, create a tunnel, or publish a plugin.",
        ],
    },
}
CLIENTS = tuple(_PROFILES)


class ClientConfigError(ValueError):
    """A configuration cannot safely be rendered or merged."""


def client_profiles() -> list[dict[str, Any]]:
    """Return fresh profile metadata without reading the environment or disk."""
    return [
        {"client": name, **deepcopy(profile), "evidence_status": EVIDENCE_STATUS}
        for name, profile in _PROFILES.items()
    ]


def render_config(client: str, command: str, args: list[str]) -> dict[str, Any]:
    """Render only our server entry; never inspect or change client configuration."""
    if client not in _PROFILES:
        raise ClientConfigError("Unknown client; choose a value from CLIENTS.")
    if not isinstance(command, str) or not command.strip() or "\x00" in command:
        raise ClientConfigError("command must be a non-empty executable path or name.")
    if not isinstance(args, list) or any(not isinstance(arg, str) or "\x00" in arg for arg in args):
        raise ClientConfigError("args must be a list of strings without NUL characters.")
    result = {
        "client": client,
        **deepcopy(_PROFILES[client]),
        "evidence_status": EVIDENCE_STATUS,
    }
    result["instructions"].append(
        "Use the installed email-in-chat executable's absolute path; desktop apps may have a different PATH. Keep mailbox secrets out of command arguments."
    )
    if result["format"] == "instructions":
        result["content"] = ""
        return result
    entry: dict[str, Any] = {"command": command, "args": list(args)}
    if client in {"claude-code", "cursor"}:
        entry = {"type": "stdio", **entry}
    if result["format"] == "toml":
        result["content"] = tomlkit.dumps({"mcp_servers": {SERVER_NAME: entry}})
    else:
        result["content"] = (
            json.dumps({"mcpServers": {SERVER_NAME: entry}}, indent=2, ensure_ascii=False) + "\n"
        )
    return result


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ClientConfigError("Existing JSON has duplicate keys; refusing to rewrite it.")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ClientConfigError("Existing JSON has a non-standard numeric constant; no changes made.")


def _merge(existing: bytes | None, rendered: dict[str, Any]) -> tuple[bytes, bool]:
    try:
        text = existing.decode("utf-8") if existing is not None else ""
        if rendered["format"] == "json":
            document = (
                json.loads(
                    text,
                    object_pairs_hook=_json_object,
                    parse_constant=_reject_json_constant,
                )
                if existing is not None
                else {}
            )
            incoming = json.loads(rendered["content"])
            root_key = "mcpServers"
        else:
            document = tomlkit.parse(text)
            incoming = tomlkit.parse(rendered["content"])
            root_key = "mcp_servers"
    except (UnicodeDecodeError, json.JSONDecodeError, ParseError):
        raise ClientConfigError(
            "Existing configuration is not valid UTF-8 JSON/TOML; no changes made."
        ) from None
    if not isinstance(document, Mapping):
        raise ClientConfigError("Existing configuration must have an object/table at the root.")
    if root_key in document and not isinstance(document[root_key], Mapping):
        raise ClientConfigError(
            "Existing MCP servers entry must be an object/table; no changes made."
        )
    if root_key not in document:
        document[root_key] = {} if rendered["format"] == "json" else tomlkit.table()
    servers = document[root_key]
    desired = incoming[root_key][SERVER_NAME]
    if SERVER_NAME in servers:
        if servers[SERVER_NAME] != desired:
            raise ClientConfigError(
                "email-in-chat already exists with different settings; refusing to overwrite it."
            )
        return existing or b"", False
    servers[SERVER_NAME] = desired
    if rendered["format"] == "json":
        merged = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    else:
        merged = tomlkit.dumps(document)
    return merged.encode("utf-8"), True


def _check_path(target: Path) -> None:
    for path in (*reversed(target.parents), target):
        if path.is_symlink():
            raise ClientConfigError(
                "Symlink configuration paths are not supported; no changes made."
            )
        if path != target and path.exists() and not path.is_dir():
            raise ClientConfigError("A parent of the configuration path is not a directory.")
    if target.exists() and not target.is_file():
        raise ClientConfigError("Configuration target must be a regular file.")


def _read_existing(target: Path) -> bytes | None:
    _check_path(target)
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(target, flags)
    except FileNotFoundError:
        return None
    except OSError:
        raise ClientConfigError("Unable to safely read configuration; no changes made.") from None
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ClientConfigError("Configuration target must be a regular file.")
        return stream.read()


def _write_private_temp(parent: Path, prefix: str, content: bytes) -> Path:
    descriptor, name = tempfile.mkstemp(dir=parent, prefix=prefix)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    return Path(name)


def install_config(
    client: str,
    command: str,
    args: list[str],
    target: Path,
    apply: bool = False,
) -> dict[str, Any]:
    """Preview or safely add our entry; output never includes unrelated settings.

    Identical entries are idempotent. Differing entries, invalid documents, and
    symlinks are refused. An applied update keeps a private backup and atomically
    replaces the target with a private file. Preview creates no files/directories.
    """
    rendered = render_config(client, command, args)
    if rendered["format"] == "instructions":
        raise ClientConfigError(
            "ChatGPT web needs remote MCP or Secure MCP Tunnel; local configuration installation is not applicable."
        )
    target = Path(target).expanduser().absolute()
    existing = _read_existing(target)
    merged, changed = _merge(existing, rendered)
    result = {
        **rendered,
        "target_path": str(target),
        "status": "preview" if changed else "unchanged",
        "changed": changed,
        "applied": False,
        "backup_path": None,
    }
    if not apply or not changed:
        return result
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _check_path(target)
    if _read_existing(target) != existing:
        raise ClientConfigError(
            "Configuration changed during installation; retry after reviewing it."
        )
    if existing is not None:
        backup = _write_private_temp(
            target.parent, target.name + ".email-in-chat-backup-", existing
        )
        result["backup_path"] = str(backup)
    pending = _write_private_temp(target.parent, ".email-in-chat-pending-", merged)
    try:
        if _read_existing(target) != existing:
            raise ClientConfigError(
                "Configuration changed during installation; retry after reviewing it."
            )
        os.replace(pending, target)
    finally:
        # Only remove a temporary file created by this function, never user data.
        pending.unlink(missing_ok=True)
    result.update(status="installed", applied=True)
    return result
