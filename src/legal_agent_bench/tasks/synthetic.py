"""Synthetic LegalBench-style tasks.

We synthesize 40 tasks across the four task families so the rest of the
toolkit can be exercised offline. Each task has a deterministic ground-truth
answer and a small document corpus the agent must navigate.
"""

from __future__ import annotations

import random

from legal_agent_bench.types import Task, TaskKind

_TASK_TEMPLATES: dict[TaskKind, list[tuple[str, str, list[str]]]] = {
    TaskKind.HOLDING_SELECTION: [
        (
            "What was the holding in Marbury v. Madison regarding judicial review?",
            "The Supreme Court has the power to declare acts of Congress unconstitutional.",
            ["Marbury v. Madison, 5 U.S. 137 (1803): established judicial review."],
        ),
        (
            "What did Brown v. Board hold about segregated public schools?",
            "Separate educational facilities are inherently unequal.",
            ["Brown v. Board of Education, 347 U.S. 483 (1954)."],
        ),
    ],
    TaskKind.CITATION_LOOKUP: [
        (
            "Cite the standard for summary judgment under FRCP 56.",
            "Fed. R. Civ. P. 56(a)",
            ["FRCP 56(a): a party may move for summary judgment, identifying each claim..."],
        ),
        (
            "Cite the federal rule governing relevance of evidence.",
            "Fed. R. Evid. 401",
            ["FRE 401 defines relevant evidence."],
        ),
    ],
    TaskKind.RULE_APPLICATION: [
        (
            "Apply the four-element negligence test to a driver running a red light.",
            "duty, breach, causation, damages all satisfied",
            ["Restatement (Second) of Torts § 281: duty, breach, causation, damages."],
        ),
        (
            "Does an oral promise to convey land satisfy the statute of frauds?",
            "no, the statute of frauds requires a writing",
            ["Statute of Frauds (UCC 2-201): writing required for sale of land."],
        ),
    ],
    TaskKind.CONTRACT_QA: [
        (
            "Identify the choice-of-law clause in this contract: 'This Agreement shall be "
            "governed by the laws of Delaware.'",
            "Delaware",
            ["Choice-of-law clauses bind the parties to a chosen jurisdiction."],
        ),
        (
            "Identify the term of this NDA: 'This Agreement remains in effect for 3 years.'",
            "3 years",
            ["NDAs typically specify a definite term."],
        ),
    ],
}


def synthesize(n_per_kind: int = 10, seed: int = 17) -> list[Task]:
    """Emit `n_per_kind * 4` tasks. Each task is a perturbed template instance."""
    rng = random.Random(seed)
    tasks: list[Task] = []
    counter = 0
    for kind, templates in _TASK_TEMPLATES.items():
        for i in range(n_per_kind):
            q, a, docs = templates[i % len(templates)]
            task_id = f"task-{counter:04d}"
            tasks.append(
                Task(
                    id=task_id,
                    kind=kind,
                    question=q,
                    ground_truth=a,
                    docs=[*docs, _distractor_doc(rng, i)],
                    min_steps=rng.choice([2, 2, 3]),
                )
            )
            counter += 1
    return tasks


def _distractor_doc(rng: random.Random, idx: int) -> str:
    """A randomly chosen unrelated document to test retrieval precision."""
    distractors = [
        "Internal Revenue Code section 501(c)(3): tax-exempt organizations.",
        "Hadley v. Baxendale (1854): contract damages must be foreseeable.",
        "Erie R.R. v. Tompkins (1938): federal courts apply state law.",
        "Younger v. Harris (1971): federal courts abstain from state cases.",
        "Chevron v. NRDC (1984): agency interpretation deference.",
    ]
    return distractors[(idx + rng.randint(0, 4)) % len(distractors)]
