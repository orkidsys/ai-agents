"""
Threat Modeling Agent — five-phase STRIDE-oriented threat modeling.
"""
from __future__ import annotations

import argparse
import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from llm_factory import build_chat_model
from orchestrator import run_threat_model_pipeline
from tools import get_threat_model_tools

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

CHAT = """You support lightweight threat modeling. Use STRIDE and trust-boundary tools when asked.
For a full 5-phase model run the CLI with --pipeline."""


class ThreatModelingAgent:
    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.22,
        tools: Optional[List[Any]] = None,
    ):
        self.provider = provider.strip().lower()
        self.llm = build_chat_model(
            provider=self.provider,
            model_name=model_name,
            temperature=temperature,
        )
        self.tools = tools if tools is not None else get_threat_model_tools()
        self.agent = create_agent(model=self.llm, tools=self.tools, system_prompt=CHAT)

    def chat(self, message: str, verbose: bool = False) -> dict:
        t = (message or "").strip()
        if verbose:
            print(f"Provider: {self.provider}")
        out = self.agent.invoke({"messages": [HumanMessage(content=t)]})
        msgs = out.get("messages", [])
        c = getattr(msgs[-1], "content", None) or str(msgs[-1]) if msgs else ""
        return {"message": t, "messages": msgs, "content": c}

    def run_pipeline(
        self,
        system_description: str,
        extra_context: str = "",
        verbose: bool = False,
    ) -> dict:
        return run_threat_model_pipeline(
            self.llm,
            system_description=system_description,
            extra_context=extra_context,
            verbose=verbose,
        )

    def print_pipeline(self, r: dict) -> None:
        print("\n" + "=" * 70)
        print("THREAT MODEL PIPELINE")
        print("=" * 70)
        for k in ("phase1_scope", "phase2_assets", "phase3_stride", "phase4_mitigations"):
            print(f"\n--- {k} ---\n")
            print(r.get(k, ""))
        print("\n--- phase5 raw ---\n")
        print(r.get("phase5_raw", ""))
        if r.get("structured"):
            print("\n--- structured ---\n")
            print(r["structured"].model_dump_json(indent=2))
        print("=" * 70 + "\n")


def _cli() -> None:
    p = argparse.ArgumentParser(description="Threat Modeling Agent")
    p.add_argument("--provider", default=os.getenv("THREAT_MODEL_AGENT_PROVIDER", "openai"))
    p.add_argument("--model", default=None)
    p.add_argument("--temperature", type=float, default=0.22)
    p.add_argument("--pipeline", action="store_true")
    p.add_argument("--context", default="")
    p.add_argument("--message", "-m", default=None)
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    agent = ThreatModelingAgent(
        provider=args.provider,
        model_name=args.model,
        temperature=args.temperature,
    )

    if args.pipeline:
        desc = args.message or (
            "Public REST API behind API gateway; JWT auth; Postgres; admin portal with session cookies; "
            "file uploads to object storage."
        )
        ctx = args.context
        if ctx and os.path.isfile(os.path.expanduser(ctx)):
            with open(os.path.expanduser(ctx), "r", encoding="utf-8", errors="replace") as f:
                ctx = f.read()
        out = agent.run_pipeline(
            system_description=desc,
            extra_context=ctx or "",
            verbose=args.verbose,
        )
        agent.print_pipeline(out)
        return

    print(agent.chat(args.message or "Explain STRIDE in one short paragraph.", verbose=args.verbose).get("content", ""))


def main() -> None:
    import sys

    if len(sys.argv) > 1:
        _cli()
        return
    agent = ThreatModelingAgent(provider=os.getenv("THREAT_MODEL_AGENT_PROVIDER", "openai"))
    r = agent.run_pipeline(
        system_description="Mobile app talks to BFF; BFF calls payment microservice; webhooks from provider.",
        verbose=True,
    )
    agent.print_pipeline(r)


if __name__ == "__main__":
    main()
