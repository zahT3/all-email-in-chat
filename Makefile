.PHONY: install-local check
install-local:
	uv tool install --python 3.12 .

check:
	uv run ruff check src tests
	uv run ruff format --check src tests
	uv run pytest -q
