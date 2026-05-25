"""Email agent for daily personalized AI news digests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.schemas.aggregator import TopDigestResponse


@dataclass(frozen=True)
class EmailDigest:
    """Rendered email digest content."""

    subject: str
    text_body: str
    html_body: str


class EmailAgent:
    """Creates daily email content from ranked digest items."""

    def build_daily_digest_email(
        self,
        recipient_name: str,
        top_digests: TopDigestResponse,
    ) -> EmailDigest:
        """Render a daily digest email for one recipient."""

        today = datetime.now(UTC).date().isoformat()
        subject = f"Your AI news digest for {today}"
        text_body = build_text_email(recipient_name, top_digests)
        html_body = build_html_email(recipient_name, top_digests)
        return EmailDigest(subject=subject, text_body=text_body, html_body=html_body)


def build_text_email(recipient_name: str, top_digests: TopDigestResponse) -> str:
    """Build a plain-text email body."""

    lines = [
        f"Hi {recipient_name},",
        "",
        "Here are the top AI updates from the last "
        f"{top_digests.lookback_hours} hours, ranked for your profile. "
        "Each item includes a short summary and the original link.",
        "",
    ]

    if not top_digests.items:
        lines.append("No matching digest items were found for this window.")
        return "\n".join(lines).rstrip() + "\n"

    for item in top_digests.items:
        date = item.published_at.date().isoformat() if item.published_at else "No date"
        lines.extend(
            [
                f"{item.rank}. {item.title}",
                f"Source: {item.source} | Type: {item.kind} | Date: {date}",
                f"Score: {item.score} | Ranking: {item.rank_source}",
                item.summary,
                f"Read more: {item.url}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_html_email(recipient_name: str, top_digests: TopDigestResponse) -> str:
    """Build a simple HTML email body."""

    items_html = []
    for item in top_digests.items:
        date = item.published_at.date().isoformat() if item.published_at else "No date"
        badges = ", ".join(f"{badge.label}: {badge.value}" for badge in item.badges)
        items_html.append(
            f"""
            <article>
              <h2>{item.rank}. {escape_html(item.title)}</h2>
              <p><strong>{escape_html(item.source)}</strong> - {escape_html(item.kind)} - {date}</p>
              <p>{escape_html(item.summary)}</p>
              <p><strong>Score:</strong> {item.score} - <strong>Ranking:</strong> {escape_html(item.rank_source)}</p>
              <p><strong>Why matched:</strong> {escape_html(badges)}</p>
              <p><a href="{item.url}">Read the original</a></p>
            </article>
            """
        )

    if not items_html:
        items_html.append("<p>No matching digest items were found for this window.</p>")

    return f"""
    <!doctype html>
    <html>
      <body>
        <p>Hi {escape_html(recipient_name)},</p>
        <p>
          Here are the top AI updates from the last {top_digests.lookback_hours}
          hours, ranked for your profile. Each item includes a short summary and
          the original link.
        </p>
        {''.join(items_html)}
      </body>
    </html>
    """.strip()


def escape_html(value: object) -> str:
    """Escape enough HTML for simple generated email templates."""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
