"""Provider-neutral model adapters."""

from crucible.models.base import ModelAdapter
from crucible.models.local import LocalOpenAIAdapter
from crucible.models.mock import DeterministicMockAdapter

__all__ = ["DeterministicMockAdapter", "LocalOpenAIAdapter", "ModelAdapter"]
