"""STRIDE and threat-modeling references."""
from __future__ import annotations

from langchain_core.tools import tool


@tool
def stride_categories_explainer() -> str:
    """STRIDE mnemonic for threat identification."""
    return (
        "STRIDE:\n"
        "- Spoofing: impersonating users, services, or devices\n"
        "- Tampering: altering data or code in transit/at rest\n"
        "- Repudiation: denying actions without proof\n"
        "- Information disclosure: leaks, overly broad access\n"
        "- Denial of service: availability attacks, resource exhaustion\n"
        "- Elevation of privilege: gaining unauthorized capabilities"
    )


@tool
def trust_boundary_prompts() -> str:
    """Questions to locate trust boundaries."""
    return (
        "Trust boundaries — ask:\n"
        "- Where does untrusted input enter?\n"
        "- Where are authZ checks enforced?\n"
        "- What crosses process / network / org boundaries?\n"
        "- What secrets exist and who can read them?"
    )


def get_threat_model_tools():
    return [stride_categories_explainer, trust_boundary_prompts]
