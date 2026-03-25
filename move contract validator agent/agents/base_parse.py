"""Shared JSON parsing for Move specialist agents."""
import json
import re
from typing import List

from schemas import Category, Finding, Severity, SpecialistReport


def parse_specialist_json(text: str, agent_name: str) -> SpecialistReport:
    findings: List[Finding] = []
    summary = f"{agent_name} validation completed."
    confidence = "medium"
    try:
        json_match = re.search(r"\{[\s\S]*\}", text)
        if not json_match:
            return SpecialistReport(
                agent_name=agent_name,
                findings=[],
                summary=summary,
                confidence=confidence,
            )
        data = json.loads(json_match.group())
        raw = data.get("findings", [])
        for f in raw:
            try:
                cat_raw = (f.get("category") or "other").lower().strip()
                try:
                    category = Category(cat_raw)
                except ValueError:
                    category = Category.OTHER
                findings.append(
                    Finding(
                        title=f.get("title", "Unnamed"),
                        severity=Severity(f.get("severity", "informational")),
                        category=category,
                        description=f.get("description", ""),
                        location=f.get("location"),
                        code_snippet=f.get("code_snippet"),
                        recommendation=f.get("recommendation", ""),
                        agent_source=agent_name,
                    )
                )
            except Exception:
                continue
        summary = data.get("summary", summary)
        confidence = data.get("confidence", confidence)
    except Exception:
        pass
    return SpecialistReport(
        agent_name=agent_name,
        findings=findings,
        summary=summary,
        confidence=confidence,
    )
