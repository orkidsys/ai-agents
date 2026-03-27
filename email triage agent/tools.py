"""
Tools for basic email triage logic.
"""
from __future__ import annotations

from langchain_core.tools import tool


@tool
def classify_email_category(email_text: str) -> str:
    """Classify email intent/category for routing."""
    text = (email_text or "").lower()
    if any(k in text for k in ("invoice", "charged", "payment", "refund", "billing")):
        return "billing"
    if any(k in text for k in ("bug", "error", "broken", "issue", "not working")):
        return "technical_support"
    if any(k in text for k in ("meeting", "schedule", "reschedule", "calendar")):
        return "scheduling"
    if any(k in text for k in ("complaint", "unhappy", "frustrated", "disappointed")):
        return "customer_complaint"
    return "general_inquiry"


@tool
def detect_urgency(email_text: str) -> str:
    """Detect likely urgency level from text cues."""
    text = (email_text or "").lower()
    if any(k in text for k in ("urgent", "asap", "immediately", "today", "critical")):
        return "high"
    if any(k in text for k in ("soon", "this week", "follow up", "reminder")):
        return "medium"
    return "low"


def get_email_triage_tools():
    return [classify_email_category, detect_urgency]
