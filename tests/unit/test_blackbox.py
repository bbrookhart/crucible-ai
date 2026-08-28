from __future__ import annotations

from pathlib import Path

from crucible.blackbox import commit, keygen, reveal, seal, verify


def test_blackbox_commit_reveal_verify(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "hidden.yaml").write_text("canary: TEST-CANARY-123", encoding="utf-8")
    key = keygen()
    vault = tmp_path / "vault.enc"
    commitment_path = tmp_path / "commitment.json"
    task_hash = seal(source, vault, key)
    commitment = commit(
        vault,
        commitment_path,
        environment_hash="env-hash",
        scoring_hash="score-hash",
        key=key,
    )
    assert task_hash == commitment.task_set_hash
    assert b"TEST-CANARY-123" not in vault.read_bytes()
    assert verify(
        vault,
        commitment_path,
        environment_hash="env-hash",
        scoring_hash="score-hash",
        key=key,
    ) == (True, [])
    destination = tmp_path / "reveal"
    assert reveal(vault, destination, key) == task_hash
    assert (destination / "hidden.yaml").read_text() == "canary: TEST-CANARY-123"
