"""SQLAlchemy ORM models for scraped news data."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    digest_item: Mapped["DigestItem | None"] = relationship(
        back_populates="news_item",
        cascade="all, delete-orphan",
        uselist=False,
    )


class User(Base):
    """Application user account and email preferences."""

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    profile_name: Mapped[str] = mapped_column(
        String(100),
        default="default_ai_reader",
        nullable=False,
    )
    plan_name: Mapped[str] = mapped_column(String(100), default="free", nullable=False)
    subscription_status: Mapped[str] = mapped_column(
        String(50),
        default="free",
        nullable=False,
        index=True,
    )
    email_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    subscriptions: Mapped[list["PaymentSubscription"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    payments: Mapped[list["PaymentTransaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["SiteReview"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class SiteReview(Base):
    """User feedback for the AI News Aggregator website."""

    __tablename__ = "site_reviews"
    __table_args__ = (UniqueConstraint("user_id", name="uq_site_reviews_user_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
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

    user: Mapped[User] = relationship(back_populates="reviews")


class PaymentSubscription(Base):
    """Stripe or local test subscription linked to a user account."""

    __tablename__ = "payment_subscriptions"
    __table_args__ = (
        UniqueConstraint(
            "stripe_subscription_id",
            name="uq_payment_subscriptions_stripe_subscription_id",
        ),
        UniqueConstraint(
            "stripe_checkout_session_id",
            name="uq_payment_subscriptions_checkout_session_id",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    plan_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(50), default="subscription", nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    interval: Mapped[str | None] = mapped_column(String(30), nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
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

    user: Mapped[User] = relationship(back_populates="subscriptions")
    transactions: Mapped[list["PaymentTransaction"]] = relationship(
        back_populates="subscription",
        cascade="all, delete-orphan",
    )


class PaymentTransaction(Base):
    """Payment or invoice event linked to a user subscription."""

    __tablename__ = "payment_transactions"
    __table_args__ = (
        UniqueConstraint(
            "stripe_payment_intent_id",
            name="uq_payment_transactions_payment_intent_id",
        ),
        UniqueConstraint("stripe_invoice_id", name="uq_payment_transactions_invoice_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("payment_subscriptions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    amount_cents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="usd", nullable=False)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    stripe_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="payments")
    subscription: Mapped[PaymentSubscription | None] = relationship(
        back_populates="transactions",
    )


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


class DigestItem(Base):
    """AI-generated digest summary linked to a stored news item."""

    __tablename__ = "digest_items"
    __table_args__ = (
        UniqueConstraint("news_item_id", name="uq_digest_items_news_item_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    news_item_id: Mapped[int] = mapped_column(
        ForeignKey("news_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    digest_title: Mapped[str] = mapped_column(Text, nullable=False)
    digest_summary: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    response_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_response: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
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

    news_item: Mapped[NewsItem] = relationship(back_populates="digest_item")
