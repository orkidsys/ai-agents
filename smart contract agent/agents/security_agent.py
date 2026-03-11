"""
Security-focused audit agent.
Detects reentrancy, access control issues, overflow/underflow, unchecked calls, front-running, etc.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import Finding, SpecialistReport, Severity, Category
import json
import re
from typing import List


class SecurityAuditAgent:
    """Agent specialized in security vulnerability detection."""

    SYSTEM_PROMPT = """You are an expert smart contract security auditor. Your job is to perform an intensive security review of Solidity/smart contract source code.

You MUST identify and report:

1. REENTRANCY: External calls before state updates, callback patterns, cross-function reentrancy.
2. ACCESS CONTROL: Missing or weak access control, unprotected admin functions, role confusions.
3. ARITHMETIC: Integer overflow/underflow (pre-Solidity 0.8), unchecked math, truncation.
4. UNCHECKED EXTERNAL CALLS: Low-level calls without checking return value, delegatecall to untrusted targets.
5. FRONT-RUNNING / MEV: Order-dependent state, sandwichability, predictable ordering.
6. ORACLE MANIPULATION: Price oracle reliance, TWAP/minimum liquidity, flash loan attacks.
7. SELF-DESTRUCT / DELEGATECALL: Dangerous delegatecall usage, proxy pitfalls.
8. SIGNATURE / REPLAY: Replay across chains or contracts, nonce issues.
9. RANDOMNESS: Block-dependent or predictable randomness.
10. TOKEN / APPROVAL: Approval race, fee-on-transfer tokens, inconsistent decimals.

For each finding you MUST provide:
- title: Short descriptive title
- severity: one of critical, high, medium, low, informational
- category: one of reentrancy, access_control, arithmetic_overflow_underflow, unchecked_external_calls, front_running, oracle_manipulation, other
- description: Clear explanation of the issue and why it is a risk
- location: File/contract name and line number if identifiable (e.g., "Token.sol:42")
- code_snippet: Relevant code snippet if applicable (optional)
- recommendation: Concrete fix or mitigation

Respond with a JSON object only, no markdown or extra text. Use this exact structure:
{
  "findings": [
    {
      "title": "...",
      "severity": "critical|high|medium|low|informational",
      "category": "reentrancy|access_control|...",
      "description": "...",
      "location": "Contract.sol:123",
      "code_snippet": "optional snippet",
      "recommendation": "..."
    }
  ],
  "summary": "Brief overall security summary",
  "confidence": "low|medium|high"
}"""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)

    def audit(self, source_code: str, contract_name: str = "contract") -> SpecialistReport:
        """Run security audit on the given source code."""
        response = self.llm.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Audit the following smart contract for security vulnerabilities.\n\nContract name or file: {contract_name}\n\n```solidity\n{source_code[:120000]}\n```"),
        ])
        text = response.content if hasattr(response, "content") else str(response)
        return self._parse_response(text, "security")

    def _parse_response(self, text: str, agent_name: str) -> SpecialistReport:
        """Parse LLM response into SpecialistReport."""
        findings = []
        summary = "Security audit completed."
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
