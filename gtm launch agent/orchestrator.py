"""
Five-phase GTM launch planning: ICP → Positioning → Channels → Timeline → JSON.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from schemas import GTMLaunchReport

SYS_P1 = """You are a GTM strategist. From the product/situation brief, define ICP & PROBLEM/SOLUTION fit.
Output markdown: who buys, pain, urgency, alternatives today, buying motion (PLG, sales-led, hybrid)."""

SYS_P2 = """Craft POSITIONING: category, differentiation, proof points. Output:
- One-liner (category + unique value)
- 3 messaging pillars with proof hints
Avoid hype; be specific."""

SYS_P3 = """Propose CHANNEL PLAN: pick a focused set (not everything). For each channel: tactic + success signal.
Markdown bullets; include a reasonable early budget emphasis (time/CAC thinking, not dollar claims)."""

SYS_P4 = """Build a TIMELINE: phased plan ~30–60 days (adjust if user specified horizon).
Include dependencies (content, analytics, partnerships). Markdown phases."""

SYS_P5 = """Output ONLY valid JSON (no markdown fences):
{"icp_summary":"string","positioning_one_liner":"string","messaging_pillars":["string"],"channel_plan":["string"],"timeline_phases":["string"],"success_metrics":["string"],"risks_and_dependencies":["string"],"launch_checklist":["string"]}
Synthesize from prior phases; checklist should be actionable one-liners."""


def _content(msg: Any) -> str:
    return (getattr(msg, "content", None) or str(msg)).strip()


def _parse(text: str) -> Tuple[Optional[GTMLaunchReport], str]:
    raw = text.strip()
    try:
        m = re.search(r"\{[\s\S]*\}\s*$", raw) or re.search(r"\{[\s\S]*\}", raw)
        if m:
            return GTMLaunchReport(**json.loads(m.group())), raw
    except Exception:
        pass
    return None, raw


def run_gtm_pipeline(
    llm: Any,
    product_brief: str,
    extra_context: str = "",
    verbose: bool = False,
) -> dict:
    pb = (product_brief or "").strip()
    x = (extra_context or "").strip()
    base = f"## Product / launch brief\n{pb}\n"
    if x:
        base += f"\n## Extra context\n{x}\n"

    def inv(sys_txt: str, suf: str = "") -> str:
        return _content(
            llm.invoke([SystemMessage(content=sys_txt), HumanMessage(content=base + suf)])
        )

    if verbose:
        print("Phase 1/5: ICP...")
    p1 = inv(SYS_P1)

    if verbose:
        print("Phase 2/5: Positioning...")
    p2 = inv(SYS_P2, f"\n## Phase 1\n{p1}\n")

    if verbose:
        print("Phase 3/5: Channels...")
    p3 = inv(SYS_P3, f"\n## Phase 1\n{p1}\n\n## Phase 2\n{p2}\n")

    if verbose:
        print("Phase 4/5: Timeline...")
    p4 = inv(SYS_P4, f"\n## Phase 1\n{p1}\n\n## Phase 2\n{p2}\n\n## Phase 3\n{p3}\n")

    if verbose:
        print("Phase 5/5: JSON...")
    p5 = inv(
        SYS_P5,
        f"\n## Phase 1\n{p1}\n\n## Phase 2\n{p2}\n\n## Phase 3\n{p3}\n\n## Phase 4\n{p4}\n",
    )

    structured, _ = _parse(p5)
    return {
        "product_brief": pb,
        "phase1_icp": p1,
        "phase2_positioning": p2,
        "phase3_channels": p3,
        "phase4_timeline": p4,
        "phase5_raw": p5,
        "structured": structured,
    }
