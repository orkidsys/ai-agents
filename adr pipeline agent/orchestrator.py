"""
Five-phase ADR pipeline: Context → Options → Evaluation → Narrative → Structured JSON.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from schemas import ADRReport

SYS_P1 = """You are an architecture scribe. Extract CONTEXT for an ADR from the user's brief.
Output markdown: Problem statement, Business/technical drivers, Constraints, Current state, Unknowns to validate."""

SYS_P2 = """You are a solutions architect. Given the context, list OPTIONS (3–5 realistic alternatives).
For each: one-line summary, pros, cons, when it's the wrong fit. Markdown bullets."""

SYS_P3 = """You are evaluating tradeoffs. Given context + options, produce an EVALUATION.
Use explicit criteria (performance, cost, complexity, security, team, ops). Markdown: criteria list + comparison
(table or bullet matrix). Do not pick a winner yet."""

SYS_P4 = """You are the decision owner. Based on context, options, and evaluation, write the DECISION NARRATIVE:
recommended option, rationale tied to criteria, Consequences (positive/negative), and Alternatives rejected with reasons.
Markdown with clear headings."""

SYS_P5 = """You consolidate the ADR into one JSON object for machines. Reply with ONLY valid JSON (no markdown fences), shape:
{"title":"string","status":"string","context":"string (multi-sentence OK)","decision":"string","consequences":["string"],"alternatives_considered":["string"],"evaluation_criteria":["string"],"risks_and_mitigations":["string"],"follow_up_actions":["string"]}
Use concise strings in arrays. Title should be slug-friendly."""


def _content(msg: Any) -> str:
    return (getattr(msg, "content", None) or str(msg)).strip()


def _parse_json(text: str) -> Tuple[Optional[ADRReport], str]:
    raw = text.strip()
    try:
        m = re.search(r"\{[\s\S]*\}\s*$", raw) or re.search(r"\{[\s\S]*\}", raw)
        if m:
            return ADRReport(**json.loads(m.group())), raw
    except Exception:
        pass
    return None, raw


def run_adr_pipeline(
    llm: Any,
    brief: str,
    extra_constraints: str = "",
    verbose: bool = False,
) -> dict:
    b = (brief or "").strip()
    c = (extra_constraints or "").strip()
    base = f"## ADR brief\n{b}\n"
    if c:
        base += f"\n## Extra constraints\n{c}\n"

    def invoke(sys_txt: str, user_extra: str = "") -> str:
        u = base + user_extra if user_extra else base
        r = llm.invoke([SystemMessage(content=sys_txt), HumanMessage(content=u)])
        return _content(r)

    if verbose:
        print("Phase 1/5: Context...")
    p1 = invoke(SYS_P1)

    if verbose:
        print("Phase 2/5: Options...")
    p2 = invoke(
        SYS_P2,
        f"\n## Phase 1 (Context)\n{p1}\n",
    )

    if verbose:
        print("Phase 3/5: Evaluation...")
    p3 = invoke(
        SYS_P3,
        f"\n## Phase 1 (Context)\n{p1}\n\n## Phase 2 (Options)\n{p2}\n",
    )

    if verbose:
        print("Phase 4/5: Decision narrative...")
    p4 = invoke(
        SYS_P4,
        f"\n## Phase 1\n{p1}\n\n## Phase 2\n{p2}\n\n## Phase 3\n{p3}\n",
    )

    if verbose:
        print("Phase 5/5: JSON synthesis...")
    p5 = invoke(
        SYS_P5,
        f"\n## Phase 1\n{p1}\n\n## Phase 2\n{p2}\n\n## Phase 3\n{p3}\n\n## Phase 4\n{p4}\n",
    )

    structured, _ = _parse_json(p5)
    return {
        "brief": b,
        "phase1_context": p1,
        "phase2_options": p2,
        "phase3_evaluation": p3,
        "phase4_decision_markdown": p4,
        "phase5_raw": p5,
        "structured": structured,
    }
