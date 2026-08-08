# Security policy

## Reporting a vulnerability

Please do not disclose exploitable vulnerabilities in a public issue. Contact the maintainer privately with the affected version, reproduction steps, impact, and any suggested mitigation. A dedicated security address will be published before the public launch.

## Supported deployment model

The hosted server uses Streamable HTTP over HTTPS. Production deployments must:

- keep MCP transport security enabled;
- explicitly allow public `Host` values and required browser `Origin` values;
- validate JSON content types;
- apply request-size, input and result limits;
- keep the corpus read-only;
- run with least-privilege identity;
- use rate limiting and cost alerts;
- avoid logging confidential query content.

The production application disables HTTP access logs and never writes request bodies or question text to logs. Rate limiting uses only a short-lived in-memory digest of network information.

Never work around proxy configuration by monkey-patching or disabling `TransportSecurityMiddleware.validate_request`.

## Scope

The current tools are read-only. They do not execute shell commands, modify the corpus, access user accounts, or accept arbitrary URLs. This reduces impact but does not remove denial-of-service, scraping, dependency, session, or transport risks.

## Sensitive files

Production databases, raw source documents, `.env` files, keys, credentials, Terraform state, model artefacts and user data must never be committed to the public repository.
