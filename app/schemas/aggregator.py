"""Pydantic schemas for profile-aware digest aggregation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.agent.aggregator_agent import AggregatedDigestItem
from app.profiles.user_profile import UserProfile

BadgeType = Literal["source", "kind", "keyword", "excluded", "recency", "other"]


class MatchBadge(BaseModel):
    """Explains why an item matched a user profile."""

    model_config = ConfigDict(frozen=True)

    type: BadgeType
    label: str
    value: str


class UserProfileSchema(BaseModel):
    """Serializable user interest profile."""

    model_config = ConfigDict(frozen=True)

    name: str
    preferred_sources: list[str] = Field(default_factory=list)
    preferred_kinds: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)
    source_weight: int
    kind_weight: int
    keyword_weight: int
    recency_weight: int
    metadata: dict = Field(default_factory=dict)

    @classmethod
    def from_profile(cls, profile: UserProfile) -> "UserProfileSchema":
        """Build a schema from an internal user profile."""

        return cls(
            name=profile.name,
            preferred_sources=list(profile.preferred_sources),
            preferred_kinds=list(profile.preferred_kinds),
            keywords=list(profile.keywords),
            excluded_keywords=list(profile.excluded_keywords),
            source_weight=profile.source_weight,
            kind_weight=profile.kind_weight,
            keyword_weight=profile.keyword_weight,
            recency_weight=profile.recency_weight,
            metadata=profile.metadata,
        )


class AggregatedDigestItemSchema(BaseModel):
    """Stable identity model for one ranked digest item."""

    model_config = ConfigDict(frozen=True)

    digest_id: int
    news_item_id: int
    identity_key: str
    source: str
    kind: str
    title: str
    summary: str
    url: HttpUrl
    published_at: datetime | None = None
    score: int
    rank: int
    rank_source: Literal["llm", "deterministic", "fallback"]
    llm_reason: str | None = None
    badges: list[MatchBadge] = Field(default_factory=list)

    @classmethod
    def from_aggregated_item(
        cls,
        item: AggregatedDigestItem,
        rank: int,
    ) -> "AggregatedDigestItemSchema":
        """Build a stable frontend/API schema from an aggregated item."""

        return cls(
            digest_id=item.digest_id,
            news_item_id=item.news_item_id,
            identity_key=f"digest:{item.digest_id}:news:{item.news_item_id}",
            source=item.source,
            kind=item.kind,
            title=item.title,
            summary=item.summary,
            url=item.url,
            published_at=item.published_at,
            score=item.score,
            rank=rank,
            rank_source=item.rank_source,
            llm_reason=item.llm_reason,
            badges=parse_match_badges(item.matched_reasons),
        )


class AggregatedDigestResponse(BaseModel):
    """Complete response for a personalized digest request."""

    model_config = ConfigDict(frozen=True)

    profile: UserProfileSchema
    lookback_hours: int
    ranking_method: Literal["llm", "deterministic", "fallback"]
    fallback_reason: str | None = None
    total_items: int
    items: list[AggregatedDigestItemSchema]


class TopDigestResponse(BaseModel):
    """Top ranked digest/article response for website users."""

    model_config = ConfigDict(frozen=True)

    profile: UserProfileSchema
    lookback_hours: int
    top_n: int
    ranking_method: Literal["llm", "deterministic", "fallback"]
    fallback_reason: str | None = None
    total_items: int
    items: list[AggregatedDigestItemSchema]


def parse_match_badges(reasons: tuple[str, ...]) -> list[MatchBadge]:
    """Convert internal match reasons into display/API badges."""

    badges: list[MatchBadge] = []
    for reason in reasons:
        if ":" in reason:
            reason_type, value = reason.split(":", 1)
        else:
            reason_type, value = reason, reason

        badge_type: BadgeType
        label: str
        if reason_type == "source":
            badge_type = "source"
            label = "Source"
        elif reason_type == "kind":
            badge_type = "kind"
            label = "Type"
        elif reason_type == "keyword":
            badge_type = "keyword"
            label = "Keyword"
        elif reason_type == "excluded":
            badge_type = "excluded"
            label = "Excluded"
        elif reason_type == "has_published_at":
            badge_type = "recency"
            label = "Recent"
            value = "published"
        else:
            badge_type = "other"
            label = reason_type.replace("_", " ").title()

        badges.append(MatchBadge(type=badge_type, label=label, value=value))
    return badges
