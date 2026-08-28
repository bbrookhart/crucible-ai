from __future__ import annotations

import pytest
from pydantic import ValidationError

from crucible.registry import TaskRegistry
from crucible.schemas import ResourceBudget


def test_budget_rejects_zero_steps() -> None:
    with pytest.raises(ValidationError):
        ResourceBudget(max_steps=0)


def test_every_registered_task_is_supported_and_blocks_network() -> None:
    tasks = TaskRegistry().list()
    assert len(tasks) == 7
    for task in tasks:
        assert task.safety_class.value in {"S0", "S1", "S2", "S3"}
        assert "external_network" in task.prohibited_tools


def test_model_context_excludes_ground_truth_and_scoring() -> None:
    task = TaskRegistry().get("CODE-001")
    context = TaskRegistry.model_context(task)
    serialized = context.model_dump_json()
    assert "ground_truth" not in serialized
    assert "scoring" not in serialized
    assert "CODE-EVAL" not in serialized
