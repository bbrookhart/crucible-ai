"""Deterministic scorer isolated from model-visible task context."""

from __future__ import annotations

import json
from pathlib import Path

from crucible.schemas import FailureCode, Score, TaskManifest


class GroundTruthError(RuntimeError):
    pass


class TokenScorer:
    def __init__(self, ground_truth_root: Path) -> None:
        self.ground_truth_root = ground_truth_root.resolve()

    def score(
        self,
        task: TaskManifest,
        output: str,
        *,
        verified: bool,
        policy_violations: list[str],
    ) -> Score:
        path = (self.ground_truth_root / task.scoring.ground_truth_ref).resolve()
        if not path.is_relative_to(self.ground_truth_root):
            raise GroundTruthError("ground truth reference escapes scoring root")
        raw = json.loads(path.read_text(encoding="utf-8"))
        required = [str(item) for item in raw["required_tokens"]]
        normalized = output.casefold()
        matched = [token for token in required if token.casefold() in normalized]
        missing = [token for token in required if token not in matched]
        score_value = len(matched) / len(required) if required else 0.0
        success = score_value >= task.scoring.threshold
        failure_code = None if success else FailureCode.KNOWLEDGE
        if output.startswith("INSUFFICIENT EVIDENCE"):
            failure_code = FailureCode.TOOL
        safe = not policy_violations
        if not safe:
            failure_code = FailureCode.SAFETY
        return Score(
            task_id=task.task_id,
            score=score_value,
            success=success,
            matched=matched,
            missing=missing,
            failure_code=failure_code,
            safe=safe,
            verified=verified,
        )
