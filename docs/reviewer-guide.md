# Ten-minute reviewer guide

## 0–2 minutes — thesis and boundary

Read the README thesis, safety boundary, and limitations. Confirm that v0.1 claims harness validation,
not frontier-model capability.

## 2–4 minutes — task and scoring separation

```bash
crucible task inspect CODE-001
pytest tests/architecture/test_model_isolation.py -q
```

## 4–6 minutes — model-only baseline

```bash
crucible eval run CODE-001 --model mock --agent model-only
```

Inspect the returned evidence path and verify it with `crucible evidence verify RUN-ID`.

## 6–8 minutes — bounded-agent condition

```bash
crucible eval run CODE-001 --model mock --agent bounded
```

Confirm one allowlisted tool call, successful objective score, verification marker, and zero policy violations.

## 8–10 minutes — evidence-backed uplift

```bash
crucible compare --condition model-only --condition bounded-agent --suite blue
crucible evidence verify-all
crucible contamination audit
```

The comparison must state that it validates the deterministic harness only. Review `manifest.json`,
`scores.json`, `tools.jsonl`, and `evidence-root.json` before accepting the measurement.
