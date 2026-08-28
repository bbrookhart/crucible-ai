# Contamination model

Every task is classified `PUBLIC`, `PRIVATE`, `SEQUESTERED`, or `PROCEDURALLY_GENERATED`. Public
development tasks exist for harness debugging and reproduction; they are not suitable for headline
capability claims. Sequestered tasks must never enter Git history.

Controls include parameterized variants, semantic variants where feasible, task rotation, task-set
commitments, hidden canaries, and scanning published artifacts for canary overlap and sequestered paths.
Canary findings indicate contamination suspicion, not proof. A clean scan lowers observed leakage risk
but cannot establish absence of training-data exposure.

Each release should report public availability, age, searchability, publication status, procedural
variation, and sequestration. Retired task sets remain reproducibility artifacts but should not anchor
current headline claims.
