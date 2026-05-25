"""Helpers for turning LLM errors into user-facing status messages."""

from __future__ import annotations

import requests


def classify_llm_error(error: str | None) -> str | None:
    """Classify a Gemini/LLM error string without exposing secrets."""

    if not error:
        return None

    lowered = error.lower()
    if "missing gemini_api_key" in lowered:
        return "missing_key"
    if "429" in lowered or "rate" in lowered or "quota" in lowered:
        return "rate_limited"
    if "400" in lowered or "401" in lowered or "403" in lowered or "api key" in lowered:
        return "invalid_or_forbidden_key"
    if "timeout" in lowered or "timed out" in lowered:
        return "timeout"
    return "unavailable"


def classify_http_error(exc: requests.HTTPError) -> str:
    """Classify an HTTP error from Gemini."""

    status_code = exc.response.status_code if exc.response is not None else None
    if status_code == 429:
        return "rate_limited"
    if status_code in {400, 401, 403}:
        return "invalid_or_forbidden_key"
    if status_code and status_code >= 500:
        return "unavailable"
    return classify_llm_error(str(exc)) or "unavailable"


def llm_status_message(status: str | None) -> str | None:
    """Return a friendly user-facing message for an LLM status code."""

    if status is None or status == "ok":
        return None
    if status == "missing_key":
        return "The backend AI API key is missing. Please configure GROQ_API_KEY or GEMINI_API_KEY on Render."
    if status == "rate_limited":
        return "The AI key is currently busy or rate-limited. Too many requests may be using it right now. Please try again later."
    if status == "invalid_or_forbidden_key":
        return "The backend AI API key is invalid, forbidden, or not enabled for this model. Please update the key on Render and redeploy."
    if status == "timeout":
        return "The AI request timed out. Please try again in a moment."
    return "The AI service is currently unavailable. Please try again later."
