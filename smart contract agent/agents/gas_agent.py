"""
Gas and optimization audit agent.
Identifies gas inefficiencies and optimization opportunities.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import Finding, SpecialistReport, Severity, Category
import json
import re


class GasAuditAgent:
    """Agent specialized in gas usage and optimization."""

    SYSTEM_PROMPT = """You are an expert smart contract gas auditor. Your job is to find gas inefficiencies and suggest optimizations.

Focus on:

1. STORAGE: SLOAD/SSTORE cost, packing variables, storage vs memory, redundant reads.
2. LOOPS: Unbounded loops, caching length, early exit, batch operations.
3. MEMORY VS CALLDATA: Use calldata for external read-only params.
4. SHORT-CIRCUIT: Order conditions to fail fast and avoid expensive checks.
5. BYTES VS STRING: Prefer bytes32/bytes when possible.
6. EXTERNAL CALLS: Batching, avoiding repeated calls in loops.
7. CONSTRUCTOR / INIT: Immutable vs constant, one-time init.
8. EVENTS: Indexed params, avoid storing data that can be derived from events.
9. ASSEMBLY: Safe use of assembly for hot paths.
10. CONTRACT SIZE: Inlining, library usage, deployment cost.

For each finding provide:
- title, severity (use low or informational for most gas findings), category "gas_optimization"
- description (include gas impact if estimable), location, code_snippet (optional), recommendation

Respond with a JSON object only:
{
  "findings": [
    {
      "title": "...",
      "severity": "low|informational",
      "category": "gas_optimization",
      "description": "...",
      "location": "...",
      "code_snippet": "...",
      "recommendation": "..."
    }
  ],
  "summary": "Brief gas audit summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def audit(self, source_code: str, contract_name: str = "contract") -> SpecialistReport:
        """Run gas audit on the given source code."""
        response = self.llm.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Audit the following smart contract for gas optimizations.\n\nContract: {contract_name}\n\n```solidity\n{source_code[:120000]}\n```"),
        ])
        text = response.content if hasattr(response, "content") else str(response)
        return self._parse_response(text, "gas")

    def _parse_response(self, text: str, agent_name: str) -> SpecialistReport:
        findings = []
        summary = "Gas audit completed."
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
                            category=Category(f.get("category", "gas_optimization")),
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
