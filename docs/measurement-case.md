# Measurement assurance case

## Claim M-001

The A2 harness can measure tool-mediated uplift relative to A0 for CRUCIBLE // BLUE development tasks.

**Argument:** both conditions use the same deterministic model, task definitions, objective scorer, and
recorded budget. A0 receives no artifact tool. A2 receives only task-scoped read access and records it.

**Evidence:** run manifests; tool events; scores; architecture test proving ground truth is absent from
model-visible context; root-hash verification; comparison output.

**Limitation:** the mock adapter is programmed for harness validation. The result does not estimate AI
capability and does not generalize beyond the included public fixtures.

## Claim M-002

Published evidence detects post-run artifact modification.

**Argument:** the writer hashes every artifact and hashes the canonical file-hash map.

**Evidence:** `tests/unit/test_evidence.py` verifies an intact package and detects score tampering.

**Limitation:** hashes do not authenticate the evaluator or provide third-party timestamping.
