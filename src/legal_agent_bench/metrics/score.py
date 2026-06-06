"""Per-trajectory and aggregate metrics.

Five distinct metrics are reported:

  - task_success: did the council vote correct?
  - action_efficiency: min_steps / actual_steps (>= 1.0 means optimal)
  - tool_call_precision: # tool calls inferred to be necessary / total
  - cost_per_task: USD spent across all tool calls
  - replan_rate: # replans / steps
"""

from __future__ import annotations

from dataclasses import dataclass

from legal_agent_bench.types import CouncilResult, Task, Trajectory


@dataclass
class TaskMetrics:
    task_id: str
    kind: str
    success: bool
    action_efficiency: float
    tool_call_precision: float
    cost_usd: float
    replan_rate: float


def _necessary_tool_calls(traj: Trajectory) -> int:
    """Heuristic: any tool call whose name is in {search, retrieve} counts as
    necessary; summarize / citation_check beyond two calls is treated as bloat.
    """
    necessary = 0
    summaries = 0
    cite_checks = 0
    for step in traj.steps:
        if step.name in ("search", "retrieve"):
            necessary += 1
        elif step.name == "summarize":
            summaries += 1
            if summaries <= 1:
                necessary += 1
        elif step.name == "citation_check":
            cite_checks += 1
            if cite_checks <= 1:
                necessary += 1
    return necessary


def score_task(task: Task, traj: Trajectory, verdict: CouncilResult) -> TaskMetrics:
    n_steps = max(1, len(traj.steps))
    eff = task.min_steps / n_steps
    necessary = _necessary_tool_calls(traj)
    precision = necessary / n_steps if n_steps else 0.0
    replan_rate = traj.replans / n_steps if n_steps else 0.0
    return TaskMetrics(
        task_id=task.id,
        kind=task.kind.value,
        success=verdict.majority_correct,
        action_efficiency=eff,
        tool_call_precision=precision,
        cost_usd=traj.total_cost_usd,
        replan_rate=replan_rate,
    )


def aggregate(rows: list[TaskMetrics]) -> dict[str, float]:
    if not rows:
        return {}
    n = len(rows)
    return {
        "n": float(n),
        "success_rate": sum(r.success for r in rows) / n,
        "mean_action_efficiency": sum(r.action_efficiency for r in rows) / n,
        "mean_tool_call_precision": sum(r.tool_call_precision for r in rows) / n,
        "mean_cost_per_task": sum(r.cost_usd for r in rows) / n,
        "mean_replan_rate": sum(r.replan_rate for r in rows) / n,
    }
