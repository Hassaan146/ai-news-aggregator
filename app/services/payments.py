"""Stripe Checkout payment service."""

from __future__ import annotations

import os
from uuid import uuid4

import stripe
from dotenv import load_dotenv

from app.database.repository import validate_email_address

load_dotenv()

DEFAULT_PRODUCT_NAME = "AI News Daily Email Plan"
DEFAULT_CURRENCY = "usd"
DEFAULT_AMOUNT_CENTS = 500
DEFAULT_INTERVAL = "month"


def create_checkout_session(
    customer_email: str,
    customer_name: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """Create a Stripe Checkout Session and return its id/url."""

    customer_email = validate_email_address(customer_email)
    mode = os.getenv("STRIPE_CHECKOUT_MODE", "subscription").strip().lower()
    price_id = clean_optional(os.getenv("STRIPE_PRICE_ID"))
    amount = int(os.getenv("STRIPE_AMOUNT_CENTS", str(DEFAULT_AMOUNT_CENTS)))
    currency = os.getenv("STRIPE_CURRENCY", DEFAULT_CURRENCY).strip().lower()
    interval = os.getenv("STRIPE_INTERVAL", DEFAULT_INTERVAL).strip().lower()
    product_name = os.getenv("STRIPE_PRODUCT_NAME", DEFAULT_PRODUCT_NAME).strip()

    if mode not in {"subscription", "payment"}:
        raise RuntimeError("STRIPE_CHECKOUT_MODE must be subscription or payment.")

    if amount <= 0 and not price_id:
        session_id = f"free_test_{uuid4().hex}"
        success_url = success_url.replace("{CHECKOUT_SESSION_ID}", session_id)
        separator = "&" if "?" in success_url else "?"
        return {
            "id": session_id,
            "url": f"{success_url}{separator}free_plan=1",
            "free_plan": True,
            "mode": mode,
            "plan_name": product_name,
            "amount_cents": 0,
            "currency": currency,
            "interval": interval if mode == "subscription" else None,
        }

    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key or secret_key == "sk_test_your_stripe_secret_key_here":
        raise RuntimeError("Missing real STRIPE_SECRET_KEY in .env.")

    stripe.api_key = secret_key
    session = stripe.checkout.Session.create(
        mode=mode,
        customer_email=customer_email,
        line_items=[
            build_line_item(
                mode=mode,
                price_id=price_id,
                amount_cents=amount,
                currency=currency,
                interval=interval,
                product_name=product_name,
            )
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "customer_name": customer_name,
            "customer_email": customer_email,
            "product": "ai_news_email_plan",
        },
    )
    return {
        "id": session.id,
        "url": session.url,
        "free_plan": False,
        "mode": mode,
        "plan_name": product_name,
        "amount_cents": amount,
        "currency": currency,
        "interval": interval if mode == "subscription" else None,
        "stripe_customer_id": session.customer,
    }


def build_line_item(
    mode: str,
    price_id: str | None = None,
    amount_cents: int = DEFAULT_AMOUNT_CENTS,
    currency: str = DEFAULT_CURRENCY,
    interval: str = DEFAULT_INTERVAL,
    product_name: str = DEFAULT_PRODUCT_NAME,
) -> dict:
    """Build Checkout line item from a configured price or inline price data."""

    if price_id:
        return {"price": price_id, "quantity": 1}

    price_data = {
        "currency": currency,
        "product_data": {"name": product_name},
        "unit_amount": amount_cents,
    }
    if mode == "subscription":
        price_data["recurring"] = {"interval": interval}
    return {"price_data": price_data, "quantity": 1}


def retrieve_checkout_session(session_id: str):
    """Retrieve a Stripe Checkout Session after the user returns."""

    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key or secret_key == "sk_test_your_stripe_secret_key_here":
        raise RuntimeError("Missing real STRIPE_SECRET_KEY in .env.")
    stripe.api_key = secret_key
    return stripe.checkout.Session.retrieve(session_id)


def clean_optional(value: str | None) -> str | None:
    """Return a stripped optional string."""

    if value is None:
        return None
    value = value.strip()
    return value or None
