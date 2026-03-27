"""
Email Triage Agent - classifies and drafts responses for incoming emails.
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
from schemas import EmailTriageReply
from tools import get_email_triage_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """You are EmailTriageAgent, focused on inbox triage.

## Rules
1. Classify each email by priority and intent (request, complaint, follow-up, FYI).
2. Keep suggested reply concise and professional.
3. Include clear next actions and ask for missing details when needed.
4. Use tools for classification and urgency checks when useful.
5. If user requests JSON, end with:
   {"category":"...", "priority":"...", "reply_draft":"...", "next_actions":[]}
"""


class EmailTriageAgent:
    """LangChain email triage assistant with lightweight tools."""

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
        self.tools = tools if tools is not None else get_email_triage_tools()
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

    def _try_parse_structured(self, content: str) -> Optional[EmailTriageReply]:
        try:
            m = re.search(r"\{[\s\S]*\}\s*$", content) or re.search(r"\{[\s\S]*\}", content)
            if m:
                return EmailTriageReply(**json.loads(m.group()))
        except Exception:
            pass
        return None

    def print_result(self, result: Dict[str, Any]) -> None:
        print("\n" + "=" * 70)
        print("EMAIL TRIAGE RESULT")
        print("=" * 70)
        print(f"Message: {result.get('message', 'N/A')}")
        print("-" * 70)
        print(result.get("content", ""))
        if result.get("structured"):
            print("-" * 70)
            print("Structured:", result["structured"].model_dump_json(indent=2))
        print("=" * 70 + "\n")


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Email Triage Agent")
    parser.add_argument(
        "--provider",
        default=os.getenv("EMAIL_AGENT_PROVIDER", "openai"),
        help="openai | anthropic | google | gemini | vertex",
    )
    parser.add_argument("--model", default=None, help="Model id (optional)")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--message", "-m", default=None, help="Email content to triage")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    agent = EmailTriageAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )
    msg = args.message or (
        "Subject: Urgent billing issue. I was charged twice and need this fixed today."
    )
    r = agent.chat(message=msg, verbose=args.verbose)
    agent.print_result(r)


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        _cli()
        return

    agent = EmailTriageAgent(provider=os.getenv("EMAIL_AGENT_PROVIDER", "openai"))
    result = agent.chat(
        message="Triage and draft a reply: Can we move tomorrow's meeting to Friday?",
        verbose=True,
    )
    agent.print_result(result)


if __name__ == "__main__":
    main()
