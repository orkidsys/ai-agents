"""Structured schema for interview prep output."""
from typing import List

from pydantic import BaseModel, Field


class InterviewReply(BaseModel):
    question_type: str = Field(description="behavioral, system_design, technical_coding, etc.")
    sample_answer_bullets: List[str] = Field(
        default_factory=list,
        description="Memorizable bullets or STAR sections",
    )
    follow_up_drills: List[str] = Field(
        default_factory=list,
        description="Extra questions to practice",
    )
    tips: List[str] = Field(default_factory=list, description="Delivery and framing tips")
