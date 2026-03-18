"""
Wallet Poisoning Agent – Web3 address poisoning education and risk assessment.

This agent helps users understand wallet (address) poisoning attacks, check whether
two addresses might be a lookalike pair, and get actionable defense recommendations.
"""
import os
import json
import re
from typing import Optional, Dict, List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from tools import check_address_similarity, get_poisoning_facts, validate_evm_address, all_tools
from schemas import WalletPoisoningReport, AddressCheckResult

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


SYSTEM_PROMPT = """You are a Web3 security assistant focused on wallet (address) poisoning.

Your role:
- Educate users on what address poisoning is: attackers create lookalike addresses (same first/last characters) and send "dust" to the victim so the fake address appears in history; users may then copy the wrong address and send funds to the attacker.
- Help users verify destinations: when they have two addresses (e.g. trusted vs. unknown), use check_address_similarity to compare them and explain the risk.
- Encourage safe habits: always verify the FULL address, use address books, and be wary of addresses that only match at the start/end.

Rules:
1. Use get_poisoning_facts when the user asks what wallet/address poisoning is or how to protect themselves.
2. Use check_address_similarity when the user provides two addresses to compare (trusted vs. destination).
3. Use validate_evm_address when the user asks if an address format is valid.
4. Do not encourage or assist any attack; only explain defenses and help users verify their own transactions.
5. Keep answers clear and actionable. Include a short disclaimer that this is educational and users should verify through trusted sources.
6. If the user asks to "poison" a wallet or perform an attack, refuse and explain that you only help with defense and education."""


class WalletPoisoningAgent:
    """Agent for wallet poisoning education and address risk assessment."""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
    ):
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.agent = create_agent(
            model=self.llm,
            tools=all_tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def ask(self, query: str, verbose: bool = False) -> Dict:
        """
        Ask the agent anything about wallet poisoning or address safety.
        Returns raw agent response and, when possible, a structured WalletPoisoningReport.
        """
        if verbose:
            print(f"🔍 Wallet Poisoning Agent")
            print(f"Query: {query}")
            print("=" * 60)
        try:
            result = self.agent.invoke({
                "messages": [HumanMessage(content=query)]
            })
            messages = result.get("messages", [])
            if not messages:
                raise ValueError("No messages returned from agent")
            final = messages[-1]
            content = final.content if hasattr(final, "content") else str(final)
            if verbose:
                print("✅ Response received\n")
            report = self._parse_report(query, content)
            return {
                "query": query,
                "response_text": content,
                "report": report,
                "messages": [str(m) for m in messages],
            }
        except Exception as e:
            if verbose:
                print(f"❌ Error: {e}")
            raise

    def check_address(
        self,
        trusted_address: str,
        address_to_check: str,
        verbose: bool = False,
    ) -> Dict:
        """
        Compare two EVM addresses for lookalike/poisoning risk.
        Returns analysis and a structured AddressCheckResult when possible.
        """
        from tools import _similarity_analysis
        analysis = _similarity_analysis(trusted_address, address_to_check)
        rec = "Verify the full address before sending funds."
        if analysis.get("risk_note"):
            rec = analysis["risk_note"]
        if analysis.get("identical"):
            rec = "Addresses are the same; no poisoning risk for this pair."
        try:
            addr_result = AddressCheckResult(
                addresses_valid=analysis["valid"],
                identical=analysis.get("identical", False),
                prefix_match_chars=analysis.get("prefix_match_len", 0),
                suffix_match_chars=analysis.get("suffix_match_len", 0),
                risk_note=analysis.get("risk_note"),
                recommendation=rec,
            )
        except Exception:
            addr_result = None
        if verbose:
            print("Address comparison:")
            print(f"  Valid: {analysis['valid']}, Identical: {analysis.get('identical')}")
            print(f"  Prefix match: {analysis.get('prefix_match_len')}, Suffix match: {analysis.get('suffix_match_len')}")
            if analysis.get("risk_note"):
                print(f"  ⚠️  {analysis['risk_note']}")
        return {
            "trusted_address": trusted_address,
            "address_to_check": address_to_check,
            "analysis": analysis,
            "address_check_result": addr_result.dict() if addr_result else None,
        }

    def _parse_report(self, query: str, content: str) -> Optional[WalletPoisoningReport]:
        """Try to build WalletPoisoningReport from agent response."""
        try:
            json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return WalletPoisoningReport(**parsed)
        except Exception:
            pass
        return WalletPoisoningReport(
            topic="Wallet poisoning",
            summary=content[:500] + ("..." if len(content) > 500 else ""),
            key_points=[],
            recommendations=[
                "Always verify the full destination address before sending.",
                "Use address book or verified contacts when possible.",
            ],
        )

    def print_report(self, response: Dict) -> None:
        """Pretty-print the response from ask()."""
        print("\n" + "=" * 70)
        print("🛡️  WALLET POISONING AGENT")
        print("=" * 70)
        print(f"\nQuery: {response.get('query', '')}")
        print("\nResponse:")
        print("-" * 70)
        print(response.get("response_text", ""))
        report = response.get("report")
        if report and isinstance(report, WalletPoisoningReport):
            if report.recommendations:
                print("\nRecommendations:")
                for r in report.recommendations:
                    print(f"  • {r}")
            print(f"\n{report.disclaimer}")
        print("=" * 70 + "\n")


def main():
    """Run example: explain poisoning and optional address check."""
    agent = WalletPoisoningAgent(model_name="gpt-4", temperature=0.3)

    # Example 1: What is wallet poisoning?
    result = agent.ask("What is wallet or address poisoning and how can I avoid it?", verbose=True)
    agent.print_report(result)

    # Example 2: Compare two addresses (optional – use real-looking addresses for demo)
    # trusted = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
    # unknown = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b7"  # one char different
    # check = agent.check_address(trusted, unknown, verbose=True)
    # print("Check result:", check.get("address_check_result"))


if __name__ == "__main__":
    main()
