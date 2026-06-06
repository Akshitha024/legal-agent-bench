"""Tests for the LLM judge council."""

from __future__ import annotations

from legal_agent_bench.judges.council import (
    DEFAULT_COUNCIL,
    lenient_judge,
    run_council,
    strict_judge,
    token_overlap_judge,
)
from legal_agent_bench.types import Task, TaskKind, Trajectory


def _task(answer: str) -> Task:
    return Task(
        id="t-1",
        kind=TaskKind.CITATION_LOOKUP,
        question="q",
        ground_truth=answer,
        docs=["d"],
    )


def test_strict_judge_exact_match() -> None:
    task = _task("Fed. R. Civ. P. 56(a)")
    traj = Trajectory(task_id="t-1", final_answer="Fed. R. Civ. P. 56(a)")
    assert strict_judge(task, traj).correct


def test_lenient_judge_substring() -> None:
    task = _task("Fed. R. Civ. P. 56(a)")
    traj = Trajectory(task_id="t-1", final_answer="frcp 56(a)")
    assert lenient_judge(task, traj).correct is False
    traj2 = Trajectory(task_id="t-1", final_answer="fed. r. civ. p. 56(a) standard")
    assert lenient_judge(task, traj2).correct


def test_token_overlap_threshold() -> None:
    task = _task("duty breach causation damages")
    traj = Trajectory(task_id="t-1", final_answer="duty breach causation damages")
    v = token_overlap_judge(task, traj)
    assert v.correct
    assert 0.99 < v.confidence <= 1.0


def test_council_majority_vote() -> None:
    task = _task("Fed. R. Civ. P. 56(a)")
    traj = Trajectory(task_id="t-1", final_answer="Fed. R. Civ. P. 56(a)")
    result = run_council(task, traj, DEFAULT_COUNCIL)
    assert result.majority_correct
    assert result.agreement >= 0.66
