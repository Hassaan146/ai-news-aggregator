"""CRUD helpers for persisted news items."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .models import (
    DigestItem,
    NewsItem,
    PaymentSubscription,
    PaymentTransaction,
    SourceRun,
    User,
)

if TYPE_CHECKING:
    from app.services.models import ProcessedItem

GMAIL_ADDRESS_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9._%+-]{0,62}[a-z0-9])?@(gmail\.com|googlemail\.com)$"
)


def create_user(
    session: Session,
    name: str,
    email: str,
    profile_name: str = "default_ai_reader",
) -> User:
    """Create a user with a Gmail address."""

    normalized_email = validate_gmail_address(email)
    user = User(name=name.strip(), email=normalized_email, profile_name=profile_name)
    session.add(user)
    session.flush()
    return user


def upsert_user(
    session: Session,
    name: str,
    email: str,
    profile_name: str = "default_ai_reader",
) -> User:
    """Create or update a user by email."""

    normalized_email = validate_gmail_address(email)
    user = get_user_by_email(session, normalized_email)
    if user is None:
        return create_user(session, name, normalized_email, profile_name)

    user.name = name.strip()
    user.profile_name = profile_name
    user.is_active = True
    user.updated_at = datetime.now(UTC)
    session.flush()
    return user


def update_user_subscription_status(
    session: Session,
    user: User,
    plan_name: str,
    subscription_status: str,
    stripe_customer_id: str | None = None,
) -> User:
    """Update account-level plan and subscription state."""

    user.plan_name = plan_name
    user.subscription_status = subscription_status
    user.stripe_customer_id = stripe_customer_id or user.stripe_customer_id
    user.updated_at = datetime.now(UTC)
    session.flush()
    return user


def get_user(session: Session, user_id: int) -> User | None:
    """Return one user by id."""

    return session.get(User, user_id)


def get_user_by_email(session: Session, email: str) -> User | None:
    """Return one user by email."""

    statement = select(User).where(User.email == email.strip().lower())
    return session.execute(statement).scalar_one_or_none()


def list_active_users(session: Session) -> list[User]:
    """List active users."""

    statement = select(User).where(User.is_active.is_(True)).order_by(User.created_at)
    return list(session.execute(statement).scalars())


def create_payment_subscription(
    session: Session,
    user: User,
    plan_name: str,
    status: str,
    mode: str = "subscription",
    amount_cents: int = 0,
    currency: str = "usd",
    interval: str | None = "month",
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
    stripe_checkout_session_id: str | None = None,
    raw_payload: dict | None = None,
) -> PaymentSubscription:
    """Create or update a subscription row for a user."""

    subscription = None
    if stripe_checkout_session_id:
        statement = select(PaymentSubscription).where(
            PaymentSubscription.stripe_checkout_session_id == stripe_checkout_session_id
        )
        subscription = session.execute(statement).scalar_one_or_none()
    if subscription is None and stripe_subscription_id:
        statement = select(PaymentSubscription).where(
            PaymentSubscription.stripe_subscription_id == stripe_subscription_id
        )
        subscription = session.execute(statement).scalar_one_or_none()

    now = datetime.now(UTC)
    if subscription is None:
        subscription = PaymentSubscription(
            user_id=user.id,
            plan_name=plan_name,
            status=status,
            mode=mode,
            amount_cents=amount_cents,
            currency=currency,
            interval=interval,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            stripe_checkout_session_id=stripe_checkout_session_id,
            started_at=now if status in {"active", "trialing"} else None,
            raw_payload=raw_payload or {},
        )
        session.add(subscription)
    else:
        subscription.plan_name = plan_name
        subscription.status = status
        subscription.mode = mode
        subscription.amount_cents = amount_cents
        subscription.currency = currency
        subscription.interval = interval
        subscription.stripe_customer_id = stripe_customer_id
        subscription.stripe_subscription_id = stripe_subscription_id
        subscription.stripe_checkout_session_id = stripe_checkout_session_id
        subscription.raw_payload = raw_payload or {}
        subscription.updated_at = now
        if status in {"active", "trialing"} and subscription.started_at is None:
            subscription.started_at = now

    update_user_subscription_status(
        session=session,
        user=user,
        plan_name=plan_name,
        subscription_status=status,
        stripe_customer_id=stripe_customer_id,
    )
    session.flush()
    return subscription


def create_payment_transaction(
    session: Session,
    user: User,
    status: str,
    amount_cents: int = 0,
    currency: str = "usd",
    subscription: PaymentSubscription | None = None,
    stripe_payment_intent_id: str | None = None,
    stripe_invoice_id: str | None = None,
    stripe_checkout_session_id: str | None = None,
    raw_payload: dict | None = None,
) -> PaymentTransaction:
    """Create a payment transaction row."""

    transaction = PaymentTransaction(
        user_id=user.id,
        subscription_id=subscription.id if subscription else None,
        status=status,
        amount_cents=amount_cents,
        currency=currency,
        stripe_payment_intent_id=stripe_payment_intent_id,
        stripe_invoice_id=stripe_invoice_id,
        stripe_checkout_session_id=stripe_checkout_session_id,
        paid_at=datetime.now(UTC) if status in {"paid", "complete"} else None,
        raw_payload=raw_payload or {},
    )
    session.add(transaction)
    session.flush()
    return transaction


def get_payment_subscription_by_checkout_session_id(
    session: Session,
    checkout_session_id: str,
) -> PaymentSubscription | None:
    """Return a subscription by Stripe Checkout Session id."""

    statement = select(PaymentSubscription).where(
        PaymentSubscription.stripe_checkout_session_id == checkout_session_id
    )
    return session.execute(statement).scalar_one_or_none()


def activate_payment_subscription(
    session: Session,
    subscription: PaymentSubscription,
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
    raw_payload: dict | None = None,
) -> PaymentSubscription:
    """Mark a subscription active and mirror the status onto the user."""

    now = datetime.now(UTC)
    subscription.status = "active"
    subscription.started_at = subscription.started_at or now
    subscription.stripe_customer_id = stripe_customer_id or subscription.stripe_customer_id
    subscription.stripe_subscription_id = (
        stripe_subscription_id or subscription.stripe_subscription_id
    )
    subscription.raw_payload = raw_payload or subscription.raw_payload
    subscription.updated_at = now
    update_user_subscription_status(
        session=session,
        user=subscription.user,
        plan_name=subscription.plan_name,
        subscription_status="active",
        stripe_customer_id=subscription.stripe_customer_id,
    )
    session.flush()
    return subscription


def validate_gmail_address(email: str) -> str:
    """Require a Gmail or Googlemail address for user accounts."""

    normalized_email = email.strip().lower()
    if not GMAIL_ADDRESS_PATTERN.fullmatch(normalized_email):
        raise ValueError("User email must be a valid Gmail address.")
    return normalized_email


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


def list_news_items_without_digest(
    session: Session,
    limit: int = 25,
    hours: int | None = None,
) -> list[NewsItem]:
    """List stored items that do not yet have digest rows."""

    statement = (
        select(NewsItem)
        .outerjoin(DigestItem, DigestItem.news_item_id == NewsItem.id)
        .where(DigestItem.id.is_(None))
        .order_by(NewsItem.published_at.desc().nullslast(), NewsItem.scraped_at.desc())
        .limit(limit)
    )
    if hours is not None:
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        statement = statement.where(
            (NewsItem.published_at >= cutoff) | (NewsItem.scraped_at >= cutoff)
        )
    return list(session.execute(statement).scalars())


def upsert_digest_item(
    session: Session,
    news_item: NewsItem,
    digest_title: str,
    digest_summary: str,
    model: str,
    response_id: str | None = None,
    raw_response: dict | None = None,
) -> DigestItem:
    """Insert or update one digest row linked to a news item."""

    statement = select(DigestItem).where(DigestItem.news_item_id == news_item.id)
    digest = session.execute(statement).scalar_one_or_none()
    if digest is None:
        digest = DigestItem(
            news_item_id=news_item.id,
            source=news_item.source,
            kind=news_item.kind,
            url=news_item.url,
            digest_title=digest_title,
            digest_summary=digest_summary,
            model=model,
            response_id=response_id,
            raw_response=raw_response or {},
        )
        session.add(digest)
    else:
        digest.source = news_item.source
        digest.kind = news_item.kind
        digest.url = news_item.url
        digest.digest_title = digest_title
        digest.digest_summary = digest_summary
        digest.model = model
        digest.response_id = response_id
        digest.raw_response = raw_response or {}
        digest.updated_at = datetime.now(UTC)
    session.flush()
    return digest


def list_digest_items(session: Session, limit: int = 100) -> list[DigestItem]:
    """List generated digest rows newest first."""

    statement = select(DigestItem).order_by(DigestItem.created_at.desc()).limit(limit)
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
