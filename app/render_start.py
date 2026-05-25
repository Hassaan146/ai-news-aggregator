"""Render startup wrapper with explicit diagnostics.

Render sometimes shows only "Exited with status 1" when the ASGI import fails.
This module prints a safe startup report and a full traceback before exiting.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
import traceback
from urllib.parse import urlsplit, urlunsplit

import uvicorn


def env_status(name: str) -> str:
    """Return whether an environment variable is configured without leaking it."""

    value = os.getenv(name)
    return "set" if value else "missing"


def normalize_database_url_preview(database_url: str) -> str:
    """Normalize common URL paste formats without importing the DB module."""

    database_url = database_url.strip().strip("\"'")
    database_url = re.sub(r"^export\s+", "", database_url).strip()
    if database_url.startswith("psql "):
        match = re.search(r"['\"]([^'\"]+)['\"]", database_url)
        if match:
            database_url = match.group(1)
    if re.match(r"^DATABASE_URL\s*=", database_url):
        database_url = database_url.split("=", 1)[1].strip().strip("\"'")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return database_url


def mask_database_url(database_url: str) -> str:
    """Return a safe database URL preview for Render logs."""

    database_url = normalize_database_url_preview(database_url)
    try:
        parts = urlsplit(database_url)
    except ValueError:
        return f"unparseable prefix={database_url[:20]!r} length={len(database_url)}"

    netloc = parts.netloc
    if "@" in netloc:
        credentials, host = netloc.rsplit("@", 1)
        username = credentials.split(":", 1)[0]
        netloc = f"{username}:***@{host}"

    safe_url = urlunsplit((parts.scheme, netloc, parts.path, parts.query, ""))
    return f"{safe_url[:120]} length={len(database_url)}"


def print_startup_report() -> None:
    """Print dependency and environment information useful for Render deploys."""

    fastapi = importlib.import_module("fastapi")
    starlette = importlib.import_module("starlette")
    sqlalchemy = importlib.import_module("sqlalchemy")
    stripe = importlib.import_module("stripe")

    print("=== Render startup diagnostics ===", flush=True)
    print(f"Python: {sys.version}", flush=True)
    print(f"FastAPI: {fastapi.__version__}", flush=True)
    print(f"Starlette: {starlette.__version__}", flush=True)
    print(f"SQLAlchemy: {sqlalchemy.__version__}", flush=True)
    print(f"Stripe: {getattr(stripe, 'VERSION', 'unknown')}", flush=True)
    print(f"PORT: {env_status('PORT')}", flush=True)
    print(f"DATABASE_URL: {env_status('DATABASE_URL')}", flush=True)
    if os.getenv("DATABASE_URL"):
        print(
            f"DATABASE_URL preview: {mask_database_url(os.getenv('DATABASE_URL', ''))}",
            flush=True,
        )
    print(f"CORS_ORIGINS: {env_status('CORS_ORIGINS')}", flush=True)
    print(f"AUTH_SECRET_KEY: {env_status('AUTH_SECRET_KEY')}", flush=True)
    print(f"GEMINI_API_KEY: {env_status('GEMINI_API_KEY')}", flush=True)
    print(f"STRIPE_SECRET_KEY: {env_status('STRIPE_SECRET_KEY')}", flush=True)
    print("==================================", flush=True)


def main() -> None:
    """Import the FastAPI app with diagnostics, then start Uvicorn."""

    try:
        print_startup_report()
        importlib.import_module("app.web")
        print("ASGI import check: app.web imported successfully", flush=True)
    except Exception:
        print("ASGI import check failed. Full traceback:", flush=True)
        traceback.print_exc()
        raise

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.web:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
