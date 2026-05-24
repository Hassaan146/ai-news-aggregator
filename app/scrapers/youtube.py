"""Simple YouTube channel scraper using channel IDs and public RSS feeds."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from re import fullmatch
from urllib.parse import parse_qs, urlparse

import feedparser
from bs4 import BeautifulSoup

YOUTUBE_FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


@dataclass(frozen=True)
class YouTubeVideo:
    """A normalized YouTube video discovered from a channel feed."""

    channel: str
    channel_id: str
    title: str
    url: str
    video_id: str
    published_at: datetime | None = None
    summary: str = ""


class YouTubeScraperError(ValueError):
    """Raised when a YouTube channel ID cannot be scraped."""


def scrape_youtube_channel(channel_id: str, limit: int = 10) -> list[YouTubeVideo]:
    """Scrape recent videos from a YouTube channel ID.

    Example:
        videos = scrape_youtube_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw", limit=5)

    Args:
        channel_id: YouTube channel ID only. It must start with "UC".
        limit: Maximum number of videos to return.
    """

    channel_id = clean_channel_id(channel_id)
    feed_url = YOUTUBE_FEED_URL.format(channel_id=channel_id)
    feed = feedparser.parse(feed_url)

    if getattr(feed, "bozo", False) and not feed.entries:
        raise YouTubeScraperError(f"Could not read YouTube feed: {feed_url}")

    channel_name = clean_text(feed.feed.get("title", channel_id))
    videos: list[YouTubeVideo] = []

    for entry in feed.entries[:limit]:
        title = clean_text(entry.get("title", ""))
        url = entry.get("link", "")
        video_id = entry.get("yt_videoid", "") or extract_video_id(url)
        published_at = parse_feed_date(entry.get("published"))
        summary = clean_text(entry.get("summary", ""))

        if title and video_id:
            videos.append(
                YouTubeVideo(
                    channel=channel_name,
                    channel_id=channel_id,
                    title=title,
                    url=url or f"https://www.youtube.com/watch?v={video_id}",
                    video_id=video_id,
                    published_at=published_at,
                    summary=summary,
                )
            )

    return videos


def clean_channel_id(channel_id: str) -> str:
    """Validate and normalize a YouTube channel ID."""

    value = channel_id.strip()
    if not fullmatch(r"UC[0-9A-Za-z_-]{20,}", value):
        raise YouTubeScraperError(
            "Use a YouTube channel ID only, for example: "
            "UC_x5XG1OV2P6uZZ5FSM9Ttw"
        )
    return value


def extract_video_id(url: str) -> str:
    """Extract a video ID from a YouTube watch URL."""

    parsed = urlparse(url)
    if parsed.netloc.endswith("youtu.be"):
        return parsed.path.strip("/")
    return parse_qs(parsed.query).get("v", [""])[0]


def parse_feed_date(value: str | None) -> datetime | None:
    """Parse a YouTube RSS date value into a datetime."""

    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        pass

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def clean_text(value: str) -> str:
    """Normalize whitespace and strip HTML from a string."""

    text = BeautifulSoup(value or "", "html.parser").get_text(" ")
    return " ".join(text.split())


if __name__ == "__main__":
    channel = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    for video in scrape_youtube_channel(channel, limit=5):
        print(f"{video.published_at} | {video.title} | {video.url}")

