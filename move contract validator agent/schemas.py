"""
Schemas for Move contract validation across multiple specialist agents (Aptos / Sui aware).
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Category(str, Enum):
    """Move-focused finding categories."""

    RESOURCE_SAFETY = "resource_safety"
    ACCESS_CONTROL = "access_control"
    ABORT_INVARIANT = "abort_invariant"
    GAS_STORAGE = "gas_storage"
    STANDARDS = "standards_compliance"
    OTHER = "other"


class Finding(BaseModel):
    title: str = Field(description="Short title")
    severity: Severity = Field(description="Severity")
    category: Category = Field(description="Category")
    description: str = Field(description="Explanation")
    location: Optional[str] = Field(None, description="Module::function or file:line")
    code_snippet: Optional[str] = Field(None)
    recommendation: str = Field(description="Fix or mitigation")
    agent_source: str = Field(description="Specialist id (security, logic, gas, compliance)")


class SpecialistReport(BaseModel):
    agent_name: str = Field(description="security | logic | gas | compliance")
    findings: List[Finding] = Field(default_factory=list)
    summary: str = Field(description="Short summary")
    confidence: str = Field(default="medium", description="low | medium | high")


class MoveValidationReport(BaseModel):
    contract_name: Optional[str] = None
    chain_hint: Optional[str] = Field(
        None,
        description="aptos | sui | unknown — best-effort from user or heuristics",
    )
    validation_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
    )
    specialist_reports: List[SpecialistReport] = Field(default_factory=list)
    all_findings: List[Finding] = Field(default_factory=list)
    executive_summary: str = ""
    risk_level: str = Field(description="critical | high | medium | low")
    recommendations: List[str] = Field(default_factory=list)
