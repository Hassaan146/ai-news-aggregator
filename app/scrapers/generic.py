"""Generic website and RSS scraping helpers for AI news sources."""

from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from .models import Article, NewsSource
from .sources import SOURCES

DEFAULT_TIMEOUT = 20
HEADERS = {
    "User-Agent": "ai-news-aggregator/0.1 (+https://example.com/bot)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def scrape_all_sources(
    limit_per_source: int = 10,
    max_sources: int | None = None,
    source_names: list[str] | tuple[str, ...] | None = None,
) -> list[Article]:
    """Scrape every configured AI news source."""

    if limit_per_source <= 0:
        return []

    articles: list[Article] = []
    selected_sources = SOURCES
    if source_names:
        allowed_names = {name.strip().lower() for name in source_names if name.strip()}
        selected_sources = tuple(
            source for source in selected_sources if source.name.lower() in allowed_names
        )
    selected_sources = selected_sources[:max_sources] if max_sources else selected_sources
    for source in selected_sources:
        try:
            articles.extend(scrape_source(source, limit=limit_per_source))
        except Exception as exc:
            print(f"Skipping {source.name}: {exc}")
    return dedupe_articles(articles)


def scrape_source(source: NewsSource, limit: int = 10) -> list[Article]:
    """Scrape one source, preferring RSS/Atom when configured."""

    if limit <= 0:
        return []

    if source.feed_url:
        feed_articles = scrape_feed(source, limit=limit)
        if feed_articles:
            return feed_articles
    return scrape_listing_page(source, limit=limit)


def scrape_feed(source: NewsSource, limit: int = 10) -> list[Article]:
    """Read articles from an RSS or Atom feed."""

    parsed = feedparser.parse(source.feed_url or source.url)
    articles: list[Article] = []
    for entry in parsed.entries[:limit]:
        title = clean_text(getattr(entry, "title", ""))
        url = getattr(entry, "link", "")
        summary = clean_text(getattr(entry, "summary", ""))
        published_at = parse_entry_date(entry)
        if title and url:
            articles.append(
                Article(
                    source=source.name,
                    title=title,
                    url=url,
                    summary=summary,
                    published_at=published_at,
                )
            )
    return articles


def scrape_listing_page(source: NewsSource, limit: int = 10) -> list[Article]:
    """Find likely article links on a source listing page."""

    response = requests.get(source.url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    articles: list[Article] = []
    seen_urls: set[str] = set()
    for link in soup.select("article a[href], h1 a[href], h2 a[href], h3 a[href], a[href]"):
        title = clean_text(link.get_text(" "))
        url = urljoin(source.url, link.get("href", ""))
        if not is_probable_article(title, url, source.url) or url in seen_urls:
            continue
        seen_urls.add(url)
        articles.append(Article(source=source.name, title=title, url=url))
        if len(articles) >= limit:
            break
    return articles


def dedupe_articles(articles: list[Article]) -> list[Article]:
    """Remove duplicate article URLs while keeping source order."""

    deduped: list[Article] = []
    seen: set[str] = set()
    for article in articles:
        normalized_url = article.url.rstrip("/")
        if normalized_url in seen:
            continue
        seen.add(normalized_url)
        deduped.append(article)
    return deduped


def parse_entry_date(entry: object) -> datetime | None:
    """Parse common feed date fields into a datetime."""

    for field in ("published", "updated", "created"):
        value = getattr(entry, field, None)
        if not value:
            continue
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError):
            continue
    return None


def clean_text(value: str) -> str:
    """Normalize whitespace and strip HTML from a string."""

    text = BeautifulSoup(value or "", "html.parser").get_text(" ")
    return " ".join(unescape(text).split())


def is_probable_article(title: str, url: str, base_url: str) -> bool:
    """Filter navigation links while keeping likely article links."""

    if not title or len(title) < 12 or not url.startswith(("http://", "https://")):
        return False
    ignored = ("#", "mailto:", "javascript:", ".pdf")
    if any(token in url.lower() for token in ignored):
        return False
    nav_titles = {
        "about", "advertise", "careers", "contact", "home", "login", "privacy",
        "subscribe", "terms", "topics", "events", "newsletter", "podcasts",
        "skip to main content",
    }
    if title.strip().lower() in nav_titles:
        return False
    return True
