"""User interest profiles for digest aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserProfile:
    """Describes what a user wants to see in their AI news feed."""

    name: str
    preferred_sources: tuple[str, ...] = ()
    preferred_kinds: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    excluded_keywords: tuple[str, ...] = ()
    source_weight: int = 5
    kind_weight: int = 3
    keyword_weight: int = 2
    recency_weight: int = 1
    metadata: dict = field(default_factory=dict)


DEFAULT_PROFILE = UserProfile(
    name="default_ai_reader",
    preferred_sources=(
        "OpenAI News",
        "OpenAI Blog",
        "Anthropic News",
        "Google DeepMind News",
        "Hugging Face Blog",
        "TechCrunch AI",
    ),
    preferred_kinds=("article", "youtube_video"),
    keywords=(
        "openai",
        "anthropic",
        "agent",
        "agents",
        "ai",
        "llm",
        "model",
        "rag",
        "research",
        "safety",
    ),
)

PROFILES: dict[str, UserProfile] = {
    DEFAULT_PROFILE.name: DEFAULT_PROFILE,
    "openai_anthropic": UserProfile(
        name="openai_anthropic",
        preferred_sources=("OpenAI News", "OpenAI Blog", "Anthropic News"),
        preferred_kinds=("article",),
        keywords=("openai", "anthropic", "claude", "chatgpt", "model", "agent"),
    ),
    "builders": UserProfile(
        name="builders",
        preferred_sources=(
            "Hugging Face Blog",
            "Towards Data Science",
            "InfoQ AI ML Data Engineering",
            "TechCrunch AI",
        ),
        preferred_kinds=("article", "youtube_video"),
        keywords=("python", "agent", "rag", "api", "developer", "open source"),
    ),
}


def get_profile(profile_name: str | None = None) -> UserProfile:
    """Return a named profile, falling back to the default profile."""

    if not profile_name:
        return DEFAULT_PROFILE
    return PROFILES.get(profile_name, DEFAULT_PROFILE)
