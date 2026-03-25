"""
Move security specialist: resources, access control, coins/tokens, public entry safety.
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


class MoveSecurityValidator:
    """Focus: resource safety, signer/capability misuse, re-entrancy analogs, token safety."""

    SYSTEM_PROMPT = """You are an expert Move language security reviewer for Aptos and/or Sui style modules.

Analyze the given Move source for:

1. RESOURCE SAFETY: Missing acquires, incorrect `acquires` lists, leaking resources, double withdraw/deposit, improper `move_to` / `borrow_global` patterns (Aptos), object ownership and transfer rules (Sui).
2. ACCESS CONTROL: Missing `signer` checks, friend-only vs public exposure, admin capabilities, upgrade hooks, unauthorized mint/burn/withdraw.
3. COIN / FA / TOKEN: Incorrect decimal handling, unchecked mint, fee-on-transfer assumptions, metadata abuse.
4. CROSS-MODULE TRUST: Public functions callable by anyone that escalate privileges; dependency on untrusted modules.
5. ARITHMETIC & LIMITS: Overflow-friendly patterns (Move 64-bit), division by zero, unchecked bounds.
6. ABORT / ASSERT: Security-relevant missing asserts (e.g. zero address, empty vector) where exploitable.

For each issue provide: title, severity (critical|high|medium|low|informational), category (must be one of: resource_safety, access_control, abort_invariant, gas_storage, standards_compliance, other), description, location (module::item or snippet context), optional code_snippet, recommendation.

Respond with JSON only, no markdown:
{
  "findings": [ { "title", "severity", "category", "description", "location", "code_snippet", "recommendation" } ],
  "summary": "brief security summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.15):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def validate(self, source_code: str, contract_name: str = "module") -> SpecialistReport:
        msg = (
            f"Perform a security-focused Move validation.\n\n"
            f"Module / file name: {contract_name}\n"
            f"If the code targets Aptos, Sui, or another stack, infer from imports and APIs.\n\n"
            f"```move\n{source_code[:120000]}\n```"
        )
        response = self.llm.invoke(
            [SystemMessage(content=self.SYSTEM_PROMPT), HumanMessage(content=msg)]
        )
        text = response.content if hasattr(response, "content") else str(response)
        return parse_specialist_json(text, "security")
