"""Process YouTube channel videos returned by the YouTube scraper."""

from __future__ import annotations

from app.database.connection import get_session
from app.database.models import NewsItem
from app.database.repository import (
    list_youtube_items_for_channel,
    record_source_failure,
    record_source_success,
    should_scrape_source,
    upsert_news_items,
)
from app.scrapers.youtube import YouTubeVideo, scrape_youtube_channel

from .models import ProcessedItem


def process_youtube_channel(
    channel_id: str,
    limit: int = 10,
    cooldown_hours: int = 6,
    retry_after_hours: int = 12,
    use_cache: bool = True,
) -> list[ProcessedItem]:
    """Scrape and normalize videos for one YouTube channel ID.

    Uses the database as a free cache so repeated runs do not keep hitting YouTube.
    """

    source_key = youtube_source_key(channel_id)
    if use_cache:
        with get_session() as session:
            if not should_scrape_source(session, source_key, cooldown_hours):
                cached_items = list_youtube_items_for_channel(
                    session,
                    channel_id=channel_id,
                    limit=limit,
                )
                return process_cached_youtube_items(cached_items)

    try:
        videos = scrape_youtube_channel(channel_id=channel_id, limit=limit)
    except Exception as exc:
        if use_cache:
            with get_session() as session:
                record_source_failure(
                    session,
                    source_key=source_key,
                    source_type="youtube_channel",
                    error=str(exc),
                    retry_after_hours=retry_after_hours,
                    metadata={"channel_id": channel_id},
                )
                cached_items = list_youtube_items_for_channel(
                    session,
                    channel_id=channel_id,
                    limit=limit,
                )
                return process_cached_youtube_items(cached_items)
        raise

    processed = process_youtube_videos(videos)
    if use_cache:
        with get_session() as session:
            upsert_news_items(session, processed)
            record_source_success(
                session,
                source_key=source_key,
                source_type="youtube_channel",
                metadata={"channel_id": channel_id, "items": len(processed)},
            )
    return processed


def process_youtube_channels(
    channel_ids: list[str] | tuple[str, ...],
    limit_per_channel: int = 10,
    cooldown_hours: int = 6,
    retry_after_hours: int = 12,
    use_cache: bool = True,
) -> list[ProcessedItem]:
    """Scrape and normalize videos for multiple YouTube channel IDs."""

    processed: list[ProcessedItem] = []
    for channel_id in channel_ids:
        processed.extend(
            process_youtube_channel(
                channel_id,
                limit=limit_per_channel,
                cooldown_hours=cooldown_hours,
                retry_after_hours=retry_after_hours,
                use_cache=use_cache,
            )
        )
    return processed


def process_youtube_videos(videos: list[YouTubeVideo]) -> list[ProcessedItem]:
    """Normalize YouTube videos for downstream services."""

    processed: list[ProcessedItem] = []
    for video in videos:
        if not video.title or not video.url:
            continue
        processed.append(
            ProcessedItem(
                source=video.channel,
                title=video.title.strip(),
                url=video.url.strip(),
                kind="youtube_video",
                summary=video.summary.strip(),
                published_at=video.published_at,
                metadata={
                    "channel_id": video.channel_id,
                    "video_id": video.video_id,
                },
            )
        )
    return processed


def process_cached_youtube_items(items: list[NewsItem]) -> list[ProcessedItem]:
    """Convert cached database YouTube rows back into processed items."""

    return [
        ProcessedItem(
            source=item.source,
            title=item.title,
            url=item.url,
            kind=item.kind,
            summary=item.summary,
            published_at=item.published_at,
            metadata=item.item_metadata or {},
            content=item.content,
            transcript=item.transcript,
            transcript_status=item.transcript_status,
        )
        for item in items
    ]


def youtube_source_key(channel_id: str) -> str:
    """Build a stable source-run key for a YouTube channel."""

    return f"youtube:{channel_id}"
