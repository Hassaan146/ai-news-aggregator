"""Create AI-generated digest rows from stored news items."""

from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from app.agent.digest_agent import DEFAULT_DIGEST_MODEL, DigestAgent
from app.database.connection import get_session
from app.database.models import DigestItem
from app.database.repository import (
    list_news_items_without_digest,
    upsert_digest_item,
)


@dataclass(frozen=True)
class DigestProcessingResult:
    """Summary of one digest processing run."""

    processed: int
    created_or_updated: int
    failed: int = 0
    stopped_reason: str | None = None


def process_digest_items(
    limit: int = 25,
    lookback_hours: int | None = 48,
    model: str = DEFAULT_DIGEST_MODEL,
    delay_seconds: float = 6.0,
) -> DigestProcessingResult:
    """Create digest rows for stored news items that do not have one yet."""

    agent = DigestAgent(model=model)
    created_or_updated = 0
    failed = 0
    stopped_reason: str | None = None

    with get_session() as session:
        news_items = list_news_items_without_digest(
            session,
            limit=limit,
            hours=lookback_hours,
        )
        for news_item in news_items:
            try:
                result = agent.summarize_news_item(news_item)
                upsert_digest_item(
                    session=session,
                    news_item=news_item,
                    digest_title=result.title,
                    digest_summary=result.summary,
                    model=result.model,
                    response_id=result.response_id,
                    raw_response=result.raw_response,
                )
                session.commit()
                created_or_updated += 1
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
            except requests.HTTPError as exc:
                session.rollback()
                failed += 1
                if exc.response is not None and exc.response.status_code == 429:
                    stopped_reason = "rate_limited"
                    break
                stopped_reason = str(exc)
            except Exception as exc:
                session.rollback()
                failed += 1
                stopped_reason = str(exc)

    return DigestProcessingResult(
        processed=len(news_items),
        created_or_updated=created_or_updated,
        failed=failed,
        stopped_reason=stopped_reason,
    )


def list_generated_digest_items(limit: int = 100) -> list[DigestItem]:
    """Return generated digest items for display/API surfaces."""

    from app.database.repository import list_digest_items

    with get_session() as session:
        items = list_digest_items(session, limit=limit)
        for item in items:
            session.expunge(item)
        return items
