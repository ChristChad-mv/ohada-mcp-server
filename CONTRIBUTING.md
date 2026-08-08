# Contributing to OHADA MCP

Thank you for helping make OHADA legal information easier to use responsibly.

## Suitable contributions

- server reliability and MCP interoperability;
- schemas, validation and error handling;
- documentation and integration examples;
- test coverage;
- accessibility and French-language corrections;
- reproducible corpus-error reports with an official source URL.

The private production corpus, embeddings and ingestion operations are not maintained in this repository.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
ruff check src tests
```

Tests use a temporary fixture corpus and must not depend on a production database.

## Pull requests

Keep changes focused, add tests for behavior changes, and update documentation when a public contract changes. Do not commit generated databases, source PDFs, credentials, Terraform state, model weights, user queries, or client documents.

## Corpus corrections

Include the legal-text code, article reference, observed text, expected text, official publication URL, and publication date. Do not paste an entire publication when a short reproducible excerpt is sufficient.

## Responsible communication

Do not describe the project as an official OHADA service. Do not submit personal or confidential legal data. Security vulnerabilities should follow `SECURITY.md`, not a public issue.

