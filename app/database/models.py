"""SQLAlchemy ORM models for scraped news data."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .connection import Base


class NewsItem(Base):
    """Stored article or video discovered by the aggregation pipeline."""

    __tablename__ = "news_items"
    __table_args__ = (UniqueConstraint("url", name="uq_news_items_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="", nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_status: Mapped[str] = mapped_column(
        String(30),
        default="not_requested",
        nullable=False,
        index=True,
    )
    transcript_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_transcript_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    item_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class SourceRun(Base):
    """Tracks scrape attempts so sources are not hit too often."""

    __tablename__ = "source_runs"
    __table_args__ = (UniqueConstraint("source_key", name="uq_source_runs_source_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="success")
    last_scraped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    run_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
