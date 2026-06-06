"""Karpathy-style LLM judge council.

We run N judges over each (task, trajectory) pair and report (a) per-judge
verdicts, (b) majority correctness, (c) inter-judge agreement. The judges in
this file are deterministic mocks; production swap-in would replace each with
a real model adapter behind the same `Judge` protocol.
"""

from __future__ import annotations

from collections.abc import Callable

from legal_agent_bench.types import CouncilResult, JudgeVerdict, Task, Trajectory

Judge = Callable[[Task, Trajectory], JudgeVerdict]


def strict_judge(task: Task, traj: Trajectory) -> JudgeVerdict:
    """Exact-string judge (the most pessimistic)."""
    correct = traj.final_answer.strip() == task.ground_truth.strip()
    return JudgeVerdict(judge_name="strict", correct=correct, confidence=0.95)


def lenient_judge(task: Task, traj: Trajectory) -> JudgeVerdict:
    """Lowercased-substring judge (the most optimistic)."""
    pred = traj.final_answer.lower().strip()
    gt = task.ground_truth.lower().strip()
    correct = bool(pred) and (pred in gt or gt in pred)
    return JudgeVerdict(judge_name="lenient", correct=correct, confidence=0.7)


def token_overlap_judge(task: Task, traj: Trajectory) -> JudgeVerdict:
    """Token-overlap judge (>= 0.5 Jaccard => correct)."""
    pred_toks = set(traj.final_answer.lower().split())
    gt_toks = set(task.ground_truth.lower().split())
    if not pred_toks or not gt_toks:
        return JudgeVerdict(judge_name="token_overlap", correct=False, confidence=0.5)
    inter = pred_toks & gt_toks
    union = pred_toks | gt_toks
    jacc = len(inter) / len(union) if union else 0.0
    return JudgeVerdict(judge_name="token_overlap", correct=jacc >= 0.5, confidence=float(jacc))


def run_council(task: Task, traj: Trajectory, judges: list[Judge]) -> CouncilResult:
    """Run every judge in `judges` over (task, traj) and reduce to a verdict."""
    verdicts = [j(task, traj) for j in judges]
    yes = sum(1 for v in verdicts if v.correct)
    n = len(verdicts)
    majority = yes > n / 2 if n else False
    agreement = max(yes, n - yes) / n if n else 0.0
    return CouncilResult(
        task_id=task.id,
        verdicts=verdicts,
        majority_correct=majority,
        agreement=agreement,
    )


DEFAULT_COUNCIL: list[Judge] = [strict_judge, lenient_judge, token_overlap_judge]
