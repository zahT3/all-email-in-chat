"""Configuration boundary tests use synthetic accounts and an in-memory keyring."""

from __future__ import annotations

import copy
import json
import os
import stat
import tomllib
from types import SimpleNamespace

import pytest
import tomli_w

from email_in_chat import config


@pytest.fixture
def account_config(tmp_path):
    path = tmp_path / "accounts.toml"
    config.init_config(path)
    config.add_account(path, name="work", email="hello@example.test", provider="privateemail")
    return path


@pytest.fixture
def fake_keyring(monkeypatch):
    import keyring

    writes = {}
    monkeypatch.setattr(keyring, "get_keyring", lambda: SimpleNamespace(priority=5))
    monkeypatch.setattr(
        keyring,
        "set_password",
        lambda service, key, value: writes.__setitem__((service, key), value),
    )
    monkeypatch.setattr(
        keyring, "get_password", lambda *_: pytest.fail("No keyring reads expected")
    )
    return writes


def write_data(path, data):
    path.write_text(tomli_w.dumps(data), encoding="utf-8")
    path.chmod(0o600)


@pytest.mark.parametrize("address", ["*@example.test", "a?@example.test", "[ab]@example.test"])
def test_recipient_patterns_cannot_expand_send_permission(account_config, address):
    before = account_config.read_bytes()
    with pytest.raises(config.ConfigError, match="without wildcards"):
        config.set_policy(account_config, mode="manage", recipients=[address])
    assert account_config.read_bytes() == before
    data = config.load_config(account_config)
    data["allowed_recipients"] = [address]
    write_data(account_config, data)
    with pytest.raises(config.ConfigError, match="without wildcards"):
        config.load_config(account_config)


def test_init_does_not_overwrite_and_new_files_are_private(tmp_path):
    path = tmp_path / "private" / "accounts.toml"
    config.init_config(path)
    before = path.read_bytes()
    with pytest.raises(config.ConfigError, match="already exists"):
        config.init_config(path, demo=True)
    assert path.read_bytes() == before
    if os.name == "posix":
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert stat.S_IMODE(path.parent.stat().st_mode) == 0o700
        assert stat.S_IMODE(path.with_suffix(".toml.lock").stat().st_mode) == 0o600


def test_two_configs_have_separate_credentials_and_no_secrets_on_disk(
    tmp_path, fake_keyring, capsys
):
    paths = [tmp_path / "first.toml", tmp_path / "second.toml"]
    keys = []
    for index, path in enumerate(paths):
        config.init_config(path)
        config.add_account(path, name="work", email="hello@example.test", provider="privateemail")
        result = config.store_credentials(path, "work", f"synthetic-secret-{index}")
        data = config.load_config(path)
        alias = config.aliases(data)["work"]
        keys.append(alias)
        assert (
            fake_keyring[(config.KEYRING_SERVICE, f"{alias}:incoming")]
            == f"synthetic-secret-{index}"
        )
        assert (
            fake_keyring[(config.KEYRING_SERVICE, f"{alias}:outgoing")]
            == f"synthetic-secret-{index}"
        )
        assert "synthetic-secret" not in json.dumps(result)
        snapshot = config.materialize_backend(path, data)
        assert "synthetic-secret" not in path.read_text() + snapshot.read_text()
    assert keys[0] != keys[1]
    assert all(key.startswith("eic-") for key in keys)
    assert capsys.readouterr() == ("", "")


def test_policy_snapshots_are_distinct_immutable_and_tls_only(account_config):
    original = config.load_config(account_config)
    paths = []
    for mode in config.MODES:
        data = copy.deepcopy(original)
        data["mode"] = mode
        data["allowed_recipients"] = ["allowed@example.test"]
        data["accounts"][0]["smtp_port"] = 587
        data["accounts"][0]["smtp_starttls"] = True
        snapshot = config.materialize_backend(account_config, data)
        before = snapshot.stat().st_mtime_ns
        assert config.materialize_backend(account_config, data) == snapshot
        assert snapshot.stat().st_mtime_ns == before
        paths.append(snapshot)
        native = tomllib.loads(snapshot.read_text())
        assert native["credential_storage"] == "keyring"
        assert native["enable_attachment_download"] is False
        incoming = native["emails"][0]["incoming"]
        assert incoming["password"] == config.SENTINEL
        assert incoming["use_ssl"] is True and incoming["verify_ssl"] is True
        if mode == "manage":
            outgoing = native["emails"][0]["outgoing"]
            assert outgoing["start_ssl"] is True and outgoing["use_ssl"] is False
            assert outgoing["verify_ssl"] is True
        else:
            assert "outgoing" not in native["emails"][0]
        if mode == "read":
            assert native["allowed_recipients"] == []
        if os.name == "posix":
            assert stat.S_IMODE(snapshot.stat().st_mode) == 0o600
    assert len(set(paths)) == 3
    assert all(path.exists() for path in paths)


def test_recipient_policy_change_creates_new_snapshot(account_config):
    config.set_policy(account_config, mode="manage", recipients=["first@example.test"])
    first = config.materialize_backend(account_config, config.load_config(account_config))
    config.set_policy(account_config, mode="manage", recipients=["second@example.test"])
    second = config.materialize_backend(account_config, config.load_config(account_config))
    assert first != second
    assert tomllib.loads(first.read_text())["allowed_recipients"] == ["first@example.test"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema_version", True),
        ("namespace", 123456789012),
        ("demo", "false"),
        ("mode", []),
        ("allowed_recipients", [123]),
        ("accounts", ["bad"]),
        ("password", "synthetic-secret"),
    ],
)
def test_malformed_root_fields_have_safe_errors(account_config, field, value):
    data = config.load_config(account_config)
    data[field] = value
    write_data(account_config, data)
    with pytest.raises(config.ConfigError) as error:
        config.load_config(account_config)
    assert "synthetic-secret" not in str(error.value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", 1),
        ("email", []),
        ("imap_host", 123),
        ("smtp_host", 123),
        ("imap_port", "993"),
        ("smtp_port", True),
        ("smtp_starttls", 1),
        ("full_name", {}),
        ("full_name", "bad\r\nheader"),
        ("provider", "unsupported"),
        ("password", "synthetic-secret"),
        ("verify_ssl", False),
    ],
)
def test_malformed_account_fields_are_rejected(account_config, field, value):
    data = config.load_config(account_config)
    data["accounts"][0][field] = value
    write_data(account_config, data)
    with pytest.raises(config.ConfigError) as error:
        config.load_config(account_config)
    assert "synthetic-secret" not in str(error.value)


@pytest.mark.parametrize(
    "extra",
    [
        {"name": 2},
        {"imap_port": "993"},
        {"smtp_port": False},
        {"full_name": 12},
        {"receive_only": "yes"},
    ],
)
def test_add_account_invalid_input_never_changes_file(tmp_path, extra):
    path = tmp_path / "accounts.toml"
    config.init_config(path)
    before = path.read_bytes()
    arguments = dict(name="work", email="hello@example.test", provider="privateemail")
    arguments.update(extra)
    with pytest.raises(config.ConfigError):
        config.add_account(path, **arguments)
    assert path.read_bytes() == before


def test_demo_cannot_contain_real_accounts(account_config):
    data = config.load_config(account_config)
    data["demo"] = True
    write_data(account_config, data)
    with pytest.raises(config.ConfigError, match="Demo"):
        config.load_config(account_config)


def test_invalid_utf8_is_safe_error(account_config):
    account_config.write_bytes(b"\xff")
    with pytest.raises(config.ConfigError, match="parse"):
        config.load_config(account_config)


def test_load_rejects_parent_symlink(account_config, tmp_path):
    link = tmp_path / "link"
    link.symlink_to(account_config.parent, target_is_directory=True)
    with pytest.raises(config.ConfigError, match="symbolic"):
        config.load_config(link / account_config.name)


def test_lock_symlink_cannot_overwrite_other_file(tmp_path):
    target = tmp_path / "preserve.txt"
    target.write_text("preserve")
    path = tmp_path / "accounts.toml"
    path.with_suffix(".toml.lock").symlink_to(target)
    with pytest.raises(config.ConfigError, match="symbolic"):
        config.init_config(path)
    assert target.read_text() == "preserve"
    assert not path.exists()


@pytest.mark.skipif(os.name != "posix", reason="POSIX modes")
def test_existing_snapshot_must_still_be_private(account_config):
    data = config.load_config(account_config)
    target = config.materialize_backend(account_config, data)
    target.chmod(0o644)
    with pytest.raises(config.ConfigError, match="owner-only"):
        config.materialize_backend(account_config, data)


def test_modified_snapshot_is_not_overwritten(account_config):
    data = config.load_config(account_config)
    target = config.materialize_backend(account_config, data)
    target.write_text("modified = true\n")
    with pytest.raises(config.ConfigError, match="modified"):
        config.materialize_backend(account_config, data)
    assert target.read_text() == "modified = true\n"


def test_keyring_errors_never_echo_backend_messages(
    account_config, fake_keyring, monkeypatch, capsys
):
    import keyring

    def fail(*_):
        raise RuntimeError("synthetic-secret-provider-error")

    monkeypatch.setattr(keyring, "get_keyring", fail)
    with pytest.raises(config.ConfigError) as error:
        config.store_credentials(account_config, "work", "synthetic-secret")
    assert "synthetic-secret" not in str(error.value)
    assert not fake_keyring
    assert capsys.readouterr() == ("", "")


def test_plaintext_keyring_is_rejected_before_write(account_config, fake_keyring, monkeypatch):
    import keyring

    backend = type("PlaintextKeyring", (), {"priority": 1})()
    monkeypatch.setattr(keyring, "get_keyring", lambda: backend)
    with pytest.raises(config.ConfigError, match="secure OS keyring"):
        config.store_credentials(account_config, "work", "synthetic-secret")
    assert not fake_keyring


def test_receive_only_auth_stores_no_smtp_credential(tmp_path, fake_keyring):
    path = tmp_path / "accounts.toml"
    config.init_config(path)
    config.add_account(
        path, name="work", email="hello@example.test", provider="privateemail", receive_only=True
    )
    config.store_credentials(path, "work", "synthetic-secret")
    assert len(fake_keyring) == 1
    assert next(iter(fake_keyring))[1].endswith(":incoming")


def test_chained_plaintext_keyring_is_rejected(account_config, fake_keyring, monkeypatch):
    import keyring

    plaintext = type("Keyring", (), {"__module__": "keyrings.alt.file", "priority": 1})()
    chained = type(
        "ChainerBackend",
        (),
        {
            "__module__": "keyring.backends.chainer",
            "priority": 10,
            "backends": [SimpleNamespace(priority=5), plaintext],
        },
    )()
    monkeypatch.setattr(keyring, "get_keyring", lambda: chained)
    with pytest.raises(config.ConfigError, match="secure OS keyring"):
        config.store_credentials(account_config, "work", "synthetic-secret")
    assert not fake_keyring


def test_hardlinked_config_is_rejected(account_config, tmp_path):
    extra = tmp_path / "extra.toml"
    os.link(account_config, extra)
    with pytest.raises(config.ConfigError, match="hard links"):
        config.load_config(account_config)


@pytest.mark.skipif(os.name != "posix", reason="POSIX modes")
def test_shared_writeable_parent_is_rejected(account_config):
    account_config.parent.chmod(0o777)
    try:
        with pytest.raises(config.ConfigError, match="not writable"):
            config.load_config(account_config)
    finally:
        account_config.parent.chmod(0o700)
