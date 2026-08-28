"""Transparent capability, uplift, calibration, and uncertainty metrics."""

from __future__ import annotations

import math
import random
import statistics
from collections.abc import Callable, Sequence


def task_success_rate(successes: Sequence[bool]) -> float:
    return sum(successes) / len(successes) if successes else 0.0


def safe_capability_rate(successes: Sequence[bool], safe: Sequence[bool]) -> float:
    if len(successes) != len(safe):
        raise ValueError("success and safety vectors must have equal length")
    return (
        sum(ok and bounded for ok, bounded in zip(successes, safe, strict=True)) / len(successes)
        if successes
        else 0.0
    )


def capability_uplift(treatment: float, baseline: float) -> float:
    return treatment - baseline


def generalization_gap(public_score: float, sequestered_score: float) -> float:
    return public_score - sequestered_score


def brier_score(confidences: Sequence[float], outcomes: Sequence[bool]) -> float:
    if len(confidences) != len(outcomes) or not outcomes:
        raise ValueError("confidence and outcome vectors must be non-empty and equal length")
    return statistics.fmean(
        (confidence - int(outcome)) ** 2
        for confidence, outcome in zip(confidences, outcomes, strict=True)
    )


def pass_at_k(n: int, c: int, k: int) -> float:
    if not 0 <= c <= n or not 1 <= k <= n:
        raise ValueError("require 0 <= c <= n and 1 <= k <= n")
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def bootstrap_interval(
    values: Sequence[float],
    statistic: Callable[[Sequence[float]], float] = statistics.fmean,
    *,
    trials: int = 2_000,
    seed: int = 0,
    alpha: float = 0.05,
) -> tuple[float, float]:
    if not values:
        raise ValueError("values cannot be empty")
    rng = random.Random(seed)  # noqa: S311 - deterministic statistical resampling
    estimates = sorted(statistic(rng.choices(values, k=len(values))) for _ in range(trials))
    lower = estimates[int((alpha / 2) * trials)]
    upper = estimates[min(trials - 1, int((1 - alpha / 2) * trials))]
    return lower, upper
