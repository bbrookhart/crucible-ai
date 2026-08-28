from __future__ import annotations

import asyncio
from pathlib import Path

from crucible.evidence import verify_evidence
from crucible.models import DeterministicMockAdapter
from crucible.orchestrator import EvaluationOrchestrator


def test_evidence_verifies_and_detects_tampering(tmp_path: Path) -> None:
    result = asyncio.run(
        EvaluationOrchestrator(DeterministicMockAdapter(), evidence_root=tmp_path).run(
            "CODE-001", "bounded"
        )
    )
    path = Path(result.evidence_path or "")
    assert verify_evidence(path) == (True, [])
    with (path / "scores.json").open("a", encoding="utf-8") as handle:
        handle.write("tamper")
    valid, errors = verify_evidence(path)
    assert not valid
    assert "digest mismatch: scores.json" in errors
