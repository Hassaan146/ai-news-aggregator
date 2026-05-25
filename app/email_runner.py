"""Runner for previewing or sending daily personalized email digests."""

from __future__ import annotations

import argparse
import sys

from app.services.process_email import (
    build_daily_email_digest,
    build_daily_email_digest_for_user,
    send_daily_email_digest_to_user,
)


def main() -> None:
    """Print a daily email digest preview."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Preview or send a daily AI news email.")
    parser.add_argument("--name", default="Hassan")
    parser.add_argument("--to", help="Stored user Gmail address.")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--send", action="store_true", help="Send the email via Gmail SMTP.")
    args = parser.parse_args()

    if args.send:
        if not args.to:
            parser.error("--send requires --to with a stored Gmail user.")
        send_daily_email_digest_to_user(
            email=args.to,
            hours=args.hours,
            top_n=args.top_n,
            use_llm=not args.no_llm,
        )
        print(f"Email sent to {args.to}.")
        return

    if args.to:
        recipient_email, email = build_daily_email_digest_for_user(
            email=args.to,
            hours=args.hours,
            top_n=args.top_n,
            use_llm=not args.no_llm,
        )
        print(f"Preview for: {recipient_email}")
        print(f"Subject: {email.subject}")
        print("")
        print(email.html_body if args.html else email.text_body)
        return

    email = build_daily_email_digest(
        recipient_name=args.name,
        profile_name=args.profile,
        hours=args.hours,
        top_n=args.top_n,
        use_llm=not args.no_llm,
    )
    print(f"Subject: {email.subject}")
    print("")
    print(email.html_body if args.html else email.text_body)


if __name__ == "__main__":
    main()
