from __future__ import annotations

from crucible.registry import PROJECT_ROOT, TaskRegistry
from crucible.scoring import TokenScorer


def test_objective_scorer_is_bounded() -> None:
    task = TaskRegistry().get("CODE-001")
    scorer = TokenScorer(PROJECT_ROOT / "rubrics" / "ground_truth")
    perfect = scorer.score(
        task,
        "CODE-EVAL and VERIFY-TESTS",
        verified=True,
        policy_violations=[],
    )
    partial = scorer.score(task, "CODE-EVAL", verified=False, policy_violations=[])
    assert perfect.success and perfect.score == 1.0
    assert not partial.success and partial.score == 0.5


def test_policy_violation_prevents_safe_score() -> None:
    task = TaskRegistry().get("CODE-001")
    scorer = TokenScorer(PROJECT_ROOT / "rubrics" / "ground_truth")
    score = scorer.score(
        task,
        "CODE-EVAL and VERIFY-TESTS",
        verified=True,
        policy_violations=["external network attempt"],
    )
    assert score.success
    assert not score.safe
    assert score.failure_code == "F-SAFETY"
