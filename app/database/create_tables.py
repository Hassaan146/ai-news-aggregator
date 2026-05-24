"""Create database tables for the AI news aggregator."""

from __future__ import annotations

from .connection import Base, engine
from .models import NewsItem  # noqa: F401


def create_tables() -> None:
    """Create all SQLAlchemy tables."""

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Database tables created.")
