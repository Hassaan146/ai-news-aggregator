"""Build digest output from processed/curated items."""

from __future__ import annotations

from collections import defaultdict

from .models import ProcessedItem


def build_markdown_digest(items: list[ProcessedItem], title: str = "AI News Digest") -> str:
    """Create a Markdown digest grouped by item type."""

    grouped: dict[str, list[ProcessedItem]] = defaultdict(list)
    for item in items:
        grouped[item.kind].append(item)

    lines = [f"# {title}", ""]
    for kind, kind_items in grouped.items():
        heading = kind.replace("_", " ").title()
        lines.extend([f"## {heading}", ""])
        for item in kind_items:
            date = item.published_at.date().isoformat() if item.published_at else "No date"
            lines.append(f"- {date} | {item.title}")
            lines.append(f"  {item.url}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
