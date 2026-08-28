# Threat and safety model

## Assets

- sequestered task content, canaries, answers, ground truth, and scoring rules;
- model and agent configuration identity;
- tool authorization and resource budgets;
- run transcripts, scores, metrics, and evidence hashes;
- reviewer trust in published claims.

## Adversaries and failure sources

The evaluated model may be compromised, prompt-injected, overconfident, or strategically optimized for
the benchmark. An evaluator may accidentally leak answers or cherry-pick trials. Dependencies or model
endpoints may drift. A local host or BLACKBOX key may be compromised. Public task language may reveal
the answer shape.

## Controls

- reduced model-visible context and separate scoring root;
- typed allowlisted tools with canonical paths and server-side budgets;
- external-network prohibition and container policy for executable tasks;
- encrypted local BLACKBOX vault excluded from Git and CI;
- commit → run → reveal → verify workflow;
- deterministic public baselines, recorded seeds, exact known metadata, and `UNKNOWN` otherwise;
- root-hashed evidence package and explicit failure/safety outcomes;
- contamination canaries and repository leakage auditing;
- claim templates that bind conclusions to task distribution and budget.

## Residual risk

Local encryption does not resist a compromised evaluator host or disclosed key. Hashes detect changes
but do not authenticate an evaluator without external signing. Sequestration does not prove absence of
pretraining contamination. Container controls are defense in depth, not a complete VM boundary. Formal
human research requires institutional governance beyond this repository.
