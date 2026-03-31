"""
Five-phase threat modeling: Scope → Assets → STRIDE threats → Mitigations → JSON.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from schemas import ThreatModelReport

SYS_P1 = """You are a security architect. From the system description, define SCOPE & TRUST BOUNDARIES.
Output markdown: system summary, actors, main data flows, trust boundaries (where untrusted meets trusted), assumptions."""

SYS_P2 = """List KEY ASSETS to protect: data classes, credentials, admin surfaces, critical workflows.
Markdown bullets; map each asset to rough confidentiality/integrity/availability importance."""

SYS_P3 = """Perform STRIDE-style threat brainstorming for this system. For each relevant STRIDE category,
list concrete threats tied to components (not generic platitudes). Markdown with STRIDE headings."""

SYS_P4 = """Propose MITIGATIONS and PRIORITIES: map mitigations to threats, suggest priority (P0–P3) and rollout order.
Include detection/telemetry ideas. Markdown."""

SYS_P5 = """Output ONLY valid JSON (no markdown fences):
{"scope_summary":"string","assumptions":["string"],"threats":[{"component":"string","stride_category":"string","threat_statement":"string","mitigation":"string","priority":"string"}],"open_questions":["string"]}
Consolidate from prior phases; limit to ~12 threats max, most important first."""


def _content(msg: Any) -> str:
    return (getattr(msg, "content", None) or str(msg)).strip()


def _parse(text: str) -> Tuple[Optional[ThreatModelReport], str]:
    raw = text.strip()
    try:
        m = re.search(r"\{[\s\S]*\}\s*$", raw) or re.search(r"\{[\s\S]*\}", raw)
        if m:
            return ThreatModelReport(**json.loads(m.group())), raw
    except Exception:
        pass
    return None, raw


def run_threat_model_pipeline(
    llm: Any,
    system_description: str,
    extra_context: str = "",
    verbose: bool = False,
) -> dict:
    sd = (system_description or "").strip()
    x = (extra_context or "").strip()
    base = f"## System / feature description\n{sd}\n"
    if x:
        base += f"\n## Extra context\n{x}\n"

    def invoke(sys_txt: str, suffix: str = "") -> str:
        r = llm.invoke(
            [SystemMessage(content=sys_txt), HumanMessage(content=base + suffix)]
        )
        return _content(r)

    if verbose:
        print("Phase 1/5: Scope & boundaries...")
    p1 = invoke(SYS_P1)

    if verbose:
        print("Phase 2/5: Assets...")
    p2 = invoke(SYS_P2, f"\n## Phase 1\n{p1}\n")

    if verbose:
        print("Phase 3/5: STRIDE threats...")
    p3 = invoke(
        SYS_P3,
        f"\n## Phase 1\n{p1}\n\n## Phase 2\n{p2}\n",
    )

    if verbose:
        print("Phase 4/5: Mitigations...")
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

    structured, _ = _parse(p5)
    return {
        "system_description": sd,
        "phase1_scope": p1,
        "phase2_assets": p2,
        "phase3_stride": p3,
        "phase4_mitigations": p4,
        "phase5_raw": p5,
        "structured": structured,
    }
