"""Convenience entry points for scraping AI news websites."""

from .generic import scrape_all_sources, scrape_feed, scrape_listing_page, scrape_source
from .models import Article, NewsSource
from .sources import SOURCES, sources_by_category
from .youtube import YouTubeVideo, scrape_youtube_channel

__all__ = [
    "Article",
    "NewsSource",
    "SOURCES",
    "scrape_all_sources",
    "scrape_feed",
    "scrape_listing_page",
    "scrape_source",
    "sources_by_category",
    "YouTubeVideo",
    "scrape_youtube_channel",
]


