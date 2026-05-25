"""Gemini-powered agent for creating digest summaries."""

from __future__ import annotations

from dataclasses import dataclass

from dotenv import load_dotenv

from app.database.models import NewsItem
from app.agent.llm_client import default_model, default_provider, generate_json

load_dotenv()

DEFAULT_DIGEST_MODEL = default_model(default_provider())

DIGEST_INSTRUCTIONS = """
You are an AI news digest editor.
Your job is to turn one scraped news item into a useful digest entry.
Write a concise, factual title and a two to three sentence summary.
Prefer concrete details from the source item. Do not invent facts.
If the source item is weak or navigation-like, summarize only what is clearly present.
"""

@dataclass(frozen=True)
class DigestAgentResult:
    """Structured output returned by the digest agent."""

    title: str
    summary: str
    model: str
    response_id: str | None
    raw_response: dict


class DigestAgent:
    """Creates short structured digest entries with the configured LLM API."""

    def __init__(
        self,
        model: str = DEFAULT_DIGEST_MODEL,
        api_key: str | None = None,
    ) -> None:
        self.model = model
        self.api_key = api_key

    def summarize_news_item(self, news_item: NewsItem) -> DigestAgentResult:
        """Generate one digest entry for a database news item."""

        schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "A concise digest title for this item.",
                },
                "summary": {
                    "type": "string",
                    "description": "A factual two to three sentence summary.",
                },
            },
            "required": ["title", "summary"],
        }
        payload, raw_response, response_id, model = generate_json(
            system_instruction=DIGEST_INSTRUCTIONS,
            user_prompt=build_digest_input(news_item),
            schema=schema,
            model=self.model,
            api_key=self.api_key,
            max_output_tokens=300,
            temperature=0,
        )
        return DigestAgentResult(
            title=payload["title"].strip(),
            summary=payload["summary"].strip(),
            model=model,
            response_id=response_id,
            raw_response=raw_response,
        )


def build_digest_input(news_item: NewsItem) -> str:
    """Build the model input from a stored news item."""

    metadata = json.dumps(news_item.item_metadata or {}, ensure_ascii=False)
    parts = [
        f"Source: {news_item.source}",
        f"Type: {news_item.kind}",
        f"Original title: {news_item.title}",
        f"URL: {news_item.url}",
        f"Published at: {news_item.published_at}",
        f"Scraped summary: {news_item.summary or ''}",
        f"Content: {news_item.content or ''}",
        f"Transcript: {news_item.transcript or ''}",
        f"Metadata: {metadata}",
    ]
    return "\n".join(parts)
