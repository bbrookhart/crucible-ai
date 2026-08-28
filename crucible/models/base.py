"""Model trust-boundary interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from crucible.schemas import ModelMetadata, ModelResponse, TaskContext


class ModelAdapter(ABC):
    @abstractmethod
    async def infer(
        self,
        context: TaskContext,
        observations: Mapping[str, str] | None = None,
    ) -> ModelResponse:
        """Produce a response from model-visible context only."""

    @abstractmethod
    async def metadata(self) -> ModelMetadata:
        """Return exact known metadata, using UNKNOWN for unavailable fields."""
