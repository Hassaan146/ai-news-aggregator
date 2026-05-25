"""Runner for managing local user accounts."""

from __future__ import annotations

import argparse
import sys

from app.database.connection import get_session
from app.database.repository import list_active_users, upsert_user, validate_gmail_address


def main() -> None:
    """Create or list user accounts."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Manage AI news user accounts.")
    parser.add_argument("--create", action="store_true", help="Create or update a user.")
    parser.add_argument("--list", action="store_true", help="List active users.")
    parser.add_argument("--name", help="User display name.")
    parser.add_argument("--email", help="User Gmail address.")
    parser.add_argument("--profile", default="default_ai_reader")
    args = parser.parse_args()

    if args.create:
        if not args.name or not args.email:
            parser.error("--create requires --name and --email")
        with get_session() as session:
            user = upsert_user(
                session=session,
                name=args.name,
                email=args.email,
                profile_name=args.profile,
            )
            print(
                "User saved: "
                f"id={user.id}, name={user.name}, email={user.email}, "
                f"profile={user.profile_name}"
            )
        return

    if args.list:
        with get_session() as session:
            users = list_active_users(session)
            if not users:
                print("No active users found.")
                return
            for user in users:
                print(
                    f"{user.id}: {user.name} <{user.email}> "
                    f"profile={user.profile_name}"
                )
        return

    if args.email:
        print(validate_gmail_address(args.email))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
