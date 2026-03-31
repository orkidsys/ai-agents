"""
ADR Pipeline Agent — five-phase Architecture Decision Record workflow.
"""
from __future__ import annotations

import argparse
import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from llm_factory import build_chat_model
from orchestrator import run_adr_pipeline
from tools import get_adr_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

CHAT = """You help with ADRs and architecture decisions. Use tools for section templates or criteria examples.
For the full 5-phase pipeline run CLI with --pipeline."""


class ADRPipelineAgent:
    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.28,
        tools: Optional[List[Any]] = None,
    ):
        self.provider = provider.strip().lower()
        self.llm = build_chat_model(
            provider=self.provider,
            model_name=model_name,
            temperature=temperature,
        )
        self.tools = tools if tools is not None else get_adr_tools()
        self.agent = create_agent(model=self.llm, tools=self.tools, system_prompt=CHAT)

    def chat(self, message: str, verbose: bool = False) -> dict:
        t = (message or "").strip()
        if verbose:
            print(f"Provider: {self.provider}")
        out = self.agent.invoke({"messages": [HumanMessage(content=t)]})
        msgs = out.get("messages", [])
        content = ""
        if msgs:
            content = getattr(msgs[-1], "content", None) or str(msgs[-1])
        return {"message": t, "messages": msgs, "content": content}

    def run_pipeline(
        self,
        brief: str,
        extra_constraints: str = "",
        verbose: bool = False,
    ) -> dict:
        return run_adr_pipeline(
            self.llm,
            brief=brief,
            extra_constraints=extra_constraints,
            verbose=verbose,
        )

    def print_pipeline(self, r: dict) -> None:
        print("\n" + "=" * 70)
        print("ADR PIPELINE (5 phases)")
        print("=" * 70)
        for k in ("phase1_context", "phase2_options", "phase3_evaluation", "phase4_decision_markdown"):
            print(f"\n--- {k} ---\n")
            print(r.get(k, ""))
        print("\n--- phase5 (raw) ---\n")
        print(r.get("phase5_raw", ""))
        if r.get("structured"):
            print("\n--- structured ---\n")
            print(r["structured"].model_dump_json(indent=2))
        print("=" * 70 + "\n")


def _cli() -> None:
    p = argparse.ArgumentParser(description="ADR Pipeline Agent")
    p.add_argument("--provider", default=os.getenv("ADR_PIPELINE_AGENT_PROVIDER", "openai"))
    p.add_argument("--model", default=None)
    p.add_argument("--temperature", type=float, default=0.28)
    p.add_argument("--pipeline", action="store_true", help="Run full 5-phase ADR pipeline")
    p.add_argument("--constraints", default="", help="Extra constraints text or path to file")
    p.add_argument("--message", "-m", default=None)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    agent = ADRPipelineAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )

    if args.pipeline:
        brief = args.message or (
            "We need to choose between row-level security in Postgres vs application-layer auth "
            "for a multi-tenant B2B SaaS with ~500 tenants."
        )
        cons = args.constraints
        if cons and os.path.isfile(os.path.expanduser(cons)):
            with open(os.path.expanduser(cons), "r", encoding="utf-8", errors="replace") as f:
                cons = f.read()
        out = agent.run_pipeline(brief=brief, extra_constraints=cons or "", verbose=args.verbose)
        agent.print_pipeline(out)
        return

    msg = args.message or "List ADR section headings I should use."
    print(agent.chat(msg, verbose=args.verbose).get("content", ""))


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        _cli()
        return
    agent = ADRPipelineAgent(provider=os.getenv("ADR_PIPELINE_AGENT_PROVIDER", "openai"))
    r = agent.run_pipeline(
        brief="Replace REST internal APIs with gRPC between two services.",
        extra_constraints="Team knows REST well; 6 week deadline.",
        verbose=True,
    )
    agent.print_pipeline(r)


if __name__ == "__main__":
    main()
