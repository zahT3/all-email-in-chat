# Validation record

Verified locally on 2026-09-28, macOS arm64, Python 3.12.12. Runtime versions:
`all-email-in-chat==0.1.0`, `mcp-email-server==1.9.1`, `mcp==1.30.0`.

| Layer | Result | Scope |
| --- | --- | --- |
| Formatting and lint | Passed | Ruff checks and format validation of project source, tests and installed smoke script |
| Project test suite | **101 passed** | Config isolation and permissions, credential mocks, recipient policy, bridge denial and aliases, client merge behavior, CLI and real stdio subprocesses |
| Six generated client profiles | Passed through MCP SDK | Generated command → package entrypoint → bridge → demo backend → account discovery and synthetic read; these are part of the 101 tests |
| Published backend | Empty-account handshake passed | Actual installed Wh1isper 1.9.1, isolated config; no live mailbox |
| Distribution | Wheel and sdist built | Python package build; wheel installed as a PATH command |
| Installed CLI outside source tree | Passed | Temporary working directory; doctor, simulated search/read/draft, send preview, client install preview; [machine-readable result](installed-smoke.json) |
| Four upstreams | Scoped tests passed | [Separate audit](research/README.md); not part of this project's test count |
| GitHub Actions | **Passed: 101 tests, lint, formatting, build** | Linux runner; [initial publication run](https://github.com/zahT3/all-email-in-chat/actions/runs/36389912274), commit `3cb0c62` |
| Actual desktop UIs | Not run | Official configuration documentation checked; product-version acceptance remains pending |
| Real providers / credentials | Not run | No real email read, draft saved remotely, email sent or existing credentials accessed |
| OS coverage | macOS local + Linux CI; Windows pending | Linux tests use synthetic accounts and mocked credentials; real OS keyring and desktop acceptance remain pending |

Reproduce the project checks:

```sh
uv sync --locked --python 3.12
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run pytest -q
uv build
uv tool install --python 3.12 dist/all_email_in_chat-0.1.0-py3-none-any.whl
python3 scripts/smoke_installed.py
```

The last script uses the PATH-installed executable, creates and cleans its own
temporary config, and does not modify any real client settings. It exercises
offline fixtures only. Runtime invocation success is distinct from a successful
mail operation; inspect upstream `unknown` and reconciliation outcomes.
