"""
Compliance and standards audit agent.
Checks ERC conformance, naming, and best practices.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import Finding, SpecialistReport, Severity, Category
import json
import re


class ComplianceAuditAgent:
    """Agent specialized in standards compliance (ERC-20, ERC-721, etc.) and best practices."""

    SYSTEM_PROMPT = """You are an expert smart contract compliance auditor. Your job is to verify conformance to standards and best practices.

Focus on:

1. ERC-20: Required interface (balanceOf, transfer, approve, transferFrom, allowance, events Transfer/Approval), decimals, totalSupply, return values, revert behavior.
2. ERC-721: Ownership, approval flows, safeTransferFrom, tokenURI, enumeration if applicable.
3. ERC-1155: Balance and batch operations, approval model, events.
4. ERC-4626 (Vaults): Asset/shares math, rounding direction, preview functions.
5. NAMING & NATSPEC: Function names match standard, NatSpec comments, events named correctly.
6. VISIBILITY: External vs public, proper use of internal/private.
7. REENTRANCY GUARD: Use of ReentrancyGuard where appropriate for standard patterns.
8. PAUSABILITY: If present, correct scope and access control.
9. UPGRADEABILITY: Proxy patterns (UUPS, Transparent), initializer instead of constructor.
10. DEPRECATIONS: Avoid deprecated patterns (e.g., safeMath when using Solidity >= 0.8).

For each finding provide:
- title, severity, category "compliance_standards" or "other"
- description, location, code_snippet (optional), recommendation

Respond with a JSON object only:
{
  "findings": [
    {
      "title": "...",
      "severity": "critical|high|medium|low|informational",
      "category": "compliance_standards|other",
      "description": "...",
      "location": "...",
      "code_snippet": "...",
      "recommendation": "..."
    }
  ],
  "summary": "Brief compliance summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def audit(self, source_code: str, contract_name: str = "contract") -> SpecialistReport:
        """Run compliance audit on the given source code."""
        response = self.llm.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Audit the following smart contract for standards compliance and best practices.\n\nContract: {contract_name}\n\n```solidity\n{source_code[:120000]}\n```"),
        ])
        text = response.content if hasattr(response, "content") else str(response)
        return self._parse_response(text, "compliance")

    def _parse_response(self, text: str, agent_name: str) -> SpecialistReport:
        findings = []
        summary = "Compliance audit completed."
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
