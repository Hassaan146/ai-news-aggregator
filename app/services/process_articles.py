"""Process articles returned by website scrapers."""

from __future__ import annotations

from app.scrapers.models import Article

from .models import ProcessedItem


def process_articles(articles: list[Article]) -> list[ProcessedItem]:
    """Normalize scraped website articles for downstream services."""

    processed: list[ProcessedItem] = []
    for article in articles:
        if not article.title or not article.url:
            continue
        processed.append(
            ProcessedItem(
                source=article.source,
                title=article.title.strip(),
                url=article.url.strip(),
                kind="article",
                summary=article.summary.strip(),
                published_at=article.published_at,
            )
        )
    return processed
