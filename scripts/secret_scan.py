"""Fail CI on common credential assignments in tracked project text."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"gh[opusr]_[A-Za-z0-9_]{36,}"),
]
git = shutil.which("git")
if git is None:
    raise SystemExit("git is required for the tracked-file secret scan")
tracked = subprocess.run(  # noqa: S603 - fixed executable resolved with shutil.which
    [git, "ls-files"],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
findings: list[str] = []
for relative in tracked:
    path = ROOT / relative
    if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".pdf", ".woff"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if any(pattern.search(text) for pattern in PATTERNS):
        findings.append(relative)
if findings:
    raise SystemExit(f"possible secrets in tracked files: {', '.join(findings)}")
print(f"secret scan passed: {len(tracked)} tracked paths")
