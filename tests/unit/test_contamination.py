from __future__ import annotations

from pathlib import Path

from crucible.contamination import audit


def test_contamination_audit_reports_digest_not_secret(tmp_path: Path) -> None:
    canary = "HIDDEN-CANARY-1234"
    (tmp_path / "public.txt").write_text(f"leak {canary}", encoding="utf-8")
    findings = audit(tmp_path, [canary])
    assert len(findings) == 1
    assert findings[0].path == "public.txt"
    assert canary not in findings[0].canary_digest
