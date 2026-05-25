"""Service surface for profile-aware digest aggregation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.agent.aggregator_agent import AggregatedDigestItem, AggregatorAgent
from app.agent.ranking_agent import RankingAgent
from app.database.connection import get_session
from app.database.models import DigestItem, NewsItem
from app.profiles.user_profile import UserProfile, get_profile
from app.schemas.aggregator import (
    AggregatedDigestItemSchema,
    AggregatedDigestResponse,
    TopDigestResponse,
    UserProfileSchema,
)


def get_aggregated_digest(
    hours: int = 48,
    profile_name: str | None = None,
    profile: UserProfile | None = None,
    limit: int = 50,
    use_llm: bool = True,
) -> list[AggregatedDigestItem]:
    """Return recent digest items sorted for a user profile."""

    selected_profile = profile or get_profile(profile_name)
    rows = fetch_digest_rows(hours=hours, limit=limit)
    deterministic_items = AggregatorAgent().rank(rows, selected_profile)
    if not use_llm:
        return deterministic_items

    try:
        return rank_with_llm(selected_profile, deterministic_items)
    except Exception as exc:
        return [
            AggregatedDigestItem(
                digest_id=item.digest_id,
                news_item_id=item.news_item_id,
                source=item.source,
                kind=item.kind,
                title=item.title,
                summary=item.summary,
                url=item.url,
                published_at=item.published_at,
                score=item.score,
                matched_reasons=(*item.matched_reasons, "fallback:llm_unavailable"),
                rank_source="fallback",
                llm_reason=str(exc),
            )
            for item in deterministic_items
        ]


def fetch_digest_rows(
    hours: int = 48,
    limit: int = 50,
) -> list[tuple[DigestItem, NewsItem]]:
    """Fetch recent digest/news rows for aggregation."""

    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    with get_session() as session:
        statement = (
            select(DigestItem, NewsItem)
            .join(NewsItem, NewsItem.id == DigestItem.news_item_id)
            .where((NewsItem.published_at >= cutoff) | (NewsItem.scraped_at >= cutoff))
            .limit(limit)
        )
        rows = list(session.execute(statement).all())
    return rows


def rank_with_llm(
    profile: UserProfile,
    deterministic_items: list[AggregatedDigestItem],
) -> list[AggregatedDigestItem]:
    """Use Gemini to rerank deterministic candidates."""

    candidates = [
        {
            "digest_id": item.digest_id,
            "source": item.source,
            "kind": item.kind,
            "title": item.title,
            "summary": item.summary,
            "url": item.url,
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "deterministic_score": item.score,
            "deterministic_reasons": list(item.matched_reasons),
        }
        for item in deterministic_items
    ]
    ranked = RankingAgent().rank_digest_items(profile, candidates)
    ranked_by_id = {item.digest_id: item for item in ranked}
    original_by_id = {item.digest_id: item for item in deterministic_items}

    llm_items: list[AggregatedDigestItem] = []
    for ranked_item in sorted(ranked, key=lambda item: item.rank):
        original = original_by_id.get(ranked_item.digest_id)
        if original is None:
            continue
        llm_items.append(
            AggregatedDigestItem(
                digest_id=original.digest_id,
                news_item_id=original.news_item_id,
                source=original.source,
                kind=original.kind,
                title=original.title,
                summary=original.summary,
                url=original.url,
                published_at=original.published_at,
                score=ranked_item.relevance_score,
                matched_reasons=(*original.matched_reasons, "ranked_by:llm"),
                rank_source="llm",
                llm_reason=ranked_item.reason,
            )
        )

    missing_items = [
        item for item in deterministic_items if item.digest_id not in ranked_by_id
    ]
    return llm_items + missing_items


def get_aggregated_digest_response(
    hours: int = 48,
    profile_name: str | None = None,
    profile: UserProfile | None = None,
    limit: int = 50,
    use_llm: bool = True,
) -> AggregatedDigestResponse:
    """Return a Pydantic response for API/frontend use."""

    selected_profile = profile or get_profile(profile_name)
    items = get_aggregated_digest(
        hours=hours,
        profile=selected_profile,
        limit=limit,
        use_llm=use_llm,
    )
    item_schemas = [
        AggregatedDigestItemSchema.from_aggregated_item(item, rank=index + 1)
        for index, item in enumerate(items)
    ]
    return AggregatedDigestResponse(
        profile=UserProfileSchema.from_profile(selected_profile),
        lookback_hours=hours,
        ranking_method=detect_ranking_method(items, use_llm),
        fallback_reason=detect_fallback_reason(items),
        total_items=len(item_schemas),
        items=item_schemas,
    )


def detect_ranking_method(
    items: list[AggregatedDigestItem],
    use_llm: bool,
) -> str:
    """Return the ranking method used for response metadata."""

    if not use_llm:
        return "deterministic"
    if any(item.rank_source == "fallback" for item in items):
        return "fallback"
    if any(item.rank_source == "llm" for item in items):
        return "llm"
    return "deterministic"


def detect_fallback_reason(items: list[AggregatedDigestItem]) -> str | None:
    """Return the fallback reason if LLM ranking failed."""

    for item in items:
        if item.rank_source == "fallback":
            return item.llm_reason
    return None


def build_aggregated_markdown(
    items: list[AggregatedDigestItem],
    title: str = "Personalized AI Digest",
) -> str:
    """Render aggregated digest items as Markdown."""

    lines = [f"# {title}", ""]
    for item in items:
        date = item.published_at.date().isoformat() if item.published_at else "No date"
        lines.append(f"## {item.title}")
        lines.append(f"- Source: {item.source}")
        lines.append(f"- Type: {item.kind}")
        lines.append(f"- Date: {date}")
        lines.append(f"- Score: {item.score}")
        lines.append(f"- URL: {item.url}")
        lines.append("")
        lines.append(item.summary)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def get_top_digests(
    hours: int = 24,
    top_n: int = 10,
    profile_name: str | None = None,
    profile: UserProfile | None = None,
    limit: int = 100,
    use_llm: bool = False,
) -> TopBadgesResponse:
    """Return top ranked digests/articles for recent website views."""

    response = get_aggregated_digest_response(
        hours=hours,
        profile_name=profile_name,
        profile=profile,
        limit=limit,
        use_llm=use_llm,
    )

    return TopDigestResponse(
        profile=response.profile,
        lookback_hours=hours,
        top_n=top_n,
        ranking_method=response.ranking_method,
        fallback_reason=response.fallback_reason,
        total_items=min(len(response.items), top_n),
        items=response.items[:top_n],
    )
