"""Structured ADR output from final synthesis phase."""
from typing import List

from pydantic import BaseModel, Field


class ADRReport(BaseModel):
    title: str = Field(description="ADR title, e.g. 0001-use-postgres")
    status: str = Field(
        default="proposed",
        description="proposed | accepted | deprecated | superseded (model may vary)",
    )
    context: str = Field(description="Problem, forces, constraints, links")
    decision: str = Field(description="What we decided and why (concise)")
    consequences: List[str] = Field(default_factory=list, description="Positive and negative")
    alternatives_considered: List[str] = Field(default_factory=list)
    evaluation_criteria: List[str] = Field(
        default_factory=list,
        description="Criteria used to compare options",
    )
    risks_and_mitigations: List[str] = Field(default_factory=list)
    follow_up_actions: List[str] = Field(default_factory=list)
