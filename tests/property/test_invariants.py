from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from crucible.blackbox import canonical_task_payload
from crucible.metrics import pass_at_k
from crucible.task_generation import generate_access_log_variant


@given(st.integers(min_value=1, max_value=10_000))
def test_procedural_variant_is_deterministic(seed: int) -> None:
    assert generate_access_log_variant(seed) == generate_access_log_variant(seed)


@given(
    n=st.integers(min_value=1, max_value=100),
    ratio=st.floats(min_value=0, max_value=1, allow_nan=False),
)
def test_pass_at_one_is_bounded(n: int, ratio: float) -> None:
    c = min(n, round(n * ratio))
    value = pass_at_k(n, c, 1)
    assert 0 <= value <= 1


def test_task_commitment_changes_with_hidden_task(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    task = source / "task.txt"
    task.write_text("version one", encoding="utf-8")
    first = canonical_task_payload(source)
    task.write_text("version two", encoding="utf-8")
    second = canonical_task_payload(source)
    assert first != second
