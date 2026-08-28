"""Strongly typed, versioned contracts for CRUCIBLE evaluations."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SafetyClass(StrEnum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


class ContaminationStatus(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    SEQUESTERED = "SEQUESTERED"
    PROCEDURALLY_GENERATED = "PROCEDURALLY_GENERATED"


class EvaluationMode(StrEnum):
    MODEL = "MODEL"
    AGENT = "AGENT"
    HUMAN = "HUMAN"
    HUMAN_AI = "HUMAN_AI"


class FailureCode(StrEnum):
    KNOWLEDGE = "F-KNOWLEDGE"
    REASONING = "F-REASONING"
    PLANNING = "F-PLANNING"
    TOOL = "F-TOOL"
    EXECUTION = "F-EXECUTION"
    STATE = "F-STATE"
    RECOVERY = "F-RECOVERY"
    VERIFICATION = "F-VERIFICATION"
    CALIBRATION = "F-CALIBRATION"
    SAFETY = "F-SAFETY"
    REFUSAL = "F-REFUSAL"


class Difficulty(StrictModel):
    knowledge_depth: int = Field(ge=0, le=5)
    reasoning_depth: int = Field(ge=0, le=5)
    tool_complexity: int = Field(ge=0, le=5)
    environment_uncertainty: int = Field(ge=0, le=5)
    step_count: int = Field(ge=1, le=100)
    state_requirements: int = Field(ge=0, le=5)
    error_recovery_requirement: int = Field(ge=0, le=5)
    verification_difficulty: int = Field(ge=0, le=5)


class ResourceBudget(StrictModel):
    max_steps: int = Field(default=8, ge=1, le=100)
    max_tool_calls: int = Field(default=12, ge=0, le=500)
    max_tokens: int = Field(default=16_000, ge=1)
    max_wall_time: float = Field(default=60.0, gt=0, le=3600)
    max_compute_cost: float = Field(default=0.0, ge=0)


class ScoringSpec(StrictModel):
    method: str
    ground_truth_ref: str
    threshold: float = Field(default=1.0, ge=0, le=1)


class TaskManifest(StrictModel):
    schema_version: str = "1.0"
    task_id: str = Field(pattern=r"^[A-Z][A-Z0-9-]+$")
    version: str
    title: str
    domain: str
    capability_dimension: list[str]
    objective: str
    difficulty: Difficulty
    environment: str
    input_artifacts: list[str]
    allowed_tools: list[str]
    prohibited_tools: list[str]
    resource_budget: ResourceBudget
    scoring: ScoringSpec
    success_condition: str
    failure_condition: str
    safety_class: SafetyClass
    contamination_status: ContaminationStatus
    instructions: str

    @field_validator("prohibited_tools")
    @classmethod
    def require_external_network_prohibition(cls, value: list[str]) -> list[str]:
        if "external_network" not in value:
            raise ValueError("every task must prohibit external_network")
        return value

    @model_validator(mode="after")
    def enforce_supported_safety_class(self) -> TaskManifest:
        if self.safety_class not in set(SafetyClass):
            raise ValueError("CRUCIBLE v0.1 supports only S0-S3")
        return self


class TaskContext(StrictModel):
    """The only task representation that may cross the model trust boundary."""

    task_id: str
    title: str
    objective: str
    instructions: str
    artifact_names: list[str]
    allowed_tools: list[str]
    budget: ResourceBudget


class ModelMetadata(StrictModel):
    model_id: str
    provider: str = "UNKNOWN"
    model_name: str = "UNKNOWN"
    model_version: str = "UNKNOWN"
    release_date: str = "UNKNOWN"
    context_window: str = "UNKNOWN"
    reasoning_mode: str = "UNKNOWN"
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 4096
    tool_support: bool = False
    sampling_seed: int | str = "UNKNOWN"
    api_version: str = "UNKNOWN"
    evaluated_at: datetime = Field(default_factory=utc_now)
    weights_pinnable: bool = False


class AgentConfiguration(StrictModel):
    agent_id: str
    framework: str = "crucible-native"
    planner: str
    memory: str
    tools: list[str]
    max_steps: int
    retry_policy: str
    context_policy: str
    human_in_loop: bool = False
    mode: EvaluationMode


class ToolEvent(StrictModel):
    sequence: int = Field(ge=1)
    tool: str
    arguments: dict[str, Any]
    timestamp: datetime = Field(default_factory=utc_now)
    latency_ms: float = Field(ge=0)
    result_digest: str
    error: str | None = None


class Usage(StrictModel):
    steps: int = Field(ge=0)
    tool_calls: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    wall_time_seconds: float = Field(ge=0)
    compute_cost: float = Field(ge=0)


class ModelResponse(StrictModel):
    content: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    confidence: float | None = Field(default=None, ge=0, le=1)
    refused: bool = False


class Score(StrictModel):
    task_id: str
    score: float = Field(ge=0, le=1)
    success: bool
    matched: list[str]
    missing: list[str]
    unsupported_claims: list[str] = Field(default_factory=list)
    failure_code: FailureCode | None = None
    safe: bool = True
    verified: bool = False


class EvaluationManifest(StrictModel):
    schema_version: str = "1.0"
    evaluation_id: str
    task_set: str
    task_set_commitment: str
    model: ModelMetadata
    agent: AgentConfiguration
    tools: list[str]
    environment: dict[str, Any]
    budget: ResourceBudget
    sampling: dict[str, Any]
    scoring: dict[str, Any]
    started_at: datetime
    completed_at: datetime
    crucible_version: str
    reproducibility_level: str = "R2"


class EvaluationResult(StrictModel):
    manifest: EvaluationManifest
    response: ModelResponse
    score: Score
    usage: Usage
    tool_events: list[ToolEvent]
    policy_violations: list[str]
    evidence_path: str | None = None


class Commitment(StrictModel):
    version: str = "1.0"
    task_set_hash: str
    environment_hash: str
    scoring_hash: str
    commitment_hash: str
    created_at: datetime = Field(default_factory=utc_now)
