"""Structured schema for triage output."""
from typing import List, Literal

from pydantic import BaseModel, Field


class EmailTriageReply(BaseModel):
    category: str = Field(description="Intent category for routing")
    priority: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Suggested reply urgency",
    )
    reply_draft: str = Field(description="Draft response to sender")
    next_actions: List[str] = Field(
        default_factory=list,
        description="Suggested next steps for the recipient",
    )
