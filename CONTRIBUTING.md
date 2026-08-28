# Contributing

Contributions must preserve CRUCIBLE's measurement integrity and defensive safety boundary.

1. Open an issue that states the research question and the evidence the change will produce.
2. Keep ground truth outside model-visible task material.
3. Use synthetic or deliberately vulnerable local fixtures only.
4. Add objective tests for schemas, budgets, scoring, isolation, and evidence integrity.
5. Run `make lint typecheck test test-properties test-sandbox docs` before requesting review.

Never commit sequestered task material, real credentials, production telemetry, proprietary model
transcripts, or identifiable human-subject data. New benchmark claims must include exact model,
agent, tool, task, budget, trial, date, scoring, and limitation metadata.
