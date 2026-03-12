"""
Structured response schemas for the Frontend Developer Agent.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class FileChange(BaseModel):
    """A file that was created or modified."""
    path: str = Field(description="Path relative to workspace")
    action: str = Field(description="'created' or 'modified'")
    summary: Optional[str] = Field(default=None, description="Brief description of the change")


class FrontendTaskResponse(BaseModel):
    """Structured response for a frontend implementation task."""
    task_summary: str = Field(description="One-line summary of what was done")
    files_changed: List[FileChange] = Field(
        default_factory=list,
        description="List of files created or modified"
    )
    explanation: str = Field(description="Brief explanation of the implementation and any trade-offs")
    next_steps: Optional[List[str]] = Field(
        default=None,
        description="Optional follow-up steps (e.g. run npm install, test in browser)"
    )
