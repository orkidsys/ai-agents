"""GTM reference frameworks."""
from __future__ import annotations

from langchain_core.tools import tool


@tool
def channel_mix_framework() -> str:
    """High-level channel thinking (not a media plan)."""
    return (
        "Channel dimensions:\n"
        "- Organic: SEO, community, product-led loops\n"
        "- Outbound: email, LinkedIn, partners\n"
        "- Paid: search, social, sponsorships\n"
        "- Product surfaces: in-app upsell, referrals, integrations marketplace\n"
        "Pick 2–3 bets for early stage; measure CAC and payback."
    )


@tool
def launch_readiness_categories() -> str:
    """Buckets for launch readiness."""
    return (
        "Readiness buckets:\n"
        "- Product: QA, analytics events, feature flags, rollback\n"
        "- GTM: positioning, pricing page, sales deck, demo script\n"
        "- Support: docs, FAQs, SLAs\n"
        "- Legal: terms, privacy, export controls if relevant\n"
        "- Comms: blog, email, social, changelog"
    )


def get_gtm_tools():
    return [channel_mix_framework, launch_readiness_categories]
