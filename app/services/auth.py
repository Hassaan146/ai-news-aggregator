"""Small password and token helpers for local account auth."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from dotenv import load_dotenv

load_dotenv()

DEFAULT_TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256."""

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 260_000)
    return "pbkdf2_sha256$260000${}${}".format(
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, stored_hash: str | None) -> bool:
    """Verify a password against a stored PBKDF2 hash."""

    if not stored_hash:
        return False
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    salt = base64.urlsafe_b64decode(salt_b64.encode())
    expected = base64.urlsafe_b64decode(digest_b64.encode())
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        int(iterations),
    )
    return hmac.compare_digest(actual, expected)


def create_token(user_id: int, ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS) -> str:
    """Create a signed stateless auth token."""

    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + ttl_seconds,
        "nonce": secrets.token_urlsafe(8),
    }
    encoded_payload = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode()
    signature = sign(encoded_payload)
    return f"{encoded_payload}.{signature}"


def parse_token(token: str) -> dict:
    """Validate and decode a signed auth token."""

    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("Invalid auth token.") from exc
    if not hmac.compare_digest(signature, sign(encoded_payload)):
        raise ValueError("Invalid auth token signature.")

    payload = json.loads(base64.urlsafe_b64decode(encoded_payload.encode()).decode())
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Auth token expired.")
    return payload


def sign(value: str) -> str:
    """Return an HMAC signature for a token payload."""

    secret = os.getenv("AUTH_SECRET_KEY") or os.getenv("GEMINI_API_KEY") or "dev-secret"
    digest = hmac.new(secret.encode(), value.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode()
