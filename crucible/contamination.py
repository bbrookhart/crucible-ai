"""Repository leakage checks for sequestered canaries and answer material."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ContaminationFinding:
    path: str
    line: int
    canary_digest: str


def audit(root: Path, canaries: list[str]) -> list[ContaminationFinding]:
    if any(len(canary) < 8 for canary in canaries):
        raise ValueError("canaries must contain at least eight characters")
    ignored = {".git", ".venv", ".crucible", "__pycache__", "evidence"}
    findings: list[ContaminationFinding] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if any(part in ignored for part in path.parts):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            for canary in canaries:
                if canary in line:
                    findings.append(
                        ContaminationFinding(
                            path=str(path.relative_to(root)),
                            line=number,
                            canary_digest=hashlib.sha256(canary.encode()).hexdigest(),
                        )
                    )
    return findings


def audit_ground_truth_references(root: Path) -> list[str]:
    """Reject direct public-task references to files under sequestered/vault paths."""
    violations: list[str] = []
    for path in sorted((root / "tasks").rglob("*.yaml")):
        text = path.read_text(encoding="utf-8").casefold()
        if "sequestered/" in text or ".crucible/" in text or "vault.enc" in text:
            violations.append(str(path.relative_to(root)))
    return violations
