"""Process YouTube channel videos returned by the YouTube scraper."""

from __future__ import annotations

from app.scrapers.youtube import YouTubeVideo, scrape_youtube_channel

from .models import ProcessedItem


def process_youtube_channel(channel_id: str, limit: int = 10) -> list[ProcessedItem]:
    """Scrape and normalize videos for one YouTube channel ID."""

    videos = scrape_youtube_channel(channel_id=channel_id, limit=limit)
    return process_youtube_videos(videos)


def process_youtube_channels(
    channel_ids: list[str] | tuple[str, ...],
    limit_per_channel: int = 10,
) -> list[ProcessedItem]:
    """Scrape and normalize videos for multiple YouTube channel IDs."""

    processed: list[ProcessedItem] = []
    for channel_id in channel_ids:
        processed.extend(process_youtube_channel(channel_id, limit=limit_per_channel))
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
