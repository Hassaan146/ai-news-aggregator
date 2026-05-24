"""App configuration for the AI news aggregation pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_LOOKBACK_HOURS = 24
DEFAULT_SOURCE_LIMIT = 5
DEFAULT_YOUTUBE_LIMIT = 5

# Website sources are predefined in app.scrapers.sources.SOURCES.
# Add YouTube channel IDs here when you want the pipeline to watch them.
YOUTUBE_CHANNEL_IDS = [
    "UCn8ujwUInbJkBhffxqAPBVQ",
]


@dataclass(frozen=True)
class PipelineConfig:
    """Runtime settings for one pipeline run."""

    youtube_channel_ids: list[str] = field(default_factory=lambda: YOUTUBE_CHANNEL_IDS.copy())
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS
    source_limit: int = DEFAULT_SOURCE_LIMIT
    youtube_limit: int = DEFAULT_YOUTUBE_LIMIT
    curate: bool = True
