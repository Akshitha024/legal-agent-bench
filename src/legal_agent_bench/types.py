"""Task, trajectory, and judging types."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class TaskKind(StrEnum):
    """The four LegalBench-style task families this benchmark covers."""

    HOLDING_SELECTION = "holding_selection"
    CITATION_LOOKUP = "citation_lookup"
    RULE_APPLICATION = "rule_application"
    CONTRACT_QA = "contract_qa"


class Task(BaseModel):
    id: str
    kind: TaskKind
    question: str
    ground_truth: str
    docs: list[str] = Field(default_factory=list)
    min_steps: int = Field(default=2, ge=1)


class ToolCall(BaseModel):
    name: str
    args: dict[str, str]
    result: str
    cost_usd: float = 0.0


class Trajectory(BaseModel):
    task_id: str
    steps: list[ToolCall] = Field(default_factory=list)
    final_answer: str = ""
    replans: int = 0
    total_cost_usd: float = 0.0


class JudgeVerdict(BaseModel):
    judge_name: str
    correct: bool
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    rationale: str = ""


class CouncilResult(BaseModel):
    task_id: str
    verdicts: list[JudgeVerdict]
    majority_correct: bool
    agreement: float = Field(ge=0.0, le=1.0)
