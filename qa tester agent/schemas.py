"""
Structured response schemas for the QA Tester Agent.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class TestCase(BaseModel):
    """A single test case definition."""
    id: Optional[str] = Field(
        default=None,
        description="Optional identifier for the test case (e.g. TC_LOGIN_001).",
    )
    title: str = Field(description="Short, clear description of what is being tested.")
    type: str = Field(
        description="Type of test case (e.g. 'positive', 'negative', 'edge', 'regression').",
    )
    preconditions: Optional[str] = Field(
        default=None,
        description="Setup or state required before executing the test.",
    )
    steps: List[str] = Field(
        default_factory=list,
        description="Ordered list of human-readable test steps.",
    )
    expected_result: str = Field(
        description="Expected outcome of the test case if the system behaves correctly.",
    )
    priority: Optional[str] = Field(
        default=None,
        description="Optional priority (e.g. 'P0', 'P1', 'high', 'medium', 'low').",
    )


class TestFileChange(BaseModel):
    """Represents a created or updated test file."""
    path: str = Field(description="Path to the test file, relative to workspace root.")
    action: str = Field(description="'created' or 'modified'.")
    framework: Optional[str] = Field(
        default=None,
        description="Testing framework used (e.g. 'jest', 'vitest', 'cypress', 'playwright', 'pytest').",
    )
    summary: Optional[str] = Field(
        default=None,
        description="Brief description of what tests are in this file.",
    )


class QATaskResponse(BaseModel):
    """Structured response for a QA testing task."""
    task_summary: str = Field(
        description="One-line summary of what testing work was proposed or implemented.",
    )
    area_under_test: str = Field(
        description="Feature, module, or user flow under test (e.g. 'login', 'checkout').",
    )
    strategy_summary: str = Field(
        description="High-level summary of the test approach, risks, and coverage focus.",
    )
    test_cases: List[TestCase] = Field(
        default_factory=list,
        description="List of key test cases (scenarios) designed for this task.",
    )
    test_files: List[TestFileChange] = Field(
        default_factory=list,
        description="Test files that were created or modified as part of this task.",
    )
    next_steps: Optional[List[str]] = Field(
        default=None,
        description=(
            "Optional suggested next steps (e.g. run npm test, integrate into CI, "
            "expand coverage to specific edge cases)."
        ),
    )

