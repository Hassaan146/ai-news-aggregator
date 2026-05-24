"""Facade service for scraping, processing, curating, and digesting news."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.scrapers.generic import scrape_all_sources

from .models import ProcessedItem
from .process_articles import process_articles
from .process_curator import curate_items
from .process_digest import build_markdown_digest
from .process_youtube import process_youtube_channels


def collect_ai_news(
    youtube_channel_ids: list[str] | tuple[str, ...] = (),
    source_limit: int = 5,
    youtube_limit: int = 5,
    lookback_hours: int | None = 24,
    curate: bool = True,
) -> list[ProcessedItem]:
    """Collect and process website articles plus YouTube channel videos."""

    items: list[ProcessedItem] = []

    articles = scrape_all_sources(limit_per_source=source_limit)
    items.extend(process_articles(articles))

    if youtube_channel_ids:
        items.extend(
            process_youtube_channels(
                channel_ids=youtube_channel_ids,
                limit_per_channel=youtube_limit,
            )
        )

    items = filter_by_lookback(items, lookback_hours)
    if curate:
        return curate_items(items)
    return items


def collect_youtube_news(
    youtube_channel_ids: list[str] | tuple[str, ...],
    youtube_limit: int = 5,
    lookback_hours: int | None = 24,
    curate: bool = True,
) -> list[ProcessedItem]:
    """Collect and process only YouTube channel videos."""

    items = process_youtube_channels(
        channel_ids=youtube_channel_ids,
        limit_per_channel=youtube_limit,
    )
    items = filter_by_lookback(items, lookback_hours)
    if curate:
        return curate_items(items)
    return items


def collect_youtube_digest(
    youtube_channel_ids: list[str] | tuple[str, ...],
    youtube_limit: int = 5,
    lookback_hours: int | None = 24,
    curate: bool = True,
) -> str:
    """Collect YouTube videos and return a Markdown digest."""

    items = collect_youtube_news(
        youtube_channel_ids=youtube_channel_ids,
        youtube_limit=youtube_limit,
        lookback_hours=lookback_hours,
        curate=curate,
    )
    return build_markdown_digest(items, title="YouTube AI Digest")


def collect_ai_digest(
    youtube_channel_ids: list[str] | tuple[str, ...] = (),
    source_limit: int = 5,
    youtube_limit: int = 5,
    lookback_hours: int | None = 24,
    curate: bool = True,
) -> str:
    """Collect all configured sources and return a Markdown digest."""

    items = collect_ai_news(
        youtube_channel_ids=youtube_channel_ids,
        source_limit=source_limit,
        youtube_limit=youtube_limit,
        lookback_hours=lookback_hours,
        curate=curate,
    )
    return build_markdown_digest(items, title="AI News Digest")


def filter_by_lookback(
    items: list[ProcessedItem],
    lookback_hours: int | None,
) -> list[ProcessedItem]:
    """Keep dated items inside the lookback window and undated items."""

    if lookback_hours is None:
        return items

    cutoff = datetime.now(UTC) - timedelta(hours=lookback_hours)
    filtered: list[ProcessedItem] = []
    for item in items:
        if item.published_at is None:
            filtered.append(item)
            continue
        published_at = item.published_at
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=UTC)
        if published_at >= cutoff:
            filtered.append(item)
    return filtered
