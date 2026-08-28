# Security policy

CRUCIBLE is defensive evaluation infrastructure. Do not use it against public, production,
or third-party systems. Supported tasks are limited to synthetic data, controlled repositories,
and isolated local services in safety classes S0–S3.

## Reporting a vulnerability

Do not open a public issue for an unpatched vulnerability. Use GitHub's private vulnerability
reporting feature for this repository. Include the affected version, reproduction steps using a
synthetic target, impact, and a proposed mitigation when possible.

## Boundaries

The project intentionally does not provide internet scanning, credential harvesting, persistence,
malware delivery, destructive payloads, unrestricted external shell access, or autonomous attack
capability. Reports that add or bypass those boundaries will not be accepted.

See [the threat model](docs/threat-model.md) for the complete trust-boundary analysis.
