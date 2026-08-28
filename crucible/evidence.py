"""Tamper-evident evaluation evidence packages."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from crucible.schemas import EvaluationResult


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class EvidenceWriter:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def write(self, result: EvaluationResult) -> Path:
        destination = self.root / result.manifest.evaluation_id
        destination.mkdir(parents=True, exist_ok=False)
        records: dict[str, object] = {
            "manifest.json": result.manifest.model_dump(mode="json"),
            "model.json": result.manifest.model.model_dump(mode="json"),
            "agent.json": result.manifest.agent.model_dump(mode="json"),
            "environment.json": result.manifest.environment,
            "scores.json": result.score.model_dump(mode="json"),
            "metrics.json": result.usage.model_dump(mode="json"),
            "verification.json": {
                "agent_verified": result.score.verified,
                "policy_violations": result.policy_violations,
            },
        }
        for name, content in records.items():
            (destination / name).write_bytes(canonical_json(content) + b"\n")

        transcript = {
            "role": "assistant",
            "content": result.response.content,
            "refused": result.response.refused,
        }
        (destination / "transcript.jsonl").write_bytes(canonical_json(transcript) + b"\n")
        tool_lines = b"".join(
            canonical_json(event.model_dump(mode="json")) + b"\n" for event in result.tool_events
        )
        (destination / "tools.jsonl").write_bytes(tool_lines)
        (destination / "task-commitment.json").write_bytes(
            canonical_json({"sha256": result.manifest.task_set_commitment}) + b"\n"
        )
        (destination / "report.md").write_text(self._report(result), encoding="utf-8")

        files = sorted(path for path in destination.iterdir() if path.name != "evidence-root.json")
        hashes = {path.name: sha256_file(path) for path in files}
        root_hash = sha256_bytes(canonical_json(hashes))
        (destination / "evidence-root.json").write_bytes(
            canonical_json({"algorithm": "sha256", "files": hashes, "root_hash": root_hash}) + b"\n"
        )
        return destination

    @staticmethod
    def _report(result: EvaluationResult) -> str:
        score = result.score
        return (
            f"# Evaluation {result.manifest.evaluation_id}\n\n"
            f"- Model: `{result.manifest.model.model_id}`\n"
            f"- Agent: `{result.manifest.agent.agent_id}`\n"
            f"- Task set: `{result.manifest.task_set}`\n"
            f"- Score: `{score.score:.3f}`\n"
            f"- Success: `{score.success}`\n"
            f"- Safe: `{score.safe}`\n"
            f"- Verified: `{score.verified}`\n"
            f"- Reproducibility: `{result.manifest.reproducibility_level}`\n\n"
            "This result is bounded by the documented task, scaffold, tools, budget, "
            "and environment.\n"
        )


def verify_evidence(path: Path) -> tuple[bool, list[str]]:
    manifest_path = path / "evidence-root.json"
    if not manifest_path.exists():
        return False, ["missing evidence-root.json"]
    root = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    expected_files: dict[str, str] = root["files"]
    for name, expected in expected_files.items():
        file_path = path / name
        if not file_path.exists():
            errors.append(f"missing {name}")
        elif sha256_file(file_path) != expected:
            errors.append(f"digest mismatch: {name}")
    computed_root = sha256_bytes(canonical_json(expected_files))
    if computed_root != root["root_hash"]:
        errors.append("root hash mismatch")
    return not errors, errors
