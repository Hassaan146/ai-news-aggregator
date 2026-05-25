"""App configuration for the AI news aggregation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.scrapers.youtube_channels import YOUTUBE_CHANNEL_IDS


DEFAULT_LOOKBACK_HOURS = 24
DEFAULT_SOURCE_LIMIT = 5
DEFAULT_YOUTUBE_LIMIT = 5
DEFAULT_YOUTUBE_COOLDOWN_HOURS = 6
DEFAULT_YOUTUBE_RETRY_AFTER_HOURS = 12

# Website sources are predefined in app.scrapers.sources.SOURCES.
# YouTube channels are predefined in app.scrapers.youtube_channels.


@dataclass(frozen=True)
class PipelineConfig:
    """Runtime settings for one pipeline run."""

    youtube_channel_ids: list[str] = field(default_factory=lambda: YOUTUBE_CHANNEL_IDS.copy())
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS
    source_limit: int = DEFAULT_SOURCE_LIMIT
    youtube_limit: int = DEFAULT_YOUTUBE_LIMIT
    youtube_cooldown_hours: int = DEFAULT_YOUTUBE_COOLDOWN_HOURS
    youtube_retry_after_hours: int = DEFAULT_YOUTUBE_RETRY_AFTER_HOURS
    curate: bool = True
    store: bool = True
