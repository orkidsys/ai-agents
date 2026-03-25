"""
Move Contract Validator — multi-agent validation for Aptos / Sui Move modules.

Runs four specialists (security, logic, gas, compliance) and merges findings into one report.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI

_AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _AGENT_DIR not in sys.path:
    sys.path.insert(0, _AGENT_DIR)

from agents import (
    MoveComplianceValidator,
    MoveGasValidator,
    MoveLogicValidator,
    MoveSecurityValidator,
)
from schemas import Finding, MoveValidationReport, Severity, SpecialistReport
from tools import all_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")


def _infer_chain_hint(source: str) -> Optional[str]:
    s = source.lower()
    if "sui::" in s or "0x2::" in source or " sui " in f" {s} ":
        return "sui"
    if "aptos_framework" in s or "aptos_std" in s or "0x1::" in source:
        return "aptos"
    return None


class MoveContractValidator:
    """
    Orchestrates MoveSecurityValidator, MoveLogicValidator, MoveGasValidator, MoveComplianceValidator.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.15,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.security = MoveSecurityValidator(model_name=model_name, temperature=temperature)
        self.logic = MoveLogicValidator(model_name=model_name, temperature=temperature)
        self.gas = MoveGasValidator(model_name=model_name, temperature=temperature)
        self.compliance = MoveComplianceValidator(model_name=model_name, temperature=temperature)

    def _get_source(
        self,
        file_path: Optional[str] = None,
        source_code: Optional[str] = None,
    ) -> Tuple[str, str]:
        if file_path:
            path = os.path.abspath(os.path.expanduser(file_path))
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Move file not found: {path}")
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                source = f.read()
            name = os.path.basename(path)
            return source, name
        if source_code:
            return source_code.strip(), "module"
        raise ValueError("Provide either file_path or source_code.")

    def validate(
        self,
        file_path: Optional[str] = None,
        source_code: Optional[str] = None,
        chain_hint: Optional[str] = None,
        verbose: bool = False,
    ) -> MoveValidationReport:
        source, contract_name = self._get_source(file_path=file_path, source_code=source_code)
        hint = chain_hint or _infer_chain_hint(source)

        if verbose:
            print(f"Validating: {contract_name} ({len(source)} chars), chain_hint={hint}")
            print("Running security specialist...")
        security_report = self.security.validate(source, contract_name)
        if verbose:
            print("Running logic specialist...")
        logic_report = self.logic.validate(source, contract_name)
        if verbose:
            print("Running gas specialist...")
        gas_report = self.gas.validate(source, contract_name)
        if verbose:
            print("Running compliance specialist...")
        compliance_report = self.compliance.validate(source, contract_name)

        specialist_reports = [security_report, logic_report, gas_report, compliance_report]
        all_findings: List[Finding] = []
        for r in specialist_reports:
            all_findings.extend(r.findings)

        seen = set()
        unique: List[Finding] = []
        for f in all_findings:
            key = (f.title, f.location or "")
            if key not in seen:
                seen.add(key)
                unique.append(f)

        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFORMATIONAL: 4,
        }
        unique.sort(key=lambda x: (severity_order.get(x.severity, 5), x.title))

        risk_level, executive_summary, recommendations = self._synthesize(
            contract_name, specialist_reports, unique
        )

        return MoveValidationReport(
            contract_name=contract_name,
            chain_hint=hint,
            validation_timestamp=datetime.utcnow().isoformat() + "Z",
            specialist_reports=specialist_reports,
            all_findings=unique,
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
            f"Move validation of {contract_name}: {len(findings)} finding(s) from 4 specialists.",
            f"Severity: {critical} critical, {high} high, {medium} medium.",
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

    def validate_with_orchestrator(
        self,
        user_message: str,
        file_path: Optional[str] = None,
        verbose: bool = False,
    ) -> dict:
        """LLM orchestrator: read files and call specialist tools as needed."""
        llm = ChatOpenAI(model=self.model_name, temperature=self.temperature)
        llm_with_tools = llm.bind_tools(all_tools)
        messages = [
            SystemMessage(content=self._orchestrator_prompt()),
            HumanMessage(content=user_message),
        ]
        if file_path:
            messages.append(
                HumanMessage(
                    content=f"User file path (read with read_move_file if needed): {file_path}"
                )
            )
        max_rounds = 12
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
                    ToolMessage(content=out, tool_call_id=tc.get("id", ""))
                )
            messages.append(response)
        return {"response": "Max tool rounds reached.", "messages": messages}

    def _orchestrator_prompt(self) -> str:
        return """You orchestrate Move contract validation (Aptos / Sui).

Tools:
1. read_move_file(file_path) — load Move source from disk.
2. move_security_validate(source_code, contract_name) — security specialist.
3. move_logic_validate(source_code, contract_name) — logic/invariants specialist.
4. move_gas_validate(source_code, contract_name) — gas/storage specialist.
5. move_compliance_validate(source_code, contract_name) — standards specialist.

For a full validation: read the file if needed, then run all four specialists on the same source.
Summarize: overall risk, key findings by severity, and top recommendations. Note this is LLM-assisted review, not a substitute for formal audit or the Move prover."""

    def print_report(self, report: MoveValidationReport) -> None:
        print("\n" + "=" * 70)
        print("MOVE CONTRACT VALIDATION REPORT")
        print("=" * 70)
        print(f"Module / file: {report.contract_name}")
        if report.chain_hint:
            print(f"Chain hint: {report.chain_hint}")
        print(f"Timestamp: {report.validation_timestamp}")
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
        print("FINDINGS")
        print("-" * 70)
        for f in report.all_findings:
            print(f"  [{f.severity.value.upper()}] {f.title}")
            print(f"    Category: {f.category.value} | Agent: {f.agent_source}")
            if f.location:
                print(f"    Location: {f.location}")
            desc = (f.description or "")[:220]
            rec = (f.recommendation or "")[:160]
            print(f"    {desc}{'...' if len(f.description or '') > 220 else ''}")
            print(f"    Fix: {rec}{'...' if len(f.recommendation or '') > 160 else ''}")
            print()
        print("SPECIALIST SUMMARIES")
        print("-" * 70)
        for r in report.specialist_reports:
            print(f"  {r.agent_name}: {r.summary} (confidence: {r.confidence})")
        print("=" * 70 + "\n")


def main() -> None:
    import sys

    validator = MoveContractValidator(model_name=os.getenv("MOVE_VALIDATOR_MODEL", "gpt-4o"))

    if len(sys.argv) > 1:
        path = sys.argv[1]
        path = os.path.join(UPLOADS_DIR, path) if not os.path.isabs(path) else path
        if not os.path.isfile(path):
            path = sys.argv[1]
        print(f"Validating: {path}")
        try:
            report = validator.validate(file_path=path, verbose=True)
            validator.print_report(report)
            out_path = os.path.join(os.path.dirname(__file__), "move_validation_report.json")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
            print(f"Report saved to {out_path}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        sample = """
module 0x42::example {
    use std::signer;

    struct Counter has key {
        value: u64
    }

    public entry fun init(account: &signer) {
        move_to(account, Counter { value: 0 });
    }

    public entry fun bump(account: &signer) acquires Counter {
        let c = borrow_global_mut<Counter>(signer::address_of(account));
        c.value = c.value + 1;
    }
}
"""
        print("Running example validation on inline Move snippet...")
        report = validator.validate(source_code=sample, chain_hint="aptos", verbose=True)
        validator.print_report(report)


if __name__ == "__main__":
    main()
