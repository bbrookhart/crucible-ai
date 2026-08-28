"""File-backed task registry and static agent registry."""

from __future__ import annotations

from pathlib import Path

import yaml

from crucible.schemas import AgentConfiguration, EvaluationMode, TaskContext, TaskManifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TaskRegistry:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or PROJECT_ROOT / "tasks").resolve()

    def list(self, visibility: str | None = None) -> list[TaskManifest]:
        paths = sorted(
            path
            for collection in ("development", "public")
            for path in (self.root / collection).glob("*.yaml")
        )
        manifests = [self.load_path(path) for path in paths]
        if visibility is None:
            return manifests
        return [task for task in manifests if task.contamination_status == visibility]

    def get(self, task_id: str) -> TaskManifest:
        for task in self.list():
            if task.task_id == task_id:
                return task
        raise KeyError(f"unknown task: {task_id}")

    @staticmethod
    def load_path(path: Path) -> TaskManifest:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return TaskManifest.model_validate(raw)

    @staticmethod
    def model_context(task: TaskManifest) -> TaskContext:
        return TaskContext(
            task_id=task.task_id,
            title=task.title,
            objective=task.objective,
            instructions=task.instructions,
            artifact_names=[Path(item).name for item in task.input_artifacts],
            allowed_tools=task.allowed_tools,
            budget=task.resource_budget,
        )


AGENTS: dict[str, AgentConfiguration] = {
    "model-only": AgentConfiguration(
        agent_id="A0-model-only",
        planner="none",
        memory="none",
        tools=[],
        max_steps=1,
        retry_policy="none",
        context_policy="task-context-only",
        mode=EvaluationMode.MODEL,
    ),
    "single-tool": AgentConfiguration(
        agent_id="A1-single-tool-turn",
        planner="none",
        memory="single-turn",
        tools=["read_file"],
        max_steps=2,
        retry_policy="none",
        context_policy="task-context-plus-one-observation",
        mode=EvaluationMode.AGENT,
    ),
    "bounded": AgentConfiguration(
        agent_id="A2-bounded-agent",
        planner="explicit-observe-act-verify",
        memory="bounded-transcript",
        tools=["read_file", "search_repository", "submit_answer"],
        max_steps=8,
        retry_policy="one-recoverable-retry",
        context_policy="task-context-and-typed-tool-results",
        mode=EvaluationMode.AGENT,
    ),
    "long-horizon": AgentConfiguration(
        agent_id="A3-long-horizon-agent",
        planner="stateful-plan-replan-verify",
        memory="bounded-state-store",
        tools=["read_file", "search_repository", "run_tests", "submit_answer"],
        max_steps=32,
        retry_policy="bounded-by-run-budget",
        context_policy="task-scoped-state-and-typed-tool-results",
        mode=EvaluationMode.AGENT,
    ),
}


def get_agent(name: str) -> AgentConfiguration:
    try:
        return AGENTS[name]
    except KeyError as exc:
        raise KeyError(f"unknown agent configuration: {name}") from exc
