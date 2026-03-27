"""
Tools for documentation structure and changelog formatting.
"""
from __future__ import annotations

from langchain_core.tools import tool


_OUTLINES = {
    "readme": [
        "Overview",
        "Requirements",
        "Installation",
        "Configuration",
        "Usage",
        "Development",
        "License",
    ],
    "api": [
        "Overview",
        "Authentication",
        "Base URL and versioning",
        "Endpoints (grouped by resource)",
        "Request/response schemas",
        "Errors and rate limits",
        "Examples",
    ],
    "runbook": [
        "Service overview",
        "Dependencies and owners",
        "Common procedures",
        "Alerts and dashboards",
        "Incident response",
        "Rollback",
        "Contacts",
    ],
    "changelog": [
        "Unreleased (optional)",
        "Version headers with date",
        "Added / Changed / Fixed / Removed",
        "Migration notes",
    ],
    "adr": [
        "Title and status",
        "Context",
        "Decision",
        "Consequences",
        "Alternatives considered",
    ],
}


@tool
def suggest_doc_outline(doc_type: str) -> str:
    """Return a sensible section outline for a documentation type.

    doc_type: readme | api | runbook | changelog | adr (case-insensitive).
    """
    key = (doc_type or "readme").strip().lower()
    if key not in _OUTLINES:
        key = "readme"
    sections = _OUTLINES[key]
    return "Suggested outline:\n" + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(sections))


@tool
def format_changelog_entry(version: str, bullets: str) -> str:
    """Format a Keep-a-Changelog-style block from a version label and newline-separated bullets."""
    ver = (version or "x.y.z").strip() or "x.y.z"
    lines = [ln.strip() for ln in (bullets or "").splitlines() if ln.strip()]
    if not lines:
        lines = ["(no items provided)"]
    body = "\n".join(f"- {line}" for line in lines)
    return f"## [{ver}] — YYYY-MM-DD\n\n{body}\n"


def get_technical_doc_tools():
    return [suggest_doc_outline, format_changelog_entry]
