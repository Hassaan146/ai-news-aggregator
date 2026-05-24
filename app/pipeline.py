"""Pipeline entry point for one complete AI news aggregation run."""

from __future__ import annotations

from app.config import PipelineConfig
from app.services.news_surface import collect_ai_digest, collect_ai_news


def run_pipeline(config: PipelineConfig | None = None) -> str:
    """Run scraping, processing, curation, and digest creation."""

    config = config or PipelineConfig()
    return collect_ai_digest(
        youtube_channel_ids=config.youtube_channel_ids,
        source_limit=config.source_limit,
        youtube_limit=config.youtube_limit,
        youtube_cooldown_hours=config.youtube_cooldown_hours,
        youtube_retry_after_hours=config.youtube_retry_after_hours,
        lookback_hours=config.lookback_hours,
        curate=config.curate,
        store=config.store,
    )


def run_pipeline_items(config: PipelineConfig | None = None):
    """Run the pipeline and return processed items instead of Markdown."""

    config = config or PipelineConfig()
    return collect_ai_news(
        youtube_channel_ids=config.youtube_channel_ids,
        source_limit=config.source_limit,
        youtube_limit=config.youtube_limit,
        youtube_cooldown_hours=config.youtube_cooldown_hours,
        youtube_retry_after_hours=config.youtube_retry_after_hours,
        lookback_hours=config.lookback_hours,
        curate=config.curate,
        store=config.store,
    )
