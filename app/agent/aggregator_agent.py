"""Profile-aware aggregator for generated digest items."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.database.models import DigestItem, NewsItem
from app.profiles.user_profile import UserProfile


@dataclass(frozen=True)
class AggregatedDigestItem:
    """Digest item ranked for a user's profile."""

    digest_id: int
    news_item_id: int
    source: str
    kind: str
    title: str
    summary: str
    url: str
    published_at: datetime | None
    score: int
    matched_reasons: tuple[str, ...]
    rank_source: str = "deterministic"
    llm_reason: str | None = None


class AggregatorAgent:
    """Sorts digest items according to a user interest profile."""

    def rank(
        self,
        rows: list[tuple[DigestItem, NewsItem]],
        profile: UserProfile,
    ) -> list[AggregatedDigestItem]:
        """Return digest rows sorted by profile score and recency."""

        aggregated = [
            self.score_item(digest_item, news_item, profile)
            for digest_item, news_item in rows
        ]
        return sorted(
            aggregated,
            key=lambda item: (
                item.score,
                item.published_at or datetime.min.replace(tzinfo=UTC),
                item.digest_id,
            ),
            reverse=True,
        )

    def score_item(
        self,
        digest_item: DigestItem,
        news_item: NewsItem,
        profile: UserProfile,
    ) -> AggregatedDigestItem:
        """Score one digest item for a profile."""

        score = 0
        reasons: list[str] = []

        if digest_item.source in profile.preferred_sources:
            score += profile.source_weight
            reasons.append(f"source:{digest_item.source}")

        if digest_item.kind in profile.preferred_kinds:
            score += profile.kind_weight
            reasons.append(f"kind:{digest_item.kind}")

        searchable_text = " ".join(
            [
                digest_item.source,
                digest_item.kind,
                digest_item.digest_title,
                digest_item.digest_summary,
                news_item.title,
                news_item.summary or "",
            ]
        ).lower()

        for keyword in profile.keywords:
            if keyword.lower() in searchable_text:
                score += profile.keyword_weight
                reasons.append(f"keyword:{keyword}")

        for keyword in profile.excluded_keywords:
            if keyword.lower() in searchable_text:
                score -= profile.keyword_weight
                reasons.append(f"excluded:{keyword}")

        if news_item.published_at:
            score += profile.recency_weight
            reasons.append("has_published_at")

        return AggregatedDigestItem(
            digest_id=digest_item.id,
            news_item_id=news_item.id,
            source=digest_item.source,
            kind=digest_item.kind,
            title=digest_item.digest_title,
            summary=digest_item.digest_summary,
            url=digest_item.url,
            published_at=news_item.published_at,
            score=score,
            matched_reasons=tuple(reasons),
        )
