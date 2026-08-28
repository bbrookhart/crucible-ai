"""Reproducible container policy construction for S2/S3 tasks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SandboxPolicy:
    network: str = "none"
    read_only: bool = True
    memory: str = "512m"
    cpus: str = "1.0"
    pids_limit: int = 128
    user: str = "65534:65534"


class DockerSandboxManager:
    def build_run_command(
        self, image_digest: str, policy: SandboxPolicy | None = None
    ) -> list[str]:
        selected = policy or SandboxPolicy()
        if "@sha256:" not in image_digest:
            raise ValueError("sandbox images must be pinned by digest")
        command = [
            "docker",
            "run",
            "--rm",
            f"--network={selected.network}",
            f"--memory={selected.memory}",
            f"--cpus={selected.cpus}",
            f"--pids-limit={selected.pids_limit}",
            f"--user={selected.user}",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges",
        ]
        if selected.read_only:
            command.append("--read-only")
        command.append(image_digest)
        return command
