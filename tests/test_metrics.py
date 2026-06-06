"""Tests for the per-task and aggregate metrics."""

from __future__ import annotations

from legal_agent_bench.judges.council import DEFAULT_COUNCIL, run_council
from legal_agent_bench.metrics.score import aggregate, score_task
from legal_agent_bench.types import Task, TaskKind, ToolCall, Trajectory


def _task() -> Task:
    return Task(
        id="t-1",
        kind=TaskKind.CITATION_LOOKUP,
        question="q",
        ground_truth="answer",
        docs=["d"],
        min_steps=2,
    )


def test_optimal_efficiency_when_steps_match_min() -> None:
    task = _task()
    traj = Trajectory(
        task_id="t-1",
        final_answer="answer",
        steps=[
            ToolCall(name="search", args={}, result=""),
            ToolCall(name="retrieve", args={}, result=""),
        ],
    )
    verdict = run_council(task, traj, DEFAULT_COUNCIL)
    m = score_task(task, traj, verdict)
    assert m.action_efficiency == 1.0


def test_precision_low_when_summarize_repeated() -> None:
    task = _task()
    traj = Trajectory(
        task_id="t-1",
        final_answer="answer",
        steps=[
            ToolCall(name="summarize", args={}, result=""),
            ToolCall(name="summarize", args={}, result=""),
            ToolCall(name="summarize", args={}, result=""),
        ],
    )
    verdict = run_council(task, traj, DEFAULT_COUNCIL)
    m = score_task(task, traj, verdict)
    assert m.tool_call_precision < 0.5


def test_aggregate_handles_empty() -> None:
    assert aggregate([]) == {}
