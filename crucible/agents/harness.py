"""CRUCIBLE-owned agent loop; no opaque agent framework is used."""

from __future__ import annotations

from pathlib import Path

from crucible.models.base import ModelAdapter
from crucible.registry import TaskRegistry
from crucible.schemas import AgentConfiguration, ModelResponse, TaskManifest
from crucible.tools import ToolGateway


class AgentHarness:
    def __init__(
        self,
        model: ModelAdapter,
        configuration: AgentConfiguration,
        fixture_root: Path,
    ) -> None:
        self.model = model
        self.configuration = configuration
        self.fixture_root = fixture_root.resolve()

    async def run(self, task: TaskManifest) -> tuple[ModelResponse, ToolGateway | None, bool]:
        context = TaskRegistry.model_context(task)
        if self.configuration.agent_id == "A0-model-only":
            return await self.model.infer(context), None, False

        gateway = ToolGateway(
            task_root=self.fixture_root,
            allowed_artifacts=task.input_artifacts,
            allowed_tools=task.allowed_tools,
            budget=task.resource_budget,
        )
        observations: dict[str, str] = {}
        for artifact in task.input_artifacts:
            observations[Path(artifact).name] = gateway.read_file(artifact)

        response = await self.model.infer(context, observations)
        verified = "VERIFY-" in response.content.upper()
        return response, gateway, verified
