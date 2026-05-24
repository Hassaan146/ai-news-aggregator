"""OpenAI news scraper."""

from __future__ import annotations

from .generic import scrape_source
from .models import Article
from .sources import SOURCES

OPENAI_SOURCES = tuple(source for source in SOURCES if "openai.com" in source.url)


def scrape_openai(limit_per_source: int = 10) -> list[Article]:
    """Scrape OpenAI news/blog sources."""

    articles: list[Article] = []
    for source in OPENAI_SOURCES:
        articles.extend(scrape_source(source, limit=limit_per_source))
    return articles
