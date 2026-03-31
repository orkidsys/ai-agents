"""Multi-provider chat model factory."""
from __future__ import annotations

import os
from typing import Any, Optional

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet-20241022",
    "google": "gemini-2.0-flash",
    "gemini": "gemini-2.0-flash",
    "vertex": "gemini-2.0-flash",
}


def _resolve_model(provider: str, model_name: Optional[str]) -> str:
    if model_name and model_name.strip():
        return model_name.strip()
    env = os.getenv("GTM_LAUNCH_AGENT_MODEL")
    if env:
        return env.strip()
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS["openai"])


def build_chat_model(
    provider: str,
    model_name: Optional[str] = None,
    temperature: float = 0.42,
) -> Any:
    p = provider.strip().lower()
    if p == "gemini":
        p = "google"
    model = _resolve_model(p, model_name)

    if p == "openai":
        from langchain_openai import ChatOpenAI

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY is not set.")
        return ChatOpenAI(model=model, temperature=temperature, api_key=key)

    if p == "anthropic":
        from langchain_anthropic import ChatAnthropic

        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is not set.")
        return ChatAnthropic(model=model, temperature=temperature, api_key=key)

    if p == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY is not set.")
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=key)

    if p == "vertex":
        from langchain_google_vertexai import ChatVertexAI

        proj = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or os.getenv("VERTEX_PROJECT")
        loc = os.getenv("GOOGLE_CLOUD_LOCATION") or os.getenv("VERTEX_LOCATION") or "us-central1"
        if not proj:
            raise ValueError("GOOGLE_CLOUD_PROJECT (or GCP_PROJECT or VERTEX_PROJECT) is not set.")
        return ChatVertexAI(model=model, temperature=temperature, project=proj, location=loc)

    raise ValueError(f"Unknown provider '{provider}'.")
