# Changelog

All notable server, schema and corpus releases will be documented here.

## Unreleased

### Added

- Explicit MCP transport host and origin allowlists.
- Stateless Streamable HTTP configuration for scalable deployments.
- Input validation for searches, article references and ISO dates.
- Recognition of canonical codes and controlled official-title citation aliases.
- Hermetic tests that do not require the private production corpus.
- Public documentation site and self-hosting guidance.
- Privacy-preserving in-memory rate limiting and response security headers.
- Cloud Monitoring uptime, 5xx alerting and production dashboard resources.
- Bounded `get_articles` retrieval for two to five complete provisions in one call.
- Shared MCP/Gemini tool contracts, read-only annotations and reference assistant prompt.

### Changed

- Search is described accurately as SQLite FTS5 full-text retrieval.
- Historical tools explicitly report the scope of the currently indexed version.
- Unknown act codes are rejected instead of receiving generated fallback metadata.
- The public Docker image no longer embeds the production corpus.
- Search responses now expose bounded discovery snippets; citation and temporal checks return compact metadata without duplicating article text.

### Security

- Removed the global monkey patch that disabled MCP transport validation.
- Production databases, Terraform and generated artefacts are excluded from the public repository.

### Fixed

- Verification of long-form AUSCGIE citations.
- Exact article matching avoids confusing references such as article 16 and article 160.
- Complete reconstruction of provisions split across consecutive chunks.
- Exact extraction of articles embedded inside section-level corpus chunks, without neighbouring provisions.
