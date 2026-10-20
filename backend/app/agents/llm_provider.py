"""Thin LLM provider abstraction over OpenAI-compatible chat completion APIs
(Groq, OpenAI, or any compatible gateway). When no provider is configured the
copilot still works end-to-end using deterministic templates — the LLM only
ever rephrases numbers that were already computed by the financial engine,
never invents them.
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

PROVIDER_BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1",
}


def is_llm_configured() -> bool:
    settings = get_settings()
    return bool(settings.llm_provider and settings.llm_provider != "none" and settings.llm_api_key)


def complete(messages: list[dict], temperature: float = 0.2, timeout: float = 20.0) -> str | None:
    """Returns the model's text response, or None if the LLM is unavailable/misconfigured
    or the request fails. Callers must always have a deterministic fallback ready."""
    settings = get_settings()
    if not is_llm_configured():
        return None

    base_url = settings.llm_base_url or PROVIDER_BASE_URLS.get(settings.llm_provider)
    if not base_url:
        logger.warning("Unknown LLM provider %s with no llm_base_url override", settings.llm_provider)
        return None

    try:
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": messages,
                "temperature": temperature,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        logger.exception("LLM completion failed; falling back to deterministic response")
        return None


def chat_with_tools(messages: list[dict], tools: list[dict], timeout: float = 30.0) -> dict:
    """One tool-calling round trip. Returns the assistant message dict (which may
    contain `tool_calls`). Raises on any failure so the caller can fall back."""
    settings = get_settings()
    if not is_llm_configured():
        raise RuntimeError("LLM not configured")
    base_url = settings.llm_base_url or PROVIDER_BASE_URLS.get(settings.llm_provider)
    if not base_url:
        raise RuntimeError(f"Unknown LLM provider {settings.llm_provider}")
    response = httpx.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0.1,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]
