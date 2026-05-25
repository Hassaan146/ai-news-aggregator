"""LLM-based ranking agent for personalized digest feeds."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

from app.agent.digest_agent import GEMINI_API_URL
from app.profiles.user_profile import UserProfile

load_dotenv()

DEFAULT_RANKING_MODEL = "gemini-2.5-flash-lite"

RANKING_INSTRUCTIONS = """
You are a personalized AI news ranking agent.
Rank digest items for a user's stated interests.
Prefer items that directly match the user's preferred sources, content types, and keywords.
Also consider semantic relevance: for example, "agentic workflows" should match an interest in "agents".
Return every candidate exactly once.
Use deterministic, consistent scoring from 0 to 100.
Do not invent facts. Base reasons only on the provided candidate text and profile.
"""


@dataclass(frozen=True)
class LLMRankedItem:
    """One item ranked by the LLM."""

    digest_id: int
    rank: int
    relevance_score: int
    reason: str


class RankingAgent:
    """Ranks digest candidates with Gemini and structured JSON output."""

    def __init__(
        self,
        model: str = DEFAULT_RANKING_MODEL,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in environment.")

    def rank_digest_items(
        self,
        profile: UserProfile,
        candidates: list[dict],
    ) -> list[LLMRankedItem]:
        """Rank digest candidates for the given user profile."""

        if not candidates:
            return []

        response = requests.post(
            GEMINI_API_URL.format(model=self.model),
            params={"key": self.api_key},
            json={
                "systemInstruction": {
                    "parts": [{"text": RANKING_INSTRUCTIONS.strip()}],
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": json.dumps(
                                    {
                                        "profile": profile_to_payload(profile),
                                        "candidates": candidates,
                                    },
                                    ensure_ascii=False,
                                )
                            }
                        ],
                    }
                ],
                "generationConfig": {
                    "temperature": 0,
                    "responseMimeType": "application/json",
                    "responseSchema": {
                        "type": "object",
                        "properties": {
                            "ranked_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "digest_id": {"type": "integer"},
                                        "rank": {"type": "integer"},
                                        "relevance_score": {"type": "integer"},
                                        "reason": {"type": "string"},
                                    },
                                    "required": [
                                        "digest_id",
                                        "rank",
                                        "relevance_score",
                                        "reason",
                                    ],
                                },
                            }
                        },
                        "required": ["ranked_items"],
                    },
                    "maxOutputTokens": 2048,
                },
            },
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        text = extract_gemini_text(payload)
        data = json.loads(text)
        return [
            LLMRankedItem(
                digest_id=int(item["digest_id"]),
                rank=int(item["rank"]),
                relevance_score=int(item["relevance_score"]),
                reason=str(item["reason"]),
            )
            for item in data["ranked_items"]
        ]


def profile_to_payload(profile: UserProfile) -> dict:
    """Serialize a profile for LLM ranking."""

    return {
        "name": profile.name,
        "preferred_sources": list(profile.preferred_sources),
        "preferred_kinds": list(profile.preferred_kinds),
        "keywords": list(profile.keywords),
        "excluded_keywords": list(profile.excluded_keywords),
        "metadata": profile.metadata,
    }


def extract_gemini_text(response: dict) -> str:
    """Extract text from a Gemini generateContent response."""

    candidates = response.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini ranking response did not include candidates.")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts if part.get("text"))
    if not text:
        raise RuntimeError("Gemini ranking response did not include output text.")
    return text
