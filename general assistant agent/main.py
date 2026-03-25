"""
General Assistant Agent — conversational help with pluggable LLMs and small utility tools.
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
from schemas import AssistantReply
from tools import get_general_assistant_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """You are GeneralAssistant, a helpful, accurate assistant.

## Rules
1. Use tools when they help: get_current_time for "what time" or scheduling context; safe_calculate for arithmetic the user asks you to compute precisely.
2. Be concise unless the user asks for depth. Prefer clear structure (short paragraphs or bullets).
3. If you are unsure, say so and suggest how to verify.
4. When the user wants structured output, end with a JSON object matching this shape:
   {"summary": "...", "reasoning_brief": null, "bullet_points": [], "suggested_follow_up": null}
"""


class GeneralAssistantAgent:
    """LangChain agent with optional time/math tools and pluggable chat model."""

    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.3,
        tools: Optional[List[Any]] = None,
    ):
        self.provider = provider.strip().lower()
        self.llm = build_chat_model(
            provider=self.provider,
            model_name=model_name,
            temperature=temperature,
        )
        self.tools = tools if tools is not None else get_general_assistant_tools()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
        )

    def chat(
        self,
        message: str,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Run the agent on a user message.

        Returns:
            Dict with keys: message, messages, content, structured (AssistantReply or None).
        """
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

        out: Dict[str, Any] = {
            "message": user_text,
            "messages": messages,
            "content": content,
            "structured": structured,
        }
        if verbose:
            print("\n--- Response ---\n")
            print(content[:8000] if len(content) > 8000 else content)
        return out

    def _try_parse_structured(self, content: str) -> Optional[AssistantReply]:
        try:
            m = re.search(r"\{[\s\S]*\}\s*$", content)
            if not m:
                m = re.search(r"\{[\s\S]*\}", content)
            if m:
                data = json.loads(m.group())
                return AssistantReply(**data)
        except Exception:
            pass
        return None

    def print_result(self, result: Dict[str, Any]) -> None:
        print("\n" + "=" * 70)
        print("GENERAL ASSISTANT RESULT")
        print("=" * 70)
        print(f"Message: {result.get('message', 'N/A')}")
        print("-" * 70)
        print(result.get("content", ""))
        if result.get("structured"):
            print("-" * 70)
            print("Structured:", result["structured"].model_dump_json(indent=2))
        print("=" * 70 + "\n")


def _cli() -> None:
    parser = argparse.ArgumentParser(description="General Assistant Agent (multi-provider LLM)")
    parser.add_argument(
        "--provider",
        default=os.getenv("GENERAL_AGENT_PROVIDER", "openai"),
        help="openai | anthropic | google | gemini | vertex",
    )
    parser.add_argument("--model", default=None, help="Model id (optional)")
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument(
        "--message",
        "-m",
        default=None,
        help="User message (if omitted, runs a short demo)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    agent = GeneralAssistantAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )
    msg = args.message or (
        "What time is it in UTC? Then compute (19 + 23) * 2 using the calculator tool."
    )
    r = agent.chat(message=msg, verbose=args.verbose)
    agent.print_result(r)


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        _cli()
        return

    agent = GeneralAssistantAgent(provider=os.getenv("GENERAL_AGENT_PROVIDER", "openai"))
    result = agent.chat(
        message="Say hello in one sentence and suggest one thing you can help with.",
        verbose=True,
    )
    agent.print_result(result)


if __name__ == "__main__":
    main()
