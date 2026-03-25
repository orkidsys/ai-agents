"""
Build LangChain chat models for multiple providers (OpenAI, Anthropic, Gemini, Vertex AI).
"""
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
    env_key = os.getenv("GENERAL_AGENT_MODEL")
    if env_key:
        return env_key.strip()
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS["openai"])


def build_chat_model(
    provider: str,
    model_name: Optional[str] = None,
    temperature: float = 0.3,
) -> Any:
    """
    Instantiate a LangChain chat model for the given provider.

    Args:
        provider: openai | anthropic | google | gemini | vertex
        model_name: Model id; defaults per provider or GENERAL_AGENT_MODEL
        temperature: Sampling temperature
    """
    p = provider.strip().lower()
    if p == "gemini":
        p = "google"

    model = _resolve_model(p, model_name)

    if p == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError(
                "OpenAI provider requires langchain-openai. pip install langchain-openai"
            ) from e
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set (required for provider=openai).")
        return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)

    if p == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            raise ImportError(
                "Anthropic provider requires langchain-anthropic. pip install langchain-anthropic"
            ) from e
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set (required for provider=anthropic).")
        return ChatAnthropic(model=model, temperature=temperature, api_key=api_key)

    if p == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as e:
            raise ImportError(
                "Google Gemini requires langchain-google-genai. pip install langchain-google-genai"
            ) from e
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY or GEMINI_API_KEY is not set (required for provider=google/gemini)."
            )
        return ChatGoogleGenerativeAI(model=model, temperature=temperature, google_api_key=api_key)

    if p == "vertex":
        try:
            from langchain_google_vertexai import ChatVertexAI
        except ImportError as e:
            raise ImportError(
                "Vertex AI requires langchain-google-vertexai. pip install langchain-google-vertexai"
            ) from e
        project = (
            os.getenv("GOOGLE_CLOUD_PROJECT")
            or os.getenv("GCP_PROJECT")
            or os.getenv("VERTEX_PROJECT")
        )
        location = (
            os.getenv("GOOGLE_CLOUD_LOCATION")
            or os.getenv("VERTEX_LOCATION")
            or "us-central1"
        )
        if not project:
            raise ValueError(
                "Vertex AI requires GOOGLE_CLOUD_PROJECT (or GCP_PROJECT or VERTEX_PROJECT)."
            )
        return ChatVertexAI(
            model=model,
            temperature=temperature,
            project=project,
            location=location,
        )

    supported = "openai, anthropic, google (gemini), vertex"
    raise ValueError(f"Unknown provider '{provider}'. Use one of: {supported}")
