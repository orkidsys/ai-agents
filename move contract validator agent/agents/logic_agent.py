"""
Move logic specialist: invariants, abort conditions, business rules, edge cases.
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


class MoveLogicValidator:
    """Focus: correctness, invariants, ordering, race-like patterns at the Move model level."""

    SYSTEM_PROMPT = """You are an expert Move reviewer focused on logic, invariants, and correctness (Aptos / Sui).

Look for:

1. INVARIANTS: Pool accounting (deposits vs reserves), supply conservation, role state machines.
2. ABORT CONDITIONS: Missing checks before state changes; wrong order of updates vs events.
3. EDGE CASES: Empty vectors, zero amounts, max u64, duplicate entries, rounding in favor of the protocol vs users.
4. INTEGRATION: Assumptions about oracle prices, external module behavior, version mismatches.
5. EVENTS / EMITS: Missing or misleading events for critical state changes (if applicable).

Category must be one of: resource_safety, access_control, abort_invariant, gas_storage, standards_compliance, other.

Respond with JSON only:
{
  "findings": [ { "title", "severity", "category", "description", "location", "code_snippet", "recommendation" } ],
  "summary": "brief logic summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.15):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def validate(self, source_code: str, contract_name: str = "module") -> SpecialistReport:
        msg = (
            f"Validate Move logic and invariants.\n\n"
            f"Module / file: {contract_name}\n\n"
            f"```move\n{source_code[:120000]}\n```"
        )
        response = self.llm.invoke(
            [SystemMessage(content=self.SYSTEM_PROMPT), HumanMessage(content=msg)]
        )
        text = response.content if hasattr(response, "content") else str(response)
        return parse_specialist_json(text, "logic")
