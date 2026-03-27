"""
Technical Documentation Agent - turns rough notes into structured docs and outlines.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from llm_factory import build_chat_model
from schemas import DocReply
from tools import get_technical_doc_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """You are TechnicalDocumentationAgent. You produce clear technical writing.

## Rules
1. Ask what the doc is for if unclear (README, API reference, runbook, changelog, ADR).
2. Match the reader: developers, operators, or end users as appropriate.
3. Use tools when helpful: suggest_doc_outline for structure, format_changelog_entry for release notes.
4. Prefer concrete examples, install steps, and copy-paste commands where relevant.
5. Do not invent APIs, flags, or version numbers the user did not provide.
6. If JSON is requested, end with:
   {"title":"...","doc_type":"...","outline":[],"draft_markdown":"...","review_checklist":[]}
"""


class TechnicalDocumentationAgent:
    """LangChain agent for drafts and outlines of technical documentation."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        tools: Optional[List[Any]] = None,
    ):
        self.provider = provider.strip().lower()
        self.llm = build_chat_model(
            provider=self.provider,
            model_name=model_name,
            temperature=temperature,
        )
        self.tools = tools if tools is not None else get_technical_doc_tools()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def chat(self, message: str, verbose: bool = False) -> Dict[str, Any]:
        user_text = (message or "").strip()
        if verbose:
            print(f"Provider: {self.provider}")

        result = self.agent.invoke({"messages": [HumanMessage(content=user_text)]})
        messages = result.get("messages", [])
        content = ""
        if messages:
            last = messages[-1]
            content = getattr(last, "content", None) or str(last)

        structured = self._try_parse_structured(content)
        return {
            "message": user_text,
            "messages": messages,
            "content": content,
            "structured": structured,
        }

    def _try_parse_structured(self, content: str) -> Optional[DocReply]:
        try:
            m = re.search(r"\{[\s\S]*\}\s*$", content) or re.search(r"\{[\s\S]*\}", content)
            if m:
                return DocReply(**json.loads(m.group()))
        except Exception:
            pass
        return None

    def print_result(self, result: Dict[str, Any]) -> None:
        print("\n" + "=" * 70)
        print("TECHNICAL DOCUMENTATION RESULT")
        print("=" * 70)
        print(f"Message: {result.get('message', 'N/A')}")
        print("-" * 70)
        print(result.get("content", ""))
        if result.get("structured"):
            print("-" * 70)
            print("Structured:", result["structured"].model_dump_json(indent=2))
        print("=" * 70 + "\n")


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Technical Documentation Agent")
    parser.add_argument(
        "--provider",
        default=os.getenv("TECH_DOC_AGENT_PROVIDER", "openai"),
        help="openai | anthropic | google | gemini | vertex",
    )
    parser.add_argument("--model", default=None, help="Model id (optional)")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--message", "-m", default=None, help="Request or rough notes")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    agent = TechnicalDocumentationAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )
    msg = args.message or (
        "Draft a short README section for a Python CLI tool that ingests CSV and outputs JSON. "
        "Include install and one example command."
    )
    r = agent.chat(message=msg, verbose=args.verbose)
    agent.print_result(r)


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        _cli()
        return

    agent = TechnicalDocumentationAgent(provider=os.getenv("TECH_DOC_AGENT_PROVIDER", "openai"))
    result = agent.chat(
        message="Outline and draft changelog for v1.2.0: fixed upload bug, added dark mode.",
        verbose=True,
    )
    agent.print_result(result)


if __name__ == "__main__":
    main()
