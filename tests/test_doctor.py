import json
import sys

import pytest

from email_in_chat.cli import main
from email_in_chat.config import init_config


def test_failed_protocol_check_is_a_failed_cli_result(tmp_path, monkeypatch, capsys):
    from email_in_chat import bridge

    config = tmp_path / "demo.toml"
    init_config(config, demo=True)

    async def failed_check(*args, **kwargs):
        return {"ok": False, "sent_mail": False}

    monkeypatch.setattr(bridge, "run_smoke", failed_check)
    monkeypatch.setattr(
        sys, "argv", ["email-in-chat", "--json", "--config", str(config), "doctor", "--smoke"]
    )
    with pytest.raises(SystemExit) as stopped:
        main()
    assert stopped.value.code == 1
    assert json.loads(capsys.readouterr().out)["ok"] is False
