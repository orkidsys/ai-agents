"""Reference material for ADR workflows."""
from __future__ import annotations

from langchain_core.tools import tool


@tool
def adr_standard_sections() -> str:
    """Classic ADR section order (adapt to your template)."""
    return (
        "Typical ADR sections:\n"
        "1. Title & status\n"
        "2. Context (problem, constraints, drivers)\n"
        "3. Decision (the chosen option)\n"
        "4. Consequences (tradeoffs, operational impact)\n"
        "5. Alternatives considered (with why rejected)\n"
        "Optional: compliance, cost, diagram links, review date."
    )


@tool
def decision_criteria_examples() -> str:
    """Example criteria dimensions for technical decisions."""
    return (
        "Common evaluation dimensions:\n"
        "- Team familiarity / hiring & onboarding\n"
        "- Operational complexity & run cost\n"
        "- Performance & scalability headroom\n"
        "- Security & compliance fit\n"
        "- Vendor lock-in & migration cost\n"
        "- Time-to-value & delivery risk\n"
        "- Observability & incident response"
    )


def get_adr_tools():
    return [adr_standard_sections, decision_criteria_examples]
