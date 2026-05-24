"""Service helpers for storing processed scraper output."""

from __future__ import annotations

from app.database.connection import get_session
from app.database.models import NewsItem
from app.database.repository import (
    list_recent_news_items,
    upsert_news_items,
)

from .models import ProcessedItem


def save_processed_items(items: list[ProcessedItem]) -> list[NewsItem]:
    """Persist processed scraper items using URL-based upserts."""

    with get_session() as session:
        saved_items = upsert_news_items(session, items)
        return [item for item in saved_items]


def get_recent_items(hours: int = 24) -> list[NewsItem]:
    """Return stored items inside a lookback window."""

    with get_session() as session:
        items = list_recent_news_items(session, hours=hours)
        for item in items:
            session.expunge(item)
        return items
