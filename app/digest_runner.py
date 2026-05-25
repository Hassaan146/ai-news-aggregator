"""Runner for generating digest rows from stored news items."""

from __future__ import annotations

import argparse
import sys

from app.agent.digest_agent import DEFAULT_DIGEST_MODEL
from app.services.process_digest_items import process_digest_items


def main() -> None:
    """Run digest generation for stored news items."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Generate digest rows with OpenAI.")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--lookback-hours", type=int, default=48)
    parser.add_argument("--model", default=DEFAULT_DIGEST_MODEL)
    parser.add_argument("--delay-seconds", type=float, default=6.0)
    args = parser.parse_args()

    result = process_digest_items(
        limit=args.limit,
        lookback_hours=args.lookback_hours,
        model=args.model,
        delay_seconds=args.delay_seconds,
    )
    print(
        "Digest processing complete: "
        f"processed={result.processed}, "
        f"created_or_updated={result.created_or_updated}, "
        f"failed={result.failed}, "
        f"stopped_reason={result.stopped_reason}"
    )


if __name__ == "__main__":
    main()
