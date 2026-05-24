"""CRUD helpers for persisted news items."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import NewsItem, SourceRun

if TYPE_CHECKING:
    from app.services.models import ProcessedItem


def create_news_item(session: Session, item: ProcessedItem) -> NewsItem:
    """Create a news item without duplicate handling."""

    db_item = NewsItem(
        source=item.source,
        kind=item.kind,
        title=item.title,
        url=item.url,
        summary=item.summary,
        published_at=item.published_at,
        item_metadata=item.metadata,
        content=item.content,
        transcript=item.transcript,
        transcript_status=item.transcript_status,
    )
    session.add(db_item)
    session.flush()
    return db_item


def upsert_news_item(session: Session, item: ProcessedItem) -> NewsItem:
    """Insert a new item or update an existing item matched by URL."""

    existing = get_news_item_by_url(session, item.url)
    if existing is None:
        return create_news_item(session, item)

    existing.source = item.source
    existing.kind = item.kind
    existing.title = item.title
    existing.summary = item.summary
    existing.published_at = item.published_at or existing.published_at
    existing.item_metadata = {**(existing.item_metadata or {}), **item.metadata}
    existing.content = item.content or existing.content
    existing.transcript = item.transcript or existing.transcript
    existing.transcript_status = item.transcript_status or existing.transcript_status
    existing.updated_at = datetime.now(UTC)
    session.flush()
    return existing


def upsert_news_items(
    session: Session,
    items: Iterable[ProcessedItem],
) -> list[NewsItem]:
    """Upsert many processed items."""

    return [upsert_news_item(session, item) for item in items]


def get_news_item(session: Session, item_id: int) -> NewsItem | None:
    """Return one item by primary key."""

    return session.get(NewsItem, item_id)


def get_news_item_by_url(session: Session, url: str) -> NewsItem | None:
    """Return one item by URL."""

    statement = select(NewsItem).where(NewsItem.url == url)
    return session.execute(statement).scalar_one_or_none()


def list_news_items(
    session: Session,
    limit: int = 100,
    kind: str | None = None,
    source: str | None = None,
) -> list[NewsItem]:
    """List stored items newest first."""

    statement = select(NewsItem).order_by(NewsItem.scraped_at.desc()).limit(limit)
    if kind:
        statement = statement.where(NewsItem.kind == kind)
    if source:
        statement = statement.where(NewsItem.source == source)
    return list(session.execute(statement).scalars())


def list_recent_news_items(session: Session, hours: int = 24) -> list[NewsItem]:
    """List items published or scraped inside a lookback window."""

    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    statement = (
        select(NewsItem)
        .where((NewsItem.published_at >= cutoff) | (NewsItem.scraped_at >= cutoff))
        .order_by(NewsItem.published_at.desc().nullslast(), NewsItem.scraped_at.desc())
    )
    return list(session.execute(statement).scalars())


def list_youtube_items_for_channel(
    session: Session,
    channel_id: str,
    limit: int = 10,
) -> list[NewsItem]:
    """List stored YouTube items for a channel."""

    statement = (
        select(NewsItem)
        .where(
            NewsItem.kind == "youtube_video",
            NewsItem.item_metadata["channel_id"].as_string() == channel_id,
        )
        .order_by(NewsItem.published_at.desc().nullslast(), NewsItem.scraped_at.desc())
        .limit(limit)
    )
    return list(session.execute(statement).scalars())


def get_source_run(session: Session, source_key: str) -> SourceRun | None:
    """Return source run state by key."""

    statement = select(SourceRun).where(SourceRun.source_key == source_key)
    return session.execute(statement).scalar_one_or_none()


def should_scrape_source(
    session: Session,
    source_key: str,
    cooldown_hours: int,
) -> bool:
    """Return False when a source was scraped inside the cooldown window."""

    run = get_source_run(session, source_key)
    if run is None or run.last_scraped_at is None:
        return True

    now = datetime.now(UTC)
    last_scraped_at = run.last_scraped_at
    if last_scraped_at.tzinfo is None:
        last_scraped_at = last_scraped_at.replace(tzinfo=UTC)

    if run.next_retry_at:
        next_retry_at = run.next_retry_at
        if next_retry_at.tzinfo is None:
            next_retry_at = next_retry_at.replace(tzinfo=UTC)
        if next_retry_at > now:
            return False

    return last_scraped_at <= now - timedelta(hours=cooldown_hours)


def record_source_success(
    session: Session,
    source_key: str,
    source_type: str,
    metadata: dict | None = None,
) -> SourceRun:
    """Record a successful scrape attempt."""

    run = get_source_run(session, source_key)
    if run is None:
        run = SourceRun(source_key=source_key, source_type=source_type)
        session.add(run)

    run.status = "success"
    run.last_scraped_at = datetime.now(UTC)
    run.next_retry_at = None
    run.error = None
    run.run_metadata = metadata or {}
    session.flush()
    return run


def record_source_failure(
    session: Session,
    source_key: str,
    source_type: str,
    error: str,
    retry_after_hours: int = 6,
    metadata: dict | None = None,
) -> SourceRun:
    """Record a failed scrape attempt and set a retry time."""

    run = get_source_run(session, source_key)
    if run is None:
        run = SourceRun(source_key=source_key, source_type=source_type)
        session.add(run)

    now = datetime.now(UTC)
    run.status = "failed"
    run.last_scraped_at = now
    run.next_retry_at = now + timedelta(hours=retry_after_hours)
    run.error = error
    run.run_metadata = metadata or {}
    session.flush()
    return run


def update_transcript(
    session: Session,
    item_id: int,
    transcript: str | None,
    status: str = "completed",
    error: str | None = None,
) -> NewsItem:
    """Update transcript fields for a stored item."""

    item = get_news_item(session, item_id)
    if item is None:
        raise ValueError(f"News item not found: {item_id}")

    item.transcript = transcript
    item.transcript_status = status
    item.last_transcript_error = error
    item.transcript_attempts += 1
    item.updated_at = datetime.now(UTC)
    session.flush()
    return item


def delete_news_item(session: Session, item_id: int) -> bool:
    """Delete one item by primary key."""

    result = session.execute(delete(NewsItem).where(NewsItem.id == item_id))
    return result.rowcount > 0
