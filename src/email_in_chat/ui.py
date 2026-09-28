"""Ephemeral loopback onboarding UI. Credentials never become MCP arguments."""

from __future__ import annotations

import asyncio
import json
import os
import secrets
import socket
import time
import webbrowser
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Route

from email_in_chat.clients import ClientConfigError, client_profiles, install_config, render_config
from email_in_chat.config import (
    PROVIDERS,
    ConfigError,
    add_account,
    aliases,
    init_config,
    load_config,
    materialize_backend,
    store_credentials,
)

STATIC = Path(__file__).parent / "static"
SESSION_SECONDS = 30 * 60
BODY_LIMIT = 16_384


class UIError(ConfigError):
    """Safe, fixed user-facing text; never include provider exceptions."""


async def check_connection(path: Path, account: str) -> dict:
    """Authenticate and IMAP LIST; never read messages, set flags, or send mail."""
    from email_in_chat.bridge import invoke_tool

    data = await asyncio.to_thread(load_config, path)
    if account not in aliases(data):
        raise UIError("请选择已配置的邮箱。")
    # Always strip outgoing endpoints and use the read tool gate for diagnostics.
    native = await asyncio.to_thread(materialize_backend, path, {**data, "mode": "read"})
    try:
        async with asyncio.timeout(35):
            result = await invoke_tool(
                native,
                "list_mailboxes",
                {"account_name": account},
                mode="read",
                aliases=aliases(data),
                demo=data["demo"],
            )
    except TimeoutError:
        raise UIError("连接超时。请检查网络、服务器地址及 IMAP 开关后重试。") from None
    if result.isError:
        raise UIError(
            "收信连接未通过。请检查客户端专用密码、IMAP 权限、服务器地址和网络；可重新保存密码后重试。"
        )
    payload = result.structuredContent
    if payload is None:
        try:
            payload = json.loads(next(c.text for c in result.content if c.type == "text"))
        except (ValueError, StopIteration):
            payload = None
    folders = payload.get("result") if isinstance(payload, dict) else payload
    if not isinstance(folders, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("name"), str) for item in folders
    ):
        raise UIError("服务器返回了无法确认的目录结果；尚未判定连接成功。")
    return {
        "account": account,
        "demo": data["demo"],
        "verified": "demo" if data["demo"] else "imap_login_and_list",
        "folder_count": len(folders),
        "smtp_tested": False,
    }


class LocalUI:
    def __init__(self, path: Path, command: str, origin: str):
        self.path = path
        self.command = command
        self.origin = origin
        self.prefix = "/" + secrets.token_urlsafe(18)
        self.bootstrap = secrets.token_urlsafe(32)
        self.session = secrets.token_urlsafe(32)
        self.csrf = secrets.token_urlsafe(32)
        self.cookie = "eic_" + secrets.token_hex(8)
        self.expires = time.monotonic() + SESSION_SECONDS
        self.used = False
        self.lock = asyncio.Lock()
        self.previews: dict[str, str] = {}
        routes = [
            Route(self.prefix + "/api/{action}", self.api, methods=["GET", "POST"]),
            Route(self.prefix + "/{asset:path}", self.asset),
        ]
        self.app = Starlette(routes=routes)
        self.app.add_middleware(BaseHTTPMiddleware, dispatch=self.guard)

    @property
    def url(self) -> str:
        return f"{self.origin}{self.prefix}/#token={self.bootstrap}"

    async def guard(self, request: Request, call_next):
        if request.headers.get("host") != self.origin.removeprefix("http://"):
            response = JSONResponse({"error": "Host rejected"}, status_code=403)
        elif request.headers.get("origin") not in (None, self.origin):
            response = JSONResponse({"error": "Origin rejected"}, status_code=403)
        elif request.headers.get("sec-fetch-site") == "cross-site":
            response = JSONResponse({"error": "Cross-site request rejected"}, status_code=403)
        else:
            response = await call_next(request)
        response.headers.update(
            {
                "Cache-Control": "no-store",
                "Referrer-Policy": "no-referrer",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Content-Security-Policy": (
                    "default-src 'none'; script-src 'self'; style-src 'self'; "
                    "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
                    "base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
                ),
            }
        )
        return response

    async def asset(self, request: Request):
        name = request.path_params["asset"] or "index.html"
        target = (STATIC / name).resolve()
        if not target.is_relative_to(STATIC.resolve()) or not target.is_file():
            return JSONResponse({"error": "Not found"}, status_code=404)
        return FileResponse(target)

    async def body(self, request: Request) -> dict:
        if request.headers.get("content-type", "").split(";")[0] != "application/json":
            raise ConfigError("请求需要 JSON 格式。")
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > BODY_LIMIT:
                raise ConfigError("请求过大。")
        try:
            value = json.loads(body)
        except (ValueError, UnicodeError):
            raise ConfigError("请求格式无效。") from None
        if not isinstance(value, dict):
            raise ConfigError("请求格式无效。")
        return value

    async def api(self, request: Request):
        action = request.path_params["action"]
        try:
            if time.monotonic() >= self.expires:
                return JSONResponse({"error": "会话已过期，请重新运行 email-in-chat ui。"}, 401)
            if request.method == "POST" and request.headers.get("origin") != self.origin:
                return JSONResponse({"error": "Origin required"}, 403)
            if action == "session" and request.method == "POST":
                body = await self.body(request)
                token = body.get("token")
                if (
                    self.used
                    or not isinstance(token, str)
                    or not secrets.compare_digest(token, self.bootstrap)
                ):
                    return JSONResponse({"error": "启动链接已使用或无效，请重新启动向导。"}, 401)
                self.used = True
                response = JSONResponse({"csrf": self.csrf})
                response.set_cookie(
                    self.cookie,
                    self.session,
                    httponly=True,
                    samesite="strict",
                    path=self.prefix + "/",
                    max_age=SESSION_SECONDS,
                )
                return response
            if not secrets.compare_digest(request.cookies.get(self.cookie, ""), self.session):
                return JSONResponse({"error": "请使用终端生成的完整链接打开向导。"}, 401)
            if request.method == "GET" and action == "state":
                return JSONResponse({**await asyncio.to_thread(self.state), "csrf": self.csrf})
            if request.method != "POST":
                return JSONResponse({"error": "Not found"}, 404)
            if not secrets.compare_digest(request.headers.get("x-eic-csrf", ""), self.csrf):
                return JSONResponse({"error": "CSRF rejected"}, 403)
            body = await self.body(request)
            async with self.lock:
                if action == "check":
                    name = body.get("name")
                    if not isinstance(name, str):
                        raise ConfigError("请选择邮箱。")
                    return JSONResponse(await check_connection(self.path, name))
                result = await asyncio.to_thread(self.mutate, action, body)
            return JSONResponse(result)
        except UIError as exc:
            return JSONResponse({"error": str(exc)}, 400)
        except (ConfigError, ValueError, TypeError):
            # Validation errors may contain upstream input; return only our bounded messages.
            return JSONResponse(
                {
                    "error": (
                        "客户端配置操作未完成。请重新预览；检查同名条目、文件格式和权限后再试。"
                        if action in {"preview", "install"}
                        else "操作未完成，请检查填写内容。账号若已创建，可选择它并编辑服务器或重新保存密码后重试。"
                    )
                },
                400,
            )
        except Exception:
            return JSONResponse(
                {"error": "操作未完成。请检查系统钥匙串或配置文件权限后重试。"}, 500
            )

    def profiles(self) -> list[dict]:
        return [
            p
            for p in client_profiles()
            if p["client"] != ("claude-desktop" if os.name == "nt" else "claude-desktop-windows")
            and p["client"] != "chatgpt-web"
        ]

    def state(self) -> dict:
        data = load_config(self.path) if self.path.exists() else None
        return {
            "initialized": data is not None,
            "demo": data["demo"] if data else False,
            "mode": data["mode"] if data else "read",
            "accounts": (
                [
                    {"name": name, "email": f"{name}@example.test", "provider": "demo"}
                    for name in aliases(data)
                ]
                if data and data["demo"]
                else data["accounts"]
                if data
                else []
            ),
            "providers": PROVIDERS,
            "clients": self.profiles(),
            "config_path": str(self.path),
        }

    def mutate(self, action: str, body: dict) -> dict:
        if action == "init":
            if set(body) != {"demo"} or not isinstance(body["demo"], bool):
                raise ConfigError("请选择真实或模拟邮箱。")
            if body["demo"]:
                # A demo must never occupy or overwrite the normal account config.
                demo_path = self.path.parent / ("demo-" + secrets.token_hex(6)) / "accounts.toml"
                init_config(demo_path, demo=True)
                self.path = demo_path
                self.previews.clear()
            else:
                init_config(self.path)
            return self.state()
        if action in {"account", "account-update"}:
            fields = {
                "name",
                "email",
                "provider",
                "full_name",
                "imap_host",
                "smtp_host",
                "imap_port",
                "smtp_port",
                "receive_only",
                "password",
                "smtp_password",
            }
            if (
                set(body) - fields
                or not isinstance(body.get("password"), str)
                or not body["password"]
            ):
                raise ConfigError("请填写邮箱和客户端专用密码。")
            if not self.path.exists():
                init_config(self.path)
            metadata = {
                key: value
                for key, value in body.items()
                if key not in {"password", "smtp_password"}
            }
            add_account(self.path, **metadata, replace_existing=action == "account-update")
            self.previews.clear()
            return self.save_password(body)
        if action == "credentials":
            if set(body) - {"name", "password", "smtp_password"}:
                raise ConfigError("请求字段无效。")
            return self.save_password(body)
        if action in {"preview", "install"}:
            client = body.get("client")
            if client not in {p["client"] for p in self.profiles()}:
                raise ConfigError("请选择当前系统支持的 Agent。")
            data = load_config(self.path)
            if not aliases(data):
                raise ConfigError("请先添加邮箱。")
            argv = ["--config", str(self.path), "serve"]
            profile = render_config(client, self.command, argv)
            target = (
                self.path.parent / "demo-clients" / (client + "." + profile["format"])
                if data["demo"]
                else Path(os.path.expandvars(profile["target_path"])).expanduser()
            )
            if action == "install" and self.previews.get(client) != body.get("preview_token"):
                raise UIError("配置预览已失效或尚未生成，请重新点击预览后再写入。")
            if action == "install" and client not in self.previews:
                raise UIError("配置预览已失效或尚未生成，请重新点击预览后再写入。")
            try:
                result = install_config(
                    client, self.command, argv, target, apply=action == "install"
                )
            except ClientConfigError:
                raise UIError(
                    f"无法合并客户端配置：{target}。请检查已有 email-in-chat 条目是否与当前配置冲突、"
                    "文件格式是否有效，以及是否为符号链接。向导没有覆盖原设置；处理后重新预览。"
                ) from None
            except OSError:
                raise UIError(
                    f"无法写入客户端配置：{target}。请检查目录权限或磁盘空间，处理后重新预览。"
                ) from None
            result["demo"] = data["demo"]
            if action == "preview":
                self.previews[client] = secrets.token_urlsafe(24)
                result["preview_token"] = self.previews[client]
            else:
                self.previews.pop(client, None)
            return result
        raise ConfigError("未知操作。")

    def save_password(self, body: dict) -> dict:
        try:
            store_credentials(
                self.path, body.get("name"), body.get("password"), body.get("smtp_password")
            )
        except ConfigError:
            return {
                "credential_saved": False,
                "state": self.state(),
                "error": "账号资料已保留，但密码未完整保存。请检查系统钥匙串，选择该账号并重新保存密码。",
            }
        return {"credential_saved": True, "state": self.state()}


def run_ui(path: Path, command: str, *, open_browser: bool = True) -> None:
    import uvicorn

    if not (STATIC / "index.html").is_file():
        raise ConfigError(
            "UI assets are missing. Build frontend first: cd frontend && npm ci && npm run build"
        )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        ui = LocalUI(path, command, f"http://127.0.0.1:{listener.getsockname()[1]}")
        # Only the local terminal receives the single-use fragment; no HTTP access logging.
        print(f"Local setup (30 minutes): {ui.url}", flush=True)
        print("Press Ctrl+C to close. Keep this launch link private.", flush=True)
        if open_browser:
            webbrowser.open(ui.url)
        server = uvicorn.Server(uvicorn.Config(ui.app, access_log=False, log_level="critical"))
        server.run(sockets=[listener])
