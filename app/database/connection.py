"""SQLAlchemy engine and session setup."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

load_dotenv()

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg2://ai_news:ai_news_password@localhost:5432/ai_news"
)
DEFAULT_POSTGRES_USER = "ai_news"
DEFAULT_POSTGRES_PASSWORD = "ai_news_password"
DEFAULT_POSTGRES_DB = "ai_news"
DEFAULT_POSTGRES_HOST = "localhost"
DEFAULT_POSTGRES_PORT = "5432"


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


def get_database_url() -> str:
    """Return the configured database URL."""

    if database_url := os.getenv("DATABASE_URL"):
        return database_url

    user = os.getenv("POSTGRES_USER", DEFAULT_POSTGRES_USER)
    password = os.getenv("POSTGRES_PASSWORD", DEFAULT_POSTGRES_PASSWORD)
    db_name = os.getenv("POSTGRES_DB", DEFAULT_POSTGRES_DB)
    host = os.getenv("POSTGRES_HOST", DEFAULT_POSTGRES_HOST)
    port = os.getenv("POSTGRES_PORT", DEFAULT_POSTGRES_PORT)
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"


def ensure_sqlite_directory(database_url: str) -> None:
    """Create the parent folder for a local SQLite database."""

    if not database_url.startswith("sqlite:///"):
        return

    db_path = database_url.replace("sqlite:///", "", 1)
    if db_path == ":memory:":
        return

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


DATABASE_URL = get_database_url()
ensure_sqlite_directory(DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite:///")
    else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def get_session() -> Iterator[Session]:
    """Yield a database session and handle commit/rollback."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
