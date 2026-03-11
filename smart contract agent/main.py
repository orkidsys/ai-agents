"""
Smart Contract Auditing Agent — Multi-agent intensive auditing with file upload support.

Orchestrates four specialist agents (Security, Logic, Gas, Compliance) and produces
a structured audit report. Accepts a file path (e.g. uploaded contract) or raw source.
"""
from dotenv import load_dotenv
import os
import sys

# Ensure agent root is on path when run from any directory
_AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)

from typing import Optional, List, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from schemas import (
    AuditReport,
    SpecialistReport,
    Finding,
    Severity,
)
from tools import (
    ReadContractFileTool,
    all_tools,
)
from agents import (
    SecurityAuditAgent,
    LogicAuditAgent,
    GasAuditAgent,
    ComplianceAuditAgent,
)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Default uploads directory (relative to agent root)
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")


class SmartContractAuditor:
    """
    Multi-agent smart contract auditor.
    Runs Security, Logic, Gas, and Compliance specialists and merges findings.
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.2,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.security_agent = SecurityAuditAgent(model_name=model_name, temperature=temperature)
        self.logic_agent = LogicAuditAgent(model_name=model_name, temperature=temperature)
        self.gas_agent = GasAuditAgent(model_name=model_name, temperature=temperature)
        self.compliance_agent = ComplianceAuditAgent(model_name=model_name, temperature=temperature)
        self.read_tool = ReadContractFileTool()

    def _get_source(self, file_path: Optional[str] = None, source_code: Optional[str] = None) -> Tuple[str, str]:
        """Resolve contract source and a display name. Prefer file_path over source_code."""
        if file_path:
            path = os.path.abspath(os.path.expanduser(file_path))
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Contract file not found: {path}")
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            name = os.path.basename(path)
            return source, name
        if source_code:
            return source_code.strip(), "contract"
        raise ValueError("Provide either file_path or source_code.")

    def audit(
        self,
        file_path: Optional[str] = None,
        source_code: Optional[str] = None,
        verbose: bool = False,
    ) -> AuditReport:
        """
        Run intensive multi-agent audit.

        Args:
            file_path: Path to contract file (e.g. uploads/Token.sol or absolute path).
            source_code: Raw source as string (alternative to file_path).
            verbose: Print progress per agent.

        Returns:
            AuditReport with specialist reports and merged findings.
        """
        source, contract_name = self._get_source(file_path=file_path, source_code=source_code)

        if verbose:
            print(f"Auditing: {contract_name} ({len(source)} chars)")
            print("Running Security agent...")
        security_report = self.security_agent.audit(source, contract_name)
        if verbose:
            print("Running Logic agent...")
        logic_report = self.logic_agent.audit(source, contract_name)
        if verbose:
            print("Running Gas agent...")
        gas_report = self.gas_agent.audit(source, contract_name)
        if verbose:
            print("Running Compliance agent...")
        compliance_report = self.compliance_agent.audit(source, contract_name)

        specialist_reports = [security_report, logic_report, gas_report, compliance_report]
        all_findings: List[Finding] = []
        for r in specialist_reports:
            all_findings.extend(r.findings)

        # Deduplicate by title+location (simple merge)
        seen = set()
        unique_findings: List[Finding] = []
        for f in all_findings:
            key = (f.title, f.location or "")
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)

        # Sort by severity (critical first)
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFORMATIONAL: 4,
        }
        unique_findings.sort(key=lambda x: (severity_order.get(x.severity, 5), x.title))

        # Overall risk and executive summary
        risk_level, executive_summary, recommendations = self._synthesize(
            contract_name, specialist_reports, unique_findings
        )

        return AuditReport(
            contract_name=contract_name,
            audit_timestamp=datetime.utcnow().isoformat() + "Z",
            specialist_reports=specialist_reports,
            all_findings=unique_findings,
            executive_summary=executive_summary,
            risk_level=risk_level,
            recommendations=recommendations,
        )

    def _synthesize(
        self,
        contract_name: str,
        specialist_reports: List[SpecialistReport],
        findings: List[Finding],
    ) -> Tuple[str, str, List[str]]:
        """Compute overall risk level, executive summary, and top recommendations."""
        critical = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in findings if f.severity == Severity.HIGH)
        medium = sum(1 for f in findings if f.severity == Severity.MEDIUM)

        if critical > 0:
            risk_level = "critical"
        elif high > 0:
            risk_level = "high"
        elif medium > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        summary_parts = [
            f"Audit of {contract_name} completed with {len(findings)} finding(s) across 4 specialist agents.",
            f"Severity breakdown: {critical} critical, {high} high, {medium} medium.",
        ]
        for r in specialist_reports:
            summary_parts.append(f"{r.agent_name}: {r.summary}")
        executive_summary = " ".join(summary_parts)

        recs: List[str] = []
        for f in findings:
            if f.severity in (Severity.CRITICAL, Severity.HIGH) and (f.recommendation or "").strip():
                recs.append(f"[{f.severity.value}] {f.title}: {(f.recommendation or '')[:200]}")
        recs = recs[:10]
        if not recs and findings:
            recs = [f.recommendation for f in findings[:5] if f.recommendation]

        return risk_level, executive_summary, recs

    def audit_with_orchestrator(
        self,
        user_message: str,
        file_path: Optional[str] = None,
        verbose: bool = False,
    ) -> dict:
        """
        Run audit via orchestrator LLM: it can read files and call specialist tools.
        Use when you want the model to decide steps (e.g. multiple files).
        """
        llm = ChatOpenAI(model=self.model_name, temperature=self.temperature)
        llm_with_tools = llm.bind_tools(all_tools)

        messages = [
            SystemMessage(content=self._orchestrator_prompt()),
            HumanMessage(content=user_message),
        ]
        max_rounds = 10
        for _ in range(max_rounds):
            response = llm_with_tools.invoke(messages)
            if not getattr(response, "tool_calls", None):
                return {
                    "response": getattr(response, "content", None) or "",
                    "messages": messages + [response],
                }
            for tc in response.tool_calls:
                name = tc.get("name", "")
                args = tc.get("args") or {}
                tool = next((t for t in all_tools if t.name == name), None)
                if not tool:
                    continue
                try:
                    out = tool.invoke(args)
                except Exception as e:
                    out = f"Error: {e}"
                messages.append(
                    ToolMessage(
                        content=out,
                        tool_call_id=tc.get("id", ""),
                    )
                )
            messages.append(response)
        return {"response": "Max rounds reached.", "messages": messages}

    def _orchestrator_prompt(self) -> str:
        return """You are the orchestrator for a smart contract auditing system. You have these tools:

1. read_contract_file(file_path) — Read a contract file from disk. Use first when the user gives a path or says they uploaded a file.
2. security_audit(source_code, contract_name) — Run the security specialist (reentrancy, access control, etc.).
3. logic_audit(source_code, contract_name) — Run the logic/business-rules specialist.
4. gas_audit(source_code, contract_name) — Run the gas optimization specialist.
5. compliance_audit(source_code, contract_name) — Run the compliance/standards specialist.

When the user asks to audit a contract:
1. Read the file with read_contract_file if they gave a path.
2. Run all four audits (security, logic, gas, compliance) on the source code.
3. Synthesize a final report: executive summary, overall risk level, and top recommendations. List key findings by severity.

Always run all four specialist audits for an intensive audit. Be thorough and structured in your final report."""

    def print_report(self, report: AuditReport) -> None:
        """Pretty-print an AuditReport."""
        print("\n" + "=" * 70)
        print("SMART CONTRACT AUDIT REPORT")
        print("=" * 70)
        print(f"Contract: {report.contract_name}")
        print(f"Timestamp: {report.audit_timestamp}")
        print(f"Overall risk: {report.risk_level.upper()}")
        print()
        print("EXECUTIVE SUMMARY")
        print("-" * 70)
        print(report.executive_summary)
        print()
        if report.recommendations:
            print("TOP RECOMMENDATIONS")
            print("-" * 70)
            for i, r in enumerate(report.recommendations, 1):
                print(f"  {i}. {r}")
            print()
        print("FINDINGS BY SEVERITY")
        print("-" * 70)
        for f in report.all_findings:
            print(f"  [{f.severity.value.upper()}] {f.title}")
            print(f"    Category: {f.category.value} | Agent: {f.agent_source}")
            if f.location:
                print(f"    Location: {f.location}")
            desc = (f.description or "")[:200]
            rec = (f.recommendation or "")[:150]
            print(f"    {desc}{'...' if len(f.description or '') > 200 else ''}")
            print(f"    Recommendation: {rec}{'...' if len(f.recommendation or '') > 150 else ''}")
            print()
        print("SPECIALIST SUMMARIES")
        print("-" * 70)
        for r in report.specialist_reports:
            print(f"  {r.agent_name}: {r.summary} (confidence: {r.confidence})")
        print("=" * 70 + "\n")


def main():
    """CLI entrypoint: audit a file path or run example."""
    import sys
    auditor = SmartContractAuditor(model_name="gpt-4", temperature=0.2)

    if len(sys.argv) > 1:
        path = sys.argv[1]
        path = os.path.join(UPLOADS_DIR, path) if not os.path.isabs(path) else path
        if not os.path.isfile(path):
            path = sys.argv[1]  # try raw path
        print(f"Auditing: {path}")
        try:
            report = auditor.audit(file_path=path, verbose=True)
            auditor.print_report(report)
            out_path = os.path.join(os.path.dirname(__file__), "audit_report.json")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
            print(f"Report saved to {out_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Usage: python main.py <file_path>   (e.g. uploads/Token.sol or Token.sol)")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # Example: audit inline source
        sample = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleToken {
    mapping(address => uint256) public balanceOf;
    function transfer(address to, uint256 amount) external {
        require(balanceOf[msg.sender] >= amount);
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
    }
}
"""
        print("Running example audit on inline Solidity snippet...")
        report = auditor.audit(source_code=sample, verbose=True)
        auditor.print_report(report)


if __name__ == "__main__":
    main()
