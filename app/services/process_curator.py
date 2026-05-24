"""Curate processed items for AI-news relevance."""

from __future__ import annotations

from .models import ProcessedItem

AI_KEYWORDS = (
    "ai",
    "agent",
    "agents",
    "artificial intelligence",
    "automation",
    "chatgpt",
    "deep learning",
    "embedding",
    "generative",
    "llm",
    "machine learning",
    "model",
    "openai",
    "rag",
    "reasoning",
)


def curate_items(
    items: list[ProcessedItem],
    keywords: tuple[str, ...] = AI_KEYWORDS,
) -> list[ProcessedItem]:
    """Keep items that look relevant to AI topics."""

    curated: list[ProcessedItem] = []
    seen_urls: set[str] = set()

    for item in items:
        normalized_url = item.url.rstrip("/")
        if normalized_url in seen_urls:
            continue
        seen_urls.add(normalized_url)

        text = f"{item.title} {item.summary}".lower()
        if any(keyword.lower() in text for keyword in keywords):
            curated.append(item)

    return curated
