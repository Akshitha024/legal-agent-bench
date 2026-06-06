"""Policies the ReAct agent can use.

The mock policy follows a deterministic search -> answer pattern. It is the
policy used in CI so the test suite is hermetic; a real-LLM policy lives
behind an `if os.getenv('ANTHROPIC_API_KEY')` switch in the runner.
"""

from __future__ import annotations

from legal_agent_bench.types import Task, ToolCall

ACTION_SEARCH = "search"
ACTION_ANSWER = "answer"


def mock_policy(task: Task, steps: list[ToolCall]) -> dict[str, str]:
    """Search first, then answer using the ground truth (CI determinism)."""
    if not steps:
        return {"tool": ACTION_SEARCH, "query": task.question[:64]}
    return {"tool": ACTION_ANSWER, "answer": task.ground_truth}


_REPLAN_BUDGET: dict[str, int] = {}


def confused_policy(task: Task, steps: list[ToolCall]) -> dict[str, str]:
    """A policy that takes too many steps and replans once.

    Used in the test suite to exercise the action-efficiency and replan-rate
    metrics so they aren't dead code. The replan budget is per-task; once
    exhausted, the policy makes progress.
    """
    n = len(steps)
    if n == 0:
        return {"tool": ACTION_SEARCH, "query": task.question[:32]}
    if n == 1 and _REPLAN_BUDGET.get(task.id, 0) < 1:
        _REPLAN_BUDGET[task.id] = _REPLAN_BUDGET.get(task.id, 0) + 1
        return {"tool": "replan"}
    if n == 1:
        return {"tool": "retrieve", "idx": "0"}
    return {"tool": ACTION_ANSWER, "answer": task.ground_truth}
