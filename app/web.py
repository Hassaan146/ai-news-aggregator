"""FastAPI app for the basic AI news aggregator GUI."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.agent.email_agent import EmailAgent
from app.database.connection import get_session
from app.database.repository import (
    activate_payment_subscription,
    create_payment_subscription,
    create_payment_transaction,
    get_payment_subscription_by_checkout_session_id,
    get_site_review_by_user,
    get_user,
    get_user_by_email,
    list_site_reviews,
    upsert_user,
    upsert_site_review,
    update_user_preferences,
)
from app.profiles.user_profile import PROFILES, UserProfile, get_profile
from app.scrapers.youtube_channels import YOUTUBE_CHANNEL_IDS
from app.services.aggregator_surface import get_top_digests
from app.services.auth import create_token, hash_password, parse_token, verify_password
from app.services.email import send_email_digest
from app.services.llm_status import classify_llm_error, llm_status_message
from app.services.news_surface import collect_ai_news
from app.services.payments import (
    construct_webhook_event,
    create_checkout_session,
    retrieve_checkout_session,
)
from app.services.process_digest_items import process_digest_items

WEB_DIR = Path(__file__).parent / "web_static"
DEFAULT_CORS_ORIGIN_REGEX = (
    r"^https://.*\.vercel\.app$|"
    r"^https://.*\.onrender\.com$|"
    r"^http://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+):(5173|4173|8000)$"
)

app = FastAPI(title="AI News Aggregator GUI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5173,http://localhost:5173",
        ).split(",")
        if origin.strip()
    ],
    allow_origin_regex=DEFAULT_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
security = HTTPBearer(auto_error=False)


@app.on_event("startup")
def initialize_database() -> None:
    """Create required tables when a new hosted database is attached."""

    if os.getenv("AUTO_CREATE_TABLES", "true").strip().lower() not in {
        "1",
        "true",
        "yes",
    }:
        return

    from app.database.create_tables import create_tables

    create_tables()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return JSON for unexpected errors so browser clients can display details."""

    detail = "Internal server error. Check backend logs."
    if os.getenv("DEBUG_API_ERRORS", "false").strip().lower() in {"1", "true", "yes"}:
        detail = f"{type(exc).__name__}: {exc}"
    return JSONResponse(status_code=500, content={"detail": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return readable validation errors for browser clients."""

    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", []) if part != "body")
        message = error.get("msg", "Invalid value.")
        messages.append(f"{location}: {message}" if location else message)
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "message": "Please fix the highlighted request values before trying again.",
                "errors": messages,
            }
        },
    )


class DigestRequest(BaseModel):
    """Request for personalized digest results."""

    hours: int = Field(default=72, ge=1, le=72)
    top_n: int = Field(default=10, ge=1, le=10)
    profile_name: str | None = "default_ai_reader"
    use_llm: bool = True
    preferred_sources: list[str] = Field(default_factory=list)
    preferred_kinds: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    excluded_keywords: list[str] = Field(default_factory=list)
    generate_missing_digests: bool = True


class UserRequest(BaseModel):
    """Request to create/update a user account."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    profile_name: str = "default_ai_reader"


class EmailPreviewRequest(DigestRequest):
    """Request for a rendered email preview."""

    name: str = "Sample User"


class EmailSendRequest(EmailPreviewRequest):
    """Request to send a rendered email to a Gmail user."""

    email: str = Field(min_length=3)


class CheckoutRequest(BaseModel):
    """Request for starting a paid Stripe Checkout session."""

    name: str = Field(min_length=1)
    email: str = Field(min_length=3)


class AuthRequest(BaseModel):
    """Request for account registration/login."""

    name: str | None = None
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    profile_name: str = "default_ai_reader"


class PreferencesRequest(DigestRequest):
    """Saved preference payload for a logged-in user."""


class ReviewRequest(BaseModel):
    """Request to create or update a website review."""

    rating: int = Field(ge=1, le=5)
    review_text: str = Field(default="", max_length=2000)


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    """Resolve the authenticated user from a bearer token."""

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing auth token.")
    try:
        payload = parse_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    with get_session() as session:
        user = get_user(session, int(payload["user_id"]))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found.")
        session.expunge(user)
        return user


@app.get("/")
def index() -> FileResponse:
    """Serve the local test GUI."""

    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health(request: Request) -> dict:
    """Return basic deployment diagnostics for frontend connectivity checks."""

    return {
        "ok": True,
        "service": "ai-news-aggregator-api",
        "origin": request.headers.get("origin"),
        "cors_origins_configured": bool(os.getenv("CORS_ORIGINS")),
    }


@app.post("/api/auth/register")
def register(request: AuthRequest) -> dict:
    """Register a user account."""

    if not request.name:
        raise HTTPException(status_code=400, detail="Name is required.")
    with get_session() as session:
        existing = get_user_by_email(session, request.email)
        if existing and existing.password_hash:
            raise HTTPException(status_code=400, detail="Account already exists.")
        user = upsert_user(
            session=session,
            name=request.name,
            email=request.email,
            profile_name=request.profile_name,
            password_hash=hash_password(request.password),
            preferences=default_preferences(request.profile_name),
        )
        return auth_payload(user)


@app.post("/api/auth/login")
def login(request: AuthRequest) -> dict:
    """Login with email and password."""

    with get_session() as session:
        user = get_user_by_email(session, request.email)
        if user is None or not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        return auth_payload(user)


@app.get("/api/auth/me")
def me(user=Depends(current_user)) -> dict:
    """Return the current authenticated user."""

    return user_payload(user)


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
            limit=max(request.top_n, 100),
            profile=build_profile(request),
            use_llm=request.use_llm,
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


@app.get("/api/preferences")
def get_preferences(user=Depends(current_user)) -> dict:
    """Return saved preferences for the logged-in user."""

    return {
        "profile_name": user.profile_name,
        "preferences": user.preferences or default_preferences(user.profile_name),
    }


@app.get("/api/reviews")
def reviews(user=Depends(current_user)) -> dict:
    """Return the current user's review and recent public review summary."""

    with get_session() as session:
        own_review = get_site_review_by_user(session, user.id)
        recent_reviews = list_site_reviews(session, limit=12)
        return {
            "my_review": serialize_review(own_review),
            "reviews": [serialize_review(review) for review in recent_reviews],
        }


@app.post("/api/reviews")
def save_review(request: ReviewRequest, user=Depends(current_user)) -> dict:
    """Create or update a logged-in user's website review."""

    with get_session() as session:
        db_user = get_user(session, user.id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        review = upsert_site_review(
            session=session,
            user=db_user,
            rating=request.rating,
            review_text=request.review_text,
        )
        return {"review": serialize_review(review)}


@app.post("/api/preferences")
def save_preferences(request: PreferencesRequest, user=Depends(current_user)) -> dict:
    """Save digest preferences for the logged-in user."""

    preferences = digest_request_to_preferences(request)
    with get_session() as session:
        db_user = get_user(session, user.id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        update_user_preferences(
            session=session,
            user=db_user,
            profile_name=request.profile_name or "default_ai_reader",
            preferences=preferences,
        )
        return {
            "profile_name": db_user.profile_name,
            "preferences": db_user.preferences,
        }


@app.post("/api/dashboard/digests")
def dashboard_digests(request: DigestRequest, user=Depends(current_user)) -> dict:
    """Return top digests using the request or saved user preferences."""

    merged = merge_saved_preferences(request, user.preferences or {})
    try:
        digest_generation = None
        scrape_result = None
        if merged.generate_missing_digests:
            if os.getenv("SCRAPE_ON_DIGEST", "true").strip().lower() in {
                "1",
                "true",
                "yes",
            }:
                source_limit = int(os.getenv("SCRAPE_SOURCE_LIMIT", "3"))
                max_sources = int(os.getenv("SCRAPE_MAX_SOURCES", "20"))
                youtube_limit = int(os.getenv("SCRAPE_YOUTUBE_LIMIT", "1"))
                youtube_channel_limit = int(os.getenv("YOUTUBE_CHANNEL_LIMIT", "10"))
                youtube_channel_ids = (
                    YOUTUBE_CHANNEL_IDS[:youtube_channel_limit]
                    if "youtube_video" in merged.preferred_kinds and youtube_limit > 0
                    else []
                )
                scraped_items = collect_ai_news(
                    youtube_channel_ids=youtube_channel_ids,
                    source_limit=source_limit,
                    max_sources=max_sources,
                    source_names=merged.preferred_sources,
                    youtube_limit=youtube_limit,
                    lookback_hours=merged.hours,
                    curate=True,
                    store=True,
                )
                scrape_result = {
                    "stored_or_updated": len(scraped_items),
                    "source_limit": source_limit,
                    "max_sources": max_sources,
                    "selected_sources": merged.preferred_sources,
                    "youtube_limit": youtube_limit,
                    "youtube_channels": len(youtube_channel_ids),
                    "lookback_hours": merged.hours,
                }
            generation_limit = min(int(os.getenv("DIGEST_GENERATION_LIMIT", "25")), 500)
            digest_generation = process_digest_items(
                limit=generation_limit,
                lookback_hours=merged.hours,
                delay_seconds=float(os.getenv("DIGEST_GENERATION_DELAY_SECONDS", "8")),
                allow_fallback=os.getenv("DIGEST_ALLOW_FALLBACK", "true")
                .strip()
                .lower()
                in {"1", "true", "yes"},
            )
        response = get_top_digests(
            hours=merged.hours,
            top_n=merged.top_n,
            limit=max(merged.top_n, 100),
            profile=build_profile(merged),
            use_llm=merged.use_llm,
        )
        payload = response.model_dump(mode="json")
        if scrape_result is not None:
            payload["scrape_result"] = scrape_result
        if digest_generation is not None:
            payload["digest_generation"] = {
                "processed": digest_generation.processed,
                "created_or_updated": digest_generation.created_or_updated,
                "failed": digest_generation.failed,
                "stopped_reason": digest_generation.stopped_reason,
                "llm_status": digest_generation.llm_status,
            }
        llm_status = (
            digest_generation.llm_status
            if digest_generation is not None
            else classify_llm_error(response.fallback_reason)
        )
        if response.fallback_reason and llm_status is None:
            llm_status = classify_llm_error(response.fallback_reason)
        payload["llm_status"] = {
            "status": llm_status or ("ok" if response.ranking_method == "llm" else None),
            "message": llm_status_message(llm_status),
            "fallback_reason": response.fallback_reason,
        }
        return payload
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
def checkout(request: CheckoutRequest, http_request: Request) -> dict:
    """Create a Stripe Checkout Session for the paid email plan."""

    try:
        with get_session() as session:
            user = upsert_user(
                session=session,
                name=request.name,
                email=request.email,
                profile_name="default_ai_reader",
            )
        base_url = os.getenv("APP_BASE_URL") or str(http_request.base_url).rstrip("/")
        base_url = base_url.rstrip("/")
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
                status="pending_setup" if checkout_session["setup_mode"] else "pending",
                mode=checkout_session["mode"],
                amount_cents=checkout_session["amount_cents"],
                currency=checkout_session["currency"],
                interval=checkout_session["interval"],
                stripe_customer_id=checkout_session.get("stripe_customer_id"),
                stripe_checkout_session_id=checkout_session["id"],
                raw_payload=checkout_session,
            )
        return checkout_session
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/payments/webhook")
async def stripe_webhook(request: Request) -> dict:
    """Handle Stripe webhook events for production checkout fulfillment."""

    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = construct_webhook_event(payload, signature)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if event["type"] == "checkout.session.completed":
        checkout_session = event["data"]["object"]
        fulfill_checkout_session(
            checkout_session_id=checkout_session["id"],
            checkout_payload=checkout_session,
            send_email=True,
        )
    return {"received": True}


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


def auth_payload(user) -> dict:
    """Return user data with an auth token."""

    return {"token": create_token(user.id), "user": user_payload(user)}


def user_payload(user) -> dict:
    """Serialize a user for the dashboard."""

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profile_name": user.profile_name,
        "plan_name": user.plan_name,
        "subscription_status": user.subscription_status,
        "preferences": user.preferences or default_preferences(user.profile_name),
    }


def serialize_review(review) -> dict | None:
    """Serialize a site review for API responses."""

    if review is None:
        return None
    return {
        "id": review.id,
        "rating": review.rating,
        "review_text": review.review_text,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "updated_at": review.updated_at.isoformat() if review.updated_at else None,
    }


def default_preferences(profile_name: str = "default_ai_reader") -> dict:
    """Default preference payload."""

    profile = get_profile(profile_name)
    return {
        "hours": 72,
        "top_n": 10,
        "profile_name": profile.name,
        "use_llm": True,
        "preferred_sources": list(profile.preferred_sources),
        "preferred_kinds": list(profile.preferred_kinds),
        "keywords": list(profile.keywords),
        "excluded_keywords": list(profile.excluded_keywords),
    }


def digest_request_to_preferences(request: DigestRequest) -> dict:
    """Convert a digest request into stored preferences."""

    return {
        "hours": request.hours,
        "top_n": request.top_n,
        "profile_name": request.profile_name or "default_ai_reader",
        "use_llm": request.use_llm,
        "preferred_sources": request.preferred_sources,
        "preferred_kinds": request.preferred_kinds,
        "keywords": request.keywords,
        "excluded_keywords": request.excluded_keywords,
    }


def merge_saved_preferences(request: DigestRequest, saved: dict) -> DigestRequest:
    """Fill empty request fields from saved user preferences."""

    return DigestRequest(
        hours=request.hours or int(saved.get("hours", 72)),
        top_n=request.top_n or int(saved.get("top_n", 10)),
        profile_name=request.profile_name or saved.get("profile_name"),
        use_llm=request.use_llm,
        preferred_sources=request.preferred_sources or saved.get("preferred_sources", []),
        preferred_kinds=request.preferred_kinds or saved.get("preferred_kinds", []),
        keywords=request.keywords or saved.get("keywords", []),
        excluded_keywords=request.excluded_keywords
        or saved.get("excluded_keywords", []),
        generate_missing_digests=request.generate_missing_digests,
    )


def complete_checkout_success(session_id: str) -> str:
    """Activate a local subscription after Stripe redirects back."""

    checkout_payload = retrieve_checkout_session(session_id)
    email_address = fulfill_checkout_session(
        checkout_session_id=session_id,
        checkout_payload=checkout_payload,
        send_email=True,
    )
    return f"Subscription activated and a demo digest email was sent to {email_address}."


def fulfill_checkout_session(
    checkout_session_id: str,
    checkout_payload,
    send_email: bool = True,
) -> str:
    """Activate a subscription and optionally send the demo digest email."""

    stripe_customer_id = getattr(checkout_payload, "customer", None) or checkout_payload.get(
        "customer"
    )
    stripe_subscription_id = getattr(
        checkout_payload, "subscription", None
    ) or checkout_payload.get("subscription")
    setup_intent_id = getattr(checkout_payload, "setup_intent", None) or checkout_payload.get(
        "setup_intent"
    )
    payload_dict = (
        checkout_payload.to_dict()
        if hasattr(checkout_payload, "to_dict")
        else dict(checkout_payload)
    )
    with get_session() as session:
        subscription = get_payment_subscription_by_checkout_session_id(
            session=session,
            checkout_session_id=checkout_session_id,
        )
        if subscription is None:
            raise RuntimeError("Checkout succeeded, but no local subscription row was found.")

        activate_payment_subscription(
            session=session,
            subscription=subscription,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
            raw_payload=payload_dict,
        )
        create_payment_transaction(
            session=session,
            user=subscription.user,
            status="setup_complete" if setup_intent_id else "paid",
            amount_cents=subscription.amount_cents,
            currency=subscription.currency,
            subscription=subscription,
            stripe_checkout_session_id=checkout_session_id,
            raw_payload=payload_dict,
        )
        email_address = subscription.user.email
        name = subscription.user.name

    if send_email:
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
    return email_address


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
