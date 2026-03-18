"""
Pydantic schemas for wallet poisoning agent responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AddressCheckResult(BaseModel):
    """Result of comparing two addresses for poisoning risk."""
    addresses_valid: bool = Field(description="Whether both addresses were valid EVM format")
    identical: bool = Field(description="True if the two addresses are the same")
    prefix_match_chars: int = Field(description="Number of matching characters at the start")
    suffix_match_chars: int = Field(description="Number of matching characters at the end")
    risk_note: Optional[str] = Field(None, description="Warning if lookalike/poisoning risk detected")
    recommendation: str = Field(description="Short recommendation (e.g. verify full address)")


class WalletPoisoningReport(BaseModel):
    """Structured report for wallet poisoning education or risk assessment."""
    topic: str = Field(description="Topic of the query (e.g. 'Address poisoning', 'Risk check')")
    summary: str = Field(description="Clear summary of what wallet poisoning is or what was found")
    key_points: List[str] = Field(default_factory=list, description="Bullet points or key facts")
    risk_level: Optional[str] = Field(
        None,
        description="If applicable: 'low', 'medium', 'high', or 'none'"
    )
    address_analysis: Optional[AddressCheckResult] = Field(
        None,
        description="If user compared two addresses, the analysis result"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable steps to stay safe"
    )
    disclaimer: str = Field(
        default="This is for educational purposes. Always verify addresses through trusted sources.",
        description="Short disclaimer"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the report was generated"
    )
