"""
Tools: read Move source files and invoke specialist validators (orchestrator mode).
"""
import os
from typing import Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

_agents = {}


def _model_name() -> str:
    return os.getenv("MOVE_VALIDATOR_MODEL", "gpt-4o")


def _get_security():
    from agents.security_agent import MoveSecurityValidator

    if "security" not in _agents:
        _agents["security"] = MoveSecurityValidator(model_name=_model_name())
    return _agents["security"]


def _get_logic():
    from agents.logic_agent import MoveLogicValidator

    if "logic" not in _agents:
        _agents["logic"] = MoveLogicValidator(model_name=_model_name())
    return _agents["logic"]


def _get_gas():
    from agents.gas_agent import MoveGasValidator

    if "gas" not in _agents:
        _agents["gas"] = MoveGasValidator(model_name=_model_name())
    return _agents["gas"]


def _get_compliance():
    from agents.compliance_agent import MoveComplianceValidator

    if "compliance" not in _agents:
        _agents["compliance"] = MoveComplianceValidator(model_name=_model_name())
    return _agents["compliance"]


class ReadMoveFileInput(BaseModel):
    file_path: str = Field(description="Path to a .move file or package entry")


class ValidateSourceInput(BaseModel):
    source_code: str = Field(description="Full Move source")
    contract_name: Optional[str] = Field(default="module", description="Module or file name for context")


class ReadMoveFileTool(BaseTool):
    name: str = "read_move_file"
    description: str = (
        "Read Move source from disk. Use when the user provides a file path or uploaded file."
    )
    args_schema: type[BaseModel] = ReadMoveFileInput

    def _run(self, file_path: str) -> str:
        path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.isfile(path):
            uploads = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
            alt = os.path.normpath(os.path.join(uploads, file_path.lstrip(os.sep)))
            if os.path.isfile(alt):
                path = alt
        if not os.path.isfile(path):
            return f"Error: File not found: {path}"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"


class MoveSecurityTool(BaseTool):
    name: str = "move_security_validate"
    description: str = "Run the Move security specialist (resources, access control, token safety)."
    args_schema: type[BaseModel] = ValidateSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "module") -> str:
        r = _get_security().validate(source_code, contract_name or "module")
        return r.model_dump_json(indent=2)


class MoveLogicTool(BaseTool):
    name: str = "move_logic_validate"
    description: str = "Run the Move logic/invariants specialist."
    args_schema: type[BaseModel] = ValidateSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "module") -> str:
        r = _get_logic().validate(source_code, contract_name or "module")
        return r.model_dump_json(indent=2)


class MoveGasTool(BaseTool):
    name: str = "move_gas_validate"
    description: str = "Run the Move gas/storage specialist."
    args_schema: type[BaseModel] = ValidateSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "module") -> str:
        r = _get_gas().validate(source_code, contract_name or "module")
        return r.model_dump_json(indent=2)


class MoveComplianceTool(BaseTool):
    name: str = "move_compliance_validate"
    description: str = "Run the Move standards/compliance specialist."
    args_schema: type[BaseModel] = ValidateSourceInput

    def _run(self, source_code: str, contract_name: Optional[str] = "module") -> str:
        r = _get_compliance().validate(source_code, contract_name or "module")
        return r.model_dump_json(indent=2)


read_move_file_tool = ReadMoveFileTool()
move_security_tool = MoveSecurityTool()
move_logic_tool = MoveLogicTool()
move_gas_tool = MoveGasTool()
move_compliance_tool = MoveComplianceTool()

all_tools = [
    read_move_file_tool,
    move_security_tool,
    move_logic_tool,
    move_gas_tool,
    move_compliance_tool,
]
