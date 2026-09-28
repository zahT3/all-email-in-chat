"""Exercise the PATH-installed wheel from a temporary working directory."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


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
