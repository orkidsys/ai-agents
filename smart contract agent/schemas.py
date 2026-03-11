"""
Schemas for smart contract audit reports and findings.
Supports multi-agent intensive auditing with structured severity and categories.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Category(str, Enum):
    """Audit finding categories."""
    REENTRANCY = "reentrancy"
    ACCESS_CONTROL = "access_control"
    ARITHMETIC = "arithmetic_overflow_underflow"
    UNCHECKED_CALLS = "unchecked_external_calls"
    FRONT_RUNNING = "front_running"
    LOGIC = "business_logic"
    GAS = "gas_optimization"
    COMPLIANCE = "compliance_standards"
    UPGRADEABILITY = "upgradeability"
    ORACLE = "oracle_manipulation"
    OTHER = "other"


class Finding(BaseModel):
    """A single audit finding."""
    title: str = Field(description="Short title of the finding")
    severity: Severity = Field(description="Severity level")
    category: Category = Field(description="Finding category")
    description: str = Field(description="Detailed description of the issue")
    location: Optional[str] = Field(None, description="File/contract and line reference (e.g., Token.sol:42)")
    code_snippet: Optional[str] = Field(None, description="Relevant code snippet if applicable")
    recommendation: str = Field(description="Recommended fix or mitigation")
    agent_source: str = Field(description="Which specialist agent reported this (security, logic, gas, compliance)")


class SpecialistReport(BaseModel):
    """Report from one specialist agent."""
    agent_name: str = Field(description="Name of the specialist (security, logic, gas, compliance)")
    findings: List[Finding] = Field(default_factory=list, description="Findings from this agent")
    summary: str = Field(description="Short summary from this agent")
    confidence: str = Field(default="medium", description="Confidence in the audit (low, medium, high)")


class AuditReport(BaseModel):
    """Full audit report aggregating all specialist agents."""
    contract_name: Optional[str] = Field(None, description="Name or path of the audited contract")
    audit_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="When the audit was run"
    )
    specialist_reports: List[SpecialistReport] = Field(
        default_factory=list,
        description="Reports from each specialist agent"
    )
    all_findings: List[Finding] = Field(
        default_factory=list,
        description="Deduplicated and merged findings from all agents"
    )
    executive_summary: str = Field(description="High-level executive summary")
    risk_level: str = Field(description="Overall risk level: critical, high, medium, low")
    recommendations: List[str] = Field(default_factory=list, description="Top-level recommendations")
