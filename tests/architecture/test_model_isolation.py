from __future__ import annotations

import asyncio
from collections.abc import Mapping
from pathlib import Path

import pytest

from crucible.models.base import ModelAdapter
from crucible.orchestrator import EvaluationOrchestrator
from crucible.schemas import ModelMetadata, ModelResponse, TaskContext


class RecordingModel(ModelAdapter):
    def __init__(self) -> None:
        self.visible = ""

    async def infer(
        self, context: TaskContext, observations: Mapping[str, str] | None = None
    ) -> ModelResponse:
        self.visible = context.model_dump_json() + str(observations)
        return ModelResponse(content="INSUFFICIENT EVIDENCE")

    async def metadata(self) -> ModelMetadata:
        return ModelMetadata(model_id="recording-test")


@pytest.mark.sandbox
def test_model_never_receives_ground_truth(tmp_path: Path) -> None:
    model = RecordingModel()
    asyncio.run(EvaluationOrchestrator(model, evidence_root=tmp_path).run("CODE-001", "bounded"))
    assert "CODE-EVAL" not in model.visible
    assert "required_tokens" not in model.visible
    assert "ground_truth" not in model.visible
