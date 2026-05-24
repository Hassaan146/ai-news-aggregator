"""Data structures returned by website scrapers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsSource:
    """A website or feed to scrape for AI-related news."""

    name: str
    url: str
    category: str
    feed_url: str | None = None


@dataclass(frozen=True)
class Article:
    """A normalized article discovered from a news source."""

    source: str
    title: str
    url: str
    summary: str = ""
    published_at: datetime | None = None
