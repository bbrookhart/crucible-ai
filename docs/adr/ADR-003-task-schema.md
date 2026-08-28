# ADR-003: Versioned task manifests

Status: Accepted — 2026-08-28

Tasks use strict Pydantic-validated YAML with multidimensional difficulty, explicit tools/prohibitions,
budgets, safety class, contamination status, and an external ground-truth reference. A reduced
`TaskContext` crosses the model boundary.
