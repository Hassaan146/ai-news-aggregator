"""Shared service-layer data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ProcessedItem:
    """A normalized item after scraping and service processing."""

    source: str
    title: str
    url: str
    kind: str
    summary: str = ""
    published_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    content: str | None = None
    transcript: str | None = None
    transcript_status: str = "not_requested"

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly dictionary."""

        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "kind": self.kind,
            "summary": self.summary,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "metadata": self.metadata,
            "content": self.content,
            "transcript": self.transcript,
            "transcript_status": self.transcript_status,
        }
