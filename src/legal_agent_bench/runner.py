"""End-to-end pipeline: tasks -> agent -> council -> metrics -> charts."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from legal_agent_bench.agent.policies import mock_policy
from legal_agent_bench.agent.react import ReActAgent
from legal_agent_bench.judges.council import DEFAULT_COUNCIL, run_council
from legal_agent_bench.metrics.score import TaskMetrics, aggregate, score_task
from legal_agent_bench.tasks.synthetic import synthesize
from legal_agent_bench.tools.registry import default_registry
from legal_agent_bench.types import CouncilResult, Trajectory
from legal_agent_bench.viz.charts import (
    cost_breakdown_stack,
    efficiency_vs_cost_scatter,
    judge_agreement_hist,
    replan_rate_box,
    success_by_kind_bar,
)


def run(out_dir: Path, n_per_kind: int = 10, seed: int = 17) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    figs = Path("results/figures")

    tasks = synthesize(n_per_kind=n_per_kind, seed=seed)
    corpus: list[str] = []
    for t in tasks:
        corpus.extend(t.docs)
    registry = default_registry(corpus)
    agent = ReActAgent(tools=registry, policy=mock_policy)

    rows: list[TaskMetrics] = []
    trajs: list[Trajectory] = []
    verdicts: list[CouncilResult] = []
    for t in tasks:
        traj = agent.run(t)
        verdict = run_council(t, traj, DEFAULT_COUNCIL)
        rows.append(score_task(t, traj, verdict))
        trajs.append(traj)
        verdicts.append(verdict)

    success_by_kind_bar(rows, figs / "success_by_kind.png")
    efficiency_vs_cost_scatter(rows, figs / "efficiency_vs_cost.png")
    judge_agreement_hist(verdicts, figs / "judge_agreement.png")
    replan_rate_box(rows, figs / "replan_rate.png")
    cost_breakdown_stack(rows, figs / "cost_breakdown.png")

    agg = aggregate(rows)
    summary = {
        "aggregate": agg,
        "n_tasks": len(rows),
        "per_task": [asdict(r) for r in rows],
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    return summary
