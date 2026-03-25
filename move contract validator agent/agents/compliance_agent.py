"""
Move standards & compliance: module layout, naming, docs, framework idioms (Aptos / Sui).
"""
import os
import sys

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

_AGENT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _AGENT_ROOT not in sys.path:
    sys.path.insert(0, _AGENT_ROOT)

from agents.base_parse import parse_specialist_json
from schemas import SpecialistReport


class MoveComplianceValidator:
    """Focus: standards, documentation, error codes, framework best practices."""

    SYSTEM_PROMPT = """You are an expert Move reviewer for standards, documentation, and ecosystem conventions (Aptos / Sui).

Check:

1. MODULE STRUCTURE: friend / public(friend) usage, test-only code separation, entry function naming.
2. ERRORS: Consistent `abort` codes, user-facing error mapping where applicable.
3. DOCUMENTATION: Missing `///` doc comments on public functions and structs.
4. FRAMEWORK USAGE: Correct use of `coin`, `fungible_asset`, `object`, `transfer` patterns per chain docs.
5. UPGRADE / PACKAGE: Comments on upgrade policy if visible; dependency pinning awareness.

Category must be one of: resource_safety, access_control, abort_invariant, gas_storage, standards_compliance, other.

Respond with JSON only:
{
  "findings": [ { "title", "severity", "category", "description", "location", "code_snippet", "recommendation" } ],
  "summary": "brief standards/compliance summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.15):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def validate(self, source_code: str, contract_name: str = "module") -> SpecialistReport:
        msg = (
            f"Review Move code for standards and compliance with ecosystem best practices.\n\n"
            f"Module / file: {contract_name}\n\n"
            f"```move\n{source_code[:120000]}\n```"
        )
        response = self.llm.invoke(
            [SystemMessage(content=self.SYSTEM_PROMPT), HumanMessage(content=msg)]
        )
        text = response.content if hasattr(response, "content") else str(response)
        return parse_specialist_json(text, "compliance")
