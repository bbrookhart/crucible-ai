# ADR-005: CRUCIBLE-owned bounded agent loop

Status: Accepted — 2026-08-28

Avoid opaque agent frameworks. Register A0–A3 scaffolds explicitly and execute A0/A2 in a typed loop.
Memory, planner, retry, context, tools, and human approval are system configuration, not model metadata.
