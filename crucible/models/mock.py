"""Deterministic harness-validation model; it is not an AI capability baseline."""

from __future__ import annotations

from collections.abc import Mapping

from crucible.models.base import ModelAdapter
from crucible.schemas import ModelMetadata, ModelResponse, TaskContext


class DeterministicMockAdapter(ModelAdapter):
    RESPONSES: tuple[tuple[str, str], ...] = (
        ("eval(", "CWE-95 CODE-EVAL Replace eval with an allowlisted parser. VERIFY-TESTS"),
        (
            "privileged: true",
            "K8S-PRIVILEGED Set privileged false and drop ALL capabilities. VERIFY-POLICY",
        ),
        (
            "203.0.113.77",
            "IOC-203.0.113.77 Detect repeated denied access followed by success. VERIFY-QUERY",
        ),
        (
            "admin-login-success",
            "ACCOUNT-admin SOURCE-198.51.100.24 TIMELINE-CONFIRMED VERIFY-EVIDENCE",
        ),
        (
            "permissions: ['*']",
            "EXCESSIVE-AGENCY Enforce task-scoped allowlists and approval. VERIFY-AUTHZ",
        ),
        (
            "expected_signer",
            "SIGNER-MISMATCH Reject artifact and verify provenance chain. VERIFY-ATTESTATION",
        ),
        (
            "sha1",
            "LEGACY-SHA1 Prioritize migration to SHA-256 or stronger with crypto agility. "
            "VERIFY-CRYPTO",
        ),
    )

    async def infer(
        self,
        context: TaskContext,
        observations: Mapping[str, str] | None = None,
    ) -> ModelResponse:
        visible = "\n".join((observations or {}).values()).lower()
        if not visible:
            content = "INSUFFICIENT EVIDENCE: task artifacts were not available in model-only mode."
            return ModelResponse(
                content=content, input_tokens=28, output_tokens=13, confidence=0.98
            )
        for needle, answer in self.RESPONSES:
            if needle.lower() in visible:
                return ModelResponse(
                    content=answer,
                    input_tokens=max(1, len(visible.split())),
                    output_tokens=len(answer.split()),
                    confidence=0.99,
                )
        return ModelResponse(
            content="INSUFFICIENT EVIDENCE",
            input_tokens=max(1, len(visible.split())),
            output_tokens=2,
            confidence=0.8,
        )

    async def metadata(self) -> ModelMetadata:
        return ModelMetadata(
            model_id="mock-deterministic-v1",
            provider="CRUCIBLE",
            model_name="DeterministicMockAdapter",
            model_version="1.0.0",
            release_date="2026-08-28",
            context_window="UNBOUNDED_TEST_FIXTURE",
            reasoning_mode="deterministic-rules",
            tool_support=False,
            sampling_seed=0,
            api_version="internal-1",
            weights_pinnable=True,
        )
