"""Smoke test for the end-to-end runner."""

from __future__ import annotations

from pathlib import Path

from legal_agent_bench.runner import run


def test_runner_smoke(tmp_path: Path) -> None:
    summary = run(tmp_path / "out", n_per_kind=3, seed=1)
    assert summary["n_tasks"] == 12
    agg = summary["aggregate"]
    assert isinstance(agg, dict)
    assert 0.0 <= agg["success_rate"] <= 1.0  # type: ignore[index]
    assert (tmp_path / "out" / "summary.json").exists()
