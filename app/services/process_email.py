"""Service surface for creating daily email digests."""

from __future__ import annotations

from app.agent.email_agent import EmailAgent, EmailDigest
from app.database.connection import get_session
from app.database.repository import get_user, get_user_by_email
from app.services.aggregator_surface import get_top_digests
from app.services.email import send_email_digest


def build_daily_email_digest(
    recipient_name: str,
    profile_name: str | None = None,
    hours: int = 24,
    top_n: int = 10,
    use_llm: bool = True,
) -> EmailDigest:
    """Build a daily personalized email digest without sending it."""

    top_digests = get_top_digests(
        hours=hours,
        top_n=top_n,
        profile_name=profile_name,
        limit=max(top_n, 25),
        use_llm=use_llm,
    )
    return EmailAgent().build_daily_digest_email(
        recipient_name=recipient_name,
        top_digests=top_digests,
    )


def build_daily_email_digest_for_user(
    user_id: int | None = None,
    email: str | None = None,
    hours: int = 24,
    top_n: int = 10,
    use_llm: bool = True,
) -> tuple[str, EmailDigest]:
    """Build a daily email digest for a stored user."""

    with get_session() as session:
        user = get_user(session, user_id) if user_id is not None else None
        if user is None and email:
            user = get_user_by_email(session, email)
        if user is None:
            raise ValueError("User not found.")

        recipient_email = user.email
        recipient_name = user.name
        profile_name = user.profile_name

    digest = build_daily_email_digest(
        recipient_name=recipient_name,
        profile_name=profile_name,
        hours=hours,
        top_n=top_n,
        use_llm=use_llm,
    )
    return recipient_email, digest


def send_daily_email_digest_to_user(
    user_id: int | None = None,
    email: str | None = None,
    hours: int = 24,
    top_n: int = 10,
    use_llm: bool = True,
) -> None:
    """Build and send a daily digest to a stored user."""

    recipient_email, digest = build_daily_email_digest_for_user(
        user_id=user_id,
        email=email,
        hours=hours,
        top_n=top_n,
        use_llm=use_llm,
    )
    send_email_digest(recipient_email, digest)
