"""Tests for the ReAct agent loop + mock/confused policies."""

from __future__ import annotations

from legal_agent_bench.agent.policies import confused_policy, mock_policy
from legal_agent_bench.agent.react import ReActAgent
from legal_agent_bench.tasks.synthetic import synthesize
from legal_agent_bench.tools.registry import default_registry


def test_mock_policy_takes_two_steps() -> None:
    tasks = synthesize(n_per_kind=2, seed=3)
    corpus: list[str] = []
    for t in tasks:
        corpus.extend(t.docs)
    agent = ReActAgent(tools=default_registry(corpus), policy=mock_policy)
    traj = agent.run(tasks[0])
    assert len(traj.steps) == 1
    assert traj.final_answer == tasks[0].ground_truth


def test_confused_policy_replans() -> None:
    tasks = synthesize(n_per_kind=2, seed=3)
    corpus: list[str] = []
    for t in tasks:
        corpus.extend(t.docs)
    agent = ReActAgent(tools=default_registry(corpus), policy=confused_policy)
    traj = agent.run(tasks[0])
    assert traj.replans >= 1
    assert traj.final_answer == tasks[0].ground_truth


def test_total_cost_accumulates() -> None:
    tasks = synthesize(n_per_kind=2, seed=3)
    corpus: list[str] = []
    for t in tasks:
        corpus.extend(t.docs)
    agent = ReActAgent(tools=default_registry(corpus), policy=mock_policy)
    traj = agent.run(tasks[0])
    assert traj.total_cost_usd > 0
