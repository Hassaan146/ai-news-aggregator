"""Runner for profile-aware digest aggregation."""

from __future__ import annotations

import argparse
import sys

from app.services.aggregator_surface import (
    build_aggregated_markdown,
    get_aggregated_digest,
    get_top_digests,
)


def main() -> None:
    """Print a personalized digest feed."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Aggregate digest items by profile.")
    parser.add_argument("--hours", type=int, default=48)
    parser.add_argument("--profile", default=None)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--top-digests", action="store_true")
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    if args.top_digests:
        print(
            get_top_digests(
                hours=args.hours,
                top_n=args.top_n,
                profile_name=args.profile,
                limit=args.limit,
                use_llm=not args.no_llm,
            ).model_dump_json(indent=2)
        )
        return

    items = get_aggregated_digest(
        hours=args.hours,
        profile_name=args.profile,
        limit=args.limit,
        use_llm=not args.no_llm,
    )
    print(build_aggregated_markdown(items))


if __name__ == "__main__":
    main()
