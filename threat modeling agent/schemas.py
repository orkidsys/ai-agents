"""Threat model synthesis output."""
from typing import List

from pydantic import BaseModel, Field


class ThreatRow(BaseModel):
    component: str = Field(default="", description="System part or flow")
    stride_category: str = Field(default="", description="S|T|R|I|D|E or spelled out")
    threat_statement: str = Field(default="", description="What could go wrong")
    mitigation: str = Field(default="", description="Control or design change")
    priority: str = Field(default="", description="P0–P3 or high/medium/low")


class ThreatModelReport(BaseModel):
    scope_summary: str = Field(description="System boundary and data summary")
    assumptions: List[str] = Field(default_factory=list)
    threats: List[ThreatRow] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
