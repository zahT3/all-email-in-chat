"""Local UI trust boundary, recovery, and real MCP demo integration."""

import json
import time
from pathlib import Path

import pytest
from mcp import types
from starlette.testclient import TestClient

from email_in_chat import ui
from email_in_chat.config import ConfigError, add_account, init_config, load_config


@pytest.fixture
def setup(tmp_path):
    path = tmp_path.resolve() / "private" / "accounts.toml"
    server = ui.LocalUI(path, "/installed/bin/email-in-chat", "http://127.0.0.1:4567")
    with TestClient(server.app, base_url=server.origin) as client:
        yield server, client


def login(server, client):
    response = client.post(
        server.prefix + "/api/session",
        json={"token": server.bootstrap},
        headers={"origin": server.origin},
    )
    assert response.status_code == 200
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=strict" in response.headers["set-cookie"]
    client.headers.update({"origin": server.origin, "x-eic-csrf": response.json()["csrf"]})
    return lambda action, body: client.post(server.prefix + "/api/" + action, json=body)


def test_auth_bootstrap_and_headers(setup):
    server, client = setup
    assert client.get(server.prefix + "/api/state").status_code == 401
    assert (
        client.post(server.prefix + "/api/session", json={"token": server.bootstrap}).status_code
        == 403
    )
    assert (
        client.post(
            server.prefix + "/api/session",
            json={"token": "wrong"},
            headers={"origin": server.origin},
        ).status_code
        == 401
    )
    post = login(server, client)
    assert post("session", {"token": server.bootstrap}).status_code == 401
    response = client.get(server.prefix + "/api/state")
    assert response.status_code == 200
    assert response.json()["initialized"] is False
    assert response.headers["cache-control"] == "no-store"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert response.headers["referrer-policy"] == "no-referrer"
    assert not server.path.exists()


@pytest.mark.parametrize(
    "headers",
    [
        {"host": "evil.test:4567"},
        {"origin": "https://evil.test"},
        {"origin": "null"},
        {"sec-fetch-site": "cross-site"},
    ],
)
def test_cross_site_and_rebinding_rejected(setup, headers):
    server, client = setup
    login(server, client)
    response = client.get(server.prefix + "/api/state", headers=headers)
    assert response.status_code == 403
    assert not server.path.exists()


def test_csrf_expiry_and_body_limits(setup):
    server, client = setup
    post = login(server, client)
    client.headers.pop("x-eic-csrf")
    assert post("init", {"demo": False}).status_code == 403
    client.headers["x-eic-csrf"] = server.csrf
    assert (
        client.post(
            server.prefix + "/api/init", content="no", headers={"content-type": "text/plain"}
        ).status_code
        == 400
    )
    assert post("init", {"demo": False, "oversize": "x" * ui.BODY_LIMIT}).status_code == 400
    assert post("init", []).status_code == 400
    assert not server.path.exists()
    server.expires = time.monotonic() - 1
    assert post("init", {"demo": False}).status_code == 401


def test_demo_full_flow_isolated_from_real_config(setup):
    server, client = setup
    real_path = server.path
    init_config(real_path)
    before = real_path.read_bytes()
    post = login(server, client)
    state = post("init", {"demo": True}).json()
    assert state["demo"]
    assert server.path != real_path
    assert real_path.read_bytes() == before
    result = post("check", {"name": "work"})
    assert result.status_code == 200, result.text
    assert result.json() == {
        "account": "work",
        "demo": True,
        "verified": "demo",
        "folder_count": 3,
        "smtp_tested": False,
    }
    assert post("install", {"client": "cursor"}).status_code == 400
    preview = post("preview", {"client": "cursor"}).json()
    target = Path(preview["target_path"])
    assert target.parent == server.path.parent / "demo-clients"
    assert not target.exists()
    assert post("install", {"client": "cursor", "preview_token": "wrong"}).status_code == 400
    installed = post(
        "install", {"client": "cursor", "preview_token": preview["preview_token"]}
    ).json()
    assert installed["applied"] and target.exists()
    assert json.loads(target.read_text())["mcpServers"]["email-in-chat"]["args"] == [
        "--config",
        str(server.path),
        "serve",
    ]
    assert (
        post("install", {"client": "cursor", "preview_token": preview["preview_token"]}).status_code
        == 400
    )
    assert real_path.read_bytes() == before


def test_partial_keyring_failure_recovers_without_duplicate_account(setup, monkeypatch):
    server, client = setup
    post = login(server, client)

    def failed(*args):
        raise ConfigError("SECRET-in-provider-exception")

    monkeypatch.setattr(ui, "store_credentials", failed)
    response = post(
        "account",
        {
            "name": "work",
            "email": "test@example.test",
            "provider": "aliyun-enterprise",
            "password": "PRIVATE-PASSWORD",
        },
    )
    assert response.status_code == 200
    assert response.json()["credential_saved"] is False
    assert "SECRET" not in response.text and "PRIVATE-PASSWORD" not in response.text
    assert len(load_config(server.path)["accounts"]) == 1
    assert "PRIVATE-PASSWORD" not in server.path.read_text()
    stored = []
    monkeypatch.setattr(ui, "store_credentials", lambda *args: stored.append(args))
    assert post("credentials", {"name": "work", "password": "replacement"}).json()[
        "credential_saved"
    ]
    assert stored[0][2] == "replacement"
    assert len(load_config(server.path)["accounts"]) == 1
    assert post("account", {"name": "bad", "password": "x", "unexpected": True}).status_code == 400


@pytest.mark.asyncio
async def test_provider_check_forces_read_and_omits_mail_content(tmp_path, monkeypatch):
    path = tmp_path.resolve() / "private" / "accounts.toml"
    init_config(path)
    add_account(path, name="work", email="a@example.test", provider="aliyun-enterprise")
    calls = []

    async def invoke(native, name, arguments, **kwargs):
        calls.append((native, name, arguments, kwargs))
        return types.CallToolResult(
            content=[], structuredContent={"result": [{"name": "PRIVATE-FOLDER"}]}
        )

    monkeypatch.setattr("email_in_chat.bridge.invoke_tool", invoke)
    result = await ui.check_connection(path, "work")
    assert result["verified"] == "imap_login_and_list"
    assert "PRIVATE-FOLDER" not in json.dumps(result)
    assert calls[0][1:3] == ("list_mailboxes", {"account_name": "work"})
    assert calls[0][3]["mode"] == "read"
    assert "outgoing" not in calls[0][0].read_text()


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [None, {"result": "error"}, {"result": [{"error": "no"}]}])
async def test_ambiguous_result_is_not_success(tmp_path, monkeypatch, payload):
    path = tmp_path.resolve() / "private" / "accounts.toml"
    init_config(path, demo=True)

    async def invoke(*args, **kwargs):
        return types.CallToolResult(content=[], structuredContent=payload)

    monkeypatch.setattr("email_in_chat.bridge.invoke_tool", invoke)
    with pytest.raises(ui.UIError, match="无法确认"):
        await ui.check_connection(path, "work")


def test_connection_failure_is_actionable_and_redacted(setup, monkeypatch):
    server, client = setup
    post = login(server, client)
    post("init", {"demo": True})

    async def invoke(*args, **kwargs):
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="secret-token")], isError=True
        )

    monkeypatch.setattr("email_in_chat.bridge.invoke_tool", invoke)
    response = post("check", {"name": "work"})
    assert response.status_code == 400
    assert "IMAP" in response.json()["error"]
    assert "secret-token" not in response.text


def test_static_assets_and_no_traversal(setup):
    server, client = setup
    response = client.get(server.prefix + "/")
    assert response.status_code == 200
    assert "<script" in response.text
    assert client.get(server.prefix + "/%2e%2e/ui.py").status_code == 404
    assert client.get(server.prefix + "/api/state").status_code == 401
    assert client.get("/api/state").status_code == 404


def test_edit_account_preserves_identity_and_validates_atomically(setup, monkeypatch):
    server, client = setup
    post = login(server, client)
    monkeypatch.setattr(ui, "store_credentials", lambda *args: None)
    body = {
        "name": "work",
        "email": "test@example.test",
        "provider": "custom",
        "imap_host": "wrong.example.test",
        "receive_only": True,
        "password": "synthetic",
    }
    assert post("account", body).json()["credential_saved"]
    original = load_config(server.path)
    preview = post("preview", {"client": "cursor"}).json()
    assert preview["preview_token"]
    changed = post(
        "account-update", {**body, "imap_host": "correct.example.test", "imap_port": 999}
    )
    assert changed.json()["credential_saved"]
    updated = load_config(server.path)
    assert updated["namespace"] == original["namespace"]
    assert len(updated["accounts"]) == 1
    assert updated["accounts"][0]["imap_host"] == "correct.example.test"
    assert updated["accounts"][0]["imap_port"] == 999
    assert not server.previews
    before = server.path.read_bytes()
    assert post("account-update", {**body, "imap_port": -1}).status_code == 400
    assert post("account-update", {**body, "name": "missing"}).status_code == 400
    assert server.path.read_bytes() == before


def test_client_conflict_and_stale_preview_recovery(setup):
    server, client = setup
    post = login(server, client)
    post("init", {"demo": True})
    preview = post("preview", {"client": "cursor"}).json()
    target = Path(preview["target_path"])
    target.parent.mkdir(parents=True)
    target.write_text('{"mcpServers":{"email-in-chat":{"command":"different"}}}')
    before = target.read_bytes()
    response = post("install", {"client": "cursor", "preview_token": preview["preview_token"]})
    assert response.status_code == 400
    assert "冲突" in response.json()["error"]
    assert str(target) in response.json()["error"]
    assert response.json()["target_path"] == str(target)
    assert response.json()["code"] == "client_conflict"
    assert "密码" not in response.json()["error"]
    assert target.read_bytes() == before
    response = post("install", {"client": "cursor", "preview_token": "stale"})
    assert "重新点击预览" in response.json()["error"]


@pytest.mark.asyncio
async def test_check_timeout_is_not_success(tmp_path, monkeypatch):
    path = tmp_path.resolve() / "private" / "accounts.toml"
    init_config(path, demo=True)

    async def invoke(*args, **kwargs):
        raise TimeoutError()

    monkeypatch.setattr("email_in_chat.bridge.invoke_tool", invoke)
    with pytest.raises(ui.UIError, match="连接超时"):
        await ui.check_connection(path, "work")


def test_catalog_distinguishes_presets_and_oauth_requirement(setup):
    server, client = setup
    login(server, client)
    catalog = client.get(server.prefix + "/api/state").json()["providers"]
    assert catalog["qq"]["domains"] == ["qq.com"]
    assert catalog["icloud"]["smtp_port"] == 587
    assert catalog["gmail"]["auth"] == "google_app_password"
    assert catalog["outlook"]["available"] is False
    assert catalog["outlook"]["auth"] == "oauth_required"
    assert catalog["aliyun-enterprise"]["domains"] == []
    assert all(p["name"]["en"] and p["name"]["zh"] for p in catalog.values())


def test_errors_have_localizable_safe_codes(setup, monkeypatch):
    server, client = setup
    assert client.get(server.prefix + "/api/state").json()["code"] == "session_required"
    post = login(server, client)
    assert post("account", {"password": "SECRET"}).json()["code"] == "validation_failed"

    async def failed(*args):
        raise ui.UIError("固定文案", "connection_failed")

    monkeypatch.setattr(ui, "check_connection", failed)
    assert post("check", {"name": "work"}).json()["code"] == "connection_failed"
    server.expires = time.monotonic() - 1
    assert post("check", {"name": "work"}).json()["code"] == "session_expired"
