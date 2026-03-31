"""Go-to-market launch synthesis."""
from typing import List

from pydantic import BaseModel, Field


class GTMLaunchReport(BaseModel):
    icp_summary: str = Field(description="Ideal customer and pain")
    positioning_one_liner: str = Field(description="Category + differentiation")
    messaging_pillars: List[str] = Field(default_factory=list)
    channel_plan: List[str] = Field(default_factory=list, description="Channel + rough tactic")
    timeline_phases: List[str] = Field(
        default_factory=list,
        description="Phased milestones (e.g. Week 0–2)",
    )
    success_metrics: List[str] = Field(default_factory=list)
    risks_and_dependencies: List[str] = Field(default_factory=list)
    launch_checklist: List[str] = Field(default_factory=list)
