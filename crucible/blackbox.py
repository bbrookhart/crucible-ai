"""Local sequestered-evaluation primitives: seal, commit, reveal, and verify."""

from __future__ import annotations

import base64
import contextlib
import json
import os
import secrets
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from crucible.evidence import canonical_json, sha256_bytes
from crucible.schemas import Commitment


class BlackboxError(RuntimeError):
    pass


def keygen() -> str:
    return Fernet.generate_key().decode()


def _fernet(key: str | None = None) -> Fernet:
    selected = key or os.getenv("CRUCIBLE_BLACKBOX_KEY")
    if not selected:
        raise BlackboxError("set CRUCIBLE_BLACKBOX_KEY or pass an explicit key")
    try:
        return Fernet(selected.encode())
    except (ValueError, TypeError) as exc:
        raise BlackboxError("invalid BLACKBOX key") from exc


def canonical_task_payload(source: Path) -> bytes:
    source = source.resolve()
    if not source.is_dir():
        raise BlackboxError(f"sequestered source directory does not exist: {source}")
    entries: dict[str, str] = {}
    for path in sorted(item for item in source.rglob("*") if item.is_file()):
        relative = str(path.relative_to(source))
        entries[relative] = base64.b64encode(path.read_bytes()).decode()
    if not entries:
        raise BlackboxError("sequestered source is empty")
    return canonical_json({"format": "crucible-blackbox-v1", "files": entries})


def seal(source: Path, vault: Path, key: str | None = None) -> str:
    plaintext = canonical_task_payload(source)
    ciphertext = _fernet(key).encrypt(plaintext)
    vault.parent.mkdir(parents=True, exist_ok=True)
    vault.write_bytes(ciphertext)
    with contextlib.suppress(OSError):
        vault.chmod(0o600)
    return sha256_bytes(plaintext)


def _decrypt(vault: Path, key: str | None = None) -> bytes:
    try:
        return _fernet(key).decrypt(vault.read_bytes())
    except (InvalidToken, OSError) as exc:
        raise BlackboxError("vault could not be decrypted") from exc


def commit(
    vault: Path,
    commitment_path: Path,
    *,
    environment_hash: str,
    scoring_hash: str,
    key: str | None = None,
) -> Commitment:
    plaintext = _decrypt(vault, key)
    fields = {
        "task_set_hash": sha256_bytes(plaintext),
        "environment_hash": environment_hash,
        "scoring_hash": scoring_hash,
    }
    commitment = Commitment(
        task_set_hash=fields["task_set_hash"],
        environment_hash=fields["environment_hash"],
        scoring_hash=fields["scoring_hash"],
        commitment_hash=sha256_bytes(canonical_json(fields)),
    )
    commitment_path.parent.mkdir(parents=True, exist_ok=True)
    commitment_path.write_bytes(canonical_json(commitment.model_dump(mode="json")) + b"\n")
    return commitment


def reveal(vault: Path, destination: Path, key: str | None = None) -> str:
    plaintext = _decrypt(vault, key)
    payload = json.loads(plaintext)
    destination.mkdir(parents=True, exist_ok=False)
    for relative, encoded in payload["files"].items():
        target = (destination / relative).resolve()
        if not target.is_relative_to(destination.resolve()):
            raise BlackboxError("vault entry attempts path traversal")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(encoded))
    return sha256_bytes(plaintext)


def verify(
    vault: Path,
    commitment_path: Path,
    *,
    environment_hash: str | None = None,
    scoring_hash: str | None = None,
    key: str | None = None,
) -> tuple[bool, list[str]]:
    commitment = Commitment.model_validate_json(commitment_path.read_text(encoding="utf-8"))
    plaintext = _decrypt(vault, key)
    errors: list[str] = []
    if sha256_bytes(plaintext) != commitment.task_set_hash:
        errors.append("task-set hash mismatch")
    if environment_hash is not None and environment_hash != commitment.environment_hash:
        errors.append("environment hash mismatch")
    if scoring_hash is not None and scoring_hash != commitment.scoring_hash:
        errors.append("scoring hash mismatch")
    fields = {
        "task_set_hash": commitment.task_set_hash,
        "environment_hash": commitment.environment_hash,
        "scoring_hash": commitment.scoring_hash,
    }
    if sha256_bytes(canonical_json(fields)) != commitment.commitment_hash:
        errors.append("commitment hash mismatch")
    return not errors, errors


def ephemeral_reveal(
    vault: Path, key: str | None = None
) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix=f"crucible-{secrets.token_hex(4)}-")
    destination = Path(temporary.name) / "tasks"
    reveal(vault, destination, key)
    return temporary, destination
