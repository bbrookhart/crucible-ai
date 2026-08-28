# CRUCIBLE build report

## Release

Version `0.1.0`, built and verified 2026-08-28.

## Research questions

v0.1 evaluates whether the harness separates model-only from bounded tool-mediated conditions and
whether it preserves scorer isolation, budget enforcement, tool observability, evidence integrity, and
safety. Autonomous frontier capability, human uplift, sequestered generalization, and resource scaling
remain `NOT MEASURED`.

## Models and agents

The only evaluated configuration is `mock-deterministic-v1`, exact internal version `1.0.0`, seed 0.
It is not a learned model. Conditions are A0 model-only and A2 bounded agent using the same adapter.

## Benchmark and safety boundary

CRUCIBLE // BLUE v0.1 contains seven public S1 defensive static-artifact tasks. Every task prohibits
external network, arbitrary shell, credentials, destructive action, and active external response.

## BLACKBOX

v0.1 implements encrypted-at-rest local vaults, task/environment/scorer commitments, ephemeral reveal,
and verification. Tests prove ciphertext does not expose the synthetic canary and commitments change
with hidden content. No sequestered task set is distributed or evaluated in this release.

## Model-only results

- N: 7 tasks, one deterministic trial each
- Task success: 0/7
- Safe capability: 0/7
- Verification: 0/7
- Tool calls: 0
- Input/output tokens: 196/91 (deterministic adapter accounting)
- Median wall time: 0.01157 seconds on the build host

## Bounded-agent results

- N: 7 tasks, one deterministic trial each
- Task success: 7/7
- Safe capability: 7/7
- Verification: 7/7
- Tool calls: 7
- Input/output tokens: 106/57 (deterministic adapter accounting)
- Median wall time: 0.01169 seconds on the build host

## Capability uplift and generalization

Observed A0 → A2 success uplift is +100 percentage points. This is an expected harness-validation
contrast because A0 intentionally lacks artifact access and A2 receives task-scoped reads. It is not an
AI capability estimate. Public-versus-sequestered generalization gap is `NOT MEASURED`.

## Failure modes and safety

All A0 outcomes are `F-TOOL` with appropriate `INSUFFICIENT EVIDENCE` abstention. A2 recorded no policy
violations or out-of-scope attempts. No controlled recovery fault was triggered, so recovery rate is
`NOT MEASURED`.

## Evidence and statistics

Fourteen release run packages and [the aggregate summary](../evidence/release-summary-v0.1.json) are
checked in. Every package verifies against its SHA-256 root manifest. The adapter is deterministic, so
inferential significance is not applicable; intervals [0, 0] and [1, 1] describe these seven fixed tasks
only and must not be interpreted as population confidence intervals.

## Verification

- Ruff format/lint: passed
- strict mypy: passed across 22 source files
- pytest: 21 passed; 63% aggregate branch-insensitive line coverage
- property tests: 3 passed
- sandbox architecture tests: 4 passed
- dependency audit: no known vulnerabilities after patched lockfile refresh
- secret scan: passed
- contamination audit: LOW observed risk; no findings (not proof of absence)
- wheel and source distribution: built
- CLI smoke, BLUE suite, comparison, evidence verification, docs check: passed
- local `/health` service: passed
- Docker runtime validation: not run because Docker is unavailable on the build host; command-policy tests passed

## Limitations

No learned model, provider model, human participant, dynamic S2/S3 workload, sequestered task set,
formal power analysis, or external independent reproduction is included. Docker base image uses a
versioned tag but is not digest-pinned in v0.1; executable task images are rejected unless digest-pinned.

## Reviewer path

```bash
make bootstrap
make lint typecheck test test-properties test-sandbox security build docs
crucible compare --condition model-only --condition bounded-agent --suite blue
crucible evidence verify-all
crucible contamination audit
```

## Next research milestone

Build CRUCIBLE // LONGFORM with digest-pinned dynamic defensive environments, procedurally varied
tasks, controlled recoverable failures, repeated open-model trials, and verification-quality scoring.

**Technical status: v0.1 research foundation and public harness validation complete.**
