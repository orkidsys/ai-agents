"""Structured schema for documentation outputs."""
from typing import List

from pydantic import BaseModel, Field


class DocReply(BaseModel):
    title: str = Field(description="Working title for the document or section")
    doc_type: str = Field(description="readme, api, runbook, changelog, adr, or other")
    outline: List[str] = Field(default_factory=list, description="Section headings or plan")
    draft_markdown: str = Field(description="Primary markdown draft")
    review_checklist: List[str] = Field(
        default_factory=list,
        description="Items to verify before publishing",
    )
