"""A minimal ReAct-style agent loop.

The agent is intentionally simple so the *evaluator* gets the spotlight: pick
a tool, run it, optionally pick a second tool, then commit an answer. The
agent is parameterized by a "policy" callable so the same harness can swap in
a mock policy (used in CI) or a real-LLM policy (used in production).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from legal_agent_bench.tools.registry import ToolRegistry
from legal_agent_bench.types import Task, ToolCall, Trajectory

Policy = Callable[[Task, list[ToolCall]], dict[str, str]]


@dataclass
class ReActAgent:
    tools: ToolRegistry
    policy: Policy
    max_steps: int = 4

    def run(self, task: Task) -> Trajectory:
        traj = Trajectory(task_id=task.id)
        for _ in range(self.max_steps):
            action = self.policy(task, traj.steps)
            tool_name = action.get("tool", "")
            if tool_name == "answer":
                traj.final_answer = action.get("answer", "")
                break
            if tool_name == "replan":
                traj.replans += 1
                continue
            try:
                fn = self.tools.get(tool_name)
            except KeyError:
                traj.replans += 1
                continue
            args = {k: v for k, v in action.items() if k != "tool"}
            result, cost = fn(args)
            step = ToolCall(name=tool_name, args=args, result=result, cost_usd=cost)
            traj.steps.append(step)
            traj.total_cost_usd += cost
        return traj
