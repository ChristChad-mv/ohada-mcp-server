.PHONY: help install dev test lint docs build

help:
	@echo "install  Install development and documentation dependencies"
	@echo "dev      Run the local MCP server"
	@echo "test     Run the hermetic test suite"
	@echo "lint     Check Python sources"
	@echo "docs     Build documentation strictly"
	@echo "build    Build Python source and wheel packages"

install:
	uv sync --locked --extra dev --extra docs

dev:
	uv run ohada-mcp

test:
	uv run pytest -q

lint:
	uv run ruff check src tests

docs:
	uv run mkdocs build --strict

build:
	uv build
