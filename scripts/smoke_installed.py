"""Exercise the PATH-installed wheel from a temporary working directory."""

import argparse
import http.cookiejar
import json
import re
import selectors
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener


def check_installed_ui(executable: str, config: Path, root: Path) -> None:
    process = subprocess.Popen(
        [executable, "--config", str(config), "ui", "--no-open"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            assert selector.select(10), "Installed UI did not start"
        line = process.stdout.readline()
        link = line.split(": ", 1)[1].strip()
        parts = urlsplit(link)
        base = f"{parts.scheme}://{parts.netloc}{parts.path}"
        origin = f"{parts.scheme}://{parts.netloc}"
        opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with opener.open(base, timeout=10) as response:
            html = response.read().decode()
        script = re.search(r'src="([^\"]+\.js)"', html)[1]
        with opener.open(base + script.removeprefix("./"), timeout=10) as response:
            assert response.status == 200 and len(response.read()) > 1000
        with opener.open(base + "LICENSES.txt", timeout=10) as response:
            assert b"react" in response.read()

        def post(action, data, csrf=""):
            request = Request(
                base + "api/" + action,
                data=json.dumps(data).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Origin": origin,
                    "X-EIC-CSRF": csrf,
                },
            )
            with opener.open(request, timeout=45) as response:
                return json.load(response)

        session = post("session", {"token": parse_qs(parts.fragment)["token"][0]})
        csrf = session["csrf"]
        result = post("check", {"name": "work"}, csrf)
        assert result["verified"] == "demo" and result["smtp_tested"] is False
        preview = post("preview", {"client": "cursor"}, csrf)
        assert Path(preview["target_path"]).parent == root / "demo-clients"
        result = post(
            "install", {"client": "cursor", "preview_token": preview["preview_token"]}, csrf
        )
        assert result["applied"] is True
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        if process.stdout:
            process.stdout.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    executable = shutil.which("email-in-chat")
    assert executable, "Install the CLI on PATH first"
    with tempfile.TemporaryDirectory(prefix="email-in-chat-smoke-") as directory:
        root = Path(directory).resolve()
        config = root / "demo.toml"

        def call(*arguments):
            result = subprocess.run(
                [executable, "--json", "--config", str(config), *arguments],
                cwd=root,
                text=True,
                capture_output=True,
                timeout=30,
                check=True,
            )
            data = json.loads(result.stdout)
            assert data["ok"], "Installed CLI returned a failure"
            return data

        missing = call("doctor")
        assert missing["data"]["config_exists"] is False
        call("init", "--demo")
        smoke = call("doctor", "--smoke")
        assert smoke["data"]["mcp"]["demo_read"]["demo"] is True
        found = call("messages", "search", "--account", "work", "--unread")
        assert found["data"]["structuredContent"]["emails"][0]["email_id"] == "101"
        read = call("messages", "read", "--account", "work", "--id", "101")
        assert read["data"]["structuredContent"]["mark_as_read_applied"] is False
        request = root / "request.json"
        request.write_text(
            json.dumps(
                {
                    "account_name": "work",
                    "recipients": ["test@example.test"],
                    "subject": "Synthetic smoke",
                    "body": "No real message is sent.",
                }
            )
        )
        call("policy", "set", "--mode", "draft", "--allow-recipient", "test@example.test")
        drafted = call("draft", "--request", str(request))
        assert drafted["demo"] is True
        preview = call("send", "--request", str(request))
        assert preview["data"]["sent"] is False
        target = root / "client.json"
        install = call("clients", "install", "cursor", "--target", str(target))
        assert install["data"]["applied"] is False and not target.exists()
        check_installed_ui(executable, config, root)
        report = {
            "ok": True,
            "installation": "wheel_on_PATH",
            "cwd": "isolated_temporary_directory",
            "packages": smoke["data"]["packages"],
            "checks": [
                "doctor_without_config",
                "demo_mcp_handshake",
                "search",
                "read_without_seen",
                "synthetic_draft",
                "send_preview",
                "client_install_preview",
                "installed_ui_assets_and_licenses",
                "ui_authenticated_demo_connection",
                "ui_isolated_client_install",
            ],
            "real_provider_accessed": False,
            "real_mail_sent": False,
            "desktop_settings_modified": False,
        }
    output = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.write_text(output)
    print(output, end="")


if __name__ == "__main__":
    main()
