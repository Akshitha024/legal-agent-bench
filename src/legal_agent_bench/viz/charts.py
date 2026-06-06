"""Five distinct chart families for the agent benchmark."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from legal_agent_bench.metrics.score import TaskMetrics
from legal_agent_bench.types import CouncilResult


def _save(fig: Figure, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


def success_by_kind_bar(rows: list[TaskMetrics], out: Path) -> Path:
    by_kind: dict[str, list[int]] = {}
    for r in rows:
        by_kind.setdefault(r.kind, []).append(int(r.success))
    kinds = sorted(by_kind)
    rates = [sum(by_kind[k]) / len(by_kind[k]) for k in kinds]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(kinds, rates, color="#3b6fa1")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("success rate")
    ax.set_title("Success rate by task family")
    for xi, rate in enumerate(rates):
        ax.text(xi, rate + 0.02, f"{rate:.0%}", ha="center", fontsize=9)
    return _save(fig, out)


def efficiency_vs_cost_scatter(rows: list[TaskMetrics], out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    xs = [r.action_efficiency for r in rows]
    ys = [r.cost_usd * 1000 for r in rows]
    colors = ["#5b8d4a" if r.success else "#c25a4f" for r in rows]
    ax.scatter(xs, ys, c=colors, alpha=0.7)
    ax.set_xlabel("action efficiency (min/actual)")
    ax.set_ylabel("cost per task (USD x1000)")
    ax.set_title("Efficiency vs cost (green=correct, red=wrong)")
    return _save(fig, out)


def judge_agreement_hist(verdicts: list[CouncilResult], out: Path) -> Path:
    vals = [c.agreement for c in verdicts]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(vals, bins=[0.5, 0.66, 0.83, 1.0], color="#5b8d4a", edgecolor="white")
    ax.set_xlabel("inter-judge agreement")
    ax.set_ylabel("tasks")
    ax.set_title("Judge-council agreement distribution")
    return _save(fig, out)


def replan_rate_box(rows: list[TaskMetrics], out: Path) -> Path:
    by_kind: dict[str, list[float]] = {}
    for r in rows:
        by_kind.setdefault(r.kind, []).append(r.replan_rate)
    kinds = sorted(by_kind)
    data = [by_kind[k] for k in kinds]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot(data, tick_labels=kinds)
    ax.set_ylabel("replan rate")
    ax.set_title("Replan rate by task family")
    return _save(fig, out)


def cost_breakdown_stack(rows: list[TaskMetrics], out: Path) -> Path:
    counts = Counter(r.kind for r in rows)
    kinds = sorted(counts)
    costs = [sum(r.cost_usd for r in rows if r.kind == k) for k in kinds]
    fig, ax = plt.subplots(figsize=(7, 4))
    x = np.arange(len(kinds))
    ax.bar(x, costs, color="#c25a4f")
    ax.set_xticks(x)
    ax.set_xticklabels(kinds)
    ax.set_ylabel("total USD")
    ax.set_title("Total cost by task family")
    for xi, c in zip(x, costs, strict=True):
        ax.text(float(xi), c, f"${c:.4f}", ha="center", va="bottom", fontsize=9)
    return _save(fig, out)
