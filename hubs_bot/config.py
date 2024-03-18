"""Configuration for the bot."""
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Final

BASE_URL: Final = "https://www.beaconjournal.com"
NEWS_TAGS: Final = ("LOCAL", "HUDSON HUB TIMES")


def create_tuple_factory(
    env_name: str, default: tuple[str, ...], env: Mapping[str, str | tuple[str, ...]]
) -> Callable[[], tuple[str, ...]]:
    """Create a factory for a tuple from an environment variable."""

    def _get_set() -> tuple[str, ...]:
        value = env.get(env_name, default)
        if isinstance(value, str):
            return tuple(value.split(","))
        if isinstance(value, tuple):
            return value
        msg = f"${env_name} is not set correctly"
        raise ValueError(msg)

    return _get_set


@dataclass
class Config:
    """Configuration for the bot."""

    base_url: str = field(default=os.environ.get("BASE_URL", BASE_URL))
    hubtimes_url: str = field(
        default=os.environ.get("HUBTIMES_URL", f"{BASE_URL}/communities/hudsonhubtimes/")
    )
    cookies_file: str = field(default=os.environ.get("COOKIES_FILE", "cookies.txt"))
    subreddit: str = field(default=os.environ.get("SUBREDDIT", "hudsonohtest"))
    subreddit_flair: str = field(
        default=os.environ.get("SUBREDDIT_FLAIR", "93312688-b815-11ea-917e-0e65e9cea44f")
    )
    news_tags: tuple[str, ...] = field(
        default_factory=create_tuple_factory("NEWS_TAGS", NEWS_TAGS, os.environ)
    )
    username: str = field(default=os.environ.get("USERNAME", "hubs-bot"))
    password: str = field(default=os.environ.get("PASSWORD", "password"))
    client_id: str = field(default=os.environ.get("CLIENT_ID", "client_id"))
    client_secret: str = field(default=os.environ.get("CLIENT_SECRET", "client_secret"))
    openai_key: str = field(default=os.environ.get("OPEN_AI_KEY", "open_ai_key"))
    openai_model: str = field(default=os.environ.get("OPEN_AI_MODEL", "gpt-3.5-turbo-instruct"))

    def __post_init__(self) -> None:
        """Post-initialization of the configuration. Ensure that the OpenAI key is set."""
        import openai

        openai.api_key = self.openai_key
