# Security policy

## Reporting a vulnerability

Please do not disclose exploitable vulnerabilities in a public issue. Use the repository's private **Report a vulnerability** form under the Security tab. Include the affected version, reproduction steps, impact, and any suggested mitigation.

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

The public endpoint is intentionally anonymous because it exposes public, read-only legal material. If authenticated access is introduced, it must follow the MCP authorization specification and OAuth 2.1 resource/audience validation. Client tokens must never be forwarded to another service.

The built-in limiter is a per-instance safeguard. A high-traffic public deployment must additionally use an edge rate limiter so that limits remain global across instances.

Never work around proxy configuration by monkey-patching or disabling `TransportSecurityMiddleware.validate_request`.

## Scope

The current tools are read-only. They do not execute shell commands, modify the corpus, access user accounts, or accept arbitrary URLs. This reduces impact but does not remove denial-of-service, scraping, dependency, session, or transport risks.

## Sensitive files

Production databases, raw source documents, `.env` files, keys, credentials, Terraform state, model artefacts and user data must never be committed to the public repository.

## Container and dependencies

The reference image runs as an unprivileged user, installs dependencies from the hashed production lock export, and does not contain package managers or database command-line tools beyond the base image. Production corpus files must be mounted read-only. Keep the base-image digest and dependency lock current through reviewed automated updates.
