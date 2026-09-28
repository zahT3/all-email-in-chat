# Contributing

Start with the README and `docs/architecture.md`. Keep mailbox protocols inside
the backend; keep client configuration and operation policy in this package.

```sh
uv sync --locked --python 3.12
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -q
uv build
```

Use synthetic accounts and fixture mail in tests. Do not commit credentials,
private configuration, `.eml` exports, customer data or screenshots containing mail.
Normal tests must not depend on a live mailbox or modify desktop configurations.

For a provider or desktop compatibility claim, record the version, date,
authentication method, exact scope and evidence. Keep documented support,
protocol tests and real product/provider tests separate. A new profile needs
official documentation and a generated-command test. A new backend needs tests
for policy denial, account isolation, pagination and uncertain write outcomes.

Use a new branch for changes. Describe the behavior and validation in your PR;
do not label local tests as a successful GitHub Actions run.
