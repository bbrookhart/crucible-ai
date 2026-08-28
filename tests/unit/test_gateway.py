from __future__ import annotations

from pathlib import Path

import pytest

from crucible.schemas import ResourceBudget
from crucible.tools import ToolBudgetExceeded, ToolGateway, ToolPolicyViolation


def gateway(root: Path, calls: int = 2) -> ToolGateway:
    (root / "allowed.txt").write_text("synthetic evidence", encoding="utf-8")
    return ToolGateway(root, ["allowed.txt"], ["read_file"], ResourceBudget(max_tool_calls=calls))


def test_gateway_reads_only_allowlisted_file(tmp_path: Path) -> None:
    selected = gateway(tmp_path)
    assert selected.read_file("allowed.txt") == "synthetic evidence"
    with pytest.raises(ToolPolicyViolation):
        selected.read_file("../secret.txt")
    assert selected.policy_violations


def test_gateway_enforces_tool_budget(tmp_path: Path) -> None:
    selected = gateway(tmp_path, calls=1)
    selected.read_file("allowed.txt")
    with pytest.raises(ToolBudgetExceeded):
        selected.read_file("allowed.txt")
