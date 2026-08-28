"""Evaluation control plane that keeps model, tools, scorer, and evidence separated."""

from __future__ import annotations

import hashlib
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from crucible import __version__
from crucible.agents import AgentHarness
from crucible.evidence import EvidenceWriter, canonical_json
from crucible.models.base import ModelAdapter
from crucible.registry import PROJECT_ROOT, TaskRegistry, get_agent
from crucible.schemas import EvaluationManifest, EvaluationResult, Usage
from crucible.scoring import TokenScorer


class EvaluationOrchestrator:
    def __init__(
        self,
        model: ModelAdapter,
        *,
        project_root: Path | None = None,
        evidence_root: Path | None = None,
    ) -> None:
        self.project_root = (project_root or PROJECT_ROOT).resolve()
        self.registry = TaskRegistry(self.project_root / "tasks")
        self.model = model
        self.scorer = TokenScorer(self.project_root / "rubrics" / "ground_truth")
        self.evidence = EvidenceWriter(evidence_root or self.project_root / "evidence")

    async def run(self, task_id: str, agent_name: str) -> EvaluationResult:
        started_at = datetime.now(UTC)
        started = time.monotonic()
        task = self.registry.get(task_id)
        agent = get_agent(agent_name)
        if agent.max_steps > task.resource_budget.max_steps:
            agent = agent.model_copy(update={"max_steps": task.resource_budget.max_steps})
        harness = AgentHarness(
            self.model,
            agent,
            self.project_root / "tasks" / "fixtures",
        )
        response, gateway, verified = await harness.run(task)
        elapsed = time.monotonic() - started
        if elapsed > task.resource_budget.max_wall_time:
            raise TimeoutError("evaluation exceeded wall-time budget")
        events = gateway.events if gateway else []
        policy_violations = gateway.policy_violations if gateway else []
        score = self.scorer.score(
            task,
            response.content,
            verified=verified,
            policy_violations=policy_violations,
        )
        model_metadata = await self.model.metadata()
        task_commitment = hashlib.sha256(canonical_json(task.model_dump(mode="json"))).hexdigest()
        evaluation_id = f"RUN-{datetime.now(UTC):%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:8]}"
        completed_at = datetime.now(UTC)
        usage = Usage(
            steps=1 + len(events),
            tool_calls=len(events),
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            wall_time_seconds=elapsed,
            compute_cost=0.0,
        )
        manifest = EvaluationManifest(
            evaluation_id=evaluation_id,
            task_set=f"CRUCIBLE-BLUE-v0.1:{task.task_id}:{task.version}",
            task_set_commitment=task_commitment,
            model=model_metadata,
            agent=agent,
            tools=[event.tool for event in events],
            environment={
                "environment_id": task.environment,
                "task_version": task.version,
                "network_policy": "none",
                "runtime": "local-static-artifact",
                "image_digest": "NOT_APPLICABLE_S1",
            },
            budget=task.resource_budget,
            sampling={
                "temperature": model_metadata.temperature,
                "seed": model_metadata.sampling_seed,
            },
            scoring={"method": task.scoring.method, "threshold": task.scoring.threshold},
            started_at=started_at,
            completed_at=completed_at,
            crucible_version=__version__,
        )
        initial = EvaluationResult(
            manifest=manifest,
            response=response,
            score=score,
            usage=usage,
            tool_events=events,
            policy_violations=policy_violations,
        )
        path = self.evidence.write(initial)
        return initial.model_copy(update={"evidence_path": str(path)})
