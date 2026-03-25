"""Optional structured reply shape when the model returns JSON."""
from typing import List, Optional

from pydantic import BaseModel, Field


class AssistantReply(BaseModel):
    """Structured answer the LLM may echo in JSON for downstream use."""

    summary: str = Field(description="Short answer to the user")
    reasoning_brief: Optional[str] = Field(
        default=None,
        description="Optional one-line rationale",
    )
    bullet_points: List[str] = Field(
        default_factory=list,
        description="Optional supporting bullets",
    )
    suggested_follow_up: Optional[str] = Field(
        default=None,
        description="One optional follow-up question or task",
    )
