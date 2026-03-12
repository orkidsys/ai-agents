"""
Frontend developer tools: read/write files and list directory within a workspace.
Used by the Frontend Developer Agent to implement UI, components, and config.
"""
import os
from pathlib import Path
from typing import Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


def _resolve_path(base: Optional[str], path: str) -> Path:
    """Resolve path relative to base; ensure it stays under base for safety."""
    base_path = Path(base or os.getcwd()).resolve()
    full = (base_path / path).resolve()
    try:
        full.relative_to(base_path)
    except ValueError:
        raise ValueError(f"Path must be inside workspace: {path}")
    return full


class ReadFileInput(BaseModel):
    """Input for read_file tool."""
    path: str = Field(description="Path to the file, relative to workspace root (e.g. 'src/App.jsx', 'package.json')")


class WriteFileInput(BaseModel):
    """Input for write_file tool."""
    path: str = Field(description="Path to the file, relative to workspace root")
    content: str = Field(description="Full content to write to the file")


class ListDirectoryInput(BaseModel):
    """Input for list_directory tool."""
    path: str = Field(
        default=".",
        description="Directory path relative to workspace root (use '.' for root)"
    )


class ReadFileTool(BaseTool):
    """Read a file from the workspace."""

    name: str = "read_file"
    description: str = (
        "Read the contents of a file. Use this to inspect existing components, "
        "config files, or styles before making changes. Path is relative to workspace root."
    )
    args_schema: type[BaseModel] = ReadFileInput
    workspace_root: Optional[str] = None

    def _run(self, path: str) -> str:
        try:
            full = _resolve_path(self.workspace_root, path)
            if not full.is_file():
                return f"Error: not a file or does not exist: {path}"
            return full.read_text(encoding="utf-8", errors="replace")
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"Error reading {path}: {e}"


class WriteFileTool(BaseTool):
    """Write content to a file in the workspace."""

    name: str = "write_file"
    description: str = (
        "Write or overwrite a file with the given content. Use to create or update "
        "components, styles, or config. Path is relative to workspace root. Creates parent directories if needed."
    )
    args_schema: type[BaseModel] = WriteFileInput
    workspace_root: Optional[str] = None

    def _run(self, path: str, content: str) -> str:
        try:
            full = _resolve_path(self.workspace_root, path)
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            return f"Wrote {path} ({len(content)} chars)"
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"Error writing {path}: {e}"


class ListDirectoryTool(BaseTool):
    """List files and directories in a workspace folder."""

    name: str = "list_directory"
    description: str = (
        "List files and subdirectories in a directory. Use to explore project structure, "
        "find components, or see existing files. Path is relative to workspace root; use '.' for root."
    )
    args_schema: type[BaseModel] = ListDirectoryInput
    workspace_root: Optional[str] = None

    def _run(self, path: str = ".") -> str:
        try:
            full = _resolve_path(self.workspace_root, path)
            if not full.is_dir():
                return f"Error: not a directory or does not exist: {path}"
            entries = []
            for p in sorted(full.iterdir()):
                kind = "dir" if p.is_dir() else "file"
                entries.append(f"  {kind}: {p.name}")
            return "\n".join(entries) if entries else "(empty)"
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"Error listing {path}: {e}"


def get_frontend_tools(workspace_root: Optional[str] = None) -> list:
    """Build read_file, write_file, and list_directory tools with optional workspace root."""
    root = workspace_root or os.getcwd()
    tools = [
        ReadFileTool(workspace_root=root),
        WriteFileTool(workspace_root=root),
        ListDirectoryTool(workspace_root=root),
    ]
    return tools
