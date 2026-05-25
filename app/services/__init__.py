"""Services package exports."""

from .models import ProcessedItem
from .aggregator_surface import (
    build_aggregated_markdown,
    get_aggregated_digest,
    get_aggregated_digest_response,
    get_top_digests,
)
from .news_surface import (
    collect_ai_digest,
    collect_ai_news,
    collect_youtube_digest,
    collect_youtube_news,
    filter_by_lookback,
)
from .process_articles import process_articles
from .process_curator import curate_items
from .process_digest import build_markdown_digest
from .process_digest_items import (
    DigestProcessingResult,
    list_generated_digest_items,
    process_digest_items,
)
from .process_email import (
    build_daily_email_digest,
    build_daily_email_digest_for_user,
    send_daily_email_digest_to_user,
)
from .process_youtube import (
    process_youtube_channel,
    process_youtube_channels,
    youtube_source_key,
)
from .storage import get_recent_items, save_processed_items

__all__ = [
    "ProcessedItem",
    "DigestProcessingResult",
    "build_markdown_digest",
    "build_daily_email_digest",
    "build_daily_email_digest_for_user",
    "build_aggregated_markdown",
    "collect_ai_digest",
    "collect_ai_news",
    "collect_youtube_digest",
    "collect_youtube_news",
    "curate_items",
    "filter_by_lookback",
    "get_recent_items",
    "get_aggregated_digest",
    "get_aggregated_digest_response",
    "get_top_digests",
    "process_articles",
    "process_digest_items",
    "process_youtube_channel",
    "process_youtube_channels",
    "save_processed_items",
    "send_daily_email_digest_to_user",
    "list_generated_digest_items",
    "youtube_source_key",
]
