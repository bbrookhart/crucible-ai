"""Evidence-backed aggregate analysis and explicit comparison metadata."""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from crucible.metrics import bootstrap_interval, capability_uplift, task_success_rate


@dataclass(frozen=True)
class ConditionSummary:
    condition: str
    model_ids: tuple[str, ...]
    task_count: int
    success_rate: float
    mean_score: float
    score_ci95: tuple[float, float]
    median_seconds: float
    total_tool_calls: int
    verification_rate: float
    safe_capability_rate: float


def summarize(condition: str, paths: list[Path]) -> ConditionSummary:
    if not paths:
        raise ValueError(f"no evidence found for condition {condition}")
    scores: list[float] = []
    successes: list[bool] = []
    safe_success: list[bool] = []
    verified: list[bool] = []
    times: list[float] = []
    tool_calls = 0
    models: set[str] = set()
    for path in paths:
        manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
        score = json.loads((path / "scores.json").read_text(encoding="utf-8"))
        usage = json.loads((path / "metrics.json").read_text(encoding="utf-8"))
        models.add(manifest["model"]["model_id"])
        scores.append(float(score["score"]))
        successes.append(bool(score["success"]))
        safe_success.append(bool(score["success"] and score["safe"]))
        verified.append(bool(score["verified"]))
        times.append(float(usage["wall_time_seconds"]))
        tool_calls += int(usage["tool_calls"])
    return ConditionSummary(
        condition=condition,
        model_ids=tuple(sorted(models)),
        task_count=len(paths),
        success_rate=task_success_rate(successes),
        mean_score=statistics.fmean(scores),
        score_ci95=bootstrap_interval(scores),
        median_seconds=statistics.median(times),
        total_tool_calls=tool_calls,
        verification_rate=task_success_rate(verified),
        safe_capability_rate=task_success_rate(safe_success),
    )


def compare_summaries(baseline: ConditionSummary, treatment: ConditionSummary) -> dict[str, object]:
    if baseline.model_ids != treatment.model_ids:
        raise ValueError("comparison requires the same exact model identifiers")
    return {
        "baseline": baseline.__dict__,
        "treatment": treatment.__dict__,
        "success_uplift_pp": capability_uplift(treatment.success_rate, baseline.success_rate) * 100,
        "scope": "deterministic harness validation; not frontier-model capability",
    }
