"""Create database tables for the AI news aggregator."""

from __future__ import annotations

from sqlalchemy import inspect, text

from .connection import Base, engine
from .models import (  # noqa: F401
    DigestItem,
    NewsItem,
    PaymentSubscription,
    PaymentTransaction,
    SourceRun,
    User,
)

USER_COLUMN_DEFINITIONS = {
    "password_hash": "TEXT",
    "stripe_customer_id": "VARCHAR(255)",
    "plan_name": "VARCHAR(100) NOT NULL DEFAULT 'free'",
    "subscription_status": "VARCHAR(50) NOT NULL DEFAULT 'free'",
    "email_verified": "BOOLEAN NOT NULL DEFAULT false",
    "preferences": "JSON NOT NULL DEFAULT '{}'",
}


def create_tables() -> None:
    """Create all SQLAlchemy tables."""

    Base.metadata.create_all(bind=engine)
    ensure_user_columns()


def ensure_user_columns() -> None:
    """Add new account columns when upgrading an existing local database."""

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = [
        (name, definition)
        for name, definition in USER_COLUMN_DEFINITIONS.items()
        if name not in existing_columns
    ]
    if not missing_columns:
        return

    with engine.begin() as connection:
        for name, definition in missing_columns:
            connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))


if __name__ == "__main__":
    create_tables()
    print("Database tables created.")
