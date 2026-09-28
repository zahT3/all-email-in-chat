"""Application-owned configuration. Credential values never belong in TOML."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
import tomllib
import uuid
from pathlib import Path

import tomli_w
from filelock import FileLock

MODES = ("read", "draft", "manage")
SENTINEL = "__KEYRING__"
KEYRING_SERVICE = "mcp-email-server"
PROVIDERS = {
    "privateemail": {"imap": "mail.privateemail.com", "smtp": "mail.privateemail.com"},
    "aliyun-enterprise": {"imap": "imap.qiye.aliyun.com", "smtp": "smtp.qiye.aliyun.com"},
    "aliyun-personal": {"imap": "imap.aliyun.com", "smtp": "smtp.aliyun.com"},
    "custom": {},
}


class ConfigError(ValueError):
    pass


def default_path() -> Path:
    value = os.environ.get("EMAIL_IN_CHAT_CONFIG")
    if value:
        return Path(value).expanduser().absolute()
    root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return root / "all-email-in-chat" / "accounts.toml"


def private_parent(path: Path) -> None:
    path = path.expanduser().absolute()
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ConfigError("Configuration paths must not contain symbolic links.")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if os.name == "posix":
        parent = path.parent.stat()
        if parent.st_uid != os.getuid() or parent.st_mode & 0o022:
            raise ConfigError(
                "Configuration directory must be owned by you and not writable by others."
            )


def _private_file(path: Path) -> None:
    """Check existing local files without reading their contents."""
    for item in (path.absolute(), *path.absolute().parents):
        if item.is_symlink():
            raise ConfigError("Configuration paths must not contain symbolic links.")
    if not path.is_file():
        raise ConfigError("Configuration is missing or is not a regular file.")
    info = path.stat()
    if info.st_nlink != 1:
        raise ConfigError("Configuration must not have hard links.")
    if os.name == "posix":
        parent = path.parent.stat()
        if parent.st_uid != os.getuid() or parent.st_mode & 0o022:
            raise ConfigError(
                "Configuration directory must be owned by you and not writable by others."
            )
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ConfigError("Configuration must be owner-only (chmod 600).")


def _lock(path: Path) -> FileLock:
    lock_path = Path(str(path) + ".lock")
    private_parent(lock_path)
    if lock_path.exists():
        _private_file(lock_path)
    return FileLock(str(lock_path), mode=0o600)


def write_private(path: Path, text: str) -> None:
    private_parent(path)
    if path.exists() and not path.is_file():
        raise ConfigError("Configuration target must be a regular file.")
    fd, temp = tempfile.mkstemp(prefix=".email-in-chat-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        # Only our own unpublished temporary file is removed.
        if os.path.exists(temp):
            os.unlink(temp)


def init_config(path: Path, *, demo: bool = False) -> dict:
    private_parent(path)
    if not isinstance(demo, bool):
        raise ConfigError("demo must be a boolean.")
    with _lock(path):
        if path.exists():
            raise ConfigError("Configuration already exists; it was not changed.")
        data = {
            "schema_version": 1,
            "namespace": uuid.uuid4().hex[:12],
            "mode": "read",
            "demo": demo,
            "allowed_recipients": [],
            "accounts": [],
        }
        write_private(path, tomli_w.dumps(data))
    return {"path": str(path), "mode": "read", "demo": demo}


def _address(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"[^\s<>@,;]+@[^\s<>@,;]+\.[^\s<>@,;]+", value
    ):
        raise ConfigError("Use one plain email address, without a display name.")
    return value


def _host(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.\-]*", value):
        raise ConfigError("Use a mail server hostname, without a URL, path, or port.")
    return value


def _recipient(value: str) -> str:
    _address(value)
    # Upstream interprets allowlist entries as shell-style patterns. This
    # project promises individual addresses, so never pass pattern syntax.
    if any(character in value for character in "*?[]"):
        raise ConfigError("Allowed recipients must be exact addresses, without wildcards.")
    return value


def load_config(path: Path) -> dict:
    _private_file(path)
    if path.stat().st_size > 1_000_000:
        raise ConfigError("Configuration exceeds the supported size.")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        raise ConfigError("Cannot parse configuration TOML.") from None
    return _validate_config(data)


def _validate_config(data: dict) -> dict:
    """Reject malformed snapshots before writes, keyring access, or launch."""
    if not isinstance(data, dict):
        raise ConfigError("Configuration must be a table.")
    allowed = {"schema_version", "namespace", "mode", "demo", "allowed_recipients", "accounts"}
    if set(data) - allowed:
        raise ConfigError("Unknown configuration fields; do not put secrets in this file.")
    if (
        type(data.get("schema_version")) is not int
        or data["schema_version"] != 1
        or data.get("mode") not in MODES
    ):
        raise ConfigError("Unsupported configuration version or mode.")
    if not isinstance(data.get("namespace"), str) or not re.fullmatch(
        r"[a-f0-9]{12}", data["namespace"]
    ):
        raise ConfigError("Invalid credential namespace.")
    if not isinstance(data.get("demo"), bool):
        raise ConfigError("demo must be a boolean.")
    accounts = data.get("accounts")
    recipients = data.get("allowed_recipients")
    if not isinstance(accounts, list) or not isinstance(recipients, list):
        raise ConfigError("accounts and allowed_recipients must be lists.")
    if data["demo"] and accounts:
        raise ConfigError("Demo config cannot contain real accounts.")
    for address in recipients:
        _recipient(address)
    names = set()
    keys = {
        "name",
        "email",
        "full_name",
        "provider",
        "imap_host",
        "imap_port",
        "smtp_host",
        "smtp_port",
        "smtp_starttls",
    }
    for account in accounts:
        if not isinstance(account, dict) or set(account) - keys:
            raise ConfigError("Invalid account fields; credentials must use the keyring.")
        if not isinstance(account.get("name"), str) or not re.fullmatch(
            r"[a-z][a-z0-9-]{0,39}", account["name"]
        ):
            raise ConfigError("Account names must be lowercase letters, digits, and hyphens.")
        if not isinstance(account.get("provider"), str) or account["provider"] not in PROVIDERS:
            raise ConfigError("Unknown provider preset.")
        if not isinstance(account.get("full_name"), str) or any(
            c in account["full_name"] for c in "\r\n\x00"
        ):
            raise ConfigError("full_name must be a single-line string.")
        if account["name"] in names:
            raise ConfigError("Duplicate account name.")
        names.add(account["name"])
        _address(account.get("email", ""))
        _host(account.get("imap_host", ""))
        if not isinstance(account.get("smtp_host"), str):
            raise ConfigError("smtp_host must be a hostname or an empty string.")
        if account["smtp_host"]:
            _host(account["smtp_host"])
        for field in ("imap_port", "smtp_port"):
            value = account.get(field, 0)
            if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 65535:
                raise ConfigError("Invalid mail server port.")
        if not isinstance(account.get("smtp_starttls"), bool):
            raise ConfigError("smtp_starttls must be a boolean.")
    return data


def add_account(
    path: Path,
    *,
    name: str,
    email: str,
    provider: str,
    full_name: str = "",
    imap_host: str | None = None,
    smtp_host: str | None = None,
    imap_port: int = 993,
    smtp_port: int = 465,
    receive_only: bool = False,
) -> dict:
    private_parent(path)
    if not isinstance(receive_only, bool):
        raise ConfigError("receive_only must be a boolean.")
    if not isinstance(full_name, str):
        raise ConfigError("full_name must be a single-line string.")
    with _lock(path):
        data = load_config(path)
        if data["demo"]:
            raise ConfigError("Demo config cannot contain real accounts. Use a separate config.")
        if any(a["name"] == name for a in data["accounts"]):
            raise ConfigError("Account already exists; it was not changed.")
        if not isinstance(provider, str) or provider not in PROVIDERS:
            raise ConfigError("Unknown provider preset.")
        preset = PROVIDERS[provider]
        item = {
            "name": name,
            "email": _address(email),
            "provider": provider,
            "full_name": full_name or name,
            "imap_host": _host(imap_host or preset.get("imap", "")),
            "imap_port": imap_port,
            "smtp_host": "" if receive_only else _host(smtp_host or preset.get("smtp", "")),
            "smtp_port": smtp_port,
            "smtp_starttls": smtp_port == 587,
        }
        data["accounts"].append(item)
        _validate_config(data)
        write_private(path, tomli_w.dumps(data))
    return {
        "account": name,
        "configured": True,
        "credential": "not_checked",
        "next": f"email-in-chat accounts auth {name}",
    }


def aliases(data: dict) -> dict[str, str]:
    if data["demo"]:
        return {"work": "demo-work", "personal": "demo-personal"}
    return {a["name"]: f"eic-{data['namespace']}-{a['name']}" for a in data["accounts"]}


def _unsafe_keyring(backend: object) -> bool:
    identity = f"{type(backend).__module__}.{type(backend).__name__}".lower()
    if "plaintext" in identity or "keyrings.alt" in identity:
        return True
    if identity == "keyring.backends.chainer.chainerbackend":
        return any(_unsafe_keyring(child) for child in backend.backends)
    return False


def store_credentials(
    path: Path, name: str, password: str, smtp_password: str | None = None
) -> dict:
    """Only called from a private terminal. Never an MCP tool."""
    import keyring

    data = load_config(path)
    account = next((a for a in data["accounts"] if a["name"] == name), None)
    if account is None or data["demo"]:
        raise ConfigError("Unknown real account.")
    if (
        not isinstance(password, str)
        or not password
        or password == SENTINEL
        or (
            smtp_password is not None
            and (
                not isinstance(smtp_password, str) or not smtp_password or smtp_password == SENTINEL
            )
        )
    ):
        raise ConfigError("Invalid credential value.")
    key = aliases(data)[name]
    try:
        backend = keyring.get_keyring()
        if backend.priority <= 0 or _unsafe_keyring(backend):
            raise ConfigError("No secure OS keyring is available.")
        keyring.set_password(KEYRING_SERVICE, f"{key}:incoming", password)
        if account["smtp_host"]:
            keyring.set_password(KEYRING_SERVICE, f"{key}:outgoing", smtp_password or password)
    except ConfigError:
        raise
    except Exception:
        raise ConfigError(
            "Keyring update incomplete. Re-run accounts auth in a private terminal."
        ) from None
    return {"account": name, "credential": "stored_in_os_keyring", "connection": "not_tested"}


def set_policy(path: Path, *, mode: str, recipients: list[str]) -> dict:
    private_parent(path)
    if mode not in MODES:
        raise ConfigError("Unknown mode.")
    if not isinstance(recipients, list):
        raise ConfigError("allowed_recipients must be a list.")
    for address in recipients:
        _recipient(address)
    with _lock(path):
        data = load_config(path)
        data["mode"] = mode
        data["allowed_recipients"] = sorted(set(recipients))
        write_private(path, tomli_w.dumps(data))
    return {"mode": mode, "allowed_recipients": sorted(set(recipients)), "restart_required": True}


def materialize_backend(path: Path, data: dict) -> Path:
    """Generate an isolated, secret-free upstream config from a validated snapshot."""
    _validate_config(data)
    native = {
        "credential_storage": "keyring",
        "allowed_recipients": [] if data["mode"] == "read" else data["allowed_recipients"],
        "enable_attachment_download": False,
        "emails": [],
    }
    mapping = aliases(data)
    for item in data["accounts"]:

        def endpoint(role: str) -> dict:
            starttls = role == "smtp" and item["smtp_starttls"]
            return {
                "user_name": item["email"],
                "password": SENTINEL,
                "host": item[f"{role}_host"],
                "port": item[f"{role}_port"],
                "use_ssl": not starttls,
                "start_ssl": starttls,
                "verify_ssl": True,
            }

        account = {
            "account_name": mapping[item["name"]],
            "full_name": item["full_name"],
            "email_address": item["email"],
            "incoming": endpoint("imap"),
            "save_to_sent": True,
        }
        if item["smtp_host"] and data["mode"] == "manage":
            account["outgoing"] = endpoint("smtp")
        native["emails"].append(account)
    text = f"# email-in-chat mode: {data['mode']}\n" + tomli_w.dumps(native)
    # Distinct immutable snapshots avoid concurrent sessions changing each other's endpoints.
    stamp = hashlib.sha256(text.encode()).hexdigest()[:16]
    target = path.parent / "runtime" / f"backend-{stamp}.toml"
    private_parent(target)
    with _lock(target):
        if not target.exists():
            write_private(target, text)
        else:
            _private_file(target)
            if target.read_text() != text:
                raise ConfigError("Backend configuration snapshot was modified.")
    return target
