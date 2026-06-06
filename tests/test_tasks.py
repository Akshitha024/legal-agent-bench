"""Tests for the synthetic task generator."""

from __future__ import annotations

from legal_agent_bench.tasks.synthetic import synthesize
from legal_agent_bench.types import TaskKind


def test_default_emits_correct_count() -> None:
    tasks = synthesize(n_per_kind=5, seed=7)
    assert len(tasks) == 5 * len(list(TaskKind))


def test_task_ids_unique() -> None:
    tasks = synthesize(n_per_kind=8, seed=11)
    assert len({t.id for t in tasks}) == len(tasks)


def test_each_kind_present() -> None:
    tasks = synthesize(n_per_kind=3)
    kinds = {t.kind for t in tasks}
    assert kinds == set(TaskKind)


def test_each_task_has_at_least_one_doc() -> None:
    for t in synthesize(n_per_kind=5):
        assert len(t.docs) >= 1
