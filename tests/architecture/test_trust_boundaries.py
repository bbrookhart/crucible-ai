from __future__ import annotations

import pytest

from crucible.registry import PROJECT_ROOT, TaskRegistry
from crucible.sandbox import DockerSandboxManager


@pytest.mark.sandbox
def test_sandbox_command_has_mandatory_isolation_controls() -> None:
    command = DockerSandboxManager().build_run_command("fixture@sha256:" + "0" * 64)
    joined = " ".join(command)
    assert "--network=none" in joined
    assert "--read-only" in joined
    assert "--cap-drop=ALL" in joined
    assert "no-new-privileges" in joined
    assert "/var/run/docker.sock" not in joined


@pytest.mark.sandbox
def test_task_artifacts_do_not_reference_ground_truth_tree() -> None:
    root = (PROJECT_ROOT / "tasks" / "fixtures").resolve()
    for task in TaskRegistry().list():
        for relative in task.input_artifacts:
            path = (root / relative).resolve()
            assert path.is_relative_to(root)
            assert "rubrics" not in path.parts
            assert path.is_file()


@pytest.mark.sandbox
def test_public_repository_contains_no_encrypted_vault() -> None:
    forbidden = list(PROJECT_ROOT.rglob("*.enc")) + list(PROJECT_ROOT.rglob("*.key"))
    assert forbidden == []
