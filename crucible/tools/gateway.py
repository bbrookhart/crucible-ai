"""Task-scoped tool gateway with server-side policy and budget enforcement."""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

from crucible.schemas import ResourceBudget, ToolEvent


class ToolPolicyViolation(RuntimeError):
    pass


class ToolBudgetExceeded(RuntimeError):
    pass


class ToolGateway:
    def __init__(
        self,
        task_root: Path,
        allowed_artifacts: list[str],
        allowed_tools: list[str],
        budget: ResourceBudget,
    ) -> None:
        self.task_root = task_root.resolve()
        self.allowed_paths = {
            (self.task_root / artifact).resolve() for artifact in allowed_artifacts
        }
        self.allowed_tools = frozenset(allowed_tools)
        self.budget = budget
        self.events: list[ToolEvent] = []
        self.policy_violations: list[str] = []

    def _authorize(self, tool: str) -> None:
        if tool not in self.allowed_tools:
            message = f"tool not authorized for task: {tool}"
            self.policy_violations.append(message)
            raise ToolPolicyViolation(message)
        if len(self.events) >= self.budget.max_tool_calls:
            raise ToolBudgetExceeded("maximum tool-call budget reached")

    def _record(
        self,
        tool: str,
        arguments: dict[str, object],
        result: str,
        started: float,
        error: str | None = None,
    ) -> None:
        self.events.append(
            ToolEvent(
                sequence=len(self.events) + 1,
                tool=tool,
                arguments=arguments,
                latency_ms=(time.monotonic() - started) * 1000,
                result_digest=hashlib.sha256(result.encode()).hexdigest(),
                error=error,
            )
        )

    def read_file(self, relative_path: str) -> str:
        tool = "read_file"
        started = time.monotonic()
        self._authorize(tool)
        candidate = (self.task_root / relative_path).resolve()
        if candidate not in self.allowed_paths or not candidate.is_relative_to(self.task_root):
            message = "path is outside the task-scoped artifact allowlist"
            self.policy_violations.append(message)
            self._record(tool, {"path": relative_path}, "", started, message)
            raise ToolPolicyViolation(message)
        result = candidate.read_text(encoding="utf-8")
        self._record(tool, {"path": relative_path}, result, started)
        return result

    def search_repository(self, query: str) -> str:
        tool = "search_repository"
        started = time.monotonic()
        self._authorize(tool)
        if len(query) < 2 or len(query) > 120:
            message = "query length outside policy"
            self.policy_violations.append(message)
            self._record(tool, {"query": query}, "", started, message)
            raise ToolPolicyViolation(message)
        matches: list[str] = []
        for path in sorted(self.allowed_paths):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if query.casefold() in line.casefold():
                    matches.append(f"{path.name}:{number}:{line[:240]}")
        result = "\n".join(matches[:100])
        self._record(tool, {"query": query}, result, started)
        return result


def safe_result_digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
