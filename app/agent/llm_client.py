"""Shared LLM client helpers for digest and ranking agents."""

from __future__ import annotations

import json
import os

import requests

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"


def default_provider() -> str:
    """Choose the configured LLM provider."""

    provider = os.getenv("LLM_PROVIDER")
    if provider:
        return provider.strip().lower()
    if os.getenv("GROQ_API_KEY"):
        return "groq"
    return "gemini"


def default_model(provider: str) -> str:
    """Return the default model for a provider."""

    configured = os.getenv("LLM_MODEL")
    if configured:
        return configured.strip()
    if provider == "groq":
        return DEFAULT_GROQ_MODEL
    return DEFAULT_GEMINI_MODEL


def resolve_api_key(provider: str, api_key: str | None = None) -> str:
    """Return the provider API key from an explicit value or environment."""

    if api_key:
        return api_key
    if provider == "groq":
        key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("Missing GROQ_API_KEY in environment.")
        return key
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Missing GEMINI_API_KEY in environment.")
    return key


def generate_json(
    *,
    system_instruction: str,
    user_prompt: str,
    schema: dict,
    model: str | None = None,
    api_key: str | None = None,
    max_output_tokens: int = 512,
    temperature: float = 0,
) -> tuple[dict, dict, str | None, str]:
    """Generate a JSON object using the configured LLM provider."""

    provider = default_provider()
    selected_model = model or default_model(provider)
    selected_key = resolve_api_key(provider, api_key)
    if provider == "groq":
        return generate_groq_json(
            system_instruction=system_instruction,
            user_prompt=user_prompt,
            schema=schema,
            model=selected_model,
            api_key=selected_key,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )
    return generate_gemini_json(
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        schema=schema,
        model=selected_model,
        api_key=selected_key,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
    )


def generate_groq_json(
    *,
    system_instruction: str,
    user_prompt: str,
    schema: dict,
    model: str,
    api_key: str,
    max_output_tokens: int,
    temperature: float,
) -> tuple[dict, dict, str | None, str]:
    """Generate JSON through Groq's OpenAI-compatible API."""

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_instruction.strip()},
                {
                    "role": "user",
                    "content": (
                        f"{user_prompt}\n\nReturn only JSON matching this schema:\n"
                        f"{json.dumps(schema, ensure_ascii=False)}"
                    ),
                },
            ],
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "response_format": {"type": "json_object"},
        },
        timeout=90,
    )
    response.raise_for_status()
    raw_response = response.json()
    message = raw_response["choices"][0]["message"]
    output_text = (message.get("content") or "").strip()
    if not output_text:
        raise RuntimeError("Groq response did not include output text.")
    return json.loads(output_text), raw_response, raw_response.get("id"), model


def generate_gemini_json(
    *,
    system_instruction: str,
    user_prompt: str,
    schema: dict,
    model: str,
    api_key: str,
    max_output_tokens: int,
    temperature: float,
) -> tuple[dict, dict, str | None, str]:
    """Generate JSON through Gemini."""

    response = requests.post(
        GEMINI_API_URL.format(model=model),
        params={"key": api_key},
        json={
            "systemInstruction": {
                "parts": [{"text": system_instruction.strip()}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "maxOutputTokens": max_output_tokens,
            },
        },
        timeout=90,
    )
    response.raise_for_status()
    raw_response = response.json()
    output_text = extract_gemini_text(raw_response)
    return json.loads(output_text), raw_response, raw_response.get("responseId"), model


def extract_gemini_text(response: dict) -> str:
    """Extract text from a Gemini generateContent response."""

    candidates = response.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini response did not include candidates.")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    output_text = "".join(text_parts).strip()
    if not output_text:
        raise RuntimeError("Gemini response did not include output text.")
    return output_text
