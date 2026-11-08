.PHONY: install run lint format build package-install

install:
	uv sync

run:
	uv run database

lint:
	uv run ruff check .

format:
	uv run ruff format .

build:
	uv build

package-install:
	uv tool install --reinstall dist/*.whl
