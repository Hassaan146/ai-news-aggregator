"""Gemini-powered agent for creating digest summaries."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

from app.database.models import NewsItem

load_dotenv()

DEFAULT_DIGEST_MODEL = "gemini-2.5-flash-lite"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

DIGEST_INSTRUCTIONS = """
You are an AI news digest editor.
Your job is to turn one scraped news item into a useful digest entry.
Write a concise, factual title and a two to three sentence summary.
Prefer concrete details from the source item. Do not invent facts.
If the source item is weak or navigation-like, summarize only what is clearly present.
"""

@dataclass(frozen=True)
class DigestAgentResult:
    """Structured output returned by the digest agent."""

    title: str
    summary: str
    model: str
    response_id: str | None
    raw_response: dict


class DigestAgent:
    """Creates short structured digest entries with the Gemini API."""

    def __init__(
        self,
        model: str = DEFAULT_DIGEST_MODEL,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in environment.")

    def summarize_news_item(self, news_item: NewsItem) -> DigestAgentResult:
        """Generate one digest entry for a database news item."""

        response = requests.post(
            GEMINI_API_URL.format(model=self.model),
            params={"key": self.api_key},
            json={
                "systemInstruction": {
                    "parts": [{"text": DIGEST_INSTRUCTIONS.strip()}],
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": build_digest_input(news_item)}],
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseSchema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "A concise digest title for this item.",
                            },
                            "summary": {
                                "type": "string",
                                "description": "A factual two to three sentence summary.",
                            },
                        },
                        "required": ["title", "summary"],
                    },
                    "maxOutputTokens": 300,
                },
            },
            timeout=60,
        )
        response.raise_for_status()
        raw_response = response.json()
        output_text = extract_gemini_text(raw_response)
        payload = json.loads(output_text)
        return DigestAgentResult(
            title=payload["title"].strip(),
            summary=payload["summary"].strip(),
            model=self.model,
            response_id=raw_response.get("responseId"),
            raw_response=raw_response,
        )


def build_digest_input(news_item: NewsItem) -> str:
    """Build the model input from a stored news item."""

    metadata = json.dumps(news_item.item_metadata or {}, ensure_ascii=False)
    parts = [
        f"Source: {news_item.source}",
        f"Type: {news_item.kind}",
        f"Original title: {news_item.title}",
        f"URL: {news_item.url}",
        f"Published at: {news_item.published_at}",
        f"Scraped summary: {news_item.summary or ''}",
        f"Content: {news_item.content or ''}",
        f"Transcript: {news_item.transcript or ''}",
        f"Metadata: {metadata}",
    ]
    return "\n".join(parts)


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
