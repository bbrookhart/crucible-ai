"""Validate required documentation without external link crawling."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "SECURITY.md",
    "docs/research-question.md",
    "docs/architecture.md",
    "docs/threat-model.md",
    "docs/evaluation-methodology.md",
    "docs/blackbox-design.md",
    "docs/research-integrity.md",
    "docs/reviewer-guide.md",
    "docs/CRUCIBLE-whitepaper.md",
]
missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
if missing:
    raise SystemExit(f"missing required documentation: {', '.join(missing)}")
empty = [name for name in REQUIRED if not (ROOT / name).read_text(encoding="utf-8").strip()]
if empty:
    raise SystemExit(f"empty documentation: {', '.join(empty)}")
print(f"documentation check passed: {len(REQUIRED)} required files")
