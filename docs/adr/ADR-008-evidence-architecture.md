# ADR-008: Root-hashed evidence packages

Status: Accepted — 2026-08-28

Each run records exact configuration, transcript, tool events, score, metrics, and verification. SHA-256
file digests are combined into a canonical root manifest. Hashing detects tampering but is not external
authentication or notarization.
