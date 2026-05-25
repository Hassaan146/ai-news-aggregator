"""Curated YouTube channel IDs for AI news, research, and builder content."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class YouTubeChannelSource:
    """A YouTube channel tracked through the public RSS feed."""

    name: str
    channel_id: str
    category: str
    handle: str | None = None


YOUTUBE_CHANNEL_SOURCES: tuple[YouTubeChannelSource, ...] = (
    YouTubeChannelSource("Dave Ebbelaar", "UCn8ujwUInbJkBhffxqAPBVQ", "builder", "DaveEbbelaar"),
    YouTubeChannelSource("OpenAI", "UCXZCJLdBC09xxGZ6gcdrc6A", "official", "OpenAI"),
    YouTubeChannelSource("Google DeepMind", "UCP7jMXSY2xbc3KCAE0MHQ-A", "official", "GoogleDeepMind"),
    YouTubeChannelSource("Google Developers", "UC_x5XG1OV2P6uZZ5FSM9Ttw", "official", "GoogleDevelopers"),
    YouTubeChannelSource("Microsoft Developer", "UCV_6HOhwxYLXAGd-JOqKPoQ", "official", "MicrosoftDeveloper"),
    YouTubeChannelSource("NVIDIA Developer", "UCBHcMCGaiJhv-ESTcWGJPcw", "official", "NVIDIADeveloper"),
    YouTubeChannelSource("Hugging Face", "UCHlNU7kIZhRgSbhHvFoy72w", "official", "huggingface"),
    YouTubeChannelSource("DeepLearning.AI", "UCcIXc5mJsHVYTZR1maL5l9w", "education", "DeepLearningAI"),
    YouTubeChannelSource("LangChain", "UCC-lyoTfSrcJzA1ab3APAgw", "builder", "LangChain"),
    YouTubeChannelSource("Weights & Biases", "UCBp3w4DCEC64FZr4k9ROxig", "builder", "WeightsBiases"),
    YouTubeChannelSource("AssemblyAI", "UCtatfZMf-8EkIwASXM4ts0A", "builder", "AssemblyAI"),
    YouTubeChannelSource("Lex Fridman", "UCJIfeSCssxSC_Dhc5s7woww", "interviews", "lexfridman"),
    YouTubeChannelSource("Two Minute Papers", "UCbfYPyITQ-7l4upoX8nvctg", "research", "TwoMinutePapers"),
    YouTubeChannelSource("Yannic Kilcher", "UCHmD-oSpV0sNfAUnpYpj8KA", "research", "YannicKilcher"),
    YouTubeChannelSource("Arxiv Insights", "UCNIkB2IeJ-6AmZv7bQ1oBYg", "research", "ArxivInsights"),
    YouTubeChannelSource("Henry AI Labs", "UCGOKiIVAts7Ji-YDvNonc8w", "research", "HenryAILabs"),
    YouTubeChannelSource("AI Explained", "UCNJ1Ymd5yFuUPtn21xtRbbw", "analysis", "AIExplained-Official"),
    YouTubeChannelSource("Wes Roth", "UCqcbQf6yw5KzRoDDcZ_wBSw", "news", "WesRoth"),
    YouTubeChannelSource("The AI Grid", "UCSPkiRjFYpz-8DY-aF_1wRg", "news", "TheAIGRID"),
    YouTubeChannelSource("Matthew Berman", "UCzi5kcwU8aT4aLR7LcYhfWQ", "news", "MatthewBerman"),
    YouTubeChannelSource("MattVidPro AI", "UC06GdmaEdCdCFwR3NvszloQ", "news", "MattVidPro"),
    YouTubeChannelSource("All About AI", "UCR9j1jqqB5Rse69wjUnbYwA", "builder", "AllAboutAI"),
    YouTubeChannelSource("Prompt Engineering", "UCf4tGwyNQGyFWX3F-9rUk9A", "builder", "PromptEngineering"),
    YouTubeChannelSource("AI Jason", "UCrXSVX9a1mj8l0CMLwKgMVw", "builder", "AIJasonZ"),
    YouTubeChannelSource("James Briggs", "UCv83tO5cePwHMt1952IVVHw", "builder", "JamesBriggs"),
    YouTubeChannelSource("Nicholas Renotte", "UCHXa4OpASJEwrHrLeIzw7Yg", "builder", "NicholasRenotte"),
    YouTubeChannelSource("Fireship", "UC2Xd-TjJByJyK2w1zNwY0zQ", "developer", "Fireship"),
    YouTubeChannelSource("IBM Technology", "UC8cc4pVKVHG7A9fbNsRNrLQ", "developer", "IBMTechnology"),
    YouTubeChannelSource("Google Cloud Tech", "UCTMRxtyHoE3LPcrl-kT4AQQ", "developer", "GoogleCloudTech"),
    YouTubeChannelSource("AWS Developers", "UCd6MoB9NC6uYN2grvUNT-Zg", "developer", "AWSDevelopers"),
    YouTubeChannelSource("Coding Tech", "UCtxCXg-UvSnTKPOzLH4wJaQ", "developer", "CodingTech"),
    YouTubeChannelSource("sentdex", "UCQALLeQPoZdZC4JNUboVEUg", "education", "sentdex"),
    YouTubeChannelSource("CodeEmporium", "UC5_6ZD6s8klmMu9TXEB_1IA", "education", "CodeEmporium"),
    YouTubeChannelSource("StatQuest", "UCtYLUTtgS3k1Fg4y5tAhLbw", "education", "StatQuest"),
    YouTubeChannelSource("Computerphile", "UCoxcjq-8xIDTYp3uz647V5A", "education", "Computerphile"),
    YouTubeChannelSource("3Blue1Brown", "UC1_uAIS3r8Vu6JjXWvastJg", "education", "3blue1brown"),
)

YOUTUBE_CHANNEL_IDS = [channel.channel_id for channel in YOUTUBE_CHANNEL_SOURCES]
