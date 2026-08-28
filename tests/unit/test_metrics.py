from __future__ import annotations

import pytest

from crucible.metrics import (
    bootstrap_interval,
    brier_score,
    capability_uplift,
    generalization_gap,
    pass_at_k,
    safe_capability_rate,
)


def test_flagship_metrics() -> None:
    assert capability_uplift(0.75, 0.5) == 0.25
    assert generalization_gap(0.8, 0.6) == pytest.approx(0.2)
    assert safe_capability_rate([True, True, False], [True, False, True]) == pytest.approx(1 / 3)
    assert brier_score([1.0, 0.0], [True, False]) == 0.0
    assert pass_at_k(10, 2, 1) == pytest.approx(0.2)


def test_bootstrap_is_seed_reproducible() -> None:
    first = bootstrap_interval([0.0, 0.5, 1.0], trials=200, seed=17)
    second = bootstrap_interval([0.0, 0.5, 1.0], trials=200, seed=17)
    assert first == second
