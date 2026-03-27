"""
Lightweight tools for interview question typing and STAR structure.
"""
from __future__ import annotations

from langchain_core.tools import tool


@tool
def classify_question_type(question_text: str) -> str:
    """Roughly classify an interview prompt for routing and framing."""
    text = (question_text or "").lower()
    if any(
        k in text
        for k in (
            "design ",
            "how would you scale",
            "cap theorem",
            "distributed",
            "load balancer",
            "cache",
        )
    ):
        return "system_design"
    if any(
        k in text
        for k in (
            "tell me about a time",
            "conflict",
            "failure",
            "strength",
            "weakness",
            "leadership",
            "disagree",
        )
    ):
        return "behavioral"
    if any(k in text for k in ("salary", "compensation", "offer", "negotiate")):
        return "compensation"
    if any(
        k in text
        for k in (
            "leetcode",
            "big o",
            "complexity",
            "array",
            "graph",
            "tree",
            "sort",
            "mutex",
        )
    ):
        return "technical_coding"
    return "general"


@tool
def star_framework_outline(topic_hint: str = "") -> str:
    """Return a STAR outline template. Optional topic_hint is ignored but keeps the tool simple."""
    _ = topic_hint
    return (
        "STAR answer skeleton:\n"
        "- Situation: 1–2 sentences on context and stakes.\n"
        "- Task: what you were responsible for.\n"
        "- Action: 2–4 bullets on what *you* did (not the team vaguely).\n"
        "- Result: measurable outcome, learning, or follow-up."
    )


def get_interview_prep_tools():
    return [classify_question_type, star_framework_outline]
