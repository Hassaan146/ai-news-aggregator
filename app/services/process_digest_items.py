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
    api_key: str | None = None,
    allow_fallback: bool = True,
) -> DigestProcessingResult:
    """Create digest rows for stored news items that do not have one yet."""

    agent = None
    agent_error: Exception | None = None
    try:
        agent = DigestAgent(model=model, api_key=api_key)
    except Exception as exc:
        if not allow_fallback:
            raise
        agent_error = exc
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
                if agent is None:
                    raise RuntimeError(str(agent_error))
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
                if allow_fallback:
                    create_fallback_digest(session, news_item, model, str(exc))
                    session.commit()
                    created_or_updated += 1
                    if delay_seconds > 0:
                        time.sleep(delay_seconds)
                    continue
                stopped_reason = str(exc)
            except Exception as exc:
                session.rollback()
                failed += 1
                if allow_fallback:
                    create_fallback_digest(session, news_item, model, str(exc))
                    session.commit()
                    created_or_updated += 1
                    if delay_seconds > 0:
                        time.sleep(delay_seconds)
                    continue
                stopped_reason = str(exc)

    return DigestProcessingResult(
        processed=len(news_items),
        created_or_updated=created_or_updated,
        failed=failed,
        stopped_reason=stopped_reason,
    )


def create_fallback_digest(
    session,
    news_item,
    model: str,
    error: str,
) -> None:
    """Create a usable digest row when the LLM is unavailable."""

    summary = build_fallback_summary(news_item)
    upsert_digest_item(
        session=session,
        news_item=news_item,
        digest_title=news_item.title.strip(),
        digest_summary=summary,
        model=f"{model}:deterministic_fallback",
        response_id=None,
        raw_response={"fallback": True, "error": error[:500]},
    )


def build_fallback_summary(news_item) -> str:
    """Build a concise deterministic summary from stored source text."""

    text = (
        news_item.summary
        or news_item.content
        or news_item.transcript
        or "No source summary was available."
    )
    text = " ".join(str(text).split())
    if len(text) > 500:
        text = text[:497].rstrip() + "..."
    return text


def list_generated_digest_items(limit: int = 100) -> list[DigestItem]:
    """Return generated digest items for display/API surfaces."""

    from app.database.repository import list_digest_items

    with get_session() as session:
        items = list_digest_items(session, limit=limit)
        for item in items:
            session.expunge(item)
        return items
