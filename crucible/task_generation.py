"""Deterministic procedural variants that preserve declared ground truth."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class AccessLogVariant:
    seed: int
    synthetic_source: str
    lines: tuple[str, ...]
    ground_truth: tuple[str, ...]
    commitment: str


def generate_access_log_variant(seed: int) -> AccessLogVariant:
    rng = random.Random(seed)  # noqa: S311 - deterministic benchmark generation
    source = f"203.0.113.{rng.randint(1, 254)}"
    minute = rng.randint(10, 50)
    lines = (
        f"2026-08-28T12:{minute:02d}:01Z source=192.0.2.10 action=allow resource=/status",
        f"2026-08-28T12:{minute:02d}:04Z source={source} action=deny resource=/admin",
        f"2026-08-28T12:{minute:02d}:07Z source={source} action=deny resource=/admin",
        f"2026-08-28T12:{minute:02d}:12Z source={source} action=allow resource=/admin",
    )
    truth = (f"IOC-{source}", "VERIFY-QUERY")
    canonical = "\n".join(lines + truth).encode()
    return AccessLogVariant(
        seed=seed,
        synthetic_source=source,
        lines=lines,
        ground_truth=truth,
        commitment=hashlib.sha256(canonical).hexdigest(),
    )
