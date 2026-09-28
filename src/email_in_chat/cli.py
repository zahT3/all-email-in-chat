"""User setup, client onboarding, and composable email operations."""

from __future__ import annotations

import argparse
import asyncio
import getpass
import importlib.metadata
import json
import os
import shutil
import sys
from pathlib import Path

from email_in_chat import __version__
from email_in_chat.config import (
    MODES,
    PROVIDERS,
    ConfigError,
    add_account,
    aliases,
    default_path,
    init_config,
    load_config,
    materialize_backend,
    set_policy,
    store_credentials,
)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ConfigError(message)


def parser() -> argparse.ArgumentParser:
    from email_in_chat.clients import CLIENTS

    app = Parser(prog="email-in-chat", description="One email configuration, many desktop agents.")
    app.add_argument("--version", action="version", version=__version__)
    app.add_argument(
        "--json", action="store_true", help="Emit a stable JSON success/error envelope."
    )
    app.add_argument("--config", type=Path, default=default_path(), help="Private account config.")
    commands = app.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a private config without credentials.")
    init.add_argument("--demo", action="store_true", help="Use fictional offline mail only.")
    commands.add_parser("providers", help="List verified connection presets and custom support.")
    accounts = commands.add_parser("accounts", help="Configure accounts and store credentials.")
    acc = accounts.add_subparsers(dest="action", required=True)
    acc.add_parser("list", help="List configured account names without credential lookup.")
    add = acc.add_parser("add", help="Add account metadata; passwords go through accounts auth.")
    add.add_argument("name")
    add.add_argument("--email", required=True)
    add.add_argument("--provider", choices=PROVIDERS, default="custom")
    add.add_argument("--full-name", default="")
    add.add_argument("--imap-host")
    add.add_argument("--smtp-host")
    add.add_argument("--imap-port", type=int)
    add.add_argument("--smtp-port", type=int)
    add.add_argument("--receive-only", action="store_true")
    auth = acc.add_parser("auth", help="Hidden terminal prompt; saves credentials to OS keyring.")
    auth.add_argument("name")
    auth.add_argument("--separate-smtp", action="store_true")
    pol = commands.add_parser("policy", help="Set the operations agents can perform.")
    actions = pol.add_subparsers(dest="action", required=True)
    actions.add_parser("show")
    change = actions.add_parser("set", help="Replace operation mode and recipient allowlist.")
    change.add_argument("--mode", choices=MODES, required=True)
    change.add_argument(
        "--allow-recipient",
        action="append",
        default=[],
        help="Repeat for each allowed recipient. Omission disables sending.",
    )
    clients = commands.add_parser("clients", help="Generate or merge agent MCP configuration.")
    actions = clients.add_subparsers(dest="action", required=True)
    actions.add_parser("list")
    for verb in ("config", "install"):
        item = actions.add_parser(verb)
        item.add_argument("client", choices=CLIENTS)
        item.add_argument("--executable", help="Absolute email-in-chat executable path.")
        if verb == "install":
            item.add_argument("--target", type=Path, help="Override client config path.")
            item.add_argument("--apply", action="store_true", help="Apply the previewed merge.")
    doctor = commands.add_parser("doctor", help="Check local setup; no mailbox access by default.")
    doctor.add_argument(
        "--smoke",
        action="store_true",
        help="Initialize the MCP backend and list accounts, without sending.",
    )
    commands.add_parser("serve", help="Serve mail tools to an agent over MCP stdio.")
    ui = commands.add_parser("ui", help="Open the local mailbox and Agent setup wizard.")
    ui.add_argument(
        "--no-open", action="store_true", help="Print the private link without opening a browser."
    )
    commands.add_parser("tools", help="Discover permitted MCP tools and check the connection.")
    raw = commands.add_parser("tool-call", help="Call a named MCP tool through the same policy.")
    raw.add_argument("name")
    raw.add_argument("--arguments", default="{}", help="JSON object; never pass credentials here.")
    messages = commands.add_parser("messages", help="Search and read emails without marking read.")
    actions = messages.add_subparsers(dest="action", required=True)
    search = actions.add_parser("search")
    search.add_argument("--account", required=True)
    search.add_argument("--subject")
    search.add_argument("--text")
    search.add_argument("--from-address")
    search.add_argument("--unread", action="store_true")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--mailbox", default="INBOX")
    read = actions.add_parser("read")
    read.add_argument("--account", required=True)
    read.add_argument(
        "--id", action="append", required=True, help="Message UID; repeat for a batch."
    )
    read.add_argument("--mailbox", default="INBOX")
    for name in ("draft", "send"):
        item = commands.add_parser(
            name,
            help=("Save a draft" if name == "draft" else "Send a message")
            + " from a reviewed JSON request file.",
        )
        item.add_argument(
            "--request",
            type=Path,
            required=True,
            help="JSON with account_name, recipients, subject, body, optional threading.",
        )
        if name == "send":
            item.add_argument(
                "--execute",
                action="store_true",
                help="Submit once; without this flag only a preview is returned.",
            )
    return app


def context(path: Path) -> tuple[dict, Path]:
    data = load_config(path)
    return data, materialize_backend(path, data)


def executable() -> str:
    candidate = Path(sys.executable).parent / (
        "email-in-chat.exe" if os.name == "nt" else "email-in-chat"
    )
    if candidate.is_file():
        return str(candidate)
    found = shutil.which("email-in-chat")
    if found:
        return str(Path(found).absolute())
    raise ConfigError("Install the CLI with uv tool install . before generating client settings.")


def _object(text: str) -> dict:
    if len(text) > 1_000_000:
        raise ConfigError("Arguments exceed the supported size.")
    try:
        data = json.loads(text)
    except ValueError:
        raise ConfigError("Arguments must be valid JSON.") from None
    if not isinstance(data, dict):
        raise ConfigError("Arguments must be a JSON object.")
    return data


def call(path: Path, name: str, arguments: dict) -> dict:
    from email_in_chat.bridge import invoke_tool

    data, native = context(path)
    result = asyncio.run(
        invoke_tool(
            native, name, arguments, mode=data["mode"], aliases=aliases(data), demo=data["demo"]
        )
    )
    value = result.model_dump(mode="json", by_alias=True, exclude_none=True)
    return {"ok": not result.isError, "data": value, "demo": data["demo"]}


def dispatch(args) -> dict | None:
    path = args.config.expanduser().absolute()
    if args.command == "ui":
        from email_in_chat.ui import run_ui

        run_ui(path, executable(), open_browser=not args.no_open)
        return None
    if args.command == "init":
        return init_config(path, demo=args.demo)
    if args.command == "providers":
        return {
            "presets": PROVIDERS,
            "imap_tls_port": 993,
            "smtp_tls_port": 465,
            "authentication": "password_or_app_password",
            "oauth": "not_implemented",
            "provider_live_tests": "not_performed",
        }
    if args.command == "accounts":
        if args.action == "add":
            fields = {
                name: getattr(args, name)
                for name in (
                    "name",
                    "email",
                    "provider",
                    "full_name",
                    "imap_host",
                    "smtp_host",
                    "imap_port",
                    "smtp_port",
                    "receive_only",
                )
            }
            return add_account(path, **fields)
        if args.action == "auth":
            if not sys.stdin.isatty():
                raise ConfigError("Run accounts auth yourself in a private interactive terminal.")
            password = getpass.getpass("Mailbox app password (hidden; never paste into chat): ")
            smtp = (
                getpass.getpass("Separate SMTP app password (hidden): ")
                if args.separate_smtp
                else None
            )
            return store_credentials(path, args.name, password, smtp)
        data = load_config(path)
        return {
            "demo": data["demo"],
            "mode": data["mode"],
            "accounts": (
                [{"name": name, "fictional": True} for name in aliases(data)]
                if data["demo"]
                else [
                    {
                        "name": a["name"],
                        "provider": a["provider"],
                        "email": a["email"],
                        "can_receive": True,
                        "smtp_configured": bool(a["smtp_host"]),
                        "credential": "not_checked",
                    }
                    for a in data["accounts"]
                ]
            ),
        }
    if args.command == "policy":
        if args.action == "set":
            return set_policy(path, mode=args.mode, recipients=args.allow_recipient)
        data = load_config(path)
        return {
            "mode": data["mode"],
            "allowed_recipients": data["allowed_recipients"],
            "effective_on": "next server start",
        }
    if args.command == "clients":
        from email_in_chat.clients import client_profiles, install_config, render_config

        if args.action == "list":
            return {"clients": client_profiles()}
        command = args.executable or executable()
        if not Path(command).is_absolute():
            raise ConfigError("Use an absolute executable path for desktop clients.")
        argv = ["--config", str(path), "serve"]
        profile = render_config(args.client, command, argv)
        if args.action == "config":
            return profile
        if not profile.get("target_path"):
            raise ConfigError(
                "This client requires the remote setup instructions; no local file applies."
            )
        if args.client == "claude-desktop-windows" and os.name != "nt" and not args.target:
            raise ConfigError(
                "Specify --target when preparing a Windows configuration on another OS."
            )
        target = args.target or Path(os.path.expandvars(profile["target_path"])).expanduser()
        return install_config(args.client, command, argv, target=target, apply=args.apply)
    if args.command == "doctor":
        versions = {}
        for package in ("all-email-in-chat", "mcp-email-server", "mcp"):
            try:
                versions[package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                versions[package] = "missing"
        report = {
            "version": __version__,
            "python": sys.version.split()[0],
            "packages": versions,
            "config_path": str(path),
            "config_exists": path.is_file(),
            "mailbox_connection": "not_tested",
            "credential_lookup": "not_performed",
            "desktop_end_to_end": "not_tested",
            "sent_mail": False,
        }
        if not path.exists():
            report["next"] = "email-in-chat init --demo"
            if args.smoke:
                raise ConfigError("Initialize a config before requesting a protocol smoke test.")
            return report
        data = load_config(path)
        report.update(mode=data["mode"], demo=data["demo"], accounts=len(aliases(data)))
        if args.smoke:
            from email_in_chat.bridge import run_smoke

            native = materialize_backend(path, data)
            report["mcp"] = asyncio.run(
                run_smoke(native, mode=data["mode"], aliases=aliases(data), demo=data["demo"])
            )
            report["ok"] = report["mcp"]["ok"]
            report["credential_lookup"] = (
                "not_required" if data["demo"] else "backend_initialization"
            )
        return report
    if args.command in ("serve", "tools"):
        from email_in_chat.bridge import run_smoke, run_stdio

        data, native = context(path)
        if args.command == "serve":
            asyncio.run(
                run_stdio(native, mode=data["mode"], aliases=aliases(data), demo=data["demo"])
            )
            return None
        report = asyncio.run(
            run_smoke(native, mode=data["mode"], aliases=aliases(data), demo=data["demo"])
        )
        return report
    if args.command == "tool-call":
        return call(path, args.name, _object(args.arguments))
    if args.command == "messages":
        if args.action == "read":
            return call(
                path,
                "get_emails_content",
                {
                    "account_name": args.account,
                    "email_ids": args.id,
                    "mailbox": args.mailbox,
                    "mark_as_read": False,
                },
            )
        if not 1 <= args.limit <= 100 or args.page < 1:
            raise ConfigError("Use --limit 1..100 and --page >= 1.")
        arguments = {
            "account_name": args.account,
            "page": args.page,
            "page_size": args.limit,
            "mailbox": args.mailbox,
        }
        for key in ("subject", "text", "from_address"):
            if getattr(args, key):
                arguments[key] = getattr(args, key)
        if args.unread:
            arguments["seen"] = False
        return call(path, "list_emails_metadata", arguments)
    if args.command in ("draft", "send"):
        if args.request.stat().st_size > 1_000_000:
            raise ConfigError("Request file is too large.")
        arguments = _object(args.request.read_text())
        if args.command == "send" and not args.execute:
            return {
                "preview": True,
                "sent": False,
                "request": arguments,
                "next": "Review the exact request, then repeat with --execute.",
            }
        if args.command == "draft":
            arguments.setdefault("mailbox", "Drafts")
        return call(path, "save_to_mailbox" if args.command == "draft" else "send_email", arguments)
    raise ConfigError("Unsupported command.")


def main() -> None:
    as_json = "--json" in sys.argv
    try:
        args = parser().parse_args()
        result = dispatch(args)
        if result is None:
            return
        envelope = (
            result
            if "ok" in result and "data" in result
            else {"ok": result.get("ok", True), "data": result}
        )
        if as_json:
            print(json.dumps(envelope, ensure_ascii=False, default=str))
        elif args.command == "clients" and args.action == "config":
            print(result.get("content", ""))
            for instruction in result.get("instructions", []):
                print(instruction, file=sys.stderr)
        else:
            print(json.dumps(envelope, ensure_ascii=False, indent=2, default=str))
        if not envelope["ok"]:
            raise SystemExit(1)
    except (ConfigError, ValueError) as exc:
        message = str(exc)
        if as_json:
            print(
                json.dumps({"ok": False, "error": {"code": "invalid_request", "message": message}})
            )
        else:
            print(message, file=sys.stderr)
        raise SystemExit(2) from None
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception:
        message = (
            "Operation incomplete; no automatic retry. Run doctor and inspect the last result."
        )
        if as_json:
            print(
                json.dumps({"ok": False, "error": {"code": "operation_failed", "message": message}})
            )
        else:
            print(message, file=sys.stderr)
        raise SystemExit(1) from None
