# ADR-002: Defensive S0–S3 boundary

Status: Accepted — 2026-08-28

CRUCIBLE supports synthetic/local S0–S3 tasks and prohibits S4, public targets, credentials, malware,
persistence, destructive actions, phishing, external scanning, and unrestricted shell. Controlled
findings, patches, tests, and proof tokens are sufficient endpoints.
