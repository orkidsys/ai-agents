"""
Move gas & storage specialist: hot paths, storage churn, iteration costs.
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


class MoveGasValidator:
    """Focus: storage efficiency, unnecessary global borrows, table usage, hot loops."""

    SYSTEM_PROMPT = """You are an expert Move reviewer for gas and storage efficiency on Aptos and/or Sui.

Consider:

1. STORAGE: Frequent `borrow_global_mut` on large structs, unnecessary writes, splitting hot vs cold fields.
2. TABLES / BAGS / COLLECTIONS: Unbounded iteration risks, key churn, large vectors in resources.
3. HOT PATHS: Redundant checks, repeated lookups, expensive operations in public entry points.
4. SUI SPECIFICS: Object wrapping depth, dynamic field abuse, shared object contention (conceptual).
5. APTOS SPECIFICS: Event emission cost, module init patterns, friend call chains.

Category must be one of: resource_safety, access_control, abort_invariant, gas_storage, standards_compliance, other.

Respond with JSON only:
{
  "findings": [ { "title", "severity", "category", "description", "location", "code_snippet", "recommendation" } ],
  "summary": "brief gas/storage summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.15):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def validate(self, source_code: str, contract_name: str = "module") -> SpecialistReport:
        msg = (
            f"Review Move code for gas and storage patterns.\n\n"
            f"Module / file: {contract_name}\n\n"
            f"```move\n{source_code[:120000]}\n```"
        )
        response = self.llm.invoke(
            [SystemMessage(content=self.SYSTEM_PROMPT), HumanMessage(content=msg)]
        )
        text = response.content if hasattr(response, "content") else str(response)
        return parse_specialist_json(text, "gas")
