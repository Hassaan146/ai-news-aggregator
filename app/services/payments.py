"""Stripe Checkout payment service."""

from __future__ import annotations

import os

import stripe
from dotenv import load_dotenv

from app.database.repository import validate_gmail_address

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

    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key or secret_key == "sk_test_your_stripe_secret_key_here":
        raise RuntimeError("Missing real STRIPE_SECRET_KEY in .env.")

    stripe.api_key = secret_key
    customer_email = validate_gmail_address(customer_email)
    mode = os.getenv("STRIPE_CHECKOUT_MODE", "subscription").strip().lower()
    price_id = clean_optional(os.getenv("STRIPE_PRICE_ID"))

    if mode not in {"subscription", "payment"}:
        raise RuntimeError("STRIPE_CHECKOUT_MODE must be subscription or payment.")

    session = stripe.checkout.Session.create(
        mode=mode,
        customer_email=customer_email,
        line_items=[build_line_item(mode=mode, price_id=price_id)],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "customer_name": customer_name,
            "customer_email": customer_email,
            "product": "ai_news_email_plan",
        },
    )
    return {"id": session.id, "url": session.url}


def build_line_item(mode: str, price_id: str | None = None) -> dict:
    """Build Checkout line item from a configured price or inline price data."""

    if price_id:
        return {"price": price_id, "quantity": 1}

    amount = int(os.getenv("STRIPE_AMOUNT_CENTS", str(DEFAULT_AMOUNT_CENTS)))
    currency = os.getenv("STRIPE_CURRENCY", DEFAULT_CURRENCY).strip().lower()
    product_name = os.getenv("STRIPE_PRODUCT_NAME", DEFAULT_PRODUCT_NAME).strip()
    price_data = {
        "currency": currency,
        "product_data": {"name": product_name},
        "unit_amount": amount,
    }
    if mode == "subscription":
        price_data["recurring"] = {
            "interval": os.getenv("STRIPE_INTERVAL", DEFAULT_INTERVAL).strip().lower()
        }
    return {"price_data": price_data, "quantity": 1}


def clean_optional(value: str | None) -> str | None:
    """Return a stripped optional string."""

    if value is None:
        return None
    value = value.strip()
    return value or None
