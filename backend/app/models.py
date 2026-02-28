from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class IssueType(str, Enum):
    BUG = "Bug"
    TASK = "Task"
    STORY = "Story"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Estimate(str, Enum):
    S = "S"
    M = "M"
    L = "L"


class GenerateRequest(BaseModel):
    ticket_details: str = Field(..., min_length=1)
    issue_type: IssueType = IssueType.TASK
    priority: Priority = Priority.MEDIUM
    project_key: Optional[str] = None
    labels: Optional[str] = None

    @field_validator("ticket_details")
    @classmethod
    def validate_ticket_details(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("ticket_details must not be empty")
        return stripped


class TicketDescription(BaseModel):
    problem: str
    proposed_solution: str
    notes: str


class GenerateResponse(BaseModel):
    title: str
    issue_type: IssueType
    priority: Priority
    project_key: Optional[str] = None
    description: TicketDescription
    acceptance_criteria: list[str]
    definition_of_done: list[str]
    labels: list[str]
    estimate: Estimate
    assumptions: list[str]
