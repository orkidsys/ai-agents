"""
Tools for the smart contract auditing agent.
- Read contract files (upload path or local path).
- Run specialist audits (security, logic, gas, compliance) as tools for the orchestrator.
"""
import os
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# Lazy init of specialist agents to avoid heavy imports at module load
_agents = {}


def _get_security_agent():
    from agents.security_agent import SecurityAuditAgent
    if "security" not in _agents:
        _agents["security"] = SecurityAuditAgent()
    return _agents["security"]


def _get_logic_agent():
    from agents.logic_agent import LogicAuditAgent
    if "logic" not in _agents:
        _agents["logic"] = LogicAuditAgent()
    return _agents["logic"]


def _get_gas_agent():
    from agents.gas_agent import GasAuditAgent
    if "gas" not in _agents:
        _agents["gas"] = GasAuditAgent()
    return _agents["gas"]


def _get_compliance_agent():
    from agents.compliance_agent import ComplianceAuditAgent
    if "compliance" not in _agents:
        _agents["compliance"] = ComplianceAuditAgent()
    return _agents["compliance"]


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ReadContractFileInput(BaseModel):
    """Input for reading a contract file."""
    file_path: str = Field(description="Absolute or relative path to the smart contract file (.sol or other)")


class AuditSourceInput(BaseModel):
    """Input for running a specialist audit on source code."""
    source_code: str = Field(description="Full smart contract source code as string")
    contract_name: Optional[str] = Field(default="contract", description="Name or path of the contract for reference")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class ReadContractFileTool(BaseTool):
    """Read smart contract source from a file path (e.g. uploaded file or local path)."""

    name: str = "read_contract_file"
    description: str = (
        "Read the contents of a smart contract file from disk. "
        "Use this first when the user provides a file path or says they uploaded a file. "
        "Input: file_path (e.g. 'uploads/Token.sol' or '/path/to/Contract.sol'). "
        "Returns the raw source code as a string."
    )
    args_schema: type[BaseModel] = ReadContractFileInput

    def _run(self, file_path: str) -> str:
        path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.isfile(path):
            return f"Error: File not found: {path}"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"


class SecurityAuditTool(BaseTool):
    """Run the security specialist audit on contract source code."""

    name: str = "security_audit"
    description: str = (
        "Run an intensive security audit on smart contract source code. "
        "Detects reentrancy, access control issues, overflow, unchecked calls, front-running, etc. "
        "Input: source_code (the full Solidity/source text), optional contract_name."
    )
    args_schema: type[BaseModel] = AuditSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "contract") -> str:
        report = _get_security_agent().audit(source_code, contract_name or "contract")
        return report.model_dump_json(indent=2)


class LogicAuditTool(BaseTool):
    """Run the logic/business-rules specialist audit on contract source code."""

    name: str = "logic_audit"
    description: str = (
        "Run a logic and business-rules audit on smart contract source code. "
        "Finds invariant violations, edge cases, race conditions, and integration issues."
    )
    args_schema: type[BaseModel] = AuditSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "contract") -> str:
        report = _get_logic_agent().audit(source_code, contract_name or "contract")
        return report.model_dump_json(indent=2)


class GasAuditTool(BaseTool):
    """Run the gas/optimization specialist audit on contract source code."""

    name: str = "gas_audit"
    description: str = (
        "Run a gas and optimization audit on smart contract source code. "
        "Identifies gas inefficiencies and suggests optimizations."
    )
    args_schema: type[BaseModel] = AuditSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "contract") -> str:
        report = _get_gas_agent().audit(source_code, contract_name or "contract")
        return report.model_dump_json(indent=2)


class ComplianceAuditTool(BaseTool):
    """Run the compliance/standards specialist audit on contract source code."""

    name: str = "compliance_audit"
    description: str = (
        "Run a compliance and standards audit on smart contract source code. "
        "Checks ERC conformance (ERC-20, ERC-721, etc.) and best practices."
    )
    args_schema: type[BaseModel] = AuditSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "contract") -> str:
        report = _get_compliance_agent().audit(source_code, contract_name or "contract")
        return report.model_dump_json(indent=2)


# Export tools for the orchestrator
read_contract_file_tool = ReadContractFileTool()
security_audit_tool = SecurityAuditTool()
logic_audit_tool = LogicAuditTool()
gas_audit_tool = GasAuditTool()
compliance_audit_tool = ComplianceAuditTool()

all_tools = [
    read_contract_file_tool,
    security_audit_tool,
    logic_audit_tool,
    gas_audit_tool,
    compliance_audit_tool,
]
