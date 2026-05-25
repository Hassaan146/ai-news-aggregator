"""LLM-based ranking agent for personalized digest feeds."""

from __future__ import annotations

import json
from dataclasses import dataclass

from dotenv import load_dotenv

from app.agent.llm_client import default_model, default_provider, generate_json
from app.profiles.user_profile import UserProfile

load_dotenv()

DEFAULT_RANKING_MODEL = default_model(default_provider())

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
    """Ranks digest candidates with the configured LLM and structured JSON output."""

    def __init__(
        self,
        model: str = DEFAULT_RANKING_MODEL,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key

    def rank_digest_items(
        self,
        profile: UserProfile,
        candidates: list[dict],
    ) -> list[LLMRankedItem]:
        """Rank digest candidates for the given user profile."""

        if not candidates:
            return []

        schema = {
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
                },
            },
            "required": ["ranked_items"],
        }
        data, _, _, _ = generate_json(
            system_instruction=RANKING_INSTRUCTIONS,
            user_prompt=json.dumps(
                {
                    "profile": profile_to_payload(profile),
                    "candidates": candidates,
                },
                ensure_ascii=False,
            ),
            schema=schema,
            model=self.model,
            api_key=self.api_key,
            max_output_tokens=2048,
            temperature=0,
        )
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
