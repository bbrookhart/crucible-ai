from __future__ import annotations

import asyncio
from pathlib import Path

from crucible.models import DeterministicMockAdapter
from crucible.orchestrator import EvaluationOrchestrator


def test_model_only_and_bounded_conditions_are_separate(tmp_path: Path) -> None:
    orchestrator = EvaluationOrchestrator(DeterministicMockAdapter(), evidence_root=tmp_path)
    model_only = asyncio.run(orchestrator.run("CODE-001", "model-only"))
    bounded = asyncio.run(orchestrator.run("CODE-001", "bounded"))
    assert not model_only.score.success
    assert model_only.usage.tool_calls == 0
    assert bounded.score.success
    assert bounded.usage.tool_calls == 1
    assert bounded.score.verified
    assert bounded.manifest.model.model_id == model_only.manifest.model.model_id


def test_blue_pack_mock_validation(tmp_path: Path) -> None:
    orchestrator = EvaluationOrchestrator(DeterministicMockAdapter(), evidence_root=tmp_path)
    task_ids = [
        "CODE-001",
        "PATCH-001",
        "DETECT-001",
        "INCIDENT-001",
        "AGENT-001",
        "SUPPLY-001",
        "CRYPTO-001",
    ]
    results = [asyncio.run(orchestrator.run(task_id, "bounded")) for task_id in task_ids]
    assert all(result.score.success for result in results)
    assert all(result.score.safe for result in results)
