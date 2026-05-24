"""Anthropic news scraper."""

from __future__ import annotations

from .generic import scrape_source
from .models import Article
from .sources import SOURCES

ANTHROPIC_SOURCES = tuple(source for source in SOURCES if "anthropic.com" in source.url)


def scrape_anthropic(limit_per_source: int = 10) -> list[Article]:
    """Scrape Anthropic news sources."""

    articles: list[Article] = []
    for source in ANTHROPIC_SOURCES:
        articles.extend(scrape_source(source, limit=limit_per_source))
    return articles
