"""AI News Aggregator - Main entry point."""

from __future__ import annotations

import argparse

from app.config import PipelineConfig, YOUTUBE_CHANNEL_IDS
from app.pipeline import run_pipeline


def main() -> None:
    """Run the AI news aggregation pipeline."""

    parser = argparse.ArgumentParser(description="Run the AI news aggregation pipeline.")
    parser.add_argument("--lookback-hours", type=int, default=24)
    parser.add_argument("--source-limit", type=int, default=5)
    parser.add_argument("--youtube-limit", type=int, default=5)
    parser.add_argument("--youtube-channel-id", action="append", default=[])
    parser.add_argument("--no-curate", action="store_true")
    args = parser.parse_args()

    channel_ids = args.youtube_channel_id or YOUTUBE_CHANNEL_IDS
    config = PipelineConfig(
        youtube_channel_ids=channel_ids,
        lookback_hours=args.lookback_hours,
        source_limit=args.source_limit,
        youtube_limit=args.youtube_limit,
        curate=not args.no_curate,
    )
    print(run_pipeline(config))


if __name__ == "__main__":
    main()
