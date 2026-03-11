"""
Logic and business-rules audit agent.
Detects inconsistencies, invariant violations, and logical flaws.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import Finding, SpecialistReport, Severity, Category
import json
import re


class LogicAuditAgent:
    """Agent specialized in business logic and invariant analysis."""

    SYSTEM_PROMPT = """You are an expert smart contract logic auditor. Your job is to find business logic flaws, invariant violations, and consistency issues.

Focus on:

1. STATE INVARIANTS: Quantities that should never go negative, total supply vs balances, ownership consistency.
2. EDGE CASES: Zero amounts, max uint, first/last user, empty lists, division by zero.
3. RACE CONDITIONS: Order of operations, state changes that can be reordered or interleaved.
4. CONFIGURATION / PARAMS: Misconfiguration risks, dangerous defaults, missing validation.
5. UPGRADEABILITY: Storage layout, initializer re-entrancy, missing gaps, proxy logic bugs.
6. INTEGRATION: Assumptions about external contracts (ERC behavior), token decimals, return values.
7. ACCESS FLOWS: Who can call what, privilege escalation, missing checks.
8. MATH / ROUNDING: Favoring one side due to rounding, precision loss.

For each finding provide:
- title, severity (critical|high|medium|low|informational), category (use "business_logic" or "other")
- description, location (e.g., "Vault.sol:88"), code_snippet (optional), recommendation

Respond with a JSON object only:
{
  "findings": [
    {
      "title": "...",
      "severity": "...",
      "category": "business_logic|other",
      "description": "...",
      "location": "...",
      "code_snippet": "...",
      "recommendation": "..."
    }
  ],
  "summary": "Brief logic audit summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def audit(self, source_code: str, contract_name: str = "contract") -> SpecialistReport:
        """Run logic audit on the given source code."""
        response = self.llm.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Audit the following smart contract for logic and business-rule flaws.\n\nContract: {contract_name}\n\n```solidity\n{source_code[:120000]}\n```"),
        ])
        text = response.content if hasattr(response, "content") else str(response)
        return self._parse_response(text, "logic")

    def _parse_response(self, text: str, agent_name: str) -> SpecialistReport:
        findings = []
        summary = "Logic audit completed."
        confidence = "medium"
        try:
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                data = json.loads(json_match.group())
                raw = data.get("findings", [])
                for f in raw:
                    try:
                        findings.append(Finding(
                            title=f.get("title", "Unnamed"),
                            severity=Severity(f.get("severity", "informational")),
                            category=Category(f.get("category", "other")),
                            description=f.get("description", ""),
                            location=f.get("location"),
                            code_snippet=f.get("code_snippet"),
                            recommendation=f.get("recommendation", ""),
                            agent_source=agent_name,
                        ))
                    except Exception:
                        pass
                summary = data.get("summary", summary)
                confidence = data.get("confidence", confidence)
        except Exception:
            pass
        return SpecialistReport(
            agent_name=agent_name,
            findings=findings,
            summary=summary,
            confidence=confidence,
        )
