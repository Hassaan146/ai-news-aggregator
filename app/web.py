"""FastAPI app for the basic AI news aggregator GUI."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent.email_agent import EmailAgent
from app.database.connection import get_session
from app.database.repository import (
    activate_payment_subscription,
    create_payment_subscription,
    create_payment_transaction,
    get_payment_subscription_by_checkout_session_id,
    upsert_user,
)
from app.profiles.user_profile import PROFILES, UserProfile, get_profile
from app.services.aggregator_surface import get_top_digests
from app.services.email import send_email_digest
from app.services.payments import create_checkout_session, retrieve_checkout_session

WEB_DIR = Path(__file__).parent / "web_static"

app = FastAPI(title="AI News Aggregator GUI")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


class DigestRequest(BaseModel):
    """Request for personalized digest results."""

    hours: int = Field(default=24, ge=1, le=168)
    top_n: int = Field(default=10, ge=1, le=50)
    profile_name: str | None = "default_ai_reader"
    use_llm: bool = True
    gemini_api_key: str | None = None
    preferred_sources: list[str] = Field(default_factory=list)
    preferred_kinds: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)


class UserRequest(BaseModel):
    """Request to create/update a user account."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    profile_name: str = "default_ai_reader"


class EmailPreviewRequest(DigestRequest):
    """Request for a rendered email preview."""

    name: str = "Hassan"


class EmailSendRequest(EmailPreviewRequest):
    """Request to send a rendered email to a Gmail user."""

    email: str = Field(min_length=3)


class CheckoutRequest(BaseModel):
    """Request for starting a paid Stripe Checkout session."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)


@app.get("/")
def index() -> FileResponse:
    """Serve the local test GUI."""

    return FileResponse(WEB_DIR / "index.html")


@app.get("/success", response_class=HTMLResponse)
def success(session_id: str | None = None) -> HTMLResponse:
    """Complete a checkout and serve a payment success page."""

    if not session_id:
        return HTMLResponse((WEB_DIR / "success.html").read_text(encoding="utf-8"))

    try:
        message = complete_checkout_success(session_id)
    except Exception as exc:
        message = f"Payment completed, but local fulfillment failed: {exc}"

    return HTMLResponse(
        build_message_page(
            title="Payment successful",
            eyebrow="Stripe checkout",
            message=message,
        )
    )


@app.get("/cancel")
def cancel() -> FileResponse:
    """Serve a payment cancellation page."""

    return FileResponse(WEB_DIR / "cancel.html")


@app.get("/api/profiles")
def list_profiles() -> dict:
    """Return available built-in profiles."""

    return {
        "profiles": [
            {
                "name": profile.name,
                "preferred_sources": list(profile.preferred_sources),
                "preferred_kinds": list(profile.preferred_kinds),
                "keywords": list(profile.keywords),
                "excluded_keywords": list(profile.excluded_keywords),
            }
            for profile in PROFILES.values()
        ]
    }


@app.post("/api/digests")
def digests(request: DigestRequest) -> dict:
    """Return top ranked digests for the requested preferences."""

    try:
        response = get_top_digests(
            hours=request.hours,
            top_n=request.top_n,
            profile=build_profile(request),
            use_llm=request.use_llm,
            llm_api_key=clean_optional(request.gemini_api_key),
        )
        return response.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/users")
def create_user(request: UserRequest) -> dict:
    """Create or update a Gmail user account."""

    try:
        with get_session() as session:
            user = upsert_user(
                session=session,
                name=request.name,
                email=request.email,
                profile_name=request.profile_name,
            )
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "profile_name": user.profile_name,
                "is_active": user.is_active,
            }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/email/preview")
def preview_email(request: EmailPreviewRequest) -> dict:
    """Build an email preview without sending."""

    try:
        digest_response = get_top_digests(
            hours=request.hours,
            top_n=request.top_n,
            profile=build_profile(request),
            use_llm=request.use_llm,
            llm_api_key=clean_optional(request.gemini_api_key),
        )
        email = EmailAgent().build_daily_digest_email(
            recipient_name=request.name,
            top_digests=digest_response,
        )
        return {
            "subject": email.subject,
            "text_body": email.text_body,
            "html_body": email.html_body,
            "ranking_method": digest_response.ranking_method,
            "fallback_reason": digest_response.fallback_reason,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/email/send")
def send_email(request: EmailSendRequest) -> dict:
    """Send a live Gmail digest email."""

    try:
        with get_session() as session:
            upsert_user(
                session=session,
                name=request.name,
                email=request.email,
                profile_name=request.profile_name or "default_ai_reader",
            )

        digest_response = get_top_digests(
            hours=request.hours,
            top_n=request.top_n,
            profile=build_profile(request),
            use_llm=request.use_llm,
            llm_api_key=clean_optional(request.gemini_api_key),
        )
        email = EmailAgent().build_daily_digest_email(
            recipient_name=request.name,
            top_digests=digest_response,
        )
        send_email_digest(request.email, email)
        return {
            "sent": True,
            "to": request.email,
            "subject": email.subject,
            "ranking_method": digest_response.ranking_method,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/payments/checkout")
def checkout(request: CheckoutRequest) -> dict:
    """Create a Stripe Checkout Session for the paid email plan."""

    try:
        with get_session() as session:
            user = upsert_user(
                session=session,
                name=request.name,
                email=request.email,
                profile_name="default_ai_reader",
            )
        base_url = "http://127.0.0.1:8000"
        checkout_session = create_checkout_session(
            customer_email=user.email,
            customer_name=user.name,
            success_url=f"{base_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{base_url}/cancel",
        )
        with get_session() as session:
            user = upsert_user(
                session=session,
                name=request.name,
                email=request.email,
                profile_name="default_ai_reader",
            )
            subscription = create_payment_subscription(
                session=session,
                user=user,
                plan_name=checkout_session["plan_name"],
                status="active" if checkout_session["free_plan"] else "pending",
                mode=checkout_session["mode"],
                amount_cents=checkout_session["amount_cents"],
                currency=checkout_session["currency"],
                interval=checkout_session["interval"],
                stripe_customer_id=checkout_session.get("stripe_customer_id"),
                stripe_checkout_session_id=checkout_session["id"],
                raw_payload=checkout_session,
            )
            if checkout_session["free_plan"]:
                create_payment_transaction(
                    session=session,
                    user=user,
                    status="paid",
                    amount_cents=0,
                    currency=checkout_session["currency"],
                    subscription=subscription,
                    stripe_checkout_session_id=checkout_session["id"],
                    raw_payload=checkout_session,
                )
        return checkout_session
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def build_profile(request: DigestRequest) -> UserProfile:
    """Build either a custom profile or a built-in profile."""

    base = get_profile(request.profile_name)
    if not any(
        [
            request.preferred_sources,
            request.preferred_kinds,
            request.keywords,
            request.excluded_keywords,
        ]
    ):
        return base

    return UserProfile(
        name=f"custom_{base.name}",
        preferred_sources=tuple(request.preferred_sources or base.preferred_sources),
        preferred_kinds=tuple(request.preferred_kinds or base.preferred_kinds),
        keywords=tuple(request.keywords or base.keywords),
        excluded_keywords=tuple(request.excluded_keywords or base.excluded_keywords),
        source_weight=base.source_weight,
        kind_weight=base.kind_weight,
        keyword_weight=base.keyword_weight,
        recency_weight=base.recency_weight,
        metadata={**base.metadata, "source_profile": base.name},
    )


def clean_optional(value: str | None) -> str | None:
    """Normalize optional form text."""

    if value is None:
        return None
    value = value.strip()
    return value or None


def complete_checkout_success(session_id: str) -> str:
    """Activate a local subscription after Stripe redirects back."""

    checkout_payload = None
    stripe_customer_id = None
    stripe_subscription_id = None
    if not session_id.startswith("free_test_"):
        checkout_payload = retrieve_checkout_session(session_id)
        stripe_customer_id = checkout_payload.customer
        stripe_subscription_id = checkout_payload.subscription

    with get_session() as session:
        subscription = get_payment_subscription_by_checkout_session_id(
            session=session,
            checkout_session_id=session_id,
        )
        if subscription is None:
            return "Checkout succeeded, but no local subscription row was found."

        activate_payment_subscription(
            session=session,
            subscription=subscription,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            raw_payload=checkout_payload.to_dict() if checkout_payload else None,
        )
        create_payment_transaction(
            session=session,
            user=subscription.user,
            status="paid",
            amount_cents=subscription.amount_cents,
            currency=subscription.currency,
            subscription=subscription,
            stripe_checkout_session_id=session_id,
            raw_payload=checkout_payload.to_dict() if checkout_payload else {},
        )
        email_address = subscription.user.email
        name = subscription.user.name

    digest_response = get_top_digests(
        hours=24,
        top_n=10,
        profile_name="default_ai_reader",
        use_llm=False,
    )
    email = EmailAgent().build_daily_digest_email(
        recipient_name=name,
        top_digests=digest_response,
    )
    send_email_digest(email_address, email)
    return f"Subscription activated and a demo digest email was sent to {email_address}."


def build_message_page(title: str, eyebrow: str, message: str) -> str:
    """Render a small HTML message page."""

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="stylesheet" href="/static/styles.css" />
  </head>
  <body>
    <main class="center-page">
      <section class="panel message-panel">
        <p class="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{message}</p>
        <a class="link-button" href="/">Back to dashboard</a>
      </section>
    </main>
  </body>
</html>"""
