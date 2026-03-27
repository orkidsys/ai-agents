"""
Interview Prep Agent - practice answers for behavioral and technical interviews.
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
from schemas import InterviewReply
from tools import get_interview_prep_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """You are InterviewPrepAgent, a practical interview coach.

## Rules
1. Tailor advice to the role and seniority when the user provides them; otherwise ask once for missing context.
2. Do not invent the user's past jobs, metrics, or projects. Use placeholders like [your team size] if specifics are unknown.
3. For behavioral questions, prefer STAR (Situation, Task, Action, Result) with concise bullets the user can memorize.
4. For technical questions, explain trade-offs and suggest follow-up practice prompts.
5. Use tools when helpful: classify_question_type and star_framework_outline.
6. Stay professional and encouraging; avoid discriminatory or unethical interview "hacks".
7. If JSON is requested, end with:
   {"question_type":"...","sample_answer_bullets":[],"follow_up_drills":[],"tips":[]}
"""


class InterviewPrepAgent:
    """LangChain interview preparation assistant."""

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
        self.tools = tools if tools is not None else get_interview_prep_tools()
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

    def _try_parse_structured(self, content: str) -> Optional[InterviewReply]:
        try:
            m = re.search(r"\{[\s\S]*\}\s*$", content) or re.search(r"\{[\s\S]*\}", content)
            if m:
                return InterviewReply(**json.loads(m.group()))
        except Exception:
            pass
        return None

    def print_result(self, result: Dict[str, Any]) -> None:
        print("\n" + "=" * 70)
        print("INTERVIEW PREP RESULT")
        print("=" * 70)
        print(f"Message: {result.get('message', 'N/A')}")
        print("-" * 70)
        print(result.get("content", ""))
        if result.get("structured"):
            print("-" * 70)
            print("Structured:", result["structured"].model_dump_json(indent=2))
        print("=" * 70 + "\n")


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Interview Prep Agent")
    parser.add_argument(
        "--provider",
        default=os.getenv("INTERVIEW_AGENT_PROVIDER", "openai"),
        help="openai | anthropic | google | gemini | vertex",
    )
    parser.add_argument("--model", default=None, help="Model id (optional)")
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--message", "-m", default=None, help="Interview question or scenario")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    agent = InterviewPrepAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )
    msg = args.message or (
        "I'm interviewing for a mid-level backend role. "
        "How should I answer: Tell me about a time you disagreed with your manager?"
    )
    r = agent.chat(message=msg, verbose=args.verbose)
    agent.print_result(r)


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        _cli()
        return

    agent = InterviewPrepAgent(provider=os.getenv("INTERVIEW_AGENT_PROVIDER", "openai"))
    result = agent.chat(
        message="Help me structure an answer for: Explain how you would design a URL shortener.",
        verbose=True,
    )
    agent.print_result(result)


if __name__ == "__main__":
    main()
