# ADR-004: Provider-neutral model abstraction

Status: Accepted — 2026-08-28

Adapters expose `infer` and `metadata`; unknown provider fields remain `UNKNOWN`. Tests require no
provider. v0.1 includes a deterministic mock and a loopback-only OpenAI-compatible local adapter.
