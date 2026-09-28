import json
import os
import stat
from pathlib import Path

import pytest
import tomlkit

from email_in_chat.clients import (
    CLIENTS,
    SERVER_NAME,
    ClientConfigError,
    client_profiles,
    install_config,
    render_config,
)

COMMAND = "/opt/example/bin/email-in-chat"
ARGS = ["serve"]


def test_profiles_and_render_are_independent_values():
    profiles = client_profiles()
    assert {profile["client"] for profile in profiles} == set(CLIENTS)
    profiles[0]["instructions"].clear()
    assert client_profiles()[0]["instructions"]
    args = ["serve", "--config", "/a path/中文.toml"]
    rendered = render_config("cursor", COMMAND, args)
    args.clear()
    assert (
        json.loads(rendered["content"])["mcpServers"][SERVER_NAME]["args"][-1]
        == "/a path/中文.toml"
    )
    assert "desktop_e2e_not_verified" in rendered["evidence_status"]


@pytest.mark.parametrize(
    "client",
    ["claude-code", "claude-desktop", "claude-desktop-windows", "cursor", "kimi-code"],
)
def test_json_profiles_use_documented_transport_shape(client):
    result = render_config(client, COMMAND, ARGS)
    entry = json.loads(result["content"])["mcpServers"][SERVER_NAME]
    assert entry["command"] == COMMAND
    assert entry["args"] == ARGS
    if client in {"cursor", "claude-code"}:
        assert entry["type"] == "stdio"
    else:
        assert "type" not in entry


@pytest.mark.parametrize("client", ["codex", "chatgpt-desktop"])
def test_openai_profiles_share_toml_path(client):
    result = render_config(client, r"C:\Apps\email-in-chat.exe", ["serve"])
    assert result["target_path"] == "~/.codex/config.toml"
    assert (
        tomlkit.parse(result["content"])["mcp_servers"][SERVER_NAME]["command"]
        == r"C:\Apps\email-in-chat.exe"
    )


def test_web_explains_remote_route_and_refuses_local_install(tmp_path):
    result = render_config("chatgpt-web", COMMAND, ARGS)
    assert result["target_path"] is None
    assert result["format"] == "instructions"
    assert not result["content"]
    assert "Secure MCP Tunnel" in " ".join(result["instructions"])
    with pytest.raises(ClientConfigError, match="not applicable"):
        install_config("chatgpt-web", COMMAND, ARGS, tmp_path / "config", apply=True)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize(
    "client,command,args",
    [
        ("unsupported", COMMAND, ARGS),
        ("cursor", " ", ARGS),
        ("cursor", "bad\x00command", ARGS),
        ("cursor", COMMAND, "serve"),
        ("cursor", COMMAND, [1]),
    ],
)
def test_invalid_render_arguments_are_rejected(client, command, args):
    with pytest.raises(ClientConfigError):
        render_config(client, command, args)


def test_preview_does_not_create_directories(tmp_path):
    target = tmp_path / "not-created" / "mcp.json"
    result = install_config("cursor", COMMAND, ARGS, target)
    assert result["status"] == "preview"
    assert result["changed"] and not result["applied"]
    assert not target.parent.exists()


def test_json_merge_preserves_other_settings_backs_up_and_hides_secrets(tmp_path):
    target = tmp_path / "mcp.json"
    original = '{"theme":"dark","mcpServers":{"other":{"env":{"TOKEN":"secret-keep-local"}}}}\n'
    target.write_text(original)
    preview = install_config("cursor", COMMAND, ARGS, target)
    assert target.read_text() == original
    assert "secret-keep-local" not in json.dumps(preview)
    result = install_config("cursor", COMMAND, ARGS, target, apply=True)
    assert result["status"] == "installed"
    merged = json.loads(target.read_text())
    assert merged["theme"] == "dark"
    assert merged["mcpServers"]["other"]["env"]["TOKEN"] == "secret-keep-local"
    assert merged["mcpServers"][SERVER_NAME]["command"] == COMMAND
    backup = Path(result["backup_path"])
    assert backup.read_text() == original
    assert "secret-keep-local" not in json.dumps(result)
    if os.name == "posix":
        assert stat.S_IMODE(target.stat().st_mode) == 0o600
        assert stat.S_IMODE(backup.stat().st_mode) == 0o600


def test_toml_merge_preserves_comments_and_settings(tmp_path):
    target = tmp_path / "config.toml"
    original = '# Keep this comment\nmodel = "existing"  # Keep inline\n\n[mcp_servers.other]\ncommand = "other"\n# secret-local\n'
    target.write_text(original)
    result = install_config("codex", COMMAND, ARGS, target, apply=True)
    updated = target.read_text()
    assert original in updated
    document = tomlkit.parse(updated)
    assert document["model"] == "existing"
    assert document["mcp_servers"]["other"]["command"] == "other"
    assert document["mcp_servers"][SERVER_NAME]["command"] == COMMAND
    assert Path(result["backup_path"]).read_text() == original
    assert "secret-local" not in json.dumps(result)


@pytest.mark.parametrize("client,suffix", [("cursor", "json"), ("codex", "toml")])
def test_identical_install_does_not_write_or_create_backup(client, suffix, tmp_path):
    target = tmp_path / f"config.{suffix}"
    first = install_config(client, COMMAND, ARGS, target, apply=True)
    assert first["backup_path"] is None
    before = target.stat().st_mtime_ns
    result = install_config(client, COMMAND, ARGS, target, apply=True)
    assert result["status"] == "unchanged"
    assert not result["changed"] and not result["applied"]
    assert result["backup_path"] is None
    assert target.stat().st_mtime_ns == before
    assert list(tmp_path.iterdir()) == [target]


@pytest.mark.parametrize("client", ["cursor", "codex"])
def test_different_existing_entry_is_never_overwritten(client, tmp_path):
    target = tmp_path / "config"
    original = render_config(client, "/old/command", ARGS)["content"]
    target.write_text(original)
    with pytest.raises(ClientConfigError, match="refusing to overwrite"):
        install_config(client, COMMAND, ARGS, target, apply=True)
    assert target.read_text() == original
    assert list(tmp_path.iterdir()) == [target]


@pytest.mark.parametrize(
    "client,text",
    [
        ("cursor", ""),
        ("cursor", '{"broken": "secret-local"'),
        ("cursor", "[]"),
        ("cursor", '{"mcpServers":[]}'),
        ("cursor", '{"value": NaN}'),
        ("cursor", '{"mcpServers":{},"mcpServers":{"other":{}}}'),
        ("codex", "broken = ["),
        ("codex", 'mcp_servers = "bad"'),
    ],
)
def test_malformed_or_ambiguous_existing_file_is_preserved(client, text, tmp_path):
    target = tmp_path / "config"
    target.write_text(text)
    with pytest.raises(ClientConfigError) as raised:
        install_config(client, COMMAND, ARGS, target, apply=True)
    assert "secret-local" not in str(raised.value)
    assert target.read_text() == text
    assert list(tmp_path.iterdir()) == [target]


def test_invalid_utf8_is_preserved(tmp_path):
    target = tmp_path / "config"
    target.write_bytes(b"\xff")
    with pytest.raises(ClientConfigError, match="UTF-8"):
        install_config("cursor", COMMAND, ARGS, target, apply=True)
    assert target.read_bytes() == b"\xff"


@pytest.mark.parametrize("kind", ["file", "parent", "broken"])
def test_symlinks_are_refused(kind, tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    config = real / "mcp.json"
    config.write_text("{}")
    link = tmp_path / "link"
    if kind == "parent":
        link.symlink_to(real, target_is_directory=True)
        target = link / "mcp.json"
    else:
        link.symlink_to(config if kind == "file" else real / "missing")
        target = link
    with pytest.raises(ClientConfigError, match="Symlink"):
        install_config("cursor", COMMAND, ARGS, target, apply=True)
    assert config.read_text() == "{}"


def test_concurrent_change_is_refused(tmp_path, monkeypatch):
    from email_in_chat import clients

    target = tmp_path / "mcp.json"
    target.write_text("{}")
    real_write = clients._write_private_temp

    def write_and_change(parent, prefix, content):
        path = real_write(parent, prefix, content)
        if "pending" in prefix:
            target.write_text('{"changed_by_client":true}')
        return path

    monkeypatch.setattr(clients, "_write_private_temp", write_and_change)
    with pytest.raises(ClientConfigError, match="changed during"):
        install_config("cursor", COMMAND, ARGS, target, apply=True)
    assert json.loads(target.read_text()) == {"changed_by_client": True}
    assert not list(tmp_path.glob(".email-in-chat-pending-*"))
